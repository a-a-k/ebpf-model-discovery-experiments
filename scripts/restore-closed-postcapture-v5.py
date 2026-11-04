"""Restore one exact same-run closed capture using the existing ZIP transport."""
import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import time
import zipfile

import requests

from ebpf_discovery import remote_toolchain_v4 as transport

def restore(*, capture_run_id=None, capture_source=None, release_verified_delivery=False):
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("closed capture restoration runs in GitHub Actions only")

    if (capture_run_id is None) != (capture_source is None):
        raise ValueError("explicit capture run and source must be supplied together")
    expected_run = str(capture_run_id or os.environ["GITHUB_RUN_ID"])
    expected_source = capture_source or os.environ["GITHUB_SHA"]
    work = Path("work").resolve()
    host = work / "offline-host"
    host.mkdir(parents=True, exist_ok=True)
    retry_log = host / "transport-retries.jsonl"
    record = {"status": "started", "started_ns": time.time_ns(), "retry_log_file": str(retry_log),
              "capture_run_id": expected_run, "capture_source": expected_source,
              "processing_run_id": os.environ["GITHUB_RUN_ID"], "processing_source": os.environ["GITHUB_SHA"]}
    try:
        artifact_id = int(os.environ["CAPTURE_ARTIFACT_ID"])
        expected_digest = "sha256:" + os.environ["CAPTURE_ARTIFACT_DIGEST"].removeprefix("sha256:")
        scientific_bytes = int(os.environ["CAPTURE_FILE_BYTES"])
        proof_bytes = int(os.environ["CAPTURE_PROOF_BYTES"])
        index_bytes = int(os.environ["CAPTURE_INDEX_BYTES"])
        assert min(scientific_bytes, proof_bytes, index_bytes) > 0
        session = requests.Session()
        headers = transport._headers(os.environ["GH_TOKEN"])
        api_url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{artifact_id}"
        metadata = transport._get(session, api_url, headers, retry_log=retry_log).json()
        assert metadata["id"] == artifact_id and not metadata["expired"]
        assert metadata["digest"] == expected_digest
        assert str(metadata["workflow_run"]["id"]) == expected_run
        assert metadata["workflow_run"]["head_sha"] == expected_source
        transport._atomic_json(host / "artifact-api.json", metadata)
        # Reserve the complete delivery and a separate SQL/WAL growth budget. This
        # is a disk reservation, not a cap on observations or database contents.
        required = metadata["size_in_bytes"] + scientific_bytes + proof_bytes + 4*index_bytes + 1024**3
        if release_verified_delivery:
            fixed = scientific_bytes + proof_bytes
            required = max(metadata["size_in_bytes"] + fixed, fixed + 4*index_bytes) + 1024**3
        guard = {"required_bytes": required, "available_bytes": shutil.disk_usage(work).free,
                 "archive_bytes": metadata["size_in_bytes"], "scientific_file_bytes": scientific_bytes,
                 "proof_bytes": proof_bytes, "SQL_WAL_growth_reserve_bytes": 4*index_bytes,
                 "scientific_limit_or_filter": False}
        if release_verified_delivery:
            guard.update(budget="verified-delivery-nonoverlapping-phases-v1",
                         download_restore_required_bytes=metadata["size_in_bytes"] + fixed + 1024**3,
                         restored_processing_peak_bytes=fixed + 4*index_bytes + 1024**3)
        transport._atomic_json(host / "disk-before-download.json", guard)
        assert guard["available_bytes"] >= required, "Closed-capture restore has insufficient actual disk capacity"
        archive, restored, campaign = work / "closed-postcapture.zip", work / "restored-postcapture", work / "campaign"
        assert not os.path.lexists(archive) and not restored.exists() and not campaign.exists()
        actual = transport._download(session, metadata["archive_download_url"], headers, archive,
                                     retry_log=retry_log)
        assert "sha256:"+actual == expected_digest and archive.stat().st_size == metadata["size_in_bytes"]
        delivery_stat = archive.lstat()
        assert stat.S_ISREG(delivery_stat.st_mode) and not archive.is_symlink()
        delivery_identity = {"device": delivery_stat.st_dev, "inode": delivery_stat.st_ino,
                             "type": stat.S_IFMT(delivery_stat.st_mode), "bytes": delivery_stat.st_size}
        record["verified_delivery_identity"] = delivery_identity
        with zipfile.ZipFile(archive) as bundle:
            members = bundle.infolist()
            assert all(e.filename.split("/", 1)[0] in {"campaign", "postcapture-proof"} for e in members)
            assert sum(e.file_size for e in members) == scientific_bytes + proof_bytes
        transport._safe_extract(archive, restored)
        (restored / "campaign").rename(campaign)
        proof = restored / "postcapture-proof"
        assert transport._sha(proof / "closed.json") == os.environ["CAPTURE_MANIFEST_SHA256"]
        closed = transport._read(proof / "closed.json")
        assert closed["file_bytes"] == scientific_bytes and closed["index_bytes"] == index_bytes
        assert closed["identity"]["run_id"] == expected_run
        assert closed["identity"]["commit"] == expected_source
        assert closed["identity"]["mode"] == os.environ["CAPTURE_MODE"]
        assert closed["identity"]["seed"] == int(os.environ["CAPTURE_SEED"])
        transport._atomic_json(proof / "artifact-api.json", metadata)
        if release_verified_delivery:
            # This exact owned delivery was completely SHA/size/EOF/CRC/marker checked above.
            # Its original API artifact and every restored scientific file remain intact.
            current = archive.lstat()
            assert stat.S_ISREG(current.st_mode) and not archive.is_symlink()
            assert {"device": current.st_dev, "inode": current.st_ino,
                    "type": stat.S_IFMT(current.st_mode), "bytes": current.st_size} == delivery_identity
            assert archive.parent == work and archive.name == "closed-postcapture.zip"
            free_before = shutil.disk_usage(work).free
            archive.unlink()
            assert not archive.exists()
            free_after = shutil.disk_usage(work).free
            record["delivery_working_copy"] = {"path": str(archive), "bytes": metadata["size_in_bytes"],
                "sha256": actual, "disposition": "verified_then_removed_owned_delivery",
                "removed_after_all_restore_checks": True, "verified_file_identity": delivery_identity, "free_before": free_before,
                "free_after": free_after, "recorded_ns": time.time_ns()}
            processing_guard = {"required_bytes": 4*index_bytes + 1024**3, "available_bytes": free_after,
                "SQL_WAL_growth_reserve_bytes": 4*index_bytes, "scientific_limit_or_filter": False,
                "scientific_tree_already_restored": True, "verified_delivery_removed": True}
            transport._atomic_json(host / "disk-before-processing.json", processing_guard)
            assert free_after >= processing_guard["required_bytes"], "Restored capture has insufficient actual SQL/WAL headroom"
        record.update(status="complete", artifact_id=artifact_id, artifact_digest=expected_digest,
                      archive_bytes=metadata["size_in_bytes"], archive_sha256=actual,
                      selected_members=len(members), all_original_members_read_to_EOF_and_CRC_checked=True,
                      closed_manifest_sha256=transport._sha(proof / "closed.json"),
                      actual_available_after_restore=shutil.disk_usage(work).free,
                      whole_scientific_manifest_validation="Required by finalize BEFORE any mutation")
        return record
    except BaseException as error:
        record.update(status="failed", error=repr(error))
        raise
    finally:
        record["ended_ns"] = time.time_ns()
        record["elapsed_seconds"] = (record["ended_ns"]-record["started_ns"])/1e9
        transport._atomic_json(host / "restore.json", record)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-run-id")
    parser.add_argument("--capture-source")
    parser.add_argument("--release-verified-delivery", action="store_true")
    args = parser.parse_args()
    restore(capture_run_id=args.capture_run_id, capture_source=args.capture_source,
            release_verified_delivery=args.release_verified_delivery)
