import hashlib
import json
import os
from pathlib import Path
import struct
import zipfile

import pytest

from ebpf_discovery.remote_toolchain_v4 import _safe_extract


def closed_zip(path, *, second=b"closed snapshot", hint=None):
    payload = b"closed snapshot"
    files = {
        "discovery/a.json": {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()},
        "discovery/b.json": {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()},
    }
    if hint is not None:
        files["discovery/b.json"] = hint
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("output-manifest.json", json.dumps({"toolchain_files": files}))
        archive.writestr("toolchain/discovery/a.json", payload)
        archive.writestr("toolchain/discovery/b.json", second)
        archive.writestr("toolchain/inputs/a.json", payload)
        archive.writestr("toolchain/inputs/b.json", payload)


def census(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mode)
            for p in root.rglob("*") if p.is_file()}


def test_closed_import_preserves_all_bytes_paths_modes_and_only_links_discovery(tmp_path):
    archive = tmp_path / "worker.zip"
    closed_zip(archive)
    baseline, candidate = tmp_path / "baseline", tmp_path / "candidate"
    assert _safe_extract(archive, baseline) is None
    proof = _safe_extract(archive, candidate, closed_discovery_links=True)
    assert census(baseline) == census(candidate)
    assert os.path.samefile(candidate / "toolchain/discovery/a.json",
                            candidate / "toolchain/discovery/b.json")
    assert not os.path.samefile(candidate / "toolchain/inputs/a.json",
                                candidate / "toolchain/inputs/b.json")
    assert not os.path.samefile(baseline / "toolchain/discovery/a.json",
                                baseline / "toolchain/discovery/b.json")
    assert proof["linked_files"] == 1
    assert proof["duplicate_bytes_not_allocated"] == len(b"closed snapshot")
    assert proof["discovery_members_verified"] == 2
    assert proof["all_original_members_read_to_EOF"] is True


def test_closed_import_verifies_duplicate_bytes_instead_of_trusting_hint(tmp_path):
    archive = tmp_path / "worker.zip"
    closed_zip(archive, second=b"changed payload")
    with pytest.raises(ValueError, match="differs from its file manifest"):
        _safe_extract(archive, tmp_path / "out", closed_discovery_links=True)
    assert not (tmp_path / "out/toolchain/discovery/b.json").exists()


def test_closed_import_consumes_duplicate_member_and_rejects_bad_crc(tmp_path):
    archive = tmp_path / "worker.zip"
    closed_zip(archive)
    with zipfile.ZipFile(archive) as bundle:
        member = bundle.getinfo("toolchain/discovery/b.json")
    body = bytearray(archive.read_bytes())
    name_size, extra_size = struct.unpack_from("<HH", body, member.header_offset + 26)
    offset = member.header_offset + 30 + name_size + extra_size
    body[offset] ^= 1
    archive.write_bytes(body)
    with pytest.raises(zipfile.BadZipFile, match="CRC"):
        _safe_extract(archive, tmp_path / "out", closed_discovery_links=True)
    assert not (tmp_path / "out/toolchain/discovery/b.json").exists()


@pytest.mark.parametrize("hint", [{"bytes": -1, "sha256": "0" * 64},
                                  {"bytes": 15, "sha256": "bad"}])
def test_closed_import_rejects_invalid_duplicate_hints(tmp_path, hint):
    archive = tmp_path / "worker.zip"
    closed_zip(archive, hint=hint)
    with pytest.raises(ValueError, match="hint is invalid"):
        _safe_extract(archive, tmp_path / "out", closed_discovery_links=True)


def test_default_restore_still_accepts_checkpoint_without_worker_manifest(tmp_path):
    archive = tmp_path / "checkpoint.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("checkpoint.json", "unchanged checkpoint")
    assert _safe_extract(archive, tmp_path / "out") is None
    assert (tmp_path / "out/checkpoint.json").read_text() == "unchanged checkpoint"
