"""Read-only structural supplement over frozen v3 models and retained indexes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import ijson
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
PROJECTION_SOURCES = (*SOURCES, "entry_http")
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


def _reason(value: Any) -> str:
    return value if isinstance(value, str) and value else "not recorded"


def _increment(counter: dict[str, int], key: str) -> None:
    counter[key] = counter.get(key, 0) + 1


def _witness(witnesses: dict[str, list[str]], category: str, attempt_key: Any) -> None:
    if not isinstance(attempt_key, str) or not attempt_key:
        return
    witnesses[category] = sorted(set(witnesses.get(category, []) + [attempt_key]))[:WITNESS_LIMIT]


def _projection_diagnostics(path: Path, source: str) -> dict[str, Any]:
    """Stream recorded projection diagnostics without re-projecting retained evidence."""
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    attempts: set[str] = set()
    records = 0
    with path.open("rb") as stream:
        for row in ijson.items(stream, "item", use_float=True):
            if not isinstance(row, dict) or row.get("source") != source:
                raise ValueError(f"{source} projection contains a malformed or cross-source record")
            attempt = row.get("attempt_key")
            operation, phase = row.get("operation_id"), row.get("phase")
            if not all(isinstance(value, str) and value for value in (attempt, operation, phase)):
                raise ValueError(f"{source} projection record lacks its opaque identity or grouping fields")
            if attempt in attempts:
                raise ValueError(f"{source} projection repeats attempt_key {attempt}")
            attempts.add(attempt)
            records += 1
            group = groups.setdefault((operation, phase), {
                "attempt_denominator": 0,
                "proxy_attempts": {"true": 0, "false": 0, "unknown": 0},
                "censor_flag_attempts": {"true": 0, "false": 0, "not recorded": 0},
                "body_evidence_reason_attempts": {}, "payload_verdict_reason_attempts": {},
                "steps_field_attempts": {"recorded": 0, "not recorded": 0},
                "step_occurrence_denominator": 0,
                "step_binding_reason_occurrences": {}, "step_window_reason_occurrences": {},
                "step_header_rule_occurrences": {}, "step_header_window_rule_occurrences": {},
                "bounded_opaque_attempt_witnesses": {},
            })
            group["attempt_denominator"] += 1
            proxy = "true" if row.get("proxy") is True else "false" if row.get("proxy") is False else "unknown"
            group["proxy_attempts"][proxy] += 1
            _witness(group["bounded_opaque_attempt_witnesses"], f"proxy:{proxy}", attempt)
            if "observation_censored" not in row:
                censored = "not recorded"
            else:
                censored = "true" if row.get("observation_censored") is True else (
                    "false" if row.get("observation_censored") is False else "not recorded")
            group["censor_flag_attempts"][censored] += 1
            _witness(group["bounded_opaque_attempt_witnesses"], f"censor:{censored}", attempt)
            body = row.get("body_evidence")
            body_reason = _reason(body.get("reason") if isinstance(body, dict) else None)
            _increment(group["body_evidence_reason_attempts"], body_reason)
            _witness(group["bounded_opaque_attempt_witnesses"], f"body:{body_reason}", attempt)
            payload = row.get("payload_verdict")
            payload_reason = _reason(payload.get("reason") if isinstance(payload, dict) else None)
            _increment(group["payload_verdict_reason_attempts"], payload_reason)
            _witness(group["bounded_opaque_attempt_witnesses"], f"payload:{payload_reason}", attempt)
            steps = row.get("steps")
            if not isinstance(steps, list):
                group["steps_field_attempts"]["not recorded"] += 1
                _witness(group["bounded_opaque_attempt_witnesses"], "steps:not recorded", attempt)
                continue
            group["steps_field_attempts"]["recorded"] += 1
            for step in steps:
                if not isinstance(step, dict):
                    raise ValueError(f"{source} projection contains a malformed step record")
                group["step_occurrence_denominator"] += 1
                binding = _reason(step.get("binding"))
                window = _reason(step.get("window_binding"))
                header = step.get("header_binding")
                header_rule = _reason(header.get("rule") if isinstance(header, dict) else None)
                attribution = header.get("window_attribution") if isinstance(header, dict) else None
                header_window = _reason(attribution.get("rule") if isinstance(attribution, dict) else None)
                for field, reason in (
                    ("step_binding_reason_occurrences", binding),
                    ("step_window_reason_occurrences", window),
                    ("step_header_rule_occurrences", header_rule),
                    ("step_header_window_rule_occurrences", header_window),
                ):
                    _increment(group[field], reason)
                    _witness(group["bounded_opaque_attempt_witnesses"], f"{field}:{reason}", attempt)
    return {
        "records": records,
        "groups": [
            {"operation_id": operation, "phase": phase, **group}
            for (operation, phase), group in sorted(groups.items())
        ],
        "attempt_keys": attempts,
    }


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
        "known_instance_label_nodes": sum(node.get("instance") not in (None, "") for node in services),
        "unknown_instance_label_nodes": sum(node.get("instance") in (None, "") for node in services),
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


def _trace_valid(alias: str) -> str:
    return (f"length({alias}.trace) IN (16,32) AND {alias}.trace NOT GLOB '*[^0-9a-f]*' "
            f"AND trim({alias}.trace,'0')!=''")


def _span_valid(alias: str, field: str = "span") -> str:
    return (f"length({alias}.{field})=16 AND {alias}.{field} NOT GLOB '*[^0-9a-f]*' "
            f"AND trim({alias}.{field},'0')!=''")


def _prepare_valid_ids(db: sqlite3.Connection) -> None:
    """Materialize the original identity predicate once with explicit lookup keys.

    The input database is opened mode=ro. Only the file-backed TEMP schema is
    written, and its cache is bounded independently of the retained index.
    """
    db.execute("PRAGMA temp_store=FILE")
    db.execute("PRAGMA temp.cache_size=-65536")
    db.execute("""CREATE TEMP TABLE valid_ids (
        source TEXT, trace TEXT, span TEXT,
        PRIMARY KEY (source,trace,span)
    )""")
    db.execute("""INSERT INTO temp.valid_ids(source,trace,span)
        SELECT source,trace,span FROM (
          SELECT source,trace,span,COUNT(*) n,MAX(conflicted) conflicting
          FROM main.spans GROUP BY source,trace,span
        ) ids WHERE """ + _trace_valid("ids") + " AND " + _span_valid("ids") +
        " AND n=1 AND conflicting=0")


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
    invalid_identity_count = db.execute(
        f"SELECT COUNT(*) FROM spans s {'WHERE' if source != 'combined' else 'WHERE'} "
        f"NOT ({_trace_valid('s')} AND {_span_valid('s')}) {and_source}", params,
    ).fetchone()[0]
    invalid_identity_rows = db.execute(
        f"SELECT data FROM spans s {'WHERE' if source != 'combined' else 'WHERE'} "
        f"NOT ({_trace_valid('s')} AND {_span_valid('s')}) {and_source} "
        "ORDER BY source,trace,span,digest LIMIT ?",
        (*params, WITNESS_LIMIT),
    ).fetchall()
    parent_valid = _span_valid("c", "parent")
    joins = """
      FROM spans c JOIN temp.valid_ids cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
      JOIN spans p ON p.source=c.source AND p.trace=c.trace AND p.span=c.parent
      JOIN temp.valid_ids pv ON pv.source=p.source AND pv.trace=p.trace AND pv.span=p.span
      WHERE c.parent!='' AND """ + parent_valid + (" AND c.source=?" if source != "combined" else "")
    qualified_links = db.execute(" SELECT COUNT(*) " + joins, params).fetchone()[0]
    pair_rows = db.execute(
        " SELECT DISTINCT c.source,p.service,p.instance,p.node,c.service,c.instance,c.node " + joins,
        params,
    ).fetchall()
    structural_pairs = {tuple(row) for row in pair_rows if tuple(row[1:4]) != tuple(row[4:7])}
    cross_guest = {
        pair for pair in structural_pairs
        if pair[3] not in (None, "") and pair[6] not in (None, "") and pair[3] != pair[6]
    }
    unresolved_count = db.execute(
        " SELECT COUNT(*) " + joins + " AND (c.node IS NULL OR c.node='' OR p.node IS NULL OR p.node='')",
        params,
    ).fetchone()[0]
    witness_select = " SELECT c.data,p.data,c.node,p.node,c.service,c.instance,p.service,p.instance "
    ordered = " ORDER BY c.source,c.trace,c.span,p.span LIMIT ?"
    cross_witnesses = db.execute(
        witness_select + joins
        + " AND c.node IS NOT NULL AND c.node!='' AND p.node IS NOT NULL AND p.node!='' AND c.node!=p.node"
        + ordered,
        (*params, WITNESS_LIMIT),
    ).fetchall()
    unresolved_witnesses = db.execute(
        witness_select + joins + " AND (c.node IS NULL OR c.node='' OR p.node IS NULL OR p.node='')"
        + ordered,
        (*params, WITNESS_LIMIT),
    ).fetchall()
    missing_sql = """
      SELECT c.data FROM spans c
      JOIN temp.valid_ids cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
      WHERE c.parent!='' AND """ + parent_valid + """ AND NOT EXISTS (
        SELECT 1 FROM spans p WHERE p.source=c.source AND p.trace=c.trace AND p.span=c.parent)
    """ + (" AND c.source=?" if source != "combined" else "")
    missing_count = db.execute("SELECT COUNT(*) FROM (" + missing_sql + ")", params).fetchone()[0]
    missing = db.execute(missing_sql + " ORDER BY c.source,c.trace,c.span LIMIT ?", (*params, WITNESS_LIMIT)).fetchall()
    ambiguous_parent_sql = """
      SELECT c.data FROM spans c
      JOIN temp.valid_ids cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
      WHERE c.parent!='' AND """ + parent_valid + """
      AND EXISTS (SELECT 1 FROM spans p WHERE p.source=c.source AND p.trace=c.trace AND p.span=c.parent)
      AND NOT EXISTS (SELECT 1 FROM temp.valid_ids pv WHERE pv.source=c.source AND pv.trace=c.trace AND pv.span=c.parent)
    """ + (" AND c.source=?" if source != "combined" else "")
    ambiguous_parent_count = db.execute(
        "SELECT COUNT(*) FROM (" + ambiguous_parent_sql + ")", params
    ).fetchone()[0]
    ambiguous_parents = db.execute(
        ambiguous_parent_sql + " ORDER BY c.source,c.trace,c.span LIMIT ?", (*params, WITNESS_LIMIT)
    ).fetchall()
    invalid_parent_sql = """
      SELECT c.data FROM spans c
      JOIN temp.valid_ids cv ON cv.source=c.source AND cv.trace=c.trace AND cv.span=c.span
      WHERE c.parent!='' AND NOT (""" + parent_valid + ")" + (
        " AND c.source=?" if source != "combined" else ""
    )
    invalid_parent_count = db.execute(
        "SELECT COUNT(*) FROM (" + invalid_parent_sql + ")", params
    ).fetchone()[0]
    invalid_parents = db.execute(
        invalid_parent_sql + " ORDER BY c.source,c.trace,c.span LIMIT ?", (*params, WITNESS_LIMIT)
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
        "invalid_identity_observations": invalid_identity_count,
        "invalid_parent_references": invalid_parent_count,
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
            "invalid_identity": [
                {"reason": "malformed_or_all_zero_trace_or_span_identity_excluded",
                 "span": _participant(row[0], "span")}
                for row in invalid_identity_rows
            ],
            "invalid_parent_reference": [
                {"reason": "malformed_or_all_zero_parent_excluded", "child": _participant(row[0], "child")}
                for row in invalid_parents
            ],
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
    cell_label = f"{reference.get('system')}/{reference.get('mode')}/{reference.get('seed')}"
    print(f"structural_v3 {cell_label}: verifying retained inputs", flush=True)
    summary_status_path, full_status_path = _one(summary, "status.json"), _one(full, "status.json")
    expected_status_hash = reference.get("status_sha256")
    if (not isinstance(expected_status_hash, str) or len(expected_status_hash) != 64
            or _digest(summary_status_path) != expected_status_hash
            or _digest(full_status_path) != expected_status_hash):
        raise ValueError("admitted status hash does not match compact and full artifacts")
    expected_identity = (
        reference.get("system"), reference.get("mode"), int(reference.get("seed", -1)),
        str(reference.get("run_id")),
    )
    for status in (_read(summary_status_path), _read(full_status_path)):
        actual_identity = (
            status.get("system"), status.get("mode"), int(status.get("seed", -1)), str(status.get("run_id"))
        )
        if actual_identity != expected_identity or status.get("status") != "acquisition_complete":
            raise ValueError("artifact status does not match the admitted campaign cell")
    saved_path, integrity_path = _one(summary, "forecast-saved.json"), _one(summary, "freeze-integrity.json")
    full_saved_path = _one(full, "forecast-saved.json")
    full_integrity_path = _one(full, "freeze-integrity.json")
    if _digest(saved_path) != _digest(full_saved_path) or _digest(integrity_path) != _digest(full_integrity_path):
        raise ValueError("compact and full frozen hash ledgers differ")
    saved, integrity = _read(saved_path), _read(integrity_path)
    expected = saved.get("sha256_by_path")
    if (not isinstance(expected, dict) or integrity.get("sha256_by_path") != expected
            or integrity.get("all_unchanged") is not True):
        raise ValueError("frozen hash ledgers are inconsistent")
    graphs, inputs = {}, {
        "compact/status.json": expected_status_hash, "full/status.json": expected_status_hash,
        "compact/forecast-saved.json": _digest(saved_path),
        "full/forecast-saved.json": _digest(full_saved_path),
        "compact/freeze-integrity.json": _digest(integrity_path),
        "full/freeze-integrity.json": _digest(full_integrity_path),
    }
    compact_metrics_path, full_metrics_path = _one(summary, "metrics-v3.json"), _one(full, "metrics-v3.json")
    if compact_metrics_path.read_bytes() != full_metrics_path.read_bytes():
        raise ValueError("compact and full metrics-v3.json bytes differ")
    metrics_hash = _digest(compact_metrics_path)
    metrics = _read(compact_metrics_path)
    inputs["compact/metrics-v3.json"] = metrics_hash
    inputs["full/metrics-v3.json"] = metrics_hash
    for source in SOURCES:
        relative = f"models/{source}/model.json"
        model_path = summary / relative
        full_model_path = full / relative
        if expected.get(relative) != _digest(model_path):
            raise ValueError(f"saved model hash mismatch for {source}")
        if not full_model_path.is_file() or _digest(full_model_path) != expected[relative]:
            raise ValueError(f"full artifact model hash mismatch for {source}")
        inputs[f"compact/{relative}"] = expected[relative]
        inputs[f"full/{relative}"] = expected[relative]
        graphs[source] = _graph_summary(_read(model_path).get("graph"), source)
    projections, attempt_sets = {}, {}
    source_inputs = metrics.get("source_inputs")
    if not isinstance(source_inputs, dict):
        raise ValueError("compact metrics lack source_inputs")
    for source in PROJECTION_SOURCES:
        projection_path = _one(full, f"{source}-final.json")
        expected_projection_hash = source_inputs.get(source, {}).get("projection_sha256")
        actual_projection_hash = _digest(projection_path)
        if (not isinstance(expected_projection_hash, str) or len(expected_projection_hash) != 64
                or actual_projection_hash != expected_projection_hash):
            raise ValueError(f"retained projection hash mismatch for {source}")
        inputs[f"full/projections/{source}-final.json"] = actual_projection_hash
        projection = _projection_diagnostics(projection_path, source)
        attempt_sets[source] = projection.pop("attempt_keys")
        projections[source] = projection
    first_attempts = attempt_sets[PROJECTION_SOURCES[0]]
    if any(attempt_sets[source] != first_attempts for source in PROJECTION_SOURCES[1:]):
        raise ValueError("retained projections do not contain the same attempt population")
    index = _one(full, "observation-index.sqlite")
    index_hash = _digest(index)
    summary_acquisition_path = _one(summary, "acquisition-complete.json")
    full_acquisition_path = _one(full, "acquisition-complete.json")
    if _digest(summary_acquisition_path) != _digest(full_acquisition_path):
        raise ValueError("compact and full acquisition markers differ")
    if _read(full_acquisition_path).get("index_sha256") != index_hash:
        raise ValueError("final observation index hash does not match acquisition marker")
    print(f"structural_v3 {cell_label}: index hash admitted; preparing keyed identities", flush=True)
    inputs["compact/acquisition-complete.json"] = _digest(summary_acquisition_path)
    inputs["full/acquisition-complete.json"] = _digest(full_acquisition_path)
    inputs["full/observation-index.sqlite"] = index_hash
    reference_placement, reference_hashes = _reference(full)
    inputs.update(reference_hashes)
    uri = index.resolve().as_uri() + "?mode=ro"
    database = sqlite3.connect(uri, uri=True)
    try:
        columns = {row[1] for row in database.execute("PRAGMA table_info(spans)")}
        required = {"digest", "source", "node", "trace", "span", "parent", "service", "instance", "conflicted", "data"}
        if not required <= columns:
            raise ValueError("retained observation index has an unexpected schema")
        _prepare_valid_ids(database)
        print(f"structural_v3 {cell_label}: keyed identities ready after "
              f"{time.perf_counter()-started:.1f}s", flush=True)
        raw = {}
        for source in SOURCES:
            raw[source] = _raw_source(database, source)
            print(f"structural_v3 {cell_label}: {source} structural summary ready after "
                  f"{time.perf_counter()-started:.1f}s", flush=True)
    finally:
        database.close()
    return {
        "schema_version": 1,
        "system": reference["system"], "mode": reference["mode"], "seed": int(reference["seed"]),
        "run_id": str(reference["run_id"]),
        "frozen_graphs": graphs,
        "projection_recorded_diagnostics": {
            "interpretation": (
                "Reasons and flags are records from retained projections, not independently proven root causes. "
                "Reason occurrences can overlap and are not exclusive causes; attempt and step denominators are separate."
            ),
            "missing_fields_label": "not recorded", "witness_limit": WITNESS_LIMIT,
            "sources": projections,
        },
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
            "scope": "supplement input-artifact download/decompression and structural processing only",
            "download_and_decompression_seconds": sum(
                transfer["download_and_decompression_seconds"] for transfer in transfers
            ),
            "processing_seconds": sum(cell["processing_seconds"] for cell in cells),
            "stored_archive_bytes": sum(stored_sizes) if all(value is not None for value in stored_sizes) else None,
            "extracted_bytes": sum(transfer["extracted_bytes"] for transfer in transfers),
            "human_agent_seconds": None,
            "local_compute_seconds": None,
            "complete_runner_job_elapsed_seconds": None,
        },
        "supplement_run_id": provenance.get("supplement_run_id"),
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
    diagnostic_rows = []
    for cell in result["cells"]:
        for source in PROJECTION_SOURCES:
            for group in cell["projection_recorded_diagnostics"]["sources"][source]["groups"]:
                diagnostic_rows.append({
                    "system": system, "mode": cell["mode"], "seed": cell["seed"],
                    "run_id": cell["run_id"], "source": source,
                    "operation_id": group["operation_id"], "phase": group["phase"],
                    "attempt_denominator": group["attempt_denominator"],
                    "proxy_true": group["proxy_attempts"]["true"],
                    "proxy_false": group["proxy_attempts"]["false"],
                    "proxy_unknown": group["proxy_attempts"]["unknown"],
                    "censor_true": group["censor_flag_attempts"]["true"],
                    "censor_false": group["censor_flag_attempts"]["false"],
                    "censor_not_recorded": group["censor_flag_attempts"]["not recorded"],
                    "step_occurrence_denominator": group["step_occurrence_denominator"],
                    "body_evidence_reason_attempts": json.dumps(
                        group["body_evidence_reason_attempts"], sort_keys=True, separators=(",", ":")),
                    "payload_verdict_reason_attempts": json.dumps(
                        group["payload_verdict_reason_attempts"], sort_keys=True, separators=(",", ":")),
                    "step_binding_reason_occurrences": json.dumps(
                        group["step_binding_reason_occurrences"], sort_keys=True, separators=(",", ":")),
                    "step_window_reason_occurrences": json.dumps(
                        group["step_window_reason_occurrences"], sort_keys=True, separators=(",", ":")),
                    "step_header_rule_occurrences": json.dumps(
                        group["step_header_rule_occurrences"], sort_keys=True, separators=(",", ":")),
                    "step_header_window_rule_occurrences": json.dumps(
                        group["step_header_window_rule_occurrences"], sort_keys=True, separators=(",", ":")),
                })
    with (output / "projection-recorded-diagnostics-v3.csv").open(
            "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(diagnostic_rows[0]))
        writer.writeheader()
        writer.writerows(diagnostic_rows)
    lines = [
        f"# Iteration 3 structural supplement: {system}", "",
        "All nine admitted cells are included. Frozen calibration graphs and full-capture parent links are separate.",
        ("Full-capture counts include indexed preparation and control observations; "
         "they are not primary-attempt counts."),
        "Combined-source nodes are a source-qualified union, not additional physical instances.",
        "Deployment and boot records are evaluation-only references and do not correct observed placement.",
        "No per-request independent structural truth is available; correctness error rate remains unknown.", "",
        ("Projection diagnostics reproduce recorded reasons and flags; they are not independently proven root causes, "
         "and overlapping step-reason occurrences are not exclusive causes."),
        "Attempt and step-occurrence denominators are reported separately; absent fields are `not recorded`.", "",
        ("Recorded costs cover input-artifact transfer/decompression and processing only. Complete runner-job, "
         "local-compute, and human/agent effort remain unknown."), "",
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
        "supplement_run_id": os.environ.get("GITHUB_RUN_ID"),
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
            "supplement_run_id": os.environ.get("GITHUB_RUN_ID"),
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
