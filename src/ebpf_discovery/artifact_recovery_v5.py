"""Exact saved-member recovery for historical iteration-5 compact artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
from typing import Any
import zipfile


PROOF_NAME = "declared-file-recovery.json"


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _safe_name(name: str) -> bool:
    parts = PurePosixPath(name).parts
    return bool(name and "\\" not in name and not PurePosixPath(name).is_absolute()
                and ".." not in parts)


def missing_declared_files(folder: Path) -> list[dict[str, str]]:
    manifest_path = folder / "evaluation-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hashes = manifest.get("files_sha256")
    if not isinstance(hashes, dict):
        raise ValueError("saved v5 summary lacks file hashes")
    missing = []
    for name, expected in hashes.items():
        if expected is None:
            continue
        if (not isinstance(name, str) or not _safe_name(name)
                or not isinstance(expected, str) or len(expected) != 64
                or any(character not in "0123456789abcdef" for character in expected)):
            raise ValueError(f"invalid manifest file claim: {name!r}")
        target = folder / PurePosixPath(name)
        if not target.is_file():
            missing.append({"name": name, "manifest_sha256": expected})
    return missing


def retain_unavailable(
    folder: Path, missing: list[dict[str, str]], source: dict[str, Any],
    status: str, detail: str | None = None,
) -> dict[str, Any]:
    proof = {
        "schema_version": "v5-declared-file-recovery",
        "status": status,
        "source": source,
        "requested_files": missing,
        "recovered_files": [],
        "detail": detail,
        "original_compact_unchanged": True,
        "empirical_recomputation_performed": False,
    }
    (folder / PROOF_NAME).write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return proof


def recover_declared_files(
    folder: Path, full_archive: Path, source: dict[str, Any],
) -> dict[str, Any]:
    """Recover only absent manifest-declared members from one exact full ZIP."""
    missing = missing_declared_files(folder)
    if not missing:
        return retain_unavailable(folder, [], source, "not_required")
    expected_digest = source.get("full_artifact_digest")
    computed_digest = "sha256:" + _sha256(full_archive)
    archive_proof = {
        "path": str(full_archive),
        "expected_digest": expected_digest,
        "computed_digest": computed_digest,
        "received_bytes": full_archive.stat().st_size,
    }
    proof_source = {**source, "full_zip_verification": archive_proof}
    if not isinstance(expected_digest, str) or computed_digest != expected_digest:
        return retain_unavailable(
            folder, missing, proof_source, "full_zip_digest_mismatch"
        )
    expected_size = source.get("full_artifact_size_in_bytes")
    if (type(expected_size) is int and expected_size >= 0
            and archive_proof["received_bytes"] != expected_size):
        return retain_unavailable(
            folder, missing, proof_source, "full_zip_size_mismatch"
        )
    try:
        with zipfile.ZipFile(full_archive) as bundle:
            members = bundle.infolist()
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                return retain_unavailable(
                    folder, missing, proof_source, "full_zip_duplicate_members"
                )
            for member in members:
                if (not _safe_name(member.filename)
                        or stat.S_ISLNK(member.external_attr >> 16)):
                    return retain_unavailable(
                        folder, missing, proof_source, "full_zip_unsafe_member",
                        member.filename,
                    )
            by_name = {member.filename: member for member in members}
            verified: list[tuple[dict[str, str], zipfile.ZipInfo, bytes]] = []
            for request in missing:
                member = by_name.get(request["name"])
                if member is None or member.is_dir():
                    return retain_unavailable(
                        folder, missing, proof_source, "declared_member_missing_from_full",
                        request["name"],
                    )
                raw = bundle.read(member)  # also verifies the member CRC
                actual = hashlib.sha256(raw).hexdigest()
                if actual != request["manifest_sha256"]:
                    return retain_unavailable(
                        folder, missing, proof_source,
                        "declared_member_manifest_hash_mismatch", request["name"],
                    )
                verified.append((request, member, raw))
    except (OSError, zipfile.BadZipFile) as exc:
        return retain_unavailable(
            folder, missing, proof_source, "full_zip_unreadable",
            f"{type(exc).__name__}:{exc}",
        )

    recovered = []
    for request, member, raw in verified:
        target = folder / PurePosixPath(request["name"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        recovered.append({
            **request,
            "copied_sha256": hashlib.sha256(raw).hexdigest(),
            "copied_bytes": len(raw),
            "zip_member_crc32": f"{member.CRC:08x}",
            "zip_member_file_size": member.file_size,
            "zip_member_compress_size": member.compress_size,
            "zip_member_name": member.filename,
            "lineage": "direct_full_artifact_zip_member",
        })
    proof = {
        "schema_version": "v5-declared-file-recovery",
        "status": "recovered",
        "source": proof_source,
        "requested_files": missing,
        "recovered_files": recovered,
        "detail": None,
        "nested_retention_transport_traversed": False,
        "original_compact_unchanged": True,
        "empirical_recomputation_performed": False,
    }
    (folder / PROOF_NAME).write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return proof
