"""Observer/decoder boundary fixtures only; no guests, applications or agents."""
from copy import deepcopy
import base64
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from ebpf_discovery import context_diagnostic_v6 as diagnostic


def test_node_observer_preserves_hooks_arguments_and_nonrecording_context():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node is installed explicitly in the diagnostic source qualification job')
    source = diagnostic.checkout() / 'scripts/context-witness-v6.cjs'
    code = r"""
const assert=require('node:assert/strict'),{EventEmitter}=require('node:events');
const {createObserver}=require(process.argv[1]);
const rows=[];
const passed={spanContext:()=>({traceId:'1'.repeat(32),spanId:'2'.repeat(16),traceFlags:0}),isRecording:()=>false};
const active={spanContext:()=>({traceId:'3'.repeat(32),spanId:'4'.repeat(16),traceFlags:1}),isRecording:()=>true};
const context={};
const api=Object.freeze({context:Object.freeze({active:()=>context}),trace:Object.freeze({getSpan:c=>{assert.equal(c,context);return active}})});
const session=new EventEmitter(), stream=new EventEmitter();
stream.id=undefined;
const headers=Object.freeze({':method':'POST',':path':'/Service/Call',traceparent:'literal',extra:'not selected'});
const options=Object.freeze({endStream:false});
let calls=0;
session.request=function(h,o){assert.equal(this,session);assert.equal(h,headers);assert.equal(o,options);calls++;return stream};
const h2={connect:function(address,opts){assert.equal(this,h2);assert.equal(address,'http://peer');assert.equal(opts,options);return session}};
const observer=createObserver(api,line=>rows.push(JSON.parse(line)),h2,()=>({version:'0.221.0'}));
observer.installHttp2();
const receiver={}; let oldCalls=0;
const old=Object.freeze({enabled:false,headersToSpanAttributes:Object.freeze({server:'preserved'}),requestHook:function(...args){assert.equal(this,receiver);assert.equal(args[0],passed);oldCalls++;return 'old-result'}});
const initial=Object.freeze({'@opentelemetry/instrumentation-http':old,other:Object.freeze({enabled:false})});
const patched=observer.withHttpHook(initial);
assert.equal(patched.other,initial.other); assert.equal(patched['@opentelemetry/instrumentation-http'].enabled,false);
assert.equal(patched['@opentelemetry/instrumentation-http'].headersToSpanAttributes,old.headersToSpanAttributes);
const request=Object.freeze({constructor:{name:'IncomingMessage'},method:'GET',url:'/api',rawHeaders:Object.freeze(['traceparent','input','X-Experiment-Request-Id','opaque'])});
assert.equal(patched['@opentelemetry/instrumentation-http'].requestHook.call(receiver,passed,request),'old-result');
assert.equal(oldCalls,1); assert.equal(initial['@opentelemetry/instrumentation-http'],old);
const hook=rows.find(r=>r.kind==='http-request-hook');
assert.equal(hook.passedSpan.isRecording,false);assert.equal(hook.passedSpan.spanContext.traceFlags,0);
assert.notEqual(hook.passedSpan.spanContext.traceId,hook.activeSpan.spanContext.traceId);
const hostile={get rawHeaders(){throw new Error('read unavailable')}};
assert.equal(patched['@opentelemetry/instrumentation-http'].requestHook.call(receiver,passed,hostile),'old-result');
assert(rows.some(r=>r.kind==='http-request-hook-read-error'));
assert.equal(h2.connect('http://peer',options),session);
assert.equal(session.request(headers,options),stream);assert.equal(calls,1);
stream.id=7;stream.emit('ready');
const dispatch=rows.find(r=>r.kind==='http2-dispatch');
assert.equal(dispatch.headersMutatedByObserver,false);assert.deepEqual(headers,{':method':'POST',':path':'/Service/Call',traceparent:'literal',extra:'not selected'});
assert.equal(rows.find(r=>r.kind==='http2-stream-id').streamId,7);
assert.equal(rows[0].sdkProviderInstalledByObserver,false);
assert.equal(rows[0].spansCreatedByObserver,false);
assert(rows.every((r,i)=>r.sequence===i+1 && r.instanceId===rows[0].instanceId));
console.log(JSON.stringify({fixture:'PASS',events:rows.length}));
"""
    result = subprocess.run([node, '-e', code, str(source)], check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)['fixture'] == 'PASS'


def test_instrumentation_patch_preserves_original_options_and_rejects_drift():
    before = "const sdk = new SDK({instrumentations: [\n    getNodeAutoInstrumentations({\n      existing: { enabled: false },\n    })\n  ],\n});\n"
    after = diagnostic.patch_instrumentation(before)
    assert 'existing: { enabled: false }' in after
    assert 'getNodeAutoInstrumentations(contextWitnessV6.withHttpHook({' in after
    assert after.index('installHttp2()') < after.index('new SDK')
    with pytest.raises(ValueError, match='anchor'):
        diagnostic.patch_instrumentation(after)
    with pytest.raises(ValueError, match='anchor'):
        diagnostic.patch_instrumentation(before.replace('    })', 'different'))


class AdapterFixture:
    mode = 'full'

    def plan_operation(self, name, index, namespace):
        from systems.otel_demo.experiment_v4 import Adapter
        return Adapter.plan_operation(self, name, index, namespace)

    def operation(self, name, index, namespace):
        from systems.otel_demo import experiment_v4
        plan = self.plan_operation(name, index, namespace)
        completed = []
        for step in plan['http_steps']:
            response = experiment_v4._v4_request(step['method'], 'http://fixture'+step['path'],
                headers={'x-experiment-request-id':step['request_id']})
            completed.append(response.status_code)
            if response.status_code != 200: break
        return {'actual_statuses':completed}


def test_exact_approved_counts_unique_ids_and_prespecified_contexts(tmp_path, monkeypatch):
    from systems.otel_demo import experiment_v4
    sent = []
    def transport(method, url, **kwargs):
        sent.append(deepcopy(kwargs['headers']))
        return SimpleNamespace(status_code=200, request=SimpleNamespace(headers=kwargs['headers']))
    monkeypatch.setattr(experiment_v4, '_v4_request', transport)
    for arm in diagnostic.ARMS:
        path = tmp_path / arm
        path.mkdir()
        summary = diagnostic.issue_operations(AdapterFixture(), arm, path)
        assert summary['logical_operations'] == 9
        assert summary['planned_HTTP_steps'] == summary['attempted_HTTP_steps'] == 18
    assert len(sent) == 54
    assert len({row['x-experiment-request-id'] for row in sent}) == 54
    assert sum('traceparent' not in row for row in sent) == 18
    assert sum(row.get('traceparent','').endswith('-00') for row in sent) == 18
    assert sum(row.get('traceparent','').endswith('-01') for row in sent) == 18
    assert experiment_v4._v4_request is transport


def test_adverse_outcomes_are_kept_without_retrying_suffixes(tmp_path, monkeypatch):
    from systems.otel_demo import experiment_v4
    calls = []
    def transport(method, url, **kwargs):
        calls.append(url)
        return SimpleNamespace(status_code=500,request=SimpleNamespace(headers=kwargs['headers']))
    monkeypatch.setattr(experiment_v4, '_v4_request', transport)
    summary = diagnostic.issue_operations(AdapterFixture(), 'none', tmp_path)
    assert summary['attempted_HTTP_steps'] == 9
    assert summary['planned_HTTP_steps'] == 18
    assert len(calls) == 9
    assert all(row['actual']['actual_statuses'] == [500] for row in diagnostic.read(tmp_path/'operations.json'))


def test_unexpected_failure_retains_all_intentions_and_restores_driver(tmp_path, monkeypatch):
    from systems.otel_demo import experiment_v4
    def transport(*args, **kwargs): raise RuntimeError('actual fixture transport failure')
    monkeypatch.setattr(experiment_v4, '_v4_request', transport)
    with pytest.raises(RuntimeError): diagnostic.issue_operations(AdapterFixture(), 'none', tmp_path)
    rows = diagnostic.read(tmp_path/'operations.json')
    assert len(rows)==9 and rows[0]['status']=='technical_failure'
    assert all(row['status']=='not_attempted' for row in rows[1:])
    assert experiment_v4._v4_request is transport


def sdk_rows():
    install={'schema':'context-witness-v6','instanceId':'one','pid':1,'sequence':1,
             'kind':'observer-installed','observerSha256':'a'*64,'httpInstrumentation':{'version':'0.221.0'}}
    hook={'schema':'context-witness-v6','instanceId':'one','pid':1,'sequence':2,
          'kind':'http-request-hook','requestType':'IncomingMessage','headers':[['x-experiment-request-id','opaque']],
          'passedSpan':{'spanContext':{'traceId':'1'*32,'spanId':'2'*16,'traceFlags':0},'isRecording':False},
          'activeSpan':{'spanContext':{'traceId':'3'*32,'spanId':'4'*16,'traceFlags':1},'isRecording':True}}
    return [install,hook]


def sdk_result(tmp_path, rows):
    path=tmp_path/'sdk.jsonl'
    path.write_text(''.join(json.dumps(row)+'\n' for row in rows),encoding='utf8')
    return diagnostic.sdk_summary(path,[{'condition':'unsampled00','plan':{'http_steps':[{'request_id':'opaque'}]}}],'a'*64)


def test_sdk_nonrecording_context_and_active_span_are_distinct(tmp_path):
    result=sdk_result(tmp_path,sdk_rows())
    row=result['HTTP_steps'][0]
    assert row['verdict']=='OBSERVED' and row['passedSpan']['isRecording'] is False
    assert row['passedSpan']['spanContext']['traceFlags']==0
    assert row['passedSpan']['spanContext']!=row['activeSpan']['spanContext']
    assert result['SDK_span_equals_active_span_assumed'] is False


@pytest.mark.parametrize('mutation',['missing-install','wrong-source','wrong-version','gap','duplicate','invalid-context'])
def test_missing_or_unqualified_sdk_witness_is_unknown(tmp_path,mutation):
    rows=sdk_rows()
    if mutation=='missing-install': rows=rows[1:]
    elif mutation=='wrong-source': rows[0]['observerSha256']='b'*64
    elif mutation=='wrong-version': rows[0]['httpInstrumentation']['version']='0.222.0'
    elif mutation=='gap': rows[1]['sequence']=3
    elif mutation=='duplicate': rows.append({**rows[1],'sequence':3})
    elif mutation=='invalid-context': rows[1]['passedSpan']['spanContext']['traceId']='0'*32
    assert sdk_result(tmp_path,rows)['HTTP_steps'][0]['verdict']=='UNKNOWN'


def frame(kind,body=b'',flags=0,stream=0):
    return len(body).to_bytes(3,'big')+bytes([kind,flags])+stream.to_bytes(4,'big')+body


def packets(*,client_settings=b'',server_settings=b''):
    hpack=pytest.importorskip('hpack')
    encoder=hpack.Encoder()
    headers=[(':method','POST'),(':path','/Service/Call'),('traceparent','00-'+'1'*32+'-'+'2'*16+'-00'),
             ('x-experiment-request-id','opaque')]
    wire=diagnostic.MAGIC+frame(4,client_settings)+frame(1,encoder.encode(headers),4,1)
    # Second block uses the actual encoder's dynamic table.
    wire+=frame(1,encoder.encode(headers),4,3)
    def row(src,dst,sport,dport,seq,syn,payload=b''):
        return dict(src=src,dst=dst,sport=str(sport),dport=str(dport),seq=str(seq),syn=str(syn),payload=payload.hex())
    return [row('a','b',1000,3550,100,1),row('a','b',1000,3550,101,0,wire),
            row('b','a',3550,1000,300,1),row('b','a',3550,1000,301,0,frame(4,server_settings))]


def client_result(rows,drops=True):
    return next(row for row in diagnostic.decode_packets(rows,drops) if row['flow'][:2]==['a','1000'])


def test_complete_bidirectional_prefix_decodes_literal_hpack_and_dynamic_references():
    result=client_result(packets())
    assert result['verdict']=='OBSERVED' and len(result['headers'])==2
    decoded=[{base64.b64decode(v['name_b64']):base64.b64decode(v['value_b64'])
              for v in row['fields']} for row in result['headers']]
    assert decoded[0]==decoded[1]
    assert decoded[0][b'traceparent'].endswith(b'-00')


@pytest.mark.parametrize('mutation',['no-client-syn','no-server-syn','no-server-prefix','gap','conflict','tls','truncated','drops','peer-table'])
def test_incomplete_or_unsupported_wire_evidence_remains_unknown(mutation):
    rows=packets()
    drops=True
    if mutation=='no-client-syn': rows[0]['syn']='0'
    elif mutation=='no-server-syn': rows[2]['syn']='0'
    elif mutation=='no-server-prefix': rows[3]['payload']=''
    elif mutation=='gap': rows[1]['seq']='103'
    elif mutation=='conflict': rows.append({**rows[1],'payload':('X'+bytes.fromhex(rows[1]['payload'])[1:].decode('latin1')).encode('latin1').hex()})
    elif mutation=='tls': rows[1]['payload']='1603010000'
    elif mutation=='truncated': rows[1]['payload']=rows[1]['payload'][:-2]
    elif mutation=='drops': drops=False
    elif mutation=='peer-table': rows=packets(server_settings=b'\x00\x01'+(8192).to_bytes(4,'big'))
    assert client_result(rows,drops)['verdict']=='UNKNOWN'


def test_client_table_setting_does_not_describe_the_peer_encoder_limit():
    result=client_result(packets(client_settings=b'\x00\x01'+(8192).to_bytes(4,'big')))
    assert result['verdict']=='OBSERVED'


def test_identical_tcp_retransmission_is_not_a_missing_prefix():
    rows=packets()
    rows.append(deepcopy(rows[1]))
    assert client_result(rows)['verdict']=='OBSERVED'


def test_diagnostic_obi_changes_only_pinned_propagation_field(tmp_path):
    import yaml
    from ebpf_discovery.collectors_v5 import OBICollectorsV5
    original=OBICollectorsV5(SimpleNamespace(out=tmp_path/'original'))
    changed=diagnostic.DiagnosticOBI(SimpleNamespace(out=tmp_path/'diagnostic'),'disabled')
    first=original._write_config('a',4318)[0]
    second=changed._write_config('a',4318)[0]
    left,right=[yaml.safe_load(path.read_text(encoding='utf8')) for path in (first,second)]
    assert left['ebpf']['context_propagation']=='all'
    assert right['ebpf']['context_propagation']=='disabled'
    right['ebpf']['context_propagation']='all'
    assert left==right


def test_derivative_preserves_parent_images_sdk_options_and_source(tmp_path,monkeypatch):
    import yaml
    parent=tmp_path/'parent'
    assets=parent/'assets'
    source=assets/'source/src/frontend/utils/telemetry/Instrumentation.js'
    source.parent.mkdir(parents=True)
    original="const x = getNodeAutoInstrumentations({\n      preserved: { enabled: false },\n    })\n  ],\n"
    source.write_text(original,encoding='utf8')
    compose={'services':{'frontend':{'image':'frozen-image','environment':{'OTEL_TRACES_SAMPLER':'parentbased_always_on'},
        'volumes':['./source/src/frontend/utils/telemetry/Instrumentation.js:/app/Instrumentation.js:ro']}}}
    (assets/'node-a.yaml').write_text(yaml.safe_dump(compose),encoding='utf8')
    manifest={'system':'otel_demo','mode':'partial','images':{'frozen-image':{'archive':'unchanged'}},
              'nodes':{n:{'services':{'frontend':{'image_id':'frozen-image'}}} for n in ('a','b')},
              'assets':diagnostic._tree(assets)}
    diagnostic.write_json(parent/'blueprint.json',manifest)
    monkeypatch.setattr(diagnostic,'capacity',lambda *args:None)
    derivative=tmp_path/'derivative'
    diagnostic.derive(parent,derivative,'partial')
    result=diagnostic.read(derivative/'blueprint.json')
    actual=yaml.safe_load((derivative/'assets/node-a.yaml').read_text(encoding='utf8'))
    assert result['images']==manifest['images'] and result['nodes']==manifest['nodes']
    assert source.read_text(encoding='utf8')==original
    assert actual['services']['frontend']['environment']['OTEL_TRACES_SAMPLER']=='parentbased_always_on'
    assert 'preserved: { enabled: false }' in (derivative/'assets/source/src/frontend/utils/telemetry/Instrumentation.js').read_text()
    assert result['diagnostic_derivative']['observer_sha256']==diagnostic.sha(diagnostic.checkout()/'scripts/context-witness-v6.cjs')


def test_diagnostic_parent_needs_separate_execution_approval_not_main_or_replay(tmp_path,monkeypatch):
    root=tmp_path/'repo'
    path=root/'docs/parent.json'
    path.parent.mkdir(parents=True)
    value={'schema':diagnostic.SCHEMA,'system':'otel_demo','mode':'full','diagnostic_execution_GO':False,
           'root_diagnostic_execution_GO':False,'independent_diagnostic_execution_GO':False,
           'original_main_execution_GO':True,'root_replay_GO':True,'independent_replay_GO':True}
    diagnostic.write_json(path,value)
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    monkeypatch.setattr(diagnostic,'checkout',lambda:root)
    monkeypatch.setattr(diagnostic.subprocess,'run',lambda *args,**kwargs:None)
    monkeypatch.setattr(diagnostic,'api',lambda *args:pytest.fail('no API read before approval'))
    with pytest.raises(ValueError,match='execution GO'):
        diagnostic.approved_parent(path,diagnostic.sha(path),'full')
