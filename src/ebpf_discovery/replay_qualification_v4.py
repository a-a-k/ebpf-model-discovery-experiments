"""Actions-only, source-only replay of one retained v4 qualification capture.

The original artifact is read only. The SQLite copy changes only files.path so
loss-preserving raw export can open the downloaded capture at its new location.
This is a technical diagnostic, never a new acquisition or a scored campaign.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import time

from .runtime import Context, write_json
from .store_v3 import ObservationStore
from .toolchain_v4 import PINS, Toolchain


SYSTEMS = ('deathstarbench', 'otel_demo', 'petclinic')


def digest(path: Path) -> str:
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def file_manifest(root: Path) -> dict[str, dict]:
    root = Path(root).resolve()
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'original capture contains a symlink: {path}')
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            result[relative] = {'sha256': digest(path), 'bytes': path.stat().st_size}
    return result


def verified_binaries(original: Path, replay: Path) -> tuple[Path, Path, dict]:
    manifest_path = original/'toolchain-build'/'toolchain-build.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 'toolchain-build-v4':
        raise ValueError('retained toolchain build manifest schema mismatch')
    rows = manifest.get('binaries') or []
    expected = {name.lower(): commit for name, commit in PINS.items()}
    if len(rows) != len(expected) or {r.get('name') for r in rows} != set(expected):
        raise ValueError('retained toolchain does not contain exactly the pinned tools')
    old_roots, binary_evidence = set(), {}
    bin_copy = replay/'pinned-bin'
    bin_copy.mkdir(parents=True, exist_ok=False)
    for row in rows:
        name = row['name']
        old_binary = Path(row['binary'])
        if not old_binary.is_absolute() or old_binary.name != name:
            raise ValueError(f'invalid retained binary path for {name}')
        old_root = old_binary.parents[2]
        if old_binary.parent != old_root/'toolchain-build'/'bin':
            raise ValueError(f'retained binary is outside expected toolchain bin: {name}')
        old_roots.add(old_root)
        binary = original/'toolchain-build'/'bin'/name
        if row.get('commit') != expected[name] or not binary.is_file():
            raise ValueError(f'pinned commit or binary missing for {name}')
        actual = digest(binary)
        if actual != row.get('binary_sha256') or binary.stat().st_size != row.get('binary_bytes'):
            raise ValueError(f'retained binary digest or byte length mismatch: {name}')
        executable = bin_copy/name
        shutil.copy2(binary, executable)
        if digest(executable) != actual:
            raise ValueError(f'copied pinned binary changed: {name}')
        executable.chmod(executable.stat().st_mode | 0o111)
        binary_evidence[name] = {'commit': row['commit'], 'sha256': actual,
                                 'bytes': binary.stat().st_size,
                                 'original_binary_path': row['binary']}
    if len(old_roots) != 1:
        raise ValueError('retained binary paths disagree on original capture root')
    return bin_copy, next(iter(old_roots)), binary_evidence


def _table_hash(db: sqlite3.Connection, table: str, order: str) -> str:
    hasher = hashlib.sha256()
    for row in db.execute(f'SELECT * FROM {table} ORDER BY {order}'):
        hasher.update(json.dumps(row, separators=(',', ':'), ensure_ascii=False).encode())
        hasher.update(b'\n')
    return hasher.hexdigest()


def relocate_index(original: Path, replay: Path, old_root: Path) -> dict:
    source = original/'observation-index.sqlite'
    destination = replay/'observation-index.sqlite'
    if not source.is_file():
        raise ValueError('retained observation index is missing')
    shutil.copy2(source, destination)
    if digest(source) != digest(destination):
        raise ValueError('copied observation index differs before relocation')
    original_sha = digest(source)
    db = sqlite3.connect(destination)
    try:
        if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError('copied observation index failed quick_check')
        spans_before = _table_hash(db, 'spans', 'digest')
        links_before = _table_hash(db, 'links', 'source,linked_trace,linked_span,trace')
        rows = list(db.execute('SELECT path,consumed FROM files ORDER BY path'))
        if not rows:
            raise ValueError('retained observation index has no consumed source files')
        relocations = []
        for old_path, consumed in rows:
            old_file = Path(old_path)
            if not old_file.is_absolute():
                raise ValueError(f'indexed source path is not absolute: {old_path}')
            try:
                relative = old_file.relative_to(old_root)
            except ValueError as error:
                raise ValueError(f'indexed source path outside original capture root: {old_path}') from error
            candidate = original/relative
            if not candidate.is_file() or candidate.is_symlink() or candidate.resolve().is_relative_to(replay.resolve()):
                raise ValueError(f'relocated source file missing or redirected: {candidate}')
            if not isinstance(consumed, int) or consumed < 0 or consumed > candidate.stat().st_size:
                raise ValueError(f'invalid consumed prefix for {candidate}')
            db.execute('UPDATE files SET path=? WHERE path=?', (str(candidate.resolve()), old_path))
            relocations.append({'old_path': old_path, 'new_path': str(candidate.resolve()),
                                'consumed': consumed, 'source_sha256': digest(candidate)})
        db.commit()
        spans_after = _table_hash(db, 'spans', 'digest')
        links_after = _table_hash(db, 'links', 'source,linked_trace,linked_span,trace')
        if spans_before != spans_after or links_before != links_after:
            raise ValueError('index relocation modified spans or source-local links')
        if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError('relocated index failed quick_check')
    finally:
        db.close()
    return {'original_index_sha256': original_sha,
            'copied_index_sha256_after_relocation': digest(destination),
            'spans_rows_sha256_before': spans_before, 'spans_rows_sha256_after': spans_after,
            'links_rows_sha256_before': links_before, 'links_rows_sha256_after': links_after,
            'files_path_relocations': relocations,
            'changed_table_policy': 'files.path only; spans/data/links unchanged'}


def replay(original: Path, out: Path, system: str, source: dict) -> dict:
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('v4 capture replay is permitted only in GitHub Actions')
    if system not in SYSTEMS:
        raise ValueError(f'unsupported system: {system}')
    original, out = Path(original).resolve(), Path(out).resolve()
    if out == original or original in out.parents or out in original.parents:
        raise ValueError('replay and original capture directories must be separate')
    if out.exists() and any(out.iterdir()):
        raise ValueError('replay output must be empty before execution')
    out.mkdir(parents=True, exist_ok=True)
    status = {'status': 'capture_replay_started', 'system': system,
              'source_run_id': source.get('run_id'), 'source_artifact_id': source.get('artifact_id'),
              'current_commit': os.environ.get('GITHUB_SHA'), 'started_ns': time.time_ns(),
              'interpretation': 'retained-capture technical replay; not a full qualification or new acquisition'}
    write_json(out/'status.json', status)
    original_files = None
    try:
        original_files = file_manifest(original)
        write_json(out/'original-input-hashes.json', original_files)
        expected_name = f"qualification-v4-{system}-full-6-{source.get('run_id')}"
        if (source.get('artifact_name') != expected_name or type(source.get('artifact_id')) is not int
                or not re.fullmatch(r'[0-9a-f]{40}', str(source.get('run_sha', '')))
                or not re.fullmatch(r'sha256:[0-9a-f]{64}', str(source.get('artifact_digest', '')))
                or source.get('run_status') != 'completed' or source.get('expired') is True):
            raise ValueError('source artifact identity, run SHA, or availability mismatch')
        original_status = json.loads((original/'status.json').read_text(encoding='utf-8'))
        if (original_status.get('system'), original_status.get('mode'), original_status.get('seed')) != (system, 'full', 6):
            raise ValueError('retained qualification cell identity differs from requested replay')
        if str(original_status.get('run_id')) != str(source['run_id']) or original_status.get('commit') != source['run_sha']:
            raise ValueError('retained status differs from immutable Actions run metadata')
        plans = json.loads((original/'plans.json').read_text(encoding='utf-8'))
        if len(plans) != 240 or any(plan.get('phase') != 'qualification' for plan in plans):
            raise ValueError('retained capture lacks exactly 240 qualification intents')
        if len({plan.get('attempt_id') for plan in plans}) != 240:
            raise ValueError('retained qualification attempt IDs are missing or duplicate')
        binary_dir, old_root, binary_evidence = verified_binaries(original, out)
        index_evidence = relocate_index(original, out, old_root)
        shutil.copy2(original/'deployment.json', out/'deployment.json')
        ctx = Context(out, 'full', 6)
        ctx.deployment_dir = original/'deployment'
        old_bin = os.environ.get('PBS_BIN')
        os.environ['PBS_BIN'] = str(binary_dir.resolve())
        store = ObservationStore(out/'observation-index.sqlite', same_trace_parents=True)
        try:
            declaration = importlib.import_module(f'systems.{system}.experiment_v4')
            forecasts = Toolchain(ctx, system, store, declaration).forecast(plans)
        finally:
            store.close()
            if old_bin is None:
                os.environ.pop('PBS_BIN', None)
            else:
                os.environ['PBS_BIN'] = old_bin
        write_json(out/'replay-provenance.json', {'source_artifact': source,
            'original_status_sha256': original_files['status.json']['sha256'],
            'original_plans_sha256': original_files['plans.json']['sha256'],
            'original_deployment_sha256': original_files['deployment.json']['sha256'],
            'original_artifact_files': len(original_files),
            'original_capture_root_from_build_manifest': str(old_root),
            'binary_evidence': binary_evidence, 'index': index_evidence,
            'forecast_branches': {s: {v: {op: {'available': bool(f.get('available')),
                'reason': f.get('reason')} for op, f in operations.items()}
                for v, operations in variants.items()} for s, variants in forecasts.items()},
            'original_raw_capture_reused': True, 'new_application_traffic': False})
        status['status'] = 'capture_replay_complete'
        return status
    except BaseException as error:
        status.update(status='capture_replay_technical_failure', error=repr(error))
        raise
    finally:
        status['ended_ns'] = time.time_ns()
        status['original_files_unchanged'] = (file_manifest(original) == original_files
                                             if original_files is not None else None)
        write_json(out/'status.json', status)
        if status['original_files_unchanged'] is False:
            raise RuntimeError('original qualification artifact changed during replay')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--system', choices=SYSTEMS, required=True)
    parser.add_argument('--source', type=Path, required=True,
                        help='saved GitHub Actions run/artifact metadata JSON')
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding='utf-8'))
    replay(args.original, args.out, args.system, source)


if __name__ == '__main__':
    main()
