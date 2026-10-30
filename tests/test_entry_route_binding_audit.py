import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from ebpf_discovery.store_v3 import normalized_file
from ebpf_discovery.store_v5 import _digest


spec = importlib.util.spec_from_file_location('entry_route_binding_audit',
    Path(__file__).parents[1] / 'scripts/audit-entry-route-binding.py')
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


@pytest.mark.parametrize('tamper', [None, 'source', 'digest'])
def test_saved_root_is_recovered_only_from_exact_hashed_native_segment(tmp_path, tamper):
    path = tmp_path / 'native/training/native-node-a.jsonl'
    path.parent.mkdir(parents=True)
    payload = {'resourceSpans': [{'resource': {'attributes': [
        {'key': 'service.name', 'value': {'stringValue': 'gateway'}}]},
        'scopeSpans': [{'spans': [{'kind': 2, 'name': 'GET customers',
            'attributes': [{'key': 'http.request.method', 'value': {'stringValue': 'GET'}},
                           {'key': 'url.path', 'value': {'stringValue': '/api/customer/owners'}},
                           {'key': 'http.route', 'value': {'stringValue': 'customers'}}]}]}]}]}
    body = (json.dumps(payload) + '\n').encode()
    path.write_bytes(body)
    row = next(normalized_file(path, 'native', 0, len(body)))
    digest = _digest(row)
    root = {'observation_digest': digest, 'observation_provenance': [{
        'raw_file': '/original/native/training/native-node-a.jsonl', 'from_byte': 0,
        'through_byte': len(body), 'normalized_ordinal': 0,
        'segment_sha256': hashlib.sha256(body).hexdigest()}]}
    if tamper == 'source':
        path.write_bytes(body.replace(b'customers', b'different'))
    elif tamper == 'digest':
        root['observation_digest'] = '0' * 64
    if tamper:
        with pytest.raises(ValueError):
            AUDIT.SavedRoots(tmp_path, [root])
    else:
        observed = AUDIT.SavedRoots(tmp_path, [root]).observation_v5(digest)
        assert observed['attributes']['http.route'] == 'customers'
        assert observed['attributes']['url.path'] == '/api/customer/owners'
