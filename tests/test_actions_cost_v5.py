from copy import deepcopy

import pytest

from ebpf_discovery.actions_cost_v5 import recorded_job_costs

CONTEXT = dict(repository="owner/repo", run_id=10, workflow_path=".github/workflows/series-v5.yml",
               head_sha="a" * 40)


def job(identifier, name, start, end, attempt=1, conclusion="success"):
    return dict(id=identifier, name=name, run_id=10, head_sha="a" * 40,
                run_attempt=attempt, status="completed", conclusion=conclusion,
                runner_id=300, runner_name="host-300", runner_group_id=0,
                started_at=start, completed_at=end,
                steps=[dict(number=1, name="run", status="completed", conclusion=conclusion,
                            started_at=start, completed_at=end)])


def records():
    prepare = job(1, "prepare", "2026-11-04T05:48:19Z", "2026-11-04T05:48:21Z")
    capture = job(2, "capture", "2026-11-04T05:48:23Z", "2026-11-04T11:00:48Z")
    failed = job(3, "offline", "2026-11-04T11:00:51Z", "2026-11-04T12:48:43Z",
                 conclusion="failure")
    retry = job(4, "offline", "2026-11-04T12:55:56Z", None, attempt=2, conclusion=None)
    retry["status"] = "in_progress"
    copies = []
    for original in (prepare, capture):
        copy = deepcopy(original)
        copy.update(id=original["id"] + 10, run_attempt=2, runner_group_id=None)
        copies.append(copy)
    return [prepare, capture, failed, retry, *copies]


def test_failed_only_retry_preserves_all_rows_and_charges_copied_success_once():
    rows = records()
    before = deepcopy(rows)
    result = recorded_job_costs(rows, **CONTEXT)
    assert rows == before
    assert len(result["jobs"]) == 6
    assert result["raw_completed_job_elapsed_seconds"] == 43966
    assert result["completed_job_elapsed_seconds"] == 25219
    assert result["reused_success_elapsed_seconds"] == 18747
    assert result["reused_success_rows"] == 2
    assert result["jobs_with_unknown_elapsed"] == 1
    assert result["jobs"][2]["charged_elapsed_seconds"] == 6472
    assert result["jobs"][4]["alias_of_job_id"] == 1
    assert result["jobs"][5]["alias_of_job_id"] == 2
    assert result["jobs"][5]["elapsed_seconds"] == 18745
    assert result["jobs"][5]["charged_elapsed_seconds"] == 0


@pytest.mark.parametrize("field,value", [
    ("runner_id", 301), ("runner_name", "other"), ("head_sha", "b" * 40),
    ("run_id", 11), ("run_attempt", 1), ("run_attempt", None),
    ("started_at", "2026-11-04T05:48:24Z"),
    ("completed_at", "2026-11-04T11:00:49Z"),
    ("runner_id", None), ("runner_name", ""), ("name", "other"),
    ("status", "in_progress"), ("conclusion", "failure"),
])
def test_incomplete_or_different_execution_is_never_aliased(field, value):
    rows = records()
    rows[-1][field] = value
    result = recorded_job_costs(rows, **CONTEXT)
    assert result["jobs"][-1]["charged"]
    assert result["reused_success_rows"] == 1


@pytest.mark.parametrize("field", ["number", "name", "status", "conclusion",
                                  "started_at", "completed_at"])
def test_any_step_identity_or_clock_change_keeps_execution_distinct(field):
    rows = records()
    rows[-1]["steps"][0][field] = 2 if field == "number" else "different"
    assert recorded_job_costs(rows, **CONTEXT)["jobs"][-1]["charged"]


def test_missing_step_identity_and_missing_clocks_are_not_inferred():
    rows = records()
    rows[-1]["steps"][0]["started_at"] = None
    rows[-2]["completed_at"] = None
    result = recorded_job_costs(rows, **CONTEXT)
    assert result["reused_success_rows"] == 0
    assert result["jobs_with_unknown_elapsed"] == 2


def test_first_real_attempt_is_charged_even_when_api_rows_are_reordered():
    result = recorded_job_costs(list(reversed(records())), **CONTEXT)
    by = {r["id"]: r for r in result["jobs"]}
    assert by[12]["alias_of_job_id"] == 2
    assert by[2]["charged"]
    assert result["completed_job_elapsed_seconds"] == 25219


def test_real_later_retry_and_failed_copies_remain_charged():
    rows = records()
    rows[3] = job(4, "offline", "2026-11-04T12:55:56Z", "2026-11-04T13:55:56Z",
                  attempt=2)
    failed_copy = deepcopy(rows[2])
    failed_copy.update(id=20, run_attempt=2)
    rows.append(failed_copy)
    result = recorded_job_costs(rows, **CONTEXT)
    assert result["jobs"][3]["charged_elapsed_seconds"] == 3600
    assert result["jobs"][-1]["charged_elapsed_seconds"] == 6472
    assert result["completed_job_elapsed_seconds"] == 35291
