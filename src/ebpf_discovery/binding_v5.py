"""Endpoint rebinding from common graph-v5 observation locators."""
from __future__ import annotations

from .binding_v4 import _path
from .selection_v4 import method_path


def endpoint_alias_evidence(store, roots, step, entry_service, endpoints):
    expected = (str(step.get('method') or '').upper(), _path(step.get('path')))
    endpoint_ids, evidence = set(), []
    for root in roots:
        if (root.get('binding_reason') != 'unique_observation_entry'
                or root.get('service') != entry_service
                or (str(root.get('method') or '').upper(), _path(root.get('path'))) != expected):
            continue
        digest = root.get('observation_digest')
        row = store.observation_v5(digest) if digest and hasattr(store, 'observation_v5') else None
        if row is None or row.get('service') != entry_service or row.get('attribute_conflicts'):
            continue
        observed = method_path(row)
        if (str(observed[0] or '').upper(), observed[1]) != expected:
            continue
        matched = sorted({endpoint['id'] for endpoint in endpoints
            if endpoint.get('entry_service') == entry_service
            and (str(endpoint.get('method') or '').upper(), _path(endpoint.get('path'))) == expected})
        if not matched:
            continue
        endpoint_ids.update(matched)
        evidence.append({
            'basis': 'common_v5_observation_locator_entry_endpoint',
            'expected_step': {'method': expected[0], 'path': expected[1]},
            'entry_service': entry_service, 'endpoint_ids': matched,
            'observation_digest': digest,
            'observation_provenance': row.get('_observation_provenance', []),
            'genuine_ancestry_identity': root.get('genuine_ancestry_identity', False),
            'ids_rewritten': False,
        })
    return {'endpoint_ids': sorted(endpoint_ids), 'evidence': evidence,
            'basis': 'common v5 retained observation locators; no global alias or ancestry requirement'}
