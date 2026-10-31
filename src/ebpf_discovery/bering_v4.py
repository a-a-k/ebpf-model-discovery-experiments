"""Replay retained exports through Bering's actual native and OBI source inputs."""
from __future__ import annotations

import hashlib
import heapq
import itertools
import gzip
import json
import os
from pathlib import Path
import signal
import socket
import sqlite3
import subprocess
import sys
from tempfile import NamedTemporaryFile
import time
from contextlib import contextmanager
from contextvars import ContextVar

import requests
import yaml

from .runtime import write_json


_CHILD_GO_ENV = ContextVar('bering_v4_child_go_env', default=None)
_GO_ENV_KEYS = ('GOMEMLIMIT', 'GOGC', 'GODEBUG')


@contextmanager
def child_go_environment(overrides=None):
    """Scope Go settings to Bering children, never other tools."""
    supplied = dict(overrides or {})
    unknown = set(supplied) - set(_GO_ENV_KEYS)
    if unknown or any(not isinstance(value, str) for value in supplied.values()):
        raise ValueError('Bering child environment only accepts string Go runtime settings')
    token = _CHILD_GO_ENV.set(supplied or None)
    try:
        yield _child_process_environment()[1]
    finally:
        _CHILD_GO_ENV.reset(token)


def _child_process_environment():
    overrides = _CHILD_GO_ENV.get()
    inherited = {key: os.environ.get(key) for key in _GO_ENV_KEYS}
    if not overrides:
        return None, {'configured': False, 'requested_go_environment': {},
                      'inherited_go_environment': inherited,
                      'effective_go_environment': inherited}
    effective = dict(inherited)
    effective.update(overrides)
    if 'GODEBUG' in overrides and inherited.get('GODEBUG'):
        requested = [part for part in overrides['GODEBUG'].split(',') if part]
        requested_names = {part.split('=', 1)[0] for part in requested}
        retained = [part for part in inherited['GODEBUG'].split(',')
                    if part and part.split('=', 1)[0] not in requested_names]
        effective['GODEBUG'] = ','.join([*retained, *requested])
    environment = os.environ.copy()
    environment.update({key: value for key, value in effective.items() if value is not None})
    return environment, {'configured': True, 'requested_go_environment': dict(overrides),
                         'inherited_go_environment': inherited,
                         'effective_go_environment': effective,
                         'scope': 'Bering child wrapper and Bering child only'}


def decoded_size(export):
    """Match Bering's decoded-body limit without filtering selected observations."""
    path = Path(export['path'])
    encoding = (export.get('content_encoding') or '').lower()
    if not encoding:
        return path.stat().st_size
    if encoding != 'gzip':
        raise ValueError('Unsupported retained content encoding: '+encoding)
    size = 0
    with gzip.open(path, 'rb') as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
    return size


class _ArchiveSlice:
    """Seekable bounded view of one retained request inside a storage shard."""

    def __init__(self, path, offset, length):
        self.stream = Path(path).open('rb'); self.offset = offset; self.length = length
        self.position = 0; self.stream.seek(offset)

    def read(self, size=-1):
        remaining = self.length - self.position
        if size is None or size < 0 or size > remaining:
            size = remaining
        body = self.stream.read(size); self.position += len(body)
        return body

    def tell(self):
        return self.position

    def seek(self, offset, whence=os.SEEK_SET):
        target = (offset if whence == os.SEEK_SET else
                  self.position + offset if whence == os.SEEK_CUR else
                  self.length + offset)
        if not 0 <= target <= self.length:
            raise ValueError('archive request slice seek escapes retained request')
        self.stream.seek(self.offset + target); self.position = target
        return target

    def close(self):
        self.stream.close()


def _verified_stream_requests(manifest, *, materialize=True):
    """Yield retained HTTP bodies; archive shards never become HTTP batches."""
    for descriptor in manifest.get('stream_exports', []):
        if descriptor.get('schema_version') != 'deepflow-request-archive-v5':
            raise ValueError('unsupported streamed export schema')
        index_proof = descriptor.get('request_index') or {}
        index_path = Path(index_proof.get('path', ''))
        if (not index_path.is_file() or index_path.stat().st_size != index_proof.get('bytes')):
            raise ValueError('streamed export request index changed')
        index_stream = index_path.open('rb')
        if hashlib.file_digest(index_stream, 'sha256').hexdigest() != index_proof.get('sha256'):
            index_stream.close()
            raise ValueError('streamed export request index changed')
        index_stream.seek(0)
        shards = descriptor.get('shards') or []
        values = descriptor.get('runtime_identity_values') or {}
        value_db = value_db_path = None
        try:
            for proof in shards:
                path = Path(proof.get('path', ''))
                if not path.is_file() or path.stat().st_size != proof.get('bytes'):
                    raise ValueError('streamed export archive shard changed')
                with path.open('rb') as stream:
                    if hashlib.file_digest(stream, 'sha256').hexdigest() != proof.get('sha256'):
                        raise ValueError('streamed export archive shard changed')
            if values:
                value_path = Path(values.get('path', ''))
                if (not value_path.is_file()
                        or value_path.stat().st_size != values.get('bytes')):
                    raise ValueError('runtime identity value store changed')
                value_stream = value_path.open('rb')
                if hashlib.file_digest(value_stream, 'sha256').hexdigest() != values.get('sha256'):
                    value_stream.close()
                    raise ValueError('runtime identity value store changed')
                value_stream.seek(0)
                temporary = NamedTemporaryFile(prefix='runtime-values-', suffix='.sqlite',
                                               delete=False)
                value_db_path = Path(temporary.name); temporary.close()
                value_db = sqlite3.connect(value_db_path)
                value_db.execute('CREATE TABLE values_by_sha (sha256 TEXT PRIMARY KEY)')
                rows = 0
                with value_stream:
                    for raw_line in value_stream:
                        if not raw_line.strip():
                            continue
                        item = json.loads(raw_line)
                        encoded = json.dumps(item.get('value'), sort_keys=True,
                                             separators=(',', ':'), allow_nan=False).encode()
                        if hashlib.sha256(encoded).hexdigest() != item.get('sha256'):
                            raise ValueError('runtime identity value store row changed')
                        try:
                            value_db.execute('INSERT INTO values_by_sha VALUES (?)',
                                             (item['sha256'],))
                        except sqlite3.IntegrityError as exc:
                            raise ValueError('duplicate runtime identity value-store row') from exc
                        rows += 1
                value_db.commit()
                if rows != values.get('values'):
                    raise ValueError('runtime identity value-store row count changed')
            requests_seen = observations = transformations = 0
            with index_stream:
                for raw_line in index_stream:
                    if not raw_line.strip():
                        continue
                    row = json.loads(raw_line)
                    if (row.get('source') != descriptor.get('source')
                            or row.get('content_type') != 'application/json'
                            or row.get('content_encoding') not in ('', None)):
                        raise ValueError('streamed export request framing changed')
                    shard = row.get('shard')
                    if type(shard) is not int or not 0 <= shard < len(shards):
                        raise ValueError('streamed export request has invalid shard')
                    path = Path(shards[shard]['path'])
                    offset, length = row.get('offset'), row.get('length')
                    if (type(offset) is not int or type(length) is not int
                            or offset < 0 or length <= 0 or offset + length > path.stat().st_size):
                        raise ValueError('streamed export request has invalid byte range')
                    body = _ArchiveSlice(path, offset, length)
                    digest, seen = hashlib.sha256(), 0
                    while chunk := body.read(1024 * 1024):
                        digest.update(chunk); seen += len(chunk)
                    if seen != length or digest.hexdigest() != row.get('sha256'):
                        body.close()
                        raise ValueError('streamed export request body changed')
                    body.seek(0)
                    refs = row.get('runtime_identity_transformation_refs') or []
                    if refs and value_db is None:
                        raise ValueError('streamed transformation lacks value store')
                    for ref in refs:
                        if (not isinstance(ref, dict) or set(ref) != {'sha256'}
                                or value_db.execute('SELECT 1 FROM values_by_sha WHERE sha256=?',
                                                    (ref.get('sha256'),)).fetchone() is None):
                            raise ValueError('streamed transformation value reference is unavailable')
                    requests_seen += 1; observations += int(row.get('observations', 0))
                    transformations += len(refs)
                    if materialize:
                        retained = body.read(); body.close()
                        yield row, retained
                    else:
                        yield row, body
            if (requests_seen != descriptor.get('requests')
                    or observations != descriptor.get('observations')
                    or transformations != descriptor.get('runtime_identity_transformations')):
                raise ValueError('streamed export request index count changed')
        finally:
            if not index_stream.closed:
                index_stream.close()
            if value_db is not None:
                value_db.close()
            if value_db_path is not None:
                value_db_path.unlink(missing_ok=True)


def _request_manifests(manifest):
    groups = manifest.get('ordered_request_group_manifests') or []
    if not groups:
        return [manifest]
    loaded, observations = [], 0
    for proof in groups:
        path = Path(proof.get('path', ''))
        if not path.is_file():
            raise ValueError('ordered request-group manifest changed')
        body = path.read_bytes()
        if (len(body) != proof.get('bytes')
                or hashlib.sha256(body).hexdigest() != proof.get('sha256')):
            raise ValueError('ordered request-group manifest changed')
        group = json.loads(body)
        if group.get('ordered_request_group_manifests'):
            raise ValueError('nested ordered request groups are unsupported')
        loaded.append(group); observations += int(group.get('observations', 0))
    if observations != manifest.get('observations'):
        raise ValueError('ordered request-group observation count changed')
    return loaded


def _ordered_manifest_requests(manifest, *, materialize=False):
    """Merge legacy and streamed storage forms by original request ordinal."""
    exports, streams = manifest.get('exports', []), manifest.get('stream_exports', [])
    if not streams:
        yield from ((item, None) for item in exports)
        return
    iterators = [iter((item, None) for item in exports)]
    iterators.extend(_verified_stream_requests(
        {'stream_exports': [descriptor]}, materialize=materialize) for descriptor in streams)
    expected = 1
    for item, body in heapq.merge(*iterators, key=lambda pair: pair[0].get('request_order', -1)):
        order = item.get('request_order')
        if type(order) is not int or order != expected:
            if body is not None and not materialize:
                body.close()
            raise ValueError('retained request order is missing, duplicate or changed')
        expected += 1
        yield item, body


def _tail(path, limit=8192):
    with Path(path).open('rb') as stream:
        stream.seek(0, os.SEEK_END)
        stream.seek(max(0, stream.tell() - limit))
        return stream.read().decode('utf-8', errors='replace')


def _retain_ingest_error(response, export, run_dir, endpoint, export_index):
    """Keep the full failure body; console excerpts never replace stored bytes."""
    body = response.content
    evidence = {'http_status': response.status_code, 'endpoint': endpoint,
                'export_index': export_index, 'export': dict(export),
                'response_headers': dict(response.headers),
                'response_body_file': 'ingest-error-body.bin',
                'response_body_representation': 'requests response.content, with content encoding decoded',
                'response_body_bytes': len(body),
                'response_body_sha256': hashlib.sha256(body).hexdigest(),
                'observed_ns': time.time_ns(), 'branch_runtime': str(run_dir),
                'ingest_retried': False}
    try:
        (run_dir / evidence['response_body_file']).write_bytes(body)
        write_json(run_dir / 'ingest-error.json', evidence)
    except OSError as error:
        # Disk failure must not erase the original receiver error from stdout.
        evidence['retention_error'] = repr(error)
    console = {key: evidence[key] for key in ('http_status', 'endpoint', 'export_index',
        'response_body_bytes', 'response_body_sha256', 'branch_runtime', 'ingest_retried')}
    console['export_source'] = export['source']
    console['export_sha256'] = export['sha256']
    console['body_tail'] = body[-8192:].decode('utf-8', errors='replace')
    if evidence.get('retention_error'):
        console['retention_error'] = evidence['retention_error']
    try:
        console['bering_log_tail'] = _tail(run_dir / 'bering.log')
    except OSError as error:
        console['bering_log_error'] = repr(error)
    print('BERING_INGEST_FAILURE ' + json.dumps(console), flush=True)
    return evidence


def replay(binary, manifest, folder, domain, overlay=None, prefix='model', *,
           publication_mode='on_shutdown', source_profile=None, joint_otlp=False):
    """One offline discovery batch, with all graph construction inside Bering.

    New runs publish only on shutdown, without a clock window. Explicit windowed
    mode preserves historical diagnostics on their original Bering binary. A
    split or dropped batch is a technical failure, never a successful forecast.
    """
    if publication_mode not in ('on_shutdown', 'windowed'):
        raise ValueError('unsupported Bering publication mode: '+str(publication_mode))
    folder = Path(folder).resolve()
    run_dir = folder / (prefix + '-runtime')
    run_dir.mkdir(parents=True, exist_ok=False)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    snapshot_path = folder / (prefix + '.snapshot.json')
    quality_path = folder / (prefix + '.signal-quality.json')
    request_manifests = _request_manifests(manifest)
    exports = [item for group in request_manifests for item in group.get('exports', [])]
    stream_exports = [item for group in request_manifests
                      for item in group.get('stream_exports', [])]
    count = manifest['observations']
    profile = dict(source_profile or {'source_id': 'obi', 'input_type': 'ebpf-obi'})
    source_id, input_type = profile.get('source_id'), profile.get('input_type')
    if input_type == 'ebpf-obi' and source_id == 'obi':
        source_id, source = 'obi', {'id': 'obi', 'type': 'ebpf-obi', 'domain': domain,
                                    'capture_directory': str(run_dir / 'obi-capture')}
        expected_connector = 'obi'
    elif input_type == 'ebpf-otlp' and isinstance(source_id, str) and source_id:
        source = {'id': source_id, 'type': 'ebpf-otlp',
                  'domain': domain, 'capture_directory': str(run_dir / 'ebpf-capture')}
        expected_connector = 'ebpf-otlp'
    else:
        raise ValueError('invalid Bering logical source profile')
    config = {
        'server': {'listen_address': f'127.0.0.1:{port}', 'grpc_listen_address': '',
                   'max_request_bytes': max([5242880, *(decoded_size(e) + 1 for e in exports),
                        *(int(e.get('max_request_bytes', 0)) + 1 for e in stream_exports)])},
        'sources': [source],
        'runtime': {'max_in_memory_spans': max(1, count + 1),
                    'reconciliation': {'enabled': False}},
        'sink': {'directory': str(run_dir / 'snapshots'), 'latest_path': str(snapshot_path),
                 'signal_quality_path': str(quality_path)},
        'logging': {'structured': True}, 'overlays': [str(Path(overlay).resolve())] if overlay else [],
    }
    if publication_mode == 'on_shutdown':
        config['runtime']['publication_mode'] = 'on_shutdown'
    else:
        # Bering 1.1.1 predates publication_mode; keep its original configuration.
        config['runtime'].update(flush_interval='24h', window_size='24h',
                                 late_span_policy='current_window')
    config_path = run_dir / 'serve.yaml'
    config_path.write_text(yaml.safe_dump(config), encoding='utf-8')
    argv = [str(Path(binary).resolve()), 'serve', '--config', str(config_path)]
    resource_path = run_dir / 'bering-resources.json'
    supervisor_argv = [sys.executable, str(Path(__file__).with_name('child_resources_v4.py')),
                       '--report', str(resource_path), '--', *argv]
    record = {'argv': argv, 'started_ns': time.time_ns(), 'input_observations': count,
              'publication_mode': publication_mode,
              'source_domain': domain, 'source_profile': profile,
              'clock_admission_filter': False,
              'discovery_mode': 'one offline batch; no historical reconciliation',
              'child_resource_report': str(resource_path), 'accepted_ingest_requests': []}
    if joint_otlp:
        record.update(request_routing='ordinary_otlp_joint_view',
                      original_source_profile=profile, declared_ebpf_collection_domain=domain,
                      source_profile={'input_type': 'otlp', 'trace_context_domain': ''},
                      source_domain='', original_export_roles_retained=True)
    child_env, go_environment = _child_process_environment()
    record['go_runtime_environment'] = go_environment
    process = None
    try:
        with (run_dir / 'bering.log').open('wb') as log:
            popen_options = {'stdout': log, 'stderr': subprocess.STDOUT}
            if child_env is not None:
                popen_options['env'] = child_env
            process = subprocess.Popen(supervisor_argv, **popen_options)
            # Startup readiness only: no workload observation is measured here.
            ready_started = time.monotonic()
            while True:
                if process.poll() is not None:
                    raise RuntimeError('Bering exited before source readiness')
                try:
                    if requests.get(base + '/readyz', timeout=1).status_code == 200:
                        break
                except requests.RequestException:
                    pass
                if time.monotonic() - ready_started > 120:
                    raise RuntimeError('Bering technical startup failed; inspect retained log')
                time.sleep(.1)
            accepted_stream_path = run_dir / 'accepted-stream-requests.jsonl'
            accepted_stream_digest = hashlib.sha256(); accepted_stream_count = 0
            accepted_sequence_path = run_dir / 'accepted-request-sequence.jsonl'
            accepted_sequence_digest = hashlib.sha256(); accepted_sequence_count = 0
            request_iterator = itertools.chain.from_iterable(
                _ordered_manifest_requests(group, materialize=False)
                for group in request_manifests)
            with (accepted_stream_path.open('wb') as accepted_stream,
                  accepted_sequence_path.open('wb') as accepted_sequence):
              for export_index, (export, streamed_body) in enumerate(request_iterator):
                endpoint = (f'/sources/{source_id}/v1/traces'
                            if export['source'] == 'ebpf' and not joint_otlp else '/v1/traces')
                path = Path(export['path']) if streamed_body is None else None
                content_length = (path.stat().st_size if path is not None
                                  else int(export['length']))
                headers = {'Content-Type': export['content_type'],
                           'Content-Length': str(content_length)}
                if export.get('content_encoding'):
                    headers['Content-Encoding'] = export['content_encoding']
                # Verify, rewind, then stream the identical retained wire file.
                # This avoids an avoidable whole-export sender copy; Bering still
                # receives the original bytes, framing metadata, and encoding.
                if path is not None:
                    with path.open('rb') as stream:
                        if hashlib.file_digest(stream, 'sha256').hexdigest() != export['sha256']:
                            raise RuntimeError('Selected export changed before Bering ingest')
                        stream.seek(0)
                        response = requests.post(base + endpoint, data=stream,
                            headers=headers, timeout=None)
                else:
                    try:
                        response = requests.post(base + endpoint, data=streamed_body,
                            headers=headers, timeout=None)
                    finally:
                        streamed_body.close()
                if response.status_code >= 400:
                    record['ingest_error'] = _retain_ingest_error(
                        response, export, run_dir, endpoint, export_index)
                response.raise_for_status()
                accepted = {
                    'http_status': response.status_code,
                    'endpoint': endpoint,
                    'export_index': export_index,
                    'content_bytes': content_length,
                    'content_sha256': export['sha256'],
                }
                if joint_otlp:
                    accepted['original_source'] = export['source']
                if streamed_body is None:
                    record['accepted_ingest_requests'].append(accepted)
                else:
                    line = json.dumps(accepted, sort_keys=True, separators=(',', ':')).encode()+b'\n'
                    accepted_stream.write(line); accepted_stream_digest.update(line)
                    accepted_stream_count += 1
                sequence_line = json.dumps({**accepted,
                    'storage_form': ('ordinary_export' if streamed_body is None
                                     else 'stream_archive_slice')},
                    sort_keys=True, separators=(',', ':')).encode()+b'\n'
                accepted_sequence.write(sequence_line); accepted_sequence_digest.update(sequence_line)
                accepted_sequence_count += 1
            if accepted_stream_count:
                record['accepted_stream_requests'] = {
                    'path': str(accepted_stream_path), 'requests': accepted_stream_count,
                    'bytes': accepted_stream_path.stat().st_size,
                    'sha256': accepted_stream_digest.hexdigest(),
                    'same_http_body_order_as_request_index': True}
            else:
                accepted_stream_path.unlink(missing_ok=True)
            record['accepted_request_sequence'] = {
                'path': str(accepted_sequence_path), 'requests': accepted_sequence_count,
                'bytes': accepted_sequence_path.stat().st_size,
                'sha256': accepted_sequence_digest.hexdigest(),
                'same_order_as_original_request_ordinals_and_source_groups': True}
            process.send_signal(signal.SIGTERM)
            record['returncode'] = process.wait()
            if record['returncode']:
                raise RuntimeError('Bering failed while publishing the replayed graph')
        snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
        published = [p for p in (run_dir / 'snapshots').glob('*.json')
                     if not p.name.endswith('.signal-quality.json')]
        ingest = snapshot['ingest']
        record['ingest'] = ingest
        if len(published) != 1 or ingest['spans'] != count or ingest['dropped_spans']:
            raise RuntimeError(f'Incomplete or split Bering replay batch: {ingest}, publications={len(published)}')
        if sum(s.get('observations', 0) for s in snapshot['sources']) != count:
            raise RuntimeError('Bering source accounting differs from replayed raw inputs')
        if not joint_otlp and (any(e['source'] == 'ebpf' for e in exports)
                or any(e['source'] == 'ebpf' for e in stream_exports)) and not any(
                s['type'] == 'ebpf' and s['connector'] == expected_connector
                for s in snapshot['sources']):
            raise RuntimeError('Bering output lost its declared logical source attribution')
        # Extract the model emitted by Bering without adding nodes or edges.
        write_json(folder / (prefix + '.json'), snapshot['model'])
        record['status'] = 'complete'
        return snapshot['model'], json.loads(quality_path.read_text(encoding='utf-8'))
    except BaseException as exc:
        record.update(status='technical_failure', error=str(exc))
        raise
    finally:
        if process is not None and process.poll() is None:
            process.send_signal(signal.SIGTERM)
            process.wait()
        if process is not None:
            record.setdefault('returncode', process.returncode)
        if resource_path.exists():
            record['child_resources'] = json.loads(resource_path.read_text(encoding='utf-8'))
        else:
            record['child_resources_unavailable'] = 'child wrapper did not produce a resource report'
        record['ended_ns'] = time.time_ns()
        write_json(run_dir / 'replay-command.json', record)
