import json
from pathlib import Path
from types import SimpleNamespace

from ebpf_discovery.binding_v5 import endpoint_alias_evidence
from ebpf_discovery.classes_v5 import fit
from ebpf_discovery.selection_v5 import bind_entry, select_planned
from ebpf_discovery.store_v5 import ObservationStoreV5


def _attribute(key, value):
    raw = ({'arrayValue': {'values': [{'stringValue': item} for item in value]}}
           if isinstance(value, list) else {'stringValue': value})
    return {'key': key, 'value': raw}


def _span(*, trace='', span='', parent='', instance='one', request='opaque',
          method='GET', path='/entry', kind=2, name='entry'):
    return {
        'traceId': trace, 'spanId': span, 'parentSpanId': parent, 'name': name, 'kind': kind,
        'startTimeUnixNano': '1', 'endTimeUnixNano': '2',
        'attributes': [
            _attribute('http.request.header.x-experiment-request-id', [request]),
            _attribute('http.request.method', method), _attribute('url.path', path),
        ] if request is not None else []}


def _store(tmp_path: Path, spans, *, duplicate_document=False):
    observations, native = tmp_path/'observations', tmp_path/'native'
    observations.mkdir(); native.mkdir()
    payload = {'resourceSpans': [{
        'resource': {'attributes': [_attribute('service.name', 'entry'),
                                    _attribute('service.instance.id', 'one')]},
        'scopeSpans': [{'spans': spans}]}]}
    rows = [json.dumps({'payload': payload})]
    if duplicate_document:
        rows.append(rows[0])
    (observations/'a.jsonl').write_text('\n'.join(rows)+'\n', encoding='utf-8')
    store = ObservationStoreV5(tmp_path/'index.sqlite')
    store.ingest(observations, native)
    return store


def _plan():
    return [{'phase': 'class_train', 'attempt_id': 'a',
             'http_steps': [{'request_id': 'opaque', 'method': 'GET', 'path': '/entry'}]}]


def _contract():
    return {'entry_services': ['entry'],
            'steps': [{'method': 'GET', 'path': '/entry'}], 'required_calls': []}


def test_blank_ids_bind_by_observation_and_rebind_endpoint_with_every_locator(tmp_path):
    store = _store(tmp_path, [_span()], duplicate_document=True)
    try:
        root, reason = bind_entry(store, 'ebpf', 'opaque', _plan()[0]['http_steps'][0], ['entry'])
        assert reason == 'unique_observation_entry'
        assert root['trace_id'] == root['span_id'] == ''
        assert len(root['_observation_provenance']) == 2
        assert [item['normalized_ordinal'] for item in root['_observation_provenance']] == [0, 1]
        selected, evidence = select_planned(store, _plan(), _contract(), 'ebpf')
        assert selected == {'ebpf': set()}
        retained = evidence['roots'][0]
        assert retained['genuine_ancestry_identity'] is False
        proof = endpoint_alias_evidence(store, evidence['roots'], _contract()['steps'][0],
            'entry', [{'id': 'endpoint', 'entry_service': 'entry',
                       'method': 'GET', 'path': '/entry'}])
        assert proof['endpoint_ids'] == ['endpoint']
        assert len(proof['evidence'][0]['observation_provenance']) == 2
        assert proof['evidence'][0]['ids_rewritten'] is False
    finally:
        store.close()


def test_distinct_matches_are_ambiguous_even_with_same_header_method_and_route(tmp_path):
    first, second = _span(name='one'), _span(name='two')
    store = _store(tmp_path, [first, second])
    try:
        root, reason = bind_entry(store, 'ebpf', 'opaque', _plan()[0]['http_steps'][0], ['entry'])
        assert root is None and reason == 'multiple_distinct_entries'
    finally:
        store.close()


def test_same_semantics_from_distinct_guests_do_not_deduplicate(tmp_path):
    observations, native = tmp_path/'observations', tmp_path/'native'
    observations.mkdir(); native.mkdir()
    payload = {'resourceSpans': [{
        'resource': {'attributes': [_attribute('service.name', 'entry'),
                                    _attribute('service.instance.id', 'instance-one')]},
        'scopeSpans': [{'spans': [_span()]}]}]}
    for node in ('a', 'b'):
        (observations/f'{node}.jsonl').write_text(
            json.dumps({'payload': payload})+'\n', encoding='utf-8')
    store = ObservationStoreV5(tmp_path/'index.sqlite')
    store.ingest(observations, native)
    try:
        root, reason = bind_entry(store, 'ebpf', 'opaque', _plan()[0]['http_steps'][0], ['entry'])
        assert root is None and reason == 'multiple_distinct_entries'
        rows = store.candidates_v5('ebpf', 'opaque')
        assert {row['node'] for row in rows} == {'a', 'b'}
        assert len({row['_observation_digest'] for row in rows}) == 2
    finally:
        store.close()


def test_invalid_nonempty_and_empty_ids_never_enable_descendants(tmp_path):
    for case, root, child in (
        ('invalid', _span(trace='nothex', span='bad', name='root'),
         _span(trace='nothex', span='child', parent='bad', request=None, name='child')),
        ('empty', _span(name='root'), _span(parent='', request=None, name='child')),
    ):
        folder = tmp_path/case
        folder.mkdir()
        store = _store(folder, [root, child])
        try:
            selected, evidence = select_planned(store, _plan(), _contract(), 'ebpf',
                                                include_descendants=True)
            assert selected['ebpf'] == set()
            assert evidence['roots'][0]['genuine_ancestry_identity'] is False
            assert evidence['selected_observation_digests']['ebpf'] == [
                evidence['roots'][0]['observation_digest']]
        finally:
            store.close()


def test_v5_family_uses_common_entry_baseline_while_legacy_output_is_paired(tmp_path):
    store = _store(tmp_path, [_span()])
    declaration = SimpleNamespace(CONTRACTS={'entry': _contract()},
                                  UNTYPED_ENTRY_COMPONENTS={})
    try:
        model = fit(store, _plan(), declaration, tmp_path/'classes')
        assert (tmp_path/'classes'/'classes-model.json').is_file()
        assert model['legacy_model'] == 'classes-model.json'
        assert len(model['sources']['ebpf']['families']) == 1
        family = model['sources']['ebpf']['families'][0]
        assert family['signature'] == [[{'source': 'ebpf', 'method': 'GET', 'route': '/entry'}]]
        assert family['training_descriptors'][0]['steps'][0]['status'] == (
            'entry_bound_without_genuine_ancestry')
    finally:
        store.close()
