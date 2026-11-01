import hashlib
import json
from pathlib import Path

import pytest
import requests

from ebpf_discovery import remote_toolchain_v4 as remote


@pytest.fixture
def copied_checkpoint(tmp_path):
    live = tmp_path / "work/campaign"
    checkpoint = live.parent / "training-checkpoint"
    live.mkdir(parents=True)
    checkpoint.mkdir()
    files = {}
    for name, body in {"plans.json": b"[]\n", "observations/capture.jsonl": b'{"value":1}\n'}.items():
        for root in (live, checkpoint):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        files[name] = {"relative_path": name, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}
    identity = {"run_id": "77", "commit": "c" * 40, "system": "deathstarbench", "mode": "full", "seed": 6}
    manifest = {"schema_version": "v4-training-prefix-checkpoint", "identity": identity,
        "status": "partial_training_capture_only; no forecast or completed cell", "files": files}
    (checkpoint / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    expected = {**identity, "manifest_sha256": remote._sha(checkpoint / "manifest.json"),
        "artifact_id": "42", "artifact_name": "training-v4-deathstarbench-full-6-77",
        "artifact_digest": "sha256:" + "a" * 64}
    (checkpoint / "ready.json").write_text(json.dumps({**identity, "manifest_sha256": expected["manifest_sha256"],
        "status": "training_checkpoint_ready"}), encoding="utf-8")
    (checkpoint / "release.json").write_text(json.dumps({**expected, "upload_success": True}), encoding="utf-8")
    _, proof = remote._validate_checkpoint(checkpoint, expected)
    artifact = {"id": 42, "name": expected["artifact_name"], "digest": expected["artifact_digest"],
        "expired": False, "size_in_bytes": 1234, "workflow_run": {"id": 77, "head_sha": identity["commit"]}}
    state = live / "infrastructure/remote-toolchain-v4"
    state.mkdir(parents=True)
    class Session:
        gets = 0
        def get(self, url, **kwargs):
            assert url == "https://api.github.com/repos/owner/repo/actions/artifacts/42"
            self.gets += 1
            response = requests.Response()
            response.status_code = 200
            response._content = json.dumps(artifact).encode()
            return response
    return checkpoint, live, expected, proof, artifact, state, Session()


def release_copy(fixture):
    checkpoint, live, expected, proof, _, state, session = fixture
    return remote._release_uploaded_checkpoint_copy(checkpoint, live, expected, proof,
        session, {"Authorization": "Bearer secret"}, "owner/repo", state)


def test_releases_only_uploaded_copy_and_preserves_exact_live_data_and_identity(copied_checkpoint):
    cp, live, expected, proof, _, state, session = copied_checkpoint
    metadata = {name: (cp / name).read_bytes() for name in ("manifest.json", "ready.json", "release.json")}
    originals = {name: (live / name).read_bytes() for name in proof["files"]}
    result = release_copy(copied_checkpoint)
    assert result["status"] == "released_verified_local_payload"
    assert result["logical_bytes_unlinked"] == sum(row["bytes"] for row in proof["files"].values())
    assert result["removed_files"] == len(proof["files"])
    assert session.gets == 1
    assert {p.name for p in cp.iterdir()} == set(metadata)
    assert {name: (cp / name).read_bytes() for name in metadata} == metadata
    assert {name: (live / name).read_bytes() for name in originals} == originals
    audit = json.loads((state / "uploaded-checkpoint-copy-release.json").read_text())
    assert audit["original_actions_artifact"]["digest"] == expected["artifact_digest"]
    assert audit["elapsed_seconds"] >= audit["verification_seconds"] >= 0
    assert "secret" not in json.dumps(audit)


@pytest.mark.parametrize("change", ["run", "head", "digest", "expired", "size", "name"])
def test_rejects_wrong_or_unavailable_original_before_deleting_any_copy(copied_checkpoint, change):
    cp, _, _, proof, artifact, _, _ = copied_checkpoint
    if change == "run": artifact["workflow_run"]["id"] = 78
    elif change == "head": artifact["workflow_run"]["head_sha"] = "d" * 40
    elif change == "digest": artifact["digest"] = "sha256:" + "b" * 64
    elif change == "expired": artifact["expired"] = True
    elif change == "size": artifact["size_in_bytes"] = 0
    else: artifact["name"] = "other-cell"
    with pytest.raises(ValueError, match="uploaded checkpoint identity"):
        release_copy(copied_checkpoint)
    assert all((cp / name).is_file() for name in proof["files"])


def test_validates_all_payload_before_removing_the_first_file(copied_checkpoint):
    cp, _, _, proof, _, _, _ = copied_checkpoint
    (cp / "plans.json").write_bytes(b"changed")
    with pytest.raises(ValueError, match="payload changed"):
        release_copy(copied_checkpoint)
    assert all((cp / name).is_file() for name in proof["files"])


def test_does_not_remove_unlisted_or_outside_files(copied_checkpoint, tmp_path):
    cp, _, _, proof, _, _, _ = copied_checkpoint
    outside = tmp_path / "outside.txt"
    outside.write_text("keep", encoding="utf-8")
    proof["files"]["../../outside.txt"] = {"bytes": 4, "sha256": remote._sha(outside)}
    with pytest.raises(ValueError, match="contents changed"):
        release_copy(copied_checkpoint)
    assert outside.read_text() == "keep"
    assert (cp / "plans.json").exists()


def test_custom_checkpoint_path_is_never_deleted(copied_checkpoint, tmp_path):
    cp, live, expected, proof, _, state, session = copied_checkpoint
    other = tmp_path / "unrelated"
    other.mkdir()
    (other / "keep").write_text("keep")
    result = remote._release_uploaded_checkpoint_copy(other, live, expected, proof, session, {}, "owner/repo", state)
    assert result["payload_removed"] is False and session.gets == 0
    assert (other / "keep").read_text() == "keep"
    assert (cp / "plans.json").exists()


def test_rejects_symlink_escape_without_touching_the_original(copied_checkpoint, tmp_path):
    cp, _, _, _, _, _, _ = copied_checkpoint
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "capture.jsonl").write_bytes(b'{"value":1}\n')
    folder = cp / "observations"
    (folder / "capture.jsonl").unlink()
    folder.rmdir()
    try:
        folder.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks unavailable")
    with pytest.raises(ValueError):
        release_copy(copied_checkpoint)
    assert (outside / "capture.jsonl").read_bytes() == b'{"value":1}\n'
    assert (cp / "plans.json").exists()


def test_parent_releases_verified_copy_before_its_single_worker_dispatch(copied_checkpoint, monkeypatch):
    cp, live, expected, proof, _, state, session = copied_checkpoint
    class Context:
        out, mode, seed = live, "full", 6
    class Campaign:
        ctx, system = Context(), "deathstarbench"
        store = type("Store", (), {"db": object()})()
    posts = []
    def post(*args, **kwargs):
        posts.append(kwargs)
        assert not (cp / "plans.json").exists()
        assert (live / "plans.json").read_bytes() == b"[]\n"
        assert (cp / "manifest.json").is_file()
        raise requests.ConnectionError("ambiguous transport")
    session.post = post
    for key, value in {"GITHUB_ACTIONS": "true", "GH_TOKEN": "secret", "GITHUB_REPOSITORY": "owner/repo"}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(remote, "_expected", lambda *_: (dict(expected), proof))
    monkeypatch.setattr(remote, "_index_table_proof", lambda *_: {"same": True})
    monkeypatch.setattr(remote, "_consistent_live_index_proof", lambda *_: {"same": True})
    monkeypatch.setattr(remote.requests, "Session", lambda: session)
    with pytest.raises(RuntimeError, match="ambiguous"):
        remote.forecast_on_worker(Campaign(), cp, {}, [])
    assert len(posts) == 1
    assert json.loads((state / "dispatch.json").read_text())["status"] == "post_ambiguous_no_retry"
