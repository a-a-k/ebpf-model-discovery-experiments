from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from ebpf_discovery.deepflow_v5 import (
    DEEPFLOW_IMAGE,
    MAX_DATA_FILE_SIZE_BYTES,
    MAX_DATA_FILE_SIZE_MIB,
    DeepFlowCollectorsV5,
    _config,
)
from ebpf_discovery.observations import attributes


class Result:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode


class Context:
    def __init__(self, root: Path):
        self.out = root
        self.calls = []
        self.puts = []
        self.remote_files: dict[tuple[str, str], Path] = {}

    def node_put(self, node, source, destination):
        self.puts.append((node, Path(source), destination))

    def node_get(self, node, source, destination):
        shutil.copyfile(self.remote_files[(node, source)], destination)

    def node_exec(self, node, command, **kwargs):
        self.calls.append((node, command, kwargs))
        if "mktemp -d" in command:
            return Result(f"/opt/ebpf-study/deepflow-v5.{node}12345\n")
        if "df -B1" in command:
            return Result("500000000000\n")
        if "boot_id" in command:
            return Result(f"boot-{node}\n")
        if "readlink /proc/1/ns/pid" in command:
            return Result("pid:[4026531836]\n")
        if "docker image inspect" in command:
            return Result('[{"Id":"sha256:pinned"}]')
        if "docker inspect" in command and "--format" in command:
            return Result("true\n")
        if "grep -h -E" in command:
            return Result("Start eBPF dispatcher\n")
        return Result("ok\n")


def _row(path="/control"):
    return {
        "signal_source": "EBPF",
        "tap_side": "ServerProcess",
        "ebpf_type": "TracePoint",
        "l7_protocol": "Http1",
        "msg_type": "Request",
        "start_time": 10,
        "end_time": 20,
        "request_type": "GET",
        "request_resource": path,
        "x_request_id_0": "step-1",
        "process_id_1": 99,
        "process_kname_1": "server",
    }


def test_config_uses_1tib_threshold_and_exact_experiment_header() -> None:
    config = _config()
    assert config["global"]["standalone_mode"]["max_data_file_size"] == MAX_DATA_FILE_SIZE_MIB
    assert MAX_DATA_FILE_SIZE_BYTES == 1 << 40
    assert config["processors"]["request_log"]["tag_extraction"]["tracing_tag"]["x_request_id"] == [
        "x-experiment-request-id"
    ]


def test_start_uses_fresh_two_guest_directories_without_asymmetric_caps(tmp_path: Path, monkeypatch) -> None:
    ctx = Context(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    monkeypatch.setattr(collector, "_start_receivers", lambda: None)
    monkeypatch.setattr(collector, "_wait_container_readiness", lambda: None)
    collector.start()
    manifest = json.loads((collector.root / "collector.json").read_text())
    assert manifest["collector"] == "deepflow"
    assert manifest["source_version"] == "v7.2.3"
    assert manifest["image"] == DEEPFLOW_IMAGE
    assert manifest["fresh_directory_per_attempt"] is True
    assert manifest["restart_permitted"] is False
    assert manifest["rotation_threshold_above_guest_capacity"] is True
    assert set(manifest["remote_roots"]) == {"a", "b"}
    assert set(manifest["configs"]) == {"a", "b"}
    assert all("--memory" not in command and "--cpus" not in command
               for command in manifest["commands"].values())
    assert all("--log-opt" not in command for command in manifest["commands"].values())
    assert all("--privileged --pid=host --network=host" in command
               for command in manifest["commands"].values())
    assert len(ctx.puts) == 4  # config and immutable snapshot helper on each guest


def _remote_snapshot(ctx: Context, collector: DeepFlowCollectorsV5, tmp_path: Path,
                     node: str, stage: str, rows) -> None:
    source = tmp_path / f"remote-{node}-{stage}"
    source.mkdir()
    body = b"".join(json.dumps(row, separators=(",", ":")).encode() + b"\n" for row in rows)
    raw = source / "l7_flow_log"
    raw.write_bytes(body)
    manifest = {
        "schema": "deepflow-standalone-snapshot-v5",
        "mode": "prefix",
        "files": [{
            "source_name": "l7_flow_log",
            "snapshot_name": "l7_flow_log",
            "source_size_before": len(body),
            "source_size_after": len(body),
            "source_changed_during_snapshot": False,
            "copied_bytes": len(body),
            "copied_sha256": __import__("hashlib").sha256(body).hexdigest(),
            "complete_prefix_bytes": len(body),
            "complete_prefix_sha256": __import__("hashlib").sha256(body).hexdigest(),
            "pending_tail_bytes_at_read": 0,
            "full_file_retained": False,
        }],
        "l7_rotation_observed": False,
        "rotation_observed": False,
    }
    snapshot_path = source / "snapshot.json"
    snapshot_path.write_text(json.dumps(manifest))
    remote = collector.remote_roots[node] + "/snapshots/" + stage
    ctx.remote_files[(node, remote + "/snapshot.json")] = snapshot_path
    ctx.remote_files[(node, remote + "/l7_flow_log")] = raw


def test_capture_batches_flat_raw_with_portable_per_record_provenance(tmp_path: Path) -> None:
    ctx = Context(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    collector.remote_roots = {"a": "/remote/a", "b": "/remote/b"}
    collector.guest_context = {
        "a": {"boot_id": "boot-a", "pid_namespace": "pid:[1]"},
        "b": {"boot_id": "boot-b", "pid_namespace": "pid:[2]"},
    }
    _remote_snapshot(ctx, collector, tmp_path, "a", "001-training", [_row("/one"), _row("/two")])
    _remote_snapshot(ctx, collector, tmp_path, "b", "001-training", [_row("/three")])
    capture = collector._capture_all("training")
    assert capture["technical_valid"] is True
    document = json.loads((collector.root / "a.jsonl").read_text().splitlines()[0])
    spans = document["payload"]["resourceSpans"][0]["scopeSpans"][0]["spans"]
    assert len(spans) == 2
    attrs = attributes(spans[0]["attributes"])
    assert attrs["deepflow.raw.retained_file"].startswith("deepflow-raw/node-a/")
    assert attrs["deepflow.guest.boot_id"] == "boot-a"
    assert attrs["deepflow.guest.pid_namespace"] == "pid:[1]"
    assert attrs["deepflow.clock.controller_ntp_correction_enabled"] is False
    assert attrs["deepflow.event.start_time_us"] == "10"
    assert attrs["deepflow.event.end_time_us"] == "20"
    assert attrs["_runtime_identity.request_nonce"] == "step-1"
    assert attrs["_runtime_identity.boot_id"] == "boot-a"
    assert attrs["_runtime_identity.pid_namespace"] == "pid:[1]"
    assert attrs["_runtime_identity.pid_scope"] == "guest_host"
    assert attrs["_runtime_identity.locator"]["sha256"] == attrs["deepflow.raw.sha256"]
    assert not Path(attrs["deepflow.raw.retained_file"]).is_absolute()
    assert "traceId" not in spans[0] and "spanId" not in spans[0]
    resource = attributes(document["payload"]["resourceSpans"][0]["resource"]["attributes"])
    assert "service.name" not in resource
    accounting = [json.loads(line) for line in
                  (collector.root / "deepflow-codec-accounting.jsonl").read_text().splitlines()]
    assert len(accounting) == 3
    assert all(item["status"] == "normalized" for item in accounting)
    assert accounting[0]["_runtime_identity"]["request_nonce"] == "step-1"
    assert accounting[0]["_runtime_identity"]["boot_id"] == "boot-a"
    assert accounting[0]["_runtime_identity"]["pid_namespace"] == "pid:[1]"
    assert accounting[0]["_runtime_identity"]["pid_scope"] == "guest_host"
    assert accounting[0]["_runtime_identity"]["locator"]["sha256"] == (
        attrs["deepflow.raw.sha256"]
    )
    assert all({"offset", "length", "sha256", "retained_file"} <= item.keys()
               for item in accounting)


def test_clean_empty_live_capture_remains_pending_not_invalid(tmp_path: Path) -> None:
    ctx = Context(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    collector.remote_roots = {"a": "/remote/a", "b": "/remote/b"}
    for node in ("a", "b"):
        source = tmp_path / f"empty-{node}"
        source.mkdir()
        manifest = {
            "schema": "deepflow-standalone-snapshot-v5", "mode": "prefix", "files": [],
            "l7_rotation_observed": False, "rotation_observed": False,
        }
        snapshot = source / "snapshot.json"
        snapshot.write_text(json.dumps(manifest), encoding="utf-8")
        remote = collector.remote_roots[node] + "/snapshots/001-live"
        ctx.remote_files[(node, remote + "/snapshot.json")] = snapshot
    capture = collector._capture_all("live")
    assert capture["technical_valid"] is True
    assert all(item["pending_no_standalone_files"] for item in capture["nodes"].values())


def test_source_specific_write_failure_marker_is_narrow() -> None:
    collector = DeepFlowCollectorsV5(Context(Path("unused")))
    harmless = collector._assess_terminal_logs("WARN protocol parse unsupported\n")
    assert harmless["invalid_reasons"] == []
    failed = collector._assess_terminal_logs(
        "WARN l7_flow_log sender send item HTTP failed No space left on device\n"
    )
    assert failed["invalid_reasons"] == ["deepflow_standalone_write_failure"]
    assert len(failed["source_specific_failure_markers"]) == 1


def test_retained_standalone_log_write_failure_marker_is_narrow(tmp_path: Path) -> None:
    log = tmp_path / "deepflow-agent.log"
    log.write_text(
        "WARN unsupported application protocol\n"
        "WARN l7_flow_log sender send item HTTP failed No space left on device\n",
        encoding="utf-8",
    )
    failures = DeepFlowCollectorsV5._standalone_write_failures(log)
    assert len(failures) == 1
    assert failures[0]["file"] == "deepflow-agent.log"
    assert failures[0]["line"] == 2


def test_start_rejects_rotation_threshold_not_above_guest_capacity(tmp_path: Path, monkeypatch) -> None:
    ctx = Context(tmp_path)
    original = ctx.node_exec

    def execute(node, command, **kwargs):
        if "df -B1" in command:
            return Result(str(MAX_DATA_FILE_SIZE_BYTES) + "\n")
        return original(node, command, **kwargs)

    ctx.node_exec = execute
    collector = DeepFlowCollectorsV5(ctx)
    monkeypatch.setattr(collector, "_start_receivers", lambda: None)
    with pytest.raises(RuntimeError, match="does not exceed"):
        collector.start()


def test_final_drain_separates_retained_bytes_from_unproven_internal_flush(
    tmp_path: Path, monkeypatch
) -> None:
    collector = DeepFlowCollectorsV5(Context(tmp_path))
    collector.remote_roots = {"a": "/remote/a", "b": "/remote/b"}
    monkeypatch.setattr(collector, "_retain_node_evidence", lambda node, stage: None)
    monkeypatch.setattr(
        collector, "_termination_evidence",
        lambda **kwargs: {"technical_valid": True, "log_assessment": {
            "source_specific_failure_markers": [], "invalid_reasons": []
        }},
    )
    monkeypatch.setattr(collector, "_capture_all", lambda label, final=False: {
        "technical_valid": True,
        "nodes": {"a": {"stage": "001-final"}, "b": {"stage": "001-final"}},
    })
    monkeypatch.setattr(collector, "_verify_prefixes", lambda capture: {
        "a/l7_flow_log": {"unchanged": True},
        "b/l7_flow_log": {"unchanged": True},
    })
    monkeypatch.setattr(collector, "_receiver_barrier", lambda node: {"accepted": True})
    monkeypatch.setattr(collector, "_close_receivers", lambda: {
        "native": {"technical_valid": True, "parent_hash_verification": True}
    })
    evidence = collector.final_drain()
    assert evidence["technical_complete"] is True
    assert evidence["accepted_receiver_bytes_closed_and_hashed"] is True
    assert evidence["collector_exporter_flush"]["status"] == "internal_flush_loss_unproven"
    assert evidence["kernel_or_producer_loss_absent"] is None
    assert evidence["service_identity_enrichment"] == "not_performed"
