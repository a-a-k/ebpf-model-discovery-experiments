"""One Actions-only exact original prefix construction and full preparation check."""
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
from ebpf_discovery.runtime import Context
from ebpf_discovery.store_v5 import ObservationStoreV5
import importlib
from ebpf_discovery.toolchain_v5 import PINS

assert os.environ.get('GITHUB_ACTIONS') == 'true'
out = Path('work/frozen-admission-qualification'); out.mkdir(parents=True, exist_ok=False)
inputs = Path('work/frozen-admission-input'); inputs.mkdir(parents=True, exist_ok=False)
repo = 'repos/a-a-k/ebpf-model-discovery-experiments/'
api = lambda path: json.loads(subprocess.check_output(['gh', 'api', repo + path]))
status = {'status': 'started', 'source': os.environ['GITHUB_SHA'],
          'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
          'started_ns': time.time_ns(), 'new_models_or_traffic': False,
          'full_current_preparation_measured': False, 'whole_six_hour_headroom_GO': False}
phases, clocks = {}, Counter()
root = None
store = None
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
        root = Path(raw['stream_exports'][0]['request_index']['path']).parents[5]
        assert root == Path(os.environ['GITHUB_WORKSPACE'])/'work/campaign' and not root.exists()
        baseline_indexes = {}
        for variant, manifest in [('raw', raw), ('network_scope', old_network)]:
            assert len(manifest['stream_exports']) == 1 and not manifest['exports']
            stream = manifest['stream_exports'][0]
            assert (stream['requests'], stream['observations'], stream['runtime_identity_transformations']) == (3275, 837860, 793692)
            assert len(stream['shards']) == 69
            for claim in [stream['request_index'], *stream['shards'], stream['runtime_identity_values']]:
                name = Path(claim['path']).relative_to(root).as_posix()
                assert claims[name.removeprefix('toolchain/')] == {key: claim[key] for key in ('bytes', 'sha256')}
            claim = stream['request_index']
            name = Path(claim['path']).relative_to(root).as_posix()
            entry = bundle.getinfo(name)
            assert entry.file_size == claim['bytes'] and not stat.S_ISLNK(entry.external_attr >> 16)
            target = inputs / ('original-' + variant + '-index.jsonl')
            with bundle.open(name) as source_stream, target.open('xb') as saved:
                shutil.copyfileobj(source_stream, saved, 1024*1024)
            assert target.stat().st_size == claim['bytes'] and remote._sha(target) == claim['sha256']
            baseline_indexes[variant] = target
        remote._atomic_json(out/'original-source-validation.json', {
            'worker_identity': identity, 'original_worker_run': 41676388484,
            'original_scientific_implementation': source,
            'original_workflow_definition': workflow_source,
            'whole_worker_ZIP_SHA_verified': True,
            'complete_original_output_census_entries': len(claims),
            'complete_original_output_census_sha256': remote._json_sha(claims),
            'every_old_raw_network_and_value_claim_bound': True,
            'original_indexes_EOF_CRC_and_SHA_verified': True})
    phases['original_worker_metadata_provenance_and_two_indexes'] = (time.monotonic_ns()-phase_start)/1e9
    remote._atomic_json(out/'phase-costs.json', phases)
    phase_start = time.monotonic_ns()
    prefix_archive = inputs/'original-prefix.zip'
    guard = {'required_bytes': prefix['size_in_bytes']+1024**3,
             'actual_available_bytes': shutil.disk_usage(inputs).free}
    remote._atomic_json(out/'disk-before-prefix-download.json', guard)
    assert guard['actual_available_bytes'] >= guard['required_bytes']
    with prefix_archive.open('xb') as stream:
        subprocess.run(['gh', 'api', repo+'actions/artifacts/13247569257/zip'], stdout=stream, check=True)
    assert prefix_archive.stat().st_size == prefix['size_in_bytes'] and 'sha256:'+remote._sha(prefix_archive) == prefix['digest']
    phases['whole_original_prefix_download_and_SHA'] = (time.monotonic_ns()-phase_start)/1e9
    with zipfile.ZipFile(prefix_archive) as bundle:
        entries = bundle.infolist()
        assert len(entries) == len({e.filename for e in entries})
        prefix_bytes = sum(e.file_size for e in entries if not e.is_dir())
        sql_bytes = bundle.getinfo('observation-index.sqlite').file_size
    expected_wire = sum(m['stream_exports'][0]['wire_bytes'] for m in (raw, old_network))
    new_indexes = sum(m['stream_exports'][0]['request_index']['bytes'] for m in (raw, old_network))
    value_reserve = 4*raw['stream_exports'][0]['runtime_identity_values']['bytes']
    required = prefix_bytes+3*sql_bytes+expected_wire+new_indexes+value_reserve+1024**3
    guard = {'required_additional_bytes': required, 'actual_available_bytes': shutil.disk_usage(inputs).free,
             'complete_original_prefix_bytes': prefix_bytes, 'three_SQL_preparation_reserve_bytes': 3*sql_bytes,
             'new_both_view_wire_bytes': expected_wire, 'new_request_indexes_bytes': new_indexes,
             'helper_temporary_value_SQLite_reserve_bytes': value_reserve,
             'both_original_ZIPs_and_baseline_indexes_already_allocated': True}
    remote._atomic_json(out/'disk-before-complete-prefix-restore.json', guard)
    assert guard['actual_available_bytes'] >= required
    phase_start = time.monotonic_ns()
    remote._safe_extract(prefix_archive, root)
    expected = {key: identity[key] for key in remote.IDENTITY_KEYS}
    expected['training_index_proof_sha256'] = identity['training_index_proof_sha256']
    manifest, before = remote._validate_checkpoint(root, expected)
    index_proof = remote._index_table_proof(root/'observation-index.sqlite')
    assert remote._json_sha(index_proof) == identity['training_index_proof_sha256']
    assert remote._json_sha(index_proof) == remote._json_sha(provenance['training_index_proof'])
    pins, toolchain_type, collector = remote._checkpoint_toolchain(root, manifest)
    assert pins == PINS and collector['collector'] == 'deepflow'
    binaries = remote._verify_binaries(root, manifest, pins=pins)
    remote._make_binaries_executable(binaries)
    plans = remote._read(root/'plans.json')
    assert remote._json_sha(plans) == identity['plans_sha256']
    remote._atomic_json(out/'original-prefix-proof.json', {
        'identity': manifest['identity'], 'manifest_sha256': before['manifest_sha256'],
        'complete_checkpoint_file_census_sha256': remote._json_sha(before['files']),
        'complete_checkpoint_file_count': len(before['files']), 'full_SQL_proof': index_proof,
        'collector': collector, 'verified_binary_pins': binaries,
        'original_source': source, 'current_qualifier_source': status['source'],
        'same_original_absolute_root': True, 'whole_prefix_ZIP_SHA_and_all_member_CRC_verified': True})
    phases['complete_prefix_restore_checkpoint_SQL_binary_proof'] = (time.monotonic_ns()-phase_start)/1e9
    remote._atomic_json(out/'phase-costs.json', phases)
    ctx = Context(root, 'absent', 8)
    ctx.command_log = out/'qualification-only-commands.jsonl'
    os.environ['PBS_BIN'] = str(root/'toolchain-build/bin')
    temporary = inputs/'reader-tmp'
    temporary.mkdir(); tempfile.tempdir = str(temporary.resolve())
    store = remote._readonly_store(root/'observation-index.sqlite', ObservationStoreV5, immutable_prefix=True)
    phase_start = time.monotonic_ns()
    try:
        reference = remote._frozen_training_admission_reference(root, manifest, before, index_proof, expected, collector)
        assert reference is not None
    finally:
        phases['exact_frozen_admission_reference_source_checks'] = (time.monotonic_ns()-phase_start)/1e9
        remote._atomic_json(out/'phase-costs.json', phases)
    phase_start = time.monotonic_ns()
    try:
        engine = toolchain_type(ctx, 'otel_demo', store, importlib.import_module('systems.otel_demo.experiment_v4'),
                                frozen_training_admission_reference=reference)
    finally:
        phases['current_complete_constructor_and_full_projection_verification'] = (time.monotonic_ns()-phase_start)/1e9
        remote._atomic_json(out/'phase-costs.json', phases)
    shutil.copyfile(engine.root/'frozen-training-admission-reference.json', out/'frozen-training-admission-reference.json')
    remote._atomic_json(out/'phase-costs.json', phases)
    phase_start = time.monotonic_ns(); engine.preflight()
    phases['original_Procrustes_preflight'] = (time.monotonic_ns()-phase_start)/1e9
    phase_start = time.monotonic_ns()
    try:
        engine.prepare_inputs(plans)
    finally:
        phases['current_complete_prepare_inputs'] = (time.monotonic_ns()-phase_start)/1e9
        remote._atomic_json(out/'phase-costs.json', phases)
        for src, target in [('input-preparation-cost.json', 'new-input-preparation-cost.json'),
                            ('inputs/ebpf/network_scope/network-scope-derivation.json', 'network-scope-derivation.json')]:
            if (engine.root/src).is_file(): shutil.copyfile(engine.root/src, out/target)
        for (origin, variant), (path, value) in engine.input_manifests.items():
            shutil.copyfile(path, out/(origin+'-'+variant+'-observations.json'))
    store.close(); store = None
    phase_start = time.monotonic_ns()
    spec = importlib.util.spec_from_file_location('existing_clock_equality', 'scripts/check-fixed-dsb-path-preparation-v5.py')
    equality = importlib.util.module_from_spec(spec); spec.loader.exec_module(equality)
    old_cost = old['toolchain/input-preparation-cost.json']
    new_cost = remote._read(out/'new-input-preparation-cost.json')
    windows = ((old_cost['started_ns'], old_cost['ended_ns']), (new_cost['started_ns'], new_cost['ended_ns']))
    comparisons = []
    for variant, old_manifest in [('raw', raw), ('network_scope', old_network)]:
        current = engine.input_manifests['ebpf', variant][1]
        a, b = old_manifest['stream_exports'][0], current['stream_exports'][0]
        assert len(current['stream_exports']) == 1 and not current['exports']
        assert a['request_index']['bytes'] == b['request_index']['bytes']
        old_index, new_index = baseline_indexes[variant], Path(b['request_index']['path'])
        assert remote._sha(old_index) == a['request_index']['sha256']
        assert new_index.stat().st_size == b['request_index']['bytes'] and remote._sha(new_index) == b['request_index']['sha256']
        normalized = hashlib.sha256(); rows = 0
        with old_index.open('rb') as left_rows, new_index.open('rb') as right_rows:
            for ordinal, (left_line, right_line) in enumerate(itertools.zip_longest(left_rows, right_rows), 1):
                if left_line is None or right_line is None: raise ValueError('request index row count changed')
                left, right = json.loads(left_line), json.loads(right_line)
                for line, value in ((left_line, left), (right_line, right)):
                    assert (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode() == line
                try:
                    equality.strip_clock_pair(left['derived_otlp_proof']['codec_accounting']['index_preparation_cost'],
                        right['derived_otlp_proof']['codec_accounting']['index_preparation_cost'],
                        *windows, clocks, variant+'.codec_accounting.index_preparation_cost')
                    equality.equal(left, right)
                except (ValueError, KeyError) as error:
                    remote._atomic_json(out/'first-index-difference.json', {
                        'view': variant, 'row': ordinal, 'error': repr(error),
                        'changed_fields': [key for key in sorted(set(left)|set(right))
                            if key not in left or key not in right or equality.canonical(left[key]) != equality.canonical(right[key])],
                        'old_nonclock_record_SHA': hashlib.sha256(equality.canonical(left)).hexdigest(),
                        'new_nonclock_record_SHA': hashlib.sha256(equality.canonical(right)).hexdigest()})
                    raise
                normalized.update(equality.canonical(left)+b'\n'); rows += 1
        assert rows == a['requests'] == b['requests'] == 3275
        assert a['shards'] == b['shards'] and len(b['shards']) == 69
        for claim in [*b['shards'], b['runtime_identity_values']]:
            path = Path(claim['path'])
            assert path.stat().st_size == claim['bytes'] and remote._sha(path) == claim['sha256']
        left, right = deepcopy(old_manifest), deepcopy(current)
        for value in (left, right):
            value['stream_exports'][0]['request_index']['sha256'] = 'verified-equivalent-child:'+normalized.hexdigest()
        for name in ('archive_preparation_cost', 'runtime_identity_values'):
            l, r = left['stream_exports'][0][name], right['stream_exports'][0][name]
            if name == 'runtime_identity_values': l, r = l['preparation_cost'], r['preparation_cost']
            equality.strip_clock_pair(l, r, *windows, clocks, variant+'.'+name)
        try:
            equality.equal(left, right)
        except ValueError:
            remote._atomic_json(out/'first-manifest-difference.json', {
                'view': variant, 'old_nonclock_SHA': hashlib.sha256(equality.canonical(left)).hexdigest(),
                'new_nonclock_SHA': hashlib.sha256(equality.canonical(right)).hexdigest()})
            raise
        comparisons.append({'view': variant, 'ordered_nonclock_rows_SHA': normalized.hexdigest(),
                            'rows': rows, 'observations': b['observations'], 'wire_shards': len(b['shards']),
                            'literal_index': b['request_index'],
                            'all_wire_value_and_other_manifest_fields_exact': True})
    phases['all_raw_network_ordered_rows_manifests_wire_value_comparison'] = (time.monotonic_ns()-phase_start)/1e9
    phase_start = time.monotonic_ns()
    _, after = remote._validate_checkpoint(root, expected, allow_toolchain=True)
    assert after == before
    phases['complete_original_checkpoint_final_revalidation'] = (time.monotonic_ns()-phase_start)/1e9
    remote._atomic_json(out/'qualification.json', {
        'schema_version': 'exact-original-prefix-frozen-admission-reference-qualification-v1',
        'source': status['source'], 'original_scientific_source': source, 'original_worker': 41676388484,
        'original_prefix': 13247569257, 'all_original_inputs_after_equal_before': True,
        'full_current_constructor_and_preparation_measured': True,
        'historical_whole_prepare_seconds': (old_cost['ended_ns']-old_cost['started_ns'])/1e9,
        'actual_current_phase_seconds': phases, 'comparisons': comparisons,
        'new_models_Bering_Sheaft_or_application_traffic': False, 'three_main_or_six_hour_headroom_GO': False,
        'cost_boundary': 'Original training admission and source/codec costs counted once; all historical duplicate/failed/CI/model/preparation work, current sourcefetch/API/ZIP/restore/SQL/reference/constructor/projection/preflight/preparation/secondhash/comparison/finalcheck/publication/review/finite retention remain charged. Cross-host/cache/order confounds; SELF CPU excludes children; human effort unknown.'})
    status.update(status='complete', full_current_preparation_measured=True)
except BaseException as error:
    status.update(status='technical_failure', error=repr(error))
    raise
finally:
    if store is not None: store.close()
    if root is not None:
        for src, name in [('toolchain/frozen-training-admission-reference.json', 'frozen-training-admission-reference.json'),
                          ('toolchain/input-preparation-cost.json', 'new-input-preparation-cost.json'),
                          ('toolchain/inputs/ebpf/network_scope/network-scope-derivation.json', 'network-scope-derivation.json')]:
            if (root/src).is_file(): shutil.copyfile(root/src, out/name)
    remote._atomic_json(out/'allowed-cost-clock-pairs.json', [
        {'scope': key[0], 'old_started_ns': key[1], 'old_ended_ns': key[2],
         'new_started_ns': key[3], 'new_ended_ns': key[4], 'occurrences': count}
        for key, count in sorted(clocks.items())])
    status.update(ended_ns=time.time_ns(), SELF_user_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,
        SELF_system_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime,
        SELF_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    remote._atomic_json(out/'status.json', status); remote._atomic_json(out/'phase-costs.json', phases)
    print(json.dumps(status), flush=True)
