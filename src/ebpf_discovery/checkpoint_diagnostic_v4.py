"""Actions-only toolchain diagnostic from one immutable v4 training checkpoint.

This reuses the complete frozen training prefix without application traffic.  It
is not a campaign resume, a completed cell, or evidence about guest capacity.
"""
from __future__ import annotations

from collections import Counter
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import time

from .replay_qualification_v4 import (
    digest, file_manifest, relocate_index, verified_binaries,
)
from .runtime import Context, write_json
from .store_v3 import ObservationStore
from .toolchain_v4 import Toolchain


SOURCE_RUN_ID = 40718665137
SOURCE_ARTIFACT_ID = 12830934533
SOURCE_ARTIFACT_NAME = "training-v4-otel_demo-full-6-40718665137"
SOURCE_ARTIFACT_DIGEST = "sha256:47def427dfe5dd7509b0d31b3198affef8dc25dabd69a2c6e551824d4b0f0a1c"
SOURCE_MANIFEST_SHA256 = "1947882e9a8ce92732ca31e14907afde9c5def9dd33050658b2e66440b14e765"


def _read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_artifact_identity(source: dict) -> None:
    expected = {
        "run_id": SOURCE_RUN_ID, "artifact_id": SOURCE_ARTIFACT_ID,
        "artifact_name": SOURCE_ARTIFACT_NAME,
        "artifact_digest": SOURCE_ARTIFACT_DIGEST,
    }
    if any(source.get(key) != value for key, value in expected.items()):
        raise ValueError("checkpoint Actions artifact identity or digest mismatch")
    if (source.get("expired") is True
            or not re.fullmatch(r"[0-9a-f]{40}", str(source.get("run_sha", "")))):
        raise ValueError("checkpoint source commit or availability is invalid")


def validate_checkpoint_manifest(original: Path, source: dict) -> dict:
    """Verify the ready binding and every byte recorded by the checkpoint."""
    original = Path(original).resolve()
    validate_artifact_identity(source)
    manifest_path, ready_path = original/"manifest.json", original/"ready.json"
    if digest(manifest_path) != SOURCE_MANIFEST_SHA256:
        raise ValueError("checkpoint manifest differs from the admitted immutable digest")
    manifest, ready = _read(manifest_path), _read(ready_path)
    identity = {"run_id": str(SOURCE_RUN_ID), "commit": source["run_sha"],
                "system": "otel_demo", "mode": "full", "seed": 6}
    if (manifest.get("schema_version") != "v4-training-prefix-checkpoint"
            or manifest.get("status") != "partial_training_capture_only; no forecast or completed cell"
            or any(str(manifest.get("identity", {}).get(key)) != str(value)
                   for key, value in identity.items())):
        raise ValueError("checkpoint manifest identity or partial-training status mismatch")
    if (ready.get("schema_version") != "v4-training-prefix-checkpoint-ready"
            or ready.get("status") != "training_checkpoint_ready"
            or ready.get("manifest_sha256") != SOURCE_MANIFEST_SHA256
            or any(str(ready.get(key)) != str(value) for key, value in identity.items())):
        raise ValueError("checkpoint ready marker does not bind the admitted manifest")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("checkpoint manifest has no frozen file census")
    verified = {}
    for relative, record in sorted(files.items()):
        path = original/relative
        if (not isinstance(relative, str) or Path(relative).is_absolute() or ".." in Path(relative).parts
                or not isinstance(record, dict) or record.get("relative_path") != relative
                or path.is_symlink() or not path.is_file()):
            raise ValueError(f"invalid checkpoint file record: {relative}")
        actual = {"bytes": path.stat().st_size, "sha256": digest(path)}
        if actual != {"bytes": record.get("bytes"), "sha256": record.get("sha256")}:
            raise ValueError(f"checkpoint file digest or length mismatch: {relative}")
        verified[relative] = actual
    actual_files = {path.relative_to(original).as_posix() for path in original.rglob("*") if path.is_file()}
    expected_files = set(files) | {"manifest.json", "ready.json"}
    if actual_files != expected_files:
        raise ValueError("checkpoint artifact contains unmanifested or missing files")
    return {"identity": identity, "manifest_sha256": SOURCE_MANIFEST_SHA256,
            "verified_files": verified, "verified_file_count": len(verified),
            "source_cutoff_rule": manifest.get("source_cutoff_rule"),
            "new_application_traffic": manifest.get("new_application_traffic")}


def validate_training_prefix(original: Path) -> tuple[list[dict], dict]:
    plans = _read(Path(original)/"plans.json")
    blocks = _read(Path(original)/"blocks.json")
    census = _read(Path(original)/"census.json")
    records = _read(Path(original)/"external.json")
    expected = Counter({("class_train", "11"): 600,
                        **{("calibration", state): 6000 for state in ("11", "10", "01", "00")}})
    plan_counts = Counter((row.get("phase"), row.get("state")) for row in plans)
    if len(plans) != 24600 or plan_counts != expected:
        raise ValueError("checkpoint plans differ from exact 600 + 4x6000 training design")
    attempt_ids = [row.get("attempt_id") for row in plans]
    if any(not isinstance(value, str) or not value for value in attempt_ids) or len(set(attempt_ids)) != 24600:
        raise ValueError("checkpoint training attempt IDs are missing or duplicate")
    block_counts = {(row.get("phase"), row.get("state")): row.get("attempts") for row in blocks}
    if (len(blocks) != 5 or block_counts != expected
            or any(row.get("completed_requests") != row.get("attempts") for row in blocks)):
        raise ValueError("checkpoint completed blocks differ from exact training design")
    census_counts = Counter((row.get("phase"), row.get("state")) for row in census)
    record_counts = Counter((row.get("phase"), row.get("state")) for row in records)
    if len(census) != 24600 or census_counts != expected or len(records) != 24600 or record_counts != expected:
        raise ValueError("checkpoint census or external records differ from completed training plans")
    census_ids = [row.get("attempt_key") for row in census]
    record_ids = [row.get("attempt_id") for row in records]
    if (any(not isinstance(value, str) or not value for value in census_ids + record_ids)
            or len(set(census_ids)) != 24600 or set(record_ids) != set(attempt_ids)):
        raise ValueError("checkpoint census or external attempt identities are missing, duplicate, or mismatched")
    return plans, {"plans": len(plans), "blocks": len(blocks), "census": len(census),
                   "external_records": len(records),
                   "phase_state_counts": {f"{phase}:{state}": count
                                          for (phase, state), count in sorted(expected.items())}}


def diagnose(original: Path, out: Path, source: dict) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("v4 training-checkpoint diagnostic is permitted only in GitHub Actions")
    original, out = Path(original).resolve(), Path(out).resolve()
    if out == original or out in original.parents or original in out.parents:
        raise ValueError("diagnostic output and immutable checkpoint must be separate")
    if out.exists() and any(out.iterdir()):
        raise ValueError("diagnostic output must be empty")
    out.mkdir(parents=True, exist_ok=True)
    status = {"schema_version": "v4-training-checkpoint-diagnostic",
              "status": "diagnostic_started", "source_run_id": SOURCE_RUN_ID,
              "source_artifact_id": SOURCE_ARTIFACT_ID, "started_ns": time.time_ns(),
              "completed_campaign_cell": False, "new_application_traffic": False,
              "interpretation": "immutable full-training-prefix toolchain diagnostic only"}
    write_json(out/"status.json", status)
    original_files = None
    try:
        original_files = file_manifest(original)
        manifest_proof = validate_checkpoint_manifest(original, source)
        plans, census_proof = validate_training_prefix(original)
        write_json(out/"checkpoint-validation.json", {
            "source_artifact": source, "manifest": manifest_proof, "training": census_proof,
            "artifact_digest_basis": "GitHub Actions API immutable artifact digest",
            "full_checkpoint_rehashed_before_tools": True,
        })
        binary_dir, old_root, binary_proof = verified_binaries(original, out)
        index_proof = relocate_index(original, out, old_root)
        shutil.copy2(original/"deployment.json", out/"deployment.json")
        ctx = Context(out, "full", 6)
        ctx.deployment_dir = original/"deployment"
        old_bin = os.environ.get("PBS_BIN")
        os.environ["PBS_BIN"] = str(binary_dir.resolve())
        store = ObservationStore(out/"observation-index.sqlite", same_trace_parents=True)
        try:
            declaration = importlib.import_module("systems.otel_demo.experiment_v4")
            forecasts = Toolchain(ctx, "otel_demo", store, declaration).forecast(plans)
        finally:
            store.close()
            if old_bin is None:
                os.environ.pop("PBS_BIN", None)
            else:
                os.environ["PBS_BIN"] = old_bin
        write_json(out/"diagnostic-provenance.json", {
            "source_artifact": source, "manifest": manifest_proof,
            "training": census_proof, "binary_evidence": binary_proof,
            "index": index_proof, "forecast_branches": {
                source_name: {variant: {operation: {"available": bool(value.get("available")),
                    "reason": value.get("reason")} for operation, value in operations.items()}
                    for variant, operations in variants.items()}
                for source_name, variants in forecasts.items()},
            "completed_campaign_cell": False, "campaign_resume": False,
            "new_application_traffic": False,
        })
        status["status"] = "diagnostic_complete"
        return status
    except BaseException as error:
        status.update(status="diagnostic_technical_failure", error=repr(error))
        raise
    finally:
        status["ended_ns"] = time.time_ns()
        try:
            status["immutable_checkpoint_unchanged"] = (
                file_manifest(original) == original_files if original_files is not None else None)
        except Exception as error:
            status["immutable_checkpoint_unchanged"] = False
            status["checkpoint_rehash_error"] = repr(error)
        if status["immutable_checkpoint_unchanged"] is False:
            status.update(status="diagnostic_technical_failure",
                          error="immutable checkpoint changed or could not be rehashed")
        write_json(out/"status.json", status)
        if status["immutable_checkpoint_unchanged"] is False:
            raise RuntimeError("immutable checkpoint changed during diagnostic")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    diagnose(args.original, args.out, _read(args.source))


if __name__ == "__main__":
    main()
