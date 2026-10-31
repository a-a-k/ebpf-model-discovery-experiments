"""Saved-artifact-only reporting for the fixed iteration-5 collector matrix.

The reporter validates and copies evaluations produced by the source campaign.
It never invokes acquisition, fitting, graph discovery, simulation, or scoring.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any
import zlib

from .compact_transport_v5 import PROOF_SCHEMA, verified_nonmaterialized_files


COLLECTORS = ("obi", "deepflow", "coroot")
SYSTEMS = ("deathstarbench", "otel_demo", "petclinic")
MODES = ("absent", "partial", "full")
SEEDS = (6, 7, 8)
STAGES = ("smoke", "main")
EXPECTED_MAIN = {
    (collector, system, mode, seed)
    for collector in COLLECTORS
    for system in SYSTEMS
    for mode in MODES
    for seed in SEEDS
}
SOURCE_PINS = {
    "obi": {
        "source_version": "v0.15.2",
        "source_commit": None,
        "image": "otel/ebpf-instrument:v0.15.2@sha256:101b5c773ac84545cac007ce3dbaf38bfb0e7091f26e813c08d649f35dca253e",
    },
    "deepflow": {
        "source_version": "v7.2.3",
        "source_commit": "9a1219fa5cf1471ba2ec8742019661567d98002e",
        "image": "deepflowce/deepflow-agent:v7.2.3@sha256:5f72c0996fdb5008fdb8fd0524f427a895fc54c61690b26ba2cae648929ea95a",
    },
    "coroot": {
        "source_version": "1.37.0",
        "source_commit": "89a858a0ee35c4eb938b86d56f23168fb0ac7573",
        "image": "ghcr.io/coroot/coroot-node-agent:1.37.0@sha256:f360c31c5e2fa75550c0029f3c02a0e54b83831bae59201b9fe76bab2fe564b4",
    },
}

LEGACY_AGGREGATE_SCHEMA = "evaluation-v5-saved-aggregate"
REFERENCED_AGGREGATE_SCHEMA = "evaluation-v5-saved-aggregate-referenced-v1"
EVALUATION_REFERENCE_SCHEMA = "evaluation-v5-source-evaluation-reference-v1"
PAYLOAD_MANIFEST_SCHEMA = "evaluation-v5-payload-manifest-v1"


def _read(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _stream_digest(stream) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


def _evaluation_projection(evaluation: dict[str, Any]) -> dict[str, Any]:
    """Retain only exact fields consumed by render; the reference is lossless."""
    status = evaluation.get("status") or {}
    acquisition = evaluation.get("acquisition") or {}
    cost = evaluation.get("cost") or {}
    manual = cost.get("manual_preparation") or {}
    rows = []
    row_keys = (
        "operation", "source", "variant", "available", "prediction",
        "point_prediction", "forecast_interval", "actual_target_success_counts",
        "actual_counts", "reason", "unknown_obligations", "database_unknown_reason",
        "database_fault_unknown", "assumed_satisfied_database_requirements",
    )
    for row in evaluation.get("evaluations") or []:
        rows.append({key: row[key] for key in row_keys if key in row})
    projection = {
        "status": {"status": status.get("status")},
        "smoke_technical_pass": evaluation.get("smoke_technical_pass"),
        "acquisition": {
            "valid": acquisition.get("valid"),
            "problems": acquisition.get("problems"),
        },
        "evaluations": rows,
        "cost": {
            "campaign_elapsed_seconds": cost.get("campaign_elapsed_seconds"),
            "toolchain_build_seconds": cost.get("toolchain_build_seconds"),
            "toolchain_command_seconds": cost.get("toolchain_command_seconds"),
            "manual_preparation": {
                "measured": manual.get("measured"),
                "reason": manual.get("reason"),
            },
        },
    }
    if "scientific_summaries" in evaluation:
        projection["scientific_summaries"] = evaluation["scientific_summaries"]
    encoded = json.dumps(
        projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return {**projection, "projection_sha256": hashlib.sha256(encoded).hexdigest()}


def _retain_evaluation_payload(
    source: Path, report_dir: Path, *, artifact_id: int, run_id: int,
    head_sha: str, expected_sha256: str,
) -> dict[str, Any]:
    payload_dir = report_dir / "evaluation-payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    target = payload_dir / f"{artifact_id}.evaluation-v5.json.gz"
    temporary = target.with_suffix(target.suffix + ".tmp")
    raw_digest, raw_bytes = hashlib.sha256(), 0
    with source.open("rb") as input_stream, temporary.open("wb") as output_stream:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=output_stream, compresslevel=9, mtime=0,
        ) as packed:
            while chunk := input_stream.read(1024 * 1024):
                raw_digest.update(chunk)
                raw_bytes += len(chunk)
                packed.write(chunk)
    source_sha256 = raw_digest.hexdigest()
    if source_sha256 != expected_sha256:
        temporary.unlink(missing_ok=True)
        raise ValueError(f"evaluation payload source hash changed: {source}")
    os.replace(temporary, target)
    gzip_sha256, gzip_bytes = _digest(target), target.stat().st_size
    with gzip.open(target, "rb") as restored:
        restored_sha256, restored_bytes = _stream_digest(restored)
    if (restored_sha256, restored_bytes) != (source_sha256, raw_bytes):
        raise ValueError(f"evaluation payload does not restore source bytes: {source}")
    return {
        "schema_version": EVALUATION_REFERENCE_SCHEMA,
        "path": target.relative_to(report_dir).as_posix(),
        "encoding": "gzip",
        "deterministic_gzip": {"filename": "", "mtime": 0, "compresslevel": 9},
        "source_member": "evaluation-v5.json",
        "source_sha256": source_sha256,
        "source_bytes": raw_bytes,
        "gzip_sha256": gzip_sha256,
        "gzip_bytes": gzip_bytes,
        "restore_verified": True,
        "exact_original_bytes": True,
        "artifact_id": artifact_id,
        "run_id": run_id,
        "head_sha": head_sha,
    }


def resolve_evaluation_reference(reference: dict[str, Any], aggregate_path: Path) -> dict:
    """Resolve one explicit lossless reference; legacy inline objects never enter here."""
    if (not isinstance(reference, dict)
            or reference.get("schema_version") != EVALUATION_REFERENCE_SCHEMA
            or reference.get("encoding") != "gzip"
            or reference.get("restore_verified") is not True
            or reference.get("exact_original_bytes") is not True):
        raise ValueError("invalid saved evaluation reference")
    root = Path(aggregate_path).resolve().parent
    payload = (root / str(reference.get("path", ""))).resolve()
    try:
        payload.relative_to(root)
    except ValueError as error:
        raise ValueError("saved evaluation reference escapes aggregate directory") from error
    if (not payload.is_file() or _digest(payload) != reference.get("gzip_sha256")
            or payload.stat().st_size != reference.get("gzip_bytes")):
        raise ValueError("saved evaluation payload gzip proof mismatch")
    with tempfile.TemporaryFile(mode="w+b") as restored:
        digest, size = hashlib.sha256(), 0
        with gzip.open(payload, "rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
                restored.write(chunk)
        if (size != reference.get("source_bytes")
                or digest.hexdigest() != reference.get("source_sha256")):
            raise ValueError("saved evaluation payload source proof mismatch")
        restored.seek(0)
        value = json.load(restored)
    if not isinstance(value, dict) or value.get("schema_version") != "evaluation-v5":
        raise ValueError("saved evaluation payload has wrong schema")
    return value


def _cell(row: dict[str, Any]) -> tuple[str, str, str, int]:
    value = (row.get("collector"), row.get("system"), row.get("mode"), row.get("seed"))
    if (value[0] not in COLLECTORS or value[1] not in SYSTEMS
            or value[2] not in MODES or value[3] not in SEEDS):
        raise ValueError(f"invalid v5 cell identity: {value}")
    return value  # type: ignore[return-value]


def _declarations(path: Path) -> tuple[dict[str, Any], dict[tuple[int, tuple], dict]]:
    value = _read(path)
    if not isinstance(value, dict) or value.get("schema_version") != "v5-report-declarations":
        raise ValueError("v5 report declarations have the wrong schema")
    if 'experiment_head' in value and (not isinstance(value['experiment_head'], str)
            or len(value['experiment_head']) != 40
            or any(ch not in '0123456789abcdef' for ch in value['experiment_head'])):
        raise ValueError('declared experiment_head must be a full lowercase 40-character commit SHA')
    attempts: dict[tuple[int, tuple], dict] = {}
    run_ids: set[int] = set()
    for run in value.get("attempt_runs") or []:
        repository = run.get("repository")
        if repository is not None and (
            not isinstance(repository, str) or repository.count("/") != 1
            or any(not part for part in repository.split("/"))
        ):
            raise ValueError(f"invalid attempt repository: {repository}")
        run_id = run.get("run_id")
        if type(run_id) is not int or run_id <= 0 or run_id in run_ids:
            raise ValueError("attempt run IDs must be unique positive integers")
        run_ids.add(run_id)
        collector, stage = run.get("collector"), run.get("stage")
        if collector not in COLLECTORS or stage not in STAGES:
            raise ValueError(f"invalid attempt declaration: {run}")
        cells = run.get("cells")
        if not isinstance(cells, list) or not cells:
            raise ValueError("each attempt run must declare at least one cell")
        for raw in cells:
            declared = {**raw, "collector": collector}
            identity = _cell(declared)
            if stage == "smoke" and identity[3] != 6:
                raise ValueError("smoke declarations are fixed to seed 6")
            key = (run_id, identity)
            if key in attempts:
                raise ValueError(f"duplicate declared attempt cell: {key}")
            attempts[key] = {
                "run_id": run_id, "collector": collector, "stage": stage,
                "system": identity[1], "mode": identity[2], "seed": identity[3],
                "repository": repository, "note": run.get("note"),
            }
    related_ids = set()
    roles = {"preparation", "product_ci", "worker", "wait", "report", "archive", "evidence"}
    for run in value.get("related_runs") or []:
        run_id = run.get("run_id")
        repository = run.get("repository")
        if (type(run_id) is not int or run_id <= 0 or run_id in run_ids
                or run_id in related_ids or run.get("role") not in roles
                or not isinstance(run.get("note"), str)
                or (repository is not None and (
                    not isinstance(repository, str) or repository.count("/") != 1
                    or any(not part for part in repository.split("/"))))):
            raise ValueError(f"invalid related run declaration: {run}")
        related_ids.add(run_id)
    blocked = set()
    for row in value.get("blocked_main_cells") or []:
        identity = _cell(row)
        if identity in blocked or not isinstance(row.get("reason"), str):
            raise ValueError(f"invalid blocked cell declaration: {row}")
        blocked.add(identity)
    return value, attempts


def _validate_source(folder: Path, evaluation: dict, collector: str) -> dict[str, Any]:
    path = folder / "observations" / "collector.json"
    retained = _read(path)
    if not isinstance(retained, dict):
        raise ValueError(f"saved v5 summary lacks collector provenance: {path}")
    expected = SOURCE_PINS[collector]
    for key, wanted in expected.items():
        if retained.get(key) != wanted:
            raise ValueError(f"saved collector source pin mismatch: {path}: {key}")
    acquisition = evaluation.get("acquisition") or {}
    provenance = acquisition.get("provenance") or {}
    if (retained.get("collector") != collector or provenance.get("collector") != collector
            or provenance.get("source_domain") != retained.get("source_domain")):
        raise ValueError(f"saved collector provenance mismatch: {path}")
    drain = acquisition.get("final_drain") or {}
    control = acquisition.get("positive_control") or {}
    if (drain.get("collector") != collector or control.get("collector") != collector
            or drain.get("source_version") != retained.get("source_version")):
        raise ValueError(f"saved collector technical provenance mismatch: {path}")
    return {
        "path": "observations/collector.json", "sha256": _digest(path),
        **{key: retained.get(key) for key in
           ("collector", "source_domain", "source_version", "source_commit", "image")},
    }


def _saved_summaries(
    roots: list[Path], declarations: dict[tuple[int, tuple], dict], report_dir: Path,
) -> list[dict]:
    folders = set()
    for root in roots:
        folders.update(path.parent.resolve() for path in Path(root).rglob("evaluation-manifest.json"))
    reports = []
    artifact_ids = set()
    for folder in sorted(folders):
        manifest = _read(folder / "evaluation-manifest.json")
        artifact = _read(folder / "artifact-provenance.json")
        if not isinstance(manifest, dict) or manifest.get("schema_version") != "v5-cell-summary-manifest":
            raise ValueError(f"invalid v5 summary manifest: {folder}")
        if not isinstance(artifact, dict) or type(artifact.get("artifact_id")) is not int:
            raise ValueError(f"v5 summary lacks immutable artifact identity: {folder}")
        artifact_id = artifact["artifact_id"]
        if artifact_id in artifact_ids:
            raise ValueError("duplicate v5 summary artifact ID")
        artifact_ids.add(artifact_id)
        stage = "smoke" if manifest.get("smoke") is True else "main"
        identity = _cell(manifest)
        run_id = int(manifest.get("run_id"))
        declaration = declarations.get((run_id, identity))
        if declaration is None or declaration["stage"] != stage:
            raise ValueError(f"saved summary was not declared with the same cell/stage: {folder}")
        artifact_repository = artifact.get("repository")
        if (not isinstance(artifact_repository, str)
                or artifact_repository.count("/") != 1
                or any(not part for part in artifact_repository.split("/"))
                or (declaration.get("repository") is not None
                    and artifact_repository != declaration["repository"])):
            raise ValueError(f"saved v5 artifact repository mismatch: {folder}")
        expected_name = (
            f"v5-summary-{identity[0]}-{stage}-{identity[1]}-{identity[2]}-"
            f"{identity[3]}-{run_id}"
        )
        expected_full = expected_name.replace("v5-summary-", "campaign-v5-", 1)
        if (artifact.get("name") != expected_name or artifact.get("run_id") != run_id
                or artifact.get("head_sha") != manifest.get("commit")
                or artifact.get("full_artifact_name") != expected_full
                or manifest.get("full_artifact_name") != expected_full
                or not artifact.get("digest")):
            raise ValueError(f"saved v5 artifact/run/full provenance mismatch: {folder}")
        zip_proof = artifact.get("compact_zip_verification") or {}
        if (zip_proof.get("expected_sha256") != artifact.get("digest")
                or zip_proof.get("computed_sha256") != artifact.get("digest")
                or zip_proof.get("safe_extract") is not True
                or type(zip_proof.get("received_bytes")) is not int
                or zip_proof.get("received_bytes") <= 0):
            raise ValueError(f"saved compact ZIP was not byte-verified before extraction: {folder}")
        full_available = (
            type(artifact.get("full_artifact_id")) is int
            and bool(artifact.get("full_artifact_digest"))
            and artifact.get("full_artifact_expired") is False
        )
        full_unavailable_reason = (
            None if full_available else
            "full_artifact_expired" if artifact.get("full_artifact_expired") is True else
            "full_artifact_missing" if artifact.get("full_artifact_id") is None else
            "full_artifact_provenance_incomplete"
        )
        recovery_ref = artifact.get("declared_file_recovery")
        recovery = None
        if recovery_ref is not None:
            if (not isinstance(recovery_ref, dict)
                    or recovery_ref.get("path") != "declared-file-recovery.json"
                    or not isinstance(recovery_ref.get("sha256"), str)):
                raise ValueError(f"invalid declared-file recovery reference: {folder}")
            recovery_path = folder / recovery_ref["path"]
            if (not recovery_path.is_file()
                    or _digest(recovery_path) != recovery_ref["sha256"]):
                raise ValueError(f"declared-file recovery proof mismatch: {folder}")
            recovery = _read(recovery_path)
            source = recovery.get("source") if isinstance(recovery, dict) else None
            if (not isinstance(recovery, dict)
                    or recovery.get("schema_version") != "v5-declared-file-recovery"
                    or recovery_ref.get("status") != recovery.get("status")
                    or not isinstance(source, dict)
                    or source.get("repository") != artifact_repository
                    or source.get("run_id") != run_id
                    or source.get("head_sha") != manifest.get("commit")
                    or source.get("compact_artifact_id") != artifact_id
                    or source.get("compact_artifact_name") != artifact.get("name")
                    or source.get("compact_artifact_digest") != artifact.get("digest")
                    or source.get("full_artifact_id") != artifact.get("full_artifact_id")
                    or source.get("full_artifact_name") != artifact.get("full_artifact_name")
                    or source.get("full_artifact_digest") != artifact.get(
                        "full_artifact_digest")):
                raise ValueError(f"invalid declared-file recovery proof: {folder}")
        hashes = manifest.get("files_sha256")
        if not isinstance(hashes, dict):
            raise ValueError(f"saved v5 summary lacks file hashes: {folder}")
        nonmaterialized = set()
        if zip_proof.get("schema_version") == PROOF_SCHEMA:
            nonmaterialized = verified_nonmaterialized_files(
                zip_proof, folder / "evaluation-manifest.json", artifact["digest"]
            )
        missing_declared = []
        for name, expected in hashes.items():
            target = folder / name
            if expected is None:
                if target.is_file():
                    raise ValueError(f"unexpected unhashed compact file: {target}")
            elif not target.is_file():
                if name not in nonmaterialized:
                    missing_declared.append({"name": name, "manifest_sha256": expected})
            elif _digest(target) != expected:
                raise ValueError(f"saved v5 compact hash mismatch: {target}")
        if missing_declared:
            if recovery is not None and (
                recovery.get("requested_files") != missing_declared
                or recovery.get("status") == "recovered"
            ):
                raise ValueError(f"invalid declared-file recovery proof: {folder}")
        elif recovery is not None:
            requested = recovery.get("requested_files")
            recovered = recovery.get("recovered_files")
            full_zip = (recovery.get("source") or {}).get("full_zip_verification")
            source = recovery.get("source") or {}
            full_archive = (
                Path(full_zip.get("path")) if isinstance(full_zip, dict)
                and isinstance(full_zip.get("path"), str) else None
            )
            if (recovery.get("status") != "recovered"
                    or recovery.get("nested_retention_transport_traversed") is not False
                    or not isinstance(requested, list) or not requested
                    or not isinstance(recovered, list) or len(recovered) != len(requested)
                    or not isinstance(full_zip, dict)
                    or full_zip.get("expected_digest") != artifact.get("full_artifact_digest")
                    or full_zip.get("computed_digest") != artifact.get("full_artifact_digest")
                    or type(full_zip.get("received_bytes")) is not int
                    or full_zip.get("received_bytes") <= 0
                    or full_archive is None or not full_archive.is_file()
                    or full_archive.stat().st_size != full_zip.get("received_bytes")
                    or "sha256:" + _digest(full_archive)
                    != full_zip.get("computed_digest")
                    or (type(source.get("full_artifact_size_in_bytes")) is int
                        and source.get("full_artifact_size_in_bytes")
                        != full_zip.get("received_bytes"))):
                raise ValueError(f"invalid successful declared-file recovery: {folder}")
            recovered_by_name = {row.get("name"): row for row in recovered
                                 if isinstance(row, dict)}
            if len(recovered_by_name) != len(recovered):
                raise ValueError(f"invalid successful declared-file recovery: {folder}")
            for request in requested:
                row = recovered_by_name.get(request.get("name")) if isinstance(request, dict) else None
                expected = hashes.get(request.get("name")) if isinstance(request, dict) else None
                target = folder / request.get("name") if isinstance(request, dict) else None
                target_bytes = target.read_bytes() if target is not None and target.is_file() else None
                if (not isinstance(row, dict) or expected != request.get("manifest_sha256")
                        or row.get("copied_sha256") != expected
                        or row.get("zip_member_name") != request.get("name")
                        or row.get("lineage") != "direct_full_artifact_zip_member"
                        or type(row.get("copied_bytes")) is not int
                        or target_bytes is None
                        or row.get("copied_bytes") != len(target_bytes)
                        or row.get("zip_member_file_size") != len(target_bytes)
                        or row.get("zip_member_crc32") != f"{zlib.crc32(target_bytes):08x}"
                        or type(row.get("zip_member_compress_size")) is not int
                        or row.get("zip_member_compress_size") < 0):
                    raise ValueError(f"invalid successful declared-file recovery: {folder}")
        evaluation_path = folder / "evaluation-v5.json"
        evaluation = _read(evaluation_path)
        if evaluation is None:
            reports.append({
                **declaration, "artifact": artifact, "manifest": manifest,
                "root": str(folder), "evaluation_reference": None,
                "evaluation_projection": None,
                "technical_complete_self_reported": False,
                "full_source_artifact_available": full_available,
                "full_source_artifact_reason": full_unavailable_reason,
                "eligible_main_coverage": False,
                "independently_admitted": False,
                "manifest_declared_transport_complete": not missing_declared,
                "missing_manifest_declared_files": missing_declared,
                "verified_nonmaterialized_manifest_files": sorted(nonmaterialized),
                "declared_file_recovery": recovery,
                "reason": "saved_evaluation_missing",
            })
            continue
        if hashes.get("evaluation-v5.json") != _digest(evaluation_path):
            raise ValueError(f"saved evaluation is not hash-bound: {evaluation_path}")
        if evaluation.get("schema_version") != "evaluation-v5":
            raise ValueError(f"invalid saved v5 evaluation schema: {evaluation_path}")
        status = _read(folder / "status.json")
        if not isinstance(status, dict):
            raise ValueError(f"saved v5 evaluation lacks status identity: {evaluation_path}")
        try:
            status_run_id = int(status.get("run_id"))
        except (TypeError, ValueError):
            status_run_id = None
        if (status_run_id != run_id or status.get("commit") != manifest.get("commit")
                or status.get("smoke") is not (stage == "smoke")):
            raise ValueError(f"saved v5 status run/commit/stage mismatch: {evaluation_path}")
        for key, wanted in zip(("collector", "system", "mode", "seed"), identity):
            if evaluation.get(key) != wanted or status.get(key) != wanted:
                raise ValueError(f"saved v5 evaluation identity mismatch: {evaluation_path}: {key}")
        if evaluation.get("smoke") is not (stage == "smoke"):
            raise ValueError(f"saved v5 evaluation stage mismatch: {evaluation_path}")
        if status is not None and evaluation.get("status") != status:
            raise ValueError(f"saved v5 evaluation status mismatch: {evaluation_path}")
        complete = evaluation.get("complete_for_evaluation") is True
        if evaluation.get("smoke_technical_pass") is not (stage == "smoke" and complete):
            raise ValueError(f"saved smoke verdict inconsistent with completeness: {evaluation_path}")
        if evaluation.get("primary_series_result") is not (stage == "main" and complete):
            raise ValueError(f"saved main verdict inconsistent with completeness: {evaluation_path}")
        source = _validate_source(folder, evaluation, identity[0]) if complete else None
        coverage_eligible = complete and full_available and not missing_declared
        reference = _retain_evaluation_payload(
            evaluation_path, report_dir, artifact_id=artifact_id, run_id=run_id,
            head_sha=manifest["commit"], expected_sha256=hashes["evaluation-v5.json"],
        )
        reports.append({
            **declaration, "artifact": artifact, "manifest": manifest,
            "root": str(folder), "evaluation_reference": reference,
            "evaluation_projection": _evaluation_projection(evaluation),
            "source_provenance": source,
            "technical_complete_self_reported": complete,
            "full_source_artifact_available": full_available,
            "full_source_artifact_reason": full_unavailable_reason,
            "eligible_main_coverage": coverage_eligible,
            "independently_admitted": False,
            "manifest_declared_transport_complete": not missing_declared,
            "missing_manifest_declared_files": missing_declared,
            "verified_nonmaterialized_manifest_files": sorted(nonmaterialized),
            "declared_file_recovery": recovery,
            "reason": (
                None if coverage_eligible else
                "manifest_declared_file_unavailable" if missing_declared else
                full_unavailable_reason if complete else
                "source_evaluation_technically_incomplete"
            ),
        })
    return reports


def _selection(path: Path | None, attempts: list[dict]) -> tuple[dict[tuple, int], dict]:
    if path is None:
        return {}, {"provided": False}
    value = _read(path)
    if (not isinstance(value, dict)
            or value.get("policy") != "technical_replacement_only_no_outcome_selection"):
        raise ValueError("v5 selection must assert technical-only outcome-independent replacement")
    chosen = {}
    for row in value.get("cells") or []:
        identity = _cell(row)
        if identity in chosen or type(row.get("selected_artifact_id")) is not int:
            raise ValueError(f"invalid v5 technical selection: {row}")
        candidates = [item for item in attempts
                      if item["stage"] == "main" and _cell(item) == identity]
        candidate_ids = {
            item["artifact"]["artifact_id"] for item in candidates if item.get("artifact")
        }
        candidate_runs = {item["run_id"] for item in candidates}
        declared = set(row.get("candidate_artifact_ids") or [])
        declared_runs = set(row.get("candidate_run_ids") or [])
        selected = row["selected_artifact_id"]
        complete = [item["artifact"]["artifact_id"] for item in candidates
                    if item.get("eligible_main_coverage") and item.get("artifact")]
        if (len(candidates) <= 1 or declared != candidate_ids
                or declared_runs != candidate_runs or selected not in candidate_ids
                or len(complete) != 1
                or selected != complete[0]
                or not str(row.get("reason_code", "")).startswith("technical_")):
            raise ValueError(f"invalid technical-only replacement for {identity}")
        chosen[identity] = selected
    return chosen, {"provided": True, "path": str(path.resolve()),
                    "sha256": _digest(path), "manifest": value}


def build(
    roots: list[Path], declarations_path: Path, report_dir: Path,
    *, retrieval_path: Path | None = None, selection_path: Path | None = None,
) -> dict[str, Any]:
    report_dir.mkdir(parents=True, exist_ok=True)
    declarations, declared_attempts = _declarations(declarations_path)
    reports = _saved_summaries(roots, declared_attempts, report_dir)
    by_declared = {}
    for item in reports:
        key = (item["run_id"], _cell(item))
        if key in by_declared:
            raise ValueError(f"multiple saved summaries claim the same declared run/cell: {key}")
        by_declared[key] = item
    attempts = []
    retrieval = _read(retrieval_path, []) if retrieval_path else []
    retrieval_by_key = {
        (row.get("run_id"), tuple(row.get("cell") or [])): row
        for row in retrieval if isinstance(row, dict)
    }
    for key, declaration in sorted(declared_attempts.items(), key=str):
        saved = by_declared.get(key)
        attempts.append(saved or {
            **declaration, "root": None, "artifact": None, "manifest": None,
            "evaluation_reference": None, "evaluation_projection": None,
            "technical_complete_self_reported": False,
            "manifest_declared_transport_complete": False,
            "full_source_artifact_available": False,
            "full_source_artifact_reason": "compact_artifact_not_retained",
            "eligible_main_coverage": False,
            "independently_admitted": False,
            "reason": (retrieval_by_key.get((key[0], key[1])) or {}).get(
                "status", "compact_artifact_not_retained"
            ),
        })
    common_head = declarations.get('experiment_head')
    for item in attempts:
        observed_head = (item.get('manifest') or {}).get('commit')
        if common_head and item['stage'] == 'main' and observed_head != common_head:
            item['common_source_coverage_exclusion'] = {
                'rule': ('outside_predeclared_common_source' if observed_head else 'source_commit_unavailable'),
                'expected_head': common_head, 'observed_head': observed_head,
                'previous_eligible_main_coverage': item['eligible_main_coverage'],
                'previous_reason': item.get('reason')}
            item['eligible_main_coverage'] = False
        item["attempt_key"] = ":".join(str(value) for value in (
            item["run_id"], item["collector"], item["stage"], item["system"],
            item["mode"], item["seed"],
        ))
    attempt_keys = [item["attempt_key"] for item in attempts]
    if len(set(attempt_keys)) != len(attempt_keys):
        raise ValueError("duplicate canonical v5 attempt key")
    selected_ids, selection = _selection(selection_path, attempts)
    grouped: dict[tuple, list[dict]] = {}
    for item in attempts:
        if item["stage"] == "main":
            grouped.setdefault(_cell(item), []).append(item)
    selected = {}
    ambiguous = []
    for identity, candidates in sorted(grouped.items()):
        complete = [item for item in candidates if item.get("eligible_main_coverage")]
        if len(candidates) == 1 and len(complete) == 1:
            selected[identity] = complete[0]
        elif len(candidates) > 1:
            artifact_id = selected_ids.get(identity)
            if artifact_id is None:
                ambiguous.append({
                    "cell": list(identity),
                    "candidate_artifact_ids": [
                        (item.get("artifact") or {}).get("artifact_id") for item in candidates
                    ],
                    "reason": "duplicate_main_cell_requires_technical_selection",
                })
            else:
                selected[identity] = next(
                    item for item in candidates
                    if (item.get("artifact") or {}).get("artifact_id") == artifact_id
                )
    blocked = {_cell(row): row["reason"] for row in declarations.get("blocked_main_cells") or []}
    undeclared_blocks = set(blocked) - EXPECTED_MAIN
    if undeclared_blocks:
        raise ValueError(f"blocked cells outside fixed main grid: {sorted(undeclared_blocks)}")
    payload_references = [
        item["evaluation_reference"] for item in attempts
        if item.get("evaluation_reference") is not None
    ]
    payload_manifest = {
        "schema_version": PAYLOAD_MANIFEST_SCHEMA,
        "payloads": sorted(payload_references, key=lambda row: row["artifact_id"]),
        "payload_count": len(payload_references),
        "claim": "exact retained source evaluation bytes; no scientific recomputation",
    }
    payload_manifest_path = report_dir / "evaluation-payload-manifest.json"
    payload_manifest_path.write_text(
        json.dumps(payload_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    result = {
        "schema_version": REFERENCED_AGGREGATE_SCHEMA,
        "input_mode": "saved_source_evaluations_no_raw_recompute",
        "declarations": declarations,
        "declarations_sha256": _digest(declarations_path),
        "retrieval": retrieval,
        "retrieval_sha256": _digest(retrieval_path) if retrieval_path else None,
        "source_pins": SOURCE_PINS,
        "source_pin_validation_scope": (
            "collector manifests only; full toolchain/input admission remains external"
        ),
        "attempts": attempts,
        "smoke_attempt_references": [
            item["attempt_key"] for item in attempts if item["stage"] == "smoke"
        ],
        "main_attempt_references": [
            item["attempt_key"] for item in attempts if item["stage"] == "main"
        ],
        "selected_main_attempt_references": [
            selected[key]["attempt_key"] for key in sorted(selected)
        ],
        "evaluation_payload_manifest": {
            "schema_version": PAYLOAD_MANIFEST_SCHEMA,
            "path": payload_manifest_path.relative_to(report_dir).as_posix(),
            "sha256": _digest(payload_manifest_path),
            "payload_count": len(payload_references),
        },
        "selection": selection,
        "ambiguous_duplicate_main_cells": ambiguous,
        "grid": {
            "declared_main_cells": len(EXPECTED_MAIN),
            "technically_complete_main_cells": len(selected),
            "blocked_main_cells": [list(key) + [blocked[key]] for key in sorted(blocked)],
            "incomplete_or_missing_main_cells": [
                list(key) for key in sorted(EXPECTED_MAIN - set(selected))
            ],
            "smoke_attempts_excluded_from_main_coverage": True,
        },
        "independent_admission": {
            "performed_by_reporter": False,
            "self_reported_technical_completeness_is_not_independent_review": True,
        },
        "claim": (
            "saved fields only; no acquisition, refit, relinking, rescoring, "
            "threshold, or positive contribution claim"
        ),
    }
    target = report_dir / "evaluation-v5.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _value(value: Any) -> str:
    if value is None:
        return "unknown"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, separators=(",", ":")).replace("|", "\\|")
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(_value(item) for item in row) + " |" for row in rows]
    if not rows:
        lines.append("| unavailable |" + " unknown |" * (len(headers) - 1))
    return lines


def _referenced_attempts(
    payload: dict[str, Any], aggregate_path: Path, field: str, *, stage: str,
) -> list[dict[str, Any]]:
    attempts = payload.get("attempts") or []
    by_key = {}
    for item in attempts:
        key = item.get("attempt_key") if isinstance(item, dict) else None
        if not isinstance(key, str) or not key or key in by_key:
            raise ValueError("invalid canonical attempt index")
        by_key[key] = item
    references = payload.get(field)
    if not isinstance(references, list) or any(not isinstance(key, str) for key in references):
        raise ValueError(f"invalid {field}")
    result = []
    seen = set()
    for key in references:
        item = by_key.get(key)
        if item is None or key in seen or item.get("stage") != stage:
            raise ValueError(f"invalid canonical attempt reference: {key}")
        seen.add(key)
        result.append(item)
    return result


def _validate_payload_manifest(payload: dict[str, Any], aggregate_path: Path) -> None:
    reference = payload.get("evaluation_payload_manifest")
    if (not isinstance(reference, dict)
            or reference.get("schema_version") != PAYLOAD_MANIFEST_SCHEMA
            or not isinstance(reference.get("path"), str)
            or not isinstance(reference.get("sha256"), str)):
        raise ValueError("invalid evaluation payload manifest reference")
    root = aggregate_path.resolve().parent
    path = (root / reference["path"]).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError("evaluation payload manifest escapes aggregate directory") from error
    manifest = _read(path)
    attempts = payload.get("attempts") or []
    expected = [item.get("evaluation_reference") for item in attempts
                if item.get("evaluation_reference") is not None]
    if (not path.is_file() or _digest(path) != reference["sha256"]
            or not isinstance(manifest, dict)
            or manifest.get("schema_version") != PAYLOAD_MANIFEST_SCHEMA
            or manifest.get("payloads") != sorted(expected, key=lambda row: row["artifact_id"])
            or manifest.get("payload_count") != len(expected)
            or reference.get("payload_count") != len(expected)):
        raise ValueError("evaluation payload manifest proof mismatch")
    for item in expected:
        payload_path = (root / str(item.get("path", ""))).resolve()
        try:
            payload_path.relative_to(root)
        except ValueError as error:
            raise ValueError("saved evaluation reference escapes aggregate directory") from error
        if (not payload_path.is_file() or payload_path.stat().st_size != item.get("gzip_bytes")
                or _digest(payload_path) != item.get("gzip_sha256")):
            raise ValueError("saved evaluation payload gzip proof mismatch")
    for attempt in attempts:
        evaluation_reference = attempt.get("evaluation_reference")
        projection = attempt.get("evaluation_projection")
        if evaluation_reference is None:
            if projection is not None:
                raise ValueError("projection exists without a source evaluation reference")
            continue
        evaluation = resolve_evaluation_reference(evaluation_reference, aggregate_path)
        if _evaluation_projection(evaluation) != projection:
            raise ValueError("saved evaluation projection does not match source payload")
        del evaluation


def _scientific_tables(attempts, schema):
    """Render source-produced summaries without reopening or rescoring raw data."""
    identity_headers = ["Run", "Collector", "System", "Mode", "Seed", "Complete"]
    failures, availability, graphs, baselines, db_counts, db_impact = [], [], [], [], [], []
    classes, persistence, cross_guest, causal_rows, causal_scope, db_identity = [], [], [], [], [], []
    for item in attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        identity = [item.get(key) for key in ("run_id", "collector", "system", "mode", "seed")]
        identity.append(item.get("technical_complete_self_reported"))
        summary = evaluation.get("scientific_summaries")
        availability.append(identity + [summary is not None,
                            "source-produced summary" if summary is not None else
                            "not retained in this historical source evaluation"])
        for row in evaluation.get("evaluations") or []:
            if row.get("available") is not True:
                failures.append(identity + [row.get("operation"), row.get("source"),
                    row.get("variant"), row.get("reason"),
                    row["unknown_obligations"] if "unknown_obligations" in row else
                    "not retained in this source evaluation"])
        if summary is None:
            continue
        for source, variants in (summary.get("graphs") or {}).items():
            for variant, operations in variants.items():
                for operation, graph in operations.items():
                    graphs.append(identity + [operation, source, variant, graph.get("available"),
                        graph.get("services"), graph.get("edges"), graph.get("endpoints"),
                        graph.get("bering_outputs_present"), graph.get("reason")])
                    db_identity.append(identity + [operation, source, variant,
                        graph.get("database_mapping"), graph.get("database_aliases"),
                        graph.get("incomplete_database_alias_count")])
        for operation, baseline in (summary.get("manual_baselines") or {}).items():
            baselines.append(identity + [operation, baseline.get("available"),
                baseline.get("prediction"), baseline.get("by_state"),
                baseline.get("primary_conditional_assumption"), baseline.get("database"),
                baseline.get("basis")])
        database = summary.get("database") or {}
        for phase in ("db_up", "db_down"):
            for operation, entry in (database.get(phase) or {}).items():
                db_counts.append(identity + [phase, operation, entry.get("counts")])
        for row in database.get("forecast_impact") or []:
            db_impact.append(identity + [row.get("operation"), row.get("source"), row.get("variant"),
                row.get("healthy_state_11_prediction"), row.get("database_down_prediction"),
                row.get("prognostic_impact"), row.get("comparison")])
        for classifier, result in (summary.get("classes") or {}).items():
            for row in result.get("class_test_metrics") or []:
                classes.append(identity + [classifier, row.get("source"), row.get("variant"),
                    row.get("total"), row.get("known"), row.get("unknown"), row.get("coverage"),
                    row.get("ari_labeled_known_subset"), row.get("ari_on_known_subset"),
                    row.get("pattern_statuses"), row.get("equivalent_to_base_family_assignment")])
        for phase, row in (summary.get("async") or {}).items():
            persistence.append(identity + [phase, row.get("available"), row.get("records"),
                row.get("states"), row.get("paused_absence_is_failure"), row.get("reason")])
        for source, row in (summary.get("cross_guest") or {}).items():
            cross_guest.append(identity + [source, row.get("exact_parent_links"),
                row.get("invalid_identity_candidates"), row.get("placement_coverage"),
                row.get("header_verdicts"), row.get("interpretation")])
        verdicts = summary.get("causal_attempt_verdicts")
        causal_scope.append(identity + [summary.get("causal_scope")])
        if verdicts is None:
            causal_rows.append(identity + [None, None, None, None,
                                          "causal attempt verdicts not retained"])
        else:
            census = {}
            for row in verdicts:
                key = (row.get("source"), row.get("phase"), row.get("four_stage_causal_chain"))
                census[key] = census.get(key, 0) + 1
            for (source, phase, verdict), count in census.items():
                causal_rows.append(identity + [source, phase, verdict, count,
                                               "census of saved verdicts; no relinking"])
    lines = ["", "## Additional saved scientific results", "",
             "Missing historical fields remain not retained. Graph presence, operation binding, "
             "simulation, independent outcomes and causal association are separate evidence.",
             "Repeated source/variant rows share external attempts and do not increase sample size."]
    tables = [
        ("Scientific detail availability", ["Details retained", "Scope"], availability),
        ("Stored unavailable obligations", ["Operation", "Source", "Variant", "Stored reason",
            "Frozen binding obligations"], failures),
        ("Actual saved Bering graph presence", ["Operation", "Source", "Variant", "Graph available",
            "Services", "Edges", "Endpoints", "Bering files present", "Reason"], graphs),
        ("Same-information direct baselines", ["Operation", "Available", "Prediction", "By state",
            "Conditional assumption", "Database baseline", "Basis"], baselines),
        ("Independent database controls", ["Phase", "Operation", "Stored outcome counts"], db_counts),
        ("Observed database identity and shared participation", ["Operation", "Source", "Variant",
            "Saved mapping checks", "Logical endpoints and callers", "Incomplete aliases"], db_identity),
        ("Saved database forecast impact", ["Operation", "Source", "Variant", "Healthy state 11",
            "DB-down prediction", "Impact", "Comparison"], db_impact),
        ("Frozen operation classification", ["Classifier", "Source", "Variant", "Total", "Known",
            "Unknown", "Coverage", "ARI labeled-known denominator", "ARI on known subset",
            "Pattern statuses", "Equivalent to base family"], classes),
        ("Independent asynchronous persistence", ["Phase", "Available", "Records", "States",
            "Paused absence treated as failure", "Reason"], persistence),
        ("Source-local cross-guest evidence", ["Source", "Exact parent links", "Invalid IDs",
            "Placement coverage", "Header verdicts", "Interpretation"], cross_guest),
        ("Saved asynchronous association verdicts", ["Source", "Phase", "Stored verdict",
            "Count", "Scope"], causal_rows),
        ("Asynchronous association scope", ["Saved scope and invalid identity count"], causal_scope),
    ]
    for title, headers, rows in tables:
        lines += ["", "### " + title, ""] + _table(identity_headers + headers, rows)
    lines += ["", "Binding obligations identify an unavailable transition, not a proven collector "
              "root cause. Direct-baseline equivalence does not invalidate feasibility. DB impact "
              "compares healthy state 11 with DB-down. Async association does not establish SQL durability.", ""]
    return lines


def render(aggregate_path: Path, out: Path, costs_path: Path | None = None) -> dict[str, Any]:
    payload = _read(aggregate_path)
    schema = payload.get("schema_version") if isinstance(payload, dict) else None
    if schema not in (LEGACY_AGGREGATE_SCHEMA, REFERENCED_AGGREGATE_SCHEMA):
        raise ValueError("report_v5 requires an evaluation-v5 saved aggregate")
    attempts = payload.get("attempts") or []
    if schema == REFERENCED_AGGREGATE_SCHEMA:
        _validate_payload_manifest(payload, aggregate_path)
        smoke_attempts = _referenced_attempts(
            payload, aggregate_path, "smoke_attempt_references", stage="smoke",
        )
        main_attempts = _referenced_attempts(
            payload, aggregate_path, "main_attempt_references", stage="main",
        )
        selected_main_attempts = _referenced_attempts(
            payload, aggregate_path, "selected_main_attempt_references", stage="main",
        )
        expected_smoke = [item for item in attempts if item.get("stage") == "smoke"]
        expected_main = [item for item in attempts if item.get("stage") == "main"]
        if smoke_attempts != expected_smoke or main_attempts != expected_main:
            raise ValueError("canonical stage references do not cover attempts in stored order")
        if any(item.get("eligible_main_coverage") is not True
               for item in selected_main_attempts):
            raise ValueError("selected main reference is not coverage eligible")
    else:
        smoke_attempts = payload.get("smoke_attempts") or []
        main_attempts = payload.get("main_attempts") or []
    costs = _read(costs_path, {}) if costs_path else {}
    if costs_path and (
        not isinstance(costs, dict) or costs.get("schema_version") != "v5-actions-costs"
    ):
        raise ValueError("report_v5 requires a v5 Actions cost ledger")
    lines = [
        "# Iteration-5 saved-artifact report", "",
        "This report copies source-produced evaluations and technical records. It performs no refit, relinking, rescoring, thresholding, or accuracy-based selection.",
        f"Technical smoke status is separate from the {(payload.get('grid') or {}).get('declared_main_cells', 'unknown')}-cell main grid and is not an independent admission or positive contribution claim.",
        "", "## Fixed grid and execution boundary", "",
    ]
    lines += _table(["Stored field", "Value"], [
        [key, value] for key, value in (payload.get("grid") or {}).items()
    ])
    if (payload.get('declarations') or {}).get('experiment_head'):
        lines += ['', 'Declared common source commit: `' + payload['declarations']['experiment_head'] +
                  '`. Historical main rows remain visible; other source commits do not contribute to this grid.']
    lines += ["", "## Every declared attempt", ""]
    attempt_rows = []
    for item in attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        artifact = item.get("artifact") or {}
        status = evaluation.get("status") or {}
        attempt_rows.append([
            item.get("run_id"), item.get("repository"), item.get("collector"), item.get("stage"),
            item.get("system"), item.get("mode"), item.get("seed"),
            item.get("technical_complete_self_reported"),
            item.get("manifest_declared_transport_complete"),
            item.get("full_source_artifact_available"),
            item.get("eligible_main_coverage"), False,
            status.get("status"), artifact.get("artifact_id"), artifact.get("digest"),
            artifact.get("full_artifact_id"), artifact.get("full_artifact_digest"),
            item.get("reason"),
            (item.get('manifest') or {}).get('commit'), item.get('common_source_coverage_exclusion'),
        ])
    lines += _table([
        "Run", "Repository", "Collector", "Stage", "System", "Mode", "Seed",
        "Self-reported complete", "Declared transport complete",
        "Full source artifact available", "Coverage eligible", "Independently admitted",
        "Status", "Summary artifact", "Summary digest",
        "Full artifact", "Full digest", "Missing/incomplete reason",
        'Source commit', 'Common-source coverage exclusion',
    ], attempt_rows)
    lines += ["", "## Technical smoke qualification records", ""]
    smoke_rows = []
    for item in smoke_attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        acquisition = evaluation.get("acquisition") or {}
        smoke_rows.append([
            item.get("run_id"), item.get("collector"), item.get("system"), item.get("mode"),
            item.get("seed"), evaluation.get("smoke_technical_pass"),
            acquisition.get("valid"), acquisition.get("problems"), False,
        ])
    lines += _table([
        "Run", "Collector", "System", "Mode", "Seed", "Source technical pass",
        "Acquisition valid", "Stored problems", "Independent admission",
    ], smoke_rows)
    lines += ["", "## Saved main forecasts and external outcomes", ""]
    forecast_rows = []
    for item in main_attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        for row in evaluation.get("evaluations") or []:
            counts = row.get("actual_target_success_counts") or row.get("actual_counts") or {}
            forecast_rows.append([
                item.get("run_id"), item.get("collector"), item.get("system"), item.get("mode"),
                item.get("seed"), item.get("technical_complete_self_reported"),
                (item.get('manifest') or {}).get('commit'), item.get('eligible_main_coverage'),
                row.get("operation"), row.get("source"), row.get("variant"), row.get("available"),
                row.get("prediction", row.get("point_prediction")), row.get("forecast_interval"),
                counts.get("true", counts.get("success")), counts.get("false", counts.get("failure")),
                counts.get("none", counts.get("unknown")), row.get("reason"),
            ])
    lines += _table([
        "Run", "Collector", "System", "Mode", "Seed", "Complete", 'Source commit', 'Coverage eligible', "Operation", "Source",
        "Variant", "Available", "Stored forecast", "Stored interval", "Actual true",
        "Actual false", "Actual unknown", "Stored reason",
    ], forecast_rows)
    lines += _scientific_tables(main_attempts, schema)
    lines += ["", "## Saved campaign and Actions costs", ""]
    lines += _table(["Ledger field", "Stored value"], [
        [key, costs.get(key)] for key in (
            "known_completed_job_elapsed_seconds", "runs_with_unknown_job_elapsed",
            "known_stored_artifact_bytes", "runs_with_unknown_artifact_bytes",
            "report_artifact_transfer", "human_agent_seconds",
            "current_report_job_tail_seconds",
            "scope", "overlap_rule",
        )
    ])
    lines += [""]
    campaign_cost_rows = []
    for item in attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        cost = evaluation.get("cost") or {}
        campaign_cost_rows.append([
            item.get("run_id"), item.get("collector"), item.get("stage"), item.get("system"),
            item.get("mode"), item.get("seed"), cost.get("campaign_elapsed_seconds"),
            cost.get("toolchain_build_seconds"), cost.get("toolchain_command_seconds"),
            (cost.get("manual_preparation") or {}).get("measured"),
            (cost.get("manual_preparation") or {}).get("reason"),
        ])
    lines += _table([
        "Run", "Collector", "Stage", "System", "Mode", "Seed", "Campaign s",
        "Toolchain build s", "Toolchain command s", "Manual effort measured", "Reason",
    ], campaign_cost_rows)
    lines += ["", "Actions jobs, including runs without a campaign artifact:", ""]
    job_rows = []
    for run in costs.get("runs") or []:
        jobs = run.get("jobs") or [None]
        for job in jobs:
            job = job or {}
            job_rows.append([
                run.get("run_id"), run.get("repository"), run.get("role"),
                run.get("status"), run.get("conclusion"),
                job.get("id"), job.get("name"), job.get("status"), job.get("conclusion"),
                job.get("elapsed_seconds"), len(run.get("artifacts") or []),
            ])
    lines += _table([
        "Run", "Repository", "Role", "Run status", "Run conclusion", "Job", "Job name", "Job status",
        "Job conclusion", "Stored elapsed s", "Artifacts",
    ], job_rows)
    lines += [
        "", "Human/agent preparation effort: " + _value(costs.get("human_agent_seconds")),
        "", "Current report-job unfinished tail: " + _value(costs.get("current_report_job_tail_seconds")),
        "", (
            "Every source evaluation remains losslessly restorable from an explicit hash-bound "
            "payload reference. The small aggregate retains only fields used by these tables."
            if schema == REFERENCED_AGGREGATE_SCHEMA else
            "The legacy aggregate retains every source evaluation object, including detailed "
            "DB, baseline, class, async, causal and cost fields not expanded here."
        ),
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"attempts": len(attempts), "report": str(out.resolve())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, nargs="+")
    parser.add_argument("--declarations", type=Path)
    parser.add_argument("--retrieval", type=Path)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--aggregate", type=Path)
    parser.add_argument("--costs", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        parser.error("v5 research reporting is permitted only in GitHub Actions")
    if args.inputs:
        if not args.declarations or not args.report_dir:
            parser.error("--inputs requires --declarations and --report-dir")
        build(args.inputs, args.declarations, args.report_dir,
              retrieval_path=args.retrieval, selection_path=args.selection)
    elif args.aggregate and args.out:
        render(args.aggregate, args.out, args.costs)
    else:
        parser.error("choose saved aggregation or rendering")


if __name__ == "__main__":
    main()
