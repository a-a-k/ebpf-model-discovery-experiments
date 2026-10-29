"""Compare streaming preprocessing with its pinned implementation on one saved packet."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import stat
import subprocess
import sys
import time
import traceback
import zipfile


REPOSITORY = "a-a-k/ebpf-model-discovery-experiments"
RUN_ID = 40916651613
SOURCE_HEAD = "5457d14ddd20307ec92c0af9767d49e0538158b2"
ARTIFACT_ID = 12917472672
ARTIFACT_NAME = "campaign-v5-coroot-smoke-deathstarbench-full-6-40916651613"
ARTIFACT_DIGEST = "sha256:7ae5939f65873e43cbbdde394379c08d1883072ee7a6db7286884915d9ed9fae"
ARTIFACT_SIZE = 37_522_162
ORIGINAL_COMMIT = "fb339581d28a2ae9e5e8f23c90c604cccb15bcfa"
SOURCE_FILES = (
    "src/ebpf_discovery/supplied_alias_v5.py",
    "src/ebpf_discovery/store_v5.py",
)
FIXED_MEMBERS = {
    "status.json",
    "observation-index.sqlite",
    "observations/collector.json",
    "runtime-identity-v5/inventory-training.json",
    "runtime-identity-v5/supplied-service-aliases-training.json",
}
CORE_KEYS = (
    "schema", "origin", "aliases", "conflicts", "occurrence_proofs",
    "scoped_digest_aliases", "verified_scoped_digest_roles",
    "unique_verified_segments", "receiver_segments_reverified",
    "same_table_all_sources_and_direct_baseline", "physical_identity_inferred",
)


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n").encode()


def _safe(info: zipfile.ZipInfo) -> bool:
    name, parts = info.filename, PurePosixPath(info.filename).parts
    return bool(name and "\\" not in name and not PurePosixPath(name).is_absolute()
                and ".." not in parts and not stat.S_ISLNK(info.external_attr >> 16))


def _verify_source(archive: Path, artifact: dict, run: dict) -> dict:
    expected = {"id": ARTIFACT_ID, "name": ARTIFACT_NAME,
                "size_in_bytes": ARTIFACT_SIZE, "digest": ARTIFACT_DIGEST,
                "expired": False}
    if {key: artifact.get(key) for key in expected} != expected:
        raise ValueError("artifact API identity mismatch")
    workflow = artifact.get("workflow_run") or {}
    if (workflow.get("id") != RUN_ID or workflow.get("head_sha") != SOURCE_HEAD
            or run.get("id") != RUN_ID or run.get("head_sha") != SOURCE_HEAD
            or run.get("repository", {}).get("full_name") != REPOSITORY
            or run.get("conclusion") != "success"):
        raise ValueError("workflow run API identity mismatch")
    digest, size = "sha256:" + _sha(archive), archive.stat().st_size
    if digest != ARTIFACT_DIGEST or size != ARTIFACT_SIZE:
        raise ValueError("received full artifact differs from API identity")
    return {"repository": REPOSITORY, "run_id": RUN_ID, "head_sha": SOURCE_HEAD,
            "artifact_id": ARTIFACT_ID, "artifact_name": ARTIFACT_NAME,
            "api_digest": ARTIFACT_DIGEST, "computed_digest": digest,
            "api_size_in_bytes": ARTIFACT_SIZE, "received_bytes": size}


def _wanted(name: str) -> bool:
    return (name in FIXED_MEMBERS or name.startswith("observations/")
            or name.startswith("native/")
            or name.startswith("runtime-identity-v5/supplied-service-alias-admission-training"))


def _extract(archive: Path, destination: Path) -> list[dict]:
    destination.mkdir(parents=True, exist_ok=False)
    proofs = []
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries) or not all(
                _safe(entry) for entry in entries):
            raise ValueError("artifact ZIP names are duplicate or unsafe")
        names = {entry.filename for entry in entries}
        if not FIXED_MEMBERS <= names:
            raise ValueError("artifact lacks a fixed required member")
        for entry in entries:
            if entry.is_dir() or not _wanted(entry.filename):
                continue
            body = bundle.read(entry)  # CRC is verified by zipfile.
            target = (destination / PurePosixPath(entry.filename)).resolve()
            target.relative_to(destination.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            proofs.append({"path": entry.filename, "bytes": len(body),
                           "sha256": hashlib.sha256(body).hexdigest(),
                           "zip_crc32": f"{entry.CRC:08x}"})
    return proofs


def _git_sources(destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=False)
    proof = {}
    for relative in SOURCE_FILES:
        body = subprocess.run(
            ["git", "show", f"{ORIGINAL_COMMIT}:{relative}"], check=True,
            stdout=subprocess.PIPE).stdout
        target = destination / Path(relative).name
        target.write_bytes(body)
        proof[relative] = {"sha256": hashlib.sha256(body).hexdigest(),
                           "bytes": len(body)}
    return proof


def _load_original(path: Path, name: str):
    module_name = "ebpf_discovery._saved_memory_validation_" + name
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pinned source: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _retained_evidence_path(raw_file: str) -> Path:
    parts = Path(raw_file).parts
    roots = [parts.index(name) for name in ("observations", "native") if name in parts]
    if not roots:
        raise ValueError(f"provenance path has no retained evidence root: {raw_file}")
    return Path(*parts[min(roots):])


def _rebase_provenance(db: sqlite3.Connection, root: Path) -> dict:
    mappings = {}
    for (raw_file,) in db.execute("SELECT DISTINCT raw_file FROM observation_provenance"):
        relative = _retained_evidence_path(raw_file)
        target = (root / relative).resolve()
        target.relative_to(root.resolve())
        if not target.is_file():
            raise ValueError(f"retained provenance dependency is absent: {relative}")
        mappings[raw_file] = str(target)
    for old, new in mappings.items():
        db.execute("UPDATE observation_provenance SET raw_file=? WHERE raw_file=?", (new, old))
    db.commit()
    return {"paths": len(mappings), "policy": "same observations-relative rebase per copy"}


def _table_proof(db: sqlite3.Connection, table: str) -> dict:
    columns = [row[1] for row in db.execute(f"PRAGMA table_info({table})")]
    if not columns:
        raise ValueError(f"missing table: {table}")
    digest, count = hashlib.sha256(), 0
    for row in db.execute(f"SELECT * FROM {table} ORDER BY 1"):
        digest.update(_canonical(dict(zip(columns, row))))
        count += 1
    return {"table": table, "rows": count, "sha256": digest.hexdigest(),
            "columns": columns}


def _peak_rss_kib() -> int | None:
    try:
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except ImportError:  # The saved validation runs on Linux; keep --help portable.
        return None


def _worker(args) -> None:
    started = time.monotonic()
    root, output = args.root.resolve(), args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.variant == "original":
        supplied = _load_original(args.original_sources / "supplied_alias_v5.py", "supplied")
        store_module = _load_original(args.original_sources / "store_v5.py", "store")
    else:
        from ebpf_discovery import supplied_alias_v5 as supplied
        from ebpf_discovery import store_v5 as store_module

    status, collector = _json(root / "status.json"), _json(root / "observations/collector.json")
    if (status.get("system"), status.get("mode"), status.get("seed"),
            status.get("collector"), status.get("smoke")) != (
            "deathstarbench", "full", 6, "coroot", True):
        raise ValueError("saved cell identity differs from fixed validation source")
    if collector.get("collector") != "coroot":
        raise ValueError("saved collector identity differs from fixed validation source")

    db_path = root / "observation-index.sqlite"
    store = store_module.ObservationStoreV5(db_path, same_trace_parents=True)
    rebase = _rebase_provenance(store.db, root)
    store.db.execute("DELETE FROM supplied_logical_alias_projection")
    store.db.execute("DELETE FROM runtime_identity_projection")
    store.db.commit()

    inventory_path = root / "runtime-identity-v5/inventory-training.json"
    inventory = _json(inventory_path)
    inventory_proof = {"path": "runtime-identity-v5/inventory-training.json",
                       "sha256": _sha(inventory_path), "bytes": inventory_path.stat().st_size}
    projection_path = output / "projection-training.jsonl"
    runtime_result = store.apply_runtime_identity(
        inventory, projection_path, inventory_proof=inventory_proof, stage="training")

    table_path = root / "runtime-identity-v5/supplied-service-aliases-training.json"
    table = _json(table_path)
    admission = supplied.admit_observed(
        store, table, expected_source_prefix="ebpf-coroot")
    admission_core = supplied.admission_core(admission)
    (output / "admission-core.json").write_bytes(_canonical(admission_core))
    alias_result = store.apply_supplied_logical_aliases(admission)
    preprocessing_elapsed = time.monotonic() - started
    preprocessing_peak = _peak_rss_kib()

    proof_started = time.monotonic()
    runtime_table = _table_proof(store.db, "runtime_identity_projection")
    alias_table = _table_proof(store.db, "supplied_logical_alias_projection")
    spans = _table_proof(store.db, "spans")
    store.db.close()
    report = {
        "variant": args.variant,
        "runtime_result": runtime_result,
        "alias_result": alias_result,
        "provenance_rebase": rebase,
        "projection_jsonl": {"bytes": projection_path.stat().st_size,
                             "sha256": _sha(projection_path)},
        "admission_core": {"bytes": (output / "admission-core.json").stat().st_size,
                           "sha256": _sha(output / "admission-core.json")},
        "tables": {"runtime_identity_projection": runtime_table,
                   "supplied_logical_alias_projection": alias_table, "spans": spans},
        "cost": {"preprocessing_elapsed_seconds": preprocessing_elapsed,
                 "peak_rss_kib_after_preprocessing": preprocessing_peak,
                 "proof_elapsed_seconds": time.monotonic() - proof_started},
    }
    _write(output / "worker-report.json", report)


def _run_worker(script: Path, variant: str, root: Path, sources: Path, output: Path) -> dict:
    started = time.monotonic()
    command = [sys.executable, str(script), "--worker", "--variant", variant,
               "--root", str(root), "--original-sources", str(sources),
               "--out", str(output)]
    completed = subprocess.run(command, text=True, capture_output=True)
    invocation = {"argv": command, "returncode": completed.returncode,
                  "elapsed_seconds": time.monotonic() - started,
                  "stdout": completed.stdout, "stderr": completed.stderr}
    _write(output.parent / f"{variant}-invocation.json", invocation)
    if completed.returncode:
        raise RuntimeError(f"{variant} preprocessing failed")
    return _json(output / "worker-report.json")


def validate(args) -> dict:
    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    _write(out / "started.json", {"schema": "memory-streaming-validation-v5",
                                  "started_ns": time.time_ns()})
    source = _verify_source(args.archive, _json(args.artifact_metadata),
                            _json(args.run_metadata))
    selected = out.parent / "selected-input"
    member_proofs = _extract(args.archive, selected)
    original_sources = out.parent / "original-sources"
    original_source_proofs = _git_sources(original_sources)
    current_source_proofs = {
        relative: {"sha256": _sha(Path(relative)), "bytes": Path(relative).stat().st_size}
        for relative in SOURCE_FILES}
    if any(original_source_proofs[path]["sha256"] == current_source_proofs[path]["sha256"]
           for path in SOURCE_FILES):
        raise ValueError("integrated source does not contain both reviewed streaming changes")
    checked_out_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, text=True,
        stdout=subprocess.PIPE).stdout.strip()
    if os.environ.get("GITHUB_SHA") and checked_out_head != os.environ["GITHUB_SHA"]:
        raise ValueError("checked-out validation source differs from GITHUB_SHA")

    workspaces = out.parent / "workspaces"
    original_root, current_root = workspaces / "original", workspaces / "current"
    shutil.copytree(selected, original_root)
    shutil.copytree(selected, current_root)
    original_report = _run_worker(Path(__file__).resolve(), "original", original_root,
                                  original_sources, out / "original")
    current_report = _run_worker(Path(__file__).resolve(), "current", current_root,
                                 original_sources, out / "current")

    exact_files = ("projection-training.jsonl", "admission-core.json")
    comparisons = {}
    for name in exact_files:
        old, new = out / "original" / name, out / "current" / name
        comparisons[name] = {"identical_bytes": old.read_bytes() == new.read_bytes(),
                             "original_sha256": _sha(old), "current_sha256": _sha(new),
                             "original_bytes": old.stat().st_size,
                             "current_bytes": new.stat().st_size}
    tables = {}
    for name in ("runtime_identity_projection", "supplied_logical_alias_projection", "spans"):
        old = original_report["tables"][name]
        new = current_report["tables"][name]
        tables[name] = {"identical": old == new, "original": old, "current": new}
    if not all(row["identical_bytes"] for row in comparisons.values()) or not all(
            row["identical"] for row in tables.values()):
        raise ValueError("streaming preprocessing changed saved semantic outputs")
    if "sha256:" + _sha(args.archive) != ARTIFACT_DIGEST or any(
            _sha(selected / row["path"]) != row["sha256"] for row in member_proofs):
        raise ValueError("immutable source bytes changed during validation")

    result = {
        "schema": "memory-streaming-validation-v5",
        "scope": ("preprocessing equivalence and preparation costs newly calculated; "
                  "no graph, forecast, class, or outcome metrics recomputed"),
        "source": source,
        "selected_members": member_proofs,
        "original_implementation": {"commit": ORIGINAL_COMMIT,
                                    "source_files": original_source_proofs},
        "current_implementation": {
            "github_sha": os.environ.get("GITHUB_SHA"), "checked_out_head": checked_out_head,
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "source_files": current_source_proofs,
        },
        "comparisons": comparisons,
        "table_comparisons": tables,
        "costs": {"preparation_and_validation_elapsed_seconds": time.monotonic() - started,
                  "original": original_report["cost"], "current": current_report["cost"],
                  "source_campaign_cost_reused_not_zero": True},
        "original_artifact_unchanged": True,
        "graphs_or_forecasts_executed": False,
        "external_outcomes_recomputed": False,
        "equivalent": True,
    }
    _write(out / "validation.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--artifact-metadata", type=Path)
    parser.add_argument("--run-metadata", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--variant", choices=("original", "current"))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--original-sources", type=Path)
    args = parser.parse_args()
    try:
        if args.worker:
            if not all((args.variant, args.root, args.original_sources)):
                parser.error("worker mode requires variant, root and original sources")
            _worker(args)
        else:
            if not all((args.archive, args.artifact_metadata, args.run_metadata)):
                parser.error("validation mode requires archive and API metadata")
            validate(args)
    except BaseException as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        _write(args.out / "failure.json", {
            "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc(),
            "github_sha": os.environ.get("GITHUB_SHA"),
            "github_run_id": os.environ.get("GITHUB_RUN_ID")})
        raise


if __name__ == "__main__":
    main()
