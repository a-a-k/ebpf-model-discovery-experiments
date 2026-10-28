from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace

from ebpf_discovery.classes_v4 import evaluate, fit


TRACE = "a" * 32


class Store:
    def __init__(self, rows):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE spans(source TEXT, trace TEXT, span TEXT, parent TEXT, digest TEXT, data TEXT)")
        for index, row in enumerate(rows):
            self.db.execute("INSERT INTO spans VALUES (?,?,?,?,?,?)", (
                row["source"], row["trace_id"], row["span_id"], row["parent_id"], str(index), json.dumps(row)))

    def candidates(self, source, request_id):
        return [json.loads(value) for (value,) in self.db.execute("SELECT data FROM spans WHERE source=?", (source,))
                if json.loads(value)["attributes"].get("http.request.header.x-experiment-request-id") == request_id]

    def identity(self, source, trace, span):
        return [json.loads(value) for (value,) in self.db.execute(
            "SELECT data FROM spans WHERE source=? AND trace=? AND span=?", (source, trace, span))]


def _row(span, request, route, *, parent="", service="frontend", db=None,
         rpc_service=None, rpc_method=None, name=None):
    attributes = {"http.request.method": "GET", "http.route": route}
    if request:
        attributes["http.request.header.x-experiment-request-id"] = request
    if db:
        attributes["db.system"] = db
    if rpc_service:
        attributes["rpc.service"] = rpc_service
    if rpc_method:
        attributes["rpc.method"] = rpc_method
    return {"source": "ebpf", "trace_id": TRACE, "span_id": span, "parent_id": parent,
            "service": service, "instance": "one", "node": "a", "kind": "SPAN_KIND_SERVER",
            "name": name, "attributes": attributes}


def _declaration():
    return SimpleNamespace(CONTRACTS={
        "red_herring_label": {"entry_services": ["frontend"], "steps": [{"method": "GET", "path": "/a"}]},
        "another_label": {"entry_services": ["frontend"], "steps": [{"method": "GET", "path": "/b"}]},
    }, UNTYPED_ENTRY_COMPONENTS={})


def _plan(attempt, phase, request, path, operation="must_not_be_fit_feature"):
    return {"attempt_id": attempt, "phase": phase, "operation": operation,
            "http_steps": [{"request_id": request, "method": "GET", "path": path}]}


def test_fit_ignores_operation_labels_and_freezes_exact_signatures(tmp_path: Path):
    rows = [_row("1" * 16, "train-a", "/a"), _row("2" * 16, "train-b", "/b")]
    plans = [_plan("a", "class_train", "train-a", "/a", "label-one"),
             _plan("b", "class_train", "train-b", "/b", "label-two")]
    model = fit(Store(rows), plans, _declaration(), tmp_path)
    classes = model["sources"]["ebpf"]["base"]["classes"]
    assert len(classes) == 2
    assert sum(item["training_count"] for item in classes) == 2
    encoded = json.dumps(model)
    assert "label-one" not in encoded and "label-two" not in encoded
    assert model["driver_grouping"].startswith("supplied attempt")
    relabeled = fit(Store(rows),
        [_plan("a", "class_train", "train-a", "/a", "swapped-two"),
         _plan("b", "class_train", "train-b", "/b", "swapped-one")],
        _declaration(), tmp_path / "relabeled")
    assert relabeled == model


def test_unseen_test_signature_is_unknown_and_does_not_refit(tmp_path: Path):
    training = Store([_row("1" * 16, "train", "/a")])
    model = fit(training, [_plan("train-attempt", "class_train", "train", "/a")], _declaration(), tmp_path)
    model_before = (tmp_path / "classes-model.json").read_bytes()
    testing = Store([_row("2" * 16, "test-known", "/a"), _row("3" * 16, "test-new", "/never-seen")])
    plans = [_plan("known", "class_test", "test-known", "/a"),
             _plan("new", "class_test", "test-new", "/never-seen")]
    records = [{"attempt_id": "known", "phase": "class_test", "operation": "actual-a"},
               {"attempt_id": "new", "phase": "class_test", "operation": "actual-new"}]
    result = evaluate(testing, plans, records, _declaration(), tmp_path / "classes-model.json", tmp_path)
    rows = [row for row in result["class_test_assignments"]
            if row["source"] == "ebpf" and row["variant"] == "base"]
    assert [row["reason"] for row in rows] == ["known_frozen_signature", "unseen_signature"]
    metric = next(row for row in result["class_test_metrics"]
                  if row["source"] == "ebpf" and row["variant"] == "base")
    assert metric["known"] == 1 and metric["unknown"] == 1
    assert metric["unknowns_assigned_one_class"] is False
    assert (tmp_path / "classes-model.json").read_bytes() == model_before


def test_downstream_conflict_and_missing_root_are_unknown_not_optimized(tmp_path: Path):
    root = _row("1" * 16, "request", "/a")
    child_one = _row("2" * 16, None, "/rpc", parent="1" * 16, service="worker", db="postgresql")
    child_two = {**child_one, "attributes": {**child_one["attributes"], "db.system": "mysql"}}
    model = fit(Store([root, child_one, child_two]),
                [_plan("attempt", "class_train", "request", "/a")], _declaration(), tmp_path)
    downstream = model["sources"]["ebpf"]["downstream"]
    assert downstream["classes"] == []
    assert downstream["unknown_attempts"] == 1
    assert downstream["binding_reasons"]["ebpf:ambiguous_descendant_identity"] == 1


def test_target_assignments_are_descriptive_and_labels_enter_after_prediction(tmp_path: Path):
    store = Store([_row("1" * 16, "train", "/a"), _row("2" * 16, "test", "/a"),
                   _row("3" * 16, "target", "/a")])
    model = fit(store, [_plan("train", "class_train", "train", "/a")], _declaration(), tmp_path)
    result = evaluate(store,
        [_plan("test", "class_test", "test", "/a"), _plan("target", "target", "target", "/a")],
        [{"attempt_id": "test", "phase": "class_test", "operation": "external-only"}],
        _declaration(), tmp_path / "classes-model.json", tmp_path)
    assert result["fit_updated_during_evaluation"] is False
    assert result["target_descriptive_assignments"]
    assert all(metric["labels_used_after_prediction_only"] for metric in result["class_test_metrics"])


def test_downstream_excludes_entry_and_keeps_rpc_call_identity(tmp_path: Path):
    root = _row("1" * 16, "train", "/a")
    child = _row("2" * 16, None, "/rpc", parent="1" * 16, service="worker",
                 rpc_service="catalog.v1.Products", rpc_method="GetProduct", name="grpc.call")
    model = fit(Store([root, child]), [_plan("attempt", "class_train", "train", "/a")],
                _declaration(), tmp_path)
    signature = model["sources"]["ebpf"]["downstream"]["classes"][0]["signature"]
    descendants = signature[0][0]["descendants"]
    assert descendants == [["worker", "GET", "/rpc", "catalog.v1.Products",
                            "GetProduct", None, "grpc.call"]]
