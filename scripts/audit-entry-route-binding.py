"""Compare pure endpoint binding on frozen native roots; no simulation or scoring."""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import time
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


def audit(source, cell, out):
    started = time.monotonic()
    root = source / 'unpacked'
    for role in ('full', 'compact'):
        metadata = read(source / (role + '-api.json'))
        if ({k: metadata[k] for k in cell[role]} != cell[role]
                or metadata['workflow_run']['id'] != cell['run_id']
                or metadata['workflow_run']['head_sha'] != cell['head_sha']
                or metadata.get('expired') is not False
                or (source / (role + '.zip')).stat().st_size != cell[role]['size_in_bytes']
                or sha(source / (role + '.zip')) != cell[role]['digest'].removeprefix('sha256:')):
            raise ValueError('original artifact identity/digest differs')
    with zipfile.ZipFile(source / 'full.zip') as archive:
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise ValueError('duplicate source member')
        for item in archive.infolist():
            name = PurePosixPath(item.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in item.filename or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('unsafe source member')
        archive.extractall(root)
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
    args = parser.parse_args()
    audit(args.source, read(args.cell), args.out)
