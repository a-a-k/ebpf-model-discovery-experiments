from copy import deepcopy
import hashlib
import json

import pytest
import yaml

from ebpf_discovery.store_v5 import ObservationStoreV5
from ebpf_discovery.supplied_alias_v5 import (
    admission_core, admission_sha256, admit_observed, load, semantic_view, write_training)


def supplied(root, *, duplicate_instance=False):
    samples = []
    for node in ('a', 'b'):
        service, name = 'visits-' + node, 'pc-' + node + '-visits-1'
        document = {'name': 'pc-' + node, 'services': {service: {'environment': {
            'OTEL_SERVICE_NAME': 'visits-service',
            'OTEL_RESOURCE_ATTRIBUTES': 'service.instance.id=' + ('same' if duplicate_instance else service)}}}}
        path = root / 'deployment' / 'petclinic' / ('node-' + node) / 'compose.yml'
        path.parent.mkdir(parents=True)
        path.write_text(yaml.safe_dump(document), encoding='utf-8')
        samples.append({'node': node, 'containers': [{'name': name, 'compose': {
            'project': 'pc-' + node, 'service': service}}]})
    inventory = {'samples': samples}
    path = root / 'runtime-identity-v5' / 'inventory-training.json'
    path.parent.mkdir()
    path.write_text(json.dumps(inventory), encoding='utf-8')
    table_path = path.with_name('supplied-service-aliases-training.json')
    write_training(inventory, path, table_path)
    return load(table_path, root), table_path


def observations(root, *, wrong_owner=False, forged_carrier=False):
    folder = root / 'observations'; folder.mkdir()
    native = root / 'native'; native.mkdir()
    for node in ('a', 'b'):
        body = folder / (node + '.raw') / 'capture' / 'body.pb'
        body.parent.mkdir(parents=True)
        body.write_bytes(b'unchanged synthetic wire')
        metadata = {'source': 'ebpf-deepflow:' + node, 'node': node, 'received_ns': 1,
                    'raw_ref': body.relative_to(folder).as_posix(),
                    'raw_sha256': hashlib.sha256(body.read_bytes()).hexdigest(),
                    'raw_size_bytes': body.stat().st_size}
        body.with_name('metadata.json').write_text(json.dumps(metadata), encoding='utf-8')
        wrapper = {**metadata, 'raw_metadata_ref': body.with_name('metadata.json').relative_to(folder).as_posix(),
                   'id_encoding': 'hex', 'payload': {'resourceSpans': [{
            'resource': {'attributes': [{'key': 'service.name', 'value': {'stringValue': 'visits-' + node}},
                                        {'key': 'container.id', 'value': {'stringValue': node * 64}}]},
            'scopeSpans': [{'spans': [{'traceId': node * 32, 'spanId': node * 16,
                'name': 'GET', 'kind': 'SPAN_KIND_SERVER', 'startTimeUnixNano': '1',
                'endTimeUnixNano': '2', 'attributes': []}]}]}]}}
        (folder / (node + '.jsonl')).write_text(json.dumps(wrapper) + '\n', encoding='utf-8')
    store = ObservationStoreV5(root / 'observation-index.sqlite', same_trace_parents=True)
    store.ingest(folder, native)
    for digest, data in store.db.execute('SELECT digest,data FROM spans').fetchall():
        node = json.loads(data)['node']
        identity = {'compose_project': 'other' if wrong_owner else 'pc-' + node,
                    'compose_service': 'visits-' + node, 'container_name': 'pc-' + node + '-visits-1'}
        resolution = {'status': 'resolved', 'service_identity': identity}
        store.db.execute('INSERT INTO runtime_identity_projection VALUES (?,?,?,?,?,?,?,?,?)',
                         (digest, 'training', 'resolved_existing', 'visits-' + node,
                          None, None, json.dumps(resolution), 'inventory', 'hash'))
        if forged_carrier:
            store.db.execute('UPDATE spans SET data=? WHERE digest=?',
                             (json.dumps({**json.loads(data), 'node': 'b' if node == 'a' else 'a'}), digest))
    store.db.commit()
    return store


def test_provided_distinct_slots_share_role_without_adding_model_instances(tmp_path):
    table, _ = supplied(tmp_path)
    assert {row['instance_id'] for row in table['provided_logical_groups']['visits-service']} == {
        'visits-a', 'visits-b'}
    store = observations(tmp_path)
    original_rows = store.db.execute('SELECT digest,data FROM spans ORDER BY digest').fetchall()
    admission = admit_observed(store, table, expected_source_prefix='ebpf-deepflow')
    assert admission['aliases'] == {'visits-a': 'visits-service', 'visits-b': 'visits-service'}
    assert set(admission['scoped_digest_compose_services'].values()) == {'visits-a', 'visits-b'}
    assert store.apply_supplied_logical_aliases(admission)['rows'] == 2
    assert store.verify_supplied_logical_aliases(admission)['rows'] == 2
    assert store.db.execute('SELECT digest,data FROM spans ORDER BY digest').fetchall() == original_rows
    model = {'services': [{'id': name, 'name': name, 'replicas': 1}
                          for name in ('visits-a', 'visits-b', 'visits-service')],
             'edges': [{'id': 'existing-a', 'from': 'visits-a', 'to': 'database'},
                       {'id': 'existing-b', 'from': 'visits-b', 'to': 'database'}], 'endpoints': []}
    original = deepcopy(model)
    effective, _, proof = semantic_view(model, {}, table, admission['aliases'])
    assert model == original
    assert effective['services'] == [{'id': 'visits-service', 'name': 'visits-service', 'replicas': 1}]
    assert [edge['id'] for edge in effective['edges']] == ['existing-a', 'existing-b']
    assert all(edge['from'] == 'visits-service' for edge in effective['edges'])
    assert proof['metadata_collisions'] == []
    store.close()


@pytest.mark.parametrize('case', ['wrong_owner', 'forged_carrier', 'duplicate_instance'])
def test_unproved_ownership_or_duplicate_supplied_slot_stays_unknown(tmp_path, case):
    table, _ = supplied(tmp_path, duplicate_instance=case == 'duplicate_instance')
    store = observations(tmp_path, wrong_owner=case == 'wrong_owner', forged_carrier=case == 'forged_carrier')
    admission = admit_observed(store, table, expected_source_prefix='ebpf-deepflow')
    assert admission['aliases'] == {}
    assert admission['conflicts']
    store.close()


def test_frozen_provided_names_require_the_original_deployment_bytes(tmp_path):
    table, table_path = supplied(tmp_path)
    declaration = table['rows'][0]['declaration']
    path = tmp_path / declaration['path']
    path.write_text(path.read_text().replace('visits-service', 'another-service'), encoding='utf-8')
    with pytest.raises(ValueError, match='deployment dependency changed'):
        load(table_path, tmp_path)


def test_runtime_label_conflict_uses_compose_owner_not_sdk_target(tmp_path):
    table, _ = supplied(tmp_path)
    store = observations(tmp_path)
    for digest, encoded in store.db.execute('SELECT digest,data FROM spans').fetchall():
        row = json.loads(encoded)
        identity = {'compose_project': 'pc-' + row['node'], 'compose_service': row['service'],
                    'container_name': 'pc-' + row['node'] + '-visits-1'}
        store.db.execute('UPDATE runtime_identity_projection SET status=?,resolution=? WHERE digest=?',
                         ('label_conflict', json.dumps({'service_identity': None,
                            'observed_runtime_service_identity': identity,
                            'observed_runtime_compose_service': row['service']}), digest))
    admission = admit_observed(store, table, expected_source_prefix='ebpf-deepflow')
    assert len(admission['aliases']) == 2
    assert store.apply_supplied_logical_aliases(admission)['rows'] == 2
    assert store.verify_supplied_logical_aliases(admission)['rows'] == 2
    store.close()


def test_original_admission_hash_is_unchanged_without_the_new_field():
    old = {'schema': 'old', 'aliases': {'container': 'role'}}
    # Obtained with admission_core from original a434 source, before this repair.
    expected = 'ce3f475d2db0bdd4c51181c683f75c9ca43dfec6d0bfb0bfc3328f0a846cfa81'
    assert 'scoped_digest_compose_services' not in admission_core(old)
    assert admission_sha256(old) == expected
    assert admission_sha256({**old, 'scoped_digest_compose_services': {}}) != expected
