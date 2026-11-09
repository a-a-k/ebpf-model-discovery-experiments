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


def final_archive_fixture():
    roots = archive.payloads(json.loads((ROOT / archive.MANIFEST).read_bytes()))
    info = {"id": 7, "tag_name": "publication-archive-42", "target_commitish": "a" * 40,
            "body": archive.ARCHIVE_MARKER, "draft": True}
    assets = {f"artifact-{a['id']}.zip": {"id": i + 100, "name": f"artifact-{a['id']}.zip",
              "size": a["bytes"], "digest": "sha256:" + a["sha256"], "state": "uploaded"}
              for i, a in enumerate(roots.values())}
    assets["publication-inputs.zip"] = {"id": 8, "name": "publication-inputs.zip", "size": 5,
                                        "digest": "sha256:" + "b" * 64, "state": "uploaded"}
    bundle = SimpleNamespace(index={"payloads": list(roots.values()), "archive_owner": {
        "release_id": 7, "release_tag": info["tag_name"], "creation_source": info["target_commitish"]}})
    index = {"repository": archive.REPO, "source": archive.SOURCE, "release_id": 7,
             "release_tag": info["tag_name"], "payload_count": 103, "payload_bytes": 12344016466,
             "bundle_asset": assets["publication-inputs.zip"],
             "payload_assets": [assets[f"artifact-{a['id']}.zip"] for a in roots.values()],
             "projection": {"scientific_fields_equal_reference": True, "reference_sha256": archive.REFERENCE_SHA},
             "historical_prefix_is_extra_independent_case": False}
    return roots, info, SimpleNamespace(id=7, assets=assets), bundle, index


def test_index_checks_bundle_membership_and_historical_103rd_asset():
    _, info, release, bundle, index = final_archive_fixture()
    archive.validate_archive_index(index, bundle, release, info)
    original = release.assets["artifact-13617096437.zip"]
    release.assets[original["name"]] = {**original, "digest": "sha256:" + "0" * 64}
    with pytest.raises(ValueError, match="asset ID/bytes/SHA/state differs"):
        archive.validate_archive_index(index, bundle, release, info)
    release.assets[original["name"]] = original
    release.assets["publication-inputs.zip"] = {**index["bundle_asset"], "id": 999}
    with pytest.raises(ValueError, match="asset ID/bytes/SHA/state differs"):
        archive.validate_archive_index(index, bundle, release, info)


def test_resume_requires_dataset_creation_workflow_and_exact_existing_assets():
    roots, info, release, _, _ = final_archive_fixture()
    github = Mock()
    github.json.return_value = {"id": 42, "head_sha": "a" * 40,
                               "path": ".github/workflows/publication-archive.yml", "event": "workflow_dispatch"}
    archive.validate_release_owner(github, info, release, roots)
    with pytest.raises(ValueError, match="not the intended"):
        archive.validate_release_owner(github, {**info, "body": "unrelated draft"}, release, roots)
    github.json.return_value["head_sha"] = "c" * 40
    with pytest.raises(ValueError, match="creation workflow/source differs"):
        archive.validate_release_owner(github, info, release, roots)
    github.json.return_value["head_sha"] = "a" * 40
    release.assets["unrelated.zip"] = {"id": 99}
    with pytest.raises(ValueError, match="unexpected assets"):
        archive.validate_release_owner(github, info, release, roots)


def test_upload_success_on_last_retry_is_verified_without_another_post(tmp_path, monkeypatch):
    import requests
    path = tmp_path / "small.zip"
    path.write_bytes(b"original")
    asset = {"id": 2, "name": path.name, "size": 8,
             "digest": "sha256:" + archive.digest(b"original"), "state": "uploaded"}
    github = Mock()
    github.pages.return_value = []
    github.json.return_value = asset
    response = Mock()
    response.json.return_value = asset
    github.request.side_effect = [requests.ConnectionError("ambiguous upload")] * 3 + [response]
    monkeypatch.setattr(archive.time, "sleep", lambda _: None)
    assert archive.Release(github, 1).publish(path) == asset
    assert github.request.call_count == 4
    github.json.assert_called_once_with("releases/assets/2")


def test_resume_after_final_index_reuses_immutable_index_without_reprojection(tmp_path, monkeypatch):
    roots, info, release, bundle, index = final_archive_fixture()
    index_body = json.dumps(index).encode()
    release.assets["archive-index.json"] = {"id": 9, "name": "archive-index.json", "size": len(index_body),
        "digest": "sha256:" + archive.digest(index_body), "state": "uploaded", "browser_download_url": "https://example.test/index"}
    github = Mock(calls=[])
    def api(path):
        if path == "actions/runs/42":
            return {"id": 42, "head_sha": "a" * 40, "path": ".github/workflows/publication-archive.yml", "event": "workflow_dispatch"}
        return info
    github.json.side_effect = api
    published = Mock()
    published.json.return_value = {**info, "draft": False}
    github.request.return_value = published
    def download(endpoint, path, size, sha):
        path.write_bytes(index_body if endpoint == "releases/assets/9" else b"input")
    github.download.side_effect = download
    release.publish = Mock(return_value=release.assets["publication-inputs.zip"])
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REPOSITORY", archive.REPO)
    monkeypatch.setenv("GITHUB_SHA", "d" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "43")
    monkeypatch.setattr("sys.argv", ["archive", "create", "--release-id", "7"])
    monkeypatch.setattr(archive, "GitHub", lambda **_: github)
    monkeypatch.setattr(archive, "Release", lambda *_: release)
    monkeypatch.setattr(archive, "Bundle", lambda _: bundle)
    monkeypatch.setattr(archive, "git_blob", lambda _: (ROOT / archive.MANIFEST).read_bytes())
    monkeypatch.setattr(archive, "project", Mock(side_effect=AssertionError("must not repeat projection")))
    archive.main()
    proof = json.loads((tmp_path / "work/publication-archive/proof.json").read_text())
    assert proof["status"] == "complete"
    assert proof["resumed_existing_immutable_index"] is True
    assert proof["fresh_scientific_projection_performed"] is False
    assert proof["archive_index"]["sha256"] == archive.digest(index_body)
    release.publish.assert_called_once()  # Original bundle only; no regenerated index upload.
