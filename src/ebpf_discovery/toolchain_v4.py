"""Actual source-pinned Procrustes/Bering/Sheaft orchestration.

No evaluator response or outcome rate is accepted by this module.
"""
from __future__ import annotations

from collections import defaultdict, deque
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
from .selection_v4 import canonical_route, select_planned
from .raw_v4 import export_selection
from .bering_v4 import replay

PINS = {
    'Procrustes': '39f76000f8a39c971155e08ebffde829b525911b',
    'Bering': 'dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3',
    'Sheaft': '686a602f4e7b71f3612f1810885e29dd66c8733a',
}
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


def unique_path(model, start, end, *, intermediates=None, call_hint=None):
    """A unique observed directed service path; keep every typed edge on its hops.

    Parallel operation identities on one channel are not alternate service paths.
    More than one service path stays ambiguous rather than selecting a convenient one.
    """
    adjacency = defaultdict(set)
    by_pair = defaultdict(list)
    for edge in model['edges']:
        if edge['kind'] == 'sync':
            if call_hint and edge['to'] == end:
                identity = edge.get('identity') or {}
                http = re.fullmatch(r'(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) (/.+)', call_hint)
                if http:
                    matched = (identity.get('operation', '').upper() == http[1]
                               and canonical_route(identity.get('route', '')) == canonical_route(http[2]))
                else:
                    # RPC service aliases were resolved separately. Match the method
                    # as a complete token, not a substring of another operation.
                    matched = (str(identity.get('operation', '')).rsplit('/', 1)[-1]
                               == call_hint.rsplit('/', 1)[-1])
                if not matched:
                    continue
            adjacency[edge['from']].add(edge['to'])
            by_pair[edge['from'], edge['to']].append(edge['id'])
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
    return sorted({eid for a, b in zip(path, path[1:]) for eid in by_pair[a, b]})


def resolve_contract(model, quality, contract, proxy_aliases=()):
    """Compile supplied obligations against recovered structure, never add structure."""
    required, targets, resolved, unknown = set(), set(), [], []
    databases = db_aliases(model, quality)
    entry = unique_service(model, contract['entry_services'])
    if not entry:
        unknown.append({'reason': 'entry_service_missing_or_ambiguous'})
    for call in contract['required_calls']:
        caller = unique_service(model, call['caller'])
        if 'db_system' in call:
            candidates = []
            for edge in model['edges']:
                if edge['from'] != caller or edge['kind'] != 'sync':
                    continue
                if any(d.get('system') == call['db_system'] for d in databases.get(edge['to'], [])):
                    candidates.append(edge['to'])
            candidates = sorted(set(candidates))
            callee = candidates[0] if len(candidates) == 1 else None
        else:
            callee = unique_service(model, call['callee'])
        path = unique_path(model, caller, callee, intermediates=set(proxy_aliases),
                           call_hint=call.get('operation_hint') if 'db_system' not in call else None) if caller and callee else None
        if path is None:
            unknown.append({'reason': 'required_call_missing_or_ambiguous', 'obligation': call,
                            'resolved_caller': caller, 'resolved_callee': callee})
            continue
        if entry and not reachable(model, entry, caller):
            unknown.append({'reason': 'required_caller_not_uniquely_reachable', 'obligation': call})
            continue
        required.update(path)
        targets.update([caller, callee])
        resolved.append({'obligation': call, 'caller': caller, 'callee': callee,
                         'required_edge_ids': path,
                         **({'compiled_semantics': 'mandatory caller-to-database-endpoint channel',
                             'basis': 'all typed edges on this channel share endpoint liveness; live-edge probability is one',
                             'validity': 'node/whole-endpoint fail-stop interventions only; no individual command or edge failures',
                             'command_level_necessity_inferred': False}
                            if 'db_system' in call else {})})
    endpoints = []
    for step in contract['steps']:
        candidates = [e for e in model['endpoints'] if e['entry_service'] == entry
                      and e.get('method') == step['method']
                      and canonical_route(e.get('path', '')) == canonical_route(step['path'])]
        if len(candidates) != 1:
            unknown.append({'reason': 'entry_endpoint_missing_or_ambiguous', 'step': step,
                            'candidates': [e['id'] for e in candidates]})
        else:
            endpoints.append(candidates[0]['id'])
    return {'entry_service': entry, 'required_edges': sorted(required),
            'mandatory_targets': sorted(targets-{entry}), 'endpoints': sorted(set(endpoints)),
            'resolved_calls': resolved, 'unknown': unknown, 'available': not unknown}


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
    def __init__(self, ctx, system, store, declaration):
        self.ctx, self.system, self.store, self.declaration = ctx, system, store, declaration
        self.root = ctx.out/'toolchain'
        self.root.mkdir(exist_ok=True)
        self.bin = Path(os.environ.get('PBS_BIN', 'work/toolchain/bin')).resolve()
        self.inventory = json.loads((ctx.out/'deployment.json').read_text())

    def command(self, tool, args, folder, name):
        started = time.time_ns()
        result = self.ctx.run([str(self.bin/tool), *map(str, args)], timeout=None, check=False)
        write_json(folder/(name+'.command.json'), dict(started_ns=started, ended_ns=time.time_ns(),
            argv=[tool, *map(str, args)], returncode=result.returncode,
            stdout=result.stdout, stderr=result.stderr))
        if result.returncode:
            raise RuntimeError(f'{tool} {name} failed: {result.stderr[-2500:]}')

    def preflight(self):
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
                goal = {'contract': {'name': 'io.mb3r.procrustes.goal', 'version': '0.1.0'},
                        'scope': {'namespaces': ['*'], 'services': services},
                        'operation': {'id': name+f'-step-{i}', 'entry_service': entry,
                                      'method': step['method'], 'path': step['path'], 'mandatory_targets': []}}
                for source in ('native', 'ebpf'):
                    folder = self.root/'procrustes'/source/name/str(i)
                    folder.mkdir(parents=True, exist_ok=True)
                    write_json(folder/'goal.json', goal)
                    selection = ['--collection-source', 'ebpf-obi', '--source-domain', self.system+'-deployment'] if source == 'ebpf' else []
                    self.command('procrustes', ['analyze', *args, '--goal', folder/'goal.json',
                                               '--out-dir', folder, *selection], folder, 'preflight')
                    self.preflight_reports[source, name].append(folder/'report.json')
        write_json(self.root/'static-inputs.json', {'deployment': self.inventory,
            'tool_pins': PINS, 'contracts': self.declaration.CONTRACTS,
            'procrustes_use': 'reports unchanged; only confirmed identity and replica facts attach to recovered nodes',
            'preflight_scope': 'one declared canonical name per alias group; all deployment namespaces',
            'scenario_limitation': 'custom workload driver is retained separately; no Tracetest scenario is fabricated to pass preflight',
            'supplied_placement_basis': 'rendered controlled-replica inventory, independently attributed',
            'network_scope_rule': 'one declared routed application address space on these two guests',
            'unmatched_inventory': 'retained here; never inserted into graph'})

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

    def select(self, plans, contract, source, path, enriched):
        selected, evidence = select_planned(self.store, plans, contract, source,
            getattr(self.declaration, 'UNTYPED_ENTRY_COMPONENTS', {}))
        manifest = export_selection(self.store, selected, path.parent/'selected-inputs',
                                    self.system+'-routed-network' if enriched else None)
        write_json(path, manifest)
        write_json(path.with_suffix('.selection.json'), dict(evidence,
            observations=manifest['observations'], network_scope_supplied=enriched,
            input_manifest_sha256=digest(path)))
        return manifest['observations']

    def discover(self, input_path, folder, overlay=None, prefix='model'):
        manifest = json.loads(input_path.read_text(encoding='utf-8'))
        return replay(self.bin/'bering', manifest, folder, self.system+'-deployment', overlay, prefix)

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
                        or value.get('network_scope') not in (None, '', expected_scope)
                        or (value.get('address'), value.get('port')) not in endpoints):
                    continue
                selected.add(node)
                witnesses.append({'node': node, 'observed_alias': value})
        return sorted(selected), {
            'declared_system': system, 'declared_endpoints': [list(pair) for pair in sorted(endpoints)],
            'declared_network_scope': expected_scope, 'matched_observed_nodes': sorted(selected),
            'witnesses': witnesses, 'physical_identity_inferred': False,
            'fault_scope': 'all namespaces of the stopped deployment endpoint',
            'mapping_basis': 'explicit deployment attribution of complete address/port pairs; no graph merge',
            'source_files': extra.get('source_files', []),
        }

    def forecast(self, plans):
        self.preflight()
        results = {}
        for source in ('ebpf', 'native', 'combined'):
            results[source] = {}
            for variant in ('raw', 'network_scope'):
                results[source][variant] = {}
                for name, contract in self.declaration.CONTRACTS.items():
                    folder = self.root/source/variant/name
                    folder.mkdir(parents=True, exist_ok=True)
                    input_path = folder/'observations.json'
                    unavailable = {'prediction': None, 'interval': [0, 1], 'by_state': {}, 'available': False}
                    if not self.select(plans, contract, source, input_path, variant != 'raw'):
                        answer = dict(unavailable, reason='no_observed_entry_traces')
                        write_json(folder/'forecast.json', answer)
                        results[source][variant][name] = answer
                        continue
                    model, quality = self.discover(input_path, folder, prefix='observed')
                    proxy_names = aliases(self.inventory.get('proxy', {}).get('name'))
                    binding = resolve_contract(model, quality, contract, proxy_names)
                    controlled = unique_service(model, self.declaration.CONTROLLED_SERVICE_ALIASES)
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
                    selected_db, mapping = self.database_nodes(model, quality)
                    write_json(folder/'database-mapping.json', mapping)
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
                    model, quality = self.discover(input_path, folder, folder/'overlay.json')
                    faults = fault_inputs(controlled, selected_db)
                    write_json(folder/'faults.json', faults)
                    predicate = {k: binding[k] for k in ('entry_service', 'mandatory_targets', 'required_edges')}
                    predicate.update(type='edge_aware', edge_modes=['sync'])
                    definitions = {name: predicate}
                    for endpoint in model['endpoints']:
                        if endpoint['id'] not in binding['endpoints']:
                            definitions[endpoint['success_predicate_ref']] = {
                                'type': 'edge_aware', 'entry_service': endpoint['entry_service'],
                                'mandatory_targets': [], 'edge_modes': ['sync']}
                    write_json(folder/'predicates.json', {'schema_version': '1.1', 'predicates': definitions})
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
                              'state_weights': STATE_WEIGHTS, 'simulator': 'Sheaft',
                              'graph_sha256': digest(folder/'model.json'),
                              'analysis_sha256': digest(folder/'analysis.json'),
                              'structural_adequacy_is_tested': True}
                    if contract.get('conditional_db'):
                        answer['database_down_prediction'] = None
                    write_json(folder/'forecast.json', answer)
                    results[source][variant][name] = answer
        write_json(self.root/'forecasts.json', results)
        execution = []
        for source, variants in results.items():
            for variant, operations in variants.items():
                for operation, forecast in operations.items():
                    folder = self.root/source/variant/operation
                    replay_path = folder/'observed-runtime'/'replay-command.json'
                    simulation_path = folder/'simulation.command.json'
                    execution.append({'source': source, 'variant': variant, 'operation': operation,
                        'bering_executed': replay_path.is_file(),
                        'sheaft_executed': simulation_path.is_file(),
                        'prediction_available': forecast['available'],
                        'unknown_reason': forecast.get('reason')})
        write_json(self.root/'execution-summary.json', {'branches': execution,
            'interpretation': 'completed acquisition or qualification does not imply every source produced a graph or reached simulation'})
        return results
