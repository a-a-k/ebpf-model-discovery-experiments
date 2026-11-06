"""Explicit inspected-parent continuation of v6 QUALIFICATION; never MAIN.

The tracked docs parent record has schema ``v6-qualification-parent-v1``;
system/mode/repetition/smoke; parent_run_id/parent_source; shared_artifact and
training_artifacts (all four collector keys), each with id/name/size_in_bytes/
digest. Inspection requires root_inspection_GO and independent_inspection_GO.
Its small report supplies parent_plan_sha256/shared_sha256/golden_sha256/
blueprint_sha256 and closed_input_sha256_by_collector. Replay additionally
requires those exact fields, inspection_report_sha256, root_replay_GO and
independent_replay_GO in a NEW reviewed tracked record. Neither record is
generated or approved by this program. All downloaded bodies stay in Actions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import time

from . import block_v6 as b
from .capture_checks_v6 import verify_capture
from .plan_v6 import COLLECTORS, STUDY, block
from .runtime import write_json
from .validation_v6 import require_block_freeze, require_forecast

SCHEMA = 'v6-qualification-parent-v1'
HEX = re.compile('[0-9a-f]{64}')


def execution():
    return {'run_id': int(os.environ['GITHUB_RUN_ID']), 'source': os.environ['GITHUB_SHA']}


def record(path, expected_sha, *, replay=False):
    b.gate('qualification')
    path = Path(path)
    if (not path.parts or path.is_absolute() or '..' in path.parts or path.parts[0] != 'docs'
            or path.suffix != '.json'):
        raise ValueError('parent record must be an explicitly tracked docs JSON')
    full = b.repo() / path
    if any(p.is_symlink() for p in (full, *full.parents)) or b.sha(full) != expected_sha:
        raise ValueError('reviewed parent record bytes differ')
    subprocess.run(['git', 'ls-files', '--error-unmatch', '--', path.as_posix()],
                   cwd=b.repo(), check=True, stdout=subprocess.DEVNULL)
    value = b.read(full)
    if (value.get('schema') != SCHEMA or value.get('study') != STUDY
            or value.get('stage') != 'qualification' or type(value.get('smoke')) is not bool
            or type(value.get('parent_run_id')) is not int or value['parent_run_id'] <= 0
            or not re.fullmatch('[0-9a-f]{40}', str(value.get('parent_source', '')))
            or value['parent_run_id'] == execution()['run_id']
            or any(value.get(k) is not True for k in ('root_inspection_GO', 'independent_inspection_GO'))):
        raise ValueError('only reviewed original v6 qualification parent inputs are allowed')
    block(value['system'], value['mode'], value['repetition'])
    if set(value.get('training_artifacts', {})) != set(COLLECTORS):
        raise ValueError('exactly the four original training artifacts are required')
    artifacts = [value['shared_artifact'], *value['training_artifacts'].values()]
    if len({a['id'] for a in artifacts}) != 5:
        raise ValueError('parent publication IDs must be distinct')
    for artifact in artifacts:
        if (type(artifact.get('id')) is not int or artifact['id'] <= 0
                or type(artifact.get('size_in_bytes')) is not int or artifact['size_in_bytes'] <= 0
                or not re.fullmatch('sha256:[0-9a-f]{64}', str(artifact.get('digest', '')))):
            raise ValueError('every original publication needs its exact API size and digest')
    expected_names = {'shared_artifact': f"v6-shared-blueprint-{value['parent_run_id']}"}
    if value['shared_artifact']['name'] != expected_names['shared_artifact'] or any(
            value['training_artifacts'][c]['name'] != f"v6-training-{c}-{value['parent_run_id']}"
            for c in COLLECTORS):
        raise ValueError('foreign publication name')
    if replay:
        if any(value.get(k) is not True for k in ('root_replay_GO', 'independent_replay_GO')):
            raise ValueError('models/targets require a separately reviewed inspected-parent replay GO')
        for key in ('inspection_report_sha256', 'parent_plan_sha256', 'shared_sha256',
                    'golden_sha256', 'blueprint_sha256'):
            if not HEX.fullmatch(str(value.get(key, ''))):
                raise ValueError('replay requires every actual inspected inner seal')
        hashes = value.get('closed_input_sha256_by_collector', {})
        if set(hashes) != set(COLLECTORS) or any(not HEX.fullmatch(str(x)) for x in hashes.values()):
            raise ValueError('replay requires all four actual inspected training closure hashes')
    return value


def artifact(value, expected):
    actual = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{expected['id']}")
    if (actual.get('expired') is not False
            or any(actual.get(k) != expected[k] for k in ('id', 'name', 'size_in_bytes', 'digest'))
            or (actual.get('workflow_run') or {}).get('id') != value['parent_run_id']
            or (actual.get('workflow_run') or {}).get('head_sha') != value['parent_source']):
        raise ValueError('original qualification publication API differs from reviewed parent')
    return actual


def preflight(args):
    parent = record(args.parent_record, args.parent_sha256, replay=args.operation == 'replay')
    root = b.owned_root(args.root)
    run = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{parent['parent_run_id']}")
    if (run.get('id') != parent['parent_run_id'] or run.get('head_sha') != parent['parent_source']
            or run.get('path') != '.github/workflows/series-v6.yml'
            or run.get('event') != 'workflow_dispatch'):
        raise ValueError('parent is not the exact original v6 qualification source run')
    rows = {'shared': artifact(parent, parent['shared_artifact'])}
    rows.update({c: artifact(parent, parent['training_artifacts'][c]) for c in COLLECTORS})
    write_json(root / 'parent-publication-API.json', {'parent_run': run, 'artifacts': rows})
    # Only common + one capture coexist in inspection. Validation downloads the
    # common archive and all four ACTUAL current model publications instead.
    incoming = max(a['size_in_bytes'] for a in parent['training_artifacts'].values())
    if getattr(args, 'models_ready', False):
        if args.operation != 'replay':
            raise ValueError('only approved replay validation imports models')
        current, page = [], 1
        while True:
            items = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}/artifacts?per_page=100&page={page}")['artifacts']
            current.extend(items)
            if len(items) < 100: break
            page += 1
        models = []
        for collector in COLLECTORS:
            name = f"v6-model-{collector}-{os.environ['GITHUB_RUN_ID']}"
            matches = [a for a in current if a['name'] == name]
            if len(matches) != 1:
                raise ValueError('all four exact current model publications are required before download')
            b.artifact_identity(matches[0], name)
            models.extend(matches)
        incoming = sum(a['size_in_bytes'] for a in models)
        write_json(root / 'validation-current-run-artifact-API.json', models)
    b.capacity(root, parent['shared_artifact']['size_in_bytes'] + incoming)
    if os.environ.get('GITHUB_OUTPUT'):
        outputs = {'parent_run_id': parent['parent_run_id'],
                   'shared_artifact_id': parent['shared_artifact']['id'],
                   'system': parent['system'], 'mode': parent['mode'],
                   'repetition': parent['repetition']}
        outputs.update({c + '_artifact_id': parent['training_artifacts'][c]['id'] for c in COLLECTORS})
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf8') as f:
            for key, value in outputs.items(): f.write(f'{key}={value}\n')


def common(args, parent):
    root = b.owned_root(args.root)
    source = root / 'shared-input'
    for name in ('shared-seal.json', 'block-plan.json', 'shared.tar.gz', 'shared.tar.gz.json'):
        path = source / name
        if not path.is_file() or any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('common inputs must be owned ordinary downloaded files')
    seal, plan = b.read(source / 'shared-seal.json'), b.read(source / 'block-plan.json')
    planned = block(parent['system'], parent['mode'], parent['repetition'])
    planned.update(stage='qualification', smoke=parent['smoke'])
    if any(plan.get(k) != planned[k] for k in planned):
        raise ValueError('parent order/settings are not the original fixed qualification block')
    if (plan.get('run_id'), plan.get('source')) != (parent['parent_run_id'], parent['parent_source']):
        raise ValueError('parent common plan has another origin')
    if (b.sha(source / 'block-plan.json') != seal['block_plan_sha256']
            or b.sha(source / 'shared.tar.gz') != seal['shared_sha256']
            or any(seal[k] != plan[k] for k in ('golden_sha256', 'blueprint_sha256'))):
        raise ValueError('parent shared archive/plan/seals differ')
    package = b.read(source / 'shared.tar.gz.json')
    if package['sha256'] != seal['shared_sha256'] or package['bytes'] != (source / 'shared.tar.gz').stat().st_size:
        raise ValueError('parent common package differs from its complete delivery inventory')
    # One sequential archive walk; no repeated decompression or VM disk materialization.
    import hashlib
    wanted = {'blueprint/blueprint.json': 'blueprint_sha256',
              'vms/golden/manifest.json': 'golden_sha256'}
    seen, files = set(), set()
    with tarfile.open(source / 'shared.tar.gz', 'r|gz') as tar:
        for member in tar:
            path = Path(member.name)
            if (member.name in seen or path.is_absolute() or '..' in path.parts
                    or not (member.isfile() or member.isdir()) or member.mode & 0o7000):
                raise ValueError('invalid original common package member')
            seen.add(member.name)
            if member.isfile():
                files.add(member.name)
                claim = package['files'].get(member.name)
                if claim is None or member.size != claim['bytes'] or member.mode & 0o777 != claim['mode']:
                    raise ValueError('common archive header differs from complete delivery inventory')
            if member.name in wanted:
                if not member.isfile() or member.size > 4 * 1024**2:
                    raise ValueError('oversize parent common metadata member')
                if hashlib.sha256(tar.extractfile(member).read()).hexdigest() != seal[wanted[member.name]]:
                    raise ValueError('actual archived parent common manifest differs')
    if files != set(package['files']) or not set(wanted).issubset(seen):
        raise ValueError('missing original common package files')
    result = {'parent_plan_sha256': seal['block_plan_sha256'],
              **{k: seal[k] for k in ('shared_sha256', 'golden_sha256', 'blueprint_sha256')}}
    if args.operation == 'replay' and any(parent[k] != result[k] for k in result):
        raise ValueError('common inputs differ from reviewed actual inspection')
    write_json(root / 'inspection/common.json', result)
    return plan, seal, package


def restore_training(args):
    parent = record(args.parent_record, args.parent_sha256, replay=args.operation == 'replay')
    root, collector = b.owned_root(args.root), args.collector
    actual = artifact(parent, parent['training_artifacts'][collector])
    incoming = root / 'capture-input' / collector
    archive, package_path = incoming / 'capture.tar.gz', incoming / 'capture.tar.gz.json'
    package = b.read(package_path)
    if (package.get('study'), package.get('phase'), package.get('collector'),
            package.get('run_id'), package.get('source')) != (
            STUDY, 'training', collector, parent['parent_run_id'], parent['parent_source']):
        raise ValueError('package is not the allowlisted immutable original training arm')
    if args.operation == 'replay' and package['block_plan_sha256'] != parent['parent_plan_sha256']:
        raise ValueError('original capture block plan differs from inspected parent')
    target = root / 'case'
    if target.exists() or target.is_symlink():
        raise FileExistsError('never overwrite an original training working copy')
    before = archive.stat()
    if archive.is_symlink() or before.st_size != package['bytes']:
        raise ValueError('original archive path/size differs')
    guard = b.unpack(archive, target, package['sha256'], guard_root=root)
    if b.inventory(target) != package['files']:
        raise ValueError('every original training file/byte/SHA/mode must remain identical')
    closed = verify_capture(target, 'training')  # Includes exact readonly sealed-journal warmup proof.
    status = closed['status']
    if (status != package['case'] or status.get('stage') != 'qualification'
            or status.get('smoke') is not parent['smoke']
            or (status.get('system'), status.get('mode'), status.get('seed'), status.get('collector'))
            != (parent['system'], parent['mode'], parent['repetition'], collector)
            or (str(status.get('run_id')), status.get('commit'))
            != (str(parent['parent_run_id']), parent['parent_source'])):
        raise ValueError('closed capture identity differs from reviewed original qualification')
    closure_sha = b.sha(target / 'closed-input.json')
    if args.operation == 'replay' and (closure_sha != parent['closed_input_sha256_by_collector'][collector]
            or status.get('blueprint_sha256') != parent['blueprint_sha256']):
        raise ValueError('original closure/blueprint differs from separately inspected exact bytes')
    rows = b.read(target / 'external.json')
    receipt = {'collector': collector, 'original_capture_identity': status,
               'closed_input_sha256': closure_sha, 'block_plan_sha256': package['block_plan_sha256'],
               'phase_counts': dict(Counter(r['phase'] for r in rows)),
               'preparation_count': sum(r['phase'] == 'preparation' for r in rows),
               'all_original_files_bytes_SHA_modes_verified': True,
               'sealed_journal_preparation_verified': True, 'artifact_API': actual,
               'archive_sha256': package['sha256'], 'inventory_sha256': b.sha(package_path),
               'parent_record_sha256': args.parent_sha256, 'processing_execution': execution(),
               'preextract_actual_disk_guard': guard}
    write_json(root / 'inspection' / f'{collector}.json', receipt)
    after = archive.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('owned input archive changed before releasing its local copy')
    archive.unlink()  # Exact verified owned download only; cloud original remains immutable.
    if args.operation == 'inspect':
        if b.inventory(target) != package['files']:
            raise ValueError('inspection changed original source bytes')
        shutil.rmtree(target)  # One exact private, hash-verified restored arm; never parent source.
    else:
        write_json(target / 'v6-training-publication-restored.json', receipt)


def finish_inspection(args):
    parent = record(args.parent_record, args.parent_sha256)
    root = b.owned_root(args.root)
    source = root / 'shared-input'
    common_seals = b.read(root / 'inspection/common.json')
    if b.sha(source / 'block-plan.json') != common_seals['parent_plan_sha256']:
        raise ValueError('parent plan changed after inspection')
    rows = [b.read(root / 'inspection' / f'{c}.json') for c in COLLECTORS]
    identities = {(r['original_capture_identity']['runner_boot_id'],
                   r['original_capture_identity']['blueprint_sha256'], r['block_plan_sha256']) for r in rows}
    seals = b.read(root / 'inspection/common.json')
    if (len(identities) != 1 or next(iter(identities))[1:] != (
            seals['blueprint_sha256'], seals['parent_plan_sha256'])):
        raise ValueError('all four captures must share the same original host/order/blueprint')
    write_json(root / 'qualification-inspection-report.json', {
        'study': STUDY, 'stage': 'qualification', 'parent_record_sha256': args.parent_sha256,
        'parent_run_id': parent['parent_run_id'], 'parent_source': parent['parent_source'],
        'inspection_execution': execution(), **seals,
        'closed_input_sha256_by_collector': {r['collector']: r['closed_input_sha256'] for r in rows},
        'captures': rows, 'models_or_VMs_or_targets_executed': False,
        'scope': 'Original immutable qualification training only; manual review required before replay'})


def import_validation(args, parent):
    root = b.owned_root(args.root)
    if (root / 'block-plan.json').exists():
        raise FileExistsError('qualification validation cannot import twice')
    original, seal, package = common(args, parent)
    source = root / 'shared-input'
    guard = b.unpack(source / 'shared.tar.gz', root, seal['shared_sha256'], guard_root=root)
    for name, claim in package['files'].items():
        path = root / name
        if (path.stat().st_size != claim['bytes'] or b.sha(path) != claim['sha256']
                or (path.stat().st_mode & 0o777) != claim['mode']):
            raise ValueError('shared images/VM baseline/config bytes differ from original package')
    # Original parent bytes remain a separate immutable provenance file.
    shutil.copyfile(source / 'block-plan.json', root / 'qualification-parent-block-plan.json')
    current = dict(original)
    current.update(**execution(), qualification_parent={
        'run_id': parent['parent_run_id'], 'source': parent['parent_source'],
        'block_plan_sha256': parent['parent_plan_sha256'], 'parent_record_sha256': args.parent_sha256})
    write_json(root / 'block-plan.json', current)
    imports = []
    for collector in COLLECTORS:
        name = f"v6-model-{collector}-{os.environ['GITHUB_RUN_ID']}"
        values = []
        page = 1
        while True:
            rows = b.api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}/artifacts?per_page=100&page={page}")['artifacts']
            values.extend(a for a in rows if a['name'] == name)
            if len(rows) < 100: break
            page += 1
        if len(values) != 1:
            raise ValueError('exactly four actual current replay model publications are required')
        b.artifact_identity(values[0], name)
        folder = root / 'model-input' / name
        model_package = b.read(folder / 'model.tar.gz.json')
        target = root / 'models' / collector
        target.mkdir(parents=True)
        model_guard = b.unpack(folder / 'model.tar.gz', target, model_package['sha256'], guard_root=root)
        if b.inventory(target) != model_package['files']:
            raise ValueError('replay model complete package inventory differs')
        saved = require_forecast(target, parent['system'], parent['mode'], parent['repetition'],
                                 collector, stage='qualification', smoke=parent['smoke'])
        status = saved['case']
        if ((str(status.get('run_id')), status.get('commit'), status.get('blueprint_sha256')) != (
                str(parent['parent_run_id']), parent['parent_source'], parent['blueprint_sha256'])
                or saved['training_closed_input_sha256'] != parent['closed_input_sha256_by_collector'][collector]
                or b.read(target / 'v6-block-reference.json')['block_plan_sha256'] != parent['parent_plan_sha256']
                or (str(saved['processing_execution'].get('run_id')), saved['processing_execution'].get('commit'))
                != (str(execution()['run_id']), execution()['source'])
                or b.read(target / 'v6-training-publication-restored.json')['parent_record_sha256'] != args.parent_sha256):
            raise ValueError('frozen replay origin/current processing/approval binding differs')
        imports.append({'collector': collector, 'artifact_API': values[0],
                        'package_sha256': model_package['sha256'], 'preextract_actual_disk_guard': model_guard})
    write_json(root / 'model-package-imports.json', imports)
    write_json(root / 'block-all-forecasts-frozen.json',
               require_block_freeze([root / 'models' / c for c in COLLECTORS]))
    write_json(root / 'qualification-replay-import.json', {
        'parent_record_path': args.parent_record.as_posix(), 'parent_record_sha256': args.parent_sha256,
        'execution': execution(), 'current_plan_sha256': b.sha(root / 'block-plan.json'),
        'original_plan_sha256': b.sha(root / 'qualification-parent-block-plan.json'),
        'all_four_frozen_manifest_sha256': b.sha(root / 'block-all-forecasts-frozen.json'),
        'shared_archive_sha256': seal['shared_sha256'], 'preextract_actual_disk_guard': guard,
        'status': 'complete', 'stage': 'qualification'})


def require_prepared_validation(root):
    """Only the private explicit replay caller may select the prepared-plan branch."""
    receipt = b.read(root / 'qualification-replay-import.json')
    parent = record(receipt['parent_record_path'], receipt['parent_record_sha256'], replay=True)
    current = b.read(root / 'block-plan.json')
    original = b.read(root / 'qualification-parent-block-plan.json')
    expected = dict(original)
    expected.update(**execution(), qualification_parent={
        'run_id': parent['parent_run_id'], 'source': parent['parent_source'],
        'block_plan_sha256': parent['parent_plan_sha256'], 'parent_record_sha256': receipt['parent_record_sha256']})
    if (receipt.get('status') != 'complete' or receipt.get('stage') != 'qualification'
            or receipt['execution'] != execution() or current != expected
            or b.sha(root / 'block-plan.json') != receipt['current_plan_sha256']
            or b.sha(root / 'qualification-parent-block-plan.json') != parent['parent_plan_sha256']
            or receipt['original_plan_sha256'] != parent['parent_plan_sha256']
            or b.sha(root / 'block-all-forecasts-frozen.json') != receipt['all_four_frozen_manifest_sha256']
            or b.sha(root / 'blueprint/blueprint.json') != parent['blueprint_sha256']
            or b.sha(root / 'vms/golden/manifest.json') != parent['golden_sha256']):
        raise ValueError('explicit inspected-parent qualification import differs')
    require_block_freeze([root / 'models' / c for c in COLLECTORS])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('preflight', 'inspect-shared', 'inspect-capture',
                                           'finish-inspection', 'restore-training', 'validation'))
    parser.add_argument('--operation', choices=('inspect', 'replay'), required=True)
    parser.add_argument('--parent-record', type=Path, required=True)
    parser.add_argument('--parent-sha256', required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--collector', choices=COLLECTORS)
    parser.add_argument('--slot', type=int, choices=range(4))
    parser.add_argument('--models-ready', action='store_true')
    args = parser.parse_args()
    root = b.owned_root(args.root)
    started = time.time_ns()
    cpu = lambda: {k: getattr(os.times(), k) for k in ('user', 'system', 'children_user', 'children_system')}
    cost = {'command': args.command, 'operation': args.operation, 'started_ns': started,
            'CPU_seconds_start': cpu(), 'execution': execution(), 'status': 'started'}
    try:
        parent = record(args.parent_record, args.parent_sha256, replay=args.operation == 'replay')
        if args.command == 'preflight': preflight(args)
        elif args.command == 'inspect-shared': common(args, parent)
        elif args.command == 'inspect-capture':
            if args.operation != 'inspect' or not args.collector: parser.error('inspect requires one declared collector')
            restore_training(args)
        elif args.command == 'finish-inspection':
            if args.operation != 'inspect': parser.error('inspection is a distinct no-model execution')
            finish_inspection(args)
        elif args.command == 'restore-training':
            if args.operation != 'replay' or not args.collector: parser.error('training restore requires replay approval')
            restore_training(args)
        else:
            if args.operation != 'replay' or args.slot is None: parser.error('validation requires replay approval and slot')
            if args.slot == 0: import_validation(args, parent)
            args.system, args.mode, args.repetition = parent['system'], parent['mode'], parent['repetition']
            args.stage, args.phase = 'qualification', 'validation'
            args.full_size_qualification = not parent['smoke']
            b.capture_slot(args, prepared_plan=True)
        cost['status'] = 'complete'
    except BaseException as error:
        cost.update(status='failed', error=repr(error))
        raise
    finally:
        cost.update(ended_ns=time.time_ns(), CPU_seconds_end=cpu(), free_bytes_end=shutil.disk_usage(root).free)
        with (root / 'qualification-replay-cost.jsonl').open('a', encoding='utf8') as f:
            f.write(json.dumps(cost) + '\n')


if __name__ == '__main__':
    main()
