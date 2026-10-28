from __future__ import annotations

import sys
import types

import requests

from .adapter import Adapter as HistoricalAdapter
from .experiment_v4 import Adapter, CONTRACTS
from .contracts_v3 import STABLE_FIXTURE_TEXT


class _Context:
    mode = "absent"
    deployment_dir = "/unused"
    journal = object()

    @staticmethod
    def node_ip(node):
        assert node == "a"
        return "127.0.0.1"


def _response(code: int, body: bytes) -> requests.Response:
    result = requests.Response()
    result.status_code = code
    result._content = body
    return result


def _transport(monkeypatch, reply):
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setitem(sys.modules, "ebpf_discovery.transport_v4", types.SimpleNamespace(request=request))
    return calls


def test_predeclared_ids_match_uncapped_issued_requests(monkeypatch):
    adapter = Adapter(_Context())
    for operation, path, body in (
        ("compose_post", "/wrk2-api/post/compose", b"Successfully upload post"),
        ("read_home_timeline", "/wrk2-api/home-timeline/read?user_id=3&start=0&stop=10", ('[{"post_id":"1","text":"' + STABLE_FIXTURE_TEXT + '"}]').encode()),
        ("read_user_timeline", "/wrk2-api/user-timeline/read?user_id=2&start=0&stop=10", ('[{"post_id":"1","text":"' + STABLE_FIXTURE_TEXT + '"}]').encode()),
    ):
        calls = _transport(monkeypatch, _response(200, body))
        plan = adapter.plan_operation(operation, 7, "fixed")
        result = adapter.operation(operation, 7, "fixed")
        assert result["success"] is True
        assert result["attempt_id"] == plan["attempt_id"]
        assert result["http_steps"][0]["request_id"] == plan["http_steps"][0]["request_id"]
        assert calls[0][0] == plan["http_steps"][0]["method"]
        assert calls[0][1] == "http://127.0.0.1:8080" + path
        assert calls[0][2]["headers"]["X-Experiment-Request-Id"] == plan["http_steps"][0]["request_id"]
        assert calls[0][2]["timeout"] is None
        assert calls[0][2]["journal"] is adapter.ctx.journal
        assert "deadline_seconds" not in result["http_steps"][0]
        assert "observation" not in result


def test_completed_mismatch_false_and_incomplete_transport_unknown(monkeypatch):
    adapter = Adapter(_Context())
    _transport(monkeypatch, _response(500, b"error"))
    complete = adapter.operation("compose_post", 1, "fixed")
    assert complete["success"] is False
    assert complete["http_steps"][0]["status"] == 500

    _transport(monkeypatch, requests.ConnectionError("connection closed"))
    incomplete = adapter.operation("compose_post", 2, "fixed")
    assert incomplete["success"] is None
    assert "status" not in incomplete["http_steps"][0]
    assert "transport_error" in incomplete["http_steps"][0]


def test_later_verification_has_no_deadline_and_cannot_change_primary(monkeypatch):
    adapter = Adapter(_Context())
    plan = adapter.plan_operation("compose_post", 4, "fixed")
    result = {
        "operation": "compose_post", "success": True,
        "http_steps": plan["http_steps"],
        "validation": {"control_epoch": 0},
    }
    calls = _transport(monkeypatch, requests.ConnectionError("incomplete"))
    checked = adapter.verify([result])[0]
    assert checked["success"] is True
    assert checked["eventual_postcondition"]["success"] is None
    assert len(calls) == 2
    assert all(call[2]["timeout"] is None for call in calls)


def test_mongo_fallback_is_not_an_unconditional_user_read_call():
    read = CONTRACTS["read_user_timeline"]
    assert not any(item.get("db_system") == "mongodb" for item in read["required_calls"])
    assert read["conditional_db"] == [{
        "caller": ["user-timeline-service"], "db_system": "mongodb",
        "db_role": "user-timeline", "when": "Redis returns fewer than stop-start post IDs",
    }]
    assert any(item.get("db_system") == "mongodb" for item in CONTRACTS["compose_post"]["required_calls"])
    assert not any(item.get("db_system") == "mongodb" for item in CONTRACTS["read_home_timeline"]["required_calls"])


def test_v4_render_removes_only_injected_proxy_limits(monkeypatch, tmp_path):
    adapter = Adapter(_Context())
    adapter.node_dirs["a"] = tmp_path
    config = tmp_path / "haproxy.cfg"
    legacy = (
        "defaults\n  mode tcp\n  timeout connect 2s\n"
        "  timeout client 15s\n  timeout server 15s\n"
        "backend replicas\n  balance roundrobin\n"
    )

    def render(_self):
        config.write_text(legacy, encoding="utf-8")

    monkeypatch.setattr(HistoricalAdapter, "_render", render)
    adapter._render()
    assert config.read_text(encoding="utf-8") == (
        "defaults\n  mode tcp\nbackend replicas\n  balance roundrobin\n"
    )
