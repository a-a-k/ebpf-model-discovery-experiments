"""Closed DeepFlow OTel capture, followed by the unchanged offline study suffix."""
from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import threading
import time
from types import SimpleNamespace

from .remote_toolchain_v4 import _index_table_proof, _read, _sha
from .runtime import write_json


def delivered(path: str) -> bool:
    """Existing full-artifact exclusions; frozen scientific files may not match."""
    parts = Path(path).parts
    return (not any(part in {"source", "upstream", "image-context"} for part in parts)
            and Path(path).name != "petclinic-image.tar"
            and not path.startswith(("toolchain-build/checkouts/", "toolchain-build/go/")))


def files(root: Path):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not delivered(relative):
            continue
        if path.is_symlink():
            raise ValueError("closed capture contains a symbolic link: " + relative)
        if path.is_file():
            yield relative, path
        elif not path.is_dir():
            raise ValueError("unsupported closed capture file type: " + relative)


def identity(status):
    if (status.get("system"), status.get("collector"), status.get("controller"), status.get("smoke")) != (
            "otel_demo", "deepflow", "clean-study", False):
        raise ValueError("closed postcapture processing is restricted to DeepFlow OTel main")
    if status.get("mode") not in {"absent", "partial", "full"} or status.get("seed") not in {6, 7, 8}:
        raise ValueError("closed capture is outside the fixed study")
    return {key: status[key] for key in ("run_id", "commit", "system", "collector", "controller", "mode", "seed", "smoke")}


def frozen_files(root: Path):
    frozen = _read(root / "forecast-saved.json")["sha256_by_path"]
    for relative, expected in frozen.items():
        path = root / relative
        if (not delivered(relative) or not path.is_file() or path.is_symlink()
                or not path.resolve().is_relative_to(root.resolve()) or _sha(path) != expected):
            raise ValueError("Frozen discovery or prediction changed: " + relative)
    return frozen


def capture_closure(root: Path, status):
    """Reuse the fixed protocol's acquisition and record-identity gates."""
    from .evaluate_v4 import _completeness
    from .evaluate_v5 import acquisition_checks, expected_counts
    from .transport_v4 import Journal

    declaration, counts, phases, states = expected_counts(status["system"], False)
    if status.get("protocol_version") != "graph-v5" or status.get("workload_counts") != counts:
        raise ValueError("capture protocol or workload differs from the fixed study")
    records, plans, census = (_read(root / name) for name in ("external.json", "plans.json", "census.json"))
    completeness = _completeness(records, plans, census, expected_phases=phases, expected_states=states)
    if not completeness["valid"] or status.get("observed_operations") != len(records):
        raise ValueError("closed primary acquisition is incomplete: " + str(completeness["problems"]))
    acquisition = acquisition_checks(root, status, declaration)
    if not acquisition["valid"]:
        raise ValueError("closed acquisition controls failed: " + str(acquisition["problems"]))
    connection = sqlite3.connect(f"file:{(root/'attempt-journal.sqlite').as_posix()}?mode=ro&immutable=1", uri=True)
    try:
        readonly = SimpleNamespace(lock=threading.Lock(), db=connection)
        if Journal.unresolved_transports(readonly):
            raise ValueError("closed capture has an unconfirmed remote transport")
    finally:
        connection.close()
    return {"completeness": completeness, "acquisition": acquisition, "unresolved_transports": 0}


def seal(root: Path, proof: Path, *, capture_run_id=None, capture_source=None):
    """Bind the already closed producer state without copying or dropping data."""
    started = time.time_ns()
    root, proof = root.resolve(), proof.resolve()
    if proof.exists() or proof.is_relative_to(root):
        raise ValueError("closed capture proof must be a new directory outside its input tree")
    status = _read(root / "status.json")
    expected = identity(status)
    if status["status"] != "postcapture_complete" or any(key.endswith("_close_error") for key in status):
        raise ValueError("capture is not closed successfully")
    if (expected["run_id"] != (capture_run_id or os.environ["GITHUB_RUN_ID"])
            or expected["commit"] != (capture_source or os.environ["GITHUB_SHA"])):
        raise ValueError("capture source/run differs from its producer")
    release = _read(root / "infrastructure/postcapture-guest-release.json")
    if (release.get("status") != "complete" or len(release.get("owned_processes", [])) != 2
            or not release.get("owned_guests_confirmed_exited_ns")):
        raise ValueError("owned-guest release is incomplete")
    if _sha(root / "infrastructure/guest-evidence-capture.json") != release["guest_evidence_capture_SHA256"]:
        raise ValueError("owned-guest diagnostics changed")
    frozen = frozen_files(root)
    for name in ("observation-index.sqlite", "attempt-journal.sqlite"):
        for suffix in ("-wal", "-shm"):
            path = root / (name + suffix)
            if path.exists() and path.stat().st_size:
                raise ValueError("SQLite sidecar is not closed: " + str(path))
    closure = capture_closure(root, status)
    proof.mkdir(parents=True)
    count = size = 0
    with (proof / "files.jsonl").open("w", encoding="utf-8") as stream:
        for relative, path in files(root):
            record = {"path": relative, "bytes": path.stat().st_size,
                      "mode": stat.S_IMODE(path.stat().st_mode), "sha256": _sha(path)}
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
            count += 1
            size += record["bytes"]
    directories = {path.relative_to(root).as_posix(): stat.S_IMODE(path.stat().st_mode)
                   for path in sorted(root.rglob("*"))
                   if delivered(path.relative_to(root).as_posix()) and path.is_dir()}
    with sqlite3.connect(f"file:{(root/'attempt-journal.sqlite').as_posix()}?mode=ro&immutable=1", uri=True) as journal:
        if journal.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("closed attempt journal failed quick_check")
        events = journal.execute("SELECT count(*),max(seq) FROM events").fetchone()
    write_json(proof / "capture-status.json", status)
    marker = {"schema": "closed-otel-postcapture-v5", "identity": expected,
              "files": count, "file_bytes": size, "file_inventory_sha256": _sha(proof / "files.jsonl"),
              "capture_status_sha256": _sha(proof / "capture-status.json"),
              "directories": directories,
              "frozen_file_count": len(frozen), "training_SQL": _index_table_proof(root / "observation-index.sqlite"),
              "acquisition_closure": closure,
              "journal_events": events[0], "journal_max_seq": events[1],
              "journal_sha256": _sha(root / "attempt-journal.sqlite"),
              "sealing_run_id": os.environ["GITHUB_RUN_ID"], "sealing_source": os.environ["GITHUB_SHA"],
              "index_bytes": (root / "observation-index.sqlite").stat().st_size,
              "excluded_only_existing_source_build_delivery_paths": True,
              "cost_scope": "All seal prechecks, closure, inventory and SQL proof; excludes marker write and outer upload/job costs",
              "started_ns": started, "ended_ns": time.time_ns()}
    write_json(proof / "closed.json", marker)
    return marker


def verify(root: Path, proof: Path, *, capture_run_id=None, capture_source=None):
    """Check every delivered file before any index mutation or evaluation."""
    root, proof = root.resolve(), proof.resolve()
    marker = _read(proof / "closed.json")
    if marker["schema"] != "closed-otel-postcapture-v5":
        raise ValueError("closed capture marker differs")
    status = _read(proof / "capture-status.json")
    expected = identity(status)
    if (marker["identity"] != expected or status["status"] != "postcapture_complete"
            or expected["run_id"] != (capture_run_id or os.environ["GITHUB_RUN_ID"])
            or expected["commit"] != (capture_source or os.environ["GITHUB_SHA"])
            or _sha(proof / "capture-status.json") != marker["capture_status_sha256"]
            or _sha(proof / "files.jsonl") != marker["file_inventory_sha256"]):
        raise ValueError("closed capture identity or manifest differs")
    seen, total = set(), 0
    for relative, mode in marker["directories"].items():
        path = root / relative
        if (Path(relative).is_absolute() or ".." in Path(relative).parts or path.is_symlink()
                or not path.resolve().is_relative_to(root)):
            raise ValueError("unsafe closed capture directory: " + relative)
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(mode)
    with (proof / "files.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            relative = row["path"]
            path = root / relative
            if (relative in seen or Path(relative).is_absolute() or ".." in Path(relative).parts
                    or not path.resolve().is_relative_to(root) or path.is_symlink()
                    or path.stat().st_size != row["bytes"] or _sha(path) != row["sha256"]):
                raise ValueError("closed capture member differs: " + relative)
            path.chmod(row["mode"])
            seen.add(relative)
            total += row["bytes"]
    if (seen != {relative for relative, _ in files(root)} or len(seen) != marker["files"]
            or total != marker["file_bytes"] or _read(root / "status.json") != status):
        raise ValueError("closed capture file population differs")
    if (_index_table_proof(root / "observation-index.sqlite") != marker["training_SQL"]
            or _sha(root / "attempt-journal.sqlite") != marker["journal_sha256"]):
        raise ValueError("closed capture SQL or journal differs")
    frozen_files(root)
    if capture_closure(root, status) != marker["acquisition_closure"]:
        raise ValueError("closed acquisition proof changed")
    return marker, status


def finalize(root: Path, proof: Path, *, capture_run_id=None, capture_source=None):
    """Run the original final ingest/refresh/classes/evidence/freeze sequence."""
    started = time.time_ns()
    from .classes_v5 import evaluate as evaluate_classes
    from .evidence_v4 import evaluate as evaluate_evidence
    from .identity_projection_v5 import refresh
    from .store_v5 import ObservationStoreV5
    from .transport_v4 import Journal

    marker, status = verify(root, proof, capture_run_id=capture_run_id, capture_source=capture_source)
    root = root.resolve()
    destination = root / "infrastructure/postcapture"
    if destination.exists():
        raise ValueError("refusing repeated offline finalization")
    shutil.copytree(proof, destination)
    result = {"status": "started", "identity": marker["identity"], "started_ns": started,
              "closed_manifest_sha256": _sha(proof / "closed.json"),
              "input_file_inventory_sha256": marker["file_inventory_sha256"],
              "processing_run_id": os.environ["GITHUB_RUN_ID"], "processing_source": os.environ["GITHUB_SHA"],
              "cost_scope": "Complete input verification/copy and unchanged offline suffix; outer restore/upload/queue costs retained separately",
              "offline_only": True, "traffic_replay_or_model_refit": False}
    store = ObservationStoreV5(root / "observation-index.sqlite", same_trace_parents=True)
    journal = Journal(root / "attempt-journal.sqlite")
    plans, records = _read(root / "plans.json"), _read(root / "external.json")
    ctx = SimpleNamespace(out=root, journal=journal)
    campaign = SimpleNamespace(ctx=ctx, collector=status["collector"], store=store, plans=plans)
    try:
        write_json(root / "index-final.json", store.ingest(root / "observations", root / "native"))
        refresh(campaign, "final")
        declaration = importlib.import_module("systems.otel_demo.experiment_v5")
        evaluate_classes(store, plans, records, declaration,
                         root / "toolchain/classes/classes-family-model.json", root)
        evaluate_evidence(ctx, status["system"], store, plans, records)
        write_json(root / "freeze-integrity.json", {"all_unchanged": True, "sha256_by_path": frozen_files(root)})
        status["status"] = "acquisition_complete"
        result["status"] = "complete"
    except BaseException as exc:
        status.update(status="technical_failure", error=repr(exc))
        result.update(status="failed", error=repr(exc))
        raise
    finally:
        store.close()
        journal.export(root / "attempt-journal.jsonl")
        journal.close()
        ended = time.time_ns()
        status.update(ended_ns=ended, elapsed_seconds=(ended-status["started_ns"])/1e9)
        result.update(ended_ns=ended, elapsed_seconds=(ended-started)/1e9)
        write_json(root / "status.json", status)
        write_json(destination / "processing.json", result)
    return result


def main():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("closed capture processing runs in GitHub Actions only")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("seal", "finalize"))
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--capture-run-id")
    parser.add_argument("--capture-source")
    args = parser.parse_args()
    print(json.dumps({"action": args.action, "status": "started", "time_ns": time.time_ns()}), flush=True)
    {"seal": seal, "finalize": finalize}[args.action](
        args.campaign, args.proof, capture_run_id=args.capture_run_id, capture_source=args.capture_source)
    print(json.dumps({"action": args.action, "status": "complete", "time_ns": time.time_ns(),
                      "proof_sha256": _sha(args.proof / "closed.json")}), flush=True)


if __name__ == "__main__":
    main()
