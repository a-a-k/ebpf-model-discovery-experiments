"""Hash-verified runtime identity enclosures and immutable service projections."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlsplit

import yaml

from .runtime_identity_v5 import _locator, inventory


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def journal_event_sha256(seq, kind, wall_ns, monotonic_ns, encoded_data) -> str:
    """Digest the exact retained SQLite event fields, including the original JSON bytes."""
    value = [seq, kind, wall_ns, monotonic_ns, encoded_data]
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def _runtime(row: dict) -> dict | None:
    value = row.get("_runtime_identity")
    attributes = row.get("attributes") or {}
    if not isinstance(value, dict):
        value = attributes.get("_runtime_identity")
    if not isinstance(value, dict):
        prefix = "_runtime_identity."
        value = {key[len(prefix):]: item for key, item in attributes.items()
                 if isinstance(key, str) and key.startswith(prefix)}
    return value or None


def _verified_capture(root: Path, stage: str) -> tuple[dict, dict]:
    path = root / "runtime-identity-v5" / f"capture-{stage}.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "runtime-identity-capture-v5" or value.get("stage") != stage:
        raise ValueError(f"runtime identity capture schema/stage mismatch: {stage}")
    verified = {}
    for name, proof in (value.get("files") or {}).items():
        member = path.parent / name
        if (not member.is_file() or member.stat().st_size != proof.get("bytes")
                or _sha(member) != proof.get("sha256")):
            raise ValueError(f"runtime identity capture member changed: {member}")
        verified[name] = dict(proof)
    interval = value.get("runner_interval") or {}
    if not all(type(interval.get(key)) is int for key in
               ("started_monotonic_ns", "ended_monotonic_ns")):
        raise ValueError(f"runtime identity capture lacks runner interval: {stage}")
    return value, {"path": path.relative_to(root).as_posix(), "sha256": _sha(path),
                   "bytes": path.stat().st_size,
                   "files": verified, "runner_interval": interval}


def _verify_locator(root: Path, raw) -> tuple[dict, dict]:
    canonical = _locator(raw)
    if canonical is None:
        raise ValueError("runtime identity event lacks a canonical raw locator")
    path = Path(canonical["retained_file"])
    path = path if path.is_absolute() else root / "observations" / path
    path = path.resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("runtime identity raw locator leaves campaign root")
    with path.open("rb") as stream:
        stream.seek(canonical["offset"])
        body = stream.read(canonical["length"])
    if len(body) != canonical["length"] or hashlib.sha256(body).hexdigest() != canonical["sha256"]:
        raise ValueError("runtime identity raw locator byte proof failed")
    return canonical, {"path": path.relative_to(root).as_posix(),
                       "offset": canonical["offset"], "length": canonical["length"],
                       "sha256": canonical["sha256"]}


def _verified_clock_relations(root: Path) -> list[dict]:
    """Verify retained source/config/guest clock declarations before resolution."""
    from .deepflow_codec_v5 import DEEPFLOW_SOURCE_COMMIT, DEEPFLOW_VERSION
    from .deepflow_v5 import DEEPFLOW_IMAGE

    collector_path = root / "observations" / "collector.json"
    if not collector_path.is_file():
        return []
    collector = json.loads(collector_path.read_text(encoding="utf-8"))
    rows = []
    for path in sorted((root / "runtime-identity-v5").glob("clock-relation-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        producer, config, serialization = (value.get("producer") or {},
                                            value.get("runtime_configuration") or {},
                                            value.get("event_serialization") or {})
        if (value.get("schema") != "runtime-identity-clock-relation-v5"
                or value.get("node") not in ("a", "b")
                or not isinstance(value.get("boot_id"), str) or not value["boot_id"]
                or not isinstance(value.get("pid_namespace"), str) or not value["pid_namespace"]
                or value.get("domain") != "guest_realtime_unix_ns"
                or value.get("relation") != "documented_same_guest_realtime_relation"
                or producer.get("name") != "deepflow-agent"
                or producer.get("version") != DEEPFLOW_VERSION
                or producer.get("source_commit") != DEEPFLOW_SOURCE_COMMIT
                or producer.get("image") != DEEPFLOW_IMAGE
                or not all(isinstance(item, str) and item
                           for item in producer.get("pinned_source_paths") or [])
                or serialization.get("unit") != "microseconds"
                or serialization.get("quantization_ns") != 1000
                or serialization.get("unix_nanosecond_conversion")
                != "exact_integer_multiply_by_1000"
                or config.get("event_clock_adjustment_to_external_domain_enabled") is not False
                or value.get("host_receipt_time_used") is not False
                or value.get("empirical_endpoint_offsets_used_as_hard_bound") is not False
                or value.get("arbitrary_tolerance_or_age_filter_used") is not False
                or value.get("clock_step_limitation_retained") is not True):
            raise ValueError(f"runtime clock relation declaration is incomplete: {path}")
        if (collector.get("schema") != "collector-lifecycle-v5"
                or collector.get("collector") != "deepflow"
                or collector.get("source_version") != DEEPFLOW_VERSION
                or collector.get("source_commit") != DEEPFLOW_SOURCE_COMMIT
                or collector.get("image") != DEEPFLOW_IMAGE
                or (collector.get("commands") or {}).get(value["node"])
                != producer.get("runtime_command")
                or (collector.get("runtime_clock_relations") or {}).get(value["node"], {}).get(
                    "evidence", {}).get("locator") != path.relative_to(root).as_posix()):
            raise ValueError(f"runtime clock relation differs from collector manifest: {path}")
        config_path = Path(str(config.get("path", "")))
        if config_path.is_absolute():
            raise ValueError("runtime clock relation config path must be campaign-relative")
        config_path = (root / config_path).resolve()
        if (not config_path.is_relative_to(root.resolve()) or not config_path.is_file()
                or config_path.stat().st_size != config.get("bytes")
                or _sha(config_path) != config.get("sha256")):
            raise ValueError(f"runtime clock relation configuration changed: {config_path}")
        manifest_config = (collector.get("configs") or {}).get(value["node"]) or {}
        parsed_config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        facts = config.get("validated_effective_facts") or {}
        if (manifest_config.get("path") != config_path.name
                or manifest_config.get("sha256") != config.get("sha256")
                or not isinstance((parsed_config.get("global") or {}).get("standalone_mode"), dict)
                or facts != {"standalone_mode_config_present": True,
                             "standalone_cli_enabled": True,
                             "controller_ntp_correction_enabled": False}
                or " --standalone " not in str(producer.get("runtime_command", ""))):
            raise ValueError(f"runtime clock relation effective standalone facts failed: {path}")
        evidence = {"kind": "documented_clock_relation",
                    "locator": path.relative_to(root).as_posix(),
                    "sha256": _sha(path), "bytes": path.stat().st_size}
        rows.append({
            "node": value["node"], "boot_id": value["boot_id"],
            "pid_namespace": value["pid_namespace"], "domain": value["domain"],
            "relation": value["relation"], "evidence": evidence,
            "configuration": dict(config), "producer": dict(producer),
            "event_serialization": dict(serialization),
            "verified_hash_bound_source_config_guest_relation": True,
            "host_receipt_time_used": False,
            "arbitrary_tolerance_or_age_filter_used": False,
            "clock_step_limitation_retained": True,
        })
    return rows


def _journal_transports(journal) -> dict[str, dict]:
    """Index a fixed journal prefix without retaining response bodies in memory."""
    by_transport = {}
    with journal.lock:
        maximum = journal.db.execute("SELECT COALESCE(MAX(seq),0) FROM events").fetchone()[0]
        rows = journal.db.execute(
            "SELECT seq,kind,wall_ns,monotonic_ns,data FROM events "
            "WHERE seq <= ? AND kind IN "
            "('step_started','step_finished','step_transport_unknown') ORDER BY seq", (maximum,))
        for seq, kind, wall_ns, monotonic_ns, encoded in rows:
            data = json.loads(encoded)
            identity = data.get("transport_id")
            if not identity:
                continue
            row = by_transport.setdefault(identity, {"started": [], "terminal": []})
            target = "started" if kind == "step_started" else "terminal"
            row[target].append({
                "seq": seq, "kind": kind, "wall_ns": wall_ns,
                "monotonic_ns": monotonic_ns, "request_id": data.get("request_id"),
                "event_row_sha256": journal_event_sha256(
                    seq, kind, wall_ns, monotonic_ns, encoded),
            })
    result = {}
    for identity, row in by_transport.items():
        if len(row["started"]) != 1 or len(row["terminal"]) != 1:
            continue
        start, terminal = row["started"][0], row["terminal"][0]
        request_id = start["request_id"]
        if (terminal["kind"] != "step_finished" or terminal["request_id"] != request_id):
            continue
        if request_id in result:
            result[request_id] = None
        else:
            result[request_id] = {"transport_id": identity, "started": start, "terminal": terminal,
                                  "snapshot_max_seq": maximum}
    return result


def _load_transport(journal, reference: dict) -> dict:
    """Restore exact original evidence rows, rejecting changes since indexing."""
    result = {"transport_id": reference["transport_id"]}
    with journal.lock:
        for role in ("started", "terminal"):
            expected = reference[role]
            row = journal.db.execute(
                "SELECT seq,kind,wall_ns,monotonic_ns,data FROM events WHERE seq=? AND seq<=?",
                (expected["seq"], reference["snapshot_max_seq"])).fetchone()
            if row is None or journal_event_sha256(*row) != expected["event_row_sha256"]:
                raise ValueError("runtime identity journal event changed after indexing")
            seq, kind, wall_ns, monotonic_ns, encoded = row
            result[role] = {"seq": seq, "kind": kind, "wall_ns": wall_ns,
                            "monotonic_ns": monotonic_ns, "data": json.loads(encoded),
                            "data_json": encoded, "event_row_sha256": expected["event_row_sha256"]}
    return result


def refresh(campaign, stage: str) -> dict:
    """Resolve indexed observations using only retained, hash-checked evidence."""
    root, started = campaign.ctx.out, time.monotonic_ns()
    capture_cache = {}
    plan_by_request = {}
    for plan in campaign.plans:
        for step in plan.get("http_steps", []):
            plan_by_request[step.get("request_id")] = {
                "block_id": plan.get("block_id"), "method": str(step.get("method") or "").upper(),
                "route": urlsplit(step.get("path") or "").path}
    transports = None
    enclosure_rows, evidence_files = [], []
    for digest, encoded in campaign.store.db.execute("SELECT digest,data FROM spans ORDER BY digest"):
        row = json.loads(encoded)
        runtime = _runtime(row)
        if not runtime or runtime.get("event_role") != "synchronous_server_entry":
            continue
        request_id = runtime.get("request_nonce")
        plan = plan_by_request.get(request_id)
        if not plan or not plan.get("block_id"):
            continue
        if (str(runtime.get("method") or "").upper() != plan["method"]
                or urlsplit(runtime.get("route") or "").path != plan["route"]):
            continue
        if transports is None:
            transports = _journal_transports(campaign.ctx.journal)
        transport = transports.get(request_id)
        if not transport:
            continue
        before_stage, after_stage = "before-" + plan["block_id"], "after-" + plan["block_id"]
        for sample_stage in (before_stage, after_stage):
            if sample_stage not in capture_cache:
                capture_cache[sample_stage] = _verified_capture(root, sample_stage)
        before, before_proof = capture_cache[before_stage]
        after, after_proof = capture_cache[after_stage]
        sequence = {
            "before_sample_completed_ns": before["runner_interval"]["ended_monotonic_ns"],
            "request_started_ns": transport["started"]["monotonic_ns"],
            "request_completed_ns": transport["terminal"]["monotonic_ns"],
            "after_sample_started_ns": after["runner_interval"]["started_monotonic_ns"],
        }
        if list(sequence.values()) != sorted(sequence.values()):
            continue
        canonical, raw_proof = _verify_locator(root, runtime.get("locator"))
        evidence = {
            "schema": "runtime-identity-enclosure-evidence-v5", "observation_digest": digest,
            "request_nonce": request_id, "method": plan["method"], "route": plan["route"],
            "transport": _load_transport(campaign.ctx.journal, transport),
            "runner_monotonic_sequence": sequence,
            "before_capture": before_proof, "after_capture": after_proof,
            "raw_locator": raw_proof, "source_event_role": runtime["event_role"],
        }
        evidence_path = root / "runtime-identity-v5" / "enclosures" / f"{digest}.json"
        _write(evidence_path, evidence)
        evidence_files.append({"path": evidence_path.relative_to(root).as_posix(),
                               "sha256": _sha(evidence_path), "bytes": evidence_path.stat().st_size})
        enclosure_rows.append({
            "request_nonce": request_id, "node": runtime.get("node"),
            "record_locator": canonical, "method": plan["method"], "route": plan["route"],
            "before_stage": before_stage, "after_stage": after_stage,
            "source_event_contains_exact_nonce": True, "synchronous_server_entry": True,
            "terminal_request_exchange": True, "technical_complete": True,
            "runner_monotonic_sequence": sequence,
            "evidence": {"kind": "retained_exact_nonce",
                         "locator": evidence_path.relative_to(root).as_posix(),
                         "sha256": _sha(evidence_path),
                         "bytes": evidence_path.stat().st_size},
        })
    for path in sorted((root / "runtime-identity-v5").glob("capture-*.json")):
        sample_stage = path.stem.removeprefix("capture-")
        if sample_stage not in capture_cache:
            capture_cache[sample_stage] = _verified_capture(root, sample_stage)
    captures = [capture_cache[key][0] for key in sorted(capture_cache)]
    retained = inventory(captures, event_enclosures=enclosure_rows,
                         clock_relations=_verified_clock_relations(root))
    retained["capture_proofs"] = {
        key: capture_cache[key][1] for key in sorted(capture_cache)}
    inventory_path = root / "runtime-identity-v5" / f"inventory-{stage}.json"
    _write(inventory_path, retained)
    inventory_proof = {"path": inventory_path.relative_to(root).as_posix(),
                       "sha256": _sha(inventory_path), "bytes": inventory_path.stat().st_size}
    supplied_aliases = None
    alias_path = root / "runtime-identity-v5" / "supplied-service-aliases-training.json"
    admission_path = root / "runtime-identity-v5" / "supplied-service-alias-admission-training.json"
    if stage == "training":
        from .supplied_alias_v5 import write_training
        supplied_aliases = write_training(
            retained, inventory_path, alias_path)
    projection = campaign.store.apply_runtime_identity(
        retained, root / "runtime-identity-v5" / f"projection-{stage}.jsonl",
        inventory_proof=inventory_proof, stage=stage)
    from .supplied_alias_v5 import (admission_sha256, admit_observed, load,
                                    load_admission, write_admission)
    alias_table = load(alias_path, root)
    if stage == "training":
        alias_admission = admit_observed(
            campaign.store, alias_table,
            expected_source_prefix="ebpf-" + campaign.collector)
        alias_admission["effective_store_projection"] = (
            campaign.store.apply_supplied_logical_aliases(alias_admission))
        effective_alias_projection = alias_admission["effective_store_projection"]
        alias_admission = write_admission(
            alias_admission, alias_path, admission_path)
    else:
        alias_admission = load_admission(admission_path, root, alias_table)
        scoped = admit_observed(
            campaign.store, alias_table,
            expected_source_prefix="ebpf-" + campaign.collector)
        final_digest_aliases = {
            digest: role["logical_service"]
            for digest, role in scoped["verified_scoped_digest_roles"].items()
            if alias_admission.get("aliases", {}).get(role["carrier"])
            == role["logical_service"]}
        scope_path = root / "runtime-identity-v5" / f"supplied-alias-scope-{stage}.json"
        _write(scope_path, {
            "schema": "supplied-logical-alias-scope-revalidation-v5", "stage": stage,
            "frozen_admission_sha256": admission_sha256(alias_admission),
            "new_mappings_admitted": False,
            "scoped_digest_aliases": final_digest_aliases,
            "verified_scoped_digest_roles": scoped["verified_scoped_digest_roles"],
            "occurrence_proofs": scoped["occurrence_proofs"],
            "conflicts": scoped["conflicts"]})
        effective_alias_projection = campaign.store.apply_supplied_logical_aliases(
            alias_admission, scoped_digest_aliases=final_digest_aliases)
        effective_alias_projection["scope_revalidation"] = {
            "path": scope_path.relative_to(root).as_posix(),
            "sha256": _sha(scope_path), "bytes": scope_path.stat().st_size}
    cost = {"schema": "runtime-identity-refresh-cost-v5", "stage": stage,
            "elapsed_seconds": (time.monotonic_ns() - started) / 1e9,
            "captures": len(captures), "enclosures": len(enclosure_rows),
            "evidence_files": evidence_files, "inventory": inventory_proof,
            "projection": projection, "supplied_logical_aliases": supplied_aliases,
            "supplied_logical_alias_admission": {
                "path": admission_path.relative_to(root).as_posix(),
                "sha256": _sha(admission_path), "bytes": admission_path.stat().st_size,
                "effective_store_projection": effective_alias_projection}}
    _write(root / "runtime-identity-v5" / f"refresh-cost-{stage}.json", cost)
    return cost
