"""Tiny packaging fixtures only; historical scientific data are not replayed here."""
import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from ebpf_discovery import compact_publication as compact


def sha(body):
    return hashlib.sha256(body).hexdigest()


def seal(path):
    return {**compact.identity(path), 'mode': 0o644}


def synthetic_zip(path, members):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, body in members.items():
            archive.writestr(name, body)
    return {'id': 1, 'size_in_bytes': path.stat().st_size,
            'digest': 'sha256:' + compact.file_digest(path)}


def test_only_committed_regular_files_enter_and_work_is_excluded(tmp_path, monkeypatch):
    (tmp_path / 'source.py').write_text('value = 1\n')
    (tmp_path / 'untracked.txt').write_text('not selected')
    listing = (b'100644 blob abc\tsource.py\0'
               b'100644 blob def\twork/old-results.json\0'
               b'100644 blob ghi\t.git/internal\0')
    def git(args):
        command = args[3:]
        return {('rev-parse', 'HEAD'): b'a' * 40 + b'\n',
                ('status', '--porcelain', '--untracked-files=no'): b'',
                ('ls-tree', '-r', '-z', '--full-tree', 'HEAD'): listing}[tuple(command)]
    monkeypatch.setattr(compact.subprocess, 'check_output', git)
    source, files = compact.tracked_files(tmp_path)
    assert source == 'a' * 40
    assert set(files) == {'source.py'}


def test_dirty_source_is_rejected_before_selection(tmp_path, monkeypatch):
    monkeypatch.setattr(compact.subprocess, 'check_output',
                        lambda args: b'a' * 40 if args[3] == 'rev-parse' else b' M source.py\n')
    with pytest.raises(ValueError, match='clean committed tree'):
        compact.tracked_files(tmp_path)


def test_budget_is_checked_before_network_or_payload_download(tmp_path, monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setenv('GITHUB_REPOSITORY', compact.REPO)
    monkeypatch.setenv('GITHUB_SHA', 'a' * 40)
    files = {compact.SELECTION: {'bytes': 1, 'sha256': '0' * 64},
             'src/ebpf_discovery/compact_publication.py': {'bytes': compact.CORE_BUDGET, 'sha256': '1' * 64}}
    chosen = {'core': {'corrected_summary': {'size': 4, 'sha256': '2' * 64}},
              'optional_real_example': {'key': ['synthetic'],
                                        'training': {'size_in_bytes': 1}, 'model': {'size_in_bytes': 1}}}
    monkeypatch.setattr(compact, 'tracked_files', lambda root: ('a' * 40, files))
    monkeypatch.setattr(compact, 'selection', lambda root: chosen)
    monkeypatch.setattr(compact, 'verify_record_files', lambda *args: None)
    def forbidden(*args, **kwargs):
        pytest.fail('network client created before budget rejection')
    monkeypatch.setattr(compact, 'GitHub', forbidden)
    with pytest.raises(ValueError, match='100 MB'):
        compact.build(tmp_path, tmp_path / 'work' / 'deposit')
    with pytest.raises(ValueError, match='2 GB'):
        compact.budget({}, 1, [compact.TOTAL_BUDGET])


def test_zip_seal_rejects_source_modified_after_inventory(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_bytes(b'original')
    info = seal(source)
    source.write_bytes(b'changed!')
    with pytest.raises(ValueError, match='changed after sealing'):
        compact.write_zip(tmp_path / 'bad.zip', {'source.txt': (source, info)}, {},
                          compression=zipfile.ZIP_DEFLATED)


def test_selected_input_requires_exact_members_hash_and_crc(tmp_path):
    path = tmp_path / 'input.zip'
    expected = synthetic_zip(path, {'capture.tar.gz': b'synthetic body',
                                    'capture.tar.gz.json': b'{}'})
    names = ['capture.tar.gz', 'capture.tar.gz.json']
    assert compact.verify_input_zip(path, expected, names)['all_ZIP_CRCs_verified']
    with pytest.raises(ValueError, match='member set'):
        compact.verify_input_zip(path, expected, names + ['unselected'])
    with pytest.raises(ValueError, match='bytes/SHA'):
        compact.verify_input_zip(path, {**expected, 'digest': 'sha256:' + '0' * 64}, names)
    body = bytearray(path.read_bytes())
    body[30 + len('capture.tar.gz')] ^= 1
    path.write_bytes(body)
    expected['digest'] = 'sha256:' + sha(body)
    with pytest.raises(ValueError, match='CRC'):
        compact.verify_input_zip(path, expected, names)


@pytest.mark.parametrize('field,value', [('id', 2), ('name', 'foreign'), ('size_in_bytes', 2),
                                        ('digest', 'sha256:wrong'), ('expired', True),
                                        ('workflow_run', {'id': 8, 'head_sha': 'b' * 40})])
def test_example_metadata_binds_exact_source_run_and_bytes(field, value):
    expected = {'id': 1, 'name': 'selected', 'size_in_bytes': 1, 'digest': 'sha256:' + '1' * 64,
                'run_id': 7, 'source': 'a' * 40}
    actual = {k: expected[k] for k in ('id', 'name', 'size_in_bytes', 'digest')}
    actual.update(expired=False, workflow_run={'id': 7, 'head_sha': 'a' * 40})
    compact.check_artifact(actual, expected)
    actual[field] = value
    with pytest.raises(ValueError, match='identity/source/run'):
        compact.check_artifact(actual, expected)


def test_extracted_closed_set_and_hashes_reject_extra_file(tmp_path):
    body = b'tiny source'
    source = tmp_path / 'source.txt'
    source.write_bytes(body)
    scope = {'files': {'source.txt': seal(source)}}
    archive = tmp_path / 'core.zip'
    compact.write_zip(archive, {'source.txt': (source, seal(source))},
                      {compact.SCOPE: compact.encoded(scope), 'extra.txt': b'unselected'},
                      compression=zipfile.ZIP_DEFLATED)
    with pytest.raises(ValueError, match='closed file set'):
        compact.extract_core(archive, tmp_path / 'extracted')


@pytest.mark.parametrize('name', ['../outside', '/absolute', '.git/config', 'work/old', 'a\\b'])
def test_package_paths_do_not_escape_or_include_work(name):
    with pytest.raises(ValueError, match='unsafe or excluded'):
        compact.member_name(name)


def test_verifier_imports_only_synthetic_extracted_code_in_isolated_python(tmp_path, monkeypatch):
    """No original report is processed; the ZIP supplies a tiny substitute module."""
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setenv('GITHUB_REPOSITORY', 'reviewer/reproduction-fork')
    monkeypatch.setenv('PYTHONPATH', str(tmp_path / 'invalid-checkout-shadow'))
    source = tmp_path / 'module.py'
    source.write_text('from pathlib import Path\nimport sys\n'
        'def verify_extracted(root):\n'
        '    assert Path(__file__).resolve().is_relative_to(root)\n'
        '    assert Path.cwd() == root\n'
        '    return {"synthetic": True, "isolated": sys.flags.isolated == 1}\n')
    init = tmp_path / 'init.py'
    init.write_bytes(b'')
    entries = {'src/ebpf_discovery/compact_publication.py': (source, seal(source)),
               'src/ebpf_discovery/__init__.py': (init, seal(init))}
    archive = tmp_path / 'core.zip'
    compact.write_zip(archive, entries,
                      {compact.SCOPE: compact.encoded({'files': {k: v[1] for k, v in entries.items()}})},
                      compression=zipfile.ZIP_DEFLATED)
    monkeypatch.setattr(compact, 'selection', lambda root: {'synthetic_selection': True})
    receipt, _, chosen = compact.verify_core(archive)
    assert receipt == {'synthetic': True, 'isolated': True}
    assert chosen == {'synthetic_selection': True}


def test_build_and_verification_require_actual_actions_context(monkeypatch, tmp_path):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    with pytest.raises(ValueError, match='GitHub Actions only'):
        compact.verify_core(tmp_path / 'anything.zip')
    with pytest.raises(ValueError, match='GitHub Actions only'):
        compact.build(tmp_path, tmp_path / 'work')
