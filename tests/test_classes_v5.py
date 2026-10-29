import json
import sqlite3
from types import SimpleNamespace

from ebpf_discovery.classes_v5 import evaluate, fit


DECLARATION = SimpleNamespace(CONTRACTS={"unused_label": {"entry_services": ["frontend"]}},
                              UNTYPED_ENTRY_COMPONENTS={})


class Store:
    def __init__(self, rows):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE spans(source,trace,span,parent,digest,data)")
        for n, row in enumerate(rows):
            self.db.execute("INSERT INTO spans VALUES (?,?,?,?,?,?)", (
                row["source"], row["trace_id"], row["span_id"], row["parent_id"], str(n), json.dumps(row)))

    def candidates(self, source, request_id):
        return [json.loads(value) for (value,) in self.db.execute("SELECT data FROM spans WHERE source=?", (source,))
                if json.loads(value)["attributes"].get("http.request.header.x-experiment-request-id") == request_id]

    def identity(self, source, trace, span):
        return [json.loads(value) for (value,) in self.db.execute(
            "SELECT data FROM spans WHERE source=? AND trace=? AND span=?", (source, trace, span))]


def attempt(n, phase, calls, *, route="/items", label="unread-business-label"):
    request = f"request-{n}"
    root_id = f"{n * 100:016x}"
    root = {"source": "ebpf", "trace_id": f"{n:032x}", "span_id": root_id, "parent_id": "",
            "service": "frontend", "kind": "SPAN_KIND_SERVER", "node": "a", "instance": "one",
            "attributes": {"http.request.method": "GET", "http.route": route,
                           "http.request.header.x-experiment-request-id": request}}
    rows = [root]
    for offset, call in enumerate(calls, 1):
        row = {**root, "span_id": f"{n * 100 + offset:016x}", "parent_id": root_id,
               "service": "worker", "attributes": {}, "name": call}
        if call != "processing":
            row["attributes"] = {"rpc.service": "example.Service", "rpc.method": call}
        rows.append(row)
    plan = {"attempt_id": str(n), "phase": phase, "operation": label,
            "http_steps": [{"request_id": request, "method": "GET", "path": route}]}
    return rows, plan


def build(specs):
    rows, plans = [], []
    for n, phase, calls in specs:
        batch, plan = attempt(n, phase, calls)
        rows.extend(batch)
        plans.append(plan)
    return Store(rows), plans


def test_family_survives_optional_repeated_missing_and_novel_descendants(tmp_path):
    store, plans = build([(1, "class_train", ["x"]), (2, "class_train", ["x", "y"]),
                          (3, "class_train", ["x", "x", "processing"]), (4, "class_train", []),
                          (5, "class_test", ["x"]), (6, "class_test", []),
                          (7, "class_test", ["x", "x", "processing"]),
                          (8, "class_test", ["z"]), (9, "class_test", ["x", "y"])])
    model = fit(store, plans, DECLARATION, tmp_path)
    family, = model["sources"]["ebpf"]["families"]
    # Nested patterns must survive: deleting {x} would turn missing y into an
    # unjustified unique assignment to {x,y}.
    assert sorted(len(p["positive_tokens"]) for p in family["structural_patterns"]) == [1, 2]
    repeated = family["training_descriptors"][2]["steps"][0]
    assert repeated["semantic_calls"][0]["observed_count"] == 2
    assert repeated["unclassified_descendants"][0]["identity"][-1] == "processing"
    path = tmp_path / "classes-family-model.json"
    before = path.read_bytes()
    result = evaluate(store, plans, [{"attempt_id": str(n), "phase": "class_test", "operation": "browse"}
                                     for n in range(5, 10)], DECLARATION, path, tmp_path)
    assignments = [r for r in result["class_test_assignments"] if r["source"] == "ebpf"]
    assert {r["class_id"] for r in assignments} == {family["class_id"]}
    assert [r["pattern_match"]["status"] for r in assignments] == [
        "ambiguous_patterns", "no_positive_evidence", "ambiguous_patterns", "unseen_pattern",
        "unique_compatible_pattern"]
    assert assignments[-1]["pattern_match"]["complete_pattern_established"] is False
    assert path.read_bytes() == before
    assert (tmp_path / "classes-v4.json").exists()
    assert (tmp_path / "classes-v5.json").exists()
    old = json.loads((tmp_path / "classes-v4.json").read_text())
    base = [r["class_id"] for r in old["class_test_assignments"] if r["source"] == "ebpf" and r["variant"] == "base"]
    assert base == [r["class_id"] for r in assignments]


def test_ambiguous_descendant_does_not_destroy_unambiguous_entry_family(tmp_path):
    training, plan = attempt(1, "class_train", ["x"])
    testing, test_plan = attempt(2, "class_test", ["x"])
    testing.append({**testing[-1], "attributes": {"rpc.method": "conflicting"}})
    store = Store(training + testing)
    fit(store, [plan], DECLARATION, tmp_path)
    result = evaluate(store, [test_plan], [], DECLARATION, tmp_path / "classes-family-model.json", tmp_path)
    row = next(r for r in result["class_test_assignments"] if r["source"] == "ebpf")
    assert row["class_id"] is not None
    assert row["pattern_match"]["status"] == "ambiguous_identity"


def test_labels_and_test_patterns_do_not_enter_fit(tmp_path):
    store, plans = build([(1, "class_train", ["x"]), (2, "class_test", ["never-fit-this"]),
                          (3, "target", ["never-fit-that"])])
    first = fit(store, plans, DECLARATION, tmp_path / "first")
    second = fit(store, [{**p, "operation": "different-label"} for p in plans], DECLARATION, tmp_path / "second")
    assert first == second
    encoded = json.dumps(first)
    for forbidden in ("unread-business-label", "different-label", "never-fit-this", "never-fit-that"):
        assert forbidden not in encoded


def test_unseen_entry_and_missing_entry_remain_unknown(tmp_path):
    training, train_plan = attempt(1, "class_train", ["x"])
    testing, test_plan = attempt(2, "class_test", ["x"], route="/different")
    _, missing_plan = attempt(3, "class_test", ["x"])
    store = Store(training + testing)
    fit(store, [train_plan], DECLARATION, tmp_path)
    result = evaluate(store, [test_plan, missing_plan], [], DECLARATION,
                      tmp_path / "classes-family-model.json", tmp_path)
    rows = [r for r in result["class_test_assignments"] if r["source"] == "ebpf"]
    assert [r["reason"] for r in rows] == ["unseen_entry_family", "binding_unknown"]
    assert all(r["class_id"] is None for r in rows)
