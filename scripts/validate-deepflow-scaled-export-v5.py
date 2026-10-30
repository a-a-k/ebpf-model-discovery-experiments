"""Qualify bounded DeepFlow preparation on one immutable failed-main checkpoint.

This is software qualification only: it does not run traffic, fit a model, invoke
Sheaft, forecast, score, or replace any saved scientific result.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import stat
import subprocess
import sys
import time
import traceback
import zipfile
import yaml
import copy
import re


REPOSITORY = "a-a-k/ebpf-model-discovery-experiments"
RUN_ID = 40965631880
SOURCE_HEAD = "6ecd280207fbf850757c2c67e807054305f058ec"
ARTIFACT_ID = 12941184407
ARTIFACT_NAME = "training-v4-petclinic-absent-7-40965631880"
ARTIFACT_DIGEST = "sha256:8de2dc25fecb8ada7c44107f426d69976a1174a7fc7519468cd41ee5df54dbf9"
ARTIFACT_SIZE = 1_257_490_009
ORIGINAL_RAW = "src/ebpf_discovery/raw_v4.py"
CANDIDATE_FILES = (
    "src/ebpf_discovery/store_v5.py", "src/ebpf_discovery/deepflow_handoff_v5.py",
    "src/ebpf_discovery/raw_v4.py", "src/ebpf_discovery/bering_v4.py",
    "src/ebpf_discovery/toolchain_v4.py",
    "scripts/validate-deepflow-scaled-export-v5.py",
    ".github/workflows/validate-deepflow-scaled-export-v5.yml",
)


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _peak_rss_kib():
    try:
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except ImportError:
        return None


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
    if (workflow.get("id") != RUN_ID or workflow.get("head_sha") != SOURCE_HEAD
            or run.get("id") != RUN_ID or run.get("head_sha") != SOURCE_HEAD
            or run.get("repository", {}).get("full_name") != REPOSITORY
            or run.get("conclusion") != "failure"):
        raise ValueError("workflow run API identity mismatch")
    digest = "sha256:" + _sha(archive)
    if digest != ARTIFACT_DIGEST or archive.stat().st_size != ARTIFACT_SIZE:
        raise ValueError("received checkpoint artifact differs from API identity")
    return {"repository": REPOSITORY, "run_id": RUN_ID, "head_sha": SOURCE_HEAD,
            "artifact_id": ARTIFACT_ID, "artifact_name": ARTIFACT_NAME,
            "api_digest": ARTIFACT_DIGEST, "computed_digest": digest,
            "api_size_in_bytes": ARTIFACT_SIZE, "received_bytes": archive.stat().st_size,
            "source_run_conclusion": run.get("conclusion"),
            "source_result_scope": "failed main retained training checkpoint only"}


def _extract(archive: Path, destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=False)
    digest, count, total = hashlib.sha256(), 0, 0
    proof_path = destination.parent / "checkpoint-members.jsonl"
    with zipfile.ZipFile(archive) as bundle, proof_path.open("wb") as proofs:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries) or not all(
                _safe(entry) for entry in entries):
            raise ValueError("checkpoint ZIP names are duplicate or unsafe")
        for entry in entries:
            if entry.is_dir():
                continue
            target = (destination / PurePosixPath(entry.filename)).resolve()
            target.relative_to(destination.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(entry) as source, target.open("wb") as output:
                file_digest, size = hashlib.sha256(), 0
                while chunk := source.read(1024 * 1024):
                    output.write(chunk); file_digest.update(chunk); size += len(chunk)
            if size != entry.file_size:
                raise ValueError("checkpoint member size changed")
            line = json.dumps({"path": entry.filename, "bytes": size,
                "sha256": file_digest.hexdigest(), "zip_crc32": f"{entry.CRC:08x}"},
                sort_keys=True, separators=(",", ":")).encode() + b"\n"
            proofs.write(line); digest.update(line); count += 1; total += size
    indexes = list(destination.rglob("observation-index.sqlite"))
    if len(indexes) != 1:
        raise ValueError("checkpoint lacks one observation index")
    return {"root": indexes[0].parent, "members": count, "expanded_bytes": total,
            "member_proof": {"path": str(proof_path.resolve()),
                             "bytes": proof_path.stat().st_size,
                             "sha256": digest.hexdigest()}}


def _load_original(path: Path):
    name = "ebpf_discovery._saved_scaled_export_raw_v4"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import pinned raw_v4 source")
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _rebase_index(root: Path) -> dict:
    db = sqlite3.connect(root / "observation-index.sqlite")
    mappings = []
    for (old,) in db.execute("SELECT path FROM files ORDER BY path"):
        parts = Path(old).parts
        candidates = [i for i, part in enumerate(parts) if part in ("observations", "native")]
        if not candidates:
            raise ValueError(f"indexed source has no retained root: {old}")
        relative = Path(*parts[min(candidates):])
        new = (root / relative).resolve(); new.relative_to(root.resolve())
        if not new.is_file():
            raise ValueError(f"indexed source is absent from checkpoint: {relative}")
        mappings.append((old, str(new)))
    for old, new in mappings:
        db.execute("UPDATE files SET path=? WHERE path=?", (new, old))
    db.commit(); db.close()
    return {"indexed_sources_rebased": len(mappings),
            "policy": "same observations/native suffix inside exact checkpoint copy"}


def _validate_original_checkpoint(root: Path) -> dict:
    from ebpf_discovery.remote_toolchain_v4 import (_index_table_proof,
                                                     _validate_checkpoint)
    ready_path, manifest_path = root / "ready.json", root / "manifest.json"
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    expected = {key: ready[key] for key in (
        "run_id", "commit", "system", "mode", "seed", "manifest_sha256")}
    fixed = {"run_id": RUN_ID, "commit": SOURCE_HEAD, "system": "petclinic",
             "mode": "absent", "seed": 7}
    if any(str(expected.get(key)) != str(value) for key, value in fixed.items()):
        raise ValueError("checkpoint ready identity differs from fixed qualification source")
    manifest, file_proof = _validate_checkpoint(root, expected)
    logical = _index_table_proof(root / "observation-index.sqlite")
    canonical_files = json.dumps(file_proof, sort_keys=True, separators=(",", ":")).encode()
    return {"identity": expected, "schema_version": manifest.get("schema_version"),
            "status": manifest.get("status"),
            "manifest": {"path": str(manifest_path), "bytes": manifest_path.stat().st_size,
                         "sha256": _sha(manifest_path)},
            "ready": {"path": str(ready_path), "bytes": ready_path.stat().st_size,
                      "sha256": _sha(ready_path)},
            "manifest_files": len(file_proof["files"]),
            "file_proof_sha256": hashlib.sha256(canonical_files).hexdigest(),
            "logical_training_index": logical,
            "validated_before_rebase_or_any_checkpoint_mutation": True}


def _verified_bering_binary(build_root: Path) -> tuple[Path, dict]:
    from ebpf_discovery.toolchain_v5 import PINS
    build_path = build_root / "toolchain-build.json"
    build = json.loads(build_path.read_text(encoding="utf-8"))
    matches = [row for row in build.get("binaries", []) if row.get("name") == "bering"]
    binary = (build_root / "bin" / "bering").resolve()
    if (build.get("schema_version") != "toolchain-build-v4" or len(matches) != 1
            or matches[0].get("commit") != PINS["Bering"] or not binary.is_file()
            or binary.stat().st_size != matches[0].get("binary_bytes")
            or _sha(binary) != matches[0].get("binary_sha256")):
        raise ValueError("executed Bering binary differs from exact graph-v5 build pin")
    return binary, {"build_manifest": {"path": str(build_path.resolve()),
        "bytes": build_path.stat().st_size, "sha256": _sha(build_path)},
        "commit": matches[0]["commit"], "tree": matches[0].get("tree"),
        "binary": {"path": str(binary), "bytes": binary.stat().st_size,
                   "sha256": _sha(binary)}}


def _old_request_bodies(original, store, projections):
    from ebpf_discovery.store_v3 import LimitedReader
    for raw_path, consumed in store.db.execute("SELECT path,consumed FROM files ORDER BY path"):
        path = Path(raw_path)
        if original._source(path) != "ebpf":
            continue
        with path.open("rb") as stream:
            reader = LimitedReader(stream, consumed)
            for raw_line in original._lines(reader):
                if not raw_line.strip():
                    continue
                document = json.loads(raw_line)
                if document.get("raw_ref") or "payload" not in document:
                    raise ValueError("fixed DeepFlow checkpoint has unexpected wire representation")
                transformations = []
                filtered, count, _, _ = original._filter_json(
                    document["payload"], None, document.get("id_encoding", "hex"),
                    None, "ebpf", {}, projections, transformations)
                if count:
                    yield ((json.dumps(filtered, separators=(",", ":")) + "\n").encode(),
                           count, transformations)


def _old_bytes_splitlines_for_lf_source(stream):
    """Call the historical bytes.splitlines on each bounded LF producer row."""
    offset = 0
    for physical in stream:
        if b"\r" in physical or (b"\n" in physical[:-1]):
            raise ValueError("fixed accounting source is not LF-only JSONL")
        parts = physical.splitlines()  # The exact historical operation.
        if len(parts) != 1:
            raise ValueError("fixed accounting source row has an unexpected boundary")
        yield offset, parts[0]
        offset += len(physical)


def _verify_accounting_index(root: Path) -> dict:
    from ebpf_discovery.deepflow_handoff_v5 import DeepFlowDerivedValidator
    validator = DeepFlowDerivedValidator(root / "observations")
    index = validator._load_accounting("deepflow-codec-accounting.jsonl")
    candidate = iter(index.execute(
        "SELECT source_file,retained_file,offset_value,length_value,raw_sha256,ordinal,"
        "byte_offset,byte_length,row_sha256,status FROM rows ORDER BY ordinal"))
    path = root / "observations" / "deepflow-codec-accounting.jsonl"
    ordered, rows = hashlib.sha256(), 0
    with path.open("rb") as stream:
        for byte_offset, line in _old_bytes_splitlines_for_lf_source(stream):
            if not line.strip():
                continue
            row = json.loads(line)
            expected = (row.get("source_file"), row.get("retained_file"), row.get("offset"),
                row.get("length"), row.get("sha256"), rows, byte_offset, len(line),
                hashlib.sha256(line).hexdigest(), row.get("status"))
            if next(candidate, None) != expected:
                raise ValueError("candidate accounting index differs from independent byte stream")
            ordered.update(json.dumps(expected, separators=(",", ":"), ensure_ascii=False,
                                      allow_nan=False).encode()+b"\n")
            rows += 1
    if next(candidate, None) is not None:
        raise ValueError("candidate accounting index has an extra row")
    proof = dict(validator._accounting_proof)
    validator.close()
    return {"rows": rows, "ordered_row_proof_sha256": ordered.hexdigest(),
            "source": {"path": str(path), "bytes": path.stat().st_size,
                       "sha256": _sha(path)}, "candidate_index_proof": proof,
            "oracle": ("historical bytes.splitlines applied independently to each bounded "
                       "verified LF producer row; status/key/ordinal/offset/row-hash compared")}


class _OldSqlProjectionOracle:
    """Independent disk lookup of the exact old SQL-authoritative returned value."""

    def __init__(self, source: sqlite3.Connection, destination: Path):
        self.db = sqlite3.connect(destination)
        self.db.execute('''CREATE TABLE projections(
          source_file TEXT, retained_file TEXT, offset_value INTEGER, length_value INTEGER,
          raw_sha256 TEXT, encoded TEXT,
          PRIMARY KEY(source_file,retained_file,offset_value,length_value,raw_sha256))''')
        for resolution, inventory_path, inventory_sha in source.execute(
                "SELECT resolution,inventory_path,inventory_sha256 "
                "FROM runtime_identity_projection WHERE status='resolved_enriched'"):
            row = json.loads(resolution); locator = row["record_locator"]
            key = (str(locator["source_file"]), str(locator["retained_file"]),
                   int(locator["offset"]), int(locator["length"]), str(locator["sha256"]))
            value = {"service": row["service_identity"]["compose_service"],
                     "resolution": row, "inventory_path": inventory_path,
                     "inventory_sha256": inventory_sha}
            encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
            existing = self.db.execute(
                "SELECT encoded FROM projections WHERE source_file=? AND retained_file=? "
                "AND offset_value=? AND length_value=? AND raw_sha256=?", key).fetchone()
            if existing is not None and json.loads(existing[0]) != value:
                raise ValueError("old SQL projection has conflicting duplicate locator")
            self.db.execute("INSERT OR REPLACE INTO projections VALUES (?,?,?,?,?,?)",
                            (*key, encoded))
        self.db.commit()

    def get(self, key, default=None):
        row = self.db.execute(
            "SELECT encoded FROM projections WHERE source_file=? AND retained_file=? "
            "AND offset_value=? AND length_value=? AND raw_sha256=?", tuple(key)).fetchone()
        return json.loads(row[0]) if row is not None else default

    def __bool__(self):
        return True

    def close(self):
        self.db.close()


def _repack(descriptor: dict, destination: Path) -> dict:
    """Change storage only: put every exact indexed request into one archive shard."""
    from ebpf_discovery.bering_v4 import _verified_stream_requests
    destination.mkdir(parents=True, exist_ok=False)
    shard = destination / "ebpf-requests-one-shard.bin"
    index = destination / "ebpf-request-index.jsonl"
    shard_hash, index_hash, offset, index_bytes = hashlib.sha256(), hashlib.sha256(), 0, 0
    with shard.open("wb") as bodies, index.open("wb") as rows:
        for row, body in _verified_stream_requests(
                {"stream_exports": [descriptor]}, materialize=False):
            written = 0
            while chunk := body.read(1024 * 1024):
                bodies.write(chunk); shard_hash.update(chunk); written += len(chunk)
            body.close()
            if written != row["length"]:
                raise ValueError("repacked request length changed")
            retained = {**row, "shard": 0, "offset": offset, "length": written,
                        "sha256": row["sha256"]}
            line = json.dumps(retained, sort_keys=True, separators=(",", ":")).encode()+b"\n"
            rows.write(line); index_hash.update(line); index_bytes += len(line); offset += written
    result = dict(descriptor)
    result["request_index"] = {"path": str(index.resolve()), "bytes": index_bytes,
                               "sha256": index_hash.hexdigest()}
    result["shards"] = [{"path": str(shard.resolve()), "bytes": offset,
                          "sha256": shard_hash.hexdigest()}]
    result["qualification_storage_layout"] = "one shard; HTTP boundaries unchanged"
    return result


def _accepted_hashes(folder: Path) -> dict:
    record = json.loads((folder / "model-runtime" / "replay-command.json").read_text())
    proof = record.get("accepted_request_sequence") or {}
    path = Path(proof["path"]); ordered, count, hashes = hashlib.sha256(), 0, []
    with path.open("rb") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line); ordered.update(bytes.fromhex(row["content_sha256"]))
            hashes.append(row["content_sha256"])
            count += 1
    return ({"requests": count, "ordered_content_sha256_digest": ordered.hexdigest(),
             "journal_bytes": path.stat().st_size, "journal_sha256": _sha(path)}, hashes)


_BERING_RUNTIME_REF = re.compile(r"^bering://serve\?listen=127\.0\.0\.1(?::|%3A)[0-9]+$")
_BERING_CAPTURE_REF = re.compile(
    r"^(?P<prefix>.*(?:observed-runtime|model-runtime)/ebpf-capture/)"
    r"[0-9]+-(?P<ordinal>[0-9]+)-(?P<sha>[0-9a-f]{64})\.(?:json|pb)$")


def _bering_semantic_projection(model: dict, snapshot: dict, quality: dict,
                                accepted_hashes=()):
    """Apply the reviewed fresh-Bering provenance normalization, nothing broader."""
    differences = []
    projected_model, projected_snapshot, projected_quality = copy.deepcopy(
        (model, snapshot, quality))
    if projected_snapshot.get("model") != projected_model:
        raise ValueError("Bering snapshot/model copies disagree")
    if any(projected_quality.get("artifact", {}).get(key) != projected_snapshot.get(key)
           for key in ("topology_version", "snapshot_id", "window_start", "window_end")):
        raise ValueError("Bering quality/snapshot runtime identity mismatch")

    def replace(container, key, path, marker):
        if isinstance(container, dict) and key in container:
            differences.append({"path": path, "value": container[key]})
            container[key] = marker

    metadata = projected_model.get("metadata")
    replace(metadata, "discovered_at", "model.metadata.discovered_at", "<run-time>")
    artifact = projected_quality.get("artifact")
    for key, marker in (("path", "<run-output-path>"), ("snapshot_id", "<snapshot-id>"),
                        ("window_start", "<run-window-start>"),
                        ("window_end", "<run-window-end>")):
        replace(artifact, key, f"quality.artifact.{key}", marker)
    replace(projected_quality, "generated_at", "quality.generated_at", "<generated-at>")

    def sort_sources(rows):
        if isinstance(rows, list) and all(isinstance(row, dict) and "ref" in row for row in rows):
            rows.sort(key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")))

    def sort_evidence_sources(record):
        if not isinstance(record, dict):
            return
        entities = [*record.get("instances", []), *record.get("database_aliases", [])]
        entities.extend(record[key] for key in ("database", "peer", "relation") if key in record)
        for entity in entities:
            if isinstance(entity, dict) and "sources" in entity:
                sort_sources(entity["sources"])

    def normalize_refs(value, path):
        if isinstance(value, dict):
            for key, item in list(value.items()):
                child = f"{path}.{key}"
                if key in ("ref", "source_ref") and isinstance(item, str) and _BERING_RUNTIME_REF.fullmatch(item):
                    differences.append({"path": child, "value": item})
                    value[key] = "bering://serve?listen=<run-port>"
                elif key in ("ref", "source_ref") and isinstance(item, str):
                    capture = _BERING_CAPTURE_REF.fullmatch(item)
                    if capture is not None:
                        ordinal = int(capture.group("ordinal"))
                        if (ordinal < 1 or ordinal > len(accepted_hashes)
                                or accepted_hashes[ordinal - 1] != capture.group("sha")):
                            raise ValueError("Bering capture provenance does not bind accepted request")
                        differences.append({"path": child, "value": item})
                        value[key] = (f"bering-capture://accepted-request/{ordinal:08d}/"
                                      f"{capture.group('sha')}")
                    else:
                        normalize_refs(item, child)
                elif key == "bering.observation_evidence.v1" and isinstance(item, str):
                    decoded = json.loads(item); normalize_refs(decoded, child + "<json>")
                    sort_evidence_sources(decoded)
                    value[key] = json.dumps(decoded, sort_keys=True, separators=(",", ":"))
                else:
                    normalize_refs(item, child)
        elif isinstance(value, list):
            for ordinal, item in enumerate(value):
                normalize_refs(item, f"{path}[{ordinal}]")
    normalize_refs(projected_model, "model")
    normalize_refs(projected_snapshot, "snapshot")
    normalize_refs(projected_quality, "quality")
    sort_sources(projected_snapshot.get("sources"))
    for collection in ("services", "edges", "endpoints"):
        for entity in projected_snapshot.get("discovery", {}).get(collection, []):
            sort_sources(entity.get("provenance"))
    for entity in projected_quality.get("observation_evidence", []):
        sort_evidence_sources(entity.get("evidence"))
    snapshot_metadata = projected_snapshot.get("metadata")
    replace(snapshot_metadata, "emitted_at", "snapshot.metadata.emitted_at", "<run-time>")
    for key, marker in (("window_start", "<run-window-start>"),
                        ("window_end", "<run-window-end>"),
                        ("snapshot_id", "<snapshot-id>")):
        replace(projected_snapshot, key, f"snapshot.{key}", marker)
    normalized_model_sha = "sha256:" + hashlib.sha256(json.dumps(
        projected_model, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if "topology_version" in projected_snapshot:
        differences.append({"path": "snapshot.topology_version",
                            "value": projected_snapshot["topology_version"]})
        projected_snapshot["topology_version"] = normalized_model_sha
    if isinstance(artifact, dict) and "topology_version" in artifact:
        differences.append({"path": "quality.artifact.topology_version",
                            "value": artifact["topology_version"]})
        artifact["topology_version"] = normalized_model_sha
    projected_snapshot["model"] = copy.deepcopy(projected_model)
    return {"model": projected_model, "snapshot": projected_snapshot,
            "quality": projected_quality}, differences


def _value_index(proof: dict, destination: Path) -> sqlite3.Connection:
    path = Path(proof["path"])
    if path.stat().st_size != proof["bytes"] or _sha(path) != proof["sha256"]:
        raise ValueError("candidate authoritative value store changed")
    db = sqlite3.connect(destination)
    db.execute("CREATE TABLE values_by_sha(sha256 TEXT PRIMARY KEY, encoded TEXT NOT NULL)")
    rows = 0
    with path.open("rb") as stream:
        for line in stream:
            if not line.strip():
                continue
            item = json.loads(line)
            encoded = json.dumps(item["value"], sort_keys=True, separators=(",", ":"),
                                 allow_nan=False)
            if hashlib.sha256(encoded.encode()).hexdigest() != item.get("sha256"):
                raise ValueError("candidate authoritative value row changed")
            db.execute("INSERT INTO values_by_sha VALUES (?,?)", (item["sha256"], encoded))
            rows += 1
    db.commit()
    if rows != proof["values"]:
        raise ValueError("candidate authoritative value count changed")
    return db


def validate(args) -> dict:
    from ebpf_discovery.bering_v4 import _verified_stream_requests, replay
    from ebpf_discovery.raw_v4 import export_selection
    from ebpf_discovery.store_v5 import ObservationStoreV5

    started = time.time_ns(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    run, artifact = (json.loads(args.run_metadata.read_text()),
                     json.loads(args.artifact_metadata.read_text()))
    source = _verify_source(args.archive, artifact, run)
    extracted = _extract(args.archive, out / "checkpoint")
    root = extracted.pop("root")
    # The immutable received ZIP is already hash-proved above. Removing this local
    # transport copy reduces qualification peak disk; the GitHub source remains.
    args.archive.unlink()
    checkpoint_proof = _validate_original_checkpoint(root)
    rebase = _rebase_index(root)
    accounting_equivalence = _verify_accounting_index(root)
    original_path = out / "original-raw_v4.py"
    original_path.write_bytes(subprocess.run(
        ["git", "show", f"{SOURCE_HEAD}:{ORIGINAL_RAW}"], check=True,
        stdout=subprocess.PIPE).stdout)
    original = _load_original(original_path)
    store = ObservationStoreV5(root / "observation-index.sqlite", same_trace_parents=True)
    projections = store.service_projections(out / "candidate" / "runtime-identity-values.jsonl")
    old_projection_index = out / "old-sql-projections.sqlite"
    old_projections = _OldSqlProjectionOracle(store.db, old_projection_index)
    manifest = export_selection(store, {"ebpf": None}, out / "candidate" / "exports",
                                service_projections=projections)
    if len(manifest.get("stream_exports", [])) != 1 or manifest.get("exports"):
        raise ValueError("candidate did not produce exactly one streamed DeepFlow source")
    candidate = _verified_stream_requests(manifest, materialize=False)
    old = _old_request_bodies(original, store, old_projections)
    value_index_path = out / "candidate-values.sqlite"
    values = _value_index(manifest["stream_exports"][0]["runtime_identity_values"],
                          value_index_path)
    body_digest, requests_seen, observations, restored_count = hashlib.sha256(), 0, 0, 0
    for (row, body), (old_body, old_count, old_transformations) in zip(candidate, old, strict=True):
        same = len(old_body) == row["length"]
        cursor = 0
        while chunk := body.read(1024 * 1024):
            same = same and chunk == old_body[cursor:cursor + len(chunk)]
            cursor += len(chunk)
        body.close()
        if not same or cursor != len(old_body) or row.get("observations") != old_count:
            raise ValueError("candidate HTTP request differs from exact old-head body/order")
        refs = row.get("runtime_identity_transformation_refs") or []
        restored = []
        for ref in refs:
            match = values.execute("SELECT encoded FROM values_by_sha WHERE sha256=?",
                                   (ref.get("sha256"),)).fetchone()
            if match is None:
                raise ValueError("candidate transformation reference cannot be restored")
            restored.append(json.loads(match[0]))
        if restored != old_transformations:
            raise ValueError("candidate restored transformations differ from old-head values")
        restored_count += len(restored)
        body_digest.update(bytes.fromhex(row["sha256"])); requests_seen += 1
        observations += old_count
    if (requests_seen != manifest["stream_exports"][0]["requests"]
            or observations != manifest["observations"]):
        raise ValueError("candidate/oracle request count changed")
    transient_costs = {"old_sql_oracle_index_bytes": old_projection_index.stat().st_size,
                       "candidate_value_lookup_index_bytes": value_index_path.stat().st_size}
    values.close(); old_projections.close(); projections.close(); store.close()

    alternate = _repack(manifest["stream_exports"][0], out / "alternate-layout")
    with Path(manifest["stream_exports"][0]["request_index"]["path"]).open(
            encoding="utf-8") as request_index:
        first_request = json.loads(next(line for line in request_index if line.strip()))
    accounting_cost = first_request["derived_otlp_proof"]["codec_accounting"][
        "index_preparation_cost"]
    build = json.loads((args.toolchain_build / "toolchain-build.json").read_text())
    binary, binary_proof = _verified_bering_binary(args.toolchain_build)
    replay_manifests = [manifest, {**manifest, "stream_exports": [alternate]}]
    replay_proofs = []
    for ordinal, replay_manifest in enumerate(replay_manifests):
        folder = out / f"bering-layout-{ordinal}"
        model, quality = replay(binary, replay_manifest, folder, "petclinic-deployment",
            source_profile={"source_id": "ebpf", "input_type": "ebpf-otlp"},
            publication_mode="on_shutdown")
        command = json.loads((folder / "model-runtime" / "replay-command.json").read_text())
        config_path = folder / "model-runtime" / "serve.yaml"
        config_body = config_path.read_bytes(); config = yaml.safe_load(config_body)
        semantic_config = {"max_request_bytes": config["server"]["max_request_bytes"],
            "max_in_memory_spans": config["runtime"]["max_in_memory_spans"],
            "publication_mode": config["runtime"].get("publication_mode"),
            "source": {key: config["sources"][0].get(key)
                       for key in ("id", "type", "domain")}}
        accepted_order, accepted_hashes = _accepted_hashes(folder)
        snapshot_path = folder / "model.snapshot.json"
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        semantic, volatility = _bering_semantic_projection(
            model, snapshot, quality, accepted_hashes)
        semantic_sha = hashlib.sha256(json.dumps(
            semantic, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        replay_proofs.append({"semantic_model_quality_sha256": semantic_sha,
            "raw_outputs": {
                "model": {"path": str(folder / "model.json"),
                          "bytes": (folder / "model.json").stat().st_size,
                          "sha256": _sha(folder / "model.json")},
                "quality": {"path": str(folder / "model.signal-quality.json"),
                            "bytes": (folder / "model.signal-quality.json").stat().st_size,
                            "sha256": _sha(folder / "model.signal-quality.json")},
                "snapshot": {"path": str(snapshot_path),
                             "bytes": snapshot_path.stat().st_size,
                             "sha256": _sha(snapshot_path)}},
            "documented_fresh_process_provenance": volatility,
            "accepted_request_order": accepted_order,
            "serve_config_sha256": hashlib.sha256(config_body).hexdigest(),
            "semantic_config": semantic_config,
            "publication_mode": command.get("publication_mode"),
            "ingest": command.get("ingest")})
    comparable = [{key: value for key, value in proof.items()
                   if key not in ("serve_config_sha256", "raw_outputs",
                                  "documented_fresh_process_provenance")}
                  for proof in replay_proofs]
    if comparable[0] != comparable[1]:
        raise ValueError("storage shard boundary changed Bering request/model semantics")
    result = {"schema": "deepflow-scaled-export-qualification-v5",
        "status": "passed", "scope": "engineering qualification only",
        "source": source, "extraction": extracted,
        "checkpoint_validation_before_rebase": checkpoint_proof, "rebase": rebase,
        "accounting_index_equivalence": accounting_equivalence,
        "source_selection": {
            "originally_proposed_seed": 6,
            "fixed_qualification_seed": 7,
            "reason": ("seed 7 has the smaller retained observation index at the same "
                       "post-training, pre-discovery/pre-outcome technical-failure boundary; "
                       "this reduces qualification disk/preparation cost"),
            "outcome_selection": False,
            "saved_forecast_or_outcome_available_for_either_failed_source": False},
        "original_source": {"commit": SOURCE_HEAD, "path": ORIGINAL_RAW,
                            "sha256": _sha(original_path)},
        "candidate_source": {"github_sha": os.environ.get("GITHUB_SHA"),
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "files": {relative: {"bytes": Path(relative).stat().st_size,
                                  "sha256": _sha(Path(relative))}
                      for relative in CANDIDATE_FILES}},
        "request_equivalence": {"requests": requests_seen, "observations": observations,
            "ordered_body_digest": body_digest.hexdigest(),
            "old_head_body_and_order_equal": True,
            "original_http_envelopes_preserved": True,
            "restored_transformations": restored_count,
            "restored_transformations_equal_old_head": True,
            "authoritative_value_store": manifest["stream_exports"][0][
                "runtime_identity_values"]},
        "bering_layout_equivalence": replay_proofs,
        "toolchain_build": build,
        "executed_bering_binary": binary_proof,
        "static_procrustes_scope": {
            "executed": False,
            "old_new_output_equivalence_claimed": False,
            "reason": ("this bounded qualification exercises post-checkpoint input export, "
                       "Bering ingestion and publication only; it does not rerun unchanged "
                       "static Procrustes preflight")},
        "scientific_actions": {"traffic": False, "fit": False, "forecast": False,
                               "procrustes": False, "sheaft": False,
                               "outcome_metrics": False},
        "cost": {"started_ns": started, "ended_ns": time.time_ns(),
            "peak_rss_kib": _peak_rss_kib(),
            "candidate_request_index_bytes": manifest["stream_exports"][0][
                "request_index"]["bytes"],
            "candidate_storage_bytes": sum(item["bytes"] for item in manifest[
                "stream_exports"][0]["shards"]),
            "alternate_storage_bytes": sum(item["bytes"] for item in alternate["shards"]),
            **transient_costs,
            "accounting_index_preparation": accounting_cost,
            "archive_preparation": manifest["stream_exports"][0][
                "archive_preparation_cost"]}}
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--artifact-metadata", type=Path, required=True)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--toolchain-build", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.time_ns()
    try:
        result = validate(args)
        _write(args.out / "qualification.json", result)
        return 0
    except BaseException as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        _write(args.out / "failure.json", {"status": "failed", "error_type": type(exc).__name__,
            "error": str(exc), "traceback": traceback.format_exc(), "started_ns": started,
            "ended_ns": time.time_ns(), "github_sha": os.environ.get("GITHUB_SHA"),
            "github_run_id": os.environ.get("GITHUB_RUN_ID")})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
