"""Separate OTel context witnesses; never a primary capture/model input."""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time
from collections import defaultdict

import yaml

from .block_v6 import api, capacity, inventory, owned_root, pack, sha, stop_and_discard, unpack, vms
from .collectors_v5 import OBICollectorsV5
from .collectors_v6 import NoAgent, certify_controls
from .deployment_v6 import _compose, _copy_remote_assets, _tree, deploy_blueprint, get_adapter
from .runtime import Context, write_json
from .transport_v4 import Journal

ARMS = ('none', 'obi-all', 'obi-off')
CONTEXTS = ('natural', 'sampled01', 'unsampled00')
OPERATIONS = ('browse_product', 'add_to_cart', 'checkout')
SCHEMA = 'separate-context-diagnostic-v6'
MAGIC = b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'
OBI_COMMIT = 'b28e4e7fe0a01f1961b7c4747a13b8ff486d6fec'
REMOTE = '/opt/ebpf-study/context-diagnostic-v6'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def checkout():
    return Path(__file__).resolve().parents[2]


def approved_parent(path, expected_sha, mode):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('diagnostic execution is Actions only')
    supplied = Path(path).absolute()
    if any(p.is_symlink() for p in (supplied, *supplied.parents)):
        raise ValueError('parent record cannot contain symlinks')
    path = supplied.resolve()
    if not path.is_relative_to(checkout() / 'docs') or sha(path) != expected_sha:
        raise ValueError('parent record must be separately reviewed and tracked in docs')
    subprocess.run(['git', 'ls-files', '--error-unmatch', '--', path.relative_to(checkout()).as_posix()],
                   cwd=checkout(), check=True, stdout=subprocess.DEVNULL)
    value = read(path)
    if (value.get('schema'), value.get('system'), value.get('mode')) != (SCHEMA, 'otel_demo', mode):
        raise ValueError('parent record belongs to another diagnostic/SDK mode')
    if any(value.get(k) is not True for k in ('diagnostic_execution_GO',
            'root_diagnostic_execution_GO', 'independent_diagnostic_execution_GO')):
        raise ValueError('design/source approval is not diagnostic execution GO')
    if (type(value.get('parent_run_id')) is not int or value['parent_run_id'] <= 0
            or not re.fullmatch('[0-9a-f]{40}', str(value.get('parent_source', '')))
            or type(value.get('repetition')) is not int or value['repetition'] not in (9, 10, 11)
            or value.get('parent_stage') not in ('qualification', 'main')
            or type(value.get('parent_smoke')) is not bool):
        raise ValueError('parent origin/settings must be explicit v6 inputs')
    for key in ('artifact_id', 'artifact_bytes', 'shared_tar_bytes', 'shared_materialized_bytes'):
        if type(value.get(key)) is not int or value[key] <= 0:
            raise ValueError('missing exact parent size/identity: ' + key)
    if not re.fullmatch('sha256:[0-9a-f]{64}', str(value.get('artifact_digest', ''))):
        raise ValueError('parent publication digest required')
    for key in ('shared_tar_sha256', 'block_plan_sha256', 'golden_sha256', 'blueprint_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', value.get(key, '')):
            raise ValueError('missing exact parent seal: ' + key)
    artifact = api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{value['artifact_id']}")
    origin = artifact.get('workflow_run') or {}
    if (artifact.get('id'), artifact.get('name'), artifact.get('size_in_bytes'),
            artifact.get('digest'), artifact.get('expired'), origin.get('id'), origin.get('head_sha')) != (
            value['artifact_id'], f"v6-shared-blueprint-{value['parent_run_id']}",
            value['artifact_bytes'], value['artifact_digest'], False,
            value['parent_run_id'], value['parent_source']):
        raise ValueError('actual parent shared artifact tuple/source differs')
    return value, artifact


def patch_instrumentation(text):
    """Exact pinned call boundary; preserve every existing option and hook."""
    opening = 'getNodeAutoInstrumentations({'
    closing = '    })\n  ],'
    if text.count(opening) != 1 or text.count(closing) != 1 or 'context-witness-v6' in text:
        raise ValueError('pinned frontend instrumentation anchor differs')
    return ("const contextWitnessV6 = require('/app/context-witness-v6.cjs');\n"
            "contextWitnessV6.installHttp2();\n" + text.replace(
                opening, 'getNodeAutoInstrumentations(contextWitnessV6.withHttpHook({', 1)
            .replace(closing, '    }))\n  ],', 1))


def derive(parent, destination, mode):
    if destination.exists():
        raise FileExistsError('diagnostic derivative is immutable')
    original = read(parent / 'blueprint.json')
    if (original['system'] != 'otel_demo' or original['mode'] != mode or mode not in ('full', 'partial')
            or _tree(parent / 'assets') != original['assets']):
        raise ValueError('only matching full/partial OTel parent is in scope')
    capacity(destination.parent, sum(p.stat().st_size for p in parent.rglob('*') if p.is_file()))
    shutil.copytree(parent, destination)
    assets = destination / 'assets'
    observer = checkout() / 'scripts/context-witness-v6.cjs'
    shutil.copy2(observer, assets / observer.name)
    script = assets / 'source/src/frontend/utils/telemetry/Instrumentation.js'
    script.write_text(patch_instrumentation(script.read_text(encoding='utf8')), encoding='utf8')
    compose_path = assets / 'node-a.yaml'
    compose = yaml.safe_load(compose_path.read_text(encoding='utf8'))
    frontend = compose['services']['frontend']
    if any('/app/context-witness-v6.cjs' in str(v) or '/context-witness-v6' in str(v)
           for v in frontend.get('volumes', [])) or 'CONTEXT_WITNESS_V6_OUT' in frontend.get('environment', {}):
        raise ValueError('parent unexpectedly contains diagnostic observer state')
    frontend.setdefault('volumes', []).extend([
        './context-witness-v6.cjs:/app/context-witness-v6.cjs:ro',
        f'{REMOTE}:/context-witness-v6'])
    frontend.setdefault('environment', {})['CONTEXT_WITNESS_V6_OUT'] = '/context-witness-v6/sdk-witness.jsonl'
    compose_path.write_text(yaml.safe_dump(compose, sort_keys=False), encoding='utf8')
    value = read(destination / 'blueprint.json')
    value['assets'] = _tree(assets)
    value['diagnostic_derivative'] = {'schema': SCHEMA, 'parent_blueprint_sha256': sha(parent/'blueprint.json'),
        'observer_sha256': sha(observer), 'SDK_mode_preserved': True,
        'primary_data_use': False, 'performance_equivalence_to_primary_claimed': False}
    if value['images'] != original['images'] or any(value['nodes'][n]['services'] !=
            original['nodes'][n]['services'] for n in ('a', 'b')):
        raise ValueError('diagnostic cannot replace an application image')
    write_json(destination / 'blueprint.json', value)
    return sha(destination / 'blueprint.json')


def resolve_derivative(root, mode, golden_sha):
    """Use the real frozen guest Compose parser; never guess normalization."""
    label='context-blueprint'
    value=read(root/'derivative/blueprint.json')
    try:
        vms(root,'start',label,golden_sha)
        ctx=Context(root/'derivative-preparation',mode,value['seed'],vm_dir=root/'vms/active')
        adapter=get_adapter(ctx,'otel_demo')
        capacity(root,sum(p.stat().st_size for p in (root/'derivative/assets').rglob('*') if p.is_file()))
        shutil.copytree(root/'derivative/assets',adapter.bundle)
        _copy_remote_assets(ctx,adapter,'otel_demo')
        for node in ('a','b'):
            value['nodes'][node]['resolved_compose']=json.loads(ctx.node_exec(
                node,_compose('otel_demo',node,'config --format json')).stdout)
        value['diagnostic_derivative']['resolved_with_frozen_guest_compose']=True
        write_json(root/'derivative/blueprint.json',value)
    finally:
        stop_and_discard(root,label)
    return sha(root/'derivative/blueprint.json')


class DiagnosticOBI(OBICollectorsV5):
    def __init__(self, ctx, propagation):
        if propagation not in ('all', 'disabled'):
            raise ValueError('pinned OBI propagation value is all or disabled')
        self.propagation = propagation
        super().__init__(ctx)

    def _write_config(self, node, port):
        path, remote = super()._write_config(node, port)
        value = yaml.safe_load(path.read_text(encoding='utf8'))
        if value['ebpf']['context_propagation'] != 'all':
            raise ValueError('primary OBI setting changed')
        value['ebpf']['context_propagation'] = self.propagation
        path.write_text(yaml.safe_dump(value, sort_keys=False), encoding='utf8')
        return path, remote

    def _config_summary(self):
        return {**super()._config_summary(), 'context_propagation': self.propagation,
                'diagnostic_only': True, 'pinned_propagation_parser_commit': OBI_COMMIT}


def actual_runtime_configuration(ctx, collector, derivative):
    """Read actual config mounts/env/image IDs; never infer them from an arm label."""
    expected = read(derivative / 'blueprint.json')
    frontend_id = ctx.node_exec('a', _compose('otel_demo', 'a', 'ps -q frontend')).stdout.strip()
    if not re.fullmatch('[0-9a-f]{12,64}', frontend_id):
        raise ValueError('ambiguous actual frontend process container')
    frontend = json.loads(ctx.node_exec('a', 'docker inspect ' + frontend_id).stdout)
    if len(frontend) != 1 or frontend[0]['Image'] != expected['nodes']['a']['services']['frontend']['image_id']:
        raise ValueError('actual diagnostic frontend image differs from frozen parent')
    frontend = frontend[0]
    env = dict(item.split('=', 1) for item in frontend['Config']['Env'])
    if env.get('CONTEXT_WITNESS_V6_OUT') != '/context-witness-v6/sdk-witness.jsonl':
        raise ValueError('actual observer output differs from derivative')
    observed_sources = {}
    for filename in ('context-witness-v6.cjs', 'source/src/frontend/utils/telemetry/Instrumentation.js'):
        source = '/opt/ebpf-study/otel_demo/' + filename
        observed = ctx.node_exec('a', 'sha256sum ' + shlex.quote(source)).stdout.split()[0]
        if observed != sha(derivative / 'assets' / filename):
            raise ValueError('actual mounted diagnostic source differs')
        observed_sources[source] = observed
    for destination, source in (('/app/context-witness-v6.cjs', '/opt/ebpf-study/otel_demo/context-witness-v6.cjs'),
            ('/app/Instrumentation.js', '/opt/ebpf-study/otel_demo/source/src/frontend/utils/telemetry/Instrumentation.js')):
        mounts = [m for m in frontend['Mounts'] if m['Destination'] == destination]
        if len(mounts) != 1 or mounts[0]['Source'] != source or mounts[0].get('RW') is not False:
            raise ValueError('diagnostic runtime source must be the exact readonly bindmount')
    result = {'frontend_container': frontend, 'actual_source_sha256': observed_sources,
              'observer_sha256': sha(derivative / 'assets/context-witness-v6.cjs'),
              'SDK_mode_preserved': True, 'agent': {'collector': collector.collector}}
    if isinstance(collector, DiagnosticOBI):
        result['agent'].update(context_propagation=collector.propagation, nodes={})
        for node in ('a', 'b'):
            config = collector.root / f'config-{node}.yaml'
            remote = '/tmp/collector-v5-obi.yaml'
            observed = ctx.node_exec(node, 'sha256sum ' + remote).stdout.split()[0]
            containers = json.loads(ctx.node_exec(node, 'docker inspect ' + collector.container_name).stdout)
            if len(containers) != 1 or observed != sha(config):
                raise ValueError('actual OBI configuration bytes differ')
            container = containers[0]
            environment = dict(item.split('=', 1) for item in container['Config']['Env'])
            mounts = [m for m in container['Mounts'] if m['Destination'] == '/config.yaml']
            if (environment.get('OTEL_EBPF_CONFIG_PATH') != '/config.yaml'
                    or environment.get('OTEL_EBPF_BPF_CONTEXT_PROPAGATION', collector.propagation) != collector.propagation
                    or len(mounts) != 1 or mounts[0]['Source'] != remote or mounts[0].get('RW') is not False
                    or yaml.safe_load(config.read_text(encoding='utf8'))['ebpf']['context_propagation'] != collector.propagation):
                raise ValueError('actual OBI propagation setting/mount/env differs')
            result['agent']['nodes'][node] = {'config_sha256': observed, 'container': container}
    write_json(ctx.out / 'runtime-context-configuration.json', result)
    return result


def external_parent(request_id, kind):
    if kind == 'natural':
        return {}
    if kind not in CONTEXTS:
        raise ValueError('unknown fixed context condition')
    trace_id = hashlib.sha256(('trace:' + request_id).encode()).hexdigest()[:32]
    span_id = hashlib.sha256(('parent:' + request_id).encode()).hexdigest()[:16]
    return {'traceparent': f"00-{trace_id}-{span_id}-{'01' if kind == 'sampled01' else '00'}"}


def issue_operations(adapter, arm, output):
    """Use unchanged operation planning/body/verification, changing only the
    prespecified external traceparent input. Unattempted suffixes stay explicit.
    """
    from systems.otel_demo import experiment_v4 as original
    underlying = original._v4_request
    records, transports = [], []
    for index, (context, operation) in enumerate((context, operation)
            for context in CONTEXTS for operation in OPERATIONS):
        namespace = f'context-diagnostic-v6-{adapter.mode}-{arm}-{context}'
        records.append({'condition': context, 'operation': operation, 'index': index,
                        'namespace': namespace, 'plan': adapter.plan_operation(operation, index, namespace),
                        'actual': None, 'status': 'not_attempted'})
    condition = None
    def request(method, url, **kwargs):
        headers = dict(kwargs.get('headers') or {})
        request_id = next(v for k, v in headers.items() if k.lower() == 'x-experiment-request-id')
        if any(k.lower() in ('traceparent', 'tracestate', 'baggage') for k in headers):
            raise ValueError('unexpected pre-existing driver context')
        headers.update(external_parent(request_id, condition))
        kwargs['headers'] = headers
        item = {'request_id': request_id, 'condition': condition, 'method': method, 'url': url,
                'prespecified_headers': headers, 'started_ns': time.time_ns()}
        transports.append(item)
        try:
            response = underlying(method, url, **kwargs)
            actual=dict(response.request.headers)
            item.update(actual_sent_headers=actual, status=response.status_code)
            w3c={k.lower():v for k,v in actual.items() if k.lower() in ('traceparent','tracestate','baggage')}
            if w3c != external_parent(request_id,condition):
                raise RuntimeError('driver actually sent unplanned external context')
            return response
        finally:
            item['ended_ns'] = time.time_ns()
    original._v4_request = request
    try:
        for item in records:
            condition = item['condition']
            item.update(status='started', started_ns=time.time_ns())
            try:
                item['actual'] = adapter.operation(item['operation'], item['index'], item['namespace'])
                item['status'] = 'returned_actual_outcome'
            except BaseException as error:
                item.update(status='technical_failure', error=repr(error))
                raise
            finally: item['ended_ns'] = time.time_ns()
    finally:
        original._v4_request = underlying
        write_json(output / 'operations.json', records)
        write_json(output / 'driver-transports.json', transports)
    ids = [s['request_id'] for row in records for s in row['plan']['http_steps']]
    if len(records) != 9 or len(ids) != 18 or len(set(ids)) != 18:
        raise ValueError('fixed diagnostic intention/ID counts changed')
    return {'logical_operations': 9, 'planned_HTTP_steps': 18, 'attempted_HTTP_steps': len(transports),
            'unattempted_suffixes_retained': True, 'positive_result_required': False}


def sdk_summary(path, operations, observer_sha256):
    try:
        events=[json.loads(line) for line in path.read_text(encoding='utf8').splitlines() if line.strip()]
    except (OSError, ValueError) as error:
        events=[]
        read_error=repr(error)
    else: read_error=None
    instances=defaultdict(list)
    for row in events: instances[row.get('instanceId')].append(row)
    complete=bool(events) and all(instance and all(
        row.get('schema')=='context-witness-v6' and row.get('sequence')==i
        for i,row in enumerate(rows,1)) and len([row for row in rows if row.get('kind')=='observer-installed'
            and row.get('observerSha256')==observer_sha256
            and row.get('httpInstrumentation',{}).get('version')=='0.221.0'])==1
        for instance,rows in instances.items())
    results=[]
    for operation in operations:
        for step in operation['plan']['http_steps']:
            matches=[]
            for row in events:
                if row.get('kind')!='http-request-hook' or row.get('requestType')!='IncomingMessage':continue
                headers=row.get('headers')
                if isinstance(headers,list) and any(str(k).lower()=='x-experiment-request-id' and v==step['request_id'] for k,v in headers):
                    matches.append(row)
            result={'request_id':step['request_id'],'condition':operation['condition'],'verdict':'UNKNOWN'}
            if complete and len(matches)==1:
                row=matches[0];passed=row.get('passedSpan') or {};context=passed.get('spanContext') or {}
                if (re.fullmatch('[0-9a-f]{32}',context.get('traceId','')) and context['traceId']!='0'*32
                        and re.fullmatch('[0-9a-f]{16}',context.get('spanId','')) and context['spanId']!='0'*16
                        and type(context.get('traceFlags')) is int and 0 <= context['traceFlags'] <= 255
                        and type(passed.get('isRecording')) is bool):
                    result.update(verdict='OBSERVED',passedSpan=passed,activeSpan=row.get('activeSpan'),
                                  received_API_headers=row['headers'])
            if result['verdict']=='UNKNOWN':result['reason']='missing/ambiguous/incomplete SDK hook witness; not proof of absent context'
            results.append(result)
    return {'event_sequence_complete':complete,'read_error':read_error,'HTTP_steps':results,
            'http2_dispatches':[e for e in events if e.get('kind') in ('http2-session-connect','http2-dispatch','http2-stream-id')],
            'SDK_span_equals_active_span_assumed':False,'sampled_flag_equals_recording_assumed':False}


def start_wire(ctx, node):
    ctx.node_exec(node, f'sudo mkdir -p {REMOTE} && sudo chown $(id -u):$(id -g) {REMOTE} && chmod 0777 {REMOTE}')
    code = """import json,os,pathlib,subprocess,time
p=pathlib.Path('/opt/ebpf-study/context-diagnostic-v6');log=p/'tcpdump.log'
assert not log.exists() and not (p/'wire.pcap').exists()
os.umask(0o022)
with log.open('wb') as stream:
 argv=['tcpdump','-i','any','-s','0','-U','-Z','root','-w',str(p/'wire.pcap'),'tcp and not port 22']
 child=subprocess.Popen(argv,stdout=stream,stderr=stream,start_new_session=True)
 deadline=time.monotonic()+15
 while True:
  assert child.poll() is None,'tcpdump exited before readiness'
  current=[os.fsdecode(v) for v in (pathlib.Path('/proc')/str(child.pid)/'cmdline').read_bytes().rstrip(b'\\0').split(b'\\0')]
  if current==argv and (p/'wire.pcap').is_file() and 'listening on' in log.read_text(errors='replace'):break
  assert time.monotonic()<deadline,'tcpdump did not become ready before application start'
  time.sleep(.1)
 row={'pid':child.pid,'start_ticks':(pathlib.Path('/proc')/str(child.pid)/'stat').read_text().rsplit(') ',1)[1].split()[19],'argv':(pathlib.Path('/proc')/str(child.pid)/'cmdline').read_bytes().rstrip(b'\\0').split(b'\\0')}
 row['argv']=[os.fsdecode(v) for v in row['argv']]
 print(json.dumps(row))
"""
    value = json.loads(ctx.node_exec(node, 'sudo python3 -c ' + shlex.quote(code)).stdout)
    ctx.node_exec(node, f'test -f {REMOTE}/wire.pcap', timeout=30)
    return value


def stop_wire(ctx, node, expected):
    code = """import json,os,pathlib,signal,sys,time
e=json.loads(sys.argv[1]);p=pathlib.Path('/proc')/str(e['pid']);fd=os.pidfd_open(e['pid'])
try:
 assert p.joinpath('stat').read_text().rsplit(') ',1)[1].split()[19]==e['start_ticks']
 assert [os.fsdecode(v) for v in p.joinpath('cmdline').read_bytes().rstrip(b'\\0').split(b'\\0')]==e['argv']
 assert pathlib.Path(e['argv'][0]).name=='tcpdump' and e['argv'][-1]=='tcp and not port 22'
 signal.pidfd_send_signal(fd,signal.SIGINT)
finally:os.close(fd)
deadline=time.monotonic()+30
def alive():
 try:return p.joinpath('stat').read_text().rsplit(') ',1)[1].split()[0]!='Z'
 except FileNotFoundError:return False
while alive():
 assert time.monotonic()<deadline,'capture did not stop cleanly'
 time.sleep(.1)
root=pathlib.Path('/opt/ebpf-study/context-diagnostic-v6')
print(json.dumps({n:{'bytes':(root/n).stat().st_size,'sha256':__import__('hashlib').file_digest((root/n).open('rb'),'sha256').hexdigest()} for n in ('wire.pcap','tcpdump.log')}))
"""
    value = json.loads(ctx.node_exec(node, 'sudo python3 -c ' + shlex.quote(code) + ' ' +
                                    shlex.quote(json.dumps(expected)), timeout=45).stdout)
    target = ctx.out / 'wire' / node
    target.mkdir(parents=True)
    capacity(ctx.out, sum(row['bytes'] for row in value.values()))
    for name, row in value.items():
        ctx.node_get(node, f'{REMOTE}/{name}', target / name)
        if (target/name).stat().st_size != row['bytes'] or sha(target/name) != row['sha256']:
            raise ValueError('wire transfer bytes/SHA differ')
    write_json(target / 'capture-proof.json', {'owned_process': expected, 'files': value,
               'capture_started_before_application_deployment': True})
    return target


def frames(data, preface):
    cursor = len(MAGIC) if preface else 0
    while cursor < len(data):
        if len(data) - cursor < 9: raise ValueError('incomplete HTTP2 frame header')
        length = int.from_bytes(data[cursor:cursor+3], 'big')
        kind, flags = data[cursor+3], data[cursor+4]
        stream = int.from_bytes(data[cursor+5:cursor+9], 'big') & 0x7fffffff
        cursor += 9
        if len(data) - cursor < length: raise ValueError('incomplete HTTP2 frame payload')
        yield kind, flags, stream, data[cursor:cursor+length]
        cursor += length


def tcp_prefix(packets):
    syn = {int(p['seq']) for p in packets if p.get('syn') == '1'}
    if len(syn) != 1: raise ValueError('missing or ambiguous TCP SYN prefix')
    first = (next(iter(syn)) + 1) & 0xffffffff
    chunks = sorted((((int(p['seq'])-first)&0xffffffff), bytes.fromhex(p['payload']))
                    for p in packets if p.get('payload'))
    data = bytearray()
    for offset, chunk in chunks:
        if offset > len(data): raise ValueError('missing captured TCP bytes')
        overlap = min(len(data)-offset, len(chunk))
        if data[offset:offset+overlap] != chunk[:overlap]: raise ValueError('conflicting TCP retransmission')
        data.extend(chunk[overlap:])
    return data


def decode_packets(rows, no_capture_drops):
    """Only complete captured TCP prefixes can produce observed HPACK headers.
    Unsupported settings, gaps, TLS or missing prefix remain UNKNOWN.
    """
    from hpack import Decoder
    groups = {}
    for row in rows:
        if not all(row.get(k) for k in ('src', 'dst', 'sport', 'dport', 'seq')): continue
        key = tuple(row[k] for k in ('src','sport','dst','dport'))
        groups.setdefault(key, []).append(row)
    result = []
    for key, packets in groups.items():
        if not any(p.get('payload') for p in packets): continue
        record = {'flow': list(key), 'verdict': 'UNKNOWN', 'headers': [], 'reasons': []}
        try:
            data = tcp_prefix(packets)
            if not data.startswith(MAGIC):
                raise ValueError('TLS or no HTTP2 client preface; not decoded as HTTP2')
            reverse = (key[2], key[3], key[0], key[1])
            peer = list(frames(tcp_prefix(groups.get(reverse, [])), False))
            if not peer or peer[0][0] != 4 or peer[0][1] & 1 or peer[0][2] != 0:
                raise ValueError('missing captured initial peer SETTINGS')
            # Peer settings constrain the CLIENT encoder. Do not mistake the
            # client's settings (which constrain server response encoding) for these.
            for kind, flags, stream, body in peer:
                if kind != 4: continue
                if stream != 0 or (flags & 1 and body) or (not flags & 1 and len(body) % 6):
                    raise ValueError('malformed peer SETTINGS')
                if not flags & 1:
                    for i in range(0, len(body), 6):
                        if int.from_bytes(body[i:i+2], 'big') == 1 and int.from_bytes(body[i+2:i+6], 'big') != 4096:
                            raise ValueError('nondefault peer dynamic-table setting requires separate qualification')
            decoder = Decoder(max_header_list_size=2**63-1)
            pending, pending_stream = bytearray(), None
            first_frame = True
            for kind, flags, stream, body in frames(data, True):
                if first_frame and (kind != 4 or flags & 1 or stream != 0):
                    raise ValueError('missing captured initial client SETTINGS')
                first_frame = False
                if pending_stream is not None and (kind != 9 or stream != pending_stream):
                    raise ValueError('interrupted HTTP2 CONTINUATION')
                if kind == 4 and (stream != 0 or (flags & 1 and body) or (not flags & 1 and len(body) % 6)):
                    raise ValueError('malformed client SETTINGS')
                if kind == 1:
                    if stream == 0 or len(body) < (1 if flags & 8 else 0) + (5 if flags & 32 else 0):
                        raise ValueError('malformed HEADERS padding/priority/stream')
                    pad = body[0] if flags & 8 else 0
                    body = body[(1 if flags & 8 else 0) + (5 if flags & 32 else 0):]
                    if pad > len(body): raise ValueError('invalid header padding')
                    pending.extend(body[:-pad] if pad else body);pending_stream = stream
                elif kind == 9:
                    if pending_stream != stream: raise ValueError('unmatched CONTINUATION')
                    pending.extend(body)
                if kind in (1,9) and flags & 4:
                    headers = decoder.decode(bytes(pending), raw=True)
                    record['headers'].append({'stream_id': stream, 'fields': [
                        {'name_b64': base64.b64encode(n).decode(), 'value_b64': base64.b64encode(v).decode()}
                        for n,v in headers if n.lower() in (b'traceparent',b'tracestate',b'baggage',
                            b'x-experiment-request-id',b':method',b':path',b':authority')]})
                    pending.clear();pending_stream = None
            if pending_stream is not None: raise ValueError('incomplete HPACK header block')
            if no_capture_drops is not True: raise ValueError('capture drops or missing drop counters')
            record['verdict'] = 'OBSERVED' if record['headers'] else 'UNKNOWN'
            if not record['headers']: record['reasons'].append('no HTTP2 header block')
        except Exception as error:
            record['reasons'].append(str(error))
            # Partial decoded blocks are retained but cannot be claimed complete.
        result.append(record)
    return result


def decode_wire(folder):
    log = (folder / 'tcpdump.log').read_text(encoding='utf8', errors='replace')
    dropped = re.findall(r'(\d+) packets dropped by kernel', log)
    interface = re.findall(r'(\d+) packets dropped by interface', log)
    no_drops = len(dropped) == 1 and int(dropped[0]) == 0 and not any(int(v) for v in interface)
    names = ('src','dst','sport','dport','seq','syn','payload')
    fields = ('ip.src','ip.dst','tcp.srcport','tcp.dstport','tcp.seq_raw','tcp.flags.syn','tcp.payload')
    command = ['tshark','-n','-r',str(folder/'wire.pcap'),'-Y','tcp','-T','fields','-E','separator=\t']
    for name in fields: command.extend(['-e',name])
    with (folder/'tcp-fields.tsv').open('w', encoding='utf8') as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.PIPE, text=True)
    write_json(folder/'decode-command.json', {'argv':command,'returncode':result.returncode,'stderr':result.stderr})
    if result.returncode:
        value={'verdict':'UNKNOWN','reason':'packet extraction failed'}
        write_json(folder/'http2-witness.json',value)
        return value
    with (folder/'tcp-fields.tsv').open(encoding='utf8') as source:
        rows = [dict(zip(names,row)) for row in csv.reader(source,delimiter='\t') if len(row)==len(names)]
    value = {'kernel_drop_counter': dropped, 'interface_drop_counter': interface,
             'capture_no_reported_drops': no_drops, 'streams':decode_packets(rows,no_drops),
             'scope':'client HTTP2 header decoding only; no TLS decryption, SDK parentage or writer attribution'}
    value['verdict'] = 'OBSERVED' if any(s['verdict']=='OBSERVED' for s in value['streams']) else 'UNKNOWN'
    write_json(folder/'http2-witness.json',value)
    return value


def import_parent(root, parent, mode):
    source = root/'parent'
    for name in ('shared.tar.gz', 'shared.tar.gz.json', 'shared-seal.json', 'block-plan.json'):
        path=source/name
        if not path.is_file() or any(p.is_symlink() for p in (path,*path.parents)):
            raise ValueError('parent input must be an owned regular download')
    plan,seal,package=[read(source/name) for name in ('block-plan.json','shared-seal.json','shared.tar.gz.json')]
    if ((plan.get('study'),plan.get('system'),plan.get('mode'),plan.get('repetition'),
            plan.get('run_id'),plan.get('source'),plan.get('stage'),plan.get('smoke')) != (
            'clean-restart-v6','otel_demo',mode,parent['repetition'],parent['parent_run_id'],
            parent['parent_source'],parent['parent_stage'],parent['parent_smoke'])
            or sha(source/'block-plan.json') != parent['block_plan_sha256']
            or seal != {'block_plan_sha256':parent['block_plan_sha256'],
                        'shared_sha256':parent['shared_tar_sha256'],
                        'golden_sha256':parent['golden_sha256'],
                        'blueprint_sha256':parent['blueprint_sha256']}
            or package['sha256'] != parent['shared_tar_sha256']
            or package['bytes'] != parent['shared_tar_bytes']
            or (source/'shared.tar.gz').stat().st_size != package['bytes']
            or sum(r['bytes'] for r in package['files'].values()) != parent['shared_materialized_bytes']):
        raise ValueError('diagnostic parent plan/delivery seals or byte budget differ')
    guard=unpack(source/'shared.tar.gz',root,parent['shared_tar_sha256'],guard_root=root)
    actual={}
    for folder in ('vms/golden','blueprint'):
        actual.update({folder+'/'+name:claim for name,claim in inventory(root/folder).items()})
    if actual != package['files'] or (sha(root/'vms/golden/manifest.json'),sha(root/'blueprint/blueprint.json')) != (
            parent['golden_sha256'],parent['blueprint_sha256']):
        raise ValueError('all actual shared image/guest/config bytes must remain identical')
    shutil.copyfile(source/'block-plan.json',root/'parent-block-plan.json')
    write_json(root/'parent-import-receipt.json',{'actual_disk_guard':guard,
        'original_parent_identity':{'run_id':parent['parent_run_id'],'source':parent['parent_source']},
        'shared_tar_sha256':parent['shared_tar_sha256'],'all_original_files_SHA_bytes_modes_verified':True})


def run(args):
    root = owned_root(args.root)
    parent, artifact = approved_parent(args.parent_record,args.parent_record_sha256,args.mode)
    if (root/'derivative').exists(): raise FileExistsError('diagnostic does not retry/replace arms')
    write_json(root/'actual-parent-artifact.json',artifact)
    shutil.copyfile(Path(args.parent_record),root/'diagnostic-parent-record.json')
    write_json(root/'diagnostic-plan.json',{'schema':SCHEMA,'mode':args.mode,'arms':ARMS,
        'contexts':CONTEXTS,'operations':OPERATIONS,'operations_per_arm':9,'HTTP_steps_per_arm':18,
        'logical_operations_per_mode':27,'HTTP_steps_per_mode':54,'repetitions_per_combination':1,
        'execution_run_id':os.environ['GITHUB_RUN_ID'],'execution_source':os.environ['GITHUB_SHA'],
        'parent_record_sha256':args.parent_record_sha256,'primary_data_use':False})
    import_parent(root,parent,args.mode)
    derive(root/'blueprint',root/'derivative',args.mode)
    derivative_sha = resolve_derivative(root,args.mode,parent['golden_sha256'])
    receipts=[];frontend_environments=[]
    for arm in ARMS:
        label='context-'+arm
        ctx=Context(root/arm,args.mode,read(root/'blueprint/blueprint.json')['seed'],vm_dir=root/'vms/active')
        ctx.collector='none' if arm=='none' else 'obi'
        ctx.journal=Journal(ctx.out/'diagnostic-journal.sqlite')
        collector=NoAgent(ctx) if arm=='none' else DiagnosticOBI(ctx,'all' if arm=='obi-all' else 'disabled')
        status={'schema':SCHEMA,'arm':arm,'mode':args.mode,'started_ns':time.time_ns(),'status':'started',
                'parent_blueprint_sha256':parent['blueprint_sha256'],'derivative_sha256':derivative_sha,
                'primary_data_use':False,'errors':[]}
        write_json(ctx.out/'diagnostic-status.json',status)
        captures={};adapter=None
        try:
            vms(root,'start',label,parent['golden_sha256'])
            for node in ('a','b'):captures[node]=start_wire(ctx,node)
            collector.start()
            adapter=deploy_blueprint(ctx,'otel_demo',root/'derivative',expected_sha256=derivative_sha)
            adapter.ready();collector.settle();certify_controls(collector)
            runtime=actual_runtime_configuration(ctx,collector,root/'derivative')
            environment=sorted(runtime['frontend_container']['Config']['Env'])
            if frontend_environments and environment != frontend_environments[0]:
                raise ValueError('frontend SDK/sampler/observer environment differs between diagnostic arms')
            frontend_environments.append(environment)
            status.update(issue_operations(adapter,arm,ctx.out))
            collector.final_drain()
            adapter.collect_native(ctx.out/'native-diagnostic')
            status['status']='complete'
        except BaseException as error:
            status['errors'].append(repr(error));status['status']='technical_failure'
        finally:
            for name,action in [('application',lambda:adapter.close() if adapter else None),('collector',collector.close)]:
                try:action()
                except Exception as error:status['errors'].append(name+':'+repr(error))
            for node,expected in captures.items():
                try:decode_wire(stop_wire(ctx,node,expected))
                except Exception as error:status['errors'].append('wire-'+node+':'+repr(error))
            try:
                ctx.node_get('a',REMOTE+'/sdk-witness.jsonl',ctx.out/'sdk-witness.jsonl')
                if (ctx.out/'operations.json').exists():
                    write_json(ctx.out/'sdk-summary.json',sdk_summary(ctx.out/'sdk-witness.jsonl',
                        read(ctx.out/'operations.json'),sha(root/'derivative/assets/context-witness-v6.cjs')))
            except Exception as error:
                # Missing witness is an UNKNOWN result, not a positive-result retry condition.
                write_json(ctx.out/'sdk-summary.json',{'verdict':'UNKNOWN','reason':repr(error)})
            try:stop_and_discard(root,label)
            except Exception as error:status['errors'].append('guest-cleanup:'+repr(error))
            ctx.journal.close()
            if status['errors']: status['status']='technical_failure'
            status['ended_ns']=time.time_ns()
            write_json(ctx.out/'diagnostic-status.json',status);receipts.append(status)
            write_json(root/'diagnostic-summary.json',{'schema':SCHEMA,'arms':receipts,'primary_data_use':False,
                'expected_arms':ARMS,'planned_operations_per_mode':27,'planned_HTTP_steps_per_mode':54,
                'execution_status':'complete' if len(receipts)==3 and all(
                    r['status']=='complete' and not r['errors'] for r in receipts) else 'partial',
                'no_unavailable_witness_imputed':True,'header_writer_inferred':False})
        if status['status']!='complete' or status['errors']:
            raise RuntimeError('diagnostic attempt retained; no automatic retry or next-arm repair')


def package_output(root):
    if os.environ.get('GITHUB_ACTIONS') != 'true': raise RuntimeError('diagnostic packaging is Actions only')
    root=owned_root(root)
    def selected_name(name):
        if name in ('derivative/assets/context-witness-v6.cjs','derivative/assets/node-a.yaml',
                    'derivative/assets/source/src/frontend/utils/telemetry/Instrumentation.js','blueprint/blueprint.json'):
            return True
        return (not any(name.startswith(prefix) for prefix in
            ('parent/','blueprint/','derivative/assets/','derivative/images/','vms/golden/','derivative-preparation/deployment/'))
            and '/deployment/' not in name and not name.endswith(('.qcow2','id_ed25519','id_ed25519.pub')))
    # Parent images/guest templates remain in their original shared artifact.
    # Keep actual diagnostics and the precise changed runtime source instead.
    selected={p.relative_to(root).as_posix():None for p in root.rglob('*') if p.is_file()
              and selected_name(p.relative_to(root).as_posix())}
    pack(root,root.parent/'context-diagnostic.tar.gz',selected)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('preflight','run','package'))
    parser.add_argument('--mode',choices=('full','partial'),required=True)
    parser.add_argument('--root',type=Path,default=Path('work/context-diagnostic'))
    parser.add_argument('--parent-record',type=Path,required=True)
    parser.add_argument('--parent-record-sha256',required=True)
    args=parser.parse_args()
    root=owned_root(args.root)
    cpu=lambda:{k:getattr(os.times(),k) for k in ('user','system','children_user','children_system')}
    cost={'command':args.command,'started_ns':time.time_ns(),'CPU_seconds_start':cpu(),'status':'started',
          'CPU_scope':'controller/waited children; independently daemonized QEMU/guest CPU not included',
          'execution_run_id':os.environ.get('GITHUB_RUN_ID'),'execution_source':os.environ.get('GITHUB_SHA')}
    write_json(root/f'context-{args.command}-status.json',cost)
    try:
        if args.command=='preflight':
            value,artifact=approved_parent(args.parent_record,args.parent_record_sha256,args.mode)
            capacity(root,artifact['size_in_bytes']+value['shared_materialized_bytes']+value['shared_tar_bytes'])
            with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf8') as output:
                output.write(f"artifact_id={value['artifact_id']}\nparent_run_id={value['parent_run_id']}\n")
        elif args.command=='run':run(args)
        else:package_output(root)
        cost['status']='complete'
    except BaseException as error:
        cost.update(status='failed',error=repr(error));raise
    finally:
        cost.update(ended_ns=time.time_ns(),CPU_seconds_end=cpu(),free_bytes_end=shutil.disk_usage(root).free)
        write_json(root/f'context-{args.command}-status.json',cost)
        with (root/'context-controller-cost.jsonl').open('a',encoding='utf8') as stream:
            stream.write(json.dumps(cost)+'\n')


if __name__=='__main__':main()
