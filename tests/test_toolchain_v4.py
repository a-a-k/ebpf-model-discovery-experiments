import json
from types import SimpleNamespace

from ebpf_discovery.toolchain_v4 import Toolchain, exact_graph_outcome, fault_inputs, unique_path, resolve_contract, predicate_contract, resolve_entry_representations


def test_shared_database_requires_both_calls_and_affects_prediction():
    model = {'services': [{'id': s} for s in ('entry', 'customers', 'visits', 'db')],
             'edges': [dict(id=eid, **{'from': a, 'to': b}, kind='sync') for eid, a, b in (
                 ('a', 'entry', 'customers'), ('b', 'entry', 'visits'),
                 ('c', 'customers', 'db'), ('d', 'visits', 'db'))]}
    binding = {'entry_service': 'entry', 'mandatory_targets': ['db'], 'required_edges': ['c', 'd']}
    assert exact_graph_outcome(model, binding) == 1
    assert exact_graph_outcome(model, binding, ['db']) == 0
    # One remaining route to the shared database does not satisfy both calls.
    assert exact_graph_outcome(model, binding, ['visits']) == 0
    assert exact_graph_outcome(model, dict(binding, required_edges=['c']), ['visits']) == 1


def test_ancillary_endpoint_has_valid_but_unscored_liveness_without_changing_operation():
    model = {'endpoints': [
        {'id': 'selected', 'entry_service': 'gateway', 'success_predicate_ref': 'owner'},
        {'id': 'other', 'entry_service': 'customers', 'success_predicate_ref': 'customers-get'}]}
    binding = {'endpoints': ['selected'], 'entry_service': 'gateway',
               'mandatory_targets': ['customers', 'db'], 'required_edges': ['gateway-customers', 'customers-db']}
    contract = predicate_contract(model, binding, 'owner')
    assert contract['predicates']['owner'] == {
        'type': 'edge_aware', 'entry_service': 'gateway', 'mandatory_targets': ['customers', 'db'],
        'required_edges': ['gateway-customers', 'customers-db'], 'edge_modes': ['sync']}
    assert contract['endpoint_weights'] == {'selected': 1, 'other': 0}
    assert contract['predicates']['customers-get']['type'] == 'all_of'
    assert contract['predicates']['customers-get']['services'] == ['customers']
    assert len(model['endpoints']) == 2


def test_database_mapping_requires_port_system_and_compatible_network_scope(tmp_path):
    tool = object.__new__(Toolchain)
    tool.system = 'example'
    tool.ctx = SimpleNamespace(deployment_dir=tmp_path)
    tool.declaration = SimpleNamespace(SELECTED_DATABASE={'db_system': 'postgresql'})
    tool.inventory = {'database': {'ip': '172.20.0.9', 'port': 5432,
        'transport_host': '192.168.76.11', 'transport_port': 15432}}
    databases = [dict(identity_kind='logical_endpoint', system=system, address=address,
                      port=port, network_scope=scope) for system, address, port, scope in (
        ('postgresql', '172.20.0.9', 5432, ''),
        ('postgresql', '172.20.0.9', 6432, ''),
        ('postgresql', '192.168.76.11', 15432, 'example-routed-network'),
        ('postgresql', '172.20.0.9', 5432, 'another-deployment'),
        ('mysql', '172.20.0.9', 5432, ''),
        ('postgresql', '172.20.0.9', 5432, 'declared:example-routed-network'),
        ('postgresql', '172.20.0.9', 5432, 'declared:another-deployment'),
    )]
    model = {'services': [{'id': str(i)} for i in range(len(databases))], 'edges': []}
    quality = {'observation_evidence': [{'entity_type': 'service', 'entity_id': str(i),
                'evidence': {'database': database}} for i, database in enumerate(databases)]}
    selected, evidence = tool.database_nodes(model, quality)
    assert selected == ['0', '2', '5']
    assert evidence['physical_identity_inferred'] is False


def test_preflight_attachment_never_adds_missing_or_unconfirmed_nodes(tmp_path):
    report = {'services': [dict(id=sid, identity={'status': identity},
                               replicas={'status': 'CONFIRMED', 'value': '2'})
                           for sid, identity in [('observed', 'CONFIRMED'), ('unobserved', 'CONFIRMED'),
                                                 ('ambiguous', 'CONFLICT')]]}
    path = tmp_path / 'report.json'
    path.write_text(json.dumps(report))
    tool = object.__new__(Toolchain)
    tool.preflight_reports = {('ebpf', 'operation'): [path]}
    model = {'services': [{'id': 'observed'}, {'id': 'ambiguous'}]}
    overlay, evidence = tool.static_overlay(model, 'ebpf', 'operation')
    assert [s['id'] for s in overlay] == ['observed']
    assert len(model['services']) == 2
    assert evidence[0]['report'] == str(path)


def test_preflight_uses_declared_required_services_as_nonempty_goal_targets(tmp_path):
    deployment = tmp_path/'deployment'
    deployment.mkdir()
    (deployment/'compose.yaml').write_text('services: {}\n')
    tool = object.__new__(Toolchain)
    tool.root = tmp_path/'toolchain'
    tool.ctx = SimpleNamespace(deployment_dir=deployment)
    tool.system, tool.inventory = 'generic', {}
    tool.declaration = SimpleNamespace(CONTRACTS={'read': {
        'entry_services': ['edge', 'edge-alias'],
        'steps': [{'method': 'GET', 'path': '/read'}],
        'required_calls': [{'caller': ['edge', 'edge-alias'], 'callee': ['reader', 'reader-alias']},
                           {'caller': ['reader'], 'db_system': 'postgresql'}]}})
    goals = []
    def command(tool_name, args, folder, name):
        assert tool_name == 'procrustes'
        goals.append(json.loads((folder/'goal.json').read_text()))
    tool.command = command
    tool.preflight()
    assert len(goals) == 2
    assert all(goal['operation']['mandatory_targets'] == ['reader'] for goal in goals)
    assert all(goal['scope']['services'] == ['edge', 'reader'] for goal in goals)


def test_composite_preflight_targets_describe_the_individual_http_step(tmp_path):
    from systems.otel_demo import experiment_v4
    deployment = tmp_path/'deployment'
    deployment.mkdir()
    (deployment/'compose.yaml').write_text('services: {}\n')
    tool = object.__new__(Toolchain)
    tool.root, tool.system, tool.inventory = tmp_path/'toolchain', 'generic', {}
    tool.ctx = SimpleNamespace(deployment_dir=deployment)
    tool.declaration = experiment_v4
    goals = []
    tool.command = lambda tool_name, args, folder, name: goals.append(json.loads((folder/'goal.json').read_text()))
    tool.preflight()
    for goal in goals:
        operation = goal['operation']
        if operation['method'] == 'GET':
            assert operation['mandatory_targets'] == ['product-catalog']
        elif operation['path'] == '/api/cart':
            assert operation['mandatory_targets'] == ['cart']
        else:
            assert set(operation['mandatory_targets']) == {'checkout', 'cart', 'product-catalog', 'currency', 'shipping', 'payment'}


def test_faults_scope_replica_loss_and_database_outage_separately():
    faults = fault_inputs('visits', ['shared-db'])['profiles']
    assert faults['state-10']['faults'][0]['selector'] == {
        'service_ids': ['visits'], 'placement_labels': {'controlled_replica': 'b'}}
    assert faults['state-01']['faults'][0]['selector']['placement_labels']['controlled_replica'] == 'a'
    assert len(faults['state-00']['faults']) == 2
    assert faults['db-down']['faults'] == [{'type': 'correlated_failure_domain',
        'only_failure_eligible': False, 'selector': {'service_ids': ['shared-db']}}]


def test_rpc_hint_matches_exact_method_and_purpose_is_not_identity():
    from systems.otel_demo.experiment_v4 import CONTRACTS
    edges = [{'id': op, 'from': 'checkout', 'to': 'currency', 'kind': 'sync',
              'identity': {'operation': op}} for op in ('Convert', 'ConvertAll')]
    calls = [call for call in CONTRACTS['checkout']['required_calls']
             if call.get('purpose') in ('item price', 'shipping price')]
    assert len(calls) == 2
    for call in calls:
        assert unique_path({'edges': edges}, 'checkout', 'currency',
                           call_hint=call['operation_hint']) == ['Convert']


def test_http_hint_distinguishes_method_and_route():
    edges = [{'id': method+path, 'from': 'checkout', 'to': 'shipping', 'kind': 'sync',
              'identity': {'operation': method, 'route': path}}
             for method, path in [('POST', '/get-quote'), ('GET', '/get-quote'), ('POST', '/get-quote-extra')]]
    assert unique_path({'edges': edges}, 'checkout', 'shipping',
                       call_hint='POST /get-quote') == ['POST/get-quote']


def test_database_predicate_is_explicitly_a_channel_under_node_faults():
    model = {'services': [{'id': x} for x in ('cart', 'db')],
             'edges': [{'id': x, 'from': 'cart', 'to': 'db', 'kind': 'sync'} for x in ('HGET', 'HSET')],
             'endpoints': [{'id': 'e', 'entry_service': 'cart', 'method': 'POST', 'path': '/cart'}]}
    quality = {'observation_evidence': [{'entity_type': 'service', 'entity_id': 'db',
                'evidence': {'database': {'system': 'redis'}}}]}
    binding = resolve_contract(model, quality, {'entry_services': ['cart'],
        'required_calls': [{'caller': ['cart'], 'db_system': 'redis'}],
        'steps': [{'method': 'POST', 'path': '/cart'}]})
    assert binding['available']
    assert binding['required_edges'] == ['HGET', 'HSET']
    assert binding['resolved_calls'][0]['command_level_necessity_inferred'] is False
    for unavailable in ([], ['cart'], ['db'], ['cart', 'db']):
        assert exact_graph_outcome(model, binding, unavailable) == exact_graph_outcome(
            model, dict(binding, required_edges=['HGET']), unavailable)


def test_missing_db_export_does_not_veto_explicit_fixed_condition_replica_forecast():
    model = {'services': [{'id': name} for name in ('gateway', 'worker')],
        'edges': [{'id': 'gw', 'from': 'gateway', 'to': 'worker', 'kind': 'sync'}],
        'endpoints': [{'id': 'entry', 'entry_service': 'gateway', 'method': 'GET', 'path': '/work'}]}
    contract = {'entry_services': ['gateway'], 'steps': [{'method': 'GET', 'path': '/work'}],
        'required_calls': [{'caller': ['gateway'], 'callee': ['worker']},
                           {'caller': ['worker'], 'db_system': 'postgresql'}]}
    projected = resolve_contract(model, {}, contract)
    assert projected['available']
    assert not projected['all_required_database_channels_observed']
    assert projected['assumed_satisfied_database_requirements'][0]['recovered_dependency'] is False
    assert projected['required_edges'] == ['gw']
    full_model = {**model, 'services': [*model['services'], {'id': 'db'}],
        'edges': [*model['edges'], {'id': 'wd', 'from': 'worker', 'to': 'db', 'kind': 'sync'}]}
    quality = {'observation_evidence': [{'entity_type': 'service', 'entity_id': 'db',
        'evidence': {'database': {'system': 'postgresql'}}}]}
    observed = resolve_contract(full_model, quality, contract)
    assert observed['available'] and observed['all_required_database_channels_observed']
    for down in ([], ['worker']):
        assert exact_graph_outcome(model, projected, down) == exact_graph_outcome(full_model, observed, down)
    assert exact_graph_outcome(full_model, observed, ['db']) == 0
    # Projection is not evidence for the DB intervention; the observed model has
    # a distinct response and the binding explicitly records missing DB coverage.
    assert exact_graph_outcome(model, projected, ['db']) == 1


def test_database_projection_cannot_invent_a_required_service_path():
    model = {'services': [{'id': 'gateway'}, {'id': 'worker'}], 'edges': [],
        'endpoints': [{'id': 'entry', 'entry_service': 'gateway', 'method': 'GET', 'path': '/work'}]}
    contract = {'entry_services': ['gateway'], 'steps': [{'method': 'GET', 'path': '/work'}],
        'required_calls': [{'caller': ['gateway'], 'callee': ['worker']},
                           {'caller': ['worker'], 'db_system': 'postgresql'}]}
    binding = resolve_contract(model, {}, contract)
    assert not binding['available']
    assert binding['assumed_satisfied_database_requirements'] == []
    assert len(binding['unknown']) == 2


def test_global_inputs_keep_unlinked_calls_without_request_roots_and_reuse_wire(tmp_path):
    import sqlite3
    from pathlib import Path
    store = SimpleNamespace(db=sqlite3.connect(':memory:'))
    store.db.execute('CREATE TABLE files(path TEXT, consumed INTEGER)')
    for filename in ('a.jsonl', 'native-node-a.jsonl'):
        payload = {'resourceSpans': [{'resource': {'attributes': [
            {'key': 'service.name', 'value': {'stringValue': 'unlinked-worker'}}]},
            'scopeSpans': [{'spans': [{'traceId': '1'*32, 'spanId': '2'*16,
                'kind': 'SPAN_KIND_CLIENT', 'name': 'GET /downstream', 'attributes': []}]}]}]}
        path = tmp_path/filename
        path.write_text(json.dumps(payload)+'\n', encoding='utf-8')
        store.db.execute('INSERT INTO files VALUES (?, ?)', (str(path), path.stat().st_size))
    tool = object.__new__(Toolchain)
    tool.root, tool.store, tool.system = tmp_path/'toolchain', store, 'generic'
    tool.root.mkdir()
    tool.declaration = SimpleNamespace(CONTRACTS={name: {'entry_services': ['entry'],
        'steps': [{'method': 'GET', 'path': '/'+name}]} for name in ('first', 'second')})
    tool.prepare_inputs([])
    for variant in ('raw', 'network_scope'):
        ebpf = tool.input_manifests['ebpf', variant][1]
        native = tool.input_manifests['native', variant][1]
        combined = tool.input_manifests['combined', variant][1]
        assert ebpf['observations'] == native['observations'] == 1
        assert combined['observations'] == 2
        assert [item['path'] for item in combined['exports']] == [
            ebpf['exports'][0]['path'], native['exports'][0]['path']]
        assert all(Path(item['path']).is_file() for item in combined['exports'])
        assert {item['source'] for item in ebpf['exports']} == {'ebpf'}
        assert {item['source'] for item in native['exports']} == {'native'}
    assert all(not evidence['roots'] for evidence in tool.entry_evidence.values())
    # Missing entry binding cannot silently reduce the structural graph input.
    assert len(list(tool.root.rglob('*.json'))) > 0


def test_contract_rpc_wire_spelling_and_proven_endpoint_alias_preserve_graph():
    model = {'services': [{'id': name} for name in ('frontend', 'cart')],
        'edges': [{'id': 'call', 'from': 'frontend', 'to': 'cart', 'kind': 'sync',
                   'identity': {'protocol': 'http', 'operation': 'POST', 'route': '/oteldemo.CartService/AddItem'}}],
        'endpoints': [{'id': 'concrete', 'entry_service': 'frontend', 'method': 'POST', 'path': '/cart/6'},
                      {'id': 'template', 'entry_service': 'frontend', 'method': 'POST', 'path': '/cart/{id}'}]}
    original = json.dumps(model, sort_keys=True)
    contract = {'entry_services': ['frontend'], 'steps': [{'method': 'POST', 'path': '/cart/6'}],
        'required_calls': [{'caller': ['frontend'], 'callee': ['cart', 'oteldemo.CartService'],
                           'operation_hint': 'CartService/AddItem'}]}
    assert not resolve_contract(model, {}, contract)['available']
    proof = {'endpoint_ids': ['concrete', 'template'], 'evidence': [{'basis': 'fixture exact bound root'}]}
    binding = resolve_contract(model, {}, contract, entry_proofs={0: proof})
    assert binding['available'] and binding['endpoints'] == ['concrete', 'template']
    assert binding['resolved_calls'][0]['call_hint_evidence'][0]['basis'] == 'rpc_over_http_post_route_exact'
    assert json.dumps(model, sort_keys=True) == original
    model['edges'][0]['identity']['route'] = '/another.CartService/AddItem'
    assert not resolve_contract(model, {}, contract, entry_proofs={0: proof})['available']


def test_direct_and_transparent_proxy_representations_have_same_declared_fault_law():
    model = {'services': [{'id': name} for name in ('entry', 'proxy', 'worker')],
        'edges': [{'id': name, 'from': a, 'to': b, 'kind': 'sync'} for name, a, b in (
            ('direct', 'entry', 'worker'), ('first', 'entry', 'proxy'), ('second', 'proxy', 'worker'))]}
    evidence = {}
    direct = unique_path(model, 'entry', 'worker', intermediates={'proxy'}, provenance=evidence)
    assert direct == ['direct'] and 'direct observed' in evidence['policy']
    proxy_model = {**model, 'edges': model['edges'][1:]}
    indirect = unique_path(proxy_model, 'entry', 'worker', intermediates={'proxy'})
    assert indirect == ['first', 'second']
    assert unique_path(proxy_model, 'entry', 'worker', intermediates=set()) is None
    base = {'entry_service': 'entry', 'mandatory_targets': ['worker']}
    for unavailable in ([], ['worker']):
        assert exact_graph_outcome(model, {**base, 'required_edges': direct}, unavailable) == \
               exact_graph_outcome(proxy_model, {**base, 'required_edges': indirect}, unavailable)


def test_mapped_database_alias_group_is_not_a_graph_merge_or_complete_db_coverage():
    model = {'services': [{'id': name} for name in ('entry', 'worker', 'db-local', 'db-forward')],
        'edges': [{'id': name, 'from': a, 'to': b, 'kind': 'sync'} for name, a, b in (
            ('call', 'entry', 'worker'), ('local', 'worker', 'db-local'), ('forward', 'worker', 'db-forward'))],
        'endpoints': [{'id': 'endpoint', 'entry_service': 'entry', 'method': 'GET', 'path': '/work'}]}
    quality = {'observation_evidence': [{'entity_type': 'service', 'entity_id': name,
        'evidence': {'database': {'system': 'mysql'}}} for name in ('db-local', 'db-forward')]}
    contract = {'entry_services': ['entry'], 'steps': [{'method': 'GET', 'path': '/work'}],
        'required_calls': [{'caller': ['entry'], 'callee': ['worker']},
                           {'caller': ['worker'], 'db_system': 'mysql'},
                           {'caller': ['worker'], 'db_system': 'redis'}]}
    group = {'declared_system': 'mysql', 'matched_observed_nodes': ['db-local', 'db-forward'],
             'fault_scope': 'same declared stopped container', 'mapping_basis': 'exact supplied endpoint aliases'}
    before = json.dumps(model, sort_keys=True)
    binding = resolve_contract(model, quality, contract, database_fault_group=group)
    assert binding['available'] and binding['database_fault_prediction_available']
    assert not binding['all_required_database_channels_observed']  # Redis remains unobserved
    assert binding['required_edges'] == ['call', 'forward', 'local']
    assert binding['database_fault_fixed_other_requirements'][0]['obligation']['db_system'] == 'redis'
    assert exact_graph_outcome(model, binding) == 1
    assert exact_graph_outcome(model, binding, group['matched_observed_nodes']) == 0
    assert json.dumps(model, sort_keys=True) == before
    incomplete = resolve_contract(model, quality, contract,
        database_fault_group={**group, 'matched_observed_nodes': ['db-local']})
    assert incomplete['available'] and not incomplete['database_fault_prediction_available']
    assert not incomplete['all_required_database_channels_observed']


def test_proven_entry_alias_selects_only_an_observed_supported_representation():
    model = {'services': [{'id': name} for name in ('entry-ebpf', 'entry-native', 'worker')],
        'edges': [{'id': 'call', 'from': 'entry-native', 'to': 'worker', 'kind': 'sync'}],
        'endpoints': [{'id': name, 'entry_service': name, 'method': 'GET', 'path': '/work'}
                      for name in ('entry-ebpf', 'entry-native')]}
    contract = {'entry_services': ['entry-ebpf', 'entry-native'],
        'steps': [{'method': 'GET', 'path': '/work'}], 'required_calls': [
            {'caller': ['entry-ebpf', 'entry-native'], 'callee': ['worker']}]}
    before = json.dumps(model, sort_keys=True)
    assert not resolve_entry_representations(model, {}, contract, [], proof_builder=lambda _: {})['available']
    binding = resolve_entry_representations(model, {}, contract, [], proof_builder=lambda _: {},
        identity_groups=[{'aliases': ['entry-ebpf', 'entry-native'], 'proof': ['fixture retained configuration']}],
        controlled='worker')
    assert binding['available'] and binding['entry_service'] == 'entry-native'
    assert binding['required_edges'] == ['call']
    candidates = binding['entry_identity_resolution']['candidates']
    assert not candidates[0]['binding']['available']
    assert candidates[1]['exact_state_vector'] == {'11': 1, '10': 1, '01': 1, '00': 0}
    assert json.dumps(model, sort_keys=True) == before


def test_entry_representations_with_different_observed_fault_paths_remain_unknown():
    model = {'services': [{'id': name} for name in ('entry-a', 'entry-b', 'controlled', 'caller', 'target')],
        'edges': [{'id': name, 'from': a, 'to': b, 'kind': 'sync'} for name, a, b in (
            ('a', 'entry-a', 'controlled'), ('b', 'controlled', 'caller'),
            ('c', 'entry-b', 'caller'), ('d', 'caller', 'target'))],
        'endpoints': [{'id': name, 'entry_service': name, 'method': 'GET', 'path': '/work'}
                      for name in ('entry-a', 'entry-b')]}
    contract = {'entry_services': ['entry-a', 'entry-b'], 'steps': [{'method': 'GET', 'path': '/work'}],
                'required_calls': [{'caller': ['caller'], 'callee': ['target']}]}
    binding = resolve_entry_representations(model, {}, contract, [], proof_builder=lambda _: {},
        identity_groups=[{'aliases': ['entry-a', 'entry-b'], 'proof': ['fixture retained configuration']}],
        controlled='controlled')
    assert not binding['available']
    assert not binding['entry_identity_resolution']['all_supported_state_vectors_agree']
    assert binding['entry_identity_resolution']['selected_observed_entry'] is None
