import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml


@pytest.fixture
def control():
    path = Path(__file__).resolve().parents[1] / "scripts/control-closed-offline-resources-v5.py"
    spec = importlib.util.spec_from_file_location("fixed_closed_resource_control", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _environment(control, monkeypatch, tmp_path, seed=7):
    v = control.ORIGINALS[seed]
    fields = ("SCIENTIFIC_CAPTURE_RUN_ID", "SCIENTIFIC_CAPTURE_SOURCE", "CAPTURE_ARTIFACT_ID",
              "CAPTURE_ARTIFACT_DIGEST", "CAPTURE_ARCHIVE_BYTES", "CAPTURE_FILE_BYTES",
              "CAPTURE_PROOF_BYTES", "CAPTURE_INDEX_BYTES", "CAPTURE_MANIFEST_SHA256")
    for key, value in zip(fields, v):
        monkeypatch.setenv(key, str(value))
    for key, value in {"CAPTURE_SEED": seed, "CAPTURE_MODE": "absent", "GITHUB_ACTIONS": "true",
                       "GITHUB_WORKSPACE": tmp_path, "GITHUB_RUN_ID": "999999",
                       "GITHUB_SHA": "c" * 40,
                       "GITHUB_REPOSITORY": "a-a-k/ebpf-model-discovery-experiments"}.items():
        monkeypatch.setenv(key, str(value))
    monkeypatch.chdir(tmp_path)
    return control._context()


@pytest.mark.parametrize("seed, expected", [(7, 126154964613), (8, 123052236136)])
def test_whole_original_peak_plus_swap_matches_actual_closed_metadata(control, seed, expected):
    v = control.ORIGINALS[seed]
    assert control.required_before_swap(v[4], v[5], v[6], v[7]) == expected
    # Eight additional GiB would exceed the previously observed 127.38GB host.
    assert expected - control.SWAP_BYTES + 8 * control.GIB > 127382827008


def test_insufficient_capacity_stops_before_any_allocation(control, monkeypatch, tmp_path):
    c = _environment(control, monkeypatch, tmp_path)
    required = control.required_before_swap(c["Z"], c["F"], c["P"], c["I"])
    monkeypatch.setattr(control, "_actions_only", lambda: None)
    monkeypatch.setattr(control.shutil, "disk_usage", lambda _: SimpleNamespace(free=required - 1))
    def forbidden(*args, **kwargs):
        raise AssertionError("No memory probe, sudo or file allocation before the disk guard")
    monkeypatch.setattr(control, "_meminfo", forbidden)
    monkeypatch.setattr(control.subprocess, "run", forbidden)
    with pytest.raises(RuntimeError, match="Insufficient actual disk"):
        control.prepare()
    assert not (c["work"] / "closed-offline-swapfile").exists()
    assert json.loads((c["host"] / "resource-prepare.json").read_text())["status"] == "failed"


def test_wrong_original_index_size_is_rejected(control, monkeypatch, tmp_path):
    _environment(control, monkeypatch, tmp_path)
    monkeypatch.setenv("CAPTURE_INDEX_BYTES", "1")
    with pytest.raises(ValueError, match="exact original"):
        control._context()


def test_workflow_preserves_source_binding_and_qualified_step_order(control):
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/infrastructure.yml").read_text(encoding="utf-8"))
    job = workflow["jobs"]["recover"]
    env, steps = job["env"], job["steps"]
    seed = int(env["CAPTURE_SEED"])
    v = control.ORIGINALS[seed]
    assert env["SCIENTIFIC_CAPTURE_RUN_ID"] == v[0]
    assert env["SCIENTIFIC_CAPTURE_SOURCE"] == v[1]
    assert int(env["CAPTURE_FILE_BYTES"]) == v[5]
    assert int(env["CAPTURE_PROOF_BYTES"]) == v[6]
    assert int(env["CAPTURE_INDEX_BYTES"]) == v[7]
    assert env["CAPTURE_MANIFEST_SHA256"] == v[8]
    assert len(steps) == 12
    assert steps[3]["run"].rstrip().endswith("control-closed-offline-resources-v5.py prepare")
    assert "Restore the exact closed capture" in steps[4]["name"]
    assert f"--capture-run-id {v[0]} --capture-source {v[1]}" in steps[4]["run"]
    assert steps[5]["run"] == "python scripts/control-closed-offline-resources-v5.py run"
    assert "Evaluate retained full campaign" in steps[7]["name"]
    assert steps[11]["if"] == "always()"


def _ready_for_synthetic_child(control, monkeypatch, tmp_path):
    c = _environment(control, monkeypatch, tmp_path)
    ready = {k: c[k] for k in ("capture_source", "processing_run_id", "processing_source")}
    ready.update(status="ready", requested_swap_bytes=control.SWAP_BYTES)
    (c["host"] / "resource-prepare.json").write_text(json.dumps(ready))
    (c["host"] / "disk-before-processing.json").write_text(json.dumps({"required_bytes": 4 * c["I"] + control.GIB}))
    monkeypatch.setattr(control.shutil, "disk_usage", lambda _: SimpleNamespace(free=10**15))
    return c


@pytest.mark.skipif(sys.platform != "linux" or not shutil.which("ionice"), reason="Linux owned-child priority integration")
def test_nonzero_synthetic_child_is_reaped_and_does_not_change_parent_priority(control, monkeypatch, tmp_path, capfd):
    c = _ready_for_synthetic_child(control, monkeypatch, tmp_path)
    before = Path("/proc/self/oom_score_adj").read_text()
    code = "import json,os,pathlib; print('CHILD_PRIORITY '+json.dumps({'nice':os.getpriority(os.PRIO_PROCESS,0),'oom':int(pathlib.Path('/proc/self/oom_score_adj').read_text())}),flush=True); raise SystemExit(7)"
    monkeypatch.setattr(control, "_finalize_argv", lambda _: [sys.executable, "-c", code])
    assert control.run() == 7
    child = json.loads(next(line.removeprefix("CHILD_PRIORITY ") for line in capfd.readouterr().out.splitlines() if line.startswith("CHILD_PRIORITY ")))
    assert child["nice"] >= 10 and child["oom"] >= 500
    assert Path("/proc/self/oom_score_adj").read_text() == before
    result = json.loads((c["host"] / "processing-child-result.json").read_text())
    assert result["status"] == "child_failed"
    assert result["child_returncode"] == result["final_child_returncode"] == 7
    assert result["model_refit"] is result["new_application_traffic"] is False


@pytest.mark.skipif(sys.platform != "linux" or not shutil.which("ionice"), reason="Linux owned-child interruption integration")
def test_interruption_reaps_only_owned_child_and_keeps_failure_diagnostics(control, monkeypatch, tmp_path):
    c = _ready_for_synthetic_child(control, monkeypatch, tmp_path)
    monkeypatch.setattr(control, "_finalize_argv", lambda _: [sys.executable, "-c", "import time; time.sleep(60)"])
    children, original = [], subprocess.Popen
    def remember(*args, **kwargs):
        child = original(*args, **kwargs)
        children.append(child)
        return child
    monkeypatch.setattr(control.subprocess, "Popen", remember)
    def interrupt(*args):
        raise KeyboardInterrupt("synthetic interruption")
    monkeypatch.setattr(control, "_sample", interrupt)
    with pytest.raises(KeyboardInterrupt, match="synthetic interruption"):
        control.run()
    assert len(children) == 1 and children[0].poll() is not None
    result = json.loads((c["host"] / "processing-child-result.json").read_text())
    assert result["status"] == "interrupted_or_failed"
    assert result["final_child_returncode"] < 0
