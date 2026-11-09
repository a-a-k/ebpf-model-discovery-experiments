"""Small synthetic I/O checks; the actual report replay runs only in Actions."""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import zipfile

import pytest

from ebpf_discovery import publication_archive as archive


ROOT = Path(__file__).resolve().parents[1]


def test_original_reader_body_is_unchanged_except_three_io_definitions():
    body = (ROOT / archive.READER).read_bytes()
    original = archive.reader_tree(body)
    expected = [n for n in original.body if not
                (isinstance(n, ast.FunctionDef) and n.name in {"api", "blob", "download"})]
    bound = archive.bound_reader(body)
    assert bound.co_filename == "archived-c4-publication-reader"
    assert {n.name for n in original.body if isinstance(n, ast.FunctionDef)} - {
        n.name for n in expected if isinstance(n, ast.FunctionDef)} == {"api", "blob", "download"}
    # Capture the AST actually passed to compile, then compare every remaining node.
    import builtins
    from unittest.mock import patch
    with patch.object(archive, "compile", wraps=builtins.compile, create=True) as compiler:
        archive.bound_reader(body)
    assert ast.dump(compiler.call_args.args[0]) == ast.dump(ast.Module(body=expected, type_ignores=[]))
    with pytest.raises(ValueError, match="unqualified reader"):
        archive.bound_reader(body + b"\n")


def test_fixed_allowlist_includes_historical_prefix_without_extra_case():
    manifest = json.loads((ROOT / archive.MANIFEST).read_bytes())
    roots = archive.payloads(manifest)
    assert len(manifest["cells"]) == 108
    assert len(roots) == 103
    assert roots[13617096437]["bytes"] == 241176860
    assert sum(a["bytes"] for a in roots.values()) == 12344016466
    assert max(a["bytes"] for a in roots.values()) < 2 * 1024**3


def test_replay_forbids_live_actions_network_even_if_called_directly():
    github = archive.GitHub(replay=True)
    for path in ("actions/artifacts/123/zip", "actions/jobs/123", "https://api.github.com/repos/" + archive.REPO + "/actions/runs/123"):
        with pytest.raises(ValueError, match="live Actions API forbidden"):
            github.request("GET", path)
    bundle = object.__new__(archive.Bundle)
    bundle.receipts = {"endpoint_views": {"actions/jobs/123": {"id": 123}}}
    assert bundle.api("actions/jobs/123") == {"id": 123}
    with pytest.raises(ValueError, match="missing archived API receipt"):
        bundle.api("actions/jobs/456")


def test_replay_uses_release_exact_bytes_and_rejects_unlisted_payload(tmp_path):
    body = b"synthetic original ZIP bytes"
    a = {"id": 123, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}
    bundle = SimpleNamespace(index={"payloads": [a]})
    release = SimpleNamespace(assets={"artifact-123.zip": {
        "id": 789, "size": len(body), "digest": "sha256:" + a["sha256"], "state": "uploaded"}})
    github = Mock()
    backend = archive.Backend(bundle, github, release, create=False)
    backend.download(a, tmp_path / "one.zip")
    github.download.assert_called_once_with("releases/assets/789", tmp_path / "one.zip", a["bytes"], a["sha256"])
    with pytest.raises(ValueError, match="outside exact"):
        backend.download({**a, "id": 456}, tmp_path / "two.zip")
    release.assets["artifact-123.zip"]["digest"] = "sha256:wrong"
    with pytest.raises(ValueError, match="identity differs"):
        backend.download(a, tmp_path / "one.zip")


def test_stream_download_rejects_corruption_and_cleans_only_owned_partial(tmp_path, monkeypatch):
    github = archive.GitHub(replay=True)
    response = Mock(is_redirect=False)
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.iter_content.return_value = [b"wrong"]
    monkeypatch.setattr(github, "request", Mock(return_value=response))
    monkeypatch.setattr(archive.shutil, "disk_usage", lambda _: SimpleNamespace(free=archive.RESERVE + 100))
    with pytest.raises(ValueError, match="byte count/SHA differs"):
        github.download("releases/assets/1", tmp_path / "original.zip", 5, hashlib.sha256(b"right").hexdigest())
    assert not (tmp_path / "original.zip").exists()
    assert not (tmp_path / "original.zip.partial").exists()


def test_existing_upload_is_reused_only_after_exact_remote_verification(tmp_path):
    body = b"original"
    path = tmp_path / "artifact-1.zip"
    path.write_bytes(body)
    asset = {"id": 2, "name": path.name, "size": len(body), "digest": "sha256:" + archive.digest(body), "state": "uploaded"}
    github = Mock()
    github.pages.return_value = [asset]
    github.json.return_value = asset
    release = archive.Release(github, 1)
    assert release.publish(path) == asset
    github.request.assert_not_called()
    github.json.return_value = {**asset, "size": len(body) + 1}
    with pytest.raises(ValueError, match="conflicting/incomplete"):
        release.publish(path)


def test_bundle_rejects_tampered_member_before_any_api_or_scientific_work(tmp_path):
    path = tmp_path / "inputs.zip"
    with zipfile.ZipFile(path, "w") as output:
        output.writestr("source/test", b"tampered")
        output.writestr("bundle-index.json", json.dumps({"files": {"source/test": {
            "bytes": 8, "sha256": archive.digest(b"original")}}}))
    with pytest.raises(ValueError, match="source receipt differs"):
        archive.Bundle(path)
