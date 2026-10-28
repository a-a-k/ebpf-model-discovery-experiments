"""Measure one Linux child without intercepting its graceful termination."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def run(command: list[str], report: Path) -> int:
    import resource  # Linux Actions runner; an isolated wrapper has exactly one child.

    if not command:
        raise ValueError("child command is empty")
    report = Path(report)
    report.parent.mkdir(parents=True, exist_ok=True)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started_ns, started_mono = time.time_ns(), time.monotonic()
    child = None
    forwarded: list[int] = []
    child_returncode, wrapper_returncode, error = None, 125, None

    def forward(signum, _frame):
        forwarded.append(signum)
        if child is not None and child.poll() is None:
            child.send_signal(signum)

    prior = {signum: signal.getsignal(signum) for signum in (signal.SIGTERM, signal.SIGINT)}
    for signum in prior:
        signal.signal(signum, forward)
    try:
        child = subprocess.Popen(command)
        for signum in forwarded:
            if child.poll() is None:
                child.send_signal(signum)
        child_returncode = child.wait()
        wrapper_returncode = child_returncode
    except BaseException as exc:
        error = repr(exc)
        if child is not None and child.poll() is None:
            child.send_signal(signal.SIGTERM)
            child_returncode = child.wait()
    finally:
        ended_ns = time.time_ns()
        elapsed = time.monotonic() - started_mono
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        data = {
            "command": command, "started_ns": started_ns, "ended_ns": ended_ns,
            "wall_seconds": elapsed,
            "child_user_seconds": after.ru_utime - before.ru_utime,
            "child_system_seconds": after.ru_stime - before.ru_stime,
            "child_peak_rss_kib": after.ru_maxrss,
            "exit_status": child_returncode,
            "wrapper_exit_status": wrapper_returncode,
            "forwarded_signals": forwarded,
            "scope": "one direct child of isolated Linux wrapper; peak RSS from RUSAGE_CHILDREN",
        }
        if error is not None:
            data["error"] = error
        temporary = report.with_name("." + report.name + ".tmp")
        temporary.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, report)
        for signum, handler in prior.items():
            signal.signal(signum, handler)
    return wrapper_returncode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args()
    command = options.command[1:] if options.command[:1] == ["--"] else options.command
    sys.exit(run(command, options.report))


if __name__ == "__main__":
    main()
