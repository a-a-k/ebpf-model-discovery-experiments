from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from pathlib import Path

import pytest

from ebpf_discovery.collectors_v5 import (
    CONTROL_IMAGE,
    COROOT_IMAGE,
    CollectorUnavailable,
    CorootCollectorsV5,
    OBICollectorsV5,
    create_collectors_v5,
    make_collectors,
    _control_request_script,
    _control_server_script,
)
from ebpf_discovery.receiver import _capture_wire_body
from ebpf_discovery.receiver_v5 import _file, _raw_capture_audit


class Result:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class Context:
    def __init__(self, root: Path):
        self.out = root
        self.calls = []
        self.puts = []
        self.results = {}

    def node_put(self, node, source, destination):
        self.puts.append((node, Path(source), destination))

    def node_exec(self, node, command, **kwargs):
        self.calls.append((node, command, kwargs))
        for needle, result in self.results.items():
            if needle in command:
                return result
        if "docker image inspect" in command:
            return Result('[{"Id":"sha256:pinned"}]')
        return Result("ok")


@pytest.mark.parametrize(
    ("name", "kind"), [("obi", OBICollectorsV5), ("coroot", CorootCollectorsV5)]
)
def test_factory_has_no_cross_arm_substitution(tmp_path: Path, name, kind) -> None:
    assert isinstance(create_collectors_v5(Context(tmp_path), name), kind)
    assert isinstance(make_collectors(Context(tmp_path), name), kind)
    from ebpf_discovery.deepflow_v5 import DeepFlowCollectorsV5
    assert isinstance(create_collectors_v5(Context(tmp_path), "deepflow"), DeepFlowCollectorsV5)
    for blocked in ("newrelic", "unknown"):
        with pytest.raises(CollectorUnavailable) as exc:
            create_collectors_v5(Context(tmp_path), blocked)
        assert exc.value.collector == blocked
        assert "substitution" in exc.value.reason or "fixed collector" in exc.value.reason or "license" in exc.value.reason


@pytest.mark.parametrize("collector_type", [OBICollectorsV5, CorootCollectorsV5])
def test_start_manifest_identifies_collector_and_both_guest_receivers(
    tmp_path: Path, monkeypatch, collector_type
) -> None:
    ctx = Context(tmp_path)
    collector = collector_type(ctx)
    monkeypatch.setattr(collector, "_start_receivers", lambda: None)
    monkeypatch.setattr(collector, "_wait_container_readiness", lambda: None)
    collector.start()

    manifest = json.loads((collector.root / "collector.json").read_text())
    assert manifest["collector"] == collector.collector
    assert manifest["source_domain"] == f"ebpf-{collector.collector}"
    assert manifest["source_version"]
    assert manifest["receiver_ports"] == {"a": 4318, "b": 4320, "native": 4319}
    assert manifest["raw_capture"] is True
    assert manifest["operational_readiness_only"] is True
    assert manifest["application_coverage_proven"] is False
    assert manifest["closed_checkpoint"] is False
    assert manifest["resource_envelope"]["collector_hard_cap"] is None
    assert set(manifest["configs"]) == {"a", "b"}
    assert all(len(value["sha256"]) == 64 for value in manifest["configs"].values())
    assert set(node for node, _, _ in ctx.puts) == {"a", "b"}
    assert all("--memory" not in command and "--cpus" not in command
               for command in manifest["commands"].values())


def test_coroot_is_local_trace_only_keyless_and_sampling_one(tmp_path: Path) -> None:
    collector = CorootCollectorsV5(Context(tmp_path))
    path, remote = collector._write_config("a", 4318)
    config = json.loads(path.read_text())
    assert collector.image == COROOT_IMAGE
    assert config["TRACES_ENDPOINT"] == "http://192.168.76.1:4318/v1/traces"
    assert config["TRACES_SAMPLING"] == "1"
    assert config["MAX_SPOOL_SIZE"] == "500MB"
    assert config["DISABLE_LOG_PARSING"] == "true"
    assert config["DISABLE_PINGER"] == "true"
    for forbidden in (
        "API_KEY", "COLLECTOR_ENDPOINT", "METRICS_ENDPOINT", "LOGS_ENDPOINT", "PROFILES_ENDPOINT"
    ):
        assert forbidden not in config
    command = collector._docker_command("a", remote, 4318)
    assert "--privileged --pid=host --network=host" in command
    assert COROOT_IMAGE in command
    assert "API_KEY" not in command
    assert "--memory" not in command and "--cpus" not in command


def test_obi_config_keeps_raw_semantic_capture_and_direct_local_otlp(tmp_path: Path) -> None:
    collector = OBICollectorsV5(Context(tmp_path), semantic=True)
    path, remote = collector._write_config("b", 4320)
    config = json.loads(json.dumps(__import__("yaml").safe_load(path.read_text())))
    assert config["otel_traces_export"] == {
        "endpoint": "http://192.168.76.1:4320/v1/traces",
        "protocol": "http/protobuf",
    }
    assert config["ebpf"]["context_propagation"] == "all"
    assert config["ebpf"]["buffer_sizes"]["http"] == 16384
    patterns = config["ebpf"]["payload_extraction"]["http"]["enrichment"]["rules"][0]["match"]["patterns"]
    assert "x-experiment-request-id" in patterns
    command = collector._docker_command("b", remote, 4320)
    assert "OTEL_EBPF_CONFIG_PATH=/config.yaml" in command
    assert "--memory" not in command and "--cpus" not in command


def _write_record(collector, node: str, *, coroot: bool) -> None:
    raw_dir = collector.root / f"{node}.raw" / "capture"
    raw_dir.mkdir(parents=True)
    (raw_dir / "body.json").write_text("{}")
    marker = "collector-control-v5-marker"
    attrs = (
        [
            {"key": "service.name", "value": {"stringValue": "control"}},
            {"key": "container.id", "value": {"stringValue": "container"}},
        ]
        if coroot
        else [
            {"key": "telemetry.distro.name", "value": {"stringValue": "opentelemetry-ebpf-instrumentation"}},
            {"key": "telemetry.distro.version", "value": {"stringValue": "v0.15.2"}},
            {"key": "otel.scope.name", "value": {"stringValue": "go.opentelemetry.io/obi"}},
            {"key": "container.name", "value": {"stringValue": "study-ebpf-control-client-a"}},
        ]
    )
    record = {
        "source": f"ebpf-{collector.collector}:{node}",
        "raw_ref": f"{node}.raw/capture/body.json",
        "raw_sha256": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "payload": {"resourceSpans": [{
            "resource": {"attributes": attrs},
            "scopeSpans": [{
                "scope": {"name": "coroot-node-agent"} if coroot else {},
                "spans": [{"name": f"GET /{marker}", "attributes": []}],
            }],
        }]},
    }
    (collector.root / f"{node}.jsonl").write_text(json.dumps(record) + "\n")


@pytest.mark.parametrize(
    ("collector_type", "coroot"),
    [(OBICollectorsV5, False), (CorootCollectorsV5, True)],
)
def test_positive_control_requires_raw_marker_and_collector_origin(
    tmp_path: Path, collector_type, coroot
) -> None:
    collector = collector_type(Context(tmp_path))
    _write_record(collector, "a", coroot=coroot)
    proof = collector._control_proof("a", "collector-control-v5-marker")
    assert proof["proven"] is True
    assert proof["reason"] == "raw_collector_record"
    assert proof["raw_ref"] == "a.raw/capture/body.json"

    row = json.loads((collector.root / "a.jsonl").read_text())
    row["source"] = "ebpf-other:a"
    (collector.root / "a.jsonl").write_text(json.dumps(row) + "\n")
    assert collector._control_proof("a", "collector-control-v5-marker")["proven"] is False


def test_resource_sampler_unavailability_is_explicit(tmp_path: Path) -> None:
    ctx = Context(tmp_path)
    ctx.results["docker stats"] = Result(stderr="stats unavailable", returncode=1)
    collector = OBICollectorsV5(ctx)
    collector._retain_node_evidence("a", "sample")
    evidence = json.loads((collector.root / "sample-a-evidence.json").read_text())
    assert evidence["stats"]["available"] is False
    assert evidence["stats"]["returncode"] == 1
    assert evidence["logs"]["available"] is True


def test_final_drain_retains_clean_shutdown_closed_bytes_and_honest_flush_bound(
    tmp_path: Path, monkeypatch
) -> None:
    ctx = Context(tmp_path)
    ctx.results["date +%s"] = Result("100")
    ctx.results["docker inspect"] = Result(json.dumps([{
        "RestartCount": 0,
        "State": {
            "Running": False,
            "ExitCode": 0,
            "OOMKilled": False,
            "Error": "",
            "FinishedAt": "2026-10-29T12:00:00Z",
        },
    }]))
    ctx.results["docker logs"] = Result("received terminated, shutting down\ncleanup completed\n")
    ctx.results["docker events"] = Result(json.dumps({
        "Action": "kill", "Actor": {"Attributes": {"signal": "15"}}
    }) + "\n")
    collector = CorootCollectorsV5(ctx)
    monkeypatch.setattr(collector, "_retain_node_evidence", lambda node, stage: None)
    monkeypatch.setattr(
        collector,
        "_receiver_barrier",
        lambda node: {"accepted": True, "scope": "receiver write only"},
    )
    monkeypatch.setattr(
        collector,
        "_close_receivers",
        lambda: {node: {
            "technical_valid": True,
            "saved_bytes_valid": True,
            "parent_hash_verification": True,
            "in_flight_handlers_joined": True,
        } for node in ("a", "b", "native")},
    )
    evidence = collector.final_drain()
    evidence = json.loads((collector.root / "drain-evidence.json").read_text())
    assert evidence["technical_valid"] is True
    assert evidence["technical_complete"] is True
    assert evidence["accepted_receiver_bytes_closed_and_hashed"] is True
    assert evidence["collector_exporter_flush"]["status"] == "unsupported_by_pinned_source"
    assert evidence["kernel_or_producer_loss_absent"] is None
    assert all(value["accepted"] for value in evidence["receiver_acceptance_barriers"].values())
    assert set(evidence["termination"]) == {"a", "b"}
    checkpoint = json.loads((collector.root / "collector.json").read_text())
    assert checkpoint["lifecycle"] == "closed"
    assert checkpoint["closed_checkpoint"] is True
    assert checkpoint["retained_file_hashes"]["drain-evidence.json"]["sha256"]
    collector.snapshot()
    final_snapshot = json.loads((collector.root / "final-snapshot.json").read_text())
    assert final_snapshot["technical_complete"] is True
    assert final_snapshot["accepted_receiver_bytes_closed_and_hashed"] is True
    assert "pre-receiver exporter loss" in final_snapshot["scope"]
    checkpoint = json.loads((collector.root / "collector.json").read_text())
    assert checkpoint["retained_file_hashes"]["final-snapshot.json"]["sha256"]


def test_termination_rejects_exit_137_oom_sigkill_and_missing_success(tmp_path: Path) -> None:
    collector = OBICollectorsV5(Context(tmp_path))
    inspect = Result(json.dumps([{
        "RestartCount": 1,
        "State": {
            "Running": False,
            "ExitCode": 137,
            "OOMKilled": True,
            "Error": "forced",
            "FinishedAt": "2026-10-29T12:00:00Z",
        },
    }]))
    events = Result(json.dumps({
        "Action": "kill", "Actor": {"Attributes": {"signal": "9"}}
    }) + "\n")
    result = collector._termination_evidence(
        stop=Result("study-obi-v5"), inspect=inspect, events=events, logs=""
    )
    assert result["technical_valid"] is False
    assert "unexpected_exit_code:137" in result["technical_invalid_reasons"]
    assert "oom_killed" in result["technical_invalid_reasons"]
    assert "sigkill_observed" in result["technical_invalid_reasons"]
    assert "obi_successful_exit_marker_missing" in result["technical_invalid_reasons"]


def test_obi_clean_shutdown_claim_is_limited_to_source_queue_path(tmp_path: Path) -> None:
    collector = OBICollectorsV5(Context(tmp_path))
    inspect = Result(json.dumps([{
        "RestartCount": 0,
        "State": {
            "Running": False,
            "ExitCode": 0,
            "OOMKilled": False,
            "Error": "",
            "FinishedAt": "2026-10-29T12:00:00Z",
        },
    }]))
    result = collector._termination_evidence(
        stop=Result("study-obi-v5"),
        inspect=inspect,
        events=Result(json.dumps({
            "Action": "kill", "Actor": {"Attributes": {"signal": "15"}}
        }) + "\n"),
        logs="OpenTelemetry eBPF Instrumentation successfully exiting\n",
    )
    assert result["technical_valid"] is True
    claim = collector._exporter_flush_claim({"a": result, "b": result})
    assert claim["status"] == "graceful_source_path_observed"
    assert claim["zero_pre_queue_or_kernel_loss_proven"] is False


def test_parent_rehash_detects_post_checkpoint_raw_body_change(tmp_path: Path) -> None:
    collector = OBICollectorsV5(Context(tmp_path))
    output = collector.root / "a.jsonl"
    output.write_text('{"complete":true}\n', encoding="utf-8")
    capture = _capture_wire_body(
        output,
        b'{"resourceSpans":[]}',
        source="ebpf-obi:a",
        node="a",
        received_ns=1,
        headers={"Content-Type": "application/json"},
    )
    checkpoint = {
        "wrapper": _file(output),
        "errors": _file(output.with_suffix(".errors.jsonl")),
        "raw_capture": _raw_capture_audit(output),
    }
    assert collector._verify_receiver_checkpoint("a", checkpoint) is True
    (collector.root / capture["raw_ref"]).write_bytes(b"changed")
    assert collector._verify_receiver_checkpoint("a", checkpoint) is False


def test_control_image_is_existing_exact_pin() -> None:
    assert CONTROL_IMAGE.startswith("haproxy:3.0-alpine@sha256:")
    assert len(CONTROL_IMAGE.rsplit(":", 1)[1]) == 64


def test_control_server_uses_haproxy_not_missing_busybox_httpd() -> None:
    script = _control_server_script(18081)
    assert "haproxy -c -f /tmp/control-haproxy.cfg" in script
    assert "exec haproxy -W -db -f /tmp/control-haproxy.cfg" in script
    assert "bind 0.0.0.0:18081" in script
    assert "busybox httpd" not in script
    assert "collector-control-marker" in _control_request_script(
        18081, "collector-control-marker", persistent=False
    )


def test_control_failure_retains_attempt_diagnostics_and_cleans_both_nodes(
    tmp_path: Path, monkeypatch
) -> None:
    from ebpf_discovery import collectors_v5 as module

    class FailureContext(Context):
        def node_exec(self, node, command, **kwargs):
            self.calls.append((node, command, kwargs))
            if command.startswith("docker inspect study-ebpf-control-server-"):
                return Result(json.dumps([{"State": {"Running": True}}]))
            if "docker exec study-ebpf-control-server-" in command:
                return Result("Configuration file is valid\n")
            if "-probe" in command:
                raise RuntimeError("request transport failed")
            if command.startswith("docker logs"):
                return Result("retained server log\n")
            if command.startswith("docker image inspect"):
                return Result('[{"Id":"sha256:pinned"}]')
            return Result("ok")

    ticks = iter((0.0, 0.5, 2.0))
    monkeypatch.setattr(module, "CONTROL_READY_TIMEOUT_SECONDS", 1.0)
    monkeypatch.setattr(module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    ctx = FailureContext(tmp_path)
    collector = OBICollectorsV5(ctx)
    with pytest.raises(RuntimeError, match="HTTP readiness failed on a"):
        collector.positive_control()

    evidence = json.loads(
        (collector.root / "technical-positive-control.json").read_text(encoding="utf-8")
    )
    assert evidence["technical_failure"] == "technical control HTTP readiness failed on a"
    assert len(evidence["nodes"]["a"]["request_attempts"]) == 1
    attempt = evidence["nodes"]["a"]["request_attempts"][0]
    assert attempt["request"]["returncode"] == 255
    assert attempt["request"]["stderr"] == "RuntimeError: request transport failed"
    assert evidence["nodes"]["a"]["server_inspect"]["sha256"]
    assert evidence["nodes"]["a"]["server_logs"]["sha256"]
    cleanup = [command for _, command, _ in ctx.calls if command.startswith("docker rm -f")]
    assert any("control-client-a" in command and "control-server-a" in command for command in cleanup)
    assert any("control-client-b" in command and "control-server-b" in command for command in cleanup)
    assert evidence["cleanup_verified"] is False
    assert evidence["technical_failure"] == "technical control HTTP readiness failed on a"


def test_successful_origin_still_fails_if_control_container_remains(
    tmp_path: Path, monkeypatch
) -> None:
    class RemnantContext(Context):
        def node_exec(self, node, command, **kwargs):
            self.calls.append((node, command, kwargs))
            if command.startswith("docker inspect study-ebpf-control-server-"):
                return Result(json.dumps([{"State": {"Running": True}}]))
            if command.startswith("docker inspect study-ebpf-control-client-"):
                return Result(json.dumps([{"State": {"Running": True}}]))
            if "docker exec study-ebpf-control-server-" in command:
                return Result("Configuration file is valid\n")
            if "-probe" in command and command.startswith("docker run"):
                return Result("ok\n")
            if command.startswith("docker image inspect"):
                return Result('[{"Id":"sha256:pinned"}]')
            if command.startswith("docker ps -a"):
                if node == "a" and "control-client-a-probe" in command:
                    return Result("study-ebpf-control-client-a-probe\n")
                return Result("")
            return Result("ok")

    ctx = RemnantContext(tmp_path)
    collector = OBICollectorsV5(ctx)
    monkeypatch.setattr(
        collector, "_control_proof", lambda node, marker: {
            "proven": True, "reason": "raw_collector_record"
        }
    )
    with pytest.raises(RuntimeError, match="cleanup absence verification failed"):
        collector.positive_control(timeout=1)
    evidence = json.loads(
        (collector.root / "technical-positive-control.json").read_text(encoding="utf-8")
    )
    assert evidence["selected_ebpf_origin_proven"] is True
    assert evidence["cleanup_verified"] is False
    assert evidence["technical_failure"] == (
        "technical control cleanup absence verification failed"
    )
    assert evidence["cleanup_failures"] == [{
        "container": "study-ebpf-control-client-a-probe",
        "node": "a",
        "observed_names": ["study-ebpf-control-client-a-probe"],
        "returncode": 0,
        "role": "probe",
    }]


@pytest.mark.skipif(
    os.environ.get("RUN_DOCKER_CONTROL_FIXTURE") != "1",
    reason="technical Docker fixture runs in Actions only",
)
def test_pinned_haproxy_control_fixture_executes() -> None:
    suffix = uuid.uuid4().hex[:10]
    server = f"study-control-fixture-{suffix}"
    client = f"study-control-client-{suffix}"
    port = 18081
    subprocess.run(["docker", "pull", CONTROL_IMAGE], check=True)
    try:
        subprocess.run(
            [
                "docker", "run", "-d", "--name", server, "--network", "host",
                "--entrypoint", "/bin/sh", CONTROL_IMAGE, "-ec", _control_server_script(port),
            ],
            check=True,
        )
        deadline = time.monotonic() + 30
        last = None
        while time.monotonic() < deadline:
            inspect = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Running}}", server],
                capture_output=True, text=True, check=False,
            )
            if inspect.returncode == 0 and inspect.stdout.strip() == "true":
                config = subprocess.run(
                    ["docker", "exec", server, "haproxy", "-c", "-f", "/tmp/control-haproxy.cfg"],
                    capture_output=True, text=True, check=False,
                )
                if config.returncode == 0:
                    last = subprocess.run(
                        [
                            "docker", "run", "--rm", "--network", "host",
                            "--entrypoint", "/bin/sh", CONTROL_IMAGE, "-ec",
                            _control_request_script(port, "fixture-marker", persistent=False),
                        ],
                        capture_output=True, text=True, check=False,
                    )
                    if last.returncode == 0 and last.stdout.strip() == "ok":
                        break
            time.sleep(0.25)
        assert last is not None
        assert last.returncode == 0, last.stderr
        assert last.stdout.strip() == "ok"
        subprocess.run(
            [
                "docker", "run", "-d", "--name", client, "--network", "host",
                "--entrypoint", "/bin/sh", CONTROL_IMAGE, "-ec",
                _control_request_script(port, "fixture-marker", persistent=True),
            ],
            check=True,
        )
        persistent = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Running}}", client],
            capture_output=True, text=True, check=False,
        )
        assert persistent.returncode == 0
        assert persistent.stdout.strip() == "true"
    finally:
        subprocess.run(["docker", "logs", server], check=False)
        subprocess.run(["docker", "logs", client], check=False)
        subprocess.run(["docker", "rm", "-f", client, server], check=False)
