from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest

from ebpf_discovery.checkpoint_v4 import create_checkpoint, wait_for_release
from ebpf_discovery.store_v3 import ObservationStore
from ebpf_discovery.toolchain_v4 import PINS
from ebpf_discovery.transport_v4 import Journal


def _json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + '\n', encoding='utf-8')


def _capture(tmp_path: Path, monkeypatch):
    monkeypatch.setenv('GITHUB_RUN_ID', '12345')
    monkeypatch.setenv('GITHUB_SHA', 'a' * 40)
    live = tmp_path/'campaign'
    live.mkdir()
    for name in ('plans.json', 'external.json', 'census.json', 'blocks.json',
                 'preparation-operations.json', 'deployment.json', 'index-training.json'):
        _json(live/name, [] if name not in ('deployment.json', 'index-training.json') else {})
    _json(live/'status.json', {'system': 'petclinic', 'mode': 'full', 'seed': 6,
                              'commit': 'a' * 40, 'run_id': '12345', 'status': 'running'})
    _json(live/'deployment'/'petclinic'/'node-a'/'compose.yml', {'services': {'api': {}}})

    payload = {'resourceSpans': [{'resource': {'attributes': [
        {'key': 'service.name', 'value': {'stringValue': 'api'}}]},
        'scopeSpans': [{'spans': [{'traceId': '1' * 32, 'spanId': '2' * 16,
                                   'startTimeUnixNano': '1', 'endTimeUnixNano': '2'}]}]}]}
    observations = live/'observations'
    body = (json.dumps(payload) + '\n').encode()
    wire = observations/'a.raw'/'one'/'body.json'
    wire.parent.mkdir(parents=True)
    wire.write_bytes(body)
    wrapper = {'payload': payload, 'id_encoding': 'hex',
               'raw_ref': wire.relative_to(observations).as_posix(),
               'raw_sha256': hashlib.sha256(body).hexdigest(),
               'content_type': 'application/json'}
    prefix = (json.dumps(wrapper) + '\n').encode()
    source = observations/'a.jsonl'
    source.write_bytes(prefix)
    native = live/'native'
    native.mkdir()
    store = ObservationStore(live/'observation-index.sqlite')
    store.ingest(observations, native)
    # This complete later line is deliberately absent from files.consumed.
    source.write_bytes(prefix + (json.dumps({'payload': payload}) + '\n').encode())
    journal = Journal(live/'attempt-journal.sqlite')
    journal.append('attempt_intent', attempt_id='training-1')

    build = live/'toolchain-build'
    binary_rows = []
    for name, commit in PINS.items():
        path = build/'bin'/name.lower()
        path.parent.mkdir(parents=True, exist_ok=True)
        data = ('synthetic-'+name).encode()
        path.write_bytes(data)
        binary_rows.append({'name': name.lower(), 'commit': commit,
                            'binary': str(path.resolve()), 'binary_sha256': hashlib.sha256(data).hexdigest(),
                            'binary_bytes': len(data)})
    _json(build/'toolchain-build.json', {'schema_version': 'toolchain-build-v4',
                                         'binaries': binary_rows})
    campaign = SimpleNamespace(ctx=SimpleNamespace(out=live, mode='full', seed=6, journal=journal),
                               system='petclinic', store=store)
    return campaign, prefix, body


def test_checkpoint_is_closed_training_prefix_with_independent_sqlite_backups(tmp_path: Path, monkeypatch):
    campaign, prefix, body = _capture(tmp_path, monkeypatch)
    try:
        folder = tmp_path/'training-checkpoint'
        ready = create_checkpoint(campaign, folder)
        assert ready['status'] == 'training_checkpoint_ready'
        assert (folder/'observations'/'a.jsonl').read_bytes() == prefix
        assert (folder/'observations'/'a.raw'/'one'/'body.json').read_bytes() == body
        assert (campaign.ctx.out/'observations'/'a.jsonl').stat().st_size > len(prefix)
        manifest_bytes = (folder/'manifest.json').read_bytes()
        assert ready['manifest_sha256'] == hashlib.sha256(manifest_bytes).hexdigest()
        manifest = json.loads(manifest_bytes)
        assert manifest['indexed_sources'][0]['consumed_prefix_bytes'] == len(prefix)
        assert manifest['files']['observations/a.jsonl']['sha256'] == hashlib.sha256(prefix).hexdigest()
        assert {item['name'] for item in manifest['toolchain']['binaries']} == {
            name.lower() for name in PINS}
        with sqlite3.connect(folder/'observation-index.sqlite') as db:
            assert db.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
            assert db.execute('SELECT consumed FROM files').fetchone()[0] == len(prefix)
            assert db.execute('SELECT COUNT(*) FROM spans').fetchone()[0] == 1
        with sqlite3.connect(folder/'attempt-journal.sqlite') as db:
            assert db.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
            assert db.execute('SELECT COUNT(*) FROM events').fetchone()[0] == 1
        campaign.ctx.journal.append('later_event')
        with sqlite3.connect(folder/'attempt-journal.sqlite') as db:
            assert db.execute('SELECT COUNT(*) FROM events').fetchone()[0] == 1
    finally:
        campaign.store.close()
        campaign.ctx.journal.close()


def test_release_requires_exact_binding_and_upload_success(tmp_path: Path, monkeypatch):
    campaign, _, _ = _capture(tmp_path, monkeypatch)
    try:
        folder = tmp_path/'training-checkpoint'
        ready = create_checkpoint(campaign, folder)
        _json(folder/'release.json', {**ready, 'manifest_sha256': '0' * 64,
                                      'upload_success': True})
        with pytest.raises(ValueError, match='manifest_sha256'):
            wait_for_release(campaign, folder, ready)
        _json(folder/'release.json', {**ready, 'upload_success': False})
        with pytest.raises(RuntimeError, match='no forecast'):
            wait_for_release(campaign, folder, ready)
        assert campaign.ctx.journal.db.execute(
            "SELECT COUNT(*) FROM events WHERE kind='training_checkpoint_release'").fetchone()[0] == 1
        assert not (campaign.ctx.out/'toolchain').exists()
    finally:
        campaign.store.close()
        campaign.ctx.journal.close()
