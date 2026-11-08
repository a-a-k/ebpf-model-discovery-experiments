"""Four fixed fresh arms, with publication before releasing each working copy."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tarfile
import time
import urllib.request

from .deployment_v6 import prepare_blueprint
from .plan_v6 import COLLECTORS, MODES, REPETITIONS, STUDY, SYSTEMS, block
from .runtime import Context, write_json
from .study_v6 import Case, verify_files
from .validation_v6 import evaluate, require_block_freeze, require_forecast

RESERVE = 2 * 1024**3
QUALIFICATION = 'docs/clean-restart-v6-execution-qualification.json'

def implementation_hashes():
    # The approval document is intentionally outside this source census: adding
    # the reviewed qualification record must not require hashing itself.
    listed = subprocess.check_output([
        'git', 'ls-files', '-z', '--', 'src', 'systems', 'scripts',
        '.github/workflows/series-v6.yml', '.github/workflows/checks.yml',
        '.github/workflows/qualification-replay-v6.yml',
        '.github/workflows/series-isolated-v6.yml',
        '.github/workflows/main-continuation-v6.yml',
        'docs/PROTOCOL_V6.md', 'docs/PROTOCOL_V6_ISOLATED_ARMS.md', 'AGENTS.md', 'pyproject.toml'], cwd=repo())
    names = sorted(set(listed.decode('utf8').split('\0')) - {''})
    return {name: sha(repo() / name) for name in names}


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def repo():
    return Path(__file__).resolve().parents[2]


def owned_root(path):
    supplied = Path(path).absolute()
    if any(p.is_symlink() for p in (supplied, *supplied.parents)):
        raise ValueError('working root cannot contain symlinks')
    root, work = supplied.resolve(), (repo() / 'work').resolve()
    if not root.is_relative_to(work):
        raise ValueError('v6 working root must remain within this checkout/work')
    root.mkdir(parents=True, exist_ok=True)
    return root


def capacity(root, incoming):
    free = shutil.disk_usage(root).free
    row = {'at_ns': time.time_ns(), 'free_bytes': free,
           'incoming_bytes': incoming, 'reserve_bytes': RESERVE}
    with (root / 'block-disk-guards.jsonl').open('a', encoding='utf8') as f:
        f.write(json.dumps(row) + '\n')
    if free < incoming + RESERVE:
        raise OSError('insufficient actual block workspace free bytes')
    return row


def inventory(root):
    rows = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink() or not (p.is_dir() or p.is_file()):
            raise ValueError('only regular files/directories enter a v6 publication')
        if p.is_file():
            rows[p.relative_to(root).as_posix()] = {
                'bytes': p.stat().st_size, 'sha256': sha(p),
                'mode': stat.S_IMODE(p.stat().st_mode)}
    return rows


def gate(stage):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('v6 research execution is GitHub Actions only')
    if stage == 'main':
        approval = read(repo() / QUALIFICATION)
        if not all(approval.get(k) is True for k in (
                'original_main_execution_GO', 'root_original_GO',
                'independent_original_GO', 'actual_actions_execution_qualified',
                'full_size_phase_budgets_qualified')):
            raise ValueError('MAIN requires reviewed actual full-size original qualification')
        if not approval.get('qualification_runs'):
            raise ValueError('qualification must name its actual Actions runs')
        expected = implementation_hashes()
        if approval.get('implementation_sha256') != expected:
            raise ValueError('qualified v6 implementation differs from this source')


def api(path):
    request = urllib.request.Request('https://api.github.com/' + path,
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2026-03-10'})
    with urllib.request.urlopen(request, timeout=60) as result:
        return json.load(result)


def artifact_identity(value, name, artifact_id=None, digest=None):
    expected_run = int(os.environ['GITHUB_RUN_ID'])
    origin = value.get('workflow_run') or {}
    if digest is not None:
        if re.fullmatch('[0-9a-f]{64}', digest):
            digest = 'sha256:' + digest
        elif not re.fullmatch('sha256:[0-9a-f]{64}', digest):
            raise ValueError('invalid upload-action SHA256 output')
    if (value.get('name') != name or value.get('expired') is not False
            or type(value.get('size_in_bytes')) is not int or value['size_in_bytes'] <= 0
            or origin.get('id') != expected_run or origin.get('head_sha') != os.environ['GITHUB_SHA']
            or not re.fullmatch('sha256:[0-9a-f]{64}', str(value.get('digest', '')))
            or (artifact_id is not None and value.get('id') != artifact_id)
            or (digest is not None and value.get('digest') != digest)):
        raise ValueError('actual published artifact differs from this exact run/source/arm')


def vms(root, action, label, golden_sha=None):
    env = dict(os.environ)
    if golden_sha:
        env['V6_GOLDEN_SHA256'] = golden_sha
    with (root / 'block-vm-commands.jsonl').open('a', encoding='utf8') as f:
        started = time.time_ns()
        result = subprocess.run(['bash', str(repo() / 'scripts/vms-v6.sh'), action,
                                 str(root / 'vms'), label], env=env)
        f.write(json.dumps({'action': action, 'label': label, 'started_ns': started,
                            'ended_ns': time.time_ns(), 'exit_status': result.returncode}) + '\n')
    result.check_returncode()


def stop_and_discard(root, label):
    if (root / 'vms/active/owner.json').is_file():
        vms(root, 'stop', label)
        vms(root, 'discard', label)


class CompressedModelWriter:
    """Preserve the disk reserve on every compressed portable-model write."""
    def __init__(self, stream, folder, guard):
        self.stream, self.folder, self.guard = stream, folder, guard

    def write(self, data):
        free = shutil.disk_usage(self.folder).free
        self.guard['minimum_free_before_write_bytes'] = min(self.guard['minimum_free_before_write_bytes'], free)
        if free < len(data) + RESERVE:
            raise OSError('compressed model write would cross the actual disk reserve')
        count = self.stream.write(data)
        if count != len(data):
            raise OSError('incomplete compressed model write')
        self.guard['compressed_bytes_written'] += count
        return count

    def tell(self):
        return self.stream.tell()

    def flush(self):
        self.stream.flush()


def pack(root, destination, files, directories=(), *, guard_compressed_writes=False):
    if destination.exists():
        raise FileExistsError('never replace a sealed v6 package')
    total = sum((root / name).stat().st_size for name in files)
    if guard_compressed_writes:
        if (destination.name != 'model.tar.gz'
                or not destination.resolve().is_relative_to((repo() / 'work').resolve())
                or any(p.is_symlink() for p in (destination, *destination.parents))):
            raise ValueError('compressed-write guard is only for the owned portable model archive')
        guard = capacity(destination.parent, 0)
        guard.update(budget='actual compressed writes', uncompressed_member_bytes=total,
                     minimum_free_before_write_bytes=guard['free_bytes'], compressed_bytes_written=0)
        stream = destination.open('xb', buffering=0)
    else:
        guard = capacity(destination.parent, total + total // 100 + 8192 * (len(files) + len(directories)) + 10240)
        stream = None
    try:
        writer = CompressedModelWriter(stream, destination.parent, guard) if stream else None
        with tarfile.open(destination, 'w:gz', fileobj=writer, compresslevel=1) as tar:
            for name in sorted(directories):
                tar.add(root / name, arcname=name, recursive=False)
            for name in sorted(files):
                if (root / name).is_symlink() or not (root / name).is_file():
                    raise ValueError('only regular files can enter a model/common package')
                tar.add(root / name, arcname=name, recursive=False)
    finally:
        if stream is not None:
            stream.close()
            guard['free_bytes_after_close'] = shutil.disk_usage(destination.parent).free
            write_json(root / 'portable-model-write-guard.json', guard)
    if guard_compressed_writes:
        capacity(destination.parent, 0)
    write_json(destination.with_suffix(destination.suffix + '.json'), {
        'bytes': destination.stat().st_size, 'sha256': sha(destination),
        'prepack_actual_disk_guard': guard,
        'directories': sorted(directories),
        'files': {n: {'bytes': (root/n).stat().st_size, 'sha256': sha(root/n),
                      'mode': stat.S_IMODE((root/n).stat().st_mode)} for n in files}})


def unpack(archive, destination, expected_sha, *, guard_root=None, expected_inventory=None):
    if sha(archive) != expected_sha:
        raise ValueError('parent-bound package SHA differs')
    if expected_inventory is not None and (archive.stat().st_size != expected_inventory['bytes']
            or expected_inventory['sha256'] != expected_sha):
        raise ValueError('complete package bytes/SHA differ from inventory')
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        names = [m.name for m in members]
        if len(set(names)) != len(names):
            raise ValueError('duplicate package member')
        for member in members:
            p = Path(member.name)
            if p.is_absolute() or '..' in p.parts or not (member.isfile() or member.isdir()):
                raise ValueError('package can contain only owned relative regular files')
            if member.mode & 0o7000:
                raise ValueError('package cannot request special permission bits')
        if expected_inventory is not None:
            expected_names = set(expected_inventory['files']) | set(expected_inventory.get('directories', []))
            if set(names) != expected_names or any(
                    m.isfile() != (m.name in expected_inventory['files']) for m in members):
                raise ValueError('complete package member census differs from inventory')
        guard = capacity(guard_root or destination.parent, sum(m.size for m in members))
        tar.extractall(destination, filter='data')
        # The safe data filter strips dangerous special bits. Restore only the
        # original ordinary permission bits, including readonly golden disks.
        for member in members:
            (destination / member.name).chmod(member.mode & 0o777)
        if expected_inventory is not None:
            for name, expected in expected_inventory['files'].items():
                path = destination / name
                if (path.stat().st_size, sha(path), stat.S_IMODE(path.stat().st_mode)) != (
                        expected['bytes'], expected['sha256'], expected['mode']):
                    raise ValueError('restored complete package bytes/SHA/modes differ')
    return guard


def common_prepare(root, plan):
    vms(root, 'provision', 'preparation')
    golden_sha = sha(root / 'vms/golden/manifest.json')
    try:
        vms(root, 'start', 'blueprint', golden_sha)
        ctx = Context(root / 'blueprint-preparation', plan['mode'], plan['repetition'],
                      vm_dir=root / 'vms/active')
        ctx.collector = 'none'
        adapter = prepare_blueprint(ctx, plan['system'], root / 'blueprint')
        blueprint_sha = adapter.v6_blueprint_sha256
        adapter.close()
    finally:
        stop_and_discard(root, 'blueprint')
    plan.update(golden_sha256=golden_sha, blueprint_sha256=blueprint_sha,
                run_id=int(os.environ['GITHUB_RUN_ID']), source=os.environ['GITHUB_SHA'])
    write_json(root / 'block-plan.json', plan)
    paths = [p.relative_to(root).as_posix() for folder in ('vms/golden', 'blueprint')
             for p in (root / folder).rglob('*') if p.is_file()]
    directories = [p.relative_to(root).as_posix() for folder in ('vms/golden', 'blueprint')
                   for p in (root / folder).rglob('*') if p.is_dir()]
    pack(root, root / 'shared.tar.gz', paths, directories)
    write_json(root / 'shared-seal.json', {'shared_sha256': sha(root / 'shared.tar.gz'),
        'block_plan_sha256': sha(root / 'block-plan.json'),
        'golden_sha256': golden_sha, 'blueprint_sha256': blueprint_sha})


def import_validation(root, plan):
    source = root / 'shared-input'
    seal = read(source / 'shared-seal.json')
    for key, env in (('block_plan_sha256', 'V6_BLOCK_PLAN_SHA256'),
                     ('shared_sha256', 'V6_SHARED_SHA256')):
        if seal[key] != os.environ[env]:
            raise ValueError('shared inputs differ from original training job outputs')
    if sha(source / 'block-plan.json') != seal['block_plan_sha256']:
        raise ValueError('training block plan differs')
    frozen_plan = read(source / 'block-plan.json')
    for k in ('study', 'system', 'mode', 'repetition', 'arm_orders', 'stage', 'smoke'):
        if frozen_plan[k] != plan[k]:
            raise ValueError('shared blueprint belongs to another fixed block')
    if (frozen_plan['run_id'], frozen_plan['source']) != (
            int(os.environ['GITHUB_RUN_ID']), os.environ['GITHUB_SHA']):
        raise ValueError('historical shared input is forbidden')
    guard = unpack(source / 'shared.tar.gz', root, seal['shared_sha256'], guard_root=root)
    write_json(root / 'shared-restored.json', {'shared_sha256': seal['shared_sha256'],
               'preextract_actual_disk_guard': guard})
    if (sha(root / 'vms/golden/manifest.json'), sha(root / 'blueprint/blueprint.json')) != (
            frozen_plan['golden_sha256'], frozen_plan['blueprint_sha256']):
        raise ValueError('shared golden/blueprint seals differ')
    write_json(root / 'block-plan.json', frozen_plan)
    model_root = root / 'models'
    model_root.mkdir()
    all_artifacts = []
    page = 1
    while True:
        rows = api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}/artifacts?per_page=100&page={page}")['artifacts']
        all_artifacts.extend(rows)
        if len(rows) < 100: break
        page += 1
    write_json(root / 'validation-current-run-artifact-API.json', all_artifacts)
    imports = []
    for collector in COLLECTORS:
        name = f"v6-model-{collector}-{os.environ['GITHUB_RUN_ID']}"
        matches = [a for a in all_artifacts if a['name'] == name]
        if len(matches) != 1:
            raise ValueError('exactly one model artifact per frozen arm is required')
        artifact_identity(matches[0], name)
        folder = root / 'model-input' / name
        package = read(folder / 'model.tar.gz.json')
        target = model_root / collector
        target.mkdir()
        guard = unpack(folder / 'model.tar.gz', target, package['sha256'])
        if inventory(target) != package['files']:
            raise ValueError('model package members differ from their complete inventory')
        saved = require_forecast(target, plan['system'], plan['mode'], plan['repetition'], collector,
                                 smoke=plan['smoke'], stage=plan['stage'])
        if (saved['case'].get('blueprint_sha256') != frozen_plan['blueprint_sha256']
                or sha(target / 'closed-input.json') != saved['training_closed_input_sha256']
                or read(target / 'v6-block-reference.json')['block_plan_sha256'] != seal['block_plan_sha256']):
            raise ValueError('model training inputs differ from the original frozen common block')
        imports.append({'collector': collector, 'artifact_API': matches[0],
                        'package_sha256': package['sha256'], 'preextract_actual_disk_guard': guard})
    write_json(root / 'model-package-imports.json', imports)
    write_json(root / 'block-all-forecasts-frozen.json',
               require_block_freeze([model_root / c for c in COLLECTORS]))
    return frozen_plan


def capture_slot(args, *, prepared_plan=False):
    gate(args.stage)
    root = owned_root(args.root)
    if prepared_plan:
        if args.stage != 'qualification' or args.phase != 'validation':
            raise ValueError('prepared parent imports are qualification-validation only')
        from .qualification_replay_v6 import require_prepared_validation
        require_prepared_validation(root)
    planned = block(args.system, args.mode, args.repetition)
    planned.update(stage=args.stage,
                   smoke=args.stage == 'qualification' and not args.full_size_qualification)
    if args.slot == 0 and not prepared_plan:
        if (root / 'block-plan.json').exists():
            raise FileExistsError('a block phase cannot start twice')
        if args.phase == 'training':
            common_prepare(root, planned)
        else:
            import_validation(root, planned)
    plan = read(root / 'block-plan.json')
    if any(plan[k] != planned[k] for k in ('study', 'system', 'mode', 'repetition', 'arm_orders', 'stage', 'smoke')):
        raise ValueError('slot differs from frozen block plan')
    if (plan['run_id'], plan['source']) != (int(os.environ['GITHUB_RUN_ID']), os.environ['GITHUB_SHA']):
        raise ValueError('all slots require the same actual current run and exact source')
    for earlier in plan['arm_orders'][args.phase][:args.slot]:
        receipt = read(root / 'publications' / args.phase / f'{earlier}.json')
        if receipt.get('working_copy_released') is not True:
            raise ValueError('publish/release the previous complete arm before starting another')
    collector = plan['arm_orders'][args.phase][args.slot]
    case_root = root / args.phase / collector
    path = root / f'block-{args.phase}-slot{args.slot}-status.json'
    if path.exists() or case_root.exists():
        raise FileExistsError('a declared arm attempt cannot be repeated or replaced in this block')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf8') as f:
            f.write(f'collector={collector}\ncase_path={case_root.as_posix()}\n')
            if args.slot == 0 and args.phase == 'training':
                f.write(f"block_plan_sha256={sha(root/'block-plan.json')}\nshared_sha256={sha(root/'shared.tar.gz')}\n")
    label = f'{args.phase}-{args.slot}-{collector}'
    status = {'phase': args.phase, 'slot': args.slot, 'collector': collector,
              'started_ns': time.time_ns(), 'status': 'started'}
    write_json(path, status)
    try:
        vms(root, 'start', label, plan['golden_sha256'])
        if args.phase == 'validation':
            require_block_freeze([root / 'models' / c for c in COLLECTORS])
        case = Case(case_root, args.system, args.mode, args.repetition, collector,
                    args.phase, smoke=args.stage == 'qualification' and not args.full_size_qualification,
                    stage=args.stage, vm_dir=root / 'vms/active')
        if args.phase == 'validation':
            write_json(case.ctx.out / 'block-freeze-verified-before-capture.json',
                       read(root / 'block-all-forecasts-frozen.json'))
        case.capture(root / 'blueprint', plan['blueprint_sha256'])
    except BaseException as error:
        status.update(status='failed', error=repr(error))
        raise
    finally:
        try:
            stop_and_discard(root, label)
        except BaseException as error:
            status.update(status='failed', guest_cleanup_error=repr(error))
            raise
        finally:
            status.update(ended_ns=time.time_ns())
            write_json(path, status)
    if args.phase == 'validation':
        result = evaluate(root / 'models' / collector, case_root)
        if result['technical_complete'] is not True:
            raise ValueError('validation technically incomplete; retain the actual attempt')
        write_json(root / 'summaries' / f'{collector}.json', result)
    write_json(case_root / 'v6-block-reference.json', {
        'study': STUDY, 'block_plan_sha256': sha(root / 'block-plan.json'),
        'blueprint_sha256': plan['blueprint_sha256'], 'golden_sha256': plan['golden_sha256'],
        'run_id': plan['run_id'], 'source': plan['source']})
    planned_publication = root / 'publications' / args.phase / f'{collector}-before-upload.json'
    write_json(planned_publication, {'closed_input_sha256': sha(case_root / 'closed-input.json'),
                                    'files': inventory(case_root)})
    status.update(status='complete', capture_complete=True)
    write_json(path, status)


def release(args):
    root = owned_root(args.root)
    plan = read(root / 'block-plan.json')
    collector = plan['arm_orders'][args.phase][args.slot]
    case = root / args.phase / collector
    expected = read(root / 'publications' / args.phase / f'{collector}-before-upload.json')
    if case.is_symlink() or case.resolve() != root / args.phase / collector:
        raise ValueError('foreign working copy')
    if inventory(case) != expected['files']:
        raise ValueError('working capture changed after its publication inventory')
    archive = root / 'deliveries' / args.phase / collector / 'capture.tar.gz'
    package = read(archive.with_suffix('.gz.json'))
    if package['files'] != expected['files'] or sha(archive) != package['sha256']:
        raise ValueError('the exact published capture package changed')
    value = api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{args.artifact_id}")
    artifact_identity(value, f"v6-{args.phase}-{collector}-{os.environ['GITHUB_RUN_ID']}",
                      args.artifact_id, args.artifact_digest)
    receipt = {'artifact_API': value, 'actual_publication_verified_ns': time.time_ns(),
               'closed_input_sha256': expected['closed_input_sha256'],
               'complete_local_inventory_sha256': sha(root / 'publications' / args.phase / f'{collector}-before-upload.json'),
               'working_copy_released': False}
    path = root / 'publications' / args.phase / f'{collector}.json'
    write_json(path, receipt)
    shutil.rmtree(case)
    archive.unlink()
    receipt.update(working_copy_released=True, released_ns=time.time_ns())
    write_json(path, receipt)


def package_capture(args):
    root = owned_root(args.root)
    plan = read(root / 'block-plan.json')
    collector = plan['arm_orders'][args.capture_phase][args.slot]
    case = root / args.capture_phase / collector
    if not case.is_dir() or case.is_symlink():
        raise ValueError('there is no owned capture to package')
    files = inventory(case)
    directories = [p.relative_to(case).as_posix() for p in case.rglob('*') if p.is_dir()]
    destination = root / 'deliveries' / args.capture_phase / collector / 'capture.tar.gz'
    destination.parent.mkdir(parents=True, exist_ok=True)
    pack(case, destination, files, directories)
    if inventory(case) != files:
        raise ValueError('capture changed while creating its lossless delivery')
    path = destination.with_suffix('.gz.json')
    package = read(path)
    package.update(study=STUDY, phase=args.capture_phase, collector=collector,
                   case=read(case / 'status.json') if (case / 'status.json').is_file() else None,
                   block_plan_sha256=sha(root / 'block-plan.json'),
                   run_id=int(os.environ['GITHUB_RUN_ID']), source=os.environ['GITHUB_SHA'])
    write_json(path, package)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf8') as f:
            f.write(f'archive_path={destination.as_posix()}\nmanifest_path={path.as_posix()}\n')


def restore_capture(args):
    root = owned_root(args.root)
    if any(root.iterdir()):
        raise FileExistsError('capture restoration requires an empty target')
    archive = Path(args.archive).resolve()
    if (Path(args.archive).is_symlink() or not archive.is_relative_to((repo() / 'work').resolve())
            or archive.name != 'capture.tar.gz'):
        raise ValueError('only the owned downloaded capture delivery can be restored')
    package = read(args.inventory)
    if (package.get('study'), package.get('phase'), package.get('collector'),
            package.get('run_id'), package.get('source')) != (
            STUDY, 'training', args.collector, int(os.environ['GITHUB_RUN_ID']), os.environ['GITHUB_SHA']):
        raise ValueError('capture package belongs to another actual source/cell')
    name = f"v6-training-{args.collector}-{os.environ['GITHUB_RUN_ID']}"
    values, page = [], 1
    while True:
        rows = api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}/artifacts?per_page=100&page={page}")['artifacts']
        values.extend(a for a in rows if a['name'] == name)
        if len(rows) < 100: break
        page += 1
    if len(values) != 1:
        raise ValueError('exactly one immutable original training publication required')
    artifact_identity(values[0], name)
    before = archive.stat()
    if before.st_size != package['bytes'] or sha(archive) != package['sha256']:
        raise ValueError('downloaded capture archive differs from its exact inventory')
    guard = unpack(archive, root, package['sha256'])
    if inventory(root) != package['files']:
        raise ValueError('restored capture files/bytes/SHA/modes differ')
    if read(root / 'status.json') != package['case']:
        raise ValueError('restored capture identity differs')
    after = archive.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('owned archive identity changed before release')
    archive.unlink()
    write_json(root / 'v6-training-publication-restored.json', {
        'artifact_API': values[0], 'archive_sha256': package['sha256'],
        'preextract_actual_disk_guard': guard,
        'inventory_sha256': sha(args.inventory), 'restored_all_bytes_SHA_modes': True,
        'owned_local_delivery_released': True, 'cloud_original_untouched': True})


def package_model(args):
    root = Path(args.root).resolve()
    saved = read(root / 'forecast-saved.json')
    status = saved['case']
    if saved['study'] != STUDY or status['phase'] != 'training':
        raise ValueError('only actual fresh frozen training models can be packaged')
    verify_files(root, saved['sha256_by_path'])
    paths = set(saved['sha256_by_path'])
    if any(p.startswith('toolchain/inputs/') for p in paths):
        raise ValueError('portable forecast freeze must exclude original prepared raw wire/value bodies')
    for name in ('forecast-saved.json', 'closed-input.json', 'status.json', 'plans.json',
                 'deployment.json', 'external.json', 'census.json', 'blocks.json',
                 'v6-block-reference.json', 'model-worker-resources.json',
                 'v6-training-publication-restored.json', 'capture-host-resources.json'):
        if (root / name).is_file(): paths.add(name)
    for folder in ('deployment', 'runtime-identity-v5'):
        for p in (root / folder).rglob('*'):
            relative = p.relative_to(root).as_posix()
            if p.is_file() and not p.is_symlink() and not relative.endswith(('.sqlite', '.tar', '.jsonl')):
                paths.add(relative)
    paths = {p for p in paths if (root / p).is_file()}
    target = Path(args.out).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    pack(root, target, paths, guard_compressed_writes=True)
    verify_files(root, saved['sha256_by_path'])
    capacity(target.parent, 0)


def processing_paths(root):
    if (root / 'forecast-saved.json').is_file():
        saved = read(root / 'forecast-saved.json')
        files = saved['complete_processing_sha256_by_path']
        paths = set(files) | {'forecast-saved.json'}
    else:
        paths = {p.relative_to(root).as_posix() for p in (root / 'toolchain').rglob('*') if p.is_file()}
    paths.update(p.relative_to(root).as_posix() for p in (root / 'runtime-identity-v5').rglob('*')
                 if p.is_file())
    paths.update(name for name in ('observation-index.sqlite', 'observation-index.sqlite-wal',
                 'observation-index.sqlite-shm', 'index-training.json',
                 'model-worker-resources.json', 'commands.jsonl', 'v6-block-reference.json',
                 'processing-execution.json',
                 'model-swap-resources.json',
                 'v6-training-publication-restored.json')
                 if (root / name).is_file())
    return paths


def publication_path(root, name):
    relative = Path(name)
    if (relative.is_absolute() or '..' in relative.parts or not relative.parts
            or re.search(r'[\\:"<>|*?\r\n]', name)):
        raise ValueError('processing path is incompatible with the artifact uploader')
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('processing publications require regular files without symlinks')
    return path


def processing_publication_preflight(root):
    for path in root.rglob('*'):
        if not path.is_dir():
            publication_path(root, path.relative_to(root).as_posix())


def package_processing(args):
    """Stage hard links for streaming upload, retaining bytes and reconstruction metadata."""
    root = Path(args.root).resolve()
    target = Path(args.out).absolute()
    work = (repo() / 'work').resolve()
    if (target.name != 'processing-publication' or target.exists()
            or any(p.is_symlink() for p in (target, *target.parents))
            or not target.resolve().is_relative_to(work)
            or target.resolve().is_relative_to(root) or not target.parent.is_dir()):
        raise ValueError('processing staging requires a new owned sibling directory')
    paths = processing_paths(root)
    if not paths:
        raise ValueError('no processing files to publish')
    capacity(target.parent, 0)
    if root.stat().st_dev != target.parent.stat().st_dev:
        raise ValueError('processing hard links require the same filesystem')
    target.mkdir()
    records = {}
    for name in sorted(paths):
        source = publication_path(root, name)
        before = source.stat()
        record = {'bytes': before.st_size, 'sha256': sha(source),
                  'mode': stat.S_IMODE(before.st_mode), 'mtime_ns': before.st_mtime_ns,
                  'device': before.st_dev, 'inode': before.st_ino}
        destination = target / 'files' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.link(source, destination, follow_symlinks=False)
        records[name] = record
    write_json(target / 'processing-manifest.json', {
        'schema': 'v6-direct-processing-publication-v1', 'files': records,
        'scope': 'COMPLETE_FROZEN' if (root / 'forecast-saved.json').is_file() else 'PARTIAL_UNFROZEN',
        'source_root': str(root), 'created_ns': time.time_ns(),
        'storage': 'streamed ZIP of hard links; restore original mode/mtime from this manifest',
        'execution': {'run_id': os.environ.get('GITHUB_RUN_ID'), 'source': os.environ.get('GITHUB_SHA')}})
    manifest_sha = sha(target / 'processing-manifest.json')
    verify_processing_publication(args, manifest_sha=manifest_sha)
    if os.environ.get('GITHUB_OUTPUT'):
        with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf8') as stream:
            stream.write(f'manifest_sha256={manifest_sha}\n')


def verify_processing_publication(args, *, manifest_sha=None):
    root, target = Path(args.root).resolve(), Path(args.out).absolute()
    manifest_path = target / 'processing-manifest.json'
    if (any(p.is_symlink() for p in (target, *target.parents))
            or not target.resolve().is_relative_to((repo() / 'work').resolve())
            or manifest_path.is_symlink() or sha(manifest_path) != (manifest_sha or args.manifest_sha256)):
        raise ValueError('processing publication manifest changed')
    manifest = read(manifest_path)
    if manifest['source_root'] != str(root) or set(manifest['files']) != processing_paths(root):
        raise ValueError('processing source census changed')
    frozen = read(root / 'forecast-saved.json')['complete_processing_sha256_by_path'] if (root / 'forecast-saved.json').is_file() else {}
    staged = {p.relative_to(target / 'files').as_posix() for p in (target / 'files').rglob('*') if not p.is_dir()}
    if staged != set(manifest['files']) or set(target.iterdir()) != {target / 'files', manifest_path}:
        raise ValueError('processing staging census changed')
    for name, expected in manifest['files'].items():
        source, linked = publication_path(root, name), publication_path(target / 'files', name)
        digest = sha(source)
        if name in frozen and digest != frozen[name]:
            raise ValueError('processing bytes differ from the frozen model')
        for path in (source, linked):
            actual = path.stat()
            record = {'bytes': actual.st_size, 'sha256': digest,
                      'mode': stat.S_IMODE(actual.st_mode), 'mtime_ns': actual.st_mtime_ns,
                      'device': actual.st_dev, 'inode': actual.st_ino}
            if record != expected:
                raise ValueError('processing source or hard link changed during publication')
    capacity(target.parent, 0)
    write_json(root / 'processing-publication-verification.json', {
        'verified_ns': time.time_ns(), 'manifest_sha256': sha(manifest_path),
        'all_bytes_SHA_modes_mtimes_and_source_links_verified': True,
        'phase': 'before_upload' if manifest_sha else 'after_upload'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('training', 'validation', 'release', 'package-model', 'package-processing', 'verify-processing-publication',
                                         'package-capture', 'restore-capture'))
    parser.add_argument('--system', choices=SYSTEMS)
    parser.add_argument('--mode', choices=MODES)
    parser.add_argument('--repetition', type=int, choices=REPETITIONS)
    parser.add_argument('--stage', choices=('qualification', 'main'), default='qualification')
    parser.add_argument('--full-size-qualification', action='store_true')
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--slot', type=int, choices=range(4))
    parser.add_argument('--capture-phase', choices=('training', 'validation'))
    parser.add_argument('--artifact-id', type=int)
    parser.add_argument('--artifact-digest')
    parser.add_argument('--collector', choices=COLLECTORS)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--inventory', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--manifest-sha256')
    args = parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('v6 phase execution is GitHub Actions only')
    root = owned_root(args.root)
    operation = args.phase
    cpu = lambda: {name: getattr(os.times(), name) for name in
                   ('user', 'system', 'children_user', 'children_system')}
    receipt = {'operation': operation, 'slot': args.slot, 'started_ns': time.time_ns(),
               'CPU_seconds_start': cpu(), 'status': 'started',
               'free_bytes_start': shutil.disk_usage(root).free,
               'CPU_scope': 'controller and waited subprocess accounting; excludes independently daemonized QEMU/remote guests'}
    try:
        if args.phase in ('package-model', 'package-processing'):
            if args.out is None: parser.error('--out is required')
            (package_model if args.phase == 'package-model' else package_processing)(args)
        elif args.phase == 'verify-processing-publication':
            if args.out is None or not args.manifest_sha256:
                parser.error('verification requires the exact staging directory and manifest SHA256')
            verify_processing_publication(args)
        elif args.phase == 'package-capture':
            if args.capture_phase is None or args.slot is None:
                parser.error('package-capture requires declared phase/slot')
            package_capture(args)
        elif args.phase == 'restore-capture':
            if not all((args.collector, args.archive, args.inventory)):
                parser.error('restore-capture requires exact archive/inventory/collector')
            restore_capture(args)
        elif args.phase == 'release':
            if args.capture_phase is None or args.slot is None or not args.artifact_id or not args.artifact_digest:
                parser.error('release requires exact phase, slot and actual upload artifact identity')
            args.phase = args.capture_phase
            release(args)
        else:
            if not all((args.system, args.mode, args.repetition)) or args.slot is None:
                parser.error('capture requires fixed block identity and slot')
            capture_slot(args)
        receipt['status'] = 'complete'
    except BaseException as error:
        receipt.update(status='failed', error=repr(error))
        raise
    finally:
        receipt.update(ended_ns=time.time_ns(), CPU_seconds_end=cpu(),
                       free_bytes_end=shutil.disk_usage(root).free)
        with (root / 'block-controller-cost.jsonl').open('a', encoding='utf8') as f:
            f.write(json.dumps(receipt) + '\n')


if __name__ == '__main__':
    main()
