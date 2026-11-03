"""Closed-input integrity and prefix rejection, with tiny synthetic fixtures."""
import hashlib
import json
import os
from pathlib import Path

import pytest

from ebpf_discovery import evaluate_v5
from ebpf_discovery import postcapture_v5 as postcapture
from ebpf_discovery.transport_v4 import Journal


def put(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def capsule(tmp_path, monkeypatch):
    root, proof = tmp_path / "campaign", tmp_path / "proof"
    root.mkdir()
    monkeypatch.setenv("GITHUB_RUN_ID", "42")
    monkeypatch.setenv("GITHUB_SHA", "a"*40)
    counts = {"target": 2}
    monkeypatch.setattr(evaluate_v5, "expected_counts", lambda *args: (object(), counts, counts, {"11": 2}))
    monkeypatch.setattr(evaluate_v5, "acquisition_checks", lambda *args: {"valid": True, "problems": []})
    monkeypatch.setattr(postcapture, "_index_table_proof", lambda path: {"all_rows_fixture": "unchanged"})
    rows = [{"attempt_id": f"attempt-{i}", "phase": "target", "state": "11", "success": True,
             "http_steps": [{"request_id": f"request-{i}"}]} for i in range(2)]
    census = [{"attempt_key": hashlib.sha256(row["attempt_id"].encode()).hexdigest(),
               "phase": "target", "state": "11", "step_ids": [row["http_steps"][0]["request_id"]]}
              for row in rows]
    status = {"run_id": "42", "commit": "a"*40, "system": "otel_demo", "collector": "deepflow",
              "controller": "clean-study", "mode": "absent", "seed": 6, "smoke": False,
              "protocol_version": "graph-v5", "workload_counts": counts,
              "status": "postcapture_complete", "observed_operations": len(rows)}
    for name, value in (("status.json", status), ("external.json", rows), ("plans.json", rows),
                        ("census.json", census), ("infrastructure/guest-evidence-capture.json", {"status": "complete"})):
        put(root, name, value)
    put(root, "infrastructure/postcapture-guest-release.json", {
        "status": "complete", "owned_processes": [{"node": "a"}, {"node": "b"}],
        "owned_guests_confirmed_exited_ns": 1,
        "guest_evidence_capture_SHA256": postcapture._sha(root / "infrastructure/guest-evidence-capture.json")})
    put(root, "toolchain/model.json", {"fixture": "not a fitted scientific model"})
    put(root, "forecast-saved.json", {"sha256_by_path": {
        "toolchain/model.json": postcapture._sha(root / "toolchain/model.json")}})
    (root / "observation-index.sqlite").write_bytes(b"tiny index proof fixture")
    journal = Journal(root / "attempt-journal.sqlite")
    journal.close()
    (root / "empty-directory").mkdir()
    return root, proof


def test_closed_capsule_restores_modes_and_empty_directories(capsule):
    root, proof = capsule
    marker = postcapture.seal(root, proof)
    (root / "empty-directory").rmdir()
    actual, status = postcapture.verify(root, proof)
    assert actual == marker and status["status"] == "postcapture_complete"
    assert (root / "empty-directory").is_dir()
    assert actual["acquisition_closure"]["completeness"]["primary_records"] == 2


def test_relabelled_training_prefix_is_not_a_complete_capture(capsule):
    root, proof = capsule
    put(root, "external.json", json.loads((root / "external.json").read_text())[:1])
    with pytest.raises(ValueError, match="primary acquisition is incomplete"):
        postcapture.seal(root, proof)


def test_unresolved_transport_is_not_a_closed_capture(capsule):
    root, proof = capsule
    journal = Journal(root / "attempt-journal.sqlite")
    journal.append("step_started", transport_id="incomplete-request")
    journal.close()
    with pytest.raises(ValueError, match="unconfirmed remote transport"):
        postcapture.seal(root, proof)


@pytest.mark.parametrize("name", ["toolchain/model.json", "external.json", "attempt-journal.sqlite"])
def test_any_changed_scientific_file_prevents_processing(capsule, name):
    root, proof = capsule
    postcapture.seal(root, proof)
    with (root / name).open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="closed capture member differs"):
        postcapture.verify(root, proof)


def test_added_scientific_file_is_not_silently_ignored(capsule):
    root, proof = capsule
    postcapture.seal(root, proof)
    put(root, "native/final/additional.json", {"unbound": True})
    with pytest.raises(ValueError, match="file population differs"):
        postcapture.verify(root, proof)


def test_relocated_capture_is_rejected_before_index_mutation(capsule):
    root, proof = capsule
    postcapture.seal(root, proof)
    relocated = root.parent / "different-root"
    assert root.resolve().parent == relocated.resolve().parent == proof.resolve().parent
    root.rename(relocated)
    with pytest.raises(ValueError, match="original absolute scientific root"):
        postcapture.verify(relocated, proof)


def test_capture_identity_is_distinct_from_actual_processing_identity(capsule, monkeypatch):
    root, proof = capsule
    monkeypatch.setenv("GITHUB_RUN_ID", "99")
    monkeypatch.setenv("GITHUB_SHA", "b"*40)
    with pytest.raises(ValueError, match="source/run differs"):
        postcapture.seal(root, proof)
    marker = postcapture.seal(root, proof, capture_run_id="42", capture_source="a"*40)
    assert marker["identity"]["commit"] == "a"*40
    assert marker["sealing_source"] == "b"*40 and marker["sealing_run_id"] == "99"
    postcapture.verify(root, proof, capture_run_id="42", capture_source="a"*40)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="POSIX file type")
def test_delivered_special_file_is_rejected(capsule):
    root, _ = capsule
    os.mkfifo(root / "unsupported-pipe")
    with pytest.raises(ValueError, match="unsupported closed capture file type"):
        list(postcapture.files(root))
