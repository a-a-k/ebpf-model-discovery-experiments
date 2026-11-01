"""One Actions-only, unprofiled full7 preparation comparison; no model rerun."""
from collections import Counter
from copy import deepcopy
import hashlib
import importlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

from ebpf_discovery.artifact_transport_v4 import unpack
from ebpf_discovery.remote_toolchain_v4 import (
    _checkpoint_toolchain, _index_table_proof, _json_sha, _readonly_store,
    _safe_extract, _sha, _validate_checkpoint, _verify_binaries,
)
from ebpf_discovery.runtime import Context, write_json
from ebpf_discovery.store_v5 import ObservationStoreV5


REPOSITORY = 'a-a-k/ebpf-model-discovery-experiments'
EXPECTED = {
    'run_id': '41164824120', 'system': 'deathstarbench', 'mode': 'full', 'seed': '7',
    'commit': '0c98bf4520e863ab021b60d00517ee2aa49ab38e',
    'manifest_sha256': 'a6c521efe353685b267a64e6ba034c1f69ce79a7e623dc9c98646863f6f2a347',
    'plans_sha256': 'fa6e700f5553873cfc9c24ce4509e6ab45acbac2739abd83e9c8e236d9b03070',
    'training_index_proof_sha256': '8a7fcacb6207a9a58066e0754438cf3fd316112b675044b684e7ba008b663877',
}
CORE_BLOBS = {
    'src/ebpf_discovery/raw_v4.py': '8d964d7dc969a922f9ab1701f371eed5ea190321',
    'src/ebpf_discovery/remote_toolchain_v4.py': '627d0fc8d4dc466c7bf2ec3d7b403a8616e0fe89',
    'src/ebpf_discovery/store_v5.py': '6569299a8a0a31f2ded3781433045ba303ae097a',
    'src/ebpf_discovery/toolchain_v4.py': 'b8b4c635952b5d0e72d436951df2463b38f28105',
}
ARTIFACTS = (
    (13047984145, 3356747245, 'a36d286a30830b93e2958f22da6f6e5ad735ad4f32bfe1dcc6b5a0a2abe1ddac',
     41164824120, EXPECTED['commit'], 'training-v4-deathstarbench-full-7-41164824120', 'training-prefix'),
    (13053549827, 1074613934, '8120d163a0c995ce20e562ac48d2c76070a425de106938749b9706d983761202',
     41219370499, '13c017bf72a86a6853f93a5b8f503de199bf7865',
     'toolchain-v4-deathstarbench-full-7-41219370499', 'old-worker'),
)


def canonical(value):
    # Python equality would conceal bool/int changes; lists keep their order.
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def equal(left, right):
    if canonical(left) != canonical(right):
        raise ValueError('non-clock preparation content changed')


def clock_pair(cost, window):
    pair = tuple(cost[key] for key in ('started_ns', 'ended_ns'))
    if (any(type(value) is not int for value in pair)
            or not 0 < window[0] <= pair[0] <= pair[1] <= window[1]):
        raise ValueError('preparation clock is not ordered inside its full preparation window')
    return pair


def strip_clock_pair(left, right, old_window, new_window, clocks, scope):
    old = clock_pair(left, old_window)
    new = clock_pair(right, new_window)
    clocks[(scope, *old, *new)] += 1
    for value in (left, right):
        del value['started_ns'], value['ended_ns']
    # Counts and storage facts within the SAME cost dictionary remain strict.
    equal(left, right)


def compare_index(old_path, new_path, windows, clocks):
    if old_path.stat().st_size != new_path.stat().st_size:
        raise ValueError('request index bytes changed')
    digest = hashlib.sha256()
    count = 0
    with old_path.open(encoding='utf-8') as old, new_path.open(encoding='utf-8') as new:
        for old_line, new_line in itertools.zip_longest(old, new):
            if old_line is None or new_line is None:
                raise ValueError('request index row count changed')
            left, right = json.loads(old_line), json.loads(new_line)
            strip_clock_pair(
                left['derived_otlp_proof']['codec_accounting']['index_preparation_cost'],
                right['derived_otlp_proof']['codec_accounting']['index_preparation_cost'],
                *windows, clocks, 'codec_accounting.index_preparation_cost')
            equal(left, right)
            digest.update(canonical(left) + b'\n')
            count += 1
    return {'rows': count, 'ordered_nonclock_rows_sha256': digest.hexdigest()}


def bind_reference(left, right, campaign, old_root, new_root, proven):
    equal(left['path'], right['path'])
    relative = Path(left['path']).relative_to(campaign / 'toolchain').as_posix()
    if relative not in proven:
        raise ValueError('changed reference lacks a completed child equivalence proof')
    for value, root in ((left, old_root), (right, new_root)):
        physical = root / relative
        if value['sha256'] != _sha(physical):
            raise ValueError('reference SHA does not bind its actual child file')
        if 'bytes' in value and value['bytes'] != physical.stat().st_size:
            raise ValueError('reference bytes do not bind its actual child file')
        value['sha256'] = 'bound-equivalent-child'
        if 'bytes' in value:
            value['bytes'] = 'bound-equivalent-child'


def compare_manifest(left, right, windows, clocks, campaign, old_root, new_root, proven):
    left, right = deepcopy(left), deepcopy(right)
    if len(left['stream_exports']) != len(right['stream_exports']):
        raise ValueError('stream count changed')
    for old, new in zip(left['stream_exports'], right['stream_exports']):
        strip_clock_pair(old['archive_preparation_cost'], new['archive_preparation_cost'],
                         *windows, clocks, 'stream.archive_preparation_cost')
        strip_clock_pair(old['runtime_identity_values']['preparation_cost'],
                         new['runtime_identity_values']['preparation_cost'],
                         *windows, clocks, 'stream.runtime_identity_values.preparation_cost')
        bind_reference(old['request_index'], new['request_index'],
                       campaign, old_root, new_root, proven)
    for field in ('source_manifests', 'ordered_request_group_manifests'):
        if (field in left) != (field in right):
            raise ValueError('combined child reference field changed')
        if field in left:
            if len(left[field]) != len(right[field]):
                raise ValueError('combined child reference count changed')
            for old, new in zip(left[field], right[field]):
                bind_reference(old, new, campaign, old_root, new_root, proven)
    equal(left, right)


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Full saved-prefix processing is Actions-only')
    import resource
    output = Path('work/preparation-equivalence')
    output.mkdir(parents=True, exist_ok=True)
    campaign = Path('work/campaign').resolve()
    status = {'status': 'source_check', 'started_ns': time.time_ns(),
              'input_identity': EXPECTED, 'new_application_traffic': False,
              'new_model_execution_or_scoring': False, 'profiled': False}
    write_json(output/'status.json', status)
    try:
        changed = subprocess.check_output([
            'git', 'diff', '--name-only', EXPECTED['commit'], 'HEAD', '--', 'src', 'systems'],
            text=True).splitlines()
        equal(sorted(changed), sorted(CORE_BLOBS))
        for path, blob in CORE_BLOBS.items():
            equal(subprocess.check_output(['git', 'rev-parse', 'HEAD:'+path], text=True).strip(), blob)
        status['implementation_sha'] = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], text=True).strip()
        status['changed_core_blobs'] = CORE_BLOBS
        for artifact_id, size, sha, run_id, head, name, local in ARTIFACTS:
            api = json.loads(subprocess.check_output([
                'gh', 'api', f'repos/{REPOSITORY}/actions/artifacts/{artifact_id}']))
            run = json.loads(subprocess.check_output([
                'gh', 'api', f'repos/{REPOSITORY}/actions/runs/{run_id}']))
            write_json(output/(local+'-artifact-api.json'), api)
            write_json(output/(local+'-run-api.json'), run)
            equal([api['id'], api['size_in_bytes'], api['digest'], api['expired'], api['name'],
                   api['workflow_run']['id'], api['workflow_run']['head_sha'], run['id'], run['head_sha']],
                  [artifact_id, size, 'sha256:'+sha, False, name, run_id, head, run_id, head])
            if local == 'old-worker':
                equal([run['status'], run['conclusion']], ['completed', 'success'])
            if shutil.disk_usage('work').free < size + 64*1024**2:
                raise RuntimeError('insufficient disk before fixed artifact download')
            started = time.time_ns()
            archive = Path('work')/(local+'.zip')
            with archive.open('xb') as stream:
                subprocess.run(['gh', 'api', f'repos/{REPOSITORY}/actions/artifacts/{artifact_id}/zip'],
                               stdout=stream, check=True)
            equal([archive.stat().st_size, _sha(archive)], [size, sha])
            write_json(output/(local+'-download.json'), {
                'started_ns': started, 'ended_ns': time.time_ns(), 'bytes': size, 'sha256': sha})
        # Enough room for full old output, restored prefix and all regenerated inputs.
        with zipfile.ZipFile('work/training-prefix.zip') as archive:
            prefix_bytes = sum(member.file_size for member in archive.infolist())
        required = prefix_bytes + 2*14430995917 + 1024**3
        free = shutil.disk_usage('work').free
        write_json(output/'disk-before-restore.json', {'free_bytes': free, 'required_bytes': required,
                   'basis': 'full prefix plus twice actual old worker tree plus 1 GiB'})
        if free < required:
            raise RuntimeError('insufficient disk before immutable full comparison')
        _safe_extract(Path('work/old-worker.zip'), Path('work/old-worker-package'))
        proof = unpack(Path('work/old-worker-package'), Path('work/old-worker'), kind='worker')
        write_json(output/'old-worker-unpack.json', proof)
        old_payload = Path('work/old-worker')
        old_root = old_payload/'toolchain'
        old_status = json.loads((old_payload/'worker-status.json').read_text())
        equal([old_status['status'], old_status['checkpoint_unchanged']], ['complete', True])
        for key, value in EXPECTED.items():
            equal(old_status['identity'][key], value)
        shutil.copyfile('work/old-worker-package/payload.manifest.jsonl', output/'old-payload.manifest.jsonl')
        old_files = {}
        with (output/'old-payload.manifest.jsonl').open() as stream:
            for line in stream:
                row = json.loads(line)
                if row['type'] == 'file' and row['path'].startswith('toolchain/'):
                    old_files[row['path'][len('toolchain/'):]] = row
        _safe_extract(Path('work/training-prefix.zip'), campaign)
        manifest, before = _validate_checkpoint(campaign, EXPECTED)
        before_index = _index_table_proof(campaign/'observation-index.sqlite')
        equal(_json_sha(before_index), EXPECTED['training_index_proof_sha256'])
        pins, toolchain_type, collector = _checkpoint_toolchain(campaign, manifest)
        equal(collector['collector'], 'deepflow')
        binary_proof = _verify_binaries(campaign, manifest, pins=pins)
        plans = json.loads((campaign/'plans.json').read_text())
        equal(_json_sha(plans), EXPECTED['plans_sha256'])
        old_cost = json.loads((old_root/'input-preparation-cost.json').read_text())
        equal(old_cost['completed'], True)
        old_window = clock_pair(old_cost, (1, time.time_ns()))
        store = _readonly_store(campaign/'observation-index.sqlite', ObservationStoreV5,
                                immutable_prefix=True)
        status['status'] = 'preparing_inputs'
        write_json(output/'status.json', status)
        try:
            ctx = Context(campaign, 'full', 7)
            ctx.command_log = output/'unexpected-worker-commands.jsonl'
            declaration = importlib.import_module('systems.deathstarbench.experiment_v4')
            toolchain = toolchain_type(ctx, 'deathstarbench', store, declaration)
            toolchain.prepare_inputs(plans)
        finally:
            store.close()
            after_manifest, after = _validate_checkpoint(campaign, EXPECTED, allow_toolchain=True)
            equal(after_manifest, manifest)
            equal(after, before)
            equal(_index_table_proof(campaign/'observation-index.sqlite'), before_index)
        if ctx.command_log.exists():
            raise ValueError('offline preparation unexpectedly executed external commands')
        new_root = campaign/'toolchain'
        new_cost = json.loads((new_root/'input-preparation-cost.json').read_text())
        equal(new_cost['completed'], True)
        new_window = clock_pair(new_cost, (1, time.time_ns()))
        write_json(output/'old-input-preparation-cost.json', old_cost)
        write_json(output/'new-input-preparation-cost.json', new_cost)
        # Every physical input, including exact native exports, shards and values.
        old_inputs = {path for path in old_files if path.startswith('inputs/')}
        new_inputs = {path.relative_to(new_root).as_posix()
                      for path in (new_root/'inputs').rglob('*') if path.is_file()}
        equal(sorted(old_inputs), sorted(new_inputs))
        manifests = {f'inputs/{source}/{view}/observations.json'
                     for source in ('ebpf', 'native', 'combined') for view in ('raw', 'network_scope')}
        indexes = {f'inputs/ebpf/{view}/exports/ebpf-request-index.jsonl'
                   for view in ('raw', 'network_scope')}
        if not manifests | indexes <= old_inputs:
            raise ValueError('fixed full7 lacks the expected six manifests and two indexes')
        exact = []
        for relative in sorted(old_inputs - manifests - indexes):
            path, old = new_root/relative, old_files[relative]
            equal([path.stat().st_size, _sha(path)], [old['bytes'], old['sha256']])
            exact.append({'path': relative, 'bytes': old['bytes'], 'sha256': old['sha256']})
        clocks = Counter()
        proven = set()
        index_proofs = {}
        for relative in sorted(indexes):
            index_proofs[relative] = compare_index(old_root/relative, new_root/relative,
                                                  (old_window, new_window), clocks)
            proven.add(relative)
        manifest_proofs = []
        for source in ('ebpf', 'native', 'combined'):
            for view in ('raw', 'network_scope'):
                relative = f'inputs/{source}/{view}/observations.json'
                compare_manifest(json.loads((old_root/relative).read_text()),
                                 json.loads((new_root/relative).read_text()),
                                 (old_window, new_window), clocks,
                                 campaign, old_root, new_root, proven)
                proven.add(relative)
                manifest_proofs.append({'path': relative, 'old_sha256': _sha(old_root/relative),
                                        'new_sha256': _sha(new_root/relative)})
        entries = []
        for (source, operation), evidence in sorted(toolchain.entry_evidence.items()):
            for view in ('raw', 'network_scope'):
                relative = f'{source}/{view}/{operation}/entry-evidence.json'
                serialized = output/'entry-evidence'/relative
                write_json(serialized, evidence)
                old = old_files[relative]
                equal([serialized.stat().st_size, _sha(serialized)], [old['bytes'], old['sha256']])
                entries.append({'path': relative, 'bytes': old['bytes'], 'sha256': old['sha256']})
        equal(len(entries), 18)
        write_json(output/'equivalence.json', {
            'all_inputs_same_file_census': True, 'exact_byte_inputs': exact,
            'request_indexes': index_proofs, 'manifests': manifest_proofs, 'entry_evidence': entries,
            'allowed_clock_pairs': [{'scope': key[0], 'old_started_ns': key[1], 'old_ended_ns': key[2],
                                    'new_started_ns': key[3], 'new_ended_ns': key[4], 'occurrences': count}
                                   for key, count in sorted(clocks.items())],
            'checkpoint_before_after_identical': True, 'index_before_after_identical': True,
            'binary_proofs': binary_proof, 'downstream_code_unchanged': True,
            'old_models_and_sheaft_outputs_preserved_in_original_artifact': True,
            'new_models_or_sheaft_executed': False,
            'same_observational_inputs_and_entry_proofs_allow_reusing_actual_old_tool_results': True})
        status.update(status='complete', input_equivalence_proven=True,
                      old_preparation_seconds=(old_window[1]-old_window[0])/1e9,
                      new_preparation_seconds=(new_window[1]-new_window[0])/1e9)
    except BaseException as error:
        status.update(status='technical_failure', error=repr(error))
        raise
    finally:
        status.update(ended_ns=time.time_ns(), max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      user_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,
                      system_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime)
        write_json(output/'status.json', status)
        print(json.dumps(status), flush=True)


if __name__ == '__main__':
    main()
