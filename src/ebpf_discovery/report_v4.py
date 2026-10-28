"""Markdown tables copied from a saved protocol-v4 evaluation aggregate."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _cell(value) -> str:
    if value is None:
        return "unknown"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (list, tuple)):
        return ", ".join(_cell(item) for item in value) if value else "none"
    if isinstance(value, dict):
        return "; ".join(f"{key}={_cell(item)}" for key, item in sorted(value.items())) if value else "none"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list]) -> list[str]:
    result = ["| " + " | ".join(headers) + " |",
              "|" + "|".join("---" for _ in headers) + "|"]
    result.extend("| " + " | ".join(_cell(value) for value in row) + " |" for row in rows)
    if not rows:
        result.append("| " + " | ".join(["unavailable"] + ["unknown"] * (len(headers) - 1)) + " |")
    return result


def _identity(campaign: dict) -> tuple:
    status = campaign.get("status") or {}
    provenance = campaign.get("saved_evaluation_provenance") or {}
    return (status.get("run_id") or provenance.get("run_id"), campaign.get("system"),
            campaign.get("mode"), campaign.get("seed"), campaign.get("root"))


def _heading(lines: list[str], title: str) -> None:
    lines.extend(["", f"## {title}", ""])


def render(aggregate: Path, out: Path, costs: Path | None = None) -> dict:
    payload = _read(aggregate)
    if payload.get("schema_version") != "evaluation-v4-aggregate":
        raise ValueError("report_v4 requires an evaluation-v4 aggregate")
    campaigns = payload.get("campaigns")
    if not isinstance(campaigns, list):
        raise ValueError("aggregate campaigns must be a list")
    cost_payload = _read(costs) if costs else None
    out.parent.mkdir(parents=True, exist_ok=True)
    aggregate_link = os.path.relpath(aggregate.resolve(), out.parent.resolve()).replace("\\", "/")
    lines = [
        "# Protocol-v4 saved evaluation report",
        "",
        f"Aggregate input: [`evaluation-v4.json`]({aggregate_link})",
        "",
        "This report copies stored evaluation metrics and descriptively counts retained causal verdicts. It introduces no threshold, cross-campaign pooling, relinking, refit, or new forecast.",
        "Every retained campaign is listed as an attempt; selection metadata determines evaluation inclusion.",
    ]
    if costs:
        cost_link = os.path.relpath(costs.resolve(), out.parent.resolve()).replace("\\", "/")
        lines.extend(["", f"Optional saved cost input: [`costs-v4.json`]({cost_link})"])

    grid = payload.get("grid") or {}
    _heading(lines, "Grid and retained attempts")
    lines += _table(["Stored field", "Value"], [
        ["expected_cells", grid.get("expected_cells")],
        ["selected_unambiguous_cells", grid.get("selected_unambiguous_cells")],
        ["retained_campaign_attempts", grid.get("retained_campaign_attempts")],
        ["expected_primary_total", grid.get("expected_primary_total")],
        ["selected_primary_total", grid.get("selected_primary_total")],
        ["retained_attempt_primary_total", grid.get("retained_attempt_primary_total")],
        ["missing_cells", grid.get("missing_cells")],
    ])
    lines.extend(["", "All retained attempts (not all are necessarily selected):", ""])
    attempt_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, root = _identity(campaign)
        attempt_rows.append([run_id, system, mode, seed, campaign.get("complete_for_evaluation"),
                             (campaign.get("status") or {}).get("status"), root,
                             (campaign.get("counts") or {}).get("primary")])
    lines += _table(["Run", "System", "Mode", "Seed", "Complete", "Status", "Retained root", "Primary"],
                    attempt_rows)
    lines.extend(["", "Saved artifact provenance:", ""])
    provenance_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, root = _identity(campaign)
        item = campaign.get("saved_evaluation_provenance") or {}
        provenance_rows.append([
            run_id, system, mode, seed, item.get("head_sha"), item.get("artifact_id"),
            item.get("artifact_name"), item.get("artifact_digest"), item.get("full_artifact_id"),
            item.get("full_artifact_name"), item.get("full_artifact_digest"),
            item.get("evaluation_sha256"), item.get("manifest_sha256"),
            campaign.get("original_campaign_root"), root,
            item.get("full_originals_reverified_by_report_job"),
        ])
    lines += _table([
        "Run", "System", "Mode", "Seed", "Head SHA", "Summary artifact ID", "Summary artifact",
        "Summary digest", "Full artifact ID", "Full artifact", "Full digest", "Evaluation SHA-256",
        "Manifest SHA-256", "Original campaign root", "Retained compact root", "Full originals reverified",
    ], provenance_rows)

    _heading(lines, "Selection and technical replacements")
    selection = payload.get("selection") or {}
    lines += _table(["Stored field", "Value"], [[key, value] for key, value in sorted(selection.items())])
    lines.extend(["", "Technical replacements:", ""])
    lines += _table(["Cell", "Selected root", "Excluded roots", "Reason"], [
        [item.get("cell"), item.get("selected_root"), item.get("excluded_roots"), item.get("reason_code")]
        for item in payload.get("technical_replacements") or []])
    lines.extend(["", "Ambiguous duplicate cells (unscored unless explicitly selected):", ""])
    lines += _table(["Cell", "Candidate roots", "Reason"], [
        [item.get("cell"), item.get("candidate_roots"), item.get("reason")]
        for item in payload.get("ambiguous_duplicate_cells") or []])

    _heading(lines, "Per-attempt forecasts and external outcomes")
    forecast_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        for row in campaign.get("evaluations") or []:
            counts = row.get("actual_target_success_counts") or row.get("actual_counts") or {}
            error = row.get("error") or {}
            forecast_rows.append([
                run_id, system, mode, seed, campaign.get("complete_for_evaluation"),
                row.get("operation"), row.get("source"), row.get("variant"), row.get("available"),
                row.get("point_prediction", row.get("prediction")), row.get("forecast_interval"),
                counts.get("true", counts.get("success")), counts.get("false", counts.get("failure")),
                counts.get("none", counts.get("unknown")), row.get("observed_empirical_bounds"),
                error.get("worst_end_error"), row.get("reason"), row.get("graph_sha256"),
            ])
    lines += _table([
        "Run", "System", "Mode", "Seed", "Complete", "Operation", "Source", "Variant", "Available",
        "Forecast", "Forecast interval", "Actual true", "Actual false", "Actual unknown",
        "External bounds", "Worst-end error", "Unavailable reason", "Graph SHA-256",
    ], forecast_rows)

    _heading(lines, "Database up/down evidence")
    database_count_rows, database_impact_rows = [], []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        database = campaign.get("database") or {}
        for phase in ("db_up", "db_down"):
            for operation, entry in (database.get(phase) or {}).items():
                counts = (entry or {}).get("counts") or {}
                database_count_rows.append([run_id, system, mode, seed, phase, operation,
                                            counts.get("success"), counts.get("failure"), counts.get("unknown"),
                                            counts.get("total")])
        for item in database.get("forecast_impact") or []:
            database_impact_rows.append([
                run_id, system, mode, seed, item.get("operation"), item.get("source"), item.get("variant"),
                item.get("structural_graph_available"), item.get("healthy_state_11_prediction"),
                item.get("database_down_prediction"), item.get("prognostic_impact"), item.get("comparison"),
                item.get("counted_as_accuracy_benefit"),
            ])
    lines += _table(["Run", "System", "Mode", "Seed", "Phase", "Operation", "Success", "Failure", "Unknown", "Total"],
                    database_count_rows)
    lines.extend(["", "Stored forecast impact (healthy state 11 versus database down):", ""])
    lines += _table(["Run", "System", "Mode", "Seed", "Operation", "Source", "Variant", "Graph available",
                     "Healthy 11", "DB down", "Impact", "Comparison", "Accuracy benefit"], database_impact_rows)

    _heading(lines, "Strong manual baselines")
    baseline_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        for operation, item in (campaign.get("manual_baselines") or {}).items():
            database = item.get("database") or {}
            baseline_rows.append([run_id, system, mode, seed, operation, item.get("available"),
                                  item.get("prediction"), item.get("by_state"),
                                  database.get("available"), database.get("database_down_prediction"),
                                  database.get("reason", database.get("basis")), item.get("basis")])
    lines += _table(["Run", "System", "Mode", "Seed", "Operation", "Available", "Prediction", "By state",
                     "DB baseline available", "DB-down prediction", "DB basis/reason", "Baseline basis"], baseline_rows)

    _heading(lines, "Frozen class evaluation")
    class_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        classes = campaign.get("classes") or {}
        for item in classes.get("class_test_metrics") or []:
            class_rows.append([run_id, system, mode, seed, item.get("source"), item.get("variant"),
                               item.get("total"), item.get("known"), item.get("unknown"), item.get("coverage"),
                               item.get("ari_labeled_known_subset"), item.get("ari_on_known_subset"),
                               item.get("unknowns_assigned_one_class"), item.get("labels_used_after_prediction_only")])
        if not classes.get("class_test_metrics"):
            class_rows.append([run_id, system, mode, seed, "unavailable", "unavailable", None, None, None,
                               None, None, None, None, classes.get("reason")])
    lines += _table(["Run", "System", "Mode", "Seed", "Source", "Variant", "Total", "Known", "Unknown",
                     "Coverage", "ARI labeled known", "ARI known subset", "Unknowns merged", "Labels after prediction/reason"],
                    class_rows)

    _heading(lines, "Asynchronous persistence states")
    async_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        for phase, item in (campaign.get("async") or {}).items():
            async_rows.append([run_id, system, mode, seed, phase, item.get("available"), item.get("records"),
                               item.get("states"), item.get("paused_absence_is_failure"), item.get("reason")])
    lines += _table(["Run", "System", "Mode", "Seed", "Async phase", "Available", "Records", "Stored states",
                     "Paused absence is failure", "Reason"], async_rows)
    lines.extend(["", "`async_paused` identifies requests issued while the consumer was paused; it does not claim completion during the pause.",
                  "The paused SQL snapshot and the separate after-resume/recovered verification remain distinct external observations.", ""])

    _heading(lines, "Cross-guest and causal evidence")
    cross_rows = []
    causal_availability = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        evidence = campaign.get("evidence") or {}
        for source, item in (evidence.get("cross_guest") or {}).items():
            cross_rows.append([run_id, system, mode, seed, source, item.get("exact_parent_links"),
                               item.get("invalid_identity_candidates"), item.get("placement_coverage"),
                               item.get("header_verdicts")])
        async_evidence = evidence.get("async")
        causal_availability.append([run_id, system, mode, seed, async_evidence is not None,
                                    "linked attempt rows retained in evidence-v4; no saved aggregate summary"
                                    if isinstance(async_evidence, dict) and async_evidence.get("attempts") is not None
                                    else (evidence.get("reason") or "no stored causal summary")])
    lines += _table(["Run", "System", "Mode", "Seed", "Source", "Exact parent links", "Invalid IDs",
                     "Placement coverage", "Header verdicts"], cross_rows)
    lines.extend(["", "Causal evidence availability (not recomputed from attempt rows):", ""])
    lines += _table(["Run", "System", "Mode", "Seed", "Attempt evidence present", "Stored-summary status"],
                    causal_availability)
    lines.extend(["", "Stored exact-chain association verdict census:", "",
                  "These verdicts describe source-local exact chain association in the final capture. They do not establish SQL durability or business correctness.", ""])
    causal_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        async_evidence = ((campaign.get("evidence") or {}).get("async"))
        if not isinstance(async_evidence, dict) or not isinstance(async_evidence.get("attempts"), list):
            causal_rows.append([run_id, system, mode, seed, "unavailable", "unavailable", None,
                                None, None, None, None, "unavailable", "stored async attempt evidence missing"])
            continue
        grouped = {}
        for item in async_evidence["attempts"]:
            key = (item.get("source") or "not_recorded", item.get("phase") or "not_recorded")
            state = item.get("four_stage_causal_chain")
            state = "not_recorded" if state is None else str(state)
            bucket = grouped.setdefault(key, {})
            bucket[state] = bucket.get(state, 0) + 1
        if not grouped:
            causal_rows.append([run_id, system, mode, seed, "none", "none", 0, 0, 0, 0,
                                "none", "0/0", "stored attempt list empty"])
        for (source, phase), states in sorted(grouped.items()):
            total = sum(states.values())
            unexpected = {key: value for key, value in states.items()
                          if key not in {"observed", "unknown", "not_recorded"}}
            causal_rows.append([run_id, system, mode, seed, source, phase, total,
                                states.get("observed", 0), states.get("unknown", 0),
                                states.get("not_recorded", 0), unexpected or "none",
                                f"{states.get('observed', 0)}/{total}", states])
    lines += _table(["Run", "System", "Mode", "Seed", "Source", "Phase", "Total", "Observed",
                     "Unknown", "Not recorded", "Unexpected states", "Coverage observed/total",
                     "All stored states"], causal_rows)

    _heading(lines, "Costs")
    cost_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        item = campaign.get("cost") or {}
        manual = item.get("manual_preparation") or {}
        cost_rows.append([run_id, system, mode, seed, item.get("campaign_elapsed_seconds"),
                          item.get("toolchain_clone_seconds"), item.get("toolchain_build_seconds"),
                          item.get("shared_input_preparation_seconds"), item.get("toolchain_command_seconds"),
                          item.get("bering_replay_command_seconds"), item.get("bering_child_peak_rss_kib"),
                          item.get("infrastructure_time_fields"), manual.get("measured"), manual.get("reason")])
    lines += _table(["Run", "System", "Mode", "Seed", "Campaign s", "Clone s", "Build s", "Input prep s",
                     "Toolchain commands s", "Bering replay s", "Bering peak RSS KiB", "Infrastructure fields",
                     "Manual prep measured", "Unavailable reason"], cost_rows)
    lines.extend(["", "Saved campaign phase costs:", "",
                  "Checkpoint creation/upload hold is nested inside campaign elapsed; swap setup precedes campaign elapsed. "
                  "Full stored cost records remain in the linked evaluation input.", ""])
    phase_rows = []
    for campaign in campaigns:
        run_id, system, mode, seed, _ = _identity(campaign)
        item = campaign.get("cost") or {}
        checkpoint = item.get("training_checkpoint") or {}
        upload = item.get("training_checkpoint_upload") or {}
        swap = item.get("swap_setup") or {}
        phase_rows.append([
            run_id, system, mode, seed,
            checkpoint.get("creation_wall_seconds"), checkpoint.get("upload_hold_wall_seconds"),
            checkpoint.get("total_wall_seconds"), upload.get("upload_success"),
            upload.get("artifact_id"), swap.get("elapsed_seconds"), swap.get("status"),
            swap.get("requested_additional_bytes"), item.get("resource_heartbeats_retained"),
        ])
    lines += _table([
        "Run", "System", "Mode", "Seed", "Checkpoint creation s", "Checkpoint upload hold s",
        "Checkpoint total s", "Upload success", "Upload artifact ID", "Swap setup s", "Swap status",
        "Swap requested additional bytes", "Resource heartbeat retained",
    ], phase_rows)
    if cost_payload is not None:
        lines.extend(["", "Optional saved cost artifact metadata:", ""])
        lines += _table(["Stored field", "Value"], [
            [key, value] for key, value in sorted(cost_payload.items())
            if not isinstance(value, (list, dict))])
        if not any(not isinstance(value, (list, dict)) for value in cost_payload.values()):
            lines.append("No scalar summary fields were stored; detailed cost data remains linked above and was not recomputed.")
        lines.extend([
            "",
            "Saved Actions jobs (independent of retained campaign artifacts):",
            "",
            "A job with no stored artifact is retained here as a technical execution record. "
            "It is not a campaign row and does not imply zero observations or any scientific outcome.",
            "",
        ])
        job_rows = []
        for run in cost_payload.get("runs") or []:
            artifacts = run.get("artifacts")
            artifact_names = ([item.get("name") for item in artifacts]
                              if isinstance(artifacts, list) else None)
            jobs = run.get("jobs")
            if not isinstance(jobs, list) or not jobs:
                job_rows.append([
                    run.get("run_id"), run.get("role"), run.get("head_sha"),
                    run.get("status"), run.get("conclusion"), None, None, None, None,
                    None, len(artifacts) if isinstance(artifacts, list) else None, artifact_names,
                ])
                continue
            for job in jobs:
                job_rows.append([
                    run.get("run_id"), run.get("role"), run.get("head_sha"),
                    run.get("status"), run.get("conclusion"), job.get("id"),
                    job.get("name"), job.get("status"), job.get("conclusion"),
                    job.get("elapsed_seconds"),
                    len(artifacts) if isinstance(artifacts, list) else None, artifact_names,
                ])
        lines += _table([
            "Run", "Role", "Head SHA", "Run status", "Run conclusion", "Job ID", "Job name",
            "Job status", "Job conclusion", "Stored elapsed s", "Run artifacts", "Run artifact names",
        ], job_rows)

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"report": str(out.resolve()), "aggregate": str(aggregate.resolve()),
            "attempts": len(campaigns), "costs": str(costs.resolve()) if costs else None}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", type=Path, required=True)
    parser.add_argument("--costs", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        parser.error("v4 research reporting is permitted only in GitHub Actions")
    render(args.aggregate, args.out, args.costs)


if __name__ == "__main__":
    main()
