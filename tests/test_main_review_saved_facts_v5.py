from __future__ import annotations

import hashlib
import importlib.util
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import textwrap

import pytest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest


ROOT = Path(__file__).parents[1]


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


REVIEW = load("review_main_saved_facts_v5", "scripts/review-main-saved-facts-v5.py")
SELECT = load("select_main_review_evidence_v5", "scripts/select-main-review-evidence-v5.py")


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, (dict, list)):
        path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    else:
        path.write_bytes(value)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(tmp_path: Path, *, available: bool = True):
    compact, full = tmp_path / "compact", tmp_path / "full"
    declaration = {
        "collector": "obi", "system": "otel_demo", "mode": "partial", "seed": 6,
        "run_id": 123, "head_sha": "a" * 40,
        "compact_artifact_name": "v5-summary-obi-main-otel_demo-partial-6-123",
    }
    evaluations = [{
        "source": "ebpf", "variant": "raw", "operation": "browse",
        "available": available,
        "reason": None if available else "arbitrary_saved_unknown_reason",
        "prediction": 0.123 if available else None,
        "forecast_interval": [0.12, 0.13] if available else [0, 1],
        "graph_sha256": None,
        "actual_counts": {"success": 17, "failure": 2, "unknown": 1, "total": 20},
    }]
    evaluation = {
        "integrity": {"valid": True}, "completeness": {"valid": True},
        "complete_for_evaluation": True,
        "counts": {"primary": 34800, "target": 9600, "blocks": 19},
        "acquisition": {"valid": True, "problems": [], "final_drain": {
            "technical_complete": True, "technical_valid": True,
            "accepted_receiver_bytes_closed_and_hashed": True}},
        "evaluations": evaluations, "manual_baselines": {"saved": True},
        "cost": {"seconds": 4},
    }
    status = {**{key: declaration[key] for key in ("collector", "system", "mode", "seed")},
              "run_id": "123", "commit": "a" * 40}
    forecasts = {"ebpf": {"raw": {"browse": {
        "available": available, "reason": evaluations[0]["reason"],
        "prediction": evaluations[0]["prediction"],
        "interval": evaluations[0]["forecast_interval"],
    }}}}
    freeze_map = {}
    compact_values = {
        "evaluation-v5.json": evaluation, "status.json": status,
        "plans.json": {}, "census.json": {},
        "blocks.json": [{"phase": "target", "started_ns": 20}],
        "freeze-integrity.json": {"all_unchanged": True, "sha256_by_path": freeze_map},
        "toolchain/forecasts.json": forecasts, "evidence-v4.json": {},
    }
    for name, value in compact_values.items():
        write(compact / name, value)
    manifest_hashes = {name: digest(compact / name) for name in compact_values}
    manifest_hashes["attempt-journal.jsonl"] = "b" * 64
    write(compact / "evaluation-manifest.json", {
        "commit": "a" * 40, "run_id": "123", "files_sha256": manifest_hashes})

    write(full / "forecast-saved.json", {"saved_ns": 10, "sha256_by_path": freeze_map})
    write(full / "toolchain-build/toolchain-build.json", {"binaries": [
        {"name": name, "commit": commit} for name, commit in REVIEW.PINS.items()]})
    write(full / "toolchain/forecasts.json", forecasts)
    write(full / "toolchain/inputs/ebpf/raw/observations.json", {
        "observations": 1, "exports": [{
            "path": "/saved/toolchain/inputs/ebpf/raw/export.pb",
            "sha256": "c" * 64}]})
    write(full / "toolchain/discovery/ebpf/raw/observed-runtime/replay-command.json", {
        "returncode": 0, "status": "complete", "source_domain": "fixture-domain",
        "source_profile": {"source_id": "ebpf", "input_type": "ebpf-otlp"},
        "clock_admission_filter": False,
        "ingest": {"spans": 1, "dropped_spans": 0, "late_spans": 0},
        "accepted_ingest_requests": [{"content_sha256": "c" * 64, "http_status": 200}]})
    observed_model = {"services": [], "edges": [], "endpoints": []}
    write(full / "toolchain/discovery/ebpf/raw/observed.json", observed_model)
    write(full / "toolchain/discovery/ebpf/raw/observed.snapshot.json", {
        "model": observed_model})
    write(full / "toolchain/procrustes/ebpf/browse/0/preflight.command.json", {
        "returncode": 0, "argv": ["procrustes", "--collection-source", "ebpf-otlp"]})
    write(full / "toolchain/procrustes/native/browse/0/preflight.command.json", {
        "returncode": 0, "argv": ["procrustes", "analyze", "--source", "deployment-0=x"]})
    branch = full / "toolchain/ebpf/raw/browse"
    if available:
        write(branch / "simulation.command.json", {"returncode": 0})
        write(branch / "model.json", observed_model)
    write(full / "observations/drain-evidence.json", {
        "technical_complete": True, "technical_valid": True,
        "accepted_receiver_bytes_closed_and_hashed": True})
    write(full / "observations/collector.json", {
        "collector": "obi", "technical_valid": True, "closed_checkpoint": True,
        "nodes": ["a", "b"], **REVIEW.COLLECTOR_PINS["obi"]})
    for node in ("a", "b", "native"):
        write(full / f"observations/receiver-closed-{node}.json", {
            "node": node, "saved_bytes_valid": True,
            "in_flight_handlers_joined": True, "listening_socket_closed": True,
            "wrapper_json_decode_error_count": 0, "errors_json_decode_error_count": 0,
            "receiver_parse_or_read_failure_count": 0})
    write(full / "observations/technical-positive-control.json", {
        "collector": "obi", "marker": "marker-123", "cleanup_verified": True,
        "cleanup_failures": [], "proofs": {}})
    control = json.loads((full / "observations/technical-positive-control.json").read_text())
    for node in ("a", "b"):
        request = ExportTraceServiceRequest()
        resource = request.resource_spans.add()
        for key, value in {
            "telemetry.distro.name": "opentelemetry-ebpf-instrumentation",
            "telemetry.distro.version": "v0.15.2",
            "container.name": f"study-ebpf-control-server-{node}",
        }.items():
            attribute = resource.resource.attributes.add()
            attribute.key = key
            attribute.value.string_value = value
        scoped = resource.scope_spans.add()
        scoped.scope.name = "go.opentelemetry.io/obi"
        span = scoped.spans.add()
        marker_attribute = span.attributes.add()
        marker_attribute.key = "x-experiment-request-id"
        marker_attribute.value.string_value = "marker-123"
        body = full / f"observations/{node}.raw/body.pb"
        write(body, request.SerializeToString())
        control["proofs"][node] = {
            "raw_ref": f"{node}.raw/body.pb", "raw_sha256": digest(body)}
    write(full / "observations/technical-positive-control.json", control)
    write(full / "deployment/otel_demo/runtime-resolved-node-a.yaml", {
        "services": {"frontend": {"environment": {}},
                     "product-catalog-a": {
                         "environment": {"OTEL_SDK_DISABLED": "true"}}}})
    write(full / "deployment/otel_demo/runtime-resolved-node-b.yaml", {
        "services": {"product-catalog-b": {
            "environment": {"OTEL_SDK_DISABLED": "true"}}}})
    for stage in ("training", "final"):
        write(full / f"native/{stage}/native-metadata.json", {
            "mode": "partial", "actual_census": {"malformed_records": 0, "spans": 1},
            "mode_compliance": {"compliant": True}})
    freeze_map.update({
        "toolchain/inputs/ebpf/raw/export.pb": "c" * 64,
        **{f"toolchain/{path.relative_to(full / 'toolchain').as_posix()}": digest(path)
           for path in (branch / "simulation.command.json", branch / "model.json")
           if path.is_file()}})
    worker_claim = {"bytes": (full / "toolchain/forecasts.json").stat().st_size,
                    "sha256": digest(full / "toolchain/forecasts.json")}
    freeze_map["toolchain/forecasts.json"] = worker_claim["sha256"]
    identity = {"run_id": "123", "system": "otel_demo", "mode": "partial",
                "seed": 6, "commit": "a" * 40}
    remote = full / "infrastructure/remote-toolchain-v4"
    write(remote / "parent-import.json", {
        "identity": identity, "worker_run_id": "456",
        "downloaded_archive_sha256": "d" * 64,
        "worker_artifact_digest": "sha256:" + "d" * 64})
    write(remote / "worker/worker-provenance.json", {
        "identity": identity, "worker_run_id": "456",
        "checkpoint_unchanged": True, "new_application_traffic": False,
        "toolchain_files": {"forecasts.json": worker_claim}})
    write(remote / "worker/worker-status.json", {
        "identity": {**identity, "worker_run_id": "456"}, "status": "complete",
        "checkpoint_unchanged": True, "new_application_traffic": False})
    write(remote / "worker/output-manifest.json", {
        "identity": identity, "toolchain_files": {"forecasts.json": worker_claim}})
    write(remote / "training-index-proof.json", {
        "checkpoint": {"sha256": "e" * 64},
        "parent_before_dispatch": {"sha256": "e" * 64},
        "parent_after_worker": {"sha256": "e" * 64}})
    write(compact / "freeze-integrity.json", {
        "all_unchanged": True, "sha256_by_path": freeze_map})
    write(full / "forecast-saved.json", {"saved_ns": 10, "sha256_by_path": freeze_map})
    manifest_hashes["freeze-integrity.json"] = digest(compact / "freeze-integrity.json")
    write(compact / "evaluation-manifest.json", {
        "commit": "a" * 40, "run_id": "123", "files_sha256": manifest_hashes})
    files = {}
    for path in full.rglob("*"):
        if path.is_file():
            files[path.relative_to(full).as_posix()] = {
                "bytes": path.stat().st_size, "sha256": digest(path), "zip_crc32": "00000000"}
    write(full / "selected-transport-proof.json", {
        "complete": True, "scientific_processing_performed": False,
        "artifact": {"name": "campaign-v5-obi-main-otel_demo-partial-6-123",
                     "expired": False,
                     "workflow_run": {"id": 123, "head_sha": "a" * 40}},
        "files": files,
    })
    return declaration, compact, full


@pytest.mark.parametrize("available", [True, False])
def test_saved_availability_is_observed_not_a_fixed_gate(tmp_path: Path, available: bool) -> None:
    declaration, compact, full = fixture(tmp_path, available=available)
    result = REVIEW.review(declaration, compact, full, tmp_path / "out")
    branch = result["full_facts"]["saved_branch_facts"][0]
    assert branch["available_copied"] is available
    assert result["availability_outcome_or_accuracy_used_as_gate"] is False
    assert result["independent_admission_performed"] is False
    assert result["compact_facts"]["evaluations_copied_not_recomputed"][0]["actual_counts"]["success"] == 17


def test_available_saved_branch_requires_actual_sheaft_command_and_model(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path, available=True)
    (full / "toolchain/ebpf/raw/browse/model.json").unlink()
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    proof["files"].pop("toolchain/ebpf/raw/browse/model.json")
    write(full / "selected-transport-proof.json", proof)
    with pytest.raises(ValueError, match="lacks successful Sheaft"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_control_requires_selected_agent_proof_on_both_guests(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    control_path = full / "observations/technical-positive-control.json"
    control = json.loads(control_path.read_text())
    control["proofs"].pop("b")
    write(control_path, control)
    proof_path = full / "selected-transport-proof.json"
    proof = json.loads(proof_path.read_text())
    proof["files"]["observations/technical-positive-control.json"].update(
        bytes=control_path.stat().st_size, sha256=digest(control_path))
    write(proof_path, proof)
    with pytest.raises(ValueError, match="exact two-node"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_unavailable_saved_branch_retains_attempted_command_truthfully(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path, available=False)
    write(full / "toolchain/ebpf/raw/browse/simulation.command.json", {"returncode": 7})
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    path = full / "toolchain/ebpf/raw/browse/simulation.command.json"
    proof["files"][path.relative_to(full).as_posix()] = {
        "bytes": path.stat().st_size, "sha256": digest(path), "zip_crc32": "00000000"}
    write(full / "selected-transport-proof.json", proof)
    result = REVIEW.review(declaration, compact, full, tmp_path / "out")
    assert result["full_facts"]["saved_branch_facts"][0]["saved_command_returncode"] == 7


def test_dsb_native_manifest_uses_application_audit_trace_policy(tmp_path: Path) -> None:
    declaration = {"system": "deathstarbench", "mode": "absent"}
    for stage in ("training", "final"):
        write(tmp_path / f"native/{stage}/manifest.json", {
            "mode": "absent", "errors": [], "absence_verified": True,
            "application_trace_count": 0, "audit_self_trace_count": 1,
            "audit_self_trace_provenance": {
                "excluded_service_exact_match": "jaeger-all-in-one",
                "raw_responses_retained": True}})
    facts = REVIEW.native_mode_facts(tmp_path, declaration, {
        "acquisition": {"native_observations_by_service": {"jaeger-all-in-one": 1}}})
    assert facts["training"]["application_trace_count"] == 0
    assert facts["final"]["audit_self_trace_count"] == 1


def test_older_otel_absent_suppression_audit_shape_is_verified(tmp_path: Path) -> None:
    declaration = {"system": "otel_demo", "mode": "absent"}
    audit = {"mode": "absent", "mode_compliant": True,
             "malformed_records": 0, "exporter_records": 0,
             "span_markers": 0, "trace_file_bytes": 0,
             "trace_file_sha256": hashlib.sha256(b"").hexdigest()}
    for stage in ("training", "final"):
        write(tmp_path / f"native/{stage}/native-suppression-verification.json", audit)
    facts = REVIEW.native_mode_facts(
        tmp_path, declaration,
        {"acquisition": {"native_observations_by_service": {}}})
    assert facts["training"]["schema"] == "native-suppression-verification"
    assert facts["final"]["saved_audit"]["trace_file_bytes"] == 0


def test_otel_rendered_sdk_settings_follow_pinned_adapter_omission_convention() -> None:
    partial = {"frontend": None, "product-catalog": None,
               "product-catalog-a": "true", "product-catalog-b": "true"}
    assert REVIEW.validate_otel_demo_sdk_settings(partial, "partial") == ["true", "true"]
    full = {service: None for service in partial}
    assert REVIEW.validate_otel_demo_sdk_settings(full, "full") == []
    absent = {"frontend": "true", "product-catalog-a": "true",
              "product-catalog-b": "true", "otel-collector": None,
              "product-catalog": None}
    assert REVIEW.validate_otel_demo_sdk_settings(absent, "absent") == [
        "true", "true", "true"]


def test_otel_partial_rendered_sdk_settings_reject_unexpected_enabled_service_true() -> None:
    with pytest.raises(ValueError, match="differs from declared mode"):
        REVIEW.validate_otel_demo_sdk_settings({
            "frontend": "true", "product-catalog-a": "true",
            "product-catalog-b": "true"}, "partial")


def test_otel_rendered_sdk_settings_require_both_controlled_replicas() -> None:
    with pytest.raises(ValueError, match="lacks a controlled product-catalog replica"):
        REVIEW.validate_otel_demo_sdk_settings({
            "frontend": None, "product-catalog-a": None}, "full")


def test_native_preflight_retains_deployment_only_argv_contract(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    result = REVIEW.review(declaration, compact, full, tmp_path / "out")
    assert "procrustes/native/browse/0/preflight.command.json" in (
        result["full_facts"]["actual_procrustes"])


def test_untyped_worker_claims_verify_only_retained_frozen_selection(tmp_path: Path) -> None:
    toolchain = tmp_path / "toolchain"
    selected = toolchain / "forecasts.json"
    write(selected, {"saved": True})
    claims = {
        "forecasts.json": {"bytes": selected.stat().st_size, "sha256": digest(selected)},
        "unselected.bin": {"bytes": 99, "sha256": "f" * 64},
    }
    proof = REVIEW.verify_worker_output_claims(
        claims, dict(claims), {}, toolchain,
        {"sha256_by_path": {"toolchain/forecasts.json": digest(selected)}})
    assert proof["scope"] == "selected_untyped_outputs_only"
    assert proof["verified_selected_paths"] == ["forecasts.json"]
    assert proof["unselected_claims"] == ["unselected.bin"]
    assert proof["whole_worker_tree_verified"] is False


def test_full_only_reuse_binds_untyped_claims_to_saved_freeze_and_marks_external_compact(
        tmp_path: Path) -> None:
    declaration, _compact, full = fixture(tmp_path)
    result = REVIEW.review(declaration, None, full, tmp_path / "out")
    scope = result["full_facts"]["worker_import_facts"]["output_claim_scope"]
    assert scope["scope"] == "selected_untyped_outputs_only"
    assert scope["verified_selected_paths"] == ["forecasts.json"]
    assert scope["freeze_map_binding"] == (
        "selected_claims_match_forecast_saved; compact_freeze_comparison_external_pending")
    assert result["compact_facts"] is None


def test_fixed_identity_and_order_remain_gates(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    saved = json.loads((full / "forecast-saved.json").read_text())
    saved["saved_ns"] = 21
    write(full / "forecast-saved.json", saved)
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    path = full / "forecast-saved.json"
    proof["files"]["forecast-saved.json"].update(bytes=path.stat().st_size, sha256=digest(path))
    write(full / "selected-transport-proof.json", proof)
    with pytest.raises(ValueError, match="does not precede"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_selection_is_family_scope_not_outcome_scope() -> None:
    assert SELECT.wanted_member("evaluation-v5.json", "compact")
    assert not SELECT.wanted_member("attempt-journal.jsonl", "compact")
    assert SELECT.wanted_member("toolchain/static-inputs.json", "input-supplement")
    assert SELECT.wanted_member(
        "toolchain/inputs/combined/network_scope/observations.json", "input-supplement")
    assert SELECT.wanted_member(
        "runtime-identity-v5/supplied-alias-scope-final.json", "full")
    assert SELECT.wanted_member("toolchain/ebpf/raw/browse/model.json", "full")
    assert not SELECT.wanted_member("unrelated/raw-journal.jsonl", "full")


def test_fixed_declaration_has_exact_coverage_scopes() -> None:
    declaration = json.loads((ROOT / "docs/iteration5-main-review-candidates.json").read_text())
    cells = declaration["cells"]
    qualification = declaration["qualification_cells"]
    assert len(cells) == 17
    assert len({(x["run_id"], x["collector"], x["system"], x["mode"], x["seed"])
                for x in cells}) == 17
    assert sum(x["compact_scope"] == "retrieve_selected_nonjournal" for x in cells) == 8
    assert sum(x["compact_scope"] == "reuse_existing_verified_facts" for x in cells) == 9
    assert sum(x["full_scope"] == "retrieve_input_supplement" for x in cells) == 2
    assert sum(x["full_scope"] == "reuse_existing_selected" for x in cells) == 1
    assert [(x["collector"], x["system"]) for x in qualification] == [
        ("obi", "otel_demo"), ("obi", "deathstarbench"), ("coroot", "petclinic")]
    assert all(len(x["manual_review_restored_sha256"]) == 64 for x in qualification)
    assert all(x["full_artifact_id"] > 0 and x["full_artifact_bytes"] > 0
               and len(x["full_artifact_digest"]) == 71 for x in qualification)


def test_future_candidate_manifest_is_exact_three_fixed_coroot_pc_full_cells() -> None:
    path = ROOT / "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    declaration = json.loads(path.read_text())
    cells = declaration["cells"]
    assert [(row["collector"], row["system"], row["mode"], row["seed"])
            for row in cells] == [
                ("coroot", "petclinic", "full", 6),
                ("coroot", "petclinic", "full", 7),
                ("coroot", "petclinic", "full", 8)]
    assert {row["run_id"] for row in cells} == {41004291277}
    assert {row["head_sha"] for row in cells} == {
        "c5df32ffc3039136c184b7915337836c39db811f"}
    assert all(row["compact_scope"] == "retrieve_selected_nonjournal"
               and row["full_scope"] == "retrieve_family_selected"
               and row["compact_artifact_digest"].startswith("sha256:")
               and row["full_artifact_digest"].startswith("sha256:")
               for row in cells)


def _run_manifest_selector(tmp_path: Path, manifest: str, *, phase: str = "pending17",
                           document: dict | None = None):
    workflow = (ROOT / ".github/workflows/review-pending-main-evidence-v5.yml").read_text()
    script = textwrap.dedent(
        workflow.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0])
    source = ROOT / "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    target = tmp_path / "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    if document is not None:
        target.write_text(json.dumps(document))
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "docs"], cwd=tmp_path, check=True)
    output = tmp_path / "github-output.txt"
    environment = os.environ | {
        "PHASE": phase, "QUALIFICATION_SYSTEM": "all",
        "CANDIDATE_MANIFEST": manifest, "PENDING17_GO": "true",
        "GITHUB_OUTPUT": str(output)}
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=tmp_path, env=environment,
        text=True, capture_output=True)
    return result, output


def test_pending_manifest_selector_binds_exact_tracked_manifest_and_three_cells(
        tmp_path: Path) -> None:
    name = "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    result, output = _run_manifest_selector(tmp_path, name)
    assert result.returncode == 0, result.stderr
    values = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert len(json.loads(values["matrix"])["cell"]) == 3
    assert values["candidate_manifest"] == name
    assert len(values["candidate_manifest_sha256"]) == 64
    assert len(values["candidate_manifest_git_blob"]) == 40


@pytest.mark.parametrize(("manifest", "phase", "message"), [
    ("docs/iteration5-main-review-candidates-coroot-petclinic-full.json",
     "qualification", "qualification requires the original candidate manifest"),
    ("../outside.json", "pending17",
     "candidate_manifest must be a normalized repo-relative docs/*.json path"),
])
def test_candidate_manifest_scope_is_fail_closed(
        tmp_path: Path, manifest: str, phase: str, message: str) -> None:
    result, _ = _run_manifest_selector(tmp_path, manifest, phase=phase)
    assert result.returncode != 0
    assert message in result.stderr


def test_candidate_manifest_invalid_scope_is_rejected(tmp_path: Path) -> None:
    name = "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    document = json.loads((ROOT / name).read_text())
    document["cells"][0]["full_scope"] = "unreviewed_whole_archive"
    result, _ = _run_manifest_selector(tmp_path, name, document=document)
    assert result.returncode != 0
    assert "candidate manifest has a malformed cell or invalid scope" in result.stderr


def test_selected_transport_identity_and_member_hash_fail_closed(tmp_path: Path) -> None:
    declaration, compact, full = fixture(tmp_path)
    proof = json.loads((full / "selected-transport-proof.json").read_text())
    proof["artifact"]["workflow_run"]["head_sha"] = "f" * 40
    write(full / "selected-transport-proof.json", proof)
    with pytest.raises(ValueError, match="identity/integrity"):
        REVIEW.review(declaration, compact, full, tmp_path / "out")


def test_failed_selected_transport_retains_cost_and_failure_phase(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class FailedRemote:
        verified_received_bytes = 17
        attempted_received_bytes = 23
        failures = [{"attempt": 1, "error_type": "fixture"}]

        def __init__(self, metadata, out):
            pass

    monkeypatch.setattr(SELECT, "RemoteZip", FailedRemote)
    monkeypatch.setattr(SELECT.zipfile, "ZipFile",
                        lambda remote: (_ for _ in ()).throw(SELECT.zipfile.BadZipFile()))
    metadata = {"id": 1, "name": "a", "size_in_bytes": 2,
                "digest": "sha256:" + "a" * 64, "expired": False,
                "workflow_run": {"id": 3, "head_sha": "b" * 40}}
    expected = {**{key: metadata[key] for key in ("id", "name", "size_in_bytes", "digest")},
                "run_id": 3, "head_sha": "b" * 40}
    with pytest.raises(SELECT.zipfile.BadZipFile):
        SELECT.select(metadata, expected, "compact", tmp_path / "selected")
    proof = json.loads((tmp_path / "selected/selected-transport-proof.json").read_text())
    assert proof["complete"] is False
    assert proof["failure"] == {
        "phase": "selected_member_transport", "error_type": "BadZipFile"}
    assert proof["range_verified_received_bytes"] == 17
    assert proof["range_attempted_received_bytes"] == 23


def test_typed_package_stream_verifies_every_file_and_selects_method_bytes(tmp_path: Path) -> None:
    package, selected = tmp_path / "package", tmp_path / "selected"
    package.mkdir()
    bodies = {"forecasts.json": b"{}\n", "unselected/raw.bin": b"raw-evidence"}
    archive = package / "payload.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for name, body in bodies.items():
            info = tarfile.TarInfo(name)
            info.size = len(body)
            import io
            bundle.addfile(info, io.BytesIO(body))
    rows = [{"path": name, "type": "file", "bytes": len(body),
             "sha256": hashlib.sha256(body).hexdigest()} for name, body in bodies.items()]
    write(package / "payload.manifest.jsonl", "".join(json.dumps(row) + "\n" for row in rows).encode())
    write(package / "transport.json", {"kind": "toolchain",
        "archive_bytes": archive.stat().st_size, "archive_sha256": digest(archive),
        "manifest_sha256": digest(package / "payload.manifest.jsonl")})
    proof = REVIEW.verify_package(package, selected, kind="toolchain")
    assert proof["all_files_verified"] == 2
    assert (selected / "forecasts.json").is_file()
    assert not (selected / "unselected/raw.bin").exists()


def test_handoff_selection_retains_complete_small_identity_tree() -> None:
    assert REVIEW._package_selected("parent-import.json", "handoff")
    assert REVIEW._package_selected("training-index-proof.json", "handoff")
    assert REVIEW._package_selected("worker/worker-provenance.json", "handoff")
    assert REVIEW._package_selected("worker/worker-status.json", "handoff")
    assert REVIEW._package_selected("worker/output-manifest.json", "handoff")


def test_workflow_and_checker_never_emit_admission_verdict() -> None:
    workflow = (ROOT / ".github/workflows/review-pending-main-evidence-v5.yml").read_text()
    checker = (ROOT / "scripts/review-main-saved-facts-v5.py").read_text()
    assert "independent_admission_performed\": False" in checker
    assert "availability_outcome_or_accuracy_used_as_gate\": False" in checker
    assert "0.875" not in checker
    assert "scientific_GO" not in workflow
    assert "default: qualification" in workflow
    assert "qualification_system:" in workflow
    assert "if qualification_system!='all':" in workflow
    assert "qualification_system must be all for pending17" in workflow
    assert "default: docs/iteration5-main-review-candidates.json" in workflow
    assert "qualification requires the original candidate manifest" in workflow
    assert "candidate_manifest must be a normalized repo-relative docs/*.json path" in workflow
    assert "candidate manifest has a malformed cell or invalid scope" in workflow
    assert "candidate-manifest.json" in workflow
    assert "pending17 requires explicit post-qualification independent GO" in workflow


def indexed_fixture(root: Path):
    freeze = {"sha256_by_path": {}}

    def reference(name, value):
        path = root / name
        write(path, value)
        freeze["sha256_by_path"]["toolchain/" + name] = digest(path)
        return {"path": "/saved/toolchain/" + name, "bytes": path.stat().st_size,
                "sha256": digest(path)}

    def request(order, code, source="ebpf"):
        return {"request_order": order, "sha256": str(code) * 64, "source": source,
                "observations": 1, "content_type": "application/json"}

    ordinary = {**request(2, 2), "path": "/saved/toolchain/inputs/ordinary.json"}
    native = {**request(1, 4, "native"), "path": "/saved/toolchain/inputs/native.json"}
    for row in (ordinary, native):
        freeze["sha256_by_path"]["toolchain/" + REVIEW.toolchain_relative(row["path"])] = row["sha256"]
    rows = [{**request(order, code), "shard": 0, "offset": index * 10, "length": 10}
            for index, (order, code) in enumerate(((1, 1), (3, 3)))]
    index = reference("inputs/ebpf/raw/exports/ebpf-request-index.jsonl",
                      ("\n".join(json.dumps(row) for row in rows) + "\n").encode())
    shard = {"path": "/saved/toolchain/inputs/shard.bin", "bytes": 20, "sha256": "a" * 64}
    freeze["sha256_by_path"]["toolchain/inputs/shard.bin"] = shard["sha256"]
    ebpf = {"observations": 3, "exports": [ordinary], "stream_exports": [{
        "schema_version": "deepflow-request-archive-v5", "source": "ebpf",
        "requests": 2, "observations": 2, "wire_bytes": 20,
        "request_index": index, "shards": [shard]}]}
    groups = [reference("inputs/ebpf/raw/observations.json", ebpf),
              reference("inputs/native/raw/observations.json", {"observations": 1, "exports": [native]})]
    manifest = {"observations": 4, "ordered_request_group_manifests": groups}
    accepted = [{"http_status": 200, "export_index": index, "content_bytes": 10,
                 "content_sha256": str(index + 1) * 64,
                 "endpoint": "/v1/traces" if index == 3 else "/sources/ebpf/v1/traces",
                 "storage_form": "stream_archive_slice" if index in (0, 2) else "ordinary_export"}
                for index in range(4)]
    sequence = reference("discovery/combined/raw/observed-runtime/accepted-request-sequence.jsonl",
                         ("\n".join(json.dumps(row) for row in accepted) + "\n").encode())
    sequence.update(requests=4, same_order_as_original_request_ordinals_and_source_groups=True)
    plain = lambda row: {key: value for key, value in row.items() if key != "storage_form"}
    stream_proof = reference("discovery/combined/raw/observed-runtime/accepted-stream-requests.jsonl",
                             ("\n".join(json.dumps(plain(accepted[i])) for i in (0, 2)) + "\n").encode())
    stream_proof.update(requests=2, same_http_body_order_as_request_index=True)
    replay = {"accepted_request_sequence": sequence, "accepted_stream_requests": stream_proof,
              "accepted_ingest_requests": [plain(accepted[i]) for i in (1, 3)]}
    return manifest, replay, freeze


def test_stream_and_ordinary_requests_preserve_group_order_and_ordinal_reset(tmp_path: Path) -> None:
    manifest, replay, freeze = indexed_fixture(tmp_path)
    facts = REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)
    assert (facts["accepted_inputs"], facts["ordinary_requests"], facts["streamed_requests"]) == (4, 2, 2)
    assert facts["unselected_wire_payloads_independently_rehashed"] is False
    manifest["ordered_request_group_manifests"].reverse()
    with pytest.raises(ValueError, match="differs from saved source order"):
        REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)


def test_stream_metadata_must_be_frozen_even_when_downloaded_hash_matches(tmp_path: Path) -> None:
    manifest, replay, freeze = indexed_fixture(tmp_path)
    freeze["sha256_by_path"]["toolchain/inputs/ebpf/raw/exports/ebpf-request-index.jsonl"] = "0" * 64
    with pytest.raises(ValueError, match="metadata is not frozen"):
        REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)


def test_acceptance_subsets_cannot_omit_stream_requests(tmp_path: Path) -> None:
    manifest, replay, freeze = indexed_fixture(tmp_path)
    replay["accepted_ingest_requests"].pop()
    with pytest.raises(ValueError, match="ordinary acceptance subset"):
        REVIEW.accepted_sequence_facts(tmp_path, manifest, replay, freeze)


@pytest.mark.parametrize("signal,marker,valid", [("EBPF", "control-123", True),
                                               ("Packet", "control-123", False),
                                               ("EBPF", "other", False)])
def test_deepflow_control_uses_exact_raw_record_origin_and_marker(
        tmp_path: Path, signal: str, marker: str, valid: bool) -> None:
    body = json.dumps({"signal_source": signal, "l7_protocol": "Http1",
                       "tap_side": "ServerProcess", "request_resource": "/" + marker}).encode()
    name = "deepflow-raw/node-a/001-positive-control/l7_flow_log"
    path = tmp_path / "observations" / name
    write(path, b"preceding\n" + body + b"\nfollowing\n")
    write(path.parent / "snapshot.json", {"node": "a", "files": [{
        "snapshot_name": "l7_flow_log", "copied_bytes": path.stat().st_size,
        "copied_sha256": digest(path)}]})
    claim = {"raw_file": "/saved/observations/" + name, "raw_offset": 10,
             "raw_length": len(body), "raw_sha256": hashlib.sha256(body).hexdigest(),
             "proven": True, "protocol": "Http1", "tap_side": "ServerProcess"}
    if valid:
        facts = REVIEW.deepflow_control_facts(tmp_path, {"marker": "control-123"}, "a", claim)
        assert facts["raw_offset"] == 10
    else:
        with pytest.raises(ValueError, match="raw eBPF HTTP origin and marker"):
            REVIEW.deepflow_control_facts(tmp_path, {"marker": "control-123"}, "a", claim)


def test_fresh_selector_keeps_index_and_acceptance_metadata_without_wire_shards() -> None:
    for name in ("inputs/ebpf/raw/exports/ebpf-request-index.jsonl",
                 "discovery/combined/raw/observed-runtime/accepted-request-sequence.jsonl",
                 "discovery/combined/raw/observed-runtime/accepted-stream-requests.jsonl"):
        assert SELECT.wanted_member("toolchain/" + name, "full")
        assert REVIEW._package_selected(name, "toolchain")
    assert not SELECT.wanted_member("toolchain/inputs/ebpf/raw/exports/ebpf-requests-000001.bin", "full")


def test_fresh_qualification_requires_main_source_and_all_three_fixed_families(tmp_path: Path) -> None:
    name = "docs/iteration5-main-review-candidates-coroot-petclinic-full.json"
    cells = []
    for collector, system, mode, run_id in (("deepflow", "deathstarbench", "absent", 1),
                                           ("coroot", "otel_demo", "full", 2),
                                           ("obi", "petclinic", "partial", 3)):
        row = json.loads((ROOT / name).read_text())["cells"][0]
        row.update(collector=collector, system=system, mode=mode, seed=6, run_id=run_id,
                   head_sha=REVIEW.FRESH_HEAD, stage="main", runner="study")
        cells.append(row)
    result, output = _run_manifest_selector(tmp_path, name, phase="fresh-qualification",
                                            document={"cells": cells})
    assert result.returncode == 0, result.stderr
    values = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert len(json.loads(values["matrix"])["cell"]) == 3


def closure_fixture(root: Path):
    claims, capture, termination, prefixes = [], {}, {}, {}
    observations = root / "observations"
    for node in ("a", "b"):
        for stage, final in (("002-training", False), ("003-final", True)):
            row = {"snapshot_name": "l7_flow_log", "source_name": "l7_flow_log",
                   "copied_bytes": 100, "copied_sha256": "a" * 64,
                   "source_changed_during_snapshot": False, "pending_tail_bytes_at_read": 0}
            snapshot = {"node": node, "stage": stage, "files": [row],
                        "technical_valid": True, "producer_closed": final,
                        "closed_checkpoint": final, "codec_technical_failure_records": 0}
            name = f"deepflow-raw/node-{node}/{stage}/snapshot.json"
            write(observations / name, snapshot)
            claims.extend([{"path": name, "bytes": (observations / name).stat().st_size,
                            "sha256": digest(observations / name)},
                           {"path": name.replace("snapshot.json", "l7_flow_log"),
                            "bytes": 100, "sha256": "a" * 64}])
            if final:
                capture[node] = snapshot
        prefixes[f"{node}/l7_flow_log"] = {"unchanged": True, "bytes": 100,
                                            "training_sha256": "a" * 64,
                                            "final_prefix_sha256": "a" * 64}
        raw = {}
        for label in ("stop", "inspect", "events"):
            name = f"final-{node}-{label}.txt"
            write(observations / name, b"retained termination source")
            raw[label] = {"path": name, "sha256": digest(observations / name)}
        termination[node] = {"technical_valid": True, "running": False,
                             "exit_code": 0, "oom_killed": False, "sigkill_events": 0,
                             "raw_evidence": raw}
    retention = {"files": claims, "file_count": len(claims),
                 "raw_bytes": sum(row["bytes"] for row in claims), "zero_internal_loss_proven": False}
    path = observations / "deepflow-retention-manifest.json"
    write(path, retention)
    collector = {"retained_file_hashes": {path.name: {
        "bytes": path.stat().st_size, "sha256": digest(path)}}}
    drain = {"final_raw_capture": {"final": True, "technical_valid": True, "nodes": capture},
             "termination": termination, "training_prefix_unchanged_in_final": prefixes}
    return collector, drain


def test_deepflow_closure_verifies_saved_hash_chain_without_claiming_all_raw_bytes(tmp_path: Path) -> None:
    collector, drain = closure_fixture(tmp_path)
    facts = REVIEW.deepflow_closure_facts(tmp_path, collector, drain)
    assert facts["snapshot_hash_chains_verified"] == 4
    assert facts["all_raw_payload_bytes_independently_rehashed"] is False
    assert facts["zero_kernel_producer_or_flush_loss_proven"] is False


@pytest.mark.parametrize("problem", ["prefix", "termination", "snapshot"])
def test_deepflow_closure_rejects_inconsistent_saved_sources(tmp_path: Path, problem: str) -> None:
    collector, drain = closure_fixture(tmp_path)
    if problem == "prefix":
        drain["training_prefix_unchanged_in_final"]["a/l7_flow_log"]["final_prefix_sha256"] = "b" * 64
    elif problem == "termination":
        drain["termination"]["b"]["oom_killed"] = True
    else:
        write(tmp_path / "observations/deepflow-raw/node-a/003-final/snapshot.json", {})
    with pytest.raises(ValueError):
        REVIEW.deepflow_closure_facts(tmp_path, collector, drain)
