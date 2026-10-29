"""Actions-only toolchain diagnostic from one immutable v4 training checkpoint.

This reuses the complete frozen training prefix without application traffic.  It
is not a campaign resume, a completed cell, or evidence about guest capacity.
"""
from __future__ import annotations

from collections import Counter
import hashlib
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
from .toolchain_v4 import BERING_120_PINS, ORIGINAL_PINS, Toolchain
from .bering_v4 import child_go_environment


SOURCE_RUN_ID = 40718665137
SOURCE_ARTIFACT_ID = 12830934533
SOURCE_ARTIFACT_NAME = "training-v4-otel_demo-full-6-40718665137"
SOURCE_ARTIFACT_DIGEST = "sha256:47def427dfe5dd7509b0d31b3198affef8dc25dabd69a2c6e551824d4b0f0a1c"
SOURCE_MANIFEST_SHA256 = "1947882e9a8ce92732ca31e14907afde9c5def9dd33050658b2e66440b14e765"

DEFAULT_PROFILE = "original-40718665137"
LARGE_GC_PROFILE = "full6-40754529169-gomemlimit12g"
DSB_GC_PROFILE = "full6-40731158179-dsb-gomemlimit12g"
DSB_SHUTDOWN_PROFILE = "full6-40731158179-dsb-bering120-on-shutdown"
PROFILES = {
    DEFAULT_PROFILE: {
        "system": "otel_demo",
        "run_id": SOURCE_RUN_ID,
        "artifact_id": SOURCE_ARTIFACT_ID,
        "artifact_name": SOURCE_ARTIFACT_NAME,
        "artifact_digest": SOURCE_ARTIFACT_DIGEST,
        "manifest_sha256": SOURCE_MANIFEST_SHA256,
        "commit": "ea2e278e50f64bd50597c243d84f834be1b92576",
        "bering_child_go_environment": {},
    },
    LARGE_GC_PROFILE: {
        "system": "otel_demo",
        "run_id": 40754529169,
        "artifact_id": 12847933267,
        "artifact_name": "training-v4-otel_demo-full-6-40754529169",
        "artifact_digest": "sha256:ba0289fd1e0cefd4be96cfbf0a0ac4a335db2ef4f748de4b0ffa63aa00c2c422",
        "manifest_sha256": "b90d303797e4285d16659b4515195b0fc58276d8d4200ec6a9fa9eae070e333c",
        "commit": "72133c00df3f7e4150a3f737dee33e4bee12527d",
        "bering_child_go_environment": {"GOMEMLIMIT": "12GiB", "GODEBUG": "gctrace=1"},
    },
    DSB_GC_PROFILE: {
        "system": "deathstarbench",
        "run_id": 40731158179,
        "artifact_id": 12843610949,
        "artifact_name": "training-v4-deathstarbench-full-6-40731158179",
        "artifact_digest": "sha256:8689c137f482d5ffef5a184762c7f212a5d35f22ea6d014b0d06984788cafed0",
        "manifest_sha256": "8a518c3edbfb4f6904ece3b344c85f211cd55bd909cd0629f4a5f29303948235",
        "commit": "3e708879889eac8a238027a4640466fc8a76eca5",
        "bering_child_go_environment": {"GOMEMLIMIT": "12GiB", "GODEBUG": "gctrace=1"},
    },
}
PROFILES[DSB_SHUTDOWN_PROFILE] = {**PROFILES[DSB_GC_PROFILE],
    "replacement_pins": dict(BERING_120_PINS), "publication_mode": "on_shutdown"}


def runtime_binaries(original: Path, out: Path, profile: dict,
                     replacement_root: Path | None = None):
    """Verify original binaries first, then an explicitly separate released-source build."""
    original_bin, old_root, original_proof = verified_binaries(
        original, out/"original-toolchain", expected_pins=ORIGINAL_PINS)
    original_manifest = original/"toolchain-build"/"toolchain-build.json"
    shutil.copy2(original_manifest, out/"original-toolchain"/"toolchain-build.json")
    proof = {"original": {"pins": ORIGINAL_PINS, "binaries": original_proof,
        "build_manifest_sha256": digest(original_manifest), "publication_mode": "windowed"}}
    replacement_pins = profile.get("replacement_pins")
    if replacement_pins is None:
        if replacement_root is not None:
            raise ValueError("historical diagnostic does not accept a replacement toolchain")
        proof["effective"] = dict(proof["original"])
        return original_bin, old_root, proof
    if replacement_root is None:
        raise ValueError("this named diagnostic requires a separate replacement toolchain build")
    replacement_root = Path(replacement_root).resolve()
    for other in (original.resolve(), out.resolve()):
        if replacement_root == other or replacement_root in other.parents or other in replacement_root.parents:
            raise ValueError("replacement toolchain build must be separate from source and output")
    effective = out/"effective-toolchain"
    binary_dir, build_root, binary_proof = verified_binaries(
        replacement_root, effective, expected_pins=replacement_pins)
    if build_root != replacement_root:
        raise ValueError("replacement manifest must identify this Actions build location")
    build = replacement_root/"toolchain-build"
    manifest = _read(build/"toolchain-build.json")
    compiler_proof = []
    for row in manifest["binaries"]:
        compiler = Path(row["go_binary"]).resolve()
        if (compiler != build/"go"/row["go_version"]/"bin"/"go"
                or not compiler.is_file() or compiler.is_symlink()):
            raise ValueError("replacement compiler path or file mismatch")
        compiler_proof.append({"tool": row["name"], "version": row["go_version"],
            "path": str(compiler), "bytes": compiler.stat().st_size, "sha256": digest(compiler)})
    archive_proof = []
    for row in manifest["go_archives"]:
        archive = Path(row["path"]).resolve()
        if archive.parent != build/"go" or archive.is_symlink() or not archive.is_file():
            raise ValueError("replacement compiler archive path mismatch")
        actual = digest(archive)
        if actual != row["sha256"]:
            raise ValueError("replacement compiler archive digest mismatch")
        archive_proof.append({**row, "bytes": archive.stat().st_size})
    expected_archives = {str(build/"go"/f"go{row['go_version']}.linux-amd64.tar.gz")
                         for row in manifest["binaries"]}
    if {row["path"] for row in archive_proof} != expected_archives or len(archive_proof) != len(expected_archives):
        raise ValueError("replacement compiler archive census mismatch")
    # Preserve measured build commands, compiler identity and logs, without
    # pretending these source builds are byte-identical to release binaries.
    for name in ("toolchain-build.json", "builds.tsv", "pins.tsv"):
        shutil.copy2(build/name, effective/name)
    shutil.copytree(build/"logs", effective/"logs")
    (effective/"go-metadata").mkdir()
    for path in (build/"go").glob("go*.json"):
        shutil.copy2(path, effective/"go-metadata"/path.name)
    proof["effective"] = {"pins": replacement_pins, "binaries": binary_proof,
        "build_manifest_sha256": digest(build/"toolchain-build.json"),
        "publication_mode": profile["publication_mode"],
        "compilers": compiler_proof, "compiler_archives": archive_proof,
        "binary_basis": "Actions source build of exact released commits; not published-asset byte identity"}
    return binary_dir, old_root, proof


def _profile(name=DEFAULT_PROFILE):
    try:
        return PROFILES[name]
    except KeyError as error:
        raise ValueError(f"unknown immutable diagnostic profile: {name}") from error


def _read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_artifact_identity(source: dict, profile_name=DEFAULT_PROFILE) -> None:
    profile = _profile(profile_name)
    expected = {
        "run_id": profile["run_id"], "artifact_id": profile["artifact_id"],
        "artifact_name": profile["artifact_name"],
        "artifact_digest": profile["artifact_digest"],
    }
    if any(source.get(key) != value for key, value in expected.items()):
        raise ValueError("checkpoint Actions artifact identity or digest mismatch")
    if (source.get("expired") is True
            or not re.fullmatch(r"[0-9a-f]{40}", str(source.get("run_sha", "")))):
        raise ValueError("checkpoint source commit or availability is invalid")


def validate_checkpoint_manifest(original: Path, source: dict, profile_name=DEFAULT_PROFILE) -> dict:
    """Verify the ready binding and every byte recorded by the checkpoint."""
    original = Path(original).resolve()
    profile = _profile(profile_name)
    validate_artifact_identity(source, profile_name)
    manifest_path, ready_path = original/"manifest.json", original/"ready.json"
    if digest(manifest_path) != profile["manifest_sha256"]:
        raise ValueError("checkpoint manifest differs from the admitted immutable digest")
    manifest, ready = _read(manifest_path), _read(ready_path)
    identity = {"run_id": str(profile["run_id"]), "commit": profile["commit"],
                "system": profile["system"], "mode": "full", "seed": 6}
    if source["run_sha"] != profile["commit"]:
        raise ValueError("checkpoint source commit differs from the named immutable profile")
    if (manifest.get("schema_version") != "v4-training-prefix-checkpoint"
            or manifest.get("status") != "partial_training_capture_only; no forecast or completed cell"
            or any(str(manifest.get("identity", {}).get(key)) != str(value)
                   for key, value in identity.items())):
        raise ValueError("checkpoint manifest identity or partial-training status mismatch")
    if (ready.get("schema_version") != "v4-training-prefix-checkpoint-ready"
            or ready.get("status") != "training_checkpoint_ready"
            or ready.get("manifest_sha256") != profile["manifest_sha256"]
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
    return {"identity": identity, "manifest_sha256": profile["manifest_sha256"],
            "verified_files": verified, "verified_file_count": len(verified),
            "source_cutoff_rule": manifest.get("source_cutoff_rule"),
            "new_application_traffic": manifest.get("new_application_traffic")}


def validate_training_prefix(original: Path) -> tuple[list[dict], dict]:
    plans = _read(Path(original)/"plans.json")
    blocks = _read(Path(original)/"blocks.json")
    census = _read(Path(original)/"census.json")
    records = _read(Path(original)/"external.json")
    preparation = _read(Path(original)/"preparation-operations.json")
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
    primary_records = [row for row in records if row.get("phase") in ("class_train", "calibration")]
    preparation_records = [row for row in records if row.get("phase") == "preparation"]
    other_records = [row for row in records
                     if row.get("phase") not in ("class_train", "calibration", "preparation")]
    record_counts = Counter((row.get("phase"), row.get("state")) for row in primary_records)
    if len(census) != 24600 or census_counts != expected or len(primary_records) != 24600 or record_counts != expected:
        raise ValueError("checkpoint census or external records differ from completed training plans")
    record_ids = [row.get("attempt_id") for row in primary_records]
    if (any(not isinstance(value, str) or not value for value in record_ids)
            or set(record_ids) != set(attempt_ids) or len(set(record_ids)) != 24600):
        raise ValueError("checkpoint census or external attempt identities are missing, duplicate, or mismatched")
    records_by_id = {row["attempt_id"]: row for row in primary_records}
    expected_census = {}
    for plan in plans:
        record = records_by_id[plan["attempt_id"]]
        planned = [step.get("request_id") for step in plan.get("http_steps", [])]
        dispatched = [step.get("request_id") for step in record.get("http_steps", [])]
        for request_id in dispatched:
            if not isinstance(request_id, str) or not request_id:
                raise ValueError("checkpoint external record has an invalid dispatched request identity")
            if request_id not in planned:
                raise ValueError("checkpoint dispatched request identity is absent from the plan")
        if (record.get("phase") != plan.get("phase")
                or record.get("state") != plan.get("state")):
            raise ValueError("checkpoint external record differs from its planned attempt")
        key = hashlib.sha256(plan["attempt_id"].encode()).hexdigest()
        expected_census[key] = {"attempt_key": key, "step_ids": dispatched,
                                "phase": plan.get("phase"), "state": plan.get("state")}
    actual_census = {row.get("attempt_key"): row for row in census
                     if isinstance(row.get("attempt_key"), str) and row.get("attempt_key")}
    if len(actual_census) != 24600 or actual_census != expected_census:
        raise ValueError("checkpoint census or external attempt identities are missing, duplicate, or mismatched")
    preparation_ids = [row.get("attempt_id") for row in preparation_records]
    retained_preparation_ids = [row.get("attempt_id") for row in preparation]
    if (other_records or len(preparation_records) != len(preparation)
            or any(not isinstance(value, str) or not value
                   for value in preparation_ids + retained_preparation_ids)
            or len(set(preparation_ids)) != len(preparation_ids)
            or set(preparation_ids) & set(attempt_ids)
            or {row["attempt_id"]: row for row in preparation_records}
               != {row["attempt_id"]: row for row in preparation}):
        raise ValueError("checkpoint preparation records differ from preparation-operations evidence")
    return plans, {"plans": len(plans), "blocks": len(blocks), "census": len(census),
                   "primary_external_records": len(primary_records),
                   "preparation_external_records": len(preparation_records),
                   "all_external_records": len(records),
                   "phase_state_counts": {f"{phase}:{state}": count
                                          for (phase, state), count in sorted(expected.items())}}


def diagnose(original: Path, out: Path, source: dict, profile_name=DEFAULT_PROFILE,
             replacement_root: Path | None = None) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("v4 training-checkpoint diagnostic is permitted only in GitHub Actions")
    profile = _profile(profile_name)
    original, out = Path(original).resolve(), Path(out).resolve()
    if out == original or out in original.parents or original in out.parents:
        raise ValueError("diagnostic output and immutable checkpoint must be separate")
    if out.exists() and any(out.iterdir()):
        raise ValueError("diagnostic output must be empty")
    out.mkdir(parents=True, exist_ok=True)
    status = {"schema_version": "v4-training-checkpoint-diagnostic",
              "status": "diagnostic_started", "profile": profile_name,
              "system": profile["system"],
              "source_run_id": profile["run_id"],
              "source_artifact_id": profile["artifact_id"], "started_ns": time.time_ns(),
              "completed_campaign_cell": False, "new_application_traffic": False,
              "interpretation": "immutable full-training-prefix toolchain diagnostic only"}
    write_json(out/"status.json", status)
    original_files = None
    try:
        original_files = file_manifest(original)
        manifest_proof = validate_checkpoint_manifest(original, source, profile_name)
        plans, census_proof = validate_training_prefix(original)
        write_json(out/"checkpoint-validation.json", {
            "source_artifact": source, "manifest": manifest_proof, "training": census_proof,
            "artifact_digest_basis": "GitHub Actions API immutable artifact digest",
            "full_checkpoint_rehashed_before_tools": True,
        })
        binary_dir, old_root, toolchain_proof = runtime_binaries(
            original, out, profile, replacement_root)
        write_json(out/"toolchain-provenance.json", toolchain_proof)
        index_proof = relocate_index(original, out, old_root)
        shutil.copy2(original/"deployment.json", out/"deployment.json")
        ctx = Context(out, "full", 6)
        ctx.deployment_dir = original/"deployment"
        old_bin = os.environ.get("PBS_BIN")
        os.environ["PBS_BIN"] = str(binary_dir.resolve())
        store = ObservationStore(out/"observation-index.sqlite", same_trace_parents=True)
        try:
            declaration = importlib.import_module(f"systems.{profile['system']}.experiment_v4")
            with child_go_environment(profile["bering_child_go_environment"]):
                forecasts = Toolchain(ctx, profile["system"], store, declaration,
                    tool_pins=toolchain_proof["effective"]["pins"],
                    publication_mode=toolchain_proof["effective"]["publication_mode"],
                    native_jaeger_envelope="per_trace").forecast(plans)
        finally:
            store.close()
            if old_bin is None:
                os.environ.pop("PBS_BIN", None)
            else:
                os.environ["PBS_BIN"] = old_bin
        write_json(out/"diagnostic-provenance.json", {
            "source_artifact": source, "manifest": manifest_proof,
            "training": census_proof, "binary_evidence": toolchain_proof["effective"]["binaries"],
            "toolchain": toolchain_proof,
            "index": index_proof, "forecast_branches": {
                source_name: {variant: {operation: {"available": bool(value.get("available")),
                    "reason": value.get("reason")} for operation, value in operations.items()}
                    for variant, operations in variants.items()}
                for source_name, variants in forecasts.items()},
            "completed_campaign_cell": False, "campaign_resume": False,
            "new_application_traffic": False,
            "profile": profile_name,
            "bering_child_go_environment": {
                "requested": profile["bering_child_go_environment"],
                "scope": "Bering child only; Procrustes and Sheaft environment unchanged",
                "gogc_override": False,
            },
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
    parser.add_argument("--profile", choices=sorted(PROFILES), default=DEFAULT_PROFILE)
    parser.add_argument("--replacement-root", type=Path)
    args = parser.parse_args()
    diagnose(args.original, args.out, _read(args.source), args.profile, args.replacement_root)


if __name__ == "__main__":
    main()
