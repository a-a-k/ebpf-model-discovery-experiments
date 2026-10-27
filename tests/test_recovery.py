import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import ebpf_discovery.recover as recovery


def complete_capture(tmp_path):
    def put(name, value):
        path = tmp_path/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
    put('status.json', {'status': 'acquisition_complete', 'system': 'otel_demo', 'commit': 'a'*40})
    put('parse-errors-final.json', [])
    put('normalized-final.json', [])
    counts = {'class_train': 120, 'calibration': 960, 'target': 960, 'class_test': 120,
              'db_up': 20, 'db_down': 20, 'async_normal': 20, 'async_paused': 20, 'async_recovered': 20}
    records = [{'phase': phase} for phase, count in counts.items() for _ in range(count)]
    put('external.json', records)
    put('census.json', records)
    put('blocks.json', [{'phase': 'calibration', 'state': s} for s in ('11', '10', '01', '00')]
        + [{'phase': 'target', 'state': s} for s in ['11']*4+['10']*2+['01', '00']])
    for source in ('ebpf', 'native', 'combined'):
        for name in ('model.json', 'forecast.json', 'evaluation-map.json', 'calibration-assignments.json'):
            put(f'models/{source}/{name}', {})
    frozen = tmp_path/'models/ebpf/target-assignments.json'
    frozen.write_bytes(b'[ { "original": true } ]\n')
    return frozen


def mock_git(monkeypatch, *, matching=True):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setattr(recovery.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0))
    repository = Path(recovery.__file__).resolve().parents[2]
    monkeypatch.setattr(recovery.subprocess, 'check_output',
                        lambda args, **kwargs: (repository/args[-1].split(':', 1)[1]).read_bytes() if matching else b'different code')


def test_recovery_rejects_changed_projection_code(tmp_path, monkeypatch):
    complete_capture(tmp_path)
    mock_git(monkeypatch, matching=False)
    monkeypatch.setattr(recovery, 'evaluate', lambda root: pytest.fail('evaluation must not run'))
    with pytest.raises(RuntimeError, match='code differs'):
        recovery.recover(tmp_path)


def test_recovery_preserves_existing_assignment_bytes(tmp_path, monkeypatch):
    frozen = complete_capture(tmp_path)
    original = frozen.read_bytes()
    mock_git(monkeypatch)
    monkeypatch.setattr(recovery, 'evaluate', lambda root: {})
    recovery.recover(tmp_path)
    assert frozen.read_bytes() == original
    assert json.loads((tmp_path/'evaluation-recovery.json').read_text())['status'] == 'completed'


def test_recovery_rejects_mutation_of_frozen_inputs(tmp_path, monkeypatch):
    frozen = complete_capture(tmp_path)
    mock_git(monkeypatch)
    def corrupt(root):
        frozen.write_text('[]')
        return {}
    monkeypatch.setattr(recovery, 'evaluate', corrupt)
    with pytest.raises(RuntimeError, match='Protected acquisition input changed'):
        recovery.recover(tmp_path)


def test_recovery_rejects_incomplete_capture(tmp_path, monkeypatch):
    complete_capture(tmp_path)
    mock_git(monkeypatch)
    (tmp_path/'external.json').write_text('[]')
    with pytest.raises(RuntimeError, match='Incomplete acquisition records'):
        recovery.recover(tmp_path)
