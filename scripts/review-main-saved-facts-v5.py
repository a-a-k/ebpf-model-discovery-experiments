"""Verify saved main-review facts without replay, fitting, scoring, or admission."""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import yaml

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest


PINS = {
    "procrustes": "9648ae3fe9ef24725e665d008c79d0681ce40f85",
    "bering": "70d4145d3e26f11d8b3fb5be8917c50c1c6d8c2a",
    "sheaft": "686a602f4e7b71f3612f1810885e29dd66c8733a",
}

COLLECTOR_PINS = {
    "obi": {
        "source_version": "v0.15.2",
        "image": "otel/ebpf-instrument:v0.15.2@sha256:101b5c773ac84545cac007ce3dbaf38bfb0e7091f26e813c08d649f35dca253e",
    },
    "coroot": {
        "source_version": "1.37.0",
        "source_commit": "89a858a0ee35c4eb938b86d56f23168fb0ac7573",
        "image": "ghcr.io/coroot/coroot-node-agent:1.37.0@sha256:f360c31c5e2fa75550c0029f3c02a0e54b83831bae59201b9fe76bab2fe564b4",
    },
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _safe(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name and "\\" not in name and not path.is_absolute() and ".." not in path.parts)


def _package_selected(name: str, kind: str) -> bool:
    if kind == "handoff":
        # The historical DSB review retains the complete small handoff (35 files),
        # including parent/import/index and worker identity/provenance records.
        return True
    if name in ("execution-summary.json", "forecasts.json", "static-inputs.json",
                "classes/classes-model.json", "classes/classes-family-model.json"):
        return True
    if name.startswith("inputs/") and name.endswith("/observations.json"):
        return True
    if name.startswith("discovery/"):
        return name.endswith(("observed.json", "observed.bering-raw.json",
                              "observed.supplied-aliases.json", "observed.snapshot.json",
                              "replay-command.json", "observations.json"))
    if name.startswith("procrustes/") and "/0/" in name:
        return name.endswith(("preflight.command.json", "report.json"))
    parts = name.split("/")
    return (len(parts) == 4 and parts[0] in ("ebpf", "native", "combined")
            and parts[1] in ("raw", "network_scope")
            and parts[-1] in ("binding.json", "forecast.json",
                              "simulation.command.json", "model.json"))


def verify_package(package: Path, selected: Path, *, kind: str,
                   freeze: dict | None = None) -> dict:
    transport = read(package / "transport.json")
    if transport.get("kind") != kind:
        raise ValueError("typed package kind differs from declared role")
    manifest_path = package / "payload.manifest.jsonl"
    archive = package / "payload.tar.gz"
    if (archive.stat().st_size != transport["archive_bytes"]
            or sha(archive) != transport["archive_sha256"]
            or sha(manifest_path) != transport["manifest_sha256"]):
        raise ValueError("typed package transport differs from its manifest")
    rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines()]
    expected = {row["path"]: row for row in rows if row["type"] == "file"}
    seen: set[str] = set()
    copied = []
    frozen = []
    nonfrozen = []
    total = 0
    selected.mkdir(parents=True, exist_ok=True)
    with gzip.open(archive, "rb") as raw:
        with tarfile.open(fileobj=raw, mode="r|") as bundle:
            for member in bundle:
                name = member.name
                if not _safe(name):
                    raise ValueError("unsafe typed package member")
                if member.isdir():
                    continue
                if not member.isfile() or name not in expected or name in seen:
                    raise ValueError(f"unexpected typed package member: {name}")
                claim = expected[name]
                digest = hashlib.sha256()
                size = 0
                target = selected / PurePosixPath(name)
                output = None
                if _package_selected(name, kind):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    output = target.open("wb")
                try:
                    source = bundle.extractfile(member)
                    if source is None:
                        raise ValueError("typed package file has no body")
                    with source:
                        while chunk := source.read(1024 * 1024):
                            digest.update(chunk)
                            size += len(chunk)
                            if output:
                                output.write(chunk)
                finally:
                    if output:
                        output.close()
                if size != member.size or size != claim["bytes"] or digest.hexdigest() != claim["sha256"]:
                    raise ValueError(f"typed package member differs: {name}")
                seen.add(name)
                total += size
                freeze_key = "toolchain/" + name
                if freeze is not None and freeze_key in freeze:
                    if digest.hexdigest() != freeze[freeze_key]:
                        raise ValueError(f"typed package differs from pre-target freeze: {name}")
                    frozen.append(freeze_key)
                else:
                    nonfrozen.append(freeze_key)
                if output:
                    copied.append({"path": name, "bytes": size, "sha256": digest.hexdigest()})
        while raw.read(1024 * 1024):
            pass
    if seen != set(expected):
        raise ValueError("typed package did not contain every declared file")
    return {
        "archive_bytes": archive.stat().st_size, "archive_sha256": sha(archive),
        "manifest_sha256": sha(manifest_path), "all_files_verified": len(seen),
        "uncompressed_file_bytes_verified": total, "selected_files": copied,
        "frozen_file_hashes_matched": len(frozen),
        "not_in_pre_target_freeze": nonfrozen,
        "scientific_processing_performed": False,
        "_file_claims": {name: {"bytes": row["bytes"], "sha256": row["sha256"]}
                         for name, row in expected.items()},
    }


def verify_worker_output_claims(manifest_claims: dict, provenance_claims: dict,
                                package_claims: dict, toolchain: Path,
                                freeze: dict | None) -> dict:
    if manifest_claims != provenance_claims:
        raise ValueError("worker output manifest and provenance toolchain claims differ")
    if package_claims:
        for name, claim in manifest_claims.items():
            if package_claims.get(name) != {
                    "bytes": claim["bytes"], "sha256": claim["sha256"]}:
                raise ValueError(f"worker output claim differs from typed package: {name}")
        return {"scope": "complete_typed_toolchain_package",
                "verified_claims": len(manifest_claims), "unselected_claims": []}
    verified = []
    unselected = []
    frozen = (freeze or {}).get("sha256_by_path") or {}
    for name, claim in manifest_claims.items():
        path = toolchain / name
        if not path.is_file():
            unselected.append(name)
            continue
        if (path.stat().st_size != claim["bytes"] or sha(path) != claim["sha256"]
                or frozen.get("toolchain/" + name) != claim["sha256"]):
            raise ValueError(f"selected untyped worker output differs: {name}")
        verified.append(name)
    if not verified:
        raise ValueError("untyped worker evidence has no selected frozen output claims")
    return {"scope": "selected_untyped_outputs_only",
            "verified_claims": len(verified),
            "verified_selected_paths": sorted(verified),
            "unselected_claims": sorted(unselected),
            "whole_worker_tree_verified": False}


def compact_facts(root: Path, declaration: dict) -> tuple[dict, dict, dict]:
    manifest = read(root / "evaluation-manifest.json")
    status = read(root / "status.json")
    evaluation = read(root / "evaluation-v5.json")
    identity = (status.get("collector"), status.get("system"), status.get("mode"),
                status.get("seed"), int(status.get("run_id")))
    expected = (declaration["collector"], declaration["system"], declaration["mode"],
                declaration["seed"], declaration["run_id"])
    if identity != expected or status.get("commit") != declaration["head_sha"]:
        raise ValueError(f"saved compact identity differs: {identity!r}")
    if (manifest.get("commit") != declaration["head_sha"]
            or manifest.get("run_id") != str(declaration["run_id"])):
        raise ValueError("evaluation manifest source differs from declaration")
    missing = []
    verified = []
    for name, digest in (manifest.get("files_sha256") or {}).items():
        path = root / name
        if not path.is_file():
            if name == "attempt-journal.jsonl":
                missing.append(name)
                continue
            raise ValueError(f"manifest-declared selected compact member missing: {name}")
        if digest is not None and sha(path) != digest:
            raise ValueError(f"compact member hash differs: {name}")
        verified.append(name)
    counts = evaluation.get("counts") or {}
    expected_blocks = 19 if declaration["system"] == "otel_demo" else 16
    if (counts.get("primary") != 34800 or counts.get("target") != 9600
            or counts.get("blocks") != expected_blocks):
        raise ValueError("fixed workload count identity differs")
    if not (evaluation.get("integrity", {}).get("valid")
            and evaluation.get("completeness", {}).get("valid")
            and evaluation.get("complete_for_evaluation")):
        raise ValueError("saved evaluation integrity/completeness is not valid")
    acquisition = evaluation.get("acquisition") or {}
    if not acquisition.get("valid") or acquisition.get("problems"):
        raise ValueError("saved acquisition is not technically valid")
    blocks = json.loads((root / "blocks.json").read_text(encoding="utf-8"))
    targets = [row["started_ns"] for row in blocks if row.get("phase") == "target"]
    if not targets:
        raise ValueError("saved blocks contain no target phase")
    facts = {
        "identity": dict(zip(("collector", "system", "mode", "seed", "run_id"), identity)),
        "manifest_members_verified": sorted(verified),
        "nonmaterialized_members": missing,
        "counts": counts, "acquisition": acquisition,
        "first_target_started_ns": min(targets),
        "evaluations_copied_not_recomputed": evaluation.get("evaluations"),
        "manual_baselines_copied_not_recomputed": evaluation.get("manual_baselines"),
        "cost_copied_not_recomputed": evaluation.get("cost"),
    }
    return facts, evaluation, read(root / "freeze-integrity.json")


def _selected_proof(root: Path, declaration: dict) -> dict:
    proof = read(root / "selected-transport-proof.json")
    artifact = proof.get("artifact") or {}
    workflow = artifact.get("workflow_run") or {}
    expected_name = declaration["compact_artifact_name"].replace("v5-summary-", "campaign-v5-", 1)
    if (proof.get("complete") is not True or proof.get("scientific_processing_performed") is not False
            or artifact.get("name") != expected_name or artifact.get("expired") is not False
            or workflow.get("id") != declaration["run_id"]
            or workflow.get("head_sha") != declaration["head_sha"]):
        raise ValueError("selected evidence transport identity/integrity differs")
    if "full_artifact_id" in declaration and {
            "id": artifact.get("id"), "name": artifact.get("name"),
            "size_in_bytes": artifact.get("size_in_bytes"),
            "digest": artifact.get("digest")} != {
                "id": declaration["full_artifact_id"],
                "name": declaration["full_artifact_name"],
                "size_in_bytes": declaration["full_artifact_bytes"],
                "digest": declaration["full_artifact_digest"]}:
        raise ValueError("selected full artifact differs from fixed qualification declaration")
    for name, claim in (proof.get("files") or {}).items():
        path = root / name
        if (not path.is_file() or path.stat().st_size != claim["bytes"]
                or sha(path) != claim["sha256"]):
            raise ValueError(f"selected evidence file differs: {name}")
    return proof


def native_mode_facts(root: Path, declaration: dict,
                      evaluation: dict | None = None) -> dict:
    facts = {}
    for stage in ("training", "final"):
        if declaration["system"] == "deathstarbench":
            manifest_path = root / f"native/{stage}/manifest.json"
            manifest = read(manifest_path)
            provenance = manifest.get("audit_self_trace_provenance") or {}
            if (manifest.get("mode") != declaration["mode"] or manifest.get("errors")
                    or provenance.get("excluded_service_exact_match") != "jaeger-all-in-one"
                    or provenance.get("raw_responses_retained") is not True
                    or not isinstance(manifest.get("application_trace_count"), int)
                    or not isinstance(manifest.get("audit_self_trace_count"), int)
                    or (declaration["mode"] == "absent"
                        and (manifest.get("absence_verified") is not True
                             or manifest.get("application_trace_count") != 0))):
                raise ValueError(f"DSB native {stage} manifest contradicts trace audit policy")
            facts[stage] = {
                "manifest_sha256": sha(manifest_path),
                "application_trace_count": manifest["application_trace_count"],
                "audit_self_trace_count": manifest["audit_self_trace_count"],
                "absence_verified": manifest.get("absence_verified"),
                "audit_self_trace_provenance": provenance}
        else:
            metadata_path = root / f"native/{stage}/native-metadata.json"
            if metadata_path.is_file():
                metadata = read(metadata_path)
                census = metadata.get("actual_census") or {}
                compliance = metadata.get("mode_compliance") or {}
                if (metadata.get("mode") != declaration["mode"]
                        or census.get("malformed_records") != 0
                        or compliance.get("compliant") is False
                        or (declaration["mode"] == "absent" and census.get("spans") != 0)):
                    raise ValueError(f"native {stage} census contradicts rendered tracing mode")
                facts[stage] = {
                    "schema": "native-metadata", "metadata_sha256": sha(metadata_path),
                    "actual_census": census, "mode_compliance": compliance}
                continue
            suppression_path = root / f"native/{stage}/native-suppression-verification.json"
            suppression = read(suppression_path)
            absent_nonzero = declaration["mode"] == "absent" and any(
                suppression.get(key) != 0 for key in (
                    "exporter_records", "span_markers", "trace_file_bytes"))
            if (suppression.get("mode") != declaration["mode"]
                    or suppression.get("malformed_records") != 0
                    or suppression.get("mode_compliant") is False
                    or absent_nonzero):
                raise ValueError(
                    f"native {stage} suppression audit contradicts rendered tracing mode")
            facts[stage] = {
                "schema": "native-suppression-verification",
                "suppression_sha256": sha(suppression_path),
                "saved_audit": suppression}
    if (declaration["system"] != "deathstarbench"
            and declaration["mode"] == "absent" and evaluation is not None
            and (evaluation.get("acquisition") or {}).get("native_observations_by_service")):
        raise ValueError("absent mode compact records native observations")
    return facts


def validate_otel_demo_sdk_settings(settings: dict[str, str | None], mode: str) -> list[str]:
    invalid = {service: value for service, value in settings.items()
               if value not in (None, "true", "false")}
    if invalid:
        raise ValueError("rendered OTel SDK configuration has invalid disable values")
    enabled_by_default = {service for service, value in settings.items() if value == "true"}
    if mode == "absent":
        expected = set(settings) - {"otel-collector", "product-catalog"}
    elif mode == "partial":
        expected = {"product-catalog-a", "product-catalog-b"}
    elif mode == "full":
        expected = set()
    else:
        raise ValueError("unknown rendered OTel tracing mode")
    if enabled_by_default != expected:
        raise ValueError("rendered SDK configuration differs from declared mode")
    return sorted(value for value in settings.values() if value is not None)


def full_facts(root: Path, declaration: dict, freeze: dict | None,
               evaluation: dict | None, package_out: Path) -> dict:
    proof = _selected_proof(root, declaration)
    toolchain = root / "toolchain"
    packages = {}
    typed = root / "toolchain-package"
    if typed.is_dir() and (typed / "payload.tar.gz").is_file():
        toolchain = package_out / "toolchain"
        packages["toolchain"] = verify_package(
            typed, toolchain, kind="toolchain",
            freeze=(freeze or {}).get("sha256_by_path"))
    handoff = root / "infrastructure/handoff-package"
    handoff_selected = package_out / "handoff"
    if handoff.is_dir() and (handoff / "payload.tar.gz").is_file():
        packages["handoff"] = verify_package(
            handoff, handoff_selected, kind="handoff")

    saved = read(root / "forecast-saved.json")
    if freeze is not None:
        if not freeze.get("all_unchanged") or saved.get("sha256_by_path") != freeze.get("sha256_by_path"):
            raise ValueError("saved forecast and freeze maps differ")
        for name, claim in (proof.get("files") or {}).items():
            if name in freeze["sha256_by_path"] and claim["sha256"] != freeze["sha256_by_path"][name]:
                raise ValueError(f"selected full evidence differs from pre-target freeze: {name}")
    build = read(root / "toolchain-build/toolchain-build.json")
    pins = {row["name"]: row["commit"] for row in build.get("binaries") or []}
    if pins != PINS:
        raise ValueError("saved toolchain source pins differ")
    graphs = []
    for replay_path in sorted(toolchain.glob("discovery/*/*/observed-runtime/replay-command.json")):
        replay = read(replay_path)
        if replay.get("returncode") != 0 or replay.get("status") != "complete":
            raise ValueError("saved Bering replay did not complete")
        relative = replay_path.relative_to(toolchain)
        source, variant = relative.parts[1], relative.parts[2]
        observations = read(toolchain / "inputs" / source / variant / "observations.json")
        accepted = replay.get("accepted_ingest_requests") or []
        exports = observations.get("exports") or []
        ingest = replay.get("ingest") or {}
        observed_path = replay_path.parent.parent / "observed.json"
        snapshot_path = replay_path.parent.parent / "observed.snapshot.json"
        raw_model_path = replay_path.parent.parent / "observed.bering-raw.json"
        snapshot = read(snapshot_path)
        observed = read(observed_path)
        source_model = read(raw_model_path) if raw_model_path.is_file() else observed
        if (replay.get("source_profile") != {
                "source_id": "ebpf", "input_type": "ebpf-otlp"}
                or not replay.get("source_domain")
                or replay.get("clock_admission_filter") is not False
                or ingest.get("spans") != observations.get("observations")
                or ingest.get("dropped_spans") != 0 or ingest.get("late_spans") != 0
                or len(accepted) != len(exports)
                or snapshot.get("model") != source_model):
            raise ValueError("Bering source/input/ingest/model binding differs")
        for export, request in zip(exports, accepted, strict=True):
            if export.get("sha256") != request.get("content_sha256") or request.get("http_status") != 200:
                raise ValueError("Bering accepted request differs from saved input")
            relative_export = "toolchain/" + export["path"].split("/toolchain/", 1)[1]
            if freeze is not None and freeze["sha256_by_path"].get(relative_export) != export["sha256"]:
                raise ValueError("Bering accepted export is not the frozen source input")
        graphs.append({"source": source, "variant": variant,
                       "source_domain": replay.get("source_domain"),
                       "source_profile": replay.get("source_profile"),
                       "ingest": ingest, "accepted_inputs": len(accepted),
                       "observed_model_sha256": sha(observed_path),
                       "snapshot_sha256": sha(snapshot_path)})
    if not graphs:
        raise ValueError("selected evidence contains no actual Bering execution")

    preflights = []
    for command_path in sorted(toolchain.glob("procrustes/*/*/0/preflight.command.json")):
        command = read(command_path)
        source = command_path.relative_to(toolchain).parts[1]
        argv = command.get("argv") or []
        has_neutral_source = any(
            argv[index:index + 2] == ["--collection-source", "ebpf-otlp"]
            for index in range(max(0, len(argv) - 1)))
        if (command.get("returncode") != 0
                or (source == "native" and has_neutral_source)
                or (source != "native" and not has_neutral_source)):
            raise ValueError("saved Procrustes preflight failed")
        preflights.append(command_path.relative_to(toolchain).as_posix())
    if not preflights:
        raise ValueError("selected evidence contains no actual Procrustes preflight")

    alias_facts = None
    if declaration["collector"] == "coroot":
        table_path = root / "runtime-identity-v5/supplied-service-aliases-training.json"
        admission_path = root / "runtime-identity-v5/supplied-service-alias-admission-training.json"
        table_sha = sha(table_path)
        admission = read(admission_path)
        if (admission.get("conflicts") or admission.get("physical_identity_inferred")
                or admission.get("same_table_all_sources_and_direct_baseline") is not True):
            raise ValueError("supplied logical alias admission exceeds its reviewed boundary")
        projected_models = []
        for alias_path in sorted(toolchain.glob(
                "discovery/*/*/observed.supplied-aliases.json")):
            alias = read(alias_path)
            directory = alias_path.parent
            raw = read(directory / "observed.bering-raw.json")
            effective = read(directory / "observed.json")
            if (alias.get("raw_model_sha256") != sha(directory / "observed.bering-raw.json")
                    or alias.get("table_sha256") != table_sha
                    or alias.get("metadata_collisions")
                    or alias.get("graph_edges_injected")
                    or alias.get("physical_identity_inferred")
                    or alias.get("roles_or_endpoints_created")):
                raise ValueError("saved Coroot alias proof exceeds exact logical renaming")
            projected = copy.deepcopy(raw)
            aliases = alias.get("effective_aliases") or {}
            by_id = {}
            for service in projected.get("services") or []:
                old = service["id"]
                service["id"] = aliases.get(old, old)
                if service.get("name") == old:
                    service["name"] = service["id"]
                if service["id"] in by_id and by_id[service["id"]] != service:
                    raise ValueError("saved Coroot alias collision has differing metadata")
                by_id[service["id"]] = service
            projected["services"] = [by_id[key] for key in sorted(by_id)]
            for edge in projected.get("edges") or []:
                for key in ("from", "to"):
                    edge[key] = aliases.get(edge.get(key), edge.get(key))
            for endpoint in projected.get("endpoints") or []:
                endpoint["entry_service"] = aliases.get(
                    endpoint.get("entry_service"), endpoint.get("entry_service"))
            if projected != effective:
                raise ValueError("saved Coroot semantic model is not exact alias-only projection")
            projected_models.append(alias_path.relative_to(toolchain).as_posix())
        if not projected_models:
            raise ValueError("Coroot evidence contains no supplied-alias graph proof")
        alias_facts = {"table_sha256": table_sha, "admission_sha256": sha(admission_path),
                       "exact_alias_only_models": projected_models}

    branch_facts = []
    forecasts_path = toolchain / "forecasts.json"
    forecasts = read(forecasts_path) if forecasts_path.is_file() else None
    if forecasts is not None:
        evaluation_list = ((evaluation or {}).get("evaluations") or [])
        evaluation_rows = {(row["source"], row["variant"], row["operation"]): row
                           for row in evaluation_list}
        if len(evaluation_rows) != len(evaluation_list):
            raise ValueError("saved evaluation contains duplicate branch keys")
        forecast_keys = {
            (source, variant, operation)
            for source, variants in forecasts.items()
            for variant, operations in variants.items()
            for operation in operations}
        if evaluation is not None and forecast_keys != set(evaluation_rows):
            raise ValueError("saved forecast and evaluation branch-key coverage differs")
        for source, variants in forecasts.items():
            for variant, operations in variants.items():
                for operation, saved_row in operations.items():
                    row = evaluation_rows.get((source, variant, operation))
                    if evaluation is not None and row is None:
                        raise ValueError(
                            f"saved forecast has no evaluation row: {source}/{variant}/{operation}")
                    if row is not None:
                        for key in ("available", "reason", "prediction", "interval"):
                            evaluation_key = "forecast_interval" if key == "interval" else key
                            if row.get(evaluation_key) != saved_row.get(key):
                                raise ValueError(
                                    "saved forecast/evaluation field differs: "
                                    f"{source}/{variant}/{operation}/{key}")
                    branch = toolchain / source / variant / operation
                    command_path = branch / "simulation.command.json"
                    model_path = branch / "model.json"
                    command = read(command_path) if command_path.is_file() else None
                    if saved_row.get("available"):
                        if (command is None or command.get("returncode") != 0
                                or not model_path.is_file()):
                            raise ValueError(
                                "available saved branch lacks successful Sheaft command/model")
                        graph_sha = (row.get("graph_sha256") if row is not None
                                     else saved_row.get("graph_sha256"))
                        if graph_sha and sha(model_path) != graph_sha:
                            raise ValueError(
                                "available Sheaft model hash differs from saved forecast")
                        for path in (command_path, model_path):
                            freeze_key = "toolchain/" + path.relative_to(toolchain).as_posix()
                            if (freeze is not None
                                    and freeze["sha256_by_path"].get(freeze_key) != sha(path)):
                                raise ValueError("available Sheaft input is not frozen")
                        graph_path = toolchain / "discovery" / source / variant / "observed.json"
                        graph = read(graph_path)
                        model = read(model_path)
                        graph_edges = {item["id"] for item in graph.get("edges") or []}
                        graph_endpoints = {item["id"] for item in graph.get("endpoints") or []}
                        model_edges = {item["id"] for item in model.get("edges") or []}
                        model_endpoints = {item["id"] for item in model.get("endpoints") or []}
                        if not model_edges.issubset(graph_edges) or not model_endpoints.issubset(graph_endpoints):
                            raise ValueError("Sheaft model contains unobserved graph identities")
                    branch_facts.append({
                        "source": source, "variant": variant, "operation": operation,
                        "available_copied": saved_row.get("available"),
                        "reason_copied": saved_row.get("reason"),
                        "prediction_copied": saved_row.get("prediction"),
                        "saved_command_present": command is not None,
                        "saved_command_returncode": command.get("returncode") if command else None,
                        "saved_model_present": model_path.is_file(),
                        "observed_edge_ids_retained": (
                            sorted(model_edges) if saved_row.get("available") else None),
                        "observed_endpoint_ids_retained": (
                            sorted(model_endpoints) if saved_row.get("available") else None),
                    })
    else:
        raise ValueError("selected evidence lacks saved forecasts")

    drain = read(root / "observations/drain-evidence.json")
    if (not drain.get("technical_complete") or not drain.get("technical_valid")
            or not drain.get("accepted_receiver_bytes_closed_and_hashed")):
        raise ValueError("saved final drain is not technically complete")
    collector = read(root / "observations/collector.json")
    expected_collector = COLLECTOR_PINS[declaration["collector"]]
    if (collector.get("collector") != declaration["collector"]
            or collector.get("technical_valid") is False
            or collector.get("closed_checkpoint") is not True
            or collector.get("nodes") != ["a", "b"]
            or any(collector.get(key) != value for key, value in expected_collector.items())):
        raise ValueError("collector manifest differs from the pinned closed acquisition")
    closures = {}
    for node in ("a", "b", "native"):
        closure = read(root / f"observations/receiver-closed-{node}.json")
        if (closure.get("node") != node or closure.get("saved_bytes_valid") is not True
                or closure.get("in_flight_handlers_joined") is not True
                or closure.get("listening_socket_closed") is not True
                or closure.get("wrapper_json_decode_error_count") != 0
                or closure.get("errors_json_decode_error_count") != 0
                or closure.get("receiver_parse_or_read_failure_count") != 0):
            raise ValueError(f"receiver closure is incomplete: {node}")
        closures[node] = {key: closure.get(key) for key in (
            "saved_bytes_valid", "in_flight_handlers_joined", "listening_socket_closed",
            "wrapper_json_decode_error_count", "errors_json_decode_error_count",
            "receiver_parse_or_read_failure_count")}
    control = read(root / "observations/technical-positive-control.json")
    if (control.get("collector") != declaration["collector"]
            or set(control.get("proofs") or {}) != {"a", "b"}
            or control.get("cleanup_verified") is not True
            or control.get("cleanup_failures")):
        raise ValueError("technical control lacks exact two-node origin/cleanup proof")
    controls = []
    for node, claim in (control.get("proofs") or {}).items():
        body = root / "observations" / claim["raw_ref"]
        if not body.is_file() or sha(body) != claim["raw_sha256"]:
            raise ValueError("selected-agent raw control body differs")
        request = ExportTraceServiceRequest.FromString(body.read_bytes())
        matched = []
        for resource in request.resource_spans:
            resource_attrs = {
                item.key: getattr(item.value, item.value.WhichOneof("value"))
                for item in resource.resource.attributes}
            for scope in resource.scope_spans:
                for span in scope.spans:
                    attrs = {item.key: getattr(item.value, item.value.WhichOneof("value"))
                             for item in span.attributes}
                    if control.get("marker") not in str(attrs) and control.get("marker") not in str(span):
                        continue
                    if declaration["collector"] == "obi":
                        if (resource_attrs.get("telemetry.distro.name")
                                != "opentelemetry-ebpf-instrumentation"
                                or resource_attrs.get("telemetry.distro.version") != "v0.15.2"
                                or (scope.scope.name or resource_attrs.get("otel.scope.name"))
                                != "go.opentelemetry.io/obi"
                                or resource_attrs.get("container.name") not in {
                                    f"study-ebpf-control-server-{node}",
                                    f"study-ebpf-control-client-{node}"}):
                            continue
                    elif declaration["collector"] == "coroot":
                        if (scope.scope.name != "coroot-node-agent" or span.kind != 3
                                or resource_attrs.get("service.name")
                                != f"/docker/study-ebpf-control-client-{node}"):
                            continue
                    matched.append({"scope": scope.scope.name, "span_kind": span.kind,
                                    "service": resource_attrs.get("service.name"),
                                    "container": resource_attrs.get("container.name")})
        if not matched:
            raise ValueError("raw control lacks the selected collector origin")
        controls.append({"node": node, "raw_sha256": claim["raw_sha256"], "matches": matched})
    worker_facts = None
    remote_root = root / "infrastructure/remote-toolchain-v4"
    if not (remote_root / "parent-import.json").is_file() and handoff_selected.is_dir():
        remote_root = handoff_selected
    parent_import_path = remote_root / "parent-import.json"
    worker_provenance_path = remote_root / "worker/worker-provenance.json"
    worker_status_path = remote_root / "worker/worker-status.json"
    if parent_import_path.is_file():
        parent_import = read(parent_import_path)
        worker_provenance = read(worker_provenance_path)
        worker_status = read(worker_status_path)
        output_manifest = read(remote_root / "worker/output-manifest.json")
        index = read(remote_root / "training-index-proof.json")
        identities = [parent_import.get("identity") or {},
                      worker_provenance.get("identity") or {},
                      worker_status.get("identity") or {},
                      output_manifest.get("identity") or {}]
        for identity in identities:
            if (str(identity.get("run_id")) != str(declaration["run_id"])
                    or identity.get("system") != declaration["system"]
                    or identity.get("mode") != declaration["mode"]
                    or int(identity.get("seed")) != declaration["seed"]
                    or identity.get("commit") != declaration["head_sha"]):
                raise ValueError("saved worker/handoff identity differs from declared cell")
        if (parent_import.get("downloaded_archive_sha256")
                != str(parent_import.get("worker_artifact_digest", "")).removeprefix("sha256:")
                or worker_status.get("status") != "complete"
                or worker_status.get("checkpoint_unchanged") is not True
                or worker_provenance.get("checkpoint_unchanged") is not True
                or worker_status.get("new_application_traffic") is not False
                or worker_provenance.get("new_application_traffic") is not False
                or str(parent_import.get("worker_run_id"))
                    != str(worker_provenance.get("worker_run_id"))
                or str(parent_import.get("worker_run_id"))
                    != str(worker_status["identity"].get("worker_run_id"))
                or index.get("checkpoint") != index.get("parent_before_dispatch")
                or index.get("checkpoint") != index.get("parent_after_worker")):
            raise ValueError("saved worker import/status identity is incomplete")
        manifest_claims = output_manifest.get("toolchain_files") or {}
        package_claims = (packages.get("toolchain") or {}).get("_file_claims") or {}
        worker_freeze = freeze if freeze is not None else {
            "sha256_by_path": saved.get("sha256_by_path") or {}}
        output_claim_scope = verify_worker_output_claims(
            manifest_claims, worker_provenance.get("toolchain_files") or {},
            package_claims, toolchain, worker_freeze)
        output_claim_scope["freeze_map_binding"] = (
            "compact_freeze_equals_forecast_saved_and_selected_claims_match"
            if freeze is not None else
            "selected_claims_match_forecast_saved; compact_freeze_comparison_external_pending")
        worker_facts = {"parent_import": parent_import,
                        "worker_provenance": worker_provenance,
                        "worker_status": worker_status,
                        "output_manifest": output_manifest,
                        "training_index_proof": index,
                        "output_claim_scope": output_claim_scope}
    if declaration["system"] == "deathstarbench" and worker_facts is None:
        raise ValueError("DSB evidence lacks the required remote worker/handoff proof")
    for package in packages.values():
        package.pop("_file_claims", None)
    mode_files = {}
    sdk_flags = []
    otel_sdk_settings = {}
    for pattern in (
        "deployment/otel_demo/runtime-resolved-node-*.yaml",
        "deployment/petclinic/node-*/compose.yml",
        "deployment/deathstarbench/tracing-mode.json",
        "native/training/native-metadata.json", "native/final/native-metadata.json",
        "native/training/native-suppression-verification.json",
        "native/final/native-suppression-verification.json",
    ):
        for path in sorted(root.glob(pattern)):
            mode_files[path.relative_to(root).as_posix()] = sha(path)
            if path.suffix in (".yaml", ".yml"):
                document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                for name, service in (document.get("services") or {}).items():
                    environment = service.get("environment") or {}
                    value = (str(environment["OTEL_SDK_DISABLED"]).lower()
                             if "OTEL_SDK_DISABLED" in environment else None)
                    if name in otel_sdk_settings and otel_sdk_settings[name] != value:
                        raise ValueError("rendered service has conflicting SDK settings")
                    otel_sdk_settings[name] = value
                    if "OTEL_SDK_DISABLED" in environment:
                        sdk_flags.append(value)
    if declaration["system"] == "deathstarbench":
        tracing = read(root / "deployment/deathstarbench/tracing-mode.json")
        if tracing.get("mode") != declaration["mode"]:
            raise ValueError("DSB rendered tracing mode differs from declaration")
        if declaration["mode"] == "absent" and not all(
                tracing.get(key) is True for key in (
                    "controlled_replica_sdks_disabled", "frontend_sdk_disabled",
                    "ordinary_service_sdks_disabled", "export_is_not_merely_blocked")):
            raise ValueError("DSB absent configuration does not disable native tracing")
    elif declaration["system"] == "otel_demo":
        sdk_flags = validate_otel_demo_sdk_settings(
            otel_sdk_settings, declaration["mode"])
    else:
        if not sdk_flags:
            raise ValueError("rendered deployment lacks explicit OTEL_SDK_DISABLED values")
        expected = declaration["mode"]
        if ((expected == "absent" and set(sdk_flags) != {"true"})
                or (expected == "partial" and set(sdk_flags) != {"true", "false"})
                or (expected == "full" and set(sdk_flags) != {"false"})):
            raise ValueError("rendered SDK configuration differs from declared mode")
    native_facts = native_mode_facts(root, declaration, evaluation)
    return {
        "selected_transport": proof, "typed_packages": packages,
        "source_pins": pins, "saved_mode_evidence_sha256": mode_files,
        "collector_manifest": collector, "receiver_closure_facts": closures,
        "rendered_sdk_disabled_values": sorted(sdk_flags),
        "native_mode_facts": native_facts,
        "supplied_logical_alias_facts": alias_facts,
        "worker_import_facts": worker_facts,
        "forecast_saved_ns": saved.get("saved_ns"), "actual_bering": graphs,
        "actual_procrustes": preflights, "saved_branch_facts": branch_facts,
        "selected_raw_controls": controls, "final_drain": drain,
    }


def review(declaration: dict, compact: Path | None, full: Path | None, out: Path) -> dict:
    if out.exists():
        raise ValueError("review output already exists")
    out.mkdir(parents=True)
    compact_result = evaluation = freeze = None
    if compact is not None:
        compact_result, evaluation, freeze = compact_facts(compact, declaration)
    full_result = None
    if full is not None:
        full_result = full_facts(full, declaration, freeze, evaluation, out / "selected-packages")
        if compact_result is not None and full_result["forecast_saved_ns"] >= compact_result["first_target_started_ns"]:
            raise ValueError("saved forecast does not precede first target block")
    result = {
        "schema_version": "main-saved-evidence-facts-v5",
        "declaration": declaration,
        "compact_facts": compact_result,
        "full_facts": full_result,
        "evidence_status": "automated_saved_fact_checks_complete; independent_family_interpretation_required",
        "automated_domain_checks": {
            "selected_transport_and_hashes": full_result is not None,
            "acquisition_controls_closure_and_collector_pins": full_result is not None,
            "bering_inputs_exports_and_models": full_result is not None,
            "saved_forecast_branch_coverage_and_sheaft_inputs": full_result is not None,
            "rendered_mode_and_native_census_contradictions": full_result is not None,
            "independent_scientific_admission_or_utility": False,
        },
        "independent_admission_performed": False,
        "scientific_processing_performed": False,
        "traffic_replay_refit_rescore_or_metric_performed": False,
        "availability_outcome_or_accuracy_used_as_gate": False,
        "cost_boundary": "saved cell costs copied; Actions transport/verification costs retained separately; human effort unknown",
    }
    (out / "saved-evidence-facts.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--declaration", type=Path, required=True)
    parser.add_argument("--compact", type=Path)
    parser.add_argument("--full", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    declaration = read(args.declaration)
    result = review(declaration, args.compact, args.full, args.out)
    print(json.dumps({"cell": [declaration[key] for key in
                               ("collector", "system", "mode", "seed")],
                      "domains": {"compact": result["compact_facts"] is not None,
                                  "full": result["full_facts"] is not None}}))


if __name__ == "__main__":
    main()
