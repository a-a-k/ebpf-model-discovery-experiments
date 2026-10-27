"""Two-guest adapter for the pinned DeathStarBench Social Network benchmark.

Application downloads and Docker operations are deliberately performed through the
context, i.e. on a GitHub Actions runner or its guests, never at module import time.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import shutil
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests
import yaml

from .contracts_v3 import STABLE_FIXTURE_TEXT


UPSTREAM = "https://github.com/delimitrou/DeathStarBench.git"
COMMIT = "6ecb09706140f8730b5385c08f1386c654c3c526"
PROJECT = "dsb-ebpf-study"
REMOTE_ROOT = "/opt/ebpf-study/deathstarbench"

IMAGE_LOCKS = {
    "deathstarbench/social-network-microservices:latest": "deathstarbench/social-network-microservices:latest@sha256:a845266e98ce15d204ee7b98d41a2a95820af525013ce70f14104f5b9b5e92b6",
    "jaegertracing/all-in-one:latest": "jaegertracing/all-in-one:latest@sha256:8f165334f418ca53691ce358c19b4244226ed35c5d18408c5acf305af2065fb9",
    "memcached:latest": "memcached:latest@sha256:75c93cc91e76853da7c029e74d6e8dbd44774dd3713c93be8cd1971ad26120a4",
    "memcached": "memcached:latest@sha256:75c93cc91e76853da7c029e74d6e8dbd44774dd3713c93be8cd1971ad26120a4",
    "mongo:4.4.6": "mongo:4.4.6@sha256:6efa052039903e731e4a5550c68a13c4869ddc93742c716332883fd9c77eb79b",
    "redis:latest": "redis:latest@sha256:298e5b3bc566bade82f46ad5511777a4a07a294097ce16ada2f6a42be5239df5",
    "redis": "redis:latest@sha256:298e5b3bc566bade82f46ad5511777a4a07a294097ce16ada2f6a42be5239df5",
    "yg397/media-frontend:xenial": "yg397/media-frontend:xenial@sha256:272049995f2929435b91da34f20fc16216a7f974d1b8f9afa0ccbb529f1a9840",
    "yg397/openresty-thrift:xenial": "yg397/openresty-thrift:xenial@sha256:6c295fda3c2f6b941d85ebf16421bafac0dcf72450c96f53a2d031b29d8c81ef",
}
HAPROXY_IMAGE = "haproxy:3.0-alpine@sha256:34cc7d1f6142464d7d2b73e2a1eef7392556dbf304160aef543e513cfd9e5162"

REPLICA_CONTAINERS = {"a": "dsb-user-timeline-a", "b": "dsb-user-timeline-b"}
REPLICA_IPS = {"a": "172.28.11.41", "b": "172.28.12.41"}
PROXY_IP = "172.28.11.40"
DB_SERVICE = "user-timeline-mongodb"
DB_CONTAINER = "dsb-user-timeline-mongodb"
CROSS_NODE_PORTS = {
    "user-timeline-replica": 19090,
    "user-timeline-mongodb": 37020,
    "user-timeline-redis": 16383,
    "post-storage-service": 19092,
    "jaeger-agent-udp": 16831,
}
NATIVE_QUERY_LIMIT = 20_000
NATIVE_WINDOW_US = 120_000_000
NATIVE_MIN_WINDOW_US = 1_000_000
NATIVE_MAX_WINDOWS = 1_000


class AdapterError(RuntimeError):
    pass


def _json_dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_yaml(path: Path, value: Any) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def _tracing_yaml(disabled: bool, agent: str = "jaeger-agent:6831") -> str:
    return yaml.safe_dump(
        {
            "disabled": disabled,
            "reporter": {
                "logSpans": False,
                "localAgentHostPort": agent,
                "queueSize": 1_000_000,
                "bufferFlushInterval": 1,
            },
            "sampler": {"type": "const", "param": 0 if disabled else 1},
        },
        sort_keys=False,
    )


def _tag_nginx_request_spans(nginx_root: Path) -> None:
    """Put the opaque request ID on nginx's authoritative HTTP request span."""
    path = nginx_root / "conf" / "nginx.conf"
    source = path.read_text(encoding="utf-8")
    marker = "  opentracing on;\n"
    directive = (
        marker
        + "  opentracing_tag http.request.header.x-experiment-request-id "
        + "$http_x_experiment_request_id;\n"
    )
    if source.count(marker) != 1:
        raise AdapterError("unexpected nginx OpenTracing configuration shape")
    path.write_text(source.replace(marker, directive, 1), encoding="utf-8")


def _service_ip_map(names: list[str]) -> dict[str, str]:
    # Leave .40/.41 for the stable proxy and local controlled replica.
    addresses = [f"172.28.11.{i}" for i in range(10, 40)]
    if len(names) > len(addresses):
        raise AdapterError("too many upstream services for the reserved subnet")
    return dict(zip(sorted(names), addresses))


class Adapter:
    operations = ("compose_post", "read_home_timeline", "read_user_timeline")

    def __init__(self, context: Any):
        self.ctx = context
        if context.mode not in {"absent", "partial", "full"}:
            raise ValueError(f"unsupported tracing mode: {context.mode!r}")
        self.root = Path(context.deployment_dir) / "deathstarbench"
        self.source = self.root / "upstream"
        self.node_dirs = {n: self.root / f"node-{n}" for n in ("a", "b")}
        self.entry_url = f"http://{context.node_ip('a')}:8080"
        self._mapping: dict[str, str] = {}
        self._replica_state = "11"
        self._database_up = True
        self._control_epoch = 0
        # Includes preparation traffic and qualification if capture is requested.
        self._native_capture_since_us = time.time_ns() // 1000

    def prepare(self) -> None:
        """Fetch the pinned source and render independent guest deployments."""
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)
        self.source.mkdir()
        self.ctx.run(["git", "init", "-q"], cwd=self.source)
        self.ctx.run(["git", "remote", "add", "origin", UPSTREAM], cwd=self.source)
        self.ctx.run(["git", "fetch", "--depth=1", "origin", COMMIT], cwd=self.source, timeout=900)
        self.ctx.run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=self.source)
        actual = self.ctx.run(["git", "rev-parse", "HEAD"], cwd=self.source)
        if getattr(actual, "stdout", "").strip() != COMMIT:
            raise AdapterError("DeathStarBench checkout did not resolve to the pinned commit")
        self._render()

    def _render(self) -> None:
        social = self.source / "socialNetwork"
        upstream = yaml.safe_load((social / "docker-compose.yml").read_text(encoding="utf-8"))
        services = upstream["services"]
        original_replica = services.pop("user-timeline-service")
        node_a = self.node_dirs["a"]
        node_b = self.node_dirs["b"]
        node_a.mkdir(parents=True)
        node_b.mkdir(parents=True)

        # Copy only runtime bind mounts, not build trees.
        for relative in ("config", "nginx-web-server", "gen-lua", "media-frontend", "docker/openresty-thrift/lua-thrift"):
            src = social / relative
            dst = node_a / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
        _tag_nginx_request_spans(node_a / "nginx-web-server")
        shutil.copytree(social / "config", node_b / "config")
        shutil.copytree(social / "config", node_a / "config-disabled")
        shutil.copytree(social / "config", node_b / "config-disabled")

        common_disabled = self.ctx.mode == "absent"
        (node_a / "config" / "jaeger-config.yml").write_text(_tracing_yaml(common_disabled), encoding="utf-8")
        (node_a / "config-disabled" / "jaeger-config.yml").write_text(_tracing_yaml(True), encoding="utf-8")
        (node_b / "config" / "jaeger-config.yml").write_text(_tracing_yaml(self.ctx.mode != "full"), encoding="utf-8")
        (node_b / "config-disabled" / "jaeger-config.yml").write_text(_tracing_yaml(True), encoding="utf-8")
        nginx_cfg = json.loads((node_a / "nginx-web-server" / "jaeger-config.json").read_text(encoding="utf-8"))
        nginx_cfg.pop("diabled", None)  # upstream typo is not a tracing control
        nginx_cfg["disabled"] = common_disabled
        nginx_cfg["sampler"] = {"type": "const", "param": 0 if common_disabled else 1}
        _json_dump(node_a / "nginx-web-server" / "jaeger-config.json", nginx_cfg)

        # Docker 29 bridge forwarding between the guest subnets is not assumed.
        # Only replica B's config uses node A's published dependency ports; node
        # A services retain their original container-local identities.
        node_b_service_config_path = node_b / "config" / "service-config.json"
        node_b_service_config = json.loads(node_b_service_config_path.read_text(encoding="utf-8"))
        for service, port in (
            ("user-timeline-mongodb", CROSS_NODE_PORTS["user-timeline-mongodb"]),
            ("user-timeline-redis", CROSS_NODE_PORTS["user-timeline-redis"]),
            ("post-storage-service", CROSS_NODE_PORTS["post-storage-service"]),
        ):
            node_b_service_config[service]["addr"] = self.ctx.node_ip("a")
            node_b_service_config[service]["port"] = port
        _json_dump(node_b_service_config_path, node_b_service_config)
        (node_b / "config" / "jaeger-config.yml").write_text(
            _tracing_yaml(
                self.ctx.mode != "full",
                f"{self.ctx.node_ip('a')}:{CROSS_NODE_PORTS['jaeger-agent-udp']}",
            ),
            encoding="utf-8",
        )

        names = list(services)
        ip_map = _service_ip_map(names)
        for name, spec in services.items():
            image = str(spec.get("image", ""))
            if image not in IMAGE_LOCKS:
                raise AdapterError(f"no image lock for {name}: {image}")
            spec["image"] = IMAGE_LOCKS[image]
            spec["container_name"] = f"dsb-{name}"
            spec["networks"] = {"app": {"ipv4_address": ip_map[name]}}
            # Compose's local ordering cannot describe the remote replica; all
            # actual readiness is checked by ready().
        services["user-timeline-mongodb"]["ports"] = [
            f"{CROSS_NODE_PORTS['user-timeline-mongodb']}:27017"
        ]
        services["user-timeline-redis"]["ports"] = [
            f"{CROSS_NODE_PORTS['user-timeline-redis']}:6379"
        ]
        services["post-storage-service"]["ports"] = [
            f"{CROSS_NODE_PORTS['post-storage-service']}:9090"
        ]
        services["jaeger-agent"]["ports"] = [
            "16686:16686", f"{CROSS_NODE_PORTS['jaeger-agent-udp']}:6831/udp"
        ]
        replica_a = json.loads(json.dumps(original_replica))
        replica_a.update(
            image=IMAGE_LOCKS[str(original_replica["image"])],
            hostname="user-timeline-service-replica-a",
            container_name=REPLICA_CONTAINERS["a"],
            networks={"app": {"ipv4_address": REPLICA_IPS["a"]}},
            ports=[f"{CROSS_NODE_PORTS['user-timeline-replica']}:9090"],
        )
        if self.ctx.mode == "partial":
            replica_a["volumes"] = ["./config-disabled:/social-network-microservices/config"]
        services["user-timeline-service-replica-a"] = replica_a
        services["user-timeline-service"] = {
            "image": HAPROXY_IMAGE,
            "hostname": "user-timeline-service",
            "container_name": "dsb-user-timeline-proxy",
            "restart": "always",
            "volumes": ["./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro"],
            "networks": {"app": {"ipv4_address": PROXY_IP}},
        }
        upstream["name"] = PROJECT
        upstream["networks"] = {"app": {"external": True, "name": "dsb-app-a"}}
        _write_yaml(node_a / "docker-compose.yml", upstream)

        replica_b = json.loads(json.dumps(original_replica))
        replica_b.pop("depends_on", None)
        replica_b.update(
            image=IMAGE_LOCKS[str(original_replica["image"])],
            hostname="user-timeline-service-replica-b",
            container_name=REPLICA_CONTAINERS["b"],
            networks={"app": {"ipv4_address": REPLICA_IPS["b"]}},
            ports=[f"{CROSS_NODE_PORTS['user-timeline-replica']}:9090"],
            volumes=["./config:/social-network-microservices/config"],
        )
        compose_b = {
            "name": PROJECT,
            "services": {"user-timeline-service-replica-b": replica_b},
            "networks": {"app": {"external": True, "name": "dsb-app-b"}},
        }
        _write_yaml(node_b / "docker-compose.yml", compose_b)

        (node_a / "haproxy.cfg").write_text(
            "global\n  log stdout format raw local0\n"
            "defaults\n  mode tcp\n  timeout connect 2s\n  timeout client 15s\n  timeout server 15s\n"
            "frontend thrift\n  bind *:9090\n  default_backend replicas\n"
            "backend replicas\n  balance roundrobin\n  option tcp-check\n"
            f"  server replica-a {REPLICA_IPS['a']}:9090 check inter 1s fall 2 rise 1\n"
            f"  server replica-b {self.ctx.node_ip('b')}:{CROSS_NODE_PORTS['user-timeline-replica']} check inter 1s fall 2 rise 1\n",
            encoding="utf-8",
        )
        self._mapping = {**ip_map, "user-timeline-service": PROXY_IP, **{f"user-timeline-replica-{k}": v for k, v in REPLICA_IPS.items()}}
        _json_dump(self.root / "container-ip-mapping.json", {
            "node_a_subnet": "172.28.11.0/24", "node_b_subnet": "172.28.12.0/24",
            "services": self._mapping,
        })
        shutil.copy2(node_a / "docker-compose.yml", self.root / "resolved-node-a.yml")
        shutil.copy2(node_b / "docker-compose.yml", self.root / "resolved-node-b.yml")

    def deploy(self) -> None:
        for node in ("a", "b"):
            self.ctx.node_exec(node, f"sudo mkdir -p {REMOTE_ROOT} && sudo chown -R $(id -u):$(id -g) {REMOTE_ROOT}")
            # Context.node_put copies a directory's contents into destination.
            self.ctx.node_put(node, self.node_dirs[node], f"{REMOTE_ROOT}/node-{node}")
        self.ctx.node_exec("a", "docker network inspect dsb-app-a >/dev/null 2>&1 || docker network create --driver bridge --subnet 172.28.11.0/24 dsb-app-a")
        self.ctx.node_exec("b", "docker network inspect dsb-app-b >/dev/null 2>&1 || docker network create --driver bridge --subnet 172.28.12.0/24 dsb-app-b")
        self.ctx.node_exec("a", f"cd {REMOTE_ROOT}/node-a && docker compose pull && docker compose up -d", timeout=1200)
        self.ctx.node_exec("b", f"cd {REMOTE_ROOT}/node-b && docker compose pull && docker compose up -d", timeout=1200)
        for node in ("a", "b"):
            rendered = self.ctx.node_exec(node, f"cd {REMOTE_ROOT}/node-{node} && docker compose config")
            (self.root / f"runtime-resolved-node-{node}.yml").write_text(rendered.stdout, encoding="utf-8")
        _json_dump(self.root / "tracing-mode.json", self._tracing_record())

    def _tracing_record(self) -> dict[str, Any]:
        return {
            "mode": self.ctx.mode,
            "mechanism": "Jaeger SDK disabled flag plus const-zero sampler; collector remains for negative observation",
            "frontend_sdk_disabled": self.ctx.mode == "absent",
            "ordinary_service_sdks_disabled": self.ctx.mode == "absent",
            "controlled_replica_sdks_disabled": self.ctx.mode in {"absent", "partial"},
            "export_is_not_merely_blocked": True,
        }

    def ready(self) -> None:
        deadline = time.monotonic() + 360
        last = "not attempted"
        while time.monotonic() < deadline:
            try:
                response = requests.get(self.entry_url + "/", timeout=2)
                last = f"HTTP {response.status_code}"
                both = all(self._container_running(node, name) for node, name in REPLICA_CONTAINERS.items())
                if response.ok and both:
                    break
            except requests.RequestException as exc:
                last = str(exc)
            time.sleep(2)
        else:
            raise AdapterError(f"DeathStarBench did not become ready in 360s: {last}")
        self._initialize_fixtures()
        self._assert_stable_fixture(timeout=15)
        self._verify_each_replica_serves()

    def _container_running(self, node: str, container: str) -> bool:
        result = self.ctx.node_exec(
            node, f"docker inspect -f '{{{{.State.Running}}}}' {container}", check=False
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def _initialize_fixtures(self) -> None:
        actions = []
        for uid in (0, 1, 2, 3):
            actions.append(("/wrk2-api/user/register", {
                "first_name": f"first_name_{uid}", "last_name": f"last_name_{uid}",
                "username": f"username_{uid}", "password": f"password_{uid}", "user_id": str(uid),
            }))
        # User 0/1 are reserved for unique compose attempts and their fan-out.
        # User 2/3 remain untouched after setup and provide stable read oracles.
        for uid, followee in ((1, 0), (3, 2)):
            actions.append(("/wrk2-api/user/follow", {
                "user_name": f"username_{uid}", "followee_name": f"username_{followee}",
            }))
        evidence = []
        for path, form in actions:
            attempts = []
            for _ in range(30):
                try:
                    response = requests.post(self.entry_url + path, data=form, timeout=10)
                    attempts.append({"status": response.status_code, "body_sha256": hashlib.sha256(response.content).hexdigest()})
                    if response.ok:
                        break
                except requests.RequestException as exc:
                    attempts.append({"error": str(exc)})
                time.sleep(2)
            else:
                evidence.append({"path": path, "attempts": attempts})
                _json_dump(self.root / "fixture-initialization.json", evidence)
                raise AdapterError(f"fixture initialization {path} did not succeed in 30 attempts")
            evidence.append({"path": path, "attempts": attempts})
        stable_form = {
            "username": "username_2", "user_id": "2", "text": STABLE_FIXTURE_TEXT,
            "media_ids": "[]", "media_types": "[]", "post_type": "0",
        }
        stable_attempts = []
        for _ in range(30):
            try:
                response = requests.post(self.entry_url + "/wrk2-api/post/compose", data=stable_form, timeout=10)
                stable_attempts.append({"status": response.status_code, "body_sha256": hashlib.sha256(response.content).hexdigest()})
                if response.ok and b"Successfully upload post" in response.content:
                    break
            except requests.RequestException as exc:
                stable_attempts.append({"error": str(exc)})
            time.sleep(2)
        else:
            raise AdapterError("stable timeline fixture could not be composed")
        evidence.append({"path": "/wrk2-api/post/compose", "fixture": "stable-read-principals", "attempts": stable_attempts})
        _json_dump(self.root / "fixture-initialization.json", evidence)

    def _assert_stable_fixture(self, timeout: float) -> None:
        paths = (
            "/wrk2-api/user-timeline/read?user_id=2&start=0&stop=10",
            "/wrk2-api/home-timeline/read?user_id=3&start=0&stop=10",
        )
        for path in paths:
            until = time.monotonic() + timeout
            while time.monotonic() < until:
                try:
                    response = requests.get(self.entry_url + path, timeout=min(2, timeout))
                    if response.ok and self._valid_timeline(response.content, STABLE_FIXTURE_TEXT):
                        break
                except requests.RequestException:
                    pass
                time.sleep(0.25)
            else:
                raise AdapterError(f"stable timeline fixture unavailable at {path}")

    def _verify_each_replica_serves(self) -> None:
        evidence = []
        for selected, other in (("a", "b"), ("b", "a")):
            self.ctx.node_exec(other, f"docker stop {REPLICA_CONTAINERS[other]}", timeout=120)
            record: dict[str, Any] | None = None
            try:
                deadline = time.monotonic() + 20
                attempt = 0
                while time.monotonic() < deadline:
                    record = self.operation(
                        "read_user_timeline", attempt,
                        f"readiness-replica-{selected}", deadline=5,
                    )
                    if record["success"] is True:
                        break
                    attempt += 1
                    time.sleep(1)
                else:
                    raise AdapterError(
                        f"user-timeline replica {selected} did not serve the semantic probe alone"
                    )
                evidence.append({
                    "selected_replica": selected,
                    "other_replica_stopped": other,
                    "attempts": attempt + 1,
                    "response_sha256": record["http_steps"][0].get("response_sha256"),
                    "success": True,
                })
            finally:
                self.ctx.node_exec(other, f"docker start {REPLICA_CONTAINERS[other]}", timeout=120)
        listener_deadline = time.monotonic() + 30
        while time.monotonic() < listener_deadline:
            checks = (
                self.ctx.node_exec(
                    "a", f"timeout 1 bash -c '</dev/tcp/127.0.0.1/{CROSS_NODE_PORTS['user-timeline-replica']}'",
                    check=False,
                ),
                self.ctx.node_exec(
                    "b", f"timeout 1 bash -c '</dev/tcp/127.0.0.1/{CROSS_NODE_PORTS['user-timeline-replica']}'",
                    check=False,
                ),
            )
            if all(check.returncode == 0 for check in checks):
                break
            time.sleep(1)
        else:
            raise AdapterError("both user-timeline replica listeners were not restored after readiness probes")
        _json_dump(self.root / "replica-readiness.json", evidence)

    def metadata(self) -> dict[str, Any]:
        return {
            "system": "deathstarbench",
            "operations": list(self.operations),
            "entry_url": self.entry_url,
            "replicas": [
                {
                    "name": REPLICA_CONTAINERS[n], "node": n,
                    "ip": REPLICA_IPS[n], "port": 9090,
                    "transport_host": self.ctx.node_ip(n),
                    "transport_port": CROSS_NODE_PORTS["user-timeline-replica"],
                }
                for n in ("a", "b")
            ],
            "proxy": {"name": "dsb-user-timeline-proxy", "node": "a", "ip": PROXY_IP, "policy": "roundrobin"},
            "database": {
                "logical_identity": DB_SERVICE, "name": DB_CONTAINER,
                "node": "a", "ip": self._mapping.get(DB_SERVICE), "port": 27017,
                "transport_host": self.ctx.node_ip("a"),
                "transport_port": CROSS_NODE_PORTS["user-timeline-mongodb"],
            },
            "cross_node_transport": {
                "kind": "docker_published_guest_ports",
                "node_a_host": self.ctx.node_ip("a"),
                "node_b_host": self.ctx.node_ip("b"),
                "ports": CROSS_NODE_PORTS,
                "readiness_record": str(self.root / "replica-readiness.json"),
            },
            "source": {"repository": UPSTREAM, "commit": COMMIT},
            "images": sorted(set(IMAGE_LOCKS.values()) | {HAPROXY_IMAGE}),
            "native_export": {"kind": "jaeger_api", "url": f"http://{self.ctx.node_ip('a')}:16686", "mode": self.ctx.mode},
            "deployment_records": [str(self.root / "runtime-resolved-node-a.yml"), str(self.root / "runtime-resolved-node-b.yml"), str(self.root / "container-ip-mapping.json")],
            "tracing_suppression": self._tracing_record(),
        }

    def reset(self) -> None:
        # There is no queue in this pinned compose path. Keep registered users and
        # posts: Mongo/Redis persistence is required for meaningful timeline reads.
        self.set_database(True)
        self.set_replicas("11")
        self.ready_without_fixtures()

    def ready_without_fixtures(self) -> None:
        self._assert_stable_fixture(timeout=120)

    def set_replicas(self, state: str) -> None:
        if state not in {"11", "10", "01", "00"}:
            raise ValueError(f"invalid replica state: {state}")
        for bit, node in zip(state, ("a", "b"), strict=True):
            action = "start" if bit == "1" else "stop"
            self.ctx.node_exec(node, f"docker {action} {REPLICA_CONTAINERS[node]}", timeout=120)
        self._replica_state = state
        self._control_epoch += 1

    def set_database(self, up: bool) -> None:
        self.ctx.node_exec("a", f"docker {'start' if up else 'stop'} {DB_CONTAINER}", timeout=120)
        self._database_up = up
        self._control_epoch += 1

    @staticmethod
    def _valid_timeline(body: bytes, expected_text: str) -> bool:
        try:
            value = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        valid_shape = isinstance(value, list) and all(
            isinstance(item, dict) and isinstance(item.get("post_id"), str) and isinstance(item.get("text"), str)
            for item in value
        )
        return valid_shape and any(item["text"] == expected_text for item in value)

    @staticmethod
    def _within_deadline(started_monotonic_ns: int, ended_monotonic_ns: int, deadline: float) -> bool:
        return ended_monotonic_ns - started_monotonic_ns <= int(deadline * 1_000_000_000)

    def operation(self, name: str, index: int, namespace: str, deadline: float = 2.0) -> dict[str, Any]:
        if name not in self.operations:
            raise ValueError(f"unknown DeathStarBench operation: {name}")
        if deadline <= 0:
            raise ValueError("deadline must be positive")
        attempt_id = f"{namespace}-{name}-{index:08d}"
        digest = hashlib.sha256(attempt_id.encode("utf-8")).hexdigest()
        request_id = "req-" + digest
        headers = {"X-Experiment-Request-Id": request_id}
        started = time.time_ns()
        monotonic_started = time.monotonic_ns()
        censored_policy = getattr(self.ctx, "observation_policy", None) == "censored-v3"
        method = "GET"
        path: str
        data: dict[str, str] | None = None
        marker = f"ebpf-study {request_id}"
        if name == "compose_post":
            method = "POST"
            path = "/wrk2-api/post/compose"
            data = {
                "username": "username_0", "user_id": "0", "text": marker,
                "media_ids": '["123456789012345678"]' if index % 2 else "[]",
                "media_types": '["png"]' if index % 2 else "[]", "post_type": "0",
            }
        elif name == "read_home_timeline":
            path = "/wrk2-api/home-timeline/read?user_id=3&start=0&stop=10"
        else:
            path = "/wrk2-api/user-timeline/read?user_id=2&start=0&stop=10"
        step: dict[str, Any] = {"request_id": request_id, "method": method, "url": self.entry_url + path, "request_form": data, "request_headers": headers}
        error = ""
        success: bool | None
        termination = "complete"
        try:
            if censored_policy:
                from ebpf_discovery.transport_v3 import request as observed_request
                remaining = deadline-(time.monotonic_ns()-monotonic_started)/1e9
                response = observed_request(method, step["url"], data=data, headers=headers, timeout=remaining)
            else:
                response = requests.request(method, step["url"], data=data, headers=headers, timeout=deadline)
            body = response.content
            if censored_policy:
                step["body_completed_ns"] = getattr(response, "_study_body_completed_ns", time.time_ns())
            monotonic_ended = time.monotonic_ns()
            within_deadline = self._within_deadline(monotonic_started, monotonic_ended, deadline)
            step.update(status=response.status_code, response_body_base64=base64.b64encode(body).decode("ascii"), response_sha256=hashlib.sha256(body).hexdigest())
            if name == "compose_post":
                content_valid = response.ok and b"Successfully upload post" in body
                success = content_valid if censored_policy else content_valid and within_deadline
                reason = "" if content_valid else "missing exact compose acknowledgement"
            else:
                content_valid = response.ok and self._valid_timeline(body, STABLE_FIXTURE_TEXT)
                success = content_valid if censored_policy else content_valid and within_deadline
                reason = "" if content_valid else "response does not contain the stable fixture in the pinned timeline JSON shape"
            if not response.ok:
                reason = f"HTTP {response.status_code}"
            elif not censored_policy and not within_deadline:
                reason = f"response completed after {deadline:.6f}s deadline"
            error = reason
        except requests.Timeout as exc:
            success = None if censored_policy else False
            termination = "cap_reached"
            error = f"observation cap reached: {exc}" if censored_policy else f"deadline exceeded: {exc}"
            step["transport_error"] = error
        except requests.RequestException as exc:
            success = None if censored_policy else False
            termination = "transport_incomplete"
            error = str(exc)
            step["transport_error"] = error
        ended = time.time_ns()
        monotonic_ended = time.monotonic_ns()
        step["started_ns"] = started
        step["ended_ns"] = ended
        step["elapsed_ns"] = monotonic_ended - monotonic_started
        step["deadline_seconds"] = deadline
        step["within_deadline"] = self._within_deadline(monotonic_started, monotonic_ended, deadline)
        if not censored_policy and success is True and not step["within_deadline"]:
            success = False
            error = f"response processing completed after {deadline:.6f}s deadline"
        result = {
            "operation": name, "attempt_id": attempt_id, "started_ns": started, "ended_ns": ended,
            "success": success, "http_steps": [step], "error": error,
            "validation": {
                "kind": "exact_http_content_oracle",
                "compose_marker_sha256": hashlib.sha256(marker.encode()).hexdigest() if name == "compose_post" else None,
                "control_epoch": self._control_epoch,
                "replica_state": self._replica_state,
                "database_up": self._database_up,
            },
        }
        if censored_policy:
            result["observation"] = {
                "policy": "censored-v3", "cap_seconds": deadline,
                "cutoff_ns": started + int(deadline * 1_000_000_000),
                "censored": termination != "complete", "termination": termination,
            }
        return result

    def verify(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # Return copies: eventual evidence never changes the immediate HTTP
        # outcome. Its deadline is anchored to the original response time, so a
        # verification delayed until after block restoration becomes unknown.
        verified = copy.deepcopy(records)
        for record in verified:
            if record.get("operation") != "compose_post" or record.get("success") is not True:
                continue
            if record.get("validation", {}).get("control_epoch") != self._control_epoch:
                record["eventual_postcondition"] = {
                    "kind": "compose_eventual_fanout", "success": None,
                    "unknown_reason": "control state changed before verification",
                }
                continue
            request_id = str(record["http_steps"][0]["request_id"])
            expected = f"ebpf-study {request_id}"
            locations = {
                "user_timeline_owner": "/wrk2-api/user-timeline/read?user_id=0&start=0&stop=1000",
                "home_timeline_follower": "/wrk2-api/home-timeline/read?user_id=1&start=0&stop=1000",
            }
            evidence: dict[str, Any] = {}
            deadline_ns = int(record["ended_ns"]) + 10_000_000_000
            for label, path in locations.items():
                found = False
                last: dict[str, Any] = {"error": "not attempted"}
                while time.time_ns() < deadline_ns:
                    try:
                        remaining = max(0.001, (deadline_ns - time.time_ns()) / 1_000_000_000)
                        r = requests.get(self.entry_url + path, timeout=min(2, remaining))
                        found = r.ok and time.time_ns() <= deadline_ns and self._valid_timeline(r.content, expected)
                        last = {"status": r.status_code, "body_sha256": hashlib.sha256(r.content).hexdigest(), "found": found}
                    except requests.RequestException as exc:
                        last = {"error": str(exc), "found": False}
                    if found:
                        break
                    time.sleep(0.25)
                evidence[label] = last
            settled = all(v.get("found") is True for v in evidence.values())
            record["eventual_postcondition"] = {
                "kind": "compose_eventual_fanout", "expected_text_sha256": hashlib.sha256(expected.encode()).hexdigest(),
                "deadline_ns": deadline_ns, "locations": evidence,
                "success": settled if time.time_ns() <= deadline_ns or settled else None,
                "unknown_reason": None if settled else "not observed before original ten-second deadline",
                "control_epoch": self._control_epoch,
            }
        return verified

    def collect_native(self, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=True)
        base = f"http://{self.ctx.node_ip('a')}:16686"
        manifest: dict[str, Any] = {
            "mode": self.ctx.mode, "queries": [], "errors": [],
            "service_census": {},
        }
        try:
            services_response = requests.get(base + "/api/services", timeout=30)
            (destination / "services.json").write_bytes(services_response.content)
            services_response.raise_for_status()
            document = services_response.json()
            if not isinstance(document, dict):
                raise ValueError("Jaeger service census is not a JSON object")
            api_errors = document.get("errors")
            data = document.get("data")
            manifest["service_census"] = {
                "http_status": services_response.status_code,
                "data_is_null": data is None,
                "api_errors": api_errors,
                "raw_sha256": hashlib.sha256(services_response.content).hexdigest(),
            }
            if api_errors:
                manifest["errors"].append(f"service census API errors: {api_errors}")
            if data is None:
                services = []
            elif isinstance(data, list):
                services = data
            else:
                raise ValueError("Jaeger service census data is neither null nor a list")
        except (requests.RequestException, ValueError, AttributeError) as exc:
            services = []
            manifest["errors"].append(f"service census: {exc}")
        trace_count = 0
        application_trace_count = 0
        audit_self_trace_count = 0
        capture_end_us = max(self._native_capture_since_us + 1, time.time_ns() // 1000 + 1)
        manifest["capture_window_us"] = [self._native_capture_since_us, capture_end_us]
        manifest["query_limit"] = NATIVE_QUERY_LIMIT
        manifest["maximum_windows_per_service"] = NATIVE_MAX_WINDOWS
        for service in services:
            seen_trace_ids: set[str] = set()
            safe = urllib.parse.quote(str(service), safe="")
            windows = [
                (start, min(start + NATIVE_WINDOW_US - 1, capture_end_us))
                for start in range(self._native_capture_since_us, capture_end_us + 1, NATIVE_WINDOW_US)
            ]
            queried = 0
            while windows:
                if queried >= NATIVE_MAX_WINDOWS:
                    manifest["errors"].append(f"trace query {service}: maximum native windows reached")
                    break
                start_us, end_us = windows.pop(0)
                queried += 1
                try:
                    r = requests.get(base + "/api/traces", params={
                        "service": service, "start": start_us, "end": end_us,
                        "limit": NATIVE_QUERY_LIMIT,
                    }, timeout=60)
                    filename = f"traces-{safe}-{start_us}-{end_us}.json"
                    (destination / filename).write_bytes(r.content)
                    r.raise_for_status()
                    trace_document = r.json()
                    if not isinstance(trace_document, dict):
                        raise ValueError("Jaeger trace response is not a JSON object")
                    trace_api_errors = trace_document.get("errors")
                    trace_data = trace_document.get("data")
                    if trace_data is None:
                        trace_data = []
                    if not isinstance(trace_data, list):
                        raise ValueError("Jaeger trace data is neither null nor a list")
                    count = len(trace_data)
                    total = trace_document.get("total")
                    saturated = count >= NATIVE_QUERY_LIMIT or (
                        type(total) is int and total > count
                    )
                    manifest["queries"].append({
                        "service": service, "count": count, "total": total,
                        "start_us": start_us, "end_us": end_us, "file": filename,
                        "saturated": saturated,
                        "excluded_from_application_trace_count": service == "jaeger-all-in-one",
                        "data_is_null": trace_document.get("data") is None,
                        "api_errors": trace_api_errors,
                        "sha256": hashlib.sha256(r.content).hexdigest(),
                    })
                    if trace_api_errors:
                        manifest["errors"].append(f"trace query {service} API errors: {trace_api_errors}")
                    if saturated:
                        if end_us - start_us < NATIVE_MIN_WINDOW_US:
                            manifest["errors"].append(
                                f"trace query {service}: unresolved saturated window {start_us}-{end_us}"
                            )
                        else:
                            midpoint = (start_us + end_us) // 2
                            windows[0:0] = [(start_us, midpoint), (midpoint + 1, end_us)]
                        continue
                    for trace in trace_data:
                        trace_id = trace.get("traceID") if isinstance(trace, dict) else None
                        if not isinstance(trace_id, str) or not trace_id:
                            manifest["errors"].append(f"trace query {service}: trace without identity")
                            continue
                        seen_trace_ids.add(trace_id)
                except (requests.RequestException, ValueError, AttributeError) as exc:
                    manifest["errors"].append(f"trace query {service} {start_us}-{end_us}: {exc}")
            count = len(seen_trace_ids)
            trace_count += count
            if service == "jaeger-all-in-one":
                audit_self_trace_count += count
            else:
                application_trace_count += count
        manifest["trace_count"] = trace_count
        manifest["application_trace_count"] = application_trace_count
        manifest["audit_self_trace_count"] = audit_self_trace_count
        manifest["audit_self_trace_provenance"] = {
            "excluded_service_exact_match": "jaeger-all-in-one",
            "reason": "Jaeger's instrumented query API can trace the audit's own /api/services and /api/traces requests",
            "raw_responses_retained": True,
        }
        manifest["absence_verified"] = (
            self.ctx.mode == "absent"
            and not manifest["errors"]
            and application_trace_count == 0
        )
        _json_dump(destination / "manifest.json", manifest)

    def close(self) -> None:
        diagnostics = Path(self.ctx.out) / "deathstarbench-diagnostics"
        diagnostics.mkdir(parents=True, exist_ok=True)
        for node in ("a", "b"):
            for command, filename in (
                ("docker ps -a --no-trunc", "containers.txt"),
                (f"cd {REMOTE_ROOT}/node-{node} && docker compose logs --no-color --timestamps", "compose.log"),
            ):
                try:
                    result = self.ctx.node_exec(node, command, timeout=120)
                    (diagnostics / f"node-{node}-{filename}").write_text(result.stdout + getattr(result, "stderr", ""), encoding="utf-8")
                except Exception as exc:  # cleanup must continue on a failed campaign
                    (diagnostics / f"node-{node}-{filename}.error").write_text(str(exc), encoding="utf-8")
            try:
                self.ctx.node_exec(node, f"cd {REMOTE_ROOT}/node-{node} && docker compose down --remove-orphans", timeout=300)
            except Exception as exc:
                (diagnostics / f"node-{node}-cleanup.error").write_text(str(exc), encoding="utf-8")
