from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import yaml

from systems.deathstarbench.adapter import Adapter
from systems.deathstarbench.deepflow_fallback import CONFIG, DEEPFLOW_IMAGE, fallback


class OracleTests(unittest.TestCase):
    def test_native_null_service_data_is_verified_absence(self):
        class Context:
            mode = "absent"
            seed = 0

            def __init__(self, root):
                self.deployment_dir = root / "deployment"
                self.out = root

            @staticmethod
            def node_ip(_node):
                return "192.0.2.1"

        class Response:
            status_code = 200
            content = b'{"data":null,"total":0,"limit":0,"offset":0,"errors":null}'

            @staticmethod
            def raise_for_status():
                return None

            @staticmethod
            def json():
                return {"data": None, "total": 0, "errors": None}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapter = Adapter(Context(root))
            with mock.patch("systems.deathstarbench.adapter.requests.get", return_value=Response()):
                adapter.collect_native(root / "native")
            manifest = json.loads((root / "native" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["errors"], [])
        self.assertTrue(manifest["service_census"]["data_is_null"])
        self.assertIsNone(manifest["service_census"]["api_errors"])
        self.assertTrue(manifest["absence_verified"])

    def test_native_http_200_api_errors_are_not_verified_absence(self):
        class Context:
            mode = "absent"
            seed = 0

            def __init__(self, root):
                self.deployment_dir = root / "deployment"
                self.out = root

            @staticmethod
            def node_ip(_node):
                return "192.0.2.1"

        class Response:
            status_code = 200
            content = b'{"data":null,"errors":[{"code":500,"msg":"storage unavailable"}]}'

            @staticmethod
            def raise_for_status():
                return None

            @staticmethod
            def json():
                return {"data": None, "errors": [{"code": 500, "msg": "storage unavailable"}]}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapter = Adapter(Context(root))
            with mock.patch("systems.deathstarbench.adapter.requests.get", return_value=Response()):
                adapter.collect_native(root / "native")
            manifest = json.loads((root / "native" / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["errors"])
        self.assertFalse(manifest["absence_verified"])
        self.assertEqual(manifest["service_census"]["api_errors"][0]["code"], 500)

    def test_render_complete_pinned_upstream_shape(self):
        class Context:
            mode = "partial"
            seed = 0

            def __init__(self, root):
                self.deployment_dir = root / "deployment"
                self.out = root

            @staticmethod
            def node_ip(_node):
                return "192.0.2.1"

        images = {
            "social-graph-service": "deathstarbench/social-network-microservices:latest",
            "social-graph-mongodb": "mongo:4.4.6",
            "social-graph-redis": "redis",
            "home-timeline-redis": "redis",
            "compose-post-service": "deathstarbench/social-network-microservices:latest",
            "post-storage-service": "deathstarbench/social-network-microservices:latest",
            "post-storage-memcached": "memcached",
            "post-storage-mongodb": "mongo:4.4.6",
            "user-timeline-service": "deathstarbench/social-network-microservices:latest",
            "user-timeline-redis": "redis",
            "user-timeline-mongodb": "mongo:4.4.6",
            "url-shorten-service": "deathstarbench/social-network-microservices:latest",
            "url-shorten-memcached": "memcached",
            "url-shorten-mongodb": "mongo:4.4.6",
            "user-service": "deathstarbench/social-network-microservices:latest",
            "user-memcached": "memcached",
            "user-mongodb": "mongo:4.4.6",
            "media-service": "deathstarbench/social-network-microservices:latest",
            "media-memcached": "memcached",
            "media-mongodb": "mongo:4.4.6",
            "text-service": "deathstarbench/social-network-microservices:latest",
            "unique-id-service": "deathstarbench/social-network-microservices:latest",
            "user-mention-service": "deathstarbench/social-network-microservices:latest",
            "home-timeline-service": "deathstarbench/social-network-microservices:latest",
            "nginx-thrift": "yg397/openresty-thrift:xenial",
            "media-frontend": "yg397/media-frontend:xenial",
            "jaeger-agent": "jaegertracing/all-in-one:latest",
        }
        with tempfile.TemporaryDirectory() as directory:
            adapter = Adapter(Context(Path(directory)))
            social = adapter.source / "socialNetwork"
            for relative in ("config", "nginx-web-server", "gen-lua", "media-frontend", "docker/openresty-thrift/lua-thrift"):
                (social / relative).mkdir(parents=True, exist_ok=True)
            (social / "config" / "jaeger-config.yml").write_text("disabled: false\n", encoding="utf-8")
            (social / "config" / "service-config.json").write_text(json.dumps({
                "user-timeline-mongodb": {"addr": "user-timeline-mongodb", "port": 27017},
                "user-timeline-redis": {"addr": "user-timeline-redis", "port": 6379},
                "post-storage-service": {"addr": "post-storage-service", "port": 9090},
            }), encoding="utf-8")
            (social / "nginx-web-server" / "jaeger-config.json").write_text('{"diabled": false}', encoding="utf-8")
            services = {name: {"image": image} for name, image in images.items()}
            services["user-timeline-service"].update({
                "hostname": "user-timeline-service", "entrypoint": "UserTimelineService",
                "depends_on": {"jaeger-agent": {"condition": "service_started"}, "user-timeline-mongodb": {"condition": "service_started"}},
                "volumes": ["./config:/social-network-microservices/config"],
            })
            (social / "docker-compose.yml").write_text(yaml.safe_dump({"version": "3.9", "services": services}), encoding="utf-8")
            adapter._render()
            node_a = yaml.safe_load((adapter.node_dirs["a"] / "docker-compose.yml").read_text(encoding="utf-8"))
            node_b = yaml.safe_load((adapter.node_dirs["b"] / "docker-compose.yml").read_text(encoding="utf-8"))
            node_b_config = json.loads((adapter.node_dirs["b"] / "config" / "service-config.json").read_text(encoding="utf-8"))
        self.assertEqual(node_a["services"]["user-timeline-service"]["networks"]["app"]["ipv4_address"], "172.28.11.40")
        self.assertIn("user-timeline-service-replica-a", node_a["services"])
        self.assertEqual(node_a["services"]["user-timeline-service-replica-a"]["ports"], ["19090:9090"])
        self.assertEqual(list(node_b["services"]), ["user-timeline-service-replica-b"])
        self.assertEqual(node_b["services"]["user-timeline-service-replica-b"]["ports"], ["19090:9090"])
        self.assertEqual(node_a["services"]["user-timeline-mongodb"]["ports"], ["37020:27017"])
        self.assertEqual(node_b_config["user-timeline-mongodb"], {"addr": "192.0.2.1", "port": 37020})
        addresses = [spec["networks"]["app"]["ipv4_address"] for spec in node_a["services"].values()]
        self.assertEqual(len(addresses), len(set(addresses)))

    def test_timeline_oracle_accepts_only_pinned_shapes(self):
        self.assertFalse(Adapter._valid_timeline(b"{}", "fixture"))
        self.assertTrue(Adapter._valid_timeline(json.dumps([{"post_id": "1", "text": "fixture"}]).encode(), "fixture"))
        self.assertFalse(Adapter._valid_timeline(json.dumps([{"post_id": "1", "text": "other"}]).encode(), "fixture"))
        self.assertFalse(Adapter._valid_timeline(b'{"post_id":"1","text":"fixture"}', "fixture"))
        self.assertFalse(Adapter._valid_timeline(json.dumps([{"post_id": 1, "text": "fixture"}]).encode(), "fixture"))
        self.assertFalse(Adapter._valid_timeline(b"not json", "fixture"))

    def test_deadline_uses_monotonic_elapsed_time(self):
        self.assertTrue(Adapter._within_deadline(1_000, 2_000_000_000, 2.0))
        self.assertFalse(Adapter._within_deadline(1_000, 2_000_001_001, 2.0))

    def test_late_response_fails_and_wire_identity_is_opaque(self):
        class Context:
            mode = "full"
            seed = 0

            def __init__(self, root):
                self.deployment_dir = root / "deployment"
                self.out = root

            @staticmethod
            def node_ip(_node):
                return "192.0.2.1"

        class Response:
            ok = True
            status_code = 200
            content = b"Successfully upload post"

        with tempfile.TemporaryDirectory() as directory:
            adapter = Adapter(Context(Path(directory)))
            with mock.patch("systems.deathstarbench.adapter.requests.request", return_value=Response()) as request:
                with mock.patch("systems.deathstarbench.adapter.time.monotonic_ns", side_effect=[0, 1_900_000_000, 2_100_000_001]):
                    with mock.patch("systems.deathstarbench.adapter.time.time_ns", side_effect=[10, 20]):
                        record = adapter.operation("compose_post", 7, "secret-operation-label", deadline=2.0)
        self.assertFalse(record["success"])
        step = record["http_steps"][0]
        self.assertFalse(step["within_deadline"])
        self.assertEqual(step["request_id"], step["request_headers"]["X-Experiment-Request-Id"])
        self.assertTrue(step["request_id"].startswith("req-"))
        self.assertNotIn("secret-operation-label", step["url"])
        self.assertNotIn("secret-operation-label", json.dumps(step["request_headers"]))
        self.assertNotIn("uber-trace-id", {key.lower() for key in step["request_headers"]})

    def test_verification_after_control_change_is_unknown_and_nonmutating(self):
        class Context:
            mode = "full"
            seed = 0

            def __init__(self, root):
                self.deployment_dir = root / "deployment"
                self.out = root

            @staticmethod
            def node_ip(_node):
                return "192.0.2.1"

        source = [{
            "operation": "compose_post", "success": True, "ended_ns": 1,
            "http_steps": [{"request_id": "req-abc"}],
            "validation": {"control_epoch": 0},
        }]
        with tempfile.TemporaryDirectory() as directory:
            adapter = Adapter(Context(Path(directory)))
            adapter._control_epoch = 1
            verified = adapter.verify(source)
        self.assertNotIn("eventual_postcondition", source[0])
        self.assertIsNone(verified[0]["eventual_postcondition"]["success"])
        self.assertEqual(verified[0]["eventual_postcondition"]["unknown_reason"], "control state changed before verification")


class DeepFlowFallbackTests(unittest.TestCase):
    def test_two_node_standalone_lifecycle_and_raw_manifest(self):
        class Context:
            def __init__(self):
                self.commands = []

            def node_exec(self, node, command, timeout=300, check=True):
                self.commands.append((node, command))
                if "mktemp -d" in command:
                    return SimpleNamespace(returncode=0, stdout=f"/opt/ebpf-study/deepflow-fallback.{node}12345\n", stderr="")
                if "docker inspect -f" in command:
                    return SimpleNamespace(returncode=0, stdout="true\n", stderr="")
                if "grep -h -E" in command:
                    return SimpleNamespace(returncode=0, stdout="Start dispatcher 0\n", stderr="")
                if command.startswith("find "):
                    return SimpleNamespace(returncode=0, stdout="l4_flow_log\n", stderr="")
                return SimpleNamespace(returncode=0, stdout="{}\n", stderr="")

            def node_put(self, node, source, destination):
                self.commands.append((node, f"put {source} {destination}"))

            def node_get(self, node, source, destination):
                destination = Path(destination)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(f"raw-{node}\n", encoding="utf-8")

        context = Context()
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch("systems.deathstarbench.deepflow_fallback.time.sleep"):
                handle = fallback(context, object(), Path(directory))
            output = handle.collect()
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        runs = [command for _, command in context.commands if command.startswith("docker run")]
        self.assertEqual(len(runs), 2)
        self.assertTrue(all("--standalone" in command and "--network=host" in command for command in runs))
        self.assertTrue(all(DEEPFLOW_IMAGE in command for command in runs))
        self.assertIn("proactive_request_interval: 10s", CONFIG)
        self.assertEqual(manifest["status"], "collected")
        self.assertTrue(manifest["interpretation"]["raw_only"])
        self.assertFalse(manifest["interpretation"]["thrift_supported_by_v7_2_3_builtin_l7_enum"])
        self.assertEqual(manifest["resource_limit_per_node"]["memory_mib"], 1024)
        self.assertTrue(any(item["path"].endswith("l4_flow_log") for item in manifest["files"]))
