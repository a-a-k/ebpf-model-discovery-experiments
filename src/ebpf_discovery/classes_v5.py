"""Stable entry families with uncertain, source-local structural descriptors.

Family identity intentionally equals the route/step baseline. Descendant patterns
describe positive observed evidence, not additional business-operation identities.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from . import classes_v4 as legacy
from .evaluate import ari
from .selection_v4 import method_path, valid_identity
from .selection_v5 import bind_entry


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def describe(store, plan, declaration, source):
    """Retain call multiplicity separately; never infer an unobserved descendant."""
    aliases = legacy._entry_aliases(declaration)
    untyped = getattr(declaration, "UNTYPED_ENTRY_COMPONENTS", {})
    sources = ("ebpf", "native") if source == "combined" else (source,)
    steps, positive, errors = [], set(), []
    for step_index, step in enumerate(plan.get("http_steps", [])):
        for actual_source in sources:
            root, reason = bind_entry(store, actual_source, step.get("request_id"),
                                     step, aliases, untyped.get(actual_source, ()))
            row = {"step": step_index, "source": actual_source, "entry_reason": reason,
                   "semantic_calls": [], "unclassified_descendants": []}
            if root is None:
                row["status"] = "entry_unavailable"
                if reason != "entry_missing":
                    errors.append(reason)
                steps.append(row)
                continue
            if not valid_identity(root.get('trace_id'), root.get('span_id')):
                row['status'] = 'entry_bound_without_genuine_ancestry'
                row['observation_digest'] = root.get('_observation_digest')
                row['observation_provenance'] = root.get('_observation_provenance', [])
                steps.append(row)
                continue
            tokens, error = legacy._descendant_tokens(store, root)
            if error:
                row["status"] = error
                errors.append(error)
                steps.append(row)
                continue
            semantic, unclassified = Counter(), Counter()
            for token in tokens:
                service, method, route, rpc_service, rpc_method, database, name = token
                # A runtime-only name such as "processing" is retained as an
                # unclassified observation, not a semantic operation identity.
                if not ((method and route) or rpc_method or database):
                    unclassified[legacy._key(list(token))] += 1
                    continue
                canonical = [service, method, route, rpc_service, rpc_method, database]
                semantic[legacy._key(canonical)] += 1
                positive.add(legacy._key([step_index, actual_source, canonical]))
            row["semantic_calls"] = [
                {"identity": json.loads(key), "observed_count": count}
                for key, count in sorted(semantic.items())]
            row["unclassified_descendants"] = [
                {"identity": json.loads(key), "observed_count": count}
                for key, count in sorted(unclassified.items())]
            row["status"] = "positive_semantic_evidence" if semantic else "no_semantic_descendants"
            steps.append(row)
    return {"steps": steps, "positive_tokens": [json.loads(key) for key in sorted(positive)],
            "identity_errors": sorted(set(errors)), "complete_execution_observed": None,
            "interpretation": "positive source-local ancestry only; absence is not a negative call fact"}


def _attempt_signature(store, plan, declaration, source):
    aliases = legacy._entry_aliases(declaration)
    untyped = getattr(declaration, 'UNTYPED_ENTRY_COMPONENTS', {})
    sources = ('ebpf', 'native') if source == 'combined' else (source,)
    sequence, reasons = [], Counter()
    for step in plan.get('http_steps', []):
        observed, ambiguous = [], False
        for actual_source in sources:
            root, reason = bind_entry(store, actual_source, step.get('request_id'), step,
                                      aliases, untyped.get(actual_source, ()))
            reasons[actual_source+':'+reason] += 1
            if reason not in ('unique_observation_entry', 'entry_missing'):
                ambiguous = True
            if root is not None:
                method, route = method_path(root)
                observed.append({'source': actual_source, 'method': method, 'route': route})
        if ambiguous or not observed:
            return None, dict(reasons)
        sequence.append(observed)
    return (sequence, dict(reasons)) if sequence else (None, dict(reasons))


def fit(store, plans, declaration, out):
    out = Path(out)
    old = legacy.fit(store, plans, declaration, out)
    training = [p for p in plans if p.get("phase") == "class_train"]
    model = {"schema_version": "classes-v5-family", "fit_phase": "class_train",
             "legacy_model": "classes-model.json", "sources": {},
             "family_rule": "identical to frozen base entry/step/source signature",
             "structural_rule": "all distinct positive semantic sets retained, including nested sets",
             "multiplicity_rule": "retained in descriptors; never changes family or set-pattern identity",
             "business_subclasses": "unresolved; structural patterns are not business-operation labels",
             "driver_grouping": old["driver_grouping"],
             "fit_features_exclude": old["fit_features_exclude"]}
    for source in legacy.SOURCES:
        families = {}
        counts = Counter()
        unknown = Counter()
        for plan in training:
            signature, reasons = _attempt_signature(store, plan, declaration, source)
            if signature is None:
                unknown.update(reasons or {'unbound_attempt': 1})
            else:
                counts[legacy._key(signature)] += 1
        for signature, count in sorted(counts.items()):
            families[signature] = {
                'class_id': legacy._class_id(signature), 'signature': json.loads(signature),
                'training_count': count, 'structural_patterns': [],
                'descriptor_states': {}, 'training_descriptors': []}
        patterns = {key: Counter() for key in families}
        states = {key: Counter() for key in families}
        for plan in training:
            signature, _ = _attempt_signature(store, plan, declaration, source)
            key = legacy._key(signature)
            if signature is None or key not in families:
                continue
            description = describe(store, plan, declaration, source)
            families[key]["training_descriptors"].append(description)
            if description["identity_errors"]:
                states[key]["ambiguous_identity"] += 1
            elif not description["positive_tokens"]:
                states[key]["no_positive_evidence"] += 1
            else:
                states[key]["positive_evidence"] += 1
                patterns[key][legacy._key(description["positive_tokens"])] += 1
        for key, family in families.items():
            family["structural_patterns"] = [
                {"pattern_id": "pattern-" + legacy._class_id(pattern).removeprefix("class-"),
                 "positive_tokens": json.loads(pattern), "training_count": count}
                for pattern, count in sorted(patterns[key].items())]
            family["descriptor_states"] = dict(states[key])
        model["sources"][source] = {"families": list(families.values()),
                                    "training_attempts": len(training),
                                    'unknown_attempts': len(training)-sum(counts.values()),
                                    'binding_reasons': dict(unknown)}
    _write(out / "classes-family-model.json", model)
    return model


def compatible_patterns(description, patterns):
    if description["identity_errors"]:
        return {"status": "ambiguous_identity", "candidate_pattern_ids": []}
    observed = {legacy._key(t) for t in description["positive_tokens"]}
    if not observed:
        return {"status": "no_positive_evidence", "candidate_pattern_ids": []}
    candidates = [p["pattern_id"] for p in patterns
                  if observed <= {legacy._key(t) for t in p["positive_tokens"]}]
    return {"status": ("unique_compatible_pattern" if len(candidates) == 1 else
                       "ambiguous_patterns" if candidates else "unseen_pattern"),
            "candidate_pattern_ids": candidates,
            "complete_pattern_established": False}


def _assign(store, plans, declaration, model, phase):
    rows = []
    for source in legacy.SOURCES:
        families = {legacy._key(f["signature"]): f
                    for f in model["sources"][source]["families"]}
        for plan in plans:
            if plan.get("phase") != phase:
                continue
            signature, reasons = _attempt_signature(store, plan, declaration, source)
            family = families.get(legacy._key(signature)) if signature is not None else None
            descriptor = describe(store, plan, declaration, source)
            rows.append({"attempt_id": plan.get("attempt_id"), "phase": phase,
                         "source": source, "variant": "hierarchical",
                         "class_id": family["class_id"] if family else None,
                         "reason": ("known_entry_family" if family else
                                    "unseen_entry_family" if signature is not None else "binding_unknown"),
                         "binding_reasons": reasons, "descriptor": descriptor,
                         "pattern_match": (compatible_patterns(descriptor, family["structural_patterns"])
                                           if family else {"status": "family_unknown", "candidate_pattern_ids": []})})
    return rows


def evaluate(store, plans, records, declaration, model_path, out):
    model_path, out = Path(model_path), Path(out)
    model = json.loads(model_path.read_text(encoding="utf-8"))
    legacy.evaluate(store, plans, records, declaration, model_path.parent / model["legacy_model"], out)
    assignments = _assign(store, plans, declaration, model, "class_test")
    targets = _assign(store, plans, declaration, model, "target")
    labels = {r["attempt_id"]: r["operation"] for r in records
              if r.get("phase") == "class_test" and r.get("operation") and r.get("attempt_id")}
    metrics = []
    for source in legacy.SOURCES:
        rows = [r for r in assignments if r["source"] == source]
        known = [r for r in rows if r["class_id"] is not None]
        labeled = [r for r in known if r["attempt_id"] in labels]
        metrics.append({"source": source, "variant": "hierarchical", "total": len(rows),
                        "known": len(known), "unknown": len(rows) - len(known),
                        "coverage": len(known) / len(rows) if rows else None,
                        "ari_on_known_subset": ari([labels[r["attempt_id"]] for r in labeled],
                                                   [r["class_id"] for r in labeled]),
                        "ari_labeled_known_subset": len(labeled),
                        "pattern_statuses": dict(Counter(r["pattern_match"]["status"] for r in rows)),
                        "equivalent_to_base_family_assignment": True,
                        "labels_used_after_prediction_only": True})
    result = {"schema_version": "classes-v5-evaluation", "model": str(model_path.resolve()),
              "class_test_assignments": assignments, "target_descriptive_assignments": targets,
              "class_test_metrics": metrics, "fit_updated_during_evaluation": False,
              "interpretation": "stable route families with uncertain structure; no recognition gain over base claimed"}
    _write(out / "classes-v5.json", result)
    return result
