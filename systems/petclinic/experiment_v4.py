"""Iteration-4 Petclinic adapter and structural operation contracts.

The deployment remains the pinned v3 application build.  This subclass removes
study-injected request deadlines and gateway recovery filters while preserving
the upstream application's own owner-details fallback.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

import requests

from systems.petclinic.adapter import Adapter as V3Adapter
from systems.petclinic.adapter import IPS, OPERATIONS, _canonical, _require_actions
from systems.petclinic.database_v3 import endpoint_inventory


SERVICE_ALIASES = {
    "gateway": ["api-gateway", "gateway"],
    "customers": ["customers-service", "customers"],
    "visits": ["visits-service", "visits-a", "visits-b", "visits"],
    "vets": ["vets-service", "vets"],
}
CONTROLLED_SERVICE = "visits-service"
CONTROLLED_SERVICE_ALIASES = tuple(SERVICE_ALIASES["visits"])
SELECTED_DATABASE = {"db_system": "mysql", "db_role": "shared",
                     "container": "database", "fault_scope": "whole_database_container"}
ENTRY_SERVICES = {"ebpf": SERVICE_ALIASES["gateway"], "native": SERVICE_ALIASES["gateway"]}


def _service_call(caller: str, callee: str) -> dict[str, Any]:
    return {"caller": SERVICE_ALIASES[caller], "callee": SERVICE_ALIASES[callee]}


def _database_call(caller: str, role: str) -> dict[str, Any]:
    return {"caller": SERVICE_ALIASES[caller], "db_system": "mysql", "db_role": role}


CONTRACTS: dict[str, dict[str, Any]] = {
    "list_owners": {
        "steps": [{"method": "GET", "path": "/api/customer/owners"}],
        "entry_services": SERVICE_ALIASES["gateway"],
        "required_calls": [_service_call("gateway", "customers"), _database_call("customers", "read")],
    },
    "owner_details_with_visits": {
        "steps": [{"method": "GET", "path": "/api/gateway/owners/6"}],
        "entry_services": SERVICE_ALIASES["gateway"],
        "required_calls": [
            _service_call("gateway", "customers"),
            _service_call("gateway", "visits"),
            _database_call("customers", "read"),
            _database_call("visits", "read"),
        ],
    },
    "create_visit": {
        "steps": [{"method": "POST", "path": "/api/visit/owners/1/pets/1/visits"}],
        "entry_services": SERVICE_ALIASES["gateway"],
        "required_calls": [_service_call("gateway", "visits"), _database_call("visits", "write")],
    },
    "list_vets": {
        "steps": [{"method": "GET", "path": "/api/vet/vets"}],
        "entry_services": SERVICE_ALIASES["gateway"],
        "required_calls": [_service_call("gateway", "vets")],
        "conditional_db": {
            "condition": "vets_cache_miss",
            "call": _database_call("vets", "read"),
            "unobserved_condition": "unknown",
        },
    },
}


def shared_database_inventory(deployment_dir: str | Path) -> dict[str, Any]:
    """Return deployment-attributed aliases without manufacturing graph structure."""
    inventory = endpoint_inventory(deployment_dir)
    return {
        "kind": "shared_mysql_deployment_attribution",
        "database_system": "mysql",
        "database_fault_aliases": inventory["database_fault_aliases"],
        "service_database_endpoints": inventory["service_database_endpoints"],
        "source_files": inventory["source_files"],
        "attachment_rule": "metadata_only_on_recovered_nodes_and_database_dependencies",
        "physical_identity_claim": None,
        "limitations": [
            "matching deployment aliases do not independently prove one physical database instance",
            "inventory never creates a graph node or edge",
        ],
    }


# Stable name for common orchestration without embedding an expected graph.
database_inventory = shared_database_inventory


class Adapter(V3Adapter):
    """No-deadline v4 driver retaining v3 deployment and native collection."""

    @staticmethod
    def plan_operation(name: str, index: int, namespace: str) -> dict[str, Any]:
        if name not in CONTRACTS:
            raise ValueError(f"Unknown Petclinic operation: {name}")
        attempt_id = f"{namespace}-{index}-{name}"
        request_id = "req-" + hashlib.sha256(("http-step:" + attempt_id).encode()).hexdigest()
        step = CONTRACTS[name]["steps"][0]
        return {
            "attempt_id": attempt_id,
            "operation": name,
            "http_steps": [{"request_id": request_id, "method": step["method"], "path": step["path"]}],
        }

    def _spring_environment(
        self,
        service: str,
        instance: str,
        collector_ip: str,
        instrumented: bool,
        database_endpoint: str | None = None,
    ) -> dict[str, str]:
        environment = super()._spring_environment(service, instance, collector_ip, instrumented, database_endpoint)
        if service != "api-gateway":
            return environment
        properties = json.loads(environment["SPRING_APPLICATION_JSON"])
        properties.pop("spring.cloud.gateway.server.webflux.default-filters", None)
        for route in properties.get("spring.cloud.gateway.server.webflux.routes", []):
            route["filters"] = [item for item in route.get("filters", []) if item == "StripPrefix=2"]
        environment["SPRING_APPLICATION_JSON"] = json.dumps(properties, separators=(",", ":"))
        return environment

    def _write_deployment_assets(self) -> None:
        super()._write_deployment_assets()
        guest_b = self.ctx.node_ip("b")
        # HAProxy's zero timeout means disabled.  There is no study-imposed
        # request/response clock; health checks only select a reachable replica.
        (self.assets / "node-a" / "haproxy.cfg").write_text(
            f"""global
  maxconn 1024
defaults
  mode http
  timeout connect 0
  timeout client 0
  timeout server 0
  retries 0
frontend visits
  bind *:8080
  default_backend visits_replicas
backend visits_replicas
  balance roundrobin
  option http-server-close
  option redispatch
  server visits_a {IPS['visits_a']}:8080 check inter 500ms fall 1 rise 1
  server visits_b {guest_b}:18081 check inter 500ms fall 1 rise 1
""",
            encoding="utf-8",
        )

    def ready(self) -> None:
        """Run bounded technical probes without invoking scored operations."""
        _require_actions()
        self.fixture = self.fixture or json.loads((self.assets / "fixture.json").read_text(encoding="utf-8"))
        self._wait_replica_ports({"a": IPS["visits_a"], "b": IPS["visits_b"]}, 180)
        stop = time.monotonic() + 420
        last: list[dict[str, Any]] = []
        while time.monotonic() < stop:
            last = [self._readiness_probe(name) for name in ("list_owners", "owner_details_with_visits", "list_vets")]
            if all(item["ready"] is True for item in last):
                return
            time.sleep(5)
        raise RuntimeError("Petclinic failed seed-derived technical readiness probes: " + json.dumps(last))

    def _readiness_probe(self, name: str) -> dict[str, Any]:
        """Check deployed application health; results never enter experiment records."""
        step = CONTRACTS[name]["steps"][0]
        fixture_key = {
            "list_owners": "owners",
            "owner_details_with_visits": "details",
            "list_vets": "vets",
        }[name]
        url = f"http://{self.ctx.node_ip('a')}:18080{step['path']}"
        try:
            response = requests.request(
                step["method"], url,
                headers={"Connection": "close", "X-Technical-Probe": "readiness"},
                timeout=5.0,
            )
            if response.status_code != 200:
                return {"operation": name, "ready": False, "status": response.status_code}
            _canonical(response.json(), self.fixture[fixture_key])
            return {"operation": name, "ready": True, "status": response.status_code}
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError, TypeError, ValueError) as exc:
            return {"operation": name, "ready": False, "error": f"{type(exc).__name__}: {exc}"}

    def operation(self, name: str, index: int, namespace: str, deadline: float | None = None) -> dict[str, Any]:
        _require_actions()
        if deadline is not None:
            raise ValueError("iteration-4 operations do not accept experiment deadlines")
        plan = self.plan_operation(name, index, namespace)
        self.fixture = self.fixture or json.loads((self.assets / "fixture.json").read_text(encoding="utf-8"))
        step = plan["http_steps"][0]
        digest = hashlib.sha256(plan["attempt_id"].encode()).hexdigest()
        marker = "ebpf-study-" + digest
        request_json = {"date": "2026-09-01", "description": marker} if name == "create_visit" else None
        url = f"http://{self.ctx.node_ip('a')}:18080{step['path']}"
        started_ns = time.time_ns()
        response: requests.Response | None = None
        payload: Any = None
        raw = b""
        error: str | None = None
        transport_complete = False
        try:
            from ebpf_discovery.transport_v4 import request

            response = request(
                step["method"],
                url,
                journal=self.ctx.journal,
                json=request_json,
                headers={"X-Experiment-Request-Id": step["request_id"], "Connection": "close"},
                timeout=None,
            )
            raw = response.content
            transport_complete = True
            try:
                payload = response.json()
            except (requests.exceptions.JSONDecodeError, ValueError) as exc:
                error = f"{type(exc).__name__}: {exc}"
        except requests.exceptions.RequestException as exc:
            error = f"{type(exc).__name__}: {exc}"
        ended_ns = time.time_ns()
        status = response.status_code if response is not None else None
        success: bool | None = None
        validation: dict[str, Any] = {"kind": "payload", "valid": False}
        if transport_complete:
            if name == "create_visit":
                acknowledgement_matches = _visit_acknowledgement_matches(payload, marker)
                if status == 201 and error is None and acknowledgement_matches:
                    validation = {"kind": "sql_exact_row", "state": "pending", "marker": marker}
                else:
                    success = False
                    validation = {
                        "kind": "sql_exact_row",
                        "state": "http_failed",
                        "marker": marker,
                        "response_identity_match": acknowledgement_matches,
                    }
            elif status == 200 and error is None:
                fixture_key = {
                    "list_owners": "owners",
                    "owner_details_with_visits": "details",
                    "list_vets": "vets",
                }[name]
                try:
                    _canonical(payload, self.fixture[fixture_key])
                    success = True
                    validation = {"kind": "payload", "valid": True, "fixture": fixture_key}
                except (KeyError, TypeError, ValueError) as exc:
                    success = False
                    error = f"semantic_validation: {exc}"
            else:
                success = False
        return {
            **plan,
            "started_ns": started_ns,
            "ended_ns": ended_ns,
            "success": success,
            "http_steps": [{
                **step,
                "url": url,
                "request_json": request_json,
                "status": status,
                "started_ns": started_ns,
                "ended_ns": ended_ns,
                "response_body_base64": base64.b64encode(raw).decode(),
                "response_content_type": response.headers.get("content-type") if response is not None else None,
                "transport_complete": transport_complete,
            }],
            "error": error,
            "validation": validation,
            "response_json": payload,
        }

    def verify(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Verify every acknowledged create against one exact post-request SQL census."""
        _require_actions()
        verified = copy.deepcopy(records)
        candidates: list[tuple[dict[str, Any], str]] = []
        for row in verified:
            if row.get("operation") != "create_visit" or row.get("success") is False:
                continue
            steps = row.get("http_steps", [])
            if not steps or steps[0].get("transport_complete") is not True:
                # An unresolved request supplies no evidence that the write did
                # or did not commit.  A later census must not turn transport
                # incompleteness into a fabricated terminal outcome.
                row["success"] = None
                continue
            marker = row.get("validation", {}).get("marker", "")
            if not re.fullmatch(r"ebpf-study-[0-9a-f]{64}", marker):
                row["success"] = False
                row["error"] = "invalid_or_missing_write_marker"
                continue
            candidates.append((row, marker))
        groups = {marker: [] for _, marker in candidates}
        errors: dict[str, str] = {}
        query_times: dict[str, dict[str, int]] = {}
        markers = sorted(groups)
        for offset in range(0, len(markers), 100):
            chunk = markers[offset:offset + 100]
            quoted = ",".join(f"'{marker}'" for marker in chunk)
            sql = (
                "SELECT description,id,pet_id,DATE_FORMAT(visit_date,'%Y-%m-%d') FROM visits "
                f"WHERE description IN ({quoted}) ORDER BY description,id"
            )
            started = time.time_ns()
            try:
                result = self._mysql(sql)
                completed = time.time_ns()
            except Exception as exc:  # noqa: BLE001 - technical oracle loss is unknown
                completed = time.time_ns()
                for marker in chunk:
                    query_times[marker] = {"query_started_ns": started, "query_completed_ns": completed}
                    errors[marker] = str(exc)
                continue
            for marker in chunk:
                query_times[marker] = {"query_started_ns": started, "query_completed_ns": completed}
            malformed = False
            for line in getattr(result, "stdout", "").splitlines():
                fields = line.split("\t")
                if len(fields) != 4 or fields[0] not in chunk:
                    malformed = True
                    continue
                try:
                    groups[fields[0]].append({
                        "description": fields[0], "id": int(fields[1]),
                        "petId": int(fields[2]), "date": fields[3],
                    })
                except ValueError:
                    malformed = True
            if malformed:
                for marker in chunk:
                    errors[marker] = "sql_census_parse_error"
        for row, marker in candidates:
            timing = query_times[marker]
            if marker in errors:
                row["success"] = None
                row["validation"] = {
                    "kind": "sql_exact_row", "state": "oracle_unavailable", "marker": marker,
                    "error": errors[marker], **timing,
                }
                continue
            rows = groups[marker]
            payload = row.get("response_json")
            response_match = _visit_acknowledgement_matches(payload, marker)
            acknowledged_id = payload.get("id") if isinstance(payload, dict) else None
            database_match = (
                len(rows) == 1 and rows[0]["petId"] == 1 and rows[0]["date"] == "2026-09-01"
                and rows[0]["description"] == marker and rows[0]["id"] == acknowledged_id
            )
            exact = response_match and database_match
            row["success"] = bool(exact)
            row["validation"] = {
                "kind": "sql_exact_row", "state": "verified", "marker": marker,
                "row_count": len(rows), "rows": rows, "acknowledged_id": acknowledged_id,
                "response_identity_match": response_match,
                "database_exactly_once_contract_match": database_match,
                "exactly_once_and_identity_match": exact,
                **timing,
            }
            if exact:
                row["validation"]["database_commit_time_interval_ns"] = {
                    "lower": None,
                    "upper": timing["query_completed_ns"],
                    "meaning": "first positive SQL census only bounds commit from above",
                }
            elif not row.get("error"):
                row["error"] = "write_not_persisted_exactly_once_with_acknowledged_identity"
        return verified


def _visit_acknowledgement_matches(payload: Any, marker: str) -> bool:
    return (
        isinstance(payload, dict)
        and type(payload.get("id")) is int
        and payload["id"] > 0
        and payload.get("petId") == 1
        and isinstance(payload.get("date"), str)
        and payload["date"][:10] == "2026-09-01"
        and payload.get("description") == marker
    )
