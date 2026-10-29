from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

from ebpf_discovery import campaign_v5, evaluate_v5


class _Journal:
    def append(self, *args, **kwargs):
        pass

    def export(self, path):
        Path(path).write_text("", encoding="utf-8")

    def close(self):
        pass


def test_full_and_smoke_counts_match_the_fixed_design():
    for system in ("deathstarbench", "otel_demo", "petclinic"):
        _, full, phases, states = evaluate_v5.expected_counts(system, False)
        assert full == {"class_train": 600, "calibration": 6000, "target": 1200,
                        "class_test": 600, "database": 20, "async": 20}
        assert phases == {"class_train": 600, "calibration": 24000,
                          "target": 9600, "class_test": 600}
        assert sum(phases.values()) == 34800
        assert states == {"11": 4800, "10": 2400, "01": 1200, "00": 1200}

        declaration, smoke, phases, states = evaluate_v5.expected_counts(system, True)
        operations = len(declaration.CONTRACTS)
        assert phases == {"class_train": 3 * operations, "calibration": 4 * operations,
                          "target": 8 * operations, "class_test": 3 * operations}
        assert states == {"11": 4 * operations, "10": 2 * operations,
                          "01": operations, "00": operations}
        assert smoke["database"] == operations
        assert smoke["async"] == 1


def test_campaign_drains_before_the_final_store_ingest(tmp_path, monkeypatch):
    calls = []

    class Collector:
        root = tmp_path / "observations"
        drained = False

        def start(self): calls.append("collector-start")
        def settle(self): calls.append("collector-settle")
        def certify_controls(self): calls.append("collector-controls")
        def snapshot(self): calls.append("collector-final-snapshot" if self.drained else "collector-live-snapshot")
        def final_drain(self):
            self.drained = True
            calls.append("collector-drain")
        def close(self): calls.append("collector-close")

    class Adapter:
        def prepare(self): calls.append("prepare")
        def deploy(self): calls.append("deploy")
        def ready(self): calls.append("ready")
        def metadata(self): return {}
        def reset(self): pass
        def set_database(self, value): pass
        def collect_native(self, destination): calls.append("native-" + Path(destination).name)
        def close(self): calls.append("application-close")

    class Store:
        def ingest(self, observations, native):
            calls.append("store-final" if collector.drained else "store-training")
            return {"files": []}
        def close(self): calls.append("store-close")

    collector = Collector()
    collector.root.mkdir()
    value = object.__new__(campaign_v5.CampaignV5)
    value.system = "petclinic"
    value.collector = "obi"
    value.smoke = True
    value.ctx = SimpleNamespace(out=tmp_path, mode="full", seed=6, journal=_Journal())
    value.declaration = SimpleNamespace(CONTRACTS={"operation": {}})
    value.adapter = Adapter()
    value.collectors = collector
    value.store = Store()
    value.rng = __import__("random").Random(6)
    value.records, value.plans, value.frozen = [], [], {}
    value.metadata = {}
    value.training_checkpoint = None
    value.training_release = None
    value.toolchain_execution = "local"
    value.block = lambda phase, state, count, names, reset=True: []
    value.freeze = lambda: calls.append("freeze")
    value.save_records = lambda: None
    monkeypatch.setattr(campaign_v5, "evaluate_classes", lambda *args: calls.append("classes"))
    monkeypatch.setattr(campaign_v5, "evaluate_evidence", lambda *args: calls.append("evidence"))

    value.run()

    assert calls.index("collector-drain") < calls.index("collector-final-snapshot")
    assert calls.index("collector-final-snapshot") < calls.index("store-final")
    assert calls.index("store-final") < calls.index("classes")
    assert json.loads((tmp_path / "status.json").read_text())["status"] == "smoke_complete"


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def test_acquisition_check_consumes_the_closed_drain_contract(tmp_path):
    status = {"protocol_version": "graph-v5", "collector": "obi", "mode": "absent"}
    _write(tmp_path / "observations" / "collector.json", {
        "schema": "collector-lifecycle-v5", "collector": "obi", "source_domain": "ebpf-obi"})
    _write(tmp_path / "observations" / "technical-positive-control.json", {
        "collector": "obi", "selected_ebpf_origin_proven": True,
        "proofs": {"a": {"proven": True}, "b": {"proven": True}}})
    drain = {"collector": "obi", "technical_complete": True,
             "accepted_receiver_bytes_closed_and_hashed": True}
    _write(tmp_path / "observations" / "drain-evidence.json", drain)
    with sqlite3.connect(tmp_path / "observation-index.sqlite") as connection:
        connection.execute("CREATE TABLE spans(source TEXT, service TEXT)")
    declaration = SimpleNamespace(CONTROLLED_SERVICE_ALIASES=["controlled"])

    assert evaluate_v5.acquisition_checks(tmp_path, status, declaration)["valid"] is True
    drain["accepted_receiver_bytes_closed_and_hashed"] = False
    _write(tmp_path / "observations" / "drain-evidence.json", drain)
    report = evaluate_v5.acquisition_checks(tmp_path, status, declaration)
    assert report["valid"] is False
    assert "accepted_observation_capture_not_closed" in report["problems"]


def test_native_coverage_shortfall_remains_an_empirical_result(tmp_path):
    status = {"protocol_version": "graph-v5", "collector": "obi", "mode": "full"}
    _write(tmp_path / "observations" / "collector.json", {
        "schema": "collector-lifecycle-v5", "collector": "obi", "source_domain": "ebpf-obi"})
    _write(tmp_path / "observations" / "technical-positive-control.json", {
        "collector": "obi", "selected_ebpf_origin_proven": True,
        "proofs": {"a": {"proven": True}, "b": {"proven": True}}})
    _write(tmp_path / "observations" / "drain-evidence.json", {
        "collector": "obi", "technical_complete": True,
        "accepted_receiver_bytes_closed_and_hashed": True})
    with sqlite3.connect(tmp_path / "observation-index.sqlite") as connection:
        connection.execute("CREATE TABLE spans(source TEXT, service TEXT)")
        connection.execute("INSERT INTO spans VALUES ('native', 'entry')")
    declaration = SimpleNamespace(CONTROLLED_SERVICE_ALIASES=["controlled"])
    report = evaluate_v5.acquisition_checks(tmp_path, status, declaration)
    assert report["valid"] is True
    assert report["native_observations_by_service"] == {"entry": 1}

    with sqlite3.connect(tmp_path / "observation-index.sqlite") as connection:
        connection.execute("DELETE FROM spans")
    assert evaluate_v5.acquisition_checks(tmp_path, status, declaration)["valid"] is True
    status["mode"] = "partial"
    assert evaluate_v5.acquisition_checks(tmp_path, status, declaration)["valid"] is True
