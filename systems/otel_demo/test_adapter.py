from pathlib import Path
import json
import time

from systems.otel_demo import adapter as adapter_module
from systems.otel_demo.adapter import (
    Adapter,
    ENTRY_GUEST_PORT,
    PRODUCT_ID,
    REPLICA_A_GUEST_PORT,
    REPLICA_B_GUEST_PORT,
)


def test_compose_environment_merge() -> None:
    merged = Adapter._compose_merge(
        {"environment": ["A=1", "B=2"]},
        {"environment": ["B=3", "C=4"]},
    )
    assert merged["environment"] == {"A": "1", "B": "3", "C": "4"}


def test_verify_payloads() -> None:
    adapter = object.__new__(Adapter)
    records = [
        {
            "operation": "browse_product",
            "success": True,
            "http_steps": [{"json": {"id": PRODUCT_ID}}],
        },
        {
            "operation": "add_to_cart",
            "success": True,
            "http_steps": [
                {"json": {"items": [{"productId": PRODUCT_ID, "quantity": 1}]}}
            ],
        },
        {
            "operation": "checkout",
            "success": True,
            "order_id": "abc",
            "http_steps": [{"json": {"orderId": "abc"}}],
        },
    ]
    assert all(item["success"] for item in adapter.verify(records))


def test_native_suppression_file_checks(tmp_path: Path) -> None:
    traces = tmp_path / "traces.json"
    traces.write_text(
        '{"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"frontend"}}]},"scopeSpans":[{"spans":[{"spanId":"1","attributes":[{"key":"http.request.header.x_experiment_request_id","value":{"arrayValue":{"values":[{"stringValue":"opaque"}]}}}]}]}]}]}\n'
    )
    adapter = object.__new__(Adapter)
    adapter.mode = "partial"
    verification = adapter._verify_native_file(traces)
    assert verification["mode_compliant"]
    assert verification["request_id_capture_status"] == "observed"
    traces.write_text(
        '{"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"product-catalog"}}]},"scopeSpans":[{"spans":[{"spanId":"1"}]}]}]}\n'
    )
    assert not adapter._verify_native_file(traces)["mode_compliant"]


def test_native_collector_is_unfiltered_and_build_context_is_nested() -> None:
    adapter = object.__new__(Adapter)
    adapter.mode = "absent"
    config = adapter._collector_config()
    assert "filter/native_suppression" not in config
    assert 'path: /native/traces.json' in config
    description = adapter._suppression_description()
    assert description["collector_filter"].startswith("none")
    assert "always-off sampling" in description["source_guards"]
    assert "NoopTracerProvider" in description["native_component_guards"]

    service = {"build": {"context": "./", "dockerfile": "./src/checkout/Dockerfile"}}
    adapter._prefix_source_build(service)
    assert service["build"]["context"] == "./source"
    assert service["build"]["dockerfile"] == "./src/checkout/Dockerfile"


def test_native_enabled_frontend_mounts_exact_server_header_capture() -> None:
    adapter = object.__new__(Adapter)
    adapter.mode = "full"
    frontend = {"environment": {}, "volumes": []}
    adapter._configure_frontend_native_capture(frontend)
    assert frontend["volumes"] == [
        "./source/src/frontend/utils/telemetry/Instrumentation.js:/app/Instrumentation.js:ro"
    ]

    adapter.mode = "absent"
    absent_frontend = {"environment": {}}
    adapter._configure_frontend_native_capture(absent_frontend)
    assert "volumes" not in absent_frontend


def test_frontend_patch_uses_server_only_supported_header_config(tmp_path: Path) -> None:
    instrumentation = tmp_path / "Instrumentation.js"
    instrumentation.write_text(
        """getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-fs': {
        enabled: false,
      },
})
""",
        encoding="utf-8",
    )
    adapter = object.__new__(Adapter)
    adapter._patch_frontend_request_id_capture(instrumentation)
    patched = instrumentation.read_text(encoding="utf-8")
    assert "headersToSpanAttributes" in patched
    assert "server:" in patched
    assert "requestHeaders: ['x-experiment-request-id']" in patched
    assert "client:" not in patched
    assert "requestHook" not in patched


def test_collect_native_rotates_exporter_targets_before_restart(tmp_path: Path) -> None:
    events = []

    class Context:
        out = tmp_path

        def node_exec(self, node, command, **kwargs):
            events.append(command)
            if "ps -a --format '{{.Name}}'" in command:
                return ""
            return ""

        def node_get(self, node, remote, local):
            Path(local).write_text("", encoding="utf-8")

    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    adapter.mode = "absent"
    adapter._wait_collector_ready = lambda: events.append("collector-ready")
    adapter.collect_native(tmp_path / "snapshot")

    stop_index = events.index("docker stop -t 20 otel-collector")
    rotate_index = next(
        index
        for index, command in enumerate(events)
        if "/native/snapshots/" in command and "mv --" in command
    )
    restart_index = next(
        index for index, command in enumerate(events) if "start otel-collector" in command
    )
    assert stop_index < rotate_index < restart_index
    rotate_command = events[rotate_index]
    assert "traces.json" in rotate_command
    assert "otel-logs.json" in rotate_command
    assert "metrics.json" in rotate_command
    assert "suppression.json" not in rotate_command

    lifecycle = json.loads(
        (tmp_path / "snapshot" / "snapshot-lifecycle.json").read_text()
    )
    assert lifecycle["local_snapshot_preserved"] is True
    assert lifecycle["subsequent_export_mode"] == "fresh_file_after_rotation"
    assert lifecycle["exporter_file_rotation_targets"] == [
        "traces.json",
        "otel-logs.json",
        "metrics.json",
    ]


def test_absent_native_configs_disable_non_sdk_tracing(tmp_path: Path) -> None:
    adapter = object.__new__(Adapter)
    adapter.mode = "absent"
    adapter.bundle = tmp_path / "bundle"
    adapter.source = tmp_path / "source"
    (adapter.source / "src/frontend-proxy").mkdir(parents=True)
    (adapter.source / "src/image-provider").mkdir(parents=True)
    adapter.bundle.mkdir()
    (adapter.source / "src/frontend-proxy/envoy.tmpl.yaml").write_text(
        """static_resources:
  listeners:
  - filter_chains:
    - filters:
      - typed_config:
          tracing:
            provider: {name: envoy.tracers.opentelemetry}
          route_config: {name: routes}
""",
        encoding="utf-8",
    )
    (adapter.source / "src/image-provider/nginx.conf.template").write_text(
        "http {\n    otel_trace on;\n}\n", encoding="utf-8"
    )
    adapter._write_absent_native_configs()
    proxy = (adapter.bundle / "frontend-proxy-no-tracing.yaml").read_text()
    nginx = (adapter.bundle / "image-provider-no-tracing.conf").read_text()
    assert "tracing:" not in proxy
    assert "route_config:" in proxy
    assert "otel_trace off;" in nginx


def test_envoy_uses_guest_transport_for_remote_replica() -> None:
    adapter = object.__new__(Adapter)
    adapter.ctx = type(
        "Context", (), {"node_ip": lambda self, node: "192.168.76.12"}
    )()
    config = adapter._envoy_config()
    assert "address: 192.168.76.12" in config
    assert f"port_value: {REPLICA_B_GUEST_PORT}" in config


def test_runner_entry_and_replica_metadata_use_guest_transport(tmp_path: Path) -> None:
    context = type(
        "Context",
        (),
        {
            "mode": "absent",
            "deployment_dir": tmp_path,
            "node_ip": lambda self, node: (
                "192.168.76.11" if node == "a" else "192.168.76.12"
            ),
        },
    )()
    adapter = Adapter(context)
    assert adapter.entry_url == f"http://192.168.76.11:{ENTRY_GUEST_PORT}"
    replicas = adapter.metadata()["replicas"]
    assert replicas[0]["transport_host"] == "192.168.76.11"
    assert replicas[0]["transport_port"] == REPLICA_A_GUEST_PORT
    assert replicas[1]["transport_host"] == "192.168.76.12"


def test_reset_uses_owner_session_only_for_accounting_cleanup() -> None:
    events = []
    adapter = object.__new__(Adapter)
    adapter.ctx = type(
        "Context",
        (),
        {"node_exec": lambda self, node, command, **kwargs: events.append(command) or ""},
    )()
    adapter.set_database = lambda up: events.append(("database", up))
    adapter.set_replicas = lambda state: events.append(("replicas", state))
    adapter.set_consumer = lambda up: events.append(("consumer", up))
    adapter.ready = lambda: events.append("ready")
    adapter._psql = lambda sql: (_ for _ in ()).throw(
        AssertionError("reset must not TRUNCATE through the evaluator/app session")
    )

    adapter.reset()

    admin = next(command for command in events if isinstance(command, str) and "psql" in command)
    assert "-U postgres -d astronomy_db" in admin
    assert "-U astronomy_user" not in admin
    assert events[-1] == "ready"


def test_http_step_uses_fresh_opaque_request_id(monkeypatch) -> None:
    captured = {}

    class Response:
        status_code = 200
        content = b'{"id":"OLJCESPC7Z"}'

        @staticmethod
        def json():
            return {"id": PRODUCT_ID}

    def request(method, url, **kwargs):
        captured.update(kwargs)
        return Response()

    monkeypatch.setattr(adapter_module.requests, "request", request)
    adapter = object.__new__(Adapter)
    adapter.entry_url = "http://example.invalid"
    record = {"attempt_id": "semantic-label-must-not-be-sent", "http_steps": []}
    step = adapter._http_step(record, "GET", "/api/products/x", 1.0)
    assert step["request_id"] == captured["headers"]["X-Experiment-Request-Id"]
    assert len(step["request_id"]) == 32
    assert record["attempt_id"] not in str(captured["headers"])


def test_async_late_first_positive_is_unknown() -> None:
    now = time.time_ns()
    adapter = object.__new__(Adapter)
    adapter._latest_async_deadline_ns = 0
    adapter._read_order = lambda order_id: {
        "query_ok": True,
        "complete": True,
        "query_started_ns": now - 1_000_000,
        "query_completed_ns": now,
    }
    record = {"order_id": "order-1", "started_ns": now - 11_000_000_000}
    result = adapter.verify_async([record])[0]["async_verification"]
    assert result["deadline_ns"] == record["started_ns"] + 10_000_000_000
    assert result["success"] is None


def _stub_kafka_admin_setup(adapter) -> None:
    adapter._cleanup_kafka_admin = lambda deadline, name, allow_late, evidence=None: {
        "returncode": 0,
        "helper_absent": True,
    }
    adapter._kafka_image_id = lambda deadline: "sha256:broker-image"


def test_consumer_drain_uses_pinned_apache_kafka_cli_path() -> None:
    calls = []

    class Result:
        stdout = (
            "GROUP TOPIC PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG CONSUMER-ID HOST CLIENT-ID\n"
            "accounting orders 0 42 42 0 consumer /172.0.0.1 client\n"
        )
        stderr = ""
        returncode = 0

    class Context:
        def node_exec(self, node, command, **kwargs):
            calls.append((node, command, kwargs))
            return Result()

    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    _stub_kafka_admin_setup(adapter)
    adapter._kafka_started_at = lambda deadline: "stable"
    adapter._wait_consumer_drain(1)

    assert len(calls) == 1
    node, command, kwargs = calls[0]
    assert node == "a"
    assert "docker exec" not in command
    assert "docker run --rm --pull never" in command
    assert "--network container:kafka --memory 256m --cpus 1" in command
    assert "--entrypoint /opt/kafka/bin/kafka-consumer-groups.sh" in command
    assert "'sha256:broker-image'" in command
    # Kafka binds its listener to the Compose hostname, not loopback.  The
    # helper shares Kafka's network namespace and its Docker DNS configuration.
    assert "--bootstrap-server kafka:9092" in command
    assert "OTEL_SDK_DISABLED=true" in command
    assert "OTEL_SERVICE_NAME=study-kafka-admin" in command
    assert "study-kafka-admin-" in command
    assert "-javaagent" not in command
    assert kwargs["check"] is False
    assert 0 < kwargs["timeout"] <= 1


def test_consumer_drain_rejects_failed_missing_partial_and_nonzero_rows(
    monkeypatch,
) -> None:
    header = "GROUP TOPIC PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG CONSUMER-ID HOST CLIENT-ID\n"

    class Result:
        stderr = "diagnostic"

        def __init__(self, stdout, returncode=0):
            self.stdout = header + stdout
            self.returncode = returncode

    results = iter(
        [
            Result("accounting orders 0 42 42 0 consumer host client\n", 1),
            Result(
                "accounting orders - - - - consumer host client\n"
                "accounting orders 0 42 42 0 consumer host client\n"
            ),
            Result("accounting another-topic 0 42 42 0 consumer host client\n"),
            Result("accounting orders 0 41 42 1 consumer host client\n"),
            Result(
                "accounting orders 0 42 42 0 consumer host client\n"
                "accounting orders 1 21 21 0 consumer host client\n"
            ),
        ]
    )
    calls = []

    class Context:
        def node_exec(self, node, command, **kwargs):
            calls.append(kwargs)
            return next(results)

    monkeypatch.setattr(adapter_module.time, "sleep", lambda _: None)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    _stub_kafka_admin_setup(adapter)
    adapter._kafka_started_at = lambda deadline: "stable"
    adapter._wait_consumer_drain(1)

    assert len(calls) == 5
    assert all(call["check"] is False for call in calls)
    assert all(0 < call["timeout"] <= 1 for call in calls)


def test_consumer_drain_failure_retains_probe_diagnostics(monkeypatch) -> None:
    class Result:
        stdout = "accounting orders - - - - consumer host client\n"
        stderr = "consumer group unavailable"
        returncode = 1

    class Context:
        def node_exec(self, node, command, **kwargs):
            return Result()

    ticks = iter([0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    monkeypatch.setattr(adapter_module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(adapter_module.time, "sleep", lambda _: None)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    _stub_kafka_admin_setup(adapter)
    adapter._kafka_started_at = lambda deadline: "stable"

    try:
        adapter._wait_consumer_drain(0.5)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("an invalid probe must not establish a drained backlog")

    assert "consumer group unavailable" in message
    assert "returncode=1" in message


def test_consumer_drain_retries_bounded_probe_timeout(monkeypatch) -> None:
    class Result:
        stdout = "accounting orders 0 42 42 0 consumer host client\n"
        stderr = ""
        returncode = 0

    calls = []

    class Context:
        def node_exec(self, node, command, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise adapter_module.subprocess.TimeoutExpired(
                    command, kwargs["timeout"], output="partial", stderr="slow probe"
                )
            return Result()

    monkeypatch.setattr(adapter_module.time, "sleep", lambda _: None)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    cleanup_calls = []
    adapter._cleanup_kafka_admin = (
        lambda deadline, name, allow_late, evidence=None: cleanup_calls.append(
            (deadline, name, allow_late)
        )
        or {"returncode": 0, "helper_absent": True}
    )
    adapter._kafka_image_id = lambda deadline: "sha256:broker-image"
    adapter._kafka_started_at = lambda deadline: "stable"
    adapter._wait_consumer_drain(1)

    assert len(calls) == 2
    assert all(0 < call["timeout"] <= 1 for call in calls)
    assert any(allow_late for _, _, allow_late in cleanup_calls)


def test_consumer_drain_probe_uses_full_remaining_budget(monkeypatch) -> None:
    class Result:
        stdout = "accounting orders 0 42 42 0 consumer host client\n"
        stderr = ""
        returncode = 0

    calls = []

    class Context:
        def node_exec(self, node, command, **kwargs):
            calls.append((command, kwargs))
            return Result()

    ticks = iter([100.0, 100.0, 100.0, 100.0])
    monkeypatch.setattr(adapter_module.time, "monotonic", lambda: next(ticks))
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    _stub_kafka_admin_setup(adapter)
    adapter._kafka_started_at = lambda deadline: "stable"
    adapter._wait_consumer_drain(60)

    command, kwargs = calls[0]
    assert kwargs["timeout"] == 60.0
    assert "timeout --signal=TERM --kill-after=2s 55.000s" in command


def test_consumer_drain_all_timeouts_retain_diagnostics(monkeypatch) -> None:
    class Context:
        def node_exec(self, node, command, **kwargs):
            raise adapter_module.subprocess.TimeoutExpired(
                command, kwargs["timeout"], output="partial", stderr="still slow"
            )

    ticks = iter([0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    monkeypatch.setattr(adapter_module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(adapter_module.time, "sleep", lambda _: None)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    _stub_kafka_admin_setup(adapter)
    adapter._kafka_started_at = lambda deadline: "stable"

    try:
        adapter._wait_consumer_drain(0.5)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("timed-out probes must not establish a drained backlog")

    assert "probe_timeout=" in message
    assert "partial" in message
    assert "still slow" in message


def test_consumer_drain_rejects_broker_restart() -> None:
    class Result:
        stdout = "accounting orders 0 42 42 0 consumer host client\n"
        stderr = ""
        returncode = 0

    class Context:
        def node_exec(self, node, command, **kwargs):
            return Result()

    starts = iter(["before", "after"])
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    _stub_kafka_admin_setup(adapter)
    adapter._kafka_started_at = lambda deadline: next(starts)

    try:
        adapter._wait_consumer_drain(1)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("a broker restart must invalidate drain evidence")

    assert "Kafka restarted" in message
    assert "before=before after=after" in message


def test_kafka_start_query_is_bounded_and_strict(monkeypatch) -> None:
    calls = []

    class Result:
        stdout = ""
        stderr = "inspect failed"
        returncode = 1

    class Context:
        def node_exec(self, node, command, **kwargs):
            calls.append((node, command, kwargs))
            return Result()

    monkeypatch.setattr(adapter_module.time, "monotonic", lambda: 10.0)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()

    try:
        adapter._kafka_started_at(70.0)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("a failed start-time query must be technical failure")

    assert calls == [
        (
            "a",
            "docker inspect -f '{{.State.StartedAt}}' kafka",
            {"check": False, "timeout": 60.0},
        )
    ]
    assert "inspect failed" in message
    assert "returncode=1" in message


def test_kafka_admin_cleanup_is_named_bounded_and_verified(monkeypatch) -> None:
    calls = []

    class Result:
        stdout = ""
        stderr = ""
        returncode = 0

    class Context:
        def node_exec(self, node, command, **kwargs):
            calls.append((node, command, kwargs))
            return Result()

    monkeypatch.setattr(adapter_module.time, "monotonic", lambda: 10.0)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    result = adapter._cleanup_kafka_admin(
        70.0, "study-kafka-admin-deadbeef", allow_late=False
    )

    node, command, kwargs = calls[0]
    assert node == "a"
    assert "docker rm -f 'study-kafka-admin-deadbeef'" in command
    assert "ids=$(docker ps -aq --filter name=^/study-kafka-admin-deadbeef$) || exit $?" in command
    assert 'test -z "$ids"' in command
    assert kwargs == {"check": False, "timeout": 5.0}
    assert result["status"] == "completed"
    assert result["helper_absent"] is True


def test_kafka_admin_cleanup_timeout_is_persisted(tmp_path: Path, monkeypatch) -> None:
    class Context:
        out = tmp_path

        def node_exec(self, node, command, **kwargs):
            raise adapter_module.subprocess.TimeoutExpired(
                command, kwargs["timeout"], output="cleanup out", stderr="cleanup err"
            )

    monkeypatch.setattr(adapter_module.time, "monotonic", lambda: 10.0)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    evidence = {"cleanups": []}

    try:
        adapter._cleanup_kafka_admin(
            70.0,
            "study-kafka-admin-deadbeef",
            allow_late=False,
            evidence=evidence,
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("cleanup timeout must be a technical failure")

    persisted = json.loads((tmp_path / "kafka-admin-drain.json").read_text())
    assert persisted["cleanups"][0]["status"] == "timeout"
    assert "cleanup err" in persisted["cleanups"][0]["stderr"]


def test_kafka_admin_cleanup_rejects_docker_ps_failure(
    tmp_path: Path, monkeypatch
) -> None:
    class Result:
        stdout = ""
        stderr = "docker daemon unavailable"
        returncode = 1

    class Context:
        out = tmp_path

        def node_exec(self, node, command, **kwargs):
            return Result()

    monkeypatch.setattr(adapter_module.time, "monotonic", lambda: 10.0)
    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    evidence = {"cleanups": []}

    try:
        adapter._cleanup_kafka_admin(
            70.0,
            "study-kafka-admin-deadbeef",
            allow_late=False,
            evidence=evidence,
        )
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("docker ps failure must not prove helper absence")

    persisted = json.loads((tmp_path / "kafka-admin-drain.json").read_text())
    assert persisted["cleanups"][0]["status"] == "error"
    assert persisted["cleanups"][0]["returncode"] == 1
    assert "docker daemon unavailable" in persisted["cleanups"][0]["stderr"]
    assert "docker daemon unavailable" in message


def test_kafka_admin_evidence_persists_image_helper_and_probe(tmp_path: Path) -> None:
    class Result:
        stdout = "accounting orders 0 42 42 0 consumer host client\n"
        stderr = ""
        returncode = 0

    class Context:
        out = tmp_path

        def node_exec(self, node, command, **kwargs):
            return Result()

    adapter = object.__new__(Adapter)
    adapter.ctx = Context()
    _stub_kafka_admin_setup(adapter)
    adapter._kafka_started_at = lambda deadline: "stable-start"
    adapter._wait_consumer_drain(1)

    evidence = json.loads((tmp_path / "kafka-admin-drain.json").read_text())
    assert evidence["status"] == "completed"
    assert evidence["broker_image_id"] == "sha256:broker-image"
    assert evidence["broker_started_at_before"] == "stable-start"
    assert evidence["broker_started_at_after"] == "stable-start"
    assert evidence["helper_name"].startswith("study-kafka-admin-")
    assert evidence["probes"][0]["returncode"] == 0
    assert evidence["probes"][0]["lags"] == [0]


def test_async_in_boundary_positive_and_missing_oracle() -> None:
    now = time.time_ns()
    adapter = object.__new__(Adapter)
    adapter._latest_async_deadline_ns = 0
    adapter._read_order = lambda order_id: {
        "query_ok": True,
        "complete": True,
        "query_started_ns": now,
        "query_completed_ns": now + 1_000_000,
    }
    success = adapter.verify_async(
        [{"order_id": "order-2", "started_ns": now}]
    )[0]["async_verification"]
    assert success["success"] is True

    missing = adapter.verify_async(
        [{"order_id": None, "started_ns": now}]
    )[0]
    assert missing["async_verification"]["success"] is None
    assert missing["async_verification"]["observations"] == []

    adapter._read_order = lambda order_id: {
        "query_ok": False,
        "complete": None,
        "query_completed_ns": now,
        "error": "oracle unavailable",
    }
    unavailable = adapter.verify_async(
        [{"order_id": "order-3", "started_ns": now - 11_000_000_000}]
    )[0]["async_verification"]
    assert unavailable["success"] is None
    assert unavailable["observations"][0]["query_ok"] is False


def test_async_late_negative_requires_post_deadline_snapshot() -> None:
    now = time.time_ns()
    started = now - 11_000_000_000
    deadline_ns = started + 10_000_000_000
    adapter = object.__new__(Adapter)
    adapter._latest_async_deadline_ns = 0
    adapter._read_order = lambda order_id: {
        "query_ok": True,
        "complete": False,
        "query_started_ns": deadline_ns - 1,
        "query_completed_ns": now,
    }
    ambiguous = adapter.verify_async(
        [{"order_id": "order-before", "started_ns": started}]
    )[0]["async_verification"]
    assert ambiguous["success"] is None

    adapter._read_order = lambda order_id: {
        "query_ok": True,
        "complete": False,
        "query_started_ns": deadline_ns,
        "query_completed_ns": now,
    }
    negative = adapter.verify_async(
        [{"order_id": "order-after", "started_ns": started}]
    )[0]["async_verification"]
    assert negative["success"] is False


def test_order_oracle_requires_exact_item_and_shipping() -> None:
    adapter = object.__new__(Adapter)
    adapter._psql = lambda sql: (
        '{"order_count":1,"item_count":1,"shipping_count":1,'
        '"items":[{"product_id":"OLJCESPC7Z","quantity":1}],'
        '"shipping":[{"shipping_tracking_id":"track","shipping_cost_currency_code":"USD",'
        '"shipping_cost_units":1,"shipping_cost_nanos":0,"street_address":"1 Observatory Way",'
        '"city":"Testville","state":"CA","country":"US","zip_code":"94000"}]}\n'
    )
    observation = adapter._read_order("order-exact")
    assert observation["complete"] is True
    assert observation["postcondition_exact"] is True
    assert observation["role"] == "evaluator_only"
    assert observation["query_text"].startswith("SELECT json_build_object")

    adapter._psql = lambda sql: (
        '{"order_count":1,"item_count":1,"shipping_count":1,'
        '"items":[{"product_id":"WRONG","quantity":1}],'
        '"shipping":[{"shipping_tracking_id":"track","shipping_cost_currency_code":"USD",'
        '"shipping_cost_units":1,"shipping_cost_nanos":0,"street_address":"1 Observatory Way",'
        '"city":"Testville","state":"CA","country":"US","zip_code":"94000"}]}\n'
    )
    assert adapter._read_order("order-wrong")["complete"] is False
