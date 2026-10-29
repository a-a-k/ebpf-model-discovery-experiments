import hashlib
import json
from pathlib import Path

import pytest

from ebpf_discovery.report_v5 import build, render


OBI_IMAGE = (
    "otel/ebpf-instrument:v0.15.2@"
    "sha256:101b5c773ac84545cac007ce3dbaf38bfb0e7091f26e813c08d649f35dca253e"
)


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def declared(path: Path, runs: list[dict], blocked=None) -> Path:
    write(path, {
        "schema_version": "v5-report-declarations", "attempt_runs": runs,
        "related_runs": [{"run_id": 99, "role": "product_ci",
                          "repository": "MB3R-Lab/Bering", "note": "exact-head CI"}],
        "blocked_main_cells": blocked or [],
    })
    return path


def run(run_id: int, stage: str, mode="absent") -> dict:
    return {"run_id": run_id, "collector": "obi", "stage": stage,
            "cells": [{"system": "petclinic", "mode": mode, "seed": 6}],
            "note": "declared attempt"}


def summary(root: Path, run_id: int, stage: str, complete=True) -> tuple[Path, dict]:
    name = f"v5-summary-obi-{stage}-petclinic-absent-6-{run_id}"
    folder = root / str(run_id) / name
    status = {"run_id": str(run_id), "commit": "a" * 40, "collector": "obi",
              "system": "petclinic", "mode": "absent", "seed": 6,
              "smoke": stage == "smoke",
              "status": ("smoke_complete" if stage == "smoke" else "acquisition_complete")
                        if complete else "technical_failure"}
    evaluation = {
        "schema_version": "evaluation-v5", "collector": "obi", "system": "petclinic",
        "mode": "absent", "seed": 6, "smoke": stage == "smoke", "status": status,
        "complete_for_evaluation": complete,
        "smoke_technical_pass": stage == "smoke" and complete,
        "primary_series_result": stage == "main" and complete,
        "acquisition": {"valid": complete,
            "problems": [] if complete else ["capture_incomplete"],
            "provenance": {"collector": "obi", "source_domain": "ebpf-obi"},
            "positive_control": {"collector": "obi"},
            "final_drain": {"collector": "obi", "source_version": "v0.15.2"}},
        "evaluations": [{"operation": "list", "source": "ebpf", "variant": "raw",
            "available": complete, "prediction": .75 if complete else None,
            "forecast_interval": [.7, .8] if complete else None,
            "actual_target_success_counts": {"true": 7, "false": 2, "none": 1},
            "reason": None if complete else "campaign_technical_validation_failed"}],
        "classes": {"sentinel": "preserved-verbatim"},
        "async": {"phase": {"available": False, "reason": "unknown"}},
        "cost": {"campaign_elapsed_seconds": 12, "toolchain_build_seconds": None,
                 "manual_preparation": {"measured": False, "reason": "unknown"}},
    }
    write(folder / "evaluation-v5.json", evaluation)
    write(folder / "status.json", status)
    write(folder / "observations/collector.json", {
        "schema": "collector-lifecycle-v5", "collector": "obi",
        "source_domain": "ebpf-obi", "source_version": "v0.15.2",
        "source_commit": None, "image": OBI_IMAGE})
    full = name.replace("v5-summary-", "campaign-v5-", 1)
    write(folder / "evaluation-manifest.json", {
        "schema_version": "v5-cell-summary-manifest", "run_id": str(run_id),
        "commit": "a" * 40, "collector": "obi", "system": "petclinic",
        "mode": "absent", "seed": 6, "smoke": stage == "smoke",
        "full_artifact_name": full, "files_sha256": {
            "evaluation-v5.json": sha(folder / "evaluation-v5.json"),
            "status.json": sha(folder / "status.json")}})
    write(folder / "artifact-provenance.json", {
        "run_id": run_id, "repository": "MB3R-Lab/ebpf-model-discovery-experiments",
        "head_sha": "a" * 40, "artifact_id": run_id * 10,
        "name": name, "digest": f"sha256:summary-{run_id}", "expired": False,
        "full_artifact_id": run_id * 10 + 1, "full_artifact_name": full,
        "full_artifact_digest": f"sha256:full-{run_id}", "full_artifact_expired": False,
        "compact_zip_verification": {
            "expected_sha256": f"sha256:summary-{run_id}",
            "computed_sha256": f"sha256:summary-{run_id}",
            "received_bytes": 123, "safe_extract": True}})
    return folder, evaluation


def test_smoke_is_separate_and_main_evaluation_is_verbatim(tmp_path: Path) -> None:
    _, smoke = summary(tmp_path / "inputs", 1, "smoke")
    _, main = summary(tmp_path / "inputs", 2, "main")
    declarations = declared(tmp_path / "declared.json", [run(1, "smoke"), run(2, "main")])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    assert result["grid"]["declared_main_cells"] == 108
    assert result["grid"]["technically_complete_main_cells"] == 1
    assert result["smoke_attempts"][0]["evaluation"] == smoke
    assert result["selected_main_evaluations"][0]["evaluation"] == main
    assert result["selected_main_evaluations"][0]["independently_admitted"] is False


def test_failed_no_artifact_and_blocked_are_retained_not_coverage(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 3, "main", complete=False)
    declarations = declared(tmp_path / "declared.json", [run(3, "main"), run(4, "main", "partial")],
        [{"collector": "newrelic", "system": "petclinic", "mode": "absent",
          "seed": 6, "reason": "license unavailable"}])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    assert result["grid"]["technically_complete_main_cells"] == 0
    assert {row["reason"] for row in result["main_attempts"]} == {
        "source_evaluation_technically_incomplete", "compact_artifact_not_retained"}
    assert result["grid"]["blocked_main_cells"] == [
        ["newrelic", "petclinic", "absent", 6, "license unavailable"]]


def test_hash_stage_and_source_pin_mismatches_are_rejected(tmp_path: Path) -> None:
    folder, _ = summary(tmp_path / "one", 5, "main")
    declarations = declared(tmp_path / "one.json", [run(5, "main")])
    (folder / "status.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="compact hash mismatch"):
        build([tmp_path / "one"], declarations, tmp_path / "out1")

    summary(tmp_path / "two", 6, "main")
    declarations = declared(tmp_path / "two.json", [run(6, "smoke")])
    with pytest.raises(ValueError, match="same cell/stage"):
        build([tmp_path / "two"], declarations, tmp_path / "out2")

    folder, _ = summary(tmp_path / "three", 7, "main")
    value = json.loads((folder / "observations/collector.json").read_text())
    value["image"] = "otel/ebpf-instrument:unpinned"
    write(folder / "observations/collector.json", value)
    declarations = declared(tmp_path / "three.json", [run(7, "main")])
    with pytest.raises(ValueError, match="source pin mismatch"):
        build([tmp_path / "three"], declarations, tmp_path / "out3")


def test_status_identity_and_compact_zip_proof_are_cross_checked(tmp_path: Path) -> None:
    folder, _ = summary(tmp_path / "inputs", 14, "main")
    declarations = declared(tmp_path / "declared.json", [run(14, "main")])
    status = json.loads((folder / "status.json").read_text())
    status["commit"] = "b" * 40
    write(folder / "status.json", status)
    manifest = json.loads((folder / "evaluation-manifest.json").read_text())
    manifest["files_sha256"]["status.json"] = sha(folder / "status.json")
    write(folder / "evaluation-manifest.json", manifest)
    with pytest.raises(ValueError, match="status run/commit/stage mismatch"):
        build([tmp_path / "inputs"], declarations, tmp_path / "bad-status")

    folder, _ = summary(tmp_path / "zip", 15, "main")
    declarations = declared(tmp_path / "zip.json", [run(15, "main")])
    provenance = json.loads((folder / "artifact-provenance.json").read_text())
    provenance["compact_zip_verification"]["computed_sha256"] = "sha256:not-the-api-digest"
    write(folder / "artifact-provenance.json", provenance)
    with pytest.raises(ValueError, match="not byte-verified"):
        build([tmp_path / "zip"], declarations, tmp_path / "bad-zip")


def test_available_compact_with_missing_full_is_retained_but_not_coverage(tmp_path: Path) -> None:
    folder, evaluation = summary(tmp_path / "inputs", 16, "main", complete=True)
    provenance = json.loads((folder / "artifact-provenance.json").read_text())
    provenance.update(full_artifact_id=None, full_artifact_digest=None,
                      full_artifact_expired=None)
    write(folder / "artifact-provenance.json", provenance)
    declarations = declared(tmp_path / "declared.json", [run(16, "main")])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    attempt = result["main_attempts"][0]
    assert attempt["evaluation"] == evaluation
    assert attempt["technical_complete_self_reported"] is True
    assert attempt["full_source_artifact_available"] is False
    assert attempt["eligible_main_coverage"] is False
    assert attempt["reason"] == "full_artifact_missing"
    assert result["grid"]["technically_complete_main_cells"] == 0


def test_same_declared_run_cell_cannot_silently_overwrite_an_artifact(tmp_path: Path) -> None:
    summary(tmp_path / "first", 17, "main")
    second, _ = summary(tmp_path / "second", 17, "main")
    provenance = json.loads((second / "artifact-provenance.json").read_text())
    provenance.update(artifact_id=171, full_artifact_id=172)
    write(second / "artifact-provenance.json", provenance)
    declarations = declared(tmp_path / "declared.json", [run(17, "main")])
    with pytest.raises(ValueError, match="same declared run/cell"):
        build([tmp_path / "first", tmp_path / "second"], declarations, tmp_path / "bad")


def test_duplicate_requires_exact_technical_selection(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 8, "main", complete=False)
    summary(tmp_path / "inputs", 9, "main", complete=True)
    declarations = declared(tmp_path / "declared.json", [run(8, "main"), run(9, "main")])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "unselected")
    assert result["grid"]["technically_complete_main_cells"] == 0
    selection = tmp_path / "selection.json"
    write(selection, {"policy": "technical_replacement_only_no_outcome_selection", "cells": [{
        "collector": "obi", "system": "petclinic", "mode": "absent", "seed": 6,
        "candidate_artifact_ids": [80, 90], "selected_artifact_id": 90,
        "candidate_run_ids": [8, 9],
        "reason_code": "technical_incomplete_original"}]})
    selected = build([tmp_path / "inputs"], declarations, tmp_path / "selected",
                     selection_path=selection)
    assert selected["grid"]["technically_complete_main_cells"] == 1
    assert selected["selected_main_evaluations"][0]["run_id"] == 9
    assert len(selected["main_attempts"]) == 2
    value = json.loads(selection.read_text())
    value["cells"][0]["reason_code"] = "best_accuracy"
    write(selection, value)
    with pytest.raises(ValueError, match="technical-only replacement"):
        build([tmp_path / "inputs"], declarations, tmp_path / "bad", selection_path=selection)


def test_selection_cannot_be_applied_to_a_single_attempt(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 11, "main", complete=True)
    declarations = declared(tmp_path / "declared.json", [run(11, "main")])
    selection = tmp_path / "selection.json"
    write(selection, {"policy": "technical_replacement_only_no_outcome_selection", "cells": [{
        "collector": "obi", "system": "petclinic", "mode": "absent", "seed": 6,
        "candidate_artifact_ids": [110], "selected_artifact_id": 110,
        "candidate_run_ids": [11],
        "reason_code": "technical_only_complete_attempt"}]})
    with pytest.raises(ValueError, match="technical-only replacement"):
        build([tmp_path / "inputs"], declarations, tmp_path / "bad", selection_path=selection)


def test_technical_selection_retains_a_prior_no_artifact_attempt(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 13, "main", complete=True)
    declarations = declared(tmp_path / "declared.json", [run(12, "main"), run(13, "main")])
    selection = tmp_path / "selection.json"
    write(selection, {"policy": "technical_replacement_only_no_outcome_selection", "cells": [{
        "collector": "obi", "system": "petclinic", "mode": "absent", "seed": 6,
        "candidate_artifact_ids": [130], "selected_artifact_id": 130,
        "candidate_run_ids": [12, 13], "reason_code": "technical_no_artifact_original"}]})
    result = build([tmp_path / "inputs"], declarations, tmp_path / "selected",
                   selection_path=selection)
    assert result["grid"]["technically_complete_main_cells"] == 1
    assert len(result["main_attempts"]) == 2
    assert result["main_attempts"][0]["reason"] == "compact_artifact_not_retained"


def test_renderer_keeps_unknown_cost_and_actions_failure(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 10, "main")
    declarations = declared(tmp_path / "declared.json", [run(10, "main")])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    costs = tmp_path / "costs.json"
    write(costs, {"schema_version": "v5-actions-costs", "human_agent_seconds": None,
        "current_report_job_tail_seconds": None, "runs": [{"run_id": 99,
        "role": "product_ci", "status": "completed", "conclusion": "failure",
        "artifacts": [], "jobs": [{"id": 101, "name": "checks", "status": "completed",
        "conclusion": "failure", "elapsed_seconds": None}]}]})
    out = tmp_path / "report.md"
    assert render(tmp_path / "report/evaluation-v5.json", out, costs)["attempts"] == 1
    text = out.read_text(encoding="utf-8")
    assert "108" in text and "Self-reported complete" in text
    assert "99 | unknown | product_ci | completed | failure | 101 | checks" in text
    assert "Human/agent preparation effort: unknown" in text
    assert result["attempts"][0]["evaluation"]["classes"] == {
        "sentinel": "preserved-verbatim"}
