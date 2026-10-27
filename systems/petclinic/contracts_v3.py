"""Fixed Petclinic operation contracts for source-only completion binding."""
from __future__ import annotations

import json
import math
from typing import Any

from systems.petclinic.adapter import _canonical

ENTRY_SERVICES = {"ebpf": ["api-gateway"], "native": ["api-gateway"]}

CONTRACTS = {
    "list_owners": {
        "steps": [{"method": "GET", "path": "/api/customer/owners"}],
        "response_kind": "json",
    },
    "owner_details_with_visits": {
        "steps": [{"method": "GET", "path": "/api/gateway/owners/6"}],
        "response_kind": "json",
    },
    "create_visit": {
        "steps": [{"method": "POST", "path": "/api/visit/owners/1/pets/1/visits"}],
        "response_kind": "json",
    },
    "list_vets": {
        "steps": [{"method": "GET", "path": "/api/vet/vets"}],
        "response_kind": "json",
    },
}

_FIXTURE_KEYS = {
    "list_owners": "owners",
    "owner_details_with_visits": "details",
    "list_vets": "vets",
}


def _reject_constant(value: str) -> None:
    raise ValueError(f"non_finite_json_constant:{value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _reject_nonfinite(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non_finite_json_number")
    if isinstance(value, list):
        for item in value:
            _reject_nonfinite(item)
    elif isinstance(value, dict):
        for item in value.values():
            _reject_nonfinite(item)
    return value


def strict_json(text: str) -> Any:
    """Parse one JSON value while rejecting duplicate keys and non-finite numbers."""
    if not isinstance(text, str):
        raise TypeError("body_must_be_text")
    return _reject_nonfinite(
        json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    )


def status_ok(operation: str, step_index: int, code: int | None) -> bool:
    """Apply the original exact HTTP predicate for a declared operation step."""
    if operation not in CONTRACTS:
        raise ValueError(f"unknown Petclinic operation: {operation}")
    if step_index != 0:
        raise IndexError("Petclinic contracts contain exactly one external HTTP step")
    return code == (201 if operation == "create_visit" else 200)


def payload_verdict(operation: str, text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Evaluate an observed complete body without consulting external outcomes."""
    if operation not in CONTRACTS:
        raise ValueError(f"unknown Petclinic operation: {operation}")
    complete_transport = context.get("complete_transport_body") is True
    try:
        payload = json.loads(text) if complete_transport else strict_json(text)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return {"value": False if complete_transport else None, "reason": f"unusable_captured_json:{exc}"}

    if operation == "create_visit":
        # These are necessary response facts, not proof of durable persistence.
        if not isinstance(payload, dict):
            return {"value": False, "reason": "acknowledgement_not_object"}
        acknowledged_id = payload.get("id")
        date = payload.get("date")
        if not (
            type(acknowledged_id) is int and acknowledged_id > 0
            and payload.get("petId") == 1
            and isinstance(date, str) and date[:10] == "2026-09-01"
            and isinstance(payload.get("description"), str)
        ):
            return {"value": False, "reason": "acknowledgement_contract_mismatch"}
        attempt_key = context.get("attempt_key")
        if not (
            isinstance(attempt_key, str) and len(attempt_key) == 64
            and all(character in "0123456789abcdef" for character in attempt_key)
        ):
            return {"value": None, "reason": "attempt_identity_unavailable"}
        # The adapter's marker is exactly this already-supplied opaque attempt
        # identity. No SQL result or evaluator success label supplies the value.
        if payload["description"] != "ebpf-study-" + attempt_key:
            return {"value": False, "reason": "acknowledgement_identity_mismatch"}
        return {"value": None, "reason": "persistence_requires_independent_sql_oracle"}

    fixture = context.get("fixture")
    if not isinstance(fixture, dict):
        return {"value": None, "reason": "fixture_unavailable"}
    try:
        _canonical(payload, fixture[_FIXTURE_KEYS[operation]])
    except KeyError:
        return {"value": None, "reason": "fixture_unavailable"}
    except (TypeError, ValueError) as exc:
        return {"value": False, "reason": f"payload_contract_mismatch:{exc}"}
    return {"value": True, "reason": "complete_payload_matches_pinned_fixture"}
