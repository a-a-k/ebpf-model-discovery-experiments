"""Declared DeathStarBench HTTP completion contracts for source-only observations.

The caller must bind an actual, complete response body to the unique nginx entry
span and check the attempt deadline. Evaluator response bytes are never inputs.
"""

from __future__ import annotations

import json
import math
from typing import Any


ENTRY_SERVICES = {"ebpf": ["nginx-thrift"], "native": ["nginx-web-server"]}
# The pinned nginx OpenTracing exporter emits no span.kind. Its HTTP boundary
# is the outermost same-process component=nginx ancestor, proved by parent IDs.
UNTYPED_ENTRY_COMPONENTS = {"native": ["nginx"]}
STABLE_FIXTURE_TEXT = "ebpf-study-stable-timeline-fixture-v1"
ACKNOWLEDGEMENT = "Successfully upload post"

CONTRACTS = {
    "compose_post": {
        "steps": [{"method": "POST", "path": "/wrk2-api/post/compose"}],
        "response_kind": "text",
    },
    "read_home_timeline": {
        "steps": [{"method": "GET", "path": "/wrk2-api/home-timeline/read"}],
        "response_kind": "json",
    },
    "read_user_timeline": {
        "steps": [{"method": "GET", "path": "/wrk2-api/user-timeline/read"}],
        "response_kind": "json",
    },
}


def status_ok(operation: str, step_index: int, code: Any) -> bool:
    """Match the adapter's requests.Response.ok predicate for an HTTP status."""
    CONTRACTS[operation]["steps"][step_index]
    return type(code) is int and 100 <= code < 400


class _InvalidJSON(ValueError):
    pass


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _InvalidJSON("duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise _InvalidJSON(f"nonstandard JSON constant: {value}")


def payload_verdict(operation: str, text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the declared body predicate after source binding/completeness checks.

    A malformed JSON body is unknown because the caller may have received an
    incomplete capture. A well-formed body that fails the predicate is false.
    The context is reserved for contract versioning; no evaluator fields are read.
    """
    complete_transport = context.get("complete_transport_body") is True
    kind = CONTRACTS[operation]["response_kind"]
    if not isinstance(text, str):
        return {"value": None, "reason": "response body is not text"}
    if kind == "text":
        value = ACKNOWLEDGEMENT in text
        return {"value": value, "reason": "compose acknowledgement present" if value else "compose acknowledgement absent"}
    try:
        body = json.loads(text) if complete_transport else json.loads(
            text, object_pairs_hook=_unique_pairs, parse_constant=_invalid_constant)
    except (ValueError, TypeError, RecursionError) as exc:
        return {"value": False if complete_transport else None, "reason": f"invalid or incomplete timeline JSON: {exc}"}
    def finite(value):
        if isinstance(value, float):
            return math.isfinite(value)
        if isinstance(value, list):
            return all(finite(v) for v in value)
        if isinstance(value, dict):
            return all(finite(v) for v in value.values())
        return True
    if not complete_transport and not finite(body):
        return {"value": None, "reason": "nonfinite timeline JSON number"}
    valid_shape = isinstance(body, list) and all(
        isinstance(item, dict)
        and isinstance(item.get("post_id"), str)
        and isinstance(item.get("text"), str)
        for item in body
    )
    value = valid_shape and any(item["text"] == STABLE_FIXTURE_TEXT for item in body)
    return {"value": value, "reason": "stable fixture in valid timeline" if value else "stable fixture or timeline shape absent"}
