"""Small contract checks; product compilation/simulation runs only in Actions."""
from copy import deepcopy

from ebpf_discovery.compose_ack_contract import bind, contracts, direct_baselines, semantics
from ebpf_discovery.toolchain_v4 import exact_graph_outcome


def observed_prefix(include_home=True):
    names = ['nginx-thrift', 'compose-post-service', 'text-service', 'user-service',
             'media-service', 'unique-id-service', 'post-storage-service',
             'user-timeline-service', 'mongo', 'user-redis', 'home-timeline-service',
             'social-graph-service', 'home-redis']
    calls = contracts()['primary']['compose_post']['required_calls']
    edges = []
    for i, call in enumerate(calls):
        target = (call.get('callee') or [
            'mongo' if call.get('db_system') == 'mongodb' else
            'user-redis' if call['caller'] == ['user-timeline-service'] else 'home-redis'])[0]
        if target == 'home-timeline-service' and not include_home:
            continue
        edges.append({'id': 'edge-' + str(i), 'from': call['caller'][0], 'to': target, 'kind': 'sync'})
    model = {'services': [{'id': n} for n in names], 'edges': edges,
             'endpoints': [{'id': 'compose', 'entry_service': 'nginx-thrift',
                            'method': 'POST', 'path': '/wrk2-api/post/compose'}]}
    # No typed DB aliases means the primary model explicitly assumes those
    # fixed DB conditions; the separately observed Mongo fault map is retained.
    mapping = {'declared_system': 'mongodb', 'matched_observed_nodes': ['mongo']}
    return model, mapping


def test_ack_prefix_does_not_require_success_of_db_or_unexecuted_suffix():
    spec = contracts()
    primary = spec['primary']['compose_post']['required_calls']
    prefix = spec['database_down']['compose_post']['required_calls']
    assert any(c.get('db_system') == 'mongodb' for c in primary)
    assert not any('db_system' in c for c in prefix)
    assert any(c.get('callee') == ['user-timeline-service'] for c in prefix)
    assert not any(c.get('callee') == ['home-timeline-service'] for c in prefix)
    assert semantics('compose_post')['selected_database_is_off_path'] is False


def test_primary_and_database_down_are_separate_predicates_on_same_observations():
    model, mapping = observed_prefix()
    before = deepcopy(model)
    primary, controlled = bind(model, {}, contracts()['primary']['compose_post'], {}, mapping, {}, [])
    prefix, _ = bind(model, {}, contracts()['database_down']['compose_post'], {}, mapping, {}, [])
    assert primary['available'] and prefix['available']
    assert exact_graph_outcome(model, primary, [controlled]) == 0
    assert exact_graph_outcome(model, prefix, ['mongo']) == 1
    assert model == before


def test_missing_suffix_can_block_primary_while_db_error_prefix_remains_known():
    model, mapping = observed_prefix(include_home=False)
    primary, _ = bind(model, {}, contracts()['primary']['compose_post'], {}, mapping, {}, [])
    prefix, _ = bind(model, {}, contracts()['database_down']['compose_post'], {}, mapping, {}, [])
    assert primary['available'] is False
    assert prefix['available'] is True
    model['edges'] = [e for e in model['edges'] if e['to'] != 'user-timeline-service']
    missing, _ = bind(model, {}, contracts()['database_down']['compose_post'], {}, mapping, {}, [])
    assert missing['available'] is False


def test_direct_baseline_has_identical_semantics_without_graph_admission():
    baseline = direct_baselines()
    assert baseline['compose_post']['prediction'] == 0.875
    assert baseline['compose_post']['database']['database_down_prediction'] == 1
    assert baseline['compose_post']['database']['selected_database_is_off_path'] is False
    assert baseline['read_user_timeline']['database']['available'] is True
    assert baseline['read_user_timeline']['database']['database_down_prediction'] == 1
    assert baseline['read_user_timeline']['database']['selected_database_is_off_path'] is False
    assert contracts()['primary']['read_user_timeline']['conditional_db']
    assert contracts()['database_down']['read_user_timeline']['conditional_db'] == []


def test_selected_mongo_mapping_is_required_even_though_success_is_not():
    model, _ = observed_prefix()
    binding, _ = bind(model, {}, contracts()['database_down']['compose_post'], {},
                      {'declared_system': 'mongodb', 'matched_observed_nodes': []}, {}, [])
    assert binding['available'] is True
    assert binding['database_fault_prediction_available'] is False
