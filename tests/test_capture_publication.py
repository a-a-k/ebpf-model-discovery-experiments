"""Exercise the complete capture pack/publish and failed-delivery recovery path."""
import hashlib
import json
import os
from pathlib import Path
import tarfile
from types import SimpleNamespace

import pytest

from ebpf_discovery import compose_ack_repair as repair


class Delivery:
    def __init__(self, fail=False):
        self.fail, self.saved = fail, {}

    def publish(self, path):
        if self.fail:
            raise OSError('synthetic Release service unavailable')
        body = Path(path).read_bytes()
        self.saved[Path(path).name] = body
        return {'id': len(self.saved), 'name': Path(path).name, 'size': len(body),
                'digest': 'sha256:' + hashlib.sha256(body).hexdigest(), 'state': 'uploaded'}


def capture(tmp_path, monkeypatch, *, unusual_name=False):
    monkeypatch.setattr(repair.b, 'repo', lambda: tmp_path)
    root = tmp_path / 'work/ack-correction'
    folder = root / 'capture/deployment/upstream/tmp'
    folder.mkdir(parents=True)
    name = 'tester-0*1645152149690-img-0' if unusual_name else 'tester-ordinary'
    body = b'unchanged pinned application source with a legal Linux filename\n'
    (folder / name).write_bytes(body)
    (root / 'capture/external.json').write_text('[{"success":false},{"success":null}]', encoding='utf8')
    (root / 'result.json').write_text('{"technical_complete":true}', encoding='utf8')
    monkeypatch.setenv('GITHUB_RUN_ATTEMPT', '1')
    monkeypatch.setenv('GITHUB_RUN_ID', '123')
    monkeypatch.setenv('GITHUB_SHA', 'a' * 40)
    args = SimpleNamespace(mode='absent', repetition=9, collector='none')
    return root, args, 'deployment/upstream/tmp/' + name, body


def assert_raw(root, args, member, expected):
    raw = repair.target_archive(root, args)
    inventory = json.loads(raw.with_name(raw.name + '.json').read_bytes())
    assert inventory['sha256'] == hashlib.sha256(raw.read_bytes()).hexdigest()
    assert inventory['bytes'] == raw.stat().st_size
    with tarfile.open(raw) as archive:
        assert archive.extractfile(member).read() == expected
        assert json.loads(archive.extractfile('external.json').read()) == [{'success': False}, {'success': None}]
        assert set(archive.getnames()) == set(inventory['files'])
    assert inventory['prepack_actual_disk_guard']['budget'] == 'actual compressed capture writes'
    return raw


@pytest.mark.parametrize('fail', [False, True])
def test_actual_publish_target_and_failed_delivery_retains_verified_container(tmp_path, monkeypatch, fail):
    root, args, member, expected = capture(tmp_path, monkeypatch)
    service = Delivery(fail)
    if fail:
        with pytest.raises(OSError, match='service unavailable'):
            repair.publish_target(service, root, args, None)
    else:
        repair.publish_target(service, root, args, None)
        receipt = json.loads(service.saved['target-absent-9-none-attempt1.json'])
        assert receipt['raw_data']['asset']['digest'].startswith('sha256:')
        assert receipt['result']['technical_complete'] is True
    raw = assert_raw(root, args, member, expected)
    before = raw.read_bytes()
    assert repair.preserve_target(root, args) == raw
    assert raw.read_bytes() == before


@pytest.mark.skipif(os.name == 'nt', reason='the upstream Linux filename is not representable on Windows')
@pytest.mark.parametrize('fail', [False, True])
def test_linux_star_filename_stays_inside_safe_fallback_container(tmp_path, monkeypatch, fail):
    root, args, member, expected = capture(tmp_path, monkeypatch, unusual_name=True)
    service = Delivery(fail)
    if fail:
        with pytest.raises(OSError, match='service unavailable'):
            repair.publish_target(service, root, args, None)
        repair.preserve_target(root, args)
    else:
        repair.publish_target(service, root, args, None)
    raw = assert_raw(root, args, member, expected)
    assert '*' not in raw.name and '*' in member


def test_capture_disk_guard_failure_never_publishes_an_incomplete_archive(tmp_path, monkeypatch):
    root, args, _, _ = capture(tmp_path, monkeypatch)
    monkeypatch.setattr(repair.b, 'capacity', lambda *a: {'free_bytes': 10**30})
    monkeypatch.setattr(repair.b.shutil, 'disk_usage', lambda _: SimpleNamespace(free=0))
    with pytest.raises(OSError, match='reserve'):
        repair.publish_target(Delivery(), root, args, None)
    assert not repair.target_archive(root, args).exists()


def test_recovery_freezes_are_fixed_and_all_36_replacements_selected():
    from ebpf_discovery.compose_ack_recovery import frozen_inputs
    value = frozen_inputs()
    assert value['forecast_run_id'] == 42685277599
    assert len(value['freeze_assets']) == 9
    assert len(value['prior_target_metadata_artifacts']) == 36
    assert value['replacement_scope']['all_cases'] == 36
