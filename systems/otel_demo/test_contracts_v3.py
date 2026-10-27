import pytest

from src.ebpf_discovery.observations import census
from systems.otel_demo.adapter import Adapter
from systems.otel_demo.contracts_v3 import (
    CONTRACTS,
    ENTRY_SERVICES,
    PRODUCT_ID,
    payload_verdict,
    status_ok,
)


def test_contract_declarations_and_status_are_exact() -> None:
    assert ENTRY_SERVICES == {"ebpf": ["frontend"], "native": ["frontend"]}
    assert [step["path"] for step in CONTRACTS["checkout"]["steps"]] == [
        f"/api/products/{PRODUCT_ID}", "/api/cart", "/api/checkout"
    ]
    assert status_ok("checkout", 2, 200)
    assert not status_ok("checkout", 2, 201)
    assert not status_ok("checkout", 2, "200")
    with pytest.raises(ValueError):
        status_ok("checkout", 3, 200)


@pytest.mark.parametrize(
    ("operation", "payload", "expected"),
    [
        ("browse_product", '{"id":"OLJCESPC7Z"}', True),
        ("browse_product", '{"id":"wrong"}', False),
        ("add_to_cart", '{"items":[{"productId":"OLJCESPC7Z","quantity":1}]}', True),
        ("add_to_cart", '{"items":[{"productId":"OLJCESPC7Z","quantity":2}]}', False),
        ("checkout", '{"orderId":"order-1"}', True),
        ("checkout", '{"order_id":"order-1"}', True),
        ("checkout", '{"orderId":""}', False),
    ],
)
def test_payload_verdict_matches_existing_final_response_semantics(
    operation: str, payload: str, expected: bool
) -> None:
    assert payload_verdict(operation, payload, {})["value"] is expected


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        ('{"orderId":"one","orderId":"two"}', "duplicate_json_key"),
        ('{"orderId":NaN}', "non_finite_json_number"),
        ('{"number":1e999}', "non_finite_json_number"),
        ('{"orderId":', "invalid_json"),
    ],
)
def test_payload_verdict_rejects_non_strict_json_as_unknown(payload: str, reason: str) -> None:
    assert payload_verdict("checkout", payload, {}) == {"value": None, "reason": reason}


def test_only_final_response_has_a_payload_verdict() -> None:
    assert payload_verdict(
        "checkout", '{"id":"OLJCESPC7Z"}', {"step_index": 0}
    ) == {"value": None, "reason": "not_final_response"}


def test_complete_checkout_intent_exists_before_first_failed_call() -> None:
    adapter = object.__new__(Adapter)
    adapter._consumer_paused = False
    seen = []

    def fail(record, method, path, timeout, body=None, request_id=None):
        seen.append((method, path, request_id, record["request_intent"]))
        raise RuntimeError("first request failed")

    adapter._http_step = fail
    record = adapter.operation("checkout", 7, "intent-test")
    intent = record["request_intent"]
    assert set(intent) == {"started_ns", "operation_id", "steps"}
    assert record["started_ns"] == intent["started_ns"]
    assert intent["operation_id"] == "checkout"
    assert intent["steps"] == [
        {"ordinal": index, "request_id": step["request_id"], **declared}
        for index, (step, declared) in enumerate(zip(intent["steps"], CONTRACTS["checkout"]["steps"]))
    ]
    assert len({step["request_id"] for step in intent["steps"]}) == 3
    assert all(set(step) == {"ordinal", "request_id", "method", "path"} for step in intent["steps"])
    assert seen[0][2] == intent["steps"][0]["request_id"]
    assert record["http_steps"] == []
    assert record["success"] is False
    automatic_row = census([record], "calibration", "11")[0]
    assert automatic_row["step_ids"] == []
    assert "operation" not in automatic_row and "request_intent" not in automatic_row
