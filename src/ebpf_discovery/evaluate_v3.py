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
from urllib.parse import urlsplit

from .model import wilson
from .observations import opaque_attempt

SOURCES = ("ebpf", "native", "combined", "entry_http")
SYSTEMS = ("deathstarbench", "otel_demo", "petclinic")
MODES = ("absent", "partial", "full")
SEEDS = (3, 4, 5)
PRIMARY_COUNTS = {"class_train": 600, "calibration": 24000, "target": 9600, "class_test": 600}
OBSERVATION_POLICY = "censored-v3"
HTTP_OBSERVATION_CAP_SECONDS = 10


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


def _complete_sum(values: Iterable[int | float | None]) -> int | float | None:
    values = list(values)
    return sum(values) if all(value is not None for value in values) else None


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


def _validate_observations(external: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    observations = {}
    for row in external:
        key = opaque_attempt(row)
        observation = row.get("observation")
        if not isinstance(observation, dict) or observation.get("policy") != OBSERVATION_POLICY:
            raise ValueError("external attempt is missing the censored-v3 observation policy")
        if observation.get("cap_seconds") != HTTP_OBSERVATION_CAP_SECONDS:
            raise ValueError("external attempt has the wrong HTTP observation cap")
        if type(observation.get("censored")) is not bool:
            raise ValueError("external observation censored must be boolean")
        if observation.get("termination") not in {"complete", "transport_incomplete", "cap_reached"}:
            raise ValueError("external observation has an invalid termination")
        started_ns, cutoff_ns = row.get("started_ns"), observation.get("cutoff_ns")
        if type(started_ns) is not int or type(cutoff_ns) is not int:
            raise ValueError("external observation timestamps must be integers")
        if cutoff_ns != started_ns + HTTP_OBSERVATION_CAP_SECONDS * 1_000_000_000:
            raise ValueError("external observation cutoff does not match the engineering cap")
        if observation["censored"] and row.get("success") is not None:
            raise ValueError("censored external outcomes must remain unknown")
        observations[key] = observation
    return observations


def _validate_http_curves(path: Path, primary: list[dict[str, Any]]) -> dict[str, Any]:
    data = _read(path)
    if (data.get("engineering_observation_cap_seconds") != HTTP_OBSERVATION_CAP_SECONDS
            or data.get("application_slo") is not None
            or data.get("not_business_success_or_database_commit_latency") is not True
            or data.get("shared_journal_for_all_methods") is not True):
        raise ValueError("HTTP observation curves do not preserve their descriptive-only meaning")
    expected = Counter((row["phase"], row["state"], row["operation"]) for row in primary)
    expected_censored = Counter(
        (row["phase"], row["state"], row["operation"])
        for row in primary if row["observation"]["censored"]
    )
    expected_completed = Counter()
    for row in primary:
        receipts = [
            step.get("body_completed_ns", step.get("ended_ns"))
            for step in row.get("http_steps", []) if step.get("status") is not None
        ]
        if not row["observation"]["censored"] and any(value is not None for value in receipts):
            expected_completed[(row["phase"], row["state"], row["operation"])] += 1
    seen = {}
    for curve in data.get("curves", []):
        key = (curve.get("phase"), curve.get("state"), curve.get("operation"))
        if key in seen or key not in expected:
            raise ValueError("HTTP observation curves contain an unexpected or duplicate population")
        if (curve.get("n") != expected[key] or curve.get("censored") != expected_censored[key]
                or curve.get("completed_response_observations") != expected_completed[key]):
            raise ValueError("HTTP observation curve census differs from the external journal")
        points = curve.get("points")
        if not isinstance(points, list) or not points:
            raise ValueError("HTTP observation curve has no points")
        previous_seconds, previous_fraction = -1.0, -1.0
        for point in points:
            seconds, fraction = point.get("seconds"), point.get("fraction")
            if (type(seconds) not in (int, float) or type(fraction) not in (int, float)
                    or not 0 <= seconds <= HTTP_OBSERVATION_CAP_SECONDS
                    or not 0 <= fraction <= 1 or seconds < previous_seconds or fraction < previous_fraction):
                raise ValueError("HTTP observed-response fractions are not monotone and bounded")
            previous_seconds, previous_fraction = seconds, fraction
        if previous_fraction != expected_completed[key] / expected[key]:
            raise ValueError("HTTP observation curve endpoint differs from completed response census")
        seen[key] = curve
    if set(seen) != set(expected):
        raise ValueError("HTTP observation curves do not cover the complete primary journal")
    return {"path": path.name, "sha256": _digest(path), "data": data}


def _campaign_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    common = {
        "system": result["system"], "mode": result["mode"], "seed": result["seed"],
        "run_id": result["run_id"], "protocol_version": result["protocol_version"],
        "observation_policy": result["observation_policy"],
        "http_observation_cap_seconds": result["http_observation_cap_seconds"],
        "application_deadline_seconds": result["application_deadline_seconds"],
    }
    return [{**common, **row} for row in result["metrics"]]


def _completion_interval_evidence(status: dict[str, Any], external: list[dict[str, Any]]) -> dict[str, Any]:
    """Retain independently observed interval endpoints without estimating event times."""
    if status["system"] == "petclinic":
        records = []
        for row in external:
            validation = row.get("validation") or {}
            query_started = validation.get("query_started_ns")
            query_completed = validation.get("query_completed_ns")
            operation_interval = validation.get("operation_completion_interval_ns")
            commit_interval = validation.get("database_commit_time_interval_ns")
            if any(value is not None for value in (
                query_started, query_completed, operation_interval, commit_interval
            )):
                if (type(query_started) is not int or type(query_completed) is not int
                        or query_started > query_completed):
                    raise ValueError("Petclinic SQL verification timing is incomplete or reversed")
                if (operation_interval is None) != (commit_interval is None):
                    raise ValueError("Petclinic SQL completion intervals must be retained together")
                if operation_interval is not None:
                    for name, interval in (
                        ("operation", operation_interval), ("database commit", commit_interval)
                    ):
                        if not isinstance(interval, dict):
                            raise ValueError(f"Petclinic {name} completion interval is missing")
                        lower, upper = interval.get("lower"), interval.get("upper")
                        if type(upper) is not int or (lower is not None and type(lower) is not int):
                            raise ValueError(f"Petclinic {name} completion interval has invalid endpoints")
                        if lower is not None and lower > upper:
                            raise ValueError(f"Petclinic {name} completion interval is reversed")
                    if commit_interval["lower"] is not None or commit_interval["upper"] != query_completed:
                        raise ValueError("Petclinic commit interval must remain left-unknown through SQL completion")
                records.append({
                    "attempt_key": opaque_attempt(row),
                    "query_started_ns": query_started,
                    "query_completed_ns": query_completed,
                    "operation_completion_interval_ns": operation_interval,
                    "database_commit_time_interval_ns": commit_interval,
                })
        return {
            "kind": "independent_sql_postcondition_intervals",
            "query_started_observed": sum(type(row["query_started_ns"]) is int for row in records),
            "query_completed_observed": sum(type(row["query_completed_ns"]) is int for row in records),
            "operation_completion_intervals": sum(
                isinstance(row["operation_completion_interval_ns"], dict) for row in records
            ),
            "database_commit_time_intervals": sum(
                isinstance(row["database_commit_time_interval_ns"], dict) for row in records
            ),
            "records": records,
            "exact_database_commit_time_inferred": False,
        }
    if status["system"] == "otel_demo":
        records = []
        for row in external:
            verification = row.get("async_verification") or {}
            interval = verification.get("completion_time_interval_ns")
            if interval is not None:
                if not isinstance(interval, dict):
                    raise ValueError("OTel async completion interval must be an object")
                lower, upper = interval.get("lower_bound_ns"), interval.get("upper_bound_ns")
                if (lower is not None and type(lower) is not int) or (upper is not None and type(upper) is not int):
                    raise ValueError("OTel async completion interval has invalid endpoints")
                if lower is not None and upper is not None and lower > upper:
                    raise ValueError("OTel async completion interval is reversed")
                records.append({"attempt_key": opaque_attempt(row), "completion_time_interval_ns": interval})
        return {
            "kind": "independent_async_completion_intervals",
            "intervals": len(records), "records": records,
            "exact_completion_time_inferred": False,
        }
    return {"kind": "not_applicable", "records": []}


def _control_evidence(root: Path, status: dict[str, Any], external: list[dict[str, Any]]) -> dict[str, Any]:
    automatic_path = root / "automatic-metrics.json"
    database_controls_path = root / "database-controls.json"
    automatic = _read(automatic_path)
    database_controls = _read(database_controls_path)
    evidence: dict[str, Any] = {
        "automatic": {"sha256": _digest(automatic_path), "metrics": automatic},
        "database_controls": {"sha256": _digest(database_controls_path), "rates": database_controls},
        "completion_interval_evidence": _completion_interval_evidence(status, external),
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
        comparisons = []
        for predictor in ("ebpf", "native", "combined", "static_endpoint_baseline"):
            grouped: dict[tuple[str, str], Counter] = defaultdict(Counter)
            for row in attempts:
                external_row = by_key[row["attempt_key"]]
                value = (row["static_endpoint_baseline"] if predictor == "static_endpoint_baseline"
                         else row["predicted_database_caused_failure"][predictor])
                external_value = external_row.get("success")
                counts = grouped[(external_row["operation"], external_row["phase"])]
                counts[f"predicted_{str(value).lower()}"] += 1
                counts[f"external_{str(external_value).lower()}"] += 1
                if value is True and external_value is True:
                    counts["predicted_failure_but_external_success"] += 1
                if value is True and external_value is False:
                    counts["predicted_failure_supported_by_external_failure"] += 1
            comparisons.extend({"predictor": predictor, "operation": operation, "phase": phase, **dict(counts)}
                               for (operation, phase), counts in sorted(grouped.items()))
        evidence["petclinic_database_prediction"] = {
            "sha256_by_file": {name: _digest(path) for name, path in files.items()},
            "attempts": len(attempts), "comparisons": comparisons,
            "interpretation": "one-sided DB-caused-failure prediction; false never implies business success",
        }
    if status["system"] == "otel_demo":
        chain_path, selection_path = root / "async-chains.json", root / "async-selection.json"
        chains, selection = _read(chain_path), _read(selection_path)
        async_rows = [row for row in external if str(row.get("phase", "")).startswith("async_")]
        if len(async_rows) != 60:
            raise ValueError("OTel async controls must contain 60 attempts")
        phases = {}
        for phase in ("async_normal", "async_paused", "async_recovered"):
            population = [row for row in async_rows if row["phase"] == phase]
            if len(population) != 20:
                raise ValueError(f"OTel {phase} control must contain 20 attempts")
            sources = {}
            for source in ("ebpf", "native"):
                statuses = Counter()
                for row in population:
                    anchors = [step for step in row.get("http_steps", [])
                               if urlsplit(str(step.get("url", ""))).path == "/api/checkout"
                               and step.get("request_id")]
                    proof = (chains.get(anchors[0]["request_id"], {}).get("sources", {}).get(source)
                             if len(anchors) == 1 else None)
                    statuses[(proof or {}).get("status", "unknown")] += 1
                sources[source] = dict(statuses)
            phases[phase] = {
                "attempts": 20, "sources": sources,
                "immediate_outcome": _outcome_rate([{"success": row.get("success")} for row in population]),
                "durable_outcome": _outcome_rate([
                    {"success": (row.get("async_verification") or {}).get("success")} for row in population
                ]),
            }
        evidence["async_association"] = {
            "chains_sha256": _digest(chain_path), "selection_sha256": _digest(selection_path),
            "selection": selection, "attempts": len(async_rows), "phases": phases,
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
    if (status.get("observation_policy") != OBSERVATION_POLICY
            or status.get("http_observation_cap_seconds") != HTTP_OBSERVATION_CAP_SECONDS
            or status.get("application_deadline_seconds", "missing") is not None):
        raise ValueError("campaign does not use the approved censored-v3 observation policy")
    if status.get("status") != "acquisition_complete":
        raise ValueError("campaign acquisition is incomplete")
    saved_path, integrity_path = root / "forecast-saved.json", root / "freeze-integrity.json"
    saved, integrity = _read(saved_path), _read(integrity_path)
    target_starts = [block["load_started_ns"] for block in blocks if block.get("phase") == "target"]
    if not target_starts or saved.get("saved_ns", 0) >= min(target_starts):
        raise ValueError("forecasts were not frozen before target acquisition")
    saved_hashes = saved.get("sha256_by_path")
    integrity_hashes = integrity.get("sha256_by_path")
    if integrity.get("all_unchanged") is not True or not isinstance(saved_hashes, dict) or saved_hashes != integrity_hashes:
        raise ValueError("frozen artifact integrity record is incomplete or inconsistent")
    for relative, expected_hash in saved_hashes.items():
        path = root / relative
        if not path.is_file() or _digest(path) != expected_hash:
            raise ValueError(f"frozen artifact changed: {relative}")
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
    observations_by_key = _validate_observations(external)
    curve_evidence = _validate_http_curves(root / "http-observation-curves.json", primary)
    targets = [row for row in primary if row.get("phase") == "target"]

    operations: tuple[str, ...] | None = None
    source_inputs = {}
    source_projections = {}
    source_primary = {}
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
            observation = observations_by_key[key]
            if (row.get("observation_policy") != observation["policy"]
                    or row.get("observation_censored") is not observation["censored"]):
                raise ValueError(f"{source} projection censoring differs from the external journal")
        source_inputs[source] = {
            "model_sha256": _digest(model_path),
            "forecast_sha256": _digest(forecast_path),
            "projection_sha256": _digest(projection_path),
        }
        source_projections[source] = (
            forecast, {key: row for key, row in projected_by_key.items() if row["phase"] == "target"}
        )
        source_primary[source] = projected_by_key

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
                "nominal_worst_end_error": _worst_end_error(nominal, observed["empirical_bounds"]),
                "nominal_vs_external_wilson_worst_end_error": (
                    _worst_end_error(nominal, observed["nominal_bounds"])
                ),
                "empirical_interval_width": empirical[1] - empirical[0],
                "nominal_interval_width": nominal[1] - nominal[0],
                "historical_reference_width_10pp": prediction.get("historical_reference_width_10pp"),
                "accuracy_gate_applied": False,
            })

    confusion = []
    label = {True: "true", False: "false", None: "unknown"}
    for source in SOURCES:
        for operation in operations or ():
            for phase in ("calibration", "target"):
                external_rows = [row for row in primary if row["phase"] == phase and row["operation"] == operation]
                categories: dict[str, list[str]] = defaultdict(list)
                for external_row in external_rows:
                    attempt_key = opaque_attempt(external_row)
                    proxy = source_primary[source][attempt_key].get("proxy")
                    outcome = external_row.get("success")
                    if proxy not in label or outcome not in label:
                        raise ValueError("confusion inputs must be true, false, or null")
                    categories[f"source_{label[proxy]}_external_{label[outcome]}"].append(attempt_key)
                confusion.append({
                    "source": source, "operation": operation, "phase": phase, "n": len(external_rows),
                    "counts": {category: len(ids) for category, ids in sorted(categories.items())},
                    "witness_attempt_ids": {
                        category: sorted(ids)[:10] for category, ids in sorted(categories.items())
                    },
                    "witness_limit_per_category": 10,
                })

    traffic_blocks = [{
        "id": block.get("id"), "phase": block.get("phase"), "state": block.get("state"),
        "attempts": block.get("attempts"),
        "requested_operations_per_second": block.get("requested_operations_per_second"),
        "achieved_operations_per_second": block.get("achieved_operations_per_second"),
        "worker_capacity": block.get("worker_capacity"),
        "peak_in_flight_attempts": block.get("peak_in_flight_attempts"),
        "nominal_load_seconds": block.get("nominal_load_seconds"),
        "load_started_ns": block.get("load_started_ns"), "ended_ns": block.get("ended_ns"),
    } for block in blocks]
    result = {
        "schema_version": 3,
        "system": status["system"], "mode": status["mode"], "seed": status["seed"],
        "run_id": status.get("run_id"), "protocol_version": status["protocol_version"],
        "observation_policy": status["observation_policy"],
        "http_observation_cap_seconds": status["http_observation_cap_seconds"],
        "application_deadline_seconds": status["application_deadline_seconds"],
        "acquisition_commit": status.get("commit"),
        "status_sha256": _digest(status_path),
        "external_sha256": _digest(external_path),
        "source_inputs": source_inputs,
        "http_observation_curves": curve_evidence,
        "freeze": {
            "forecast_saved_sha256": _digest(saved_path),
            "freeze_integrity_sha256": _digest(integrity_path),
            "saved_ns": saved["saved_ns"], "target_started_ns": min(target_starts),
            "verified_paths": len(saved_hashes),
        },
        "primary_population": {
            **{phase: phase_counts[phase] for phase in PRIMARY_COUNTS}, "total": expected_primary,
        },
        "metrics": metrics,
        "confusion": confusion,
        "controls": _control_evidence(root, status, external),
        "costs": {
            "campaign_elapsed_seconds": status.get("elapsed_seconds"),
            "fit_and_discovery_seconds": saved.get("fit_and_discovery_seconds"),
            "attempted_operations": status.get("attempted_operations"),
            "preparation_operations": status.get("preparation_operations"),
            "http_observation_cap_seconds": status["http_observation_cap_seconds"],
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
        ("The 10-second value is an engineering whole-response observation cap, not an application SLO. "
         "The cumulative observed-response fractions include incorrect terminal responses and retain every attempt "
         "in the denominator; they are neither an uncensored distribution nor a Kaplan–Meier estimate, "
         "and exclude SQL/async completion time."), "",
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
    for root, result in zip(campaign_paths, evaluations, strict=True):
        if (result.get("observation_policy") != OBSERVATION_POLICY
                or result.get("http_observation_cap_seconds") != HTTP_OBSERVATION_CAP_SECONDS
                or result.get("application_deadline_seconds", "missing") is not None):
            raise ValueError("aggregate contains an ineligible observation policy")
        reference = result.get("http_observation_curves") or {}
        curve_path = root / str(reference.get("path", ""))
        if (not curve_path.is_file() or reference.get("sha256") != _digest(curve_path)
                or reference.get("data") != _read(curve_path)):
            raise ValueError("aggregate HTTP observation curve reference is incomplete or changed")
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
    database_groups: dict[tuple[str, str, str, str], Counter] = defaultdict(Counter)
    async_groups: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    confusion_groups: dict[tuple[str, str, str, str, str], Counter] = defaultdict(Counter)
    for result in evaluations:
        automatic = result["controls"]["automatic"]["metrics"]
        for source, variants in automatic.items():
            for variant, phases in variants.items():
                for phase, metrics in phases.items():
                    automatic_groups[(result["system"], result["mode"], source, variant, phase)].append(metrics)
        petclinic_db = result["controls"].get("petclinic_database_prediction", {}).get("comparisons", [])
        for row in petclinic_db:
            counts = {key: value for key, value in row.items()
                      if key not in {"predictor", "operation", "phase"}}
            database_groups[(result["mode"], row["predictor"], row["operation"], row["phase"])].update(counts)
        async_data = result["controls"].get("async_association", {}).get("phases", {})
        for phase, phase_data in async_data.items():
            for source, counts in phase_data["sources"].items():
                key = (result["mode"], source, phase)
                async_groups[key].update(counts)
                for outcome_name in ("immediate_outcome", "durable_outcome"):
                    outcome = phase_data[outcome_name]
                    async_groups[key].update({f"{outcome_name}_{name}": outcome[name]
                                              for name in ("successes", "failures", "unknown")})
        for row in result["confusion"]:
            key = (result["system"], result["mode"], row["operation"], row["source"], row["phase"])
            confusion_groups[key].update(row["counts"])
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
        {"mode": mode, "predictor": predictor, "operation": operation, "phase": phase, **dict(counts)}
        for (mode, predictor, operation, phase), counts in sorted(database_groups.items())
    ]
    async_summaries = [
        {"mode": mode, "source": source, "phase": phase, **dict(counts)}
        for (mode, source, phase), counts in sorted(async_groups.items())
    ]
    confusion_summaries = [
        {"system": system, "mode": mode, "operation": operation, "source": source,
         "phase": phase, "counts": dict(counts)}
        for (system, mode, operation, source, phase), counts in sorted(confusion_groups.items())
    ]

    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    json_path, csv_path, markdown_path = out / "results.json", out / "metrics.csv", out / "report.md"
    result = {
        "schema_version": 3,
        "protocol_version": "source-contract-v3",
        "observation_policy": OBSERVATION_POLICY,
        "http_observation_cap_seconds": HTTP_OBSERVATION_CAP_SECONDS,
        "application_deadline_seconds": None,
        "campaigns": len(evaluations),
        "costs": {
            "campaign_elapsed_seconds": _complete_sum(
                result["costs"]["campaign_elapsed_seconds"] for result in evaluations
            ),
            "model_preparation_seconds": {
                source: _complete_sum(
                    result["costs"]["model_preparation_seconds"][source]
                    for result in evaluations
                )
                for source in SOURCES
            },
            "fit_and_discovery_seconds": _complete_sum(
                result["costs"]["fit_and_discovery_seconds"] for result in evaluations
            ),
            "attempted_operations": _complete_sum(
                result["costs"]["attempted_operations"] for result in evaluations
            ),
            "preparation_operations": _complete_sum(
                result["costs"]["preparation_operations"] for result in evaluations
            ),
            "primary_attempts": sum(result["primary_population"]["total"] for result in evaluations),
            "all_recorded_block_attempts": _complete_sum(
                block["attempts"]
                for result in evaluations for block in result["costs"]["traffic_blocks"]
            ),
            "traffic_blocks": sum(len(result["costs"]["traffic_blocks"]) for result in evaluations),
            "http_observation_cap_seconds": HTTP_OBSERVATION_CAP_SECONDS,
            "maximum_peak_in_flight_attempts": (
                max(
                    block["peak_in_flight_attempts"]
                    for result in evaluations for block in result["costs"]["traffic_blocks"]
                ) if all(
                    block["peak_in_flight_attempts"] is not None
                    for result in evaluations for block in result["costs"]["traffic_blocks"]
                ) else None
            ),
            "human_agent_seconds": None,
        },
        "summaries": summaries,
        "automatic_grouping": automatic_summaries,
        "petclinic_database_prediction": database_summaries,
        "otel_async_association": async_summaries,
        "per_attempt_confusion": confusion_summaries,
        "http_observation_curves": [{
            "system": result["system"], "mode": result["mode"], "seed": result["seed"],
            **result["http_observation_curves"],
        } for result in evaluations],
        "control_references": [{
            "system": result["system"], "mode": result["mode"], "seed": result["seed"],
            "controls": result["controls"],
        } for result in evaluations],
        "campaign_references": [{
            "system": result["system"], "mode": result["mode"], "seed": result["seed"],
            "run_id": result["run_id"], "status_sha256": result["status_sha256"],
            "http_observation_curves_sha256": result["http_observation_curves"]["sha256"],
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
        ("The shared 10-second client observation cap is not an application deadline. HTTP receipt curves include "
         "incorrect terminal responses; independent SQL and async completion intervals remain separate controls."), "",
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
              "| Mode | Predictor | Operation | Phase | Predicted true | Predicted false | Predicted unknown | Supported | Contradicted |",
              "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in database_summaries:
        lines.append(
            f"| {row['mode']} | {row['predictor']} | {row['operation']} | {row['phase']} | "
            f"{row.get('predicted_true', 0)} | "
            f"{row.get('predicted_false', 0)} | {row.get('predicted_none', 0)} | "
            f"{row.get('predicted_failure_supported_by_external_failure', 0)} | "
            f"{row.get('predicted_failure_but_external_success', 0)} |"
        )
    lines += ["", "### OTel asynchronous association", "",
              "| Mode | Source | Phase | Linked | Unknown | Immediate T/F/U | Durable T/F/U |",
              "| --- | --- | --- | ---: | ---: | --- | --- |"]
    for row in async_summaries:
        immediate = "/".join(str(row.get(f"immediate_outcome_{key}", 0))
                             for key in ("successes", "failures", "unknown"))
        durable = "/".join(str(row.get(f"durable_outcome_{key}", 0))
                           for key in ("successes", "failures", "unknown"))
        lines.append(f"| {row['mode']} | {row['source']} | {row['phase']} | {row.get('linked', 0)} | "
                     f"{row.get('unknown', 0)} | {immediate} | {durable} |")
    lines += ["", "### Per-attempt semantic confusion", "",
              ("Full calibration/target confusion counts and bounded witness attempt IDs are retained in `results.json`. "
               "False positives, false negatives, and source/external unknowns are not absorbed into interval averages.")]
    elapsed = result["costs"]["campaign_elapsed_seconds"]
    elapsed_text = "unknown" if elapsed is None else f"{elapsed:.1f} seconds"
    lines += ["", (f"Recorded campaign elapsed time: {elapsed_text}. "
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
