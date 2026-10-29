from __future__ import annotations

import hashlib
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
