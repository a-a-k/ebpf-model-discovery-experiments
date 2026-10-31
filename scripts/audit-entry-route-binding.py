"""Inspect fixed saved bindings, supplied roles, or operation metadata.

The explicit semantic-metadata and context-baseline modes run diagnostic tools;
neither creates a primary forecast or scores application outcomes.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
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


def context_training_root(cell, workspace):
    """Restore only at the actual checkpoint locator root, inside this workspace."""
    expected = Path(workspace).resolve() / 'work/campaign'
    if Path(cell['original_root']).resolve() != expected:
        raise ValueError('closed training root is not this workspace/work/campaign')
    if expected.exists() and any(expected.iterdir()):
        raise ValueError('closed training restore destination is not empty')
    return expected


def context_input_sequence(manifest):
    """Verify complete retained HTTP bodies in original group/request order."""
    from ebpf_discovery.bering_v4 import _ordered_manifest_requests, _request_manifests
    sequence = []
    for group in _request_manifests(manifest):
        for export, body in _ordered_manifest_requests(group, materialize=False):
            if body is None:
                path = Path(export['path'])
                length, digest = path.stat().st_size, sha(path)
            else:
                digest_value, length = hashlib.sha256(), 0
                try:
                    while chunk := body.read(1024 * 1024):
                        digest_value.update(chunk)
                        length += len(chunk)
                finally:
                    body.close()
                digest = digest_value.hexdigest()
                if length != export['length']:
                    raise ValueError('streamed diagnostic input length differs')
            if digest != export['sha256'] or export['source'] not in ('native', 'ebpf'):
                raise ValueError('diagnostic input bytes or original emitter role differs')
            sequence.append({'source': export['source'], 'bytes': length, 'sha256': digest,
                             'content_type': export['content_type'],
                             'content_encoding': export.get('content_encoding') or ''})
    return sequence


def context_accepted_sequence(root, runtime, expected, *, joint):
    command = read(root / runtime / 'replay-command.json')
    proof = command['accepted_request_sequence']
    path = root / runtime / 'accepted-request-sequence.jsonl'
    if (command.get('status') != 'complete' or command.get('returncode') != 0
            or Path(proof['path']) != path or sha(path) != proof['sha256']
            or path.stat().st_size != proof['bytes']):
        raise ValueError('actual diagnostic accepted sequence identity differs')
    body = path.read_bytes()
    rows = [json.loads(line) for line in body.splitlines()]
    if not body.endswith(b'\n') or len(rows) != proof['requests'] or len(rows) != len(expected):
        raise ValueError('actual diagnostic accepted sequence count differs')
    for i, (row, wire) in enumerate(zip(rows, expected)):
        endpoint = '/v1/traces' if joint or wire['source'] == 'native' else '/sources/ebpf/v1/traces'
        if (row['http_status'] != 200 or row['export_index'] != i or row['endpoint'] != endpoint
                or row['content_bytes'] != wire['bytes'] or row['content_sha256'] != wire['sha256']
                or (joint and row.get('original_source') != wire['source'])):
            raise ValueError('actual diagnostic ingest changed request bytes/order/role')
    return {'path': str(path), 'sha256': sha(path), 'requests': len(rows),
            'bytes': len(body), 'same_original_wire_order_and_roles': True}


def audit_context_baseline(source, cell, out):
    """New paired diagnostic only; original closed training and forecasts stay intact."""
    from collections import defaultdict
    import importlib
    from ebpf_discovery.bering_v4 import child_go_environment
    from ebpf_discovery.remote_toolchain_v4 import (
        _safe_extract, _validate_checkpoint, _verify_binaries, _make_binaries_executable,
        _readonly_store, _index_table_proof, WORKER_BERING_GO_ENV)
    from ebpf_discovery.runtime import Context, write_json
    from ebpf_discovery.store_v5 import ObservationStoreV5
    from ebpf_discovery.toolchain_v5 import Toolchain, PINS
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('saved paired diagnostic execution is Actions only')
    started = time.monotonic()
    source, out = source.resolve(), out.resolve()
    destination = out.parent / 'context-baseline'
    destination.mkdir(parents=True, exist_ok=False)
    original, artifacts = source / 'frozen-toolchain', {}
    original.mkdir(exist_ok=False)
    for role in ('full', 'compact', 'training'):
        metadata, expected = read(source / (role + '-api.json')), cell[role]
        archive_path = source / (role + '.zip')
        if ({key: metadata[key] for key in expected} != expected
                or metadata['workflow_run']['id'] != cell['run_id']
                or metadata['workflow_run']['head_sha'] != cell['head_sha']
                or metadata.get('expired') is not False
                or archive_path.stat().st_size != expected['size_in_bytes']
                or sha(archive_path) != expected['digest'].removeprefix('sha256:')):
            raise ValueError('original paired audit artifact differs: ' + role)
        artifacts[role] = metadata
    with (zipfile.ZipFile(source / 'full.zip') as full,
          zipfile.ZipFile(source / 'compact.zip') as compact):
        manifest = json.loads(compact.read('evaluation-manifest.json'))
        if manifest['commit'] != cell['head_sha'] or manifest['run_id'] != str(cell['run_id']):
            raise ValueError('original paired compact identity differs')
        for name in ('freeze-integrity.json', 'toolchain/forecasts.json'):
            body = compact.read(name)
            if (hashlib.sha256(body).hexdigest() != manifest['files_sha256'][name]
                    or body != full.read(name)):
                raise ValueError('original paired full/compact freeze or forecasts differs')
        freeze = json.loads(compact.read('freeze-integrity.json'))
        if not freeze['all_unchanged']:
            raise ValueError('original paired source freeze was not intact')
        names = full.namelist()
        if len(names) != len(set(names)):
            raise ValueError('duplicate original paired full member')
        frozen = {name: digest for name, digest in freeze['sha256_by_path'].items()
                  if name.startswith('toolchain/')}
        if not frozen or any(name.startswith('toolchain/context-baseline/') for name in frozen):
            raise ValueError('diagnostic source already contains paired output or lacks original toolchain')
        for name, digest in frozen.items():
            item = full.getinfo(name)
            relative = PurePosixPath(name)
            if ('..' in relative.parts or relative.is_absolute() or '\\' in name
                    or item.is_dir() or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError('unsafe frozen paired toolchain member')
            target = original / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with full.open(item) as stream, target.open('wb') as output:
                shutil.copyfileobj(stream, output)
            if sha(target) != digest:
                raise ValueError('original frozen paired toolchain digest differs: ' + name)
    training = source / 'closed-training'
    _safe_extract(source / 'training.zip', training)
    expected = {'run_id': str(cell['run_id']), 'commit': cell['head_sha'],
                'system': cell['system'], 'mode': cell['mode'], 'seed': cell['seed'],
                'manifest_sha256': cell['training_manifest_sha256']}
    checkpoint, input_proof = _validate_checkpoint(training, expected)
    restore = context_training_root(cell, os.environ['GITHUB_WORKSPACE'])
    for row in checkpoint['indexed_sources']:
        if Path(row['original_path']) != restore / row['relative_path']:
            raise ValueError('training source locator is outside the exact restored prefix')
    _safe_extract(source / 'training.zip', restore)
    _validate_checkpoint(restore, expected)
    if sha(training / 'toolchain-build/toolchain-build.json') != checkpoint['toolchain']['manifest_sha256']:
        raise ValueError('closed training binary manifest differs')
    binaries = _verify_binaries(restore, checkpoint, pins=PINS)
    for proof in checkpoint['toolchain']['binaries']:
        actual = binaries[proof['name']]
        if actual['bytes'] != proof['bytes'] or actual['sha256'] != proof['sha256']:
            raise ValueError('closed training declared binary differs')
    _make_binaries_executable(binaries)
    shutil.copytree(original / 'toolchain', restore / 'toolchain')
    static = read(restore / 'toolchain/static-inputs.json')
    declaration = importlib.import_module('systems.' + cell['system'] + '.experiment_v4')
    if (static['tool_pins'] != PINS or static['deployment'] != read(restore / 'deployment.json')
            or static['contracts'] != json.loads(json.dumps(declaration.CONTRACTS))):
        raise ValueError('paired diagnostic would use different supplied semantics or tool pins')
    # These original frozen alias dependencies must be the CLOSED training copies.
    for name in ('supplied-service-aliases-training.json', 'supplied-service-alias-admission-training.json'):
        relative = 'runtime-identity-v5/' + name
        if (freeze['sha256_by_path'].get(relative) != sha(training / relative)
                or (restore / relative).read_bytes() != (training / relative).read_bytes()):
            raise ValueError('full freeze alias dependency differs from closed training')
    before_index = _index_table_proof(restore / 'observation-index.sqlite')
    before_forecasts = (restore / 'toolchain/forecasts.json').read_bytes()
    ctx = Context(restore, cell['mode'], cell['seed'])
    ctx.command_log = destination / 'diagnostic-commands.jsonl'
    previous_bin = os.environ.get('PBS_BIN')
    os.environ['PBS_BIN'] = str(restore / 'toolchain-build/bin')
    store = _readonly_store(restore / 'observation-index.sqlite', ObservationStoreV5)
    sequences = {}
    try:
        toolchain = Toolchain(ctx, cell['system'], store, declaration, collector=cell['collector'])
        toolchain.entry_identity_groups = static['supplied_entry_identity_groups']
        toolchain.entry_evidence, toolchain.input_manifests = {}, {}
        toolchain.preflight_reports = defaultdict(list)
        for origin in ('native', 'ebpf'):
            for name, contract in declaration.CONTRACTS.items():
                for step in range(len(contract['steps'])):
                    path = restore / f'toolchain/procrustes/{origin}/{name}/{step}/report.json'
                    if path.relative_to(restore).as_posix() not in frozen:
                        raise ValueError('saved preflight report is not pre-target frozen')
                    toolchain.preflight_reports[origin, name].append(path)
        for emitter in ('native', 'ebpf', 'combined'):
            for name in declaration.CONTRACTS:
                entry = [read(restore / f'toolchain/{emitter}/{v}/{name}/entry-evidence.json')
                         for v in ('raw', 'network_scope')]
                if entry[0] != entry[1]:
                    raise ValueError('original variant entry evidence differs')
                toolchain.entry_evidence[emitter, name] = entry[0]
            for variant in ('raw', 'network_scope'):
                path = restore / f'toolchain/inputs/{emitter}/{variant}/observations.json'
                toolchain.input_manifests[emitter, variant] = (path, read(path))
                if emitter == 'combined':
                    sequence = context_input_sequence(read(path))
                    accepted = context_accepted_sequence(restore,
                        f'toolchain/discovery/combined/{variant}/observed-runtime', sequence, joint=False)
                    sequences[variant] = {'wire': sequence, 'original_accepted': accepted}
        with child_go_environment(WORKER_BERING_GO_ENV) as go_environment:
            write_json(destination / 'bering-go-environment.json', go_environment)
            toolchain.forecast_context_baseline(json.loads(before_forecasts))
    finally:
        store.close()
        if previous_bin is None:
            os.environ.pop('PBS_BIN', None)
        else:
            os.environ['PBS_BIN'] = previous_bin
        # Preserve actual partial commands/models even when a diagnostic tool fails.
        paired_output = restore / 'toolchain/context-baseline'
        if paired_output.exists():
            shutil.copytree(paired_output, destination / 'paired')
    for variant, evidence in sequences.items():
        evidence['joint_accepted'] = context_accepted_sequence(restore,
            f'toolchain/context-baseline/{variant}/joint/observed-runtime', evidence['wire'], joint=True)
        base = read(restore / f'toolchain/discovery/combined/{variant}/observed.json')
        union = read(restore / f'toolchain/context-baseline/{variant}/union-model.json')
        joint = read(restore / f'toolchain/context-baseline/{variant}/joint/canonical.json')
        proof = read(restore / f'toolchain/context-baseline/{variant}/union-proof.json')
        original_edges = {edge['id']: edge for edge in base['edges']}
        services = {service['id'] for service in base['services']}
        added = [edge for edge in joint['edges'] if edge['id'] not in original_edges
                 and (edge.get('identity') or {}).get('span_kind') == 'server'
                 and {edge['from'], edge['to']} <= services]
        if (set(union) != set(base) or any(union[k] != base[k] for k in base if k != 'edges')
                or union['edges'] != base['edges'] + added
                or [edge['id'] for edge in added] != proof['added_edge_ids']):
            raise ValueError('paired union changed base records or imported an unobserved edge')
        evidence.update(added_edge_ids=proof['added_edge_ids'],
                        semantic_identity_conflicts=proof['semantic_identity_conflicts'],
                        joint_alias_metadata_collisions=proof['joint_alias_metadata_collisions'],
                        complete_original_model_records_preserved=True)
    paired = restore / 'toolchain/context-baseline'
    diagnostic_forecasts = read(paired / 'forecasts.json')
    executions = []
    for variant, forecasts in diagnostic_forecasts.items():
        provenance = read(paired / variant / 'provenance.json')
        if set(forecasts) != set(declaration.CONTRACTS):
            raise ValueError('diagnostic operation coverage changed')
        reused = provenance['status'] in ('reuse_single_source_equivalence', 'reuse_unchanged_union')
        if reused and forecasts != json.loads(before_forecasts)['combined'][variant]:
            raise ValueError('diagnostic reused forecast differs from original combined')
        for operation, forecast in forecasts.items():
            if not forecast['available'] or reused:
                continue
            folder = paired / variant / 'operations' / operation
            validate, simulation = (read(folder / (name + '.command.json'))
                                    for name in ('provided-metadata-validation', 'simulation'))
            if (forecast['simulator'] != 'Sheaft' or forecast['graph_sha256'] != sha(folder / 'model.json')
                    or forecast['analysis_sha256'] != sha(folder / 'analysis.json')
                    or validate['returncode'] != 0 or simulation['returncode'] != 0
                    or validate['argv'] != ['bering', 'validate', '--input', str(folder / 'model.json')]
                    or simulation['argv'] != ['sheaft', 'run', '--model', str(folder / 'model.json'),
                       '--analysis', str(folder / 'analysis.json'), '--out-dir', str(folder / 'simulation')]
                    or not (folder / 'simulation/report.json').is_file()):
                raise ValueError('available diagnostic forecast lacks its actual pinned model execution')
            executions.append({'variant': variant, 'operation': operation,
                               'model_sha256': forecast['graph_sha256'],
                               'validation_command_sha256': sha(folder / 'provided-metadata-validation.command.json'),
                               'simulation_command_sha256': sha(folder / 'simulation.command.json'),
                               'simulation_report_sha256': sha(folder / 'simulation/report.json')})
    after_checkpoint, after = _validate_checkpoint(restore, expected, allow_toolchain=True)
    _validate_checkpoint(training, expected)
    if (after_checkpoint != checkpoint or after != input_proof
            or _index_table_proof(restore / 'observation-index.sqlite') != before_index
            or (restore / 'toolchain/forecasts.json').read_bytes() != before_forecasts
            or any(sha(restore / name) != digest or sha(original / name) != digest
                   for name, digest in frozen.items())):
        raise ValueError('original closed prefix or scientific file changed during paired diagnostic')
    write_json(out, {'cell': cell, 'artifact_api': artifacts, 'training_input_proof': input_proof,
        'training_index_table_proof': before_index, 'checkpoint_binary_proofs': binaries,
        'original_frozen_toolchain_sha256_verified_before_and_after': frozen,
        'original_forecasts_sha256': hashlib.sha256(before_forecasts).hexdigest(),
        'paired_forecasts': diagnostic_forecasts, 'sequences': sequences, 'actual_executions': executions,
        'path_relocations': [], 'restored_exact_original_root': str(restore),
        'final_full_database_extracted_or_used': False, 'closed_training_only': True,
        'new_application_traffic_or_external_outcome_scoring': False,
        'new_pre_target_primary_forecast_claimed': False, 'diagnostic_discovery_and_simulation_only': True,
        'elapsed_seconds': time.monotonic() - started, 'human_preparation_seconds': None})


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
    parser.add_argument('--context-baseline', action='store_true')
    args = parser.parse_args()
    if sum((args.semantic_metadata, args.provided_roles, args.context_baseline)) > 1:
        parser.error('choose only one saved audit mode')
    if args.context_baseline:
        audit_context_baseline(args.source, read(args.cell), args.out)
    elif args.semantic_metadata:
        audit_semantic_metadata(args.source, read(args.cell), args.out)
    else:
        audit(args.source, read(args.cell), args.out, provided_roles=args.provided_roles)
