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


def context_edge_union(original, joint):
    """Preserve the strict view; copy only additional observed SERVER edges."""
    result = deepcopy(original)
    services = {item['id'] for item in original['services']}
    existing = {item['id']: item for item in original['edges']}
    added, conflicts, skipped = [], [], []
    semantic = ('from', 'to', 'kind', 'blocking', 'identity')
    for edge in joint['edges']:
        previous = existing.get(edge['id'])
        if previous is not None:
            if any(previous.get(key) != edge.get(key) for key in semantic):
                conflicts.append(edge['id'])
            continue  # Descriptive statistics stay in their two original views.
        if (edge.get('identity') or {}).get('span_kind') != 'server':
            skipped.append({'id': edge['id'], 'reason': 'not_an_actual_server_child_edge'})
        elif edge['from'] not in services or edge['to'] not in services:
            skipped.append({'id': edge['id'], 'reason': 'endpoint_service_not_in_original_view'})
        else:
            result['edges'].append(deepcopy(edge))
            added.append(edge['id'])
    return result, {'added_edge_ids': added, 'semantic_identity_conflicts': conflicts,
                    'skipped_joint_edges': skipped,
                    'original_services_endpoints_and_metadata_unchanged': True,
                    'all_existing_edge_fields_unchanged': True,
                    'new_edges_copied_from_actual_joint_bering_view': True,
                    'contract_inferred_edges': False, 'physical_identity_inferred': False,
                    'union_is_a_bering_emitted_snapshot': False}


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
                'paired_context_baseline': 'observed_server_edge_union_v1',
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

    def operation_model(self, input_path, folder, overlay_path, model, quality, source_folder, *,
                        observation_derivation=None):
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
        if observation_derivation is not None:
            files['observed_model'] = Path(observation_derivation['model']['path'])
            files['observation_derivation'] = Path(observation_derivation['proof']['path'])
        proof = {
            'origin': 'provided_metadata_after_verified_semantic_view',
            'files': {key: {'path': str(path),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                      for key, path in files.items()},
            'supplied': overlay, 'new_nodes_edges_or_endpoints': False,
            'graph_structure_and_observed_edge_fields_unchanged': True,
            'entity_ids_unchanged': True,
            'final_model_is_a_bering_emitted_snapshot': False,
            'source_signal_quality_unchanged': True,
            'same_information_all_sources_and_direct_baseline': True}
        if observation_derivation is not None:
            proof.update(observed_graph_origin='paired_context_edge_union',
                         source_signal_quality_scope='base entities and database aliases; added edge evidence is in the actual joint quality',
                         observation_derivation=observation_derivation)
        write_json(folder/'provided-metadata-attachment.json', proof)
        return attached, quality

    def forecast(self, plans):
        results = super().forecast(plans)
        self.forecast_context_baseline(results)
        return results

    def forecast_context_baseline(self, original_results):
        """A paired forecast in the same pre-target phase; original arms stay intact."""
        from .bering_v4 import replay
        from .runtime import write_json
        from .supplied_alias_v5 import semantic_view
        baseline = self.root/'context-baseline'
        baseline.mkdir(parents=True, exist_ok=True)
        predictions, variants = {}, {}
        def reference(path):
            return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        for variant in ('raw', 'network_scope'):
            predictions[variant] = {}
            out = baseline/variant
            out.mkdir(parents=True, exist_ok=True)
            shared = self.root/'discovery'/'combined'/variant
            input_path, manifest = self.input_manifests['combined', variant]
            counts = {source: self.input_manifests[source, variant][1]['observations']
                      for source in ('ebpf', 'native')}
            provenance = {'input_manifest': reference(input_path), 'source_observations': counts,
                          'original_forecasts': reference(self.root/'forecasts.json')}
            if not all(counts.values()):
                predictions[variant] = deepcopy(original_results['combined'][variant])
                provenance.update(status='reuse_single_source_equivalence',
                                  extra_bering_or_sheaft_executed=False)
                variants[variant] = provenance
                write_json(out/'provenance.json', provenance)
                continue
            original_path = shared/'observed.json'
            original = json.loads(original_path.read_text(encoding='utf-8'))
            quality = json.loads((shared/'observed.signal-quality.json').read_text(encoding='utf-8'))
            joint_folder = out/'joint'
            raw_joint, raw_quality = replay(
                self.bin/'bering', manifest, joint_folder, self.system+'-deployment',
                prefix='observed', publication_mode=self.publication_mode,
                source_profile=self.bering_source_profile(), joint_otlp=True)
            joint, joint_quality, alias_proof = semantic_view(
                raw_joint, raw_quality, self.supplied_alias_table,
                self.supplied_alias_admission['aliases'])
            alias_proof.update(table_path=str(self.supplied_alias_path),
                               table_sha256=reference(self.supplied_alias_path)['sha256'],
                               raw_model_path='observed.json',
                               raw_model_sha256=reference(joint_folder/'observed.json')['sha256'],
                               raw_quality_path='observed.signal-quality.json',
                               raw_quality_sha256=reference(joint_folder/'observed.signal-quality.json')['sha256'])
            write_json(joint_folder/'canonical.json', joint)
            write_json(joint_folder/'canonical.signal-quality.json', joint_quality)
            write_json(joint_folder/'supplied-aliases.json', alias_proof)
            model, union = context_edge_union(original, joint)
            write_json(out/'union-model.json', model)
            union['joint_alias_metadata_collisions'] = alias_proof['metadata_collisions']
            union['files'] = {
                'base_model': reference(original_path),
                'base_raw_model': reference(shared/'observed.bering-raw.json'),
                'base_snapshot': reference(shared/'observed.snapshot.json'),
                'base_quality': reference(shared/'observed.signal-quality.json'),
                'base_alias_projection': reference(shared/'observed.supplied-aliases.json'),
                'joint_raw_model': reference(joint_folder/'observed.json'),
                'joint_snapshot': reference(joint_folder/'observed.snapshot.json'),
                'joint_quality': reference(joint_folder/'observed.signal-quality.json'),
                'joint_model': reference(joint_folder/'canonical.json'),
                'joint_canonical_quality': reference(joint_folder/'canonical.signal-quality.json'),
                'joint_alias_projection': reference(joint_folder/'supplied-aliases.json'),
                'joint_replay': reference(joint_folder/'observed-runtime/replay-command.json'),
                'joint_config': reference(joint_folder/'observed-runtime/serve.yaml'),
                'joint_accepted_sequence': reference(joint_folder/'observed-runtime/accepted-request-sequence.jsonl'),
                'union_model': reference(out/'union-model.json'),
                'input_manifest': reference(input_path),
                'static_inputs': reference(self.root/'static-inputs.json'),
                'alias_table': reference(self.supplied_alias_path),
                'alias_admission': reference(self.supplied_alias_admission_path)}
            union['configured_tool_pins'] = self.tool_pins
            union['quality_scope'] = ('Base quality remains unchanged for original entities and DB aliases; '
                                      'added SERVER edges have actual joint-view evidence, not invented aggregate quality.')
            write_json(out/'union-proof.json', union)
            derivation = {'model': reference(out/'union-model.json'),
                          'proof': reference(out/'union-proof.json')}
            provenance.update(union=derivation, extra_bering_executed=True)
            if union['semantic_identity_conflicts'] or union['joint_alias_metadata_collisions']:
                for name in self.declaration.CONTRACTS:
                    predictions[variant][name] = {
                        'prediction': None, 'interval': [0, 1], 'by_state': {}, 'available': False,
                        'reason': 'context_view_identity_or_alias_conflict',
                        'semantic_identity_conflicts': union['semantic_identity_conflicts'],
                        'metadata_collisions': union['joint_alias_metadata_collisions']}
                provenance.update(status='unknown_view_alignment', extra_sheaft_executed=False)
            elif not union['added_edge_ids']:
                predictions[variant] = deepcopy(original_results['combined'][variant])
                provenance.update(status='reuse_unchanged_union', extra_sheaft_executed=False)
            else:
                for name, contract in self.declaration.CONTRACTS.items():
                    predictions[variant][name] = self.forecast_operation(
                        'combined', variant, name, contract, input_path, manifest, shared,
                        model, quality, out/'operations'/name, observation_derivation=derivation)
                provenance.update(status='forecast_from_observed_context_union',
                                  simulation_commands_present=len(list((out/'operations').glob('*/simulation.command.json'))))
            variants[variant] = provenance
            write_json(out/'provenance.json', provenance)
        write_json(baseline/'forecasts.json', predictions)
        write_json(baseline/'manifest.json', {
            'policy_id': 'observed_server_edge_union_v1',
            'policy': 'original graph plus additional actual joint-view SERVER edges',
            'variants': variants, 'same_policy_all_collectors_and_scenarios': True,
            'requires_capture_freeze_before_targets': True,
            'post_target_diagnostic_is_not_a_primary_forecast': True})

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
