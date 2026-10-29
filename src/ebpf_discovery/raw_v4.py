"""Loss-preserving export of source-local observations selected from a frozen index."""
from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

import ijson

from .store_v3 import LimitedReader


def _hash_prefix(path: Path, size: int) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        remaining = size
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError(f"indexed prefix exceeds file: {path}")
            digest.update(chunk)
            remaining -= len(chunk)
    return digest.hexdigest()


def _lines(reader: LimitedReader):
    pending = b""
    while True:
        chunk = reader.read(65536)
        if not chunk:
            break
        pending += chunk
        while b"\n" in pending:
            line, pending = pending.split(b"\n", 1)
            yield line + b"\n"
    if pending:
        yield pending


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _source(path: Path) -> str:
    return "ebpf" if path.name in {"a.jsonl", "b.jsonl"} else "native"


def _identity(raw: Any, encoding: str) -> str:
    if not raw:
        return ""
    if encoding == "base64":
        try:
            return base64.b64decode(raw).hex()
        except Exception:
            return ""
    return str(raw).lower()


def _add_network_scope_json(payload: dict, network_scope: str | None) -> None:
    if network_scope is None:
        return
    for resource in payload.get("resourceSpans", []):
        resource.setdefault("resource", {}).setdefault("attributes", []).append({
            "key": "bering.network.scope", "value": {"stringValue": network_scope},
        })


def _observed_http_attributes(span, protobuf: bool) -> dict[str, str]:
    """Read only route-relevant source strings, rejecting conflicting repetitions."""
    wanted = {'http.url', 'url.full', 'url.path', 'http.target', 'http.route'}
    result = {}
    for item in span.attributes if protobuf else span.get('attributes', []):
        key = item.key if protobuf else item.get('key')
        if key not in wanted:
            continue
        if protobuf:
            if item.value.WhichOneof('value') != 'string_value':
                raise ValueError(f'non-string observed HTTP attribute: {key}')
            value = item.value.string_value
        else:
            raw = item.get('value', {})
            if set(raw) != {'stringValue'} or not isinstance(raw['stringValue'], str):
                raise ValueError(f'non-string observed HTTP attribute: {key}')
            value = raw['stringValue']
        if key in result and result[key] != value:
            raise ValueError(f'conflicting observed HTTP attribute: {key}')
        result[key] = value
    return result


def _derived_path_from_actual_url(span, protobuf: bool, source: str, key):
    attrs = _observed_http_attributes(span, protobuf)
    candidates = []
    for field in ('http.url', 'url.full'):
        if not attrs.get(field):
            continue
        url = attrs[field]
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in ('http', 'https') or not parsed.netloc or not parsed.path.startswith('/'):
            raise ValueError(f'invalid observed full HTTP URL for supplied entry: {source} {key}')
        candidates.append({'field': field, 'url': url, 'path': parsed.path,
                           'query_stripped': bool(parsed.query), 'fragment_stripped': bool(parsed.fragment)})
    if not candidates:
        return None
    paths = {candidate['path'] for candidate in candidates}
    if len(paths) != 1:
        raise ValueError(f'contradictory observed HTTP URL paths for supplied entry: {source} {key}')
    path = candidates[0]['path']
    for field in ('url.path', 'http.target'):
        if attrs.get(field) and urlsplit(attrs[field]).path != path:
            raise ValueError(f'contradictory observed HTTP URL and {field}: {source} {key}')
    if any(attrs.get(field) for field in ('http.route', 'url.path', 'http.target')):
        return None
    if protobuf:
        span.attributes.add(key='url.path').value.string_value = path
    else:
        span.setdefault('attributes', []).append({'key': 'url.path', 'value': {'stringValue': path}})
    return {'source_urls': candidates, 'derived_path': path,
            'rule': 'parsed path from actual observed full HTTP URL; query and fragment removed; declared path unused'}


def _supply_server_role(span, key, source, roles, *, protobuf=False):
    declaration = roles.get((source, *key))
    if declaration is None:
        return None
    if protobuf:
        original = int(span.kind)
        if original != 0:
            raise ValueError(f"supplied server role conflicts with explicit kind: {source} {key}")
        span.kind = 2
    else:
        original = span.get("kind")
        if original not in (None, 0, "SPAN_KIND_UNSPECIFIED"):
            raise ValueError(f"supplied server role conflicts with explicit kind: {source} {key}")
        span["kind"] = "SPAN_KIND_SERVER"
    if declaration.get("original_kind") not in (None, 0, "0", "SPAN_KIND_UNSPECIFIED"):
        raise ValueError(f"invalid supplied server role provenance: {source} {key}")
    applied = dict(declaration)
    derivation = _derived_path_from_actual_url(span, protobuf, source, key)
    if derivation is not None:
        applied['supplied_url_path'] = derivation
    return applied


def _filter_json(payload: dict, identities: set[tuple[str, str]] | None, encoding: str,
                 network_scope: str | None, source: str = "ebpf",
                 roles: dict | None = None) -> tuple[dict, int, list[tuple[str, str]], list[dict]]:
    filtered = copy.deepcopy(payload)
    kept_resources, found, supplied, count = [], [] if identities is not None else None, [], 0
    for resource in filtered.get("resourceSpans", []):
        scope_key = "scopeSpans" if "scopeSpans" in resource else "instrumentationLibrarySpans"
        kept_scopes = []
        for scope in resource.get(scope_key, []):
            kept_spans = []
            for span in scope.get("spans", []):
                key = (_identity(span.get("traceId"), encoding), _identity(span.get("spanId"), encoding))
                if identities is None or key in identities:
                    role = _supply_server_role(span, key, source, roles or {})
                    if role is not None:
                        supplied.append(role)
                    kept_spans.append(span)
                    count += 1
                    if found is not None:
                        found.append(key)
            if kept_spans:
                scope["spans"] = kept_spans
                kept_scopes.append(scope)
        if kept_scopes:
            resource[scope_key] = kept_scopes
            kept_resources.append(resource)
    filtered["resourceSpans"] = kept_resources
    _add_network_scope_json(filtered, network_scope)
    return filtered, count, found, supplied


def _filter_protobuf(wire: bytes, identities: set[tuple[str, str]] | None,
                     network_scope: str | None, source: str = "ebpf",
                     roles: dict | None = None):
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
    from opentelemetry.proto.common.v1.common_pb2 import KeyValue

    original = ExportTraceServiceRequest()
    original.ParseFromString(wire)
    filtered = ExportTraceServiceRequest()
    filtered.CopyFrom(original)
    filtered.ClearField("resource_spans")
    found, supplied, count = [] if identities is not None else None, [], 0
    for resource in original.resource_spans:
        kept_resource = None
        for scope in resource.scope_spans:
            matches = []
            for span in scope.spans:
                key = (bytes(span.trace_id).hex(), bytes(span.span_id).hex())
                if identities is None or key in identities:
                    matches.append(span)
                    count += 1
                    if found is not None:
                        found.append(key)
            if not matches:
                continue
            if kept_resource is None:
                kept_resource = filtered.resource_spans.add()
                kept_resource.CopyFrom(resource)
                kept_resource.ClearField("scope_spans")
                if network_scope is not None:
                    attribute = KeyValue(key="bering.network.scope")
                    attribute.value.string_value = network_scope
                    kept_resource.resource.attributes.append(attribute)
            kept_scope = kept_resource.scope_spans.add()
            kept_scope.CopyFrom(scope)
            kept_scope.ClearField("spans")
            for span in matches:
                copied = kept_scope.spans.add()
                copied.CopyFrom(span)
                role = _supply_server_role(copied, (bytes(span.trace_id).hex(), bytes(span.span_id).hex()),
                                           source, roles or {}, protobuf=True)
                if role is not None:
                    supplied.append(role)
    return filtered.SerializeToString(), count, found, supplied


def _typed_value(tag: dict) -> dict:
    value, kind = tag.get("value"), str(tag.get("type", "")).lower()
    if kind == "bool" or isinstance(value, bool):
        return {"boolValue": bool(value)}
    if kind in {"int64", "int"} or isinstance(value, int):
        return {"intValue": str(value)}
    if kind in {"float64", "float"} or isinstance(value, float):
        return {"doubleValue": value}
    if kind == "binary":
        return {"bytesValue": str(value)}
    return {"stringValue": "" if value is None else str(value)}


def _tags(tags: Iterable[dict]) -> list[dict]:
    return [{"key": str(tag.get("key", "")), "value": _typed_value(tag)} for tag in tags]


def _codec_id(raw: Any, width: int) -> str:
    value = str(raw or "").lower()
    if not value or len(value) > width or any(char not in "0123456789abcdef" for char in value):
        return value
    return value.zfill(width)


def _jaeger_trace(trace: dict, identities: set[tuple[str, str]] | None,
                  network_scope: str | None, roles: dict | None = None
                  ) -> tuple[dict, int, list[tuple[str, str]], list[dict]]:
    processes = trace.get("processes", {})
    resources: dict[str, dict] = {}
    found, supplied, count = [] if identities is not None else None, [], 0
    kinds = {
        "server": "SPAN_KIND_SERVER", "client": "SPAN_KIND_CLIENT",
        "producer": "SPAN_KIND_PRODUCER", "consumer": "SPAN_KIND_CONSUMER",
        "internal": "SPAN_KIND_INTERNAL",
    }
    for span in trace.get("spans", []):
        raw_key = (str(span.get("traceID", "")).lower(), str(span.get("spanID", "")).lower())
        if identities is not None and raw_key not in identities:
            continue
        count += 1
        if found is not None:
            found.append(raw_key)
        process_id = str(span.get("processID", ""))
        process = processes.get(process_id, {})
        resource = resources.setdefault(process_id, {
            "resource": {"attributes": [
                {"key": "service.name", "value": {"stringValue": str(process.get("serviceName", "unknown"))}},
                *_tags(process.get("tags", [])),
            ]},
            "scopeSpans": [{"scope": {"name": "jaeger-api-faithful-codec"}, "spans": []}],
        })
        if network_scope is not None and not any(
            item.get("key") == "bering.network.scope" and item.get("_supplied_by_raw_v4")
            for item in resource["resource"]["attributes"]
        ):
            resource["resource"]["attributes"].append({
                "key": "bering.network.scope", "value": {"stringValue": network_scope},
                "_supplied_by_raw_v4": True,
            })

        same_trace_children = [ref for ref in span.get("references", [])
            if ref.get("refType") == "CHILD_OF"
            and str(ref.get("traceID", "")).lower() == raw_key[0]]
        parent_ref = same_trace_children[0] if len(same_trace_children) == 1 else None
        otlp_span = {
            "traceId": _codec_id(span.get("traceID"), 32),
            "spanId": _codec_id(span.get("spanID"), 16),
            "name": str(span.get("operationName", "")),
            "startTimeUnixNano": str(int(span.get("startTime", 0)) * 1000),
            "endTimeUnixNano": str((int(span.get("startTime", 0)) + int(span.get("duration", 0))) * 1000),
            "attributes": _tags(span.get("tags", [])),
        }
        if parent_ref is not None:
            otlp_span["parentSpanId"] = _codec_id(parent_ref.get("spanID"), 16)
        explicit_kind = next((str(tag.get("value", "")).lower() for tag in span.get("tags", [])
                              if tag.get("key") == "span.kind"), "")
        if explicit_kind in kinds:
            otlp_span["kind"] = kinds[explicit_kind]
        elif explicit_kind and ("native", *raw_key) in (roles or {}):
            raise ValueError(f"supplied server role conflicts with explicit Jaeger kind: {raw_key}")
        role = _supply_server_role(otlp_span, raw_key, "native", roles or {})
        if role is not None:
            supplied.append(role)
        if any(tag.get("key") == "error" and bool(tag.get("value")) for tag in span.get("tags", [])):
            otlp_span["status"] = {"code": "STATUS_CODE_ERROR"}
        events = []
        for log in span.get("logs", []):
            events.append({"timeUnixNano": str(int(log.get("timestamp", 0)) * 1000),
                           "name": "jaeger.log", "attributes": _tags(log.get("fields", []))})
        if events:
            otlp_span["events"] = events
        links = []
        for ref in span.get("references", []):
            if ref is parent_ref:
                continue
            links.append({
                "traceId": _codec_id(ref.get("traceID"), 32),
                "spanId": _codec_id(ref.get("spanID"), 16),
                "attributes": [{"key": "jaeger.ref_type", "value": {"stringValue": str(ref.get("refType", ""))}}],
            })
        if links:
            otlp_span["links"] = links
        resource["scopeSpans"][0]["spans"].append(otlp_span)

    for resource in resources.values():
        for attribute in resource["resource"]["attributes"]:
            attribute.pop("_supplied_by_raw_v4", None)
    return {"resourceSpans": list(resources.values())}, count, found, supplied


def _write_export(out: Path, ordinal: int, source: str, content_type: str, body: bytes,
                  raw_file: Path, raw_sha256: str, observations: int,
                  selected_ids: list[tuple[str, str]] | None, codec_steps: list[str],
                  *, content_encoding: str = "", network_scope: str | None = None,
                  raw_prefix_bytes: int | None = None,
                  supplied_server_roles: list[dict] | None = None,
                  index_file: Path | None = None,
                  index_prefix_sha256: str | None = None,
                  prepared_path: Path | None = None) -> dict:
    suffix = ".pb" if "protobuf" in content_type else ".json"
    if content_encoding == "gzip":
        suffix += ".gz"
    path = (out / f"{source}-{ordinal:06d}{suffix}").resolve()
    if prepared_path is None:
        _atomic_write(path, body)
        exported_sha256 = hashlib.sha256(body).hexdigest()
    else:
        if Path(prepared_path).resolve() != path or not path.is_file():
            raise ValueError("prepared export path differs from declared export")
        with path.open("rb") as stream:
            exported_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
    result = {
        "path": str(path), "source": source, "content_type": content_type,
        "content_encoding": content_encoding, "observations": observations,
        "sha256": exported_sha256, "raw_file": str(raw_file.resolve()),
        "raw_sha256": raw_sha256,
        "codec_steps": codec_steps,
    }
    if selected_ids is None:
        result["selection"] = "all_frozen_source_records"
    else:
        result["selected_ids"] = [list(item) for item in selected_ids]
    if raw_prefix_bytes is not None:
        result["raw_prefix_bytes"] = raw_prefix_bytes
    if index_file is not None:
        result["indexed_wrapper_file"] = str(index_file.resolve())
        result["indexed_wrapper_prefix_sha256"] = index_prefix_sha256
    if network_scope is not None:
        result["network_scope"] = network_scope
        result["network_scope_provenance"] = "explicit experiment inventory enrichment"
    if supplied_server_roles:
        result["supplied_server_roles"] = supplied_server_roles
    return result


def export_selection(store, selected: dict[str, set[tuple[str, str]] | None], out: Path,
                     network_scope: str | None = None,
                     supplied_server_roles: dict | None = None,
                     native_jaeger_envelope: str = "per_file") -> dict:
    """Export frozen prefixes; a source value of None selects all its records."""
    if native_jaeger_envelope not in ("per_file", "per_trace"):
        raise ValueError("unsupported native Jaeger envelope granularity")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    exports, ordinal, total = [], 0, 0
    roles = supplied_server_roles or {}
    rows = list(store.db.execute("SELECT path,consumed FROM files ORDER BY path"))
    for raw_path, consumed in rows:
        path = Path(raw_path)
        source = _source(path)
        identities = selected.get(source, set())
        if identities is not None and not identities:
            continue
        if consumed < 0 or consumed > path.stat().st_size:
            raise ValueError(f"invalid indexed prefix for {path}: {consumed}")
        prefix_hash = _hash_prefix(path, consumed)
        if path.name.startswith("traces-") and path.suffix == ".json":
            if native_jaeger_envelope == "per_file":
                prepared = (out / f"{source}-{ordinal + 1:06d}.json").resolve()
                temporary = prepared.with_name(f".{prepared.name}.tmp")
                file_count, traces_seen, traces_exported = 0, 0, 0
                found_all = [] if identities is not None else None
                supplied_all = []
                first_resource = True
                try:
                    with path.open("rb") as stream, temporary.open("wb") as output:
                        reader = LimitedReader(stream, consumed)
                        output.write(b'{"resourceSpans":[')
                        for trace in ijson.items(reader, "data.item", use_float=True):
                            traces_seen += 1
                            payload, count, found, supplied = _jaeger_trace(
                                trace, identities, network_scope, roles)
                            if not count:
                                continue
                            traces_exported += 1
                            file_count += count
                            if found_all is not None:
                                found_all.extend(found)
                            supplied_all.extend(supplied)
                            for resource in payload["resourceSpans"]:
                                if not first_resource:
                                    output.write(b",")
                                first_resource = False
                                output.write(json.dumps(resource, separators=(",", ":")).encode())
                        output.write(b"]}\n")
                    if file_count:
                        os.replace(temporary, prepared)
                        ordinal += 1
                        exported = _write_export(
                            out, ordinal, source, "application/json", b"", path, prefix_hash,
                            file_count, found_all,
                            ["jaeger tags/process tags/logs/references converted to typed OTLP JSON",
                             "nonzero short hexadecimal IDs left-padded only to OTLP bit width",
                             "resourceSpans appended from each original Jaeger trace in query order without merging"],
                            network_scope=network_scope, raw_prefix_bytes=consumed,
                            supplied_server_roles=supplied_all, prepared_path=prepared,
                        )
                        exported.update(native_jaeger_envelope="per_file",
                                        jaeger_query_traces_seen=traces_seen,
                                        jaeger_query_traces_exported=traces_exported)
                        exports.append(exported)
                        total += file_count
                    else:
                        temporary.unlink(missing_ok=True)
                except BaseException:
                    temporary.unlink(missing_ok=True)
                    raise
                continue
            with path.open("rb") as stream:
                reader = LimitedReader(stream, consumed)
                for trace in ijson.items(reader, "data.item", use_float=True):
                    payload, count, found, supplied = _jaeger_trace(trace, identities, network_scope, roles)
                    if not count:
                        continue
                    ordinal += 1
                    body = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
                    exports.append(_write_export(
                        out, ordinal, source, "application/json", body, path, prefix_hash,
                        count, found,
                        ["jaeger tags/process tags/logs/references converted to typed OTLP JSON",
                         "nonzero short hexadecimal IDs left-padded only to OTLP bit width"],
                        network_scope=network_scope, raw_prefix_bytes=consumed,
                        supplied_server_roles=supplied,
                    ))
                    total += count
            continue

        with path.open("rb") as stream:
            reader = LimitedReader(stream, consumed)
            for raw_line in _lines(reader):
                if not raw_line.strip():
                    continue
                document = json.loads(raw_line)
                raw_ref = document.get("raw_ref")
                if "payload" in document and not raw_ref:
                    raise ValueError(
                        f"receiver wrapper lacks original wire capture: {path}; "
                        "decoded MessageToDict payload is not a lossless OTLP export"
                    )
                if raw_ref:
                    original_path = Path(raw_ref)
                    if not original_path.is_absolute():
                        original_path = path.parent / original_path
                    original = original_path.read_bytes()
                    raw_hash = hashlib.sha256(original).hexdigest()
                    if raw_hash != document.get("raw_sha256"):
                        raise ValueError(f"raw capture digest mismatch: {original_path}")
                    content_type = document.get("content_type", "application/x-protobuf")
                    content_encoding = document.get("content_encoding", "").lower().strip()
                    decoded = gzip.decompress(original) if content_encoding == "gzip" else original
                    if "json" in content_type.lower():
                        payload, count, found, supplied = _filter_json(json.loads(decoded), identities,
                            document.get("id_encoding", "hex"), network_scope, source, roles)
                        body = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
                    else:
                        body, count, found, supplied = _filter_protobuf(decoded, identities,
                                                                       network_scope, source, roles)
                    if not count:
                        continue
                    if content_encoding == "gzip":
                        body = gzip.compress(body, mtime=0)
                    ordinal += 1
                    exports.append(_write_export(
                        out, ordinal, source, content_type, body, original_path, raw_hash,
                        count, found, [("all source records in frozen indexed prefix from original wire export"
                                       if identities is None else "selected exact source-local IDs from original wire export"),
                                       "copied complete resource/scope/span structures"],
                        content_encoding=content_encoding, network_scope=network_scope,
                        supplied_server_roles=supplied,
                        **({'index_file': path, 'index_prefix_sha256': prefix_hash,
                            'raw_prefix_bytes': consumed} if identities is None else {}),
                    ))
                    total += count
                    continue

                payload = document.get("payload", document)
                encoding = document.get("id_encoding", "hex")
                filtered, count, found, supplied = _filter_json(payload, identities, encoding,
                                                                 network_scope, source, roles)
                if not count:
                    continue
                ordinal += 1
                body = (json.dumps(filtered, separators=(",", ":")) + "\n").encode()
                exported = _write_export(
                    out, ordinal, source, "application/json", body, path,
                    prefix_hash, count, found,
                    [("all records in frozen direct OTLP JSONL document without normalized reconstruction"
                      if identities is None else "filtered direct OTLP JSONL document without normalized reconstruction")],
                    network_scope=network_scope, raw_prefix_bytes=consumed,
                    supplied_server_roles=supplied,
                )
                exported["raw_record_sha256"] = hashlib.sha256(raw_line).hexdigest()
                exports.append(exported)
                total += count
    if roles:
        applied = {(role["source"], role["trace_id"], role["span_id"])
                   for item in exports for role in item.get("supplied_server_roles", [])}
        if applied != set(roles):
            raise ValueError(f"supplied server roles not applied to exact selected source identities: {sorted(set(roles)-applied)}")
    result = {"exports": exports, "observations": total}
    if "native" in selected:
        result["native_jaeger_envelope"] = native_jaeger_envelope
    if any(ids is None for ids in selected.values()):
        result["selection_by_source"] = {
            source: ("all_frozen_source_records" if ids is None
                     else "exact_selected_source_identities") for source, ids in selected.items()}
    return result
