import hashlib
import json
import copy
from pathlib import Path
import zipfile

import pytest

from ebpf_discovery.artifact_recovery_v5 import recover_declared_files, retain_unavailable
from ebpf_discovery.compact_transport_v5 import (
    extract_verified_compact, remove_verified_working_copy,
)
from ebpf_discovery.report_v5 import build, render, resolve_evaluation_reference


OBI_IMAGE = (
    "otel/ebpf-instrument:v0.15.2@"
    "sha256:101b5c773ac84545cac007ce3dbaf38bfb0e7091f26e813c08d649f35dca253e"
)


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attempts(result: dict, stage: str) -> list[dict]:
    by_key = {row["attempt_key"]: row for row in result["attempts"]}
    return [by_key[key] for key in result[f"{stage}_attempt_references"]]


def restored(report_dir: Path, attempt: dict) -> dict:
    return resolve_evaluation_reference(
        attempt["evaluation_reference"], report_dir / "evaluation-v5.json",
    )


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


def summary(root: Path, run_id: int, stage: str, complete=True, *, head_sha='a' * 40) -> tuple[Path, dict]:
    name = f"v5-summary-obi-{stage}-petclinic-absent-6-{run_id}"
    folder = root / str(run_id) / name
    status = {"run_id": str(run_id), "commit": head_sha, "collector": "obi",
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
        "commit": head_sha, "collector": "obi", "system": "petclinic",
        "mode": "absent", "seed": 6, "smoke": stage == "smoke",
        "full_artifact_name": full, "files_sha256": {
            "evaluation-v5.json": sha(folder / "evaluation-v5.json"),
            "status.json": sha(folder / "status.json")}})
    write(folder / "artifact-provenance.json", {
        "run_id": run_id, "repository": "MB3R-Lab/ebpf-model-discovery-experiments",
        "head_sha": head_sha, "artifact_id": run_id * 10,
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
    assert result["grid"]["declared_main_cells"] == 81
    assert result["grid"]["technically_complete_main_cells"] == 1
    assert restored(tmp_path / "report", attempts(result, "smoke")[0]) == smoke
    selected = {row["attempt_key"]: row for row in result["attempts"]}[
        result["selected_main_attempt_references"][0]
    ]
    assert restored(tmp_path / "report", selected) == main
    assert selected["independently_admitted"] is False


def test_scientific_details_survive_hash_bound_projection_and_render(tmp_path):
    from ebpf_discovery.evaluate_v5 import scientific_summaries

    folder, evaluation = summary(tmp_path / "inputs", 25, "main")
    old_row = copy.deepcopy(evaluation["evaluations"][0])
    evaluation.update(
        manual_baselines={"list": {"available": True, "prediction": .875,
            "basis": "same supplied semantics"}},
        database={"db_down": {"list": {"counts": {"success": 0, "failure": 4}}},
            "forecast_impact": [{"operation": "list", "healthy_state_11_prediction": 1,
                                  "database_down_prediction": 0, "prognostic_impact": 1}]},
        evidence={"graphs": {"ebpf": {"raw": {"list": {"available": True,
            "services": 2, "edges": 1, "endpoints": 0,
            "bering_outputs_present": {"observed": True}, "large_detail": "omit"}}}},
            "async": {"attempts": [{"attempt_id": "a", "source": "ebpf", "phase": "normal",
                "four_stage_causal_chain": "unknown", "proofs": ["not duplicated"]}]}},
        classes={"class_test_metrics": [{"source": "ebpf", "total": 8, "known": 4,
            "unknown": 4, "coverage": .5, "ari_labeled_known_subset": 4,
            "equivalent_to_base_family_assignment": True}]},
    )
    evaluation["scientific_summaries"] = scientific_summaries(evaluation)
    assert evaluation["evaluations"][0] == old_row
    assert "large_detail" not in evaluation["scientific_summaries"]["graphs"]["ebpf"]["raw"]["list"]
    assert "proofs" not in evaluation["scientific_summaries"]["causal_attempt_verdicts"][0]
    write(folder / "evaluation-v5.json", evaluation)
    manifest = json.loads((folder / "evaluation-manifest.json").read_text())
    manifest["files_sha256"]["evaluation-v5.json"] = sha(folder / "evaluation-v5.json")
    write(folder / "evaluation-manifest.json", manifest)
    declarations = declared(tmp_path / "declared.json", [run(25, "main")])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    projection = result["attempts"][0]["evaluation_projection"]
    assert projection["scientific_summaries"] == evaluation["scientific_summaries"]
    aggregate_path = tmp_path / "report/evaluation-v5.json"
    output = tmp_path / "report.md"
    render(aggregate_path, output)
    rendered = output.read_text()
    for text in ("same supplied semantics", "0.875", "Independent database controls",
                 "Frozen operation classification", "census of saved verdicts", "not retained"):
        assert text in rendered
    # Even a recomputed projection hash cannot replace its frozen source facts.
    projection["scientific_summaries"]["manual_baselines"]["list"]["prediction"] = .99
    unhashed = {key: value for key, value in projection.items() if key != "projection_sha256"}
    projection["projection_sha256"] = hashlib.sha256(json.dumps(
        unhashed, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    write(aggregate_path, result)
    with pytest.raises(ValueError, match="projection does not match source payload"):
        render(aggregate_path, tmp_path / "tampered.md")


def test_figures_copy_main_errors_and_preserve_unknowns_and_source_proofs(tmp_path):
    from ebpf_discovery.plot_v5 import display_value, saved_values

    summary(tmp_path / 'inputs', 1, 'smoke')
    folder, evaluation = summary(tmp_path / 'inputs', 2, 'main')
    row = evaluation['evaluations'][0]
    row['error'] = {'range': [0.0, .1], 'worst_end_error': .1}
    unknown = {**row, 'source': 'native', 'available': False, 'prediction': None,
               'forecast_interval': [0, 1], 'error': {'range': None, 'worst_end_error': None}}
    zero = {**row, 'source': 'combined', 'error': {'range': [0, 0], 'worst_end_error': 0}}
    evaluation['evaluations'] += [unknown, zero]
    write(folder / 'evaluation-v5.json', evaluation)
    manifest = json.loads((folder / 'evaluation-manifest.json').read_text())
    manifest['files_sha256']['evaluation-v5.json'] = sha(folder / 'evaluation-v5.json')
    write(folder / 'evaluation-manifest.json', manifest)
    declarations = declared(tmp_path / 'declared.json', [run(1, 'smoke'), run(2, 'main')],
                            blocked=[{'collector': 'coroot', 'system': 'petclinic',
                                      'mode': 'absent', 'seed': 6, 'reason': 'synthetic infrastructure block'}])
    build([tmp_path / 'inputs'], declarations, tmp_path / 'report')
    aggregate = tmp_path / 'report/evaluation-v5.json'
    values = saved_values(aggregate)
    assert len(values['rows']) == 3
    assert {item['run_id'] for item in values['rows']} == {2}
    assert values['grid']['declared_main_cells'] == 81
    assert len(values['grid']['blocked_main_cells']) == 1
    assert values['independent_admission']['performed_by_reporter'] is False
    assert values['rows'][0]['saved']['error'] == row['error']
    assert values['rows'][0]['evaluation_reference']['source_sha256'] == sha(folder / 'evaluation-v5.json')
    assert display_value(values['rows'][0]) == (.1, [0.0, .1], 1)
    assert display_value(values['rows'][1]) == (None, None, 1)
    assert display_value(values['rows'][2]) == (0, [0, 0], 1)
    # Reusing the independent hash-bound loader rejects corruption before a plot.
    reference = values['rows'][0]['evaluation_reference']
    (aggregate.parent / reference['path']).write_bytes(b'corrupted')
    with pytest.raises(ValueError, match='gzip proof mismatch'):
        saved_values(aggregate)


def test_figures_render_unknown_rows_without_collapsing_y_limits(tmp_path):
    from ebpf_discovery.plot_v5 import _figure

    _figure([{'seed': seed, 'saved': {'operation': 'operation', 'source': 'ebpf',
               'variant': 'raw', 'available': False,
               'error': {'range': None, 'worst_end_error': None},
               'actual_counts': {'success': 0, 'failure': 0, 'unknown': 3}}}
             for seed in (6, 7, 8)], 'Synthetic unknown example', tmp_path / 'unknown')
    svg = (tmp_path / 'unknown.svg').read_text(encoding='utf-8')
    assert svg.count('unknown; U=3') == 3
    for suffix in ('svg', 'png', 'pdf'):
        assert (tmp_path / ('unknown.' + suffix)).stat().st_size > 0


def test_failed_no_artifact_and_blocked_are_retained_not_coverage(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 3, "main", complete=False)
    declarations = declared(tmp_path / "declared.json", [run(3, "main"), run(4, "main", "partial")],
        [{"collector": "coroot", "system": "petclinic", "mode": "absent",
          "seed": 6, "reason": "synthetic infrastructure block"}])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    assert result["grid"]["technically_complete_main_cells"] == 0
    assert {row["reason"] for row in attempts(result, "main")} == {
        "source_evaluation_technically_incomplete", "compact_artifact_not_retained"}
    assert result["grid"]["blocked_main_cells"] == [
        ["coroot", "petclinic", "absent", 6, "synthetic infrastructure block"]]


def test_excluded_collector_cannot_reenter_active_grid(tmp_path: Path) -> None:
    excluded = {**run(1, "main"), "collector": "newrelic"}
    declarations = declared(tmp_path / "attempt.json", [excluded])
    with pytest.raises(ValueError):
        build([], declarations, tmp_path / "attempt-report")
    declarations = declared(tmp_path / "blocked.json", [], [
        {"collector": "newrelic", "system": "petclinic", "mode": "absent",
         "seed": 6, "reason": "obsolete access block"},
    ])
    with pytest.raises(ValueError):
        build([], declarations, tmp_path / "blocked-report")


def test_renderer_preserves_historical_stored_grid_count(tmp_path: Path) -> None:
    declarations = declared(tmp_path / "declared.json", [])
    result = build([], declarations, tmp_path / "report")
    assert result["grid"]["declared_main_cells"] == 81
    # A retained historical aggregate carries its own original grid boundary.
    result["grid"]["declared_main_cells"] = 108
    aggregate = tmp_path / "report/evaluation-v5.json"
    write(aggregate, result)
    output = tmp_path / "historical.md"
    render(aggregate, output)
    assert "108-cell main grid" in output.read_text()
    assert "81-cell main grid" not in output.read_text()


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


def test_historically_omitted_declared_file_is_retained_unavailable(
        tmp_path: Path) -> None:
    folder, evaluation = summary(tmp_path / "inputs", 18, "main")
    journal = b'{"attempt":1}\n'
    manifest = json.loads((folder / "evaluation-manifest.json").read_text())
    manifest["files_sha256"]["attempt-journal.jsonl"] = hashlib.sha256(
        journal).hexdigest()
    write(folder / "evaluation-manifest.json", manifest)
    provenance_path = folder / "artifact-provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance.update(full_artifact_id=None, full_artifact_digest=None,
                      full_artifact_expired=None)
    source = {
        "repository": provenance["repository"], "run_id": 18,
        "head_sha": "a" * 40,
        "compact_artifact_id": provenance["artifact_id"],
        "compact_artifact_name": provenance["name"],
        "compact_artifact_digest": provenance["digest"],
        "full_artifact_id": provenance["full_artifact_id"],
        "full_artifact_name": provenance["full_artifact_name"],
        "full_artifact_digest": provenance["full_artifact_digest"],
        "full_artifact_size_in_bytes": None,
    }
    proof = retain_unavailable(folder, [{
        "name": "attempt-journal.jsonl",
        "manifest_sha256": hashlib.sha256(journal).hexdigest(),
    }], source, "full_artifact_missing")
    proof_path = folder / "declared-file-recovery.json"
    provenance["declared_file_recovery"] = {
        "path": proof_path.name, "sha256": sha(proof_path),
        "status": proof["status"],
    }
    write(provenance_path, provenance)
    declarations = declared(tmp_path / "declared.json", [run(18, "main")])

    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")

    attempt = attempts(result, "main")[0]
    assert attempt["reason"] == "manifest_declared_file_unavailable"
    assert attempt["eligible_main_coverage"] is False
    assert restored(tmp_path / "report", attempt) == evaluation
    assert attempt["technical_complete_self_reported"] is True
    assert attempt["manifest_declared_transport_complete"] is False
    assert attempt["full_source_artifact_available"] is False
    assert attempt["independently_admitted"] is False
    assert attempt["missing_manifest_declared_files"] == proof["requested_files"]
    assert result["grid"]["technically_complete_main_cells"] == 0


def test_recovered_declared_file_and_full_source_are_revalidated(
        tmp_path: Path) -> None:
    folder, evaluation = summary(tmp_path / "inputs", 19, "main")
    journal = b'{"attempt":1}\n'
    manifest = json.loads((folder / "evaluation-manifest.json").read_text())
    manifest["files_sha256"]["attempt-journal.jsonl"] = hashlib.sha256(
        journal).hexdigest()
    write(folder / "evaluation-manifest.json", manifest)
    archive = tmp_path / "full.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("attempt-journal.jsonl", journal)
    full_digest = "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest()
    provenance_path = folder / "artifact-provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["full_artifact_digest"] = full_digest
    source = {
        "repository": provenance["repository"], "run_id": 19,
        "head_sha": "a" * 40,
        "compact_artifact_id": provenance["artifact_id"],
        "compact_artifact_name": provenance["name"],
        "compact_artifact_digest": provenance["digest"],
        "full_artifact_id": provenance["full_artifact_id"],
        "full_artifact_name": provenance["full_artifact_name"],
        "full_artifact_digest": full_digest,
        "full_artifact_size_in_bytes": archive.stat().st_size,
    }
    proof = recover_declared_files(folder, archive, source)
    proof_path = folder / "declared-file-recovery.json"
    provenance["declared_file_recovery"] = {
        "path": proof_path.name, "sha256": sha(proof_path),
        "status": proof["status"],
    }
    write(provenance_path, provenance)
    declarations = declared(tmp_path / "declared.json", [run(19, "main")])

    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")

    attempt = attempts(result, "main")[0]
    assert restored(tmp_path / "report", attempt) == evaluation
    assert attempt["eligible_main_coverage"] is True
    assert result["grid"]["technically_complete_main_cells"] == 1


def test_recovery_does_not_rematerialize_stream_verified_journal(tmp_path: Path) -> None:
    folder, _ = summary(tmp_path / "inputs", 19, "main")
    journal, other = b'{"attempt":1}\n', b"other\n"
    manifest_path = folder / "evaluation-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files_sha256"].update({
        "attempt-journal.jsonl": hashlib.sha256(journal).hexdigest(),
        "other.txt": hashlib.sha256(other).hexdigest(),
    })
    write(manifest_path, manifest)
    archive = tmp_path / "full.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("attempt-journal.jsonl", journal)
        bundle.writestr("other.txt", other)
    source = {
        "full_artifact_digest": "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest(),
        "full_artifact_size_in_bytes": archive.stat().st_size,
    }

    proof = recover_declared_files(
        folder, archive, source, {"attempt-journal.jsonl"})

    assert proof["status"] == "recovered"
    assert [row["name"] for row in proof["requested_files"]] == ["other.txt"]
    assert (folder / "other.txt").read_bytes() == other
    assert not (folder / "attempt-journal.jsonl").exists()


def test_stream_verified_nonmaterialized_journal_preserves_coverage(tmp_path: Path) -> None:
    folder, evaluation = summary(tmp_path / "inputs", 20, "main")
    journal = b'{"attempt":1}\n'
    manifest_path = folder / "evaluation-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files_sha256"]["attempt-journal.jsonl"] = hashlib.sha256(
        journal).hexdigest()
    write(manifest_path, manifest)
    archive = tmp_path / "compact.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in ("evaluation-manifest.json", "evaluation-v5.json", "status.json"):
            bundle.write(folder / name, name)
        bundle.writestr("attempt-journal.jsonl", journal)
    digest = "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest()
    proof = extract_verified_compact(archive, folder, expected_digest=digest)
    remove_verified_working_copy(archive, proof)
    provenance_path = folder / "artifact-provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["digest"] = digest
    provenance["compact_zip_verification"] = proof
    write(provenance_path, provenance)

    result = build(
        [tmp_path / "inputs"], declared(tmp_path / "declared.json", [run(20, "main")]),
        tmp_path / "report",
    )

    attempt = attempts(result, "main")[0]
    assert restored(tmp_path / "report", attempt) == evaluation
    assert attempt["eligible_main_coverage"] is True
    assert attempt["manifest_declared_transport_complete"] is True
    assert attempt["verified_nonmaterialized_manifest_files"] == [
        "attempt-journal.jsonl"]
    assert not (folder / "attempt-journal.jsonl").exists()


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
    attempt = attempts(result, "main")[0]
    assert restored(tmp_path / "report", attempt) == evaluation
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
    selected_item = {row["attempt_key"]: row for row in selected["attempts"]}[
        selected["selected_main_attempt_references"][0]
    ]
    assert selected_item["run_id"] == 9
    assert len(attempts(selected, "main")) == 2
    value = json.loads(selection.read_text())
    value["cells"][0]["reason_code"] = "best_accuracy"
    write(selection, value)
    with pytest.raises(ValueError, match="technical-only replacement"):
        build([tmp_path / "inputs"], declarations, tmp_path / "bad", selection_path=selection)


def test_declared_common_source_keeps_old_complete_results_and_requires_explicit_selection(tmp_path):
    summary(tmp_path/'inputs', 20, 'smoke', head_sha='a' * 40)
    _, old = summary(tmp_path/'inputs', 21, 'main', head_sha='a' * 40)
    current_folder, current = summary(tmp_path/'inputs', 22, 'main', head_sha='b' * 40)
    current['evaluations'][0].update(prediction=.01, forecast_interval=[.01, .01])
    write(current_folder/'evaluation-v5.json', current)
    current_manifest = json.loads((current_folder/'evaluation-manifest.json').read_text())
    current_manifest['files_sha256']['evaluation-v5.json'] = sha(current_folder/'evaluation-v5.json')
    write(current_folder/'evaluation-manifest.json', current_manifest)
    declarations = declared(tmp_path/'declared.json', [run(20, 'smoke'), run(21, 'main'), run(22, 'main')])
    value = json.loads(declarations.read_text())
    value['experiment_head'] = 'b' * 40
    write(declarations, value)
    unselected = build([tmp_path/'inputs'], declarations, tmp_path/'unselected')
    assert unselected['grid']['technically_complete_main_cells'] == 0
    selection = tmp_path/'selection.json'
    write(selection, {'policy': 'technical_replacement_only_no_outcome_selection', 'cells': [{
        'collector': 'obi', 'system': 'petclinic', 'mode': 'absent', 'seed': 6,
        'candidate_artifact_ids': [210, 220], 'candidate_run_ids': [21, 22],
        'selected_artifact_id': 220, 'reason_code': 'technical_common_source_replacement'}]})
    report = tmp_path/'selected'
    result = build([tmp_path/'inputs'], declarations, report, selection_path=selection)
    assert result['grid']['technically_complete_main_cells'] == 1
    old_row, new_row = attempts(result, 'main')
    smoke = attempts(result, 'smoke')[0]
    assert smoke['eligible_main_coverage'] is True and 'common_source_coverage_exclusion' not in smoke
    assert old_row['technical_complete_self_reported'] is new_row['technical_complete_self_reported'] is True
    assert old_row['eligible_main_coverage'] is False and new_row['eligible_main_coverage'] is True
    assert old_row['common_source_coverage_exclusion'] == {
        'rule': 'outside_predeclared_common_source', 'expected_head': 'b' * 40,
        'observed_head': 'a' * 40, 'previous_eligible_main_coverage': True, 'previous_reason': None}
    assert old_row['reason'] is None
    assert restored(report, old_row) == old and restored(report, new_row) == current
    assert result['selected_main_attempt_references'] == [new_row['attempt_key']]
    out = report/'report.md'
    render(report/'evaluation-v5.json', out)
    text = out.read_text(encoding='utf-8')
    assert 'Declared common source commit: `' + 'b' * 40 + '`' in text
    assert 'a' * 40 in text and 'outside_predeclared_common_source' in text


def test_common_source_does_not_allow_picking_between_two_complete_same_head_attempts(tmp_path):
    summary(tmp_path/'inputs', 23, 'main')
    summary(tmp_path/'inputs', 24, 'main')
    declarations = declared(tmp_path/'declared.json', [run(23, 'main'), run(24, 'main')])
    value = json.loads(declarations.read_text()); value['experiment_head'] = 'a' * 40
    write(declarations, value)
    selection = tmp_path/'selection.json'
    write(selection, {'policy': 'technical_replacement_only_no_outcome_selection', 'cells': [{
        'collector': 'obi', 'system': 'petclinic', 'mode': 'absent', 'seed': 6,
        'candidate_artifact_ids': [230, 240], 'candidate_run_ids': [23, 24],
        'selected_artifact_id': 240, 'reason_code': 'technical_common_source_replacement'}]})
    with pytest.raises(ValueError, match='technical-only replacement'):
        build([tmp_path/'inputs'], declarations, tmp_path/'report', selection_path=selection)


@pytest.mark.parametrize('observed_head', [None, ''])
def test_complete_unknown_source_cannot_count_in_explicit_common_source_grid(tmp_path, observed_head):
    _, original = summary(tmp_path/'inputs', 25, 'main', head_sha=observed_head)
    declarations = declared(tmp_path/'declared.json', [run(25, 'main')])
    legacy = build([tmp_path/'inputs'], declarations, tmp_path/'legacy')
    assert legacy['grid']['technically_complete_main_cells'] == 1
    value = json.loads(declarations.read_text()); value['experiment_head'] = 'b' * 40
    write(declarations, value)
    result = build([tmp_path/'inputs'], declarations, tmp_path/'report')
    assert result['grid']['technically_complete_main_cells'] == 0
    item = attempts(result, 'main')[0]
    assert item['eligible_main_coverage'] is False and item['technical_complete_self_reported'] is True
    assert item['common_source_coverage_exclusion']['rule'] == 'source_commit_unavailable'
    assert item['common_source_coverage_exclusion']['previous_eligible_main_coverage'] is True
    assert restored(tmp_path/'report', item) == original


@pytest.mark.parametrize('head', [None, '', 'b' * 7, 'g' * 40])
def test_explicit_common_head_must_name_a_full_commit(tmp_path, head):
    declarations = declared(tmp_path/'declared.json', [])
    value = json.loads(declarations.read_text()); value['experiment_head'] = head
    write(declarations, value)
    with pytest.raises(ValueError, match='full lowercase 40-character commit'):
        build([], declarations, tmp_path/'report')


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
    assert len(attempts(result, "main")) == 2
    assert attempts(result, "main")[0]["reason"] == "compact_artifact_not_retained"


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
    assert "81-cell main grid" in text and "Self-reported complete" in text
    assert "99 | unknown | product_ci | completed | failure | 101 | checks" in text
    assert "Human/agent preparation effort: unknown" in text
    assert restored(tmp_path / "report", result["attempts"][0])["classes"] == {
        "sentinel": "preserved-verbatim"}


def test_payload_is_lossless_deterministic_and_not_duplicated_inline(tmp_path: Path) -> None:
    _, evaluation = summary(tmp_path / "inputs", 20, "main", complete=False)
    declarations = declared(tmp_path / "declared.json", [run(20, "main")])
    first = build([tmp_path / "inputs"], declarations, tmp_path / "first")
    second = build([tmp_path / "inputs"], declarations, tmp_path / "second")
    first_attempt = first["attempts"][0]
    second_attempt = second["attempts"][0]

    assert first_attempt["technical_complete_self_reported"] is False
    assert restored(tmp_path / "first", first_attempt) == evaluation
    assert first_attempt["evaluation_reference"]["gzip_sha256"] == (
        second_attempt["evaluation_reference"]["gzip_sha256"]
    )
    assert first_attempt["evaluation_reference"]["source_sha256"] == sha(
        tmp_path / "inputs/20/v5-summary-obi-main-petclinic-absent-6-20/evaluation-v5.json"
    )
    aggregate_text = (tmp_path / "first/evaluation-v5.json").read_text(encoding="utf-8")
    assert '"evaluation": {' not in aggregate_text
    assert aggregate_text.count('"evaluation_reference"') == 1


def test_reference_tamper_and_stage_reference_tamper_are_rejected(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 21, "main")
    declarations = declared(tmp_path / "declared.json", [run(21, "main")])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    payload_path = tmp_path / "report" / result["attempts"][0]["evaluation_reference"]["path"]
    payload_path.write_bytes(payload_path.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="gzip proof mismatch"):
        render(tmp_path / "report/evaluation-v5.json", tmp_path / "bad.md")

    build([tmp_path / "inputs"], declarations, tmp_path / "report2")
    aggregate = json.loads((tmp_path / "report2/evaluation-v5.json").read_text())
    aggregate["smoke_attempt_references"] = aggregate["main_attempt_references"]
    write(tmp_path / "report2/evaluation-v5.json", aggregate)
    with pytest.raises(ValueError, match="canonical attempt reference"):
        render(tmp_path / "report2/evaluation-v5.json", tmp_path / "bad-stage.md")


@pytest.mark.parametrize("recompute_self_hash", [False, True])
def test_projection_cannot_diverge_from_source_payload(
        tmp_path: Path, recompute_self_hash: bool) -> None:
    summary(tmp_path / "inputs", 24, "main")
    declarations = declared(tmp_path / "declared.json", [run(24, "main")])
    build([tmp_path / "inputs"], declarations, tmp_path / "report")
    aggregate_path = tmp_path / "report/evaluation-v5.json"
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    projection = aggregate["attempts"][0]["evaluation_projection"]
    projection["evaluations"][0]["prediction"] = 0.99
    if recompute_self_hash:
        unhashed = {key: value for key, value in projection.items()
                    if key != "projection_sha256"}
        projection["projection_sha256"] = hashlib.sha256(json.dumps(
            unhashed, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")).hexdigest()
    write(aggregate_path, aggregate)
    with pytest.raises(ValueError, match="projection does not match source payload"):
        render(aggregate_path, tmp_path / "bad-projection.md")


def test_referenced_and_legacy_schemas_render_identical_tables(tmp_path: Path) -> None:
    summary(tmp_path / "inputs", 22, "smoke")
    summary(tmp_path / "inputs", 23, "main")
    declarations = declared(tmp_path / "declared.json", [run(22, "smoke"), run(23, "main")])
    result = build([tmp_path / "inputs"], declarations, tmp_path / "report")
    new_out = tmp_path / "new.md"
    render(tmp_path / "report/evaluation-v5.json", new_out)

    legacy = copy.deepcopy(json.loads(
        (tmp_path / "report/evaluation-v5.json").read_text(encoding="utf-8")
    ))
    legacy["schema_version"] = "evaluation-v5-saved-aggregate"
    for item in legacy["attempts"]:
        item["evaluation"] = resolve_evaluation_reference(
            item["evaluation_reference"], tmp_path / "report/evaluation-v5.json",
        )
    legacy["smoke_attempts"] = [item for item in legacy["attempts"]
                                if item["stage"] == "smoke"]
    legacy["main_attempts"] = [item for item in legacy["attempts"]
                               if item["stage"] == "main"]
    legacy["selected_main_evaluations"] = [
        next(item for item in legacy["attempts"] if item["attempt_key"] == key)
        for key in legacy["selected_main_attempt_references"]
    ]
    for field in ("smoke_attempt_references", "main_attempt_references",
                  "selected_main_attempt_references", "evaluation_payload_manifest"):
        legacy.pop(field, None)
    write(tmp_path / "legacy.json", legacy)
    old_out = tmp_path / "old.md"
    render(tmp_path / "legacy.json", old_out)

    new_tables = [line for line in new_out.read_text().splitlines() if line.startswith("|")]
    old_tables = [line for line in old_out.read_text().splitlines() if line.startswith("|")]
    assert new_tables == old_tables
