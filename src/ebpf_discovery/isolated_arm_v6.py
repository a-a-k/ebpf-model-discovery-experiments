"""Capture, model import and validation on isolated workers."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

from . import block_v6 as b
from .plan_v6 import COLLECTORS, MODES, REPETITIONS, SYSTEMS, block
from .runtime import write_json
from .study_v6 import Case
from .validation_v6 import evaluate, require_block_freeze, require_forecast

REGIME = 'randomized-between-host-arms-v6'
STAGED_BLOCKS = ['petclinic-absent-9', 'otel_demo-absent-9', 'deathstarbench-absent-9',
                 'deathstarbench-full-9']
STAGED_APPROVAL = 'docs/v6-isolated-scientific-pilots-original-execution-GO-20261106.json'
STAGED_DESIGN_SHA256 = 'e165146a357451831da40319c2581aba3a278b2f54c7b7b39cb5e3bd7ee1a400'
DSB_RETRY_DESIGN_SHA256 = 'f1b20784d65ec028555c37ca02426de48db6099106e40a72499a5a6d9ba19c0b'
PCDSB_BLOCKS = [
    'petclinic-absent-10', 'petclinic-absent-11',
    'petclinic-partial-9', 'petclinic-partial-10', 'petclinic-partial-11',
    'petclinic-full-10', 'petclinic-full-11',
    'deathstarbench-absent-10', 'deathstarbench-absent-11',
    'deathstarbench-partial-9', 'deathstarbench-partial-10', 'deathstarbench-partial-11',
    'deathstarbench-full-10', 'deathstarbench-full-11']
PCDSB_APPROVAL = 'docs/v6-PCDSB-remaining56-original-execution-GO-20261107.json'
PCDSB_DESIGN_SHA256 = 'e2f8d59fd53a7e77904df62b92556040a774ebfc2357683c7340f16d8bef6755'
OTEL_STAGED_BLOCKS = ['otel_demo-absent-10', 'otel_demo-absent-11',
                      'otel_demo-partial-9', 'otel_demo-partial-10', 'otel_demo-partial-11']
OTEL_STAGED_APPROVAL = 'docs/v6-OTel-remaining20-original-execution-GO-20261107.json'
OTEL_STAGED_DESIGN_SHA256 = '8d6a18af535bb05ae3bfda3aa26b7f5927cfd6f7475d9a6f07cbe8b1991b0970'
OTEL_FINAL_BLOCKS = ['otel_demo-full-10', 'otel_demo-full-11']
OTEL_FINAL_APPROVAL = 'docs/v6-OTel-final8-original-execution-GO-20261107.json'
OTEL_FINAL_DESIGN_SHA256 = 'c028a347ac51a03fce4a5f817765c0b4ee2662abb37a9f2aebd1327462b3c143'
DSB_ORIGINAL = {'run_id': 42267262342, 'source': '9d6414e8824331d368d1732a15200cdad691350b',
    'retained_training_artifacts': [
        {'collector': 'none', 'id': 13536919189, 'bytes': 4388197895,
         'sha256': '355c2eca79c63a80d5dd7ad2cc4b27f654a1074688a4ebf25fa6376046bfe21e'},
        {'collector': 'obi', 'id': 13543313932, 'bytes': 4422519367,
         'sha256': 'a65cd16116a5715415e83c36d8a106779af8d2b311a29e8b932ca8a4a9786c52'},
        {'collector': 'coroot', 'id': 13550356049, 'bytes': 4399502468,
         'sha256': '07bff995b223ba742b6b8bca1846b139b78f6f97a48173c42438366d915f8977'}],
    'retained_shared_artifact': {'id': 13550562409, 'bytes': 3173706949,
        'sha256': '2946f87a9c8d23409c16dbd5495502440962e72a2d405d2b45098ae58bdce26e'}}


def gate(args):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('isolated-arm execution is repository Actions only')
    identity = f'{args.system}-{args.mode}-{args.repetition}'
    if args.stage == 'main' and identity in OTEL_FINAL_BLOCKS:
        approved = b.read(b.repo() / OTEL_FINAL_APPROVAL)
        if (not all(approved.get(k) is True for k in ('original_source_execution_GO',
                'root_original_GO', 'independent_original_GO', 'original_scientific_rollout_GO',
                'original108_scope_retained', 'all_four_GC25_full9_model_publications_verified',
                'actual_model_resource_review_GO', 'full_validation_unknown_budget_risk_accepted',
                'full9_first_validation_required_and_retained'))
                or approved.get('blocks') != OTEL_FINAL_BLOCKS
                or approved.get('allocation_regime') != REGIME
                or approved.get('full_size_phase_budgets_qualified') is not False
                or approved.get('full_validation_budget_observed') is not False
                or approved.get('rollout_design_GO_sha256') != OTEL_FINAL_DESIGN_SHA256
                or approved.get('actual_resource_runs') != [42457632259]
                or approved.get('actual_resource_source') != '76aebebfc11c68c2c6f4b916f715a833f548d9cc'
                or approved.get('actual_resource_parent_sha256') != 'd11b21048dc9876ee34b909ad3980fd0c319965ee01f6903bbd89b6735fa62b4'
                or approved.get('bering_child_go_environment') != {'GOGC': '25'}
                or approved.get('additional_model_swap_file_bytes') != 16 * 1024**3
                or approved.get('model_swap_design_GO_sha256') !=
                    '3d91a5c64cc8a74a2c0cb71409094e339d7fa577bd0ef46835e6058d010c1c33'
                or approved.get('implementation_sha256') != b.implementation_hashes()):
            raise ValueError('exact OTel full remaining8 actual-model and prospective source approval required')
        return
    if args.stage == 'main' and identity in OTEL_STAGED_BLOCKS:
        approved = b.read(b.repo() / OTEL_STAGED_APPROVAL)
        if (not all(approved.get(k) is True for k in ('original_source_execution_GO',
                'root_original_GO', 'independent_original_GO', 'original_scientific_rollout_GO',
                'original108_scope_retained', 'partial_unknown_budget_risk_accepted'))
                or approved.get('blocks') != OTEL_STAGED_BLOCKS
                or approved.get('allocation_regime') != REGIME
                or approved.get('full_size_phase_budgets_qualified') is not False
                or approved.get('partial_full_count_budget_observed') is not False
                or approved.get('OTel_remaining_full8_dispatch_GO') is not False
                or approved.get('rollout_design_GO_sha256') != OTEL_STAGED_DESIGN_SHA256
                or approved.get('actual_resource_runs') != [42347357851]
                or approved.get('implementation_sha256') != b.implementation_hashes()):
            raise ValueError('exact OTel absent/partial remaining20 prospective source approval required')
        return
    if args.stage == 'main' and identity in PCDSB_BLOCKS:
        approved = b.read(b.repo() / PCDSB_APPROVAL)
        if (not all(approved.get(k) is True for k in ('original_source_execution_GO',
                'root_original_GO', 'independent_original_GO', 'original_scientific_rollout_GO',
                'original108_scope_retained', 'partial_unknown_budget_risk_accepted'))
                or approved.get('blocks') != PCDSB_BLOCKS
                or approved.get('allocation_regime') != REGIME
                or approved.get('full_size_phase_budgets_qualified') is not False
                or approved.get('partial_full_count_budget_observed') is not False
                or approved.get('OTel_remaining28_dispatch_GO') is not False
                or approved.get('rollout_design_GO_sha256') != PCDSB_DESIGN_SHA256
                or approved.get('actual_resource_runs') != [42267236483, 42347353371, 42347362261, 42347366203]
                or approved.get('implementation_sha256') != b.implementation_hashes()):
            raise ValueError('exact PC/DSB remaining56 prospective source approval required')
        return
    if args.stage != 'main' or identity not in STAGED_BLOCKS:
        return b.gate(args.stage)
    approved = b.read(b.repo() / STAGED_APPROVAL)
    if (not all(approved.get(k) is True for k in ('original_source_execution_GO', 'root_original_GO',
            'independent_original_GO', 'original_scientific_rollout_GO'))
            or approved.get('blocks') != STAGED_BLOCKS or approved.get('allocation_regime') != REGIME
            or approved.get('full_size_phase_budgets_qualified') is not False
            or approved.get('rollout_design_GO_sha256') != STAGED_DESIGN_SHA256
            or approved.get('DSB_retry_design_GO_sha256') != DSB_RETRY_DESIGN_SHA256
            or approved.get('failed_DSB_attempt') != DSB_ORIGINAL
            or approved.get('all_four_replacement_captures_new') is not True
            or approved.get('old_DSB_inputs_imported') is not False
            or approved.get('implementation_sha256') != b.implementation_hashes()):
        raise ValueError('exact four-block prospective scientific rollout source approval required')


def execution():
    return {'run_id': int(os.environ['GITHUB_RUN_ID']), 'source': os.environ['GITHUB_SHA']}


def planned(args):
    # Only the separately registered failed DSB block may be replaced, wholly.
    if args.mode == 'full' and args.repetition == 9 and (
            args.system != 'deathstarbench' or args.stage != 'main'):
        raise ValueError('registered paired blocks excluded; DSB replacement requires its main source gate')
    value = block(args.system, args.mode, args.repetition)
    value.update(stage=args.stage, smoke=False, allocation_regime=REGIME)
    return value


def name(phase, slot=None):
    middle = phase if slot is None else f'{phase}-slot{slot}'
    return f"v6-isolated-{middle}-{os.environ['GITHUB_RUN_ID']}-attempt{os.environ['GITHUB_RUN_ATTEMPT']}"


def output(**values):
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf8') as stream:
            for key, value in values.items():
                stream.write(f'{key}={value}\n')


def claim(value):
    row = json.loads(value) if isinstance(value, str) else value
    if (set(row) != {'id', 'digest', 'name'} or not str(row['id']).isdigit()
            or int(row['id']) <= 0 or not isinstance(row['name'], str)):
        raise ValueError('an exact upstream artifact ID, digest and name are required')
    return {**row, 'id': int(row['id'])}


def dependency(value):
    """Literal job-output boundary, never search for an artifact by its name."""
    row = json.loads(value)
    if set(row) - {'artifact_id', 'artifact_digest', 'artifact_name', 'collector',
                   'block_plan_sha256', 'shared_sha256'}:
        raise ValueError('unexpected direct upstream job outputs')
    return claim({'id': row['artifact_id'], 'digest': row['artifact_digest'], 'name': row['artifact_name']})


def actual_artifact(value):
    value = claim(value)
    api = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{value['id']}")
    b.artifact_identity(api, value['name'], value['id'], value['digest'])
    return api


def fetch(value, destination, expected_names, *, original_parent=None):
    """One exact current-run publication, whole ZIP SHA and every member CRC."""
    value = claim(value)
    if original_parent is None:
        actual = actual_artifact(value)
    else:
        from .main_continuation_v6 import original_artifact
        actual = original_artifact(original_parent, value)
    destination.mkdir(parents=True)
    predownload = b.capacity(destination, actual['size_in_bytes'])
    archive = destination / 'delivery.zip'
    request = urllib.request.Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{value['id']}/zip",
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2026-03-10'})

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    try:
        response = urllib.request.build_opener(NoRedirect).open(request, timeout=60)
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise
        target = error.headers.get('Location', '')
        parsed = urllib.parse.urlsplit(target)
        if parsed.scheme != 'https' or not parsed.hostname or not any(parsed.hostname.endswith(s) for s in
                ('.blob.core.windows.net', '.githubusercontent.com', '.actions.githubusercontent.com')):
            raise ValueError('unexpected immutable delivery host')
        response = urllib.request.urlopen(target, timeout=60)
    digest, total = hashlib.sha256(), 0
    with response, archive.open('xb') as stream:
        while data := response.read(1024**2):
            total += len(data)
            if total > actual['size_in_bytes']:
                raise ValueError('outer publication exceeds its actual API bytes')
            digest.update(data)
            stream.write(data)
    if total != actual['size_in_bytes'] or 'sha256:' + digest.hexdigest() != actual['digest']:
        raise ValueError('complete cloud ZIP bytes/SHA differ')
    members = {}
    with zipfile.ZipFile(archive) as zipped:
        infos = zipped.infolist()
        if len(infos) != len(expected_names) or {i.filename for i in infos} != set(expected_names):
            raise ValueError('publication contains unexpected or duplicate package members')
        preunwrap = b.capacity(destination, sum(i.file_size for i in infos))
        for info in infos:
            if info.is_dir() or stat.S_IFMT(info.external_attr >> 16) not in (0, stat.S_IFREG) or info.flag_bits & 1:
                raise ValueError('ordinary unencrypted package files required')
            path = destination / info.filename
            with zipped.open(info) as source, path.open('xb') as target:
                shutil.copyfileobj(source, target, 1024**2)
            if path.stat().st_size != info.file_size:
                raise ValueError('incomplete package member')
            members[info.filename] = {'bytes': info.file_size, 'sha256': b.sha(path), 'CRC32': f'{info.CRC:08x}'}
    return {'artifact_API': actual, 'whole_ZIP_sha256': digest.hexdigest(), 'ZIP_members': members,
            'all_members_EOF_CRC_verified': True, 'delivery': str(archive),
            'predownload_actual_disk_guard': predownload, 'preunwrap_actual_disk_guard': preunwrap}


def release_delivery(receipt):
    path = Path(receipt['delivery'])
    if path.is_symlink() or path.name != 'delivery.zip' or b.sha(path) != receipt['whole_ZIP_sha256']:
        raise ValueError('owned verified delivery changed before release')
    path.unlink()
    receipt['verified_outer_delivery_released'] = True


def release_package(path, package):
    if (path.is_symlink() or path.name not in ('shared.tar.gz', 'capture.tar.gz', 'model.tar.gz')
            or path.stat().st_size != package['bytes'] or b.sha(path) != package['sha256']):
        raise ValueError('verified owned package changed before release')
    path.unlink()


def import_shared(root, args):
    if getattr(args, 'main_parent_record', None):
        from .main_continuation_v6 import import_shared as original_shared
        return original_shared(root, args)
    wanted = planned(args)
    folder = root / 'shared-input'
    receipt = fetch(dependency(os.environ['V6_SHARED_ARTIFACT']), folder,
                    ('shared.tar.gz', 'shared.tar.gz.json', 'shared-seal.json', 'block-plan.json'))
    seal, package, plan = (b.read(folder / p) for p in
                           ('shared-seal.json', 'shared.tar.gz.json', 'block-plan.json'))
    if (seal['block_plan_sha256'] != os.environ['V6_BLOCK_PLAN_SHA256']
            or seal['shared_sha256'] != os.environ['V6_SHARED_SHA256']
            or b.sha(folder / 'block-plan.json') != seal['block_plan_sha256']
            or package['sha256'] != seal['shared_sha256']):
        raise ValueError('upstream common plan/package seals differ')
    if any(plan.get(key) != value for key, value in wanted.items()) or any(
            plan.get(key) != value for key, value in execution().items()):
        raise ValueError('shared input is not this exact fresh fixed block/source/allocation')
    guard = b.unpack(folder / 'shared.tar.gz', root, seal['shared_sha256'], guard_root=root, expected_inventory=package)
    for relative, expected in package['files'].items():
        path = root / relative
        if (path.stat().st_size, b.sha(path), stat.S_IMODE(path.stat().st_mode)) != (
                expected['bytes'], expected['sha256'], expected['mode']):
            raise ValueError('restored common image/config/kernel file differs')
    if (b.sha(root / 'vms/golden/manifest.json'), b.sha(root / 'blueprint/blueprint.json')) != (
            plan['golden_sha256'], plan['blueprint_sha256']):
        raise ValueError('common golden/blueprint identity differs')
    if (seal.get('golden_sha256'), seal.get('blueprint_sha256')) != (
            plan['golden_sha256'], plan['blueprint_sha256']):
        raise ValueError('common seal and exact plan identities differ')
    shutil.copyfile(folder / 'block-plan.json', root / 'block-plan.json')
    release_delivery(receipt)
    release_package(folder / 'shared.tar.gz', package)
    receipt.update(preextract_actual_disk_guard=guard, block_plan_sha256=seal['block_plan_sha256'])
    write_json(root / 'isolated-shared-import.json', receipt)
    return plan


def verify_allocation(roots, saved, allocation):
    if allocation.get('main_closed_input_parent'):
        from .main_continuation_v6 import verify_allocation as original_allocation
        return original_allocation(roots, saved, allocation)
    """Explicit alternate allocation; the ordinary paired predicate stays strict."""
    plan = allocation.get('plan') or {}
    expected = block(plan.get('system'), plan.get('mode'), plan.get('repetition'))
    if (allocation.get('regime') != REGIME or plan.get('allocation_regime') != REGIME
            or (plan.get('mode') == 'full' and plan.get('repetition') == 9 and (
                plan.get('system') != 'deathstarbench' or plan.get('stage') != 'main'))
            or any(plan.get(k) != v for k, v in expected.items())
            or any(plan.get(k) != v for k, v in execution().items())
            or set(allocation.get('models', {})) != set(COLLECTORS)):
        raise ValueError('unreviewed/foreign between-host allocation')
    plan_sha = hashlib.sha256((json.dumps(plan, indent=2, ensure_ascii=False) + '\n').encode()).hexdigest()
    # Compare the exact original plan bytes through each retained block reference.
    if allocation.get('block_plan_sha256') != plan_sha:
        raise ValueError('allocation common plan hash differs')
    if len({s['case'].get('runner_boot_id') for s in saved}) != 4:
        raise ValueError('four isolated training hosts require distinct recorded boot IDs')
    for field in ('training_artifact_API', 'model_artifact_API'):
        if len({row[field]['id'] for row in allocation['models'].values()}) != 4:
            raise ValueError('four distinct actual publications required')
    for root, forecast in zip(roots, saved):
        status = forecast['case']
        collector = status['collector']
        row = allocation['models'][collector]
        reference = b.read(Path(root) / 'v6-block-reference.json')
        restored = b.read(Path(root) / 'v6-training-publication-restored.json')
        processing = forecast.get('processing_execution') or {}
        if (row.get('case') != status or row.get('forecast_sha256') != b.sha(Path(root) / 'forecast-saved.json')
                or row.get('training_artifact_API') != restored.get('artifact_API')
                or restored.get('training_closed_input_sha256') != forecast['training_closed_input_sha256']
                or not status.get('runner_boot_id')
                or reference.get('allocation_regime') != REGIME
                or reference.get('training_slot') != plan['arm_orders']['training'].index(collector)
                or reference.get('block_plan_sha256') != plan_sha
                or reference.get('blueprint_sha256') != plan.get('blueprint_sha256')
                or reference.get('golden_sha256') != plan.get('golden_sha256')
                or (reference.get('run_id'), reference.get('source')) != (plan['run_id'], plan['source'])
                or reference.get('capture_host_resources_sha256') != b.sha(Path(root) / 'capture-host-resources.json')
                or status.get('allocation_regime') != REGIME
                or (str(processing.get('run_id')), processing.get('commit')) != (str(plan['run_id']), plan['source'])
                or b.read(Path(root) / 'processing-execution.json') != processing
                or (str(status.get('run_id')), status.get('commit'), status.get('blueprint_sha256'),
                    status.get('stage'), status.get('smoke')) != (
                    str(plan['run_id']), plan['source'], plan['blueprint_sha256'], plan['stage'], False)):
            raise ValueError('actual individual training host/slot/source/closure differs')
        for api in (row['training_artifact_API'], row['model_artifact_API']):
            b.artifact_identity(api, api['name'], api['id'], api['digest'])
        slot = plan['arm_orders']['training'].index(collector)
        producing = status.get('producing_job') or {}
        if (producing.get('job'), producing.get('slot')) != (f'training{slot}', slot) or (
                type(producing.get('attempt')) is not int or producing['attempt'] < 1):
            raise ValueError('actual training job/attempt/slot identity missing')
        if row['training_artifact_API']['name'] != f"v6-isolated-training-slot{slot}-{plan['run_id']}-attempt{producing['attempt']}":
            raise ValueError('training publication differs from its actual producing attempt')
        model_job = restored.get('model_producing_job') or {}
        if ((model_job.get('job'), model_job.get('slot'), model_job.get('runner_boot_id')) != (
                f'model{slot}', slot, processing.get('runner_boot_id'))
                or type(model_job.get('attempt')) is not int or model_job['attempt'] < 1
                or model_job.get('restored_ns', processing['started_ns']) > processing['started_ns']
                or row['model_artifact_API']['name'] !=
                f"v6-isolated-model-slot{slot}-{plan['run_id']}-attempt{model_job['attempt']}"):
            raise ValueError('actual model producing job/attempt/boot differs from its frozen processing')
        for phase, api in (('training', row['training_artifact_API']), ('model', row['model_artifact_API'])):
            if not re.fullmatch(f"v6-isolated-{phase}-slot{slot}-{plan['run_id']}-attempt[1-9][0-9]*", api['name']):
                raise ValueError('publication belongs to another opaque producing slot')


def import_models(root, plan):
    if plan.get('main_closed_input_parent'):
        from .main_continuation_v6 import import_models as original_models
        return original_models(root, plan)
    jobs = json.loads(os.environ['V6_MODEL_ARTIFACTS'])
    upstream = {}
    for slot in range(4):
        job = jobs[f'model{slot}']
        collector = plan['arm_orders']['training'][slot]
        if job.get('result') != 'success' or job['outputs'].get('collector') != collector:
            raise ValueError('all four actual successful model jobs/opaque assignments required')
        upstream[collector] = dependency(json.dumps(job['outputs']))
    allocation = {'regime': REGIME, 'plan': plan, 'block_plan_sha256': b.sha(root / 'block-plan.json'), 'models': {}}
    for collector in COLLECTORS:
        folder = root / 'model-input' / collector
        receipt = fetch(upstream[collector], folder, ('model.tar.gz', 'model.tar.gz.json'))
        package = b.read(folder / 'model.tar.gz.json')
        target = root / 'models' / collector
        target.mkdir(parents=True)
        guard = b.unpack(folder / 'model.tar.gz', target, package['sha256'], guard_root=root, expected_inventory=package)
        if b.inventory(target) != package['files']:
            raise ValueError('all portable model member bytes/SHA/modes must match')
        frozen = require_forecast(target, plan['system'], plan['mode'], plan['repetition'], collector,
                                  stage=plan['stage'], smoke=False)
        training = b.read(target / 'v6-training-publication-restored.json')
        allocation['models'][collector] = {'case': frozen['case'],
            'forecast_sha256': b.sha(target / 'forecast-saved.json'),
            'training_artifact_API': training['artifact_API'], 'model_artifact_API': receipt['artifact_API']}
        release_delivery(receipt)
        release_package(folder / 'model.tar.gz', package)
        receipt['preextract_actual_disk_guard'] = guard
        write_json(folder / 'verified-import.json', receipt)
    barrier = require_block_freeze([root / 'models' / c for c in COLLECTORS], allocation=allocation)
    write_json(root / 'isolated-allocation.json', allocation)
    write_json(root / 'block-all-forecasts-frozen.json', barrier)
    return allocation, barrier


def capture(args, root):
    plan = import_shared(root, args)
    collector = plan['arm_orders'][args.capture_phase][args.slot]
    output(collector=collector, artifact_name=name(args.capture_phase, args.slot))
    allocation, barrier = (import_models(root, plan) if args.capture_phase == 'validation' else (None, None))
    case_root = root / args.capture_phase / collector
    status_path = root / f'block-{args.capture_phase}-slot{args.slot}-status.json'
    status = {'phase': args.capture_phase, 'slot': args.slot, 'collector': collector,
              'allocation_regime': REGIME, 'execution': execution(), 'started_ns': time.time_ns(), 'status': 'started'}
    write_json(status_path, status)
    label = f'{args.capture_phase}-{args.slot}-{collector}'
    try:
        b.vms(root, 'start', label, plan['golden_sha256'])
        case = Case(case_root, args.system, args.mode, args.repetition, collector, args.capture_phase,
                    smoke=False, stage=args.stage, vm_dir=root / 'vms/active')
        case.status['allocation_regime'] = REGIME
        case.status['producing_job'] = {'job': os.environ['GITHUB_JOB'],
                                       'attempt': int(os.environ['GITHUB_RUN_ATTEMPT']), 'slot': args.slot}
        shutil.copyfile(root / 'host-resources.json', case_root / 'capture-host-resources.json')
        if barrier is not None:
            write_json(case.ctx.out / 'block-freeze-verified-before-capture.json', barrier)
        case.capture(root / 'blueprint', plan['blueprint_sha256'])
    except BaseException as error:
        status.update(status='failed', error=repr(error))
        raise
    finally:
        try:
            b.stop_and_discard(root, label)
        except BaseException as error:
            status.update(status='failed', guest_cleanup_error=repr(error))
            raise
        finally:
            status['ended_ns'] = time.time_ns()
            write_json(status_path, status)
    if args.capture_phase == 'validation':
        result = evaluate(root / 'models' / collector, case_root, allocation=allocation)
        write_json(root / 'summaries' / f'{collector}.json', result)
        if result['technical_complete'] is not True:
            raise ValueError('technically incomplete validation remains retained')
    write_json(case_root / 'v6-block-reference.json', {
        'study': plan['study'], 'block_plan_sha256': b.sha(root / 'block-plan.json'),
        'blueprint_sha256': plan['blueprint_sha256'], 'golden_sha256': plan['golden_sha256'],
        **execution(), 'allocation_regime': REGIME,
        'capture_host_resources_sha256': b.sha(case_root / 'capture-host-resources.json'),
        'training_slot': plan['arm_orders']['training'].index(collector)})
    write_json(root / 'publications' / args.capture_phase / f'{collector}-before-upload.json',
               {'closed_input_sha256': b.sha(case_root / 'closed-input.json'), 'files': b.inventory(case_root)})
    status.update(status='complete', capture_complete=True)
    write_json(status_path, status)


def restore_training(args, root):
    receipt = fetch(dependency(os.environ['V6_TRAINING_ARTIFACT']), root / 'capture-input',
                    ('capture.tar.gz', 'capture.tar.gz.json'))
    folder = root / 'capture-input'
    package = b.read(folder / 'capture.tar.gz.json')
    if (package.get('study'), package.get('phase'), package.get('collector'), package.get('run_id'), package.get('source')) != (
            'clean-restart-v6', 'training', args.collector, execution()['run_id'], execution()['source']):
        raise ValueError('only this current fresh training input is allowed')
    target = root / 'case'
    target.mkdir()
    guard = b.unpack(folder / 'capture.tar.gz', target, package['sha256'], guard_root=root, expected_inventory=package)
    if b.inventory(target) != package['files'] or b.read(target / 'status.json') != package['case']:
        raise ValueError('restored complete capture inventory/identity differs')
    reference = b.read(target / 'v6-block-reference.json')
    if reference.get('allocation_regime') != REGIME or reference.get('training_slot') != args.slot:
        raise ValueError('training input assigned to another opaque slot')
    release_delivery(receipt)
    release_package(folder / 'capture.tar.gz', package)
    write_json(target / 'v6-training-publication-restored.json', {**receipt,
        'model_producing_job': {'job': os.environ['GITHUB_JOB'], 'slot': args.slot,
            'attempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
            'runner_boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'restored_ns': time.time_ns()},
        'training_closed_input_sha256': b.sha(target / 'closed-input.json'),
        'archive_sha256': package['sha256'], 'inventory_sha256': b.sha(folder / 'capture.tar.gz.json'),
        'preextract_actual_disk_guard': guard, 'restored_all_bytes_SHA_modes': True,
        'owned_local_delivery_released': True, 'cloud_original_untouched': True})
    output(collector=args.collector, artifact_name=name('model', args.slot))


def release(args, root):
    plan = b.read(root / 'block-plan.json')
    collector = plan['arm_orders'][args.capture_phase][args.slot]
    case = root / args.capture_phase / collector
    expected = b.read(root / 'publications' / args.capture_phase / f'{collector}-before-upload.json')
    archive = root / 'deliveries' / args.capture_phase / collector / 'capture.tar.gz'
    package = b.read(archive.with_suffix('.gz.json'))
    if (case.is_symlink() or b.inventory(case) != expected['files'] or package['files'] != expected['files']
            or b.sha(archive) != package['sha256']):
        raise ValueError('owned complete capture changed before publication/release')
    artifact = actual_artifact({'id': args.artifact_id, 'digest': args.artifact_digest,
                                'name': name(args.capture_phase, args.slot)})
    receipt = {'artifact_API': artifact, 'closed_input_sha256': expected['closed_input_sha256'],
               'actual_publication_verified_ns': time.time_ns(), 'working_copy_released': False}
    path = root / 'publications' / args.capture_phase / f'{collector}.json'
    write_json(path, receipt)
    shutil.rmtree(case)
    archive.unlink()
    receipt.update(working_copy_released=True, released_ns=time.time_ns())
    write_json(path, receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'capture', 'restore-training', 'release'))
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--system', choices=SYSTEMS)
    parser.add_argument('--mode', choices=MODES)
    parser.add_argument('--repetition', type=int, choices=REPETITIONS)
    parser.add_argument('--stage', choices=('qualification', 'main'), default='qualification')
    parser.add_argument('--slot', type=int, choices=range(4))
    parser.add_argument('--capture-phase', choices=('training', 'validation'))
    parser.add_argument('--collector', choices=COLLECTORS)
    parser.add_argument('--artifact-id', type=int)
    parser.add_argument('--artifact-digest')
    args = parser.parse_args()
    gate(args)
    root = b.owned_root(args.root)
    started, cpu = time.time_ns(), os.times()
    receipt = {'command': args.command, 'execution': execution(), 'allocation_regime': REGIME,
               'slot': args.slot, 'block': {'system': args.system, 'mode': args.mode,
                'repetition': args.repetition, 'stage': args.stage}, 'phase': args.capture_phase,
               'started_ns': started, 'free_bytes_start': shutil.disk_usage(root).free, 'status': 'started',
               'upstream_job_outputs': {key: json.loads(os.environ[key]) for key in
                   ('V6_SHARED_ARTIFACT', 'V6_TRAINING_ARTIFACT', 'V6_MODEL_ARTIFACTS') if key in os.environ}}
    status_path = root / f'isolated-{args.command}-status.json'
    write_json(status_path, receipt)
    try:
        if args.command == 'prepare':
            b.common_prepare(root, planned(args))
            output(block_plan_sha256=b.sha(root / 'block-plan.json'), shared_sha256=b.sha(root / 'shared.tar.gz'),
                   artifact_name=name('shared'))
        elif args.command == 'capture':
            if args.slot is None or args.capture_phase is None:
                parser.error('capture needs explicit phase and opaque slot')
            capture(args, root)
        elif args.command == 'restore-training':
            if args.slot is None or args.collector is None:
                parser.error('restore needs exact training slot and collector')
            restore_training(args, root)
        else:
            if args.slot is None or args.capture_phase is None or not args.artifact_id or not args.artifact_digest:
                parser.error('release requires exact phase/slot/actual artifact ID and digest')
            release(args, root)
        receipt['status'] = 'complete'
    except BaseException as error:
        receipt.update(status='failed', error=repr(error))
        raise
    finally:
        end = os.times()
        receipt.update(ended_ns=time.time_ns(), CPU_seconds={k: getattr(end, k)-getattr(cpu, k)
                       for k in ('user', 'system', 'children_user', 'children_system')},
                       free_bytes_end=shutil.disk_usage(root).free)
        write_json(status_path, receipt)
        with (root / 'isolated-controller-cost.jsonl').open('a', encoding='utf8') as stream:
            stream.write(json.dumps(receipt) + '\n')


if __name__ == '__main__':
    main()
