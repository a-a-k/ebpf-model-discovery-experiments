"""Source-only shared-MySQL evidence and a resolved-compose endpoint baseline."""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from systems.petclinic.contracts_v3 import CONTRACTS, ENTRY_SERVICES

MYSQL_SYSTEMS = {"mysql", "mariadb"}
EXPECTED_DATABASE_NECESSITY = {
    "list_owners": True,
    "owner_details_with_visits": True,
    "create_visit": True,
    "list_vets": None,  # the vets application cache makes necessity unknown
}
OPERATION_SERVICES = {
    "list_owners": ["customers-service"],
    "owner_details_with_visits": ["customers-service", "visits-service"],
    "create_visit": ["visits-service"],
    "list_vets": ["vets-service"],
}
MANDATORY_REQUESTS = {
    "list_owners": {"customers-service": ("GET", "/owners")},
    "owner_details_with_visits": {
        "customers-service": ("GET", "/owners/6"),
        "visits-service": ("GET", "/pets/visits"),
    },
    "create_visit": {"visits-service": ("POST", "/owners/1/pets/1/visits")},
    "list_vets": {"vets-service": ("GET", "/vets")},
}


def _header(span: dict[str, Any]) -> str | None:
    for key, value in span.get("attributes", {}).items():
        if key.lower().replace("_", "-").endswith("x-experiment-request-id"):
            if isinstance(value, list):
                return value[0] if len(value) == 1 and isinstance(value[0], str) else None
            return value if isinstance(value, str) else None
    return None


def _method(span: dict[str, Any]) -> str | None:
    attrs = span.get("attributes", {})
    return attrs.get("http.request.method", attrs.get("http.method"))


def _path(span: dict[str, Any]) -> str | None:
    attrs = span.get("attributes", {})
    raw = attrs.get("url.path") or attrs.get("http.target") or attrs.get("url.full") or attrs.get("http.url")
    return urlsplit(str(raw)).path if raw else None


def _server(span: dict[str, Any]) -> bool:
    return str(span.get("kind")) in {"SPAN_KIND_SERVER", "2", "server"}


def _client(span: dict[str, Any]) -> bool:
    return str(span.get("kind")) in {"SPAN_KIND_CLIENT", "3", "client"}


def _semantic_record(span: dict[str, Any]) -> str:
    evidence = {key: value for key, value in span.items() if key not in {"raw_file", "_graph_node"}}
    return json.dumps(evidence, sort_keys=True, separators=(",", ":"), default=str)


def _operation(row: dict[str, Any]) -> str:
    declared = row.get("declared_operation_id", row.get("contract_id"))
    if row.get("contract_id") not in (None, declared):
        raise ValueError("conflicting operation declarations")
    if declared not in CONTRACTS:
        raise ValueError(f"unknown Petclinic operation: {declared}")
    return str(declared)


def _steps(row: dict[str, Any]) -> list[str]:
    values = row.get("step_ids")
    if not isinstance(values, list) or not values or not all(isinstance(value, str) and value for value in values):
        raise ValueError("step_ids must be a non-empty string list")
    expected = row.get("expected_step_count")
    if expected is not None and expected != len(values):
        raise ValueError("step_ids do not match expected_step_count")
    return values


def _window(row: dict[str, Any]) -> tuple[int, int]:
    start, end, deadline = (row.get(key) for key in ("started_ns", "ended_ns", "deadline_ns"))
    if not all(type(value) is int for value in (start, end, deadline)):
        raise ValueError("intent lifetime fields must be integer nanoseconds")
    if end < start or deadline < start:
        raise ValueError("invalid intent lifetime")
    return start, min(end, deadline)


def _in_window(span: dict[str, Any], window: tuple[int, int]) -> bool:
    start = int(span.get("start_ns", 0))
    end = int(span.get("end_ns", start))
    return window[0] <= start <= window[1] and start <= end <= window[1]


def _jdbc_endpoint(value: str) -> tuple[str, int] | None:
    match = re.match(r"jdbc:mysql://([^/:?]+)(?::(\d+))?/", value)
    return (match.group(1), int(match.group(2) or 3306)) if match else None


def endpoint_inventory(deployment_dir: str | Path) -> dict[str, Any]:
    """Read the deployed, resolved compose files; do not infer a manifest graph."""
    root = Path(deployment_dir)
    if (root / "petclinic").is_dir():
        root /= "petclinic"
    placement_path = root / "placement.json"
    placement = json.loads(placement_path.read_text(encoding="utf-8")) if placement_path.exists() else {}
    client_endpoints: dict[str, set[tuple[str, int]]] = defaultdict(set)
    aliases: set[tuple[str, int]] = {("database", 3306)}
    source_files = []
    for node in ("a", "b"):
        path = root / f"node-{node}" / "resolved-compose.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        source_files.append(str(path))
        for compose_name, service in document.get("services", {}).items():
            networks = service.get("networks", {})
            for network in networks.values() if isinstance(networks, dict) else ():
                if compose_name == "database" and isinstance(network, dict) and network.get("ipv4_address"):
                    aliases.add((str(network["ipv4_address"]), 3306))
            if compose_name == "database":
                for publication in service.get("ports", []):
                    parts = str(publication).rsplit(":", 2)
                    if len(parts) == 3:
                        aliases.add((parts[0], int(parts[1])))
            environment = service.get("environment", {})
            raw_properties = environment.get("SPRING_APPLICATION_JSON") if isinstance(environment, dict) else None
            if not raw_properties:
                continue
            properties = json.loads(raw_properties)
            endpoint = _jdbc_endpoint(str(properties.get("spring.datasource.url", "")))
            service_name = environment.get("OTEL_SERVICE_NAME", compose_name)
            if endpoint:
                client_endpoints[str(service_name)].add(endpoint)
    guest_a = placement.get("nodes", {}).get("a", {}).get("guest_ip")
    if guest_a:
        aliases.add((str(guest_a), 13306))
    return {
        "kind": "resolved_compose_endpoint_inventory",
        "source_files": source_files,
        "database_fault_aliases": [
            {"host": host, "port": port} for host, port in sorted(aliases)
        ],
        "service_database_endpoints": {
            service: [{"host": host, "port": port} for host, port in sorted(endpoints)]
            for service, endpoints in sorted(client_endpoints.items())
        },
        "operation_services": OPERATION_SERVICES,
        "expected_database_necessity": EXPECTED_DATABASE_NECESSITY,
    }


class _Index:
    def __init__(self, spans: list[dict[str, Any]]):
        variants: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
        self.headers: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for span in spans:
            source = span.get("source")
            if source not in ENTRY_SERVICES:
                continue
            identity = (source, span.get("trace_id", ""), span.get("span_id", ""))
            variants[identity].setdefault(_semantic_record(span), span)
        self.conflicts = {identity for identity, rows in variants.items() if len(rows) > 1}
        self.conflict_headers: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        self.children: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        self.blocked_children: set[tuple[str, str, str]] = set()
        self.rows = []
        for identity, rows in variants.items():
            if identity in self.conflicts:
                for span in rows.values():
                    request_id = _header(span)
                    if request_id:
                        self.conflict_headers[(span["source"], request_id)].append(span)
                    self.blocked_children.add(
                        (span["source"], span.get("trace_id", ""), span.get("parent_id", ""))
                    )
                continue
            span = next(iter(rows.values()))
            self.rows.append(span)
            self.children[(span["source"], span.get("trace_id", ""), span.get("parent_id", ""))].append(span)
            request_id = _header(span)
            if request_id:
                self.headers[(span["source"], request_id)].append(span)

    def descendants(self, seeds: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
        output, queue, seen, ambiguous = [], list(seeds), set(), False
        while queue:
            span = queue.pop()
            identity = (span["source"], span.get("trace_id", ""), span.get("span_id", ""))
            if identity in seen:
                continue
            seen.add(identity)
            output.append(span)
            parent_key = (span["source"], span.get("trace_id", ""), span.get("span_id", ""))
            children = self.children.get(parent_key, ())
            queue.extend(children)
            ambiguous |= parent_key in self.blocked_children
        return output, ambiguous


def _db_endpoint(span: dict[str, Any]) -> tuple[str, int] | None:
    attrs = span.get("attributes", {})
    system = str(attrs.get("db.system.name", attrs.get("db.system", ""))).lower()
    if system not in MYSQL_SYSTEMS:
        return None
    host = attrs.get("server.address", attrs.get("net.peer.name", attrs.get("net.peer.ip")))
    port = attrs.get("server.port", attrs.get("net.peer.port", 3306))
    try:
        return (str(host), int(port)) if host else None
    except (TypeError, ValueError):
        return None


def _attempt_evidence(index: _Index, source: str, row: dict[str, Any], aliases: set[tuple[str, int]]) -> dict[str, Any]:
    operation = _operation(row)
    steps = _steps(row)
    window = _window(row)
    declared = CONTRACTS[operation]["steps"][0]
    candidates = []
    request_rows = []
    for request_id in steps:
        if any(_in_window(span, window) for span in index.conflict_headers.get((source, request_id), ())):
            return {"bound": False, "reason": "conflicting_request_identity",
                    "database_endpoints": [], "database_services": []}
        rows = [span for span in index.headers.get((source, request_id), ()) if _in_window(span, window)]
        candidates.extend(span for span in rows if _server(span)
                          and span.get("service") in ENTRY_SERVICES[source]
                          and _method(span) == declared["method"] and _path(span) == declared["path"])
        request_rows.extend(rows)
    unique_entries = {
        (span.get("trace_id"), span.get("span_id")): span for span in candidates
    }
    if len(unique_entries) != 1:
        return {"bound": False, "reason": "entry_missing" if not unique_entries else "entry_ambiguous",
                "database_endpoints": [], "database_services": []}
    selected = []
    for service, method_path in MANDATORY_REQUESTS[operation].items():
        witnesses = [
            span for span in request_rows
            if span.get("service") == service and _server(span)
            and (_method(span), _path(span)) == method_path
        ]
        unique_witnesses = {
            (span.get("trace_id"), span.get("span_id")): span for span in witnesses
        }
        if len(unique_witnesses) != 1:
            continue
        descendants, ambiguous = index.descendants(list(unique_witnesses.values()))
        if ambiguous:
            return {"bound": False, "reason": "conflicting_descendant_identity",
                    "database_endpoints": [], "database_services": []}
        selected.extend(
            (span, endpoint) for span in descendants
            if span.get("service") == service and _client(span) and _in_window(span, window)
            and (endpoint := _db_endpoint(span)) in aliases
        )
    endpoints = sorted({endpoint for _, endpoint in selected})
    services = sorted({str(span.get("service")) for span, _ in selected})
    return {
        "bound": True,
        "reason": "selected_database_path_observed" if selected else "selected_database_path_not_observed",
        "database_endpoints": [{"host": host, "port": port} for host, port in endpoints],
        "database_services": services,
    }


def learn_database_effects(
    spans: list[dict[str, Any]],
    intent_rows: list[dict[str, Any]],
    inventory: dict[str, Any],
) -> dict[str, Any]:
    """Freeze operation-to-selected-DB evidence from a healthy training window."""
    aliases = {(row["host"], int(row["port"])) for row in inventory["database_fault_aliases"]}
    index = _Index(spans)
    effects: dict[str, dict[str, Any]] = {}
    for source in ENTRY_SERVICES:
        by_operation: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in intent_rows:
            by_operation[_operation(row)].append(_attempt_evidence(index, source, row, aliases))
        effects[source] = {}
        for operation in CONTRACTS:
            attempts = by_operation.get(operation, [])
            observed = [row for row in attempts if row["bound"] and row["database_endpoints"]]
            effects[source][operation] = {
                "selected_database_dependency": True if observed else None,
                "manual_database_necessity": EXPECTED_DATABASE_NECESSITY[operation],
                "attempts": len(attempts),
                "entry_bound": sum(row["bound"] for row in attempts),
                "database_path_observed": len(observed),
                "database_endpoints": sorted(
                    {json.dumps(endpoint, sort_keys=True) for row in observed for endpoint in row["database_endpoints"]}
                ),
                "database_services": sorted({service for row in observed for service in row["database_services"]}),
            }
            effects[source][operation]["database_endpoints"] = [
                json.loads(value) for value in effects[source][operation]["database_endpoints"]
            ]
    effects["combined"] = {}
    for operation in CONTRACTS:
        source_rows = [effects[source][operation] for source in ENTRY_SERVICES]
        effects["combined"][operation] = {
            "selected_database_dependency": (
                True if any(row["selected_database_dependency"] is True for row in source_rows) else None
            ),
            "manual_database_necessity": EXPECTED_DATABASE_NECESSITY[operation],
            "attempts": max(row["attempts"] for row in source_rows),
            "entry_bound": max(row["entry_bound"] for row in source_rows),
            "database_path_observed": max(row["database_path_observed"] for row in source_rows),
            "database_endpoints": sorted(
                {json.dumps(endpoint, sort_keys=True) for row in source_rows for endpoint in row["database_endpoints"]}
            ),
            "database_services": sorted({service for row in source_rows for service in row["database_services"]}),
        }
        effects["combined"][operation]["database_endpoints"] = [
            json.loads(value) for value in effects["combined"][operation]["database_endpoints"]
        ]
    model = {
        "schema_version": 1,
        "method": "petclinic-source-selected-database-v3",
        "frozen": True,
        "effects": effects,
        "static_endpoint_baseline": {
            operation: {
                "services": OPERATION_SERVICES[operation],
                "database_endpoints": sorted(
                    {json.dumps(endpoint, sort_keys=True)
                     for service in OPERATION_SERVICES[operation]
                     for endpoint in inventory["service_database_endpoints"].get(service, [])
                     if (endpoint["host"], int(endpoint["port"])) in aliases}
                ),
                "manual_database_necessity": EXPECTED_DATABASE_NECESSITY[operation],
            }
            for operation in CONTRACTS
        },
        "inventory": inventory,
    }
    for row in model["static_endpoint_baseline"].values():
        row["database_endpoints"] = [json.loads(value) for value in row["database_endpoints"]]
    model["model_sha256"] = hashlib.sha256(
        json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return model


def predict_database_effects(
    model: dict[str, Any], intent_rows: list[dict[str, Any]], database_up: bool
) -> list[dict[str, Any]]:
    """Predict only DB-caused failure; never substitute it for external business Y."""
    supplied_hash = model.get("model_sha256")
    content = {key: value for key, value in model.items() if key != "model_sha256"}
    actual_hash = hashlib.sha256(
        json.dumps(content, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if not model.get("frozen") or supplied_hash != actual_hash:
        raise ValueError("database model must be frozen before target prediction")
    output = []
    for row in intent_rows:
        operation = _operation(row)
        predictions = {}
        for source in (*ENTRY_SERVICES, "combined"):
            effect = model["effects"][source][operation]
            value = False if database_up else (
                True if effect["selected_database_dependency"] is True
                and effect["manual_database_necessity"] is True else None
            )
            predictions[source] = value
        baseline = model["static_endpoint_baseline"][operation]
        baseline_value = False if database_up else (
            True if baseline["database_endpoints"] and baseline["manual_database_necessity"] is True else None
        )
        output.append({
            "attempt_key": row["attempt_key"],
            "operation": operation,
            "database_up": database_up,
            "predicted_database_caused_failure": predictions,
            "static_endpoint_baseline": baseline_value,
            "external_business_outcome": None,
            "model_sha256": model["model_sha256"],
        })
    return output
