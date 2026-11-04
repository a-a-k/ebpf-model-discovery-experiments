"""One fixed original absent8 scope-composition comparison; Actions only."""
from collections import Counter
import hashlib
import importlib
import importlib.util
import io
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import resource
import zipfile

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery.runtime import Context
from ebpf_discovery.store_v5 import ObservationStoreV5

assert os.environ.get('GITHUB_ACTIONS')=='true'
out=Path('work/shared-scope-qualification');out.mkdir(parents=True,exist_ok=False)
inputs=Path('work/shared-scope-input');inputs.mkdir(parents=True,exist_ok=False)
phases={}
status={'status':'started','source':os.environ.get('GITHUB_SHA'),
        'run_id':os.environ.get('GITHUB_RUN_ID'),'run_attempt':os.environ.get('GITHUB_RUN_ATTEMPT'),
        'started_ns':time.time_ns()}
try:
 
 api=lambda path:json.loads(subprocess.check_output(['gh','api','repos/a-a-k/ebpf-model-discovery-experiments/'+path]))
 EXPECTED_METADATA = {'toolchain/inputs/ebpf/raw/observations.json': 'd298ba0a8765af45e1e2da9091318d832df4440c4a9c92ef609c05df2426ed0a', 'toolchain/inputs/ebpf/network_scope/observations.json': '6713eb44b6126e28a83b3411a445b512cfb80054610385745e33bad3cd073fa0'}
 worker=api('actions/artifacts/13264538182')
 assert (worker['name'],worker['size_in_bytes'],worker['digest'],worker['expired'])==(
  'toolchain-v4-otel_demo-absent-8-41676388484',2331631528,
  'sha256:7895b7d786c5150517166a473e9bc5711070c00d3e7902c0c4a26ad1f77e8df2',False)
 assert (worker['workflow_run']['id'],worker['workflow_run']['head_sha'])==(
  41676388484,'06d7d52bfa4b7768a4cabf02f4e66f109b3a9492')
 remote._atomic_json(out/'original-worker-artifact-api.json',worker)
 spec=importlib.util.spec_from_file_location('existing_selected_metadata_transport','scripts/select-main-review-evidence-v5.py')
 selector=importlib.util.module_from_spec(spec);spec.loader.exec_module(selector)
 transport=selector.RemoteZip(worker,out)
 old={}
 old_indexes={}
 phase_started=time.monotonic_ns()
 with zipfile.ZipFile(transport) as z:
  for name in [*EXPECTED_METADATA,'worker-status.json','toolchain/input-preparation-cost.json']:
   entry=z.getinfo(name);assert entry.file_size<4*1024*1024
   body=z.read(entry)
   if name in EXPECTED_METADATA:assert hashlib.sha256(body).hexdigest()==EXPECTED_METADATA[name]
   old[name]=json.loads(body)
   target=out/'original-metadata'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
  for variant in ('raw','network_scope'):
   claim=old['toolchain/inputs/ebpf/'+variant+'/observations.json']['stream_exports'][0]['request_index']
   name='toolchain/inputs/ebpf/'+variant+'/exports/ebpf-request-index.jsonl'
   entry=z.getinfo(name);assert entry.file_size==claim['bytes'] and entry.file_size<100*1024**2
   target=inputs/(variant+'-original-request-index.jsonl')
   with z.open(entry) as original,target.open('xb') as saved:
    shutil.copyfileobj(original,saved,1024*1024)
   assert target.stat().st_size==claim['bytes'] and remote._sha(target)==claim['sha256']
   old_indexes[variant]=target
 phases['old_metadata_and_indexes']=(time.monotonic_ns()-phase_started)/1e9
 remote._atomic_json(out/'phase-costs.json',phases)
 remote._atomic_json(out/'original-metadata-range-cost.json',{
  'verified_received_bytes':transport.verified_received_bytes,'attempted_received_bytes':transport.attempted_received_bytes,
  'range_failures':transport.failures,'whole_worker_archive_downloaded':False})
 worker_status=old['worker-status.json'];identity=worker_status['identity']
 assert worker_status['status']=='complete' and str(identity['run_id'])=='41642766254'
 assert identity['commit']=='f045cc0adec187ec00443da0bea72b4ec4d2082e'
 assert identity['system']=='otel_demo' and identity['mode']=='absent' and str(identity['seed'])=='8'
 meta=api('actions/artifacts/13247569257')
 assert (meta['size_in_bytes'],meta['digest'],meta['expired'])==(
  3129334984,'sha256:0923153ef0a45b035711d062cd173b5024f43d0ad9c273962e95b6105c68e7f0',False)
 assert (meta['workflow_run']['id'],meta['workflow_run']['head_sha'])==(
  41642766254,'f045cc0adec187ec00443da0bea72b4ec4d2082e')
 remote._atomic_json(out/'original-prefix-artifact-api.json',meta)
 archive=inputs/'prefix.zip'
 guard={'required_bytes':meta['size_in_bytes']+1024**3,'actual_available_bytes':shutil.disk_usage(inputs).free}
 remote._atomic_json(out/'disk-before-download.json',guard);assert guard['actual_available_bytes']>=guard['required_bytes']
 started=time.monotonic_ns()
 with archive.open('xb') as stream:subprocess.run(['gh','api',
  'repos/a-a-k/ebpf-model-discovery-experiments/actions/artifacts/13247569257/zip'],stdout=stream,check=True)
 assert archive.stat().st_size==meta['size_in_bytes'] and 'sha256:'+remote._sha(archive)==meta['digest']
 download=(time.monotonic_ns()-started)/1e9
 phases['prefix_download_and_SHA']=download
 remote._atomic_json(out/'phase-costs.json',phases)
 original_path=Path(old['toolchain/inputs/ebpf/raw/observations.json']['stream_exports'][0]['request_index']['path'])
 root=original_path.parents[5]
 assert root==Path(os.environ['GITHUB_WORKSPACE'])/'work/campaign'
 assert not root.exists()
 with zipfile.ZipFile(archive) as z:
  entries=z.infolist();assert len(entries)==len({e.filename for e in entries})
  original_file_bytes=sum(e.file_size for e in entries if not e.is_dir())
  index=z.getinfo('observation-index.sqlite').file_size
  wire=sum(old[name]['stream_exports'][0]['wire_bytes'] for name in EXPECTED_METADATA)
  required=original_file_bytes+3*index+wire+1024**3
  guard={'required_additional_bytes':required,'actual_available_bytes':shutil.disk_usage(inputs).free,
   'original_file_bytes':original_file_bytes,'three_SQL_sized_preparation_reserve':3*index,
   'original_expected_two_view_wire_bytes':wire,'scientific_filter_or_limit':False}
  remote._atomic_json(out/'disk-before-complete-prefix-restore.json',guard)
  assert guard['actual_available_bytes']>=required
 phase_started=time.monotonic_ns()
 remote._safe_extract(archive,root)
 phases['prefix_restore']=(time.monotonic_ns()-phase_started)/1e9
 remote._atomic_json(out/'phase-costs.json',phases)
 phase_started=time.monotonic_ns()
 expected={k:identity[k] for k in remote.IDENTITY_KEYS if k in identity}
 manifest,before=remote._validate_checkpoint(root,expected)
 assert remote._sha(root/'manifest.json')==identity['manifest_sha256']
 pins,toolchain_type,provenance=remote._checkpoint_toolchain(root,manifest)
 assert provenance is not None and provenance['collector']=='deepflow'
 proof=remote._verify_binaries(root,manifest,pins=pins);remote._make_binaries_executable(proof)
 ctx=Context(root,'absent',8);ctx.command_log=out/'qualification-only-commands.jsonl'
 os.environ['PBS_BIN']=str(root/'toolchain-build/bin')
 phases['complete_prefix_and_binary_verification']=(time.monotonic_ns()-phase_started)/1e9
 remote._atomic_json(out/'phase-costs.json',phases)
 store=remote._readonly_store(root/'observation-index.sqlite',ObservationStoreV5,immutable_prefix=True)
 try:
  engine=toolchain_type(ctx,'otel_demo',store,importlib.import_module('systems.otel_demo.experiment_v4'))
  phase_started=time.monotonic_ns();engine.preflight()
  phases['preflight']=(time.monotonic_ns()-phase_started)/1e9
  remote._atomic_json(out/'phase-costs.json',phases)
  started=time.monotonic_ns()
  try:
   engine.prepare_inputs(remote._read(root/'plans.json'))
  finally:
   phases['prepare_inputs']=(time.monotonic_ns()-started)/1e9
   remote._atomic_json(out/'phase-costs.json',phases)
   # Retain these immediately, including when the subsequent checks reject data.
   for path in [root/'toolchain/input-preparation-cost.json',
                *sorted((root/'toolchain/inputs').glob('*/*/observations.json')),
                *sorted((root/'toolchain/inputs').glob('*/*/network-scope-derivation.json'))]:
    if path.is_file():
     assert path.stat().st_size<4*1024**2
     target=out/'new-metadata'/path.relative_to(root)
     target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
  preparation=phases['prepare_inputs']
  phase_started=time.monotonic_ns()
  _,after=remote._validate_checkpoint(root,expected,allow_toolchain=True)
  assert after['files']==before['files']
  remote._atomic_json(out/'prefix-before-after.json',{
   'complete_original_files_equal':True,'files':len(before['files']),
   'before_files_proof_sha256':remote._json_sha(before['files']),
   'after_files_proof_sha256':remote._json_sha(after['files'])})
  phases['complete_prefix_after_verification']=(time.monotonic_ns()-phase_started)/1e9
  remote._atomic_json(out/'phase-costs.json',phases)
  spec=importlib.util.spec_from_file_location('existing_clock_equality','scripts/check-fixed-dsb-path-preparation-v5.py')
  equality=importlib.util.module_from_spec(spec);spec.loader.exec_module(equality)
  clocks=Counter()
  old_cost=old['toolchain/input-preparation-cost.json']
  new_cost=remote._read(root/'toolchain/input-preparation-cost.json')
  windows=((old_cost['started_ns'],old_cost['ended_ns']),
           (new_cost['started_ns'],new_cost['ended_ns']))
  comparisons=[]
  phase_started=time.monotonic_ns()
  for variant in ('raw','network_scope'):
   old_manifest=old['toolchain/inputs/ebpf/'+variant+'/observations.json']
   _,new_manifest=engine.input_manifests['ebpf',variant]
   assert new_manifest['observations']==old_manifest['observations']
   assert len(new_manifest['stream_exports'])==len(old_manifest['stream_exports'])==1
   a,b=old_manifest['stream_exports'][0],new_manifest['stream_exports'][0]
   for key in ('requests','observations','wire_bytes','runtime_identity_transformations','http_request_boundaries_preserved','storage_shards_are_not_http_batches'):
    assert a[key]==b[key],(variant,key)
   assert (a['request_index']['path'],a['request_index']['bytes'])==(b['request_index']['path'],b['request_index']['bytes'])
   new_index=Path(b['request_index']['path'])
   normalized=hashlib.sha256();row_count=0
   with old_indexes[variant].open('rb') as old_rows,new_index.open('rb') as new_rows:
    for ordinal,(left_line,right_line) in enumerate(itertools.zip_longest(old_rows,new_rows),1):
     if left_line is None or right_line is None:
      raise ValueError('request index row count changed')
     left,right=json.loads(left_line),json.loads(right_line)
     for line,value in ((left_line,left),(right_line,right)):
      if (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()!=line:
       raise ValueError('index is not exact canonical JSON; no lexical fields may be hidden')
     old_clock=left['derived_otlp_proof']['codec_accounting']['index_preparation_cost']
     new_clock=right['derived_otlp_proof']['codec_accounting']['index_preparation_cost']
     try:
      equality.strip_clock_pair(old_clock,new_clock,*windows,clocks,
                                'codec_accounting.index_preparation_cost')
      equality.equal(left,right)
     except (ValueError,KeyError) as error:
      remote._atomic_json(out/'first-index-difference.json',{
       'variant':variant,'row':ordinal,'old_cost_metadata':old_clock,
       'new_cost_metadata':new_clock,'changed_top_level_fields':[
        key for key in sorted(set(left)|set(right))
        if key not in left or key not in right or equality.canonical(left[key])!=equality.canonical(right[key])],
       'old_record_nonclock_SHA256':hashlib.sha256(equality.canonical(left)).hexdigest(),
       'new_record_nonclock_SHA256':hashlib.sha256(equality.canonical(right)).hexdigest(),
       'error':repr(error)})
      raise
     normalized.update(equality.canonical(left)+b'\n');row_count+=1
   index_equality={'rows':row_count,'ordered_nonclock_rows_sha256':normalized.hexdigest()}
   remote._atomic_json(out/(variant+'-index-comparison.json'),{
    'old_literal':a['request_index'],'new_literal':b['request_index'],
    **index_equality,'only_removed_fields':[
     'derived_otlp_proof.codec_accounting.index_preparation_cost.started_ns',
     'derived_otlp_proof.codec_accounting.index_preparation_cost.ended_ns']})
   assert a['shards']==b['shards'],variant+' wire payload bytes or storage boundaries changed'
   for key in ('path','bytes','sha256','values','authority'):
    assert a['runtime_identity_values'][key]==b['runtime_identity_values'][key],(variant,key)
   for claim in [b['request_index'],*b['shards'],b['runtime_identity_values']]:
    path=Path(claim['path']);assert path.is_file() and path.stat().st_size==claim['bytes']
    assert remote._sha(path)==claim['sha256']
   comparisons.append({'variant':variant,'observations':b['observations'],'requests':b['requests'],
    'old_literal_request_index':a['request_index'],'new_literal_request_index':b['request_index'],
    'all_ordered_nonclock_index_fields_exact':index_equality,'all_wire_shards_count':len(b['shards']),
    'all_wire_shards_exact_original_bytes_and_SHA':True,
    'complete_value_store':{k:b['runtime_identity_values'][k] for k in ('path','bytes','sha256','values')},
    'every_request_body_length_SHA_order_and_all_nonclock_metadata_refs_exact':True})
  phases['comparison']=(time.monotonic_ns()-phase_started)/1e9
  remote._atomic_json(out/'phase-costs.json',phases)
  remote._atomic_json(out/'allowed-cost-clock-pairs.json', [
   {'scope':key[0],'old_started_ns':key[1],'old_ended_ns':key[2],
    'new_started_ns':key[3],'new_ended_ns':key[4],'occurrences':count}
   for key,count in sorted(clocks.items())])
 finally:store.close()
 remote._atomic_json(out/'qualification.json',{'schema_version':'exact-original-shared-scope-qualification-v1',
  'source':os.environ['GITHUB_SHA'],'original_scientific_source':identity['commit'],'original_worker':41676388484,
  'original_prefix':13247569257,'original_worker_metadata':EXPECTED_METADATA,'actual_preparation_seconds':preparation,
  'original_preparation_seconds':(old['toolchain/input-preparation-cost.json']['ended_ns']-old['toolchain/input-preparation-cost.json']['started_ns'])/1e9,'old_cost_comparison_limit':'Different sequential runner observations; OS cache/storage variance retained, no unique-cause or whole6h guarantee',
  'actual_archive_download_SHA_seconds':download,'all_original_inputs_after_equal_before':True,
  'all_original_prepared_wire_requests_and_all_nonclock_metadata_equal':True,
  'exact_cost_clock_whitelist_recorded_separately':True,'phase_costs':phases,'comparisons':comparisons,
  'preparation_cost':remote._read(root/'toolchain/input-preparation-cost.json'),
  'Bering_Sheaft_traffic_or_scientific_case_execution':False,'whole_absent3_six_hour_headroom_GO':False,
  'complete_cost_boundary':'All original baseline/failedfe2h/failedCI/newCI/API/range/transfer/extraction/validation/preparation/hash/comparison/host/review/retention costs; human unknown'})
 print(json.dumps({'status':'complete','actual_prepare_seconds':preparation,'original_prepare_seconds':(old['toolchain/input-preparation-cost.json']['ended_ns']-old['toolchain/input-preparation-cost.json']['started_ns'])/1e9,
  'every_original_request_and_all_nonclock_metadata_exact':True,'new_main_or_model':False}))
 status['status']='complete'
except BaseException as error:
 status.update(status='technical_failure',error=repr(error))
 raise
finally:
 status.update(ended_ns=time.time_ns(),user_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,
  system_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 if 'clocks' in locals():
  remote._atomic_json(out/'allowed-cost-clock-pairs.json', [
   {'scope':key[0],'old_started_ns':key[1],'old_ended_ns':key[2],
    'new_started_ns':key[3],'new_ended_ns':key[4],'occurrences':count}
   for key,count in sorted(clocks.items())])
 remote._atomic_json(out/'status.json',status)
 remote._atomic_json(out/'phase-costs.json',phases)
 print(json.dumps(status),flush=True)
