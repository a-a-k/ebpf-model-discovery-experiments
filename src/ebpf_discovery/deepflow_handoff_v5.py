"""Validate declared DeepFlow-derived OTLP against retained source rows."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from . import deepflow_codec_v5 as codec_module
from .deepflow_codec_v5 import RawRecord, _envelope, normalize_record


_LOCATOR_FIELDS = ("source_file", "retained_file", "offset", "length", "sha256")


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _inside(root: Path, relative: str) -> Path:
    value = PurePosixPath(relative)
    if (not relative or "\\" in relative or value.is_absolute() or ".." in value.parts):
        raise ValueError(f"unsafe DeepFlow retained dependency: {relative!r}")
    target = (root / Path(*value.parts)).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"DeepFlow retained dependency escapes observations: {relative}") from exc
    return target


def _value(raw: Any) -> Any:
    if not isinstance(raw, dict) or len(raw) != 1:
        raise ValueError("DeepFlow derived OTLP attribute lacks one typed value")
    key, value = next(iter(raw.items()))
    if key == "stringValue" and isinstance(value, str):
        return value
    if key == "intValue" and isinstance(value, str):
        digits = value[1:] if value.startswith("-") else value
        if value == "0" or (digits and digits[0] in "123456789" and digits.isdecimal()):
            return int(value)
    if key == "boolValue" and isinstance(value, bool):
        return value
    if key == "doubleValue" and isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    if key == "arrayValue" and isinstance(value, dict):
        values = value.get("values")
        if not isinstance(values, list):
            raise ValueError("DeepFlow derived OTLP array lacks values")
        return [_value(item) for item in values]
    if key == "kvlistValue" and isinstance(value, dict):
        result = {}
        for item in value.get("values", []):
            name = item.get("key") if isinstance(item, dict) else None
            if not isinstance(name, str) or name in result:
                raise ValueError("DeepFlow derived OTLP kvlist has duplicate/invalid keys")
            result[name] = _value(item.get("value"))
        return result
    raise ValueError("DeepFlow derived OTLP attribute uses unsupported typed value")


def _attributes(span: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for item in span.get("attributes", []):
        key = item.get("key") if isinstance(item, dict) else None
        if not isinstance(key, str) or key in result:
            raise ValueError("DeepFlow derived OTLP span has duplicate/invalid attributes")
        result[key] = _value(item.get("value"))
    return result


def _locator(span: dict[str, Any]) -> dict[str, Any]:
    attrs = _attributes(span)
    locator = {
        "source_file": attrs.get("deepflow.raw.source_file"),
        "retained_file": attrs.get("deepflow.raw.retained_file"),
        "offset": attrs.get("deepflow.raw.offset"),
        "length": attrs.get("deepflow.raw.length"),
        "sha256": attrs.get("deepflow.raw.sha256"),
    }
    nested = attrs.get("_runtime_identity.locator")
    if (set(locator) != set(_LOCATOR_FIELDS)
            or not isinstance(locator["source_file"], str)
            or not isinstance(locator["retained_file"], str)
            or type(locator["offset"]) is not int or locator["offset"] < 0
            or type(locator["length"]) is not int or locator["length"] <= 0
            or not isinstance(locator["sha256"], str) or len(locator["sha256"]) != 64
            or any(char not in "0123456789abcdef" for char in locator["sha256"])
            or nested != locator):
        raise ValueError("DeepFlow derived OTLP span lacks one exact raw locator")
    return locator


def _key(locator: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(locator[name] for name in _LOCATOR_FIELDS)


class DeepFlowDerivedValidator:
    """Cache immutable dependency proofs; hash each referenced segment separately."""

    def __init__(self, observations: Path):
        self.root = Path(observations).resolve()
        codec_path = Path(codec_module.__file__).resolve()
        if _sha(codec_path) != codec_module.CODEC_SOURCE_SHA256:
            raise ValueError("DeepFlow codec source changed after import")
        self._accounting: dict[tuple[Any, ...], list[dict[str, Any]]] | None = None
        self._accounting_proof: dict[str, Any] | None = None
        self._raw_proofs: dict[str, dict[str, Any]] = {}
        self._snapshot_cache: dict[Path, tuple[dict[str, Any], dict[str, Any]]] = {}

    def _load_accounting(self, reference: str) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
        if reference != "deepflow-codec-accounting.jsonl":
            raise ValueError("unsupported DeepFlow codec accounting reference")
        if self._accounting is not None:
            return self._accounting
        path = _inside(self.root, reference)
        raw = path.read_bytes()
        index: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
        for line in raw.splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            locator = {name: row.get(name) for name in _LOCATOR_FIELDS}
            index.setdefault(_key(locator), []).append(row)
        self._accounting = index
        self._accounting_proof = {
            "path": reference, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        return index

    def _raw_proof(self, locator: dict[str, Any], node: str) -> tuple[Path, dict[str, Any]]:
        retained = locator["retained_file"]
        parts = PurePosixPath(retained).parts
        if len(parts) < 4 or parts[0] != "deepflow-raw" or parts[1] != f"node-{node}":
            raise ValueError("DeepFlow raw locator is outside its declared guest subtree")
        path = _inside(self.root, retained)
        proof = self._raw_proofs.get(retained)
        if proof is not None:
            return path, proof
        snapshot_path = (path.parent / "snapshot.json").resolve()
        try:
            snapshot_path.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("DeepFlow snapshot escapes observations") from exc
        cached_snapshot = self._snapshot_cache.get(snapshot_path)
        if cached_snapshot is None:
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            snapshot_proof = {
                "snapshot_path": snapshot_path.relative_to(self.root).as_posix(),
                "snapshot_bytes": snapshot_path.stat().st_size,
                "snapshot_sha256": _sha(snapshot_path),
            }
            self._snapshot_cache[snapshot_path] = (snapshot, snapshot_proof)
        else:
            snapshot, snapshot_proof = cached_snapshot
        declarations = [row for row in snapshot.get("files", [])
                        if row.get("snapshot_name") == path.name]
        if len(declarations) != 1:
            raise ValueError("DeepFlow snapshot does not uniquely declare retained raw file")
        declaration = declarations[0]
        raw_bytes, raw_sha = path.stat().st_size, _sha(path)
        if (declaration.get("copied_bytes") != raw_bytes
                or declaration.get("copied_sha256") != raw_sha):
            raise ValueError("DeepFlow snapshot does not bind retained raw file")
        proof = {
            "path": retained, "bytes": raw_bytes, "sha256": raw_sha,
            **snapshot_proof,
        }
        self._raw_proofs[retained] = proof
        return path, proof

    def validate(self, document: dict[str, Any], wrapper: Path, raw_line: bytes) -> dict[str, Any]:
        declaration = document.get("derived_otlp")
        source = document.get("source")
        node = source.split(":", 1)[1] if isinstance(source, str) and source.startswith(
            "ebpf-deepflow:") else None
        if node not in {"a", "b"}:
            raise ValueError("DeepFlow derived OTLP source is not one declared guest")
        expected_declaration = _envelope([], node)["derived_otlp"]
        if declaration != expected_declaration:
            raise ValueError("DeepFlow derived OTLP declaration differs from pinned codec")
        accounting = self._load_accounting(declaration["accounting_ref"])
        payload = document.get("payload")
        resources = payload.get("resourceSpans") if isinstance(payload, dict) else None
        if not isinstance(resources, list) or len(resources) != 1:
            raise ValueError("DeepFlow derived OTLP envelope has unexpected resources")
        scopes = resources[0].get("scopeSpans")
        if not isinstance(scopes, list) or len(scopes) != 1:
            raise ValueError("DeepFlow derived OTLP envelope has unexpected scopes")
        spans = scopes[0].get("spans")
        if not isinstance(spans, list) or not spans:
            raise ValueError("DeepFlow derived OTLP envelope has no observations")

        expected_spans, locators, dependencies = [], [], {}
        for span in spans:
            locator = _locator(span)
            if not locator["source_file"].startswith(f"{node}/"):
                raise ValueError("DeepFlow raw source locator differs from declared guest")
            matches = [row for row in accounting.get(_key(locator), [])
                       if row.get("status") == "normalized"]
            if len(matches) != 1:
                raise ValueError("DeepFlow raw locator lacks unique normalized codec accounting")
            saved_accounting = matches[0]
            path, dependency = self._raw_proof(locator, node)
            dependencies[locator["retained_file"]] = dependency
            with path.open("rb") as stream:
                stream.seek(locator["offset"])
                raw = stream.read(locator["length"])
            if (len(raw) != locator["length"]
                    or hashlib.sha256(raw).hexdigest() != locator["sha256"]):
                raise ValueError("DeepFlow retained raw segment differs from locator")
            runtime = saved_accounting.get("_runtime_identity") or {}
            guest_context = {key: runtime[key] for key in ("boot_id", "pid_namespace")
                             if isinstance(runtime.get(key), str) and runtime[key]}
            expected_span, expected_accounting = normalize_record(
                RawRecord(**locator, raw=raw), node=node, guest_context=guest_context,
            )
            if expected_span is None or any(
                saved_accounting.get(key) != value
                for key, value in expected_accounting.items()
            ):
                raise ValueError("DeepFlow saved accounting differs from deterministic codec")
            expected_spans.append(expected_span)
            locators.append(locator)
        if document != _envelope(expected_spans, node):
            raise ValueError("DeepFlow derived OTLP envelope differs from deterministic codec")
        locator_bytes = json.dumps(
            locators, sort_keys=True, separators=(",", ":")
        ).encode()
        return {
            "schema_version": "deepflow-derived-otlp-export-proof-v5",
            "representation": "derived_otlp_json",
            "original_agent_wire": False,
            "deterministic_envelope_equal": True,
            "ids_invented": False,
            "wrapper_file": str(Path(wrapper).resolve()),
            "wrapper_record_sha256": hashlib.sha256(raw_line).hexdigest(),
            "observations": len(spans),
            "locators_sha256": hashlib.sha256(locator_bytes).hexdigest(),
            "codec": declaration,
            "codec_accounting": dict(self._accounting_proof or {}),
            "raw_dependencies": [dependencies[key] for key in sorted(dependencies)],
        }
