from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests
import yaml

from systems.otel_demo import experiment_v4
from systems.otel_demo.experiment_v4 import Adapter, CONTRACTS, PRODUCT_ID


class Journal:
    pass


class Context:
    mode = "full"

    def __init__(self, root: Path):
        self.deployment_dir = root
        self.journal = Journal()

    @staticmethod
    def node_ip(node: str) -> str:
        return {"a": "192.0.2.11", "b": "192.0.2.12"}[node]


def _adapter(tmp_path: Path) -> Adapter:
    return Adapter(Context(tmp_path))


def _response(status: int, payload: object) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(payload).encode()
    response.headers["content-type"] = "application/json"
    return response


def test_plan_is_stable_and_matches_declared_calls(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    first = adapter.plan_operation("checkout", 7, "block")
    second = adapter.plan_operation("checkout", 7, "block")

    assert first == second
    assert set(first) == {"attempt_id", "operation", "http_steps"}
    assert [(step["method"], step["path"]) for step in first["http_steps"]] == [
        ("GET", f"/api/products/{PRODUCT_ID}"),
        ("POST", "/api/cart"),
        ("POST", "/api/checkout?currencyCode=USD"),
    ]
    assert len({step["request_id"] for step in first["http_steps"]}) == 3
    assert adapter.plan_operation("checkout", 8, "block") != first


def test_operation_uses_uncapped_journal_transport_and_planned_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    calls: list[tuple[str, str, dict]] = []

    def request(method: str, url: str, **kwargs):
        calls.append((method, url, kwargs))
        return _response(200, {"id": PRODUCT_ID})

    monkeypatch.setattr(experiment_v4, "_v4_request", request)
    plan = adapter.plan_operation("browse_product", 1, "healthy")
    record = adapter.operation("browse_product", 1, "healthy")

    assert record["attempt_id"] == plan["attempt_id"]
    assert record["http_steps"][0]["request_id"] == plan["http_steps"][0]["request_id"]
    assert record["success"] is True
    assert record["observation"] == {
        "policy": "uncapped-v4",
        "deadline_seconds": None,
        "timestamp_eligibility_gate": False,
        "termination": "complete",
    }
    assert calls[0][2]["timeout"] is None
    assert calls[0][2]["journal"] is adapter.ctx.journal
    assert calls[0][2]["headers"] == {
        "X-Experiment-Request-Id": plan["http_steps"][0]["request_id"]
    }


def test_completed_prerequisite_mismatch_marks_suffix_not_attempted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    monkeypatch.setattr(
        experiment_v4, "_v4_request", lambda *args, **kwargs: _response(503, {"error": "down"})
    )

    record = adapter.operation("checkout", 2, "state-00")

    assert record["success"] is False
    assert record["observation"]["termination"] == "completed_response_mismatch"
    assert len(record["http_steps"]) == 1
    assert [step["ordinal"] for step in record["not_attempted_steps"]] == [1, 2]
    assert all(step["state"] == "not_attempted" for step in record["not_attempted_steps"])


def test_incomplete_transport_is_unknown_and_suffix_is_not_attempted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)

    def fail(*args, **kwargs):
        raise requests.ConnectionError("connection interrupted")

    monkeypatch.setattr(experiment_v4, "_v4_request", fail)
    record = adapter.operation("add_to_cart", 3, "state-10")

    assert record["success"] is None
    assert record["http_steps"][0]["state"] == "transport_incomplete"
    assert record["not_attempted_steps"][0]["ordinal"] == 1
    assert adapter.verify([record])[0]["success"] is None


def test_verify_uses_complete_status_and_final_body(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    base = {
        "operation": "add_to_cart",
        "success": True,
        "http_steps": [
            {"state": "complete", "status": 200, "json": {"id": PRODUCT_ID}},
            {
                "state": "complete",
                "status": 200,
                "json": {"items": [{"productId": PRODUCT_ID, "quantity": 1}]},
            },
        ],
    }
    assert adapter.verify([base])[0]["success"] is True

    wrong = json.loads(json.dumps(base))
    wrong["http_steps"][-1]["json"]["items"][0]["quantity"] = 2
    checked = adapter.verify([wrong])[0]
    assert checked["success"] is False
    assert checked["payload_postcondition"] is False


def test_operation_applies_body_contract_before_return(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    monkeypatch.setattr(
        experiment_v4,
        "_v4_request",
        lambda *args, **kwargs: _response(200, {"id": "different-product"}),
    )

    record = adapter.operation("browse_product", 9, "healthy")

    assert record["success"] is False
    assert record["payload_postcondition"] is False
    assert record["observation"]["termination"] == "completed_payload_mismatch"


def test_checkout_extracts_actual_order_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = _adapter(tmp_path)
    replies = iter(
        [
            _response(200, {"id": PRODUCT_ID}),
            _response(200, {"items": [{"productId": PRODUCT_ID, "quantity": 1}]}),
            _response(200, {"orderId": "order-actual"}),
        ]
    )
    monkeypatch.setattr(experiment_v4, "_v4_request", lambda *a, **k: next(replies))

    record = adapter.operation("checkout", 4, "healthy")
    checked = adapter.verify([record])[0]

    assert record["order_id"] == "order-actual"
    assert checked["success"] is True
    assert checked["order_id"] == "order-actual"


def test_v4_rejects_experiment_deadlines(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    with pytest.raises(ValueError, match="does not accept"):
        adapter.operation("browse_product", 1, "x", deadline=2.0)
    with pytest.raises(ValueError, match="no completion deadline"):
        adapter.verify_async([], deadline=10.0)


@pytest.mark.parametrize(
    ("observation", "state", "success"),
    [
        ({"complete": True, "query_ok": True}, "persisted_exact", True),
        (
            {"complete": False, "terminal_wrong_persisted_payload": True, "query_ok": True},
            "persisted_mismatch",
            False,
        ),
        ({"complete": False, "query_ok": True}, "pending", None),
        ({"complete": None, "query_ok": False}, "query_unavailable", None),
    ],
)
def test_async_snapshots_have_no_time_classification(
    tmp_path: Path, observation: dict, state: str, success: bool | None
) -> None:
    adapter = _adapter(tmp_path)
    adapter._read_order = lambda order_id: {"order_id": order_id, **observation}
    record = {"order_id": "order-1", "async_expected": {"items": []}}

    paused = adapter.observe_async([record])[0]["async_verification"]
    resumed = adapter.verify_async([record])[0]["async_verification"]

    assert paused["phase"] == "paused_snapshot"
    assert resumed["phase"] == "post_resume_verification"
    assert resumed["state"] == state
    assert resumed["success"] is success
    assert resumed["deadline_seconds"] is None


def test_consumer_resume_has_no_deadline_hold_or_drain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    calls = []
    adapter._compose = lambda *args, **kwargs: calls.append((args, kwargs))
    monkeypatch.setattr(
        adapter,
        "_wait_consumer_drain",
        lambda timeout: pytest.fail("set_consumer must not poll or drain"),
    )

    adapter.set_consumer(False)
    adapter.set_consumer(True)

    assert calls == [
        (("a", "stop -t 20 accounting"), {"timeout": 60}),
        (("a", "start accounting"), {"timeout": 60}),
    ]
    assert adapter._consumer_paused is False


def test_envoy_removes_request_and_connect_limits_but_keeps_health_check(
    tmp_path: Path,
) -> None:
    config = yaml.safe_load(_adapter(tmp_path)._envoy_config())
    listener = config["static_resources"]["listeners"][0]
    manager = listener["filter_chains"][0]["filters"][0]["typed_config"]
    route = manager["route_config"]["virtual_hosts"][0]["routes"][0]["route"]
    cluster = config["static_resources"]["clusters"][0]

    assert "timeout" not in route
    assert "connect_timeout" not in cluster
    assert cluster["health_checks"][0]["timeout"] == "0.5s"


def test_contracts_keep_semantics_separate_from_discovered_edges() -> None:
    assert set(CONTRACTS) == {"browse_product", "add_to_cart", "checkout"}
    checkout_ids = {call["call_id"] for call in CONTRACTS["checkout"]["required_calls"]}
    assert "checkout.checkout.catalog.get_product" in checkout_ids
    assert "checkout.frontend.catalog.enrich_response" in checkout_ids
    assert not any("email" in call_id or "kafka" in call_id or "empty" in call_id for call_id in checkout_ids)
    assert all("edge_id" not in call for call in CONTRACTS["checkout"]["required_calls"])


def test_metadata_records_native_envoy_defaults(tmp_path: Path) -> None:
    limits = _adapter(tmp_path).metadata()["v4_contract"][
        "router_native_defaults_after_adapter_limits_removed"
    ]
    assert limits["route_timeout_seconds"] == 15
    assert limits["connect_timeout_seconds"] == 5
