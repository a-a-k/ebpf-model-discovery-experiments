"""Synthetic projection guards; no application/model data is processed locally."""
from copy import deepcopy
import pytest

from ebpf_discovery.compose_ack_repair import counts, project_targets
from ebpf_discovery.compose_ack_contract import OPERATIONS, direct_baselines, UNAVAILABLE
from ebpf_discovery.study import workload_counts


def synthetic_records():
    n = workload_counts(3, False)
    rows = [{'phase': 'preparation', 'operation': operation, 'state': '11', 'success': True}
            for operation in OPERATIONS for _ in range(11)]
    for state, multiplicity in [('11', 4), ('10', 2), ('01', 1), ('00', 1)]:
        rows.extend({'phase': 'target', 'operation': OPERATIONS[i % 3], 'state': state,
                     'success': None if i == 0 and state == '00' else state != '00'}
                    for i in range(n['target'] * multiplicity))
    for phase, size in [('class_test', n['class_test']), ('db_up', n['database']), ('db_down', n['database'])]:
        rows.extend({'phase': phase, 'operation': OPERATIONS[i % 3], 'state': '11', 'success': True}
                    for i in range(size))
    return rows


def test_projection_retains_preparation_unknowns_and_protocol_7_7_6_db_counts():
    forecasts = {'ebpf': {'raw': {op: deepcopy(UNAVAILABLE) for op in OPERATIONS}}}
    rows = synthetic_records()
    result = project_targets(forecasts, direct_baselines(), rows, {'mode': 'absent'})
    assert result['technical_complete']
    assert result['all_retained_phase_counts']['preparation'] == 33
    assert [r['db_down']['total'] for r in result['rows']] == [7, 7, 6]
    assert result['rows'][0]['observed']['unknown'] == 1
    assert len(rows) == sum(result['all_retained_phase_counts'].values())


def test_projection_rejects_missing_real_target_not_a_forecast_miss():
    rows = synthetic_records()
    rows.pop(33)
    with pytest.raises(ValueError, match='phase coverage differs'):
        project_targets({}, direct_baselines(), rows, {})


def test_invalid_outcome_is_never_silently_lost_as_unknown():
    with pytest.raises(ValueError, match='invalid external outcome'):
        counts([{'success': 'yes'}])


def test_lossless_size_fallback_preserves_exact_original_bytes(tmp_path, monkeypatch):
    from ebpf_discovery.compose_ack_repair import publish_raw
    from ebpf_discovery import compose_ack_repair as repair
    import hashlib
    from types import SimpleNamespace
    data = b'123456789abcd'
    raw = tmp_path / 'target.tar.gz'
    raw.write_bytes(data)
    saved = {}
    def publish(path):
        body = path.read_bytes()
        saved[path.name] = body
        return {'id': len(saved), 'name': path.name, 'size': len(body),
                'digest': 'sha256:' + hashlib.sha256(body).hexdigest(), 'state': 'uploaded'}
    monkeypatch.setattr(repair.b, 'capacity', lambda *_: None)
    result = publish_raw(SimpleNamespace(publish=publish), raw, max_asset_bytes=8, chunk_bytes=5)
    reconstructed = b''.join(saved[p['asset']['name']] for p in result['parts'])
    assert reconstructed == data == raw.read_bytes()
    assert result['original_sha256'] == hashlib.sha256(data).hexdigest()
    assert [p['offset'] for p in result['parts']] == [0, 5, 10]
    assert not list(tmp_path.glob('*.part*'))


def test_matrix_freezes_every_block_before_any_fresh_target():
    from pathlib import Path
    import json
    import yaml
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.load((root / '.github/workflows/compose-ack-correction.yml').read_text(), Loader=yaml.BaseLoader)
    jobs = workflow['jobs']
    assert jobs['target']['needs'] == ['prepare', 'barrier']
    assert jobs['barrier']['needs'] == ['prepare', 'freeze']
    assert jobs['freeze']['strategy']['matrix']['mode'] == ['absent', 'partial', 'full']
    assert jobs['target']['strategy']['matrix'] == '${{ fromJSON(needs.prepare.outputs.target_matrix) }}'
    assert int(jobs['target']['strategy']['max-parallel']) == 36
    assert all(job['timeout-minutes'] == '360' for job in jobs.values())
    plan = json.loads((root / 'docs/compose-ack-correction-plan.json').read_bytes())
    assert plan['fresh_cells'] == 36 and len(plan['blocks']) == 9
    assert len({a['artifact']['id'] for b in plan['blocks'] for a in b['arms'].values()}) == 36
    from ebpf_discovery.compose_ack_repair import target_matrix
    matrix = target_matrix(plan)['include']
    assert len(matrix) == 36
    for block in plan['blocks']:
        matching = [c for c in matrix if [c['mode'], c['repetition']] == block['key'][1:]]
        assert [c['collector'] for c in matching] == block['original_arm_orders']['validation']
        assert {c['collector'] for c in matching} == {'none', 'obi', 'coroot', 'deepflow'}


def target_job(job_id, attempt, offset=0):
    from datetime import datetime, timedelta, timezone
    start = datetime(2026, 11, 9, tzinfo=timezone.utc) + timedelta(seconds=offset)
    return {'id': job_id, 'run_attempt': attempt, 'status': 'completed', 'conclusion': 'success',
            'steps': [{'name': 'Capture fresh independent targets from the original sealed blueprint',
                       'status': 'completed', 'conclusion': 'success',
                       'started_at': start.isoformat(), 'completed_at': (start + timedelta(seconds=10)).isoformat()}]}


def publication(attempt, start, producer_id):
    return {'asset': {'id': attempt}, 'receipt': {'attempt': attempt, 'error': None,
            'result': {'technical_complete': True, 'status': {'started_ns': start + 10**9,
                'ended_ns': start + 5 * 10**9, 'producing_job': {'id': producer_id}}}}}


def test_reused_successful_api_alias_does_not_require_a_fictitious_new_publication():
    from ebpf_discovery.compose_ack_repair import select_actual_publication, step_interval_ns
    original = target_job(10, 1)
    base = step_interval_ns(original['steps'][0]['started_at'])
    actual = publication(1, base, 10)
    alias = target_job(20, 3)
    chosen, job, aliases = select_actual_publication([actual], [alias])
    assert chosen['receipt']['attempt'] == 1
    assert job['run_attempt'] == 3
    assert aliases == [alias]


def test_latest_actual_capture_clock_wins_over_highest_old_alias_label():
    from ebpf_discovery.compose_ack_repair import select_actual_publication, step_interval_ns
    earlier_alias, new = target_job(20, 99), target_job(30, 2, offset=20)
    first = publication(1, step_interval_ns(earlier_alias['steps'][0]['started_at']), 10)
    second = publication(2, step_interval_ns(new['steps'][0]['started_at']), 30)
    chosen, job, _ = select_actual_publication([first, second], [earlier_alias, new])
    assert chosen['receipt']['attempt'] == 2 and job['id'] == 30
