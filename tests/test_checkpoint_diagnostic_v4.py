from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ebpf_discovery import checkpoint_diagnostic_v4 as diagnostic


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _source(commit=None, profile_name=diagnostic.DEFAULT_PROFILE):
    profile = diagnostic.PROFILES[profile_name]
    commit = commit or profile["commit"]
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
            plans.append({"attempt_id": attempt, "phase": phase, "state": state,
                          "http_steps": [{"request_id": f"request-{ordinal}"}]})
            records.append({"attempt_id": attempt, "phase": phase, "state": state,
                            "http_steps": [{"request_id": f"request-{ordinal}"}]})
            census.append({"attempt_key": hashlib.sha256(attempt.encode()).hexdigest(),
                           "step_ids": [f"request-{ordinal}"], "phase": phase, "state": state})
            ordinal += 1
    blocks = [{"phase": "class_train", "state": "11", "attempts": 600,
               "completed_requests": 600}]
    blocks += [{"phase": "calibration", "state": state, "attempts": 6000,
                "completed_requests": 6000} for state in ("11", "10", "01", "00")]
    preparation = [{"attempt_id": f"warmup-{index}", "phase": "preparation",
                    "state": "11" if index < 3 else ("10", "11", "01", "00")[(index-3)//3]}
                   for index in range(15)]
    records = [*records, *preparation]
    for name, value in (("plans.json", plans), ("external.json", records),
                        ("census.json", census), ("blocks.json", blocks)):
        _write(root/name, value)
    _write(root/"preparation-operations.json", preparation)
    return plans


def test_exact_full_training_prefix_is_required(tmp_path):
    plans = _training_files(tmp_path)
    loaded, proof = diagnostic.validate_training_prefix(tmp_path)
    assert loaded == plans
    assert proof["plans"] == 24600 and proof["blocks"] == 5
    assert proof["primary_external_records"] == 24600
    assert proof["preparation_external_records"] == 15
    assert proof["all_external_records"] == 24615
    assert proof["phase_state_counts"] == {
        "calibration:00": 6000, "calibration:01": 6000,
        "calibration:10": 6000, "calibration:11": 6000,
        "class_train:11": 600,
    }
    plans[-1]["state"] = "11"
    _write(tmp_path/"plans.json", plans)
    with pytest.raises(ValueError, match="exact 600"):
        diagnostic.validate_training_prefix(tmp_path)


def test_census_and_preparation_identities_must_match_their_sources(tmp_path):
    _training_files(tmp_path)
    census = json.loads((tmp_path/"census.json").read_text())
    census[0]["attempt_key"] = "0" * 64
    _write(tmp_path/"census.json", census)
    with pytest.raises(ValueError, match="census or external attempt identities"):
        diagnostic.validate_training_prefix(tmp_path)

    _training_files(tmp_path)
    records = json.loads((tmp_path/"external.json").read_text())
    records[-1]["attempt_id"] = records[-2]["attempt_id"]
    _write(tmp_path/"external.json", records)
    with pytest.raises(ValueError, match="preparation records"):
        diagnostic.validate_training_prefix(tmp_path)


def test_census_uses_actual_steps_and_accepts_unissued_plan_suffix(tmp_path):
    _training_files(tmp_path)
    plans = json.loads((tmp_path/"plans.json").read_text())
    plans[0]["http_steps"] = [{"request_id": "request-0"},
                              {"request_id": "unissued-1"},
                              {"request_id": "unissued-2"}]
    _write(tmp_path/"plans.json", plans)
    # The retained external row and census contain only the first dispatched
    # request after a terminal failure; planned suffixes are not fabricated.
    _, proof = diagnostic.validate_training_prefix(tmp_path)
    assert proof["primary_external_records"] == 24600

    records = json.loads((tmp_path/"external.json").read_text())
    records[0]["http_steps"] = [{"request_id": "not-in-the-plan"}]
    _write(tmp_path/"external.json", records)
    with pytest.raises(ValueError, match="absent from the plan"):
        diagnostic.validate_training_prefix(tmp_path)


@pytest.mark.parametrize('profile_name', [diagnostic.DEFAULT_PROFILE,
    diagnostic.LARGE_GC_PROFILE, diagnostic.DSB_GC_PROFILE])
def test_manifest_verifies_every_file_and_rejects_unmanifested_bytes(tmp_path, monkeypatch, profile_name):
    profile = diagnostic.PROFILES[profile_name]
    commit = profile["commit"]
    source = {key: profile[key] for key in ('run_id', 'artifact_id', 'artifact_name', 'artifact_digest')}
    source.update(run_sha=commit, expired=False)
    payload = tmp_path/"plans.json"
    payload.write_bytes(b"[]\n")
    record = {"relative_path": "plans.json", "bytes": payload.stat().st_size,
              "sha256": hashlib.sha256(payload.read_bytes()).hexdigest()}
    manifest = {"schema_version": "v4-training-prefix-checkpoint",
                "identity": {"run_id": str(profile['run_id']), "commit": commit,
                             "system": profile['system'], "mode": "full", "seed": 6},
                "status": "partial_training_capture_only; no forecast or completed cell",
                "source_cutoff_rule": "exact indexed prefixes", "files": {"plans.json": record},
                "new_application_traffic": False}
    _write(tmp_path/"manifest.json", manifest)
    manifest_sha = hashlib.sha256((tmp_path/"manifest.json").read_bytes()).hexdigest()
    _write(tmp_path/"ready.json", {"schema_version": "v4-training-prefix-checkpoint-ready",
        "status": "training_checkpoint_ready", "run_id": str(profile['run_id']),
        "commit": commit, "system": profile['system'], "mode": "full", "seed": 6,
        "manifest_sha256": manifest_sha})
    monkeypatch.setitem(profile, "manifest_sha256", manifest_sha)
    proof = diagnostic.validate_checkpoint_manifest(tmp_path, source, profile_name)
    assert proof["verified_files"] == {"plans.json": {
        "bytes": payload.stat().st_size, "sha256": record["sha256"]}}
    (tmp_path/"unexpected.bin").write_bytes(b"not admitted")
    with pytest.raises(ValueError, match="unmanifested"):
        diagnostic.validate_checkpoint_manifest(tmp_path, source, profile_name)
    (tmp_path / 'unexpected.bin').unlink()
    manifest['identity']['system'] = 'wrong-system'
    _write(tmp_path / 'manifest.json', manifest)
    monkeypatch.setitem(profile, 'manifest_sha256', diagnostic.digest(tmp_path / 'manifest.json'))
    with pytest.raises(ValueError, match='manifest identity'):
        diagnostic.validate_checkpoint_manifest(tmp_path, source, profile_name)


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


def test_named_large_profile_is_exact_and_does_not_change_default():
    default = diagnostic.PROFILES[diagnostic.DEFAULT_PROFILE]
    large = diagnostic.PROFILES[diagnostic.LARGE_GC_PROFILE]
    assert default["artifact_id"] == diagnostic.SOURCE_ARTIFACT_ID
    assert default["bering_child_go_environment"] == {}
    assert large == {
        "system": "otel_demo",
        "run_id": 40754529169,
        "artifact_id": 12847933267,
        "artifact_name": "training-v4-otel_demo-full-6-40754529169",
        "artifact_digest": "sha256:ba0289fd1e0cefd4be96cfbf0a0ac4a335db2ef4f748de4b0ffa63aa00c2c422",
        "manifest_sha256": "b90d303797e4285d16659b4515195b0fc58276d8d4200ec6a9fa9eae070e333c",
        "commit": "72133c00df3f7e4150a3f737dee33e4bee12527d",
        "bering_child_go_environment": {"GOMEMLIMIT": "12GiB", "GODEBUG": "gctrace=1"},
    }
    source = {"run_id": large["run_id"], "artifact_id": large["artifact_id"],
              "artifact_name": large["artifact_name"], "artifact_digest": large["artifact_digest"],
              "run_sha": large["commit"], "expired": False}
    diagnostic.validate_artifact_identity(source, diagnostic.LARGE_GC_PROFILE)
    source["artifact_id"] = diagnostic.SOURCE_ARTIFACT_ID
    with pytest.raises(ValueError, match="identity or digest"):
        diagnostic.validate_artifact_identity(source, diagnostic.LARGE_GC_PROFILE)


@pytest.mark.parametrize('profile_name,workflow_name', [
    (diagnostic.LARGE_GC_PROFILE, 'diagnose-large-training-checkpoint-v4.yml'),
    (diagnostic.DSB_GC_PROFILE, 'diagnose-dsb-training-checkpoint-v4.yml'),
])
def test_large_profile_workflow_retains_full_diagnostic_and_child_only_gc_setting(profile_name, workflow_name):
    workflow = (Path(__file__).resolve().parents[1]/".github"/"workflows"/
                workflow_name).read_text(encoding="utf-8")
    profile = diagnostic.PROFILES[profile_name]
    for value in (profile["run_id"], profile["artifact_id"], profile["artifact_digest"],
                  profile["manifest_sha256"], profile["commit"]):
        assert str(value) in workflow
    assert f"--profile {profile_name}" in workflow
    assert profile['system'] in profile['artifact_name']
    assert "GOMEMLIMIT" not in workflow and "GOGC" not in workflow and "GODEBUG" not in workflow
    assert "BERING_GC_HEARTBEAT" in workflow and "tail -n 3" in workflow
    assert "stat --printf='path=%n inode=%i bytes=%s mtime=%Y" in workflow
    assert "campaign_v4" not in workflow and "vms.sh start" not in workflow
