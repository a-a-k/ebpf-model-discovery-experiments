from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml


spec = importlib.util.spec_from_file_location('semantic_metadata_audit',
    Path(__file__).parents[1] / 'scripts/audit-entry-route-binding.py')
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


def publication(root, name, port, second):
    folder = 'toolchain/' + name
    runtime = folder + '/observed-runtime'
    path = root / runtime
    path.mkdir(parents=True)
    model = {'metadata': {'source_ref': f'bering://serve?listen=127.0.0.1%3A{port}',
                          'discovered_at': f'2026-10-30T22:00:0{second}Z'},
             'services': [{'id': 'gateway', 'replicas': 1}], 'edges': [], 'endpoints': []}
    (root / folder / 'observed.json').write_text(json.dumps(model))
    (path / 'serve.yaml').write_text(yaml.safe_dump({'server': {'listen_address': f'127.0.0.1:{port}'}}))
    clock = 1793397600 + second
    sequence = [{'http_status': 200, 'endpoint': '/v1/traces', 'export_index': 0,
                 'content_bytes': 9, 'content_sha256': 'a' * 64, 'storage_form': 'ordinary_export'}]
    body = (json.dumps(sequence[0]) + '\n').encode()
    (path / 'accepted-request-sequence.jsonl').write_bytes(body)
    command = {'status': 'complete', 'returncode': 0,
               'argv': ['bering', 'serve', '--config', '/original/' + runtime + '/serve.yaml'],
               'started_ns': clock * 10**9, 'ended_ns': (clock + 1) * 10**9,
               'accepted_ingest_requests': sequence,
               'accepted_request_sequence': {'path': '/original/' + runtime + '/accepted-request-sequence.jsonl',
                                             'requests': 1, 'bytes': len(body),
                                             'sha256': hashlib.sha256(body).hexdigest()}}
    (path / 'replay-command.json').write_text(json.dumps(command))
    return model, AUDIT.model_publication(root, folder + '/observed.json', runtime), path


def test_only_source_proven_clock_and_listener_changes_are_excluded(tmp_path):
    first, first_proof, _ = publication(tmp_path, 'first', 1234, 0)
    old, second_proof, _ = publication(tmp_path, 'second', 5678, 2)
    replacement = deepcopy(first)
    result = AUDIT.compare_metadata_models(first, old, replacement, first_proof, second_proof)
    assert result['all_other_model_fields_exact']
    assert {r['path'] for r in result['publication_deltas']} == {'metadata.discovered_at', 'metadata.source_ref'}
    assert result['publication_deltas'][1]['original_second_publication'] == old['metadata']['source_ref']
    replacement['services'][0]['replicas'] = 2
    assert not AUDIT.compare_metadata_models(first, old, replacement, first_proof, second_proof)['all_other_model_fields_exact']


@pytest.mark.parametrize('tamper', ['different-wire', 'borrowed-proof', 'changed-first-provenance'])
def test_paired_comparison_rejects_unrelated_inputs_and_provenance(tmp_path, tamper):
    first, first_proof, _ = publication(tmp_path, 'first', 1234, 0)
    old, second_proof, _ = publication(tmp_path, 'second', 5678, 2)
    replacement = deepcopy(first)
    if tamper == 'different-wire':
        second_proof['accepted_sequence'][0] = ('/v1/traces', 10, 'b' * 64)
    elif tamper == 'borrowed-proof':
        second_proof['source_ref'] = first_proof['source_ref']
    else:
        replacement['metadata']['source_ref'] = old['metadata']['source_ref']
    with pytest.raises(ValueError):
        AUDIT.compare_metadata_models(first, old, replacement, first_proof, second_proof)


@pytest.mark.parametrize('tamper', ['listener', 'config-path', 'clock'])
def test_publication_exception_requires_exact_original_config_and_time(tmp_path, tamper):
    _, _, path = publication(tmp_path, 'first', 1234, 0)
    if tamper == 'listener':
        (path / 'serve.yaml').write_text(yaml.safe_dump({'server': {'listen_address': '127.0.0.1:9999'}}))
    else:
        command = json.loads((path / 'replay-command.json').read_text())
        if tamper == 'config-path':
            command['argv'][3] = '/original/toolchain/unrelated/serve.yaml'
        else:
            command['started_ns'] += 10 * 10**9
            command['ended_ns'] += 10 * 10**9
        (path / 'replay-command.json').write_text(json.dumps(command))
    with pytest.raises(ValueError):
        AUDIT.model_publication(tmp_path, 'toolchain/first/observed.json', 'toolchain/first/observed-runtime')


@pytest.mark.parametrize('forms', [('stream_archive_slice',), ('ordinary_export', 'stream_archive_slice')])
def test_publication_uses_the_complete_frozen_sequence_including_streamed_requests(tmp_path, forms):
    _, _, path = publication(tmp_path, 'first', 1234, 0)
    command = json.loads((path / 'replay-command.json').read_text())
    rows = [{'http_status': 200, 'endpoint': '/v1/traces', 'export_index': index,
             'content_bytes': 10 + index, 'content_sha256': str(index) * 64, 'storage_form': form}
            for index, form in enumerate(forms)]
    body = b''.join((json.dumps(row) + '\n').encode() for row in rows)
    (path / 'accepted-request-sequence.jsonl').write_bytes(body)
    command['accepted_ingest_requests'] = [row for row in rows if row['storage_form'] == 'ordinary_export']
    command['accepted_request_sequence'].update(requests=len(rows), bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    (path / 'replay-command.json').write_text(json.dumps(command))
    result = AUDIT.model_publication(tmp_path, 'toolchain/first/observed.json', 'toolchain/first/observed-runtime')
    assert result['sequence_requests'] == len(rows)
    assert result['accepted_sequence'] == [(row['endpoint'], row['content_bytes'], row['content_sha256']) for row in rows]


@pytest.mark.parametrize('tamper', ['bytes', 'count', 'order', 'locator', 'status'])
def test_sequence_hash_count_order_and_success_are_all_bound(tmp_path, tamper):
    _, _, path = publication(tmp_path, 'first', 1234, 0)
    command = json.loads((path / 'replay-command.json').read_text())
    sequence = path / 'accepted-request-sequence.jsonl'
    if tamper == 'bytes':
        sequence.write_bytes(sequence.read_bytes().replace(b'aaaaaaaa', b'bbbbbbbb'))
    elif tamper == 'count':
        command['accepted_request_sequence']['requests'] = 2
    elif tamper == 'order':
        row = json.loads(sequence.read_text())
        row['export_index'] = 1
        body = (json.dumps(row) + '\n').encode()
        sequence.write_bytes(body)
        command['accepted_request_sequence'].update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    elif tamper == 'locator':
        command['accepted_request_sequence']['path'] = '/original/toolchain/unrelated/accepted-request-sequence.jsonl'
    else:
        command.update(status='technical_failure', returncode=1)
    (path / 'replay-command.json').write_text(json.dumps(command))
    with pytest.raises(ValueError):
        AUDIT.model_publication(tmp_path, 'toolchain/first/observed.json', 'toolchain/first/observed-runtime')
