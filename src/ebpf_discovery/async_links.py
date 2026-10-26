"""Conservative asynchronous message-chain evidence from normalized spans.

This module proves association only.  Durable completion and its deadline are
evaluated independently from timestamped SQL oracle reads.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from .observations import route, step_id


KAFKA_PRODUCER_OPERATIONS = {'publish', 'produce', 'send'}
KAFKA_CONSUMER_OPERATIONS = {'fetch', 'process', 'receive'}
POSTGRES_SYSTEMS = {'postgres', 'postgresql'}
IGNORED_OBSERVATION_FIELDS = {'raw_file', '_graph_node'}


def _operation(attributes: dict[str, Any]) -> str:
    return str(
        attributes.get(
            'messaging.operation.type',
            attributes.get(
                'messaging.operation.name',
                attributes.get('messaging.operation', ''),
            ),
        )
    ).lower()


def _span_ref(span: dict[str, Any]) -> dict[str, Any]:
    return {
        'source': span['source'],
        'service': span['service'],
        'name': span['name'],
        'trace_id': span['trace_id'],
        'span_id': span['span_id'],
        'parent_id': span['parent_id'],
    }


def _message_ref(span: dict[str, Any]) -> dict[str, Any]:
    attributes = span['attributes']
    return {
        **_span_ref(span),
        'messaging.system': attributes.get('messaging.system'),
        'messaging.operation': _operation(attributes),
        'messaging.destination': attributes.get('messaging.destination.name'),
        'messaging.partition': attributes.get(
            'messaging.kafka.destination.partition',
            attributes.get('messaging.destination.partition.id'),
        ),
        'messaging.offset': attributes.get(
            'messaging.kafka.message.offset', attributes.get('messaging.kafka.offset')
        ),
    }


def _is_server(span: dict[str, Any]) -> bool:
    return span.get('kind') in (2, 'server', 'SPAN_KIND_SERVER')


def _is_producer(span: dict[str, Any]) -> bool:
    attributes = span['attributes']
    return (
        span['service'].lower() == 'checkout'
        and attributes.get('messaging.system') == 'kafka'
        and _operation(attributes) in KAFKA_PRODUCER_OPERATIONS
    )


def _is_consumer(span: dict[str, Any]) -> bool:
    attributes = span['attributes']
    return (
        span['service'].lower() == 'accounting'
        and attributes.get('messaging.system') == 'kafka'
        and _operation(attributes) in KAFKA_CONSUMER_OPERATIONS
    )


def _is_insert_write(span: dict[str, Any]) -> bool:
    attributes = span['attributes']
    if span['service'].lower() != 'accounting':
        return False
    if attributes.get('db.system.name', attributes.get('db.system')) not in POSTGRES_SYSTEMS:
        return False
    query = attributes.get('db.query.text')
    if not isinstance(query, str):
        return False
    normalized = ' '.join(query.lower().split())
    statements = (
        'insert into accounting."order"',
        'insert into accounting.orderitem',
        'insert into accounting.shipping',
    )
    return all(normalized.count(statement) == 1 for statement in statements)


def _observation_key(span: dict[str, Any]) -> str:
    """Canonical normalized evidence, excluding parser provenance/cache fields."""
    evidence = {
        key: value
        for key, value in span.items()
        if key not in IGNORED_OBSERVATION_FIELDS
    }
    return json.dumps(evidence, sort_keys=True, separators=(',', ':'))


def _deduplicate(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique = {}
    for span in spans:
        unique.setdefault(_observation_key(span), span)
    return list(unique.values())


def _span_index(
    spans: list[dict[str, Any]],
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for span in spans:
        grouped[(span['trace_id'], span['span_id'])].append(span)
    return {identity: _deduplicate(records) for identity, records in grouped.items()}


def _valid_identity(span: dict[str, Any]) -> bool:
    return bool(span.get('trace_id') and span.get('span_id'))


def _ancestry(
    span: dict[str, Any],
    lookup: dict[tuple[str, str], list[dict[str, Any]]],
    stop: tuple[str, str],
) -> tuple[list[dict[str, Any]], str | None]:
    path, visited = [], set()
    current = span
    while current and current['span_id'] not in visited:
        if not _valid_identity(current):
            return path, 'empty_ancestry_identity'
        records = lookup.get((current['trace_id'], current['span_id']), [])
        if len(records) != 1:
            return path, 'ambiguous_ancestry_identity'
        visited.add(current['span_id'])
        path.append(current)
        if (current['trace_id'], current['span_id']) == stop:
            break
        if not current['parent_id']:
            break
        parents = lookup.get((current['trace_id'], current['parent_id']), [])
        if len(parents) > 1:
            return path, 'ambiguous_ancestry_identity'
        current = parents[0] if parents else None
    return path, None


def _unknown(
    source: str, reason: str, anchor: dict[str, Any] | None = None, **evidence: Any
) -> dict[str, Any]:
    result = {
        'status': 'unknown',
        'reason': reason,
        'source': source,
        'association_only': True,
        'durability_established': False,
    }
    if anchor is not None:
        result['anchor'] = _span_ref(anchor)
    result.update(evidence)
    return result


def _application_order_evidence(path: list[dict[str, Any]]) -> dict[str, Any] | None:
    observed = []
    for span in path:
        value = span['attributes'].get('demo.order.id')
        if isinstance(value, str):
            observed.append(
                {
                    'field': 'demo.order.id',
                    'value': value,
                    'span': _span_ref(span),
                }
            )
    return observed[0] if len(observed) == 1 else None


def _source_chain(
    source: str,
    source_spans: list[dict[str, Any]],
    anchors: list[dict[str, Any]],
) -> dict[str, Any]:
    anchors = _deduplicate(anchors)
    if len(anchors) != 1:
        return _unknown(
            source,
            'ambiguous_checkout_anchor',
            anchor_candidates=[_span_ref(span) for span in anchors],
        )
    anchor = anchors[0]
    if not _valid_identity(anchor):
        return _unknown(source, 'empty_anchor_identity', anchor)
    lookup = _span_index(source_spans)
    if len(lookup.get((anchor['trace_id'], anchor['span_id']), [])) != 1:
        return _unknown(source, 'ambiguous_anchor_identity', anchor)
    indexed_spans = [record for records in lookup.values() for record in records]

    producers = []
    producer_paths: dict[str, list[dict[str, Any]]] = {}
    ancestry_issues = []
    for span in indexed_spans:
        if not _is_producer(span) or span['trace_id'] != anchor['trace_id']:
            continue
        ancestry, issue = _ancestry(
            span, lookup, (anchor['trace_id'], anchor['span_id'])
        )
        if issue is not None:
            ancestry_issues.append(issue)
            continue
        if any(parent['span_id'] == anchor['span_id'] for parent in ancestry):
            producers.append(span)
            producer_paths[span['span_id']] = list(reversed(ancestry[: ancestry.index(anchor) + 1]))
    if not producers:
        if ancestry_issues:
            return _unknown(source, sorted(ancestry_issues)[0], anchor)
        return _unknown(source, 'missing_producer_descendant', anchor)
    if len(producers) != 1:
        return _unknown(
            source,
            'ambiguous_producer_descendant',
            anchor,
            producer_candidates=[_span_ref(span) for span in producers],
        )
    producer = producers[0]
    if not _valid_identity(producer):
        return _unknown(source, 'empty_producer_identity', anchor)
    producer_path = producer_paths[producer['span_id']]
    producer_identity = {
        'trace_id': producer['trace_id'],
        'span_id': producer['span_id'],
    }

    consumers = []
    for span in indexed_spans:
        if not _is_consumer(span):
            continue
        if any(
            link.get('trace_id') == producer['trace_id']
            and link.get('span_id') == producer['span_id']
            for link in span.get('links', [])
        ):
            consumers.append(span)
    if not consumers:
        return _unknown(
            source,
            'missing_linked_consumer',
            anchor,
            producer=_message_ref(producer),
            anchor_to_producer_path=[_span_ref(span) for span in producer_path],
        )
    if len(consumers) != 1:
        return _unknown(
            source,
            'ambiguous_linked_consumer',
            anchor,
            producer=_message_ref(producer),
            consumer_candidates=[_message_ref(span) for span in consumers],
        )
    consumer = consumers[0]
    if not _valid_identity(consumer):
        return _unknown(
            source,
            'empty_consumer_identity',
            anchor,
            producer=_message_ref(producer),
        )
    if len(lookup.get((consumer['trace_id'], consumer['span_id']), [])) != 1:
        return _unknown(
            source,
            'ambiguous_consumer_identity',
            anchor,
            producer=_message_ref(producer),
            consumer_candidates=[
                _message_ref(span)
                for span in lookup[(consumer['trace_id'], consumer['span_id'])]
            ],
        )
    if len(consumer.get('links', [])) != 1:
        return _unknown(
            source,
            'ambiguous_consumer_span_links',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
            observed_links=consumer.get('links', []),
        )

    if not consumer['parent_id']:
        return _unknown(
            source,
            'empty_processing_root_identity',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
        )
    processing_roots = lookup.get((consumer['trace_id'], consumer['parent_id']), [])
    if not processing_roots:
        return _unknown(
            source,
            'missing_processing_root',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
        )
    if len(processing_roots) != 1:
        return _unknown(
            source,
            'ambiguous_processing_root_identity',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
            processing_root_candidates=[
                _span_ref(span) for span in processing_roots
            ],
        )
    processing_root = processing_roots[0]
    if (
        processing_root['service'].lower() != 'accounting'
        or processing_root['name'] != 'order-consumed'
    ):
        return _unknown(
            source,
            'invalid_processing_root',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
            processing_root=_span_ref(processing_root),
        )

    writes = [
        span
        for span in indexed_spans
        if span['trace_id'] == processing_root['trace_id']
        and span['parent_id'] == processing_root['span_id']
        and _is_insert_write(span)
    ]
    if not writes:
        return _unknown(
            source,
            'missing_database_write',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
            processing_root=_span_ref(processing_root),
        )
    if len(writes) != 1:
        return _unknown(
            source,
            'ambiguous_database_write',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
            processing_root=_span_ref(processing_root),
            database_write_candidates=[_span_ref(span) for span in writes],
        )
    write = writes[0]
    if not _valid_identity(write):
        return _unknown(
            source,
            'empty_database_write_identity',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
            processing_root=_span_ref(processing_root),
        )
    if len(lookup.get((write['trace_id'], write['span_id']), [])) != 1:
        return _unknown(
            source,
            'ambiguous_database_write_identity',
            anchor,
            producer=_message_ref(producer),
            consumer=_message_ref(consumer),
            processing_root=_span_ref(processing_root),
            database_write_candidates=[
                _span_ref(span)
                for span in lookup[(write['trace_id'], write['span_id'])]
            ],
        )
    result = {
        'status': 'linked',
        'reason': None,
        'source': source,
        'association_only': True,
        'durability_established': False,
        'anchor': _span_ref(anchor),
        'producer': _message_ref(producer),
        'anchor_to_producer_path': [_span_ref(span) for span in producer_path],
        'consumer': _message_ref(consumer),
        'span_link': producer_identity,
        'processing_root': _span_ref(processing_root),
        'consumer_to_processing_root_path': [
            _span_ref(consumer),
            _span_ref(processing_root),
        ],
        'processing_root_to_database_write_path': [
            _span_ref(processing_root),
            _span_ref(write),
        ],
        'database_write': {
            **_span_ref(write),
            'db.system': write['attributes'].get(
                'db.system.name', write['attributes'].get('db.system')
            ),
            'query_field': 'db.query.text',
            'insert_targets': [
                'accounting.order',
                'accounting.orderitem',
                'accounting.shipping',
            ],
        },
    }
    application_order = _application_order_evidence(producer_path)
    if application_order is not None:
        result['application_order_id'] = application_order
    return result


def message_chains(spans: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return exact checkout-to-accounting association evidence by opaque ID.

    Results remain partitioned by observation source.  Missing or ambiguous
    evidence is ``unknown``; this function never returns a negative business
    outcome and never treats association as durable completion.
    """
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    anchors: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for span in spans:
        source = span['source']
        by_source[source].append(span)
        request_id = step_id(span)
        if (
            request_id
            and span['service'].lower() == 'frontend'
            and _is_server(span)
            and route(span) == 'POST /api/checkout'
        ):
            anchors[(source, request_id)].append(span)

    results: dict[str, dict[str, Any]] = defaultdict(lambda: {'sources': {}})
    for (source, request_id), source_anchors in anchors.items():
        results[request_id]['sources'][source] = _source_chain(
            source, by_source[source], source_anchors
        )
    return dict(results)
