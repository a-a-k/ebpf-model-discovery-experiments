import hashlib
import gzip
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from ebpf_discovery.bering_v4 import child_go_environment, replay


def harness(tmp_path, *, ingest_count=2, dropped=0):
    inputs = []
    for source in ('ebpf', 'native'):
        path = tmp_path / (source + '.pb')
        path.write_bytes(gzip.compress(source.encode()) if source == 'ebpf' else source.encode())
        inputs.append({'source': source, 'path': str(path), 'content_type': 'application/x-protobuf',
                       'content_encoding': 'gzip' if source == 'ebpf' else '',
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'observations': 1})
    graph = {'services': [{'id': 'observed-only'}], 'edges': [], 'endpoints': []}

    class Process:
        kwargs = None

        def __init__(self, argv, **kwargs):
            Process.kwargs = kwargs
            assert Path(argv[1]).name == 'child_resources_v4.py'
            assert argv[2] == '--report'
            assert Path(argv[3]).name == 'bering-resources.json'
            assert argv[4] == '--'
            assert argv[-3:] == ['serve', '--config', argv[-1]]
            self.config = yaml.safe_load(Path(argv[-1]).read_text())
            self.finished = False
            self.returncode = None

        def poll(self):
            if self.finished:
                self.returncode = 0
            return 0 if self.finished else None

        def send_signal(self, _):
            sink = self.config['sink']
            payload = {'model': graph, 'ingest': {'spans': ingest_count, 'dropped_spans': dropped},
                       'sources': [{'type': 'ebpf', 'connector': 'obi', 'observations': 1},
                                   {'type': 'traces', 'connector': 'otlp', 'observations': 1}]}
            Path(sink['latest_path']).write_text(json.dumps(payload))
            Path(sink['signal_quality_path']).write_text('{}')
            directory = Path(sink['directory'])
            directory.mkdir(exist_ok=True)
            (directory / 'publication.json').write_text(json.dumps(payload))
            (directory / 'publication.signal-quality.json').write_text('{}')
            self.finished = True

        def wait(self):
            self.returncode = 0
            return 0

    return {'exports': inputs, 'observations': 2}, graph, Process


def test_replay_routes_actual_sources_and_preserves_producer_graph(tmp_path):
    manifest, graph, process = harness(tmp_path)
    response = Mock(status_code=200)
    sent = []
    def post(url, *, data, headers, timeout):
        assert not isinstance(data, (bytes, bytearray))
        sent.append((url, data.read(), dict(headers), timeout))
        return response
    with patch('ebpf_discovery.bering_v4.subprocess.Popen', process), \
            patch('ebpf_discovery.bering_v4.requests.get', return_value=response), \
            patch('ebpf_discovery.bering_v4.requests.post', side_effect=post):
        output, _ = replay(tmp_path / 'bering', manifest, tmp_path, 'same-deployment')
    assert output == graph
    assert sent[0][0].endswith('/sources/obi/v1/traces')
    assert sent[0][1] == Path(manifest['exports'][0]['path']).read_bytes()
    assert sent[0][2]['Content-Encoding'] == 'gzip'
    assert sent[0][2]['Content-Length'] == str(len(sent[0][1]))
    assert sent[0][3] is None
    assert sent[1][0].endswith('/v1/traces')
    assert '/sources/' not in sent[1][0]
    assert sent[1][1] == Path(manifest['exports'][1]['path']).read_bytes()
    assert sent[1][2]['Content-Length'] == str(len(sent[1][1]))
    config = yaml.safe_load((tmp_path / 'model-runtime/serve.yaml').read_text())
    assert config['sources'][0]['domain'] == 'same-deployment'
    assert config['runtime']['late_span_policy'] == 'current_window'
    assert json.loads((tmp_path / 'model.json').read_text()) == graph
    assert 'env' not in process.kwargs


def test_diagnostic_go_environment_is_child_only_and_retained(tmp_path, monkeypatch):
    manifest, _, process = harness(tmp_path)
    response = Mock(status_code=200)
    monkeypatch.setenv('GODEBUG', 'netdns=go,gctrace=0')
    monkeypatch.setenv('GOGC', '87')
    before = dict(__import__('os').environ)
    with patch('ebpf_discovery.bering_v4.subprocess.Popen', process), \
            patch('ebpf_discovery.bering_v4.requests.get', return_value=response), \
            patch('ebpf_discovery.bering_v4.requests.post', return_value=response), \
            child_go_environment({'GOMEMLIMIT': '12GiB', 'GODEBUG': 'gctrace=1'}):
        replay(tmp_path / 'bering', manifest, tmp_path, 'same-deployment')
    child = process.kwargs['env']
    assert child['GOMEMLIMIT'] == '12GiB'
    assert child['GOGC'] == '87'
    assert child['GODEBUG'] == 'netdns=go,gctrace=1'
    assert dict(__import__('os').environ) == before
    evidence = json.loads((tmp_path / 'model-runtime/replay-command.json').read_text())
    go = evidence['go_runtime_environment']
    assert go['inherited_go_environment'] == {
        'GOMEMLIMIT': None, 'GOGC': '87', 'GODEBUG': 'netdns=go,gctrace=0'}
    assert go['effective_go_environment'] == {
        'GOMEMLIMIT': '12GiB', 'GOGC': '87', 'GODEBUG': 'netdns=go,gctrace=1'}


def test_compressed_export_limit_uses_decoded_bytes(tmp_path):
    manifest, _, process = harness(tmp_path)
    export = manifest['exports'][0]
    decoded = b'x' * (6 * 1024 * 1024)
    data = gzip.compress(decoded)
    Path(export['path']).write_bytes(data)
    export['sha256'] = hashlib.sha256(data).hexdigest()
    response = Mock(status_code=200)
    with patch('ebpf_discovery.bering_v4.subprocess.Popen', process), \
            patch('ebpf_discovery.bering_v4.requests.get', return_value=response), \
            patch('ebpf_discovery.bering_v4.requests.post', return_value=response):
        replay(tmp_path / 'bering', manifest, tmp_path, 'same-deployment')
    config = yaml.safe_load((tmp_path / 'model-runtime/serve.yaml').read_text())
    assert len(data) < 5242880 < len(decoded) < config['server']['max_request_bytes']


def test_streamed_hash_mismatch_never_posts_changed_wire(tmp_path):
    manifest, _, process = harness(tmp_path)
    manifest['exports'][0]['sha256'] = '0' * 64
    response = Mock(status_code=200)
    with patch('ebpf_discovery.bering_v4.subprocess.Popen', process), \
            patch('ebpf_discovery.bering_v4.requests.get', return_value=response), \
            patch('ebpf_discovery.bering_v4.requests.post') as send:
        with pytest.raises(RuntimeError, match='changed before Bering ingest'):
            replay(tmp_path / 'bering', manifest, tmp_path, 'same-deployment')
    send.assert_not_called()


@pytest.mark.parametrize('ingest_count,dropped', [(1, 0), (2, 1)])
def test_partial_ingest_is_a_retained_technical_failure(tmp_path, ingest_count, dropped):
    manifest, _, process = harness(tmp_path, ingest_count=ingest_count, dropped=dropped)
    response = Mock(status_code=200)
    with patch('ebpf_discovery.bering_v4.subprocess.Popen', process), \
            patch('ebpf_discovery.bering_v4.requests.get', return_value=response), \
            patch('ebpf_discovery.bering_v4.requests.post', return_value=response):
        with pytest.raises(RuntimeError, match='Incomplete or split'):
            replay(tmp_path / 'bering', manifest, tmp_path, 'same-deployment')
    assert not (tmp_path / 'model.json').exists()
    evidence = json.loads((tmp_path / 'model-runtime/replay-command.json').read_text())
    assert evidence['status'] == 'technical_failure'
    assert evidence['ingest']['dropped_spans'] == dropped
