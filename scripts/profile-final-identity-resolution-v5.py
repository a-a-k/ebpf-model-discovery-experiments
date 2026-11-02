"""Fixed read-only diagnostic of unchanged S resolve; never a capture or model run."""
from __future__ import annotations

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
import sys
import time
import zipfile

SOURCE = 'f7ba801d70f9d2327031efc6dd0c00b90d252708'
MODULE_BLOB = '5fd1bd1efb427bed2dcb1e62130cc6d1f15a9cf0'
ARTIFACT = 13105593437
ARCHIVE_SHA = '8d6862f0891372194b3fe4d40ac6c7630b660ada25a8ea9f1121133cbb46acec'
ARCHIVE_BYTES = 5536654728
INVENTORY_SHA = 'd67a584f4e997d311881c5e70a811eb26e66ed652f48607e317af1b6263a9935'
INPUTS = {'observation-index.sqlite': 10481643520,
          'runtime-identity-v5/inventory-final.json': 149942755}
FULL_ROWS, SAMPLE_ROWS = 1475382, 100000
REPOSITORY = 'a-a-k/ebpf-model-discovery-experiments'


def write(path, value):
    with Path(path).open('w', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def artifact_api():
    value = json.loads(subprocess.check_output(['gh', 'api',
        f'repos/{REPOSITORY}/actions/artifacts/{ARTIFACT}']))
    assert (value['id'], value['size_in_bytes'], value['digest'], value['expired']) == (
        ARTIFACT, ARCHIVE_BYTES, 'sha256:'+ARCHIVE_SHA, False)
    assert (value['workflow_run']['id'], value['workflow_run']['head_sha']) == (41331878803, SOURCE)
    return value


def prepare(out):
    from ebpf_discovery.remote_toolchain_v4 import _download, _headers
    import requests

    out.mkdir(parents=True, exist_ok=False)
    result = {'stage': 'preparation', 'started_ns': time.time_ns(), 'status': 'started',
              'scope': 'Whole original archive SHA/selected two member CRC, no other body extraction',
              'selected': {}, 'outer_job_tail_unknown': True}
    started = time.monotonic()
    try:
        meta = artifact_api()
        write(out/'artifact-api.json', meta)
        reserve = 8*1024**3
        required = ARCHIVE_BYTES + sum(INPUTS.values()) + reserve
        free = shutil.disk_usage(out).free
        result['disk_before_download'] = {'available': free, 'required': required,
                                          'selected_uncompressed': sum(INPUTS.values()), 'reserve': reserve}
        assert free >= required, 'Insufficient space before original download/extraction'
        archive_path = out/'original.zip'
        download_start = time.monotonic()
        digest = _download(requests.Session(), meta['archive_download_url'],
                           _headers(os.environ['GH_TOKEN']), archive_path,
                           retry_log=out/'http-retries.jsonl')
        result['download_and_SHA_seconds'] = time.monotonic()-download_start
        assert digest == ARCHIVE_SHA and archive_path.stat().st_size == ARCHIVE_BYTES
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            by_name = {e.filename: e for e in entries}
            assert len(by_name) == len(entries)
            sidecars = {name: by_name[name].file_size for name in (
                'observation-index.sqlite-wal', 'observation-index.sqlite-shm',
                'observation-index.sqlite-journal') if name in by_name}
            result['original_sidecar_sizes'] = sidecars
            assert not sidecars.get('observation-index.sqlite-wal', 0)
            assert not sidecars.get('observation-index.sqlite-journal', 0)
            # ZIP times are observations only; no function-timing claim is made.
            write(out/'zip-stage-file-metadata.json', [
                {'name': e.filename, 'bytes': e.file_size, 'crc32': f'{e.CRC:08x}',
                 'zip_date_time': e.date_time}
                for e in entries if e.filename in {
                    'index-final.json', 'runtime-identity-v5/inventory-final.json',
                    'runtime-identity-v5/projection-final.jsonl',
                    'runtime-identity-v5/supplied-alias-scope-final.json',
                    'runtime-identity-v5/refresh-cost-final.json', 'freeze-integrity.json', 'status.json'}])
            for name, expected_bytes in INPUTS.items():
                entry = by_name[name]
                assert not entry.is_dir() and entry.file_size == expected_bytes
                free = shutil.disk_usage(out).free
                assert free >= expected_bytes + reserve, 'Insufficient space before selected extraction'
                target = out/name
                target.parent.mkdir(parents=True, exist_ok=True)
                stage_start = time.monotonic()
                with archive.open(entry) as source, target.open('xb') as destination:
                    shutil.copyfileobj(source, destination, 1024*1024)
                digest = sha(target)
                assert target.stat().st_size == expected_bytes
                if name.endswith('inventory-final.json'):
                    assert digest == INVENTORY_SHA
                result['selected'][name] = {'bytes': expected_bytes, 'sha256': digest,
                    'crc32': f'{entry.CRC:08x}', 'extract_and_SHA_seconds': time.monotonic()-stage_start}
        result['original_archive_SHA256'] = ARCHIVE_SHA
        result['status'] = 'complete'
        write(out/'preparation.json', result)
        artifact_api()  # Preserve proof and confirm original before removing recoverable ZIP copy.
        archive_path.unlink()
        result['verified_original_archive_copy_removed'] = True
    except BaseException as error:
        result.update(status='failed', error=repr(error))
        raise
    finally:
        result.update(ended_ns=time.time_ns(), elapsed_seconds=time.monotonic()-started)
        write(out/'preparation.json', result)


def profile(out):
    from ebpf_discovery import runtime_identity_v5

    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == SOURCE
    module_path = Path(runtime_identity_v5.__file__).resolve()
    assert module_path == (Path.cwd()/'src/ebpf_discovery/runtime_identity_v5.py').resolve()
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD:src/ebpf_discovery/runtime_identity_v5.py'], text=True).strip() == MODULE_BLOB
    expected_source = subprocess.check_output(['git', 'show', 'HEAD:src/ebpf_discovery/runtime_identity_v5.py'])
    assert module_path.read_bytes() == expected_source
    prep = json.loads((out/'preparation.json').read_text())
    assert prep['status'] == 'complete' and set(prep['selected']) == set(INPUTS)
    result = {'status': 'started', 'started_ns': time.time_ns(), 'scientific_source': SOURCE,
              'module_Git_blob': MODULE_BLOB, 'module_SHA256': sha(module_path),
              'fixed_rows': SAMPLE_ROWS, 'full_original_rows': FULL_ROWS,
              'scope': 'Unmodified resolve only via cProfile.runcall; SQL/decode/hash/setup separately in outer cost',
              'no_traffic_model_refit_rescore_or_case_admission': True,
              'no_extrapolation_to_original_full_phase_or_six_hour_cure': True}
    started = time.monotonic()
    db = None
    try:
        for name in INPUTS:
            assert sha(out/name) == prep['selected'][name]['sha256']
        inventory = json.loads((out/'runtime-identity-v5/inventory-final.json').read_text())
        assert inventory['schema'] == runtime_identity_v5.SCHEMA
        db = sqlite3.connect((out/'observation-index.sqlite').resolve().as_uri()+'?mode=ro&immutable=1', uri=True)
        db.execute('PRAGMA query_only=ON')
        integrity_start = time.monotonic()
        assert db.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
        assert db.execute('SELECT COUNT(*) FROM spans').fetchone()[0] == FULL_ROWS
        result['integrity_and_full_count_seconds'] = time.monotonic()-integrity_start
        counters, brackets, reasons = Counter(), Counter(), Counter()
        input_hash, output_hash = hashlib.sha256(), hashlib.sha256()
        profiler = cProfile.Profile()
        count, previous = 0, None
        loop_start = time.monotonic()
        for digest, encoded in db.execute('SELECT digest,data FROM spans ORDER BY digest LIMIT ?', (SAMPLE_ROWS,)):
            assert previous is None or previous < digest
            previous = digest
            original = json.loads(encoded)
            resolved = profiler.runcall(runtime_identity_v5.resolve, original, inventory)
            payload = encoded.encode('utf-8')
            input_hash.update(digest.encode('ascii')+len(payload).to_bytes(8,'big')+payload)
            payload = json.dumps(resolved,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
            output_hash.update(len(payload).to_bytes(8,'big')+payload)
            counters[resolved['status']] += 1
            brackets[(resolved.get('bracket') or {}).get('kind', 'none')] += 1
            reasons.update(resolved.get('unknown_reasons') or [])
            count += 1
        assert count == SAMPLE_ROWS
        result.update(loop_outer_seconds=time.monotonic()-loop_start, actual_rows=count,
                      input_stream_SHA256=input_hash.hexdigest(), output_stream_SHA256=output_hash.hexdigest(),
                      statuses=dict(counters), brackets=dict(brackets), unknown_reasons=dict(reasons))
        stats = pstats.Stats(profiler)
        result['functions'] = [{'file': key[0], 'line': key[1], 'function': key[2],
            'primitive_calls': value[0], 'total_calls': value[1], 'tottime': value[2], 'cumtime': value[3]}
            for key,value in sorted(stats.stats.items(),key=lambda pair:pair[1][3],reverse=True)]
        db.close()
        db = None
        for name in INPUTS:
            assert sha(out/name) == prep['selected'][name]['sha256']
        result['all_selected_inputs_byte_unchanged'] = True
        write(out/'profile.json', result)
        cleanup_start = time.monotonic()
        artifact_api()
        for name in INPUTS:
            (out/name).unlink()
        result['verified_recoverable_selected_copies_removed'] = True
        result['input_cleanup_seconds'] = time.monotonic()-cleanup_start
        result['status'] = 'complete'
    except BaseException as error:
        result.update(status='failed', error=repr(error))
        raise
    finally:
        if db is not None:
            db.close()
        result.update(ended_ns=time.time_ns(), elapsed_seconds=time.monotonic()-started)
        write(out/'profile.json', result)


if __name__ == '__main__':
    assert os.environ.get('GITHUB_ACTIONS') == 'true', 'Heavy diagnostic runs in Actions only'
    directory = Path(os.environ['FINAL_PROFILE_ROOT']).resolve()
    assert directory.is_relative_to(Path(os.environ['RUNNER_TEMP']).resolve())
    {'prepare':prepare, 'profile':profile}[sys.argv[1]](directory)
