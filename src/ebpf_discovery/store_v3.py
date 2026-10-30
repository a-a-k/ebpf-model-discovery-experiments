"""Streaming, loss-preserving normalization into a bounded-memory SQLite index."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sqlite3
import time

import ijson
from .observations import otlp, jaeger, step_id


def attribute_conflicts(items, *, jaeger_tags=False):
    """Preserve distinct repeated raw values before a dict can hide them."""
    values = {}
    for item in items:
        key = item['key'] if jaeger_tags else item.get('key', '')
        values.setdefault(key, set()).add(json.dumps(item.get('value'), sort_keys=True))
    return [{'key': key, 'raw_values': [json.loads(v) for v in sorted(variants)]}
            for key, variants in values.items() if len(variants) > 1]


def otlp_conflicts(payload):
    for resource in payload.get('resourceSpans', []):
        common = attribute_conflicts(resource.get('resource', {}).get('attributes', []))
        for scope in resource.get('scopeSpans', resource.get('instrumentationLibrarySpans', [])):
            for span in scope.get('spans', []):
                yield common+attribute_conflicts(span.get('attributes', []))


class LimitedReader:
    def __init__(self, stream, size):
        self.stream, self.remaining = stream, size

    def read(self, size=-1):
        size = self.remaining if size < 0 else min(size, self.remaining)
        result = self.stream.read(size)
        self.remaining -= len(result)
        return result


def complete_prefix(path):
    size = path.stat().st_size
    if path.suffix != '.jsonl' or not size:
        return size
    with path.open('rb') as stream:
        position = size
        while position:
            length = min(position, 65536)
            position -= length
            stream.seek(position)
            end = stream.read(length).rfind(b'\n')
            if end >= 0:
                return position+end+1
        return 0  # an in-flight first record has no complete prefix yet


def normalized_file(path, source, offset, limit, *, same_trace_parents=False):
    """Native Jaeger documents stream one trace; OTLP exports stream one batch."""
    node = path.stem if source == 'ebpf' else (path.stem[-1] if path.stem.startswith('native-node-') else None)
    is_jaeger = path.name.startswith('traces-') and path.suffix == '.json'
    with path.open('rb') as stream:
        stream.seek(offset)
        limited = LimitedReader(stream, limit-offset)
        prefix = 'data.item' if is_jaeger else ''
        for document in ijson.items(limited, prefix, multiple_values=not is_jaeger, use_float=True):
            if is_jaeger:
                records = jaeger({'data': [document]}, same_trace_parents=same_trace_parents)
                conflicts = (attribute_conflicts(span.get('tags', []), jaeger_tags=True)+
                    attribute_conflicts(document.get('processes', {}).get(span.get('processID'), {}).get('tags', []), jaeger_tags=True)
                    for span in document.get('spans', []))
            else:
                payload = document.get('payload', document)
                records = otlp(payload, source, node, document.get('id_encoding', 'hex'))
                conflicts = otlp_conflicts(payload)
            for record, conflicting in zip(records, conflicts, strict=True):
                record['raw_file'] = str(path)
                if conflicting:
                    record['attribute_conflicts'] = conflicting
                    # Keep the raw alternatives above; never supply an arbitrary
                    # last-written primitive to discovery.
                    for item in conflicting:
                        record['attributes'].pop(item['key'], None)
                yield record


class ObservationStore:
    def __init__(self, path, *, same_trace_parents=False):
        self.same_trace_parents = same_trace_parents
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute('PRAGMA cache_size=-65536')
        self.db.execute('PRAGMA temp_store=FILE')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS spans (
            digest TEXT PRIMARY KEY, source TEXT, node TEXT, trace TEXT, span TEXT,
            parent TEXT, service TEXT, instance TEXT, request TEXT, kind TEXT,
            start INTEGER, end INTEGER, dbsystem TEXT, address TEXT, port TEXT,
            namespace TEXT, conflicted INTEGER NOT NULL, data TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS request_idx ON spans(source,request);
          CREATE INDEX IF NOT EXISTS request_all_idx ON spans(request);
          CREATE INDEX IF NOT EXISTS identity_idx ON spans(source,trace,span);
          CREATE INDEX IF NOT EXISTS parent_idx ON spans(source,trace,parent);
          CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, consumed INTEGER);
          CREATE TABLE IF NOT EXISTS links (source TEXT, linked_trace TEXT, linked_span TEXT, trace TEXT,
            UNIQUE(source,linked_trace,linked_span,trace));
          CREATE INDEX IF NOT EXISTS link_idx ON links(source,linked_trace,linked_span);
        ''')

    def ingest(self, observation_root, native_root):
        started = time.perf_counter()
        paths = [(p, 'ebpf') for p in sorted(Path(observation_root).glob('[ab].jsonl'))]
        native_receiver = Path(observation_root)/'native.jsonl'
        if native_receiver.exists():
            paths.append((native_receiver, 'native'))
        paths += [(p, 'native') for p in sorted(Path(native_root).rglob('*'))
                  if p.is_file() and p.name.startswith(('traces', 'native-node-'))
                  and p.suffix in ('.json', '.jsonl')]
        manifest = []
        for path, source in paths:
            found = self.db.execute('SELECT consumed FROM files WHERE path=?', (str(path),)).fetchone()
            offset = found[0] if found else 0
            limit = complete_prefix(path)
            if limit < offset:
                raise ValueError(f'Observation file was truncated: {path}')
            if limit == offset:
                continue
            # Closed JSON documents are immutable snapshots; JSONL may append.
            if offset and path.suffix != '.jsonl':
                raise ValueError(f'Closed native snapshot changed: {path}')
            seen, added = 0, 0
            try:
                for row in normalized_file(path, source, offset, limit, same_trace_parents=self.same_trace_parents):
                    seen += 1
                    a = row['attributes']
                    evidence = {k: v for k, v in row.items() if k != 'raw_file'}
                    canonical = json.dumps(evidence, sort_keys=True, separators=(',', ':'), allow_nan=False)
                    fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
                    cur = self.db.execute('INSERT OR IGNORE INTO spans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (fingerprint, row['source'], row.get('node'), row['trace_id'], row['span_id'],
                         row['parent_id'], row['service'], row.get('instance'), step_id(row), str(row['kind']),
                         row['start_ns'], row['end_ns'], a.get('db.system.name', a.get('db.system')),
                         a.get('server.address', a.get('net.peer.name', a.get('net.peer.ip'))),
                         str(a.get('server.port', a.get('net.peer.port'))) if a.get('server.port', a.get('net.peer.port')) is not None else None,
                         a.get('db.namespace', a.get('db.name')), int(bool(row.get('attribute_conflicts'))),
                         json.dumps(row, separators=(',', ':'), allow_nan=False)))
                    added += cur.rowcount
                    for link in row.get('links', []):
                        self.db.execute('INSERT OR IGNORE INTO links VALUES (?,?,?,?)',
                            (row['source'], link.get('trace_id'), link.get('span_id'), row['trace_id']))
                    if seen % 5000 == 0:
                        self.db.commit()
                self.db.execute('INSERT OR REPLACE INTO files VALUES (?,?)', (str(path), limit))
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            manifest.append({'path': str(path), 'source': source, 'from_byte': offset, 'through_byte': limit,
                             'raw_spans': seen, 'new_unique_observations': added})
        return {'files': manifest, 'total_unique_observations': self.db.execute('SELECT COUNT(*) FROM spans').fetchone()[0],
                'index_bytes': self.path.stat().st_size, 'seconds': time.perf_counter()-started,
                'discard_policy': 'only byte-equivalent normalized duplicates; conflicting observations retained'}

    def _records(self, sql, params=()):
        return [json.loads(row[0]) for row in self.db.execute(sql, params)]

    def candidates(self, source, request_id):
        return self._records('SELECT data FROM spans WHERE source=? AND request=?', (source, request_id))

    def identity(self, source, trace, span):
        return self._records('SELECT data FROM spans WHERE source=? AND trace=? AND span=?', (source, trace, span))

    def request_traces(self, rows, *, linked_consumers=False):
        """Complete traces selected by exact request IDs, plus exact linked traces."""
        traces = set()
        for row in rows:
            for identity in row['step_ids']:
                traces.update(self.db.execute('SELECT DISTINCT source,trace FROM spans WHERE request=?', (identity,)))
        if linked_consumers:
            for source, trace in tuple(traces):
                traces.update((source, item[0]) for item in self.db.execute(
                    'SELECT DISTINCT trace FROM links WHERE source=? AND linked_trace=?', (source, trace)))
        result = []
        for source, trace in sorted(traces):
            result.extend(self._records('SELECT data FROM spans WHERE source=? AND trace=?', (source, trace)))
        return result

    def descendants(self, root):
        source, trace = root['source'], root['trace_id']
        queue, seen, output = [root], set(), []
        while queue:
            row = queue.pop()
            sid = row['span_id']
            if sid in seen:
                continue
            seen.add(sid)
            variants = self.identity(source, trace, sid)
            if len(variants) != 1 or row.get('attribute_conflicts'):
                continue
            output.append(row)
            queue.extend(self._records('SELECT data FROM spans WHERE source=? AND trace=? AND parent=?', (source, trace, sid)))
        return output

    def entry_observations(self, services):
        query = 'SELECT data FROM spans WHERE service IN ('+','.join('?' for _ in services)+') AND request IS NOT NULL'
        for row in self.db.execute(query, tuple(services)):
            yield json.loads(row[0])

    def graph(self, source):
        where, params = ('', ()) if source == 'combined' else (' WHERE source=?', (source,))
        nodes, edges = {}, set()
        sid = lambda s, n, v, i: f'{s}:service:{v}:{i or "unknown"}:{n or "unknown"}'
        for s, n, v, i in self.db.execute('SELECT DISTINCT source,node,service,instance FROM spans'+where, params):
            identity = sid(s, n, v, i)
            nodes[identity] = {'id': identity, 'kind': 'service', 'source': s, 'guest': n, 'service': v, 'instance': i}
        dbwhere = (' AND source=?', params) if source != 'combined' else ('', ())
        for s, n, v, i, system, addr, port, namespace in self.db.execute(
                """SELECT DISTINCT source,node,service,instance,dbsystem,address,port,namespace FROM spans s
                   WHERE dbsystem IS NOT NULL AND kind IN ('3','SPAN_KIND_CLIENT','client') AND conflicted=0
                   AND NOT EXISTS (SELECT 1 FROM spans x WHERE x.source=s.source AND x.trace=s.trace
                                   AND x.span=s.span AND x.digest != s.digest)"""+dbwhere[0], dbwhere[1]):
            caller = sid(s, n, v, i)
            identity = f'{s}:database:{system}:{addr}:{port}:{namespace}' if addr and port else f'{caller}:database:{system}:unknown'
            nodes[identity] = {'id': identity, 'kind': 'database', 'source': s, 'system': system,
                               'address': addr, 'port': port, 'namespace': namespace, 'concrete_instance_confirmed': None}
            edges.add((caller, identity, 'database_client_span'))
        scope = '' if source == 'combined' else ' AND c.source=?'
        for s, cn, cv, ci, pn, pv, pi in self.db.execute(
                '''SELECT DISTINCT c.source,c.node,c.service,c.instance,p.node,p.service,p.instance
                   FROM spans c JOIN spans p ON c.source=p.source AND c.trace=p.trace AND c.parent=p.span
                   WHERE c.parent != ''
                   AND c.conflicted=0 AND p.conflicted=0
                   AND NOT EXISTS (SELECT 1 FROM spans x WHERE x.source=c.source AND x.trace=c.trace
                                   AND x.span=c.span AND x.digest != c.digest)
                   AND NOT EXISTS (SELECT 1 FROM spans x WHERE x.source=p.source AND x.trace=p.trace
                                   AND x.span=p.span AND x.digest != p.digest) '''+scope, params):
            parent, child = sid(s, pn, pv, pi), sid(s, cn, cv, ci)
            if parent != child:
                edges.add((parent, child, 'source_local_observed_parent'))
        return {'nodes': list(nodes.values()), 'edges': [dict(zip(('from', 'to', 'evidence'), e)) for e in sorted(edges)],
                'source_separated_ancestry': True, 'independent_cross_node_correctness': None,
                'graph_is_not_the_state_conditional_predictor': True}

    def close(self):
        self.db.commit()
        self.db.close()
