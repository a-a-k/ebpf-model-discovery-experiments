"""Lossless publication and mutation checks using small synthetic files only."""
import os
import io
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from ebpf_discovery import block_v6 as b
from ebpf_discovery.runtime import write_json


@pytest.fixture
def publication(tmp_path, monkeypatch):
    monkeypatch.setattr(b, 'repo', lambda: tmp_path)
    monkeypatch.setattr(b, 'RESERVE', 0)
    root = tmp_path / 'work' / 'case'
    source = root / 'toolchain' / '.hidden' / 'model.bin'
    source.parent.mkdir(parents=True)
    source.write_bytes(bytes(range(256)))
    source.chmod(0o640)
    os.utime(source, ns=(1700000000000000000, 1700000000000000000))
    relative = source.relative_to(root).as_posix()
    write_json(root / 'forecast-saved.json', {'complete_processing_sha256_by_path': {relative: b.sha(source)}})
    args = SimpleNamespace(root=root, out=root.parent / 'processing-publication')
    return args, source, relative


def test_same_inode_bytes_hidden_file_and_reconstructable_metadata(publication):
    args, source, name = publication
    before = source.stat()
    b.package_processing(args)
    manifest = b.read(args.out / 'processing-manifest.json')
    linked = args.out / 'files' / name
    assert os.path.samefile(source, linked)
    assert linked.read_bytes() == bytes(range(256))
    record = manifest['files'][name]
    assert (record['mode'], record['mtime_ns']) == (before.st_mode & 0o7777, before.st_mtime_ns)
    assert source.stat().st_mtime_ns == before.st_mtime_ns
    assert manifest['scope'] == 'COMPLETE_FROZEN'
    args.manifest_sha256 = b.sha(args.out / 'processing-manifest.json')
    b.verify_processing_publication(args)
    assert b.read(args.root / 'processing-publication-verification.json')['phase'] == 'after_upload'
    assert not list(args.out.parent.glob('*.tar*'))


@pytest.mark.parametrize('mutation', ['bytes', 'unlink', 'extra', 'manifest'])
def test_mutated_publication_is_rejected(publication, mutation):
    args, source, name = publication
    b.package_processing(args)
    args.manifest_sha256 = b.sha(args.out / 'processing-manifest.json')
    if mutation == 'bytes':
        source.write_bytes(b'changed')
    elif mutation == 'unlink':
        linked = args.out / 'files' / name
        data = linked.read_bytes()
        linked.unlink()
        linked.write_bytes(data)
    elif mutation == 'extra':
        (args.out / 'files' / 'unexpected').write_bytes(b'extra')
    else:
        (args.out / 'processing-manifest.json').write_text('{}')
    with pytest.raises(ValueError):
        b.verify_processing_publication(args)


def test_frozen_bytes_and_existing_staging_cannot_be_replaced(publication):
    args, source, _ = publication
    source.write_bytes(b'changed after freeze')
    with pytest.raises(ValueError, match='frozen model'):
        b.package_processing(args)
    with pytest.raises(ValueError, match='new owned'):
        b.package_processing(args)


def test_unfrozen_processing_remains_explicitly_partial(publication):
    args, _, _ = publication
    (args.root / 'forecast-saved.json').unlink()
    b.package_processing(args)
    assert b.read(args.out / 'processing-manifest.json')['scope'] == 'PARTIAL_UNFROZEN'


@pytest.mark.parametrize('name', ['../outside', 'toolchain/a:b', 'toolchain/a?b', 'toolchain/a\nb'])
def test_incompatible_paths_are_rejected_before_linking(publication, name):
    args, _, _ = publication
    with pytest.raises(ValueError):
        b.publication_path(args.root, name)


def test_all_processing_publishers_stream_hidden_files_and_verify_after_upload():
    root = Path(__file__).resolve().parents[1]
    count = 0
    for name in ('series-isolated-v6.yml', 'qualification-replay-v6.yml', 'main-continuation-v6.yml'):
        workflow = yaml.safe_load((root / '.github/workflows' / name).read_text())
        for job in workflow['jobs'].values():
            steps = job.get('steps', [])
            for index, step in enumerate(steps):
                if step.get('id') != 'processingupload':
                    continue
                count += 1
                assert 'processing-publication/' in step['with']['path']
                assert step['with']['include-hidden-files'] is True
                assert step['with']['compression-level'] == 6
                assert 'verify-processing-publication' in steps[index + 1]['run']
                assert 'steps.processingupload.outcome' in steps[index + 1]['if']
    assert count == 6


def test_compressed_portable_archive_preserves_members_with_less_than_uncompressed_free_space(tmp_path, monkeypatch):
    monkeypatch.setattr(b, 'repo', lambda: tmp_path)
    monkeypatch.setattr(b, 'RESERVE', 1024)
    root = tmp_path / 'work' / 'case'
    root.mkdir(parents=True)
    source = root / 'model.json'
    source.write_bytes(b'0' * 100000)
    source.chmod(0o640)
    destination = root.parent / 'model.tar.gz'
    monkeypatch.setattr(b.shutil, 'disk_usage', lambda _: SimpleNamespace(
        free=5000 - (destination.stat().st_size if destination.exists() else 0)))
    with pytest.raises(OSError, match='insufficient actual'):
        b.pack(root, root.parent / 'conservative.tar.gz', {'model.json'})
    b.pack(root, destination, {'model.json'}, guard_compressed_writes=True)
    with tarfile.open(destination, 'r:gz') as archive:
        assert archive.getnames() == ['model.json']
        assert archive.extractfile('model.json').read() == source.read_bytes()
        assert archive.getmember('model.json').mode == source.stat().st_mode & 0o7777
    receipt = b.read(root / 'portable-model-write-guard.json')
    assert receipt['budget'] == 'actual compressed writes'
    assert receipt['compressed_bytes_written'] == destination.stat().st_size
    assert destination.with_suffix('.gz.json').is_file()


def test_compressed_writer_rejects_reserve_breach_and_short_writes(monkeypatch):
    monkeypatch.setattr(b, 'RESERVE', 100)
    guard = {'minimum_free_before_write_bytes': 200, 'compressed_bytes_written': 0}
    monkeypatch.setattr(b.shutil, 'disk_usage', lambda _: SimpleNamespace(free=102))
    writer = b.CompressedModelWriter(io.BytesIO(), Path('.'), guard)
    with pytest.raises(OSError, match='reserve'):
        writer.write(b'abc')
    assert guard['compressed_bytes_written'] == 0
    class ShortWriter:
        def write(self, data):
            return len(data) - 1
    writer = b.CompressedModelWriter(ShortWriter(), Path('.'), guard)
    with pytest.raises(OSError, match='incomplete'):
        writer.write(b'ab')
