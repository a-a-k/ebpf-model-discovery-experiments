"""Actual source-pinned Procrustes/Bering/Sheaft orchestration.

No evaluator response or outcome rate is accepted by this module.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
import hashlib
import importlib
import json
import os
import re
from pathlib import Path
import time
from urllib.parse import urlsplit

import yaml

from .runtime import write_json
from .selection_v4 import canonical_route, select_planned, supplied_entry_roles
from .raw_v4 import export_selection
from .bering_v4 import replay
from .binding_v4 import endpoint_alias_evidence, matches_call_hint

ORIGINAL_PINS = {
    'Procrustes': '39f76000f8a39c971155e08ebffde829b525911b',
    'Bering': 'dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3',
    'Sheaft': '686a602f4e7b71f3612f1810885e29dd66c8733a',
}
BERING_120_PINS = {**ORIGINAL_PINS, 'Bering': '6f806428509a640a6419058c2ad845ed44db7512'}
PINS = dict(BERING_120_PINS)
STATE_WEIGHTS = {'11': .5, '10': .25, '01': .125, '00': .125}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def aliases(value):
    return [value] if isinstance(value, str) else list(value or [])


def unique_service(model, names):
    found = [s['id'] for s in model['services'] if s['id'] in aliases(names)]
    return found[0] if len(found) == 1 else None


def evidence_index(quality):
    return {(r['entity_type'], r['entity_id']): r['evidence']
            for r in quality.get('observation_evidence', [])}


def db_aliases(model, quality):
    evidence = evidence_index(quality)
    result = {}
    for service in model['services']:
        ev = evidence.get(('service', service['id']), {})
        result[service['id']] = ([ev['database']] if ev.get('database') else [])+ev.get('database_aliases', [])
    for edge in model['edges']:
        result.setdefault(edge['to'], []).extend(
            evidence.get(('edge', edge['id']), {}).get('database_aliases', []))
    return result


def unique_path(model, start, end, *, intermediates=None, call_hint=None, permitted_services=(), provenance=None):
    """A unique observed directed service path; keep every typed edge on its hops.

    Parallel operation identities on one channel are not alternate service paths.
    A direct observed channel takes precedence over its declared transparent-proxy
    representation under this protocol's fixed-fulfilled proxy condition. Without
    a direct call, more than one allowed service path remains ambiguous.
    """
    adjacency = defaultdict(set)
    by_pair = defaultdict(list)
    for edge in model['edges']:
        if edge['kind'] == 'sync':
            if call_hint and edge['to'] == end:
                matched, _ = matches_call_hint(edge.get('identity') or {}, call_hint,
                                               permitted_services=tuple(permitted_services))
                if not matched:
                    continue
            adjacency[edge['from']].add(edge['to'])
            by_pair[edge['from'], edge['to']].append(edge['id'])
    if by_pair.get((start, end)):
        if provenance is not None:
            provenance.update(policy='direct observed channel before declared transparent-proxy representation',
                basis='declared proxies remain fulfilled in all modeled node/whole-DB interventions',
                allowed_proxy_services=sorted(intermediates or []),
                other_observed_proxy_edge_ids=sorted(e['id'] for e in model['edges']
                    if e['from'] in (intermediates or ()) or e['to'] in (intermediates or ())))
        return sorted(by_pair[start, end])
    found = []
    queue = deque([(start, [start])])
    while queue:
        current, path = queue.popleft()
        if current == end:
            found.append(path)
            if len(found) > 1:
                return None
            continue
        for child in sorted(adjacency[current]):
            if child not in path and (intermediates is None or child == end or child in intermediates):
                queue.append((child, path+[child]))
    if len(found) != 1:
        return None
    path = found[0]
    if provenance is not None:
        provenance.update(policy='unique observed service path through declared proxies',
                          service_path=path, allowed_proxy_services=sorted(intermediates or []))
    return sorted({eid for a, b in zip(path, path[1:]) for eid in by_pair[a, b]})


def resolve_contract(model, quality, contract, proxy_aliases=(), *, entry_proofs=None, database_fault_group=None):
    """Compile supplied obligations against recovered structure, never add structure."""
    required, targets, resolved, unknown, assumed_database = set(), set(), [], [], []
    databases = db_aliases(model, quality)
    group = database_fault_group or {}
    group_nodes = set(group.get('matched_observed_nodes', []))
    entry = unique_service(model, contract['entry_services'])
    if not entry:
        unknown.append({'reason': 'entry_service_missing_or_ambiguous'})
    for call in contract['required_calls']:
        caller = unique_service(model, call['caller'])
        grouped_callees, path_evidence = [], {}
        if 'db_system' in call:
            candidates = []
            for edge in model['edges']:
                if edge['from'] != caller or edge['kind'] != 'sync':
                    continue
                if any(d.get('system') == call['db_system'] for d in databases.get(edge['to'], [])):
                    candidates.append(edge['to'])
            candidates = sorted(set(candidates))
            callee = candidates[0] if len(candidates) == 1 else None
            if len(candidates) > 1 and set(candidates) <= group_nodes:
                grouped_callees = candidates
        else:
            callee = unique_service(model, call['callee'])
        path = unique_path(model, caller, callee, intermediates=set(proxy_aliases),
                           call_hint=call.get('operation_hint') if 'db_system' not in call else None,
                           permitted_services=aliases(call.get('callee')),
                           provenance=path_evidence) if caller and callee else None
        if grouped_callees:
            channels = [unique_path(model, caller, node) for node in grouped_callees]
            path = sorted({edge for channel in channels for edge in channel}) if all(channels) else None
            path_evidence = {'policy': 'all observed aliases in the same explicitly mapped whole-endpoint fault group',
                'separate_node_ids': grouped_callees, 'physical_identity_inferred': False,
                'fault_scope': group.get('fault_scope'), 'mapping_basis': group.get('mapping_basis'),
                'validity': 'coextensive whole-endpoint intervention; no independent alias/command failures'}
        if 'db_system' in call and caller and entry and reachable(model, entry, caller) and path is None:
            assumed_database.append({'obligation': call, 'resolved_caller': caller,
                'resolved_callee': callee, 'reason': 'database_channel_missing_or_ambiguous',
                'assumption': 'database requirement fulfilled under primary replica-only conditional model',
                'basis': 'declared fixed condition; not inferred from process readiness or observed outcomes',
                'recovered_dependency': False})
            targets.add(caller)
            continue
        if path is None:
            unknown.append({'reason': 'required_call_missing_or_ambiguous', 'obligation': call,
                            'resolved_caller': caller, 'resolved_callee': callee})
            continue
        if entry and not reachable(model, entry, caller):
            unknown.append({'reason': 'required_caller_not_uniquely_reachable', 'obligation': call})
            continue
        required.update(path)
        targets.update([caller, *(grouped_callees or [callee])])
        resolved.append({'obligation': call, 'caller': caller, 'callee': callee,
                         'callee_nodes': grouped_callees or [callee], 'path_resolution': path_evidence,
                         'required_edge_ids': path,
                         'call_hint_evidence': [
                             {'edge_id': edge['id'], 'observed_identity': edge.get('identity'),
                              'basis': matches_call_hint(edge.get('identity') or {}, call['operation_hint'],
                                  permitted_services=tuple(aliases(call.get('callee'))))[1]}
                             for edge in model['edges'] if edge['id'] in path and edge['to'] == callee
                             and 'db_system' not in call and call.get('operation_hint')],
                         **({'compiled_semantics': 'mandatory caller-to-database-endpoint channel',
                             'basis': 'all typed edges on this channel share endpoint liveness; live-edge probability is one',
                             'validity': 'node/whole-endpoint fail-stop interventions only; no individual command or edge failures',
                             'command_level_necessity_inferred': False}
                            if 'db_system' in call else {})})
    endpoints, endpoint_bindings = [], []
    for index, step in enumerate(contract['steps']):
        candidates = [e for e in model['endpoints'] if e['entry_service'] == entry
                      and e.get('method') == step['method']
                      and canonical_route(e.get('path', '')) == canonical_route(step['path'])]
        proof = (entry_proofs or {}).get(index, {})
        proven = [e['id'] for e in model['endpoints'] if e['id'] in proof.get('endpoint_ids', [])
                  and e['entry_service'] == entry and e.get('method') == step['method']]
        if proven:
            endpoints.extend(proven)
            endpoint_bindings.append({'step': step, 'endpoint_ids': proven, 'proof': proof})
        elif len(candidates) != 1:
            unknown.append({'reason': 'entry_endpoint_missing_or_ambiguous', 'step': step,
                            'candidates': [e['id'] for e in candidates]})
        else:
            endpoints.append(candidates[0]['id'])
            endpoint_bindings.append({'step': step, 'endpoint_ids': [candidates[0]['id']],
                                      'basis': 'unique observed entry method and canonical route'})
    db_fault_unknown = [item for item in assumed_database
                       if item['obligation']['db_system'] == group.get('declared_system')]
    for item in resolved:
        if (item['obligation'].get('db_system') == group.get('declared_system')
                and not set(item['callee_nodes']) <= group_nodes):
            db_fault_unknown.append({'obligation': item['obligation'],
                'reason': 'required_database_endpoint_not_attributed_to_selected_fault_group',
                'observed_nodes': item['callee_nodes']})
    return {'entry_service': entry, 'required_edges': sorted(required),
            'mandatory_targets': sorted(targets-{entry}), 'endpoints': sorted(set(endpoints)),
            'resolved_calls': resolved, 'endpoint_bindings': endpoint_bindings,
            'unknown': unknown, 'available': not unknown,
            'assumed_satisfied_database_requirements': assumed_database,
            'all_required_database_channels_observed': not assumed_database and not any(
                'db_system' in item.get('obligation', {}) for item in unknown),
            'database_fault_prediction_available': bool(group_nodes) and not db_fault_unknown,
            'database_fault_unknown': db_fault_unknown,
            'database_fault_fixed_other_requirements': [item for item in assumed_database
                if item['obligation']['db_system'] != group.get('declared_system')],
            'primary_scope': 'topology-only replica intervention conditional on nonintervened requirements being fulfilled'}


def fault_inputs(controlled, database_nodes=()):
    profiles = {}
    for state in ('10', '01', '00'):
        if controlled:
            profiles['state-'+state] = {'faults': [
            {'type': 'correlated_failure_domain', 'selector': {
                'service_ids': [controlled], 'placement_labels': {'controlled_replica': slot}}}
            for slot, bit in zip(('a', 'b'), state) if bit == '0']}
    if database_nodes:
        profiles['db-down'] = {'faults': [{'type': 'correlated_failure_domain',
                                        'only_failure_eligible': False,
                                        'selector': {'service_ids': sorted(database_nodes)}}]}
    return {'schema_version': '1.0', 'profiles': profiles}


def resolve_entry_representations(model, quality, contract, proxy_aliases, *, proof_builder,
                                  identity_groups=(), database_fault_group=None, controlled=None):
    """Interpret independently proven entry names without rewriting Bering's graph."""
    observed = {service['id'] for service in model['services']}
    present = [name for name in aliases(contract['entry_services']) if name in observed]
    groups = [group for group in identity_groups if set(present) <= set(group['aliases'])]
    if len(present) < 2 or len(groups) != 1:
        entry = unique_service(model, contract['entry_services'])
        return resolve_contract(model, quality, contract, proxy_aliases,
            entry_proofs=proof_builder(entry) if entry else {}, database_fault_group=database_fault_group)
    group, candidates = groups[0], []
    for entry in present:  # Explicit contract order, independent of outcomes.
        candidate_contract = deepcopy(contract)
        candidate_contract['entry_services'] = [entry]
        for call in candidate_contract['required_calls']:
            caller = set(aliases(call.get('caller')))
            if caller and caller <= set(group['aliases']) and caller & set(contract['entry_services']):
                call['caller'] = [entry]
        binding = resolve_contract(model, quality, candidate_contract, proxy_aliases,
            entry_proofs=proof_builder(entry), database_fault_group=database_fault_group)
        states = ({state: exact_graph_outcome(model, binding,
            [controlled] if controlled and state == '00' else []) for state in STATE_WEIGHTS}
            if binding['available'] else None)
        db_value = (exact_graph_outcome(model, binding, (database_fault_group or {}).get('matched_observed_nodes', []))
            if binding['available'] and binding['database_fault_prediction_available'] and not contract.get('conditional_db') else None)
        candidates.append({'entry': entry, 'binding': binding, 'exact_state_vector': states,
                           'exact_database_down': db_value})
    supported = [row for row in candidates if row['binding']['available']]
    same_states = len({json.dumps(row['exact_state_vector'], sort_keys=True) for row in supported}) <= 1
    known_db_values = {row['exact_database_down'] for row in supported if row['exact_database_down'] is not None}
    agreement = same_states and len(known_db_values) <= 1
    selected = supported[0] if supported and agreement else None
    result = deepcopy((selected or candidates[0])['binding'])
    if not selected:
        result['available'] = False
        result['unknown'].append({'reason': 'proven_entry_representations_unsupported_or_disagree'})
    elif any(row['exact_database_down'] is None for row in supported):
        result['database_fault_prediction_available'] = False
        result['database_fault_unknown'].append({'reason': 'database_prediction_not_supported_by_every_supported_entry_representation'})
    result['entry_identity_resolution'] = {
        'supplied_identity_group': group, 'candidates': candidates,
        'selection_rule': 'sole supported entry or declared order after full deterministic state-vector agreement',
        'selected_observed_entry': selected['entry'] if selected else None,
        'all_supported_state_vectors_agree': same_states,
        'known_database_predictions_agree': len(known_db_values) <= 1,
        'graph_modified': False, 'entry_failure_modeled': False,
        'semantic_basis': 'same provided container/listener identity; fixed-fulfilled entry; no controlled-service identity inference'}
    return result


def predicate_contract(model, binding, name):
    """Score supplied operation endpoints; retain ancillary graph endpoints unscored."""
    selected = set(binding['endpoints'])
    predicate = {key: binding[key] for key in ('entry_service', 'mandatory_targets', 'required_edges')}
    predicate.update(type='edge_aware', edge_modes=['sync'])
    definitions, weights = {name: predicate}, {}
    for endpoint in model['endpoints']:
        chosen = endpoint['id'] in selected
        weights[endpoint['id']] = 1 if chosen else 0
        if not chosen:
            reference = endpoint['success_predicate_ref']
            if reference == name:
                raise ValueError('Ancillary endpoint collides with the selected operation predicate')
            definitions[reference] = {
                'type': 'all_of', 'services': [endpoint['entry_service']],
                'description': 'Unscored entry-service liveness only; no business-operation success semantics supplied'}
    return {'schema_version': '1.1', 'predicates': definitions, 'endpoint_weights': weights}


def reachable(model, start, end):
    pending, seen = [start], set()
    adjacency = defaultdict(set)
    for edge in model['edges']:
        if edge['kind'] == 'sync':
            adjacency[edge['from']].add(edge['to'])
    while pending:
        current = pending.pop()
        if current == end:
            return True
        if current not in seen:
            seen.add(current)
            pending.extend(adjacency[current]-seen)
    return False


def exact_graph_outcome(model, binding, unavailable_services=()):
    """Exact connectivity law for the specified deterministic fail-stop state."""
    live = {s['id'] for s in model['services']} - set(unavailable_services)
    edges = {e['id']: e for e in model['edges'] if e['kind'] == 'sync'
             and e['from'] in live and e['to'] in live}
    visited, pending = set(), [binding['entry_service']]
    adjacency = defaultdict(set)
    for edge in edges.values():
        adjacency[edge['from']].add(edge['to'])
    while pending:
        node = pending.pop()
        if node in live and node not in visited:
            visited.add(node)
            pending.extend(adjacency[node] - visited)
    return int(binding['entry_service'] in visited
               and set(binding['mandatory_targets']) <= visited
               and all(eid in edges and edges[eid]['from'] in visited
                       for eid in binding['required_edges']))


class Toolchain:
    def __init__(self, ctx, system, store, declaration, *, tool_pins=None,
                 publication_mode='on_shutdown', native_jaeger_envelope='per_file'):
        self.ctx, self.system, self.store, self.declaration = ctx, system, store, declaration
        self.tool_pins = dict(PINS if tool_pins is None else tool_pins)
        self.publication_mode = publication_mode
        if native_jaeger_envelope not in ('per_file', 'per_trace'):
            raise ValueError('unsupported native Jaeger envelope granularity')
        self.native_jaeger_envelope = native_jaeger_envelope
        self.root = ctx.out/'toolchain'
        self.root.mkdir(exist_ok=True)
        self.bin = Path(os.environ.get('PBS_BIN', 'work/toolchain/bin')).resolve()
        self.inventory = json.loads((ctx.out/'deployment.json').read_text())

    def ebpf_collection_args(self):
        """Legacy v4 selection; v5 overrides this without relabeling v4 runs."""
        return ['--collection-source', 'ebpf-obi', '--source-domain', self.system+'-deployment']

    def collector_static_input(self):
        return None

    def bering_source_profile(self):
        return None

    def select_entry_evidence(self, plans, contract, source, untyped):
        """Compatibility seam for protocol-specific observation selection."""
        return select_planned(self.store, plans, contract, source, untyped,
                              include_descendants=False)

    def endpoint_entry_evidence(self, roots, step, entry, endpoints):
        """Compatibility seam for protocol-specific retained entry binding."""
        return endpoint_alias_evidence(self.store, roots, step, entry, endpoints)

    def supplied_entry_role_evidence(self, roots, entry_services, untyped_components):
        return supplied_entry_roles(self.store, roots, entry_services, untyped_components)

    def binding_uncertainties(self, model, quality):
        """Protocol-specific retained uncertainty; legacy graphs add none."""
        return []

    def apply_binding_uncertainties(self, binding, model, quality):
        additional = self.binding_uncertainties(model, quality)
        if additional:
            binding['unknown'].extend(additional)
            binding['available'] = False
        return binding

    def command(self, tool, args, folder, name):
        started = time.time_ns()
        result = self.ctx.run([str(self.bin/tool), *map(str, args)], timeout=None, check=False)
        write_json(folder/(name+'.command.json'), dict(started_ns=started, ended_ns=time.time_ns(),
            argv=[tool, *map(str, args)], returncode=result.returncode,
            stdout=result.stdout, stderr=result.stderr))
        if result.returncode:
            raise RuntimeError(f'{tool} {name} failed: {result.stderr[-2500:]}')

    def preflight(self):
        self.entry_identity_groups = (self.declaration.entry_identity_groups(self.ctx.deployment_dir)
            if hasattr(self.declaration, 'entry_identity_groups') else [])
        candidates = [p for p in self.ctx.deployment_dir.rglob('*') if p.is_file()
                      and not any(part in ('source', 'upstream', '.git')
                                  for part in p.relative_to(self.ctx.deployment_dir).parts)]
        resolved = [p for p in candidates if p.name.startswith('runtime-resolved-node-')
                    and p.suffix in ('.yml', '.yaml')]
        sources = resolved or [p for p in candidates if p.name in
            ('compose.yml', 'compose.yaml', 'docker-compose.yml', 'docker-compose.yaml', 'node-a.yaml', 'node-b.yaml')]
        if not sources:
            raise RuntimeError('No rendered deployment manifests for Procrustes')
        args = [arg for i, path in enumerate(sorted(sources)) for arg in ('--source', f'deployment-{i}={path}')]
        self.preflight_reports = defaultdict(list)
        for name, contract in self.declaration.CONTRACTS.items():
            for i, step in enumerate(contract['steps']):
                entry = contract['entry_services'][0]
                # Alias alternatives are not separate required workloads.
                services = sorted({entry, *[aliases(c[key])[0] for c in contract['required_calls']
                                           for key in ('caller', 'callee') if c.get(key)]})
                targets = step.get('preflight_targets')
                if targets is None and len(contract['steps']) == 1:
                    targets = [service for service in services if service != entry]
                if not targets or not set(targets) <= set(services)-{entry}:
                    raise ValueError('Procrustes requires declared nonempty service targets for each HTTP step: '+name)
                goal = {'contract': {'name': 'io.mb3r.procrustes.goal', 'version': '0.1.0'},
                        'scope': {'namespaces': ['*'], 'services': services},
                        'operation': {'id': name+f'-step-{i}', 'entry_service': entry,
                                      'method': step['method'], 'path': step['path'],
                                      'mandatory_targets': sorted(set(targets))}}
                for source in ('native', 'ebpf'):
                    folder = self.root/'procrustes'/source/name/str(i)
                    folder.mkdir(parents=True, exist_ok=True)
                    write_json(folder/'goal.json', goal)
                    selection = self.ebpf_collection_args() if source == 'ebpf' else []
                    self.command('procrustes', ['analyze', *args, '--goal', folder/'goal.json',
                                               '--out-dir', folder, *selection], folder, 'preflight')
                    self.preflight_reports[source, name].append(folder/'report.json')
        static_inputs = {'deployment': self.inventory,
            'tool_pins': self.tool_pins, 'bering_publication_mode': self.publication_mode,
            'native_jaeger_envelope': self.native_jaeger_envelope,
            'contracts': self.declaration.CONTRACTS,
            'supplied_entry_identity_groups': self.entry_identity_groups,
            'procrustes_use': 'reports unchanged; only confirmed identity and replica facts attach to recovered nodes',
            'preflight_scope': 'one declared canonical name per alias group; all deployment namespaces',
            'scenario_limitation': 'custom workload driver is retained separately; no Tracetest scenario is fabricated to pass preflight',
            'supplied_placement_basis': 'rendered controlled-replica inventory, independently attributed',
            'network_scope_rule': 'one declared routed application address space on these two guests',
            'unmatched_inventory': 'retained here; never inserted into graph'}
        collector = self.collector_static_input()
        if collector is not None:
            static_inputs['collector'] = collector
        write_json(self.root/'static-inputs.json', static_inputs)

    def static_overlay(self, model, source, operation):
        """Consume confirmed Procrustes output without importing expected topology."""
        observed = {s['id'] for s in model['services']}
        by_id, evidence = defaultdict(dict), []
        for origin in (('native', 'ebpf') if source == 'combined' else (source,)):
            for path in self.preflight_reports[origin, operation]:
                report = json.loads(path.read_text(encoding='utf-8'))
                for service in report['services']:
                    if service['id'] not in observed or any(service[k]['status'] != 'CONFIRMED'
                                                         for k in ('identity', 'replicas')):
                        continue
                    replicas = int(service['replicas']['value'])
                    if replicas <= 0:
                        continue
                    value = {'id': service['id'], 'replicas': replicas,
                             'attributes': {'procrustes.workload': service.get('namespace', '')+'/'+service.get('workload', '')}}
                    by_id[service['id']][json.dumps(value, sort_keys=True)] = value
                    evidence.append({'report': str(path), 'id': service['id'],
                                     'identity': service['identity'], 'replicas': service['replicas']})
        return [next(iter(values.values())) for values in by_id.values() if len(values) == 1], evidence

    def prepare_inputs(self, plans):
        """Freeze source-global graph input; exact roots serve only separate proofs.

        One export per source/variant is shared by all operations and the combined
        arm. No request ancestry or supplied expected topology filters the graph.
        """
        started = time.time_ns()
        self.entry_evidence, self.input_manifests = {}, {}
        roles = {}
        untyped = getattr(self.declaration, 'UNTYPED_ENTRY_COMPONENTS', {})
        try:
            for name, contract in self.declaration.CONTRACTS.items():
                for source in ('ebpf', 'native'):
                    _, evidence = self.select_entry_evidence(plans, contract, source, untyped)
                    self.entry_evidence[source, name] = evidence
                    for identity, declaration in self.supplied_entry_role_evidence(
                            evidence['roots'], contract['entry_services'], untyped).items():
                        if identity in roles and roles[identity] != declaration:
                            raise ValueError('Conflicting supplied role declarations for one source identity')
                        roles[identity] = declaration
                pieces = [self.entry_evidence[source, name] for source in ('ebpf', 'native')]
                self.entry_evidence['combined', name] = {
                    'source': 'combined', 'roots': [root for piece in pieces for root in piece['roots']],
                    'binding_reasons': {key: value for piece in pieces for key, value in piece['binding_reasons'].items()},
                    'selection': 'union of source-local exact entry proofs; no cross-source causal join',
                    'includes_descendants': False, 'outcomes_used': False, 'clock_gate': False}
            service_projections = (self.store.service_projections(
                self.root/'inputs'/'runtime-identity-values.jsonl')
                if hasattr(self.store, 'service_projections') else None)
            try:
                for variant in ('raw', 'network_scope'):
                    for source in ('ebpf', 'native'):
                        folder = self.root/'inputs'/source/variant
                        folder.mkdir(parents=True, exist_ok=True)
                        manifest = export_selection(self.store, {source: None}, folder/'exports',
                            self.system+'-routed-network' if variant == 'network_scope' else None,
                            supplied_server_roles={key: value for key, value in roles.items() if key[0] == source},
                            native_jaeger_envelope=self.native_jaeger_envelope,
                            service_projections=service_projections)
                        manifest.update(graph_input='all source-separated frozen training-prefix observations',
                            exported_wire_bytes=(sum(Path(export['path']).stat().st_size
                                                     for export in manifest['exports'])
                                + sum(stream['wire_bytes']
                                      for stream in manifest.get('stream_exports', []))),
                            causal_execution_inferred=False,
                            ambient_preparation_and_oracle_traffic='retained if present in frozen source prefixes',
                            supplied_role_policy='union of exact declared entry roots across all operations')
                        path = folder/'observations.json'
                        write_json(path, manifest)
                        self.input_manifests[source, variant] = (path, manifest)
                    pieces = [self.input_manifests[source, variant] for source in ('ebpf', 'native')]
                    streamed = any(piece.get('stream_exports') for _, piece in pieces)
                    manifest = {'exports': ([] if streamed else
                                             [export for _, piece in pieces
                                              for export in piece['exports']]),
                        'stream_exports': [],
                        'observations': sum(piece['observations'] for _, piece in pieces),
                        'exported_wire_bytes': sum(piece['exported_wire_bytes'] for _, piece in pieces),
                        'additional_exported_wire_bytes': 0,
                        'native_jaeger_envelope': self.native_jaeger_envelope,
                        'graph_input': 'union of unchanged source-global exports; no cross-source causal join',
                        'source_manifests': [{'path': str(path), 'sha256': digest(path)} for path, _ in pieces],
                        'causal_execution_inferred': False}
                    if streamed:
                        # Preserve the historical combined replay order (all eBPF
                        # requests, then all native requests) without copying every
                        # large streamed request row into this manifest.
                        manifest['ordered_request_group_manifests'] = [
                            {'path': str(path.resolve()), 'bytes': path.stat().st_size,
                             'sha256': digest(path)} for path, _ in pieces]
                    path = self.root/'inputs'/'combined'/variant/'observations.json'
                    path.parent.mkdir(parents=True, exist_ok=True)
                    write_json(path, manifest)
                    self.input_manifests['combined', variant] = (path, manifest)
            finally:
                if hasattr(service_projections, 'close'):
                    service_projections.close()
        finally:
            write_json(self.root/'input-preparation-cost.json', {'started_ns': started,
                'ended_ns': time.time_ns(), 'completed': len(self.input_manifests) == 6,
                'scope': 'entry proofs, role union, frozen raw exports and combined references; shared across operations'})

    def discover(self, input_path, folder, overlay=None, prefix='model'):
        manifest = json.loads(input_path.read_text(encoding='utf-8'))
        return replay(self.bin/'bering', manifest, folder, self.system+'-deployment', overlay, prefix,
                      publication_mode=self.publication_mode,
                      source_profile=self.bering_source_profile())

    def operation_model(self, input_path, folder, overlay_path, model, quality, source_folder):
        return self.discover(input_path, folder, overlay_path)

    def database_nodes(self, model, quality):
        reference = self.inventory.get('database', {})
        extra = (self.declaration.database_inventory(self.ctx.deployment_dir)
                 if hasattr(self.declaration, 'database_inventory') else {})
        declared = getattr(self.declaration, 'SELECTED_DATABASE', {})
        otel_mapping = self.inventory.get('v4_contract', {}).get('catalog_database_mapping', {})
        system = (reference.get('system') or declared.get('db_system')
                  or otel_mapping.get('db_system') or extra.get('database_system'))
        endpoints = set()
        port = reference.get('port', reference.get('container_port'))
        if port:
            for key in ('ip', 'service', 'container', 'name', 'logical_identity'):
                address = reference.get(key)
                if address and '/' not in str(address):
                    endpoints.add((str(address), int(port)))
        if reference.get('transport_host') and reference.get('transport_port'):
            endpoints.add((str(reference['transport_host']), int(reference['transport_port'])))
        for alias in extra.get('database_fault_aliases', []):
            if isinstance(alias, dict) and alias.get('port'):
                address = alias.get('address', alias.get('host'))
                if address:
                    endpoints.add((str(address), int(alias['port'])))
        selected, witnesses = set(), []
        expected_scope = self.system+'-routed-network'
        for node, values in db_aliases(model, quality).items():
            for value in values:
                if (value.get('identity_kind') != 'logical_endpoint'
                        or value.get('system') != system
                        or value.get('network_scope') not in (None, '', expected_scope, 'declared:'+expected_scope)
                        or (value.get('address'), value.get('port')) not in endpoints):
                    continue
                selected.add(node)
                witnesses.append({'node': node, 'observed_alias': value})
        return sorted(selected), {
            'declared_system': system, 'declared_endpoints': [list(pair) for pair in sorted(endpoints)],
            'declared_network_scope': expected_scope, 'matched_observed_nodes': sorted(selected),
            'scope_representation_rule': 'exact declared: prefix is the Bering encoding of the supplied scope; original value retained',
            'witnesses': witnesses, 'physical_identity_inferred': False,
            'fault_scope': 'all namespaces of the stopped deployment endpoint',
            'mapping_basis': 'explicit deployment attribution of complete address/port pairs; no graph merge',
            'source_files': extra.get('source_files', []),
        }

    def forecast(self, plans):
        print(json.dumps({'toolchain_event': 'preflight_start', 'system': self.system}), flush=True)
        self.preflight()
        self.prepare_inputs(plans)
        results = {}
        for source in ('ebpf', 'native', 'combined'):
            results[source] = {}
            for variant in ('raw', 'network_scope'):
                results[source][variant] = {}
                input_path, manifest = self.input_manifests[source, variant]
                shared = self.root/'discovery'/source/variant
                shared.mkdir(parents=True, exist_ok=True)
                if manifest['observations']:
                    print(json.dumps({'toolchain_event': 'shared_discovery_start', 'source': source,
                        'variant': variant, 'observations': manifest['observations'],
                        'wire_bytes': manifest['exported_wire_bytes']}), flush=True)
                    observed_model, observed_quality = self.discover(input_path, shared, prefix='observed')
                    print(json.dumps({'toolchain_event': 'shared_discovery_complete', 'source': source,
                        'variant': variant, 'services': len(observed_model['services']),
                        'edges': len(observed_model['edges']), 'endpoints': len(observed_model['endpoints'])}), flush=True)
                for name, contract in self.declaration.CONTRACTS.items():
                    folder = self.root/source/variant/name
                    folder.mkdir(parents=True, exist_ok=True)
                    unavailable = {'prediction': None, 'interval': [0, 1], 'by_state': {}, 'available': False}
                    write_json(folder/'input-reference.json', {'path': os.path.relpath(input_path, folder),
                        'sha256': digest(input_path), 'shared': True, 'observations': manifest['observations']})
                    write_json(folder/'entry-evidence.json', self.entry_evidence[source, name])
                    if not manifest['observations']:
                        answer = dict(unavailable, reason='no_frozen_source_observations')
                        write_json(folder/'forecast.json', answer)
                        results[source][variant][name] = answer
                        continue
                    model, quality = observed_model, observed_quality
                    write_json(folder/'observed-reference.json', {'folder': os.path.relpath(shared, folder),
                        'files': {filename: digest(shared/filename) for filename in
                                  ('observed.json', 'observed.signal-quality.json', 'observed.snapshot.json')},
                        'basis': 'same actual Bering graph reused across operations; discovery cost counted once'})
                    proxy_names = sorted({name for key in ('proxy', 'proxy_discovery')
                        for field in ('name', 'container')
                        for name in aliases(self.inventory.get(key, {}).get(field))})
                    def proof_builder(entry):
                        return {index: self.endpoint_entry_evidence(
                            self.entry_evidence[source, name]['roots'], step, entry, model['endpoints'])
                            for index, step in enumerate(contract['steps'])}
                    selected_db, mapping = self.database_nodes(model, quality)
                    write_json(folder/'database-mapping.json', mapping)
                    controlled = unique_service(model, self.declaration.CONTROLLED_SERVICE_ALIASES)
                    binding = resolve_entry_representations(model, quality, contract, proxy_names,
                        proof_builder=proof_builder, identity_groups=self.entry_identity_groups,
                        database_fault_group=mapping, controlled=controlled)
                    binding = self.apply_binding_uncertainties(binding, model, quality)
                    # A missing controlled node is acceptable only for operations
                    # whose declared requirements do not include that service.
                    needs_controlled = any(set(aliases(c.get(role))) & set(self.declaration.CONTROLLED_SERVICE_ALIASES)
                                           for c in contract['required_calls'] for role in ('caller', 'callee'))
                    if needs_controlled and not controlled:
                        binding['unknown'].append({'reason': 'controlled_service_missing_or_ambiguous'})
                        binding['available'] = False
                    write_json(folder/'binding.json', binding)
                    if not binding['available']:
                        answer = dict(unavailable, reason='required_graph_evidence_unavailable',
                                      unknown=binding['unknown'])
                        write_json(folder/'forecast.json', answer)
                        results[source][variant][name] = answer
                        continue
                    static_services, static_evidence = self.static_overlay(model, source, name)
                    write_json(folder/'procrustes-attachment.json', static_evidence)
                    overlay = {'name': 'supplied-operation-and-placement-contract',
                               'services': [s for s in static_services if s['id'] not in {*selected_db, controlled}],
                               'endpoints': []}
                    if controlled:
                        placements = self.inventory.get('replicas', [])
                        if len(placements) != 2 or {p.get('node') for p in placements} != {'a', 'b'}:
                            raise RuntimeError('Controlled placement inventory does not describe one replica per guest')
                        overlay['services'].append({'id': controlled, 'replicas': 2, 'failure_eligible': True,
                            'placements': [{'replicas': 1, 'labels': {'controlled_replica': p['node'], 'guest': p['node']}}
                                           for p in sorted(placements, key=lambda p: p['node'])]})
                    for endpoint in binding['endpoints']:
                        overlay['endpoints'].append({'id': endpoint, 'predicate_ref': name,
                            'semantics': {'predicate_mode': 'external_predicate', 'source': 'supplied_source_contract'}})
                    write_json(folder/'overlay.json', overlay)
                    model, quality = self.operation_model(
                        input_path, folder, folder/'overlay.json', model, quality, shared)
                    faults = fault_inputs(controlled, selected_db)
                    write_json(folder/'faults.json', faults)
                    write_json(folder/'predicates.json', predicate_contract(model, binding, name))
                    analysis = {'schema_version': '1.3', 'seed': self.ctx.seed, 'trials': 100000,
                        'predicate_contract': str(folder/'predicates.json'),
                        'reliability': {'node_live_probability': 1, 'edge_live_probability': 1},
                        'profiles': [{'name': 'state-'+state, 'sampling_mode': 'independent_replica',
                                      **({'fault_profile': 'state-'+state} if 'state-'+state in faults['profiles'] else {})}
                                     for state in STATE_WEIGHTS], 'gate': {'mode': 'report', 'default_action': 'report'}}
                    if faults['profiles']:
                        analysis['fault_contract'] = str(folder/'faults.json')
                    if selected_db:
                        analysis['profiles'].append({'name': 'db-down', 'sampling_mode': 'independent_replica',
                                                     'fault_profile': 'db-down'})
                    write_json(folder/'analysis.json', analysis)
                    print(json.dumps({'toolchain_event': 'simulation_start', 'source': source,
                        'variant': variant, 'operation': name}), flush=True)
                    self.command('sheaft', ['run', '--model', folder/'model.json', '--analysis', folder/'analysis.json',
                                            '--out-dir', folder/'simulation'], folder, 'simulation')
                    report = json.loads((folder/'simulation'/'report.json').read_text())
                    profiles = report['profiles']
                    if isinstance(profiles, list):
                        profiles = {p['name']: p for p in profiles}
                    values = {}
                    for profile_name, profile in profiles.items():
                        avail = profile['simulation']['endpoint_availability']
                        outcomes = [avail[e] for e in binding['endpoints']]
                        # Every endpoint uses the same union of mandatory calls.
                        if len(set(outcomes)) != 1:
                            raise RuntimeError('Composite predicates disagree despite identical obligations')
                        values[profile_name] = outcomes[0]
                    by_state = {state: values['state-'+state] for state in STATE_WEIGHTS}
                    exact = {state: exact_graph_outcome(model, binding,
                             [controlled] if controlled and state == '00' else []) for state in STATE_WEIGHTS}
                    if by_state != exact:
                        raise RuntimeError(f'Sheaft disagrees with exact deterministic graph law: {by_state} != {exact}')
                    exact_database_down = exact_graph_outcome(model, binding, selected_db) if selected_db else None
                    if selected_db and values['db-down'] != exact_database_down:
                        raise RuntimeError('Sheaft database selector disagrees with the exact graph intervention')
                    prediction = sum(STATE_WEIGHTS[s]*v for s, v in by_state.items())
                    answer = {'available': True, 'prediction': prediction, 'interval': [prediction, prediction],
                              'by_state': by_state, 'exact_by_state': exact,
                              'exact_weighted_prediction': sum(STATE_WEIGHTS[s]*v for s, v in exact.items()),
                              'database_down_prediction': values.get('db-down'),
                              'exact_database_down_given_contract': exact_database_down,
                              'database_conditional': bool(contract.get('conditional_db')),
                              'assumed_satisfied_database_requirements': binding['assumed_satisfied_database_requirements'],
                              'all_required_database_channels_observed': binding['all_required_database_channels_observed'],
                              'database_fault_prediction_available': binding['database_fault_prediction_available'],
                              'database_fault_fixed_other_requirements': binding['database_fault_fixed_other_requirements'],
                              'state_weights': STATE_WEIGHTS, 'simulator': 'Sheaft',
                              'graph_sha256': digest(folder/'model.json'),
                              'analysis_sha256': digest(folder/'analysis.json'),
                              'structural_adequacy_is_tested': True}
                    if contract.get('conditional_db'):
                        answer['database_down_prediction'] = None
                        answer['database_unknown_reason'] = 'declared_conditional_database_requirement'
                    if not binding['database_fault_prediction_available']:
                        answer['database_down_prediction'] = None
                        answer['database_unknown_reason'] = 'required_selected_database_channel_or_fault_mapping_unknown'
                        answer['database_fault_unknown'] = binding['database_fault_unknown']
                    write_json(folder/'forecast.json', answer)
                    results[source][variant][name] = answer
        write_json(self.root/'forecasts.json', results)
        execution = []
        for source, variants in results.items():
            for variant, operations in variants.items():
                for operation, forecast in operations.items():
                    folder = self.root/source/variant/operation
                    replay_path = self.root/'discovery'/source/variant/'observed-runtime'/'replay-command.json'
                    simulation_path = folder/'simulation.command.json'
                    execution.append({'source': source, 'variant': variant, 'operation': operation,
                        'bering_executed': replay_path.is_file(),
                        'bering_discovery_shared_across_operations': True,
                        'bering_discovery_record': str(replay_path),
                        'bering_overlay_executed': (folder/'model-runtime'/'replay-command.json').is_file(),
                        'sheaft_executed': simulation_path.is_file(),
                        'prediction_available': forecast['available'],
                        'unknown_reason': forecast.get('reason')})
        write_json(self.root/'execution-summary.json', {'branches': execution,
            'interpretation': 'completed acquisition or qualification does not imply every source produced a graph or reached simulation'})
        return results
