"""Collector-true graph-v5 toolchain selection over the v4 scientific pipeline."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from .toolchain_v4 import Toolchain as ToolchainV4


PROTOCOL_VERSION = 'graph-v5'
PINS = {
    'Procrustes': '9648ae3fe9ef24725e665d008c79d0681ce40f85',
    'Bering': '66ca3af1fe581839e525fb9cc5600a1edd6ca8fb',
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
        from .supplied_alias_v5 import load, load_admission
        alias_path = Path(ctx.out) / "runtime-identity-v5" / "supplied-service-aliases-training.json"
        if not alias_path.is_file():
            raise ValueError("graph-v5 training prefix lacks supplied logical alias table")
        self.supplied_alias_path = alias_path
        self.supplied_alias_table = load(alias_path, Path(ctx.out))
        self.supplied_alias_admission_path = (
            Path(ctx.out) / 'runtime-identity-v5' /
            'supplied-service-alias-admission-training.json')
        if not self.supplied_alias_admission_path.is_file():
            raise ValueError('graph-v5 training prefix lacks supplied logical alias admission')
        self.supplied_alias_admission = load_admission(
            self.supplied_alias_admission_path, Path(ctx.out), self.supplied_alias_table)
        kwargs.setdefault('tool_pins', PINS)
        super().__init__(ctx, system, store, declaration, **kwargs)
        if self.store is not None and hasattr(self.store, 'db'):
            from .supplied_alias_v5 import admission_core, admit_observed
            recomputed = admit_observed(
                self.store, self.supplied_alias_table,
                expected_source_prefix='ebpf-' + self.collector_provenance['collector'])
            if admission_core(recomputed) != admission_core(self.supplied_alias_admission):
                raise ValueError('frozen supplied logical alias admission does not revalidate')
            if not hasattr(self.store, 'verify_supplied_logical_aliases'):
                raise ValueError('graph-v5 Store cannot verify supplied logical projections')
            self.supplied_alias_projection_verification = (
                self.store.verify_supplied_logical_aliases(self.supplied_alias_admission))
        else:
            self.supplied_alias_projection_verification = {
                'logical_projection_verified': False,
                'reason': 'observation_store_unavailable'}

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
                'bering_profile': 'ebpf-otlp',
                'supplied_logical_aliases': {
                    'path': self.supplied_alias_path.relative_to(self.ctx.out).as_posix(),
                    'origin': 'supplied_deployment_inventory_alias',
                    'same_table_all_sources_and_direct_baseline': True,
                    'admission_path': self.supplied_alias_admission_path.relative_to(
                        self.ctx.out).as_posix(),
                    'projection_verification': self.supplied_alias_projection_verification,
                    'physical_identity_inferred': False}}

    def discover(self, input_path, folder, overlay=None, prefix='model'):
        """Keep exact Bering output and bind only a copied semantic presentation."""
        raw_model, raw_quality = super().discover(input_path, folder, overlay, prefix)
        model_path = Path(folder) / f"{prefix}.json"
        quality_path = Path(folder) / f"{prefix}.signal-quality.json"
        raw_model_path = Path(folder) / f"{prefix}.bering-raw.json"
        raw_quality_path = Path(folder) / f"{prefix}.bering-raw.signal-quality.json"
        shutil.copyfile(model_path, raw_model_path)
        shutil.copyfile(quality_path, raw_quality_path)
        from .runtime import write_json
        from .supplied_alias_v5 import semantic_view
        model, quality, proof = semantic_view(
            raw_model, raw_quality, self.supplied_alias_table,
            self.supplied_alias_admission['aliases'])
        proof.update({
            'table_path': self.supplied_alias_path.relative_to(self.ctx.out).as_posix(),
            'table_sha256': hashlib.sha256(self.supplied_alias_path.read_bytes()).hexdigest(),
            'raw_model_path': raw_model_path.name,
            'raw_model_sha256': hashlib.sha256(raw_model_path.read_bytes()).hexdigest(),
            'raw_quality_path': raw_quality_path.name,
            'raw_quality_sha256': hashlib.sha256(raw_quality_path.read_bytes()).hexdigest(),
        })
        write_json(model_path, model)
        write_json(quality_path, quality)
        write_json(Path(folder) / f"{prefix}.supplied-aliases.json", proof)
        return model, quality

    def binding_uncertainties(self, model, quality):
        collisions = quality.get('supplied_logical_alias_uncertainty') or []
        return ([{'reason': 'supplied_logical_alias_metadata_collision',
                  'logical_services': sorted({row['logical_service'] for row in collisions}),
                  'variants_retained': True, 'binding_suppressed': True}]
                if collisions else [])

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
