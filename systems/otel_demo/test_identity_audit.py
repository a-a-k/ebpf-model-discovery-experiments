import base64
import json
from pathlib import Path

from systems.otel_demo.identity_audit import audit_message_identity
from ebpf_discovery.observations import otlp


def _id(value: str) -> str:
    return base64.b64encode(bytes.fromhex(value)).decode()


def _attr(key: str, value):
    kind = "intValue" if isinstance(value, int) else "stringValue"
    return {"key": key, "value": {kind: value}}


def _span(
    trace: str,
    span: str,
    parent: str,
    name: str,
    service: str,
    operation: str,
    *,
    request_id: str | None = None,
    offset: int | None = None,
    links=None,
    link_attributes=None,
    event_attributes=None,
):
    attrs = [
        _attr("messaging.system", "kafka") if operation else _attr("http.request.method", "POST"),
    ]
    if operation:
        attrs += [
            _attr("messaging.operation.type", operation),
            _attr("messaging.destination.name", "orders"),
            _attr("messaging.destination.partition.id", "0"),
        ]
        if offset is not None:
            attrs.append(_attr("messaging.kafka.offset", offset))
    else:
        attrs.append(_attr("http.route", "/api/checkout"))
        attrs.append(_attr("http.request.header.x-experiment-request-id", request_id))
    raw_links = []
    for linked_trace, linked_span in links or []:
        raw_links.append(
            {
                "traceId": _id(linked_trace),
                "spanId": _id(linked_span),
                "attributes": [_attr(*item) for item in (link_attributes or [])],
            }
        )
    events = (
        [{"name": "identity", "attributes": [_attr(*item) for item in event_attributes]}]
        if event_attributes
        else []
    )
    return service, {
        "traceId": _id(trace),
        "spanId": _id(span),
        "parentSpanId": _id(parent) if parent else "",
        "name": name,
        "kind": "SPAN_KIND_SERVER" if not operation else "SPAN_KIND_PRODUCER",
        "startTimeUnixNano": "1",
        "endTimeUnixNano": "2",
        "attributes": attrs,
        "links": raw_links,
        "events": events,
    }


def _write(root: Path, spans) -> tuple[Path, list[dict]]:
    observations = root / "observations"
    observations.mkdir(parents=True)
    resources = []
    for service, span in spans:
        resources.append(
            {
                "resource": {"attributes": [_attr("service.name", service)]},
                "scopeSpans": [{"spans": [span]}],
            }
        )
    payload = {"resourceSpans": resources}
    document = {"id_encoding": "base64", "payload": payload}
    (observations / "a.jsonl").write_text(json.dumps(document) + "\n", encoding="utf-8")
    return observations, list(otlp(payload, "ebpf", "a", "base64"))


def test_partition_and_consumer_offset_are_not_an_exact_identity(tmp_path: Path) -> None:
    trace = "11" * 16
    producer = _span(trace, "21" * 8, "", "send orders", "checkout", "send")
    consumer = _span("12" * 16, "22" * 8, "", "process orders", "accounting", "process", offset=7)
    raw, normalized = _write(tmp_path, [producer, consumer])

    result = audit_message_identity(raw, None, normalized)["sources"]["ebpf"]

    assert result["identity_candidate_counts"]["complete_destination_partition_offset_intersections"] == 0
    assert result["assessment"]["status"] == "raw_candidate_absent_observed_scope"
    assert result["preservation"]["exact_normalized_record_matches"] == 2


def test_dropped_link_identity_attribute_is_explicit(tmp_path: Path) -> None:
    producer_trace, producer_span = "31" * 16, "41" * 8
    producer = _span(producer_trace, producer_span, "", "send orders", "checkout", "send")
    consumer = _span(
        "32" * 16,
        "42" * 8,
        "",
        "process orders",
        "accounting",
        "process",
        links=[(producer_trace, producer_span)],
        link_attributes=[("messaging.message.id", "record-1")],
    )
    raw, normalized = _write(tmp_path, [producer, consumer])

    result = audit_message_identity(raw, None, normalized)["sources"]["ebpf"]

    assert result["identity_candidate_counts"]["exact_consumer_links_to_observed_producer"] == 1
    assert result["identity_candidate_counts"]["identity_fields_in_dropped_link_attributes"] == 1
    assert result["preservation"]["link_identities_preserved"] == 1
    assert result["preservation"]["link_attribute_fields_not_represented_by_normalizer"] == 1
    assert result["assessment"]["status"] == "matcher_reject"


def test_event_identity_field_prevents_raw_absence_overclaim(tmp_path: Path) -> None:
    producer = _span(
        "33" * 16,
        "43" * 8,
        "",
        "send orders",
        "checkout",
        "send",
        event_attributes=[("messaging.message.id", "record-2")],
    )
    raw, normalized = _write(tmp_path, [producer])

    result = audit_message_identity(raw, None, normalized)["sources"]["ebpf"]

    assert result["identity_candidate_counts"]["identity_fields_in_dropped_event_attributes"] == 1
    assert result["preservation"]["event_attribute_fields_not_represented_by_normalizer"] == 1
    assert result["assessment"]["status"] == "normalization_discard_unresolved_candidate"


def test_raw_variants_differing_only_by_dropped_event_survive(tmp_path: Path) -> None:
    plain = _span("34" * 16, "44" * 8, "", "send orders", "checkout", "send")
    with_event = _span(
        "34" * 16,
        "44" * 8,
        "",
        "send orders",
        "checkout",
        "send",
        event_attributes=[("messaging.message.id", "later-record")],
    )
    raw, normalized = _write(tmp_path, [plain, with_event])

    result = audit_message_identity(raw, None, normalized)["sources"]["ebpf"]

    assert result["preservation"]["raw_unique_kafka_spans"] == 2
    assert result["identity_candidate_counts"]["identity_fields_in_dropped_event_attributes"] == 1
    assert result["assessment"]["status"] == "normalization_discard_unresolved_candidate"


def test_offset_tuple_overlap_is_untrusted(tmp_path: Path) -> None:
    producer = _span("35" * 16, "45" * 8, "", "send orders", "checkout", "send", offset=0)
    consumer = _span("36" * 16, "46" * 8, "", "process orders", "accounting", "process", offset=0)
    raw, normalized = _write(tmp_path, [producer, consumer])

    result = audit_message_identity(raw, None, normalized)["sources"]["ebpf"]

    assert result["stage_counts"]["raw_exact_identity_candidates"] == 0
    assert result["stage_counts"]["raw_untrusted_identity_candidates"] == 1
    assert result["assessment"]["status"] == "untrusted_candidate_only"


def test_parse_or_preservation_failure_makes_audit_incomplete(tmp_path: Path) -> None:
    raw = tmp_path / "observations"
    raw.mkdir()
    (raw / "a.jsonl").write_text("{not-json}\n", encoding="utf-8")
    malformed = audit_message_identity(raw, None, [])["sources"]["ebpf"]
    assert malformed["assessment"]["status"] == "audit_incomplete"

    other = tmp_path / "other"
    producer = _span("37" * 16, "47" * 8, "", "send orders", "checkout", "send")
    valid_raw, normalized = _write(other, [producer])
    normalized[0]["attributes"].pop("messaging.destination.name")
    mismatch = audit_message_identity(valid_raw, None, normalized)["sources"]["ebpf"]
    assert mismatch["assessment"]["status"] == "audit_incomplete"
    assert mismatch["assessment"]["basis"]["preservation_incomplete"] is True


def test_native_reference_does_not_fill_ebpf_absence(tmp_path: Path) -> None:
    ebpf_root = tmp_path / "ebpf"
    native_root = tmp_path / "native"
    producer = _span("51" * 16, "61" * 8, "", "send orders", "checkout", "send")
    raw, ebpf_normalized = _write(ebpf_root, [producer])
    native_root.mkdir()
    native_producer = _span("52" * 16, "62" * 8, "", "send orders", "checkout", "send")
    service, native_span = native_producer
    payload = {
        "resourceSpans": [
            {
                "resource": {"attributes": [_attr("service.name", service)]},
                "scopeSpans": [{"spans": [native_span]}],
            }
        ]
    }
    (native_root / "traces.json").write_text(json.dumps(payload), encoding="utf-8")
    normalized = ebpf_normalized + list(otlp(payload, "native", None, "base64"))

    result = audit_message_identity(raw, native_root, normalized)

    assert result["sources"]["ebpf"]["assessment"]["status"] == "raw_candidate_absent_observed_scope"
    assert result["sources"]["native"]["role_counts"] == {"producer": 1}
    assert result["limitations"][2].startswith("native evidence is reported separately")


def test_no_kafka_observation_is_not_reported_as_absence(tmp_path: Path) -> None:
    raw = tmp_path / "observations"
    raw.mkdir()
    (raw / "a.jsonl").write_text("", encoding="utf-8")

    result = audit_message_identity(raw, None, [])["sources"]["ebpf"]

    assert result["assessment"]["status"] == "no_observation"
    assert result["stage_counts"]["raw_kafka_spans"] == 0
