"""Fixed Actions-only diagnostic of an unchanged resolver; no scientific replay."""
from collections import Counter
import cProfile
import hashlib
import json
import os
from pathlib import Path
import pstats
import shutil
import sqlite3
import subprocess
import time
import zipfile

import requests

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery import runtime_identity_v5 as runtime

RUN = 41273870033
ARTIFACT = 13075276795
SOURCE = '06d7d52bfa4b7768a4cabf02f4e66f109b3a9492'
DIGEST = 'sha256:22d706c5099c16203cef5f407273a067042a1def970ab4e3d72d3e362422d555'
MANIFEST = '5aad17e431831e4deb7a046af03fdf8b39249e89ade6b67c86c87dabfc745749'
INVENTORY_SHA = 'db950010fe20abaa68b6d22f8a0d1f2b6fd9b49180de5dfba388ad4a6c076c4b'
MEMBERS = {
    'observation-index.sqlite': (14255300608, '47a50fc6'),
    'runtime-identity-v5/inventory-training.json': (109739059, '87adaaf4'),
}


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('saved-index profiling is Actions only')
    started = time.monotonic_ns()
    output = Path('work/fixed-deepflow-resolver-profile').resolve()
    output.mkdir(exist_ok=True)
    assert not (output / 'profile.json').exists()
    scratch = Path('work/fixed-deepflow-resolver-scratch').resolve()
    scratch.mkdir(exist_ok=False)
    original_code = subprocess.check_output(['git', 'show', SOURCE + ':src/ebpf_discovery/runtime_identity_v5.py'])
    module_sha = hashlib.sha256(Path(runtime.__file__).read_bytes()).hexdigest()
    assert module_sha == hashlib.sha256(original_code).hexdigest()
    repository = os.environ['GITHUB_REPOSITORY']
    headers = remote._headers(os.environ['GH_TOKEN'])
    session = requests.Session()
    artifact = remote._get(session, f'https://api.github.com/repos/{repository}/actions/artifacts/{ARTIFACT}', headers).json()
    assert (artifact['id'], artifact['digest'], artifact['expired']) == (ARTIFACT, DIGEST, False)
    assert artifact['workflow_run']['id'] == RUN and artifact['workflow_run']['head_sha'] == SOURCE
    assert artifact['name'] == f'training-v4-otel_demo-absent-6-{RUN}'
    remote._atomic_json(output / 'original-artifact-api.json', artifact)
    archive = scratch / 'original.zip'
    download_start = time.monotonic_ns()
    digest = remote._download(session, artifact['archive_download_url'], headers, archive)
    assert 'sha256:' + digest == DIGEST and archive.stat().st_size == artifact['size_in_bytes']
    download_seconds = (time.monotonic_ns() - download_start) / 1e9
    extraction_start = time.monotonic_ns()
    proofs = {}
    with zipfile.ZipFile(archive) as bundle:
        assert len({row.filename for row in bundle.infolist()}) == len(bundle.infolist())
        ready = json.loads(bundle.read('ready.json'))
        assert ready['manifest_sha256'] == MANIFEST
        assert (str(ready['run_id']), ready['commit'], ready['system'], ready['mode'], int(ready['seed'])) == (
            str(RUN), SOURCE, 'otel_demo', 'absent', 6)
        manifest_digest = hashlib.sha256()
        with bundle.open('manifest.json') as stream:
            while chunk := stream.read(1024 * 1024):
                manifest_digest.update(chunk)
        assert manifest_digest.hexdigest() == MANIFEST
        assert shutil.disk_usage(scratch).free > sum(row[0] for row in MEMBERS.values()) + 512 * 1024 * 1024
        for name, (length, crc) in MEMBERS.items():
            member = bundle.getinfo(name)
            assert member.file_size == length and f'{member.CRC:08x}' == crc
            target = scratch / Path(name).name
            file_digest = hashlib.sha256()
            with bundle.open(member) as source, target.open('xb') as destination:
                while chunk := source.read(1024 * 1024):
                    file_digest.update(chunk)
                    destination.write(chunk)
            assert target.stat().st_size == length
            proofs[name] = {'bytes': length, 'sha256': file_digest.hexdigest(), 'CRC32_checked': crc}
    extraction_seconds = (time.monotonic_ns() - extraction_start) / 1e9
    assert proofs['runtime-identity-v5/inventory-training.json']['sha256'] == INVENTORY_SHA
    archive.unlink()
    inventory = json.loads((scratch / 'inventory-training.json').read_text(encoding='utf-8'))
    index = scratch / 'observation-index.sqlite'
    database = sqlite3.connect(f'file:{index.as_posix()}?mode=ro&immutable=1', uri=True)
    database.execute('PRAGMA query_only=ON')
    database.execute('PRAGMA cache_size=-65536')
    assert database.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
    count = database.execute('SELECT COUNT(*) FROM spans').fetchone()[0]
    assert count == 828668
    statuses, brackets, reasons = Counter(), Counter(), Counter()
    input_sha, result_sha = hashlib.sha256(), hashlib.sha256()
    profiler = cProfile.Profile()
    sample_start = time.monotonic_ns()
    rows = 0
    for record_digest, encoded in database.execute('SELECT digest,data FROM spans ORDER BY digest LIMIT 10000'):
        record = json.loads(encoded)
        input_sha.update(json.dumps([record_digest, encoded], separators=(',', ':')).encode() + b'\n')
        result = profiler.runcall(runtime.resolve, record, inventory)
        result_sha.update(json.dumps(result, sort_keys=True, separators=(',', ':')).encode() + b'\n')
        statuses[result['status']] += 1
        brackets[(result.get('bracket') or {}).get('kind', 'none')] += 1
        reasons.update(result.get('unknown_reasons') or [])
        rows += 1
    sample_seconds = (time.monotonic_ns() - sample_start) / 1e9
    assert rows == 10000
    database.close()
    statistics = pstats.Stats(profiler)
    functions = []
    for (filename, line, name), (primitive, calls, own, cumulative, _) in statistics.stats.items():
        functions.append({'file': filename, 'line': line, 'function': name,
            'primitive_calls': primitive, 'calls': calls, 'own_seconds': own, 'cumulative_seconds': cumulative})
    functions.sort(key=lambda row: row['cumulative_seconds'], reverse=True)
    remote._atomic_json(output / 'profile.json', {
        'schema': 'fixed-original-runtime-resolver-diagnostic-v5', 'implementation_commit': os.environ['GITHUB_SHA'],
        'original_source': SOURCE, 'literal_original_resolver_sha256': module_sha,
        'source_artifact': artifact, 'whole_archive_sha256_verified': digest,
        'manifest_sha256_stream_verified_without_materializing': MANIFEST,
        'selected_member_proofs': proofs, 'original_index_rows': count,
        'diagnostic_sample_rows': rows, 'diagnostic_order': 'original digest order, first 10000, no outcome filter',
        'sample_input_sha256': input_sha.hexdigest(), 'sample_result_sha256': result_sha.hexdigest(),
        'statuses': dict(statuses), 'bracket_kinds': dict(brackets), 'unknown_reasons': dict(reasons),
        'top_functions_by_cumulative_seconds': functions[:60],
        'all_profiled_primitive_calls': statistics.prim_calls, 'all_profiled_calls': statistics.total_calls,
        'profiled_function_seconds': statistics.total_tt, 'sample_wall_seconds': sample_seconds,
        'download_seconds': download_seconds, 'manifest_stream_and_two_member_extraction_seconds': extraction_seconds,
        'total_seconds_before_cleanup': (time.monotonic_ns() - started) / 1e9,
        'new_traffic_models_simulations_or_scores': False, 'source_index_mutated': False,
        'limits': 'Auxiliary fixed diagnostic only. cProfile overhead and host memory differ from original live-guest parent. No extrapolation to all rows, whole67-minute refresh, six-hour cure, intrinsic collector speed or original81 scientific success.'})
    shutil.rmtree(scratch)


if __name__ == '__main__':
    main()
