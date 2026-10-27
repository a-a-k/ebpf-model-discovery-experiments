"""Independent evaluation and aggregation for source-contract-v3 campaigns."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from statistics import mean
from typing import Any

from .model import wilson
from .observations import opaque_attempt

SOURCES = ("ebpf", "native", "combined", "entry_http")
SYSTEMS = ("deathstarbench", "otel_demo", "petclinic")
MODES = ("absent", "partial", "full")
SEEDS = (3, 4, 5)
PRIMARY_COUNTS = {"class_train": 600, "calibration": 24000, "target": 9600, "class_test": 600}


def _require_actions() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Research result processing runs in GitHub Actions only")


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (list, dict)) else value
                             for key, value in row.items()})


def _outcome_rate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = [row.get("success") for row in rows]
    if any(value not in (True, False, None) for value in values):
        raise ValueError("external success must be true, false, or null")
    counts = Counter(values)
    n = len(values)
    empirical = [counts[True] / n, (counts[True] + counts[None]) / n] if n else [0.0, 1.0]
    nominal = [wilson(counts[True], n)[0], wilson(counts[True] + counts[None], n)[1]]
    return {
        "n": n,
        "successes": counts[True],
        "failures": counts[False],
        "unknown": counts[None],
        "point": counts[True] / n if n and not counts[None] else None,
        "empirical_bounds": empirical,
        "nominal_bounds": nominal,
        "nominal_method": "pointwise 95% iid Bernoulli Wilson envelope; temporal independence unvalidated",
    }


def _validate_bounds(value: Any, label: str) -> list[float]:
    if (not isinstance(value, list) or len(value) != 2
            or any(type(item) not in (int, float) for item in value)):
        raise ValueError(f"{label} must contain two numeric endpoints")
    bounds = [float(value[0]), float(value[1])]
    if not 0 <= bounds[0] <= bounds[1] <= 1:
        raise ValueError(f"invalid {label}")
    return bounds


def _worst_end_error(predicted: list[float], observed: list[float]) -> float:
    return max(abs(predicted[0] - observed[1]), abs(predicted[1] - observed[0]))


def _projection_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    proxy = Counter(row.get("proxy") for row in rows)
    protocol = Counter(row.get("protocol_only") for row in rows)
    if any(value not in (True, False, None) for value in proxy + protocol):
        raise ValueError("projection verdicts must be true, false, or null")
    return {
        "n": len(rows),
        "business_true": proxy[True],
        "business_false": proxy[False],
        "business_unknown": proxy[None],
        "protocol_true": protocol[True],
        "protocol_false": protocol[False],
        "protocol_unknown": protocol[None],
    }


def _campaign_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    common = {
        "system": result["system"], "mode": result["mode"], "seed": result["seed"],
        "run_id": result["run_id"], "protocol_version": result["protocol_version"],
    }
    return [{**common, **row} for row in result["metrics"]]


def _control_evidence(root: Path, status: dict[str, Any], external: list[dict[str, Any]]) -> dict[str, Any]:
    automatic_path = root / "automatic-metrics.json"
    database_controls_path = root / "database-controls.json"
    automatic = _read(automatic_path)
    database_controls = _read(database_controls_path)
    evidence: dict[str, Any] = {
        "automatic": {"sha256": _digest(automatic_path), "metrics": automatic},
        "database_controls": {"sha256": _digest(database_controls_path), "rates": database_controls},
    }
    database_rows = [row for row in external if row.get("phase") in {"db_up", "db_down"}]
    if Counter(row["phase"] for row in database_rows) != {"db_up": 20, "db_down": 20}:
        raise ValueError("database controls must contain 20 DB-up and 20 DB-down attempts")
    if status["system"] == "petclinic":
        files = {
            name: root / "database" / name
            for name in ("model.json", "predictions.json", "attempt-predictions.json")
        }
        attempts = _read(files["attempt-predictions.json"])
        by_key = {opaque_attempt(row): row for row in database_rows}
        if len(attempts) != 40 or {row["attempt_key"] for row in attempts} != set(by_key):
            raise ValueError("Petclinic database predictions do not match the control population")
        summaries = {}
        for source in ("ebpf", "native", "combined"):
            counts = Counter()
            for row in attempts:
                value = row["predicted_database_caused_failure"][source]
                external_value = by_key[row["attempt_key"]].get("success")
                counts[f"predicted_{str(value).lower()}"] += 1
                counts[f"external_{str(external_value).lower()}"] += 1
                if value is True and external_value is True:
                    counts["predicted_failure_but_external_success"] += 1
            summaries[source] = dict(counts)
        evidence["petclinic_database_prediction"] = {
            "sha256_by_file": {name: _digest(path) for name, path in files.items()},
            "attempts": len(attempts), "sources": summaries,
            "interpretation": "one-sided DB-caused-failure prediction; false never implies business success",
        }
    if status["system"] == "otel_demo":
        chain_path, selection_path = root / "async-chains.json", root / "async-selection.json"
        chains, selection = _read(chain_path), _read(selection_path)
        async_rows = [row for row in external if str(row.get("phase", "")).startswith("async_")]
        if len(async_rows) != 60:
            raise ValueError("OTel async controls must contain 60 attempts")
        summaries = {}
        for source in ("ebpf", "native"):
            statuses = Counter()
            for row in async_rows:
                request_id = row["http_steps"][-1]["request_id"]
                proof = chains.get(request_id, {}).get("sources", {}).get(source)
                statuses[(proof or {}).get("status", "unknown")] += 1
            summaries[source] = dict(statuses)
        durable = _outcome_rate([
            {"success": (row.get("async_verification") or {}).get("success")} for row in async_rows
        ])
        evidence["async_association"] = {
            "chains_sha256": _digest(chain_path), "selection_sha256": _digest(selection_path),
            "selection": selection, "attempts": len(async_rows), "sources": summaries,
            "external_durable_outcome": durable,
            "association_is_not_durability": True,
        }
    return evidence


def evaluate(campaign_dir: str | Path) -> dict[str, Any]:
    """Score one completed campaign against independent target business outcomes."""
    _require_actions()
    root = Path(campaign_dir)
    status_path = root / "status.json"
    external_path, blocks_path = root / "external.json", root / "blocks.json"
    status = _read(status_path)
    external, blocks = _read(external_path), _read(blocks_path)
    if status.get("protocol_version") != "source-contract-v3":
        raise ValueError("campaign is not source-contract-v3")
    if status.get("status") != "acquisition_complete":
        raise ValueError("campaign acquisition is incomplete")
    phase_counts = Counter(row.get("phase") for row in external)
    if any(phase_counts[phase] != expected for phase, expected in PRIMARY_COUNTS.items()):
        raise ValueError(f"primary population mismatch: {dict(phase_counts)}")
    expected_primary = sum(PRIMARY_COUNTS.values())
    if sum(phase_counts[phase] for phase in PRIMARY_COUNTS) != expected_primary:
        raise ValueError(f"primary population must contain exactly {expected_primary:,} attempts")

    primary = [row for row in external if row.get("phase") in PRIMARY_COUNTS]
    primary_by_key = {opaque_attempt(row): row for row in primary}
    if len(primary_by_key) != len(primary):
        raise ValueError("duplicate primary attempt identity")
    all_by_key = {opaque_attempt(row): row for row in external}
    if len(all_by_key) != len(external):
        raise ValueError("duplicate campaign attempt identity")
    targets = [row for row in primary if row.get("phase") == "target"]

    operations: tuple[str, ...] | None = None
    source_inputs = {}
    source_projections = {}
    for source in SOURCES:
        model_path = root / "models" / source / "model.json"
        forecast_path = root / "models" / source / "forecast.json"
        projection_path = root / "projections" / f"{source}-final.json"
        model, forecast, projected = _read(model_path), _read(forecast_path), _read(projection_path)
        source_operations = tuple(sorted(forecast["classes"]))
        if set(model["classes"]) != set(source_operations):
            raise ValueError(f"model/forecast operation mismatch for {source}")
        if operations is None:
            operations = source_operations
        elif source_operations != operations:
            raise ValueError("sources do not forecast the same operations")
        if any(row.get("oracle_fields_consumed") is not False for row in projected):
            raise ValueError(f"{source} projection did not preserve the no-oracle boundary")
        all_projected_by_key = {row["attempt_key"]: row for row in projected}
        if len(all_projected_by_key) != len(projected) or set(all_projected_by_key) != set(all_by_key):
            raise ValueError(f"{source} projection attempt identities differ from the external population")
        primary_projected = [row for row in projected if row.get("phase") in PRIMARY_COUNTS]
        projection_phases = Counter(row.get("phase") for row in primary_projected)
        if len(primary_projected) != len(primary) or any(
            projection_phases[phase] != expected for phase, expected in PRIMARY_COUNTS.items()
        ):
            raise ValueError(f"{source} projection is not the complete primary population")
        projected_by_key = {row["attempt_key"]: row for row in primary_projected}
        if len(projected_by_key) != len(primary_projected) or set(projected_by_key) != set(primary_by_key):
            raise ValueError(f"{source} projection attempt identities differ from external primary population")
        for key, row in all_projected_by_key.items():
            external_row = all_by_key[key]
            if row.get("operation_id") != external_row.get("operation"):
                raise ValueError(f"{source} projection operation declaration mismatch")
            if row.get("phase") != external_row.get("phase") or row.get("state") != external_row.get("state"):
                raise ValueError(f"{source} projection phase/state mismatch")
        source_inputs[source] = {
            "model_sha256": _digest(model_path),
            "forecast_sha256": _digest(forecast_path),
            "projection_sha256": _digest(projection_path),
        }
        source_projections[source] = (
            forecast, {key: row for key, row in projected_by_key.items() if row["phase"] == "target"}
        )

    metrics = []
    for operation in operations or ():
        operation_targets = [row for row in targets if row["operation"] == operation]
        observed = _outcome_rate(operation_targets)
        attempt_keys = {opaque_attempt(row) for row in operation_targets}
        for source in SOURCES:
            forecast, projected = source_projections[source]
            prediction = forecast["classes"][operation]
            empirical = _validate_bounds(prediction["identification_bounds"], "identification_bounds")
            nominal = _validate_bounds(prediction["uncertainty_bounds"], "uncertainty_bounds")
            point = prediction.get("point")
            if point is not None and (type(point) not in (int, float) or not 0 <= point <= 1):
                raise ValueError("forecast point must be null or a probability")
            projections = [projected[key] for key in attempt_keys]
            census = _projection_counts(projections)
            metrics.append({
                "source": source,
                "operation": operation,
                "external": observed,
                "projection": census,
                "forecast_point": point,
                "forecast_empirical_bounds": empirical,
                "forecast_nominal_bounds": nominal,
                "point_absolute_error": (
                    abs(float(point) - observed["point"])
                    if point is not None and observed["point"] is not None else None
                ),
                "empirical_worst_end_error": _worst_end_error(empirical, observed["empirical_bounds"]),
                "nominal_worst_end_error": _worst_end_error(nominal, observed["nominal_bounds"]),
                "empirical_interval_width": empirical[1] - empirical[0],
                "nominal_interval_width": nominal[1] - nominal[0],
                "historical_reference_width_10pp": prediction.get("historical_reference_width_10pp"),
                "accuracy_gate_applied": False,
            })

    traffic_blocks = [{
        "id": block.get("id"), "phase": block.get("phase"), "state": block.get("state"),
        "attempts": block.get("attempts"),
        "requested_operations_per_second": block.get("requested_operations_per_second"),
        "achieved_operations_per_second": block.get("achieved_operations_per_second"),
        "worker_capacity": block.get("worker_capacity"),
        "nominal_load_seconds": block.get("nominal_load_seconds"),
        "load_started_ns": block.get("load_started_ns"), "ended_ns": block.get("ended_ns"),
    } for block in blocks]
    result = {
        "schema_version": 3,
        "system": status["system"], "mode": status["mode"], "seed": status["seed"],
        "run_id": status.get("run_id"), "protocol_version": status["protocol_version"],
        "acquisition_commit": status.get("commit"),
        "status_sha256": _digest(status_path),
        "external_sha256": _digest(external_path),
        "source_inputs": source_inputs,
        "primary_population": {
            **{phase: phase_counts[phase] for phase in PRIMARY_COUNTS}, "total": expected_primary,
        },
        "metrics": metrics,
        "controls": _control_evidence(root, status, external),
        "costs": {
            "campaign_elapsed_seconds": status.get("elapsed_seconds"),
            "model_preparation_seconds": {
                source: _read(root / "models" / source / "model.json").get("preparation_seconds")
                for source in SOURCES
            },
            "traffic_blocks": traffic_blocks,
            "human_agent_seconds": None,
        },
        "accuracy_success_gate": None,
    }
    json_path, csv_path, markdown_path = (
        root / "metrics-v3.json", root / "metrics-v3.csv", root / "metrics-v3.md"
    )
    _write(json_path, result)
    _csv(csv_path, _campaign_rows(result))
    lines = [
        "# Source-contract-v3 campaign evaluation", "",
        f"System: `{result['system']}`; mode: `{result['mode']}`; seed: `{result['seed']}`.", "",
        "No 5 pp accuracy or 10 pp width gate is applied. Unknown outcomes and forecasts remain unknown.", "",
        "| Source | Operation | External unknown | Source unknown | Point abs. error (pp) | Empirical worst-end (pp) | Nominal worst-end (pp) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    fmt = lambda value: "unknown" if value is None else f"{100 * value:.2f}"
    for row in metrics:
        lines.append(
            f"| {row['source']} | {row['operation']} | {row['external']['unknown']} | "
            f"{row['projection']['business_unknown']} | {fmt(row['point_absolute_error'])} | "
            f"{fmt(row['empirical_worst_end_error'])} | {fmt(row['nominal_worst_end_error'])} |"
        )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result["outputs"] = {"json": str(json_path), "csv": str(csv_path), "markdown": str(markdown_path)}
    return result


def _known_mean(rows: list[dict[str, Any]], field: str) -> tuple[float | None, int]:
    values = [row[field] for row in rows]
    known = [value for value in values if value is not None]
    return (mean(known) if len(known) == len(values) else None, len(known))


def aggregate(paths: Iterable[str | Path], output: str | Path) -> dict[str, str]:
    """Create the complete 27-campaign, three-seed v3 report artifacts."""
    _require_actions()
    campaign_paths = [Path(path) for path in paths]
    if len(campaign_paths) != 27:
        raise ValueError("aggregate requires exactly 27 campaigns")
    evaluations = []
    for root in campaign_paths:
        path = root / "metrics-v3.json"
        evaluations.append(_read(path) if path.exists() else evaluate(root))
    population = {(row["system"], row["mode"], int(row["seed"])) for row in evaluations}
    expected = {(system, mode, seed) for system in SYSTEMS for mode in MODES for seed in SEEDS}
    if population != expected:
        raise ValueError("aggregate population must be systems x modes x seeds 3/4/5")

    seed_rows = [row for result in evaluations for row in _campaign_rows(result)]
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in seed_rows:
        grouped[(row["system"], row["mode"], row["operation"], row["source"])].append(row)
    summaries = []
    for key, rows in sorted(grouped.items()):
        rows.sort(key=lambda row: int(row["seed"]))
        if [int(row["seed"]) for row in rows] != list(SEEDS):
            raise ValueError(f"incomplete seed population for {key}")
        point, point_known = _known_mean(rows, "point_absolute_error")
        empirical, empirical_known = _known_mean(rows, "empirical_worst_end_error")
        nominal, nominal_known = _known_mean(rows, "nominal_worst_end_error")
        summaries.append({
            "system": key[0], "mode": key[1], "operation": key[2], "source": key[3],
            "seeds": list(SEEDS),
            "mean_point_absolute_error": point, "point_error_known_seeds": point_known,
            "mean_empirical_worst_end_error": empirical, "empirical_error_known_seeds": empirical_known,
            "mean_nominal_worst_end_error": nominal, "nominal_error_known_seeds": nominal_known,
            "external_attempts": sum(row["external"]["n"] for row in rows),
            "external_unknown": sum(row["external"]["unknown"] for row in rows),
            "source_business_unknown": sum(row["projection"]["business_unknown"] for row in rows),
            "seed_metrics": rows,
            "accuracy_gate_applied": False,
        })

    automatic_groups: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    database_groups: dict[tuple[str, str], Counter] = defaultdict(Counter)
    async_groups: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for result in evaluations:
        automatic = result["controls"]["automatic"]["metrics"]
        for source, variants in automatic.items():
            for variant, phases in variants.items():
                for phase, metrics in phases.items():
                    automatic_groups[(result["system"], result["mode"], source, variant, phase)].append(metrics)
        petclinic_db = result["controls"].get("petclinic_database_prediction", {}).get("sources", {})
        for source, counts in petclinic_db.items():
            database_groups[(result["mode"], source)].update(counts)
        async_data = result["controls"].get("async_association", {}).get("sources", {})
        for source, counts in async_data.items():
            async_groups[(result["mode"], source)].update(counts)
    automatic_summaries = []
    for key, rows in sorted(automatic_groups.items()):
        ari_values = [row.get("ari_on_covered") for row in rows]
        automatic_summaries.append({
            "system": key[0], "mode": key[1], "source": key[2], "variant": key[3], "phase": key[4],
            "total": sum(row["total"] for row in rows), "covered": sum(row["covered"] for row in rows),
            "mean_unknown_fraction": mean(row["unknown_fraction"] for row in rows),
            "mean_ari_on_covered": (
                mean(ari_values) if ari_values and all(value is not None for value in ari_values) else None
            ),
            "seeds": len(rows),
        })
    database_summaries = [
        {"mode": mode, "source": source, **dict(counts)}
        for (mode, source), counts in sorted(database_groups.items())
    ]
    async_summaries = [
        {"mode": mode, "source": source, **dict(counts)}
        for (mode, source), counts in sorted(async_groups.items())
    ]

    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    json_path, csv_path, markdown_path = out / "results.json", out / "metrics.csv", out / "report.md"
    result = {
        "schema_version": 3,
        "protocol_version": "source-contract-v3",
        "campaigns": len(evaluations),
        "costs": {
            "campaign_elapsed_seconds": sum(
                result["costs"]["campaign_elapsed_seconds"] or 0 for result in evaluations
            ),
            "model_preparation_seconds": {
                source: sum(
                    result["costs"]["model_preparation_seconds"][source] or 0
                    for result in evaluations
                )
                for source in SOURCES
            },
            "primary_attempts": sum(result["primary_population"]["total"] for result in evaluations),
            "all_recorded_block_attempts": sum(
                block["attempts"] or 0
                for result in evaluations for block in result["costs"]["traffic_blocks"]
            ),
            "traffic_blocks": sum(len(result["costs"]["traffic_blocks"]) for result in evaluations),
            "human_agent_seconds": None,
        },
        "summaries": summaries,
        "automatic_grouping": automatic_summaries,
        "petclinic_database_prediction": database_summaries,
        "otel_async_association": async_summaries,
        "control_references": [{
            "system": result["system"], "mode": result["mode"], "seed": result["seed"],
            "controls": result["controls"],
        } for result in evaluations],
        "campaign_references": [{
            "system": result["system"], "mode": result["mode"], "seed": result["seed"],
            "run_id": result["run_id"], "status_sha256": result["status_sha256"],
            "evaluation": str(campaign_paths[index] / "metrics-v3.json"),
        } for index, result in enumerate(evaluations)],
        "accuracy_success_gate": None,
    }
    _write(json_path, result)
    _csv(csv_path, seed_rows)
    fmt = lambda value: "unknown" if value is None else f"{100 * value:.2f}"
    lines = [
        "# Source-contract-v3 results", "",
        "All 27 campaigns and seeds 3/4/5 are included. No 5 pp accuracy or 10 pp width gate is applied.",
        "Unknown seed-level point errors remain unknown in the aggregate rather than being averaged away.", "",
        "| System | Mode | Operation | Source | Point abs. error (pp) | Empirical worst-end (pp) | Nominal worst-end (pp) | External unknown | Source unknown |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(
            f"| {row['system']} | {row['mode']} | {row['operation']} | {row['source']} | "
            f"{fmt(row['mean_point_absolute_error'])} | {fmt(row['mean_empirical_worst_end_error'])} | "
            f"{fmt(row['mean_nominal_worst_end_error'])} | {row['external_unknown']} | "
            f"{row['source_business_unknown']} |"
        )
    lines += ["", "## Separate controls", "",
              ("Automatic grouping, shared-database intervention, and asynchronous association remain separate controls. "
               "Their per-campaign counts and input hashes are retained in `results.json`; association is not durability, "
               "and absence of a predicted DB cause is not a prediction of business success.")]
    lines += ["", "### Automatic grouping", "",
              "| System | Mode | Source | Variant | Phase | Covered / total | Mean unknown | Mean ARI on covered |",
              "| --- | --- | --- | --- | --- | ---: | ---: | ---: |"]
    for row in automatic_summaries:
        ari = "unknown" if row["mean_ari_on_covered"] is None else f"{row['mean_ari_on_covered']:.3f}"
        lines.append(
            f"| {row['system']} | {row['mode']} | {row['source']} | {row['variant']} | {row['phase']} | "
            f"{row['covered']} / {row['total']} | {row['mean_unknown_fraction']:.3f} | {ari} |"
        )
    lines += ["", "### Petclinic selected-database prediction", "",
              "| Mode | Source | Predicted true | Predicted false | Predicted unknown | Prediction contradicted by external success |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in database_summaries:
        lines.append(
            f"| {row['mode']} | {row['source']} | {row.get('predicted_true', 0)} | "
            f"{row.get('predicted_false', 0)} | {row.get('predicted_none', 0)} | "
            f"{row.get('predicted_failure_but_external_success', 0)} |"
        )
    lines += ["", "### OTel asynchronous association", "",
              "| Mode | Source | Linked | Unknown |",
              "| --- | --- | ---: | ---: |"]
    for row in async_summaries:
        lines.append(f"| {row['mode']} | {row['source']} | {row.get('linked', 0)} | {row.get('unknown', 0)} |")
    lines += ["", (f"Recorded campaign elapsed time: {result['costs']['campaign_elapsed_seconds']:.1f} seconds. "
                   "Human/agent time is unmetered and remains unknown.")]
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(markdown_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="evaluate one campaign directory")
    parser.add_argument("--inputs", type=Path, help="directory containing compact campaign artifacts")
    parser.add_argument("--report", type=Path, help="aggregate output directory")
    args = parser.parse_args()
    if args.out and not args.inputs and not args.report:
        print(json.dumps(evaluate(args.out)["outputs"], sort_keys=True))
        return
    if args.inputs and args.report and not args.out:
        campaigns = sorted({path.parent for path in args.inputs.rglob("metrics-v3.json")})
        print(json.dumps(aggregate(campaigns, args.report), sort_keys=True))
        return
    parser.error("use either --out CAMPAIGN or --inputs ROOT --report DIRECTORY")


if __name__ == "__main__":
    main()
