from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest

from ebpf_discovery.checkpoint_v4 import (
    _inside, _runtime_observation_dependencies, create_checkpoint, wait_for_release)
from ebpf_discovery.store_v3 import ObservationStore
from ebpf_discovery.toolchain_v4 import PINS
from ebpf_discovery.toolchain_v5 import PINS as V5_PINS
from ebpf_discovery.transport_v4 import Journal


def _json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + '\n', encoding='utf-8')


def _capture(tmp_path: Path, monkeypatch, *, ingest=True, metadata_reference=True):
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
    metadata = {'source': 'ebpf:a', 'node': 'a', 'received_ns': 1,
                'content_type': 'application/json', 'content_encoding': '',
                'content_headers': {'content-type': 'application/json'},
                'raw_size_bytes': len(body), 'raw_sha256': hashlib.sha256(body).hexdigest(),
                'raw_ref': wire.relative_to(observations).as_posix()}
    _json(wire.parent/'metadata.json', metadata)
    wrapper = {**metadata, 'payload': payload, 'id_encoding': 'hex',
               'raw_metadata_ref': (wire.parent/'metadata.json').relative_to(observations).as_posix()}
    if not metadata_reference:
        wrapper.pop('raw_metadata_ref')
    prefix = (json.dumps(wrapper) + '\n').encode()
    source = observations/'a.jsonl'
    source.write_bytes(prefix)
    native = live/'native'
    native.mkdir()
    store = ObservationStore(live/'observation-index.sqlite')
    if ingest:
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
        copied_metadata = folder/'observations'/'a.raw'/'one'/'metadata.json'
        assert json.loads(copied_metadata.read_text())['raw_sha256'] == hashlib.sha256(body).hexdigest()
        assert (campaign.ctx.out/'observations'/'a.jsonl').stat().st_size > len(prefix)
        manifest_bytes = (folder/'manifest.json').read_bytes()
        assert ready['manifest_sha256'] == hashlib.sha256(manifest_bytes).hexdigest()
        manifest = json.loads(manifest_bytes)
        assert manifest['indexed_sources'][0]['consumed_prefix_bytes'] == len(prefix)
        assert manifest['referenced_wire_metadata'][0]['sha256'] == hashlib.sha256(
            copied_metadata.read_bytes()).hexdigest()
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


def test_graph_v5_checkpoint_binds_collector_and_common_binary_pins(tmp_path: Path, monkeypatch):
    campaign, _, _ = _capture(tmp_path, monkeypatch)
    try:
        live = campaign.ctx.out
        status = json.loads((live/'status.json').read_text())
        status.update(protocol_version='graph-v5', collector='coroot')
        _json(live/'status.json', status)
        _json(live/'observations'/'collector.json', {
            'schema': 'collector-lifecycle-v5', 'collector': 'coroot',
            'source_domain': 'ebpf-coroot'})
        _json(live/'runtime-identity-v5'/'inventory-training.json', {
            'schema': 'runtime-identity-inventory-v5', 'samples': [],
            'captures': [], 'capture_lifetimes': [], 'event_enclosures': []})
        rows = []
        for name, commit in V5_PINS.items():
            path = live/'toolchain-build'/'bin'/name.lower()
            data = ('v5-'+name).encode()
            path.write_bytes(data)
            rows.append({'name': name.lower(), 'commit': commit, 'binary': str(path.resolve()),
                         'binary_sha256': hashlib.sha256(data).hexdigest(),
                         'binary_bytes': len(data)})
        _json(live/'toolchain-build'/'toolchain-build.json', {
            'schema_version': 'toolchain-build-v4', 'binaries': rows})
        folder = tmp_path/'v5-checkpoint'
        create_checkpoint(campaign, folder)
        manifest = json.loads((folder/'manifest.json').read_text())
        assert manifest['collector_provenance']['collector'] == 'coroot'
        assert manifest['files']['observations/collector.json']['sha256'] == hashlib.sha256(
            (live/'observations'/'collector.json').read_bytes()).hexdigest()
        dependency = manifest['runtime_identity_dependencies'][0]
        relative = dependency['relative_path']
        assert relative == 'runtime-identity-v5/inventory-training.json'
        assert manifest['files'][relative]['sha256'] == hashlib.sha256(
            (live/relative).read_bytes()).hexdigest() == dependency['sha256']
        assert (folder/relative).read_bytes() == (live/relative).read_bytes()
        assert {row['commit'] for row in manifest['toolchain']['binaries']} == set(V5_PINS.values())
    finally:
        campaign.store.close()
        campaign.ctx.journal.close()


def test_runtime_locator_checkpoint_copies_deepflow_raw_snapshot_and_accounting(tmp_path: Path):
    live = tmp_path/'campaign'; checkpoint = tmp_path/'checkpoint'
    checkpoint.mkdir(); observations = live/'observations'
    raw = observations/'deepflow-raw'/'node-a'/'training'/'l7_flow_log'
    raw.parent.mkdir(parents=True)
    body = b'{"request":"retained"}\n'; raw.write_bytes(body)
    locator = {'source_file': 'a/l7_flow_log',
               'retained_file': raw.relative_to(observations).as_posix(),
               'offset': 0, 'length': len(body),
               'sha256': hashlib.sha256(body).hexdigest()}
    _json(raw.parent/'snapshot.json', {'files': [{
        'snapshot_name': raw.name, 'copied_bytes': len(body),
        'copied_sha256': hashlib.sha256(body).hexdigest()}]})
    _json(observations/'deepflow-codec-accounting.jsonl', {
        **locator, '_runtime_identity': {'locator': locator}, 'status': 'normalized'})
    with sqlite3.connect(checkpoint/'observation-index.sqlite') as db:
        db.execute('CREATE TABLE spans(digest TEXT, data TEXT)')
        db.execute('INSERT INTO spans VALUES (?,?)', ('digest', json.dumps({
            '_runtime_identity': {'locator': locator}})))
    copied = {}
    proofs = _runtime_observation_dependencies(live.resolve(), checkpoint, copied)
    assert len(proofs) == 1
    assert proofs[0]['locator'] == locator
    assert proofs[0]['codec_accounting_matching_rows'] == 1
    for relative in (raw.relative_to(live),
                     (raw.parent/'snapshot.json').relative_to(live),
                     (observations/'deepflow-codec-accounting.jsonl').relative_to(live)):
        assert (checkpoint/relative).read_bytes() == (live/relative).read_bytes()
        assert relative.as_posix() in copied


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


def test_empty_index_is_retained_as_unknown_evidence_not_checkpoint_failure(tmp_path: Path, monkeypatch):
    campaign, _, _ = _capture(tmp_path, monkeypatch, ingest=False)
    try:
        folder = tmp_path/'training-checkpoint'
        ready = create_checkpoint(campaign, folder)
        manifest = json.loads((folder/'manifest.json').read_text())
        assert ready['status'] == 'training_checkpoint_ready'
        assert manifest['indexed_sources'] == []
        assert manifest['referenced_wire_bodies'] == []
        assert manifest['referenced_wire_metadata'] == []
        assert manifest['metadata_reference_absent'] == []
        assert not (folder/'observations'/'a.jsonl').exists()
        with sqlite3.connect(folder/'observation-index.sqlite') as db:
            assert db.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
            assert db.execute('SELECT COUNT(*) FROM files').fetchone()[0] == 0
            assert db.execute('SELECT COUNT(*) FROM spans').fetchone()[0] == 0
        assert manifest['status'].startswith('partial_training_capture_only')
    finally:
        campaign.store.close()
        campaign.ctx.journal.close()


def test_missing_or_mispointed_wire_metadata_never_publishes_ready(tmp_path: Path, monkeypatch):
    campaign, _, _ = _capture(tmp_path, monkeypatch)
    try:
        metadata = campaign.ctx.out/'observations'/'a.raw'/'one'/'metadata.json'
        metadata.unlink()
        folder = tmp_path/'training-checkpoint'
        with pytest.raises(ValueError, match='checkpoint input is missing'):
            create_checkpoint(campaign, folder)
        assert not (folder/'ready.json').exists()
        outside = tmp_path/'outside.json'
        outside.write_text('{}')
        with pytest.raises(ValueError, match='outside live campaign'):
            _inside(outside, campaign.ctx.out.resolve())
    finally:
        campaign.store.close()
        campaign.ctx.journal.close()


def test_wire_metadata_must_match_indexed_wrapper_and_body(tmp_path: Path, monkeypatch):
    campaign, _, _ = _capture(tmp_path, monkeypatch)
    try:
        metadata = campaign.ctx.out/'observations'/'a.raw'/'one'/'metadata.json'
        document = json.loads(metadata.read_text())
        document['raw_ref'] = 'a.raw/another/body.json'
        _json(metadata, document)
        folder = tmp_path/'training-checkpoint'
        with pytest.raises(ValueError, match='differs from wrapper or wire body'):
            create_checkpoint(campaign, folder)
        assert not (folder/'ready.json').exists()
    finally:
        campaign.store.close()
        campaign.ctx.journal.close()


def test_unreferenced_metadata_is_disclosed_without_new_capture_gate(tmp_path: Path, monkeypatch):
    campaign, _, body = _capture(tmp_path, monkeypatch, metadata_reference=False)
    try:
        folder = tmp_path/'training-checkpoint'
        ready = create_checkpoint(campaign, folder)
        manifest = json.loads((folder/'manifest.json').read_text())
        assert ready['status'] == 'training_checkpoint_ready'
        assert (folder/'observations'/'a.raw'/'one'/'body.json').read_bytes() == body
        assert manifest['referenced_wire_metadata'] == []
        assert len(manifest['metadata_reference_absent']) == 1
        assert not (folder/'observations'/'a.raw'/'one'/'metadata.json').exists()
    finally:
        campaign.store.close()
        campaign.ctx.journal.close()
