import hashlib
import json
from pathlib import Path
import runpy
import pytest

from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest


def helper():
    return runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit-dsb-capture.py"))


def request():
    result = ExportTraceServiceRequest()
    for service, sid, parent in (("checkout", 1, 0), ("shipping", 2, 1)):
        resource = result.resource_spans.add()
        resource.resource.attributes.add(key="service.name").value.string_value = service
        span = resource.scope_spans.add().spans.add(name="POST /get-quote", kind=2)
        span.trace_id = bytes.fromhex("01" * 16)
        span.span_id = sid.to_bytes(8)
        if parent:
            span.parent_span_id = parent.to_bytes(8)
        span.attributes.add(key="http.request.method").value.string_value = "POST"
        span.attributes.add(key="url.path").value.string_value = "/get-quote"
    return result


def test_literal_native_projection_preserves_ids_attributes_and_default_key():
    inspect = helper()["native_span_fields"]
    message = request()
    message.resource_spans[1].scope_spans[0].spans[0].attributes.add().value.string_value = "unnamed"
    binary = list(inspect(message.SerializeToString(), "application/x-protobuf"))
    payload = MessageToDict(message)
    for resource, original in zip(payload["resourceSpans"], message.resource_spans, strict=True):
        span, source = resource["scopeSpans"][0]["spans"][0], original.scope_spans[0].spans[0]
        for name, value in (("traceId", source.trace_id), ("spanId", source.span_id), ("parentSpanId", source.parent_span_id)):
            span[name] = value.hex()
    textual = list(inspect(json.dumps(payload).encode(), "application/json"))
    assert binary == textual
    assert binary[1]["fields"]["span"]["parentSpanId"] == "0000000000000001"
    assert binary[1]["fields"]["span"]["attributes"][-1] == {"value": {"stringValue": "unnamed"}}


def test_parent_evidence_keeps_conflicting_variants_and_never_crosses_trace():
    functions = helper()
    fields = list(functions["native_span_fields"](request().SerializeToString(), "application/x-protobuf"))
    changed = json.loads(json.dumps(fields[0]))
    changed["fields"]["span"]["name"] = "conflicting original variant"
    other_trace = json.loads(json.dumps(fields[0]))
    other_trace["fields"]["span"]["traceId"] = "02" * 16
    rows = {}
    for item in [*fields, changed, other_trace]:
        digest = hashlib.sha256(json.dumps(item["fields"], sort_keys=True).encode()).hexdigest()
        rows[digest] = {"service": item["service"], "fields": item["fields"], "count": 1, "witnesses": []}
    summary = functions["shipping_summary"](rows)
    child = next(row for row in summary["checkout_shipping_variants"] if row["service"] == "shipping")
    assert summary["ambiguous_same_trace_span_identities"] == 1
    assert len(child["actual_same_trace_parent_variants"]) == 2
    assert {row["fields"]["span"]["name"] for row in child["actual_same_trace_parent_variants"]} == {
        "POST /get-quote", "conflicting original variant"}


def test_conflicting_service_names_are_not_labelled_as_unique_shipping():
    message = request()
    message.resource_spans[1].resource.attributes.add(key="service.name").value.string_value = "other"
    rows = list(helper()["native_span_fields"](message.SerializeToString(), "application/x-protobuf"))
    assert rows[1]["service"] is None


def test_zero_trace_identity_does_not_create_a_parent_relation():
    functions = helper()
    message = request()
    for resource in message.resource_spans:
        resource.scope_spans[0].spans[0].trace_id = bytes(16)
    rows = {str(index): {"service": item["service"], "fields": item["fields"], "count": 1, "witnesses": []}
            for index, item in enumerate(functions["native_span_fields"](message.SerializeToString(), "application/x-protobuf"))}
    summary = functions["shipping_summary"](rows)
    assert all(not row["actual_same_trace_parent_variants"] for row in summary["checkout_shipping_variants"])


def test_direct_toolchain_layout_is_not_extracted_over_the_retained_tree(tmp_path):
    functions = helper()
    tree = tmp_path / "toolchain"
    tree.mkdir()
    saved = tree / "original.json"
    saved.write_text("original")
    def forbidden(*args, **kwargs):
        raise AssertionError("direct retained tree must not be overwritten")
    functions["retained_toolchain"].__globals__["unpack"] = forbidden
    assert functions["retained_toolchain"](tmp_path)["unpacked"] is False
    assert saved.read_text() == "original"


def test_packed_toolchain_layout_uses_the_existing_unpacker(tmp_path):
    functions = helper()
    calls = []
    def existing_unpack(source, destination, *, kind):
        calls.append((source, destination, kind))
        return {"original_package_proof": True}
    functions["retained_toolchain"].__globals__["unpack"] = existing_unpack
    assert functions["retained_toolchain"](tmp_path) == {"original_package_proof": True}
    assert calls == [(tmp_path / "toolchain-package", tmp_path / "toolchain", "toolchain")]


def test_original_jsonl_prefix_records_keep_offsets_hashes_and_declared_encoding():
    functions = helper()
    first = json.dumps({"payload": {"resourceSpans": []}, "id_encoding": "base64"}).encode() + b"\n"
    second = b'{"resourceSpans":[]}\n'
    records = list(functions["original_jsonl_records"](first + second))
    assert records[0] == ({"resourceSpans": []}, "base64", {
        "offset": 0, "length": len(first), "raw_record_sha256": hashlib.sha256(first).hexdigest()})
    assert records[1][1:] == ("hex", {"offset": len(first), "length": len(second),
                                       "raw_record_sha256": hashlib.sha256(second).hexdigest()})
    with pytest.raises(ValueError, match="incomplete JSONL record"):
        list(functions["original_jsonl_records"](first + second.rstrip(b"\n")))


def test_saved_native_audit_reads_the_indexed_jsonl_prefix_and_exact_accepted_sequence(tmp_path):
    functions = helper()
    root, compact = tmp_path / "capture", tmp_path / "compact"
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) + "\n")
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    payload = MessageToDict(request())
    for resource in payload["resourceSpans"]:
        span = resource["scopeSpans"][0]["spans"][0]
        import base64
        for field in ("traceId", "spanId", "parentSpanId"):
            if field in span:
                span[field] = base64.b64decode(span[field]).hex()
    lines = [(json.dumps({"resourceSpans": [resource]}) + "\n").encode() for resource in payload["resourceSpans"]]
    original = root / "native/training/native-node-a.jsonl"
    original.parent.mkdir(parents=True)
    original.write_bytes(b"".join(lines) + b"later data outside indexed prefix")
    prefix = b"".join(lines)
    folder = root / "toolchain/inputs/native/raw"
    exports = []
    for index, line in enumerate(lines):
        path = folder / f"native-{index + 1:06d}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(line)
        exports.append({"path": path.as_posix(), "source": "native", "content_type": "application/json",
            "sha256": sha(path), "raw_file": original.as_posix(), "raw_prefix_bytes": len(prefix),
            "raw_sha256": hashlib.sha256(prefix).hexdigest(), "raw_record_sha256": hashlib.sha256(line).hexdigest()})
    write(folder / "observations.json", {"observations": 2,
        "selection_by_source": {"native": "all_frozen_source_records"}, "exports": exports})
    graph = root / "toolchain/discovery/native/raw/observed.json"
    write(graph, {"services": [], "edges": [], "endpoints": []})
    runtime = graph.parent / "observed-runtime"
    sequence = runtime / "accepted-request-sequence.jsonl"
    sequence.parent.mkdir()
    sequence.write_text("".join(json.dumps({"http_status": 200, "endpoint": "/v1/traces", "content_sha256": row["sha256"]}) + "\n" for row in exports))
    write(runtime / "replay-command.json", {"status": "complete", "input_observations": 2,
        "ingest": {"spans": 2, "dropped_spans": 0}, "accepted_request_sequence": {
            "path": sequence.as_posix(), "sha256": sha(sequence), "bytes": sequence.stat().st_size, "requests": 2}})
    write(root / "toolchain/forecasts.json", {"unchanged": True})
    frozen = {path.relative_to(root).as_posix(): sha(path) for path in (root / "toolchain").rglob("*") if path.is_file()}
    write(root / "freeze-integrity.json", {"all_unchanged": True, "sha256_by_path": frozen})
    for name, value in (("evaluation-v5.json", {"evidence": {"graphs": []}}), ("status.json", {}),
                        ("evidence-v4.json", {}), ("observations/collector.json", {})):
        write(compact / name, value)
    for name in ("freeze-integrity.json", "toolchain/forecasts.json"):
        write(compact / name, json.loads((root / name).read_text()))
    write(compact / "evaluation-manifest.json", {"files_sha256": {name: sha(compact / name) for name in (
        "evaluation-v5.json", "status.json", "evidence-v4.json", "freeze-integrity.json", "toolchain/forecasts.json")}})
    result = functions["audit"](root, compact, source_arm="native")
    assert result["native_raw_input_span_fields_equal"] is True
    assert result["frozen_requests"] == result["original_native_jsonl_record_claims_verified"] == 2
    assert result["original_otlp_inventory"]["spans"] == 2
    assert result["bering_accepted_sequence"]["source_manifest_sequence_equal"] is True
    assert original.read_bytes().endswith(b"later data outside indexed prefix")


def test_ebpf_comparison_matches_exact_trace_and_original_wire_without_new_parents(tmp_path):
    functions = helper()
    message = request()
    second = message.resource_spans[1].scope_spans[0].spans[0]
    second.trace_id = bytes.fromhex("02" * 16)
    second.span_id = message.resource_spans[0].scope_spans[0].spans[0].span_id
    body = message.SerializeToString()
    original = tmp_path / "observations/a.raw/capture/body.pb"
    original.parent.mkdir(parents=True)
    original.write_bytes(body)
    folder = tmp_path / "toolchain/inputs/ebpf/raw"
    folder.mkdir(parents=True)
    exported = folder / "ebpf-000001.pb"
    exported.write_bytes(body)
    digest = hashlib.sha256(body).hexdigest()
    manifest = folder / "observations.json"
    manifest.write_text(json.dumps({"observations": 2, "selection_by_source": {"ebpf": "all_frozen_source_records"},
        "exports": [{"path": exported.as_posix(), "source": "ebpf", "content_type": "application/x-protobuf",
                     "sha256": digest, "raw_file": original.as_posix(), "raw_sha256": digest}]}))
    frozen = {path.relative_to(tmp_path).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in (exported, manifest)}
    wanted = {("01" * 16, "0000000000000001")}
    facts = functions["ebpf_parent_matches"](tmp_path, frozen, wanted, lambda value: value)
    assert facts["spans"] == 2
    assert len(facts["matches"]) == 1
    assert len(facts["matches"][0]["original_variants"]) == 1
    assert facts["matches"][0]["input_span"]["service"] == "checkout"
    original.write_bytes(b"changed receiver body")
    with pytest.raises(ValueError, match="original receiver body changed"):
        functions["ebpf_parent_matches"](tmp_path, frozen, wanted, lambda value: value)
