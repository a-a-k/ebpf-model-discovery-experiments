"""Exercise the actual workflow's inline metadata gate, with no network or traffic."""
import json
from pathlib import Path

import pytest
import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/toolchain-worker-v4.yml'


def binding_script():
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding='utf-8'))
    step = next(step for step in workflow['jobs']['toolchain']['steps']
                if step.get('name') == 'Bind and download the immutable parent checkpoint')
    return step['run'].split("python - <<'PY'\n", 1)[1].split('\nPY', 1)[0]


def execute(tmp_path, monkeypatch, change=None, parent_status='queued'):
    expected = {'parent_repository': 'owner/repo', 'run_id': '10',
                'parent_run_attempt': '2', 'parent_cell_id': 'otel_demo:absent:7',
                'system': 'otel_demo', 'mode': 'absent', 'seed': '7',
                'commit': 'a' * 40, 'artifact_id': '20',
                'artifact_name': 'fixed-checkpoint', 'artifact_digest': 'sha256:' + 'b' * 64}
    run = {'id': 10, 'head_sha': expected['commit'], 'run_attempt': 2,
           'status': parent_status}
    artifact = {'id': 20, 'name': expected['artifact_name'],
                'digest': expected['artifact_digest'], 'expired': False,
                'workflow_run': {'id': 10, 'head_sha': expected['commit']}}
    job = {'id': 30, 'name': 'campaign (otel_demo, absent, 7)',
           'run_id': 10, 'run_attempt': 2, 'status': 'in_progress'}
    jobs = [job, {'id': 31, 'name': 'campaign (otel_demo, full, 8)',
                 'run_id': 10, 'run_attempt': 2, 'status': 'queued'}]
    if change:
        change(expected, run, artifact, job, jobs)
    monkeypatch.chdir(tmp_path)
    for name, value in (('expected', expected), ('parent-run-api', run),
                        ('artifact-api', artifact), ('parent-jobs-api', [{'jobs': jobs}])):
        path = tmp_path / 'work/worker-input' / (name + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')
    (tmp_path / 'work/worker-artifact/infrastructure').mkdir(parents=True)
    for key, value in {'GITHUB_REPOSITORY': 'owner/repo', 'GITHUB_SHA': 'c' * 40,
                       'GITHUB_RUN_ID': '40', 'GITHUB_RUN_ATTEMPT': '1'}.items():
        monkeypatch.setenv(key, value)
    exec(compile(binding_script(), str(WORKFLOW), 'exec'), {})
    return json.loads((tmp_path / 'work/worker-artifact/infrastructure/checkpoint-binding.json').read_text())


@pytest.mark.parametrize('parent_status', ['queued', 'in_progress'])
def test_live_exact_cell_accepts_matrix_and_single_cell_status(tmp_path, monkeypatch, parent_status):
    proof = execute(tmp_path, monkeypatch, parent_status=parent_status)
    assert proof['accepted'] and all(proof['checks'].values())
    bound = json.loads((tmp_path / 'work/worker-input/expected.json').read_text())
    assert bound['worker_run_id'] == '40'


@pytest.mark.parametrize('change,failed_check', [
    (lambda e,r,a,j,js: r.update(status='completed'), 'run_not_terminal'),
    (lambda e,r,a,j,js: j.update(status='queued'), 'cell_job_in_progress'),
    (lambda e,r,a,j,js: j.update(status='completed'), 'cell_job_in_progress'),
    (lambda e,r,a,j,js: js.pop(0), 'unique_cell_job'),
    (lambda e,r,a,j,js: js.append(dict(j)), 'unique_cell_job'),
    (lambda e,r,a,j,js: j.update(run_id=11), 'cell_job_run'),
    (lambda e,r,a,j,js: j.update(run_attempt=1), 'cell_job_attempt'),
    (lambda e,r,a,j,js: r.update(run_attempt=1), 'run_attempt'),
    (lambda e,r,a,j,js: r.update(head_sha='wrong'), 'run_head'),
    (lambda e,r,a,j,js: a.update(digest='wrong'), 'artifact_digest'),
    (lambda e,r,a,j,js: a.update(expired=True), 'artifact_not_expired'),
    (lambda e,r,a,j,js: a['workflow_run'].update(id=11), 'artifact_parent_run'),
    (lambda e,r,a,j,js: e.update(parent_cell_id='otel_demo:full:8'), 'cell_identity'),
])
def test_wrong_identity_or_inactive_exact_cell_rejects_with_proof(
        tmp_path, monkeypatch, change, failed_check):
    with pytest.raises(SystemExit, match=failed_check):
        execute(tmp_path, monkeypatch, change)
    proof = json.loads((tmp_path / 'work/worker-artifact/infrastructure/checkpoint-binding.json').read_text())
    assert not proof['accepted'] and not proof['checks'][failed_check]


def test_live_sibling_cannot_authorize_queued_requested_cell(tmp_path, monkeypatch):
    def change(expected, run, artifact, job, jobs):
        job['status'] = 'queued'
        jobs[1]['status'] = 'in_progress'
    with pytest.raises(SystemExit, match='cell_job_in_progress'):
        execute(tmp_path, monkeypatch, change)


def test_workflow_retains_exact_attempt_api_and_failure_metadata():
    body = WORKFLOW.read_text(encoding='utf-8')
    assert '/attempts/${{ inputs.parent_run_attempt }}/jobs?per_page=100' in body
    assert 'gh api --paginate --slurp' in body
    retain = yaml.safe_load(body)['jobs']['toolchain']['steps']
    retain = next(step for step in retain if step.get('name') == 'Retain worker environment and resource evidence')
    assert retain['if'] == 'always()'
    assert 'parent-jobs-api.json' in retain['run']
