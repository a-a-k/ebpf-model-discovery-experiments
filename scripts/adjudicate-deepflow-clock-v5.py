"""Revalidate only runtime identity projection on one immutable DeepFlow training packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import time
import zipfile

from ebpf_discovery.deepflow_codec_v5 import DEEPFLOW_SOURCE_COMMIT, DEEPFLOW_VERSION
from ebpf_discovery.deepflow_v5 import DEEPFLOW_IMAGE
from ebpf_discovery.identity_projection_v5 import (_verified_capture,
                                                    _verified_clock_relations)
from ebpf_discovery.runtime_identity_v5 import inventory
from ebpf_discovery.store_v5 import ObservationStoreV5


REPOSITORY = "a-a-k/ebpf-model-discovery-experiments"
RUN_ID = 40910393953
HEAD_SHA = "33d98e2ba522af1b740ec4465dc6ba6e7b3e0530"
ARTIFACT_ID = 12915445515
ARTIFACT_NAME = "campaign-v5-deepflow-smoke-petclinic-absent-6-40910393953"
ARTIFACT_DIGEST = "sha256:988cb584fba3a29a1967a7fb18cf7ea57f55769eaec38e4aed636ead81dd676c"
ARTIFACT_SIZE = 40795835
EXACT_DB_LOCATOR = {
    "source_file": "a/l7_flow_log",
    "retained_file": "deepflow-raw/node-a/002-live-prefix/l7_flow_log",
    "offset": "1758911", "length": "1168",
    "sha256": "e1d15827e5ff030d17f215791ee5114c538681292840e91ff7ae5aeebdebb967",
}
FIXED_FILES = {
    "status.json", "observation-index.sqlite", "observations/collector.json",
    "runtime-identity-v5/inventory-training.json",
    "runtime-identity-v5/projection-training.jsonl",
}
PREFIXES = ("runtime-identity-v5/", "observations/deepflow-raw/")


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe(info: zipfile.ZipInfo) -> bool:
    name, parts = info.filename, PurePosixPath(info.filename).parts
    return bool(name and "\\" not in name and not PurePosixPath(name).is_absolute()
                and ".." not in parts and not stat.S_ISLNK(info.external_attr >> 16))


def _verify_source(archive: Path, artifact: dict, run: dict) -> dict:
    expected = {"id": ARTIFACT_ID, "name": ARTIFACT_NAME, "size_in_bytes": ARTIFACT_SIZE,
                "digest": ARTIFACT_DIGEST, "expired": False}
    if {key: artifact.get(key) for key in expected} != expected:
        raise ValueError("artifact API identity mismatch")
    workflow = artifact.get("workflow_run") or {}
    if (workflow.get("id") != RUN_ID or workflow.get("head_sha") != HEAD_SHA
            or run.get("id") != RUN_ID or run.get("head_sha") != HEAD_SHA
            or run.get("repository", {}).get("full_name") != REPOSITORY):
        raise ValueError("workflow run API identity mismatch")
    digest, size = "sha256:" + _sha(archive), archive.stat().st_size
    if digest != ARTIFACT_DIGEST or size != ARTIFACT_SIZE:
        raise ValueError("full artifact bytes differ from API identity")
    return {"repository": REPOSITORY, "run_id": RUN_ID, "head_sha": HEAD_SHA,
            "artifact_id": ARTIFACT_ID, "artifact_name": ARTIFACT_NAME,
            "api_digest": ARTIFACT_DIGEST, "computed_digest": digest,
            "api_size_in_bytes": ARTIFACT_SIZE, "received_bytes": size}


def _wanted(name: str) -> bool:
    return (name in FIXED_FILES or name.startswith(PREFIXES)
            or name.startswith("observations/deepflow-agent-standalone-")
            or name == "observations/deepflow-codec-accounting.jsonl")


def _extract(archive: Path, destination: Path) -> list[dict]:
    destination.mkdir(parents=True, exist_ok=False)
    proofs = []
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries) or not all(
                _safe(entry) for entry in entries):
            raise ValueError("artifact ZIP names are duplicate or unsafe")
        names = {entry.filename for entry in entries}
        if not FIXED_FILES <= names:
            raise ValueError("artifact lacks a fixed required member")
        for entry in entries:
            if entry.is_dir() or not _wanted(entry.filename):
                continue
            body = bundle.read(entry)  # verifies member CRC
            target = destination / PurePosixPath(entry.filename)
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(body)
            proofs.append({"path": entry.filename, "bytes": len(body),
                           "sha256": hashlib.sha256(body).hexdigest(),
                           "zip_crc32": f"{entry.CRC:08x}"})
    return proofs


def _relation(root: Path, node: str, collector: dict) -> dict:
    guest, config_row = collector["guest_context"][node], collector["configs"][node]
    config = root / "observations" / config_row["path"]
    if _sha(config) != config_row["sha256"]:
        raise ValueError("saved DeepFlow config differs from collector manifest")
    path = root / "runtime-identity-v5" / f"clock-relation-{node}.json"
    value = {
        "schema": "runtime-identity-clock-relation-v5", "node": node,
        "boot_id": guest["boot_id"], "pid_namespace": guest["pid_namespace"],
        "domain": "guest_realtime_unix_ns",
        "relation": "documented_same_guest_realtime_relation",
        "producer": {"name": "deepflow-agent", "version": DEEPFLOW_VERSION,
                     "source_commit": DEEPFLOW_SOURCE_COMMIT, "image": DEEPFLOW_IMAGE,
                     "runtime_command": collector["commands"][node],
                     "pinned_source_paths": ["agent/src/ebpf/user/utils.h",
                         "agent/src/ebpf/user/socket.h", "agent/src/ebpf/user/tracer.c",
                         "agent/src/ebpf_dispatcher.rs", "agent/src/trident.rs"],
                     "timestamp_construction": "pinned same-guest realtime relation"},
        "runtime_configuration": {
            "path": config.relative_to(root).as_posix(), "sha256": _sha(config),
            "bytes": config.stat().st_size,
            "event_clock_adjustment_to_external_domain_enabled": False,
            "producer_mode": "standalone_controller_ntp_disabled",
            "validated_effective_facts": {"standalone_mode_config_present": True,
                "standalone_cli_enabled": True,
                "controller_ntp_correction_enabled": False}},
        "event_serialization": {"fields": ["start_time", "end_time"],
            "unit": "microseconds", "unix_nanosecond_conversion":
            "exact_integer_multiply_by_1000", "quantization_ns": 1000},
        "host_receipt_time_used": False,
        "empirical_endpoint_offsets_used_as_hard_bound": False,
        "arbitrary_tolerance_or_age_filter_used": False,
        "clock_step_limitation_retained": True,
        "limitation": "unseen guest realtime steps between samples are not excluded",
    }
    _write(path, value)
    return {"domain": value["domain"], "relation": value["relation"],
            "evidence": {"kind": "documented_clock_relation",
                         "locator": path.relative_to(root).as_posix(),
                         "sha256": _sha(path), "bytes": path.stat().st_size}}


def _derive_record(row: dict, relations: dict[str, dict]) -> tuple[dict, bool]:
    attributes = row.get("attributes")
    if not isinstance(attributes, dict) or not str(attributes.get(
            "_runtime_identity.source_clock", "")).startswith("deepflow_guest_realtime"):
        return row, False
    node = attributes.get("_runtime_identity.node")
    start, end = attributes.get("_runtime_identity.start"), attributes.get("_runtime_identity.end")
    if node not in relations or not str(start).isdigit() or not str(end).isdigit():
        raise ValueError("saved DeepFlow runtime record lacks exact clock carriers")
    derived = dict(row); derived_attributes = dict(attributes)
    derived_attributes.update({
        "_runtime_identity.clock": relations[node],
        "_runtime_identity.event_start_ns": str(int(start) * 1000),
        "_runtime_identity.event_end_ns": str(int(end) * 1000 + 999),
        "_runtime_identity.event_time_quantization": {
            "unit": "microseconds", "bin_width_ns": "1000",
            "start_bound": "serialized_floor_inclusive",
            "end_bound": "serialized_floor_plus_999_inclusive"},
    })
    derived["attributes"] = derived_attributes
    return derived, True


def adjudicate(archive: Path, artifact_metadata: Path, run_metadata: Path,
               out: Path, workspace: Path) -> dict:
    started = time.monotonic()
    if out.exists() or workspace.exists():
        raise ValueError("output/workspace already exists")
    source = _verify_source(archive, _json(artifact_metadata), _json(run_metadata))
    members = _extract(archive, workspace)
    status, collector = _json(workspace / "status.json"), _json(
        workspace / "observations" / "collector.json")
    if (status.get("system"), status.get("mode"), status.get("seed"),
            status.get("collector"), status.get("smoke")) != (
            "petclinic", "absent", 6, "deepflow", True):
        raise ValueError("saved cell identity differs from fixed source")
    if (collector.get("source_version"), collector.get("source_commit"),
            collector.get("image")) != (DEEPFLOW_VERSION, DEEPFLOW_SOURCE_COMMIT, DEEPFLOW_IMAGE):
        raise ValueError("saved producer identity differs from audited source contract")

    original_hashes = {row["path"]: row["sha256"] for row in members}
    derived = workspace.with_name(workspace.name + "-derived")
    if derived.exists():
        raise ValueError("derived workspace already exists")
    shutil.copytree(workspace, derived)
    derived_collector = _json(derived / "observations" / "collector.json")
    relations = {node: _relation(derived, node, derived_collector) for node in ("a", "b")}
    derived_collector["runtime_clock_relations"] = relations
    _write(derived / "observations" / "collector.json", derived_collector)
    verified_relations = _verified_clock_relations(derived)

    old_inventory = _json(workspace / "runtime-identity-v5" / "inventory-training.json")
    training_stages = [row.get("stage") for row in old_inventory.get("captures") or []]
    if not training_stages or any(not isinstance(stage, str) or not stage for stage in training_stages):
        raise ValueError("saved training inventory lacks exact capture stages")
    capture_cache = {}
    for stage in sorted(set(training_stages)):
        capture_cache[stage] = _verified_capture(derived, stage)
    retained = inventory([capture_cache[key][0] for key in sorted(capture_cache)],
                         clock_relations=verified_relations)
    retained["capture_proofs"] = {key: capture_cache[key][1] for key in sorted(capture_cache)}
    inventory_path = derived / "runtime-identity-v5" / "inventory-clock-adjudication.json"
    _write(inventory_path, retained)
    inventory_proof = {"path": inventory_path.relative_to(derived).as_posix(),
                       "sha256": _sha(inventory_path), "bytes": inventory_path.stat().st_size}

    old_projection_rows = [json.loads(line) for line in (
        workspace / "runtime-identity-v5" / "projection-training.jsonl").read_text(
            encoding="utf-8").splitlines() if line.strip()]
    training_digests = {row.get("digest") for row in old_projection_rows}
    old_clock_unknown = sum(
        row.get("resolution", {}).get("unknown_reasons") == ["source_clock_relation_unsupported"]
        for row in old_projection_rows)
    if (not training_digests or None in training_digests or old_clock_unknown == 0
            or len(training_digests) != len(old_projection_rows)):
        raise ValueError("saved training projection does not have the declared immutable scope")
    store = ObservationStoreV5(derived / "observation-index.sqlite", same_trace_parents=True)
    store.db.execute("CREATE TEMP TABLE adjudication_training_digests(digest TEXT PRIMARY KEY)")
    store.db.executemany("INSERT INTO adjudication_training_digests VALUES (?)",
                         ((digest,) for digest in sorted(training_digests)))
    store.db.execute("DELETE FROM spans WHERE digest NOT IN "
                     "(SELECT digest FROM adjudication_training_digests)")
    if store.db.execute("SELECT COUNT(*) FROM spans").fetchone()[0] != len(training_digests):
        raise ValueError("saved index does not contain exactly the frozen training projection rows")
    changed, transformations = 0, []
    for digest, encoded in list(store.db.execute("SELECT digest,data FROM spans ORDER BY digest")):
        original = json.loads(encoded); projected, did_change = _derive_record(original, relations)
        if did_change:
            projected_encoded = json.dumps(projected, sort_keys=True, separators=(",", ":"),
                                           allow_nan=False)
            store.db.execute("UPDATE spans SET data=? WHERE digest=?", (projected_encoded, digest))
            changed += 1
            transformations.append({"digest": digest,
                "original_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                "derived_sha256": hashlib.sha256(projected_encoded.encode()).hexdigest()})
    store.db.execute("DELETE FROM runtime_identity_projection"); store.db.commit()
    projection = store.apply_runtime_identity(
        retained, derived / "runtime-identity-v5" / "projection-clock-adjudication.jsonl",
        inventory_proof=inventory_proof, stage="training-clock-adjudication")
    guarded = store.service_projections()
    exact = [value for key, value in guarded.items() if dict(zip(
        ("source_file", "retained_file", "offset", "length", "sha256"), key)) == {
            **EXACT_DB_LOCATOR, "offset": int(EXACT_DB_LOCATOR["offset"]),
            "length": int(EXACT_DB_LOCATOR["length"])}]
    if len(exact) != 1 or exact[0]["service"] != "database":
        raise ValueError("exact saved database observation did not resolve uniquely")
    store.close()

    for path, digest in original_hashes.items():
        if _sha(workspace / path) != digest:
            raise ValueError("selected immutable source member changed")
    adjudicator_sha, adjudicator_run = (os.environ.get("GITHUB_SHA", ""),
                                        os.environ.get("GITHUB_RUN_ID", ""))
    if (len(adjudicator_sha) != 40
            or any(character not in "0123456789abcdef" for character in adjudicator_sha)
            or not adjudicator_run.isdigit()):
        raise ValueError("adjudicator GitHub revision/run provenance is missing or invalid")
    out.mkdir(parents=True, exist_ok=True)
    _write(out / "transformations.json", transformations)
    report = {
        "schema": "deepflow-clock-identity-adjudication-v5", "source": source,
        "adjudicator": {"repository": os.environ.get("GITHUB_REPOSITORY"),
            "run_id": adjudicator_run, "head_sha": adjudicator_sha,
            "sources_sha256": {path.relative_to(Path(__file__).parents[1]).as_posix(): _sha(path)
                for path in (Path(__file__), Path(__file__).parents[1] / "src" / "ebpf_discovery" /
                    "runtime_identity_v5.py", Path(__file__).parents[1] / "src" / "ebpf_discovery" /
                    "identity_projection_v5.py", Path(__file__).parents[1] / "src" /
                    "ebpf_discovery" / "store_v5.py", Path(__file__).parents[1] / "src" /
                    "ebpf_discovery" / "deepflow_codec_v5.py")}},
        "members": members, "selected_original_members_preserved": True,
        "source_full_artifact_unchanged": True, "old_packet_or_evaluation_overwritten": False,
        "derived_projection_only": True, "derived_observations": changed,
        "old_training_projection_rows": len(old_projection_rows),
        "old_source_clock_relation_unsupported": old_clock_unknown,
        "projection": projection, "export_dependency_guarded_resolutions": len(guarded),
        "exact_saved_database_resolution": exact[0],
        "transformations": {"path": "transformations.json",
                            "sha256": _sha(out / "transformations.json"),
                            "rows": len(transformations)},
        "derived_dependencies": {
            "collector_sha256": _sha(derived / "observations" / "collector.json"),
            "inventory": inventory_proof,
            "clock_relations": {node: relations[node]["evidence"] for node in sorted(relations)}},
        "preparation_and_validation_elapsed_seconds": time.monotonic() - started,
        "source_artifact_transfer_bytes": ARTIFACT_SIZE,
        "graph_or_forecast_recomputed": False, "model_refit_or_sheaft_run": False,
        "classes_or_external_outcomes_recomputed": False,
        "empirical_offset_bounds_or_tolerances_used": False,
    }
    _write(out / "adjudication.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--artifact-metadata", type=Path, required=True)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    adjudicate(args.archive, args.artifact_metadata, args.run_metadata,
               args.out, args.workspace)


if __name__ == "__main__":
    main()
