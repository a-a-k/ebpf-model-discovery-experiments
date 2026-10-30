import json
import hashlib
import os
from pathlib import Path
import signal
import shlex
import subprocess
import sys
import time

import pytest

from ebpf_discovery import worker_process_group_v4 as owned


POSIX_ONLY = pytest.mark.skipif(os.name != "posix", reason="POSIX process-group contract")


def _wait_for(path: Path, process: subprocess.Popen) -> None:
    deadline = time.monotonic() + 10
    while not path.exists():
        if process.poll() is not None:
            raise AssertionError(f"supervisor exited early: {process.returncode}")
        if time.monotonic() >= deadline:
            raise AssertionError("writer readiness fixture timed out")
        time.sleep(0.01)


@POSIX_ONLY
def test_owned_descendant_writer_is_joined_before_output_is_stable(tmp_path):
    writer = tmp_path / "writer.py"
    ready, output = tmp_path / "ready", tmp_path / "samples.jsonl"
    writer.write_text(
        "import pathlib,signal,time,sys\n"
        "out=pathlib.Path(sys.argv[1]); ready=pathlib.Path(sys.argv[2])\n"
        "stop=False\n"
        "def term(*_):\n global stop; stop=True\n"
        "signal.signal(signal.SIGTERM,term)\n"
        "with out.open('a') as stream:\n"
        " ready.write_text('ready')\n"
        " while not stop:\n  stream.write('sample\\n'); stream.flush(); time.sleep(.01)\n",
        encoding="utf-8")
    evidence = tmp_path / "lifecycle.json"
    # Bash is the direct child and the Python writer is its descendant. Both
    # share only the supervisor-owned session/process group.
    command = [sys.executable, "-m", "ebpf_discovery.worker_process_group_v4",
               "--evidence", str(evidence), "--label", "fixture", "--",
               "bash", "-c", " ".join(map(shlex.quote,
                   (sys.executable, str(writer), str(output), str(ready)))) + " & wait"]
    process = subprocess.Popen(command)
    _wait_for(ready, process)
    process.send_signal(signal.SIGTERM)
    assert process.wait(timeout=10) == 0
    proof = json.loads(evidence.read_text(encoding="utf-8"))
    assert proof["status"] == "stopped_and_joined"
    assert proof["group_absent_after_join"] is True
    assert proof["stop_signals_received"] == [signal.SIGTERM]
    assert proof["fixed_quiescence_sleep_or_timeout"] is False
    retained = output.read_bytes()
    time.sleep(0.1)  # Observation only after kernel group-absence proof.
    assert output.read_bytes() == retained


@POSIX_ONLY
def test_unrequested_writer_exit_is_technical_failure(tmp_path):
    evidence = tmp_path / "lifecycle.json"
    result = subprocess.run(
        [sys.executable, "-m", "ebpf_discovery.worker_process_group_v4",
         "--evidence", str(evidence), "--label", "fixture", "--",
         sys.executable, "-c", "pass"], check=False)
    assert result.returncode == 1
    proof = json.loads(evidence.read_text(encoding="utf-8"))
    assert proof["status"] == "unexpected_exit"
    assert proof["group_absent_after_join"] is True
    assert proof["stop_signals_received"] == []


@POSIX_ONLY
def test_stop_recorded_before_popen_return_is_replayed_to_owned_group(tmp_path, monkeypatch):
    killed = []
    class Child:
        pid = 424201
        returncode = None
        def __init__(self, *_args, **kwargs):
            assert kwargs["start_new_session"] is True
            os.kill(os.getpid(), signal.SIGTERM)
        def poll(self):
            return self.returncode
        def wait(self):
            self.returncode = -signal.SIGTERM
            return self.returncode
    monkeypatch.setattr(owned.subprocess, "Popen", Child)
    monkeypatch.setattr(owned.os, "killpg", lambda pgid, signum: killed.append((pgid, signum)))
    monkeypatch.setattr(owned, "_group_exists", lambda _pgid: False)
    evidence = tmp_path / "early-stop.json"
    assert owned.run(["fixture"], evidence, "early-stop") == 0
    proof = json.loads(evidence.read_text())
    assert killed == [(Child.pid, signal.SIGTERM)]
    assert proof["stop_signals_received"] == [signal.SIGTERM]
    assert proof["group_absent_after_join"] is True


@POSIX_ONLY
def test_stop_after_leader_exit_still_signals_surviving_owned_group(tmp_path, monkeypatch):
    killed = []
    group_checks = iter((True, False, False))
    class Child:
        pid = 424202
        returncode = None
        def __init__(self, *_args, **_kwargs):
            pass
        def poll(self):
            return self.returncode
        def wait(self):
            self.returncode = 0  # Leader is already exited when stop is delivered.
            os.kill(os.getpid(), signal.SIGTERM)
            return self.returncode
    monkeypatch.setattr(owned.subprocess, "Popen", Child)
    monkeypatch.setattr(owned.os, "killpg", lambda pgid, signum: killed.append((pgid, signum)))
    monkeypatch.setattr(owned, "_group_exists", lambda _pgid: next(group_checks))
    monkeypatch.setattr(owned.time, "sleep", lambda _seconds: None)
    evidence = tmp_path / "leader-exited.json"
    assert owned.run(["fixture"], evidence, "leader-exited") == 0
    proof = json.loads(evidence.read_text())
    assert killed == [(Child.pid, signal.SIGTERM)]
    assert proof["child_returncode"] == 0
    assert proof["group_absent_after_join"] is True


def test_package_gate_fails_closed_on_unquiesced_group(tmp_path):
    helper = Path(owned.__file__)
    source = tmp_path / "source.json"
    source.write_text(json.dumps({
        "schema_version": "worker-lifecycle-helper-source-v4",
        "workflow_sha": "a" * 40,
        "path": "src/ebpf_discovery/worker_process_group_v4.py",
        "bytes": helper.stat().st_size,
        "sha256": hashlib.sha256(helper.read_bytes()).hexdigest(),
    }))
    lifecycle = tmp_path / "lifecycle.json"
    lifecycle.write_text(json.dumps({
        "schema_version": owned.SCHEMA, "status": "stopped_and_joined",
        "group_absent_after_join": True,
        "fixed_quiescence_sleep_or_timeout": False,
        "stop_signals_received": [signal.SIGTERM],
    }))
    gate_path = tmp_path / "gate.json"
    gate = owned.verify_lifecycle(lifecycle, source, helper, "a" * 40, gate_path)
    assert gate["complete_typed_package_permitted"] is True
    assert json.loads(gate_path.read_text()) == gate
    changed = json.loads(lifecycle.read_text())
    changed["group_absent_after_join"] = False
    lifecycle.write_text(json.dumps(changed))
    failed = owned.verify_lifecycle(lifecycle, source, helper, "a" * 40, gate_path)
    assert failed["status"] == "technical_failure"
    assert failed["checks"]["owned_group_absent"] is False
    assert failed["complete_typed_package_permitted"] is False
