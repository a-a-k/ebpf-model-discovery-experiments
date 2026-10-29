import json
from pathlib import Path
from types import SimpleNamespace

from ebpf_discovery.binding_v5 import endpoint_alias_evidence
from ebpf_discovery.classes_v5 import fit
from ebpf_discovery.selection_v5 import bind_entry, select_planned
from ebpf_discovery.selection_v4 import bind_entry as bind_entry_v4
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


def _store(tmp_path: Path, spans, *, duplicate_document=False, service='entry'):
    observations, native = tmp_path/'observations', tmp_path/'native'
    observations.mkdir(parents=True); native.mkdir()
    payload = {'resourceSpans': [{
        'resource': {'attributes': [_attribute('service.name', service),
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


def test_matching_conflicted_entry_prevents_unique_selection(tmp_path):
    conflicted = _span(name='conflicted')
    conflicted['attributes'].extend([
        _attribute('custom.entry.attribute', 'one'),
        _attribute('custom.entry.attribute', 'two'),
    ])
    store = _store(tmp_path, [_span(name='valid'), conflicted])
    try:
        rows = store.candidates_v5('ebpf', 'opaque')
        assert sum(bool(row.get('attribute_conflicts')) for row in rows) == 1
        root, reason = bind_entry(store, 'ebpf', 'opaque', _plan()[0]['http_steps'][0], ['entry'])
        assert root is None and reason == 'conflicting_matching_entry_evidence'
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


def test_supplied_logical_role_is_common_to_both_selectors_and_classes(tmp_path):
    trace, span = '1' * 32, '2' * 16
    store = _store(tmp_path/'server', [_span(trace=trace, span=span)],
                   service='/docker/entry-1')
    admission = {'aliases': {'/docker/entry-1': 'entry'},
                 'origin': 'supplied_deployment_inventory_alias'}
    declaration = SimpleNamespace(CONTRACTS={'entry': _contract()},
                                  UNTYPED_ENTRY_COMPONENTS={})
    try:
        digest = store.db.execute('SELECT digest FROM spans').fetchone()[0]
        projection = store.apply_supplied_logical_aliases(
            admission, scoped_digest_aliases={digest: 'entry'})
        assert projection['rows'] == 1
        expected = _plan()[0]['http_steps'][0]
        current, current_reason = bind_entry(
            store, 'ebpf', 'opaque', expected, ['entry'])
        legacy, legacy_reason = bind_entry_v4(
            store, 'ebpf', 'opaque', expected, ['entry'])
        assert (current['service'], current_reason) == ('entry', 'unique_observation_entry')
        assert (legacy['service'], legacy_reason) == ('entry', 'unique_declared_entry')
        assert current['_supplied_logical_alias']['raw_service'] == '/docker/entry-1'
        original = json.loads(store.db.execute(
            'SELECT data FROM spans').fetchone()[0])
        assert original['service'] == '/docker/entry-1'
        model = fit(store, _plan(), declaration, tmp_path/'classes-alias')
        family = model['sources']['ebpf']['families'][0]
        assert family['signature'] == [[{'source': 'ebpf', 'method': 'GET',
                                         'route': '/entry'}]]
        assert family['training_descriptors'][0]['steps'][0]['status'] != 'entry_unavailable'
    finally:
        store.close()

    client_store = _store(
        tmp_path/'client', [_span(trace=trace, span=span, kind=3)],
        service='/docker/entry-1')
    try:
        digest = client_store.db.execute('SELECT digest FROM spans').fetchone()[0]
        client_store.apply_supplied_logical_aliases(
            admission, scoped_digest_aliases={digest: 'entry'})
        expected = _plan()[0]['http_steps'][0]
        assert bind_entry(client_store, 'ebpf', 'opaque', expected, ['entry'])[1] == 'entry_missing'
        assert bind_entry_v4(
            client_store, 'ebpf', 'opaque', expected, ['entry'])[1] == 'entry_missing'
    finally:
        client_store.close()


def test_supplied_role_reconciles_only_matching_runtime_label_conflict(tmp_path):
    admission = {'schema': 'supplied-logical-alias-admission-v5',
                 'origin': 'supplied_deployment_inventory_alias',
                 'aliases': {'/docker/entry-1': 'entry'}, 'conflicts': [],
                 'occurrence_proofs': [], 'unique_verified_segments': 0,
                 'receiver_segments_reverified': True,
                 'same_table_all_sources_and_direct_baseline': True,
                 'physical_identity_inferred': False}
    for case, observed, expected_service, reconciled in (
            ('same', 'entry', 'entry', True),
            ('different', 'other-role', '/docker/entry-1', False)):
        folder = tmp_path/case
        store = _store(folder, [_span(trace='1' * 32, span='2' * 16)],
                       service='/docker/entry-1')
        try:
            digest, encoded = store.db.execute('SELECT digest,data FROM spans').fetchone()
            projected = json.loads(encoded)
            projected['attribute_conflicts'] = [{'key': 'service.name'}]
            resolution = {'status': 'unknown',
                          'observed_runtime_compose_service': observed,
                          'unknown_reasons': [
                              'existing_source_label_conflicts_with_runtime_identity']}
            store.db.execute('INSERT INTO runtime_identity_projection VALUES (?,?,?,?,?,?,?,?,?)',
                (digest, 'training', 'label_conflict', '/docker/entry-1', None,
                 json.dumps(projected), json.dumps(resolution), 'inventory.json', 'a' * 64))
            store.db.commit()
            result = store.apply_supplied_logical_aliases(
                admission, scoped_digest_aliases={digest: 'entry'})
            effective = store.candidates_v5('ebpf', 'opaque')[0]
            assert effective['service'] == expected_service
            assert result['rows'] == (1 if reconciled else 0)
            if reconciled:
                assert not effective.get('attribute_conflicts')
                assert effective['_supplied_logical_alias'][
                    'runtime_label_conflict_reconciled'] is True
            else:
                assert effective['attribute_conflicts'][-1]['key'] == 'service.name'
        finally:
            store.close()
