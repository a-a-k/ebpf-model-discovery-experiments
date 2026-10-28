from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from ebpf_discovery import campaign_process_v4 as process_v4
from ebpf_discovery import checkpoint_v4


IDENTITY = {"run_id": "17", "commit": "c" * 40,
            "system": "otel_demo", "mode": "full", "seed": 6}


def write(path: Path, value: dict) -> None:
    process_v4._atomic_json(path, value)


def args(tmp_path: Path, **updates):
    value = dict(state_dir=tmp_path/"state", checkpoint=tmp_path/"checkpoint",
                 system="otel_demo", mode="full", seed=6, run_id="17",
                 commit="c" * 40,
                 manifest_sha256="a" * 64, upload_success="true",
                 artifact_id="42", artifact_url="https://example.invalid/42",
                 artifact_digest="sha256:artifact")
    value.update(updates)
    return SimpleNamespace(**value)


def fake_proc(proc_root: Path, pid: int, ticks: int) -> None:
    target = proc_root/str(pid)
    target.mkdir(parents=True)
    # Fields after comm begin at state (field 3); starttime is remainder index 19.
    target.joinpath("stat").write_text(f"{pid} (supervisor) S " + " ".join(
        ["0"] * 18 + [str(ticks)] + ["0"] * 4), encoding="ascii")


def test_release_requires_same_live_cell_and_exact_manifest(tmp_path, monkeypatch):
    proc = tmp_path/"proc"
    fake_proc(proc, 123, 456)
    state, checkpoint = tmp_path/"state", tmp_path/"checkpoint"
    write(state/"started.json", {**IDENTITY, "supervisor_pid": 123,
                                  "supervisor_start_ticks": 456,
                                  "host": socket.gethostname()})
    write(checkpoint/"ready.json", {**IDENTITY, "manifest_sha256": "a" * 64})
    original = process_v4._validate_live
    monkeypatch.setattr(process_v4, "_validate_live",
        lambda state_dir, identity: original(state_dir, identity, proc))
    assert process_v4._release(args(tmp_path)) == 0
    release = json.loads((checkpoint/"release.json").read_text())
    assert release["upload_success"] is True
    assert release["manifest_sha256"] == "a" * 64
    assert release["commit"] == "c" * 40
    assert release["artifact_id"] == "42"

    (checkpoint/"release.json").unlink()
    with pytest.raises(RuntimeError, match="manifest SHA"):
        process_v4._release(args(tmp_path, manifest_sha256="b" * 64))
    assert not (checkpoint/"release.json").exists()


def test_release_is_consumed_by_actual_checkpoint_contract(tmp_path, monkeypatch):
    proc = tmp_path/"proc"
    fake_proc(proc, 123, 456)
    state, checkpoint = tmp_path/"state", tmp_path/"checkpoint"
    ready = {**IDENTITY, "manifest_sha256": "a" * 64}
    write(state/"started.json", {**IDENTITY, "supervisor_pid": 123,
                                  "supervisor_start_ticks": 456,
                                  "host": socket.gethostname()})
    write(checkpoint/"ready.json", ready)
    original = process_v4._validate_live
    monkeypatch.setattr(process_v4, "_validate_live",
        lambda state_dir, identity: original(state_dir, identity, proc))
    assert process_v4._release(args(tmp_path)) == 0

    appended = []
    campaign = SimpleNamespace(ctx=SimpleNamespace(
        journal=SimpleNamespace(append=lambda kind, data: appended.append((kind, data)))))
    release = checkpoint_v4.wait_for_release(campaign, checkpoint, ready)
    assert release["commit"] == ready["commit"]
    assert release["manifest_sha256"] == ready["manifest_sha256"]
    assert appended == [("training_checkpoint_release", release)]


def test_disappeared_or_reused_pid_without_exit_is_technical_error(tmp_path):
    proc = tmp_path/"proc"
    fake_proc(proc, 123, 999)
    state = tmp_path/"state"
    marker = {**IDENTITY, "supervisor_pid": 123, "supervisor_start_ticks": 456,
              "host": socket.gethostname()}
    write(state/"started.json", marker)
    with pytest.raises(RuntimeError, match="disappeared without"):
        process_v4._validate_live(state, IDENTITY, proc)
    write(state/"exit.json", {**IDENTITY, "returncode": 7})
    with pytest.raises(RuntimeError, match="terminal sentinel"):
        process_v4._validate_live(state, IDENTITY, proc)


def test_stop_is_safe_before_start_and_idempotent_after_real_exit(tmp_path):
    stop_args = args(tmp_path)
    assert process_v4._stop(stop_args) == 0
    state = tmp_path/"state"
    write(state/"exit.json", {**IDENTITY, "returncode": 7})
    assert process_v4._stop(stop_args) == 0


def test_stop_never_kills_mismatched_cell(tmp_path, monkeypatch):
    state = tmp_path/"state"
    write(state/"started.json", {**IDENTITY, "seed": 8, "supervisor_pid": 123,
                                  "supervisor_start_ticks": 456,
                                  "host": socket.gethostname()})
    killed = []
    monkeypatch.setattr(process_v4.os, "killpg", lambda *value: killed.append(value), raising=False)
    with pytest.raises(RuntimeError, match="another campaign cell"):
        process_v4._stop(args(tmp_path))
    assert killed == []


def test_default_commands_preserve_full_campaign_and_resource_sampler(tmp_path):
    config = {**IDENTITY, "state_dir": str(tmp_path/"state"),
              "out": str(tmp_path/"out"), "checkpoint": str(tmp_path/"checkpoint"),
              "vms": str(tmp_path/"vms")}
    campaign, resources = process_v4._commands(config)
    assert campaign[:4] == ["/usr/bin/time", "-v", "-o", str(tmp_path/"out"/"infrastructure"/"campaign-time.txt")]
    assert campaign[campaign.index("--training-checkpoint") + 1] == str(tmp_path/"checkpoint")
    assert campaign[campaign.index("--system") + 1] == "otel_demo"
    assert campaign[campaign.index("--mode") + 1] == "full"
    assert campaign[campaign.index("--seed") + 1] == "6"
    assert campaign[campaign.index("--toolchain-execution") + 1] == "local"
    remote, _ = process_v4._commands({**config, "toolchain_execution": "worker"})
    assert remote[remote.index("--toolchain-execution") + 1] == "worker"
    assert resources[0] == "bash"
    assert Path(resources[1]).name == "capture-v4-resources.sh"
    assert resources[-2:] == ["15", str(tmp_path/"vms")]


def test_supervisor_preserves_runner_tracking_for_job_end_cleanup(monkeypatch):
    monkeypatch.setenv("RUNNER_TRACKING_ID", "actions-owned-tree")
    environment = process_v4._supervisor_environment()
    assert environment["RUNNER_TRACKING_ID"] == "actions-owned-tree"


@pytest.mark.skipif(os.name != "posix", reason="process groups and Linux /proc are exercised in Actions")
def test_terminate_group_waits_for_delayed_descendant_after_leader_exits(tmp_path):
    child = tmp_path/"child.py"
    child.write_text('''
import pathlib, signal, sys, time
ready, finished = map(pathlib.Path, sys.argv[1:])
def finish(_s, _f):
    time.sleep(.35)
    finished.write_text("flushed")
    raise SystemExit(0)
signal.signal(signal.SIGTERM, finish)
ready.write_text("ready")
while True: time.sleep(.05)
''')
    leader = tmp_path/"leader.py"
    leader.write_text('''
import pathlib, signal, subprocess, sys, time
child, ready, finished, leader_ready = sys.argv[1:]
subprocess.Popen([sys.executable, child, ready, finished])
until = time.monotonic() + 5
while not pathlib.Path(ready).exists() and time.monotonic() < until: time.sleep(.01)
def finish_leader(_s, _f): raise SystemExit(0)
signal.signal(signal.SIGTERM, finish_leader)
pathlib.Path(leader_ready).write_text("ready")
while True: time.sleep(.05)
''')
    ready, finished, leader_ready = tmp_path/"ready", tmp_path/"finished", tmp_path/"leader-ready"
    process = subprocess.Popen([sys.executable, str(leader), str(child), str(ready),
                                str(finished), str(leader_ready)], start_new_session=True)
    try:
        until = time.monotonic() + 5
        while not leader_ready.exists() and time.monotonic() < until:
            time.sleep(.01)
        assert leader_ready.exists()
        started = time.monotonic()
        result = process_v4._terminate_group(process, grace_seconds=3)
        assert time.monotonic() - started >= .25
        assert result["returncode"] == 0
        assert result["group_drained"] is True
        assert result["forced_kill"] is False
        assert result["remaining_pids"] == []
        assert finished.read_text() == "flushed"
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


@pytest.mark.skipif(os.name != "posix", reason="process groups and Linux /proc are exercised in Actions")
def test_supervisor_forwards_signal_waits_cleanup_and_writes_actual_exit(tmp_path):
    state, out, checkpoint = tmp_path/"state", tmp_path/"out", tmp_path/"checkpoint"
    config = {**IDENTITY, "state_dir": str(state), "out": str(out),
              "checkpoint": str(checkpoint), "vms": str(tmp_path/"vms")}
    child = tmp_path/"child.py"
    child.write_text('''
import pathlib, signal, sys, time
ready, stopped = map(pathlib.Path, sys.argv[1:])
def finish(_s, _f):
    stopped.write_text("stopped")
    raise SystemExit(7)
signal.signal(signal.SIGTERM, finish)
ready.write_text("ready")
while True: time.sleep(.05)
''')
    sampler = tmp_path/"sampler.py"
    sampler.write_text('''
import pathlib, signal, sys, time
target = pathlib.Path(sys.argv[1])
def finish(_s, _f):
    target.write_text("cleaned")
    raise SystemExit(0)
signal.signal(signal.SIGTERM, finish)
while True: time.sleep(.05)
''')
    config_path = tmp_path/"config.json"
    config_path.write_text(json.dumps(config))
    code = (
        "import json,sys; from ebpf_discovery.campaign_process_v4 import supervise; "
        "c=json.load(open(sys.argv[1])); raise SystemExit(supervise(c, "
        "campaign_command=[sys.executable,sys.argv[2],sys.argv[3],sys.argv[4]], "
        "resource_command=[sys.executable,sys.argv[5],sys.argv[6]]))"
    )
    ready, stopped, cleaned = tmp_path/"ready", tmp_path/"stopped", tmp_path/"cleaned"
    supervisor = subprocess.Popen([sys.executable, "-c", code, str(config_path), str(child),
                                   str(ready), str(stopped), str(sampler), str(cleaned)],
                                  start_new_session=True)
    try:
        until = time.monotonic() + 10
        while not ready.exists() and time.monotonic() < until:
            if supervisor.poll() is not None:
                pytest.fail(f"supervisor exited early: {supervisor.returncode}")
            time.sleep(.02)
        assert ready.exists()
        assert process_v4._stop(args(tmp_path)) == 0
        assert supervisor.wait(timeout=10) == 7
        terminal = json.loads((state/"exit.json").read_text())
        assert terminal["returncode"] == 7
        assert terminal["forwarded_signals"] == [signal.SIGTERM]
        assert terminal["cleanup"]["campaign"]["returncode"] == 7
        assert terminal["cleanup"]["resources"]["returncode"] == 0
        assert stopped.read_text() == "stopped" and cleaned.read_text() == "cleaned"
    finally:
        if supervisor.poll() is None:
            supervisor.kill()
            supervisor.wait()
