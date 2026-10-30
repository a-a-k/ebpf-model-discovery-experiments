"""Compare pure endpoint binding on frozen native roots; no simulation or scoring."""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import sqlite3
import time
from types import SimpleNamespace
import zipfile

from ebpf_discovery.binding_v5 import endpoint_alias_evidence
from ebpf_discovery.store_v3 import normalized_file
from ebpf_discovery.store_v5 import _digest
from systems.petclinic.experiment_v4 import CONTRACTS


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


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
              'verified_receiver_segments': admission['unique_verified_segments'],
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
    args = parser.parse_args()
    audit(args.source, read(args.cell), args.out, provided_roles=args.provided_roles)
