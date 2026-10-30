import gzip
from pathlib import Path
import runpy
from collections import Counter

import pytest
from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
import json
import hashlib


@pytest.mark.parametrize("representation", ["protobuf", "gzip", "json"])
def test_saved_inventory_counts_every_resource_scope_and_preserves_parent_absence(representation):
    helper = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit-dsb-capture.py"))
    request = ExportTraceServiceRequest()
    for service in ("first", "second"):
        resource = request.resource_spans.add()
        resource.resource.attributes.add(key="service.name").value.string_value = service
        for index in range(2):
            span = resource.scope_spans.add().spans.add(kind=3)
            span.attributes.add(key="rpc.system.name").value.string_value = "grpc"
            span.attributes.add(key="rpc.method").value.string_value = "Example/Call"
            if index:
                span.parent_span_id = bytes.fromhex("0000000000000001")
    wire, content_type, encoding = request.SerializeToString(), "application/x-protobuf", ""
    if representation == "gzip":
        wire, encoding = gzip.compress(wire), "gzip"
    elif representation == "json":
        payload = MessageToDict(request)
        for resource in payload["resourceSpans"]:
            for index, scope in enumerate(resource["scopeSpans"]):
                scope["spans"][0]["parentSpanId"] = f"{index:016x}"
        wire, content_type = json.dumps(payload).encode(), "application/json"
    joints, witnesses = Counter(), {}
    counts = helper["inventory"](wire, content_type, encoding,
        joints=joints, witnesses=witnesses, locator={"sha256": "synthetic"})
    assert counts["spans"] == counts['rpc.method:"Example/Call"'] == 4
    assert counts['rpc.system.name:"grpc"'] == 4
    assert counts["no_nonzero_parent"] == counts["nonzero_parent"] == 2
    assert counts['rpc.system:"grpc"'] == 0
    assert len(joints) == 2
    assert len(witnesses) == 2
    assert {json.loads(key)["service"] for key in joints} == {"first", "second"}


def test_capture_member_mapping_rejects_traversal_and_unknown_original_roots():
    helper = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit-dsb-capture.py"))
    assert helper["original_member"]("/original/work/campaign/observations/a.pb") == "observations/a.pb"
    for path in ("/original/observations/../outside", "/unknown/path"):
        with pytest.raises(ValueError):
            helper["original_member"](path)


def test_conflicting_resource_identity_never_becomes_a_unique_joint_service():
    helper = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit-dsb-capture.py"))
    request = ExportTraceServiceRequest()
    resource = request.resource_spans.add()
    for name in ("first", "second"):
        resource.resource.attributes.add(key="service.name").value.string_value = name
    resource.scope_spans.add().spans.add()
    joints = Counter()
    counts = helper["inventory"](request.SerializeToString(), "application/x-protobuf",
                                  joints=joints, witnesses={})
    assert counts["ambiguous_service_identity"] == 1
    signature = json.loads(next(iter(joints)))
    assert signature["service"] is None
    assert signature["attribute_conflicts"][0]["key"] == "service.name"


def test_raw_accounting_completeness_rejects_a_missing_discarded_record(tmp_path):
    helper = runpy.run_path(str(Path(__file__).parents[1] / "scripts/audit-dsb-capture.py"))
    folder = tmp_path / "observations/deepflow-raw/node-a/003-final"
    folder.mkdir(parents=True)
    wire = b'{"l7_protocol":"Memcached"}\n{"l7_protocol":"Other"}\npending'
    raw = folder / "l7_flow_log"
    raw.write_bytes(wire)
    prefix = {}
    records = list(helper["iter_complete_records"](raw, prefix, source_file="a/l7_flow_log",
                    retained_file=raw.relative_to(tmp_path / "observations").as_posix()))
    rows = [{**{k: getattr(record, k) for k in ("source_file", "retained_file", "offset", "length", "sha256")},
             "node": "a", "capture_stage": "003-final", "status": "unclassified"} for record in records]
    snapshot = {"node": "a", "stage": "003-final", "files": [{"snapshot_name": "l7_flow_log",
        "source_name": "l7_flow_log", "copied_sha256": hashlib.sha256(wire).hexdigest(),
        "copied_bytes": len(wire), "codec": prefix}]}
    (folder / "snapshot.json").write_text(json.dumps(snapshot))
    accounting = tmp_path / "observations/deepflow-codec-accounting.jsonl"
    accounting.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    facts = helper["deepflow_accounting"](tmp_path)
    assert facts["all_complete_raw_records_accounted"] is True
    assert facts["unique_first_seen_records"] == 2
    assert facts["snapshots"][0]["pending_tail_bytes"] == len(b"pending")
    accounting.write_text(json.dumps(rows[0]) + "\n")
    with pytest.raises(ValueError, match="complete raw record lacks unique codec accounting"):
        helper["deepflow_accounting"](tmp_path)
