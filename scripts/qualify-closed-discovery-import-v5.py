"""Actions-only lossless import check on one exact already-computed worker ZIP."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import requests

from ebpf_discovery import remote_toolchain_v4 as current


assert os.environ.get("GITHUB_ACTIONS") == "true"
workspace = Path.cwd().resolve()
work = workspace / "work/closed-discovery-import"
output = workspace / "results/closed-discovery-import"
assert not work.exists() and not output.exists()
work.mkdir(parents=True)
output.mkdir(parents=True)
anchor = "0056b4c8ecb85e8b40c433e63af442133a21f3cc"
source = subprocess.check_output(["git", "show", anchor + ":src/ebpf_discovery/remote_toolchain_v4.py"])
baseline_path = work / "baseline_remote.py"
baseline_path.write_bytes(source)
spec = importlib.util.spec_from_file_location("ebpf_discovery._closed_import_baseline", baseline_path)
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)

repo = "a-a-k/ebpf-model-discovery-experiments"
metadata = json.loads(subprocess.check_output([
    "gh", "api", f"repos/{repo}/actions/artifacts/13179122874"]))
assert metadata["workflow_run"]["id"] == 41504119650 and not metadata["expired"]
assert metadata["name"] == "toolchain-v4-otel_demo-absent-8-41504119650"
assert metadata["size_in_bytes"] == 2239207254
assert metadata["digest"] == "sha256:b3c0b592f0329f28e7c05bb4a06265d11b45271d96e60f47688f772579a96057"
current._atomic_json(output / "source-artifact.json", metadata)
required = 2239207254 + 32460309385 + 67108864
free = shutil.disk_usage(work).free
current._atomic_json(output / "disk-before.json", {"required_bytes": required, "available_bytes": free})
assert free >= required
archive = work / "worker.zip"
assert current._download(requests.Session(), metadata["archive_download_url"],
                         current._headers(os.environ["GH_TOKEN"]), archive) == metadata["digest"].split(":")[1]


def census(root):
    digest = hashlib.sha256()
    files = logical = allocated = 0
    inodes = set()
    for path in sorted(root.rglob("*")):
        assert not path.is_symlink()
        if not path.is_file():
            continue
        stat = path.stat()
        row = [path.relative_to(root).as_posix(), stat.st_size,
               stat.st_mode & 0o7777, current._sha(path)]
        digest.update(json.dumps(row, separators=(",", ":")).encode() + b"\n")
        files += 1
        logical += stat.st_size
        if (stat.st_dev, stat.st_ino) not in inodes:
            allocated += stat.st_blocks * 512
            inodes.add((stat.st_dev, stat.st_ino))
    return {"all_paths_bytes_modes_SHA256_census": digest.hexdigest(), "files": files,
            "logical_bytes": logical, "allocated_file_bytes": allocated, "unique_file_inodes": len(inodes)}


arms = []
for name, extractor in (("baseline", baseline._safe_extract), ("candidate", current._safe_extract)):
    arm = work / name
    started = time.time_ns()
    free_before = shutil.disk_usage(work).free
    extraction = extractor(archive, arm, **({"closed_discovery_links": True} if name == "candidate" else {}))
    expected = current._read(arm / "infrastructure/expected.json")
    assert expected["run_id"] == "41470540023" and expected["commit"] == anchor
    assert expected["worker_run_id"] == "41504119650" and expected["parent_cell_id"] == "otel_demo:absent:8"
    forecasts = current._verify_worker_output(arm, expected, 41504119650)
    record = {"arm": name, "started_ns": started, "ended_ns": time.time_ns(),
              "free_before": free_before, "free_after": shutil.disk_usage(work).free,
              "census": census(arm), "existing_worker_output_verification": "PASS",
              "forecasts_canonical_SHA256": current._json_sha(forecasts), "extraction": extraction}
    arms.append(record)
    current._atomic_json(output / (name + ".json"), record)
    # Exactly this newly-created qualification arm; the producer artifact is retained.
    assert arm.resolve().parent == work and arm.name == name and not arm.is_symlink()
    shutil.rmtree(arm)

left, right = (arm["census"] for arm in arms)
for key in ("all_paths_bytes_modes_SHA256_census", "files", "logical_bytes"):
    assert left[key] == right[key]
assert arms[0]["forecasts_canonical_SHA256"] == arms[1]["forecasts_canonical_SHA256"]
assert right["allocated_file_bytes"] < left["allocated_file_bytes"]
assert arms[1]["extraction"]["duplicate_bytes_not_allocated"] == 9919377680
current._atomic_json(output / "qualification.json", {
    "status": "complete", "source": os.environ["GITHUB_SHA"], "baseline_source": anchor,
    "baseline_module_SHA256": hashlib.sha256(source).hexdigest(), "artifact_id": metadata["id"],
    "artifact_digest": metadata["digest"], "arm_order": ["baseline", "candidate"], "arms": arms,
    "all_original_ZIP_member_CRC_and_actual_file_hashes_verified": True,
    "all_logical_paths_bytes_permissions_and_forecasts_equal": True,
    "allocated_file_bytes_saved": left["allocated_file_bytes"] - right["allocated_file_bytes"],
    "new_application_traffic": 0, "Bering_executions": 0, "Sheaft_executions": 0,
    "scope": "Exact retained-artifact import equality/allocation qualification only; fixed arm order, no speedup, full-case headroom, ENOSPC-instruction or scientific-case success claim."})
