from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from ebpf_discovery.transport_v4 import Journal


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate-journal-memory-v5.py"
SPEC = importlib.util.spec_from_file_location("validate_journal_memory_v5", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def _pair(journal: Journal, transport: str, request: str, **terminal) -> None:
    journal.append("step_started", transport_id=transport, request_id=request,
                   method="GET", body="request body")
    journal.append("step_finished", transport_id=transport, request_id=request,
                   response_body_base64="AA==", **terminal)


def test_separate_workers_emit_identical_full_transport_bytes(tmp_path: Path) -> None:
    journal = Journal(tmp_path / "attempt-journal.sqlite")
    _pair(journal, "one", "request-one", status_code=200)
    _pair(journal, "duplicate-a", "duplicate", status_code=200)
    _pair(journal, "duplicate-b", "duplicate", status_code=503)
    journal.close()
    original_source = Path(__file__).parent / "fixtures/journal_identity_v5_before.py"

    original = VALIDATOR._run_worker(
        SCRIPT, "original", tmp_path / "attempt-journal.sqlite", original_source,
        tmp_path / "original")
    current = VALIDATOR._run_worker(
        SCRIPT, "current", tmp_path / "attempt-journal.sqlite", original_source,
        tmp_path / "current")
    comparison = VALIDATOR._compare(
        tmp_path / "original", tmp_path / "current", original, current)

    assert comparison["requests"] == 2
    assert comparison["none_transports"] == 1
    assert comparison["all_per_request_canonical_bytes_identical"] is True
    values = [json.loads(line) for line in
              (tmp_path / "current/transports/canonical-transports.jsonl")
              .read_text(encoding="utf-8").splitlines()]
    value = next(row["transport"] for row in values
                 if row["request_id"] == "request-one")
    assert value["terminal"]["data"]["response_body_base64"] == "AA=="
    assert value["terminal"]["data_json"]


def test_canonical_request_order_handles_null_and_unicode(tmp_path: Path) -> None:
    output = tmp_path / "transport"
    report = VALIDATOR._emit_transports(
        output, {"Ответ": {"value": 1}, None: None, "a": {"value": 2}})
    assert report["requests"] == 3
    assert report["none_transports"] == 1
    assert [row["request_id"] for row in report["rows"]] == ["a", "Ответ", None]
    assert (output / "canonical-transports.jsonl").is_file()
