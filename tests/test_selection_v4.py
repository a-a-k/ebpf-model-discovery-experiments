import copy
import hashlib
import json
from pathlib import Path

from ebpf_discovery.raw_v4 import export_selection
from ebpf_discovery.selection_v4 import bind_entry, descendant_identities, select_planned, supplied_entry_roles
from ebpf_discovery.store_v3 import ObservationStore


TRACE = '1' * 32
ROOT = '1' * 16
CHILD = '2' * 16
SIBLING = '3' * 16
CONTRACT = {'entry_services': ['gateway'], 'steps': [{'method': 'GET', 'path': '/owners/{id}'}]}


def span(sid=ROOT, parent='', service='gateway', request='request-1', kind=2):
    attrs = [{'key': 'http.request.method', 'value': {'stringValue': 'GET'}},
             {'key': 'url.path', 'value': {'stringValue': '/owners/6'}}]
    if request:
        attrs.append({'key': 'http.request.header.x-experiment-request-id',
                      'value': {'stringValue': request}})
    return {'resourceSpans': [{'resource': {'attributes': [
        {'key': 'service.name', 'value': {'stringValue': service}}]},
        'scopeSpans': [{'spans': [{'traceId': TRACE, 'spanId': sid, 'parentSpanId': parent,
            'kind': kind, 'startTimeUnixNano': '1', 'endTimeUnixNano': '2', 'attributes': attrs}]}]}]}


def make_store(tmp_path, ebpf, native=()):
    observations = tmp_path / 'observations'
    observations.mkdir()
    (observations / 'a.jsonl').write_text(''.join(json.dumps(p) + '\n' for p in ebpf))
    native_dir = tmp_path / 'native'
    native_dir.mkdir()
    (native_dir / 'native-node-a.jsonl').write_text(''.join(json.dumps(p) + '\n' for p in native))
    store = ObservationStore(tmp_path / 'index.sqlite')
    store.ingest(observations, native_dir)
    return store


def test_exact_request_and_ancestry_exclude_same_trace_sibling(tmp_path):
    store = make_store(tmp_path, [span(), span(CHILD, ROOT, 'customers', None),
                                  span(SIBLING, '', 'other-operation', None)])
    plans = [{'http_steps': [{'method': 'GET', 'path': '/owners/6', 'request_id': 'request-1'}],
              'success': False, 'operation': 'label-not-used'}]
    selected, evidence = select_planned(store, plans, CONTRACT, 'ebpf')
    assert selected == {'ebpf': {(TRACE, ROOT), (TRACE, CHILD)}}
    assert evidence['clock_gate'] is False
    # Collector times need not overlap generator times and outcomes have no role.
    plans[0].update(success=True, started_ns=10**18, ended_ns=10**18 + 1)
    assert select_planned(store, plans, CONTRACT, 'ebpf')[0] == selected
    store.close()


def test_same_ids_do_not_join_sources(tmp_path):
    store = make_store(tmp_path, [span()], [span(CHILD, ROOT, 'customers', None)])
    plans = [{'http_steps': [{'method': 'GET', 'path': '/owners/6', 'request_id': 'request-1'}]}]
    selected, _ = select_planned(store, plans, CONTRACT, 'combined')
    assert selected == {'ebpf': {(TRACE, ROOT)}, 'native': set()}
    store.close()


def test_conflicting_entry_never_selects_a_convenient_variant(tmp_path):
    changed = copy.deepcopy(span())
    changed['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['name'] = 'conflicting-export'
    store = make_store(tmp_path, [span(), changed])
    root, reason = bind_entry(store, 'ebpf', 'request-1', CONTRACT['steps'][0], ['gateway'])
    assert root is None and reason == 'conflicting_entry_identity'
    store.close()


def test_zero_id_is_not_repaired_by_source_prefix(tmp_path):
    document = span()
    document['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['spanId'] = '0' * 16
    store = make_store(tmp_path, [document])
    root, reason = bind_entry(store, 'ebpf', 'request-1', CONTRACT['steps'][0], ['gateway'])
    assert root is None and reason == 'invalid_trace_or_span_identity'
    store.close()


def test_conflicting_descendant_is_retained_but_cannot_extend_selection():
    root = {'trace_id': TRACE, 'span_id': ROOT, 'parent_id': ''}
    child = {'trace_id': TRACE, 'span_id': CHILD, 'parent_id': ROOT}
    grandchild = {'trace_id': TRACE, 'span_id': SIBLING, 'parent_id': CHILD}
    rows = [root, child, dict(child, name='conflicting-export'), grandchild]
    assert set(descendant_identities(rows, {ROOT})) == {(TRACE, ROOT), (TRACE, CHILD)}


def test_untyped_http_requires_explicit_source_contract(tmp_path):
    document = span(kind=None)
    attrs = document['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['attributes']
    attrs.append({'key': 'component', 'value': {'stringValue': 'nginx'}})
    store = make_store(tmp_path, [], [document])
    assert bind_entry(store, 'native', 'request-1', CONTRACT['steps'][0], ['gateway'])[0] is None
    root, _ = bind_entry(store, 'native', 'request-1', CONTRACT['steps'][0], ['gateway'], ['nginx'])
    assert root['span_id'] == ROOT
    store.close()


def test_jaeger_cross_trace_reference_cannot_select_unrelated_child(tmp_path):
    from ebpf_discovery.observations import jaeger
    document = {'data': [{'processes': {'p': {'serviceName': 'gateway'}}, 'spans': [
        {'traceID': TRACE, 'spanID': ROOT, 'processID': 'p', 'references': []},
        {'traceID': TRACE, 'spanID': CHILD, 'processID': 'p', 'references': [
            {'refType': 'CHILD_OF', 'traceID': 'a' * 32, 'spanID': ROOT}]},
    ]}]}
    rows = list(jaeger(document, same_trace_parents=True))
    assert rows[1]['parent_id'] == ''
    assert set(descendant_identities(rows, {ROOT})) == {(TRACE, ROOT)}
    # Historical default behavior remains reproducible; only v4 opts in.
    assert list(jaeger(document))[1]['parent_id'] == ROOT


def test_supplied_receiver_role_needs_unique_bound_native_root_and_keeps_raw(tmp_path):
    native = span(kind=None)
    native_span = native['resourceSpans'][0]['scopeSpans'][0]['spans'][0]
    native_span['attributes'].append({'key': 'component', 'value': {'stringValue': 'nginx'}})
    native_span['name'] = '/owners/6'
    store = make_store(tmp_path, [span()], [native])
    plans = [{'http_steps': [{'method': 'GET', 'path': '/owners/6', 'request_id': 'request-1'}]}]
    selected, evidence = select_planned(store, plans, CONTRACT, 'combined', {'native': ['nginx']})
    roles = supplied_entry_roles(store, evidence['roots'], ['gateway'], {'native': ['nginx']})
    assert set(roles) == {('native', TRACE, ROOT)}
    assert roles['native', TRACE, ROOT]['original_kind'] is None
    raw_path = tmp_path/'native'/'native-node-a.jsonl'
    before = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    result = export_selection(store, selected, tmp_path/'export', supplied_server_roles=roles)
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == before
    exports = {item['source']: item for item in result['exports']}
    assert exports['native']['supplied_server_roles'][0]['rule'].startswith('unique declared entry')
    output = json.loads(Path(exports['native']['path']).read_text())
    assert output['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['kind'] == 'SPAN_KIND_SERVER'
    original = json.loads(raw_path.read_text())
    assert original['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['kind'] is None
    assert 'supplied_server_roles' not in exports['ebpf']
    forged = [dict(evidence['roots'][-1], request_id='another-request')]
    assert supplied_entry_roles(store, forged, ['gateway'], {'native': ['nginx']}) == {}
    store.close()


def test_supplied_role_rejects_client_and_conflicting_attributes(tmp_path):
    untyped = span(kind=None)
    attrs = untyped['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['attributes']
    attrs.append({'key': 'component', 'value': {'stringValue': 'nginx'}})
    attrs.append({'key': 'http.request.method', 'value': {'stringValue': 'POST'}})
    store = make_store(tmp_path, [], [untyped])
    plans = [{'http_steps': [{'method': 'GET', 'path': '/owners/6', 'request_id': 'request-1'}]}]
    selected, evidence = select_planned(store, plans, CONTRACT, 'native', {'native': ['nginx']})
    assert not evidence['roots']
    assert supplied_entry_roles(store, evidence['roots'], ['gateway'], {'native': ['nginx']}) == {}
    store.close()
    client = span(kind=3)
    client['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['attributes'].append(
        {'key': 'component', 'value': {'stringValue': 'nginx'}})
    (tmp_path/'client').mkdir()
    store = make_store(tmp_path/'client', [], [client])
    selected, evidence = select_planned(store, plans, CONTRACT, 'native', {'native': ['nginx']})
    assert not evidence['roots']
    assert supplied_entry_roles(store, evidence['roots'], ['gateway'], {'native': ['nginx']}) == {}
    store.close()
