"""Resource control for the two original closed OTel absent captures only."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time


GIB = 1024 ** 3
SWAP_BYTES = 2 * GIB
ORIGINALS = {
    7: ("41781475751", "8166f7d5ed3ef1e5c505cd22aea6745d5ad81070", 13315023235,
        "c91fafafbfaf8a752a19083c882ae29552fb46c5eb916822fbce9568a3683169", 5725603997,
        63496892082, 20434899, 14854103040,
        "2bc2601e7c2db4e69e3671fbf83b03c1994730f17466d45defe924ebb0e28aea"),
    8: ("41816827576", "2fae9a6bdc8519444bb84dcfa74a8fd4f3705932", 13340037317,
        "0bf83d762319dbc6037c9d0d4be42c5e0aea91f90616366961d0505a37a9a639", 5628481016,
        62441989204, 20396308, 14342156288,
        "e62f21be661aa4e68e857fa3056cb81fe573747cc12e62d8fb708b9c57dd0b42"),
}


def _write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _actions_only():
    if os.environ.get("GITHUB_ACTIONS") != "true" or sys.platform != "linux":
        raise RuntimeError("Closed offline resource control is Linux Actions-only")


def _context():
    seed = int(os.environ["CAPTURE_SEED"])
    expected = ORIGINALS[seed]
    actual = (os.environ["SCIENTIFIC_CAPTURE_RUN_ID"], os.environ["SCIENTIFIC_CAPTURE_SOURCE"],
              int(os.environ["CAPTURE_ARTIFACT_ID"]),
              os.environ["CAPTURE_ARTIFACT_DIGEST"].removeprefix("sha256:"),
              int(os.environ["CAPTURE_ARCHIVE_BYTES"]),
              *(int(os.environ[name]) for name in
                ("CAPTURE_FILE_BYTES", "CAPTURE_PROOF_BYTES", "CAPTURE_INDEX_BYTES")),
              os.environ["CAPTURE_MANIFEST_SHA256"])
    if actual != expected or os.environ["CAPTURE_MODE"] != "absent":
        raise ValueError("Resource carrier differs from the exact original closed capture")
    if (os.environ.get("GITHUB_REPOSITORY") != "a-a-k/ebpf-model-discovery-experiments"
            or os.environ["GITHUB_RUN_ID"] == expected[0]):
        raise ValueError("A separate processing run in the original repository is required")
    workspace = Path(os.environ["GITHUB_WORKSPACE"]).resolve()
    if workspace != Path.cwd().resolve():
        raise ValueError("Resource carrier must run in its checked-out workspace")
    work = workspace / "work"
    host = work / "offline-host"
    host.mkdir(parents=True, exist_ok=True)
    file_bytes, proof_bytes, index_bytes = (
        int(os.environ[name]) for name in
        ("CAPTURE_FILE_BYTES", "CAPTURE_PROOF_BYTES", "CAPTURE_INDEX_BYTES"))
    if min(file_bytes, proof_bytes, index_bytes) <= 0:
        raise ValueError("Complete positive original F/P/I metadata is required")
    return {"seed": seed, "capture_run_id": expected[0], "capture_source": expected[1],
            "processing_run_id": os.environ["GITHUB_RUN_ID"],
            "processing_source": os.environ["GITHUB_SHA"], "work": work, "host": host,
            "Z": expected[4], "F": file_bytes, "P": proof_bytes, "I": index_bytes}


def required_before_swap(z, f, p, i):
    if any(type(n) is not int or n <= 0 for n in (z, f, p, i)):
        raise ValueError("Original archive, scientific, proof and index sizes must be positive")
    return max(z + f + p, f + p + 4 * i) + GIB + SWAP_BYTES


def _meminfo():
    return {k: int(v.split()[0]) * 1024 for line in Path("/proc/meminfo").read_text().splitlines()
            for k, v in [line.split(":", 1)]
            if k in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree", "Dirty", "Writeback"}}


def prepare():
    _actions_only()
    c = _context()
    target = c["work"] / "closed-offline-swapfile"
    if target.exists() or target.is_symlink() or target.resolve().parent != c["work"]:
        raise ValueError("Refusing to replace or escape the owned swap path")
    receipt = c["host"] / "resource-prepare.json"
    if receipt.exists():
        raise ValueError("Refusing repeated resource preparation")
    result = {k: c[k] for k in ("seed", "capture_run_id", "capture_source", "processing_run_id",
                                "processing_source", "Z", "F", "P", "I")}
    result.update(status="started", started_ns=time.time_ns(), requested_swap_bytes=SWAP_BYTES,
                  swap_path=str(target), actual_free_before=shutil.disk_usage(c["work"]).free,
                  required_before_allocation=required_before_swap(c["Z"], c["F"], c["P"], c["I"]),
                  memory_sufficiency_or_root_cause_proven=False)
    _write(receipt, result)
    try:
        if result["actual_free_before"] < result["required_before_allocation"]:
            raise RuntimeError("Insufficient actual disk for complete staged restore, 4I reserve and swap")
        result["meminfo_before"] = _meminfo()
        for argv in (["sudo", "install", "-m", "600", "/dev/null", str(target)],
                     ["sudo", "fallocate", "-l", str(SWAP_BYTES), str(target)],
                     ["sudo", "mkswap", str(target)], ["sudo", "swapon", str(target)]):
            completed = subprocess.run(argv, capture_output=True, text=True)
            result.setdefault("allocation_commands", []).append({
                "argv": argv, "returncode": completed.returncode,
                "stdout": completed.stdout, "stderr": completed.stderr})
            _write(receipt, result)
            completed.check_returncode()
        if target.stat().st_size != SWAP_BYTES:
            raise RuntimeError("Owned swap file size differs from the measured request")
        result["meminfo_after"] = _meminfo()
        active = [row.split() for row in Path("/proc/swaps").read_text().splitlines()[1:]]
        owned = [r for r in active if Path(r[0]).resolve() == target]
        if len(owned) != 1 or int(owned[0][2]) * 1024 < SWAP_BYTES - 1024 ** 2:
            raise RuntimeError("Owned swap allocation is not active at its requested size")
        result["active_owned_swap"] = owned[0]
        result["actual_free_after"] = shutil.disk_usage(c["work"]).free
        if result["actual_free_after"] < result["required_before_allocation"] - SWAP_BYTES:
            raise RuntimeError("Remaining disk no longer covers the unchanged complete restore budget")
        result["status"] = "ready"
    except BaseException as error:
        result.update(status="failed", error=repr(error))
        raise
    finally:
        result["ended_ns"] = time.time_ns()
        _write(receipt, result)


def _child_priority():
    os.nice(10)
    score = Path("/proc/self/oom_score_adj")
    score.write_text(str(max(500, int(score.read_text()))))


def _finalize_argv(c):
    return [sys.executable, "-m", "ebpf_discovery.postcapture_v5", "finalize", "--campaign",
            "work/campaign", "--proof", "work/restored-postcapture/postcapture-proof",
            "--capture-run-id", c["capture_run_id"], "--capture-source", c["capture_source"]]


def _sample(child, work):
    row = {"recorded_ns": time.time_ns(), "owned_pid": child.pid,
           "actual_disk_free": shutil.disk_usage(work).free, "host_memory": _meminfo()}
    for name in ("cpu", "memory", "io"):
        try:
            row.setdefault("host_pressure", {})[name] = (Path("/proc/pressure") / name).read_text()
        except OSError as error:
            row.setdefault("host_pressure_error", {})[name] = type(error).__name__
    try:
        proc = Path("/proc") / str(child.pid)
        row["process_status"] = {k: v.strip() for line in (proc / "status").read_text().splitlines()
                                 for k, v in [line.split(":", 1)]
                                 if k in {"Name", "State", "VmRSS", "VmHWM", "VmSize", "VmSwap", "Threads"}}
        row["oom_score_adj"] = int((proc / "oom_score_adj").read_text())
        row["cpu_stat"] = (proc / "stat").read_text()
        row["io"] = (proc / "io").read_text()
    except OSError as error:
        row["process_sample_error"] = type(error).__name__
    return row


def _stop_owned(child):
    if child.poll() is None:
        if os.getpgid(child.pid) != child.pid:
            raise RuntimeError("Refusing to signal an unrelated process group")
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()


def run():
    _actions_only()
    import resource
    c = _context()
    ready = json.loads((c["host"] / "resource-prepare.json").read_text())
    if (ready.get("status") != "ready" or ready.get("capture_source") != c["capture_source"]
            or ready.get("processing_run_id") != c["processing_run_id"]
            or ready.get("processing_source") != c["processing_source"]
            or ready.get("requested_swap_bytes") != SWAP_BYTES):
        raise RuntimeError("Exact measured resource preparation has not completed")
    guard = json.loads((c["host"] / "disk-before-processing.json").read_text())
    if guard.get("required_bytes") != 4 * c["I"] + GIB:
        raise RuntimeError("The original 4I processing reserve differs")
    if shutil.disk_usage(c["work"]).free < guard["required_bytes"]:
        raise RuntimeError("Original processing disk headroom no longer available")
    result_path = c["host"] / "processing-child-result.json"
    if result_path.exists():
        raise RuntimeError("Refusing repeated processing in the same carrier")
    result = {k: c[k] for k in ("seed", "capture_run_id", "capture_source", "processing_run_id", "processing_source")}
    result.update(status="started", started_ns=time.time_ns(), new_application_traffic=False,
                  model_refit=False, priority_policy={"nice_increment": 10, "ionice_class": 2,
                  "ionice_level": 7, "child_oom_score_adj_at_least": 500})
    child = None
    def interrupt(signum, frame):
        raise KeyboardInterrupt("Resource carrier received termination")
    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        argv = ["ionice", "-c", "2", "-n", "7", *_finalize_argv(c)]
        child = subprocess.Popen(argv, start_new_session=True, preexec_fn=_child_priority)
        result.update(owned_pid=child.pid, argv=argv)
        _write(result_path, result)
        with (c["host"] / "processing-resource-samples.jsonl").open("x", encoding="utf-8") as stream:
            while True:
                row = _sample(child, c["work"])
                line = json.dumps(row, separators=(",", ":"))
                stream.write(line + "\n")
                stream.flush()
                print("OFFLINE_RESOURCE " + line, flush=True)
                try:
                    code = child.wait(timeout=30)
                    break
                except subprocess.TimeoutExpired:
                    pass
        result.update(status="complete" if code == 0 else "child_failed", child_returncode=code)
        return code if code >= 0 else 128 - code
    except BaseException as error:
        result.update(status="interrupted_or_failed", error=repr(error))
        raise
    finally:
        if child is not None:
            _stop_owned(child)
            result["final_child_returncode"] = child.returncode
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        result.update(ended_ns=time.time_ns(), child_maxrss_kib=usage.ru_maxrss,
                      child_user_seconds=usage.ru_utime, child_system_seconds=usage.ru_stime)
        _write(result_path, result)
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "run"))
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        raise SystemExit(run())
