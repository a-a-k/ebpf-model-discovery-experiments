"""Evidence-bound compatibility helpers for graph-v4 contract binding.

These helpers do not discover structure or use outcomes.  Endpoint aliases are
accepted only when an exact request-ID-bound entry root supplies the observed
HTTP spelling.  Call hints are matched as complete protocol tokens.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

from .selection_v4 import canonical_route, method_path, valid_identity


_HTTP_HINT = re.compile(r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) (/.+)")
_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})
_PATH_ATTRIBUTES = ("http.route", "url.path", "http.target", "url.full", "http.url")


def _path(value: object) -> str | None:
    if value is None or value == "":
        return None
    path = urlsplit(str(value)).path
    # Bering represents HTTP endpoint paths with a leading slash, while some
    # frameworks expose an otherwise identical route token without one (for
    # example ``customers``).  Canonicalize that representation only; the
    # token still comes from the exact request-bound observation.
    if path and not path.startswith("/"):
        path = "/" + path
    return canonical_route(path)


def _method(identity: dict) -> str:
    return str(identity.get("operation") or identity.get("method") or "").upper()


def _rpc_parts(value: object) -> tuple[str, str] | None:
    text = str(value or "").strip().strip("/")
    if text.count("/") != 1:
        return None
    service, method = text.split("/", 1)
    if not service or not method or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", method):
        return None
    return service, method


def _rpc_service_matches(observed: str, expected: str,
                         permitted_services: tuple[str, ...]) -> bool:
    """Match the exact declared service or an explicitly supplied spelling."""
    allowed = {expected, *(str(item).strip().strip("/") for item in permitted_services)}
    return observed in allowed


def matches_call_hint(identity: dict, hint: str, *,
                      permitted_services: tuple[str, ...] = ()) -> tuple[bool, str | None]:
    """Match a declared call hint to one recovered edge identity.

    HTTP hints retain exact method+canonical-route behavior.  RPC hints accept
    either an exact RPC method identity (the callee was resolved separately) or
    the common gRPC-over-HTTP server representation ``POST /pkg.Service/Method``.
    The latter keeps the observed HTTP protocol; it is compatibility evidence,
    not a rewrite to gRPC.
    """
    http = _HTTP_HINT.fullmatch(str(hint or ""))
    if http:
        observed_path = _path(identity.get("route") or identity.get("path"))
        matched = (_method(identity), observed_path) == (http.group(1), _path(http.group(2)))
        return matched, "http_method_route_exact" if matched else None

    expected = _rpc_parts(hint)
    if expected is None:
        return False, None
    expected_service, expected_method = expected

    rpc_service = identity.get("rpc.service") or identity.get("rpc_service")
    rpc_method = identity.get("rpc.method") or identity.get("rpc_method")
    if rpc_method is not None:
        if str(rpc_method) != expected_method:
            return False, None
        if rpc_service is not None and not _rpc_service_matches(
                str(rpc_service), expected_service, permitted_services):
            return False, None
        return True, "rpc_method_token_exact"

    operation = str(identity.get("operation") or "")
    operation_rpc = _rpc_parts(operation)
    if operation_rpc is not None:
        matched = (operation_rpc[1] == expected_method and _rpc_service_matches(
            operation_rpc[0], expected_service, permitted_services))
        return matched, "rpc_service_method_exact" if matched else None
    if operation == expected_method:
        return True, "rpc_method_token_exact"

    # Several SDKs expose a gRPC server as an HTTP server span.  Require POST and
    # a complete /Service/Method route; GET and substring matches are rejected.
    route_rpc = _rpc_parts(_path(identity.get("route") or identity.get("path")))
    if (_method(identity) == "POST" and route_rpc is not None
            and route_rpc[1] == expected_method
            and _rpc_service_matches(route_rpc[0], expected_service, permitted_services)):
        return True, "rpc_over_http_post_route_exact"
    return False, None


def endpoint_alias_evidence(store, roots: list[dict], step: dict,
                            entry_service: str, endpoints: list[dict]) -> dict:
    """Return model endpoint IDs evidenced by exact bound entry roots.

    Multiple endpoint IDs can be aliases of the same expected entry step.  All
    are retained; cardinality alone is not ambiguity.  A root is usable only if
    its selection evidence and the indexed observation agree on source identity,
    request ID, service, method, and expected concrete path.
    """
    expected_method = str(step.get("method") or "").upper()
    expected_path = _path(step.get("path"))
    evidence, endpoint_ids = [], set()
    for root in roots:
        if (root.get("binding_reason") != "unique_declared_entry"
                or root.get("service") != entry_service
                or str(root.get("method") or "").upper() != expected_method
                or _path(root.get("path")) != expected_path
                or not root.get("request_id")
                or not valid_identity(root.get("trace_id"), root.get("span_id"))):
            continue
        variants = store.identity(root.get("source"), root.get("trace_id"), root.get("span_id"))
        if len(variants) != 1:
            continue
        row = variants[0]
        if row.get("attribute_conflicts") or row.get("service") != entry_service:
            continue
        candidates = store.candidates(root.get("source"), root["request_id"])
        if not any((item.get("trace_id"), item.get("span_id"))
                   == (root.get("trace_id"), root.get("span_id")) for item in candidates):
            continue
        indexed_method, indexed_path = method_path(row)
        if (str(indexed_method or "").upper(), indexed_path) != (expected_method, expected_path):
            continue
        attrs = row.get("attributes", {})
        observed_method = str(attrs.get("http.request.method", attrs.get("http.method", ""))).upper()
        if observed_method != expected_method:
            continue
        aliases = []
        for attribute in _PATH_ATTRIBUTES:
            value = attrs.get(attribute)
            path = _path(value)
            if path and (attribute, str(value), path) not in {
                    (item["attribute"], item["value"], item["path"]) for item in aliases}:
                aliases.append({"attribute": attribute, "value": str(value), "path": path})
        matched = []
        for endpoint in endpoints:
            if (endpoint.get("entry_service") == entry_service
                    and str(endpoint.get("method") or "").upper() == expected_method
                    and any(_path(endpoint.get("path")) == alias["path"] for alias in aliases)):
                matched.append(endpoint["id"])
        if not matched:
            continue
        endpoint_ids.update(matched)
        evidence.append({
            "basis": "exact_request_bound_entry_endpoint_alias",
            "expected_step": {"method": expected_method, "path": expected_path},
            "entry_service": entry_service,
            "endpoint_ids": sorted(set(matched)),
            "observed_aliases": aliases,
            "provenance": {
                "source": root.get("source"), "request_id": root.get("request_id"),
                "trace_id": root.get("trace_id"), "span_id": root.get("span_id"),
                "node": row.get("node"), "raw_file": row.get("raw_file"),
            },
        })
    return {
        "endpoint_ids": sorted(endpoint_ids),
        "evidence": evidence,
        "basis": "exact request-ID-bound roots only; no global route alias heuristic",
    }
