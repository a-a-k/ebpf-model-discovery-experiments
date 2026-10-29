from __future__ import annotations

import json
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
)


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
    for blocked in ("deepflow", "newrelic", "unknown"):
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


def test_close_retains_termination_barrier_and_unproven_flush(
    tmp_path: Path, monkeypatch
) -> None:
    ctx = Context(tmp_path)
    ctx.results["docker inspect --format"] = Result('{"Running":false,"ExitCode":0}')
    collector = CorootCollectorsV5(ctx)
    monkeypatch.setattr(collector, "_retain_node_evidence", lambda node, stage: None)
    monkeypatch.setattr(
        collector,
        "_receiver_barrier",
        lambda node: {"accepted": True, "scope": "receiver write only"},
    )
    collector.close()
    evidence = json.loads((collector.root / "drain-evidence.json").read_text())
    assert evidence["collector_flush_proven"] is False
    assert "not an exporter flush" in evidence["exporter_loss"]
    assert all(value["accepted"] for value in evidence["receiver_write_barriers"].values())
    assert set(evidence["termination"]) == {"a", "b"}
    checkpoint = json.loads((collector.root / "collector.json").read_text())
    assert checkpoint["lifecycle"] == "closed"
    assert checkpoint["closed_checkpoint"] is True
    assert checkpoint["retained_file_hashes"]["drain-evidence.json"]["sha256"]


def test_control_image_is_existing_exact_pin() -> None:
    assert CONTROL_IMAGE.startswith("haproxy:3.0-alpine@sha256:")
    assert len(CONTROL_IMAGE.rsplit(":", 1)[1]) == 64
