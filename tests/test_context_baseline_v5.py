from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from ebpf_discovery.toolchain_v5 import Toolchain, context_edge_union


def edge(identity, origin='gateway', target='catalog', kind='server', support=1):
    return {'id': identity, 'from': origin, 'to': target, 'kind': 'sync', 'blocking': True,
            'identity': {'protocol': 'grpc', 'span_kind': kind},
            'observed': {'support': support, 'latency': support * 2}}


def graph():
    return {'services': [{'id': 'gateway', 'replicas': 1}, {'id': 'catalog', 'replicas': 1}],
            'edges': [edge('existing')],
            'endpoints': [{'id': 'actual-server-entry', 'entry_service': 'gateway'}],
            'metadata': {'source_ref': 'actual-first-publication'}}


def test_union_preserves_strict_view_and_ignores_client_candidates_and_new_nodes():
    original = graph()
    joint = graph()
    joint['services'].append({'id': 'not-in-original', 'replicas': 1})
    joint['endpoints'].append({'id': 'client-fallback-entry', 'entry_service': 'catalog'})
    joint['edges'] = [edge('existing', support=99), edge('new-server'),
                      edge('new-client', kind='client'), edge('new-node', target='not-in-original')]
    before, joint_before = deepcopy(original), deepcopy(joint)
    result, proof = context_edge_union(original, joint)
    assert result == {**before, 'edges': [*before['edges'], joint['edges'][1]]}
    assert proof['added_edge_ids'] == ['new-server']
    assert {item['reason'] for item in proof['skipped_joint_edges']} == {
        'not_an_actual_server_child_edge', 'endpoint_service_not_in_original_view'}
    assert proof['semantic_identity_conflicts'] == []
    assert not proof['union_is_a_bering_emitted_snapshot']
    assert original == before and joint == joint_before


@pytest.mark.parametrize('field,value', [('from', 'catalog'), ('to', 'gateway'),
                                      ('kind', 'async'), ('blocking', False),
                                      ('identity', {'protocol': 'http', 'span_kind': 'server'})])
def test_semantic_conflicts_remain_explicit_and_never_replace_the_original_edge(field, value):
    original, joint = graph(), graph()
    joint['edges'][0][field] = value
    result, proof = context_edge_union(original, joint)
    assert result == original
    assert proof['semantic_identity_conflicts'] == ['existing']


@pytest.mark.parametrize('counts', [(0, 3), (3, 0), (0, 0)])
def test_single_source_reuses_exact_original_predictions_and_never_executes_extra_tools(tmp_path, monkeypatch, counts):
    def forbidden(*args, **kwargs):
        raise AssertionError('single-source equivalence must not run another Bering or Sheaft')
    monkeypatch.setattr('ebpf_discovery.bering_v4.replay', forbidden)
    root = tmp_path/'toolchain'
    root.mkdir()
    original = {'combined': {variant: {'operation': {'available': False, 'prediction': None,
                                                   'reason': 'original-unknown'}}
                             for variant in ('raw', 'network_scope')}}
    original['combined']['network_scope']['operation'] = {'available': True, 'prediction': .875}
    (root/'forecasts.json').write_text(json.dumps(original))
    path = root/'mixed-input.json'
    path.write_text(json.dumps({'observations': sum(counts)}))
    inputs = {(source, variant): (path, {'observations': count})
              for variant in ('raw', 'network_scope')
              for source, count in zip(('ebpf', 'native', 'combined'), (*counts, sum(counts)), strict=True)}
    tool = SimpleNamespace(root=root, input_manifests=inputs, forecast_operation=forbidden)
    before = deepcopy(original)
    Toolchain.forecast_context_baseline(tool, original)
    assert json.loads((root/'context-baseline/forecasts.json').read_text()) == original['combined']
    provenance = json.loads((root/'context-baseline/manifest.json').read_text())
    assert all(row['status'] == 'reuse_single_source_equivalence' for row in provenance['variants'].values())
    assert all(row['extra_bering_or_sheaft_executed'] is False for row in provenance['variants'].values())
    assert original == before
