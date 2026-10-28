import hashlib
import json

import pytest

from ebpf_discovery.qualification_readout_v4 import build_readout, main


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def observed(folder):
    write(folder / "observed.json", {
        "services": [{"id": "frontend"}, {"id": "catalog"}],
        "edges": [{"id": "frontend|catalog"}],
        "endpoints": [{"id": "frontend:GET /product"}],
    })
    write(folder / "observed.signal-quality.json", {
        "counts": {"services": 2, "edges": 1, "endpoints": 1},
        "artifact": {"snapshot_id": "snap-1"}, "source_mix": {"records": 4},
        "warnings": ["placement unknown"],
    })
    write(folder / "observed.snapshot.json", {"snapshot_id": "snap-1"})


def branch(folder):
    observed(folder)
    write(folder / "entry-evidence.json", {"source": "native", "roots": [{"request_id": "r1"}],
        "binding_reasons": {"native:unique_declared_entry": 1}, "outcomes_used": False})
    write(folder / "binding.json", {"available": False,
        "unknown": [{"reason": "required_call_missing_or_ambiguous"}]})
    write(folder / "forecast.json", {"available": False,
        "reason": "required_graph_evidence_unavailable", "prediction": None})
    write(folder / "observed-runtime" / "replay-command.json", {
        "returncode": 0, "started_ns": 1, "ended_ns": 2, "argv": ["bering", "serve"]})


def test_readout_retains_computed_graph_binding_forecast_and_not_run(tmp_path):
    folder = tmp_path / "toolchain" / "native" / "raw" / "browse"
    branch(folder)
    result = build_readout(tmp_path, operations=["browse"])
    value = result["branches"]["native"]["raw"]["browse"]
    assert value["status"] == "completed"
    assert value["bering"]["returncode"] == 0
    assert value["entry_evidence"]["roots_count"] == 1
    assert value["observed"]["counts"] == {"services": 2, "edges": 1, "endpoints": 1}
    assert value["observed"]["services"] == ["catalog", "frontend"]
    assert value["observed"]["edges"] == ["frontend|catalog"]
    assert value["binding"]["unknown"][0]["reason"] == "required_call_missing_or_ambiguous"
    assert value["forecast"]["prediction"] is None
    assert value["sheaft"]["status"] == "not_run"
    assert result["branches"]["ebpf"]["raw"]["browse"]["status"] == "not_run"
    assert result["integrity"]["ok"]


def test_rc_zero_with_retained_technical_failure_is_not_completed(tmp_path):
    folder = tmp_path / "toolchain" / "native" / "raw" / "browse"
    branch(folder)
    write(folder / "observed-runtime" / "replay-command.json", {
        "returncode": 0, "status": "technical_failure", "error": "post-ingest hash mismatch",
        "started_ns": 1, "ended_ns": 2, "argv": ["bering", "serve"]})
    result = build_readout(tmp_path, operations=["browse"])
    value = result["branches"]["native"]["raw"]["browse"]
    assert value["status"] == "technical_error"
    assert value["bering"]["stored_status"] == "technical_failure"
    assert value["bering"]["error"] == "post-ingest hash mismatch"
    assert "bering_execution_not_completed" in value["integrity_errors"]


def test_relative_observed_reference_verifies_all_hashes(tmp_path):
    folder = tmp_path / "toolchain" / "native" / "raw" / "browse"
    branch(folder)
    discovery = tmp_path / "toolchain" / "discovery" / "native" / "raw"
    observed(discovery)
    hashes = {name: hashlib.sha256((discovery / name).read_bytes()).hexdigest()
              for name in ("observed.json", "observed.signal-quality.json", "observed.snapshot.json")}
    write(discovery / "observed-runtime" / "replay-command.json", {
        "returncode": 0, "started_ns": 3, "ended_ns": 4, "argv": ["bering", "serve"]})
    write(folder / "observed-reference.json", {"folder": "../../../discovery/native/raw", "files": hashes})
    result = build_readout(tmp_path, operations=["browse"])
    value = result["branches"]["native"]["raw"]["browse"]
    assert value["status"] == "completed"
    assert value["observed"]["provenance"]["kind"] == "reference"
    assert value["observed"]["provenance"]["verified_sha256"] == hashes
    # The actual shared Bering execution record is under the verified target.
    assert value["bering"]["path"].endswith("discovery/native/raw/observed-runtime/replay-command.json")
    assert value["bering"]["started_ns"] == 3


def test_reference_hash_mismatch_is_retained_as_technical_error(tmp_path):
    folder = tmp_path / "toolchain" / "native" / "raw" / "browse"
    branch(folder)
    discovery = tmp_path / "toolchain" / "discovery" / "native" / "raw"
    observed(discovery)
    write(discovery / "observed-runtime" / "replay-command.json", {
        "returncode": 0, "started_ns": 3, "ended_ns": 4, "argv": ["bering", "serve"]})
    hashes = {name: "0" * 64 for name in (
        "observed.json", "observed.signal-quality.json", "observed.snapshot.json")}
    write(folder / "observed-reference.json", {"folder": "../../../discovery/native/raw", "files": hashes})
    result = build_readout(tmp_path, operations=["browse"])
    value = result["branches"]["native"]["raw"]["browse"]
    assert value["status"] == "technical_error"
    assert value["integrity_errors"] == [
        "observed.json:sha256_mismatch", "observed.signal-quality.json:sha256_mismatch",
        "observed.snapshot.json:sha256_mismatch"]
    assert not result["integrity"]["ok"]


def test_zero_source_branch_is_expected_unavailable_and_verifies_input_reference(tmp_path):
    folder = tmp_path / "toolchain" / "ebpf" / "raw" / "browse"
    input_path = tmp_path / "toolchain" / "inputs" / "ebpf" / "raw" / "observations.json"
    write(input_path, {"observations": 0, "exports": []})
    write(folder / "input-reference.json", {"path": "../../../inputs/ebpf/raw/observations.json",
        "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(), "observations": 0, "shared": True})
    write(folder / "entry-evidence.json", {"source": "ebpf", "roots": [], "outcomes_used": False})
    write(folder / "forecast.json", {"available": False, "prediction": None,
        "reason": "no_frozen_source_observations"})
    result = build_readout(tmp_path, operations=["browse"])
    value = result["branches"]["ebpf"]["raw"]["browse"]
    assert value["status"] == "expected_unavailable"
    assert value["input_reference"]["verified"]
    assert value["observed"] is None and value["binding"] is None
    assert value["bering"]["status"] == value["sheaft"]["status"] == "not_run"
    assert result["integrity"]["ok"]
    reference = folder / "input-reference.json"
    broken = json.loads(reference.read_text(encoding="utf-8"))
    broken["sha256"] = "0" * 64
    write(reference, broken)
    broken_result = build_readout(tmp_path, operations=["browse"])
    broken_value = broken_result["branches"]["ebpf"]["raw"]["browse"]
    assert broken_value["status"] == "technical_error"
    assert broken_value["integrity_errors"] == ["input-reference:sha256_mismatch"]
    assert not broken_result["integrity"]["ok"]

    # Pointer metadata cannot declare zero when the hash-verified manifest does not.
    write(input_path, {"observations": 4, "exports": []})
    inconsistent = json.loads(reference.read_text(encoding="utf-8"))
    inconsistent["sha256"] = hashlib.sha256(input_path.read_bytes()).hexdigest()
    inconsistent["observations"] = 0
    write(reference, inconsistent)
    inconsistent_result = build_readout(tmp_path, operations=["browse"])
    inconsistent_value = inconsistent_result["branches"]["ebpf"]["raw"]["browse"]
    assert inconsistent_value["status"] == "technical_error"
    assert "input-reference:observations_mismatch" in inconsistent_value["integrity_errors"]


def test_retained_gnu_time_has_source_path_hash_and_fields(tmp_path):
    timing = tmp_path / "campaign-time.txt"
    timing.write_text("\tElapsed (wall clock) time (h:mm:ss or m:ss): 9:54.21\n"
                      "\tMaximum resident set size (kbytes): 118260\n", encoding="utf-8")
    result = build_readout(tmp_path, operations=["browse"], resources=[("campaign", timing)])
    resource = result["resources"][0]
    assert resource["status"] == "retained"
    assert resource["fields"]["Maximum resident set size (kbytes)"] == "118260"
    assert resource["sha256"] == hashlib.sha256(timing.read_bytes()).hexdigest()


def test_cli_is_actions_only(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    with pytest.raises(SystemExit, match="Actions-only"):
        main(["--replay-dir", str(tmp_path), "--out", str(tmp_path / "out.json")])


def test_cli_writes_and_prints_manifest_in_actions(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    out = tmp_path / "readout.json"
    assert main(["--replay-dir", str(tmp_path), "--out", str(out),
                 "--operation", "browse"]) == 0
    stored = json.loads(out.read_text(encoding="utf-8"))
    printed = json.loads(capsys.readouterr().out)
    assert printed == stored
    assert stored["branches"]["combined"]["network_scope"]["browse"]["status"] == "not_run"
