"""Extract the already published, pinned model example; never rebuild a model."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
import zipfile

from ebpf_discovery.publication_archive import GitHub, require
from ebpf_discovery.compact_publication import EXAMPLE_PINS, EXAMPLE_RUN, EXAMPLE_SOURCE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    require(os.environ.get('GITHUB_ACTIONS') == 'true', 'scientific extraction runs in Actions')
    args.out.mkdir(parents=True, exist_ok=True)
    args.cache.mkdir(parents=True, exist_ok=True)
    aid, size, sha = EXAMPLE_PINS['model']
    gh = GitHub()
    meta = gh.json(f'actions/artifacts/{aid}')
    require((meta['id'], meta['size_in_bytes'], meta['digest'], meta['expired']) ==
            (aid, size, 'sha256:' + sha, False), 'selected model artifact identity differs')
    require(meta['workflow_run']['id'] == EXAMPLE_RUN and
            meta['workflow_run']['head_sha'] == EXAMPLE_SOURCE, 'selected producing source differs')
    path = args.cache / 'selected-model.zip'
    gh.download(f'actions/artifacts/{aid}/zip', path, size, sha)
    keep_names = {'binding.json', 'forecast.json', 'model.json', 'overlay.json',
                  'predicates.json', 'analysis.json', 'provided-metadata-attachment.json',
                  'report.json', 'observed-reference.json', 'input-reference.json'}
    extracted = {}
    with zipfile.ZipFile(path) as archive:
        require(set(archive.namelist()) == {'model.tar.gz', 'model.tar.gz.json'}, 'ZIP members differ')
        require(archive.testzip() is None, 'model ZIP CRC failure')
        inventory = json.loads(archive.read('model.tar.gz.json'))
        h, n = hashlib.sha256(), 0
        with archive.open('model.tar.gz') as incoming:
            for block in iter(lambda: incoming.read(1024**2), b''):
                h.update(block)
                n += len(block)
        require((n, h.hexdigest()) == (inventory['bytes'], inventory['sha256']),
                'nested model TAR identity differs')
        chosen = {name: item for name, item in inventory['files'].items()
                  if ((name.startswith('toolchain/ebpf/network_scope/') and
                       PurePosixPath(name).name in keep_names) or
                      name in ('status.json', 'deployment.json', 'v6-block-reference.json'))
                  and item['bytes'] <= 10_000_000}
        require(chosen and sum(v['bytes'] for v in chosen.values()) <= 25_000_000,
                'selected small model files missing or exceed publication bound')
        with archive.open('model.tar.gz') as incoming, tarfile.open(fileobj=incoming, mode='r|gz') as tar:
            for member in tar:
                if member.name not in chosen:
                    continue
                relative = PurePosixPath(member.name)
                require(member.isfile() and not relative.is_absolute() and '..' not in relative.parts,
                        'unsafe selected model member')
                require(member.name not in extracted and member.size == chosen[member.name]['bytes'],
                        'selected member duplicated or size differs')
                body = tar.extractfile(member).read()
                digest = hashlib.sha256(body).hexdigest()
                require(digest == chosen[member.name]['sha256'], 'selected member SHA differs')
                target = args.out / 'selected-example' / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
                extracted[member.name] = {'bytes': len(body), 'sha256': digest}
        require(set(extracted) == set(chosen), 'missing selected nested model members')
    for operation in ('browse_product', 'add_to_cart', 'checkout'):
        require(any(name.endswith('/' + operation + '/forecast.json') for name in extracted),
                'missing operation forecast ' + operation)
    receipt = {'key': ['otel_demo', 'absent', 9, 'obi'], 'producing_source': EXAMPLE_SOURCE,
               'producing_run': EXAMPLE_RUN, 'original_artifact': meta,
               'model_archive_sha256': inventory['sha256'], 'selected_files': extracted,
               'model_rebuild_executed': False, 'new_measurements_executed': False,
               'selection_purpose': 'Existing case already included in the Zenodo worked example.',
               'reader_source': os.environ['GITHUB_SHA'], 'reader_run': os.environ['GITHUB_RUN_ID']}
    (args.out / 'selected-example-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'selected_example_files': len(extracted), 'selected_example_bytes':
                     sum(v['bytes'] for v in extracted.values()), 'model_rebuild_executed': False}))


if __name__ == '__main__':
    main()
