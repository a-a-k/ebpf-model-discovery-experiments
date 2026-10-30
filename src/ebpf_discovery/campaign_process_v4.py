"""Same-runner process supervision around the staged protocol-v4 campaign.

The supervisor survives ordinary GitHub Actions step cleanup, but never treats
PID disappearance as campaign success and never resumes on another host.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time


TECHNICAL_ERROR = 125


def _atomic_json(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _read(path: Path) -> dict | None:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"invalid process marker {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"process marker is not an object: {path}")
    return value


def _start_ticks(pid: int, proc_root: Path = Path("/proc")) -> int:
    # /proc/PID/stat field 22. Parenthesized comm may contain spaces.
    text = (Path(proc_root) / str(pid) / "stat").read_text(encoding="ascii")
    remainder = text[text.rfind(")") + 2:].split()
    return int(remainder[19])


def _identity(args) -> dict:
    run_id = args.run_id or os.environ.get("GITHUB_RUN_ID")
    commit = args.commit or os.environ.get("GITHUB_SHA")
    if not run_id:
        raise RuntimeError("run identity requires --run-id or GITHUB_RUN_ID")
    if not commit:
        raise RuntimeError("run identity requires --commit or GITHUB_SHA")
    return {"run_id": str(run_id), "commit": str(commit), "system": str(args.system),
            "mode": str(args.mode), "seed": int(args.seed)}


def _same_identity(marker: dict, identity: dict) -> bool:
    return all(marker.get(key) == value for key, value in identity.items())


def _live_started(marker: dict, proc_root: Path = Path("/proc")) -> bool:
    try:
        if marker["host"] != socket.gethostname():
            return False
        pid, ticks = int(marker["supervisor_pid"]), int(marker["supervisor_start_ticks"])
        return _start_ticks(pid, proc_root) == ticks
    except (AttributeError, KeyError, TypeError, ValueError, OSError):
        return False


def _validate_live(state_dir: Path, identity: dict, proc_root: Path = Path("/proc")) -> dict:
    marker = _read(Path(state_dir) / "started.json")
    if marker is None or not _same_identity(marker, identity):
        raise RuntimeError("started marker missing or belongs to another campaign cell")
    if not _live_started(marker, proc_root):
        if _read(Path(state_dir) / "exit.json") is not None:
            raise RuntimeError("campaign supervisor already reached its terminal sentinel")
        raise RuntimeError("campaign supervisor disappeared without an atomic terminal sentinel")
    return marker


def _group_members(pgid: int, proc_root: Path = Path("/proc")) -> list[int]:
    """Return live (non-zombie) members of one Linux process group."""
    members = []
    for entry in Path(proc_root).iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            text = entry.joinpath("stat").read_text(encoding="ascii")
            remainder = text[text.rfind(")") + 2:].split()
            # Fields after comm start at state (3), ppid (4), pgrp (5).
            if remainder[0] != "Z" and int(remainder[2]) == pgid:
                members.append(int(entry.name))
        except (FileNotFoundError, PermissionError, OSError, ValueError, IndexError):
            continue
    return sorted(members)


def _wait_group_drain(pgid: int, seconds: float, proc_root: Path = Path("/proc")) -> list[int]:
    deadline = time.monotonic() + seconds
    while True:
        members = _group_members(pgid, proc_root)
        if not members or time.monotonic() >= deadline:
            return members
        time.sleep(.05)


def _terminate_group(process: subprocess.Popen | None, signum: int = signal.SIGTERM,
                     *, grace_seconds: float = 30.0,
                     proc_root: Path = Path("/proc")) -> dict:
    if process is None:
        return {"started": False, "returncode": None, "group_drained": True}
    pgid = process.pid
    sent = False
    members = _group_members(pgid, proc_root)
    if members:
        try:
            os.killpg(pgid, signum)
            sent = True
        except ProcessLookupError:
            pass
    try:
        returncode = process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        returncode = None
    remaining = _wait_group_drain(pgid, grace_seconds, proc_root)
    forced = bool(remaining)
    if forced:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if returncode is None:
            returncode = process.wait()
        remaining = _wait_group_drain(pgid, grace_seconds, proc_root)
    elif returncode is None:
        returncode = process.wait()
    return {"started": True, "pgid": pgid, "signal_sent": sent,
            "forced_kill": forced, "group_drained": not remaining,
            "remaining_pids": remaining, "returncode": returncode}


def _commands(config: dict) -> tuple[list[str], list[str]]:
    root = Path(__file__).resolve().parents[2]
    out = Path(config["out"])
    runner = config.get("runner", "legacy")
    if runner not in ("legacy", "study"):
        raise ValueError("unknown campaign runner")
    if runner == "study" and not config.get("collector"):
        raise ValueError("the study runner requires an explicit collector")
    module = ("ebpf_discovery.study" if runner == "study" else
              "ebpf_discovery.campaign_v5" if config.get("collector") else
              "ebpf_discovery.campaign_v4")
    campaign = [
        "/usr/bin/time", "-v", "-o", str(out / "infrastructure" / "campaign-time.txt"),
        sys.executable, "-m", module,
        "--system", config["system"], "--mode", config["mode"],
        "--seed", str(config["seed"]), "--out", str(out),
        "--training-checkpoint", config["checkpoint"],
        "--toolchain-execution", config.get("toolchain_execution", "local"),
    ]
    if config.get("collector"):
        campaign.extend(["--collector", config["collector"]])
        if config.get("smoke"):
            campaign.append("--smoke")
    resources = ["bash", str(root / "scripts" / "capture-v4-resources.sh"),
                 str(out / "infrastructure" / "resources"), "15", config["vms"]]
    return campaign, resources


def _supervisor_environment() -> dict[str, str]:
    """Preserve runner ownership so job-end cleanup remains a final fallback."""
    return dict(os.environ)


def supervise(config: dict, *, campaign_command: list[str] | None = None,
              resource_command: list[str] | None = None) -> int:
    """Run and supervise one campaign; command overrides are synthetic-test hooks."""
    state_dir = Path(config["state_dir"])
    state_dir.mkdir(parents=True, exist_ok=True)
    log_path = state_dir / "campaign.log"
    identity = {key: config[key] for key in ("run_id", "commit", "system", "mode", "seed")}
    started = {**identity, "schema_version": "campaign-process-v4",
               "supervisor_pid": os.getpid(), "supervisor_start_ticks": _start_ticks(os.getpid()),
               "started_ns": time.time_ns(), "host": socket.gethostname(),
               "log": str(log_path.resolve())}
    _atomic_json(state_dir / "started.json", started)
    campaign = resources = None
    campaign_rc = TECHNICAL_ERROR
    forwarded: list[int] = []

    def forward(signum, _frame):
        forwarded.append(signum)
        for child in (campaign, resources):
            if child is not None and child.poll() is None:
                try:
                    os.killpg(child.pid, signum)
                except ProcessLookupError:
                    pass

    prior = {item: signal.getsignal(item) for item in (signal.SIGTERM, signal.SIGINT)}
    for item in prior:
        signal.signal(item, forward)
    cleanup = {}
    error = None
    try:
        default_campaign, default_resources = _commands(config)
        campaign_command = campaign_command or default_campaign
        resource_command = resource_command or default_resources
        Path(config["out"]).joinpath("infrastructure").mkdir(parents=True, exist_ok=True)
        with log_path.open("ab", buffering=0) as log:
            resources = subprocess.Popen(resource_command, stdin=subprocess.DEVNULL,
                                         stdout=log, stderr=subprocess.STDOUT,
                                         start_new_session=True)
            campaign = subprocess.Popen(campaign_command, stdin=subprocess.DEVNULL,
                                        stdout=log, stderr=subprocess.STDOUT,
                                        start_new_session=True)
            started.update(campaign_pid=campaign.pid,
                           campaign_start_ticks=_start_ticks(campaign.pid),
                           resource_pid=resources.pid,
                           resource_start_ticks=_start_ticks(resources.pid))
            _atomic_json(state_dir / "started.json", started)
            campaign_rc = campaign.wait()
    except BaseException as exc:
        error = repr(exc)
    finally:
        cleanup["campaign"] = _terminate_group(campaign)
        cleanup["resources"] = _terminate_group(resources)
        cleanup_complete = all(item.get("group_drained", False) for item in cleanup.values())
        supervisor_rc = int(campaign_rc) if cleanup_complete else TECHNICAL_ERROR
        for item, handler in prior.items():
            signal.signal(item, handler)
        terminal = {**identity, "schema_version": "campaign-process-v4-exit",
                    "supervisor_pid": os.getpid(),
                    "supervisor_start_ticks": started["supervisor_start_ticks"],
                    "returncode": campaign_rc, "supervisor_returncode": supervisor_rc,
                    "cleanup_complete": cleanup_complete, "ended_ns": time.time_ns(),
                    "forwarded_signals": forwarded, "cleanup": cleanup}
        if error is not None:
            terminal["supervisor_error"] = error
        # This is deliberately last: its presence means child wait and cleanup
        # both happened, never merely that a PID disappeared.
        _atomic_json(state_dir / "exit.json", terminal)
    return supervisor_rc


def _spawn(args) -> int:
    if os.name != "posix" or not Path("/proc/self/stat").is_file():
        raise RuntimeError("campaign process supervision requires Linux /proc")
    state_dir = Path(args.state_dir)
    if (state_dir / "started.json").exists() or (state_dir / "exit.json").exists():
        raise RuntimeError("refusing stale campaign-process state directory")
    identity = _identity(args)
    config = {**identity, "state_dir": str(state_dir.resolve()),
              "out": str(Path(args.out).resolve()),
              "checkpoint": str(Path(args.checkpoint).resolve()),
              "vms": str(Path(args.vms).resolve()),
               "toolchain_execution": args.toolchain_execution,
               "runner": getattr(args, "runner", "legacy")}
    if getattr(args, "collector", None):
        config.update(collector=args.collector, smoke=bool(args.smoke))
    elif getattr(args, "smoke", False):
        raise ValueError("--smoke requires an iteration-5 collector")
    config_path = state_dir / "config.json"
    _atomic_json(config_path, config)
    # Preserve RUNNER_TRACKING_ID: explicit stop is normal cleanup, while the
    # runner must still own and reap the tree on cancellation or job failure.
    environment = _supervisor_environment()
    bootstrap = (state_dir / "bootstrap.log").open("ab", buffering=0)
    process = subprocess.Popen([sys.executable, "-m", "ebpf_discovery.campaign_process_v4",
                                "supervise", "--config", str(config_path)],
                               stdin=subprocess.DEVNULL, stdout=bootstrap,
                               stderr=subprocess.STDOUT, start_new_session=True,
                               close_fds=True, env=environment)
    bootstrap.close()
    while True:
        terminal = _read(state_dir / "exit.json")
        marker = _read(state_dir / "started.json")
        if marker is not None:
            if not _same_identity(marker, identity) or not _live_started(marker):
                raise RuntimeError("new supervisor marker identity/liveness check failed")
            return 0
        if terminal is not None:
            raise RuntimeError(f"campaign supervisor failed before its started marker: {terminal}")
        if process.poll() is not None:
            raise RuntimeError("campaign supervisor exited without atomic state")
        time.sleep(.1)


def _tail_wait(args) -> int:
    identity = _identity(args)
    state_dir, checkpoint = Path(args.state_dir), Path(args.checkpoint)
    log_path, position = state_dir / "campaign.log", 0
    while True:
        if log_path.exists():
            with log_path.open("r", encoding="utf-8", errors="replace") as stream:
                stream.seek(position)
                chunk = stream.read()
                position = stream.tell()
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()
        terminal = _read(state_dir / "exit.json")
        if terminal is not None:
            if not _same_identity(terminal, identity):
                raise RuntimeError("terminal sentinel belongs to another campaign cell")
            if args.until == "exit":
                return int(terminal.get("supervisor_returncode", TECHNICAL_ERROR))
            raise RuntimeError(f"campaign exited before checkpoint release: {terminal}")
        _validate_live(state_dir, identity)
        if args.until == "checkpoint":
            ready = _read(checkpoint / "ready.json")
            if ready is not None:
                if not _same_identity(ready, identity):
                    raise RuntimeError("checkpoint ready marker belongs to another campaign cell")
                return 0
        time.sleep(.25)


def _release(args) -> int:
    identity = _identity(args)
    _validate_live(Path(args.state_dir), identity)
    checkpoint = Path(args.checkpoint)
    ready = _read(checkpoint / "ready.json")
    if ready is None or not _same_identity(ready, identity):
        raise RuntimeError("checkpoint ready marker missing or belongs to another campaign cell")
    if ready.get("manifest_sha256") != args.manifest_sha256:
        raise RuntimeError("release manifest SHA differs from checkpoint ready identity")
    success = args.upload_success == "true"
    if success and not all((args.artifact_id, args.artifact_url, args.artifact_digest)):
        raise RuntimeError("successful checkpoint upload requires artifact ID, URL, and digest")
    release = {**identity, "schema_version": "campaign-process-v4-release",
               "manifest_sha256": ready["manifest_sha256"],
               "upload_success": success, "artifact_id": args.artifact_id,
               "artifact_url": args.artifact_url, "artifact_digest": args.artifact_digest,
               "released_ns": time.time_ns()}
    _atomic_json(checkpoint / "release.json", release)
    return 0


def _stop(args) -> int:
    """Stop only the owned live supervisor and wait for its real exit marker."""
    identity, state_dir = _identity(args), Path(args.state_dir)
    terminal = _read(state_dir / "exit.json")
    if terminal is not None:
        if not _same_identity(terminal, identity):
            raise RuntimeError("terminal sentinel belongs to another campaign cell")
        return 0
    marker = _read(state_dir / "started.json")
    if marker is None:
        # Safe cleanup when an earlier workflow step failed before start.
        return 0
    if not _same_identity(marker, identity):
        raise RuntimeError("refusing to stop supervisor owned by another campaign cell")
    if not _live_started(marker):
        raise RuntimeError("campaign supervisor disappeared without an atomic terminal sentinel")
    pid = int(marker["supervisor_pid"])
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        if _read(state_dir / "exit.json") is None:
            raise RuntimeError("owned supervisor disappeared before stop signal and without terminal sentinel")
    while True:
        terminal = _read(state_dir / "exit.json")
        if terminal is not None:
            if not _same_identity(terminal, identity):
                raise RuntimeError("terminal sentinel belongs to another campaign cell")
            return 0
        if not _live_started(marker):
            raise RuntimeError("owned supervisor exited without writing its atomic terminal sentinel")
        time.sleep(.1)


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--system", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--commit")


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    _common(start)
    start.add_argument("--out", type=Path, required=True)
    start.add_argument("--vms", type=Path, required=True)
    start.add_argument("--toolchain-execution", choices=("local", "worker"), default="local")
    start.add_argument("--collector", choices=("obi", "deepflow", "coroot"))
    start.add_argument("--runner", choices=("legacy", "study"), default="legacy")
    start.add_argument("--smoke", action="store_true")
    wait = commands.add_parser("wait")
    _common(wait)
    wait.add_argument("--until", choices=("checkpoint", "exit"), required=True)
    release = commands.add_parser("release")
    _common(release)
    release.add_argument("--manifest-sha256", required=True)
    release.add_argument("--upload-success", choices=("true", "false"), required=True)
    release.add_argument("--artifact-id")
    release.add_argument("--artifact-url")
    release.add_argument("--artifact-digest")
    stop = commands.add_parser("stop")
    _common(stop)
    supervise_parser = commands.add_parser("supervise", help=argparse.SUPPRESS)
    supervise_parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "start":
            code = _spawn(args)
        elif args.command == "wait":
            code = _tail_wait(args)
        elif args.command == "release":
            code = _release(args)
        elif args.command == "stop":
            code = _stop(args)
        else:
            code = supervise(_read(args.config) or {})
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
