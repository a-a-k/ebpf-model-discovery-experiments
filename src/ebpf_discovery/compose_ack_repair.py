"""Finite prospective ACK repair: original graphs, new freezes, fresh targets.

No acquisition/model discovery is performed here. Large bodies remain on the
Actions worker and are published with exact byte/SHA receipts to one Release.
"""
from __future__ import annotations

import argparse
import calendar
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import zipfile

import requests

from . import block_v6 as b
from . import compose_ack_contract as contract
from .publication_archive import GitHub, Release, file_digest, require
from .runtime import Context, write_json
from .study_v6 import Case, verify_files
from .validation_v6 import classify, require_forecast


PLAN = Path('docs/compose-ack-correction-plan.json')
ARMS = ('none', 'obi', 'coroot', 'deepflow')
REPO = 'a-a-k/ebpf-model-discovery-experiments'


def record():
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == REPO,
            'scientific execution is repository Actions only')
    value = b.read(PLAN)
    require(value['fresh_cells'] == 36 and len(value['blocks']) == 9 and
            {tuple(v['key']) for v in value['blocks']} ==
            {('deathstarbench', m, r) for m in ('absent', 'partial', 'full') for r in (9, 10, 11)},
            'fixed complete correction scope required')
    require(all(set(v['arms']) == set(ARMS) for v in value['blocks']), 'all four runtime arms required')
    return value


def selected(plan, mode, repetition):
    matches = [v for v in plan['blocks'] if v['key'] == ['deathstarbench', mode, repetition]]
    require(len(matches) == 1, 'unknown/ambiguous correction block')
    return matches[0]


def output(**values):
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf8') as stream:
        for key, value in values.items():
            stream.write(f'{key}={value}\n')


def asset_identity(asset):
    return {k: asset[k] for k in ('id', 'name', 'size', 'digest', 'state')}


def download_asset(github, asset, path):
    require(asset['state'] == 'uploaded' and asset['digest'].startswith('sha256:'), 'unverified Release asset')
    github.download(f"releases/assets/{asset['id']}", path, asset['size'], asset['digest'][7:])


def package_import(github, expected, folder, kind, target):
    """Verify original outer ZIP, original package inventory and every member."""
    folder, target = Path(folder), Path(target)
    folder.mkdir(parents=True)
    actual = github.json(f"actions/artifacts/{expected['id']}")
    require(all(actual[k] == expected[k] for k in ('id', 'name', 'size_in_bytes', 'digest')) and
            actual['workflow_run'] == expected['workflow_run'] and not actual['expired'], 'original publication identity differs')
    archive = folder / 'original.zip'
    github.download(f"actions/artifacts/{actual['id']}/zip", archive, actual['size_in_bytes'], actual['digest'][7:])
    wanted = (kind + '.tar.gz', kind + '.tar.gz.json')
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        require(len(names) == len(set(names)) and all(name in names for name in wanted), 'original package members differ')
        for name in wanted:
            with zipped.open(name) as source, (folder / name).open('xb') as stream:
                shutil.copyfileobj(source, stream, 1024**2)
        if kind == 'shared':
            for name in ('shared-seal.json', 'block-plan.json'):
                (folder / name).write_bytes(zipped.read(name))
        require(zipped.testzip() is None, 'original outer ZIP CRC differs')
    archive.unlink()
    package = b.read(folder / wanted[1])
    guard = b.unpack(folder / wanted[0], target, package['sha256'], guard_root=folder.parent,
                     expected_inventory=package)
    require(b.inventory(target) == package['files'], 'original package complete inventory differs')
    # Only verified working delivery copies are released; original publications
    # are never deleted. The unpacked source is owned by this fresh worker.
    (folder / wanted[0]).unlink()
    write_json(folder / 'verified-import.json', {'artifact': actual, 'package': package,
                                                'preextract_disk_guard': guard})
    return package


def owned_model(github, arm, destination):
    destination = Path(destination)
    package_import(github, arm['artifact'], destination.parent / (destination.name + '-delivery'), 'model', destination)
    require(file_digest(destination / 'forecast-saved.json') == arm['original_forecast_manifest_sha256'],
            'original canonical forecast manifest differs')
    case = arm['original_capture_case']
    frozen = require_forecast(destination, case['system'], case['mode'], case['seed'], case['collector'],
                              smoke=False, stage=case['stage'])
    require(frozen['case'] == case, 'original captured identity differs')
    return frozen


def make_zip(folder, target):
    folder, target = Path(folder), Path(target)
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                require(not path.is_symlink(), 'no links in corrected forecast package')
                archive.write(path, path.relative_to(folder).as_posix())


def read_freeze(path, expected_block, *, source=None):
    with zipfile.ZipFile(path) as archive:
        value = json.loads(archive.read('freeze.json'))
        require(value['key'] == expected_block['key'] and value['plan_sha256'] == file_digest(PLAN) and
                value['parent_run_id'] == expected_block['parent_run_id'] and
                set(value['arms']) == set(ARMS), 'foreign/incomplete corrected freeze')
        if source:
            require(value['execution_source'] == source, 'corrected freeze implementation differs')
        require(value['execution_run_id'] == os.environ['GITHUB_RUN_ID'], 'foreign correction run')
        names = archive.namelist()
        require(len(names) == len(set(names)) and set(names) == {'freeze.json', *value['files']}, 'freeze member set differs')
        for name, identity in value['files'].items():
            body = archive.read(name)
            require(len(body) == identity['bytes'] and hashlib.sha256(body).hexdigest() == identity['sha256'],
                    'corrected frozen member bytes differ')
        for arm, provenance in value['arms'].items():
            require(provenance['original_model_artifact'] == expected_block['arms'][arm]['artifact'] and
                    provenance['original_forecast_manifest_sha256'] == expected_block['arms'][arm]['original_forecast_manifest_sha256'],
                    'corrected forecast origin differs')
        return value


def prepare(github, root):
    plan = record()
    marker = 'ACK-correction-plan-sha256: ' + file_digest(PLAN)
    tag = 'compose-ack-correction-' + os.environ['GITHUB_RUN_ID']
    try:
        info = github.json('releases/tags/' + tag)
    except requests.HTTPError as error:
        if error.response.status_code != 404:
            raise
        info = github.request('POST', 'releases', json={
            'tag_name': tag, 'target_commitish': os.environ['GITHUB_SHA'], 'draft': True,
            'name': 'Prospective correction of the Social Network ACK contract',
            'body': marker + '\n\nExact original observed models and new contract forecasts before fresh independent targets for all 36 Social Network cells and all three operations. HTTP ACK is distinct from MongoDB storage or durability. Unknown/unavailable forecasts and adverse outcomes are retained. No forecasting or effort superiority is assumed.'}).json()
    require(info['target_commitish'] == os.environ['GITHUB_SHA'] and marker in info['body'], 'foreign correction Release')
    release = Release(github, info['id'])
    bundle = root / 'registered-inputs.zip'
    sources = (PLAN.as_posix(), 'src/ebpf_discovery/compose_ack_contract.py',
               'src/ebpf_discovery/compose_ack_repair.py', '.github/workflows/compose-ack-correction.yml')
    if bundle.name in release.assets:
        download_asset(github, release.assets[bundle.name], bundle)
        with zipfile.ZipFile(bundle) as archive:
            require(set(archive.namelist()) == set(sources) and all(
                archive.read(name) == Path(name).read_bytes() for name in sources), 'existing registered source bundle differs')
    else:
        with zipfile.ZipFile(bundle, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sources:
                archive.write(name, name)
    release.publish(bundle)
    write_json(root / 'release.json', info)
    output(release_id=release.id, release_tag=tag)


def freeze(github, release, root, block):
    mode, repetition = block['key'][1:]
    filename = f'freeze-{mode}-{repetition}.zip'
    saved_asset = release.assets.get(filename)
    if saved_asset:
        path = root / filename
        download_asset(github, saved_asset, path)
        read_freeze(path, block, source=os.environ['GITHUB_SHA'])
        write_json(root / 'reused-freeze.json', asset_identity(saved_asset))
        return
    folder = root / 'corrected'
    folder.mkdir()
    tools = Path(os.environ['PBS_BIN']).resolve().parent
    build = b.read(tools / 'toolchain-build.json')
    from .toolchain_v5 import PINS
    for name, pin in (('bering', PINS['Bering']), ('sheaft', PINS['Sheaft'])):
        actual = next(row for row in build['binaries'] if row['name'] == name)
        require(actual['commit'] == pin and file_digest(tools / 'bin' / name) == actual['binary_sha256'],
                'actual product binary differs from approved pin/build receipt')
    shutil.copyfile(tools / 'toolchain-build.json', folder / 'actual-toolchain-build.json')
    shutil.copyfile(tools / 'builds.tsv', folder / 'actual-toolchain-builds.tsv')
    provenance = {}
    for arm in ARMS:
        model = root / 'original' / arm
        historical = owned_model(github, block['arms'][arm], model)
        ctx = Context(root / 'compiler-cost' / arm, mode, repetition)
        started = time.time_ns()
        contract.compile_forecasts(model, folder / arm, ctx)
        verify_files(model, historical['sha256_by_path'])
        require(file_digest(model / 'forecast-saved.json') == block['arms'][arm]['original_forecast_manifest_sha256'],
                'original forecast header changed during rebinding')
        provenance[arm] = {'original_model_artifact': block['arms'][arm]['artifact'],
                           'original_forecast_manifest_sha256': block['arms'][arm]['original_forecast_manifest_sha256'],
                           'original_capture_case': historical['case'], 'started_ns': started,
                           'ended_ns': time.time_ns(), 'old_inputs_and_forecasts_changed': False}
        # Input inventory has already been fully verified and its origin sealed.
        # Release only this owned, disposable unpacked model; keep new outputs.
        require(model.resolve().is_relative_to(root.resolve() / 'original'), 'model cleanup escapes owned root')
        shutil.rmtree(model)
    files = {p.relative_to(folder).as_posix(): {'bytes': p.stat().st_size, 'sha256': file_digest(p)}
             for p in folder.rglob('*') if p.is_file()}
    value = {'study': plan_name(), 'key': block['key'], 'parent_run_id': block['parent_run_id'],
             'plan_sha256': file_digest(PLAN), 'execution_source': os.environ['GITHUB_SHA'],
             'execution_run_id': os.environ['GITHUB_RUN_ID'], 'compiler_host_boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
             'saved_ns': time.time_ns(), 'arms': provenance, 'files': files,
             'historical_graphs_reused_without_Bering_discovery': True, 'targets_started': False}
    write_json(folder / 'freeze.json', value)
    archive = root / filename
    make_zip(folder, archive)
    read_freeze(archive, block, source=os.environ['GITHUB_SHA'])
    receipt = release.publish(archive)
    write_json(root / 'published-freeze.json', receipt)


def plan_name():
    return 'compose-ack-contract-correction'


def barrier(github, release, root, plan):
    entries = []
    for block in plan['blocks']:
        name = f"freeze-{block['key'][1]}-{block['key'][2]}.zip"
        require(name in release.assets, 'all nine corrected blocks must freeze before any target')
        asset = release.assets[name]
        path = root / name
        download_asset(github, asset, path)
        value = read_freeze(path, block, source=os.environ['GITHUB_SHA'])
        entries.append({'key': block['key'], 'asset': asset_identity(asset), 'saved_ns': value['saved_ns'],
                        'original_parent_run': block['parent_run_id']})
    name = 'all-nine-blocks-frozen.json'
    existing = release.assets.get(name)
    path = root / name
    if existing:
        download_asset(github, existing, path)
        value = b.read(path)
        require(value['blocks'] == entries and value['execution_source'] == os.environ['GITHUB_SHA'], 'existing barrier differs')
        receipt = existing
    else:
        value = {'study': plan_name(), 'plan_sha256': file_digest(PLAN), 'execution_source': os.environ['GITHUB_SHA'],
                 'execution_run_id': os.environ['GITHUB_RUN_ID'], 'saved_ns': time.time_ns(),
                 'all_36_forecasts_before_any_target': True, 'blocks': entries}
        write_json(path, value)
        receipt = release.publish(path)
    output(barrier_asset_id=receipt['id'], barrier_bytes=receipt['size'], barrier_sha256=receipt['digest'][7:])


def counts(records):
    from .evaluate_v4 import _counts
    require(all(r.get('success') is True or r.get('success') is False or r.get('success') is None
                for r in records), 'invalid external outcome value')
    return _counts(records)


def project_targets(forecasts, direct, records, status):
    from .study import workload_counts
    from .evaluate_v4 import _bounds, _error
    expected = workload_counts(3, False)
    expected_phases = {'target': 8 * expected['target'], 'class_test': expected['class_test'],
                       'db_up': expected['database'], 'db_down': expected['database']}
    phase_counts = Counter(r['phase'] for r in records)
    require(all(phase_counts[p] == n for p, n in expected_phases.items()), 'fresh target phase coverage differs')
    rows = []
    for operation in contract.OPERATIONS:
        actual = [r for r in records if r['phase'] == 'target' and r['operation'] == operation]
        require(len(actual) == 8 * expected['target'] // 3, 'unbalanced fresh operation coverage')
        by_state = {s: counts([r for r in actual if r['state'] == s]) for s in ('11', '10', '01', '00')}
        require({s: v['total'] for s, v in by_state.items()} ==
                {s: expected['target'] // 3 * n for s, n in [('11', 4), ('10', 2), ('01', 1), ('00', 1)]},
                'fresh replica state law differs')
        db_up = counts([r for r in records if r['phase'] == 'db_up' and r['operation'] == operation])
        db_down = counts([r for r in records if r['phase'] == 'db_down' and r['operation'] == operation])
        position = contract.OPERATIONS.index(operation)
        operation_db_count = len(range(position, expected['database'], len(contract.OPERATIONS)))
        require(db_up['total'] == db_down['total'] == operation_db_count, 'fresh DB control coverage differs')
        for source, views in forecasts.items():
            for view, values in views.items():
                forecast = values[operation]
                observed = counts(actual)
                primary = forecast['prediction'] if forecast['available'] else None
                db = forecast.get('database_forecast') or {}
                rows.append({'operation': operation, 'source': source, 'view': view,
                             'primary_forecast': forecast, 'direct_baseline': direct[operation],
                             'observed': observed, 'by_state': by_state, 'db_up': db_up, 'db_down': db_down,
                             'primary_error': _error(primary, _bounds(observed)),
                             'database_down_error': _error(db.get('prediction') if db.get('available') else None, _bounds(db_down)),
                             'direct_primary_error': _error(direct[operation]['prediction'], _bounds(observed)),
                             'direct_database_down_error': _error(direct[operation]['database']['database_down_prediction'], _bounds(db_down))})
    return {'study': plan_name(), 'status': status, 'technical_complete': True, 'rows': rows,
            'row_count': len(rows), 'all_retained_phase_counts': dict(phase_counts),
            'source_views_share_external_attempts': True,
            'scientific_misses_are_results_not_technical_retry_reasons': True,
            'target_outcomes_fit_forecasts': False, 'write_or_durability_evidence': False}


def validate(github, release, root, plan, block, arm, args):
    barrier_path = root / 'all-nine-blocks-frozen.json'
    github.download(f'releases/assets/{args.barrier_asset_id}', barrier_path, args.barrier_bytes, args.barrier_sha256)
    all_frozen = b.read(barrier_path)
    require(all_frozen['plan_sha256'] == file_digest(PLAN) and all_frozen['execution_source'] == os.environ['GITHUB_SHA'] and
            all_frozen['execution_run_id'] == os.environ['GITHUB_RUN_ID'] and
            all_frozen['all_36_forecasts_before_any_target'] is True and len(all_frozen['blocks']) == 9 and
            {tuple(r['key']) for r in all_frozen['blocks']} == {tuple(b['key']) for b in plan['blocks']},
            'qualified all36 prospective barrier required')
    row = next(r for r in all_frozen['blocks'] if r['key'] == block['key'])
    frozen_zip = root / row['asset']['name']
    download_asset(github, row['asset'], frozen_zip)
    frozen = read_freeze(frozen_zip, block, source=os.environ['GITHUB_SHA'])
    require(row['saved_ns'] == frozen['saved_ns'], 'barrier and selected freeze time differ')
    with zipfile.ZipFile(frozen_zip) as archive:
        forecasts = json.loads(archive.read(arm + '/forecasts.json'))
        direct = json.loads(archive.read(arm + '/direct-baselines.json'))
    model = root / 'original' / arm
    original = owned_model(github, block['arms'][arm], model)
    package = package_import(github, block['shared_artifact'], root / 'shared-delivery', 'shared', root / 'deployment')
    deploy = root / 'deployment'
    shared_plan = b.read(deploy / 'block-plan.json') if (deploy / 'block-plan.json').exists() else b.read(root / 'shared-delivery/block-plan.json')
    require(b.sha(deploy / 'blueprint/blueprint.json') == original['case']['blueprint_sha256'] == shared_plan['blueprint_sha256'] and
            b.sha(deploy / 'vms/golden/manifest.json') == shared_plan['golden_sha256'], 'original sealed deployment identity differs')
    label = f"ack-{block['key'][1]}-{block['key'][2]}-{arm}"
    capture = root / 'capture'
    try:
        b.vms(deploy, 'start', label, shared_plan['golden_sha256'])
        case = Case(capture, 'deathstarbench', block['key'][1], block['key'][2], arm, 'validation',
                    smoke=False, stage=original['case']['stage'], vm_dir=deploy / 'vms/active')
        require(max(frozen['saved_ns'], all_frozen['saved_ns']) < case.status['started_ns'], 'forecasts must precede fresh target deployment')
        require(case.status['runner_boot_id'] != original['case']['runner_boot_id'], 'validation reused an original capture host')
        case.status['correction_series'] = plan_name()
        case.status['correction_allocation_regime'] = 'one runtime arm per independent target worker'
        case.status['original_capture_case'] = original['case']
        name = f"target {block['key'][1]}/{block['key'][2]}/{arm}"
        jobs = github.pages(f"actions/runs/{os.environ['GITHUB_RUN_ID']}/jobs?filter=all", 'jobs')
        producer = [j for j in jobs if j['name'] == name and j['status'] == 'in_progress' and
                    j['run_attempt'] == int(os.environ['GITHUB_RUN_ATTEMPT']) and j['head_sha'] == os.environ['GITHUB_SHA']]
        require(len(producer) == 1, 'exact current target producer job required')
        case.status['producing_job'] = {'id': producer[0]['id'], 'name': name,
                                       'attempt': int(os.environ['GITHUB_RUN_ATTEMPT'])}
        shutil.copyfile('work/host-resources.json', capture / 'capture-host-resources.json')
        write_json(capture / 'block-freeze-verified-before-capture.json', all_frozen)
        case.capture(deploy / 'blueprint', shared_plan['blueprint_sha256'])
    finally:
        b.stop_and_discard(deploy, label)
    from .capture_checks_v6 import verify_capture
    closed = verify_capture(capture, 'validation')
    require(closed['status']['status'] == 'capture_complete', 'new target capture is technically incomplete')
    class_result = classify(model, capture, original)
    verify_files(capture, closed['files'])
    result = project_targets(forecasts, direct, b.read(capture / 'external.json'), closed['status'])
    commands = [json.loads(line) for line in (deploy / 'block-vm-commands.jsonl').read_text().splitlines() if line.strip()]
    commands = [row for row in commands if row['label'] == label]
    require([row['action'] for row in commands] == ['start', 'stop', 'discard'] and
            all(row['exit_status'] == 0 for row in commands) and commands[0]['started_ns'] > all_frozen['saved_ns'],
            'fresh guest lifecycle does not follow the corrected forecast barrier')
    class_file = capture / 'class-evaluation/classes-v5.json'
    omitted = [{'field': name, 'items': len(class_result[name])} for name in
               ('class_test_assignments', 'target_descriptive_assignments') if name in class_result]
    class_projection = {k: v for k, v in class_result.items()
                        if k not in ('class_test_assignments', 'target_descriptive_assignments')}
    result.update(freeze_asset=row['asset'], all36_barrier={'asset_id': args.barrier_asset_id,
                  'bytes': args.barrier_bytes, 'sha256': args.barrier_sha256},
                  original_model=block['arms'][arm], fresh_guest_lifecycle=commands,
                  frozen_classification_applied_without_refit=class_projection,
                  classification_array_omissions=omitted,
                  full_classification_in_raw_capture={'path': class_file.relative_to(capture).as_posix(),
                                                       'bytes': class_file.stat().st_size, 'sha256': file_digest(class_file)})
    write_json(root / 'result.json', result)


def publish_raw(release, path, *, max_asset_bytes=2 * 1024**3, chunk_bytes=1024**3):
    """Lossless platform-size fallback; never repeat targets to repackage data."""
    path = Path(path)
    size, sha = path.stat().st_size, file_digest(path)
    if size < max_asset_bytes:
        return {'original_bytes': size, 'original_sha256': sha, 'asset': asset_identity(release.publish(path))}
    require(0 < chunk_bytes < max_asset_bytes, 'invalid platform chunk size')
    parts = []
    joined = hashlib.sha256()
    with path.open('rb') as source:
        index = 0
        while source.tell() < size:
            target = path.with_name(path.name + f'.part{index:04d}')
            b.capacity(path.parent, min(chunk_bytes, size - source.tell()))
            offset, left = source.tell(), chunk_bytes
            with target.open('xb') as output_stream:
                while left and (body := source.read(min(left, 4 * 1024**2))):
                    joined.update(body)
                    output_stream.write(body)
                    left -= len(body)
            parts.append({'offset': offset, 'asset': asset_identity(release.publish(target))})
            target.unlink()  # Verified disposable part; the complete source tar remains.
            index += 1
    require(joined.hexdigest() == sha and sum(p['asset']['size'] for p in parts) == size,
            'lossless chunk reassembly identity differs')
    manifest = path.with_name(path.name + '.chunks.json')
    write_json(manifest, {'original_name': path.name, 'original_bytes': size, 'original_sha256': sha,
                          'reassembly': 'Concatenate listed parts in order, then verify original bytes/SHA256.', 'parts': parts})
    return {'original_bytes': size, 'original_sha256': sha, 'parts': parts,
            'chunks_manifest_asset': asset_identity(release.publish(manifest))}


def publish_target(release, root, args, error):
    stem = f"target-{args.mode}-{args.repetition}-{args.collector}-attempt{os.environ['GITHUB_RUN_ATTEMPT']}"
    evidence = root / 'capture'
    raw_data = None
    if evidence.exists():
        raw = root / (stem + '.tar.gz')
        paths = {p.relative_to(evidence).as_posix() for p in evidence.rglob('*') if p.is_file() and not p.is_symlink()}
        b.pack(evidence, raw, paths, guard_compressed_writes=True)
        raw_data = publish_raw(release, raw)
        release.publish(raw.with_name(raw.name + '.json'))
    receipt = {'mode': args.mode, 'repetition': args.repetition, 'collector': args.collector,
               'source': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
               'attempt': int(os.environ['GITHUB_RUN_ATTEMPT']), 'error': repr(error) if error else None,
               'raw_data': raw_data,
               'result': b.read(root / 'result.json') if (root / 'result.json').exists() else None}
    path = root / (stem + '.json')
    write_json(path, receipt)
    release.publish(path)


def step_interval_ns(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)
    return calendar.timegm(date.utctimetuple()) * 10**9 + date.microsecond * 1000


def select_actual_publication(attempts, jobs):
    """Use actual capture clocks, not later reused-successful API attempt labels."""
    valid = []
    for attempt in attempts:
        receipt = attempt['receipt']
        result = receipt.get('result') or {}
        if receipt['error'] is not None or result.get('technical_complete') is not True:
            continue
        status = result['status']
        matches = []
        for job in jobs:
            if job['status'] != 'completed' or job['conclusion'] != 'success':
                continue
            for step in job.get('steps', []):
                if (step['name'] == 'Capture fresh independent targets from the original sealed blueprint' and
                        step['status'] == 'completed' and step['conclusion'] == 'success' and
                        step_interval_ns(step['started_at']) <= status['started_ns'] <= status['ended_ns'] <
                        step_interval_ns(step['completed_at']) + 10**9):
                    matches.append(job)
                    break
        if matches:
            preferred = [j for j in matches if j['id'] == status.get('producing_job', {}).get('id')]
            producer = (preferred or sorted(matches, key=lambda j: (j['run_attempt'], j['id'])))[0]
            valid.append((status['started_ns'], attempt, producer, matches))
    require(valid, 'no published successful target matches an actual executed step interval')
    _, chosen, producer, aliases = max(valid, key=lambda value: value[0])
    return chosen, producer, aliases


def summarize(github, release, root, plan):
    """Select successful technical job attempts, retain every other attempt."""
    jobs = github.pages(f"actions/runs/{os.environ['GITHUB_RUN_ID']}/jobs?filter=all", 'jobs')
    cases, all_attempts = [], []
    for block in plan['blocks']:
        mode, repetition = block['key'][1:]
        for arm in ARMS:
            name = f'target {mode}/{repetition}/{arm}'
            actual = [j for j in jobs if j['name'] == name and j['conclusion'] == 'success' and
                      j['status'] == 'completed' and j['head_sha'] == os.environ['GITHUB_SHA']]
            require(actual, 'missing completed technical target job: ' + name)
            prefix = f'target-{mode}-{repetition}-{arm}-attempt'
            attempts = []
            for asset in release.assets.values():
                if re.fullmatch(re.escape(prefix) + r'[1-9][0-9]*\.json', asset['name']):
                    path = root / asset['name']
                    download_asset(github, asset, path)
                    receipt = b.read(path)
                    require(receipt['source'] == os.environ['GITHUB_SHA'] and
                            (receipt['mode'], receipt['repetition'], receipt['collector']) == (mode, repetition, arm),
                            'foreign target publication')
                    attempts.append({'asset': asset_identity(asset), 'receipt': receipt})
            all_attempts.extend({'asset': a['asset'], 'key': [*block['key'], arm],
                                 'attempt': a['receipt']['attempt'], 'error': a['receipt']['error'],
                                 'result_retained_at_exact_receipt_asset': True} for a in attempts)
            chosen, job, aliases = select_actual_publication(attempts, actual)
            cases.append({'key': [*block['key'], arm], 'producing_job_API': job,
                          'capture_producer': chosen['receipt']['result']['status'].get('producing_job'),
                          'all_matching_successful_job_API_aliases': aliases,
                          'publication': chosen['asset'], 'published_attempt': chosen['receipt']['attempt'],
                          'result': chosen['receipt']['result']})
    require(len(cases) == 36 and sum(c['result']['row_count'] for c in cases) == 864, 'fixed36/864 coverage differs')
    value = {'study': plan_name(), 'source': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
             'status': 'complete', 'plan_sha256': file_digest(PLAN), 'cases': cases,
             'all_target_attempts': all_attempts, 'job_API_receipts_at_finite_pre_summary_cut': jobs,
             'counts': {'fresh_cases': 36, 'case_operation_sets': 108, 'source_view_rows': 864},
             'source_views_are_not_independent_repetitions': True, 'known_targets_were_not_used_to_fit_new_forecasts': True,
             'original_results_modified': False, 'new_graph_discovery': False,
             'corrected_forecasts_before_fresh_targets': True, 'write_or_durability_evidence': False,
             'complete_comparable_cost_comparison': False, 'human_seconds': None,
             'summary_and_later_delivery_costs_outside_finite_job_cut_are_not_zero': True}
    path = root / f"prospective-results-attempt{os.environ['GITHUB_RUN_ATTEMPT']}.json"
    write_json(path, value)
    asset = release.publish(path)
    published = github.request('PATCH', f'releases/{release.id}', json={'draft': False}).json()
    require(not published['draft'], 'correction results release did not publish')
    print(json.dumps({'result_asset': asset_identity(asset), 'release_url': published['html_url'],
                      'counts': value['counts']}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'freeze', 'barrier', 'validate', 'summarize'))
    parser.add_argument('--release-id', type=int)
    parser.add_argument('--mode', choices=('absent', 'partial', 'full'))
    parser.add_argument('--repetition', type=int, choices=(9, 10, 11))
    parser.add_argument('--collector', choices=ARMS)
    parser.add_argument('--barrier-asset-id', type=int)
    parser.add_argument('--barrier-bytes', type=int)
    parser.add_argument('--barrier-sha256')
    args = parser.parse_args()
    plan = record()
    root = Path('work/ack-correction').resolve()
    root.mkdir(parents=True, exist_ok=True)
    github = GitHub()
    started = time.time_ns()
    error = None
    release = None
    try:
        if args.command == 'prepare':
            prepare(github, root)
        else:
            require(args.release_id, 'exact correction Release required')
            info = github.json(f'releases/{args.release_id}')
            require(info['tag_name'] == 'compose-ack-correction-' + os.environ['GITHUB_RUN_ID'] and
                    info['target_commitish'] == os.environ['GITHUB_SHA'] and
                    'ACK-correction-plan-sha256: ' + file_digest(PLAN) in info['body'], 'foreign correction Release/source')
            release = Release(github, args.release_id)
            if args.command == 'summarize':
                summarize(github, release, root, plan)
            elif args.command == 'barrier':
                barrier(github, release, root, plan)
            else:
                block = selected(plan, args.mode, args.repetition)
                if args.command == 'freeze':
                    freeze(github, release, root, block)
                else:
                    require(args.collector and args.barrier_asset_id and args.barrier_bytes and args.barrier_sha256,
                            'validation needs its exact arm and global prospective barrier')
                    validate(github, release, root, plan, block, args.collector, args)
    except BaseException as exc:
        error = exc
        raise
    finally:
        publication_error = None
        if args.command == 'validate' and release:
            try:
                publish_target(release, root, args, error)
            except BaseException as exc:
                publication_error = exc
        cost = {'command': args.command, 'source': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
                'attempt': int(os.environ['GITHUB_RUN_ATTEMPT']), 'started_ns': started, 'ended_ns': time.time_ns(),
                'status': 'failed' if error or publication_error else 'complete', 'error': repr(error) if error else None,
                'publication_error': repr(publication_error) if publication_error else None,
                'API_requests': github.calls, 'human_seconds': None, 'complete_comparable_cost_comparison': False,
                'free_disk_bytes': shutil.disk_usage(root).free,
                'host': {'CPUs': sorted(os.sched_getaffinity(0)), 'memory': Path('/proc/meminfo').read_text()},
                'later_Actions_artifact_poststeps_accounted_by_whole_worker_API_interval': True}
        write_json(root / 'execution-cost.json', cost)
        if publication_error is not None and error is None:
            raise publication_error


if __name__ == '__main__':
    main()
