"""Evidence equivalence and bounded body retention for journal indexing."""
import importlib.util
import json
from pathlib import Path
import tracemalloc

import pytest

from ebpf_discovery.identity_projection_v5 import _journal_transports, _load_transport
from ebpf_discovery.transport_v4 import Journal


def _original():
    path = Path(__file__).parent / 'fixtures' / 'journal_identity_v5_before.py'
    spec = importlib.util.spec_from_file_location('journal_before', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._journal_transports


def _pair(journal, identity, request_id, **extra):
    journal.append('step_started', transport_id=identity, request_id=request_id)
    journal.append('step_finished', transport_id=identity, request_id=request_id, **extra)


def _bytes(value):
    # Same byte serialization as enclosure evidence; Unicode and whitespace retained in data_json.
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def test_original_transport_evidence_bytes_and_ambiguities(tmp_path):
    journal = Journal(tmp_path / 'journal.sqlite')
    _pair(journal, 'valid', 'valid', body='Ответ\nwith whitespace', status_code=503,
          response_body_base64='AA==')
    _pair(journal, 'none', None)
    _pair(journal, 'duplicate-a', 'duplicate')
    _pair(journal, 'duplicate-b', 'duplicate')
    _pair(journal, 'duplicate-c', 'duplicate')
    _pair(journal, 'multiple-terminal', 'multiple-terminal')
    journal.append('step_finished', transport_id='multiple-terminal', request_id='multiple-terminal')
    journal.append('step_started', transport_id='unknown', request_id='unknown')
    journal.append('step_transport_unknown', transport_id='unknown', request_id='unknown')
    journal.append('step_started', transport_id='unmatched', request_id='start')
    journal.append('step_finished', transport_id='unmatched', request_id='end')
    journal.append('step_started', request_id='no-transport')
    expected = _original()(journal)
    references = _journal_transports(journal)
    actual = {key: _load_transport(journal, value) if value else None
              for key, value in references.items()}
    assert actual == expected
    for key in actual:
        assert _bytes(actual[key]) == _bytes(expected[key])
    assert set(actual) == {'valid', None, 'duplicate'}
    assert actual['duplicate'] is None
    journal.close()


@pytest.mark.parametrize('mutation', ['body', 'timestamp', 'delete'])
def test_late_hydration_rejects_changed_original_event(tmp_path, mutation):
    journal = Journal(tmp_path / 'journal.sqlite')
    _pair(journal, 't', 'r', body='original')
    reference = _journal_transports(journal)['r']
    seq = reference['terminal']['seq']
    if mutation == 'body':
        journal.db.execute("UPDATE events SET data=json_set(data,'$.body','changed') WHERE seq=?", (seq,))
    elif mutation == 'timestamp':
        journal.db.execute('UPDATE events SET monotonic_ns=monotonic_ns+1 WHERE seq=?', (seq,))
    else:
        journal.db.execute('DELETE FROM events WHERE seq=?', (seq,))
    journal.db.commit()
    with pytest.raises(ValueError, match='journal event changed'):
        _load_transport(journal, reference)
    journal.close()


def test_append_does_not_change_captured_prefix(tmp_path):
    journal = Journal(tmp_path / 'journal.sqlite')
    _pair(journal, 't', 'r', body='original')
    expected = _original()(journal)['r']
    reference = _journal_transports(journal)['r']
    journal.append('step_finished', transport_id='t', request_id='r', body='later duplicate')
    assert _load_transport(journal, reference) == expected
    assert 'r' not in _journal_transports(journal)
    journal.close()


def test_large_bodies_are_not_retained_by_index(tmp_path):
    journal = Journal(tmp_path / 'journal.sqlite')
    # Synthetic storage regression, not a workload/result cutoff.
    for index in range(32):
        _pair(journal, str(index), str(index), body='x' * (256 * 1024),
              response_body_base64='y' * (256 * 1024))
    tracemalloc.start()
    references = _journal_transports(journal)
    retained, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(references) == 32
    assert retained < 512 * 1024
    assert peak < 8 * 1024 * 1024
    assert 'data' not in references['0']['terminal']
    assert _load_transport(journal, references['31'])['terminal']['data']['body'] == 'x' * (256 * 1024)
    journal.close()
