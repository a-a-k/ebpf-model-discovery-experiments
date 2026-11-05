"""Create immutable DeepFlow standalone file snapshots on a guest.

This file is intentionally stdlib-only: the campaign uploads and executes it on
each guest. Prefix mode copies only complete JSONL records. Failure mode copies
all currently available bytes without claiming producer closure. Final mode
runs after collector termination and copies every regular standalone byte.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import time


def _sha256(path: Path, limit: int | None = None) -> str:
    digest = hashlib.sha256()
    remaining = limit
    with path.open("rb") as stream:
        while remaining is None or remaining:
            size = 1024 * 1024 if remaining is None else min(1024 * 1024, remaining)
            chunk = stream.read(size)
            if not chunk:
                break
            digest.update(chunk)
            if remaining is not None:
                remaining -= len(chunk)
    return digest.hexdigest()


def _complete_prefix(path: Path, size: int) -> int:
    if not size:
        return 0
    with path.open("rb") as stream:
        position = size
        while position:
            length = min(position, 65536)
            position -= length
            stream.seek(position)
            end = stream.read(length).rfind(b"\n")
            if end >= 0:
                return position + end + 1
    return 0


def _copy(path: Path, target: Path, length: int) -> str:
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    digest = hashlib.sha256()
    remaining = length
    try:
        with path.open("rb") as source, os.fdopen(descriptor, "wb") as output:
            while remaining:
                chunk = source.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise RuntimeError(f"source shortened while copying {path}")
                output.write(chunk)
                digest.update(chunk)
                remaining -= len(chunk)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return digest.hexdigest()


def _link_closed_final(path: Path, target: Path, length: int) -> tuple[str, dict]:
    """Retain the closed inode at both paths, without another full data allocation."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or path.is_symlink():
        raise ValueError(f"closed snapshot source must be a regular non-symlink: {path}")
    if before.st_size != length or before.st_dev != target.parent.stat().st_dev:
        raise ValueError(f"closed snapshot source size/filesystem mismatch: {path}")
    linked = False
    try:
        os.link(path, target, follow_symlinks=False)
        linked = True
        retained = target.lstat()
        if (not stat.S_ISREG(retained.st_mode)
                or (retained.st_dev, retained.st_ino) != (before.st_dev, before.st_ino)):
            raise RuntimeError(f"closed snapshot link identity mismatch: {path}")
        copied_hash = _sha256(target)
        after = path.lstat()
        retained = target.lstat()
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
        if identity(after) != identity(before) or identity(retained) != identity(before):
            raise RuntimeError(f"closed snapshot source changed while hashing: {path}")
        return copied_hash, {
            "name": path.name, "logical_bytes": length,
            "source_device": before.st_dev, "snapshot_device": retained.st_dev,
            "source_inode": before.st_ino, "snapshot_inode": retained.st_ino,
            "source_mode": stat.S_IMODE(before.st_mode),
            "snapshot_mode": stat.S_IMODE(retained.st_mode),
            "same_inode": True, "source_path_retained": True,
        }
    except BaseException:
        if linked:
            target.unlink(missing_ok=True)
        raise


def snapshot(data: Path, out: Path, mode: str, *, producer_closed: bool = False) -> dict:
    data, out = Path(data), Path(out)
    if producer_closed and mode != "final":
        raise ValueError("hardlinks require final mode and explicit producer closure")
    if out.exists():
        raise FileExistsError(f"snapshot output already exists: {out}")
    out.mkdir(parents=True)
    started_ns = time.time_ns() if producer_closed else None
    free_before = shutil.disk_usage(out).free if producer_closed else None
    storage_files = []
    files = []
    for path in sorted(item for item in data.iterdir() if item.is_file()):
        if mode == "prefix" and path.name not in {"l7_flow_log", "l7_flow_log.pre"}:
            continue
        before = path.stat().st_size
        prefix = _complete_prefix(path, before) if path.name.startswith("l7_flow_log") else before
        copied = prefix if mode == "prefix" else before
        target = out / path.name
        if producer_closed:
            copied_hash, storage = _link_closed_final(path, target, copied)
            storage_files.append(storage)
        else:
            copied_hash = _copy(path, target, copied)
        after = path.stat().st_size
        files.append({
            "source_name": path.name,
            "snapshot_name": target.name,
            "source_size_before": before,
            "source_size_after": after,
            "source_changed_during_snapshot": before != after,
            "copied_bytes": copied,
            "copied_sha256": copied_hash,
            "complete_prefix_bytes": prefix,
            "complete_prefix_sha256": _sha256(target, min(prefix, copied)),
            "pending_tail_bytes_at_read": before - prefix,
            "full_file_retained": mode in {"failure", "final"},
        })
    manifest = {
        "schema": "deepflow-standalone-snapshot-v5",
        "mode": mode,
        "data_directory": str(data),
        "files": files,
        "l7_rotation_observed": any(item["source_name"] == "l7_flow_log.pre" for item in files),
        "rotation_observed": any(item["source_name"].endswith(".pre") for item in files),
        "complete_prefix_only": mode == "prefix",
        "startup_incomplete": mode == "failure",
        "producer_closed": mode == "final",
        "closed_checkpoint": mode == "final",
    }
    (out / "snapshot.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if producer_closed:
        audit = {
            "schema": "deepflow-closed-final-snapshot-storage-v5",
            "strategy": "hardlinks_after_positive_per_node_termination",
            "positive_external_producer_closure_supplied": True,
            "source_paths_unlinked": False,
            "logical_bytes_retained": sum(item["logical_bytes"] for item in storage_files),
            "free_bytes_before": free_before,
            "free_bytes_after_manifest": shutil.disk_usage(out).free,
            "elapsed_seconds": (time.time_ns() - started_ns) / 1e9,
            "files": storage_files,
            "scope": "same full bytes and unchanged snapshot manifest; no zero-loss or case-success claim",
        }
        # Keep this diagnostic off the nearly full guest filesystem.
        print(json.dumps(audit, sort_keys=True), flush=True)
    return manifest


def release_verified_prefix(data: Path, out: Path, manifest_sha256: str) -> dict:
    """Release an imported prefix copy, retaining the live file and parent mirror."""
    started = time.monotonic_ns()
    data, out = Path(data), Path(out)
    root = data.parent.resolve()
    if (data.is_symlink() or data.parent.is_symlink() or data.name != "data" or not data.is_dir()
            or out.is_symlink() or out.parent.is_symlink()
            or not out.is_dir() or out.stat().st_dev != data.stat().st_dev
            or out.resolve().parent != root / "snapshots" or out.resolve() == data.resolve()):
        raise ValueError("prefix release is outside the owned snapshot directory")
    manifest_path = out / "snapshot.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("prefix release lacks its original regular manifest")
    free_before = shutil.disk_usage(out).free
    if _sha256(manifest_path) != manifest_sha256:
        raise ValueError("prefix release manifest differs from the imported manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("mode") != "prefix" or manifest.get("complete_prefix_only") is not True
            or manifest.get("rotation_observed") or manifest.get("producer_closed")
            or Path(manifest.get("data_directory", "")).resolve() != data.resolve()):
        raise ValueError("only an unchanged live-prefix copy may be released")
    targets, names = [], set()
    for row in manifest.get("files", []):
        name = row.get("snapshot_name")
        if name != "l7_flow_log" or name != row.get("source_name") or name in names:
            raise ValueError("prefix release has an unexpected or duplicate filename")
        names.add(name)
        target, source = out / name, data / name
        if target.is_symlink() or source.is_symlink():
            raise ValueError("prefix release refuses symlinks")
        before, original = target.lstat(), source.lstat()
        length = row.get("copied_bytes")
        if (not stat.S_ISREG(before.st_mode) or not stat.S_ISREG(original.st_mode)
                or type(length) is not int or length < 0 or before.st_size != length or before.st_nlink != 1
                or original.st_size < length or (before.st_dev, before.st_ino) == (original.st_dev, original.st_ino)
                or _sha256(target) != row.get("copied_sha256")
                or _sha256(source, length) != row.get("copied_sha256")):
            raise ValueError("prefix release cannot verify both retained copies")
        targets.append((target, before))
    if {item.name for item in out.iterdir()} != names | {"snapshot.json"}:
        raise ValueError("prefix release directory has unexpected entries")
    # Check the complete census and all identities before the first unlink.
    for target, before in targets:
        current = target.lstat()
        if (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) != (
                before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns):
            raise ValueError("prefix copy changed before release")
    verification_seconds = (time.monotonic_ns() - started) / 1e9
    removed = 0
    for target, before in targets:
        target.unlink()
        removed += before.st_size
    manifest_path.unlink()
    out.rmdir()
    return {"schema": "deepflow-verified-prefix-copy-release-v5", "status": "released_verified_prefix_copy",
            "original_manifest_sha256": manifest_sha256, "snapshot_directory": str(out),
            "files_removed": len(targets), "logical_bytes_unlinked": removed,
            "live_source_paths_retained": True, "parent_import_verified_by_caller": True,
            "free_bytes_before": free_before, "free_bytes_after": shutil.disk_usage(data).free,
            "verification_seconds": verification_seconds,
            "elapsed_seconds": (time.monotonic_ns() - started) / 1e9,
            "limit": "Only imported guest prefix duplicates; concurrent producer activity affects free-space delta."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("prefix", "failure", "final"), required=True)
    parser.add_argument("--producer-closed", action="store_true")
    parser.add_argument("--release-verified-prefix", action="store_true")
    parser.add_argument("--imported-manifest-sha256")
    args = parser.parse_args()
    if args.release_verified_prefix:
        if args.mode != "prefix" or args.producer_closed or not args.imported_manifest_sha256:
            raise ValueError("prefix release requires the imported prefix manifest digest")
        print(json.dumps(release_verified_prefix(args.data, args.out, args.imported_manifest_sha256), sort_keys=True))
    else:
        if args.imported_manifest_sha256 is not None:
            raise ValueError("imported manifest digest is only valid for prefix release")
        snapshot(args.data, args.out, args.mode, producer_closed=args.producer_closed)


if __name__ == "__main__":
    main()
