"""Declared OpenTelemetry Demo business contracts for the v3 source audit.

The declarations contain only intent known before an operation is dispatched.
They deliberately exclude workload outcomes and the independent SQL oracle.
"""
from __future__ import annotations

import json
import math
from typing import Any


PRODUCT_ID = "OLJCESPC7Z"

ENTRY_SERVICES = {"ebpf": ["frontend"], "native": ["frontend"]}

CONTRACTS = {
    "browse_product": {
        "steps": [
            {"method": "GET", "path": f"/api/products/{PRODUCT_ID}"},
        ],
        "response_kind": "json",
    },
    "add_to_cart": {
        "steps": [
            {"method": "GET", "path": f"/api/products/{PRODUCT_ID}"},
            {"method": "POST", "path": "/api/cart"},
        ],
        "response_kind": "json",
    },
    "checkout": {
        "steps": [
            {"method": "GET", "path": f"/api/products/{PRODUCT_ID}"},
            {"method": "POST", "path": "/api/cart"},
            {"method": "POST", "path": "/api/checkout"},
        ],
        "response_kind": "json",
    },
}


class _DuplicateKey(ValueError):
    pass


class _NonFiniteNumber(ValueError):
    pass


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise _NonFiniteNumber(value)


def _finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_finite(item) for item in value)
    if isinstance(value, dict):
        return all(_finite(item) for item in value.values())
    return True


def status_ok(operation: str, step_index: int, code: Any) -> bool:
    """Return whether the declared step has the adapter's exact HTTP status."""
    contract = CONTRACTS.get(operation)
    if contract is None:
        raise ValueError(f"unknown OpenTelemetry Demo operation: {operation!r}")
    if type(step_index) is not int or not 0 <= step_index < len(contract["steps"]):
        raise ValueError(f"invalid step index for {operation}: {step_index!r}")
    return type(code) is int and code == 200


def payload_verdict(operation: str, text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Evaluate only the existing final-response predicate, without an oracle.

    Missing or incomplete bodies are handled by the caller.  This function
    fails closed to unknown for text that is not strict JSON (including
    duplicate object keys and non-finite numbers).
    """
    contract = CONTRACTS.get(operation)
    if contract is None:
        raise ValueError(f"unknown OpenTelemetry Demo operation: {operation!r}")
    if not isinstance(context, dict):
        raise TypeError("context must be a dictionary")
    step_index = context.get("step_index", len(contract["steps"]) - 1)
    if type(step_index) is not int or not 0 <= step_index < len(contract["steps"]):
        raise ValueError(f"invalid step index for {operation}: {step_index!r}")
    if step_index != len(contract["steps"]) - 1:
        return {"value": None, "reason": "not_final_response"}
    if not isinstance(text, str):
        return {"value": None, "reason": "response_body_not_text"}
    complete_transport = context.get("complete_transport_body") is True
    try:
        payload = json.loads(text) if complete_transport else json.loads(
            text, object_pairs_hook=_object, parse_constant=_constant)
    except _DuplicateKey:
        return {"value": None, "reason": "duplicate_json_key"}
    except _NonFiniteNumber:
        return {"value": None, "reason": "non_finite_json_number"}
    except (json.JSONDecodeError, UnicodeError):
        return {"value": False if complete_transport else None, "reason": "invalid_json"}
    if not complete_transport and not _finite(payload):
        return {"value": None, "reason": "non_finite_json_number"}
    if not isinstance(payload, dict):
        return {"value": False, "reason": "response_not_object"}

    if operation == "browse_product":
        value = payload.get("id") == PRODUCT_ID
        return {"value": value, "reason": "product_id_matches" if value else "product_id_mismatch"}
    if operation == "add_to_cart":
        items = payload.get("items", [])
        value = isinstance(items, list) and any(
            isinstance(item, dict)
            and item.get("productId") == PRODUCT_ID
            and item.get("quantity") == 1
            for item in items
        )
        return {"value": value, "reason": "cart_contains_expected_item" if value else "cart_missing_expected_item"}

    order_id = payload.get("orderId") or payload.get("order_id")
    value = bool(order_id)
    return {"value": value, "reason": "checkout_order_id_present" if value else "checkout_order_id_missing"}
