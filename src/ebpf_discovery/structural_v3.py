"""Read-only structural supplement over frozen v3 models and retained indexes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import time
from typing import Any

SOURCES = ("ebpf", "native", "combined")
MODES = ("absent", "partial", "full")
SEEDS = (3, 4, 5)
WITNESS_LIMIT = 5


def _require_actions() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Structural report computation runs in GitHub Actions only")


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _tree_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _one(root: Path, name: str) -> Path:
    matches = list(root.rglob(name))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {name} below {root}, found {len(matches)}")
    return matches[0]


def _safe_remove(path: Path, root: Path) -> None:
    resolved, boundary = path.resolve(), root.resolve()
    if resolved == boundary or boundary not in resolved.parents:
        raise ValueError(f"refusing cleanup outside structural work root: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def _graph_summary(graph: dict[str, Any], source: str) -> dict[str, Any]:
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError(f"{source} frozen graph is malformed")
    services = [node for node in nodes if node.get("kind") == "service"]
    databases = [node for node in nodes if node.get("kind") == "database"]
    by_id = {node.get("id"): node for node in services}
    cross_guest = set()
    for edge in edges:
        parent, child = by_id.get(edge.get("from")), by_id.get(edge.get("to"))
        if (parent and child and parent.get("guest") not in (None, "")
                and child.get("guest") not in (None, "") and parent["guest"] != child["guest"]):
            cross_guest.add((
                parent.get("source"), parent.get("service"), parent.get("instance"), parent.get("guest"),
                child.get("service"), child.get("instance"), child.get("guest"), edge.get("evidence"),
            ))
    return {
        "service_nodes": len(services),
        "service_labels": sorted({str(node.get("service")) for node in services}),
        "observed_instance_labels": sorted({str(node["instance"]) for node in services if node.get("instance")}),
        "known_guest_placement": sum(node.get("guest") not in (None, "") for node in services),
        "unknown_guest_placement": sum(node.get("guest") in (None, "") for node in services),
        "database_logical_nodes": [{
            "source": node.get("source"), "system": node.get("system"),
            "address": node.get("address"), "port": node.get("port"),
            "namespace": node.get("namespace"), "concrete_physical_instance_confirmed": None,
        } for node in databases],
        "distinct_cross_guest_ancestry_edge_pairs": len(cross_guest),
        "cross_guest_edge_pairs": [list(item) for item in sorted(cross_guest, key=str)],
        "qualified_union_not_additional_physical_instances": source == "combined",
        "frozen_graph_scope": "calibration snapshot used by the saved model",
    }


def _participant(raw: str, role: str) -> dict[str, Any]:
    row = json.loads(raw)
    return {
        "role": role, "source": row.get("source"), "trace_id": row.get("trace_id"),
        "span_id": row.get("span_id"), "parent_id": row.get("parent_id"),
        "span_kind": row.get("kind"), "service": row.get("service"),
        "instance": row.get("instance"), "observer_guest": row.get("node"),
        "raw_file": row.get("raw_file"),
    }


def _raw_source(db: sqlite3.Connection, source: str) -> dict[str, Any]:
    where, params = ("", ()) if source == "combined" else ("WHERE source=?", (source,))
    and_source = "" if source == "combined" else "AND s.source=?"
    identity_groups = db.execute(
        f"SELECT COUNT(*) FROM (SELECT source,trace,span FROM spans {where} GROUP BY source,trace,span)", params
    ).fetchone()[0]
    ambiguous = db.execute(
        f"SELECT COUNT(*) FROM (SELECT source,trace,span FROM spans {where} "
        "GROUP BY source,trace,span HAVING COUNT(*) != 1)", params
    ).fetchone()[0]
    conflicted = db.execute(
        f"SELECT COUNT(*) FROM spans s {'WHERE' if source != 'combined' else 'WHERE'} conflicted!=0 {and_source}",
        params,
    ).fetchone()[0]
    valid = """WITH ids AS (
      SELECT source,trace,span,COUNT(*) n,MAX(conflicted) conflicting FROM spans GROUP BY source,trace,span
    ), valid AS (SELECT source,trace,span FROM ids WHERE n=1 AND conflicting=0)"""
    joins = """
      FROM spans c JOIN valid cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
      JOIN spans p ON p.source=c.source AND p.trace=c.trace AND p.span=c.parent
      JOIN valid pv ON pv.source=p.source AND pv.trace=p.trace AND pv.span=p.span
      WHERE c.parent!=''""" + (" AND c.source=?" if source != "combined" else "")
    qualified_links = db.execute(valid + " SELECT COUNT(*) " + joins, params).fetchone()[0]
    pair_rows = db.execute(
        valid + " SELECT DISTINCT c.source,p.service,p.instance,p.node,c.service,c.instance,c.node " + joins,
        params,
    ).fetchall()
    structural_pairs = {tuple(row) for row in pair_rows if tuple(row[1:4]) != tuple(row[4:7])}
    cross_guest = {
        pair for pair in structural_pairs
        if pair[3] not in (None, "") and pair[6] not in (None, "") and pair[3] != pair[6]
    }
    unresolved_count = db.execute(
        valid + " SELECT COUNT(*) " + joins + " AND (c.node IS NULL OR c.node='' OR p.node IS NULL OR p.node='')",
        params,
    ).fetchone()[0]
    witness_select = " SELECT c.data,p.data,c.node,p.node,c.service,c.instance,p.service,p.instance "
    ordered = " ORDER BY c.source,c.trace,c.span,p.span LIMIT ?"
    cross_witnesses = db.execute(
        valid + witness_select + joins
        + " AND c.node IS NOT NULL AND c.node!='' AND p.node IS NOT NULL AND p.node!='' AND c.node!=p.node"
        + ordered,
        (*params, WITNESS_LIMIT),
    ).fetchall()
    unresolved_witnesses = db.execute(
        valid + witness_select + joins + " AND (c.node IS NULL OR c.node='' OR p.node IS NULL OR p.node='')"
        + ordered,
        (*params, WITNESS_LIMIT),
    ).fetchall()
    missing_sql = valid + """
      SELECT c.data FROM spans c
      JOIN valid cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
      WHERE c.parent!='' AND NOT EXISTS (
        SELECT 1 FROM spans p WHERE p.source=c.source AND p.trace=c.trace AND p.span=c.parent)
    """ + (" AND c.source=?" if source != "combined" else "")
    missing_count = db.execute("SELECT COUNT(*) FROM (" + missing_sql + ")", params).fetchone()[0]
    missing = db.execute(missing_sql + " ORDER BY c.source,c.trace,c.span LIMIT ?", (*params, WITNESS_LIMIT)).fetchall()
    ambiguous_parent_sql = valid + """
      SELECT c.data FROM spans c
      JOIN valid cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
      WHERE c.parent!=''
      AND EXISTS (SELECT 1 FROM spans p WHERE p.source=c.source AND p.trace=c.trace AND p.span=c.parent)
      AND NOT EXISTS (SELECT 1 FROM valid pv WHERE pv.source=c.source AND pv.trace=c.trace AND pv.span=c.parent)
    """ + (" AND c.source=?" if source != "combined" else "")
    ambiguous_parent_count = db.execute(
        "SELECT COUNT(*) FROM (" + ambiguous_parent_sql + ")", params
    ).fetchone()[0]
    ambiguous_parents = db.execute(
        ambiguous_parent_sql + " ORDER BY c.source,c.trace,c.span LIMIT ?", (*params, WITNESS_LIMIT)
    ).fetchall()
    ambiguous_witness_sql = (
        f"SELECT source,trace,span FROM spans {where} "
        "GROUP BY source,trace,span HAVING COUNT(*) != 1 ORDER BY source,trace,span LIMIT ?"
    )
    ambiguous_witnesses = []
    for identity_source, trace, span in db.execute(ambiguous_witness_sql, (*params, WITNESS_LIMIT)):
        variants = db.execute(
            "SELECT data FROM spans WHERE source=? AND trace=? AND span=? ORDER BY digest",
            (identity_source, trace, span),
        ).fetchall()
        ambiguous_witnesses.append({
            "reason": "ambiguous_same_source_trace_span_identity",
            "variants": [_participant(item[0], "identity_variant") for item in variants],
        })
    def pair_witness(row: tuple[Any, ...], reason: str) -> dict[str, Any]:
        return {"reason": reason, "child": _participant(row[0], "child"),
                "parent": _participant(row[1], "parent")}
    return {
        "identity_groups": identity_groups,
        "ambiguous_identity_groups": ambiguous,
        "attribute_conflicted_observations": conflicted,
        "qualified_parent_links": qualified_links,
        "distinct_structural_edge_pairs": len(structural_pairs),
        "distinct_cross_guest_ancestry_edge_pairs": len(cross_guest),
        "cross_guest_edge_pairs": [list(pair) for pair in sorted(cross_guest, key=str)],
        "missing_parent_links": missing_count,
        "ambiguous_parent_links": ambiguous_parent_count,
        "unresolved_guest_placement_links": unresolved_count,
        "witnesses": {
            "cross_guest": [pair_witness(row, "qualified_cross_guest_parent_id") for row in cross_witnesses],
            "missing_parent": [{"reason": "parent_identity_absent", "child": _participant(row[0], "child")}
                               for row in missing],
            "ambiguous_identity": ambiguous_witnesses,
            "ambiguous_parent": [{"reason": "parent_identity_not_unique_or_conflicted",
                                  "child": _participant(row[0], "child")}
                                 for row in ambiguous_parents],
            "unresolved_placement": [pair_witness(row, "qualified_parent_id_guest_unknown")
                                     for row in unresolved_witnesses],
        },
        "scope": "full retained capture source-local parent-ID links",
        "population_scope": (
            "all observations indexed through the final snapshot, including preparation and control observations; "
            "not filtered to primary workload attempts"
        ),
        "operation_level_causality_inferred": False,
        "independent_cross_guest_correctness_error_rate": None,
    }


def _reference(full: Path) -> tuple[dict[str, Any], dict[str, str]]:
    deployment = _read(_one(full, "deployment.json"))
    hashes = {"deployment.json": _digest(_one(full, "deployment.json"))}
    boot_ids = {}
    for guest in ("a", "b"):
        candidates = [path for path in full.rglob("check.txt") if path.parent.name == guest]
        if len(candidates) == 1:
            lines = candidates[0].read_text(encoding="utf-8", errors="replace").splitlines()
            value = lines[1].strip() if len(lines) > 1 else ""
            boot_ids[guest] = value if re.fullmatch(r"[0-9a-f-]{36}", value) else None
            hashes[f"infrastructure/{guest}/check.txt"] = _digest(candidates[0])
        else:
            boot_ids[guest] = None
    container_files = sorted(
        path for path in full.rglob("*")
        if path.is_file() and "container" in path.name.lower() and path.suffix.lower() in {".json", ".yml", ".yaml"}
    )
    for path in container_files:
        hashes[f"reference/{path.relative_to(full).as_posix()}"] = _digest(path)
    return ({
        "evaluation_only": True,
        "observed_graph_placement_not_corrected_from_reference": True,
        "replicas": deployment.get("replicas"),
        "database": deployment.get("database"),
        "routing": deployment.get("routing", deployment.get("proxy", deployment.get("proxy_discovery"))),
        "guest_boot_ids": boot_ids,
        "distinct_guest_boot_ids_confirmed": (
            None if None in boot_ids.values() else len(set(boot_ids.values())) == 2
        ),
        "reference_resolved_service_placement": None,
        "container_reference_files": [path.relative_to(full).as_posix() for path in container_files],
        "no_name_or_ip_causality_inferred": True,
    }, hashes)


def summarize_cell(reference: dict[str, Any], summary: Path, full: Path,
                   download: dict[str, Any] | None = None) -> dict[str, Any]:
    """Summarize one admitted cell without changing any retained input."""
    started = time.perf_counter()
    saved_path, integrity_path = _one(summary, "forecast-saved.json"), _one(summary, "freeze-integrity.json")
    saved, integrity = _read(saved_path), _read(integrity_path)
    expected = saved.get("sha256_by_path")
    if (not isinstance(expected, dict) or integrity.get("sha256_by_path") != expected
            or integrity.get("all_unchanged") is not True):
        raise ValueError("frozen hash ledgers are inconsistent")
    graphs, inputs = {}, {
        "forecast-saved.json": _digest(saved_path), "freeze-integrity.json": _digest(integrity_path)
    }
    for source in SOURCES:
        relative = f"models/{source}/model.json"
        model_path = summary / relative
        if expected.get(relative) != _digest(model_path):
            raise ValueError(f"saved model hash mismatch for {source}")
        inputs[relative] = expected[relative]
        graphs[source] = _graph_summary(_read(model_path).get("graph"), source)
    index = _one(full, "observation-index.sqlite")
    inputs["observation-index.sqlite"] = _digest(index)
    reference_placement, reference_hashes = _reference(full)
    inputs.update(reference_hashes)
    uri = index.resolve().as_uri() + "?mode=ro"
    database = sqlite3.connect(uri, uri=True)
    try:
        columns = {row[1] for row in database.execute("PRAGMA table_info(spans)")}
        required = {"digest", "source", "node", "trace", "span", "parent", "service", "instance", "conflicted", "data"}
        if not required <= columns:
            raise ValueError("retained observation index has an unexpected schema")
        raw = {source: _raw_source(database, source) for source in SOURCES}
    finally:
        database.close()
    return {
        "schema_version": 1,
        "system": reference["system"], "mode": reference["mode"], "seed": int(reference["seed"]),
        "run_id": str(reference["run_id"]),
        "frozen_graphs": graphs,
        "full_capture_parent_links": raw,
        "reference_placement": reference_placement,
        "input_sha256": inputs,
        "artifact_transfer": download,
        "processing_seconds": time.perf_counter() - started,
        "correctness_error_rate": None,
        "graph_only_forecast_benefit_evaluated": False,
        "interpretation": (
            "Frozen graph edges and full-capture source-local parent-ID links are structural observations, not "
            "per-request independent correctness. Combined is a qualified union, not additional physical instances."
        ),
    }


def _artifact(run_id: str, name: str) -> dict[str, Any]:
    raw = subprocess.check_output([
        "gh", "api", "--paginate", "--slurp",
        f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{run_id}/artifacts?per_page=100",
    ], text=True)
    matches = [row for page in json.loads(raw) for row in page["artifacts"] if row.get("name") == name]
    if len(matches) != 1 or matches[0].get("expired") is True:
        raise ValueError(f"expected one unexpired artifact {name} in run {run_id}")
    return matches[0]


def _download(run_id: str, name: str, destination: Path) -> dict[str, Any]:
    artifact = _artifact(run_id, name)
    started = time.perf_counter()
    subprocess.run(["gh", "run", "download", run_id, "-n", name, "-D", str(destination)], check=True)
    return {
        "artifact_id": artifact["id"], "artifact_name": name,
        "github_artifact_digest": artifact.get("digest"),
        "stored_archive_bytes": artifact.get("size_in_bytes"),
        "extracted_bytes": _tree_bytes(destination),
        "download_and_decompression_seconds": time.perf_counter() - started,
    }


def _report(cells: list[dict[str, Any]], system: str, output: Path, provenance: dict[str, Any]) -> None:
    expected = {(mode, seed) for mode in MODES for seed in SEEDS}
    if {(row["mode"], row["seed"]) for row in cells} != expected or len(cells) != 9:
        raise ValueError(f"{system} structural report requires exactly nine admitted cells")
    transfers = [provenance["primary_report_transfer"]] + [
        transfer for cell in cells for transfer in (cell["artifact_transfer"] or {}).values()
    ]
    stored_sizes = [transfer.get("stored_archive_bytes") for transfer in transfers]
    result = {
        "schema_version": 1, "system": system, "cells": sorted(cells, key=lambda row: (row["mode"], row["seed"])),
        "provenance": provenance, "correctness_error_rate": None,
        "full_capture_counts_are_not_frozen_graph_edges": True,
        "combined_is_source_qualified_union_not_physical_instance_count": True,
        "graph_only_forecast_benefit_evaluated": False,
        "costs": {
            "download_and_decompression_seconds": sum(
                transfer["download_and_decompression_seconds"] for transfer in transfers
            ),
            "processing_seconds": sum(cell["processing_seconds"] for cell in cells),
            "stored_archive_bytes": sum(stored_sizes) if all(value is not None for value in stored_sizes) else None,
            "extracted_bytes": sum(transfer["extracted_bytes"] for transfer in transfers),
            "human_agent_seconds": None,
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    _write(output / "structural-v3.json", result)
    rows = []
    for cell in result["cells"]:
        for source in SOURCES:
            graph, raw = cell["frozen_graphs"][source], cell["full_capture_parent_links"][source]
            rows.append({
                "system": system, "mode": cell["mode"], "seed": cell["seed"], "run_id": cell["run_id"],
                "source": source, "frozen_service_nodes": graph["service_nodes"],
                "frozen_database_logical_nodes": len(graph["database_logical_nodes"]),
                "frozen_cross_guest_edge_pairs": graph["distinct_cross_guest_ancestry_edge_pairs"],
                "full_qualified_parent_links": raw["qualified_parent_links"],
                "full_cross_guest_edge_pairs": raw["distinct_cross_guest_ancestry_edge_pairs"],
                "missing_parents": raw["missing_parent_links"], "ambiguous_ids": raw["ambiguous_identity_groups"],
                "unresolved_placement": raw["unresolved_guest_placement_links"],
                "correctness_error_rate": None,
            })
    with (output / "structural-v3.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        f"# Iteration 3 structural supplement: {system}", "",
        "All nine admitted cells are included. Frozen calibration graphs and full-capture parent links are separate.",
        ("Full-capture counts include indexed preparation and control observations; "
         "they are not primary-attempt counts."),
        "Combined-source nodes are a source-qualified union, not additional physical instances.",
        "Deployment and boot records are evaluation-only references and do not correct observed placement.",
        "No per-request independent structural truth is available; correctness error rate remains unknown.", "",
        ("| Mode | Seed | Source | Frozen services | Frozen DB logical nodes | Frozen/full cross-guest pairs | "
         "Missing parent | Ambiguous ID | Unresolved placement |"),
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['mode']} | {row['seed']} | {row['source']} | {row['frozen_service_nodes']} | "
            f"{row['frozen_database_logical_nodes']} | {row['frozen_cross_guest_edge_pairs']}/"
            f"{row['full_cross_guest_edge_pairs']} | {row['missing_parents']} | {row['ambiguous_ids']} | "
            f"{row['unresolved_placement']} |"
        )
    (output / "structural-v3.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(report_run_id: str, system: str, work: Path, output: Path) -> None:
    _require_actions()
    if not report_run_id.isdigit() or system not in {"deathstarbench", "otel_demo", "petclinic"}:
        raise ValueError("invalid report run ID or system")
    root = work.resolve()
    allowed = (Path.cwd() / "work" / "structural-v3").resolve()
    if root != allowed and allowed not in root.parents:
        raise ValueError("structural temporary directory must remain below work/structural-v3")
    root.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    status_path = output / "status.json"
    status = {
        "status": "running", "report_run_id": report_run_id, "system": system,
        "cells_completed": 0, "started_ns": time.time_ns(), "analysis_commit": os.environ.get("GITHUB_SHA"),
    }
    _write(status_path, status)
    report_dir = root / "primary-report"
    cells_dir = output / "cells"
    try:
        _safe_remove(report_dir, root)
        report_transfer = _download(report_run_id, f"report-v3-{report_run_id}", report_dir)
        results_path = _one(report_dir, "results.json")
        results = _read(results_path)
        if results.get("campaigns") != 27:
            raise ValueError("primary report does not declare 27 campaigns")
        references = results.get("campaign_references")
        if not isinstance(references, list) or len(references) != 27:
            raise ValueError("primary report does not contain exactly 27 admitted campaign references")
        expected_all = {
            (candidate, mode, seed)
            for candidate in ("deathstarbench", "otel_demo", "petclinic") for mode in MODES for seed in SEEDS
        }
        identities = {
            (row.get("system"), row.get("mode"), int(row.get("seed", -1))) for row in references
        }
        if identities != expected_all:
            raise ValueError("primary report campaign references are not the fixed 27-cell population")
        selected = [row for row in references if row.get("system") == system]
        expected = {(mode, seed) for mode in MODES for seed in SEEDS}
        if len(selected) != 9 or {(row.get("mode"), int(row.get("seed", -1))) for row in selected} != expected:
            raise ValueError(f"primary report does not identify the nine admitted {system} cells")
        cells = []
        for reference in sorted(selected, key=lambda row: (row["mode"], int(row["seed"]))):
            run_id, mode, seed = str(reference["run_id"]), reference["mode"], int(reference["seed"])
            if not run_id.isdigit():
                raise ValueError("admitted campaign run ID is not numeric")
            cell_work = root / f"{mode}-{seed}-{run_id}"
            _safe_remove(cell_work, root)
            summary, full = cell_work / "summary", cell_work / "full"
            try:
                summary_name = f"v3-summary-{system}-{mode}-{seed}-{run_id}"
                full_name = f"campaign-v3-{system}-{mode}-{seed}-{run_id}"
                transfers = {
                    "summary": _download(run_id, summary_name, summary),
                    "full": _download(run_id, full_name, full),
                }
                cell = summarize_cell(reference, summary, full, transfers)
                _write(cells_dir / f"{mode}-{seed}-{run_id}.json", cell)
                cells.append(cell)
                status["cells_completed"] = len(cells)
                _write(status_path, status)
            finally:
                _safe_remove(cell_work, root)
        provenance = {
            "primary_report_run_id": report_run_id,
            "primary_results_sha256": _digest(results_path),
            "primary_report_transfer": report_transfer,
            "report_campaign_references": selected,
            "analysis_commit": os.environ.get("GITHUB_SHA"),
            "repository": os.environ.get("GITHUB_REPOSITORY"),
            "all_computation_in_github_actions": True,
        }
        _report(cells, system, output, provenance)
        status["status"] = "complete"
    except Exception as exc:
        status.update(status="technical_failure", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        status["ended_ns"] = time.time_ns()
        _write(status_path, status)
        if report_dir.exists():
            _safe_remove(report_dir, root)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-run-id", required=True)
    parser.add_argument("--system", required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.report_run_id, args.system, args.work, args.out)


if __name__ == "__main__":
    main()
