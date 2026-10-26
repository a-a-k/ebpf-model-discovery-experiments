"""Normalize actual OTLP and Jaeger observations; never construct missing spans."""
from __future__ import annotations
import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


def value(item):
    if not isinstance(item, dict):
        return item
    if 'arrayValue' in item:
        return [value(v) for v in item['arrayValue'].get('values', [])]
    if 'kvlistValue' in item:
        return attributes(item['kvlistValue'].get('values', []))
    return next(iter(item.values()), None)


def attributes(items):
    return {v['key']: value(v.get('value')) for v in items}


def identifier(raw, encoding='hex'):
    if not raw:
        return ''
    return base64.b64decode(raw).hex() if encoding == 'base64' else raw.lower()


def normalized_route(raw):
    path = urlsplit(raw).path
    return re.sub(r'/([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}|[0-9a-fA-F]{24,})(?=/|$)', '/{id}', path)


def otlp(payload, source, node, encoding='hex'):
    for resource in payload.get('resourceSpans', []):
        attrs = attributes(resource.get('resource', {}).get('attributes', []))
        for scope in resource.get('scopeSpans', resource.get('instrumentationLibrarySpans', [])):
            for span in scope.get('spans', []):
                a = attributes(span.get('attributes', []))
                yield {
                    'source': source, 'node': node,
                    'trace_id': identifier(span.get('traceId'), encoding),
                    'span_id': identifier(span.get('spanId'), encoding),
                    'parent_id': identifier(span.get('parentSpanId'), encoding),
                    'service': attrs.get('service.name', 'unknown'),
                    'instance': attrs.get('service.instance.id'),
                    'name': span.get('name'), 'kind': span.get('kind'),
                    'start_ns': int(span.get('startTimeUnixNano', 0)),
                    'end_ns': int(span.get('endTimeUnixNano', 0)),
                    'attributes': a, 'resource': attrs, 'status': span.get('status', {}),
                    'links': [{'trace_id': identifier(l.get('traceId'), encoding),
                               'span_id': identifier(l.get('spanId'), encoding)} for l in span.get('links', [])],
                }


def jaeger(payload, source='native'):
    for trace in payload.get('data', []):
        if not isinstance(trace, dict) or 'spans' not in trace:
            continue
        processes = trace.get('processes', {})
        for s in trace['spans']:
            process = processes.get(s.get('processID'), {})
            a = {x['key']: x.get('value') for x in s.get('tags', [])}
            refs = [r for r in s.get('references', []) if r.get('refType') == 'CHILD_OF']
            resource = {x['key']: x.get('value') for x in process.get('tags', [])}
            instance = resource.get('service.instance.id') or resource.get('hostname') or resource.get('host.name') or resource.get('ip')
            yield {'source': source, 'node': None, 'trace_id': s['traceID'].lower(),
                   'span_id': s['spanID'].lower(), 'parent_id': refs[0]['spanID'].lower() if len(refs) == 1 else '',
                   'service': process.get('serviceName', 'unknown'), 'instance': instance,
                   'name': s.get('operationName'), 'kind': a.get('span.kind'),
                   'start_ns': int(s.get('startTime', 0)) * 1000,
                   'end_ns': (int(s.get('startTime', 0)) + int(s.get('duration', 0))) * 1000,
                   'attributes': a, 'resource': resource,
                   'status': {'code': 'STATUS_CODE_ERROR'} if a.get('error') else {}, 'links': []}


def read_spans(root: Path, native: Path | None = None):
    spans, errors = [], []
    paths = [(p, 'ebpf') for p in root.glob('[ab].jsonl')]
    if (root / 'native.jsonl').exists():
        paths.append((root / 'native.jsonl', 'native'))
    if native and native.exists():
        paths += [(p, 'native') for p in sorted(native.rglob('*')) if p.name.startswith(('traces', 'native-node-')) and p.suffix in {'.json', '.jsonl'}]
    for path, source in paths:
        text = path.read_text(encoding='utf-8').strip()
        if not text:
            continue
        try:
            try:
                documents = [json.loads(text)]
            except json.JSONDecodeError:
                documents = [json.loads(line) for line in text.splitlines() if line.strip()]
            for document in documents:
                payload = document.get('payload', document)
                node = path.stem if source == 'ebpf' else (path.stem[-1] if path.stem.startswith('native-node-') else None)
                encoding = document.get('id_encoding', 'hex')
                rows = list(otlp(payload, source, node, encoding))
                if not rows:
                    rows = list(jaeger(payload))
                for row in rows:
                    row['raw_file'] = str(path)
                spans.extend(rows)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({'file': str(path), 'error': str(exc)})
    unique = {}
    for span in spans:
        # Repeated exports are harmless; conflicting same-ID observations must
        # survive so identity matchers can reject ambiguity rather than pick the
        # last file arbitrarily. File provenance is not semantic evidence.
        evidence = {k: v for k, v in span.items() if k not in ('raw_file', '_graph_node')}
        canonical = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        key = (span['source'], span['node'], span['trace_id'], span['span_id'], canonical)
        unique[key] = span
    return list(unique.values()), errors


def step_id(span):
    for key, val in span['attributes'].items():
        if key.lower().replace('_', '-').endswith('x-experiment-request-id'):
            if isinstance(val, list):
                return val[0] if len(val) == 1 else None
            return val
    return None


def route(span):
    a = span['attributes']
    method = a.get('http.request.method', a.get('http.method'))
    path = a.get('http.route', a.get('url.path', a.get('http.target', a.get('url.full', a.get('http.url')))))
    return f'{method} {normalized_route(str(path))}' if method and path else None


def graph(spans):
    nodes, edges, cross_node, databases = {}, set(), [], {}
    by_id = {}
    for s in spans:
        key = (s['trace_id'], s['span_id'])
        by_id.setdefault(key, []).append(s)
        identity = f"service:{s['service']}:{s['instance'] or 'unknown'}:{s['node'] or 'unknown'}"
        s['_graph_node'] = identity
        nodes[identity] = {'id': identity, 'kind': 'service', 'service': s['service'],
                           'instance': s['instance'], 'guest': s['node'], 'source': s['source']}
        a = s['attributes']
        db = a.get('db.system.name', a.get('db.system'))
        if db and s['kind'] in ('SPAN_KIND_CLIENT', 3, 'client'):
            address = a.get('server.address', a.get('net.peer.name', a.get('net.peer.ip')))
            port = a.get('server.port', a.get('net.peer.port'))
            namespace = a.get('db.namespace', a.get('db.name'))
            dbid = f'db:{db}:{address or "unknown"}:{port or "unknown"}:{namespace or "unknown"}'
            complete_endpoint = bool(address and str(address).strip()) and str(port).isdigit() and 1 <= int(port) <= 65535
            if not complete_endpoint:
                # An unknown endpoint is not a shared database identity.
                dbid += ':unresolved-for:' + identity
            nodes[dbid] = {'id': dbid, 'kind': 'database', 'system': db, 'address': address,
                           'port': port, 'namespace': namespace, 'source': s['source'],
                           'complete_endpoint_observed': complete_endpoint,
                           'numeric_address_observed': bool(address and re.fullmatch(r'\d+\.\d+\.\d+\.\d+', str(address))),
                           'concrete_instance_confirmed': None}
            edges.add((identity, dbid, 'database_client_span'))
            if complete_endpoint:
                databases.setdefault(dbid, set()).add(s['service'])
    for s in spans:
        for p in by_id.get((s['trace_id'], s['parent_id']), []):
            if p['_graph_node'] != s['_graph_node']:
                edges.add((p['_graph_node'], s['_graph_node'], 'observed_parent_id'))
            if p['node'] and s['node'] and p['node'] != s['node']:
                cross_node.append({'trace_id': s['trace_id'], 'parent_id': p['span_id'],
                                   'child_id': s['span_id'], 'from': p['node'], 'to': s['node'],
                                   'evidence': 'observed_parent_id', 'external_correctness': None})
    return {'nodes': list(nodes.values()), 'edges': [dict(zip(('from', 'to', 'evidence'), e)) for e in sorted(edges)],
            'cross_node': cross_node,
            'shared_database_dependencies': {k: sorted(v) for k, v in databases.items() if len(v) > 1},
            'cross_node_error_rate': None,
            'cross_node_error_rate_note': 'Requires independent per-request linking evidence; adjacency is not correctness.'}


def opaque_attempt(record):
    return hashlib.sha256(record['attempt_id'].encode()).hexdigest()


def census(records, phase, state):
    """Strict allow-list boundary: evaluator labels, payloads and outcomes cannot enter fitting."""
    return [{'attempt_key': opaque_attempt(r), 'step_ids': [s.get('request_id') for s in r['http_steps']],
             'phase': phase, 'state': state} for r in records]
