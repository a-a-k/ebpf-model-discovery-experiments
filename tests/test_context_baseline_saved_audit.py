import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location('context_baseline_saved_audit',
    Path(__file__).parents[1] / 'scripts/audit-entry-route-binding.py')
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


def test_exact_training_restore_rejects_other_workspace_and_live_destination(tmp_path):
    cell = {'original_root': str(tmp_path / 'work/campaign')}
    assert AUDIT.context_training_root(cell, tmp_path) == tmp_path / 'work/campaign'
    with pytest.raises(ValueError, match='not this workspace'):
        AUDIT.context_training_root({'original_root': str(tmp_path / 'other')}, tmp_path)
    target = tmp_path / 'work/campaign'
    target.mkdir(parents=True)
    (target / 'observation-index.sqlite').write_bytes(b'live target database')
    with pytest.raises(ValueError, match='not empty'):
        AUDIT.context_training_root(cell, tmp_path)


def inputs(tmp_path):
    exports = []
    for i, source in enumerate(('ebpf', 'native', 'ebpf')):
        path = tmp_path / f'{i}.pb'
        path.write_bytes(f'original wire {i}'.encode())
        exports.append({'source': source, 'path': str(path), 'content_type': 'application/x-protobuf',
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return exports, AUDIT.context_input_sequence({'exports': exports})


def accepted(tmp_path, expected, *, joint):
    runtime = tmp_path / 'toolchain/joint/observed-runtime'
    runtime.mkdir(parents=True)
    rows = [{'export_index': i, 'http_status': 200, 'endpoint': '/v1/traces'
             if joint or wire['source'] == 'native' else '/sources/ebpf/v1/traces',
             'content_bytes': wire['bytes'], 'content_sha256': wire['sha256'],
             **({'original_source': wire['source']} if joint else {})}
            for i, wire in enumerate(expected)]
    return runtime, rows


def write_sequence(runtime, rows):
    body = b''.join(json.dumps(row).encode() + b'\n' for row in rows)
    path = runtime / 'accepted-request-sequence.jsonl'
    path.write_bytes(body)
    (runtime / 'replay-command.json').write_text(json.dumps({'status': 'complete', 'returncode': 0,
        'accepted_request_sequence': {'path': str(path), 'bytes': len(body), 'requests': len(rows),
                                      'sha256': hashlib.sha256(body).hexdigest()},
        # Deliberately incomplete inline list: only the complete sidecar is authoritative.
        'accepted_ingest_requests': rows[:1]}))


@pytest.mark.parametrize('joint', [False, True])
def test_identical_wire_order_and_original_roles_bound_to_complete_sequence(tmp_path, joint):
    _, expected = inputs(tmp_path)
    runtime, rows = accepted(tmp_path, expected, joint=joint)
    write_sequence(runtime, rows)
    proof = AUDIT.context_accepted_sequence(tmp_path, runtime.relative_to(tmp_path), expected, joint=joint)
    assert proof['requests'] == 3 and proof['same_original_wire_order_and_roles']


@pytest.mark.parametrize('tamper', ['wire', 'order', 'role', 'endpoint', 'truncated'])
def test_joint_sequence_rejects_same_count_rewritten_wire_or_roles(tmp_path, tamper):
    _, expected = inputs(tmp_path)
    runtime, rows = accepted(tmp_path, expected, joint=True)
    if tamper == 'wire':
        rows[1]['content_sha256'] = 'f' * 64
    elif tamper == 'order':
        rows[0], rows[1] = rows[1], rows[0]
    elif tamper == 'role':
        rows[1]['original_source'] = 'ebpf'
    elif tamper == 'endpoint':
        rows[0]['endpoint'] = '/sources/ebpf/v1/traces'
    else:
        rows.pop()
    write_sequence(runtime, rows)
    with pytest.raises(ValueError, match='differs|changed'):
        AUDIT.context_accepted_sequence(tmp_path, runtime.relative_to(tmp_path), expected, joint=True)


def test_input_verification_fails_before_diagnostic_tool_on_tampered_original_body(tmp_path):
    exports, _ = inputs(tmp_path)
    Path(exports[1]['path']).write_bytes(b'rewritten')
    with pytest.raises(ValueError, match='input bytes'):
        AUDIT.context_input_sequence({'exports': exports})
