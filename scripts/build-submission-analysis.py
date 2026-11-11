#!/usr/bin/env python3
"""Reaggregate the pinned publication data in GitHub Actions.

This program never reconstructs a model, recomputes ARI from assignments, refits a
forecast, or selects cases by observed accuracy. Primary summaries use one raw
projection per source and one outcome record per case-operation. Both saved
views and all unavailable/adverse observations remain in the machine-readable
outputs. The source archives are not modified.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from statistics import mean, median
import sys


PINS = {
    "original": "1153f70032bc36bbc1936e666c8338e0935c24d2c8553b64836e711c9005bf36",
    "corrected": "d772bd51c199397f5b5d2aaa623d255946cbaf6541b7955ab74a145eaac2a345",
    "correction_report": "d69134c8bf4bc617d3ab5fbe8146617277c7b62cd425801a9c9a8b3928b57f44",
    "cost_ledger": "198cd5825bea33567353afb5166d552c9a2df963b8f4a86628122de82a4cbf3e",
    "provenance": "851a1d5a3f10077ebdbf4d4da9feb9bf29fd32c9d744b9d939ada930a6c05db1",
}
SYSTEMS = ("petclinic", "otel_demo", "deathstarbench")
MODES = ("absent", "partial", "full")
REPETITIONS = (9, 10, 11)
ARMS = ("none", "obi", "coroot", "deepflow")
SOURCES = ("native", "ebpf", "combined", "context-baseline")
VIEWS = ("raw", "network_scope")
STATES = ("11", "10", "01", "00")
OPERATIONS = {
    "petclinic": ("list_owners", "list_vets", "owner_details_with_visits", "create_visit"),
    "otel_demo": ("browse_product", "add_to_cart", "checkout"),
    "deathstarbench": ("compose_post", "read_home_timeline", "read_user_timeline"),
}
LABELS = {"petclinic": "Petclinic", "otel_demo": "OTel Demo", "deathstarbench": "Social Network",
          "none": "No agent", "obi": "OBI", "coroot": "Coroot", "deepflow": "DeepFlow"}
EPS = 1e-12


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def read_pinned(path, role):
    require(path.is_absolute(), f"{role} path must be absolute")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    require(digest == PINS[role], f"{role} SHA-256 mismatch: {digest}")
    return json.loads(data), {"path": path.name, "bytes": len(data), "sha256": digest}


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def equal_number(a, b):
    return a is None and b is None or numeric(a) and numeric(b) and abs(a - b) <= EPS


def checked_counts(value):
    require(isinstance(value, dict), "missing outcome counts")
    result = {k: value.get(k, 0) for k in ("success", "failure", "unknown", "invalid", "total")}
    require(all(type(v) is int and v >= 0 for v in result.values()), "invalid outcome count")
    require(sum(result[k] for k in ("success", "failure", "unknown", "invalid")) == result["total"],
            "outcome counts do not close")
    return result


def bounds(counts):
    if not counts["total"] or counts["invalid"]:
        return [None, None]
    return [counts["success"] / counts["total"],
            (counts["success"] + counts["unknown"]) / counts["total"]]


def error(prediction, counts):
    low, high = bounds(counts)
    if prediction is None or low is None:
        return {"range": None, "worst_end_error": None}
    require(numeric(prediction) and 0 <= prediction <= 1, "malformed probability")
    least = 0.0 if low <= prediction <= high else min(abs(prediction - low), abs(prediction - high))
    return {"range": [least, max(abs(prediction - low), abs(prediction - high))],
            "worst_end_error": max(abs(prediction - low), abs(prediction - high))}


def check_saved_error(actual, saved, label):
    require(equal_number(actual["worst_end_error"], saved["worst_end_error"]), label + " saved error differs")
    require(actual["range"] is None and saved["range"] is None or
            isinstance(actual["range"], list) and isinstance(saved["range"], list) and
            len(actual["range"]) == len(saved["range"]) == 2 and
            all(equal_number(a, b) for a, b in zip(actual["range"], saved["range"])),
            label + " saved interval differs")


def add_counts(values):
    return {k: sum(v[k] for v in values) for k in ("success", "failure", "unknown", "invalid", "total")}


def identity(key):
    require(len(key) == 4, "case key has wrong arity")
    return dict(zip(("system", "sdk", "repetition", "collector"), key))


def case_key(row):
    return tuple(row[k] for k in ("system", "sdk", "repetition", "collector"))


def operation_key(row):
    return case_key(row) + (row["operation"],)


def normalized_row(key, row, corrected):
    r = {**identity(key), "operation": row["operation"], "source": row["source"],
         "view": row["view"] if corrected else row["variant"],
         "measurement_generation": "corrected_social_network" if corrected else "original_petclinic_otel"}
    f = row["primary_forecast"] if corrected else row
    observed = checked_counts(row["observed"] if corrected else row["actual_counts"])
    db_up = checked_counts(row["db_up"] if corrected else row["database_up_actual_counts"])
    db_down = checked_counts(row["db_down"] if corrected else row["database_down_actual_counts"])
    r.update(available=f["available"], prediction=f["prediction"] if f["available"] else None)
    require(type(r["available"]) is bool, "availability must be boolean")
    require(not r["available"] or numeric(r["prediction"]), "available forecast has no probability")
    pe = error(r["prediction"], observed)
    check_saved_error(pe, row["primary_error"] if corrected else row["error"], "primary")
    direct = row["direct_baseline"] if corrected else row["direct_reference"]
    direct_prediction = direct["prediction"] if direct["available"] else None
    require(numeric(direct_prediction), "direct conditional reference missing")
    direct_db = direct["database"]
    direct_db_prediction = direct_db["database_down_prediction"] if direct_db["available"] else None
    if corrected:
        db = f.get("database_forecast") or {}
        db_prediction = db.get("prediction") if db.get("available") else None
        check_saved_error(error(db_prediction, db_down), row["database_down_error"], "database")
        check_saved_error(error(direct_prediction, observed), row["direct_primary_error"], "direct primary")
        check_saved_error(error(direct_db_prediction, db_down), row["direct_database_down_error"], "direct database")
    else:
        db_prediction = row["database_down_prediction"]
    state_counts, state_predictions = {}, {}
    for state in STATES:
        saved = row["by_state"][state]
        state_counts[state] = checked_counts(saved if corrected else saved["actual_counts"])
        state_predictions[state] = f.get("by_state", {}).get(state) if corrected and r["available"] else (
            saved.get("prediction") if not corrected else None)
    require(add_counts(state_counts.values()) == observed, "state counts do not equal target counts")
    r.update(observed=observed, observed_bounds=bounds(observed), by_state=state_counts,
             prediction_by_state=state_predictions, error=pe,
             direct_prediction=direct_prediction, direct_error=error(direct_prediction, observed),
             direct_prediction_by_state=direct["by_state"],
             db_up=db_up, db_down=db_down, db_prediction=db_prediction,
             db_error=error(db_prediction, db_down), direct_db_prediction=direct_db_prediction,
             direct_db_error=error(direct_db_prediction, db_down),
             unavailable_reason=(f.get("reason") if corrected else row.get("unavailable_reason"))
                                if not r["available"] else None,
             graph_sha256=f.get("execution", {}).get("graph_sha256") if corrected else row.get("graph_sha256"))
    if corrected:
        semantics = direct["outcome_contract_scope"]
        r["outcome_semantics"] = semantics["outcomes"][row["operation"]]
    else:
        r["outcome_semantics"] = "original operation-specific external postcondition"
    return r


def flatten_row(row):
    result = {k: row[k] for k in ("system", "sdk", "repetition", "collector", "operation", "source", "view",
                                  "measurement_generation", "available", "prediction", "direct_prediction",
                                  "db_prediction", "direct_db_prediction", "outcome_semantics", "graph_sha256")}
    for name in ("observed", "db_up", "db_down"):
        result.update({name + "_" + k: v for k, v in row[name].items()})
    for name in ("error", "direct_error", "db_error", "direct_db_error"):
        value = row[name]["worst_end_error"]
        result[name] = value
        result[name + "_pp"] = None if value is None else 100 * value
    result["observed_lower"], result["observed_upper"] = row["observed_bounds"]
    result["unavailable_reason"] = canonical(row["unavailable_reason"])
    return result


def describe_numbers(values):
    finite = [v for v in values if v is not None]
    return {"known": len(finite), "missing": len(values) - len(finite),
            "mean": mean(finite) if finite else None, "median": median(finite) if finite else None,
            "min": min(finite) if finite else None, "max": max(finite) if finite else None}


def metrics(rows, database=False):
    field = "db_error" if database else "error"
    prediction = "db_prediction" if database else "prediction"
    eligible = [r for r in rows if r[prediction] is not None]
    known = [r for r in eligible if r[field]["worst_end_error"] is not None]
    by_case = defaultdict(list)
    for row in rows:
        by_case[case_key(row)].append(row)
    case_means, case_support = [], []
    for group in by_case.values():
        errors = [r[field]["worst_end_error"] for r in group if r[field]["worst_end_error"] is not None]
        case_means.append(mean(errors) if errors else None)
        case_support.append(sum(r[prediction] is not None for r in group) / len(group))
    return {"cases": len(by_case), "operation_cases": len(rows), "available": len(eligible),
            "unavailable": len(rows) - len(eligible), "support_fraction": len(eligible) / len(rows) if rows else None,
            "known_errors": len(known), "available_but_unknown_errors": len(eligible) - len(known),
            "nonzero_errors": sum(r[field]["worst_end_error"] > EPS for r in known),
            "max_error": max((r[field]["worst_end_error"] for r in known), default=None),
            "case_mean_error": describe_numbers(case_means),
            "case_support_fraction": describe_numbers(case_support)}


def grouped_metrics(rows, keys, database=False):
    grouped = defaultdict(list)
    for row in rows:
        grouped[tuple(row[k] for k in keys)].append(row)
    return [{**dict(zip(keys, key)), **metrics(group, database)} for key, group in sorted(grouped.items())]


def flat_metrics(row):
    result = {}
    for k, v in row.items():
        if isinstance(v, dict):
            result.update({k + "_" + kk: vv for kk, vv in v.items()})
        else:
            result[k] = v
    return result


def write_csv(path, rows):
    require(rows, f"refusing to emit empty table {path.name}")
    names = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=names)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: canonical(v) if isinstance(v, (dict, list, tuple)) else v for k, v in row.items()})


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def tex(value):
    mapping = {"\\": r"\textbackslash{}", "_": r"\_", "%": r"\%", "&": r"\&", "#": r"\#"}
    return "".join(mapping.get(ch, ch) for ch in str(value))


def table(path, header, rows, align, long=False):
    env = "longtable" if long else "tabular"
    lines = [r"\begin{" + env + "}{" + align + "}", r"\toprule",
             " & ".join(header) + r" \\", r"\midrule"]
    if long:
        lines += [r"\endfirsthead", r"\toprule", " & ".join(header) + r" \\",
                  r"\midrule", r"\endhead"]
    lines += [" & ".join(str(v) for v in row) + r" \\" for row in rows]
    lines += [r"\bottomrule", r"\end{" + env + "}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for role in PINS:
        parser.add_argument("--" + role.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--zenodo-doi", default="10.5281/zenodo.24131735")
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true", "scientific reaggregation must run in GitHub Actions")
    require(args.out.is_absolute(), "output path must be absolute")
    require(not args.out.exists() or not any(args.out.iterdir()), "output directory must be new or empty")
    inputs, manifests = {}, {}
    for role in PINS:
        inputs[role], manifests[role] = read_pinned(getattr(args, role), role)
    old, corrected, report = inputs["original"], inputs["corrected"], inputs["correction_report"]
    ledger, provenance = inputs["cost_ledger"], inputs["provenance"]
    require(old["status"] == corrected["status"] == report["status"] == "complete", "incomplete input report")
    require(corrected["source"] == report["capture_source"] == "a53b45d510584b79e6a558945740a17a46bb0830",
            "wrong corrected measurement source")
    require(str(corrected["run_id"]) == str(report["capture_run_id"]) == "42769442057", "wrong corrected run")
    require(corrected["new_graph_discovery"] is False and corrected["write_or_durability_evidence"] is False,
            "correction scope changed")
    require(corrected["corrected_forecasts_before_fresh_targets"] is True, "correction freeze missing")
    require(old["coverage"]["actual_cells"] == 108 and old["coverage"]["actual_rows"] == 2880,
            "original full matrix differs")
    require(old["cost_ledger"]["literal"] == ledger, "embedded original ledger differs")
    require(report["generated_summary_asset"]["digest"] == "sha256:" + PINS["corrected"], "summary binding differs")
    require(corrected["counts"] == {"fresh_cases": 36, "case_operation_sets": 108, "source_view_rows": 864},
            "corrected summary census differs")
    original_by_key = {}
    for cell in old["cells"]:
        key = tuple(cell["key"])
        require(key not in original_by_key, "duplicate original key")
        original_by_key[key] = cell
    expected = set(itertools.product(SYSTEMS, MODES, REPETITIONS, ARMS))
    require(set(original_by_key) == expected, "original matrix identity differs")
    corrected_by_key = {}
    for cell in corrected["cases"]:
        key = tuple(cell["key"])
        require(key not in corrected_by_key, "duplicate corrected key")
        corrected_by_key[key] = cell
    require(set(corrected_by_key) == {k for k in expected if k[0] == "deathstarbench"}, "corrected matrix differs")
    rows, cases, classifications, latencies, asynchronous, case_provenance = [], [], [], [], [], []
    for key in sorted(expected):
        is_corrected = key[0] == "deathstarbench"
        old_cell = original_by_key[key]
        cell = corrected_by_key[key] if is_corrected else old_cell
        result = cell["result"] if is_corrected else cell["literal_evaluation"]
        require(result["technical_complete"] is True, "technical incomplete case in publication selection")
        case_rows = [normalized_row(key, row, is_corrected) for row in result["rows"]]
        required = set(itertools.product(OPERATIONS[key[0]], SOURCES, VIEWS))
        actual = {(r["operation"], r["source"], r["view"]) for r in case_rows}
        require(actual == required and len(case_rows) == len(required), "operation/source/view matrix differs")
        unique_operations = []
        for operation in OPERATIONS[key[0]]:
            group = [r for r in case_rows if r["operation"] == operation]
            first = group[0]
            shared = ("observed", "by_state", "direct_prediction", "direct_prediction_by_state", "direct_error", "db_up", "db_down",
                      "direct_db_prediction", "direct_db_error")
            require(all(all(r[k] == first[k] for k in shared) for r in group),
                    "source/view projections do not share the same external outcomes")
            unique_operations.append(first)
        target = add_counts([r["observed"] for r in unique_operations])
        db_up = add_counts([r["db_up"] for r in unique_operations])
        db_down = add_counts([r["db_down"] for r in unique_operations])
        require(target["total"] == 9600 and db_up["total"] == db_down["total"] == 20,
                "fixed per-case external workload differs")
        cases.append({**identity(key), "measurement_generation": "corrected" if is_corrected else "original",
                      "operation_count": len(unique_operations), "source_view_rows": len(case_rows),
                      "capture_allocation_regime": old_cell["allocation_regime"],
                      **{"target_" + k: v for k, v in target.items()},
                      **{"db_up_" + k: v for k, v in db_up.items()},
                      **{"db_down_" + k: v for k, v in db_down.items()}})
        rows.extend(case_rows)
        class_report = result.get("frozen_classification_applied_without_refit" if is_corrected else "frozen_classification")
        require(class_report and class_report["fit_updated_during_evaluation"] is False, "classification freeze missing")
        for metric in class_report["class_test_metrics"]:
            classifications.append({**identity(key), **metric, "metric_provenance": "reported_from_frozen_evaluation",
                                    "recomputed_from_assignments": False})
        if not is_corrected:
            latencies.append({**identity(key), **result["target_latency"],
                              "metric_provenance": "reported_case_quantiles_not_recomputed_or_pooled"})
        if key[0] == "otel_demo":
            require(result["asynchronous"] is not None, "missing OTel asynchronous controls")
            for phase, details in result["asynchronous"].items():
                asynchronous.append({**identity(key), "phase": phase, **details,
                                     "resumed_phase_reuses_paused_requests": phase == "paused_after_resume"})
        if is_corrected:
            case_provenance.append({"key": key, "measurement_generation": "corrected",
                                    "capture_producer": cell["capture_producer"],
                                    "target_publication": cell["publication"],
                                    "original_model": result["original_model"],
                                    "forecast_source": result["forecast_execution_source"],
                                    "forecast_run": result["forecast_execution_run_id"],
                                    "original_result_retained_but_excluded_from_current_analysis": True})
        else:
            case_provenance.append({"key": key, "measurement_generation": "original",
                                    **{k: old_cell[k] for k in ("allocation_regime", "original_metadata_artifact",
                                        "original_forecast", "verified_replay_lineage", "source_member_hashes", "omitted")}})

    raw = [r for r in rows if r["view"] == "raw"]
    require(len(cases) == 108 and len(rows) == 2880 and len(raw) == 1440, "selected matrix counts differ")
    grouped_operations = defaultdict(list)
    for row in raw:
        grouped_operations[operation_key(row)].append(row)
    operation_rows, direct_rows, state_rows, database_outcomes = [], [], [], []
    for key, group in sorted(grouped_operations.items()):
        first = group[0]
        supported = [r for r in group if r["available"]]
        predictions = sorted({r["prediction"] for r in supported})
        observed, direct_error = first["observed"], first["direct_error"]["worst_end_error"]
        row = {**identity(key[:4]), "operation": key[4], **observed,
               "observed_lower": first["observed_bounds"][0], "observed_upper": first["observed_bounds"][1],
               "direct_prediction": first["direct_prediction"], "direct_error": direct_error,
               "direct_error_pp": None if direct_error is None else direct_error * 100,
               "has_observation_forecast": bool(supported), "available_sources": [r["source"] for r in supported],
               "supported_predictions": predictions,
               "any_supported_forecast_error": any(r["error"]["worst_end_error"] is not None and
                                                     r["error"]["worst_end_error"] > EPS for r in supported),
               "max_supported_error": max((r["error"]["worst_end_error"] for r in supported
                                           if r["error"]["worst_end_error"] is not None), default=None)}
        operation_rows.append(row)
        direct_rows.append({**identity(key[:4]), "operation": key[4], "source": "direct-reference", "view": "raw",
                            "prediction": first["direct_prediction"], "available": True,
                            "observed": observed, "error": first["direct_error"],
                            "db_prediction": first["direct_db_prediction"], "db_error": first["direct_db_error"]})
        for state in STATES:
            state_prediction = first["direct_prediction_by_state"][state]
            state_rows.append({**identity(key[:4]), "operation": key[4], "state": state,
                               **first["by_state"][state], "direct_prediction": state_prediction,
                               "direct_error": error(state_prediction, first["by_state"][state])["worst_end_error"]})
        database_outcomes.append({**identity(key[:4]), "operation": key[4],
                                  **{"db_up_" + k: v for k, v in first["db_up"].items()},
                                  **{"db_down_" + k: v for k, v in first["db_down"].items()},
                                  "direct_db_prediction": first["direct_db_prediction"],
                                  "direct_db_error": first["direct_db_error"]["worst_end_error"],
                                  "outcome_semantics": first["outcome_semantics"]})
    require(len(operation_rows) == 360, "unique case-operation count differs")
    target_counts = add_counts(operation_rows)
    primary_groups = grouped_metrics(raw, ("system", "sdk", "collector", "source"))
    all_view_groups = grouped_metrics(rows, ("system", "sdk", "collector", "source", "view"))
    database_groups = grouped_metrics(rows, ("system", "sdk", "collector", "source", "view"), True)
    direct_groups = grouped_metrics(direct_rows, ("system", "sdk", "collector", "source"))
    primary_coverage_by_case = []
    for key, group in itertools.groupby(sorted(raw, key=lambda r: case_key(r) + (r["source"],)),
                                        key=lambda r: case_key(r) + (r["source"],)):
        primary_coverage_by_case.append({**identity(key[:4]), "source": key[4], **metrics(list(group))})

    by_projection = {(operation_key(r), r["source"], r["view"]): r for r in rows}
    primary_view_differences = []
    for row in raw:
        other = by_projection[(operation_key(row), row["source"], "network_scope")]
        if row["available"] != other["available"] or not equal_number(row["prediction"], other["prediction"]):
            primary_view_differences.append({"key": operation_key(row), "source": row["source"]})
    require(not primary_view_differences, "primary views differ; the predeclared collapse is not justified")
    context_comparisons = []
    for opkey in sorted(grouped_operations):
        combined = by_projection[(opkey, "combined", "raw")]
        context = by_projection[(opkey, "context-baseline", "raw")]
        context_comparisons.append({**identity(opkey[:4]), "operation": opkey[4],
                                   "combined_available": combined["available"], "context_available": context["available"],
                                   "combined_prediction": combined["prediction"], "context_prediction": context["prediction"],
                                   "availability_differs": combined["available"] != context["available"],
                                   "context_only": context["available"] and not combined["available"],
                                   "combined_only": combined["available"] and not context["available"],
                                   "both_available_prediction_differs": combined["available"] and context["available"] and
                                    not equal_number(combined["prediction"], context["prediction"])})
    classification_groups = []
    group_class = defaultdict(list)
    for row in classifications:
        group_class[(row["system"], row["sdk"], row["collector"], row["source"])].append(row)
    for key, group in sorted(group_class.items()):
        classification_groups.append({**dict(zip(("system", "sdk", "collector", "source"), key)),
                                     "cases": len(group), "total_assignments_across_cases": sum(r["total"] for r in group),
                                     "known_assignments_across_cases": sum(r["known"] for r in group),
                                     "unknown_assignments_across_cases": sum(r["unknown"] for r in group),
                                     "case_coverage": describe_numbers([r["coverage"] for r in group]),
                                     "reported_case_ari_on_known_subset": describe_numbers([r["ari_on_known_subset"] for r in group]),
                                     "all_equal_base_family": all(r["equivalent_to_base_family_assignment"] for r in group),
                                     "pooled_ari_computed": False})
    latency_groups = []
    group_latency = defaultdict(list)
    for row in latencies:
        group_latency[(row["system"], row["sdk"], row["collector"])].append(row)
    for key, group in sorted(group_latency.items()):
        latency_groups.append({**dict(zip(("system", "sdk", "collector"), key)), "cases": len(group),
                               **{f"case_{metric}_ms": describe_numbers([r.get(metric) for r in group])
                                  for metric in ("p50", "p90", "mean", "max")},
                               "pooled_quantiles_computed": False, "causal_collector_overhead_claimed": False})
    cost_rows = []
    for category, value in ledger["summary"].items():
        cost_rows.append({"scope": "original_pre_reader_cut", "category": category,
                          "known_worker_seconds": value["known_worker_interval_seconds"],
                          "unknown_interval_rows": value["unknown_interval_rows"],
                          "API_rows": value["API_rows"], "exact_extra_alias_rows": value["exact_extra_alias_rows"],
                          "additive_category": category == "all/all"})
    closing = provenance["cost_scope"]
    cost_rows += [{"scope": "original_closing_cut", "category": "all/all",
                   "known_worker_seconds": closing["closing_unique_known_worker_seconds"],
                   "unknown_interval_rows": None, "additive_category": True},
                  {"scope": "correction_finite_cut", "category": "all/all",
                   "known_worker_seconds": report["costs"]["known_incremental_worker_seconds"],
                   "unknown_interval_rows": len(report["costs"]["unknown_intervals"]), "additive_category": True}]
    known_subtotal = sum(r["known_worker_seconds"] for r in cost_rows if r["additive_category"])
    require(ledger["summary"]["all/all"]["known_worker_interval_seconds"] == closing["pre_reader_unique_known_worker_seconds"],
            "cost scope cross-reference differs")
    obs_supported = [r for r in operation_rows if r["has_observation_forecast"]]
    graph_misses = [r for r in obs_supported if r["any_supported_forecast_error"]]
    direct_misses = [r for r in operation_rows if r["direct_error"] is not None and r["direct_error"] > EPS]
    available_rows = [r for r in rows if r["available"]]
    unsupported_direct_misses = [r for r in direct_misses if not r["has_observation_forecast"]]
    equal_direct = all(equal_number(r["prediction"], r["direct_prediction"]) for r in available_rows)
    obi_absent = [r for r in raw if r["collector"] == "obi" and r["source"] == "ebpf" and
                  r["sdk"] == "absent" and r["system"] in ("petclinic", "otel_demo")]
    require(len(obi_absent) == 21, "OBI absent Petclinic/OTel census differs")
    db_available = [r for r in rows if r["db_prediction"] is not None]
    operation_group_summaries = []
    for system, sdk in itertools.product(SYSTEMS, MODES):
        group = [r for r in operation_rows if r["system"] == system and r["sdk"] == sdk]
        operation_group_summaries.append({"system": system, "sdk": sdk, "case_operation_sets": len(group),
            "sets_with_available_forecast": sum(r["has_observation_forecast"] for r in group),
            "sets_with_graph_forecast_miss": sum(r["any_supported_forecast_error"] for r in group),
            "sets_with_direct_miss": sum(r["direct_error"] is not None and r["direct_error"] > EPS for r in group),
            "sets_with_direct_miss_without_graph": sum(r["direct_error"] is not None and r["direct_error"] > EPS and
                                                         not r["has_observation_forecast"] for r in group),
            "max_direct_error": max((r["direct_error"] for r in group if r["direct_error"] is not None), default=None)})

    summary = {
        "schema": "sosym-publication-analysis-v1", "zenodo_doi": args.zenodo_doi,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "execution": {"run_id": os.environ.get("GITHUB_RUN_ID"), "source": os.environ.get("GITHUB_SHA"),
                      "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "inputs": manifests,
        "selection": {"original_selected_cases": 72, "corrected_selected_cases": 36,
                      "historical_social_network_cases_excluded_from_current_analysis": 36,
                      "no_outcome_based_selection": True, "cases": 108, "logical_blocks": 27,
                      "source_view_rows": len(rows), "raw_source_rows": len(raw), "case_operation_sets": len(operation_rows),
                      "capture_allocation_regimes": dict(Counter(c["capture_allocation_regime"] for c in cases))},
        "primary": {"distinct_target_counts": target_counts, "available_source_view_rows": len(available_rows),
                    "available_raw_source_rows": sum(r["available"] for r in raw),
                    "unavailable_raw_source_rows": sum(not r["available"] for r in raw),
                    "case_operation_sets_with_available_forecast": len(obs_supported),
                    "case_operation_sets_without_available_forecast": len(operation_rows) - len(obs_supported),
                    "case_operation_sets_with_graph_forecast_miss": len(graph_misses),
                    "case_operation_sets_with_direct_miss": len(direct_misses),
                    "direct_misses_with_graph_forecast": len(direct_misses) - len(unsupported_direct_misses),
                    "direct_misses_without_graph_forecast": len(unsupported_direct_misses),
                    "nonzero_error_source_view_rows": sum(r["error"]["worst_end_error"] is not None and
                                                            r["error"]["worst_end_error"] > EPS for r in rows),
                    "all_available_forecasts_equal_direct_reference": equal_direct,
                    "max_available_forecast_error": max((r["error"]["worst_end_error"] for r in available_rows
                                                          if r["error"]["worst_end_error"] is not None), default=None),
                    "primary_view_differences": primary_view_differences},
        "obi_absent_petclinic_otel": {**metrics(obi_absent), "distinct_counts": add_counts([r["observed"] for r in obi_absent]),
                                    "errors": [flatten_row(r) for r in obi_absent]},
        "primary_groups": primary_groups, "all_view_groups": all_view_groups,
        "operation_group_summaries": operation_group_summaries,
        "database": {"available_source_view_rows": len(db_available),
                     "available_raw_rows": sum(r["view"] == "raw" for r in db_available),
                     "available_network_rows": sum(r["view"] == "network_scope" for r in db_available),
                     "by_system": dict(Counter(r["system"] for r in db_available)),
                     "distinct_case_operation_sets_with_available_forecast": len({operation_key(r) for r in db_available}),
                     "nonzero_errors": sum(r["db_error"]["worst_end_error"] is not None and
                                           r["db_error"]["worst_end_error"] > EPS for r in db_available),
                     "all_available_equal_direct": all(equal_number(r["db_prediction"], r["direct_db_prediction"])
                                                       for r in db_available),
                     "social_network_write_or_durability_claim": False},
        "database_groups": database_groups, "direct_groups": direct_groups,
        "context_comparison": {"case_operation_sets": len(context_comparisons),
                               "context_only": sum(r["context_only"] for r in context_comparisons),
                               "combined_only": sum(r["combined_only"] for r in context_comparisons),
                               "both_available_prediction_differences": sum(r["both_available_prediction_differs"] for r in context_comparisons)},
        "classification_groups": classification_groups, "latency_groups": latency_groups,
        "costs": {"finite_known_worker_seconds_subtotal": known_subtotal,
                  "finite_known_worker_hours_subtotal": known_subtotal / 3600,
                  "original_ledger_scope": ledger["scope"], "original_cut_utc": ledger["cut_utc"],
                  "original_unknown_interval_rows": ledger["summary"]["all/all"]["unknown_interval_rows"],
                  "original_unallocated_annotation": ledger["unallocated_runner_interval_annotation"],
                  "closing_scope": {k: v for k, v in closing.items() if k != "closing_workflows"},
                  "correction_unknown_intervals": report["costs"]["unknown_intervals"],
                  "correction_cut_ns": report["finite_metadata_cut_ns"],
                  "complete_comparable_cost_comparison": False, "human_seconds": None,
                  "successful_finalizer_and_later_delivery_costs_not_in_finite_subtotal": True,
                  "worker_intervals_are_not_CPU_billing_or_sequential_elapsed_time": True,
                  "nested_phase_or_reader_telemetry_added_again": False},
        "interpretation": {"source_view_rows_share_external_attempts": True,
                           "no_pooled_request_IID_confidence_intervals": True,
                           "error_summary_unit": "case-level mean across available operation forecasts; availability denominator retained",
                           "latency_and_ARI_are_saved_aggregate_metrics": True,
                           "new_measurements": False, "new_model_build": False,
                           "all_historical_request_records_in_publication_package": False},
    }
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    csv_outputs = {
        "cases.csv": cases, "source-view-results.csv": [flatten_row(r) for r in rows],
        "primary-outcomes.csv": operation_rows, "primary-state-outcomes.csv": state_rows,
        "database-outcomes.csv": database_outcomes,
        "primary-summary.csv": [flat_metrics(r) for r in primary_groups],
        "all-view-summary.csv": [flat_metrics(r) for r in all_view_groups],
        "case-source-summary.csv": [flat_metrics(r) for r in primary_coverage_by_case],
        "database-summary.csv": [flat_metrics(r) for r in database_groups],
        "direct-summary.csv": [flat_metrics(r) for r in direct_groups],
        "operation-summary.csv": operation_group_summaries,
        "context-comparison.csv": context_comparisons,
        "classification.csv": classifications,
        "classification-summary.csv": [flat_metrics(r) for r in classification_groups],
        "case-latency.csv": latencies,
        "latency-summary.csv": [flat_metrics(r) for r in latency_groups],
        "asynchronous-controls.csv": asynchronous, "costs.csv": cost_rows,
        "obi-absent-results.csv": [flatten_row(r) for r in obi_absent],
        "all-primary-discrepancies.csv": direct_misses,
    }
    for filename, values in csv_outputs.items():
        write_csv(out / filename, values)
    write_json(out / "analysis.json", summary)
    write_json(out / "case-provenance.json", case_provenance)
    lookup = {(r["system"], r["sdk"], r["collector"], r["source"]): r for r in primary_groups}
    def support(system, sdk, arm, source):
        group = lookup[(system, sdk, arm, source)]
        return f'{group["available"]}/{group["operation_cases"]}'
    full_coverage = [[LABELS[system], sdk, LABELS[arm], *[support(system, sdk, arm, source) for source in SOURCES]]
                     for system, sdk, arm in itertools.product(SYSTEMS, MODES, ARMS)]
    table(out / "table-coverage-full.tex", ["Application", "SDK", "Treatment", "Native", "eBPF", "Combined", "Context"],
          full_coverage, "@{}lllrrrr@{}", long=True)
    main_coverage = [[LABELS[system], sdk, support(system, sdk, "none", "native"),
                     *[support(system, sdk, arm, "ebpf") for arm in ("obi", "coroot", "deepflow")],
                     support(system, sdk, "obi", "combined"), support(system, sdk, "obi", "context-baseline")]
                    for system, sdk in itertools.product(SYSTEMS, MODES)]
    table(out / "table-coverage-main.tex", ["Application", "SDK", "Native control", "OBI", "Coroot", "DeepFlow", "Combined", "Context"],
          main_coverage, "@{}llrrrrrr@{}")
    summary_table = [[LABELS[r["system"]], r["sdk"], r["case_operation_sets"], r["sets_with_available_forecast"],
                      r["sets_with_graph_forecast_miss"], r["sets_with_direct_miss"],
                      f'{r["max_direct_error"]*100:.5f}'.rstrip("0").rstrip(".")]
                     for r in operation_group_summaries]
    table(out / "table-errors-summary.tex", ["Application", "SDK", "Sets", "Supported", "Graph misses", "Direct misses", "Max. error (pp)"],
          summary_table, "@{}llrrrrr@{}")
    discrepancy_table = [[LABELS[r["system"]], tex(f'{r["sdk"]}/{r["repetition"]}, {LABELS[r["collector"]]}'),
                          tex(r["operation"]), f'{r["success"]}/{r["total"]}', f'{r["direct_prediction"]:.3f}',
                          f'{r["direct_error_pp"]:.5f}'.rstrip("0").rstrip("."),
                          "yes" if r["has_observation_forecast"] else "no"] for r in direct_misses]
    table(out / "table-all-discrepancies.tex", ["Application", "Case", "Operation", "Successes", "Forecast", "Error (pp)", "Graph"],
          discrepancy_table, "@{}lllr r r l@{}", long=True)
    metadata = {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted(out.iterdir()) if p.is_file()}
    write_json(out / "analysis-manifest.json", {"schema": "sosym-analysis-files-v1", "outputs": metadata,
                                               "inputs": manifests, "new_measurements": False})
    print(json.dumps({"selection": summary["selection"], "primary": summary["primary"],
                      "obi_absent": {k: v for k, v in summary["obi_absent_petclinic_otel"].items() if k != "errors"},
                      "database": summary["database"], "context": summary["context_comparison"],
                      "finite_known_worker_seconds": known_subtotal,
                      "output_files": len(metadata) + 1}, indent=2), flush=True)


if __name__ == "__main__":
    main()
