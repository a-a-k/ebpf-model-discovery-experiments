import hashlib
import json
from pathlib import Path

import pytest

from ebpf_discovery import evaluate_v3
from ebpf_discovery.evaluate_v3 import aggregate, evaluate
from ebpf_discovery.observations import opaque_attempt


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def campaign(root: Path, system="petclinic", mode="absent", seed=3):
    external = []
    counts = {"class_train": 1, "calibration": 2, "target": 2, "class_test": 1}
    for phase, count in counts.items():
        for index in range(count):
            external.append({
                "attempt_id": f"{phase}-{index}", "phase": phase, "state": "11",
                "operation": "read", "success": None if phase == "target" and index == 1 else True,
                "http_steps": [{"request_id": f"req-{phase}-{index}"}],
            })
    for phase in ("db_up", "db_down"):
        for index in range(20):
            external.append({
                "attempt_id": f"{phase}-{index}", "phase": phase, "state": "11",
                "operation": "read", "success": phase == "db_up",
                "http_steps": [{"request_id": f"req-{phase}-{index}"}],
            })
    if system == "otel_demo":
        for phase in ("async_normal", "async_paused", "async_recovered"):
            for index in range(20):
                external.append({
                    "attempt_id": f"{phase}-{index}", "phase": phase, "state": "11",
                    "operation": "read", "success": None if index == 0 else True,
                    "http_steps": [] if index == 0 else [{
                        "request_id": f"req-{phase}-{index}", "url": "http://frontend/api/checkout",
                    }],
                    "async_verification": {"success": None if index == 0 else index % 2 == 0},
                })
    write(root / "status.json", {
        "system": system, "mode": mode, "seed": seed, "run_id": "1",
        "protocol_version": "source-contract-v3", "status": "acquisition_complete",
        "elapsed_seconds": 10,
    })
    write(root / "external.json", external)
    write(root / "blocks.json", [{
        "id": "target", "phase": "target", "state": "11", "attempts": 2,
        "requested_operations_per_second": 20, "achieved_operations_per_second": 19.5,
        "worker_capacity": 256, "nominal_load_seconds": 60,
        "load_started_ns": 1, "ended_ns": 2,
    }])
    write(root / "automatic-metrics.json", {
        "ebpf": {"route": {"target": {"total": 2, "covered": 1, "unknown_fraction": 0.5,
                                         "ari_on_covered": 1.0}}}
    })
    write(root / "database-controls.json", {
        "db_up": {"read": {"n": 20, "successes": 20, "failures": 0, "unknown": 0}},
        "db_down": {"read": {"n": 20, "successes": 0, "failures": 20, "unknown": 0}},
    })
    if system == "petclinic":
        write(root / "database" / "model.json", {"frozen": True})
        write(root / "database" / "predictions.json", {"True": [], "False": []})
        database_rows = [row for row in external if row["phase"] in {"db_up", "db_down"}]
        write(root / "database" / "attempt-predictions.json", [{
            "attempt_key": opaque_attempt(row),
            "operation": "read", "database_up": row["phase"] == "db_up",
            "predicted_database_caused_failure": {
                "ebpf": row["phase"] == "db_down", "native": None, "combined": row["phase"] == "db_down",
            },
            "static_endpoint_baseline": row["phase"] == "db_down",
        } for row in database_rows])
    if system == "otel_demo":
        write(root / "async-chains.json", {
            f"req-{phase}-{index}": {"sources": {"ebpf": {"status": "linked"}}}
            for phase in ("async_normal", "async_paused", "async_recovered") for index in range(1, 20)
        })
        write(root / "async-selection.json", {"control_attempts": 60, "selected_spans": 60})
    for source in evaluate_v3.SOURCES:
        write(root / "models" / source / "model.json", {
            "classes": {"read": {}}, "preparation_seconds": 0.1,
        })
        write(root / "models" / source / "forecast.json", {
            "classes": {"read": {
                "point": None, "identification_bounds": [0.5, 1.0],
                "uncertainty_bounds": [0.2, 1.0], "historical_reference_width_10pp": False,
            }}
        })
        projected = [{
            "attempt_key": opaque_attempt(row), "operation_id": "read", "phase": row["phase"],
            "state": row["state"],
            "proxy": None if row["phase"] == "target" and row["attempt_id"].endswith("-1") else True,
            "protocol_only": True,
            "oracle_fields_consumed": False,
        } for row in external]
        write(root / "projections" / f"{source}-final.json", projected)
    frozen = {}
    for source in evaluate_v3.SOURCES:
        for name in ("model.json", "forecast.json"):
            path = root / "models" / source / name
            frozen[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    write(root / "forecast-saved.json", {"saved_ns": 0, "sha256_by_path": frozen})
    write(root / "freeze-integrity.json", {"all_unchanged": True, "sha256_by_path": frozen})
    return counts


def test_evaluate_preserves_unknowns_and_scores_both_bounds(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    counts = campaign(tmp_path)
    monkeypatch.setattr(evaluate_v3, "PRIMARY_COUNTS", counts)
    result = evaluate(tmp_path)
    assert len(result["metrics"]) == 4
    row = result["metrics"][0]
    assert row["external"]["unknown"] == 1
    assert row["external"]["point"] is None
    assert row["projection"]["business_unknown"] == 1
    assert row["point_absolute_error"] is None
    assert row["empirical_worst_end_error"] == pytest.approx(0.5)
    assert row["nominal_worst_end_error"] == pytest.approx(0.8)
    assert row["nominal_vs_external_wilson_worst_end_error"] != row["nominal_worst_end_error"]
    assert row["accuracy_gate_applied"] is False
    assert result["confusion"]
    assert result["costs"]["traffic_blocks"][0]["requested_operations_per_second"] == 20
    assert result["controls"]["petclinic_database_prediction"]["attempts"] == 40
    assert any(row["predictor"] == "static_endpoint_baseline"
               for row in result["controls"]["petclinic_database_prediction"]["comparisons"])
    target_confusion = next(row for row in result["confusion"]
                            if row["source"] == "ebpf" and row["phase"] == "target")
    assert target_confusion["counts"] == {
        "source_true_external_true": 1, "source_unknown_external_unknown": 1,
    }
    assert Path(result["outputs"]["json"]).exists()


def test_evaluate_rejects_frozen_artifact_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    counts = campaign(tmp_path)
    monkeypatch.setattr(evaluate_v3, "PRIMARY_COUNTS", counts)
    path = tmp_path / "models" / "ebpf" / "forecast.json"
    path.write_text(path.read_text() + " ")
    with pytest.raises(ValueError, match="frozen artifact changed"):
        evaluate(tmp_path)


def test_evaluate_rejects_projection_that_consumed_oracle_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    counts = campaign(tmp_path)
    monkeypatch.setattr(evaluate_v3, "PRIMARY_COUNTS", counts)
    path = tmp_path / "projections" / "ebpf-final.json"
    rows = json.loads(path.read_text())
    rows[0]["oracle_fields_consumed"] = True
    write(path, rows)
    with pytest.raises(ValueError, match="no-oracle boundary"):
        evaluate(tmp_path)


def test_aggregate_requires_complete_population_and_keeps_unknown_mean(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    paths = []
    for system in evaluate_v3.SYSTEMS:
        for mode in evaluate_v3.MODES:
            for seed in evaluate_v3.SEEDS:
                root = tmp_path / f"{system}-{mode}-{seed}"
                counts = campaign(root, system, mode, seed)
                monkeypatch.setattr(evaluate_v3, "PRIMARY_COUNTS", counts)
                evaluate(root)
                paths.append(root)
    first = json.loads((paths[0] / "metrics-v3.json").read_text())
    first["costs"]["campaign_elapsed_seconds"] = None
    write(paths[0] / "metrics-v3.json", first)
    outputs = aggregate(paths, tmp_path / "aggregate")
    result = json.loads(Path(outputs["json"]).read_text())
    assert result["campaigns"] == 27
    assert result["summaries"][0]["mean_point_absolute_error"] is None
    assert result["summaries"][0]["point_error_known_seeds"] == 0
    assert result["accuracy_success_gate"] is None
    assert result["costs"]["primary_attempts"] == 27 * sum(counts.values())
    assert result["costs"]["campaign_elapsed_seconds"] is None
    assert result["costs"]["human_agent_seconds"] is None
    assert result["automatic_grouping"]
    assert result["petclinic_database_prediction"]
    assert result["otel_async_association"]
    async_normal = next(row for row in result["otel_async_association"]
                        if row["mode"] == "absent" and row["source"] == "ebpf"
                        and row["phase"] == "async_normal")
    assert async_normal["linked"] == 57
    assert async_normal["unknown"] == 3
    assert async_normal["immediate_outcome_unknown"] == 3
    assert result["per_attempt_confusion"]
    assert Path(outputs["csv"]).exists()
    assert Path(outputs["markdown"]).exists()
