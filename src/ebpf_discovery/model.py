"""Empirical joint execution events, conservative missingness, and exact/MC transfer.

This module accepts only observations and the allow-listed census. Business labels
and independent oracle outcomes belong to evaluate.py, never to this interface.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import json
import math
import time

import numpy as np
from .observations import graph, route, step_id

STATES = ('11', '10', '01', '00')
WEIGHTS = dict(zip(STATES, (0.5, 0.25, 0.125, 0.125)))


def class_key(signature):
    return hashlib.sha256(json.dumps(signature, separators=(',', ':')).encode()).hexdigest()[:16]


class Projection:
    def __init__(self, spans):
        self.spans = spans
        self.headers = defaultdict(list)
        self.children = defaultdict(list)
        for s in spans:
            identity = step_id(s)
            if identity:
                self.headers[identity].append(s)
            self.children[(s['trace_id'], s['parent_id'])].append(s)

    def attempt(self, row):
        roots, signatures, events = [], [], []
        for identity in row['step_ids']:
            candidates = [s for s in self.headers.get(identity, []) if route(s)]
            servers = [s for s in candidates if s['kind'] in ('SPAN_KIND_SERVER', 2, 'server')]
            candidates = servers or candidates
            # Header binding plus earliest observed server boundary. Duplicates
            # from fusion describe the same request, not extra independent trials.
            candidates.sort(key=lambda s: (s['start_ns'], s['source'] != 'ebpf'))
            if not candidates:
                signatures.append(None)
                events.append(None)
                continue
            s = candidates[0]
            roots.append(s)
            signatures.append(route(s))
            attrs = s['attributes']
            status = attrs.get('http.response.status_code', attrs.get('http.status_code'))
            try:
                code = int(status)
            except (TypeError, ValueError):
                code = None
            if s['status'].get('code') in (2, 'STATUS_CODE_ERROR'):
                events.append(False)
            elif code and 100 <= code <= 599:
                events.append(200 <= code < 300)
            else:
                events.append(None)
        elapsed = (max(s['end_ns'] for s in roots) - min(s['start_ns'] for s in roots)) / 1e9 if roots else None
        complete = bool(events) and None not in events
        proxy = False if False in events or (elapsed is not None and elapsed > 2) else (True if complete else None)
        descendants, seen, queue = [], set(), list(roots)
        while queue:
            s = queue.pop()
            identity = (s['source'], s['node'], s['trace_id'], s['span_id'])
            if identity in seen:
                continue
            seen.add(identity)
            descendants.append((s['service'], route(s) or s['name'], s['attributes'].get('db.system.name', s['attributes'].get('db.system'))))
            queue.extend(self.children.get((s['trace_id'], s['span_id']), []))
        return {**row, 'signature': signatures, 'proxy': proxy, 'observed_window_seconds': elapsed,
                'bound_steps': len(roots), 'requested_steps': len(row['step_ids']),
                'downstream': sorted(set(descendants), key=str),
                'root_evidence': [{'source': s['source'], 'node': s['node'], 'trace_id': s['trace_id'], 'span_id': s['span_id']} for s in roots]}


def assign(row, classes):
    signature = row['signature']
    compatible = []
    for key, cls in classes.items():
        expected = cls['signature']
        if len(signature) > len(expected):
            continue
        if all(observed is None or observed == wanted for observed, wanted in zip(signature, expected)):
            if row['proxy'] is True and len(signature) != len(expected):
                continue
            compatible.append(key)
    # Novel/empty/entirely missing signatures cannot safely exclude a class.
    fallback = not compatible
    if fallback:
        compatible = list(classes)
    classified = compatible[0] if not fallback and len(compatible) == 1 and signature and all(signature) else None
    return {**row, 'class_id': classified, 'compatible_classes': compatible}


def wilson(successes, n, z=1.959963984540054):
    if not n:
        return [0.0, 1.0]
    p = successes / n
    divisor = 1 + z*z/n
    centre = (p + z*z/(2*n)) / divisor
    width = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / divisor
    return [max(0.0, centre-width), min(1.0, centre+width)]


def conditional(rows, key, state):
    known = [r for r in rows if r['state'] == state and r['class_id'] == key]
    ambiguous = [r for r in rows if r['state'] == state and r['class_id'] is None and key in r['compatible_classes']]
    successes = sum(r['proxy'] is True for r in known)
    unknown = sum(r['proxy'] is None for r in known)
    n = len(known) + len(ambiguous)
    # Conservative: every compatible unclassified attempt may belong to this
    # class with either outcome. Nothing failure-associated is dropped.
    low = successes/n if n else 0.0
    high = (successes+unknown+len(ambiguous))/n if n else 1.0
    return {'known_class_attempts': len(known), 'ambiguous_class_attempts': len(ambiguous),
            'known_successes': successes, 'known_failures': sum(r['proxy'] is False for r in known),
            'unknown_outcomes': unknown, 'identification_bounds': [low, high],
            'uncertainty_bounds': [wilson(successes, n)[0], wilson(successes+unknown+len(ambiguous), n)[1]],
            'uncertainty_method': 'weighted pointwise 95% Wilson envelopes; no simultaneous-coverage claim'}


def fit(spans, census, seed):
    start = time.perf_counter()
    projection = Projection(spans)
    projected = [projection.attempt(r) for r in census]
    classes = {}
    for row in projected:
        if row['phase'] == 'class_train' and row['proxy'] is True and all(row['signature']):
            key = class_key(row['signature'])
            classes[key] = {'signature': row['signature']}
    assigned = [assign(row, classes) for row in projected]
    calibration = [r for r in assigned if r['phase'] == 'calibration']
    conditionals = {key: {state: conditional(calibration, key, state) for state in STATES} for key in classes}
    model = {'schema_version': 1, 'created_ns': time.time_ns(), 'classes': classes,
             'conditional': conditionals, 'target_weights': WEIGHTS, 'graph': graph(spans),
             'census_attempts': len(census), 'calibration_attempts': len(calibration),
             'unclassified_calibration_attempts': sum(r['class_id'] is None for r in calibration),
             'manual_inputs': ['grouped HTTP-step census', 'replica states', '2s HTTP proxy deadline', 'target weights'],
             'outcome': 'joint observed HTTP 2xx and observed window <=2s; external semantics evaluated separately',
             'preparation_seconds': time.perf_counter()-start}
    rng = np.random.default_rng(seed)
    forecast = {'created_ns': time.time_ns(), 'draws_per_class': 100000, 'seed': seed, 'classes': {},
                'baseline': 'direct conditional-state weighting; algebraically equivalent'}
    for key, states in conditionals.items():
        draw_start = time.perf_counter()
        exact = [sum(WEIGHTS[s]*states[s]['identification_bounds'][i] for s in STATES) for i in (0, 1)]
        uncertainty = [sum(WEIGHTS[s]*states[s]['uncertainty_bounds'][i] for s in STATES) for i in (0, 1)]
        sampled_states = rng.choice(4, size=100000, p=[WEIGHTS[s] for s in STATES])
        uniforms = rng.random(100000)
        mc = [float(np.mean(uniforms < np.asarray([states[s]['identification_bounds'][i] for s in STATES])[sampled_states])) for i in (0, 1)]
        deviations = [abs(a-b) for a,b in zip(exact, mc)]
        if max(deviations) > .01:
            raise RuntimeError('100000-draw simulation differs from exact integration by over 1pp')
        forecast['classes'][key] = {'point': exact[0] if math.isclose(*exact, abs_tol=1e-12) else None,
                                    'identification_bounds': exact, 'uncertainty_bounds': uncertainty,
                                    'monte_carlo_bounds': mc, 'mc_absolute_deviation': deviations,
                                    'informative_width_10pp': uncertainty[1]-uncertainty[0] <= .10,
                                    'simulation_seconds': time.perf_counter()-draw_start}
    return model, forecast, assigned
