import hashlib
import json
from pathlib import Path
import zipfile
from types import SimpleNamespace

import pytest

import yaml

from ebpf_discovery.artifact_recovery_v5 import recover_declared_files


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _source(digest: str) -> dict:
    return {
        "repository": "MB3R-Lab/ebpf-model-discovery-experiments",
        "run_id": 40880849418,
        "head_sha": "a" * 40,
        "compact_artifact_id": 1,
        "compact_artifact_name": "v5-summary-cell",
        "compact_artifact_digest": "sha256:compact",
        "full_artifact_id": 2,
        "full_artifact_name": "campaign-v5-cell",
        "full_artifact_digest": digest,
        "full_artifact_size_in_bytes": None,
    }


def test_recovers_only_exact_manifest_member_with_full_zip_proof(tmp_path: Path) -> None:
    folder = tmp_path / "summary"
    folder.mkdir()
    journal = b'{"attempt":1}\n'
    (folder / "evaluation-manifest.json").write_text(json.dumps({
        "files_sha256": {"attempt-journal.jsonl": _sha(journal)},
    }))
    archive = tmp_path / "full.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("attempt-journal.jsonl", journal)
        bundle.writestr("unrequested-raw.bin", b"must not be copied")
    digest = "sha256:" + _sha(archive.read_bytes())

    proof = recover_declared_files(folder, archive, _source(digest))

    assert proof["status"] == "recovered"
    assert (folder / "attempt-journal.jsonl").read_bytes() == journal
    assert not (folder / "unrequested-raw.bin").exists()
    assert proof["source"]["full_zip_verification"] == {
        "path": str(archive), "expected_digest": digest,
        "computed_digest": digest, "received_bytes": archive.stat().st_size,
    }
    recovered = proof["recovered_files"][0]
    assert recovered["manifest_sha256"] == _sha(journal)
    assert recovered["copied_sha256"] == _sha(journal)
    assert recovered["copied_bytes"] == len(journal)
    assert recovered["zip_member_name"] == "attempt-journal.jsonl"
    assert proof["original_compact_unchanged"] is True
    assert proof["empirical_recomputation_performed"] is False


def test_wrong_full_zip_digest_remains_unavailable_without_copy(tmp_path: Path) -> None:
    folder = tmp_path / "summary"
    folder.mkdir()
    journal = b'{"attempt":1}\n'
    (folder / "evaluation-manifest.json").write_text(json.dumps({
        "files_sha256": {"attempt-journal.jsonl": _sha(journal)},
    }))
    archive = tmp_path / "full.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("attempt-journal.jsonl", journal)

    proof = recover_declared_files(folder, archive, _source("sha256:" + "0" * 64))

    assert proof["status"] == "full_zip_digest_mismatch"
    assert proof["recovered_files"] == []
    assert not (folder / "attempt-journal.jsonl").exists()


def test_does_not_assume_declared_member_from_nested_or_prefixed_transport(
        tmp_path: Path) -> None:
    folder = tmp_path / "summary"
    folder.mkdir()
    journal = b'{"attempt":1}\n'
    (folder / "evaluation-manifest.json").write_text(json.dumps({
        "files_sha256": {"attempt-journal.jsonl": _sha(journal)},
    }))
    archive = tmp_path / "full.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("toolchain-package/attempt-journal.jsonl", journal)
    digest = "sha256:" + _sha(archive.read_bytes())

    proof = recover_declared_files(folder, archive, _source(digest))

    assert proof["status"] == "declared_member_missing_from_full"
    assert proof["detail"] == "attempt-journal.jsonl"
    assert not (folder / "attempt-journal.jsonl").exists()


def test_future_compact_upload_includes_manifest_declared_journal() -> None:
    workflow = yaml.safe_load((
        Path(__file__).resolve().parents[1] / ".github" / "workflows" / "series-v5.yml"
    ).read_text(encoding="utf-8"))
    assert {"campaign", "postcapture"} <= set(workflow["jobs"])
    for job_name in ("campaign", "postcapture"):
        summaries = [step for step in workflow["jobs"][job_name]["steps"]
                     if step.get("uses", "").startswith("actions/upload-artifact@")
                     and step.get("with", {}).get("name", "").startswith("v5-summary-")]
        assert len(summaries) == 1, job_name
        paths = [line.strip() for line in summaries[0]["with"]["path"].splitlines()]
        assert paths.count("work/campaign/attempt-journal.jsonl") == 1, job_name


@pytest.mark.parametrize("spare", [-1, 0])
def test_recovery_checks_requested_bytes_before_reading_members(tmp_path, monkeypatch, spare):
    from ebpf_discovery.compact_transport_v5 import REPORT_DISK_RESERVE_BYTES, ReportDiskSpaceError
    folder = tmp_path / "summary"
    folder.mkdir()
    raw = b"requested metadata"
    (folder / "evaluation-manifest.json").write_text(json.dumps({
        "files_sha256": {"status.json": _sha(raw)},
    }))
    archive = tmp_path / "full.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("status.json", raw)
        bundle.writestr("unrequested.bin", b"x" * 8192)
    digest = "sha256:" + _sha(archive.read_bytes())
    monkeypatch.setattr("ebpf_discovery.compact_transport_v5.shutil.disk_usage",
                        lambda _: SimpleNamespace(free=REPORT_DISK_RESERVE_BYTES + len(raw) + spare))
    opened = []
    original = zipfile.ZipFile.open
    def observe(self, *args, **kwargs):
        opened.append(args[0])
        return original(self, *args, **kwargs)
    monkeypatch.setattr(zipfile.ZipFile, "open", observe)
    if spare < 0:
        with pytest.raises(ReportDiskSpaceError):
            recover_declared_files(folder, archive, _source(digest))
        assert opened == []
        assert not (folder / "status.json").exists()
    else:
        proof = recover_declared_files(folder, archive, _source(digest))
        assert proof["status"] == "recovered"
        assert proof["source"]["disk_before_recovery"]["incoming_bytes"] == len(raw)
        assert (folder / "status.json").read_bytes() == raw
        assert not (folder / "unrequested.bin").exists()
