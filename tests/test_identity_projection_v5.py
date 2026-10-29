from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ebpf_discovery.deepflow_codec_v5 import codec_file
from ebpf_discovery.identity_projection_v5 import refresh
from ebpf_discovery.observations import attributes
from ebpf_discovery.raw_v4 import export_selection
from ebpf_discovery.store_v5 import ObservationStoreV5
from ebpf_discovery.transport_v4 import Journal


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _sample(stage, point):
    owner = {"container_id": "a" * 64, "container_name": "frontend-1",
             "image": "sha256:image", "config_image": "image@sha256:image",
             "container_started_at": "2026-10-29T00:00:00Z", "container_running": True,
             "compose": {"project": "application", "service": "frontend",
                         "container_number": "1"},
             "ownership_proofs": ["exact_container_init_cgroup_set"]}
    return {"schema": "runtime-identity-guest-sample-v5", "node": "a", "stage": stage,
            "boot_id": "boot-a", "host_pid_namespace": "pid:[100]",
            "clock_ticks_per_second": 100,
            "clocks": {edge: {"realtime_unix_ns": point, "monotonic_ns": point,
                               "boottime_ns": point} for edge in ("started", "ended")},
            "containers": [], "docker_proof": {"list_returncode": 0, "inspect_returncode": 0},
            "processes": [{"host_pid": 123, "state": "S", "comm": "frontend",
                           "start_ticks": 900, "pid_namespace": "pid:[200]",
                           "cgroups": [{"path": "/docker/" + "a" * 64}],
                           "exe": "/app/frontend", "owner": owner}], "process_scan_errors": []}


def _capture(root, stage, point):
    folder = root / "runtime-identity-v5"
    sample_path = folder / f"sample-{stage}-a.json"
    _write(sample_path, _sample(stage, point))
    value = {"schema": "runtime-identity-capture-v5", "stage": stage,
             "helper": {"sha256": "b" * 64}, "samples": [_sample(stage, point)], "errors": [],
             "runner_interval": {"started_monotonic_ns": point,
                                 "ended_monotonic_ns": point},
             "files": {sample_path.name: {"bytes": sample_path.stat().st_size,
                                           "sha256": _sha(sample_path)}},
             "cost_file": None}
    _write(folder / f"capture-{stage}.json", value)


def test_hash_verified_enclosure_projects_copied_export_only(tmp_path):
    root = tmp_path / "campaign"; observations = root / "observations"
    raw = observations / "deepflow-raw" / "a" / "l7_flow_log"
    row = {"signal_source": "EBPF", "tap_side": "ServerProcess", "ebpf_type": "TracePoint",
           "l7_protocol": "Http1", "msg_type": "Request", "start_time": 10, "end_time": 20,
           "ip_src": "192.0.2.1", "ip_dst": "192.0.2.2", "port_src": 41000,
           "port_dst": 8080, "process_id_1": 123, "process_kname_1": "frontend",
           "request_type": "GET", "request_resource": "/items/7", "version": "1.1",
           "x_request_id_0": "request-1"}
    raw.parent.mkdir(parents=True); raw.write_text(json.dumps(row, separators=(",", ":")) + "\n")
    batches, accounting, _ = codec_file(
        raw, node="a", source_file="a/l7_flow_log",
        retained_file="deepflow-raw/a/l7_flow_log",
        guest_context={"boot_id": "boot-a", "pid_namespace": "pid:[100]"})
    payload = batches[0]["payload"]
    payload["resourceSpans"][0]["schemaUrl"] = "retained-unknown-envelope-field"
    receiver_wire = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
    receiver_raw = observations / "a.raw" / "capture" / "body.json"
    receiver_raw.parent.mkdir(parents=True)
    receiver_raw.write_bytes(receiver_wire)
    wrapper = observations / "a.jsonl"
    _write(wrapper, {
        "payload": payload,
        "raw_ref": receiver_raw.relative_to(observations).as_posix(),
        "raw_sha256": hashlib.sha256(receiver_wire).hexdigest(),
        "content_type": "application/json",
        "content_encoding": "",
        "id_encoding": "hex",
    })
    original_wrapper = wrapper.read_bytes(); original_raw = raw.read_bytes()
    (observations / "b.jsonl").write_text("")
    native = root / "native"; native.mkdir(parents=True)
    store = ObservationStoreV5(root / "observation-index.sqlite", same_trace_parents=True)
    store.ingest(observations, native)

    _capture(root, "before-target-00", 10)
    _capture(root, "after-target-00", 40)
    journal = Journal(root / "attempt-journal.sqlite")
    started = {"transport_id": "transport-1", "request_id": "request-1",
               "method": "GET", "url": "http://entry/items/7"}
    journal.db.execute("INSERT INTO events(kind,wall_ns,monotonic_ns,data) VALUES (?,?,?,?)",
                       ("step_started", 1, 20, json.dumps(started)))
    journal.db.execute("INSERT INTO events(kind,wall_ns,monotonic_ns,data) VALUES (?,?,?,?)",
                       ("step_finished", 2, 30, json.dumps({**started, "transport_state": "complete"})))
    journal.db.commit()
    campaign = SimpleNamespace(ctx=SimpleNamespace(out=root, journal=journal), store=store,
        plans=[{"block_id": "target-00", "http_steps": [{"request_id": "request-1",
                                                            "method": "GET", "path": "/items/7"}]}])
    result = refresh(campaign, "training")
    assert result["projection"]["counts"]["resolved_enriched"] == 1
    effective = store.candidates_v5("ebpf", "request-1")[0]
    assert effective["service"] == "frontend"

    manifest = export_selection(store, {"ebpf": None}, root / "exports",
                                service_projections=store.service_projections())
    assert manifest["runtime_identity_projected_observations"] == 1
    exported = json.loads(Path(manifest["exports"][0]["path"]).read_text())
    resource = exported["resourceSpans"][0]
    assert resource["schemaUrl"] == "retained-unknown-envelope-field"
    assert attributes(resource["resource"]["attributes"])["service.name"] == "frontend"
    assert wrapper.read_bytes() == original_wrapper
    assert raw.read_bytes() == original_raw
    assert manifest["exports"][0]["original_wire_unchanged"] is True
    assert manifest["exports"][0]["graph_edges_injected"] is False

    journal.db.execute("UPDATE events SET wall_ns=999 WHERE kind='step_finished'")
    journal.db.commit()
    with pytest.raises(ValueError, match="journal event changed"):
        store.service_projections()
    journal.db.execute("UPDATE events SET wall_ns=2 WHERE kind='step_finished'")
    journal.db.commit()
    assert len(store.service_projections()) == 1

    # Target-stage evidence cannot rewrite the already frozen training projection.
    empty_inventory = {"schema": "runtime-identity-inventory-v5", "samples": [],
                       "captures": [], "capture_lifetimes": [], "event_enclosures": []}
    immutable = store.apply_runtime_identity(
        empty_inventory, root / "runtime-identity-v5" / "projection-target.jsonl",
        inventory_proof={"path": "runtime-identity-v5/inventory-target.json",
                         "sha256": "0" * 64}, stage="target")
    assert immutable["counts"]["unknown"] == 1
    assert store.candidates_v5("ebpf", "request-1")[0]["service"] == "frontend"
    assert store.db.execute(
        "SELECT stage,status FROM runtime_identity_projection").fetchone() == (
            "training", "resolved_enriched")

    # A nonempty source label remains authoritative data and disagreement is explicit.
    store.db.execute("DELETE FROM runtime_identity_projection")
    digest, encoded = store.db.execute("SELECT digest,data FROM spans").fetchone()
    original = json.loads(encoded); original["service"] = "source-declared-other"
    store.db.execute("UPDATE spans SET service=?,data=? WHERE digest=?", (
        original["service"], json.dumps(original, sort_keys=True, separators=(",", ":")), digest))
    store.db.commit()
    inventory_path = root / result["inventory"]["path"]
    conflict = store.apply_runtime_identity(
        json.loads(inventory_path.read_text()),
        root / "runtime-identity-v5" / "projection-conflict.jsonl",
        inventory_proof=result["inventory"], stage="training")
    assert conflict["counts"]["label_conflict"] == 1
    assert store.candidates_v5("ebpf", "request-1")[0]["service"] == "source-declared-other"
    resolution = json.loads(store.db.execute(
        "SELECT resolution FROM runtime_identity_projection").fetchone()[0])
    assert resolution["status"] == "unknown"
    assert resolution["unknown_reasons"] == [
        "existing_source_label_conflicts_with_runtime_identity"]
    journal.close(); store.close()
