from copy import deepcopy
import hashlib
import json
import pytest
import sqlite3
from types import SimpleNamespace

from ebpf_discovery.supplied_alias_v5 import admit_observed, build, semantic_view
from ebpf_discovery.store_v3 import normalized_file
from ebpf_discovery.store_v5 import _digest
from ebpf_discovery.toolchain_v5 import Toolchain


def inventory(*containers):
    return {"samples": [{"node": node, "containers": rows} for node, rows in containers]}


def container(name, service, *, project="p", identity="a", started="one"):
    return {"id": identity * 64, "name": name, "state": {"StartedAt": started},
            "compose": {"project": project, "service": service}}


def proof():
    return {"path": "runtime-identity-v5/inventory-training.json",
            "sha256": "a" * 64, "bytes": 10}


def test_same_scoped_name_across_restarts_keeps_one_supplied_logical_role():
    value = build(inventory(
        ("a", [container("app-1", "app", identity="a", started="one")]),
        ("a", [container("app-1", "app", identity="b", started="two")]),
    ), inventory_proof=proof())
    assert value["conflicts"] == []
    assert value["global_aliases"]["/docker/app-1"] == "app"
    assert value["rows"][0]["inventory_occurrences"] == 2
    assert value["same_table_all_sources_and_direct_baseline"] is True
    assert value["direct_baseline"]["mapping_source"] == "rows"
    assert value["direct_baseline"]["same_information"] is True
    assert value["manual_preparation_seconds"] is None


def test_multiple_roles_for_one_scoped_name_and_cross_guest_collision_are_unknown():
    scoped = build(inventory(
        ("a", [container("shared", "one")]),
        ("a", [container("shared", "two")]),
    ), inventory_proof=proof())
    assert scoped["rows"] == []
    assert scoped["conflicts"][0]["reason"] == "scoped_name_maps_to_multiple_logical_roles"

    guests = build(inventory(
        ("a", [container("shared", "one")]),
        ("b", [container("shared", "two")]),
    ), inventory_proof=proof())
    assert "shared" not in guests["global_aliases"]
    assert guests["global_conflicts"][0]["reason"] == (
        "cross_guest_carrier_maps_to_multiple_logical_roles")


def test_semantic_view_preserves_raw_model_and_does_not_invent_causality_or_instances():
    table = build(inventory(("a", [container("app-1", "app")])),
                  inventory_proof=proof())
    model = {"services": [{"id": "/docker/app-1", "replicas": 1}],
             "edges": [{"id": "edge", "from": "/docker/app-1", "to": "peer:x",
                        "kind": "sync", "identity": {"span_kind": "client"}}],
             "endpoints": []}
    quality = {"observation_evidence": []}
    original = deepcopy(model)
    transformed, transformed_quality, applied = semantic_view(model, quality, table)
    assert model == original
    assert transformed["services"] == [{"id": "app", "replicas": 1}]
    assert transformed["edges"] == [{"id": "edge", "from": "app", "to": "peer:x",
                                     "kind": "sync", "identity": {"span_kind": "client"}}]
    assert transformed["endpoints"] == []
    assert transformed_quality == quality
    assert applied["graph_edges_injected"] is False
    assert applied["roles_or_endpoints_created"] is False
    assert applied["physical_identity_inferred"] is False
    assert all(key not in transformed["services"][0]
               for key in ("pid", "process_identity", "service.instance.id"))


def test_combined_source_metadata_collision_stays_unresolved_and_suppresses_binding():
    table = build(inventory(("a", [container("app-1", "app")])),
                  inventory_proof=proof())
    model = {"services": [{"id": "/docker/app-1", "name": "/docker/app-1",
                            "replicas": 1, "attributes": {"source": "ebpf"}},
                           {"id": "app", "name": "app", "replicas": 2,
                            "attributes": {"source": "native"}}],
             "edges": [{"id": "e", "from": "/docker/app-1", "to": "peer:x",
                        "kind": "sync"}], "endpoints": []}
    transformed, transformed_quality, application = semantic_view(
        model, {}, table, {"/docker/app-1": "app"})
    assert transformed == model
    assert application["applied"] == []
    assert application["metadata_collisions"] == [{
        "logical_service": "app", "raw_variants": model["services"],
        "reason": "non_name_service_metadata_differs"}]
    assert application["effective_aliases"] == {}
    assert transformed_quality["supplied_logical_alias_uncertainty"] == (
        application["metadata_collisions"])
    uncertainty = Toolchain.__new__(Toolchain).binding_uncertainties(
        transformed, transformed_quality)
    assert uncertainty == [{
        "reason": "supplied_logical_alias_metadata_collision",
        "logical_services": ["app"], "variants_retained": True,
        "binding_suppressed": True}]
    binding = {"available": True, "unknown": []}
    Toolchain.__new__(Toolchain).apply_binding_uncertainties(
        binding, transformed, transformed_quality)
    assert binding["available"] is False
    assert binding["unknown"] == uncertainty


def test_receiver_guest_provenance_admits_exact_carrier_and_rejects_scope_mismatch(tmp_path):
    raw = tmp_path / "a.jsonl"
    raw_body = tmp_path / "a.raw" / "capture" / "body.pb"
    metadata_path = raw_body.parent / "metadata.json"
    raw_body.parent.mkdir(parents=True)
    raw_body.write_bytes(b"original wire body")
    raw_sha = hashlib.sha256(raw_body.read_bytes()).hexdigest()
    wrapper = {"source": "ebpf-coroot:a", "node": "a", "id_encoding": "hex",
        "received_ns": 123, "raw_ref": "a.raw/capture/body.pb",
        "raw_metadata_ref": "a.raw/capture/metadata.json",
        "raw_sha256": raw_sha, "raw_size_bytes": raw_body.stat().st_size,
        "payload": {"resourceSpans": [{"resource": {"attributes": [
            {"key": "service.name", "value": {"stringValue": "/docker/app-1"}},
            {"key": "container.id", "value": {"stringValue": "/docker/app-1"}}]},
            "scopeSpans": [{"spans": [{"traceId": "1" * 32, "spanId": "2" * 16,
                "name": "GET", "kind": "SPAN_KIND_CLIENT",
                "startTimeUnixNano": "1", "endTimeUnixNano": "2",
                "attributes": [], "status": {}},
                {"traceId": "3" * 32, "spanId": "4" * 16,
                 "name": "POST", "kind": "SPAN_KIND_CLIENT",
                 "startTimeUnixNano": "3", "endTimeUnixNano": "4",
                 "attributes": [], "status": {}}]}]}]}}
    metadata_path.write_text(json.dumps({key: wrapper[key] for key in (
        "source", "node", "received_ns", "raw_ref", "raw_metadata_ref",
        "raw_sha256", "raw_size_bytes")}), encoding="utf-8")
    raw.write_text(json.dumps(wrapper) + "\n", encoding="utf-8")
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE spans(digest TEXT, data TEXT)")
    db.execute("CREATE TABLE observation_provenance("
               "digest TEXT,raw_file TEXT,from_byte INTEGER,through_byte INTEGER,"
               "normalized_ordinal INTEGER,segment_sha256 TEXT)")
    normalized = list(normalized_file(raw, "ebpf", 0, raw.stat().st_size))
    for ordinal, row in enumerate(normalized):
        span_digest = _digest(row)
        db.execute("INSERT INTO spans VALUES (?,?)", (span_digest, json.dumps(row)))
        db.execute("INSERT INTO observation_provenance VALUES (?,?,?,?,?,?)",
                   (span_digest, str(raw), 0, raw.stat().st_size, ordinal, digest))
    table = build(inventory(("a", [container("app-1", "app")])),
                  inventory_proof=proof())
    admitted = admit_observed(SimpleNamespace(db=db), table,
                              expected_source_prefix="ebpf-coroot")
    assert admitted["aliases"] == {"/docker/app-1": "app"}
    assert admitted["receiver_segments_reverified"] is True
    assert admitted["unique_verified_segments"] == 1
    assert len(admitted["occurrence_proofs"]) == 2

    db.execute("INSERT INTO spans VALUES (?,?)", (
        "native-logical-service-row",
        json.dumps({**normalized[0], "source": "native", "service": "app"})))
    separate_source = admit_observed(SimpleNamespace(db=db), table,
                                     expected_source_prefix="ebpf-coroot")
    assert separate_source["aliases"] == {"/docker/app-1": "app"}
    db.execute("DELETE FROM spans WHERE digest='native-logical-service-row'")

    db.execute("INSERT INTO spans VALUES (?,?)", (
        "logical-service-row", json.dumps({**normalized[0], "service": "app"})))
    collision = admit_observed(SimpleNamespace(db=db), table,
                               expected_source_prefix="ebpf-coroot")
    assert collision["aliases"] == {}
    assert any(item["reason"] == "logical_target_already_observed_as_service"
               for item in collision["conflicts"])
    db.execute("DELETE FROM spans WHERE digest='logical-service-row'")

    db.execute("UPDATE spans SET data=?", (json.dumps({**normalized[0], "node": "b"}),))
    rejected = admit_observed(SimpleNamespace(db=db), table,
                              expected_source_prefix="ebpf-coroot")
    assert rejected["aliases"] == {}
    assert rejected["conflicts"][0]["reason"] == (
        "receiver_scope_missing_ambiguous_or_conflicting")

    malformed = b"not-json\n"
    raw.write_bytes(malformed)
    db.execute("UPDATE observation_provenance SET through_byte=?,segment_sha256=?",
               (len(malformed), hashlib.sha256(malformed).hexdigest()))
    with pytest.raises(ValueError, match="segment is malformed"):
        admit_observed(SimpleNamespace(db=db), table,
                       expected_source_prefix="ebpf-coroot")
