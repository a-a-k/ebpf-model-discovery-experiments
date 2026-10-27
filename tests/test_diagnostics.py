import pytest

from ebpf_discovery.diagnostics import diagnostic_cell, score, semantic_census


def rows():
    assignments = [{'attempt_key': state, 'phase': 'calibration', 'state': state,
                    'class_id': 'original' if state != '00' else None,
                    'compatible_classes': ['original'], 'proxy': state != '00'}
                   for state in ('11', '10', '01', '00')]
    gold = {r['attempt_key']: {'phase': 'calibration', 'state': r['state'],
                             'operation': 'op', 'success': r['state'] != '00'} for r in assignments}
    return assignments, gold


def test_label_oracle_isolates_failure_class_ambiguity_without_repairing_proxy():
    assignments, gold = rows()
    original, _ = diagnostic_cell(assignments, gold, 'original', 'op', 'original')
    oracle, _ = diagnostic_cell(assignments, gold, 'original', 'op', 'oracle_class')
    assert original['identification_bounds'] == [.875, 1.]
    assert oracle['identification_bounds'] == [.875, .875]
    assert assignments[-1]['class_id'] is None


def test_outcome_oracle_keeps_class_ambiguity_and_unknown_business_outcome():
    assignments, gold = rows()
    gold['11']['success'] = None
    outcome, _ = diagnostic_cell(assignments, gold, 'original', 'op', 'oracle_outcome')
    both, _ = diagnostic_cell(assignments, gold, 'original', 'op', 'oracle_both')
    assert outcome['identification_bounds'] == [.375, 1.]
    assert both['identification_bounds'] == [.375, .875]


def test_target_outcomes_are_rejected_at_fitting_boundary():
    assignments, gold = rows()
    gold['11']['phase'] = 'target'
    with pytest.raises(ValueError, match='Target outcomes'):
        diagnostic_cell(assignments, gold, 'original', 'op', 'oracle_both')


def test_missing_native_class_is_not_repaired_by_outcome_oracle():
    assignments, gold = rows()
    for row in assignments:
        row.update(class_id=None, compatible_classes=[], proxy=None)
    observed, _ = diagnostic_cell(assignments, gold, None, 'op', 'oracle_outcome')
    classes, _ = diagnostic_cell(assignments, gold, None, 'op', 'oracle_class')
    assert observed['identification_bounds'] == [0., 1.]
    assert classes['identification_bounds'] == [0., 1.]


def test_semantic_audit_census_does_not_expose_outcome_or_payload():
    source = {'attempt_id': 'sensitive-labelled-attempt', 'operation': 'op', 'phase': 'target',
              'state': '11', 'started_ns': 0, 'ended_ns': 100, 'success': True,
              'http_steps': [{'request_id': 'opaque', 'status': 200, 'json': {'secret': 1}}],
              'validation': {'row_persisted': True}}
    projected = semantic_census([source])[0]
    assert set(projected) == {'attempt_key', 'step_ids', 'contract_id', 'phase', 'state',
                              'started_ns', 'ended_ns', 'deadline_ns'}
    assert projected['attempt_key'] != source['attempt_id']


def test_wilson_padding_is_separate_from_identification_error():
    result = score({'point': .5, 'identification_bounds': [.5, .5], 'uncertainty_bounds': [.4, .6]},
                   {'point': .5, 'bounds': [.5, .5], 'n': 10, 'unknown': 0})
    assert result['absolute_error_pp'] == 0
    assert result['identification_worst_error_pp'] == 0
    assert result['wilson_padding_pp'] == pytest.approx(20)
    assert result['wilson_worst_error_pp'] == pytest.approx(10)
