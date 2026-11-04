"""Small synthetic wiring and corruption checks; real Bering stays on Actions."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ebpf_discovery.toolchain_v4 import Toolchain as Base, digest
from ebpf_discovery.toolchain_v5 import Toolchain, PINS
from ebpf_discovery.runtime import write_json


@pytest.fixture
def engine(tmp_path, monkeypatch):
    tool = Toolchain.__new__(Toolchain)
    tool.ctx = SimpleNamespace(mode='absent', out=tmp_path)
    tool.system, tool.collector_provenance = 'otel_demo', {'collector': 'deepflow'}
    tool.tool_pins, tool.publication_mode = PINS, 'on_shutdown'
    tool.bin = tmp_path/'bin'; tool.bin.mkdir(); (tool.bin/'bering').write_bytes(b'synthetic-binary')
    tool.supplied_alias_path = tmp_path/'aliases.json'; tool.supplied_alias_path.write_text('{}')
    tool.supplied_alias_admission_path = tmp_path/'admission.json'; tool.supplied_alias_admission_path.write_text('{}')
    tool.supplied_alias_table, tool.supplied_alias_admission = {}, {'aliases': {}}
    tool.root = tmp_path/'toolchain'; tool.root.mkdir()
    tool.declaration = SimpleNamespace(CONTRACTS={'first': {}, 'second': {}})
    tool.preflight = lambda: None
    tool.input_manifests = {}
    def proof(path):
        return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)}
    for view in ('raw', 'network_scope'):
        folder = tool.root/'inputs/ebpf'/view; folder.mkdir(parents=True)
        for name in ('index.jsonl', 'shard.bin', 'values.jsonl'):
            (folder/name).write_bytes(b'synthetic '+name.encode())
        ebpf = {'observations': 2, 'exports': [], 'exported_wire_bytes': 20,
                'stream_exports': [{'request_index': proof(folder/'index.jsonl'),
                    'shards': [proof(folder/'shard.bin')], 'runtime_identity_values': proof(folder/'values.jsonl')}]}
        native = {'observations': 0, 'exports': [], 'stream_exports': [], 'exported_wire_bytes': 0}
        groups = []
        for source, value in [('ebpf', ebpf), ('native', native)]:
            path = tool.root/'inputs'/source/view/'observations.json'
            write_json(path, value); tool.input_manifests[source, view] = path, value
            groups.append(proof(path))
        combined = {'observations': 2, 'exports': [], 'stream_exports': [],
                    'exported_wire_bytes': 20, 'ordered_request_group_manifests': groups}
        path = tool.root/'inputs/combined'/view/'observations.json'
        write_json(path, combined); tool.input_manifests['combined', view] = path, combined
    tool.prepare_inputs = lambda plans: None
    calls = []
    def synthetic_discover(self, input_path, folder, overlay=None, prefix='model'):
        folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
        calls.append((str(input_path), str(folder)))
        model = {'services': [], 'edges': [], 'endpoints': []}; quality = {}
        for name, value in [('observed.json', model), ('observed.signal-quality.json', quality),
                            ('observed.snapshot.json', {'model': model})]:
            write_json(folder/name, value)
        profile = self._identical_input_profile()
        record = {'status': 'complete', 'returncode': 0, 'argv': [str(self.bin/'bering')],
                  **{k: profile[k] for k in ('source_profile','source_domain','publication_mode',
                                           'clock_admission_filter','go_runtime_environment')},
                  'ingest': {'spans': 2, 'dropped_spans': 0, 'late_spans': 0}}
        write_json(folder/'observed-runtime/replay-command.json', record)
        for name in ('serve.yaml', 'accepted-request-sequence.jsonl'):
            (folder/'observed-runtime'/name).write_text('synthetic metadata\n')
        return model, quality
    monkeypatch.setattr(Base, 'discover', synthetic_discover)
    operations = []
    def operation(source, view, name, contract, input_path, manifest, shared, model, quality, folder):
        folder.mkdir(parents=True, exist_ok=True); operations.append((source, view, name, str(shared)))
        answer = {'available': bool(manifest['observations']), 'prediction': .875 if manifest['observations'] else None}
        if manifest['observations']: write_json(folder/'simulation.command.json', {'synthetic': True})
        write_json(folder/'forecast.json', answer)
        return answer
    tool.forecast_operation = operation
    return tool, calls, operations


def test_same_input_uses_two_genuine_origins_and_keeps_every_operation(engine):
    tool, calls, operations = engine
    result = Base.forecast(tool, [])
    assert len(calls) == 2 and len(operations) == 12
    assert result['ebpf'] == result['combined']
    for view in ('raw', 'network_scope'):
        folder = tool.root/'discovery/combined'/view
        assert not (folder/'observed.json').exists()
        assert not (folder/'observed-runtime').exists()
        proof = json.loads((folder/'shared-observed-reference.json').read_text())
        assert proof['origin_source'] == 'ebpf' and proof['additional_Bering_execution'] is False
        assert all(Path(p['path']).is_file() and digest(p['path']) == p['sha256']
                   for p in proof['genuine_origin_files'].values())
    summary = json.loads((tool.root/'execution-summary.json').read_text())['branches']
    assert sum(r['sheaft_executed'] for r in summary) == 8
    assert all('/ebpf/' in r['bering_discovery_record'].replace('\\','/')
               and r['bering_discovery_shared_across_sources'] for r in summary if r['source']=='combined')


@pytest.mark.parametrize('kind', ['source_manifest', 'combined_manifest', 'native_manifest',
                                 'source_shard', 'source_index', 'source_values',
                                 'origin_graph', 'origin_quality', 'origin_replay', 'foreign_group'])
def test_modified_input_or_genuine_origin_cannot_be_shared(engine, kind):
    tool, _, _ = engine
    source_path, _ = tool.input_manifests['ebpf','raw']
    shared = tool.root/'discovery/ebpf/raw'
    tool.discover(source_path, shared, prefix='observed')
    paths = {'source_manifest': source_path, 'source_shard': source_path.parent/'shard.bin',
             'combined_manifest': tool.input_manifests['combined','raw'][0],
             'native_manifest': tool.input_manifests['native','raw'][0],
             'source_index': source_path.parent/'index.jsonl', 'source_values': source_path.parent/'values.jsonl',
             'origin_graph': shared/'observed.json', 'origin_quality': shared/'observed.signal-quality.json',
             'origin_replay': shared/'observed-runtime/replay-command.json'}
    if kind == 'foreign_group':
        other = tool.root/'foreign.json'; other.write_bytes(source_path.read_bytes())
        tool.input_manifests['combined','raw'][1]['ordered_request_group_manifests'][0]['path'] = str(other)
    elif kind in ('combined_manifest', 'native_manifest'):
        changed = json.loads(paths[kind].read_text())
        changed['observations'] += 1
        write_json(paths[kind], changed)
    else:
        with paths[kind].open('ab') as stream: stream.write(b'changed')
    with pytest.raises(ValueError): tool.reuse_observed_discovery('combined','raw')


@pytest.mark.parametrize('condition', ['native_present', 'other_collector', 'other_system',
                                       'other_mode', 'windowed', 'other_profile', 'no_actual_origin'])
def test_unqualified_cases_keep_original_discovery(engine, condition):
    tool, _, _ = engine
    if condition != 'no_actual_origin':
        tool.discover(tool.input_manifests['ebpf','raw'][0], tool.root/'discovery/ebpf/raw', prefix='observed')
    if condition == 'native_present': tool.input_manifests['native','raw'][1]['observations'] = 1
    if condition == 'other_collector': tool.collector_provenance = {'collector': 'coroot'}
    if condition == 'other_system': tool.system = 'petclinic'
    if condition == 'other_mode': tool.ctx.mode = 'partial'
    if condition == 'windowed': tool.publication_mode = 'windowed'
    if condition == 'other_profile': tool.bering_source_profile = lambda: {'source_id':'different','input_type':'ebpf-otlp'}
    assert tool.reuse_observed_discovery('combined','raw') is None


def test_default_path_without_reuse_still_executes_four_discoveries(engine):
    tool, calls, operations = engine
    tool.reuse_observed_discovery = lambda source, view: None
    Base.forecast(tool, [])
    assert len(calls) == 4 and len(operations) == 12
