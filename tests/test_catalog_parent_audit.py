from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy

import pytest
import yaml
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest


def helper():
    return runpy.run_path(str(Path(__file__).parents[1] / 'scripts/audit-dsb-capture.py'))


def request(service='product-catalog', sid=2, parent=1, trace='01'):
    pb = ExportTraceServiceRequest()
    resource = pb.resource_spans.add()
    resource.resource.attributes.add(key='service.name').value.string_value = service
    span = resource.scope_spans.add().spans.add(name='oteldemo.ProductCatalogService/GetProduct', kind=2)
    span.trace_id = bytes.fromhex(trace * 16)
    span.span_id = sid.to_bytes(8)
    span.parent_span_id = parent.to_bytes(8)
    span.attributes.add(key='rpc.method').value.string_value = 'oteldemo.ProductCatalogService/GetProduct'
    return pb.SerializeToString()


def rows(wire):
    result = {}
    for item in helper()['native_span_fields'](wire, 'application/x-protobuf'):
        digest = hashlib.sha256(json.dumps(item['fields'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        result[digest] = {'service': item['service'], 'fields': item['fields'], 'count': 1, 'witnesses': []}
    return result


def test_literal_catalog_summary_retains_conflicts_and_separates_sdk_domain_without_inventing_parent():
    functions = helper()
    local = rows(request())
    sdk = rows(request('frontend', sid=1, parent=0))
    other = rows(request('other', sid=1, parent=0, trace='02'))
    result = functions['catalog_summary']({**local, **other}, 'ebpf-otlp:4:ebpf:deployment', sdk)
    child = result['catalog_get_product_server_variants'][0]
    assert child['actual_same_domain_same_trace_parent_variants'] == []
    assert len(child['same_ids_in_native_frozen_input_other_domain']) == 1
    assert child['native_input_domain'] == ''
    changed = deepcopy(next(iter(sdk.values())))
    changed['fields']['span']['name'] = 'conflicting literal variant'
    parents = {**sdk, 'changed': changed}
    result = functions['catalog_summary']({**local, **parents}, 'ebpf-otlp:4:ebpf:deployment', {})
    child = result['catalog_get_product_server_variants'][0]
    assert len(child['actual_same_domain_same_trace_parent_variants']) == 2
    assert result['literal_same_identity_with_multiple_field_variants'] == 1


def test_invalid_zero_parent_and_conflicting_service_do_not_become_unique_identity():
    functions = helper()
    pb = ExportTraceServiceRequest()
    pb.ParseFromString(request(parent=0))
    pb.resource_spans[0].resource.attributes.add(key='service.name').value.string_value = 'other'
    variants = rows(pb.SerializeToString())
    item = next(iter(variants.values()))
    assert item['service'] is None
    child = functions['catalog_summary'](variants, 'domain', {})['catalog_get_product_server_variants'][0]
    assert child['service'] is None and not child['usable_parent_identity']
    assert child['actual_same_domain_same_trace_parent_variants'] == []


@pytest.mark.parametrize('changed', [None, 'sequence-bytes', 'sequence-order', 'ingest-count'])
def test_catalog_evidence_uses_complete_actual_sequence_and_literal_native_counterparts(tmp_path, changed):
    functions = helper()
    root = tmp_path / 'capture'
    def write(name, value):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) + '\n')
        return path
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    wire = request('frontend', sid=1, parent=0)
    native_path = root / 'toolchain/inputs/native/raw/native.pb'
    native_path.parent.mkdir(parents=True)
    native_path.write_bytes(wire)
    write('toolchain/inputs/native/raw/observations.json', {'observations': 1,
        'exports': [{'source': 'native', 'path': native_path.as_posix(), 'sha256': sha(native_path),
                     'content_type': 'application/x-protobuf'}]})
    runtime = root / 'toolchain/discovery/ebpf/raw/observed-runtime'
    runtime.mkdir(parents=True)
    sequence = runtime / 'accepted-request-sequence.jsonl'
    sequence.write_text(json.dumps({'http_status': 200, 'endpoint': '/sources/ebpf/v1/traces',
                                   'export_index': 0, 'content_sha256': 'a' * 64, 'content_bytes': 17}) + '\n')
    replay = {'status': 'complete', 'returncode': 0, 'source_domain': 'deployment',
              'source_profile': {'source_id': 'ebpf', 'input_type': 'ebpf-otlp'},
              'input_observations': 1, 'ingest': {'spans': 1, 'dropped_spans': 0, 'late_spans': 0},
              'accepted_request_sequence': {'path': sequence.as_posix(), 'sha256': sha(sequence),
                                             'bytes': sequence.stat().st_size, 'requests': 1}}
    write('toolchain/discovery/ebpf/raw/observed-runtime/replay-command.json', replay)
    config = runtime / 'serve.yaml'
    config.write_text(yaml.safe_dump({'sources': [{'id': 'ebpf', 'type': 'ebpf-otlp', 'domain': 'deployment'}]}))
    write('toolchain/static-inputs.json', {'tool_pins': {'Bering': '66ca3af1fe581839e525fb9cc5600a1edd6ca8fb'}})
    for leaf in ('observed.json', 'observed.bering-raw.json', 'observed.signal-quality.json', 'observed.supplied-aliases.json'):
        write('toolchain/discovery/ebpf/raw/' + leaf, {'unchanged': leaf})
    frozen = {p.relative_to(root).as_posix(): sha(p) for p in root.rglob('*') if p.is_file()}
    if changed == 'sequence-bytes':
        sequence.write_bytes(sequence.read_bytes().replace(b'aaaa', b'bbbb'))
    elif changed == 'sequence-order':
        entry = json.loads(sequence.read_text())
        entry['export_index'] = 1
        sequence.write_text(json.dumps(entry) + '\n')
        replay['accepted_request_sequence'].update(sha256=sha(sequence), bytes=sequence.stat().st_size)
        write('toolchain/discovery/ebpf/raw/observed-runtime/replay-command.json', replay)
        frozen.update({p.relative_to(root).as_posix(): sha(p) for p in (sequence, runtime / 'replay-command.json')})
    elif changed == 'ingest-count':
        replay['ingest']['spans'] = 2
        write('toolchain/discovery/ebpf/raw/observed-runtime/replay-command.json', replay)
        frozen['toolchain/discovery/ebpf/raw/observed-runtime/replay-command.json'] = sha(runtime / 'replay-command.json')
    literal = rows(request())
    if changed:
        with pytest.raises(ValueError):
            functions['catalog_parent_facts'](root, frozen, {'input': literal, 'original': literal}, [('a' * 64, 17)], lambda v: v)
    else:
        facts = functions['catalog_parent_facts'](root, frozen, {'input': literal, 'original': literal}, [('a' * 64, 17)], lambda v: v)
        assert facts['raw_input_all_literal_field_counts_equal']
        assert facts['raw_input_trace_span_parent_kind_name_counts_equal']
        assert facts['source_domain'] == 'ebpf-otlp:4:ebpf:deployment'
        assert facts['domain_derivation']['different_internal_domains_do_not_prove_independent_trace_universes']
        child = facts['catalog']['original']['catalog_get_product_server_variants'][0]
        assert len(child['same_ids_in_native_frozen_input_other_domain']) == 1
        assert child['actual_same_domain_same_trace_parent_variants'] == []
