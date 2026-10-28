import io
import hashlib
import json
import os
from pathlib import Path
import zipfile

import pytest
import requests

from ebpf_discovery import remote_toolchain_v4 as remote


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def checkpoint(root, identity):
    root.mkdir(parents=True)
    payload = root / "plans.json"
    write_json(payload, [{"attempt_id": "a", "phase": "class_train", "state": "11",
                          "http_steps": []}])
    files = {"plans.json": {"relative_path": "plans.json", "bytes": payload.stat().st_size,
                             "sha256": remote._sha(payload)}}
    manifest = {"schema_version": "v4-training-prefix-checkpoint",
                "status": "partial_training_capture_only; no forecast or completed cell",
                "identity": identity, "files": files}
    write_json(root / "manifest.json", manifest)
    write_json(root / "ready.json", {**identity, "status": "training_checkpoint_ready",
                                      "manifest_sha256": remote._sha(root / "manifest.json")})
    return manifest


def identity():
    return {"run_id": "77", "commit": "c" * 40, "system": "otel_demo",
            "mode": "full", "seed": 6}


def test_checkpoint_validation_allows_only_parent_release(tmp_path):
    root = tmp_path / "checkpoint"
    checkpoint(root, identity())
    expected = {**identity(), "manifest_sha256": remote._sha(root / "manifest.json")}
    manifest, proof = remote._validate_checkpoint(root, expected)
    assert proof["files"]["plans.json"]["sha256"] == manifest["files"]["plans.json"]["sha256"]
    write_json(root / "release.json", {"upload_success": True})
    remote._validate_checkpoint(root, expected)
    (root / "unlisted.txt").write_text("not admitted", encoding="utf-8")
    with pytest.raises(ValueError, match="unmanifested"):
        remote._validate_checkpoint(root, expected)


def test_safe_extract_rejects_traversal_and_symlink(tmp_path):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../escape", b"bad")
    with pytest.raises(ValueError, match="unsafe"):
        remote._safe_extract(archive, tmp_path / "out")
    archive2 = tmp_path / "link.zip"
    info = zipfile.ZipInfo("link")
    info.external_attr = (0o120777 << 16)
    with zipfile.ZipFile(archive2, "w") as bundle:
        bundle.writestr(info, "target")
    with pytest.raises(ValueError, match="unsafe"):
        remote._safe_extract(archive2, tmp_path / "out2")


def worker_bundle(root, expected, worker_run_id=91):
    toolchain = root / "toolchain"
    write_json(toolchain / "forecasts.json", {"ebpf": {"raw": {"browse": {"available": False}}}})
    write_json(toolchain / "unknown.txt", {"reason": "retained"})
    files = remote._manifest(toolchain)
    common = {"schema_version": "remote-toolchain-output-v4",
              "identity": {key: expected[key] for key in remote.IDENTITY_KEYS},
              "parent_run_attempt": expected["parent_run_attempt"],
              "parent_cell_id": expected["parent_cell_id"], "worker_run_id": str(worker_run_id),
              "request_id": expected["request_id"],
              "worker_run_attempt": expected["worker_run_attempt"],
              "workflow_sha": expected["worker_workflow_sha"],
              "plans_sha256": expected["plans_sha256"],
              "training_index_proof_sha256": expected["training_index_proof_sha256"],
              "toolchain_files": files}
    write_json(root / "output-manifest.json", common)
    write_json(root / "worker-provenance.json", {
        "identity": common["identity"], "worker_run_id": str(worker_run_id),
        "worker_run_attempt": expected["worker_run_attempt"], "request_id": expected["request_id"],
        "implementation_sha": expected["commit"], "workflow_sha": expected["worker_workflow_sha"],
        "plans_sha256": expected["plans_sha256"], "training_index_proof": {"spans": "same"},
        "checkpoint_artifact": {key: expected.get(key) for key in
                                ("artifact_id", "artifact_name", "artifact_digest")},
        "toolchain_files": files})
    write_json(root / "worker-status.json", {"status": "complete"})


def test_worker_output_requires_exact_complete_file_census_and_workflow_sha(tmp_path):
    expected = {**identity(), "manifest_sha256": "m" * 64, "parent_run_attempt": "2",
                "parent_cell_id": "otel_demo:full:6", "plans_sha256": "p" * 64,
                "worker_workflow_sha": "w" * 40, "worker_run_attempt": "1",
                "request_id": "request-1", "artifact_id": "42", "artifact_name": "training",
                "artifact_digest": "sha256:" + "a" * 64,
                "training_index_proof_sha256": remote._json_sha({"spans": "same"})}
    worker_bundle(tmp_path, expected)
    forecasts = remote._verify_worker_output(tmp_path, expected, 91)
    assert forecasts["ebpf"]["raw"]["browse"]["available"] is False
    (tmp_path / "toolchain" / "extra").write_text("unlisted", encoding="utf-8")
    with pytest.raises(ValueError, match="unlisted"):
        remote._verify_worker_output(tmp_path, expected, 91)


class FakeResponse:
    def __init__(self, status=200, value=None, content=b""):
        self.status_code, self.value, self.content = status, value or {}, content
        self.text = json.dumps(self.value)

    def json(self):
        return self.value

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))

    def iter_content(self, _size):
        yield self.content


class AmbiguousSession:
    posts = 0

    def post(self, *_args, **_kwargs):
        self.posts += 1
        raise requests.Timeout("unknown whether server accepted request")


def test_dispatch_transport_ambiguity_is_persisted_without_retry(tmp_path, monkeypatch):
    class Ctx:
        out = tmp_path / "campaign"
        mode = "full"
        seed = 6

    class Campaign:
        ctx = Ctx()
        system = "otel_demo"
        store = type("Store", (), {"db": object()})()

    Ctx.out.mkdir()
    cp = tmp_path / "checkpoint"
    checkpoint(cp, identity())
    plans = json.loads((cp / "plans.json").read_text())
    release = {**identity(), "manifest_sha256": remote._sha(cp / "manifest.json"),
               "upload_success": True, "artifact_id": "42", "artifact_url": "url",
               "artifact_digest": "sha256:" + "a" * 64}
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GH_TOKEN", "secret")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "3")
    monkeypatch.setattr(remote, "_verify_binaries", lambda *_: {})
    monkeypatch.setattr(remote, "_index_table_proof", lambda *_: {"spans": "same"})
    monkeypatch.setattr(remote, "_consistent_live_index_proof", lambda *_: {"spans": "same"})
    session = AmbiguousSession()
    monkeypatch.setattr(remote.requests, "Session", lambda: session)
    with pytest.raises(RuntimeError, match="ambiguous"):
        remote.forecast_on_worker(Campaign(), cp, release, plans)
    assert session.posts == 1
    saved = json.loads((Ctx.out / "infrastructure/remote-toolchain-v4/dispatch.json").read_text())
    assert saved["status"] == "post_ambiguous_no_retry"
    assert "secret" not in json.dumps(saved)


def test_download_hashes_exact_archive_bytes(tmp_path):
    payload = b"PK\x03\x04not-a-real-zip-but-exact-wire"
    class Session:
        def get(self, *_args, **_kwargs):
            return FakeResponse(content=payload)
    path = tmp_path / "artifact.zip"
    assert remote._download(Session(), "url", {}, path) == __import__("hashlib").sha256(payload).hexdigest()
    assert path.read_bytes() == payload


def test_successful_worker_return_is_verified_and_atomically_imported(tmp_path, monkeypatch):
    class Ctx:
        out = tmp_path / "campaign"
        mode = "full"
        seed = 6
    class Campaign:
        ctx = Ctx()
        system = "otel_demo"
        store = type("Store", (), {"db": object()})()
    Ctx.out.mkdir()
    expected = {**identity(), "manifest_sha256": "m" * 64,
                "parent_run_attempt": "2", "parent_cell_id": "otel_demo:full:6",
                "plans_sha256": "p" * 64, "artifact_id": "42",
                "artifact_name": "training", "artifact_digest": "sha256:" + "a" * 64,
                "training_index_proof_sha256": remote._json_sha({"spans": "same"}),
                "worker_workflow_sha": "w" * 40, "worker_run_attempt": "1",
                "request_id": "00000000-0000-0000-0000-000000000001"}
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    worker_bundle(bundle, expected)
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w") as archive:
        for path in sorted(bundle.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle).as_posix())
    wire = memory.getvalue()
    digest = hashlib.sha256(wire).hexdigest()

    class Session:
        def post(self, *_args, **_kwargs):
            return FakeResponse(value={"workflow_run_id": 91, "run_url": "api/run/91",
                                       "html_url": "html/run/91"})
        def get(self, url, **_kwargs):
            if url.endswith("/actions/runs/91"):
                return FakeResponse(value={"id": 91, "event": "workflow_dispatch",
                    "path": ".github/workflows/toolchain-worker-v4.yml", "status": "completed",
                    "conclusion": "success", "head_sha": "w" * 40, "run_attempt": 1,
                    "repository": {"full_name": "owner/repo"}})
            if "artifacts?" in url:
                return FakeResponse(value={"artifacts": [{"id": 100, "expired": False,
                    "name": "toolchain-v4-otel_demo-full-6-91", "digest": "sha256:" + digest,
                    "archive_download_url": "download", "workflow_run": {"id": 91,
                    "head_sha": "w" * 40}}]})
            if url == "download":
                return FakeResponse(content=wire)
            raise AssertionError(url)

    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GH_TOKEN", "secret")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(remote.uuid, "uuid4", lambda: expected["request_id"])
    base_expected = {key: value for key, value in expected.items()
                     if key not in ("request_id", "worker_workflow_sha", "worker_run_attempt")}
    monkeypatch.setattr(remote, "_expected", lambda *_: (dict(base_expected), {"files": {}}))
    monkeypatch.setattr(remote, "_index_table_proof", lambda *_: {"spans": "same"})
    monkeypatch.setattr(remote, "_consistent_live_index_proof", lambda *_: {"spans": "same"})
    monkeypatch.setattr(remote.requests, "Session", Session)
    forecasts = remote.forecast_on_worker(Campaign(), tmp_path / "checkpoint", {}, [])
    assert forecasts["ebpf"]["raw"]["browse"]["available"] is False
    assert (Ctx.out / "toolchain/forecasts.json").is_file()
    evidence = Ctx.out / "infrastructure/remote-toolchain-v4"
    assert (evidence / "worker/output-manifest.json").is_file()
    assert not (evidence / "worker-output.zip").exists()
    cost = json.loads((evidence / "cost.json").read_text())
    assert cost["worker_run_id"] == 91 and cost["worker_run_attempt"] == 1


def test_release_identity_failure_happens_before_dispatch(tmp_path, monkeypatch):
    class Ctx:
        out = tmp_path / "campaign"
        mode = "full"
        seed = 6
    class Campaign:
        ctx = Ctx()
        system = "otel_demo"
    Ctx.out.mkdir()
    cp = tmp_path / "checkpoint"
    checkpoint(cp, identity())
    release = {**identity(), "commit": "d" * 40, "manifest_sha256": remote._sha(cp / "manifest.json"),
               "upload_success": True, "artifact_id": "42", "artifact_url": "url",
               "artifact_digest": "sha256:" + "a" * 64}
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GH_TOKEN", "secret")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    class NeverSession:
        def __init__(self):
            raise AssertionError("dispatch session must not be created")
    monkeypatch.setattr(remote.requests, "Session", NeverSession)
    with pytest.raises(ValueError, match="release and checkpoint"):
        remote.forecast_on_worker(Campaign(), cp, release, [])
