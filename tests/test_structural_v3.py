import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from ebpf_discovery.structural_v3 import (
    _prepare_valid_ids, _projection_diagnostics, _raw_source, _report, summarize_cell)


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def span(source, trace, identity, parent, service, instance, node, raw_file, *, conflicted=0):
    value = {
        "source": source, "trace_id": trace, "span_id": identity, "parent_id": parent,
        "service": service, "instance": instance, "node": node, "kind": "SPAN_KIND_SERVER",
        "raw_file": raw_file,
    }
    return value, conflicted


def fixture(root: Path):
    summary, full = root / "summary", root / "full"
    hashes = {}
    for source in ("ebpf", "native", "combined"):
        graph = {
            "nodes": [
                {"id": f"{source}:a", "kind": "service", "source": source,
                 "service": "gateway", "instance": "one", "guest": "a"},
                {"id": f"{source}:b", "kind": "service", "source": source,
                 "service": "worker", "instance": None, "guest": "b"},
                {"id": f"{source}:db", "kind": "database", "source": source,
                 "system": "mysql", "address": "db", "port": "3306", "namespace": "app"},
            ],
            "edges": [{"from": f"{source}:a", "to": f"{source}:b",
                       "evidence": "source_local_observed_parent"}],
        }
        path = summary / "models" / source / "model.json"
        write(path, {"graph": graph})
        write(full / "models" / source / "model.json", {"graph": graph})
        hashes[path.relative_to(summary).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    write(summary / "forecast-saved.json", {"sha256_by_path": hashes})
    write(summary / "freeze-integrity.json", {"all_unchanged": True, "sha256_by_path": hashes})
    write(full / "forecast-saved.json", {"sha256_by_path": hashes})
    write(full / "freeze-integrity.json", {"all_unchanged": True, "sha256_by_path": hashes})
    status = {"system": "petclinic", "mode": "full", "seed": 3, "run_id": "100",
              "status": "acquisition_complete"}
    write(summary / "status.json", status)
    write(full / "status.json", status)
    projection_hashes = {}
    for source in ("ebpf", "native", "combined", "entry_http"):
        rows = []
        for index, proxy in enumerate((True, None)):
            row = {
                "source": source, "attempt_key": f"opaque-{index}",
                "operation_id": "owner_details_with_visits", "phase": "target",
                "proxy": proxy, "observation_censored": index == 1,
                "payload_verdict": {"reason": "fixture_match" if index == 0 else "payload_missing"},
            }
            if source != "entry_http":
                row["body_evidence"] = {"reason": "captured_body"}
                row["steps"] = [{
                    "binding": "unique_declared_entry", "window_binding": "strict_sealed_window",
                    "header_binding": {"rule": "explicit_server"},
                }]
            rows.append(row)
        path = full / "projections" / f"{source}-final.json"
        write(path, rows)
        projection_hashes[source] = hashlib.sha256(path.read_bytes()).hexdigest()
    metrics = {"source_inputs": {
        source: {"projection_sha256": digest} for source, digest in projection_hashes.items()
    }}
    write(summary / "metrics-v3.json", metrics)
    write(full / "metrics-v3.json", metrics)
    write(full / "deployment.json", {
        "replicas": [{"name": "worker", "node": "b"}],
        "database": {"logical_identity": "db", "node": "a"},
    })
    for guest, boot in (("a", "11111111-1111-1111-1111-111111111111"),
                        ("b", "22222222-2222-2222-2222-222222222222")):
        path = full / "infrastructure" / guest / "check.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"6.8.0\n{boot}\n", encoding="utf-8")
    database = sqlite3.connect(full / "observation-index.sqlite")
    database.executescript("""
      CREATE TABLE spans (
        digest TEXT PRIMARY KEY, source TEXT, node TEXT, trace TEXT, span TEXT,
        parent TEXT, service TEXT, instance TEXT, request TEXT, kind TEXT,
        start INTEGER, end INTEGER, dbsystem TEXT, address TEXT, port TEXT,
        namespace TEXT, conflicted INTEGER NOT NULL, data TEXT NOT NULL);
      CREATE INDEX identity_idx ON spans(source,trace,span);
      CREATE INDEX parent_idx ON spans(source,trace,parent);
    """)
    records = [
        span("ebpf", "1" * 32, "a" * 16, "", "gateway", "one", "a", "a.jsonl"),
        span("ebpf", "1" * 32, "b" * 16, "a" * 16, "worker", "two", "b", "b.jsonl"),
        span("ebpf", "2" * 32, "c" * 16, "d" * 16, "worker", "two", "b", "b.jsonl"),
        span("ebpf", "3" * 32, "e" * 16, "", "worker", "two", "a", "a.jsonl"),
        span("ebpf", "3" * 32, "e" * 16, "", "worker", "other", "b", "b.jsonl"),
        span("native", "4" * 16, "1" * 16, "", "gateway", "one", None, "native-a.jsonl"),
        span("native", "4" * 16, "2" * 16, "1" * 16, "worker", "two", "b", "native-b.jsonl"),
        span("ebpf", "", "3" * 16, "", "gateway", "one", "a", "a.jsonl"),
        span("ebpf", "", "4" * 16, "3" * 16, "worker", "two", "b", "b.jsonl"),
        span("ebpf", "z" * 32, "5" * 16, "", "worker", "two", "b", "b.jsonl"),
        span("ebpf", "5" * 32, "0" * 16, "", "worker", "two", "b", "b.jsonl"),
        span("ebpf", "6" * 32, "6" * 16, "g" * 16, "worker", "two", "b", "b.jsonl"),
        span("ebpf", "7" * 32, "7" * 16, "0" * 16, "worker", "two", "b", "b.jsonl"),
        span("ebpf", "3" * 32, "f" * 16, "e" * 16, "worker", "two", "b", "b.jsonl"),
        span("ebpf", "8" * 32, "8" * 16, "", "worker", "two", "b", "b.jsonl", conflicted=1),
        # The same trace/span in a different source is a distinct observation.
        span("native", "1" * 32, "a" * 16, "", "gateway", "one", "a", "native-a.jsonl"),
        span("native", "1" * 32, "c" * 16, "b" * 16, "worker", "two", "b", "native-b.jsonl"),
        span(None, "9" * 32, "9" * 16, "", "unknown", None, None, "unknown.jsonl"),
    ]
    for index, (record, conflicted) in enumerate(records):
        database.execute(
            "INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (f"d{index}", record["source"], record["node"], record["trace_id"], record["span_id"],
             record["parent_id"], record["service"], record["instance"], None, record["kind"],
             0, 1, None, None, None, None, conflicted, json.dumps(record, separators=(",", ":"))),
        )
    database.commit()
    database.close()
    index_hash = hashlib.sha256((full / "observation-index.sqlite").read_bytes()).hexdigest()
    marker = {"index_sha256": index_hash}
    write(summary / "acquisition-complete.json", marker)
    write(full / "acquisition-complete.json", marker)
    status_hash = hashlib.sha256((summary / "status.json").read_bytes()).hexdigest()
    return summary, full, status_hash


def test_structural_summary_separates_frozen_graph_and_full_capture(tmp_path):
    summary, full, status_hash = fixture(tmp_path)
    result = summarize_cell(
        {"system": "petclinic", "mode": "full", "seed": 3, "run_id": "100",
         "status_sha256": status_hash},
        summary, full, {"summary": {"stored_archive_bytes": 10}},
    )
    graph = result["frozen_graphs"]["ebpf"]
    raw = result["full_capture_parent_links"]["ebpf"]
    assert graph["distinct_cross_guest_ancestry_edge_pairs"] == 1
    assert graph["database_logical_nodes"][0]["concrete_physical_instance_confirmed"] is None
    assert raw["qualified_parent_links"] == 1
    assert raw["distinct_cross_guest_ancestry_edge_pairs"] == 1
    assert raw["missing_parent_links"] == 1
    assert raw["ambiguous_identity_groups"] == 1
    assert raw["ambiguous_parent_links"] == 1
    assert result["full_capture_parent_links"]["native"]["missing_parent_links"] == 1
    assert raw["invalid_identity_observations"] == 4
    assert any(row["span"]["trace_id"] == "" for row in raw["witnesses"]["invalid_identity"])
    assert raw["invalid_parent_references"] == 2
    assert {row["child"]["parent_id"] for row in raw["witnesses"]["invalid_parent_reference"]} == {
        "g" * 16, "0" * 16,
    }
    assert raw["witnesses"]["cross_guest"][0]["child"]["raw_file"] == "b.jsonl"
    assert result["full_capture_parent_links"]["native"]["unresolved_guest_placement_links"] == 1
    assert result["reference_placement"]["distinct_guest_boot_ids_confirmed"] is True
    assert result["correctness_error_rate"] is None
    assert result["frozen_graphs"]["combined"]["qualified_union_not_additional_physical_instances"] is True
    assert graph["known_instance_label_nodes"] == 1
    assert graph["unknown_instance_label_nodes"] == 1
    diagnostics = result["projection_recorded_diagnostics"]
    ebpf = diagnostics["sources"]["ebpf"]["groups"][0]
    assert ebpf["attempt_denominator"] == 2
    assert ebpf["proxy_attempts"] == {"true": 1, "false": 0, "unknown": 1}
    assert ebpf["step_occurrence_denominator"] == 2
    assert ebpf["step_binding_reason_occurrences"] == {"unique_declared_entry": 2}
    assert sum(ebpf["body_evidence_reason_attempts"].values()) == ebpf["attempt_denominator"]
    entry = diagnostics["sources"]["entry_http"]["groups"][0]
    assert entry["body_evidence_reason_attempts"] == {"not recorded": 2}
    assert entry["steps_field_attempts"] == {"recorded": 0, "not recorded": 2}
    assert entry["step_occurrence_denominator"] == 0
    assert result["input_sha256"]["full/projections/entry_http-final.json"]


def test_materialized_valid_identity_matches_pre_repair_full_outputs_and_uses_keyed_lookups(tmp_path):
    _, full, _ = fixture(tmp_path)
    index = full / "observation-index.sqlite"
    original_hash = hashlib.sha256(index.read_bytes()).hexdigest()
    database = sqlite3.connect(index.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        _prepare_valid_ids(database)
        assert database.execute("PRAGMA temp_store").fetchone()[0] == 1  # FILE
        assert database.execute("PRAGMA temp.cache_size").fetchone()[0] == -65536
        assert database.execute("SELECT COUNT(*) FROM temp.valid_ids WHERE source IS NULL").fetchone()[0] == 1
        # Complete serialized source outputs, including every bounded witness,
        # captured from d0d81f8's CTE implementation on this synthetic fixture.
        expected = {
            "ebpf": "bc51a1a03c2f2d166834a24b0500f3006eb79ee3c8c6fdefc4866127d53237c9",
            "native": "0d1936db7da02b438fa727392969df9a43befc54a141314dd826048d36a06473",
            "combined": "e049491f0c763b06a1a831f6572ca937f4851e87ac9ea5f82f8402de64b40a78",
        }
        for source, baseline_hash in expected.items():
            result = _raw_source(database, source)
            actual = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            assert actual == baseline_hash
        sql = """SELECT COUNT(*) FROM spans c
            JOIN temp.valid_ids cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
            JOIN spans p ON p.source=c.source AND p.trace=c.trace AND p.span=c.parent
            JOIN temp.valid_ids pv ON pv.source=p.source AND pv.trace=p.trace AND pv.span=p.span
            WHERE c.parent!='' AND c.source=?"""
        plan = [row[3] for row in database.execute("EXPLAIN QUERY PLAN " + sql, ("ebpf",))]
        for alias in ("cv", "pv"):
            assert any(f"SEARCH {alias} USING COVERING INDEX sqlite_autoindex_valid_ids_1 "
                       "(source=? AND trace=? AND span=?)" in item
                       for item in plan), plan
    finally:
        database.close()
    assert hashlib.sha256(index.read_bytes()).hexdigest() == original_hash


def test_structural_summary_rejects_changed_frozen_model(tmp_path):
    summary, full, status_hash = fixture(tmp_path)
    path = summary / "models" / "ebpf" / "model.json"
    path.write_text(path.read_text() + " ", encoding="utf-8")
    try:
        summarize_cell({"system": "petclinic", "mode": "full", "seed": 3, "run_id": "100",
                        "status_sha256": status_hash}, summary, full)
    except ValueError as exc:
        assert "saved model hash mismatch" in str(exc)
    else:
        raise AssertionError("changed frozen model was accepted")


def test_structural_summary_verifies_admission_and_final_index_hashes(tmp_path):
    summary, full, status_hash = fixture(tmp_path / "status")
    reference = {"system": "petclinic", "mode": "full", "seed": 3, "run_id": "100",
                 "status_sha256": "0" * 64}
    with pytest.raises(ValueError, match="admitted status hash"):
        summarize_cell(reference, summary, full)

    summary, full, status_hash = fixture(tmp_path / "index")
    write(summary / "acquisition-complete.json", {"index_sha256": "0" * 64})
    write(full / "acquisition-complete.json", {"index_sha256": "0" * 64})
    reference["status_sha256"] = status_hash
    with pytest.raises(ValueError, match="final observation index hash"):
        summarize_cell(reference, summary, full)


def test_structural_summary_rejects_metrics_or_projection_integrity_mismatch(tmp_path):
    summary, full, status_hash = fixture(tmp_path / "metrics")
    reference = {"system": "petclinic", "mode": "full", "seed": 3, "run_id": "100",
                 "status_sha256": status_hash}
    (full / "metrics-v3.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="metrics-v3.json bytes differ"):
        summarize_cell(reference, summary, full)

    summary, full, status_hash = fixture(tmp_path / "projection")
    with (full / "projections" / "native-final.json").open("ab") as stream:
        stream.write(b" ")
    reference["status_sha256"] = status_hash
    with pytest.raises(ValueError, match="projection hash mismatch for native"):
        summarize_cell(reference, summary, full)


def test_projection_diagnostic_witnesses_are_bounded_and_deterministic(tmp_path):
    path = tmp_path / "ebpf-final.json"
    write(path, [{
        "source": "ebpf", "attempt_key": f"opaque-{index}", "operation_id": "op",
        "phase": "target", "proxy": None, "observation_censored": False,
        "body_evidence": {"reason": "body_missing"}, "steps": [],
    } for index in range(9, -1, -1)])
    group = _projection_diagnostics(path, "ebpf")["groups"][0]
    assert group["attempt_denominator"] == 10
    assert group["bounded_opaque_attempt_witnesses"]["body:body_missing"] == [
        "opaque-0", "opaque-1", "opaque-2", "opaque-3", "opaque-4",
    ]


def test_structural_report_requires_and_emits_nine_cells(tmp_path):
    cells = []
    for mode in ("absent", "partial", "full"):
        for seed in (3, 4, 5):
            cells.append({
                "system": "petclinic", "mode": mode, "seed": seed, "run_id": "100",
                "frozen_graphs": {
                    source: {"service_nodes": 1, "database_logical_nodes": [],
                             "distinct_cross_guest_ancestry_edge_pairs": 0}
                    for source in ("ebpf", "native", "combined")
                },
                "full_capture_parent_links": {
                    source: {"qualified_parent_links": 1, "distinct_cross_guest_ancestry_edge_pairs": 0,
                             "missing_parent_links": 0, "ambiguous_identity_groups": 0,
                             "unresolved_guest_placement_links": 0}
                    for source in ("ebpf", "native", "combined")
                },
                "artifact_transfer": {
                    "summary": {"stored_archive_bytes": 1, "extracted_bytes": 2,
                                "download_and_decompression_seconds": 0.1},
                    "full": {"stored_archive_bytes": 3, "extracted_bytes": 4,
                             "download_and_decompression_seconds": 0.2},
                },
                "projection_recorded_diagnostics": {
                    "sources": {
                        source: {"groups": [{
                            "operation_id": "op", "phase": "target", "attempt_denominator": 1,
                            "proxy_attempts": {"true": 1, "false": 0, "unknown": 0},
                            "censor_flag_attempts": {"true": 0, "false": 1, "not recorded": 0},
                            "step_occurrence_denominator": 0,
                            "body_evidence_reason_attempts": {"not recorded": 1},
                            "payload_verdict_reason_attempts": {"ok": 1},
                            "step_binding_reason_occurrences": {},
                            "step_window_reason_occurrences": {},
                            "step_header_rule_occurrences": {},
                            "step_header_window_rule_occurrences": {},
                        }]}
                        for source in ("ebpf", "native", "combined", "entry_http")
                    }
                },
                "processing_seconds": 0.3,
            })
    _report(cells, "petclinic", tmp_path / "out", {
        "primary_report_run_id": "1",
        "primary_report_transfer": {"stored_archive_bytes": 5, "extracted_bytes": 6,
                                    "download_and_decompression_seconds": 0.4},
    })
    result = json.loads((tmp_path / "out" / "structural-v3.json").read_text())
    assert len(result["cells"]) == 9
    assert len((tmp_path / "out" / "structural-v3.csv").read_text().splitlines()) == 28
    assert len((tmp_path / "out" / "projection-recorded-diagnostics-v3.csv").read_text().splitlines()) == 37
    assert result["correctness_error_rate"] is None
    assert result["costs"]["stored_archive_bytes"] == 41
