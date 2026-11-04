"""One fixed Actions-only comparison of the new operator on its retained complete input."""
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import resource
import shutil
import stat
import tempfile
import subprocess
import time
from types import SimpleNamespace
import zipfile

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery.raw_v4 import _scope_validated_deepflow_export
from ebpf_discovery.toolchain_v5 import PINS

assert os.environ.get('GITHUB_ACTIONS') == 'true'
out = Path('work/shared-scope-qualification'); out.mkdir(parents=True, exist_ok=False)
inputs = Path('work/shared-scope-input'); inputs.mkdir(parents=True, exist_ok=False)
repo = 'repos/a-a-k/ebpf-model-discovery-experiments/'
api = lambda path: json.loads(subprocess.check_output(['gh', 'api', repo + path]))
status = {'status': 'started', 'source': os.environ['GITHUB_SHA'],
          'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
          'started_ns': time.time_ns(), 'new_models_or_traffic': False,
          'full_current_preparation_measured': False, 'whole_six_hour_headroom_GO': False}
phases, clocks = {}, Counter()
source = 'f045cc0adec187ec00443da0bea72b4ec4d2082e'
workflow_source = '06d7d52bfa4b7768a4cabf02f4e66f109b3a9492'
expected_meta = {'toolchain/inputs/ebpf/raw/observations.json':
 'd298ba0a8765af45e1e2da9091318d832df4440c4a9c92ef609c05df2426ed0a',
 'toolchain/inputs/ebpf/network_scope/observations.json':
 '6713eb44b6126e28a83b3411a445b512cfb80054610385745e33bad3cd073fa0'}
metadata_names = ['worker-status.json', 'worker-provenance.json', 'output-manifest.json',
                  'toolchain/input-preparation-cost.json', *expected_meta]
try:
    phase_start = time.monotonic_ns()
    worker = api('actions/runs/41676388484')
    assert (worker['head_sha'], worker['status'], worker['conclusion'], worker['run_attempt']) == (
        workflow_source, 'completed', 'success', 1)
    assert worker['path'] == '.github/workflows/toolchain-worker-v4.yml' and worker['event'] == 'workflow_dispatch'
    jobs = api('actions/runs/41676388484/jobs?per_page=100')
    assert jobs['total_count'] == len(jobs['jobs']) == 1
    assert (jobs['jobs'][0]['id'], jobs['jobs'][0]['conclusion']) == (126058043364, 'success')
    artifact = api('actions/artifacts/13264538182')
    assert (artifact['name'], artifact['size_in_bytes'], artifact['digest'], artifact['expired']) == (
        'toolchain-v4-otel_demo-absent-8-41676388484', 2331631528,
        'sha256:7895b7d786c5150517166a473e9bc5711070c00d3e7902c0c4a26ad1f77e8df2', False)
    assert (artifact['workflow_run']['id'], artifact['workflow_run']['head_sha']) == (41676388484, workflow_source)
    prefix = api('actions/artifacts/13247569257')
    assert (prefix['size_in_bytes'], prefix['digest'], prefix['expired']) == (3129334984,
        'sha256:0923153ef0a45b035711d062cd173b5024f43d0ad9c273962e95b6105c68e7f0', False)
    assert (prefix['workflow_run']['id'], prefix['workflow_run']['head_sha']) == (41642766254, source)
    assert prefix['name'] == 'training-v4-otel_demo-absent-8-41642766254'
    for name, value in [('worker-run-api', worker), ('worker-jobs-api', jobs),
                        ('worker-artifact-api', artifact), ('prefix-artifact-api', prefix)]:
        remote._atomic_json(out / (name + '.json'), value)
    phases['source_API'] = (time.monotonic_ns() - phase_start) / 1e9
    guard = {'required_bytes': artifact['size_in_bytes'] + 1024**3,
             'actual_available_bytes': shutil.disk_usage(inputs).free}
    remote._atomic_json(out / 'disk-before-download.json', guard)
    assert guard['actual_available_bytes'] >= guard['required_bytes']
    phase_start = time.monotonic_ns()
    archive = inputs / 'original-worker.zip'
    with archive.open('xb') as stream:
        subprocess.run(['gh', 'api', repo + 'actions/artifacts/13264538182/zip'], stdout=stream, check=True)
    assert archive.stat().st_size == artifact['size_in_bytes'] and 'sha256:' + remote._sha(archive) == artifact['digest']
    phases['whole_worker_download_and_SHA'] = (time.monotonic_ns() - phase_start) / 1e9
    remote._atomic_json(out / 'phase-costs.json', phases)
    phase_start = time.monotonic_ns()
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist(); names = [e.filename for e in entries]
        assert len(names) == len(set(names))
        meta_bodies = {name: bundle.read(name) for name in metadata_names}
        for name, digest in expected_meta.items():
            assert hashlib.sha256(meta_bodies[name]).hexdigest() == digest
        old = {name: json.loads(body) for name, body in meta_bodies.items()}
        old_status, provenance, output_manifest = (old[name] for name in metadata_names[:3])
        # Preserve thin source identities and the small reference manifests even
        # if a later provenance assertion rejects a header.
        remote._atomic_json(out / 'original-metadata-digests.json', {
            name: {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
            for name, body in meta_bodies.items()})
        remote._atomic_json(out / 'original-worker-identities.json', {
            'status_identity': old_status.get('identity'),
            'provenance_identity': provenance.get('identity'),
            'output_identity': output_manifest.get('identity'),
            'implementation_sha': provenance.get('implementation_sha'),
            'scientific_sha': provenance.get('scientific_sha'),
            'workflow_sha': provenance.get('workflow_sha'),
            'worker_run_id': provenance.get('worker_run_id'),
            'checkpoint_artifact': provenance.get('checkpoint_artifact'),
            'binaries': provenance.get('binaries')})
        for name in ('worker-status.json', 'toolchain/input-preparation-cost.json', *expected_meta):
            assert len(meta_bodies[name]) < 4 * 1024**2
            target = out / 'original-metadata' / name
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(meta_bodies[name])
        assert old_status['schema_version'] == provenance['schema_version'] == 'remote-toolchain-worker-v4'
        assert output_manifest['schema_version'] == 'remote-toolchain-output-v4'

        identity = old_status['identity']
        assert old_status['status'] == 'complete' and old_status['checkpoint_unchanged'] is True
        assert old_status['new_application_traffic'] is False and old_status['completed_campaign_cell'] is False
        wanted_identity = {'commit': source, 'run_id': '41642766254', 'system': 'otel_demo',
            'mode': 'absent', 'seed': '8',
            'manifest_sha256': '2efc7e380ef779e7073e4ba267e16619420ed81c12b37c3d336c83828d241925'}
        assert all(str(identity[key]) == value for key, value in wanted_identity.items())
        assert (str(identity['worker_run_id']), identity['worker_workflow_sha']) == ('41676388484', workflow_source)
        assert identity['plans_sha256'] == '117e0e39fb3c20437454448bfc4980cf8e25d6eaf6101551fae1e0d1b20990fe'
        assert identity['training_index_proof_sha256'] == 'a7db8f95d74f28f57b19d87fc090f3d58606cd7feeac4ee9c2a60d42359c88b5'
        assert provenance['scientific_sha'] == provenance['implementation_sha'] == source
        assert provenance['workflow_sha'] == workflow_source and str(provenance['worker_run_id']) == '41676388484'
        assert str(provenance['worker_run_attempt']) == '1' and provenance['checkpoint_unchanged'] is True
        assert provenance['new_application_traffic'] is False and provenance['completed_campaign_cell'] is False
        assert provenance['checkpoint_artifact'] == {key: identity[key] for key in ('artifact_id', 'artifact_name', 'artifact_digest')}
        assert str(identity['artifact_id']) == '13247569257' and identity['artifact_digest'] == prefix['digest']
        assert identity['artifact_name'] == prefix['name']
        assert provenance['checkpoint_input']['manifest_sha256'] == wanted_identity['manifest_sha256']
        assert remote._json_sha(provenance['training_index_proof']) == identity['training_index_proof_sha256']
        assert provenance['plans_sha256'] == output_manifest['plans_sha256'] == identity['plans_sha256']
        assert output_manifest['training_index_proof_sha256'] == identity['training_index_proof_sha256']
        for header in (provenance, output_manifest):
            assert all(str(header['identity'][key]) == value for key, value in wanted_identity.items())
            assert str(header['worker_run_id']) == '41676388484' and str(header['worker_run_attempt']) == '1'
            assert header['workflow_sha'] == workflow_source
        assert provenance['toolchain_files'] == output_manifest['toolchain_files']
        claims = output_manifest['toolchain_files']
        assert old_status['toolchain_files'] == len(claims)
        assert {name: proof['commit'] for name, proof in provenance['binaries'].items()} == {name.lower(): pin for name, pin in PINS.items()}
        raw = old['toolchain/inputs/ebpf/raw/observations.json']
        old_network = old['toolchain/inputs/ebpf/network_scope/observations.json']
        raw_stream, network_stream = raw['stream_exports'][0], old_network['stream_exports'][0]
        assert len(raw['stream_exports']) == len(old_network['stream_exports']) == 1 and not raw['exports'] and not old_network['exports']
        assert (raw_stream['requests'], raw_stream['observations'], raw_stream['runtime_identity_transformations']) == (3275, 837860, 793692)
        assert len(raw_stream['shards']) == len(network_stream['shards']) == 69
        root = Path(raw_stream['request_index']['path']).parents[5]
        assert root == Path(os.environ['GITHUB_WORKSPACE']) / 'work/campaign' and not root.exists()
        data = [raw_stream['request_index'], *raw_stream['shards'], raw_stream['runtime_identity_values'], network_stream['request_index']]
        payloads = {Path(c['path']).relative_to(root).as_posix(): c for c in data}
        assert len(payloads) == 72 and sum(c['bytes'] for c in data) == 7083550435
        selected = set(payloads) | set(metadata_names); assert len(selected) == 78
        for name in selected:
            entry = bundle.getinfo(name)
            assert not entry.is_dir() and not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name
            mode = entry.external_attr >> 16
            assert not stat.S_ISLNK(mode) and (stat.S_IFMT(mode) == 0 or stat.S_ISREG(mode))
            if name.startswith('toolchain/'):
                claim = claims[name.removeprefix('toolchain/')]
                assert set(claim) == {'bytes', 'sha256'} and claim['bytes'] == entry.file_size
                if name in payloads: assert (claim['bytes'], claim['sha256']) == (payloads[name]['bytes'], payloads[name]['sha256'])
                else: assert claim['sha256'] == hashlib.sha256(meta_bodies[name]).hexdigest()
        # The old network bodies remain in the original archive. Bind every
        # comparison reference to the completed worker's output census too.
        for claim in network_stream['shards']:
            relative = Path(claim['path']).relative_to(root / 'toolchain').as_posix()
            assert (claims[relative]['bytes'], claims[relative]['sha256']) == (claim['bytes'], claim['sha256'])
        metadata_bytes = sum(bundle.getinfo(name).file_size for name in metadata_names)
        required = (sum(c['bytes'] for c in data) + metadata_bytes + network_stream['wire_bytes']
                    + network_stream['request_index']['bytes'] + 4 * raw_stream['runtime_identity_values']['bytes'] + 1024**3)
        guard = {'required_additional_bytes': required, 'actual_available_bytes': shutil.disk_usage(inputs).free,
                 'selected_payload_bytes': sum(c['bytes'] for c in data), 'actual_metadata_bytes': metadata_bytes,
                 'new_scope_wire_bytes': network_stream['wire_bytes'], 'new_scope_index_bytes': network_stream['request_index']['bytes'],
                 'temporary_value_index_reserve_bytes': 4 * raw_stream['runtime_identity_values']['bytes'],
                 'archive_already_allocated': True, 'source_SQL_or_models_restored': False}
        remote._atomic_json(out / 'disk-before-selected-restore.json', guard)
        assert guard['actual_available_bytes'] >= required
        restored = []
        for name in sorted(selected):
            if name == 'toolchain/inputs/ebpf/network_scope/exports/ebpf-request-index.jsonl':
                target = inputs / 'original-network-request-index.jsonl'
            elif name == 'toolchain/inputs/ebpf/raw/observations.json' or name in payloads:
                target = root / name
            else:
                target = inputs / 'original-metadata' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(name) as source_stream, target.open('xb') as saved:
                shutil.copyfileobj(source_stream, saved, 1024 * 1024)
            actual = remote._sha(target); size = target.stat().st_size
            expected = payloads[name]['sha256'] if name in payloads else hashlib.sha256(meta_bodies[name]).hexdigest()
            assert actual == expected
            restored.append({'member': name, 'path': str(target), 'bytes': size, 'sha256': actual,
                             'ZIP_CRC32': f'{bundle.getinfo(name).CRC:08x}', 'read_to_EOF': True})
        assert len(restored) == 78
    remote._atomic_json(out / 'selected-input-restoration.json', {'files': restored, 'whole_original_ZIP_SHA_verified': True})
    remote._atomic_json(out / 'original-source-validation.json', {
        'worker_identity': wanted_identity, 'original_worker_run': 41676388484,
        'original_workflow_source': workflow_source, 'original_implementation_source': provenance['implementation_sha'],
        'metadata_members': {name: {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()} for name, body in meta_bodies.items()},
        'complete_output_census_entries': len(claims), 'output_census_SHA256': remote._json_sha(claims),
        'original_checkpoint_input_proof_SHA256': remote._json_sha(provenance['checkpoint_input']),
        'original_training_index_proof_SHA256': remote._json_sha(provenance['training_index_proof']),
        'all_selected_claims_bound': True, 'unselected_network_wire_claims_bound_to_original_output_census': True,
        'new_source_codec_or_projection_pass_executed': False,
        'new_SQL_or_whole_original_source_prefix_reverification_claimed': False})
    phases['selected_restore_CRC_SHA_and_source_provenance'] = (time.monotonic_ns() - phase_start) / 1e9
    remote._atomic_json(out / 'phase-costs.json', phases)
    # Use exactly the authority proof consumed by the production helper. Its
    # existing reader independently rechecks every full value and request ref.
    # Keep the existing reader's temporary SQLite on the volume covered by the guard.
    temporary_values = inputs / 'reader-tmp'; temporary_values.mkdir()
    tempfile.tempdir = str(temporary_values.resolve())
    status['temporary_value_index_root'] = tempfile.tempdir
    authority = SimpleNamespace(value_store_proof=raw_stream['runtime_identity_values'])
    raw_path = root / 'toolchain/inputs/ebpf/raw/observations.json'
    derivation_window = [time.time_ns()]
    phase_start = time.monotonic_ns()
    try:
        current = _scope_validated_deepflow_export(raw_path, expected_meta['toolchain/inputs/ebpf/raw/observations.json'],
            root / 'toolchain/inputs/ebpf/network_scope/exports', 'otel_demo-routed-network', authority)
        # The unchanged production caller makes the same assignment.
        current['exported_wire_bytes'] = current['stream_exports'][0]['wire_bytes']
    finally:
        derivation_window.append(time.time_ns())
        phases['current_helper_derivation_and_full_input_verification'] = (time.monotonic_ns() - phase_start) / 1e9
        remote._atomic_json(out / 'phase-costs.json', phases)
        receipt = root / 'toolchain/inputs/ebpf/network_scope/network-scope-derivation.json'
        if receipt.is_file(): shutil.copyfile(receipt, out / 'network-scope-derivation.json')
    remote._atomic_json(out / 'new-network-observations.json', current)
    phase_start = time.monotonic_ns()
    spec = importlib.util.spec_from_file_location('existing_clock_equality', 'scripts/check-fixed-dsb-path-preparation-v5.py')
    equality = importlib.util.module_from_spec(spec); spec.loader.exec_module(equality)
    cost = old['toolchain/input-preparation-cost.json']; old_window = (cost['started_ns'], cost['ended_ns'])
    assert old_status['started_ns'] <= old_window[0] <= old_window[1] <= old_status['ended_ns']
    new_stream = current['stream_exports'][0]
    old_index = inputs / 'original-network-request-index.jsonl'; new_index = Path(new_stream['request_index']['path'])
    assert (old_index.stat().st_size, remote._sha(old_index)) == (network_stream['request_index']['bytes'], network_stream['request_index']['sha256'])
    assert (new_index.stat().st_size, remote._sha(new_index)) == (new_stream['request_index']['bytes'], new_stream['request_index']['sha256'])
    normalized = hashlib.sha256(); rows = 0
    with old_index.open('rb') as old_rows, new_index.open('rb') as new_rows:
        for ordinal, (left_line, right_line) in enumerate(itertools.zip_longest(old_rows, new_rows), 1):
            if left_line is None or right_line is None: raise ValueError('request index row count changed')
            left, right = json.loads(left_line), json.loads(right_line)
            for line, value in ((left_line, left), (right_line, right)):
                if (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode() != line:
                    raise ValueError('request index is not exact canonical JSON')
            old_clock = left['derived_otlp_proof']['codec_accounting']['index_preparation_cost']
            new_clock = right['derived_otlp_proof']['codec_accounting']['index_preparation_cost']
            try:
                equality.strip_clock_pair(old_clock, new_clock, old_window, old_window, clocks, 'reused_source_codec_cost')
                equality.equal(left, right)
            except (ValueError, KeyError) as error:
                remote._atomic_json(out / 'first-index-difference.json', {'row': ordinal,
                    'changed_top_level_fields': [key for key in sorted(set(left) | set(right))
                        if key not in left or key not in right or equality.canonical(left[key]) != equality.canonical(right[key])],
                    'old_record_SHA256': hashlib.sha256(equality.canonical(left)).hexdigest(),
                    'new_record_SHA256': hashlib.sha256(equality.canonical(right)).hexdigest(), 'error': repr(error)})
                raise
            normalized.update(equality.canonical(left) + b'\n'); rows += 1
    assert rows == network_stream['requests'] == 3275
    assert new_stream['shards'] == network_stream['shards']
    assert new_stream['runtime_identity_values'] == network_stream['runtime_identity_values']
    for claim in [new_stream['request_index'], *new_stream['shards'], new_stream['runtime_identity_values']]:
        path = Path(claim['path']); assert path.stat().st_size == claim['bytes'] and remote._sha(path) == claim['sha256']
    left, right = deepcopy(old_network), deepcopy(current)
    for manifest in (left, right):
        manifest['stream_exports'][0]['request_index']['sha256'] = 'verified-equivalent-child:' + normalized.hexdigest()
    equality.strip_clock_pair(left['stream_exports'][0]['archive_preparation_cost'],
        right['stream_exports'][0]['archive_preparation_cost'], old_window, tuple(derivation_window), clocks, 'actual_archive_cost')
    equality.equal(left, right)
    phases['all_records_manifest_wire_value_comparison'] = (time.monotonic_ns() - phase_start) / 1e9
    remote._atomic_json(out / 'qualification.json', {
        'schema_version': 'direct-original-prepared-raw-scope-equivalence-v1', 'source': status['source'],
        'original_worker_run': 41676388484, 'original_implementation_source': provenance['implementation_sha'],
        'old_literal_network_index': network_stream['request_index'], 'new_literal_network_index': new_stream['request_index'],
        'all_ordered_nonclock_index_fields_exact': True, 'ordered_nonclock_rows_SHA256': normalized.hexdigest(),
        'request_index_rows': rows, 'all_wire_shards_exact_original_bytes_SHA': True,
        'all_69_original_raw_shards_and_complete_values_verified': True, 'all_other_manifest_fields_exact': True,
        'observations': new_stream['observations'], 'runtime_identity_transformations': new_stream['runtime_identity_transformations'],
        'codec_proof_clock_window_both_original': old_window, 'current_derivation_clock_window': derivation_window,
        'actual_operator_seconds': phases['current_helper_derivation_and_full_input_verification'],
        'historical_whole_preparation_seconds': (old_window[1] - old_window[0]) / 1e9,
        'whole_current_preparation_measured': False, 'six_hour_main_headroom_GO': False,
        'Bering_Sheaft_or_application_traffic_executed': False,
        'cost_boundary': 'All original source/raw/value preparation, old network, failed fe2h, CI, current download/CRC/SHA/helper/second hashes/comparison/retention/review costs retained. Reused original source cost counted once. SELF CPU excludes children, cache/host/order confounds and human effort unknown.'})
    status['status'] = 'complete'
except BaseException as error:
    status.update(status='technical_failure', error=repr(error))
    raise
finally:
    remote._atomic_json(out / 'allowed-cost-clock-pairs.json', [
        {'scope': key[0], 'old_started_ns': key[1], 'old_ended_ns': key[2],
         'new_started_ns': key[3], 'new_ended_ns': key[4], 'occurrences': count}
        for key, count in sorted(clocks.items())])
    status.update(ended_ns=time.time_ns(), SELF_user_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,
        SELF_system_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime,
        SELF_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    remote._atomic_json(out / 'status.json', status); remote._atomic_json(out / 'phase-costs.json', phases)
    print(json.dumps(status), flush=True)
