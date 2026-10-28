from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ebpf_discovery.model_figure_v4 import dot_from_model, main, render_saved_model


def model():
    return {
        'services': [
            {'id': 'api', 'name': 'api', 'replicas': 1},
            {'id': 'api-alias', 'name': 'api', 'replicas': 1},
            {'id': 'database:opaque', 'name': 'database:opaque', 'replicas': 1,
             'metadata': {'labels': {'bering.node.kind': 'database',
                                     'bering.database.identity': 'logical_endpoint',
                                     'db.system.name': 'postgresql',
                                     'server.address': 'db.internal', 'server.port': '5432'}}},
        ],
        'edges': [
            {'id': 'first', 'from': 'api', 'to': 'database:opaque', 'kind': 'sync',
             'identity': {'protocol': 'http', 'operation': 'GET', 'route': '/items'}},
            {'id': 'second', 'from': 'api', 'to': 'database:opaque', 'kind': 'async',
             'identity': {'topic': 'saved-topic'}},
            {'id': 'third', 'from': 'api-alias', 'to': 'api', 'kind': 'sync'},
        ],
        'endpoints': [{'id': 'api:GET /items', 'entry_service': 'api',
                       'method': 'GET', 'path': '/items'}],
    }


def test_dot_keeps_distinct_alias_nodes_parallel_edges_and_observed_db_label():
    dot = dot_from_model(model(), 'a' * 64)
    assert 'Original observed.json SHA-256: ' + 'a' * 64 in dot
    assert dot.count(' -> ') == 3
    assert '"api" [' in dot and '"api-alias" [' in dot
    assert dot.count('"api" -> "database:opaque"') == 2
    assert 'postgresql database (logical_endpoint)' in dot
    assert 'db.internal:5432' in dot
    assert 'entry: GET /items' in dot
    assert 'style="dashed"' in dot
    assert 'placement' not in dot.lower()


def test_synthetic_saved_render_records_exact_input_hash_and_all_ids(tmp_path: Path, monkeypatch):
    source = tmp_path/'observed.json'
    raw = json.dumps(model(), indent=2).encode()
    source.write_bytes(raw)
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    result = render_saved_model(source, tmp_path/'figure', svg=False)
    assert result['original_model_sha256'] == hashlib.sha256(raw).hexdigest()
    assert result['service_ids'] == ['api', 'api-alias', 'database:opaque']
    assert [edge['id'] for edge in result['edges']] == ['first', 'second', 'third']
    assert result['endpoint_ids'] == ['api:GET /items']
    assert Path(result['dot_path']).exists()
    assert json.loads((tmp_path/'figure.figure.json').read_text()) == result
    assert source.read_bytes() == raw


def test_cli_level_file_render_guard_and_invalid_graph(tmp_path: Path, monkeypatch):
    source = tmp_path/'observed.json'
    source.write_text(json.dumps(model()))
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    with pytest.raises(RuntimeError, match='only in GitHub Actions'):
        main(['--input', str(source), '--out-prefix', str(tmp_path/'blocked')])
    assert not (tmp_path/'blocked.dot').exists()
    broken = model()
    broken['edges'][0]['to'] = 'absent'
    with pytest.raises(ValueError, match='absent service'):
        dot_from_model(broken, 'b' * 64)
    broken = model()
    broken['services'].append(dict(broken['services'][0]))
    with pytest.raises(ValueError, match='duplicate Bering service ID'):
        dot_from_model(broken, 'b' * 64)
