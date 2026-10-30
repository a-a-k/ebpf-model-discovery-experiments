from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ebpf_discovery.deepflow_codec_v5 import (DEEPFLOW_SOURCE_COMMIT,
                                               DEEPFLOW_VERSION, codec_file)
from ebpf_discovery.deepflow_v5 import DEEPFLOW_IMAGE
from ebpf_discovery.identity_projection_v5 import _verified_clock_relations, refresh
from ebpf_discovery.observations import attributes
from ebpf_discovery.raw_v4 import export_selection
from ebpf_discovery.selection_v4 import bind_entry as bind_entry_v4
from ebpf_discovery.selection_v5 import bind_entry as bind_entry_v5
from ebpf_discovery.store_v5 import ObservationStoreV5
from ebpf_discovery.store_v5 import ProjectionResolver
from ebpf_discovery.toolchain_v5 import Toolchain
from ebpf_discovery.remote_toolchain_v4 import _readonly_store
from ebpf_discovery.transport_v4 import Journal


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def test_clock_relation_verifies_exact_source_config_guest_proof(tmp_path):
    root = tmp_path / "campaign"
    config = root / "deepflow-agent-standalone-a.yaml"
    config.parent.mkdir(parents=True); config.write_text("global:\n  standalone_mode: {}\n")
    command = "docker run pinned /bin/deepflow-agent --standalone -f config"
    relation = root / "runtime-identity-v5" / "clock-relation-a.json"
    _write(relation, {
        "schema": "runtime-identity-clock-relation-v5", "node": "a",
        "boot_id": "boot-a", "pid_namespace": "pid:[1]",
        "domain": "guest_realtime_unix_ns",
        "relation": "documented_same_guest_realtime_relation",
        "producer": {"name": "deepflow-agent", "version": DEEPFLOW_VERSION,
                     "source_commit": DEEPFLOW_SOURCE_COMMIT, "image": DEEPFLOW_IMAGE,
                     "runtime_command": command,
                     "pinned_source_paths": ["agent/src/ebpf/user/socket.h"]},
        "runtime_configuration": {"path": config.relative_to(root).as_posix(),
                                  "sha256": _sha(config), "bytes": config.stat().st_size,
                                  "event_clock_adjustment_to_external_domain_enabled": False,
                                  "validated_effective_facts": {
                                      "standalone_mode_config_present": True,
                                      "standalone_cli_enabled": True,
                                      "controller_ntp_correction_enabled": False}},
        "event_serialization": {"unit": "microseconds", "quantization_ns": 1000,
                                "unix_nanosecond_conversion":
                                "exact_integer_multiply_by_1000"},
        "host_receipt_time_used": False,
        "empirical_endpoint_offsets_used_as_hard_bound": False,
        "arbitrary_tolerance_or_age_filter_used": False,
        "clock_step_limitation_retained": True})
    _write(root / "observations" / "collector.json", {
        "schema": "collector-lifecycle-v5", "collector": "deepflow",
        "source_version": DEEPFLOW_VERSION, "source_commit": DEEPFLOW_SOURCE_COMMIT,
        "image": DEEPFLOW_IMAGE, "commands": {"a": command},
        "configs": {"a": {"path": config.name, "sha256": _sha(config)}},
        "runtime_clock_relations": {"a": {"evidence": {
            "locator": relation.relative_to(root).as_posix()}}}})
    rows = _verified_clock_relations(root)
    assert rows[0]["verified_hash_bound_source_config_guest_relation"] is True
    assert rows[0]["evidence"]["sha256"] == _sha(relation)

    collector_path = root / "observations" / "collector.json"
    collector = json.loads(collector_path.read_text()); collector["commands"]["a"] += " changed"
    _write(collector_path, collector)
    with pytest.raises(ValueError, match="differs from collector manifest"):
        _verified_clock_relations(root)
    collector["commands"]["a"] = command; _write(collector_path, collector)
    config.write_text("global: {changed: true}\n")
    with pytest.raises(ValueError, match="configuration changed"):
        _verified_clock_relations(root)


def test_source_clock_projection_export_revalidates_relation_captures_and_raw(
        tmp_path, monkeypatch):
    root = tmp_path / "campaign"; observations = root / "observations"
    raw = observations / "deepflow-raw" / "a" / "l7_flow_log"
    raw.parent.mkdir(parents=True); raw.write_bytes(b'{"saved":"row"}\n')
    config = observations / "deepflow-agent-standalone-a.yaml"
    config.write_text("global:\n  standalone_mode: {}\n")
    command = "docker run pinned /bin/deepflow-agent --standalone -f config"
    relation_path = root / "runtime-identity-v5" / "clock-relation-a.json"
    _write(relation_path, {
        "schema": "runtime-identity-clock-relation-v5", "node": "a",
        "boot_id": "boot-a", "pid_namespace": "pid:[100]",
        "domain": "guest_realtime_unix_ns",
        "relation": "documented_same_guest_realtime_relation",
        "producer": {"name": "deepflow-agent", "version": DEEPFLOW_VERSION,
                     "source_commit": DEEPFLOW_SOURCE_COMMIT, "image": DEEPFLOW_IMAGE,
                     "runtime_command": command, "pinned_source_paths": ["socket.h"]},
        "runtime_configuration": {"path": config.relative_to(root).as_posix(),
                                  "sha256": _sha(config), "bytes": config.stat().st_size,
                                  "event_clock_adjustment_to_external_domain_enabled": False,
                                  "validated_effective_facts": {
                                      "standalone_mode_config_present": True,
                                      "standalone_cli_enabled": True,
                                      "controller_ntp_correction_enabled": False}},
        "event_serialization": {"unit": "microseconds", "quantization_ns": 1000,
                                "unix_nanosecond_conversion":
                                "exact_integer_multiply_by_1000"},
        "host_receipt_time_used": False,
        "empirical_endpoint_offsets_used_as_hard_bound": False,
        "arbitrary_tolerance_or_age_filter_used": False,
        "clock_step_limitation_retained": True})
    _write(observations / "collector.json", {
        "schema": "collector-lifecycle-v5", "collector": "deepflow",
        "source_version": DEEPFLOW_VERSION, "source_commit": DEEPFLOW_SOURCE_COMMIT,
        "image": DEEPFLOW_IMAGE, "commands": {"a": command},
        "configs": {"a": {"path": config.name, "sha256": _sha(config)}},
        "runtime_clock_relations": {"a": {"evidence": {
            "locator": relation_path.relative_to(root).as_posix()}}}})
    evidence = {"kind": "documented_clock_relation",
                "locator": relation_path.relative_to(root).as_posix(),
                "sha256": _sha(relation_path), "bytes": relation_path.stat().st_size}
    proofs = {}
    for stage, point in (("before-block-1", 10), ("after-block-1", 40)):
        _capture(root, stage, point)
        capture_path = root / "runtime-identity-v5" / f"capture-{stage}.json"
        capture = json.loads(capture_path.read_text())
        proofs[stage] = {"path": capture_path.relative_to(root).as_posix(),
                         "sha256": _sha(capture_path), "bytes": capture_path.stat().st_size,
                         "files": capture["files"], "runner_interval": capture["runner_interval"]}
    inventory_path = root / "runtime-identity-v5" / "inventory-training.json"
    _write(inventory_path, {"schema": "runtime-identity-inventory-v5", "samples": [],
                            "captures": [], "capture_lifetimes": [], "event_enclosures": [],
                            "clock_relations": _verified_clock_relations(root),
                            "capture_proofs": proofs})
    locator = {"source_file": "a/l7_flow_log",
               "retained_file": raw.relative_to(observations).as_posix(), "offset": 0,
               "length": raw.stat().st_size, "sha256": _sha(raw)}
    resolution = {"status": "resolved", "service_identity": {"compose_service": "database"},
                  "process_identity": {"node": "a"}, "record_locator": locator,
                  "duplicate_order_probe": {"value": 1},
                  "clock_evidence": evidence,
                  "bracket": {"kind": "source_event_clock",
                              "before_stage": "before-block-1", "after_stage": "after-block-1",
                              "clock_domain": "guest_realtime_unix_ns",
                              "clock_relation": "documented_same_guest_realtime_relation"},
                  "inventory_proof": {"path": inventory_path.relative_to(root).as_posix(),
                                      "sha256": _sha(inventory_path),
                                      "bytes": inventory_path.stat().st_size}}
    store = ObservationStoreV5(root / "observation-index.sqlite", same_trace_parents=True)
    store.db.execute("INSERT INTO runtime_identity_projection VALUES (?,?,?,?,?,?,?,?,?)", (
        "z-first-insertion", "training", "resolved_enriched", "unknown", "database", "{}",
        json.dumps(resolution), inventory_path.relative_to(root).as_posix(), _sha(inventory_path)))
    later_resolution = json.loads(json.dumps(resolution))
    later_resolution["duplicate_order_probe"]["value"] = True
    store.db.execute("INSERT INTO runtime_identity_projection VALUES (?,?,?,?,?,?,?,?,?)", (
        "a-second-insertion", "training", "resolved_enriched", "unknown", "database", "{}",
        json.dumps(later_resolution), inventory_path.relative_to(root).as_posix(), _sha(inventory_path)))
    store.db.commit()
    inventory_decodes = 0
    original_loads = json.loads
    inventory_bytes = inventory_path.read_bytes()
    def tracked_loads(value, *args, **kwargs):
        nonlocal inventory_decodes
        if value == inventory_bytes:
            inventory_decodes += 1
        return original_loads(value, *args, **kwargs)
    monkeypatch.setattr("ebpf_discovery.store_v5.json.loads", tracked_loads)
    diagnostic = root / "runtime-identity-v5" / "projection-training.jsonl"
    diagnostic.write_text('{"service":"deliberately-divergent-diagnostic"}\n')
    resolver = store.service_projections(root / "toolchain" / "runtime-identity-values.jsonl")
    assert next(iter(resolver.values()))["service"] == "database"
    assert next(iter(resolver.values()))["resolution"]["duplicate_order_probe"]["value"] is True
    assert diagnostic.read_text() == '{"service":"deliberately-divergent-diagnostic"}\n'
    resolver.close()
    assert inventory_decodes == 1
    assert not (root / "attempt-journal.sqlite").exists()
    config.write_text("changed: true\n")
    with pytest.raises(ValueError, match="configuration changed"):
        store.service_projections()
    store.close()


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
            "containers": [{"id": "a" * 64, "name": "frontend-1",
                            "state": {"StartedAt": "2026-10-29T00:00:00Z"},
                            "compose": owner["compose"]}],
            "docker_proof": {"list_returncode": 0, "inspect_returncode": 0},
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


def _append_receiver_span(observations, *, request_id, trace, span, capture, node="a"):
    capture_dir = observations / f"{node}.raw" / capture
    capture_dir.mkdir(parents=True)
    body = capture_dir / "body.pb"
    body.write_bytes(("wire-" + request_id).encode())
    raw_ref = body.relative_to(observations).as_posix()
    metadata_ref = (capture_dir / "metadata.json").relative_to(observations).as_posix()
    raw_sha = hashlib.sha256(body.read_bytes()).hexdigest()
    metadata = {"source": f"ebpf-coroot:{node}", "node": node,
                "received_ns": len(request_id),
                "raw_ref": raw_ref, "raw_sha256": raw_sha,
                "raw_size_bytes": body.stat().st_size}
    _write(capture_dir / "metadata.json", metadata)
    payload = {"resourceSpans": [{"resource": {"attributes": [
        {"key": "service.name", "value": {"stringValue": "/docker/frontend-1"}},
        {"key": "container.id", "value": {"stringValue": "/docker/frontend-1"}}]},
        "scopeSpans": [{"spans": [{"traceId": trace, "spanId": span,
            "name": "GET", "kind": "SPAN_KIND_SERVER", "startTimeUnixNano": "1",
            "endTimeUnixNano": "2", "attributes": [
                {"key": "http.request.header.x-experiment-request-id",
                 "value": {"arrayValue": {"values": [{"stringValue": request_id}]}}},
                {"key": "http.request.method", "value": {"stringValue": "GET"}},
                {"key": "url.path", "value": {"stringValue": "/entry"}}]}]}]}]}
    wrapper = {**metadata, "raw_metadata_ref": metadata_ref, "id_encoding": "hex",
               "payload": payload}
    with (observations / f"{node}.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(wrapper, separators=(",", ":")) + "\n")


def test_parent_training_freezes_alias_and_final_append_uses_same_effective_rows(tmp_path, monkeypatch):
    root = tmp_path / "campaign"; observations = root / "observations"
    observations.mkdir(parents=True); (root / "native").mkdir()
    (observations / "b.jsonl").write_text("")
    _append_receiver_span(observations, request_id="training-request",
                          trace="1" * 32, span="2" * 16, capture="training")
    store = ObservationStoreV5(root / "observation-index.sqlite", same_trace_parents=True)
    store.ingest(observations, root / "native")
    _capture(root, "training-sample", 10)
    journal = Journal(root / "attempt-journal.sqlite")
    campaign = SimpleNamespace(ctx=SimpleNamespace(out=root, journal=journal), store=store,
                               collector="coroot", plans=[])
    # No synchronous nonce candidate exists here: response bodies need not be read.
    def unexpected_journal_read(_journal):
        raise AssertionError("journal read without an enclosure candidate")
    with monkeypatch.context() as guard:
        guard.setattr("ebpf_discovery.identity_projection_v5._journal_transports",
                      unexpected_journal_read)
        training = refresh(campaign, "training")
    assert training["supplied_logical_alias_admission"][
        "effective_store_projection"]["rows"] == 1
    assert store.candidates_v5("ebpf", "training-request")[0]["service"] == "frontend"
    admission_path = root / training["supplied_logical_alias_admission"]["path"]
    retained_admission = json.loads(admission_path.read_text())
    assert {row["path"] for row in retained_admission["occurrence_proofs"]} == {
        "observations/a.jsonl"}
    frozen_admission = admission_path.read_bytes()

    _write(root / "status.json", {"protocol_version": "graph-v5", "collector": "coroot"})
    _write(observations / "collector.json", {"schema": "collector-lifecycle-v5",
                                              "collector": "coroot",
                                              "source_domain": "ebpf-coroot"})
    _write(root / "deployment.json", {})
    store.close()
    readonly = _readonly_store(root / "observation-index.sqlite", ObservationStoreV5)
    try:
        worker_view = Toolchain(SimpleNamespace(out=root), "demo", readonly,
                                SimpleNamespace())
        assert worker_view.supplied_alias_projection_verification[
            "logical_projection_verified"] is True
    finally:
        readonly.close()
    store = ObservationStoreV5(root / "observation-index.sqlite", same_trace_parents=True)
    campaign.store = store

    _append_receiver_span(observations, request_id="target-request",
                          trace="3" * 32, span="4" * 16, capture="target")
    _append_receiver_span(observations, request_id="other-guest-request",
                          trace="5" * 32, span="6" * 16, capture="other-guest", node="b")
    store.ingest(observations, root / "native")
    columns = [row[1] for row in store.db.execute("PRAGMA table_info(spans)")]
    base = dict(zip(columns, store.db.execute("SELECT * FROM spans LIMIT 1").fetchone()))
    for digest, source, node in (("missing-node-digest", "ebpf", None),
                                 ("native-carrier-digest", "native", "a")):
        data = json.loads(base["data"])
        data.update(source=source, node=node, request=digest)
        values = {**base, "digest": digest, "source": source, "node": node,
                  "request": digest,
                  "data": json.dumps(data, sort_keys=True, separators=(",", ":"))}
        store.db.execute(
            f"INSERT INTO spans({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[column] for column in columns))
    store.db.commit()
    final = refresh(campaign, "final")
    assert final["supplied_logical_alias_admission"][
        "effective_store_projection"]["rows"] == 2
    assert admission_path.read_bytes() == frozen_admission
    assert store.candidates_v5("ebpf", "target-request")[0]["service"] == "frontend"
    assert store.candidates_v5("ebpf", "other-guest-request")[0]["service"] == (
        "/docker/frontend-1")
    assert store.observation_v5("missing-node-digest")["service"] == "/docker/frontend-1"
    assert store.observation_v5("native-carrier-digest")["service"] == "/docker/frontend-1"
    expected = {"method": "GET", "path": "/entry"}
    assert bind_entry_v5(store, "ebpf", "target-request", expected, ["frontend"])[0][
        "service"] == "frontend"
    assert bind_entry_v4(store, "ebpf", "target-request", expected, ["frontend"])[0][
        "service"] == "frontend"
    assert {json.loads(row[0])["service"] for row in store.db.execute(
        "SELECT data FROM spans")} == {"/docker/frontend-1"}
    scope_proof = json.loads((root / final["supplied_logical_alias_admission"]
                              ["effective_store_projection"]["scope_revalidation"]
                              ["path"]).read_text())
    assert set(scope_proof["scoped_digest_aliases"]) == {
        row[0] for row in store.db.execute(
            "SELECT digest FROM spans WHERE request IN ('training-request','target-request')")}
    assert scope_proof["new_mappings_admitted"] is False
    assert store.db.execute(
        "SELECT COUNT(*) FROM supplied_logical_alias_projection").fetchone()[0] == 2
    journal.close(); store.close()


def test_hash_verified_enclosure_projects_copied_export_only(tmp_path, monkeypatch):
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
    payload["resourceSpans"][0]["scopeSpans"][0][
        "_projection_scope_ordinal"] = "original-unknown-field"
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
        collector="deepflow",
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
    assert resource["scopeSpans"][0]["_projection_scope_ordinal"] == "original-unknown-field"
    assert attributes(resource["resource"]["attributes"])["service.name"] == "frontend"
    assert wrapper.read_bytes() == original_wrapper
    assert raw.read_bytes() == original_raw
    assert manifest["exports"][0]["original_wire_unchanged"] is True
    assert manifest["exports"][0]["graph_edges_injected"] is False

    # Multiple resolved rows sharing immutable dependencies hash each full file once per call.
    store.db.execute('''INSERT INTO runtime_identity_projection
        SELECT ?,stage,status,original_service,projected_service,projected_data,resolution,
               inventory_path,inventory_sha256 FROM runtime_identity_projection LIMIT 1''',
        ("second-digest",))
    store.db.commit()
    reads = {}
    original_read_bytes = Path.read_bytes
    def tracked_read_bytes(path):
        key = str(path.resolve()); reads[key] = reads.get(key, 0) + 1
        return original_read_bytes(path)
    monkeypatch.setattr(Path, "read_bytes", tracked_read_bytes)
    assert len(store.service_projections()) == 1
    inventory_dependency = str((root / result["inventory"]["path"]).resolve())
    assert reads[inventory_dependency] == 1
    store.db.execute("DELETE FROM runtime_identity_projection WHERE digest='second-digest'")
    store.db.commit()

    encoded_resolution = store.db.execute(
        "SELECT resolution FROM runtime_identity_projection").fetchone()[0]
    enclosure_dependency = (root / json.loads(encoded_resolution)["clock_evidence"]["locator"]).resolve()
    def changed_after_proof(path):
        retained = original_read_bytes(path)
        return retained + (b" " if path.resolve() == enclosure_dependency else b"")
    monkeypatch.setattr(Path, "read_bytes", changed_after_proof)
    with pytest.raises(ValueError, match="enclosure evidence changed"):
        store.service_projections()
    monkeypatch.setattr(Path, "read_bytes", tracked_read_bytes)

    journal.db.execute("UPDATE events SET wall_ns=999 WHERE kind='step_finished'")
    journal.db.commit()
    with pytest.raises(ValueError, match="journal event changed"):
        store.service_projections()
    journal.db.execute("UPDATE events SET wall_ns=2 WHERE kind='step_finished'")
    journal.db.commit()
    assert len(store.service_projections()) == 1

    terminal = journal.db.execute(
        "SELECT seq,kind,wall_ns,monotonic_ns,data FROM events WHERE kind='step_finished'").fetchone()
    journal.db.execute("DELETE FROM events WHERE seq=?", (terminal[0],)); journal.db.commit()
    with pytest.raises(ValueError, match="journal event changed"):
        store.service_projections()
    journal.db.execute("INSERT INTO events(seq,kind,wall_ns,monotonic_ns,data) VALUES (?,?,?,?,?)",
                       terminal); journal.db.commit()

    encoded_resolution = store.db.execute(
        "SELECT resolution FROM runtime_identity_projection").fetchone()[0]
    retained_resolution = json.loads(encoded_resolution)
    enclosure_path = root / retained_resolution["clock_evidence"]["locator"]
    enclosure_body = original_read_bytes(enclosure_path)
    enclosure = json.loads(enclosure_body)
    del enclosure["transport"]["terminal"]["event_row_sha256"]
    enclosure_path.write_text(json.dumps(enclosure), encoding="utf-8")
    retained_resolution["clock_evidence"]["sha256"] = _sha(enclosure_path)
    retained_resolution["clock_evidence"]["bytes"] = enclosure_path.stat().st_size
    store.db.execute("UPDATE runtime_identity_projection SET resolution=?",
                     (json.dumps(retained_resolution),)); store.db.commit()
    with pytest.raises(ValueError, match="journal event changed"):
        store.service_projections()
    enclosure_path.write_bytes(enclosure_body)
    store.db.execute("UPDATE runtime_identity_projection SET resolution=?", (encoded_resolution,))
    store.db.commit()
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
    effective_conflict = store.candidates_v5("ebpf", "request-1")[0]
    assert effective_conflict["service"] == "source-declared-other"
    assert effective_conflict["attribute_conflicts"][-1]["key"] == "service.name"
    assert effective_conflict["_runtime_identity_uncertainty"][
        "admissible_service_identity"] is None
    # Give the synthetic DeepFlow row genuine IDs so legacy rejection is tested
    # specifically on the identity contradiction, not its usual missing ancestry.
    effective_conflict["trace_id"], effective_conflict["span_id"] = "1" * 32, "2" * 16
    store.db.execute("UPDATE runtime_identity_projection SET projected_data=?", (
        json.dumps(effective_conflict, sort_keys=True, separators=(",", ":")),))
    store.db.commit()
    expected = {"method": "GET", "path": "/items/7"}
    root_v5, reason_v5 = bind_entry_v5(
        store, "ebpf", "request-1", expected, ["source-declared-other"])
    root_v4, reason_v4 = bind_entry_v4(
        store, "ebpf", "request-1", expected, ["source-declared-other"])
    assert root_v5 is None and reason_v5 == "conflicting_matching_entry_evidence"
    assert root_v4 is None and reason_v4 == "conflicting_entry_attributes"
    journal.close(); store.close()
def test_projection_resolver_preserves_identical_duplicate_and_conflict_semantics(tmp_path):
    resolver = ProjectionResolver(tmp_path, tmp_path / "values.jsonl")
    key = ("a/raw", "deepflow-raw/a/raw", 1, 2, "a" * 64)
    value = {"service": "database", "resolution": {"status": "resolved"}}
    resolver.add(key, value)
    resolver.add(key, json.loads(json.dumps(value)))
    assert len(resolver) == 1 and resolver.get(key) == value
    with pytest.raises(ValueError, match="conflicting runtime identity projection"):
        resolver.add(key, {**value, "service": "frontend"})
    resolver.finalize()
    retained = [json.loads(line) for line in (tmp_path / "values.jsonl").read_text().splitlines()]
    assert retained == [{"sha256": resolver.value_reference(value)["sha256"], "value": value}]
    resolver.close()
    # Python dict assignment replaces a later value even when JSON-distinct
    # scalar types compare equal; preserve that historical edge case exactly.
    resolver = ProjectionResolver(tmp_path, tmp_path / "equal-values.jsonl")
    resolver.add(key, {"service": "database", "resolution": {"flag": 1}})
    resolver.add(key, {"service": "database", "resolution": {"flag": True}})
    assert resolver.get(key)["resolution"]["flag"] is True
    resolver.finalize()
    assert len((tmp_path / "equal-values.jsonl").read_text().splitlines()) == 1
    resolver.close()
