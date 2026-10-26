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
from .async_links import message_chains


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
    train_augmented = {class_key([r['signature'], r['downstream']]) for r in training
                       if r['phase'] == 'class_train' and r['class_id'] and r['proxy'] is True}
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


def typed_order_chains(spans):
    """Conservative declared-schema matcher, separate from arbitrary UUID presence.

The existing control specifies checkout/accounting roles and order_id semantics.
Only a field explicitly named order_id/orderId/order.id is accepted, including
JSON HTTP bodies. SQL placeholders, topic/time matches, broker fetches and UUIDs
elsewhere are insufficient. This deliberately leaves other possible matchers open.
"""
    found = defaultdict(lambda: defaultdict(list))
    uuid = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    def fields(obj, prefix=''):
        result = []
        if isinstance(obj, dict):
            for key, val in obj.items():
                path = prefix+'.'+key
                normal = key.lower().replace('_', '').replace('.', '')
                if normal == 'orderid' and isinstance(val, str) and uuid.fullmatch(val):
                    result.append((val.lower(), path))
                # Only the declared current-order object is a semantic alias.
                # History, previous_order_id, arbitrary nested payloads and
                # UUID-shaped strings do not establish the current order.
                if key == 'order' and isinstance(val, dict):
                    result.extend(fields(val, path))
        return result
    for span in spans:
        attrs = span['attributes']
        identities = fields(attrs)
        for key, val in attrs.items():
            if 'body' in key and isinstance(val, str):
                try:
                    identities.extend(fields(json.loads(val), key))
                except (ValueError, TypeError):
                    pass
        operation = str(attrs.get('messaging.operation.type', attrs.get('messaging.operation.name', attrs.get('messaging.operation', '')))).lower()
        service = span['service'].lower()
        stage = None
        if attrs.get('messaging.system') == 'kafka':
            if 'checkout' in service and operation in ('send', 'publish', 'produce'):
                stage = 'checkout_produce'
            elif 'accounting' in service and operation in ('receive', 'process', 'fetch'):
                stage = 'accounting_consume'
        elif 'accounting' in service and attrs.get('db.system.name', attrs.get('db.system')) in ('postgresql', 'postgres'):
            db_operation = str(attrs.get('db.operation.name', attrs.get('db.operation', ''))).upper()
            if db_operation in ('INSERT', 'COMMIT'):
                stage = 'accounting_write'
        elif '/api/checkout' in json.dumps(attrs):
            stage = 'checkout_http'
        if stage:
            for identity, field in identities:
                found[identity][stage].append({'field': field, 'service': span['service'],
                                              'trace_id': span['trace_id'], 'span_id': span['span_id'],
                                              'source': span['source']})
    return {key: dict(stages) for key, stages in found.items()}


def validate_cross_node(links, native_spans):
    """Use only independently recorded native IDs; unmatched evidence is unknown."""
    lookup = {(s['trace_id'], s['span_id']): s for s in native_spans}
    output = []
    for link in links:
        trace = link['trace_id']
        current = lookup.get((trace, link['child_id']))
        reference_parent = lookup.get((trace, link['parent_id']))
        correct, visited = None, set()
        if current and reference_parent:
            while current and current['span_id'] not in visited:
                visited.add(current['span_id'])
                parent = current['parent_id']
                if parent == link['parent_id']:
                    correct = True
                    break
                if not parent:
                    correct = False
                    break
                current = lookup.get((trace, parent))
        output.append({**link, 'reference': 'independent native observed ancestry with exact trace/span IDs',
                       'reference_correct': correct})
    known = sum(row['reference_correct'] is not None for row in output)
    wrong = sum(row['reference_correct'] is False for row in output)
    return {'links': output, 'reference_covered': known, 'unknown': len(output)-known,
            'error_rate_on_covered': wrong/known if known else None}


def database_reference_match(node, reference):
    """Evaluation-only endpoint match; a host shared by DB ports is ambiguous."""
    address = str(node.get('address') or '')
    if not address:
        return None
    published = {}
    if reference.get('transport_host'):
        published[str(reference['transport_host'])] = reference.get('transport_port')
    if reference.get('cross_guest_endpoint'):
        host, port = reference['cross_guest_endpoint'].rsplit(':', 1)
        published[host] = port
    port = node.get('port')
    if address in published:
        expected = published[address]
        return str(port) == str(expected) if port is not None and expected is not None else None
    names = {str(reference[k]) for k in ('ip', 'name', 'container', 'logical_identity') if reference.get(k)}
    names.update(str(v) for v in reference.get('observed_aliases', []) if str(v) not in published)
    if address not in names:
        return False
    expected = reference.get('port', reference.get('container_port'))
    return str(port) == str(expected) if port is not None and expected is not None else True


def database_activity(spans):
    """Retain DB activity that lacks endpoint attributes; never invent sharing."""
    tallies = {}
    for s in spans:
        a = s['attributes']
        system = a.get('db.system.name', a.get('db.system'))
        basis = 'explicit_db_system_attribute'
        if not system:
            named = re.search(r'(?:^|_)(mongo|redis)(?:_|$)', (s.get('name') or '').lower())
            if not named:
                continue
            system = {'mongo': 'mongodb', 'redis': 'redis'}[named.group(1)]
            basis = 'interpretation_of_observed_operation_name; not_endpoint_identity'
        address = a.get('server.address', a.get('net.peer.name', a.get('net.peer.ip')))
        port = a.get('server.port', a.get('net.peer.port'))
        key = (s['source'], s['service'], s.get('instance'), s.get('node'), s.get('name'), system, basis, address, port)
        if key not in tallies:
            tallies[key] = dict(zip(('source', 'caller', 'instance', 'node', 'span_name', 'interpreted_system',
                                    'interpretation_basis', 'observed_address', 'observed_port'), key))
            tallies[key].update(count=0, example={'trace_id': s['trace_id'], 'span_id': s['span_id'],
                                                'raw_file': s.get('raw_file')})
        tallies[key]['count'] += 1
    return list(tallies.values())


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
              'protocol_version': status.get('protocol_version', 'pre-warmup-pilot'),
              'run_id': status['run_id'], 'sources': {}, 'costs': {'campaign_elapsed_seconds': status['elapsed_seconds']},
              'forecast_saved_before_target': True, 'evaluation_commit': os.environ.get('GITHUB_SHA')}
    for source in ('ebpf', 'native', 'combined'):
        folder = Path('models') / source
        if hashlib.sha256((root/folder/'forecast.json').read_bytes()).hexdigest() != saved['sha256'][source]:
            raise RuntimeError('Saved forecast hash changed')
        for file, field in [('model.json', 'model_sha256'), ('evaluation-map.json', 'evaluation_map_sha256')]:
            if hashlib.sha256((root/folder/file).read_bytes()).hexdigest() != saved[field][source]:
                raise RuntimeError(f'Saved {file} hash changed')
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
                                     'coverage': bounds[0] <= ylo + 1e-12 and bounds[1] >= yhi - 1e-12,
                                     'unsupported': predicted is None,
                                     'target_unclassified': sum(by_key[opaque_attempt(r)]['class_id'] is None for r in targets)}
            for row in targets:
                proxy = by_key[opaque_attempt(row)]['proxy']
                business = row.get('success')
                mismatches.append({'attempt_key': opaque_attempt(row), 'operation': operation,
                                   'proxy': proxy, 'external': business,
                                   'mismatch': proxy != business if proxy is not None and business is not None else None})
        observed_graph = graph(data)
        cross_validation = validate_cross_node(observed_graph['cross_node'], [s for s in spans if s['source'] == 'native']) if source == 'ebpf' else None
        db = metadata['database']
        # Deployment reference is evaluator-only. Never relabel the observed
        # graph to hide a collector's protocol misclassification.
        reference_db_system = {'deathstarbench': 'mongodb', 'petclinic': 'mysql', 'otel_demo': 'postgresql'}[status['system']]
        database_nodes = []
        for node in observed_graph['nodes']:
            if node['kind'] == 'database':
                endpoint_match = database_reference_match(node, db)
                observed_system = {'postgres': 'postgresql', 'mongo': 'mongodb'}.get(node['system'], node['system'])
                database_nodes.append({**node, 'matches_selected_database': endpoint_match,
                                       'reference_system_for_selected_endpoint': reference_db_system if endpoint_match is True else None,
                                       'selected_endpoint_protocol_agrees': observed_system == reference_db_system if endpoint_match is True else None,
                                       'match_kind': 'evaluation-only declared logical name or address/port endpoint; not physical-instance proof'})
        db_controls = {operation: {phase: external_rate([r for r in external if r['operation'] == operation and r['phase'] == phase])
                                   for phase in ('db_up', 'db_down')} for operation in metadata['operations']}
        identities = async_identities(data)
        typed = typed_order_chains(data)
        message_evidence = message_chains(data) if status['system'] == 'otel_demo' else {}
        asynchronous = []
        for row in external:
            if not row['phase'].startswith('async_'):
                continue
            identity = str(row.get('order_id', '')).lower()
            evidence = identities.get(identity, {})
            typed_evidence = typed.get(identity, {})
            chains = {step['request_id']: message_evidence[step['request_id']] for step in row['http_steps']
                      if step.get('request_id') in message_evidence}
            chain_sources = sorted({observed_source for chain in chains.values()
                                    for observed_source, proof in chain['sources'].items() if proof['status'] == 'linked'})
            typed_complete = all(stage in typed_evidence for stage in ('checkout_http', 'checkout_produce', 'accounting_consume', 'accounting_write'))
            asynchronous.append({'attempt_key': opaque_attempt(row), 'phase': row['phase'],
                                 'http_success': row.get('success'), 'durable': row.get('async_verification'),
                                 'uuid_stage_presence': evidence,
                                 'typed_order_evidence': typed_evidence,
                                 'message_chain_evidence': chains, 'message_chain_supporting_sources': chain_sources,
                                 'complete_identity_chain': True if typed_complete or chain_sources else None,
                                 'identity_note': 'Typed current-order identity or a unique exact producer SpanLink/processing-root chain establishes association only. SQL durability/deadline is independently evaluated; missing or ambiguous chains remain unknown.'})
        result['sources'][source] = {'operations': operations,
            'classes': class_metrics(external, projected, training),
            'database_nodes': database_nodes, 'db_controls': db_controls,
            'database_activity': database_activity(data),
            'shared_database_dependencies': observed_graph['shared_database_dependencies'],
            'database_edges': [e for e in observed_graph['edges'] if e['evidence'] == 'database_client_span'],
            'database_forecast_effect': None,
            'database_forecast_effect_note': 'DB graph nodes are not variables in the saturated four-state predictor; no structural forecast gain claimed.',
            'cross_node': observed_graph['cross_node'],
            'cross_node_reference_validation': cross_validation,
            'cross_node_error_rate': None,
            'native_reference_disagreement_rate': cross_validation['error_rate_on_covered'] if cross_validation else None,
            'async': asynchronous,
            'proxy_mismatches': sum(r['mismatch'] is True for r in mismatches),
            'proxy_comparable': sum(r['mismatch'] is not None for r in mismatches),
            'normalized_spans': len(data)}
        write_json(root/folder/'target-assignments.json', projected)
        write_json(root/folder/'proxy-semantic-comparison.json', mismatches)
        write_json(root/folder/'observed-uuid-census.json', identities)
        write_json(root/folder/'observed-final-graph.json', observed_graph)
        calibration_spans = read('normalized-calibration.json')
        calibration_source = calibration_spans if source == 'combined' else [s for s in calibration_spans if s['source'] == source]
        write_json(root/folder/'validated-calibration-graph.json', graph(calibration_source))
        write_json(root/folder/'message-chain-evidence.json', message_evidence)
    write_json(root/'metrics.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    evaluate(p.parse_args().out)
