"""Descriptive v4 evidence readout from retained inputs and actual Bering outputs.

This module neither discovers graph structure nor selects observations for a fit.
All application outcomes are used only for the separate evaluation readout.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from .runtime import write_json
from .selection_v4 import valid_identity


SOURCES = ('ebpf', 'native', 'combined')
VARIANTS = ('raw', 'network_scope')


def _read(path):
    path = Path(path)
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def _quality(quality):
    return {(r.get('entity_type'), r.get('entity_id')): r.get('evidence') or {}
            for r in (quality or {}).get('observation_evidence', [])}


def _alias_key(alias):
    """A logical database endpoint is identified by all four observed fields."""
    if not isinstance(alias, dict) or alias.get('identity_kind') != 'logical_endpoint':
        return None
    system, address, port, scope = (alias.get(k) for k in
                                     ('system', 'address', 'port', 'network_scope'))
    if not all((system, address, port, scope)):
        return None
    return (str(system).lower(), str(address).lower(), str(port), str(scope))


def _graph(folder):
    model = _read(folder/'observed.json')
    quality = _read(folder/'observed.signal-quality.json')
    snapshot = _read(folder/'observed.snapshot.json')
    final_model = _read(folder/'model.json')
    final_quality = _read(folder/'model.signal-quality.json')
    final_snapshot = _read(folder/'model.snapshot.json')
    mapping = _read(folder/'database-mapping.json')
    forecast = _read(folder/'forecast.json')
    if model is None:
        return {'available': False, 'reason': 'observed_bering_graph_absent',
                'forecast_available': bool(forecast and forecast.get('available'))}
    services = model.get('services') or []
    edges = model.get('edges') or []
    endpoints = model.get('endpoints') or []
    evidence = _quality(quality)
    aliases = defaultdict(lambda: {'nodes': set(), 'callers': set(), 'witnesses': []})
    incomplete_aliases = []
    aliases_by_node = defaultdict(list)
    observed_instances = set()
    for service in services:
        sid = service.get('id')
        ev = evidence.get(('service', sid), {})
        for instance in ev.get('instances') or []:
            if instance.get('identity_status') == 'observed':
                observed_instances.add((sid, json.dumps(instance, sort_keys=True)))
        for alias in ([ev['database']] if ev.get('database') else []) + (ev.get('database_aliases') or []):
            aliases_by_node[sid].append(alias)
            key = _alias_key(alias)
            if key:
                aliases[key]['nodes'].add(sid)
                aliases[key]['witnesses'].append({'entity_type': 'service', 'entity_id': sid})
            else:
                incomplete_aliases.append({'entity_type': 'service', 'entity_id': sid,
                                           'observed_alias': alias, 'logical_identity': 'unknown'})
    for edge in edges:
        ev = evidence.get(('edge', edge.get('id')), {})
        for alias in ev.get('database_aliases') or []:
            aliases_by_node[edge.get('to')].append(alias)
            key = _alias_key(alias)
            if key:
                aliases[key]['nodes'].add(edge.get('to'))
                aliases[key]['witnesses'].append({'entity_type': 'edge', 'entity_id': edge.get('id')})
            else:
                incomplete_aliases.append({'entity_type': 'edge', 'entity_id': edge.get('id'),
                                           'observed_alias': alias, 'logical_identity': 'unknown'})
    for edge in edges:
        for data in aliases.values():
            if edge.get('to') in data['nodes']:
                data['callers'].add(edge.get('from'))
    alias_rows = [dict(system=k[0], address=k[1], port=k[2], network_scope=k[3],
                       identity_kind='logical_endpoint', nodes=sorted(v['nodes']),
                       callers=sorted(v['callers']), shared_by_at_least_two_callers=len(v['callers']) >= 2,
                       observed_witnesses=v['witnesses']) for k, v in sorted(aliases.items())]
    mapped = set((mapping or {}).get('matched_observed_nodes') or [])
    mapped_witnesses = (mapping or {}).get('witnesses') or []
    mapping_checks = []
    for witness in mapped_witnesses:
        key = _alias_key(witness.get('observed_alias'))
        mapping_checks.append({'node': witness.get('node'), 'alias_key': list(key) if key else None,
                               'present_in_observed_evidence': witness.get('observed_alias') in
                                   aliases_by_node.get(witness.get('node'), [])})
    db_impact = {'status': 'unknown', 'reason': 'mapped_database_or_forecast_unavailable',
                 'state_11': None, 'database_down': None}
    if mapped and forecast and forecast.get('available'):
        state11 = (forecast.get('by_state') or {}).get('11')
        dbdown = forecast.get('database_down_prediction')
        if state11 is not None and dbdown is not None:
            db_impact = {'status': 'available', 'state_11': state11,
                         'database_down': dbdown, 'difference': state11-dbdown,
                         'meaning': 'separate graph interventions, not an observed business outcome'}
        else:
            db_impact['reason'] = 'conditional_database_or_profile_unavailable'
    return {'available': True, 'services': len(services), 'edges': len(edges),
            'endpoints': len(endpoints), 'observed_instance_evidence': len(observed_instances),
            'bering_outputs_present': {'observed_model': True, 'observed_snapshot': snapshot is not None,
                'observed_quality': quality is not None, 'final_model': final_model is not None,
                'final_snapshot': final_snapshot is not None, 'final_quality': final_quality is not None},
            'snapshot_discovery_counts': {kind: len((snapshot or {}).get('discovery', {}).get(kind) or [])
                                          for kind in ('services', 'edges', 'endpoints')},
            'final_model_counts_after_supplied_overlay': None if final_model is None else
                {kind: len(final_model.get(kind) or []) for kind in ('services', 'edges', 'endpoints')},
            'database_aliases': alias_rows,
            'incomplete_database_aliases': incomplete_aliases,
            'database_mapping': {'available': mapping is not None, 'matched_observed_nodes': sorted(mapped),
                                 'witness_checks': mapping_checks,
                                 'all_saved_witnesses_reproduced': bool(mapped_witnesses) and all(
                                     w['present_in_observed_evidence'] for w in mapping_checks),
                                 'physical_identity_inferred': False},
            'database_fault_prognostic_impact': db_impact}


def _planned_ids(plans):
    return {step['request_id'] for plan in plans for step in plan.get('http_steps', [])
            if step.get('request_id')}


def _cross_guest(store, plans):
    """Exact, source-local parent links; header agreement is independent evidence."""
    ids = _planned_ids(plans)
    # The unique-identity relation avoids arbitrary selection among conflicting
    # exports. It is a TEMP relation, leaving the retained observation index intact.
    store.db.execute('DROP TABLE IF EXISTS temp.evidence_v4_unique')
    store.db.execute('''CREATE TEMP TABLE evidence_v4_unique AS
        SELECT source, trace, span FROM spans
        WHERE trace IS NOT NULL AND trace!='' AND span IS NOT NULL AND span!=''
        GROUP BY source,trace,span
        HAVING COUNT(*)=1 AND MAX(conflicted)=0''')
    store.db.execute('CREATE UNIQUE INDEX evidence_v4_unique_key ON evidence_v4_unique(source,trace,span)')
    sql = '''SELECT c.source,c.node,c.trace,c.span,c.parent,c.request,c.digest,
                    p.node,p.span,p.request,p.digest
             FROM spans c JOIN evidence_v4_unique cu
                  ON cu.source=c.source AND cu.trace=c.trace AND cu.span=c.span
             JOIN spans p ON p.source=c.source AND p.trace=c.trace AND p.span=c.parent
             JOIN evidence_v4_unique pu
                  ON pu.source=p.source AND pu.trace=p.trace AND pu.span=p.span
             WHERE c.node IN ('a','b') AND p.node IN ('a','b') AND c.node!=p.node'''
    counts = defaultdict(Counter)
    invalid = Counter()
    witnesses = defaultdict(lambda: defaultdict(list))
    for source, child_node, trace, child, parent, child_req, child_digest, parent_node, _, parent_req, parent_digest in store.db.execute(sql):
        if source not in ('ebpf', 'native'):
            continue
        if not valid_identity(trace, child) or not valid_identity(trace, parent):
            invalid[source] += 1
            continue
        if child_req and parent_req and child_req in ids and parent_req in ids:
            verdict = 'corroborated_same_planned_header' if child_req == parent_req else 'contradictory_planned_headers'
        else:
            verdict = 'unknown_missing_or_unplanned_header'
        counts[source][verdict] += 1
        if len(witnesses[source][verdict]) < 5:
            witnesses[source][verdict].append({'source': source, 'trace_id': trace,
                'child_span_id': child, 'parent_span_id': parent, 'child_node': child_node,
                'parent_node': parent_node, 'child_request_id': child_req,
                'parent_request_id': parent_req, 'child_digest': child_digest,
                'parent_digest': parent_digest})
    store.db.execute('DROP TABLE temp.evidence_v4_unique')
    return {source: {'exact_parent_links': sum(counts[source].values()),
                     'invalid_identity_candidates': invalid[source],
                     'header_verdicts': dict(counts[source]),
                     'witnesses': dict(witnesses[source]),
                     'interpretation': 'structural parent link; header comparison does not prove application correctness'}
            for source in ('ebpf', 'native')}


def _async(root, store, records):
    """Report markers, retaining unknown for unsupported order-specific links."""
    from .async_links import message_chains
    selected = [r for r in records if str(r.get('phase', '')).startswith('async_')]
    rows = [{'step_ids': [s['request_id'] for s in r.get('http_steps', []) if s.get('request_id')]}
            for r in selected]
    spans = store.request_traces(rows, linked_consumers=True) if rows else []
    invalid = [s for s in spans if not valid_identity(s.get('trace_id'), s.get('span_id'))]
    spans = [s for s in spans if valid_identity(s.get('trace_id'), s.get('span_id'))]
    chains = message_chains(spans)
    by_identity = defaultdict(list)
    for span in spans:
        by_identity[(span.get('source'), span.get('trace_id'), span.get('span_id'))].append(span)

    def source_span(ref):
        if not ref:
            return None
        values = by_identity.get((ref.get('source'), ref.get('trace_id'), ref.get('span_id')), [])
        return values[0] if len(values) == 1 and not values[0].get('attribute_conflicts') else None

    def explicit_order_ids(span):
        if not span:
            return set()
        attrs = span.get('attributes') or {}
        values = {str(attrs['demo.order.id'])} if attrs.get('demo.order.id') else set()
        for key in ('http.request.body', 'http.response.body'):
            body = attrs.get(key)
            if not isinstance(body, str):
                continue
            try:
                decoded = json.loads(body)
            except (ValueError, TypeError):
                continue
            if isinstance(decoded, dict):
                for field in ('orderId', 'order_id'):
                    if isinstance(decoded.get(field), str) and decoded[field]:
                        values.add(decoded[field])
        sql = attrs.get('db.query.text')
        if isinstance(sql, str):
            # Only a literal explicitly attached to an order_id column qualifies.
            values.update(re.findall(r"\border_id\s*=\s*'([^']+)'", sql, re.I))
        return values

    def message_id(span):
        if not span:
            return None
        value = (span.get('attributes') or {}).get('messaging.message.id')
        return str(value) if value is not None and str(value) else None

    result = []
    for record in selected:
        request_ids = [s['request_id'] for s in record.get('http_steps', []) if s.get('request_id')]
        for source in ('ebpf', 'native'):
            links = [chains.get(rid, {}).get('sources', {}).get(source) for rid in request_ids]
            linked = [item for item in links if item and item.get('status') == 'linked']
            proofs = []
            for item in linked:
                producer = source_span(item.get('producer'))
                consumer = source_span(item.get('consumer'))
                write = source_span(item.get('database_write'))
                processing = source_span(item.get('processing_root'))
                participants_present = all(s is not None for s in (producer, consumer, write, processing))
                left, right = message_id(producer), message_id(consumer)
                source_orders = set().union(*(explicit_order_ids(s) for s in (producer, consumer, processing, write)))
                # Source evidence selects the chain; external order IDs only
                # evaluate its business identity after association is resolved.
                declared_order = item.get('application_order_id', {}).get('value')
                if declared_order:
                    source_orders.add(str(declared_order))
                contradiction = bool(left and right and left != right)
                proofs.append({'proof_kind': 'exact_consumer_span_link',
                    'association': 'observed' if participants_present and not contradiction else 'unknown',
                    'unique_participants_present': participants_present,
                    'message_identifier_conflict': contradiction,
                    'explicit_message_id_corroboration': left == right if left and right else None,
                    'source_order_ids': sorted(source_orders),
                    'source_order_corroboration': bool(explicit_order_ids(producer) &
                        (explicit_order_ids(consumer) | explicit_order_ids(processing) | explicit_order_ids(write))),
                    'external_order_agreement': (all(value == str(record['order_id']) for value in source_orders)
                        if source_orders and record.get('order_id') else None),
                    'chain': item})
            markers = {'checkout_trace_context': bool(any(links)),
                       'kafka_producer_consumer_span_link': bool(linked),
                       'accounting_database_write_span': bool(linked),
                       'external_order_id': bool(record.get('order_id')),
                       'source_order_id': any(p['source_order_ids'] for p in proofs),
                       'same_explicit_message_id_across_stages': any(p['explicit_message_id_corroboration'] is True for p in proofs)}
            strong = len(proofs) == 1 and proofs[0]['association'] == 'observed'
            result.append({'attempt_id': record.get('attempt_id'), 'phase': record.get('phase'),
                           'source': source, 'request_ids': request_ids,
                           'four_stage_causal_chain': 'observed' if strong else 'unknown',
                           'proofs': proofs,
                           'markers': markers,
                           'unresolved_markers': [k for k,v in markers.items() if not v],
                           'trace_context_reasons': [item.get('reason') for item in links if item]})
    external = {name: _read(root/name) for name in ('async-normal-persistence.json',
        'async-paused-snapshot.json', 'async-paused-after-resume.json',
        'async-recovered-persistence.json')}
    return {'attempts': result, 'invalid_identity_observations': len(invalid),
            'linker_scope': 'exact source-local ancestry plus consumer SpanLink; ID-only joins without SpanLinks are not implemented and remain unknown',
            'external_verification_files_present':
            {k: v is not None for k,v in external.items()},
            'interpretation': 'external order IDs and persistence files are evaluation evidence only'}


def evaluate(ctx, system, store, plans, records):
    """Write evidence-v4.json without modifying graphs, captures, or outcomes."""
    root = Path(ctx.out)
    operations = sorted({p.get('operation') for p in plans if p.get('operation')})
    graphs = {source: {variant: {operation: _graph(root/'toolchain'/source/variant/operation)
                                 for operation in operations}
                       for variant in VARIANTS} for source in SOURCES}
    result = {'schema_version': '1.0', 'system': system,
              'population': {'planned_attempts': len(plans), 'recorded_attempts': len(records),
                             'operations': dict(Counter(p.get('operation') for p in plans))},
              'graphs': graphs, 'cross_guest': _cross_guest(store, plans),
              'async': _async(root, store, records) if system == 'otel_demo' else None,
              'scope': 'descriptive actual saved outputs; no graph mutation or success claim'}
    write_json(root/'evidence-v4.json', result)
    return result
