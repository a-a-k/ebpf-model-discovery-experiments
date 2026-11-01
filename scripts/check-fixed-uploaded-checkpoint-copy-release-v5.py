"""One real saved T/full6 checkpoint: verify duplicate release, no model execution."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

import requests

from ebpf_discovery import remote_toolchain_v4 as remote

RUN = 41261041075
ARTIFACT = 13067209799
SOURCE = "06d7d52bfa4b7768a4cabf02f4e66f109b3a9492"
DIGEST = "sha256:49ca3a52504fd8087472087b852631fe0f2e0c3bac99813676e0136a7e975706"
MANIFEST = "7d7e6990be5caeba2e1698fe5a9736781d2b0df081fa6e1be3fdcacb594fc757"


def main():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("real saved-checkpoint work runs only in Actions")
    started = time.monotonic_ns()
    repository = os.environ["GITHUB_REPOSITORY"]
    headers = remote._headers(os.environ["GH_TOKEN"])
    session = requests.Session()
    work = Path("work").resolve()
    output = work / "checkpoint-copy-release-proof"
    output.mkdir(parents=True, exist_ok=False)
    checkpoint, live = work / "training-checkpoint", work / "campaign"
    assert not checkpoint.exists() and not live.exists()
    run = remote._get(session, f"https://api.github.com/repos/{repository}/actions/runs/{RUN}", headers).json()
    artifact = remote._get(session, f"https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}", headers).json()
    assert (run["id"], run["head_sha"], run["status"], run["conclusion"]) == (RUN, SOURCE, "completed", "failure")
    assert artifact["id"] == ARTIFACT and artifact["digest"] == DIGEST and artifact["expired"] is False
    assert artifact["workflow_run"]["id"] == RUN and artifact["workflow_run"]["head_sha"] == SOURCE
    assert artifact["name"] == f"training-v4-deathstarbench-full-6-{RUN}"
    remote._atomic_json(output / "original-run-api.json", run)
    remote._atomic_json(output / "original-artifact-api.json", artifact)
    archive = work / "fixed-T-full6-checkpoint.zip"
    download_start = time.monotonic_ns()
    actual_digest = remote._download(session, artifact["archive_download_url"], headers, archive)
    assert "sha256:" + actual_digest == DIGEST and archive.stat().st_size == artifact["size_in_bytes"]
    download_seconds = (time.monotonic_ns()-download_start)/1e9
    with zipfile.ZipFile(archive) as bundle:
        uncompressed = sum(member.file_size for member in bundle.infolist())
    free = shutil.disk_usage(work).free
    # Two physical payload copies model the parent and its uploaded snapshot.
    assert free > 2 * uncompressed + 64 * 1024 * 1024
    extract_start = time.monotonic_ns()
    remote._safe_extract(archive, checkpoint)
    extract_seconds = (time.monotonic_ns()-extract_start)/1e9
    ready = remote._read(checkpoint / "ready.json")
    assert ready["manifest_sha256"] == MANIFEST
    expected = {key: ready[key] for key in remote.IDENTITY_KEYS}
    assert (str(expected["run_id"]), expected["commit"], expected["system"], expected["mode"], expected["seed"]) == (
        str(RUN), SOURCE, "deathstarbench", "full", 6)
    expected.update(artifact_id=str(ARTIFACT), artifact_name=artifact["name"], artifact_digest=DIGEST)
    # The archived prefix predates release. This is labelled qualification control
    # metadata, never a claim that the old parent's literal release was recovered.
    remote._atomic_json(checkpoint / "release.json", {**expected, "upload_success": True,
        "qualification_control_only": True})
    validation_start = time.monotonic_ns()
    _, proof = remote._validate_checkpoint(checkpoint, expected)
    validation_seconds = (time.monotonic_ns()-validation_start)/1e9
    live.mkdir()
    mirror_start = time.monotonic_ns()
    for relative in proof["files"]:
        target = live / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(checkpoint / relative, target)
    mirror_seconds = (time.monotonic_ns()-mirror_start)/1e9
    metadata_before = {name: remote._sha(checkpoint / name) for name in ("manifest.json", "ready.json", "release.json")}
    result = remote._release_uploaded_checkpoint_copy(checkpoint, live, expected, proof,
        session, headers, repository, output)
    assert result["status"] == "released_verified_local_payload"
    assert result["removed_files"] == len(proof["files"])
    assert result["logical_bytes_unlinked"] == sum(row["bytes"] for row in proof["files"].values())
    assert {p.name for p in checkpoint.iterdir()} == set(metadata_before)
    assert {name: remote._sha(checkpoint / name) for name in metadata_before} == metadata_before
    mirror_after = {}
    for relative, record in proof["files"].items():
        target = live / relative
        mirror_after[relative] = {"bytes": target.stat().st_size, "sha256": remote._sha(target)}
        assert mirror_after[relative] == record
    final_artifact = remote._get(session,
        f"https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}", headers).json()
    assert final_artifact["digest"] == DIGEST and final_artifact["expired"] is False
    assert result["observed_disk_free_delta"] > 0
    remote._atomic_json(output / "proof.json", {
        "schema_version": "fixed-uploaded-checkpoint-copy-release-proof-v5",
        "implementation_commit": os.environ["GITHUB_SHA"],
        "implementation_module_sha256": hashlib.sha256(Path(remote.__file__).read_bytes()).hexdigest(),
        "source_run": RUN, "source_commit": SOURCE, "original_artifact": ARTIFACT,
        "original_archive_sha256": actual_digest, "original_archive_bytes": archive.stat().st_size,
        "archive_declared_uncompressed_bytes": uncompressed,
        "checkpoint_manifest_sha256": MANIFEST, "source_payload_files": len(proof["files"]),
        "source_payload_bytes": sum(row["bytes"] for row in proof["files"].values()),
        "all_physical_live_mirror_files_after": mirror_after,
        "retained_metadata_sha256": metadata_before, "release_control_is_synthetic_and_labelled": True,
        "cleanup": result, "remote_original_still_available": True,
        "download_seconds": download_seconds, "extract_seconds": extract_seconds,
        "full_checkpoint_validation_seconds": validation_seconds, "physical_mirror_seconds": mirror_seconds,
        "total_seconds": (time.monotonic_ns()-started)/1e9,
        "new_application_traffic": False, "new_models_or_simulations": False,
        "no_end_to_end_or_sufficient_headroom_claim": True})
    subprocess.run(["df", "-B1", "."], check=True, stdout=(output / "disk-final.txt").open("w"))


if __name__ == "__main__":
    main()
