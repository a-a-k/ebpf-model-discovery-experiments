"""Closed training-prefix checkpoint while the original campaign remains live."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import time

from .toolchain_v4 import PINS


CORE_FILES = (
    'status.json', 'plans.json', 'external.json', 'census.json', 'blocks.json',
    'preparation-operations.json', 'deployment.json', 'index-training.json',
)
EXCLUDED_DEPLOYMENT_PARTS = {'source', 'upstream', 'image-context'}


def _sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _inside(path: Path, live_root: Path) -> tuple[Path, Path]:
    if path.is_symlink():
        raise ValueError(f'checkpoint input is a symlink: {path}')
    resolved = path.resolve()
    if not resolved.is_relative_to(live_root):
        raise ValueError(f'checkpoint input lies outside live campaign: {path}')
    return resolved, resolved.relative_to(live_root)


def _copy(path: Path, live_root: Path, checkpoint: Path, copied: dict,
          *, prefix_bytes: int | None = None) -> dict:
    source, relative = _inside(path, live_root)
    if not source.is_file():
        raise ValueError(f'checkpoint input is missing: {source}')
    limit = source.stat().st_size if prefix_bytes is None else prefix_bytes
    if not isinstance(limit, int) or limit < 0 or limit > source.stat().st_size:
        raise ValueError(f'invalid frozen source prefix: {source}')
    destination = checkpoint/relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with source.open('rb') as input_stream, destination.open('wb') as output_stream:
        remaining = limit
        while remaining:
            chunk = input_stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError(f'source shortened while copying frozen prefix: {source}')
            output_stream.write(chunk)
            digest.update(chunk)
            remaining -= len(chunk)
        output_stream.flush()
        os.fsync(output_stream.fileno())
    value = digest.hexdigest()
    if _sha(destination) != value:
        raise ValueError(f'checkpoint copy differs from source prefix: {relative}')
    # Receiver JSONL may append; its already indexed prefix must remain identical.
    with source.open('rb') as input_stream:
        original_digest, remaining = hashlib.sha256(), limit
        while remaining:
            chunk = input_stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError(f'source shortened after frozen-prefix copy: {source}')
            original_digest.update(chunk)
            remaining -= len(chunk)
    if original_digest.hexdigest() != value:
        raise ValueError(f'frozen source prefix changed during checkpoint: {source}')
    record = {'relative_path': relative.as_posix(), 'bytes': limit, 'sha256': value}
    if prefix_bytes is not None:
        record['consumed_prefix_bytes'] = limit
        record['source_size_at_copy'] = source.stat().st_size
    copied[relative.as_posix()] = record
    return record


def _backup(connection: sqlite3.Connection, destination: Path) -> dict:
    with sqlite3.connect(destination) as target:
        connection.backup(target)
        if target.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError(f'checkpoint SQLite backup failed quick_check: {destination}')
    return {'relative_path': destination.name, 'bytes': destination.stat().st_size,
            'sha256': _sha(destination)}


def _indexed_sources(campaign, checkpoint: Path, copied: dict) -> tuple[list[dict], list[dict]]:
    live_root = campaign.ctx.out.resolve()
    with sqlite3.connect(checkpoint/'observation-index.sqlite') as frozen_index:
        indexed = list(frozen_index.execute('SELECT path,consumed FROM files ORDER BY path'))
    source_records, wire_records = [], []
    for name, consumed in indexed:
        original = Path(name)
        record = _copy(original, live_root, checkpoint, copied, prefix_bytes=consumed)
        source_records.append({'original_path': str(original), **record})
        if original.suffix != '.jsonl':
            continue
        copied_jsonl = checkpoint/record['relative_path']
        with copied_jsonl.open('rb') as stream:
            for line in stream:
                if not line.strip():
                    continue
                document = json.loads(line)
                raw_ref = document.get('raw_ref')
                if not raw_ref:
                    continue
                ref = Path(raw_ref)
                if ref.is_absolute():
                    raise ValueError('absolute receiver raw_ref needs explicit replay relocation')
                wire_path = original.parent/ref
                wire_source, wire_relative = _inside(wire_path, live_root)
                expected = document.get('raw_sha256')
                if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
                    raise ValueError(f'indexed wire body lacks valid raw SHA-256: {wire_relative}')
                key = wire_relative.as_posix()
                if key not in copied:
                    wire_record = _copy(wire_source, live_root, checkpoint, copied)
                    wire_records.append(wire_record)
                if copied[key]['sha256'] != expected:
                    raise ValueError(f'indexed wire body digest mismatch: {wire_relative}')
    return source_records, wire_records


def _toolchain(campaign, checkpoint: Path, copied: dict) -> dict:
    live_root = campaign.ctx.out.resolve()
    path = live_root/'toolchain-build'/'toolchain-build.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    expected = {name.lower(): commit for name, commit in PINS.items()}
    rows = manifest.get('binaries') or []
    if manifest.get('schema_version') != 'toolchain-build-v4' or len(rows) != len(expected):
        raise ValueError('training checkpoint lacks exact toolchain build manifest')
    if {row.get('name') for row in rows} != set(expected):
        raise ValueError('training checkpoint tool names differ from pinned toolchain')
    proofs = []
    for row in rows:
        name = row['name']
        binary = live_root/'toolchain-build'/'bin'/name
        if (row.get('commit') != expected[name]
                or Path(row.get('binary', '')).resolve() != binary.resolve()
                or not re.fullmatch(r'[0-9a-f]{64}', str(row.get('binary_sha256', '')))
                or binary.stat().st_size != row.get('binary_bytes')
                or _sha(binary) != row['binary_sha256']):
            raise ValueError(f'training checkpoint pinned binary proof failed: {name}')
        proofs.append({'name': name, 'commit': row['commit'],
                       **_copy(binary, live_root, checkpoint, copied)})
    _copy(path, live_root, checkpoint, copied)
    builds = live_root/'toolchain-build'/'builds.tsv'
    if builds.is_file():
        _copy(builds, live_root, checkpoint, copied)
    return {'manifest_sha256': copied['toolchain-build/toolchain-build.json']['sha256'],
            'binaries': proofs}


def create_checkpoint(campaign, folder: Path) -> dict:
    """Close one reproducible training snapshot without touching live source files."""
    live_root, folder = campaign.ctx.out.resolve(), Path(folder).resolve()
    if folder == live_root or folder in live_root.parents or live_root in folder.parents:
        raise ValueError('checkpoint must be separate from live campaign output')
    if folder.exists() and any(folder.iterdir()):
        raise ValueError('checkpoint output must be empty')
    folder.mkdir(parents=True, exist_ok=True)
    copied = {}
    identity = {'run_id': os.environ.get('GITHUB_RUN_ID'),
                'commit': os.environ.get('GITHUB_SHA'),
                'system': campaign.system, 'mode': campaign.ctx.mode, 'seed': campaign.ctx.seed}
    for name in CORE_FILES:
        _copy(live_root/name, live_root, folder, copied)
    original_status = json.loads((folder/'status.json').read_text(encoding='utf-8'))
    if any(original_status.get(key) != identity[key] for key in ('system', 'mode', 'seed', 'commit')):
        raise ValueError('checkpoint identity differs from running campaign')
    index = _backup(campaign.store.db, folder/'observation-index.sqlite')
    with campaign.ctx.journal.lock:
        journal = _backup(campaign.ctx.journal.db, folder/'attempt-journal.sqlite')
    copied[index['relative_path']] = index
    copied[journal['relative_path']] = journal
    sources, wires = _indexed_sources(campaign, folder, copied)
    deployment = live_root/'deployment'
    if deployment.is_dir():
        for path in sorted(deployment.rglob('*')):
            if (any(part in EXCLUDED_DEPLOYMENT_PARTS for part in path.relative_to(deployment).parts)
                    or path.name == 'petclinic-image.tar'):
                continue
            if path.is_symlink():
                raise ValueError(f'deployment checkpoint contains a symlink: {path}')
            if path.is_file():
                _copy(path, live_root, folder, copied)
    binaries = _toolchain(campaign, folder, copied)
    manifest = {'schema_version': 'v4-training-prefix-checkpoint', 'identity': identity,
                'status': 'partial_training_capture_only; no forecast or completed cell',
                'source_cutoff_rule': 'exact files.consumed byte prefixes in backed-up observation-index.sqlite',
                'index': index, 'journal': journal, 'indexed_sources': sources,
                'referenced_wire_bodies': wires, 'toolchain': binaries,
                'files': copied, 'created_ns': time.time_ns(),
                'new_application_traffic': False, 'same_live_campaign_required_to_continue': True}
    _atomic_json(folder/'manifest.json', manifest)
    ready = {**identity, 'schema_version': 'v4-training-prefix-checkpoint-ready',
             'status': 'training_checkpoint_ready', 'manifest_sha256': _sha(folder/'manifest.json'),
             'created_ns': time.time_ns()}
    _atomic_json(folder/'ready.json', ready)
    return ready


def wait_for_release(campaign, folder: Path, ready: dict) -> dict:
    release_path = Path(folder)/'release.json'
    while not release_path.exists():
        time.sleep(1)
    release = json.loads(release_path.read_text(encoding='utf-8'))
    for key in ('run_id', 'commit', 'system', 'mode', 'seed', 'manifest_sha256'):
        if release.get(key) != ready[key]:
            raise ValueError(f'training checkpoint release binding mismatch: {key}')
    if type(release.get('upload_success')) is not bool:
        raise ValueError('training checkpoint release lacks upload_success boolean')
    campaign.ctx.journal.append('training_checkpoint_release', release)
    if not release['upload_success']:
        raise RuntimeError('training checkpoint upload failed; no forecast or further intervention')
    return release


def checkpoint_and_wait(campaign, folder: Path) -> dict:
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('live v4 training checkpoint is permitted only in GitHub Actions')
    started_ns = time.time_ns()
    ready = None
    release = None
    try:
        ready = create_checkpoint(campaign, folder)
        campaign.ctx.journal.append('training_checkpoint_ready', ready)
        release = wait_for_release(campaign, folder, ready)
        return release
    finally:
        if release is None and ready is not None:
            release_path = Path(folder)/'release.json'
            if release_path.is_file():
                try:
                    candidate = json.loads(release_path.read_text(encoding='utf-8'))
                    if (isinstance(candidate, dict) and type(candidate.get('upload_success')) is bool
                            and all(candidate.get(key) == ready[key] for key in
                                    ('run_id', 'commit', 'system', 'mode', 'seed', 'manifest_sha256'))):
                        release = candidate
                except (OSError, ValueError):
                    pass
        _atomic_json(campaign.ctx.out/'training-checkpoint-cost.json', {
            'started_ns': started_ns, 'ended_ns': time.time_ns(),
            'ready': ready is not None, 'upload_success': release.get('upload_success') if release else None,
            'checkpoint_path': str(Path(folder).resolve()),
            'scope': 'same live runner and guests; preparation, upload and hold counted as campaign cost',
        })
