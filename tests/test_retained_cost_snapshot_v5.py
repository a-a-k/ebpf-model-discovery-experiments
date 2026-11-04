"""The report reuses frozen cost observations and queries only the fresh tail."""
import json
from pathlib import Path

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/report-v5.yml"


def run_cost_step(tmp_path, monkeypatch, *, invalid=None):
    from copy import deepcopy
    import subprocess

    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["report"]["steps"]
    script = next(s["run"] for s in steps if s.get("name") ==
                  "Retain Actions metadata and complete declared cost scope")
    script = script.split("python - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    rows = [dict(repository="owner/repo", run_id=i, role="worker", note="old",
                 metadata_status="retained_terminal_archive_snapshot",
                 completed_job_elapsed_seconds=1, raw_completed_job_elapsed_seconds=1,
                 reused_success_rows=0, reused_success_elapsed_seconds=0,
                 jobs_with_unknown_elapsed=0, jobs=[], artifacts=[], stored_artifact_bytes=0)
            for i in range(1, 860)]
    declarations = dict(related_runs=[
        dict(run_id=i, role="preparation", note="declared")
        for i in range(1, 860)] + [dict(run_id=9001, role="worker", note="live")])
    if invalid == "duplicate":
        rows[-1]["run_id"] = rows[0]["run_id"]
    if invalid == "undeclared":
        rows[-1]["run_id"] = 10000
    snapshot = dict(schema_version="v5-fixed-retained-cost-snapshot", rows=rows)
    body = json.dumps(snapshot).encode()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_SHA", "f" * 40)
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    path = tmp_path / "docs/clean-study-retained-cost-snapshot-20261104.json"
    path.parent.mkdir()
    path.write_bytes(body + (b" " if invalid == "blob_drift" else b""))
    root = tmp_path / "results/iteration-5/provenance"
    root.mkdir(parents=True)
    (root / "declarations.json").write_text(json.dumps(declarations))
    calls = []

    def read(command, **kwargs):
        if command[:2] == ["git", "show"]:
            return body
        if command[:2] == ["git", "rev-parse"]:
            return "b" * 40 + "\n"
        assert command[:2] == ["gh", "api"]
        calls.append(command)
        endpoint = command[-1]
        if "/jobs?" in endpoint:
            data = [dict(total_count=1, jobs=[dict(id=200, run_id=9001, run_attempt=1,
                head_sha="a" * 40, name="fresh", status="completed", conclusion="success",
                runner_id=1, runner_name="host", started_at="2026-11-04T00:00:00Z",
                completed_at="2026-11-04T00:00:01Z",
                steps=[dict(number=1, name="work", status="completed", conclusion="success",
                    started_at="2026-11-04T00:00:00Z", completed_at="2026-11-04T00:00:01Z")])])]
        elif "/artifacts?" in endpoint:
            data = [dict(total_count=0, artifacts=[])]
        else:
            assert endpoint.endswith("/9001")
            data = dict(id=9001, head_sha="a" * 40, path=".github/workflows/checks.yml",
                        status="completed", conclusion="success", html_url="url")
        return json.dumps(data)

    monkeypatch.setattr(subprocess, "check_output", read)
    exec(compile(script, str(WORKFLOW), "exec"), {})
    return json.loads((root.parent / "costs-v5.json").read_text()), calls


def test_frozen_859_keys_need_no_API_and_declared_role_note_win(tmp_path, monkeypatch):
    costs, calls = run_cost_step(tmp_path, monkeypatch)
    assert len(costs["runs"]) == 860
    assert len(calls) == 3
    assert all("/9001" in call[-1] for call in calls)
    assert costs["runs"][0]["role"] == "preparation"
    assert costs["runs"][0]["note"] == "declared"
    assert costs["runs"][-1]["metadata_status"] == "retained"
    assert costs["known_completed_job_elapsed_seconds"] == 860
    assert costs["raw_completed_job_elapsed_seconds"] == 860
    assert costs["runs_with_unknown_job_elapsed"] == 0
    assert (tmp_path / "results/iteration-5/provenance/retained-cost-snapshot.json").exists()


@pytest.mark.parametrize("invalid", ["duplicate", "undeclared", "blob_drift"])
def test_unreviewed_snapshot_identity_or_blob_is_rejected(tmp_path, monkeypatch, invalid):
    with pytest.raises(SystemExit, match="snapshot"):
        run_cost_step(tmp_path, monkeypatch, invalid=invalid)
