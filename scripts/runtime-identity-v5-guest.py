#!/usr/bin/env python3
"""Capture guest process/container identity without inferring application topology."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time


COMPOSE_LABELS = {
    "project": "com.docker.compose.project",
    "service": "com.docker.compose.service",
    "container_number": "com.docker.compose.container-number",
    "config_hash": "com.docker.compose.config-hash",
    "oneoff": "com.docker.compose.oneoff",
}


def _clock() -> dict[str, int]:
    return {
        "realtime_unix_ns": time.clock_gettime_ns(time.CLOCK_REALTIME),
        "monotonic_ns": time.clock_gettime_ns(time.CLOCK_MONOTONIC),
        "boottime_ns": time.clock_gettime_ns(time.CLOCK_BOOTTIME),
    }


def _read(path: Path, *, binary: bool = False):
    data = path.read_bytes()
    return data if binary else data.decode("utf-8", errors="surrogateescape")


def _cgroups(pid: int) -> list[dict[str, str]]:
    rows = []
    for line in _read(Path("/proc") / str(pid) / "cgroup").splitlines():
        hierarchy, controllers, path = line.split(":", 2)
        rows.append({"hierarchy": hierarchy, "controllers": controllers, "path": path})
    return rows


def _stat(pid: int) -> tuple[str, str, int]:
    text = _read(Path("/proc") / str(pid) / "stat")
    end = text.rfind(")")
    if end < 0:
        raise ValueError("missing stat comm terminator")
    comm = text[text.find("(") + 1:end]
    remainder = text[end + 2:].split()
    return comm, remainder[0], int(remainder[19])


def _docker() -> tuple[list[dict], dict]:
    command = ["docker", "inspect"]
    listed = subprocess.run(["docker", "ps", "-aq"], text=True, capture_output=True)
    ids = [value for value in listed.stdout.splitlines() if value]
    proof = {"list_command": ["docker", "ps", "-aq"], "list_returncode": listed.returncode,
             "list_stderr": listed.stderr, "inspect_command": command + ids}
    if listed.returncode or not ids:
        proof["inspect_returncode"] = None
        proof["inspect_stderr"] = None
        return [], proof
    inspected = subprocess.run(command + ids, text=True, capture_output=True)
    proof.update(inspect_returncode=inspected.returncode, inspect_stderr=inspected.stderr)
    if inspected.returncode:
        return [], proof
    documents = json.loads(inspected.stdout)
    containers = []
    for item in documents:
        labels = (item.get("Config") or {}).get("Labels") or {}
        state = item.get("State") or {}
        pid = int(state.get("Pid") or 0)
        try:
            init_cgroups = _cgroups(pid) if pid > 0 else []
        except (OSError, ValueError):
            init_cgroups = []
        containers.append({
            "id": item.get("Id"), "name": str(item.get("Name") or "").lstrip("/"),
            "image": item.get("Image"), "config_image": (item.get("Config") or {}).get("Image"),
            "state": {key: state.get(key) for key in
                      ("Status", "Running", "Pid", "StartedAt", "FinishedAt", "ExitCode")},
            "compose": {name: labels.get(label) for name, label in COMPOSE_LABELS.items()},
            "cgroup_parent": (item.get("HostConfig") or {}).get("CgroupParent"),
            "init_cgroups": init_cgroups,
        })
    return containers, proof


def _owner(pid: int, groups: list[dict], containers: list[dict]) -> dict | None:
    candidates: dict[str, tuple[dict, set[str]]] = {}
    group_paths = {item["path"] for item in groups}
    for container in containers:
        identity = container.get("id")
        if not identity:
            continue
        reasons = set()
        if pid == int((container.get("state") or {}).get("Pid") or 0):
            reasons.add("container_init_host_pid")
        init_paths = {item["path"] for item in container.get("init_cgroups", [])}
        # '/' is shared by ordinary host processes and proves no container owner.
        if (group_paths and init_paths and group_paths == init_paths
                and any(path not in ("", "/") for path in group_paths)):
            reasons.add("exact_container_init_cgroup_set")
        if any(identity in path for path in group_paths):
            reasons.add("container_id_in_process_cgroup")
        if reasons:
            candidates[identity] = (container, reasons)
    if len(candidates) != 1:
        return None
    container, reasons = next(iter(candidates.values()))
    return {"container_id": container["id"], "container_name": container["name"],
            "image": container["image"], "config_image": container["config_image"],
            "container_started_at": container["state"].get("StartedAt"),
            "container_running": container["state"].get("Running"),
            "compose": container["compose"], "ownership_proofs": sorted(reasons)}


def capture(node: str, stage: str) -> dict:
    started = _clock()
    boot_id = _read(Path("/proc/sys/kernel/random/boot_id")).strip()
    host_pid_namespace = os.readlink("/proc/1/ns/pid")
    containers, docker_proof = _docker()
    processes, errors = [], []
    for path in sorted(Path("/proc").iterdir(), key=lambda item: item.name):
        if not path.name.isdecimal():
            continue
        pid = int(path.name)
        try:
            comm, state, start_ticks = _stat(pid)
            groups = _cgroups(pid)
            try:
                exe = os.readlink(f"/proc/{pid}/exe")
                exe_error = None
            except OSError as exc:
                exe = None
                exe_error = repr(exc)
            processes.append({
                "host_pid": pid, "state": state, "comm": comm, "start_ticks": start_ticks,
                "pid_namespace": os.readlink(f"/proc/{pid}/ns/pid"),
                "cgroups": groups,
                "exe": exe, "exe_error": exe_error,
                "owner": _owner(pid, groups, containers),
            })
        except (FileNotFoundError, ProcessLookupError):
            continue
        except (OSError, ValueError, IndexError) as exc:
            errors.append({"host_pid": pid, "error": repr(exc)})
    ended = _clock()
    return {
        "schema": "runtime-identity-guest-sample-v5", "node": node, "stage": stage,
        "boot_id": boot_id, "host_pid_namespace": host_pid_namespace,
        "clock_ticks_per_second": os.sysconf("SC_CLK_TCK"),
        "clocks": {"started": started, "ended": ended},
        "containers": containers, "docker_proof": docker_proof,
        "processes": processes, "process_scan_errors": errors,
        "identity_scope": "observed guest host PIDs and actual Docker ownership only",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", required=True)
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()
    print(json.dumps(capture(args.node, args.stage), sort_keys=True, separators=(",", ":")))
