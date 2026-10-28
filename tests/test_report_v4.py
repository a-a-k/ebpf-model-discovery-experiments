import json
import sys

import pytest

from ebpf_discovery.report_v4 import main, render


def campaign(complete=True):
    return {
        "root": "/retained/run", "system": "otel_demo", "mode": "full", "seed": 6,
        "original_campaign_root": "/runner/original/campaign",
        "status": {"run_id": "123", "status": "acquisition_complete"},
        "saved_evaluation_provenance": {
            "run_id": "123", "head_sha": "deadbeef", "artifact_id": 41,
            "artifact_name": "v4-summary-otel_demo-full-6-123", "artifact_digest": "sha256:summary",
            "full_artifact_id": 40, "full_artifact_name": "v4-otel_demo-full-6-123",
            "full_artifact_digest": "sha256:full", "evaluation_sha256": "evalsha",
            "manifest_sha256": "manifestsha", "full_originals_reverified_by_report_job": False,
        },
        "complete_for_evaluation": complete, "counts": {"primary": 34800},
        "evaluations": [{"operation": "browse", "source": "ebpf", "variant": "raw",
            "available": True, "point_prediction": .75, "forecast_interval": [.7, .8],
            "actual_target_success_counts": {"true": 7, "false": 2, "none": 1},
            "observed_empirical_bounds": [.7, .8], "error": {"worst_end_error": .05},
            "graph_sha256": "abc"}],
        "database": {"db_up": {"browse": {"counts": {"success": 3, "failure": 1,
            "unknown": 0, "total": 4}}}, "db_down": {"browse": {"counts": {"success": 0,
            "failure": 3, "unknown": 1, "total": 4}}}, "forecast_impact": [{
                "operation": "browse", "source": "ebpf", "variant": "raw",
                "structural_graph_available": True, "healthy_state_11_prediction": 1.0,
                "database_down_prediction": 0.0, "prognostic_impact": 1.0,
                "comparison": "healthy_state_11_minus_database_down",
                "counted_as_accuracy_benefit": False}]},
        "manual_baselines": {"browse": {"available": True, "prediction": .875,
            "by_state": {"11": 1, "10": 1, "01": 1, "00": 0}, "basis": "declared contract",
            "database": {"available": True, "database_down_prediction": 0,
                         "basis": "declared unconditional selected database requirement"}}},
        "classes": {"class_test_metrics": [{"source": "ebpf", "variant": "raw", "total": 10,
            "known": 8, "unknown": 2, "coverage": .8, "ari_labeled_known_subset": 8,
            "ari_on_known_subset": .6, "unknowns_assigned_one_class": False,
            "labels_used_after_prediction_only": True}]},
        "async": {"paused_snapshot": {"available": True, "records": 2,
            "states": {"pending": 2}, "paused_absence_is_failure": False}},
        "evidence": {"cross_guest": {"ebpf": {"exact_parent_links": 4,
            "invalid_identity_candidates": 0, "placement_coverage": {"known_guest_observations": 9},
            "header_verdicts": {"corroborated_same_planned_header": 4}}},
            "async": {"attempts": [{"four_stage_causal_chain": "unknown"}]}},
        "cost": {"campaign_elapsed_seconds": 12, "toolchain_clone_seconds": None,
            "toolchain_build_seconds": 4, "shared_input_preparation_seconds": 1,
            "toolchain_command_seconds": 3, "bering_replay_command_seconds": 2,
            "bering_child_peak_rss_kib": 100, "infrastructure_time_fields": None,
            "manual_preparation": {"measured": False, "reason": "not instrumented"}},
    }


def aggregate(campaigns):
    return {"schema_version": "evaluation-v4-aggregate", "campaigns": campaigns,
            "grid": {"expected_cells": 27, "selected_unambiguous_cells": 1,
                     "retained_campaign_attempts": len(campaigns), "missing_cells": [["x", "y", 7]]},
            "selection": {"provided": True},
            "technical_replacements": [{"cell": ["otel_demo", "full", 6],
                "selected_root": "/retained/run", "excluded_roots": ["/failed"],
                "reason_code": "technical_incomplete_original"}],
            "ambiguous_duplicate_cells": []}


def test_report_copies_saved_tables_and_marks_unknown_cost(tmp_path):
    source = tmp_path / "evaluation-v4.json"
    source.write_text(json.dumps(aggregate([campaign()])), encoding="utf-8")
    out = tmp_path / "report-v4.md"
    result = render(source, out)
    text = out.read_text(encoding="utf-8")
    assert result["attempts"] == 1
    assert "All retained attempts (not all are necessarily selected)" in text
    assert "v4-summary-otel_demo-full-6-123" in text
    assert "sha256:full" in text and "evalsha" in text and "manifestsha" in text
    assert "technical_incomplete_original" in text
    assert "0.7, 0.8" in text and "7 | 2 | 1" in text
    assert "healthy_state_11_minus_database_down" in text
    assert "declared contract" in text
    assert "0.8" in text and "0.6" in text
    assert "pending=2" in text
    assert "corroborated_same_planned_header=4" in text
    assert "linked attempt rows retained" in text
    assert "unknown | 4" in text  # unavailable clone seconds is not rendered as zero


def test_report_retains_excluded_incomplete_attempt(tmp_path):
    selected, failed = campaign(), campaign(False)
    failed["root"] = "/failed"
    failed["status"] = {"run_id": "122", "status": "technical_failure"}
    source = tmp_path / "evaluation-v4.json"
    source.write_text(json.dumps(aggregate([selected, failed])), encoding="utf-8")
    out = tmp_path / "report-v4.md"
    render(source, out)
    text = out.read_text(encoding="utf-8")
    assert "122 | otel_demo | full | 6 | false | technical_failure | /failed" in text
    assert "Every retained campaign is listed as an attempt" in text


def test_statusless_saved_attempt_uses_actual_saved_provenance_schema(tmp_path):
    failed = campaign(False)
    failed["status"] = {}
    failed["saved_evaluation_provenance"] = {
        "run_id": "987", "head_sha": "feedface", "artifact_id": 52,
        "artifact_name": "v4-summary-otel_demo-full-6-987", "artifact_digest": "sha256:compact",
        "full_artifact_id": 51, "full_artifact_name": "v4-otel_demo-full-6-987",
        "full_artifact_digest": "sha256:original", "evaluation_sha256": "saved-eval",
        "manifest_sha256": "saved-manifest", "full_originals_reverified_by_report_job": False,
    }
    source = tmp_path / "evaluation-v4.json"
    source.write_text(json.dumps(aggregate([failed])), encoding="utf-8")
    out = tmp_path / "report-v4.md"
    render(source, out)
    text = out.read_text(encoding="utf-8")
    assert "987 | otel_demo | full | 6 | false | unknown" in text
    assert "52 | v4-summary-otel_demo-full-6-987 | sha256:compact" in text
    assert "51 | v4-otel_demo-full-6-987 | sha256:original" in text


def test_cli_requires_actions(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(sys, "argv", ["report_v4", "--aggregate", str(tmp_path / "input.json"),
                                      "--out", str(tmp_path / "report.md")])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
