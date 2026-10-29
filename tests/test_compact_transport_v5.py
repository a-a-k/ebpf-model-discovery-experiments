from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from ebpf_discovery.compact_transport_v5 import (
    extract_verified_compact,
    remove_verified_working_copy,
    verified_nonmaterialized_files,
)


def _archive(path: Path, *, journal_claim: str | None = None) -> tuple[str, bytes]:
    journal = b'{"attempt":1}\n'
    claim = journal_claim or hashlib.sha256(journal).hexdigest()
    manifest = json.dumps({
        "schema_version": "v5-cell-summary-manifest",
        "files_sha256": {
            "status.json": hashlib.sha256(b"{}\n").hexdigest(),
            "attempt-journal.jsonl": claim,
        },
    }).encode()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("evaluation-manifest.json", manifest)
        bundle.writestr("status.json", b"{}\n")
        bundle.writestr("attempt-journal.jsonl", journal)
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(), journal


def test_stream_verifies_all_members_and_does_not_materialize_journal(tmp_path: Path) -> None:
    archive = tmp_path / "compact.zip"
    expected, journal = _archive(archive)
    destination = tmp_path / "out"

    proof = extract_verified_compact(
        archive, destination, expected_digest=expected,
        expected_bytes=archive.stat().st_size,
    )
    remove_verified_working_copy(archive, proof)

    assert not archive.exists()
    assert (destination / "status.json").read_bytes() == b"{}\n"
    assert not (destination / "attempt-journal.jsonl").exists()
    assert proof["member_count"] == 3
    assert proof["working_copy_disposition"] == "verified_then_removed_working_copy"
    assert proof["skipped_member"]["sha256"] == hashlib.sha256(journal).hexdigest()
    assert verified_nonmaterialized_files(
        proof, destination / "evaluation-manifest.json", expected
    ) == {"attempt-journal.jsonl"}


def test_stream_rejects_api_and_manifest_tampering(tmp_path: Path) -> None:
    archive = tmp_path / "compact.zip"
    expected, _ = _archive(archive)
    with pytest.raises(ValueError, match="API digest"):
        extract_verified_compact(
            archive, tmp_path / "digest", expected_digest="sha256:" + "0" * 64
        )
    bad = tmp_path / "bad.zip"
    _archive(bad, journal_claim="0" * 64)
    bad_expected = "sha256:" + hashlib.sha256(bad.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="manifest hash mismatch"):
        extract_verified_compact(bad, tmp_path / "manifest", expected_digest=bad_expected)


def test_stream_preserves_harmless_directory_entries(tmp_path: Path) -> None:
    archive = tmp_path / "compact.zip"
    manifest = json.dumps({"files_sha256": {}}).encode()
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("observations/", b"")
        bundle.writestr("evaluation-manifest.json", manifest)
    digest = "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest()

    proof = extract_verified_compact(archive, tmp_path / "out", expected_digest=digest)

    directory = next(row for row in proof["members"] if row["name"] == "observations/")
    assert directory["directory"] is True
    assert directory["disposition"] == "verified_directory_entry"
    assert (tmp_path / "out/observations").is_dir()


def test_stream_rejects_directory_entry_with_payload(tmp_path: Path) -> None:
    archive = tmp_path / "compact.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("observations/", b"not-a-directory-payload")
        bundle.writestr("evaluation-manifest.json", json.dumps({"files_sha256": {}}))
    digest = "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest()

    with pytest.raises(ValueError, match="directory member carries data"):
        extract_verified_compact(archive, tmp_path / "out", expected_digest=digest)


def test_reader_rejects_tampered_or_nonjournal_skip_proof(tmp_path: Path) -> None:
    archive = tmp_path / "compact.zip"
    expected, _ = _archive(archive)
    destination = tmp_path / "out"
    proof = extract_verified_compact(archive, destination, expected_digest=expected)
    remove_verified_working_copy(archive, proof)

    original = proof["skipped_member"]["sha256"]
    proof["skipped_member"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="journal proof"):
        verified_nonmaterialized_files(
            proof, destination / "evaluation-manifest.json", expected
        )

    proof["skipped_member"]["sha256"] = original
    proof["members"][-1]["name"] = "status.json"
    with pytest.raises(ValueError, match="member proof|journal proof"):
        verified_nonmaterialized_files(
            proof, destination / "evaluation-manifest.json", expected
        )
