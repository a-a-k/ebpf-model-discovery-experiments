import base64
import unittest
from ebpf_discovery.model import Projection, assign, conditional, wilson
from ebpf_discovery.observations import census, identifier, graph
from ebpf_discovery.evaluate import database_activity, database_reference_match, typed_order_chains


def span(identity, status=200, start=0, end=1000000, path='/product'):
    return {'source': 'ebpf', 'node': 'a', 'trace_id': identity, 'span_id': identity,
            'parent_id': '', 'kind': 'SPAN_KIND_SERVER', 'service': 'frontend', 'name': 'GET',
            'start_ns': start, 'end_ns': end, 'status': {},
            'attributes': {'http.request.header.x-experiment-request-id': identity,
                           'http.request.method': 'GET', 'url.path': path, 'http.response.status_code': status}}


class BoundaryTests(unittest.TestCase):
    def test_unknown_database_endpoints_do_not_invent_shared_identity(self):
        records = [{**span(name), 'instance': name, 'service': name, 'kind': 'SPAN_KIND_CLIENT',
                    'attributes': {'db.system': 'mysql', 'db.name': 'common_namespace'}} for name in ('caller_a', 'caller_b')]
        observed = graph(records)
        self.assertEqual(len([n for n in observed['nodes'] if n['kind'] == 'database']), 2)
        self.assertEqual(observed['shared_database_dependencies'], {})
        for record in records:
            record['attributes'].update({'server.address': 'database', 'server.port': 3306})
        self.assertEqual(len(graph(records)['shared_database_dependencies']), 1)

    def test_mongo_named_native_activity_survives_missing_endpoint_tags(self):
        record = {**span('native'), 'source': 'native', 'name': 'user_timeline_mongo_find_client',
                  'attributes': {}, 'kind': None}
        audit = database_activity([record])[0]
        self.assertEqual(audit['interpreted_system'], 'mongodb')
        self.assertEqual(audit['count'], 1)
        self.assertIsNone(audit['observed_address'])

    def test_child_header_binds_exact_http_parent_and_full_duration(self):
        for code, duration, expected in ((200, 500_000_000, True), (200, 3_000_000_000, False), (500, 500_000_000, False)):
            parent = span('parent', status=code, start=0, end=duration)
            del parent['attributes']['http.request.header.x-experiment-request-id']
            child = {**span('request'), 'trace_id': parent['trace_id'], 'parent_id': parent['span_id'],
                     'kind': 'SPAN_KIND_CLIENT', 'start_ns': 100_000_000, 'end_ns': 1_000_000_000,
                     'attributes': {'http.request.header.x-experiment-request-id': 'request'}}
            projected = Projection([parent, child]).attempt({'step_ids': ['request']})
            self.assertEqual(projected['signature'], ['GET /product'])
            self.assertEqual(projected['observed_window_seconds'], duration/1e9)
            self.assertIs(projected['proxy'], expected)
            self.assertEqual(projected['root_evidence'][0]['binding_path'], ['request', 'parent'])
            parent['source'] = 'native'
            self.assertIsNone(Projection([parent, child]).attempt({'step_ids': ['request']})['proxy'])

    def test_published_database_host_requires_the_selected_port(self):
        db = {'ip': '172.28.11.20', 'transport_host': '192.168.76.11', 'transport_port': 37020}
        self.assertIs(database_reference_match({'address': '192.168.76.11', 'port': 37020}, db), True)
        self.assertIs(database_reference_match({'address': '192.168.76.11', 'port': 37021}, db), False)
        self.assertIsNone(database_reference_match({'address': '192.168.76.11'}, db))

    def test_previous_order_identity_does_not_link_current_execution(self):
        identity = '12345678-1234-1234-1234-123456789abc'
        item = span('http')
        item['attributes'].update({'url.path': '/api/checkout', 'previous_order_id': identity,
                                   'history': {'order_id': identity}})
        self.assertEqual(typed_order_chains([item]), {})
        item['attributes']['order_id'] = identity
        self.assertIn('checkout_http', typed_order_chains([item])[identity])

    def test_wilson_boundary_outcomes_include_zero_and_one(self):
        for n in (1, 60, 80, 240):
            self.assertEqual(wilson(0, n)[0], 0.0)
            self.assertEqual(wilson(n, n)[1], 1.0)

    def test_failure_associated_missing_classes_widen_bounds(self):
        rows = [{'class_id': 'c', 'state': '00', 'proxy': True, 'compatible_classes': ['c']}]
        rows += [{'class_id': None, 'state': '00', 'proxy': None, 'compatible_classes': ['c']}] * 9
        bounds = conditional(rows, 'c', '00')['identification_bounds']
        self.assertEqual(bounds, [.1, 1.0])

    def test_failed_common_prefix_is_not_identified_as_short_operation(self):
        row = {'signature': ['GET /product'], 'proxy': False}
        classes = {'browse': {'signature': ['GET /product']},
                   'checkout': {'signature': ['GET /product', 'POST /cart', 'POST /checkout']}}
        self.assertIsNone(assign(row, classes)['class_id'])

    def test_joint_window_includes_gap_between_steps(self):
        p = Projection([span('a'), span('b', start=3_000_000_000, end=3_001_000_000)])
        self.assertIs(p.attempt({'step_ids': ['a', 'b']})['proxy'], False)

    def test_missing_step_is_unknown_not_success(self):
        self.assertIsNone(Projection([span('a')]).attempt({'step_ids': ['a', 'missing']})['proxy'])

    def test_novel_or_empty_signature_is_not_single_known_class(self):
        classes = {'browse': {'signature': ['GET /product']}}
        for signature in (['POST /checkout'], []):
            self.assertIsNone(assign({'signature': signature, 'proxy': True}, classes)['class_id'])

    def test_census_removes_semantic_labels_and_outcomes(self):
        row = {'attempt_id': 'checkout-secret', 'operation': 'checkout', 'success': True,
               'http_steps': [{'request_id': 'opaque', 'status': 200, 'response_json': {'order': 'x'}}]}
        projected = census([row], 'calibration', '11')[0]
        self.assertEqual(set(projected), {'attempt_key', 'step_ids', 'phase', 'state'})
        self.assertNotIn('checkout', str(projected))

    def test_protobuf_and_json_identifiers_match(self):
        raw = bytes(range(16))
        self.assertEqual(identifier(base64.b64encode(raw).decode(), 'base64'), identifier(raw.hex()))


if __name__ == '__main__':
    unittest.main()
