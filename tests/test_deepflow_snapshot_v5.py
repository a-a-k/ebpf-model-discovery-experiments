from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from ebpf_discovery.deepflow_snapshot_v5 import snapshot


def test_prefix_snapshot_closes_last_complete_record_and_retains_tail_metadata(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    body = b'{"one":1}\n{"two":2}\n{"pending":'
    (data / "l7_flow_log").write_bytes(body)
    (data / "l4_flow_log").write_bytes(b"not copied live")
    out = tmp_path / "prefix"
    manifest = snapshot(data, out, "prefix")
    expected = b'{"one":1}\n{"two":2}\n'
    assert (out / "l7_flow_log").read_bytes() == expected
    assert not (out / "l4_flow_log").exists()
    item = manifest["files"][0]
    assert item["complete_prefix_bytes"] == len(expected)
    assert item["pending_tail_bytes_at_read"] == len(body) - len(expected)
    assert item["copied_sha256"] == hashlib.sha256(expected).hexdigest()
    assert item["full_file_retained"] is False


def test_final_snapshot_retains_every_file_and_flags_rotation(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "l7_flow_log.pre").write_bytes(b'{"old":1}\n')
    (data / "l7_flow_log").write_bytes(b'{"new":2}\npartial')
    (data / "l4_flow_log").write_bytes(b"opaque l4 bytes")
    out = tmp_path / "final"
    manifest = snapshot(data, out, "final")
    assert manifest["l7_rotation_observed"] is True
    assert manifest["rotation_observed"] is True
    for name in ("l7_flow_log.pre", "l7_flow_log", "l4_flow_log"):
        assert (out / name).read_bytes() == (data / name).read_bytes()
    current = next(item for item in manifest["files"] if item["source_name"] == "l7_flow_log")
    assert current["pending_tail_bytes_at_read"] == len(b"partial")
    assert current["full_file_retained"] is True


def test_failure_snapshot_retains_pending_tail_and_non_l7_without_closure_claim(
        tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    l7 = b'{"complete":true}\n{"pending":'
    other = b"sole agent error\n"
    (data / "l7_flow_log").write_bytes(l7)
    (data / "deepflow-agent.log").write_bytes(other)
    out = tmp_path / "failure"
    manifest = snapshot(data, out, "failure")
    assert (out / "l7_flow_log").read_bytes() == l7
    assert (out / "deepflow-agent.log").read_bytes() == other
    current = next(item for item in manifest["files"]
                   if item["source_name"] == "l7_flow_log")
    assert current["pending_tail_bytes_at_read"] == len(b'{"pending":')
    assert current["full_file_retained"] is True
    assert manifest["startup_incomplete"] is True
    assert manifest["producer_closed"] is False
    assert manifest["closed_checkpoint"] is False


def test_snapshot_output_is_fresh_and_never_overwritten(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "l7_flow_log").write_bytes(b"{}\n")
    out = tmp_path / "snapshot"
    snapshot(data, out, "prefix")
    with pytest.raises(FileExistsError):
        snapshot(data, out, "prefix")


def test_closed_final_links_keep_exact_copy_manifest_bytes_and_originals(tmp_path, capsys):
    data = tmp_path / "data"
    data.mkdir()
    files = {"l7_flow_log": b'{"one":1}\npartial', "agent.log": b"all diagnostics\x00\xff"}
    for name, body in files.items():
        (data / name).write_bytes(body)
    original_modes = {name: (data / name).stat().st_mode for name in files}
    old = tmp_path / "copy"
    linked = tmp_path / "linked"
    snapshot(data, old, "final")
    snapshot(data, linked, "final", producer_closed=True)
    assert (old / "snapshot.json").read_bytes() == (linked / "snapshot.json").read_bytes()
    for name, body in files.items():
        assert (data / name).read_bytes() == (old / name).read_bytes() == (linked / name).read_bytes() == body
        assert os.path.samefile(data / name, linked / name)
        assert not os.path.samefile(data / name, old / name)
        assert (data / name).stat().st_mode == (linked / name).stat().st_mode
        assert (data / name).stat().st_mode == original_modes[name]
    audit = json.loads(capsys.readouterr().out)
    assert audit["logical_bytes_retained"] == sum(map(len, files.values()))
    assert audit["source_paths_unlinked"] is False
    assert not (linked / "snapshot-storage.json").exists()


@pytest.mark.parametrize("mode", ["prefix", "failure"])
def test_live_or_failure_capture_cannot_request_final_hardlinks(tmp_path, mode):
    data = tmp_path / "data"
    data.mkdir()
    (data / "l7_flow_log").write_bytes(b"{}\n")
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="explicit producer closure"):
        snapshot(data, out, mode, producer_closed=True)
    assert not out.exists()
    assert (data / "l7_flow_log").read_bytes() == b"{}\n"


def test_default_final_remains_a_real_copy_without_positive_closure(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    source = data / "l7_flow_log"
    source.write_bytes(b"{}\n")
    out = tmp_path / "out"
    snapshot(data, out, "final")
    source.write_bytes(b"changed after unproved closure\n")
    assert (out / "l7_flow_log").read_bytes() == b"{}\n"


def test_link_failure_preserves_source_without_hidden_copy_fallback(tmp_path, monkeypatch):
    import ebpf_discovery.deepflow_snapshot_v5 as helper
    data = tmp_path / "data"
    data.mkdir()
    source = data / "l7_flow_log"
    source.write_bytes(b"{}\n")
    def unavailable(*args, **kwargs):
        raise OSError("cross-device or unavailable hardlink")
    monkeypatch.setattr(helper.os, "link", unavailable)
    out = tmp_path / "out"
    with pytest.raises(OSError, match="unavailable hardlink"):
        snapshot(data, out, "final", producer_closed=True)
    assert source.read_bytes() == b"{}\n"
    assert not (out / "l7_flow_log").exists()
    assert not (out / "snapshot.json").exists()


def test_source_mutation_during_hash_rejects_link_and_keeps_source(tmp_path, monkeypatch):
    import ebpf_discovery.deepflow_snapshot_v5 as helper
    data = tmp_path / "data"
    data.mkdir()
    source = data / "l7_flow_log"
    source.write_bytes(b"{}\n")
    original = helper._sha256
    def mutate(path, limit=None):
        result = original(path, limit)
        with source.open("ab") as stream:
            stream.write(b"unexpected writer\n")
        return result
    monkeypatch.setattr(helper, "_sha256", mutate)
    out = tmp_path / "out"
    with pytest.raises(RuntimeError, match="source changed"):
        snapshot(data, out, "final", producer_closed=True)
    assert source.read_bytes().endswith(b"unexpected writer\n")
    assert not (out / "l7_flow_log").exists()


def test_existing_link_target_is_never_overwritten(tmp_path):
    from ebpf_discovery.deepflow_snapshot_v5 import _link_closed_final
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.write_bytes(b"source")
    target.write_bytes(b"independent existing bytes")
    with pytest.raises(FileExistsError):
        _link_closed_final(source, target, source.stat().st_size)
    assert source.read_bytes() == b"source"
    assert target.read_bytes() == b"independent existing bytes"


def test_final_hardlink_rejects_symlink_without_touching_original(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    original = tmp_path / "outside-original"
    original.write_bytes(b"original standalone bytes\n")
    link = data / "l7_flow_log"
    try:
        link.symlink_to(original)
    except OSError:
        pytest.skip("symlink creation requires unavailable local privilege")
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="non-symlink"):
        snapshot(data, out, "final", producer_closed=True)
    assert original.read_bytes() == b"original standalone bytes\n"
    assert link.is_symlink()
    assert not (out / "l7_flow_log").exists()
