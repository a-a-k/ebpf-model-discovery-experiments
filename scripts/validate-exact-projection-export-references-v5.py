"""One original absent8 immutable export-equivalence comparison; Actions only."""
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery.runtime import Context
from ebpf_discovery.store_v5 import ObservationStoreV5

assert os.environ.get('GITHUB_ACTIONS')=='true'
out=Path('work/projection-reference-qualification');out.mkdir(parents=True,exist_ok=False)
inputs=Path('work/projection-reference-input');inputs.mkdir(parents=True,exist_ok=False)
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
with zipfile.ZipFile(transport) as z:
 for name in [*EXPECTED_METADATA,'worker-status.json','toolchain/input-preparation-cost.json']:
  entry=z.getinfo(name);assert entry.file_size<4*1024*1024
  body=z.read(entry)
  if name in EXPECTED_METADATA:assert hashlib.sha256(body).hexdigest()==EXPECTED_METADATA[name]
  old[name]=json.loads(body)
  target=out/'original-metadata'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
remote._atomic_json(out/'original-metadata-range-cost.json',{
 'verified_received_bytes':transport.verified_received_bytes,'attempted_received_bytes':transport.attempted_received_bytes,
 'range_failures':transport.failures,'whole_worker_archive_downloaded':False})
status=old['worker-status.json'];identity=status['identity']
assert status['status']=='complete' and str(identity['run_id'])=='41642766254'
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
remote._safe_extract(archive,root)
expected={k:identity[k] for k in remote.IDENTITY_KEYS if k in identity}
manifest,before=remote._validate_checkpoint(root,expected)
assert remote._sha(root/'manifest.json')==identity['manifest_sha256']
pins,toolchain_type,provenance=remote._checkpoint_toolchain(root,manifest)
assert provenance is not None and provenance['collector']=='deepflow'
proof=remote._verify_binaries(root,manifest,pins=pins);remote._make_binaries_executable(proof)
ctx=Context(root,'absent',8);ctx.command_log=out/'qualification-only-commands.jsonl'
os.environ['PBS_BIN']=str(root/'toolchain-build/bin')
store=remote._readonly_store(root/'observation-index.sqlite',ObservationStoreV5,immutable_prefix=True)
try:
 engine=toolchain_type(ctx,'otel_demo',store,importlib.import_module('systems.otel_demo.experiment_v4'))
 engine.preflight()
 started=time.monotonic_ns();engine.prepare_inputs(remote._read(root/'plans.json'))
 preparation=(time.monotonic_ns()-started)/1e9
 comparisons=[]
 for variant in ('raw','network_scope'):
  old_manifest=old['toolchain/inputs/ebpf/'+variant+'/observations.json']
  _,new_manifest=engine.input_manifests['ebpf',variant]
  assert new_manifest['observations']==old_manifest['observations']
  assert len(new_manifest['stream_exports'])==len(old_manifest['stream_exports'])==1
  a,b=old_manifest['stream_exports'][0],new_manifest['stream_exports'][0]
  for key in ('requests','observations','wire_bytes','runtime_identity_transformations','http_request_boundaries_preserved','storage_shards_are_not_http_batches'):
   assert a[key]==b[key],(variant,key)
  assert a['request_index']==b['request_index'],variant+' complete ordered per-request metadata changed'
  assert a['shards']==b['shards'],variant+' wire payload bytes or storage boundaries changed'
  for key in ('path','bytes','sha256','values','authority'):
   assert a['runtime_identity_values'][key]==b['runtime_identity_values'][key],(variant,key)
  for claim in [b['request_index'],*b['shards'],b['runtime_identity_values']]:
   path=Path(claim['path']);assert path.is_file() and path.stat().st_size==claim['bytes']
   assert remote._sha(path)==claim['sha256']
  comparisons.append({'variant':variant,'observations':b['observations'],'requests':b['requests'],
   'complete_ordered_request_index':b['request_index'],'all_wire_shards_count':len(b['shards']),
   'all_wire_shards_exact_original_bytes_and_SHA':True,
   'complete_value_store':{k:b['runtime_identity_values'][k] for k in ('path','bytes','sha256','values')},
   'every_request_body_length_SHA_order_and_all_metadata_refs_exact':True})
finally:store.close()
_,after=remote._validate_checkpoint(root,expected,allow_toolchain=True)
assert after['files']==before['files']
remote._atomic_json(out/'qualification.json',{'schema_version':'exact-original-stored-projection-reference-qualification-v1',
 'source':os.environ['GITHUB_SHA'],'original_scientific_source':identity['commit'],'original_worker':41676388484,
 'original_prefix':13247569257,'original_worker_metadata':EXPECTED_METADATA,'actual_preparation_seconds':preparation,
 'original_preparation_seconds':(old['toolchain/input-preparation-cost.json']['ended_ns']-old['toolchain/input-preparation-cost.json']['started_ns'])/1e9,'old_cost_comparison_limit':'Different sequential runner observations; OS cache/storage variance retained, no unique-cause or whole6h guarantee',
 'actual_archive_download_SHA_seconds':download,'all_original_inputs_after_equal_before':True,
 'all_original_prepared_wire_requests_and_full_metadata_equal':True,'comparisons':comparisons,
 'preparation_cost':remote._read(root/'toolchain/input-preparation-cost.json'),
 'Bering_Sheaft_traffic_or_scientific_case_execution':False,'whole_absent3_six_hour_headroom_GO':False,
 'complete_cost_boundary':'All original baseline/failedCI/newCI/API/range/transfer/extraction/validation/preparation/hash/comparison/host/review/retention costs; human unknown'})
print(json.dumps({'status':'complete','actual_prepare_seconds':preparation,'original_prepare_seconds':(old['toolchain/input-preparation-cost.json']['ended_ns']-old['toolchain/input-preparation-cost.json']['started_ns'])/1e9,
 'every_original_request_and_metadata_exact':True,'new_main_or_model':False}))
