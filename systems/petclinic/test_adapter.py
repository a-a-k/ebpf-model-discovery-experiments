import importlib.util
import sys
from types import SimpleNamespace

import pytest

if importlib.util.find_spec("requests") is None:  # keep the static local check independent of app tooling
    sys.modules["requests"] = SimpleNamespace()

from systems.petclinic.adapter import Adapter, _canonical


def test_canonical_rejects_missing_owner_visits():
    expected = {"id": 6, "pets": [{"id": 7, "visits": [{"id": 1}, {"id": 2}]}]}
    actual = {"id": 6, "pets": [{"id": 7, "visits": [{"id": 1}]}]}
    with pytest.raises(ValueError, match="incomplete_or_duplicate_list"):
        _canonical(actual, expected)


def test_canonical_accepts_timestamp_date_and_extra_fields():
    assert _canonical({"id": 1, "date": "2026-09-01T00:00:00Z", "extra": True}, {"id": 1, "date": "2026-09-01"})


def test_metadata_records_split_replicas_and_suppression(tmp_path):
    context = SimpleNamespace(
        deployment_dir=tmp_path, out=tmp_path, mode="partial",
        node_ip=lambda node: {"a": "192.168.76.11", "b": "192.168.76.12"}[node],
    )
    metadata = Adapter(context).metadata()
    assert [row["node"] for row in metadata["replicas"]] == ["a", "b"]
    assert "both controlled Visits replicas" in metadata["native"]["suppression"]
    assert metadata["proxy_discovery"]["policy"] == "roundrobin"


def test_verify_rejects_duplicate_exact_visit_rows(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    context = SimpleNamespace(deployment_dir=tmp_path, out=tmp_path, mode="full")
    adapter = Adapter(context)
    marker = "ebpf-study-" + "a" * 64
    adapter._mysql = lambda _sql: SimpleNamespace(
        stdout=f"42\t1\t2026-09-01\t{marker}\n43\t1\t2026-09-01\t{marker}\n"
    )
    record = {
        "operation": "create_visit",
        "success": None,
        "error": None,
        "started_ns": 0,
        "ended_ns": 1,
        "deadline_seconds": 2.0,
        "http_steps": [{"status": 201}],
        "response_json": {"id": 42, "petId": 1, "date": "2026-09-01", "description": marker},
        "validation": {"marker": marker},
    }
    verified = adapter.verify([record])[0]
    assert verified["success"] is False
    assert verified["validation"]["row_count"] == 2
