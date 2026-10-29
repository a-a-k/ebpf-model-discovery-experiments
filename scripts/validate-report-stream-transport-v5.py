"""Validate bounded compact transport against the exact extract-all reporter."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tarfile
import tempfile
import time
import zipfile

try:
    import resource
except ImportError:  # pragma: no cover - the retained validation runs on Linux
    resource = None

from ebpf_discovery.compact_transport_v5 import (
    extract_verified_compact, remove_verified_working_copy,
)
from ebpf_discovery.report_v5 import build, render, resolve_evaluation_reference


REPOSITORY = "a-a-k/ebpf-model-discovery-experiments"
RUN_ID = 40942429097
SOURCE_HEAD = "5cfdd7cbb60daec95d447109a18f82219ea29e8f"
ARTIFACT_ID = 12933554459
ARTIFACT_NAME = "v5-summary-obi-main-deathstarbench-absent-7-40942429097"
ARTIFACT_DIGEST = "sha256:d6003f14d541e8cc23948451142f9724c70f706318b761edbf1ff880b8fd768e"
ARTIFACT_SIZE = 2_591_423_771
FULL_ARTIFACT_ID = 12933019490
FULL_ARTIFACT_NAME = "campaign-v5-obi-main-deathstarbench-absent-7-40942429097"
FULL_ARTIFACT_DIGEST = "sha256:5a8655821fcb86ffb27bc1811d5994e9425898a339d8801ca771a54ce184585e"
FULL_ARTIFACT_SIZE = 6_111_686_489
OLD_REPORT_COMMIT = "8a985f99bfd2ecd4ebe13274e100c86feaae0560"


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _verify_api(archive: Path, artifact: dict, full_artifact: dict, run: dict) -> dict:
    expected = {"id": ARTIFACT_ID, "name": ARTIFACT_NAME,
                "size_in_bytes": ARTIFACT_SIZE, "digest": ARTIFACT_DIGEST,
                "expired": False}
    if {key: artifact.get(key) for key in expected} != expected:
        raise ValueError("pinned compact artifact API identity mismatch")
    expected_full = {"id": FULL_ARTIFACT_ID, "name": FULL_ARTIFACT_NAME,
                     "size_in_bytes": FULL_ARTIFACT_SIZE,
                     "digest": FULL_ARTIFACT_DIGEST, "expired": False}
    if {key: full_artifact.get(key) for key in expected_full} != expected_full:
        raise ValueError("pinned full artifact API identity mismatch")
    workflow = artifact.get("workflow_run") or {}
    full_workflow = full_artifact.get("workflow_run") or {}
    if (workflow.get("id") != RUN_ID or workflow.get("head_sha") != SOURCE_HEAD
            or full_workflow.get("id") != RUN_ID
            or full_workflow.get("head_sha") != SOURCE_HEAD
            or run.get("id") != RUN_ID or run.get("head_sha") != SOURCE_HEAD
            or run.get("repository", {}).get("full_name") != REPOSITORY):
        raise ValueError("pinned compact workflow API identity mismatch")
    computed = "sha256:" + _sha(archive)
    if computed != ARTIFACT_DIGEST or archive.stat().st_size != ARTIFACT_SIZE:
        raise ValueError("received compact ZIP differs from pinned API identity")
    return {**expected, "repository": REPOSITORY, "run_id": RUN_ID,
            "head_sha": SOURCE_HEAD, "computed_digest": computed,
            "received_bytes": archive.stat().st_size,
            "full_artifact": expected_full,
            "run_status": run.get("status"), "run_conclusion": run.get("conclusion")}


def _safe(info: zipfile.ZipInfo) -> bool:
    name, parts = info.filename, PurePosixPath(info.filename).parts
    return bool(name and "\\" not in name and not PurePosixPath(name).is_absolute()
                and ".." not in parts and not stat.S_ISLNK(info.external_attr >> 16))


def _extract_all(archive: Path, destination: Path) -> list[dict]:
    destination.mkdir(parents=True, exist_ok=False)
    proofs = []
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries):
            raise ValueError("extract-all source has duplicate members")
        if not all(_safe(entry) and not entry.is_dir() for entry in entries):
            raise ValueError("extract-all source has unsafe members")
        for entry in entries:
            target = destination / PurePosixPath(entry.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            digest, size = hashlib.sha256(), 0
            with bundle.open(entry) as source, target.open("wb") as output:
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
            proofs.append({"name": entry.filename, "sha256": digest.hexdigest(),
                           "bytes": size, "crc32": f"{entry.CRC:08x}",
                           "compressed_bytes": entry.compress_size})
    return proofs


def _declarations(manifest: dict) -> dict:
    return {"schema_version": "v5-report-declarations", "attempt_runs": [{
        "run_id": RUN_ID, "repository": REPOSITORY,
        "collector": manifest["collector"],
        "stage": "smoke" if manifest.get("smoke") is True else "main",
        "cells": [{"system": manifest["system"], "mode": manifest["mode"],
                   "seed": manifest["seed"]}],
        "note": "pinned saved transport equivalence validation",
    }], "related_runs": [], "blocked_main_cells": []}


def _sidecar(manifest: dict, proof: dict) -> dict:
    return {"run_id": RUN_ID, "repository": REPOSITORY, "head_sha": SOURCE_HEAD,
            "artifact_id": ARTIFACT_ID, "name": ARTIFACT_NAME,
            "digest": ARTIFACT_DIGEST, "expired": False,
            "full_artifact_id": FULL_ARTIFACT_ID,
            "full_artifact_name": FULL_ARTIFACT_NAME,
            "full_artifact_digest": FULL_ARTIFACT_DIGEST,
            "full_artifact_expired": False,
            "compact_zip_verification": proof, "declared_file_recovery": None}


def _old_source(destination: Path) -> dict:
    completed = subprocess.run(
        ["git", "archive", "--format=tar", OLD_REPORT_COMMIT, "src/ebpf_discovery"],
        check=True, stdout=subprocess.PIPE,
    )
    with tempfile.NamedTemporaryFile() as temporary:
        temporary.write(completed.stdout)
        temporary.flush()
        with tarfile.open(temporary.name) as bundle:
            bundle.extractall(destination, filter="data")
    report = destination / "src/ebpf_discovery/report_v5.py"
    return {"commit": OLD_REPORT_COMMIT, "report_v5_sha256": _sha(report),
            "archive_sha256": hashlib.sha256(completed.stdout).hexdigest(),
            "archive_bytes": len(completed.stdout)}


def _run_old(source: Path, inputs: Path, declarations: Path, report: Path) -> dict:
    environment = {**os.environ, "PYTHONPATH": str(source / "src"),
                   "GITHUB_ACTIONS": "true"}
    command = [os.sys.executable, "-m", "ebpf_discovery.report_v5", "--inputs",
               str(inputs), "--declarations", str(declarations),
               "--report-dir", str(report)]
    started = time.monotonic()
    completed = subprocess.run(command, text=True, capture_output=True, env=environment)
    elapsed = time.monotonic() - started
    if completed.returncode:
        raise ValueError(f"old reporter failed: {completed.stderr}")
    render_command = [os.sys.executable, "-m", "ebpf_discovery.report_v5",
                      "--aggregate", str(report / "evaluation-v5.json"),
                      "--out", str(report / "report-v5.md")]
    render_started = time.monotonic()
    rendered = subprocess.run(render_command, text=True, capture_output=True, env=environment)
    render_elapsed = time.monotonic() - render_started
    if rendered.returncode:
        raise ValueError(f"old renderer failed: {rendered.stderr}")
    return {"command": command, "returncode": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr,
            "report_seconds": elapsed, "render_seconds": render_elapsed}


def _tables(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("|")]


def _comparison(old_report: Path, new_report: Path) -> dict:
    old, new = _json(old_report / "evaluation-v5.json"), _json(
        new_report / "evaluation-v5.json")
    old_attempt, new_attempt = old["attempts"][0], new["attempts"][0]
    old_payload = resolve_evaluation_reference(
        old_attempt["evaluation_reference"], old_report / "evaluation-v5.json")
    new_payload = resolve_evaluation_reference(
        new_attempt["evaluation_reference"], new_report / "evaluation-v5.json")
    checks = {
        "source_evaluation_payload_equal": old_payload == new_payload,
        "evaluation_projection_equal": (old_attempt["evaluation_projection"]
                                        == new_attempt["evaluation_projection"]),
        "eligible_main_coverage_equal_and_true": (
            old_attempt["eligible_main_coverage"] is True
            and new_attempt["eligible_main_coverage"] is True),
        "grid_equal": old["grid"] == new["grid"],
        "selected_main_attempt_references_equal": (
            old["selected_main_attempt_references"]
            == new["selected_main_attempt_references"]),
        "ambiguous_main_cells_equal": old["ambiguous_main_cells"]
                                      == new["ambiguous_main_cells"],
        "rendered_tables_equal": (_tables(old_report / "report-v5.md")
                                  == _tables(new_report / "report-v5.md")),
        "evaluation_reference_source_sha256_equal": (
            old_attempt["evaluation_reference"]["source_sha256"]
            == new_attempt["evaluation_reference"]["source_sha256"]),
    }
    if not all(checks.values()):
        raise ValueError(f"old/new saved report semantics differ: {checks}")
    return checks


def validate(archive: Path, artifact_metadata: Path, full_artifact_metadata: Path,
             run_metadata: Path, out: Path) -> dict:
    started = time.monotonic()
    out.mkdir(parents=True, exist_ok=False)
    identity = _verify_api(
        archive, _json(artifact_metadata), _json(full_artifact_metadata),
        _json(run_metadata),
    )
    old_source = out / "old-source"
    source_proof = _old_source(old_source)
    old_input = out / "old-input"
    old_extract_started = time.monotonic()
    old_members = _extract_all(archive, old_input)
    old_extract_seconds = time.monotonic() - old_extract_started
    manifest = _json(old_input / "evaluation-manifest.json")
    declarations = out / "declarations.json"
    _write(declarations, _declarations(manifest))
    legacy_proof = {"expected_sha256": ARTIFACT_DIGEST,
                    "computed_sha256": ARTIFACT_DIGEST,
                    "received_bytes": ARTIFACT_SIZE,
                    "member_count": len(old_members), "safe_extract": True,
                    "retained_path": str(archive)}
    _write(old_input / "artifact-provenance.json", _sidecar(manifest, legacy_proof))
    old_report = out / "old-report"
    old_run = _run_old(old_source, old_input, declarations, old_report)
    old_input_bytes = sum(path.stat().st_size for path in old_input.rglob("*")
                          if path.is_file())
    shutil.rmtree(old_input)
    if old_input.exists():
        raise OSError("extract-all working tree remains before bounded validation")

    new_input = out / "new-input"
    new_extract_started = time.monotonic()
    proof = extract_verified_compact(
        archive, new_input, expected_digest=ARTIFACT_DIGEST,
        expected_bytes=ARTIFACT_SIZE,
    )
    new_extract_seconds = time.monotonic() - new_extract_started
    remove_verified_working_copy(archive, proof)
    if archive.exists():
        raise OSError("bounded compact working ZIP was not removed")
    _write(new_input / "artifact-provenance.json", _sidecar(manifest, proof))
    new_report = out / "new-report"
    new_started = time.monotonic()
    aggregate = build([new_input], declarations, new_report)
    new_report_seconds = time.monotonic() - new_started
    render_started = time.monotonic()
    render(new_report / "evaluation-v5.json", new_report / "report-v5.md")
    new_render_seconds = time.monotonic() - render_started
    checks = _comparison(old_report, new_report)
    old_by_name = {row["name"]: row for row in old_members}
    new_by_name = {row["name"]: row for row in proof["members"]}
    member_fields = ("sha256", "bytes", "crc32", "compressed_bytes")
    member_equivalence = (old_by_name.keys() == new_by_name.keys()
                          and all(all(old_by_name[name][key] == new_by_name[name][key]
                                      for key in member_fields) for name in old_by_name))
    if not member_equivalence:
        raise ValueError("extract-all and bounded member proofs differ")
    if (len(aggregate["selected_main_attempt_references"]) != 1
            or aggregate["selected_main_attempt_references"][0]
            != f"{RUN_ID}:obi:main:deathstarbench:absent:7"):
        raise ValueError("bounded validation did not select the pinned complete main cell")
    journal = new_by_name["attempt-journal.jsonl"]
    if (journal["materialized"] is not False
            or journal["sha256"] != manifest["files_sha256"]["attempt-journal.jsonl"]):
        raise ValueError("bounded journal proof is not exact")
    result = {
        "schema_version": "v5-report-stream-transport-validation",
        "equivalent": True, "source": identity, "old_source": source_proof,
        "old_extract_all": {"members": old_members,
                            "extract_seconds": old_extract_seconds,
                            "materialized_bytes": old_input_bytes, **old_run},
        "bounded_transport": {"proof": proof,
                              "extract_seconds": new_extract_seconds,
                              "report_seconds": new_report_seconds,
                              "render_seconds": new_render_seconds,
                              "archive_removed": True},
        "member_proofs_equal": member_equivalence, "report_checks": checks,
        "journal": {"sha256": journal["sha256"], "bytes": journal["bytes"],
                    "compressed_bytes": journal["compressed_bytes"],
                    "retained_as": journal["disposition"],
                    "locally_reopened_after_removal": False},
        "aggregate_attempt_count": len(aggregate["attempts"]),
        "cost": {"elapsed_seconds": time.monotonic() - started,
                 "process_max_rss_platform_units": (resource.getrusage(
                     resource.RUSAGE_SELF).ru_maxrss if resource else None),
                 "child_max_rss_platform_units": (resource.getrusage(
                     resource.RUSAGE_CHILDREN).ru_maxrss if resource else None),
                 "claim": "retained execution cost; no memory, speed, or utility advantage claim"},
    }
    _write(out / "validation.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--artifact-metadata", type=Path, required=True)
    parser.add_argument("--full-artifact-metadata", type=Path, required=True)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        validate(args.archive, args.artifact_metadata, args.full_artifact_metadata,
                 args.run_metadata, args.out)
    except Exception as error:
        args.out.mkdir(parents=True, exist_ok=True)
        _write(args.out / "failure.json", {"type": type(error).__name__,
                                            "message": str(error)})
        raise


if __name__ == "__main__":
    main()
