"""Retain compact failure evidence first, then lossless diagnostic output."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tarfile
import time

from .runtime import write_json


def _sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _roots(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if (source == destination or source.is_relative_to(destination)
            or destination.is_relative_to(source)):
        raise ValueError('retention destination must be outside the source tree')
    if not source.is_dir():
        raise ValueError('diagnostic source directory is missing')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('retention destination must be fresh')
    destination.mkdir(parents=True, exist_ok=True)
    return source, destination


def _entries(root):
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs.sort()
        for name in sorted([*dirs, *files]):
            path = Path(directory) / name
            mode = path.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError(f'unsupported diagnostic file type: {path.relative_to(root)}')
            yield path, {'path': path.relative_to(root).as_posix(),
                         'type': 'directory' if stat.S_ISDIR(mode) else 'file',
                         'mode': stat.S_IMODE(mode),
                         'bytes': 0 if stat.S_ISDIR(mode) else path.stat().st_size}


def compact(source, destination):
    source, destination = _roots(source, destination)
    paths = []
    for directory in ('infrastructure', 'source-metadata'):
        root = source / directory
        if root.is_dir():
            paths.extend(path for path, row in _entries(root) if row['type'] == 'file')
    for name in ('status.json', 'checkpoint-validation.json', 'diagnostic-provenance.json',
                 'toolchain-provenance.json'):
        path = source / 'output' / name
        if path.is_file():
            paths.append(path)
    toolchain = source / 'output' / 'toolchain'
    runtimes = [*toolchain.glob('discovery/*/*/observed-runtime'),
                *toolchain.glob('*/*/*/model-runtime')]
    for runtime in runtimes:
        for name in ('replay-command.json', 'bering-resources.json', 'bering.log',
                     'ingest-error.json', 'ingest-error-body.bin'):
            path = runtime / name
            if path.is_file():
                paths.append(path)
    rows = []
    for path in sorted(set(paths)):
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError('compact evidence is redirected outside the source')
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        digest = _sha(path)
        if _sha(target) != digest:
            raise ValueError('compact evidence copy changed')
        rows.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': digest})
    record = {'schema_version': 'v4-compact-diagnostic-evidence', 'files': rows,
              'scope': 'Explicit status, provenance, infrastructure and tool failure files; not a full output archive',
              'scientific_status_unchanged': True}
    write_json(destination / 'compact-manifest.json', record)
    print(json.dumps({'compact_evidence_files': len(rows), 'destination': str(destination)}), flush=True)
    return record


def _tree_line(row):
    return (json.dumps({key: row[key] for key in ('path', 'type', 'mode', 'bytes')},
                       sort_keys=True) + '\n').encode()


def _verify_archive(source, archive_path, manifest_path):
    expected_tree = hashlib.sha256()
    with manifest_path.open(encoding='utf-8') as manifest, gzip.open(archive_path, 'rb') as wire:
        with tarfile.open(fileobj=wire, mode='r|') as archive:
            for member in archive:
                line = manifest.readline()
                if not line:
                    raise ValueError('archive has an unmanifested member')
                row = json.loads(line)
                if (member.name != row['path'] or member.mode != row['mode']
                        or member.size != row['bytes']
                        or (member.isdir() if row['type'] == 'directory' else member.isfile()) is not True):
                    raise ValueError('archive member identity differs from manifest')
                expected_tree.update(_tree_line(row))
                if member.isfile():
                    payload = archive.extractfile(member)
                    actual = hashlib.file_digest(payload, 'sha256').hexdigest()
                    if actual != row['sha256'] or _sha(source / row['path']) != actual:
                        raise ValueError('archive bytes differ from original output')
                archive.members.clear()  # Streaming verification must not retain every TarInfo.
            if manifest.readline():
                raise ValueError('archive omitted a manifested member')
        while wire.read(1024 * 1024):
            pass  # Consume gzip trailer and verify CRC even after tar end markers.
    actual_tree = hashlib.sha256()
    for _, row in _entries(source):
        actual_tree.update(_tree_line(row))
    if actual_tree.digest() != expected_tree.digest():
        raise ValueError('original output tree changed during packaging')


def package(source, destination):
    source, destination = _roots(source, destination)
    archive_path = destination / 'diagnostic-output.tar.gz'
    manifest_path = destination / 'output-manifest.jsonl'
    record = {'schema_version': 'v4-lossless-diagnostic-package', 'status': 'started',
              'started_ns': time.time_ns(), 'source': str(source),
              'files': 0, 'directories': 0, 'uncompressed_file_bytes': 0,
              'free_bytes_before': shutil.disk_usage(destination).free,
              'source_deleted_or_trimmed': False}
    started = time.monotonic()
    write_json(destination / 'packaging.json', record)
    try:
        with manifest_path.open('w', encoding='utf-8') as manifest, \
                gzip.open(archive_path, 'wb', compresslevel=1) as wire:
            with tarfile.open(fileobj=wire, mode='w|', dereference=True) as archive:
                for path, row in _entries(source):
                    info = archive.gettarinfo(str(path), arcname=row['path'])
                    if row['type'] == 'file':
                        row['sha256'] = _sha(path)
                        with path.open('rb') as payload:
                            archive.addfile(info, payload)
                        record['files'] += 1
                        record['uncompressed_file_bytes'] += row['bytes']
                    else:
                        archive.addfile(info)
                        record['directories'] += 1
                    archive.members.clear()
                    manifest.write(json.dumps(row, sort_keys=True) + '\n')
        _verify_archive(source, archive_path, manifest_path)
        record.update(status='complete', archive_file=archive_path.name,
                      archive_bytes=archive_path.stat().st_size, archive_sha256=_sha(archive_path),
                      manifest_file=manifest_path.name, manifest_sha256=_sha(manifest_path),
                      exact_paths_bytes_and_current_source_verified=True,
                      gzip_crc_verified=True,
                      extraction='Verify SHA-256; gzip -t diagnostic-output.tar.gz; extract into a fresh directory using tar -xzf diagnostic-output.tar.gz')
        return record
    except BaseException as error:
        record.update(status='packaging_failed', error=repr(error))
        raise
    finally:
        record.update(ended_ns=time.time_ns(), elapsed_seconds=time.monotonic() - started,
                      free_bytes_after=shutil.disk_usage(destination).free)
        print('DIAGNOSTIC_PACKAGING ' + json.dumps(record), flush=True)
        try:
            write_json(destination / 'packaging.json', record)
        except OSError as error:
            print('DIAGNOSTIC_PACKAGING_STATUS_WRITE_ERROR ' + repr(error), flush=True)
            if record['status'] != 'packaging_failed':
                raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('compact', 'package'))
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    (compact if args.operation == 'compact' else package)(args.source, args.out)


if __name__ == '__main__':
    main()
