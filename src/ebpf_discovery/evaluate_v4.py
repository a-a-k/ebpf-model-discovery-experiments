"""External evaluation of graph-driven v4 forecasts without outcome leakage."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import html
import importlib
import json
import math
import os
from pathlib import Path
from statistics import mean


PRIMARY_PHASES = {"class_train", "calibration", "target", "class_test"}
EXPECTED_PRIMARY_PER_CELL = 34_800
EXPECTED_GRID_TOTAL = 939_600
EXPECTED_PHASE_COUNTS = {"class_train": 600, "calibration": 24_000,
                         "target": 9_600, "class_test": 600}
EXPECTED_TARGET_STATES = {"11": 4_800, "10": 2_400, "01": 1_200, "00": 1_200}
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
    counts = {
        "success": sum(row.get("success") is True for row in records),
        "failure": sum(row.get("success") is False for row in records),
        "unknown": sum(row.get("success") is None for row in records),
        "total": len(records),
    }
    counts["invalid"] = counts["total"] - counts["success"] - counts["failure"] - counts["unknown"]
    return counts


def _bounds(counts: dict) -> list[float] | None:
    if not counts["total"] or counts.get("invalid"):
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
    if counts.get("invalid"):
        return {"interval": None, "label": "unknown: invalid external success value",
                "assumption": "not evaluated"}
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


def _completeness(records: list[dict], plans: list[dict], census: list[dict], *,
                  expected_phases=None, expected_states=None) -> dict:
    """Validate the fixed primary acquisition and its three durable identity views."""
    expected_phases = EXPECTED_PHASE_COUNTS if expected_phases is None else expected_phases
    expected_states = EXPECTED_TARGET_STATES if expected_states is None else expected_states
    primary = [row for row in records if row.get("phase") in PRIMARY_PHASES]
    primary_plans = [row for row in plans if row.get("phase") in PRIMARY_PHASES]
    primary_census = [row for row in census if row.get("phase") in PRIMARY_PHASES]
    phase_counts = {phase: sum(row.get("phase") == phase for row in primary)
                    for phase in expected_phases}
    target = [row for row in primary if row.get("phase") == "target"]
    state_counts = {state: sum(row.get("state") == state for row in target)
                    for state in expected_states}
    problems = []
    if phase_counts != expected_phases:
        problems.append("primary_phase_counts_mismatch")
    if state_counts != expected_states:
        problems.append("target_state_counts_mismatch")

    record_ids = [row.get("attempt_id") for row in primary]
    plan_ids = [row.get("attempt_id") for row in primary_plans]
    if any(not value for value in record_ids) or len(set(record_ids)) != len(record_ids):
        problems.append("primary_record_attempt_ids_missing_or_duplicate")
    if any(not value for value in plan_ids) or len(set(plan_ids)) != len(plan_ids):
        problems.append("primary_plan_attempt_ids_missing_or_duplicate")
    if set(record_ids) != set(plan_ids) or len(record_ids) != len(plan_ids):
        problems.append("primary_records_plans_do_not_match")

    records_by_id = {row.get("attempt_id"): row for row in primary if row.get("attempt_id")}
    plans_by_id = {row.get("attempt_id"): row for row in primary_plans if row.get("attempt_id")}
    for attempt_id in set(records_by_id) & set(plans_by_id):
        record, plan = records_by_id[attempt_id], plans_by_id[attempt_id]
        if (record.get("phase"), record.get("state")) != (plan.get("phase"), plan.get("state")):
            problems.append(f"record_plan_phase_state_mismatch:{attempt_id}")

    census_keys = [row.get("attempt_key") for row in primary_census]
    if any(not value for value in census_keys) or len(set(census_keys)) != len(census_keys):
        problems.append("primary_census_attempt_keys_missing_or_duplicate")
    expected_keys = {hashlib.sha256(value.encode()).hexdigest() for value in record_ids if value}
    if set(census_keys) != expected_keys or len(census_keys) != len(record_ids):
        problems.append("primary_census_attempts_do_not_match")
    census_by_key = {row.get("attempt_key"): row for row in primary_census if row.get("attempt_key")}
    for attempt_id, record in records_by_id.items():
        key = hashlib.sha256(attempt_id.encode()).hexdigest()
        observed = census_by_key.get(key)
        plan = plans_by_id.get(attempt_id)
        if not observed or not plan:
            continue
        actual_steps = [step.get("request_id") for step in record.get("http_steps", [])]
        planned_steps = [step.get("request_id") for step in plan.get("http_steps", [])]
        if (observed.get("phase"), observed.get("state")) != (record.get("phase"), record.get("state")):
            problems.append(f"census_phase_state_mismatch:{attempt_id}")
        if observed.get("step_ids") != actual_steps or any(step not in planned_steps for step in actual_steps):
            problems.append(f"census_steps_mismatch:{attempt_id}")

    invalid = [row.get("attempt_id") for row in records
               if row.get("success") is not True and row.get("success") is not False
               and row.get("success") is not None]
    if invalid:
        problems.append("invalid_success_values")
    return {
        "valid": not problems, "problems": problems,
        "phase_counts": phase_counts, "expected_phase_counts": expected_phases,
        "target_state_counts": state_counts, "expected_target_state_counts": expected_states,
        "primary_records": len(primary), "primary_plans": len(primary_plans),
        "primary_census": len(primary_census), "invalid_success_attempt_ids": invalid,
        "rule": "fixed phase/state counts, unique attempt identities, and matching records/plans/census",
    }


def _valid_probability(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0.0 <= value <= 1.0


def _valid_forecast(forecast) -> bool:
    interval = (forecast or {}).get("interval")
    states = (forecast or {}).get("by_state", {})
    return bool(forecast and forecast.get("available")
                and _valid_probability(forecast.get("prediction"))
                and isinstance(interval, list) and len(interval) == 2
                and all(_valid_probability(value) for value in interval)
                and interval[0] <= interval[1]
                and all(_valid_probability(states.get(state)) for state in EXPECTED_TARGET_STATES))


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
        def selected(call):
            if call.get("db_system") != selected_db.get("db_system"):
                return False
            role = selected_db.get("db_role")
            return role in (None, "shared") or call.get("db_role") == role
        db_calls = [call for call in contract["required_calls"] if "db_system" in call]
        conditional_value = contract.get("conditional_db") or []
        conditional_calls = (conditional_value if isinstance(conditional_value, list)
                             else [conditional_value.get("call", conditional_value)])
        unconditional_selected = any(selected(call) for call in db_calls)
        conditional_selected = any(selected(call) for call in conditional_calls)
        if conditional_selected:
            database = {"available": False, "reason": "declared_database_requirement_is_conditional"}
        elif selected_db and unconditional_selected:
            database = {"available": True, "database_down_prediction": 0.0,
                        "basis": "declared unconditional selected database requirement"}
        else:
            database = {"available": True, "database_down_prediction": 1.0,
                        "basis": "selected database is off-path under the declared complete contract"}
        result[operation] = {
            "available": True, "prediction": prediction, "by_state": by_state,
            "basis": "declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph",
            "controlled_service_required": requires_controlled, "database": database,
            "primary_conditional_assumption": "nonintervened requirements are fulfilled; not inferred from readiness or fitted outcomes",
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


def _journal_transport_cost(root: Path) -> dict:
    journal = root/"attempt-journal.jsonl"
    if not journal.is_file():
        return {"available": False, "reason": "attempt_journal_missing"}
    by_request = {}
    for plan in _read(root/"plans.json", []):
        category = "primary" if plan.get("phase") in PRIMARY_PHASES else "control"
        for step in plan.get("http_steps", []):
            by_request[step["request_id"]] = (category, plan.get("phase"))
    for record in _read(root/"preparation-operations.json", []):
        for step in record.get("http_steps", []):
            by_request[step["request_id"]] = ("preparation", "preparation")
    transports = {}
    with journal.open(encoding="utf-8") as stream:
        for line in stream:
            event = json.loads(line)
            kind, data = event.get("kind"), event.get("data") or {}
            if kind not in ("step_started", "step_finished", "step_transport_unknown"):
                continue
            identity, request_id = data.get("transport_id"), data.get("request_id")
            if not identity:
                raise ValueError("HTTP transport journal event lacks transport_id")
            if isinstance(request_id, str) and request_id.startswith("verify-"):
                category, phase = "verification", "verification"
            else:
                category, phase = by_request.get(request_id, ("unclassified", None))
            if category == "verification" and data.get("method") != "GET":
                raise ValueError("verification transport is not a GET")
            if kind == "step_started":
                if identity in transports:
                    raise ValueError("duplicate HTTP transport start")
                transports[identity] = {"category": category, "phase": phase,
                                        "request_id": request_id, "terminal": None}
            else:
                row = transports.get(identity)
                if row is None or row["terminal"] is not None:
                    raise ValueError("HTTP terminal event lacks one unique started event")
                if row["request_id"] != request_id:
                    raise ValueError("HTTP terminal request ID differs from start")
                row["terminal"] = kind
                row["elapsed_ns"] = data.get("elapsed_ns")
                row["error"] = data.get("error") if kind == "step_transport_unknown" else None
                row["status_code"] = data.get("status_code") if kind == "step_finished" else None
                if kind == "step_finished":
                    encoded = data.get("response_body_base64") or ""
                    if not isinstance(encoded, str) or len(encoded) % 4:
                        raise ValueError("invalid journal response body encoding")
                    row["response_body_bytes"] = (len(encoded)//4)*3 - (len(encoded)-len(encoded.rstrip("=")))
    categories = {}
    for category in ("primary", "preparation", "verification", "control", "unclassified"):
        rows = [row for row in transports.values() if row["category"] == category]
        categories[category] = {
            "started_gets": len(rows) if category == "verification" else None,
            "started_requests": len(rows),
            "completed_requests": sum(row["terminal"] == "step_finished" for row in rows),
            "transport_unknown_requests": sum(row["terminal"] == "step_transport_unknown" for row in rows),
            "unresolved_requests": sum(row["terminal"] is None for row in rows),
            "summed_completed_request_seconds": sum((row.get("elapsed_ns") or 0)/1e9 for row in rows
                                                    if row["terminal"] == "step_finished"),
            "summed_transport_unknown_seconds": sum((row.get("elapsed_ns") or 0)/1e9 for row in rows
                                                    if row["terminal"] == "step_transport_unknown"),
            "completed_response_body_bytes": sum(row.get("response_body_bytes", 0) for row in rows),
            "http_error_responses": sum(isinstance(row.get("status_code"), int) and
                                        row["status_code"] >= 400 for row in rows),
            "error_transport_ids": sorted(identity for identity, row in transports.items()
                                          if row["category"] == category and row.get("error")),
        }
    return {"available": True, "by_category": categories,
            "summed_request_seconds_are_not_wall_clock": True,
            "journal_path": str(journal),
            "rule": "each started transport_id counted once; terminal errors and unresolved requests retained"}


def _cost(root: Path, status: dict) -> dict:
    build = _read(root/"toolchain-build"/"toolchain-build.json")
    binaries = build.get("binaries", []) if isinstance(build, dict) else []
    preparation = _read(root/"toolchain"/"input-preparation-cost.json", {})
    preparation_seconds = ((preparation['ended_ns']-preparation['started_ns'])/1e9
        if isinstance(preparation.get('started_ns'), int) and isinstance(preparation.get('ended_ns'), int) else None)
    commands, returncodes, bering_replays, replay_statuses, bering_resources = [], [], [], [], []
    for path in (root/"toolchain").rglob("*.command.json") if (root/"toolchain").exists() else []:
        row = _read(path, {})
        if isinstance(row.get("started_ns"), int) and isinstance(row.get("ended_ns"), int):
            commands.append((row["ended_ns"]-row["started_ns"])/1e9)
        returncodes.append(row.get("returncode"))
    for path in (root/"toolchain").rglob("replay-command.json") if (root/"toolchain").exists() else []:
        row = _read(path, {})
        replay_statuses.append(row.get("status", "unknown"))
        if isinstance(row.get('child_resources'), dict):
            bering_resources.append({'command_record': str(path),
                'input_observations': row.get('input_observations'), **row['child_resources']})
        if isinstance(row.get("started_ns"), int) and isinstance(row.get("ended_ns"), int):
            elapsed = (row["ended_ns"]-row["started_ns"])/1e9
            commands.append(elapsed)
            bering_replays.append(elapsed)
        returncodes.append(row.get("returncode"))
    transport_cost = _journal_transport_cost(root)
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
        "toolchain_build_evidence_present": bool(binaries),
        "toolchain_clone_seconds": sum(row.get("clone_seconds", 0) for row in binaries) if binaries else None,
        "toolchain_build_seconds": sum(row.get("build_seconds", 0) for row in binaries) if binaries else None,
        "toolchain_command_seconds": sum(commands) if commands else None,
        "toolchain_command_count": len(commands),
        "shared_input_preparation_seconds": preparation_seconds,
        "shared_input_preparation_completed": preparation.get('completed'),
        "bering_replay_command_seconds": sum(bering_replays) if bering_replays else None,
        "bering_replay_command_count": len(bering_replays),
        "bering_replay_attempts": len(replay_statuses),
        "bering_replay_statuses": dict(Counter(replay_statuses)),
        "bering_child_resources": bering_resources,
        "bering_child_peak_rss_kib": max((row['child_peak_rss_kib'] for row in bering_resources
            if isinstance(row.get('child_peak_rss_kib'), (float, int))), default=None),
        "toolchain_command_returncodes": returncodes,
        "toolchain_command_failures": sum(code not in (0, None) for code in returncodes) if returncodes else None,
        "infrastructure_time_file": str(time_file),
        "infrastructure_time_file_present": time_file.is_file(),
        "infrastructure_time_fields": time_fields if time_file.is_file() else None,
        "training_checkpoint": _read(root/"training-checkpoint-cost.json"),
        "training_checkpoint_upload": _read(root/"infrastructure"/"training-checkpoint"/"release.json"),
        "remote_toolchain": _read(root/"infrastructure"/"remote-toolchain-v4"/"cost.json"),
        "swap_setup": _read(root/"infrastructure"/"swap-after.json"),
        "resource_heartbeats_retained": (root/"infrastructure"/"resources"/"heartbeats.jsonl").is_file(),
        "cost_overlap_note": "checkpoint creation/upload/hold and any remote worker wait are included in campaign elapsed; worker compute overlaps parent wait and is a separate Actions job; swap setup precedes campaign elapsed",
        "http_transport": transport_cost,
        "auxiliary_timeline_probes": (transport_cost.get("by_category") or {}).get("verification"),
        "manual_preparation": {"measured": False, "reason": "human preparation time was not instrumented; no full-cost advantage claimed"},
    }


def evaluate_campaign(root: Path, *, expected_phases=None, expected_states=None,
                      completed_status="acquisition_complete") -> dict:
    root = Path(root)
    status = _read(root/"status.json", {})
    records = _read(root/"external.json", [])
    blocks = _read(root/"blocks.json", [])
    plans = _read(root/"plans.json", [])
    census = _read(root/"census.json", [])
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
    completeness = _completeness(records, plans, census, expected_phases=expected_phases,
                                 expected_states=expected_states)
    expected_primary = sum(completeness["expected_phase_counts"].values())
    complete = (status.get("status") == completed_status and integrity["valid"]
                and completeness["valid"])
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
                forecast_valid = _valid_forecast(forecast)
                available = bool(complete and forecast_valid)
                prediction = forecast.get("prediction") if available else None
                state_eval = {}
                for state, actual_state in per_state.items():
                    candidate = forecast.get("by_state", {}).get(state) if available else None
                    predicted = candidate if _valid_probability(candidate) else None
                    state_eval[state] = {**actual_state, "prediction": predicted,
                                         "error": _error(predicted, actual_state["bounds"])}
                evaluations.append({
                    "operation": operation, "source": source, "variant": variant,
                    "available": available, "reason": None if available else (
                        "campaign_incomplete_or_integrity_failed" if not complete else
                        (forecast or {}).get("reason", "forecast_missing_or_invalid")),
                    "prediction": prediction, "actual_counts": actual_counts,
                    "point_prediction": prediction,
                    "forecast_interval": (forecast or {}).get("interval"),
                    "forecast_interval_status": ("valid" if available else
                        "retained_unavailable_or_invalid_forecast_interval" if forecast else
                        "unknown_missing_forecast"),
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
        "healthy_state_11_prediction": (
            forecasts.get(item["source"], {}).get(item["variant"], {})
            .get(item["operation"], {}).get("by_state", {}).get("11") if item["available"] else None),
        "database_down_prediction": (
            forecasts.get(item["source"], {}).get(item["variant"], {})
            .get(item["operation"], {}).get("database_down_prediction") if item["available"] else None),
        "prognostic_impact": None,
        "counted_as_accuracy_benefit": False,
    } for item in evaluations]
    for item in database["forecast_impact"]:
        healthy, down = item["healthy_state_11_prediction"], item["database_down_prediction"]
        if _valid_probability(healthy) and _valid_probability(down):
            item["prognostic_impact"] = healthy - down
            item["comparison"] = "healthy_state_11_minus_database_down"
        else:
            item["healthy_state_11_prediction"] = healthy if _valid_probability(healthy) else None
            item["database_down_prediction"] = down if _valid_probability(down) else None
            item["comparison"] = "unknown_unless_both_predictions_available"
    classes = _read(root/"classes-v4.json")
    return {
        "schema_version": "evaluation-v4", "root": str(root.resolve()),
        "system": status.get("system"), "mode": status.get("mode"), "seed": status.get("seed"),
        "status": status, "integrity": integrity, "completeness": completeness,
        "complete_for_evaluation": complete,
        "counts": {"all_records": len(records), "primary": len(primary), "target": len(target),
                   "expected_primary": expected_primary,
                   "primary_count_matches": len(primary) == expected_primary,
                   "target_state_counts": {state: sum(row.get("state") == state for row in target)
                                           for state in ("11", "10", "01", "00")},
                   "blocks": len(blocks)},
        "evaluations": evaluations, "manual_baselines": _manual_baselines(status.get("system"), operations)
            if status.get("system") else {},
        "manual_baseline_supplied_entry_identity_groups": _read(
            root/"toolchain"/"static-inputs.json", {}).get('supplied_entry_identity_groups', []),
        "database": database, "async": _async_results(root),
        "classes": classes if classes is not None else {"available": False, "reason": "classes-v4.json pending"},
        "evidence": _read(root/"evidence-v4.json") or {"available": False, "reason": "evidence-v4.json pending"},
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


def _saved_reports(roots: list[Path]) -> list[dict]:
    """Admit compact reports by their original Actions artifact/run identity.

    This validates copied compact files, but cannot reverify omitted raw capture
    or frozen Bering outputs. The source cell's full-evidence evaluation remains
    explicitly attributed to its original Actions run.
    """
    found = set()
    for root in roots:
        root = Path(root)
        if root.is_file() and root.name == "evaluation-v4.json":
            found.add(root.resolve())
        elif root.is_dir():
            found.update(path.resolve() for path in root.rglob("evaluation-v4.json"))
    reports = []
    artifact_ids = set()
    for path in sorted(found):
        folder = path.parent
        manifest = _read(folder/"evaluation-manifest.json")
        artifact = _read(folder/"artifact-provenance.json")
        if not manifest or manifest.get("schema_version") != "v4-cell-summary-manifest":
            raise ValueError(f"saved v4 evaluation lacks its cell manifest: {path}")
        if not artifact or type(artifact.get("artifact_id")) is not int:
            raise ValueError(f"saved v4 evaluation lacks immutable artifact identity: {path}")
        if artifact["artifact_id"] in artifact_ids:
            raise ValueError("duplicate v4 summary artifact ID")
        artifact_ids.add(artifact["artifact_id"])
        if (str(artifact.get("run_id")) != str(manifest.get("run_id"))
                or artifact.get("head_sha") != manifest.get("commit")
                or artifact.get("name") != f"v4-summary-{manifest.get('system')}-{manifest.get('mode')}-{manifest.get('seed')}-{manifest.get('run_id')}"
                or artifact.get("full_artifact_name") != manifest.get("full_artifact_name")
                or type(artifact.get("full_artifact_id")) is not int
                or artifact.get("expired") is True):
            raise ValueError(f"saved v4 evaluation artifact/run provenance mismatch: {path}")
        hashes = manifest.get("files_sha256") or {}
        for name in ("evaluation-v4.json", "status.json", "plans.json", "census.json",
                     "blocks.json", "freeze-integrity.json", "toolchain/forecasts.json",
                     "evidence-v4.json"):
            expected = hashes.get(name)
            target = folder/name
            if expected is not None and (not target.is_file() or _digest(target) != expected):
                raise ValueError(f"saved v4 evaluation compact hash mismatch: {target}")
            if expected is None and target.is_file():
                raise ValueError(f"unexpected unadmitted compact file: {target}")
        if not hashes.get("evaluation-v4.json"):
            raise ValueError(f"saved v4 evaluation missing: {path}")
        report = _read(path)
        if report.get("schema_version") != "evaluation-v4":
            raise ValueError(f"invalid saved v4 evaluation schema: {path}")
        status = _read(folder/"status.json")
        for key in ("system", "mode", "seed"):
            declared = manifest.get(key)
            if (report.get(key) is not None and report.get(key) != declared) or (
                    status is not None and status.get(key) is not None and status.get(key) != declared):
                raise ValueError(f"saved v4 cell identity mismatch: {path}: {key}")
        if status is not None and report.get("status") != status:
            raise ValueError(f"saved v4 evaluation status differs from copied status: {path}")
        if status is None and report.get("status") not in ({}, None):
            raise ValueError(f"saved v4 evaluation has status absent from compact source: {path}")
        if report.get("complete_for_evaluation") and any(hashes.get(name) is None for name in
                ("status.json", "plans.json", "census.json", "blocks.json", "freeze-integrity.json",
                 "toolchain/forecasts.json")):
            raise ValueError(f"complete saved v4 evaluation lacks required compact proof files: {path}")
        if status is None and report.get("complete_for_evaluation"):
            raise ValueError(f"status-less saved v4 evaluation cannot be complete: {path}")
        if status is None or any(report.get(key) is None for key in ("system", "mode", "seed")):
            if report.get("complete_for_evaluation"):
                raise ValueError(f"complete saved v4 evaluation lacks source cell identity: {path}")
            for key in ("system", "mode", "seed"):
                report[key] = manifest[key]
            report["technical_identity_from_workflow_matrix"] = True
        report["original_campaign_root"] = report.get("root")
        report["root"] = str(folder.resolve())
        report["saved_evaluation_provenance"] = {
            "run_id": manifest["run_id"], "head_sha": manifest["commit"],
            "artifact_id": artifact["artifact_id"], "artifact_name": artifact["name"],
            "artifact_digest": artifact.get("digest"),
            "full_artifact_name": manifest.get("full_artifact_name"),
            "full_artifact_id": artifact["full_artifact_id"],
            "full_artifact_digest": artifact.get("full_artifact_digest"),
            "full_artifact_expired": artifact.get("full_artifact_expired"),
            "full_originals_reverified_by_report_job": False,
            "original_journal_sha256_claim": hashes.get("attempt-journal.jsonl"),
            "manifest_sha256": _digest(folder/"evaluation-manifest.json"),
            "evaluation_sha256": hashes["evaluation-v4.json"],
        }
        reports.append(report)
    return reports


def _selection(selection_manifest) -> tuple[dict, dict]:
    if selection_manifest is None:
        return {}, {"provided": False}
    path = Path(selection_manifest) if not isinstance(selection_manifest, dict) else None
    value = _read(path) if path else selection_manifest
    if value.get("policy") != "technical_replacement_only_no_outcome_selection":
        raise ValueError("selection manifest must assert technical-only, outcome-independent replacement")
    selected = {}
    for row in value.get("cells", []):
        key = (row.get("system"), row.get("mode"), row.get("seed"))
        if key in selected or not row.get("reason_code", "").startswith("technical_"):
            raise ValueError(f"invalid or duplicate technical selection for {key}")
        selected[key] = row
    provenance = {"provided": True, "path": str(path.resolve()) if path else None,
                  "sha256": _digest(path) if path else None, "manifest": value}
    return selected, provenance


def aggregate(roots: list[Path], report_dir: Path, selection_manifest=None,
              *, saved: bool = False) -> dict:
    reports = (_saved_reports(roots) if saved else
               [evaluate_campaign(path) for path in _find_campaigns(roots)])
    candidates = {}
    for report in reports:
        candidates.setdefault((report["system"], report["mode"], report["seed"]), []).append(report)
    requested, selection_provenance = _selection(selection_manifest)
    selected, ambiguous, replacements = {}, [], []
    for key, attempts in sorted(candidates.items(), key=lambda item: str(item[0])):
        if len(attempts) == 1:
            if key in requested:
                raise ValueError(f"selection manifest names non-duplicate cell {key}")
            selected[key] = attempts[0]
            continue
        choice = requested.get(key)
        roots_for_cell = {str(Path(row["root"]).resolve()) for row in attempts}
        if choice is None:
            ambiguous.append({"cell": list(key), "candidate_roots": sorted(roots_for_cell),
                              "reason": "duplicate_cell_requires_explicit_technical_selection"})
            continue
        declared = {str(Path(value).resolve()) for value in choice.get("candidate_roots", [])}
        chosen = str(Path(choice.get("selected_root", "")).resolve())
        if declared != roots_for_cell or chosen not in roots_for_cell:
            raise ValueError(f"selection candidates do not exactly match retained inputs for {key}")
        chosen_report = next(row for row in attempts if str(Path(row["root"]).resolve()) == chosen)
        excluded_reports = [row for row in attempts if str(Path(row["root"]).resolve()) != chosen]
        if not chosen_report["complete_for_evaluation"] or any(
                row["complete_for_evaluation"] for row in excluded_reports):
            raise ValueError(f"technical selection for {key} must retain the sole complete campaign")
        selected[key] = chosen_report
        replacements.append({"cell": list(key), "selected_root": chosen,
                             "excluded_roots": sorted(roots_for_cell-{chosen}),
                             "reason_code": choice["reason_code"]})
    unused = set(requested)-set(candidates)
    if unused:
        raise ValueError(f"selection manifest names missing cells: {sorted(unused)}")
    expected = {(s, m, z) for s in ("deathstarbench", "otel_demo", "petclinic")
                for m in ("absent", "partial", "full") for z in (6, 7, 8)}
    grouped = {}
    for report in selected.values():
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
        "input_mode": ("saved_actions_evaluations_original_raw_not_reverified" if saved else
                       "full_campaign_evidence_recomputed"),
        "selection": selection_provenance,
        "technical_replacements": replacements,
        "ambiguous_duplicate_cells": ambiguous,
        "grid": {"expected_cells": 27, "selected_unambiguous_cells": len(selected),
                 "retained_campaign_attempts": len(reports),
                 "missing_cells": [list(item) for item in sorted(expected-set(selected))],
                 "expected_primary_total": EXPECTED_GRID_TOTAL,
                 "selected_primary_total": sum(r["counts"]["primary"] for r in selected.values()),
                 "retained_attempt_primary_total": sum(r["counts"]["primary"] for r in reports)},
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
    group.add_argument("--aggregate-saved", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--selection", type=Path,
                        help="auditable technical-only selection for duplicate cells")
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        parser.error("v4 research evaluation is permitted only in GitHub Actions")
    if args.campaign:
        if args.selection is not None: parser.error("--selection is only valid with --aggregate")
        if args.out is None: parser.error("--campaign requires --out")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(evaluate_campaign(args.campaign), indent=2)+"\n")
    else:
        if args.report_dir is None: parser.error("--aggregate requires --report-dir")
        aggregate(args.aggregate or args.aggregate_saved, args.report_dir, args.selection,
                  saved=bool(args.aggregate_saved))


if __name__ == "__main__":
    main()
