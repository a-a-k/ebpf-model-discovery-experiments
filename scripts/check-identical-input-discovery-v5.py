"""Actions-only tiny real-Bering wiring check, not an empirical study case."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

from ebpf_discovery.bering_v4 import child_go_environment
from ebpf_discovery.raw_v4 import _scope_validated_deepflow_export
from ebpf_discovery.remote_toolchain_v4 import WORKER_BERING_GO_ENV
from ebpf_discovery.runtime import write_json
from ebpf_discovery.toolchain_v4 import Toolchain as Base, digest
from ebpf_discovery.toolchain_v5 import Toolchain, PINS

assert os.environ.get('GITHUB_ACTIONS') == 'true'
out = Path('work/identical-input-discovery-fixture').resolve()
out.mkdir(parents=True, exist_ok=False)
tool = Toolchain.__new__(Toolchain)
tool.ctx = SimpleNamespace(out=out, mode='absent')
tool.system, tool.collector_provenance = 'otel_demo', {'collector':'deepflow'}
tool.tool_pins, tool.publication_mode = PINS, 'on_shutdown'
tool.bin = Path('work/toolchain-build/bin').resolve()
build = json.loads(Path('work/toolchain-build/toolchain-build.json').read_text())
binary = next(row for row in build['binaries'] if row['name']=='bering')
assert binary['commit'] == PINS['Bering'] and digest(tool.bin/'bering') == binary['binary_sha256']
tool.supplied_alias_path = out/'aliases.json'
tool.supplied_alias_admission_path = out/'admission.json'
write_json(tool.supplied_alias_path, {})
write_json(tool.supplied_alias_admission_path, {'aliases':{}})
tool.supplied_alias_table, tool.supplied_alias_admission = {}, {'aliases':{}}
tool.root = out/'toolchain'; tool.root.mkdir()
spec = importlib.util.spec_from_file_location('existing_two_flow_fixture', 'tests/test_deepflow_handoff_v5.py')
fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
store, resolver, raw_path, _ = fixture._prepared_scope_source(tool.root)
raw = json.loads(raw_path.read_text())
raw['exported_wire_bytes'] = raw['stream_exports'][0]['wire_bytes']
write_json(raw_path, raw)
network_folder = tool.root/'inputs/ebpf/network_scope'; network_folder.mkdir(parents=True)
network = _scope_validated_deepflow_export(raw_path, digest(raw_path), network_folder/'exports',
                                          'otel_demo-routed-network', resolver)
network['exported_wire_bytes'] = network['stream_exports'][0]['wire_bytes']
network_path = network_folder/'observations.json'; write_json(network_path, network)
tool.input_manifests = {}
for view, path, value in [('raw',raw_path,raw), ('network_scope',network_path,network)]:
    native = {'exports':[], 'stream_exports':[], 'observations':0, 'exported_wire_bytes':0}
    native_path = tool.root/'inputs/native'/view/'observations.json'; write_json(native_path, native)
    groups = [{'path':str(p), 'bytes':p.stat().st_size, 'sha256':digest(p)} for p in (path,native_path)]
    combined = {'exports':[], 'stream_exports':[], 'observations':2,
                'exported_wire_bytes':value['exported_wire_bytes'], 'ordered_request_group_manifests':groups}
    combined_path = tool.root/'inputs/combined'/view/'observations.json'; write_json(combined_path, combined)
    for source, p, manifest in [('ebpf',path,value), ('native',native_path,native),
                                ('combined',combined_path,combined)]:
        tool.input_manifests[source,view] = p, manifest
tool.preflight = lambda: None
tool.prepare_inputs = lambda plans: None
tool.declaration = SimpleNamespace(CONTRACTS={'synthetic_wiring':{}})
operations = []
def inspect_operation(source, view, name, contract, input_path, manifest, shared, model, quality, folder):
    folder.mkdir(parents=True, exist_ok=True); operations.append([source,view,name])
    if manifest['observations']:
        write_json(folder/'observed-reference.json', {
            'folder':os.path.relpath(shared,folder), 'files':{n:digest(shared/n) for n in
                ('observed.json','observed.signal-quality.json','observed.snapshot.json')}})
    answer = {'available':False, 'prediction':None, 'reason':'engineering_fixture_no_scored_operation'}
    write_json(folder/'forecast.json', answer)
    return answer
tool.forecast_operation = inspect_operation
try:
    with child_go_environment(WORKER_BERING_GO_ENV):
        result = Base.forecast(tool, [])
    physical = sorted(tool.root.glob('discovery/*/*/observed-runtime/replay-command.json'))
    references = sorted(tool.root.glob('discovery/*/*/shared-observed-reference.json'))
    assert len(physical) == len(references) == 2 and len(operations) == 6
    assert result['ebpf'] == result['combined']
    for path in physical:
        replay = json.loads(path.read_text())
        assert replay['status']=='complete' and replay['returncode']==0
        assert replay['ingest']['spans']==2 and replay['ingest']['dropped_spans']==replay['ingest']['late_spans']==0
    for path in references:
        reference = json.loads(path.read_text())
        assert reference['origin_source']=='ebpf' and reference['additional_Bering_execution'] is False
        assert not (path.parent/'observed.json').exists() and not (path.parent/'observed-runtime').exists()
        assert all(digest(p['path'])==p['sha256'] for p in reference['genuine_origin_files'].values())
    write_json(out/'qualification.json', {'status':'complete', 'kind':'tiny_synthetic_real_Bering_wiring_only',
        'source':os.environ['GITHUB_SHA'], 'Bering_pin':PINS['Bering'], 'binary_SHA256':digest(tool.bin/'bering'),
        'observations_per_view':2, 'physical_Bering_executions':2, 'logical_nonempty_source_views':4,
        'separate_operation_dispatches':operations, 'fabricated_combined_replays':False,
        'source_mutation_and_fallback_unit_tests':'tests/test_identical_input_discovery_v5.py',
        'main_scientific_or_six_hour_admission':False, 'Sheaft_executed':False,
        'original_empirical_payloads_used':False})
finally:
    resolver.close(); store.db.close()
