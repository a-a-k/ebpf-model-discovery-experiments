import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from ebpf_discovery.structural_v3 import _report, summarize_cell


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
    assert result["correctness_error_rate"] is None
    assert result["costs"]["stored_archive_bytes"] == 41
