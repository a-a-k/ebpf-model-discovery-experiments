"""Collector-true graph-v5 toolchain selection over the v4 scientific pipeline."""
from __future__ import annotations

from copy import deepcopy
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


def attach_operation_metadata(model, overlay):
    """The controller's restricted Bering overlay, applied to existing logical IDs."""
    if set(overlay) - {'name', 'services', 'endpoints'}:
        raise ValueError('operation metadata cannot change graph topology')
    result = deepcopy(model)
    services = {item['id']: item for item in result['services']}
    endpoints = {item['id']: item for item in result['endpoints']}
    for supplied in overlay.get('services') or []:
        if (set(supplied) - {'id', 'replicas', 'failure_eligible', 'placements', 'attributes'}
                or supplied['id'] not in services):
            raise ValueError('operation metadata requires an existing service and supported fields')
        service = services[supplied['id']]
        if 'replicas' in supplied:
            service['replicas'] = supplied['replicas']
        for key in ('failure_eligible', 'placements'):
            if key in supplied:
                service.setdefault('metadata', {})[key] = deepcopy(supplied[key])
        # Bering's procrustes attributes annotate snapshot records only. The
        # original supplied overlay and attachment evidence retain them.
    for supplied in overlay.get('endpoints') or []:
        if (set(supplied) - {'id', 'predicate_ref', 'semantics'}
                or supplied['id'] not in endpoints
                or set(supplied.get('semantics') or {}) - {'predicate_mode', 'source'}):
            raise ValueError('operation metadata requires an existing endpoint and supported fields')
        endpoint = endpoints[supplied['id']]
        if 'predicate_ref' in supplied:
            endpoint['success_predicate_ref'] = supplied['predicate_ref']
        if supplied.get('semantics'):
            endpoint.setdefault('metadata', {}).setdefault('semantics', {}).update(deepcopy(supplied['semantics']))
    return result


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

    def operation_model(self, input_path, folder, overlay_path, model, quality, source_folder):
        from .runtime import write_json
        overlay = json.loads(overlay_path.read_text(encoding='utf-8'))
        attached = attach_operation_metadata(model, overlay)
        write_json(folder/'model.json', attached)
        write_json(folder/'model.signal-quality.json', quality)
        self.command('bering', ['validate', '--input', folder/'model.json'],
                     folder, 'provided-metadata-validation')
        files = {'observed_model': source_folder/'observed.json',
                 'raw_bering_model': source_folder/'observed.bering-raw.json',
                 'raw_bering_snapshot': source_folder/'observed.snapshot.json',
                 'semantic_projection': source_folder/'observed.supplied-aliases.json',
                 'provided_overlay': overlay_path, 'simulator_model': folder/'model.json'}
        write_json(folder/'provided-metadata-attachment.json', {
            'origin': 'provided_metadata_after_verified_semantic_view',
            'files': {key: {'path': str(path),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                      for key, path in files.items()},
            'supplied': overlay, 'new_nodes_edges_or_endpoints': False,
            'graph_structure_and_observed_edge_fields_unchanged': True,
            'entity_ids_unchanged': True,
            'final_model_is_a_bering_emitted_snapshot': False,
            'source_signal_quality_unchanged': True,
            'same_information_all_sources_and_direct_baseline': True})
        return attached, quality

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
