import json

import pytest

from systems.petclinic.database_v3 import (
    endpoint_inventory,
    learn_database_effects,
    predict_database_effects,
)


def span(sid, parent, service, kind, request_id=None, path=None, db=False):
    attrs = {}
    if request_id:
        attrs["http.request.header.x-experiment-request-id"] = [request_id]
    if path:
        attrs.update({"http.request.method": "GET", "url.path": path})
    if db:
        attrs.update({"db.system.name": "mysql", "server.address": "database", "server.port": 3306})
    return {
        "source": "ebpf", "node": "a", "trace_id": "trace", "span_id": sid,
        "parent_id": parent, "service": service, "kind": kind, "name": sid,
        "start_ns": 110, "end_ns": 120, "attributes": attrs, "status": {},
    }


def intent(operation="list_owners"):
    return {
        "attempt_key": "attempt-1", "step_ids": ["req-1"], "contract_id": operation,
        "phase": "class_train", "state": "11", "started_ns": 100,
        "ended_ns": 200, "deadline_ns": 200,
    }


def inventory_value():
    return {
        "database_fault_aliases": [{"host": "database", "port": 3306}],
        "service_database_endpoints": {
            "customers-service": [{"host": "database", "port": 3306}],
            "visits-service": [{"host": "database", "port": 3306}],
            "vets-service": [{"host": "database", "port": 3306}],
        },
    }


def test_learn_and_freeze_source_database_effect_without_outcomes():
    spans = [
        span("root", "", "api-gateway", "SPAN_KIND_SERVER", "req-1", "/api/customer/owners"),
        span("customer", "missing-cross-source-parent", "customers-service", "SPAN_KIND_SERVER", "req-1", "/owners"),
        span("sql", "customer", "customers-service", "SPAN_KIND_CLIENT", db=True),
    ]
    model = learn_database_effects(spans, [intent()], inventory_value())
    effect = model["effects"]["ebpf"]["list_owners"]
    assert effect["selected_database_dependency"] is True
    assert effect["database_path_observed"] == 1
    assert len(model["model_sha256"]) == 64
    prediction = predict_database_effects(model, [intent()], database_up=False)[0]
    assert prediction["predicted_database_caused_failure"]["ebpf"] is True
    assert prediction["predicted_database_caused_failure"]["combined"] is True
    assert prediction["static_endpoint_baseline"] is True
    assert prediction["external_business_outcome"] is None


def test_vets_cache_necessity_remains_unknown_even_with_observed_database_path():
    spans = [
        span("root", "", "api-gateway", "SPAN_KIND_SERVER", "req-1", "/api/vet/vets"),
        span("vets", "root", "vets-service", "SPAN_KIND_SERVER", "req-1", "/vets"),
        span("sql", "vets", "vets-service", "SPAN_KIND_CLIENT", db=True),
    ]
    row = intent("list_vets")
    model = learn_database_effects(spans, [row], inventory_value())
    prediction = predict_database_effects(model, [row], database_up=False)[0]
    assert prediction["predicted_database_caused_failure"]["ebpf"] is None
    assert prediction["static_endpoint_baseline"] is None


def test_static_baseline_does_not_treat_unrelated_datasource_as_selected_database():
    inventory = inventory_value()
    inventory["service_database_endpoints"]["customers-service"] = [
        {"host": "unrelated-database", "port": 3306}
    ]
    model = learn_database_effects([], [intent()], inventory)
    prediction = predict_database_effects(model, [intent()], database_up=False)[0]
    assert prediction["static_endpoint_baseline"] is None


def test_conflicting_request_identity_fails_closed():
    spans = [
        span("root", "", "api-gateway", "SPAN_KIND_SERVER", "req-1", "/api/customer/owners"),
        span("root", "", "api-gateway", "SPAN_KIND_SERVER", "req-1", "/api/customer/owners"),
        span("customer", "root", "customers-service", "SPAN_KIND_SERVER", "req-1", "/owners"),
        span("sql", "customer", "customers-service", "SPAN_KIND_CLIENT", db=True),
    ]
    spans[1]["attributes"]["http.response.status_code"] = 503
    model = learn_database_effects(spans, [intent()], inventory_value())
    effect = model["effects"]["ebpf"]["list_owners"]
    assert effect["entry_bound"] == 0
    assert effect["selected_database_dependency"] is None


@pytest.mark.parametrize("mutation", ["wrong_service", "server_kind", "outside_window", "unattached"])
def test_incidental_database_activity_cannot_promote_dependency(mutation):
    spans = [
        span("root", "", "api-gateway", "SPAN_KIND_SERVER", "req-1", "/api/customer/owners"),
        span("customer", "missing-transport-parent", "customers-service", "SPAN_KIND_SERVER", "req-1", "/owners"),
        span("sql", "customer", "customers-service", "SPAN_KIND_CLIENT", db=True),
    ]
    if mutation == "wrong_service":
        spans[-1]["service"] = "vets-service"
    elif mutation == "server_kind":
        spans[-1]["kind"] = "SPAN_KIND_SERVER"
    elif mutation == "outside_window":
        spans[-1].update(start_ns=201, end_ns=202)
    else:
        spans[-1]["parent_id"] = "unrelated"
    model = learn_database_effects(spans, [intent()], inventory_value())
    assert model["effects"]["ebpf"]["list_owners"]["selected_database_dependency"] is None


def test_prediction_rejects_mutated_frozen_model():
    model = learn_database_effects([], [intent()], inventory_value())
    model["effects"]["ebpf"]["list_owners"]["selected_database_dependency"] = True
    with pytest.raises(ValueError, match="must be frozen"):
        predict_database_effects(model, [intent()], database_up=False)


def test_endpoint_inventory_uses_resolved_compose_and_fault_aliases(tmp_path):
    root = tmp_path / "petclinic"
    for node in ("a", "b"):
        (root / f"node-{node}").mkdir(parents=True)
    properties = {"spring.datasource.url": "jdbc:mysql://database:3306/petclinic"}
    compose_a = {"services": {
        "database": {"networks": {"application": {"ipv4_address": "172.28.11.20"}},
                     "ports": ["192.168.76.11:13306:3306"]},
        "customers": {"environment": {"OTEL_SERVICE_NAME": "customers-service",
                                        "SPRING_APPLICATION_JSON": json.dumps(properties)}},
    }}
    compose_b = {"services": {}}
    (root / "node-a" / "resolved-compose.json").write_text(json.dumps(compose_a))
    (root / "node-b" / "resolved-compose.json").write_text(json.dumps(compose_b))
    (root / "placement.json").write_text(json.dumps({"nodes": {"a": {"guest_ip": "192.168.76.11"}}}))
    inventory = endpoint_inventory(tmp_path)
    aliases = {(row["host"], row["port"]) for row in inventory["database_fault_aliases"]}
    assert ("database", 3306) in aliases
    assert ("172.28.11.20", 3306) in aliases
    assert ("192.168.76.11", 13306) in aliases
    assert inventory["service_database_endpoints"]["customers-service"] == [
        {"host": "database", "port": 3306}
    ]
