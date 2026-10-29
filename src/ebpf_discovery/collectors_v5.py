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
        raise CollectorUnavailable(
            name, "owned by the DeepFlow adapter; no substitution by OBI or Coroot"
        )
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
                "ebpf_discovery.receiver",
                "--port",
                str(port),
                "--out",
                str(self.root / f"{node}.jsonl"),
                "--source",
                source,
                "--node",
                node,
                "--raw-capture",
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

    def positive_control(self, timeout: float = 60.0) -> dict[str, Any]:
        """Prove selected eBPF origin with a non-SDK container HTTP exchange."""
        marker = f"collector-control-v5-{self.collector}-{time.time_ns()}"
        nodes: dict[str, Any] = {}
        for index, node in enumerate(("a", "b")):
            port = 18081 + index
            pull = self.ctx.node_exec(
                node, f"docker pull {shlex.quote(CONTROL_IMAGE)}", timeout=300
            )
            (self.root / f"control-pull-{node}.log").write_text(
                _stdout(pull) + _stderr(pull), encoding="utf-8"
            )
            image_inspect = self.ctx.node_exec(
                node, f"docker image inspect {shlex.quote(CONTROL_IMAGE)}", timeout=60
            )
            (self.root / f"control-image-{node}.json").write_text(
                _stdout(image_inspect), encoding="utf-8"
            )
            server = f"study-ebpf-control-server-{node}"
            client = f"study-ebpf-control-client-{node}"
            self.ctx.node_exec(
                node,
                f"docker rm -f {server} >/dev/null 2>&1 || true; "
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
                f"docker run --rm --name {client}-probe --network host --entrypoint /bin/sh "
                f"{shlex.quote(CONTROL_IMAGE)} -c "
                + shlex.quote(f"busybox wget -qO- http://127.0.0.1:{port}/{marker}"),
                timeout=60,
                check=False,
            )
            client_start = self.ctx.node_exec(
                node,
                f"docker rm -f {client} >/dev/null 2>&1 || true; "
                f"docker run -d --name {client} --network host --entrypoint /bin/sh "
                f"{shlex.quote(CONTROL_IMAGE)} -c "
                + shlex.quote(
                    f"while true; do busybox wget -qO- http://127.0.0.1:{port}/{marker} "
                    ">/dev/null || exit 1; sleep 1; done"
                ),
                timeout=60,
                check=False,
            )
            nodes[node] = {
                "port": port,
                "server_container": server,
                "client_container": client,
                "request_returncode": _returncode(request),
                "request_stdout": _stdout(request),
                "request_stderr": _stderr(request),
                "client_start_returncode": _returncode(client_start),
                "client_start_stdout": _stdout(client_start).strip(),
                "control_image": CONTROL_IMAGE,
            }
            if (
                _returncode(request)
                or _stdout(request).strip() != "ok"
                or _returncode(client_start)
            ):
                raise RuntimeError(f"technical control HTTP request failed on {node}")

        deadline = time.monotonic() + timeout
        proofs = {}
        while time.monotonic() < deadline:
            proofs = {
                node: self._control_proof(node, marker) for node in ("a", "b")
            }
            if all(value["proven"] for value in proofs.values()):
                break
            self.health()
            time.sleep(0.5)
        for node in ("a", "b"):
            self.ctx.node_exec(
                node,
                f"docker rm -f study-ebpf-control-client-{node} study-ebpf-control-server-{node}",
                timeout=30,
                check=False,
            )
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
            "native_sdk": False,
        }
        _write_json(self.root / "technical-positive-control.json", evidence)
        self.positive_control_evidence = evidence
        if not evidence["selected_ebpf_origin_proven"]:
            raise RuntimeError(f"{self.collector} eBPF positive control was not observed")
        return evidence

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
                if not origin:
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

    def snapshot(self) -> None:
        self.health()
        for node in ("a", "b"):
            self._retain_node_evidence(node, "snapshot")

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

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        termination = {}
        for node in ("a", "b"):
            self._retain_node_evidence(node, "pre-close")
            stop = self.ctx.node_exec(
                node,
                f"docker stop -t 30 {self.container_name}",
                timeout=60,
                check=False,
            )
            inspect = self.ctx.node_exec(
                node,
                f"docker inspect --format '{{{{json .State}}}}' {self.container_name}",
                timeout=30,
                check=False,
            )
            logs = self.ctx.node_exec(
                node, f"docker logs {self.container_name}", timeout=30, check=False
            )
            (self.root / f"final-{node}-collector.log").write_text(
                _stdout(logs) + _stderr(logs), encoding="utf-8"
            )
            termination[node] = {
                "stop_returncode": _returncode(stop),
                "stop_stdout": _stdout(stop).strip(),
                "stop_stderr": _stderr(stop).strip(),
                "state": _stdout(inspect).strip(),
                "state_returncode": _returncode(inspect),
            }

        barriers = {node: self._receiver_barrier(node) for node in ("a", "b")}
        _write_json(
            self.root / "drain-evidence.json",
            {
                "collector": self.collector,
                "termination": termination,
                "receiver_write_barriers": barriers,
                "collector_flush_proven": False,
                "exporter_loss": "unproven; collector termination plus receiver acceptance barrier is retained but is not an exporter flush acknowledgement",
            },
        )
        for process in self.processes.values():
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        for log in self.logs:
            log.close()
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

    def _write_config(self, node: str, port: int) -> tuple[Path, str]:
        raise NotImplementedError

    def _docker_command(self, node: str, remote_config: str, port: int) -> str:
        raise NotImplementedError


class OBICollectorsV5(CollectorsV5):
    collector = "obi"
    container_name = "study-obi-v5"
    image = OBI_IMAGE
    source_version = "v0.15.2"

    def _config_summary(self) -> dict[str, Any]:
        return {
            "transport": "OTLP/HTTP protobuf",
            "receiver_per_guest": True,
            "context_propagation": "all",
            "semantic_capture": self.semantic,
            "raw_wire_capture": True,
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
