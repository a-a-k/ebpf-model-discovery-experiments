"""Read complete saved DSB fit prefixes; no replay, fitting, scoring or traffic."""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import time
import zipfile

import yaml

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


def native_span_fields(wire, content_type, encoding="", *, json_id_encoding="hex"):
    """Independent literal wire projection, reused from the saved shipping audit."""
    if encoding == "gzip":
        wire = gzip.decompress(wire)
    if "json" in content_type:
        if json_id_encoding not in ("hex", "base64"):
            raise ValueError("unknown original JSON identifier encoding")
        payload, id_encoding = json.loads(wire), json_id_encoding
    else:
        message = ExportTraceServiceRequest()
        message.ParseFromString(wire)
        payload, id_encoding = MessageToDict(message), "base64"
    def identifier(value):
        return base64.b64decode(value).hex() if value and id_encoding == "base64" else value.lower()
    for ri, resource in enumerate(payload.get("resourceSpans", [])):
        attrs = resource.get("resource", {}).get("attributes", [])
        names = {json.dumps(item.get("value"), sort_keys=True)
                 for item in attrs if item.get("key", "") == "service.name"}
        service = json.loads(next(iter(names))).get("stringValue") if len(names) == 1 else None
        for si, scope in enumerate(resource.get("scopeSpans", resource.get("instrumentationLibrarySpans", []))):
            for pi, span in enumerate(scope.get("spans", [])):
                fields = {"resource": resource.get("resource", {}),
                          "resource_schema_url": resource.get("schemaUrl", ""),
                          "scope": scope.get("scope", scope.get("instrumentationLibrary", {})),
                          "scope_schema_url": scope.get("schemaUrl", ""),
                          "span": copy.deepcopy(span)}
                for key in ("traceId", "spanId", "parentSpanId"):
                    fields["span"][key] = identifier(span.get(key, ""))
                yield {"service": service, "fields": fields,
                       "locator": {"resource": ri, "scope": si, "span": pi}}


def retained_toolchain(root):
    """Same direct/packed layout handling as the existing saved shipping audit."""
    if (root / "toolchain").is_dir():
        return {"layout": "retained_directory", "unpacked": False,
                "integrity": "individual scientific/input files are checked against the original freeze"}
    return unpack(root / "toolchain-package", root / "toolchain", kind="toolchain")


def catalog_summary(rows, source_domain, native_rows):
    """Literal parent candidates; do not choose a conflicting variant or infer edges."""
    def usable(value, size):
        return len(value) == size and bool(value.strip("0")) and all(c in "0123456789abcdef" for c in value)
    def index(items):
        result = {}
        for key, item in items.items():
            span = item["fields"]["span"]
            if usable(span["traceId"], 32) and usable(span["spanId"], 16):
                result.setdefault((span["traceId"], span["spanId"]), []).append({"signature_sha256": key, **item})
        return result
    local, sdk = index(rows), index(native_rows)
    selected = []
    for signature, item in rows.items():
        span = item["fields"]["span"]
        names = [a.get("value", {}).get("stringValue") for a in item["fields"]["resource"].get("attributes", [])
                 if a.get("key", "") == "service.name"]
        methods = [a.get("value", {}).get("stringValue") for a in span.get("attributes", [])
                   if a.get("key", "") == "rpc.method"]
        if ("product-catalog" not in names or span.get("kind") not in (2, "SPAN_KIND_SERVER")
                or not (any(value and value.split("/")[-1] == "GetProduct" for value in methods)
                        or span.get("name", "").split("/")[-1] == "GetProduct")):
            continue
        key = span["traceId"], span["parentSpanId"]
        valid = usable(key[0], 32) and usable(key[1], 16)
        selected.append({"signature_sha256": signature, **item, "source_domain": source_domain,
            "usable_parent_identity": valid,
            "actual_same_domain_same_trace_parent_variants": local.get(key, []) if valid else [],
            "same_ids_in_native_frozen_input_other_domain": sdk.get(key, []) if valid else [],
            "native_input_domain": "", "native_raw_prefix_rescanned": False})
    return {"catalog_get_product_server_variants": selected,
            "literal_same_identity_with_multiple_field_variants": sum(len(v) > 1 for v in local.values()),
            "scope": "All literal variants retained. Different timing/resource fields are not automatically Bering ambiguity. Native candidates have a different source domain; no cross-domain parent or graph edge is constructed."}


def catalog_parent_facts(root, frozen, rows, accepted_sequence, relocate):
    """Bind literal raw/input identities to the original accepted prefix and domains."""
    checked = {}
    def saved(name):
        if frozen.get(name) != sha(root / name):
            raise ValueError("catalog source is not frozen: " + name)
        checked[name] = frozen[name]
        return read(root / name)
    if saved("toolchain/static-inputs.json")["tool_pins"]["Bering"] != "66ca3af1fe581839e525fb9cc5600a1edd6ca8fb":
        raise ValueError("catalog domain interpretation requires its exact original Bering pin")
    replay_name = "toolchain/discovery/ebpf/raw/observed-runtime/replay-command.json"
    replay = saved(replay_name)
    config_name = "toolchain/discovery/ebpf/raw/observed-runtime/serve.yaml"
    if frozen.get(config_name) != sha(root / config_name):
        raise ValueError("catalog source config is not frozen")
    checked[config_name] = frozen[config_name]
    config = yaml.safe_load((root / config_name).read_text())
    source = next(s for s in config["sources"] if s["id"] == "ebpf")
    if (source["type"] != "ebpf-otlp" or source["domain"] != replay["source_domain"]
            or replay["source_profile"] != {"source_id": "ebpf", "input_type": "ebpf-otlp"}
            or replay["status"] != "complete" or replay["returncode"] != 0):
        raise ValueError("catalog Bering source/domain differs")
    effective_domain = f"ebpf-otlp:{len(source['id'])}:{source['id']}:{source['domain']}"
    input_spans = sum(row["count"] for row in rows["input"].values())
    if (replay["input_observations"] != input_spans or replay["ingest"]["spans"] != input_spans
            or replay["ingest"]["dropped_spans"] or replay["ingest"]["late_spans"]):
        raise ValueError("catalog actual Bering ingest differs from the complete input")
    sequence = replay["accepted_request_sequence"]
    name = original_member(sequence["path"])
    if name != "toolchain/discovery/ebpf/raw/observed-runtime/accepted-request-sequence.jsonl":
        raise ValueError("catalog accepted sequence has a different publication locator")
    if (frozen.get(name) != sequence["sha256"] or sha(root / name) != sequence["sha256"]
            or (root / name).stat().st_size != sequence["bytes"]):
        raise ValueError("catalog accepted request sequence changed")
    checked[name] = sequence["sha256"]
    accepted = [json.loads(line) for line in (root / name).read_text().splitlines()]
    if (len(accepted) != sequence["requests"] or not accepted
            or [(r["content_sha256"], r["content_bytes"]) for r in accepted] != accepted_sequence
            or any(r["http_status"] != 200 or r["export_index"] != index
                   or r["endpoint"] != "/sources/ebpf/v1/traces" for index, r in enumerate(accepted))):
        raise ValueError("catalog actual Bering accepted a different complete frozen input")
    native_rows, native_spans, native_requests = {}, 0, 0
    native_name = "toolchain/inputs/native/raw/observations.json"
    manifest = saved(native_name)
    for name, expected in frozen.items():
        if name.startswith("toolchain/inputs/native/raw/"):
            if sha(root / name) != expected:
                raise ValueError("native frozen input for catalog comparison changed")
            checked[name] = expected
    for entry, body in _ordered_manifest_requests(relocate(copy.deepcopy(manifest)), materialize=False):
        try:
            wire = body.read() if body is not None else Path(entry["path"]).read_bytes()
        finally:
            if body is not None:
                body.close()
        if entry["source"] != "native" or hashlib.sha256(wire).hexdigest() != entry["sha256"]:
            raise ValueError("native catalog comparison input differs")
        native_requests += 1
        for item in native_span_fields(wire, entry["content_type"], entry.get("content_encoding", "")):
            native_spans += 1
            signature = hashlib.sha256(json.dumps(item["fields"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            row = native_rows.setdefault(signature, {"service": item["service"], "fields": item["fields"], "count": 0, "witnesses": []})
            row["count"] += 1
            if len(row["witnesses"]) < 2:
                row["witnesses"].append({"request_path": entry["path"], "request_sha256": entry["sha256"], "span": item["locator"]})
    if native_spans != manifest["observations"]:
        raise ValueError("native catalog comparison input count differs")
    counts = {role: {signature: row["count"] for signature, row in items.items()} for role, items in rows.items()}
    identities = {role: Counter() for role in rows}
    for role, items in rows.items():
        for row in items.values():
            span = row["fields"]["span"]
            identities[role][json.dumps({key: span.get(key) for key in ("traceId", "spanId", "parentSpanId", "kind", "name")}, sort_keys=True)] += row["count"]
    summaries = {role: catalog_summary(items, effective_domain, native_rows) for role, items in rows.items()}
    # Retain existing summaries and binding JSON; no new evaluation is performed.
    paths = {root / "toolchain/static-inputs.json"}
    for leaf in ("observed.json", "observed.bering-raw.json", "observed.signal-quality.json", "observed.supplied-aliases.json"):
        paths.update(root.glob("toolchain/discovery/*/raw/" + leaf))
    paths.update(root.glob("toolchain/*/raw/*/binding.json"))
    copied = {}
    for path in paths:
        name = path.relative_to(root).as_posix()
        saved(name)
        copied[name] = {"sha256": sha(path), "json": read(path)}
    if any(sha(root / name) != expected for name, expected in checked.items()):
        raise ValueError("catalog sources changed during read-only diagnosis")
    return {"raw_input_all_literal_field_counts_equal": counts["original"] == counts["input"],
            "raw_input_trace_span_parent_kind_name_counts_equal": identities["original"] == identities["input"],
            "all_literal_field_variant_counts": counts, "identity_field_counts": {r: dict(v) for r, v in identities.items()},
            "catalog": summaries, "declared_collection_domain": source["domain"],
            "source_domain": effective_domain, "native_input_domain": "",
            "domain_derivation": {"bering_pin": "66ca3af1fe581839e525fb9cc5600a1edd6ca8fb",
                "ebpf": "internal/connectors/ebpf/load.go:69-100; declared source ID/domain are added by the eBPF normalization profile",
                "native": "internal/connectors/otlp/http.go:114-150 leaves SourceDomain at its empty Go string default; runtime/service.go:244 uses this decoder for /v1/traces",
                "source_kind": "eBPF profile also sets SourceKind=ebpf, while ordinary OTLP leaves it empty; routing everything through ordinary OTLP would change endpoint/peer handling and is not full-model equivalence",
                "parent_key": "internal/discovery/discovery.go:276-293: (SourceDomain, trace ID, span ID)",
                "different_internal_domains_do_not_prove_independent_trace_universes": True,
                "cross_source_parent_joins_performed": False},
            "native_comparison_requests": native_requests, "native_comparison_spans": native_spans,
            "native_raw_prefix_rescanned": False, "accepted_request_sequence": {"requests": len(accepted), "sha256": sequence["sha256"], "all_request_sha256_bytes_equal": True},
            "frozen_source_files": checked, "original_interpretation_json": copied,
            "no_new_graph_ancestry_prediction_or_scoring": True}


def audit(root, compact, *, catalog=False):
    package_proof = retained_toolchain(root)
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
    literal_rows = {"input": {}, "original": {}}
    accepted_sequence = []
    def catalog_fields(wire, entry, locator, role):
        if not catalog:
            return
        for item in native_span_fields(wire, entry["content_type"], entry.get("content_encoding", "")):
            signature = hashlib.sha256(json.dumps(item["fields"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            row = literal_rows[role].setdefault(signature, {"service": item["service"], "fields": item["fields"], "count": 0, "witnesses": []})
            row["count"] += 1
            if len(row["witnesses"]) < 2:
                row["witnesses"].append({"request": locator, "span": item["locator"]})
    for group in groups:
        for entry, body in _ordered_manifest_requests(relocate(copy.deepcopy(group)), materialize=False):
            try:
                wire = body.read() if body is not None else Path(entry["path"]).read_bytes()
            finally:
                if body is not None:
                    body.close()
            if hashlib.sha256(wire).hexdigest() != entry["sha256"]:
                raise ValueError("frozen request body differs")
            if catalog and (entry["source"] != "ebpf" or entry.get("raw_file_role") or "json" in entry["content_type"]):
                raise ValueError("fixed catalog diagnosis requires original OBI protobuf receiver bodies")
            accepted_sequence.append((entry["sha256"], len(wire)))
            catalog_fields(wire, entry, {k: entry[k] for k in ("path", "sha256", "request_order") if k in entry}, "input")
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
                    catalog_fields(raw, entry, raw_proofs[key], "original")
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
    result = {"package_proof": package_proof, "frozen_input_files": verified_files,
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
    if catalog:
        result["catalog_parent_diagnosis"] = catalog_parent_facts(root, frozen, literal_rows, accepted_sequence, relocate)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--cell", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--catalog", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    cell = read(args.cell)
    for role in ("full", "compact"):
        extract(args.source / (role + ".zip"), read(args.source / (role + "-api.json")),
                cell[role], args.source / role)
    if args.catalog:
        status = read(args.source / "compact/status.json")
        if (cell["collector"] != "obi" or cell["system"] != "otel_demo" or cell["mode"] not in ("absent", "partial")
                or status["commit"] != cell["full"]["head_sha"] or status["run_id"] != str(cell["full"]["run_id"])
                or status["collector"] != cell["collector"] or status["system"] != cell["system"]
                or status["mode"] != cell["mode"] or status["seed"] != cell["seed"]
                or (args.source / "compact/status.json").read_bytes() != (args.source / "full/status.json").read_bytes()
                or not read(args.source / "full/freeze-integrity.json")["all_unchanged"]):
            raise ValueError("fixed catalog source differs")
    facts = audit(args.source / "full", args.source / "compact", catalog=args.catalog)
    facts.update(cell=cell, elapsed_seconds=time.monotonic() - started,
                 claim="Saved-evidence diagnosis; no new scientific fit, forecast, outcome score or admission.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
    if args.catalog and not facts["catalog_parent_diagnosis"]["raw_input_trace_span_parent_kind_name_counts_equal"]:
        raise ValueError("catalog raw/input identity field multisets differ; inspect retained facts")


if __name__ == "__main__":
    main()
