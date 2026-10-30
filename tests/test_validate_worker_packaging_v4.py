from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

from ebpf_discovery import artifact_transport_v4 as transport


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate-worker-packaging-v4.py"
SPEC = importlib.util.spec_from_file_location("validate_worker_packaging_v4", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def _write(path: Path, value) -> None:
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def test_saved_package_validator_uses_real_package_build_and_comparison(tmp_path, monkeypatch):
    run_id, parent_run_id = VALIDATOR.RUN_ID, VALIDATOR.PARENT_RUN_ID
    artifact_id, name = VALIDATOR.ARTIFACT_ID, VALIDATOR.ARTIFACT_NAME
    workflow_head, scientific_head = VALIDATOR.WORKFLOW_HEAD, VALIDATOR.SCIENTIFIC_HEAD
    assert workflow_head != scientific_head  # The pinned saved worker's real identity shape.
    identity = {"run_id": str(parent_run_id), "commit": scientific_head,
                "system": "deathstarbench", "mode": "absent", "seed": "6"}
    source = tmp_path / "worker-tree"
    source.mkdir()
    (source / "nested").mkdir()
    (source / "nested/data.bin").write_bytes(b"\x00\xffworker-output")
    (source / "nested/data.bin").chmod(0o640)
    _write(source / "worker-status.json", {"status": "complete", "identity": {
        **identity, "worker_run_id": str(run_id), "worker_workflow_sha": workflow_head}})
    _write(source / "worker-provenance.json", {
        "worker_run_id": str(run_id), "scientific_sha": scientific_head,
        "implementation_sha": scientific_head, "workflow_sha": workflow_head,
        "identity": identity})
    _write(source / "output-manifest.json", {
        "worker_run_id": str(run_id), "workflow_sha": workflow_head, "identity": identity})
    package = tmp_path / "saved-package"
    transport.package(source, package, kind="worker")
    archive = tmp_path / "artifact.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for path in sorted(package.iterdir()):
            bundle.write(path, path.name)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    for key, value in (("ARTIFACT_BYTES", archive.stat().st_size),
                       ("ARTIFACT_SHA256", digest)):
        monkeypatch.setattr(VALIDATOR, key, value)
    artifact_api = tmp_path / "artifact-api.json"
    run_api = tmp_path / "run-api.json"
    _write(artifact_api, {"id": artifact_id, "name": name, "size_in_bytes": archive.stat().st_size,
        "digest": "sha256:" + digest, "expired": False,
        "workflow_run": {"id": run_id, "head_sha": workflow_head}})
    _write(run_api, {"id": run_id, "head_sha": workflow_head, "conclusion": "success"})
    result = VALIDATOR.validate(archive, artifact_api, run_api, tmp_path / "proof")
    assert result["status"] == "equivalent"
    assert result["comparison"]["all_paths_bytes_modes_and_sha256_equal"] is True
    assert result["comparison"]["files"] == 4
    assert result["source"]["workflow_head_sha"] == workflow_head
    assert result["source"]["scientific_head_sha"] == scientific_head
    assert result["downloaded_working_zip_removed_after_verification"] is True
    assert not archive.exists()
    assert json.loads((tmp_path / "proof/validation.json").read_text()) == result
