"""Closed training-prefix checkpoint while the original campaign remains live."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import time

from .toolchain_v4 import PINS as V4_PINS


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


def _indexed_sources(campaign, checkpoint: Path, copied: dict) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    live_root = campaign.ctx.out.resolve()
    with sqlite3.connect(checkpoint/'observation-index.sqlite') as frozen_index:
        indexed = list(frozen_index.execute('SELECT path,consumed FROM files ORDER BY path'))
    source_records, wire_records, metadata_records, absent_metadata = [], [], [], []
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
                metadata_ref = document.get('raw_metadata_ref')
                if metadata_ref is not None and not raw_ref:
                    raise ValueError('indexed receiver metadata reference has no raw_ref body')
                if not raw_ref:
                    continue
                if not isinstance(raw_ref, str):
                    raise ValueError('indexed receiver raw_ref must be a relative string')
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
                if metadata_ref is None:
                    absent_metadata.append({'indexed_source': record['relative_path'],
                                            'raw_ref': raw_ref, 'status': 'no metadata reference in original wrapper'})
                    continue
                if not isinstance(metadata_ref, str) or not metadata_ref:
                    raise ValueError('indexed receiver raw_metadata_ref must be a relative string')
                metadata_path = Path(metadata_ref)
                if metadata_path.is_absolute():
                    raise ValueError('absolute receiver raw_metadata_ref needs explicit replay relocation')
                metadata_source, metadata_relative = _inside(original.parent/metadata_path, live_root)
                if metadata_source.parent != wire_source.parent or metadata_source.name != 'metadata.json':
                    raise ValueError(f'indexed receiver metadata is not alongside wire body: {metadata_relative}')
                metadata_key = metadata_relative.as_posix()
                if metadata_key not in copied:
                    metadata_records.append(_copy(metadata_source, live_root, checkpoint, copied))
                metadata = json.loads((checkpoint/metadata_key).read_text(encoding='utf-8'))
                required = ('source', 'node', 'received_ns', 'content_type', 'content_encoding',
                            'content_headers', 'raw_size_bytes', 'raw_sha256', 'raw_ref')
                if (not isinstance(metadata, dict)
                        or any(metadata.get(field) != document.get(field) for field in required)
                        or metadata.get('raw_size_bytes') != copied[key]['bytes']):
                    raise ValueError(f'indexed receiver metadata differs from wrapper or wire body: {metadata_relative}')
    return source_records, wire_records, metadata_records, absent_metadata


def _runtime_observation_dependencies(live_root: Path, checkpoint: Path,
                                      copied: dict) -> list[dict]:
    """Copy exact raw-locator inputs that normalized OTLP wrappers do not reference."""
    from .identity_projection_v5 import _runtime
    from .runtime_identity_v5 import _locator

    locators = {}
    with sqlite3.connect(checkpoint/'observation-index.sqlite') as frozen_index:
        for (encoded,) in frozen_index.execute('SELECT data FROM spans ORDER BY digest'):
            runtime = _runtime(json.loads(encoded))
            canonical = _locator((runtime or {}).get('locator'))
            if canonical is not None:
                key = tuple(canonical[name] for name in (
                    'source_file', 'retained_file', 'offset', 'length', 'sha256'))
                locators[key] = canonical
    if not locators:
        return []

    accounting_path = live_root/'observations'/'deepflow-codec-accounting.jsonl'
    accounting_by_locator = {}
    if accounting_path.is_file():
        for line in accounting_path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                canonical = _locator(row.get('_runtime_identity', {}).get('locator') or row)
                if canonical is not None:
                    key = tuple(canonical[name] for name in (
                        'source_file', 'retained_file', 'offset', 'length', 'sha256'))
                    accounting_by_locator.setdefault(key, []).append(row)
    records = []
    for canonical in locators.values():
        retained = Path(canonical['retained_file'])
        if retained.is_absolute():
            raise ValueError('runtime observation locator must be campaign-relative')
        raw_path = live_root/'observations'/retained
        raw_source, raw_relative = _inside(raw_path, live_root)
        with raw_source.open('rb') as stream:
            stream.seek(canonical['offset'])
            segment = stream.read(canonical['length'])
        if (len(segment) != canonical['length']
                or hashlib.sha256(segment).hexdigest() != canonical['sha256']):
            raise ValueError(f'runtime observation raw locator changed: {raw_relative}')
        raw_key = raw_relative.as_posix()
        if raw_key not in copied:
            _copy(raw_source, live_root, checkpoint, copied)
        proof = {'locator': canonical, 'raw_file': copied[raw_key]}
        if retained.parts and retained.parts[0] == 'deepflow-raw':
            locator_key = tuple(canonical[name] for name in (
                'source_file', 'retained_file', 'offset', 'length', 'sha256'))
            matches = accounting_by_locator.get(locator_key, [])
            if not matches:
                raise ValueError(f'DeepFlow locator lacks codec accounting: {raw_relative}')
            snapshot_path = raw_source.parent/'snapshot.json'
            snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
            declarations = [row for row in snapshot.get('files', [])
                            if row.get('snapshot_name') == raw_source.name]
            if (len(declarations) != 1
                    or declarations[0].get('copied_bytes') != raw_source.stat().st_size
                    or declarations[0].get('copied_sha256') != _sha(raw_source)):
                raise ValueError(f'DeepFlow snapshot does not bind retained raw file: {raw_relative}')
            for dependency in (accounting_path, snapshot_path):
                _, relative = _inside(dependency, live_root)
                if relative.as_posix() not in copied:
                    _copy(dependency, live_root, checkpoint, copied)
            proof.update({
                'codec_accounting_file': copied[
                    accounting_path.resolve().relative_to(live_root).as_posix()],
                'codec_accounting_matching_rows': len(matches),
                'snapshot_manifest': copied[
                    snapshot_path.resolve().relative_to(live_root).as_posix()],
            })
        records.append(proof)
    return records


def _toolchain(campaign, checkpoint: Path, copied: dict, pins: dict) -> dict:
    live_root = campaign.ctx.out.resolve()
    path = live_root/'toolchain-build'/'toolchain-build.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    expected = {name.lower(): commit for name, commit in pins.items()}
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
    collector = None
    runtime_identity_dependencies = []
    pins = V4_PINS
    if original_status.get('protocol_version') == 'graph-v5':
        from .toolchain_v5 import PINS as V5_PINS, collector_provenance
        collector = collector_provenance(live_root, original_status)
        _copy(live_root/collector['collector_file'], live_root, folder, copied)
        identity_root = live_root/'runtime-identity-v5'
        if not identity_root.is_dir():
            raise ValueError('graph-v5 checkpoint lacks runtime identity evidence')
        for path in sorted(identity_root.rglob('*')):
            if path.is_symlink():
                raise ValueError(f'runtime identity checkpoint input is a symlink: {path}')
            if path.is_file():
                runtime_identity_dependencies.append(
                    _copy(path, live_root, folder, copied))
        pins = V5_PINS
    index = _backup(campaign.store.db, folder/'observation-index.sqlite')
    with campaign.ctx.journal.lock:
        journal = _backup(campaign.ctx.journal.db, folder/'attempt-journal.sqlite')
    copied[index['relative_path']] = index
    copied[journal['relative_path']] = journal
    sources, wires, wire_metadata, absent_metadata = _indexed_sources(campaign, folder, copied)
    runtime_observation_dependencies = _runtime_observation_dependencies(live_root, folder, copied)
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
    binaries = _toolchain(campaign, folder, copied, pins)
    manifest = {'schema_version': 'v4-training-prefix-checkpoint', 'identity': identity,
                'status': 'partial_training_capture_only; no forecast or completed cell',
                'source_cutoff_rule': 'exact files.consumed byte prefixes in backed-up observation-index.sqlite',
                'index': index, 'journal': journal, 'indexed_sources': sources,
                'referenced_wire_bodies': wires, 'referenced_wire_metadata': wire_metadata,
                'metadata_reference_absent': absent_metadata,
                'toolchain': binaries,
                **({'runtime_identity_dependencies': runtime_identity_dependencies}
                   if runtime_identity_dependencies else {}),
                **({'runtime_observation_dependencies': runtime_observation_dependencies}
                   if runtime_observation_dependencies else {}),
                **({'collector_provenance': collector} if collector is not None else {}),
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
    started_mono = time.monotonic_ns()
    ready = None
    ready_mono = None
    release = None
    try:
        ready = create_checkpoint(campaign, folder)
        ready_mono = time.monotonic_ns()
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
        ended_mono = time.monotonic_ns()
        _atomic_json(campaign.ctx.out/'training-checkpoint-cost.json', {
            'started_ns': started_ns, 'ended_ns': time.time_ns(),
            'total_wall_seconds': (ended_mono-started_mono)/1e9,
            'creation_wall_seconds': ((ready_mono or ended_mono)-started_mono)/1e9,
            'upload_hold_wall_seconds': (ended_mono-ready_mono)/1e9 if ready_mono else None,
            'ready': ready is not None, 'upload_success': release.get('upload_success') if release else None,
            'checkpoint_path': str(Path(folder).resolve()),
            'scope': 'checkpoint creation and upload hold on same live runner and guests; toolchain setup and earlier campaign are recorded separately',
        })
