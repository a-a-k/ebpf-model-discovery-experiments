"""External evaluation of graph-driven v4 forecasts without outcome leakage."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import importlib
import json
import math
from pathlib import Path
from statistics import mean


PRIMARY_PHASES = {"class_train", "calibration", "target", "class_test"}
EXPECTED_PRIMARY_PER_CELL = 34_800
EXPECTED_GRID_TOTAL = 939_600
SOURCES = ("ebpf", "native", "combined")
VARIANTS = ("raw", "network_scope")


def _read(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _counts(records: list[dict]) -> dict:
    return {
        "success": sum(row.get("success") is True for row in records),
        "failure": sum(row.get("success") is False for row in records),
        "unknown": sum(row.get("success") is None for row in records),
        "total": len(records),
    }


def _bounds(counts: dict) -> list[float] | None:
    if not counts["total"]:
        return None
    return [counts["success"] / counts["total"],
            (counts["success"] + counts["unknown"]) / counts["total"]]


def _wilson(success: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if not total:
        return None
    center = (success + z*z/2) / (total + z*z)
    half = z * math.sqrt(success*(total-success)/total + z*z/4) / (total + z*z)
    return [max(0.0, center-half), min(1.0, center+half)]


def _nominal_envelope(counts: dict) -> dict:
    total = counts["total"]
    lower = _wilson(counts["success"], total)
    upper = _wilson(counts["success"] + counts["unknown"], total)
    return {
        "interval": None if not total else [lower[0], upper[1]],
        "label": "nominal Wilson envelope under an IID Bernoulli assumption; unknowns bracketed as failure/success",
        "assumption": "IID repetitions; descriptive only, not an experiment admission or success threshold",
    }


def _error(prediction, bounds):
    if prediction is None or bounds is None:
        return {"range": None, "worst_end_error": None}
    low, high = bounds
    minimum = 0.0 if low <= prediction <= high else min(abs(prediction-low), abs(prediction-high))
    maximum = max(abs(prediction-low), abs(prediction-high))
    return {"range": [minimum, maximum], "worst_end_error": maximum}


def _latency(records: list[dict]) -> dict:
    values = sorted((row["ended_ns"]-row["started_ns"])/1e6 for row in records
                    if isinstance(row.get("started_ns"), int)
                    and isinstance(row.get("ended_ns"), int)
                    and row["ended_ns"] >= row["started_ns"])
    if not values:
        return {"count": 0, "unit": "milliseconds", "outcome_rule": "descriptive_not_deadline"}
    pick = lambda q: values[min(len(values)-1, int(q*(len(values)-1)))]
    return {"count": len(values), "unit": "milliseconds", "min": values[0],
            "p50": pick(.5), "p90": pick(.9), "max": values[-1], "mean": mean(values),
            "outcome_rule": "descriptive_not_deadline"}


def _integrity(root: Path, frozen: dict, forecasts: dict) -> dict:
    problems = []
    if not frozen or frozen.get("all_unchanged") is not True:
        problems.append("freeze_integrity_missing_or_false")
    for relative, expected in (frozen or {}).get("sha256_by_path", {}).items():
        path = root / relative
        if not path.is_file() or _digest(path) != expected:
            problems.append(f"frozen_hash_mismatch:{relative}")
    for source in SOURCES:
        for variant in VARIANTS:
            for operation, forecast in forecasts.get(source, {}).get(variant, {}).items():
                if not forecast.get("available"):
                    continue
                model = root / "toolchain" / source / variant / operation / "model.json"
                if not model.is_file() or forecast.get("graph_sha256") != _digest(model):
                    problems.append(f"forecast_graph_hash_mismatch:{source}:{variant}:{operation}")
                if forecast.get("simulator") != "Sheaft":
                    problems.append(f"forecast_not_sheaft:{source}:{variant}:{operation}")
    return {"valid": not problems, "problems": problems,
            "rule": "all frozen hashes and every available forecast's actual Sheaft graph hash must match"}


def _manual_baselines(system: str, operations: list[str]) -> dict:
    declaration = importlib.import_module(f"systems.{system}.experiment_v4")
    controlled = set(declaration.CONTROLLED_SERVICE_ALIASES)
    selected_db = getattr(declaration, "SELECTED_DATABASE", {})
    result = {}
    names = lambda value: {value} if isinstance(value, str) else set(value or [])
    for operation in operations:
        contract = declaration.CONTRACTS[operation]
        requires_controlled = any(
            bool(controlled & names(call.get("caller"))) or
            bool(controlled & names(call.get("callee")))
            for call in contract["required_calls"]
        )
        by_state = {state: (0.0 if requires_controlled and state == "00" else 1.0)
                    for state in ("11", "10", "01", "00")}
        prediction = .5*by_state["11"] + .25*by_state["10"] + .125*by_state["01"] + .125*by_state["00"]
        db_calls = [call for call in contract["required_calls"] if "db_system" in call]
        conditional = bool(contract.get("conditional_db"))
        if conditional:
            database = {"available": False, "reason": "declared_database_requirement_is_conditional"}
        elif selected_db and any(call.get("db_system") == selected_db.get("db_system") for call in db_calls):
            database = {"available": True, "database_down_prediction": 0.0,
                        "basis": "declared unconditional selected database requirement"}
        else:
            database = {"available": False, "reason": "no_sound_unconditional_selected_database_contract"}
        result[operation] = {
            "available": True, "prediction": prediction, "by_state": by_state,
            "basis": "declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph",
            "controlled_service_required": requires_controlled, "database": database,
        }
    return result


def _async_results(root: Path) -> dict:
    files = {
        "normal": "async-normal-persistence.json",
        "paused_snapshot": "async-paused-snapshot.json",
        "paused_after_resume": "async-paused-after-resume.json",
        "recovered": "async-recovered-persistence.json",
    }
    result = {}
    for label, name in files.items():
        rows = _read(root/name)
        if rows is None:
            result[label] = {"available": False, "reason": "file_missing"}
            continue
        states = {}
        for row in rows:
            verification = row.get("async_verification", {})
            state = verification.get("state", "unknown")
            states[state] = states.get(state, 0) + 1
        result[label] = {"available": True, "records": len(rows), "states": states,
                         "paused_absence_is_failure": False}
    return result


def _cost(root: Path, status: dict) -> dict:
    build = _read(root/"toolchain-build"/"toolchain-build.json", {})
    commands, returncodes = [], []
    for path in (root/"toolchain").rglob("*.command.json") if (root/"toolchain").exists() else []:
        row = _read(path, {})
        if isinstance(row.get("started_ns"), int) and isinstance(row.get("ended_ns"), int):
            commands.append((row["ended_ns"]-row["started_ns"])/1e9)
        returncodes.append(row.get("returncode"))
    time_file = root/"infrastructure"/"campaign-time.txt"
    time_fields = {}
    if time_file.is_file():
        for line in time_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if ":" in line:
                key, value = line.strip().split(":", 1)
                if key in {"User time (seconds)", "System time (seconds)",
                           "Elapsed (wall clock) time (h:mm:ss or m:ss)",
                           "Maximum resident set size (kbytes)"}:
                    time_fields[key] = value.strip()
    return {
        "campaign_elapsed_seconds": status.get("elapsed_seconds"),
        "toolchain_clone_seconds": sum(row.get("clone_seconds", 0) for row in build.get("binaries", [])),
        "toolchain_build_seconds": sum(row.get("build_seconds", 0) for row in build.get("binaries", [])),
        "toolchain_command_seconds": sum(commands), "toolchain_command_count": len(commands),
        "toolchain_command_returncodes": returncodes,
        "toolchain_command_failures": sum(code not in (0, None) for code in returncodes),
        "infrastructure_time_file": str(time_file), "infrastructure_time_fields": time_fields,
        "manual_preparation": {"measured": False, "reason": "human preparation time was not instrumented; no full-cost advantage claimed"},
    }


def evaluate_campaign(root: Path) -> dict:
    root = Path(root)
    status = _read(root/"status.json", {})
    records = _read(root/"external.json", [])
    blocks = _read(root/"blocks.json", [])
    forecasts = _read(root/"toolchain"/"forecasts.json", {})
    frozen = _read(root/"freeze-integrity.json", {})
    declared_operations = set()
    if status.get("system"):
        declared_operations = set(importlib.import_module(
            f"systems.{status['system']}.experiment_v4").CONTRACTS)
    operations = sorted({row.get("operation") for row in records if row.get("operation")}
                        | {op for source in forecasts.values() for variant in source.values() for op in variant}
                        | declared_operations)
    primary = [row for row in records if row.get("phase") in PRIMARY_PHASES]
    target = [row for row in records if row.get("phase") == "target"]
    integrity = _integrity(root, frozen, forecasts)
    complete = status.get("status") == "acquisition_complete" and integrity["valid"]
    evaluations = []
    for operation in operations:
        actual = [row for row in target if row.get("operation") == operation]
        actual_counts = _counts(actual)
        actual_bounds = _bounds(actual_counts)
        per_state = {}
        for state in ("11", "10", "01", "00"):
            state_counts = _counts([row for row in actual if row.get("state") == state])
            per_state[state] = {"counts": state_counts, "bounds": _bounds(state_counts)}
        for source in SOURCES:
            for variant in VARIANTS:
                forecast = forecasts.get(source, {}).get(variant, {}).get(operation)
                available = bool(complete and forecast and forecast.get("available"))
                prediction = forecast.get("prediction") if available else None
                state_eval = {}
                for state, actual_state in per_state.items():
                    predicted = forecast.get("by_state", {}).get(state) if available else None
                    state_eval[state] = {**actual_state, "prediction": predicted,
                                         "error": _error(predicted, actual_state["bounds"])}
                evaluations.append({
                    "operation": operation, "source": source, "variant": variant,
                    "available": available, "reason": None if available else (
                        "campaign_incomplete_or_integrity_failed" if not complete else
                        (forecast or {}).get("reason", "forecast_missing")),
                    "prediction": prediction, "actual_counts": actual_counts,
                    "point_prediction": prediction,
                    "actual_target_success_counts": {"true": actual_counts["success"],
                                                      "false": actual_counts["failure"],
                                                      "none": actual_counts["unknown"]},
                    "observed_empirical_bounds": actual_bounds,
                    "nominal_wilson_envelope": _nominal_envelope(actual_counts),
                    "error": _error(prediction, actual_bounds), "by_state": state_eval,
                    "latency": _latency(actual),
                    "graph_sha256": forecast.get("graph_sha256") if forecast else None,
                })
    database = {}
    for phase in ("db_up", "db_down"):
        database[phase] = {op: {"counts": _counts([row for row in records
                                                   if row.get("phase") == phase and row.get("operation") == op])}
                           for op in operations}
    database["forecast_impact"] = [{
        "operation": item["operation"], "source": item["source"], "variant": item["variant"],
        "structural_graph_available": bool(item["graph_sha256"]),
        "database_down_prediction": forecasts.get(item["source"], {}).get(item["variant"], {})
            .get(item["operation"], {}).get("database_down_prediction"),
        "prognostic_impact": None if item["prediction"] is None else (
            None if forecasts.get(item["source"], {}).get(item["variant"], {})
            .get(item["operation"], {}).get("database_down_prediction") is None else
            item["prediction"] - forecasts[item["source"]][item["variant"]][item["operation"]]["database_down_prediction"]),
        "counted_as_accuracy_benefit": False,
    } for item in evaluations]
    classes = _read(root/"classes-v4.json")
    return {
        "schema_version": "evaluation-v4", "root": str(root.resolve()),
        "system": status.get("system"), "mode": status.get("mode"), "seed": status.get("seed"),
        "status": status, "integrity": integrity, "complete_for_evaluation": complete,
        "counts": {"all_records": len(records), "primary": len(primary), "target": len(target),
                   "expected_primary": EXPECTED_PRIMARY_PER_CELL,
                   "primary_count_matches": len(primary) == EXPECTED_PRIMARY_PER_CELL,
                   "target_state_counts": {state: sum(row.get("state") == state for row in target)
                                           for state in ("11", "10", "01", "00")},
                   "blocks": len(blocks)},
        "evaluations": evaluations, "manual_baselines": _manual_baselines(status.get("system"), operations)
            if status.get("system") else {},
        "database": database, "async": _async_results(root),
        "classes": classes if classes is not None else {"available": False, "reason": "classes-v4.json pending"},
        "cost": _cost(root, status),
        "claim": "external descriptive evaluation only; no accuracy threshold and no success claim",
    }


def _find_campaigns(roots: list[Path]) -> list[Path]:
    found = set()
    for root in roots:
        if (root/"status.json").is_file() and (root/"external.json").is_file():
            found.add(root.resolve())
        for status in root.rglob("status.json"):
            if (status.parent/"external.json").is_file():
                found.add(status.parent.resolve())
    return sorted(found)


def aggregate(roots: list[Path], report_dir: Path) -> dict:
    reports = [evaluate_campaign(path) for path in _find_campaigns(roots)]
    cells = {(r["system"], r["mode"], r["seed"]): r for r in reports}
    expected = {(s, m, z) for s in ("deathstarbench", "otel_demo", "petclinic")
                for m in ("absent", "partial", "full") for z in (6, 7, 8)}
    grouped = {}
    for report in reports:
        for row in report["evaluations"]:
            key = (report["system"], report["mode"], row["operation"], row["source"], row["variant"])
            grouped.setdefault(key, []).append(row)
    summaries = []
    for key, rows in sorted(grouped.items()):
        predictions = [r["prediction"] for r in rows if r["prediction"] is not None]
        errors = [r["error"]["worst_end_error"] for r in rows if r["error"]["worst_end_error"] is not None]
        summaries.append({
            **dict(zip(("system", "mode", "operation", "source", "variant"), key)),
            "repeat_count": len(rows), "available_count": len(predictions), "evaluable_error_count": len(errors),
            "prediction_mean": mean(predictions) if predictions else None,
            "prediction_range": [min(predictions), max(predictions)] if predictions else None,
            "worst_end_error_mean": mean(errors) if errors else None,
            "worst_end_error_range": [min(errors), max(errors)] if errors else None,
            "coverage": {"expected_repeats": 3, "observed": len(rows), "available": len(predictions)},
        })
    result = {
        "schema_version": "evaluation-v4-aggregate", "campaigns": reports,
        "grid": {"expected_cells": 27, "observed_cells": len(cells),
                 "missing_cells": [list(item) for item in sorted(expected-set(cells))],
                 "expected_primary_total": EXPECTED_GRID_TOTAL,
                 "observed_primary_total": sum(r["counts"]["primary"] for r in reports)},
        "per_operation_source_variant_repeats": summaries,
        "overall_accuracy_mean": None,
        "claim": "operations and sources remain separate; no masking overall mean or accuracy threshold",
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir/"evaluation-v4.json").write_text(json.dumps(result, indent=2)+"\n")
    fields = ["system", "mode", "operation", "source", "variant", "repeat_count", "available_count",
              "evaluable_error_count", "prediction_mean", "prediction_range", "worst_end_error_mean",
              "worst_end_error_range"]
    with (report_dir/"evaluation-v4.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        for row in summaries:
            writer.writerow({key: json.dumps(row[key]) if isinstance(row.get(key), list) else row.get(key) for key in fields})
    height = max(80, 24*(len(summaries)+2))
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}">',
             '<style>text{font:12px monospace}.missing{fill:#777}.value{fill:#a33}</style>',
             '<text x="10" y="18">Worst-end absolute error by operation/source/variant/repeat group (no threshold)</text>']
    for index, row in enumerate(summaries, 1):
        value = row["worst_end_error_mean"]
        label = "/".join(str(row[key]) for key in ("system", "mode", "operation", "source", "variant"))
        lines.append(f'<text x="10" y="{24*(index+1)}">{html.escape(label)}</text>')
        if value is None:
            lines.append(f'<text class="missing" x="650" y="{24*(index+1)}">unknown</text>')
        else:
            lines.append(f'<rect class="value" x="650" y="{24*index+10}" width="{500*value:.3f}" height="10"/>')
            lines.append(f'<text x="1160" y="{24*(index+1)}">{value:.4f}</text>')
    lines.append("</svg>")
    (report_dir/"evaluation-v4-errors.svg").write_text("\n".join(lines)+"\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--campaign", type=Path)
    group.add_argument("--aggregate", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args()
    if args.campaign:
        if args.out is None: parser.error("--campaign requires --out")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(evaluate_campaign(args.campaign), indent=2)+"\n")
    else:
        if args.report_dir is None: parser.error("--aggregate requires --report-dir")
        aggregate(args.aggregate, args.report_dir)


if __name__ == "__main__":
    main()
