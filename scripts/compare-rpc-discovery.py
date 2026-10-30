"""Compare two Bering binaries on one complete, immutable saved eBPF input.

Fixed technical diagnosis only: no new traffic, forecast fit or outcome scoring.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import time
import zipfile

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

from ebpf_discovery.bering_v4 import replay
from ebpf_discovery.binding_v4 import matches_call_hint
from ebpf_discovery.runtime import write_json
from ebpf_discovery.toolchain_v4 import unique_service
from systems.otel_demo.experiment_v4 import CONTRACTS

ARTIFACT = 12950018152
SOURCE_RUN = 40971766251
SOURCE_SHA = "eb7342e79e6f622123c572e222cbf60608b099e0"
ZIP_SHA = "c85a186a8b25b864f76fdaf2a1e6d0de4ab82498fa9a855448d67f56505f07fa"
INPUT_MANIFEST = "toolchain/inputs/ebpf/raw/observations.json"


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def member_name(original):
    marker = "/work/campaign/"
    if marker not in original:
        raise ValueError("saved export is outside the declared campaign")
    name = original.split(marker, 1)[1]
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        raise ValueError("unsafe saved export path")
    return name


def rpc_fields(wire):
    request = ExportTraceServiceRequest()
    request.ParseFromString(wire)
    counts = Counter()
    signatures = Counter()
    for resource in request.resource_spans:
        service = next((a.value.string_value for a in resource.resource.attributes
                        if a.key == "service.name"), "")
        for scope in resource.scope_spans:
            for span in scope.spans:
                attrs = {a.key: a.value.string_value for a in span.attributes
                         if a.value.WhichOneof("value") == "string_value"}
                counts["spans"] += 1
                for key in ("rpc.system", "rpc.system.name", "rpc.method"):
                    if key in attrs:
                        counts[key] += 1
                if "rpc.system" in attrs or "rpc.system.name" in attrs:
                    signatures[(service, str(span.kind), attrs.get("rpc.system", ""),
                                attrs.get("rpc.system.name", ""), attrs.get("rpc.method", ""))] += 1
    return counts, signatures


def rpc_graph_facts(model):
    rows = []
    for operation, contract in CONTRACTS.items():
        for call in contract["required_calls"]:
            if call.get("protocol") != "grpc":
                continue
            caller = unique_service(model, call["caller"])
            callee = unique_service(model, call["callee"])
            matches = [e for e in model["edges"]
                       if caller and e["from"] == caller
                       and matches_call_hint(e.get("identity") or {}, call["operation_hint"],
                                             permitted_services=tuple(call["callee"]))[0]]
            rows.append({"operation": operation, "call_id": call["call_id"],
                         "observed_caller": caller, "observed_callee": callee,
                         "matching_method_edges": [
                             {"id": e["id"], "to": e["to"],
                              "is_declared_observed_callee": callee is not None and e["to"] == callee,
                              "identity": e.get("identity")} for e in matches]})
    return {"services": len(model["services"]), "edges": len(model["edges"]),
            "endpoints": len(model["endpoints"]),
            "grpc_edges": [e for e in model["edges"]
                           if (e.get("identity") or {}).get("protocol") == "grpc"],
            "grpc_endpoints": [e for e in model["endpoints"] if e.get("method") == "GRPC"],
            "declared_rpc_method_coverage": rows,
            "interpretation": "Observed method edges only; not full operation admission or causal ancestry."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--old-binary", type=Path, required=True)
    parser.add_argument("--new-binary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    metadata = json.loads(args.metadata.read_text())
    if (metadata.get("id") != ARTIFACT or metadata.get("workflow_run", {}).get("id") != SOURCE_RUN
            or metadata.get("workflow_run", {}).get("head_sha") != SOURCE_SHA
            or metadata.get("digest") != "sha256:" + ZIP_SHA
            or args.archive.stat().st_size != metadata["size_in_bytes"]
            or digest(args.archive) != ZIP_SHA):
        raise ValueError("immutable source identity differs")
    raw_counts, input_counts = Counter(), Counter()
    raw_signatures, input_signatures = Counter(), Counter()
    copies = []
    with zipfile.ZipFile(args.archive) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("duplicate ZIP member")
        manifest_wire = archive.read(INPUT_MANIFEST)
        manifest = json.loads(manifest_wire)
        if manifest["selection_by_source"] != {"ebpf": "all_frozen_source_records"}:
            raise ValueError("diagnosis requires the complete frozen eBPF input")
        local_manifest = copy.deepcopy(manifest)
        for entry, local in zip(manifest["exports"], local_manifest["exports"], strict=True):
            name = member_name(entry["path"])
            wire = archive.read(name)
            if hashlib.sha256(wire).hexdigest() != entry["sha256"]:
                raise ValueError("frozen input hash differs")
            if entry.get("content_type") != "application/x-protobuf":
                raise ValueError("fixed source was not protobuf")
            counts, signatures = rpc_fields(wire)
            input_counts.update(counts)
            input_signatures.update(signatures)
            raw_name = member_name(entry["raw_file"])
            raw = archive.read(raw_name)
            if hashlib.sha256(raw).hexdigest() != entry["raw_sha256"]:
                raise ValueError("original collector wire hash differs")
            counts, signatures = rpc_fields(raw)
            raw_counts.update(counts)
            raw_signatures.update(signatures)
            target = args.out / "inputs" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(wire)
            local["path"] = str(target.resolve())
            copies.append({"member": name, "sha256": entry["sha256"], "bytes": len(wire),
                           "raw_member": raw_name, "raw_sha256": entry["raw_sha256"]})
        if input_counts["spans"] != manifest["observations"]:
            raise ValueError("saved full-prefix observation count differs")
        write_json(args.out / "input-proof.json", {
            "artifact_id": ARTIFACT, "source_run": SOURCE_RUN, "source_sha": SOURCE_SHA,
            "whole_zip_sha256_verified": ZIP_SHA,
            "manifest_sha256": hashlib.sha256(manifest_wire).hexdigest(),
            "original_manifest": manifest,
            "copies": copies, "raw_field_counts": dict(raw_counts),
            "input_field_counts": dict(input_counts),
            "rpc_signatures_identical_raw_and_input": raw_signatures == input_signatures,
            "raw_rpc_signatures": [{"service": key[0], "kind": key[1], "rpc.system": key[2],
                                    "rpc.system.name": key[3], "rpc.method": key[4], "count": count}
                                   for key, count in sorted(raw_signatures.items())],
            "rpc_signatures": [{"service": key[0], "kind": key[1], "rpc.system": key[2],
                                "rpc.system.name": key[3], "rpc.method": key[4], "count": count}
                               for key, count in sorted(input_signatures.items())]})
    facts = {}
    request_sequences = {}
    for label, binary in (("old", args.old_binary), ("new", args.new_binary)):
        folder = args.out / label
        model, quality = replay(binary, local_manifest, folder, "otel_demo-deployment",
                                prefix="observed",
                                source_profile={"source_id": "ebpf", "input_type": "ebpf-otlp"})
        command = json.loads((folder / "observed-runtime" / "replay-command.json").read_text())
        request_sequences[label] = [(r["content_sha256"], r["content_bytes"])
                                    for r in command["accepted_ingest_requests"]]
        facts[label] = {**rpc_graph_facts(model), "binary_sha256": digest(binary),
                        "model_sha256": digest(folder / "observed.json"),
                        "ingest": command["ingest"]}
        write_json(args.out / "comparison-partial.json", facts)
    if request_sequences["old"] != request_sequences["new"]:
        raise ValueError("old/new accepted input sequences differ")
    facts.update({"same_ordered_accepted_input": True,
                  "elapsed_seconds": time.monotonic() - started,
                  "claim": "Fixed saved-input engineering diagnosis; no new forecasts or outcomes."})
    write_json(args.out / "comparison.json", facts)


if __name__ == "__main__":
    main()
