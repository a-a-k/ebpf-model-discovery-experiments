"""Compact Actions-only technical readout for retained graph-v4 replay outputs.

This is not an evaluator.  It copies already produced execution, graph, binding,
forecast and resource evidence into a small manifest and verifies referenced
observed artifacts.  Missing execution remains explicitly ``not_run``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable


SOURCES = ("ebpf", "native", "combined")
VARIANTS = ("raw", "network_scope")
OBSERVED_FILES = ("observed.json", "observed.signal-quality.json", "observed.snapshot.json")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _command(path: Path, root: Path) -> dict:
    if not path.exists():
        return {"status": "not_run", "path": _relative(path, root)}
    value = _json(path)
    stored_status = value.get("status")
    completed = (value.get("returncode") == 0
                 and (stored_status is None or stored_status == "complete"))
    return {
        "status": "completed" if completed else "technical_error",
        "path": _relative(path, root),
        "returncode": value.get("returncode"),
        "stored_status": stored_status,
        "error": value.get("error"),
        "started_ns": value.get("started_ns"),
        "ended_ns": value.get("ended_ns"),
        "argv": value.get("argv", []),
        "stderr": value.get("stderr", ""),
    }


def _observed_paths(folder: Path, root: Path) -> tuple[dict[str, Path], dict, Path]:
    reference = folder / "observed-reference.json"
    if not reference.exists():
        paths = {name: folder / name for name in OBSERVED_FILES}
        return paths, {"kind": "local", "reference": None}, folder
    value = _json(reference)
    relative = value.get("folder")
    if not isinstance(relative, str) or not relative:
        return {}, {"kind": "reference", "reference": _relative(reference, root),
                    "errors": ["reference_folder_missing"]}, folder
    target = (folder / relative).resolve()
    replay_root = root.resolve()
    try:
        target.relative_to(replay_root)
    except ValueError:
        return {}, {"kind": "reference", "reference": _relative(reference, root),
                    "errors": ["reference_folder_outside_replay_root"]}, folder
    declared = value.get("files")
    if not isinstance(declared, dict):
        return {}, {"kind": "reference", "reference": _relative(reference, root),
                    "errors": ["reference_files_missing"]}, target
    return ({name: target / name for name in OBSERVED_FILES},
            {"kind": "reference", "reference": _relative(reference, root),
             "folder": _relative(target, root), "declared_hashes": declared}, target)


def _observed(folder: Path, root: Path) -> tuple[dict, list[str], Path]:
    paths, provenance, runtime_folder = _observed_paths(folder, root)
    errors = list(provenance.pop("errors", []))
    declared = provenance.pop("declared_hashes", {})
    hashes = {}
    for name in OBSERVED_FILES:
        path = paths.get(name)
        if path is None or not path.is_file():
            errors.append(f"{name}:missing")
            continue
        actual = _digest(path)
        hashes[name] = actual
        if provenance["kind"] == "reference":
            expected = declared.get(name)
            if not isinstance(expected, str):
                errors.append(f"{name}:hash_not_declared")
            elif actual != expected:
                errors.append(f"{name}:sha256_mismatch")
    provenance["verified_sha256"] = hashes
    model_path, quality_path = paths.get("observed.json"), paths.get("observed.signal-quality.json")
    if errors or model_path is None or quality_path is None:
        return {"provenance": provenance}, errors, runtime_folder
    model, quality = _json(model_path), _json(quality_path)
    return {
        "provenance": provenance,
        "counts": quality.get("counts"),
        "services": sorted(str(item.get("id")) for item in model.get("services", []) if item.get("id")),
        "edges": sorted(str(item.get("id")) for item in model.get("edges", []) if item.get("id")),
        "endpoints": sorted(str(item.get("id")) for item in model.get("endpoints", []) if item.get("id")),
        "quality_artifact": quality.get("artifact"),
        "source_mix": quality.get("source_mix"),
        "warnings": quality.get("warnings", []),
    }, errors, runtime_folder


def _entry_evidence(path: Path) -> dict | None:
    if not path.exists():
        return None
    value = _json(path)
    keys = ("source", "binding_reasons", "selection", "includes_descendants",
            "clock_gate", "outcomes_used", "ids_rewritten")
    result = {key: value[key] for key in keys if key in value}
    result["roots_count"] = len(value.get("roots", []))
    return result


def _binding(path: Path) -> dict | None:
    if not path.exists():
        return None
    value = _json(path)
    keys = ("available", "entry_service", "required_edges", "mandatory_targets", "endpoints",
            "unknown", "assumed_satisfied_database_requirements",
            "all_required_database_channels_observed")
    return {key: value[key] for key in keys if key in value}


def _input_reference(folder: Path, root: Path) -> tuple[dict | None, list[str]]:
    path = folder / "input-reference.json"
    if not path.exists():
        return None, []
    value = _json(path)
    errors = []
    relative = value.get("path")
    target = (folder / relative).resolve() if isinstance(relative, str) and relative else None
    manifest_observations = None
    if target is None:
        errors.append("input-reference:path_missing")
    else:
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append("input-reference:path_outside_replay_root")
        if not target.is_file():
            errors.append("input-reference:target_missing")
        elif not isinstance(value.get("sha256"), str):
            errors.append("input-reference:hash_not_declared")
        else:
            if _digest(target) != value["sha256"]:
                errors.append("input-reference:sha256_mismatch")
            try:
                manifest = _json(target)
                manifest_observations = manifest.get("observations") if isinstance(manifest, dict) else None
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                errors.append("input-reference:manifest_invalid_json")
            if manifest_observations != value.get("observations"):
                errors.append("input-reference:observations_mismatch")
    return ({"path": relative, "sha256": value.get("sha256"),
             "observations": value.get("observations"), "shared": value.get("shared"),
             "verified_observations": manifest_observations,
             "verified": not errors}, errors)


def _branch(folder: Path, root: Path) -> dict:
    exists = folder.is_dir()
    result = {"status": "not_run", "folder": _relative(folder, root)}
    if not exists:
        return result
    entry = folder / "entry-evidence.json"
    binding = folder / "binding.json"
    forecast = folder / "forecast.json"
    forecast_value = _json(forecast) if forecast.exists() else None
    input_reference, errors = _input_reference(folder, root)
    no_source = (forecast_value is not None
                 and forecast_value.get("available") is False
                 and forecast_value.get("reason") == "no_frozen_source_observations"
                 and input_reference is not None
                 and input_reference.get("verified_observations") == 0)
    if no_source:
        result.update({
            "status": "technical_error" if errors else "expected_unavailable",
            "input_reference": input_reference,
            "entry_evidence": _entry_evidence(entry),
            "bering": {"status": "not_run", "reason": "no_frozen_source_observations"},
            "observed": None, "binding": None, "forecast": forecast_value,
            "sheaft": {"status": "not_run", "reason": "no_frozen_source_observations"},
            "integrity_errors": errors,
        })
        return result
    observed, observed_errors, runtime_folder = _observed(folder, root)
    errors.extend(observed_errors)
    bering = _command(runtime_folder / "observed-runtime" / "replay-command.json", root)
    sheaft_paths = sorted(folder.rglob("*command.json"))
    sheaft_paths = [path for path in sheaft_paths if "sheaft" in path.name.lower()
                    or "simulation" in path.as_posix().lower()]
    result.update({
        "status": "technical_error" if errors else "completed",
        "input_reference": input_reference,
        "entry_evidence": _entry_evidence(entry),
        "bering": bering,
        "observed": observed,
        "binding": _binding(binding),
        "forecast": forecast_value,
        "sheaft": (_command(sheaft_paths[0], root) if sheaft_paths else {"status": "not_run"}),
        "integrity_errors": errors,
    })
    if bering["status"] != "completed":
        result["status"] = "technical_error"
        result["integrity_errors"].append("bering_execution_not_completed")
    if not binding.exists() or not forecast.exists():
        result["status"] = "technical_error"
        result["integrity_errors"].append("binding_or_forecast_missing")
    if (forecast_value and forecast_value.get("available") is True
            and result["sheaft"]["status"] != "completed"):
        result["status"] = "technical_error"
        result["integrity_errors"].append("sheaft_execution_not_completed")
    return result


def _operations(toolchain: Path, supplied: Iterable[str] | None) -> list[str]:
    if supplied:
        return sorted(set(supplied))
    forecast = toolchain / "forecasts.json"
    names = set()
    if forecast.exists():
        value = _json(forecast)
        for source in value.values():
            for variant in source.values():
                names.update(variant)
    for source in SOURCES:
        for variant in VARIANTS:
            folder = toolchain / source / variant
            if folder.is_dir():
                names.update(item.name for item in folder.iterdir() if item.is_dir())
    return sorted(names)


def _gnu_time(label: str, path: Path, root: Path) -> dict:
    if not path.is_file():
        return {"label": label, "status": "missing", "path": _relative(path, root)}
    raw = path.read_text(encoding="utf-8", errors="replace")
    fields = {}
    for line in raw.splitlines():
        if ": " in line:
            key, value = line.strip().split(": ", 1)
            fields[key] = value
    return {"label": label, "status": "retained", "path": _relative(path, root),
            "sha256": _digest(path), "fields": fields}


def build_readout(replay_dir: Path, *, operations: Iterable[str] | None = None,
                  resources: Iterable[tuple[str, Path]] = ()) -> dict:
    """Build a technical readout from retained outputs without rerunning tools."""
    root = Path(replay_dir).resolve()
    toolchain = root / "toolchain" if (root / "toolchain").is_dir() else root
    names = _operations(toolchain, operations)
    branches = {}
    for source in SOURCES:
        branches[source] = {}
        for variant in VARIANTS:
            branches[source][variant] = {
                operation: _branch(toolchain / source / variant / operation, root)
                for operation in names
            }
    integrity_errors = [f"{source}/{variant}/{operation}:{error}"
        for source in SOURCES for variant in VARIANTS for operation in names
        for error in branches[source][variant][operation].get("integrity_errors", [])]
    return {
        "schema_version": "qualification-readout-v4",
        "kind": "technical retained replay readout; not accuracy or resource qualification",
        "replay_dir": str(root),
        "operations": names,
        "branches": branches,
        "resources": [_gnu_time(label, Path(path), root) for label, path in resources],
        "integrity": {"ok": not integrity_errors, "errors": integrity_errors},
    }


def _resource(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("resource must be LABEL=PATH")
    label, path = value.split("=", 1)
    if not label or not path:
        raise argparse.ArgumentTypeError("resource must be LABEL=PATH")
    return label, Path(path)


def main(argv=None) -> int:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("qualification_readout_v4 CLI is Actions-only")
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--operation", action="append", dest="operations")
    parser.add_argument("--resource", action="append", type=_resource, default=[])
    args = parser.parse_args(argv)
    result = build_readout(args.replay_dir, operations=args.operations, resources=args.resource)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["integrity"]["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
