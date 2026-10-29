"""Streaming must preserve evidence while avoiding whole-capture allocations."""
import hashlib
import json
from pathlib import Path
import tracemalloc

import pytest

from ebpf_discovery.store_v5 import ObservationStoreV5, _digest
from ebpf_discovery.store_v3 import normalized_file
from ebpf_discovery.supplied_alias_v5 import _verified_segment


def _receiver(tmp_path, count=1, padding=0):
    raw = tmp_path / 'body.pb'
    raw.write_bytes(b'original body')
    wrapper = {'source': 'ebpf-coroot:a', 'node': 'a', 'received_ns': 123,
               'raw_ref': raw.name, 'raw_metadata_ref': 'metadata.json',
               'raw_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
               'raw_size_bytes': raw.stat().st_size}
    (tmp_path / 'metadata.json').write_text(json.dumps(wrapper))
    wrapper['payload'] = {'resourceSpans': [{
        'resource': {'attributes': [{'key': 'service.name',
                                    'value': {'stringValue': '/docker/app'}}]},
        'scopeSpans': [{'spans': [{'traceId': '1' * 32, 'spanId': '2' * 16,
                                 'name': 'GET', 'kind': 'SPAN_KIND_CLIENT',
                                 'startTimeUnixNano': '1', 'endTimeUnixNano': '2'}]}]}]}
    wrapper['retained_padding'] = 'x' * padding
    path = tmp_path / 'a.jsonl'
    with path.open('wb') as stream:
        for _ in range(count):
            stream.write(json.dumps(wrapper).encode() + b'\n')
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    return path, path.stat().st_size, sha


def test_receiver_segment_keeps_exact_prefix_ordinals_and_detects_tampering(tmp_path):
    path, end, sha = _receiver(tmp_path, count=3)
    expected = {i: _digest(row) for i, row in enumerate(normalized_file(
        path, 'ebpf', 0, end))}
    with path.open('ab') as stream:
        stream.write(b'not part of the retained prefix')
    assert _verified_segment(path, 0, end, sha, 'a', 'ebpf-coroot', False) == {
        'node': 'a', 'sources': ['ebpf-coroot:a'], 'ordinals': expected}
    with pytest.raises(ValueError, match='source/node mismatch'):
        _verified_segment(path, 0, end, sha, 'a', 'ebpf-obi', False)
    (tmp_path / 'body.pb').write_bytes(b'changed body')
    with pytest.raises(ValueError, match='raw receiver body changed'):
        _verified_segment(path, 0, end, sha, 'a', 'ebpf-coroot', False)
    with pytest.raises(ValueError, match='receiver provenance changed'):
        _verified_segment(path, 0, end, '0' * 64, 'a', 'ebpf-coroot', False)


def test_receiver_segment_does_not_retain_all_wrappers(tmp_path):
    path, end, sha = _receiver(tmp_path, count=32, padding=512 * 1024)
    tracemalloc.start()
    try:
        result = _verified_segment(path, 0, end, sha, 'a', 'ebpf-coroot', False)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert len(result['ordinals']) == 32
    # The capture alone is >16 MiB; the parser needs only a few 512 KiB rows.
    assert peak < 8 * 1024 * 1024


def _store(tmp_path, services):
    store = ObservationStoreV5(tmp_path / 'index.sqlite')
    for index, service in enumerate(services):
        row = {'service': service, 'source': 'native' if service == 'native' else 'ebpf',
               'attributes': {}, 'ordinal': index}
        store.db.execute('INSERT INTO spans(digest,data,conflicted) VALUES (?,?,0)',
                         (f'{index:04d}', json.dumps(row)))
    store.db.commit()
    return store


PROOF = {'path': 'inventory.json', 'sha256': 'a' * 64, 'bytes': 123}


def _resolution(row, inventory):
    if row['service'] == 'native':
        return {'status': 'unknown', 'service_identity': None,
                'unknown_reasons': ['runtime_identity_unavailable']}
    return {'status': 'resolved', 'service_identity': {'compose_service': 'app'}}


def test_projection_matches_pre_streaming_mixed_row_bytes_and_preserves_training(
        tmp_path, monkeypatch):
    monkeypatch.setattr('ebpf_discovery.store_v5.resolve', _resolution)
    store = _store(tmp_path, ['unknown', 'app', 'other', 'native'])
    out = tmp_path / 'projection.jsonl'
    summary = store.apply_runtime_identity({}, out, inventory_proof=PROOF, stage='training')
    expected = Path(__file__).with_name('fixtures') / 'projection-v5-pre-streaming.jsonl'
    assert out.read_text() == expected.read_text()
    assert summary['counts'] == dict(resolved_enriched=1, resolved_existing=1,
                                     label_conflict=1, unknown=1)
    assert summary['rows'] == 4
    assert summary['sha256'] == hashlib.sha256(out.read_bytes()).hexdigest()
    before = list(store.db.execute('SELECT * FROM runtime_identity_projection ORDER BY digest'))
    monkeypatch.setattr('ebpf_discovery.store_v5.resolve', lambda *_: {
        'status': 'unknown', 'service_identity': None, 'unknown_reasons': ['changed']})
    store.apply_runtime_identity({}, out, inventory_proof=PROOF, stage='final')
    assert list(store.db.execute('SELECT * FROM runtime_identity_projection ORDER BY digest')) == before
    assert all(json.loads(line)['existing_projection_retained'] for line in out.read_text().splitlines())
    store.close()


def test_projection_error_rolls_back_and_keeps_previous_file(tmp_path, monkeypatch):
    store = _store(tmp_path, ['unknown', 'app'])
    out = tmp_path / 'projection.jsonl'
    out.write_bytes(b'previous complete proof\n')
    def resolve(row, inventory):
        if row['ordinal'] == 1:
            raise ValueError('synthetic resolver failure')
        return _resolution(row, inventory)
    monkeypatch.setattr('ebpf_discovery.store_v5.resolve', resolve)
    with pytest.raises(ValueError, match='synthetic resolver failure'):
        store.apply_runtime_identity({}, out, inventory_proof=PROOF, stage='training')
    assert out.read_bytes() == b'previous complete proof\n'
    assert store.db.execute('SELECT COUNT(*) FROM runtime_identity_projection').fetchone()[0] == 0
    assert list(tmp_path.glob('*.pending')) == []
    store.close()


def test_projection_does_not_retain_every_serialized_row(tmp_path, monkeypatch):
    store = _store(tmp_path, ['native'] * 128)
    monkeypatch.setattr('ebpf_discovery.store_v5.resolve', lambda *_: {
        'status': 'unknown', 'service_identity': None, 'unknown_reasons': ['unavailable'],
        'retained_test_payload': 'x' * (256 * 1024)})
    out = tmp_path / 'projection.jsonl'
    tracemalloc.start()
    try:
        result = store.apply_runtime_identity({}, out, inventory_proof=PROOF, stage='training')
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result['rows'] == 128
    assert out.stat().st_size > 32 * 1024 * 1024
    assert peak < 8 * 1024 * 1024
    store.close()
