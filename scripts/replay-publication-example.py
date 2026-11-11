#!/usr/bin/env python3
"""Retrospective replay of one retained example, in GitHub Actions only.

The historical implementation constructs the graph, resolves the supplied
contracts and executes Sheaft. This harness verifies and compares artifacts;
it never supplies missing edges, changes a contract or fits an outcome.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import csv
import gzip
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import resource
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import threading
import time
import traceback
from types import SimpleNamespace
import zipfile

import requests

SOURCE = 'b913a5df7be680c5e6ede001d0f8eb6fb856a4ed'
PRODUCER_RUN = 42347357851
KEY = ['otel_demo', 'absent', 9, 'obi']
ZENODO = 'https://zenodo.org/api/records/24131735/files/ebpf-model-discovery-artifact-v1.0.zip/content'
REPOSITORY = 'a-a-k/ebpf-model-discovery-experiments'
OUTER = (13834388706, 1079616429, '589abd24ce48d28b5b0bdb8fd348ed1ba8efe2efb00abc38f720132cc1ae086b')
CORE = (3165309, '47d9c9a07efc45a9d127a9f0a718a6acc90197c94a878eb6b74548e805b641fa')
EXAMPLE = (1076445237, '4e029a494967435dd199777982afad785611a4ba46a5f6f09bb3699ed2d7c1cd')
TRAINING = (13565862245, 329226484, 'f910fb03380e6e7ad0c60c4f1e14e8fa7f1858dbcffba9eb37710ba3d9990efb')
MODEL = (13567701925, 747216214, '19099f3bdc275fc595c6e819ce010f1da1536152feca3069a1e5333f2389f662')
FREEZE = 'e820f17d4e670e5b0e22ab0c73f362ec7f991e8c3bec45f09c42386f0724f2b3'
OPS = ('browse_product', 'add_to_cart', 'checkout')
DISCOVERY = 'toolchain/discovery/ebpf/network_scope/'
OPERATIONS = 'toolchain/ebpf/network_scope/'
ARCHIVE_DOWNLOAD_BUDGET = 6_000_000_000
RESERVE = 4 * 1024**3
RETAINED_OUTPUT_BUDGET = 64 * 1024**2



def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def reference(path):
    path = Path(path)
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)}


def verify(path, size, sha):
    require(Path(path).stat().st_size == size, 'byte count differs: ' + str(path))
    require(digest(path) == sha, 'SHA256 differs: ' + str(path))


def safe_name(name):
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and '..' not in path.parts and '\\' not in name,
            'unsafe archive member: ' + name)
    return path


def capacity(path, needed):
    require(shutil.disk_usage(path).free >= needed + RESERVE,
            f'insufficient disk for {needed} bytes plus {RESERVE} reserve')


def sanitized(value):
    # Never retain object-store signature queries in failed-download diagnostics.
    return re.sub(r'(https?://[^\s?\"\']+)\?[^\s\"\']+', r'\1?[redacted]', str(value))


class DownloadBudget:
    def __init__(self, receipt):
        self.receipt = Path(receipt)
        self.value = read(receipt) if self.receipt.exists() else {
            'maximum_archive_response_bytes': ARCHIVE_DOWNLOAD_BUDGET,
            'consumed_archive_response_bytes': 0, 'attempts': []}

    def save(self):
        write(self.receipt, self.value)

    def download(self, url, target, size, sha, label):
        require(self.value['consumed_archive_response_bytes'] + size <= ARCHIVE_DOWNLOAD_BUDGET,
                'aggregate archive download budget would be exceeded')
        capacity(target.parent, size)
        attempt = {'source': label, 'expected_bytes': size, 'expected_sha256': sha,
                   'started_ns': time.time_ns(), 'received_bytes': 0, 'status': 'started'}
        self.value['attempts'].append(attempt)
        self.save()
        try:
            # No token is sent to Zenodo or a temporary object-store URL.
            with requests.get(url, stream=True, timeout=(30, 180)) as response:
                response.raise_for_status()
                require(response.status_code == 200, 'whole-file download requires HTTP 200')
                length = response.headers.get('Content-Length')
                require(length is None or int(length) == size, 'download Content-Length differs')
                hasher = hashlib.sha256()
                with target.open('xb') as output:
                    for block in response.iter_content(1024**2):
                        if not block:
                            continue
                        attempt['received_bytes'] += len(block)
                        self.value['consumed_archive_response_bytes'] += len(block)
                        require(attempt['received_bytes'] <= size and
                                self.value['consumed_archive_response_bytes'] <= ARCHIVE_DOWNLOAD_BUDGET,
                                'download exceeds its declared size or collective budget')
                        output.write(block)
                        hasher.update(block)
                attempt['actual_sha256'] = hasher.hexdigest()
                require((attempt['received_bytes'], hasher.hexdigest()) == (size, sha),
                        'downloaded artifact does not match independently pinned bytes/SHA')
                attempt['status'] = 'verified'
        except Exception as exc:
            attempt.update(status='failed', error_type=type(exc).__name__)
            # Exception text from HTTP libraries can contain signed URLs.
            raise
        finally:
            attempt['ended_ns'] = time.time_ns()
            self.save()


def github_artifact(aid, expected_size, expected_sha, budget, target):
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    require(token, 'GitHub artifact fallback requires a read-only Actions token')
    base = f'https://api.github.com/repos/{REPOSITORY}/actions/artifacts/{aid}'
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28'}
    response = requests.get(base, headers=headers, timeout=60)
    response.raise_for_status()
    meta = response.json()
    require((meta['id'], meta['size_in_bytes'], meta['digest'], meta['expired']) ==
            (aid, expected_size, 'sha256:' + expected_sha, False), 'GitHub artifact identity differs')
    response = requests.get(base + '/zip', headers=headers, allow_redirects=False, timeout=60)
    require(response.status_code in (301, 302, 303, 307), 'expected GitHub artifact redirect')
    url = response.headers['Location']
    require(url.startswith('https://'), 'non-HTTPS artifact redirect')
    budget.download(url, target, expected_size, expected_sha, f'github-actions-artifact:{aid}')
    return meta


def extract_zip_member(archive, name, target, size=None, sha=None):
    names = archive.namelist()
    require(names.count(name) == 1, 'missing/duplicate ZIP member: ' + name)
    info = archive.getinfo(name)
    require(not info.is_dir(), 'ZIP regular member required')
    if size is not None:
        require(info.file_size == size, 'ZIP member size differs: ' + name)
    capacity(target.parent, info.file_size)
    with archive.open(info) as incoming, target.open('xb') as output:
        shutil.copyfileobj(incoming, output, 1024**2)
    if size is not None and sha is not None:
        verify(target, size, sha)


def unpack_package(archive_path, package, target, choose, maximum):
    """Verify complete compressed TAR, then selected regular members and modes."""
    target.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive_path) as archive:
        require(set(archive.namelist()) == {package + '.tar.gz', package + '.tar.gz.json'} and
                len(archive.namelist()) == 2, 'package ZIP inventory differs')
        inv_name = package + '.tar.gz.json'
        require(archive.getinfo(inv_name).file_size <= 80_000_000, 'inventory is unexpectedly large')
        inventory = json.loads(archive.read(inv_name))
        files = inventory['files']
        for name in files:
            safe_name(name)
        selected = {name: item for name, item in files.items() if choose(name)}
        expansion = sum(item['bytes'] for item in selected.values())
        require(expansion <= maximum, 'selected TAR expansion exceeds its explicit bound')
        capacity(target, expansion)
        # The ZIP bytes were independently pinned before trusting its inventory.
        with archive.open(package + '.tar.gz') as incoming:
            hasher, count = hashlib.sha256(), 0
            for chunk in iter(lambda: incoming.read(1024**2), b''):
                count += len(chunk)
                hasher.update(chunk)
            require((count, hasher.hexdigest()) == (inventory['bytes'], inventory['sha256']),
                    'compressed TAR bytes/SHA differ from the verified ZIP inventory')
        extracted, seen = {}, set()
        with archive.open(package + '.tar.gz') as incoming, tarfile.open(fileobj=incoming, mode='r|gz') as tar:
            for member in tar:
                safe_name(member.name)
                require(member.name not in seen, 'duplicate TAR member')
                seen.add(member.name)
                require(member.isdir() or member.isfile(), 'nonregular TAR member forbidden')
                if member.isdir():
                    continue
                require(member.name in files, 'unmanifested TAR member')
                require(member.size == files[member.name]['bytes'], 'TAR member size differs')
                if member.name not in selected:
                    continue
                path = target / member.name
                path.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, path.open('xb') as output:
                    shutil.copyfileobj(source, output, 1024**2)
                verify(path, selected[member.name]['bytes'], selected[member.name]['sha256'])
                require((member.mode & 0o777) == (selected[member.name]['mode'] & 0o777),
                        'TAR member mode differs')
                os.chmod(path, member.mode & 0o777)
                extracted[member.name] = selected[member.name]
        require(set(extracted) == set(selected), 'selected TAR member missing')
    return {'archive': reference(archive_path), 'tar_bytes': inventory['bytes'],
            'tar_sha256': inventory['sha256'], 'selected_uncompressed_bytes': expansion,
            'selected_files': extracted, 'full_compressed_TAR_verified': True,
            'all_selected_member_bytes_SHA_modes_verified': True}


def compress_copy(source, target, maximum=12 * 1024**2):
    target.parent.mkdir(parents=True, exist_ok=True)
    with Path(source).open('rb') as incoming, target.open('wb') as output:
        with gzip.GzipFile(filename='', fileobj=output, mode='wb', mtime=0, compresslevel=6) as compressed:
            for block in iter(lambda: incoming.read(1024**2), b''):
                compressed.write(block)
                if output.tell() > maximum:
                    raise ValueError('retained compressed file exceeds explicit publication bound')
    require(target.stat().st_size <= maximum, 'retained compressed file exceeds explicit publication bound')
    return {'original': reference(source), 'retained_gzip': reference(target),
            'content_unchanged': True}


def retain_selected(original, replay, evidence):
    receipts = []
    used = sum(p.stat().st_size for p in evidence.rglob('*') if p.is_file())
    require(used <= RETAINED_OUTPUT_BUDGET, 'evidence already exceeds publication output bound')
    allowed = {'observed.json', 'observed.bering-raw.json', 'observed.signal-quality.json',
        'observed.supplied-aliases.json', 'binding.json', 'forecast.json', 'model.json',
        'predicates.json', 'overlay.json', 'faults.json', 'analysis.json', 'report.json',
        'provided-metadata-attachment.json', 'database-mapping.json', 'observed-reference.json',
        'input-reference.json', 'simulation.command.json', 'replay-command.json', 'bering-resources.json'}
    for label, root in [('original', original), ('replay', replay)]:
        for prefix in (DISCOVERY, OPERATIONS):
            for path in sorted((root / prefix).rglob('*')):
                if not path.is_file():
                    continue
                rel = path.relative_to(root).as_posix()
                if path.name not in allowed:
                    continue
                remaining = RETAINED_OUTPUT_BUDGET - used
                if remaining < 100_000:
                    receipts.append({'original': reference(path), 'retained': False,
                                     'reason': 'aggregate_publication_output_bound'})
                    continue
                if path.stat().st_size > 1_000_000:
                    target = evidence / label / (rel + '.gz')
                    try:
                        receipts.append(compress_copy(path, target, min(remaining, 12 * 1024**2)))
                    except ValueError:
                        target.unlink(missing_ok=True)
                        receipts.append({'original': reference(path), 'retained': False,
                            'reason': 'full_sidecar_exceeds_output_bound; selected edge evidence retained separately'})
                        continue
                else:
                    if path.stat().st_size > remaining:
                        continue
                    target = evidence / label / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, target)
                    receipts.append({'original': reference(path), 'retained': reference(target)})
                used += target.stat().st_size
    write(evidence / 'retained-model-sidecars.json', receipts)


def load_core(path):
    with zipfile.ZipFile(path) as archive:
        candidates = [n for n in archive.namelist() if n.endswith('/results/literal-results.json') or
                      n == 'results/literal-results.json']
        require(len(candidates) == 1, 'exactly one core literal-results.json required')
        return json.loads(archive.read(candidates[0]))


def prepare_example(args, receipt, budget):
    cache, evidence = args.work / 'cache', args.out / 'evidence'
    cache.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    outer = cache / 'publication.zip'
    try:
        budget.download(ZENODO, outer, OUTER[1], OUTER[2], 'anonymous-zenodo:24131735')
        receipt['zenodo_public_download'] = {'status': 'verified', **reference(outer), 'URL': ZENODO}
    except requests.RequestException as exc:
        # A transport error may fall back. An integrity error never does.
        receipt['zenodo_public_download'] = {'status': 'not_completed', 'error_type': type(exc).__name__}
        outer.unlink(missing_ok=True)
        receipt['source_artifact_fallback'] = github_artifact(*OUTER, budget, outer)
    core, example = evidence / 'code-and-results.zip', cache / 'worked-example.zip'
    with zipfile.ZipFile(outer) as archive:
        names = archive.namelist()
        for base, target, pin in [('code-and-results.zip', core, CORE), ('worked-example.zip', example, EXAMPLE)]:
            matching = [n for n in names if PurePosixPath(n).name == base]
            require(len(matching) == 1, 'publication subarchive missing or ambiguous')
            safe_name(matching[0])
            extract_zip_member(archive, matching[0], target, *pin)
    receipt['publication_subarchives'] = {'core': reference(core), 'worked_example': reference(example)}
    outer.unlink()
    nested = {}
    with zipfile.ZipFile(example) as archive:
        for kind, pin in [('capture', TRAINING), ('model', MODEL)]:
            name = f'artifact-{pin[0]}.zip'
            path = cache / name
            extract_zip_member(archive, name, path, pin[1], pin[2])
            nested[kind] = path
        selected = archive.read('selected-inputs.json')
        (evidence / 'selected-inputs.json').write_bytes(selected)
    example.unlink()
    receipt['capture_package'] = unpack_package(nested['capture'], 'capture', args.work / 'case',
                                                lambda name: True, 12 * 1024**3)
    nested['capture'].unlink()
    keep = lambda name: name.startswith((DISCOVERY, OPERATIONS)) or name in {
        'forecast-saved.json', 'closed-input.json', 'status.json', 'deployment.json',
        'v6-block-reference.json', 'v6-training-publication-restored.json', 'processing-execution.json',
        'model-worker-resources.json'} or (
        name.startswith('runtime-identity-v5/') and name.endswith('.json'))
    receipt['model_package'] = unpack_package(nested['model'], 'model', args.work / 'original',
                                              keep, 8 * 1024**3)
    nested['model'].unlink()
    original = args.work / 'original'
    require(digest(original / 'forecast-saved.json') == FREEZE, 'original forecast freeze SHA differs')
    saved = read(original / 'forecast-saved.json')
    require([saved['case'][k] for k in ('system', 'mode', 'seed', 'collector')] == KEY and
            saved['case']['commit'] == SOURCE and int(saved['case']['run_id']) == PRODUCER_RUN,
            'original forecast provenance differs')
    for rel in receipt['model_package']['selected_files']:
        if rel in saved['sha256_by_path']:
            require(digest(original / rel) == saved['sha256_by_path'][rel], 'frozen member differs: ' + rel)
    receipt['historical_forecast'] = {'manifest_sha256': FREEZE, 'case': saved['case'],
        'processing_execution': saved.get('processing_execution'), 'original_freeze_unchanged': True}
    require(digest(args.work / 'case/closed-input.json') == saved['training_closed_input_sha256'],
            'retained capture closure differs from the frozen model training input')
    shutil.copyfile(original / 'forecast-saved.json', evidence / 'original-forecast-saved.json')
    rows = load_core(core)['cells']
    cell = next(r for r in rows if r['key'] == KEY)
    require(cell['original_forecast']['forecast_manifest_sha256'] == FREEZE,
            'compact results refer to another freeze')
    write(evidence / 'original-cell-results.json', cell)
    return cell


def reaggregate_core(args):
    """Execute the existing five-input article script against the deposited core."""
    script = Path(__file__).with_name('build-submission-analysis.py')
    require(digest(script) == '10255b138ccd49e575007b358590066759f3b244c80dc262314e1416e86354fe',
            'article reaggregation script differs from the reviewed version')
    inputs = {'original': 'results/literal-results.json', 'corrected': 'data/prospective-results.json',
              'correction-report': 'results/correction-publication.json',
              'cost-ledger': 'docs/v6-full108-completed-cost-ledger.json', 'provenance': 'results/provenance.json'}
    folder = args.work / 'article-inputs'
    folder.mkdir(exist_ok=False)
    argv, records = [sys.executable, str(script)], {}
    with zipfile.ZipFile(args.out / 'evidence/code-and-results.zip') as archive:
        for role, name in inputs.items():
            selected = [n for n in archive.namelist() if n == name or n.endswith('/' + name)]
            require(len(selected) == 1, 'core reaggregation input missing/ambiguous: ' + name)
            target = folder / (role + '.json')
            extract_zip_member(archive, selected[0], target)
            records[role] = {'core_member': selected[0], **reference(target)}
            argv.extend(['--' + role, str(target)])
    output = args.out / 'article-reaggregation'
    argv.extend(['--out', str(output)])
    command(argv, args.work, args.out / 'logs/article-reaggregation.log')
    receipt = {'script': reference(script), 'inputs': records, 'status': 'completed',
               'table_output_sha256': {str(p.relative_to(output)): digest(p)
                                      for p in output.rglob('*') if p.is_file()},
               'new_models_or_outcomes': False}
    write(args.out / 'article-reaggregation-receipt.json', receipt)
    return receipt


def command(argv, cwd, logfile):
    logfile.parent.mkdir(parents=True, exist_ok=True)
    with logfile.open('wb') as output:
        subprocess.run([str(x) for x in argv], cwd=cwd, stdout=output,
                       stderr=subprocess.STDOUT, check=True)


def execute_historical(args, receipt):
    from ebpf_discovery.bering_v4 import child_go_environment
    from ebpf_discovery.capture_checks_v6 import verify_capture
    from ebpf_discovery.evaluate_v5 import acquisition_checks
    from ebpf_discovery.identity_projection_v5 import refresh
    from ebpf_discovery.runtime import Context
    from ebpf_discovery.store_v5 import ObservationStoreV5
    from ebpf_discovery.study_v6 import declaration, verify_files
    from ebpf_discovery.toolchain_v5 import Toolchain, PINS
    case_root = args.work / 'case'
    closed = verify_capture(case_root, 'training')
    status = closed['status']
    require([status[k] for k in ('system', 'mode', 'seed', 'collector')] == KEY and
            status['commit'] == SOURCE and int(status['run_id']) == PRODUCER_RUN,
            'capture identity differs from selected example')
    require(not (case_root / 'forecast-saved.json').exists(), 'capture unexpectedly contains a forecast')
    ctx = Context(case_root, status['mode'], status['seed'])
    ctx.collector = status['collector']
    connection = sqlite3.connect((case_root / 'attempt-journal.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)
    ctx.journal = SimpleNamespace(db=connection, lock=threading.Lock(), path=case_root / 'attempt-journal.sqlite')
    # A fresh index is required; original frozen observations remain unchanged.
    require(not (case_root / 'observation-index.sqlite').exists(), 'training archive contains a derived index')
    store = ObservationStoreV5(case_root / 'observation-index.sqlite', same_trace_parents=True)
    declared = declaration(status['system'])
    plans = read(case_root / 'plans.json')
    try:
        write(args.out / 'evidence/index-training.json', store.ingest(case_root / 'observations', case_root / 'native'))
        acquisition = acquisition_checks(case_root, status, declared, agent_expected=True)
        write(args.out / 'evidence/training-acquisition-checks.json', acquisition)
        require(acquisition['valid'], 'historical acquisition checks rejected the saved capture')
        refresh(SimpleNamespace(ctx=ctx, store=store, plans=plans, collector='obi'), 'training')
        with child_go_environment():
            tool = Toolchain(ctx, 'otel_demo', store, declared)
            tool.preflight()
            tool.prepare_inputs(plans)
            source, variant = 'ebpf', 'network_scope'
            input_path, manifest = tool.input_manifests[source, variant]
            shared = tool.root / 'discovery' / source / variant
            model, quality = tool.discover(input_path, shared, prefix='observed')
            forecasts = {}
            for op in OPS:
                forecasts[op] = tool.forecast_operation(source, variant, op, declared.CONTRACTS[op],
                    input_path, manifest, shared, model, quality, tool.root / source / variant / op)
        verify_files(case_root, closed['files'])
        receipt['historical_execution'] = {'status': 'completed', 'source': SOURCE,
            'pins': PINS, 'capture_closed_input_sha256': digest(case_root / 'closed-input.json'),
            'scope': {'source': 'ebpf', 'variant': 'network_scope', 'operations': list(OPS)},
            'all_declared_entry_roots_used_by_original_prepare_inputs': True,
            'source_global_training_prefix_preserved': True, 'new_capture_executed': False,
            'additional_swap_provisioned': False, 'Bering_child_Go_overrides': {},
            'new_forecast_freeze_claimed': False, 'training_closed_members_unchanged': True}
        return forecasts
    finally:
        store.close()
        connection.close()


def model_semantics(model):
    model = copy.deepcopy(model)
    # These two model metadata fields describe this replay process, not topology.
    removed = {k: model.get('metadata', {}).pop(k, None) for k in ('discovered_at', 'source_ref')}
    for field in ('services', 'edges', 'endpoints'):
        model[field] = sorted(model[field], key=lambda r: r['id'])
    return model, removed


def compare_results(args, cell):
    original, replay = args.work / 'original', args.work / 'case'
    comparisons = {'scope': KEY, 'discovery': {}, 'operations': {}, 'differences_retained': True,
                   'accuracy_improvement_claimed': False}
    sequence = DISCOVERY + 'observed-runtime/accepted-request-sequence.jsonl'
    comparisons['input_wire_sequence'] = {
        'original': reference(original / sequence), 'replay': reference(replay / sequence),
        'same_ordered_HTTP_body_hashes_sizes_endpoints_statuses': digest(original / sequence) == digest(replay / sequence),
        'full_sequence_in_original_deposit': True}
    for rel in (DISCOVERY + 'observed.json', DISCOVERY + 'observed.bering-raw.json'):
        old, old_removed = model_semantics(read(original / rel))
        new, new_removed = model_semantics(read(replay / rel))
        same = old == new
        comparisons['discovery'][rel] = {'equal_except_declared_process_metadata': same,
            'original_sha256': digest(original / rel), 'replay_sha256': digest(replay / rel),
            'process_metadata': {'original': old_removed, 'replay': new_removed}}
        if not same:
            write(args.out / 'differences' / (Path(rel).name + '.json'), {'original': old, 'replay': new})
    for op in OPS:
        folder = OPERATIONS + op + '/'
        old_model, old_removed = model_semantics(read(original / (folder + 'model.json')))
        new_model, new_removed = model_semantics(read(replay / (folder + 'model.json')))
        row = {'model_semantics_equal': old_model == new_model,
               'predicates_equal': read(original / (folder + 'predicates.json')) == read(replay / (folder + 'predicates.json')),
               'model_process_metadata': {'original': old_removed, 'replay': new_removed}}
        old = read(original / (folder + 'forecast.json'))
        new = read(replay / (folder + 'forecast.json'))
        row['forecast_file_references'] = {label: {k: obj.pop(k, None) for k in ('graph_sha256', 'analysis_sha256')}
                                           for label, obj in [('original', old), ('replay', new)]}
        row['forecast_semantics_equal'] = old == new
        binding_old, binding_new = read(original / (folder + 'binding.json')), read(replay / (folder + 'binding.json'))
        fields = ('available', 'entry_service', 'required_edges', 'mandatory_targets', 'endpoints', 'unknown',
                  'resolved_calls', 'assumed_satisfied_database_requirements', 'all_required_database_channels_observed',
                  'database_fault_prediction_available', 'database_fault_unknown', 'database_fault_fixed_other_requirements')
        row['binding_semantics_equal'] = all(binding_old.get(k) == binding_new.get(k) for k in fields)
        row['binding_compared_fields'] = list(fields)
        external = next(r for r in cell['literal_evaluation']['rows'] if
                        (r['operation'], r['source'], r['variant']) == (op, 'ebpf', 'network_scope'))
        row['saved_external_evaluation'] = external
        row['external_saved_forecast_consistent'] = (external['prediction'] == old.get('prediction') and
            external['available'] == old['available'] and
            {state: value.get('prediction') for state, value in external['by_state'].items()} == old['by_state'] and
            external.get('database_down_prediction') == old.get('database_down_prediction'))
        row['external_counts_newly_measured'] = False
        row['agreement_with_observed_outcomes_required_for_replay_success'] = False
        row['saved_adverse_errors_preserved'] = external.get('error')
        if not all(row[k] for k in ('model_semantics_equal', 'predicates_equal', 'forecast_semantics_equal', 'binding_semantics_equal')):
            write(args.out / 'differences' / (op + '.json'), {'original_model': old_model, 'replay_model': new_model,
                'original_forecast': old, 'replay_forecast': new,
                'original_binding': {k: binding_old.get(k) for k in fields},
                'replay_binding': {k: binding_new.get(k) for k in fields}})
        comparisons['operations'][op] = row
    comparisons['all_semantic_checks_passed'] = (
        comparisons['input_wire_sequence']['same_ordered_HTTP_body_hashes_sizes_endpoints_statuses'] and
        all(r['equal_except_declared_process_metadata'] for r in comparisons['discovery'].values()) and
        all(all(r[k] for k in ('model_semantics_equal', 'predicates_equal', 'forecast_semantics_equal',
                              'binding_semantics_equal', 'external_saved_forecast_consistent'))
            for r in comparisons['operations'].values()))
    write(args.out / 'evidence/replay-comparison.json', comparisons)
    return comparisons


def environment(args):
    versions = {}
    for package in ('requests', 'PyYAML', 'numpy', 'ijson', 'aiohttp', 'protobuf', 'opentelemetry-proto'):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {'python': sys.version, 'platform': platform.platform(), 'package_versions': versions,
            'processor_affinity': sorted(os.sched_getaffinity(0)),
            'runner_os_image': {k: os.environ.get(k) for k in ('ImageOS', 'ImageVersion', 'RUNNER_OS', 'RUNNER_ARCH')},
            'reader': {k: os.environ.get(k) for k in ('GITHUB_SHA', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_JOB')},
            'historical_source': SOURCE, 'full_historical_environment_identity_claimed': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--historical', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.stage = 'replay'
    require(os.environ.get('GITHUB_ACTIONS') == 'true', 'scientific artifact processing is GitHub Actions only')
    args.historical, args.work, args.out = [p.resolve() for p in (args.historical, args.work, args.out)]
    for path in (args.work, args.out):
        path.mkdir(parents=True, exist_ok=True)
    sys.path[:0] = [str(args.historical / 'src'), str(args.historical)]
    actual = subprocess.check_output(['git', '-C', str(args.historical), 'rev-parse', 'HEAD'], text=True).strip()
    require(actual == SOURCE, 'historical checkout differs from producing source')
    require(not subprocess.check_output(['git', '-C', str(args.historical), 'diff', '--name-only'], text=True).strip(),
            'historical source has local edits')
    started, cpu = time.time_ns(), os.times()
    receipt = {'started_ns': started, 'stage': args.stage, 'status': 'running',
               'environment': environment(args), 'human_seconds': None,
               'human_cost_status': 'unmeasured', 'new_application_measurements': False}
    receipt_path = args.out / (args.stage + '-receipt.json')
    budget = DownloadBudget(args.out / 'download-budget.json')
    write(receipt_path, receipt)
    failed = False
    try:
        from ebpf_discovery.resources_v6 import prepare
        prepare(args.out / 'worker-resources.json')
        cell = prepare_example(args, receipt, budget)
        write(receipt_path, receipt)
        try:
            receipt['article_reaggregation'] = reaggregate_core(args)
        except Exception as exc:
            receipt['article_reaggregation'] = {'status': 'failed', 'error_type': type(exc).__name__,
                                               'error': sanitized(exc)[:600]}
            write(args.out / 'article-reaggregation-receipt.json', receipt['article_reaggregation'])
        tool_root = args.work / 'toolchain'
        os.environ['PBS_BIN'] = str(tool_root / 'bin')
        os.environ['PYTHONPATH'] = os.pathsep.join((str(args.historical / 'src'), str(args.historical)))
        command(['bash', args.historical / 'scripts/setup-toolchain-v4.sh', tool_root, 'v5'],
                args.historical, args.out / 'logs/toolchain-build.log')
        shutil.copyfile(tool_root / 'toolchain-build.json', args.out / 'toolchain-build.json')
        receipt['executed_toolchain'] = read(tool_root / 'toolchain-build.json')
        execute_historical(args, receipt)
        comparison = compare_results(args, cell)
        failed = not comparison['all_semantic_checks_passed']
        receipt['semantic_replay_status'] = 'matched' if comparison['all_semantic_checks_passed'] else 'differences'
        # Imported only after the real replay; the helper performs no discovery.
        from publication_edge_evidence import extract_evidence
        receipt['edge_evidence'] = extract_evidence(args.work / 'original', args.work / 'case', args.out / 'evidence')
        receipt['status'] = 'completed' if comparison['all_semantic_checks_passed'] else 'completed_with_differences'
    except Exception as exc:
        failed = True
        receipt.update(status='failed', error_type=type(exc).__name__, error=sanitized(exc)[:1200])
        (args.out / 'logs').mkdir(exist_ok=True)
        (args.out / 'logs/failure.txt').write_text(sanitized(traceback.format_exc()), encoding='utf-8')
    finally:
        if args.stage == 'replay':
            try:
                retain_selected(args.work / 'original', args.work / 'case', args.out / 'evidence')
            except Exception as exc:
                failed = True
                receipt['retention_error'] = {'error_type': type(exc).__name__, 'error': str(exc)[:500]}
            for path in (args.work / 'case').glob('commands.jsonl'):
                try:
                    compress_copy(path, args.out / 'logs/commands.jsonl.gz')
                except ValueError:
                    (args.out / 'logs/commands.jsonl.gz').unlink(missing_ok=True)
                    receipt['command_log_retention'] = {'original': reference(path),
                        'reason': 'complete log exceeded output bound; individual replay command sidecars retained'}
        now = os.times()
        receipt.update(ended_ns=time.time_ns(), elapsed_seconds=(time.time_ns() - started) / 1e9,
            cpu_seconds={'user': now.user - cpu.user, 'system': now.system - cpu.system,
                         'children_user': now.children_user - cpu.children_user,
                         'children_system': now.children_system - cpu.children_system},
            max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            max_child_rss_KiB=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            disk_free_bytes=shutil.disk_usage(args.work).free)
        write(receipt_path, receipt)
        print(json.dumps({'stage': args.stage, 'status': receipt['status'],
                          'semantic_replay_status': receipt.get('semantic_replay_status')}), flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
