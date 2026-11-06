"""Qualification provenance boundaries; tiny metadata only, no research execution."""
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from ebpf_discovery import block_v6 as b
from ebpf_discovery import qualification_replay_v6 as q
from ebpf_discovery.plan_v6 import COLLECTORS, STUDY


@pytest.fixture
def reviewed_parent(tmp_path, monkeypatch):
    monkeypatch.setattr(b, 'repo', lambda: tmp_path)
    monkeypatch.setattr(b, 'gate', lambda stage: None)
    monkeypatch.setenv('GITHUB_RUN_ID', '200')
    monkeypatch.setenv('GITHUB_SHA', 'a' * 40)
    subprocess.run(['git', 'init', '--quiet', str(tmp_path)], check=True)
    (tmp_path / 'docs').mkdir()
    path = Path('docs/parent.json')
    def artifact(index, name):
        return {'id': index, 'name': name, 'size_in_bytes': 10,
                'digest': 'sha256:' + 'c' * 64}
    value = {'schema': q.SCHEMA, 'study': STUDY, 'stage': 'qualification',
             'system': 'deathstarbench', 'mode': 'full', 'repetition': 9, 'smoke': True,
             'parent_run_id': 100, 'parent_source': 'b' * 40,
             'root_inspection_GO': True, 'independent_inspection_GO': True,
             'root_replay_GO': False, 'independent_replay_GO': False,
             'shared_artifact': artifact(1, 'v6-shared-blueprint-100'),
             'training_artifacts': {c: artifact(i + 2, f'v6-training-{c}-100')
                                    for i, c in enumerate(COLLECTORS)}}
    def save():
        raw = (json.dumps(value) + '\n').encode('utf8')
        (tmp_path / path).write_bytes(raw)
        subprocess.run(['git', 'add', '--', path.as_posix()], cwd=tmp_path, check=True)
        return hashlib.sha256(raw).hexdigest()
    return value, path, save


def test_inspection_approval_does_not_authorize_models_or_targets(reviewed_parent):
    value, path, save = reviewed_parent
    seal = save()
    assert q.record(path, seal)['parent_run_id'] == 100
    with pytest.raises(ValueError, match='separately reviewed'):
        q.record(path, seal, replay=True)


@pytest.mark.parametrize('field,bad', [('stage', 'main'), ('study', 'historical-v5')])
def test_main_or_historical_capture_cannot_enter_qualification_continuation(reviewed_parent, field, bad):
    value, path, save = reviewed_parent
    value[field] = bad
    with pytest.raises(ValueError, match='qualification parent'):
        q.record(path, save())


def test_parent_cannot_change_after_approval(reviewed_parent):
    value, path, save = reviewed_parent
    original = save()
    value['parent_source'] = 'd' * 40
    save()
    with pytest.raises(ValueError, match='bytes differ'):
        q.record(path, original)


def test_replay_needs_all_four_actual_closures_and_common_seals(reviewed_parent):
    value, path, save = reviewed_parent
    value.update(root_replay_GO=True, independent_replay_GO=True)
    with pytest.raises(ValueError, match='actual inspected inner seal'):
        q.record(path, save(), replay=True)
    value.update({key: 'd' * 64 for key in ('inspection_report_sha256', 'parent_plan_sha256',
                 'shared_sha256', 'golden_sha256', 'blueprint_sha256')})
    value['closed_input_sha256_by_collector'] = {c: 'e' * 64 for c in COLLECTORS}
    assert q.record(path, save(), replay=True)['root_replay_GO'] is True
    del value['closed_input_sha256_by_collector']['none']
    with pytest.raises(ValueError, match='all four actual inspected'):
        q.record(path, save(), replay=True)


@pytest.mark.parametrize('stage,phase', [('main', 'validation'), ('qualification', 'training')])
def test_private_prepared_plan_does_not_relax_main_or_training(tmp_path, monkeypatch, stage, phase):
    monkeypatch.setattr(b, 'gate', lambda stage: None)
    monkeypatch.setattr(b, 'owned_root', lambda root: tmp_path)
    with pytest.raises(ValueError, match='qualification-validation only'):
        b.capture_slot(SimpleNamespace(stage=stage, phase=phase, root=tmp_path), prepared_plan=True)
