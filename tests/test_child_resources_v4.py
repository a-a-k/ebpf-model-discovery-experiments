from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from ebpf_discovery import child_resources_v4


@pytest.mark.skipif(os.name != 'posix', reason='RUSAGE_CHILDREN and POSIX signal semantics are Linux Actions checks')
def test_sigterm_reaches_child_and_resource_report_survives(tmp_path: Path):
    wrapper = Path(child_resources_v4.__file__)
    ready, flushed, report = (tmp_path/name for name in ('ready', 'flushed', 'resources.json'))
    code = '''
import pathlib, signal, sys, time
ready, flushed = map(pathlib.Path, sys.argv[1:])
def finish(_signal, _frame):
    flushed.write_text('published')
    sys.exit(0)
signal.signal(signal.SIGTERM, finish)
payload = bytearray(8 * 1024 * 1024)
payload[::4096] = b'x' * (len(payload) // 4096)
ready.write_text('ready')
while True: time.sleep(.05)
'''
    process = subprocess.Popen([sys.executable, str(wrapper), '--report', str(report), '--',
                                sys.executable, '-c', code, str(ready), str(flushed)])
    try:
        until = time.monotonic() + 10
        while not ready.exists() and time.monotonic() < until:
            if process.poll() is not None:
                pytest.fail(f'wrapper exited before child readiness: {process.returncode}')
            time.sleep(.02)
        assert ready.exists()
        process.terminate()
        assert process.wait(timeout=10) == 0
        assert flushed.read_text() == 'published'
        data = json.loads(report.read_text())
        assert data['exit_status'] == 0
        assert data['forwarded_signals'] == [15]
        assert data['child_peak_rss_kib'] > 0
        assert data['wall_seconds'] > 0
        assert data['child_user_seconds'] >= 0
        assert data['child_system_seconds'] >= 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


@pytest.mark.skipif(os.name != 'posix', reason='RUSAGE_CHILDREN is measured on Linux Actions')
def test_nonzero_child_exit_is_reported_and_propagated(tmp_path: Path):
    report = tmp_path/'resources.json'
    completed = subprocess.run([sys.executable, str(Path(child_resources_v4.__file__)),
                                '--report', str(report), '--', sys.executable, '-c',
                                'raise SystemExit(7)'], check=False, timeout=10)
    assert completed.returncode == 7
    data = json.loads(report.read_text())
    assert data['exit_status'] == 7
    assert data['forwarded_signals'] == []
    assert data['child_peak_rss_kib'] > 0
