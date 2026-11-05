"""One retained absent8 SQLite proof comparison; GitHub Actions only."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time
import zipfile

from ebpf_discovery import remote_toolchain_v4 as remote

assert os.environ.get('GITHUB_ACTIONS')=='true','Scientific saved-input work runs in Actions only'
out=Path('work/sql-proof-reuse-qualification');out.mkdir(parents=True,exist_ok=False)
inputs=Path('work/sql-proof-reuse-input');inputs.mkdir(parents=True,exist_ok=False)
artifact_id=13247569257
run_id=41642766254
producer='f045cc0adec187ec00443da0bea72b4ec4d2082e'
api=lambda path:json.loads(subprocess.check_output(['gh','api','repos/a-a-k/ebpf-model-discovery-experiments/'+path]))
artifact=api(f'actions/artifacts/{artifact_id}')
run=api(f'actions/runs/{run_id}')
assert (artifact['id'],artifact['name'],artifact['size_in_bytes'],artifact['digest'],artifact['expired'])==(
 artifact_id,'training-v4-otel_demo-absent-8-41642766254',3129334984,
 'sha256:0923153ef0a45b035711d062cd173b5024f43d0ad9c273962e95b6105c68e7f0',False)
assert artifact['workflow_run']['id']==run_id and artifact['workflow_run']['head_sha']==producer
assert run['id']==run_id and run['head_sha']==producer
remote._atomic_json(out/'artifact-api.json',artifact);remote._atomic_json(out/'original-run-api.json',run)
archive=inputs/'checkpoint.zip'
started=time.monotonic_ns()
pre_guard={'required_bytes':artifact['size_in_bytes']+1024**3,'actual_available_bytes':shutil.disk_usage(inputs).free}
remote._atomic_json(out/'disk-before-download.json',pre_guard)
assert pre_guard['actual_available_bytes']>=pre_guard['required_bytes']
with archive.open('xb') as stream:
 subprocess.run(['gh','api',f'repos/a-a-k/ebpf-model-discovery-experiments/actions/artifacts/{artifact_id}/zip'],stdout=stream,check=True)
assert archive.stat().st_size==artifact['size_in_bytes'] and 'sha256:'+remote._sha(archive)==artifact['digest']
transfer=(time.monotonic_ns()-started)/1e9
checkpoint=inputs/'checkpoint';checkpoint.mkdir()
with zipfile.ZipFile(archive) as z:
 names=z.namelist()
 assert len(names)==len(set(names)) and all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
 wanted=('manifest.json','ready.json','observation-index.sqlite')
 assert all(n in names for n in wanted)
 required=3*z.getinfo('observation-index.sqlite').file_size+1024**3
 guard={'required_additional_bytes':required,'actual_available_bytes':shutil.disk_usage(inputs).free,
  'basis':'original SQLite + separate live copy + one closed consistent backup + 1GiB; downloaded ZIP already allocated',
  'scientific_data_filter_or_limit':False}
 remote._atomic_json(out/'disk-before-selected-extraction.json',guard)
 assert guard['actual_available_bytes']>=required
 for n in wanted:
  target=checkpoint/n
  with z.open(n) as source,target.open('xb') as dest:shutil.copyfileobj(source,dest,1024*1024)
manifest=json.loads((checkpoint/'manifest.json').read_text());ready=json.loads((checkpoint/'ready.json').read_text())
assert str(manifest['identity']['run_id'])==str(run_id) and manifest['identity']['commit']==producer
assert manifest['identity']['mode']=='absent' and manifest['identity']['seed']==8
assert ready['manifest_sha256']==remote._sha(checkpoint/'manifest.json')
record=manifest['files']['observation-index.sqlite']
assert (checkpoint/'observation-index.sqlite').stat().st_size==record['bytes']
assert remote._sha(checkpoint/'observation-index.sqlite')==record['sha256']
verified={'manifest_sha256':ready['manifest_sha256'],'files':{'observation-index.sqlite':{k:record[k] for k in ('bytes','sha256')}}}
remote._atomic_json(out/'source-binding.json',{'identity':manifest['identity'],'manifest_sha256':ready['manifest_sha256'],
 'original_SQL_input':verified['files']['observation-index.sqlite'],'scope':'Exact selected original SQLite/manifest/ready; not a full checkpoint or scientific-case validation',
 'selected_members_CRC_read_to_EOF':list(wanted),'entire_delivered_ZIP_SHA256_verified':True})
reference=remote._checkpoint_index_reference(checkpoint,verified)
remote._atomic_json(out/'original-proof-reference.json',reference)
live_path=inputs/'live.sqlite';copy_started=time.monotonic_ns()
shutil.copyfile(checkpoint/'observation-index.sqlite',live_path)
copy_seconds=(time.monotonic_ns()-copy_started)/1e9
connection=sqlite3.connect(live_path)
try:
 started=time.monotonic_ns()
 baseline=remote._consistent_live_index_proof(connection,inputs/'baseline-backup.sqlite')
 baseline_seconds=(time.monotonic_ns()-started)/1e9
 assert baseline==reference['logical_proof']
 measured=[]
 for phase in ('before','after'):
  receipt=out/f'{phase}-reuse.json'
  actual=remote._consistent_live_index_proof(connection,inputs/f'{phase}-backup.sqlite',reference=reference,receipt=receipt)
  proof=json.loads(receipt.read_text())
  assert actual==baseline
  measured.append(proof)
finally:connection.close()
remote._atomic_json(out/'qualification.json',{'schema_version':'exact-saved-SQL-proof-reuse-qualification-v1',
 'recorded_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source':os.environ['GITHUB_SHA'],
 'original_producer':run_id,'original_source':producer,'artifact_id':artifact_id,'artifact_digest':artifact['digest'],
 'all_original_logical_proofs_equal':True,'same_exact_complete_SQL_inputs':all(r['logical_proof_reused'] for r in measured),
 'original_proof_sha256':reference['logical_proof_sha256'],'original_full_proof_seconds':reference['original_logical_proof_seconds'],
 'reference_total_seconds':reference['elapsed_seconds'],'old_consistent_backup_and_full_walk_seconds':baseline_seconds,
 'optimized_backup_proof_receipts':measured,'archive_download_SHA_seconds':transfer,'live_copy_seconds':copy_seconds,
 'whole_main_case_headroom_or_six_hour_cure_proven':False,'new_traffic_model_fit_Sheaft_or_scientific_admission':False,
 'complete_cost_boundary':'original source qualification, transfer, extraction, reference, copy, baseline, both optimized phases, CI/Actions/review costs; human effort unknown'})
print(json.dumps({'status':'complete','old_seconds':baseline_seconds,'optimized_seconds':[r['elapsed_seconds'] for r in measured],
 'reuse_hits':[r['logical_proof_reused'] for r in measured],'all_logical_proofs_equal':True}))
