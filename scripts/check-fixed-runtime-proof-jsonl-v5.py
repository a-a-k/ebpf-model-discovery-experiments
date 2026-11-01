"""Actions-only exact ordered-proof encoding comparison on the fixed saved prefix."""
import argparse
import gc
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time
import zipfile

import ijson
import requests

from ebpf_discovery import checkpoint_v4 as checkpoint
from ebpf_discovery import remote_toolchain_v4 as remote

RUN = 41273870033
ARTIFACT = 13075276795
SOURCE = '06d7d52bfa4b7768a4cabf02f4e66f109b3a9492'
BASE = 'c1369df7b579f9a4c73e9ebc7df63a9d6eef6349'
DIGEST = 'sha256:22d706c5099c16203cef5f407273a067042a1def970ab4e3d72d3e362422d555'
MANIFEST = '5aad17e431831e4deb7a046af03fdf8b39249e89ade6b67c86c87dabfc745749'


def load_old(name):
    path = Path('work/runtime-proof-jsonl-scratch') / (name + '-original.py')
    path.write_bytes(subprocess.check_output(['git', 'show', f'{BASE}:src/ebpf_discovery/{name}.py']))
    spec = importlib.util.spec_from_file_location('ebpf_discovery._jsonl_original_' + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def arm(variant, source, destination, metadata, output):
    started = time.monotonic_ns()
    destination.mkdir(exist_ok=False)
    # The index is immutable; the dependency copier writes to distinct files.
    os.link(source/'observation-index.sqlite', destination/'observation-index.sqlite')
    copied = {}
    manifest = remote._read(metadata)
    if variant == 'original_array':
        module = load_old('checkpoint_v4')
        records = module._runtime_observation_dependencies(source, destination, copied)
        manifest['runtime_observation_dependencies'] = records
    else:
        reference = checkpoint._write_runtime_observation_dependencies(source, destination, copied)
        assert reference is not None
        manifest['runtime_observation_dependencies_jsonl'] = reference
    assert all(record == manifest['files'][name] for name, record in copied.items()
               if name != checkpoint.RUNTIME_DEPENDENCIES_FILE)
    for name in manifest['files']:
        target = destination/name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            os.link(source/name, target)
    if variant != 'original_array':
        manifest['files'][checkpoint.RUNTIME_DEPENDENCIES_FILE] = copied[checkpoint.RUNTIME_DEPENDENCIES_FILE]
    checkpoint._atomic_json(destination/'manifest.json', manifest)
    ready = {**manifest['identity'], 'status': 'training_checkpoint_ready',
             'manifest_sha256': remote._sha(destination/'manifest.json')}
    checkpoint._atomic_json(destination/'ready.json', ready)
    if variant == 'original_array':
        del records
    del manifest
    gc.collect()
    producer_seconds = (time.monotonic_ns() - started) / 1e9
    expected = {key: ready[key] for key in remote.IDENTITY_KEYS}
    checked, proof = remote._validate_checkpoint(destination, expected)
    del checked
    validation_seconds = (time.monotonic_ns() - started) / 1e9 - producer_seconds
    if variant != 'original_array':
        legacy, legacy_proof = load_old('remote_toolchain_v4')._validate_checkpoint(destination, expected)
        assert legacy_proof == proof
        del legacy, legacy_proof
    files = proof['files'].copy()
    files.pop(checkpoint.RUNTIME_DEPENDENCIES_FILE, None)
    expected_files = {name: {key: value[key] for key in ('bytes', 'sha256')}
                      for name, value in remote._read(metadata)['files'].items()}
    assert files == expected_files
    index_proof = remote._index_table_proof(destination/'observation-index.sqlite')
    report = {'variant': variant, 'producer_copy_encode_seconds': producer_seconds,
        'first_current_validator_seconds': validation_seconds,
        'total_seconds_including_legacy_validator_and_SQL_proof': (time.monotonic_ns() - started) / 1e9,
        'max_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'original_payload_files': len(files), 'all_original_file_bytes_and_hashes_equal': True,
        'ordered_original_file_proofs_sha256': hashlib.sha256(canonical(files)).hexdigest(),
        'logical_index_proof': index_proof, 'manifest_bytes': (destination/'manifest.json').stat().st_size,
        'manifest_sha256': ready['manifest_sha256'],
        'proof_file_bytes': ((destination/checkpoint.RUNTIME_DEPENDENCIES_FILE).stat().st_size
                             if variant != 'original_array' else None),
        'conversion_control_not_original_uploaded_artifact': True}
    remote._atomic_json(output, report)


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    started = time.monotonic_ns()
    out = Path('work/runtime-proof-jsonl-proof').resolve()
    out.mkdir(exist_ok=True)
    scratch = Path('work/runtime-proof-jsonl-scratch').resolve()
    scratch.mkdir(exist_ok=False)
    session, headers = requests.Session(), remote._headers(os.environ['GH_TOKEN'])
    artifact = remote._get(session, f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{ARTIFACT}", headers).json()
    assert (artifact['id'], artifact['digest'], artifact['expired']) == (ARTIFACT, DIGEST, False)
    assert artifact['workflow_run']['id'] == RUN and artifact['workflow_run']['head_sha'] == SOURCE
    assert artifact['name'] == f'training-v4-otel_demo-absent-6-{RUN}'
    remote._atomic_json(out/'original-artifact-api.json', artifact)
    archive = scratch/'original.zip'
    digest = remote._download(session, artifact['archive_download_url'], headers, archive)
    assert 'sha256:' + digest == DIGEST and archive.stat().st_size == artifact['size_in_bytes']
    with zipfile.ZipFile(archive) as bundle:
        uncompressed = sum(row.file_size for row in bundle.infolist())
    assert shutil.disk_usage(scratch).free > 3 * uncompressed + 4 * 1024**3
    source = scratch/'original'
    remote._safe_extract(archive, source)
    assert remote._sha(source/'manifest.json') == MANIFEST
    ready = remote._read(source/'ready.json')
    expected = {key: ready[key] for key in remote.IDENTITY_KEYS}
    assert expected == {'run_id': str(RUN), 'commit': SOURCE, 'system': 'otel_demo',
                        'mode': 'absent', 'seed': 6, 'manifest_sha256': MANIFEST}
    manifest, proof = remote._validate_checkpoint(source, expected)
    assert isinstance(manifest.pop('runtime_observation_dependencies'), list)
    metadata = scratch/'manifest-without-runtime-array.json'
    remote._atomic_json(metadata, manifest)
    del manifest, proof
    gc.collect()
    results = {}
    for variant in ('original_array', 'ordered_jsonl'):
        result_path = out/(variant + '.json')
        subprocess.run(['/usr/bin/time', '-v', '-o', str(out/(variant + '-time.txt')),
            sys.executable, str(Path(__file__).resolve()), '--arm', variant,
            '--source', str(source), '--destination', str(scratch/variant),
            '--metadata', str(metadata), '--output', str(result_path)], check=True)
        results[variant] = remote._read(result_path)
    assert results['original_array']['logical_index_proof'] == results['ordered_jsonl']['logical_index_proof']
    assert results['original_array']['ordered_original_file_proofs_sha256'] == results['ordered_jsonl']['ordered_original_file_proofs_sha256']
    count, record_digest = 0, hashlib.sha256()
    with (source/'manifest.json').open('rb') as original, (scratch/'original_array/manifest.json').open('rb') as old, (scratch/'ordered_jsonl'/checkpoint.RUNTIME_DEPENDENCIES_FILE).open(encoding='utf-8') as new:
        original_records = ijson.items(original, 'runtime_observation_dependencies.item', use_float=True)
        old_records = ijson.items(old, 'runtime_observation_dependencies.item', use_float=True)
        new_records = (json.loads(line) for line in new)
        for before, regenerated, after in itertools.zip_longest(original_records, old_records, new_records):
            encoded = canonical(before)
            assert before is not None and encoded == canonical(regenerated) == canonical(after)
            record_digest.update(encoded + b'\n')
            count += 1
    assert count > 0
    final = remote._get(session, f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{ARTIFACT}", headers).json()
    assert final['digest'] == DIGEST and final['expired'] is False
    remote._atomic_json(out/'proof.json', {'implementation_commit': os.environ['GITHUB_SHA'],
        'original_artifact': artifact, 'whole_original_archive_sha256_verified': digest,
        'original_manifest_sha256': MANIFEST, 'baseline_source': BASE,
        'ordered_every_record_equal_saved_vs_original_generator_vs_new_JSONL': True,
        'record_count': count, 'canonical_ordered_records_sha256': record_digest.hexdigest(),
        'comparisons': results, 'all_original_payloads_and_logical_SQL_proofs_equal': True,
        'new_checkpoint_verified_by_current_and_legacy_validators': True,
        'converted_manifest_ready_and_JSONL_are_labelled_controls_not_old_artifact_members': True,
        'uploaded_copy_release_new_traffic_models_simulations_scores_or_case_admission': False,
        'all_preparation_and_old_new_costs_retained_human_unknown': True,
        'six_hour_cure_or_full81_scientific_success_proven': False,
        'total_seconds_including_download_validation_comparison': (time.monotonic_ns() - started) / 1e9})
    shutil.rmtree(scratch)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arm', choices=('original_array', 'ordered_jsonl'))
    for name in ('source', 'destination', 'metadata', 'output'):
        parser.add_argument('--' + name, type=Path)
    args = parser.parse_args()
    if args.arm:
        arm(args.arm, args.source, args.destination, args.metadata, args.output)
    else:
        main()
