import io
import hashlib
import json
import os
from pathlib import Path
import zipfile

import pytest
import requests
import sqlite3
import yaml

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery import artifact_transport_v4 as transport
from ebpf_discovery.toolchain_v5 import PINS as V5_PINS


def test_index_logical_proof_binds_runtime_identity_projection_rows(tmp_path):
    index = tmp_path / "index.sqlite"
    with sqlite3.connect(index) as db:
        for table in ("spans", "links", "files"):
            db.execute(f"CREATE TABLE {table}(value TEXT)")
        db.execute("CREATE TABLE runtime_identity_projection(digest TEXT, resolution TEXT)")
        db.execute("INSERT INTO runtime_identity_projection VALUES (?,?)",
                   ("digest", '{"status":"resolved"}'))
    before = remote._index_table_proof(index)
    assert before["runtime_identity_projection"]["rows"] == 1
    with sqlite3.connect(index) as db:
        db.execute("UPDATE runtime_identity_projection SET resolution=?",
                   ('{"status":"unknown"}',))
    after = remote._index_table_proof(index)
    assert before["spans"] == after["spans"]
    assert before["runtime_identity_projection"] != after["runtime_identity_projection"]
    assert remote._json_sha(before) != remote._json_sha(after)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def test_graph_v5_checkpoint_selects_v5_toolchain_from_bound_collector(tmp_path):
    from ebpf_discovery.toolchain_v5 import Toolchain as V5Toolchain
    write_json(tmp_path/'status.json', {'protocol_version': 'graph-v5', 'collector': 'coroot'})
    write_json(tmp_path/'observations'/'collector.json', {
        'schema': 'collector-lifecycle-v5', 'collector': 'coroot',
        'source_domain': 'ebpf-coroot'})
    provenance = {
        'protocol_version': 'graph-v5', 'collector': 'coroot',
        'source_domain': 'ebpf-coroot', 'collector_schema': 'collector-lifecycle-v5',
        'collector_file': 'observations/collector.json'}
    pins, toolchain, selected = remote._checkpoint_toolchain(
        tmp_path, {'collector_provenance': provenance})
    assert pins == V5_PINS
    assert toolchain is V5Toolchain
    assert selected == provenance


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


@pytest.mark.parametrize('change', [None, 'legacy', 'conflict', 'path', 'hash', 'count',
                                  'count_bool', 'encoding', 'unlisted', 'truncated', 'not_object'])
def test_runtime_dependency_file_is_bound_and_legacy_array_remains_readable(tmp_path, change):
    root = tmp_path/'checkpoint'
    manifest = checkpoint(root, identity())
    relative = 'runtime-observation-dependencies.jsonl'
    payload = root/relative
    payload.write_text('{"locator":{"text":"a\\nb"}}\n{"locator":{}}\n', encoding='utf-8')
    if change == 'truncated':
        payload.write_bytes(payload.read_bytes().rstrip(b'\n'))
    if change == 'not_object':
        payload.write_text('[]\n{}\n', encoding='utf-8')
    proof = {'relative_path': relative, 'bytes': payload.stat().st_size, 'sha256': remote._sha(payload)}
    manifest['files'][relative] = proof
    reference = {**proof, 'records': 2, 'encoding': 'utf-8-jsonl'}
    manifest['runtime_observation_dependencies_jsonl'] = reference
    if change == 'legacy':
        manifest.pop('runtime_observation_dependencies_jsonl')
        manifest['runtime_observation_dependencies'] = [{'legacy': 'preserved'}]
    elif change == 'conflict':
        manifest['runtime_observation_dependencies'] = []
    elif change == 'path':
        reference['relative_path'] = '../' + relative
    elif change == 'hash':
        reference['sha256'] = '0' * 64
    elif change == 'count':
        reference['records'] = 3
    elif change == 'count_bool':
        reference['records'] = True
    elif change == 'encoding':
        reference['encoding'] = 'json'
    elif change == 'unlisted':
        manifest['files'].pop(relative)
    write_json(root/'manifest.json', manifest)
    expected = {**identity(), 'manifest_sha256': remote._sha(root/'manifest.json')}
    write_json(root/'ready.json', {**expected, 'status': 'training_checkpoint_ready'})
    if change in (None, 'legacy'):
        actual, _ = remote._validate_checkpoint(root, expected)
        assert actual == manifest
    else:
        with pytest.raises(ValueError):
            remote._validate_checkpoint(root, expected)


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
    if "collector_provenance" in expected:
        common["collector_provenance"] = expected["collector_provenance"]
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
    def __init__(self, status=200, value=None, content=b"", headers=None):
        self.status_code, self.value, self.content = status, value or {}, content
        self.text = json.dumps(self.value)
        self.headers = requests.structures.CaseInsensitiveDict(headers or {})
        self.closed = False

    def close(self):
        self.closed = True

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
    monkeypatch.setenv("GITHUB_RUN_ID", identity()["run_id"])
    monkeypatch.setenv("GITHUB_SHA", identity()["commit"])
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "3")
    monkeypatch.setattr(remote, "_verify_binaries", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(remote, "_index_table_proof", lambda *_: {"spans": "same"})
    monkeypatch.setattr(remote, "_consistent_live_index_proof", lambda *_, **__: {"spans": "same"})
    monkeypatch.setattr(remote, "_checkpoint_index_reference", lambda *_: {"logical_proof": {"spans": "same"}})
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


@pytest.mark.parametrize("status,headers,value,wait", [
    (403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1180"}, {}, 181),
    (429, {"Retry-After": "1800"}, {}, 1800),
    (403, {}, {"message": "You have exceeded a secondary rate limit."}, 60),
    (403, {"Retry-After": "90", "X-RateLimit-Remaining": "50"}, {}, 90),
    (429, {"Retry-After": "NaN", "X-RateLimit-Reset": "Infinity"}, {}, 60),
])
def test_get_honors_rate_limit_before_retry(status, headers, value, wait, monkeypatch):
    limited = FakeResponse(status=status, headers=headers, value=value)
    success = FakeResponse(value={"status": "completed"})
    replies = iter([limited, success])
    sleeps = []
    class Session:
        def get(self, *_args, **_kwargs):
            return next(replies)
    def sleep(seconds):
        assert limited.closed
        sleeps.append(seconds)
    monkeypatch.setattr(remote.time, "time", lambda: 1000)
    monkeypatch.setattr(remote.time, "sleep", sleep)
    assert remote._get(Session(), "url", {}) is success
    assert sleeps == [wait]


def test_secondary_retries_back_off_and_log_only_sanitized_metadata(tmp_path, monkeypatch):
    limited = [FakeResponse(status=403, value={"message": "Secondary rate limit; secret-body"})
               for _ in range(6)]
    success = FakeResponse()
    replies = iter([*limited, success])
    sleeps = []
    class Session:
        def get(self, *_args, **_kwargs):
            return next(replies)
    monkeypatch.setattr(remote.time, "sleep", sleeps.append)
    log = tmp_path / "http-retries.jsonl"
    assert remote._get(Session(), "https://api/secret-query", {"Authorization": "secret-token"},
                       retry_log=log, operation="worker_status") is success
    assert sleeps == [60, 120, 240, 480, 900, 900]
    assert all(r.closed for r in limited)
    text = log.read_text()
    assert "secret" not in text and "https://" not in text
    rows = [json.loads(line) for line in text.splitlines()]
    assert [r["event"] for r in rows] == ["wait_started", "wait_ended"] * 6
    assert [r["requested_wait_seconds"] for r in rows[::2]] == sleeps
    assert all(r["reason"] == "rate_limit" for r in rows)


@pytest.mark.parametrize("status", [401, 403, 404])
def test_get_does_not_retry_permission_or_identity_failures(status, monkeypatch):
    response = FakeResponse(status=status, value={"message": "Resource not accessible"})
    class Session:
        calls = 0
        def get(self, *_args, **_kwargs):
            self.calls += 1
            return response
    def unexpected_sleep(_seconds):
        pytest.fail("hard failure must not be delayed")
    monkeypatch.setattr(remote.time, "sleep", unexpected_sleep)
    session = Session()
    with pytest.raises(requests.HTTPError):
        remote._get(session, "url", {})
    assert session.calls == 1 and response.closed


def test_artifact_get_retries_headers_but_never_partial_body(tmp_path, monkeypatch):
    limited = FakeResponse(status=429, headers={"Retry-After": "61"})
    payload = b"exact archive bytes"
    response = FakeResponse(content=payload)
    replies = iter([limited, response])
    class Session:
        calls = 0
        def get(self, *_args, **kwargs):
            assert kwargs["stream"] is True
            self.calls += 1
            return next(replies)
    sleeps = []
    monkeypatch.setattr(remote.time, "sleep", sleeps.append)
    session = Session()
    path = tmp_path / "artifact.zip"
    assert remote._download(session, "url", {}, path) == hashlib.sha256(payload).hexdigest()
    assert session.calls == 2 and sleeps == [61]
    assert path.read_bytes() == payload and limited.closed and response.closed

    def broken_body(_size):
        yield b"partial"
        raise requests.ConnectionError("body interrupted")
    broken = FakeResponse()
    broken.iter_content = broken_body
    replies = iter([broken])
    session = Session()
    failed = tmp_path / "failed.zip"
    with pytest.raises(requests.ConnectionError, match="body interrupted"):
        remote._download(session, "url", {}, failed)
    assert session.calls == 1 and broken.closed and not failed.exists()
    assert (tmp_path / ".failed.zip.tmp").read_bytes() == b"partial"




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


def test_actual_upload_artifact_bare_digest_is_canonicalized(tmp_path, monkeypatch):
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
    plans = json.loads((cp / "plans.json").read_text())
    bare = "38149e16" + "a" * 56
    release = {**identity(), "manifest_sha256": remote._sha(cp / "manifest.json"),
               "upload_success": True, "artifact_id": "12830934533",
               "artifact_url": "https://github.example/artifact/12830934533",
               "artifact_digest": bare}
    monkeypatch.setenv("GITHUB_RUN_ID", identity()["run_id"])
    monkeypatch.setenv("GITHUB_SHA", identity()["commit"])
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "4")
    monkeypatch.setattr(remote, "_verify_binaries", lambda *_args, **_kwargs: {})
    expected, _ = remote._expected(Campaign(), cp, release, plans)
    assert expected["artifact_digest"] == "sha256:" + bare


@pytest.mark.skipif(os.name == "nt", reason="Linux executable-mode regression")
def test_zip_restored_verified_binary_is_made_executable(tmp_path):
    binary = tmp_path / "tool"
    binary.write_text("#!/bin/sh\nprintf executable-mode-ok", encoding="utf-8")
    binary.chmod(0o644)
    proof = {"tool": {"path": str(binary), "sha256": remote._sha(binary)}}
    remote._make_binaries_executable(proof)
    result = __import__("subprocess").run([str(binary)], check=True, text=True, capture_output=True)
    assert result.stdout == "executable-mode-ok"


@pytest.mark.parametrize('immutable_prefix', [False, True])
def test_readonly_store_preserves_observation_store_connection_pragmas(tmp_path, immutable_prefix):
    path = tmp_path / "index.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE spans(value TEXT)")
    store = remote._readonly_store(path, immutable_prefix=immutable_prefix)
    try:
        assert store._immutable_path_prefix is immutable_prefix
        assert store.db.execute("PRAGMA query_only").fetchone()[0] == 1
        assert store.db.execute("PRAGMA cache_size").fetchone()[0] == -65536
        assert store.db.execute("PRAGMA temp_store").fetchone()[0] == 1
    finally:
        store.close()




