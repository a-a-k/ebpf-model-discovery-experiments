"""Exact, synchronous Actions handoff for the v4 training toolchain.

The parent campaign remains the owner of the live guests.  This module moves only
the already closed training checkpoint to another standard Actions runner and
returns a byte-manifested ``toolchain`` directory.  It does not resume a campaign,
issue application traffic, filter observations, or choose between outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
import time
import uuid
import zipfile

import requests

from .runtime import Context
from .store_v3 import ObservationStore
from .toolchain_v4 import PINS, Toolchain


API_VERSION = "2026-03-10"
WORKFLOW = "toolchain-worker-v4.yml"
IDENTITY_KEYS = ("run_id", "commit", "system", "mode", "seed", "manifest_sha256")


def _sha(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def _atomic_json(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _manifest(root: Path) -> dict[str, dict]:
    root = Path(root).resolve()
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"manifested tree contains a symlink: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            result[relative] = {"bytes": path.stat().st_size, "sha256": _sha(path)}
    return result


def _safe_extract(archive: Path, destination: Path) -> None:
    """Extract an Actions ZIP without accepting links, duplicates or traversal."""
    destination = Path(destination).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("archive destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    seen = set()
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            name = member.filename.replace("\\", "/")
            parts = Path(name).parts
            mode = member.external_attr >> 16
            if (not name or name.startswith("/") or ".." in parts or Path(name).is_absolute()
                    or name in seen or stat.S_ISLNK(mode)):
                raise ValueError(f"unsafe or duplicate archive member: {member.filename}")
            seen.add(name)
            target = (destination / name).resolve()
            if not target.is_relative_to(destination):
                raise ValueError(f"archive member escapes destination: {member.filename}")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(member) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)


def _read(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _index_table_proof(path: Path) -> dict:
    """Hash the logical closed index; SQLite file layout and WAL are irrelevant."""
    db = sqlite3.connect(f"file:{Path(path).resolve().as_posix()}?mode=ro&immutable=1", uri=True)
    try:
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("training observation index failed quick_check")
        result = {}
        ordering = {"spans": "digest", "links": "source,linked_trace,linked_span,trace",
                    "files": "path"}
        for table, order in ordering.items():
            digest, count = hashlib.sha256(), 0
            for row in db.execute(f"SELECT * FROM {table} ORDER BY {order}"):
                digest.update(json.dumps(row, separators=(",", ":"), ensure_ascii=False).encode())
                digest.update(b"\n")
                count += 1
            result[table] = {"rows": count, "sha256": digest.hexdigest()}
        schema = list(db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master "
                                 "WHERE type IN ('table','index') ORDER BY type,name"))
        result["schema_sha256"] = _json_sha(schema)
        return result
    finally:
        db.close()


def _consistent_live_index_proof(connection: sqlite3.Connection, temporary: Path) -> dict:
    temporary = Path(temporary)
    temporary.parent.mkdir(parents=True, exist_ok=True)
    if temporary.exists():
        raise ValueError("consistent parent-index backup destination already exists")
    target = sqlite3.connect(temporary)
    try:
        connection.backup(target)
        target.commit()
    finally:
        target.close()
    try:
        return _index_table_proof(temporary)
    finally:
        temporary.unlink(missing_ok=True)


def _readonly_store(path: Path) -> ObservationStore:
    store = ObservationStore.__new__(ObservationStore)
    store.same_trace_parents = True
    store.path = Path(path)
    store.db = sqlite3.connect(f"file:{store.path.resolve().as_posix()}?mode=ro&immutable=1", uri=True)
    store.db.execute("PRAGMA query_only=ON")
    return store


def _validate_checkpoint(root: Path, expected: dict, *, allow_toolchain: bool = False) -> tuple[dict, dict]:
    """Validate the closed backup, not mutable parent DB/WAL or append-only files."""
    root = Path(root).resolve()
    manifest_path, ready_path = root / "manifest.json", root / "ready.json"
    if not manifest_path.is_file() or not ready_path.is_file():
        raise ValueError("training checkpoint lacks manifest or ready marker")
    manifest, ready = _read(manifest_path), _read(ready_path)
    if _sha(manifest_path) != expected.get("manifest_sha256"):
        raise ValueError("training checkpoint manifest digest mismatch")
    if (manifest.get("schema_version") != "v4-training-prefix-checkpoint"
            or manifest.get("status") != "partial_training_capture_only; no forecast or completed cell"
            or ready.get("status") != "training_checkpoint_ready"):
        raise ValueError("training checkpoint schema or status mismatch")
    identity = manifest.get("identity") or {}
    for key in IDENTITY_KEYS[:-1]:
        if str(identity.get(key)) != str(expected.get(key)) or str(ready.get(key)) != str(expected.get(key)):
            raise ValueError(f"training checkpoint identity mismatch: {key}")
    if ready.get("manifest_sha256") != expected.get("manifest_sha256"):
        raise ValueError("training checkpoint ready digest mismatch")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("training checkpoint file census is empty")
    actual = {}
    for relative, record in sorted(files.items()):
        path = root / relative
        if (not isinstance(relative, str) or Path(relative).is_absolute()
                or ".." in Path(relative).parts or path.is_symlink() or not path.is_file()
                or not isinstance(record, dict) or record.get("relative_path") != relative):
            raise ValueError(f"invalid checkpoint file record: {relative}")
        proof = {"bytes": path.stat().st_size, "sha256": _sha(path)}
        if proof != {"bytes": record.get("bytes"), "sha256": record.get("sha256")}:
            raise ValueError(f"checkpoint file changed: {relative}")
        actual[relative] = proof
    present = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    allowed = set(files) | {"manifest.json", "ready.json"}
    # A live parent has release.json beside the uploaded checkpoint; the uploaded
    # artifact itself was closed before release and therefore does not.
    extras = present - allowed
    permitted_extras = {"release.json"}
    if allow_toolchain:
        permitted_extras.update(path for path in extras if Path(path).parts[0] == "toolchain")
    if extras - permitted_extras or allowed - present:
        raise ValueError("checkpoint contains unmanifested or missing files")
    return manifest, {"manifest_sha256": _sha(manifest_path), "files": actual}


def _verify_binaries(root: Path, manifest: dict) -> dict:
    build = _read(root / "toolchain-build" / "toolchain-build.json")
    rows = build.get("binaries") or []
    expected = {name.lower(): commit for name, commit in PINS.items()}
    if build.get("schema_version") != "toolchain-build-v4" or {r.get("name") for r in rows} != set(expected):
        raise ValueError("checkpoint toolchain build manifest differs from exact pins")
    proofs = {}
    for row in rows:
        name = row["name"]
        binary = (root / "toolchain-build" / "bin" / name).resolve()
        recorded = Path(str(row.get("binary", "")))
        if (row.get("commit") != expected[name] or recorded != binary
                or not binary.is_file() or binary.is_symlink()
                or binary.stat().st_size != row.get("binary_bytes")
                or _sha(binary) != row.get("binary_sha256")):
            raise ValueError(f"checkpoint binary identity mismatch: {name}")
        proofs[name] = {"commit": row["commit"], "bytes": binary.stat().st_size,
                        "sha256": _sha(binary), "path": str(binary)}
    manifest_pins = (manifest.get("toolchain") or {}).get("binaries") or []
    if {p.get("name") for p in manifest_pins} != set(expected):
        raise ValueError("checkpoint manifest lacks exact binary proofs")
    return proofs


def execute_worker(checkpoint_zip: Path, campaign_root: Path, artifact_root: Path,
                   expected: dict) -> dict:
    """Restore one checkpoint at its original absolute root and execute tools."""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("remote v4 toolchain execution is permitted only in GitHub Actions")
    campaign_root, artifact_root = Path(campaign_root).resolve(), Path(artifact_root).resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)
    status = {"schema_version": "remote-toolchain-worker-v4", "status": "started",
              "started_ns": time.time_ns(), "identity": expected,
              "new_application_traffic": False, "completed_campaign_cell": False}
    _atomic_json(artifact_root / "worker-status.json", status)
    before = None
    try:
        if campaign_root.exists() and any(campaign_root.iterdir()):
            raise ValueError("exact worker campaign restore root is not empty")
        _safe_extract(checkpoint_zip, campaign_root)
        manifest, input_proof = _validate_checkpoint(campaign_root, expected)
        index_proof = _index_table_proof(campaign_root / "observation-index.sqlite")
        if _json_sha(index_proof) != expected.get("training_index_proof_sha256"):
            raise ValueError("worker checkpoint index differs logically from live parent training index")
        repository_root = Path(__file__).resolve().parents[2]
        implementation_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repository_root, check=True,
            text=True, capture_output=True).stdout.strip()
        if implementation_sha != expected.get("commit"):
            raise ValueError("worker checkout differs from parent scientific implementation")
        binary_proof = _verify_binaries(campaign_root, manifest)
        before = input_proof["files"]
        plans = _read(campaign_root / "plans.json")
        if _json_sha(plans) != expected.get("plans_sha256"):
            raise ValueError("worker plans differ from parent supplied plan digest")
        toolchain = campaign_root / "toolchain"
        if toolchain.exists():
            raise ValueError("checkpoint unexpectedly contains toolchain output")
        ctx = Context(campaign_root, expected["mode"], int(expected["seed"]))
        # Never append worker commands to any checkpoint-originated log.
        ctx.command_log = artifact_root / "worker-commands.jsonl"
        declaration = importlib.import_module(f"systems.{expected['system']}.experiment_v4")
        old_bin = os.environ.get("PBS_BIN")
        os.environ["PBS_BIN"] = str((campaign_root / "toolchain-build" / "bin").resolve())
        store = _readonly_store(campaign_root / "observation-index.sqlite")
        try:
            forecasts = Toolchain(ctx, expected["system"], store, declaration).forecast(plans)
        finally:
            store.close()
            if old_bin is None:
                os.environ.pop("PBS_BIN", None)
            else:
                os.environ["PBS_BIN"] = old_bin
        after_manifest, after = _validate_checkpoint(campaign_root, expected, allow_toolchain=True)
        if after["files"] != before or after_manifest != manifest:
            raise RuntimeError("closed checkpoint changed during worker execution")
        if not (toolchain / "forecasts.json").is_file() or _read(toolchain / "forecasts.json") != forecasts:
            raise RuntimeError("worker forecasts are absent or disagree with returned values")
        destination = artifact_root / "toolchain"
        if destination.exists():
            raise ValueError("worker artifact toolchain destination already exists")
        os.replace(toolchain, destination)
        output_files = _manifest(destination)
        provenance = {
            "schema_version": "remote-toolchain-worker-v4",
            "identity": {key: expected.get(key) for key in IDENTITY_KEYS},
            "parent_run_attempt": expected.get("parent_run_attempt"),
            "parent_cell_id": expected.get("parent_cell_id"),
            "request_id": expected.get("request_id"),
            "scientific_sha": expected.get("commit"),
            "implementation_sha": implementation_sha,
            "workflow_sha": os.environ.get("GITHUB_SHA"),
            "worker_run_id": os.environ.get("GITHUB_RUN_ID"),
            "worker_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "checkpoint_artifact": {key: expected.get(key) for key in
                ("artifact_id", "artifact_name", "artifact_digest")},
            "checkpoint_input": input_proof,
            "binaries": binary_proof,
            "plans_sha256": expected["plans_sha256"],
            "training_index_proof": index_proof,
            "toolchain_files": output_files,
            "checkpoint_unchanged": True,
            "new_application_traffic": False,
            "completed_campaign_cell": False,
        }
        _atomic_json(artifact_root / "worker-provenance.json", provenance)
        _atomic_json(artifact_root / "output-manifest.json", {
            "schema_version": "remote-toolchain-output-v4",
            "identity": provenance["identity"],
            "parent_run_attempt": provenance["parent_run_attempt"],
            "parent_cell_id": provenance["parent_cell_id"],
            "request_id": provenance["request_id"],
            "worker_run_id": provenance["worker_run_id"],
            "worker_run_attempt": provenance["worker_run_attempt"],
            "workflow_sha": provenance["workflow_sha"],
            "plans_sha256": provenance["plans_sha256"],
            "training_index_proof_sha256": _json_sha(index_proof),
            "toolchain_files": output_files,
        })
        status.update(status="complete", ended_ns=time.time_ns(), checkpoint_unchanged=True,
                      toolchain_files=len(output_files))
        return forecasts
    except BaseException as error:
        partial = campaign_root / "toolchain"
        retained = artifact_root / "partial-toolchain"
        if partial.is_dir() and not retained.exists():
            try:
                os.replace(partial, retained)
                status["partial_toolchain_retained"] = True
            except OSError as retain_error:
                status["partial_toolchain_retain_error"] = repr(retain_error)
        status.update(status="technical_failure", ended_ns=time.time_ns(), error=repr(error))
        raise
    finally:
        _atomic_json(artifact_root / "worker-status.json", status)


def _headers(token: str) -> dict:
    return {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION}


def _get(session, url: str, headers: dict):
    while True:
        try:
            response = session.get(url, headers=headers, timeout=(20, 60))
            if response.status_code >= 500 or response.status_code in (408, 429):
                time.sleep(15)
                continue
            response.raise_for_status()
            return response
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(15)


def _download(session, url: str, headers: dict, destination: Path) -> str:
    response = session.get(url, headers=headers, timeout=(20, 300), stream=True)
    response.raise_for_status()
    digest = hashlib.sha256()
    temporary = destination.with_name("." + destination.name + ".tmp")
    with temporary.open("xb") as stream:
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                stream.write(chunk)
                digest.update(chunk)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, destination)
    return digest.hexdigest()


def _expected(campaign, checkpoint: Path, release: dict, plans: list) -> tuple[dict, dict]:
    if release.get("upload_success") is not True:
        raise ValueError("remote toolchain requires a successful immutable checkpoint upload")
    ready = _read(Path(checkpoint) / "ready.json")
    for key in IDENTITY_KEYS:
        if str(release.get(key)) != str(ready.get(key)):
            raise ValueError(f"release and checkpoint identity mismatch: {key}")
    if (str(release.get("system")) != str(campaign.system)
            or str(release.get("mode")) != str(campaign.ctx.mode)
            or str(release.get("seed")) != str(campaign.ctx.seed)):
        raise ValueError("release differs from live parent cell")
    for key in ("artifact_id", "artifact_url", "artifact_digest"):
        if not release.get(key):
            raise ValueError(f"checkpoint release lacks {key}")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(release["artifact_digest"])):
        raise ValueError("checkpoint artifact digest is invalid")
    expected = {key: ready[key] for key in IDENTITY_KEYS}
    expected.update(parent_run_attempt=os.environ.get("GITHUB_RUN_ATTEMPT"),
                    parent_cell_id=f"{campaign.system}:{campaign.ctx.mode}:{campaign.ctx.seed}",
                    artifact_id=str(release["artifact_id"]),
                    artifact_url=release["artifact_url"],
                    artifact_digest=release["artifact_digest"],
                    artifact_name=f"training-v4-{campaign.system}-{campaign.ctx.mode}-{campaign.ctx.seed}-{ready['run_id']}",
                    plans_sha256=_json_sha(plans))
    manifest, proof = _validate_checkpoint(Path(checkpoint), expected)
    _verify_binaries(Path(checkpoint), manifest)
    return expected, proof


def _verify_worker_output(root: Path, expected: dict, worker_run_id: int) -> dict:
    root = Path(root)
    output = _read(root / "output-manifest.json")
    provenance = _read(root / "worker-provenance.json")
    status_value = _read(root / "worker-status.json")
    if (output.get("schema_version") != "remote-toolchain-output-v4"
            or status_value.get("status") != "complete"
            or str(output.get("worker_run_id")) != str(worker_run_id)
            or str(output.get("worker_run_attempt")) != str(expected.get("worker_run_attempt"))
            or output.get("workflow_sha") != expected.get("worker_workflow_sha")
            or output.get("plans_sha256") != expected["plans_sha256"]
            or output.get("training_index_proof_sha256") != expected.get("training_index_proof_sha256")):
        raise ValueError("worker output status, run or plans binding mismatch")
    for key in IDENTITY_KEYS:
        if str(output.get("identity", {}).get(key)) != str(expected.get(key)):
            raise ValueError(f"worker output identity mismatch: {key}")
    if (str(output.get("parent_run_attempt")) != str(expected.get("parent_run_attempt"))
            or output.get("parent_cell_id") != expected.get("parent_cell_id")
            or output.get("request_id") != expected.get("request_id")):
        raise ValueError("worker output parent attempt or cell binding mismatch")
    if (provenance.get("identity") != output.get("identity")
            or str(provenance.get("worker_run_id")) != str(worker_run_id)
            or str(provenance.get("worker_run_attempt")) != str(expected.get("worker_run_attempt"))
            or provenance.get("request_id") != expected.get("request_id")
            or provenance.get("implementation_sha") != expected.get("commit")
            or provenance.get("workflow_sha") != expected.get("worker_workflow_sha")
            or provenance.get("plans_sha256") != expected.get("plans_sha256")
            or _json_sha(provenance.get("training_index_proof")) != expected.get("training_index_proof_sha256")
            or provenance.get("checkpoint_artifact") != {key: expected.get(key) for key in
                ("artifact_id", "artifact_name", "artifact_digest")}):
        raise ValueError("worker provenance differs from parent, checkpoint or implementation identity")
    files = output.get("toolchain_files")
    if not isinstance(files, dict) or not files or files != provenance.get("toolchain_files"):
        raise ValueError("worker output lacks one complete toolchain file manifest")
    actual = _manifest(root / "toolchain")
    if actual != files:
        raise ValueError("worker toolchain has missing, changed or unlisted output")
    if not (root / "toolchain" / "forecasts.json").is_file():
        raise ValueError("worker output lacks forecasts")
    return _read(root / "toolchain" / "forecasts.json")


def forecast_on_worker(campaign, checkpoint: Path, release: dict, plans: list) -> dict:
    """Dispatch once, wait synchronously, verify and atomically import forecasts."""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("remote v4 toolchain handoff is permitted only in GitHub Actions")
    token = os.environ.get("GH_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository:
        raise RuntimeError("remote toolchain handoff requires GH_TOKEN and GITHUB_REPOSITORY")
    state = campaign.ctx.out / "infrastructure" / "remote-toolchain-v4"
    state.mkdir(parents=True, exist_ok=True)
    cost = {"schema_version": "remote-toolchain-cost-v4", "started_ns": time.time_ns(),
            "checkpoint_validation_seconds": None, "dispatch_seconds": None,
            "parent_wait_wall_seconds": None, "output_transfer_seconds": None,
            "verification_import_seconds": None, "worker_run_id": None,
            "worker_run_attempt": None,
            "scope": "parent-side checkpoint validation, dispatch, wait, transfer, verification and import",
            "nesting": "parent_wait_wall_seconds contains worker compute; do not add it to worker command or compute costs"}
    cost_path = state / "cost.json"
    _atomic_json(cost_path, cost)
    validation_started = time.monotonic_ns()
    expected, checkpoint_proof = _expected(campaign, Path(checkpoint), release, plans)
    checkpoint_index_proof = _index_table_proof(Path(checkpoint) / "observation-index.sqlite")
    live_index_proof = _consistent_live_index_proof(
        campaign.store.db, state / ".parent-index-before.sqlite")
    if live_index_proof != checkpoint_index_proof:
        raise RuntimeError("live parent training index differs from its closed checkpoint backup")
    expected["training_index_proof_sha256"] = _json_sha(checkpoint_index_proof)
    _atomic_json(state / "training-index-proof.json", {
        "checkpoint": checkpoint_index_proof, "parent_before_dispatch": live_index_proof,
        "parent_after_worker": None,
        "basis": "logical tables from consistent SQLite backup; mutable DB/WAL bytes and append-only collector tails excluded"})
    cost["checkpoint_validation_seconds"] = (time.monotonic_ns() - validation_started) / 1e9
    _atomic_json(cost_path, cost)
    if (campaign.ctx.out / "toolchain").exists():
        raise ValueError("remote toolchain destination must be previously absent")
    request_id = str(uuid.uuid4())
    expected["request_id"] = request_id
    inputs = {key: str(value) for key, value in expected.items() if value is not None}
    inputs["request_id"] = request_id
    inputs["parent_repository"] = repository
    dispatch = {"schema_version": "remote-toolchain-dispatch-v4", "request_id": request_id,
                "workflow": WORKFLOW, "ref": "main", "inputs": inputs,
                "checkpoint_proof": checkpoint_proof, "started_ns": time.time_ns(),
                "status": "prepared_not_sent"}
    _atomic_json(state / "dispatch.json", dispatch)
    session = requests.Session()
    headers = _headers(token)
    url = f"https://api.github.com/repos/{repository}/actions/workflows/{WORKFLOW}/dispatches"
    dispatch["status"] = "post_started_response_unknown"
    dispatch["post_started_ns"] = time.time_ns()
    post_started = time.monotonic_ns()
    _atomic_json(state / "dispatch.json", dispatch)
    try:
        # Exactly one POST. A transport-ambiguous result is retained and raised;
        # callers must reconcile it, never blindly create a second worker run.
        response = session.post(url, headers=headers, json={"ref": "main", "inputs": inputs},
                                timeout=(20, 60))
    except requests.RequestException as error:
        cost["dispatch_seconds"] = (time.monotonic_ns() - post_started) / 1e9
        cost["ended_ns"] = time.time_ns()
        _atomic_json(cost_path, cost)
        dispatch.update(status="post_ambiguous_no_retry", ended_ns=time.time_ns(), error=repr(error))
        _atomic_json(state / "dispatch.json", dispatch)
        raise RuntimeError("worker dispatch result is ambiguous; do not retry blindly") from error
    cost["dispatch_seconds"] = (time.monotonic_ns() - post_started) / 1e9
    _atomic_json(cost_path, cost)
    if response.status_code != 200:
        dispatch.update(status="post_rejected_no_retry", ended_ns=time.time_ns(),
                        http_status=response.status_code, response_excerpt=response.text[:1000])
        _atomic_json(state / "dispatch.json", dispatch)
        raise RuntimeError(f"worker dispatch rejected with HTTP {response.status_code}")
    body = response.json()
    worker_run_id = body.get("workflow_run_id")
    if type(worker_run_id) is not int or worker_run_id <= 0:
        dispatch.update(status="post_200_invalid_identity_no_retry", ended_ns=time.time_ns(),
                        response_keys=sorted(body) if isinstance(body, dict) else None)
        _atomic_json(state / "dispatch.json", dispatch)
        raise RuntimeError("worker dispatch returned no unambiguous workflow_run_id")
    dispatch.update(status="dispatched", worker_run_id=worker_run_id,
                    run_url=body.get("run_url"), html_url=body.get("html_url"),
                    dispatched_ns=time.time_ns())
    _atomic_json(state / "dispatch.json", dispatch)
    cost["worker_run_id"] = worker_run_id
    _atomic_json(cost_path, cost)

    run_url = f"https://api.github.com/repos/{repository}/actions/runs/{worker_run_id}"
    polls = state / "polls.jsonl"
    wait_started = time.time_ns()
    while True:
        run = _get(session, run_url, headers).json()
        with polls.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"observed_ns": time.time_ns(), "id": run.get("id"),
                "status": run.get("status"), "conclusion": run.get("conclusion"),
                "head_sha": run.get("head_sha"), "run_attempt": run.get("run_attempt")}) + "\n")
        if run.get("status") == "completed":
            break
        time.sleep(15)
    if (run.get("id") != worker_run_id or run.get("event") != "workflow_dispatch"
            or (run.get("repository") or {}).get("full_name") not in (None, repository)
            or not str(run.get("path", "")).endswith(WORKFLOW)):
        raise RuntimeError("returned worker run identity differs from dispatched workflow")
    dispatch.update(worker_head_sha=run.get("head_sha"), worker_run_attempt=run.get("run_attempt"),
                    worker_conclusion=run.get("conclusion"), wait_ended_ns=time.time_ns())
    _atomic_json(state / "dispatch.json", dispatch)
    cost["parent_wait_wall_seconds"] = (time.time_ns() - wait_started) / 1e9
    cost["worker_run_attempt"] = run.get("run_attempt")
    _atomic_json(cost_path, cost)

    artifacts_url = f"https://api.github.com/repos/{repository}/actions/runs/{worker_run_id}/artifacts?per_page=100"
    artifacts = _get(session, artifacts_url, headers).json().get("artifacts") or []
    name = f"toolchain-v4-{campaign.system}-{campaign.ctx.mode}-{campaign.ctx.seed}-{worker_run_id}"
    matches = [row for row in artifacts if row.get("name") == name and row.get("expired") is not True]
    if len(matches) != 1:
        raise RuntimeError("worker run did not retain exactly one expected output artifact")
    artifact = matches[0]
    artifact_run = artifact.get("workflow_run") or {}
    if (artifact_run.get("id") not in (None, worker_run_id)
            or artifact_run.get("head_sha") not in (None, run.get("head_sha"))):
        raise RuntimeError("worker artifact differs from returned workflow run")
    archive = state / "worker-output.zip"
    transfer_started = time.monotonic_ns()
    archive_sha = _download(session, artifact["archive_download_url"], headers, archive)
    archive_bytes = archive.stat().st_size
    advertised = str(artifact.get("digest", ""))
    if advertised != "sha256:" + archive_sha:
        raise RuntimeError("downloaded worker artifact differs from Actions digest")
    stage = state / "staged-worker-output"
    _safe_extract(archive, stage)
    expected["worker_workflow_sha"] = run.get("head_sha")
    expected["worker_run_attempt"] = run.get("run_attempt")
    verification_started = time.monotonic_ns()
    forecasts = _verify_worker_output(stage, expected, worker_run_id)
    if run.get("conclusion") != "success":
        raise RuntimeError(f"worker completed without success: {run.get('conclusion')}")
    destination = campaign.ctx.out / "toolchain"
    if destination.exists():
        raise ValueError("toolchain destination appeared before atomic import")
    live_after = _consistent_live_index_proof(
        campaign.store.db, state / ".parent-index-after.sqlite")
    if live_after != checkpoint_index_proof:
        raise RuntimeError("live parent training index changed while worker was running")
    _atomic_json(state / "training-index-proof.json", {
        "checkpoint": checkpoint_index_proof, "parent_before_dispatch": live_index_proof,
        "parent_after_worker": live_after,
        "basis": "logical tables from consistent SQLite backup; mutable DB/WAL bytes and append-only collector tails excluded"})
    os.replace(stage / "toolchain", destination)
    worker_evidence = state / "worker"
    if worker_evidence.exists():
        raise ValueError("worker evidence destination appeared before import")
    os.replace(stage, worker_evidence)
    archive.unlink()
    cost["output_transfer_seconds"] = (verification_started - transfer_started) / 1e9
    cost["verification_import_seconds"] = (time.monotonic_ns() - verification_started) / 1e9
    cost["worker_artifact_id"] = artifact.get("id")
    cost["worker_artifact_digest"] = advertised
    cost["ended_ns"] = time.time_ns()
    _atomic_json(cost_path, cost)
    _atomic_json(state / "parent-import.json", {
        "schema_version": "remote-toolchain-parent-import-v4",
        "identity": {key: expected.get(key) for key in IDENTITY_KEYS},
        "parent_run_attempt": expected.get("parent_run_attempt"),
        "parent_cell_id": expected.get("parent_cell_id"),
        "worker_run_id": worker_run_id, "worker_run_attempt": run.get("run_attempt"),
        "worker_head_sha": run.get("head_sha"), "worker_artifact_id": artifact.get("id"),
        "worker_artifact_digest": advertised, "downloaded_archive_sha256": archive_sha,
        "downloaded_archive_bytes": archive_bytes,
        "downloaded_archive_retained": False,
        "downloaded_archive_disposition": "deleted after digest verification and successful atomic import; Actions artifact and complete imported files retained",
        "checkpoint_manifest_sha256": expected["manifest_sha256"],
        "plans_sha256": expected["plans_sha256"], "imported_ns": time.time_ns(),
        "parent_wait_wall_seconds": cost["parent_wait_wall_seconds"],
        "output_transfer_seconds": cost["output_transfer_seconds"],
        "verification_import_seconds": cost["verification_import_seconds"],
        "new_application_traffic": False,
    })
    return forecasts


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    worker = commands.add_parser("worker")
    worker.add_argument("--checkpoint-zip", type=Path, required=True)
    worker.add_argument("--campaign-root", type=Path, required=True)
    worker.add_argument("--artifact-root", type=Path, required=True)
    worker.add_argument("--expected", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "worker":
        execute_worker(args.checkpoint_zip, args.campaign_root, args.artifact_root,
                       _read(args.expected))


if __name__ == "__main__":
    main()
