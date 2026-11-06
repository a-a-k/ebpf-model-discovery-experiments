#!/usr/bin/env python3
"""One fixed preserved-DSB metadata inspection; no application/model execution."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tarfile
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'docs/v6-DSB-db-control-fixed-source-20261106.json'
PROFILE_SHA = '9e4da5cdaa94dbaf857810448a2f9e94294e43cf9cfdf8862cae2a4a0c37b63f'
REPOSITORY = 'a-a-k/ebpf-model-discovery-experiments'
DB = 'dsb-user-timeline-mongodb'
SERVICE = 'user-timeline-mongodb'
RESERVE = 2 * 1024**3
CHUNK = 1024**2


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def atomic(path, value):
    pending = path.with_suffix(path.suffix + '.pending')
    data = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf8')
    if len(data) > 4 * 1024**2:
        raise ValueError('fixed derived metadata output exceeds reviewed small-output scope')
    pending.write_bytes(data)
    os.replace(pending, path)


def guard(root, incoming):
    row = {'at_ns':time.time_ns(), 'free_bytes':shutil.disk_usage(root).free,
           'incoming_bytes':incoming, 'reserve_bytes':RESERVE}
    if row['free_bytes'] < incoming + RESERVE:
        raise OSError('insufficient actual free bytes for this one immutable publication')
    return row


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def request(path):
    return urllib.request.Request('https://api.github.com/repos/' + REPOSITORY + '/' + path,
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],
                 'Accept':'application/vnd.github+json', 'X-GitHub-Api-Version':'2026-03-10'})


def api(path):
    with urllib.request.urlopen(request(path), timeout=60) as response:
        return json.load(response)


def artifact_identity(actual, expected):
    origin = actual.get('workflow_run') or {}
    if (actual.get('expired') is not False
            or any(actual.get(k) != expected[k] for k in ('id','name','size_in_bytes','digest'))
            or origin.get('id') != expected['run_id'] or origin.get('head_sha') != expected['source']):
        raise ValueError('fixed original artifact API identity differs')


def download(expected, destination):
    # Resolve the authenticated API redirect without forwarding its token to the signed host.
    try:
        response = urllib.request.build_opener(NoRedirect).open(
            request(f"actions/artifacts/{expected['id']}/zip"), timeout=60)
    except urllib.error.HTTPError as error:
        if error.code != 302: raise
        location = error.headers.get('Location', '')
        target = urllib.parse.urlsplit(location)
        if (target.scheme != 'https' or not target.hostname or not any(
                target.hostname.endswith(suffix) for suffix in
                ('.blob.core.windows.net','.githubusercontent.com','.actions.githubusercontent.com'))):
            raise ValueError('unexpected signed artifact delivery host')
        response = urllib.request.urlopen(urllib.request.Request(location), timeout=60)
    digest, total = hashlib.sha256(), 0
    with response, destination.open('xb') as output:
        while chunk := response.read(CHUNK):
            total += len(chunk)
            if total > expected['size_in_bytes']:
                raise ValueError('artifact exceeds exact approved API byte size')
            output.write(chunk); digest.update(chunk)
    if total != expected['size_in_bytes'] or 'sha256:'+digest.hexdigest() != expected['digest']:
        raise ValueError('whole original artifact ZIP bytes/SHA differ')
    return {'bytes':total,'sha256':digest.hexdigest()}


def unwrap_zip(path, directory):
    expected_names = {'capture.tar.gz','capture.tar.gz.json'}
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) != 2 or {m.filename for m in members} != expected_names:
            raise ValueError('fixed capture ZIP must contain exactly its tar and inventory')
        for member in members:
            kind = stat.S_IFMT(member.external_attr >> 16)
            if member.is_dir() or kind not in (0,stat.S_IFREG) or member.flag_bits & 1:
                raise ValueError('ZIP members must be ordinary unencrypted fixed-name files')
        disk = guard(directory, sum(m.file_size for m in members))
        claims = {}
        for member in members:
            digest, total = hashlib.sha256(), 0
            with archive.open(member) as source, (directory/member.filename).open('xb') as target:
                while chunk := source.read(CHUNK):
                    total += len(chunk); digest.update(chunk); target.write(chunk)
            if total != member.file_size:
                raise ValueError('incomplete ZIP member')
            claims[member.filename] = {'bytes':total,'sha256':digest.hexdigest(),
                                      'ZIP_CRC32':f'{member.CRC:08x}'}
    return claims, disk  # zipfile validates every member CRC at EOF.


def safe_name(name):
    path = PurePosixPath(name)
    if (not name or '\\' in name or path.is_absolute() or '..' in path.parts
            or path.as_posix() != name or ':' in name):
        raise ValueError('invalid original tar member path')
    return name


def selected(name):
    return (name in ('closed-input.json','status.json','external.json','blocks.json','deployment.json',
                     'capture-commands.jsonl','commands.jsonl')
            or re.fullmatch(r'runtime-identity-v5/capture-(?:before|after)-db_down-\d+\.json', name)
            or re.fullmatch(r'runtime-identity-v5/sample-(?:before|after)-db_down-\d+-a\.json', name)
            or name in ('deployment/deathstarbench/container-ip-mapping.json',
                'deployment/deathstarbench/node-a/config/service-config.json',
                'deployment/deathstarbench/node-b/config/service-config.json',
                'deployment/deathstarbench/node-a/config-disabled/service-config.json',
                'deployment/deathstarbench/node-b/config-disabled/service-config.json'))


def pick(value, keys):
    return {key:value[key] for key in keys if key in value}


def external_rows(rows):
    result = []
    for row in rows:
        if row.get('phase') not in ('db_up','db_down'): continue
        saved = pick(row, ('operation','attempt_id','phase','state','block_id','started_ns','ended_ns',
                           'scheduled_ns','dispatched_ns','success'))
        saved['http_steps'] = [pick(step, ('request_id','method','path','status','started_ns','ended_ns',
                               'elapsed_ns','body_completed_ns','response_sha256')) for step in row.get('http_steps', [])]
        saved['validation'] = pick(row.get('validation') or {}, ('kind','control_epoch','replica_state',
                                                                  'database_up','compose_marker_sha256'))
        eventual = row.get('eventual_postcondition')
        if isinstance(eventual, dict):
            saved['eventual_postcondition'] = pick(eventual, ('kind','success','unknown_reason',
                                                             'control_epoch','expected_text_sha256'))
            saved['eventual_postcondition']['locations'] = {
                key:pick(item, ('request_id','status','body_sha256','found'))
                for key,item in (eventual.get('locations') or {}).items()
                if key in ('user_timeline_owner','home_timeline_follower')}
        else:
            saved['eventual_postcondition'] = {'verdict':'UNKNOWN','reason':'no saved auxiliary postcondition'}
        result.append(saved)
    return result


def command_rows(body):
    result = []
    for line in body.decode('utf8').splitlines():
        if not line.strip(): continue
        row = json.loads(line)
        argv = row.get('command') or []
        if not isinstance(argv,list) or not all(isinstance(x,str) for x in argv): continue
        text = ' '.join(argv)
        node = 'a' if 'ubuntu@192.168.76.11' in argv else 'b' if 'ubuntu@192.168.76.12' in argv else None
        direct = re.search(r'\bdocker\s+(?:start|stop|restart|kill|pause|unpause|rm)\s+'+re.escape(DB)+r'''(?=\s|['"]|$)''',text)
        compose = ('docker compose' in text and ('dsb-ebpf-study' in text or '/deathstarbench/' in text)
                   and re.search(r'\b(?:up|down|start|stop|restart|kill|rm)\b',text))
        if not (direct or compose): continue
        result.append({'command':argv,'node':node, **pick(row, ('started_ns','ended_ns','returncode')),
            'command_row_sha256':hashlib.sha256(line.encode('utf8')).hexdigest(),
            'scope':'selected container control' if direct else 'DSB Compose lifecycle; may affect selected DB'})
    return result


def db_snapshot(name, value, all_files, sample_files):
    stage = name.removeprefix('runtime-identity-v5/capture-').removesuffix('.json')
    result = {'member':name,'stage':stage,'verdict':'UNKNOWN',
              'runner_interval':value.get('runner_interval'),'errors':value.get('errors')}
    samples = [s for s in value.get('samples',[]) if s.get('node')=='a' and s.get('stage')==stage]
    proofs_valid = all(all_files.get('runtime-identity-v5/'+key,{}).get('sha256')==claim.get('sha256')
        and all_files.get('runtime-identity-v5/'+key,{}).get('bytes')==claim.get('bytes')
        for key,claim in (value.get('files') or {}).items()) and bool(value.get('files'))
    if value.get('schema') != 'runtime-identity-capture-v5' or value.get('stage') != stage or len(samples)!=1 or not proofs_valid:
        result['reason']='missing/ambiguous/mismatched saved capture evidence'; return result
    sample = samples[0]
    separate = sample_files.get('runtime-identity-v5/sample-'+stage+'-a.json')
    if separate is not None and separate != sample:
        result['reason']='separately retained node-a sample differs'; return result
    result.update(boot_id=sample.get('boot_id'), clocks=sample.get('clocks'),
        docker_proof=pick(sample.get('docker_proof') or {}, ('list_returncode','inspect_returncode')))
    containers = [c for c in sample.get('containers',[]) if c.get('name')==DB]
    if len(containers)!=1:
        result['reason']='selected Mongo container missing or ambiguous'; return result
    container=containers[0]
    result['selected_container'] = pick(container, ('id','name','image','config_image','state','compose',
                                                   'network_settings','host_network_config'))
    state=container.get('state') or {}
    result['selected_container']['state']=pick(state,('Status','Running','Pid','StartedAt','FinishedAt','ExitCode'))
    clocks=sample.get('clocks') or {}
    clock_valid=all(type((clocks.get(edge) or {}).get(key)) is int
        for edge in ('started','ended') for key in ('realtime_unix_ns','monotonic_ns','boottime_ns'))
    interval=value.get('runner_interval') or {}
    interval_valid=all(type(interval.get(key)) is int for key in (
        'started_monotonic_ns','ended_monotonic_ns')) and interval.get('started_monotonic_ns',1)<=interval.get('ended_monotonic_ns',0)
    if (sample.get('schema')=='runtime-identity-guest-sample-v5' and sample.get('boot_id')
            and sample.get('docker_proof',{}).get('list_returncode')==0
            and sample.get('docker_proof',{}).get('inspect_returncode')==0
            and type(state.get('Running')) is bool and container.get('id') and clock_valid and interval_valid
            and all(key in state for key in ('Status','Running','Pid','StartedAt','FinishedAt','ExitCode'))):
        result['verdict']='OBSERVED'
    else: result['reason']='selected Docker state/identity/clock evidence incomplete'
    result['continuous_downtime_proven']=False
    return result


def inspect_tar(path, package, fixed):
    if (package.get('study'),package.get('phase'),package.get('collector'),package.get('run_id'),package.get('source')) != (
            'clean-restart-v6','validation',fixed['collector'],fixed['run_id'],fixed['source']):
        raise ValueError('original capture package origin differs')
    if path.stat().st_size != package['bytes'] or sha(path) != package['sha256']:
        raise ValueError('whole original capture tar SHA/bytes differ')
    before=path.stat()
    actual, directories, retained, selected_claims = {}, set(), {}, {}
    seen=set()
    with tarfile.open(path,'r|gz') as archive:
        for member in archive:
            name=safe_name(member.name)
            if name in seen or not (member.isfile() or member.isdir()) or member.mode & 0o7000:
                raise ValueError('duplicate/link/special original tar member')
            seen.add(name)
            if member.isdir(): directories.add(name); continue
            expected=package['files'].get(name)
            if expected is None or expected['bytes']!=member.size or expected['mode']!=stat.S_IMODE(member.mode):
                raise ValueError('original member bytes/mode/header differs from inventory')
            digest=hashlib.sha256(); total=0; output=io.BytesIO() if selected(name) else None
            stream=archive.extractfile(member)
            while chunk:=stream.read(CHUNK):
                total+=len(chunk);digest.update(chunk)
                if output is not None: output.write(chunk)
            claim={'bytes':total,'sha256':digest.hexdigest(),'mode':stat.S_IMODE(member.mode)}
            if claim!=expected: raise ValueError('original member full bytes/SHA/mode differs')
            actual[name]=claim
            if output is not None:
                selected_claims[name]=claim
                retained[name]=output.getvalue()
    if actual!=package['files'] or directories!=set(package.get('directories',[])):
        raise ValueError('original complete tar member census differs')
    closed_bytes=retained['closed-input.json']
    if hashlib.sha256(closed_bytes).hexdigest()!=fixed['closed_input_sha256']:
        raise ValueError('exact approved original closed-input SHA differs')
    closed=json.loads(closed_bytes); status=json.loads(retained['status.json'])
    if (closed.get('status')!=status or package.get('case')!=status
            or (status.get('study'),status.get('system'),status.get('mode'),status.get('seed'),
                status.get('stage'),status.get('smoke'),status.get('phase'),status.get('collector'),
                str(status.get('run_id')),status.get('commit'),status.get('status')) != (
                'clean-restart-v6','deathstarbench','full',9,'qualification',True,'validation',fixed['collector'],
                str(fixed['run_id']),fixed['source'],'capture_complete')
            or closed.get('phase')!='validation' or any(
                actual.get(name,{}).get('sha256')!=expected for name,expected in closed['files'].items())):
        raise ValueError('closed original capture identity/complete source hashes differ')
    decoded={name:json.loads(body) for name,body in retained.items() if name.endswith('.json')}
    rows=external_rows(decoded.get('external.json',[]))
    snapshots=[db_snapshot(name,value,actual,decoded) for name,value in decoded.items()
               if re.fullmatch(r'runtime-identity-v5/capture-(?:before|after)-db_down-\d+\.json',name)]
    commands={name:command_rows(body) for name,body in retained.items() if name.endswith('.jsonl')}
    configs={}
    for name,value in decoded.items():
        if name.endswith('/service-config.json'):
            configs[name]={key:pick(item,('addr','port')) for key,item in value.items()
                           if isinstance(item,dict) and ('mongodb' in key or key in (
                               'user-timeline-service','post-storage-service','home-timeline-service','compose-post-service'))}
        elif name.endswith('/container-ip-mapping.json'):
            configs[name]={key:value.get('services',{}).get(key) for key in (
                SERVICE,'user-timeline-service','user-timeline-replica-a','user-timeline-replica-b')}
    after=path.stat()
    if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(
            after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):
        raise ValueError('owned original tar changed during inspection')
    return {'fixed_input':fixed,'all_original_member_bytes_SHA_modes_verified':True,
        'verified_files':len(actual),'verified_file_bytes':sum(v['bytes'] for v in actual.values()),
        'complete_member_inventory_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'capture_tar_sha256':package['sha256'],'closed_input_sha256':fixed['closed_input_sha256'],
        'selected_member_hashes':selected_claims,'DB_snapshots':snapshots or [{'verdict':'UNKNOWN','reason':'saved before/after DB snapshots absent'}],
        'selected_DB_control_commands':commands or {'verdict':'UNKNOWN','reason':'saved command log absent'},
        'reset_method_attribution':'UNKNOWN: Context logs commands, not high-level Python reset calls',
        'DB_control_outcomes':rows,'outcome_evidence':{
            'verdict':'OBSERVED' if {row['phase'] for row in rows}=={'db_up','db_down'} else 'UNKNOWN',
            'reason':'Both saved phases present' if {row['phase'] for row in rows}=={'db_up','db_down'} else 'one or both saved DB-control phases absent'},
        'DB_control_blocks':[pick(row,('id','phase','state','attempts','started_ns',
            'load_started_ns','ended_ns','completed_requests')) for row in decoded.get('blocks.json',[])
            if row.get('phase') in ('db_up','db_down')],
        'rendered_Mongo_addresses':configs or {'verdict':'UNKNOWN','reason':'saved service-config JSON absent'},
        'declared_selected_database':pick(decoded.get('deployment.json',{}).get('database',{}),
            ('logical_identity','name','node','ip','port','transport_host','transport_port')),
        'interpretation':'Snapshots bracket observations, not continuous downtime. HTTP acknowledgement is not Mongo durability. Cache/async/lost-write mechanism UNKNOWN.'}


def run():
    if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!=REPOSITORY:
        raise RuntimeError('fixed preserved-file inspection is this repository Actions only')
    if sha(PROFILE)!=PROFILE_SHA: raise ValueError('fixed reviewed source record differs')
    profile=read(PROFILE)
    root=ROOT/'work/v6-DSB-db-control'
    if any(p.is_symlink() for p in (root,*root.parents)): raise ValueError('owned output path required')
    root.mkdir(parents=True,exist_ok=True)
    report=root/'inspection.json'
    if report.exists(): raise FileExistsError('one retained reader attempt per clean job workspace')
    result={'schema':'v6-DSB-db-control-derived-metadata-v1','profile_sha256':PROFILE_SHA,
        'execution':{'run_id':os.environ['GITHUB_RUN_ID'],'source':os.environ['GITHUB_SHA']},
        'started_ns':time.time_ns(),'status':'started','arms':[],'MAIN_GO':False,
        'scope':'Saved-file read only; no VM/model/target/refit; all four adverse/UNKNOWN inputs preserved'}
    atomic(report,result)
    try:
        for fixed in profile['inputs']:
            started=time.time_ns(); cpu=os.times(); folder=root/fixed['collector'];folder.mkdir()
            current={'collector':fixed['collector'],'started_ns':started,'status':'started'}
            result['arms'].append(current);atomic(report,result)
            try:
                actual=api(f"actions/artifacts/{fixed['id']}");artifact_identity(actual,fixed)
                current['actual_artifact_API']=pick(actual,('id','name','size_in_bytes','digest','expired','workflow_run'))
                current['download_guard']=guard(root,fixed['size_in_bytes'])
                source=folder/'original.zip';current['whole_ZIP']=download(fixed,source)
                zipped,capacity=unwrap_zip(source,folder)
                current.update(ZIP_members=zipped,ZIP_members_all_EOF_CRC_verified=True,preunwrap_guard=capacity)
                package=read(folder/'capture.tar.gz.json')
                current['facts']=inspect_tar(folder/'capture.tar.gz',package,fixed)
                # Only these exact owned, fully verified ephemeral delivery copies are released.
                for path in (source,folder/'capture.tar.gz',folder/'capture.tar.gz.json'):
                    if path.is_symlink() or path.parent!=folder: raise ValueError('foreign delivery release')
                if (sha(source)!=current['whole_ZIP']['sha256'] or sha(folder/'capture.tar.gz')!=package['sha256']
                        or sha(folder/'capture.tar.gz.json')!=zipped['capture.tar.gz.json']['sha256']):
                    raise ValueError('owned delivery bytes changed before release')
                for path in (source,folder/'capture.tar.gz',folder/'capture.tar.gz.json'): path.unlink()
                current.update(status='complete',verified_ephemeral_deliveries_released=True,cloud_original_untouched=True)
            except BaseException as error:
                current.update(status='failed',error=repr(error));raise
            finally:
                end=os.times(); current.update(ended_ns=time.time_ns(),CPU_seconds={key:getattr(end,key)-getattr(cpu,key)
                    for key in ('user','system','children_user','children_system')},free_bytes_after=shutil.disk_usage(root).free)
                atomic(report,result)
        result['status']='complete'
    except BaseException as error:
        result.update(status='failed',error=repr(error));raise
    finally:
        result['ended_ns']=time.time_ns();atomic(report,result)


def self_test():
    def fixture(directory):
        fixed=dict(read(PROFILE)['inputs'][0])
        status={'study':'clean-restart-v6','system':'deathstarbench','mode':'full','seed':9,
            'stage':'qualification','smoke':True,'phase':'validation','collector':fixed['collector'],
            'run_id':str(fixed['run_id']),'commit':fixed['source'],'status':'capture_complete'}
        objects={'status.json':status,'external.json':[{'phase':'db_down','attempt_id':'one','success':True,
            'http_steps':[{'request_id':'id','status':200,'response_body_base64':'SECRET_BODY'}]}]}
        stage='before-db_down-09'
        sample={'schema':'runtime-identity-guest-sample-v5','node':'a','stage':stage,'boot_id':'boot',
            'clocks':{edge:{key:i for i,key in enumerate(('realtime_unix_ns','monotonic_ns','boottime_ns'),1)}
                      for edge in ('started','ended')},'docker_proof':{'list_returncode':0,'inspect_returncode':0},
            'containers':[{'id':'container','name':DB,'state':{'Status':'exited','Running':False,'Pid':0,
                'StartedAt':'start','FinishedAt':'finish','ExitCode':0,'response_body':'SECRET_BODY'}}]}
        sample_name='runtime-identity-v5/sample-'+stage+'-a.json'
        objects[sample_name]=sample
        encoded=lambda value:(json.dumps(value)+'\n').encode()
        sample_body=encoded(sample)
        objects['runtime-identity-v5/capture-'+stage+'.json']={'schema':'runtime-identity-capture-v5','stage':stage,
            'runner_interval':{'started_monotonic_ns':1,'ended_monotonic_ns':2},'samples':[sample],
            'files':{Path(sample_name).name:{'bytes':len(sample_body),'sha256':hashlib.sha256(sample_body).hexdigest()}}}
        files={name:encoded(value) for name,value in objects.items()}
        closed={'study':'clean-restart-v6','phase':'validation','status':status,
                'files':{name:hashlib.sha256(body).hexdigest() for name,body in files.items()}}
        files['closed-input.json']=encoded(closed)
        fixed['closed_input_sha256']=hashlib.sha256(files['closed-input.json']).hexdigest()
        path=Path(directory)/'capture.tar.gz'
        with tarfile.open(path,'w:gz') as archive:
            for name,body in files.items():
                member=tarfile.TarInfo(name);member.size=len(body);member.mode=0o640
                archive.addfile(member,io.BytesIO(body))
        package={'study':'clean-restart-v6','phase':'validation','collector':fixed['collector'],
            'run_id':fixed['run_id'],'source':fixed['source'],'case':status,'directories':[],
            'files':{name:{'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'mode':0o640}
                     for name,body in files.items()},'bytes':path.stat().st_size,'sha256':sha(path)}
        return path,package,fixed
    class Boundaries(unittest.TestCase):
        def test_actual_profile_GitLF_hash_and_all_four_inputs(self):
            self.assertEqual(sha(PROFILE),PROFILE_SHA)
            self.assertEqual({row['collector'] for row in read(PROFILE)['inputs']},{'none','obi','coroot','deepflow'})
        def test_complete_stream_integrity_and_body_free_snapshot(self):
            with tempfile.TemporaryDirectory() as directory:
                path,package,fixed=fixture(directory)
                value=inspect_tar(path,package,fixed)
                self.assertTrue(value['all_original_member_bytes_SHA_modes_verified'])
                self.assertEqual(value['verified_files'],len(package['files']))
                self.assertNotIn('SECRET_BODY',json.dumps(value))
                self.assertEqual(value['DB_snapshots'][0]['verdict'],'OBSERVED')
                self.assertFalse(value['DB_snapshots'][0]['selected_container']['state']['Running'])
                self.assertFalse(value['DB_snapshots'][0]['continuous_downtime_proven'])
        def test_member_hash_mode_and_closed_input_mutations(self):
            for kind in ('hash','mode','closed'):
                with self.subTest(kind=kind),tempfile.TemporaryDirectory() as directory:
                    path,package,fixed=fixture(directory)
                    if kind=='hash':package['files']['external.json']['sha256']='0'*64
                    elif kind=='mode':package['files']['external.json']['mode']=0o600
                    else:fixed['closed_input_sha256']='0'*64
                    with self.assertRaises(ValueError):inspect_tar(path,package,fixed)
        def test_body_free_outcomes(self):
            row={'phase':'db_down','attempt_id':'one','success':True,'request_form':{'text':'SECRET_BODY'},
                 'http_steps':[{'request_id':'opaque','status':200,'response_body_base64':'SECRET_BODY'}],
                 'validation':{'database_up':False,'response_body':'SECRET_BODY'},
                 'eventual_postcondition':{'success':None,'locations':{'user':{'found':None,'body':'SECRET_BODY'}}}}
            selected_rows=external_rows([row])
            self.assertNotIn('SECRET_BODY',json.dumps(selected_rows));self.assertEqual(selected_rows[0]['success'],True)
            self.assertIsNone(selected_rows[0]['eventual_postcondition']['success'])
        def test_all_control_rows_without_stdout(self):
            rows=[{'command':['ssh','ubuntu@192.168.76.11',"bash -lc 'docker "+action+' '+DB+"'"],
                   'started_ns':n,'ended_ns':n+1,'returncode':0,'stdout':'SECRET_BODY','stderr':'SECRET_BODY'}
                  for n,action in enumerate(('start','stop','start'))]
            selected_rows=command_rows(('\n'.join(json.dumps(r) for r in rows)).encode())
            self.assertEqual(len(selected_rows),3);self.assertNotIn('SECRET_BODY',json.dumps(selected_rows))
            foreign={'command':['ssh','ubuntu@192.168.76.11','docker stop '+DB+'-other']}
            self.assertEqual(command_rows(json.dumps(foreign).encode()),[])
        def test_artifact_wrong_origin(self):
            fixed=read(PROFILE)['inputs'][0]
            row={**fixed,'expired':False,'workflow_run':{'id':fixed['run_id'],'head_sha':fixed['source']}}
            artifact_identity(row,fixed);row['workflow_run']['head_sha']='0'*40
            with self.assertRaises(ValueError): artifact_identity(row,fixed)
        def test_missing_snapshot_is_unknown(self):
            self.assertEqual(db_snapshot('runtime-identity-v5/capture-before-db_down-10.json',{}, {},{})['verdict'],'UNKNOWN')
        def test_link_and_traversal_rejected(self):
            for name in ('../foreign','/absolute','a/../foreign','a\\foreign'):
                with self.assertRaises(ValueError):safe_name(name)
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory);path=root/'original.zip'
                with zipfile.ZipFile(path,'w') as archive:
                    link=zipfile.ZipInfo('capture.tar.gz');link.external_attr=(stat.S_IFLNK|0o777)<<16
                    archive.writestr(link,b'other');archive.writestr('capture.tar.gz.json',b'{}')
                with self.assertRaises(ValueError):unwrap_zip(path,root)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Boundaries)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful(): raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true',help='tiny synthetic metadata fixtures only')
    args=parser.parse_args()
    self_test() if args.self_test else run()
