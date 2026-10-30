from copy import deepcopy
import hashlib
import json
from types import SimpleNamespace

import pytest

from ebpf_discovery.supplied_alias_v5 import semantic_view
from ebpf_discovery.toolchain_v4 import Toolchain as LegacyToolchain, reachable
from ebpf_discovery.toolchain_v5 import Toolchain, attach_operation_metadata


def model():
    return {'services': [{'id': name, 'name': name, 'replicas': 1}
                         for name in ('gateway', 'visits-service', '/docker/visits-a', '/docker/visits-b', 'db')],
            'edges': [{'id': 'native-app', 'from': 'gateway', 'to': 'visits-service', 'kind': 'sync'},
                      {'id': 'raw-docker-db', 'from': '/docker/visits-a', 'to': 'db', 'kind': 'sync',
                       'observed': {'latency': 'unchanged'}}],
            'endpoints': [{'id': 'owners', 'entry_service': 'gateway', 'success_predicate_ref': 'old',
                           'metadata': {'semantics': {'dependency_modes': ['sync'], 'confidence': 0.5}}}],
            'metadata': {'discovered_at': 'original-structural-discovery'}}


def overlay():
    return {'name': 'provided', 'services': [{'id': 'visits-service', 'replicas': 2,
        'failure_eligible': True, 'placements': [{'replicas': 1, 'labels': {'guest': node}}
                                              for node in ('a', 'b')],
        'attributes': {'procrustes.workload': 'provided/workload'}}],
        'endpoints': [{'id': 'owners', 'predicate_ref': 'operation',
                       'semantics': {'predicate_mode': 'external_predicate', 'source': 'supplied_source_contract'}}]}


def test_provided_metadata_does_not_reopen_the_raw_aliases_or_break_required_edge_reachability():
    raw = model(); original = deepcopy(raw)
    canonical, quality, proof = semantic_view(raw, {}, {}, {
        '/docker/visits-a': 'visits-service', '/docker/visits-b': 'visits-service'})
    assert proof['metadata_collisions'] == []
    before = deepcopy(canonical); supplied = overlay(); supplied_before = deepcopy(supplied)
    attached = attach_operation_metadata(canonical, supplied)
    assert raw == original and canonical == before and supplied == supplied_before
    assert attached['edges'] == before['edges']
    assert attached['metadata'] == before['metadata']
    assert reachable(attached, 'gateway', 'visits-service')
    edge = next(e for e in attached['edges'] if e['id'] == 'raw-docker-db')
    assert edge['from'] == 'visits-service' and reachable(attached, 'gateway', edge['from'])
    visits = next(s for s in attached['services'] if s['id'] == 'visits-service')
    assert visits['replicas'] == 2
    assert {p['labels']['guest'] for p in visits['metadata']['placements']} == {'a', 'b'}
    assert 'attributes' not in visits['metadata']
    assert attached['endpoints'][0]['metadata']['semantics'] == {
        'dependency_modes': ['sync'], 'confidence': 0.5,
        'predicate_mode': 'external_predicate', 'source': 'supplied_source_contract'}


@pytest.mark.parametrize('bad', [
    {'services': [{'id': 'unobserved', 'replicas': 2}]},
    {'endpoints': [{'id': 'unobserved', 'predicate_ref': 'operation'}]},
    {'edges': [{'id': 'invented', 'from': 'gateway', 'to': 'db'}]},
    {'services': [{'id': 'gateway', 'reliability': {'live_probability': 1}}]},
])
def test_unknown_entities_or_unprovided_topology_fields_are_not_synthesized(bad):
    raw = model(); before = deepcopy(raw)
    with pytest.raises(ValueError):
        attach_operation_metadata(raw, bad)
    assert raw == before


def test_v5_keeps_the_original_discovery_and_records_a_distinct_validated_attachment(tmp_path):
    source = tmp_path/'discovery'; source.mkdir()
    for name in ('observed.json', 'observed.bering-raw.json', 'observed.snapshot.json', 'observed.supplied-aliases.json'):
        (source/name).write_text(json.dumps(model()))
    folder = tmp_path/'operation'; folder.mkdir()
    supplied = folder/'overlay.json'; supplied.write_text(json.dumps(overlay()))
    calls = []
    tool = object.__new__(Toolchain)
    tool.command = lambda *args: calls.append(args)
    tool.discover = lambda *args: pytest.fail('operation metadata must not rediscover raw input')
    before = {path.name: path.read_bytes() for path in source.iterdir()}
    attached, quality = tool.operation_model(tmp_path/'input.json', folder, supplied, model(), {'kept': True}, source)
    assert quality == {'kept': True}
    assert calls[0][:2] == ('bering', ['validate', '--input', folder/'model.json'])
    proof = json.loads((folder/'provided-metadata-attachment.json').read_text())
    assert proof['final_model_is_a_bering_emitted_snapshot'] is False
    assert proof['files']['simulator_model']['sha256'] == hashlib.sha256((folder/'model.json').read_bytes()).hexdigest()
    assert {path.name: path.read_bytes() for path in source.iterdir()} == before


def test_legacy_overlay_path_retains_its_original_discovery_call():
    calls = []
    tool = SimpleNamespace(discover=lambda *args: calls.append(args) or ('model', 'quality'))
    assert LegacyToolchain.operation_model(tool, 'input', 'folder', 'overlay', {}, {}, 'source') == ('model', 'quality')
    assert calls == [('input', 'folder', 'overlay')]
