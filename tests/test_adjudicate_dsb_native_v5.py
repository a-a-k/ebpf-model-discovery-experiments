import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "adjudicate-dsb-native-v5.py"
SPEC = importlib.util.spec_from_file_location("adjudicate_dsb_native_v5", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def _dump(value) -> bytes:
    return (json.dumps(value, sort_keys=True) + "\n").encode()


def test_preserves_originals_and_calls_only_acquisition_checks(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_SHA", "b" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_REPOSITORY", module.REPOSITORY)
    status = {"system": "deathstarbench", "mode": "absent", "seed": 6,
              "collector": "obi", "smoke": True, "protocol_version": "graph-v5"}
    old = {"complete_for_evaluation": False, "legacy_complete_for_evaluation": True,
           "acquisition": {"valid": False,
                           "problems": [module.OLD_SOLE_PROBLEM]},
           "evaluations": [{"prediction": None, "reason": "preserved"}]}
    index = tmp_path / "source.sqlite"
    connection = sqlite3.connect(index)
    connection.execute("CREATE TABLE spans (service TEXT, source TEXT)")
    connection.execute("INSERT INTO spans VALUES (?, ?)", ("jaeger-all-in-one", "native"))
    connection.commit()
    connection.close()
    files = {
        "evaluation-v5.json": _dump(old), "status.json": _dump(status),
        "observation-index.sqlite": index.read_bytes(),
        "observations/collector.json": _dump({
            "collector": "obi", "source_domain": "deathstarbench-deployment",
            "schema": "collector-provenance-v5"}),
        "observations/drain-evidence.json": _dump({
            "collector": "obi", "technical_complete": True,
            "accepted_receiver_bytes_closed_and_hashed": True}),
        "observations/technical-positive-control.json": _dump({
            "collector": "obi", "selected_ebpf_origin_proven": True,
            "proofs": {"a": {"proven": True}, "b": {"proven": True}}}),
    }
    manifest = {
        "run_id": str(module.RUN_ID), "commit": module.HEAD_SHA,
        "full_artifact_name": module.ARTIFACT_NAME,
        "files_sha256": {name: hashlib.sha256(files[name]).hexdigest()
                         for name in ("evaluation-v5.json", "status.json")},
    }
    files["evaluation-manifest.json"] = _dump(manifest)
    archive = tmp_path / "full.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for name, raw in files.items():
            bundle.writestr(name, raw)

    monkeypatch.setattr(module, "ARTIFACT_SIZE", archive.stat().st_size)
    monkeypatch.setattr(module, "ARTIFACT_DIGEST",
                        "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest())
    artifact = {"id": module.ARTIFACT_ID, "name": module.ARTIFACT_NAME,
                "size_in_bytes": module.ARTIFACT_SIZE, "digest": module.ARTIFACT_DIGEST,
                "expired": False,
                "workflow_run": {"id": module.RUN_ID, "head_sha": module.HEAD_SHA}}
    run = {"id": module.RUN_ID, "head_sha": module.HEAD_SHA,
           "repository": {"full_name": module.REPOSITORY}}
    artifact_path, run_path = tmp_path / "artifact.json", tmp_path / "run.json"
    artifact_path.write_text(json.dumps(artifact))
    run_path.write_text(json.dumps(run))
    calls = []
    real_acquisition = module.evaluate_v5.acquisition_checks

    def acquisition(root, actual_status, actual_declaration):
        calls.append((root, actual_status, actual_declaration))
        assert (root / "observation-index.sqlite").read_bytes() == files["observation-index.sqlite"]
        return real_acquisition(root, actual_status, actual_declaration)

    result = module.adjudicate(
        archive, artifact_path, run_path, tmp_path / "out", acquisition_fn=acquisition)

    assert len(calls) == 1
    assert result["old_evaluation"] == old
    assert result["old_acquisition"] == old["acquisition"]
    assert result["new_acquisition"]["valid"] is True
    assert result["new_acquisition"]["native_observations_by_service"] == {
        "jaeger-all-in-one": 1}
    assert result["new_acquisition"]["native_application_observations_by_service"] == {}
    assert result["new_acquisition"]["native_audit_observations_by_service"] == {
        "jaeger-all-in-one": 1}
    assert result["acquisition_validation_counts_recomputed"] is True
    assert result["forecast_class_outcome_metrics_recomputed"] is False
    assert result["selected_original_members_preserved"] is True
    assert result["source_full_artifact_unchanged"] is True
    assert result["source_full_artifact_retained_in_output"] is False
    assert result["adjudicator"]["head_sha"] == "b" * 40
    assert set(result["adjudicator"]["sources_sha256"]) == {
        "scripts/adjudicate-dsb-native-v5.py",
        "src/ebpf_discovery/evaluate_v5.py",
        "systems/deathstarbench/experiment_v4.py",
    }
    assert (tmp_path / "out/original/evaluation-v5.json").read_bytes() == files["evaluation-v5.json"]


def test_rejects_wrong_fixed_artifact_identity(tmp_path: Path) -> None:
    archive = tmp_path / "full.zip"
    archive.write_bytes(b"not relevant")
    artifact = tmp_path / "artifact.json"
    artifact.write_text(json.dumps({"id": 0}))
    run = tmp_path / "run.json"
    run.write_text("{}")
    try:
        module.adjudicate(archive, artifact, run, tmp_path / "out")
    except ValueError as exc:
        assert "artifact API identity mismatch" in str(exc)
    else:
        raise AssertionError("wrong artifact identity was accepted")


def test_workflow_is_fixed_and_does_not_run_campaign_or_evaluator() -> None:
    workflow = (Path(__file__).resolve().parents[1] / ".github/workflows" /
                "adjudicate-dsb-native-v5.yml").read_text()
    assert str(module.RUN_ID) in workflow and str(module.ARTIFACT_ID) in workflow
    assert "campaign_v5" not in workflow
    assert "evaluate_v5 --campaign" not in workflow
    assert "adjudicate-dsb-native-v5.py" in workflow


def test_adjudicator_cli_imports_source_and_system_adapters() -> None:
    root = SCRIPT.parents[1]
    environment = dict(os.environ, PYTHONPATH=os.pathsep.join((str(root / "src"), str(root))))
    result = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=root,
                            env=environment, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "--artifact-metadata" in result.stdout
    workflow = (root / ".github/workflows/adjudicate-dsb-native-v5.yml").read_text()
    assert "PYTHONPATH: src:." in workflow
