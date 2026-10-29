from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
import yaml

from ebpf_discovery.collectors_v5 import CollectorsV5
from ebpf_discovery.deepflow_v5 import (
    DEEPFLOW_CONTAINER,
    DEEPFLOW_EBPF_READY_MARKER,
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
        if command == "cat /proc/meminfo":
            total = {"a": 2_097_153, "b": 3_145_728}[node]
            return Result(f"MemTotal:       {total} kB\nMemFree:          123 kB\n")
        if command == "nproc":
            return Result({"a": "2\n", "b": "4\n"}[node])
        if "docker image inspect" in command:
            return Result('[{"Id":"sha256:pinned"}]')
        if "json .HostConfig" in command:
            return Result(json.dumps({
                "Memory": 0, "NanoCpus": 0, "CpuQuota": 0, "CpuPeriod": 0,
                "CpusetCpus": "",
            }) + "\n")
        if ".State.Pid" in command:
            return Result("4242\n")
        if "cgroup_file_begin" in command:
            return Result(
                "host_pid=4242\ncgroup_file_begin\n"
                "0::/system.slice/docker-test.scope\ncgroup_file_end\n"
                "visit|/system.slice/docker-test.scope|directory\n"
                "limit|/system.slice/docker-test.scope|memory.max|max\n"
                "limit|/system.slice/docker-test.scope|cpu.max|max 100000\n"
                "visit|/system.slice|directory\n"
                "limit|/system.slice|memory.max|max\n"
                "limit|/system.slice|cpu.max|max 100000\n"
                "visit|/|directory\n"
                "control|/|memory.max|absent\ncontrol|/|cpu.max|absent\n"
            )
        if "memory.max=" in command and "cpu.max=" in command:
            return Result(
                "memory.max=max\ncpu.max=max 100000\nnproc="
                + {"a": "2\n", "b": "4\n"}[node]
            )
        if "docker inspect" in command and "--format" in command:
            return Result("true\n")
        if "grep -h -F" in command:
            return Result("ebpf collector started\n")
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
    config = _config(max_memory_mib=2048, max_millicpus=2000)
    assert config["global"]["standalone_mode"]["max_data_file_size"] == MAX_DATA_FILE_SIZE_MIB
    assert MAX_DATA_FILE_SIZE_BYTES == 1 << 40
    assert config["processors"]["request_log"]["tag_extraction"]["tracing_tag"]["x_request_id"] == [
        "x-experiment-request-id"
    ]
    assert config["inputs"]["ebpf"]["profile"]["on_cpu"]["disabled"] is True
    assert config["global"]["limits"] == {
        "max_memory": 2048, "max_millicpus": 2000,
    }
    assert config["global"]["limits"]["max_memory"] << 20 == 2 * (1 << 30)


def test_config_rejects_zero_resource_envelopes() -> None:
    with pytest.raises(ValueError, match="positive guest envelopes"):
        _config(max_memory_mib=0, max_millicpus=1000)
    with pytest.raises(ValueError, match="positive guest envelopes"):
        _config(max_memory_mib=1024, max_millicpus=0)


def test_readiness_uses_pinned_success_marker_not_initialization_marker(
        tmp_path: Path, monkeypatch) -> None:
    ctx = Context(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    monkeypatch.setattr("ebpf_discovery.deepflow_v5.time.sleep", lambda _: None)

    collector._wait_container_readiness()

    commands = [command for _, command, _ in ctx.calls if "grep -h -F" in command]
    assert len(commands) == 4
    assert all(DEEPFLOW_EBPF_READY_MARKER in command for command in commands)
    assert all("Start (.* )?dispatcher" not in command for command in commands)
    assert json.loads((collector.root / "readiness.json").read_text()) == {
        "ebpf_origin_proven": False,
        "operational_only": True,
        "ready": True,
    }


def test_readiness_does_not_accept_collector_initialization_line(
        tmp_path: Path, monkeypatch) -> None:
    class InitializingContext(Context):
        def node_exec(self, node, command, **kwargs):
            result = super().node_exec(node, command, **kwargs)
            if "grep -h -F" in command:
                return Result("ebpf collector init... uprobe_meltdown: false\n")
            return result

    ctx = InitializingContext(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    clock = iter((0.0, 1.0, 91.0))
    monkeypatch.setattr("ebpf_discovery.deepflow_v5.time.monotonic", lambda: next(clock))
    monkeypatch.setattr("ebpf_discovery.deepflow_v5.time.sleep", lambda _: None)

    with pytest.raises(RuntimeError, match="readiness not established"):
        collector._wait_container_readiness()

    assert json.loads((collector.root / "readiness.json").read_text())["ready"] is False


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
    assert set(manifest["runtime_clock_relations"]) == {"a", "b"}
    for node in ("a", "b"):
        proof = manifest["runtime_clock_relations"][node]
        relation_path = collector.root.parent / proof["evidence"]["locator"]
        relation = json.loads(relation_path.read_text())
        assert relation["boot_id"] == f"boot-{node}"
        assert relation["event_serialization"]["quantization_ns"] == 1000
        assert relation["clock_step_limitation_retained"] is True
        assert relation["empirical_endpoint_offsets_used_as_hard_bound"] is False
        assert proof["evidence"]["sha256"] == hashlib.sha256(
            relation_path.read_bytes()).hexdigest()
    assert set(manifest["remote_roots"]) == {"a", "b"}
    assert set(manifest["configs"]) == {"a", "b"}
    assert all("--memory" not in command and "--cpus" not in command
               for command in manifest["commands"].values())
    assert all("--log-opt" not in command for command in manifest["commands"].values())
    assert all("--privileged --pid=host --network=host" in command
               for command in manifest["commands"].values())
    assert [command for _, command, _ in ctx.calls
            if command == "sudo readlink /proc/1/ns/pid"] == [
                "sudo readlink /proc/1/ns/pid", "sudo readlink /proc/1/ns/pid"]
    assert "common post-capture projection" in manifest["service_identity_enrichment"]
    questions = json.loads((collector.root / "deepflow-integration-questions.json").read_text())
    assert questions["service_identity"]["status"] == (
        "available_via_common_verified_runtime_identity_projection")
    assert len(ctx.puts) == 4  # config and immutable snapshot helper on each guest
    configs = {
        node: yaml.safe_load(next(source for put_node, source, _ in ctx.puts
                                  if put_node == node and source.suffix == ".yaml").read_text())
        for node in ("a", "b")
    }
    assert configs["a"]["global"]["limits"] == {
        "max_memory": 2049, "max_millicpus": 2000,
    }
    assert configs["b"]["global"]["limits"] == {
        "max_memory": 3072, "max_millicpus": 4000,
    }
    assert configs["a"] != configs["b"]
    for node in ("a", "b"):
        inventory = json.loads((collector.root / f"resource-inventory-{node}.json").read_text())
        assert inventory["effective_container_constraints"][
            "verified_no_explicit_docker_hard_limit_below_guest_envelope"] is True
        assert inventory["effective_container_constraints"]["hierarchy_complete_to_root"] is True
        assert inventory["effective_container_constraints"][
            "root_visit_is_traversal_evidence_not_unlimited_limit"] is True
        assert inventory["effective_container_constraints"][
            "cgroup_missing_or_unreadable_controls"] == [
                {"path": "/", "kind": "memory.max", "status": "absent"},
                {"path": "/", "kind": "cpu.max", "status": "absent"},
            ]
        assert inventory["effective_container_constraints"]["host_pid"] == 4242
        assert inventory["commands"]["meminfo"]["stdout"].startswith("MemTotal:")
        assert inventory["commands"]["cpu_count"]["command"] == "nproc"
        assert configs[node]["global"]["limits"]["max_memory"] << 20 == (
            inventory["parsed"]["max_memory_bytes"])


def test_resource_policy_rejects_extra_lower_docker_or_leaf_cgroup_limit(
        tmp_path: Path) -> None:
    class LimitedContext(Context):
        def __init__(self, root: Path, limit_source: str):
            super().__init__(root)
            self.limit_source = limit_source

        def node_exec(self, node, command, **kwargs):
            if "json .HostConfig" in command and self.limit_source == "docker":
                return Result(json.dumps({
                    "Memory": 1 << 30, "NanoCpus": 0,
                    "CpuQuota": 0, "CpuPeriod": 0,
                }) + "\n")
            if "cgroup_file_begin" in command and self.limit_source == "leaf":
                return Result(
                    "host_pid=4242\ncgroup_file_begin\n"
                    "0::/system.slice/docker-test.scope\ncgroup_file_end\n"
                    "visit|/system.slice/docker-test.scope|directory\n"
                    f"limit|/system.slice/docker-test.scope|memory.max|{1 << 30}\n"
                    "limit|/system.slice/docker-test.scope|cpu.max|max 100000\n"
                    "visit|/system.slice|directory\n"
                    "limit|/system.slice|memory.max|max\n"
                    "limit|/system.slice|cpu.max|max 100000\n"
                    "visit|/|directory\n"
                    "control|/|memory.max|absent\ncontrol|/|cpu.max|absent\n"
                )
            return super().node_exec(node, command, **kwargs)

    for source, error in (
        ("docker", "Docker memory limit is below guest envelope"),
        ("leaf", "collector-specific memory.max is below guest envelope"),
    ):
        root = tmp_path / source
        ctx = LimitedContext(root, source)
        collector = DeepFlowCollectorsV5(ctx)
        collector._guest_resource_inventory("a")
        with pytest.raises(RuntimeError, match=error):
            collector._verify_container_resource_envelope("a")


def test_resource_policy_accepts_leaf_equal_to_shared_parent_below_root(
        tmp_path: Path) -> None:
    shared_memory = 1 << 30

    class SharedLimitContext(Context):
        def node_exec(self, node, command, **kwargs):
            if "cgroup_file_begin" in command:
                return Result(
                    "host_pid=4242\ncgroup_file_begin\n"
                    "0::/system.slice/docker-test.scope\ncgroup_file_end\n"
                    "visit|/system.slice/docker-test.scope|directory\n"
                    f"limit|/system.slice/docker-test.scope|memory.max|{shared_memory}\n"
                    "limit|/system.slice/docker-test.scope|cpu.max|max 100000\n"
                    "visit|/system.slice|directory\n"
                    f"limit|/system.slice|memory.max|{shared_memory}\n"
                    "limit|/system.slice|cpu.max|max 100000\n"
                    "visit|/|directory\n"
                    "control|/|memory.max|absent\ncontrol|/|cpu.max|absent\n"
                )
            if "memory.max=" in command and "cpu.max=" in command:
                return Result(
                    f"memory.max={shared_memory}\ncpu.max=max 100000\nnproc=2\n"
                )
            return super().node_exec(node, command, **kwargs)

    ctx = SharedLimitContext(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    collector._guest_resource_inventory("a")
    collector._verify_container_resource_envelope("a")

    constraints = collector.resource_inventory["a"]["effective_container_constraints"]
    assert constraints["effective_shared_ancestor_hard_limit"]["memory.max"] == shared_memory
    assert constraints["shared_hard_limit_below_declared_guest_envelope"]["memory.max"] is True
    assert constraints["verification_complete"] is True


def test_resource_policy_still_rejects_hierarchy_without_root_visit(tmp_path: Path) -> None:
    class TruncatedHierarchyContext(Context):
        def node_exec(self, node, command, **kwargs):
            result = super().node_exec(node, command, **kwargs)
            if "cgroup_file_begin" in command:
                result.stdout = "\n".join(
                    line for line in result.stdout.splitlines()
                    if not line.startswith(("visit|/|", "control|/|"))
                ) + "\n"
            return result

    ctx = TruncatedHierarchyContext(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    collector._guest_resource_inventory("a")
    with pytest.raises(RuntimeError, match="incomplete container cgroup hierarchy"):
        collector._verify_container_resource_envelope("a")


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ("control", "missing non-root cgroup hard-limit evidence"),
        ("directory", "unreadable container cgroup hierarchy directory"),
    ],
)
def test_resource_policy_rejects_missing_nonroot_hard_limit_evidence(
        tmp_path: Path, mutation: str, error: str) -> None:
    class BrokenHierarchyContext(Context):
        def node_exec(self, node, command, **kwargs):
            result = super().node_exec(node, command, **kwargs)
            if "cgroup_file_begin" not in command:
                return result
            if mutation == "control":
                result.stdout = result.stdout.replace(
                    "limit|/system.slice|memory.max|max\n",
                    "control|/system.slice|memory.max|unreadable\n",
                )
            else:
                result.stdout = result.stdout.replace(
                    "visit|/system.slice|directory\n",
                    "visit|/system.slice|missing\n",
                )
            return result

    ctx = BrokenHierarchyContext(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    collector._guest_resource_inventory("a")
    with pytest.raises(RuntimeError, match=error):
        collector._verify_container_resource_envelope("a")

    retained = json.loads((collector.root / "resource-inventory-a.json").read_text())
    constraints = retained["effective_container_constraints"]
    assert constraints["verification_complete"] is False
    assert constraints["cgroup_directory_visits_leaf_to_root"]
    if mutation == "control":
        assert {"path": "/system.slice", "kind": "memory.max", "status": "unreadable"} in (
            constraints["cgroup_missing_or_unreadable_controls"])


def test_protected_pid_namespace_read_uses_sudo_and_preserves_startup_failure(
        tmp_path: Path, monkeypatch) -> None:
    class ProtectedProcContext(Context):
        def node_exec(self, node, command, **kwargs):
            if command == "readlink /proc/1/ns/pid":
                raise AssertionError("unprivileged protected-proc read attempted")
            if command == "sudo readlink /proc/1/ns/pid":
                self.calls.append((node, command, kwargs))
                raise RuntimeError("sudo readlink failed: protected proc unavailable")
            return super().node_exec(node, command, **kwargs)

    ctx = ProtectedProcContext(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    monkeypatch.setattr(collector, "_start_receivers", lambda: None)
    with pytest.raises(RuntimeError, match="protected proc unavailable"):
        collector.start()
    collector.close()  # defensive campaign cleanup must not attempt a final snapshot/drain

    failure = json.loads((collector.root / "startup-failure.json").read_text())
    assert failure["original_error"]["message"] == (
        "sudo readlink failed: protected proc unavailable")
    assert failure["cleanup"]["drain_attempted"] is False
    assert failure["cleanup"]["collector_closed_checkpoint_created"] is False
    assert failure["collector_closed_checkpoint"] is False
    assert failure["accepted_receiver_bytes_closed_and_hashed"] is False
    assert not (collector.root / "drain-evidence.json").exists()
    assert not (collector.root / "final-snapshot.json").exists()
    assert not any("deepflow_snapshot_v5.py" in command for _, command, _ in ctx.calls)


def test_late_startup_failure_retains_diagnostics_and_raw_prefix_before_removal(
        tmp_path: Path, monkeypatch) -> None:
    class LateFailureContext(Context):
        def node_exec(self, node, command, **kwargs):
            if command == f"docker logs {DEEPFLOW_CONTAINER}":
                self.calls.append((node, command, kwargs))
                return Result("sole startup error: dispatcher did not stabilize\n")
            if command == f"docker inspect {DEEPFLOW_CONTAINER}":
                self.calls.append((node, command, kwargs))
                return Result('[{"State":{"Running":true}}]\n')
            return super().node_exec(node, command, **kwargs)

    ctx = LateFailureContext(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    monkeypatch.setattr(collector, "_start_receivers", lambda: None)

    def late_failure():
        for node in ("a", "b"):
            source = tmp_path / f"remote-{node}-startup-failure"
            source.mkdir()
            complete = json.dumps(_row("/late"), separators=(",", ":")).encode() + b"\n"
            pending = b'{"pending":'
            raw = source / "l7_flow_log"
            agent_log = source / "deepflow-agent.log"
            raw.write_bytes(complete + pending)
            agent_log.write_bytes(b"sole raw agent file error\n")
            files = []
            for path, prefix in ((raw, len(complete)), (agent_log, agent_log.stat().st_size)):
                body = path.read_bytes()
                files.append({
                    "source_name": path.name, "snapshot_name": path.name,
                    "source_size_before": len(body), "source_size_after": len(body),
                    "source_changed_during_snapshot": False,
                    "copied_bytes": len(body),
                    "copied_sha256": __import__("hashlib").sha256(body).hexdigest(),
                    "complete_prefix_bytes": prefix,
                    "complete_prefix_sha256": __import__("hashlib").sha256(
                        body[:prefix]).hexdigest(),
                    "pending_tail_bytes_at_read": len(body) - prefix,
                    "full_file_retained": True,
                })
            manifest = {
                "schema": "deepflow-standalone-snapshot-v5", "mode": "failure",
                "files": files, "l7_rotation_observed": False,
                "rotation_observed": False, "complete_prefix_only": False,
                "startup_incomplete": True, "producer_closed": False,
                "closed_checkpoint": False,
            }
            snapshot_path = source / "snapshot.json"
            snapshot_path.write_text(json.dumps(manifest), encoding="utf-8")
            remote = collector.remote_roots[node] + "/snapshots/startup-failure"
            ctx.remote_files[(node, remote + "/snapshot.json")] = snapshot_path
            ctx.remote_files[(node, remote + "/l7_flow_log")] = raw
            ctx.remote_files[(node, remote + "/deepflow-agent.log")] = agent_log
        raise RuntimeError("late readiness failure must remain primary")

    monkeypatch.setattr(collector, "_wait_container_readiness", late_failure)
    with pytest.raises(RuntimeError, match="late readiness failure must remain primary"):
        collector.start()
    collector.close()

    failure = json.loads((collector.root / "startup-failure.json").read_text())
    assert failure["original_error"]["message"] == "late readiness failure must remain primary"
    assert failure["cleanup"]["drain_attempted"] is False
    for node in ("a", "b"):
        diagnostics = failure["cleanup"]["diagnostics_before_removal"][node]
        assert diagnostics["inspect"]["available"] is True
        assert diagnostics["logs"]["available"] is True
        log_path = collector.root / diagnostics["logs"]["path"]
        assert log_path.read_text() == "sole startup error: dispatcher did not stabilize\n"
        assert diagnostics["logs"]["sha256"] == __import__("hashlib").sha256(
            log_path.read_bytes()).hexdigest()
        prefix = failure["cleanup"]["available_raw_prefixes_before_removal"][node]
        assert prefix["retained"] is True
        assert prefix["startup_incomplete"] is True
        assert prefix["producer_closed"] is False
        retained_root = collector.root / prefix["path"]
        assert (retained_root / "l7_flow_log").read_bytes().endswith(b'{"pending":')
        assert (retained_root / "deepflow-agent.log").read_bytes() == (
            b"sole raw agent file error\n")
        assert prefix["normalization_performed"] is False
        commands = [command for call_node, command, _ in ctx.calls if call_node == node]
        assert commands.index(f"docker logs {DEEPFLOW_CONTAINER}") < commands.index(
            f"docker rm -f {DEEPFLOW_CONTAINER}")
        assert next(i for i, command in enumerate(commands)
                    if "deepflow_snapshot_v5.py" in command) < commands.index(
                        f"docker rm -f {DEEPFLOW_CONTAINER}")
    assert not (collector.root / "drain-evidence.json").exists()
    assert not (collector.root / "final-snapshot.json").exists()


def _remote_snapshot(ctx: Context, collector: DeepFlowCollectorsV5, tmp_path: Path,
                     node: str, stage: str, rows) -> None:
    source = tmp_path / f"remote-{node}-{stage}"
    source.mkdir()
    body = b"".join(
        (row if isinstance(row, bytes) else
         json.dumps(row, separators=(",", ":")).encode()) + b"\n"
        for row in rows
    )
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


def test_deepflow_raw_control_proof_uses_retained_ebpf_record(tmp_path: Path) -> None:
    ctx = Context(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    collector.remote_roots = {"a": "/remote/a", "b": "/remote/b"}
    marker = "deepflow-control-marker"
    _remote_snapshot(ctx, collector, tmp_path, "a", "001-control", [_row(f"/{marker}")])
    _remote_snapshot(ctx, collector, tmp_path, "b", "001-control", [_row("/other")])
    capture = collector._capture_all("control")
    assert capture["technical_valid"] is True
    proof = collector._control_proof("a", marker)
    assert proof["proven"] is True
    assert proof["reason"] == "raw_deepflow_ebpf_http_record"
    assert proof["signal_source"] == "EBPF"
    assert proof["raw_sha256"]


def test_deepflow_raw_control_proof_accepts_pinned_flattened_session_row(
        tmp_path: Path) -> None:
    ctx = Context(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    collector.remote_roots = {"a": "/remote/a", "b": "/remote/b"}
    fixture = (
        Path(__file__).parent / "fixtures" / "deepflow-v7.2.3-http-session.jsonl"
    )
    raw = fixture.read_bytes().removesuffix(b"\n")
    marker = "collector-control-v5-deepflow-1793286908082095797"
    _remote_snapshot(ctx, collector, tmp_path, "a", "001-control", [raw])
    _remote_snapshot(ctx, collector, tmp_path, "b", "001-control", [_row("/other")])

    capture = collector._capture_all("control")
    proof = collector._control_proof("a", marker)

    assert capture["technical_valid"] is True
    assert proof["proven"] is True
    assert proof["reason"] == "raw_deepflow_ebpf_http_record"
    assert proof["signal_source"] == "EBPF"
    assert proof["raw_sha256"] == __import__("hashlib").sha256(raw).hexdigest()


def test_deepflow_reuses_shared_haproxy_control_lifecycle(
    tmp_path: Path, monkeypatch
) -> None:
    class ControlContext(Context):
        def node_exec(self, node, command, **kwargs):
            self.calls.append((node, command, kwargs))
            if command.startswith("docker inspect study-ebpf-control-"):
                return Result(json.dumps([{"State": {"Running": True}}]))
            if "docker exec study-ebpf-control-server-" in command:
                return Result("Configuration file is valid\n")
            if "-probe" in command and command.startswith("docker run"):
                return Result("ok\n")
            if command.startswith("docker image inspect"):
                return Result('[{"Id":"sha256:pinned"}]')
            if command.startswith("docker ps -a"):
                return Result("")
            return Result("ok\n")

    ctx = ControlContext(tmp_path)
    collector = DeepFlowCollectorsV5(ctx)
    captures = []
    monkeypatch.setattr(
        collector, "_capture_all",
        lambda label, final=False: captures.append((label, final)) or {"technical_valid": True},
    )
    monkeypatch.setattr(
        collector, "_control_proof",
        lambda node, marker: {"proven": True, "reason": "raw_deepflow_ebpf_http_record"},
    )
    evidence = collector.certify_controls(timeout=1)
    assert DeepFlowCollectorsV5.certify_controls is CollectorsV5.certify_controls
    assert captures == [("positive-control", False)]
    assert evidence["selected_ebpf_origin_proven"] is True
    assert evidence["cleanup_verified"] is True
    assert all("busybox httpd" not in command for _, command, _ in ctx.calls)
    assert any("exec haproxy -W -db" in command for _, command, _ in ctx.calls)


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
