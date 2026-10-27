"""Bounded post-acquisition body-fidelity audit for OTel v3 qualification.

This module consumes only retained request journals and saved source projections.
It does not fit a model or use evaluator success, SQL, or async-oracle fields.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
from typing import Any

import ijson


def _attempt_key(record: dict[str, Any]) -> str:
    return hashlib.sha256(record["attempt_id"].encode()).hexdigest()


def _body(encoded: Any) -> tuple[str | None, int | None]:
    if encoded is None:
        return None, None
    try:
        raw = base64.b64decode(encoded, validate=True)
        # Reproduce qualification_v3 exactly: strict UTF-8 decode followed by
        # hashing the encoded text, which round-trips to the original bytes.
        text = raw.decode("utf-8", errors="strict")
    except (ValueError, UnicodeDecodeError):
        return None, None
    data = text.encode("utf-8")
    return hashlib.sha256(data).hexdigest(), len(data)


def _external_fact(record: dict[str, Any]) -> dict[str, Any]:
    intent = record.get("request_intent") or {}
    planned = intent.get("steps") or []
    actual = record.get("http_steps") or []
    planned_final = planned[-1] if planned else None
    planned_id = planned_final.get("request_id") if planned_final else None
    observed = [step for step in actual if step.get("request_id") == planned_id]
    final = observed[-1] if len(observed) == 1 else None
    last = actual[-1] if actual else None
    encoded = None if last is None else last.get(
        "response_body_b64", last.get("response_body_base64")
    )
    body_sha, body_bytes = _body(encoded)
    final_completed = bool(
        final is not None
        and final.get("status") is not None
        and not final.get("transport_error")
        and not final.get("error")
    )
    if final is None:
        dispatch_state = "aborted_before_final"
    elif final_completed:
        dispatch_state = "final_completed"
    else:
        dispatch_state = "final_incomplete"
    started = int(record.get("started_ns") or 0)
    ended = int(record.get("ended_ns") or 0)
    deadline = started + int(float(record.get("deadline_seconds", 2.0)) * 1e9)
    return {
        "attempt_key": _attempt_key(record),
        "operation": record.get("operation"),
        "planned_final_request_id": planned_id,
        "actual_last_request_id": last.get("request_id") if last else None,
        "actual_step_count": len(actual),
        "planned_step_count": len(planned),
        "final_planned_step_observed": len(observed) == 1,
        "final_planned_step_ambiguous": len(observed) > 1,
        "final_step_completed": final_completed,
        "dispatch_state": "ambiguous_final_step" if len(observed) > 1 else dispatch_state,
        "client_status": final.get("status") if final else None,
        "transport_error": final.get("transport_error") if final else None,
        "client_error": final.get("error") if final else None,
        "comparison_step_is_planned_final": bool(last and planned_id and last.get("request_id") == planned_id),
        "external_body_sha256": body_sha,
        "external_body_bytes": body_bytes,
        "started_ns": started,
        "ended_ns": ended,
        "deadline_ns": deadline,
        "external_timely": ended <= deadline,
    }


def _stream_array(path: Path):
    with path.open("rb") as stream:
        yield from ijson.items(stream, "item")


def _index_external(path: Path, database: sqlite3.Connection) -> int:
    database.execute("CREATE TABLE external (attempt_key TEXT PRIMARY KEY, evidence TEXT NOT NULL)")
    count = 0
    for record in _stream_array(path):
        fact = _external_fact(record)
        database.execute(
            "INSERT INTO external(attempt_key,evidence) VALUES (?,?)",
            (fact["attempt_key"], json.dumps(fact, separators=(",", ":"))),
        )
        count += 1
    database.commit()
    return count


def _source_audit(path: Path, source: str, database: sqlite3.Connection) -> dict[str, Any]:
    counts = Counter()
    strata = Counter()
    mismatches = []
    for projection in _stream_array(path):
        counts["projection_rows"] += 1
        found = database.execute(
            "SELECT evidence FROM external WHERE attempt_key=?",
            (projection.get("attempt_key"),),
        ).fetchone()
        if found is None:
            counts["external_attempt_missing"] += 1
            continue
        external = json.loads(found[0])
        body_evidence = projection.get("body_evidence") or {}
        captured_sha = body_evidence.get("sha256")
        if not captured_sha:
            counts["source_body_sha_missing"] += 1
            continue
        counts["source_body_evidence"] += 1
        external_sha = external.get("external_body_sha256")
        if external_sha is None:
            counts["external_body_unavailable"] += 1
            continue

        # This is the exact comparison population used by qualification_v3.
        counts["compared"] += 1
        dispatch_state = external["dispatch_state"]
        equal = captured_sha == external_sha
        strata[(dispatch_state, "match" if equal else "mismatch")] += 1
        if equal:
            counts["exact_body_matches"] += 1
            continue

        counts["mismatches"] += 1
        final_step = (projection.get("steps") or [{}])[-1]
        witness = final_step.get("witness") or {}
        binding = final_step.get("header_binding") or {}
        mismatches.append(
            {
                "source": source,
                "attempt_key": projection.get("attempt_key"),
                "operation": external.get("operation"),
                "planned_final_request_id": external.get("planned_final_request_id"),
                "actual_last_request_id": external.get("actual_last_request_id"),
                "actual_step_count": external.get("actual_step_count"),
                "planned_step_count": external.get("planned_step_count"),
                "final_planned_step_observed": external.get("final_planned_step_observed"),
                "final_planned_step_ambiguous": external.get("final_planned_step_ambiguous"),
                "final_step_completed": external.get("final_step_completed"),
                "dispatch_state": dispatch_state,
                "comparison_step_is_planned_final": external.get("comparison_step_is_planned_final"),
                "client_status": external.get("client_status"),
                "source_final_step_status": final_step.get("status"),
                "transport_error": external.get("transport_error"),
                "client_error": external.get("client_error"),
                "started_ns": external.get("started_ns"),
                "ended_ns": external.get("ended_ns"),
                "deadline_ns": external.get("deadline_ns"),
                "external_timely": external.get("external_timely"),
                "source_projection_timely": projection.get("timely"),
                "captured_body_sha256": captured_sha,
                "captured_body_bytes": body_evidence.get("bytes"),
                "captured_body_reason": body_evidence.get("reason"),
                "external_body_sha256": external_sha,
                "external_body_bytes": external.get("external_body_bytes"),
                "witness_raw_file": witness.get("raw_file"),
                "witness_trace_id": witness.get("trace_id"),
                "witness_span_id": witness.get("span_id"),
                "header_span_id": binding.get("header_span_id"),
                "source_local_parent_path": binding.get("source_local_parent_path"),
            }
        )
    return {
        "counts": dict(sorted(counts.items())),
        "comparison_strata": [
            {"dispatch_state": state, "result": result, "count": count}
            for (state, result), count in sorted(strata.items())
        ],
        "mismatches": mismatches,
    }


def audit_campaign(campaign: Path) -> dict[str, Any]:
    campaign = Path(campaign)
    qualification_path = campaign / "qualification.json"
    qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="otel-v3-fidelity-") as temporary:
        database = sqlite3.connect(Path(temporary) / "external.sqlite")
        try:
            external_records = _index_external(campaign / "external.json", database)
            sources = {
                source: _source_audit(
                    campaign / "projections" / f"{source}-final.json", source, database
                )
                for source in ("ebpf", "native")
            }
        finally:
            database.close()
    saved = qualification.get("independent_body_fidelity", {})
    reproduced = all(
        sources[source]["counts"].get("compared", 0) == saved.get(source, {}).get("compared")
        and sources[source]["counts"].get("exact_body_matches", 0)
        == saved.get(source, {}).get("exact_body_matches")
        and sources[source]["counts"].get("mismatches", 0) == saved.get(source, {}).get("mismatches")
        for source in ("ebpf", "native")
    )
    return {
        "schema_version": 1,
        "method": "otel-v3-saved-projection-body-fidelity-audit",
        "campaign": campaign.name,
        "external_records": external_records,
        "sources": sources,
        "saved_independent_body_fidelity": saved,
        "reproduces_saved_qualification_counts": reproduced,
        "qualification_json_sha256": hashlib.sha256(qualification_path.read_bytes()).hexdigest(),
        "fitting_performed": False,
        "oracle_fields_consumed": False,
        "comparison_note": (
            "Counts first reproduce the original final-actual-step body hash comparison. "
            "Dispatch/completion strata are descriptive and do not filter mismatches or assert semantics."
        ),
    }


def audit_qualifications(inputs: Path) -> dict[str, Any]:
    campaigns = []
    for status in sorted(Path(inputs).rglob("status.json")):
        value = json.loads(status.read_text(encoding="utf-8"))
        if value.get("system") == "otel_demo" and value.get("qualification") is True:
            campaigns.append(audit_campaign(status.parent))
    if not campaigns:
        raise ValueError("no OTel v3 qualification artifact found")
    return {"schema_version": 1, "campaigns": campaigns}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit_qualifications(args.inputs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
