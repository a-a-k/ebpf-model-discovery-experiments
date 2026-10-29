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


def snapshot(data: Path, out: Path, mode: str) -> dict:
    data, out = Path(data), Path(out)
    if out.exists():
        raise FileExistsError(f"snapshot output already exists: {out}")
    out.mkdir(parents=True)
    files = []
    for path in sorted(item for item in data.iterdir() if item.is_file()):
        if mode == "prefix" and path.name not in {"l7_flow_log", "l7_flow_log.pre"}:
            continue
        before = path.stat().st_size
        prefix = _complete_prefix(path, before) if path.name.startswith("l7_flow_log") else before
        copied = prefix if mode == "prefix" else before
        target = out / path.name
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
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("prefix", "failure", "final"), required=True)
    args = parser.parse_args()
    snapshot(args.data, args.out, args.mode)


if __name__ == "__main__":
    main()
