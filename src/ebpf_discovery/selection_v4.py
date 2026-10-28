"""Select raw observation identities using declared intent and exact headers.

This module constructs no graph and reads no evaluator outcomes. Bering receives
the corresponding complete source records, including conflicting raw variants.
"""
from __future__ import annotations

from collections import defaultdict
import json
import re
from urllib.parse import urlsplit

from .observations import normalized_route


def canonical_route(path):
    return re.sub(r'\{[^}]+\}', '{id}', normalized_route(str(path)))


def valid_identity(trace, span):
    """OTLP IDs or the equivalent native Jaeger 64-bit trace representation."""
    return (bool(re.fullmatch(r'(?:[0-9a-f]{16}|[0-9a-f]{32})', trace or ''))
            and bool(re.fullmatch(r'[0-9a-f]{16}', span or ''))
            and int(trace, 16) != 0 and int(span, 16) != 0)


def method_path(row):
    attrs = row['attributes']
    method = attrs.get('http.request.method', attrs.get('http.method'))
    path = next((attrs[k] for k in ('url.path', 'http.target', 'url.full', 'http.url', 'http.route')
                 if attrs.get(k)), None)
    return method, canonical_route(urlsplit(str(path)).path) if path else None


def bind_entry(store, source, request_id, expected, entry_services, untyped_components=()):
    if not request_id:
        return None, 'request_identity_missing'
    expected = expected['method'], canonical_route(expected['path'])
    selected = {}
    for anchor in store.candidates(source, request_id):
        if anchor['service'] not in entry_services:
            continue
        row, visited, candidate = anchor, set(), None
        while row and row['span_id'] not in visited:
            visited.add(row['span_id'])
            if not valid_identity(row['trace_id'], row['span_id']):
                return None, 'invalid_trace_or_span_identity'
            if row.get('attribute_conflicts'):
                return None, 'conflicting_entry_attributes'
            if len(store.identity(source, row['trace_id'], row['span_id'])) != 1:
                return None, 'conflicting_entry_identity'
            kind = str(row.get('kind'))
            if kind in ('3', 'SPAN_KIND_CLIENT', 'client'):
                candidate = None
                break
            explicit_server = kind in ('2', 'SPAN_KIND_SERVER', 'server')
            untyped = row.get('kind') is None and row['attributes'].get('component') in untyped_components
            if (explicit_server or untyped) and method_path(row) == expected:
                candidate = row
                if explicit_server:
                    break
            parents = store.identity(source, row['trace_id'], row['parent_id']) if row['parent_id'] else []
            if len(parents) > 1:
                return None, 'conflicting_entry_parent'
            row = parents[0] if parents and all(parents[0].get(k) == anchor.get(k)
                       for k in ('service', 'instance', 'node')) else None
        if candidate:
            selected[candidate['trace_id'], candidate['span_id']] = candidate
    if len(selected) != 1:
        return None, 'entry_missing' if not selected else 'multiple_entries'
    return next(iter(selected.values())), 'unique_declared_entry'


def descendant_identities(rows, roots):
    by_id, children = defaultdict(list), defaultdict(set)
    for row in rows:
        by_id[row['span_id']].append(row)
        children[row['parent_id']].add(row['span_id'])
    pending, seen = list(roots), set()
    while pending:
        identity = pending.pop()
        if identity in seen:
            continue
        seen.add(identity)
        variants = by_id[identity]
        if not variants or not valid_identity(variants[0]['trace_id'], identity):
            continue
        # Include every raw variant for this observed child. Ambiguous parentage
        # cannot justify selecting its descendants; Bering decides its graph use.
        yield variants[0]['trace_id'], identity
        if len(variants) == 1:
            pending.extend(children[identity] - seen)


def select_planned(store, plans, contract, source, untyped_components=None):
    wanted = {(s['method'], canonical_route(s['path'])) for s in contract['steps']}
    traces, roots, reasons = defaultdict(set), [], defaultdict(int)
    sources = ('ebpf', 'native') if source == 'combined' else (source,)
    for plan in plans:
        for step in plan['http_steps']:
            if (step['method'], canonical_route(step['path'])) not in wanted:
                continue
            for actual_source in sources:
                root, reason = bind_entry(store, actual_source, step['request_id'], step,
                    contract['entry_services'], (untyped_components or {}).get(actual_source, ()))
                reasons[actual_source + ':' + reason] += 1
                if root:
                    traces[actual_source, root['trace_id']].add(root['span_id'])
                    roots.append({k: root[k] for k in ('source', 'trace_id', 'span_id', 'service')})
    selected = {s: set() for s in sources}
    for (actual_source, trace), ids in sorted(traces.items()):
        rows = [json.loads(encoded) for (encoded,) in store.db.execute(
            'SELECT data FROM spans WHERE source=? AND trace=? ORDER BY digest', (actual_source, trace))]
        selected[actual_source].update(descendant_identities(rows, ids))
    return selected, {'source': source, 'roots': roots, 'binding_reasons': dict(reasons),
        'selected_identity_counts': {s: len(ids) for s, ids in selected.items()},
        'selection': 'declared routes, exact training request IDs and source-local ancestry',
        'clock_gate': False, 'outcomes_used': False, 'ids_rewritten': False}
