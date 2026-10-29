"""Pinned DeepFlow v7.2.3 standalone lifecycle for iteration 5.

DeepFlow writes flat JSONL on each guest rather than OTLP.  Immutable snapshots
are copied and decoded losslessly by :mod:`deepflow_codec_v5`; the native OTLP
receiver remains unchanged.  No PID, kernel command, endpoint, or expected
deployment identity is promoted to ``service.name``.
"""
from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from .collectors_v5 import (
    CONTROL_IMAGE,
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
    append_jsonl,
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


def _config() -> dict[str, Any]:
    return {
        "global": {
            "communication": {"proactive_request_interval": "10s"},
            "standalone_mode": {
                "max_data_file_size": MAX_DATA_FILE_SIZE_MIB,
                "data_file_dir": "/var/log/deepflow-agent/",
            },
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
        self._seen: set[tuple[str, int, str]] = set()
        self._seen_offsets: dict[tuple[str, int], str] = {}
        self._prefixes: dict[str, dict[str, dict[str, Any]]] = {"a": {}, "b": {}}
        self._capture_counter = 0
        self._capture_evidence: list[dict[str, Any]] = []

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
        self.started_ns = time.time_ns()
        self._start_receivers()
        config = self.root / "deepflow-agent-standalone.yaml"
        config.write_text(yaml.safe_dump(_config(), sort_keys=False), encoding="utf-8")
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
                node, "readlink /proc/1/ns/pid", timeout=30
            )).strip()
            if not boot_id or not pid_namespace:
                raise RuntimeError(f"guest boot/PID namespace identity unavailable on {node}")
            self.guest_context[node] = {
                "boot_id": boot_id,
                "pid_namespace": pid_namespace,
            }
            remote_config = remote + "/deepflow-agent-standalone.yaml"
            remote_helper = remote + "/deepflow_snapshot_v5.py"
            self.ctx.node_put(node, config, remote_config)
            self.ctx.node_put(node, helper, remote_helper)
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
            self.ctx.node_exec(node, command, timeout=180)
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
            "service_identity_enrichment": "not_implemented_without_verified_runtime_inventory",
            "started_ns": self.started_ns,
            "lifecycle": "started",
            "closed_checkpoint": False,
        })
        _write_json(self.root / "deepflow-integration-questions.json", {
            "schema": "deepflow-integration-questions-v5",
            "service_identity": {
                "status": "required_for_entry_binding_not_implemented",
                "question": (
                    "Which reviewed runtime inventory artifact will join observed guest boot ID, "
                    "PID namespace/cgroup and observation-time PID to a container/service identity?"
                ),
                "forbidden_fallbacks": [
                    "process_kname_as_service_name", "pid_as_service_name",
                    "ip_alias_as_service_name", "expected_deployment_topology",
                ],
            },
            "http_graph_to_sheaft_smoke": (
                "blocked until the verified runtime identity join is supplied; codec output alone "
                "must remain service.name=unknown"
            ),
        })

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
                        "grep -h -E 'Start (.* )?dispatcher' "
                        "/var/log/deepflow-agent/* 2>/dev/null | head -n 1"
                    ),
                    timeout=30, check=False,
                )
                running.append(_returncode(state) == 0 and _stdout(state).strip() == "true")
                dispatcher.append(_returncode(ready) == 0 and "dispatcher" in _stdout(ready).lower())
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
                "hashed_runtime_clock_relation_included": False,
                "direct_bracketing_admissible_from_config_alone": False,
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
            batches, rows, prefix = codec_file(
                target, node=node, source_file=source_file,
                retained_file=target.relative_to(self.root).as_posix(), seen=self._seen,
                guest_context=self.guest_context.get(node),
            )
            for row in rows:
                key = (source_file, int(row["offset"]))
                previous = self._seen_offsets.get(key)
                if previous is not None and previous != row["sha256"]:
                    raise RuntimeError(
                        f"DeepFlow source bytes changed at {source_file}:{row['offset']}"
                    )
                self._seen_offsets[key] = row["sha256"]
                row.update(node=node, capture_stage=stage)
            normalized += append_jsonl(self.root / f"{node}.jsonl", batches)
            accounting += append_jsonl(self.root / "deepflow-codec-accounting.jsonl", rows)
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
                        }
        return {"proven": False, "reason": "marker_or_ebpf_origin_missing"}

    def certify_controls(self, timeout: float = 60.0) -> dict[str, Any]:
        marker = f"collector-control-v5-deepflow-{time.time_ns()}"
        nodes: dict[str, Any] = {}
        for index, node in enumerate(("a", "b")):
            port = 18081 + index
            self.ctx.node_exec(node, f"docker pull {shlex.quote(CONTROL_IMAGE)}", timeout=300)
            server = f"study-ebpf-control-server-{node}"
            client = f"study-ebpf-control-client-{node}"
            self.ctx.node_exec(
                node,
                f"docker rm -f {server} {client} >/dev/null 2>&1 || true; "
                f"docker run -d --name {server} --network host --entrypoint /bin/sh "
                f"{shlex.quote(CONTROL_IMAGE)} -c "
                + shlex.quote(
                    f"mkdir -p /tmp/control; printf ok > /tmp/control/{marker}; "
                    f"exec busybox httpd -f -p {port} -h /tmp/control"
                ),
                timeout=60,
            )
            request = self.ctx.node_exec(
                node,
                f"docker run -d --name {client} --network host --entrypoint /bin/sh "
                f"{shlex.quote(CONTROL_IMAGE)} -c "
                + shlex.quote(
                    f"while true; do busybox wget -qO- http://127.0.0.1:{port}/{marker} "
                    ">/dev/null || exit 1; sleep 1; done"
                ),
                timeout=60, check=False,
            )
            nodes[node] = {
                "port": port, "server_container": server, "client_container": client,
                "client_start_returncode": _returncode(request),
                "control_image": CONTROL_IMAGE,
            }
            if _returncode(request):
                raise RuntimeError(f"DeepFlow technical control failed to start on {node}")
        deadline, proofs = time.monotonic() + timeout, {}
        while time.monotonic() < deadline:
            capture = self._capture_all("positive-control", final=False)
            if not capture["technical_valid"]:
                break
            proofs = {node: self._control_proof(node, marker) for node in ("a", "b")}
            if all(item.get("proven") for item in proofs.values()):
                break
            self.health()
            time.sleep(1)
        for node in ("a", "b"):
            self.ctx.node_exec(
                node,
                f"docker rm -f study-ebpf-control-client-{node} study-ebpf-control-server-{node}",
                timeout=30, check=False,
            )
        evidence = {
            "schema": "collector-positive-control-v5",
            "collector": self.collector,
            "source_domain": self.source_domain,
            "marker": marker,
            "nodes": nodes,
            "proofs": proofs,
            "selected_ebpf_origin_proven": bool(proofs) and all(
                item.get("proven") for item in proofs.values()
            ),
            "application_coverage": "not_assessed_by_technical_control",
            "native_sdk": False,
        }
        _write_json(self.root / "technical-positive-control.json", evidence)
        self.positive_control_evidence = evidence
        if not evidence["selected_ebpf_origin_proven"]:
            raise RuntimeError("DeepFlow eBPF HTTP positive control was not observed on both guests")
        return evidence

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
