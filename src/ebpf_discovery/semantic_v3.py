"""Declared source-only operation completion; independent HTTP/body comparator."""
from __future__ import annotations
import base64
import hashlib
import importlib
import json
import math
import time
from urllib.parse import urlsplit
import numpy as np

from .model import STATES, WEIGHTS, conditional, assign, class_key
from .observations import opaque_attempt, route, step_id

SOURCES = ('ebpf', 'native', 'combined', 'entry_http')


def declared_census(records):
    """Only supplied intent and timing; never a success/status/body/oracle field."""
    output = []
    for record in records:
        intent = record.get('request_intent') or {}
        planned = intent.get('steps', [])
        ids = [s['request_id'] for s in planned] if planned else [s['request_id'] for s in record['http_steps']]
        observation = record.get('observation') or {}
        output.append({'attempt_key': opaque_attempt(record), 'operation_id': record['operation'],
                       'step_ids': ids, 'actual_step_ids': [s['request_id'] for s in record['http_steps']],
                       'phase': record['phase'], 'state': record['state'],
                       'started_ns': record['started_ns'], 'ended_ns': record['ended_ns'],
                       'deadline_ns': observation.get('cutoff_ns', record['started_ns']+int(record.get('deadline_seconds', 2.)*1e9)),
                       'observation_policy': observation.get('policy'),
                       'observation_censored': observation.get('censored'),
                       'observation_termination': observation.get('termination')})
    return output


def transport_observations(records):
    """Separate cheap baseline boundary: HTTP transport facts, no SQL/oracle labels."""
    result = {}
    for record in records:
        steps = []
        for step in record['http_steps']:
            encoded = step.get('response_body_b64', step.get('response_body_base64'))
            decoded = None
            try:
                decoded = base64.b64decode(encoded, validate=True) if encoded is not None else None
                body = decoded.decode('utf-8', errors='strict') if decoded is not None else None
            except (ValueError, UnicodeDecodeError):
                body = None
            steps.append({'request_id': step['request_id'], 'status': step.get('status'),
                          'body': body, 'complete_transport_body': encoded is not None and step.get('status') is not None
                          and not step.get('transport_error') and not step.get('error'),
                          'body_bytes': len(decoded) if decoded is not None else None})
        result[opaque_attempt(record)] = steps
    return result


def raw_route(span):
    attrs = span['attributes']
    method = attrs.get('http.request.method', attrs.get('http.method'))
    path = next((attrs[k] for k in ('url.path', 'http.target', 'url.full', 'http.url', 'http.route') if attrs.get(k)), None)
    return method, urlsplit(str(path)).path if path else None


def status_code(span):
    if not span:
        return None
    a = span['attributes']
    try:
        code = int(a.get('http.response.status_code', a.get('http.status_code')))
        return code if 100 <= code <= 599 else None
    except (TypeError, ValueError):
        return None


def witness(span):
    if not span:
        return None
    return {k: span.get(k) for k in ('source', 'node', 'trace_id', 'span_id', 'parent_id', 'service', 'raw_file')}


def conjunction(values):
    return False if False in values else (True if values and all(v is True for v in values) else None)


def merge_verdicts(values):
    known = {v for v in values if v is not None}
    return next(iter(known)) if len(known) == 1 else None


def captured_body(span, limit=16384):
    if not span:
        return None, {'reason': 'entry_unbound'}
    attrs = span['attributes']
    content = attrs.get('http.response.body.content')
    if not isinstance(content, str):
        return None, {'reason': 'body_not_exported'}
    size = len(content.encode('utf-8'))
    proof = {'bytes': size, 'sha256': hashlib.sha256(content.encode()).hexdigest(),
             'field': 'http.response.body.content', 'limit_bytes': limit}
    if size >= limit or any(v is True for k, v in attrs.items() if 'truncat' in k.lower()):
        return None, {**proof, 'reason': 'truncated_or_at_capture_limit'}
    lengths = []
    for key, value in attrs.items():
        if 'response' in key.lower() and key.lower().replace('_', '-').endswith('content-length'):
            try:
                lengths.append(int(value[0] if isinstance(value, list) and len(value) == 1 else value))
            except (ValueError, TypeError):
                return None, {**proof, 'reason': 'ambiguous_content_length'}
    if lengths and any(length != size for length in lengths):
        return None, {**proof, 'reason': 'content_length_mismatch', 'declared_lengths': lengths}
    return content, {**proof, 'reason': 'length_verified' if lengths else 'below_limit_single_document_assumption'}


class Binder:
    def __init__(self, store, system, context=None):
        self.store = store
        self.system = system
        self.contracts = importlib.import_module(f'systems.{system}.contracts_v3')
        self.context = context or {}

    def entry(self, source, identity, expected=None):
        if not identity:
            return None, 'step_not_observed'
        candidates = self.store.candidates(source, identity)
        selected = {}
        allowed = {(s['method'], s['path']) for c in self.contracts.CONTRACTS.values() for s in c['steps']}
        for anchor in candidates:
            if anchor['service'] not in self.contracts.ENTRY_SERVICES[source]:
                continue
            span, path, candidate = anchor, [], None
            while span and span['span_id'] not in path:
                path.append(span['span_id'])
                if span.get('attribute_conflicts'):
                    return None, 'conflicting_raw_attributes'
                if len(self.store.identity(source, span['trace_id'], span['span_id'])) != 1:
                    return None, 'conflicting_entry_identity'
                method_path = raw_route(span)
                server = str(span['kind']) in ('2', 'SPAN_KIND_SERVER', 'server')
                untyped = span['kind'] is None and span['attributes'].get('component') in getattr(
                    self.contracts, 'UNTYPED_ENTRY_COMPONENTS', {}).get(source, [])
                if str(span['kind']) in ('3', 'SPAN_KIND_CLIENT', 'client'):
                    candidate = None
                    break
                if ((server or untyped) and method_path in allowed
                        and (not expected or method_path == (expected['method'], expected['path']))):
                    candidate = {
                        **span, '_header_binding': {'header_span_id': anchor['span_id'],
                                                   'source_local_parent_path': path[:],
                                                   'same_service_instance_node': True, 'raw_kind': span['kind'],
                                                   'rule': 'declared_nginx_untyped_outer_http' if untyped else 'explicit_server'}}
                    if server:
                        break
                parents = self.store.identity(source, span['trace_id'], span['parent_id']) if span['parent_id'] else []
                if len(parents) > 1:
                    return None, 'conflicting_entry_identity'
                span = parents[0] if parents and all(parents[0].get(k) == anchor.get(k)
                            for k in ('service', 'instance', 'node')) else None
            if candidate:
                selected[(candidate['trace_id'], candidate['span_id'])] = candidate
        if len(selected) != 1:
            return None, 'entry_missing' if not selected else 'multiple_entries'
        return next(iter(selected.values())), 'unique_declared_entry'

    def entry_window(self, span, source, identity, row):
        """Admit an entry inside the sealed journal, with one narrow DSB proof.

        A coarse native nginx outer start may precede the client journal. Only
        an exact header-bearing descendant proves request presence. The outer
        span remains the source of HTTP status, body, raw start and end.
        """
        if row.get('observation_policy') != 'censored-v3':
            return (True, 'legacy_window', None)
        started, cutoff = row['started_ns'], row['deadline_ns']
        if not (type(started) is int and type(cutoff) is int and started < cutoff and
                type(span['start_ns']) is int and type(span['end_ns']) is int and
                0 < span['start_ns'] <= span['end_ns'] <= cutoff):
            return (False, 'entry_outside_sealed_observation_window', None)
        if started <= span['start_ns']:
            if row.get('observation_censored'):
                return (False, 'observation_censored', None)
            return (True, 'strict_sealed_window', None)
        native_coarse_nginx = (
            self.system == 'deathstarbench' and source == 'native' and
            span['service'] in self.contracts.ENTRY_SERVICES['native'] and
            span['kind'] is None and span['attributes'].get('component') in
                getattr(self.contracts, 'UNTYPED_ENTRY_COMPONENTS', {}).get('native', [])
        )
        if not native_coarse_nginx or not identity:
            return (False, 'entry_outside_sealed_observation_window', None)
        proofs = []
        for anchor in self.store.candidates(source, identity):
            if anchor['span_id'] == span['span_id'] or step_id(anchor) != identity:
                continue
            if str(anchor['kind']) in ('3', 'SPAN_KIND_CLIENT', 'client'):
                continue
            if any(anchor.get(key) != span.get(key) for key in
                   ('source', 'trace_id', 'service', 'instance', 'node')):
                continue
            if not (type(anchor['start_ns']) is int and type(anchor['end_ns']) is int and
                    0 < started <= anchor['start_ns'] < anchor['end_ns'] <= span['end_ns'] <= cutoff):
                continue
            current, path, visited = anchor, [], set()
            while current and current['span_id'] not in visited:
                visited.add(current['span_id'])
                path.append(current['span_id'])
                if current.get('attribute_conflicts') or len(self.store.identity(
                        source, current['trace_id'], current['span_id'])) != 1:
                    break
                if current['span_id'] != span['span_id'] and str(current['kind']) in (
                        '3', 'SPAN_KIND_CLIENT', 'client'):
                    break
                if any(current.get(key) != span.get(key) for key in
                       ('source', 'trace_id', 'service', 'instance', 'node')):
                    break
                if current['span_id'] == span['span_id']:
                    proofs.append({'rule': 'native_nginx_coarse_outer_start_exact_header_child',
                        'outer_raw_start_ns': span['start_ns'], 'outer_end_ns': span['end_ns'],
                        'header_child_start_ns': anchor['start_ns'],
                        'header_child_end_ns': anchor['end_ns'],
                        'header_child_span_id': anchor['span_id'],
                        'source_local_parent_path': path[:]})
                    break
                parent = current.get('parent_id')
                parents = self.store.identity(source, current['trace_id'], parent) if parent else []
                current = parents[0] if len(parents) == 1 else None
        if not proofs:
            return (False, 'entry_outside_sealed_observation_window', None)
        if row.get('observation_censored'):
            return (False, 'observation_censored', None)
        proofs.sort(key=lambda proof: (proof['header_child_start_ns'],
                                       proof['header_child_span_id'], proof['source_local_parent_path']))
        return (True, 'native_header_child_attribution',
                {**proofs[0], 'valid_header_children': len(proofs)})

    def source_attempt(self, row, source):
        operation = row['operation_id']
        contract = self.contracts.CONTRACTS[operation]
        steps, values, final = [], [], None
        for ordinal, expected in enumerate(contract['steps']):
            identity = row['step_ids'][ordinal] if ordinal < len(row['step_ids']) else None
            span, reason = self.entry(source, identity, expected)
            window_reason = None
            if span:
                if row.get('observation_policy') == 'censored-v3':
                    eligible, window_reason, proof = self.entry_window(span, source, identity, row)
                    if not eligible:
                        span, reason = None, window_reason
                    elif proof:
                        span['_header_binding'] = {**span['_header_binding'], 'window_attribution': proof}
                elif span['start_ns'] < row['started_ns']-1_000_000_000 or span['start_ns'] > row['ended_ns']+1_000_000_000:
                    span, reason = None, 'entry_outside_journal_window'
            code = status_code(span)
            valid = self.contracts.status_ok(operation, ordinal, code) if code is not None else None
            values.append(valid)
            steps.append({'ordinal': ordinal, 'request_id': identity, 'binding': reason, 'status': code,
                          'protocol': valid, 'witness': witness(span),
                          'window_binding': window_reason,
                          'header_binding': span.get('_header_binding') if span else None})
            if ordinal == len(contract['steps'])-1:
                final = span
        body, body_evidence = captured_body(final)
        semantic = self.contracts.payload_verdict(operation, body,
            {**self.context, 'attempt_key': row['attempt_key']}) if body is not None else {'value': None, 'reason': body_evidence['reason']}
        censored_policy = row.get('observation_policy') == 'censored-v3'
        timely = None if censored_policy else row['ended_ns'] <= row['deadline_ns']
        verdict = conjunction(values+[semantic['value']]+([] if censored_policy else [timely]))
        if censored_policy and row['observation_censored']:
            verdict = None
        return {**row, 'source': source, 'class_id': operation, 'compatible_classes': [operation],
                'proxy': verdict, 'protocol_only': conjunction(values+([] if censored_policy else [timely])), 'timely': timely,
                'steps': steps, 'body_evidence': body_evidence, 'payload_verdict': semantic,
                'outcome_kind': 'declared_business_completion', 'oracle_fields_consumed': False}

    def cheap_attempt(self, row, transport):
        operation = row['operation_id']
        expected = self.contracts.CONTRACTS[operation]['steps']
        actual = transport.get(row['attempt_key'], [])
        statuses = [self.contracts.status_ok(operation, i, actual[i]['status'])
                    if i < len(actual) and actual[i]['status'] is not None else None for i in range(len(expected))]
        body = actual[-1]['body'] if len(actual) == len(expected) else None
        complete = len(actual) == len(expected) and actual[-1].get('complete_transport_body', False)
        semantic = self.contracts.payload_verdict(operation, body,
            {**self.context, 'attempt_key': row['attempt_key'], 'complete_transport_body': True}) if body is not None and complete else {'value': None, 'reason': 'no_complete_final_response'}
        if self.system == 'petclinic' and actual and (actual[-1].get('body_bytes') or 0) > 1024*1024:
            semantic = {'value': False, 'reason': 'response_exceeds_declared_limit'}
        censored_policy = row.get('observation_policy') == 'censored-v3'
        timely = None if censored_policy else row['ended_ns'] <= row['deadline_ns']
        verdict = conjunction(statuses+[semantic['value']]+([] if censored_policy else [timely]))
        if censored_policy and row['observation_censored']:
            verdict = None
        return {**row, 'source': 'entry_http', 'class_id': operation, 'compatible_classes': [operation],
                'proxy': verdict,
                'protocol_only': conjunction(statuses+([] if censored_policy else [timely])), 'payload_verdict': semantic,
                'outcome_kind': 'declared_business_completion', 'oracle_fields_consumed': False}

    def project(self, rows, transport):
        output = {source: [] for source in SOURCES}
        for row in rows:
            individual = [self.source_attempt(row, source) for source in ('ebpf', 'native')]
            for item in individual:
                output[item['source']].append(item)
            verdicts = [item['proxy'] for item in individual]
            merged_steps = [merge_verdicts([item['steps'][ordinal]['protocol'] for item in individual])
                            for ordinal in range(len(individual[0]['steps']))]
            payload_values = [item['payload_verdict']['value'] for item in individual]
            primitive_values = [[item['steps'][ordinal]['protocol'] for item in individual]
                                for ordinal in range(len(merged_steps))]+[payload_values]
            conflict = any(True in values and False in values for values in primitive_values)
            censored_policy = row.get('observation_policy') == 'censored-v3'
            timing = [] if censored_policy else [individual[0]['timely']]
            combined = conjunction(merged_steps+[merge_verdicts(payload_values)]+timing)
            if censored_policy and row['observation_censored']:
                combined = None
            output['combined'].append({**row, 'source': 'combined', 'class_id': row['operation_id'],
                'compatible_classes': [row['operation_id']], 'proxy': None if conflict else combined,
                'protocol_only': conjunction(merged_steps+timing),
                'source_verdicts': dict(zip(('ebpf', 'native'), verdicts)),
                'primitive_conflict': conflict, 'merged_step_status_verdicts': merged_steps,
                'conflict': conflict, 'oracle_fields_consumed': False})
            output['entry_http'].append(self.cheap_attempt(row, transport))
        return output

    def automatic(self, actual_census, source, classes=None, *, downstream=False):
        """Label-free route grouping only; this arm does not borrow operation IDs."""
        projected = []
        for row in actual_census:
            signatures, evidence = [], []
            for identity in row['step_ids']:
                sources = ('ebpf', 'native') if source == 'combined' else (source,)
                choices = [(s, self.entry(s, identity)[0]) for s in sources]
                if row.get('observation_policy') == 'censored-v3':
                    choices = [(s, span) for s, span in choices if span and
                               self.entry_window(span, s, identity, row)[0]]
                signatures_found = set()
                for _, span in choices:
                    if not span or not route(span):
                        continue
                    signature = route(span)
                    if downstream:
                        descendants = self.store.descendants(span)
                        if row.get('observation_policy') == 'censored-v3':
                            descendants = [item for item in descendants if
                                row['started_ns'] <= item['start_ns'] <= item['end_ns'] <= row['deadline_ns']]
                        features = sorted({(s['service'], route(s) or s['name'],
                            s['attributes'].get('db.system.name', s['attributes'].get('db.system')))
                            for s in descendants}, key=str)
                        signature = json.dumps([signature, features], separators=(',', ':'))
                    signatures_found.add(signature)
                signatures.append(next(iter(signatures_found)) if len(signatures_found) == 1 else None)
                codes = [status_code(span) for _, span in choices if span]
                evidence.append(merge_verdicts([200 <= c < 300 for c in codes if c is not None]))
            proxy = None if row.get('observation_censored') else conjunction(evidence)
            projected.append({**row, 'signature': signatures, 'proxy': proxy})
        if classes is None:
            classes = {class_key(r['signature']): {'signature': r['signature']} for r in projected
                       if r['phase'] == 'class_train' and r['proxy'] is True and r['signature'] and all(r['signature'])}
        return classes, [assign(row, classes) for row in projected]


def fit_declared(rows, operations, seed, graph):
    started = time.perf_counter()
    calibration = [r for r in rows if r['phase'] == 'calibration']
    conditions = {operation: {s: conditional(calibration, operation, s) for s in STATES} for operation in operations}
    model = {'schema_version': 3, 'classes': {o: {'declared_operation': o} for o in operations},
             'conditional': conditions, 'graph': graph, 'target_weights': WEIGHTS,
             'manual_inputs': ['operation contracts and identity', 'opaque request grouping/timing', 'replica states', 'target weights'],
             'business_oracle_input': False, 'created_ns': time.time_ns()}
    model['observation_policy'] = sorted({str(row.get('observation_policy')) for row in rows})
    model['application_deadline_seconds'] = None
    rng = np.random.default_rng(seed)
    forecast = {'schema_version': 3, 'classes': {}, 'created_ns': time.time_ns(), 'draws_per_class': 100000,
                'baseline': 'identical direct conditional-state weighting', 'no_accuracy_success_gate': True}
    for operation, states in conditions.items():
        exact = [sum(WEIGHTS[s]*states[s]['identification_bounds'][i] for s in STATES) for i in (0, 1)]
        nominal = [sum(WEIGHTS[s]*states[s]['uncertainty_bounds'][i] for s in STATES) for i in (0, 1)]
        drawn = rng.choice(4, size=100000, p=list(WEIGHTS.values()))
        uniform = rng.random(100000)
        mc = [float(np.mean(uniform < np.asarray([states[s]['identification_bounds'][i] for s in STATES])[drawn])) for i in (0, 1)]
        if max(abs(a-b) for a, b in zip(exact, mc)) > .01:
            raise ValueError('MC failed exact-arithmetic check')
        forecast['classes'][operation] = {'point': exact[0] if math.isclose(*exact, abs_tol=1e-12) else None,
            'identification_bounds': exact, 'uncertainty_bounds': nominal, 'monte_carlo_bounds': mc}
    model['preparation_seconds'] = time.perf_counter()-started
    return model, forecast
