"""Validate frozen predictions without changing models or fitting target labels."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import sqlite3
import threading
import time
from types import SimpleNamespace

from .evaluate_v4 import _async_results, _counts, _error, _bounds, _latency, _valid_forecast
from .plan_v6 import COLLECTORS, STUDY
from .runtime import write_json
from .study import workload_counts
from .study_v6 import declaration, verify_files
from .toolchain_v4 import digest


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def require_forecast(root, system, mode, repetition, collector, *, smoke=None, stage=None):
    root = Path(root).resolve()
    saved = read(root / 'forecast-saved.json')
    identity = saved['case']
    if (saved.get('study') != STUDY or identity.get('phase') != 'training'
            or (identity['system'], identity['mode'], identity['seed'], identity['collector'])
            != (system, mode, repetition, collector)):
        raise ValueError('forecast does not belong to this fresh validation cell')
    if ((smoke is not None and identity.get('smoke') is not smoke)
            or (stage is not None and identity.get('stage') != stage)):
        raise ValueError('forecast qualification/main workload differs from validation')
    closed_path = root / 'closed-input.json'
    if digest(closed_path) != saved.get('training_closed_input_sha256'):
        raise ValueError('frozen training closure manifest changed')
    if read(closed_path).get('status') != identity:
        raise ValueError('forecast identity differs from its closed training source')
    verify_files(root, saved['sha256_by_path'])
    mandatory = {'toolchain/forecasts.json', 'toolchain/context-baseline/forecasts.json',
                 'toolchain/manual-baselines.json', 'toolchain/classes/classes-family-model.json'}
    if not mandatory.issubset(saved['sha256_by_path']):
        raise ValueError('portable model bundle lacks its frozen scientific outputs')
    if (root / 'validation-external.json').exists():
        raise ValueError('a forecast input bundle must not contain validation targets')
    return saved


def require_block_freeze(roots, *, allocation=None):
    """The workflow calls this for ALL four arms before starting validation."""
    saved = []
    for root in roots:
        metadata = read(Path(root) / 'forecast-saved.json')['case']
        saved.append(require_forecast(root, metadata['system'], metadata['mode'],
                                      metadata['seed'], metadata['collector']))
    if len(saved) != 4 or {s['case']['collector'] for s in saved} != set(COLLECTORS):
        raise ValueError('all four fresh runtime arms must be frozen before targets')
    if allocation is not None:
        from .isolated_arm_v6 import verify_allocation
        verify_allocation(roots, saved, allocation)
    identities = {(s['case']['system'], s['case']['mode'], s['case']['seed'], s['case']['smoke'],
                   s['case'].get('stage'), s['case'].get('blueprint_sha256'),
                   s['case'].get('run_id'), s['case'].get('runner_boot_id') if allocation is None else None)
                  for s in saved}
    if len(identities) != 1:
        raise ValueError('models do not form one fresh paired block')
    return {'study': STUDY, 'all_four_frozen_before_targets': True,
            **({'allocation': allocation} if allocation is not None else {}),
            'verified_ns': time.time_ns(), 'models': [
                {'case': s['case'], 'forecast_manifest_sha256': digest(Path(p) / 'forecast-saved.json')}
                for p, s in zip(roots, saved)]}


def graph_origin(frozen, source, variant, operation, forecast, forecasts):
    origin = source
    if source == 'context-baseline':
        provenance = read(frozen / 'toolchain/context-baseline' / variant / 'provenance.json')
        if provenance.get('status') in ('reuse_single_source_equivalence', 'reuse_unchanged_union'):
            if forecast != forecasts['combined'][variant][operation]:
                raise ValueError('reused context forecast differs from its frozen combined origin')
            origin = 'combined'
        elif provenance.get('status') != 'forecast_from_observed_context_union':
            raise ValueError('available context forecast has no admitted frozen execution origin')
    return (frozen / 'toolchain/context-baseline' / variant / 'operations' / operation / 'model.json'
            if origin == 'context-baseline' else
            frozen / 'toolchain' / origin / variant / operation / 'model.json')


def classify(frozen, validation, saved):
    """Apply only frozen roles/families to observations from the fresh boot."""
    from .runtime import Context
    from .identity_projection_v5 import refresh
    from .store_v5 import ObservationStoreV5
    from .classes_v5 import evaluate as evaluate_classes
    from .evaluate_v5 import acquisition_checks
    status = read(validation / 'status.json')
    ctx = Context(validation, status['mode'], status['seed'])
    ctx.collector = status['collector']
    connection = sqlite3.connect((validation / 'attempt-journal.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)
    ctx.journal = SimpleNamespace(db=connection, lock=threading.Lock(),
                                 path=validation / 'attempt-journal.sqlite')
    # Only frozen logical alias definitions and their inventory proof cross epochs.
    # Old boot-specific capture files are NOT mixed into the validation inventory.
    for name in ('supplied-service-aliases-training.json',
                 'supplied-service-alias-admission-training.json', 'inventory-training.json'):
        source = frozen / 'runtime-identity-v5' / name
        target = validation / 'runtime-identity-v5' / name
        if target.exists():
            if digest(target) != digest(source):
                raise ValueError('validation tried to replace a frozen logical alias dependency')
        else:
            shutil.copyfile(source, target)
    plans, records = read(validation / 'plans.json'), read(validation / 'external.json')
    store = ObservationStoreV5(validation / 'observation-index.sqlite', same_trace_parents=True)
    declared = declaration(status['system'])
    try:
        write_json(validation / 'index-validation.json',
                   store.ingest(validation / 'observations', validation / 'native'))
        acquisition = acquisition_checks(validation, status, declared,
                                         agent_expected=status['collector'] != 'none')
        write_json(validation / 'validation-acquisition-checks.json', acquisition)
        if not acquisition['valid']:
            raise ValueError('validation acquisition invalid: ' + ','.join(acquisition['problems']))
        refresh(SimpleNamespace(ctx=ctx, store=store, plans=plans, collector=status['collector']), 'validation')
        result = evaluate_classes(store, plans, records, declared,
                                  frozen / 'toolchain/classes/classes-family-model.json',
                                  validation / 'class-evaluation')
        verify_files(frozen, saved['sha256_by_path'])
        return result
    finally:
        store.close()
        connection.close()


def evaluate(frozen, validation, *, allocation=None):
    frozen, validation = Path(frozen).resolve(), Path(validation).resolve()
    from .capture_checks_v6 import verify_capture
    closed = verify_capture(validation, 'validation')
    status = closed['status']
    if status.get('study') != STUDY or status.get('phase') != 'validation':
        raise ValueError('not a fresh v6 validation deployment')
    saved = require_forecast(frozen, status['system'], status['mode'], status['seed'], status['collector'],
                             smoke=status['smoke'], stage=status['stage'])
    if status.get('blueprint_sha256') != saved['case'].get('blueprint_sha256'):
        raise ValueError('training and validation blueprints differ')
    receipt = read(validation / 'block-freeze-verified-before-capture.json')
    current = require_block_freeze([frozen.parent / collector for collector in COLLECTORS], allocation=allocation)
    if (receipt.get('models') != current['models'] or receipt.get('allocation') != current.get('allocation')
            or receipt.get('all_four_frozen_before_targets') is not True
            or receipt.get('verified_ns', status['started_ns']) >= status['started_ns']):
        raise ValueError('missing or inconsistent four-arm freeze before validation capture')
    if saved['saved_ns'] >= status['started_ns']:
        raise ValueError('forecast was not fixed before this validation deployment')
    class_result = classify(frozen, validation, saved)
    # Derived indexing/classification cannot change any sealed source or target.
    verify_files(validation, closed['files'])
    records = read(validation / 'external.json')
    declared = declaration(status['system'])
    counts = workload_counts(len(declared.CONTRACTS), status['smoke'])
    problems = []
    if status['status'] != 'capture_complete':
        problems.append('incomplete_validation_capture')
    expected_phases = {'target': 8 * counts['target'], 'class_test': counts['class_test'],
                       'db_up': counts['database'], 'db_down': counts['database']}
    observed_phases = Counter(r['phase'] for r in records)
    if any(observed_phases[p] != n for p, n in expected_phases.items()):
        problems.append('workload_phase_counts_differ_from_protocol')
    targets = [r for r in records if r['phase'] == 'target']
    expected_states = {s: counts['target'] * n for s, n in [('11', 4), ('10', 2), ('01', 1), ('00', 1)]}
    if dict(Counter(r['state'] for r in targets)) != expected_states:
        problems.append('target_replica_state_mixture_differs_from_protocol')
    forecasts = read(frozen / 'toolchain' / 'forecasts.json')
    forecasts['context-baseline'] = read(frozen / 'toolchain' / 'context-baseline' / 'forecasts.json')
    direct = read(frozen / 'toolchain' / 'manual-baselines.json')
    rows = []
    for operation in declared.CONTRACTS:
        actual = [r for r in targets if r['operation'] == operation]
        observed = _counts(actual)
        if observed['total'] != 8 * counts['target'] // len(declared.CONTRACTS):
            problems.append('unbalanced_operation:' + operation)
        for source, variants in forecasts.items():
            for variant, operations in variants.items():
                forecast = operations[operation]
                available = _valid_forecast(forecast)
                if forecast.get('available') is True and not available:
                    raise ValueError('a claimed available forecast is malformed')
                graph_path = None
                if available:
                    graph_path = graph_origin(frozen, source, variant, operation, forecast, forecasts)
                    if forecast.get('simulator') != 'Sheaft' or digest(graph_path) != forecast.get('graph_sha256'):
                        raise ValueError('forecast does not bind its actual executed Sheaft graph')
                prediction = forecast.get('prediction') if available else None
                db_records = [r for r in records if r['phase'] == 'db_down' and r['operation'] == operation]
                db_up = [r for r in records if r['phase'] == 'db_up' and r['operation'] == operation]
                by_state = {}
                for state in ('11', '10', '01', '00'):
                    state_counts = _counts([r for r in actual if r['state'] == state])
                    state_prediction = forecast.get('by_state', {}).get(state) if available else None
                    by_state[state] = {'actual_counts': state_counts, 'prediction': state_prediction,
                                       'error': _error(state_prediction, _bounds(state_counts))}
                healthy = forecast.get('by_state', {}).get('11') if available else None
                down = forecast.get('database_down_prediction') if available else None
                rows.append({'operation': operation, 'source': source, 'variant': variant,
                             'available': available, 'prediction': prediction,
                             'forecast_interval': forecast.get('interval'), 'by_state': by_state,
                             'unavailable_reason': forecast.get('reason') if not available else None,
                             'unknown_obligations': forecast.get('unknown'),
                             'assumed_satisfied_database_requirements': forecast.get('assumed_satisfied_database_requirements'),
                             'actual_counts': observed, 'observed_bounds': _bounds(observed),
                             'error': _error(prediction, _bounds(observed)),
                             'direct_reference': direct[operation],
                             'database_down_prediction': down,
                             'database_down_actual_counts': _counts(db_records),
                             'database_up_actual_counts': _counts(db_up),
                             'database_prognostic_impact': healthy - down if healthy is not None and down is not None else None,
                             'graph_sha256': forecast.get('graph_sha256')})
                rows[-1]['graph_origin'] = graph_path.relative_to(frozen).as_posix() if graph_path else None
    result = {'study': STUDY, 'cell': status, 'technical_complete': not problems,
              'technical_problems': sorted(set(problems)), 'forecast_manifest_sha256': digest(frozen / 'forecast-saved.json'),
              'validation_closed_input_sha256': digest(validation / 'closed-input.json'),
              'rows': rows, 'target_latency': _latency(targets),
              'frozen_classification': class_result,
              'asynchronous': _async_results(validation) if status['system'] == 'otel_demo' else None,
              'source_views_reuse_same_cell_outcomes': True,
              'no_accuracy_or_support_admission_threshold': True,
              'target_labels_used_to_fit_forecasts': False}
    write_json(validation / 'evaluation-v6.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frozen', type=Path, required=True)
    parser.add_argument('--validation', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.frozen, args.validation)
    if not result['technical_complete']:
        raise SystemExit('incomplete technical evidence, not a negative scientific result')


if __name__ == '__main__':
    main()
