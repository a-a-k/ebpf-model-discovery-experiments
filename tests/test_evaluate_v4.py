from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import types

from ebpf_discovery.evaluate_v4 import aggregate, evaluate_campaign


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fake_declaration(monkeypatch):
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
        "conditional": {"conditional_db": True, "required_calls": [
            {"caller": ["entry"], "db_system": "postgresql", "db_role": "conditional"},
        ]},
    }
    monkeypatch.setitem(sys.modules, "systems.fake", fake)
    monkeypatch.setitem(sys.modules, "systems.fake.experiment_v4", experiment)
    setattr(systems, "fake", fake)


def _campaign(root: Path, *, seed=6, status="acquisition_complete", outcomes=(True, None)) -> Path:
    _write(root / "status.json", {"system": "fake", "mode": "full", "seed": seed,
                                   "status": status, "elapsed_seconds": 12.0})
    records = []
    for index, outcome in enumerate(outcomes):
        records.append({"operation": "required", "phase": "target", "state": ("11", "00")[index % 2],
                        "success": outcome, "started_ns": index * 10, "ended_ns": index * 10 + 5})
    records += [{"operation": "required", "phase": "db_up", "state": "11", "success": True},
                {"operation": "required", "phase": "db_down", "state": "11", "success": False}]
    _write(root / "external.json", records)
    _write(root / "blocks.json", [{"phase": "target"}])
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
    assert row["actual_counts"] == {"success": 1, "failure": 0, "unknown": 1, "total": 2}
    assert row["observed_empirical_bounds"] == [.5, 1.0]
    assert row["error"] == {"range": [0.0, .25], "worst_end_error": .25}
    assert "IID" in row["nominal_wilson_envelope"]["label"]
    assert report["manual_baselines"]["required"]["prediction"] == .875
    assert report["manual_baselines"]["independent"]["prediction"] == 1.0
    assert report["manual_baselines"]["conditional"]["database"]["available"] is False
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
