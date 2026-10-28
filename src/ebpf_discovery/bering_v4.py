"""Replay retained exports through Bering's actual native and OBI source inputs."""
from __future__ import annotations

import hashlib
import gzip
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
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
    """Scope diagnostic Go settings to Bering children, never other tools."""
    supplied = dict(overrides or {})
    unknown = set(supplied) - set(_GO_ENV_KEYS)
    if unknown or any(not isinstance(value, str) for value in supplied.values()):
        raise ValueError('Bering child environment only accepts string Go runtime settings')
    token = _CHILD_GO_ENV.set(supplied or None)
    try:
        yield
    finally:
        _CHILD_GO_ENV.reset(token)


def _child_process_environment():
    overrides = _CHILD_GO_ENV.get()
    inherited = {key: os.environ.get(key) for key in _GO_ENV_KEYS}
    if not overrides:
        return None, {'configured': False, 'inherited_go_environment': inherited,
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
    return environment, {'configured': True, 'inherited_go_environment': inherited,
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


def replay(binary, manifest, folder, domain, overlay=None, prefix='model'):
    """One offline discovery batch, with all graph construction inside Bering.

    The publication timer is not an observation filter. Native late records are
    admitted; OBI uses receipt-time admission. A split or dropped batch is a
    technical failure and never becomes a partial successful forecast.
    """
    folder = Path(folder).resolve()
    run_dir = folder / (prefix + '-runtime')
    run_dir.mkdir(parents=True, exist_ok=False)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    snapshot_path = folder / (prefix + '.snapshot.json')
    quality_path = folder / (prefix + '.signal-quality.json')
    exports = manifest['exports']
    count = manifest['observations']
    config = {
        'server': {'listen_address': f'127.0.0.1:{port}', 'grpc_listen_address': '',
                   'max_request_bytes': max([5242880, *(decoded_size(e) + 1 for e in exports)])},
        'sources': [{'id': 'obi', 'type': 'ebpf-obi', 'domain': domain,
                     'capture_directory': str(run_dir / 'obi-capture')}],
        'runtime': {'flush_interval': '24h', 'window_size': '24h',
                    'max_in_memory_spans': max(1, count + 1), 'late_span_policy': 'current_window',
                    'reconciliation': {'enabled': False}},
        'sink': {'directory': str(run_dir / 'snapshots'), 'latest_path': str(snapshot_path),
                 'signal_quality_path': str(quality_path)},
        'logging': {'structured': True}, 'overlays': [str(Path(overlay).resolve())] if overlay else [],
    }
    config_path = run_dir / 'serve.yaml'
    config_path.write_text(yaml.safe_dump(config), encoding='utf-8')
    argv = [str(Path(binary).resolve()), 'serve', '--config', str(config_path)]
    resource_path = run_dir / 'bering-resources.json'
    supervisor_argv = [sys.executable, str(Path(__file__).with_name('child_resources_v4.py')),
                       '--report', str(resource_path), '--', *argv]
    record = {'argv': argv, 'started_ns': time.time_ns(), 'input_observations': count,
              'source_domain': domain, 'clock_admission_filter': False,
              'discovery_mode': 'one offline batch; no historical reconciliation',
              'child_resource_report': str(resource_path)}
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
            for export in exports:
                path = Path(export['path'])
                endpoint = '/sources/obi/v1/traces' if export['source'] == 'ebpf' else '/v1/traces'
                headers = {'Content-Type': export['content_type'],
                           'Content-Length': str(path.stat().st_size)}
                if export.get('content_encoding'):
                    headers['Content-Encoding'] = export['content_encoding']
                # Verify, rewind, then stream the identical retained wire file.
                # This avoids an avoidable whole-export sender copy; Bering still
                # receives the original bytes, framing metadata, and encoding.
                with path.open('rb') as stream:
                    if hashlib.file_digest(stream, 'sha256').hexdigest() != export['sha256']:
                        raise RuntimeError('Selected export changed before Bering ingest')
                    stream.seek(0)
                    response = requests.post(base + endpoint, data=stream,
                        headers=headers, timeout=None)
                response.raise_for_status()
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
        if any(e['source'] == 'ebpf' for e in exports) and not any(
                s['type'] == 'ebpf' and s['connector'] == 'obi' for s in snapshot['sources']):
            raise RuntimeError('Bering output lost its OBI source attribution')
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
