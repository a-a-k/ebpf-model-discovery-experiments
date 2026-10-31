"""Collector-separated evaluation with technical, never accuracy-based gates."""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sqlite3

from . import evaluate_v4 as legacy
from .campaign_v5 import COLLECTORS, workload_counts
from .toolchain_v5 import collector_provenance


def expected_counts(system, smoke):
    declaration = importlib.import_module(f"systems.{system}.experiment_v4")
    counts = workload_counts(len(declaration.CONTRACTS), smoke)
    phases = {key: counts[key] * multiplier for key, multiplier in (
        ("class_train", 1), ("calibration", 4), ("target", 8), ("class_test", 1))}
    states = {key: counts["target"] * multiplier
              for key, multiplier in (("11", 4), ("10", 2), ("01", 1), ("00", 1))}
    return declaration, counts, phases, states


def acquisition_checks(root, status, declaration):
    problems = []
    try:
        provenance = collector_provenance(root, status)
    except (OSError, ValueError) as exc:
        provenance = None
        problems.append("collector_provenance_invalid:" + str(exc))
    if status.get("collector") not in COLLECTORS:
        problems.append("collector_outside_fixed_four")
    control = legacy._read(root / "observations/technical-positive-control.json", {})
    if (control.get("collector") != status.get("collector")
            or control.get("selected_ebpf_origin_proven") is not True
            or set(control.get("proofs", {})) != {"a", "b"}
            or not all(item.get("proven") is True for item in control.get("proofs", {}).values())):
        problems.append("two_guest_ebpf_origin_control_missing_or_failed")
    drain = legacy._read(root / "observations/drain-evidence.json", {})
    if (drain.get("collector") != status.get("collector")
            or drain.get("technical_complete") is not True
            or drain.get("accepted_receiver_bytes_closed_and_hashed") is not True):
        problems.append("accepted_observation_capture_not_closed")
    native_counts = {}
    audit_services = dict(getattr(declaration, "NATIVE_AUDIT_SERVICES", {}))
    native_audit_counts = {}
    native_application_counts = {}
    index = root / "observation-index.sqlite"
    if index.is_file():
        connection = sqlite3.connect(index.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            native_counts = dict(connection.execute(
                "SELECT service, COUNT(*) FROM spans WHERE source='native' GROUP BY service"))
        finally:
            connection.close()
        native_audit_counts = {service: count for service, count in native_counts.items()
                               if service in audit_services}
        native_application_counts = {service: count for service, count in native_counts.items()
                                     if service not in audit_services}
        if status.get("mode") == "absent" and sum(native_application_counts.values()):
            problems.append("native_observations_present_in_absent_mode")
        if status.get("mode") == "partial" and any(
                native_counts.get(alias, 0) for alias in declaration.CONTROLLED_SERVICE_ALIASES):
            problems.append("controlled_native_observations_present_in_partial_mode")
    else:
        problems.append("observation_index_missing")
    return {"valid": not problems, "problems": problems, "provenance": provenance,
            "native_observations_by_service": native_counts,
            "native_application_observations_by_service": native_application_counts,
            "native_audit_observations_by_service": native_audit_counts,
            "native_audit_service_declarations": audit_services,
            "native_observation_count_unit": "span",
            "native_audit_exclusion_scope": "application_tracing_mode_check_only",
            "missing_native_coverage_is_technical_failure": False,
            "positive_control": control, "final_drain": drain,
            "application_protocol_coverage_required": False,
            "accuracy_threshold": None, "kernel_or_producer_loss_absent": None}


def scientific_summaries(report):
    """Copy bounded saved scientific fields for the report; do not rescore."""
    evidence = report.get("evidence") or {}
    graph_keys = ("available", "reason", "services", "edges", "endpoints",
                  "bering_outputs_present", "snapshot_discovery_counts", "database_mapping",
                  "database_fault_prognostic_impact")
    alias_keys = ("system", "address", "port", "network_scope", "identity_kind", "nodes",
                  "callers", "shared_by_at_least_two_callers")
    graphs = {
        source: {variant: {
            operation: {**{key: row[key] for key in graph_keys if key in row},
                **({"database_aliases": [{key: alias[key] for key in alias_keys if key in alias}
                                         for alias in row["database_aliases"]]}
                   if "database_aliases" in row else {}),
                **({"incomplete_database_alias_count": len(row["incomplete_database_aliases"])}
                   if "incomplete_database_aliases" in row else {})}
            for operation, row in operations.items()}
            for variant, operations in variants.items()}
        for source, variants in (evidence.get("graphs") or {}).items()}
    cross_keys = ("exact_parent_links", "invalid_identity_candidates",
                  "placement_coverage", "header_verdicts", "interpretation")
    cross_guest = {
        source: {key: row[key] for key in cross_keys if key in row}
        for source, row in (evidence.get("cross_guest") or {}).items()}
    causal = evidence.get("async")
    attempts = causal.get("attempts") if isinstance(causal, dict) else None
    causal_rows = None if attempts is None else [
        {key: row[key] for key in ("attempt_id", "source", "phase", "four_stage_causal_chain",
                                   "trace_context_reasons", "markers", "unresolved_markers")
         if key in row} for row in attempts]
    return {
        "manual_baselines": report.get("manual_baselines"),
        "database": report.get("database"),
        "graphs": graphs,
        "classes": {name: {
            "class_test_metrics": (report.get(name) or {}).get("class_test_metrics"),
            "fit_updated_during_evaluation": (report.get(name) or {}).get("fit_updated_during_evaluation"),
            "interpretation": (report.get(name) or {}).get("interpretation")}
            for name in ("classes", "legacy_classes")},
        "async": report.get("async"),
        "cross_guest": cross_guest,
        "causal_attempt_verdicts": causal_rows,
        "causal_scope": ({key: causal[key] for key in
                          ("linker_scope", "invalid_identity_observations", "scope",
                           "external_verification_files_present") if key in causal}
                         if isinstance(causal, dict) else None),
        "interpretation": "Copied saved fields. Repeated source/variant rows do not create independent external attempts.",
    }


def evaluate_campaign(root):
    root = Path(root)
    status = legacy._read(root / "status.json", {})
    smoke = status.get("smoke") is True
    declaration, counts, phases, states = expected_counts(status["system"], smoke)
    static = legacy._read(root/'toolchain/static-inputs.json', {})
    paired_context = bool((static.get('collector') or {}).get('paired_context_baseline')
                          or (root/'toolchain/context-baseline/forecasts.json').is_file())
    report = legacy.evaluate_campaign(root, expected_phases=phases, expected_states=states,
                                     completed_status="smoke_complete" if smoke else "acquisition_complete",
                                     paired_context_baseline=paired_context)
    acquisition = acquisition_checks(root, status, declaration)
    if status.get("workload_counts") != counts:
        acquisition["problems"].append("workload_configuration_differs_from_fixed_design")
    if smoke and status.get("seed") != 6:
        acquisition["problems"].append("smoke_seed_differs_from_fixed_design")
    acquisition["valid"] = not acquisition["problems"]
    report.update(schema_version="evaluation-v5", collector=status.get("collector"), smoke=smoke,
                  acquisition=acquisition, legacy_classes=report["classes"],
                  classes=legacy._read(root / "classes-v5.json"),
                  complete_for_evaluation=bool(report["complete_for_evaluation"] and acquisition["valid"]))
    if not report["complete_for_evaluation"]:
        # Retain raw candidate numbers, but never score a technically invalid run.
        for row in report["evaluations"]:
            row["candidate_before_acquisition_gate"] = {
                key: row.get(key) for key in ("available", "prediction", "error")}
            row.update(available=False, prediction=None, point_prediction=None,
                       reason="campaign_technical_validation_failed", error=legacy._error(None, None))
            for state in row["by_state"].values():
                state.update(prediction=None, error=legacy._error(None, None))
        for item in report["database"]["forecast_impact"]:
            item.update(prognostic_impact=None, comparison="unknown_technical_validation_failed")
    report["smoke_technical_pass"] = bool(smoke and report["complete_for_evaluation"])
    report["primary_series_result"] = bool(not smoke and report["complete_for_evaluation"])
    report["scientific_summaries"] = scientific_summaries(report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate_campaign(args.campaign)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["complete_for_evaluation"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
