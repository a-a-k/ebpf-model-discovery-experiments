"""Delivery lifetime, actual phase guards and original/processing identity checks."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import zipfile

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/restore-closed-postcapture-v5.py"
SPEC = importlib.util.spec_from_file_location("closed_restore", SCRIPT)
RESTORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RESTORE)


def fixture_capture(tmp_path, monkeypatch, *, recovery=True):
    monkeypatch.chdir(tmp_path)
    original_run, original_source = "123", "a" * 40
    processing_run, processing_source = ("456", "b" * 40) if recovery else (original_run, original_source)
    payload = b"unchanged scientific input\n"
    marker = {"file_bytes": len(payload), "index_bytes": 4096,
              "identity": {"run_id": original_run, "commit": original_source, "mode": "full", "seed": 8}}
    marker_bytes = json.dumps(marker).encode()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as bundle:
        bundle.writestr("campaign/input.bin", payload)
        bundle.writestr("postcapture-proof/closed.json", marker_bytes)
    archive = stream.getvalue()
    digest = hashlib.sha256(archive).hexdigest()
    metadata = {"id": 777, "expired": False, "digest": "sha256:" + digest,
                "size_in_bytes": len(archive), "archive_download_url": "https://example.invalid/original",
                "workflow_run": {"id": int(original_run), "head_sha": original_source}}
    env = {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": processing_run, "GITHUB_SHA": processing_source,
           "GITHUB_REPOSITORY": "owner/repo", "GH_TOKEN": "test-only",
           "CAPTURE_ARTIFACT_ID": "777", "CAPTURE_ARTIFACT_DIGEST": digest,
           "CAPTURE_FILE_BYTES": str(len(payload)), "CAPTURE_PROOF_BYTES": str(len(marker_bytes)),
           "CAPTURE_INDEX_BYTES": "4096", "CAPTURE_MANIFEST_SHA256": hashlib.sha256(marker_bytes).hexdigest(),
           "CAPTURE_MODE": "full", "CAPTURE_SEED": "8"}
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(RESTORE.transport, "_get", lambda *a, **kw: SimpleNamespace(json=lambda: metadata))
    downloads = []

    def download(session, url, headers, target, **kwargs):
        downloads.append(url)
        target.write_bytes(archive)
        return digest

    monkeypatch.setattr(RESTORE.transport, "_download", download)
    reserve = 4 * marker["index_bytes"]
    fixed = len(payload) + len(marker_bytes)
    staged = max(len(archive) + fixed, fixed + reserve) + 1024**3
    legacy = len(archive) + fixed + reserve + 1024**3
    monkeypatch.setattr(RESTORE.shutil, "disk_usage", lambda path: SimpleNamespace(free=staged + 1))
    return SimpleNamespace(payload=payload, marker=marker_bytes, metadata=metadata,
                           downloads=downloads, staged=staged, legacy=legacy,
                           kwargs={"capture_run_id": original_run, "capture_source": original_source})


def read(tmp_path, name):
    return json.loads((tmp_path / "work/offline-host" / name).read_text())


def test_verified_delivery_lifetime_fits_without_reducing_SQL_reserve(tmp_path, monkeypatch):
    capture = fixture_capture(tmp_path, monkeypatch)
    assert capture.staged + 1 < capture.legacy
    result = RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert result["status"] == "complete"
    assert (tmp_path / "work/campaign/input.bin").read_bytes() == capture.payload
    assert (tmp_path / "work/restored-postcapture/postcapture-proof/closed.json").read_bytes() == capture.marker
    assert not (tmp_path / "work/closed-postcapture.zip").exists()
    assert result["delivery_working_copy"]["removed_after_all_restore_checks"] is True
    assert result["all_original_members_read_to_EOF_and_CRC_checked"] is True
    assert (result["capture_run_id"], result["processing_run_id"]) == ("123", "456")
    assert (result["capture_source"], result["processing_source"]) == ("a" * 40, "b" * 40)
    before = read(tmp_path, "disk-before-download.json")
    after = read(tmp_path, "disk-before-processing.json")
    assert before["required_bytes"] == capture.staged
    assert before["SQL_WAL_growth_reserve_bytes"] == after["SQL_WAL_growth_reserve_bytes"] == 4 * 4096
    assert after["required_bytes"] == 4 * 4096 + 1024**3


def test_default_retains_original_budget_and_delivery(tmp_path, monkeypatch):
    capture = fixture_capture(tmp_path, monkeypatch, recovery=False)
    monkeypatch.setattr(RESTORE.shutil, "disk_usage", lambda path: SimpleNamespace(free=capture.legacy + 1))
    result = RESTORE.restore()
    assert result["status"] == "complete"
    assert (tmp_path / "work/closed-postcapture.zip").is_file()
    assert "delivery_working_copy" not in result
    assert read(tmp_path, "disk-before-download.json")["required_bytes"] == capture.legacy
    assert not (tmp_path / "work/offline-host/disk-before-processing.json").exists()


def test_insufficient_initial_space_stops_before_download(tmp_path, monkeypatch):
    capture = fixture_capture(tmp_path, monkeypatch)
    monkeypatch.setattr(RESTORE.shutil, "disk_usage", lambda path: SimpleNamespace(free=capture.staged - 1))
    with pytest.raises(AssertionError, match="insufficient actual disk"):
        RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert capture.downloads == []
    assert read(tmp_path, "restore.json")["status"] == "failed"


@pytest.mark.parametrize("field,value", [("id", 778), ("digest", "sha256:" + "0" * 64),
                                         ("expired", True)])
def test_wrong_artifact_stops_before_download(tmp_path, monkeypatch, field, value):
    capture = fixture_capture(tmp_path, monkeypatch)
    capture.metadata[field] = value
    with pytest.raises(AssertionError):
        RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert capture.downloads == []


@pytest.mark.parametrize("field,value", [("id", 456), ("head_sha", "b" * 40)])
def test_original_capture_is_not_confused_with_processing_identity(tmp_path, monkeypatch, field, value):
    capture = fixture_capture(tmp_path, monkeypatch)
    capture.metadata["workflow_run"][field] = value
    with pytest.raises(AssertionError):
        RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert capture.downloads == []


def test_bad_marker_never_releases_delivery(tmp_path, monkeypatch):
    capture = fixture_capture(tmp_path, monkeypatch)
    monkeypatch.setenv("CAPTURE_MANIFEST_SHA256", "0" * 64)
    with pytest.raises(AssertionError):
        RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert (tmp_path / "work/closed-postcapture.zip").is_file()
    assert "delivery_working_copy" not in read(tmp_path, "restore.json")
    assert (tmp_path / "work/campaign/input.bin").read_bytes() == capture.payload


def test_actual_post_restore_guard_catches_space_change(tmp_path, monkeypatch):
    capture = fixture_capture(tmp_path, monkeypatch)
    free = iter([capture.staged + 1, capture.staged + 1, 0])
    monkeypatch.setattr(RESTORE.shutil, "disk_usage", lambda path: SimpleNamespace(free=next(free)))
    with pytest.raises(AssertionError, match="SQL/WAL headroom"):
        RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert read(tmp_path, "restore.json")["status"] == "failed"
    assert read(tmp_path, "disk-before-processing.json")["available_bytes"] == 0
    assert (tmp_path / "work/campaign/input.bin").read_bytes() == capture.payload
    assert not (tmp_path / "work/closed-postcapture.zip").exists()


def test_rejects_partial_explicit_identity_without_io(tmp_path, monkeypatch):
    fixture_capture(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="supplied together"):
        RESTORE.restore(capture_run_id="123", release_verified_delivery=True)
    assert not (tmp_path / "work").exists()


def test_existing_dangling_delivery_symlink_is_not_overwritten(tmp_path, monkeypatch):
    capture = fixture_capture(tmp_path, monkeypatch)
    work = tmp_path / "work"
    work.mkdir()
    delivery = work / "closed-postcapture.zip"
    try:
        delivery.symlink_to(work / "missing-target")
    except OSError:
        pytest.skip("platform does not permit creation of symlinks")
    with pytest.raises(AssertionError):
        RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert capture.downloads == []
    assert delivery.is_symlink()


def test_replaced_delivery_inode_is_not_removed(tmp_path, monkeypatch):
    capture = fixture_capture(tmp_path, monkeypatch)
    extract = RESTORE.transport._safe_extract

    def extract_and_replace(archive, destination):
        extract(archive, destination)
        saved = archive.with_name("original-delivery.backup")
        archive.rename(saved)
        archive.write_bytes(saved.read_bytes())

    monkeypatch.setattr(RESTORE.transport, "_safe_extract", extract_and_replace)
    with pytest.raises(AssertionError):
        RESTORE.restore(**capture.kwargs, release_verified_delivery=True)
    assert read(tmp_path, "restore.json")["status"] == "failed"
    assert (tmp_path / "work/closed-postcapture.zip").is_file()
    assert (tmp_path / "work/original-delivery.backup").is_file()
    assert (tmp_path / "work/campaign/input.bin").read_bytes() == capture.payload
    assert "delivery_working_copy" not in read(tmp_path, "restore.json")
