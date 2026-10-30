"""Repackage one immutable saved DSB worker tree and prove byte equivalence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time
import zipfile

from ebpf_discovery import artifact_transport_v4 as transport
from ebpf_discovery.remote_toolchain_v4 import _manifest

try:
    import resource
except ImportError:  # Windows unit import; saved validation runs on Linux Actions.
    resource = None


RUN_ID = 40956304402
PARENT_RUN_ID = 40942429097
ARTIFACT_ID = 12932698721
ARTIFACT_NAME = "toolchain-v4-deathstarbench-absent-6-40956304402"
ARTIFACT_BYTES = 169854924
ARTIFACT_SHA256 = "7569fbc7ae98112666f573b528f4a8e5a0625a4690ce58ddf17292208a040aaf"
WORKFLOW_HEAD = "597811ce6fad4466fd7f7511f4a5dc3bdc503a07"
SCIENTIFIC_HEAD = "5cfdd7cbb60daec95d447109a18f82219ea29e8f"


def _sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe(entry: zipfile.ZipInfo) -> bool:
    path = Path(entry.filename)
    mode = (entry.external_attr >> 16) & 0xFFFF
    return (not path.is_absolute() and ".." not in path.parts
            and not stat.S_ISLNK(mode))


def _extract_package(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries):
            raise ValueError("saved worker artifact ZIP contains duplicate names")
        if not all(_safe(entry) for entry in entries):
            raise ValueError("saved worker artifact ZIP contains unsafe names")
        bundle.extractall(destination)
    if {path.name for path in destination.iterdir()} != {
            transport.ARCHIVE, transport.MANIFEST, transport.MARKER,
            transport.STATUS, "packaging.json"}:
        raise ValueError("saved worker artifact is not one typed worker package")


def _validate_api(artifact: dict, run: dict, archive: Path) -> dict:
    expected_digest = "sha256:" + ARTIFACT_SHA256
    if (artifact.get("id") != ARTIFACT_ID or artifact.get("name") != ARTIFACT_NAME
            or artifact.get("size_in_bytes") != ARTIFACT_BYTES
            or artifact.get("digest") != expected_digest or artifact.get("expired") is not False
            or (artifact.get("workflow_run") or {}).get("id") != RUN_ID
            or (artifact.get("workflow_run") or {}).get("head_sha") != WORKFLOW_HEAD):
        raise ValueError("saved worker artifact API identity mismatch")
    if (run.get("id") != RUN_ID or run.get("head_sha") != WORKFLOW_HEAD
            or run.get("conclusion") != "success"):
        raise ValueError("saved worker run API identity mismatch")
    actual = {"bytes": archive.stat().st_size, "sha256": _sha(archive)}
    if actual != {"bytes": ARTIFACT_BYTES, "sha256": ARTIFACT_SHA256}:
        raise ValueError("saved worker artifact body differs from API identity")
    return actual


def validate(archive: Path, artifact_metadata: Path, run_metadata: Path, out: Path) -> dict:
    started, started_ns = time.monotonic(), time.time_ns()
    usage_before = resource.getrusage(resource.RUSAGE_SELF) if resource is not None else None
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    workspace = out.parent / (out.name + "-working")
    workspace.mkdir(parents=True, exist_ok=False)
    disk_before = shutil.disk_usage(workspace).free
    result = {"schema_version": "validate-worker-packaging-v4",
              "status": "started", "started_ns": started_ns}
    succeeded = False
    try:
        artifact = json.loads(Path(artifact_metadata).read_text(encoding="utf-8"))
        run = json.loads(Path(run_metadata).read_text(encoding="utf-8"))
        source_zip = _validate_api(artifact, run, Path(archive))
        original_package = workspace / "original-package"
        _extract_package(Path(archive), original_package)
        original_tree = workspace / "original-tree"
        original_unpack = transport.unpack(original_package, original_tree, kind="worker")
        original_files = _manifest(original_tree)
        for name in (transport.MANIFEST, transport.MARKER, transport.STATUS, "packaging.json"):
            shutil.copy2(original_package / name, out / ("original-" + name))

        current_package = workspace / "current-package"
        current_marker = transport.package(original_tree, current_package, kind="worker")
        current_tree = workspace / "current-tree"
        current_unpack = transport.unpack(current_package, current_tree, kind="worker")
        current_files = _manifest(current_tree)
        for name in (transport.MANIFEST, transport.MARKER, transport.STATUS, "packaging.json"):
            shutil.copy2(current_package / name, out / ("current-" + name))

        original_manifest = (original_package / transport.MANIFEST).read_bytes()
        current_manifest = (current_package / transport.MANIFEST).read_bytes()
        if original_files != current_files or original_manifest != current_manifest:
            raise ValueError("current worker package differs from saved worker tree")
        status = json.loads((original_tree / "worker-status.json").read_text(encoding="utf-8"))
        provenance = json.loads((original_tree / "worker-provenance.json").read_text(encoding="utf-8"))
        output_manifest = json.loads((original_tree / "output-manifest.json").read_text(encoding="utf-8"))
        identity = {"run_id": str(PARENT_RUN_ID), "commit": SCIENTIFIC_HEAD,
                    "system": "deathstarbench", "mode": "absent", "seed": "6"}
        status_identity = status.get("identity") or {}
        provenance_identity = provenance.get("identity") or {}
        output_identity = output_manifest.get("identity") or {}
        if (status.get("status") != "complete"
                or status_identity.get("worker_run_id") != str(RUN_ID)
                or status_identity.get("worker_workflow_sha") != WORKFLOW_HEAD
                or provenance.get("worker_run_id") != str(RUN_ID)
                or provenance.get("scientific_sha") != SCIENTIFIC_HEAD
                or provenance.get("implementation_sha") != SCIENTIFIC_HEAD
                or provenance.get("workflow_sha") != WORKFLOW_HEAD
                or output_manifest.get("worker_run_id") != str(RUN_ID)
                or output_manifest.get("workflow_sha") != WORKFLOW_HEAD
                or any(actual.get(key) != value for actual in
                       (status_identity, provenance_identity, output_identity)
                       for key, value in identity.items())):
            raise ValueError("saved worker internal source identity mismatch")
        repository = Path(__file__).resolve().parents[1]
        current_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repository, check=True,
            text=True, capture_output=True).stdout.strip()
        current_sources = {}
        for relative in (
                "src/ebpf_discovery/diagnostic_artifacts_v4.py",
                "src/ebpf_discovery/artifact_transport_v4.py",
                "src/ebpf_discovery/worker_process_group_v4.py",
                ".github/workflows/toolchain-worker-v4.yml",
                ".github/workflows/validate-worker-packaging-v4.yml"):
            current_sources[relative] = _sha(repository / relative)
        result.update({
            "status": "equivalent",
            "source": {"run_id": RUN_ID, "artifact_id": ARTIFACT_ID,
                       "artifact_name": ARTIFACT_NAME,
                       "workflow_head_sha": WORKFLOW_HEAD,
                       "parent_run_id": PARENT_RUN_ID,
                       "scientific_head_sha": SCIENTIFIC_HEAD,
                       "artifact_zip": source_zip,
                       "remote_original_retained": True},
            "current_implementation": {"commit": current_head,
                                       "source_sha256": current_sources},
            "comparison": {
                "files": len(original_files),
                "manifest_bytes": len(original_manifest),
                "manifest_sha256": hashlib.sha256(original_manifest).hexdigest(),
                "all_paths_bytes_modes_and_sha256_equal": True,
                "original_unpack": original_unpack,
                "current_unpack": current_unpack,
                "current_package": current_marker,
                "worker_status_sha256": _sha(original_tree / "worker-status.json"),
                "worker_provenance_sha256": _sha(original_tree / "worker-provenance.json"),
                "output_manifest_sha256": _sha(original_tree / "output-manifest.json"),
            },
            "scope": ("Saved immutable package/unpack/repackage equivalence only; does not "
                      "identify the historical run 40947264867 writer or prove a performance gain")})
        succeeded = True
    except BaseException as error:
        result.update(status="technical_failure", error=repr(error))
        raise
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
        if succeeded:
            Path(archive).unlink()
        usage_after = resource.getrusage(resource.RUSAGE_SELF) if resource is not None else None
        result.update(
            ended_ns=time.time_ns(), elapsed_seconds=time.monotonic() - started,
            disk_free_bytes_before=disk_before,
            disk_free_bytes_after=shutil.disk_usage(out).free,
            downloaded_working_zip_removed_after_verification=not Path(archive).exists(),
            working_trees_removed=not workspace.exists())
        if usage_before is not None and usage_after is not None:
            result.update(user_cpu_seconds=usage_after.ru_utime - usage_before.ru_utime,
                          system_cpu_seconds=usage_after.ru_stime - usage_before.ru_stime,
                          peak_rss_kib=usage_after.ru_maxrss)
        _write(out / "validation.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--artifact-metadata", type=Path, required=True)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    validate(args.archive, args.artifact_metadata, args.run_metadata, args.out)


if __name__ == "__main__":
    main()
