"""Iteration-4 DeathStarBench operation and source-audited call declarations.

This module does not add topology to a discovered graph. Call declarations must
be resolved against observed Bering edges before constructing a predicate.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
import time
from typing import Any

import requests
import yaml

from .adapter import Adapter as HistoricalAdapter
from .adapter import (
    AdapterError, CROSS_NODE_PORTS, DB_CONTAINER, DB_SERVICE,
    REPLICA_CONTAINERS, REPLICA_IPS, _json_dump,
)
from .contracts_v3 import STABLE_FIXTURE_TEXT


ENTRY_SERVICES = ["nginx-thrift", "nginx-web-server"]
# Source-audited native nginx spans omit span.kind; this declaration only binds
# request observations. The original kind remains unchanged in Bering input.
UNTYPED_ENTRY_COMPONENTS = {"native": ["nginx"]}
CONTROLLED_SERVICE_ALIASES = ["user-timeline-service"]
SELECTED_DATABASE = {
    "db_system": "mongodb",
    "db_role": "user-timeline",
    "logical_identity": DB_SERVICE,
    "container": DB_CONTAINER,
}


def entry_identity_groups(deployment_dir: str | Path) -> list[dict[str, Any]]:
    """Prove two entry telemetry names from this retained rendered deployment.

    This does not rename observed nodes or supply a graph edge. Missing or
    changed rendered files yield no identity equivalence.
    """
    root = Path(deployment_dir).resolve()
    node = root / 'deathstarbench' / 'node-a'
    compose_path = node / 'docker-compose.yml'
    config_path = node / 'nginx-web-server' / 'jaeger-config.json'
    nginx_path = node / 'nginx-web-server' / 'conf' / 'nginx.conf'
    files = (compose_path, config_path, nginx_path)
    if any(not path.is_file() or not path.resolve().is_relative_to(root) for path in files):
        return []
    try:
        raw = {path: path.read_bytes() for path in files}
        compose = yaml.safe_load(raw[compose_path].decode('utf-8'))
        config = json.loads(raw[config_path].decode('utf-8'))
        lines = raw[nginx_path].decode('utf-8').splitlines()
    except (OSError, UnicodeError, ValueError, yaml.YAMLError):
        return []
    if not isinstance(compose, dict) or not isinstance(compose.get('services'), dict):
        return []
    service = compose['services'].get('nginx-thrift')
    if not isinstance(service, dict) or not isinstance(config, dict):
        return []
    if (service.get('hostname') != 'nginx-thrift'
            or service.get('container_name') != 'dsb-nginx-thrift'
            or service.get('ports') != ['8080:8080']
            or config.get('service_name') != 'nginx-web-server'):
        return []
    volumes = service.get('volumes')
    if not isinstance(volumes, list) or not all(isinstance(value, str) for value in volumes):
        return []
    mounts = (
        ('./nginx-web-server/conf/nginx.conf', '/usr/local/openresty/nginx/conf/nginx.conf'),
        ('./nginx-web-server/jaeger-config.json', '/usr/local/openresty/nginx/jaeger-config.json'),
    )
    mount_indices = []
    for source, target in mounts:
        matches = [index for index, value in enumerate(volumes)
                   if len(value.split(':')) >= 2 and value.split(':')[1] == target]
        if len(matches) != 1 or volumes[matches[0]] != f'{source}:{target}':
            return []
        mount_indices.append(matches[0])
    loader = ('opentracing_load_tracer /usr/local/lib/libjaegertracing_plugin.so '
              '/usr/local/openresty/nginx/jaeger-config.json;')
    loaders = [(index + 1, line.strip()) for index, line in enumerate(lines)
               if line.strip().startswith('opentracing_load_tracer ')]
    if len(loaders) != 1 or loaders[0][1] != loader:
        return []

    digests = {path: hashlib.sha256(raw[path]).hexdigest() for path in files}
    def proof(path: Path, pointer: str, value: Any) -> dict[str, Any]:
        return {'relative_path': path.relative_to(root).as_posix(),
                'sha256': digests[path], 'pointer': pointer, 'observed_value': value}

    return [{
        'aliases': ['nginx-thrift', 'nginx-web-server'],
        'scope': 'entry representation only; same declared container/listener; entry fixed fulfilled',
        'proof': [
            proof(compose_path, '/services/nginx-thrift/hostname', 'nginx-thrift'),
            proof(compose_path, '/services/nginx-thrift/container_name', 'dsb-nginx-thrift'),
            proof(compose_path, '/services/nginx-thrift/ports/0', '8080:8080'),
            proof(compose_path, f'/services/nginx-thrift/volumes/{mount_indices[0]}', volumes[mount_indices[0]]),
            proof(compose_path, f'/services/nginx-thrift/volumes/{mount_indices[1]}', volumes[mount_indices[1]]),
            proof(nginx_path, f'line:{loaders[0][0]}', loader),
            proof(config_path, '/service_name', 'nginx-web-server'),
        ],
    }]

_NGINX = ENTRY_SERVICES
_COMPOSE = ["compose-post-service"]
_USER = ["user-timeline-service"]
_HOME = ["home-timeline-service"]
_POST = ["post-storage-service"]
_REQUEST_PATHS = {
    "compose_post": "/wrk2-api/post/compose",
    "read_home_timeline": "/wrk2-api/home-timeline/read?user_id=3&start=0&stop=10",
    "read_user_timeline": "/wrk2-api/user-timeline/read?user_id=2&start=0&stop=10",
}

CONTRACTS: dict[str, dict[str, Any]] = {
    "compose_post": {
        "steps": [{"method": "POST", "path": "/wrk2-api/post/compose"}],
        "entry_services": ENTRY_SERVICES,
        "required_calls": [
            {"caller": _NGINX, "callee": _COMPOSE},
            {"caller": _COMPOSE, "callee": ["text-service"]},
            {"caller": _COMPOSE, "callee": ["user-service"]},
            {"caller": _COMPOSE, "callee": ["media-service"]},
            {"caller": _COMPOSE, "callee": ["unique-id-service"]},
            {"caller": _COMPOSE, "callee": _POST},
            {"caller": _COMPOSE, "callee": _USER},
            {"caller": _COMPOSE, "callee": _HOME},
            {"caller": _USER, "db_system": "mongodb", "db_role": "user-timeline"},
            {"caller": _USER, "db_system": "redis", "db_role": "user-timeline"},
            {"caller": _HOME, "callee": ["social-graph-service"]},
            {"caller": _HOME, "db_system": "redis", "db_role": "home-timeline"},
        ],
        "conditional_db": [],
    },
    "read_home_timeline": {
        "steps": [{"method": "GET", "path": "/wrk2-api/home-timeline/read"}],
        "entry_services": ENTRY_SERVICES,
        "required_calls": [
            {"caller": _NGINX, "callee": _HOME},
            {"caller": _HOME, "db_system": "redis", "db_role": "home-timeline"},
            {"caller": _HOME, "callee": _POST},
        ],
        "conditional_db": [],
    },
    "read_user_timeline": {
        "steps": [{"method": "GET", "path": "/wrk2-api/user-timeline/read"}],
        "entry_services": ENTRY_SERVICES,
        "required_calls": [
            {"caller": _NGINX, "callee": _USER},
            {"caller": _USER, "db_system": "redis", "db_role": "user-timeline"},
            {"caller": _USER, "callee": _POST},
        ],
        "conditional_db": [
            {"caller": _USER, "db_system": "mongodb", "db_role": "user-timeline",
             "when": "Redis returns fewer than stop-start post IDs"},
        ],
    },
}


class Adapter(HistoricalAdapter):
    """V4 behavior; historical adapter and its v3 deadline semantics are intact."""

    def _render(self) -> None:
        super()._render()
        configuration = self.node_dirs["a"] / "haproxy.cfg"
        source = configuration.read_text(encoding="utf-8")
        old = "  timeout connect 2s\n  timeout client 15s\n  timeout server 15s\n"
        if source.count(old) != 1:
            raise RuntimeError("unexpected injected HAProxy timeout configuration")
        configuration.write_text(source.replace(old, "", 1), encoding="utf-8")

    def _verify_each_replica_serves(self) -> None:
        """Technical readiness probe; never call the scored v4 operation here."""
        evidence = []
        path = "/wrk2-api/user-timeline/read?user_id=2&start=0&stop=10"
        for selected, other in (("a", "b"), ("b", "a")):
            self.ctx.node_exec(other, f"docker stop {REPLICA_CONTAINERS[other]}", timeout=120)
            try:
                until = time.monotonic() + 20
                attempts = []
                while time.monotonic() < until:
                    try:
                        response = requests.get(self.entry_url + path, timeout=5)
                        body = response.content
                        matched = response.ok and self._valid_timeline(body, STABLE_FIXTURE_TEXT)
                        attempts.append({
                            "status": response.status_code,
                            "body_sha256": hashlib.sha256(body).hexdigest(),
                            "matched": matched,
                        })
                        if matched:
                            break
                    except requests.RequestException as exc:
                        attempts.append({"error": str(exc), "matched": False})
                    time.sleep(1)
                else:
                    raise AdapterError(f"user-timeline replica {selected} did not serve the semantic readiness probe")
                evidence.append({
                    "selected_replica": selected,
                    "other_replica_stopped": other,
                    "attempts": attempts,
                    "success": True,
                    "purpose": "technical_readiness_only",
                })
            finally:
                self.ctx.node_exec(other, f"docker start {REPLICA_CONTAINERS[other]}", timeout=120)
        listener_until = time.monotonic() + 30
        while time.monotonic() < listener_until:
            checks = (
                self.ctx.node_exec("a", f"timeout 1 bash -c '</dev/tcp/127.0.0.1/{CROSS_NODE_PORTS['user-timeline-replica']}'", check=False),
                self.ctx.node_exec("b", f"timeout 1 bash -c '</dev/tcp/127.0.0.1/{CROSS_NODE_PORTS['user-timeline-replica']}'", check=False),
            )
            if all(check.returncode == 0 for check in checks):
                break
            time.sleep(1)
        else:
            raise AdapterError("both user-timeline replica listeners were not restored after readiness probes")
        _json_dump(self.root / "replica-readiness.json", evidence)

    @staticmethod
    def plan_operation(name: str, index: int, namespace: str) -> dict[str, Any]:
        if name not in CONTRACTS:
            raise ValueError(f"unknown DeathStarBench operation: {name}")
        attempt_id = f"{namespace}-{name}-{index:08d}"
        request_id = "req-" + hashlib.sha256(attempt_id.encode("utf-8")).hexdigest()
        declared = CONTRACTS[name]["steps"]
        return {
            "attempt_id": attempt_id,
            "operation": name,
            "http_steps": [{"request_id": request_id, **item, "path": _REQUEST_PATHS[name]} for item in declared],
        }

    def operation(self, name: str, index: int, namespace: str, deadline: float | None = None) -> dict[str, Any]:
        if deadline is not None:
            raise ValueError("v4 operations have no experiment-imposed deadline")
        from ebpf_discovery.transport_v4 import request as observed_request

        plan = self.plan_operation(name, index, namespace)
        planned_step = plan["http_steps"][0]
        request_id = planned_step["request_id"]
        path = planned_step["path"]
        method = planned_step["method"]
        marker = f"ebpf-study {request_id}"
        data = None
        if name == "compose_post":
            data = {
                "username": "username_0", "user_id": "0", "text": marker,
                "media_ids": '["123456789012345678"]' if index % 2 else "[]",
                "media_types": '["png"]' if index % 2 else "[]", "post_type": "0",
            }
        step: dict[str, Any] = {
            **planned_step,
            "url": self.entry_url + path,
            "request_form": data,
            "request_headers": {"X-Experiment-Request-Id": request_id},
        }
        started_ns = time.time_ns()
        started_mono = time.monotonic_ns()
        success: bool | None = None
        reason = ""
        try:
            response = observed_request(
                method, step["url"], journal=self.ctx.journal, data=data,
                headers=step["request_headers"], timeout=None,
            )
            body = response.content
            step.update(
                status=response.status_code,
                response_body_base64=base64.b64encode(body).decode("ascii"),
                response_sha256=hashlib.sha256(body).hexdigest(),
                body_completed_ns=getattr(response, "_study_body_completed_ns", time.time_ns()),
            )
            if name == "compose_post":
                success = response.ok and b"Successfully upload post" in body
                reason = "" if success else "missing exact compose acknowledgement"
            else:
                success = response.ok and self._valid_timeline(body, STABLE_FIXTURE_TEXT)
                reason = "" if success else "stable fixture or timeline shape absent"
            if not response.ok:
                reason = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            reason = f"incomplete HTTP transport: {exc}"
            step["transport_error"] = reason
        ended_ns = time.time_ns()
        step.update(started_ns=started_ns, ended_ns=ended_ns, elapsed_ns=time.monotonic_ns() - started_mono)
        return {
            "operation": name, "attempt_id": plan["attempt_id"],
            "started_ns": started_ns, "ended_ns": ended_ns,
            "success": success, "http_steps": [step], "error": reason,
            "validation": {
                "kind": "exact_http_content_oracle",
                "compose_marker_sha256": hashlib.sha256(marker.encode()).hexdigest() if name == "compose_post" else None,
                "control_epoch": self._control_epoch,
                "replica_state": self._replica_state,
                "database_up": self._database_up,
            },
        }

    def verify(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """One complete probe per compose postcondition, with no time gate."""
        from ebpf_discovery.transport_v4 import request as observed_request

        verified = copy.deepcopy(records)
        locations = {
            "user_timeline_owner": "/wrk2-api/user-timeline/read?user_id=0&start=0&stop=1000",
            "home_timeline_follower": "/wrk2-api/home-timeline/read?user_id=1&start=0&stop=1000",
        }
        for record in verified:
            if record.get("operation") != "compose_post" or record.get("success") is not True:
                continue
            if record.get("validation", {}).get("control_epoch") != self._control_epoch:
                record["eventual_postcondition"] = {
                    "kind": "compose_eventual_fanout", "success": None,
                    "unknown_reason": "control state changed before verification",
                }
                continue
            request_id = record["http_steps"][0]["request_id"]
            expected = f"ebpf-study {request_id}"
            evidence = {}
            for label, path in locations.items():
                probe_id = "verify-" + hashlib.sha256(f"{request_id}:{label}".encode()).hexdigest()
                try:
                    response = observed_request(
                        "GET", self.entry_url + path, journal=self.ctx.journal,
                        headers={"X-Experiment-Request-Id": probe_id}, timeout=None,
                    )
                    body = response.content
                    found = response.ok and self._valid_timeline(body, expected)
                    evidence[label] = {
                        "request_id": probe_id, "status": response.status_code,
                        "body_sha256": hashlib.sha256(body).hexdigest(), "found": found,
                    }
                except requests.RequestException as exc:
                    evidence[label] = {"request_id": probe_id, "found": None, "error": str(exc)}
            states = [item["found"] for item in evidence.values()]
            # A bounded first page can omit an older acknowledged post. Only
            # exact positive witnesses establish this auxiliary postcondition.
            success = True if all(state is True for state in states) else None
            record["eventual_postcondition"] = {
                "kind": "compose_eventual_fanout",
                "expected_text_sha256": hashlib.sha256(expected.encode()).hexdigest(),
                "locations": evidence, "success": success,
                "unknown_reason": (
                    "incomplete verification transport" if None in states else
                    "bounded_page_no_witness" if success is None else None
                ),
                "control_epoch": self._control_epoch,
            }
        return verified

    def selected_inventory(self) -> dict[str, Any]:
        """Explicit deployment facts, separate from recovered topology."""
        return {
            "controlled_service_aliases": CONTROLLED_SERVICE_ALIASES,
            "replicas": [
                {"container": REPLICA_CONTAINERS[node], "controlled_replica": node,
                 "guest": node, "ip": REPLICA_IPS[node], "port": 9090}
                for node in ("a", "b")
            ],
            "selected_database": {**SELECTED_DATABASE, "guest": "a", "port": 27017},
        }
