from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
import pytest

from ebpf_discovery.raw_v4 import export_selection


TRACE = "00112233445566778899aabbccddeeff"
SPAN = "0102030405060708"


class Store:
    def __init__(self, rows):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE files(path TEXT, consumed INTEGER)")
        self.db.executemany("INSERT INTO files VALUES (?,?)", rows)


def _span(attribute: str) -> dict:
    return {
        "traceId": TRACE,
        "spanId": SPAN,
        "name": "GET /lookup",
        "kind": "SPAN_KIND_SERVER",
        "startTimeUnixNano": "10",
        "endTimeUnixNano": "20",
        "attributes": [{"key": "variant", "value": {"stringValue": attribute}}],
        "links": [{"traceId": "f" * 32, "spanId": "e" * 16,
                   "attributes": [{"key": "link", "value": {"intValue": "7"}}]}],
    }


def _payload(*spans: dict) -> dict:
    return {"resourceSpans": [{
        "resource": {"attributes": [
            {"key": "service.name", "value": {"stringValue": "lookup-api"}},
            {"key": "bering.network.scope", "value": {"stringValue": "observed-old"}},
        ]},
        "scopeSpans": [{
            "scope": {"name": "scope", "version": "1", "attributes": [
                {"key": "scope.attr", "value": {"boolValue": True}},
            ]},
            "spans": list(spans),
        }],
    }]}


def _wrapper(root: Path, payload: dict, name: str = "capture") -> tuple[dict, Path]:
    raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
    raw_path = root / "a.raw" / name / "body.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(raw)
    return ({
        "source": "ebpf:a", "node": "a", "received_ns": 1,
        "id_encoding": "hex", "payload": payload,
        "raw_ref": raw_path.relative_to(root).as_posix(),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "content_type": "application/json", "content_encoding": "",
    }, raw_path)


def test_json_conflicts_scope_links_source_isolation_and_training_prefix(tmp_path: Path):
    observations = tmp_path / "observations"
    observations.mkdir()
    wrapper, raw_path = _wrapper(observations, _payload(_span("one"), _span("two")))
    ebpf = observations / "a.jsonl"
    frozen = (json.dumps(wrapper) + "\n").encode()
    appended, _ = _wrapper(observations, _payload(_span("appended")), "appended")
    ebpf.write_bytes(frozen + (json.dumps(appended) + "\n").encode())

    native = observations / "native-node-a.jsonl"
    native_line = (json.dumps(_payload(_span("native"))) + "\n").encode()
    native.write_bytes(native_line)
    store = Store([(str(ebpf), len(frozen)), (str(native), len(native_line))])

    result = export_selection(
        store, {"ebpf": {(TRACE, SPAN)}, "native": {(TRACE, SPAN)}},
        tmp_path / "out", network_scope="guest-a",
    )
    assert result["observations"] == 3
    assert [item["source"] for item in result["exports"]] == ["ebpf", "native"]
    ebpf_export = result["exports"][0]
    assert ebpf_export["raw_file"] == str(raw_path.resolve())
    assert ebpf_export["selected_ids"] == [[TRACE, SPAN], [TRACE, SPAN]]
    exported = json.loads(Path(ebpf_export["path"]).read_text())
    resource = exported["resourceSpans"][0]
    assert [span["attributes"][0]["value"]["stringValue"]
            for span in resource["scopeSpans"][0]["spans"]] == ["one", "two"]
    assert resource["scopeSpans"][0]["scope"]["attributes"][0]["key"] == "scope.attr"
    assert resource["scopeSpans"][0]["spans"][0]["links"][0]["attributes"][0]["key"] == "link"
    scopes = [item["value"]["stringValue"] for item in resource["resource"]["attributes"]
              if item["key"] == "bering.network.scope"]
    assert scopes == ["observed-old", "guest-a"]
    assert all(not trace.startswith(("ebpf:", "native:"))
               for item in result["exports"] for trace, _span_id in item["selected_ids"])
    native_export = result["exports"][1]
    assert native_export["raw_sha256"] == hashlib.sha256(native_line).hexdigest()
    assert native_export["raw_record_sha256"] == hashlib.sha256(native_line).hexdigest()


def test_protobuf_copy_preserves_duplicate_variants_scope_attributes_and_links(tmp_path: Path):
    observations = tmp_path / "observations"
    raw_path = observations / "a.raw" / "pb" / "body.pb"
    raw_path.parent.mkdir(parents=True)
    request = ExportTraceServiceRequest()
    resource = request.resource_spans.add()
    resource.resource.attributes.add(key="service.name").value.string_value = "lookup-api"
    scope = resource.scope_spans.add()
    scope.scope.name = "scope"
    scope.scope.attributes.add(key="scope.attr").value.bool_value = True
    unknown_field = b"\xa0\x06\x07"  # unknown field 100, varint 7
    for value in ("one", "two"):
        span = scope.spans.add(trace_id=bytes.fromhex(TRACE), span_id=bytes.fromhex(SPAN), name="lookup")
        span.attributes.add(key="variant").value.string_value = value
        link = span.links.add(trace_id=b"\xff" * 16, span_id=b"\xee" * 8)
        link.attributes.add(key="link").value.int_value = 7
        if value == "one":
            span.ParseFromString(span.SerializeToString() + unknown_field)
    wire = request.SerializeToString()
    raw_path.write_bytes(wire)
    wrapper = {
        "source": "ebpf:a", "id_encoding": "base64", "payload": {},
        "raw_ref": raw_path.relative_to(observations).as_posix(),
        "raw_sha256": hashlib.sha256(wire).hexdigest(),
        "content_type": "application/x-protobuf", "content_encoding": "",
    }
    index = observations / "a.jsonl"
    line = (json.dumps(wrapper) + "\n").encode()
    index.write_bytes(line)
    result = export_selection(Store([(str(index), len(line))]), {"ebpf": {(TRACE, SPAN)}}, tmp_path / "out")
    assert result["observations"] == 2
    exported = ExportTraceServiceRequest()
    exported.ParseFromString(Path(result["exports"][0]["path"]).read_bytes())
    spans = exported.resource_spans[0].scope_spans[0].spans
    assert [span.attributes[0].value.string_value for span in spans] == ["one", "two"]
    assert exported.resource_spans[0].scope_spans[0].scope.attributes[0].key == "scope.attr"
    assert spans[0].links[0].attributes[0].value.int_value == 7
    assert unknown_field in spans[0].SerializeToString()


def test_supplied_role_changes_only_derived_protobuf_kind_and_preserves_unknown_wire(tmp_path: Path):
    observations = tmp_path/'observations'
    raw = observations/'a.raw'/'one'/'body.pb'
    raw.parent.mkdir(parents=True)
    request = ExportTraceServiceRequest()
    scope = request.resource_spans.add().scope_spans.add()
    root = scope.spans.add(trace_id=bytes.fromhex(TRACE), span_id=bytes.fromhex(SPAN), name='receiver')
    unknown = b'\xa0\x06\x07'
    root.ParseFromString(root.SerializeToString() + unknown)
    wire = request.SerializeToString()
    raw.write_bytes(wire)
    wrapper = {'raw_ref': raw.relative_to(observations).as_posix(),
               'raw_sha256': hashlib.sha256(wire).hexdigest(),
               'content_type': 'application/x-protobuf'}
    index = observations/'a.jsonl'
    line = (json.dumps(wrapper)+'\n').encode()
    index.write_bytes(line)
    role = {'source': 'ebpf', 'trace_id': TRACE, 'span_id': SPAN,
            'original_kind': None, 'supplied_kind': 'SPAN_KIND_SERVER',
            'rule': 'unique declared entry; untyped declared receiver component with actual HTTP method and path'}
    result = export_selection(Store([(str(index), len(line))]), {'ebpf': {(TRACE, SPAN)}},
                              tmp_path/'out', supplied_server_roles={('ebpf', TRACE, SPAN): role})
    output = ExportTraceServiceRequest()
    output.ParseFromString(Path(result['exports'][0]['path']).read_bytes())
    exported_span = output.resource_spans[0].scope_spans[0].spans[0]
    assert exported_span.kind == 2
    assert unknown in exported_span.SerializeToString()
    assert raw.read_bytes() == wire
    assert result['exports'][0]['raw_sha256'] == hashlib.sha256(wire).hexdigest()
    assert result['exports'][0]['supplied_server_roles'] == [role]
    root.kind = 3
    wire_client = request.SerializeToString()
    raw.write_bytes(wire_client)
    wrapper['raw_sha256'] = hashlib.sha256(wire_client).hexdigest()
    line = (json.dumps(wrapper)+'\n').encode()
    index.write_bytes(line)
    with pytest.raises(ValueError, match='conflicts with explicit kind'):
        export_selection(Store([(str(index), len(line))]), {'ebpf': {(TRACE, SPAN)}},
                         tmp_path/'reject', supplied_server_roles={('ebpf', TRACE, SPAN): role})


@pytest.mark.parametrize("name", ["a.jsonl", "native.jsonl"])
def test_receiver_wrapper_without_original_wire_is_rejected(tmp_path: Path, name: str):
    path = tmp_path / name
    line = (json.dumps({"payload": _payload(_span("decoded-only")), "id_encoding": "base64"}) + "\n").encode()
    path.write_bytes(line)
    source = "ebpf" if name == "a.jsonl" else "native"
    with pytest.raises(ValueError, match="lacks original wire capture"):
        export_selection(Store([(str(path), len(line))]), {source: {(TRACE, SPAN)}}, tmp_path / "out")


def test_jaeger_codec_preserves_typed_evidence_and_reference_semantics(tmp_path: Path):
    trace_id, parent_id, child_id = "abcdef0123456789", "1", "2"
    zero_trace = "0" * 16
    trace = {"traceID": trace_id, "processes": {"p": {
        "serviceName": "frontend", "tags": [{"key": "host.port", "type": "int64", "value": 8080}],
    }}, "spans": [{
        "traceID": trace_id, "spanID": child_id, "operationName": "GET /call", "processID": "p",
        "startTime": 10, "duration": 5,
        "tags": [{"key": "span.kind", "type": "string", "value": "server"},
                 {"key": "error", "type": "bool", "value": True}],
        "logs": [{"timestamp": 12, "fields": [{"key": "event", "type": "string", "value": "failed"}]}],
        "references": [
            {"refType": "CHILD_OF", "traceID": trace_id, "spanID": parent_id},
            {"refType": "FOLLOWS_FROM", "traceID": "0" * 16, "spanID": "0"},
        ],
    }, {
        "traceID": zero_trace, "spanID": "0", "operationName": "invalid-zero-id", "processID": "p",
        "startTime": 20, "duration": 1, "tags": [], "references": [],
    }]}
    raw = tmp_path / "traces-frontend.json"
    raw.write_text(json.dumps({"data": [trace], "errors": None}), encoding="utf-8")
    result = export_selection(Store([(str(raw), raw.stat().st_size)]),
                              {"native": {(trace_id, child_id), (zero_trace, "0")}}, tmp_path / "out")
    assert result["observations"] == 2
    payload = json.loads(Path(result["exports"][0]["path"]).read_text())
    resource = payload["resourceSpans"][0]
    spans = resource["scopeSpans"][0]["spans"]
    span = next(item for item in spans if item["name"] == "GET /call")
    assert span["traceId"] == trace_id.zfill(32)
    assert span["spanId"] == child_id.zfill(16)
    assert span["parentSpanId"] == parent_id.zfill(16)
    assert span["kind"] == "SPAN_KIND_SERVER"
    assert span["status"]["code"] == "STATUS_CODE_ERROR"
    assert span["events"][0]["attributes"][0]["value"]["stringValue"] == "failed"
    assert span["links"][0]["traceId"] == "0" * 32
    assert span["links"][0]["spanId"] == "0" * 16
    assert span["links"][0]["attributes"][0]["value"]["stringValue"] == "FOLLOWS_FROM"
    process_tag = next(item for item in resource["resource"]["attributes"] if item["key"] == "host.port")
    assert process_tag["value"]["intValue"] == "8080"
    invalid = next(item for item in spans if item["name"] == "invalid-zero-id")
    assert invalid["traceId"] == "0" * 32
    assert invalid["spanId"] == "0" * 16


def test_supplied_role_on_jaeger_entry_does_not_rewrite_source_or_client(tmp_path: Path):
    trace_id, root_id, client_id = 'abcdef0123456789', '1234567890abcdef', 'fedcba0987654321'
    def raw_span(sid, tags):
        return {'traceID': trace_id, 'spanID': sid, 'operationName': '/lookup',
                'processID': 'p', 'startTime': 10, 'duration': 5,
                'tags': tags, 'references': []}
    trace = {'data': [{'processes': {'p': {'serviceName': 'gateway'}}, 'spans': [
        raw_span(root_id, [{'key': 'component', 'type': 'string', 'value': 'nginx'},
                           {'key': 'http.method', 'type': 'string', 'value': 'GET'}]),
        raw_span(client_id, [{'key': 'span.kind', 'type': 'string', 'value': 'client'}]),
    ]}]}
    raw = tmp_path/'traces-gateway.json'
    raw.write_text(json.dumps(trace), encoding='utf-8')
    original = raw.read_bytes()
    role = {'source': 'native', 'trace_id': trace_id, 'span_id': root_id,
            'original_kind': None, 'supplied_kind': 'SPAN_KIND_SERVER',
            'rule': 'unique declared entry; untyped declared receiver component with actual HTTP method and path'}
    result = export_selection(Store([(str(raw), len(original))]),
                              {'native': {(trace_id, root_id), (trace_id, client_id)}},
                              tmp_path/'out', supplied_server_roles={('native', trace_id, root_id): role})
    payload = json.loads(Path(result['exports'][0]['path']).read_text())
    spans = payload['resourceSpans'][0]['scopeSpans'][0]['spans']
    assert {s['spanId']: s['kind'] for s in spans} == {
        root_id: 'SPAN_KIND_SERVER', client_id: 'SPAN_KIND_CLIENT'}
    assert result['exports'][0]['supplied_server_roles'] == [role]
    assert raw.read_bytes() == original
