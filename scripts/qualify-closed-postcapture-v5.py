"""Fixed saved full/6 whole-suffix qualification; no traffic, fitting or simulation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import sqlite3
import subprocess
import time
import zipfile

import requests

from ebpf_discovery import postcapture_v5 as closed
from ebpf_discovery import remote_toolchain_v4 as transport
from ebpf_discovery.evaluate_v5 import evaluate_campaign
from ebpf_discovery.summary_manifest_v5 import record as record_manifest

ANCHOR = "0056b4c8ecb85e8b40c433e63af442133a21f3cc"
PRODUCER = "41470575905"
TRAINING = (13162514595, 1864728289, "709e6c4f3e8af5dd9dfadb31b2c90c28449ca3a635be31c1cb5363fc3e6ba36e")
FINAL = (13180555929, 5335924987, "7541e1387ba9311fc8b4c09eb3685d8b6dbc4774cad035e72cabf128661db26d")
TRAINING_INDEX_SHA = "c36fdfafd41dea71b12e06744c2988e01a3e20bdb5c295093ea9b4a77186b745"
FINAL_OUTPUTS = (
    "classes-v4.json", "classes-v5.json", "evidence-v4.json", "freeze-integrity.json",
    "runtime-identity-v5/projection-final.jsonl", "runtime-identity-v5/supplied-alias-scope-final.json",
    "attempt-journal.jsonl",
)
RECREATED = (*FINAL_OUTPUTS[:-1], "index-final.json", "evaluation-v5.json", "evaluation-manifest.json",
             "runtime-identity-v5/refresh-cost-final.json")
MUTABLE_INPUTS = {"status.json", "observation-index.sqlite", "attempt-journal.sqlite", "attempt-journal.jsonl"}
OBSERVED_COST_FIELDS = {"index-final.json": ("seconds", "index_bytes"),
                        "runtime-identity-v5/refresh-cost-final.json": ("elapsed_seconds",)}
WORK = Path("work/closed-postcapture-qualification").resolve()
ROOT = Path("work/campaign").resolve()
PROOF = Path("work/postcapture-proof").resolve()
OUT = Path("results/closed-postcapture-qualification").resolve()


def canonical_file(path):
    digest = hashlib.sha256()
    if path.suffix == ".jsonl":
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                digest.update(json.dumps(json.loads(line), sort_keys=True, separators=(",", ":"),
                                         ensure_ascii=False).encode() + b"\n")
    else:
        digest.update(json.dumps(transport._read(path), sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False).encode())
    return digest.hexdigest()


def evaluation_scientific_sha(path):
    value = transport._read(path)
    assert value["complete_for_evaluation"] is True and value["primary_series_result"] is True
    removed_cost = value.pop("cost")
    status = value["status"]
    assert status["status"] == "acquisition_complete"
    status.pop("ended_ns")
    status.pop("elapsed_seconds")
    return transport._json_sha(value), transport._json_sha(removed_cost)


def non_cost_metadata(path, cost_fields):
    value = transport._read(path)
    observed_cost = {key: value.pop(key) for key in cost_fields}
    return {"non_cost_fields_sha256": transport._json_sha(value),
            "full_file_sha256": transport._sha(path), "observed_cost_fields": observed_cost}


def journal_proof(path):
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro&immutable=1", uri=True)
    try:
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        digest, count = hashlib.sha256(), 0
        for row in connection.execute("SELECT seq,kind,wall_ns,monotonic_ns,data FROM events ORDER BY seq"):
            digest.update(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode() + b"\n")
            count += 1
        schema = list(connection.execute("SELECT type,name,tbl_name,sql FROM sqlite_master "
                                         "WHERE type IN ('table','index') ORDER BY type,name"))
        return {"rows": count, "all_columns_sha256": digest.hexdigest(), "schema_sha256": transport._json_sha(schema)}
    finally:
        connection.close()


def measure(name, function):
    wall, cpu = time.perf_counter(), time.process_time()
    phase = {"phase": name, "started_ns": time.time_ns(), "free_before": shutil.disk_usage(".").free}
    try:
        return function()
    finally:
        phase.update(ended_ns=time.time_ns(), wall_seconds=time.perf_counter()-wall,
                     process_cpu_seconds=time.process_time()-cpu,
                     peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                     free_after=shutil.disk_usage(".").free)
        with (OUT / "phases.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(phase) + "\n")
        print(json.dumps(phase), flush=True)


def artifact(declaration):
    number, size, sha = declaration
    meta = json.loads(subprocess.check_output(["gh", "api", f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{number}"]))
    assert (str(meta["workflow_run"]["id"]), meta["workflow_run"]["head_sha"],
            meta["size_in_bytes"], meta["digest"], meta["expired"]) == (PRODUCER, ANCHOR, size, "sha256:"+sha, False)
    transport._atomic_json(OUT / f"original-artifact-{number}.json", meta)
    destination = WORK / f"{number}.zip"
    assert not destination.exists() and shutil.disk_usage(WORK).free >= size + 1024**3
    assert transport._download(requests.Session(), meta["archive_download_url"],
                               transport._headers(os.environ["GH_TOKEN"]), destination,
                               retry_log=OUT / "download-retries.jsonl") == sha
    assert destination.stat().st_size == size
    return destination


def build():
    assert not ROOT.exists() and not WORK.exists() and not PROOF.exists()
    WORK.mkdir(parents=True)
    engines = ("store_v3", "store_v5", "identity_projection_v5", "runtime_identity_v5", "classes_v4",
               "classes_v5", "evidence_v4", "evaluate_v4", "evaluate_v5", "toolchain_v4", "toolchain_v5",
               "bering_v4", "observations")
    for name in engines:
        relative = f"src/ebpf_discovery/{name}.py"
        before, after = subprocess.check_output(["git", "rev-parse", f"{ANCHOR}:{relative}", f"HEAD:{relative}"], text=True).splitlines()
        assert before == after, relative
    # Fixed directory-only census: all original delivery includes frozen models.
    # Restore peak also retains the training SQL and the complete encoded final.
    required = 53783856314 + 7664906240 + FINAL[1] + 1024**3
    reservation = {"required_bytes": required, "available_bytes": shutil.disk_usage(WORK).free,
                   "includes_all_frozen_toolchain_files": True, "scientific_cap": False}
    transport._atomic_json(OUT / "initial-disk-guard.json", reservation)
    assert reservation["available_bytes"] >= required, "Whole-suffix fixed reconstruction does not fit this actual host"
    training = measure("download_original_training", lambda: artifact(TRAINING))
    prefix = WORK / "training"
    measure("restore_complete_training_prefix", lambda: transport._safe_extract(training, prefix))
    ready = transport._read(prefix / "ready.json")
    expected = {key: ready[key] for key in transport.IDENTITY_KEYS}
    assert (expected["run_id"], expected["commit"], expected["mode"], str(expected["seed"])) == (PRODUCER, ANCHOR, "full", "6")
    manifest, verified = measure("verify_original_closed_training", lambda: transport._validate_checkpoint(prefix, expected))
    _, _, provenance = transport._checkpoint_toolchain(prefix, manifest)
    assert provenance["collector"] == "deepflow"
    training_index = WORK / "training.sqlite"
    (prefix / "observation-index.sqlite").rename(training_index)
    assert transport._sha(training_index) == TRAINING_INDEX_SHA
    training_SQL = measure("prove_complete_training_SQL", lambda: transport._index_table_proof(training_index))
    transport._atomic_json(OUT / "training-validation.json", {
        "identity": expected, "manifest_sha256": verified["manifest_sha256"],
        "files_verified": len(verified["files"]), "SQL": training_SQL, "index_sha256": TRAINING_INDEX_SHA})
    del manifest, verified
    assert prefix.resolve().parent == WORK and prefix.name == "training" and not prefix.is_symlink()
    measure("release_only_validated_training_mirror", lambda: shutil.rmtree(prefix))
    training.unlink()
    full = measure("download_original_full_delivery", lambda: artifact(FINAL))
    with zipfile.ZipFile(full) as bundle:
        logical = sum(e.file_size for e in bundle.infolist())
    assert logical == 53783856314
    assert shutil.disk_usage(WORK).free >= logical + 1024**3
    measure("restore_ALL_original_delivery_including_frozen_models", lambda: transport._safe_extract(full, ROOT))
    original_status = transport._read(ROOT / "status.json")
    assert original_status["status"] == "acquisition_complete"
    index = ROOT / "observation-index.sqlite"
    final_SQL = measure("prove_complete_original_final_SQL", lambda: transport._index_table_proof(index))
    expected_outputs = {name: measure("reference_"+name.replace("/", "_"), lambda name=name: canonical_file(ROOT / name))
                        for name in FINAL_OUTPUTS}
    scientific_SHA, cost_SHA = measure("reference_ALL_scientific_evaluation_fields", lambda: evaluation_scientific_sha(ROOT / "evaluation-v5.json"))
    reference = {"scientific_source": ANCHOR, "producer": PRODUCER,
                 "original_status": original_status, "original_final_SQL": final_SQL,
                 "original_final_SQL_file_SHA256": transport._sha(index),
                 "expected_outputs": expected_outputs, "scientific_evaluation_sha256": scientific_SHA,
                 "original_cost_object_sha256": cost_SHA,
                 "ingest_refresh_metadata": {
                     name: non_cost_metadata(ROOT / name, fields) for name, fields in OBSERVED_COST_FIELDS.items()},
                 "journal": measure("prove_original_journal_rows", lambda: journal_proof(ROOT / "attempt-journal.sqlite")),
                 "semantic_normalization": "JSON object key order, whitespace and escape formatting normalized; JSONL row sequence and all field values retained exactly. Evaluation excludes only cost and status.ended_ns/status.elapsed_seconds; all costs retained separately. Ingest metadata excludes only seconds/index_bytes; refresh metadata excludes only elapsed_seconds, with both complete-file hashes and observed costs retained.",
                 "no_historical_missing_source_build_cache_recovery_claim": True,
                 "no_new_traffic_model_fitting_or_simulation": True}
    transport._atomic_json(OUT / "original-reference.json", reference)
    index.unlink()  # Full unchanged original SQLite remains encoded in exact remote artifact and this ZIP.
    training_index.rename(index)
    assert transport._sha(index) == TRAINING_INDEX_SHA and transport._index_table_proof(index) == training_SQL
    removed = {}
    for name in RECREATED:
        path = ROOT / name
        if path.exists():
            removed[name] = {"bytes": path.stat().st_size, "sha256": transport._sha(path)}
            path.unlink()
    transport._atomic_json(OUT / "only_write_only_final_outputs_removed.json", removed)
    release = transport._read(ROOT / "infrastructure/postcapture-guest-release.json")
    status = dict(original_status, status="postcapture_complete", ended_ns=release["ended_ns"])
    status["elapsed_seconds"] = (status["ended_ns"]-status["started_ns"])/1e9
    transport._atomic_json(ROOT / "status.json", status)
    marker = measure("seal_reconstructed_complete_capture", lambda: closed.seal(
        ROOT, PROOF, capture_run_id=PRODUCER, capture_source=ANCHOR))
    transport._atomic_json(PROOF / "qualification-reference.json", reference)
    transport._atomic_json(OUT / "closed-input-summary.json", {
        "identity": marker["identity"], "scientific_root": marker["scientific_root"],
        "file_count": marker["files"], "file_bytes": marker["file_bytes"],
        "file_inventory_sha256": marker["file_inventory_sha256"],
        "frozen_file_count": marker["frozen_file_count"], "reconstruction_not_historical_handoff": True})
    assert transport._sha(full) == FINAL[2]
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        stream.write("file_bytes="+str(marker["file_bytes"])+"\n")
        stream.write("index_bytes="+str(marker["index_bytes"])+"\n")
        stream.write("proof_bytes="+str(sum(p.stat().st_size for p in PROOF.rglob("*") if p.is_file()))+"\n")
        stream.write("manifest_sha256="+transport._sha(PROOF / "closed.json")+"\n")


def compare():
    reference = transport._read(ROOT / "infrastructure/postcapture/qualification-reference.json")
    assert reference["scientific_source"] == ANCHOR and reference["producer"] == PRODUCER
    processing = transport._read(ROOT / "infrastructure/postcapture/processing.json")
    assert processing["status"] == "complete" and processing["traffic_replay_or_model_refit"] is False
    assert processing["processing_run_id"] == os.environ["GITHUB_RUN_ID"] and processing["processing_source"] == os.environ["GITHUB_SHA"]
    actual_SQL = measure("prove_ALL_candidate_final_SQL_rows", lambda: transport._index_table_proof(ROOT / "observation-index.sqlite"))
    assert actual_SQL == reference["original_final_SQL"]
    for name, expected in reference["expected_outputs"].items():
        assert measure("compare_"+name.replace("/", "_"), lambda name=name: canonical_file(ROOT / name)) == expected, name
    assert measure("compare_ALL_journal_rows", lambda: journal_proof(ROOT / "attempt-journal.sqlite")) == reference["journal"]
    report = measure("evaluate_original_unchanged_final_protocol", lambda: evaluate_campaign(ROOT))
    transport._atomic_json(ROOT / "evaluation-v5.json", report)
    del report
    actual_scientific, actual_cost = measure("compare_ALL_scientific_evaluation_fields", lambda: evaluation_scientific_sha(ROOT / "evaluation-v5.json"))
    assert actual_scientific == reference["scientific_evaluation_sha256"]
    compared_metadata = {}
    for name, fields in OBSERVED_COST_FIELDS.items():
        actual = non_cost_metadata(ROOT / name, fields)
        original = reference["ingest_refresh_metadata"][name]
        assert actual["non_cost_fields_sha256"] == original["non_cost_fields_sha256"], name
        compared_metadata[name] = {"original": original, "candidate": actual}
    immutable_count = 0
    with (ROOT / "infrastructure/postcapture/files.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row["path"] in MUTABLE_INPUTS:
                continue
            path = ROOT / row["path"]
            assert path.is_file() and path.stat().st_size == row["bytes"] and transport._sha(path) == row["sha256"], row["path"]
            assert path.stat().st_mode & 0o7777 == row["mode"], row["path"]
            immutable_count += 1
    frozen = closed.frozen_files(ROOT)
    manifest = measure("record_production_compact_payload_manifest", lambda: record_manifest(
        ROOT, system="otel_demo", mode="full", seed=6, collector="deepflow", stage="main",
        run_id=os.environ["GITHUB_RUN_ID"], commit=os.environ["GITHUB_SHA"], qualification_only=True))
    assert manifest["qualification_only"] is True
    for name, digest in manifest["files_sha256"].items():
        assert digest is not None and transport._sha(ROOT / name) == digest, name
    transport._atomic_json(OUT / "whole-suffix-equality.json", {
        "status": "complete", "actual_processing_run_id": os.environ["GITHUB_RUN_ID"],
        "actual_processing_source": os.environ["GITHUB_SHA"], "original_producer": PRODUCER,
        "original_scientific_source": ANCHOR, "ALL_final_logical_SQL_rows_and_schema_equal": True,
        "ALL_saved_scientific_evaluation_fields_equal": True, "ALL_reference_outputs_equal": True,
        "ALL_ingest_refresh_non_cost_fields_equal": True, "ingest_refresh_metadata": compared_metadata,
        "production_compact_manifest_payload_hashes_verified": len(manifest["files_sha256"]),
        "published_full_artifact_name": manifest["full_artifact_name"],
        "compact_manifest_sha256": transport._sha(ROOT / "evaluation-manifest.json"),
        "ALL_journal_rows_and_schema_equal": True, "immutable_input_files_rehashed": immutable_count,
        "ALL_frozen_model_and_input_hashes_equal": len(frozen),
        "original_cost_object_sha256": reference["original_cost_object_sha256"],
        "candidate_cost_object_sha256": actual_cost, "complete_processing_cost": processing,
        "normalization": reference["semantic_normalization"],
        "qualification_only_not_new_main_cell": True, "no_traffic_Bering_or_Sheaft_execution": True,
        "no_all_seven_runtime_or_source_admission_claim": True})


if __name__ == "__main__":
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("whole-suffix qualification runs in GitHub Actions only")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("build", "compare"))
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    status = {"stage": args.stage, "status": "running", "started_ns": time.time_ns(),
              "processing_source": os.environ["GITHUB_SHA"], "qualification_only": True}
    try:
        {"build": build, "compare": compare}[args.stage]()
        status["status"] = "complete"
    except BaseException as error:
        status.update(status="failed", error=repr(error))
        raise
    finally:
        status["ended_ns"] = time.time_ns()
        transport._atomic_json(OUT / (args.stage+"-status.json"), status)
