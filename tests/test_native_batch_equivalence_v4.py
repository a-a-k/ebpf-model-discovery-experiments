import copy
import io
import json

import pytest

from ebpf_discovery import native_batch_equivalence_v4 as module


def test_ordered_full_typed_resources_ignore_only_envelope_boundaries():
    first = {'resource': {'attributes': [{'key': 'n', 'value': {'intValue': '9007199254740993'}}]},
             'scopeSpans': [{'spans': [{'traceId': 'a', 'spanId': 'b',
                'events': [{'timeUnixNano': '123', 'name': 'event'}], 'links': [{'traceId': 'c'}]}]}]}
    second = copy.deepcopy(first)
    second['scopeSpans'][0]['spans'][0]['traceId'] = 'd'
    def fingerprint(groups):
        result = module.Resources()
        for group in groups:
            result.add(io.BytesIO(json.dumps({'resourceSpans': group}).encode()))
        return result.result()
    old = fingerprint([[first], [second], [first]])
    new = fingerprint([[first, second, first]])
    assert old['exports'] == 3 and new['exports'] == 1
    assert {k:v for k,v in old.items() if k != 'exports'} == {k:v for k,v in new.items() if k != 'exports'}
    assert old['ordered_resource_spans_sha256'] != fingerprint([[first, first, second]])['ordered_resource_spans_sha256']
    assert old['ordered_resource_spans_sha256'] != fingerprint([[first, second]])['ordered_resource_spans_sha256']


def fixture(port, clock, directory):
    uri = f'bering://serve?listen=127.0.0.1%3A{port}'
    capture = f'{directory}/obi-capture/{clock:020d}-00000001-'+'a'*64+'.pb'
    application_attributes = {'source_ref': 'bering://serve?listen=127.0.0.1%3A7777',
                              'snapshot_id': 'business-id', 'timestamp': '123'}
    evidence = {'schema_version': '1.0.0', 'instances': [{'id': 'instance',
        'attributes': application_attributes, 'sources': [{'ref': capture}, {'ref': uri}]}],
        'warnings': ['unknown-parent']}
    model = {'metadata': {'source_ref': uri, 'discovered_at': str(clock), 'confidence': .9},
             'services': [{'id': 'service', 'replicas': 2}], 'edges': [], 'endpoints': []}
    snapshot = {'model': copy.deepcopy(model),
        'metadata': {'source_ref': uri, 'emitted_at': str(clock), 'confidence': .9},
        'sources': [{'type': 'ebpf', 'ref': capture, 'observations': 1}],
        'ingest': {'spans': 1, 'dropped_spans': 0}, 'topology_version': str(clock),
        'window_start': str(clock), 'window_end': str(clock), 'snapshot_id': str(clock),
        'discovery': {'services': [{'id': 'service', 'first_seen': 'observed-123',
            'support': {'observations': 2},
            'provenance': [{'type': 'traces', 'ref': uri}, {'type': 'overlay', 'ref': directory+'/overlay.json'}],
            'metadata': {'attributes': {module.EVIDENCE_KEY: json.dumps(evidence), **application_attributes}}}],
            'edges': [], 'endpoints': [], 'overlays': [{'ref': directory+'/overlay.json', 'name': 'operation'}]}}
    quality = {'generated_at': str(clock), 'artifact': {'path': directory+'/model.json',
        'snapshot_id': str(clock), 'window_start': str(clock), 'window_end': str(clock),
        'topology_version': str(clock), 'schema': 'schema-kept'},
        'observation_evidence': [{'entity_id': 'service', 'evidence': evidence}], 'warnings': ['unknown-parent']}
    return model, snapshot, quality


def project(values, directory):
    return module.semantic_projection(*values, ['a'*64], directory+'/overlay.json', 'b'*64)


def test_projection_only_normalizes_explicit_runtime_paths():
    old, new = fixture(5000, 100, '/old'), fixture(6000, 200, '/new')
    left, right = project(old, '/old'), project(new, '/new')
    assert left == right
    attributes = left['snapshot']['discovery']['services'][0]['metadata']['attributes']
    assert attributes['source_ref'].endswith('7777')
    assert attributes['timestamp'] == '123'
    assert attributes[module.EVIDENCE_KEY]['instances'][0]['attributes']['snapshot_id'] == 'business-id'
    assert old[0]['metadata']['discovered_at'] == '100'  # Originals remain untouched.


@pytest.mark.parametrize('change', ['edge', 'support', 'observed_time', 'unknown', 'instance', 'duplicate', 'attribute'])
def test_projection_does_not_hide_semantic_differences(change):
    original = fixture(5000, 100, '/old')
    changed = copy.deepcopy(original)
    if change == 'edge':
        changed[0]['edges'].append({'from':'a', 'to':'b'})
        changed[1]['model'] = copy.deepcopy(changed[0])
    elif change == 'support':
        changed[1]['discovery']['services'][0]['support']['observations'] += 1
    elif change == 'observed_time':
        changed[1]['discovery']['services'][0]['first_seen'] = 'changed'
    elif change == 'unknown':
        changed[2]['warnings'] = []
    elif change == 'instance':
        changed[2]['observation_evidence'][0]['evidence']['instances'][0]['id'] = 'changed'
    elif change == 'duplicate':
        changed[1]['sources'].append(copy.deepcopy(changed[1]['sources'][0]))
    elif change == 'attribute':
        changed[2]['observation_evidence'][0]['evidence']['instances'][0]['attributes']['source_ref'] = 'changed'
    assert project(original, '/old') != project(changed, '/old')


def test_projection_rejects_unbound_capture_hash_or_ordinal():
    values = fixture(5000, 100, '/old')
    with pytest.raises(ValueError, match='ordinal/hash'):
        module.semantic_projection(*values, ['c'*64], '/old/overlay.json', 'b'*64)


@pytest.mark.parametrize('key', ['snapshot_id', 'topology_version', 'window_start', 'window_end'])
def test_projection_rejects_stale_quality_before_normalization(key):
    values = fixture(5000, 100, '/old')
    values[2]['artifact'][key] = 'stale'
    with pytest.raises(ValueError, match='quality/snapshot runtime identity'):
        project(values, '/old')


def test_real_data_compare_is_actions_only(tmp_path, monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    with pytest.raises(RuntimeError, match='GitHub Actions'):
        module.compare(tmp_path, tmp_path, tmp_path, {}, tmp_path)


def test_rehash_failure_keeps_primary_error_and_writes_status(tmp_path, monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    calls = []
    def manifest(_):
        calls.append(True)
        if len(calls) > 1:
            raise OSError('rehash unavailable')
        return {}
    def validate(*_):
        raise ValueError('primary checkpoint error')
    monkeypatch.setattr(module, 'file_manifest', manifest)
    monkeypatch.setattr(module, 'validate_checkpoint_manifest', validate)
    with pytest.raises(ValueError, match='primary checkpoint error'):
        module.compare(tmp_path/'original', tmp_path/'reference', tmp_path/'out', {}, tmp_path/'replacement')
    status = module.read(tmp_path/'out/status.json')
    assert 'primary checkpoint error' in status['error']
    assert 'rehash unavailable' in status['checkpoint_rehash_error']
    assert status['immutable_checkpoint_unchanged'] is False


def test_reference_stream_verifies_members_and_manifest_input_order(tmp_path):
    from ebpf_discovery.diagnostic_artifacts_v4 import package
    tree = tmp_path/'tree'
    def put(relative, value):
        path = tree/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')
        return path
    exports = []
    for ordinal in (1, 2):
        relative = module.NATIVE+f'/exports/native-{ordinal:06d}.json'
        path = put(relative, {'resourceSpans':[{'scopeSpans':[{'spans':[{'spanId':str(ordinal)}]}]}]})
        exports.append({'path':'/original/'+relative, 'sha256':module.digest(path)})
    put(module.NATIVE+'/observations.json', {'observations':2, 'exports':exports})
    put(module.EBPF+'/observations.json', {'observations':0, 'exports':[]})
    for name in ('model.json', 'model.snapshot.json', 'model.signal-quality.json', 'overlay.json',
                 'model-runtime/bering-resources.json'):
        put(module.BRANCH+'/'+name, {})
    put(module.BRANCH+'/model-runtime/replay-command.json', {'status':'complete', 'returncode':0,
        'publication_mode':'on_shutdown', 'ingest':{'dropped_spans':0, 'late_spans':0}})
    put('output/status.json', {'status':'diagnostic_complete', 'immutable_checkpoint_unchanged':True})
    put('output/toolchain-provenance.json', {'effective':{
        'pins':module.PROFILES[module.DSB_SHUTDOWN_PROFILE]['replacement_pins'], 'publication_mode':'on_shutdown'}})
    put('unselected/retained.json', {'evidence':'must still verify this file'})
    package(tree, tmp_path/'package')
    proof = module.inspect_reference(tmp_path/'package', tmp_path/'view', module.REFERENCE)
    assert proof['complete_archive_verified'] and proof['native']['observations'] == 2
    assert proof['native']['exports'] == 2
    assert not (tmp_path/'view'/module.NATIVE/'exports').exists()
    assert not (tmp_path/'view'/'unselected').exists()
    # A checksum-valid archive with a false export order still cannot be a
    # reference for the claimed ordered Bering input.
    put(module.NATIVE+'/observations.json', {'observations':2, 'exports':list(reversed(exports))})
    package(tree, tmp_path/'reordered')
    with pytest.raises(ValueError, match='fingerprint accounting'):
        module.inspect_reference(tmp_path/'reordered', tmp_path/'rejected', module.REFERENCE)
