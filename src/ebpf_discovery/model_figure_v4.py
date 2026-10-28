"""Render a saved Bering model without changing or inferring its graph."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def _q(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _attrs(values: dict[str, object]) -> str:
    return ', '.join(f'{key}={_q(value)}' for key, value in values.items())


def _validated(model: dict) -> tuple[list[dict], list[dict], list[dict]]:
    if not isinstance(model, dict):
        raise ValueError('Bering model must be an object')
    services, edges, endpoints = (model.get(key) for key in ('services', 'edges', 'endpoints'))
    if not all(isinstance(value, list) for value in (services, edges, endpoints)):
        raise ValueError('Bering model requires services, edges, and endpoints arrays')
    ids = [item.get('id') for item in services if isinstance(item, dict)]
    if len(ids) != len(services) or any(not isinstance(value, str) or not value for value in ids):
        raise ValueError('Bering service IDs must be nonempty strings')
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate Bering service ID would merge nodes in DOT')
    known = set(ids)
    if any(not isinstance(edge, dict) or edge.get('from') not in known or edge.get('to') not in known
           for edge in edges):
        raise ValueError('Bering edge refers to an absent service')
    if any(edge.get('kind') not in ('sync', 'async') for edge in edges):
        raise ValueError('Bering edge kind must be sync or async')
    if any(not isinstance(endpoint, dict) or endpoint.get('entry_service') not in known
           for endpoint in endpoints):
        raise ValueError('Bering endpoint refers to an absent service')
    return services, edges, endpoints


def dot_from_model(model: dict, original_sha256: str) -> str:
    """Pure renderer for synthetic unit fixtures; every observed edge is emitted."""
    if len(original_sha256) != 64 or any(char not in '0123456789abcdef' for char in original_sha256):
        raise ValueError('original model SHA-256 must be lowercase hexadecimal')
    services, edges, endpoints = _validated(model)
    by_service: dict[str, list[dict]] = {service['id']: [] for service in services}
    for endpoint in endpoints:
        by_service[endpoint['entry_service']].append(endpoint)
    lines = [
        'digraph bering_observed {',
        '  graph [' + _attrs({'label': 'Observed Bering model\nOriginal observed.json SHA-256: '+original_sha256,
                              'labelloc': 't', 'fontsize': '12', 'rankdir': 'LR'}) + '];',
        '  node [fontname="Helvetica", fontsize="10"];',
        '  edge [fontname="Helvetica", fontsize="9"];',
    ]
    for service in services:
        sid = service['id']
        labels = ((service.get('metadata') or {}).get('labels') or {})
        is_database = labels.get('bering.node.kind') == 'database'
        caption = [sid]
        if is_database:
            system = labels.get('db.system.name', 'database')
            identity = labels.get('bering.database.identity', 'identity unknown')
            caption.append(f'{system} database ({identity})')
            if labels.get('server.address'):
                address = labels['server.address']
                port = labels.get('server.port')
                caption.append(address + (f':{port}' if port else ''))
        for endpoint in by_service[sid]:
            method, path = endpoint.get('method') or '', endpoint.get('path') or ''
            caption.append('entry: ' + ((method + ' ' + path).strip() or str(endpoint.get('id') or 'unspecified')))
        node_attrs = {'label': '\n'.join(caption), 'tooltip': sid,
                      'shape': 'cylinder' if is_database else 'box',
                      'style': 'filled', 'fillcolor': '#e9f3fb' if is_database else '#f6f7f9'}
        lines.append(f'  {_q(sid)} [{_attrs(node_attrs)}];')
    for index, edge in enumerate(edges):
        identity = edge.get('identity') or {}
        detail = [str(edge.get('kind') or 'kind unspecified')]
        for key in ('protocol', 'operation', 'route', 'topic', 'span_kind'):
            if identity.get(key):
                detail.append(str(identity[key]))
        edge_attrs = {'label': '\n'.join(detail),
                      'tooltip': str(edge.get('id') or f'input edge index {index}'),
                      'id': f'bering-edge-{index}',
                      'style': 'dashed' if edge.get('kind') == 'async' else 'solid'}
        lines.append(f'  {_q(edge["from"])} -> {_q(edge["to"])} [{_attrs(edge_attrs)}];')
    lines.append('}')
    return '\n'.join(lines) + '\n'


def render_saved_model(input_path: Path, out_prefix: Path, *, svg: bool = False) -> dict:
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('saved Bering model rendering is permitted only in GitHub Actions')
    input_path, out_prefix = Path(input_path).resolve(), Path(out_prefix).resolve()
    raw = input_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    model = json.loads(raw)
    services, edges, endpoints = _validated(model)
    dot = dot_from_model(model, sha256)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    dot_path = out_prefix.with_name(out_prefix.name + '.dot')
    sidecar_path = out_prefix.with_name(out_prefix.name + '.figure.json')
    dot_path.write_text(dot, encoding='utf-8')
    result = {
        'source': 'saved Bering observed.json', 'original_model_path': str(input_path),
        'original_model_sha256': sha256,
        'counts': {'services': len(services), 'edges': len(edges), 'endpoints': len(endpoints)},
        'service_ids': [item['id'] for item in services],
        'edges': [{'input_index': index, 'id': item.get('id'), 'from': item['from'], 'to': item['to']}
                  for index, item in enumerate(edges)],
        'endpoint_ids': [item.get('id') for item in endpoints],
        'dot_path': str(dot_path),
        'graph_rule': 'every observed service and edge retained; endpoints annotate observed entry services; no identity merge or placement inference',
    }
    if svg:
        svg_path = out_prefix.with_name(out_prefix.name + '.svg')
        subprocess.run(['dot', '-Tsvg', str(dot_path), '-o', str(svg_path)], check=True)
        result['svg_path'] = str(svg_path)
    sidecar_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out-prefix', type=Path, required=True)
    parser.add_argument('--svg', action='store_true')
    args = parser.parse_args(argv)
    print(json.dumps(render_saved_model(args.input, args.out_prefix, svg=args.svg), ensure_ascii=False))


if __name__ == '__main__':
    main()
