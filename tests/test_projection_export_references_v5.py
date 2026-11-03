"""Exact export equivalence and rejection of stale/mutable projection references."""
import copy
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
import sqlite3

import pytest

from ebpf_discovery.raw_v4 import _DeepFlowRequestArchive, _filter_json
from ebpf_discovery.store_v5 import ProjectionResolver, _ExportProjectionReference

KEY=('a.jsonl','wire.bin',0,12,'a'*64)
VALUE={'service':'service-α','resolution':{'proof':1},'inventory_path':'inventory.json'}


def resolver(tmp_path,value=None):
    r=ProjectionResolver(tmp_path,tmp_path/'values.jsonl')
    r.add(KEY,copy.deepcopy(VALUE if value is None else value));r.finalize()
    return r


def test_streamed_reference_preserves_full_value_and_last_equal_json_representation(tmp_path):
    r=ProjectionResolver(tmp_path,tmp_path/'values.jsonl')
    first={**VALUE,'resolution':{'proof':1}}
    last={**VALUE,'resolution':{'proof':True}}
    r.add(KEY,first);r.add(KEY,last);r.finalize()
    try:
        actual=r.get_for_stream_export(KEY)
        assert isinstance(actual,_ExportProjectionReference)
        assert actual.get('service')==last['service']
        assert r.value_reference(actual)==r.value_reference(last)
        assert r.value_reference(actual)!=r.value_reference(first)
        line=json.loads((tmp_path/'values.jsonl').read_text())
        assert line['value']==last and line['value']['resolution']['proof'] is True
        assert line['sha256']==hashlib.sha256(r._encoded(last).encode()).hexdigest()
        with pytest.raises(FrozenInstanceError):actual.service='changed'
        assert r.get_for_stream_export(('missing',*KEY[1:])) is None
    finally:r.close()


@pytest.mark.parametrize('service',[True,1,1.5,None,[],{'nested':'value'}])
def test_non_text_service_keeps_original_full_python_json_representation(tmp_path,service):
    value={'service':service,'resolution':{'proof':'unchanged'}}
    r=resolver(tmp_path,value)
    try:
        actual=r.get_for_stream_export(KEY)
        assert type(actual) is dict and actual==value
        assert type(actual['service']) is type(service)
        assert r.value_reference(actual)==r.value_reference(value)
    finally:r.close()


@pytest.mark.parametrize('mutation',['foreign_resolver','wrong_sha','wrong_service','changed_proof','changed_file','changed_index','closed'])
def test_reference_rejects_foreign_or_changed_authority(tmp_path,mutation):
    r=resolver(tmp_path/'a');other=None
    try:
        reference=r.get_for_stream_export(KEY)
        if mutation=='foreign_resolver':
            other=resolver(tmp_path/'b');reference=other.get_for_stream_export(KEY)
        if mutation=='wrong_sha':reference=replace(reference,value_sha256='f'*64)
        if mutation=='wrong_service':reference=replace(reference,service='foreign')
        if mutation=='changed_proof':r.value_store_proof['sha256']='0'*64
        if mutation=='changed_file':r.value_store.write_bytes(r.value_store.read_bytes()+b'\n')
        if mutation=='changed_index':
            with sqlite3.connect(r.path) as external:
                external.execute("UPDATE values_by_sha SET encoded='{}'")
            external.close()
        if mutation=='closed':r.close()
        with pytest.raises(ValueError):r.value_reference(reference)
    finally:
        r.close()
        if other:other.close()


def test_fast_reference_prevents_writes_to_finalized_lookup_index(tmp_path):
    r=resolver(tmp_path)
    try:
        r.get_for_stream_export(KEY)
        with pytest.raises(sqlite3.OperationalError):r.db.execute("UPDATE values_by_sha SET encoded='{}'")
    finally:r.close()


def test_old_and_new_filters_emit_identical_requests_indices_and_value_references(tmp_path):
    r=resolver(tmp_path/'resolver')
    locator=dict(zip(('source_file','retained_file','offset','length','sha256'),KEY))
    attribute={'key':'_runtime_identity.locator','value':{'kvlistValue':{'values':[
        {'key':k,'value':{'intValue':v} if type(v)is int else {'stringValue':v}}
        for k,v in locator.items()]}}}
    payload={'resourceSpans':[{'resource':{'attributes':[]},'scopeSpans':[{'scope':{'name':'synthetic'},'spans':[
        {'traceId':'1'*32,'spanId':'2'*16,'name':'request','attributes':[attribute]}]}]}]}
    results=[]
    try:
        for label,fast in [('old',False),('new',True)]:
            transformations=[]
            filtered,count,_,supplied=_filter_json(payload,None,'hex','same-network','ebpf',{},r,transformations,
                projection_references=fast)
            body=(json.dumps(filtered,separators=(',',':'))+'\n').encode()
            folder=tmp_path/label;folder.mkdir()
            archive=_DeepFlowRequestArchive(folder,'ebpf',r)
            archive.append(body,{'observations':count,'supplied_server_roles':supplied},transformations)
            summary=archive.finish()
            results.append((body,(folder/'ebpf-request-index.jsonl').read_bytes(),
                (folder/'ebpf-requests-000001.bin').read_bytes(),summary['runtime_identity_values']['sha256']))
        assert results[0]==results[1]
        assert json.loads(results[1][1])['runtime_identity_transformation_refs']==[r.value_reference(r.get(KEY))]
    finally:r.close()



def test_existing_other_value_hash_cannot_replace_reference_for_this_locator(tmp_path):
    r=ProjectionResolver(tmp_path,tmp_path/'values.jsonl')
    other_key=('b.jsonl',*KEY[1:])
    r.add(KEY,VALUE);r.add(other_key,{**VALUE,'resolution':{'proof':'different-authoritative-value'}});r.finalize()
    try:
        one=r.get_for_stream_export(KEY);two=r.get_for_stream_export(other_key)
        assert one.service==two.service and one.value_sha256!=two.value_sha256
        with pytest.raises(ValueError):r.value_reference(replace(one,value_sha256=two.value_sha256))
    finally:r.close()
