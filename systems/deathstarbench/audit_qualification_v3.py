"""Bounded, read-only explanation of saved DSB qualification entry bindings.

Consumes existing Actions artifacts. It neither changes a binding rule nor fits
or forecasts a model. Response contents and evaluator outcomes are not read.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import sqlite3

from ebpf_discovery.semantic_v3 import Binder, raw_route
from systems.deathstarbench.contracts_v3 import CONTRACTS, ENTRY_SERVICES

MAX_WITNESSES_PER_REASON_OPERATION = 3
MAX_ANCHORS_PER_WITNESS = 8
MAX_ANCESTORS = 8


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class ReadOnlyStore:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
        self.db.execute("PRAGMA query_only=ON")

    def candidates(self, source: str, request_id: str) -> list[dict]:
        return [json.loads(row[0]) for row in self.db.execute(
            "SELECT data FROM spans WHERE source=? AND request=? ORDER BY start,trace,span",
            (source, request_id))]

    def identity(self, source: str, trace_id: str, span_id: str) -> list[dict]:
        return [json.loads(row[0]) for row in self.db.execute(
            "SELECT data FROM spans WHERE source=? AND trace=? AND span=? ORDER BY digest",
            (source, trace_id, span_id))]

    def nearby_native_entries(self, row: dict, expected: dict) -> list[dict]:
        """Timing context only: nearby spans have no proven request identity."""
        start = row["started_ns"] - 1_000_000_000
        end = row["deadline_ns"] + 1_000_000_000
        result = []
        for item in self.db.execute(
                "SELECT data FROM spans WHERE source='native' AND service='nginx-web-server' "
                "AND start BETWEEN ? AND ? ORDER BY ABS(start-?) LIMIT 80",
                (start, end, row["started_ns"])):
            span = json.loads(item[0])
            if raw_route(span) == (expected["method"], expected["path"]):
                result.append(span)
            if len(result) == 5:
                break
        return result

    def close(self) -> None:
        self.db.close()


def span_fact(span: dict, row: dict) -> dict:
    attrs = span["attributes"]
    started, cutoff = row["started_ns"], row["deadline_ns"]
    body = attrs.get("http.response.body.content")
    return {
        "source": span["source"], "service": span["service"], "instance": span.get("instance"),
        "node": span.get("node"), "trace_id": span["trace_id"], "span_id": span["span_id"],
        "parent_id": span["parent_id"], "kind": span["kind"], "component": attrs.get("component"),
        "method_path": raw_route(span), "start_ns": span["start_ns"], "end_ns": span["end_ns"],
        "start_mod_millisecond_ns": span["start_ns"] % 1_000_000,
        "end_mod_millisecond_ns": span["end_ns"] % 1_000_000,
        "start_minus_journal_ns": span["start_ns"]-started,
        "end_minus_cutoff_ns": span["end_ns"]-cutoff,
        "inside_sealed_window": started <= span["start_ns"] <= span["end_ns"] <= cutoff,
        "response_status": attrs.get("http.response.status_code", attrs.get("http.status_code")),
        "response_body_present": isinstance(body, str),
        "response_body_bytes": len(body.encode("utf-8")) if isinstance(body, str) else None,
        "attribute_conflict_keys": [item.get("key") for item in span.get("attribute_conflicts", [])],
        "raw_file_basename": Path(span.get("raw_file") or "").name,
    }


def anchor_chain(store: ReadOnlyStore, anchor: dict, row: dict) -> dict:
    chain = []
    current = anchor
    seen = set()
    stop = "depth_limit"
    for _ in range(MAX_ANCESTORS):
        identity = (current["trace_id"], current["span_id"])
        if identity in seen:
            stop = "cycle"
            break
        seen.add(identity)
        chain.append(span_fact(current, row))
        parent_id = current.get("parent_id")
        if not parent_id:
            stop = "root"
            break
        parents = store.identity(current["source"], current["trace_id"], parent_id)
        if len(parents) != 1:
            stop = "missing_parent" if not parents else "conflicting_parent_identity"
            break
        parent = parents[0]
        if any(parent.get(key) != anchor.get(key) for key in ("service", "instance", "node")):
            stop = "different_service_instance_or_node"
            chain.append(span_fact(parent, row))
            break
        current = parent
    return {"spans": chain, "stop": stop}


def find_capture(inputs: Path) -> Path:
    matches = []
    for status_file in inputs.rglob("status.json"):
        status = json.loads(status_file.read_text(encoding="utf-8"))
        if (status.get("system"), status.get("mode"), status.get("seed")) == (
                "deathstarbench", "full", 3):
            matches.append(status_file.parent)
    if len(matches) != 1:
        raise ValueError(f"Expected one saved DSB full/seed-3 qualification; found {len(matches)}")
    return matches[0]


def audit(capture: Path) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Research capture diagnostics run in GitHub Actions only")
    projection_path = capture / "projections" / "native-final.json"
    ebpf_projection_path = capture / "projections" / "ebpf-final.json"
    index_path = capture / "observation-index.sqlite"
    status_path = capture / "status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    if status.get("status") != "qualification_complete" or status.get("system") != "deathstarbench":
        raise ValueError("Saved DSB qualification is incomplete")
    rows = json.loads(projection_path.read_text(encoding="utf-8"))
    ebpf_rows = json.loads(ebpf_projection_path.read_text(encoding="utf-8"))
    if len(rows) != 1200 or len({row["attempt_key"] for row in rows}) != 1200:
        raise ValueError("Expected 1200 distinct saved DSB qualification projections")
    if len(ebpf_rows) != 1200 or {row["attempt_key"] for row in ebpf_rows} != {
            row["attempt_key"] for row in rows}:
        raise ValueError("eBPF and native qualification attempt populations differ")
    store = ReadOnlyStore(index_path)
    try:
        binder = Binder(store, "deathstarbench")
        reasons, bodies, entry_replay, windows, anchor_categories = (
            Counter(), Counter(), Counter(), Counter(), Counter())
        boundary_flags, revised_eligibility = Counter(), Counter()
        by_operation = Counter()
        witnesses = defaultdict(list)
        for row in sorted(rows, key=lambda item: item["attempt_key"]):
            operation = row["operation_id"]
            expected = CONTRACTS[operation]["steps"][0]
            request_id = row["step_ids"][0]
            step = row["steps"][0]
            reason = step["binding"]
            body_reason = row.get("body_evidence", {}).get("reason", "missing")
            anchors = store.candidates("native", request_id)
            anchor_categories["no_native_header_anchor" if not anchors else
                              "allowed_service_header_anchor" if any(
                                  anchor["service"] in ENTRY_SERVICES["native"] for anchor in anchors)
                              else "only_other_service_header_anchors"] += 1
            reasons[reason] += 1
            bodies[body_reason] += 1
            by_operation[(operation, reason, body_reason)] += 1
            entry, replay_reason = binder.entry("native", request_id, expected)
            entry_replay[replay_reason] += 1
            relation = "unbound_before_window"
            eligible, revised_reason, proof = (False, "entry_unbound", None)
            if entry:
                relation = ("inside" if row["started_ns"] <= entry["start_ns"] <=
                            entry["end_ns"] <= row["deadline_ns"] else "outside")
                if entry["start_ns"] < row["started_ns"]:
                    boundary_flags["start_before_journal"] += 1
                if entry["end_ns"] > row["deadline_ns"]:
                    boundary_flags["end_after_cutoff"] += 1
                if entry["end_ns"] < entry["start_ns"]:
                    boundary_flags["inverted_outer"] += 1
                if relation == "inside":
                    boundary_flags["strict_inside"] += 1
                eligible, revised_reason, proof = binder.entry_window(entry, "native", request_id, row)
            windows[relation] += 1
            revised_eligibility[(reason, revised_reason, eligible)] += 1
            if len(witnesses[(operation, reason)]) >= MAX_WITNESSES_PER_REASON_OPERATION:
                continue
            witness = {
                "attempt_key": row["attempt_key"], "operation": operation,
                "request_id": request_id, "journal_started_ns": row["started_ns"],
                "journal_ended_ns": row["ended_ns"], "cutoff_ns": row["deadline_ns"],
                "observation_censored": row.get("observation_censored"),
                "saved_binding_reason": reason, "saved_body_reason": body_reason,
                "replayed_pre_window_entry_reason": replay_reason,
                "replayed_entry": span_fact(entry, row) if entry else None,
                "revised_entry_eligible": eligible, "revised_entry_reason": revised_reason,
                "revised_attribution_proof": proof,
                "total_native_header_anchors": len(anchors),
                "anchors_shown": [anchor_chain(store, anchor, row)
                                  for anchor in anchors[:MAX_ANCHORS_PER_WITNESS]],
                "anchors_omitted": max(0, len(anchors)-MAX_ANCHORS_PER_WITNESS),
                "nearby_expected_route_without_identity": [
                    span_fact(span, row) for span in store.nearby_native_entries(row, expected)
                ] if not anchors else [],
            }
            witnesses[(operation, reason)].append(witness)
        return {
            "kind": "retained_dsb_native_binding_diagnostic", "no_new_traffic_or_fitting": True,
            "source_run_id": status.get("run_id"), "qualification_attempts": len(rows),
            "audit_code_sha": os.environ.get("GITHUB_SHA"),
            "input_sha256": {"native_projection": digest(projection_path),
                             "ebpf_projection": digest(ebpf_projection_path), "index": digest(index_path),
                             "status": digest(status_path)},
            "native_entry_services": ENTRY_SERVICES["native"],
            "ebpf_binding_reasons": dict(sorted(Counter(
                row["steps"][0]["binding"] for row in ebpf_rows).items())),
            "binding_reasons": dict(sorted(reasons.items())),
            "body_reasons": dict(sorted(bodies.items())),
            "native_header_anchor_categories": dict(sorted(anchor_categories.items())),
            "pre_window_entry_replay_reasons": dict(sorted(entry_replay.items())),
            "pre_window_entry_window_relation": dict(sorted(windows.items())),
            "raw_entry_boundary_counts": dict(sorted(boundary_flags.items())),
            "saved_binding_vs_revised_eligibility": [
                {"saved_binding": saved, "revised_reason": revised, "eligible": eligible,
                 "n": count}
                for (saved, revised, eligible), count in sorted(revised_eligibility.items())],
            "by_operation_binding_body": [
                {"operation": operation, "binding": binding, "body_reason": body, "n": count}
                for (operation, binding, body), count in sorted(by_operation.items())],
            "witnesses": [item for key in sorted(witnesses) for item in witnesses[key]],
            "witness_selection": "first three attempt hashes per operation and saved binding reason",
            "timing_interpretation": ("Timestamp residues and journal differences are descriptive. "
                                      "A coarse exported native timestamp or an older capture does not prove "
                                      "the cause of missing bindings, clock offset, or admissibility of a tolerance."),
            "raw_response_bodies_retained_in_source_artifact_only": True,
        }
    finally:
        store.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(find_capture(args.inputs))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
