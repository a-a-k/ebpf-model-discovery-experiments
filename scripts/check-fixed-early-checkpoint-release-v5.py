"""Actions-only replay of the checkpoint/consistent-backup allocation order."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time
import zipfile

import requests

from ebpf_discovery import remote_toolchain_v4 as remote

RUN = 41273870033
ARTIFACT = 13075276795
SOURCE = '06d7d52bfa4b7768a4cabf02f4e66f109b3a9492'
DIGEST = 'sha256:22d706c5099c16203cef5f407273a067042a1def970ab4e3d72d3e362422d555'
MANIFEST = '5aad17e431831e4deb7a046af03fdf8b39249e89ade6b67c86c87dabfc745749'
MIB = 1024 * 1024


def command(*args):
    subprocess.run(args, check=True, capture_output=True)


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true' and os.geteuid() == 0
    started = time.monotonic_ns()
    out = Path('work/early-checkpoint-release-proof').resolve()
    out.mkdir(exist_ok=True)
    scratch = Path('work/early-checkpoint-release-scratch').resolve()
    scratch.mkdir(exist_ok=False)
    source, mount = scratch / 'original', scratch / 'mounted'
    mount.mkdir()
    session, headers = requests.Session(), remote._headers(os.environ['GH_TOKEN'])
    repository = os.environ['GITHUB_REPOSITORY']
    artifact = remote._get(session, f'https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}', headers).json()
    assert (artifact['id'], artifact['digest'], artifact['expired']) == (ARTIFACT, DIGEST, False)
    assert artifact['workflow_run']['id'] == RUN and artifact['workflow_run']['head_sha'] == SOURCE
    assert artifact['name'] == f'training-v4-otel_demo-absent-6-{RUN}'
    remote._atomic_json(out / 'original-artifact-api.json', artifact)
    archive = scratch / 'original.zip'
    digest = remote._download(session, artifact['archive_download_url'], headers, archive)
    assert 'sha256:' + digest == DIGEST and archive.stat().st_size == artifact['size_in_bytes']
    with zipfile.ZipFile(archive) as bundle:
        uncompressed = sum(row.file_size for row in bundle.infolist())
    assert shutil.disk_usage(scratch).free > 3 * uncompressed + 4 * 1024**3
    remote._safe_extract(archive, source)
    ready = remote._read(source / 'ready.json')
    assert ready['manifest_sha256'] == MANIFEST
    expected = {key: ready[key] for key in remote.IDENTITY_KEYS}
    assert (str(expected['run_id']), expected['commit'], expected['system'], expected['mode'], int(expected['seed'])) == (str(RUN), SOURCE, 'otel_demo', 'absent', 6)
    expected.update(artifact_id=str(ARTIFACT), artifact_name=artifact['name'], artifact_digest=DIGEST)
    original_manifest, original_proof = remote._validate_checkpoint(source, expected)
    del original_manifest
    original_index = remote._index_table_proof(source / 'observation-index.sqlite')
    database_bytes = (source / 'observation-index.sqlite').stat().st_size
    assert database_bytes == 14255300608
    payload_physical = sum((source / name).stat().st_blocks * 512 for name in original_proof['files'])
    checkpoint_physical = sum(p.stat().st_blocks * 512 for p in source.rglob('*') if p.is_file())
    image_bytes = ((payload_physical + checkpoint_physical + database_bytes // 2 + 2 * 1024**3 + MIB - 1) // MIB) * MIB
    image = scratch / 'case.ext4'
    pristine = scratch / 'empty-pristine.ext4'
    with pristine.open('xb') as stream:
        stream.truncate(image_bytes)
    command('mkfs.ext4', '-q', '-F', '-m', '0', str(pristine))
    results = {}
    for method in ('late_release_after_live_backup', 'early_release_before_live_backup'):
        # Reuse the same empty filesystem bytes, UUID and directory-hash seed.
        # Bound even a fully allocated image against actual hosted free space.
        assert shutil.disk_usage(scratch).free > image_bytes + 1024**3
        command('cp', '--sparse=always', str(pristine), str(image))
        mounted, connection = False, None
        case_out = out / method
        case_out.mkdir()
        try:
            command('mount', '-o', 'loop,noatime', str(image), str(mount))
            mounted = True
            checkpoint, live = mount / 'training-checkpoint', mount / 'campaign'
            shutil.copytree(source, checkpoint)
            # This labelled upload-release control was not present in the old
            # saved ZIP and is never represented as recovered live evidence.
            remote._atomic_json(checkpoint / 'release.json', {**expected,
                'upload_success': True, 'qualification_control_only': True})
            manifest, proof = remote._validate_checkpoint(checkpoint, expected)
            del manifest
            assert proof == original_proof
            live.mkdir()
            for relative in proof['files']:
                destination = live / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(checkpoint / relative, destination)
            checkpoint_index = remote._index_table_proof(checkpoint / 'observation-index.sqlite')
            assert checkpoint_index == original_index
            connection = sqlite3.connect(f'file:{(live / "observation-index.sqlite").as_posix()}?mode=ro', uri=True)
            connection.execute('PRAGMA query_only=ON')
            os.sync()
            before = shutil.disk_usage(mount).free
            assert 0 < before < database_bytes
            metadata_before = {name: remote._sha(checkpoint / name) for name in ('manifest.json', 'ready.json', 'release.json')}
            release, failure, live_proof = None, None, None
            if method == 'early_release_before_live_backup':
                release = remote._release_uploaded_checkpoint_copy(checkpoint, live, expected, proof,
                    session, headers, repository, case_out)
                assert release['status'] == 'released_verified_local_payload'
            try:
                live_proof = remote._consistent_live_index_proof(connection, live / '.parent-index-before.sqlite')
            except sqlite3.Error as error:
                assert method == 'late_release_after_live_backup' and 'full' in str(error).lower()
                failure = {'type': type(error).__name__, 'message': str(error)}
            if method == 'late_release_after_live_backup':
                assert failure is not None
            else:
                assert failure is None and live_proof == checkpoint_index
                assert {p.name for p in checkpoint.iterdir()} == set(metadata_before)
                assert {name: remote._sha(checkpoint / name) for name in metadata_before} == metadata_before
                assert not (live / '.parent-index-before.sqlite').exists()
            connection.close()
            connection = None
            all_files_digest = hashlib.sha256()
            for relative, record in sorted(proof['files'].items()):
                path = live / relative
                observed = {'bytes': path.stat().st_size, 'sha256': remote._sha(path)}
                assert observed == record
                all_files_digest.update(json.dumps([relative, observed], sort_keys=True, separators=(',', ':')).encode() + b'\n')
            results[method] = {'initial_free_bytes': before, 'cleanup': release, 'backup_failure': failure,
                'original_checkpoint_index_proof': checkpoint_index, 'live_backup_proof': live_proof,
                'all_original_live_payloads_unchanged': True, 'payload_file_count': len(proof['files']),
                'ordered_named_payload_hashes_sha256': all_files_digest.hexdigest(),
                'retained_metadata_sha256': metadata_before,
                'labelled_synthetic_release_control_not_historical_recovery': True}
            remote._atomic_json(case_out / 'comparison.json', results[method])
        finally:
            if connection is not None:
                connection.close()
            if mounted:
                command('umount', str(mount))
            image.unlink(missing_ok=True)
    assert results['late_release_after_live_backup']['initial_free_bytes'] == results['early_release_before_live_backup']['initial_free_bytes']
    assert results['late_release_after_live_backup']['ordered_named_payload_hashes_sha256'] == results['early_release_before_live_backup']['ordered_named_payload_hashes_sha256']
    final = remote._get(session, f'https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}', headers).json()
    assert final['digest'] == DIGEST and final['expired'] is False
    shutil.rmtree(scratch)
    remote._atomic_json(out / 'proof.json', {'implementation_commit': os.environ['GITHUB_SHA'],
        'original_artifact': artifact, 'whole_archive_sha256_verified': digest,
        'manifest_sha256': MANIFEST, 'source_database_bytes': database_bytes,
        'filesystem_image_bytes': image_bytes, 'comparisons': results,
        'new_traffic_models_simulations_scores_worker_dispatch_or_case_admission': False,
        'new_caller_order_replayed_without_running_a_live_campaign': True,
        'current_live_free_space_or_full_case_sufficiency_proven': False,
        'total_seconds_including_download_validation_cleanup': (time.monotonic_ns() - started) / 1e9})


if __name__ == '__main__':
    main()
