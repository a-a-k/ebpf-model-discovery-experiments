"""Frozen exact-signature class diagnostic using supplied driver boundaries."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from .evaluate import ari
from .selection_v4 import bind_entry, method_path, valid_identity


SOURCES = ("ebpf", "native", "combined")
VARIANTS = ("base", "downstream")


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _entry_aliases(declaration) -> set[str]:
    return {alias for contract in declaration.CONTRACTS.values()
            for alias in contract.get("entry_services", [])}


def _rows_for_trace(store, source: str, trace: str) -> list[dict]:
    if hasattr(store, 'trace_v5'):
        return store.trace_v5(source, trace)
    return [json.loads(row[0]) for row in store.db.execute(
        "SELECT data FROM spans WHERE source=? AND trace=? ORDER BY digest", (source, trace))]


def _descendant_tokens(store, root: dict) -> tuple[list[tuple], str | None]:
    rows = _rows_for_trace(store, root["source"], root["trace_id"])
    variants, children = defaultdict(list), defaultdict(set)
    for row in rows:
        variants[row["span_id"]].append(row)
        children[row.get("parent_id", "")].add(row["span_id"])
    pending = sorted(children.get(root["span_id"], set()))
    seen, tokens = {root["span_id"]}, []
    while pending:
        identity = pending.pop()
        if identity in seen:
            continue
        seen.add(identity)
        observed = variants.get(identity, [])
        if len(observed) != 1 or observed[0].get("attribute_conflicts"):
            return [], "ambiguous_descendant_identity"
        row = observed[0]
        if not valid_identity(row.get("trace_id"), row.get("span_id")):
            return [], "invalid_descendant_identity"
        attrs = row.get("attributes", {})
        method, route = method_path(row)
        rpc_service = attrs.get("rpc.service")
        rpc_method = attrs.get("rpc.method")
        database = attrs.get("db.system.name", attrs.get("db.system"))
        # Raw span names can contain IDs, SQL values or other instance data.  Use
        # one only as source-observed operation evidence when no canonical HTTP,
        # RPC or database identity exists.
        operation_name = (row.get("name") if not any(
            (method, route, rpc_service, rpc_method, database)) else None)
        tokens.append((row.get("service"), method, route, rpc_service, rpc_method,
                       database, operation_name))
        pending.extend(sorted(children.get(identity, set()) - seen))
    return sorted(tokens, key=lambda item: tuple("" if value is None else str(value) for value in item)), None


def _attempt_signature(store, plan: dict, declaration, source: str, variant: str):
    aliases = _entry_aliases(declaration)
    actual_sources = ("ebpf", "native") if source == "combined" else (source,)
    untyped = getattr(declaration, "UNTYPED_ENTRY_COMPONENTS", {})
    sequence = []
    reasons = Counter()
    for step in plan.get("http_steps", []):
        observed = []
        ambiguous = False
        for actual_source in actual_sources:
            root, reason = bind_entry(store, actual_source, step.get("request_id"), step,
                                      aliases, untyped.get(actual_source, ()))
            reasons[f"{actual_source}:{reason}"] += 1
            if reason not in ("unique_declared_entry", "entry_missing"):
                ambiguous = True
            if root is None:
                continue
            method, route = method_path(root)
            feature = {"source": actual_source, "method": method, "route": route}
            if variant == "downstream":
                tokens, error = _descendant_tokens(store, root)
                if error:
                    reasons[f"{actual_source}:{error}"] += 1
                    ambiguous = True
                feature["descendants"] = tokens
            observed.append(feature)
        if ambiguous or not observed:
            return None, dict(reasons)
        sequence.append(observed)
    if not sequence:
        return None, dict(reasons)
    return sequence, dict(reasons)


def _key(signature) -> str:
    return json.dumps(signature, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _class_id(signature_key: str) -> str:
    return "class-" + hashlib.sha256(signature_key.encode()).hexdigest()[:16]


def fit(store, plans: list[dict], declaration, out: Path) -> dict:
    """Fit exact signatures from healthy class_train plans; operation labels are unread."""
    out = Path(out)
    training = [plan for plan in plans if plan.get("phase") == "class_train"]
    model = {"schema_version": "classes-v4", "fit_phase": "class_train", "sources": {},
             "driver_grouping": "supplied attempt and planned-step boundaries; not automatic business-session segmentation",
             "raw_operation_name_rule": "fallback only when HTTP, RPC and database call identity are all absent",
             "fit_features_exclude": ["plan.operation", "record.operation", "timestamps", "status", "body", "success", "outcome"]}
    for source in SOURCES:
        model["sources"][source] = {}
        for variant in VARIANTS:
            counts, unknown = Counter(), Counter()
            for plan in training:
                signature, reasons = _attempt_signature(store, plan, declaration, source, variant)
                if signature is None:
                    unknown.update(reasons or {"unbound_attempt": 1})
                else:
                    counts[_key(signature)] += 1
            model["sources"][source][variant] = {
                "classes": [{"class_id": _class_id(signature), "signature": json.loads(signature),
                             "training_count": count}
                            for signature, count in sorted(counts.items())],
                "training_attempts": len(training), "unknown_attempts": len(training)-sum(counts.values()),
                "binding_reasons": dict(unknown),
            }
    _write(out/"classes-model.json", model)
    return model


def _assign(store, plans, declaration, model, phase: str) -> list[dict]:
    selected = [plan for plan in plans if plan.get("phase") == phase]
    output = []
    for source in SOURCES:
        for variant in VARIANTS:
            frozen = {_key(item["signature"]): item["class_id"]
                      for item in model["sources"][source][variant]["classes"]}
            for plan in selected:
                signature, reasons = _attempt_signature(store, plan, declaration, source, variant)
                key = _key(signature) if signature is not None else None
                output.append({
                    "attempt_id": plan.get("attempt_id"), "phase": phase, "source": source,
                    "variant": variant, "class_id": frozen.get(key),
                    "known_signature": key in frozen if key is not None else False,
                    "reason": ("known_frozen_signature" if key in frozen else
                               "unseen_signature" if key is not None else "binding_unknown"),
                    "binding_reasons": reasons,
                })
    return output


def evaluate(store, plans: list[dict], records: list[dict], declaration,
             model_path: Path, out: Path) -> dict:
    """Apply frozen signatures, then use external labels only for known-subset ARI."""
    model = json.loads(Path(model_path).read_text(encoding="utf-8"))
    assignments = _assign(store, plans, declaration, model, "class_test")
    target = _assign(store, plans, declaration, model, "target")
    labels = {row.get("attempt_id"): row.get("operation") for row in records
              if row.get("phase") == "class_test" and row.get("attempt_id") and row.get("operation")}
    metrics = []
    for source in SOURCES:
        for variant in VARIANTS:
            rows = [row for row in assignments if row["source"] == source and row["variant"] == variant]
            predicted_known = [row for row in rows if row["class_id"] is not None]
            ari_known = [row for row in predicted_known if row["attempt_id"] in labels]
            truth = [labels[row["attempt_id"]] for row in ari_known]
            predicted = [row["class_id"] for row in ari_known]
            metrics.append({
                "source": source, "variant": variant, "total": len(rows),
                "known": len(predicted_known), "unknown": len(rows)-len(predicted_known),
                "coverage": len(predicted_known)/len(rows) if rows else None,
                "ari_labeled_known_subset": len(ari_known),
                "ari_on_known_subset": ari(truth, predicted),
                "unknowns_assigned_one_class": False,
                "labels_used_after_prediction_only": True,
            })
    result = {
        "schema_version": "classes-v4-evaluation", "model": str(Path(model_path).resolve()),
        "class_test_assignments": assignments, "class_test_metrics": metrics,
        "target_descriptive_assignments": target,
        "fit_updated_during_evaluation": False,
        "driver_grouping_limitation": "attempt and step boundaries are supplied by the workload driver; automatic business-session segmentation is not claimed",
    }
    _write(Path(out)/"classes-v4.json", result)
    return result
