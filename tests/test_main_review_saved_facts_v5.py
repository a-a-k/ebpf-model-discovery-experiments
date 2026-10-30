from __future__ import annotations

import hashlib
import importlib.util
import gzip
import json
from pathlib import Path
import tarfile

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
        "services": {"enabled": {"environment": {"OTEL_SDK_DISABLED": "false"}},
                     "disabled": {"environment": {"OTEL_SDK_DISABLED": "true"}}}})
    write(full / "deployment/otel_demo/runtime-resolved-node-b.yaml", {
        "services": {"disabled": {"environment": {"OTEL_SDK_DISABLED": "true"}}}})
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
    facts = REVIEW.native_mode_facts(tmp_path, declaration)
    assert facts["training"]["application_trace_count"] == 0
    assert facts["final"]["audit_self_trace_count"] == 1


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
    assert "pending17 requires explicit post-qualification independent GO" in workflow
