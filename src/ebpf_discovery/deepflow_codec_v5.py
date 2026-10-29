"""Lossless DeepFlow v7.2.3 standalone JSONL codec for iteration 5.

The original flat JSON record remains the authority.  This module emits a
generic OTLP-shaped observation only for unambiguous ``signal_source=EBPF``
records with a supported protocol.  It never creates trace, span, parent,
message, request, or service identities.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Iterable


DEEPFLOW_VERSION = "v7.2.3"
DEEPFLOW_SOURCE_COMMIT = "9a1219fa5cf1471ba2ec8742019661567d98002e"
SUPPORTED_PROTOCOLS = {
    "Http1", "Http2", "Grpc", "MySQL", "PostgreSQL", "Redis", "MongoDB", "Kafka"
}
MAX_OTLP_UNIX_NANO = (1 << 64) - 1
# Pinned v7.2.3 eBPF socket timestamps are kernel monotonic nanoseconds plus
# DeepFlow's periodically refreshed CLOCK_REALTIME-CLOCK_MONOTONIC boot offset.
# Standalone mode disables DeepFlow controller NTP correction.  The serialized
# start_time/end_time fields below are therefore guest-realtime-derived Unix
# epoch microseconds, not host receiver arrival times.
SOURCE_CLOCK = "deepflow_guest_realtime_derived_epoch_us_standalone_ntp_disabled"
_MSG_TYPE_NAMESPACE = "__deepflow_msg_type_source_namespaces"
_MSG_TYPE_NAMESPACE_FIELDS = ("base_head_msg_type", "protocol_info_msg_type")


class _Pairs(list):
    pass


@dataclass(frozen=True)
class RawRecord:
    source_file: str
    retained_file: str
    offset: int
    length: int
    sha256: str
    raw: bytes


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _decode_pairs(value: Any, path: str = "$") -> tuple[Any, list[dict[str, Any]]]:
    """Coalesce identical duplicate keys and report every conflicting variant."""
    if isinstance(value, _Pairs):
        grouped: dict[str, list[Any]] = {}
        conflicts: list[dict[str, Any]] = []
        for key, item in value:
            decoded, nested = _decode_pairs(item, f"{path}.{key}")
            grouped.setdefault(str(key), []).append(decoded)
            conflicts.extend(nested)
        output = {}
        for key, variants in grouped.items():
            unique = {_canonical(item): item for item in variants}
            if len(unique) == 1:
                output[key] = next(iter(unique.values()))
            elif (path == "$" and key == "msg_type" and len(variants) == 2
                  and variants[0] == "Session"
                  and variants[1] in ("Request", "Response")
                  and _MSG_TYPE_NAMESPACE not in grouped
                  and all(field not in grouped for field in _MSG_TYPE_NAMESPACE_FIELDS)):
                # Pinned DeepFlow v7.2.3 flattens AppProtoLogsBaseInfo before
                # protocol-specific L7 info. Both structures serialize a
                # msg_type: the merged base head is Session while HTTP retains
                # its Request/Response phase. This is an ordered source-schema
                # namespace split, not general duplicate-key last-wins.
                output[key] = variants[0]
                output[_MSG_TYPE_NAMESPACE] = {
                    "path": "$.msg_type",
                    "ordered_values": list(variants),
                    "base_head_msg_type": variants[0],
                    "protocol_info_msg_type": variants[1],
                }
            else:
                conflicts.append({
                    "path": f"{path}.{key}",
                    "values": [unique[item] for item in sorted(unique)],
                })
        return output, conflicts
    if isinstance(value, list):
        output, conflicts = [], []
        for index, item in enumerate(value):
            decoded, nested = _decode_pairs(item, f"{path}[{index}]")
            output.append(decoded)
            conflicts.extend(nested)
        return output, conflicts
    return value, []


def _parse(raw: bytes) -> tuple[dict[str, Any] | None, list[dict[str, Any]], str | None]:
    try:
        parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=_Pairs)
        decoded, conflicts = _decode_pairs(parsed)
        if not isinstance(decoded, dict):
            return None, conflicts, "top_level_not_object"
        return decoded, conflicts, None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [], f"invalid_json:{type(exc).__name__}:{exc}"


def complete_records(path: Path, *, source_file: str | None = None,
                     retained_file: str | None = None,
                     limit: int | None = None) -> tuple[list[RawRecord], dict[str, Any]]:
    """Compatibility materializer for small fixtures; acquisition streams below."""
    prefix = {}
    records = list(iter_complete_records(path, prefix, source_file=source_file,
                                        retained_file=retained_file, limit=limit))
    return records, prefix


def iter_complete_records(path: Path, prefix: dict[str, Any], *,
                          source_file: str | None = None,
                          retained_file: str | None = None,
                          limit: int | None = None) -> Iterable[RawRecord]:
    """Read one JSONL record at a time; preserve exact prefix/tail accounting."""
    path = Path(path)
    size = path.stat().st_size
    limit = size if limit is None else limit
    if type(limit) is not int or not 0 <= limit <= size:
        raise ValueError(f"invalid prefix limit {limit} for {path} ({size} bytes)")
    cursor, count, pending = 0, 0, 0
    complete_hash, pending_hash = hashlib.sha256(), hashlib.sha256()
    logical = source_file or path.name
    with path.open("rb") as stream:
        remaining = limit
        while remaining:
            line = stream.readline(remaining)
            if not line:
                raise ValueError(f"retained DeepFlow prefix truncated during read: {path}")
            remaining -= len(line)
            if not line.endswith(b"\n"):
                pending_hash.update(line)
                pending += len(line)
                continue
            content = line[:-1]
            if content.endswith(b"\r"):
                content = content[:-1]
            complete_hash.update(line)
            yield RawRecord(source_file=logical, retained_file=retained_file or str(path),
                            offset=cursor, length=len(content),
                            sha256=hashlib.sha256(content).hexdigest(), raw=content)
            cursor += len(line)
            count += 1
    prefix.update({
        "retained_file": retained_file or str(path),
        "source_file": logical,
        "file_bytes": limit,
        "complete_prefix_bytes": cursor,
        "complete_prefix_sha256": complete_hash.hexdigest(),
        "pending_tail_bytes": pending,
        "pending_tail_sha256": pending_hash.hexdigest(),
        "record_count": count,
    })


def _value(value: Any) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int):
        return {"intValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, list):
        return {"arrayValue": {"values": [_value(item) for item in value]}}
    if isinstance(value, dict):
        return {"kvlistValue": {"values": [
            {"key": str(key), "value": _value(item)} for key, item in sorted(value.items())
        ]}}
    return {"stringValue": str(value)}


def _attr(key: str, value: Any) -> dict[str, Any]:
    return {"key": key, "value": _value(value)}


def _integer(record: dict[str, Any], key: str) -> int | None:
    value = record.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _string(record: dict[str, Any], key: str) -> str | None:
    value = record.get(key)
    return value if isinstance(value, str) and value else None


def _add_if(attributes: dict[str, Any], key: str, value: Any) -> None:
    if value is not None and value != "":
        attributes[key] = value


def _common_attributes(record: dict[str, Any], raw: RawRecord, node: str,
                       guest_context: dict[str, str] | None = None) -> tuple[dict[str, Any], list[str]]:
    attributes: dict[str, Any] = {
        "deepflow.signal_source": record["signal_source"],
        "deepflow.l7_protocol": record["l7_protocol"],
        "deepflow.raw.source_file": raw.source_file,
        "deepflow.raw.retained_file": raw.retained_file,
        "deepflow.raw.offset": raw.offset,
        "deepflow.raw.length": raw.length,
        "deepflow.raw.sha256": raw.sha256,
        "deepflow.guest": node,
        "deepflow.source_commit": DEEPFLOW_SOURCE_COMMIT,
        "deepflow.clock.domain": SOURCE_CLOCK,
        "deepflow.clock.unit": "microseconds",
        "deepflow.clock.controller_ntp_correction_enabled": False,
    }
    warnings: list[str] = []
    for key, value in sorted((guest_context or {}).items()):
        _add_if(attributes, "deepflow.guest." + key, value)
    for field in (
        "tap_side", "ebpf_type", "msg_type", "flow_id", "gpid_0", "gpid_1",
        "syscall_trace_id_request", "syscall_trace_id_response", "thread_id_0",
        "thread_id_1", "coroutine_id_0", "coroutine_id_1", "cap_seq_0", "cap_seq_1",
        "ip_src", "ip_dst", "port_src", "port_dst", "response_duration",
    ):
        _add_if(attributes, "deepflow." + field, record.get(field))
    namespace = record.get(_MSG_TYPE_NAMESPACE)
    if isinstance(namespace, dict):
        _add_if(attributes, "deepflow.base_head.msg_type",
                namespace.get("base_head_msg_type"))
        _add_if(attributes, "deepflow.protocol_info.msg_type",
                namespace.get("protocol_info_msg_type"))
    for field in ("trace_ids", "span_id"):
        _add_if(attributes, "deepflow.carrier." + field, record.get(field))
    _add_if(attributes, "deepflow.x_request_id_0", record.get("x_request_id_0"))
    _add_if(attributes, "deepflow.x_request_id_1", record.get("x_request_id_1"))

    side = record.get("tap_side")
    local_index = 0 if side == "ClientProcess" else 1 if side == "ServerProcess" else None
    if side == "ClientProcess":
        _add_if(attributes, "server.address", record.get("ip_dst"))
        _add_if(attributes, "server.port", _integer(record, "port_dst"))
    elif side == "ServerProcess":
        _add_if(attributes, "client.address", record.get("ip_src"))
        _add_if(attributes, "client.port", _integer(record, "port_src"))
    if local_index is None:
        warnings.append("local_process_unknown_for_nonprocess_tap_side")
    else:
        _add_if(attributes, "process.pid", _integer(record, f"process_id_{local_index}"))
        # A kernel command name is retained as process evidence, never service.name.
        _add_if(attributes, "process.command", _string(record, f"process_kname_{local_index}"))
        attributes["deepflow.local_process_index"] = local_index
    return attributes, warnings


def _protocol_attributes(record: dict[str, Any], attributes: dict[str, Any]) -> tuple[str, list[str]]:
    protocol = record["l7_protocol"]
    warnings: list[str] = []
    request_type = record.get("request_type")
    resource = record.get("request_resource")
    if protocol in {"Http1", "Http2"}:
        _add_if(attributes, "http.request.method", request_type)
        _add_if(attributes, "url.path", resource)
        _add_if(attributes, "server.address", record.get("request_domain"))
        _add_if(attributes, "network.protocol.version", record.get("version"))
        _add_if(attributes, "http.response.status_code", _integer(record, "response_code"))
        _add_if(attributes, "deepflow.http.endpoint", record.get("endpoint"))
        if protocol == "Http2":
            _add_if(attributes, "deepflow.http2.stream_id", record.get("request_id"))
        # Only request-direction extraction is the configured experiment header.
        _add_if(attributes, "http.request.header.x-experiment-request-id",
                _string(record, "x_request_id_0"))
        if not request_type or not resource:
            warnings.append("http_method_or_path_missing")
        return f"{request_type or 'HTTP'} {resource or ''}".strip(), warnings
    if protocol == "Grpc":
        attributes["rpc.system"] = "grpc"
        _add_if(attributes, "deepflow.grpc.path", resource)
        if isinstance(resource, str) and resource.startswith("/") and resource.count("/") == 2:
            service, method = resource[1:].split("/", 1)
            if service and method:
                attributes["rpc.service"] = service
                attributes["rpc.method"] = method
            else:
                warnings.append("grpc_path_not_splittable")
        else:
            warnings.append("grpc_path_missing_or_unrecognized")
        return str(resource or "grpc"), warnings
    if protocol == "MySQL":
        attributes["db.system.name"] = "mysql"
        _add_if(attributes, "db.query.text", resource)
        _add_if(attributes, "deepflow.mysql.command_code", request_type)
        _add_if(attributes, "deepflow.mysql.statement_id", record.get("statement_id"))
        return "mysql", warnings
    if protocol == "PostgreSQL":
        attributes["db.system.name"] = "postgresql"
        _add_if(attributes, "db.query.text", resource)
        _add_if(attributes, "deepflow.postgresql.request_type", request_type)
        _add_if(attributes, "deepflow.postgresql.status", record.get("status"))
        return "postgresql", warnings
    if protocol == "Redis":
        attributes["db.system.name"] = "redis"
        _add_if(attributes, "db.operation.name", request_type)
        _add_if(attributes, "db.query.text", resource)
        attributes["deepflow.redis.lossy_utf8_possible"] = True
        return "redis", warnings
    if protocol == "MongoDB":
        attributes["db.system.name"] = "mongodb"
        _add_if(attributes, "db.query.text", resource)
        for field in ("op_code", "request_id", "response_id", "req_len", "resp_len"):
            _add_if(attributes, "deepflow.mongodb." + field, record.get(field))
        return "mongodb", warnings
    if protocol == "Kafka":
        attributes["messaging.system"] = "kafka"
        _add_if(attributes, "messaging.operation.name", request_type)
        _add_if(attributes, "messaging.destination.name", resource)
        for field in ("partition", "offset", "group_id", "request_id"):
            _add_if(attributes, "deepflow.kafka." + field, record.get(field))
        return f"kafka {request_type or ''}".strip(), warnings
    raise AssertionError(f"unsupported protocol entered mapper: {protocol}")


def normalize_record(raw: RawRecord, *, node: str,
                     guest_context: dict[str, str] | None = None) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    decoded, conflicts, parse_error = _parse(raw.raw)
    locator = {
        "source_file": raw.source_file, "retained_file": raw.retained_file,
        "offset": raw.offset, "length": raw.length, "sha256": raw.sha256,
    }
    if parse_error:
        return None, {**locator, "status": "unclassified", "reasons": [parse_error],
                      "technical_failure": True}
    if conflicts:
        return None, {**locator, "status": "unclassified",
                      "reasons": ["conflicting_duplicate_keys"], "conflicts": conflicts,
                      "technical_failure": False}
    assert decoded is not None
    if decoded.get("signal_source") != "EBPF":
        return None, {**locator, "status": "retained_non_ebpf",
                      "reasons": [f"signal_source:{decoded.get('signal_source')!r}"],
                      "technical_failure": False}
    protocol = decoded.get("l7_protocol")
    if protocol not in SUPPORTED_PROTOCOLS:
        return None, {**locator, "status": "unclassified",
                      "reasons": [f"unsupported_or_unknown_protocol:{protocol!r}"],
                      "technical_failure": False}
    start_us, end_us = _integer(decoded, "start_time"), _integer(decoded, "end_time")
    if start_us is None or end_us is None:
        return None, {**locator, "status": "unclassified",
                      "reasons": ["start_time_or_end_time_not_integer_microseconds"],
                      "technical_failure": True}
    if (start_us < 0 or end_us < 0
            or start_us > MAX_OTLP_UNIX_NANO // 1000
            or end_us > MAX_OTLP_UNIX_NANO // 1000):
        return None, {**locator, "status": "unclassified",
                      "reasons": ["start_time_or_end_time_not_representable_as_otlp_unix_nano"],
                      "raw_start_time_us": start_us, "raw_end_time_us": end_us,
                      "technical_failure": True}
    attributes, warnings = _common_attributes(decoded, raw, node, guest_context)
    attributes["deepflow.event.start_time_us"] = start_us
    attributes["deepflow.event.end_time_us"] = end_us
    name, protocol_warnings = _protocol_attributes(decoded, attributes)
    warnings.extend(protocol_warnings)
    if end_us < start_us:
        warnings.append("end_time_precedes_start_time_source_clock_uncertainty")
    guest_scope = {
        key: value for key, value in (guest_context or {}).items()
        if key in {"boot_id", "pid_namespace"} and value
    }
    host_pid = attributes.get("process.pid")
    runtime_identity = {
        "node": node,
        "host_pid": host_pid,
        "boot_id": guest_scope.get("boot_id"),
        "pid_namespace": guest_scope.get("pid_namespace"),
        # The collector runs with --pid=host and DeepFlow serializes the
        # kernel-observed process_id_0/1, so this coordinate is the guest host
        # PID namespace, not the collector container's private namespace.
        "pid_scope": "guest_host" if host_pid is not None else None,
        "source_clock": SOURCE_CLOCK,
        "start": start_us,
        "end": end_us,
        "unit": "microseconds",
        "locator": dict(locator),
    }
    request_nonce = _string(decoded, "x_request_id_0")
    if protocol in {"Http1", "Http2", "Grpc"} and request_nonce:
        runtime_identity["request_nonce"] = request_nonce
        runtime_identity["method"] = _string(decoded, "request_type")
        runtime_identity["route"] = _string(decoded, "request_resource")
        if decoded.get("tap_side") == "ServerProcess":
            runtime_identity["event_role"] = "synchronous_server_entry"
    for key in ("node", "host_pid", "boot_id", "pid_namespace", "pid_scope", "source_clock",
                "start", "end", "unit", "locator", "request_nonce", "method", "route",
                "event_role"):
        _add_if(attributes, "_runtime_identity." + key, runtime_identity.get(key))
    side = decoded.get("tap_side")
    kind = "SPAN_KIND_CLIENT" if side == "ClientProcess" else (
        "SPAN_KIND_SERVER" if side == "ServerProcess" else "SPAN_KIND_UNSPECIFIED"
    )
    span = {
        # Deliberately absent: traceId, spanId, parentSpanId.
        "name": name,
        "kind": kind,
        "startTimeUnixNano": str(start_us * 1000),
        "endTimeUnixNano": str(end_us * 1000),
        "attributes": [_attr(key, value) for key, value in sorted(attributes.items())],
    }
    accounting = {**locator, "status": "normalized", "protocol": protocol,
                  "source_clock": SOURCE_CLOCK,
                  "start_time_us": start_us, "end_time_us": end_us,
                  "warnings": warnings, "ids_invented": False,
                  "service_identity_enriched": False, "technical_failure": False}
    namespace = decoded.get(_MSG_TYPE_NAMESPACE)
    if isinstance(namespace, dict):
        accounting["source_namespace_split"] = dict(namespace)
    accounting["_runtime_identity"] = runtime_identity
    return span, accounting


def _batch(spans: Iterable[dict[str, Any]], *, node: str,
           batch_size: int = 256) -> Iterable[dict[str, Any]]:
    pending: list[dict[str, Any]] = []
    for span in spans:
        pending.append(span)
        if len(pending) == batch_size:
            yield _envelope(pending, node)
            pending = []
    if pending:
        yield _envelope(pending, node)


def _envelope(spans: list[dict[str, Any]], node: str) -> dict[str, Any]:
    return {
        "source": f"ebpf-deepflow:{node}",
        "id_encoding": "hex",
        "payload": {"resourceSpans": [{
            "resource": {"attributes": [
                _attr("deepflow.guest", node),
                _attr("deepflow.version", DEEPFLOW_VERSION),
                _attr("deepflow.source_commit", DEEPFLOW_SOURCE_COMMIT),
            ]},
            "scopeSpans": [{
                "scope": {"name": "deepflow-standalone-codec-v5"},
                "spans": spans,
            }],
        }]},
    }


def codec_file(path: Path, *, node: str, source_file: str | None = None,
               retained_file: str | None = None,
               limit: int | None = None, seen: set[tuple[str, int, str]] | None = None,
               batch_size: int = 256,
               guest_context: dict[str, str] | None = None,
               on_batch: Callable[[dict[str, Any]], None] | None = None,
               on_accounting: Callable[[dict[str, Any]], None] | None = None,
               ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Stream to sinks in acquisition; materialize outputs only when requested."""
    if type(batch_size) is not int or batch_size <= 0:
        raise ValueError("batch_size must be a positive envelope size, never an observation cap")
    prefix = {}
    records = iter_complete_records(path, prefix, source_file=source_file,
                                    retained_file=retained_file, limit=limit)
    seen = seen if seen is not None else set()
    batches, accounting, pending = [], [], []
    counts = {key: 0 for key in ("normalized_records", "unclassified_records", "non_ebpf_records",
                                "already_normalized_records", "technical_failure_records",
                                "normalized_batches")}
    def emit_batch():
        envelope = _envelope(list(pending), node)
        (on_batch if on_batch is not None else batches.append)(envelope)
        counts["normalized_batches"] += 1
        pending.clear()
    for raw in records:
        key = (raw.source_file, raw.offset, raw.sha256)
        if key in seen:
            span = None
            entry = {
                "source_file": raw.source_file, "retained_file": raw.retained_file,
                "offset": raw.offset, "length": raw.length, "sha256": raw.sha256,
                "status": "already_normalized",
                "technical_failure": False,
            }
        else:
            span, entry = normalize_record(raw, node=node, guest_context=guest_context)
            seen.add(key)
        (on_accounting if on_accounting is not None else accounting.append)(entry)
        counts["unclassified_records"] += entry["status"] == "unclassified"
        counts["non_ebpf_records"] += entry["status"] == "retained_non_ebpf"
        counts["already_normalized_records"] += entry["status"] == "already_normalized"
        counts["technical_failure_records"] += bool(entry.get("technical_failure"))
        if span is not None:
            counts["normalized_records"] += 1
            pending.append(span)
            if len(pending) == batch_size:
                emit_batch()
    if pending:
        emit_batch()
    prefix.update(counts)
    return batches, accounting, prefix


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n")
            count += 1
        stream.flush()
    return count
