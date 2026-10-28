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
    write(folder / "observations.selection.json", {"observations": 4, "outcomes_used": False})
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
    assert value["selection"] == {"observations": 4, "outcomes_used": False}
    assert value["observed"]["counts"] == {"services": 2, "edges": 1, "endpoints": 1}
    assert value["observed"]["services"] == ["catalog", "frontend"]
    assert value["observed"]["edges"] == ["frontend|catalog"]
    assert value["binding"]["unknown"][0]["reason"] == "required_call_missing_or_ambiguous"
    assert value["forecast"]["prediction"] is None
    assert value["sheaft"]["status"] == "not_run"
    assert result["branches"]["ebpf"]["raw"]["browse"]["status"] == "not_run"
    assert result["integrity"]["ok"]


def test_relative_observed_reference_verifies_all_hashes(tmp_path):
    folder = tmp_path / "toolchain" / "native" / "raw" / "browse"
    branch(folder)
    discovery = tmp_path / "toolchain" / "discovery" / "native" / "raw"
    observed(discovery)
    hashes = {name: hashlib.sha256((discovery / name).read_bytes()).hexdigest()
              for name in ("observed.json", "observed.signal-quality.json", "observed.snapshot.json")}
    write(folder / "observed-reference.json", {"folder": "../../../discovery/native/raw", "files": hashes})
    result = build_readout(tmp_path, operations=["browse"])
    value = result["branches"]["native"]["raw"]["browse"]
    assert value["status"] == "completed"
    assert value["observed"]["provenance"]["kind"] == "reference"
    assert value["observed"]["provenance"]["verified_sha256"] == hashes


def test_reference_hash_mismatch_is_retained_as_technical_error(tmp_path):
    folder = tmp_path / "toolchain" / "native" / "raw" / "browse"
    branch(folder)
    discovery = tmp_path / "toolchain" / "discovery" / "native" / "raw"
    observed(discovery)
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
