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
    root.attributes.add(key='http.url').value.string_value = 'https://example.test/lookup?token=fixture'
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
    assert any(a.key == 'url.path' and a.value.string_value == '/lookup' for a in exported_span.attributes)
    assert unknown in exported_span.SerializeToString()
    assert raw.read_bytes() == wire
    assert result['exports'][0]['raw_sha256'] == hashlib.sha256(wire).hexdigest()
    supplied = result['exports'][0]['supplied_server_roles'][0]
    assert {k: supplied[k] for k in role} == role
    assert supplied['supplied_url_path']['derived_path'] == '/lookup'
    assert supplied['supplied_url_path']['source_urls'][0]['field'] == 'http.url'
    assert supplied['supplied_url_path']['source_urls'][0]['query_stripped'] is True
    all_result = export_selection(Store([(str(index), len(line))]), {'ebpf': None},
                                  tmp_path/'all', supplied_server_roles={('ebpf', TRACE, SPAN): role})
    assert all_result['observations'] == 1
    assert all_result['exports'][0]['selection'] == 'all_frozen_source_records'
    assert 'selected_ids' not in all_result['exports'][0]
    assert all_result['exports'][0]['raw_prefix_bytes'] == len(line)
    assert all_result['exports'][0]['indexed_wrapper_prefix_sha256'] == hashlib.sha256(line).hexdigest()
    all_wire = ExportTraceServiceRequest()
    all_wire.ParseFromString(Path(all_result['exports'][0]['path']).read_bytes())
    assert unknown in all_wire.resource_spans[0].scope_spans[0].spans[0].SerializeToString()
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


def test_jaeger_per_file_stream_matches_all_per_trace_resource_spans_and_provenance(tmp_path: Path):
    trace_id = "abcdef0123456789"
    def jaeger_span(span_id, value, kind):
        return {"traceID": trace_id, "spanID": span_id,
                "operationName": "GET /same", "processID": "p",
                "startTime": 100, "duration": 4,
                "tags": [{"key": "span.kind", "type": "string", "value": kind},
                         {"key": "conflicting.value", "type": "string", "value": value}],
                "logs": [{"timestamp": 101, "fields": [
                    {"key": "event.id", "type": "int64", "value": 7}]}],
                "references": [{"refType": "FOLLOWS_FROM", "traceID": trace_id,
                                "spanID": "3"}]}
    def trace(*spans):
        return {"traceID": trace_id, "processes": {"p": {
            "serviceName": "api", "tags": [{"key": "process.pid", "type": "int64", "value": 12}]}},
            "spans": list(spans)}
    # Repeated exact source-local identity with disagreeing typed values is
    # retained twice, including cross-trace order and reference evidence.
    queries = [trace(jaeger_span("1", "first", "client")),
               trace(jaeger_span("1", "second", "server"), jaeger_span("2", "third", "client"))]
    raw = tmp_path / "traces-api.json"
    frozen = json.dumps({"data": queries}, separators=(",", ":")).encode()
    raw.write_bytes(frozen + b"\n" + json.dumps({"data": [trace(jaeger_span("4", "tail", "client"))]}).encode())
    store = Store([(str(raw), len(frozen))])
    old = export_selection(store, {"native": None}, tmp_path / "per-trace",
                           native_jaeger_envelope="per_trace")
    new = export_selection(store, {"native": None}, tmp_path / "per-file",
                           native_jaeger_envelope="per_file")
    assert old["observations"] == new["observations"] == 3
    assert len(old["exports"]) == 2 and len(new["exports"]) == 1
    old_resources = [resource for item in old["exports"]
                     for resource in json.loads(Path(item["path"]).read_text())["resourceSpans"]]
    new_resources = json.loads(Path(new["exports"][0]["path"]).read_text())["resourceSpans"]
    assert new_resources == old_resources
    spans = [span for resource in new_resources for span in resource["scopeSpans"][0]["spans"]]
    assert [span["attributes"][1]["value"]["stringValue"] for span in spans] == [
        "first", "second", "third"]
    assert [span["kind"] for span in spans] == [
        "SPAN_KIND_CLIENT", "SPAN_KIND_SERVER", "SPAN_KIND_CLIENT"]
    assert all(span["events"][0]["attributes"][0]["value"]["intValue"] == "7" for span in spans)
    assert all(span["links"][0]["attributes"][0]["value"]["stringValue"] == "FOLLOWS_FROM"
               for span in spans)
    manifest = new["exports"][0]
    assert manifest["native_jaeger_envelope"] == "per_file"
    assert manifest["raw_file"] == str(raw.resolve())
    assert manifest["raw_prefix_bytes"] == len(frozen)
    assert manifest["raw_sha256"] == hashlib.sha256(frozen).hexdigest()
    assert manifest["jaeger_query_traces_seen"] == manifest["jaeger_query_traces_exported"] == 2
    assert manifest["selection"] == "all_frozen_source_records"
    assert "selected_ids" not in manifest
    assert new["native_jaeger_envelope"] == "per_file"
    assert old["native_jaeger_envelope"] == "per_trace"


def test_jaeger_empty_frozen_file_emits_no_envelope(tmp_path: Path):
    raw = tmp_path / "traces-empty.json"
    frozen = b'{"data":[]}'
    raw.write_bytes(frozen + b'\n{"data":[{"spans":[{"spanID":"tail"}]}]}')
    result = export_selection(Store([(str(raw), len(frozen))]), {"native": None}, tmp_path / "out")
    assert result["observations"] == 0
    assert result["exports"] == []
    assert not list((tmp_path / "out").iterdir())


def test_jaeger_query_files_remain_separate_with_their_own_frozen_prefixes(tmp_path: Path):
    rows = []
    for name, value in (("traces-a.json", "a"), ("traces-b.json", "b")):
        path = tmp_path / name
        frozen = json.dumps({"data": [{"processes": {"p": {"serviceName": "same"}},
            "spans": [{"traceID": TRACE, "spanID": SPAN, "processID": "p",
                       "operationName": value, "startTime": 1, "duration": 1}]}]}).encode()
        path.write_bytes(frozen + b"\nignored unindexed tail")
        rows.append((str(path), len(frozen)))
    result = export_selection(Store(rows), {"native": None}, tmp_path / "out")
    assert len(result["exports"]) == 2
    assert [item["raw_file"] for item in result["exports"]] == [
        str((tmp_path / "traces-a.json").resolve()), str((tmp_path / "traces-b.json").resolve())]
    assert [item["observations"] for item in result["exports"]] == [1, 1]
    assert [json.loads(Path(item["path"]).read_text())["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["name"]
            for item in result["exports"]] == ["a", "b"]
    with pytest.raises(ValueError, match="unsupported native Jaeger envelope"):
        export_selection(Store(rows), {"native": None}, tmp_path / "bad",
                         native_jaeger_envelope="per_minute")


def test_jaeger_per_file_preserves_ordered_supplied_roles_and_network_scope(tmp_path: Path):
    trace_id = "abcdef0123456789"
    roots = ("1234567890abcdef", "1234567890abcdee")
    traces = []
    roles = {}
    for number, span_id in enumerate(roots):
        traces.append({"traceID": trace_id,
            "processes": {"p": {"serviceName": "gateway", "tags": [
                {"key": "host.id", "type": "string", "value": "host-a"}]}},
            "spans": [{"traceID": trace_id, "spanID": span_id, "processID": "p",
                "operationName": "/lookup", "startTime": 10 + number, "duration": 5,
                "tags": [{"key": "component", "type": "string", "value": "nginx"},
                         {"key": "http.method", "type": "string", "value": "GET"},
                         {"key": "http.url", "type": "string",
                          "value": f"https://example.test/lookup/{number}?private=fixture"}],
                "references": []}]})
        roles[("native", trace_id, span_id)] = {
            "source": "native", "trace_id": trace_id, "span_id": span_id,
            "original_kind": None, "supplied_kind": "SPAN_KIND_SERVER",
            "rule": "unique declared entry with observed HTTP URL"}
    raw = tmp_path / "traces-gateway.json"
    frozen = json.dumps({"data": traces}, separators=(",", ":")).encode()
    raw.write_bytes(frozen)
    store = Store([(str(raw), len(frozen))])
    old = export_selection(store, {"native": None}, tmp_path / "old",
                           network_scope="declared-network", supplied_server_roles=roles,
                           native_jaeger_envelope="per_trace")
    new = export_selection(store, {"native": None}, tmp_path / "new",
                           network_scope="declared-network", supplied_server_roles=roles,
                           native_jaeger_envelope="per_file")
    old_resources = [resource for item in old["exports"]
                     for resource in json.loads(Path(item["path"]).read_text())["resourceSpans"]]
    new_resources = json.loads(Path(new["exports"][0]["path"]).read_text())["resourceSpans"]
    assert new_resources == old_resources
    old_roles = [role for item in old["exports"] for role in item["supplied_server_roles"]]
    assert new["exports"][0]["supplied_server_roles"] == old_roles
    assert [role["supplied_url_path"]["derived_path"] for role in old_roles] == [
        "/lookup/0", "/lookup/1"]
    assert all(role["supplied_url_path"]["source_urls"][0]["query_stripped"]
               for role in old_roles)
    assert [resource["resource"]["attributes"][-1]["value"]["stringValue"]
            for resource in new_resources] == ["declared-network", "declared-network"]
    assert raw.read_bytes() == frozen


def test_supplied_role_on_jaeger_entry_does_not_rewrite_source_or_client(tmp_path: Path):
    trace_id, root_id, client_id = 'abcdef0123456789', '1234567890abcdef', 'fedcba0987654321'
    def raw_span(sid, tags):
        return {'traceID': trace_id, 'spanID': sid, 'operationName': '/lookup',
                'processID': 'p', 'startTime': 10, 'duration': 5,
                'tags': tags, 'references': []}
    trace = {'data': [{'processes': {'p': {'serviceName': 'gateway'}}, 'spans': [
        raw_span(root_id, [{'key': 'component', 'type': 'string', 'value': 'nginx'},
                           {'key': 'http.method', 'type': 'string', 'value': 'GET'},
                           {'key': 'http.url', 'type': 'string', 'value': 'http://example.test/lookup?id=1'}]),
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
    assert any(a['key'] == 'url.path' and a['value']['stringValue'] == '/lookup'
               for a in next(s for s in spans if s['spanId'] == root_id)['attributes'])
    assert result['exports'][0]['supplied_server_roles'][0]['supplied_url_path']['derived_path'] == '/lookup'
    assert raw.read_bytes() == original
    all_result = export_selection(Store([(str(raw), len(original))]), {'native': None},
                                  tmp_path/'all', supplied_server_roles={('native', trace_id, root_id): role})
    assert all_result['observations'] == 2
    assert 'selected_ids' not in all_result['exports'][0]
    assert all_result['exports'][0]['supplied_server_roles'][0]['supplied_url_path']['derived_path'] == '/lookup'


def test_all_frozen_source_records_excludes_unindexed_tail_and_other_source(tmp_path: Path):
    observations = tmp_path/'observations'
    observations.mkdir()
    zero = _span('zero')
    zero['traceId'] = '0' * 32
    zero['spanId'] = '0' * 16
    first = (json.dumps(_payload(_span('first'), zero))+'\n').encode()
    tail = (json.dumps(_payload(_span('tail')))+'\n').encode()
    ebpf = observations/'a.jsonl'
    ebpf.write_bytes(first+tail)
    native = observations/'native-node-a.jsonl'
    native.write_bytes(first)
    result = export_selection(Store([(str(ebpf), len(first)), (str(native), len(first))]),
                              {'ebpf': None, 'native': set()}, tmp_path/'out')
    assert result['observations'] == 2
    assert len(result['exports']) == 1
    item = result['exports'][0]
    assert item['source'] == 'ebpf'
    assert item['raw_prefix_bytes'] == len(first)
    assert item['raw_sha256'] == hashlib.sha256(first).hexdigest()
    assert item['selection'] == 'all_frozen_source_records'
    assert 'selected_ids' not in item
    payload = json.loads(Path(item['path']).read_text())
    spans = payload['resourceSpans'][0]['scopeSpans'][0]['spans']
    assert [s['attributes'][0]['value']['stringValue'] for s in spans] == ['first', 'zero']
    assert spans[1]['traceId'] == '0' * 32 and spans[1]['spanId'] == '0' * 16
    assert ebpf.read_bytes() == first+tail
    assert native.read_bytes() == first


def test_supplied_url_path_uses_observed_url_only_and_rejects_contradictions(tmp_path: Path):
    span = _span('one')
    span.pop('kind')
    attrs = span['attributes']
    attrs.extend([
        {'key': 'http.url', 'value': {'stringValue': 'https://example.test/actual/path?x=1'}},
        {'key': 'url.full', 'value': {'stringValue': 'https://example.test/actual/path?x=2'}},
    ])
    role = {'source': 'native', 'trace_id': TRACE, 'span_id': SPAN,
            'original_kind': None, 'path': '/declared/different',
            'supplied_kind': 'SPAN_KIND_SERVER'}
    raw = tmp_path/'native-node-a.jsonl'

    def export(attributes, folder):
        span['attributes'] = attributes
        line = (json.dumps(_payload(span))+'\n').encode()
        raw.write_bytes(line)
        return export_selection(Store([(str(raw), len(line))]), {'native': None},
                                tmp_path/folder, supplied_server_roles={('native', TRACE, SPAN): role})

    result = export(attrs, 'derived')
    item = result['exports'][0]
    exported = json.loads(Path(item['path']).read_text())['resourceSpans'][0]['scopeSpans'][0]['spans'][0]
    assert exported['kind'] == 'SPAN_KIND_SERVER'
    assert [a['value']['stringValue'] for a in exported['attributes'] if a['key'] == 'url.path'] == ['/actual/path']
    derivation = item['supplied_server_roles'][0]['supplied_url_path']
    assert derivation['derived_path'] == '/actual/path' != role['path']
    assert {a['field'] for a in derivation['source_urls']} == {'http.url', 'url.full'}
    assert all(a['query_stripped'] for a in derivation['source_urls'])
    original_attrs = json.loads(raw.read_text())['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['attributes']
    assert all(a['key'] != 'url.path' for a in original_attrs)

    existing = attrs + [{'key': 'url.path', 'value': {'stringValue': '/actual/path'}}]
    result = export(existing, 'existing')
    item = result['exports'][0]
    assert 'supplied_url_path' not in item['supplied_server_roles'][0]
    exported = json.loads(Path(item['path']).read_text())['resourceSpans'][0]['scopeSpans'][0]['spans'][0]
    assert sum(a['key'] == 'url.path' for a in exported['attributes']) == 1

    with pytest.raises(ValueError, match='contradictory observed HTTP URL and url.path'):
        export(attrs + [{'key': 'url.path', 'value': {'stringValue': '/other'}}], 'bad-explicit')
    with pytest.raises(ValueError, match='contradictory observed HTTP URL paths'):
        export(attrs[:-1] + [{'key': 'url.full', 'value': {'stringValue': 'https://example.test/other'}}],
               'bad-urls')
