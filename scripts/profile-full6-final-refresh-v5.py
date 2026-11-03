"""Actions-only full-input profile of the unchanged saved-case final refresh."""
import cProfile
import hashlib
import json
import os
from pathlib import Path
import pstats
import resource
import shutil
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
        print(json.dumps(record), flush=True)


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
    sql_member = None
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
            if name == "observation-index.sqlite":
                sql_member = {"name": name, "bytes": received, "sha256": sha.hexdigest(),
                              "crc32": f"{entry.CRC:08x}"}
            census.update(json.dumps([name, received, sha.hexdigest()], separators=(",", ":")).encode() + b"\n")
            count += 1
            logical += received
    assert sql_member is not None
    return {"selected_files": count, "selected_bytes": logical, "original_final_SQL_member": sql_member,
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
    # Exact pinned-artifact stage bounds, checked again against actual ZIP directories.
    known_training_bytes = 15735636394
    known_training_SQL_bytes = 7664906240
    known_full_nonmodel_bytes = 35776434485
    known_final_SQL_bytes = 14050770944
    full_ZIP_bytes = 5335924987
    margin = 1073741824
    peak = known_full_nonmodel_bytes + known_final_SQL_bytes + full_ZIP_bytes + margin
    free = shutil.disk_usage(work).free
    remote._atomic_json(out / "initial-peak-reservation.json", {
        "available_bytes": free, "required_bytes": peak,
        "basis": "Retained full ZIP plus full nonmodel tree, final SQLite-sized WAL allowance and 1GiB; no simultaneous training mirror or redundant decoded SQL reference."})
    assert free >= peak
    training = measure("download_exact_training", lambda: artifact(
        13162514595, 1864728289, "709e6c4f3e8af5dd9dfadb31b2c90c28449ca3a635be31c1cb5363fc3e6ba36e"))
    with zipfile.ZipFile(training) as left:
        training_bytes = sum(e.file_size for e in left.infolist() if not e.is_dir())
    assert training_bytes == known_training_bytes
    free = shutil.disk_usage(work).free
    remote._atomic_json(out / "training-restore-disk-guard.json", {
        "available_bytes": free, "required_bytes": training_bytes + margin})
    assert free >= training_bytes + margin
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
    training_index = prefix / "observation-index.sqlite"
    assert training_index.stat().st_size == known_training_SQL_bytes
    training_SHA = remote._sha(training_index)
    assert training_SHA == "c36fdfafd41dea71b12e06744c2988e01a3e20bdb5c295093ea9b4a77186b745"
    training_proof = measure("prove_training_SQL", lambda: remote._index_table_proof(training_index))
    training_reference = references / "closed-training.sqlite"
    before = training_index.stat()
    os.replace(training_index, training_reference)
    after = training_reference.stat()
    assert (before.st_dev, before.st_ino, before.st_size) == (after.st_dev, after.st_ino, after.st_size)
    assert remote._sha(training_reference) == training_SHA
    del manifest, proof
    assert prefix.resolve().parent == work and prefix.name == "closed-training" and not prefix.is_symlink()
    measure("release_validated_training_mirror_after_SQL_move", lambda: shutil.rmtree(prefix))
    measure("release_verified_downloaded_training_ZIP", training.unlink)
    remote._atomic_json(out / "training-reference.json", {
        "bytes": after.st_size, "sha256": training_SHA, "same_inode_move": True,
        "complete_logical_proof": training_proof, "original_remote_artifact_retained": 13162514595})
    free = shutil.disk_usage(work).free
    required = full_ZIP_bytes + known_full_nonmodel_bytes + margin
    remote._atomic_json(out / "final-download-restore-disk-guard.json", {
        "available_bytes": free, "required_bytes": required})
    assert free >= required
    full = measure("download_exact_final", lambda: artifact(
        13180555929, full_ZIP_bytes, "7541e1387ba9311fc8b4c09eb3685d8b6dbc4774cad035e72cabf128661db26d"))
    with zipfile.ZipFile(full) as right:
        full_bytes = sum(e.file_size for e in right.infolist()
                         if not e.is_dir() and not e.filename.startswith(("toolchain/", "toolchain-build/")))
        final_index_bytes = right.getinfo("observation-index.sqlite").file_size
    assert (full_bytes, final_index_bytes) == (known_full_nonmodel_bytes, known_final_SQL_bytes)
    assert shutil.disk_usage(work).free >= full_bytes + margin
    os.chmod(full, 0o444)
    restored = measure("restore_final_nonmodel_inputs", lambda: restore_full_inputs(full))
    remote._atomic_json(out / "final-input-selection.json", restored)
    original_cost = remote._read(campaign_root / "runtime-identity-v5/refresh-cost-final.json")
    assert Path(original_cost["projection"]["path"]).parents[1] == campaign_root
    remote._atomic_json(out / "original-refresh-timing.json", {
        "elapsed_seconds": original_cost["elapsed_seconds"], "captures": original_cost["captures"],
        "enclosures": original_cost["enclosures"], "cost_file_SHA256": remote._sha(
            campaign_root / "runtime-identity-v5/refresh-cost-final.json")})
    del original_cost
    reference_runtime = measure("hash_original_runtime_inputs_and_outputs", runtime_census)
    remote._atomic_json(references / "runtime-census.json", reference_runtime)
    index = campaign_root / "observation-index.sqlite"
    original_final = references / "original-final.sqlite"
    for path in (Path(str(index) + "-wal"), Path(str(index) + "-shm")):
        assert not path.exists() or path.stat().st_size == 0, "Original final SQLite must be closed/checkpointed"
        path.unlink(missing_ok=True)
    before = index.stat()
    os.replace(index, original_final)
    after = original_final.stat()
    assert (before.st_dev, before.st_ino, before.st_size) == (after.st_dev, after.st_ino, after.st_size)
    os.chmod(original_final, 0o444)
    assert remote._sha(original_final) == restored["original_final_SQL_member"]["sha256"]
    final_proof = measure("prove_original_final_SQL_before_last_read_release",
                          lambda: remote._index_table_proof(original_final))
    remote._atomic_json(out / "original-final-logical-proof.json", final_proof)
    remote._atomic_json(references / "encoded-original-final-SQL.json", {
        "archive": str(full), "archive_sha256": "7541e1387ba9311fc8b4c09eb3685d8b6dbc4774cad035e72cabf128661db26d",
        "complete_SQL_member": restored["original_final_SQL_member"], "logical_proof": final_proof,
        "source": "Unchanged readonly original full ZIP retains every original SQLite byte; decoded redundant file has had its last reference read."})
    measure("release_only_redundant_decoded_SQL_reference", original_final.unlink)
    os.replace(training_reference, index)
    assert remote._sha(index) == training_SHA
    assert remote._index_table_proof(index) == training_proof
    removed_outputs = {}
    for name in ("projection-final.jsonl", "supplied-alias-scope-final.json"):
        path = campaign_root / "runtime-identity-v5" / name
        removed_outputs[name] = {"bytes": path.stat().st_size, "sha256": remote._sha(path)}
        path.unlink()
    remote._atomic_json(out / "removed_derived_final_outputs_to_be_recreated.json", removed_outputs)
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
    encoded_SHA = measure("verify_immutable_encoded_SQL_reference_after_profile", lambda: remote._sha(full))
    assert encoded_SHA == "7541e1387ba9311fc8b4c09eb3685d8b6dbc4774cad035e72cabf128661db26d"
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
