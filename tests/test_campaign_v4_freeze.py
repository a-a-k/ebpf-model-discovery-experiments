from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from ebpf_discovery import campaign_v4


def campaign(tmp_path):
    value = campaign_v4.CampaignV4.__new__(campaign_v4.CampaignV4)
    value.ctx = SimpleNamespace(out=tmp_path)
    value.system = 'otel_demo'
    value.store = object()
    value.declaration = object()
    value.plans = [{'phase': phase} for phase in ('class_train', 'calibration', 'target')]
    value.training_checkpoint = tmp_path/'checkpoint'
    value.training_release = {'upload_success': True}
    value.toolchain_execution = 'worker'
    value.frozen = {}
    return value


def test_remote_result_and_classes_are_frozen_before_validation(tmp_path, monkeypatch):
    value = campaign(tmp_path)
    forecast = {'unknown_branch': {'status': 'unknown', 'reason': 'missing evidence'}}
    calls = []

    def worker(current, checkpoint, release, plans):
        assert current is value and checkpoint == value.training_checkpoint
        assert release is value.training_release
        assert [p['phase'] for p in plans] == ['class_train', 'calibration']
        assert not (tmp_path/'forecast-saved.json').exists()
        calls.append('worker')
        (tmp_path/'toolchain').mkdir()
        (tmp_path/'toolchain'/'forecasts.json').write_text(json.dumps(forecast))
        return forecast

    def classes(store, plans, declaration, out):
        assert calls == ['worker']
        assert store is value.store and declaration is value.declaration
        assert not (tmp_path/'forecast-saved.json').exists()
        calls.append('classes')
        out.mkdir()
        (out/'classes-model.json').write_text('{"fitted":true}')

    monkeypatch.setitem(sys.modules, 'ebpf_discovery.remote_toolchain_v4',
                        SimpleNamespace(forecast_on_worker=worker))
    monkeypatch.setattr(campaign_v4, 'fit_classes', classes)
    assert value.freeze() == forecast
    frozen = json.loads((tmp_path/'forecast-saved.json').read_text())
    assert calls == ['worker', 'classes']
    assert {Path(path).as_posix() for path in frozen['sha256_by_path']} == {
        'toolchain/forecasts.json', 'toolchain/classes/classes-model.json'}
    assert all(campaign_v4.digest(tmp_path/path) == sha
               for path, sha in frozen['sha256_by_path'].items())


def test_worker_failure_cannot_publish_a_frozen_forecast(tmp_path, monkeypatch):
    value = campaign(tmp_path)

    def failed(*args):
        raise RuntimeError('worker artifact identity mismatch')

    monkeypatch.setitem(sys.modules, 'ebpf_discovery.remote_toolchain_v4',
                        SimpleNamespace(forecast_on_worker=failed))
    monkeypatch.setattr(campaign_v4, 'fit_classes',
                        lambda *args: pytest.fail('classes must not fit after failed worker'))
    with pytest.raises(RuntimeError, match='artifact identity mismatch'):
        value.freeze()
    assert not (tmp_path/'forecast-saved.json').exists()
    assert not value.frozen


def test_worker_requires_live_checkpoint_before_any_preparation(tmp_path):
    with pytest.raises(ValueError, match='full live campaign'):
        campaign_v4.CampaignV4('otel_demo', 'full', 6, tmp_path,
                               toolchain_execution='worker')
    with pytest.raises(ValueError, match='full live campaign'):
        campaign_v4.CampaignV4('otel_demo', 'full', 6, tmp_path,
                               qualification=True, training_checkpoint=Path('checkpoint'),
                               toolchain_execution='worker')
    assert not list(tmp_path.iterdir())


def test_worker_cannot_start_before_checkpoint_release(tmp_path):
    value = campaign(tmp_path)
    value.training_release = None
    with pytest.raises(RuntimeError, match='checkpoint release'):
        value.freeze()
    assert not (tmp_path/'forecast-saved.json').exists()
