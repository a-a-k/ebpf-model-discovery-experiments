"""Report complete Actions job and stored-artifact costs for iteration 3."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def _require_actions() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Iteration-3 cost reporting runs in GitHub Actions only")


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _elapsed(start: Any, end: Any) -> float | None:
    if not isinstance(start, str) or not isinstance(end, str):
        return None
    seconds = (
        datetime.fromisoformat(end.replace("Z", "+00:00"))
        - datetime.fromisoformat(start.replace("Z", "+00:00"))
    ).total_seconds()
    if seconds < 0:
        raise ValueError("job completion precedes job start")
    return seconds


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pages(payload: Any, key: str) -> list[dict[str, Any]]:
    pages = payload if isinstance(payload, list) else [payload]
    if not pages or any(not isinstance(page, dict) or not isinstance(page.get(key), list) for page in pages):
        raise ValueError(f"invalid paginated {key} metadata")
    return [row for page in pages for row in page[key]]


def _complete_sum(values: list[int | float | None]) -> int | float | None:
    return sum(values) if all(value is not None for value in values) else None


def _group(rows: list[dict[str, Any]], classification: str) -> dict[str, Any]:
    selected = [row for row in rows if row["classification"] == classification]
    job_seconds = [job["elapsed_seconds"] for row in selected for job in row["jobs"]]
    artifact_bytes = [artifact["size_in_bytes"] for row in selected for artifact in row["artifacts"]]
    return {
        "runs": len(selected),
        "jobs": sum(len(row["jobs"]) for row in selected),
        "completed_job_elapsed_seconds": _complete_sum(job_seconds),
        "known_job_elapsed_seconds_subtotal": (
            sum(value for value in job_seconds if value is not None)
            if any(value is not None for value in job_seconds) else None
        ),
        "jobs_with_unknown_elapsed": sum(value is None for value in job_seconds),
        "job_conclusions": dict(sorted(Counter(
            job["conclusion"] or "unknown" for row in selected for job in row["jobs"]
        ).items())),
        "stored_artifact_bytes": _complete_sum(artifact_bytes),
        "known_stored_artifact_bytes_subtotal": (
            sum(value for value in artifact_bytes if value is not None)
            if any(value is not None for value in artifact_bytes) else None
        ),
        "artifacts_with_unknown_size": sum(value is None for value in artifact_bytes),
    }


def report(provenance: Path, manifest_path: Path, series_path: Path, output: Path) -> dict[str, str]:
    """Build a cost ledger from already fetched GitHub API responses."""
    _require_actions()
    manifest, series = _read(manifest_path), _read(series_path)
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("runs"), list):
        raise ValueError("invalid preparation run manifest")
    if not isinstance(series, list) or not series or any(type(run_id) is not int for run_id in series):
        raise ValueError("series run manifest must be a nonempty JSON array of integer run IDs")
    preparation = {}
    for row in manifest["runs"]:
        if (not isinstance(row, dict) or type(row.get("run_id")) is not int
                or row.get("role") not in {"qualification", "replay", "evidence"}):
            raise ValueError("invalid preparation run declaration")
        if row["run_id"] in preparation:
            raise ValueError("duplicate preparation run ID")
        preparation[row["run_id"]] = row
    if len(set(series)) != len(series) or set(series) & set(preparation):
        raise ValueError("series and preparation run IDs must be unique and disjoint")

    rows = []
    for run_id in [*series, *preparation]:
        paths = {name: provenance / f"{run_id}-{name}.json" for name in ("run", "jobs", "artifacts")}
        run = _read(paths["run"])
        jobs = _pages(_read(paths["jobs"]), "jobs")
        artifacts = _pages(_read(paths["artifacts"]), "artifacts")
        if run.get("id") != run_id or any(job.get("run_id") != run_id for job in jobs):
            raise ValueError(f"GitHub metadata identity mismatch for run {run_id}")
        seen_jobs = set()
        job_rows = []
        for job in jobs:
            if job.get("id") in seen_jobs:
                raise ValueError(f"duplicate job metadata for run {run_id}")
            seen_jobs.add(job.get("id"))
            job_rows.append({
                "job_id": job.get("id"), "name": job.get("name"),
                "status": job.get("status"), "conclusion": job.get("conclusion"),
                "started_at": job.get("started_at"), "completed_at": job.get("completed_at"),
                "elapsed_seconds": _elapsed(job.get("started_at"), job.get("completed_at")),
                "html_url": job.get("html_url"), "run_attempt": job.get("run_attempt"),
            })
        artifact_rows = [{
            "artifact_id": artifact.get("id"), "name": artifact.get("name"),
            "size_in_bytes": artifact.get("size_in_bytes") if type(artifact.get("size_in_bytes")) is int else None,
            "expired": artifact.get("expired"), "created_at": artifact.get("created_at"),
            "expires_at": artifact.get("expires_at"), "archive_download_url": artifact.get("archive_download_url"),
        } for artifact in artifacts]
        declaration = preparation.get(run_id)
        rows.append({
            "run_id": run_id,
            "classification": "preparation" if declaration else "scientific_acquisition",
            "declared_role": declaration.get("role") if declaration else "series_input",
            "declared_note": declaration.get("note") if declaration else None,
            "workflow_name": run.get("name"), "workflow_path": run.get("path"),
            "display_title": run.get("display_title"), "event": run.get("event"),
            "status": run.get("status"), "conclusion": run.get("conclusion"),
            "run_attempt": run.get("run_attempt"), "created_at": run.get("created_at"),
            "run_started_at": run.get("run_started_at"), "updated_at": run.get("updated_at"),
            "head_sha": run.get("head_sha"), "html_url": run.get("html_url"),
            "metadata_sha256": {name: _digest(path) for name, path in paths.items()},
            "jobs": job_rows, "artifacts": artifact_rows,
        })

    output.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": 1,
        "repository": manifest.get("repository"),
        "input_sha256": {
            "preparation_manifest": _digest(manifest_path),
            "series_run_manifest": _digest(series_path),
        },
        "cost_definition": {
            "job_elapsed": "sum of GitHub job started_at-to-completed_at durations, including setup, preparation and failures",
            "stored_artifact_bytes": "sum of GitHub artifact size_in_bytes values; repeated or overlapping artifacts are charged repeatedly and are not content-deduplicated",
            "run_wall_clock_not_substituted": True,
        },
        "scientific_acquisition": _group(rows, "scientific_acquisition"),
        "preparation": _group(rows, "preparation"),
        "runs": rows,
        "human_agent_time_seconds": None,
        "human_agent_time_note": manifest.get("human_agent_time_note"),
        "current_reporting_job": {
            "elapsed_seconds": None,
            "included_in_fetched_job_totals": False,
            "reason": "the reporting job is incomplete when this report is generated",
        },
    }
    json_path, csv_path, markdown_path = output / "costs-v3.json", output / "job-costs-v3.csv", output / "costs-v3.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    jobs = [{"run_id": row["run_id"], "classification": row["classification"],
             "declared_role": row["declared_role"], **job} for row in rows for job in row["jobs"]]
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        fields = list(jobs[0]) if jobs else []
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(jobs)
    def display(value: Any, unit: str) -> str:
        return "unknown" if value is None else f"{value} {unit}"
    lines = [
        "# Iteration 3 Actions cost ledger", "",
        "Preparation/replay/evidence runs are reported separately from scientific acquisition runs.", "",
        "| Class | Runs | Jobs | Total job elapsed | Stored artifact bytes | Unknown job durations |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("scientific_acquisition", "preparation"):
        group = result[name]
        lines.append(
            f"| {name} | {group['runs']} | {group['jobs']} | "
            f"{display(group['completed_job_elapsed_seconds'], 'seconds')} | "
            f"{display(group['stored_artifact_bytes'], 'bytes')} | {group['jobs_with_unknown_elapsed']} |"
        )
    lines += ["", ("Artifact bytes are stored capture cost: duplicate and overlapping artifacts are counted each time. "
                     "No content deduplication is claimed."), "",
              "Human/agent time and the still-running reporting job remain unknown; neither is filled with zero."]
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(markdown_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--series-runs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(report(args.provenance, args.manifest, args.series_runs, args.out), sort_keys=True))


if __name__ == "__main__":
    main()
