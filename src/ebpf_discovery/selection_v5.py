"""Common graph-v5 entry binding over retained observations, with optional ancestry."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json

from .selection_v4 import canonical_route, descendant_identities, method_path, valid_identity


_SERVER_KINDS = (2, '2', 'SPAN_KIND_SERVER', 'server')
_UNTYPED_KINDS = (None, 0, '0', 'SPAN_KIND_UNSPECIFIED')


def _canonical_digest(row):
    evidence = {key: value for key, value in row.items()
                if key not in ('raw_file', '_observation_digest', '_observation_provenance')}
    return hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def _candidates(store, source, request_id):
    if hasattr(store, 'candidates_v5'):
        return store.candidates_v5(source, request_id)
    rows = store.candidates(source, request_id)
    for row in rows:
        row['_observation_digest'] = _canonical_digest(row)
        row['_observation_provenance'] = [{'raw_file': row.get('raw_file'),
            'status': 'legacy_index_has_no_occurrence_table'}]
    return rows


def bind_entry(store, source, request_id, expected, entry_services, untyped_components=()):
    """Bind one content-distinct retained server observation; IDs are optional."""
    if not request_id:
        return None, 'request_identity_missing'
    expected_identity = (str(expected.get('method') or '').upper(),
                         canonical_route(expected.get('path') or ''))
    matches, conflicted_matches = {}, {}
    for row in _candidates(store, source, request_id):
        if row.get('service') not in entry_services:
            continue
        explicit = row.get('kind') in _SERVER_KINDS
        supplied = (row.get('kind') in _UNTYPED_KINDS
                    and row.get('attributes', {}).get('component') in untyped_components)
        if not (explicit or supplied):
            continue
        observed = method_path(row)
        observed_identity = (str(observed[0] or '').upper(), observed[1])
        if observed_identity != expected_identity:
            continue
        row['_entry_server_role'] = 'observed_server' if explicit else 'declared_untyped_receiver'
        target = conflicted_matches if row.get('attribute_conflicts') else matches
        target[row['_observation_digest']] = row
    if conflicted_matches:
        return None, 'conflicting_matching_entry_evidence'
    if len(matches) != 1:
        return None, 'entry_missing' if not matches else 'multiple_distinct_entries'
    return next(iter(matches.values())), 'unique_observation_entry'


def select_planned(store, plans, contract, source, untyped_components=None, *,
                   include_descendants=True):
    wanted = {(str(step['method']).upper(), canonical_route(step['path']))
              for step in contract['steps']}
    sources = ('ebpf', 'native') if source == 'combined' else (source,)
    selected = {item: set() for item in sources}
    roots, reasons, digests = [], defaultdict(int), {item: set() for item in sources}
    for plan in plans:
        for step in plan['http_steps']:
            if (str(step['method']).upper(), canonical_route(step['path'])) not in wanted:
                continue
            for actual_source in sources:
                root, reason = bind_entry(store, actual_source, step.get('request_id'), step,
                    contract['entry_services'], (untyped_components or {}).get(actual_source, ()))
                reasons[actual_source+':'+reason] += 1
                if root is None:
                    continue
                genuine = valid_identity(root.get('trace_id'), root.get('span_id'))
                roots.append({
                    'source': actual_source, 'trace_id': root.get('trace_id', ''),
                    'span_id': root.get('span_id', ''), 'service': root['service'],
                    'request_id': step['request_id'], 'method': str(step['method']).upper(),
                    'path': canonical_route(step['path']), 'binding_reason': reason,
                    'observation_digest': root['_observation_digest'],
                    'observation_provenance': root['_observation_provenance'],
                    'server_role_basis': root['_entry_server_role'],
                    'genuine_ancestry_identity': genuine,
                })
                digests[actual_source].add(root['_observation_digest'])
                if not genuine:
                    reasons[actual_source+':ancestry_unavailable_missing_genuine_ids'] += 1
                    continue
                if not include_descendants:
                    selected[actual_source].add((root['trace_id'], root['span_id']))
                    continue
                rows = (store.trace_v5(actual_source, root['trace_id'])
                        if hasattr(store, 'trace_v5') else
                        [json.loads(encoded) for (encoded,) in store.db.execute(
                         'SELECT data FROM spans WHERE source=? AND trace=? ORDER BY digest',
                         (actual_source, root['trace_id']))])
                selected[actual_source].update(descendant_identities(rows, {root['span_id']}))
    return selected, {
        'source': source, 'roots': roots, 'binding_reasons': dict(reasons),
        'selected_identity_counts': {item: len(ids) for item, ids in selected.items()},
        'selected_observation_digests': {item: sorted(ids) for item, ids in digests.items()},
        'selection': ('common exact opaque header + method/route + server role + service identity; '
                      'descendants only from genuine source-local trace/span IDs'),
        'includes_descendants': include_descendants, 'clock_gate': False,
        'outcomes_used': False, 'ids_rewritten': False,
    }


def supplied_entry_roles(store, roots, entry_services, untyped_components):
    """Legacy raw-export role overlays remain possible only for genuine exact IDs."""
    result = {}
    for root in roots:
        if (root.get('server_role_basis') != 'declared_untyped_receiver'
                or root.get('service') not in entry_services
                or not root.get('genuine_ancestry_identity')):
            continue
        key = (root['source'], root['trace_id'], root['span_id'])
        result[key] = {
            'source': root['source'], 'trace_id': root['trace_id'], 'span_id': root['span_id'],
            'service': root['service'], 'request_id': root['request_id'],
            'method': root['method'], 'path': root['path'], 'supplied_kind': 'SPAN_KIND_SERVER',
            'observation_digest': root['observation_digest'],
            'rule': 'unique common-v5 observation; declared untyped receiver; genuine exact IDs',
        }
    return result
