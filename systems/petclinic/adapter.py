"""Two-guest Spring Petclinic Microservices adapter for the eBPF study.

Application downloads, builds, deployment, and traffic are deliberately guarded to
GitHub Actions.  The adapter emits deployment and native-telemetry provenance, but
never an expected dependency graph or synthetic observation records.
"""

from __future__ import annotations

import ast
import base64
import copy
import hashlib
import io
import json
import os
import re
import shlex
import time
from pathlib import Path
from typing import Any

import requests
import yaml

SOURCE_REPOSITORY = "https://github.com/spring-petclinic/spring-petclinic-microservices.git"
SOURCE_COMMIT = "3858f9c630cf989bb6809a86edf47c2be78dc9f1"
JAVA_IMAGE = "eclipse-temurin:17-jre@sha256:13cc28a6cc72a38ce1f00c906be3580c1a3e604b8984d694f369a96742abc93b"
MYSQL_IMAGE = "mysql:8.4@sha256:b3b90af2a6552ae30c266fdb7d5dd55f3afb72404bb78d37fe8a23eb857fd3fb"
HAPROXY_IMAGE = "haproxy:3.0-alpine@sha256:34cc7d1f6142464d7d2b73e2a1eef7392556dbf304160aef543e513cfd9e5162"
COLLECTOR_IMAGE = "ghcr.io/open-telemetry/opentelemetry-collector-releases/opentelemetry-collector-contrib:0.159.0@sha256:1f2c54a30e713fac6b3ae77a1ec84010c2007e29ced8ec666214fc2f6739c1cc"
AGENT_URL = "https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v2.31.1/opentelemetry-javaagent.jar"
AGENT_SHA256 = "bbf83c151b6400709e2f225bdd07a04f839d9d13b8b93464241333fd25d3e3ba"
IMAGE_TAG = f"petclinic-ebpf-study:{SOURCE_COMMIT[:12]}"
QUALIFIED_IMAGE_ID = "sha256:48a71a0f944e3cda4fcf445a66371d0f76240a6b2603fc2d1c7395779cb71a0d"
REMOTE_DIR = "/opt/ebpf-study/petclinic"
OPERATIONS = ("list_owners", "owner_details_with_visits", "create_visit", "list_vets")
IPS = {
    "gateway": "172.28.11.10",
    "customers": "172.28.11.11",
    "vets": "172.28.11.12",
    "visits_proxy": "172.28.11.13",
    "visits_a": "172.28.11.14",
    "database": "172.28.11.20",
    "collector_a": "172.28.11.30",
    "visits_b": "172.28.12.14",
    "collector_b": "172.28.12.30",
}


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_actions() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Petclinic application builds, deployments, and requests run only in GitHub Actions")


def _fixture_from_source(source: Path) -> dict[str, Any]:
    """Derive immutable response oracles from pinned upstream SQL, not live replies."""
    tables: dict[str, list[tuple[Any, ...]]] = {}
    hashes: dict[str, str] = {}
    for service in ("customers", "visits", "vets"):
        path = source / f"spring-petclinic-{service}-service/src/main/resources/db/mysql/data.sql"
        hashes[path.relative_to(source).as_posix()] = _sha256(path)
        for table, fields in re.findall(r"INSERT IGNORE INTO (\w+) VALUES \((.*?)\);", path.read_text(encoding="utf-8")):
            tables.setdefault(table, []).append(ast.literal_eval("(" + fields + ",)"))
    types = {row[0]: {"id": row[0], "name": row[1]} for row in tables["types"]}
    owners = []
    for owner in tables["owners"]:
        item = dict(zip(("id", "firstName", "lastName", "address", "city", "telephone"), owner))
        item["pets"] = [
            {"id": pid, "name": name, "birthDate": date, "type": types[kind]}
            for pid, name, date, kind, owner_id in tables["pets"]
            if owner_id == item["id"]
        ]
        owners.append(item)
    details = copy.deepcopy(next(row for row in owners if row["id"] == 6))
    for pet in details["pets"]:
        pet["type"] = {"name": pet["type"]["name"]}  # pinned gateway DTO drops the type ID
        pet["visits"] = [
            {"id": vid, "petId": pet_id, "date": date, "description": description}
            for vid, pet_id, date, description in tables["visits"]
            if pet_id == pet["id"]
        ]
    specialties = {row[0]: {"id": row[0], "name": row[1]} for row in tables["specialties"]}
    vets = [
        {
            "id": vid,
            "firstName": first,
            "lastName": last,
            "specialties": [specialties[sid] for vet_id, sid in tables["vet_specialties"] if vet_id == vid],
        }
        for vid, first, last in tables["vets"]
    ]
    if len(details["pets"]) != 2 or sum(len(pet["visits"]) for pet in details["pets"]) != 4:
        raise RuntimeError("Pinned owner-details fixture no longer has the qualified visit census")
    return {"owners": owners, "details": details, "vets": vets, "seed_sha256": hashes}


def _canonical(actual: Any, expected: Any, key: str = "") -> Any:
    """Compare every seed-derived semantic field, allowing extra response metadata."""
    if key in {"birthDate", "date"} and isinstance(actual, str) and isinstance(expected, str):
        actual, expected = actual[:10], expected[:10]
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or not set(expected).issubset(actual):
            raise ValueError("missing_object_fields")
        return {name: _canonical(actual[name], value, name) for name, value in expected.items()}
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValueError("incomplete_or_duplicate_list")
        if expected and all(isinstance(row, dict) and "id" in row for row in expected):
            ids = [row.get("id") for row in actual if isinstance(row, dict)]
            if len(ids) != len(actual) or len(set(ids)) != len(ids):
                raise ValueError("duplicate_or_invalid_entity_id")
            by_id = {row["id"]: row for row in actual}
            return [_canonical(by_id[row["id"]], row) for row in expected]
        return [_canonical(a, e) for a, e in zip(actual, expected)]
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError("semantic_value_mismatch")
    return actual


def _native_service_census(raw: Any) -> dict[str, Any]:
    """Count service-owned spans in collector JSONL without interpreting topology."""
    services: dict[str, int] = {}
    spans = 0
    valid_records = 0
    malformed_records = 0
    lines = io.BytesIO(raw) if isinstance(raw, bytes) else raw
    for line in lines:
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            malformed_records += 1
            continue
        valid_records += 1
        resource_spans = record.get("resourceSpans", record.get("resource_spans", [])) if isinstance(record, dict) else []
        for resource_span in resource_spans if isinstance(resource_spans, list) else []:
            resource = resource_span.get("resource", {}) if isinstance(resource_span, dict) else {}
            service = ""
            for attribute in resource.get("attributes", []) if isinstance(resource, dict) else []:
                if not isinstance(attribute, dict) or attribute.get("key") != "service.name":
                    continue
                value = attribute.get("value", {})
                if isinstance(value, dict):
                    service = str(value.get("stringValue", value.get("string_value", "")))
            scope_spans = resource_span.get("scopeSpans", resource_span.get("scope_spans", []))
            count = sum(len(scope.get("spans", [])) for scope in scope_spans if isinstance(scope, dict)) if isinstance(scope_spans, list) else 0
            spans += count
            if service and count:
                services[service] = services.get(service, 0) + count
    return {
        "spans": spans,
        "services": dict(sorted(services.items())),
        "valid_records": valid_records,
        "malformed_records": malformed_records,
    }


def _native_mode_compliance(mode: str, census: dict[str, Any]) -> dict[str, Any]:
    """Audit actual span evidence while leaving unavailable evidence explicitly unknown."""
    observed = set(census["services"])
    expected_instrumented = {
        "partial": {"api-gateway", "customers-service", "vets-service"},
        "full": {"api-gateway", "customers-service", "vets-service", "visits-service"},
    }
    if census["malformed_records"]:
        return {"compliant": None, "reason": "malformed_native_records", "observed_services": sorted(observed)}
    if census.get("source_files_present", 0) < census.get("source_files_expected", 0):
        return {
            "compliant": None,
            "reason": "native_export_file_unavailable",
            "source_files_present": census.get("source_files_present", 0),
            "source_files_expected": census.get("source_files_expected", 0),
            "observed_services": sorted(observed),
        }
    if mode == "absent":
        compliant = census["spans"] == 0
        return {
            "compliant": compliant,
            "reason": "no_application_spans" if compliant else "native_spans_present_while_absent",
            "observed_services": sorted(observed),
        }
    if mode == "partial" and "visits-service" in observed:
        return {"compliant": False, "reason": "controlled_visits_native_spans_present", "observed_services": sorted(observed)}
    missing = expected_instrumented[mode] - observed
    if missing:
        return {
            "compliant": None,
            "reason": "required_native_service_evidence_unavailable",
            "missing_services": sorted(missing),
            "observed_services": sorted(observed),
        }
    return {"compliant": True, "reason": "service_mode_matches_actual_spans", "observed_services": sorted(observed)}


class Adapter:
    """Deploy and drive the pinned Petclinic services on two independent guests."""

    def __init__(self, context: Any):
        self.ctx = context
        self.assets = Path(context.deployment_dir) / "petclinic"
        self.fixture: dict[str, Any] | None = None
        self._source_mode = "unprepared"
        self._image_id: str | None = None
        self._current_state = "11"

    def _run(self, argv: list[str], *, cwd: Path | None = None, timeout: int = 1800):
        return self.ctx.run(argv, cwd=cwd, timeout=timeout)

    def _node(self, node: str, command: str, timeout: int = 300, check: bool = True):
        return self.ctx.node_exec(node, command, timeout=timeout, check=check)

    @staticmethod
    def _compose(node: str, arguments: str) -> str:
        return f"docker compose -p petclinic-{node} -f {REMOTE_DIR}/node-{node}/compose.yml {arguments}"

    def prepare(self) -> None:
        _require_actions()
        self.assets.mkdir(parents=True, exist_ok=True)
        source = self.assets / "source"
        archive_override = os.environ.get("PETCLINIC_IMAGE_ARCHIVE", "").strip()
        if not source.exists():
            self._run(["git", "clone", "--filter=blob:none", SOURCE_REPOSITORY, str(source)], timeout=600)
        self._run(["git", "fetch", "--depth=1", "origin", SOURCE_COMMIT], cwd=source, timeout=600)
        self._run(["git", "checkout", "--detach", SOURCE_COMMIT], cwd=source)
        head = self._run(["git", "rev-parse", "HEAD"], cwd=source)
        if getattr(head, "stdout", "").strip() != SOURCE_COMMIT:
            raise RuntimeError("Petclinic source checkout does not match the pinned commit")

        self.fixture = _fixture_from_source(source)
        _json_write(self.assets / "fixture.json", self.fixture)
        image_archive = self.assets / "petclinic-image.tar"
        build_context = self.assets / "image-context"
        build_context.mkdir(exist_ok=True)
        if archive_override:
            override = Path(archive_override)
            if not override.is_file():
                raise RuntimeError("PETCLINIC_IMAGE_ARCHIVE was specified but is not a file")
            self._run(["cp", str(override), str(image_archive)])
            loaded = self._run(["docker", "load", "-i", str(image_archive)], timeout=900)
            self._run(["docker", "tag", f"petclinic-study:{SOURCE_COMMIT[:12]}", IMAGE_TAG])
            self._source_mode = "qualified_archive_override"
        else:
            # The historic qualified Actions artifact may expire and its API download requires
            # credentials. Public reproduction therefore rebuilds the same pinned source and
            # dependency inputs, and records that this is not the byte-identical old image.
            agent = build_context / "opentelemetry-javaagent.jar"
            self._run(["curl", "--fail", "--location", "--retry", "3", "-o", str(agent), AGENT_URL], timeout=300)
            if _sha256(agent) != AGENT_SHA256:
                raise RuntimeError("OpenTelemetry Java agent digest mismatch")
            self._run(
                ["mvn", "-B", "-ntp", "-DskipTests", "-pl",
                 "spring-petclinic-customers-service,spring-petclinic-visits-service,spring-petclinic-vets-service,spring-petclinic-api-gateway",
                 "-am", "package"],
                cwd=source,
                timeout=1800,
            )
            for module in ("customers-service", "visits-service", "vets-service", "api-gateway"):
                jar = source / f"spring-petclinic-{module}/target/spring-petclinic-{module}-4.0.1.jar"
                if not jar.is_file():
                    raise RuntimeError(f"Expected pinned build output is absent: {jar.name}")
                self._run(["cp", str(jar), str(build_context / f"{module}.jar")])
            (build_context / "Dockerfile").write_text(
                f"FROM {JAVA_IMAGE}\nWORKDIR /app\nCOPY *.jar opentelemetry-javaagent.jar /app/\n",
                encoding="utf-8",
            )
            self._run(["docker", "build", "--platform", "linux/amd64", "-t", IMAGE_TAG, str(build_context)], timeout=1800)
            self._run(["docker", "save", "-o", str(image_archive), IMAGE_TAG], timeout=900)
            loaded = None
            self._source_mode = "rebuild_from_pinned_source"

        inspect = self._run(["docker", "image", "inspect", IMAGE_TAG, "--format", "{{.Id}}"])
        self._image_id = getattr(inspect, "stdout", "").strip()
        if not self._image_id:
            detail = getattr(loaded, "stdout", "") if loaded is not None else ""
            raise RuntimeError(f"Prepared archive did not provide required image tag {IMAGE_TAG}: {detail}")
        if archive_override and self._image_id != QUALIFIED_IMAGE_ID:
            raise RuntimeError("Archive override is not the previously qualified Petclinic image ID")
        self._write_deployment_assets()
        _json_write(
            self.assets / "source-image-provenance.json",
            {
                "source_repository": SOURCE_REPOSITORY,
                "source_commit": SOURCE_COMMIT,
                "image_tag": IMAGE_TAG,
                "image_id": self._image_id,
                "image_archive_sha256": _sha256(image_archive),
                "preparation": self._source_mode,
                "historic_qualified_artifact": {
                    "artifact_id": 10045092166,
                    "expired_artifact_fallback": "rebuild_from_pinned_source",
                    "byte_identity_claimed": self._source_mode == "qualified_archive_override",
                },
                "java_agent": {"url": AGENT_URL, "sha256": AGENT_SHA256},
                "runtime_images": {"java": JAVA_IMAGE, "mysql": MYSQL_IMAGE, "haproxy": HAPROXY_IMAGE, "collector": COLLECTOR_IMAGE},
            },
        )

    def _spring_environment(
        self,
        service: str,
        instance: str,
        collector_ip: str,
        instrumented: bool,
        database_endpoint: str | None = None,
    ) -> dict[str, str]:
        database_endpoint = database_endpoint or f"{IPS['database']}:3306"
        props: dict[str, Any] = {
            "server.port": 8080,
            "spring.cloud.config.enabled": False,
            "eureka.client.enabled": False,
            "spring.sql.init.mode": "never",
            "spring.jpa.hibernate.ddl-auto": "none",
            "spring.jpa.open-in-view": False,
            "management.tracing.export.enabled": False,
            "management.tracing.export.zipkin.enabled": False,
            "spring.autoconfigure.exclude": [
                "org.springframework.boot.micrometer.tracing.brave.autoconfigure.BraveAutoConfiguration",
                "org.springframework.boot.micrometer.tracing.autoconfigure.MicrometerTracingAutoConfiguration",
            ],
            "management.endpoints.web.exposure.include": "health,info",
            "spring.datasource.url": f"jdbc:mysql://{database_endpoint}/petclinic?allowPublicKeyRetrieval=true&useSSL=false",
            "spring.datasource.username": "root",
            "spring.datasource.password": "petclinic-study",
            "spring.datasource.driver-class-name": "com.mysql.cj.jdbc.Driver",
            "spring.datasource.hikari.maximum-pool-size": 5,
            "spring.datasource.hikari.minimum-idle": 1,
        }
        if service == "api-gateway":
            props.update({
                "spring.cloud.discovery.client.simple.instances.customers-service[0].uri": f"http://{IPS['customers']}:8080",
                "spring.cloud.discovery.client.simple.instances.visits-service[0].uri": f"http://{IPS['visits_proxy']}:8080",
                "spring.cloud.discovery.client.simple.instances.vets-service[0].uri": f"http://{IPS['vets']}:8080",
                "spring.cloud.gateway.server.webflux.default-filters": [
                    {"name": "Retry", "args": {"retries": 1, "statuses": "SERVICE_UNAVAILABLE", "methods": "POST"}}
                ],
                "spring.cloud.gateway.server.webflux.routes": [
                    {"id": target, "uri": f"lb://{target}-service", "predicates": [f"Path=/api/{prefix}/**"],
                     "filters": ["StripPrefix=2", {"name": "CircuitBreaker", "args": {"name": f"{target}CircuitBreaker", "fallbackUri": "forward:/fallback"}}]}
                    for target, prefix in (("vets", "vet"), ("visits", "visit"), ("customers", "customer"))
                ],
            })
        env = {
            "SPRING_APPLICATION_JSON": json.dumps(props, separators=(",", ":")),
            "OTEL_SERVICE_NAME": service,
            "OTEL_RESOURCE_ATTRIBUTES": f"service.instance.id={instance}",
            "OTEL_EXPORTER_OTLP_ENDPOINT": f"http://{collector_ip}:4318",
            "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
            "OTEL_TRACES_SAMPLER": "always_on",
            "OTEL_INSTRUMENTATION_HTTP_SERVER_CAPTURE_REQUEST_HEADERS": "x-experiment-request-id",
            "OTEL_METRICS_EXPORTER": "none",
            "OTEL_LOGS_EXPORTER": "none",
            "OTEL_SDK_DISABLED": "false" if instrumented else "true",
        }
        return env

    def _application_service(
        self,
        service: str,
        instance: str,
        ip: str,
        collector: str,
        instrumented: bool,
        database_endpoint: str | None = None,
    ) -> dict[str, Any]:
        java = ["java", "-Xms64m", "-Xmx320m", "-XX:MaxMetaspaceSize=192m"]
        if instrumented:
            java.append("-javaagent:/app/opentelemetry-javaagent.jar")
        java += ["-jar", f"/app/{service}.jar"]
        return {
            "image": IMAGE_TAG,
            "command": java,
            "environment": self._spring_environment(service, instance, collector, instrumented, database_endpoint),
            "restart": "unless-stopped",
            "networks": {"application": {"ipv4_address": ip}},
            "extra_hosts": [
                f"database:{(database_endpoint or IPS['database'] + ':3306').rsplit(':', 1)[0]}", f"customers-service:{IPS['customers']}",
                f"vets-service:{IPS['vets']}", f"visits-service:{IPS['visits_proxy']}",
            ],
            "mem_limit": "768m",
        }

    def _write_deployment_assets(self) -> None:
        mode = self.ctx.mode
        if mode not in {"absent", "partial", "full"}:
            raise ValueError(f"Unsupported tracing mode: {mode}")
        for node in ("a", "b"):
            directory = self.assets / f"node-{node}"
            (directory / "native").mkdir(parents=True, exist_ok=True)
            collector = {
                "receivers": {"otlp": {"protocols": {"http": {"endpoint": "0.0.0.0:4318"}}}},
                "processors": {"batch": {"timeout": "1s"}},
                "exporters": {"file": {"path": "/output/native.jsonl", "format": "json"}},
                "service": {"pipelines": {"traces": {"receivers": ["otlp"], "processors": ["batch"], "exporters": ["file"]}}},
            }
            (directory / "collector.yml").write_text(yaml.safe_dump(collector, sort_keys=False), encoding="utf-8")

        guest_a = self.ctx.node_ip("a")
        guest_b = self.ctx.node_ip("b")
        (self.assets / "node-a" / "haproxy.cfg").write_text(
            f"""global
  maxconn 1024
defaults
  mode http
  timeout connect 500ms
  timeout client 3s
  timeout server 3s
  retries 0
frontend visits
  bind *:8080
  default_backend visits_replicas
backend visits_replicas
  balance roundrobin
  option http-server-close
  option redispatch
  server visits_a {IPS['visits_a']}:8080 check inter 500ms fall 1 rise 1
  server visits_b {guest_b}:18081 check inter 500ms fall 1 rise 1
""",
            encoding="utf-8",
        )

        sql_dir = self.assets / "node-a" / "sql"
        sql_dir.mkdir(exist_ok=True)
        source = self.assets / "source"
        sequence = 0
        for service in ("customers", "visits", "vets"):
            for kind in ("schema", "data"):
                origin = source / f"spring-petclinic-{service}-service/src/main/resources/db/mysql/{kind}.sql"
                target = sql_dir / f"{sequence:02d}-{service}-{kind}.sql"
                target.write_bytes(origin.read_bytes())
                sequence += 1

        instrument = {
            "gateway": mode in {"partial", "full"},
            "customers": mode in {"partial", "full"},
            "vets": mode in {"partial", "full"},
            "visits_a": mode == "full",
            "visits_b": mode == "full",
        }
        common_network_a = {"application": {"name": "petclinic-a-application", "ipam": {"config": [{"subnet": "172.28.11.0/24"}]}}}
        services_a: dict[str, Any] = {
            "database": {
                "image": MYSQL_IMAGE,
                "environment": {"MYSQL_ROOT_PASSWORD": "petclinic-study", "MYSQL_ROOT_HOST": "%", "MYSQL_DATABASE": "petclinic"},
                "command": ["--innodb-buffer-pool-size=128M", "--max-connections=64"],
                "restart": "unless-stopped",
                "networks": {"application": {"ipv4_address": IPS["database"]}},
                "ports": [f"{guest_a}:13306:3306"],
                "volumes": [f"{REMOTE_DIR}/node-a/sql:/docker-entrypoint-initdb.d:ro"],
                "healthcheck": {"test": ["CMD-SHELL", "MYSQL_PWD=petclinic-study mysqladmin ping -h 127.0.0.1 -uroot --silent"], "interval": "2s", "timeout": "2s", "retries": 60},
                "mem_limit": "768m",
            },
            "collector-a": {
                "image": COLLECTOR_IMAGE,
                "command": ["--config=/etc/study/collector.yml"], "user": "0:0",
                "networks": {"application": {"ipv4_address": IPS["collector_a"]}},
                "volumes": [f"{REMOTE_DIR}/node-a/collector.yml:/etc/study/collector.yml:ro", f"{REMOTE_DIR}/node-a/native:/output"],
            },
            "customers": self._application_service("customers-service", "customers-a", IPS["customers"], IPS["collector_a"], instrument["customers"]),
            "vets": self._application_service("vets-service", "vets-a", IPS["vets"], IPS["collector_a"], instrument["vets"]),
            "visits-a": self._application_service("visits-service", "visits-a", IPS["visits_a"], IPS["collector_a"], instrument["visits_a"]),
            "visits-proxy": {
                "image": HAPROXY_IMAGE,
                "networks": {"application": {"ipv4_address": IPS["visits_proxy"]}},
                "volumes": [f"{REMOTE_DIR}/node-a/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro"],
                "restart": "unless-stopped",
            },
            "gateway": self._application_service("api-gateway", "gateway-a", IPS["gateway"], IPS["collector_a"], instrument["gateway"]),
        }
        services_a["gateway"]["ports"] = ["0.0.0.0:18080:8080"]
        services_a["visits-a"]["ports"] = [f"{guest_a}:18081:8080"]
        compose_a = {"name": "petclinic-a", "services": services_a, "networks": common_network_a}

        compose_b = {
            "name": "petclinic-b",
            "services": {
                "collector-b": {
                    "image": COLLECTOR_IMAGE, "command": ["--config=/etc/study/collector.yml"], "user": "0:0",
                    "networks": {"application": {"ipv4_address": IPS["collector_b"]}},
                    "volumes": [f"{REMOTE_DIR}/node-b/collector.yml:/etc/study/collector.yml:ro", f"{REMOTE_DIR}/node-b/native:/output"],
                },
                "visits-b": self._application_service(
                    "visits-service",
                    "visits-b",
                    IPS["visits_b"],
                    IPS["collector_b"],
                    instrument["visits_b"],
                    f"{guest_a}:13306",
                ),
            },
            "networks": {"application": {"name": "petclinic-b-application", "ipam": {"config": [{"subnet": "172.28.12.0/24"}]}}},
        }
        compose_b["services"]["visits-b"]["ports"] = [f"{guest_b}:18081:8080"]
        for node, compose in (("a", compose_a), ("b", compose_b)):
            path = self.assets / f"node-{node}" / "compose.yml"
            path.write_text(yaml.safe_dump(compose, sort_keys=False), encoding="utf-8")
            _json_write(self.assets / f"node-{node}" / "resolved-compose.json", compose)
        _json_write(
            self.assets / "placement.json",
            {
                "nodes": {"a": {"guest_ip": self.ctx.node_ip("a"), "subnet": "172.28.11.0/24"}, "b": {"guest_ip": self.ctx.node_ip("b"), "subnet": "172.28.12.0/24"}},
                "containers": {name: {"node": "b" if name.endswith("_b") else "a", "ip": ip} for name, ip in IPS.items()},
                "proxy": {
                    "name": "visits-proxy",
                    "ip": IPS["visits_proxy"],
                    "policy": "roundrobin",
                    "backends": [f"{IPS['visits_a']}:8080", f"{guest_b}:18081"],
                    "visits_b_container_ip": IPS["visits_b"],
                },
                "native_instrumentation": instrument,
            },
        )

    def deploy(self) -> None:
        _require_actions()
        if not (self.assets / "petclinic-image.tar").is_file():
            raise RuntimeError("prepare() must complete before deploy()")
        for node in ("a", "b"):
            self._node(node, f"sudo mkdir -p {REMOTE_DIR} && sudo chown -R $(id -u):$(id -g) {REMOTE_DIR}")
            self.ctx.node_put(node, self.assets / f"node-{node}", f"{REMOTE_DIR}/node-{node}")
            self.ctx.node_put(node, self.assets / "petclinic-image.tar", f"{REMOTE_DIR}/petclinic-image.tar")
            self._node(node, f"docker load -i {REMOTE_DIR}/petclinic-image.tar", timeout=900)
        self._node("a", self._compose("a", "up -d database collector-a"), timeout=600)
        self._wait_database(180)
        self._wait_tcp("b", self.ctx.node_ip("a"), 13306, 60, "node-a published MySQL")
        self._node("a", self._compose("a", "up -d customers vets visits-a visits-proxy gateway"), timeout=600)
        self._node("b", self._compose("b", "up -d"), timeout=600)
        self._current_state = "11"

    def _wait_database(self, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        command = self._compose("a", "exec -T -e MYSQL_PWD=petclinic-study database mysqladmin ping -h 127.0.0.1 -uroot --silent")
        last = ""
        while time.monotonic() < deadline:
            try:
                result = self._node("a", command, timeout=15)
                if result.returncode == 0:
                    return
            except Exception as exc:  # noqa: BLE001 - context defines its remote exception type
                last = str(exc)
            time.sleep(2)
        raise RuntimeError(f"Petclinic database unavailable after {timeout:.0f}s: {last}")

    def ready(self) -> None:
        _require_actions()
        self.fixture = self.fixture or json.loads((self.assets / "fixture.json").read_text(encoding="utf-8"))
        self._wait_replica_ports({"a": IPS["visits_a"], "b": IPS["visits_b"]}, 180)
        deadline = time.monotonic() + 420
        last: list[dict[str, Any]] = []
        while time.monotonic() < deadline:
            last = [self.operation(name, index=-1, namespace="readiness", deadline=5.0) for name in ("list_owners", "owner_details_with_visits", "list_vets")]
            if all(row["success"] is True for row in last):
                return
            time.sleep(5)
        raise RuntimeError("Petclinic failed seed-derived readiness contracts: " + json.dumps(last))

    def metadata(self) -> dict[str, Any]:
        provenance_path = self.assets / "source-image-provenance.json"
        provenance = json.loads(provenance_path.read_text(encoding="utf-8")) if provenance_path.is_file() else {}
        mode = self.ctx.mode
        return {
            "system": "petclinic",
            "operations": list(OPERATIONS),
            "entry_url": f"http://{self.ctx.node_ip('a')}:18080",
            "replicas": [
                {
                    "name": "visits-a",
                    "node": "a",
                    "ip": IPS["visits_a"],
                    "transport_host": self.ctx.node_ip("a"),
                    "transport_port": 18081,
                },
                {
                    "name": "visits-b",
                    "node": "b",
                    "ip": IPS["visits_b"],
                    "transport_host": self.ctx.node_ip("b"),
                    "transport_port": 18081,
                },
            ],
            "database": {
                "logical_identity": "petclinic-mysql",
                "node": "a",
                "container": "database",
                "ip": IPS["database"],
                "cross_guest_endpoint": f"{self.ctx.node_ip('a')}:13306",
                "observed_aliases": ["database", IPS["database"], self.ctx.node_ip("a")],
                "published_port": 13306,
                "container_port": 3306,
            },
            "proxy_discovery": {
                "node": "a",
                "container": "visits-proxy",
                "ip": IPS["visits_proxy"],
                "policy": "roundrobin",
                "static_backends": [f"{IPS['visits_a']}:8080", f"{self.ctx.node_ip('b')}:18081"],
                "visits_b_container": {"ip": IPS["visits_b"], "published_endpoint": f"{self.ctx.node_ip('b')}:18081"},
                "cross_guest_transport": "stable_guest_published_port",
            },
            "source": provenance,
            "placement_file": str(self.assets / "placement.json"),
            "native": {
                "mode": mode,
                "export_locations": {"a": f"{REMOTE_DIR}/node-a/native/native.jsonl", "b": f"{REMOTE_DIR}/node-b/native/native.jsonl"},
                "suppression": {
                    "absent": "No application starts with -javaagent; OTEL_SDK_DISABLED=true everywhere.",
                    "partial": "Gateway/customers/vets use the agent; both controlled Visits replicas omit -javaagent and set OTEL_SDK_DISABLED=true.",
                    "full": "All five application processes use the pinned Java agent and always_on sampling.",
                }[mode],
                "micrometer_export_disabled": True,
            },
        }

    def reset(self) -> None:
        _require_actions()
        self.set_database(True)
        self.set_replicas("11")
        sql = "DELETE FROM visits WHERE description LIKE 'ebpf-study-%'"
        self._mysql(sql)
        self.ready()

    def set_replicas(self, state: str) -> None:
        _require_actions()
        if state not in {"11", "10", "01", "00"}:
            raise ValueError("Replica state must be one of 11, 10, 01, 00")
        for node, service, desired in (("a", "visits-a", state[0] == "1"), ("b", "visits-b", state[1] == "1")):
            verb = "start" if desired else "stop"
            self._node(node, self._compose(node, f"{verb} {service}"), timeout=120)
        self._current_state = state
        wanted = {}
        if state[0] == "1":
            wanted["a"] = IPS["visits_a"]
        if state[1] == "1":
            wanted["b"] = IPS["visits_b"]
        self._wait_replica_ports(wanted, 180)
        time.sleep(2)

    def _wait_replica_ports(self, replicas: dict[str, str], timeout: float) -> None:
        pending = dict(replicas)
        errors: dict[str, str] = {}
        deadline = time.monotonic() + timeout
        while pending and time.monotonic() < deadline:
            for node, ip in list(pending.items()):
                try:
                    self._node(node, f"timeout 2 bash -c '</dev/tcp/{ip}/8080'", timeout=5)
                    del pending[node]
                except Exception as exc:  # noqa: BLE001 - context defines its remote exception type
                    errors[node] = str(exc)
            if pending:
                time.sleep(2)
        if pending:
            raise RuntimeError(f"Visits replicas did not open port 8080: {pending}; last errors: {errors}")
        if "b" in replicas:
            self._wait_tcp("a", self.ctx.node_ip("b"), 18081, timeout, "node-b published Visits")

    def _wait_tcp(self, node: str, address: str, port: int, timeout: float, label: str) -> None:
        deadline = time.monotonic() + timeout
        last_error = ""
        while time.monotonic() < deadline:
            probe = self._node(node, f"timeout 2 bash -c '</dev/tcp/{address}/{port}'", timeout=5, check=False)
            if probe.returncode == 0:
                return
            last_error = getattr(probe, "stderr", "")
            time.sleep(2)
        raise RuntimeError(f"{label} did not open {address}:{port}: {last_error}")

    def set_database(self, up: bool) -> None:
        _require_actions()
        self._node("a", self._compose("a", ("start" if up else "stop") + " database"), timeout=180)
        if up:
            self._wait_database(180)
        time.sleep(2)

    def operation(self, name: str, index: int, namespace: str, deadline: float = 2.0) -> dict[str, Any]:
        _require_actions()
        if name not in OPERATIONS:
            raise ValueError(f"Unknown Petclinic operation: {name}")
        self.fixture = self.fixture or json.loads((self.assets / "fixture.json").read_text(encoding="utf-8"))
        attempt_id = f"{namespace}-{index}-{name}"
        digest = hashlib.sha256(attempt_id.encode()).hexdigest()
        request_id = "req-" + hashlib.sha256(("http-step:" + attempt_id).encode()).hexdigest()
        marker = "ebpf-study-" + digest
        method = "GET"
        paths = {"list_owners": "/api/customer/owners", "owner_details_with_visits": "/api/gateway/owners/6", "create_visit": "/api/visit/owners/1/pets/1/visits", "list_vets": "/api/vet/vets"}
        body: dict[str, Any] | None = None
        if name == "create_visit":
            method, body = "POST", {"date": "2026-09-01", "description": marker}
        url = f"http://{self.ctx.node_ip('a')}:18080{paths[name]}"
        started_ns = time.time_ns()
        response = None
        payload = None
        raw = b""
        error = None
        try:
            response = requests.request(
                method,
                url,
                json=body,
                headers={
                    "X-Experiment-Request-Id": request_id,
                    "Connection": "close",
                },
                timeout=deadline,
            )
            raw = response.content[: 1024 * 1024 + 1]
            if len(raw) > 1024 * 1024:
                raise ValueError("response_exceeds_declared_limit")
            payload = response.json()
        except (requests.exceptions.RequestException, ValueError) as exc:
            error = f"{type(exc).__name__}: {exc}"
        ended_ns = time.time_ns()
        timely = ended_ns - started_ns <= int(deadline * 1_000_000_000)
        status = response.status_code if response is not None else None
        success: bool | None = False
        validation: dict[str, Any] = {"kind": "payload", "valid": False}
        if name == "create_visit":
            success = None if status == 201 and error is None and timely else False
            validation = {"kind": "sql_exact_row", "state": "pending" if success is None else "http_failed", "marker": marker}
        elif status == 200 and error is None and timely:
            fixture_key = {"list_owners": "owners", "owner_details_with_visits": "details", "list_vets": "vets"}[name]
            try:
                _canonical(payload, self.fixture[fixture_key])
                success = True
                validation = {"kind": "payload", "valid": True, "fixture": fixture_key}
            except (ValueError, KeyError, TypeError) as exc:
                error = f"semantic_validation: {exc}"
        if not timely and error is None:
            error = "whole_operation_deadline_exceeded"
        return {
            "operation": name,
            "attempt_id": attempt_id,
            "started_ns": started_ns,
            "ended_ns": ended_ns,
            "deadline_seconds": deadline,
            "success": success,
            "http_steps": [{
                "method": method, "url": url, "request_json": body, "status": status,
                "request_id": request_id,
                "started_ns": started_ns, "ended_ns": ended_ns,
                "response_body_base64": base64.b64encode(raw).decode(),
                "response_content_type": response.headers.get("content-type") if response is not None else None,
            }],
            "error": error,
            "validation": validation,
            "response_json": payload,
        }

    def _mysql(self, sql: str):
        encoded = base64.b64encode(sql.encode()).decode()
        script = f"echo {shlex.quote(encoded)} | base64 -d | docker compose -p petclinic-a -f {REMOTE_DIR}/node-a/compose.yml exec -T -e MYSQL_PWD=petclinic-study database mysql -uroot --batch --skip-column-names petclinic"
        return self._node("a", script, timeout=60)

    def verify(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        _require_actions()
        verified = copy.deepcopy(records)
        candidates: list[tuple[dict[str, Any], str]] = []
        for row in verified:
            if row.get("operation") != "create_visit":
                continue
            marker = row.get("validation", {}).get("marker", "")
            if not re.fullmatch(r"ebpf-study-[0-9a-f]{64}", marker):
                row["success"] = False
                row["error"] = "invalid_or_missing_write_marker"
                continue
            candidates.append((row, marker))
        if not candidates:
            return verified
        markers = sorted({marker for _, marker in candidates})
        grouped: dict[str, list[dict[str, Any]]] = {marker: [] for marker in markers}
        oracle_errors: dict[str, dict[str, Any]] = {}
        for offset in range(0, len(markers), 100):
            chunk = markers[offset:offset + 100]
            quoted = ",".join(f"'{marker}'" for marker in chunk)
            sql = (
                "SELECT description,id,pet_id,DATE_FORMAT(visit_date,'%Y-%m-%d') FROM visits "
                f"WHERE description IN ({quoted}) ORDER BY description,id"
            )
            try:
                result = self._mysql(sql)
            except Exception as exc:  # noqa: BLE001 - unavailable remote SQL is an explicit unknown oracle
                for marker in chunk:
                    oracle_errors[marker] = {"error": str(exc)}
                continue
            parse_errors: list[str] = []
            for line in getattr(result, "stdout", "").splitlines():
                fields = line.split("\t")
                if len(fields) != 4 or fields[0] not in grouped or fields[0] not in chunk:
                    parse_errors.append(line)
                    continue
                try:
                    grouped[fields[0]].append({
                        "id": int(fields[1]), "petId": int(fields[2]),
                        "date": fields[3], "description": fields[0],
                    })
                except ValueError:
                    parse_errors.append(line)
            if parse_errors:
                for marker in chunk:
                    oracle_errors[marker] = {
                        "error": "sql_census_parse_error",
                        "malformed_rows": parse_errors,
                    }
        for row, marker in candidates:
            if marker in oracle_errors:
                row["success"] = None if row.get("success") is None else row.get("success")
                row["validation"] = {
                    "kind": "sql_exact_row", "state": "oracle_unavailable",
                    "marker": marker, **oracle_errors[marker],
                }
                continue
            db_rows = grouped[marker]
            payload = row.get("response_json")
            acknowledged_id = payload.get("id") if isinstance(payload, dict) else None
            response_identity_match = (
                isinstance(payload, dict)
                and type(acknowledged_id) is int
                and acknowledged_id > 0
                and payload.get("petId") == 1
                and isinstance(payload.get("date"), str)
                and payload["date"][:10] == "2026-09-01"
                and payload.get("description") == marker
            )
            exact = response_identity_match and len(db_rows) == 1 and db_rows[0] == {
                "id": acknowledged_id, "petId": 1, "date": "2026-09-01", "description": marker,
            }
            elapsed_ns = row["ended_ns"] - row["started_ns"]
            deadline_ns = int(row.get("deadline_seconds", 2.0) * 1_000_000_000)
            http_created = row["http_steps"][0].get("status") == 201 and row.get("error") is None and elapsed_ns <= deadline_ns
            row["success"] = bool(http_created and exact)
            row["validation"] = {
                "kind": "sql_exact_row", "state": "verified", "marker": marker,
                "row_count": len(db_rows), "rows": db_rows, "acknowledged_id": acknowledged_id,
                "response_identity_match": response_identity_match,
                "exactly_once_and_identity_match": exact,
            }
            if not row["success"] and not row.get("error"):
                row["error"] = "write_not_persisted_exactly_once_with_acknowledged_identity"
        return verified

    def collect_native(self, destination: Path) -> None:
        _require_actions()
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        inventory: dict[str, Any] = {
            "mode": self.ctx.mode,
            "files": {},
            "suppression_verified": {},
            "snapshot_method": "graceful_stop_rotate_copy_restart_new_segment",
        }
        for node in ("a", "b"):
            collector = f"collector-{node}"
            # Compose stop waits for the collector's SIGTERM handling, including exporter flush.
            self._node(node, self._compose(node, f"stop -t 30 {collector}"), timeout=60)
            remote = f"{REMOTE_DIR}/node-{node}/native/native.jsonl"
            target = destination / f"native-node-{node}.jsonl"
            archived = f"{remote}.snapshot-{time.time_ns()}"
            try:
                exists = self._node(node, f"test -f {remote}", timeout=30, check=False)
                if exists.returncode == 0:
                    # Rotate only after the collector has flushed and stopped. Its file
                    # exporter starts a fresh segment rather than appending on restart.
                    self._node(node, f"mv {remote} {archived}", timeout=30)
                if exists.returncode == 0 and hasattr(self.ctx, "node_get"):
                    self.ctx.node_get(node, archived, target)
                elif exists.returncode == 0:
                    result = self._node(node, f"base64 -w0 {archived}", timeout=120)
                    target.write_bytes(base64.b64decode(getattr(result, "stdout", "").strip()))
                else:
                    target.write_bytes(b"")
                with target.open("rb") as stream:
                    census = _native_service_census(stream)
                census["source_files_present"] = int(exists.returncode == 0)
                census["source_files_expected"] = 1
                inventory["files"][node] = {
                    "path": target.name,
                    "bytes": target.stat().st_size,
                    "sha256": _sha256(target),
                    "guest_rotated_file": archived,
                    "census": census,
                    "mode_compliance": _native_mode_compliance(self.ctx.mode, census),
                }
                inspect = self._node(node, self._compose(node, "ps -q --all") + " | xargs -r docker inspect --format '{{.Name}} {{json .Config.Cmd}} {{json .Config.Env}}'", timeout=60)
                inventory["suppression_verified"][node] = getattr(inspect, "stdout", "").splitlines()
            finally:
                self._resume_native_collector(node, collector, remote, inventory)
        combined = {
            "spans": 0,
            "services": {},
            "valid_records": 0,
            "malformed_records": 0,
            "source_files_present": 0,
            "source_files_expected": 2,
        }
        for file_metadata in inventory["files"].values():
            census = file_metadata["census"]
            combined["spans"] += census["spans"]
            combined["valid_records"] += census["valid_records"]
            combined["malformed_records"] += census["malformed_records"]
            combined["source_files_present"] += census["source_files_present"]
            for service, count in census["services"].items():
                combined["services"][service] = combined["services"].get(service, 0) + count
        combined["services"] = dict(sorted(combined["services"].items()))
        inventory["actual_census"] = combined
        inventory["mode_compliance"] = _native_mode_compliance(self.ctx.mode, combined)
        _json_write(destination / "native-metadata.json", inventory)

    def _resume_native_collector(self, node: str, collector: str, remote: str, inventory: dict[str, Any]) -> None:
        """Resume a snapshot-stopped collector on a fresh segment and prove readiness."""
        self._node(node, self._compose(node, f"start {collector}"), timeout=60)
        collector_ip = IPS[f"collector_{node}"]
        deadline = time.monotonic() + 60
        last_error = ""
        while time.monotonic() < deadline:
            probe = self._node(node, f"timeout 2 bash -c '</dev/tcp/{collector_ip}/4318'", timeout=5, check=False)
            if probe.returncode == 0:
                break
            last_error = getattr(probe, "stderr", "")
            time.sleep(1)
        else:
            raise RuntimeError(f"Native collector {node} did not resume OTLP reception: {last_error}")
        size_result = self._node(node, f"if test -f {remote}; then stat -c %s {remote}; else echo 0; fi", timeout=30)
        resumed_size = int(getattr(size_result, "stdout", "0").strip())
        file_metadata = inventory.setdefault("files", {}).setdefault(node, {})
        file_metadata["next_segment_initial_bytes"] = resumed_size
        file_metadata["collector_resumed"] = True

    def close(self) -> None:
        diagnostics = Path(self.ctx.out) / "petclinic-diagnostics"
        diagnostics.mkdir(parents=True, exist_ok=True)
        for node in ("a", "b"):
            try:
                logs = self._node(node, self._compose(node, "logs --no-color --timestamps"), timeout=180)
                (diagnostics / f"node-{node}.log").write_text(getattr(logs, "stdout", ""), encoding="utf-8")
                state = self._node(node, self._compose(node, "ps --all --format json"), timeout=60)
                (diagnostics / f"node-{node}-containers.jsonl").write_text(getattr(state, "stdout", ""), encoding="utf-8")
                network = self._node(
                    node,
                    "ip -4 route; sudo iptables -S FORWARD; sudo iptables -S DOCKER-USER; docker network inspect petclinic-"
                    f"{node}-application",
                    timeout=60,
                    check=False,
                )
                (diagnostics / f"node-{node}-network.txt").write_text(
                    getattr(network, "stdout", "") + getattr(network, "stderr", ""),
                    encoding="utf-8",
                )
            except Exception as exc:  # noqa: BLE001 - best-effort diagnostics must not skip teardown
                (diagnostics / f"node-{node}-diagnostic-error.txt").write_text(str(exc), encoding="utf-8")
            finally:
                try:
                    self._node(node, self._compose(node, "down --remove-orphans"), timeout=300)
                except Exception as exc:  # noqa: BLE001 - retain each independent teardown failure
                    (diagnostics / f"node-{node}-close-error.txt").write_text(str(exc), encoding="utf-8")
