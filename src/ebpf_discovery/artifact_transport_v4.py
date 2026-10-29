"""Lossless, typed transport for large v4 output trees.

This changes delivery only. The source tree is never removed or rewritten.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import time
import uuid

try:
    import resource
except ImportError:  # Windows unit fixtures; Actions execution is Linux.
    resource = None

from . import diagnostic_artifacts_v4


SCHEMA = "v4-lossless-artifact-transport"
KINDS = ("worker", "toolchain", "handoff")
ARCHIVE = "payload.tar.gz"
MANIFEST = "payload.manifest.jsonl"
MARKER = "transport.json"
STATUS = "package-status.json"


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _usage():
    return resource.getrusage(resource.RUSAGE_SELF) if resource is not None else None


def _safe_name(name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise ValueError("invalid archive member path")
    pure = PurePosixPath(name)
    if pure.is_absolute() or any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("archive member escapes destination")
    return Path(*pure.parts)


def package(source: Path, destination: Path, *, kind: str) -> dict:
    if kind not in KINDS:
        raise ValueError("unsupported transport kind")
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_dir() or source == destination or source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError("source and package must be separate trees")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("package destination must be fresh")
    destination.mkdir(parents=True, exist_ok=True)
    status = {"schema_version": SCHEMA, "kind": kind, "status": "started",
              "started_ns": time.time_ns(), "source": str(source), "source_unchanged": None}
    _write(destination / STATUS, status)
    started = time.monotonic()
    usage_before = _usage()
    failed = False
    try:
        # The diagnostic packager performs a second, streaming archive pass,
        # verifies every original file against its archived digest and drains
        # gzip through its CRC trailer. Its original tree remains untouched.
        intermediate = destination / "_diagnostic"
        proof = diagnostic_artifacts_v4.package(source, intermediate)
        os.replace(intermediate / "diagnostic-output.tar.gz", destination / ARCHIVE)
        os.replace(intermediate / "output-manifest.jsonl", destination / MANIFEST)
        os.replace(intermediate / "packaging.json", destination / "packaging.json")
        intermediate.rmdir()
        proof.update(archive_file=ARCHIVE, manifest_file=MANIFEST)
        _write(destination / "packaging.json", proof)
        marker = {"schema_version": SCHEMA, "kind": kind,
                  "archive": ARCHIVE, "archive_bytes": (destination / ARCHIVE).stat().st_size,
                  "archive_sha256": _sha(destination / ARCHIVE),
                  "manifest": MANIFEST, "manifest_bytes": (destination / MANIFEST).stat().st_size,
                  "manifest_sha256": _sha(destination / MANIFEST),
                  "files": proof["files"], "directories": proof["directories"],
                  "uncompressed_file_bytes": proof["uncompressed_file_bytes"],
                  "original_tree_verified": proof["exact_paths_bytes_and_current_source_verified"],
                  "gzip_crc_verified": proof["gzip_crc_verified"]}
        _write(destination / MARKER, marker)
        status.update(status="complete", source_unchanged=True,
                      marker_sha256=_sha(destination / MARKER),
                      files=marker["files"], directories=marker["directories"],
                      uncompressed_file_bytes=marker["uncompressed_file_bytes"])
        return marker
    except BaseException as error:
        failed = True
        status.update(status="packaging_failed", error=repr(error))
        intermediate = destination / "_diagnostic"
        if (intermediate / "packaging.json").is_file():
            try:
                shutil.copy2(intermediate / "packaging.json", destination / "packaging.json")
            except OSError as retention_error:
                status["packaging_proof_copy_error"] = repr(retention_error)
        shutil.rmtree(intermediate, ignore_errors=True)
        for name in (ARCHIVE, MANIFEST, MARKER):
            try:
                (destination / name).unlink(missing_ok=True)
            except OSError as cleanup_error:
                status.setdefault("partial_package_cleanup_errors", []).append(repr(cleanup_error))
        raise
    finally:
        status.update(ended_ns=time.time_ns(), elapsed_seconds=time.monotonic() - started)
        usage_after = _usage()
        if usage_before is not None and usage_after is not None:
            status.update(user_cpu_seconds=usage_after.ru_utime - usage_before.ru_utime,
                          system_cpu_seconds=usage_after.ru_stime - usage_before.ru_stime,
                          peak_rss_kib=usage_after.ru_maxrss)
        try:
            print("ARTIFACT_PACKAGING " + json.dumps(status, sort_keys=True), flush=True)
        except OSError:
            pass
        try:
            _write(destination / STATUS, status)
        except OSError as status_error:
            if not failed:
                raise
            try:
                print("ARTIFACT_PACKAGING_STATUS_WRITE_ERROR " + repr(status_error), flush=True)
            except OSError:
                pass


def unpack(package_dir: Path, destination: Path, *, kind: str) -> dict:
    """Verify and stage a package, then publish one complete extracted tree."""
    if kind not in KINDS:
        raise ValueError("unsupported transport kind")
    package_dir, destination = Path(package_dir).resolve(), Path(destination).resolve()
    if destination.exists():
        raise ValueError("extraction destination must be absent")
    if not package_dir.is_dir() or destination.is_relative_to(package_dir) or package_dir.is_relative_to(destination):
        raise ValueError("package and extraction destination must be separate")
    if {p.name for p in package_dir.iterdir()} != {ARCHIVE, MANIFEST, MARKER, STATUS, "packaging.json"}:
        raise ValueError("unexpected package layout")
    for path in package_dir.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ValueError("package contains redirected or non-file member")
    marker = json.loads((package_dir / MARKER).read_text(encoding="utf-8"))
    status = json.loads((package_dir / STATUS).read_text(encoding="utf-8"))
    packaging = json.loads((package_dir / "packaging.json").read_text(encoding="utf-8"))
    if (marker.get("schema_version") != SCHEMA or marker.get("kind") != kind
            or status.get("schema_version") != SCHEMA or status.get("kind") != kind
            or status.get("status") != "complete"
            or status.get("marker_sha256") != _sha(package_dir / MARKER)
            or marker.get("original_tree_verified") is not True
            or marker.get("gzip_crc_verified") is not True
            or marker.get("archive") != ARCHIVE or marker.get("manifest") != MANIFEST):
        raise ValueError("package marker or status invalid")
    if (packaging.get("schema_version") != "v4-lossless-diagnostic-package"
            or packaging.get("status") != "complete"
            or packaging.get("source_deleted_or_trimmed") is not False
            or packaging.get("exact_paths_bytes_and_current_source_verified") is not True
            or packaging.get("gzip_crc_verified") is not True
            or packaging.get("archive_file") != ARCHIVE
            or packaging.get("manifest_file") != MANIFEST
            or any(packaging.get(key) != marker.get(key) for key in
                   ("files", "directories", "uncompressed_file_bytes", "archive_bytes",
                    "archive_sha256", "manifest_sha256"))):
        raise ValueError("packaging proof differs from typed transport marker")
    for name, key in ((ARCHIVE, "archive"), (MANIFEST, "manifest")):
        path = package_dir / name
        if path.stat().st_size != marker.get(key + "_bytes") or _sha(path) != marker.get(key + "_sha256"):
            raise ValueError("transport payload differs from marker")
    stage = destination.with_name(destination.name + ".staging-" + str(uuid.uuid4()).replace("-", ""))
    stage.mkdir(parents=True)
    started = time.monotonic()
    usage_before = _usage()
    count = {"files": 0, "directories": 0, "uncompressed_file_bytes": 0}
    seen = set()
    directory_modes = []
    try:
        with (package_dir / MANIFEST).open(encoding="utf-8") as rows, gzip.open(package_dir / ARCHIVE, "rb") as wire:
            with tarfile.open(fileobj=wire, mode="r|") as archive:
                for member in archive:
                    line = rows.readline()
                    if not line:
                        raise ValueError("unmanifested archive member")
                    row = json.loads(line)
                    if not isinstance(row, dict) or set(row) != {"path", "type", "mode", "bytes"} | ({"sha256"} if row.get("type") == "file" else set()):
                        raise ValueError("invalid manifest record")
                    relative = _safe_name(row["path"])
                    if row["path"] != member.name or row["path"] in seen:
                        raise ValueError("duplicate or mismatched archive member")
                    seen.add(row["path"])
                    if (type(row["mode"]) is not int or row["mode"] < 0 or row["mode"] > 0o7777
                            or type(row["bytes"]) is not int or row["bytes"] < 0
                            or member.mode != row["mode"] or member.size != row["bytes"]):
                        raise ValueError("archive metadata differs from manifest")
                    target = stage / relative
                    if not target.resolve().is_relative_to(stage):
                        raise ValueError("archive member escapes extraction stage")
                    if not target.parent.is_dir() or target.parent.is_symlink():
                        raise ValueError("archive parent directory missing or redirected")
                    if row["type"] == "directory" and member.isdir():
                        target.mkdir()
                        directory_modes.append((target, row["mode"]))
                        count["directories"] += 1
                    elif row["type"] == "file" and member.isfile():
                        if len(row["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in row["sha256"]):
                            raise ValueError("invalid file digest")
                        digest = hashlib.sha256()
                        source = archive.extractfile(member)
                        if source is None:
                            raise ValueError("archive file missing")
                        size = 0
                        with target.open("xb") as output:
                            while chunk := source.read(1024 * 1024):
                                digest.update(chunk)
                                output.write(chunk)
                                size += len(chunk)
                        if size != row["bytes"] or digest.hexdigest() != row["sha256"]:
                            raise ValueError("archive file differs from manifest")
                        target.chmod(row["mode"])
                        count["files"] += 1
                        count["uncompressed_file_bytes"] += size
                    else:
                        raise ValueError("unsupported archive member type")
                    archive.members.clear()
                if rows.readline():
                    raise ValueError("archive omitted manifested member")
            while wire.read(1024 * 1024):
                pass  # Validate gzip trailer and CRC after tar end markers.
        if any(count[key] != marker.get(key) or count[key] != status.get(key) for key in count):
            raise ValueError("extracted counts differ from package proof")
        for target, mode in reversed(directory_modes):
            target.chmod(mode)
        os.replace(stage, destination)
        usage_after = _usage()
        costs = {}
        if usage_before is not None and usage_after is not None:
            costs = {"user_cpu_seconds": usage_after.ru_utime - usage_before.ru_utime,
                     "system_cpu_seconds": usage_after.ru_stime - usage_before.ru_stime,
                     "peak_rss_kib": usage_after.ru_maxrss}
        return {"schema_version": SCHEMA, "kind": kind, **count, **costs,
                "archive_sha256": marker["archive_sha256"],
                "manifest_sha256": marker["manifest_sha256"],
                "elapsed_seconds": time.monotonic() - started}
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("package", "unpack"))
    parser.add_argument("--source", type=Path)
    parser.add_argument("--package", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--kind", required=True, choices=KINDS)
    args = parser.parse_args()
    if args.operation == "package":
        if args.source is None or args.package is not None:
            parser.error("package requires --source only")
        result = package(args.source, args.out, kind=args.kind)
    else:
        if args.package is None or args.source is not None:
            parser.error("unpack requires --package only")
        result = unpack(args.package, args.out, kind=args.kind)
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
