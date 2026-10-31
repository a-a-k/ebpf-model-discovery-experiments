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
import shutil
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
    for folder in ("toolchain", "observations", "runtime-identity-v5", "native"):
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
            or metadata.get("expired") is not False
            or metadata["size_in_bytes"] != expected["bytes"]
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
    """Independent literal wire projection; do not use the experiment normalizer."""
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


def shipping_summary(rows):
    """Retain actual variants and parent matches; never construct missing ancestry."""
    by_identity = {}
    def usable(value, length):
        return (len(value) == length and bool(value.strip("0"))
                and all(character in "0123456789abcdef" for character in value))
    for key, item in rows.items():
        span = item["fields"]["span"]
        if usable(span["traceId"], 32) and usable(span["spanId"], 16):
            by_identity.setdefault((span["traceId"], span["spanId"]), []).append(key)
    selected = []
    for key, item in rows.items():
        literal_names = [attribute.get("value", {}).get("stringValue")
                         for attribute in item["fields"]["resource"].get("attributes", [])
                         if attribute.get("key", "") == "service.name"]
        if not set(literal_names) & {"checkout", "shipping"}:
            continue
        span = item["fields"]["span"]
        parents = by_identity.get((span["traceId"], span["parentSpanId"]), []) if (
            usable(span["traceId"], 32) and usable(span["parentSpanId"], 16)) else []
        selected.append({"signature_sha256": key, **item,
            "actual_same_trace_parent_variants": [{"signature_sha256": parent, **rows[parent]} for parent in parents]})
    return {"unique_span_field_variants": len(rows),
            "ambiguous_same_trace_span_identities": sum(len(value) > 1 for value in by_identity.values()),
            "checkout_shipping_variants": selected,
            "ancestry_scope": "Literal same-trace parent-span-ID matches, including all conflicting variants; no invented ancestry."}


def original_jsonl_records(raw):
    """Read the actual direct-SDK JSONL prefix, without treating it as one export."""
    offset = 0
    for line in raw.splitlines(keepends=True):
        if not line.endswith(b"\n"):
            raise ValueError("indexed native source has an incomplete JSONL record")
        if line.strip():
            document = json.loads(line)
            yield document.get("payload", document), document.get("id_encoding", "hex"), {
                "offset": offset, "length": len(line),
                "raw_record_sha256": hashlib.sha256(line).hexdigest()}
        offset += len(line)


def retained_toolchain(root):
    """Direct layouts already contain the original tree; packed layouts do not."""
    if (root / "toolchain").is_dir():
        return {"layout": "retained_directory", "unpacked": False,
                "integrity": "individual scientific/input files are checked against the original freeze"}
    return unpack(root / "toolchain-package", root / "toolchain", kind="toolchain")


def ebpf_parent_matches(root, frozen, wanted, relocate):
    """Find literal missing native parent IDs in the same pretarget eBPF input."""
    checked = {}
    for name, expected in frozen.items():
        if name.startswith("toolchain/inputs/ebpf/raw/"):
            if sha(root / name) != expected:
                raise ValueError("frozen eBPF comparison input changed")
            checked[name] = expected
    manifest = read(root / "toolchain/inputs/ebpf/raw/observations.json")
    if manifest.get("selection_by_source") != {"ebpf": "all_frozen_source_records"}:
        raise ValueError("eBPF comparison is not the complete frozen source")
    groups = []
    for proof in manifest.get("ordered_request_group_manifests") or []:
        path = root / original_member(proof["path"])
        if sha(path) != proof["sha256"] or path.stat().st_size != proof["bytes"]:
            raise ValueError("eBPF comparison source group changed")
        groups.append(read(path))
    matches, spans, requests = [], 0, 0
    for group in groups or [manifest]:
        for entry, body in _ordered_manifest_requests(relocate(copy.deepcopy(group)), materialize=False):
            try:
                wire = body.read() if body is not None else Path(entry["path"]).read_bytes()
            finally:
                if body is not None:
                    body.close()
            if entry["source"] != "ebpf" or hashlib.sha256(wire).hexdigest() != entry["sha256"]:
                raise ValueError("eBPF comparison request changed")
            requests += 1
            selected = []
            for span in native_span_fields(wire, entry["content_type"], entry.get("content_encoding", "")):
                spans += 1
                fields = span["fields"]["span"]
                if (fields["traceId"], fields["spanId"]) in wanted:
                    selected.append(span)
            if not selected:
                continue
            if entry.get("raw_file_role") or entry.get("raw_record_sha256"):
                raise ValueError("fixed OBI identity comparison requires its original receiver body")
            raw_name = original_member(entry["raw_file"])
            raw = (root / raw_name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != entry["raw_sha256"]:
                raise ValueError("matched eBPF original receiver body changed")
            originals = list(native_span_fields(raw, entry["content_type"], entry.get("content_encoding", "")))
            for span in selected:
                fields = span["fields"]["span"]
                original_matches = [row for row in originals
                    if all(row["fields"]["span"][key] == fields[key] for key in ("traceId", "spanId"))]
                if not original_matches:
                    raise ValueError("matched eBPF input identity is absent from original body")
                matches.append({"input_span": span, "original_variants": original_matches,
                    "input_request_sha256": entry["sha256"], "request_order": entry.get("request_order"),
                    "original_body": {"member": raw_name, "sha256": entry["raw_sha256"], "bytes": len(raw)}})
    if spans != manifest["observations"]:
        raise ValueError("eBPF comparison input span count differs")
    return {"frozen_input_files": checked, "requests": requests, "spans": spans,
            "wanted_native_parent_identities": [{"trace_id": trace, "span_id": sid} for trace, sid in sorted(wanted)],
            "matches": matches,
            "scope": "Literal same-trace span IDs present in frozen eBPF input and its original receiver bodies. Matching identifies existing spans; it does not establish who wrote a traceparent header or create ancestry."}


def audit(root, compact, *, source_arm="ebpf"):
    if source_arm not in ("ebpf", "native"):
        raise ValueError("unsupported saved audit source arm")
    package_proof = retained_toolchain(root)
    manifest_hashes = read(compact / "evaluation-manifest.json")["files_sha256"]
    for name in ("evaluation-v5.json", "status.json", "toolchain/forecasts.json", "evidence-v4.json", "freeze-integrity.json"):
        if sha(compact / name) != manifest_hashes[name]:
            raise ValueError("compact source hash differs: " + name)
    frozen = read(root / "freeze-integrity.json")["sha256_by_path"]
    if (sha(compact / "freeze-integrity.json") != sha(root / "freeze-integrity.json")
            or sha(compact / "toolchain/forecasts.json") != sha(root / "toolchain/forecasts.json")):
        raise ValueError("compact and full frozen sources differ")
    for name in ("toolchain/forecasts.json", f"toolchain/discovery/{source_arm}/raw/observed.json"):
        if sha(root / name) != frozen[name]:
            raise ValueError("saved scientific output differs from pre-target freeze")
    verified_files = {}
    for name, expected in frozen.items():
        if name.startswith(f"toolchain/inputs/{source_arm}/raw/"):
            if sha(root / name) != expected:
                raise ValueError("pre-target input changed: " + name)
            verified_files[name] = expected

    def relocate(value):
        if isinstance(value, dict):
            return {key: relocate(item) for key, item in value.items()}
        if isinstance(value, list):
            return [relocate(item) for item in value]
        if (isinstance(value, str) and value.startswith("/") and any(
                "/" + folder + "/" in value for folder in ("toolchain", "observations", "runtime-identity-v5", "native"))):
            return str((root / original_member(value)).resolve())
        return value

    manifest_path = root / f"toolchain/inputs/{source_arm}/raw/observations.json"
    manifest = read(manifest_path)
    if manifest.get("selection_by_source") != {source_arm: "all_frozen_source_records"}:
        raise ValueError("diagnosis requires all frozen selected source records")
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
    native_counts = {"input": Counter(), "original": Counter()}
    native_rows = {"input": {}, "original": {}}
    native_record_claims, native_record_sources = Counter(), Counter()
    accepted_sha_sequence = []
    def native_fields(wire, entry, locator, role, *, json_id_encoding="hex"):
        if source_arm != "native":
            return
        for span in native_span_fields(wire, entry["content_type"], entry.get("content_encoding", ""), json_id_encoding=json_id_encoding):
            encoded = json.dumps(span["fields"], sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(encoded.encode()).hexdigest()
            native_counts[role][digest] += 1
            saved = native_rows[role].setdefault(digest, {"service": span["service"],
                "fields": span["fields"], "count": 0, "witnesses": []})
            saved["count"] += 1
            if len(saved["witnesses"]) < 2:
                saved["witnesses"].append({"request": locator, "span": span["locator"]})
    for group in groups:
        for entry, body in _ordered_manifest_requests(relocate(copy.deepcopy(group)), materialize=False):
            if entry["source"] != source_arm:
                raise ValueError("frozen input request has a different source arm")
            try:
                wire = body.read() if body is not None else Path(entry["path"]).read_bytes()
            finally:
                if body is not None:
                    body.close()
            if hashlib.sha256(wire).hexdigest() != entry["sha256"]:
                raise ValueError("frozen request body differs")
            accepted_sha_sequence.append(entry["sha256"])
            native_fields(wire, entry, {k: entry[k] for k in ("path", "sha256", "request_order") if k in entry}, "input")
            inputs.update(inventory(wire, entry["content_type"], entry.get("content_encoding", ""),
                joints=input_joints, witnesses=input_witnesses,
                locator={k: entry[k] for k in ("path", "request_order", "sha256", "offset", "length", "shard") if k in entry}))
            requests += 1
            raw_name = original_member(entry["raw_file"])
            direct_native_jsonl = source_arm == "native" and "raw_record_sha256" in entry
            prefix = entry.get("raw_prefix_bytes") if entry.get("raw_file_role") or direct_native_jsonl else None
            key = (raw_name, prefix, entry["raw_sha256"])
            if direct_native_jsonl:
                if type(prefix) is not int or prefix < 0:
                    raise ValueError("direct native source lacks an indexed byte prefix")
                native_record_claims[(key, entry["raw_record_sha256"])] += 1
            if key not in raw_proofs:
                with (root / raw_name).open("rb") as stream:
                    raw = stream.read() if prefix is None else stream.read(prefix)
                if prefix is not None and len(raw) != prefix:
                    raise ValueError("original indexed source prefix is shorter than declared")
                if hashlib.sha256(raw).hexdigest() != entry["raw_sha256"]:
                    raise ValueError("original source bytes differ")
                raw_proofs[key] = {"member": raw_name, "prefix_bytes": prefix,
                                   "sha256": entry["raw_sha256"]}
                if direct_native_jsonl:
                    raw_proofs[key]["representation"] = "original_direct_sdk_otlp_jsonl"
                    for payload, id_encoding, record in original_jsonl_records(raw):
                        body = json.dumps(payload).encode()
                        fields = list(native_span_fields(body, "application/json", json_id_encoding=id_encoding))
                        if fields:
                            native_record_sources[(key, record["raw_record_sha256"])] += 1
                        native_fields(body, {"content_type": "application/json"},
                            {**raw_proofs[key], **record}, "original", json_id_encoding=id_encoding)
                        originals.update(inventory(body, "application/json",
                            joints=original_joints, witnesses=original_witnesses,
                            locator={**raw_proofs[key], **record}))
                elif not entry.get("raw_file_role"):
                    native_fields(raw, entry, raw_proofs[key], "original")
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
    observed_path = root / f"toolchain/discovery/{source_arm}/raw/observed.json"
    result = {"package_proof": package_proof, "frozen_input_files": verified_files,
        "frozen_requests": requests, "input_inventory": dict(inputs),
        "original_otlp_inventory": dict(originals), "original_source_proofs": list(raw_proofs.values()),
        "input_joint_signatures": dict(input_joints), "input_witnesses": input_witnesses,
        "original_joint_signatures": dict(original_joints), "original_witnesses": original_witnesses,
        "deepflow_full_capture_accounting": deepflow_accounting(root) if source_arm == "ebpf" else None,
        "graphs": evaluation["evidence"]["graphs"],
        "actual_observed_ebpf_graph": read(observed_path),
        "actual_observed_ebpf_graph_sha256": sha(observed_path),
        "effective_parser_log_evidence": log_facts,
        "collector_provenance": read(compact / "observations/collector.json"),
        "frozen_forecasts": read(compact / "toolchain/forecasts.json"),
        "scope": "Complete frozen eBPF fit input; DeepFlow rejected accounting spans the full capture and is labeled by capture stage. Parent counts describe fields, not confirmed ancestry. No missing record establishes interception impossibility."}
    if source_arm == "native":
        if native_record_claims != native_record_sources:
            raise ValueError("native input does not match all original nonempty indexed JSONL records")
        replay_path = root / "toolchain/discovery/native/raw/observed-runtime/replay-command.json"
        replay_name = replay_path.relative_to(root).as_posix()
        if sha(replay_path) != frozen[replay_name]:
            raise ValueError("native Bering command is not frozen")
        replay = read(replay_path)
        sequence = replay["accepted_request_sequence"]
        sequence_path = root / original_member(sequence["path"])
        if sha(sequence_path) != sequence["sha256"] or sequence_path.stat().st_size != sequence["bytes"]:
            raise ValueError("native Bering accepted sequence changed")
        accepted = [json.loads(line) for line in sequence_path.read_text().splitlines()]
        if (len(accepted) != sequence["requests"] or [row["content_sha256"] for row in accepted] != accepted_sha_sequence
                or any(row["http_status"] >= 400 or row["endpoint"] != "/v1/traces" for row in accepted)
                or replay["status"] != "complete" or replay["input_observations"] != manifest["observations"]
                or replay["ingest"]["spans"] != manifest["observations"] or replay["ingest"]["dropped_spans"]):
            raise ValueError("native Bering accepted input differs from audited prefix")
        result.update(source_arm="native", actual_observed_native_graph=result.pop("actual_observed_ebpf_graph"),
            actual_observed_native_graph_sha256=result.pop("actual_observed_ebpf_graph_sha256"),
            native_raw_input_span_fields_equal=native_counts["input"] == native_counts["original"],
            native_field_variant_counts={role: dict(counts) for role, counts in native_counts.items()},
            native_shipping={role: shipping_summary(rows) for role, rows in native_rows.items()},
            bering_accepted_sequence={"requests": len(accepted), "sha256": sequence["sha256"],
                "source_manifest_sequence_equal": True, "command_sha256": sha(replay_path)},
            original_native_jsonl_record_claims_verified=sum(native_record_claims.values()),
            scope="Complete frozen native fit input and its original retained SDK source (direct OTLP JSONL or receiver bodies, explicitly labelled in proofs). Literal resource/scope/span fields and same-trace parent-ID variants are compared before inspecting the original graph. Direct file exports are not claimed to be captured HTTP/protobuf wire. No replay, new fit, scoring, admission or invented identity.")
        wanted = {(row["fields"]["span"]["traceId"], row["fields"]["span"]["parentSpanId"])
                  for row in result["native_shipping"]["original"]["checkout_shipping_variants"]
                  if row["service"] == "shipping" and row["fields"]["span"].get("kind") in (2, "SPAN_KIND_SERVER")
                  and row["fields"]["span"]["parentSpanId"].strip("0")
                  and not row["actual_same_trace_parent_variants"]}
        if wanted:
            result["same_prefix_ebpf_parent_identity_comparison"] = ebpf_parent_matches(root, frozen, wanted, relocate)
    return result


def copy_saved_bindings(root, out):
    """Copy original frozen JSON for interpretation; no binding is recomputed."""
    frozen = read(root / "freeze-integrity.json")["sha256_by_path"]
    paths = {root / "toolchain/static-inputs.json",
             root / "runtime-identity-v5/supplied-service-aliases-training.json",
             root / "runtime-identity-v5/supplied-service-alias-admission-training.json"}
    for leaf in ("observed.json", "observed.signal-quality.json",
                 "observed.bering-raw.json", "observed.supplied-aliases.json"):
        paths.update(root.glob("toolchain/discovery/*/*/" + leaf))
    for leaf in ("entry-evidence.json", "binding.json"):
        paths.update(root.glob("toolchain/*/*/*/" + leaf))
    copied = {}
    for path in sorted(paths):
        name = path.relative_to(root).as_posix()
        if not path.is_file() or frozen.get(name) != sha(path):
            raise ValueError("saved interpretation file is not frozen: " + name)
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        if sha(target) != frozen[name]:
            raise ValueError("saved interpretation copy differs: " + name)
        copied[name] = {"sha256": frozen[name], "bytes": target.stat().st_size}
    return copied


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
    facts = audit(args.source / "full", args.source / "compact", source_arm=cell.get("source_arm", "ebpf"))
    facts["copied_original_binding_files"] = copy_saved_bindings(
        args.source / "full", args.out.parent / "selected")
    facts.update(cell=cell, elapsed_seconds=time.monotonic() - started,
                 claim="Saved-evidence diagnosis; no new scientific fit, forecast, outcome score or admission.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
