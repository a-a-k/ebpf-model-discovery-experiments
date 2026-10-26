from pathlib import Path

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
        '{"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"frontend"}}]},"scopeSpans":[{"spans":[{"spanId":"1"}]}]}]}\n'
    )
    adapter = object.__new__(Adapter)
    adapter.mode = "partial"
    assert adapter._verify_native_file(traces)["mode_compliant"]
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
