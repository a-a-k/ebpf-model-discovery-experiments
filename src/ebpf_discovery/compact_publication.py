"""Bounded code/results bundle and one optional, exact historical example.

Build and analytical verification run in Actions. This module never starts an
application, builds a model, lists historical artifacts, or publishes a Release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

from .publication_archive import GitHub, REPO, REFERENCE_SHA, file_digest, require


SELECTION = 'docs/compact-publication-inputs.json'
SCOPE = 'reproduction-scope.json'
SUMMARY_PATH = 'data/prospective-results.json'
CORE_BUDGET = 100_000_000
TOTAL_BUDGET = 2_000_000_000
SUMMARY_ID = 730603417
SUMMARY_BYTES = 10530719
SUMMARY_SHA = 'd772bd51c199397f5b5d2aaa623d255946cbaf6541b7955ab74a145eaac2a345'
REPORT_SHA = 'd69134c8bf4bc617d3ab5fbe8146617277c7b62cd425801a9c9a8b3928b57f44'
EXAMPLE_PINS = {
    'training': (13565862245, 329226484,
                 'f910fb03380e6e7ad0c60c4f1e14e8fa7f1858dbcffba9eb37710ba3d9990efb'),
    'model': (13567701925, 747216214,
              '19099f3bdc275fc595c6e819ce010f1da1536152feca3069a1e5333f2389f662'),
}
EXAMPLE_RUN = 42347357851
EXAMPLE_SOURCE = 'b913a5df7be680c5e6ede001d0f8eb6fb856a4ed'


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf8')


def actions_only():
    require(os.environ.get('GITHUB_ACTIONS') == 'true',
            'publication build and analytical verification run in GitHub Actions only')


def member_name(name):
    path = PurePosixPath(name)
    require(bool(name) and not path.is_absolute() and '\\' not in name and
            all(p not in ('', '.', '..', '.git') for p in name.split('/')) and
            path.parts[0] != 'work', 'unsafe or excluded package path: ' + name)
    return name


def identity(path):
    path = Path(path)
    return {'bytes': path.stat().st_size, 'sha256': file_digest(path)}


def tracked_files(root):
    """Seal a clean committed tree; generated work and Git internals never enter."""
    root = Path(root).resolve()
    git = lambda *args: subprocess.check_output(['git', '-C', str(root), *args])
    source = git('rev-parse', 'HEAD').decode().strip()
    require(not git('status', '--porcelain', '--untracked-files=no').strip(),
            'publication source must be a clean committed tree')
    files = {}
    for item in git('ls-tree', '-r', '-z', '--full-tree', 'HEAD').split(b'\0'):
        if not item:
            continue
        header, raw_name = item.split(b'\t', 1)
        mode, kind, _ = header.decode().split()
        name = raw_name.decode('utf8')
        if name.split('/')[0] == 'work' or '.git' in name.split('/'):
            continue
        member_name(name)
        require(kind == 'blob' and mode in ('100644', '100755'),
                'only regular committed source files are packaged: ' + name)
        path = root / name
        require(path.is_file() and not path.is_symlink(), 'missing regular source file: ' + name)
        files[name] = {**identity(path), 'mode': int(mode, 8) & 0o777}
    require(files and SCOPE not in files and SUMMARY_PATH not in files,
            'empty source or reserved generated package member')
    return source, files


def selection(root):
    value = json.loads((Path(root) / SELECTION).read_bytes())
    require(value['repo'] == REPO, 'foreign input selection')
    core = value['core']
    summary = core['corrected_summary']
    require((summary['id'], summary['size'], summary['sha256']) ==
            (SUMMARY_ID, SUMMARY_BYTES, SUMMARY_SHA), 'fixed summary selection differs')
    require(core['original_analytical_result']['path'] == 'results/literal-results.json' and
            core['original_analytical_result']['sha256'] == REFERENCE_SHA and
            core['corrected_publication_report']['path'] == 'results/correction-publication.json' and
            core['corrected_publication_report']['sha256'] == REPORT_SHA,
            'fixed analytical publication selection differs')
    example = value['optional_real_example']
    require(example['key'] == ['otel_demo', 'absent', 9, 'obi'], 'fixed example case differs')
    for role, pin in EXAMPLE_PINS.items():
        item = example[role]
        require((item['id'], item['size_in_bytes'], item['digest']) ==
                (pin[0], pin[1], 'sha256:' + pin[2]) and
                item['run_id'] == EXAMPLE_RUN and item['source'] == EXAMPLE_SOURCE,
                'fixed two-package example selection differs: ' + role)
    return value


def verify_record_files(root, chosen):
    for key in ('original_analytical_result', 'corrected_publication_report'):
        item = chosen['core'][key]
        require(identity(Path(root) / item['path']) ==
                {'bytes': item['size'], 'sha256': item['sha256']},
                'analytical publication bytes differ: ' + item['path'])


def budget(files, summary_size, example_sizes=(), extra_bytes=0):
    """Conservative ZIP overhead bound, evaluated before any payload download."""
    sizes = [v['bytes'] for v in files.values()] + [summary_size, extra_bytes]
    require(all(type(n) is int and n >= 0 for n in sizes + list(example_sizes)),
            'invalid planned size')
    core_bound = sum(n + n // 100 + 4096 for n in sizes) + 65536
    # Example ZIP uses ZIP_STORED. Existing input ZIP compression is preserved.
    example_bound = sum(example_sizes) + extra_bytes + 65536 if example_sizes else 0
    require(core_bound <= CORE_BUDGET, 'planned core exceeds 100 MB budget')
    require(core_bound + example_bound + 65536 <= TOTAL_BUDGET,
            'planned complete deposit exceeds 2 GB budget')
    return {'core_archive_upper_bound_bytes': core_bound,
            'example_archive_upper_bound_bytes': example_bound,
            'core_budget_bytes': CORE_BUDGET, 'total_budget_bytes': TOTAL_BUDGET,
            'payload_download_bytes': summary_size + sum(example_sizes)}


def scope(source, files, chosen, include_example):
    return {
        'schema': 'compact-publication-scope-v1', 'source': source,
        'source_repository': os.environ.get('GITHUB_REPOSITORY'), 'input_repository': REPO,
        'files': files,
        'analytical_results': {'original_cases': 108, 'corrected_cases': 36,
            'observations_are_per_case_operation_phase_state_counts': True,
            'all_original_attempt_records_included': False,
            'per_attempt_latency_and_classification_assignments_included': False,
            'all_paper_tables_or_figures_recreated': False},
        'real_example': {'included_as_companion': include_example,
            'key': chosen['optional_real_example']['key'],
            'selection_role': 'illustrative technical example; not an additional scientific repetition',
            'selected_historical_training_and_model_packages_only': True,
            'model_rebuild_executed': False, 'new_measurements_executed': False},
        'full_historical_raw_replay_included': False,
        'unknown_human_work_is_not_zero': True,
        'verification_scope': 'Exact analytical publications, correction derived statistics, file hashes and ZIP CRCs.',
    }


def check_summary_asset(actual, expected):
    require(all(actual.get(k) == expected[k] for k in ('id', 'name', 'size')) and
            actual.get('digest') == 'sha256:' + expected['sha256'] and
            actual.get('state') == 'uploaded', 'corrected summary asset identity differs')


def check_artifact(actual, expected):
    require(all(actual.get(k) == expected[k] for k in ('id', 'name', 'size_in_bytes', 'digest')) and
            actual.get('expired') is False and
            (actual.get('workflow_run') or {}).get('id') == expected['run_id'] and
            (actual.get('workflow_run') or {}).get('head_sha') == expected['source'],
            'selected example artifact identity/source/run differs')


def verify_input_zip(path, expected, members):
    require(identity(path) == {'bytes': expected['size_in_bytes'], 'sha256': expected['digest'][7:]},
            'selected input ZIP bytes/SHA differ')
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and set(names) == set(members),
                'selected input ZIP member set differs')
        require(archive.testzip() is None, 'selected input ZIP CRC differs')
    return {'artifact_id': expected['id'], 'ZIP_members': names, 'all_ZIP_CRCs_verified': True,
            'nested_TAR_contents_verified': False, 'model_rebuild_executed': False}


def write_zip(destination, entries, metadata, *, compression):
    """entries maps relative names to (source path, sealed identity)."""
    with zipfile.ZipFile(destination, 'x', compression=compression,
                         compresslevel=6 if compression == zipfile.ZIP_DEFLATED else None) as archive:
        for name, (path, expected) in sorted(entries.items()):
            member_name(name)
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = compression
            info.external_attr = (stat.S_IFREG | expected.get('mode', 0o644)) << 16
            h, count = hashlib.sha256(), 0
            with Path(path).open('rb') as incoming, archive.open(info, 'w') as outgoing:
                for body in iter(lambda: incoming.read(1024**2), b''):
                    count += len(body)
                    require(count <= expected['bytes'], 'source grew after sealing: ' + name)
                    h.update(body)
                    outgoing.write(body)
            require(count == expected['bytes'] and h.hexdigest() == expected['sha256'],
                    'source changed after sealing: ' + name)
        for name, body in sorted(metadata.items()):
            require(name not in entries, 'duplicate generated member')
            info = zipfile.ZipInfo(member_name(name), (1980, 1, 1, 0, 0, 0))
            info.compress_type = compression
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, body)


def extract_core(path, destination):
    require(Path(path).stat().st_size <= CORE_BUDGET, 'core archive exceeds budget')
    destination = Path(destination)
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        require(len(names) == len(set(names)) and SCOPE in names and
                sum(i.file_size for i in infos) <= CORE_BUDGET,
                'duplicate, missing or oversized core contents')
        for info in infos:
            member_name(info.filename)
            require(not info.is_dir() and not stat.S_ISLNK(info.external_attr >> 16),
                    'core must contain regular files only')
        value = json.loads(archive.read(SCOPE))
        require(set(names) == set(value['files']) | {SCOPE}, 'core closed file set differs')
        for info in infos:
            target = destination / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as incoming, target.open('xb') as outgoing:
                shutil.copyfileobj(incoming, outgoing, 1024**2)
            if info.filename != SCOPE:
                expected = value['files'][info.filename]
                require(identity(target) == {k: expected[k] for k in ('bytes', 'sha256')},
                        'core member bytes/SHA differ: ' + info.filename)
                target.chmod(expected.get('mode', 0o644))
        return value


def verify_extracted(root):
    """Called by an isolated interpreter importing this file from the ZIP."""
    actions_only()
    root = Path(root).resolve()
    chosen = selection(root)
    verify_record_files(root, chosen)
    item = chosen['core']['corrected_summary']
    require(identity(root / SUMMARY_PATH) == {'bytes': item['size'], 'sha256': item['sha256']},
            'packaged corrected summary differs')
    original = json.loads((root / 'results/literal-results.json').read_bytes())
    report = json.loads((root / 'results/correction-publication.json').read_bytes())
    summary = json.loads((root / SUMMARY_PATH).read_bytes())
    expected = {(s, m, r, a) for s in ('petclinic', 'otel_demo', 'deathstarbench')
                for m in ('absent', 'partial', 'full') for r in (9, 10, 11)
                for a in ('none', 'obi', 'coroot', 'deepflow')}
    require(len(original['cells']) == 108 and {tuple(c['key']) for c in original['cells']} == expected,
            'original 108-case census differs')
    require(summary['source'] == report['capture_source'] and
            str(summary['run_id']) == str(report['capture_run_id']) and
            report['generated_summary_asset']['id'] == item['id'] and
            report['generated_summary_asset']['size'] == item['size'] and
            report['generated_summary_asset']['digest'] == 'sha256:' + item['sha256'],
            'summary actual producing source/run differs')
    from .compose_ack_publication import derived_statistics
    require(derived_statistics(summary) == report['statistics'], 'correction derived statistics differ')
    for name, module in list(sys.modules.items()):
        if name == 'systems' or name.startswith(('ebpf_discovery.', 'systems.')) or name == 'ebpf_discovery':
            location = getattr(module, '__file__', None)
            if location:
                require(Path(location).resolve().is_relative_to(root),
                        'verification imported a checkout dependency: ' + name)
    return {'status': 'success', 'original_cases': 108, 'corrected_cases': 36,
            'correction_derived_statistics_equal': True, 'live_API_requests': 0,
            'model_rebuild_executed': False, 'new_measurements_executed': False,
            'all_paper_tables_or_figures_recreated': False,
            'verification_imports_from_extracted_package_only': True}


def verify_core(path):
    actions_only()
    with tempfile.TemporaryDirectory(prefix='compact-publication-verify-') as temporary:
        root = Path(temporary)
        value = extract_core(path, root)
        script = ('import json,pathlib,sys; p=pathlib.Path(sys.argv[1]).resolve(); '
                  'sys.path[:0]=[str(p/"src"),str(p)]; '
                  'from ebpf_discovery.compact_publication import verify_extracted; '
                  'print(json.dumps(verify_extracted(p)))')
        env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONHOME', 'GH_TOKEN')}
        output = subprocess.check_output([sys.executable, '-I', '-c', script, str(root)],
                                         cwd=root, env=env, text=True)
        return json.loads(output), value, selection(root)


def verify_example(path, chosen):
    require(Path(path).stat().st_size <= TOTAL_BUDGET, 'example archive exceeds budget')
    example = chosen['optional_real_example']
    expected_names = {'selected-inputs.json'} | {f"artifact-{example[r]['id']}.zip" for r in EXAMPLE_PINS}
    with tempfile.TemporaryDirectory(prefix='compact-example-verify-') as temporary:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)) and set(names) == expected_names,
                    'example package contains unselected files')
            require(sum(i.file_size for i in archive.infolist()) <= TOTAL_BUDGET,
                    'example contents exceed budget')
            manifest = json.loads(archive.read('selected-inputs.json'))
            require(manifest['selection'] == example, 'example selection differs from core')
            checks = []
            for role in EXAMPLE_PINS:
                item = example[role]
                name = f"artifact-{item['id']}.zip"
                require(archive.getinfo(name).file_size == item['size_in_bytes'], 'example member size differs')
                destination = Path(temporary) / name
                with archive.open(name) as incoming, destination.open('xb') as outgoing:
                    shutil.copyfileobj(incoming, outgoing, 1024**2)
                checks.append(verify_input_zip(destination, item, example['members'][role]))
                destination.unlink()
            return checks


def build(root, output, include_example=False):
    actions_only()
    root, output = Path(root).resolve(), Path(output).absolute()
    require(not any(p.is_symlink() for p in (output, *output.parents)) and
            output.resolve().is_relative_to(root / 'work'), 'output must remain in checkout/work')
    source, files = tracked_files(root)
    require(source == os.environ['GITHUB_SHA'], 'checkout differs from actual Actions source')
    chosen = selection(root)
    require(SELECTION in files and 'src/ebpf_discovery/compact_publication.py' in files,
            'publication implementation and selection must be committed')
    verify_record_files(root, chosen)
    item = chosen['core']['corrected_summary']
    files[SUMMARY_PATH] = {'bytes': item['size'], 'sha256': item['sha256'], 'mode': 0o644}
    description = scope(source, files, chosen, include_example)
    example = chosen['optional_real_example']
    selected_body = encoded({'source': source, 'selection': example,
                             'model_rebuild_executed': False, 'new_measurements_executed': False})
    planned = budget({k: v for k, v in files.items() if k != SUMMARY_PATH}, item['size'],
                     [example[r]['size_in_bytes'] for r in EXAMPLE_PINS] if include_example else [],
                     len(encoded(description)) + len(selected_body))
    require(not output.exists() or not any(output.iterdir()), 'output directory must be empty')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'build-plan.json').write_bytes(encoded({'source': source, **planned,
        'include_example': include_example, 'selection_sha256': file_digest(root / SELECTION)}))
    github = GitHub(replay=not include_example)
    check_summary_asset(github.json(f"releases/assets/{item['id']}"), item)
    actual_examples = {}
    if include_example:
        for role in EXAMPLE_PINS:
            selected = example[role]
            actual = github.json(f"actions/artifacts/{selected['id']}")
            check_artifact(actual, selected)
            actual_examples[role] = actual
    checks, outputs = [], {}
    with tempfile.TemporaryDirectory(prefix='downloads-', dir=output) as temporary:
        downloads = Path(temporary)
        summary_path = downloads / 'summary.json'
        github.download(f"releases/assets/{item['id']}", summary_path, item['size'], item['sha256'])
        entries = {name: (root / name, info) for name, info in files.items() if name != SUMMARY_PATH}
        entries[SUMMARY_PATH] = (summary_path, files[SUMMARY_PATH])
        core_path = output / 'code-and-results.zip'
        write_zip(core_path, entries, {SCOPE: encoded(description)}, compression=zipfile.ZIP_DEFLATED)
        require(core_path.stat().st_size <= CORE_BUDGET, 'written core exceeds 100 MB budget')
        verification, _, _ = verify_core(core_path)
        outputs[core_path.name] = identity(core_path)
        if include_example:
            entries = {}
            for role in EXAMPLE_PINS:
                selected = example[role]
                path = downloads / f"artifact-{selected['id']}.zip"
                github.download(f"actions/artifacts/{selected['id']}/zip", path,
                                selected['size_in_bytes'], selected['digest'][7:])
                checks.append(verify_input_zip(path, selected, example['members'][role]))
                entries[path.name] = (path, {'bytes': selected['size_in_bytes'], 'sha256': selected['digest'][7:]})
            example_path = output / 'worked-example.zip'
            write_zip(example_path, entries, {'selected-inputs.json': selected_body}, compression=zipfile.ZIP_STORED)
            outputs[example_path.name] = identity(example_path)
    require(sum(v['bytes'] for v in outputs.values()) <= TOTAL_BUDGET,
            'written deposit exceeds 2 GB budget')
    manifest = {'schema': 'compact-publication-manifest-v1', 'source': source,
        'source_repository': os.environ.get('GITHUB_REPOSITORY'), 'input_repository': REPO,
        'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT', '1'),
        'outputs': outputs, 'planned_budget': planned, 'core_verification': verification,
        'example_integrity': checks, 'actual_selected_artifact_API': actual_examples,
        'API_requests': github.calls, 'model_rebuild_executed': False, 'new_measurements_executed': False,
        'human_seconds': None}
    (output / 'manifest.json').write_bytes(encoded(manifest))
    named = [output / name for name in outputs] + [output / 'build-plan.json', output / 'manifest.json']
    (output / 'SHA256SUMS.txt').write_text(''.join(f'{file_digest(p)}  {p.name}\n' for p in named), encoding='utf8')
    require(sum(p.stat().st_size for p in output.iterdir() if p.is_file()) <= TOTAL_BUDGET,
            'deposit including receipts exceeds 2 GB budget')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('build')
    create.add_argument('--out', required=True)
    create.add_argument('--include-example', action='store_true')
    check = sub.add_parser('verify')
    check.add_argument('--archive', required=True)
    check.add_argument('--example')
    args = parser.parse_args()
    actions_only()
    if args.command == 'build':
        result = build(Path(__file__).resolve().parents[2], args.out, args.include_example)
        print(json.dumps({'source': result['source'], 'outputs': result['outputs'],
                          'core_verification': result['core_verification']}))
    else:
        receipt, description, chosen = verify_core(Path(args.archive).resolve())
        if args.example:
            require(description['real_example']['included_as_companion'], 'core did not select an example')
            receipt['example_integrity'] = verify_example(Path(args.example).resolve(), chosen)
        print(json.dumps(receipt))


if __name__ == '__main__':
    main()
