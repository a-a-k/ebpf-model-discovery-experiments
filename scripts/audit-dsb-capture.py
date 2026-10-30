"""Read complete saved DSB fit prefixes; no replay, fitting, scoring or traffic."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import time
import zipfile

from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

from ebpf_discovery.artifact_transport_v4 import unpack
from ebpf_discovery.bering_v4 import _ordered_manifest_requests
from ebpf_discovery.deepflow_codec_v5 import _parse, iter_complete_records
from ebpf_discovery.observations import otlp
from ebpf_discovery.store_v3 import otlp_conflicts


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def original_member(path):
    for folder in ("toolchain", "observations", "runtime-identity-v5"):
        marker = "/" + folder + "/"
        if marker in path:
            result = folder + "/" + path.split(marker, 1)[1]
            if ".." not in PurePosixPath(result).parts:
                return result
    raise ValueError("unrecognized saved campaign path: " + path)


def inventory(wire, content_type, encoding="", *, joints=None, witnesses=None, locator=None):
    if encoding == "gzip":
        wire = gzip.decompress(wire)
    if "json" in content_type:
        payload, id_encoding = json.loads(wire), "hex"
    else:
        request = ExportTraceServiceRequest()
        request.ParseFromString(wire)
        payload, id_encoding = MessageToDict(request), "base64"
    counts = Counter()
    selected = ("rpc.system", "rpc.system.name", "rpc.service", "rpc.method", "db.system",
        "db.system.name", "db.operation", "db.operation.name", "deepflow.l7_protocol",
        "service.peer.name", "server.address", "server.port", "network.peer.address",
        "network.peer.port", "net.peer.name", "net.peer.port", "http.request.method",
        "http.method", "http.route", "url.path", "http.target", "process.pid",
        "_runtime_identity.host_pid")
    for span, conflicts in zip(otlp(payload, "ebpf", None, id_encoding), otlp_conflicts(payload), strict=True):
        if any(item["key"] == "service.name" for item in conflicts):
            span["service"] = None
            counts["ambiguous_service_identity"] += 1
        counts["spans"] += 1
        counts["service_kind:" + str(span["service"]) + ":" + str(span["kind"])] += 1
        counts["nonzero_parent" if span["parent_id"].strip("0") else "no_nonzero_parent"] += 1
        attrs = span["attributes"]
        for conflict in conflicts:
            attrs.pop(conflict["key"], None)
        for key in selected:
            if key in attrs:
                counts[key + ":" + json.dumps(attrs[key], sort_keys=True)] += 1
        if joints is not None:
            signature = json.dumps({"service": span["service"], "kind": span["kind"],
                "span_name": span["name"], "attribute_conflicts": conflicts,
                "attributes": {k: attrs[k] for k in selected if k in attrs}},
                sort_keys=True)
            joints[signature] += 1
            samples = witnesses.setdefault(signature, [])
            if len(samples) < 2:
                samples.append({"request": locator, "span_ordinal": counts["spans"],
                    **{k: span[k] for k in ("trace_id", "span_id", "parent_id")}})
    return counts


def deepflow_accounting(root):
    accounting = root / "observations/deepflow-codec-accounting.jsonl"
    if not accounting.exists():
        return None
    with accounting.open() as stream:
        rows = [json.loads(line) for line in stream]
    def key(row):
        return tuple(row[k] for k in ("node", "capture_stage", "source_file", "retained_file",
                                       "offset", "length", "sha256"))
    unmatched = {key(row): row for row in rows}
    if len(unmatched) != len(rows):
        raise ValueError("duplicate stage-local accounting locator")
    snapshots, raw_files, expected_files = [], set(), set()
    for path in sorted((root / "observations/deepflow-raw").glob("node-*/*/snapshot.json")):
        snapshot = read(path)
        for item in snapshot["files"]:
            if not item["snapshot_name"].startswith("l7_flow_log"):
                continue
            raw_path = path.parent / item["snapshot_name"]
            expected_files.add(raw_path.resolve())
            if sha(raw_path) != item["copied_sha256"] or raw_path.stat().st_size != item["copied_bytes"]:
                raise ValueError("raw snapshot differs")
            retained = raw_path.relative_to(root / "observations").as_posix()
            prefix = {}
            for raw in iter_complete_records(raw_path, prefix,
                    source_file=snapshot["node"] + "/" + item["source_name"], retained_file=retained):
                candidate = {"node": snapshot["node"], "capture_stage": snapshot["stage"],
                    **{k: getattr(raw, k) for k in ("source_file", "retained_file", "offset", "length", "sha256")}}
                if unmatched.pop(key(candidate), None) is None:
                    raise ValueError("complete raw record lacks unique codec accounting")
            if any(prefix[k] != item["codec"][k] for k in prefix):
                raise ValueError("complete raw prefix descriptor differs")
            snapshots.append({"member": raw_path.relative_to(root).as_posix(), **prefix})
    raw_files = {p.resolve() for p in (root / "observations/deepflow-raw").glob("node-*/*/l7_flow_log*")}
    if unmatched or raw_files != expected_files:
        raise ValueError("accounting/raw snapshot coverage differs")
    counts, witnesses, seen = Counter(), {}, set()
    for row in rows:
        locator = tuple(row[k] for k in ("source_file", "offset", "length", "sha256"))
        if locator in seen:
            counts["repeated_accounting_rows"] += 1
            continue
        seen.add(locator)
        with (root / "observations" / row["retained_file"]).open("rb") as stream:
            stream.seek(row["offset"])
            wire = stream.read(row["length"])
        decoded, conflicts, error = _parse(wire)
        selected = ("signal_source", "l7_protocol", "tap_side", "request_type", "request_resource",
            "ip_src", "ip_dst", "port_src", "port_dst", "process_id_0", "process_id_1")
        signature = json.dumps({"first_capture_stage": row["capture_stage"], "status": row["status"],
            "fields": {k: decoded[k] for k in selected if decoded and k in decoded},
            "reasons": row.get("reasons"), "conflicts": bool(conflicts), "parse_error": error}, sort_keys=True)
        counts[signature] += 1
        samples = witnesses.setdefault(signature, [])
        if len(samples) < 2:
            samples.append({k: row[k] for k in ("source_file", "retained_file", "offset", "length", "sha256")})
    return {"all_complete_raw_records_accounted": True, "snapshots": snapshots,
            "unique_first_seen_records": len(seen), "counts": dict(counts), "witnesses": witnesses}


def extract(archive_path, metadata, expected, destination):
    if (metadata["id"] != expected["id"] or metadata["digest"] != expected["digest"]
            or metadata["name"] != expected["name"]
            or metadata["workflow_run"]["head_sha"] != expected["head_sha"]
            or metadata["workflow_run"]["id"] != expected["run_id"]
            or archive_path.stat().st_size != expected["bytes"]
            or sha(archive_path) != expected["digest"].removeprefix("sha256:")):
        raise ValueError("saved immutable artifact identity differs")
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP members")
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            if (path.is_absolute() or ".." in path.parts or "\\" in info.filename
                    or stat.S_ISLNK(info.external_attr >> 16)):
                raise ValueError("unsafe saved ZIP member")
        archive.extractall(destination)


def audit(root, compact):
    package_proof = unpack(root / "toolchain-package", root / "toolchain", kind="toolchain")
    manifest_hashes = read(compact / "evaluation-manifest.json")["files_sha256"]
    for name in ("evaluation-v5.json", "status.json", "toolchain/forecasts.json", "evidence-v4.json", "freeze-integrity.json"):
        if sha(compact / name) != manifest_hashes[name]:
            raise ValueError("compact source hash differs: " + name)
    frozen = read(root / "freeze-integrity.json")["sha256_by_path"]
    if (sha(compact / "freeze-integrity.json") != sha(root / "freeze-integrity.json")
            or sha(compact / "toolchain/forecasts.json") != sha(root / "toolchain/forecasts.json")):
        raise ValueError("compact and full frozen sources differ")
    for name in ("toolchain/forecasts.json", "toolchain/discovery/ebpf/raw/observed.json"):
        if sha(root / name) != frozen[name]:
            raise ValueError("saved scientific output differs from pre-target freeze")
    verified_files = {}
    for name, expected in frozen.items():
        if name.startswith("toolchain/inputs/ebpf/raw/"):
            if sha(root / name) != expected:
                raise ValueError("pre-target input changed: " + name)
            verified_files[name] = expected

    def relocate(value):
        if isinstance(value, dict):
            return {key: relocate(item) for key, item in value.items()}
        if isinstance(value, list):
            return [relocate(item) for item in value]
        if (isinstance(value, str) and value.startswith("/") and any(
                "/" + folder + "/" in value for folder in ("toolchain", "observations", "runtime-identity-v5"))):
            return str((root / original_member(value)).resolve())
        return value

    manifest_path = root / "toolchain/inputs/ebpf/raw/observations.json"
    manifest = read(manifest_path)
    if manifest.get("selection_by_source") != {"ebpf": "all_frozen_source_records"}:
        raise ValueError("diagnosis requires all frozen eBPF source records")
    groups = []
    for proof in manifest.get("ordered_request_group_manifests") or []:
        path = root / original_member(proof["path"])
        if sha(path) != proof["sha256"] or path.stat().st_size != proof["bytes"]:
            raise ValueError("request group proof differs")
        groups.append(read(path))
    groups = groups or [manifest]
    inputs, originals = Counter(), Counter()
    input_joints, original_joints, input_witnesses, original_witnesses = Counter(), Counter(), {}, {}
    requests = 0
    raw_proofs = {}
    for group in groups:
        for entry, body in _ordered_manifest_requests(relocate(copy.deepcopy(group)), materialize=False):
            try:
                wire = body.read() if body is not None else Path(entry["path"]).read_bytes()
            finally:
                if body is not None:
                    body.close()
            if hashlib.sha256(wire).hexdigest() != entry["sha256"]:
                raise ValueError("frozen request body differs")
            inputs.update(inventory(wire, entry["content_type"], entry.get("content_encoding", ""),
                joints=input_joints, witnesses=input_witnesses,
                locator={k: entry[k] for k in ("path", "request_order", "sha256", "offset", "length", "shard") if k in entry}))
            requests += 1
            raw_name = original_member(entry["raw_file"])
            prefix = entry.get("raw_prefix_bytes") if entry.get("raw_file_role") else None
            key = (raw_name, prefix, entry["raw_sha256"])
            if key not in raw_proofs:
                with (root / raw_name).open("rb") as stream:
                    raw = stream.read() if prefix is None else stream.read(prefix)
                if hashlib.sha256(raw).hexdigest() != entry["raw_sha256"]:
                    raise ValueError("original source bytes differ")
                raw_proofs[key] = {"member": raw_name, "prefix_bytes": prefix,
                                   "sha256": entry["raw_sha256"]}
                if not entry.get("raw_file_role"):
                    originals.update(inventory(raw, entry["content_type"], entry.get("content_encoding", ""),
                        joints=original_joints, witnesses=original_witnesses, locator=raw_proofs[key]))
    if inputs["spans"] != manifest["observations"]:
        raise ValueError("complete frozen input count differs")
    evaluation = read(compact / "evaluation-v5.json")
    log_facts = {}
    for node in ("a", "b"):
        path = root / f"observations/final-{node}-collector.log"
        if path.exists():
            lines = path.read_text(errors="replace").splitlines()
            selected_lines = set()
            for index, line in enumerate(lines):
                if "enabled_protocols" in line:
                    end = next((j + 1 for j in range(index + 1, len(lines)) if "]" in lines[j]), index + 1)
                    selected_lines.update(range(index, end))
                elif "parse enabled" in line:
                    selected_lines.add(index)
            log_facts[node] = {"sha256": sha(path), "selected_lines": [
                {"line": i + 1, "text": lines[i]} for i in sorted(selected_lines)]}
    observed_path = root / "toolchain/discovery/ebpf/raw/observed.json"
    return {"package_proof": package_proof, "frozen_input_files": verified_files,
        "frozen_requests": requests, "input_inventory": dict(inputs),
        "original_otlp_inventory": dict(originals), "original_source_proofs": list(raw_proofs.values()),
        "input_joint_signatures": dict(input_joints), "input_witnesses": input_witnesses,
        "original_joint_signatures": dict(original_joints), "original_witnesses": original_witnesses,
        "deepflow_full_capture_accounting": deepflow_accounting(root),
        "graphs": evaluation["evidence"]["graphs"],
        "actual_observed_ebpf_graph": read(observed_path),
        "actual_observed_ebpf_graph_sha256": sha(observed_path),
        "effective_parser_log_evidence": log_facts,
        "collector_provenance": read(compact / "observations/collector.json"),
        "frozen_forecasts": read(compact / "toolchain/forecasts.json"),
        "scope": "Complete frozen eBPF fit input; DeepFlow rejected accounting spans the full capture and is labeled by capture stage. Parent counts describe fields, not confirmed ancestry. No missing record establishes interception impossibility."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--cell", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    cell = read(args.cell)
    for role in ("full", "compact"):
        extract(args.source / (role + ".zip"), read(args.source / (role + "-api.json")),
                cell[role], args.source / role)
    facts = audit(args.source / "full", args.source / "compact")
    facts.update(cell=cell, elapsed_seconds=time.monotonic() - started,
                 claim="Saved-evidence diagnosis; no new scientific fit, forecast, outcome score or admission.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
