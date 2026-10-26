"""One bounded, raw-file DeepFlow fallback collector.

The common orchestrator may start this only after measured OBI coverage is absent.
It is deliberately a lifecycle helper, not a second automatic collector campaign.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import time
from pathlib import Path
from typing import Any


DEEPFLOW_VERSION = "v7.2.3"
DEEPFLOW_SOURCE_COMMIT = "9a1219fa5cf1471ba2ec8742019661567d98002e"
DEEPFLOW_IMAGE = "deepflowce/deepflow-agent:v7.2.3@sha256:5f72c0996fdb5008fdb8fd0524f427a895fc54c61690b26ba2cae648929ea95a"
CONTAINER = "ebpf-study-deepflow-fallback"
CONFIG = """# DeepFlow v7.2.3 standalone UserConfig. Unspecified fields retain upstream defaults.
global:
  communication:
    # The first standalone config notification can precede the main-loop wait.
    # Reload promptly instead of the upstream 60-second default. 10 seconds is
    # the minimum accepted by the pinned v7.2.3 configuration template.
    proactive_request_interval: 10s
  standalone_mode:
    max_data_file_size: 128
    data_file_dir: /var/log/deepflow-agent/
"""


class DeepFlowFallback:
    """A two-node collector with explicit start/collect boundaries."""

    def __init__(self, ctx: Any, adapter: Any, out: Path):
        self.ctx = ctx
        self.adapter = adapter
        self.out = Path(out) / "deepflow-fallback"
        self.out.mkdir(parents=True, exist_ok=True)
        self.remote_roots: dict[str, str] = {}
        self.started = False
        self.collected = False

    def start(self) -> "DeepFlowFallback":
        if self.started:
            raise RuntimeError("DeepFlow fallback has already started")
        config = self.out / "deepflow-agent-standalone.yaml"
        config.write_text(CONFIG, encoding="utf-8")
        for node in ("a", "b"):
            created = self.ctx.node_exec(
                node,
                "sudo mkdir -p /opt/ebpf-study && "
                "sudo chown $(id -u):$(id -g) /opt/ebpf-study && "
                "mktemp -d /opt/ebpf-study/deepflow-fallback.XXXXXX",
            )
            remote = created.stdout.strip()
            if not remote.startswith("/opt/ebpf-study/deepflow-fallback."):
                raise RuntimeError(f"unexpected DeepFlow temporary directory on node {node}: {remote!r}")
            self.remote_roots[node] = remote
            self.ctx.node_exec(node, f"mkdir -p {shlex.quote(remote + '/data')}")
            self.ctx.node_put(node, config, remote + "/deepflow-agent-standalone.yaml")
            # Exact-name removal is limited to this fallback and permits recovery
            # from a technically failed prior attempt on the same guest.
            self.ctx.node_exec(node, f"docker rm -f {CONTAINER} >/dev/null 2>&1 || true")
            command = (
                f"docker run -d --name {CONTAINER} --privileged --pid=host --network=host "
                "--cpus=1 --memory=1024m --pids-limit=1024 "
                "--log-opt max-size=50m --log-opt max-file=2 "
                f"-v {shlex.quote(remote + '/deepflow-agent-standalone.yaml')}:/etc/deepflow-agent-standalone.yaml:ro "
                f"-v {shlex.quote(remote + '/data')}:/var/log/deepflow-agent "
                "-v /sys/kernel/debug:/sys/kernel/debug -v /sys/fs/bpf:/sys/fs/bpf "
                "-v /var/run/docker.sock:/var/run/docker.sock:ro "
                f"{DEEPFLOW_IMAGE} /bin/deepflow-agent --standalone "
                "-f /etc/deepflow-agent-standalone.yaml --cgroups-disabled"
            )
            self.ctx.node_exec(node, command, timeout=900)
        deadline = time.monotonic() + 90
        consecutive_ready = 0
        while time.monotonic() < deadline:
            states = [
                self.ctx.node_exec(
                    node,
                    f"docker inspect -f '{{{{.State.Running}}}}' {CONTAINER}",
                    check=False,
                )
                for node in ("a", "b")
            ]
            dispatchers = [
                self.ctx.node_exec(
                    node,
                    f"docker exec {CONTAINER} sh -c "
                    + shlex.quote(
                        "grep -h -E 'Start (.* )?dispatcher' "
                        "/var/log/deepflow-agent/* 2>/dev/null | head -n 1"
                    ),
                    check=False,
                )
                for node in ("a", "b")
            ]
            running = all(
                item.returncode == 0 and item.stdout.strip() == "true"
                for item in states
            )
            dispatcher_ready = all(
                item.returncode == 0 and "dispatcher" in item.stdout.lower()
                for item in dispatchers
            )
            if running and dispatcher_ready:
                consecutive_ready += 1
                if consecutive_ready >= 2:
                    self.started = True
                    self._write_provenance("running")
                    return self
            else:
                consecutive_ready = 0
            time.sleep(2)
        self._write_provenance("start_failed")
        raise RuntimeError(
            "DeepFlow fallback did not start a packet dispatcher on both guests within 90 seconds"
        )

    def collect(self) -> Path:
        if not self.started:
            raise RuntimeError("DeepFlow fallback was not started")
        if self.collected:
            return self.out
        errors: list[str] = []
        for node in ("a", "b"):
            node_out = self.out / f"node-{node}"
            node_out.mkdir(parents=True, exist_ok=True)
            for command, filename in (
                (f"docker inspect {CONTAINER}", "container-inspect-running.json"),
                (f"docker image inspect {shlex.quote(DEEPFLOW_IMAGE)}", "image-inspect.json"),
            ):
                result = self.ctx.node_exec(node, command, timeout=120, check=False)
                (node_out / filename).write_text(
                    result.stdout + result.stderr, encoding="utf-8"
                )
                if result.returncode:
                    errors.append(f"node {node} {filename}: exit {result.returncode}")
            stopped = self.ctx.node_exec(
                node, f"docker stop -t 20 {CONTAINER}", timeout=60, check=False
            )
            if stopped.returncode:
                errors.append(f"node {node} stop: exit {stopped.returncode}")
            for command, filename in (
                (f"docker logs --timestamps {CONTAINER}", "container.log"),
                (f"docker inspect {CONTAINER}", "container-inspect-stopped.json"),
            ):
                result = self.ctx.node_exec(node, command, timeout=120, check=False)
                (node_out / filename).write_text(
                    result.stdout + result.stderr, encoding="utf-8"
                )
                if result.returncode:
                    errors.append(f"node {node} {filename}: exit {result.returncode}")
            self.ctx.node_exec(
                node,
                f"sudo chmod -R a+rX {shlex.quote(self.remote_roots[node] + '/data')}",
                timeout=60,
                check=False,
            )
            raw_out = node_out / "raw"
            raw_out.mkdir(parents=True, exist_ok=True)
            listing = self.ctx.node_exec(
                node,
                f"find {shlex.quote(self.remote_roots[node] + '/data')} -maxdepth 1 -type f -printf '%f\\n'",
                timeout=60,
                check=False,
            )
            if listing.returncode:
                errors.append(f"node {node} raw listing: exit {listing.returncode}")
            for filename in listing.stdout.splitlines():
                if not filename or "/" in filename or "\\" in filename:
                    errors.append(f"node {node} unsafe raw filename: {filename!r}")
                    continue
                try:
                    self.ctx.node_get(
                        node,
                        self.remote_roots[node] + "/data/" + filename,
                        raw_out / filename,
                    )
                except Exception as exc:
                    errors.append(f"node {node} raw copy {filename}: {exc}")
            flow_files = [
                path for path in raw_out.iterdir()
                if path.name in {"l4_flow_log", "l4_flow_log.pre", "l7_flow_log", "l7_flow_log.pre"}
                and path.is_file()
            ]
            if not flow_files:
                errors.append(f"node {node}: no standalone L4/L7 flow file was produced")
            self.ctx.node_exec(node, f"docker rm {CONTAINER}", timeout=60, check=False)
        self.collected = True
        self._write_provenance("collected" if not errors else "collected_with_errors", errors)
        return self.out

    def _write_provenance(self, status: str, errors: list[str] | None = None) -> None:
        files = []
        for path in sorted(self.out.rglob("*")):
            if path.is_file() and path.name != "manifest.json":
                data = path.read_bytes()
                files.append({
                    "path": str(path.relative_to(self.out)).replace("\\", "/"),
                    "size": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                })
        manifest = {
            "schema_version": 1,
            "collector": "deepflow-agent-standalone",
            "status": status,
            "version": DEEPFLOW_VERSION,
            "image": DEEPFLOW_IMAGE,
            "source": f"https://github.com/deepflowio/deepflow/tree/{DEEPFLOW_SOURCE_COMMIT}",
            "source_commit": DEEPFLOW_SOURCE_COMMIT,
            "source_evidence": [
                f"https://github.com/deepflowio/deepflow/blob/{DEEPFLOW_SOURCE_COMMIT}/agent/src/main.rs",
                f"https://github.com/deepflowio/deepflow/blob/{DEEPFLOW_SOURCE_COMMIT}/agent/src/config/config.rs",
                f"https://github.com/deepflowio/deepflow/blob/{DEEPFLOW_SOURCE_COMMIT}/agent/src/sender/uniform_sender.rs",
                f"https://github.com/deepflowio/deepflow/blob/{DEEPFLOW_SOURCE_COMMIT}/agent/crates/public/src/l7_protocol.rs",
            ],
            "license": "Apache-2.0",
            "nodes": ["a", "b"],
            "resource_limit_per_node": {"cpus": 1, "memory_mib": 1024, "pids": 1024},
            "raw_rotation_per_node": {
                "max_mib_per_file": 128,
                "file_types": ["l4_flow_log", "l7_flow_log"],
                "max_files_per_type": 2,
                "maximum_flow_log_mib": 512,
            },
            "container_log_limit_per_node": {"max_mib_per_file": 50, "max_files": 2},
            "interpretation": {
                "raw_only": True,
                "custom_protocol_parser": False,
                "thrift_supported_by_v7_2_3_builtin_l7_enum": False,
                "limitation": "Thrift is absent from the pinned built-in L7Protocol enum; fallback may retain L4 Thrift connections and supported HTTP/MongoDB/Redis logs but cannot identify Thrift methods.",
            },
            "errors": errors or [],
            "files": files,
        }
        (self.out / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def fallback(ctx: Any, adapter: Any, out: Path) -> DeepFlowFallback:
    """Start the sole fallback and return its handle for later ``collect()``.

    The caller must start it before fallback traffic and call ``collect`` before
    guest teardown. Trigger policy remains outside this module.
    """

    return DeepFlowFallback(ctx, adapter, out).start()
