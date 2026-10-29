from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ebpf_discovery.deepflow_codec_v5 import codec_file
from ebpf_discovery.observations import attributes, otlp, step_id


def _base(**updates):
    row = {
        "signal_source": "EBPF",
        "tap_side": "ServerProcess",
        "ebpf_type": "TracePoint",
        "l7_protocol": "Http1",
        "msg_type": "Request",
        "start_time": 9_007_199_254_740_993,
        "end_time": 9_007_199_254_741_007,
        "ip_src": "192.0.2.1",
        "ip_dst": "192.0.2.2",
        "port_src": 41000,
        "port_dst": 8080,
        "process_id_1": 123,
        "process_kname_1": "frontend",
        "request_type": "GET",
        "request_resource": "/items/7",
        "request_domain": "shop.test",
        "version": "1.1",
        "x_request_id_0": "attempt-step-1",
    }
    row.update(updates)
    return row


def _write(path: Path, rows, *, terminate=True):
    body = b"\n".join(
        row if isinstance(row, bytes) else json.dumps(row, separators=(",", ":")).encode()
        for row in rows
    )
    path.write_bytes(body + (b"\n" if terminate else b""))


def _spans(batch):
    return batch["payload"]["resourceSpans"][0]["scopeSpans"][0]["spans"]


def _attrs(span):
    return attributes(span["attributes"])


def test_streaming_preserves_all_records_prefix_tail_and_repeated_capture(tmp_path, monkeypatch):
    path = tmp_path / "l7_flow_log"
    rows = [_base(x_request_id_0=str(i)) for i in range(11)]
    rows.insert(4, _base(signal_source="Packet"))
    _write(path, rows)
    with path.open("ab") as output:
        output.write(b'{"pending":')
    expected_batches, expected_accounting, expected_prefix = codec_file(path, node="a", batch_size=3)
    # Acquisition must not restore whole-file reads behind its streaming API.
    monkeypatch.setattr(Path, "read_bytes", lambda _: pytest.fail("whole-file heap copy"))
    batches, accounting, seen = [], [], set()
    empty_batches, empty_accounting, prefix = codec_file(
        path, node="a", batch_size=3, seen=seen,
        on_batch=batches.append, on_accounting=accounting.append)
    assert empty_batches == empty_accounting == []
    assert (batches, accounting, prefix) == (expected_batches, expected_accounting, expected_prefix)
    assert prefix["pending_tail_bytes"] == len(b'{"pending":')
    assert prefix["non_ebpf_records"] == 1
    repeated = []
    _, _, second = codec_file(path, node="a", batch_size=3, seen=seen,
                              on_batch=lambda _: pytest.fail("duplicate output"),
                              on_accounting=repeated.append)
    assert len(repeated) == second["already_normalized_records"] == len(rows)
    assert second["normalized_records"] == second["normalized_batches"] == 0


def test_http_record_has_exact_time_raw_locator_and_no_invented_identity(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base()])
    batches, accounting, prefix = codec_file(
        path, node="a", source_file="l7_flow_log", batch_size=64
    )
    assert prefix["record_count"] == 1
    assert prefix["normalized_records"] == 1
    span = _spans(batches[0])[0]
    assert span["startTimeUnixNano"] == "9007199254740993000"
    assert span["endTimeUnixNano"] == "9007199254741007000"
    assert "traceId" not in span and "spanId" not in span and "parentSpanId" not in span
    attrs = _attrs(span)
    assert attrs["http.request.method"] == "GET"
    assert attrs["url.path"] == "/items/7"
    assert attrs["http.request.header.x-experiment-request-id"] == "attempt-step-1"
    assert attrs["process.pid"] == "123"
    assert attrs["process.command"] == "frontend"
    assert attrs["client.address"] == "192.0.2.1"
    assert attrs["client.port"] == "41000"
    assert attrs["deepflow.raw.offset"] == "0"
    raw = path.read_bytes()[:-1]
    assert attrs["deepflow.raw.length"] == str(len(raw))
    assert attrs["deepflow.raw.sha256"] == hashlib.sha256(raw).hexdigest()
    assert attrs["_runtime_identity.request_nonce"] == "attempt-step-1"
    assert attrs["_runtime_identity.node"] == "a"
    assert attrs["_runtime_identity.host_pid"] == "123"
    assert attrs["_runtime_identity.pid_scope"] == "guest_host"
    assert attrs["_runtime_identity.source_clock"].startswith("deepflow_guest_realtime")
    assert attrs["_runtime_identity.locator"]["sha256"] == attrs["deepflow.raw.sha256"]
    assert attrs["_runtime_identity.method"] == "GET"
    assert attrs["_runtime_identity.route"] == "/items/7"
    assert attrs["_runtime_identity.event_role"] == "synchronous_server_entry"
    resource = attributes(batches[0]["payload"]["resourceSpans"][0]["resource"]["attributes"])
    assert "service.name" not in resource
    normalized = list(otlp(batches[0]["payload"], "ebpf", "a"))[0]
    assert normalized["service"] == "unknown"
    assert step_id(normalized) == "attempt-step-1"
    assert accounting[0]["service_identity_enriched"] is False
    assert accounting[0]["_runtime_identity"]["request_nonce"] == "attempt-step-1"
    assert accounting[0]["_runtime_identity"]["event_role"] == "synchronous_server_entry"
    assert accounting[0]["_runtime_identity"]["locator"]["sha256"] == attrs["deepflow.raw.sha256"]


def test_http2_stream_id_and_response_header_are_not_experiment_request_id(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(
        l7_protocol="Http2", request_id=17, x_request_id_0="", x_request_id_1="response-only"
    )])
    batches, _, _ = codec_file(path, node="b")
    span = _spans(batches[0])[0]
    attrs = _attrs(span)
    assert attrs["deepflow.http2.stream_id"] == "17"
    assert attrs["deepflow.x_request_id_1"] == "response-only"
    normalized = list(otlp(batches[0]["payload"], "ebpf", "b"))[0]
    assert step_id(normalized) is None
    assert "_runtime_identity.request_nonce" not in attrs


def test_client_process_nonce_never_claims_server_entry_role(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(tap_side="ClientProcess", process_id_0=321)])
    batches, accounting, _ = codec_file(path, node="a")
    attrs = _attrs(_spans(batches[0])[0])
    assert attrs["_runtime_identity.request_nonce"] == "attempt-step-1"
    assert "_runtime_identity.event_role" not in attrs
    assert "event_role" not in accounting[0]["_runtime_identity"]


def test_duplicate_keys_identical_coalesce_but_conflicts_are_raw_only(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    common = (
        b'{"signal_source":"EBPF","l7_protocol":"Http1",'
        b'"tap_side":"ClientProcess","start_time":1,"end_time":2,'
        b'"request_type":"GET","request_resource":"/"'
    )
    identical = common + b',"msg_type":"Request","msg_type":"Request"}'
    conflict = common + b',"msg_type":"Request","msg_type":"Response"}'
    _write(path, [identical, conflict])
    batches, accounting, prefix = codec_file(path, node="a")
    assert len(_spans(batches[0])) == 1
    assert accounting[0]["status"] == "normalized"
    assert accounting[1]["status"] == "unclassified"
    assert accounting[1]["reasons"] == ["conflicting_duplicate_keys"]
    assert accounting[1]["technical_failure"] is False
    assert accounting[1]["conflicts"][0]["path"] == "$.msg_type"
    assert accounting[1]["conflicts"][0]["values"] == ["Request", "Response"]
    assert prefix["unclassified_records"] == 1
    assert prefix["technical_failure_records"] == 0
    assert path.read_bytes().endswith(conflict + b"\n")


def test_pinned_deepflow_flattened_msg_type_namespaces_are_explicit() -> None:
    path = Path(__file__).parent / "fixtures" / "deepflow-v7.2.3-http-session.jsonl"
    raw = path.read_bytes().removesuffix(b"\n")
    batches, accounting, prefix = codec_file(path, node="a")
    spans = _spans(batches[0])
    attrs = _attrs(spans[0])

    assert len(spans) == 1
    assert attrs["deepflow.msg_type"] == "Session"
    assert attrs["deepflow.base_head.msg_type"] == "Session"
    assert attrs["deepflow.protocol_info.msg_type"] == "Request"
    assert attrs["deepflow.raw.sha256"] == hashlib.sha256(raw).hexdigest()
    assert accounting[0]["source_namespace_split"] == {
        "path": "$.msg_type",
        "ordered_values": ["Session", "Request"],
        "base_head_msg_type": "Session",
        "protocol_info_msg_type": "Request",
    }
    assert accounting[0]["status"] == "normalized"
    assert prefix["normalized_records"] == 1
    assert path.read_bytes() == raw + b"\n"


@pytest.mark.parametrize("duplicates", [
    b'"msg_type":"Request","msg_type":"Session"',
    b'"msg_type":"Request","msg_type":"Response"',
    b'"msg_type":"Session","msg_type":"Request","msg_type":"Response"',
    b'"msg_type":"Session","msg_type":"Unknown"',
])
def test_non_source_msg_type_duplicate_shapes_remain_raw_only(
        tmp_path: Path, duplicates: bytes) -> None:
    path = tmp_path / "l7_flow_log"
    raw = (
        b'{"signal_source":"EBPF","l7_protocol":"Http1",'
        b'"tap_side":"ClientProcess","start_time":1,"end_time":2,'
        b'"request_type":"GET","request_resource":"/",' + duplicates + b'}'
    )
    _write(path, [raw])
    batches, accounting, prefix = codec_file(path, node="a")
    assert batches == []
    assert accounting[0]["status"] == "unclassified"
    assert accounting[0]["reasons"] == ["conflicting_duplicate_keys"]
    assert prefix["unclassified_records"] == 1
    assert path.read_bytes() == raw + b"\n"


@pytest.mark.parametrize("collision", [
    b'"base_head_msg_type":"Session"',
    b'"protocol_info_msg_type":"Request"',
    b'"__deepflow_msg_type_source_namespaces":{}',
])
def test_msg_type_namespace_derived_key_collisions_remain_raw_only(
        tmp_path: Path, collision: bytes) -> None:
    path = tmp_path / "l7_flow_log"
    raw = (
        b'{"signal_source":"EBPF","l7_protocol":"Http1",'
        b'"tap_side":"ClientProcess","start_time":1,"end_time":2,' + collision
        + b',"msg_type":"Session","msg_type":"Request"}'
    )
    _write(path, [raw])
    batches, accounting, _ = codec_file(path, node="a")
    assert batches == []
    assert accounting[0]["reasons"] == ["conflicting_duplicate_keys"]


@pytest.mark.parametrize("reserved", [
    b'"base_head_msg_type":"Session"',
    b'"protocol_info_msg_type":"Request"',
    b'"__deepflow_msg_type_source_namespaces":{"base_head_msg_type":"Session",'
    b'"protocol_info_msg_type":"Request"}',
])
def test_single_msg_type_cannot_forge_reserved_namespace_provenance(
        tmp_path: Path, reserved: bytes) -> None:
    path = tmp_path / "l7_flow_log"
    raw = (
        b'{"signal_source":"EBPF","l7_protocol":"Http1",'
        b'"tap_side":"ClientProcess","start_time":1,"end_time":2,'
        b'"request_type":"GET","request_resource":"/",'
        b'"msg_type":"Request",' + reserved + b'}'
    )
    _write(path, [raw])
    batches, accounting, prefix = codec_file(path, node="a")
    assert batches == []
    assert accounting[0]["status"] == "unclassified"
    assert accounting[0]["reasons"] == ["conflicting_duplicate_keys"]
    reserved_key = reserved.split(b'"', 2)[1].decode()
    assert accounting[0]["conflicts"][0]["path"] == f"$.{reserved_key}"
    assert prefix["unclassified_records"] == 1
    assert path.read_bytes() == raw + b"\n"


def test_nested_msg_type_conflict_remains_raw_only(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    raw = (
        b'{"signal_source":"EBPF","l7_protocol":"Http1",'
        b'"tap_side":"ClientProcess","start_time":1,"end_time":2,'
        b'"msg_type":"Request","nested":{"msg_type":"Session",'
        b'"msg_type":"Request"}}'
    )
    _write(path, [raw])
    batches, accounting, _ = codec_file(path, node="a")
    assert batches == []
    assert accounting[0]["reasons"] == ["conflicting_duplicate_keys"]
    assert accounting[0]["conflicts"][0]["path"] == "$.nested.msg_type"


@pytest.mark.parametrize("signal", ["Packet", "XFlow", "OTel", None])
def test_non_ebpf_signal_is_retained_but_not_normalized(tmp_path: Path, signal) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(signal_source=signal)])
    batches, accounting, prefix = codec_file(path, node="a")
    assert batches == []
    assert accounting[0]["status"] == "retained_non_ebpf"
    assert prefix["non_ebpf_records"] == 1


def test_unknown_protocol_and_incomplete_tail_are_explicit(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    complete = json.dumps(_base(l7_protocol="Thrift")).encode()
    incomplete = json.dumps(_base(l7_protocol="Http1", request_resource="/pending")).encode()
    path.write_bytes(complete + b"\n" + incomplete)
    batches, accounting, prefix = codec_file(path, node="a")
    assert batches == []
    assert "unsupported_or_unknown_protocol" in accounting[0]["reasons"][0]
    assert prefix["record_count"] == 1
    assert prefix["pending_tail_bytes"] == len(incomplete)
    assert prefix["pending_tail_sha256"] == hashlib.sha256(incomplete).hexdigest()
    assert accounting[0]["technical_failure"] is False


def test_complete_invalid_json_is_codec_failure_not_protocol_unknown(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    path.write_bytes(b'{"signal_source":"EBPF" broken}\n')
    batches, accounting, prefix = codec_file(path, node="a")
    assert batches == []
    assert accounting[0]["technical_failure"] is True
    assert accounting[0]["reasons"][0].startswith("invalid_json:")
    assert prefix["technical_failure_records"] == 1


@pytest.mark.parametrize("start,end", [(-1, 1), (1, -1), ((1 << 64) // 1000 + 1, 2)])
def test_nonrepresentable_otlp_time_is_retained_as_technical_failure(
    tmp_path: Path, start: int, end: int
) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(start_time=start, end_time=end)])
    batches, accounting, prefix = codec_file(path, node="a")
    assert batches == []
    assert accounting[0]["technical_failure"] is True
    assert accounting[0]["reasons"] == [
        "start_time_or_end_time_not_representable_as_otlp_unix_nano"
    ]
    assert prefix["technical_failure_records"] == 1


def test_reversed_source_time_is_preserved_with_uncertainty_warning(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(start_time=20, end_time=10)])
    batches, accounting, prefix = codec_file(path, node="a")
    assert len(_spans(batches[0])) == 1
    assert accounting[0]["technical_failure"] is False
    assert "end_time_precedes_start_time_source_clock_uncertainty" in accounting[0]["warnings"]
    assert prefix["technical_failure_records"] == 0


@pytest.mark.parametrize(
    ("protocol", "updates", "expected"),
    [
        ("Grpc", {"request_resource": "/cart.Cart/Get"},
         {"rpc.system": "grpc", "rpc.service": "cart.Cart", "rpc.method": "Get"}),
        ("MySQL", {"request_type": 3, "request_resource": "select 1", "statement_id": 9},
         {"db.system.name": "mysql", "deepflow.mysql.command_code": "3", "db.query.text": "select 1"}),
        ("PostgreSQL", {"request_type": "Q", "request_resource": "select 1", "status": "OK"},
         {"db.system.name": "postgresql", "deepflow.postgresql.request_type": "Q"}),
        ("Redis", {"request_type": "GET", "request_resource": "GET key"},
         {"db.system.name": "redis", "db.operation.name": "GET"}),
        ("MongoDB", {"op_code": 2013, "request_id": 44, "request_resource": "find items"},
         {"db.system.name": "mongodb", "deepflow.mongodb.op_code": "2013"}),
        ("Kafka", {"request_type": "Produce", "request_resource": "orders", "partition": 2,
                   "offset": 99, "request_id": 12},
         {"messaging.system": "kafka", "messaging.destination.name": "orders",
          "deepflow.kafka.request_id": "12"}),
    ],
)
def test_protocol_semantics_are_conservative(tmp_path: Path, protocol, updates, expected) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(l7_protocol=protocol, **updates)])
    batches, _, _ = codec_file(path, node="a")
    attrs = _attrs(_spans(batches[0])[0])
    for key, value in expected.items():
        assert attrs[key] == value
    assert "messaging.message.id" not in attrs
    if protocol not in {"Grpc"}:
        assert "_runtime_identity.request_nonce" not in attrs


def test_trace_and_span_candidates_remain_carrier_attributes(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(trace_ids=["aaa", "bbb"], span_id="ccc")])
    batches, _, _ = codec_file(path, node="a")
    span = _spans(batches[0])[0]
    assert "traceId" not in span and "spanId" not in span and "parentSpanId" not in span
    attrs = _attrs(span)
    assert attrs["deepflow.carrier.trace_ids"] == ["aaa", "bbb"]
    assert attrs["deepflow.carrier.span_id"] == "ccc"


def test_codec_batches_and_seen_set_avoid_one_file_per_trace_or_duplicate_append(tmp_path: Path) -> None:
    path = tmp_path / "l7_flow_log"
    _write(path, [_base(request_resource=f"/{index}") for index in range(5)])
    seen = set()
    batches, accounting, prefix = codec_file(path, node="a", seen=seen, batch_size=2)
    assert [len(_spans(batch)) for batch in batches] == [2, 2, 1]
    assert prefix["normalized_batches"] == 3
    assert len(seen) == 5
    second, accounting2, prefix2 = codec_file(path, node="a", seen=seen, batch_size=2)
    assert second == []
    assert all(item["status"] == "already_normalized" for item in accounting2)
    assert prefix2["already_normalized_records"] == 5
