"""Synthetic report-integrity checks; no empirical capture/model processing."""
from copy import deepcopy

import pytest

from ebpf_discovery.compose_ack_contract import OPERATIONS, UNAVAILABLE, direct_baselines
from ebpf_discovery.compose_ack_publication import derived_statistics
from ebpf_discovery.compose_ack_publication import interval_seconds
from ebpf_discovery.compose_ack_repair import ARMS, project_targets
from tests.test_compose_ack_repair import synthetic_records


def summary():
    forecasts = {source: {view: {op: deepcopy(UNAVAILABLE) for op in OPERATIONS}
                         for view in ('raw', 'network_scope')}
                 for source in ('ebpf', 'native', 'combined', 'context-baseline')}
    result = project_targets(forecasts, direct_baselines(), synthetic_records(), {})
    return {'cases': [{'key': ['deathstarbench', mode, repetition, arm], 'result': deepcopy(result)}
                      for mode in ('absent', 'partial', 'full') for repetition in (9, 10, 11) for arm in ARMS]}


def test_publication_counts_measurements_once_and_retains_unavailable_forecasts():
    value = derived_statistics(summary())
    assert value['all_retained_phase_counts']['target'] == 345600
    assert len(value['direct_primary']) == 108
    assert len(value['availability']) == 144
    assert {r['source'] for r in value['availability']} == {'native', 'ebpf', 'combined', 'context-baseline'}
    assert all(r['primary']['known'] == 0 and r['primary']['unknown'] == 9
               for r in value['comparison_by_mode_collector_source_view'])
    assert sum(r['counts']['unknown'] for r in value['direct_primary']) == 36


def test_source_projection_cannot_silently_drop_unknown_observations():
    value = summary()
    value['cases'][0]['result']['rows'][0]['observed']['unknown'] = 0
    with pytest.raises(ValueError, match='same measured operation outcomes'):
        derived_statistics(value)


def test_inconsistent_platform_worker_times_are_unknown_not_zero_or_negative():
    job = {'started_at': '2026-11-09T21:00:01Z', 'completed_at': '2026-11-09T21:00:00Z'}
    assert interval_seconds(job) is None
    assert interval_seconds({'started_at': job['started_at'], 'completed_at': None}) is None
    assert interval_seconds({'started_at': job['completed_at'], 'completed_at': job['started_at']}) == 1
