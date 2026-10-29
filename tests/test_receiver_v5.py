from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from ebpf_discovery.receiver import _capture_wire_body
from ebpf_discovery.receiver_v5 import _file, _raw_capture_audit


def _port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


@pytest.mark.skipif(
    os.name == "nt",
    reason="Popen.terminate uses TerminateProcess, not catchable POSIX SIGTERM",
)
def test_sigterm_joins_requests_and_hashes_saved_raw_bytes(tmp_path: Path) -> None:
    port = _port()
    output = tmp_path / "a.jsonl"
    checkpoint = tmp_path / "receiver-closed-a.json"
    environment = dict(os.environ)
    source_root = str(Path(__file__).parents[1] / "src")
    environment["PYTHONPATH"] = source_root + os.pathsep + environment.get("PYTHONPATH", "")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "ebpf_discovery.receiver_v5",
            "--port",
            str(port),
            "--out",
            str(output),
            "--source",
            "ebpf-obi:a",
            "--node",
            "a",
            "--checkpoint",
            str(checkpoint),
        ],
        env=environment,
    )
    try:
        deadline = time.monotonic() + 10
        while True:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    break
            except OSError:
                if process.poll() is not None or time.monotonic() >= deadline:
                    raise AssertionError("receiver did not start")
                time.sleep(0.05)
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/traces",
            data=b'{"resourceSpans":[]}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            assert response.status == 200
        process.terminate()
        assert process.wait(timeout=10) == 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)

    saved = json.loads(checkpoint.read_text())
    assert saved["in_flight_handlers_joined"] is True
    assert saved["listening_socket_closed"] is True
    assert saved["saved_bytes_valid"] is True
    assert saved["wrapper"]["complete_jsonl"] is True
    assert saved["wrapper"]["sha256"]
    assert saved["raw_capture"]["capture_count"] == 1
    assert saved["raw_capture"]["captures"][0]["valid"] is True
    assert "not proven absent" in saved["scope"]


def test_saved_byte_audit_hashes_complete_jsonl_and_wire_capture(tmp_path: Path) -> None:
    output = tmp_path / "a.jsonl"
    output.write_text('{"complete":true}\n', encoding="utf-8")

    class Headers(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    capture = _capture_wire_body(
        output,
        b'{"resourceSpans":[]}',
        source="ebpf-obi:a",
        node="a",
        received_ns=1,
        headers=Headers({"Content-Type": "application/json"}),
    )
    wrapper = _file(output)
    raw = _raw_capture_audit(output)
    assert wrapper["complete_jsonl"] is True
    assert wrapper["sha256"]
    assert raw["errors"] == []
    assert raw["captures"][0]["raw_sha256"] == capture["raw_sha256"]
    assert raw["captures"][0]["raw_size_bytes"] == len(b'{"resourceSpans":[]}')
    assert raw["captures"][0]["metadata_sha256"]


def test_saved_byte_audit_rejects_incomplete_capture_directory(tmp_path: Path) -> None:
    output = tmp_path / "a.jsonl"
    incomplete = output.with_suffix(".raw") / ".unfinished.tmp"
    incomplete.mkdir(parents=True)
    raw = _raw_capture_audit(output)
    assert raw["captures"] == []
    assert "incomplete raw capture directory" in raw["errors"][0]
