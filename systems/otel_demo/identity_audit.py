"""Bounded audit of Kafka identity evidence across raw and normalized spans.

This module is diagnostic only.  It never uses workload records, order IDs from
the evaluator, timestamps, or topic-only proximity to associate messages.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from ebpf_discovery.async_links import message_chains
from ebpf_discovery.observations import identifier, otlp


PRODUCER_OPERATIONS = {"publish", "produce", "send"}
CONSUMER_OPERATIONS = {"fetch", "process", "receive"}
OPERATION_KEYS = (
    "messaging.operation.type",
    "messaging.operation.name",
    "messaging.operation",
)
DESTINATION_KEYS = ("messaging.destination.name",)
PARTITION_KEYS = (
    "messaging.destination.partition.id",
    "messaging.kafka.destination.partition",
)
OFFSET_KEYS = ("messaging.kafka.offset", "messaging.kafka.message.offset")
MESSAGE_ID_KEYS = ("messaging.message.id",)
# Kafka keys are useful raw evidence but are not unique message identifiers.
AUDITED_ATTRIBUTE_PREFIXES = ("messaging.",)
AUDITED_APPLICATION_FIELDS = {"demo.order.id"}
IGNORED_NORMALIZED_FIELDS = {"raw_file", "_graph_node"}


def _value_for(attrs: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        value = attrs.get(key)
        if value is not None and value != "":
            return value
    return None


def _operation(attrs: dict[str, Any]) -> str:
    return str(_value_for(attrs, OPERATION_KEYS) or "").lower()


def _role(span: dict[str, Any]) -> str:
    operation = _operation(span["attributes"])
    if operation in PRODUCER_OPERATIONS:
        return "producer"
    if operation in CONSUMER_OPERATIONS:
        return "consumer"
    return "other"


def _audited_key(key: str) -> bool:
    return key.startswith(AUDITED_ATTRIBUTE_PREFIXES) or key in AUDITED_APPLICATION_FIELDS


def _semantic_key(span: dict[str, Any]) -> str:
    evidence = {
        key: value
        for key, value in span.items()
        if key not in IGNORED_NORMALIZED_FIELDS
    }
    return json.dumps(evidence, sort_keys=True, separators=(",", ":"))


def _raw_value(item: Any) -> Any:
    """Decode protobuf JSON values without relying on the normalizer output."""
    if not isinstance(item, dict):
        return item
    if "arrayValue" in item:
        return [_raw_value(value) for value in item["arrayValue"].get("values", [])]
    if "kvlistValue" in item:
        return _raw_attributes(item["kvlistValue"].get("values", []))
    return next(iter(item.values()), None)


def _raw_attributes(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        item["key"]: _raw_value(item.get("value"))
        for item in items
        if isinstance(item, dict) and isinstance(item.get("key"), str)
    }


def _locator(span: dict[str, Any]) -> tuple[Any, ...]:
    return (
        span.get("source"),
        span.get("node"),
        span.get("trace_id"),
        span.get("span_id"),
        span.get("service"),
        span.get("name"),
        span.get("start_ns"),
        span.get("end_ns"),
    )


def _documents(path: Path) -> Iterable[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return
    try:
        loaded = json.loads(text)
        documents = loaded if isinstance(loaded, list) else [loaded]
    except json.JSONDecodeError:
        documents = (json.loads(line) for line in text.splitlines() if line.strip())
    for document in documents:
        if isinstance(document, dict):
            yield document


def _observation_files(root: Path, source: str) -> list[Path]:
    if not root.exists():
        return []
    if source == "ebpf":
        base = root / "observations" if (root / "observations").is_dir() else root
        return sorted(base.glob("[ab].jsonl"))
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.suffix in {".json", ".jsonl"}
        and path.name.startswith(("traces", "native-node-"))
    ]


def _raw_records(root: Path, source: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    records: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, str]] = []
    for path in _observation_files(root, source):
        try:
            for document in _documents(path):
                payload = document.get("payload", document)
                encoding = document.get("id_encoding", "hex")
                node = path.stem if source == "ebpf" else None
                normalized = list(otlp(payload, source, node, encoding))
                raw_spans = []
                for resource in payload.get("resourceSpans", []):
                    for scope in resource.get(
                        "scopeSpans", resource.get("instrumentationLibrarySpans", [])
                    ):
                        raw_spans.extend(scope.get("spans", []))
                if len(raw_spans) != len(normalized):
                    errors.append(
                        {
                            "file": str(path),
                            "error": "raw/normalized span cardinality mismatch",
                        }
                    )
                    continue
                for raw, span in zip(raw_spans, normalized):
                    if span["attributes"].get("messaging.system") != "kafka":
                        continue
                    raw_attribute_keys = [
                        item.get("key", "")
                        for item in raw.get("attributes", [])
                        if isinstance(item, dict)
                    ]
                    link_attributes = [
                        _raw_attributes(link.get("attributes", []))
                        for link in raw.get("links", [])
                        if isinstance(link, dict)
                    ]
                    events = [
                        {
                            "name": event.get("name"),
                            "timeUnixNano": event.get("timeUnixNano"),
                            "attributes": _raw_attributes(event.get("attributes", [])),
                        }
                        for event in raw.get("events", [])
                        if isinstance(event, dict)
                    ]
                    record = {
                        "span": span,
                        "raw_attributes": _raw_attributes(raw.get("attributes", [])),
                        "raw_id_presence": {
                            "traceId": bool(raw.get("traceId")),
                            "spanId": bool(raw.get("spanId")),
                            "parentSpanId": bool(raw.get("parentSpanId")),
                        },
                        "raw_attribute_keys": raw_attribute_keys,
                        "duplicate_attribute_keys": sorted(
                            key
                            for key, count in Counter(raw_attribute_keys).items()
                            if key and count > 1
                        ),
                        "raw_link_ids": [
                            (
                                identifier(link.get("traceId"), encoding),
                                identifier(link.get("spanId"), encoding),
                            )
                            for link in raw.get("links", [])
                            if isinstance(link, dict)
                        ],
                        "raw_link_attributes": link_attributes,
                        "raw_events": events,
                    }
                    # The production normalizer intentionally omits link
                    # attributes and events. Include their independently
                    # decoded values here so distinct raw observations cannot
                    # collapse merely because they normalize identically.
                    raw_key = json.dumps(record, sort_keys=True, separators=(",", ":"))
                    records.setdefault(raw_key, record)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            errors.append({"file": str(path), "error": str(exc)})
    return list(records.values()), errors


def _field_path_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        for key, present in record["raw_id_presence"].items():
            if present:
                counts[f"span.{key}"] += 1
        for key in record["raw_attribute_keys"]:
            if _audited_key(key):
                counts[f"span.attributes.{key}"] += 1
        for trace_id, span_id in record["raw_link_ids"]:
            if trace_id:
                counts["span.links[].traceId"] += 1
            if span_id:
                counts["span.links[].spanId"] += 1
        for link_attrs in record["raw_link_attributes"]:
            for key in link_attrs:
                if _audited_key(key):
                    counts[f"span.links[].attributes.{key}"] += 1
        for event in record["raw_events"]:
            for key in event["attributes"]:
                if _audited_key(key):
                    counts[f"span.events[].attributes.{key}"] += 1
    return dict(sorted(counts.items()))


def _identity_tuple(attrs: dict[str, Any]) -> tuple[str, str, str] | None:
    destination = _value_for(attrs, DESTINATION_KEYS)
    partition = _value_for(attrs, PARTITION_KEYS)
    offset = _value_for(attrs, OFFSET_KEYS)
    if destination is None or partition is None or offset is None:
        return None
    return str(destination), str(partition), str(offset)


def _message_ids(attrs: dict[str, Any]) -> set[str]:
    value = _value_for(attrs, MESSAGE_ID_KEYS)
    return {str(value)} if value is not None else set()


def _candidate_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    producer_records = [r for r in records if _role(r["span"]) == "producer"]
    consumer_records = [r for r in records if _role(r["span"]) == "consumer"]
    producers = [r["span"] for r in producer_records]
    producer_ids = {
        (span["trace_id"], span["span_id"])
        for span in producers
        if span.get("trace_id") and span.get("span_id")
    }
    direct_links = sum(
        (trace_id, span_id) in producer_ids
        for record in records
        if _role(record["span"]) == "consumer"
        for trace_id, span_id in record["raw_link_ids"]
    )
    producer_tuples = {
        value for record in producer_records if (value := _identity_tuple(record["raw_attributes"]))
    }
    consumer_tuples = {
        value for record in consumer_records if (value := _identity_tuple(record["raw_attributes"]))
    }
    producer_message_ids = (
        set().union(*(_message_ids(record["raw_attributes"]) for record in producer_records))
        if producer_records
        else set()
    )
    consumer_message_ids = (
        set().union(*(_message_ids(record["raw_attributes"]) for record in consumer_records))
        if consumer_records
        else set()
    )
    dropped_link_identity_fields = sum(
        key in MESSAGE_ID_KEYS or key in OFFSET_KEYS
        for record in records
        for link_attrs in record["raw_link_attributes"]
        for key in link_attrs
    )
    dropped_event_identity_fields = sum(
        key in MESSAGE_ID_KEYS or key in OFFSET_KEYS
        for record in records
        for event in record["raw_events"]
        for key in event["attributes"]
    )
    return {
        "exact_consumer_links_to_observed_producer": direct_links,
        "complete_destination_partition_offset_intersections": len(
            producer_tuples & consumer_tuples
        ),
        "message_id_intersections": len(producer_message_ids & consumer_message_ids),
        "identity_fields_in_dropped_link_attributes": dropped_link_identity_fields,
        "identity_fields_in_dropped_event_attributes": dropped_event_identity_fields,
    }


def _preservation(
    records: list[dict[str, Any]], normalized: list[dict[str, Any]]
) -> dict[str, Any]:
    normalized_keys = {_semantic_key(span) for span in normalized}
    by_locator: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for span in normalized:
        by_locator[_locator(span)].append(span)
    attribute_paths_seen = attribute_paths_preserved = 0
    link_ids_seen = link_ids_preserved = 0
    records_with_locator = 0
    for record in records:
        span = record["span"]
        matches = by_locator.get(_locator(span), [])
        if matches:
            records_with_locator += 1
        for key, value in record["raw_attributes"].items():
            if not _audited_key(key):
                continue
            attribute_paths_seen += 1
            if any(candidate["attributes"].get(key) == value for candidate in matches):
                attribute_paths_preserved += 1
        for link in span.get("links", []):
            link_ids_seen += 1
            identity = (link.get("trace_id"), link.get("span_id"))
            if any(
                identity
                in {
                    (item.get("trace_id"), item.get("span_id"))
                    for item in candidate.get("links", [])
                }
                for candidate in matches
            ):
                link_ids_preserved += 1
    return {
        "raw_unique_kafka_spans": len(records),
        "records_with_normalized_locator": records_with_locator,
        "exact_normalized_record_matches": sum(
            _semantic_key(record["span"]) in normalized_keys for record in records
        ),
        "audited_span_attribute_values_seen": attribute_paths_seen,
        "audited_span_attribute_values_preserved": attribute_paths_preserved,
        "link_identities_seen": link_ids_seen,
        "link_identities_preserved": link_ids_preserved,
        "link_attribute_fields_not_represented_by_normalizer": sum(
            sum(len(attrs) for attrs in record["raw_link_attributes"])
            for record in records
        ),
        "event_attribute_fields_not_represented_by_normalizer": sum(
            sum(len(event["attributes"]) for event in record["raw_events"])
            for record in records
        ),
    }


def _matcher_census(
    source: str, chains: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    statuses: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    for result in chains.values():
        evidence = result.get("sources", {}).get(source)
        if not evidence:
            continue
        statuses[str(evidence.get("status", "unknown"))] += 1
        if evidence.get("reason"):
            reasons[str(evidence["reason"])] += 1
    return {
        "observed_anchor_results": sum(statuses.values()),
        "status_counts": dict(sorted(statuses.items())),
        "reason_counts": dict(sorted(reasons.items())),
    }


def _assessment(
    records: list[dict[str, Any]],
    errors: list[dict[str, str]],
    candidates: dict[str, int],
    preservation: dict[str, Any],
    matcher: dict[str, Any],
) -> dict[str, Any]:
    linked = matcher["status_counts"].get("linked", 0)
    ambiguous = sum(
        count
        for reason, count in matcher["reason_counts"].items()
        if reason.startswith("ambiguous_")
    )
    dropped_candidates = (
        candidates["identity_fields_in_dropped_link_attributes"]
        + candidates["identity_fields_in_dropped_event_attributes"]
    )
    trusted_raw_candidates = candidates[
        "exact_consumer_links_to_observed_producer"
    ]
    untrusted_raw_candidates = (
        candidates["complete_destination_partition_offset_intersections"]
        + candidates["message_id_intersections"]
    )
    preservation_incomplete = (
        preservation["records_with_normalized_locator"]
        != preservation["raw_unique_kafka_spans"]
        or preservation["audited_span_attribute_values_seen"]
        != preservation["audited_span_attribute_values_preserved"]
        or preservation["link_identities_seen"]
        != preservation["link_identities_preserved"]
        or any(record["duplicate_attribute_keys"] for record in records)
    )
    if errors or preservation_incomplete:
        status = "audit_incomplete"
    elif not records:
        status = "no_observation"
    elif linked:
        status = "matcher_confirmed"
    elif ambiguous:
        status = "ambiguous"
    elif trusted_raw_candidates:
        status = "matcher_reject"
    elif dropped_candidates:
        # The field path is real raw evidence, but this census does not call it
        # an association without a matching value at another exact endpoint.
        status = "normalization_discard_unresolved_candidate"
    elif untrusted_raw_candidates:
        status = "untrusted_candidate_only"
    else:
        status = "raw_candidate_absent_observed_scope"
    return {
        "status": status,
        "bounded_to_observed_capture": True,
        "not_a_business_outcome": True,
        "basis": {
            "trusted_exact_raw_candidates": trusted_raw_candidates,
            "untrusted_raw_candidates": untrusted_raw_candidates,
            "dropped_candidate_fields": dropped_candidates,
            "matcher_linked": linked,
            "matcher_ambiguous": ambiguous,
            "raw_unique_kafka_spans": preservation["raw_unique_kafka_spans"],
            "parse_errors": len(errors),
            "preservation_incomplete": preservation_incomplete,
        },
    }


def audit_message_identity(
    raw_root: Path,
    native_root: Path | None,
    normalized_spans: list[dict[str, Any]],
) -> dict[str, Any]:
    """Audit observed Kafka identity fields without creating associations.

    The returned evidence is partitioned by source.  Native evidence is a
    reference and never fills a missing eBPF field or matcher stage.
    """
    roots = {"ebpf": raw_root}
    if native_root is not None:
        roots["native"] = native_root
    chains = message_chains(normalized_spans)
    output: dict[str, Any] = {
        "method": "raw OTLP field-path and normalized-preservation census",
        "limitations": [
            "observed captures only; absence is not a universal instrumentation claim",
            "topic, time, broker request correlation, and evaluator order IDs are not associations",
            "native evidence is reported separately and is not borrowed by eBPF",
        ],
        "sources": {},
    }
    for source, root in roots.items():
        records, errors = _raw_records(root, source)
        normalized = [span for span in normalized_spans if span.get("source") == source]
        roles = Counter(_role(record["span"]) for record in records)
        candidates = _candidate_counts(records)
        preservation = _preservation(records, normalized)
        matcher = _matcher_census(source, chains)
        output["sources"][source] = {
            "raw_files": [str(path) for path in _observation_files(root, source)],
            "parse_errors": errors,
            "role_counts": dict(sorted(roles.items())),
            "raw_field_path_counts": _field_path_counts(records),
            "duplicate_span_attribute_keys": dict(
                sorted(
                    Counter(
                        key
                        for record in records
                        for key in record["duplicate_attribute_keys"]
                    ).items()
                )
            ),
            "identity_candidate_counts": candidates,
            "candidate_trust": {
                "trusted": ["exact_consumer_links_to_observed_producer"],
                "untrusted": [
                    "complete_destination_partition_offset_intersections",
                    "message_id_intersections",
                ],
                "untrusted_note": (
                    "tuple/value overlaps are a census only; they do not prove "
                    "association and never trigger matcher-loss classification"
                ),
            },
            "preservation": preservation,
            "matcher": matcher,
            "stage_counts": {
                "raw_kafka_spans": len(records),
                "normalized_exact_matches": preservation["exact_normalized_record_matches"],
                "raw_exact_identity_candidates": candidates[
                    "exact_consumer_links_to_observed_producer"
                ],
                "raw_untrusted_identity_candidates": (
                    candidates["complete_destination_partition_offset_intersections"]
                    + candidates["message_id_intersections"]
                ),
                "matcher_linked": matcher["status_counts"].get("linked", 0),
                "matcher_unknown": matcher["status_counts"].get("unknown", 0),
            },
            "assessment": _assessment(records, errors, candidates, preservation, matcher),
        }
    return output
