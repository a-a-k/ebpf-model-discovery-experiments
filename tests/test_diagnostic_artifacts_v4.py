import gzip
import hashlib
import json
import os
from pathlib import Path
import tarfile

import pytest

from ebpf_discovery import diagnostic_artifacts_v4 as artifacts


def test_compact_keeps_complete_failure_body_and_scientific_failure(tmp_path):
    source = tmp_path / 'diagnostic'
    runtime = source / 'output/toolchain/combined/network_scope/operation/model-runtime'
    runtime.mkdir(parents=True)
    body = b'\xff\x00' * 10000
    (runtime / 'ingest-error-body.bin').write_bytes(body)
    (runtime / 'ingest-error.json').write_text('{"http_status":500}')
    (source / 'output/status.json').write_text('{"status":"diagnostic_technical_failure"}')
    (source / 'output/observation-index.sqlite').write_bytes(b'retained elsewhere')
    destination = tmp_path / 'compact'
    record = artifacts.compact(source, destination)
    assert (destination / runtime.relative_to(source) / 'ingest-error-body.bin').read_bytes() == body
    assert json.loads((destination / 'output/status.json').read_text())['status'] == 'diagnostic_technical_failure'
    assert not (destination / 'output/observation-index.sqlite').exists()
    assert (source / 'output/observation-index.sqlite').read_bytes() == b'retained elsewhere'
    assert record['scientific_status_unchanged'] is True


def test_package_many_files_binary_unicode_and_empty_directories_losslessly(tmp_path):
    source = tmp_path / 'diagnostic'
    (source / 'empty directory').mkdir(parents=True)
    (source / 'data').mkdir()
    expected = {}
    for index in range(2048):
        name = f'data/{index:04d}.bin'
        payload = index.to_bytes(4, 'little') + b'\x00\xff'
        (source / name).write_bytes(payload)
        expected[name] = payload
    names = ['sp ace', 'unicode-\u00ef', '.hidden']
    if os.name != 'nt':
        names.append('quote"and\nnewline')
    for name in names:
        expected[name] = name.encode()
        (source / name).write_bytes(expected[name])
    destination = tmp_path / 'packaged'
    record = artifacts.package(source, destination)
    assert record['status'] == 'complete'
    assert record['files'] == len(expected) and record['directories'] == 2
    assert record['source_deleted_or_trimmed'] is False
    assert record['exact_paths_bytes_and_current_source_verified'] is True
    archive_path = destination / record['archive_file']
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == record['archive_sha256']
    with tarfile.open(archive_path, 'r:gz') as archive:
        actual = {member.name: archive.extractfile(member).read()
                  for member in archive if member.isfile()}
        assert archive.getmember('empty directory').isdir()
    assert actual == expected
    assert {name: (source / name).read_bytes() for name in expected} == expected
    assert len(list(destination.iterdir())) == 3  # One archive plus two metadata files.


def test_packaging_failure_keeps_compact_and_originals(tmp_path, monkeypatch):
    source = tmp_path / 'diagnostic'
    (source / 'output').mkdir(parents=True)
    (source / 'output/status.json').write_text('{"status":"diagnostic_technical_failure"}')
    compact = tmp_path / 'compact'
    artifacts.compact(source, compact)
    original = (source / 'output/status.json').read_bytes()
    verify = artifacts._verify_archive
    def corrupt_before_verify(root, archive, manifest):
        wire = bytearray(archive.read_bytes())
        wire[-8] ^= 255  # Invalid gzip CRC, without changing any diagnostic input.
        archive.write_bytes(wire)
        verify(root, archive, manifest)
    monkeypatch.setattr(artifacts, '_verify_archive', corrupt_before_verify)
    destination = tmp_path / 'packaged'
    with pytest.raises(gzip.BadGzipFile):
        artifacts.package(source, destination)
    assert (source / 'output/status.json').read_bytes() == original
    assert (compact / 'output/status.json').read_bytes() == original
    record = json.loads((destination / 'packaging.json').read_text())
    assert record['status'] == 'packaging_failed' and record['source_deleted_or_trimmed'] is False


def test_retention_refuses_output_inside_source(tmp_path):
    source = tmp_path / 'diagnostic'
    source.mkdir()
    with pytest.raises(ValueError, match='outside'):
        artifacts.package(source, source / 'archive')
    assert list(source.iterdir()) == []


def test_failed_final_status_write_does_not_hide_primary_error(tmp_path, monkeypatch, capsys):
    source = tmp_path / 'diagnostic'
    source.mkdir()
    (source / 'retained.bin').write_bytes(b'unchanged')
    write = artifacts.write_json
    def fail_status(path, record):
        if record['status'] != 'started':
            raise OSError(28, 'No space left on device')
        write(path, record)
    def failed_verification(*_args):
        raise ValueError('primary verification failure')
    monkeypatch.setattr(artifacts, 'write_json', fail_status)
    monkeypatch.setattr(artifacts, '_verify_archive', failed_verification)
    with pytest.raises(ValueError, match='primary verification failure'):
        artifacts.package(source, tmp_path / 'packaged')
    console = capsys.readouterr().out
    assert 'DIAGNOSTIC_PACKAGING ' in console
    assert 'primary verification failure' in console
    assert 'DIAGNOSTIC_PACKAGING_STATUS_WRITE_ERROR' in console
    assert (source / 'retained.bin').read_bytes() == b'unchanged'


def test_mismatch_sidecar_write_failure_does_not_mask_primary_or_lose_details(
        tmp_path, monkeypatch):
    source = tmp_path / 'diagnostic'
    source.mkdir()
    retained = source / 'retained.bin'
    retained.write_bytes(b'first-version')
    verify = artifacts._verify_archive
    def mutate(root, archive, manifest):
        retained.write_bytes(b'other-version')
        verify(root, archive, manifest)
    monkeypatch.setattr(artifacts, '_verify_archive', mutate)
    write = artifacts.write_json
    def fail_only_sidecar(path, value):
        if Path(path).name == artifacts.MISMATCH:
            raise OSError(28, 'mismatch sidecar disk full')
        write(path, value)
    monkeypatch.setattr(artifacts, 'write_json', fail_only_sidecar)
    destination = tmp_path / 'packaged'
    with pytest.raises(ValueError, match='archive bytes differ from original output'):
        artifacts.package(source, destination)
    record = json.loads((destination / 'packaging.json').read_text())
    assert record['status'] == 'packaging_failed'
    assert record['content_mismatch']['path'] == 'retained.bin'
    assert record['content_mismatch']['phase'] == 'current_source_differs_from_archive'
    assert 'mismatch sidecar disk full' in record['mismatch_file_write_error']
    assert record['mismatch_file'] is None and record['mismatch_file_retained'] is False
    assert not (destination / artifacts.MISMATCH).exists()


def test_source_rehash_unavailable_is_explicit_and_preserves_os_error(tmp_path, monkeypatch):
    source = tmp_path / 'diagnostic'
    source.mkdir()
    retained = source / 'removed.bin'
    retained.write_bytes(b'removed-before-verification')
    verify = artifacts._verify_archive
    def remove_before_verify(root, archive, manifest):
        retained.unlink()
        verify(root, archive, manifest)
    monkeypatch.setattr(artifacts, '_verify_archive', remove_before_verify)
    destination = tmp_path / 'packaged'
    with pytest.raises(FileNotFoundError):
        artifacts.package(source, destination)
    record = json.loads((destination / 'packaging.json').read_text())
    mismatch = record['content_mismatch']
    assert mismatch['path'] == 'removed.bin'
    assert mismatch['phase'] == 'current_source_rehash_unavailable'
    assert mismatch['current_source']['hash_available'] is False
    assert mismatch['current_source']['stat_available'] is False
    assert 'FileNotFoundError' in mismatch['current_source']['hash_error']
    assert 'FileNotFoundError' in mismatch['current_source']['stat_error']
