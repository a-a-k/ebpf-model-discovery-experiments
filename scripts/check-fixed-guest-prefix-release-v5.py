"""Actions-only storage proof on both actual saved raw prefixes; no experiments."""
import errno
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

import requests

from ebpf_discovery import deepflow_snapshot_v5 as snapshot
from ebpf_discovery import remote_toolchain_v4 as remote

RUN = 41273434210
ARTIFACT = 13073478195
SOURCE = '06d7d52bfa4b7768a4cabf02f4e66f109b3a9492'
DIGEST = 'sha256:02c499bca37d3e5d91299234840cedf2132f499e16cee77fb1e5b6ee70b9ba99'
MANIFEST = '8b4af034ca142e7760f26dcfc64782baf3a134550df90cb138cfee0dcd60bfdf'
MIB = 1024 * 1024


def command(*args):
    subprocess.run(args, check=True, capture_output=True)


def append_fixture(original, target, offset, length):
    with original.open('rb') as source, target.open('ab') as destination:
        source.seek(offset)
        while length:
            chunk = source.read(min(MIB, length))
            assert chunk
            destination.write(chunk)
            length -= len(chunk)
        destination.flush()
        os.fsync(destination.fileno())


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true' and os.geteuid() == 0
    started = time.monotonic_ns()
    out = Path('work/guest-prefix-release-proof').resolve()
    out.mkdir(exist_ok=True)
    scratch = Path('work/guest-prefix-release-scratch').resolve()
    scratch.mkdir(exist_ok=False)
    mount = scratch / 'mounted'
    mount.mkdir()
    session, headers = requests.Session(), remote._headers(os.environ['GH_TOKEN'])
    repository = os.environ['GITHUB_REPOSITORY']
    artifact = remote._get(session, f'https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}', headers).json()
    assert (artifact['id'], artifact['digest'], artifact['expired']) == (ARTIFACT, DIGEST, False)
    assert artifact['workflow_run']['id'] == RUN and artifact['workflow_run']['head_sha'] == SOURCE
    assert artifact['name'] == f'training-v4-otel_demo-partial-6-{RUN}'
    remote._atomic_json(out / 'original-artifact-api.json', artifact)
    archive = scratch / 'original.zip'
    digest = remote._download(session, artifact['archive_download_url'], headers, archive)
    assert 'sha256:' + digest == DIGEST and archive.stat().st_size == artifact['size_in_bytes']
    sources = {}
    with zipfile.ZipFile(archive) as bundle:
        assert len({e.filename for e in bundle.infolist()}) == len(bundle.infolist())
        import json
        ready = json.loads(bundle.read('ready.json'))
        assert ready['manifest_sha256'] == MANIFEST
        assert (str(ready['run_id']), ready['commit'], ready['system'], ready['mode'], int(ready['seed'])) == (str(RUN), SOURCE, 'otel_demo', 'partial', 6)
        manifest_hash = hashlib.sha256()
        with bundle.open('manifest.json') as stream:
            while chunk := stream.read(MIB):
                manifest_hash.update(chunk)
        assert manifest_hash.hexdigest() == MANIFEST
        for node, length in [('a', 1170778914), ('b', 117539976)]:
            prefix = f'observations/deepflow-raw/node-{node}/002-live-prefix/'
            saved = json.loads(bundle.read(prefix + 'snapshot.json'))
            assert saved['mode'] == 'prefix' and not saved['rotation_observed']
            row, = saved['files']
            assert row['snapshot_name'] == row['source_name'] == 'l7_flow_log' and row['copied_bytes'] == length
            source = scratch / f'original-{node}.raw'
            with bundle.open(prefix + 'l7_flow_log') as origin, source.open('xb') as destination:
                shutil.copyfileobj(origin, destination, MIB)
            assert source.stat().st_size == length and remote._sha(source) == row['copied_sha256']
            sources[node] = source
    results = {}
    for node, original in sources.items():
        length, source_sha = original.stat().st_size, remote._sha(original)
        image = scratch / 'case.ext4'
        image_bytes = ((3 * length + MIB - 1) // MIB) * MIB
        methods = {}
        original_manifest = None
        for method in ('keep_guest_duplicate', 'release_verified_guest_duplicate'):
            assert shutil.disk_usage(scratch).free > image_bytes + 2 * length + 512 * MIB
            with image.open('xb') as stream:
                stream.truncate(image_bytes)
            command('mkfs.ext4', '-q', '-F', '-m', '0', str(image))
            mounted = False
            try:
                command('mount', '-o', 'loop,noatime', str(image), str(mount))
                mounted = True
                data = mount / 'deepflow-v5.fixture' / 'data'
                data.mkdir(parents=True)
                live = data / 'l7_flow_log'
                shutil.copyfile(original, live)
                copied = data.parent / 'snapshots' / '002-live-prefix'
                snapshot.snapshot(data, copied, 'prefix')
                manifest_bytes = (copied / 'snapshot.json').read_bytes()
                if original_manifest is None:
                    original_manifest = manifest_bytes
                assert manifest_bytes == original_manifest
                parent = scratch / f'parent-import-{node}-{method}.raw'
                shutil.copyfile(copied / 'l7_flow_log', parent)
                parent_manifest = out / f'node-{node}-{method}-snapshot.json'
                parent_manifest.write_bytes(manifest_bytes)
                assert parent.stat().st_size == length and remote._sha(parent) == source_sha
                # Same saved bytes replayed as a labelled append control, never a
                # recovered historical suffix or a scientific observation.
                initial_append = min(4096, length // 4)
                append_fixture(original, live, 0, initial_append)
                os.sync()
                before = shutil.disk_usage(data).free
                assert 0 < before < length - initial_append
                release = None
                if method == 'release_verified_guest_duplicate':
                    release = snapshot.release_verified_prefix(data, copied, hashlib.sha256(manifest_bytes).hexdigest())
                    assert not copied.exists() and live.is_file()
                failure = None
                try:
                    append_fixture(original, live, initial_append, length - initial_append)
                except OSError as error:
                    assert method == 'keep_guest_duplicate' and error.errno == errno.ENOSPC
                    failure = {'type': type(error).__name__, 'errno': error.errno, 'message': str(error)}
                if method == 'keep_guest_duplicate':
                    assert failure is not None and copied.is_dir()
                else:
                    assert failure is None and live.stat().st_size == 2 * length
                    expected = hashlib.sha256()
                    for _ in range(2):
                        with original.open('rb') as stream:
                            while chunk := stream.read(MIB):
                                expected.update(chunk)
                    assert remote._sha(live) == expected.hexdigest()
                assert snapshot._sha256(live, length) == source_sha and remote._sha(parent) == source_sha
                assert parent_manifest.read_bytes() == manifest_bytes
                methods[method] = {'initial_free_bytes': before, 'release': release, 'append_failure': failure,
                    'final_source_bytes': live.stat().st_size, 'parent_original_sha256': remote._sha(parent),
                    'original_source_prefix_retained': True, 'snapshot_manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest()}
            finally:
                if mounted:
                    command('umount', str(mount))
                image.unlink(missing_ok=True)
        assert methods['keep_guest_duplicate']['initial_free_bytes'] == methods['release_verified_guest_duplicate']['initial_free_bytes']
        results[node] = {'original_bytes': length, 'original_sha256': source_sha, 'filesystem_image_bytes': image_bytes, 'comparisons': methods}
        remote._atomic_json(out / f'node-{node}-comparison.json', results[node])
    final = remote._get(session, f'https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}', headers).json()
    assert final['digest'] == DIGEST and final['expired'] is False
    shutil.rmtree(scratch)
    remote._atomic_json(out / 'proof.json', {'implementation_commit': os.environ['GITHUB_SHA'],
        'original_artifact': artifact, 'whole_archive_sha256_verified': digest,
        'manifest_sha256_stream_verified': MANIFEST, 'nodes': results,
        'new_traffic_models_simulations_scores_or_case_admission': False,
        'fixture_growth_is_replayed_saved_bytes_only_not_historical_suffix': True,
        'current_live_free_space_or_full_case_sufficiency_proven': False,
        'total_seconds_including_download_validation_cleanup': (time.monotonic_ns() - started) / 1e9})


if __name__ == '__main__':
    main()
