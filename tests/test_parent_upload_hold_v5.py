"""Small synthetic checkpoints exercise scheduling without application traffic."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

from ebpf_discovery import checkpoint_v4 as checkpoints
from ebpf_discovery import remote_toolchain_v4 as remote
from test_checkpoint_v4 import _capture
from test_remote_toolchain_v4 import FakeResponse


@pytest.fixture
def parent(tmp_path, monkeypatch):
    campaign, _, _ = _capture(tmp_path, monkeypatch)
    campaign.system = 'otel_demo'
    campaign.ctx.mode = 'absent'
    campaign.collector = 'deepflow'
    campaign.smoke = False
    campaign.toolchain_execution = 'worker'
    status = campaign.ctx.out / 'status.json'
    value = json.loads(status.read_text())
    value.update(system='otel_demo', mode='absent')
    status.write_text(json.dumps(value), encoding='utf-8')
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setenv('GITHUB_RUN_ATTEMPT', '1')
    cp = tmp_path / 'training-checkpoint'
    ready = checkpoints.create_checkpoint(campaign, cp)
    yield campaign, cp, ready
    campaign.store.close()
    campaign.ctx.journal.close()


def release(ready):
    return {**ready, 'upload_success': True, 'artifact_id': '42',
            'artifact_url': 'https://github.com/owner/repo/actions/artifacts/42',
            'artifact_digest': 'sha256:' + 'a' * 64}


def test_full_proofs_during_upload_equal_original_after_release(parent, monkeypatch):
    campaign, cp, ready = parent
    plans = []
    original_expected, original_proof = remote._expected(campaign, cp, release(ready), plans)
    original_reference = remote._checkpoint_index_reference(cp, original_proof)
    remote.prepare_parent_checkpoint(campaign, cp, ready, plans)
    assert not (cp / 'release.json').exists()
    prepared = campaign._remote_checkpoint_preflight
    assert prepared['proof'] == original_proof
    assert prepared['index_reference']['logical_proof'] == original_reference['logical_proof']
    assert prepared['index_reference']['input'] == original_reference['input']
    def no_repeated_full_scan(*_):
        raise AssertionError('unchanged proof must be computed once during upload')
    monkeypatch.setattr(remote, '_validate_checkpoint', no_repeated_full_scan)
    actual_expected, actual_proof = remote._expected(campaign, cp, release(ready), plans)
    assert (actual_expected, actual_proof) == (original_expected, original_proof)


@pytest.mark.parametrize('change', ['payload', 'manifest', 'extra', 'plans', 'release', 'scope'])
def test_preflight_rejects_changed_released_input_before_dispatch(parent, change):
    campaign, cp, ready = parent
    remote.prepare_parent_checkpoint(campaign, cp, ready, [])
    value = release(ready)
    plans = []
    if change == 'payload':
        p = cp / 'plans.json'
        p.write_bytes(p.read_bytes() + b' ')
    elif change == 'manifest':
        p = cp / 'manifest.json'
        p.write_bytes(p.read_bytes() + b' ')
    elif change == 'extra':
        (cp / 'unlisted').write_text('x')
    elif change == 'plans':
        plans = [{'phase': 'target'}]
    elif change == 'release':
        value['seed'] = 8
    else:
        campaign.collector = 'obi'
    with pytest.raises(ValueError):
        remote._expected(campaign, cp, value, plans)


def test_preflight_detects_mutation_during_complete_SQL_proof(parent, monkeypatch):
    campaign, cp, ready = parent
    original = remote._checkpoint_index_reference
    def changed(*args):
        result = original(*args)
        p = cp / 'plans.json'
        p.write_bytes(p.read_bytes() + b' ')
        return result
    monkeypatch.setattr(remote, '_checkpoint_index_reference', changed)
    with pytest.raises(ValueError, match='changed during'):
        remote.prepare_parent_checkpoint(campaign, cp, ready, [])
    assert not hasattr(campaign, '_remote_checkpoint_preflight')
    receipt = campaign.ctx.out / 'infrastructure/remote-toolchain-v4/upload-hold-preflight.json'
    assert json.loads(receipt.read_text())['status'] == 'failed'


def test_callback_is_after_ready_and_before_upload_release(parent, monkeypatch):
    campaign, cp, ready = parent
    events = []
    monkeypatch.setattr(checkpoints, 'create_checkpoint', lambda *_: ready)
    def callback(actual):
        assert (cp / 'ready.json').is_file() and actual == ready
        events.append('full_readonly_proofs')
        remote.prepare_parent_checkpoint(campaign, cp, ready, [])
    def uploaded(*_):
        assert events == ['full_readonly_proofs']
        events.append('bind_actual_upload')
        return release(ready)
    monkeypatch.setattr(checkpoints, 'wait_for_release', uploaded)
    assert checkpoints.checkpoint_and_wait(campaign, cp, ready_callback=callback)['upload_success']
    cost = json.loads((campaign.ctx.out / 'training-checkpoint-cost.json').read_text())
    assert cost['ready_callback_seconds'] >= 0
    assert cost['upload_hold_wall_seconds'] >= cost['ready_callback_seconds']


def test_callback_failure_never_advances_to_release(parent, monkeypatch):
    campaign, cp, ready = parent
    monkeypatch.setattr(checkpoints, 'create_checkpoint', lambda *_: ready)
    def failed(_):
        raise ValueError('proof failed')
    def forbidden(*_):
        raise AssertionError('failed proof cannot advance')
    monkeypatch.setattr(checkpoints, 'wait_for_release', forbidden)
    with pytest.raises(ValueError, match='proof failed'):
        checkpoints.checkpoint_and_wait(campaign, cp, ready_callback=failed)
    cost = json.loads((campaign.ctx.out / 'training-checkpoint-cost.json').read_text())
    assert cost['upload_success'] is None and cost['ready_callback_seconds'] >= 0


@pytest.mark.parametrize('field,value', [('collector', 'obi'), ('smoke', True),
    ('system', 'petclinic'), ('toolchain_execution', 'local')])
def test_other_cells_cannot_opt_into_preflight(parent, field, value):
    campaign, cp, ready = parent
    setattr(campaign, field, value)
    with pytest.raises(ValueError, match='scope'):
        remote.prepare_parent_checkpoint(campaign, cp, ready, [])


def test_running_seed7_has_no_new_schedule(parent):
    campaign, cp, ready = parent
    campaign.ctx.seed = 7
    with pytest.raises(ValueError, match='scope'):
        remote.prepare_parent_checkpoint(campaign, cp, ready, [])


@pytest.mark.parametrize('failure', [None, 'live_SQL', 'ambiguous_POST'])
def test_actual_once_POST_precedes_live_proof_and_all_failures_block_import(tmp_path, monkeypatch, failure):
    events = []
    out = tmp_path / 'campaign'
    out.mkdir()
    campaign = SimpleNamespace(ctx=SimpleNamespace(out=out, mode='absent', seed=6),
        system='otel_demo', collector='deepflow', smoke=False, toolchain_execution='worker',
        store=SimpleNamespace(db=object()))
    identity = {'run_id': '77', 'commit': 'c' * 40, 'system': 'otel_demo',
                'mode': 'absent', 'seed': 6, 'manifest_sha256': 'm' * 64}
    prepared = {'index_reference': {'logical_proof': {'spans': 'same'}}}
    monkeypatch.setattr(remote, '_expected', lambda *_: (dict(identity), {}))
    monkeypatch.setattr(remote, '_bound_parent_preflight', lambda *_: prepared)
    state = out / 'infrastructure/remote-toolchain-v4'
    state.mkdir(parents=True)
    (state / 'upload-hold-preflight.json').write_text('{}', encoding='utf-8')
    def no_repeat(*_):
        raise AssertionError('original SQL reference was already computed during upload')
    monkeypatch.setattr(remote, '_checkpoint_index_reference', no_repeat)
    def mirror(*_, **__):
        assert events == ['POST']
        events.append('release_verified_mirror')
        return {'status': 'released_verified_local_payload'}
    monkeypatch.setattr(remote, '_release_uploaded_checkpoint_copy', mirror)
    def live(*_, **__):
        assert events == ['POST', 'release_verified_mirror']
        retained_cost = json.loads((state / 'cost.json').read_text())
        assert retained_cost['uploaded_checkpoint_copy_release']['status'] == 'released_verified_local_payload'
        events.append('full_live_proof')
        return {'spans': 'changed' if failure == 'live_SQL' else 'same'}
    monkeypatch.setattr(remote, '_consistent_live_index_proof', live)
    class Session:
        def post(self, *_, **__):
            assert events == []
            events.append('POST')
            if failure == 'ambiguous_POST':
                raise requests.Timeout('ambiguous')
            return FakeResponse(value={'workflow_run_id': 91})
        def get(self, *_, **__):
            assert events == ['POST', 'release_verified_mirror', 'full_live_proof']
            raise RuntimeError('stop after complete parent proof')
    monkeypatch.setattr(remote.requests, 'Session', Session)
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setenv('GH_TOKEN', 'synthetic')
    monkeypatch.setenv('GITHUB_REPOSITORY', 'owner/repo')
    message = {'live_SQL': 'differs from its closed', 'ambiguous_POST': 'ambiguous',
               None: 'stop after complete parent proof'}[failure]
    with pytest.raises(RuntimeError, match=message):
        remote.forecast_on_worker(campaign, tmp_path / 'checkpoint', {}, [])
    assert events.count('POST') == 1
    assert not (out / 'toolchain').exists() and not (state / 'parent-import.json').exists()
    if failure == 'ambiguous_POST':
        assert events == ['POST']
        assert not (state / 'parent-proof-schedule.json').exists()
    elif failure is None:
        proof = json.loads((state / 'parent-proof-schedule.json').read_text())
        assert proof['status'] == 'complete'
        assert proof['worker_run_id'] == 91
        assert proof['confirmed_dispatch_ns'] <= proof['parent_proof_started_ns'] <= proof['parent_proof_ended_ns']
        index = json.loads((state / 'training-index-proof.json').read_text())
        assert index['parent_after_dispatch_before_import'] == index['checkpoint']
        assert 'parent_before_dispatch' not in index
    else:
        proof = json.loads((state / 'parent-proof-schedule.json').read_text())
        assert proof['status'] == 'failed' and 'differs from its closed' in proof['error']
        cost = json.loads((state / 'cost.json').read_text())
        assert cost['parent_after_dispatch_proof_seconds'] >= 0
