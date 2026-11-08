"""Allocation/transfer barriers only; no VM, application or scientific computation."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tarfile
from types import SimpleNamespace
import zipfile

import pytest
import yaml

from ebpf_discovery import block_v6 as b, isolated_arm_v6 as isolated
from ebpf_discovery.plan_v6 import COLLECTORS, SYSTEMS, block
from ebpf_discovery.runtime import write_json
from ebpf_discovery.validation_v6 import require_block_freeze
from tests.test_fresh_study_v6 import frozen


@pytest.fixture
def allocated(tmp_path, monkeypatch):
    monkeypatch.setenv('GITHUB_RUN_ID', '900')
    monkeypatch.setenv('GITHUB_SHA', 'a'*40)
    plan = block('otel_demo', 'absent', 9)
    plan.update(stage='qualification', smoke=False, allocation_regime=isolated.REGIME,
                run_id=900, source='a'*40, blueprint_sha256='b'*64, golden_sha256='c'*64)
    plan_sha = hashlib.sha256((json.dumps(plan, indent=2)+'\n').encode()).hexdigest()
    allocation = {'regime': isolated.REGIME, 'plan': plan, 'block_plan_sha256': plan_sha, 'models': {}}
    roots = []
    for index, collector in enumerate(COLLECTORS):
        root = frozen(tmp_path/collector, collector, mode='absent')
        saved = b.read(root/'forecast-saved.json')
        saved['case'].update(smoke=False, run_id='900', commit='a'*40,
            runner_boot_id='actual-distinct-'+collector, blueprint_sha256='b'*64,
            allocation_regime=isolated.REGIME,
            producing_job={'job':f"training{plan['arm_orders']['training'].index(collector)}",'slot':plan['arm_orders']['training'].index(collector),'attempt':2})
        write_json(root/'closed-input.json', {'status': saved['case']})
        saved['training_closed_input_sha256'] = b.sha(root/'closed-input.json')
        saved['processing_execution']={'run_id':'900','commit':'a'*40,'runner_boot_id':'model-'+collector,'started_ns':1}
        write_json(root/'processing-execution.json',saved['processing_execution'])
        saved['sha256_by_path']['processing-execution.json']=b.sha(root/'processing-execution.json')
        write_json(root/'forecast-saved.json', saved)
        slot = plan['arm_orders']['training'].index(collector)
        write_json(root/'capture-host-resources.json', {'cpu_count': 4, 'actual_boot': collector})
        write_json(root/'v6-block-reference.json', {'block_plan_sha256': plan_sha,
            'blueprint_sha256': 'b'*64, 'allocation_regime': isolated.REGIME,
            'golden_sha256':'c'*64,'run_id':900,'source':'a'*40,
            'training_slot': slot, 'capture_host_resources_sha256': b.sha(root/'capture-host-resources.json')})
        def api(phase, suffix):
            return {'id': 100+index*10+suffix, 'name': f'v6-isolated-{phase}-slot{slot}-900-attempt2',
                'digest': 'sha256:'+'d'*64, 'size_in_bytes': 123, 'expired': False,
                'workflow_run': {'id': 900, 'head_sha': 'a'*40}}
        training, model = api('training', 1), api('model', 2)
        write_json(root/'v6-training-publication-restored.json', {'artifact_API': training,
            'model_producing_job': {'job':f'model{slot}','slot':slot,'attempt':2,
                'runner_boot_id':'model-'+collector,'restored_ns':0},
            'training_closed_input_sha256':saved['training_closed_input_sha256']})
        allocation['models'][collector] = {'case': saved['case'], 'forecast_sha256': b.sha(root/'forecast-saved.json'),
            'training_artifact_API': training, 'model_artifact_API': model}
        roots.append(root)
    return roots, allocation


def test_between_host_receipt_preserves_strict_default_and_binds_actual_models(allocated):
    roots, allocation = allocated
    with pytest.raises(ValueError, match='one fresh paired block'):
        require_block_freeze(roots)
    value = require_block_freeze(roots, allocation=allocation)
    assert value['all_four_frozen_before_targets'] is True
    assert value['allocation'] == allocation
    with pytest.raises(ValueError, match='all four'):
        require_block_freeze(roots[:-1], allocation=allocation)


@pytest.mark.parametrize('mutation', ['foreign_source','wrong_slot','missing_arm','wrong_plan','wrong_regime','wrong_model'])
def test_foreign_or_incomplete_allocation_cannot_open_validation(allocated, mutation):
    roots, original = allocated
    allocation = copy.deepcopy(original)
    if mutation == 'foreign_source': allocation['models']['obi']['model_artifact_API']['workflow_run']['head_sha'] = 'e'*40
    if mutation == 'wrong_slot': allocation['models']['obi']['model_artifact_API']['name'] = 'v6-isolated-model-slot9-900-attempt2'
    if mutation == 'missing_arm': del allocation['models']['none']
    if mutation == 'wrong_plan': allocation['block_plan_sha256'] = '0'*64
    if mutation == 'wrong_regime': allocation['regime'] = 'paired-but-relabelled'
    if mutation == 'wrong_model': allocation['models']['coroot']['forecast_sha256'] = '0'*64
    with pytest.raises(ValueError): require_block_freeze(roots, allocation=allocation)


def test_changed_actual_capture_host_record_rejects(allocated):
    roots, allocation = allocated
    write_json(roots[0]/'capture-host-resources.json', {'wrong': 'host'})
    with pytest.raises(ValueError, match='host/slot/source/closure'):
        require_block_freeze(roots, allocation=allocation)


def test_failed_model_barrier_runs_no_guests_or_targets(tmp_path, monkeypatch):
    monkeypatch.setenv('GITHUB_RUN_ID','900')
    monkeypatch.setenv('GITHUB_RUN_ATTEMPT','1')
    args = SimpleNamespace(capture_phase='validation', slot=0, system='otel_demo', mode='absent', repetition=9, stage='main')
    plan = block(args.system,args.mode,args.repetition)
    monkeypatch.setattr(isolated,'import_shared',lambda *_:plan)
    def failed(*_): raise ValueError('missing exact fourth frozen model')
    monkeypatch.setattr(isolated,'import_models',failed)
    monkeypatch.setattr(b,'vms',lambda *_:pytest.fail('guest started before model barrier'))
    with pytest.raises(ValueError,match='fourth'):
        isolated.capture(args,tmp_path)


def test_exact_upstream_id_required_and_metadata_extras_rejected():
    valid = {'artifact_id':'123','artifact_digest':'sha256:'+'a'*64,'artifact_name':'actual-attempt2','collector':'none'}
    assert isolated.dependency(json.dumps(valid))['id'] == 123
    for broken in ({**valid,'artifact_id':''},{**valid,'artifact_id':'not-an-ID'},{**valid,'override':'foreign'}):
        with pytest.raises(ValueError): isolated.dependency(json.dumps(broken))


def test_original_assignments_exact24_scope_plus_registered_DSB_replacement():
    total=0
    for system in SYSTEMS:
        for mode in ('absent','partial','full'):
            for repetition in (9,10,11):
                args=SimpleNamespace(system=system,mode=mode,repetition=repetition,stage='main')
                if mode=='full' and repetition==9 and system!='deathstarbench':
                    with pytest.raises(ValueError,match='paired blocks'): isolated.planned(args)
                else:
                    assert isolated.planned(args)['arm_orders']==block(system,mode,repetition)['arm_orders']
                    assert isolated.planned(args)['smoke'] is False
                    total+=1
    assert total==25


def test_staged_gate_cannot_enlarge_blocks_or_claim_resource_fit(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    hashes={'source':'bound'}
    approval={k:True for k in ('original_source_execution_GO','root_original_GO','independent_original_GO','original_scientific_rollout_GO')}
    approval.update(blocks=isolated.STAGED_BLOCKS,allocation_regime=isolated.REGIME,
        full_size_phase_budgets_qualified=False,rollout_design_GO_sha256=isolated.STAGED_DESIGN_SHA256,
        DSB_retry_design_GO_sha256=isolated.DSB_RETRY_DESIGN_SHA256,failed_DSB_attempt=isolated.DSB_ORIGINAL,
        all_four_replacement_captures_new=True,old_DSB_inputs_imported=False,implementation_sha256=hashes)
    monkeypatch.setattr(b,'read',lambda *_:approval)
    monkeypatch.setattr(b,'implementation_hashes',lambda:hashes)
    args=SimpleNamespace(system='petclinic',mode='absent',repetition=9,stage='main')
    isolated.gate(args)
    for key,value in [('full_size_phase_budgets_qualified',True),('blocks',isolated.STAGED_BLOCKS+['petclinic-partial-9']),
                      ('implementation_sha256',{}),('independent_original_GO',False),('DSB_retry_design_GO_sha256','0'*64),
                      ('old_DSB_inputs_imported',True),('failed_DSB_attempt',{})]:
        old=approval[key];approval[key]=value
        with pytest.raises(ValueError,match='four-block'): isolated.gate(args)
        approval[key]=old
    monkeypatch.setattr(b,'gate',lambda *_:(_ for _ in ()).throw(ValueError('ordinary full-size gate retained')))
    args.mode='partial'
    args.system='otel_demo'
    with pytest.raises(ValueError,match='remaining20'): isolated.gate(args)


def test_PC_DSB_scope_preserves_OTel_hold_and_rejects_false_fit(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    hashes={'unchanged_method':'bound'}
    approval={k:True for k in ('original_source_execution_GO','root_original_GO',
        'independent_original_GO','original_scientific_rollout_GO',
        'original108_scope_retained','partial_unknown_budget_risk_accepted')}
    approval.update(blocks=list(isolated.PCDSB_BLOCKS),allocation_regime=isolated.REGIME,
        full_size_phase_budgets_qualified=False,partial_full_count_budget_observed=False,
        OTel_remaining28_dispatch_GO=False,rollout_design_GO_sha256=isolated.PCDSB_DESIGN_SHA256,
        actual_resource_runs=[42267236483,42347353371,42347362261,42347366203],
        implementation_sha256=hashes)
    monkeypatch.setattr(b,'read',lambda *_:approval)
    monkeypatch.setattr(b,'implementation_hashes',lambda:hashes)
    monkeypatch.setattr(b,'gate',lambda *_:(_ for _ in ()).throw(ValueError('ordinary gate still closed')))
    for identity in isolated.PCDSB_BLOCKS:
        system,mode,repetition=identity.rsplit('-',2)
        isolated.gate(SimpleNamespace(system=system,mode=mode,repetition=int(repetition),stage='main'))
    args=SimpleNamespace(system='petclinic',mode='partial',repetition=9,stage='main')
    for key,value in [('blocks',approval['blocks']+['otel_demo-partial-9']),
            ('full_size_phase_budgets_qualified',True),('OTel_remaining28_dispatch_GO',True),
            ('partial_full_count_budget_observed',True),('partial_unknown_budget_risk_accepted',False),
            ('implementation_sha256',{}),('independent_original_GO',False),('actual_resource_runs',[])]:
        old=approval[key];approval[key]=value
        with pytest.raises(ValueError,match='remaining56'): isolated.gate(args)
        approval[key]=old
    for mode,repetition in [('partial',9),('absent',10),('full',11)]:
        expected = 'remaining8' if mode == 'full' else 'remaining20'
        with pytest.raises(ValueError,match=expected):
            isolated.gate(SimpleNamespace(system='otel_demo',mode=mode,repetition=repetition,stage='main'))


def test_complete_tar_census_checked_before_any_extraction(tmp_path):
    archive=tmp_path/'capture.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for name,body in [('expected',b'one'),('extra',b'two')]:
            member=tarfile.TarInfo(name);member.mode=0o600;member.size=len(body);tar.addfile(member,io.BytesIO(body))
    target=tmp_path/'target';target.mkdir()
    package={'bytes':archive.stat().st_size,'sha256':b.sha(archive),
             'files':{'expected':{'bytes':3,'sha256':hashlib.sha256(b'one').hexdigest(),'mode':0o600}},'directories':[]}
    with pytest.raises(ValueError,match='census'):
        b.unpack(archive,target,b.sha(archive),expected_inventory=package)
    assert not (target/'expected').exists()


@pytest.mark.parametrize('bad', [None, 'outer_SHA', 'member_CRC'])
def test_fixed_cloud_delivery_checks_whole_ZIP_and_original_member_CRC(tmp_path, monkeypatch, bad):
    memory=io.BytesIO()
    with zipfile.ZipFile(memory,'w',compression=zipfile.ZIP_STORED) as archive:
        archive.writestr('model.tar.gz',b'synthetic immutable package')
        archive.writestr('model.tar.gz.json',b'{}')
    data=memory.getvalue()
    if bad=='member_CRC':
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            info=archive.getinfo('model.tar.gz')
            offset=info.header_offset+30+len(info.filename.encode())+len(info.extra)
        mutable=bytearray(data);mutable[offset]^=1;data=bytes(mutable)
    digest=hashlib.sha256(data).hexdigest()
    api={'id':1,'name':'exact','size_in_bytes':len(data),'digest':'sha256:'+('0'*64 if bad=='outer_SHA' else digest)}
    monkeypatch.setenv('GITHUB_REPOSITORY','a-a-k/ebpf-model-discovery-experiments')
    monkeypatch.setenv('GH_TOKEN','synthetic-fixture')
    monkeypatch.setattr(isolated,'actual_artifact',lambda *_:api)
    monkeypatch.setattr(isolated.urllib.request,'build_opener',lambda *_:SimpleNamespace(open=lambda *_args,**_kw:io.BytesIO(data)))
    folder=tmp_path/'delivery'
    if bad:
        with pytest.raises((ValueError,zipfile.BadZipFile)):
            isolated.fetch({'id':1,'name':'exact','digest':api['digest']},folder,('model.tar.gz','model.tar.gz.json'))
    else:
        receipt=isolated.fetch({'id':1,'name':'exact','digest':api['digest']},folder,('model.tar.gz','model.tar.gz.json'))
        assert receipt['all_members_EOF_CRC_verified'] is True
        assert (folder/'model.tar.gz').read_bytes()==b'synthetic immutable package'
        isolated.release_delivery(receipt)
        assert not (folder/'delivery.zip').exists()


def test_workflow_direct_ids_all_four_model_dependencies_and_unlimited_standard_jobs():
    workflow=Path(__file__).resolve().parents[1]/'.github/workflows/series-isolated-v6.yml'
    jobs=yaml.safe_load(workflow.read_text(encoding='utf8'))['jobs']
    assert len(jobs)==13
    for key,job in jobs.items():
        assert job['runs-on']=='ubuntu-24.04' and job['timeout-minutes']==360
        assert 'strategy' not in job
        if key.startswith('validation'):
            assert job['needs']==['prepare','model0','model1','model2','model3']
        if key.startswith('model'):
            assert job['needs']=='training'+key[-1]
        if key!='prepare':
            assert 'artifact-id' in job['outputs']['artifact_id']
    assert 'series-isolated-v6.yml' in (workflow.parents[2]/'src/ebpf_discovery/block_v6.py').read_text(encoding='utf8')


def test_OTel_twenty_require_their_own_source_approval_and_separate_full_approval(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    hashes = {'exact_source': 'bound'}
    approval = {k: True for k in ('original_source_execution_GO', 'root_original_GO',
        'independent_original_GO', 'original_scientific_rollout_GO',
        'original108_scope_retained', 'partial_unknown_budget_risk_accepted')}
    approval.update(blocks=list(isolated.OTEL_STAGED_BLOCKS), allocation_regime=isolated.REGIME,
        full_size_phase_budgets_qualified=False, partial_full_count_budget_observed=False,
        OTel_remaining_full8_dispatch_GO=False, rollout_design_GO_sha256=isolated.OTEL_STAGED_DESIGN_SHA256,
        actual_resource_runs=[42347357851], implementation_sha256=hashes)
    monkeypatch.setattr(b, 'read', lambda *_: approval)
    monkeypatch.setattr(b, 'implementation_hashes', lambda: hashes)
    monkeypatch.setattr(b, 'gate', lambda *_: (_ for _ in ()).throw(ValueError('ordinary gate remains closed')))
    for identity in isolated.OTEL_STAGED_BLOCKS:
        system, mode, repetition = identity.rsplit('-', 2)
        isolated.gate(SimpleNamespace(system=system, mode=mode, repetition=int(repetition), stage='main'))
    args = SimpleNamespace(system='otel_demo', mode='partial', repetition=9, stage='main')
    for key, value in [('blocks', approval['blocks'] + ['otel_demo-full-10']),
            ('full_size_phase_budgets_qualified', True), ('OTel_remaining_full8_dispatch_GO', True),
            ('partial_full_count_budget_observed', True), ('partial_unknown_budget_risk_accepted', False),
            ('implementation_sha256', {}), ('independent_original_GO', False), ('actual_resource_runs', [])]:
        old = approval[key]; approval[key] = value
        with pytest.raises(ValueError, match='remaining20'):
            isolated.gate(args)
        approval[key] = old
    for repetition in (10, 11):
        with pytest.raises(ValueError, match='remaining8'):
            isolated.gate(SimpleNamespace(system='otel_demo', mode='full', repetition=repetition, stage='main'))


def test_OTel_last8_cannot_run_without_all_four_published_models_and_own_review(monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    hashes = {'exact_final_source': 'bound'}
    approval = {k: True for k in ('original_source_execution_GO', 'root_original_GO',
        'independent_original_GO', 'original_scientific_rollout_GO', 'original108_scope_retained',
        'all_four_GC25_full9_model_publications_verified', 'actual_model_resource_review_GO',
        'full_validation_unknown_budget_risk_accepted', 'full9_first_validation_required_and_retained')}
    approval.update(blocks=list(isolated.OTEL_FINAL_BLOCKS), allocation_regime=isolated.REGIME,
        full_size_phase_budgets_qualified=False, full_validation_budget_observed=False,
        rollout_design_GO_sha256=isolated.OTEL_FINAL_DESIGN_SHA256, actual_resource_runs=[42402184737],
        bering_child_go_environment={'GOGC': '25'}, additional_model_swap_file_bytes=16*1024**3,
        model_swap_design_GO_sha256='3d91a5c64cc8a74a2c0cb71409094e339d7fa577bd0ef46835e6058d010c1c33',
        implementation_sha256=hashes)
    monkeypatch.setattr(b, 'read', lambda *_: approval)
    monkeypatch.setattr(b, 'implementation_hashes', lambda: hashes)
    for repetition in (10, 11):
        isolated.gate(SimpleNamespace(system='otel_demo', mode='full', repetition=repetition, stage='main'))
    args = SimpleNamespace(system='otel_demo', mode='full', repetition=10, stage='main')
    for key, value in [('blocks', approval['blocks'] + ['otel_demo-partial-9']),
            ('all_four_GC25_full9_model_publications_verified', False),
            ('actual_model_resource_review_GO', False), ('full_validation_unknown_budget_risk_accepted', False),
            ('full9_first_validation_required_and_retained', False), ('full_size_phase_budgets_qualified', True),
            ('full_validation_budget_observed', True), ('bering_child_go_environment', {}),
            ('additional_model_swap_file_bytes', 0), ('model_swap_design_GO_sha256', '0'*64),
            ('actual_resource_runs', []), ('independent_original_GO', False), ('implementation_sha256', {})]:
        old = approval[key]; approval[key] = value
        with pytest.raises(ValueError, match='remaining8'):
            isolated.gate(args)
        approval[key] = old
