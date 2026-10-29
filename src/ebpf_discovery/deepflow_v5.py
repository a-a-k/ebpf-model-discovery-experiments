"""Pinned DeepFlow v7.2.3 standalone lifecycle for iteration 5.

DeepFlow writes flat JSONL on each guest rather than OTLP.  Immutable snapshots
are copied and decoded losslessly by :mod:`deepflow_codec_v5`; the native OTLP
receiver remains unchanged.  No PID, kernel command, endpoint, or expected
deployment identity is promoted to ``service.name``.
"""
from __future__ import annotations

import hashlib
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from .collectors_v5 import (
    CollectorsV5,
    _attributes,
    _returncode,
    _sha256_file,
    _stderr,
    _stdout,
    _write_json,
)
from .deepflow_codec_v5 import (
    DEEPFLOW_SOURCE_COMMIT,
    DEEPFLOW_VERSION,
    SOURCE_CLOCK,
    codec_file,
)


DEEPFLOW_IMAGE = (
    "deepflowce/deepflow-agent:v7.2.3@"
    "sha256:5f72c0996fdb5008fdb8fd0524f427a895fc54c61690b26ba2cae648929ea95a"
)
DEEPFLOW_CONTAINER = "study-deepflow-v5"
MAX_DATA_FILE_SIZE_MIB = 1_048_576
MAX_DATA_FILE_SIZE_BYTES = 1 << 40
NATIVE_RECEIVER_PORT = 4319
DEEPFLOW_EBPF_READY_MARKER = "ebpf collector started"
MIB = 1 << 20


def _config(*, max_memory_mib: int, max_millicpus: int) -> dict[str, Any]:
    if max_memory_mib <= 0 or max_millicpus <= 0:
        raise ValueError("DeepFlow resource limits must be positive guest envelopes")
    return {
        "global": {
            "communication": {"proactive_request_interval": "10s"},
            "limits": {
                # DeepFlow's pinned deser_u64_with_mega_unit expands MiB to bytes.
                "max_memory": max_memory_mib,
                "max_millicpus": max_millicpus,
            },
            "standalone_mode": {
                "max_data_file_size": MAX_DATA_FILE_SIZE_MIB,
                "data_file_dir": "/var/log/deepflow-agent/",
            },
        },
        # Continuous CPU profiling is unrelated to L7 request collection and
        # loads an additional DWARF-unwind BPF program during agent startup.
        "inputs": {
            "ebpf": {
                "profile": {
                    "on_cpu": {"disabled": True},
                }
            }
        },
        "processors": {
            "request_log": {
                "tag_extraction": {
                    "tracing_tag": {
                        "x_request_id": ["x-experiment-request-id"],
                    }
                }
            }
        },
    }


class DeepFlowCollectorsV5(CollectorsV5):
    collector = "deepflow"
    container_name = DEEPFLOW_CONTAINER
    image = DEEPFLOW_IMAGE
    source_version = DEEPFLOW_VERSION
    source_commit = DEEPFLOW_SOURCE_COMMIT
    stop_grace_seconds = 30

    def __init__(self, ctx, *, semantic: bool = True):
        super().__init__(ctx, semantic=semantic)
        self.remote_roots: dict[str, str] = {}
        self.filesystem_capacity: dict[str, int] = {}
        self.guest_context: dict[str, dict[str, str]] = {}
        self.runtime_clocks: dict[str, dict[str, Any]] = {}
        self.resource_inventory: dict[str, dict[str, Any]] = {}
        self._seen: set[tuple[str, int, str]] = set()
        self._seen_offsets: dict[tuple[str, int], str] = {}
        self._prefixes: dict[str, dict[str, dict[str, Any]]] = {"a": {}, "b": {}}
        self._capture_counter = 0
        self._capture_evidence: list[dict[str, Any]] = []
        self._startup_complete = False
        self._startup_helper_nodes: set[str] = set()
        self._startup_agent_attempted_nodes: set[str] = set()

    def _write_clock_relation(self, node: str, config: Path,
                              runtime_command: str) -> dict[str, Any]:
        """Retain the pinned same-guest timestamp construction; never estimate an offset."""
        guest = self.guest_context[node]
        campaign_root = self.root.parent
        path = campaign_root / "runtime-identity-v5" / f"clock-relation-{node}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        declaration = {
            "schema": "runtime-identity-clock-relation-v5",
            "node": node,
            "boot_id": guest["boot_id"],
            "pid_namespace": guest["pid_namespace"],
            "domain": "guest_realtime_unix_ns",
            "relation": "documented_same_guest_realtime_relation",
            "producer": {
                "name": "deepflow-agent", "version": self.source_version,
                "source_commit": self.source_commit,
                "image": self.image,
                "runtime_command": runtime_command,
                "pinned_source_paths": [
                    "agent/src/ebpf/user/utils.h",
                    "agent/src/ebpf/user/socket.h",
                    "agent/src/ebpf/user/tracer.c",
                    "agent/src/ebpf_dispatcher.rs",
                    "agent/src/trident.rs",
                ],
                "timestamp_construction": (
                    "kernel monotonic event timestamp plus a same-guest "
                    "CLOCK_REALTIME-CLOCK_MONOTONIC offset refreshed by the pinned producer"
                ),
            },
            "runtime_configuration": {
                "path": config.relative_to(campaign_root).as_posix(),
                "sha256": _sha256_file(config), "bytes": config.stat().st_size,
                "event_clock_adjustment_to_external_domain_enabled": False,
                "producer_mode": "standalone_controller_ntp_disabled",
                "validated_effective_facts": {
                    "standalone_mode_config_present": True,
                    "standalone_cli_enabled": True,
                    "controller_ntp_correction_enabled": False,
                },
            },
            "event_serialization": {
                "fields": ["start_time", "end_time"], "unit": "microseconds",
                "unix_nanosecond_conversion": "exact_integer_multiply_by_1000",
                "quantization_ns": 1000,
            },
            "host_receipt_time_used": False,
            "empirical_endpoint_offsets_used_as_hard_bound": False,
            "arbitrary_tolerance_or_age_filter_used": False,
            "clock_step_limitation_retained": True,
            "limitation": (
                "an unseen guest realtime clock step between retained lifecycle samples is not "
                "excluded; the relation establishes a shared semantic clock domain, not a "
                "universal adjustment bound"
            ),
        }
        _write_json(path, declaration)
        evidence = {
            "kind": "documented_clock_relation",
            "locator": path.relative_to(campaign_root).as_posix(),
            "sha256": _sha256_file(path), "bytes": path.stat().st_size,
        }
        return {"domain": declaration["domain"], "relation": declaration["relation"],
                "evidence": evidence}

    def _start_receivers(self) -> None:
        """DeepFlow is file-backed; only the unchanged native OTLP path listens."""
        node = "native"
        log = (self.root / "receiver-native.log").open("w", encoding="utf-8")
        self.logs.append(log)
        command = [
            sys.executable, "-m", "ebpf_discovery.receiver_v5",
            "--port", str(NATIVE_RECEIVER_PORT),
            "--out", str(self.root / "native.jsonl"),
            "--source", "native", "--node", node,
            "--checkpoint", str(self.root / "receiver-closed-native.json"),
        ]
        self.processes[node] = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT
        )
        self._wait_receiver(node, NATIVE_RECEIVER_PORT)

    def _wait_receiver(self, node: str, port: int) -> None:
        import socket
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            process = self.processes[node]
            if process.poll() is not None:
                raise RuntimeError(f"OTLP receiver {node} exited during startup")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    return
            except OSError:
                time.sleep(0.1)
        raise RuntimeError(f"OTLP receiver {node} did not become ready")

    def start(self) -> None:
        if self.started_ns is not None:
            raise RuntimeError("DeepFlow collector lifecycle cannot be restarted")
        # This override creates its own receivers and containers, so it must
        # enter the common lifecycle before any of those resources are made.
        self._start_entered = True
        self.started_ns = time.time_ns()
        try:
            self._start_impl()
        except BaseException as exc:
            cleanup = self._cleanup_incomplete_start()
            evidence = {
                "schema": "deepflow-startup-failure-v5",
                "collector": self.collector,
                "started_ns": self.started_ns,
                "failed_ns": time.time_ns(),
                "startup_complete": False,
                "original_error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "repr": repr(exc),
                },
                "cleanup": cleanup,
                "collector_closed_checkpoint": False,
                "accepted_receiver_bytes_closed_and_hashed": False,
                "scope": "best-effort cleanup after incomplete startup; no drain or closed collector claim",
            }
            try:
                _write_json(self.root / "startup-failure.json", evidence)
            except Exception:
                # Never replace the original technical failure with evidence-writing failure.
                pass
            raise
        self._startup_complete = True

    def _inventory_command(self, node: str, command: str) -> dict[str, Any]:
        started_ns = time.time_ns()
        result = self.ctx.node_exec(node, command, timeout=30, check=False)
        finished_ns = time.time_ns()
        record = {
            "command": command,
            "started_ns": started_ns,
            "finished_ns": finished_ns,
            "duration_ns": finished_ns - started_ns,
            "returncode": _returncode(result),
            "stdout": _stdout(result),
            "stderr": _stderr(result),
        }
        if record["returncode"] != 0:
            raise RuntimeError(f"DeepFlow resource inventory command failed on {node}: {command}")
        return record

    def _guest_resource_inventory(self, node: str) -> dict[str, Any]:
        meminfo = self._inventory_command(node, "cat /proc/meminfo")
        cpu = self._inventory_command(node, "nproc")
        cpu_tool = self._inventory_command(node, "nproc --version | head -n 1")
        matches = re.findall(r"^MemTotal:\s*([0-9]+)\s+kB\s*$", meminfo["stdout"], re.MULTILINE)
        if len(matches) != 1:
            raise RuntimeError(f"cannot parse unique MemTotal from guest {node}")
        try:
            mem_total_kib = int(matches[0])
            cpu_count = int(cpu["stdout"].strip())
        except ValueError as exc:
            raise RuntimeError(f"cannot parse guest resource inventory on {node}") from exc
        if mem_total_kib <= 0 or cpu_count <= 0:
            raise RuntimeError(f"non-positive guest resource inventory on {node}")
        max_memory = ((mem_total_kib + 1023) // 1024) * MIB
        inventory = {
            "schema": "deepflow-guest-resource-inventory-v5",
            "node": node,
            "derivation": {
                "max_memory": "ceil(MemTotal_kB / 1024) MiB",
                "max_millicpus": "nproc * 1000",
                "scope": "same guest-wide resource envelope; not infinite",
            },
            "source_paths": ["/proc/meminfo", "nproc"],
            "commands": {"meminfo": meminfo, "cpu_count": cpu, "cpu_tool": cpu_tool},
            "parsed": {
                "mem_total_kib": mem_total_kib,
                "cpu_count": cpu_count,
                "cpu_count_scope": "available processing units reported by nproc",
                "max_memory_bytes": max_memory,
                "max_memory_mib": max_memory // MIB,
                "max_millicpus": cpu_count * 1000,
            },
            "effective_container_constraints": None,
        }
        self.resource_inventory[node] = inventory
        self._write_resource_inventory(node)
        return inventory

    def _write_resource_inventory(self, node: str) -> Path:
        path = self.root / f"resource-inventory-{node}.json"
        _write_json(path, self.resource_inventory[node])
        return path

    def _verify_container_resource_envelope(self, node: str) -> None:
        inventory = self.resource_inventory[node]
        parsed = inventory["parsed"]
        evidence: dict[str, Any] = {"verification_complete": False}
        inventory["effective_container_constraints"] = evidence
        docker = self._inventory_command(
            node,
            f"docker inspect --format '{{{{json .HostConfig}}}}' {self.container_name}",
        )
        evidence["docker"] = docker
        self._write_resource_inventory(node)
        try:
            resources = json.loads(docker["stdout"])
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"cannot parse Docker resource constraints on {node}") from exc
        memory = int(resources.get("Memory", 0) or 0)
        nano_cpus = int(resources.get("NanoCpus", 0) or 0)
        cpu_quota = int(resources.get("CpuQuota", 0) or 0)
        cpu_period = int(resources.get("CpuPeriod", 0) or 0)
        if memory > 0 and memory < parsed["max_memory_bytes"]:
            raise RuntimeError(f"Docker memory limit is below guest envelope on {node}")
        requested_nano_cpus = parsed["max_millicpus"] * 1_000_000
        if nano_cpus > 0 and nano_cpus < requested_nano_cpus:
            raise RuntimeError(f"Docker CPU limit is below guest envelope on {node}")
        if cpu_quota > 0 and cpu_period > 0:
            quota_millicpus = cpu_quota * 1000 // cpu_period
            if quota_millicpus < parsed["max_millicpus"]:
                raise RuntimeError(f"Docker CPU quota is below guest envelope on {node}")
        pid_result = self._inventory_command(
            node, f"docker inspect --format '{{{{.State.Pid}}}}' {self.container_name}",
        )
        try:
            host_pid = int(pid_result["stdout"].strip())
        except ValueError as exc:
            raise RuntimeError(f"cannot parse DeepFlow container host PID on {node}") from exc
        if host_pid <= 0:
            raise RuntimeError(f"invalid DeepFlow container host PID on {node}")
        evidence["host_pid"] = host_pid
        evidence["host_pid_command"] = pid_result
        self._write_resource_inventory(node)
        hierarchy_script = (
            f"pid={host_pid}; "
            "printf 'host_pid=%s\\n' \"$pid\"; "
            "printf 'cgroup_file_begin\\n'; cat \"/proc/$pid/cgroup\"; "
            "printf 'cgroup_file_end\\n'; "
            "cg=$(awk -F: '$1 == \"0\" {print $3}' \"/proc/$pid/cgroup\"); "
            "test -n \"$cg\"; p=\"$cg\"; "
            "while :; do base=\"/sys/fs/cgroup$p\"; "
            "if test -d \"$base\"; then printf 'visit|%s|directory\\n' \"$p\"; "
            "else printf 'visit|%s|missing\\n' \"$p\"; fi; "
            "for f in memory.max cpu.max; do if test -r \"$base/$f\"; then "
            "printf 'limit|%s|%s|' \"$p\" \"$f\"; cat \"$base/$f\"; "
            "elif test -e \"$base/$f\"; then printf 'control|%s|%s|unreadable\\n' \"$p\" \"$f\"; "
            "else printf 'control|%s|%s|absent\\n' \"$p\" \"$f\"; fi; done; "
            "test \"$p\" = / && break; p=$(dirname \"$p\"); done"
        )
        hierarchy = self._inventory_command(
            node, "sudo sh -c " + shlex.quote(hierarchy_script),
        )
        evidence["cgroup_hierarchy"] = hierarchy
        self._write_resource_inventory(node)
        limits: list[dict[str, str]] = []
        visits: list[dict[str, str]] = []
        controls: list[dict[str, str]] = []
        for line in hierarchy["stdout"].splitlines():
            parts = line.split("|", 3)
            if line.startswith("limit|"):
                if len(parts) != 4 or not parts[1].startswith("/"):
                    raise RuntimeError(f"cannot parse cgroup hierarchy limit on {node}")
                limits.append({"path": parts[1], "kind": parts[2], "value": parts[3]})
            elif line.startswith("visit|"):
                if len(parts) != 3 or not parts[1].startswith("/"):
                    raise RuntimeError(f"cannot parse cgroup hierarchy visit on {node}")
                visits.append({"path": parts[1], "status": parts[2]})
            elif line.startswith("control|"):
                if (len(parts) != 4 or not parts[1].startswith("/")
                        or parts[3] not in {"absent", "unreadable"}):
                    raise RuntimeError(f"cannot parse cgroup control evidence on {node}")
                controls.append({"path": parts[1], "kind": parts[2], "status": parts[3]})
        evidence["cgroup_hard_limits_leaf_to_root"] = limits
        evidence["cgroup_directory_visits_leaf_to_root"] = visits
        evidence["cgroup_missing_or_unreadable_controls"] = controls
        self._write_resource_inventory(node)
        root_visits = [item for item in visits if item["path"] == "/"]
        if not limits or root_visits != [{"path": "/", "status": "directory"}]:
            raise RuntimeError(f"incomplete container cgroup hierarchy on {node}")
        if any(item["status"] != "directory" for item in visits):
            raise RuntimeError(f"unreadable container cgroup hierarchy directory on {node}")
        root_controls = [item for item in controls if item["path"] == "/"]
        if any(item["status"] != "absent" for item in root_controls):
            raise RuntimeError(f"unreadable root cgroup control evidence on {node}")
        nonroot_paths = {item["path"] for item in visits if item["path"] != "/"}
        readable_nonroot = {(item["path"], item["kind"]) for item in limits
                            if item["path"] != "/"}
        expected_nonroot = {(path, kind) for path in nonroot_paths
                            for kind in ("memory.max", "cpu.max")}
        if (readable_nonroot != expected_nonroot
                or any(item["path"] != "/" for item in controls)):
            raise RuntimeError(f"missing non-root cgroup hard-limit evidence on {node}")

        def hard_limit(kind: str, value: str) -> int | None:
            if kind == "memory.max":
                if value == "max":
                    return None
                return int(value)
            quota, period = value.split()
            if quota == "max":
                return None
            return int(quota) * 1000 // int(period)

        shared_hard_limit_below_declared: dict[str, bool] = {}
        effective_shared_ancestor_hard_limit: dict[str, int | None] = {}
        for kind, declared in (
            ("memory.max", parsed["max_memory_bytes"]),
            ("cpu.max", parsed["max_millicpus"]),
        ):
            chain = [item for item in limits if item["kind"] == kind]
            if not chain:
                raise RuntimeError(f"missing {kind} cgroup hierarchy on {node}")
            try:
                leaf_limit = hard_limit(kind, chain[0]["value"])
                ancestor_limits = [hard_limit(kind, item["value"]) for item in chain[1:]]
            except (ValueError, ZeroDivisionError) as exc:
                raise RuntimeError(f"cannot parse {kind} cgroup hierarchy on {node}") from exc
            finite_ancestors = [parent for parent in ancestor_limits if parent is not None]
            shared_ancestor_limit = min(finite_ancestors) if finite_ancestors else None
            below = leaf_limit is not None and leaf_limit < declared
            extra_collector_limit = below and (
                shared_ancestor_limit is None or leaf_limit < shared_ancestor_limit
            )
            if extra_collector_limit:
                raise RuntimeError(f"collector-specific {kind} is below guest envelope on {node}")
            effective_shared_ancestor_hard_limit[kind] = shared_ancestor_limit
            shared_hard_limit_below_declared[kind] = bool(
                shared_ancestor_limit is not None and shared_ancestor_limit < declared
            )
        cgroup = self._inventory_command(
            node,
            f"docker exec {self.container_name} sh -c "
            + shlex.quote(
                "test -r /sys/fs/cgroup/memory.max && "
                "printf 'memory.max=' && cat /sys/fs/cgroup/memory.max && "
                "printf 'cpu.max=' && cat /sys/fs/cgroup/cpu.max && "
                "printf 'nproc=' && nproc"
            ),
        )
        evidence["cgroup"] = cgroup
        self._write_resource_inventory(node)
        values = dict(
            line.split("=", 1) for line in cgroup["stdout"].splitlines() if "=" in line
        )
        memory_max = values.get("memory.max", "")
        cpu_max = values.get("cpu.max", "")
        try:
            namespace_memory_limit = hard_limit("memory.max", memory_max)
        except ValueError as exc:
            raise RuntimeError(f"cannot parse container memory.max on {node}") from exc
        cpu_parts = cpu_max.split()
        if len(cpu_parts) != 2:
            raise RuntimeError(f"cannot parse container cpu.max on {node}")
        try:
            namespace_cpu_limit = hard_limit("cpu.max", cpu_max)
        except (ValueError, ZeroDivisionError) as exc:
            raise RuntimeError(f"cannot parse container cpu.max on {node}") from exc
        leaf_by_kind = {
            kind: hard_limit(kind, next(item["value"] for item in limits if item["kind"] == kind))
            for kind in ("memory.max", "cpu.max")
        }
        if (namespace_memory_limit != leaf_by_kind["memory.max"]
                or namespace_cpu_limit != leaf_by_kind["cpu.max"]):
            raise RuntimeError(f"container and host cgroup hard-limit views disagree on {node}")
        try:
            container_cpus = int(values.get("nproc", ""))
        except ValueError as exc:
            raise RuntimeError(f"cannot parse container nproc on {node}") from exc
        if container_cpus * 1000 < parsed["max_millicpus"]:
            raise RuntimeError(f"container CPU availability is below guest envelope on {node}")
        evidence.update({
            "docker_resources": resources,
            "hierarchy_complete_to_root": True,
            "root_controls_expected": False,
            "root_visit_is_traversal_evidence_not_unlimited_limit": True,
            "shared_hard_limit_below_declared_guest_envelope": shared_hard_limit_below_declared,
            "effective_shared_ancestor_hard_limit": effective_shared_ancestor_hard_limit,
            "cgroup_values": values,
            "verified_no_explicit_docker_hard_limit_below_guest_envelope": True,
            "leaf_and_ancestor_hard_limits_retained": True,
            "soft_weights_and_memory_high_not_treated_as_hard_caps": True,
            "verification_complete": True,
        })
        command_records = list(inventory["commands"].values()) + [
            docker, pid_result, hierarchy, cgroup,
        ]
        inventory["capture_cost"] = {
            "remote_command_count": len(command_records),
            "observed_command_duration_ns": sum(item["duration_ns"] for item in command_records),
            "monetary_cost_scope": "included in the enclosing campaign Action runtime",
        }
        self._write_resource_inventory(node)

    def _start_impl(self) -> None:
        self._start_receivers()
        helper = Path(__file__).with_name("deepflow_snapshot_v5.py")
        commands, configs, capacities = {}, {}, {}
        for node in ("a", "b"):
            created = self.ctx.node_exec(
                node,
                "sudo mkdir -p /opt/ebpf-study && "
                "sudo chown $(id -u):$(id -g) /opt/ebpf-study && "
                "mktemp -d /opt/ebpf-study/deepflow-v5.XXXXXX",
                timeout=60,
            )
            remote = _stdout(created).strip()
            if not remote.startswith("/opt/ebpf-study/deepflow-v5."):
                raise RuntimeError(f"unexpected DeepFlow temporary directory on {node}: {remote!r}")
            self.remote_roots[node] = remote
            self.ctx.node_exec(
                node, f"mkdir -p {shlex.quote(remote + '/data')} {shlex.quote(remote + '/snapshots')}",
                timeout=30,
            )
            capacity_result = self.ctx.node_exec(
                node,
                f"df -B1 --output=size {shlex.quote(remote + '/data')} | tail -n 1",
                timeout=30,
            )
            try:
                capacity = int(_stdout(capacity_result).strip())
            except ValueError as exc:
                raise RuntimeError(f"cannot parse guest filesystem capacity on {node}") from exc
            if capacity >= MAX_DATA_FILE_SIZE_BYTES:
                raise RuntimeError(
                    f"DeepFlow 1 TiB rotation threshold does not exceed guest {node} capacity {capacity}"
                )
            capacities[node] = capacity
            self.filesystem_capacity[node] = capacity
            boot_id = _stdout(self.ctx.node_exec(
                node, "cat /proc/sys/kernel/random/boot_id", timeout=30
            )).strip()
            pid_namespace = _stdout(self.ctx.node_exec(
                node, "sudo readlink /proc/1/ns/pid", timeout=30
            )).strip()
            if not boot_id or not pid_namespace:
                raise RuntimeError(f"guest boot/PID namespace identity unavailable on {node}")
            self.guest_context[node] = {
                "boot_id": boot_id,
                "pid_namespace": pid_namespace,
            }
            inventory = self._guest_resource_inventory(node)
            limits = inventory["parsed"]
            config = self.root / f"deepflow-agent-standalone-{node}.yaml"
            config.write_text(
                yaml.safe_dump(
                    _config(
                        max_memory_mib=limits["max_memory_mib"],
                        max_millicpus=limits["max_millicpus"],
                    ),
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            remote_config = remote + "/deepflow-agent-standalone.yaml"
            remote_helper = remote + "/deepflow_snapshot_v5.py"
            self.ctx.node_put(node, config, remote_config)
            self.ctx.node_put(node, helper, remote_helper)
            self._startup_helper_nodes.add(node)
            configs[node] = {
                "path": config.name,
                "sha256": _sha256_file(config),
                "remote_path": remote_config,
                "snapshot_helper_sha256": _sha256_file(helper),
            }
            pull = self.ctx.node_exec(node, f"docker pull {shlex.quote(self.image)}", timeout=600)
            (self.root / f"pull-{node}.log").write_text(
                _stdout(pull) + _stderr(pull), encoding="utf-8"
            )
            self.ctx.node_exec(
                node, f"docker rm -f {self.container_name} >/dev/null 2>&1 || true",
                timeout=60, check=False,
            )
            command = self._docker_command(node, remote_config, NATIVE_RECEIVER_PORT)
            commands[node] = command
            self.runtime_clocks[node] = self._write_clock_relation(node, config, command)
            # The transport result can be lost after Docker accepted the run.
            self._startup_agent_attempted_nodes.add(node)
            self.ctx.node_exec(node, command, timeout=180)
            self._verify_container_resource_envelope(node)
            inventory_path = self._write_resource_inventory(node)
            configs[node]["resource_inventory_path"] = inventory_path.name
            configs[node]["resource_inventory_sha256"] = _sha256_file(inventory_path)
            inspect = self.ctx.node_exec(
                node, f"docker image inspect {shlex.quote(self.image)}", timeout=60
            )
            (self.root / f"image-{node}.json").write_text(_stdout(inspect), encoding="utf-8")
        self._wait_container_readiness()
        self._write_collector_metadata({
            "schema": "collector-lifecycle-v5",
            "collector": self.collector,
            "source_domain": self.source_domain,
            "source_version": self.source_version,
            "source_commit": self.source_commit,
            "image": self.image,
            "config_summary": self._config_summary(),
            "nodes": ["a", "b"],
            "receiver_ports": {"native": NATIVE_RECEIVER_PORT},
            "raw_capture": "standalone flat JSONL plus unchanged native OTLP receiver",
            "commands": commands,
            "configs": configs,
            "remote_roots": self.remote_roots,
            "fresh_directory_per_attempt": True,
            "restart_permitted": False,
            "filesystem_capacity_bytes": capacities,
            "guest_context": self.guest_context,
            "runtime_clock_relations": self.runtime_clocks,
            "resource_inventory": {
                node: {
                    "path": f"resource-inventory-{node}.json",
                    "sha256": configs[node]["resource_inventory_sha256"],
                    "max_memory_bytes": self.resource_inventory[node]["parsed"]["max_memory_bytes"],
                    "max_millicpus": self.resource_inventory[node]["parsed"]["max_millicpus"],
                }
                for node in ("a", "b")
            },
            "rotation_threshold_bytes": MAX_DATA_FILE_SIZE_BYTES,
            "rotation_threshold_above_guest_capacity": all(
                MAX_DATA_FILE_SIZE_BYTES > value for value in capacities.values()
            ),
            "resource_envelope": {
                "collector_hard_cap": None,
                "basis": "same guest-wide resource envelope; no --memory/--cpus flags",
            },
            "operational_readiness_only": True,
            "application_coverage_proven": False,
            "service_identity_enrichment": (
                "common post-capture projection uses verified runtime inventory; "
                "collector-normalized observations remain unchanged"
            ),
            "started_ns": self.started_ns,
            "lifecycle": "started",
            "closed_checkpoint": False,
        })
        _write_json(self.root / "deepflow-integration-questions.json", {
            "schema": "deepflow-integration-questions-v5",
            "service_identity": {
                "status": "available_via_common_verified_runtime_identity_projection",
                "scope": (
                    "post-capture projection may attach actual Compose service identity only when "
                    "hash-bound runtime inventory and lifecycle evidence resolve the observed PID"
                ),
                "forbidden_fallbacks": [
                    "process_kname_as_service_name", "pid_as_service_name",
                    "ip_alias_as_service_name", "expected_deployment_topology",
                ],
            },
            "http_graph_to_sheaft_smoke": (
                "codec output remains service.name=unknown; graph input may use the separate common "
                "projection only after its runtime inventory and lifecycle proofs verify"
            ),
        })

    def _cleanup_incomplete_start(self) -> dict[str, Any]:
        """Best-effort resource cleanup without claiming a completed collector drain."""
        containers, diagnostics, raw_prefixes, receivers, errors = {}, {}, {}, {}, []
        for node in sorted(self.remote_roots):
            node_diagnostics = {}
            for label, command in (
                    ("inspect", f"docker inspect {self.container_name}"),
                    ("logs", f"docker logs {self.container_name}")):
                path = self.root / f"startup-failure-{node}-{label}.log"
                try:
                    result = self.ctx.node_exec(node, command, timeout=60, check=False)
                    stdout, stderr = _stdout(result), _stderr(result)
                    content = stdout + ("\n--- stderr ---\n" + stderr if stderr else "")
                    path.write_text(content, encoding="utf-8")
                    node_diagnostics[label] = {
                        "command": command,
                        "path": path.relative_to(self.root).as_posix(),
                        "sha256": _sha256_file(path),
                        "bytes": path.stat().st_size,
                        "returncode": _returncode(result),
                        "stdout_bytes": len(stdout.encode("utf-8")),
                        "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
                        "stderr": stderr,
                        "stderr_bytes": len(stderr.encode("utf-8")),
                        "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
                        "available": _returncode(result) == 0,
                        "missing_or_unavailable": _returncode(result) != 0,
                    }
                except Exception as exc:
                    node_diagnostics[label] = {
                        "command": command,
                        "available": False,
                        "missing_or_unavailable": True,
                        "transport_error": repr(exc),
                    }
                    errors.append(f"diagnostic:{node}:{label}:{exc!r}")
            diagnostics[node] = node_diagnostics
            if (node in self._startup_helper_nodes
                    and node in self._startup_agent_attempted_nodes):
                try:
                    manifest = self._capture_startup_failure_node(node)
                    snapshot = self.root / "deepflow-raw" / f"node-{node}" / "startup-failure"
                    raw_prefixes[node] = {
                        "retained": True,
                        "path": snapshot.relative_to(self.root).as_posix(),
                        "manifest_technical_valid": manifest.get("technical_valid") is True,
                        "startup_incomplete": True,
                        "producer_closed": False,
                        "closed_checkpoint": False,
                        "normalization_performed": False,
                    }
                except Exception as exc:
                    raw_prefixes[node] = {
                        "retained": False,
                        "startup_incomplete": True,
                        "producer_closed": False,
                        "closed_checkpoint": False,
                        "normalization_performed": False,
                        "error": repr(exc),
                    }
                    errors.append(f"raw-prefix:{node}:{exc!r}")
            try:
                result = self.ctx.node_exec(
                    node, f"docker rm -f {self.container_name}", timeout=60, check=False)
                containers[node] = {
                    "returncode": _returncode(result),
                    "stdout": _stdout(result),
                    "stderr": _stderr(result),
                }
            except Exception as exc:
                containers[node] = {"error": repr(exc)}
                errors.append(f"container:{node}:{exc!r}")
        for name, process in self.processes.items():
            forced = False
            try:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        forced = True
                        process.kill()
                        process.wait(timeout=5)
                receivers[name] = {"returncode": process.poll(), "forced": forced}
            except Exception as exc:
                receivers[name] = {"error": repr(exc), "forced": forced}
                errors.append(f"receiver:{name}:{exc!r}")
        for log in self.logs:
            try:
                if not log.closed:
                    log.close()
            except Exception as exc:
                errors.append(f"log:{exc!r}")
        self._closed = True
        return {
            "containers": containers,
            "diagnostics_before_removal": diagnostics,
            "available_raw_prefixes_before_removal": raw_prefixes,
            "receivers": receivers,
            "errors": errors,
            "best_effort": True,
            "drain_attempted": False,
            "collector_closed_checkpoint_created": False,
        }

    def close(self) -> None:
        if self._closed:
            return
        if not self._startup_complete:
            self._cleanup_incomplete_start()
            return
        super().close()

    def _capture_startup_failure_node(self, node: str) -> dict[str, Any]:
        """Retain every available raw byte without decoding an unfinished producer file."""
        remote = self.remote_roots[node]
        stage = "startup-failure"
        remote_stage = remote + "/snapshots/" + stage
        command = (
            f"python3 {shlex.quote(remote + '/deepflow_snapshot_v5.py')} "
            f"--data {shlex.quote(remote + '/data')} --out {shlex.quote(remote_stage)} "
            "--mode failure"
        )
        permissions = self.ctx.node_exec(
            node, f"sudo chmod -R a+rX {shlex.quote(remote + '/data')}",
            timeout=60, check=False)
        if _returncode(permissions):
            raise RuntimeError(f"cannot read incomplete DeepFlow files on {node}")
        result = self.ctx.node_exec(node, command, timeout=300, check=False)
        if _returncode(result):
            raise RuntimeError(
                f"DeepFlow failure snapshot failed on {node}: {_stderr(result).strip()}")
        local = self.root / "deepflow-raw" / f"node-{node}" / stage
        local.mkdir(parents=True, exist_ok=False)
        self.ctx.node_get(node, remote_stage + "/snapshot.json", local / "snapshot.json")
        manifest = json.loads((local / "snapshot.json").read_text(encoding="utf-8"))
        if (manifest.get("schema") != "deepflow-standalone-snapshot-v5"
                or manifest.get("mode") != "failure"
                or manifest.get("startup_incomplete") is not True
                or manifest.get("producer_closed") is not False):
            raise RuntimeError(f"DeepFlow failure snapshot manifest is invalid on {node}")
        for item in manifest.get("files", []):
            name = item.get("snapshot_name")
            if not isinstance(name, str) or not name or "/" in name or "\\" in name:
                raise RuntimeError(f"unsafe DeepFlow failure snapshot filename on {node}: {name!r}")
            target = local / name
            self.ctx.node_get(node, remote_stage + "/" + name, target)
            if (target.stat().st_size != item.get("copied_bytes")
                    or _sha256_file(target) != item.get("copied_sha256")):
                raise RuntimeError(f"DeepFlow failure snapshot mismatch: {target}")
        return manifest

    def _wait_container_readiness(self) -> None:
        deadline = time.monotonic() + 90
        consecutive = 0
        while time.monotonic() < deadline:
            running, dispatcher = [], []
            for node in ("a", "b"):
                state = self.ctx.node_exec(
                    node,
                    f"docker inspect --format '{{{{.State.Running}}}}' {self.container_name}",
                    timeout=30, check=False,
                )
                ready = self.ctx.node_exec(
                    node,
                    f"docker exec {self.container_name} sh -c "
                    + shlex.quote(
                        f"grep -h -F '{DEEPFLOW_EBPF_READY_MARKER}' "
                        "/var/log/deepflow-agent/* 2>/dev/null | head -n 1"
                    ),
                    timeout=30, check=False,
                )
                running.append(_returncode(state) == 0 and _stdout(state).strip() == "true")
                dispatcher.append(
                    _returncode(ready) == 0
                    and DEEPFLOW_EBPF_READY_MARKER in _stdout(ready).lower()
                )
            if all(running) and all(dispatcher):
                consecutive += 1
                if consecutive >= 2:
                    _write_json(self.root / "readiness.json", {
                        "ready": True, "operational_only": True,
                        "ebpf_origin_proven": False,
                    })
                    return
            else:
                consecutive = 0
            time.sleep(1)
        _write_json(self.root / "readiness.json", {
            "ready": False, "operational_only": True, "ebpf_origin_proven": False,
        })
        raise RuntimeError("DeepFlow dispatcher readiness not established on both guests")

    def health(self) -> None:
        for node in ("a", "b"):
            result = self.ctx.node_exec(
                node,
                f"docker inspect --format '{{{{.State.Running}}}}' {self.container_name}",
                timeout=30, check=False,
            )
            if _returncode(result) or _stdout(result).strip() != "true":
                raise RuntimeError(f"DeepFlow exited on guest {node}")

    def settle(self) -> None:
        self.health()

    def _docker_command(self, node: str, remote_config: str, port: int) -> str:
        remote = self.remote_roots[node]
        return (
            f"docker run -d --name {self.container_name} --privileged --pid=host --network=host "
            f"-v {shlex.quote(remote_config)}:/etc/deepflow-agent-standalone.yaml:ro "
            f"-v {shlex.quote(remote + '/data')}:/var/log/deepflow-agent "
            "-v /sys/kernel/debug:/sys/kernel/debug -v /sys/fs/bpf:/sys/fs/bpf "
            "-v /var/run/docker.sock:/var/run/docker.sock:ro "
            f"{shlex.quote(self.image)} /bin/deepflow-agent --standalone "
            "-f /etc/deepflow-agent-standalone.yaml --cgroups-disabled"
        )

    def _config_summary(self) -> dict[str, Any]:
        return {
            "mode": "standalone flat JSONL",
            "max_data_file_size_mib": MAX_DATA_FILE_SIZE_MIB,
            "max_data_file_size_bytes": MAX_DATA_FILE_SIZE_BYTES,
            "request_header": "x-experiment-request-id",
            "resource_policy": {
                "max_memory": "per-guest ceil(/proc/meminfo MemTotal to MiB)",
                "max_millicpus": "per-guest nproc * 1000",
                "scope": "guest-wide positive envelope, with Docker/cgroup lower-limit rejection",
                "pinned_source_paths": [
                    "agent/src/config/config.rs",
                    "agent/src/utils/guard.rs",
                    "agent/src/policy/first_path.rs",
                ],
            },
            "native_receiver": f"OTLP/HTTP {NATIVE_RECEIVER_PORT}",
            "service_identity": "unknown until separately verified runtime inventory enrichment",
            "raw_wire_reconstruction": False,
            "redis_non_utf8_reconstruction": False,
            "event_clock": {
                "domain": SOURCE_CLOCK,
                "serialized_fields": "start_time/end_time integer microseconds",
                "conversion": "exact integer multiply by 1000 to Unix nanoseconds",
                "controller_ntp_correction": "disabled by pinned standalone set_standalone",
                "host_receiver_arrival_used": False,
                "zero_guest_wall_clock_adjustment_claimed": False,
                "hashed_runtime_clock_relation_included": True,
                "relation_scope": (
                    "pinned source construction plus actual guest identity and runtime config; "
                    "configuration alone is not the proof"
                ),
                "clock_step_limitation_retained": True,
                "empirical_endpoint_offsets_used_as_hard_bound": False,
                "arbitrary_tolerance_or_age_filter_used": False,
                "pinned_source_paths": [
                    "agent/src/ebpf/user/tracer.c",
                    "agent/src/ebpf_dispatcher.rs",
                    "agent/src/config/config.rs",
                    "agent/src/flow_generator/protocol_logs.rs",
                ],
            },
        }

    def _capture_node(self, node: str, stage: str, *, final: bool) -> dict[str, Any]:
        remote = self.remote_roots[node]
        remote_stage = remote + "/snapshots/" + stage
        mode = "final" if final else "prefix"
        command = (
            f"python3 {shlex.quote(remote + '/deepflow_snapshot_v5.py')} "
            f"--data {shlex.quote(remote + '/data')} --out {shlex.quote(remote_stage)} "
            f"--mode {mode}"
        )
        permissions = self.ctx.node_exec(
            node, f"sudo chmod -R a+rX {shlex.quote(remote + '/data')}",
            timeout=60, check=False,
        )
        if _returncode(permissions):
            raise RuntimeError(f"cannot read DeepFlow standalone files on {node}")
        result = self.ctx.node_exec(node, command, timeout=300, check=False)
        if _returncode(result):
            raise RuntimeError(
                f"DeepFlow {mode} snapshot failed on {node}: {_stderr(result).strip()}"
            )
        local = self.root / "deepflow-raw" / f"node-{node}" / stage
        local.mkdir(parents=True, exist_ok=False)
        self.ctx.node_get(node, remote_stage + "/snapshot.json", local / "snapshot.json")
        manifest = json.loads((local / "snapshot.json").read_text(encoding="utf-8"))
        normalized, accounting, codec_failures = 0, 0, 0
        file_log_write_failures: list[dict[str, Any]] = []
        for item in manifest.get("files", []):
            name = item.get("snapshot_name")
            if not isinstance(name, str) or not name or "/" in name or "\\" in name:
                raise RuntimeError(f"unsafe DeepFlow snapshot filename on {node}: {name!r}")
            target = local / name
            self.ctx.node_get(node, remote_stage + "/" + name, target)
            if target.stat().st_size != item.get("copied_bytes"):
                raise RuntimeError(f"DeepFlow snapshot size mismatch: {target}")
            if _sha256_file(target) != item.get("copied_sha256"):
                raise RuntimeError(f"DeepFlow snapshot hash mismatch: {target}")
            if not name.startswith("l7_flow_log"):
                if final:
                    file_log_write_failures.extend(self._standalone_write_failures(target))
                continue
            source_file = f"{node}/{item['source_name']}"
            with (self.root / f"{node}.jsonl").open("a", encoding="utf-8", newline="\n") as output, (
                self.root / "deepflow-codec-accounting.jsonl"
            ).open("a", encoding="utf-8", newline="\n") as evidence:
                def retain_batch(batch):
                    output.write(json.dumps(batch, separators=(",", ":"), ensure_ascii=False) + "\n")

                def retain_accounting(row):
                    key = (source_file, int(row["offset"]))
                    previous = self._seen_offsets.get(key)
                    if previous is not None and previous != row["sha256"]:
                        raise RuntimeError(
                            f"DeepFlow source bytes changed at {source_file}:{row['offset']}"
                        )
                    self._seen_offsets[key] = row["sha256"]
                    row.update(node=node, capture_stage=stage)
                    evidence.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n")

                _, _, prefix = codec_file(
                    target, node=node, source_file=source_file,
                    retained_file=target.relative_to(self.root).as_posix(), seen=self._seen,
                    guest_context=self.guest_context.get(node),
                    runtime_clock=self.runtime_clocks.get(node),
                    on_batch=retain_batch, on_accounting=retain_accounting,
                )
            normalized += prefix["normalized_batches"]
            accounting += prefix["record_count"]
            codec_failures += prefix["technical_failure_records"]
            item["codec"] = prefix
            if not final:
                self._prefixes[node][item["source_name"]] = {
                    "path": str(target),
                    "bytes": target.stat().st_size,
                    "sha256": _sha256_file(target),
                    "source_file": source_file,
                }
        manifest.update({
            "node": node,
            "stage": stage,
            "normalized_batches_appended": normalized,
            "accounting_rows_appended": accounting,
            "codec_technical_failure_records": codec_failures,
            "standalone_file_log_write_failures": file_log_write_failures,
            "technical_valid": (
                (bool(manifest.get("files")) or not final)
                and not manifest.get("rotation_observed")
                and codec_failures == 0
                and not file_log_write_failures
                and (not final or not any(
                    item.get("source_changed_during_snapshot")
                    for item in manifest.get("files", [])
                ))
                and (not final or not any(
                    item.get("source_name", "").startswith("l7_flow_log")
                    and item.get("pending_tail_bytes_at_read")
                    for item in manifest.get("files", [])
                ))
            ),
            "pending_no_standalone_files": not bool(manifest.get("files")),
        })
        _write_json(local / "snapshot.json", manifest)
        return manifest

    @staticmethod
    def _standalone_write_failures(path: Path) -> list[dict[str, Any]]:
        """Find only the pinned sender's source-supported terminal loss marker."""
        failures = []
        with path.open("rb") as stream:
            for line_number, raw in enumerate(stream, 1):
                line = raw.decode("utf-8", errors="replace")
                if "sender send item " in line and " failed " in line:
                    failures.append({
                        "file": path.name,
                        "line": line_number,
                        "sha256": hashlib.sha256(raw.rstrip(b"\r\n")).hexdigest(),
                    })
        return failures

    def _capture_all(self, label: str, *, final: bool = False) -> dict[str, Any]:
        self._capture_counter += 1
        stage = f"{self._capture_counter:03d}-{label}"
        nodes = {node: self._capture_node(node, stage, final=final) for node in ("a", "b")}
        result = {
            "schema": "deepflow-capture-v5",
            "stage": stage,
            "final": final,
            "nodes": nodes,
            "technical_valid": all(item.get("technical_valid") for item in nodes.values()),
            "rotation_policy": "any .pre is technical invalid because 1 TiB exceeds guest filesystem capacity",
        }
        self._capture_evidence.append(result)
        _write_json(self.root / f"deepflow-capture-{stage}.json", result)
        return result

    def snapshot(self) -> None:
        if self._drained:
            evidence = self._drain_evidence or {}
            final = {
                "schema": "collector-final-snapshot-v5",
                "collector": self.collector,
                "captured_ns": time.time_ns(),
                "collector_stopped": True,
                "receivers_closed": True,
                "technical_complete": evidence.get("technical_complete") is True,
                "accepted_receiver_bytes_closed_and_hashed": (
                    evidence.get("accepted_receiver_bytes_closed_and_hashed") is True
                ),
                "service_identity_enrichment": "not_performed",
                "scope": "closed raw standalone files and native receiver bytes; no zero-loss claim",
            }
            _write_json(self.root / "final-snapshot.json", final)
            self._finalize_checkpoint()
            if not final["technical_complete"]:
                raise RuntimeError("DeepFlow final snapshot is technically invalid")
            return
        self.health()
        capture = self._capture_all("live-prefix", final=False)
        if not capture["technical_valid"]:
            raise RuntimeError("DeepFlow live prefix capture is technically invalid")
        for node in ("a", "b"):
            self._retain_node_evidence(node, "snapshot")
        _write_json(self.root / "live-prefix.json", {
            "schema": "collector-live-prefix-v5",
            "collector": self.collector,
            "captured_ns": time.time_ns(),
            "receivers_closed": False,
            "producer_pending": True,
            "capture_stage": capture["stage"],
            "scope": "immutable last-complete-record prefixes; producer and incomplete tails remain pending",
        })

    def _control_proof(self, node: str, marker: str) -> dict[str, Any]:
        path = self.root / f"{node}.jsonl"
        if not path.exists():
            return {"proven": False, "reason": "normalized_file_missing"}
        for ordinal, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            document = json.loads(line)
            if document.get("source") != f"ebpf-deepflow:{node}":
                continue
            for resource in document.get("payload", {}).get("resourceSpans", []):
                for scope in resource.get("scopeSpans", []):
                    for span in scope.get("spans", []):
                        attrs = _attributes(span.get("attributes", []))
                        if attrs.get("deepflow.signal_source") != "EBPF":
                            continue
                        if marker not in str(attrs.get("url.path", "")):
                            continue
                        retained = self.root / str(attrs.get("deepflow.raw.retained_file", ""))
                        raw_hash = attrs.get("deepflow.raw.sha256")
                        offset = int(attrs.get("deepflow.raw.offset", -1))
                        length = int(attrs.get("deepflow.raw.length", -1))
                        if not retained.is_file() or offset < 0 or length < 0:
                            return {"proven": False, "reason": "raw_locator_missing"}
                        with retained.open("rb") as stream:
                            stream.seek(offset)
                            actual = hashlib.sha256(stream.read(length)).hexdigest()
                        return {
                            "proven": actual == raw_hash,
                            "reason": "raw_deepflow_ebpf_http_record" if actual == raw_hash else "raw_hash_mismatch",
                            "line": ordinal,
                            "raw_file": str(retained),
                            "raw_offset": offset,
                            "raw_length": length,
                            "raw_sha256": actual,
                            "signal_source": "EBPF",
                            "protocol": attrs.get("deepflow.l7_protocol"),
                            "tap_side": attrs.get("deepflow.tap_side"),
                            "process_command": attrs.get("process.command"),
                        }
        return {"proven": False, "reason": "marker_or_ebpf_origin_missing"}

    def _before_control_proof_poll(self, marker: str) -> None:
        capture = self._capture_all("positive-control", final=False)
        if not capture["technical_valid"]:
            raise RuntimeError("DeepFlow positive-control prefix capture is technically invalid")

    def _assess_terminal_logs(self, logs: str) -> dict[str, Any]:
        failures = [line for line in logs.splitlines()
                    if "sender send item " in line and " failed " in line]
        return {
            "graceful_success_marker": None,
            "source_specific_failure_markers": failures,
            "invalid_reasons": ["deepflow_standalone_write_failure"] if failures else [],
        }

    def _shutdown_source_facts(self) -> dict[str, Any]:
        return {
            "pin": f"{DEEPFLOW_VERSION} commit {DEEPFLOW_SOURCE_COMMIT}",
            "source_paths": [
                "agent/src/sender/uniform_sender.rs",
                "agent/src/flow_generator/protocol_logs.rs",
                "agent/src/flow_generator/protocol_logs/parser.rs",
            ],
            "writer": "the sender termination branch calls flush_writer; Docker signal-path reachability is not asserted",
            "flush_error": "pinned flush_writer discards BufWriter.flush result",
            "configured_stop_grace_seconds": self.stop_grace_seconds,
        }

    def _exporter_flush_claim(self, termination: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "internal_flush_loss_unproven",
            "clean_process_termination_observed": all(
                item.get("technical_valid") for item in termination.values()
            ),
            "known_write_failure_absent": all(
                not item.get("log_assessment", {}).get("source_specific_failure_markers")
                for item in termination.values()
            ),
            "zero_kernel_buffer_or_file_flush_loss_proven": False,
        }

    def _verify_prefixes(self, final_capture: dict[str, Any]) -> dict[str, Any]:
        results = {}
        for node, prefixes in self._prefixes.items():
            final_stage = final_capture["nodes"][node]["stage"]
            final_root = self.root / "deepflow-raw" / f"node-{node}" / final_stage
            for name, prefix in prefixes.items():
                final_path = final_root / name
                key = f"{node}/{name}"
                if not final_path.is_file() or final_path.stat().st_size < prefix["bytes"]:
                    results[key] = {"unchanged": False, "reason": "final_file_missing_or_shorter"}
                    continue
                digest = hashlib.sha256()
                with final_path.open("rb") as stream:
                    remaining = prefix["bytes"]
                    while remaining:
                        chunk = stream.read(min(1024 * 1024, remaining))
                        if not chunk:
                            break
                        digest.update(chunk)
                        remaining -= len(chunk)
                results[key] = {
                    "unchanged": remaining == 0 and digest.hexdigest() == prefix["sha256"],
                    "bytes": prefix["bytes"],
                    "training_sha256": prefix["sha256"],
                    "final_prefix_sha256": digest.hexdigest(),
                }
        return results

    def final_drain(self) -> dict[str, Any]:
        if self._drained:
            evidence = dict(self._drain_evidence or {})
            if not evidence.get("technical_valid"):
                raise RuntimeError("DeepFlow final drain is technically invalid")
            return evidence
        termination = {}
        for node in ("a", "b"):
            self._retain_node_evidence(node, "pre-drain")
            since = _stdout(self.ctx.node_exec(node, "date +%s", timeout=10, check=False)).strip()
            stop = self.ctx.node_exec(
                node, f"docker stop -t {self.stop_grace_seconds} {self.container_name}",
                timeout=self.stop_grace_seconds + 30, check=False,
            )
            inspect = self.ctx.node_exec(
                node, f"docker inspect {self.container_name}", timeout=30, check=False
            )
            logs_result = self.ctx.node_exec(
                node, f"docker logs {self.container_name}", timeout=60, check=False
            )
            logs = _stdout(logs_result) + _stderr(logs_result)
            (self.root / f"final-{node}-collector.log").write_text(logs, encoding="utf-8")
            until = _stdout(self.ctx.node_exec(node, "date +%s", timeout=10, check=False)).strip()
            events = self.ctx.node_exec(
                node,
                f"docker events --since {shlex.quote(since or '0')} --until {shlex.quote(until or '0')} "
                f"--filter container={self.container_name} --format '{{{{json .}}}}'",
                timeout=30, check=False,
            )
            termination[node] = self._termination_evidence(
                stop=stop, inspect=inspect, events=events, logs=logs
            )
            raw_evidence = {}
            for label, result in (("stop", stop), ("inspect", inspect), ("events", events)):
                path = self.root / f"final-{node}-{label}.txt"
                path.write_text(
                    _stdout(result) + ("\n--- stderr ---\n" + _stderr(result) if _stderr(result) else ""),
                    encoding="utf-8",
                )
                raw_evidence[label] = {
                    "path": path.relative_to(self.root).as_posix(),
                    "sha256": _sha256_file(path),
                    "returncode": _returncode(result),
                }
            raw_evidence["events_time_range"] = {"since_epoch_s": since, "until_epoch_s": until}
            termination[node]["raw_evidence"] = raw_evidence
        final_capture = self._capture_all("final", final=True)
        prefix_checks = self._verify_prefixes(final_capture)
        native_barrier = self._receiver_barrier("native")
        receivers = self._close_receivers()
        retained_valid = final_capture.get("technical_valid") and all(
            item.get("unchanged") for item in prefix_checks.values()
        )
        valid = (
            all(item.get("technical_valid") for item in termination.values())
            and retained_valid
            and native_barrier.get("accepted")
            and receivers.get("native", {}).get("technical_valid")
        )
        evidence = {
            "schema": "collector-final-drain-v5",
            "collector": self.collector,
            "source_version": self.source_version,
            "source_shutdown_facts": self._shutdown_source_facts(),
            "termination": termination,
            "final_raw_capture": final_capture,
            "training_prefix_unchanged_in_final": prefix_checks,
            "native_receiver_acceptance_barrier": native_barrier,
            "receiver_closed_checkpoints": receivers,
            "accepted_receiver_bytes_closed_and_hashed": bool(retained_valid)
                and receivers.get("native", {}).get("parent_hash_verification") is True,
            "collector_exporter_flush": self._exporter_flush_claim(termination),
            "kernel_or_producer_loss_absent": None,
            "technical_complete": bool(valid),
            "technical_valid": bool(valid),
            "service_identity_enrichment": "not_performed",
            "scope": (
                "complete retained standalone file bytes and native receiver bytes; "
                "zero kernel, producer, or ignored internal flush loss is not claimed"
            ),
        }
        self._drain_evidence = evidence
        _write_json(self.root / "drain-evidence.json", evidence)
        self._write_retention_manifest()
        self._finalize_checkpoint()
        self._drained = True
        if not valid:
            raise RuntimeError("DeepFlow final drain is technically invalid")
        return dict(evidence)

    def _write_retention_manifest(self) -> None:
        files = []
        raw_root = self.root / "deepflow-raw"
        if raw_root.exists():
            for path in sorted(raw_root.rglob("*")):
                if path.is_file():
                    files.append({
                        "path": path.relative_to(self.root).as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": _sha256_file(path),
                    })
        _write_json(self.root / "deepflow-retention-manifest.json", {
            "schema": "deepflow-retention-manifest-v5",
            "files": files,
            "file_count": len(files),
            "raw_bytes": sum(item["bytes"] for item in files),
            "known_write_failures": {
                node: {
                    "container_log": (self._drain_evidence or {}).get("termination", {})
                    .get(node, {}).get("log_assessment", {})
                    .get("source_specific_failure_markers", []),
                    "retained_standalone_logs": (self._drain_evidence or {})
                    .get("final_raw_capture", {}).get("nodes", {}).get(node, {})
                    .get("standalone_file_log_write_failures", []),
                }
                for node in ("a", "b")
            },
            "internal_sender_counter_snapshot": "unavailable_from_reviewed_standalone_file_interface",
            "zero_internal_loss_proven": False,
        })

    # Base abstract hooks not used by the standalone start path.
    def _write_config(self, node: str, port: int):
        raise NotImplementedError("DeepFlow writes one standalone config in start()")

    def _origin_proof(self, resource, attrs):
        return None
