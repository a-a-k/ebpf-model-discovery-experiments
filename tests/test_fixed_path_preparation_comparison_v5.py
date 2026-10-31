"""Small adversarial metadata fixtures; full empirical comparison is Actions-only."""
from collections import Counter
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    'fixed_path_preparation_comparison',
    Path(__file__).parents[1]/'scripts/check-fixed-dsb-path-preparation-v5.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


def row(identity):
    return {'identity': identity, 'derived_otlp_proof': {'codec_accounting': {
        'sha256': 'a'*64, 'index_preparation_cost': {
            'started_ns': 12, 'ended_ns': 14, 'transient_index_bytes': 8192}}}}


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(value)+'\n' for value in rows), encoding='utf-8')


@pytest.mark.parametrize('change', ['payload_type', 'count', 'order', 'out_of_window', 'extra_clock'])
def test_index_whitelist_rejects_nonclock_changes(tmp_path, change):
    left = [row(1), row(2)]
    right = deepcopy(left)
    for value in right:
        value['derived_otlp_proof']['codec_accounting']['index_preparation_cost'].update(
            started_ns=32, ended_ns=34)
    if change == 'payload_type':
        right[0]['identity'] = True
    elif change == 'count':
        right[0]['derived_otlp_proof']['codec_accounting']['index_preparation_cost'][
            'transient_index_bytes'] += 1
    elif change == 'order':
        right.reverse()
    elif change == 'out_of_window':
        right[0]['derived_otlp_proof']['codec_accounting']['index_preparation_cost'][
            'started_ns'] = 29
    else:
        right[0]['started_ns'] = 32
    old, new = tmp_path/'old.jsonl', tmp_path/'new.jsonl'
    write_rows(old, left)
    write_rows(new, right)
    with pytest.raises(ValueError):
        comparison.compare_index(old, new, ((10, 20), (30, 40)), Counter())


def test_index_accepts_only_proven_clocks_and_preserves_duplicates(tmp_path):
    left = [row(1), row(1), row(2)]
    right = deepcopy(left)
    for value in right:
        value['derived_otlp_proof']['codec_accounting']['index_preparation_cost'].update(
            started_ns=32, ended_ns=34)
    old, new = tmp_path/'old.jsonl', tmp_path/'new.jsonl'
    write_rows(old, left)
    write_rows(new, right)
    clocks = Counter()
    assert comparison.compare_index(old, new, ((10, 20), (30, 40)), clocks)['rows'] == 3
    assert sum(clocks.values()) == 3
    write_rows(new, right[1:])
    with pytest.raises(ValueError, match='count|content'):
        comparison.compare_index(old, new, ((10, 20), (30, 40)), Counter())


def test_reference_requires_completed_child_proof_and_physical_hash(tmp_path):
    old, new, campaign = tmp_path/'old', tmp_path/'new', tmp_path/'campaign'
    for folder in (old, new):
        folder.mkdir()
        (folder/'index').write_text('actual', encoding='utf-8')
    reference = {'path': str(campaign/'toolchain/index'),
                 'bytes': (old/'index').stat().st_size, 'sha256': comparison._sha(old/'index')}
    with pytest.raises(ValueError, match='completed child'):
        comparison.bind_reference(deepcopy(reference), deepcopy(reference), campaign, old, new, set())
    comparison.bind_reference(deepcopy(reference), deepcopy(reference), campaign, old, new, {'index'})
    (new/'index').write_text('changed', encoding='utf-8')
    with pytest.raises(ValueError, match='SHA'):
        comparison.bind_reference(deepcopy(reference), deepcopy(reference), campaign, old, new, {'index'})
