"""Run one worker-side writer in an owned process group and join it exactly."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


SCHEMA = "worker-owned-process-group-v4"


def _write(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def verify_lifecycle(evidence_path: Path, source_proof_path: Path, helper_path: Path,
                     workflow_sha: str, gate_path: Path) -> dict:
    errors = []
    def read(path):
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as error:
            errors.append({"file": Path(path).name, "error": repr(error)})
            return {}
    lifecycle = read(evidence_path)
    source = read(source_proof_path)
    helper = Path(helper_path)
    helper_sha, helper_bytes = None, None
    try:
        import hashlib
        payload = helper.read_bytes()
        helper_sha, helper_bytes = hashlib.sha256(payload).hexdigest(), len(payload)
    except OSError as error:
        errors.append({"file": helper.name, "error": repr(error)})
    checks = {
        "lifecycle_schema": lifecycle.get("schema_version") == SCHEMA,
        "lifecycle_status": lifecycle.get("status") == "stopped_and_joined",
        "owned_group_absent": lifecycle.get("group_absent_after_join") is True,
        "no_fixed_quiescence_timeout": (
            lifecycle.get("fixed_quiescence_sleep_or_timeout") is False),
        "stop_signal_observed": signal.SIGTERM in lifecycle.get("stop_signals_received", []),
        "helper_schema": source.get("schema_version") == "worker-lifecycle-helper-source-v4",
        "helper_workflow_sha": source.get("workflow_sha") == workflow_sha,
        "helper_path": source.get("path") == "src/ebpf_discovery/worker_process_group_v4.py",
        "helper_bytes": helper_bytes is not None and helper_bytes == source.get("bytes"),
        "helper_sha256": helper_sha is not None and helper_sha == source.get("sha256"),
    }
    passed = not errors and all(checks.values())
    gate = {"schema_version": "worker-resource-writer-package-gate-v4",
            "status": "verified_quiescent" if passed else "technical_failure",
            "checks": checks, "read_errors": errors,
            "completion_rule": "owned_group_absent_before_environment_is_packaged",
            "complete_typed_package_permitted": passed}
    _write(gate_path, gate)
    return gate


def run(command: list[str], evidence_path: Path, label: str) -> int:
    if os.name != "posix":
        raise RuntimeError("owned worker process groups require POSIX")
    if not command:
        raise ValueError("owned process-group command is empty")
    started_ns, started = time.time_ns(), time.monotonic()
    child = None
    stop_signals: list[int] = []
    unexpected_cleanup_signal_sent = False
    status = "starting"
    error = None

    def stop(signum, _frame):
        stop_signals.append(signum)
        if child is not None:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    handled = (signal.SIGTERM, signal.SIGINT)
    prior = {signum: signal.getsignal(signum) for signum in handled}
    for signum in handled:
        signal.signal(signum, stop)
    try:
        child = subprocess.Popen(command, start_new_session=True)
        status = "running"
        # A stop can arrive after the supervisor is visible to the workflow but
        # before Popen returns. Replay it against the newly owned group.
        if stop_signals:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        returncode = child.wait()
        if stop_signals:
            # The direct child is reaped, but a descendant can retain the owned
            # PGID and an inherited output descriptor.  Wait for the kernel to
            # report the whole group absent; elapsed time is measured, never a
            # timeout or a quiescence substitute.
            while _group_exists(child.pid):
                time.sleep(0.05)
            status = "stopped_and_joined"
            wrapper_returncode = 0
        else:
            if _group_exists(child.pid):
                os.killpg(child.pid, signal.SIGTERM)
                unexpected_cleanup_signal_sent = True
                while _group_exists(child.pid):
                    time.sleep(0.05)
            status = "unexpected_exit"
            wrapper_returncode = 1
    except BaseException as exc:
        error = repr(exc)
        status = "technical_failure"
        wrapper_returncode = 125
        if child is not None:
            if _group_exists(child.pid):
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            if child.poll() is None:
                child.wait()
            while _group_exists(child.pid):
                time.sleep(0.05)
    finally:
        for signum, handler in prior.items():
            signal.signal(signum, handler)
        child_returncode = child.returncode if child is not None else None
        pgid = child.pid if child is not None else None
        group_absent = None
        group_check_error = None
        if pgid is not None:
            try:
                group_absent = not _group_exists(pgid)
            except OSError as exc:
                group_check_error = repr(exc)
        if group_absent is not True and status == "stopped_and_joined":
            status = "technical_failure"
            wrapper_returncode = 125
        evidence = {
            "schema_version": SCHEMA,
            "label": label,
            "command": command,
            "started_ns": started_ns,
            "ended_ns": time.time_ns(),
            "elapsed_seconds": time.monotonic() - started,
            "supervisor_pid": os.getpid(),
            "child_pid": child.pid if child is not None else None,
            "owned_pgid": pgid,
            "stop_signals_received": stop_signals,
            "unexpected_exit_cleanup_signal_sent": unexpected_cleanup_signal_sent,
            "child_returncode": child_returncode,
            "group_absent_after_join": group_absent,
            "status": status,
            "completion_rule": "signal_owned_group_then_wait_for_kernel_group_absence",
            "fixed_quiescence_sleep_or_timeout": False,
        }
        if error is not None:
            evidence["error"] = error
        if group_check_error is not None:
            evidence["group_check_error"] = group_check_error
        _write(evidence_path, evidence)
    return wrapper_returncode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--label")
    parser.add_argument("--verify-lifecycle", action="store_true")
    parser.add_argument("--source-proof", type=Path)
    parser.add_argument("--helper", type=Path)
    parser.add_argument("--workflow-sha")
    parser.add_argument("--gate", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args()
    if options.verify_lifecycle:
        if not all((options.source_proof, options.helper, options.workflow_sha, options.gate)):
            parser.error("lifecycle verification requires source proof, helper, workflow SHA and gate")
        gate = verify_lifecycle(options.evidence, options.source_proof, options.helper,
                                options.workflow_sha, options.gate)
        sys.exit(0 if gate["complete_typed_package_permitted"] else 1)
    if not options.label:
        parser.error("process-group execution requires --label")
    command = options.command[1:] if options.command[:1] == ["--"] else options.command
    sys.exit(run(command, options.evidence, options.label))


if __name__ == "__main__":
    main()
