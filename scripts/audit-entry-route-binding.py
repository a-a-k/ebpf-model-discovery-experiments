"""Inspect fixed saved bindings, supplied roles, or operation metadata.

Only the explicit semantic-metadata mode runs diagnostic validation/simulation;
it never creates a primary forecast or scores application outcomes.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import sqlite3
import subprocess
import time
from types import SimpleNamespace
import zipfile
from urllib.parse import quote_plus

import yaml

from ebpf_discovery.binding_v5 import endpoint_alias_evidence
from ebpf_discovery.store_v3 import normalized_file
from ebpf_discovery.store_v5 import _digest
from systems.petclinic.experiment_v4 import CONTRACTS


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def model_publication(root, model_path, runtime_path):
    """Bind the two allowed publication-local fields to their original serve."""
    model = read(root / model_path)
    command_path = root / runtime_path / 'replay-command.json'
    config_path = root / runtime_path / 'serve.yaml'
    command, config = read(command_path), yaml.safe_load(config_path.read_text())
    argv = command['argv']
    if (command['status'] != 'complete' or command['returncode'] != 0
            or len(argv) != 4 or argv[1:3] != ['serve', '--config']
            or member(argv[3]) != runtime_path + '/serve.yaml'):
        raise ValueError('publication command does not name its saved serve configuration')
    reference = 'bering://serve?listen=' + quote_plus(config['server']['listen_address'], safe='')
    if model['metadata']['source_ref'] != reference:
        raise ValueError('publication source_ref differs from the exact saved listen address')
    clock = model['metadata']['discovered_at']
    stamp = datetime.fromisoformat(clock.replace('Z', '+00:00'))
    if (stamp.utcoffset() is None
            or not command['started_ns'] // 10**9 <= stamp.timestamp() <= command['ended_ns'] // 10**9):
        raise ValueError('publication clock lies outside its original serve command interval')
    sequence = command['accepted_request_sequence']
    sequence_name = runtime_path + '/accepted-request-sequence.jsonl'
    if member(sequence['path']) != sequence_name:
        raise ValueError('accepted request sequence is outside its original publication')
    sequence_path = root / sequence_name
    body = sequence_path.read_bytes()
    if (len(body) != sequence['bytes'] or hashlib.sha256(body).hexdigest() != sequence['sha256']
            or not body.endswith(b'\n')):
        raise ValueError('complete accepted request sequence bytes differ')
    accepted = [json.loads(line) for line in body.splitlines()]
    if (not accepted or len(accepted) != sequence['requests']
            or any(row['http_status'] != 200 or row['export_index'] != index
                   for index, row in enumerate(accepted))):
        raise ValueError('saved publication lacks an ordered successful complete ingest sequence')
    return {'model_path': model_path, 'model_sha256': sha(root / model_path),
            'command_path': runtime_path + '/replay-command.json', 'command_sha256': sha(command_path),
            'config_path': runtime_path + '/serve.yaml', 'config_sha256': sha(config_path),
            'sequence_path': sequence_name, 'sequence_sha256': sha(sequence_path),
            'sequence_requests': len(accepted), 'sequence_bytes': len(body),
            'listen_address': config['server']['listen_address'], 'source_ref': reference,
            'discovered_at': clock, 'started_ns': command['started_ns'], 'ended_ns': command['ended_ns'],
            'accepted_sequence': [(r['endpoint'], r['content_bytes'], r['content_sha256']) for r in accepted]}


def compare_metadata_models(first, original, replacement, first_publication, second_publication):
    """All model fields exact except two individually proven publication fields."""
    if replacement['metadata'] != first['metadata']:
        raise ValueError('replacement did not retain the actual first discovery provenance')
    for publication, model in ((first_publication, first), (second_publication, original)):
        for field in ('discovered_at', 'source_ref'):
            if publication[field] != model['metadata'][field]:
                raise ValueError('model publication proof differs from its model')
    if first_publication['accepted_sequence'] != second_publication['accepted_sequence']:
        raise ValueError('old Go overlay used a different accepted request sequence')
    compared = copy.deepcopy(original)
    deltas = []
    for field in ('discovered_at', 'source_ref'):
        old, new = original['metadata'][field], replacement['metadata'][field]
        if old != new:
            deltas.append({'path': 'metadata.' + field, 'original_second_publication': old,
                           'replacement_retained_first_publication': new,
                           'reason': 'distinct actual Bering serve publication; no second discovery in replacement'})
        compared['metadata'][field] = new
    return {'all_other_model_fields_exact': compared == replacement, 'publication_deltas': deltas,
            'first_publication': first_publication, 'second_publication': second_publication}


def audit_semantic_metadata(source, cell, out):
    """Eight frozen Go-overlay pairs and two original pre-target technical failures."""
    from ebpf_discovery.runtime import write_json
    from ebpf_discovery.supplied_alias_v5 import semantic_view
    from ebpf_discovery.toolchain_v4 import STATE_WEIGHTS, fault_inputs, predicate_contract, unique_service
    from ebpf_discovery.toolchain_v5 import PINS, attach_operation_metadata
    from systems.petclinic.experiment_v4 import CONTROLLED_SERVICE_ALIASES
    started = time.monotonic()
    source, out = source.resolve(), out.resolve()
    destination = out.parent / 'semantic-metadata'
    destination.mkdir(parents=True, exist_ok=False)
    original_hashes, roots, api_proofs = {}, {}, {}
    for label in ('baseline', 'partial', 'full'):
        identity = cell['baseline'] if label == 'baseline' else cell
        for kind in ('full', 'compact'):
            role = label + '_' + kind if label != 'full' else kind
            metadata = read(source / (role + '-api.json'))
            archive_path = source / (role + '.zip')
            expected = cell[role]
            if ({key: metadata[key] for key in expected} != expected
                    or metadata['workflow_run']['id'] != identity['run_id']
                    or metadata['workflow_run']['head_sha'] != identity['head_sha']
                    or metadata.get('expired') is not False
                    or archive_path.stat().st_size != expected['size_in_bytes']
                    or sha(archive_path) != expected['digest'].removeprefix('sha256:')):
                raise ValueError('original artifact identity/digest differs: ' + role)
            api_proofs[role] = metadata
            target = source / ('saved-' + role)
            target.mkdir(exist_ok=False)
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                if len(names) != len(set(names)):
                    raise ValueError('duplicate original archive member')
                for item in archive.infolist():
                    name = PurePosixPath(item.filename)
                    if (name.is_absolute() or '..' in name.parts or '\\' in item.filename
                            or stat.S_ISLNK(item.external_attr >> 16)):
                        raise ValueError('unsafe original archive member')
                archive.extractall(target)
            if kind == 'full':
                roots[label] = target
        root = roots[label]
        compact_role = label + '_compact' if label != 'full' else 'compact'
        compact = source / ('saved-' + compact_role)
        manifest = read(compact / 'evaluation-manifest.json')
        if manifest['commit'] != identity['head_sha'] or manifest['run_id'] != str(identity['run_id']):
            raise ValueError('compact evaluation identity differs')
        for name in ('status.json', 'evaluation-v5.json'):
            if (sha(compact / name) != manifest['files_sha256'][name]
                    or (compact / name).read_bytes() != (root / name).read_bytes()):
                raise ValueError('compact/full status or evaluation differs')
        status = read(root / 'status.json')
        if (status['commit'] != identity['head_sha'] or status['run_id'] != str(identity['run_id'])
                or status['system'] != 'petclinic' or status['collector'] != 'coroot'
                or status['mode'] != ('partial' if label == 'partial' else 'full') or status['seed'] != 6):
            raise ValueError('original capture status differs')
        if label == 'baseline':
            freeze = read(root / 'freeze-integrity.json')
            for name in ('freeze-integrity.json', 'toolchain/forecasts.json'):
                if (sha(compact / name) != manifest['files_sha256'][name]
                        or (compact / name).read_bytes() != (root / name).read_bytes()):
                    raise ValueError('baseline compact/full frozen output differs')
            if not freeze['all_unchanged']:
                raise ValueError('original baseline freeze is not intact')
        else:
            phases = read(root / 'evaluation-v5.json')['completeness']['phase_counts']
            if (status['status'] != 'technical_failure' or status['observed_operations'] != 48
                    or phases['target'] != 0 or phases['class_test'] != 0
                    or (root / 'freeze-integrity.json').exists()):
                raise ValueError('failed source is not the declared unfinished pre-target case')

    def saved(label, name):
        path = roots[label] / name
        digest = sha(path)
        if label == 'baseline' and read(roots[label] / 'freeze-integrity.json')['sha256_by_path'].get(name) != digest:
            raise ValueError('used baseline source is absent from its intact pre-target freeze: ' + name)
        original_hashes[(label, name)] = digest
        return read(path)

    for label in roots:
        static = saved(label, 'toolchain/static-inputs.json')
        if (static['tool_pins'] != PINS
                or static['contracts'] != json.loads(json.dumps(CONTRACTS))):
            raise ValueError('original tool pins or supplied operation knowledge differ')
    pairs = []
    for variant in ('raw', 'network_scope'):
        base = f'toolchain/discovery/native/{variant}'
        observed = saved('baseline', base + '/observed.json')
        if observed != saved('baseline', base + '/observed.bering-raw.json'):
            raise ValueError('baseline is not an already canonical native Bering model')
        first = model_publication(roots['baseline'], base + '/observed.json', base + '/observed-runtime')
        for operation in CONTRACTS:
            folder = f'toolchain/native/{variant}/{operation}'
            overlay = saved('baseline', folder + '/overlay.json')
            original = saved('baseline', folder + '/model.json')
            if original != saved('baseline', folder + '/model.bering-raw.json'):
                raise ValueError('old operation model includes a nonidentity semantic projection')
            second = model_publication(roots['baseline'], folder + '/model.json', folder + '/model-runtime')
            for publication in (first, second):
                for field in ('command_path', 'config_path', 'sequence_path'):
                    name = publication[field]
                    # Config is YAML, but its original bytes are frozen too.
                    path = roots['baseline'] / name
                    digest = sha(path)
                    if read(roots['baseline'] / 'freeze-integrity.json')['sha256_by_path'].get(name) != digest:
                        raise ValueError('publication evidence is absent from baseline freeze')
                    original_hashes[('baseline', name)] = digest
            attached = attach_operation_metadata(observed, overlay)
            pair = compare_metadata_models(observed, original, attached, first, second)
            pair.update(variant=variant, operation=operation)
            pairs.append(pair)
            write_json(destination / 'baseline' / variant / operation / 'original-go-model.json', original)
            write_json(destination / 'baseline' / variant / operation / 'attached-model.json', attached)
            write_json(destination / 'baseline' / variant / operation / 'original-overlay.json', overlay)

    binaries = Path(__import__('os').environ['PBS_BIN']).resolve()
    build = read(binaries.parent / 'toolchain-build.json')
    if {row['name']: row['commit'] for row in build['binaries']} != {k.lower(): v for k, v in PINS.items()}:
        raise ValueError('diagnostic binaries differ from source-pinned toolchain')
    for row in build['binaries']:
        if sha(Path(row['binary'])) != row['binary_sha256']:
            raise ValueError('built diagnostic binary hash differs')
    diagnostics = []
    for label, variant, operation in (('partial', 'raw', 'list_owners'),
                                       ('full', 'network_scope', 'owner_details_with_visits')):
        base = f'toolchain/discovery/combined/{variant}'
        folder = f'toolchain/combined/{variant}/{operation}'
        observed = saved(label, base + '/observed.json')
        projection = saved(label, base + '/observed.supplied-aliases.json')
        raw = saved(label, base + '/observed.bering-raw.json')
        table_path = 'runtime-identity-v5/supplied-service-aliases-training.json'
        table = saved(label, table_path)
        admission = saved(label, 'runtime-identity-v5/supplied-service-alias-admission-training.json')
        if (projection['raw_model_sha256'] != sha(roots[label] / base / 'observed.bering-raw.json')
                or projection['table_sha256'] != sha(roots[label] / table_path)):
            raise ValueError('saved canonical model projection differs from its original inputs')
        if projection['metadata_collisions']:
            raise ValueError('pre-attachment source has a genuine unresolved metadata conflict')
        raw_quality = saved(label, base + '/observed.bering-raw.signal-quality.json')
        canonical, _, reproduced_projection = semantic_view(raw, raw_quality, table, admission['aliases'])
        if canonical != observed or reproduced_projection['metadata_collisions']:
            raise ValueError('original canonical source does not reproduce from its saved raw graph and aliases')
        if [e['id'] for e in raw['edges']] != [e['id'] for e in observed['edges']]:
            raise ValueError('original logical projection changed raw observed edge membership')
        overlay, binding = saved(label, folder + '/overlay.json'), saved(label, folder + '/binding.json')
        if not binding['available']:
            raise ValueError('original failure did not have the declared supported binding')
        attached = attach_operation_metadata(observed, overlay)
        if (attached['edges'] != observed['edges']
                or [s['id'] for s in attached['services']] != [s['id'] for s in observed['services']]
                or [e['id'] for e in attached['endpoints']] != [e['id'] for e in observed['endpoints']]):
            raise ValueError('metadata attachment changed observed graph membership or edges')
        target = destination / label
        write_json(target / 'model.json', attached)
        if label == 'full':
            analysis = saved(label, folder + '/analysis.json')
            predicates, faults = saved(label, folder + '/predicates.json'), saved(label, folder + '/faults.json')
            original_failure = saved(label, folder + '/simulation.command.json')
            if original_failure['returncode'] == 0 or 'source unreachable from the entry service' not in original_failure['stderr']:
                raise ValueError('saved full failure differs from the declared reachability error')
            relocations = []
            for field, filename in (('predicate_contract', 'predicates.json'), ('fault_contract', 'faults.json')):
                if member(analysis[field]) != folder + '/' + filename:
                    raise ValueError('saved analysis refers outside its original operation')
                relocations.append({'field': field, 'original': analysis[field], 'relocated': str(target / filename)})
                analysis[field] = str(target / filename)
            origin = 'original saved analysis, predicates and faults; only the two analysis file paths relocated'
        else:
            mapping = saved(label, folder + '/database-mapping.json')
            selected_db = mapping['matched_observed_nodes']
            controlled = unique_service(observed, CONTROLLED_SERVICE_ALIASES)
            faults, predicates = fault_inputs(controlled, selected_db), predicate_contract(attached, binding, operation)
            analysis = {'schema_version': '1.3', 'seed': cell['seed'], 'trials': 100000,
                        'predicate_contract': str(target / 'predicates.json'),
                        'reliability': {'node_live_probability': 1, 'edge_live_probability': 1},
                        'profiles': [{'name': 'state-' + state, 'sampling_mode': 'independent_replica',
                                      **({'fault_profile': 'state-' + state} if 'state-' + state in faults['profiles'] else {})}
                                     for state in STATE_WEIGHTS],
                        'gate': {'mode': 'report', 'default_action': 'report'}}
            if faults['profiles']:
                analysis['fault_contract'] = str(target / 'faults.json')
            if selected_db:
                analysis['profiles'].append({'name': 'db-down', 'sampling_mode': 'independent_replica', 'fault_profile': 'db-down'})
            original_failure = {'bering_log': (roots[label] / folder / 'model-runtime/bering.log').read_text()}
            if 'references unknown service "visits-service"' not in original_failure['bering_log']:
                raise ValueError('saved partial failure differs from the declared overlay identity error')
            name = folder + '/model-runtime/bering.log'
            original_hashes[(label, name)] = sha(roots[label] / name)
            relocations, origin = [], 'unchanged controller fault_inputs/predicate_contract/STATE_WEIGHTS with original binding and DB mapping'
        for name, value in (('analysis', analysis), ('predicates', predicates), ('faults', faults),
                            ('original-binding', binding), ('original-overlay', overlay),
                            ('original-observed', observed), ('original-semantic-projection', projection)):
            write_json(target / (name + '.json'), value)
        write_json(target / 'original-raw-bering-model.json', raw)
        commands = []
        for tool, args in (('bering', ['validate', '--input', str(target / 'model.json')]),
                           ('sheaft', ['run', '--model', str(target / 'model.json'), '--analysis', str(target / 'analysis.json'),
                                       '--out-dir', str(target / 'simulation')])):
            stamp = time.time_ns()
            result = subprocess.run([str(binaries / tool), *args], capture_output=True, text=True, check=False)
            record = {'argv': [str(binaries / tool), *args], 'started_ns': stamp, 'ended_ns': time.time_ns(),
                      'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
            write_json(target / (tool + '.command.json'), record)
            commands.append(record)
            if result.returncode:
                break
        diagnostics.append({'source': label, 'variant': variant, 'operation': operation,
                            'original_technical_failure': original_failure, 'analysis_origin': origin,
                            'path_relocations': relocations, 'commands': commands,
                            'existing_observed_edges_exact': True, 'primary_forecast_created': False,
                            'technical_commands_succeeded': len(commands) == 2 and all(c['returncode'] == 0 for c in commands)})
    if any(sha(roots[label] / name) != expected for (label, name), expected in original_hashes.items()):
        raise ValueError('original saved scientific files changed during diagnostic inspection')
    facts = {'cell': cell, 'artifact_api': api_proofs, 'pairs': pairs, 'diagnostics': diagnostics,
             'original_file_sha256_verified_before_and_after': [{'source': label, 'path': name, 'sha256': value}
                                                               for (label, name), value in original_hashes.items()],
             'toolchain_build': build, 'capture_replay_fit_primary_forecast_or_outcome_scoring': False,
             'prototype_source_sha256': {name: sha(Path(__file__).parents[1] / 'src/ebpf_discovery' / name)
                                        for name in ('toolchain_v4.py', 'toolchain_v5.py')},
             'diagnostic_simulation_only': True, 'failed_cases_have_no_completed_pre_target_freeze': True,
             'elapsed_seconds': time.monotonic() - started, 'human_preparation_seconds': None}
    write_json(out, facts)
    if not all(pair['all_other_model_fields_exact'] for pair in pairs):
        raise ValueError('paired metadata models have unexplained differences; inspect retained models')
    if not all(row['technical_commands_succeeded'] for row in diagnostics):
        raise ValueError('diagnostic validation/simulation retained a technical failure')


def member(path):
    for folder in ('toolchain', 'native'):
        marker = '/' + folder + '/'
        if marker in path:
            result = folder + '/' + path.split(marker, 1)[1]
            if '..' not in PurePosixPath(result).parts:
                return result
    raise ValueError('unrecognized original capture locator')


class SavedRoots:
    def __init__(self, root, roots):
        self.rows = {}
        segments = {}
        for selected in roots:
            for proof in selected['observation_provenance']:
                key = (proof['raw_file'], proof['from_byte'], proof['through_byte'])
                if key not in segments:
                    path = root / member(key[0])
                    with path.open('rb') as stream:
                        stream.seek(key[1]); body = stream.read(key[2] - key[1])
                    if (len(body) != key[2] - key[1]
                            or hashlib.sha256(body).hexdigest() != proof['segment_sha256']):
                        raise ValueError('native root source segment differs')
                    segments[key] = list(normalized_file(path, 'native', key[1], key[2]))
                row = segments[key][proof['normalized_ordinal']]
                if _digest(row) != selected['observation_digest']:
                    raise ValueError('saved root digest differs from original raw observation')
                row = copy.deepcopy(row)
                row['_observation_provenance'] = selected['observation_provenance']
                self.rows[selected['observation_digest']] = row

    def observation_v5(self, digest):
        return self.rows.get(digest)


def audit_provided_roles(root, training, cell, out, started, verified):
    """Inspect the same saved inputs; no new forecasts or mutable checkpoint."""
    from collections import Counter
    from ebpf_discovery.supplied_alias_v5 import (
        admit_observed, build, deployment_roles, semantic_view)
    manifest = read(training / 'manifest.json')
    ready = read(training / 'ready.json')
    if (sha(training / 'manifest.json') != ready['manifest_sha256']
            or any(manifest['identity'][key] != cell[key] for key in ('system', 'mode', 'seed'))
            or manifest['identity']['commit'] != cell['head_sha']
            or manifest['identity']['run_id'] != str(cell['run_id'])):
        raise ValueError('original training checkpoint identity differs')
    for name, proof in manifest['files'].items():
        path = training / name
        if sha(path) != proof['sha256'] or path.stat().st_size != proof['bytes']:
            raise ValueError('original training checkpoint dependency differs: ' + name)
    table_name = 'runtime-identity-v5/supplied-service-aliases-training.json'
    if (root / table_name).read_bytes() != (training / table_name).read_bytes():
        raise ValueError('frozen full alias table differs from closed training checkpoint')
    original_table = read(training / table_name)
    inventory = training / original_table['inventory']['path']
    if sha(inventory) != original_table['inventory']['sha256']:
        raise ValueError('original runtime inventory differs')
    table = build(read(inventory), inventory_proof=original_table['inventory'],
                  provided_roles=deployment_roles(training))
    db_path = training / 'observation-index.sqlite'
    db_sha = sha(db_path)
    with sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True) as db:
        db.execute('PRAGMA query_only=ON')
        counts = Counter()
        for status, original, encoded in db.execute(
                'SELECT status,original_service,resolution FROM runtime_identity_projection'):
            read_resolution = json.loads(encoded)
            identity = read_resolution.get('service_identity') or read_resolution.get('observed_runtime_service_identity') or {}
            counts[json.dumps({'status': status, 'original_service': original,
                              'verified_owner': identity,
                              'observed_runtime_compose_service': read_resolution.get('observed_runtime_compose_service')},
                             sort_keys=True)] += 1
        admission = admit_observed(SimpleNamespace(db=db, path=db_path, same_trace_parents=True),
                                   table, expected_source_prefix='ebpf-' + cell['collector'])
    models = []
    for path in sorted((root / 'toolchain/discovery').glob('*/*/observed.bering-raw.json')):
        quality_path = path.with_name('observed.bering-raw.quality.json')
        quality = read(quality_path) if quality_path.is_file() else {}
        raw = read(path)
        effective, _, proof = semantic_view(raw, quality, table, admission['aliases'])
        if [e['id'] for e in raw.get('edges', [])] != [e['id'] for e in effective.get('edges', [])]:
            raise ValueError('provided names changed edge membership')
        models.append({'path': path.relative_to(root).as_posix(),
                       'raw_services': raw.get('services'), 'effective_services': effective.get('services'),
                       'raw_edges': raw.get('edges'), 'effective_edges': effective.get('edges'),
                       'raw_endpoints': raw.get('endpoints'), 'effective_endpoints': effective.get('endpoints'),
                       'application': proof})
    if sha(db_path) != db_sha or any(sha(root / name) != digest for name, digest in verified.items()):
        raise ValueError('saved inputs changed during read-only inspection')
    output = {'cell': cell, 'provided_table': table, 'aliases': admission['aliases'],
              'conflicts': admission['conflicts'], 'runtime_projection_counts': dict(counts),
              'verified_source_segments': admission['unique_verified_segments'],
              'derived_source_occurrences': sum(proof.get('source_representation') == 'derived_otlp_json'
                                                for proof in admission['occurrence_proofs']),
              'verified_occurrences': len(admission['occurrence_proofs']),
              'models': models, 'original_database_sha256': db_sha,
              'original_training_manifest_sha256': ready['manifest_sha256'],
              'alias_admission_uses_closed_training_prefix_only': True,
              'frozen_file_sha256_verified_before_and_after': verified,
              'new_forecasts_refit_replay_simulation_or_scoring': False,
              'elapsed_seconds': time.monotonic() - started, 'human_preparation_seconds': None}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2) + '\n')


def audit(source, cell, out, *, provided_roles=False):
    started = time.monotonic()
    root = source / 'unpacked'
    for role in (('full', 'compact', 'training') if provided_roles else ('full', 'compact')):
        metadata = read(source / (role + '-api.json'))
        if ({k: metadata[k] for k in cell[role]} != cell[role]
                or metadata['workflow_run']['id'] != cell['run_id']
                or metadata['workflow_run']['head_sha'] != cell['head_sha']
                or metadata.get('expired') is not False
                or (source / (role + '.zip')).stat().st_size != cell[role]['size_in_bytes']
                or sha(source / (role + '.zip')) != cell[role]['digest'].removeprefix('sha256:')):
            raise ValueError('original artifact identity/digest differs')
    for role in (('full', 'training') if provided_roles else ('full',)):
        with zipfile.ZipFile(source / (role + '.zip')) as archive:
            names = archive.namelist()
            if len(set(names)) != len(names):
                raise ValueError('duplicate source member')
            for item in archive.infolist():
                name = PurePosixPath(item.filename)
                if name.is_absolute() or '..' in name.parts or '\\' in item.filename or stat.S_ISLNK(item.external_attr >> 16):
                    raise ValueError('unsafe source member')
            archive.extractall(root if role == 'full' else source / 'training')
    freeze = read(root / 'freeze-integrity.json')
    if not freeze.get('all_unchanged'):
        raise ValueError('source freeze is not intact')
    with zipfile.ZipFile(source / 'compact.zip') as compact:
        manifest = json.loads(compact.read('evaluation-manifest.json'))
        if manifest['commit'] != cell['head_sha'] or manifest['run_id'] != str(cell['run_id']):
            raise ValueError('compact capture identity differs')
        for name in ('freeze-integrity.json', 'toolchain/forecasts.json'):
            body = compact.read(name)
            if (hashlib.sha256(body).hexdigest() != manifest['files_sha256'][name]
                    or body != (root / name).read_bytes()):
                raise ValueError('compact/full original frozen outputs differ')
    verified = {}
    for name, expected in freeze['sha256_by_path'].items():
        if name.startswith(('toolchain/inputs/native/', 'toolchain/discovery/native/', 'toolchain/native/')):
            if sha(root / name) != expected:
                raise ValueError('frozen native scientific input differs: ' + name)
            verified[name] = expected
    required = {f'toolchain/discovery/native/{variant}/observed.json'
                for variant in ('raw', 'network_scope')}
    required.update(f'toolchain/native/{variant}/{operation}/{name}.json'
                    for variant in ('raw', 'network_scope') for operation in CONTRACTS
                    for name in ('entry-evidence', 'binding', 'forecast'))
    if not required <= verified.keys():
        raise ValueError('used model/root/binding/forecast is absent from pre-target freeze')
    if provided_roles:
        for name, expected in freeze['sha256_by_path'].items():
            if name.startswith(('runtime-identity-v5/supplied-service-alias', 'toolchain/discovery/')):
                if sha(root / name) != expected:
                    raise ValueError('frozen alias/model input differs: ' + name)
                verified[name] = expected
        return audit_provided_roles(root, source / 'training', cell, out, started, verified)
    original_api = read(source / 'old-binding-api.json')
    original = base64.b64decode(original_api['content'])
    if (hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest() != original_api['sha']
            or original_api['html_url'] != 'https://github.com/a-a-k/ebpf-model-discovery-experiments/blob/'
                + cell['head_sha'] + '/src/ebpf_discovery/binding_v5.py'):
        raise ValueError('old binding source is not the declared capture revision')
    namespace = {'__name__': 'ebpf_discovery.saved_binding_v5', '__package__': 'ebpf_discovery'}
    exec(compile(original, 'saved-binding-v5', 'exec'), namespace)
    old_binding = namespace['endpoint_alias_evidence']
    pairs = []
    for variant in ('raw', 'network_scope'):
        model = read(root / f'toolchain/discovery/native/{variant}/observed.json')
        for operation, contract in CONTRACTS.items():
            folder = root / f'toolchain/native/{variant}/{operation}'
            entry = read(folder / 'entry-evidence.json')
            binding = read(folder / 'binding.json')
            store = SavedRoots(root, entry['roots'])
            for step in contract['steps']:
                arguments = (store, entry['roots'], step, binding['entry_service'], model['endpoints'])
                before = json.dumps(arguments[1:], sort_keys=True)
                old = old_binding(*arguments)
                new = endpoint_alias_evidence(*arguments)
                if before != json.dumps(arguments[1:], sort_keys=True):
                    raise ValueError('binding comparison mutated its frozen arguments')
                pairs.append({'variant': variant, 'operation': operation, 'step': step,
                              'old': old, 'new': new, 'raw_roots_reverified': len(store.rows),
                              'original_forecast': read(folder / 'forecast.json')})
    if any(sha(root / name) != expected for name, expected in verified.items()):
        raise ValueError('saved files changed during pure binding inspection')
    result = {'cell': cell, 'frozen_file_sha256_verified_before_and_after': verified,
              'original_binding_source_sha256': hashlib.sha256(original).hexdigest(),
              'new_binding_source_sha256': sha(Path(__file__).parents[1] / 'src/ebpf_discovery/binding_v5.py'),
              'pairs': pairs, 'traffic_replay_refit_simulation_or_scoring': False,
              'new_pre_target_forecasts_claimed': False,
              'elapsed_seconds': time.monotonic() - started,
              'cost_boundary': 'pure saved-binding inspection only; Actions downloads/CI and early stops retained separately',
              'human_preparation_seconds': None}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--cell', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--provided-roles', action='store_true')
    parser.add_argument('--semantic-metadata', action='store_true')
    args = parser.parse_args()
    if args.semantic_metadata:
        if args.provided_roles:
            parser.error('choose only one saved audit mode')
        audit_semantic_metadata(args.source, read(args.cell), args.out)
    else:
        audit(args.source, read(args.cell), args.out, provided_roles=args.provided_roles)
