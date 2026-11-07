"""Resource safety checks; the only real swap fixture is 128 KiB on Actions Linux."""
import os
from pathlib import Path
import subprocess
import sys

import pytest

from ebpf_discovery import resources_v6 as resources


def setup_owned_work(monkeypatch, tmp_path):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setattr(sys, 'platform', 'linux')
    monkeypatch.setattr(resources, '__file__', str(tmp_path / 'src/ebpf_discovery/resources_v6.py'))
    work = tmp_path / 'work'
    work.mkdir()
    return work


def test_model_swap_never_runs_outside_actions(monkeypatch, tmp_path):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    with pytest.raises(RuntimeError, match='Actions Linux'):
        resources.prepare_model_swap(tmp_path / 'receipt.json')
    assert not list(tmp_path.iterdir())


def test_existing_owned_name_is_preserved_without_provisioning(monkeypatch, tmp_path):
    work = setup_owned_work(monkeypatch, tmp_path)
    path = work / 'v6-model.swap'
    path.write_bytes(b'preserve existing bytes')
    with pytest.raises(FileExistsError):
        resources.prepare_model_swap(tmp_path / 'receipt.json')
    assert path.read_bytes() == b'preserve existing bytes'


def test_swap_reserves_disk_for_existing_archives_before_creating_file(monkeypatch, tmp_path):
    work = setup_owned_work(monkeypatch, tmp_path)
    from ebpf_discovery.block_v6 import RESERVE
    monkeypatch.setattr(resources, 'model_memory_state', lambda _: {
        'disk_free_bytes': resources.MODEL_SWAP_BYTES + RESERVE - 1})
    with pytest.raises(OSError, match='archive/staging reserve'):
        resources.prepare_model_swap(tmp_path / 'receipt.json')
    assert not (work / 'v6-model.swap').exists()


@pytest.mark.skipif(sys.platform != 'linux' or os.environ.get('GITHUB_ACTIONS') != 'true',
                    reason='tiny resource integration fixture is Actions Linux only')
def test_tiny_owned_swap_preserves_platform_swap_and_records_setup(monkeypatch, tmp_path):
    work = setup_owned_work(monkeypatch, tmp_path)
    monkeypatch.setattr(resources, 'MODEL_SWAP_BYTES', 128 * 1024)
    path = work / 'v6-model.swap'
    original_go = {k: os.environ.get(k) for k in resources.GO_OVERRIDES}
    try:
        proof = resources.prepare_model_swap(tmp_path / 'receipt.json')
        assert proof['status'] == 'active'
        assert path.stat().st_size == 128 * 1024
        assert path.stat().st_mode & 0o777 == 0o600
        assert proof['before']['memory']['MemTotal'] == proof['after']['memory']['MemTotal']
        old_paths = {line.split()[0] for line in proof['before']['swaps'].splitlines()[1:]}
        new_paths = {line.split()[0] for line in proof['after']['swaps'].splitlines()[1:]}
        assert old_paths | {str(path)} <= new_paths
        assert len(proof['commands']) == 2
        assert all(c['returncode'] == 0 for c in proof['commands'])
        assert proof['wall_seconds'] > 0
        assert proof['setup_children_CPU_seconds'] >= 0
        assert {k: os.environ.get(k) for k in resources.GO_OVERRIDES} == original_go
    finally:
        active = {line.split()[0] for line in Path('/proc/swaps').read_text().splitlines()[1:]}
        if str(path) in active:
            subprocess.run(['sudo', '-n', 'swapoff', '--', str(path)], check=True)
        if path.exists():
            assert not path.is_symlink() and path.resolve().is_relative_to(tmp_path.resolve())
            path.unlink()
