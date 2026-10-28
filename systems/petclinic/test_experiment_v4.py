from __future__ import annotations

import json
import sys
from types import ModuleType, SimpleNamespace

import pytest
import requests

from systems.petclinic import experiment_v4
from systems.petclinic.experiment_v4 import Adapter, CONTRACTS, shared_database_inventory


def context(tmp_path):
    return SimpleNamespace(
        deployment_dir=tmp_path,
        out=tmp_path,
        mode="full",
        journal=object(),
        node_ip=lambda node: {"a": "192.0.2.11", "b": "192.0.2.12"}[node],
    )


def test_plan_operation_is_deterministic_and_matches_contract():
    first = Adapter.plan_operation("owner_details_with_visits", 17, "target-10")
    second = Adapter.plan_operation("owner_details_with_visits", 17, "target-10")
    assert first == second
    assert first["attempt_id"] == "target-10-17-owner_details_with_visits"
    assert first["http_steps"] == [{
        "request_id": "req-764c1c965dfabb6ef67823bcf2847b3bc4653828ed376081bee3a529e378c4ad",
        "method": "GET",
        "path": "/api/gateway/owners/6",
    }]
    assert first["http_steps"][0]["method"] == CONTRACTS[first["operation"]]["steps"][0]["method"]


def test_contracts_retain_two_shared_database_callers_and_conditional_vets():
    details = CONTRACTS["owner_details_with_visits"]["required_calls"]
    db_callers = {tuple(call["caller"]) for call in details if call.get("db_system") == "mysql"}
    assert db_callers == {("customers-service", "customers"), ("visits-service", "visits-a", "visits-b", "visits")}
    assert CONTRACTS["create_visit"]["required_calls"][-1]["db_role"] == "write"
    assert not any("db_system" in call for call in CONTRACTS["list_vets"]["required_calls"])
    assert CONTRACTS["list_vets"]["conditional_db"]["unobserved_condition"] == "unknown"


def test_v4_gateway_removes_only_study_injected_retry_and_circuit_breakers(tmp_path):
    adapter = Adapter(context(tmp_path))
    environment = adapter._spring_environment("api-gateway", "gateway-a", "172.28.11.30", True)
    properties = json.loads(environment["SPRING_APPLICATION_JSON"])
    assert "spring.cloud.gateway.server.webflux.default-filters" not in properties
    routes = properties["spring.cloud.gateway.server.webflux.routes"]
    assert routes and all(route["filters"] == ["StripPrefix=2"] for route in routes)


def test_v4_haproxy_disables_request_clock_limits(tmp_path, monkeypatch):
    adapter = Adapter(context(tmp_path))
    (adapter.assets / "node-a").mkdir(parents=True)
    monkeypatch.setattr(experiment_v4.V3Adapter, "_write_deployment_assets", lambda _self: None)
    adapter._write_deployment_assets()
    config = (adapter.assets / "node-a" / "haproxy.cfg").read_text(encoding="utf-8")
    assert "timeout client 0" in config
    assert "timeout server 0" in config
    assert "timeout client 3s" not in config


def test_operation_uses_planned_id_unbounded_transport_and_full_body(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    adapter = Adapter(context(tmp_path))
    adapter.assets.mkdir(parents=True)
    fixture = {"owners": [{"id": 1}], "details": {}, "vets": [], "seed_sha256": {}}
    (adapter.assets / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(fixture["owners"]).encode()
    response.headers["content-type"] = "application/json"
    calls = []

    transport = ModuleType("ebpf_discovery.transport_v4")

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return response

    transport.request = request
    monkeypatch.setitem(sys.modules, "ebpf_discovery.transport_v4", transport)
    row = adapter.operation("list_owners", 3, "healthy", deadline=None)
    plan = adapter.plan_operation("list_owners", 3, "healthy")
    assert row["attempt_id"] == plan["attempt_id"]
    assert row["http_steps"][0]["request_id"] == plan["http_steps"][0]["request_id"]
    assert row["success"] is True
    assert calls[0][2]["timeout"] is None
    assert calls[0][2]["journal"] is adapter.ctx.journal
    assert calls[0][2]["headers"]["X-Experiment-Request-Id"] == plan["http_steps"][0]["request_id"]


def test_operation_rejects_reintroduced_deadline(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(ValueError, match="do not accept experiment deadlines"):
        Adapter(context(tmp_path)).operation("list_vets", 1, "target", deadline=10)


def test_verify_requires_unique_exact_sql_identity_without_elapsed_gate(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    adapter = Adapter(context(tmp_path))
    marker = "ebpf-study-" + "a" * 64
    adapter._mysql = lambda _sql: SimpleNamespace(stdout=f"{marker}\t42\t1\t2026-09-01\n")
    row = {
        "operation": "create_visit", "success": None, "error": None,
        "started_ns": 1, "ended_ns": 10**20,
        "http_steps": [{"status": 201, "transport_complete": True}],
        "response_json": {"id": 42, "petId": 1, "date": "2026-09-01", "description": marker},
        "validation": {"kind": "sql_exact_row", "state": "pending", "marker": marker},
    }
    verified = adapter.verify([row])[0]
    assert verified["success"] is True
    assert verified["validation"]["exactly_once_and_identity_match"] is True
    assert "deadline_seconds" not in verified


def test_verify_does_not_reclassify_incomplete_create_transport(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    adapter = Adapter(context(tmp_path))
    adapter._mysql = lambda _sql: pytest.fail("unresolved transport must not trigger a SQL classification")
    row = {
        "operation": "create_visit", "success": None, "error": "ConnectionError: incomplete",
        "http_steps": [{"status": None, "transport_complete": False}],
        "validation": {"kind": "payload", "valid": False},
    }
    verified = adapter.verify([row])[0]
    assert verified["success"] is None
    assert verified["error"] == "ConnectionError: incomplete"


def test_shared_database_inventory_is_metadata_only(tmp_path):
    root = tmp_path / "petclinic"
    for node in ("a", "b"):
        folder = root / f"node-{node}"
        folder.mkdir(parents=True)
        services = {}
        if node == "a":
            services = {
                "database": {"networks": {"application": {"ipv4_address": "172.28.11.20"}}},
                "customers": {"environment": {
                    "OTEL_SERVICE_NAME": "customers-service",
                    "SPRING_APPLICATION_JSON": json.dumps({"spring.datasource.url": "jdbc:mysql://database:3306/petclinic"}),
                }},
                "visits-a": {"environment": {
                    "OTEL_SERVICE_NAME": "visits-service",
                    "SPRING_APPLICATION_JSON": json.dumps({"spring.datasource.url": "jdbc:mysql://database:3306/petclinic"}),
                }},
            }
        (folder / "resolved-compose.json").write_text(json.dumps({"services": services}), encoding="utf-8")
    inventory = shared_database_inventory(tmp_path)
    assert set(inventory["service_database_endpoints"]) == {"customers-service", "visits-service"}
    assert inventory["physical_identity_claim"] is None
    assert "graph" not in inventory
    assert "inventory never creates a graph node or edge" in inventory["limitations"]
