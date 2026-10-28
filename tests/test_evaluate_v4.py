from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import types

import ebpf_discovery.evaluate_v4 as evaluator
from ebpf_discovery.evaluate_v4 import aggregate, evaluate_campaign, main


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fake_declaration(monkeypatch):
    monkeypatch.setattr(evaluator, "EXPECTED_PHASE_COUNTS",
                        {"class_train": 1, "calibration": 4, "target": 2, "class_test": 1})
    monkeypatch.setattr(evaluator, "EXPECTED_TARGET_STATES",
                        {"11": 1, "10": 0, "01": 0, "00": 1})
    systems = sys.modules.setdefault("systems", types.ModuleType("systems"))
    fake = types.ModuleType("systems.fake")
    experiment = types.ModuleType("systems.fake.experiment_v4")
    experiment.CONTROLLED_SERVICE_ALIASES = ["controlled"]
    experiment.SELECTED_DATABASE = {"db_system": "postgresql"}
    experiment.CONTRACTS = {
        "required": {"required_calls": [
            {"caller": ["entry"], "callee": ["controlled"]},
            {"caller": ["controlled"], "db_system": "postgresql", "db_role": "selected"},
        ]},
        "independent": {"required_calls": [{"caller": ["entry"], "callee": ["other"]}]},
        "conditional": {"conditional_db": {"call":
            {"caller": ["entry"], "db_system": "postgresql", "db_role": "conditional"}},
            "required_calls": []},
    }
    monkeypatch.setitem(sys.modules, "systems.fake", fake)
    monkeypatch.setitem(sys.modules, "systems.fake.experiment_v4", experiment)
    setattr(systems, "fake", fake)


def _campaign(root: Path, *, seed=6, status="acquisition_complete", outcomes=(True, None)) -> Path:
    _write(root / "status.json", {"system": "fake", "mode": "full", "seed": seed,
                                   "status": status, "elapsed_seconds": 12.0})
    records = []
    for index, outcome in enumerate(outcomes):
        records.append({"attempt_id": f"target-{index}", "operation": "required", "phase": "target",
                        "state": ("11", "00")[index % 2], "success": outcome,
                        "http_steps": [{"request_id": f"request-target-{index}"}],
                        "started_ns": index * 10, "ended_ns": index * 10 + 5})
    for phase, count in (("class_train", 1), ("calibration", 4), ("class_test", 1)):
        records.extend({"attempt_id": f"{phase}-{index}", "operation": "required", "phase": phase,
                        "state": "11", "success": True,
                        "http_steps": [{"request_id": f"request-{phase}-{index}"}]}
                       for index in range(count))
    records += [{"operation": "required", "phase": "db_up", "state": "11", "success": True},
                {"operation": "required", "phase": "db_down", "state": "11", "success": False}]
    _write(root / "external.json", records)
    _write(root / "blocks.json", [{"phase": "target"}])
    primary = [row for row in records if row["phase"] in evaluator.PRIMARY_PHASES]
    plans = [{"attempt_id": row["attempt_id"], "phase": row["phase"], "state": row["state"],
              "http_steps": row["http_steps"]} for row in primary]
    census = [{"attempt_key": hashlib.sha256(row["attempt_id"].encode()).hexdigest(),
               "phase": row["phase"], "state": row["state"],
               "step_ids": [step["request_id"] for step in row["http_steps"]]} for row in primary]
    _write(root / "plans.json", plans)
    _write(root / "census.json", census)
    forecasts = {}
    frozen = {}
    for source in ("ebpf", "native", "combined"):
        forecasts[source] = {}
        for variant in ("raw", "network_scope"):
            model = root / "toolchain" / source / variant / "required" / "model.json"
            _write(model, {"services": [{"id": "entry"}, {"id": "controlled"}], "edges": []})
            forecast = {"available": True, "prediction": .75, "interval": [.75, .75],
                        "by_state": {"11": 1.0, "10": 1.0, "01": 1.0, "00": 0.0},
                        "database_down_prediction": .25, "simulator": "Sheaft",
                        "graph_sha256": _hash(model)}
            forecasts[source][variant] = {"required": forecast}
            frozen[str(model.relative_to(root))] = _hash(model)
    forecasts_path = root / "toolchain" / "forecasts.json"
    _write(forecasts_path, forecasts)
    frozen[str(forecasts_path.relative_to(root))] = _hash(forecasts_path)
    _write(root / "freeze-integrity.json", {"all_unchanged": True, "sha256_by_path": frozen})
    return root


def test_unknown_outcomes_produce_bounds_error_range_and_no_accuracy_gate(tmp_path: Path, monkeypatch):
    _fake_declaration(monkeypatch)
    report = evaluate_campaign(_campaign(tmp_path / "campaign"))
    row = next(row for row in report["evaluations"]
               if row["operation"] == "required" and row["source"] == "ebpf" and row["variant"] == "raw")
    assert row["actual_counts"] == {"success": 1, "failure": 0, "unknown": 1,
                                    "total": 2, "invalid": 0}
    assert row["observed_empirical_bounds"] == [.5, 1.0]
    assert row["error"] == {"range": [0.0, .25], "worst_end_error": .25}
    assert "IID" in row["nominal_wilson_envelope"]["label"]
    assert report["manual_baselines"]["required"]["prediction"] == .875
    assert report["manual_baselines"]["independent"]["prediction"] == 1.0
    assert report["manual_baselines"]["conditional"]["database"]["available"] is False
    assert report["manual_baselines"]["independent"]["database"]["database_down_prediction"] == 1.0
    impact = next(row for row in report["database"]["forecast_impact"]
                  if row["operation"] == "required" and row["source"] == "ebpf"
                  and row["variant"] == "raw")
    assert impact["healthy_state_11_prediction"] == 1.0
    assert impact["prognostic_impact"] == .75
    def keys(value):
        if isinstance(value, dict):
            return set(value) | set().union(*(keys(item) for item in value.values()), set())
        if isinstance(value, list):
            return set().union(*(keys(item) for item in value), set())
        return set()
    assert all("threshold" not in key.lower() for key in keys(report))


def test_manual_baseline_does_not_change_with_external_outcomes(tmp_path: Path, monkeypatch):
    _fake_declaration(monkeypatch)
    first = evaluate_campaign(_campaign(tmp_path / "one", outcomes=(True, True)))
    second = evaluate_campaign(_campaign(tmp_path / "two", outcomes=(False, None)))
    assert first["manual_baselines"] == second["manual_baselines"]
    assert first["manual_baselines"]["required"]["database"]["database_down_prediction"] == 0.0


def test_partial_or_integrity_failed_campaign_is_unknown_not_scored(tmp_path: Path, monkeypatch):
    _fake_declaration(monkeypatch)
    root = _campaign(tmp_path / "partial", status="technical_failure")
    report = evaluate_campaign(root)
    assert report["complete_for_evaluation"] is False
    assert all(row["available"] is False and row["prediction"] is None for row in report["evaluations"])
    root = _campaign(tmp_path / "tampered")
    model = root / "toolchain" / "ebpf" / "raw" / "required" / "model.json"
    model.write_text("{}\n", encoding="utf-8")
    report = evaluate_campaign(root)
    assert report["integrity"]["valid"] is False
    assert any("hash_mismatch" in reason for reason in report["integrity"]["problems"])


def test_acquisition_status_cannot_admit_truncated_or_invalid_records(tmp_path: Path, monkeypatch):
    _fake_declaration(monkeypatch)
    root = _campaign(tmp_path / "truncated")
    records = json.loads((root / "external.json").read_text(encoding="utf-8"))
    records.pop(next(index for index, row in enumerate(records) if row.get("phase") == "class_test"))
    records[0]["success"] = "yes"
    _write(root / "external.json", records)
    report = evaluate_campaign(root)
    assert report["complete_for_evaluation"] is False
    assert "primary_phase_counts_mismatch" in report["completeness"]["problems"]
    assert "primary_records_plans_do_not_match" in report["completeness"]["problems"]
    assert "invalid_success_values" in report["completeness"]["problems"]
    assert all(row["available"] is False for row in report["evaluations"])


def test_async_pending_is_not_failure_and_aggregate_keeps_repeat_coverage(tmp_path: Path, monkeypatch):
    _fake_declaration(monkeypatch)
    roots = []
    for seed, prediction_outcomes in zip((6, 7, 8), ((True, None), (True, False), (False, None))):
        root = _campaign(tmp_path / f"seed-{seed}", seed=seed, outcomes=prediction_outcomes)
        _write(root / "async-paused-snapshot.json", [
            {"async_verification": {"state": "pending", "success": None}},
        ])
        roots.append(root)
    report = evaluate_campaign(roots[0])
    assert report["async"]["paused_snapshot"]["states"] == {"pending": 1}
    assert report["async"]["paused_snapshot"]["paused_absence_is_failure"] is False
    combined = aggregate([tmp_path], tmp_path / "report")
    group = next(row for row in combined["per_operation_source_variant_repeats"]
                 if row["operation"] == "required" and row["source"] == "ebpf" and row["variant"] == "raw")
    assert group["coverage"] == {"expected_repeats": 3, "observed": 3, "available": 3}
    assert combined["overall_accuracy_mean"] is None
    assert (tmp_path / "report" / "evaluation-v4.csv").is_file()
    assert (tmp_path / "report" / "evaluation-v4-errors.svg").is_file()
    missing = next(row for row in combined["per_operation_source_variant_repeats"]
                   if row["operation"] == "independent" and row["source"] == "ebpf"
                   and row["variant"] == "raw")
    assert missing["prediction_mean"] is None
    assert missing["available_count"] == 0


def test_duplicate_cell_is_unscored_without_audited_technical_selection(tmp_path: Path, monkeypatch):
    _fake_declaration(monkeypatch)
    first = _campaign(tmp_path / "seed-6-original", seed=6, status="technical_failure")
    replacement = _campaign(tmp_path / "seed-6-replacement", seed=6)
    _campaign(tmp_path / "seed-7", seed=7)
    _campaign(tmp_path / "seed-8", seed=8)
    ambiguous = aggregate([tmp_path], tmp_path / "ambiguous-report")
    assert len(ambiguous["ambiguous_duplicate_cells"]) == 1
    assert ambiguous["grid"]["retained_campaign_attempts"] == 4
    group = next(row for row in ambiguous["per_operation_source_variant_repeats"]
                 if row["operation"] == "required" and row["source"] == "ebpf"
                 and row["variant"] == "raw")
    assert group["repeat_count"] == 2

    manifest = {
        "policy": "technical_replacement_only_no_outcome_selection",
        "cells": [{"system": "fake", "mode": "full", "seed": 6,
                   "selected_root": str(replacement.resolve()),
                   "candidate_roots": [str(first.resolve()), str(replacement.resolve())],
                   "reason_code": "technical_incomplete_original"}],
    }
    selected = aggregate([tmp_path], tmp_path / "selected-report", manifest)
    assert selected["ambiguous_duplicate_cells"] == []
    assert len(selected["technical_replacements"]) == 1
    group = next(row for row in selected["per_operation_source_variant_repeats"]
                 if row["operation"] == "required" and row["source"] == "ebpf"
                 and row["variant"] == "raw")
    assert group["repeat_count"] == 3


def test_cli_rejects_local_research_processing(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(sys, "argv", ["evaluate_v4", "--campaign", str(tmp_path),
                                      "--out", str(tmp_path / "out.json")])
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("CLI evaluation unexpectedly ran outside GitHub Actions")
