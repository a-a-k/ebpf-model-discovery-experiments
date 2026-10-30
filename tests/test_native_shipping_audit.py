import hashlib
import json
from pathlib import Path
import runpy

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
