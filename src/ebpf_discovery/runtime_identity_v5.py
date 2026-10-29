"""Collector-neutral, lifecycle-bracketed runtime service identity evidence."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shlex
import time
from typing import Any, Iterable


SCHEMA = "runtime-identity-inventory-v5"
_STAGE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
_CLOCKS = {
    "guest_monotonic_ns": ("monotonic_ns", {"direct_clock_gettime_monotonic", "linux_bpf_ktime_get_ns"}),
    "guest_boottime_ns": ("boottime_ns", {"direct_clock_gettime_boottime", "linux_bpf_ktime_get_boot_ns"}),
    "guest_realtime_unix_ns": ("realtime_unix_ns", {
        "direct_clock_gettime_realtime", "documented_same_guest_realtime_relation"}),
}


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _normalize_sample(value: Any, node: str, stage: str) -> dict:
    if not isinstance(value, dict) or value.get("schema") != "runtime-identity-guest-sample-v5":
        raise ValueError("guest runtime identity sample has the wrong schema")
    if value.get("node") != node or value.get("stage") != stage:
        raise ValueError("guest runtime identity sample has the wrong node or stage")
    clocks = value.get("clocks") or {}
    for edge in ("started", "ended"):
        if not isinstance(clocks.get(edge), dict) or any(
                type(clocks[edge].get(name)) is not int
                for name in ("realtime_unix_ns", "monotonic_ns", "boottime_ns")):
            raise ValueError("guest runtime identity sample lacks exact clock readings")
    processes = value.get("processes")
    if not isinstance(processes, list):
        raise ValueError("guest runtime identity sample lacks a process inventory")
    docker = value.get("docker_proof") or {}
    if docker.get("list_returncode") != 0 or docker.get("inspect_returncode") != 0:
        raise ValueError("guest runtime identity sample lacks actual Docker inspection")
    if not isinstance(value.get("containers"), list):
        raise ValueError("guest runtime identity sample lacks a container inventory")
    if len({row.get("host_pid") for row in processes if isinstance(row, dict)}) != len(processes):
        raise ValueError("guest runtime identity process inventory has duplicate PIDs")
    return value


def capture(ctx, stage: str) -> dict:
    """Capture both guests; retain raw output, normalized samples, and cost separately."""
    if not isinstance(stage, str) or not _STAGE.fullmatch(stage):
        raise ValueError("runtime identity stage must be a portable, normalized identifier")
    root = Path(ctx.out) / "runtime-identity-v5"
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / f"capture-{stage}.json"
    if manifest_path.exists():
        raise ValueError(f"runtime identity stage already captured: {stage}")
    helper = Path(__file__).resolve().parents[2] / "scripts" / "runtime-identity-v5-guest.py"
    helper_sha = _sha(helper)
    remote = f"/tmp/runtime-identity-v5-{helper_sha}.py"
    started_ns, started_mono = time.time_ns(), time.monotonic_ns()
    samples, files, node_costs = [], [], {}
    errors = []
    for node in ("a", "b"):
        acquisition_started = time.monotonic_ns()
        ctx.node_put(node, helper, remote)
        result = ctx.node_exec(
            node, f"python3 {shlex.quote(remote)} --node {node} --stage {shlex.quote(stage)}",
            timeout=120, check=False)
        acquisition_ended = time.monotonic_ns()
        raw_path = root / f"raw-{stage}-{node}.json"
        stderr_path = root / f"raw-{stage}-{node}.stderr.log"
        raw_path.write_text(str(getattr(result, "stdout", "")), encoding="utf-8")
        stderr_path.write_text(str(getattr(result, "stderr", "")), encoding="utf-8")
        files.extend((raw_path, stderr_path))
        normalization_started = time.monotonic_ns()
        if int(getattr(result, "returncode", 0)) != 0:
            errors.append(f"{node}:helper_returncode:{getattr(result, 'returncode', None)}")
            node_costs[node] = {
                "capture_and_transfer_seconds": (acquisition_ended - acquisition_started) / 1e9,
                "normalization_seconds": (time.monotonic_ns() - normalization_started) / 1e9}
            continue
        try:
            sample = _normalize_sample(json.loads(raw_path.read_text(encoding="utf-8")), node, stage)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{node}:invalid_sample:{exc}")
            node_costs[node] = {
                "capture_and_transfer_seconds": (acquisition_ended - acquisition_started) / 1e9,
                "normalization_seconds": (time.monotonic_ns() - normalization_started) / 1e9}
            continue
        normalized_path = root / f"sample-{stage}-{node}.json"
        _write(normalized_path, sample)
        files.append(normalized_path)
        samples.append(sample)
        node_costs[node] = {
            "capture_and_transfer_seconds": (acquisition_ended - acquisition_started) / 1e9,
            "normalization_seconds": (time.monotonic_ns() - normalization_started) / 1e9}
    ended_mono, ended_ns = time.monotonic_ns(), time.time_ns()
    cost = {"schema": "runtime-identity-cost-v5", "stage": stage,
            "started_ns": started_ns, "ended_ns": ended_ns,
            "started_monotonic_ns": started_mono, "ended_monotonic_ns": ended_mono,
            "elapsed_seconds": (ended_mono - started_mono) / 1e9,
            "guest_count": 2, "normalized_samples": len(samples),
            "by_node": node_costs,
            "accounting": "capture/transfer and local normalization retained separately"}
    cost_path = root / f"cost-{stage}.json"
    _write(cost_path, cost)
    files.append(cost_path)
    manifest = {
        "schema": "runtime-identity-capture-v5", "stage": stage,
        "helper": {"path": helper.relative_to(Path(__file__).resolve().parents[2]).as_posix(),
                   "sha256": helper_sha, "remote_path": remote},
        "samples": samples, "errors": errors,
        "runner_interval": {"started_monotonic_ns": started_mono,
                            "ended_monotonic_ns": ended_mono},
        "files": {path.name: {"bytes": path.stat().st_size, "sha256": _sha(path)}
                  for path in files},
        "cost_file": cost_path.name,
        "service_identity_policy": "actual observed PID/container ownership only",
    }
    _write(manifest_path, manifest)
    if errors or {sample.get("node") for sample in samples} != {"a", "b"}:
        raise RuntimeError("runtime identity capture incomplete: " + "; ".join(errors))
    return manifest


def inventory(captures: Iterable[dict], capture_lifetimes: Iterable[dict] = (),
              event_enclosures: Iterable[dict] = ()) -> dict:
    samples = []
    capture_rows = []
    for item in captures:
        if not isinstance(item, dict) or item.get("schema") != "runtime-identity-capture-v5":
            raise ValueError("runtime identity inventory received a non-capture input")
        samples.extend(item.get("samples") or [])
        capture_rows.append({"stage": item.get("stage"), "files": item.get("files"),
                             "helper": item.get("helper"), "cost_file": item.get("cost_file")})
    keys = [(row.get("stage"), row.get("node")) for row in samples]
    if len(set(keys)) != len(keys):
        raise ValueError("runtime identity inventory has duplicate stage/node samples")
    lifetimes = list(capture_lifetimes)
    lifetime_keys = [(row.get("source_capture_id"), row.get("node"))
                     for row in lifetimes if isinstance(row, dict)]
    if len(lifetime_keys) != len(lifetimes) or len(set(lifetime_keys)) != len(lifetime_keys):
        raise ValueError("runtime identity inventory has invalid or duplicate source capture lifetimes")
    enclosures = list(event_enclosures)
    enclosure_keys = [(row.get("request_nonce"), row.get("node"), row.get("record_locator"))
                      for row in enclosures if isinstance(row, dict)]
    if len(enclosure_keys) != len(enclosures) or len(set(map(repr, enclosure_keys))) != len(enclosure_keys):
        raise ValueError("runtime identity inventory has invalid or duplicate event enclosures")
    return {"schema": SCHEMA, "samples": samples, "captures": capture_rows,
            "capture_lifetimes": lifetimes, "event_enclosures": enclosures}


def _unknown(runtime: Any, *reasons: str) -> dict:
    locator = runtime.get("locator") if isinstance(runtime, dict) else None
    return {"status": "unknown", "service_identity": None,
            "unknown_reasons": list(reasons), "record_locator": locator,
            "graph_edges_injected": False}


def _sample(index: dict, stage: str, node: str) -> dict | None:
    rows = index.get((stage, node), [])
    return rows[0] if len(rows) == 1 else None


def _process(sample: dict, pid: int) -> dict | None:
    rows = [row for row in sample.get("processes", []) if row.get("host_pid") == pid]
    return rows[0] if len(rows) == 1 else None


def _documented_evidence(value: Any) -> bool:
    return bool(
        isinstance(value, dict)
        and value.get("kind") in {"pinned_source", "retained_runtime_configuration",
                                  "documented_clock_relation", "retained_capture_lifecycle",
                                  "retained_exact_nonce"}
        and isinstance(value.get("locator"), str) and value["locator"]
        and isinstance(value.get("sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", value["sha256"])
    )


def _ordered_runner_sequence(value: Any, keys: tuple[str, ...]) -> bool:
    if not isinstance(value, dict):
        return False
    numbers = [value.get(key) for key in keys]
    return (all(type(number) is int and number >= 0 for number in numbers)
            and numbers == sorted(numbers))


def _capture_lifetime(runtime: dict, retained_inventory: dict, node: str) -> dict | None:
    identity = runtime.get("source_capture_id")
    if not isinstance(identity, str) or not identity:
        return None
    rows = [row for row in retained_inventory.get("capture_lifetimes") or []
            if isinstance(row, dict) and row.get("source_capture_id") == identity
            and row.get("node") == node]
    if len(rows) != 1:
        return None
    row = rows[0]
    ordered_sequence = _ordered_runner_sequence(row.get("runner_monotonic_sequence"), (
        "before_sample_completed_ns", "capture_opened_ns", "capture_closed_ns",
        "after_sample_started_ns"))
    if not (row.get("fresh_capture") is True
            and row.get("closed_capture") is True
            and row.get("technical_complete") is True
            and row.get("opened_after_before_sample") is True
            and row.get("closed_before_after_sample") is True
            and ordered_sequence
            and isinstance(row.get("before_stage"), str)
            and isinstance(row.get("after_stage"), str)
            and _documented_evidence(row.get("evidence"))):
        return None
    return row


def _event_enclosure(runtime: dict, retained_inventory: dict, node: str) -> dict | None:
    nonce, locator = runtime.get("request_nonce"), runtime.get("locator")
    method, route = runtime.get("method"), runtime.get("route")
    if (not isinstance(nonce, str) or not nonce or locator is None
            or runtime.get("event_role") != "synchronous_server_entry"
            or not isinstance(method, str) or not method
            or not isinstance(route, str) or not route):
        return None
    rows = [row for row in retained_inventory.get("event_enclosures") or []
            if isinstance(row, dict) and row.get("request_nonce") == nonce
            and row.get("node") == node and row.get("record_locator") == locator
            and row.get("method") == method and row.get("route") == route]
    if len(rows) != 1:
        return None
    row = rows[0]
    ordered = _ordered_runner_sequence(row.get("runner_monotonic_sequence"), (
        "before_sample_completed_ns", "request_started_ns", "request_completed_ns",
        "after_sample_started_ns"))
    if not (row.get("source_event_contains_exact_nonce") is True
            and row.get("synchronous_server_entry") is True
            and row.get("terminal_request_exchange") is True
            and row.get("technical_complete") is True
            and isinstance(row.get("before_stage"), str)
            and isinstance(row.get("after_stage"), str)
            and ordered and _documented_evidence(row.get("evidence"))):
        return None
    return row


def resolve(record: dict, retained_inventory: dict) -> dict:
    """Resolve one observed event without modifying it or inventing ancestry."""
    runtime = record.get("_runtime_identity") if isinstance(record, dict) else None
    if not isinstance(runtime, dict) and isinstance(record, dict):
        attributes = record.get("attributes")
        runtime = attributes.get("_runtime_identity") if isinstance(attributes, dict) else None
        if not isinstance(runtime, dict) and isinstance(attributes, dict):
            prefix = "_runtime_identity."
            flattened = {key[len(prefix):]: value for key, value in attributes.items()
                         if isinstance(key, str) and key.startswith(prefix)}
            runtime = flattened or None
    if not isinstance(runtime, dict):
        return _unknown(runtime, "runtime_identity_provenance_missing")
    if runtime.get("locator") is None:
        retained_locator = record.get("_observation_provenance") or record.get("raw_locator")
        if retained_locator is not None:
            runtime = {**runtime, "locator": retained_locator}
    if not isinstance(retained_inventory, dict) or retained_inventory.get("schema") != SCHEMA:
        return _unknown(runtime, "runtime_identity_inventory_invalid")
    node, pid = runtime.get("node"), runtime.get("host_pid")
    if node not in ("a", "b") or type(pid) is not int or pid <= 0:
        return _unknown(runtime, "guest_node_or_host_pid_invalid")
    if runtime.get("pid_scope") != "guest_host":
        return _unknown(runtime, "pid_scope_is_not_guest_host")
    block_id = runtime.get("block_id")
    before_stage = runtime.get("before_stage") or (f"before-{block_id}" if block_id else None)
    after_stage = runtime.get("after_stage") or (f"after-{block_id}" if block_id else None)
    index: dict[tuple[str, str], list[dict]] = {}
    for sample in retained_inventory.get("samples") or []:
        if isinstance(sample, dict):
            index.setdefault((sample.get("stage"), sample.get("node")), []).append(sample)
    clock = runtime.get("clock")
    lifetime = None
    if isinstance(clock, dict) and clock.get("domain") in _CLOCKS:
        field, relations = _CLOCKS[clock["domain"]]
        evidence = clock.get("evidence")
        if clock.get("relation") not in relations or not _documented_evidence(evidence):
            return _unknown(runtime, "source_clock_compatibility_unproven")
        if (clock["domain"] == "guest_realtime_unix_ns"
                and not (evidence.get("kind") == "documented_clock_relation"
                         and evidence.get("clock_adjustment_uncertainty")
                         == "included_in_event_interval_bounds")):
            return _unknown(runtime, "realtime_clock_adjustment_uncertainty_unbounded")
        bracket_kind = "source_event_clock"
    else:
        enclosure = _event_enclosure(runtime, retained_inventory, node)
        if enclosure is not None:
            before_stage, after_stage = enclosure["before_stage"], enclosure["after_stage"]
            field, evidence = None, enclosure["evidence"]
            bracket_kind = "exact_request_nonce"
        else:
            lifetime = _capture_lifetime(runtime, retained_inventory, node)
            if lifetime is None:
                return _unknown(runtime, "source_clock_relation_unsupported")
            before_stage, after_stage = lifetime["before_stage"], lifetime["after_stage"]
            field, evidence = None, lifetime["evidence"]
            bracket_kind = "whole_fresh_capture_lifetime"
    if not isinstance(before_stage, str) or not isinstance(after_stage, str):
        return _unknown(runtime, "lifecycle_bracket_stage_missing")
    before, after = _sample(index, before_stage, node), _sample(index, after_stage, node)
    if before is None or after is None:
        return _unknown(runtime, "unique_lifecycle_bracket_missing")
    source_guest_identity = (runtime.get("boot_id"), runtime.get("pid_namespace"))
    if (None in source_guest_identity
            or source_guest_identity != (before.get("boot_id"), before.get("host_pid_namespace"))
            or source_guest_identity != (after.get("boot_id"), after.get("host_pid_namespace"))):
        return _unknown(runtime, "source_guest_boot_or_pid_namespace_mismatch")
    start_ns, end_ns = runtime.get("event_start_ns"), runtime.get("event_end_ns")
    if bracket_kind == "source_event_clock":
        if type(start_ns) is not int or type(end_ns) is not int or start_ns < 0 or end_ns < start_ns:
            return _unknown(runtime, "source_event_interval_invalid")
        try:
            bracketed = (before["clocks"]["ended"][field] <= start_ns
                         and end_ns <= after["clocks"]["started"][field])
        except (KeyError, TypeError):
            return _unknown(runtime, "inventory_clock_missing")
        if not bracketed:
            return _unknown(runtime, "source_event_not_bracketed")
    first, second = _process(before, pid), _process(after, pid)
    if first is None or second is None:
        return _unknown(runtime, "pid_not_observed_in_both_brackets")
    sample_identity = (before.get("boot_id"), before.get("host_pid_namespace"))
    if (None in sample_identity or sample_identity
            != (after.get("boot_id"), after.get("host_pid_namespace"))):
        return _unknown(runtime, "guest_boot_or_host_pid_namespace_changed")
    process_identity = (first.get("host_pid"), first.get("start_ticks"), first.get("pid_namespace"))
    if (None in process_identity or process_identity
            != (second.get("host_pid"), second.get("start_ticks"), second.get("pid_namespace"))):
        return _unknown(runtime, "process_lifecycle_identity_changed")
    first_owner, second_owner = first.get("owner"), second.get("owner")
    if not isinstance(first_owner, dict) or not isinstance(second_owner, dict):
        return _unknown(runtime, "actual_container_owner_unobserved")
    owner_keys = ("container_id", "container_name", "image", "config_image",
                  "container_started_at", "compose")
    if any(first_owner.get(key) != second_owner.get(key) for key in owner_keys):
        return _unknown(runtime, "container_owner_changed")
    first_proofs, second_proofs = first_owner.get("ownership_proofs"), second_owner.get("ownership_proofs")
    if (first_owner.get("container_running") is not True
            or second_owner.get("container_running") is not True
            or not isinstance(first_proofs, list) or not first_proofs
            or not isinstance(second_proofs, list) or not second_proofs):
        return _unknown(runtime, "container_lifecycle_or_ownership_proof_missing")
    compose = first_owner.get("compose") or {}
    if not compose.get("project") or not compose.get("service"):
        return _unknown(runtime, "actual_compose_service_identity_unobserved")
    return {
        "status": "resolved",
        "service_identity": {"compose_project": compose["project"],
                             "compose_service": compose["service"],
                             "compose_container_number": compose.get("container_number"),
                             "container_id": first_owner["container_id"],
                             "container_name": first_owner["container_name"]},
        "process_identity": {"node": node, "boot_id": sample_identity[0],
                             "host_pid_namespace": sample_identity[1], "host_pid": pid,
                             "pid_namespace": process_identity[2],
                             "start_ticks": process_identity[1]},
        "bracket": {"kind": bracket_kind, "before_stage": before_stage,
                    "after_stage": after_stage,
                    "clock_domain": clock.get("domain") if isinstance(clock, dict) else None,
                    "clock_relation": clock.get("relation") if isinstance(clock, dict) else None,
                    "event_start_ns": start_ns, "event_end_ns": end_ns,
                    "before_ended_ns": (before["clocks"]["ended"][field]
                                        if field is not None else None),
                    "after_started_ns": (after["clocks"]["started"][field]
                                         if field is not None else None),
                    "source_capture_id": lifetime.get("source_capture_id") if lifetime else None,
                    "request_nonce": runtime.get("request_nonce")
                    if bracket_kind == "exact_request_nonce" else None},
        "ownership_proofs": {"before": first_proofs, "after": second_proofs},
        "clock_evidence": evidence, "record_locator": runtime.get("locator"),
        "unknown_reasons": [], "graph_edges_injected": False,
    }


def resolve_all(records: Iterable[dict], retained_inventory: dict) -> dict:
    rows = [resolve(record, retained_inventory) for record in records]
    reasons = Counter(reason for row in rows for reason in row["unknown_reasons"])
    return {"schema": "runtime-identity-coverage-v5", "records": len(rows),
            "resolved": sum(row["status"] == "resolved" for row in rows),
            "unknown": sum(row["status"] != "resolved" for row in rows),
            "unknown_reasons": dict(sorted(reasons.items())), "results": rows,
            "graph_edges_injected": False}
