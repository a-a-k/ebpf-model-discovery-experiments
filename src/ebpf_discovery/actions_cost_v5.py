"""Count recorded job time without charging GitHub's reused success rows twice."""
from __future__ import annotations

from datetime import datetime


def _elapsed(job: dict) -> float | None:
    start, end = job.get("started_at"), job.get("completed_at")
    if not start or not end:
        return None
    return (datetime.fromisoformat(end.replace("Z", "+00:00"))
            - datetime.fromisoformat(start.replace("Z", "+00:00"))).total_seconds()


def _execution_key(job, repository, run_id, workflow_path, head_sha):
    # A failed-only retry copies successful jobs with new IDs/attempts and the
    # old execution clocks. Missing identity never justifies merging records.
    attempt = job.get("run_attempt")
    fields = ("name", "runner_name", "started_at", "completed_at")
    if (job.get("status") != "completed" or job.get("conclusion") != "success"
            or type(attempt) is not int or attempt <= 0
            or type(job.get("id")) is not int or job["id"] <= 0
            or type(job.get("runner_id")) is not int or job["runner_id"] <= 0
            or not all(isinstance(job.get(k), str) and job[k] for k in fields)
            or job.get("run_id") != run_id or job.get("head_sha") != head_sha
            or not all((repository, run_id, workflow_path, head_sha))):
        return None
    steps = job.get("steps")
    keys = ("number", "name", "status", "conclusion", "started_at", "completed_at")
    if not isinstance(steps, list) or not steps:
        return None
    vector = []
    for step in steps:
        if (not isinstance(step, dict) or type(step.get("number")) is not int
                or not all(isinstance(step.get(k), str) and step[k] for k in keys[1:])):
            return None
        vector.append(tuple(step[k] for k in keys))
    if len({step[0] for step in vector}) != len(vector):
        return None
    return (repository, run_id, workflow_path, head_sha, job["name"],
            job["runner_id"], job["runner_name"], job["started_at"],
            job["completed_at"], tuple(vector))


def recorded_job_costs(jobs: list[dict], *, repository: str, run_id: int,
                       workflow_path: str, head_sha: str) -> dict:
    """Preserve all rows; charge only proven cross-attempt success copies once.

    This measures recorded execution elapsed time, not CPU, billing, or total
    campaign wall time. Failed retries and incomplete identities remain distinct.
    """
    result = [None] * len(jobs)
    seen = {}
    ordered = sorted(enumerate(jobs), key=lambda pair: (
        pair[1].get("run_attempt") if type(pair[1].get("run_attempt")) is int else float("inf"),
        pair[0]))
    for index, job in ordered:
        elapsed = _elapsed(job)
        key = _execution_key(job, repository, run_id, workflow_path, head_sha)
        original = seen.get(key) if key is not None else None
        alias = (original is not None
                 and original["run_attempt"] < job["run_attempt"]
                 and original["id"] != job["id"])
        row = {k: job.get(k) for k in ("id", "name", "status", "conclusion", "run_attempt")}
        row.update(elapsed_seconds=elapsed, charged=not alias,
                   charged_elapsed_seconds=0.0 if alias else elapsed,
                   alias_of_job_id=original["id"] if alias else None,
                   alias_of_attempt=original["run_attempt"] if alias else None)
        result[index] = row
        if key is not None and original is None:
            seen[key] = job
    return {
        "jobs": result,
        "completed_job_elapsed_seconds": sum(
            r["charged_elapsed_seconds"] for r in result
            if r["charged_elapsed_seconds"] is not None),
        "raw_completed_job_elapsed_seconds": sum(
            r["elapsed_seconds"] for r in result if r["elapsed_seconds"] is not None),
        "jobs_with_unknown_elapsed": sum(r["charged_elapsed_seconds"] is None for r in result),
        "reused_success_rows": sum(not r["charged"] for r in result),
        "reused_success_elapsed_seconds": sum(
            r["elapsed_seconds"] for r in result if not r["charged"]),
    }
