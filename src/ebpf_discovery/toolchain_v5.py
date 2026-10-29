"""Collector-true graph-v5 toolchain selection over the v4 scientific pipeline."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .toolchain_v4 import Toolchain as ToolchainV4


PROTOCOL_VERSION = 'graph-v5'
PINS = {
    'Procrustes': 'f8d322bbea376d55c22d4c4f2d9fed257cc09f9f',
    'Bering': '75fe863c014388d525e2912a76be156fb3e5f037',
    'Sheaft': '686a602f4e7b71f3612f1810885e29dd66c8733a',
}
_COLLECTOR = re.compile(r'[a-z0-9][a-z0-9._-]{0,63}')


def collector_provenance(root: Path, status: dict | None = None) -> dict:
    """Validate the declared collector against retained runtime provenance."""
    root = Path(root)
    status = status if status is not None else json.loads((root/'status.json').read_text(encoding='utf-8'))
    if status.get('protocol_version') != PROTOCOL_VERSION:
        raise ValueError('generic collector toolchain requires status.protocol_version=graph-v5')
    declared = status.get('collector')
    if not isinstance(declared, str) or not _COLLECTOR.fullmatch(declared):
        raise ValueError('graph-v5 status lacks a valid normalized collector')
    path = root/'observations'/'collector.json'
    if not path.is_file():
        raise ValueError('graph-v5 collector provenance is missing')
    retained = json.loads(path.read_text(encoding='utf-8'))
    if retained.get('collector') != declared:
        raise ValueError('status collector differs from observations/collector.json')
    return {
        'protocol_version': PROTOCOL_VERSION,
        'collector': declared,
        'source_domain': retained.get('source_domain'),
        'collector_schema': retained.get('schema'),
        'collector_file': 'observations/collector.json',
    }


class Toolchain(ToolchainV4):
    def __init__(self, ctx, system, store, declaration, *, collector=None, **kwargs):
        provenance = collector_provenance(ctx.out)
        if collector is not None and collector != provenance['collector']:
            raise ValueError('requested collector differs from hash-bound collector provenance')
        self.collector_provenance = provenance
        kwargs.setdefault('tool_pins', PINS)
        super().__init__(ctx, system, store, declaration, **kwargs)

    def ebpf_collection_args(self):
        return ['--collection-source', 'ebpf-otlp',
                '--source-domain', self.system+'-deployment']

    def collector_static_input(self):
        return {**self.collector_provenance,
                'study_provenance_only': True,
                'product_profile_contains_collector_identity': False,
                'logical_source_id': 'ebpf',
                'logical_source_domain': self.system+'-deployment',
                'procrustes_profile': 'ebpf-otlp',
                'bering_profile': 'ebpf-otlp'}

    def bering_source_profile(self):
        return {'source_id': 'ebpf', 'input_type': 'ebpf-otlp'}

    def select_entry_evidence(self, plans, contract, source, untyped):
        from .selection_v5 import select_planned
        from .selection_v4 import select_planned as select_planned_v4
        selected, evidence = select_planned(
            self.store, plans, contract, source, untyped, include_descendants=False)
        legacy_selected, legacy_evidence = select_planned_v4(
            self.store, plans, contract, source, untyped, include_descendants=False)
        evidence['legacy_v4_exact_selector'] = {
            'evidence': legacy_evidence,
            'selected_identity_counts': {key: len(value)
                                         for key, value in legacy_selected.items()},
            'paired_diagnostic_only': True,
        }
        return selected, evidence

    def endpoint_entry_evidence(self, roots, step, entry, endpoints):
        from .binding_v5 import endpoint_alias_evidence
        return endpoint_alias_evidence(self.store, roots, step, entry, endpoints)

    def supplied_entry_role_evidence(self, roots, entry_services, untyped_components):
        from .selection_v5 import supplied_entry_roles
        return supplied_entry_roles(self.store, roots, entry_services, untyped_components)
