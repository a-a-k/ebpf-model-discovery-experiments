from pathlib import Path
import time

from systems.otel_demo import adapter as adapter_module
from systems.otel_demo.adapter import Adapter, PRODUCT_ID


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
        "query_completed_ns": now,
    }
    record = {"order_id": "order-1", "started_ns": now - 11_000_000_000}
    result = adapter.verify_async([record])[0]["async_verification"]
    assert result["deadline_ns"] == record["started_ns"] + 10_000_000_000
    assert result["success"] is None


def test_async_in_boundary_positive_and_missing_oracle() -> None:
    now = time.time_ns()
    adapter = object.__new__(Adapter)
    adapter._latest_async_deadline_ns = 0
    adapter._read_order = lambda order_id: {
        "query_ok": True,
        "complete": True,
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
