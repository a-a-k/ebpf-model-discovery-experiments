"""Reject incomplete or misattributed closed-job evidence without scientific runs."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location(
    'closed_postcapture_saved_review', ROOT/'scripts/review-main-saved-facts-v5.py')
REVIEW = importlib.util.module_from_spec(spec)
spec.loader.exec_module(REVIEW)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def fixture(root, *, identity_override=None):
    identity = {'run_id': '99', 'commit': REVIEW.CLOSED_POSTCAPTURE_HEAD,
        'system': 'otel_demo', 'collector': 'deepflow', 'controller': 'clean-study',
        'mode': 'absent', 'seed': 6, 'smoke': False}
    identity.update(identity_override or {})
    declaration = {**identity, 'head_sha': identity['commit'], 'run_id': int(identity['run_id'])}
    captured = {**identity, 'status': 'postcapture_complete'}
    write(root/'status.json', captured)
    for name, body in {'observation-index.sqlite': b'pre-mutation SQL',
            'attempt-journal.sqlite': b'pre-mutation journal',
            'attempt-journal.jsonl': b'pre-mutation journal export',
            'plans.json': b'{"operation": "unchanged"}',
            'toolchain/discovery/model.json': b'{"frozen": true}'}.items():
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    rows = [{'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
             'mode': 0o644, 'sha256': REVIEW.sha(path)}
            for path in sorted(root.rglob('*')) if path.is_file()]
    frozen = {'sha256_by_path': {'toolchain/discovery/model.json':
                               REVIEW.sha(root/'toolchain/discovery/model.json')}}
    folder = root/'infrastructure/postcapture'
    folder.mkdir(parents=True)
    (folder/'files.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows))
    write(folder/'capture-status.json', captured)
    sql = {'proof_basis': 'rowid-and-all-columns-v1', 'schema_sha256': '1'*64,
           'spans': {'rows': 1, 'sha256': '2'*64}}
    marker = {'schema': 'closed-otel-postcapture-v5', 'identity': identity,
        'sealing_run_id': identity['run_id'], 'sealing_source': identity['commit'],
        'scientific_root': '/original/work/campaign',
        'directories': {'toolchain': 0o755, 'toolchain/discovery': 0o755},
        'files': len(rows), 'file_bytes': sum(row['bytes'] for row in rows),
        'file_inventory_sha256': REVIEW.sha(folder/'files.jsonl'),
        'capture_status_sha256': REVIEW.sha(folder/'capture-status.json'),
        'frozen_file_count': 1, 'training_SQL': sql,
        'journal_events': 1, 'journal_max_seq': 1,
        'journal_sha256': REVIEW.sha(root/'attempt-journal.sqlite'),
        'index_bytes': (root/'observation-index.sqlite').stat().st_size,
        'acquisition_closure': {'unresolved_transports': 0,
            'completeness': {'valid': True}, 'acquisition': {'valid': True}}}
    write(folder/'closed.json', marker)
    processing = {'identity': identity, 'status': 'complete', 'offline_only': True,
        'traffic_replay_or_model_refit': False, 'processing_run_id': identity['run_id'],
        'processing_source': identity['commit'],
        'closed_manifest_sha256': REVIEW.sha(folder/'closed.json'),
        'input_file_inventory_sha256': marker['file_inventory_sha256']}
    write(folder/'processing.json', processing)
    artifact = {'id': 777, 'name': f"postcapture-v5-deepflow-main-otel_demo-{identity['mode']}-{identity['seed']}-{identity['run_id']}",
        'expired': False, 'size_in_bytes': 100, 'digest': 'sha256:'+'3'*64,
        'workflow_run': {'id': int(identity['run_id']), 'head_sha': identity['commit']}}
    write(folder/'artifact-api.json', artifact)
    host = root/'infrastructure/postcapture-host'
    guard = {'archive_bytes': 100, 'scientific_file_bytes': marker['file_bytes'],
        'proof_bytes': sum((folder/name).stat().st_size for name in
            ('closed.json', 'capture-status.json', 'files.jsonl')),
        'SQL_WAL_growth_reserve_bytes': 4*marker['index_bytes'],
        'scientific_limit_or_filter': False}
    guard['required_bytes'] = sum(guard[k] for k in ('archive_bytes',
        'scientific_file_bytes', 'proof_bytes', 'SQL_WAL_growth_reserve_bytes'))+1024**3
    guard['available_bytes'] = guard['required_bytes']+1
    write(host/'disk-before-download.json', guard)
    write(host/'restore.json', {'status': 'complete', 'artifact_id': 777,
        'artifact_digest': artifact['digest'], 'archive_bytes': 100,
        'archive_sha256': '3'*64, 'all_original_members_read_to_EOF_and_CRC_checked': True,
        'closed_manifest_sha256': processing['closed_manifest_sha256']})
    write(root/'infrastructure/guest-evidence-capture.json',
          {'campaign_root': marker['scientific_root']})
    remote = root/'infrastructure/remote-toolchain-v4'
    write(remote/'worker/output-manifest.json', {'toolchain_files': {}})
    parent = {'identity': {k: identity[k] for k in ('run_id', 'commit', 'system', 'mode', 'seed')},
        'worker_run_id': 888, 'worker_artifact_id': 999,
        'worker_artifact_digest': 'sha256:'+'4'*64, 'downloaded_archive_sha256': '4'*64}
    parent['identity']['manifest_sha256'] = '5'*64
    linked = {'schema_version': 'closed-discovery-import-hardlinks-v1',
        'identity': parent['identity'], 'immutable_subtree': 'toolchain/discovery/',
        'all_original_members_read_to_EOF': True,
        'output_manifest_sha256': REVIEW.sha(remote/'worker/output-manifest.json'),
        'worker_run_id': 888, 'worker_artifact_id': 999,
        'worker_artifact_digest': parent['worker_artifact_digest'],
        'archive_sha256': parent['downloaded_archive_sha256'],
        'linked_files': 0, 'duplicate_bytes_not_allocated': 0}
    write(remote/'closed-discovery-import-hardlinks.json', linked)
    # Final mutable bytes legitimately differ from the sealed pre-mutation state.
    write(root/'status.json', {**captured, 'status': 'acquisition_complete'})
    (root/'observation-index.sqlite').write_bytes(b'final SQL after ingest and refresh')
    (root/'attempt-journal.sqlite').write_bytes(b'final journal file')
    selected = {'artifact': {'name': f"campaign-v5-deepflow-main-otel_demo-{identity['mode']}-{identity['seed']}-{identity['run_id']}"},
        'files': {name: {'bytes': (root/name).stat().st_size, 'sha256': REVIEW.sha(root/name)}
                  for name in ('status.json', 'plans.json', 'observation-index.sqlite')}}
    write(root/'evaluation-manifest.json', {'run_id': identity['run_id'], 'commit': identity['commit'],
        'full_artifact_name': selected['artifact']['name'],
        'files_sha256': {'status.json': REVIEW.sha(root/'status.json')}})
    worker = {'parent_import': parent, 'output_manifest': {},
              'training_index_proof': {'parent_after_worker': sql}}
    return declaration, frozen, worker, selected


@pytest.mark.parametrize('mutation', ['none', 'foreign_capture', 'foreign_artifact',
    'processing_source', 'open_transport', 'wrong_SQL', 'duplicate_inventory',
    'frozen_claim', 'selected_immutable', 'qualified_publication', 'missing_restore',
    'restore_digest', 'guard_smallhost', 'worker_manifest', 'full6_replay', 'foreign_collector',
    'SQL_size_claim', 'proof_size_claim'])
def test_closed_job_requires_complete_same_source_chain_and_preserves_mutable_state(tmp_path, mutation):
    declaration, frozen, worker, selected = fixture(tmp_path)
    folder = tmp_path/'infrastructure/postcapture'
    target = None
    if mutation == 'foreign_capture': target, key, value = folder/'capture-status.json', 'commit', '0'*40
    if mutation == 'foreign_artifact':
        target, key, value = folder/'artifact-api.json', 'workflow_run', {'id': 100, 'head_sha': declaration['head_sha']}
    if mutation == 'processing_source': target, key, value = folder/'processing.json', 'processing_source', '0'*40
    if mutation == 'open_transport':
        target, key, value = folder/'closed.json', 'acquisition_closure', {
            'unresolved_transports': 1, 'completeness': {'valid': True}, 'acquisition': {'valid': True}}
    if mutation == 'qualified_publication': target, key, value = tmp_path/'evaluation-manifest.json', 'qualification_only', True
    if mutation == 'restore_digest': target, key, value = tmp_path/'infrastructure/postcapture-host/restore.json', 'archive_sha256', '0'*64
    if mutation == 'guard_smallhost':
        target = tmp_path/'infrastructure/postcapture-host/disk-before-download.json'
        key, value = 'available_bytes', 0
    if mutation == 'SQL_size_claim': target, key, value = folder/'closed.json', 'index_bytes', 1
    if mutation == 'proof_size_claim': target, key, value = tmp_path/'infrastructure/postcapture-host/disk-before-download.json', 'proof_bytes', 0
    if mutation == 'worker_manifest': target, key, value = tmp_path/'infrastructure/remote-toolchain-v4/closed-discovery-import-hardlinks.json', 'output_manifest_sha256', '0'*64
    if target:
        document = REVIEW.read(target); document[key] = value; write(target, document)
    if mutation == 'wrong_SQL':
        worker = copy.deepcopy(worker); worker['training_index_proof']['parent_after_worker']['spans']['rows'] = 2
    if mutation in ('duplicate_inventory', 'frozen_claim'):
        path = folder/'files.jsonl'; lines = path.read_text().splitlines()
        if mutation == 'duplicate_inventory': lines.append(lines[0])
        else:
            rows = [json.loads(line) for line in lines]
            next(row for row in rows if row['path'] in frozen['sha256_by_path'])['sha256'] = '0'*64
            lines = [json.dumps(row) for row in rows]
        path.write_text('\n'.join(lines)+'\n')
        marker = REVIEW.read(folder/'closed.json'); marker['file_inventory_sha256'] = REVIEW.sha(path)
        write(folder/'closed.json', marker)
        processing = REVIEW.read(folder/'processing.json')
        processing.update(closed_manifest_sha256=REVIEW.sha(folder/'closed.json'),
                          input_file_inventory_sha256=marker['file_inventory_sha256'])
        write(folder/'processing.json', processing)
        restored = REVIEW.read(tmp_path/'infrastructure/postcapture-host/restore.json')
        restored['closed_manifest_sha256'] = processing['closed_manifest_sha256']
        write(tmp_path/'infrastructure/postcapture-host/restore.json', restored)
    if mutation in ('open_transport', 'duplicate_inventory', 'frozen_claim', 'SQL_size_claim'):
        processing = REVIEW.read(folder/'processing.json')
        processing['closed_manifest_sha256'] = REVIEW.sha(folder/'closed.json')
        write(folder/'processing.json', processing)
        host = tmp_path/'infrastructure/postcapture-host'
        restored = REVIEW.read(host/'restore.json')
        restored['closed_manifest_sha256'] = processing['closed_manifest_sha256']
        write(host/'restore.json', restored)
        guard = REVIEW.read(host/'disk-before-download.json')
        guard['proof_bytes'] = sum((folder/name).stat().st_size for name in
            ('closed.json', 'capture-status.json', 'files.jsonl'))
        if mutation == 'SQL_size_claim': guard['SQL_WAL_growth_reserve_bytes'] = 4
        guard['required_bytes'] = sum(guard[k] for k in ('archive_bytes', 'scientific_file_bytes',
            'proof_bytes', 'SQL_WAL_growth_reserve_bytes'))+1024**3
        guard['available_bytes'] = guard['required_bytes']+1
        write(host/'disk-before-download.json', guard)
    if mutation == 'selected_immutable': selected['files']['plans.json']['sha256'] = '0'*64
    if mutation == 'missing_restore': (tmp_path/'infrastructure/postcapture-host/restore.json').unlink()
    if mutation == 'full6_replay': declaration.update(mode='full', seed=6)
    if mutation == 'foreign_collector': declaration['collector'] = 'coroot'
    if mutation == 'none':
        result = REVIEW.closed_postcapture_facts(tmp_path, declaration, frozen, worker, selected)
        assert result['closed_discovery_import']['linked_files'] == 0
        assert result['mutable_SQL_status_journal_not_compared_to_pre_mutation_file_bytes']
        assert result['all_frozen_claims_bound_to_pre_mutation_inventory']
        assert result['whole_case_memory_disk_headroom_or_six_hour_cure_proven'] is False
    else:
        with pytest.raises((ValueError, FileNotFoundError)):
            REVIEW.closed_postcapture_facts(tmp_path, declaration, frozen, worker, selected)


def recovery_fixture(root):
    profile = REVIEW.CLOSED_CAPTURE_RECOVERY_SOURCE
    original = profile['capture_identity']
    declaration, frozen, worker, selected = fixture(root, identity_override=original)
    declaration.update(run_id=profile['processing_run_id'], head_sha=profile['revision'],
        scientific_capture_run_id=int(original['run_id']), scientific_capture_head_sha=original['commit'])
    folder, host = root/'infrastructure/postcapture', root/'infrastructure/postcapture-host'
    artifact = {**profile['capture_artifact'], 'expired': False,
        'workflow_run': {'id': int(original['run_id']), 'head_sha': original['commit']}}
    write(folder/'artifact-api.json', artifact)
    processing = REVIEW.read(folder/'processing.json')
    processing.update(processing_run_id=str(declaration['run_id']), processing_source=profile['revision'])
    write(folder/'processing.json', processing)
    selected['artifact']['name'] = f"campaign-v5-deepflow-main-otel_demo-full-8-{declaration['run_id']}"
    summary = REVIEW.read(root/'evaluation-manifest.json')
    summary.update(run_id=str(declaration['run_id']), commit=profile['revision'],
        full_artifact_name=selected['artifact']['name'], scientific_capture_identity=original,
        closed_capture_recovery={'capture_run_id': original['run_id'], 'capture_source': original['commit'],
            'capture_artifact_id': artifact['id'], 'capture_artifact_digest': artifact['digest'],
            'processing_run_id': str(declaration['run_id']), 'processing_source': profile['revision'],
            'new_application_traffic': False, 'refit_models': False})
    write(root/'evaluation-manifest.json', summary)
    guard = REVIEW.read(host/'disk-before-download.json')
    guard.update(archive_bytes=artifact['size_in_bytes'], budget=profile['delivery_budget'])
    fixed = guard['scientific_file_bytes']+guard['proof_bytes']
    reserve = guard['SQL_WAL_growth_reserve_bytes']
    guard.update(download_restore_required_bytes=artifact['size_in_bytes']+fixed+1024**3,
        restored_processing_peak_bytes=fixed+reserve+1024**3)
    guard['required_bytes'] = max(guard['download_restore_required_bytes'], guard['restored_processing_peak_bytes'])
    guard['available_bytes'] = guard['required_bytes']+1
    write(host/'disk-before-download.json', guard)
    phase = {'required_bytes': reserve+1024**3, 'available_bytes': reserve+1024**3+1,
        'SQL_WAL_growth_reserve_bytes': reserve, 'scientific_limit_or_filter': False,
        'scientific_tree_already_restored': True, 'verified_delivery_removed': True}
    write(host/'disk-before-processing.json', phase)
    restored = REVIEW.read(host/'restore.json')
    owned = {'device': 1, 'inode': 22, 'type': 0o100000, 'bytes': artifact['size_in_bytes']}
    restored.update(artifact_id=artifact['id'], artifact_digest=artifact['digest'],
        archive_bytes=artifact['size_in_bytes'], archive_sha256=artifact['digest'][7:],
        capture_run_id=original['run_id'], capture_source=original['commit'],
        processing_run_id=str(declaration['run_id']), processing_source=profile['revision'],
        verified_delivery_identity=owned,
        delivery_working_copy={'path': '/original/work/closed-postcapture.zip',
            'bytes': artifact['size_in_bytes'], 'sha256': artifact['digest'][7:],
            'disposition': 'verified_then_removed_owned_delivery',
            'removed_after_all_restore_checks': True, 'verified_file_identity': dict(owned),
            'recorded_ns': 123, 'free_before': 0, 'free_after': phase['available_bytes']})
    write(host/'restore.json', restored)
    return declaration, frozen, worker, selected


@pytest.mark.parametrize('mutation', ['none', 'original_identity', 'publication_run', 'capsule',
    'restore_capture_source', 'processing_identity', 'legacy_budget', 'second_guard',
    'reserve_reduction', 'inode_replaced', 'symlink_type', 'scientific_path_deletion',
    'qualification', 'refit_claim'])
def test_recovered_full8_requires_both_identities_and_owned_delivery_guards(tmp_path, mutation):
    declaration, frozen, worker, selected = recovery_fixture(tmp_path)
    folder, host = tmp_path/'infrastructure/postcapture', tmp_path/'infrastructure/postcapture-host'
    if mutation == 'original_identity':
        path = tmp_path/'evaluation-manifest.json'; value = REVIEW.read(path)
        value['scientific_capture_identity']['run_id'] = '100'; write(path, value)
    if mutation == 'publication_run': declaration['run_id'] += 1
    if mutation == 'capsule':
        path = folder/'artifact-api.json'; value = REVIEW.read(path); value['id'] += 1; write(path, value)
    if mutation == 'restore_capture_source':
        path = host/'restore.json'; value = REVIEW.read(path); value['capture_source'] = declaration['head_sha']; write(path, value)
    if mutation == 'processing_identity':
        path = folder/'processing.json'; value = REVIEW.read(path); value['processing_run_id'] = '41642796796'; write(path, value)
    if mutation == 'legacy_budget':
        path = host/'disk-before-download.json'; value = REVIEW.read(path)
        value['required_bytes'] = sum(value[k] for k in ('archive_bytes', 'scientific_file_bytes',
            'proof_bytes', 'SQL_WAL_growth_reserve_bytes'))+1024**3
        value['available_bytes'] = value['required_bytes']+1; write(path, value)
    if mutation in ('second_guard', 'reserve_reduction'):
        path = host/'disk-before-processing.json'; value = REVIEW.read(path)
        if mutation == 'second_guard': value['available_bytes'] = 0
        else: value['SQL_WAL_growth_reserve_bytes'] = 1
        write(path, value)
    if mutation in ('inode_replaced', 'symlink_type', 'scientific_path_deletion'):
        path = host/'restore.json'; value = REVIEW.read(path)
        if mutation == 'inode_replaced': value['delivery_working_copy']['verified_file_identity']['inode'] += 1
        if mutation == 'symlink_type':
            value['verified_delivery_identity']['type'] = 0o120000
            value['delivery_working_copy']['verified_file_identity']['type'] = 0o120000
        if mutation == 'scientific_path_deletion': value['delivery_working_copy']['path'] = '/original/work/campaign/observation-index.sqlite'
        write(path, value)
    if mutation in ('qualification', 'refit_claim'):
        path = tmp_path/'evaluation-manifest.json'; value = REVIEW.read(path)
        if mutation == 'qualification': value['qualification_only'] = True
        else: value['closed_capture_recovery']['refit_models'] = True
        write(path, value)
    if mutation == 'none':
        result = REVIEW.closed_postcapture_facts(tmp_path, declaration, frozen, worker, selected)
        assert result['processing']['processing_run_id'] == str(declaration['run_id'])
        assert result['capture_status']['run_id'] == '41642796796'
        assert result['mutable_SQL_status_journal_not_compared_to_pre_mutation_file_bytes']
    else:
        with pytest.raises(ValueError):
            REVIEW.closed_postcapture_facts(tmp_path, declaration, frozen, worker, selected)


def union_api_fixture(profile=None):
    p = profile or REVIEW.CLOSED_CAPTURE_COMPACT_UNION
    expected = {
        6: ('Restore the exact closed capture after the actual disk guard','success'),
        7: ('Verify all closed inputs and run the unchanged offline suffix','success'),
        9: ('Evaluate retained full campaign evidence','success'),
        10: ('Record compact evaluation provenance','success'),
        11: ('Run actions/upload-artifact@v4','success'),
        12: ('Run actions/upload-artifact@v4','failure'),
        13: ('Retain the compact postcapture processing diagnostics','success')}
    artifacts = [{**a,'expired':False,'workflow_run':{
        'id':REVIEW._closed_union_artifact_origin(p,kind)[0],
        'head_sha':REVIEW._closed_union_artifact_origin(p,kind)[1]}}
        for kind,a in p['artifacts'].items()]
    return {'run':{'id':p['run_id'],'head_sha':p['head_sha'],
                'path':p.get('workflow_path','.github/workflows/series-v5.yml'),'status':'completed','conclusion':'failure'},
        'job':{'id':p['processing_job'],'run_id':p['run_id'],'status':'completed','conclusion':'failure',
               'steps':[{'number':n,'name':name,'status':'completed','conclusion':c}
                        for n,(name,c) in expected.items()]},
        'capture_job':{'id':p['capture_job'],'run_id':p.get('capture_run_id',p['run_id']),
            'head_sha':p.get('capture_head_sha',p['head_sha']),'status':'completed','conclusion':'success'},
        'artifacts':artifacts}


@pytest.mark.parametrize('mutation',['none','foreign_run','failed_suffix','missing_compact',
    'existing_full','duplicate_step','foreign_capture','expired_restore','changed_digest'])
def test_closed_union_requires_actual_named_source_and_publication_chain(mutation):
    body=union_api_fixture()
    if mutation=='foreign_run':body['run']['head_sha']='0'*40
    if mutation=='failed_suffix':body['job']['steps'][1]['conclusion']='failure'
    if mutation=='missing_compact':body['artifacts'].pop(1)
    if mutation=='existing_full':body['artifacts'].append({'name':'campaign-v5-deepflow-main-otel_demo-partial-7-41642781338'})
    if mutation=='duplicate_step':body['job']['steps'].append(body['job']['steps'][0])
    if mutation=='foreign_capture':body['capture_job']['run_id']=123
    if mutation=='expired_restore':body['artifacts'][2]['expired']=True
    if mutation=='changed_digest':body['artifacts'][0]['digest']='sha256:'+'0'*64
    if mutation!='none':
        with pytest.raises(ValueError):REVIEW._closed_union_api_facts(body)
    else:
        facts=REVIEW._closed_union_api_facts(body)
        assert not facts['independent_scientific_admission']
        assert 'final_mutable_SQL' in facts['unavailable']


@pytest.mark.parametrize('mutation',['none','missing_restore','changed_metadata','wrong_namespace',
    'wrong_frozen_model','failed_suffix','foreign_declaration','missing_status','foreign_known_chain'])
@pytest.mark.parametrize('union_run',[41642781338,41642775376,41642789738])
def test_closed_union_preserves_scientific_predicates_without_fabricated_full_receipt(tmp_path,mutation,union_run):
    import shutil
    p=REVIEW.CLOSED_CAPTURE_COMPACT_UNIONS[union_run]
    root=tmp_path/'capsule'; compact=tmp_path/'compact'; host=tmp_path/'restore'
    declaration,frozen,worker,selected=fixture(root,identity_override={
        'run_id':str(p['run_id']),'commit':p['head_sha'],'mode':'partial','seed':p['cell'][3]})
    declaration.update(evidence_layout=p['layout'],compact_artifact_name=p['artifacts']['compact']['name'])
    compact.mkdir();host.mkdir()
    for name in ('status.json','evaluation-manifest.json'):
        shutil.copyfile(root/name,compact/name)
        (root/name).unlink()
    folder=root/'infrastructure/postcapture'
    (folder/'processing.json').unlink()
    artifact={**p['artifacts']['capture'],'expired':False,
        'workflow_run':{'id':p['run_id'],'head_sha':p['head_sha']}}
    write(host/'artifact-api.json',artifact)
    for name in ('restore.json','disk-before-download.json'):
        shutil.copyfile(root/'infrastructure/postcapture-host'/name,host/name)
    marker=REVIEW.read(folder/'closed.json')
    guard=REVIEW.read(host/'disk-before-download.json')
    guard['archive_bytes']=artifact['size_in_bytes']
    guard['required_bytes']=sum(guard[k] for k in ('archive_bytes','scientific_file_bytes','proof_bytes','SQL_WAL_growth_reserve_bytes'))+1024**3
    guard['available_bytes']=guard['required_bytes']+1
    write(host/'disk-before-download.json',guard)
    write(host/'restore.json',{'status':'complete','artifact_id':artifact['id'],
        'artifact_digest':artifact['digest'],'archive_bytes':artifact['size_in_bytes'],
        'archive_sha256':artifact['digest'][7:],
        'all_original_members_read_to_EOF_and_CRC_checked':True,
        'closed_manifest_sha256':REVIEW.sha(folder/'closed.json')})
    diag={'complete':True,'scope':'restore-diagnostics','scientific_processing_performed':False,
        'artifact':{**p['artifacts']['restore'],'expired':False,
            'workflow_run':{'id':p['run_id'],'head_sha':p['head_sha']}},
        'files':{f.name:{'bytes':f.stat().st_size,'sha256':REVIEW.sha(f)} for f in host.iterdir()}}
    write(host/'selected-transport-proof.json',diag)
    actual=tmp_path/'actual.json';write(actual,union_api_fixture(p))
    selected['artifact']=artifact
    selected['files'].pop('status.json')
    selected['closed_capture_namespace']={'scientific_file_bytes':marker['file_bytes'],
        'scientific_files':marker['files'],'proof_bytes':guard['proof_bytes'],'processed_full_snapshot':False}
    if mutation=='missing_restore':(host/'restore.json').unlink()
    if mutation=='changed_metadata':write(host/'disk-before-download.json',{})
    if mutation=='wrong_namespace':selected['closed_capture_namespace']['scientific_files']+=1
    if mutation=='wrong_frozen_model':frozen['sha256_by_path']['toolchain/discovery/model.json']='0'*64
    if mutation=='foreign_known_chain':
        other=next(v for k,v in REVIEW.CLOSED_CAPTURE_COMPACT_UNIONS.items() if k!=union_run)
        write(actual,union_api_fixture(other))
    if mutation=='failed_suffix':
        body=REVIEW.read(actual);body['job']['steps'][1]['conclusion']='failure';write(actual,body)
    if mutation=='foreign_declaration':declaration['seed']=9
    if mutation=='missing_status':(compact/'status.json').unlink()
    invoke=lambda:REVIEW.closed_postcapture_facts(root,declaration,frozen,worker,selected,
        compact=compact,restore_root=host,actual_processing=actual)
    if mutation!='none':
        with pytest.raises((ValueError,FileNotFoundError)):invoke()
    else:
        facts=invoke()
        assert facts['processing'] is None
        assert facts['scientific_packet_layout']==p['layout']
        assert 'final_mutable_SQL' in facts['unavailable_processed_full_components']


@pytest.mark.parametrize('mutation',['none','capture_as_processing','foreign_api_chain','missing_phase_guard','missing_original_identity'])
def test_full8_union_retains_both_original_and_actual_processing_identity(tmp_path,mutation):
    import shutil
    p=REVIEW.CLOSED_CAPTURE_COMPACT_UNIONS[41706823165]
    root=tmp_path/'capsule';compact=tmp_path/'compact';host=tmp_path/'restore'
    declaration,frozen,worker,selected=recovery_fixture(root)
    declaration.update(evidence_layout=p['layout'],compact_artifact_name=p['artifacts']['compact']['name'])
    compact.mkdir();host.mkdir()
    for name in ('status.json','evaluation-manifest.json'):
        shutil.copyfile(root/name,compact/name);(root/name).unlink()
    folder=root/'infrastructure/postcapture';(folder/'processing.json').unlink()
    for f in (root/'infrastructure/postcapture-host').iterdir():
        if f.is_file():shutil.copyfile(f,host/f.name)
    artifact={**p['artifacts']['capture'],'expired':False,
        'workflow_run':{'id':p['capture_run_id'],'head_sha':p['capture_head_sha']}}
    write(host/'artifact-api.json',artifact)
    write(host/'selected-transport-proof.json',{'complete':True,'scope':'restore-diagnostics',
        'scientific_processing_performed':False,'artifact':{**p['artifacts']['restore'],'expired':False,
        'workflow_run':{'id':p['run_id'],'head_sha':p['head_sha']}},
        'files':{f.name:{'bytes':f.stat().st_size,'sha256':REVIEW.sha(f)} for f in host.iterdir()}})
    marker=REVIEW.read(folder/'closed.json');guard=REVIEW.read(host/'disk-before-download.json')
    selected['artifact']=artifact;selected['files'].pop('status.json')
    selected['closed_capture_namespace']={'scientific_file_bytes':marker['file_bytes'],'scientific_files':marker['files'],
        'proof_bytes':guard['proof_bytes'],'processed_full_snapshot':False}
    actual=tmp_path/'actual.json';body=union_api_fixture(p)
    if mutation=='capture_as_processing':body['artifacts'][0]['workflow_run']['id']=p['run_id']
    if mutation=='foreign_api_chain':body=union_api_fixture()
    if mutation=='missing_phase_guard':(host/'disk-before-processing.json').unlink()
    if mutation=='missing_original_identity':declaration.pop('scientific_capture_run_id')
    write(actual,body)
    call=lambda:REVIEW.closed_postcapture_facts(root,declaration,frozen,worker,selected,
        compact=compact,restore_root=host,actual_processing=actual)
    if mutation!='none':
        with pytest.raises((ValueError,FileNotFoundError)):call()
    else:
        result=call()
        assert result['processing'] is None
        assert result['capture_status']['run_id']==str(p['capture_run_id'])
        assert result['processing_completion_evidence']['run_id']==p['run_id']
        assert result['actual_restore']['processing_run_id']==str(p['run_id'])
