"""Two-guest adapter for OpenTelemetry Demo 3.0.0.

The workload calls are derived from SIMPAT's Apache-2.0-licensed live pilot
(`telemetry_availability/live_pilot.py`).  Deployment and evaluator code here is
new; upstream OpenTelemetry Demo files remain unmodified and retain their own
Apache-2.0 notices.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import re
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import requests
import yaml


UPSTREAM_URL = "https://github.com/open-telemetry/opentelemetry-demo.git"
UPSTREAM_COMMIT = "8c47d47c9ac27710d2b2a153bcd53e483bffe66d"
DEMO_VERSION = "3.0.0"
PRODUCT_ID = "OLJCESPC7Z"
REMOTE_ROOT = "/opt/ebpf-study/otel_demo"
PROJECT = "ebpf-otel-demo"

ENTRY_IP = "172.28.11.10"
ROUTER_IP = "172.28.11.20"
REPLICA_A_IP = "172.28.11.21"
REPLICA_B_IP = "172.28.12.21"
COLLECTOR_IP = "172.28.11.30"
DATABASE_IP = "172.28.11.31"
KAFKA_IP = "172.28.11.32"
ACCOUNTING_IP = "172.28.11.33"
DATABASE_GUEST_PORT = 15432
COLLECTOR_GUEST_PORT = 14317
FLAGD_GUEST_PORT = 18013
REPLICA_B_GUEST_PORT = 13550

OPERATIONS = ("browse_product", "add_to_cart", "checkout")
DROP_SERVICES = {"load-generator", "fraud-detection", "flagd-ui", "telemetry-docs"}
_ORDER_ID = re.compile(r"^[A-Za-z0-9._:-]{1,200}$")
_ENV = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:(:-|-)([^}]*))?\}")


class Adapter:
    """OpenTelemetry Demo implementation of the system adapter contract."""

    def __init__(self, context: Any):
        self.ctx = context
        self.mode = str(context.mode)
        if self.mode not in {"absent", "partial", "full"}:
            raise ValueError(f"invalid tracing mode: {self.mode!r}")
        self.bundle = Path(context.deployment_dir) / "otel_demo"
        self.source = self.bundle / "source"
        self.entry_url = f"http://{ENTRY_IP}:8080"
        self._consumer_paused = False
        self._latest_async_deadline_ns = 0
        self._deadline_lock = threading.Lock()

    # --------------------------- deployment generation --------------------

    def prepare(self) -> None:
        """Fetch the pinned source and create fully recorded guest assets."""
        self.bundle.mkdir(parents=True, exist_ok=True)
        if self.source.exists():
            observed = self._run_stdout(
                ["git", "-C", str(self.source), "rev-parse", "HEAD"]
            ).strip()
            if observed != UPSTREAM_COMMIT:
                shutil.rmtree(self.source)
        if not self.source.exists():
            self.ctx.run(
                [
                    "git",
                    "clone",
                    "--filter=blob:none",
                    "--no-checkout",
                    UPSTREAM_URL,
                    str(self.source),
                ],
                timeout=600,
            )
            self.ctx.run(
                ["git", "-C", str(self.source), "checkout", "--detach", UPSTREAM_COMMIT],
                timeout=300,
            )

        observed = self._run_stdout(
            ["git", "-C", str(self.source), "rev-parse", "HEAD"]
        ).strip()
        if observed != UPSTREAM_COMMIT:
            raise RuntimeError(f"upstream checkout is {observed}, expected {UPSTREAM_COMMIT}")

        patch_record = self._patch_native_disable()

        environment = self._read_env(self.source / ".env")
        environment["DEMO_VERSION"] = DEMO_VERSION
        environment["IMAGE_VERSION"] = DEMO_VERSION
        base = yaml.safe_load((self.source / "compose.yaml").read_text(encoding="utf-8"))
        full = yaml.safe_load((self.source / "compose.full.yaml").read_text(encoding="utf-8"))
        merged = self._compose_merge(base, full)
        merged = self._expand(merged, environment)
        self._resolve_environment_values(merged, environment)
        node_a, node_b, mapping = self._split_compose(merged)

        self._write_yaml(self.bundle / "node-a.yaml", node_a)
        self._write_yaml(self.bundle / "node-b.yaml", node_b)
        (self.bundle / "envoy-product-router.yaml").write_text(
            self._envoy_config(), encoding="utf-8"
        )
        (self.bundle / "otel-collector.yaml").write_text(
            self._collector_config(), encoding="utf-8"
        )
        (self.bundle / "native").mkdir(exist_ok=True)
        manifest = {
            "upstream": UPSTREAM_URL,
            "commit": UPSTREAM_COMMIT,
            "demo_version": DEMO_VERSION,
            "mode": self.mode,
            "compose_layers": ["compose.yaml", "compose.full.yaml"],
            "placement": mapping,
            "native_suppression": self._suppression_description(),
            "native_disable_patch": patch_record,
            "native_request_id_capture": {
                "header": "x-experiment-request-id",
                "entry_service": "frontend",
                "configuration": [
                    "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST",
                    "OTEL_INSTRUMENTATION_HTTP_SERVER_CAPTURE_REQUEST_HEADERS",
                ],
                "status": "requested from the frontend Node HTTP instrumentation; observed support is recorded by collect_native",
            },
        }
        (self.bundle / "deployment-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (self.bundle / "container-ip-mapping.json").write_text(
            json.dumps(
                {
                    "node_a_subnet": "172.28.11.0/24",
                    "node_b_subnet": "172.28.12.0/24",
                    "services": mapping,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def deploy(self) -> None:
        """Copy assets, pull pinned application images, and start both guests."""
        if not (self.bundle / "node-a.yaml").exists():
            raise RuntimeError("prepare() must run before deploy()")
        for node in ("a", "b"):
            self.ctx.node_exec(
                node,
                f"sudo rm -rf {REMOTE_ROOT} && sudo mkdir -p /opt/ebpf-study && "
                f"sudo chown -R $(id -u):$(id -g) /opt/ebpf-study",
            )
            self.ctx.node_put(node, self.bundle, REMOTE_ROOT)

        # Infrastructure and the fixed router endpoint live on A.  B then adds
        # the second product-catalog process without changing routing policy.
        self._compose("a", "pull --ignore-buildable", timeout=1200)
        self._compose("b", "pull --ignore-buildable", timeout=600)
        # Services with direct SDK/exporter construction are built from the
        # pinned, recorded source patch. Builds happen only in Actions guests.
        self._compose("a", "build checkout email product-catalog-a", timeout=1800)
        self._compose("b", "build product-catalog-b", timeout=1800)
        self._compose("a", "up -d --remove-orphans", timeout=900)
        self._compose("b", "up -d --remove-orphans", timeout=600)

        for node, filename in (("a", "node-a.yaml"), ("b", "node-b.yaml")):
            rendered = self.ctx.node_exec(
                node,
                f"cd {REMOTE_ROOT} && docker compose -p {PROJECT} -f {filename} config",
            )
            (self.bundle / f"runtime-resolved-{filename}").write_text(
                self._stdout(rendered), encoding="utf-8"
            )
            images = self.ctx.node_exec(
                node,
                f"cd {REMOTE_ROOT} && for image in $(docker compose -p {PROJECT} -f {filename} config --images | sort -u); do "
                "docker image inspect --format '{{.Id}} {{json .RepoDigests}}' \"$image\" | sed \"s#^#$image #\"; done",
            )
            (self.bundle / f"resolved-images-{node}.txt").write_text(
                self._stdout(images), encoding="utf-8"
            )

        suppression = json.dumps(self._suppression_description(), sort_keys=True)
        self.ctx.node_exec(
            "a",
            f"printf '%s\\n' {self._shquote(suppression)} > {REMOTE_ROOT}/native/suppression.json",
        )

    def ready(self) -> None:
        """Wait boundedly for HTTP and independently confirm the SQL fixture."""
        end = time.monotonic() + 180
        last_error = "not attempted"
        while time.monotonic() < end:
            try:
                response = requests.get(
                    f"{self.entry_url}/api/products/{PRODUCT_ID}", timeout=3
                )
                if response.status_code == 200 and response.json().get("id") == PRODUCT_ID:
                    break
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            except Exception as exc:  # readiness must retain the last real cause
                last_error = repr(exc)
            time.sleep(2)
        else:
            raise RuntimeError(f"OpenTelemetry Demo did not become ready: {last_error}")

        query = (
            "SELECT count(*) FROM catalog.products WHERE id='OLJCESPC7Z';"
            " SELECT to_regclass('accounting.order') IS NOT NULL;"
        )
        result = self._psql(query)
        if "1" not in result or "t" not in result:
            raise RuntimeError(f"database fixtures/schema are incomplete: {result!r}")
        self._wait_collector_ready()

    # --------------------------- contract metadata -------------------------

    def metadata(self) -> dict[str, Any]:
        return {
            "system": "otel_demo",
            "operations": list(OPERATIONS),
            "entry_url": self.entry_url,
            "replicas": [
                {"name": "product-catalog-a", "node": "a", "ip": REPLICA_A_IP},
                {
                    "name": "product-catalog-b",
                    "node": "b",
                    "ip": REPLICA_B_IP,
                    "transport_host": self.ctx.node_ip("b"),
                    "transport_port": REPLICA_B_GUEST_PORT,
                },
            ],
            "routing": {
                "name": "product-catalog",
                "node": "a",
                "ip": ROUTER_IP,
                "policy": "envoy round_robin with active gRPC endpoint health checks",
            },
            "database": {
                "logical_identity": "astronomy_db/catalog.products",
                "node": "a",
                "container": "astronomy-db",
                "ip": DATABASE_IP,
                "transport_host": self.ctx.node_ip("a"),
                "transport_port": DATABASE_GUEST_PORT,
            },
            "async_evaluator_database": {
                "logical_identity": "astronomy_db/accounting",
                "node": "a",
                "container": "astronomy-db",
                "ip": DATABASE_IP,
                "transport_host": self.ctx.node_ip("a"),
                "transport_port": DATABASE_GUEST_PORT,
            },
            "source": {
                "url": UPSTREAM_URL,
                "commit": UPSTREAM_COMMIT,
                "version": DEMO_VERSION,
                "compose_layers": ["compose.yaml", "compose.full.yaml"],
            },
            "images": {
                "application_prefix": f"ghcr.io/open-telemetry/demo:{DEMO_VERSION}-",
                "resolved_digests": [
                    "deployment/otel_demo/resolved-images-a.txt",
                    "deployment/otel_demo/resolved-images-b.txt",
                ],
            },
            "native_export_locations": {
                "traces": "node a:/opt/ebpf-study/otel_demo/native/traces.json",
                "otel_logs": "node a:/opt/ebpf-study/otel_demo/native/otel-logs.json",
                "metrics": "node a:/opt/ebpf-study/otel_demo/native/metrics.json",
                "container_logs": "collect_native destination/application-logs/",
            },
            "native_suppression": self._suppression_description(),
        }

    # --------------------------- state controls ----------------------------

    def reset(self) -> None:
        self.set_database(True)
        self.set_replicas("11")
        self.set_consumer(True)
        self.ctx.node_exec("a", "docker exec valkey-cart valkey-cli FLUSHALL")
        self._psql(
            'TRUNCATE accounting.orderitem, accounting.shipping, accounting."order";'
        )
        self.ready()

    def set_replicas(self, state: str) -> None:
        if state not in {"11", "10", "01", "00"}:
            raise ValueError(f"replica state must be 11, 10, 01, or 00; got {state!r}")
        for node, service, bit in (
            ("a", "product-catalog-a", state[0]),
            ("b", "product-catalog-b", state[1]),
        ):
            action = f"start {service}" if bit == "1" else f"stop -t 10 {service}"
            self._compose(node, action, timeout=60)
        # Envoy is deliberately never reconfigured by a fault transition.
        time.sleep(2)

    def set_database(self, up: bool) -> None:
        self._compose("a", "start astronomy-db" if up else "stop -t 10 astronomy-db", timeout=60)
        if up:
            self._wait_container_healthy("a", "astronomy-db", 90)

    def set_consumer(self, up: bool) -> None:
        if not up:
            self._compose("a", "stop -t 20 accounting", timeout=60)
            self._consumer_paused = True
            return

        # A recovery transition may not release the consumer before the last
        # independently defined 10-second evaluator window has elapsed.
        was_paused = self._consumer_paused
        with self._deadline_lock:
            latest_deadline_ns = self._latest_async_deadline_ns
        remaining = (latest_deadline_ns - time.time_ns()) / 1e9
        if was_paused and remaining > 0:
            time.sleep(remaining)
        self._compose("a", "start accounting", timeout=60)
        self._consumer_paused = False
        if was_paused:
            self._wait_consumer_drain(60)

    # --------------------------- workload/evaluation -----------------------

    def operation(
        self, name: str, index: int, namespace: str, deadline: float = 2.0
    ) -> dict[str, Any]:
        if name not in OPERATIONS:
            raise ValueError(f"unsupported operation {name!r}")
        attempt_id = f"{namespace}-{name}-{index}-{uuid.uuid4().hex[:12]}"
        fixture_token = uuid.uuid4().hex
        user_id = f"u-{fixture_token}"
        record: dict[str, Any] = {
            "operation": name,
            "attempt_id": attempt_id,
            "started_ns": time.time_ns(),
            "ended_ns": None,
            "success": False,
            "http_steps": [],
            "error": None,
            "deadline_seconds": deadline,
        }
        operation_deadline = time.monotonic() + deadline

        def remaining() -> float:
            value = operation_deadline - time.monotonic()
            if value <= 0:
                raise TimeoutError(f"operation exceeded {deadline:.3f}s deadline")
            return value

        try:
            if name == "browse_product":
                product = self._http_step(
                    record,
                    "GET",
                    f"/api/products/{PRODUCT_ID}",
                    remaining(),
                )
                record["success"] = product["status"] == 200
            elif name == "add_to_cart":
                product = self._http_step(
                    record, "GET", f"/api/products/{PRODUCT_ID}", remaining()
                )
                if product["status"] != 200:
                    raise RuntimeError("product prerequisite failed")
                cart = self._http_step(
                    record,
                    "POST",
                    "/api/cart",
                    remaining(),
                    {"userId": user_id, "item": {"productId": PRODUCT_ID, "quantity": 1}},
                )
                record["success"] = cart["status"] == 200
                record["user_id"] = user_id
            else:
                product = self._http_step(
                    record, "GET", f"/api/products/{PRODUCT_ID}", remaining()
                )
                if product["status"] != 200:
                    raise RuntimeError("product prerequisite failed")
                cart = self._http_step(
                    record,
                    "POST",
                    "/api/cart",
                    remaining(),
                    {"userId": user_id, "item": {"productId": PRODUCT_ID, "quantity": 1}},
                )
                if cart["status"] != 200:
                    raise RuntimeError("cart prerequisite failed")
                checkout = self._http_step(
                    record,
                    "POST",
                    "/api/checkout?currencyCode=USD",
                    remaining(),
                    {
                        "userId": user_id,
                        "email": f"{fixture_token}@example.invalid",
                        "address": {
                            "streetAddress": "1 Observatory Way",
                            "city": "Testville",
                            "state": "CA",
                            "country": "US",
                            "zipCode": "94000",
                        },
                        "userCurrency": "USD",
                        "creditCard": {
                            "creditCardNumber": "4432801561520454",
                            "creditCardCvv": 672,
                            "creditCardExpirationYear": 2039,
                            "creditCardExpirationMonth": 1,
                        },
                    },
                )
                payload = checkout.get("json") if isinstance(checkout.get("json"), dict) else {}
                order_id = payload.get("orderId") or payload.get("order_id")
                record["order_id"] = order_id
                record["user_id"] = user_id
                record["async_expected"] = {
                    "items": [{"product_id": PRODUCT_ID, "quantity": 1}],
                    "shipping_address": {
                        "street_address": "1 Observatory Way",
                        "city": "Testville",
                        "state": "CA",
                        "country": "US",
                        "zip_code": "94000",
                    },
                }
                # Sarama uses RequiredAcks=NoResponse upstream.  This is only
                # immediate HTTP success; Kafka delivery is never inferred here.
                record["success"] = checkout["status"] == 200 and bool(order_id)
        except Exception as exc:
            record["error"] = str(exc)
            record["success"] = False
        finally:
            record["ended_ns"] = time.time_ns()
            if name == "checkout" and self._consumer_paused:
                # Reserve the protocol's default durable deadline immediately;
                # this prevents an eager recovery transition from releasing the
                # paused consumer before verify_async receives the records.
                self._reserve_async_deadline(record["started_ns"] + 10_000_000_000)
            if time.monotonic() > operation_deadline:
                record["success"] = False
                record["error"] = record["error"] or f"operation exceeded {deadline:.3f}s deadline"
        return record

    def verify(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        verified: list[dict[str, Any]] = []
        for original in records:
            record = copy.deepcopy(original)
            last = record.get("http_steps", [])[-1:] or [{}]
            payload = last[0].get("json") if isinstance(last[0].get("json"), dict) else {}
            operation = record.get("operation")
            if operation == "browse_product":
                postcondition = payload.get("id") == PRODUCT_ID
            elif operation == "add_to_cart":
                items = payload.get("items", [])
                postcondition = any(
                    item.get("productId") == PRODUCT_ID and item.get("quantity") == 1
                    for item in items
                    if isinstance(item, dict)
                )
            elif operation == "checkout":
                postcondition = bool(record.get("order_id"))
            else:
                postcondition = None
            record["payload_postcondition"] = postcondition
            record["success"] = (
                bool(record.get("success") and postcondition)
                if postcondition is not None
                else None
            )
            verified.append(record)
        return verified

    def verify_async(
        self, records: list[dict[str, Any]], deadline: float = 10.0
    ) -> list[dict[str, Any]]:
        """Poll independent SQL state, preserving every timestamped observation."""
        results: list[dict[str, Any]] = []
        for original in records:
            record = copy.deepcopy(original)
            order_id = record.get("order_id")
            started_ns = int(record.get("started_ns") or time.time_ns())
            deadline_ns = started_ns + int(deadline * 1_000_000_000)
            self._reserve_async_deadline(deadline_ns)
            observations: list[dict[str, Any]] = []
            settled: bool | None = None
            if not isinstance(order_id, str) or not _ORDER_ID.fullmatch(order_id):
                record["async_error"] = "missing or unsafe order_id"
            else:
                while True:
                    observation = self._read_order(order_id)
                    observations.append(observation)
                    if observation.get("complete") is True:
                        # A first positive observation after the boundary does
                        # not establish when persistence happened.
                        completed_ns = int(
                            observation.get("query_completed_ns") or time.time_ns()
                        )
                        settled = True if completed_ns <= deadline_ns else None
                        break
                    now_ns = time.time_ns()
                    if now_ns >= deadline_ns:
                        # A negative snapshot that began before the boundary
                        # cannot exclude a commit between snapshot and deadline.
                        query_started_ns = int(
                            observation.get("query_started_ns") or 0
                        )
                        settled = (
                            False
                            if observation.get("query_ok")
                            and query_started_ns >= deadline_ns
                            else None
                        )
                        break
                    time.sleep(min(0.4, max(0.0, (deadline_ns - now_ns) / 1e9)))
            record["async_verification"] = {
                "deadline_seconds": deadline,
                "deadline_ns": deadline_ns,
                "success": settled,
                "observations": observations,
                "evidence": "independent PostgreSQL reads keyed only by returned order_id",
                "expected_postcondition": record.get("async_expected")
                or {
                    "items": [{"product_id": PRODUCT_ID, "quantity": 1}],
                    "shipping_address": {
                        "street_address": "1 Observatory Way",
                        "city": "Testville",
                        "state": "CA",
                        "country": "US",
                        "zip_code": "94000",
                    },
                },
            }
            results.append(record)
        return results

    # --------------------------- evidence lifecycle ------------------------

    def collect_native(self, destination: Path) -> None:
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "application-logs").mkdir(exist_ok=True)

        snapshot_started_ns = time.time_ns()
        self.ctx.node_exec("a", "docker stop -t 20 otel-collector")
        collector_flushed_ns = time.time_ns()
        try:
            for filename in ("traces.json", "otel-logs.json", "metrics.json", "suppression.json"):
                self._copy_remote_file(
                    "a", f"{REMOTE_ROOT}/native/{filename}", destination / filename
                )
        finally:
            # File exporter output is bind-mounted and append-preserving.  A
            # calibration snapshot must not leave the collector stopped while
            # target observations are acquired.
            self._compose("a", "start otel-collector", timeout=60)
            self._wait_collector_ready()
        collector_restarted_ns = time.time_ns()
        (destination / "snapshot-lifecycle.json").write_text(
            json.dumps(
                {
                    "snapshot_started_ns": snapshot_started_ns,
                    "collector_flushed_ns": collector_flushed_ns,
                    "collector_restarted_ns": collector_restarted_ns,
                    "remote_files_preserved": True,
                    "subsequent_export_mode": "append",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        for node, compose_file in (("a", "node-a.yaml"), ("b", "node-b.yaml")):
            listing = self.ctx.node_exec(
                node,
                f"cd {REMOTE_ROOT} && docker compose -p {PROJECT} -f {compose_file} ps -a --format json",
            )
            (destination / f"compose-ps-{node}.jsonl").write_text(
                self._stdout(listing), encoding="utf-8"
            )
            names = self.ctx.node_exec(
                node,
                f"cd {REMOTE_ROOT} && docker compose -p {PROJECT} -f {compose_file} ps -a --format '{{{{.Name}}}}'",
            )
            for name in filter(None, self._stdout(names).splitlines()):
                safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
                logs = self.ctx.node_exec(node, f"docker logs --timestamps {self._shquote(name)} 2>&1 || true")
                (destination / "application-logs" / f"{node}-{safe}.log").write_text(
                    self._stdout(logs), encoding="utf-8", errors="replace"
                )

        traces = destination / "traces.json"
        verification = self._verify_native_file(traces)
        (destination / "native-suppression-verification.json").write_text(
            json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if not verification["mode_compliant"]:
            raise RuntimeError(f"native trace suppression check failed: {verification}")

    def close(self) -> None:
        diagnostics = Path(self.ctx.out) / "otel_demo-diagnostics"
        diagnostics.mkdir(parents=True, exist_ok=True)
        for node, compose_file in (("a", "node-a.yaml"), ("b", "node-b.yaml")):
            result = self.ctx.node_exec(
                node,
                f"cd {REMOTE_ROOT} && docker compose -p {PROJECT} -f {compose_file} ps -a",
            )
            (diagnostics / f"compose-ps-{node}.txt").write_text(
                self._stdout(result), encoding="utf-8"
            )
        self._compose("b", "down -v --remove-orphans", timeout=180, check=False)
        self._compose("a", "down -v --remove-orphans", timeout=240, check=False)

    # --------------------------- private helpers ---------------------------

    def _split_compose(self, document: dict[str, Any]) -> tuple[dict, dict, dict]:
        services = copy.deepcopy(document["services"])
        for name in list(services):
            if name in DROP_SERVICES:
                services.pop(name)
        for name, service in services.items():
            if name in {"checkout", "email", "product-catalog"}:
                self._prefix_source_build(service)
                service["image"] = (
                    f"ebpf-study/otel-demo-{name}:{UPSTREAM_COMMIT[:12]}-{self.mode}"
                )
            else:
                service.pop("build", None)
            service.pop("ports", None)
            service.pop("profiles", None)
            depends = service.get("depends_on")
            if isinstance(depends, dict):
                service["depends_on"] = {
                    key: value for key, value in depends.items() if key in services
                }
            elif isinstance(depends, list):
                service["depends_on"] = [key for key in depends if key in services]
            service["environment"] = self._environment_dict(service.get("environment", {}))
            self._prefix_source_mounts(service)

        product = services.pop("product-catalog")
        product_a = self._configure_product(product, "a")
        product_a["container_name"] = "product-catalog-a"
        services["product-catalog-a"] = product_a
        services["product-catalog"] = {
            "image": services["frontend-proxy"]["image"],
            "container_name": "product-catalog-router",
            "restart": "unless-stopped",
            "entrypoint": ["envoy"],
            "command": ["-c", "/etc/envoy/product-router.yaml"],
            "volumes": [
                "./envoy-product-router.yaml:/etc/envoy/product-router.yaml:ro"
            ],
            "healthcheck": {
                "test": ["CMD", "bash", "-c", "echo > /dev/tcp/127.0.0.1/3550"],
                "start_period": "5s",
                "interval": "2s",
                "timeout": "2s",
                "retries": 30,
            },
        }

        # The study collector replaces the demo's debug/metrics collector and
        # writes the three signal types to provenance-separated files.
        collector = services["otel-collector"]
        collector["command"] = ["--config=/etc/otelcol-study.yaml"]
        collector["volumes"] = [
            "./otel-collector.yaml:/etc/otelcol-study.yaml:ro",
            "./native:/native",
        ]
        collector["user"] = "0:0"

        # Cross-guest traffic uses explicit guest-published endpoints. Docker
        # bridge addresses are evidence identities, not assumed routable links.
        services["astronomy-db"]["ports"] = [f"{DATABASE_GUEST_PORT}:5432"]
        services["otel-collector"]["ports"] = [f"{COLLECTOR_GUEST_PORT}:4317"]
        services["flagd"]["ports"] = [f"{FLAGD_GUEST_PORT}:8013"]

        # Standard language SDKs get their specified master disable switch.
        # Checkout and product-catalog additionally have explicit source guards
        # because their custom provider construction can bypass env handling.
        for name, service in services.items():
            if name in {"otel-collector", "product-catalog"}:
                continue
            disabled = self.mode == "absent" or (
                self.mode == "partial" and name == "product-catalog-a"
            )
            if disabled:
                env = service.setdefault("environment", {})
                env.update(
                    {"OTEL_SDK_DISABLED": "true"}
                )

        # The frontend is the first instrumented HTTP application hop.  Node's
        # current and legacy-contrib variable names are both supplied because
        # support differs by instrumentation generation.  No traceparent is
        # injected; the opaque header remains the only experiment alignment ID.
        frontend_env = services["frontend"].setdefault("environment", {})
        frontend_env.update(
            {
                "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST": "x-experiment-request-id",
                "OTEL_INSTRUMENTATION_HTTP_SERVER_CAPTURE_REQUEST_HEADERS": "x-experiment-request-id",
            }
        )

        preferred = {
            "frontend-proxy": ENTRY_IP,
            "product-catalog": ROUTER_IP,
            "product-catalog-a": REPLICA_A_IP,
            "otel-collector": COLLECTOR_IP,
            "astronomy-db": DATABASE_IP,
            "kafka": KAFKA_IP,
            "accounting": ACCOUNTING_IP,
        }
        next_host = 40
        placement: dict[str, Any] = {}
        for name in sorted(services):
            ip = preferred.get(name)
            if ip is None:
                ip = f"172.28.11.{next_host}"
                next_host += 1
            services[name]["networks"] = {"default": {"ipv4_address": ip}}
            placement[name] = {"node": "a", "ip": ip}

        node_a = {
            "name": PROJECT,
            "services": services,
            "networks": {
                "default": {"ipam": {"config": [{"subnet": "172.28.11.0/24"}]}}
            },
        }
        for top_level in ("volumes", "configs", "secrets"):
            if document.get(top_level):
                node_a[top_level] = copy.deepcopy(document[top_level])

        product_b = self._configure_product(product, "b")
        product_b["container_name"] = "product-catalog-b"
        product_b["networks"] = {"default": {"ipv4_address": REPLICA_B_IP}}
        product_b.pop("depends_on", None)
        product_b["ports"] = [f"{REPLICA_B_GUEST_PORT}:3550"]
        node_a_host = self.ctx.node_ip("a")
        product_b["environment"].update(
            {
                "DB_CONNECTION_STRING": (
                    "postgres://astronomy_user:astronomy_password@"
                    f"{node_a_host}:{DATABASE_GUEST_PORT}/astronomy_db?sslmode=disable"
                ),
                "OTEL_EXPORTER_OTLP_ENDPOINT": (
                    f"http://{node_a_host}:{COLLECTOR_GUEST_PORT}"
                ),
                "FLAGD_HOST": node_a_host,
                "FLAGD_PORT": str(FLAGD_GUEST_PORT),
            }
        )
        node_b = {
            "name": PROJECT,
            "services": {"product-catalog-b": product_b},
            "networks": {
                "default": {"ipam": {"config": [{"subnet": "172.28.12.0/24"}]}}
            },
        }
        placement["product-catalog-b"] = {
            "node": "b",
            "ip": REPLICA_B_IP,
            "transport_host": self.ctx.node_ip("b"),
            "transport_port": REPLICA_B_GUEST_PORT,
        }
        return node_a, node_b, placement

    def _configure_product(self, source: dict[str, Any], node: str) -> dict[str, Any]:
        service = copy.deepcopy(source)
        service.pop("ports", None)
        service["environment"] = self._environment_dict(service.get("environment", {}))
        disabled = self.mode in {"absent", "partial"}
        if disabled:
            service["environment"].update(
                {"OTEL_SDK_DISABLED": "true"}
            )
        return service

    def _collector_config(self) -> str:
        processors: dict[str, Any] = {"batch": {"send_batch_size": 256, "timeout": "1s"}}
        trace_processors = ["batch"]
        config = {
            "receivers": {
                "otlp": {
                    "protocols": {
                        "grpc": {"endpoint": "0.0.0.0:4317"},
                        "http": {"endpoint": "0.0.0.0:4318"},
                    }
                }
            },
            "processors": processors,
            "exporters": {
                "file/traces": {"path": "/native/traces.json"},
                "file/logs": {"path": "/native/otel-logs.json"},
                "file/metrics": {"path": "/native/metrics.json"},
            },
            "service": {
                "pipelines": {
                    "traces": {
                        "receivers": ["otlp"],
                        "processors": trace_processors,
                        "exporters": ["file/traces"],
                    },
                    "logs": {
                        "receivers": ["otlp"],
                        "processors": ["batch"],
                        "exporters": ["file/logs"],
                    },
                    "metrics": {
                        "receivers": ["otlp"],
                        "processors": ["batch"],
                        "exporters": ["file/metrics"],
                    },
                }
            },
        }
        return yaml.safe_dump(config, sort_keys=False)

    def _envoy_config(self) -> str:
        config = {
            "static_resources": {
                "listeners": [
                    {
                        "name": "product_catalog_grpc",
                        "address": {
                            "socket_address": {"address": "0.0.0.0", "port_value": 3550}
                        },
                        "filter_chains": [
                            {
                                "filters": [
                                    {
                                        "name": "envoy.filters.network.http_connection_manager",
                                        "typed_config": {
                                            "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                                            "stat_prefix": "product_catalog",
                                            "codec_type": "HTTP2",
                                            "route_config": {
                                                "name": "grpc",
                                                "virtual_hosts": [
                                                    {
                                                        "name": "all",
                                                        "domains": ["*"],
                                                        "routes": [
                                                            {
                                                                "match": {"prefix": "/"},
                                                                "route": {
                                                                    "cluster": "product_catalog_replicas",
                                                                    "timeout": "2s",
                                                                },
                                                            }
                                                        ],
                                                    }
                                                ],
                                            },
                                            "http_filters": [
                                                {"name": "envoy.filters.http.router", "typed_config": {"@type": "type.googleapis.com/envoy.extensions.filters.http.router.v3.Router"}}
                                            ],
                                        },
                                    }
                                ]
                            }
                        ],
                    }
                ],
                "clusters": [
                    {
                        "name": "product_catalog_replicas",
                        "type": "STATIC",
                        "connect_timeout": "0.5s",
                        "lb_policy": "ROUND_ROBIN",
                        "http2_protocol_options": {},
                        "load_assignment": {
                            "cluster_name": "product_catalog_replicas",
                            "endpoints": [
                                {
                                    "lb_endpoints": [
                                        {"endpoint": {"address": {"socket_address": {"address": REPLICA_A_IP, "port_value": 3550}}}},
                                        {"endpoint": {"address": {"socket_address": {"address": self.ctx.node_ip("b"), "port_value": REPLICA_B_GUEST_PORT}}}},
                                    ]
                                }
                            ],
                        },
                        "health_checks": [
                            {
                                "timeout": "0.5s",
                                "interval": "1s",
                                "unhealthy_threshold": 1,
                                "healthy_threshold": 1,
                                "grpc_health_check": {},
                            }
                        ],
                    }
                ],
            },
            "admin": {
                "address": {
                    "socket_address": {"address": "0.0.0.0", "port_value": 10001}
                }
            },
        }
        return yaml.safe_dump(config, sort_keys=False)

    def _http_step(
        self,
        record: dict[str, Any],
        method: str,
        path: str,
        timeout: float,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = time.time_ns()
        request_id = uuid.uuid4().hex
        request_bytes = b"" if body is None else json.dumps(body, separators=(",", ":")).encode()
        step: dict[str, Any] = {
            "request_id": request_id,
            "method": method,
            "url": self.entry_url + path,
            "started_ns": started,
            "request_body_b64": base64.b64encode(request_bytes).decode("ascii"),
        }
        try:
            response = requests.request(
                method,
                self.entry_url + path,
                json=body,
                timeout=timeout,
                headers={"X-Experiment-Request-Id": request_id},
            )
            step.update(
                {
                    "status": response.status_code,
                    "response_body_b64": base64.b64encode(response.content).decode("ascii"),
                    "ended_ns": time.time_ns(),
                    "error": None,
                }
            )
            try:
                step["json"] = response.json()
            except ValueError:
                step["json"] = None
        except Exception as exc:
            step.update(
                {"status": None, "response_body_b64": "", "ended_ns": time.time_ns(), "error": str(exc), "json": None}
            )
            record["http_steps"].append(step)
            raise
        record["http_steps"].append(step)
        return step

    def _read_order(self, order_id: str) -> dict[str, Any]:
        query_started_ns = time.time_ns()
        escaped = order_id.replace("'", "''")
        sql = f"""
SELECT json_build_object(
  'db_observed_at', clock_timestamp(),
  'order_id', {self._sql_literal(order_id)},
  'order_count', (SELECT count(*) FROM accounting."order" WHERE order_id='{escaped}'),
  'item_count', (SELECT count(*) FROM accounting.orderitem WHERE order_id='{escaped}'),
  'shipping_count', (SELECT count(*) FROM accounting.shipping WHERE order_id='{escaped}'),
  'items', COALESCE((SELECT json_agg(json_build_object('product_id', product_id, 'quantity', quantity) ORDER BY product_id) FROM accounting.orderitem WHERE order_id='{escaped}'), '[]'::json),
  'shipping', COALESCE((SELECT json_agg(json_build_object(
    'shipping_tracking_id', shipping_tracking_id,
    'shipping_cost_currency_code', shipping_cost_currency_code,
    'shipping_cost_units', shipping_cost_units,
    'shipping_cost_nanos', shipping_cost_nanos,
    'street_address', street_address,
    'city', city,
    'state', state,
    'country', country,
    'zip_code', zip_code
  )) FROM accounting.shipping WHERE order_id='{escaped}'), '[]'::json)
);"""
        provenance = {
            "query_started_ns": query_started_ns,
            "query_text": sql.strip(),
            "query_sha256": hashlib.sha256(sql.encode("utf-8")).hexdigest(),
            "executor": "docker exec astronomy-db psql -U astronomy_user -d astronomy_db",
            "role": "evaluator_only",
        }
        try:
            raw = self._psql(sql).strip().splitlines()[-1]
            value = json.loads(raw)
            expected_items = [{"product_id": PRODUCT_ID, "quantity": 1}]
            expected_address = {
                "street_address": "1 Observatory Way",
                "city": "Testville",
                "state": "CA",
                "country": "US",
                "zip_code": "94000",
            }
            shipping = value.get("shipping") or []
            shipping_exact = (
                len(shipping) == 1
                and all(shipping[0].get(key) == expected for key, expected in expected_address.items())
                and bool(shipping[0].get("shipping_tracking_id"))
                and shipping[0].get("shipping_cost_currency_code") == "USD"
                and int(shipping[0].get("shipping_cost_units") or 0) >= 0
                and 0 <= int(shipping[0].get("shipping_cost_nanos") or 0) < 1_000_000_000
            )
            value.update(
                {
                    **provenance,
                    "runner_observed_ns": query_started_ns,
                    "query_completed_ns": time.time_ns(),
                    "query_ok": True,
                    "complete": value["order_count"] == 1
                    and value["item_count"] == 1
                    and value["shipping_count"] == 1,
                    "postcondition_exact": value.get("items") == expected_items
                    and shipping_exact,
                }
            )
            value["complete"] = bool(value["complete"] and value["postcondition_exact"])
            return value
        except Exception as exc:
            return {
                **provenance,
                "runner_observed_ns": query_started_ns,
                "query_completed_ns": time.time_ns(),
                "query_ok": False,
                "complete": None,
                "error": str(exc),
            }

    def _wait_consumer_drain(self, timeout: float) -> None:
        end = time.monotonic() + timeout
        last = ""
        while time.monotonic() < end:
            result = self.ctx.node_exec(
                "a",
                "docker exec kafka sh -lc \"kafka-consumer-groups.sh --bootstrap-server kafka:9092 --group accounting --describe 2>/dev/null || true\"",
            )
            last = self._stdout(result)
            lags = []
            for line in last.splitlines():
                fields = line.split()
                if len(fields) >= 6 and fields[0] == "accounting":
                    try:
                        lags.append(int(fields[5]))
                    except ValueError:
                        pass
            if lags and sum(lags) == 0:
                return
            time.sleep(1)
        raise RuntimeError(f"accounting did not drain Kafka backlog: {last[-1000:]}")

    def _reserve_async_deadline(self, deadline_ns: int) -> None:
        # Async-control attempts are verified concurrently; never let a racing
        # earlier attempt shorten the consumer pause reserved by a later one.
        lock = getattr(self, "_deadline_lock", None)
        if lock is None:  # supports focused unit construction via object.__new__
            self._latest_async_deadline_ns = max(
                self._latest_async_deadline_ns, deadline_ns
            )
            return
        with lock:
            self._latest_async_deadline_ns = max(
                self._latest_async_deadline_ns, deadline_ns
            )

    def _wait_container_healthy(self, node: str, container: str, timeout: float) -> None:
        end = time.monotonic() + timeout
        last = ""
        while time.monotonic() < end:
            result = self.ctx.node_exec(
                node,
                f"docker inspect -f '{{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{else}}}}{{{{.State.Status}}}}{{{{end}}}}' {self._shquote(container)}",
            )
            last = self._stdout(result).strip()
            if last in {"healthy", "running"}:
                return
            time.sleep(1)
        raise RuntimeError(f"{container} on node {node} did not become healthy: {last}")

    def _wait_collector_ready(self) -> None:
        self.ctx.node_exec(
            "a",
            f"for i in $(seq 1 60); do (echo > /dev/tcp/{COLLECTOR_IP}/4317) >/dev/null 2>&1 && exit 0; sleep 1; done; exit 1",
            timeout=70,
        )

    def _compose(
        self, node: str, action: str, timeout: int = 300, check: bool = True
    ) -> Any:
        compose_file = "node-a.yaml" if node == "a" else "node-b.yaml"
        command = (
            f"cd {REMOTE_ROOT} && docker compose -p {PROJECT} -f {compose_file} {action}"
        )
        if check:
            return self.ctx.node_exec(node, command, timeout=timeout)
        try:
            return self.ctx.node_exec(node, command, timeout=timeout)
        except Exception:
            return None

    def _psql(self, sql: str) -> str:
        encoded = base64.b64encode(sql.encode()).decode("ascii")
        command = (
            "printf '%s' "
            + self._shquote(encoded)
            + " | base64 -d | docker exec -i astronomy-db "
            "psql -X -v ON_ERROR_STOP=1 -At -U astronomy_user -d astronomy_db"
        )
        return self._stdout(self.ctx.node_exec("a", command, timeout=30))

    def _copy_remote_file(self, node: str, remote: str, local: Path) -> None:
        if hasattr(self.ctx, "node_get"):
            try:
                self.ctx.node_get(node, remote, local)
                if local.exists():
                    return
            except Exception:
                # Missing files are valid in suppressed modes; the bounded
                # base64 fallback also supports older contract contexts.
                pass
        result = self.ctx.node_exec(
            node,
            f"if test -f {self._shquote(remote)}; then gzip -c {self._shquote(remote)} | base64 -w0; fi",
            timeout=300,
        )
        encoded = self._stdout(result).strip()
        if encoded:
            local.write_bytes(__import__("gzip").decompress(base64.b64decode(encoded)))
        else:
            local.write_bytes(b"")

    def _verify_native_file(self, path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        service_names: list[str] = []
        span_markers = 0
        request_id_header_attributes = 0

        def walk(value: Any) -> None:
            nonlocal span_markers, request_id_header_attributes
            if isinstance(value, dict):
                if isinstance(value.get("spans"), list):
                    span_markers += len(value["spans"])
                if value.get("key") == "service.name" and isinstance(value.get("value"), dict):
                    name = value["value"].get("stringValue")
                    if isinstance(name, str):
                        service_names.append(name)
                if value.get("key") in {
                    "http.request.header.x_experiment_request_id",
                    "http.request.header.x-experiment-request-id",
                }:
                    request_id_header_attributes += 1
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        for line in text.splitlines():
            try:
                walk(json.loads(line))
            except json.JSONDecodeError:
                # Keep malformed output visible and conservatively count the
                # standard protobuf JSON span key, without guessing services.
                span_markers += len(re.findall(r'"spanId"', line))
        product_mentions = sum(name == "product-catalog" for name in service_names)
        if self.mode == "absent":
            compliant = span_markers == 0
        elif self.mode == "partial":
            compliant = product_mentions == 0
        else:
            compliant = span_markers > 0 and product_mentions > 0
        return {
            "mode": self.mode,
            "trace_file_bytes": path.stat().st_size if path.exists() else 0,
            "span_markers": span_markers,
            "product_catalog_mentions": product_mentions,
            "resource_service_names": sorted(set(service_names)),
            "request_id_header_attributes": request_id_header_attributes,
            "request_id_capture_status": (
                "not_applicable_without_native_spans"
                if self.mode == "absent"
                else "observed"
                if request_id_header_attributes > 0
                else "unsupported_or_unobserved"
            ),
            "mode_compliant": compliant,
            "method": "collector file inspection after graceful collector termination",
        }

    def _suppression_description(self) -> dict[str, Any]:
        if self.mode == "absent":
            excluded = "all native traces"
        elif self.mode == "partial":
            excluded = "native traces from both product-catalog replicas"
        else:
            excluded = "none"
        return {
            "mode": self.mode,
            "excluded": excluded,
            "sdk_settings": "OTEL_SDK_DISABLED=true on disabled standard SDKs",
            "source_guards": "checkout and product-catalog skip exporter/provider construction; email skips its direct metric exporter when OTEL_SDK_DISABLED=true",
            "collector_filter": "none; the file exporter retains the unfiltered native OTLP stream for suppression audit",
            "propagation": "checkout keeps W3C propagation with a never-sample provider; no disabled Go exporter is constructed",
        }

    def _patch_native_disable(self) -> dict[str, Any]:
        """Install small, auditable disable guards in custom SDK startup.

        The pinned checkout constructs trace, metric and log exporters directly;
        product-catalog constructs an otelconf SDK directly.  Neither path may be
        hidden later by a collector filter in an experiment whose treatment is
        genuine application tracing absence.
        """
        checkout = self.source / "src" / "checkout" / "main.go"
        product = self.source / "src" / "product-catalog" / "main.go"
        email = self.source / "src" / "email" / "email_server.rb"

        checkout_text = checkout.read_text(encoding="utf-8")
        if "func telemetrySDKDisabled() bool" not in checkout_text:
            checkout_text = self._replace_once(
                checkout_text,
                '\t"strconv"\n\t"sync"',
                '\t"strconv"\n\t"strings"\n\t"sync"',
                checkout,
            )
            checkout_text = self._replace_once(
                checkout_text,
                "func initTracerProvider() *sdktrace.TracerProvider {\n\tctx := context.Background()",
                "func telemetrySDKDisabled() bool {\n"
                '\treturn strings.EqualFold(strings.TrimSpace(os.Getenv("OTEL_SDK_DISABLED")), "true")\n'
                "}\n\n"
                "func initTracerProvider() *sdktrace.TracerProvider {\n"
                "\tif telemetrySDKDisabled() {\n"
                "\t\ttp := sdktrace.NewTracerProvider(sdktrace.WithSampler(sdktrace.NeverSample()))\n"
                "\t\totel.SetTracerProvider(tp)\n"
                "\t\totel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))\n"
                "\t\treturn tp\n"
                "\t}\n"
                "\tctx := context.Background()",
                checkout,
            )
            checkout_text = self._replace_once(
                checkout_text,
                "func initMeterProvider() *sdkmetric.MeterProvider {\n\tctx := context.Background()",
                "func initMeterProvider() *sdkmetric.MeterProvider {\n"
                "\tif telemetrySDKDisabled() {\n"
                "\t\tmp := sdkmetric.NewMeterProvider()\n"
                "\t\totel.SetMeterProvider(mp)\n"
                "\t\treturn mp\n"
                "\t}\n"
                "\tctx := context.Background()",
                checkout,
            )
            checkout_text = self._replace_once(
                checkout_text,
                "func initLoggerProvider() *sdklog.LoggerProvider {\n\tctx := context.Background()",
                "func initLoggerProvider() *sdklog.LoggerProvider {\n"
                "\tif telemetrySDKDisabled() {\n"
                "\t\tlp := sdklog.NewLoggerProvider()\n"
                "\t\tglobal.SetLoggerProvider(lp)\n"
                "\t\treturn lp\n"
                "\t}\n"
                "\tctx := context.Background()",
                checkout,
            )
            checkout.write_text(checkout_text, encoding="utf-8")

        product_text = product.read_text(encoding="utf-8")
        if "The zero global providers are intentional" not in product_text:
            old = """\t// Initialize OpenTelemetry SDK with otelconf
\tsdk, err := otelconf.NewSDK(otelconf.WithContext(ctx))
\tif err != nil {
\t\tlogger.Error(fmt.Sprintf("Failed to initialize OpenTelemetry SDK: %v", err))
\t\tos.Exit(1)
\t}
\tdefer func() {
\t\tif err := sdk.Shutdown(ctx); err != nil {
\t\t\tlogger.Error(fmt.Sprintf("Error shutting down OpenTelemetry SDK: %v", err))
\t\t}
\t\tlogger.Info("Shutdown OpenTelemetry SDK")
\t}()

\t// Set global providers and propagator
\totel.SetTracerProvider(sdk.TracerProvider())
\totel.SetMeterProvider(sdk.MeterProvider())
\tglobal.SetLoggerProvider(sdk.LoggerProvider())
\totel.SetTextMapPropagator(sdk.Propagator())
"""
            new = """\tif !strings.EqualFold(strings.TrimSpace(os.Getenv("OTEL_SDK_DISABLED")), "true") {
\t\t// Initialize OpenTelemetry SDK with otelconf only when native telemetry is enabled.
\t\tsdk, err := otelconf.NewSDK(otelconf.WithContext(ctx))
\t\tif err != nil {
\t\t\tlogger.Error(fmt.Sprintf("Failed to initialize OpenTelemetry SDK: %v", err))
\t\t\tos.Exit(1)
\t\t}
\t\tdefer func() {
\t\t\tif err := sdk.Shutdown(ctx); err != nil {
\t\t\t\tlogger.Error(fmt.Sprintf("Error shutting down OpenTelemetry SDK: %v", err))
\t\t\t}
\t\t\tlogger.Info("Shutdown OpenTelemetry SDK")
\t\t}()
\t\totel.SetTracerProvider(sdk.TracerProvider())
\t\totel.SetMeterProvider(sdk.MeterProvider())
\t\tglobal.SetLoggerProvider(sdk.LoggerProvider())
\t\totel.SetTextMapPropagator(sdk.Propagator())
\t} // The zero global providers are intentional when native telemetry is disabled.
"""
            product.write_text(
                self._replace_once(product_text, old, new, product), encoding="utf-8"
            )

        # Ruby's master switch creates no-op providers, while this application
        # unconditionally calls the SDK-only add_metric_reader method.  Guard
        # that direct construction; request handling and the test mailer remain
        # unchanged.
        email_text = email.read_text(encoding="utf-8")
        if "metric exporter is not constructed when the SDK is disabled" not in email_text:
            old = """otlp_metric_exporter = OpenTelemetry::Exporter::OTLP::Metrics::MetricsExporter.new
OpenTelemetry.meter_provider.add_metric_reader(otlp_metric_exporter)
"""
            new = """unless ENV.fetch("OTEL_SDK_DISABLED", "false").strip.casecmp?("true")
  otlp_metric_exporter = OpenTelemetry::Exporter::OTLP::Metrics::MetricsExporter.new
  OpenTelemetry.meter_provider.add_metric_reader(otlp_metric_exporter)
end # The metric exporter is not constructed when the SDK is disabled.
"""
            email.write_text(
                self._replace_once(email_text, old, new, email), encoding="utf-8"
            )

        diff = self._run_stdout(
            [
                "git",
                "-C",
                str(self.source),
                "diff",
                "--",
                "src/checkout/main.go",
                "src/product-catalog/main.go",
                "src/email/email_server.rb",
            ]
        )
        if not diff.strip():
            raise RuntimeError("native-disable source patch produced no recorded diff")
        patch_path = self.bundle / "native-disable.patch"
        patch_path.write_text(diff, encoding="utf-8")
        return {
            "path": patch_path.name,
            "sha256": hashlib.sha256(diff.encode("utf-8")).hexdigest(),
            "services": ["checkout", "email", "product-catalog-a", "product-catalog-b"],
        }

    @staticmethod
    def _replace_once(text: str, old: str, new: str, path: Path) -> str:
        if text.count(old) != 1:
            raise RuntimeError(
                f"pinned source patch anchor mismatch in {path}: expected one, found {text.count(old)}"
            )
        return text.replace(old, new, 1)

    @classmethod
    def _compose_merge(cls, base: Any, override: Any) -> Any:
        if not isinstance(base, dict) or not isinstance(override, dict):
            return copy.deepcopy(override)
        result = copy.deepcopy(base)
        for key, value in override.items():
            if key == "environment":
                env = cls._environment_dict(result.get(key, {}))
                env.update(cls._environment_dict(value))
                result[key] = env
            elif key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._compose_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result

    @staticmethod
    def _environment_dict(value: Any) -> dict[str, str]:
        if isinstance(value, dict):
            return {str(k): "" if v is None else str(v) for k, v in value.items()}
        result: dict[str, str] = {}
        for item in value or []:
            key, separator, val = str(item).partition("=")
            result[key] = val if separator else ""
        return result

    @classmethod
    def _expand(cls, value: Any, environment: dict[str, str]) -> Any:
        if isinstance(value, dict):
            return {key: cls._expand(val, environment) for key, val in value.items()}
        if isinstance(value, list):
            return [cls._expand(item, environment) for item in value]
        if not isinstance(value, str):
            return value

        def replace(match: re.Match[str]) -> str:
            name, operator, default = match.groups()
            current = environment.get(name)
            if current is None or (operator == ":-" and current == ""):
                return default or ""
            return current

        return _ENV.sub(replace, value)

    @staticmethod
    def _read_env(path: Path) -> dict[str, str]:
        values: dict[str, str] = dict(os.environ)
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.split(" #", 1)[0].strip()
        # Resolve the .env's simple references before Compose documents.
        for _ in range(4):
            values = {key: Adapter._expand(value, values) for key, value in values.items()}
        return values

    @classmethod
    def _resolve_environment_values(
        cls, document: dict[str, Any], environment: dict[str, str]
    ) -> None:
        """Apply Compose's bare `- NAME` lookup semantics before guest copy."""
        for service in document.get("services", {}).values():
            values = cls._environment_dict(service.get("environment", {}))
            service["environment"] = {
                key: environment.get(key, value) if value == "" else value
                for key, value in values.items()
            }

    @staticmethod
    def _write_yaml(path: Path, value: Any) -> None:
        path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

    @staticmethod
    def _prefix_source_mounts(service: dict[str, Any]) -> None:
        """Make upstream bind mounts relative to the preserved source checkout."""
        rewritten: list[Any] = []
        for volume in service.get("volumes", []) or []:
            if isinstance(volume, str):
                source, separator, rest = volume.partition(":")
                if source.startswith("./"):
                    source = "./source/" + source[2:]
                rewritten.append(source + separator + rest)
            elif isinstance(volume, dict):
                item = copy.deepcopy(volume)
                source = item.get("source")
                if item.get("type") == "bind" and isinstance(source, str) and source.startswith("./"):
                    item["source"] = "./source/" + source[2:]
                rewritten.append(item)
            else:
                rewritten.append(volume)
        if "volumes" in service:
            service["volumes"] = rewritten

    @staticmethod
    def _prefix_source_build(service: dict[str, Any]) -> None:
        """Retarget an upstream build context after nesting source in bundle."""
        build = service.get("build")
        if isinstance(build, str):
            service["build"] = "./source" if build in {".", "./"} else "./source/" + build.removeprefix("./")
        elif isinstance(build, dict):
            build = copy.deepcopy(build)
            context = str(build.get("context", "./"))
            build["context"] = "./source" if context in {".", "./"} else "./source/" + context.removeprefix("./")
            service["build"] = build

    def _run_stdout(self, command: list[str]) -> str:
        return self._stdout(self.ctx.run(command, timeout=300))

    @staticmethod
    def _stdout(result: Any) -> str:
        value = getattr(result, "stdout", "")
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value or ""

    @staticmethod
    def _shquote(value: str) -> str:
        return "'" + value.replace("'", "'\"'\"'") + "'"

    @staticmethod
    def _sql_literal(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"
