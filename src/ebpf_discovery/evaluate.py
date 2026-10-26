"""Independent business outcomes and evaluation-only labels enter here, after fit."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re

from .model import Projection, assign, class_key
from .observations import graph, opaque_attempt
from .runtime import write_json


def evaluation_map(external, assignments):
    """Training-only display mapping, never consumed by model fitting or simulation."""
    labels = {opaque_attempt(r): r['operation'] for r in external if r['phase'] == 'class_train'}
    counts = defaultdict(Counter)
    for row in assignments:
        if row['attempt_key'] in labels and row['class_id']:
            counts[labels[row['attempt_key']]][row['class_id']] += 1
    return {operation: {'class_id': votes.most_common()[0][0] if len(votes) == 1 else None,
                        'training_votes': dict(votes)} for operation, votes in counts.items()}


def external_rate(rows, field='success'):
    counts = Counter(r.get(field) for r in rows)
    n = len(rows)
    return {'n': n, 'successes': counts[True], 'failures': counts[False], 'unknown': counts[None],
            'bounds': [counts[True]/n, (counts[True]+counts[None])/n] if n else [0., 1.],
            'point': counts[True]/n if n and not counts[None] else None}


def ari(truth, predicted):
    if len(truth) < 2:
        return None
    table, rows, cols = Counter(zip(truth, predicted)), Counter(truth), Counter(predicted)
    pairs = lambda n: n*(n-1)/2
    nij = sum(pairs(n) for n in table.values())
    a, b = sum(pairs(n) for n in rows.values()), sum(pairs(n) for n in cols.values())
    expected = a*b/pairs(len(truth))
    denominator = (a+b)/2-expected
    return (nij-expected)/denominator if denominator else 1.0


def class_metrics(external, projected, training):
    truth = {opaque_attempt(r): r['operation'] for r in external if r['phase'] == 'class_test'}
    train_augmented = {class_key([r['signature'], r['downstream']]) for r in training if r['class_id'] and r['proxy'] is True}
    output = {}
    for variant in ('route', 'route_and_downstream'):
        labels, predictions = [], []
        for row in projected:
            if row['attempt_key'] not in truth or not row['class_id']:
                continue
            predicted = row['class_id'] if variant == 'route' else class_key([row['signature'], row['downstream']])
            if variant != 'route' and predicted not in train_augmented:
                continue
            labels.append(truth[row['attempt_key']])
            predictions.append(predicted)
        output[variant] = {'ari_on_covered': ari(labels, predictions), 'covered': len(labels), 'total': len(truth),
                           'unknown_fraction': 1-len(labels)/len(truth) if truth else None}
    return output


def async_identities(spans):
    """Generic observed UUID census; oracle order IDs are only looked up afterward."""
    found = defaultdict(lambda: defaultdict(list))
    pattern = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
    for s in spans:
        a = s['attributes']
        text = json.dumps(a)
        ids = set(x.lower() for x in pattern.findall(text))
        if not ids:
            continue
        stage = None
        system = a.get('messaging.system')
        operation = str(a.get('messaging.operation.type', a.get('messaging.operation.name', a.get('messaging.operation', '')))).lower()
        if system == 'kafka':
            stage = 'producer' if operation in ('send', 'publish', 'produce') else ('consumer' if operation in ('receive', 'process', 'fetch') else None)
        elif a.get('db.system.name', a.get('db.system')) in ('postgresql', 'postgres'):
            stage = 'sql'
        elif '/api/checkout' in text:
            stage = 'http'
        if stage:
            for identity in ids:
                found[identity][stage].append({'trace_id': s['trace_id'], 'span_id': s['span_id'],
                                              'service': s['service'], 'source': s['source']})
    return {key: dict(stages) for key, stages in found.items()}


def evaluate(root):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Research result processing runs in GitHub Actions')
    read = lambda p: json.loads((root/p).read_text(encoding='utf-8'))
    external, census, spans = read('external.json'), read('census.json'), read('normalized-final.json')
    metadata, status, saved = read('deployment.json'), read('status.json'), read('forecast-saved.json')
    target_start = min(b['load_started_ns'] for b in read('blocks.json') if b['phase'] == 'target')
    if saved['saved_ns'] >= target_start:
        raise RuntimeError('Forecast was not saved before target acquisition')
    result = {'system': status['system'], 'mode': status['mode'], 'seed': status['seed'],
              'run_id': status['run_id'], 'sources': {}, 'costs': {'campaign_elapsed_seconds': status['elapsed_seconds']},
              'forecast_saved_before_target': True}
    for source in ('ebpf', 'native', 'combined'):
        folder = Path('models') / source
        if hashlib.sha256((root/folder/'forecast.json').read_bytes()).hexdigest() != saved['sha256'][source]:
            raise RuntimeError('Saved forecast hash changed')
        model, forecast = read(folder/'model.json'), read(folder/'forecast.json')
        training = read(folder/'calibration-assignments.json')
        mapping = read(folder/'evaluation-map.json')
        data = spans if source == 'combined' else [s for s in spans if s['source'] == source]
        projection = Projection(data)
        projected = [assign(projection.attempt(row), model['classes']) for row in census]
        by_key = {r['attempt_key']: r for r in projected}
        operations = {}
        mismatches = []
        for operation in metadata['operations']:
            targets = [r for r in external if r['phase'] == 'target' and r['operation'] == operation]
            observed = external_rate(targets)
            key = mapping.get(operation, {}).get('class_id')
            predicted = forecast['classes'].get(key)
            bounds = predicted['uncertainty_bounds'] if predicted else [0., 1.]
            ylo, yhi = observed['bounds']
            worst = max(abs(bounds[0]-yhi), abs(bounds[1]-ylo))
            point = predicted.get('point') if predicted else None
            actual = observed['point']
            operations[operation] = {'external': observed, 'class_id': key, 'forecast': predicted,
                                     'absolute_error': abs(point-actual) if point is not None and actual is not None else None,
                                     'signed_error': point-actual if point is not None and actual is not None else None,
                                     'worst_interval_error': worst, 'interval_width': bounds[1]-bounds[0],
                                     'coverage': bounds[0] <= ylo and bounds[1] >= yhi,
                                     'unsupported': predicted is None,
                                     'target_unclassified': sum(by_key[opaque_attempt(r)]['class_id'] is None for r in targets)}
            for row in targets:
                proxy = by_key[opaque_attempt(row)]['proxy']
                business = row.get('success')
                mismatches.append({'attempt_key': opaque_attempt(row), 'operation': operation,
                                   'proxy': proxy, 'external': business,
                                   'mismatch': proxy != business if proxy is not None and business is not None else None})
        observed_graph = graph(data)
        db = metadata['database']
        known_addresses = {str(db.get(k)) for k in ('ip', 'name', 'container', 'logical_identity') if db.get(k)}
        known_addresses.update(str(v) for v in db.get('observed_aliases', []))
        database_nodes = []
        for node in observed_graph['nodes']:
            if node['kind'] == 'database':
                database_nodes.append({**node, 'matches_selected_database': str(node['address']) in known_addresses})
        db_controls = {operation: {phase: external_rate([r for r in external if r['operation'] == operation and r['phase'] == phase])
                                   for phase in ('db_up', 'db_down')} for operation in metadata['operations']}
        identities = async_identities(data)
        asynchronous = []
        for row in external:
            if not row['phase'].startswith('async_'):
                continue
            identity = str(row.get('order_id', '')).lower()
            evidence = identities.get(identity, {})
            asynchronous.append({'attempt_key': opaque_attempt(row), 'phase': row['phase'],
                                 'http_success': row.get('success'), 'durable': row.get('async_verification'),
                                 'uuid_stage_presence': evidence,
                                 'complete_identity_chain': None,
                                 'identity_note': 'Generic UUID presence is a candidate only; confirmed chain requires typed order identity and accounting consume/write roles.'})
        result['sources'][source] = {'operations': operations,
            'classes': class_metrics(external, projected, training),
            'database_nodes': database_nodes, 'db_controls': db_controls,
            'database_forecast_effect': None,
            'database_forecast_effect_note': 'DB graph nodes are not variables in the saturated four-state predictor; no structural forecast gain claimed.',
            'cross_node': observed_graph['cross_node'], 'cross_node_error_rate': None,
            'async': asynchronous,
            'proxy_mismatches': sum(r['mismatch'] is True for r in mismatches),
            'proxy_comparable': sum(r['mismatch'] is not None for r in mismatches),
            'normalized_spans': len(data)}
        write_json(root/folder/'target-assignments.json', projected)
        write_json(root/folder/'proxy-semantic-comparison.json', mismatches)
        write_json(root/folder/'observed-uuid-census.json', identities)
    write_json(root/'metrics.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    evaluate(p.parse_args().out)
