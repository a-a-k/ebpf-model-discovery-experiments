import base64
import hashlib
import json
from pathlib import Path

from systems.otel_demo.audit_qualification_v3 import audit_campaign


def _record(attempt: str, final: dict | None, *, earlier: bool = False) -> dict:
    steps = []
    if earlier:
        steps.append({
            "request_id": attempt + "-early", "status": 200,
            "response_body_b64": base64.b64encode(b'{"id":"early"}').decode(),
            "error": None,
        })
    if final is not None:
        steps.append({"request_id": attempt + "-final", **final})
    return {
        "attempt_id": attempt,
        "operation": "checkout",
        "started_ns": 1_000_000_000,
        "ended_ns": 2_000_000_000,
        "deadline_seconds": 2.0,
        "request_intent": {"steps": [
            {"ordinal": 0, "request_id": attempt + "-early", "method": "GET", "path": "/early"},
            {"ordinal": 1, "request_id": attempt + "-final", "method": "POST", "path": "/final"},
        ]},
        "http_steps": steps,
    }


def _projection(record: dict, captured: bytes) -> dict:
    key = hashlib.sha256(record["attempt_id"].encode()).hexdigest()
    final_id = record["request_intent"]["steps"][-1]["request_id"]
    return {
        "attempt_key": key,
        "timely": True,
        "steps": [{}, {
            "request_id": final_id,
            "status": 200,
            "witness": {"raw_file": "observations/a.jsonl", "trace_id": "trace", "span_id": "span"},
            "header_binding": {"header_span_id": "header", "source_local_parent_path": ["header", "span"]},
        }],
        "body_evidence": {
            "sha256": hashlib.sha256(captured).hexdigest(),
            "bytes": len(captured),
            "reason": "below_limit_single_document_assumption",
        },
    }


def test_fidelity_keeps_complete_incomplete_and_aborted_mismatches(tmp_path: Path) -> None:
    complete_body = b'{"orderId":"actual"}'
    complete = _record("complete", {
        "status": 200, "response_body_b64": base64.b64encode(complete_body).decode(), "error": None,
    }, earlier=True)
    incomplete = _record("incomplete", {
        "status": None, "response_body_b64": "", "error": "timeout",
    }, earlier=True)
    aborted = _record("aborted", None, earlier=True)
    match = _record("match", {
        "status": 200, "response_body_b64": base64.b64encode(b'{"orderId":"same"}').decode(), "error": None,
    }, earlier=True)
    records = [complete, incomplete, aborted, match]
    projections = [
        _projection(complete, b'{"orderId":"different"}'),
        _projection(incomplete, b'{"orderId":"server-finished"}'),
        _projection(aborted, b'{"orderId":"unattributed"}'),
        _projection(match, b'{"orderId":"same"}'),
    ]
    (tmp_path / "projections").mkdir()
    (tmp_path / "external.json").write_text(json.dumps(records), encoding="utf-8")
    for source in ("ebpf", "native"):
        (tmp_path / "projections" / f"{source}-final.json").write_text(
            json.dumps(projections), encoding="utf-8"
        )
    saved = {source: {"compared": 4, "exact_body_matches": 1, "mismatches": 3}
             for source in ("ebpf", "native")}
    (tmp_path / "qualification.json").write_text(
        json.dumps({"independent_body_fidelity": saved, "raw_bytes": 123}), encoding="utf-8"
    )

    result = audit_campaign(tmp_path)
    assert result["reproduces_saved_qualification_counts"] is True
    mismatches = result["sources"]["ebpf"]["mismatches"]
    assert {row["dispatch_state"] for row in mismatches} == {
        "final_completed", "final_incomplete", "aborted_before_final"
    }
    complete_row = next(row for row in mismatches if row["dispatch_state"] == "final_completed")
    assert complete_row["client_status"] == 200
    assert complete_row["source_final_step_status"] == 200
    assert complete_row["external_body_bytes"] == len(complete_body)
    assert complete_row["source_local_parent_path"] == ["header", "span"]
    incomplete_row = next(row for row in mismatches if row["dispatch_state"] == "final_incomplete")
    assert incomplete_row["external_body_bytes"] == 0
    assert incomplete_row["client_error"] == "timeout"


def test_invalid_external_body_is_not_silently_compared(tmp_path: Path) -> None:
    record = _record("invalid", {
        "status": 200, "response_body_b64": "not-base64", "error": None,
    }, earlier=True)
    projection = _projection(record, b"captured")
    (tmp_path / "projections").mkdir()
    (tmp_path / "external.json").write_text(json.dumps([record]), encoding="utf-8")
    for source in ("ebpf", "native"):
        (tmp_path / "projections" / f"{source}-final.json").write_text(
            json.dumps([projection]), encoding="utf-8"
        )
    saved = {source: {"compared": 0, "exact_body_matches": 0, "mismatches": 0}
             for source in ("ebpf", "native")}
    (tmp_path / "qualification.json").write_text(
        json.dumps({"independent_body_fidelity": saved}), encoding="utf-8"
    )
    result = audit_campaign(tmp_path)
    assert result["sources"]["ebpf"]["counts"]["external_body_unavailable"] == 1
    assert result["sources"]["ebpf"]["mismatches"] == []
