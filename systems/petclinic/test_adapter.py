import importlib.util
import json
import sys
from types import SimpleNamespace

import pytest

if importlib.util.find_spec("requests") is None:  # keep the static local check independent of app tooling
    sys.modules["requests"] = SimpleNamespace()

from systems.petclinic import adapter as adapter_module
from systems.petclinic.adapter import (
    Adapter,
    _canonical,
    _native_mode_compliance,
    _native_service_census,
)


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
    assert [(row["transport_host"], row["transport_port"]) for row in metadata["replicas"]] == [
        ("192.168.76.11", 18081),
        ("192.168.76.12", 18081),
    ]
    assert metadata["database"]["observed_aliases"] == ["database", "172.28.11.20", "192.168.76.11"]
    assert metadata["database"]["published_port"] == 13306
    assert "both controlled Visits replicas" in metadata["native"]["suppression"]
    assert metadata["proxy_discovery"]["policy"] == "roundrobin"
    assert metadata["proxy_discovery"]["cross_guest_transport"] == "stable_guest_published_port"


def test_node_b_uses_published_cross_guest_database_endpoint(tmp_path):
    context = SimpleNamespace(deployment_dir=tmp_path, out=tmp_path, mode="absent")
    adapter = Adapter(context)
    environment = adapter._spring_environment(
        "visits-service", "visits-b", "172.28.12.30", False, "192.168.76.11:13306"
    )
    properties = json.loads(environment["SPRING_APPLICATION_JSON"])
    assert properties["spring.datasource.url"].startswith("jdbc:mysql://192.168.76.11:13306/")


def test_verify_rejects_duplicate_exact_visit_rows(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    context = SimpleNamespace(deployment_dir=tmp_path, out=tmp_path, mode="full")
    adapter = Adapter(context)
    marker = "ebpf-study-" + "a" * 64
    adapter._mysql = lambda _sql: SimpleNamespace(
        stdout=f"{marker}\t42\t1\t2026-09-01\n{marker}\t43\t1\t2026-09-01\n"
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


def test_verify_reads_all_create_markers_in_one_sql_census(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    adapter = Adapter(SimpleNamespace(deployment_dir=tmp_path, out=tmp_path, mode="full"))
    markers = ["ebpf-study-" + character * 64 for character in ("a", "b")]
    calls = []

    def mysql(sql):
        calls.append(sql)
        return SimpleNamespace(stdout="".join(f"{marker}\t{index}\t1\t2026-09-01\n" for index, marker in enumerate(markers, 41)))

    adapter._mysql = mysql
    records = [
        {
            "operation": "create_visit", "success": None, "error": None,
            "started_ns": 0, "ended_ns": 1, "deadline_seconds": 2.0,
            "http_steps": [{"status": 201}],
            "response_json": {"id": index, "petId": 1, "date": "2026-09-01", "description": marker},
            "validation": {"marker": marker},
        }
        for index, marker in enumerate(markers, 41)
    ]
    verified = adapter.verify(records)
    assert len(calls) == 1
    assert all(marker in calls[0] for marker in markers)
    assert all(row["success"] is True for row in verified)


def test_verify_chunks_large_marker_census_and_localizes_query_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    adapter = Adapter(SimpleNamespace(deployment_dir=tmp_path, out=tmp_path, mode="full"))
    markers = [f"ebpf-study-{index:064x}" for index in range(205)]
    calls = []

    def mysql(sql):
        calls.append(sql)
        selected = [marker for marker in markers if marker in sql]
        if len(calls) == 2:
            raise RuntimeError("temporary census failure")
        return SimpleNamespace(stdout="".join(
            f"{marker}\t{markers.index(marker) + 1}\t1\t2026-09-01\n" for marker in selected
        ))

    adapter._mysql = mysql
    records = [{
        "operation": "create_visit", "success": None, "error": None,
        "started_ns": 0, "ended_ns": 1, "deadline_seconds": 2.0,
        "http_steps": [{"status": 201}],
        "response_json": {
            "id": index + 1, "petId": 1, "date": "2026-09-01", "description": marker,
        },
        "validation": {"marker": marker},
    } for index, marker in enumerate(markers)]

    verified = adapter.verify(records)
    assert len(calls) == 3
    assert max(sql.count("ebpf-study-") for sql in calls) <= 100
    assert all(row["success"] is True for row in verified[:100])
    assert all(row["success"] is None for row in verified[100:200])
    assert all(row["validation"]["state"] == "oracle_unavailable" for row in verified[100:200])
    assert all(row["success"] is True for row in verified[200:])


def test_operation_uses_only_opaque_binding_header(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    captured = {}

    class Response:
        def __init__(self):
            self.status_code = 200
            self.content = b"[]"
            self.headers = {"content-type": "application/json"}

        @staticmethod
        def json():
            return []

    def request(method, url, **kwargs):
        captured.update(method=method, url=url, **kwargs)
        return Response()

    monkeypatch.setattr(adapter_module.requests, "request", request, raising=False)
    context = SimpleNamespace(
        deployment_dir=tmp_path,
        out=tmp_path,
        mode="absent",
        node_ip=lambda _node: "192.168.76.11",
    )
    adapter = Adapter(context)
    adapter.fixture = {"owners": [], "details": {}, "vets": []}
    record = adapter.operation("list_owners", 3, "calibration")
    request_id = captured["headers"]["X-Experiment-Request-Id"]
    assert request_id.startswith("req-")
    assert "list_owners" not in request_id
    assert "traceparent" not in captured["headers"]
    assert record["http_steps"][0]["request_id"] == request_id
    assert "trace_context" not in record


def test_native_census_and_partial_mode_audit_use_actual_service_names():
    raw = b"\n".join([
        b'{"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"api-gateway"}}]},"scopeSpans":[{"spans":[{},{}]}]}]}',
        b'{"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"customers-service"}}]},"scopeSpans":[{"spans":[{}]}]},{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"vets-service"}}]},"scopeSpans":[{"spans":[{}]}]}]}',
    ])
    census = _native_service_census(raw)
    assert census["spans"] == 4
    assert _native_mode_compliance("partial", census)["compliant"] is True
    census["services"]["visits-service"] = 1
    census["spans"] += 1
    assert _native_mode_compliance("partial", census)["compliant"] is False


def test_native_snapshot_rotates_before_copy_and_accepts_fresh_segment(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    commands = []
    copied_sources = []
    raw = b'{"resourceSpans":[]}\n'

    def node_get(_node, source, destination):
        copied_sources.append(source)
        destination.write_bytes(raw)

    context = SimpleNamespace(deployment_dir=tmp_path, out=tmp_path, mode="partial", node_get=node_get)
    adapter = Adapter(context)

    def node(_node, command, timeout=300, check=True):
        commands.append(command)
        if command.startswith("test -f"):
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if command.startswith("if test -f"):
            return SimpleNamespace(returncode=0, stdout="0\n", stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    adapter._node = node
    destination = tmp_path / "native" / "calibration"
    adapter.collect_native(destination)
    metadata = json.loads((destination / "native-metadata.json").read_text())
    assert metadata["snapshot_method"] == "graceful_stop_rotate_copy_restart_new_segment"
    assert len(copied_sources) == 2
    assert all(".snapshot-" in source for source in copied_sources)
    assert sum(command.startswith("mv ") for command in commands) == 2
    assert all(file["next_segment_initial_bytes"] == 0 for file in metadata["files"].values())
