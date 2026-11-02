"""Actions-only full-input profile of the unchanged saved-case final refresh."""
import cProfile
import hashlib
import json
import os
from pathlib import Path
import pstats
import resource
import shutil
import sqlite3
import stat
import subprocess
import time
import traceback
from types import SimpleNamespace
import zipfile

import requests

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery.identity_projection_v5 import refresh
from ebpf_discovery.store_v5 import ObservationStoreV5
from ebpf_discovery.transport_v4 import Journal


assert os.environ.get("GITHUB_ACTIONS") == "true"
workspace = Path.cwd().resolve()
work = workspace / "work/final-refresh-profile"
campaign_root = workspace / "work/campaign"
out = workspace / "results/final-refresh-profile"
assert not work.exists() and not campaign_root.exists()
work.mkdir(parents=True)
out.mkdir(parents=True, exist_ok=True)
references = work / "immutable-references"
references.mkdir()
anchor = "0056b4c8ecb85e8b40c433e63af442133a21f3cc"
changed = subprocess.check_output(["git", "diff", "--name-only", anchor, "HEAD"], text=True).splitlines()
assert set(changed) == {".github/workflows/infrastructure.yml", "scripts/profile-full6-final-refresh-v5.py"}
phases = []
status = {"status": "running", "source": os.environ["GITHUB_SHA"], "scientific_source": anchor,
          "producer": 41470575905, "started_ns": time.time_ns(),
          "cProfile_timer": "time.process_time; process CPU seconds",
          "phase_timers": "time.perf_counter wall and time.process_time process CPU",
          "new_traffic_Bering_Sheaft_or_external_outcome_recomputation": False,
          "cache_boundary": "Restored files and generated final outputs preexist; no original wall reproduction or speedup claim."}


def measure(name, function):
    wall, cpu = time.perf_counter(), time.process_time()
    record = {"phase": name, "started_ns": time.time_ns(), "free_before": shutil.disk_usage(work).free}
    try:
        return function()
    finally:
        record.update(ended_ns=time.time_ns(), wall_seconds=time.perf_counter() - wall,
                      process_cpu_seconds=time.process_time() - cpu, free_after=shutil.disk_usage(work).free,
                      process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        phases.append(record)
        remote._atomic_json(out / "phases.json", phases)


def artifact(number, size, digest):
    value = json.loads(subprocess.check_output([
        "gh", "api", f"repos/a-a-k/ebpf-model-discovery-experiments/actions/artifacts/{number}"]))
    assert (value["workflow_run"]["id"], value["workflow_run"]["head_sha"], value["size_in_bytes"],
            value["digest"], value["expired"]) == (41470575905, anchor, size, "sha256:" + digest, False)
    remote._atomic_json(out / f"artifact-{number}.json", value)
    archive = work / f"{number}.zip"
    assert shutil.disk_usage(work).free >= size + 67108864
    actual = remote._download(requests.Session(), value["archive_download_url"],
                              remote._headers(os.environ["GH_TOKEN"]), archive)
    assert actual == digest
    return archive


def restore_full_inputs(archive):
    """Fixed diagnostic input selection; models are not inputs to refresh."""
    campaign_root.mkdir()
    seen, count, logical = set(), 0, 0
    census = hashlib.sha256()
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            name = entry.filename.replace("\\", "/")
            assert name and not name.startswith("/") and ".." not in Path(name).parts
            assert name not in seen and not stat.S_ISLNK(entry.external_attr >> 16)
            seen.add(name)
            if name.startswith(("toolchain/", "toolchain-build/")):
                continue
            target = (campaign_root / name).resolve()
            assert target.is_relative_to(campaign_root)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            sha = hashlib.sha256()
            received = 0
            with bundle.open(entry) as source, target.open("xb") as destination:
                while chunk := source.read(1024 * 1024):
                    destination.write(chunk)
                    sha.update(chunk)
                    received += len(chunk)
            assert received == entry.file_size
            census.update(json.dumps([name, received, sha.hexdigest()], separators=(",", ":")).encode() + b"\n")
            count += 1
            logical += received
    return {"selected_files": count, "selected_bytes": logical,
            "selected_path_size_SHA256_census": census.hexdigest(), "all_selected_member_CRCs_checked": True,
            "excluded": ["toolchain/", "toolchain-build/"], "excluded_model_member_CRCs_claimed": False}


def runtime_census():
    result, count, size = hashlib.sha256(), 0, 0
    for path in sorted((campaign_root / "runtime-identity-v5").rglob("*")):
        assert not path.is_symlink()
        if not path.is_file() or path.name == "refresh-cost-final.json":
            continue
        length = path.stat().st_size
        result.update(json.dumps([path.relative_to(campaign_root).as_posix(), length, remote._sha(path)],
                                 separators=(",", ":")).encode() + b"\n")
        count += 1
        size += length
    return {"files": count, "bytes": size, "all_path_size_SHA256_census": result.hexdigest(),
            "excluded_elapsed_cost_file": "runtime-identity-v5/refresh-cost-final.json"}


store = journal = None
try:
    training = measure("download_exact_training", lambda: artifact(
        13162514595, 1864728289, "709e6c4f3e8af5dd9dfadb31b2c90c28449ca3a635be31c1cb5363fc3e6ba36e"))
    full = measure("download_exact_final", lambda: artifact(
        13180555929, 5335924987, "7541e1387ba9311fc8b4c09eb3685d8b6dbc4774cad035e72cabf128661db26d"))
    with zipfile.ZipFile(training) as left, zipfile.ZipFile(full) as right:
        training_bytes = sum(e.file_size for e in left.infolist() if not e.is_dir())
        full_bytes = sum(e.file_size for e in right.infolist()
                         if not e.is_dir() and not e.filename.startswith(("toolchain/", "toolchain-build/")))
        final_index_bytes = right.getinfo("observation-index.sqlite").file_size
    required = training_bytes + full_bytes + 2 * final_index_bytes + 1073741824
    free = shutil.disk_usage(work).free
    remote._atomic_json(out / "restore-disk-guard.json", {
        "free_after_download": free, "required_remaining_bytes": required,
        "training_uncompressed": training_bytes, "final_selected_uncompressed": full_bytes,
        "extra_final_SQLite_and_WAL_allowance": 2 * final_index_bytes})
    assert free >= required
    prefix = work / "closed-training"
    measure("restore_training", lambda: remote._safe_extract(training, prefix))
    ready = remote._read(prefix / "ready.json")
    expected = {key: ready[key] for key in remote.IDENTITY_KEYS}
    assert (expected["run_id"], expected["commit"], expected["mode"], str(expected["seed"])) == (
        "41470575905", anchor, "full", "6")
    manifest, proof = measure("verify_closed_training", lambda: remote._validate_checkpoint(prefix, expected))
    _, _, provenance = remote._checkpoint_toolchain(prefix, manifest)
    assert provenance["collector"] == "deepflow"
    remote._atomic_json(out / "training-binding.json", {
        "identity": expected, "collector": provenance, "input_proof_SHA256": remote._json_sha(proof),
        "closed_files_verified": len(proof["files"]), "manifest_SHA256": proof["manifest_sha256"]})
    restored = measure("restore_final_nonmodel_inputs", lambda: restore_full_inputs(full))
    remote._atomic_json(out / "final-input-selection.json", restored)
    original_cost = remote._read(campaign_root / "runtime-identity-v5/refresh-cost-final.json")
    assert Path(original_cost["projection"]["path"]).parents[1] == campaign_root
    remote._atomic_json(out / "original-refresh-timing.json", {
        "elapsed_seconds": original_cost["elapsed_seconds"], "captures": original_cost["captures"],
        "enclosures": original_cost["enclosures"], "cost_file_SHA256": remote._sha(
            campaign_root / "runtime-identity-v5/refresh-cost-final.json")})
    del original_cost, manifest, proof
    reference_runtime = measure("hash_original_runtime_inputs_and_outputs", runtime_census)
    remote._atomic_json(references / "runtime-census.json", reference_runtime)
    index = campaign_root / "observation-index.sqlite"
    original_final = references / "original-final.sqlite"
    def preserve_final_sql():
        with sqlite3.connect(f"file:{index}?mode=ro", uri=True) as source, sqlite3.connect(original_final) as target:
            source.backup(target)
        return remote._index_table_proof(original_final)
    final_proof = measure("preserve_original_final_SQL_outside_mutable_root", preserve_final_sql)
    remote._atomic_json(out / "original-final-logical-proof.json", final_proof)
    training_proof = measure("prove_training_SQL", lambda: remote._index_table_proof(prefix / "observation-index.sqlite"))
    for path in (index, Path(str(index) + "-wal"), Path(str(index) + "-shm")):
        path.unlink(missing_ok=True)
    measure("copy_closed_training_SQL_into_active_campaign", lambda: shutil.copyfile(prefix / "observation-index.sqlite", index))
    assert remote._index_table_proof(index) == training_proof
    # All original data remain in pinned artifacts; remove only this validated temporary mirror.
    assert prefix.resolve().parent == work and prefix.name == "closed-training" and not prefix.is_symlink()
    shutil.rmtree(prefix)
    store = ObservationStoreV5(index, same_trace_parents=True)
    journal = Journal(campaign_root / "attempt-journal.sqlite")
    campaign = SimpleNamespace(ctx=SimpleNamespace(out=campaign_root, journal=journal),
                               collector="deepflow", store=store,
                               plans=remote._read(campaign_root / "plans.json"))
    ingest = measure("reconstruct_exact_final_ingest_from_training", lambda: store.ingest(
        campaign_root / "observations", campaign_root / "native"))
    remote._atomic_json(out / "reconstructed-ingest-summary.json", {
        k: v for k, v in ingest.items() if isinstance(v, (str, int, float, bool))})
    profiler = cProfile.Profile(timer=time.process_time)
    def run_refresh():
        profiler.enable()
        try:
            return refresh(campaign, "final")
        finally:
            profiler.disable()
            profiler.dump_stats(out / "refresh-process-CPU.prof")
            stats = pstats.Stats(profiler)
            rows = [{"file": key[0], "line": key[1], "function": key[2], "primitive_calls": value[0],
                     "total_calls": value[1], "self_process_CPU_seconds": value[2],
                     "cumulative_process_CPU_seconds": value[3]} for key, value in stats.stats.items()]
            remote._atomic_json(out / "profile-top.json", {
                "timer": "time.process_time; process CPU seconds, not wall",
                "top_self": sorted(rows, key=lambda r: r["self_process_CPU_seconds"], reverse=True)[:100],
                "top_cumulative": sorted(rows, key=lambda r: r["cumulative_process_CPU_seconds"], reverse=True)[:100]})
    refreshed = measure("full_unmodified_final_refresh_with_process_CPU_profile", run_refresh)
    store.close()
    store = None
    after_proof = measure("prove_complete_profiled_final_SQL", lambda: remote._index_table_proof(index))
    after_runtime = measure("hash_profiled_runtime_inputs_and_outputs", runtime_census)
    remote._atomic_json(out / "reconstructed-final-logical-proof.json", after_proof)
    remote._atomic_json(out / "runtime-output-equality.json", {
        "original": reference_runtime, "reconstructed": after_runtime, "equal": reference_runtime == after_runtime})
    assert after_proof == final_proof, "Reconstructed final logical tables differ from original"
    assert after_runtime == reference_runtime, "Deterministic original runtime input/output bytes differ"
    status.update(status="complete", all_final_rowid_columns_schema_equal=True,
                  all_deterministic_runtime_input_output_bytes_equal=True,
                  full_final_projection_rows=refreshed["projection"]["rows"],
                  recorded_refresh_elapsed_seconds=refreshed["elapsed_seconds"],
                  scientific_case_or_optimization_admission=False)
except BaseException as error:
    status.update(status="failed", error=repr(error), traceback=traceback.format_exc())
    raise
finally:
    if store is not None:
        store.close()
    if journal is not None:
        journal.close()
    status.update(ended_ns=time.time_ns(), phases=phases)
    remote._atomic_json(out / "status.json", status)
