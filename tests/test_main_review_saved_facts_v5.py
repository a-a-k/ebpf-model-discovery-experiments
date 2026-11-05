from __future__ import annotations

import hashlib
import importlib.util
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import textwrap

import pytest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest


ROOT = Path(__file__).parents[1]


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


REVIEW = load("review_main_saved_facts_v5", "scripts/review-main-saved-facts-v5.py")
SELECT = load("select_main_review_evidence_v5", "scripts/select-main-review-evidence-v5.py")


@pytest.fixture
def upload_hold_packet(tmp_path):
    root = tmp_path
    remote = root/'infrastructure/remote-toolchain-v4'
    canonical = lambda value: hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    identity = {'run_id':'123', 'commit':REVIEW.UPLOAD_HOLD_PARENT_PROOF_HEAD,
                'system':'otel_demo', 'mode':'absent', 'seed':6, 'manifest_sha256':'a'*64}
    declaration = {'run_id':123,'head_sha':identity['commit'],'collector':'deepflow',
                   'system':'otel_demo','mode':'absent','seed':6}
    logical = {'proof_basis':'rowid-and-all-columns-v1','spans':{'rows':1,'sha256':'e'*64}}
    proof = {'manifest_sha256':'a'*64, 'files':{'plans.json':{'bytes':2,'sha256':'f'*64}}}
    preflight = {'schema_version':'upload-hold-parent-preflight-v1','status':'complete',
        'identity':identity,'started_ns':25,'ended_ns':70,'plans_sha256':'b'*64,
        'checkpoint_proof_sha256':canonical(proof),'verified_files':1,
        'complete_original_checkpoint_proof_executed':True,
        'training_index_proof_sha256':canonical(logical)}
    def write(relative, value):
        path = root/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value)+'\n',encoding='utf-8')
        return path
    prefix = 'infrastructure/remote-toolchain-v4/'
    preflight_path = write(prefix+'upload-hold-preflight.json',preflight)
    digest = hashlib.sha256(preflight_path.read_bytes()).hexdigest()
    write(prefix+'parent-proof-schedule.json',{'schema_version':'upload-hold-parent-proof-schedule-v1',
        'status':'complete','identity':identity,'worker_run_id':456,'confirmed_dispatch_ns':110,
        'parent_proof_started_ns':120,'parent_proof_ended_ns':150,
        'training_index_proof_sha256':canonical(logical),'upload_hold_preflight_sha256':digest,
        'phase':'parent_after_dispatch_before_import','all_checks_before_import_or_target':True})
    write(prefix+'dispatch.json',{'status':'dispatched','worker_run_id':456,
        'post_started_ns':100,'dispatched_ns':110,'checkpoint_proof':proof,
        'inputs':{**{k:str(v) for k,v in identity.items()},'plans_sha256':'b'*64,
                  'training_index_proof_sha256':canonical(logical)}})
    write(prefix+'cost.json',{'worker_run_id':456,'upload_hold_preflight_sha256':digest,
        'checkpoint_validation_includes_checkpoint_copy_release':False,
        'parent_after_dispatch_proof_seconds':30/1e9})
    write('training-checkpoint-cost.json',{'ready':True,'upload_success':True,
        'ready_callback_started_ns':20,'ready_callback_ended_ns':80,'ended_ns':90,
        'ready_callback_seconds':60/1e9,'upload_hold_wall_seconds':100/1e9})
    write('infrastructure/training-checkpoint/ready.json',{**identity,'created_ns':10})
    # Upload legitimately finishes before the callback; the HOLD ends afterward.
    write('infrastructure/training-checkpoint/release.json',{
        **identity,'released_ns':55,'upload_success':True})
    index = {'checkpoint':logical,'parent_after_dispatch_before_import':logical,'parent_after_worker':logical}
    provenance = {'worker_run_id':456,'plans_sha256':'b'*64,'training_index_proof':logical,
                  'checkpoint_input':proof}
    imported = {'identity':identity,'worker_run_id':456,'plans_sha256':'b'*64,'imported_ns':200}
    return root,remote,declaration,index,provenance,imported,{'saved_ns':220}


def test_upload_hold_full_proof_order_accepts_callback_finishing_after_upload(upload_hold_packet):
    facts = REVIEW.upload_hold_parent_proof_facts(*upload_hold_packet)
    assert facts['verified_files'] == 1 and facts['worker_run_id'] == 456
    assert facts['same_parent_clock_order_ns'] == sorted(facts['same_parent_clock_order_ns'])
    assert facts['whole_case_speedup_or_six_hour_guarantee_claimed'] is False


@pytest.mark.parametrize('file,key,value', [
    ('upload-hold-preflight.json','status','failed'),
    ('upload-hold-preflight.json','checkpoint_proof_sha256','0'*64),
    ('upload-hold-preflight.json','verified_files',2),
    ('upload-hold-preflight.json','complete_original_checkpoint_proof_executed',False),
    ('parent-proof-schedule.json','status','failed'),
    ('parent-proof-schedule.json','worker_run_id',999),
    ('parent-proof-schedule.json','confirmed_dispatch_ns',109),
    ('parent-proof-schedule.json','parent_proof_started_ns',99),
    ('parent-proof-schedule.json','parent_proof_ended_ns',201),
    ('parent-proof-schedule.json','phase','parent_before_dispatch'),
    ('parent-proof-schedule.json','upload_hold_preflight_sha256','0'*64),
    ('dispatch.json','checkpoint_proof',{'manifest_sha256':'a'*64,'files':{'other':{}}}),
    ('dispatch.json','post_started_ns',60),
    ('cost.json','parent_after_dispatch_proof_seconds',-1),
    ('cost.json','checkpoint_validation_includes_checkpoint_copy_release',True)])
def test_upload_hold_rejects_incomplete_changed_or_mistimed_actual_proofs(upload_hold_packet,file,key,value):
    path = upload_hold_packet[1]/file
    data = json.loads(path.read_text())
    data[key] = value
    path.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError):
        REVIEW.upload_hold_parent_proof_facts(*upload_hold_packet)


def test_upload_hold_never_accepts_a_legacy_phase_label(upload_hold_packet):
    index = upload_hold_packet[3]
    index['parent_before_dispatch'] = index['checkpoint']
    with pytest.raises(ValueError):
        REVIEW.upload_hold_parent_proof_facts(*upload_hold_packet)


def test_upload_hold_requires_the_unchanged_worker_SQL_proof(upload_hold_packet):
    upload_hold_packet[4]['training_index_proof'] = {'spans':{'rows':2}}
    with pytest.raises(ValueError):
        REVIEW.upload_hold_parent_proof_facts(*upload_hold_packet)


def test_upload_hold_requires_the_independently_verified_worker_full_census(upload_hold_packet):
    upload_hold_packet[4]['checkpoint_input'] = {'manifest_sha256':'a'*64,
                                               'files':{'foreign.json':{'bytes':2,'sha256':'f'*64}}}
    with pytest.raises(ValueError):
        REVIEW.upload_hold_parent_proof_facts(*upload_hold_packet)


def test_upload_hold_scope_excludes_running_seed7(upload_hold_packet):
    upload_hold_packet[2]['seed'] = 7
    with pytest.raises(ValueError,match='absent6/8'):
        REVIEW.upload_hold_parent_proof_facts(*upload_hold_packet)


def test_old_sources_do_not_acquire_new_receipt_requirements(tmp_path):
    assert REVIEW.upload_hold_parent_proof_facts(tmp_path,tmp_path,
        {'head_sha':REVIEW.IDENTICAL_INPUT_DISCOVERY_SOURCE['revision']},{},{},{},{}) is None


def _shared_discovery_fixture(root, monkeypatch):
    monkeypatch.setattr(REVIEW, 'IDENTICAL_INPUT_DISCOVERY_HEADS', {'shared-fixture'})
    toolchain = root/'toolchain'
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value)+'\n', encoding='utf-8')
    def claim(relative):
        path = toolchain/relative
        return {'path':'/original/campaign/toolchain/'+relative, 'bytes':path.stat().st_size,
                'sha256':REVIEW.sha(path)}
    origin = 'discovery/ebpf/raw'
    aliases = root/'runtime-identity-v5/supplied-service-aliases-training.json'
    admission = aliases.with_name('supplied-service-alias-admission-training.json')
    write(aliases, {}); write(admission, {'aliases':{}})
    binary = {'name':'bering', 'binary':'/original/campaign/toolchain-build/bin/bering',
              'binary_sha256':'b'*64}
    invocation = {'binary':binary['binary'], 'binary_sha256':binary['binary_sha256'],
        'source_profile':{'source_id':'ebpf','input_type':'ebpf-otlp'},
        'source_domain':'otel_demo-deployment','publication_mode':'on_shutdown',
        'clock_admission_filter':False,'go_runtime_environment':{'synthetic':True},
        'alias_table_sha256':REVIEW.sha(aliases), 'alias_admission_sha256':REVIEW.sha(admission)}
    replay = {**invocation, 'ended_ns':10, 'argv':[binary['binary']],
              'status':'complete','returncode':0}
    files = ['observed.json','observed.signal-quality.json','observed.snapshot.json',
             'observed.bering-raw.json','observed.bering-raw.signal-quality.json',
             'observed.supplied-aliases.json','observed-runtime/replay-command.json',
             'observed-runtime/serve.yaml','observed-runtime/accepted-request-sequence.jsonl']
    for name in files:
        write(toolchain/origin/name, replay if name.endswith('replay-command.json') else {'synthetic':name})
    for name in ('index.jsonl','shard.bin','values.jsonl'):
        write(toolchain/'inputs/ebpf/raw'/name, {'synthetic':name})
    stream = {'request_index':claim('inputs/ebpf/raw/index.jsonl'),
              'shards':[claim('inputs/ebpf/raw/shard.bin')],
              'runtime_identity_values':claim('inputs/ebpf/raw/values.jsonl')}
    ebpf = {'observations':2,'exports':[],'stream_exports':[stream]}
    native = {'observations':0,'exports':[],'stream_exports':[]}
    write(toolchain/'inputs/ebpf/raw/observations.json', ebpf)
    write(toolchain/'inputs/native/raw/observations.json', native)
    groups = [claim('inputs/'+source+'/raw/observations.json') for source in ('ebpf','native')]
    combined = {'observations':2,'exports':[],'stream_exports':[], 'ordered_request_group_manifests':groups}
    write(toolchain/'inputs/combined/raw/observations.json', combined)
    reference = {'schema_version':'identical-empty-native-observed-discovery-v1',
        'declared_source':'combined','variant':'raw','origin_source':'ebpf',
        'origin_folder':'/original/campaign/toolchain/'+origin,
        'additional_Bering_execution':False,'actual_discovery_cost_counted_once':True,
        'source_specific_operations_and_Sheaft_not_reused':True,
        'original_request_and_value_semantic_validation_reused_under_byte_identity':True,
        'genuine_origin_files':{name:claim(origin+'/'+name) for name in files},
        'origin_input':groups[0], 'empty_native_input':groups[1],
        'combined_input':claim('inputs/combined/raw/observations.json'),
        'ordered_input_groups':groups,'whole_current_source_files_reverified':[
            stream['request_index'],*stream['shards'],stream['runtime_identity_values']],
        'invocation':invocation,'started_ns':20,'ended_ns':30}
    path = toolchain/'discovery/combined/raw/shared-observed-reference.json'; write(path, reference)
    write(toolchain/'forecasts.json', {'combined':{'raw':{'fixture':{'available':False}}}})
    write(toolchain/'combined/raw/fixture/observed-reference.json', {
        'folder':'../../../discovery/ebpf/raw', 'files':{n:claim(origin+'/'+n)['sha256'] for n in
          ('observed.json','observed.signal-quality.json','observed.snapshot.json')}})
    write(toolchain/'execution-summary.json', {'branches':[{'source':'combined','variant':'raw','operation':'fixture',
        'bering_executed':True,'bering_discovery_shared_across_sources':True,'bering_discovery_source':'ebpf',
        'bering_discovery_record':'/original/campaign/toolchain/'+origin+'/observed-runtime/replay-command.json',
        'shared_discovery_reference':'/original/campaign/toolchain/discovery/combined/raw/shared-observed-reference.json'}]})
    claims = {p.relative_to(toolchain).as_posix():{'bytes':p.stat().st_size,'sha256':REVIEW.sha(p)}
              for p in toolchain.rglob('*') if p.is_file()}
    worker = root/'infrastructure/remote-toolchain-v4/worker'
    write(worker/'output-manifest.json', {'toolchain_files':claims})
    write(worker/'worker-status.json', {'started_ns':1,'ended_ns':40})
    freeze = {'sha256_by_path':{'toolchain/'+k:v['sha256'] for k,v in claims.items()}}
    graphs = [{'source':'ebpf','variant':'raw','observed_model_sha256':claim(origin+'/observed.json')['sha256'],
               'snapshot_sha256':claim(origin+'/observed.snapshot.json')['sha256']}]
    declaration = {'head_sha':'shared-fixture','collector':'deepflow','system':'otel_demo','mode':'absent'}
    return toolchain, declaration, freeze, graphs, {'binaries':[binary]}, path


def test_shared_discovery_has_two_logical_sources_and_one_physical_graph(tmp_path, monkeypatch):
    toolchain, decl, freeze, graphs, build, path = _shared_discovery_fixture(tmp_path, monkeypatch)
    facts = REVIEW.shared_observed_discovery_facts(tmp_path, toolchain, decl, freeze, graphs, build)
    assert len(graphs)==len(facts)==1
    assert facts[0]['source']=='combined' and facts[0]['actual_origin_source']=='ebpf'
    assert facts[0]['additional_Bering_execution'] is False
    assert SELECT.wanted_member(path.relative_to(tmp_path).as_posix(), 'full')
    assert REVIEW._package_selected(path.relative_to(toolchain).as_posix(), 'toolchain')


@pytest.mark.parametrize('head', [REVIEW.IDENTICAL_INPUT_DISCOVERY_SOURCE['revision'], REVIEW.UPLOAD_HOLD_PARENT_PROOF_HEAD])
def test_named_identical_source_does_not_skip_guest_or_closed_capture_proofs(tmp_path, head):
    decl={'head_sha':head, 'collector':'deepflow',
          'system':'otel_demo','mode':'absent','seed':6,'run_id':123}
    with pytest.raises((ValueError,OSError)):
        REVIEW.postcapture_guest_facts(tmp_path,decl)
    with pytest.raises((ValueError,OSError)):
        REVIEW.closed_postcapture_facts(tmp_path,decl,{},None,{})


@pytest.mark.parametrize('mutation', ['unreviewed_source','other_mode','extra_replay','origin_source',
    'wrong_variant','file_coverage','child_order','wire_coverage','wrong_invocation','late_worker',
    'physical_graph','source_graph_hash','shadow_combined','operation_origin'])
def test_shared_discovery_rejects_false_logical_coverage(tmp_path, monkeypatch, mutation):
    toolchain, decl, freeze, graphs, build, path = _shared_discovery_fixture(tmp_path, monkeypatch)
    value = json.loads(path.read_text())
    if mutation=='unreviewed_source': decl['head_sha']='unknown'
    elif mutation=='other_mode': decl['mode']='partial'
    elif mutation=='extra_replay': value['additional_Bering_execution']=True
    elif mutation=='origin_source': value['origin_source']='native'
    elif mutation=='wrong_variant': value['variant']='network_scope'
    elif mutation=='file_coverage': value['genuine_origin_files'].pop('observed.snapshot.json')
    elif mutation=='child_order': value['ordered_input_groups']=list(reversed(value['ordered_input_groups']))
    elif mutation=='wire_coverage': value['whole_current_source_files_reverified'].pop()
    elif mutation=='wrong_invocation': value['invocation']['publication_mode']='windowed'
    elif mutation=='late_worker': value['ended_ns']=41
    elif mutation=='physical_graph': graphs=[]
    elif mutation=='source_graph_hash': graphs[0]['observed_model_sha256']='0'*64
    elif mutation=='shadow_combined':
        manifest=tmp_path/'infrastructure/remote-toolchain-v4/worker/output-manifest.json'
        body=json.loads(manifest.read_text());body['toolchain_files']['discovery/combined/raw/observed.json']={'sha256':'0'*64,'bytes':1}
        manifest.write_text(json.dumps(body))
    elif mutation=='operation_origin':
        item=toolchain/'combined/raw/fixture/observed-reference.json';body=json.loads(item.read_text());body['folder']='../../../discovery/native/raw';item.write_text(json.dumps(body))
    path.write_text(json.dumps(value)+'\n')
    # Bind the mutated proof itself so semantic rejections cannot pass merely by checksum failure.
    current={'bytes':path.stat().st_size,'sha256':REVIEW.sha(path)}
    freeze['sha256_by_path']['toolchain/discovery/combined/raw/shared-observed-reference.json']=current['sha256']
    manifest=tmp_path/'infrastructure/remote-toolchain-v4/worker/output-manifest.json';body=json.loads(manifest.read_text());body['toolchain_files']['discovery/combined/raw/shared-observed-reference.json']=current;manifest.write_text(json.dumps(body))
    with pytest.raises((ValueError, OSError)):
        REVIEW.shared_observed_discovery_facts(tmp_path,toolchain,decl,freeze,graphs,build)


@pytest.mark.parametrize('mutation', ['none', 'changed_diagnostic', 'unowned_overlay', 'missing_exit', 'empty_capture', 'missing_identity'])
@pytest.mark.parametrize('head', [REVIEW.POSTCAPTURE_GUEST_RELEASE_HEAD, REVIEW.CLOSED_POSTCAPTURE_HEAD])
def test_named_postcapture_source_requires_actual_owned_release_and_unchanged_diagnostics(tmp_path,mutation,head):
    declaration={'head_sha':head,'collector':'deepflow',
                 'system':'otel_demo','mode':'absent','seed':6,'run_id':99}
    files={}
    for node in ('a','b'):
        for name in ('check-copy.err','serial-test.err','guest-kernel-final.txt',
                     'guest-kernel-final.err','guest-kernel-final.returncode',
                     'serial-test.returncode','serial-copy.status'):
            path=tmp_path/'infrastructure'/node/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(b'1')  # Failed diagnostic RC is preserved, not fabricated as success.
            files[path.relative_to(tmp_path).as_posix()]={'bytes':1,'sha256':hashlib.sha256(b'1').hexdigest()}
    capture={'status':'complete','schema':'owned-guest-diagnostics-v5','campaign_root':'/own/campaign',
             'vm_root':'/own/vms','run_id':99,'source':declaration['head_sha'],'files':files}
    if mutation=='empty_capture':
        capture['files']={}
    capture_path=tmp_path/'infrastructure/guest-evidence-capture.json'
    capture_path.write_text(json.dumps(capture))
    owned=[{'node':node,'pid':2000+i,'start_ticks':'4','pidfile':f'/own/vms/{node}.pid',
        'overlay':f'/own/vms/{node}/root.qcow2','args':['qemu-system-x86_64','-pidfile',
        f'/own/vms/{node}.pid','-drive',f'file=/own/vms/{node}/root.qcow2,format=qcow2,if=virtio']}
        for i,node in enumerate(('a','b'))]
    release={'status':'complete','started_ns':1,'owned_guests_confirmed_exited_ns':2,'ended_ns':3,
        'guest_evidence_capture_SHA256':REVIEW.sha(capture_path),'owned_processes':owned,
        'verified_pidfd_signal_result':[{**row,'status':'TERM_sent_through_verified_pidfd'} for row in owned],
        'removed_ephemeral_overlays':[{'path':row['overlay']} for row in owned],
        'pidfile_cleanup':[{'node':row['node'],'path':row['pidfile'],
                           'disposition':'already_removed_after_confirmed_exit'} for row in owned]}
    if mutation=='unowned_overlay':
        release['removed_ephemeral_overlays'][0]['path']='/other/important.qcow2'
    if mutation=='missing_exit':
        release.pop('owned_guests_confirmed_exited_ns')
    if mutation=='missing_identity':
        release['owned_processes'][0].pop('start_ticks')
        release['verified_pidfd_signal_result'][0].pop('start_ticks')
    if mutation=='changed_diagnostic':
        (tmp_path/'infrastructure/a/guest-kernel-final.txt').write_bytes(b'changed')
    (tmp_path/'infrastructure/postcapture-guest-release.json').write_text(json.dumps(release))
    if mutation=='none':
        facts=REVIEW.postcapture_guest_facts(tmp_path,declaration)
        assert facts['diagnostic_returncodes_preserved_not_forced_success'] is True
        assert facts['whole_case_memory_disk_headroom_or_six_hour_cure_proven'] is False
    else:
        with pytest.raises(ValueError):
            REVIEW.postcapture_guest_facts(tmp_path,declaration)


@pytest.mark.parametrize('supported', [False, True])
def test_binding_summary_preserves_literal_candidates_without_witness_arrays(tmp_path, supported):
    toolchain = tmp_path/'toolchain'
    branch = toolchain/'combined/raw/browse'
    unknown = [{'reason': 'required_call_missing_or_ambiguous',
                'obligation': {'caller': ['front'], 'callee': ['catalog']}}]
    vectors = [{'11': 1, '10': 1, '01': 1, '00': 0},
               {'11': 1, '10': 1, '01': 1, '00': 1}] if supported else [None, None]
    binding = {'available': False, 'unknown': unknown,
               'endpoint_bindings': ['DO_NOT_COPY_WITNESSES' * 1000],
               'database_fault_prediction_available': False,
               'entry_identity_resolution': {
                   'selected_observed_entry': None,
                   'all_supported_state_vectors_agree': not supported,
                   'known_database_predictions_agree': False,
                   'supplied_identity_group': {'proof': 'DO_NOT_COPY_WITNESSES'},
                   'candidates': [{'entry': name, 'binding': {
                       'available': supported, 'unknown': [] if supported else unknown,
                       'endpoint_bindings': ['DO_NOT_COPY_WITNESSES']},
                       'exact_state_vector': vector, 'exact_database_down': db}
                       for name, vector, db in zip(('thrift', 'web'), vectors, (None, 0))]}}
    write(branch/'binding.json', binding)
    key = 'toolchain/combined/raw/browse/binding.json'
    facts = REVIEW.saved_binding_summary(toolchain, branch, {'sha256_by_path': {key: digest(branch/'binding.json')}})
    assert facts['path'] == key and facts['frozen_hash_matches'] is True
    assert facts['sha256'] == digest(branch/'binding.json')
    assert facts['fields_copied']['unknown'] == unknown
    entry = facts['entry_identity_resolution_copied']
    assert entry['all_supported_state_vectors_agree'] is not supported
    assert [candidate['exact_state_vector'] for candidate in entry['candidates']] == vectors
    assert [candidate['exact_database_down'] for candidate in entry['candidates']] == [None, 0]
    assert all(candidate['available'] is supported for candidate in entry['candidates'])
    assert 'DO_NOT_COPY_WITNESSES' not in json.dumps(facts)


def test_binding_summary_missing_or_unclaimed_file_does_not_add_admission_gate(tmp_path):
    toolchain, branch = tmp_path/'toolchain', tmp_path/'toolchain/ebpf/raw/browse'
    assert REVIEW.saved_binding_summary(toolchain, branch, None)['present'] is False
    write(branch/'binding.json', {'available': False, 'unknown': []})
    assert REVIEW.saved_binding_summary(toolchain, branch, None)['frozen_hash_matches'] is None
    facts = REVIEW.saved_binding_summary(toolchain, branch, {
        'sha256_by_path': {'toolchain/ebpf/raw/browse/binding.json': 'f'*64}})
    assert facts['frozen_hash_matches'] is False
    write(branch/'binding.json', b'not valid JSON')
    assert REVIEW.saved_binding_summary(toolchain, branch, None)['projection_error_type'] == 'JSONDecodeError'


def metadata_fixture(tmp_path):
    toolchain = tmp_path / "toolchain"
    branch = toolchain / "combined/raw/details"
    shared = toolchain / "discovery/combined/raw"
    observed = {"metadata": {"source_ref": "actual-first", "discovered_at": "first-time"},
                "services": [{"id": "gateway", "replicas": 1}, {"id": "visits", "replicas": 1}],
                "edges": [{"id": "opaque-docker-visits-db", "from": "gateway", "to": "visits", "observations": 7}],
                "endpoints": [{"id": "details", "entry_service": "gateway",
                               "metadata": {"semantics": {"observed": "retained"}}},
                              {"id": "scalar-only", "entry_service": "gateway"}]}
    overlay = {"services": [{"id": "visits", "replicas": 2, "failure_eligible": True,
                             "placements": [{"replicas": 1, "labels": {"guest": node}} for node in ("a", "b")],
                             "attributes": {"provided": "snapshot-only"}},
                            {"id": "gateway", "replicas": 1, "attributes": {"annotation": "snapshot-only"}}],
               "endpoints": [{"id": "details", "predicate_ref": "details",
                              "semantics": {"predicate_mode": "external_predicate", "source": "supplied_source_contract"}},
                             {"id": "scalar-only", "predicate_ref": "scalar-only"}]}
    attached = json.loads(json.dumps(observed))
    attached["services"][1].update(replicas=2, metadata={
        "failure_eligible": True, "placements": overlay["services"][0]["placements"]})
    attached["endpoints"][0]["success_predicate_ref"] = "details"
    attached["endpoints"][0]["metadata"]["semantics"].update(overlay["endpoints"][0]["semantics"])
    attached["endpoints"][1]["success_predicate_ref"] = "scalar-only"
    sources = {"observed_model": (shared / "observed.json", observed),
               "raw_bering_model": (shared / "observed.bering-raw.json", observed),
               "raw_bering_snapshot": (shared / "observed.snapshot.json", {"model": observed}),
               "semantic_projection": (shared / "observed.supplied-aliases.json", {}),
               "provided_overlay": (branch / "overlay.json", overlay),
               "simulator_model": (branch / "model.json", attached)}
    for path, value in sources.values():
        write(path, value)
    proof = {"origin": "provided_metadata_after_verified_semantic_view",
             "files": {key: {"path": "/saved/toolchain/" + path.relative_to(toolchain).as_posix(),
                             "sha256": digest(path)} for key, (path, _) in sources.items()},
             "supplied": overlay, "new_nodes_edges_or_endpoints": False,
             "graph_structure_and_observed_edge_fields_unchanged": True, "entity_ids_unchanged": True,
             "final_model_is_a_bering_emitted_snapshot": False, "source_signal_quality_unchanged": True,
             "same_information_all_sources_and_direct_baseline": True}
    write(branch / "provided-metadata-attachment.json", proof)
    write(branch / "provided-metadata-validation.command.json", {
        "argv": ["bering", "validate", "--input", "/saved/toolchain/combined/raw/details/model.json"], "returncode": 0})
    for path in (shared / "observed.signal-quality.json", branch / "model.signal-quality.json"):
        write(path, {"observed_quality": "unchanged"})
    freeze = {"sha256_by_path": {"toolchain/" + path.relative_to(toolchain).as_posix(): digest(path)
                                 for path in toolchain.rglob("*") if path.is_file()}}
    return toolchain, branch, freeze


def test_operation_metadata_review_reconstructs_all_fields_and_preserves_first_provenance(tmp_path):
    toolchain, branch, freeze = metadata_fixture(tmp_path)
    facts = REVIEW.operation_metadata_facts(toolchain, branch, freeze)
    assert facts["all_model_fields_exact"]
    assert facts["source_signal_quality_bytes_unchanged"]
    assert facts["final_model_is_a_bering_emitted_snapshot"] is False
    for name in ("overlay.json", "model.signal-quality.json", "provided-metadata-attachment.json",
                 "provided-metadata-validation.command.json"):
        assert SELECT.wanted_member("toolchain/combined/raw/details/" + name, "full")
        assert REVIEW._package_selected("combined/raw/details/" + name, "toolchain")
    assert SELECT.wanted_member("toolchain/discovery/combined/raw/observed.signal-quality.json", "full")
    assert REVIEW._package_selected("discovery/combined/raw/observed.signal-quality.json", "toolchain")


@pytest.mark.parametrize('changed', [None, 'analysis-hash', 'command-analysis', 'predicate-reference', 'unfrozen-faults'])
def test_paired_metadata_uses_seven_real_links_and_exact_analysis(tmp_path, changed):
    toolchain, original_branch, freeze = metadata_fixture(tmp_path)
    out = toolchain/'context-baseline/raw'
    branch = out/'operations/details'
    for name in ('overlay.json', 'model.json', 'model.signal-quality.json'):
        write(branch/name, (original_branch/name).read_bytes())
    write(out/'union-model.json', REVIEW.read(toolchain/'discovery/combined/raw/observed.json'))
    write(out/'union-proof.json', {'fixture_union_derivation': True})
    proof = REVIEW.read(original_branch/'provided-metadata-attachment.json')
    for key, path in (('observed_model', out/'union-model.json'),
                      ('observation_derivation', out/'union-proof.json'),
                      ('provided_overlay', branch/'overlay.json'), ('simulator_model', branch/'model.json')):
        proof['files'][key] = {'path': '/saved/toolchain/' + path.relative_to(toolchain).as_posix(), 'sha256': digest(path)}
    proof.update(observed_graph_origin='paired_context_edge_union',
                 source_signal_quality_scope='base entities and database aliases; added edge evidence is in the actual joint quality',
                 observation_derivation={key: proof['files'][name] for key, name in
                                         (('model', 'observed_model'), ('proof', 'observation_derivation'))})
    write(branch/'provided-metadata-attachment.json', proof)
    write(branch/'provided-metadata-validation.command.json', {
        'returncode': 0, 'argv': ['bering', 'validate', '--input',
                                 '/saved/toolchain/context-baseline/raw/operations/details/model.json']})
    base_path = '/saved/toolchain/context-baseline/raw/operations/details/'
    write(branch/'analysis.json', {'predicate_contract': base_path + 'predicates.json',
                                  'fault_contract': base_path + 'faults.json'})
    write(branch/'predicates.json', {'supplied_predicate_fixture': True})
    write(branch/'faults.json', {'supplied_fault_fixture': True})
    write(branch/'simulation.command.json', {'returncode': 0, 'argv': [
        'sheaft', 'run', '--model', base_path + 'model.json', '--analysis', base_path + 'analysis.json',
        '--out-dir', base_path + 'simulation']})
    forecast = {'simulator': 'Sheaft', 'graph_sha256': digest(branch/'model.json'),
                'analysis_sha256': digest(branch/'analysis.json'), 'by_state': {'11': 1, '00': 0}}
    write(branch/'simulation/report.json', {
        'input_artifact': {'digest': 'sha256:' + digest(branch/'model.json'), 'path': base_path + 'model.json'},
        'profiles': [{'name': 'state-' + state, 'simulation': {'endpoint_availability': {'details': value, 'scalar-only': value}}}
                     for state, value in forecast['by_state'].items()]})
    if changed == 'analysis-hash':
        write(branch/'analysis.json', {'different_analysis': True})
    elif changed == 'command-analysis':
        command = REVIEW.read(branch/'simulation.command.json')
        command['argv'][5] = base_path + 'other-analysis.json'
        write(branch/'simulation.command.json', command)
    elif changed == 'predicate-reference':
        analysis = REVIEW.read(branch/'analysis.json')
        analysis['predicate_contract'] = base_path + 'other-predicates.json'
        write(branch/'analysis.json', analysis)
        forecast['analysis_sha256'] = digest(branch/'analysis.json')
    freeze['sha256_by_path'].update({'toolchain/' + path.relative_to(toolchain).as_posix(): digest(path)
                                     for path in out.rglob('*') if path.is_file()})
    if changed == 'unfrozen-faults':
        del freeze['sha256_by_path']['toolchain/context-baseline/raw/operations/details/faults.json']
    if changed:
        with pytest.raises(ValueError):
            REVIEW.paired_simulation_facts(toolchain, branch, forecast, freeze)
        return
    facts = REVIEW.paired_simulation_facts(toolchain, branch, forecast, freeze)
    assert facts['all_model_fields_exact']
    assert 'toolchain/context-baseline/raw/union-proof.json' in facts['verified_frozen_paths']


@pytest.mark.parametrize('changed', [None, 'model-reference', 'one-endpoint-state', 'database-state', 'unfrozen-report'])
def test_primary_saved_report_binds_actual_model_and_every_operation_endpoint(tmp_path, changed):
    toolchain, branch, freeze = metadata_fixture(tmp_path)
    base = '/saved/toolchain/combined/raw/details/'
    write(branch/'analysis.json', {'predicate_contract': base + 'predicates.json'})
    write(branch/'predicates.json', {'provided_operation': 'details'})
    write(branch/'simulation.command.json', {'returncode': 0, 'argv': [
        'sheaft', 'run', '--model', base + 'model.json', '--analysis', base + 'analysis.json',
        '--out-dir', base + 'simulation']})
    forecast = {'simulator': 'Sheaft', 'graph_sha256': digest(branch/'model.json'),
                'analysis_sha256': digest(branch/'analysis.json'), 'by_state': {'11': 1, '00': 0},
                'database_down_prediction': 0}
    report = {'input_artifact': {'digest': 'sha256:' + digest(branch/'model.json'), 'path': base + 'model.json'},
              'profiles': {'state-' + state: {'simulation': {'endpoint_availability': {'details': value, 'scalar-only': value}}}
                           for state, value in forecast['by_state'].items()}}
    report['profiles']['db-down'] = {'simulation': {'endpoint_availability': {'details': 0, 'scalar-only': 0}}}
    if changed == 'model-reference':
        report['input_artifact']['path'] = base + 'another-model.json'
    elif changed == 'one-endpoint-state':
        report['profiles']['state-00']['simulation']['endpoint_availability']['scalar-only'] = 1
    elif changed == 'database-state':
        report['profiles']['db-down']['simulation']['endpoint_availability']['scalar-only'] = 1
    write(branch/'simulation/report.json', report)
    freeze['sha256_by_path'] = {'toolchain/' + p.relative_to(toolchain).as_posix(): digest(p)
                               for p in toolchain.rglob('*') if p.is_file()}
    if changed == 'unfrozen-report':
        freeze['sha256_by_path'].pop('toolchain/combined/raw/details/simulation/report.json')
    if changed:
        with pytest.raises(ValueError):
            REVIEW.paired_simulation_facts(toolchain, branch, forecast, freeze)
    else:
        facts = REVIEW.paired_simulation_facts(toolchain, branch, forecast, freeze)
        assert facts['saved_simulation_report']['model_digest_and_all_operation_endpoint_state_values_match']
    for name in ('analysis.json', 'predicates.json', 'faults.json', 'simulation/report.json'):
        assert SELECT.wanted_member('toolchain/combined/raw/details/' + name, 'full')
        assert REVIEW._package_selected('combined/raw/details/' + name, 'toolchain')
        assert SELECT.wanted_member('toolchain/context-baseline/raw/operations/details/' + name, 'full')
        assert REVIEW._package_selected('context-baseline/raw/operations/details/' + name, 'toolchain')


@pytest.mark.parametrize("changed", ["edge", "first-provenance", "unknown-entity", "quality", "command", "locator", "unfrozen", "publication-claim"])
def test_operation_metadata_review_rejects_even_rehashed_unexplained_changes(tmp_path, changed):
    toolchain, branch, freeze = metadata_fixture(tmp_path)
    proof_path = branch / "provided-metadata-attachment.json"
    proof = REVIEW.read(proof_path)
    if changed in ("edge", "first-provenance"):
        path = branch / "model.json"
        value = REVIEW.read(path)
        if changed == "edge":
            value["edges"][0]["observations"] += 1
        else:
            value["metadata"]["source_ref"] = "invented-second"
        write(path, value)
        proof["files"]["simulator_model"]["sha256"] = digest(path)
    elif changed == "unknown-entity":
        overlay = REVIEW.read(branch / "overlay.json")
        overlay["services"][0]["id"] = "not-observed"
        write(branch / "overlay.json", overlay)
        proof["supplied"] = overlay
        proof["files"]["provided_overlay"]["sha256"] = digest(branch / "overlay.json")
    elif changed == "quality":
        write(branch / "model.signal-quality.json", {"observed_quality": "invented"})
    elif changed == "command":
        write(branch / "provided-metadata-validation.command.json", {
            "argv": ["bering", "validate", "--input", "/saved/toolchain/combined/raw/other/model.json"], "returncode": 0})
    elif changed == "locator":
        proof["files"]["simulator_model"]["path"] = "/saved/toolchain/combined/raw/other/model.json"
    elif changed == "publication-claim":
        proof["final_model_is_a_bering_emitted_snapshot"] = True
    write(proof_path, proof)
    if changed != "unfrozen":
        freeze["sha256_by_path"].update({"toolchain/" + path.relative_to(toolchain).as_posix(): digest(path)
                                        for path in toolchain.rglob("*") if path.is_file()})
    else:
        del freeze["sha256_by_path"]["toolchain/combined/raw/details/overlay.json"]
    with pytest.raises(ValueError):
        REVIEW.operation_metadata_facts(toolchain, branch, freeze)


@pytest.mark.parametrize("changed", [None, "same_boot", "wrong_image", "check_mismatch", "invalid_boot"])
def test_fresh_guest_facts_require_actual_distinct_boot_proofs_without_claiming_hosts(tmp_path, changed):
    boots = {"a": "11111111-1111-4111-8111-111111111111",
             "b": "22222222-2222-4222-8222-222222222222"}
    if changed == "same_boot":
        boots["b"] = boots["a"]
    if changed == "invalid_boot":
        boots["b"] = "not-a-kernel-boot-uuid"
    nodes = {node: "6.8.0-147-generic\n" + boot + "\n26.0\n" for node, boot in boots.items()}
    for node, text in nodes.items():
        write(tmp_path / "infrastructure" / node / "check.txt",
              (text + "changed" if changed == "check_mismatch" and node == "b" else text).encode())
    write(tmp_path / "infrastructure/infrastructure.json", {
        "status": "ready", "nodes": nodes, "guest_memory_mib": 6144, "shared_physical_host": True})
    write(tmp_path / "infrastructure/image-provenance.json", {
        "sha256": "wrong" if changed == "wrong_image" else REVIEW.FRESH_GUEST_IMAGE_SHA256})
    if changed:
        with pytest.raises(ValueError):
            REVIEW.guest_platform_facts(tmp_path)
    else:
        facts = REVIEW.guest_platform_facts(tmp_path)
        assert facts["boot_ids"] == boots
        assert facts["guest_memory_mib"] == 6144
        assert facts["shared_runner_host"] is True
        assert facts["separate_physical_hosts_claimed"] is False
        assert facts["guest_image_bytes_independently_rehashed_by_this_review"] is False
    for name in ("infrastructure/infrastructure.json", "infrastructure/image-provenance.json",
                 "infrastructure/a/check.txt", "infrastructure/b/check.txt"):
        assert SELECT.wanted_member(name, "full")


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, (dict, list)):
        path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    else:
        path.write_bytes(value)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paired_fixture(tmp_path, *, joint=True, added=True, conflict=False):
    root, toolchain = tmp_path, tmp_path/'toolchain'
    baseline = toolchain/'context-baseline'
    original = {'combined': {}}
    predictions, variants, evaluations = {}, {}, []
    base = {'services': [{'id': 'front'}, {'id': 'catalog'}], 'endpoints': [],
            'metadata': {'source_ref': 'actual-strict-view'},
            'edges': [{'id': 'existing', 'from': 'front', 'to': 'catalog',
                       'identity': {'span_kind': 'client'}, 'observations': 9}]}
    extra = {'id': 'actual-server', 'from': 'front', 'to': 'catalog',
             'identity': {'span_kind': 'server'}, 'observations': 3}
    def ref(path):
        return {'path': '/saved/' + path.relative_to(root).as_posix(), 'sha256': digest(path)}
    for name, value in (
            ('supplied-service-aliases-training.json', {}),
            ('supplied-service-alias-admission-training.json', {'aliases': {}})):
        write(root/'runtime-identity-v5'/name, value)
    write(toolchain/'static-inputs.json', {})
    for variant in ('raw', 'network_scope'):
        counts = {'ebpf': 1, 'native': int(joint)}
        for source, count in counts.items():
            write(toolchain/'inputs'/source/variant/'observations.json', {'observations': count})
        inputs = toolchain/'inputs/combined'/variant/'observations.json'
        exports = [{'source': source, 'path': '/saved/toolchain/inputs/' + source + '/' + variant + '/body.pb',
                    'sha256': ('a' if source == 'ebpf' else 'b') * 64,
                    'observations': 1} for source, count in counts.items() if count]
        write(inputs, {'observations': sum(counts.values()), 'exports': exports})
        original['combined'][variant] = {'browse': {'available': False, 'prediction': None,
                                                   'unknown': [{'reason': 'required_call_missing', 'callee': 'catalog'}],
                                                   'interval': [0, 1], 'reason': 'saved_primary_unknown'}}
        predictions[variant] = json.loads(json.dumps(original['combined'][variant]))
        variants[variant] = {'input_manifest': ref(inputs), 'source_observations': counts,
                             'status': 'reuse_single_source_equivalence', 'extra_bering_or_sheaft_executed': False}
        for source in ('combined', 'context-baseline'):
            evaluations.append({'source': source, 'variant': variant, 'operation': 'browse',
                                **{key: value for key, value in predictions[variant]['browse'].items() if key != 'interval'},
                                'unknown_obligations': predictions[variant]['browse']['unknown'],
                                'by_state': {'11': {'counts': {'success': 2, 'failure': 0}, 'bounds': [1, 1]},
                                             '00': {'counts': {'success': 0, 'failure': 1}, 'bounds': [0, 0]}},
                                'forecast_interval': [0, 1], 'actual_counts': {'success': 2, 'failure': 1}})
    write(toolchain/'forecasts.json', original)
    for variant in variants:
        out, shared = baseline/variant, toolchain/'discovery/combined'/variant
        provenance = variants[variant]
        provenance['original_forecasts'] = ref(toolchain/'forecasts.json')
        if joint:
            folder = out/'joint'
            joint_model = json.loads(json.dumps(base))
            joint_model['edges'][0]['observations'] = 55  # Alternate statistics must not overwrite the base.
            if conflict:
                joint_model['edges'][0]['blocking'] = True
            if added:
                joint_model['edges'].append(extra)
            merged = json.loads(json.dumps(base))
            if added:
                merged['edges'].append(extra)
            for path, value in ((shared/'observed.json', base), (shared/'observed.bering-raw.json', base),
                                (shared/'observed.snapshot.json', {'model': base}),
                                (shared/'observed.signal-quality.json', {}), (shared/'observed.supplied-aliases.json', {}),
                                (folder/'observed.json', joint_model), (folder/'canonical.json', REVIEW.alias_only_model(joint_model, {})),
                                (folder/'observed.snapshot.json', {'model': joint_model}),
                                (folder/'observed.signal-quality.json', {}), (folder/'canonical.signal-quality.json', {}),
                                (out/'union-model.json', merged)):
                write(path, value)
            alias = {'table_sha256': digest(root/'runtime-identity-v5/supplied-service-aliases-training.json'),
                     'raw_model_sha256': digest(folder/'observed.json'),
                     'raw_quality_sha256': digest(folder/'observed.signal-quality.json'),
                     'metadata_collisions': [], 'effective_aliases': {}}
            write(folder/'supplied-aliases.json', alias)
            manifest = REVIEW.read(toolchain/'inputs/combined'/variant/'observations.json')
            sequence = [{'export_index': index, 'content_sha256': row['sha256'], 'content_bytes': 42,
                         'http_status': 200, 'endpoint': '/v1/traces', 'storage_form': 'ordinary_export',
                         'original_source': row['source']} for index, row in enumerate(manifest['exports'])]
            for directory, paired in ((folder, True), (shared, False)):
                rows = json.loads(json.dumps(sequence))
                if not paired:
                    for row in rows:
                        source = row.pop('original_source')
                        row['endpoint'] = '/sources/ebpf/v1/traces' if source == 'ebpf' else '/v1/traces'
                sequence_path = directory/'observed-runtime/accepted-request-sequence.jsonl'
                write(sequence_path, ''.join(json.dumps(row) + '\n' for row in rows).encode())
                replay = {'accepted_request_sequence': {**ref(sequence_path), 'bytes': sequence_path.stat().st_size,
                          'requests': len(rows), 'same_order_as_original_request_ordinals_and_source_groups': True},
                          'accepted_ingest_requests': [{key: value for key, value in row.items() if key != 'storage_form'} for row in rows]}
                if paired:
                    replay.update(returncode=0, status='complete', request_routing='ordinary_otlp_joint_view',
                                  argv=['/saved/bin/bering', 'serve', '--config', '/saved/toolchain/context-baseline/' + variant + '/joint/observed-runtime/serve.yaml'],
                                  source_profile={'input_type': 'otlp', 'trace_context_domain': ''},
                                  original_source_profile={'source_id': 'ebpf', 'input_type': 'ebpf-otlp'},
                                  source_domain='', clock_admission_filter=False, original_export_roles_retained=True,
                                  ingest={'spans': 2, 'dropped_spans': 0, 'late_spans': 0})
                    write(directory/'observed-runtime/serve.yaml', {
                        'runtime': {'publication_mode': 'on_shutdown', 'max_in_memory_spans': 3,
                                    'reconciliation': {'enabled': False}}, 'overlays': [],
                        'sink': {'latest_path': '/saved/toolchain/context-baseline/' + variant + '/joint/observed.snapshot.json',
                                 'signal_quality_path': '/saved/toolchain/context-baseline/' + variant + '/joint/observed.signal-quality.json'}})
                write(directory/'observed-runtime/replay-command.json', replay)
            files = {'base_model': shared/'observed.json', 'base_raw_model': shared/'observed.bering-raw.json',
                     'base_snapshot': shared/'observed.snapshot.json', 'base_quality': shared/'observed.signal-quality.json',
                     'base_alias_projection': shared/'observed.supplied-aliases.json',
                     'joint_raw_model': folder/'observed.json', 'joint_snapshot': folder/'observed.snapshot.json',
                     'joint_quality': folder/'observed.signal-quality.json', 'joint_model': folder/'canonical.json',
                     'joint_canonical_quality': folder/'canonical.signal-quality.json',
                     'joint_alias_projection': folder/'supplied-aliases.json',
                     'joint_replay': folder/'observed-runtime/replay-command.json',
                     'joint_config': folder/'observed-runtime/serve.yaml',
                     'joint_accepted_sequence': folder/'observed-runtime/accepted-request-sequence.jsonl',
                     'union_model': out/'union-model.json',
                     'input_manifest': toolchain/'inputs/combined'/variant/'observations.json',
                     'static_inputs': toolchain/'static-inputs.json',
                     'alias_table': root/'runtime-identity-v5/supplied-service-aliases-training.json',
                     'alias_admission': root/'runtime-identity-v5/supplied-service-alias-admission-training.json'}
            proof = {'files': {key: ref(path) for key, path in files.items()},
                     'configured_tool_pins': {'Procrustes': REVIEW.PINS['procrustes'], 'Bering': REVIEW.FRESH_BERING,
                                              'Sheaft': REVIEW.PINS['sheaft']},
                     'added_edge_ids': ['actual-server'] if added else [],
                     'semantic_identity_conflicts': ['existing'] if conflict else [],
                     'skipped_joint_edges': [], 'joint_alias_metadata_collisions': [],
                     'union_is_a_bering_emitted_snapshot': False, 'contract_inferred_edges': False,
                     'physical_identity_inferred': False}
            write(out/'union-proof.json', proof)
            status = ('unknown_view_alignment' if conflict else
                      'forecast_from_observed_context_union' if added else 'reuse_unchanged_union')
            provenance.pop('extra_bering_or_sheaft_executed')
            provenance.update(status=status, extra_bering_executed=True,
                              union={'model': ref(out/'union-model.json'), 'proof': ref(out/'union-proof.json')})
            if status != 'forecast_from_observed_context_union':
                provenance['extra_sheaft_executed'] = False
            if conflict:
                predictions[variant]['browse']['reason'] = 'context_view_identity_or_alias_conflict'
                for row in evaluations:
                    if row['source'] == 'context-baseline' and row['variant'] == variant:
                        row['reason'] = 'context_view_identity_or_alias_conflict'
        write(out/'provenance.json', provenance)
    write(baseline/'forecasts.json', predictions)
    write(baseline/'manifest.json', {'policy_id': 'observed_server_edge_union_v1', 'variants': variants,
          'same_policy_all_collectors_and_scenarios': True, 'requires_capture_freeze_before_targets': True,
          'post_target_diagnostic_is_not_a_primary_forecast': True})
    freeze = {'sha256_by_path': {path.relative_to(root).as_posix(): digest(path)
                                for path in root.rglob('*') if path.is_file()}}
    for variant in variants:
        for row in REVIEW.read(toolchain/'inputs/combined'/variant/'observations.json')['exports']:
            freeze['sha256_by_path']['toolchain/' + REVIEW.toolchain_relative(row['path'])] = row['sha256']
    return root, toolchain, freeze, original, {'evaluations': evaluations}


@pytest.mark.parametrize('joint,added,conflict', [(False, False, False), (True, False, False),
                                                (True, True, False), (True, True, True)])
def test_paired_saved_facts_cover_reuse_actual_union_and_unknown_conflict(tmp_path, joint, added, conflict):
    args = paired_fixture(tmp_path, joint=joint, added=added, conflict=conflict)
    facts = REVIEW.context_baseline_facts(*args)
    assert facts['external_outcomes_recomputed'] is False
    assert facts['variants']['raw']['union'] is None if not joint else facts['variants']['raw']['union']['exact_base_and_all_added_fields']
    for name in ('union-proof.json', 'joint/observed-runtime/accepted-request-sequence.jsonl',
                 'operations/browse/provided-metadata-attachment.json'):
        assert SELECT.wanted_member('toolchain/context-baseline/raw/' + name, 'full')
        assert REVIEW._package_selected('context-baseline/raw/' + name, 'toolchain')
    assert not SELECT.wanted_member('toolchain/context-baseline/raw/joint/attempt-journal.jsonl', 'full')


@pytest.mark.parametrize('joint,added', [(False, False), (True, False), (True, True)])
def test_paired_binding_summary_points_to_literal_binding_or_exact_combined_reuse(tmp_path, joint, added):
    args = paired_fixture(tmp_path, joint=joint, added=added)
    root, toolchain, freeze, original, evaluation = args
    for variant in ('raw', 'network_scope'):
        branch = (toolchain/'context-baseline'/variant/'operations/browse' if added
                  else toolchain/'combined'/variant/'browse')
        write(branch/'binding.json', {'available': False, 'unknown': [{'reason': 'saved_reason'}]})
        freeze['sha256_by_path']['toolchain/'+(branch/'binding.json').relative_to(toolchain).as_posix()] = digest(branch/'binding.json')
    facts = REVIEW.context_baseline_facts(*args)
    summary = facts['variants']['raw']['branches'][0]['binding_summary']
    assert summary['path'] == ('toolchain/context-baseline/raw/operations/browse/binding.json' if added
                               else 'toolchain/combined/raw/browse/binding.json')
    assert summary['frozen_hash_matches'] is True
    assert summary['fields_copied']['unknown'] == [{'reason': 'saved_reason'}]


@pytest.mark.parametrize('changed', ['base-statistic', 'extra-client', 'request-role', 'locator',
                                     'unfrozen', 'external-outcomes', 'unknown-reuse', 'unknown-details',
                                     'state-outcomes', 'config', 'config-command'])
def test_paired_saved_facts_reject_independently_rehashed_changes(tmp_path, changed):
    args = paired_fixture(tmp_path, added=changed != 'unknown-reuse')
    root, toolchain, freeze, original, evaluation = args
    baseline = toolchain/'context-baseline'
    if changed in ('base-statistic', 'extra-client'):
        path = baseline/'raw/union-model.json'
        model = REVIEW.read(path)
        if changed == 'base-statistic':
            model['edges'][0]['observations'] += 1
        else:
            model['edges'].append({'id': 'invented-client', 'from': 'front', 'to': 'catalog'})
        write(path, model)
    elif changed == 'request-role':
        path = baseline/'raw/joint/observed-runtime/accepted-request-sequence.jsonl'
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[0]['original_source'] = 'native'
        write(path, ''.join(json.dumps(row) + '\n' for row in rows).encode())
    elif changed == 'locator':
        path = baseline/'raw/union-proof.json'
        proof = REVIEW.read(path)
        proof['files']['base_model']['path'] = '/saved/toolchain/discovery/native/raw/observed.json'
        write(toolchain/'discovery/native/raw/observed.json', REVIEW.read(toolchain/'discovery/combined/raw/observed.json'))
        write(path, proof)
    elif changed == 'external-outcomes':
        evaluation['evaluations'][1]['actual_counts']['success'] += 1
    elif changed == 'unknown-details':
        evaluation['evaluations'][1]['unknown_obligations'] = [{'reason': 'silently_removed_callee'}]
    elif changed == 'state-outcomes':
        evaluation['evaluations'][1]['by_state']['11']['counts']['success'] += 1
    elif changed == 'config':
        path = baseline/'raw/joint/observed-runtime/serve.yaml'
        config = REVIEW.read(path)
        config['runtime']['publication_mode'] = 'windowed'
        write(path, config)
    elif changed == 'config-command':
        path = baseline/'raw/joint/observed-runtime/replay-command.json'
        command = REVIEW.read(path)
        command['argv'][3] = '/saved/toolchain/other/serve.yaml'
        write(path, command)
    elif changed == 'unknown-reuse':
        path = baseline/'forecasts.json'
        forecasts = REVIEW.read(path)
        forecasts['raw']['browse']['reason'] = 'relabelled_unknown'
        write(path, forecasts)
        evaluation['evaluations'][1]['reason'] = 'relabelled_unknown'
    if changed != 'unfrozen':
        # Rebind the saved hash chain as a changed producer could. The reader
        # must reject the substantive inconsistency, not merely a stale digest.
        for variant in ('raw', 'network_scope'):
            out = baseline/variant
            replay_path = out/'joint/observed-runtime/replay-command.json'
            replay = REVIEW.read(replay_path)
            sequence_path = replay_path.parent/'accepted-request-sequence.jsonl'
            sequence = [json.loads(line) for line in sequence_path.read_text().splitlines()]
            replay['accepted_request_sequence'].update(sha256=digest(sequence_path), bytes=sequence_path.stat().st_size)
            replay['accepted_ingest_requests'] = [{key: value for key, value in row.items() if key != 'storage_form'} for row in sequence]
            write(replay_path, replay)
            proof_path = out/'union-proof.json'
            proof = REVIEW.read(proof_path)
            for claim in proof['files'].values():
                claim['sha256'] = digest(root/claim['path'].split('/saved/', 1)[1])
            write(proof_path, proof)
            provenance_path = out/'provenance.json'
            provenance = REVIEW.read(provenance_path)
            provenance['union']['proof']['sha256'] = digest(proof_path)
            provenance['union']['model']['sha256'] = digest(out/'union-model.json')
            write(provenance_path, provenance)
            manifest_path = baseline/'manifest.json'
            manifest = REVIEW.read(manifest_path)
            manifest['variants'][variant] = provenance
            write(manifest_path, manifest)
        freeze['sha256_by_path'].update({path.relative_to(root).as_posix(): digest(path)
                                        for path in root.rglob('*') if path.is_file()})
    else:
        del freeze['sha256_by_path']['toolchain/context-baseline/manifest.json']
    with pytest.raises(ValueError):
        REVIEW.context_baseline_facts(*args)


def fixture(tmp_path: Path, *, available: bool = True):
    compact, full = tmp_path / "compact", tmp_path / "full"
    declaration = {
        "collector": "obi", "system": "otel_demo", "mode": "partial", "seed": 6,
        "run_id": 123, "head_sha": "a" * 40,
        "compact_artifact_name": "v5-summary-obi-main-otel_demo-partial-6-123",
    }
    evaluations = [{
        "source": "ebpf", "variant": "raw", "operation": "browse",
        "available": available,
        "reason": None if available else "arbitrary_saved_unknown_reason",
        "prediction": 0.123 if available else None,
        "forecast_interval": [0.12, 0.13] if available else [0, 1],
        "graph_sha256": None,
        "actual_counts": {"success": 17, "failure": 2, "unknown": 1, "total": 20},
    }]
    evaluation = {
        "integrity": {"valid": True}, "completeness": {"valid": True},
        "complete_for_evaluation": True,
        "counts": {"primary": 34800, "target": 9600, "blocks": 19},
        "acquisition": {"valid": True, "problems": [], "final_drain": {
            "technical_complete": True, "technical_valid": True,
            "accepted_receiver_bytes_closed_and_hashed": True}},
        "evaluations": evaluations, "manual_baselines": {"saved": True},
        "cost": {"seconds": 4},
    }
    status = {**{key: declaration[key] for key in ("collector", "system", "mode", "seed")},
              "run_id": "123", "commit": "a" * 40}
    forecasts = {"ebpf": {"raw": {"browse": {
        "available": available, "reason": evaluations[0]["reason"],
        "prediction": evaluations[0]["prediction"],
        "interval": evaluations[0]["forecast_interval"],
    }}}}
    freeze_map = {}
    compact_values = {
        "evaluation-v5.json": evaluation, "status.json": status,
        "plans.json": {}, "census.json": {},
        "blocks.json": [{"phase": "target", "started_ns": 20}],
        "freeze-integrity.json": {"all_unchanged": True, "sha256_by_path": freeze_map},
        "toolchain/forecasts.json": forecasts, "evidence-v4.json": {},
    }
    for name, value in compact_values.items():
        write(compact / name, value)
    manifest_hashes = {name: digest(compact / name) for name in compact_values}
    manifest_hashes["attempt-journal.jsonl"] = "b" * 64
    write(compact / "evaluation-manifest.json", {
        "commit": "a" * 40, "run_id": "123", "files_sha256": manifest_hashes})

    write(full / "forecast-saved.json", {"saved_ns": 10, "sha256_by_path": freeze_map})
    write(full / "toolchain-build/toolchain-build.json", {"binaries": [
        {"name": name, "commit": commit} for name, commit in REVIEW.PINS.items()]})
    write(full / "toolchain/forecasts.json", forecasts)
    write(full / "toolchain/inputs/ebpf/raw/observations.json", {
        "observations": 1, "exports": [{
            "path": "/saved/toolchain/inputs/ebpf/raw/export.pb",
            "sha256": "c" * 64}]})
    write(full / "toolchain/discovery/ebpf/raw/observed-runtime/replay-command.json", {
        "returncode": 0, "status": "complete", "source_domain": "fixture-domain",
        "source_profile": {"source_id": "ebpf", "input_type": "ebpf-otlp"},
        "clock_admission_filter": False,
        "ingest": {"spans": 1, "dropped_spans": 0, "late_spans": 0},
        "accepted_ingest_requests": [{"content_sha256": "c" * 64, "http_status": 200}]})
    observed_model = {"services": [], "edges": [], "endpoints": []}
    write(full / "toolchain/discovery/ebpf/raw/observed.json", observed_model)
    write(full / "toolchain/discovery/ebpf/raw/observed.snapshot.json", {
        "model": observed_model})
    write(full / "toolchain/procrustes/ebpf/browse/0/preflight.command.json", {
        "returncode": 0, "argv": ["procrustes", "--collection-source", "ebpf-otlp"]})
    write(full / "toolchain/procrustes/native/browse/0/preflight.command.json", {
        "returncode": 0, "argv": ["procrustes", "analyze", "--source", "deployment-0=x"]})
    branch = full / "toolchain/ebpf/raw/browse"
    if available:
        write(branch / "simulation.command.json", {"returncode": 0})
        write(branch / "model.json", observed_model)
    write(full / "observations/drain-evidence.json", {
        "technical_complete": True, "technical_valid": True,
        "accepted_receiver_bytes_closed_and_hashed": True})
    write(full / "observations/collector.json", {
        "collector": "obi", "technical_valid": True, "closed_checkpoint": True,
        "nodes": ["a", "b"], **REVIEW.COLLECTOR_PINS["obi"]})
    for node in ("a", "b", "native"):
        write(full / f"observations/receiver-closed-{node}.json", {
            "node": node, "saved_bytes_valid": True,
            "in_flight_handlers_joined": True, "listening_socket_closed": True,
            "wrapper_json_decode_error_count": 0, "errors_json_decode_error_count": 0,
            "receiver_parse_or_read_failure_count": 0})
    write(full / "observations/technical-positive-control.json", {
        "collector": "obi", "marker": "marker-123", "cleanup_verified": True,
        "cleanup_failures": [], "proofs": {}})
    control = json.loads((full / "observations/technical-positive-control.json").read_text())
    for node in ("a", "b"):
        request = ExportTraceServiceRequest()
        resource = request.resource_spans.add()
        for key, value in {
            "telemetry.distro.name": "opentelemetry-ebpf-instrumentation",
            "telemetry.distro.version": "v0.15.2",
            "container.name": f"study-ebpf-control-server-{node}",
        }.items():
            attribute = resource.resource.attributes.add()
            attribute.key = key
            attribute.value.string_value = value
        scoped = resource.scope_spans.add()
        scoped.scope.name = "go.opentelemetry.io/obi"
        span = scoped.spans.add()
        marker_attribute = span.attributes.add()
        marker_attribute.key = "x-experiment-request-id"
        marker_attribute.value.string_value = "marker-123"
        body = full / f"observations/{node}.raw/body.pb"
        write(body, request.SerializeToString())
        control["proofs"][node] = {
            "raw_ref": f"{node}.raw/body.pb", "raw_sha256": digest(body)}
    write(full / "observations/technical-positive-control.json", control)
    write(full / "deployment/otel_demo/runtime-resolved-node-a.yaml", {
        "services": {"frontend": {"environment": {}},
                     "product-catalog-a": {
                         "environment": {"OTEL_SDK_DISABLED": "true"}}}})
    write(full / "deployment/otel_demo/runtime-resolved-node-b.yaml", {
        "services": {"product-catalog-b": {
            "environment": {"OTEL_SDK_DISABLED": "true"}}}})
    for stage in ("training", "final"):
        write(full / f"native/{stage}/native-metadata.json", {
            "mode": "partial", "actual_census": {"malformed_records": 0, "spans": 1},
            "mode_compliance": {"compliant": True}})
    freeze_map.update({
        "toolchain/inputs/ebpf/raw/export.pb": "c" * 64,
        **{f"toolchain/{path.relative_to(full / 'toolchain').as_posix()}": digest(path)
           for path in (branch / "simulation.command.json", branch / "model.json")
           if path.is_file()}})
    worker_claim = {"bytes": (full / "toolchain/forecasts.json").stat().st_size,
                    "sha256": digest(full / "toolchain/forecasts.json")}
    freeze_map["toolchain/forecasts.json"] = worker_claim["sha256"]
    identity = {"run_id": "123", "system": "otel_demo", "mode": "partial",
                "seed": 6, "commit": "a" * 40}
    remote = full / "infrastructure/remote-toolchain-v4"
    write(remote / "parent-import.json", {
        "identity": identity, "worker_run_id": "456",
        "downloaded_archive_sha256": "d" * 64,
        "worker_artifact_digest": "sha256:" + "d" * 64})
    write(remote / "worker/worker-provenance.json", {
        "identity": identity, "worker_run_id": "456",
        "checkpoint_unchanged": True, "new_application_traffic": False,
        "toolchain_files": {"forecasts.json": worker_claim}})
    write(remote / "worker/worker-status.json", {
        "identity": {**identity, "worker_run_id": "456"}, "status": "complete",
        "checkpoint_unchanged": True, "new_application_traffic": False})
    write(remote / "worker/output-manifest.json", {
        "identity": identity, "toolchain_files": {"forecasts.json": worker_claim}})
    write(remote / "training-index-proof.json", {
        "checkpoint": {"sha256": "e" * 64},
        "parent_before_dispatch": {"sha256": "e" * 64},
        "parent_after_worker": {"sha256": "e" * 64}})
    write(compact / "freeze-integrity.json", {
        "all_unchanged": True, "sha256_by_path": freeze_map})
    write(full / "forecast-saved.json", {"saved_ns": 10, "sha256_by_path": freeze_map})
    manifest_hashes["freeze-integrity.json"] = digest(compact / "freeze-integrity.json")
    write(compact / "evaluation-manifest.json", {
        "commit": "a" * 40, "run_id": "123", "files_sha256": manifest_hashes})
    files = {}
    for path in full.rglob("*"):
        if path.is_file():
            files[path.relative_to(full).as_posix()] = {
                "bytes": path.stat().st_size, "sha256": digest(path), "zip_crc32": "00000000"}
    write(full / "selected-transport-proof.json", {
        "complete": True, "scientific_processing_performed": False,
        "artifact": {"name": "campaign-v5-obi-main-otel_demo-partial-6-123",
                     "expired": False,
                     "workflow_run": {"id": 123, "head_sha": "a" * 40}},
        "files": files,
    })
    return declaration, compact, full


@pytest.mark.parametrize("available", [True, False])
def test_saved_availability_is_observed_not_a_fixed_gate(tmp_path: Path, available: bool) -> None:
    declaration, compact, full = fixture(tmp_path, available=available)
    result = REVIEW.review(declaration, compact, full, tmp_path / "out")
    branch = result["full_facts"]["saved_branch_facts"][0]
    assert branch["available_copied"] is available
    assert branch['binding_summary'] == {'path': 'toolchain/ebpf/raw/browse/binding.json', 'present': False}
    assert result["availability_outcome_or_accuracy_used_as_gate"] is False
    assert result["independent_admission_performed"] is False
    assert result["compact_facts"]["evaluations_copied_not_recomputed"][0]["actual_counts"]["success"] == 17


def test_available_saved_branch_requires_actual_sheaft_command_and_model(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path, available=True)
    (full / "toolchain/ebpf/raw/browse/model.json").unlink()
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    proof["files"].pop("toolchain/ebpf/raw/browse/model.json")
    write(full / "selected-transport-proof.json", proof)
    with pytest.raises(ValueError, match="lacks successful Sheaft"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_control_requires_selected_agent_proof_on_both_guests(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    control_path = full / "observations/technical-positive-control.json"
    control = json.loads(control_path.read_text())
    control["proofs"].pop("b")
    write(control_path, control)
    proof_path = full / "selected-transport-proof.json"
    proof = json.loads(proof_path.read_text())
    proof["files"]["observations/technical-positive-control.json"].update(
        bytes=control_path.stat().st_size, sha256=digest(control_path))
    write(proof_path, proof)
    with pytest.raises(ValueError, match="exact two-node"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_unavailable_saved_branch_retains_attempted_command_truthfully(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path, available=False)
    write(full / "toolchain/ebpf/raw/browse/simulation.command.json", {"returncode": 7})
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    path = full / "toolchain/ebpf/raw/browse/simulation.command.json"
    proof["files"][path.relative_to(full).as_posix()] = {
        "bytes": path.stat().st_size, "sha256": digest(path), "zip_crc32": "00000000"}
    write(full / "selected-transport-proof.json", proof)
    result = REVIEW.review(declaration, compact, full, tmp_path / "out")
    assert result["full_facts"]["saved_branch_facts"][0]["saved_command_returncode"] == 7


def test_dsb_native_manifest_uses_application_audit_trace_policy(tmp_path: Path) -> None:
    declaration = {"system": "deathstarbench", "mode": "absent"}
    for stage in ("training", "final"):
        write(tmp_path / f"native/{stage}/manifest.json", {
            "mode": "absent", "errors": [], "absence_verified": True,
            "application_trace_count": 0, "audit_self_trace_count": 1,
            "audit_self_trace_provenance": {
                "excluded_service_exact_match": "jaeger-all-in-one",
                "raw_responses_retained": True}})
    facts = REVIEW.native_mode_facts(tmp_path, declaration, {
        "acquisition": {"native_observations_by_service": {"jaeger-all-in-one": 1}}})
    assert facts["training"]["application_trace_count"] == 0
    assert facts["final"]["audit_self_trace_count"] == 1


def test_older_otel_absent_suppression_audit_shape_is_verified(tmp_path: Path) -> None:
    declaration = {"system": "otel_demo", "mode": "absent"}
    audit = {"mode": "absent", "mode_compliant": True,
             "malformed_records": 0, "exporter_records": 0,
             "span_markers": 0, "trace_file_bytes": 0,
             "trace_file_sha256": hashlib.sha256(b"").hexdigest()}
    for stage in ("training", "final"):
        write(tmp_path / f"native/{stage}/native-suppression-verification.json", audit)
    facts = REVIEW.native_mode_facts(
        tmp_path, declaration,
        {"acquisition": {"native_observations_by_service": {}}})
    assert facts["training"]["schema"] == "native-suppression-verification"
    assert facts["final"]["saved_audit"]["trace_file_bytes"] == 0


def test_otel_rendered_sdk_settings_follow_pinned_adapter_omission_convention() -> None:
    partial = {"frontend": None, "product-catalog": None,
               "product-catalog-a": "true", "product-catalog-b": "true"}
    assert REVIEW.validate_otel_demo_sdk_settings(partial, "partial") == ["true", "true"]
    full = {service: None for service in partial}
    assert REVIEW.validate_otel_demo_sdk_settings(full, "full") == []
    absent = {"frontend": "true", "product-catalog-a": "true",
              "product-catalog-b": "true", "otel-collector": None,
              "product-catalog": None}
    assert REVIEW.validate_otel_demo_sdk_settings(absent, "absent") == [
        "true", "true", "true"]


def test_otel_partial_rendered_sdk_settings_reject_unexpected_enabled_service_true() -> None:
    with pytest.raises(ValueError, match="differs from declared mode"):
        REVIEW.validate_otel_demo_sdk_settings({
            "frontend": "true", "product-catalog-a": "true",
            "product-catalog-b": "true"}, "partial")


def test_otel_rendered_sdk_settings_require_both_controlled_replicas() -> None:
    with pytest.raises(ValueError, match="lacks a controlled product-catalog replica"):
        REVIEW.validate_otel_demo_sdk_settings({
            "frontend": None, "product-catalog-a": None}, "full")


def test_native_preflight_retains_deployment_only_argv_contract(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    result = REVIEW.review(declaration, compact, full, tmp_path / "out")
    assert "procrustes/native/browse/0/preflight.command.json" in (
        result["full_facts"]["actual_procrustes"])


def test_untyped_worker_claims_verify_only_retained_frozen_selection(tmp_path: Path) -> None:
    toolchain = tmp_path / "toolchain"
    selected = toolchain / "forecasts.json"
    write(selected, {"saved": True})
    claims = {
        "forecasts.json": {"bytes": selected.stat().st_size, "sha256": digest(selected)},
        "unselected.bin": {"bytes": 99, "sha256": "f" * 64},
    }
    proof = REVIEW.verify_worker_output_claims(
        claims, dict(claims), {}, toolchain,
        {"sha256_by_path": {"toolchain/forecasts.json": digest(selected)}})
    assert proof["scope"] == "selected_untyped_outputs_only"
    assert proof["verified_selected_paths"] == ["forecasts.json"]
    assert proof["unselected_claims"] == ["unselected.bin"]
    assert proof["whole_worker_tree_verified"] is False


def test_full_only_reuse_binds_untyped_claims_to_saved_freeze_and_marks_external_compact(
        tmp_path: Path) -> None:
    declaration, _compact, full = fixture(tmp_path)
    result = REVIEW.review(declaration, None, full, tmp_path / "out")
    scope = result["full_facts"]["worker_import_facts"]["output_claim_scope"]
    assert scope["scope"] == "selected_untyped_outputs_only"
    assert scope["verified_selected_paths"] == ["forecasts.json"]
    assert scope["freeze_map_binding"] == (
        "selected_claims_match_forecast_saved; compact_freeze_comparison_external_pending")
    assert result["compact_facts"] is None


def test_fixed_identity_and_order_remain_gates(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    saved = json.loads((full / "forecast-saved.json").read_text())
    saved["saved_ns"] = 21
    write(full / "forecast-saved.json", saved)
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    path = full / "forecast-saved.json"
    proof["files"]["forecast-saved.json"].update(bytes=path.stat().st_size, sha256=digest(path))
    write(full / "selected-transport-proof.json", proof)
    with pytest.raises(ValueError, match="does not precede"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_selection_is_family_scope_not_outcome_scope() -> None:
    assert SELECT.wanted_member("evaluation-v5.json", "compact")
    assert not SELECT.wanted_member("attempt-journal.jsonl", "compact")
    assert SELECT.wanted_member("toolchain/static-inputs.json", "input-supplement")
    assert SELECT.wanted_member(
        "toolchain/inputs/combined/network_scope/observations.json", "input-supplement")
    assert SELECT.wanted_member(
        "runtime-identity-v5/supplied-alias-scope-final.json", "full")
    assert SELECT.wanted_member("toolchain/ebpf/raw/browse/model.json", "full")
    assert not SELECT.wanted_member("unrelated/raw-journal.jsonl", "full")


def test_fixed_declaration_has_exact_coverage_scopes() -> None:
    declaration = json.loads((ROOT / "docs/iteration5-main-review-candidates.json").read_text())
    cells = declaration["cells"]
    qualification = declaration["qualification_cells"]
    assert len(cells) == 17
    assert len({(x["run_id"], x["collector"], x["system"], x["mode"], x["seed"])
                for x in cells}) == 17
    assert sum(x["compact_scope"] == "retrieve_selected_nonjournal" for x in cells) == 8
    assert sum(x["compact_scope"] == "reuse_existing_verified_facts" for x in cells) == 9
    assert sum(x["full_scope"] == "retrieve_input_supplement" for x in cells) == 2
    assert sum(x["full_scope"] == "reuse_existing_selected" for x in cells) == 1
    assert [(x["collector"], x["system"]) for x in qualification] == [
        ("obi", "otel_demo"), ("obi", "deathstarbench"), ("coroot", "petclinic")]
    assert all(len(x["manual_review_restored_sha256"]) == 64 for x in qualification)
    assert all(x["full_artifact_id"] > 0 and x["full_artifact_bytes"] > 0
               and len(x["full_artifact_digest"]) == 71 for x in qualification)


def test_future_candidate_manifest_is_exact_three_fixed_coroot_pc_full_cells() -> None:
    path = ROOT / "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    declaration = json.loads(path.read_text())
    cells = declaration["cells"]
    assert [(row["collector"], row["system"], row["mode"], row["seed"])
            for row in cells] == [
                ("coroot", "petclinic", "full", 6),
                ("coroot", "petclinic", "full", 7),
                ("coroot", "petclinic", "full", 8)]
    assert {row["run_id"] for row in cells} == {41004291277}
    assert {row["head_sha"] for row in cells} == {
        "c5df32ffc3039136c184b7915337836c39db811f"}
    assert all(row["compact_scope"] == "retrieve_selected_nonjournal"
               and row["full_scope"] == "retrieve_family_selected"
               and row["compact_artifact_digest"].startswith("sha256:")
               and row["full_artifact_digest"].startswith("sha256:")
               for row in cells)


def _run_manifest_selector(tmp_path: Path, manifest: str, *, phase: str = "pending17",
                           document: dict | None = None, fresh_go: bool = True):
    workflow = (ROOT / ".github/workflows/review-pending-main-evidence-v5.yml").read_text()
    script = textwrap.dedent(
        workflow.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0])
    source = ROOT / "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    target = tmp_path / ('docs/clean-study-smoke-review-candidates-20261031.json' if phase == 'common-smoke'
                         else 'docs/iteration5-main-review-candidates-coroot-petclinic-full.json')
    target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    if document is not None:
        target.write_text(json.dumps(document))
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "docs"], cwd=tmp_path, check=True)
    output = tmp_path / "github-output.txt"
    environment = os.environ | {
        "PHASE": phase, "QUALIFICATION_SYSTEM": "all",
        "CANDIDATE_MANIFEST": manifest, "PENDING17_GO": "true",
        "FRESH_GO": str(fresh_go).lower(),
        "GITHUB_OUTPUT": str(output)}
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=tmp_path, env=environment,
        text=True, capture_output=True)
    return result, output


def test_pending_manifest_selector_binds_exact_tracked_manifest_and_three_cells(
        tmp_path: Path) -> None:
    name = "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    result, output = _run_manifest_selector(tmp_path, name)
    assert result.returncode == 0, result.stderr
    values = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert len(json.loads(values["matrix"])["cell"]) == 3
    assert values["candidate_manifest"] == name
    assert len(values["candidate_manifest_sha256"]) == 64
    assert len(values["candidate_manifest_git_blob"]) == 40


@pytest.mark.parametrize(("manifest", "phase", "message"), [
    ("docs/iteration5-main-review-candidates-coroot-petclinic-full.json",
     "qualification", "qualification requires the original candidate manifest"),
    ("../outside.json", "pending17",
     "candidate_manifest must be a normalized repo-relative docs/*.json path"),
])
def test_candidate_manifest_scope_is_fail_closed(
        tmp_path: Path, manifest: str, phase: str, message: str) -> None:
    result, _ = _run_manifest_selector(tmp_path, manifest, phase=phase)
    assert result.returncode != 0
    assert message in result.stderr


def test_candidate_manifest_invalid_scope_is_rejected(tmp_path: Path) -> None:
    name = "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    document = json.loads((ROOT / name).read_text())
    document["cells"][0]["full_scope"] = "unreviewed_whole_archive"
    result, _ = _run_manifest_selector(tmp_path, name, document=document)
    assert result.returncode != 0
    assert "candidate manifest has a malformed cell or invalid scope" in result.stderr


def test_selected_transport_identity_and_member_hash_fail_closed(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    proof["artifact"]["workflow_run"]["head_sha"] = "f" * 40
    write(full / "selected-transport-proof.json", proof)
    with pytest.raises(ValueError, match="identity/integrity"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_failed_selected_transport_retains_cost_and_failure_phase(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class FailedRemote:
        verified_received_bytes = 17
        attempted_received_bytes = 23
        failures = [{"attempt": 1, "error_type": "fixture"}]

        def __init__(self, metadata, out):
            pass

    monkeypatch.setattr(SELECT, "RemoteZip", FailedRemote)
    monkeypatch.setattr(SELECT.zipfile, "ZipFile",
                        lambda remote: (_ for _ in ()).throw(SELECT.zipfile.BadZipFile()))
    metadata = {"id": 1, "name": "a", "size_in_bytes": 2,
                "digest": "sha256:" + "a" * 64, "expired": False,
                "workflow_run": {"id": 3, "head_sha": "b" * 40}}
    expected = {**{key: metadata[key] for key in ("id", "name", "size_in_bytes", "digest")},
                "run_id": 3, "head_sha": "b" * 40}
    with pytest.raises(SELECT.zipfile.BadZipFile):
        SELECT.select(metadata, expected, "compact", tmp_path / "selected")
    proof = json.loads((tmp_path / "selected/selected-transport-proof.json").read_text())
    assert proof["complete"] is False
    assert proof["failure"] == {
        "phase": "selected_member_transport", "error_type": "BadZipFile"}
    assert proof["range_verified_received_bytes"] == 17
    assert proof["range_attempted_received_bytes"] == 23


def test_typed_package_stream_verifies_every_file_and_selects_method_bytes(tmp_path: Path) -> None:
    package, selected = tmp_path / "package", tmp_path / "selected"
    package.mkdir()
    bodies = {"forecasts.json": b"{}\n", "unselected/raw.bin": b"raw-evidence"}
    archive = package / "payload.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for name, body in bodies.items():
            info = tarfile.TarInfo(name)
            info.size = len(body)
            import io
            bundle.addfile(info, io.BytesIO(body))
    rows = [{"path": name, "type": "file", "bytes": len(body),
             "sha256": hashlib.sha256(body).hexdigest()} for name, body in bodies.items()]
    write(package / "payload.manifest.jsonl", "".join(json.dumps(row) + "\n" for row in rows).encode())
    write(package / "transport.json", {"kind": "toolchain",
        "archive_bytes": archive.stat().st_size, "archive_sha256": digest(archive),
        "manifest_sha256": digest(package / "payload.manifest.jsonl")})
    proof = REVIEW.verify_package(package, selected, kind="toolchain")
    assert proof["all_files_verified"] == 2
    assert (selected / "forecasts.json").is_file()
    assert not (selected / "unselected/raw.bin").exists()


def test_handoff_selection_retains_complete_small_identity_tree() -> None:
    assert REVIEW._package_selected("parent-import.json", "handoff")
    assert REVIEW._package_selected("training-index-proof.json", "handoff")
    assert REVIEW._package_selected("worker/worker-provenance.json", "handoff")
    assert REVIEW._package_selected("worker/worker-status.json", "handoff")
    assert REVIEW._package_selected("worker/output-manifest.json", "handoff")


def test_workflow_and_checker_never_emit_admission_verdict() -> None:
    workflow = (ROOT / ".github/workflows/review-pending-main-evidence-v5.yml").read_text()
    checker = (ROOT / "scripts/review-main-saved-facts-v5.py").read_text()
    assert "independent_admission_performed\": False" in checker
    assert "availability_outcome_or_accuracy_used_as_gate\": False" in checker
    assert "0.875" not in checker
    assert "scientific_GO" not in workflow
    assert "default: qualification" in workflow
    assert "qualification_system:" in workflow
    assert "if qualification_system!='all':" in workflow
    assert "qualification_system must be all for pending17" in workflow
    assert "default: docs/iteration5-main-review-candidates.json" in workflow
    assert "qualification requires the original candidate manifest" in workflow
    assert "candidate_manifest must be a normalized repo-relative docs/*.json path" in workflow
    assert "candidate manifest has a malformed cell or invalid scope" in workflow
    assert "candidate-manifest.json" in workflow
    assert "pending17 requires explicit post-qualification independent GO" in workflow


def indexed_fixture(root: Path):
    freeze = {"sha256_by_path": {}}

    def reference(name, value):
        path = root / name
        write(path, value)
        freeze["sha256_by_path"]["toolchain/" + name] = digest(path)
        return {"path": "/saved/toolchain/" + name, "bytes": path.stat().st_size,
                "sha256": digest(path)}

    def request(order, code, source="ebpf"):
        return {"request_order": order, "sha256": str(code) * 64, "source": source,
                "observations": 1, "content_type": "application/json"}

    ordinary = {**request(2, 2), "path": "/saved/toolchain/inputs/ordinary.json"}
    native = {**request(1, 4, "native"), "path": "/saved/toolchain/inputs/native.json"}
    for row in (ordinary, native):
        freeze["sha256_by_path"]["toolchain/" + REVIEW.toolchain_relative(row["path"])] = row["sha256"]
    rows = [{**request(order, code), "shard": 0, "offset": index * 10, "length": 10}
            for index, (order, code) in enumerate(((1, 1), (3, 3)))]
    index = reference("inputs/ebpf/raw/exports/ebpf-request-index.jsonl",
                      ("\n".join(json.dumps(row) for row in rows) + "\n").encode())
    shard = {"path": "/saved/toolchain/inputs/shard.bin", "bytes": 20, "sha256": "a" * 64}
    freeze["sha256_by_path"]["toolchain/inputs/shard.bin"] = shard["sha256"]
    ebpf = {"observations": 3, "exports": [ordinary], "stream_exports": [{
        "schema_version": "deepflow-request-archive-v5", "source": "ebpf",
        "requests": 2, "observations": 2, "wire_bytes": 20,
        "request_index": index, "shards": [shard]}]}
    groups = [reference("inputs/ebpf/raw/observations.json", ebpf),
              reference("inputs/native/raw/observations.json", {"observations": 1, "exports": [native]})]
    manifest = {"observations": 4, "ordered_request_group_manifests": groups}
    accepted = [{"http_status": 200, "export_index": index, "content_bytes": 10,
                 "content_sha256": str(index + 1) * 64,
                 "endpoint": "/v1/traces" if index == 3 else "/sources/ebpf/v1/traces",
                 "storage_form": "stream_archive_slice" if index in (0, 2) else "ordinary_export"}
                for index in range(4)]
    sequence = reference("discovery/combined/raw/observed-runtime/accepted-request-sequence.jsonl",
                         ("\n".join(json.dumps(row) for row in accepted) + "\n").encode())
    sequence.update(requests=4, same_order_as_original_request_ordinals_and_source_groups=True)
    plain = lambda row: {key: value for key, value in row.items() if key != "storage_form"}
    stream_proof = reference("discovery/combined/raw/observed-runtime/accepted-stream-requests.jsonl",
                             ("\n".join(json.dumps(plain(accepted[i])) for i in (0, 2)) + "\n").encode())
    stream_proof.update(requests=2, same_http_body_order_as_request_index=True)
    replay = {"accepted_request_sequence": sequence, "accepted_stream_requests": stream_proof,
              "accepted_ingest_requests": [plain(accepted[i]) for i in (1, 3)]}
    return manifest, replay, freeze


def test_stream_and_ordinary_requests_preserve_group_order_and_ordinal_reset(tmp_path: Path) -> None:
    manifest, replay, freeze = indexed_fixture(tmp_path)
    facts = REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)
    assert (facts["accepted_inputs"], facts["ordinary_requests"], facts["streamed_requests"]) == (4, 2, 2)
    assert facts["unselected_wire_payloads_independently_rehashed"] is False
    manifest["ordered_request_group_manifests"].reverse()
    with pytest.raises(ValueError, match="differs from saved source order"):
        REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)


def test_stream_metadata_must_be_frozen_even_when_downloaded_hash_matches(tmp_path: Path) -> None:
    manifest, replay, freeze = indexed_fixture(tmp_path)
    freeze["sha256_by_path"]["toolchain/inputs/ebpf/raw/exports/ebpf-request-index.jsonl"] = "0" * 64
    with pytest.raises(ValueError, match="metadata is not frozen"):
        REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)


def test_acceptance_subsets_cannot_omit_stream_requests(tmp_path: Path) -> None:
    manifest, replay, freeze = indexed_fixture(tmp_path)
    replay["accepted_ingest_requests"].pop()
    with pytest.raises(ValueError, match="ordinary acceptance subset"):
        REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)


@pytest.mark.parametrize("signal,marker,valid", [("EBPF", "control-123", True),
                                               ("Packet", "control-123", False),
                                               ("EBPF", "other", False)])
def test_deepflow_control_uses_exact_raw_record_origin_and_marker(
        tmp_path: Path, signal: str, marker: str, valid: bool) -> None:
    body = json.dumps({"signal_source": signal, "l7_protocol": "Http1",
                       "tap_side": "ServerProcess", "request_resource": "/" + marker}).encode()
    name = "deepflow-raw/node-a/001-positive-control/l7_flow_log"
    path = tmp_path / "observations" / name
    write(path, b"preceding\n" + body + b"\nfollowing\n")
    write(path.parent / "snapshot.json", {"node": "a", "files": [{
        "snapshot_name": "l7_flow_log", "copied_bytes": path.stat().st_size,
        "copied_sha256": digest(path)}]})
    claim = {"raw_file": "/saved/observations/" + name, "raw_offset": 10,
             "raw_length": len(body), "raw_sha256": hashlib.sha256(body).hexdigest(),
             "proven": True, "protocol": "Http1", "tap_side": "ServerProcess"}
    if valid:
        facts = REVIEW.deepflow_control_facts(tmp_path, {"marker": "control-123"}, "a", claim)
        assert facts["raw_offset"] == 10
    else:
        with pytest.raises(ValueError, match="raw eBPF HTTP origin and marker"):
            REVIEW.deepflow_control_facts(tmp_path, {"marker": "control-123"}, "a", claim)


def test_fresh_selector_keeps_index_and_acceptance_metadata_without_wire_shards() -> None:
    for name in ("inputs/ebpf/raw/exports/ebpf-request-index.jsonl",
                 "discovery/combined/raw/observed-runtime/accepted-request-sequence.jsonl",
                 "discovery/combined/raw/observed-runtime/accepted-stream-requests.jsonl"):
        assert SELECT.wanted_member("toolchain/" + name, "full")
        assert REVIEW._package_selected(name, "toolchain")
    assert not SELECT.wanted_member("toolchain/inputs/ebpf/raw/exports/ebpf-requests-000001.bin", "full")


def test_fresh_qualification_requires_main_source_and_all_three_fixed_families(tmp_path: Path) -> None:
    name = "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    cells = []
    for collector, system, mode, run_id in (("deepflow", "deathstarbench", "absent", 1),
                                           ("coroot", "otel_demo", "full", 2),
                                           ("obi", "petclinic", "partial", 3)):
        row = json.loads((ROOT / name).read_text())["cells"][0]
        row.update(collector=collector, system=system, mode=mode, seed=6, run_id=run_id,
                   head_sha=REVIEW.FRESH_HEAD, stage="main", runner="study")
        cells.append(row)
    result, output = _run_manifest_selector(tmp_path, name, phase="fresh-qualification",
                                            document={"cells": cells})
    assert result.returncode == 0, result.stderr
    values = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert len(json.loads(values["matrix"])["cell"]) == 3


@pytest.mark.parametrize('cell_key,accepted', [
    (('deepflow', 'otel_demo', 'absent', 6), True),
    (('deepflow', 'otel_demo', 'full', 8), True),
    (('deepflow', 'otel_demo', 'full', 6), False),
    (('deepflow', 'otel_demo', 'full', 7), False),
    (('coroot', 'otel_demo', 'absent', 6), False),
])
def test_closed_job_fresh_batch_preserves_seven_case_scope(tmp_path, cell_key, accepted):
    name = 'docs/iteration5-main-review-candidates-coroot-petclinic-full.json'
    template = json.loads((ROOT/name).read_text())['cells'][0]
    planned = [{**template, 'collector': collector, 'system': system, 'mode': mode,
                'seed': seed, 'run_id': 1, 'head_sha': REVIEW.FRESH_HEAD,
                'stage': 'main', 'runner': 'study'}
               for collector in ('obi', 'deepflow', 'coroot')
               for system in ('deathstarbench', 'otel_demo', 'petclinic')
               for mode in ('absent', 'partial', 'full') for seed in (6, 7, 8)]
    cell = next(row for row in planned if
        tuple(row[key] for key in ('collector', 'system', 'mode', 'seed')) == cell_key)
    cell['head_sha'] = REVIEW.CLOSED_POSTCAPTURE_HEAD
    result, _ = _run_manifest_selector(tmp_path, name, phase='fresh-batch',
        document={'cells': [cell], 'planned_cells': planned}, fresh_go=True)
    assert (result.returncode == 0) is accepted, result.stderr


@pytest.mark.parametrize('cell_key,accepted', [
    (('deepflow','otel_demo','absent',6),True),
    (('deepflow','otel_demo','absent',7),True),
    (('deepflow','otel_demo','absent',8),True),
    (('deepflow','otel_demo','partial',6),False),
    (('deepflow','petclinic','absent',6),False),
    (('coroot','otel_demo','absent',6),False),
])
@pytest.mark.parametrize('head', [REVIEW.IDENTICAL_INPUT_DISCOVERY_SOURCE['revision'], REVIEW.UPLOAD_HOLD_PARENT_PROOF_HEAD])
def test_identical_input_source_is_limited_to_its_original_cells(tmp_path,cell_key,accepted,head):
    name='docs/iteration5-main-review-candidates-coroot-petclinic-full.json'
    template=json.loads((ROOT/name).read_text())['cells'][0]
    planned=[{**template,'collector':c,'system':s,'mode':m,'seed':z,'run_id':1,
              'head_sha':REVIEW.FRESH_HEAD,'stage':'main','runner':'study'}
             for c in ('obi','deepflow','coroot') for s in ('deathstarbench','otel_demo','petclinic')
             for m in ('absent','partial','full') for z in (6,7,8)]
    cell=next(r for r in planned if tuple(r[k] for k in ('collector','system','mode','seed'))==cell_key)
    cell['head_sha']=head
    if head == REVIEW.UPLOAD_HOLD_PARENT_PROOF_HEAD and cell_key == ('deepflow','otel_demo','absent',7):
        accepted=False
    result,_=_run_manifest_selector(tmp_path,name,phase='fresh-batch',document={'cells':[cell],'planned_cells':planned},fresh_go=True)
    assert (result.returncode==0) is accepted,result.stderr


@pytest.mark.parametrize('change', ['none', 'missing_plan_cell', 'different_packet', 'no_GO', 'final_series'])
@pytest.mark.parametrize('head', [REVIEW.FRESH_HEAD, REVIEW.IMMUTABLE_PATH_HEAD, REVIEW.UPLOADED_CHECKPOINT_COPY_HEAD, REVIEW.CLOSED_FINAL_SNAPSHOT_HEAD, REVIEW.STREAMED_CHECKPOINT_HEAD, REVIEW.PETCLINIC_WORKER_HEAD, REVIEW.POSTCAPTURE_GUEST_RELEASE_HEAD])
def test_fresh_batch_is_scheduling_only_and_keeps_final81_boundary(tmp_path, change, head):
    name = 'docs/iteration5-main-review-candidates-coroot-petclinic-full.json'
    template = json.loads((ROOT/name).read_text())['cells'][0]
    planned = [{**template, 'collector': collector, 'system': system, 'mode': mode,
                'seed': seed, 'run_id': 1, 'head_sha': head,
                'stage': 'main', 'runner': 'study'}
               for collector in ('obi', 'deepflow', 'coroot')
               for system in ('deathstarbench', 'otel_demo', 'petclinic')
               for mode in ('absent', 'partial', 'full') for seed in (6, 7, 8)]
    cells = [dict(planned[0]), dict(planned[-1])]
    if change == 'missing_plan_cell':
        planned.pop(2)
    elif change == 'different_packet':
        cells[0]['run_id'] = 2
    result, output = _run_manifest_selector(
        tmp_path, name, phase='fresh-series' if change == 'final_series' else 'fresh-batch',
        document={'cells': cells, 'planned_cells': planned}, fresh_go=change != 'no_GO')
    if change == 'none':
        assert result.returncode == 0, result.stderr
        values = dict(line.split('=', 1) for line in output.read_text().splitlines())
        assert len(json.loads(values['matrix'])['cell']) == 2
    else:
        assert result.returncode != 0
        assert any(text in result.stderr for text in (
            'complete fixed 81-cell plan', 'frozen planned identity',
            'actual-output qualification GO', 'fresh series must review all 81 cells'))


@pytest.mark.parametrize('system', ['deathstarbench', 'otel_demo', 'petclinic'])
def test_explicit_smoke_review_keeps_main_workload_boundary(tmp_path, system):
    declaration, compact, _ = fixture(tmp_path)
    declaration.update(system=system, head_sha=REVIEW.FRESH_HEAD, stage='smoke', runner='study')
    from ebpf_discovery.evaluate_v5 import expected_counts
    _, workload, phases, _ = expected_counts(system, True)
    status = REVIEW.read(compact/'status.json')
    status.update(system=system, commit=REVIEW.FRESH_HEAD, smoke=True, controller='clean-study', workload_counts=workload)
    write(compact/'status.json', status)
    evaluation = REVIEW.read(compact/'evaluation-v5.json')
    evaluation.update(primary_series_result=False, smoke_technical_pass=True)
    evaluation['counts'].update(primary=sum(phases.values()), target=phases['target'],
                                blocks=19 if system == 'otel_demo' else 16)
    write(compact/'evaluation-v5.json', evaluation)
    manifest = REVIEW.read(compact/'evaluation-manifest.json')
    manifest.update(commit=REVIEW.FRESH_HEAD)
    for name in ('status.json', 'evaluation-v5.json'):
        manifest['files_sha256'][name] = digest(compact/name)
    write(compact/'evaluation-manifest.json', manifest)
    facts, _, _ = REVIEW.compact_facts(compact, declaration, smoke_qualification=True)
    assert facts['counts']['primary'] == (72 if system == 'petclinic' else 54)
    with pytest.raises(ValueError):  # The default main reader still rejects this same packet.
        REVIEW.compact_facts(compact, declaration)
    for key, value in (('head_sha', 'f60cbfe5e19ca88b40e196d8e793ef0e2aac5d5c'),
                       ('stage', 'main'), ('runner', 'legacy'), ('seed', 7)):
        with pytest.raises(ValueError):
            REVIEW.compact_facts(compact, {**declaration, key: value}, smoke_qualification=True)
    evaluation['counts']['target'] += 1
    write(compact/'evaluation-v5.json', evaluation)
    manifest['files_sha256']['evaluation-v5.json'] = digest(compact/'evaluation-v5.json')
    write(compact/'evaluation-manifest.json', manifest)
    with pytest.raises(ValueError, match='fixed workload'):
        REVIEW.compact_facts(compact, declaration, smoke_qualification=True)


@pytest.mark.parametrize('changed', [None, 'missing', 'seed', 'source', 'stage', 'run', 'planned-missing'])
def test_common_smoke_workflow_requires_all27_exact_fixed_cells(tmp_path, changed):
    template = json.loads((ROOT/'docs/iteration5-main-review-candidates-coroot-petclinic-full.json').read_text())['cells'][0]
    cells = [{**template, 'collector': c, 'system': s, 'mode': m, 'seed': 6,
              'head_sha': REVIEW.FRESH_HEAD, 'stage': 'smoke', 'runner': 'study'}
             for c in ('obi', 'deepflow', 'coroot')
             for s in ('deathstarbench', 'otel_demo', 'petclinic') for m in ('absent', 'partial', 'full')]
    planned = json.loads(json.dumps(cells))
    if changed == 'missing':
        cells.pop()
    elif changed == 'planned-missing':
        planned.pop()
    elif changed == 'run':
        cells[0]['run_id'] += 1
    elif changed:
        key, value = {'seed': ('seed', 7), 'source': ('head_sha', 'f60cbfe5e19ca88b40e196d8e793ef0e2aac5d5c'),
                      'stage': ('stage', 'main')}[changed]
        cells[0][key] = value
    result, output = _run_manifest_selector(tmp_path, 'docs/clean-study-smoke-review-candidates-20261031.json',
                                            phase='common-smoke', document={'cells': cells, 'planned_cells': planned})
    assert (result.returncode == 0) == (changed is None), result.stderr
    if changed is None:
        values = dict(line.split('=', 1) for line in output.read_text().splitlines())
        assert len(json.loads(values['matrix'])['cell']) == 27


def closure_fixture(root: Path):
    claims, capture, termination, prefixes = [], {}, {}, {}
    observations = root / "observations"
    for node in ("a", "b"):
        for stage, final in (("002-training", False), ("003-final", True)):
            row = {"snapshot_name": "l7_flow_log", "source_name": "l7_flow_log",
                   "copied_bytes": 100, "copied_sha256": "a" * 64,
                   "source_changed_during_snapshot": False, "pending_tail_bytes_at_read": 0}
            snapshot = {"node": node, "stage": stage, "files": [row],
                        "technical_valid": True, "producer_closed": final,
                        "closed_checkpoint": final, "codec_technical_failure_records": 0}
            name = f"deepflow-raw/node-{node}/{stage}/snapshot.json"
            write(observations / name, snapshot)
            claims.extend([{"path": name, "bytes": (observations / name).stat().st_size,
                            "sha256": digest(observations / name)},
                           {"path": name.replace("snapshot.json", "l7_flow_log"),
                            "bytes": 100, "sha256": "a" * 64}])
            if final:
                capture[node] = snapshot
        prefixes[f"{node}/l7_flow_log"] = {"unchanged": True, "bytes": 100,
                                            "training_sha256": "a" * 64,
                                            "final_prefix_sha256": "a" * 64}
        raw = {}
        for label in ("stop", "inspect", "events"):
            name = f"final-{node}-{label}.txt"
            write(observations / name, b"retained termination source")
            raw[label] = {"path": name, "sha256": digest(observations / name)}
        termination[node] = {"technical_valid": True, "running": False,
                             "exit_code": 0, "oom_killed": False, "sigkill_events": 0,
                             "raw_evidence": raw}
    retention = {"files": claims, "file_count": len(claims),
                 "raw_bytes": sum(row["bytes"] for row in claims), "zero_internal_loss_proven": False}
    path = observations / "deepflow-retention-manifest.json"
    write(path, retention)
    collector = {"retained_file_hashes": {path.name: {
        "bytes": path.stat().st_size, "sha256": digest(path)}}}
    drain = {"final_raw_capture": {"final": True, "technical_valid": True, "nodes": capture},
             "termination": termination, "training_prefix_unchanged_in_final": prefixes}
    return collector, drain


def test_deepflow_closure_verifies_saved_hash_chain_without_claiming_all_raw_bytes(tmp_path: Path) -> None:
    collector, drain = closure_fixture(tmp_path)
    facts = REVIEW.deepflow_closure_facts(tmp_path, collector, drain)
    assert facts["snapshot_hash_chains_verified"] == 4
    assert facts["all_raw_payload_bytes_independently_rehashed"] is False
    assert facts["zero_kernel_producer_or_flush_loss_proven"] is False


@pytest.mark.parametrize("problem", ["prefix", "termination", "snapshot"])
def test_deepflow_closure_rejects_inconsistent_saved_sources(tmp_path: Path, problem: str) -> None:
    collector, drain = closure_fixture(tmp_path)
    if problem == "prefix":
        drain["training_prefix_unchanged_in_final"]["a/l7_flow_log"]["final_prefix_sha256"] = "b" * 64
    elif problem == "termination":
        drain["termination"]["b"]["oom_killed"] = True
    else:
        write(tmp_path / "observations/deepflow-raw/node-a/003-final/snapshot.json", {})
    with pytest.raises(ValueError):
        REVIEW.deepflow_closure_facts(tmp_path, collector, drain)


@pytest.mark.parametrize("controller,smoke,valid", [("clean-study", False, True),
                                                   ("legacy", False, False),
                                                   ("clean-study", True, False)])
@pytest.mark.parametrize('head', [REVIEW.FRESH_HEAD, REVIEW.IMMUTABLE_PATH_HEAD, REVIEW.UPLOADED_CHECKPOINT_COPY_HEAD, REVIEW.CLOSED_FINAL_SNAPSHOT_HEAD, REVIEW.STREAMED_CHECKPOINT_HEAD, REVIEW.PETCLINIC_WORKER_HEAD])
def test_fresh_compact_binds_actual_clean_main_status(
        tmp_path: Path, controller: str, smoke: bool, valid: bool, head: str) -> None:
    declaration, compact, _ = fixture(tmp_path)
    declaration["head_sha"] = head
    status = json.loads((compact / "status.json").read_text())
    status.update(commit=head, controller=controller, smoke=smoke)
    write(compact / "status.json", status)
    manifest = json.loads((compact / "evaluation-manifest.json").read_text())
    manifest["commit"] = head
    manifest["files_sha256"]["status.json"] = digest(compact / "status.json")
    write(compact / "evaluation-manifest.json", manifest)
    if valid:
        assert REVIEW.compact_facts(compact, declaration)[0]["identity"]["collector"] == "obi"
    else:
        with pytest.raises(ValueError, match="clean main controller"):
            REVIEW.compact_facts(compact, declaration)


@pytest.mark.parametrize('mutation',['none','unsafe','foreign_namespace','logical_collision','missing_seal'])
def test_original_capsule_selector_preserves_actual_zip_names_and_rejects_aliasing(tmp_path,monkeypatch,mutation):
    import io
    import zipfile
    bodies={'campaign/plans.json':b'{}','campaign/status.json':b'{}',
        'campaign/observations/technical-positive-control.json':b'{"collector":"deepflow","proofs":{}}',
        'postcapture-proof/closed.json':b'{}','postcapture-proof/capture-status.json':b'{}',
        'postcapture-proof/files.jsonl':b'{}\n','campaign/ignored.bin':b'raw'}
    if mutation=='unsafe':bodies['campaign/../escape']=b'bad'
    if mutation=='foreign_namespace':bodies['unknown/member']=b'bad'
    if mutation=='logical_collision':bodies['campaign/infrastructure/postcapture/closed.json']=b'bad'
    if mutation=='missing_seal':del bodies['postcapture-proof/closed.json']
    memory=io.BytesIO()
    with zipfile.ZipFile(memory,'w') as archive:
        for name,body in bodies.items():archive.writestr(name,body)
    class TinyRemote(io.BytesIO):
        verified_received_bytes=1
        attempted_received_bytes=1
        failures=[]
        def __init__(self,metadata,out):super().__init__(memory.getvalue())
    monkeypatch.setattr(SELECT,'RemoteZip',TinyRemote)
    meta={'id':1,'name':'capsule','size_in_bytes':len(memory.getvalue()),'digest':'sha256:'+'a'*64,
        'expired':False,'workflow_run':{'id':2,'head_sha':'b'*40}}
    expected={**{k:meta[k] for k in ('id','name','size_in_bytes','digest')},'run_id':2,'head_sha':'b'*40}
    if mutation!='none':
        with pytest.raises(ValueError):SELECT.select(meta,expected,'closed-capture',tmp_path/'selected')
    else:
        proof=SELECT.select(meta,expected,'closed-capture',tmp_path/'selected')
        assert proof['scope']=='closed-capture' and proof['complete']
        assert proof['artifact']['name']=='capsule'
        assert proof['files']['status.json']['archive_member_name']=='campaign/status.json'
        assert proof['closed_capture_namespace']['scientific_files']==4
        assert not proof['closed_capture_namespace']['processed_full_snapshot']
        assert not (tmp_path/'selected/ignored.bin').exists()


@pytest.mark.parametrize('mutation',['none','wrong_scope','fake_full','foreign_seed','foreign_artifact','no_layout'])
@pytest.mark.parametrize('manifest_path',[
    'docs/clean-study-partial7-closed-union-review-20261103.json',
    'docs/clean-study-absent6-closed-union-review-20261104.json'])
def test_actual_named_union_manifest_passes_literal_workflow_gate_only_at_exact_scope(tmp_path,mutation,manifest_path):
    import copy
    document=json.loads((ROOT/manifest_path).read_text())
    row=document['cells'][0]
    if mutation=='wrong_scope':row['full_scope']='retrieve_family_selected'
    if mutation=='fake_full':row['full_artifact_id']=777
    if mutation=='foreign_seed':row['seed']=8
    if mutation=='foreign_artifact':row['capture_artifact_id']+=1
    if mutation=='no_layout':row.pop('evidence_layout')
    result,output=_run_manifest_selector(tmp_path,'docs/iteration5-main-review-candidates-coroot-petclinic-full.json',
        phase='fresh-batch',fresh_go=True,document=document)
    assert (result.returncode==0)==(mutation=='none'),result.stderr
    if mutation=='none':
        matrix=json.loads(dict(line.split('=',1) for line in output.read_text().splitlines())['matrix'])
        assert len(matrix['cell'])==1 and 'full_artifact_id' not in matrix['cell'][0]


@pytest.mark.parametrize('mutation',['none','foreign_seed','foreign_artifact','fake_full','foreign_run'])
def test_actual_partial68_union_manifest_retains81plan_and_only2exact_original_packets(tmp_path,mutation):
    document=json.loads((ROOT/'docs/clean-study-partial68-closed-union-review-20261104.json').read_text())
    if mutation=='foreign_seed':document['cells'][0]['seed']=9
    if mutation=='foreign_artifact':document['cells'][1]['restore_artifact_id']+=1
    if mutation=='fake_full':document['cells'][0]['full_artifact_digest']='sha256:'+'0'*64
    if mutation=='foreign_run':document['cells'][1]['run_id']=123
    result,output=_run_manifest_selector(tmp_path,'docs/iteration5-main-review-candidates-coroot-petclinic-full.json',
        phase='fresh-batch',fresh_go=True,document=document)
    assert (result.returncode==0)==(mutation=='none'),result.stderr
    if mutation=='none':
        matrix=json.loads(dict(line.split('=',1) for line in output.read_text().splitlines())['matrix'])
        assert {r['seed'] for r in matrix['cell']}=={6,8}
        assert all(not any(k.startswith('full_artifact_') for k in r) for r in matrix['cell'])


@pytest.mark.parametrize('mutation',['none','new_as_capture','foreign_mode','foreign_capture_artifact','fake_full'])
def test_full8_dual_union_literal_workflow_gate_retains_exact_original_context(tmp_path,mutation):
    document=json.loads((ROOT/'docs/clean-study-full8-dual-union-review-20261104.json').read_text());row=document['cells'][0]
    if mutation=='new_as_capture':row['scientific_capture_run_id']=row['run_id']
    if mutation=='foreign_mode':row['mode']='partial'
    if mutation=='foreign_capture_artifact':row['capture_artifact_id']+=1
    if mutation=='fake_full':row['full_artifact_id']=777
    result,output=_run_manifest_selector(tmp_path,'docs/iteration5-main-review-candidates-coroot-petclinic-full.json',
        phase='fresh-batch',fresh_go=True,document=document)
    assert (result.returncode==0)==(mutation=='none'),result.stderr
    if mutation=='none':
        rows=json.loads(dict(line.split('=',1) for line in output.read_text().splitlines())['matrix'])['cell']
        assert len(rows)==1 and rows[0]['scientific_capture_run_id']==41642796796
