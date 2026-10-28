import json
import http.client
from pathlib import Path
import sqlite3
import threading

import pytest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

from ebpf_discovery.raw_v4 import export_selection
from ebpf_discovery.receiver import create_server
from ebpf_discovery.replay_qualification_v4 import (
    PINS, digest, file_manifest, relocate_index, replay, verified_binaries,
)
from ebpf_discovery.store_v3 import ObservationStore


def _fake_binaries(original: Path, old_root: Path):
    target = original/'toolchain-build'
    (target/'bin').mkdir(parents=True)
    rows = []
    for name, pin in PINS.items():
        binary = target/'bin'/name.lower()
        binary.write_bytes((name+'-synthetic-binary').encode())
        rows.append({'name':name.lower(), 'commit':pin,
                     'binary':str(old_root/'toolchain-build'/'bin'/name.lower()),
                     'binary_sha256':digest(binary), 'binary_bytes':binary.stat().st_size})
    (target/'toolchain-build.json').write_text(json.dumps(
        {'schema_version':'toolchain-build-v4','binaries':rows}))
    return rows


def test_pinned_binary_copy_preserves_original_and_rejects_hash_mismatch(tmp_path):
    original, old = tmp_path/'original', tmp_path/'old-campaign'
    rows = _fake_binaries(original, old)
    before = file_manifest(original)
    bin_dir, inferred, proof = verified_binaries(original, tmp_path/'replay')
    assert inferred == old
    assert set(proof) == {name.lower() for name in PINS}
    assert all((bin_dir/row['name']).read_bytes() ==
               (original/'toolchain-build'/'bin'/row['name']).read_bytes() for row in rows)
    assert file_manifest(original) == before
    rows[0]['binary_sha256'] = '0'*64
    (original/'toolchain-build'/'toolchain-build.json').write_text(json.dumps(
        {'schema_version':'toolchain-build-v4','binaries':rows}))
    with pytest.raises(ValueError, match='digest'):
        verified_binaries(original, tmp_path/'other-replay')


def test_index_copy_relocates_only_file_paths_and_keeps_source_payload(tmp_path):
    original, replay_dir, old = tmp_path/'original', tmp_path/'replay', tmp_path/'old-campaign'
    (original/'observations').mkdir(parents=True)
    replay_dir.mkdir()
    raw = original/'observations'/'a.jsonl'
    raw.write_text('{"synthetic":true}\n')
    store = ObservationStore(original/'observation-index.sqlite')
    data = json.dumps({'source':'ebpf','trace_id':'a'*32,'span_id':'b'*16,
                       'raw_file':str(old/'observations'/'a.jsonl')})
    store.db.execute('INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        ('digest','ebpf','a','a'*32,'b'*16,'','service',None,'req',
         'server',1,2,None,None,None,None,0,data))
    store.db.execute('INSERT INTO files VALUES (?,?)',
                     (str(old/'observations'/'a.jsonl'), raw.stat().st_size))
    store.db.commit()
    store.close()
    before = file_manifest(original)
    proof = relocate_index(original, replay_dir, old)
    copied = sqlite3.connect(replay_dir/'observation-index.sqlite')
    try:
        assert copied.execute('SELECT path FROM files').fetchone()[0] == str(raw.resolve())
        assert copied.execute('SELECT data FROM spans').fetchone()[0] == data
    finally:
        copied.close()
    assert proof['spans_rows_sha256_before'] == proof['spans_rows_sha256_after']
    assert proof['links_rows_sha256_before'] == proof['links_rows_sha256_after']
    assert file_manifest(original) == before


def test_index_rejects_indexed_path_outside_original_capture_root(tmp_path):
    original, replay_dir, old = tmp_path/'original', tmp_path/'replay', tmp_path/'old-campaign'
    original.mkdir()
    replay_dir.mkdir()
    store = ObservationStore(original/'observation-index.sqlite')
    store.db.execute('INSERT INTO files VALUES (?,?)',
                     (str(tmp_path/'foreign'/'a.jsonl'), 0))
    store.db.commit()
    store.close()
    with pytest.raises(ValueError, match='outside original capture root'):
        relocate_index(original, replay_dir, old)


def test_actual_receiver_wire_wrapper_exports_after_index_relocation(tmp_path):
    original, replay_dir, old = tmp_path/'original', tmp_path/'replay', tmp_path/'old-campaign'
    output = original/'observations'/'a.jsonl'
    output.parent.mkdir(parents=True)
    replay_dir.mkdir()
    trace, span_id = '00112233445566778899aabbccddeeff', '0102030405060708'
    request = ExportTraceServiceRequest()
    span = request.resource_spans.add().scope_spans.add().spans.add()
    span.trace_id, span.span_id = bytes.fromhex(trace), bytes.fromhex(span_id)
    span.name = 'GET /synthetic'
    wire = request.SerializeToString()
    server = create_server(0, output, 'ebpf:a', node='a', raw_capture=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
    try:
        connection.request('POST', '/v1/traces', body=wire,
                           headers={'Content-Type':'application/x-protobuf'})
        response = connection.getresponse()
        response.read()
        assert response.status == 200
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    wrapper = json.loads(output.read_text().splitlines()[0])
    assert not Path(wrapper['raw_ref']).is_absolute()
    assert (output.parent/wrapper['raw_ref']).read_bytes() == wire
    store = ObservationStore(original/'observation-index.sqlite')
    store.db.execute('INSERT INTO files VALUES (?,?)',
                     (str(old/'observations'/'a.jsonl'), output.stat().st_size))
    store.db.commit()
    store.close()
    before = file_manifest(original)
    relocate_index(original, replay_dir, old)
    copied = ObservationStore(replay_dir/'observation-index.sqlite')
    try:
        exported = export_selection(copied, {'ebpf': {(trace, span_id)}},
                                    replay_dir/'selected-inputs')
    finally:
        copied.close()
    assert exported['observations'] == 1
    body = Path(exported['exports'][0]['path']).read_bytes()
    decoded = ExportTraceServiceRequest()
    decoded.ParseFromString(body)
    assert decoded.resource_spans[0].scope_spans[0].spans[0].trace_id.hex() == trace
    assert file_manifest(original) == before


def test_replay_is_actions_only_and_never_treats_local_fixture_as_qualification(tmp_path, monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    with pytest.raises(RuntimeError, match='GitHub Actions'):
        replay(tmp_path/'original', tmp_path/'replay', 'deathstarbench', {})


def test_invalid_artifact_metadata_is_retained_as_technical_failure(tmp_path, monkeypatch):
    original = tmp_path/'original'
    original.mkdir()
    (original/'status.json').write_text('{"synthetic":true}')
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    with pytest.raises(ValueError, match='source artifact identity'):
        replay(original, tmp_path/'replay', 'deathstarbench', {'run_id':123})
    status = json.loads((tmp_path/'replay'/'status.json').read_text())
    assert status['status'] == 'capture_replay_technical_failure'
    assert status['original_files_unchanged'] is True


def test_workflow_has_no_guest_or_capture_step():
    workflow = (Path(__file__).resolve().parents[1]/'.github'/'workflows'/
                'replay-qualification-v4.yml').read_text()
    assert 'vms.sh start' not in workflow
    assert 'campaign_v4 --system' not in workflow
    assert 'capture-v3-resources.sh' not in workflow
    assert 'qualification-v4-{system}-full-6-{run_id}' in workflow
