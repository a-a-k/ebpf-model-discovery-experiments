"""Scientific boundary checks; no applications, VMs or model experiments run."""
import json
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from ebpf_discovery.collectors_v6 import NoAgent
from ebpf_discovery.plan_v6 import COLLECTORS, complete_plan, random_stream
from ebpf_discovery.study_v6 import verify_files
from ebpf_discovery.toolchain_v4 import digest
from ebpf_discovery.validation_v6 import require_block_freeze, require_forecast, graph_origin
from ebpf_discovery.resources_v6 import clear_go_overrides
from ebpf_discovery.capture_checks_v6 import verify_capture
from ebpf_discovery.transport_v4 import Journal


def frozen(root, collector, *, seed=9, system='otel_demo', mode='full'):
    root.mkdir()
    model = root / 'model.json'
    model.write_text('{"fixture":"immutable test model"}\n', encoding='utf8')
    metadata = {'study': 'clean-restart-v6', 'saved_ns': 1,
                'case': {'system': system, 'mode': mode, 'seed': seed,
                         'collector': collector, 'phase': 'training', 'smoke': True,
                         'stage': 'qualification'},
                'sha256_by_path': {'model.json': digest(model)}}
    closed = root / 'closed-input.json'
    closed.write_text(json.dumps({'status': metadata['case']}), encoding='utf8')
    metadata['training_closed_input_sha256'] = digest(closed)
    for relative in ('toolchain/forecasts.json', 'toolchain/context-baseline/forecasts.json',
                     'toolchain/manual-baselines.json', 'toolchain/classes/classes-family-model.json'):
        path = root / relative
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text('{}', encoding='utf8')
        metadata['sha256_by_path'][relative] = digest(path)
    (root / 'forecast-saved.json').write_text(json.dumps(metadata), encoding='utf8')
    return root


def test_full_matrix_has_real_none_controls_and_only_fresh_repetitions():
    plan = complete_plan()
    identities = set()
    for block in plan['blocks']:
        assert block['repetition'] in (9, 10, 11)
        assert {x['collector'] for x in block['cells']} == set(COLLECTORS)
        for phase in ('training', 'validation'):
            assert set(block['arm_orders'][phase]) == set(COLLECTORS)
            assert len(block['arm_orders'][phase]) == 4
        for cell in block['cells']:
            assert cell['cell_id'] not in identities
            identities.add(cell['cell_id'])
    assert len(identities) == plan['scientific_cells'] == 108
    assert len(plan['blocks']) == 27
    assert plan['historical_measurements_reused'] is False


def test_workload_and_treatment_order_have_separate_reproducible_streams():
    first = random_stream('otel_demo', 'partial', 10, 'training-workload')
    expected = [first.random() for _ in range(10)]
    order = random_stream('otel_demo', 'partial', 10, 'training-arm-order')
    for _ in range(100):
        order.random()
    second = random_stream('otel_demo', 'partial', 10, 'training-workload')
    assert [second.random() for _ in range(10)] == expected


def test_old_worker_heap_and_CPU_limits_do_not_leak_into_new_model_workers():
    environment = {'GOMEMLIMIT': '12GiB', 'GOMAXPROCS': '1', 'GOGC': '25',
                   'PATH': '/usr/bin', 'PBS_BIN': '/work/tools'}
    removed = clear_go_overrides(environment)
    assert removed == {'GOMEMLIMIT': '12GiB', 'GOMAXPROCS': '1', 'GOGC': '25'}
    assert environment == {'PATH': '/usr/bin', 'PBS_BIN': '/work/tools'}


def test_no_validation_without_all_four_frozen_runtime_arms(tmp_path):
    roots = [frozen(tmp_path / c, c) for c in COLLECTORS]
    assert require_block_freeze(roots)['all_four_frozen_before_targets'] is True
    with pytest.raises(ValueError, match='all four'):
        require_block_freeze(roots[1:])


def test_cannot_mix_another_repetition_into_a_paired_block(tmp_path):
    roots = [frozen(tmp_path / c, c, seed=10 if c == 'none' else 9) for c in COLLECTORS]
    with pytest.raises(ValueError, match='one fresh paired block'):
        require_block_freeze(roots)


def test_model_mutation_and_foreign_cell_cannot_enter_validation(tmp_path):
    root = frozen(tmp_path / 'obi', 'obi')
    with pytest.raises(ValueError, match='does not belong'):
        require_forecast(root, 'otel_demo', 'partial', 9, 'obi')
    (root / 'model.json').write_text('changed after freeze', encoding='utf8')
    with pytest.raises(ValueError, match='frozen evidence changed'):
        require_forecast(root, 'otel_demo', 'full', 9, 'obi')


def test_smoke_models_cannot_be_used_for_main_workload(tmp_path):
    root = frozen(tmp_path / 'obi', 'obi')
    with pytest.raises(ValueError, match='workload differs'):
        require_forecast(root, 'otel_demo', 'full', 9, 'obi', smoke=False, stage='main')


def test_changed_training_closure_cannot_enter_validation(tmp_path):
    root = frozen(tmp_path / 'obi', 'obi')
    (root / 'closed-input.json').write_text('{}', encoding='utf8')
    with pytest.raises(ValueError, match='closure manifest changed'):
        require_forecast(root, 'otel_demo', 'full', 9, 'obi')


@pytest.mark.parametrize('status', ['reuse_single_source_equivalence', 'reuse_unchanged_union'])
def test_context_reuse_resolves_actual_combined_graph_without_duplicate_simulation(tmp_path, status):
    folder = tmp_path / 'toolchain/context-baseline/raw'
    folder.mkdir(parents=True)
    (folder / 'provenance.json').write_text(json.dumps({'status': status}), encoding='utf8')
    forecast = {'available': True, 'prediction': .875}
    forecasts = {'combined': {'raw': {'checkout': dict(forecast)}}}
    path = graph_origin(tmp_path, 'context-baseline', 'raw', 'checkout', forecast, forecasts)
    assert path == tmp_path / 'toolchain/combined/raw/checkout/model.json'
    with pytest.raises(ValueError, match='differs from its frozen combined origin'):
        graph_origin(tmp_path, 'context-baseline', 'raw', 'checkout',
                     {'available': True, 'prediction': 1.0}, forecasts)


def test_model_manifest_cannot_refer_outside_its_bundle(tmp_path):
    secret = tmp_path / 'outside.txt'
    secret.write_text('not part of model bundle', encoding='utf8')
    root = tmp_path / 'model'
    root.mkdir()
    with pytest.raises(ValueError, match='frozen evidence changed'):
        verify_files(root, {'../outside.txt': digest(secret)})


def test_no_agent_uses_actual_process_census_not_absence_of_exported_spans(tmp_path):
    class Context:
        out = tmp_path

        def node_exec(self, node, command, **kwargs):
            return SimpleNamespace(stdout='study-obi-v5\n', returncode=0)

    collector = NoAgent(Context())
    with pytest.raises(RuntimeError, match='study agent is running'):
        collector.health()


def test_failed_docker_census_cannot_pass_no_agent_control(tmp_path):
    class Context:
        out = tmp_path

        def node_exec(self, node, command, **kwargs):
            return SimpleNamespace(stdout='', returncode=1 if command.startswith('docker') else 0)

    with pytest.raises(RuntimeError, match='census failed'):
        NoAgent(Context()).health()


def closed_training(root):
    for folder in ('observations', 'native', 'runtime-identity-v5'):
        (root / folder).mkdir(parents=True)
    status = {'study': 'clean-restart-v6', 'phase': 'training', 'status': 'capture_complete',
              'system': 'petclinic', 'mode': 'absent', 'seed': 9, 'collector': 'none',
              'stage': 'qualification', 'smoke': True}
    operations = ['list_owners', 'owner_details_with_visits', 'create_visit', 'list_vets']
    records = []
    for phase, states, size in [('class_train', ['11'], 12),
                                ('calibration', ['11', '10', '01', '00'], 4)]:
        for state in states:
            for i in range(size):
                identity = f'{phase}-{state}-{i}'
                records.append({'attempt_id': identity, 'phase': phase, 'state': state,
                                'operation': operations[i % 4], 'success': False,
                                'http_steps': [{'request_id': 'request-' + identity}]})
    plans = [{k: v for k, v in row.items() if k != 'success'} for row in records]
    census = [{'attempt_key': hashlib.sha256(row['attempt_id'].encode()).hexdigest(),
               'phase': row['phase'], 'state': row['state'],
               'step_ids': [s['request_id'] for s in row['http_steps']]} for row in records]
    journal = Journal(root / 'attempt-journal.sqlite')
    for block, state in enumerate(('11', '11', '10', '01', '00')):
        for operation in operations:
            identity = f'warmup-{block}-{operation}'
            row = {'attempt_id': identity, 'phase': 'preparation', 'state': state,
                   'operation': operation, 'success': False,
                   'http_steps': [{'request_id': 'request-' + identity}]}
            journal.append('attempt_intent', {k: v for k, v in row.items() if k != 'success'})
            journal.append('attempt_observed', row)
            records.append(row)
    journal.close()
    values = {'status.json': status, 'plans.json': plans, 'external.json': records, 'census.json': census}
    for name, value in values.items():
        (root / name).write_text(json.dumps(value), encoding='utf8')
    manifest = {'study': 'clean-restart-v6', 'phase': 'training', 'status': status,
                'files': {name: digest(root / name) for name in values}}
    manifest['files']['attempt-journal.sqlite'] = digest(root / 'attempt-journal.sqlite')
    (root / 'closed-input.json').write_text(json.dumps(manifest), encoding='utf8')
    return manifest


def test_valid_adverse_training_is_not_rejected_for_bad_outcomes(tmp_path):
    closed_training(tmp_path)
    assert verify_capture(tmp_path, 'training')['status']['status'] == 'capture_complete'


def test_postcapture_outcome_change_cannot_be_scored(tmp_path):
    closed_training(tmp_path)
    (tmp_path / 'external.json').write_text('[]', encoding='utf8')
    with pytest.raises(ValueError, match='frozen evidence changed'):
        verify_capture(tmp_path, 'training')


@pytest.mark.parametrize('change', ['forge_outcome', 'drop_warmup', 'relabel_scored'])
def test_unscored_preparation_cannot_hide_or_rewrite_observations(tmp_path, change):
    manifest = closed_training(tmp_path)
    path = tmp_path / 'external.json'
    rows = json.loads(path.read_text(encoding='utf8'))
    warmup = next(i for i, row in enumerate(rows) if row['phase'] == 'preparation')
    if change == 'forge_outcome':
        rows[warmup]['success'] = True
    elif change == 'drop_warmup':
        rows.pop(warmup)
    else:
        rows[0]['phase'] = 'preparation'
    path.write_text(json.dumps(rows), encoding='utf8')
    manifest['files']['external.json'] = digest(path)
    (tmp_path / 'closed-input.json').write_text(json.dumps(manifest), encoding='utf8')
    with pytest.raises(ValueError, match='preparation'):
        verify_capture(tmp_path, 'training')


def test_unmanifested_raw_input_cannot_enter_discovery(tmp_path):
    closed_training(tmp_path)
    (tmp_path / 'observations' / 'extra.jsonl').write_text('{}', encoding='utf8')
    with pytest.raises(ValueError, match='unmanifested'):
        verify_capture(tmp_path, 'training')


def test_duplicate_attempt_cannot_pass_just_by_resealing_aggregate_counts(tmp_path):
    manifest = closed_training(tmp_path)
    p = tmp_path / 'external.json'
    records = json.loads(p.read_text(encoding='utf8'))
    records[1]['attempt_id'] = records[0]['attempt_id']
    p.write_text(json.dumps(records), encoding='utf8')
    manifest['files']['external.json'] = digest(p)
    (tmp_path / 'closed-input.json').write_text(json.dumps(manifest), encoding='utf8')
    with pytest.raises(ValueError, match='integrity failed'):
        verify_capture(tmp_path, 'training')
