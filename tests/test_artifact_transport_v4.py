import gzip
import hashlib
import json
import os
from pathlib import Path
import tarfile

import pytest

from ebpf_discovery import artifact_transport_v4 as transport


@pytest.mark.parametrize("kind", ["worker", "toolchain", "handoff"])
def test_lossless_package_and_unpacked_tree_with_modes(tmp_path, kind):
    source = tmp_path / "source"
    (source / "nested").mkdir(parents=True)
    (source / "nested" / "output.bin").write_bytes(b"\x00\xff" * 8193)
    (source / "empty").mkdir()
    (source / "nested" / "output.bin").chmod(0o640)
    package = tmp_path / "package"
    marker = transport.package(source, package, kind=kind)
    assert marker["files"] == 1 and marker["directories"] == 2
    assert {p.name for p in package.iterdir()} == {
        "payload.tar.gz", "payload.manifest.jsonl", "transport.json",
        "package-status.json", "packaging.json"}
    destination = tmp_path / "unpacked"
    proof = transport.unpack(package, destination, kind=kind)
    assert proof["archive_sha256"] == marker["archive_sha256"]
    assert (destination / "nested/output.bin").read_bytes() == (source / "nested/output.bin").read_bytes()
    assert (destination / "empty").is_dir()
    if os.name != "nt":
        assert (destination / "nested/output.bin").stat().st_mode & 0o777 == 0o640
    assert (source / "nested/output.bin").is_file()  # No move or trim.


def test_tampered_payload_or_manifest_rejected_without_published_tree(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a").write_bytes(b"original")
    package = tmp_path / "package"
    transport.package(source, package, kind="toolchain")
    (package / "payload.tar.gz").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="differs"):
        transport.unpack(package, tmp_path / "out", kind="toolchain")
    assert not (tmp_path / "out").exists()


def test_wrong_kind_and_extra_layout_rejected(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a").write_bytes(b"original")
    package = tmp_path / "package"
    transport.package(source, package, kind="worker")
    with pytest.raises(ValueError, match="marker"):
        transport.unpack(package, tmp_path / "wrong", kind="toolchain")
    (package / "unlisted").write_text("extra")
    with pytest.raises(ValueError, match="layout"):
        transport.unpack(package, tmp_path / "extra", kind="worker")


def test_source_link_rejected_before_package_success(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    outside = tmp_path / "outside"
    outside.write_bytes(b"unrelated")
    try:
        (source / "link").symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    package = tmp_path / "package"
    with pytest.raises(ValueError, match="unsupported"):
        transport.package(source, package, kind="worker")
    assert json.loads((package / "package-status.json").read_text())["status"] == "packaging_failed"
    assert not (package / "transport.json").exists()


def test_status_write_failure_preserves_primary_packaging_error(tmp_path, monkeypatch, capsys):
    source = tmp_path / "source"
    source.mkdir()
    package = tmp_path / "package"
    original_write = transport._write
    def write(path, value):
        if path.name == "package-status.json" and value.get("status") == "packaging_failed":
            raise OSError("status disk full")
        original_write(path, value)
    def fail_package(*_args):
        raise OSError("primary packaging failure")
    monkeypatch.setattr(transport, "_write", write)
    monkeypatch.setattr(transport.diagnostic_artifacts_v4, "package", fail_package)
    with pytest.raises(OSError, match="primary packaging failure"):
        transport.package(source, package, kind="worker")
    assert "ARTIFACT_PACKAGING_STATUS_WRITE_ERROR" in capsys.readouterr().out


def test_status_write_failure_after_good_package_is_fatal(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a").write_bytes(b"a")
    original_write = transport._write
    def write(path, value):
        if path.name == "package-status.json" and value.get("status") == "complete":
            raise OSError("status disk full")
        original_write(path, value)
    monkeypatch.setattr(transport, "_write", write)
    with pytest.raises(OSError, match="status disk full"):
        transport.package(source, tmp_path / "package", kind="worker")


def test_internal_manifest_duplicate_rejected_even_with_resealed_outer_hash(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a").write_bytes(b"a")
    package = tmp_path / "package"
    transport.package(source, package, kind="worker")
    manifest = package / "payload.manifest.jsonl"
    row = manifest.read_text()
    manifest.write_text(row + row)
    marker = json.loads((package / "transport.json").read_text())
    marker["manifest_bytes"] = manifest.stat().st_size
    marker["manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    transport._write(package / "transport.json", marker)
    packaging = json.loads((package / "packaging.json").read_text())
    packaging["manifest_sha256"] = marker["manifest_sha256"]
    transport._write(package / "packaging.json", packaging)
    status = json.loads((package / "package-status.json").read_text())
    status["marker_sha256"] = transport._sha(package / "transport.json")
    transport._write(package / "package-status.json", status)
    with pytest.raises(ValueError, match="omitted manifested"):
        transport.unpack(package, tmp_path / "out", kind="worker")
    assert not (tmp_path / "out").exists()


def test_archive_member_traversal_rejected_with_resealed_outer_hash(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a").write_bytes(b"a")
    package = tmp_path / "package"
    transport.package(source, package, kind="worker")
    archive_path = package / "payload.tar.gz"
    malicious = tmp_path / "malicious.tar.gz"
    with gzip.open(malicious, "wb") as wire, tarfile.open(fileobj=wire, mode="w|") as archive:
        member = tarfile.TarInfo("../escape")
        member.size = 0
        archive.addfile(member)
    os.replace(malicious, archive_path)
    marker = json.loads((package / "transport.json").read_text())
    marker["archive_bytes"] = archive_path.stat().st_size
    marker["archive_sha256"] = transport._sha(archive_path)
    transport._write(package / "transport.json", marker)
    packaging = json.loads((package / "packaging.json").read_text())
    packaging["archive_bytes"] = marker["archive_bytes"]
    packaging["archive_sha256"] = marker["archive_sha256"]
    transport._write(package / "packaging.json", packaging)
    status = json.loads((package / "package-status.json").read_text())
    status["marker_sha256"] = transport._sha(package / "transport.json")
    transport._write(package / "package-status.json", status)
    with pytest.raises(ValueError, match="mismatched"):
        transport.unpack(package, tmp_path / "out", kind="worker")
    assert not (tmp_path / "escape").exists()
    assert not (tmp_path / "out").exists()


def test_series_requires_both_full_subtree_packages_and_retains_restore_proof():
    workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/series-v4.yml").read_text()
    assert "--source work/campaign/toolchain --out work/campaign/toolchain-package" in workflow
    assert "--source work/campaign/infrastructure/remote-toolchain-v4" in workflow
    assert "--out work/campaign/infrastructure/handoff-package --kind handoff" in workflow
    assert "steps.full_toolchain_package.outputs.ready == 'true'" in workflow
    assert "steps.full_handoff_package.outputs.ready == 'true'" in workflow
    assert "steps.retention_layout.outputs.ready == 'true'" in workflow
    assert "!work/campaign/toolchain/**" in workflow
    assert "!work/campaign/infrastructure/remote-toolchain-v4/**" in workflow
    assert "work/campaign/infrastructure/handoff-package/package-status.json" in workflow
    assert "work/campaign/retention-layout.json" in workflow
