from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ebpf_discovery import checkpoint_diagnostic_v4 as diagnostic


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _source(commit="a" * 40):
    return {"run_id": diagnostic.SOURCE_RUN_ID,
            "artifact_id": diagnostic.SOURCE_ARTIFACT_ID,
            "artifact_name": diagnostic.SOURCE_ARTIFACT_NAME,
            "artifact_digest": diagnostic.SOURCE_ARTIFACT_DIGEST,
            "run_sha": commit, "expired": False}


def _training_files(root: Path):
    plans, records, census = [], [], []
    ordinal = 0
    for phase, state, count in [("class_train", "11", 600),
                                *(("calibration", state, 6000)
                                  for state in ("11", "10", "01", "00"))]:
        for _ in range(count):
            attempt = f"attempt-{ordinal}"
            plans.append({"attempt_id": attempt, "phase": phase, "state": state})
            records.append({"attempt_id": attempt, "phase": phase, "state": state})
            census.append({"attempt_key": f"opaque-{ordinal}", "phase": phase, "state": state})
            ordinal += 1
    blocks = [{"phase": "class_train", "state": "11", "attempts": 600,
               "completed_requests": 600}]
    blocks += [{"phase": "calibration", "state": state, "attempts": 6000,
                "completed_requests": 6000} for state in ("11", "10", "01", "00")]
    for name, value in (("plans.json", plans), ("external.json", records),
                        ("census.json", census), ("blocks.json", blocks)):
        _write(root/name, value)
    return plans


def test_exact_full_training_prefix_is_required(tmp_path):
    plans = _training_files(tmp_path)
    loaded, proof = diagnostic.validate_training_prefix(tmp_path)
    assert loaded == plans
    assert proof["plans"] == 24600 and proof["blocks"] == 5
    assert proof["phase_state_counts"] == {
        "calibration:00": 6000, "calibration:01": 6000,
        "calibration:10": 6000, "calibration:11": 6000,
        "class_train:11": 600,
    }
    plans[-1]["state"] = "11"
    _write(tmp_path/"plans.json", plans)
    with pytest.raises(ValueError, match="exact 600"):
        diagnostic.validate_training_prefix(tmp_path)


def test_manifest_verifies_every_file_and_rejects_unmanifested_bytes(tmp_path, monkeypatch):
    commit = "a" * 40
    payload = tmp_path/"plans.json"
    payload.write_bytes(b"[]\n")
    record = {"relative_path": "plans.json", "bytes": payload.stat().st_size,
              "sha256": hashlib.sha256(payload.read_bytes()).hexdigest()}
    manifest = {"schema_version": "v4-training-prefix-checkpoint",
                "identity": {"run_id": str(diagnostic.SOURCE_RUN_ID), "commit": commit,
                             "system": "otel_demo", "mode": "full", "seed": 6},
                "status": "partial_training_capture_only; no forecast or completed cell",
                "source_cutoff_rule": "exact indexed prefixes", "files": {"plans.json": record},
                "new_application_traffic": False}
    _write(tmp_path/"manifest.json", manifest)
    manifest_sha = hashlib.sha256((tmp_path/"manifest.json").read_bytes()).hexdigest()
    _write(tmp_path/"ready.json", {"schema_version": "v4-training-prefix-checkpoint-ready",
        "status": "training_checkpoint_ready", "run_id": str(diagnostic.SOURCE_RUN_ID),
        "commit": commit, "system": "otel_demo", "mode": "full", "seed": 6,
        "manifest_sha256": manifest_sha})
    monkeypatch.setattr(diagnostic, "SOURCE_MANIFEST_SHA256", manifest_sha)
    proof = diagnostic.validate_checkpoint_manifest(tmp_path, _source(commit))
    assert proof["verified_files"] == {"plans.json": {
        "bytes": payload.stat().st_size, "sha256": record["sha256"]}}
    (tmp_path/"unexpected.bin").write_bytes(b"not admitted")
    with pytest.raises(ValueError, match="unmanifested"):
        diagnostic.validate_checkpoint_manifest(tmp_path, _source(commit))


def test_diagnostic_is_actions_only(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    with pytest.raises(RuntimeError, match="GitHub Actions"):
        diagnostic.diagnose(tmp_path/"checkpoint", tmp_path/"out", _source())


def test_workflow_is_fixed_checkpoint_only_and_retains_resources():
    workflow = (Path(__file__).resolve().parents[1]/".github"/"workflows"/
                "diagnose-training-checkpoint-v4.yml").read_text(encoding="utf-8")
    assert str(diagnostic.SOURCE_RUN_ID) in workflow
    assert str(diagnostic.SOURCE_ARTIFACT_ID) in workflow
    assert diagnostic.SOURCE_ARTIFACT_DIGEST in workflow
    assert diagnostic.SOURCE_MANIFEST_SHA256 in workflow
    assert "campaign_v4" not in workflow and "vms.sh start" not in workflow
    assert "setup-v4-swap.sh" in workflow and "capture-v4-resources.sh" in workflow
    assert "checkpoint_diagnostic_v4" in workflow
