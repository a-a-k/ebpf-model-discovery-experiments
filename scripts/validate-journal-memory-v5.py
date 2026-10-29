"""Validate lazy journal hydration against the old bulk map on saved evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import stat
import subprocess
import sys
import threading
import time
import traceback
import zipfile


ORIGINAL_COMMIT = "f6cb591a9bd93bd9cf1e9e75ac5eb241dc1c312d"
SOURCE_FILE = "src/ebpf_discovery/identity_projection_v5.py"
JOURNAL_MEMBER = "attempt-journal.sqlite"


def _memory_validator():
    path = Path(__file__).with_name("validate-memory-streaming-v5.py")
    spec = importlib.util.spec_from_file_location("_saved_memory_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load shared validation helpers: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SHARED = _memory_validator()


def _canonical(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _extract_journal(archive: Path, destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if (len({entry.filename for entry in entries}) != len(entries)
                or not all(SHARED._safe(entry) for entry in entries)):
            raise ValueError("artifact ZIP names are duplicate or unsafe")
        matches = [entry for entry in entries if entry.filename == JOURNAL_MEMBER]
        if len(matches) != 1:
            raise ValueError(f"artifact must contain exactly one root {JOURNAL_MEMBER}")
        entry = matches[0]
        body = bundle.read(entry)
    target = destination / JOURNAL_MEMBER
    target.write_bytes(body)
    return {"path": JOURNAL_MEMBER, "bytes": len(body),
            "sha256": _sha_bytes(body), "zip_crc32": f"{entry.CRC:08x}"}


def _git_source(commit: str, destination: Path) -> dict:
    body = subprocess.run(
        ["git", "show", f"{commit}:{SOURCE_FILE}"], check=True,
        stdout=subprocess.PIPE).stdout
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)
    return {"commit": commit, "path": SOURCE_FILE, "bytes": len(body),
            "sha256": _sha_bytes(body)}


def _load_source(path: Path, variant: str):
    name = "ebpf_discovery._saved_journal_validation_" + variant
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load identity projection source: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class _ReadJournal:
    """Minimum journal interface over an immutable SQLite input."""

    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        uri = path.resolve().as_uri() + "?mode=ro"
        self.db = sqlite3.connect(uri, uri=True, check_same_thread=False)

    def close(self) -> None:
        self.db.close()


def _request_sort_key(value) -> bytes:
    return _canonical(value)


def _emit_transports(output: Path, mapping: dict, hydrate=None) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    stream_path = output / "canonical-transports.jsonl"
    with stream_path.open("wb") as stream:
        for ordinal, request_id in enumerate(sorted(mapping, key=_request_sort_key)):
            reference = mapping[request_id]
            transport = (hydrate(reference)
                         if hydrate is not None and reference is not None else reference)
            transport_body = _canonical(transport)
            body = _canonical({"request_id": request_id, "transport": transport})
            offset = stream.tell()
            stream.write(body)
            rows.append({"ordinal": ordinal, "request_id": request_id,
                         "request_id_sha256": _sha_bytes(_canonical(request_id)),
                         "stream_offset": offset, "stream_length": len(body),
                         "transport_is_none": transport is None,
                         "transport_bytes": len(transport_body),
                         "transport_sha256": _sha_bytes(transport_body)})
            del transport, transport_body, body
    manifest = _canonical(rows)
    (output.parent / "transport-manifest.json").write_bytes(manifest)
    return {"requests": len(rows), "none_transports": sum(row["transport_is_none"] for row in rows),
            "manifest_bytes": len(manifest), "manifest_sha256": _sha_bytes(manifest),
            "transport_stream_bytes": stream_path.stat().st_size,
            "transport_stream_sha256": SHARED._sha(stream_path),
            "rows": rows}


def _worker(args) -> None:
    started = time.monotonic()
    journal = _ReadJournal(args.journal)
    try:
        if args.variant == "original":
            module = _load_source(args.original_source, "original")
            mapping = module._journal_transports(journal)
            report = _emit_transports(args.out / "transports", mapping)
        else:
            from ebpf_discovery import identity_projection_v5 as module
            mapping = module._journal_transports(journal)
            report = _emit_transports(
                args.out / "transports", mapping,
                hydrate=lambda reference: module._load_transport(journal, reference))
        report.update({"variant": args.variant,
                       "elapsed_seconds": time.monotonic() - started,
                       "peak_rss_kib": SHARED._peak_rss_kib(),
                       "journal_rows": journal.db.execute(
                           "SELECT COUNT(*) FROM events").fetchone()[0],
                       "maximum_seq": journal.db.execute(
                           "SELECT COALESCE(MAX(seq),0) FROM events").fetchone()[0]})
        SHARED._write(args.out / "worker-report.json",
                      {key: value for key, value in report.items() if key != "rows"})
    finally:
        journal.close()


def _run_worker(script: Path, variant: str, journal: Path,
                original_source: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, str(script), "--worker", "--variant", variant,
               "--journal", str(journal), "--original-source", str(original_source),
               "--out", str(output)]
    started = time.monotonic()
    completed = subprocess.run(command, text=True, capture_output=True)
    invocation = {"argv": command, "returncode": completed.returncode,
                  "elapsed_seconds": time.monotonic() - started,
                  "stdout": completed.stdout, "stderr": completed.stderr}
    SHARED._write(output / "invocation.json", invocation)
    if completed.returncode:
        raise RuntimeError(f"{variant} journal worker failed")
    report = SHARED._json(output / "worker-report.json")
    report["rows"] = json.loads((output / "transport-manifest.json").read_text(
        encoding="utf-8"))
    return report


def _compare(original_dir: Path, current_dir: Path,
             original: dict, current: dict) -> dict:
    old_rows, new_rows = original["rows"], current["rows"]
    if old_rows != new_rows:
        raise ValueError("per-request canonical transport manifests differ")
    old_stream = original_dir / "transports/canonical-transports.jsonl"
    new_stream = current_dir / "transports/canonical-transports.jsonl"
    if (old_stream.stat().st_size != new_stream.stat().st_size
            or SHARED._sha(old_stream) != SHARED._sha(new_stream)):
        raise ValueError("canonical per-request transport stream differs")
    with old_stream.open("rb") as old, new_stream.open("rb") as new:
        while True:
            old_chunk, new_chunk = old.read(1024 * 1024), new.read(1024 * 1024)
            if old_chunk != new_chunk:
                raise ValueError("canonical per-request transport stream bytes differ")
            if not old_chunk:
                break
    checked = [{"ordinal": row["ordinal"], "request_id": row["request_id"],
                "transport_is_none": row["transport_is_none"],
                "bytes": row["transport_bytes"], "sha256": row["transport_sha256"]}
               for row in old_rows]
    return {"requests": len(checked), "none_transports": original["none_transports"],
            "canonical_manifest_identical": True,
            "canonical_manifest_sha256": original["manifest_sha256"],
            "all_per_request_canonical_bytes_identical": True,
            "per_request": checked}


def validate(args) -> dict:
    started = time.monotonic()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = SHARED._verify_source(
        args.archive, SHARED._json(args.artifact_metadata), SHARED._json(args.run_metadata))
    selected = output.parent / "journal-memory-selected-input"
    journal_proof = _extract_journal(args.archive, selected)
    journal = selected / JOURNAL_MEMBER
    old_source = output.parent / "journal-memory-original-source" / "identity_projection_v5.py"
    old_source_proof = _git_source(ORIGINAL_COMMIT, old_source)
    current_path = Path(SOURCE_FILE)
    current_source_proof = {"path": SOURCE_FILE, "bytes": current_path.stat().st_size,
                            "sha256": SHARED._sha(current_path)}
    checked_out_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, text=True,
        stdout=subprocess.PIPE).stdout.strip()
    if os.environ.get("GITHUB_SHA") and checked_out_head != os.environ["GITHUB_SHA"]:
        raise ValueError("checked-out validation source differs from GITHUB_SHA")
    original_dir, current_dir = output / "original", output / "current"
    original = _run_worker(Path(__file__).resolve(), "original", journal,
                           old_source, original_dir)
    current = _run_worker(Path(__file__).resolve(), "current", journal,
                          old_source, current_dir)
    comparison = _compare(original_dir, current_dir, original, current)
    for path in (
        original_dir / "transports/canonical-transports.jsonl",
        current_dir / "transports/canonical-transports.jsonl",
        original_dir / "transport-manifest.json",
        current_dir / "transport-manifest.json",
    ):
        path.unlink()
    if ("sha256:" + SHARED._sha(args.archive) != SHARED.ARTIFACT_DIGEST
            or SHARED._sha(journal) != journal_proof["sha256"]
            or SHARED._sha(old_source) != old_source_proof["sha256"]):
        raise ValueError("immutable source bytes changed during validation")
    result = {
        "schema": "journal-memory-equivalence-validation-v5",
        "scope": ("old bulk journal map versus one-at-a-time hydrated current map; "
                  "no workload, graph, fit, class, forecast, score, or outcome processing"),
        "source": source,
        "selected_member": journal_proof,
        "original_implementation": old_source_proof,
        "current_implementation": {
            "github_sha": os.environ.get("GITHUB_SHA"),
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "checked_out_head": checked_out_head, "source_file": current_source_proof},
        "comparison": comparison,
        "comparison_workspace": {
            "canonical_transport_streams_removed_after_hash_and_byte_comparison": True,
            "per_request_hashes_retained_in_validation": True},
        "worker_summaries": {
            "original": {key: value for key, value in original.items() if key != "rows"},
            "current": {key: value for key, value in current.items() if key != "rows"}},
        "costs": {"validation_elapsed_seconds": time.monotonic() - started,
                  "original_worker_elapsed_seconds": original["elapsed_seconds"],
                  "original_worker_peak_rss_kib": original["peak_rss_kib"],
                  "current_worker_elapsed_seconds": current["elapsed_seconds"],
                  "current_worker_peak_rss_kib": current["peak_rss_kib"],
                  "source_campaign_cost_reused_not_zero": True,
                  "memory_or_time_improvement_claimed": False},
        "original_artifact_unchanged": True,
        "equivalent": True,
    }
    SHARED._write(output / "validation.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--artifact-metadata", type=Path)
    parser.add_argument("--run-metadata", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--variant", choices=("original", "current"))
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--original-source", type=Path)
    args = parser.parse_args()
    try:
        if args.worker:
            if not all((args.variant, args.journal, args.original_source)):
                parser.error("worker mode requires variant, journal and original source")
            _worker(args)
        else:
            if not all((args.archive, args.artifact_metadata, args.run_metadata)):
                parser.error("validation mode requires archive and API metadata")
            validate(args)
    except BaseException as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        SHARED._write(args.out / "failure.json", {
            "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc(),
            "github_sha": os.environ.get("GITHUB_SHA"),
            "github_run_id": os.environ.get("GITHUB_RUN_ID")})
        raise


if __name__ == "__main__":
    main()
