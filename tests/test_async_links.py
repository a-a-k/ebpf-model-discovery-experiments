from copy import deepcopy

import pytest

from ebpf_discovery.async_links import message_chains


REQUEST_ID = 'opaque-checkout-step'
PRODUCER_TRACE = '1' * 32
CONSUMER_TRACE = '2' * 32


def span(
    service,
    name,
    trace_id,
    span_id,
    parent_id='',
    *,
    source='native',
    kind=1,
    attributes=None,
    links=None,
):
    return {
        'source': source,
        'node': None,
        'trace_id': trace_id,
        'span_id': span_id,
        'parent_id': parent_id,
        'service': service,
        'instance': None,
        'name': name,
        'kind': kind,
        'start_ns': 1,
        'end_ns': 2,
        'attributes': attributes or {},
        'resource': {},
        'status': {},
        'links': links or [],
    }


def fixture():
    query = '''INSERT INTO accounting."order" (order_id) VALUES (@p0);
INSERT INTO accounting.orderitem (order_id) VALUES (@p1);
INSERT INTO accounting.shipping (order_id) VALUES (@p2);'''
    return [
        span(
            'frontend',
            'POST',
            PRODUCER_TRACE,
            'anchor',
            kind=2,
            attributes={
                'http.request.method': 'POST',
                'http.route': '/api/checkout',
                'http.request.header.x_experiment_request_id': [REQUEST_ID],
            },
        ),
        span(
            'checkout',
            'oteldemo.CheckoutService/PlaceOrder',
            PRODUCER_TRACE,
            'checkout',
            'anchor',
            kind=2,
            attributes={'demo.order.id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'},
        ),
        span(
            'checkout',
            'orders publish',
            PRODUCER_TRACE,
            'producer',
            'checkout',
            kind=4,
            attributes={
                'messaging.system': 'kafka',
                'messaging.operation': 'publish',
                'messaging.destination.name': 'orders',
            },
        ),
        span('accounting', 'order-consumed', CONSUMER_TRACE, 'root'),
        span(
            'accounting',
            'orders receive',
            CONSUMER_TRACE,
            'consumer',
            'root',
            kind=5,
            attributes={
                'messaging.system': 'kafka',
                'messaging.operation': 'receive',
                'messaging.destination.name': 'orders',
            },
            links=[{'trace_id': PRODUCER_TRACE, 'span_id': 'producer'}],
        ),
        # CONNECT is deliberately a sibling but cannot establish a write.
        span(
            'accounting',
            'CONNECT astronomy_db',
            CONSUMER_TRACE,
            'connect',
            'root',
            kind=3,
            attributes={'db.system.name': 'postgresql'},
        ),
        span(
            'accounting',
            'postgresql',
            CONSUMER_TRACE,
            'write',
            'root',
            kind=3,
            attributes={
                'db.system.name': 'postgresql',
                'db.query.text': query,
            },
        ),
    ]


def native_result(spans):
    return message_chains(spans)[REQUEST_ID]['sources']['native']


def test_message_chain_uses_exact_span_link_and_three_insert_write():
    result = native_result(fixture())
    assert result['status'] == 'linked'
    assert result['reason'] is None
    assert result['span_link'] == {
        'trace_id': PRODUCER_TRACE,
        'span_id': 'producer',
    }
    assert [item['span_id'] for item in result['anchor_to_producer_path']] == [
        'anchor',
        'checkout',
        'producer',
    ]
    assert [
        item['span_id'] for item in result['consumer_to_processing_root_path']
    ] == [
        'consumer',
        'root',
    ]
    assert [
        item['span_id'] for item in result['processing_root_to_database_write_path']
    ] == [
        'root',
        'write',
    ]
    assert result['producer']['messaging.operation'] == 'publish'
    assert result['consumer']['messaging.operation'] == 'receive'
    assert result['database_write']['span_id'] == 'write'
    assert result['database_write']['insert_targets'] == [
        'accounting.order',
        'accounting.orderitem',
        'accounting.shipping',
    ]
    assert result['application_order_id']['field'] == 'demo.order.id'
    assert result['association_only'] is True
    assert result['durability_established'] is False


def test_message_chain_never_borrows_links_between_sources():
    spans = fixture()
    native_consumer = next(item for item in spans if item['span_id'] == 'consumer')
    native_consumer['source'] = 'ebpf'
    ebpf_anchor = deepcopy(next(item for item in spans if item['span_id'] == 'anchor'))
    ebpf_anchor['source'] = 'ebpf'
    ebpf_anchor['span_id'] = 'ebpf-anchor'
    spans.append(ebpf_anchor)

    results = message_chains(spans)[REQUEST_ID]['sources']
    assert results['native']['status'] == 'unknown'
    assert results['native']['reason'] == 'missing_linked_consumer'
    assert results['ebpf']['status'] == 'unknown'
    assert results['ebpf']['reason'] == 'missing_producer_descendant'


@pytest.mark.parametrize(
    ('mutation', 'reason'),
    [
        ('missing_consumer', 'missing_linked_consumer'),
        ('ambiguous_consumer', 'ambiguous_linked_consumer'),
        ('ambiguous_links', 'ambiguous_consumer_span_links'),
        ('ambiguous_producer', 'ambiguous_producer_descendant'),
        ('missing_write', 'missing_database_write'),
        ('ambiguous_write', 'ambiguous_database_write'),
    ],
)
def test_message_chain_returns_unknown_for_missing_or_ambiguous_evidence(
    mutation, reason
):
    spans = fixture()
    if mutation == 'missing_consumer':
        spans = [item for item in spans if item['span_id'] != 'consumer']
    elif mutation == 'ambiguous_consumer':
        duplicate = deepcopy(next(item for item in spans if item['span_id'] == 'consumer'))
        duplicate['span_id'] = 'consumer-2'
        spans.append(duplicate)
    elif mutation == 'ambiguous_links':
        consumer = next(item for item in spans if item['span_id'] == 'consumer')
        consumer['links'].append({'trace_id': '3' * 32, 'span_id': 'other'})
    elif mutation == 'ambiguous_producer':
        duplicate = deepcopy(next(item for item in spans if item['span_id'] == 'producer'))
        duplicate['span_id'] = 'producer-2'
        spans.append(duplicate)
    elif mutation == 'missing_write':
        spans = [item for item in spans if item['span_id'] != 'write']
    elif mutation == 'ambiguous_write':
        duplicate = deepcopy(next(item for item in spans if item['span_id'] == 'write'))
        duplicate['span_id'] = 'write-2'
        spans.append(duplicate)

    result = native_result(spans)
    assert result['status'] == 'unknown'
    assert result['reason'] == reason
    assert result['durability_established'] is False


def test_connect_or_partial_insert_query_is_not_a_database_write():
    spans = fixture()
    write = next(item for item in spans if item['span_id'] == 'write')
    write['attributes']['db.query.text'] = (
        'INSERT INTO accounting."order" (order_id) VALUES (@p0);'
    )
    result = native_result(spans)
    assert result['status'] == 'unknown'
    assert result['reason'] == 'missing_database_write'
