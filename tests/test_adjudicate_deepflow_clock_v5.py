from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import zipfile

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "adjudicate-deepflow-clock-v5.py"
spec = importlib.util.spec_from_file_location("adjudicate_deepflow_clock_v5", SCRIPT)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


def test_derivation_adds_only_verified_clock_projection_fields():
    original = {"source": "ebpf", "service": "unknown", "trace_id": "", "attributes": {
        "_runtime_identity.source_clock":
            "deepflow_guest_realtime_derived_epoch_us_standalone_ntp_disabled",
        "_runtime_identity.node": "a", "_runtime_identity.start": "10",
        "_runtime_identity.end": "20", "_runtime_identity.host_pid": "41",
        "deepflow.raw.sha256": "f" * 64}}
    relation = {"domain": "guest_realtime_unix_ns", "relation": "documented",
                "evidence": {"sha256": "a" * 64}}
    derived, changed = module._derive_record(original, {"a": relation})
    assert changed is True
    assert original["attributes"].get("_runtime_identity.clock") is None
    assert derived["attributes"]["_runtime_identity.clock"] == relation
    assert derived["attributes"]["_runtime_identity.event_start_ns"] == "10000"
    assert derived["attributes"]["_runtime_identity.event_end_ns"] == "20999"
    assert derived["trace_id"] == "" and derived["service"] == "unknown"
    assert derived["attributes"]["deepflow.raw.sha256"] == "f" * 64


def test_derivation_rejects_missing_exact_source_clock_carriers():
    with pytest.raises(ValueError, match="exact clock carriers"):
        module._derive_record({"attributes": {
            "_runtime_identity.source_clock": "deepflow_guest_realtime_x",
            "_runtime_identity.node": "a", "_runtime_identity.start": "not-an-int",
            "_runtime_identity.end": "20"}}, {"a": {}})
    untouched = {"attributes": {"source": "native"}}
    assert module._derive_record(untouched, {"a": {}}) == (untouched, False)


def test_exact_extraction_is_safe_scoped_and_crc_verified(tmp_path):
    archive, destination = tmp_path / "source.zip", tmp_path / "selected"
    members = {name: b"{}\n" for name in module.FIXED_FILES}
    members.update({
        "runtime-identity-v5/capture-before-x.json": b"capture",
        "observations/deepflow-raw/node-a/prefix/l7_flow_log": b"raw\n",
        "observations/deepflow-agent-standalone-a.yaml": b"global: {}\n",
        "evaluation-v5.json": b"must-not-be-extracted",
        "toolchain/forecast.json": b"must-not-be-extracted",
    })
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name, body in members.items():
            bundle.writestr(name, body)
    proofs = module._extract(archive, destination)
    extracted = {row["path"] for row in proofs}
    assert module.FIXED_FILES <= extracted
    assert "runtime-identity-v5/capture-before-x.json" in extracted
    assert "observations/deepflow-raw/node-a/prefix/l7_flow_log" in extracted
    assert "evaluation-v5.json" not in extracted and "toolchain/forecast.json" not in extracted
    assert all(len(row["zip_crc32"]) == 8 for row in proofs)


def test_source_identity_rejects_unbound_api_before_processing(tmp_path):
    archive = tmp_path / "not-source.zip"; archive.write_bytes(b"not source")
    with pytest.raises(ValueError, match="artifact API identity mismatch"):
        module._verify_source(archive, {"id": 1}, {})


def test_workflow_has_no_empirical_pipeline_or_execution_timeout():
    workflow = (Path(__file__).parents[1] / ".github" / "workflows" /
                "adjudicate-deepflow-clock-v5.yml").read_text()
    assert "timeout-minutes" not in workflow
    assert "adjudicate-deepflow-clock-v5.py" in workflow
    for forbidden in ("campaign-v5.py", "sheaft", "forecast", "evaluate-v5"):
        assert forbidden not in workflow.lower()
