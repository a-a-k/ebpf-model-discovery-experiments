"""Bounded, byte-verifying extraction for iteration-5 compact artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import time
from typing import Any
import zipfile


PROOF_SCHEMA = "v5-compact-stream-verification"
SKIPPED_MEMBER = "attempt-journal.jsonl"


def _safe_name(name: str) -> bool:
    parts = PurePosixPath(name).parts
    return bool(name and "\\" not in name and not PurePosixPath(name).is_absolute()
                and ".." not in parts)


def _file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def extract_verified_compact(
    archive: Path, destination: Path, *, expected_digest: str,
    expected_bytes: int | None = None,
) -> dict[str, Any]:
    """Verify one whole ZIP and every member while omitting only the large journal."""
    started = time.monotonic()
    received_bytes = archive.stat().st_size
    computed_digest = "sha256:" + _file_sha256(archive)
    if computed_digest != expected_digest:
        raise ValueError("compact ZIP API digest mismatch")
    if expected_bytes is not None and received_bytes != expected_bytes:
        raise ValueError("compact ZIP API size mismatch")

    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    try:
        with zipfile.ZipFile(archive) as bundle:
            members = bundle.infolist()
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                raise ValueError("duplicate compact ZIP member")
            for member in members:
                if (not _safe_name(member.filename)
                        or stat.S_ISLNK(member.external_attr >> 16)):
                    raise ValueError(f"unsafe compact ZIP member: {member.filename!r}")
            manifest_members = [member for member in members
                                if member.filename == "evaluation-manifest.json"]
            if len(manifest_members) != 1:
                raise ValueError("compact ZIP lacks one evaluation manifest")
            manifest_raw = bundle.read(manifest_members[0])
            manifest = json.loads(manifest_raw)
            claims = manifest.get("files_sha256") if isinstance(manifest, dict) else None
            if not isinstance(claims, dict):
                raise ValueError("compact evaluation manifest lacks file hashes")

            rows = []
            actual_by_name: dict[str, str] = {}
            for member in members:
                if member.is_dir():
                    digest, size = hashlib.sha256(), 0
                    with bundle.open(member) as source:
                        while True:
                            chunk = source.read(1024 * 1024)
                            if not chunk:
                                break
                            digest.update(chunk)
                            size += len(chunk)
                    if size != member.file_size or size != 0:
                        raise ValueError(
                            f"compact directory member carries data: {member.filename}"
                        )
                    (destination / PurePosixPath(member.filename)).mkdir(
                        parents=True, exist_ok=True)
                    empty = digest.hexdigest()
                    actual_by_name[member.filename] = empty
                    rows.append({
                        "name": member.filename, "sha256": empty, "bytes": 0,
                        "crc32": f"{member.CRC:08x}",
                        "compressed_bytes": member.compress_size,
                        "materialized": True, "directory": True,
                        "disposition": "verified_directory_entry",
                    })
                    continue
                materialized = member.filename != SKIPPED_MEMBER
                target = destination / PurePosixPath(member.filename)
                temporary = target.with_name(target.name + ".partial")
                if materialized:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    output = temporary.open("wb")
                else:
                    output = None
                digest = hashlib.sha256()
                size = 0
                try:
                    with bundle.open(member) as source:
                        while True:
                            chunk = source.read(1024 * 1024)
                            if not chunk:
                                break
                            digest.update(chunk)
                            size += len(chunk)
                            if output is not None:
                                output.write(chunk)
                finally:
                    if output is not None:
                        output.close()
                if size != member.file_size:
                    raise ValueError(f"compact member size mismatch: {member.filename}")
                actual = digest.hexdigest()
                actual_by_name[member.filename] = actual
                if materialized:
                    temporary.replace(target)
                    written.append(target)
                rows.append({
                    "name": member.filename,
                    "sha256": actual,
                    "bytes": size,
                    "crc32": f"{member.CRC:08x}",
                    "compressed_bytes": member.compress_size,
                    "materialized": materialized,
                    "directory": False,
                    "disposition": (
                        "extracted_verified_member" if materialized else
                        "retained_actions_stream_verification_evidence"
                    ),
                })

            for name, expected in claims.items():
                if expected is None:
                    if name in actual_by_name:
                        raise ValueError(f"unexpected unhashed compact member: {name}")
                    continue
                if (not isinstance(name, str) or not _safe_name(name)
                        or not isinstance(expected, str) or len(expected) != 64):
                    raise ValueError(f"invalid compact manifest hash claim: {name!r}")
                actual = actual_by_name.get(name)
                if actual is not None and actual != expected:
                    raise ValueError(f"compact member manifest hash mismatch: {name}")
    except Exception:
        for target in written:
            target.unlink(missing_ok=True)
        for target in destination.rglob("*.partial"):
            target.unlink(missing_ok=True)
        raise

    journal = next((row for row in rows if row["name"] == SKIPPED_MEMBER), None)
    if journal is not None and claims.get(SKIPPED_MEMBER) != journal["sha256"]:
        raise ValueError("skipped compact journal lacks an exact manifest hash")
    return {
        "schema_version": PROOF_SCHEMA,
        "expected_sha256": expected_digest,
        "computed_sha256": computed_digest,
        "received_bytes": received_bytes,
        "member_count": len(rows),
        "safe_extract": True,
        "members": rows,
        "manifest_member_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "skipped_member": journal,
        "verification_elapsed_seconds": time.monotonic() - started,
        "working_copy_disposition": "pending_verified_working_copy_removal",
    }


def remove_verified_working_copy(archive: Path, proof: dict[str, Any]) -> None:
    """Remove only a helper-verified download and make that disposition explicit."""
    if (proof.get("schema_version") != PROOF_SCHEMA
            or proof.get("computed_sha256") != proof.get("expected_sha256")
            or proof.get("safe_extract") is not True):
        raise ValueError("refusing to remove an unverified compact working copy")
    archive.unlink()
    if archive.exists():
        raise OSError("verified compact working copy remains after removal")
    proof["working_copy_disposition"] = "verified_then_removed_working_copy"
    proof["retained_path"] = None


def verified_nonmaterialized_files(
    proof: Any, manifest_path: Path, expected_artifact_digest: str,
) -> set[str]:
    """Return exact manifest claims represented by retained stream evidence."""
    if (not isinstance(proof, dict) or proof.get("schema_version") != PROOF_SCHEMA
            or proof.get("expected_sha256") != expected_artifact_digest
            or proof.get("computed_sha256") != expected_artifact_digest
            or proof.get("safe_extract") is not True
            or proof.get("working_copy_disposition")
            != "verified_then_removed_working_copy"
            or proof.get("retained_path") is not None
            or not isinstance(proof.get("verification_elapsed_seconds"), (int, float))
            or proof["verification_elapsed_seconds"] < 0):
        raise ValueError("invalid compact stream verification proof")
    members = proof.get("members")
    if (not isinstance(members, list) or proof.get("member_count") != len(members)):
        raise ValueError("invalid compact stream member proof")
    names = [row.get("name") for row in members if isinstance(row, dict)]
    if len(names) != len(members) or len(names) != len(set(names)):
        raise ValueError("invalid compact stream member proof")
    for row in members:
        if (not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64
                or not isinstance(row.get("crc32"), str) or len(row["crc32"]) != 8
                or type(row.get("bytes")) is not int or row["bytes"] < 0
                or type(row.get("compressed_bytes")) is not int
                or row["compressed_bytes"] < 0):
            raise ValueError("invalid compact stream member proof")
        if row.get("materialized") is True:
            expected_disposition = (
                "verified_directory_entry" if row.get("directory") is True
                else "extracted_verified_member"
            )
            if row.get("disposition") != expected_disposition:
                raise ValueError("invalid compact stream member disposition")
        elif row.get("materialized") is not False:
            raise ValueError("invalid compact stream member disposition")
    if proof.get("manifest_member_sha256") != _file_sha256(manifest_path):
        raise ValueError("compact stream manifest proof mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    claims = manifest.get("files_sha256") if isinstance(manifest, dict) else None
    if not isinstance(claims, dict):
        raise ValueError("compact evaluation manifest lacks file hashes")
    skipped = [row for row in members if row.get("materialized") is False]
    if len(skipped) > 1:
        raise ValueError("compact stream proof omits multiple members")
    if not skipped:
        return set()
    row = skipped[0]
    expected = claims.get(SKIPPED_MEMBER)
    if (row.get("name") != SKIPPED_MEMBER
            or row.get("disposition") != "retained_actions_stream_verification_evidence"
            or not isinstance(expected, str) or row.get("sha256") != expected
            ):
        raise ValueError("invalid skipped compact journal proof")
    if proof.get("skipped_member") != row:
        raise ValueError("skipped compact journal proof mismatch")
    return {SKIPPED_MEMBER}
