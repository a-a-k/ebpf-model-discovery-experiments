"""Iteration-5 OBI and Coroot acquisition with collector-true provenance.

Operational liveness, selected-collector eBPF proof, application coverage, and
exporter drain are deliberately separate facts.  Nothing in this module turns a
healthy collector with no supported application record into a technical error.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from .collectors import OBI_IMAGE


COROOT_IMAGE = (
    "ghcr.io/coroot/coroot-node-agent:1.37.0@"
    "sha256:f360c31c5e2fa75550c0029f3c02a0e54b83831bae59201b9fe76bab2fe564b4"
)
COROOT_COMMIT = "89a858a0ee35c4eb938b86d56f23168fb0ac7573"
CONTROL_IMAGE = (
    "haproxy:3.0-alpine@"
    "sha256:34cc7d1f6142464d7d2b73e2a1eef7392556dbf304160aef543e513cfd9e5162"
)
RECEIVERS = {"a": 4318, "b": 4320, "native": 4319}
CONTROL_READY_TIMEOUT_SECONDS = 30.0


class CollectorUnavailable(RuntimeError):
    """A fixed study arm is not implementable under the recorded constraints."""

    def __init__(self, collector: str, reason: str):
        super().__init__(f"collector arm {collector!r} unavailable: {reason}")
        self.collector = collector
        self.reason = reason


def create_collectors_v5(ctx, collector: str, *, semantic: bool = True):
    name = collector.strip().lower()
    if name == "obi":
        return OBICollectorsV5(ctx, semantic=semantic)
    if name == "coroot":
        return CorootCollectorsV5(ctx, semantic=semantic)
    if name == "deepflow":
        from .deepflow_v5 import DeepFlowCollectorsV5
        return DeepFlowCollectorsV5(ctx, semantic=semantic)
    if name in {"newrelic", "new-relic"}:
        raise CollectorUnavailable(
            "newrelic",
            "requires an authorized existing license key and a verified local OTLP codec",
        )
    raise CollectorUnavailable(name, "not one of the four fixed collector arms")


def make_collectors(ctx, collector: str, *, semantic: bool = True):
    """Campaign-v5 factory; fixed arms never fall back to another collector."""
    return create_collectors_v5(ctx, collector, semantic=semantic)


def _stdout(result: Any) -> str:
    return str(getattr(result, "stdout", result if isinstance(result, str) else ""))


def _stderr(result: Any) -> str:
    return str(getattr(result, "stderr", ""))


def _returncode(result: Any) -> int:
    return int(getattr(result, "returncode", 0))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _result_evidence(result: Any) -> dict[str, Any]:
    return {
        "returncode": _returncode(result),
        "stdout": _stdout(result),
        "stderr": _stderr(result),
    }


def _control_server_script(port: int) -> str:
    """Run HAProxy itself as the pinned non-SDK HTTP responder."""
    config = "\n".join((
        "global",
        "  log stdout format raw local0",
        "defaults",
        "  mode http",
        "  log global",
        "  option httplog",
        "  timeout connect 5s",
        "  timeout client 30s",
        "  timeout server 30s",
        "frontend control",
        f"  bind 0.0.0.0:{port}",
        "  http-request return status 200 content-type text/plain string ok",
        "",
    ))
    return (
        f"printf %s {shlex.quote(config)} > /tmp/control-haproxy.cfg; "
        "haproxy -c -f /tmp/control-haproxy.cfg; "
        "exec haproxy -W -db -f /tmp/control-haproxy.cfg"
    )


def _control_forwarder_script(
    listen_port: int, server_port: int, *, server_host: str
) -> str:
    """Run a persistent HAProxy worker as the selected HTTP client origin."""
    config = "\n".join((
        "global",
        "  log stdout format raw local0",
        "defaults",
        "  mode http",
        "  log global",
        "  option httplog",
        "  timeout connect 5s",
        "  timeout client 30s",
        "  timeout server 30s",
        "frontend control_client",
        f"  bind 0.0.0.0:{listen_port}",
        "  default_backend control_server",
        "backend control_server",
        f"  server responder {server_host}:{server_port}",
        "",
    ))
    return (
        f"printf %s {shlex.quote(config)} > /tmp/control-haproxy-client.cfg; "
        "haproxy -c -f /tmp/control-haproxy-client.cfg; "
        "exec haproxy -W -db -f /tmp/control-haproxy-client.cfg"
    )


def _control_request_script(
    port: int, marker: str, *, persistent: bool, host: str = "127.0.0.1"
) -> str:
    request = f"busybox wget -T 2 -qO- http://{host}:{port}/{marker}"
    if not persistent:
        return request
    return f"while true; do {request} >/dev/null || exit 1; sleep 1; done"


def _inspect_running(result: Any) -> bool:
    if _returncode(result):
        return False
    try:
        payload = json.loads(_stdout(result))
        return bool(payload and payload[0].get("State", {}).get("Running") is True)
    except (json.JSONDecodeError, TypeError, AttributeError, IndexError):
        return False


def _safe_node_exec(ctx: Any, node: str, command: str, **kwargs: Any) -> Any:
    """Best-effort diagnostic/cleanup call that preserves transport failures."""
    try:
        return ctx.node_exec(node, command, **kwargs)
    except Exception as exc:
        return SimpleNamespace(
            returncode=255,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
        )


def _attributes(items: list[dict[str, Any]]) -> dict[str, Any]:
    def value(item: dict[str, Any]) -> Any:
        raw = item.get("value", {})
        for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
            if key in raw:
                return raw[key]
        array = raw.get("arrayValue", {}).get("values")
        return [value({"value": entry}) for entry in array] if isinstance(array, list) else None

    return {str(item.get("key")): value(item) for item in items if item.get("key")}


class CollectorsV5:
    collector = "base"
    container_name = "study-collector-v5"
    image = ""
    source_version = ""
    source_commit: str | None = None
    stop_grace_seconds = 30

    def __init__(self, ctx, *, semantic: bool = True):
        self.ctx = ctx
        self.semantic = semantic
        # Campaign and ObservationStore consume this stable directory directly;
        # each matrix cell has exactly one declared collector arm.
        self.root = Path(ctx.out) / "observations"
        self.root.mkdir(parents=True, exist_ok=True)
        self.processes: dict[str, subprocess.Popen] = {}
        self.logs: list[Any] = []
        self.started_ns: int | None = None
        self.positive_control_evidence: dict[str, Any] | None = None
        self._drained = False
        self._drain_evidence: dict[str, Any] | None = None
        self._closed = False

    @property
    def source_domain(self) -> str:
        return f"ebpf-{self.collector}"

    def start(self) -> None:
        self.started_ns = time.time_ns()
        self._start_receivers()
        commands = {}
        configs = {}
        for node in ("a", "b"):
            config_path, remote_path = self._write_config(node, RECEIVERS[node])
            configs[node] = {
                "path": config_path.name,
                "sha256": _sha256_file(config_path),
                "remote_path": remote_path,
            }
            self.ctx.node_put(node, config_path, remote_path)
            pull = self.ctx.node_exec(
                node, f"docker pull {shlex.quote(self.image)}", timeout=600
            )
            command = self._docker_command(node, remote_path, RECEIVERS[node])
            commands[node] = command
            self.ctx.node_exec(node, command, timeout=180)
            inspect = self.ctx.node_exec(
                node, f"docker image inspect {shlex.quote(self.image)}", timeout=60
            )
            (self.root / f"image-{node}.json").write_text(
                _stdout(inspect), encoding="utf-8"
            )
            (self.root / f"pull-{node}.log").write_text(
                _stdout(pull) + _stderr(pull), encoding="utf-8"
            )
        self._wait_container_readiness()
        self._write_collector_metadata(
            {
                "schema": "collector-lifecycle-v5",
                "collector": self.collector,
                "source_domain": self.source_domain,
                "source_version": self.source_version,
                "image": self.image,
                "source_commit": self.source_commit,
                "config_summary": self._config_summary(),
                "nodes": ["a", "b"],
                "receiver_ports": RECEIVERS,
                "raw_capture": True,
                "commands": commands,
                "configs": configs,
                "resource_envelope": {
                    "collector_hard_cap": None,
                    "basis": "same guest-wide resource envelope; no --memory/--cpus flags",
                },
                "operational_readiness_only": True,
                "application_coverage_proven": False,
                "started_ns": self.started_ns,
                "lifecycle": "started",
                "closed_checkpoint": False,
            }
        )

    def _write_collector_metadata(self, value: dict[str, Any]) -> None:
        _write_json(self.root / "collector.json", value)

    def _start_receivers(self) -> None:
        for node, port in RECEIVERS.items():
            log = (self.root / f"receiver-{node}.log").open("w", encoding="utf-8")
            self.logs.append(log)
            source = "native" if node == "native" else f"{self.source_domain}:{node}"
            command = [
                sys.executable,
                "-m",
                "ebpf_discovery.receiver_v5",
                "--port",
                str(port),
                "--out",
                str(self.root / f"{node}.jsonl"),
                "--source",
                source,
                "--node",
                node,
                "--checkpoint",
                str(self.root / f"receiver-closed-{node}.json"),
            ]
            self.processes[node] = subprocess.Popen(
                command, stdout=log, stderr=subprocess.STDOUT
            )
        deadline = time.monotonic() + 20
        pending = set(RECEIVERS)
        while pending and time.monotonic() < deadline:
            for node in list(pending):
                process = self.processes[node]
                if process.poll() is not None:
                    raise RuntimeError(f"OTLP receiver {node} exited during startup")
                try:
                    with socket.create_connection(("127.0.0.1", RECEIVERS[node]), timeout=0.2):
                        pending.remove(node)
                except OSError:
                    pass
            if pending:
                time.sleep(0.1)
        if pending:
            raise RuntimeError(f"OTLP receivers did not become ready: {sorted(pending)}")

    def _wait_container_readiness(self) -> None:
        deadline = time.monotonic() + 60
        pending = {"a", "b"}
        last = {}
        while pending and time.monotonic() < deadline:
            for node in list(pending):
                result = self.ctx.node_exec(
                    node,
                    f"docker inspect --format '{{{{.State.Running}}}} {{{{.State.Status}}}} {{{{.State.ExitCode}}}}' {self.container_name}",
                    timeout=30,
                    check=False,
                )
                last[node] = {
                    "stdout": _stdout(result).strip(),
                    "stderr": _stderr(result).strip(),
                    "returncode": _returncode(result),
                }
                if _returncode(result) == 0 and _stdout(result).split()[:1] == ["true"]:
                    pending.remove(node)
            if pending:
                time.sleep(0.5)
        _write_json(self.root / "readiness.json", {"nodes": last, "ready": not pending})
        if pending:
            raise RuntimeError(f"{self.collector} not running on guests {sorted(pending)}")

    def health(self) -> None:
        for node in ("a", "b"):
            result = self.ctx.node_exec(
                node,
                f"docker inspect --format '{{{{.State.Running}}}}' {self.container_name}",
                timeout=30,
                check=False,
            )
            if _returncode(result) or _stdout(result).strip() != "true":
                raise RuntimeError(f"{self.collector} exited on guest {node}")

    def settle(self) -> None:
        """Readiness check only; discovery time is not inferred from a fixed sleep."""
        self.health()

    def _control_nodes(self) -> dict[str, dict[str, Any]]:
        return {
            node: {
                "port": 18081 + index,
                "client_port": 19081 + index,
                "server_container": f"study-ebpf-control-server-{node}",
                "client_container": f"study-ebpf-control-client-{node}",
                "probe_container": f"study-ebpf-control-client-{node}-probe",
                "load_container": f"study-ebpf-control-client-{node}-load",
                "network": f"study-ebpf-control-net-{node}",
                "control_image": CONTROL_IMAGE,
                "request_attempts": [],
                "forwarder_request_attempts": [],
            }
            for index, node in enumerate(("a", "b"))
        }

    def _launch_control_server(self, node: str, entry: dict[str, Any]) -> None:
        server = entry["server_container"]
        client = entry["client_container"]
        probe = entry["probe_container"]
        load = entry["load_container"]
        network = entry["network"]
        pull = _safe_node_exec(
            self.ctx, node, f"docker pull {shlex.quote(CONTROL_IMAGE)}",
            timeout=300, check=False,
        )
        entry["image_pull"] = _result_evidence(pull)
        (self.root / f"control-pull-{node}.log").write_text(
            _stdout(pull) + _stderr(pull), encoding="utf-8"
        )
        if _returncode(pull):
            raise RuntimeError(f"technical control image pull failed on {node}")
        image_inspect = _safe_node_exec(
            self.ctx, node, f"docker image inspect {shlex.quote(CONTROL_IMAGE)}",
            timeout=60, check=False,
        )
        entry["image_inspect"] = _result_evidence(image_inspect)
        (self.root / f"control-image-{node}.json").write_text(
            _stdout(image_inspect), encoding="utf-8"
        )
        if _returncode(image_inspect):
            raise RuntimeError(f"technical control image inspect failed on {node}")
        _safe_node_exec(
            self.ctx, node,
            f"docker rm -f {probe} {load} {client} {server} >/dev/null 2>&1 || true",
            timeout=30, check=False,
        )
        _safe_node_exec(
            self.ctx, node, f"docker network rm {network} >/dev/null 2>&1 || true",
            timeout=30, check=False,
        )
        network_create_command = f"docker network create --driver bridge {network}"
        network_create_started_ns = time.time_ns()
        network_create = _safe_node_exec(
            self.ctx, node,
            network_create_command,
            timeout=30, check=False,
        )
        network_create_finished_ns = time.time_ns()
        entry["network_create"] = {
            **_result_evidence(network_create),
            "command": network_create_command,
            "started_ns": network_create_started_ns,
            "finished_ns": network_create_finished_ns,
            "duration_ns": network_create_finished_ns - network_create_started_ns,
        }
        if _returncode(network_create):
            raise RuntimeError(f"technical control network failed to create on {node}")
        network_inspect = _safe_node_exec(
            self.ctx, node, f"docker network inspect {network}",
            timeout=30, check=False,
        )
        network_path = self.root / f"control-{node}-network-inspect.json"
        network_path.write_text(_stdout(network_inspect), encoding="utf-8")
        entry["network_inspect"] = {
            "path": network_path.relative_to(self.root).as_posix(),
            "sha256": _sha256_file(network_path),
            "returncode": _returncode(network_inspect),
            "stderr": _stderr(network_inspect),
        }
        if _returncode(network_inspect):
            raise RuntimeError(f"technical control network inspect failed on {node}")
        server_start = _safe_node_exec(
            self.ctx, node,
            f"docker run -d --name {server} --network {network} --entrypoint /bin/sh "
            f"{shlex.quote(CONTROL_IMAGE)} -ec "
            + shlex.quote(_control_server_script(entry["port"])),
            timeout=60, check=False,
        )
        entry["server_script"] = _control_server_script(entry["port"])
        entry["server_start"] = _result_evidence(server_start)
        if _returncode(server_start):
            raise RuntimeError(f"technical control server failed to start on {node}")

    def positive_control(self, timeout: float = 60.0) -> dict[str, Any]:
        """Prove selected eBPF origin with a non-SDK container HTTP exchange."""
        marker = f"collector-control-v5-{self.collector}-{time.time_ns()}"
        nodes: dict[str, Any] = self._control_nodes()
        proofs: dict[str, Any] = {}
        failure: Exception | None = None
        evidence: dict[str, Any] = {}
        try:
            for node in ("a", "b"):
                entry = nodes[node]
                entry["control_started_ns"] = time.time_ns()
                port = entry["port"]
                server = entry["server_container"]
                client = entry["client_container"]
                probe = entry["probe_container"]
                load = entry["load_container"]
                network = entry["network"]
                self._launch_control_server(node, entry)

                ready_deadline = time.monotonic() + CONTROL_READY_TIMEOUT_SECONDS
                while time.monotonic() < ready_deadline:
                    inspect = _safe_node_exec(
                        self.ctx, node, f"docker inspect {server}",
                        timeout=30, check=False
                    )
                    attempt: dict[str, Any] = {
                        "attempt": len(entry["request_attempts"]) + 1,
                        "observed_ns": time.time_ns(),
                        "server_running": _inspect_running(inspect),
                        "server_inspect_returncode": _returncode(inspect),
                    }
                    if attempt["server_running"]:
                        config_check = _safe_node_exec(
                            self.ctx, node,
                            f"docker exec {server} haproxy -c -f /tmp/control-haproxy.cfg",
                            timeout=30, check=False,
                        )
                        attempt["config_check"] = _result_evidence(config_check)
                        if _returncode(config_check) == 0:
                            request = _safe_node_exec(
                                self.ctx, node,
                                f"docker run --rm --name {probe} --network {network} "
                                f"--entrypoint /bin/sh {shlex.quote(CONTROL_IMAGE)} -ec "
                                + shlex.quote(_control_request_script(
                                    port, marker, persistent=False, host=server
                                )),
                                timeout=30, check=False,
                            )
                            attempt["request"] = _result_evidence(request)
                            entry["request_attempts"].append(attempt)
                            if _returncode(request) == 0 and _stdout(request).strip() == "ok":
                                entry["server_ready"] = True
                                break
                        else:
                            entry["request_attempts"].append(attempt)
                    else:
                        entry["request_attempts"].append(attempt)
                    time.sleep(0.25)
                if not entry.get("server_ready"):
                    raise RuntimeError(f"technical control HTTP readiness failed on {node}")

                client_script = _control_forwarder_script(
                    entry["client_port"], port, server_host=server
                )
                client_start = _safe_node_exec(
                    self.ctx, node,
                    f"docker run -d --name {client} --network {network} --entrypoint /bin/sh "
                    f"{shlex.quote(CONTROL_IMAGE)} -ec "
                    + shlex.quote(client_script),
                    timeout=60, check=False,
                )
                entry["client_script"] = client_script
                entry["client_start"] = _result_evidence(client_start)
                if _returncode(client_start):
                    raise RuntimeError(f"technical control client failed to start on {node}")
                client_inspect = _safe_node_exec(
                    self.ctx, node, f"docker inspect {client}",
                    timeout=30, check=False
                )
                entry["client_start_inspect"] = _result_evidence(client_inspect)
                if not _inspect_running(client_inspect):
                    raise RuntimeError(f"technical control client exited during startup on {node}")
                client_config_check = _safe_node_exec(
                    self.ctx, node,
                    f"docker exec {client} haproxy -c -f /tmp/control-haproxy-client.cfg",
                    timeout=30, check=False,
                )
                entry["client_config_check"] = _result_evidence(client_config_check)
                if _returncode(client_config_check):
                    raise RuntimeError(
                        f"technical control forwarder config invalid on {node}"
                    )

                forwarder_ready_deadline = (
                    time.monotonic() + CONTROL_READY_TIMEOUT_SECONDS
                )
                while time.monotonic() < forwarder_ready_deadline:
                    probe_cleanup = _safe_node_exec(
                        self.ctx, node,
                        f"docker rm -f {probe} >/dev/null 2>&1 || true",
                        timeout=30, check=False,
                    )
                    forward_request = _safe_node_exec(
                        self.ctx, node,
                        f"docker run --rm --name {probe} --network {network} "
                        f"--entrypoint /bin/sh {shlex.quote(CONTROL_IMAGE)} -ec "
                        + shlex.quote(_control_request_script(
                            entry["client_port"], marker,
                            persistent=False, host=client,
                        )),
                        timeout=30, check=False,
                    )
                    forward_attempt = {
                        "attempt": len(entry["forwarder_request_attempts"]) + 1,
                        "observed_ns": time.time_ns(),
                        "probe_cleanup_before": _result_evidence(probe_cleanup),
                        "request": _result_evidence(forward_request),
                    }
                    entry["forwarder_request_attempts"].append(forward_attempt)
                    if (
                        _returncode(forward_request) == 0
                        and _stdout(forward_request).strip() == "ok"
                    ):
                        entry["forwarder_ready"] = True
                        break
                    time.sleep(0.25)
                if not entry.get("forwarder_ready"):
                    raise RuntimeError(
                        f"technical control forwarder request failed on {node}"
                    )

                load_start = _safe_node_exec(
                    self.ctx, node,
                    f"docker run -d --name {load} --network {network} --entrypoint /bin/sh "
                    f"{shlex.quote(CONTROL_IMAGE)} -ec "
                    + shlex.quote(_control_request_script(
                        entry["client_port"], marker,
                        persistent=True, host=client,
                    )),
                    timeout=60, check=False,
                )
                entry["load_start"] = _result_evidence(load_start)
                if _returncode(load_start):
                    raise RuntimeError(
                        f"technical control load generator failed to start on {node}"
                    )
                load_inspect = _safe_node_exec(
                    self.ctx, node, f"docker inspect {load}",
                    timeout=30, check=False,
                )
                entry["load_start_inspect"] = _result_evidence(load_inspect)
                if not _inspect_running(load_inspect):
                    raise RuntimeError(
                        f"technical control load generator exited during startup on {node}"
                    )
                entry["control_ready_ns"] = time.time_ns()
                entry["control_preparation_duration_ns"] = (
                    entry["control_ready_ns"] - entry["control_started_ns"]
                )

            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                self._before_control_proof_poll(marker)
                proofs = {
                    node: self._control_proof(node, marker) for node in ("a", "b")
                }
                if all(value["proven"] for value in proofs.values()):
                    break
                self.health()
                time.sleep(0.5)
            if not proofs or not all(value["proven"] for value in proofs.values()):
                raise RuntimeError(f"{self.collector} eBPF positive control was not observed")
        except Exception as exc:
            failure = exc
        finally:
            cleanup_failures: list[dict[str, Any]] = []
            for node in ("a", "b"):
                entry = nodes[node]
                server = entry["server_container"]
                client = entry["client_container"]
                probe = entry["probe_container"]
                load = entry["load_container"]
                network = entry["network"]
                for label, command in (
                    ("server-inspect", f"docker inspect {server}"),
                    ("server-logs", f"docker logs {server}"),
                    ("client-inspect", f"docker inspect {client}"),
                    ("client-logs", f"docker logs {client}"),
                    ("client-top", f"docker top {client} -eo pid,ppid,lstart,args"),
                    ("load-inspect", f"docker inspect {load}"),
                    ("load-logs", f"docker logs {load}"),
                    ("load-top", f"docker top {load} -eo pid,ppid,lstart,args"),
                ):
                    result = _safe_node_exec(
                        self.ctx, node, command, timeout=30, check=False
                    )
                    path = self.root / f"control-{node}-{label}.txt"
                    path.write_text(
                        _stdout(result) + ("\n--- stderr ---\n" + _stderr(result) if _stderr(result) else ""),
                        encoding="utf-8",
                    )
                    entry[label.replace("-", "_")] = {
                        "path": path.relative_to(self.root).as_posix(),
                        "sha256": _sha256_file(path),
                        "returncode": _returncode(result),
                    }
                cleanup = _safe_node_exec(
                    self.ctx, node, f"docker rm -f {probe} {load} {client} {server}",
                    timeout=30, check=False
                )
                entry["cleanup"] = _result_evidence(cleanup)
                entry["cleanup_verification"] = {}
                for role, name in (
                    ("probe", probe), ("load", load),
                    ("client", client), ("server", server),
                ):
                    verification = _safe_node_exec(
                        self.ctx,
                        node,
                        "docker ps -a --format '{{.Names}}' --filter "
                        + shlex.quote(f"name=^/{name}$"),
                        timeout=30,
                        check=False,
                    )
                    observed_names = [
                        item.strip() for item in _stdout(verification).splitlines()
                        if item.strip()
                    ]
                    absent = _returncode(verification) == 0 and name not in observed_names
                    entry["cleanup_verification"][role] = {
                        **_result_evidence(verification),
                        "container": name,
                        "observed_names": observed_names,
                        "absent": absent,
                    }
                    if not absent:
                        cleanup_failures.append({
                            "node": node,
                            "role": role,
                            "container": name,
                            "returncode": _returncode(verification),
                            "observed_names": observed_names,
                        })
                network_cleanup_command = f"docker network rm {network}"
                network_cleanup_started_ns = time.time_ns()
                network_cleanup = _safe_node_exec(
                    self.ctx, node, network_cleanup_command,
                    timeout=30, check=False,
                )
                network_cleanup_finished_ns = time.time_ns()
                entry["network_cleanup"] = {
                    **_result_evidence(network_cleanup),
                    "command": network_cleanup_command,
                    "started_ns": network_cleanup_started_ns,
                    "finished_ns": network_cleanup_finished_ns,
                    "duration_ns": network_cleanup_finished_ns - network_cleanup_started_ns,
                }
                network_verification = _safe_node_exec(
                    self.ctx,
                    node,
                    "docker network ls --format '{{.Name}}' --filter "
                    + shlex.quote(f"name=^{network}$"),
                    timeout=30,
                    check=False,
                )
                observed_networks = [
                    item.strip() for item in _stdout(network_verification).splitlines()
                    if item.strip()
                ]
                network_absent = (
                    _returncode(network_verification) == 0
                    and network not in observed_networks
                )
                entry["network_cleanup_verification"] = {
                    **_result_evidence(network_verification),
                    "network": network,
                    "observed_names": observed_networks,
                    "absent": network_absent,
                }
                if not network_absent:
                    cleanup_failures.append({
                        "node": node,
                        "role": "network",
                        "network": network,
                        "returncode": _returncode(network_verification),
                        "observed_names": observed_networks,
                    })
            if cleanup_failures and failure is None:
                failure = RuntimeError("technical control cleanup absence verification failed")
            evidence = {
                "schema": "collector-positive-control-v5",
                "collector": self.collector,
                "source_domain": self.source_domain,
                "marker": marker,
                "nodes": nodes,
                "proofs": proofs,
                "selected_ebpf_origin_proven": bool(proofs)
                and all(value["proven"] for value in proofs.values()),
                "application_coverage": "not_assessed_by_technical_control",
                "control_network_scope": "private_bridge_no_host_port_publication",
                "control_process_design": "persistent_haproxy_forwarder_with_separate_wget_generator",
                "traffic_generator": "separate_wget_loop",
                "origin_interpretation": (
                    "collector-specific retained raw marker rule; Coroot binds the "
                    "forwarder client, OBI accepts either persistent HAProxy endpoint, "
                    "and DeepFlow may observe any marker side"
                ),
                "native_sdk": False,
                "cleanup_verified": not cleanup_failures,
                "cleanup_failures": cleanup_failures,
                "technical_failure": str(failure) if failure is not None else None,
            }
            _write_json(self.root / "technical-positive-control.json", evidence)
            self.positive_control_evidence = evidence

        if failure is not None:
            raise failure
        if not evidence["selected_ebpf_origin_proven"]:
            raise RuntimeError(f"{self.collector} eBPF positive control was not observed")
        return evidence

    def _before_control_proof_poll(self, marker: str) -> None:
        """Allow file-backed collectors to expose a fresh retained prefix."""

    def certify_controls(self, timeout: float = 60.0) -> dict[str, Any]:
        """Campaign-facing name for the retained, non-SDK eBPF positive control."""
        return self.positive_control(timeout=timeout)

    def _control_proof(self, node: str, marker: str) -> dict[str, Any]:
        path = self.root / f"{node}.jsonl"
        if not path.exists():
            return {"proven": False, "reason": "receiver_file_missing"}
        expected_source = f"{self.source_domain}:{node}"
        malformed = 0
        for ordinal, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if record.get("source") != expected_source:
                continue
            for resource in record.get("payload", {}).get("resourceSpans", []):
                attrs = _attributes(resource.get("resource", {}).get("attributes", []))
                origin = self._origin_proof(resource, attrs)
                if not origin or not self._control_origin_matches(node, origin, attrs):
                    continue
                for scope in resource.get("scopeSpans", []):
                    for span in scope.get("spans", []):
                        span_attrs = _attributes(span.get("attributes", []))
                        if marker in json.dumps([span.get("name"), span_attrs], sort_keys=True):
                            raw_ref = record.get("raw_ref")
                            raw_path = self.root / raw_ref if isinstance(raw_ref, str) else None
                            raw_digest = (
                                _sha256_file(raw_path)
                                if raw_path is not None and raw_path.is_file()
                                else None
                            )
                            raw_ok = raw_digest is not None and raw_digest == record.get("raw_sha256")
                            return {
                                "proven": raw_ok,
                                "reason": "raw_collector_record" if raw_ok else "raw_body_missing",
                                "line": ordinal,
                                "raw_ref": raw_ref,
                                "raw_sha256": raw_digest,
                                "origin": origin,
                                "resource": attrs,
                                "span_name": span.get("name"),
                            }
        return {"proven": False, "reason": "marker_or_origin_missing", "malformed": malformed}

    @staticmethod
    def _control_origin_matches(
        node: str, origin: dict[str, Any], attrs: dict[str, Any]
    ) -> bool:
        """Preserve each collector's origin rule unless it narrows this hook."""
        return True

    @staticmethod
    def _control_origin_names(
        origin: dict[str, Any], attrs: dict[str, Any]
    ) -> set[str]:
        values = {
            str(value)
            for value in (
                attrs.get("container.name"), attrs.get("container.id"),
                attrs.get("service.name"), origin.get("container.name"),
                origin.get("container.id"), origin.get("service.name"),
            )
            if value
        }
        return {value.removeprefix("/docker/") for value in values}

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
                "receiver_closed_checkpoints": evidence.get(
                    "receiver_closed_checkpoints", {}
                ),
                "scope": (
                    "all bytes accepted by the three local receivers are closed and "
                    "hash checked; kernel, producer, and pre-receiver exporter loss "
                    "remain outside this snapshot"
                ),
            }
            _write_json(self.root / "final-snapshot.json", final)
            # The final snapshot is created after the drain checkpoint, so
            # refresh collector.json to bind this last retained artifact too.
            self._finalize_checkpoint()
            if not (
                final["technical_complete"]
                and final["accepted_receiver_bytes_closed_and_hashed"]
            ):
                raise RuntimeError(f"{self.collector} final snapshot is technically invalid")
            return
        self.health()
        for node in ("a", "b"):
            self._retain_node_evidence(node, "snapshot")
        _write_json(
            self.root / "live-prefix.json",
            {
                "schema": "collector-live-prefix-v5",
                "collector": self.collector,
                "captured_ns": time.time_ns(),
                "receivers_closed": False,
                "producer_pending": True,
                "scope": (
                    "complete JSONL records currently saved; collector/kernel/exporter "
                    "work may still be pending and is not part of this live prefix"
                ),
            },
        )

    def _retain_node_evidence(self, node: str, stage: str) -> None:
        commands = {
            "logs": f"docker logs {self.container_name}",
            "stats": f'docker stats --no-stream --format "{{{{json .}}}}" {self.container_name}',
            "inspect": f"docker inspect {self.container_name}",
        }
        statuses = {}
        for label, command in commands.items():
            result = self.ctx.node_exec(node, command, timeout=60, check=False)
            content = _stdout(result) + _stderr(result)
            (self.root / f"{stage}-{node}-{label}.log").write_text(content, encoding="utf-8")
            statuses[label] = {
                "available": _returncode(result) == 0 and bool(_stdout(result).strip()),
                "returncode": _returncode(result),
                "bytes": len(content.encode("utf-8")),
            }
        _write_json(self.root / f"{stage}-{node}-evidence.json", statuses)

    def final_drain(self) -> dict[str, Any]:
        """Stop collectors and freeze closed, hash-checked receiver inputs."""
        if self._drained:
            evidence = dict(self._drain_evidence or {})
            if not evidence.get("technical_valid"):
                raise RuntimeError(f"{self.collector} final drain is technically invalid")
            return evidence
        termination = {}
        for node in ("a", "b"):
            self._retain_node_evidence(node, "pre-drain")
            since_result = self.ctx.node_exec(node, "date +%s", timeout=10, check=False)
            since = _stdout(since_result).strip()
            stop = self.ctx.node_exec(
                node,
                f"docker stop -t {self.stop_grace_seconds} {self.container_name}",
                timeout=self.stop_grace_seconds + 30,
                check=False,
            )
            inspect = self.ctx.node_exec(
                node, f"docker inspect {self.container_name}", timeout=30, check=False
            )
            logs = self.ctx.node_exec(
                node, f"docker logs {self.container_name}", timeout=30, check=False
            )
            log_text = _stdout(logs) + _stderr(logs)
            (self.root / f"final-{node}-collector.log").write_text(
                log_text, encoding="utf-8"
            )
            until_result = self.ctx.node_exec(node, "date +%s", timeout=10, check=False)
            until = _stdout(until_result).strip()
            events = self.ctx.node_exec(
                node,
                f"docker events --since {shlex.quote(since or '0')} --until {shlex.quote(until or '0')} "
                f"--filter container={self.container_name} --format '{{{{json .}}}}'",
                timeout=30,
                check=False,
            )
            (self.root / f"final-{node}-docker-events.jsonl").write_text(
                _stdout(events), encoding="utf-8"
            )
            termination[node] = self._termination_evidence(
                stop=stop, inspect=inspect, events=events, logs=log_text
            )
            termination[node]["event_query"] = {
                "since": since,
                "until": until,
                "returncode": _returncode(events),
                "stderr": _stderr(events).strip(),
            }

        # The acceptance record is only a boundary marker. The subsequent
        # receiver shutdown joins all handlers and is the saved-byte closure.
        barriers = {node: self._receiver_barrier(node) for node in RECEIVERS}
        receivers = self._close_receivers()
        valid = (
            all(value.get("technical_valid") for value in termination.values())
            and all(value.get("accepted") for value in barriers.values())
            and all(value.get("technical_valid") for value in receivers.values())
        )
        evidence = {
            "schema": "collector-final-drain-v5",
            "collector": self.collector,
            "source_version": self.source_version,
            "source_shutdown_facts": self._shutdown_source_facts(),
            "termination": termination,
            "receiver_acceptance_barriers": barriers,
            "receiver_closed_checkpoints": receivers,
            "accepted_receiver_bytes_closed_and_hashed": all(
                value.get("saved_bytes_valid")
                and value.get("parent_hash_verification") is True
                for value in receivers.values()
            ),
            "collector_exporter_flush": self._exporter_flush_claim(termination),
            "kernel_or_producer_loss_absent": None,
            "technical_complete": valid,
            "technical_valid": valid,
            "scope": (
                "clean observed collector termination and complete saved receiver bytes; "
                "zero kernel, producer, or pre-receiver exporter loss is not claimed"
            ),
        }
        self._drain_evidence = evidence
        _write_json(self.root / "drain-evidence.json", evidence)
        self._finalize_checkpoint()
        # Mark complete only after receiver closure and the durable checkpoint;
        # an unexpected transport/filesystem exception remains retryable by the
        # defensive close path.
        self._drained = True
        if not valid:
            raise RuntimeError(f"{self.collector} final drain is technically invalid")
        return dict(evidence)

    def close(self) -> None:
        if self._closed:
            return
        error = None
        try:
            if not self._drained:
                self.final_drain()
        except Exception as exc:
            error = exc
        finally:
            for process in self.processes.values():
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
            for log in self.logs:
                if not log.closed:
                    log.close()
            self._closed = True
        if error is not None:
            raise error

    def _close_receivers(self) -> dict[str, Any]:
        evidence = {}
        for node, process in self.processes.items():
            forced = False
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    forced = True
                    process.kill()
                    process.wait(timeout=5)
            checkpoint_path = self.root / f"receiver-closed-{node}.json"
            checkpoint = None
            checkpoint_error = None
            try:
                checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            except Exception as exc:
                checkpoint_error = repr(exc)
            parent_verified = self._verify_receiver_checkpoint(node, checkpoint)
            evidence[node] = {
                "returncode": process.returncode,
                "forced_kill": forced,
                "checkpoint": checkpoint_path.name,
                "checkpoint_error": checkpoint_error,
                "in_flight_handlers_joined": bool(
                    checkpoint and checkpoint.get("in_flight_handlers_joined")
                ),
                "saved_bytes_valid": bool(checkpoint and checkpoint.get("saved_bytes_valid")),
                "parent_hash_verification": parent_verified,
                "technical_valid": (
                    process.returncode == 0
                    and not forced
                    and checkpoint_error is None
                    and bool(checkpoint and checkpoint.get("in_flight_handlers_joined"))
                    and bool(checkpoint and checkpoint.get("saved_bytes_valid"))
                    and parent_verified
                ),
            }
        return evidence

    def _verify_receiver_checkpoint(self, node: str, checkpoint: Any) -> bool:
        if not isinstance(checkpoint, dict):
            return False

        def matches(path: Path, expected: Any) -> bool:
            if not isinstance(expected, dict):
                return False
            present = path.is_file()
            if present != bool(expected.get("present")):
                return False
            if not present:
                return expected.get("bytes") == 0 and expected.get("sha256") is None
            return (
                path.stat().st_size == expected.get("bytes")
                and _sha256_file(path) == expected.get("sha256")
            )

        output = self.root / f"{node}.jsonl"
        if not matches(output, checkpoint.get("wrapper")):
            return False
        if not matches(output.with_suffix(".errors.jsonl"), checkpoint.get("errors")):
            return False
        raw = checkpoint.get("raw_capture")
        if not isinstance(raw, dict) or raw.get("errors"):
            return False
        captures = raw.get("captures")
        if not isinstance(captures, list) or raw.get("capture_count") != len(captures):
            return False
        capture_root = output.with_suffix(".raw")
        actual_directories = (
            len([path for path in capture_root.iterdir() if path.is_dir()])
            if capture_root.is_dir()
            else 0
        )
        if actual_directories != len(captures):
            return False
        for capture in captures:
            if not isinstance(capture, dict) or capture.get("valid") is not True:
                return False
            metadata = self.root / str(capture.get("metadata", ""))
            body = self.root / str(capture.get("raw_ref", ""))
            if not metadata.is_file() or not body.is_file():
                return False
            if _sha256_file(metadata) != capture.get("metadata_sha256"):
                return False
            if _sha256_file(body) != capture.get("raw_sha256"):
                return False
            if body.stat().st_size != capture.get("raw_size_bytes"):
                return False
        return True

    def _finalize_checkpoint(self) -> None:
        if any(process.poll() is None for process in self.processes.values()):
            raise RuntimeError("cannot finalize checkpoint with a live receiver")
        for log in self.logs:
            if not log.closed:
                log.flush()
        metadata_path = self.root / "collector.json"
        metadata = (
            json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata_path.exists()
            else {
                "schema": "collector-lifecycle-v5",
                "collector": self.collector,
                "source_domain": self.source_domain,
                "source_version": self.source_version,
                "image": self.image,
            }
        )
        retained = {}
        for path in sorted(self.root.iterdir()):
            if path == metadata_path or not path.is_file():
                continue
            retained[path.name] = {
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        metadata.update(
            lifecycle="closed",
            closed_checkpoint=True,
            closed_ns=time.time_ns(),
            selected_ebpf_origin_proven=(
                self.positive_control_evidence or {}
            ).get("selected_ebpf_origin_proven"),
            retained_file_hashes=retained,
            drain_evidence="drain-evidence.json",
        )
        self._write_collector_metadata(metadata)

    def _termination_evidence(self, *, stop, inspect, events, logs: str) -> dict[str, Any]:
        parsed = None
        parse_error = None
        try:
            rows = json.loads(_stdout(inspect))
            parsed = rows[0] if isinstance(rows, list) else rows
        except Exception as exc:
            parse_error = repr(exc)
        state = parsed.get("State", {}) if isinstance(parsed, dict) else {}
        event_rows, event_errors = [], []
        for line in _stdout(events).splitlines():
            try:
                event_rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                event_errors.append(str(exc))
        sigkills = [
            row for row in event_rows
            if row.get("Action") == "kill"
            and str(row.get("Actor", {}).get("Attributes", {}).get("signal")) == "9"
        ]
        log_assessment = self._assess_terminal_logs(logs)
        reasons = []
        if _returncode(stop) != 0:
            reasons.append("docker_stop_failed")
        if _returncode(inspect) != 0:
            reasons.append("terminal_inspect_failed")
        if parse_error or not isinstance(parsed, dict):
            reasons.append("terminal_inspect_unavailable")
        else:
            if state.get("Running") is not False:
                reasons.append("container_still_running")
            if state.get("ExitCode") != 0:
                reasons.append(f"unexpected_exit_code:{state.get('ExitCode')}")
            if state.get("OOMKilled") is not False:
                reasons.append("oom_killed")
            if state.get("Error") not in ("", None):
                reasons.append("docker_state_error")
            if not state.get("FinishedAt"):
                reasons.append("finished_at_missing")
            if "RestartCount" not in parsed:
                reasons.append("restart_count_missing")
            elif parsed.get("RestartCount") != 0:
                reasons.append(f"restarted:{parsed.get('RestartCount')}")
        if sigkills:
            reasons.append("sigkill_observed")
        if event_errors:
            reasons.append("docker_events_malformed")
        reasons.extend(log_assessment["invalid_reasons"])
        return {
            "stop_returncode": _returncode(stop),
            "stop_stdout": _stdout(stop).strip(),
            "stop_stderr": _stderr(stop).strip(),
            "inspect_returncode": _returncode(inspect),
            "inspect_parse_error": parse_error,
            "running": state.get("Running"),
            "finished_at": state.get("FinishedAt"),
            "exit_code": state.get("ExitCode"),
            "oom_killed": state.get("OOMKilled"),
            "state_error": state.get("Error"),
            "restart_count": parsed.get("RestartCount") if isinstance(parsed, dict) else None,
            "sigkill_events": len(sigkills),
            "event_rows": len(event_rows),
            "event_parse_errors": event_errors,
            "log_assessment": log_assessment,
            "technical_invalid_reasons": reasons,
            "technical_valid": not reasons,
        }

    def _receiver_barrier(self, node: str) -> dict[str, Any]:
        output = self.root / f"{node}.jsonl"
        before = output.stat().st_size if output.exists() else 0
        request = urllib.request.Request(
            f"http://127.0.0.1:{RECEIVERS[node]}/v1/traces",
            data=b'{"resourceSpans":[]}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                status = response.status
        except Exception as exc:
            return {"accepted": False, "error": repr(exc), "before_bytes": before}
        deadline = time.monotonic() + 5
        after = before
        while time.monotonic() < deadline:
            after = output.stat().st_size if output.exists() else 0
            if after > before:
                break
            time.sleep(0.05)
        return {
            "accepted": status == 200 and after > before,
            "http_status": status,
            "before_bytes": before,
            "after_bytes": after,
            "scope": "receiver write completion after collector termination; not exporter flush proof",
        }

    def _origin_proof(self, resource: dict[str, Any], attrs: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError

    def _config_summary(self) -> dict[str, Any]:
        raise NotImplementedError

    def _assess_terminal_logs(self, logs: str) -> dict[str, Any]:
        raise NotImplementedError

    def _shutdown_source_facts(self) -> dict[str, Any]:
        raise NotImplementedError

    def _exporter_flush_claim(self, termination: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def _write_config(self, node: str, port: int) -> tuple[Path, str]:
        raise NotImplementedError

    def _docker_command(self, node: str, remote_config: str, port: int) -> str:
        raise NotImplementedError


class OBICollectorsV5(CollectorsV5):
    collector = "obi"
    container_name = "study-obi-v5"
    image = OBI_IMAGE
    source_version = "v0.15.2"
    stop_grace_seconds = 45

    @staticmethod
    def _control_origin_matches(
        node: str, origin: dict[str, Any], attrs: dict[str, Any]
    ) -> bool:
        # OBI may legitimately report either persistent HAProxy side of the
        # exchange.  Exclude the short-lived readiness probe/load generator.
        expected = {
            f"study-ebpf-control-server-{node}",
            f"study-ebpf-control-client-{node}",
        }
        return bool(expected & CollectorsV5._control_origin_names(origin, attrs))

    def __init__(self, ctx, *, semantic: bool = True):
        super().__init__(ctx, semantic=semantic)
        self._obi_startup_complete = False
        self._obi_startup_error: str | None = None

    def start(self) -> None:
        try:
            super().start()
            self._obi_startup_complete = True
        except Exception as original:
            self._obi_startup_error = repr(original)
            raise

    def close(self) -> None:
        error: Exception | None = None
        if self._obi_startup_complete:
            try:
                super().close()
            except Exception as exc:
                error = exc
        elif not self._closed:
            incomplete = {"schema": "collector-incomplete-startup-v5", "collector": self.collector,
                          "startup_complete": False, "startup_error": self._obi_startup_error,
                          "collector_cleanup": {}, "receiver_processes": {}}
            for node in ("a", "b"):
                inspect = _safe_node_exec(
                    self.ctx, node, f"docker inspect {self.container_name}",
                    timeout=30, check=False,
                )
                logs = _safe_node_exec(
                    self.ctx, node, f"docker logs {self.container_name}",
                    timeout=30, check=False,
                )
                removal = _safe_node_exec(
                    self.ctx, node, f"docker rm -f {self.container_name}",
                    timeout=30, check=False,
                )
                incomplete["collector_cleanup"][node] = {
                    "inspect": _result_evidence(inspect),
                    "logs": _result_evidence(logs),
                    "removal": _result_evidence(removal),
                }
            for node, process in self.processes.items():
                forced = False
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        forced = True
                        process.kill()
                        process.wait(timeout=5)
                incomplete["receiver_processes"][node] = {
                    "returncode": process.returncode,
                    "forced_kill": forced,
                }
            for log in self.logs:
                if not log.closed:
                    log.close()
            incomplete["final_drain_attempted"] = False
            incomplete["accepted_receiver_bytes_closed_and_hashed"] = False
            _write_json(self.root / "startup-incomplete.json", incomplete)
            self._closed = True
        if error is not None:
            raise error

    def _config_summary(self) -> dict[str, Any]:
        return {
            "transport": "OTLP/HTTP protobuf",
            "receiver_per_guest": True,
            "context_propagation": "all",
            "semantic_capture": self.semantic,
            "raw_wire_capture": True,
            "control_network": "private_bridge_no_host_port_publication",
        }

    def _assess_terminal_logs(self, logs: str) -> dict[str, Any]:
        success = "OpenTelemetry eBPF Instrumentation successfully exiting" in logs
        exact_failures = [
            marker for marker in (
                "error shutting down traces exporter",
                "OpenTelemetry eBPF Instrumentation ran with errors",
                "graceful shutdown has timed out",
                "error sending trace to consumer",
                "sending queue is full",
            )
            if marker in logs
        ]
        reasons = []
        if not success:
            reasons.append("obi_successful_exit_marker_missing")
        if exact_failures:
            reasons.append("obi_unrecovered_export_or_shutdown_failure")
        return {
            "graceful_success_marker": success,
            "source_specific_failure_markers": exact_failures,
            "invalid_reasons": reasons,
        }

    def _shutdown_source_facts(self) -> dict[str, Any]:
        return {
            "pin": "v0.15.2 commit b28e4e7f",
            "source_paths": [
                "cmd/obi/main.go",
                "pkg/obi/config.go",
                "pkg/export/otel/traces.go",
                "pkg/export/otel/trace_exporter.go",
            ],
            "signal": "main registers SIGINT/SIGTERM with signal.NotifyContext",
            "pipeline": "instrumenter waits for application pipeline completion",
            "exporter": (
                "trace exporter Shutdown closes and drains its queue under a separate "
                "10-second context, then stops the OTLP client"
            ),
            "configured_stop_grace_seconds": self.stop_grace_seconds,
        }

    def _exporter_flush_claim(self, termination: dict[str, Any]) -> dict[str, Any]:
        clean = all(value.get("technical_valid") for value in termination.values())
        return {
            "status": "graceful_source_path_observed" if clean else "failed_or_unproven",
            "queue_shutdown_implemented_by_pin": True,
            "zero_pre_queue_or_kernel_loss_proven": False,
        }

    def _write_config(self, node: str, port: int) -> tuple[Path, str]:
        config: dict[str, Any] = {
            "log_level": "INFO",
            "discovery": {
                "instrument": [{"exe_path": "*", "containers_only": True}],
                "exclude_instrument": [
                    {"exe_path": "*all-in-one-linux"},
                    {"exe_path": "*jaeger*"},
                    {"exe_path": "*psql"},
                    {"exe_path": "*mysql"},
                    {"exe_path": "*valkey-cli"},
                    {"exe_path": "*deepflow-agent"},
                    {"container_name": "study-kafka-admin-*"},
                ],
                "exclude_otel_instrumented_services": False,
                "disabled_route_harvesters": ["java", "nodejs"],
            },
            "javaagent": {"enabled": False},
            "nodejs": {"enabled": False, "manual_spans": False},
            "attributes": {"select": {"traces": {"include": ["db.query.text", "service.peer.name"]}}},
            "ebpf": {
                "context_propagation": "all",
                "track_request_headers": True,
                "batch_timeout": "1s",
                "buffer_sizes": {"http": 16384 if self.semantic else 8192},
                "payload_extraction": {"http": {"enrichment": {
                    "enabled": True,
                    "policy": {"default_action": {"headers": "exclude", "body": "exclude"}},
                    "rules": [
                        {"action": "include", "type": "headers", "scope": "all", "match": {
                            "patterns": ["x-experiment-request-id", "content-length", "content-type", "content-encoding", "transfer-encoding"] if self.semantic else ["x-experiment-request-id"],
                            "case_sensitive": False,
                        }},
                        {"action": "include", "type": "body", "scope": "all", "match": {
                            "url_path_patterns": ["/api/*", "/wrk2-api/*", "/owners/*"] if self.semantic else ["/api/*"]
                        }},
                    ],
                }}},
            },
            "routes": {"unmatched": "path"},
            "otel_traces_export": {
                "endpoint": f"http://192.168.76.1:{port}/v1/traces",
                "protocol": "http/protobuf",
            },
        }
        path = self.root / f"config-{node}.yaml"
        path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        return path, "/tmp/collector-v5-obi.yaml"

    def _docker_command(self, node: str, remote_config: str, port: int) -> str:
        return (
            f"docker run -d --name {self.container_name} --privileged --pid=host --network=host "
            "-v /sys:/sys -v /proc:/host/proc:ro "
            "-v /var/run/docker.sock:/var/run/docker.sock "
            f"-v {remote_config}:/config.yaml:ro "
            "-e OTEL_EBPF_CONFIG_PATH=/config.yaml "
            f"{shlex.quote(self.image)}"
        )

    def _origin_proof(self, resource: dict[str, Any], attrs: dict[str, Any]) -> dict[str, Any] | None:
        if (
            attrs.get("telemetry.distro.name") == "opentelemetry-ebpf-instrumentation"
            and attrs.get("telemetry.distro.version") == "v0.15.2"
            and attrs.get("otel.scope.name") == "go.opentelemetry.io/obi"
            and str(attrs.get("container.name", "")).startswith("study-ebpf-control-")
        ):
            return {
                "telemetry.distro.name": attrs["telemetry.distro.name"],
                "telemetry.distro.version": attrs["telemetry.distro.version"],
                "otel.scope.name": attrs["otel.scope.name"],
                "container.name": attrs["container.name"],
            }
        return None


class CorootCollectorsV5(CollectorsV5):
    collector = "coroot"
    container_name = "study-coroot-v5"
    image = COROOT_IMAGE
    source_version = "1.37.0"
    source_commit = COROOT_COMMIT
    stop_grace_seconds = 30

    @staticmethod
    def _control_origin_matches(
        node: str, origin: dict[str, Any], attrs: dict[str, Any]
    ) -> bool:
        expected = f"study-ebpf-control-client-{node}"
        return expected in CollectorsV5._control_origin_names(origin, attrs)

    def _config_summary(self) -> dict[str, Any]:
        return {
            "transport": "OTLP/HTTP",
            "receiver_per_guest": True,
            "traces_sampling": 1,
            "api_key_set": False,
            "additional_export_endpoints": [],
            "raw_wire_capture": True,
            "known_causal_limit": "independent outbound client roots; parent/async links unknown",
        }

    def _assess_terminal_logs(self, logs: str) -> dict[str, Any]:
        success = "cleanup completed" in logs
        timed_out = "cleanup timed out, forcing exit" in logs
        reasons = []
        if not success:
            reasons.append("coroot_cleanup_completed_marker_missing")
        if timed_out:
            reasons.append("coroot_cleanup_timed_out")
        return {
            "graceful_success_marker": success,
            "source_specific_failure_markers": (
                ["cleanup timed out, forcing exit"] if timed_out else []
            ),
            "invalid_reasons": reasons,
        }

    def _shutdown_source_facts(self) -> dict[str, Any]:
        return {
            "pin": f"1.37.0 commit {self.source_commit}",
            "source_paths": ["main.go", "tracing/tracing.go"],
            "signal": "main handles SIGTERM/SIGINT and runs registry/log/profile cleanup",
            "cleanup_timeout_seconds": 10,
            "exporter": (
                "each container tracer owns an SDK batch provider; pinned source exposes "
                "no tracer-provider Shutdown during process cleanup"
            ),
            "configured_stop_grace_seconds": self.stop_grace_seconds,
        }

    def _exporter_flush_claim(self, termination: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "unsupported_by_pinned_source",
            "queue_shutdown_implemented_by_pin": False,
            "clean_process_cleanup_observed": all(
                value.get("technical_valid") for value in termination.values()
            ),
            "zero_exporter_or_kernel_loss_proven": False,
            "interpretation": (
                "ambiguous internal exporter buffers are retained uncertainty, not an "
                "automatic technical failure when process cleanup and saved bytes are valid"
            ),
        }

    def _write_config(self, node: str, port: int) -> tuple[Path, str]:
        config = {
            "TRACES_ENDPOINT": f"http://192.168.76.1:{port}/v1/traces",
            "TRACES_SAMPLING": "1",
            "DISABLE_LOG_PARSING": "true",
            "DISABLE_JSON_LOG_PARSING": "true",
            "DISABLE_PINGER": "true",
            "DISABLE_GPU_MONITORING": "true",
            "ENABLE_JAVA_TLS": "false",
            "ENABLE_JAVA_ASYNC_PROFILER": "false",
            "GO_HEAP_PROFILER": "disabled",
            "MIN_CONTAINER_AGE": "0",
            "MAX_SPOOL_SIZE": "500MB",
        }
        path = self.root / f"config-{node}.json"
        _write_json(path, config)
        return path, "/tmp/collector-v5-coroot.json"

    def _docker_command(self, node: str, remote_config: str, port: int) -> str:
        config = json.loads((self.root / f"config-{node}.json").read_text(encoding="utf-8"))
        env = " ".join(
            f"-e {key}={shlex.quote(str(value))}" for key, value in sorted(config.items())
        )
        return (
            f"docker run -d --name {self.container_name} --privileged --pid=host --network=host "
            "-v /sys/kernel/debug:/sys/kernel/debug -v /sys/fs/cgroup:/sys/fs/cgroup:ro "
            "-v /var/run/docker.sock:/var/run/docker.sock:ro "
            f"{env} {shlex.quote(self.image)}"
        )

    def _origin_proof(self, resource: dict[str, Any], attrs: dict[str, Any]) -> dict[str, Any] | None:
        scope_names = {
            str(scope.get("scope", {}).get("name", ""))
            for scope in resource.get("scopeSpans", [])
        }
        if "coroot-node-agent" in scope_names and (
            attrs.get("container.id") or attrs.get("service.name")
        ):
            return {
                "scope.name": "coroot-node-agent",
                "container.id": attrs.get("container.id"),
                "service.name": attrs.get("service.name"),
                "source_commit": self.source_commit,
            }
        return None


__all__ = [
    "CollectorUnavailable",
    "CollectorsV5",
    "OBICollectorsV5",
    "CorootCollectorsV5",
    "create_collectors_v5",
    "make_collectors",
]
