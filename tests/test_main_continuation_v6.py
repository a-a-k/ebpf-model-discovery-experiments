"""Synthetic provenance/barrier tests; no traffic, VM, model or swap provision."""
import copy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from ebpf_discovery import block_v6 as b, isolated_arm_v6 as isolated, main_continuation_v6 as continued
from ebpf_discovery.plan_v6 import COLLECTORS, block
from ebpf_discovery.runtime import write_json
from ebpf_discovery.validation_v6 import require_block_freeze
from tests.test_fresh_study_v6 import frozen

REAL_PARENT_GATE = continued.parent

@pytest.fixture(params=['partial', 'absent'])
def continued_models(tmp_path, monkeypatch, request):
    monkeypatch.setenv('GITHUB_RUN_ID', '900')
    monkeypatch.setenv('GITHUB_SHA', 'a' * 40)
    monkeypatch.setenv('GITHUB_REPOSITORY', 'a-a-k/ebpf-model-discovery-experiments')
    mode = request.param
    rep, run = (9, 42401605258) if mode == 'partial' else (10, 42401597551)
    old = block('otel_demo', mode, rep)
    old.update(stage='main', smoke=False, allocation_regime=isolated.REGIME, run_id=run,
               source=continued.ORIGINAL_SOURCE, blueprint_sha256='b' * 64, golden_sha256='c' * 64)
    old_sha = hashlib.sha256((json.dumps(old, indent=2) + '\n').encode()).hexdigest()
    ref = {'path': next(k for k, v in continued.PARENTS.items() if v == (mode, rep, run)), 'sha256': 'd' * 64}
    plan = {**old, **isolated.execution(), 'main_closed_input_parent': ref}
    value = {'mode': mode, 'parent_plan': old, 'parent_plan_sha256': old_sha, 'parent_run_id': old['run_id'],
             'blueprint_sha256': old['blueprint_sha256'], 'golden_sha256': old['golden_sha256'],
             'registered_before_processing_ns': 1, 'capture_case_by_collector': {},
             'closed_input_sha256_by_collector': {}, 'training_artifacts': {}}
    allocation = {'regime': isolated.REGIME, 'plan': plan,
                  'block_plan_sha256': hashlib.sha256((json.dumps(plan, indent=2) + '\n').encode()).hexdigest(),
                  'main_closed_input_parent': ref, 'models': {}}
    roots, jobs = [], {}
    for index, collector in enumerate(COLLECTORS):
        root = frozen(tmp_path / collector, collector, mode=mode, seed=rep)
        saved = b.read(root / 'forecast-saved.json')
        slot = old['arm_orders']['training'].index(collector)
        saved['case'].update(stage='main', smoke=False, run_id=str(old['run_id']), commit=old['source'],
            runner_boot_id='old-training-' + collector, blueprint_sha256=old['blueprint_sha256'],
            allocation_regime=isolated.REGIME,
            producing_job={'job': f'training{slot}', 'slot': slot, 'attempt': 1})
        write_json(root / 'closed-input.json', {'status': saved['case']})
        saved['training_closed_input_sha256'] = b.sha(root / 'closed-input.json')
        saved['saved_ns'] = 5
        saved['processing_execution'] = {'run_id': '900', 'commit': 'a' * 40,
            'runner_boot_id': 'new-model-' + collector, 'started_ns': 4, **continued.PROFILE}
        write_json(root / 'processing-execution.json', saved['processing_execution'])
        write_json(root / 'model-swap-resources.json', {'status': 'active',
            'additional_swap_file_bytes': continued.PROFILE['additional_model_swap_file_bytes']})
        for file in ('processing-execution.json', 'model-swap-resources.json'):
            saved['sha256_by_path'][file] = b.sha(root / file)
        write_json(root / 'forecast-saved.json', saved)
        write_json(root / 'capture-host-resources.json', {'original_capture_host': collector})
        write_json(root / 'v6-block-reference.json', {'run_id': old['run_id'], 'source': old['source'],
            'block_plan_sha256': old_sha, 'training_slot': slot, 'blueprint_sha256': old['blueprint_sha256'],
            'golden_sha256': old['golden_sha256'], 'allocation_regime': isolated.REGIME,
            'capture_host_resources_sha256': b.sha(root / 'capture-host-resources.json')})
        training = {'id': 100 + index, 'name': f'v6-isolated-training-slot{slot}-{old["run_id"]}-attempt1',
            'size_in_bytes': 123, 'digest': 'sha256:' + 'e' * 64, 'expired': False,
            'workflow_run': {'id': old['run_id'], 'head_sha': old['source']}}
        model = {'id': 200 + index, 'name': f'v6-isolated-model-slot{slot}-900-attempt1',
            'size_in_bytes': 456, 'digest': 'sha256:' + 'f' * 64, 'expired': False,
            'workflow_run': {'id': 900, 'head_sha': 'a' * 40}}
        jid = 300 + index
        jobs[str(jid)] = {'id': jid, 'run_id': 900, 'head_sha': 'a' * 40, 'run_attempt': 1,
                          'name': f'model{slot}', 'conclusion': 'success'}
        restored = {'artifact_API': training, 'original_capture_identity': saved['case'],
            'main_continuation_parent': ref, 'training_closed_input_sha256': saved['training_closed_input_sha256'],
            'model_producing_job': {'job': 'model', 'display_name': f'model{slot}', 'job_id': jid,
                'slot': slot, 'attempt': 1, 'runner_boot_id': saved['processing_execution']['runner_boot_id'], 'restored_ns': 3}}
        write_json(root / 'v6-training-publication-restored.json', restored)
        value['capture_case_by_collector'][collector] = copy.deepcopy(saved['case'])
        value['closed_input_sha256_by_collector'][collector] = saved['training_closed_input_sha256']
        value['training_artifacts'][collector] = training
        allocation['models'][collector] = {'case': saved['case'], 'forecast_sha256': b.sha(root / 'forecast-saved.json'),
                                         'training_artifact_API': training, 'model_artifact_API': model}
        roots.append(root)
    monkeypatch.setattr(continued, 'parent', lambda *_: value)
    monkeypatch.setattr(b, 'api', lambda url: jobs[url.rsplit('/', 1)[-1]])
    return roots, allocation, value, jobs


def test_truthful_old_main_capture_and_current_processing_open_only_explicit_barrier(continued_models):
    roots, allocation, _, _ = continued_models
    with pytest.raises(ValueError, match='one fresh paired block'):
        require_block_freeze(roots)
    frozen_block = require_block_freeze(roots, allocation=allocation)
    assert frozen_block['all_four_frozen_before_targets'] is True
    assert {m['case']['commit'] for m in frozen_block['models']} == {continued.ORIGINAL_SOURCE}
    assert allocation['plan']['source'] == 'a' * 40
    with pytest.raises(ValueError, match='all four'):
        require_block_freeze(roots[:-1], allocation=allocation)


@pytest.mark.parametrize('mutation', ['old_capture_relabelled', 'foreign_processing', 'wrong_training_slot',
                                    'before_registration', 'wrong_model_job', 'foreign_model_artifact'])
def test_foreign_or_relabelled_main_lineage_never_reaches_targets(continued_models, mutation):
    roots, allocation, _, jobs = continued_models
    root = roots[0]
    saved = b.read(root / 'forecast-saved.json')
    if mutation == 'old_capture_relabelled':
        saved['case']['commit'] = 'a' * 40
        allocation['models'][saved['case']['collector']]['case'] = saved['case']
    if mutation == 'foreign_processing':
        saved['processing_execution']['commit'] = '0' * 40
        write_json(root / 'processing-execution.json', saved['processing_execution'])
        saved['sha256_by_path']['processing-execution.json'] = b.sha(root / 'processing-execution.json')
    if mutation in ('wrong_training_slot', 'before_registration'):
        file = 'v6-block-reference.json' if mutation == 'wrong_training_slot' else 'v6-training-publication-restored.json'
        doc = b.read(root / file)
        if mutation == 'wrong_training_slot': doc['training_slot'] = 99
        else: doc['model_producing_job']['restored_ns'] = 0
        write_json(root / file, doc)
    if mutation == 'wrong_model_job': jobs['300']['head_sha'] = '0' * 40
    if mutation == 'foreign_model_artifact':
        allocation['models'][saved['case']['collector']]['model_artifact_API']['workflow_run']['id'] = 901
    write_json(root / 'forecast-saved.json', saved)
    allocation['models'][saved['case']['collector']]['forecast_sha256'] = b.sha(root / 'forecast-saved.json')
    with pytest.raises(ValueError):
        require_block_freeze(roots, allocation=allocation)


def test_continuation_has_no_training_jobs_and_each_target_waits_for_all_models():
    workflow = yaml.safe_load((Path(__file__).resolve().parents[1] / '.github/workflows/main-continuation-v6.yml').read_text())
    assert set(workflow['jobs']) == {'preflight', 'model', 'validation'}
    for role in ('model', 'validation'):
        job = workflow['jobs'][role]
        assert job['strategy']['matrix']['slot'] == [0, 1, 2, 3]
        assert job['strategy']['fail-fast'] is False
        assert job['runs-on'] == 'ubuntu-24.04' and job['timeout-minutes'] == 360
    assert workflow['jobs']['validation']['needs'] == ['preflight', 'model']


def test_main_parent_cannot_be_cast_as_qualification_or_use_unsigned_source(continued_models, monkeypatch, tmp_path):
    _, _, base, _ = continued_models
    # Use the real gate with synthetic provenance only, never execution helpers.
    original_parent = REAL_PARENT_GATE
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setattr(b, 'repo', lambda: tmp_path)
    hashes = {'synthetic_source': 'bound'}
    monkeypatch.setattr(b, 'implementation_hashes', lambda: hashes)
    ref = next(k for k, v in continued.PARENTS.items() if v[2] == base['parent_run_id'])
    doc = {**base, 'schema': 'v6-main-closed-input-parent-v1', 'study': 'clean-restart-v6',
        'system': 'otel_demo', 'mode': base['mode'], 'repetition': base['parent_plan']['repetition'], 'stage': 'main', 'smoke': False,
        'parent_source': continued.ORIGINAL_SOURCE, 'allocation_regime': isolated.REGIME,
        'root_parent_input_GO': True, 'independent_parent_input_GO': True,
        'root_original_execution_GO': True, 'independent_original_execution_GO': True,
        'processing_profile': continued.PROFILE, 'implementation_sha256': hashes,
        'shared_artifact': {'id': 999}}
    file = tmp_path / ref
    write_json(file, doc)
    assert original_parent(ref, b.sha(file))['stage'] == 'main'
    for key, value in [('stage', 'qualification'), ('parent_source', 'a' * 40),
            ('independent_parent_input_GO', False), ('independent_original_execution_GO', False),
            ('implementation_sha256', {}), ('processing_profile', {})]:
        broken = {**doc, key: value}
        write_json(file, broken)
        with pytest.raises(ValueError):
            original_parent(ref, b.sha(file))
    with pytest.raises(ValueError, match='four literal'):
        original_parent('docs/a-qualification-parent.json', '0' * 64)
