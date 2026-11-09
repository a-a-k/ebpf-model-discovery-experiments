"""Treatment-specific ACK contracts, compiled from unchanged observed graphs.

This is a correction of supplied outcome semantics, not graph discovery. The
normal-path list is a conservative observation requirement under the registered
fail-stop law; it is not a universal AND definition of HTTP acknowledgement.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import json
import os
from pathlib import Path
import time
from types import SimpleNamespace

from systems.deathstarbench import experiment_v4 as declared
from .runtime import write_json
from .toolchain_v4 import (
    Toolchain as OriginalToolchain, STATE_WEIGHTS, aliases, digest,
    exact_graph_outcome, fault_inputs, predicate_contract,
    resolve_entry_representations, unique_service,
)
from .toolchain_v5 import attach_operation_metadata, Toolchain as LogicalToolchain


OPERATIONS = tuple(declared.CONTRACTS)
SOURCES = ('ebpf', 'native', 'combined', 'context-baseline')
VIEWS = ('raw', 'network_scope')
SOURCE_PIN = '6ecb09706140f8730b5385c08f1386c654c3c526'
UNAVAILABLE = {'available': False, 'prediction': None, 'interval': [0, 1], 'by_state': {}}


def contracts():
    normal = deepcopy(declared.CONTRACTS)
    database = deepcopy(normal)
    # The Mongo declared exception exits before UserRedis/Home and is decoded
    # but not thrown by the pinned ComposePost Lua client. The Mongo endpoint
    # remains ON the attempted path and must still be attributed to the fault.
    database['compose_post']['required_calls'] = [
        c for c in normal['compose_post']['required_calls']
        if 'db_system' not in c and c.get('callee') != ['home-timeline-service']
        and c.get('caller') != ['home-timeline-service']
    ]
    # The registered reset/readiness establishes the untouched fixture in Redis.
    # A failed Mongo cursor is not turned into an exception by ReadUserTimeline;
    # the retained Redis IDs still reach PostStorage. This is a fixed-fixture
    # result, not a claim that Mongo is absent from the attempted fallback path.
    database['read_user_timeline']['conditional_db'] = []
    return {'primary': normal, 'database_down': database}


def semantics(operation=None):
    outcomes = {'compose_post': 'HTTP success with Successfully upload post marker; not Mongo write or durability',
                'read_home_timeline': 'HTTP success and parsed timeline containing the exact stable follower fixture',
                'read_user_timeline': 'HTTP success and parsed timeline containing the exact stable owner fixture'}
    value = {
        'outcomes': outcomes,
        'source_pin': SOURCE_PIN,
        'normal_path_is_conservative_observation_admission_not_unconditional_ACK_necessity': True,
        'primary_law': 'Only controlled UserTimeline replicas fail-stop; ordinary unvaried services, stores and noncongested client pools are fulfilled conditions.',
        'database_law': 'Selected UserTimeline MongoDB stops with both replicas up; its declared ServiceException propagates in T_REPLY and Lua ignores se. Ordinary child transport exceptions become TApplicationException and HTTP failure.',
        'compose_selected_database_is_off_path': False,
        'fixed_unvaried_conditions': [
            'Text calls URL-shortening and user-mention RPCs even for empty URL/mention lists; their empty-list backend work is skipped.',
            'CreatorWithUserId constructs the supplied identity without a user database lookup.',
            'Media RPC occurs for the supplied media list; no media database requirement is inferred.',
            'PostStorage, HomeTimeline/SocialGraph and unvaried stores remain fulfilled conditions; no recovered edges are invented for them.',
            'Pool saturation, extra runtime/application errors and cache/driver behavior outside the stated law can produce forecast misses; retain them.',
        ],
        'same_semantics_all_sources_and_direct_baseline': True,
        'read_Lua_clients_check_declared_exceptions': True,
        'read_user_database_law': 'Successful readiness/reset leaves the untouched fixture in Redis; a failed Mongo fallback cursor is ignored and retained Redis IDs are fetched from PostStorage. Client pools, Redis/PostStorage and the fixture remain fulfilled conditions.',
    }
    if operation is not None:
        value['operation'] = operation
        value['outcome'] = outcomes[operation]
        value['selected_database_is_off_path'] = operation == 'read_home_timeline'
    return value


def direct_baselines():
    from .evaluate_v4 import _manual_baselines
    result = _manual_baselines('deathstarbench', list(OPERATIONS))
    result['compose_post']['database'] = {
        'available': True, 'database_down_prediction': 1.0,
        'basis': 'Selected Mongo is on the attempted path; its declared failure is masked by the pinned Lua ACK receiver under the registered fixed-prefix conditions.',
        'selected_database_is_off_path': False,
    }
    result['read_user_timeline']['database'] = {
        'available': True, 'database_down_prediction': 1.0,
        'basis': 'Registered readiness/reset warms the untouched Redis fixture; the pinned handler ignores a failed Mongo cursor and retains cached IDs for PostStorage.',
        'selected_database_is_off_path': False,
    }
    for operation, value in result.items():
        value['outcome_contract_scope'] = semantics(operation)
    return result


def entry_proofs(old_binding, entry):
    candidates = [old_binding, *[c['binding'] for c in
        old_binding.get('entry_identity_resolution', {}).get('candidates', [])]]
    result = {}
    for candidate in candidates:
        if candidate.get('entry_service') != entry:
            continue
        for index, item in enumerate(candidate.get('endpoint_bindings', [])):
            if 'proof' in item:
                if index in result and result[index] != item['proof']:
                    raise ValueError('conflicting frozen entry proof')
                result[index] = item['proof']
    return result


def bind(model, quality, contract, old_binding, mapping, inventory, identity_groups):
    proxy_names = sorted({v for kind in ('proxy', 'proxy_discovery') for field in ('name', 'container')
                          for v in aliases(inventory.get(kind, {}).get(field))})
    controlled = unique_service(model, declared.CONTROLLED_SERVICE_ALIASES)
    value = resolve_entry_representations(model, quality, contract, proxy_names,
        proof_builder=lambda entry: entry_proofs(old_binding, entry),
        identity_groups=identity_groups, database_fault_group=mapping, controlled=controlled)
    extra = LogicalToolchain.binding_uncertainties(None, model, quality)
    if extra:
        value['unknown'].extend(extra)
        value['available'] = False
    needs_controlled = any(set(aliases(c.get(role))) & set(declared.CONTROLLED_SERVICE_ALIASES)
                           for c in contract['required_calls'] for role in ('caller', 'callee'))
    if needs_controlled and not controlled:
        value['unknown'].append({'reason': 'controlled_service_missing_or_ambiguous'})
        value['available'] = False
    return value, controlled


def frozen_graph(root, source, view, operation):
    """Select exact preexisting logical graph/proofs, never reconstruct input."""
    tool = Path(root) / 'toolchain'
    if source == 'context-baseline':
        context = tool / 'context-baseline' / view
        proof = json.loads((context / 'provenance.json').read_text(encoding='utf8'))
        if proof['status'] in ('reuse_single_source_equivalence', 'reuse_unchanged_union'):
            return frozen_graph(root, 'combined', view, operation)
        if proof['status'] != 'forecast_from_observed_context_union':
            return None, {'reason': 'frozen_context_union_not_admitted', 'provenance': proof}
        folder = context / 'operations' / operation
        union = json.loads((context / 'union-proof.json').read_text(encoding='utf8'))
        quality_path = tool / 'discovery' / 'combined' / view / 'observed.signal-quality.json'
        graph_path = context / 'union-model.json'
        if not quality_path.exists():
            # Combined may share the exact eBPF graph when native is empty.
            quality_path = tool / 'discovery' / 'ebpf' / view / 'observed.signal-quality.json'
        if (digest(quality_path) != union['files']['base_quality']['sha256'] or
                digest(graph_path) != union['files']['union_model']['sha256']):
            raise ValueError('frozen context model/quality identity differs')
        return (graph_path, quality_path, folder, 'combined'), {'union_proof_sha256': digest(context / 'union-proof.json'),
                                                               'union': union}
    folder = tool / source / view / operation
    forecast = json.loads((folder / 'forecast.json').read_text(encoding='utf8'))
    shared = tool / 'discovery' / source / view
    if (shared / 'shared-observed-reference.json').exists():
        reference = json.loads((shared / 'shared-observed-reference.json').read_text(encoding='utf8'))
        if source != 'combined' or reference['origin_source'] != 'ebpf':
            raise ValueError('unexpected frozen identical-input discovery reference')
        shared = tool / 'discovery' / 'ebpf' / view
    graph_path, quality_path = shared / 'observed.json', shared / 'observed.signal-quality.json'
    if not graph_path.exists():
        if forecast.get('reason') != 'no_frozen_source_observations':
            raise ValueError('missing graph is not an admitted empty source')
        return None, {'reason': 'no_frozen_source_observations'}
    return (graph_path, quality_path, folder, source), {'observed_graph_sha256': digest(graph_path),
                                                     'observed_quality_sha256': digest(quality_path)}


def simulate(tool, original, quality, binding, controlled, mapping, operation, scenario, folder):
    """Use the existing metadata-only overlay and actual Sheaft executable."""
    folder.mkdir(parents=True)
    selected_db = mapping['matched_observed_nodes']
    static, evidence = tool.static_overlay(original, tool.correction_origin_source, operation)
    overlay = {'name': 'audited-ACK-contract', 'services': [s for s in static
               if s['id'] not in {*selected_db, controlled}], 'endpoints': []}
    if controlled:
        replicas = tool.inventory['replicas']
        if len(replicas) != 2 or {r['node'] for r in replicas} != {'a', 'b'}:
            raise ValueError('frozen inventory must have the original two controlled slots')
        overlay['services'].append({'id': controlled, 'replicas': 2, 'failure_eligible': True,
            'placements': [{'replicas': 1, 'labels': {'controlled_replica': r['node'], 'guest': r['node']}}
                           for r in sorted(replicas, key=lambda r: r['node'])]})
    for endpoint in binding['endpoints']:
        overlay['endpoints'].append({'id': endpoint, 'predicate_ref': operation,
            'semantics': {'predicate_mode': 'external_predicate', 'source': 'supplied_source_contract'}})
    attached = attach_operation_metadata(original, overlay)
    write_json(folder / 'model.json', attached)
    write_json(folder / 'overlay.json', overlay)
    write_json(folder / 'procrustes-attachment.json', evidence)
    write_json(folder / 'binding.json', binding)
    tool.command('bering', ['validate', '--input', folder / 'model.json'], folder, 'model-validation')
    faults = fault_inputs(controlled, selected_db)
    write_json(folder / 'faults.json', faults)
    write_json(folder / 'predicates.json', predicate_contract(attached, binding, operation))
    profiles = ([{'name': 'db-down', 'sampling_mode': 'independent_replica', 'fault_profile': 'db-down'}]
                if scenario == 'database_down' else
                [{'name': 'state-' + state, 'sampling_mode': 'independent_replica',
                  **({'fault_profile': 'state-' + state} if 'state-' + state in faults['profiles'] else {})}
                 for state in STATE_WEIGHTS])
    analysis = {'schema_version': '1.3', 'seed': tool.ctx.seed, 'trials': 100000,
                'predicate_contract': str(folder / 'predicates.json'),
                'reliability': {'node_live_probability': 1, 'edge_live_probability': 1},
                'profiles': profiles, 'gate': {'mode': 'report', 'default_action': 'report'}}
    if faults['profiles']:
        analysis['fault_contract'] = str(folder / 'faults.json')
    write_json(folder / 'analysis.json', analysis)
    tool.command('sheaft', ['run', '--model', folder / 'model.json', '--analysis', folder / 'analysis.json',
                           '--out-dir', folder / 'simulation'], folder, 'simulation')
    rows = json.loads((folder / 'simulation/report.json').read_text(encoding='utf8'))['profiles']
    rows = {r['name']: r for r in rows} if isinstance(rows, list) else rows
    values = {}
    for name, profile in rows.items():
        scores = [profile['simulation']['endpoint_availability'][e] for e in binding['endpoints']]
        if len(set(scores)) != 1:
            raise ValueError('operation endpoint scores disagree')
        values[name] = scores[0]
        failed = selected_db if name == 'db-down' else ([controlled] if controlled and name == 'state-00' else [])
        if values[name] != exact_graph_outcome(attached, binding, failed):
            raise ValueError('actual Sheaft result differs from exact deterministic graph law')
    return {'values': values, 'simulator': 'Sheaft', 'graph_sha256': digest(folder / 'model.json'),
            'analysis_sha256': digest(folder / 'analysis.json')}


def compile_forecasts(root, output, ctx):
    root, output = Path(root).resolve(), Path(output).resolve()
    static = json.loads((root / 'toolchain/static-inputs.json').read_text(encoding='utf8'))
    from .toolchain_v5 import PINS
    if static['tool_pins'] != PINS:
        raise ValueError('original and corrected product pins differ')
    output.mkdir(parents=True)
    for source_path, destination in ((root / 'toolchain/static-inputs.json', output / 'original-static-inputs.json'),
                                      (root / 'deployment.json', output / 'original-deployment-inventory.json')):
        destination.write_bytes(source_path.read_bytes())
    reader_context = SimpleNamespace(out=root, seed=ctx.seed, run=ctx.run)
    tool = OriginalToolchain(reader_context, 'deathstarbench', None, declared, tool_pins=static['tool_pins'])
    tool.preflight_reports = defaultdict(list)
    for source in ('native', 'ebpf'):
        for operation in OPERATIONS:
            tool.preflight_reports[source, operation] = sorted((root / 'toolchain/procrustes' / source / operation).glob('*/report.json'))
    # The output Context supplies fresh command/cost recording; static evidence
    # and inventory belong to the exact frozen model, not the new worker.
    tool.inventory = json.loads((root / 'deployment.json').read_text(encoding='utf8'))
    all_contracts = contracts()
    result = {}
    for source in SOURCES:
        result[source] = {}
        for view in VIEWS:
            result[source][view] = {}
            for operation in OPERATIONS:
                graph, proof = frozen_graph(root, source, view, operation)
                answer = deepcopy(UNAVAILABLE)
                answer.update(database_forecast={'available': False, 'prediction': None},
                              supplied_outcome_semantics=semantics(operation), original_graph=proof)
                if graph is None:
                    answer['reason'] = proof['reason']
                    result[source][view][operation] = answer
                    continue
                graph_path, quality_path, old_folder, origin = graph
                for imported, name in ((graph_path, 'original-observed-model.json'), (quality_path, 'original-observed-quality.json')):
                    destination = output / source / view / name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if destination.exists() and digest(destination) != digest(imported):
                        raise ValueError('operation-specific graph differs from frozen shared view')
                    if not destination.exists():
                        destination.write_bytes(imported.read_bytes())
                model, quality = (json.loads(p.read_text(encoding='utf8')) for p in (graph_path, quality_path))
                mapping = json.loads((old_folder / 'database-mapping.json').read_text(encoding='utf8'))
                old_binding = json.loads((old_folder / 'binding.json').read_text(encoding='utf8'))
                write_json(output / source / view / operation / 'original-database-mapping.json', mapping)
                write_json(output / source / view / operation / 'original-entry-binding.json', old_binding)
                tool.correction_origin_source = origin
                for scenario in ('primary', 'database_down'):
                    contract = all_contracts[scenario][operation]
                    binding, controlled = bind(model, quality, contract, old_binding, mapping,
                                               tool.inventory, static.get('supplied_entry_identity_groups', []))
                    folder = output / source / view / operation / scenario
                    folder.parent.mkdir(parents=True, exist_ok=True)
                    if (not binding['available'] or (scenario == 'database_down' and
                            (contract.get('conditional_db') or not binding['database_fault_prediction_available']))):
                        folder.mkdir()
                        write_json(folder / 'binding.json', binding)
                        unknown = {'available': False, 'prediction': None,
                                   'reason': ('conditional_database_requirement' if scenario == 'database_down' and
                                              contract.get('conditional_db') else 'required_graph_or_fault_attribution_unavailable'),
                                   'unknown': binding['unknown'], 'database_fault_unknown': binding['database_fault_unknown']}
                        if scenario == 'primary':
                            answer.update(reason=unknown['reason'], unknown=unknown['unknown'])
                        else:
                            answer['database_forecast'] = unknown
                        continue
                    run = simulate(tool, model, quality, binding, controlled, mapping, operation, scenario, folder)
                    if scenario == 'primary':
                        states = {s: run['values']['state-' + s] for s in STATE_WEIGHTS}
                        prediction = sum(STATE_WEIGHTS[s] * value for s, value in states.items())
                        answer.update(available=True, prediction=prediction, interval=[prediction, prediction],
                                      by_state=states, execution=run)
                    else:
                        answer['database_forecast'] = {'available': True, 'prediction': run['values']['db-down'],
                                                       'execution': run, 'selected_database_is_off_path': operation == 'read_home_timeline'}
                result[source][view][operation] = answer
    write_json(output / 'forecasts.json', result)
    write_json(output / 'direct-baselines.json', direct_baselines())
    write_json(output / 'outcome-contracts.json', {'contracts': all_contracts, 'semantics': semantics()})
    return result
