"""Uncapped request transport and durable acquisition journal.

The journal is an evaluator artifact. It is never a source of discovered edges.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
import time
import uuid

import requests


class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS events '
                        '(seq INTEGER PRIMARY KEY, kind TEXT, wall_ns INTEGER, monotonic_ns INTEGER, data TEXT)')
        self.db.execute("CREATE INDEX IF NOT EXISTS transport_event_idx ON events "
                        "(kind, json_extract(data, '$.transport_id'))")
        self.db.commit()

    def append(self, kind, data=None, **fields):
        payload = dict(data or {}, **fields)
        with self.lock:
            self.db.execute('INSERT INTO events(kind,wall_ns,monotonic_ns,data) VALUES (?,?,?,?)',
                            (kind, time.time_ns(), time.monotonic_ns(),
                             json.dumps(payload, ensure_ascii=False, allow_nan=False, default=str)))
            self.db.commit()

    event = append

    def unresolved_transports(self):
        """An exception ends local observation, not the remote operation."""
        with self.lock:
            rows = self.db.execute("""
                SELECT started.data FROM events started
                WHERE started.kind='step_started' AND NOT EXISTS (
                  SELECT 1 FROM events finished WHERE finished.kind='step_finished'
                  AND json_extract(finished.data, '$.transport_id') =
                      json_extract(started.data, '$.transport_id'))
                ORDER BY started.seq
            """).fetchall()
        return [json.loads(row[0]) for row in rows]

    def export(self, path):
        with self.lock, Path(path).open('w', encoding='utf-8') as stream:
            for seq, kind, wall, mono, data in self.db.execute('SELECT * FROM events ORDER BY seq'):
                stream.write(json.dumps(dict(seq=seq, kind=kind, wall_ns=wall,
                                            monotonic_ns=mono, data=json.loads(data)))+'\n')

    def close(self):
        with self.lock:
            self.db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            self.db.close()


def request(method, url, *, journal=None, **kwargs):
    """requests-compatible complete-response API; no experiment timeout exists."""
    if kwargs.get('timeout') is not None:
        raise ValueError('Iteration 4 scientific HTTP requests cannot carry an experiment timeout')
    kwargs['timeout'] = None
    kwargs['stream'] = False
    headers = kwargs.get('headers') or {}
    request_id = next((v for k, v in headers.items()
                       if k.lower() == 'x-experiment-request-id'), None)
    body = kwargs.get('json', kwargs.get('data'))
    encoded = json.dumps(body, sort_keys=True, default=str).encode()
    detail = dict(transport_id=uuid.uuid4().hex, request_id=request_id, method=method.upper(), url=url,
                  request_body_intent_sha256=hashlib.sha256(encoded).hexdigest(),
                  experiment_timeout_seconds=None)
    if journal:
        journal.append('step_started', detail)
    started = time.monotonic_ns()
    try:
        response = requests.request(method, url, **kwargs)
        # Accessing content completes the body before a terminal record is written.
        content = response.content
        received_ns, received_monotonic_ns = time.time_ns(), time.monotonic_ns()
        if journal:
            journal.append('step_finished', dict(detail, status_code=response.status_code,
                body=response.text, body_sha256=hashlib.sha256(content).hexdigest(),
                response_body_base64=base64.b64encode(content).decode('ascii'),
                received_ns=received_ns, received_monotonic_ns=received_monotonic_ns,
                headers=dict(response.headers), elapsed_ns=time.monotonic_ns()-started,
                transport_state='complete'))
        return response
    except requests.RequestException as exc:
        if journal:
            journal.append('step_transport_unknown', dict(detail, error=repr(exc),
                elapsed_ns=time.monotonic_ns()-started, outcome=None))
        raise
