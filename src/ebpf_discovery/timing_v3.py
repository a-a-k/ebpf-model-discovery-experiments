"""Observation bookkeeping and client-observed HTTP curves, without an SLO."""
from collections import defaultdict


def seal_attempt(record):
    observation = record.get('observation') or {}
    if observation.get('policy') != 'censored-v3':
        return record
    receipts = [step.get('body_completed_ns', step.get('ended_ns')) for step in record['http_steps']
                if step.get('status') is not None]
    if any(value is not None and value > observation['cutoff_ns'] for value in receipts):
        observation.update(censored=True, termination='cap_reached', late_completed_response_retained=True)
    if observation['censored']:
        record['success'] = None
    return record


def automatic_census(records, rows):
    """Add transport-window facts without operation labels or planned length."""
    from .observations import opaque_attempt
    by_key = {opaque_attempt(record): record for record in records}
    output = []
    for row in rows:
        record = by_key[row['attempt_key']]
        observation = record.get('observation') or {}
        output.append({**row, 'started_ns': record['started_ns'], 'deadline_ns': observation['cutoff_ns'],
                       'observation_policy': observation['policy'],
                       'observation_censored': observation['censored']})
    return output


def http_curves(records, cap_seconds=10.0):
    """Descriptive response receipt curves; SQL durability time is not inferred."""
    groups = defaultdict(list)
    for record in records:
        if record['phase'] in ('class_train', 'calibration', 'target', 'class_test'):
            groups[(record['phase'], record['state'], record['operation'])].append(record)
    summaries = []
    grid = [cap_seconds*i/100 for i in range(101)]
    for (phase, state, operation), population in sorted(groups.items()):
        observed = []
        for record in population:
            if record['observation']['censored']:
                continue
            receipts = [step.get('body_completed_ns', step.get('ended_ns')) for step in record['http_steps']
                        if step.get('status') is not None]
            receipts = [value for value in receipts if value is not None]
            if receipts:
                observed.append((max(receipts)-record['started_ns'])/1e9)
        n = len(population)
        summaries.append({'phase': phase, 'state': state, 'operation': operation, 'n': n,
            'completed_response_observations': len(observed),
            'censored': sum(record['observation']['censored'] for record in population),
            'points': [{'seconds': t, 'fraction': sum(value <= t for value in observed)/n} for t in grid]})
    return {'meaning': 'cumulative observed HTTP response fraction; includes incorrect HTTP responses',
            'censor_adjustment': 'none; every attempt remains in the denominator',
            'is_estimated_uncensored_completion_distribution': False,
            'not_business_success_or_database_commit_latency': True, 'application_slo': None,
            'engineering_observation_cap_seconds': cap_seconds, 'shared_journal_for_all_methods': True,
            'curves': summaries}
