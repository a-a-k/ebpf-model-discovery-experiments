import pytest

from systems.petclinic.semantic_audit import audit_semantics


def span(source, trace, sid, parent, service, kind, method=None, path=None, status=None,
         request_id=None, name="span", start_ns=None, **attrs):
    attributes = dict(attrs)
    if method is not None:
        attributes["http.request.method"] = method
    if path is not None:
        attributes["url.path"] = path
        attributes.setdefault("url.full", "http://service" + path)
    if status is not None:
        attributes["http.response.status_code"] = str(status)
    if request_id is not None:
        attributes["http.request.header.x-experiment-request-id"] = [request_id]
    return {"source": source, "node": "a", "trace_id": trace, "span_id": sid,
            "parent_id": parent, "service": service, "name": name, "kind": kind,
            "start_ns": len(sid) if start_ns is None else start_ns,
            "end_ns": (len(sid) if start_ns is None else start_ns) + 1, "attributes": attributes,
            "status": {}}


def row(operation, request_id="req-1"):
    return {"attempt_key": "attempt-1", "step_ids": [request_id], "contract_id": operation,
            "phase": "target", "state": "11", "started_ns": 10, "ended_ns": 20,
            "deadline_ns": 100}


def attempt(result, source="native"):
    return result["sources"][source]["attempts"][0]


def test_strict_gateway_entry_ignores_earlier_header_bearing_downstream_server():
    spans = [
        span("native", "t", "down", "client", "customers-service", 2, "GET", "/owners", 200, "req-1"),
        span("native", "t", "root", "", "api-gateway", 2, "GET", "/api/customer/owners", 200, "req-1"),
        span("native", "t", "client", "root", "api-gateway", 3, "GET", "/owners", 200),
    ]
    record = attempt(audit_semantics(spans, [row("list_owners")]))
    assert record["entry_binding"]["status"] == "bound"
    assert record["entry_binding"]["witnesses"][0]["span_id"] == "root"
    assert record["logical_completion"] is True
    assert record["source_business_verdict"] is None


def test_owner_http_200_with_explicit_visits_503_is_business_failure():
    spans = [
        span("native", "t", "root", "", "api-gateway", 2, "GET", "/api/gateway/owners/6", 200, "req-1"),
        span("native", "t", "cc", "root", "api-gateway", 3, "GET", "/owners/6", 200),
        span("native", "t", "cs", "cc", "customers-service", 2, "GET", "/owners/6", 200),
        span("native", "t", "vc", "root", "api-gateway", 3, "GET", "/pets/visits", 503),
    ]
    record = attempt(audit_semantics(spans, [row("owner_details_with_visits")]))
    groups = {g["group"]: g for g in record["mandatory_groups"]}
    assert groups["customers"]["completion"] is True
    assert groups["visits"]["completion"] is False
    assert groups["visits"]["reason"] == "explicit_required_client_failure"
    assert record["logical_completion"] is False
    assert record["source_business_verdict"] is False


def test_missing_mandatory_calls_remain_unknown():
    spans = [span("ebpf", "t", "root", "", "api-gateway", "SPAN_KIND_SERVER",
                  "GET", "/api/gateway/owners/6", 200, "req-1")]
    record = attempt(audit_semantics(spans, [row("owner_details_with_visits")]), "ebpf")
    assert record["logical_completion"] is None
    assert record["source_business_verdict"] is None
    assert all(g["reason"] == "required_group_not_fully_observed" for g in record["mandatory_groups"])


def test_duplicate_declared_entries_are_ambiguous_not_earliest_wins():
    spans = [
        span("ebpf", "a", "one", "", "api-gateway", "SPAN_KIND_SERVER", "GET", "/api/vet/vets", 200, "req-1"),
        span("ebpf", "b", "two", "", "api-gateway", "SPAN_KIND_SERVER", "GET", "/api/vet/vets", 200, "req-1"),
    ]
    record = attempt(audit_semantics(spans, [row("list_vets")]), "ebpf")
    assert record["entry_binding"]["status"] == "ambiguous"
    assert record["logical_completion"] is None


def test_create_retry_can_complete_protocol_but_never_proves_persistence():
    spans = [
        span("ebpf", "t", "root", "", "api-gateway", "SPAN_KIND_SERVER", "POST", "/api/visit/owners/1/pets/1/visits", 201, "req-1"),
        span("ebpf", "t", "first", "root", "api-gateway", "SPAN_KIND_CLIENT", "POST", "/owners/1/pets/1/visits", 503, start_ns=2),
        span("ebpf", "t", "final", "root", "api-gateway", "SPAN_KIND_CLIENT", "POST", "/owners/1/pets/1/visits", 201, start_ns=3),
        span("ebpf", "t", "recv", "final", "visits-service", "SPAN_KIND_SERVER", "POST", "/owners/1/pets/1/visits", 201),
        span("ebpf", "t", "insert", "recv", "visits-service", "SPAN_KIND_CLIENT", name="INSERT visits",
             **{"db.system.name": "mysql", "db.operation.name": "INSERT",
                "db.query.text": "insert into visits (visit_date,description,pet_id) values ('2026-09-01','ebpf-study-" + "a"*64 + "',1)"}),
    ]
    record = attempt(audit_semantics(spans, [row("create_visit")]), "ebpf")
    assert record["mandatory_groups"][0]["completion"] is True
    assert record["logical_completion"] is True
    assert record["write_evidence"]["identity_attempted"] is True
    assert record["write_evidence"]["persistence"] is None
    assert record["source_business_verdict"] is None


def test_parent_traversal_never_crosses_sources():
    spans = [
        span("ebpf", "t", "root", "", "api-gateway", "SPAN_KIND_SERVER", "GET", "/api/customer/owners", 200, "req-1"),
        span("ebpf", "t", "client", "root", "api-gateway", "SPAN_KIND_CLIENT", "GET", "/owners", 200),
        span("native", "t", "receiver", "client", "customers-service", 2, "GET", "/owners", 200),
    ]
    result = audit_semantics(spans, [row("list_owners")])
    assert attempt(result, "ebpf")["logical_completion"] is None
    assert attempt(result, "native")["entry_binding"]["status"] == "missing"


def test_semantic_row_boundary_rejects_outcome_leakage():
    leaking = {**row("list_vets"), "success": True}
    with pytest.raises(ValueError, match="boundary violation"):
        audit_semantics([], [leaking])
