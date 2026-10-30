import hashlib
import json

import pytest
from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

from ebpf_discovery.observations import attributes, otlp
from ebpf_discovery.raw_v4 import _json_value
from ebpf_discovery.store_v3 import attribute_conflicts, normalized_file


def test_proto_default_key_preserves_value_without_inventing_method():
    request = ExportTraceServiceRequest()
    resource = request.resource_spans.add()
    resource.resource.attributes.add(key='service.name').value.string_value = 'observed'
    span = resource.scope_spans.add().spans.add()
    span.trace_id = bytes.fromhex('12' * 16)
    span.span_id = bytes.fromhex('34' * 8)
    span.attributes.add().value.string_value = 'POST'
    span.attributes.add(key='url.full').value.string_value = 'http://observed/path'
    wire = request.SerializeToString()
    digest = hashlib.sha256(wire).hexdigest()
    rows = list(otlp(MessageToDict(request), 'ebpf', 'a', 'base64'))
    assert len(rows) == 1
    assert rows[0]['attributes'] == {'': 'POST', 'url.full': 'http://observed/path'}
    assert 'http.request.method' not in rows[0]['attributes']
    assert (rows[0]['trace_id'], rows[0]['span_id']) == ('12' * 16, '34' * 8)
    assert hashlib.sha256(request.SerializeToString()).hexdigest() == digest


def test_omitted_and_explicit_empty_key_conflicts_retain_both_values(tmp_path):
    values = [{'value': {'stringValue': 'one'}},
              {'key': '', 'value': {'stringValue': 'two'}}]
    conflicts = attribute_conflicts(values)
    assert conflicts == [{'key': '', 'raw_values': [{'stringValue': 'one'}, {'stringValue': 'two'}]}]
    path = tmp_path / 'a.jsonl'
    path.write_text(json.dumps({'resourceSpans': [{'scopeSpans': [{'spans': [
        {'attributes': values}]}]}]}) + '\n')
    row = next(normalized_file(path, 'ebpf', 0, path.stat().st_size))
    assert row['attribute_conflicts'] == conflicts
    assert '' not in row['attributes']


def test_nested_otlp_kvlist_uses_the_same_default():
    nested = {'kvlistValue': {'values': [{'value': {'stringValue': 'unnamed'}}]}}
    assert attributes([{'key': 'outer', 'value': nested}]) == {'outer': {'': 'unnamed'}}
    assert _json_value(nested) == {'': 'unnamed'}


def test_missing_jaeger_tag_key_remains_an_error():
    with pytest.raises(KeyError):
        attribute_conflicts([{'value': 'unnamed'}], jaeger_tags=True)


def test_named_otlp_attributes_keep_their_original_semantics():
    values = [{'key': 'a', 'value': {'stringValue': 'one'}},
              {'key': 'b', 'value': {'intValue': '2'}}]
    assert attributes(values) == {'a': 'one', 'b': '2'}
    assert attribute_conflicts(values) == []
