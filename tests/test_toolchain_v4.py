import json
from types import SimpleNamespace

from ebpf_discovery.toolchain_v4 import Toolchain, exact_graph_outcome, fault_inputs, unique_path, resolve_contract


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
    )]
    model = {'services': [{'id': str(i)} for i in range(len(databases))], 'edges': []}
    quality = {'observation_evidence': [{'entity_type': 'service', 'entity_id': str(i),
                'evidence': {'database': database}} for i, database in enumerate(databases)]}
    selected, evidence = tool.database_nodes(model, quality)
    assert selected == ['0', '2']
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
