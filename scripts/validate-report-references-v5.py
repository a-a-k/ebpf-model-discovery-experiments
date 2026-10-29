"""Validate referenced report payloads against one immutable saved report artifact."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import time
import traceback
import zipfile

import ijson

from ebpf_discovery.artifact_recovery_v5 import recover_declared_files, retain_unavailable
from ebpf_discovery.report_v5 import build, render, resolve_evaluation_reference


REPOSITORY = "a-a-k/ebpf-model-discovery-experiments"
RUN_ID = 40930225342
SOURCE_HEAD = "f5ac530ec4a13cecd6178fffcdd886628f47af04"
ARTIFACT_ID = 12921733573
ARTIFACT_NAME = "report-v5-40930225342"
ARTIFACT_DIGEST = "sha256:b997086495790899f2579338cb2345b464280c8581bae6bb1caa1d3ae6ff6e04"
ARTIFACT_SIZE = 638_543_351
REQUIRED_OUTER = {
    "evaluation-v5.json.gz", "report-v5.md", "costs-v5.json",
    "provenance/declarations.json", "provenance/retrieval.json",
}


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe(info: zipfile.ZipInfo) -> bool:
    name, parts = info.filename, PurePosixPath(info.filename).parts
    return bool(name and "\\" not in name and not PurePosixPath(name).is_absolute()
                and ".." not in parts and not stat.S_ISLNK(info.external_attr >> 16))


def _verify_source(archive: Path, artifact: dict, run: dict) -> dict:
    expected = {"id": ARTIFACT_ID, "name": ARTIFACT_NAME, "size_in_bytes": ARTIFACT_SIZE,
                "digest": ARTIFACT_DIGEST, "expired": False}
    if {key: artifact.get(key) for key in expected} != expected:
        raise ValueError("source report artifact API identity mismatch")
    workflow = artifact.get("workflow_run") or {}
    if (workflow.get("id") != RUN_ID or workflow.get("head_sha") != SOURCE_HEAD
            or run.get("id") != RUN_ID or run.get("head_sha") != SOURCE_HEAD
            or run.get("repository", {}).get("full_name") != REPOSITORY
            or run.get("conclusion") != "success"):
        raise ValueError("source report workflow API identity mismatch")
    digest, size = "sha256:" + _sha(archive), archive.stat().st_size
    if digest != ARTIFACT_DIGEST or size != ARTIFACT_SIZE:
        raise ValueError("source report ZIP differs from API identity")
    return {"repository": REPOSITORY, "run_id": RUN_ID, "head_sha": SOURCE_HEAD,
            "artifact_id": ARTIFACT_ID, "artifact_name": ARTIFACT_NAME,
            "api_digest": ARTIFACT_DIGEST, "computed_digest": digest,
            "api_size_in_bytes": ARTIFACT_SIZE, "received_bytes": size}


def _extract_source_report(archive: Path, destination: Path) -> list[dict]:
    destination.mkdir(parents=True, exist_ok=False)
    proofs = []
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        names = {entry.filename for entry in entries}
        if len(names) != len(entries) or not all(_safe(entry) for entry in entries):
            raise ValueError("source report ZIP has duplicate or unsafe names")
        if not REQUIRED_OUTER <= names:
            raise ValueError("source report ZIP lacks a required member")
        wanted = [entry for entry in entries if not entry.is_dir() and (
            entry.filename in REQUIRED_OUTER or entry.filename.startswith("source-artifacts/")
        )]
        for entry in wanted:
            target = (destination / PurePosixPath(entry.filename)).resolve()
            target.relative_to(destination.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with bundle.open(entry) as source, target.open("wb") as output:
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
            proofs.append({"path": entry.filename, "bytes": entry.file_size,
                           "sha256": digest.hexdigest(), "zip_crc32": f"{entry.CRC:08x}"})
    return proofs


def _safe_extract(archive: Path, destination: Path) -> dict[str, bytes]:
    destination.mkdir(parents=True, exist_ok=False)
    evaluations = {}
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries) or not all(
                _safe(entry) for entry in entries):
            raise ValueError(f"compact ZIP has duplicate or unsafe names: {archive}")
        for entry in entries:
            if entry.is_dir():
                continue
            body = bundle.read(entry)  # verifies CRC
            target = (destination / PurePosixPath(entry.filename)).resolve()
            target.relative_to(destination.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            if entry.filename == "evaluation-v5.json":
                evaluations[entry.filename] = body
    return evaluations


def _retained_path(source: Path, value: str) -> Path:
    path = PurePosixPath(value)
    prefix = PurePosixPath("results/iteration-5")
    try:
        relative = path.relative_to(prefix)
    except ValueError as error:
        raise ValueError(f"retained source path has wrong root: {value}") from error
    target = (source / relative).resolve()
    target.relative_to(source.resolve())
    return target


def _recovery_semantics(value: dict) -> dict:
    copied = json.loads(json.dumps(value))
    verification = (copied.get("source") or {}).get("full_zip_verification")
    if isinstance(verification, dict):
        verification.pop("path", None)
    return copied


def _reconstruct_inputs(source: Path, destination: Path) -> tuple[dict[int, bytes], dict]:
    retrieval = _json(source / "provenance/retrieval.json")
    exact_evaluations: dict[int, bytes] = {}
    restored = []
    for row in retrieval:
        artifact = row.get("artifact")
        proof = row.get("compact_zip_verification")
        if not isinstance(artifact, dict) or not isinstance(proof, dict):
            restored.append({"run_id": row.get("run_id"), "status": row.get("status"),
                             "artifact_id": None})
            continue
        artifact_id = artifact["id"]
        compact = _retained_path(source, proof["retained_path"])
        if (not compact.is_file() or compact.stat().st_size != proof["received_bytes"]
                or "sha256:" + _sha(compact) != artifact["digest"]
                or proof.get("computed_sha256") != artifact["digest"]):
            raise ValueError(f"retained compact ZIP proof mismatch: {artifact_id}")
        folder = destination / str(row["run_id"]) / row["name"]
        found = _safe_extract(compact, folder)
        if "evaluation-v5.json" not in found:
            raise ValueError(f"compact source lacks original evaluation bytes: {artifact_id}")
        exact_evaluations[artifact_id] = found["evaluation-v5.json"]
        recovery = row.get("declared_file_recovery")
        if isinstance(recovery, dict):
            source_proof = recovery.get("source") or {}
            if recovery.get("status") == "recovered":
                clean_source = {key: value for key, value in source_proof.items()
                                if key != "full_zip_verification"}
                full_path = _retained_path(
                    source, (source_proof.get("full_zip_verification") or {}).get("path", ""),
                )
                actual_recovery = recover_declared_files(folder, full_path, clean_source)
            else:
                actual_recovery = retain_unavailable(
                    folder, recovery.get("requested_files") or [], source_proof,
                    recovery.get("status"), recovery.get("detail"),
                )
            if _recovery_semantics(actual_recovery) != _recovery_semantics(recovery):
                raise ValueError(f"frozen recovery proof did not reproduce: {artifact_id}")
        manifest = _json(folder / "evaluation-manifest.json")
        sidecar = {
            "run_id": row["run_id"], "repository": row["repository"],
            "head_sha": manifest["commit"], "artifact_id": artifact_id,
            "name": row["name"], "digest": artifact["digest"], "expired": False,
            "full_artifact_id": (row.get("full_artifact") or {}).get("id"),
            "full_artifact_name": row["full_artifact_name"],
            "full_artifact_digest": (row.get("full_artifact") or {}).get("digest"),
            "full_artifact_expired": (row.get("full_artifact") or {}).get("expired"),
            "compact_zip_verification": proof,
            "declared_file_recovery": ({"path": "declared-file-recovery.json",
                "sha256": _sha(folder / "declared-file-recovery.json"),
                "status": recovery.get("status")} if isinstance(recovery, dict) else None),
        }
        _write(folder / "artifact-provenance.json", sidecar)
        restored.append({"run_id": row["run_id"], "status": row["status"],
                         "artifact_id": artifact_id,
                         "evaluation_sha256": hashlib.sha256(found["evaluation-v5.json"]).hexdigest()})
    return exact_evaluations, {"retrieval_rows": len(retrieval), "restored": restored}


def _old_selection_and_ids(aggregate_gzip: Path) -> tuple[dict | None, list[int]]:
    with gzip.open(aggregate_gzip, "rb") as stream:
        selection = next(ijson.items(stream, "selection"))
    with gzip.open(aggregate_gzip, "rb") as stream:
        selected_ids = list(ijson.items(
            stream, "selected_main_evaluations.item.artifact.artifact_id"
        ))
    manifest = selection.get("manifest") if selection.get("provided") else None
    return manifest, selected_ids


def _tables(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("|")]


def validate(archive: Path, artifact_metadata: Path, run_metadata: Path, out: Path) -> dict:
    started = time.monotonic()
    out.mkdir(parents=True, exist_ok=False)
    source = out / "source-report"
    source_identity = _verify_source(archive, _json(artifact_metadata), _json(run_metadata))
    member_proofs = _extract_source_report(archive, source)
    inputs = out / "inputs"
    exact_evaluations, reconstruction = _reconstruct_inputs(source, inputs)
    old_selection, old_selected_ids = _old_selection_and_ids(source / "evaluation-v5.json.gz")
    selection_path = None
    if old_selection is not None:
        selection_path = out / "selection.json"
        _write(selection_path, old_selection)
    report_dir = out / "referenced-report"
    aggregate = build(
        [inputs], source / "provenance/declarations.json", report_dir,
        retrieval_path=source / "provenance/retrieval.json",
        selection_path=selection_path,
    )
    render(report_dir / "evaluation-v5.json", report_dir / "report-v5.md",
           source / "costs-v5.json")
    attempt_by_key = {row["attempt_key"]: row for row in aggregate["attempts"]}
    new_selected_ids = [attempt_by_key[key]["artifact"]["artifact_id"]
                        for key in aggregate["selected_main_attempt_references"]]
    if new_selected_ids != old_selected_ids:
        raise ValueError("selected main cells differ from the frozen source report")
    if _tables(report_dir / "report-v5.md") != _tables(source / "report-v5.md"):
        raise ValueError("rendered report tables differ from the frozen source report")
    restored = []
    for attempt in aggregate["attempts"]:
        reference = attempt.get("evaluation_reference")
        artifact = attempt.get("artifact") or {}
        if reference is None:
            if artifact.get("artifact_id") in exact_evaluations:
                raise ValueError("retained source evaluation lacks a payload reference")
            continue
        artifact_id = artifact.get("artifact_id")
        original = exact_evaluations.get(artifact_id)
        if original is None:
            raise ValueError("payload reference lacks original compact source bytes")
        value = resolve_evaluation_reference(reference, report_dir / "evaluation-v5.json")
        restored_bytes = gzip.open(report_dir / reference["path"], "rb").read()
        if restored_bytes != original or value != json.loads(original):
            raise ValueError("referenced payload does not restore exact source evaluation")
        restored.append({"artifact_id": artifact_id, "source_sha256": reference["source_sha256"],
                         "source_bytes": reference["source_bytes"],
                         "gzip_sha256": reference["gzip_sha256"],
                         "gzip_bytes": reference["gzip_bytes"]})
    if len(restored) != len(exact_evaluations):
        raise ValueError("not every retained source evaluation was restored")
    result = {
        "schema_version": "report-v5-referenced-payload-validation-v1",
        "source": source_identity,
        "outer_selected_member_proofs": member_proofs,
        "reconstruction": reconstruction,
        "declared_attempts": len(aggregate["attempts"]),
        "restored_payloads": restored,
        "restored_payload_count": len(restored),
        "selected_main_artifact_ids": new_selected_ids,
        "rendered_table_lines": len(_tables(report_dir / "report-v5.md")),
        "all_tables_identical": True,
        "all_payloads_restore_exact_original_compact_bytes": True,
        "source_packet_unchanged": True,
        "scientific_recomputation_performed": False,
        "scope": "report representation and exact transport only; no graph, forecast, class, outcome, refit, replay, or rescoring",
        "elapsed_seconds": time.monotonic() - started,
    }
    _write(out / "validation.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--artifact-metadata", type=Path, required=True)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        validate(args.archive, args.artifact_metadata, args.run_metadata, args.out)
    except Exception as error:
        args.out.mkdir(parents=True, exist_ok=True)
        _write(args.out / "failure.json", {
            "schema_version": "report-v5-referenced-payload-validation-failure-v1",
            "error": f"{type(error).__name__}:{error}", "traceback": traceback.format_exc(),
            "scientific_recomputation_performed": False,
        })
        raise


if __name__ == "__main__":
    main()
