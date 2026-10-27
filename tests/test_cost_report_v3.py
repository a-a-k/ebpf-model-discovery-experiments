import json
from pathlib import Path

from ebpf_discovery.cost_report_v3 import report


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def metadata(root: Path, run_id: int, *, complete: bool, size: int):
    write(root / f"{run_id}-run.json", {
        "id": run_id, "name": "workflow", "path": ".github/workflows/x.yml",
        "status": "completed" if complete else "in_progress", "conclusion": "success" if complete else None,
        "run_attempt": 1, "head_sha": "a" * 40,
    })
    write(root / f"{run_id}-jobs.json", [{"total_count": 1, "jobs": [{
        "id": run_id * 10, "run_id": run_id, "name": "job", "run_attempt": 1,
        "status": "completed" if complete else "in_progress", "conclusion": "success" if complete else None,
        "started_at": "2026-10-27T10:00:00Z", "completed_at": "2026-10-27T10:01:00Z" if complete else None,
    }]}])
    write(root / f"{run_id}-artifacts.json", [
        {"total_count": 2, "artifacts": [{"id": run_id, "name": "same-bytes-a", "size_in_bytes": size}]},
        {"total_count": 2, "artifacts": [{"id": run_id + 1, "name": "same-bytes-b", "size_in_bytes": size}]},
    ])


def test_report_separates_costs_and_preserves_unknowns(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    provenance = tmp_path / "provenance"
    metadata(provenance, 101, complete=True, size=50)
    metadata(provenance, 202, complete=False, size=25)
    manifest = tmp_path / "preparation.json"
    write(manifest, {
        "schema_version": 1, "repository": "owner/repo",
        "runs": [{"run_id": 202, "role": "qualification", "note": "failed preparation"}],
        "human_agent_time_note": "unknown",
    })
    series = tmp_path / "series.json"
    write(series, [101])

    outputs = report(provenance, manifest, series, tmp_path / "report")
    result = json.loads(Path(outputs["json"]).read_text())
    assert result["scientific_acquisition"]["completed_job_elapsed_seconds"] == 60
    assert result["scientific_acquisition"]["stored_artifact_bytes"] == 100
    assert result["preparation"]["completed_job_elapsed_seconds"] is None
    assert result["preparation"]["known_job_elapsed_seconds_subtotal"] is None
    assert result["preparation"]["stored_artifact_bytes"] == 50
    assert result["human_agent_time_seconds"] is None
    assert result["current_reporting_job"]["elapsed_seconds"] is None
    assert len(result["runs"][0]["artifacts"]) == 2
    assert result["runs"][0]["metadata_sha256"]["jobs"]
