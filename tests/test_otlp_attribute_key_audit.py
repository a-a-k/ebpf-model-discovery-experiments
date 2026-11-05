import hashlib
import importlib.util
import json
from pathlib import Path

from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest


spec = importlib.util.spec_from_file_location('otlp_attribute_key_audit',
    Path(__file__).parents[1] / 'scripts/audit-otlp-attribute-keys.py')
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


def test_wire_default_key_is_located_without_span_normalizer(tmp_path):
    request = ExportTraceServiceRequest()
    span = request.resource_spans.add().scope_spans.add().spans.add()
    span.attributes.add(key='known').value.string_value = 'kept'
    span.attributes.add().value.string_value = 'unnamed'
    wire = request.SerializeToString()
    body = tmp_path / 'observations/a.raw/one.pb'
    body.parent.mkdir(parents=True)
    body.write_bytes(wire)
    journal = tmp_path / 'observations/a.jsonl'
    journal.write_text(json.dumps({'payload': MessageToDict(request), 'raw_ref': 'a.raw/one.pb',
        'content_type': 'application/x-protobuf', 'raw_sha256': hashlib.sha256(wire).hexdigest()}) + '\n')
    facts = AUDIT.inspect(tmp_path)
    witness = facts['witnesses'][0]
    assert facts['streams'][0]['missing_key'] == 1
    assert witness['protobuf_key'] == witness['protobuf_key_default'] == ''
    assert witness['protobuf_nondefault_fields'] == ['value']
    assert witness['projection_equals_retained_entry'] is True
    assert witness['semantic_source'] == 'original protobuf wire'
    assert witness['scalar_wire_presence_claimed'] is False
    assert witness['surrounding_keys'] == ['known', '<missing>']
    assert witness['raw_projection_equals_retained_payload'] is True
    assert witness['record_byte_offset'] == 0
    assert witness['normalizer_context'] == 'direct_span_attributes'


def test_malformed_json_attribute_is_retained_as_an_interpretation_error(tmp_path):
    journal = tmp_path / 'observations/a.jsonl'
    journal.parent.mkdir()
    journal.write_text(json.dumps({'resourceSpans': [{'resource': {'attributes': [{'unexpected': 1}]}}]}) + '\n')
    witness = AUDIT.inspect(tmp_path)['witnesses'][0]
    assert witness['original_json_entry'] == {'unexpected': 1}
    assert witness['protobuf_interpretation_error'].startswith('ParseError:')
