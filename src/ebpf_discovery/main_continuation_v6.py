"""Registered MAIN captures with new uniform processing and isolated validation."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import time
from types import SimpleNamespace

from . import block_v6 as b, isolated_arm_v6 as i
from .capture_checks_v6 import verify_capture
from .plan_v6 import COLLECTORS, block
from .runtime import write_json
from .validation_v6 import require_block_freeze, require_forecast

ORIGINAL_SOURCE = '5e622ed58c340e2cfe85c3c287ba90bc9c610190'
PARENTS = {f'docs/v6-main-parent-OTel-partial{rep}-20261108.json': ('partial', rep, run)
           for rep, run in ((9, 42401605258), (10, 42401608466), (11, 42401611728))}
PARENTS['docs/v6-main-parent-OTel-absent10-20261108.json'] = ('absent', 10, 42401597551)
PROFILE = {'bering_child_go_environment': {'GOGC': '25'},
           'additional_model_swap_file_bytes': 16 * 1024**3}


def parent(path, sha):
    if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_REPOSITORY') != 'a-a-k/ebpf-model-discovery-experiments':
        raise RuntimeError('registered MAIN continuation is repository Actions only')
    if path not in PARENTS or not re.fullmatch('[0-9a-f]{64}', sha):
        raise ValueError('only four literal reviewed MAIN parents are allowed')
    full = b.repo() / path
    if full.is_symlink() or b.sha(full) != sha:
        raise ValueError('registered MAIN parent bytes differ')
    value = b.read(full)
    mode, rep, run = PARENTS[path]
    plan = value['parent_plan']
    expected = block('otel_demo', mode, rep)
    if (value.get('schema') != 'v6-main-closed-input-parent-v1' or value.get('study') != 'clean-restart-v6'
            or (value.get('system'), value.get('mode'), value.get('repetition'),
                value.get('stage'), value.get('smoke'), value.get('parent_run_id'), value.get('parent_source'))
            != ('otel_demo', mode, rep, 'main', False, run, ORIGINAL_SOURCE)
            or value.get('allocation_regime') != i.REGIME
            or any(value.get(k) is not True for k in ('root_parent_input_GO', 'independent_parent_input_GO',
                   'root_original_execution_GO', 'independent_original_execution_GO'))
            or value.get('processing_profile') != PROFILE
            or type(value.get('registered_before_processing_ns')) is not int
            or value['registered_before_processing_ns'] <= 0
            or value.get('implementation_sha256') != b.implementation_hashes()
            or any(plan.get(k) != v for k, v in expected.items())
            or (plan.get('stage'), plan.get('smoke'), plan.get('run_id'), plan.get('source'), plan.get('allocation_regime'))
            != ('main', False, run, ORIGINAL_SOURCE, i.REGIME)
            or set(value.get('training_artifacts', {})) != set(COLLECTORS)
            or set(value.get('closed_input_sha256_by_collector', {})) != set(COLLECTORS)
            or set(value.get('capture_case_by_collector', {})) != set(COLLECTORS)
            or len({a['id'] for a in (value['shared_artifact'], *value['training_artifacts'].values())}) != 5):
        raise ValueError('exact source/input ORIGINAL approval for this MAIN parent is required')
    plan_bytes = (json.dumps(plan, indent=2, ensure_ascii=False) + '\n').encode()
    if __import__('hashlib').sha256(plan_bytes).hexdigest() != value['parent_plan_sha256']:
        raise ValueError('original MAIN plan representation differs')
    return {**value, '_record_path': path, '_record_sha256': sha}


def original_artifact(value, claim):
    if value != parent(value['_record_path'], value['_record_sha256']):
        raise ValueError('MAIN parent changed after loading')
    matches = [a for a in (value['shared_artifact'], *value['training_artifacts'].values())
               if (a['id'], a['name'], a['digest']) == (claim['id'], claim['name'], claim['digest'])]
    if len(matches) != 1:
        raise ValueError('publication is outside the five exact original inputs')
    expected = matches[0]
    actual = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{expected['id']}")
    if (actual.get('expired') is not False
            or any(actual.get(k) != expected[k] for k in ('id', 'name', 'digest', 'size_in_bytes'))
            or (actual.get('workflow_run') or {}).get('id') != value['parent_run_id']
            or (actual.get('workflow_run') or {}).get('head_sha') != ORIGINAL_SOURCE):
        raise ValueError('original MAIN publication identity differs')
    return actual


def preflight(args, value, root):
    run = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{value['parent_run_id']}")
    jobs = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{value['parent_run_id']}/jobs?per_page=100")['jobs']
    if (run.get('head_sha') != ORIGINAL_SOURCE or run.get('path') != '.github/workflows/series-isolated-v6.yml'
            or run.get('event') != 'workflow_dispatch'
            or any(not any(j['name'] == f'training{slot}' and j['conclusion'] == 'success' for j in jobs) for slot in range(4))
            or any(j.get('steps') for j in jobs if j['name'].startswith('validation'))):
        raise ValueError('parent must have four actual successful captures and no executed targets')
    apis = [original_artifact(value, i.claim({'id': a['id'], 'name': a['name'], 'digest': a['digest']}))
            for a in (value['shared_artifact'], *value['training_artifacts'].values())]
    write_json(root / 'main-continuation-preflight.json', {'run': run, 'jobs': jobs, 'original_artifacts': apis})
    i.output(repetition=value['repetition'])


def restore_training(args, value, root):
    collector = value['parent_plan']['arm_orders']['training'][args.slot]
    a = value['training_artifacts'][collector]
    folder = root / 'capture-input'
    receipt = i.fetch({'id': a['id'], 'name': a['name'], 'digest': a['digest']}, folder,
                      ('capture.tar.gz', 'capture.tar.gz.json'), original_parent=value)
    package = b.read(folder / 'capture.tar.gz.json')
    if (b.sha(folder / 'capture.tar.gz.json') != value['capture_inventory_sha256_by_collector'][collector]
            or package['sha256'] != value['capture_archive_sha256_by_collector'][collector]
            or package['case'] != value['capture_case_by_collector'][collector]
            or package['block_plan_sha256'] != value['parent_plan_sha256']):
        raise ValueError('original MAIN capture package differs from its sealed parent')
    target = root / 'case'
    target.mkdir()
    guard = b.unpack(folder / 'capture.tar.gz', target, package['sha256'], guard_root=root, expected_inventory=package)
    if b.inventory(target) != package['files'] or b.read(target / 'status.json') != package['case']:
        raise ValueError('every original capture file/byte/SHA/mode must match')
    closed = verify_capture(target, 'training')
    if (closed['status'] != value['capture_case_by_collector'][collector]
            or b.sha(target / 'closed-input.json') != value['closed_input_sha256_by_collector'][collector]):
        raise ValueError('original closed MAIN runtime evidence differs')
    jobs = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}/jobs?per_page=100")['jobs']
    matches = [j for j in jobs if j['name'] == f'model{args.slot}' and j.get('status') == 'in_progress'
               and j.get('head_sha') == os.environ['GITHUB_SHA']
               and j.get('run_attempt') == int(os.environ['GITHUB_RUN_ATTEMPT'])]
    if len(matches) != 1:
        raise ValueError('exact actual current model job is required')
    i.release_delivery(receipt)
    i.release_package(folder / 'capture.tar.gz', package)
    write_json(target / 'v6-training-publication-restored.json', {**receipt,
        'main_continuation_parent': {'path': args.parent_record, 'sha256': args.parent_sha256},
        'original_capture_identity': closed['status'], 'restored_all_bytes_SHA_modes': True,
        'training_closed_input_sha256': value['closed_input_sha256_by_collector'][collector],
        'archive_sha256': package['sha256'], 'inventory_sha256': b.sha(folder / 'capture.tar.gz.json'),
        'preextract_actual_disk_guard': guard,
        'model_producing_job': {'job': os.environ['GITHUB_JOB'], 'display_name': f'model{args.slot}',
            'job_id': matches[0]['id'], 'slot': args.slot, 'attempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
            'runner_boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(), 'restored_ns': time.time_ns()}})
    i.output(collector=collector, artifact_name=i.name('model', args.slot))


def import_shared(root, args):
    value = parent(args.main_parent_record, args.main_parent_sha256)
    a = value['shared_artifact']
    folder = root / 'shared-input'
    receipt = i.fetch({'id': a['id'], 'name': a['name'], 'digest': a['digest']}, folder,
                      ('shared.tar.gz', 'shared.tar.gz.json', 'shared-seal.json', 'block-plan.json'), original_parent=value)
    old, seal, package = (b.read(folder / n) for n in ('block-plan.json', 'shared-seal.json', 'shared.tar.gz.json'))
    if (old != value['parent_plan'] or b.sha(folder / 'block-plan.json') != value['parent_plan_sha256']
            or seal['block_plan_sha256'] != value['parent_plan_sha256']
            or package['sha256'] != value['shared_sha256'] or seal['shared_sha256'] != value['shared_sha256']
            or any(old[k] != value[k] or seal[k] != value[k] for k in ('golden_sha256', 'blueprint_sha256'))):
        raise ValueError('original common plan/archive/seals differ')
    guard = b.unpack(folder / 'shared.tar.gz', root, package['sha256'], guard_root=root, expected_inventory=package)
    for relative, expected in package['files'].items():
        p = root / relative
        if (p.stat().st_size, b.sha(p), stat.S_IMODE(p.stat().st_mode)) != (expected['bytes'], expected['sha256'], expected['mode']):
            raise ValueError('complete original shared image/config inventory differs')
    if (b.sha(root / 'blueprint/blueprint.json'), b.sha(root / 'vms/golden/manifest.json')) != (
            value['blueprint_sha256'], value['golden_sha256']):
        raise ValueError('actual restored common manifests differ')
    shutil.copyfile(folder / 'block-plan.json', root / 'original-block-plan.json')
    plan = {**old, **i.execution(), 'main_closed_input_parent': {
        'path': args.main_parent_record, 'sha256': args.main_parent_sha256}}
    write_json(root / 'block-plan.json', plan)
    i.release_delivery(receipt)
    i.release_package(folder / 'shared.tar.gz', package)
    write_json(root / 'isolated-shared-import.json', {**receipt, 'preextract_actual_disk_guard': guard,
        'original_plan_sha256': value['parent_plan_sha256'], 'block_plan_sha256': b.sha(root / 'block-plan.json'),
        'main_closed_input_parent': plan['main_closed_input_parent']})
    return plan


def import_models(root, plan):
    ref = plan['main_closed_input_parent']
    value = parent(ref['path'], ref['sha256'])
    artifacts, page = [], 1
    while True:
        rows = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}/artifacts?per_page=100&page={page}")['artifacts']
        artifacts.extend(rows)
        if len(rows) < 100:
            break
        page += 1
    allocation = {'regime': i.REGIME, 'plan': plan, 'block_plan_sha256': b.sha(root / 'block-plan.json'),
                  'main_closed_input_parent': ref, 'models': {}}
    for collector in COLLECTORS:
        slot = plan['arm_orders']['training'].index(collector)
        candidates = [a for a in artifacts if re.fullmatch(
            f"v6-isolated-model-slot{slot}-{os.environ['GITHUB_RUN_ID']}-attempt[1-9][0-9]*", a['name'])]
        if len(candidates) != 1:
            raise ValueError('one unambiguous current model publication per slot required; no result-based selection')
        a = candidates[0]
        folder, target = root / 'model-input' / collector, root / 'models' / collector
        receipt = i.fetch({'id': a['id'], 'name': a['name'], 'digest': a['digest']}, folder,
                          ('model.tar.gz', 'model.tar.gz.json'))
        package = b.read(folder / 'model.tar.gz.json')
        target.mkdir(parents=True)
        guard = b.unpack(folder / 'model.tar.gz', target, package['sha256'], guard_root=root, expected_inventory=package)
        if b.inventory(target) != package['files']:
            raise ValueError('complete current portable model inventory differs')
        frozen = require_forecast(target, 'otel_demo', value['mode'], value['repetition'], collector, stage='main', smoke=False)
        restored = b.read(target / 'v6-training-publication-restored.json')
        allocation['models'][collector] = {'case': frozen['case'], 'forecast_sha256': b.sha(target / 'forecast-saved.json'),
            'training_artifact_API': restored['artifact_API'], 'model_artifact_API': receipt['artifact_API']}
        i.release_delivery(receipt)
        i.release_package(folder / 'model.tar.gz', package)
        write_json(folder / 'verified-import.json', {**receipt, 'preextract_actual_disk_guard': guard})
    barrier = require_block_freeze([root / 'models' / c for c in COLLECTORS], allocation=allocation)
    write_json(root / 'isolated-allocation.json', allocation)
    write_json(root / 'block-all-forecasts-frozen.json', barrier)
    return allocation, barrier


def verify_allocation(roots, saved, allocation):
    ref = allocation['main_closed_input_parent']
    value = parent(ref['path'], ref['sha256'])
    old = value['parent_plan']
    plan = {**old, **i.execution(), 'main_closed_input_parent': ref}
    plan_sha = __import__('hashlib').sha256((json.dumps(plan, indent=2, ensure_ascii=False) + '\n').encode()).hexdigest()
    if (allocation.get('regime') != i.REGIME or allocation.get('plan') != plan
            or allocation.get('block_plan_sha256') != plan_sha or set(allocation['models']) != set(COLLECTORS)
            or not all(s['case'].get('runner_boot_id') and s['processing_execution'].get('runner_boot_id') for s in saved)
            or len({s['case'].get('runner_boot_id') for s in saved}) != 4
            or len({s['processing_execution'].get('runner_boot_id') for s in saved}) != 4):
        raise ValueError('registered old captures and four current isolated model hosts required')
    if len({row['model_artifact_API']['id'] for row in allocation['models'].values()}) != 4:
        raise ValueError('four distinct current model publications required')
    for root, forecast in zip(roots, saved):
        root = Path(root)
        case, processing = forecast['case'], forecast['processing_execution']
        c = case['collector']
        slot, row = old['arm_orders']['training'].index(c), allocation['models'][c]
        restored, reference = b.read(root / 'v6-training-publication-restored.json'), b.read(root / 'v6-block-reference.json')
        model_job = restored['model_producing_job']
        actual_job = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/jobs/{model_job['job_id']}")
        training_api = row['training_artifact_API']
        expected_api = value['training_artifacts'][c]
        if (case != value['capture_case_by_collector'][c] or row['case'] != case
                or row['forecast_sha256'] != b.sha(root / 'forecast-saved.json')
                or forecast['training_closed_input_sha256'] != value['closed_input_sha256_by_collector'][c]
                or restored['training_closed_input_sha256'] != forecast['training_closed_input_sha256']
                or restored['original_capture_identity'] != case or restored['main_continuation_parent'] != ref
                or training_api != restored['artifact_API']
                or any(training_api[k] != expected_api[k] for k in ('id', 'name', 'digest', 'size_in_bytes'))
                or (training_api['workflow_run']['id'], training_api['workflow_run']['head_sha']) != (value['parent_run_id'], ORIGINAL_SOURCE)
                or (reference['run_id'], reference['source'], reference['block_plan_sha256'], reference['training_slot']) !=
                    (value['parent_run_id'], ORIGINAL_SOURCE, value['parent_plan_sha256'], slot)
                or (reference['blueprint_sha256'], reference['golden_sha256'], reference['allocation_regime']) !=
                    (value['blueprint_sha256'], value['golden_sha256'], i.REGIME)
                or reference['capture_host_resources_sha256'] != b.sha(root / 'capture-host-resources.json')
                or (str(processing['run_id']), processing['commit']) != (str(i.execution()['run_id']), i.execution()['source'])
                or b.read(root / 'processing-execution.json') != processing
                or processing.get('bering_child_go_environment') != PROFILE['bering_child_go_environment']
                or processing.get('additional_model_swap_file_bytes') != PROFILE['additional_model_swap_file_bytes']
                or not value['registered_before_processing_ns'] < model_job['restored_ns'] <= processing['started_ns'] < forecast['saved_ns']
                or (model_job['job'], model_job['display_name'], model_job['slot'], model_job['runner_boot_id']) !=
                    ('model', f'model{slot}', slot, processing['runner_boot_id'])
                or (actual_job['run_id'], actual_job['head_sha'], actual_job['run_attempt'], actual_job['name'], actual_job['conclusion']) !=
                    (i.execution()['run_id'], i.execution()['source'], model_job['attempt'], f'model{slot}', 'success')
                or row['model_artifact_API']['name'] !=
                    f"v6-isolated-model-slot{slot}-{i.execution()['run_id']}-attempt{model_job['attempt']}"):
            raise ValueError('exact old MAIN input/current model job/closure/source/freeze binding differs')
        b.artifact_identity(row['model_artifact_API'], row['model_artifact_API']['name'],
                            row['model_artifact_API']['id'], row['model_artifact_API']['digest'])
        swap = b.read(root / 'model-swap-resources.json')
        if swap['status'] != 'active' or swap['additional_swap_file_bytes'] != PROFILE['additional_model_swap_file_bytes']:
            raise ValueError('same actual model-only memory profile required')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('preflight', 'restore-training', 'validation', 'release'))
    parser.add_argument('--parent-record', required=True, choices=sorted(PARENTS))
    parser.add_argument('--parent-sha256', required=True)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--slot', type=int, choices=range(4))
    parser.add_argument('--artifact-id', type=int)
    parser.add_argument('--artifact-digest')
    args = parser.parse_args()
    value, root = parent(args.parent_record, args.parent_sha256), b.owned_root(args.root)
    started, cpu = time.time_ns(), os.times()
    cost = {'command': args.command, 'started_ns': started, 'execution': i.execution(),
            'parent_record': args.parent_record, 'parent_sha256': args.parent_sha256, 'slot': args.slot, 'status': 'started'}
    try:
        if args.command == 'preflight':
            preflight(args, value, root)
        elif args.command == 'restore-training':
            if args.slot is None:
                parser.error('model restore needs its exact slot')
            restore_training(args, value, root)
        else:
            if args.slot is None:
                parser.error('isolated target needs its exact slot')
            args.system, args.mode, args.repetition, args.stage = 'otel_demo', value['mode'], value['repetition'], 'main'
            args.capture_phase = 'validation'
            args.main_parent_record, args.main_parent_sha256 = args.parent_record, args.parent_sha256
            if args.command == 'validation':
                i.capture(args, root)
            else:
                if not args.artifact_id or not args.artifact_digest:
                    parser.error('release needs its exact published artifact')
                i.release(args, root)
        cost['status'] = 'complete'
    except BaseException as error:
        cost.update(status='failed', error=repr(error))
        raise
    finally:
        end = os.times()
        cost.update(ended_ns=time.time_ns(), CPU_seconds={k: getattr(end, k) - getattr(cpu, k)
                    for k in ('user', 'system', 'children_user', 'children_system')})
        write_json(root / f'main-continuation-{args.command}-status.json', cost)
        with (root / 'main-continuation-cost.jsonl').open('a', encoding='utf8') as stream:
            stream.write(json.dumps(cost) + '\n')


if __name__ == '__main__':
    main()
