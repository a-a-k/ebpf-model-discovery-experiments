import json
import hashlib
from types import SimpleNamespace

from ebpf_discovery.evidence_v4 import _alias_key, _cross_guest, _graph, evaluate
from ebpf_discovery.store_v3 import ObservationStore


def _id(value, width=16):
    return hashlib.sha256(value.encode()).hexdigest()[:width] if value else value


def _put(store, digest, source, node, trace, span, parent, request=None, *, invalid=False):
    if not invalid:
        trace, span, parent = _id(trace, 32), _id(span), _id(parent)
    data = {'source': source, 'node': node, 'trace_id': trace, 'span_id': span,
            'parent_id': parent, 'service': 'generic', 'kind': 'client', 'name': 'request',
            'start_ns': 1, 'end_ns': 2, 'attributes': {}, 'resource': {},
            'links': [], 'raw_file': 'synthetic.jsonl'}
    store.db.execute('INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (digest, source, node, trace, span, parent, 'generic', None, request,
         'client', 1, 2, None, None, None, None, 0, json.dumps(data)))


def _plan(*ids):
    return [{'attempt_id': 'a', 'operation': 'request',
             'http_steps': [{'request_id': item} for item in ids]}]


def test_cross_guest_requires_source_local_unique_parent_and_independent_headers(tmp_path):
    store = ObservationStore(tmp_path/'index.sqlite')
    _put(store, 'p1', 'ebpf', 'a', 'trace', 'parent', None, 'known')
    _put(store, 'c1', 'ebpf', 'b', 'trace', 'child', 'parent', 'known')
    _put(store, 'c2', 'native', 'b', 'trace', 'foreign', 'parent', 'known')
    _put(store, 'p2', 'ebpf', 'a', 'trace2', 'parent2', None, None)
    _put(store, 'c3', 'ebpf', 'b', 'trace2', 'child2', 'parent2', None)
    _put(store, 'p3', 'ebpf', 'a', 'trace3', 'parent3', None, 'known')
    _put(store, 'c4', 'ebpf', 'b', 'trace3', 'child3', 'parent3', 'other')
    result = _cross_guest(store, _plan('known', 'other'))
    assert result['ebpf']['header_verdicts'] == {
        'corroborated_same_planned_header': 1,
        'contradictory_planned_headers': 1,
        'unknown_missing_or_unplanned_header': 1}
    assert result['native']['exact_parent_links'] == 0
    assert result['ebpf']['witnesses']['contradictory_planned_headers'][0]['child_request_id'] == 'other'


def test_conflicting_identity_does_not_become_cross_guest_link(tmp_path):
    store = ObservationStore(tmp_path/'index.sqlite')
    _put(store, 'p1', 'ebpf', 'a', 'trace', 'parent', None, 'known')
    _put(store, 'p2', 'ebpf', 'a', 'trace', 'parent', None, 'known')
    _put(store, 'c1', 'ebpf', 'b', 'trace', 'child', 'parent', 'known')
    assert _cross_guest(store, _plan('known'))['ebpf']['exact_parent_links'] == 0


def test_invalid_cross_guest_ids_are_retained_but_not_confirmed(tmp_path):
    store = ObservationStore(tmp_path/'index.sqlite')
    _put(store, 'p1', 'ebpf', 'a', '0'*32, '1'*16, None, 'known', invalid=True)
    _put(store, 'c1', 'ebpf', 'b', '0'*32, '2'*16, '1'*16, 'known', invalid=True)
    result = _cross_guest(store, _plan('known'))['ebpf']
    assert result['exact_parent_links'] == 0
    assert result['invalid_identity_candidates'] == 1


def test_database_alias_requires_complete_address_port_and_scope_and_counts_shared_callers(tmp_path):
    folder = tmp_path/'graph'
    folder.mkdir()
    def save(name, value):
        (folder/name).write_text(json.dumps(value), encoding='utf-8')
    model = {'services': [{'id': name} for name in ('caller-a','caller-b','db-5432','db-5433')],
             'edges': [{'id':'e1','from':'caller-a','to':'db-5432'},
                       {'id':'e2','from':'caller-b','to':'db-5432'},
                       {'id':'e3','from':'caller-a','to':'db-5433'}],
             'endpoints': []}
    def alias(port):
        return {'identity_kind':'logical_endpoint','system':'postgresql',
                'address':'192.0.2.1','port':port,'network_scope':'net-a'}
    save('observed.json', model)
    save('observed.signal-quality.json', {'observation_evidence':[
        {'entity_type':'service','entity_id':'db-5432','evidence':{'database_aliases':[alias(5432)]}},
        {'entity_type':'service','entity_id':'db-5433','evidence':{'database_aliases':[alias(5433)]}}]})
    save('database-mapping.json', {'matched_observed_nodes':['db-5432'],
                                    'witnesses':[{'node':'db-5432','observed_alias':alias(5432)}]})
    save('forecast.json', {'available':True,'by_state':{'11':1},'database_down_prediction':0})
    result = _graph(folder)
    assert result['services'] == 4 and result['edges'] == 3
    aliases = result['database_aliases']
    assert len(aliases) == 2
    assert aliases[0]['port'] == '5432' and aliases[0]['shared_by_at_least_two_callers']
    assert aliases[1]['port'] == '5433' and not aliases[1]['shared_by_at_least_two_callers']
    assert result['database_mapping']['all_saved_witnesses_reproduced']
    assert result['database_fault_prognostic_impact']['difference'] == 1
    assert _alias_key({**alias(5432), 'port': None}) is None
    save('database-mapping.json', {'matched_observed_nodes':['db-5432'],
        'witnesses':[{'node':'db-5432','observed_alias':alias(5432)}]})
    quality = json.loads((folder/'observed.signal-quality.json').read_text())
    partial = {**alias(5432), 'network_scope':''}
    quality['observation_evidence'][0]['evidence']['database_aliases'] = [partial]
    save('observed.signal-quality.json', quality)
    save('database-mapping.json', {'matched_observed_nodes':['db-5432'],
        'witnesses':[{'node':'db-5432','observed_alias':partial}]})
    incomplete = _graph(folder)
    assert incomplete['incomplete_database_aliases'][0]['logical_identity'] == 'unknown'
    assert incomplete['database_mapping']['all_saved_witnesses_reproduced']


def test_unsupported_async_trace_context_stays_unknown(tmp_path):
    store = ObservationStore(tmp_path/'index.sqlite')
    record = {'attempt_id':'async-1','phase':'async_normal','operation':'checkout',
              'http_steps':[{'request_id':'req-1'}], 'order_id':'order-1'}
    output = evaluate(SimpleNamespace(out=tmp_path), 'otel_demo', store,
                      [{'attempt_id':'async-1','operation':'checkout','http_steps':[{'request_id':'req-1'}]}],
                      [record])
    for row in output['async']['attempts']:
        assert row['four_stage_causal_chain'] == 'unknown'
        assert row['markers']['external_order_id'] is True
        assert row['proofs'] == []
    assert (tmp_path/'evidence-v4.json').exists()


def test_async_span_link_proof_and_optional_business_corroboration_are_separate(tmp_path, monkeypatch):
    from ebpf_discovery.evidence_v4 import _async
    def span(name, attrs):
        return {'source':'ebpf','trace_id':'1'*32,'span_id':_id(name),'attributes':attrs,
                'attribute_conflicts':[]}
    spans = [span('producer', {'demo.order.id':'order-1','messaging.message.id':'message-1'}),
             span('consumer', {'messaging.message.id':'message-1'}),
             span('write', {'db.query.text':"INSERT INTO orders SELECT 1 WHERE order_id = 'order-1'"}),
             span('processing', {})]
    class FakeStore:
        def request_traces(self, rows, linked_consumers=False):
            assert linked_consumers
            return spans
    chain = {'status':'linked', **{key: {'source':'ebpf','trace_id':'1'*32,'span_id':_id(name)}
              for key, name in [('producer','producer'), ('consumer','consumer'),
                                ('database_write','write'), ('processing_root','processing')]}}
    monkeypatch.setattr('ebpf_discovery.async_links.message_chains',
                        lambda rows: {'req-1':{'sources':{'ebpf':chain}}})
    records = [{'attempt_id':'a','phase':'async_normal','order_id':'order-1',
                'http_steps':[{'request_id':'req-1'}]}]
    result = _async(tmp_path, FakeStore(), records)
    assert result['attempts'][0]['four_stage_causal_chain'] == 'observed'
    spans[1]['attributes']['messaging.message.id'] = 'different-message'
    result = _async(tmp_path, FakeStore(), records)
    assert result['attempts'][0]['four_stage_causal_chain'] == 'unknown'
    for row in spans:
        row['attributes'] = {}
    result = _async(tmp_path, FakeStore(), records)
    proof = result['attempts'][0]
    assert proof['four_stage_causal_chain'] == 'observed'
    assert proof['proofs'][0]['external_order_agreement'] is None
    spans[0]['attributes']['demo.order.id'] = 'different-order'
    result = _async(tmp_path, FakeStore(), records)
    proof = result['attempts'][0]
    assert proof['four_stage_causal_chain'] == 'observed'
    assert proof['proofs'][0]['external_order_agreement'] is False
