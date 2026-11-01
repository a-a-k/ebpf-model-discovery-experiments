"""Actions-only byte-preservation/storage proof, using one real saved raw prefix.

The prefix is a CLOSED REPLAY fixture, not the lost final guest suffix. No traffic,
models, simulations, scores or campaign eligibility decisions are made here.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import time
import zipfile

import requests

from ebpf_discovery import deepflow_snapshot_v5 as implementation
from ebpf_discovery import remote_toolchain_v4 as remote

RUN = 41273434210
ARTIFACT = 13073478195
SOURCE = "06d7d52bfa4b7768a4cabf02f4e66f109b3a9492"
DIGEST = "sha256:02c499bca37d3e5d91299234840cedf2132f499e16cee77fb1e5b6ee70b9ba99"
MANIFEST = "8b4af034ca142e7760f26dcfc64782baf3a134550df90cb138cfee0dcd60bfdf"
MIB = 1024 * 1024


def census(directory):
    return {p.name: {"bytes": p.stat().st_size, "sha256": remote._sha(p),
                      "mode": stat.S_IMODE(p.stat().st_mode), "uid": p.stat().st_uid}
            for p in sorted(directory.iterdir()) if p.is_file()}


def filesystem(directory):
    value = os.statvfs(directory)
    return {"free_bytes": value.f_bfree * value.f_frsize,
            "available_bytes": value.f_bavail * value.f_frsize,
            "free_inodes": value.f_ffree}


def command(*args):
    subprocess.run(args, check=True, capture_output=True, text=True)


def main():
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.geteuid() != 0:
        raise RuntimeError("real saved-prefix/loop-filesystem proof runs only as root in Actions")
    started = time.monotonic_ns()
    work = Path("work").resolve()
    output = work / "deepflow-final-links-proof"
    output.mkdir(exist_ok=True)
    scratch = work / "deepflow-final-links-scratch"
    scratch.mkdir(exist_ok=False)
    mount = scratch / "mounted"
    mount.mkdir()
    headers = remote._headers(os.environ["GH_TOKEN"])
    session = requests.Session()
    repository = os.environ["GITHUB_REPOSITORY"]
    run = remote._get(session, f"https://api.github.com/repos/{repository}/actions/runs/{RUN}", headers).json()
    artifact = remote._get(session, f"https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}", headers).json()
    assert (run["id"], run["head_sha"], run["status"], run["conclusion"]) == (RUN, SOURCE, "completed", "failure")
    assert (artifact["id"], artifact["digest"], artifact["expired"]) == (ARTIFACT, DIGEST, False)
    assert artifact["name"] == f"training-v4-otel_demo-partial-6-{RUN}"
    assert artifact["workflow_run"]["id"] == RUN and artifact["workflow_run"]["head_sha"] == SOURCE
    remote._atomic_json(output / "original-run-api.json", run)
    remote._atomic_json(output / "original-artifact-api.json", artifact)
    archive = scratch / "original.zip"
    download_start = time.monotonic_ns()
    actual_digest = remote._download(session, artifact["archive_download_url"], headers, archive)
    assert "sha256:" + actual_digest == DIGEST and archive.stat().st_size == artifact["size_in_bytes"]
    download_seconds = (time.monotonic_ns() - download_start) / 1e9
    validation_start = time.monotonic_ns()
    selected = {}
    source_census = {}
    with zipfile.ZipFile(archive) as bundle:
        entries = {}
        for member in bundle.infolist():
            path = PurePosixPath(member.filename)
            assert (not path.is_absolute() and ".." not in path.parts
                    and "\\" not in member.filename and not stat.S_ISLNK(member.external_attr >> 16)
                    and member.filename not in entries)
            entries[member.filename] = member
        manifest_bytes = bundle.read("manifest.json")
        assert hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST
        manifest = json.loads(manifest_bytes)
        ready = json.loads(bundle.read("ready.json"))
        assert manifest["schema_version"] == "v4-training-prefix-checkpoint"
        assert manifest["status"] == "partial_training_capture_only; no forecast or completed cell"
        assert ready["status"] == "training_checkpoint_ready" and ready["manifest_sha256"] == MANIFEST
        for key, expected in {"run_id": RUN, "commit": SOURCE, "system": "otel_demo", "mode": "partial", "seed": 6}.items():
            assert str(manifest["identity"][key]) == str(expected) == str(ready[key])
        files = manifest["files"]
        assert files and {name for name, info in entries.items() if not info.is_dir()} == set(files) | {"manifest.json", "ready.json"}
        # Select the latest genuine captured raw prefix on BOTH independent nodes.
        for node in ("a", "b"):
            groups = {}
            for relative in files:
                parts = PurePosixPath(relative).parts
                if "deepflow-raw" in parts:
                    position = parts.index("deepflow-raw")
                    if len(parts) == position + 4 and parts[position + 1] == f"node-{node}" and parts[-1].startswith("l7_flow_log"):
                        groups.setdefault(parts[position + 2], []).append(relative)
            assert groups, f"actual raw prefix missing for node {node}"
            stage = max(groups)
            selected[node] = sorted(groups[stage])
        selected_names = {relative for relatives in selected.values() for relative in relatives}
        assert shutil.disk_usage(scratch).free > sum(files[name]["bytes"] for name in selected_names) * 5 + 512 * MIB
        for relative, record in sorted(files.items()):
            assert record["relative_path"] == relative
            target = scratch / "selected" / relative if relative in selected_names else None
            if target is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
            digest, length = hashlib.sha256(), 0
            with bundle.open(entries[relative]) as source, contextlib.ExitStack() as stack:
                destination = stack.enter_context(target.open("xb")) if target is not None else None
                while chunk := source.read(MIB):
                    digest.update(chunk)
                    length += len(chunk)
                    if destination is not None:
                        destination.write(chunk)
            assert {"bytes": length, "sha256": digest.hexdigest()} == {key: record[key] for key in ("bytes", "sha256")}
            source_census[relative] = {"bytes": length, "sha256": digest.hexdigest()}
    validation_seconds = (time.monotonic_ns() - validation_start) / 1e9
    remote._atomic_json(output / "original-payload-validation.json", {"manifest_sha256": MANIFEST,
        "all_files": source_census, "all_zip_member_CRCs_checked_by_full_reads": True, "selected_raw": selected})
    # The archive's complete digest/census is retained; its recoverable local copy
    # is no longer needed while exercising the bounded filesystems.
    archive.unlink()
    baseline_source = Path(__file__).resolve().parents[1] / "src/ebpf_discovery/deepflow_snapshot_v5.py"
    baseline_bytes = subprocess.check_output(["git", "show", f"{SOURCE}:src/ebpf_discovery/deepflow_snapshot_v5.py"])
    baseline = scratch / "original-snapshot.py"
    baseline.write_bytes(baseline_bytes)
    results = {}
    for node, relatives in selected.items():
        node_start = time.monotonic_ns()
        logical_bytes = sum(source_census[name]["bytes"] for name in relatives)
        maximum_file = max(source_census[name]["bytes"] for name in relatives)
        assert maximum_file > MIB
        image_bytes = ((logical_bytes + logical_bytes // 8 + 64 * MIB + MIB - 1) // MIB) * MIB
        assert shutil.disk_usage(scratch).free > 2 * image_bytes + logical_bytes + 128 * MIB
        pristine, active = scratch / "pristine.ext4", scratch / "active.ext4"
        with pristine.open("xb") as stream:
            stream.truncate(image_bytes)
        command("mkfs.ext4", "-q", "-F", "-m", "0", str(pristine))
        mounted = False
        try:
            command("mount", "-o", "loop,noatime", str(pristine), str(mount))
            mounted = True
            data = mount / "data"
            data.mkdir()
            for relative in relatives:
                shutil.copyfile(scratch / "selected" / relative, data / PurePosixPath(relative).name)
            original = census(data)
            assert {name: {k: row[k] for k in ("bytes", "sha256")} for name, row in original.items()} == {
                PurePosixPath(name).name: source_census[name] for name in relatives}
            # The bounded filesystem itself cannot fit another full source file.
            # No filler allocation depends on reported free space being allocatable.
            command("sync")
            initial_space = filesystem(mount)
            assert initial_space["available_bytes"] > 64 * 1024
            assert initial_space["free_bytes"] < maximum_file
            command("umount", str(mount))
            mounted = False
            pristine_sha = remote._sha(pristine)
            comparisons = {}
            original_manifest = None
            for method in ("roomy_original_copy", "tight_original_copy", "tight_closed_links"):
                shutil.copyfile(pristine, active)
                assert remote._sha(active) == pristine_sha
                command("mount", "-o", "loop,noatime", str(active), str(mount))
                mounted = True
                before = filesystem(mount)
                assert census(data) == original
                destination = scratch / "roomy-final" if method.startswith("roomy") else mount / "final"
                operation_start = time.monotonic_ns()
                failure = None
                if method == "tight_closed_links":
                    audit = io.StringIO()
                    with contextlib.redirect_stdout(audit):
                        implementation.snapshot(data, destination, "final", producer_closed=True)
                    storage = json.loads(audit.getvalue())
                    remote._atomic_json(output / f"node-{node}-storage-audit.json", storage)
                else:
                    result = subprocess.run(["python", str(baseline), "--data", str(data), "--out", str(destination), "--mode", "final"], capture_output=True, text=True)
                    if result.returncode:
                        assert method == "tight_original_copy" and "[Errno 28] No space left on device" in result.stderr
                        failure = {"returncode": result.returncode, "stderr": result.stderr}
                    else:
                        assert method == "roomy_original_copy", "tight original copy unexpectedly fit"
                elapsed = (time.monotonic_ns() - operation_start) / 1e9
                assert census(data) == original
                comparison = {"initial_filesystem": before, "final_filesystem": filesystem(mount),
                    "elapsed_seconds": elapsed, "error": failure, "source_hashes_lengths_modes_uid_unchanged": True,
                    "starting_image_sha256": pristine_sha, "running_uid": os.geteuid()}
                if failure is None:
                    snapshot_bytes = (destination / "snapshot.json").read_bytes()
                    snapshot = json.loads(snapshot_bytes)
                    assert {row["snapshot_name"]: {"bytes": row["copied_bytes"], "sha256": row["copied_sha256"]} for row in snapshot["files"]} == {
                        name: {key: row[key] for key in ("bytes", "sha256")} for name, row in original.items()}
                    targets = census(destination)
                    for name, row in original.items():
                        assert targets[name]["bytes"] == row["bytes"] and targets[name]["sha256"] == row["sha256"]
                        if method == "tight_closed_links":
                            assert (data / name).stat().st_ino == (destination / name).stat().st_ino
                            assert targets[name]["mode"] == row["mode"]
                    if original_manifest is None:
                        original_manifest = snapshot_bytes
                    else:
                        assert snapshot_bytes == original_manifest
                    (output / f"node-{node}-{method}-snapshot.json").write_bytes(snapshot_bytes)
                    comparison["snapshot_manifest_sha256"] = hashlib.sha256(snapshot_bytes).hexdigest()
                    comparison["full_target_file_hashes"] = targets
                comparisons[method] = comparison
                command("umount", str(mount))
                mounted = False
                active.unlink()
                if destination == scratch / "roomy-final":
                    shutil.rmtree(destination)
            assert comparisons["tight_original_copy"]["initial_filesystem"] == comparisons["tight_closed_links"]["initial_filesystem"]
            results[node] = {"selected_source": relatives, "logical_bytes": logical_bytes,
                "image_bytes": image_bytes, "synthetic_filler_bytes": 0,
                "storage_pressure": "bounded ext4 filesystem; no filler file",
                "original_source_census": original, "comparisons": comparisons,
                "node_total_seconds": (time.monotonic_ns() - node_start) / 1e9}
            remote._atomic_json(output / f"node-{node}-comparison.json", results[node])
        finally:
            if mounted:
                command("umount", str(mount))
            active.unlink(missing_ok=True)
            pristine.unlink(missing_ok=True)
    final_api = remote._get(session, f"https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}", headers).json()
    assert final_api["digest"] == DIGEST and final_api["expired"] is False
    shutil.rmtree(scratch)
    remote._atomic_json(output / "proof.json", {
        "schema": "fixed-deepflow-closed-final-hardlink-proof-v5", "implementation_commit": os.environ["GITHUB_SHA"],
        "implementation_module_sha256": remote._sha(baseline_source),
        "original_copy_module_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
        "source_run": RUN, "source_commit": SOURCE, "source_artifact": ARTIFACT,
        "source_archive_sha256": actual_digest, "source_archive_bytes": artifact["size_in_bytes"],
        "checkpoint_manifest_sha256": MANIFEST, "download_seconds": download_seconds,
        "full_zip_crc_and_payload_hash_validation_seconds": validation_seconds,
        "closed_replay_of_saved_prefix_only": True, "lost_final_guest_suffix_reconstructed": False,
        "new_traffic_models_simulations_or_scores": False, "campaign_eligibility_changed": False,
        "zero_loss_or_full_case_success_claimed": False, "source_artifact_still_available": True,
        "scratch_copies_deleted_after_proof": True, "nodes": results,
        "total_seconds_including_validation_and_cleanup": (time.monotonic_ns() - started) / 1e9})


if __name__ == "__main__":
    main()
