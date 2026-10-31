"""Focused checks for the new controller's scientific ordering and isolation."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ebpf_discovery import study
from ebpf_discovery.campaign_process_v4 import _commands


@pytest.fixture
def rig(monkeypatch, tmp_path):
    created = []
    events = []

    class Journal:
        def __init__(self, path):
            created.append("journal")
        def append(self, *args, **kwargs):
            pass
        def unresolved_transports(self):
            return []
        def export(self, path):
            Path(path).write_text("", encoding="utf-8")
        def close(self):
            events.append("journal-close")

    class Store:
        def __init__(self, path, **kwargs):
            created.append("store")
        def close(self):
            events.append("store-close")

    class Adapter:
        def __init__(self, ctx):
            created.append("adapter")
            self.ctx = ctx
        def prepare(self):
            events.append("prepare")
        def deploy(self):
            events.append("deploy")
        def ready(self):
            events.append("ready")
        def metadata(self):
            return {"replicas": []}
        def reset(self):
            pass
        def set_replicas(self, state):
            pass
        def set_database(self, up):
            pass
        def plan_operation(self, name, index, namespace):
            key = f"{namespace}-{index}-{name}"
            return {"attempt_id": key, "http_steps": [{"request_id": key}]}
        def operation(self, name, index, namespace):
            if namespace.startswith(("target-", "class_test-")):
                assert (self.ctx.out / "forecast-saved.json").is_file()
            return {**self.plan_operation(name, index, namespace),
                    "operation": name, "success": True}
        def verify(self, rows):
            return rows
        def close(self):
            events.append("application-close")

    class Collectors:
        def __init__(self, ctx, collector):
            created.append("collector:" + collector)
            self.root = ctx.out / "observations"
        def start(self):
            events.append("collector-start")
        def settle(self):
            pass
        def certify_controls(self):
            events.append("controls")
        def final_drain(self):
            events.append("drain")
        def close(self):
            events.append("collector-close")

    class Toolchain:
        def __init__(self, ctx, system, store, declaration):
            self.ctx = ctx
        def forecast(self, plans):
            assert all(p["phase"] in ("class_train", "calibration") for p in plans)
            assert len(plans) == 28
            events.append("forecast")
            model = self.ctx.out / "toolchain" / "model.json"
            model.parent.mkdir(exist_ok=True)
            model.write_text("{}\n", encoding="utf-8")
            return {}

    def context(out, mode, seed):
        Path(out).mkdir(parents=True, exist_ok=True)
        return SimpleNamespace(out=Path(out), mode=mode, seed=seed)

    def snapshot(self, stage):
        events.append("snapshot:" + stage)
        folder = self.ctx.out / "runtime-identity-v5"
        folder.mkdir(exist_ok=True)
        for name in ("supplied-service-aliases-training.json",
                     "supplied-service-alias-admission-training.json"):
            (folder / name).write_text("{}\n", encoding="utf-8")

    declaration = SimpleNamespace(Adapter=Adapter,
                                  CONTRACTS={name: {} for name in ("owners", "details", "visit", "vets")})
    monkeypatch.setattr(study, "Context", context)
    monkeypatch.setattr(study, "Journal", Journal)
    monkeypatch.setattr(study, "ObservationStoreV5", Store)
    monkeypatch.setattr(study.importlib, "import_module", lambda name: declaration)
    monkeypatch.setattr(study, "make_collectors", Collectors)
    monkeypatch.setattr(study, "Toolchain", Toolchain)
    monkeypatch.setattr(study, "fit_classes", lambda *args: events.append("fit-classes"))
    monkeypatch.setattr(study, "evaluate_classes", lambda *args: events.append("evaluate-classes"))
    monkeypatch.setattr(study, "evaluate_evidence", lambda *args: events.append("evaluate-evidence"))
    monkeypatch.setattr(study, "intent_census", lambda *args: [])
    monkeypatch.setattr(study.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(study.Study, "snapshot", snapshot)
    monkeypatch.setattr(study.Study, "state_barrier", lambda *args: {"fixture": True})
    monkeypatch.setattr(study.Study, "before_workload_block", lambda *args: None)
    monkeypatch.setattr(study.Study, "after_workload_block", lambda *args: None)
    return SimpleNamespace(created=created, events=events, out=tmp_path)


@pytest.mark.parametrize("collector", study.COLLECTORS)
def test_each_collector_constructs_only_final_components_and_freezes_before_targets(rig, collector):
    campaign = study.Study("petclinic", "absent", 6, rig.out, collector=collector, smoke=True)
    assert rig.created == ["journal", "adapter", "collector:" + collector, "store"]
    campaign.run()
    blocks = json.loads((rig.out / "blocks.json").read_text())
    assert [(b["phase"], b["attempts"]) for b in blocks] == (
        [("class_train", 12)] + [("calibration", 4)] * 4 +
        [("target", 4)] * 8 + [("class_test", 12), ("db_up", 4), ("db_down", 4)])
    assert rig.events.index("snapshot:training") < rig.events.index("forecast")
    assert rig.events.index("forecast") < rig.events.index("drain")
    assert json.loads((rig.out / "freeze-integrity.json").read_text())["all_unchanged"]
    status = json.loads((rig.out / "status.json").read_text())
    assert status["controller"] == "clean-study"
    assert status["status"] == "smoke_complete"


def test_modified_frozen_model_is_retained_as_failure(rig, monkeypatch):
    campaign = study.Study("petclinic", "partial", 6, rig.out, collector="obi", smoke=True)
    original_verify = campaign.adapter.verify
    def tamper_after_freeze(rows):
        if rows and rows[0].get("phase") == "target":
            (rig.out / "toolchain" / "model.json").write_text('{"changed":true}\n')
        return original_verify(rows)
    monkeypatch.setattr(campaign.adapter, "verify", tamper_after_freeze)
    with pytest.raises(RuntimeError, match="Frozen discovery or prediction changed"):
        campaign.run()
    assert json.loads((rig.out / "status.json").read_text())["status"] == "technical_failure"
    assert (rig.out / "attempt-journal.jsonl").is_file()
    assert "collector-close" in rig.events


def test_supervisor_selects_study_explicitly_and_preserves_legacy_default(tmp_path):
    config = dict(out=str(tmp_path), system="petclinic", mode="partial", seed=6,
                  checkpoint=str(tmp_path / "checkpoint"), vms=str(tmp_path / "vms"),
                  collector="deepflow", smoke=True)
    command, _ = _commands(config)
    assert command[command.index("-m") + 1] == "ebpf_discovery.campaign_v5"
    command, _ = _commands({**config, "runner": "study"})
    assert command[command.index("-m") + 1] == "ebpf_discovery.study"
    assert command[command.index("--collector") + 1] == "deepflow"
    with pytest.raises(ValueError, match="explicit collector"):
        _commands({**config, "runner": "study", "collector": None})


def test_invalid_cell_is_rejected_before_constructing_components(rig):
    with pytest.raises(ValueError, match="fixed study"):
        study.Study("petclinic", "absent", 99, rig.out, collector="obi")
    assert rig.created == []


@pytest.mark.parametrize('tamper', [False, True])
def test_nested_paired_baseline_is_frozen_before_target_and_later_changes_fail(rig, monkeypatch, tamper):
    original_forecast = study.Toolchain.forecast
    names = ('toolchain/context-baseline/forecasts.json',
             'toolchain/context-baseline/raw/union-proof.json')
    def paired_forecast(self, plans):
        result = original_forecast(self, plans)
        for name in names:
            path = self.ctx.out/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{}\n', encoding='utf-8')
        return result
    monkeypatch.setattr(study.Toolchain, 'forecast', paired_forecast)
    campaign = study.Study('petclinic', 'partial', 6, rig.out, collector='obi', smoke=True)
    original_operation = campaign.adapter.operation
    def operation(name, index, namespace):
        if namespace.startswith('target-'):
            saved = json.loads((rig.out/'forecast-saved.json').read_text())
            assert set(names) <= {Path(key).as_posix() for key in saved['sha256_by_path']}
            if tamper:
                (rig.out/names[0]).write_text('{"changed":true}\n', encoding='utf-8')
        return original_operation(name, index, namespace)
    monkeypatch.setattr(campaign.adapter, 'operation', operation)
    if tamper:
        with pytest.raises(RuntimeError, match='Frozen discovery or prediction changed'):
            campaign.run()
    else:
        campaign.run()
        assert json.loads((rig.out/'freeze-integrity.json').read_text())['all_unchanged']
