"""Petclinic-only, source-evidence semantic diagnostics.

This module does not fit a model and never consumes business outcomes.  It asks
which declared protocol/completion facts are supported by each telemetry source.
Positive business success remains unsupported because response payloads and an
independent persisted-row observation are not span fields in this experiment.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from urllib.parse import urlsplit

ROW_FIELDS = {
    "attempt_key", "step_ids", "contract_id", "phase", "state",
    "started_ns", "ended_ns", "deadline_ns",
}
SERVER_KINDS = {"SPAN_KIND_SERVER", "2", "server"}
CLIENT_KINDS = {"SPAN_KIND_CLIENT", "3", "client"}

CONTRACTS = {
    "list_owners": {
        "method": "GET", "entry_path": "/api/customer/owners",
        "groups": (("customers", "customers-service", ("/owners",)),),
        "postcondition": "exact_owner_fixture_payload_not_observed",
    },
    "owner_details_with_visits": {
        "method": "GET", "entry_path": "/api/gateway/owners/6",
        "groups": (
            ("customers", "customers-service", ("/owners/6",)),
            ("visits", "visits-service", ("/pets/visits",)),
        ),
        "postcondition": "owner_pets_and_visits_payload_not_observed",
    },
    "create_visit": {
        "method": "POST", "entry_path": "/api/visit/owners/1/pets/1/visits",
        "groups": (("visits", "visits-service", ("/owners/1/pets/1/visits",)),),
        "postcondition": "exactly_once_persisted_row_not_observed",
        "single_retry": (503, 201),
    },
    "list_vets": {
        "method": "GET", "entry_path": "/api/vet/vets",
        "groups": (("vets", "vets-service", ("/vets",)),),
        "postcondition": "exact_vets_fixture_payload_not_observed",
    },
}


def _header(span):
    for key, value in span.get("attributes", {}).items():
        if key.lower().replace("_", "-").endswith("x-experiment-request-id"):
            if isinstance(value, list):
                return value[0] if len(value) == 1 else None
            return value if isinstance(value, str) else None
    return None


def _kind(span, accepted):
    return str(span.get("kind")) in accepted


def _method(span):
    attrs = span.get("attributes", {})
    return attrs.get("http.request.method", attrs.get("http.method"))


def _path(span):
    attrs = span.get("attributes", {})
    raw = attrs.get("url.path") or attrs.get("http.target")
    if raw:
        return urlsplit(str(raw)).path
    raw = attrs.get("url.full") or attrs.get("http.url") or attrs.get("http.route")
    return urlsplit(str(raw)).path if raw else None


def _explicit_status(span):
    attrs = span.get("attributes", {})
    raw = attrs.get("http.response.status_code", attrs.get("http.status_code"))
    try:
        code = int(raw)
    except (TypeError, ValueError):
        code = None
    status = span.get("status", {}).get("code")
    if status in (2, "STATUS_CODE_ERROR"):
        return False
    return 200 <= code < 300 if code is not None and 100 <= code <= 599 else None


def _status_code(span):
    attrs = span.get("attributes", {})
    raw = attrs.get("http.response.status_code", attrs.get("http.status_code"))
    try:
        code = int(raw)
    except (TypeError, ValueError):
        return None
    return code if 100 <= code <= 599 else None


def _witness(span):
    attrs = span.get("attributes", {})
    return {
        "source": span.get("source"), "node": span.get("node"),
        "trace_id": span.get("trace_id"), "span_id": span.get("span_id"),
        "parent_id": span.get("parent_id"), "service": span.get("service"),
        "name": span.get("name"), "kind": span.get("kind"),
        "method": _method(span), "path": _path(span),
        "status_code": attrs.get("http.response.status_code", attrs.get("http.status_code")),
    }


def _conjunction(values):
    values = list(values)
    return False if False in values else (True if values and all(v is True for v in values) else None)


def _validate_rows(rows):
    seen = set()
    for row in rows:
        extra = set(row) - ROW_FIELDS
        missing = ROW_FIELDS - set(row)
        if extra or missing:
            raise ValueError(f"semantic row boundary violation; extra={sorted(extra)}, missing={sorted(missing)}")
        if row["contract_id"] not in CONTRACTS:
            raise ValueError(f"unknown Petclinic contract: {row['contract_id']}")
        if row["attempt_key"] in seen:
            raise ValueError("duplicate semantic attempt_key")
        seen.add(row["attempt_key"])
        if (not isinstance(row["step_ids"], list) or not row["step_ids"]
                or not all(isinstance(x, str) and x for x in row["step_ids"])):
            raise ValueError("step_ids must be a non-empty string list")
        for field in ("started_ns", "ended_ns", "deadline_ns"):
            if type(row[field]) is not int:
                raise ValueError(f"{field} must be an integer")
        if row["ended_ns"] < row["started_ns"]:
            raise ValueError("ended_ns must not precede started_ns")
        if row["deadline_ns"] < row["started_ns"]:
            raise ValueError("deadline_ns must be an absolute timestamp at or after started_ns")


class _Index:
    def __init__(self, spans):
        self.sources = sorted({str(s.get("source")) for s in spans if s.get("source") in ("ebpf", "native")})
        self.headers = defaultdict(list)
        self.children = defaultdict(list)
        self.traces = defaultdict(list)
        self.by_id = {}
        for span in spans:
            source = span.get("source")
            if source not in ("ebpf", "native"):
                continue
            trace = span.get("trace_id", "")
            identity = (source, trace, span.get("span_id", ""))
            self.by_id[identity] = span
            self.children[(source, trace, span.get("parent_id", ""))].append(span)
            self.traces[(source, trace)].append(span)
            step = _header(span)
            if step:
                self.headers[(source, step)].append(span)
        for values in (self.headers, self.children, self.traces):
            for rows in values.values():
                rows.sort(key=lambda s: (int(s.get("start_ns", 0)), str(s.get("span_id", ""))))

    def descendants(self, root):
        source, trace = root["source"], root["trace_id"]
        output, queue, seen = [], [root], set()
        while queue:
            span = queue.pop()
            identity = span.get("span_id", "")
            if identity in seen:
                continue
            seen.add(identity)
            output.append(span)
            queue.extend(self.children.get((source, trace, identity), ()))
        return output

    def descends_from(self, span, ancestor):
        if span.get("source") != ancestor.get("source") or span.get("trace_id") != ancestor.get("trace_id"):
            return False
        current, seen = span, set()
        while current.get("parent_id") and current.get("span_id") not in seen:
            seen.add(current.get("span_id"))
            if current.get("parent_id") == ancestor.get("span_id"):
                return True
            current = self.by_id.get((span["source"], span["trace_id"], current.get("parent_id")))
            if current is None:
                return False
        return False


def _entry(index, source, row, contract):
    candidates = []
    for step in row["step_ids"]:
        candidates.extend(index.headers.get((source, step), ()))
    unique = {(s.get("trace_id"), s.get("span_id")): s for s in candidates}
    matches = [s for s in unique.values() if _kind(s, SERVER_KINDS)
               and s.get("service") == "api-gateway"
               and _method(s) == contract["method"] and _path(s) == contract["entry_path"]]
    matches.sort(key=lambda s: (int(s.get("start_ns", 0)), str(s.get("span_id", ""))))
    if len(matches) != 1:
        reason = "entry_missing" if not matches else "entry_ambiguous"
        return None, {"status": "missing" if not matches else "ambiguous", "reason": reason,
                      "candidate_count": len(matches), "witnesses": [_witness(s) for s in matches]}
    return matches[0], {"status": "bound", "reason": "unique_declared_gateway_entry",
                        "candidate_count": 1, "witnesses": [_witness(matches[0])]}


def _group(index, descendants, group, contract):
    name, target, paths = group
    clients = [s for s in descendants if s.get("service") == "api-gateway"
               and _kind(s, CLIENT_KINDS) and _method(s) == contract["method"] and _path(s) in paths]
    receivers = [s for s in descendants if s.get("service") == target
                 and _kind(s, SERVER_KINDS) and _method(s) == contract["method"] and _path(s) in paths]
    clients.sort(key=lambda s: (int(s.get("start_ns", 0)), str(s.get("span_id", ""))))
    client_statuses = [_explicit_status(s) for s in clients]
    result = {
        "group": name, "target_service": target, "completion": None,
        "reason": "required_group_not_fully_observed",
        "client_witnesses": [_witness(s) for s in clients],
        "receiver_witnesses": [_witness(s) for s in receivers],
    }
    retry = contract.get("single_retry")
    if retry and len(clients) == 2 and tuple(_status_code(s) for s in clients) == retry:
        first, final = clients
        first_receivers = [s for s in receivers if index.descends_from(s, first)]
        final_receivers = [s for s in receivers if index.descends_from(s, final) and _explicit_status(s) is True]
        if first.get("parent_id") != final.get("parent_id"):
            result["reason"] = "declared_retry_parent_mismatch"
        elif first_receivers:
            result["reason"] = "earlier_retry_receiver_effect_requires_postcondition"
        elif len(final_receivers) == 1:
            result.update(completion=True, reason="declared_single_retry_503_then_201_completed")
        else:
            result["reason"] = "final_retry_receiver_not_uniquely_verified"
        return result
    if len(clients) > 1:
        result["reason"] = "unexpected_multiple_required_calls"
        return result
    if len(clients) == 1 and client_statuses[0] is False:
        result.update(completion=False, reason="explicit_required_client_failure")
        return result
    if len(clients) != 1:
        return result
    successful = [s for s in receivers if index.descends_from(s, clients[0]) and _explicit_status(s) is True]
    failed = [s for s in receivers if index.descends_from(s, clients[0]) and _explicit_status(s) is False]
    if failed:
        result.update(completion=False, reason="explicit_required_receiver_failure")
    elif len(successful) == 1 and client_statuses[0] is not False:
        result.update(completion=True, reason="unique_required_receiver_protocol_success")
    elif len(successful) > 1:
        result["reason"] = "multiple_successful_receivers_ambiguous"
    return result


def _write_evidence(index, source, root):
    if root is None:
        return {"write_attempt_observed": None, "commit_span_observed": None,
                "persistence": None, "reason": "entry_unbound", "witnesses": [],
                "same_trace_unattached_candidates": []}
    trace_spans = index.traces.get((source, root["trace_id"]), ())
    inserts, commits = [], []
    for span in trace_spans:
        attrs = span.get("attributes", {})
        operation = str(attrs.get("db.operation.name", attrs.get("db.operation", ""))).upper()
        statement = str(attrs.get("db.query.text", attrs.get("db.statement", "")))
        if operation == "INSERT" and "visits" in statement.lower():
            inserts.append(span)
        if span.get("service") == "visits-service" and span.get("name") == "Transaction.commit":
            commits.append(span)
    attached_inserts = [s for s in inserts if index.descends_from(s, root)]
    attached_commits = [s for s in commits if index.descends_from(s, root)]
    unattached = [s for s in inserts + commits if s not in attached_inserts + attached_commits]
    reason = "no_write_span_observed"
    if attached_inserts:
        reason = "exact_ancestry_insert_attempt_observed"
    elif unattached:
        reason = "same_trace_unattached_write_candidates"
    return {
        "write_attempt_observed": True if attached_inserts else None,
        "commit_span_observed": True if attached_commits else None,
        "persistence": None,
        "reason": reason,
        "witnesses": [_witness(s) for s in attached_inserts + attached_commits],
        "same_trace_unattached_candidates": [_witness(s) for s in unattached],
    }


def _audit_attempt(index, source, row):
    contract = CONTRACTS[row["contract_id"]]
    root, binding = _entry(index, source, row, contract)
    entry_protocol = _explicit_status(root) if root else None
    timely = row["ended_ns"] <= row["deadline_ns"]
    descendants = index.descendants(root) if root else []
    groups = [_group(index, descendants, group, contract) for group in contract["groups"]]
    logical = _conjunction([entry_protocol, timely] + [g["completion"] for g in groups])
    business = False if logical is False else None
    write = _write_evidence(index, source, root) if row["contract_id"] == "create_visit" else None
    return {
        "attempt_key": row["attempt_key"], "contract_id": row["contract_id"],
        "phase": row["phase"], "state": row["state"], "source": source,
        "entry_binding": binding, "entry_protocol": entry_protocol, "timely": timely,
        "mandatory_groups": groups, "logical_completion": logical,
        "write_evidence": write,
        "business_postcondition": None,
        "source_business_verdict": business,
        "business_reason": "logical_contract_explicitly_failed" if business is False else contract["postcondition"],
    }


def audit_semantics(spans, semantic_rows):
    """Return source-specific primitive evidence without reading external outcomes."""
    _validate_rows(semantic_rows)
    index = _Index(spans)
    sources = {}
    for source in ("ebpf", "native"):
        attempts = [_audit_attempt(index, source, row) for row in semantic_rows]
        sources[source] = {
            "attempts": attempts,
            "counts": {
                "entry_binding": dict(Counter(a["entry_binding"]["status"] for a in attempts)),
                "logical_completion": {str(k).lower(): v for k, v in Counter(a["logical_completion"] for a in attempts).items()},
                "source_business_verdict": {str(k).lower(): v for k, v in Counter(a["source_business_verdict"] for a in attempts).items()},
            },
        }
    return {
        "schema_version": 1,
        "method": "petclinic-declared-semantic-evidence-audit-v1",
        "sources": sources,
        "business_success_supported": False,
        "business_success_note": "Spans can exclude success or establish logical protocol completion, but cannot certify exact response payloads or exactly-once persisted rows.",
    }
