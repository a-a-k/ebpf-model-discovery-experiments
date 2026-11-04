"""Verify saved main-review facts without replay, fitting, scoring, or admission."""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import heapq
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import tarfile
import uuid
import yaml

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from ebpf_discovery.report_v5 import (CLOSED_CAPTURE_RECOVERY_SOURCE, _saved_capture_identity,
    IDENTICAL_INPUT_DISCOVERY_SOURCE, UPLOAD_HOLD_PARENT_PROOF_SOURCE, CLOSED_CAPTURE_COMPACT_UNION, CLOSED_CAPTURE_COMPACT_UNIONS, _closed_union_profile, _closed_union_api_facts, _closed_union_artifact_origin)


PINS = {
    "procrustes": "9648ae3fe9ef24725e665d008c79d0681ce40f85",
    "bering": "70d4145d3e26f11d8b3fb5be8917c50c1c6d8c2a",
    "sheaft": "686a602f4e7b71f3612f1810885e29dd66c8733a",
}
FRESH_HEAD = "0c98bf4520e863ab021b60d00517ee2aa49ab38e"
PREPARED_PARENT_HEAD = "fbbda015cefc4f11ee73f32be6ed661c70375f18"
PREPARED_PORT_HEAD = "13c017bf72a86a6853f93a5b8f503de199bf7865"
PREPARED_GUEST_LOG_HEAD = "1d646f907d0241f25445fcfb4d07d4e0ba89d88b"
IMMUTABLE_PATH_HEAD = "06d7d52bfa4b7768a4cabf02f4e66f109b3a9492"
UPLOADED_CHECKPOINT_COPY_HEAD = "8fa2a454db58af487451c9aead6477adc0ca0485"
CLOSED_FINAL_SNAPSHOT_HEAD = "6eaa441c40253a18f18af76e4e599496927c1739"
STREAMED_CHECKPOINT_HEAD = "f7ba801d70f9d2327031efc6dd0c00b90d252708"
PETCLINIC_WORKER_HEAD = "0565115511b24db1d6bbe71e98784baded772144"
POSTCAPTURE_GUEST_RELEASE_HEAD = "0056b4c8ecb85e8b40c433e63af442133a21f3cc"
CLOSED_POSTCAPTURE_HEAD = "f045cc0adec187ec00443da0bea72b4ec4d2082e"
CLOSED_CAPTURE_RECOVERY_HEAD = CLOSED_CAPTURE_RECOVERY_SOURCE["revision"]
UPLOAD_HOLD_PARENT_PROOF_HEAD = UPLOAD_HOLD_PARENT_PROOF_SOURCE['revision']
IDENTICAL_INPUT_DISCOVERY_HEADS = {IDENTICAL_INPUT_DISCOVERY_SOURCE['revision'], UPLOAD_HOLD_PARENT_PROOF_HEAD}
CLOSED_POSTCAPTURE_CELLS = {(mode, seed) for mode in ("absent", "partial") for seed in (6, 7, 8)} | {("full", 8)}
FRESH_HEADS = {"bf49d464816aa71b7c820a02778117d3e6a0ba9d",
               "a43404ec02c77e9414878632ec6248835cf7a260",
               "6ef079a7a7eac91e464a87a97881a56bc4449e5c",
               "f60cbfe5e19ca88b40e196d8e793ef0e2aac5d5c", FRESH_HEAD, PREPARED_PARENT_HEAD, PREPARED_PORT_HEAD, PREPARED_GUEST_LOG_HEAD, IMMUTABLE_PATH_HEAD, UPLOADED_CHECKPOINT_COPY_HEAD, CLOSED_FINAL_SNAPSHOT_HEAD, STREAMED_CHECKPOINT_HEAD, PETCLINIC_WORKER_HEAD, POSTCAPTURE_GUEST_RELEASE_HEAD, CLOSED_POSTCAPTURE_HEAD, CLOSED_CAPTURE_RECOVERY_HEAD}
FRESH_BERING = "66ca3af1fe581839e525fb9cc5600a1edd6ca8fb"
METADATA_ATTACHMENT_HEADS = {"f60cbfe5e19ca88b40e196d8e793ef0e2aac5d5c", FRESH_HEAD, PREPARED_PARENT_HEAD, PREPARED_PORT_HEAD, PREPARED_GUEST_LOG_HEAD, IMMUTABLE_PATH_HEAD, UPLOADED_CHECKPOINT_COPY_HEAD, CLOSED_FINAL_SNAPSHOT_HEAD, STREAMED_CHECKPOINT_HEAD, PETCLINIC_WORKER_HEAD, POSTCAPTURE_GUEST_RELEASE_HEAD, CLOSED_POSTCAPTURE_HEAD, CLOSED_CAPTURE_RECOVERY_HEAD}
GUEST_PROOF_HEADS = {"6ef079a7a7eac91e464a87a97881a56bc4449e5c",
                     "f60cbfe5e19ca88b40e196d8e793ef0e2aac5d5c", FRESH_HEAD, PREPARED_PARENT_HEAD, PREPARED_PORT_HEAD, PREPARED_GUEST_LOG_HEAD, IMMUTABLE_PATH_HEAD, UPLOADED_CHECKPOINT_COPY_HEAD, CLOSED_FINAL_SNAPSHOT_HEAD, STREAMED_CHECKPOINT_HEAD, PETCLINIC_WORKER_HEAD, POSTCAPTURE_GUEST_RELEASE_HEAD, CLOSED_POSTCAPTURE_HEAD, CLOSED_CAPTURE_RECOVERY_HEAD}
CONTEXT_BASELINE_HEADS = {FRESH_HEAD, PREPARED_PARENT_HEAD, PREPARED_PORT_HEAD, PREPARED_GUEST_LOG_HEAD, IMMUTABLE_PATH_HEAD, UPLOADED_CHECKPOINT_COPY_HEAD, CLOSED_FINAL_SNAPSHOT_HEAD, STREAMED_CHECKPOINT_HEAD, PETCLINIC_WORKER_HEAD, POSTCAPTURE_GUEST_RELEASE_HEAD, CLOSED_POSTCAPTURE_HEAD, CLOSED_CAPTURE_RECOVERY_HEAD}
for _named_heads in (FRESH_HEADS, METADATA_ATTACHMENT_HEADS, GUEST_PROOF_HEADS, CONTEXT_BASELINE_HEADS):
    _named_heads.update(IDENTICAL_INPUT_DISCOVERY_HEADS)
FRESH_GUEST_IMAGE_SHA256 = "04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94"


def _capture_declaration(declaration):
    if declaration['head_sha'] != CLOSED_CAPTURE_RECOVERY_HEAD:
        return declaration
    profile = CLOSED_CAPTURE_RECOVERY_SOURCE
    if ((declaration['collector'], declaration['system'], declaration['mode'], declaration['seed'],
         declaration['run_id']) != ('deepflow', 'otel_demo', 'full', 8, profile['processing_run_id'])
            or declaration.get('scientific_capture_run_id') != int(profile['capture_identity']['run_id'])
            or declaration.get('scientific_capture_head_sha') != profile['capture_identity']['commit']):
        raise ValueError('saved recovery declaration is outside the fixed original full8 case')
    return {**declaration, 'run_id': int(profile['capture_identity']['run_id']),
            'head_sha': profile['capture_identity']['commit']}

COLLECTOR_PINS = {
    "deepflow": {
        "source_version": "v7.2.3",
        "source_commit": "9a1219fa5cf1471ba2ec8742019661567d98002e",
        "image": "deepflowce/deepflow-agent:v7.2.3@sha256:5f72c0996fdb5008fdb8fd0524f427a895fc54c61690b26ba2cae648929ea95a",
    },
    "obi": {
        "source_version": "v0.15.2",
        "image": "otel/ebpf-instrument:v0.15.2@sha256:101b5c773ac84545cac007ce3dbaf38bfb0e7091f26e813c08d649f35dca253e",
    },
    "coroot": {
        "source_version": "1.37.0",
        "source_commit": "89a858a0ee35c4eb938b86d56f23168fb0ac7573",
        "image": "ghcr.io/coroot/coroot-node-agent:1.37.0@sha256:f360c31c5e2fa75550c0029f3c02a0e54b83831bae59201b9fe76bab2fe564b4",
    },
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _safe(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name and "\\" not in name and not path.is_absolute() and ".." not in path.parts)


def _package_selected(name: str, kind: str) -> bool:
    if kind == "handoff":
        # The historical DSB review retains the complete small handoff (35 files),
        # including parent/import/index and worker identity/provenance records.
        return True
    if name in ("execution-summary.json", "forecasts.json", "static-inputs.json",
                "classes/classes-model.json", "classes/classes-family-model.json"):
        return True
    if name.startswith("inputs/") and name.endswith("/observations.json"):
        return True
    if name.startswith("inputs/") and name.endswith("-request-index.jsonl"):
        return True
    if name.startswith("context-baseline/"):
        if name.endswith('/simulation/report.json'):
            return True
        return name.split('/')[-1] in {
            'forecasts.json', 'manifest.json', 'provenance.json', 'union-model.json', 'union-proof.json',
            'observed.json', 'observed.snapshot.json', 'observed.signal-quality.json',
            'canonical.json', 'canonical.signal-quality.json', 'supplied-aliases.json',
            'replay-command.json', 'serve.yaml', 'accepted-request-sequence.jsonl',
            'accepted-stream-requests.jsonl', 'binding.json', 'forecast.json', 'overlay.json',
            'model.json', 'model.signal-quality.json', 'analysis.json', 'predicates.json', 'faults.json', 'simulation.command.json',
            'provided-metadata-attachment.json', 'provided-metadata-validation.command.json'}
    if name.startswith("discovery/"):
        return name.endswith(("observed.json", "observed.bering-raw.json",
                              "observed.supplied-aliases.json", "observed.snapshot.json",
                              "observed.signal-quality.json",
                              "replay-command.json", "observations.json",
                              "accepted-request-sequence.jsonl", "accepted-stream-requests.jsonl",
                              "shared-observed-reference.json"))
    if name.startswith("procrustes/") and "/0/" in name:
        return name.endswith(("preflight.command.json", "report.json"))
    parts = name.split("/")
    if (len(parts) == 5 and parts[0] in ('ebpf', 'native', 'combined')
            and parts[1] in ('raw', 'network_scope')
            and parts[3:] == ['simulation', 'report.json']):
        return True
    return (len(parts) == 4 and parts[0] in ("ebpf", "native", "combined")
            and parts[1] in ("raw", "network_scope")
            and parts[-1] in ("binding.json", "forecast.json",
                              "analysis.json", "predicates.json", "faults.json",
                              "simulation.command.json", "model.json", "overlay.json",
                              "model.signal-quality.json", "provided-metadata-attachment.json",
                              "provided-metadata-validation.command.json", "observed-reference.json"))


def operation_metadata_facts(toolchain: Path, branch: Path, freeze: dict) -> dict:
    """Independently inspect the literal metadata-only derivation, without tools."""
    parts = branch.relative_to(toolchain).parts
    baseline = parts[0] == 'context-baseline'
    if baseline:
        if len(parts) != 4 or parts[2] != 'operations':
            raise ValueError('unexpected paired operation layout')
        source, variant = 'combined', parts[1]
    else:
        source, variant, _ = parts
    shared = toolchain / "discovery" / source / variant
    proof_path = branch / "provided-metadata-attachment.json"
    proof = read(proof_path)
    flags = {"origin": "provided_metadata_after_verified_semantic_view",
             "new_nodes_edges_or_endpoints": False,
             "graph_structure_and_observed_edge_fields_unchanged": True,
             "entity_ids_unchanged": True,
             "final_model_is_a_bering_emitted_snapshot": False,
             "source_signal_quality_unchanged": True,
             "same_information_all_sources_and_direct_baseline": True}
    if any(proof.get(key) != value for key, value in flags.items()):
        raise ValueError("operation metadata proof has a different derivation boundary")
    expected = {"observed_model": shared / "observed.json",
                "raw_bering_model": shared / "observed.bering-raw.json",
                "raw_bering_snapshot": shared / "observed.snapshot.json",
                "semantic_projection": shared / "observed.supplied-aliases.json",
                "provided_overlay": branch / "overlay.json",
                "simulator_model": branch / "model.json"}
    if baseline:
        union = toolchain/'context-baseline'/variant
        expected['observed_model'] = union/'union-model.json'
        expected['observation_derivation'] = union/'union-proof.json'
        if (proof.get('observed_graph_origin') != 'paired_context_edge_union'
                or proof.get('source_signal_quality_scope') != 'base entities and database aliases; added edge evidence is in the actual joint quality'):
            raise ValueError('paired metadata misstates its graph or quality origin')
        for key, path in (('model', expected['observed_model']), ('proof', expected['observation_derivation'])):
            claim = proof['observation_derivation'][key]
            if (toolchain_relative(claim['path']) != path.relative_to(toolchain).as_posix()
                    or claim['sha256'] != sha(path)):
                raise ValueError('paired metadata derivation locator or hash differs')
    if set(proof["files"]) != set(expected):
        raise ValueError("operation metadata proof has different source locators")
    for key, path in expected.items():
        claim = proof["files"][key]
        if (toolchain_relative(claim["path"]) != path.relative_to(toolchain).as_posix()
                or sha(path) != claim["sha256"]):
            raise ValueError("operation metadata source locator or hash differs")
    command_path = branch / "provided-metadata-validation.command.json"
    quality_path = branch / "model.signal-quality.json"
    source_quality = shared / "observed.signal-quality.json"
    paths = [*expected.values(), proof_path, command_path, quality_path, source_quality]
    for path in paths:
        name = "toolchain/" + path.relative_to(toolchain).as_posix()
        if freeze["sha256_by_path"].get(name) != sha(path):
            raise ValueError("operation metadata evidence is not frozen")
    if quality_path.read_bytes() != source_quality.read_bytes():
        raise ValueError("operation metadata changed the source signal quality")
    command = read(command_path)
    argv = command["argv"]
    if (command["returncode"] != 0 or len(argv) != 4
            or argv[:3] != ["bering", "validate", "--input"]
            or toolchain_relative(argv[3]) != expected["simulator_model"].relative_to(toolchain).as_posix()):
        raise ValueError("operation metadata lacks its successful exact Bering validation")
    original = read(expected["observed_model"])
    overlay = read(expected["provided_overlay"])
    if overlay != proof["supplied"] or set(overlay) - {"name", "services", "endpoints"}:
        raise ValueError("operation overlay differs or attempts a graph edit")
    derived = copy.deepcopy(original)
    for field, allowed in (("services", {"id", "replicas", "failure_eligible", "placements", "attributes"}),
                           ("endpoints", {"id", "predicate_ref", "semantics"})):
        by_id = {row["id"]: row for row in derived[field]}
        for supplied in overlay.get(field) or []:
            if set(supplied) - allowed or supplied["id"] not in by_id:
                raise ValueError("operation overlay requires an existing entity and supported fields")
            entity = by_id[supplied["id"]]
            if field == "services":
                if "replicas" in supplied:
                    entity["replicas"] = supplied["replicas"]
                for key in ("failure_eligible", "placements"):
                    if key in supplied:
                        entity.setdefault("metadata", {})[key] = copy.deepcopy(supplied[key])
                # Pinned Go keeps attributes in snapshot annotations, not model metadata.
            else:
                if "predicate_ref" in supplied:
                    entity["success_predicate_ref"] = supplied["predicate_ref"]
                semantics = supplied.get("semantics") or {}
                if set(semantics) - {"predicate_mode", "source"}:
                    raise ValueError("operation overlay adds unsupported endpoint semantics")
                if semantics:
                    entity.setdefault("metadata", {}).setdefault("semantics", {}).update(semantics)
    if derived != read(expected["simulator_model"]):
        raise ValueError("operation model is not the exact observed graph plus supplied metadata")
    return {"proof_sha256": sha(proof_path), "all_model_fields_exact": True,
            "source_signal_quality_bytes_unchanged": True,
            "final_model_is_a_bering_emitted_snapshot": False,
            "verified_frozen_paths": sorted({"toolchain/" + path.relative_to(toolchain).as_posix()
                                             for path in paths})}


def toolchain_relative(path: str) -> str:
    name = path.split("/toolchain/", 1)[1] if "/toolchain/" in path else path
    if not _safe(name):
        raise ValueError("unsafe saved toolchain reference")
    return name


def verified_reference(root: Path, claim: dict, freeze: dict | None) -> Path:
    name = toolchain_relative(claim["path"])
    path = root / name
    if (not path.is_file() or path.stat().st_size != claim["bytes"]
            or sha(path) != claim["sha256"]):
        raise ValueError("saved request metadata reference differs")
    if freeze is not None and freeze["sha256_by_path"].get("toolchain/" + name) != claim["sha256"]:
        raise ValueError("saved request metadata is not frozen")
    return path


def shared_observed_discovery_facts(root, toolchain, declaration, freeze, graphs, build):
    """Verify named logical coverage of a genuine identical-input origin; no replay."""
    paths = sorted(toolchain.glob('discovery/*/*/shared-observed-reference.json'))
    if not paths:
        return []
    if (declaration['head_sha'] not in IDENTICAL_INPUT_DISCOVERY_HEADS
            or (declaration['collector'], declaration['system'], declaration['mode'])
            != ('deepflow', 'otel_demo', 'absent') or freeze is None
            or (declaration['head_sha'] == UPLOAD_HOLD_PARENT_PROOF_HEAD and declaration.get('seed') not in (6,8))):
        raise ValueError('shared observed discovery is outside its named producer scope')
    worker_root = root/'infrastructure/remote-toolchain-v4/worker'
    output = read(worker_root/'output-manifest.json')
    worker_status = read(worker_root/'worker-status.json')
    claims = output['toolchain_files']
    frozen = freeze['sha256_by_path']
    physical = {(g['source'], g['variant']) for g in graphs}
    names = {'observed.json', 'observed.signal-quality.json', 'observed.snapshot.json',
             'observed.bering-raw.json', 'observed.bering-raw.signal-quality.json',
             'observed.supplied-aliases.json', 'observed-runtime/replay-command.json',
             'observed-runtime/serve.yaml', 'observed-runtime/accepted-request-sequence.jsonl'}
    core = names - {'observed.bering-raw.signal-quality.json', 'observed-runtime/serve.yaml'}
    binary = next(row for row in build['binaries'] if row['name']=='bering')
    def same(a, b):
        return json.dumps(a, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(
            b, sort_keys=True, separators=(',', ':'), allow_nan=False)
    def bound(claim, expected, require_body=True):
        if (toolchain_relative(claim['path']) != expected
                or frozen.get('toolchain/'+expected) != claim['sha256']
                or claims.get(expected) != {key: claim[key] for key in ('bytes','sha256')}):
            raise ValueError('shared discovery reference differs from frozen complete worker census')
        local = toolchain/expected
        if require_body or local.is_file():
            if local.is_symlink() or local.stat().st_size != claim['bytes'] or sha(local) != claim['sha256']:
                raise ValueError('shared discovery selected reference body changed')
        return local
    for name in ('forecasts.json','execution-summary.json'):
        body = toolchain/name
        bound({'path':name,'bytes':body.stat().st_size,'sha256':sha(body)}, name)
    forecasts = read(toolchain/'forecasts.json')
    execution = read(toolchain/'execution-summary.json')['branches']
    result = []
    for path in paths:
        parts = path.relative_to(toolchain).parts
        source, view = parts[1:3]
        if source!='combined' or view not in ('raw','network_scope') or ('ebpf',view) not in physical or (source,view) in physical:
            raise ValueError('shared discovery duplicates or lacks its genuine physical origin')
        relative = path.relative_to(toolchain).as_posix()
        claim = {'path':relative, 'bytes':path.stat().st_size, 'sha256':sha(path)}
        bound(claim, relative)
        value = read(path)
        origin = f'discovery/ebpf/{view}'
        if (value.get('schema_version') != 'identical-empty-native-observed-discovery-v1'
                or value.get('declared_source') != source or value.get('variant') != view
                or value.get('origin_source') != 'ebpf' or toolchain_relative(value['origin_folder']) != origin
                or value.get('additional_Bering_execution') is not False
                or value.get('actual_discovery_cost_counted_once') is not True
                or value.get('source_specific_operations_and_Sheaft_not_reused') is not True
                or value.get('original_request_and_value_semantic_validation_reused_under_byte_identity') is not True):
            raise ValueError('shared discovery overstates execution or semantic equivalence')
        if set(value['genuine_origin_files']) != names:
            raise ValueError('shared discovery origin file coverage differs')
        origin_graph = next(g for g in graphs if (g['source'],g['variant'])==('ebpf',view))
        if (origin_graph['observed_model_sha256'] != value['genuine_origin_files']['observed.json']['sha256']
                or origin_graph['snapshot_sha256'] != value['genuine_origin_files']['observed.snapshot.json']['sha256']):
            raise ValueError('shared discovery differs from the verified physical graph')
        for name, member in value['genuine_origin_files'].items():
            bound(member, origin+'/'+name, name in core)
        if any(n.startswith(f'discovery/combined/{view}/') and n!=relative for n in claims):
            raise ValueError('shared discovery contains a fabricated combined output')
        ebpf_path = bound(value['origin_input'], f'inputs/ebpf/{view}/observations.json')
        native_path = bound(value['empty_native_input'], f'inputs/native/{view}/observations.json')
        combined_path = bound(value['combined_input'], f'inputs/combined/{view}/observations.json')
        ebpf, native, combined = read(ebpf_path), read(native_path), read(combined_path)
        if (type(native.get('observations')) is not int or native['observations'] != 0
                or native.get('exports') or native.get('stream_exports') or native.get('ordered_request_group_manifests')
                or type(ebpf.get('observations')) is not int or ebpf['observations']<=0
                or ebpf.get('exports') or len(ebpf.get('stream_exports', []))!=1
                or type(combined.get('observations')) is not int or combined['observations']!=ebpf['observations']
                or combined.get('exports') or combined.get('stream_exports')):
            raise ValueError('shared discovery does not have exactly one nonempty input')
        groups = combined.get('ordered_request_group_manifests') or []
        if len(groups)!=2 or not same(groups, value['ordered_input_groups']):
            raise ValueError('shared discovery ordered group coverage differs')
        for group, expected in zip(groups, (value['origin_input'],value['empty_native_input']), strict=True):
            if not same(group, expected):
                raise ValueError('shared discovery group identity or order differs')
        stream = ebpf['stream_exports'][0]
        source_claims = [{key:p[key] for key in ('path','bytes','sha256')} for p in
                         [stream['request_index'], *stream['shards'], stream['runtime_identity_values']]]
        if not same(source_claims, value['whole_current_source_files_reverified']):
            raise ValueError('shared discovery source-byte receipt coverage differs')
        for member in source_claims:
            relative_input = toolchain_relative(member['path'])
            if not relative_input.startswith('inputs/'):
                raise ValueError('shared discovery current source bytes are outside frozen inputs')
            bound(member, relative_input, False)
        replay = read(toolchain/origin/'observed-runtime/replay-command.json')
        invocation = value['invocation']
        if (invocation['binary'] != binary['binary'] or invocation['binary_sha256'] != binary['binary_sha256']
                or replay['argv'][0] != invocation['binary']
                or any(not same(invocation[key],replay.get(key)) for key in
                       ('source_profile','source_domain','publication_mode','clock_admission_filter','go_runtime_environment'))
                or invocation['source_profile'] != {'source_id':'ebpf','input_type':'ebpf-otlp'}
                or invocation['source_domain'] != 'otel_demo-deployment' or invocation['publication_mode']!='on_shutdown'
                or invocation['clock_admission_filter'] is not False
                or invocation['alias_table_sha256'] != sha(root/'runtime-identity-v5/supplied-service-aliases-training.json')
                or invocation['alias_admission_sha256'] != sha(root/'runtime-identity-v5/supplied-service-alias-admission-training.json')):
            raise ValueError('shared discovery invocation differs from its actual pinned origin')
        start,end = value['started_ns'],value['ended_ns']
        if (type(start) is not int or type(end) is not int
                or not worker_status['started_ns'] <= replay['ended_ns'] <= start <= end <= worker_status['ended_ns']):
            raise ValueError('shared discovery validation was not completed inside the original worker')
        for operation in forecasts[source][view]:
            branch = toolchain/source/view/operation
            reference_path = branch/'observed-reference.json'
            proof = read(reference_path)
            bound({'path':reference_path.relative_to(toolchain).as_posix(), 'bytes':reference_path.stat().st_size,
                   'sha256':sha(reference_path)}, reference_path.relative_to(toolchain).as_posix())
            if ((branch/proof['folder']).resolve() != (toolchain/origin).resolve()
                    or proof['files'] != {n:value['genuine_origin_files'][n]['sha256'] for n in
                                         ('observed.json','observed.signal-quality.json','observed.snapshot.json')}):
                raise ValueError('combined operation does not reference the genuine shared graph')
            rows = [r for r in execution if (r['source'],r['variant'],r['operation'])==(source,view,operation)]
            if (len(rows)!=1 or rows[0].get('bering_executed') is not True
                    or rows[0].get('bering_discovery_shared_across_sources') is not True
                    or rows[0].get('bering_discovery_source')!='ebpf'
                    or toolchain_relative(rows[0]['bering_discovery_record'])!=origin+'/observed-runtime/replay-command.json'
                    or toolchain_relative(rows[0]['shared_discovery_reference'])!=relative):
                raise ValueError('combined execution summary misstates actual Bering execution')
        result.append({'source':source, 'variant':view, 'actual_origin_source':'ebpf',
                       'actual_origin_folder':origin, 'reference_sha256':sha(path),
                       'additional_Bering_execution':False, 'logical_nonempty_graph_coverage':True,
                       'selected_origin_bodies_rehashed':sorted(core),
                       'other_origin_and_wire_value_claims':'bound to full frozen worker census; unselected bodies not reread'})
    return result


def indexed_requests(root: Path, manifest: dict, freeze: dict | None):
    groups = manifest.get("ordered_request_group_manifests") or []
    if groups:
        loaded = [read(verified_reference(root, claim, freeze)) for claim in groups]
        if (any(group.get("ordered_request_group_manifests") for group in loaded)
                or sum(group["observations"] for group in loaded) != manifest["observations"]):
            raise ValueError("saved source-group boundaries differ")
    else:
        loaded = [manifest]
    for group in loaded:
        ordinary = [(row, "ordinary_export") for row in group.get("exports") or []]
        streams = group.get("stream_exports") or []

        def rows(descriptor):
            if descriptor.get("schema_version") != "deepflow-request-archive-v5":
                raise ValueError("unknown saved request index")
            path = verified_reference(root, descriptor["request_index"], freeze)
            count = observations = wire_bytes = 0
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    row = json.loads(line)
                    if (row.get("source") != descriptor.get("source")
                            or row.get("content_type") != "application/json"
                            or row.get("content_encoding") not in (None, "")):
                        raise ValueError("indexed request framing differs")
                    shard = row.get("shard")
                    shards = descriptor.get("shards") or []
                    if (type(shard) is not int or not 0 <= shard < len(shards)
                            or type(row.get("offset")) is not int or row["offset"] < 0
                            or type(row.get("length")) is not int or row["length"] <= 0
                            or row["offset"] + row["length"] > shards[shard]["bytes"]):
                        raise ValueError("indexed request slice escapes its saved shard")
                    shard_name = toolchain_relative(shards[shard]["path"])
                    if freeze is not None and freeze["sha256_by_path"].get(
                            "toolchain/" + shard_name) != shards[shard]["sha256"]:
                        raise ValueError("indexed request shard is not frozen")
                    count += 1; observations += row["observations"]; wire_bytes += row["length"]
                    yield row, "stream_archive_slice"
            if (count != descriptor.get("requests") or observations != descriptor.get("observations")
                    or wire_bytes != descriptor.get("wire_bytes")):
                raise ValueError("saved request index totals differ")

        ordered = (heapq.merge(iter(ordinary), *(rows(item) for item in streams),
                               key=lambda pair: pair[0].get("request_order", -1))
                   if streams else iter(ordinary))
        group_observations = 0
        for ordinal, (row, form) in enumerate(ordered, 1):
            if streams and row.get("request_order") != ordinal:
                raise ValueError("saved request order differs within a source group")
            if form == "ordinary_export" and freeze is not None:
                name = toolchain_relative(row["path"])
                if freeze["sha256_by_path"].get("toolchain/" + name) != row["sha256"]:
                    raise ValueError("ordinary request is not frozen")
            group_observations += row["observations"]
            yield row, form
        if group_observations != group.get("observations"):
            raise ValueError("saved source-group observation total differs")


def accepted_sequence_facts(root: Path, manifest: dict, replay: dict,
                            freeze: dict | None, *, joint_otlp=False) -> dict:
    sequence = replay.get("accepted_request_sequence")
    if not sequence or sequence.get("same_order_as_original_request_ordinals_and_source_groups") is not True:
        raise ValueError("saved ordered acceptance sequence is missing")
    path = verified_reference(root, sequence, freeze)
    ordinary, streamed = [], []
    with path.open(encoding="utf-8") as stream:
        accepted = (json.loads(line) for line in stream)
        for ordinal, (expected, actual) in enumerate(itertools.zip_longest(
                indexed_requests(root, manifest, freeze), accepted)):
            if expected is None or actual is None:
                raise ValueError("accepted request sequence length differs")
            row, form = expected
            endpoint = ("/sources/ebpf/v1/traces" if row["source"] == "ebpf" and not joint_otlp else "/v1/traces")
            if (actual.get("export_index") != ordinal or actual.get("http_status") != 200
                    or actual.get("content_sha256") != row["sha256"]
                    or actual.get("endpoint") != endpoint or actual.get("storage_form") != form
                    or (form == "stream_archive_slice" and actual.get("content_bytes") != row["length"])
                    or (joint_otlp and actual.get('original_source') != row['source'])):
                raise ValueError("accepted request sequence differs from saved source order")
            item = {key: value for key, value in actual.items() if key != "storage_form"}
            (ordinary if form == "ordinary_export" else streamed).append(item)
    if ordinary != (replay.get("accepted_ingest_requests") or []):
        raise ValueError("ordinary acceptance subset differs")
    if len(ordinary) + len(streamed) != sequence.get("requests"):
        raise ValueError("accepted sequence total differs")
    if streamed:
        proof = replay.get("accepted_stream_requests") or {}
        stream_path = verified_reference(root, proof, freeze)
        with stream_path.open(encoding="utf-8") as stream:
            if ([json.loads(line) for line in stream] != streamed
                    or proof.get("requests") != len(streamed)
                    or proof.get("same_http_body_order_as_request_index") is not True):
                raise ValueError("stream acceptance subset differs")
    elif replay.get("accepted_stream_requests"):
        raise ValueError("unexpected stream acceptance claim")
    return {"accepted_inputs": sequence["requests"], "ordinary_requests": len(ordinary),
            "streamed_requests": len(streamed), "sequence_sha256": sequence["sha256"],
            "unselected_wire_payloads_independently_rehashed": False}


def alias_only_model(raw: dict, aliases: dict) -> dict:
    projected = copy.deepcopy(raw)
    by_id = {}
    for service in projected.get('services') or []:
        old = service['id']
        service['id'] = aliases.get(old, old)
        if service.get('name') == old:
            service['name'] = service['id']
        if service['id'] in by_id and by_id[service['id']] != service:
            raise ValueError('saved alias collision has differing metadata')
        by_id[service['id']] = service
    projected['services'] = [by_id[key] for key in sorted(by_id)]
    for edge in projected.get('edges') or []:
        for key in ('from', 'to'):
            edge[key] = aliases.get(edge.get(key), edge.get(key))
    for endpoint in projected.get('endpoints') or []:
        endpoint['entry_service'] = aliases.get(endpoint.get('entry_service'), endpoint.get('entry_service'))
    return projected


def paired_simulation_facts(toolchain: Path, branch: Path, forecast: dict, freeze: dict) -> dict:
    command = read(branch/'simulation.command.json')
    argv = command.get('argv') or []
    relative = branch.relative_to(toolchain).as_posix()
    if (command.get('returncode') != 0 or forecast.get('simulator') != 'Sheaft'
            or len(argv) != 8 or argv[:3] != ['sheaft', 'run', '--model']
            or argv[4] != '--analysis' or argv[6] != '--out-dir'
            or [toolchain_relative(argv[index]) for index in (3, 5, 7)] !=
               [relative + '/' + name for name in ('model.json', 'analysis.json', 'simulation')]):
        raise ValueError('paired available forecast lacks its exact successful Sheaft command')
    analysis = read(branch/'analysis.json')
    files = ['simulation.command.json', 'model.json', 'analysis.json', 'simulation/report.json']
    for key, name in (('predicate_contract', 'predicates.json'), ('fault_contract', 'faults.json')):
        if key in analysis:
            if toolchain_relative(analysis[key]) != relative + '/' + name:
                raise ValueError('paired analysis references another operation contract')
            files.append(name)
    for name in files:
        path = branch/name
        if freeze['sha256_by_path'].get('toolchain/' + relative + '/' + name) != sha(path):
            raise ValueError('paired simulation input is not frozen')
    if (forecast.get('graph_sha256') != sha(branch/'model.json')
            or forecast.get('analysis_sha256') != sha(branch/'analysis.json')):
        raise ValueError('paired forecast model or analysis hash differs')
    report = read(branch/'simulation/report.json')
    if (report.get('input_artifact', {}).get('digest') != 'sha256:' + sha(branch/'model.json')
            or toolchain_relative(report.get('input_artifact', {}).get('path', '')) != relative + '/model.json'):
        raise ValueError('saved Sheaft report references another model')
    profiles = report.get('profiles') or {}
    if isinstance(profiles, list):
        profiles = {profile['name']: profile for profile in profiles}
    endpoints = [endpoint['id'] for endpoint in read(branch/'overlay.json')['endpoints']]
    if not endpoints or not forecast.get('by_state'):
        raise ValueError('saved available forecast lacks operation endpoints or state values')
    for state, value in forecast['by_state'].items():
        values = profiles.get('state-' + state, {}).get('simulation', {}).get('endpoint_availability', {})
        if any(values.get(endpoint) != value for endpoint in endpoints):
            raise ValueError('saved Sheaft report and frozen forecast state values differ')
    database_prediction = forecast.get('database_down_prediction')
    if database_prediction is not None:
        values = profiles.get('db-down', {}).get('simulation', {}).get('endpoint_availability', {})
        if any(values.get(endpoint) != database_prediction for endpoint in endpoints):
            raise ValueError('saved Sheaft report and frozen database prediction differ')
    facts = operation_metadata_facts(toolchain, branch, freeze)
    facts['saved_simulation_report'] = {
        'path': 'toolchain/' + relative + '/simulation/report.json',
        'sha256': sha(branch/'simulation/report.json'),
        'model_digest_and_all_operation_endpoint_state_values_match': True,
        'database_down_prediction_bound_if_present': database_prediction is not None}
    return facts


def saved_binding_summary(toolchain: Path, branch: Path, freeze: dict | None) -> dict:
    """Copy bounded saved fields, without witnesses, inference or new gates."""
    path = branch / 'binding.json'
    relative = 'toolchain/' + path.relative_to(toolchain).as_posix()
    result = {'path': relative, 'present': path.is_file()}
    if not path.is_file():
        return result
    digest = sha(path)
    frozen = ((freeze or {}).get('sha256_by_path') or {}).get(relative)
    result.update(sha256=digest, pre_target_freeze_sha256=frozen,
                  frozen_hash_matches=(digest == frozen) if frozen is not None else None)
    try:
        binding = read(path)
        result['fields_copied'] = {key: binding[key] for key in (
            'entry_service', 'available', 'unknown', 'primary_scope',
            'all_required_database_channels_observed', 'database_fault_prediction_available',
            'database_fault_unknown', 'assumed_satisfied_database_requirements',
            'database_fault_fixed_other_requirements') if key in binding}
        entry = binding.get('entry_identity_resolution')
        if entry is not None:
            result['entry_identity_resolution_copied'] = {
                key: entry[key] for key in (
                    'selection_rule', 'selected_observed_entry', 'all_supported_state_vectors_agree',
                    'known_database_predictions_agree', 'graph_modified',
                    'entry_failure_modeled', 'semantic_basis') if key in entry}
            result['entry_identity_resolution_copied']['candidates'] = [{
                'entry': candidate.get('entry'),
                'available': candidate.get('binding', {}).get('available'),
                'exact_state_vector': candidate.get('exact_state_vector'),
                'exact_database_down': candidate.get('exact_database_down'),
                'unknown': candidate.get('binding', {}).get('unknown'),
            } for candidate in entry.get('candidates', [])]
    except (ValueError, TypeError, AttributeError, OSError) as error:
        # A presentation failure is evidence, never a new scientific gate.
        result['projection_error_type'] = type(error).__name__
    return result


def context_baseline_facts(root: Path, toolchain: Path, freeze: dict,
                           original: dict, evaluation: dict | None) -> dict:
    """Inspect the fixed paired files; never replay, fit, or rescore outcomes."""
    baseline = toolchain/'context-baseline'
    frozen = freeze['sha256_by_path']

    def bound(path):
        name = ('toolchain/' + path.relative_to(toolchain).as_posix()
                if path.is_relative_to(toolchain) else path.relative_to(root).as_posix())
        if frozen.get(name) != sha(path):
            raise ValueError('paired evidence is not frozen: ' + name)
        return sha(path)

    def claim_at(claim, path):
        suffix = ('toolchain/' + path.relative_to(toolchain).as_posix()
                  if path.is_relative_to(toolchain) else path.relative_to(root).as_posix())
        saved_path = claim['path']
        if (not (saved_path == suffix or saved_path.endswith('/' + suffix))
                or claim['sha256'] != bound(path)):
            raise ValueError('paired evidence locator or hash differs: ' + suffix)

    predictions = read(baseline/'forecasts.json')
    manifest = read(baseline/'manifest.json')
    for path in (baseline/'forecasts.json', baseline/'manifest.json'):
        bound(path)
    if (manifest.get('policy_id') != 'observed_server_edge_union_v1'
            or manifest.get('same_policy_all_collectors_and_scenarios') is not True
            or manifest.get('requires_capture_freeze_before_targets') is not True
            or manifest.get('post_target_diagnostic_is_not_a_primary_forecast') is not True
            or set(predictions) != {'raw', 'network_scope'}
            or set(manifest['variants']) != set(predictions)):
        raise ValueError('paired policy or variant coverage differs')
    evaluation_list = (evaluation or {}).get('evaluations') or []
    rows = {(row['source'], row['variant'], row['operation']): row for row in evaluation_list}
    expected_keys = {('context-baseline', variant, op)
                     for variant, ops in predictions.items() for op in ops}
    if evaluation is not None and (len(rows) != len(evaluation_list) or
            {key for key in rows if key[0] == 'context-baseline'} != expected_keys):
        raise ValueError('paired evaluation coverage differs')
    facts = {}
    for variant, operations in predictions.items():
        out = baseline/variant
        shared = toolchain/'discovery/combined'/variant
        provenance_path = out/'provenance.json'
        bound(provenance_path)
        provenance = read(provenance_path)
        if provenance != manifest['variants'][variant] or set(operations) != set(original['combined'][variant]):
            raise ValueError('paired provenance or operation coverage differs')
        inputs = toolchain/'inputs/combined'/variant/'observations.json'
        claim_at(provenance['input_manifest'], inputs)
        claim_at(provenance['original_forecasts'], toolchain/'forecasts.json')
        counts = {source: read(toolchain/'inputs'/source/variant/'observations.json')['observations']
                  for source in ('ebpf', 'native')}
        for source in counts:
            bound(toolchain/'inputs'/source/variant/'observations.json')
        if counts != provenance['source_observations']:
            raise ValueError('paired source counts differ')
        status = provenance['status']
        reuse = status in ('reuse_single_source_equivalence', 'reuse_unchanged_union')
        if not all(counts.values()):
            if (status != 'reuse_single_source_equivalence'
                    or provenance.get('extra_bering_or_sheaft_executed') is not False
                    or (out/'joint').exists() or (out/'operations').exists()):
                raise ValueError('single-source equivalence claims extra execution')
            union_facts = None
        else:
            joint = out/'joint'
            union_path = out/'union-proof.json'
            bound(union_path)
            union = read(union_path)
            paths = {
                'base_model': shared/'observed.json', 'base_raw_model': shared/'observed.bering-raw.json',
                'base_snapshot': shared/'observed.snapshot.json', 'base_quality': shared/'observed.signal-quality.json',
                'base_alias_projection': shared/'observed.supplied-aliases.json',
                'joint_raw_model': joint/'observed.json', 'joint_snapshot': joint/'observed.snapshot.json',
                'joint_quality': joint/'observed.signal-quality.json', 'joint_model': joint/'canonical.json',
                'joint_canonical_quality': joint/'canonical.signal-quality.json',
                'joint_alias_projection': joint/'supplied-aliases.json',
                'joint_replay': joint/'observed-runtime/replay-command.json',
                'joint_config': joint/'observed-runtime/serve.yaml',
                'joint_accepted_sequence': joint/'observed-runtime/accepted-request-sequence.jsonl',
                'union_model': out/'union-model.json', 'input_manifest': inputs,
                'static_inputs': toolchain/'static-inputs.json',
                'alias_table': root/'runtime-identity-v5/supplied-service-aliases-training.json',
                'alias_admission': root/'runtime-identity-v5/supplied-service-alias-admission-training.json'}
            if (set(union['files']) != set(paths) or union['configured_tool_pins'] != {
                    'Procrustes': PINS['procrustes'], 'Bering': FRESH_BERING, 'Sheaft': PINS['sheaft']}):
                raise ValueError('paired union source list or product pins differ')
            for key, path in paths.items():
                claim_at(union['files'][key], path)
            for key, path in (('model', paths['union_model']), ('proof', union_path)):
                claim_at(provenance['union'][key], path)
            replay = read(paths['joint_replay'])
            config = yaml.safe_load(paths['joint_config'].read_text(encoding='utf-8'))
            argv = replay.get('argv') or []
            runtime, sink = config.get('runtime') or {}, config.get('sink') or {}
            if (len(argv) != 4 or PurePosixPath(argv[0]).name != 'bering'
                    or argv[1:3] != ['serve', '--config']
                    or toolchain_relative(argv[3]) != paths['joint_config'].relative_to(toolchain).as_posix()
                    or config.get('overlays') != []
                    or runtime.get('publication_mode') != 'on_shutdown'
                    or runtime.get('reconciliation') != {'enabled': False}
                    or runtime.get('max_in_memory_spans') != sum(counts.values()) + 1
                    or toolchain_relative(sink.get('latest_path', '')) != paths['joint_snapshot'].relative_to(toolchain).as_posix()
                    or toolchain_relative(sink.get('signal_quality_path', '')) != paths['joint_quality'].relative_to(toolchain).as_posix()):
                raise ValueError('paired Bering command does not use its exact saved batch configuration')
            ingest = replay.get('ingest') or {}
            if (replay.get('returncode') != 0 or replay.get('status') != 'complete'
                    or replay.get('request_routing') != 'ordinary_otlp_joint_view'
                    or replay.get('source_profile') != {'input_type': 'otlp', 'trace_context_domain': ''}
                    or replay.get('original_source_profile') != {'source_id': 'ebpf', 'input_type': 'ebpf-otlp'}
                    or replay.get('source_domain') != '' or replay.get('clock_admission_filter') is not False
                    or replay.get('original_export_roles_retained') is not True
                    or ingest.get('spans') != sum(counts.values())
                    or ingest.get('dropped_spans') != 0 or ingest.get('late_spans') != 0
                    or read(paths['joint_snapshot'])['model'] != read(paths['joint_raw_model'])):
                raise ValueError('paired actual Bering view differs')
            sequence = accepted_sequence_facts(toolchain, read(inputs), replay, freeze, joint_otlp=True)
            base_replay = read(shared/'observed-runtime/replay-command.json')
            base_sequence = verified_reference(toolchain, base_replay['accepted_request_sequence'], freeze)
            with base_sequence.open(encoding='utf-8') as left, paths['joint_accepted_sequence'].open(encoding='utf-8') as right:
                for base_row, joint_row in itertools.zip_longest(left, right):
                    if base_row is None or joint_row is None:
                        raise ValueError('paired request count differs from original combined')
                    a, b = json.loads(base_row), json.loads(joint_row)
                    if any(a.get(key) != b.get(key) for key in
                           ('export_index', 'content_sha256', 'content_bytes', 'storage_form')):
                        raise ValueError('paired request bytes or order differ')
            alias = read(paths['joint_alias_projection'])
            admitted = read(paths['alias_admission']).get('aliases') or {}
            if (alias.get('table_sha256') != sha(paths['alias_table'])
                    or alias.get('raw_model_sha256') != sha(paths['joint_raw_model'])
                    or alias.get('raw_quality_sha256') != sha(paths['joint_quality'])
                    or any(admitted.get(key) != value for key, value in (alias.get('effective_aliases') or {}).items())
                    or alias.get('graph_edges_injected') or alias.get('physical_identity_inferred')
                    or alias.get('roles_or_endpoints_created')
                    or alias_only_model(read(paths['joint_raw_model']), alias.get('effective_aliases') or {}) != read(paths['joint_model'])):
                raise ValueError('paired joint projection exceeds the supplied alias boundary')
            base = read(paths['base_model'])
            expected = copy.deepcopy(base)
            services = {row['id'] for row in base['services']}
            edges = {row['id']: row for row in base['edges']}
            added, conflicts, skipped = [], [], []
            for edge in read(paths['joint_model'])['edges']:
                if edge['id'] in edges:
                    if any(edges[edge['id']].get(key) != edge.get(key) for key in ('from', 'to', 'kind', 'blocking', 'identity')):
                        conflicts.append(edge['id'])
                elif (edge.get('identity') or {}).get('span_kind') != 'server':
                    skipped.append({'id': edge['id'], 'reason': 'not_an_actual_server_child_edge'})
                elif edge['from'] not in services or edge['to'] not in services:
                    skipped.append({'id': edge['id'], 'reason': 'endpoint_service_not_in_original_view'})
                else:
                    expected['edges'].append(copy.deepcopy(edge))
                    added.append(edge['id'])
            if (expected != read(paths['union_model']) or added != union['added_edge_ids']
                    or conflicts != union['semantic_identity_conflicts'] or skipped != union['skipped_joint_edges']
                    or union['joint_alias_metadata_collisions'] != alias['metadata_collisions']
                    or union.get('union_is_a_bering_emitted_snapshot') is not False
                    or union.get('contract_inferred_edges') is not False
                    or union.get('physical_identity_inferred') is not False):
                raise ValueError('paired graph is not the exact base plus eligible actual SERVER edges')
            expected_status = ('unknown_view_alignment' if conflicts or alias['metadata_collisions'] else
                               'forecast_from_observed_context_union' if added else 'reuse_unchanged_union')
            if status != expected_status or provenance.get('extra_bering_executed') is not True:
                raise ValueError('paired provenance status differs from actual views')
            if status != 'forecast_from_observed_context_union' and (
                    provenance.get('extra_sheaft_executed') is not False or (out/'operations').exists()):
                raise ValueError('paired reused or conflicting view claims extra simulation')
            union_facts = {'added_edge_ids': added, 'semantic_identity_conflicts': conflicts,
                           'joint_alias_metadata_collisions': alias['metadata_collisions'],
                           'exact_base_and_all_added_fields': True, 'accepted_sequence': sequence}
        if reuse and operations != original['combined'][variant]:
            raise ValueError('paired reused forecast differs, including unknown rows')
        branches = []
        for operation, forecast in operations.items():
            row = rows.get(('context-baseline', variant, operation))
            if evaluation is not None:
                primary = rows[('combined', variant, operation)]
                if (any(row.get('forecast_interval' if key == 'interval' else key) != forecast.get(key)
                        for key in ('available', 'reason', 'prediction', 'interval'))
                        or any(row.get(key) != primary.get(key) for key in (
                            'actual_counts', 'actual_target_success_counts', 'observed_empirical_bounds',
                            'nominal_wilson_envelope', 'latency'))
                        or row.get('unknown_obligations') != forecast.get('unknown')
                        or any(row.get(key) != forecast.get(key) for key in (
                            'database_unknown_reason', 'database_fault_unknown', 'assumed_satisfied_database_requirements'))
                        or {state: {key: value for key, value in saved.items() if key not in ('prediction', 'error')}
                            for state, saved in row.get('by_state', {}).items()} !=
                           {state: {key: value for key, value in saved.items() if key not in ('prediction', 'error')}
                            for state, saved in primary.get('by_state', {}).items()}):
                    raise ValueError('paired evaluation differs from frozen forecasts or shared external outcomes')
            if status == 'unknown_view_alignment' and (forecast.get('available') is not False
                    or forecast.get('prediction') is not None
                    or forecast.get('reason') != 'context_view_identity_or_alias_conflict'):
                raise ValueError('paired conflict was not retained as unknown')
            metadata = None
            if forecast.get('available') and not reuse:
                branch = out/'operations'/operation
                metadata = paired_simulation_facts(toolchain, branch, forecast, freeze)
            binding_branch = toolchain/'combined'/variant/operation if reuse else out/'operations'/operation
            branches.append({'operation': operation, 'available_copied': forecast.get('available'),
                             'reason_copied': forecast.get('reason'), 'provided_metadata_attachment': metadata,
                             'binding_summary': saved_binding_summary(toolchain, binding_branch, freeze)})
        facts[variant] = {'status': status, 'union': union_facts, 'branches': branches}
    return {'policy_id': manifest['policy_id'], 'variants': facts,
            'external_outcomes_recomputed': False, 'original_forecasts_overwritten': False}


def deepflow_control_facts(root: Path, control: dict, node: str, claim: dict) -> dict:
    from ebpf_discovery.deepflow_codec_v5 import _parse

    name = claim["raw_file"].split("/observations/", 1)[1]
    if not _safe(name) or not name.startswith(f"deepflow-raw/node-{node}/"):
        raise ValueError("DeepFlow control locator has a different node")
    path = root / "observations" / name
    offset, length = claim["raw_offset"], claim["raw_length"]
    if (claim.get("proven") is not True or type(offset) is not int or offset < 0
            or type(length) is not int or length <= 0 or offset + length > path.stat().st_size):
        raise ValueError("DeepFlow control locator is incomplete")
    with path.open("rb") as stream:
        stream.seek(offset)
        body = stream.read(length)
    if hashlib.sha256(body).hexdigest() != claim["raw_sha256"]:
        raise ValueError("DeepFlow control record hash differs")
    record, conflicts, error = _parse(body)
    if (error or conflicts or record.get("signal_source") != "EBPF"
            or record.get("l7_protocol") not in ("Http1", "Http2")
            or record.get("l7_protocol") != claim.get("protocol")
            or not control.get("marker") or control["marker"] not in str(record.get("request_resource", ""))
            or record.get("tap_side") not in ("ClientProcess", "ServerProcess")
            or record.get("tap_side") != claim.get("tap_side")):
        raise ValueError("DeepFlow control lacks raw eBPF HTTP origin and marker")
    snapshot = read(path.parent / "snapshot.json")
    rows = [row for row in snapshot["files"] if row["snapshot_name"] == path.name]
    if (snapshot.get("node") != node or len(rows) != 1
            or rows[0]["copied_bytes"] != path.stat().st_size
            or rows[0]["copied_sha256"] != sha(path)):
        raise ValueError("DeepFlow control file differs from retained snapshot")
    return {"node": node, "raw_sha256": claim["raw_sha256"], "raw_member": name,
            "raw_offset": offset, "raw_length": length,
            "matches": [{key: record.get(key) for key in (
                "signal_source", "l7_protocol", "tap_side", "request_resource")}]}


def deepflow_closure_facts(root: Path, collector: dict, drain: dict) -> dict:
    observations = root / "observations"
    retention = read(observations / "deepflow-retention-manifest.json")
    retention_claim = (collector.get("retained_file_hashes") or {}).get("deepflow-retention-manifest.json")
    if (not retention_claim or retention_claim["sha256"] != sha(observations / "deepflow-retention-manifest.json")
            or retention_claim["bytes"] != (observations / "deepflow-retention-manifest.json").stat().st_size):
        raise ValueError("DeepFlow retention manifest is not bound to closed collector")
    claims = retention.get("files") or []
    by_name = {row["path"]: row for row in claims}
    if (len(by_name) != len(claims) or retention.get("file_count") != len(claims)
            or retention.get("raw_bytes") != sum(row["bytes"] for row in claims)
            or retention.get("zero_internal_loss_proven") is not False
            or any(retention.get("known_write_failures", {}).get(node, {}).get(key)
                   for node in ("a", "b") for key in ("container_log", "retained_standalone_logs"))):
        raise ValueError("DeepFlow retention manifest has conflicting claims")
    for path in observations.rglob("*"):
        if not path.is_file():
            continue
        name = path.relative_to(observations).as_posix()
        claim = (collector.get("retained_file_hashes") or {}).get(name) or by_name.get(name)
        if claim is not None and (path.stat().st_size != claim["bytes"] or sha(path) != claim["sha256"]):
            raise ValueError("DeepFlow selected metadata differs from closure hash chain")
    capture = drain.get("final_raw_capture") or {}
    if (capture.get("final") is not True or capture.get("technical_valid") is not True
            or set(capture.get("nodes") or {}) != {"a", "b"}
            or set(drain.get("termination") or {}) != {"a", "b"}):
        raise ValueError("DeepFlow final standalone capture is incomplete")
    snapshots = []
    for path in sorted((observations / "deepflow-raw").glob("node-*/*/snapshot.json")):
        relative = path.relative_to(observations).as_posix()
        if relative not in by_name:
            raise ValueError("DeepFlow snapshot is missing from retention manifest")
        snapshot = read(path)
        for row in snapshot.get("files") or []:
            if not _safe(row["snapshot_name"]) or "/" in row["snapshot_name"]:
                raise ValueError("unsafe DeepFlow saved snapshot member")
            member = (path.parent / row["snapshot_name"]).relative_to(observations).as_posix()
            claim = by_name.get(member) or {}
            if claim.get("bytes") != row["copied_bytes"] or claim.get("sha256") != row["copied_sha256"]:
                raise ValueError("DeepFlow snapshot/retention file claims differ")
        snapshots.append(snapshot)
    prefixes = drain.get("training_prefix_unchanged_in_final") or {}
    if not prefixes or {key.split("/", 1)[0] for key in prefixes} != {"a", "b"}:
        raise ValueError("DeepFlow lacks both saved training prefixes")
    for key, prefix in prefixes.items():
        node, name = key.split("/", 1)
        if (prefix.get("unchanged") is not True
                or prefix.get("training_sha256") != prefix.get("final_prefix_sha256")
                or not any(snapshot.get("node") == node and not snapshot.get("producer_closed")
                           and any(row.get("source_name") == name
                                   and row.get("copied_bytes") == prefix.get("bytes")
                                   and row.get("copied_sha256") == prefix.get("training_sha256")
                                   for row in snapshot.get("files") or []) for snapshot in snapshots)):
            raise ValueError("DeepFlow saved training/final prefix claims differ")
    for node, final in capture["nodes"].items():
        path = observations / "deepflow-raw" / f"node-{node}" / final["stage"] / "snapshot.json"
        if (read(path) != final or final.get("technical_valid") is not True
                or final.get("producer_closed") is not True or final.get("closed_checkpoint") is not True
                or final.get("rotation_observed") or final.get("standalone_file_log_write_failures")
                or final.get("codec_technical_failure_records") != 0
                or any(row.get("source_changed_during_snapshot")
                       or (row["source_name"].startswith("l7_flow_log") and row.get("pending_tail_bytes_at_read"))
                       for row in final.get("files") or [])):
            raise ValueError("DeepFlow final snapshot is not closed and stable")
        for key, prefix in prefixes.items():
            if key.startswith(node + "/") and not any(
                    row["source_name"] == key.split("/", 1)[1] and row["copied_bytes"] >= prefix["bytes"]
                    for row in final["files"]):
                raise ValueError("DeepFlow final file is shorter than its saved prefix")
        termination = drain["termination"][node]
        if (termination.get("technical_valid") is not True or termination.get("running") is not False
                or termination.get("exit_code") != 0 or termination.get("oom_killed") is not False
                or termination.get("sigkill_events") != 0 or termination.get("technical_invalid_reasons")):
            raise ValueError("DeepFlow producer termination is incomplete")
        for label in ("stop", "inspect", "events"):
            claim = termination["raw_evidence"][label]
            if not _safe(claim["path"]) or sha(observations / claim["path"]) != claim["sha256"]:
                raise ValueError("DeepFlow saved termination source differs")
    return {"nodes": ["a", "b"], "snapshot_hash_chains_verified": len(snapshots),
            "training_prefix_claims_verified": len(prefixes),
            "all_raw_payload_bytes_independently_rehashed": False,
            "zero_kernel_producer_or_flush_loss_proven": False}


def verify_package(package: Path, selected: Path, *, kind: str,
                   freeze: dict | None = None) -> dict:
    transport = read(package / "transport.json")
    if transport.get("kind") != kind:
        raise ValueError("typed package kind differs from declared role")
    manifest_path = package / "payload.manifest.jsonl"
    archive = package / "payload.tar.gz"
    if (archive.stat().st_size != transport["archive_bytes"]
            or sha(archive) != transport["archive_sha256"]
            or sha(manifest_path) != transport["manifest_sha256"]):
        raise ValueError("typed package transport differs from its manifest")
    rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines()]
    expected = {row["path"]: row for row in rows if row["type"] == "file"}
    seen: set[str] = set()
    copied = []
    frozen = []
    nonfrozen = []
    total = 0
    selected.mkdir(parents=True, exist_ok=True)
    with gzip.open(archive, "rb") as raw:
        with tarfile.open(fileobj=raw, mode="r|") as bundle:
            for member in bundle:
                name = member.name
                if not _safe(name):
                    raise ValueError("unsafe typed package member")
                if member.isdir():
                    continue
                if not member.isfile() or name not in expected or name in seen:
                    raise ValueError(f"unexpected typed package member: {name}")
                claim = expected[name]
                digest = hashlib.sha256()
                size = 0
                target = selected / PurePosixPath(name)
                output = None
                if _package_selected(name, kind):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    output = target.open("wb")
                try:
                    source = bundle.extractfile(member)
                    if source is None:
                        raise ValueError("typed package file has no body")
                    with source:
                        while chunk := source.read(1024 * 1024):
                            digest.update(chunk)
                            size += len(chunk)
                            if output:
                                output.write(chunk)
                finally:
                    if output:
                        output.close()
                if size != member.size or size != claim["bytes"] or digest.hexdigest() != claim["sha256"]:
                    raise ValueError(f"typed package member differs: {name}")
                seen.add(name)
                total += size
                freeze_key = "toolchain/" + name
                if freeze is not None and freeze_key in freeze:
                    if digest.hexdigest() != freeze[freeze_key]:
                        raise ValueError(f"typed package differs from pre-target freeze: {name}")
                    frozen.append(freeze_key)
                else:
                    nonfrozen.append(freeze_key)
                if output:
                    copied.append({"path": name, "bytes": size, "sha256": digest.hexdigest()})
        while raw.read(1024 * 1024):
            pass
    if seen != set(expected):
        raise ValueError("typed package did not contain every declared file")
    return {
        "archive_bytes": archive.stat().st_size, "archive_sha256": sha(archive),
        "manifest_sha256": sha(manifest_path), "all_files_verified": len(seen),
        "uncompressed_file_bytes_verified": total, "selected_files": copied,
        "frozen_file_hashes_matched": len(frozen),
        "not_in_pre_target_freeze": nonfrozen,
        "scientific_processing_performed": False,
        "_file_claims": {name: {"bytes": row["bytes"], "sha256": row["sha256"]}
                         for name, row in expected.items()},
    }


def upload_hold_parent_proof_facts(root, remote_root, declaration, index, provenance, parent_import, saved):
    """Bind the one named schedule to actual full proofs and same-parent clocks."""
    if declaration['head_sha'] != UPLOAD_HOLD_PARENT_PROOF_HEAD:
        return None
    if ((declaration['collector'], declaration['system'], declaration['mode'])
            != ('deepflow', 'otel_demo', 'absent') or declaration['seed'] not in (6,8)):
        raise ValueError('upload-hold proof is outside its named absent6/8 source')
    preflight_path = remote_root/'upload-hold-preflight.json'
    preflight = read(preflight_path)
    schedule = read(remote_root/'parent-proof-schedule.json')
    dispatch = read(remote_root/'dispatch.json')
    cost = read(remote_root/'cost.json')
    hold = read(root/'training-checkpoint-cost.json')
    ready = read(root/'infrastructure/training-checkpoint/ready.json')
    release = read(root/'infrastructure/training-checkpoint/release.json')
    inputs = dispatch.get('inputs') or {}
    proof = dispatch.get('checkpoint_proof') or {}
    logical = index.get('checkpoint')
    identity = parent_import.get('identity') or {}
    canonical_sha = lambda value: hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    if (set(identity) != {'run_id','commit','system','mode','seed','manifest_sha256'}
            or identity.get('commit') != declaration['head_sha']
            or str(identity.get('run_id')) != str(declaration['run_id'])
            or (identity.get('system'),identity.get('mode'),identity.get('seed'))
                != (declaration['system'],declaration['mode'],declaration['seed'])
            or preflight.get('schema_version') != 'upload-hold-parent-preflight-v1'
            or preflight.get('status') != 'complete'
            or preflight.get('complete_original_checkpoint_proof_executed') is not True
            or preflight.get('identity') != identity or schedule.get('identity') != identity
            or any(str(ready.get(k)) != str(v) or str(inputs.get(k)) != str(v)
                   or str(release.get(k)) != str(v) for k,v in identity.items())
            or release.get('upload_success') is not True
            or proof.get('manifest_sha256') != identity['manifest_sha256']
            or not isinstance(proof.get('files'), dict) or not proof['files']
            or preflight.get('checkpoint_proof_sha256') != canonical_sha(proof)
            or provenance.get('checkpoint_input') != proof
            or type(preflight.get('verified_files')) is not int
            or preflight['verified_files'] != len(proof['files'])
            or preflight.get('plans_sha256') != inputs.get('plans_sha256')
            or preflight.get('plans_sha256') != parent_import.get('plans_sha256')
            or preflight.get('plans_sha256') != provenance.get('plans_sha256')
            or not isinstance(preflight.get('plans_sha256'), str)
            or len(preflight['plans_sha256']) != 64
            or any(c not in '0123456789abcdef' for c in preflight['plans_sha256'])
            or not logical or provenance.get('training_index_proof') != logical
            or preflight.get('training_index_proof_sha256') != canonical_sha(logical)
            or inputs.get('training_index_proof_sha256') != canonical_sha(logical)
            or schedule.get('training_index_proof_sha256') != canonical_sha(logical)
            or index.get('parent_after_dispatch_before_import') != logical
            or index.get('parent_after_worker') != logical or 'parent_before_dispatch' in index):
        raise ValueError('upload-hold preflight lacks its exact full checkpoint/worker/SQL proof')
    if (schedule.get('schema_version') != 'upload-hold-parent-proof-schedule-v1'
            or schedule.get('status') != 'complete'
            or schedule.get('phase') != 'parent_after_dispatch_before_import'
            or schedule.get('all_checks_before_import_or_target') is not True
            or schedule.get('upload_hold_preflight_sha256') != sha(preflight_path)
            or cost.get('upload_hold_preflight_sha256') != sha(preflight_path)
            or dispatch.get('status') != 'dispatched'
            or not str(parent_import.get('worker_run_id')).isdigit()
            or int(parent_import['worker_run_id']) <= 0
            or any(str(item.get('worker_run_id')) != str(parent_import.get('worker_run_id'))
                   for item in (dispatch, schedule, cost, provenance))
            or hold.get('ready') is not True or hold.get('upload_success') is not True
            or cost.get('checkpoint_validation_includes_checkpoint_copy_release') is not False):
        raise ValueError('upload-hold schedule lacks completed source-bound worker/phase/cost evidence')
    times = [ready.get('created_ns'), hold.get('ready_callback_started_ns'),
             preflight.get('started_ns'), preflight.get('ended_ns'),
             hold.get('ready_callback_ended_ns'), hold.get('ended_ns'),
             dispatch.get('post_started_ns'), dispatch.get('dispatched_ns'),
             schedule.get('parent_proof_started_ns'), schedule.get('parent_proof_ended_ns'),
             parent_import.get('imported_ns'), saved.get('saved_ns')]
    if (any(type(v) is not int or v <= 0 for v in times) or times != sorted(times)
            or schedule.get('confirmed_dispatch_ns') != dispatch.get('dispatched_ns')
            or type(release.get('released_ns')) is not int
            or not ready['created_ns'] <= release['released_ns'] <= dispatch['post_started_ns']):
        raise ValueError('upload-hold schedule violates same-parent callback/POST/proof/import/freeze order')
    phase_seconds = (schedule['parent_proof_ended_ns']-schedule['parent_proof_started_ns'])/1e9
    callback_seconds = (hold['ready_callback_ended_ns']-hold['ready_callback_started_ns'])/1e9
    if (cost.get('parent_after_dispatch_proof_seconds') != phase_seconds
            or hold.get('ready_callback_seconds') != callback_seconds
            or type(hold.get('upload_hold_wall_seconds')) not in (int,float)
            or not math.isfinite(hold['upload_hold_wall_seconds'])
            or hold['upload_hold_wall_seconds'] < callback_seconds):
        raise ValueError('upload-hold schedule cost clocks disagree')
    return {'source': declaration['head_sha'], 'phase': schedule['phase'],
            'worker_run_id': parent_import['worker_run_id'],
            'full_checkpoint_proof_sha256': canonical_sha(proof),
            'verified_files': len(proof['files']), 'training_index_proof_sha256': canonical_sha(logical),
            'upload_hold_preflight_sha256': sha(preflight_path),
            'same_parent_clock_order_ns': times, 'callback_seconds': callback_seconds,
            'upload_hold_wall_seconds': hold['upload_hold_wall_seconds'],
            'parent_after_dispatch_proof_seconds': phase_seconds,
            'whole_case_speedup_or_six_hour_guarantee_claimed': False}


def verify_worker_output_claims(manifest_claims: dict, provenance_claims: dict,
                                package_claims: dict, toolchain: Path,
                                freeze: dict | None) -> dict:
    if manifest_claims != provenance_claims:
        raise ValueError("worker output manifest and provenance toolchain claims differ")
    if package_claims:
        for name, claim in manifest_claims.items():
            if package_claims.get(name) != {
                    "bytes": claim["bytes"], "sha256": claim["sha256"]}:
                raise ValueError(f"worker output claim differs from typed package: {name}")
        return {"scope": "complete_typed_toolchain_package",
                "verified_claims": len(manifest_claims), "unselected_claims": []}
    verified = []
    unselected = []
    frozen = (freeze or {}).get("sha256_by_path") or {}
    for name, claim in manifest_claims.items():
        path = toolchain / name
        if not path.is_file():
            unselected.append(name)
            continue
        if (path.stat().st_size != claim["bytes"] or sha(path) != claim["sha256"]
                or frozen.get("toolchain/" + name) != claim["sha256"]):
            raise ValueError(f"selected untyped worker output differs: {name}")
        verified.append(name)
    if not verified:
        raise ValueError("untyped worker evidence has no selected frozen output claims")
    return {"scope": "selected_untyped_outputs_only",
            "verified_claims": len(verified),
            "verified_selected_paths": sorted(verified),
            "unselected_claims": sorted(unselected),
            "whole_worker_tree_verified": False}


def compact_facts(root: Path, declaration: dict, *, smoke_qualification=False) -> tuple[dict, dict, dict]:
    manifest = read(root / "evaluation-manifest.json")
    status = read(root / "status.json")
    evaluation = read(root / "evaluation-v5.json")
    scientific = _capture_declaration(declaration)
    if declaration['head_sha'] == CLOSED_CAPTURE_RECOVERY_HEAD:
        _saved_capture_identity(manifest, declaration['run_id'],
            tuple(declaration[k] for k in ('collector', 'system', 'mode', 'seed')))
    identity = (status.get("collector"), status.get("system"), status.get("mode"),
                status.get("seed"), int(status.get("run_id")))
    expected = (declaration["collector"], declaration["system"], declaration["mode"],
                declaration["seed"], scientific["run_id"])
    if smoke_qualification and (
            declaration['head_sha'] not in CONTEXT_BASELINE_HEADS
            or declaration.get('stage') != 'smoke' or declaration.get('runner') != 'study'
            or declaration.get('seed') != 6 or status.get('smoke') is not True):
        raise ValueError('qualification reader requires the fixed final-source smoke identity')
    if identity != expected or status.get("commit") != scientific["head_sha"]:
        raise ValueError(f"saved compact identity differs: {identity!r}")
    if declaration["head_sha"] in FRESH_HEADS and (
            status.get("controller") != "clean-study" or status.get("smoke") is not smoke_qualification):
        raise ValueError("fresh saved status does not identify the clean main controller")
    if (manifest.get("commit") != declaration["head_sha"]
            or manifest.get("run_id") != str(declaration["run_id"])):
        raise ValueError("evaluation manifest source differs from declaration")
    missing = []
    verified = []
    for name, digest in (manifest.get("files_sha256") or {}).items():
        path = root / name
        if not path.is_file():
            if name == "attempt-journal.jsonl":
                missing.append(name)
                continue
            raise ValueError(f"manifest-declared selected compact member missing: {name}")
        if digest is not None and sha(path) != digest:
            raise ValueError(f"compact member hash differs: {name}")
        verified.append(name)
    counts = evaluation.get("counts") or {}
    expected_blocks = 19 if declaration["system"] == "otel_demo" else 16
    expected_primary, expected_target = 34800, 9600
    if smoke_qualification:
        from ebpf_discovery.evaluate_v5 import expected_counts
        _, workload, phases, _ = expected_counts(declaration['system'], True)
        expected_primary, expected_target = sum(phases.values()), phases['target']
        if (status.get('workload_counts') != workload or evaluation.get('primary_series_result') is not False
                or evaluation.get('smoke_technical_pass') is not True):
            raise ValueError('qualification workload or non-main result boundary differs')
    if (counts.get("primary") != expected_primary or counts.get("target") != expected_target
            or counts.get("blocks") != expected_blocks):
        raise ValueError("fixed workload count identity differs")
    if not (evaluation.get("integrity", {}).get("valid")
            and evaluation.get("completeness", {}).get("valid")
            and evaluation.get("complete_for_evaluation")):
        raise ValueError("saved evaluation integrity/completeness is not valid")
    acquisition = evaluation.get("acquisition") or {}
    if not acquisition.get("valid") or acquisition.get("problems"):
        raise ValueError("saved acquisition is not technically valid")
    blocks = json.loads((root / "blocks.json").read_text(encoding="utf-8"))
    targets = [row["started_ns"] for row in blocks if row.get("phase") == "target"]
    if not targets:
        raise ValueError("saved blocks contain no target phase")
    facts = {
        "identity": dict(zip(("collector", "system", "mode", "seed", "run_id"), identity)),
        "manifest_members_verified": sorted(verified),
        "nonmaterialized_members": missing,
        "counts": counts, "acquisition": acquisition,
        "first_target_started_ns": min(targets),
        "evaluations_copied_not_recomputed": evaluation.get("evaluations"),
        "manual_baselines_copied_not_recomputed": evaluation.get("manual_baselines"),
        "cost_copied_not_recomputed": evaluation.get("cost"),
    }
    if "scientific_summaries" in evaluation:
        facts["scientific_summaries_copied_not_recomputed"] = evaluation["scientific_summaries"]
    return facts, evaluation, read(root / "freeze-integrity.json")


def _selected_proof(root: Path, declaration: dict) -> dict:
    proof = read(root / "selected-transport-proof.json")
    artifact = proof.get("artifact") or {}
    workflow = artifact.get("workflow_run") or {}
    expected_name = declaration["compact_artifact_name"].replace("v5-summary-", "campaign-v5-", 1)
    union = _closed_union_profile(declaration)
    origin_run, origin_head = declaration["run_id"], declaration["head_sha"]
    if union:
        origin_run, origin_head = _closed_union_artifact_origin(union, 'capture')
        expected_name = union['artifacts']['capture']['name']
        if (proof.get('scope') != 'closed-capture' or
                {k:artifact.get(k) for k in union['artifacts']['capture']} != union['artifacts']['capture']):
            raise ValueError('closed union selected input is not its actual original capsule')
    if (proof.get("complete") is not True or proof.get("scientific_processing_performed") is not False
            or artifact.get("name") != expected_name or artifact.get("expired") is not False
            or workflow.get("id") != origin_run
            or workflow.get("head_sha") != origin_head):
        raise ValueError("selected evidence transport identity/integrity differs")
    if "full_artifact_id" in declaration and {
            "id": artifact.get("id"), "name": artifact.get("name"),
            "size_in_bytes": artifact.get("size_in_bytes"),
            "digest": artifact.get("digest")} != {
                "id": declaration["full_artifact_id"],
                "name": declaration["full_artifact_name"],
                "size_in_bytes": declaration["full_artifact_bytes"],
                "digest": declaration["full_artifact_digest"]}:
        raise ValueError("selected full artifact differs from fixed qualification declaration")
    for name, claim in (proof.get("files") or {}).items():
        path = root / name
        if (not path.is_file() or path.stat().st_size != claim["bytes"]
                or sha(path) != claim["sha256"]):
            raise ValueError(f"selected evidence file differs: {name}")
    return proof


def native_mode_facts(root: Path, declaration: dict,
                      evaluation: dict | None = None) -> dict:
    facts = {}
    for stage in ("training", "final"):
        if declaration["system"] == "deathstarbench":
            manifest_path = root / f"native/{stage}/manifest.json"
            manifest = read(manifest_path)
            provenance = manifest.get("audit_self_trace_provenance") or {}
            if (manifest.get("mode") != declaration["mode"] or manifest.get("errors")
                    or provenance.get("excluded_service_exact_match") != "jaeger-all-in-one"
                    or provenance.get("raw_responses_retained") is not True
                    or not isinstance(manifest.get("application_trace_count"), int)
                    or not isinstance(manifest.get("audit_self_trace_count"), int)
                    or (declaration["mode"] == "absent"
                        and (manifest.get("absence_verified") is not True
                             or manifest.get("application_trace_count") != 0))):
                raise ValueError(f"DSB native {stage} manifest contradicts trace audit policy")
            facts[stage] = {
                "manifest_sha256": sha(manifest_path),
                "application_trace_count": manifest["application_trace_count"],
                "audit_self_trace_count": manifest["audit_self_trace_count"],
                "absence_verified": manifest.get("absence_verified"),
                "audit_self_trace_provenance": provenance}
        else:
            metadata_path = root / f"native/{stage}/native-metadata.json"
            if metadata_path.is_file():
                metadata = read(metadata_path)
                census = metadata.get("actual_census") or {}
                compliance = metadata.get("mode_compliance") or {}
                if (metadata.get("mode") != declaration["mode"]
                        or census.get("malformed_records") != 0
                        or compliance.get("compliant") is False
                        or (declaration["mode"] == "absent" and census.get("spans") != 0)):
                    raise ValueError(f"native {stage} census contradicts rendered tracing mode")
                facts[stage] = {
                    "schema": "native-metadata", "metadata_sha256": sha(metadata_path),
                    "actual_census": census, "mode_compliance": compliance}
                continue
            suppression_path = root / f"native/{stage}/native-suppression-verification.json"
            suppression = read(suppression_path)
            absent_nonzero = declaration["mode"] == "absent" and any(
                suppression.get(key) != 0 for key in (
                    "exporter_records", "span_markers", "trace_file_bytes"))
            if (suppression.get("mode") != declaration["mode"]
                    or suppression.get("malformed_records") != 0
                    or suppression.get("mode_compliant") is False
                    or absent_nonzero):
                raise ValueError(
                    f"native {stage} suppression audit contradicts rendered tracing mode")
            facts[stage] = {
                "schema": "native-suppression-verification",
                "suppression_sha256": sha(suppression_path),
                "saved_audit": suppression}
    if (declaration["system"] != "deathstarbench"
            and declaration["mode"] == "absent" and evaluation is not None
            and (evaluation.get("acquisition") or {}).get("native_observations_by_service")):
        raise ValueError("absent mode compact records native observations")
    return facts


def validate_otel_demo_sdk_settings(settings: dict[str, str | None], mode: str) -> list[str]:
    invalid = {service: value for service, value in settings.items()
               if value not in (None, "true", "false")}
    if invalid:
        raise ValueError("rendered OTel SDK configuration has invalid disable values")
    controlled_replicas = {"product-catalog-a", "product-catalog-b"}
    if not controlled_replicas <= settings.keys():
        raise ValueError("rendered OTel deployment lacks a controlled product-catalog replica")
    disabled_services = {service for service, value in settings.items() if value == "true"}
    if mode == "absent":
        expected = set(settings) - {"otel-collector", "product-catalog"}
    elif mode == "partial":
        expected = controlled_replicas
    elif mode == "full":
        expected = set()
    else:
        raise ValueError("unknown rendered OTel tracing mode")
    if disabled_services != expected:
        raise ValueError("rendered SDK configuration differs from declared mode")
    return sorted(value for value in settings.values() if value is not None)


def guest_platform_facts(root: Path) -> dict:
    """Read the existing boot proof; two kernels share the same runner host."""
    infrastructure = read(root / "infrastructure/infrastructure.json")
    image = read(root / "infrastructure/image-provenance.json")
    kernels, boots = {}, {}
    for node in ("a", "b"):
        original = (root / "infrastructure" / node / "check.txt").read_bytes().decode("utf-8")
        lines = original.splitlines()
        if infrastructure.get("nodes", {}).get(node) != original or len(lines) < 2 or not lines[0]:
            raise ValueError("guest kernel check differs from retained infrastructure proof")
        kernels[node], boots[node] = lines[0], str(uuid.UUID(lines[1]))
    if (infrastructure.get("status") != "ready" or boots["a"] == boots["b"]
            or image.get("sha256") != FRESH_GUEST_IMAGE_SHA256
            or infrastructure.get("shared_physical_host") is not True):
        raise ValueError("guest boot/image premise differs from the fixed two-guest setup")
    return {"kernel_releases": kernels, "boot_ids": boots, "independent_guest_boots": True,
            "shared_runner_host": True, "separate_physical_hosts_claimed": False,
            "guest_memory_mib": infrastructure.get("guest_memory_mib"),
            "recorded_image_provenance": image,
            "guest_image_bytes_independently_rehashed_by_this_review": False}


def postcapture_guest_facts(root: Path, declaration: dict) -> dict | None:
    declaration = _capture_declaration(declaration)
    if declaration['head_sha'] not in ({POSTCAPTURE_GUEST_RELEASE_HEAD, CLOSED_POSTCAPTURE_HEAD, CLOSED_CAPTURE_RECOVERY_HEAD} | IDENTICAL_INPUT_DISCOVERY_HEADS):
        return None
    if declaration['head_sha'] == CLOSED_POSTCAPTURE_HEAD and (declaration['mode'], declaration['seed']) not in CLOSED_POSTCAPTURE_CELLS:
        raise ValueError('closed postcapture source is restricted to the seven technical replacements')
    if (declaration['collector'], declaration['system']) != ('deepflow', 'otel_demo') or (
            declaration['mode'], declaration['seed']) == ('full', 7):
        raise ValueError('postcapture source is restricted to the eight technical OTel replacements')
    release_path = root / 'infrastructure/postcapture-guest-release.json'
    capture_path = root / 'infrastructure/guest-evidence-capture.json'
    release, capture = read(release_path), read(capture_path)
    if (release.get('status') != 'complete' or capture.get('status') != 'complete'
            or capture.get('schema') != 'owned-guest-diagnostics-v5'
            or str(capture.get('run_id')) != str(declaration['run_id'])
            or capture.get('source') != declaration['head_sha']
            or release.get('guest_evidence_capture_SHA256') != sha(capture_path)):
        raise ValueError('postcapture source lacks its actual bound release/capture proofs')
    started, exited, ended = (release.get(name) for name in
        ('started_ns', 'owned_guests_confirmed_exited_ns', 'ended_ns'))
    if not all(type(value) is int for value in (started, exited, ended)) or not started < exited <= ended:
        raise ValueError('owned guest exit was not confirmed before completion')
    owned = release.get('owned_processes') or []
    signals = release.get('verified_pidfd_signal_result') or []
    removed = release.get('removed_ephemeral_overlays') or []
    cleanup = release.get('pidfile_cleanup') or []
    if (len(owned) != 2 or {row.get('node') for row in owned} != {'a', 'b'}
            or len({row.get('pid') for row in owned}) != 2
            or len(signals) != 2 or {row.get('node') for row in signals} != {'a', 'b'}
            or len(removed) != 2 or len(cleanup) != 2
            or {row.get('node') for row in cleanup} != {'a', 'b'}):
        raise ValueError('postcapture ownership proof does not cover exactly two guests')
    vm_root = PurePosixPath(str(capture.get('vm_root', '')))
    if not vm_root.is_absolute() or not PurePosixPath(str(capture.get('campaign_root', ''))).is_absolute():
        raise ValueError('postcapture proof lacks the original guest/campaign roots')
    for row in owned:
        if (type(row.get('pid')) is not int or row['pid'] <= 1
                or not isinstance(row.get('start_ticks'), str)
                or not row['start_ticks'].isdecimal()):
            raise ValueError('postcapture proof lacks an actual PID/start-time identity')
        node = row['node']
        expected_pidfile, expected_overlay = str(vm_root/(node+'.pid')), str(vm_root/node/'root.qcow2')
        args = row.get('args') or []
        if (row.get('pidfile') != expected_pidfile or row.get('overlay') != expected_overlay
                or not args or PurePosixPath(args[0]).name != 'qemu-system-x86_64'
                or not any(args[i] == '-pidfile' and args[i+1] == expected_pidfile for i in range(len(args)-1))
                or not any(args[i] == '-drive' and args[i+1] == 'file='+expected_overlay+',format=qcow2,if=virtio'
                           for i in range(len(args)-1))):
            raise ValueError('postcapture proof differs from the owned guest paths')
        signal = next(item for item in signals if item['node'] == node)
        if signal.get('pid') != row['pid'] or signal.get('status') not in (
                'TERM_sent_through_verified_pidfd', 'already_exited_without_signal', 'exited_before_signal'):
            raise ValueError('owned guest signal/exit proof differs')
        if signal['status'] == 'TERM_sent_through_verified_pidfd' and (
                signal.get('start_ticks') != row.get('start_ticks') or signal.get('args') != args):
            raise ValueError('signal was not bound to the original guest identity')
        disposition = next(item for item in cleanup if item['node'] == node)
        if disposition.get('path') != expected_pidfile or disposition.get('disposition') not in (
                'already_removed_after_confirmed_exit', 'removed_after_confirmed_exit'):
            raise ValueError('owned PID file cleanup differs')
        prefix = 'infrastructure/'+node+'/'
        files = capture.get('files') or {}
        required = {prefix+name for name in ('check-copy.err', 'serial-test.err',
            'guest-kernel-final.txt', 'guest-kernel-final.err', 'guest-kernel-final.returncode')}
        if not required <= files.keys():
            raise ValueError('postcapture diagnostic proof lacks a guest command')
        serial_required = ({prefix+name for name in ('serial-stat.txt', 'serial-stat.err',
                            'serial-copy.err', 'serial.log')} if prefix+'serial-copy.returncode' in files else
                           {prefix+'serial-test.returncode', prefix+'serial-copy.status'})
        if not serial_required <= files.keys():
            raise ValueError('postcapture serial disposition is missing')
    if {row.get('path') for row in removed} != {row['overlay'] for row in owned}:
        raise ValueError('postcapture removal includes an unowned overlay')
    for name, claim in capture['files'].items():
        path = (root/name).resolve()
        if (not _safe(name) or not path.is_relative_to(root.resolve()) or not path.is_file()
                or path.stat().st_size != claim.get('bytes') or sha(path) != claim.get('sha256')):
            raise ValueError('postcapture diagnostic file changed: '+name)
    return {'release': release, 'capture': capture,
            'release_sha256': sha(release_path), 'capture_sha256': sha(capture_path),
            'diagnostic_returncodes_preserved_not_forced_success': True,
            'whole_case_memory_disk_headroom_or_six_hour_cure_proven': False}


def closed_postcapture_facts(root: Path, declaration: dict, frozen: dict,
                            worker: dict | None, selected: dict, *, compact=None, restore_root=None, actual_processing=None) -> dict | None:
    """Bind the exact new source's sealed inputs to its actual offline output."""
    recovered = declaration['head_sha'] == CLOSED_CAPTURE_RECOVERY_HEAD
    staged_delivery = recovered or declaration['head_sha'] in IDENTICAL_INPUT_DISCOVERY_HEADS
    if declaration['head_sha'] not in ({CLOSED_POSTCAPTURE_HEAD, CLOSED_CAPTURE_RECOVERY_HEAD} | IDENTICAL_INPUT_DISCOVERY_HEADS):
        return None
    scientific = _capture_declaration(declaration)
    if ((declaration['collector'], declaration['system']) != ('deepflow', 'otel_demo')
            or (declaration['mode'], declaration['seed']) not in CLOSED_POSTCAPTURE_CELLS):
        raise ValueError('closed postcapture case is outside the seven technical replacements')
    if declaration['head_sha'] in IDENTICAL_INPUT_DISCOVERY_HEADS and (declaration['mode']!='absent' or declaration['seed'] not in (6,7,8)):
        raise ValueError('identical-input completion source is outside its three original cells')
    union = _closed_union_profile(declaration)
    folder = root/'infrastructure/postcapture'
    processing_evidence = None
    if union:
        if compact is None or restore_root is None or actual_processing is None:
            raise ValueError('closed union lacks its actual compact/restore/source API chain')
        processing_evidence = _closed_union_api_facts(read(actual_processing), expected_profile=union)
        diagnostic = read(restore_root/'selected-transport-proof.json')
        meta = diagnostic.get('artifact') or {}; wanted = union['artifacts']['restore']
        if (diagnostic.get('complete') is not True or diagnostic.get('scope') != 'restore-diagnostics'
                or diagnostic.get('scientific_processing_performed') is not False
                or {k:meta.get(k) for k in wanted} != wanted
                or (meta.get('workflow_run') or {}).get('id') != union['run_id']
                or (meta.get('workflow_run') or {}).get('head_sha') != union['head_sha']):
            raise ValueError('closed union actual restore metadata transport differs')
        for name,claim in diagnostic.get('files',{}).items():
            if (not _safe(name) or not (restore_root/name).is_file()
                    or (restore_root/name).stat().st_size != claim.get('bytes')
                    or sha(restore_root/name) != claim.get('sha256')):
                raise ValueError('closed union actual restore metadata changed')
        marker, captured = (read(folder/name) for name in ('closed.json','capture-status.json'))
        processing, artifact = None, read(restore_root/'artifact-api.json')
        final, summary = read(compact/'status.json'), read(compact/'evaluation-manifest.json')
    else:
        marker, captured, processing, artifact = (read(folder/name) for name in
            ('closed.json', 'capture-status.json', 'processing.json', 'artifact-api.json'))
        final, summary = read(root/'status.json'), read(root/'evaluation-manifest.json')
    expected = {'run_id': str(scientific['run_id']), 'commit': scientific['head_sha'],
        'system': 'otel_demo', 'collector': 'deepflow', 'controller': 'clean-study',
        'mode': declaration['mode'], 'seed': declaration['seed'], 'smoke': False}
    for identity in (marker.get('identity') or {}, captured, final,
                     *(() if union else (processing.get('identity') or {},))):
        actual = {key: str(identity.get(key)) if key == 'run_id' else identity.get(key) for key in expected}
        if actual != expected:
            raise ValueError('closed capture or processing identity differs from the main case')
    publication = {'run_id': str(declaration['run_id']), 'commit': declaration['head_sha']}
    workflow = artifact.get('workflow_run') or {}
    expected_name = f"postcapture-v5-deepflow-main-otel_demo-{declaration['mode']}-{declaration['seed']}-{scientific['run_id']}"
    if (marker.get('schema') != 'closed-otel-postcapture-v5'
            or marker.get('sealing_run_id') != expected['run_id']
            or marker.get('sealing_source') != expected['commit']
            or artifact.get('name') != expected_name or artifact.get('expired') is not False
            or type(artifact.get('id')) is not int or artifact['id'] <= 0
            or type(artifact.get('size_in_bytes')) is not int or artifact['size_in_bytes'] <= 0
            or workflow.get('id') != scientific['run_id'] or workflow.get('head_sha') != expected['commit']
            or not isinstance(artifact.get('digest'), str) or not artifact['digest'].startswith('sha256:')
            or len(artifact['digest']) != 71 or set(artifact['digest'][7:]) - set('0123456789abcdef')):
        raise ValueError('closed artifact lacks its exact main-run source binding')
    if (captured.get('status') != 'postcapture_complete' or final.get('status') != 'acquisition_complete'
            or (not union and (processing.get('status') != 'complete' or processing.get('offline_only') is not True
                or processing.get('traffic_replay_or_model_refit') is not False
                or processing.get('processing_run_id') != publication['run_id']
                or processing.get('processing_source') != publication['commit']
                or processing.get('closed_manifest_sha256') != sha(folder/'closed.json')
                or processing.get('input_file_inventory_sha256') != marker.get('file_inventory_sha256')))
            or marker.get('capture_status_sha256') != sha(folder/'capture-status.json')
            or marker.get('file_inventory_sha256') != sha(folder/'files.jsonl')):
        raise ValueError('closed input inventory and actual processing chain differ')
    if recovered:
        _saved_capture_identity(summary, declaration['run_id'],
            tuple(declaration[k] for k in ('collector', 'system', 'mode', 'seed')))
        if {k: artifact.get(k) for k in ('id', 'name', 'size_in_bytes', 'digest')} != CLOSED_CAPTURE_RECOVERY_SOURCE['capture_artifact']:
            raise ValueError('recovered case uses a different original closed artifact')
    expected_publication_name = (declaration['compact_artifact_name'].replace('v5-summary-', 'campaign-v5-', 1)
                                 if union else selected['artifact']['name'])
    if (summary.get('qualification_only') is True or (not recovered and summary.get('scientific_capture_identity') is not None)
            or str(summary.get('run_id')) != publication['run_id'] or summary.get('commit') != publication['commit']
            or summary.get('full_artifact_name') != expected_publication_name
            or summary.get('files_sha256', {}).get('status.json') != sha((compact if union else root)/'status.json')):
        raise ValueError('qualification or unrelated publication cannot stand in for a new main case')
    host = restore_root if union else root/'infrastructure/postcapture-host'
    restore, guard = read(host/'restore.json'), read(host/'disk-before-download.json')
    original_required = sum(guard.get(k, -1) for k in
        ('archive_bytes', 'scientific_file_bytes', 'proof_bytes', 'SQL_WAL_growth_reserve_bytes'))+1024**3
    if staged_delivery:
        fixed = guard.get('scientific_file_bytes', -1) + guard.get('proof_bytes', -1)
        original_required = max(guard.get('archive_bytes', -1)+fixed,
                                fixed+guard.get('SQL_WAL_growth_reserve_bytes', -1))+1024**3
    if (restore.get('status') != 'complete' or restore.get('artifact_id') != artifact['id']
            or restore.get('artifact_digest') != artifact['digest']
            or restore.get('archive_bytes') != artifact['size_in_bytes']
            or 'sha256:'+str(restore.get('archive_sha256')) != artifact['digest']
            or restore.get('all_original_members_read_to_EOF_and_CRC_checked') is not True
            or restore.get('closed_manifest_sha256') != sha(folder/'closed.json')
            or guard.get('archive_bytes') != artifact['size_in_bytes']
            or guard.get('scientific_file_bytes') != marker.get('file_bytes')
            or guard.get('proof_bytes') != sum((folder/name).stat().st_size for name in
                ('closed.json', 'capture-status.json', 'files.jsonl'))
            or guard.get('SQL_WAL_growth_reserve_bytes') != 4*marker.get('index_bytes', 0)
            or guard.get('scientific_limit_or_filter') is not False
            or guard.get('required_bytes') != original_required
            or guard.get('available_bytes', -1) < guard.get('required_bytes', 0)):
        raise ValueError('actual closed restore, archive integrity or pre-download capacity proof differs')
    if staged_delivery:
        phase = read(host/'disk-before-processing.json')
        delivery = restore.get('delivery_working_copy') or {}
        owned = restore.get('verified_delivery_identity') or {}
        reserve = 4*marker['index_bytes']
        expected_delivery = str(PurePosixPath(marker['scientific_root']).parent/'closed-postcapture.zip')
        if (guard.get('budget') != CLOSED_CAPTURE_RECOVERY_SOURCE['delivery_budget']
                or guard.get('download_restore_required_bytes') != artifact['size_in_bytes']+fixed+1024**3
                or guard.get('restored_processing_peak_bytes') != fixed+reserve+1024**3
                or restore.get('capture_run_id') != expected['run_id']
                or restore.get('capture_source') != expected['commit']
                or restore.get('processing_run_id') != publication['run_id']
                or restore.get('processing_source') != publication['commit']
                or set(owned) != {'device', 'inode', 'type', 'bytes'}
                or any(type(owned.get(k)) is not int for k in owned)
                or owned.get('device', 0) <= 0 or owned.get('inode', 0) <= 0
                or owned.get('type') != 0o100000 or owned.get('bytes') != artifact['size_in_bytes']
                or delivery.get('verified_file_identity') != owned
                or delivery.get('path') != expected_delivery
                or delivery.get('bytes') != artifact['size_in_bytes']
                or delivery.get('sha256') != restore.get('archive_sha256')
                or delivery.get('disposition') != 'verified_then_removed_owned_delivery'
                or delivery.get('removed_after_all_restore_checks') is not True
                or type(delivery.get('recorded_ns')) is not int
                or phase.get('scientific_tree_already_restored') is not True
                or phase.get('verified_delivery_removed') is not True
                or phase.get('scientific_limit_or_filter') is not False
                or phase.get('SQL_WAL_growth_reserve_bytes') != reserve
                or phase.get('required_bytes') != reserve+1024**3
                or phase.get('available_bytes') != delivery.get('free_after')
                or phase.get('available_bytes', -1) < phase.get('required_bytes', 0)):
            raise ValueError('saved recovery lacks its exact owned delivery lifetime or actual SQL/WAL guard')
    if union:
        namespace = selected.get('closed_capture_namespace') or {}
        if (namespace.get('scientific_file_bytes') != marker['file_bytes']
                or namespace.get('scientific_files') != marker['files']
                or namespace.get('proof_bytes') != guard['proof_bytes']
                or namespace.get('processed_full_snapshot') is not False):
            raise ValueError('closed union complete original capsule population differs')
    closure = marker.get('acquisition_closure') or {}
    if (closure.get('unresolved_transports') != 0
            or (closure.get('completeness') or {}).get('valid') is not True
            or (closure.get('acquisition') or {}).get('valid') is not True
            or any(key.endswith('_close_error') for key in captured)
            or not worker or marker.get('training_SQL') != worker['training_index_proof']['parent_after_worker']):
        raise ValueError('closed acquisition or pre-mutation worker SQL proof differs')
    guest_capture = read(root/'infrastructure/guest-evidence-capture.json')
    if (not PurePosixPath(str(marker.get('scientific_root', ''))).is_absolute()
            or marker['scientific_root'] != guest_capture.get('campaign_root')):
        raise ValueError('closed processing root differs from the captured scientific root')
    for name, mode in (marker.get('directories') or {}).items():
        if not _safe(name) or type(mode) is not int or not 0 <= mode <= 0o7777:
            raise ValueError('closed directory permission claim is invalid')
    mutable = {'status.json', 'observation-index.sqlite', 'attempt-journal.sqlite', 'attempt-journal.jsonl'}
    names, frozen_names, logical_bytes, selected_count = set(), set(), 0, 0
    hashes = frozen['sha256_by_path']
    with (folder/'files.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            name = row['path']
            if (not _safe(name) or name in names or type(row['bytes']) is not int or row['bytes'] < 0
                    or type(row['mode']) is not int or not 0 <= row['mode'] <= 0o7777
                    or not isinstance(row['sha256'], str) or len(row['sha256']) != 64
                    or set(row['sha256']) - set('0123456789abcdef')):
                raise ValueError('closed file inventory entry is invalid')
            if name == 'observation-index.sqlite' and row['bytes'] != marker.get('index_bytes'):
                raise ValueError('closed SQL byte size differs from its sealed inventory')
            if name == 'status.json' and (row['sha256'] != marker['capture_status_sha256']
                    or row['bytes'] != (folder/'capture-status.json').stat().st_size):
                raise ValueError('closed capture status differs from its sealed inventory')
            if name == 'attempt-journal.sqlite' and row['sha256'] != marker.get('journal_sha256'):
                raise ValueError('closed journal differs from its sealed inventory')
            names.add(name)
            logical_bytes += row['bytes']
            if name in hashes:
                if hashes[name] != row['sha256']:
                    raise ValueError('pre-mutation frozen model/input claim changed')
                frozen_names.add(name)
            claim = selected.get('files', {}).get(name)
            if claim is not None and name not in mutable:
                if claim['bytes'] != row['bytes'] or claim['sha256'] != row['sha256']:
                    raise ValueError('selected immutable payload differs from its sealed input')
                selected_count += 1
    if (len(names) != marker.get('files') or logical_bytes != marker.get('file_bytes')
            or frozen_names != set(hashes) or len(frozen_names) != marker.get('frozen_file_count')
            or type(marker.get('journal_events')) is not int or marker['journal_events'] < 0
            or type(marker.get('journal_max_seq')) is not int or marker['journal_max_seq'] < 0
            or not {'status.json', 'observation-index.sqlite', 'attempt-journal.sqlite'} <= names):
        raise ValueError('closed input population, SQL or frozen file claims are incomplete')
    linked = read(root/'infrastructure/remote-toolchain-v4/closed-discovery-import-hardlinks.json')
    parent = worker['parent_import']
    for key in ('run_id', 'commit', 'system', 'mode', 'seed', 'manifest_sha256'):
        if (linked.get('identity') or {}).get(key) != parent['identity'].get(key):
            raise ValueError('closed discovery-copy import identity differs')
    if (linked.get('schema_version') != 'closed-discovery-import-hardlinks-v1'
            or linked.get('immutable_subtree') != 'toolchain/discovery/'
            or linked.get('all_original_members_read_to_EOF') is not True
            or linked.get('output_manifest_sha256') != sha(root/'infrastructure/remote-toolchain-v4/worker/output-manifest.json')
            or linked.get('worker_run_id') != parent.get('worker_run_id')
            or linked.get('worker_artifact_id') != parent.get('worker_artifact_id')
            or linked.get('worker_artifact_digest') != parent.get('worker_artifact_digest')
            or linked.get('archive_sha256') != parent.get('downloaded_archive_sha256')):
        raise ValueError('closed discovery-copy import lacks complete worker/archive verification')
    return {'closed_manifest': marker, 'capture_status': captured, 'processing': processing,
        **({'processing_completion_evidence': processing_evidence,
            'scientific_packet_layout': union['layout'],
            'unavailable_processed_full_components': list(union['unavailable'])}
           if union else {}),
        'closed_artifact': artifact, 'actual_restore': restore, 'pre_download_capacity': guard,
        'closed_discovery_import': linked,
        'inventory_rows': len(names), 'inventory_logical_bytes': logical_bytes,
        'selected_immutable_payloads_bound_to_inventory': selected_count,
        'all_frozen_claims_bound_to_pre_mutation_inventory': True,
        'mutable_SQL_status_journal_not_compared_to_pre_mutation_file_bytes': True,
        'producer_full_input_hash_and_mode_verification': 'Exact qualified source verifies all before mutation',
        'reader_body_rehash_scope': 'Selected payload bodies; complete input inventory claims streamed, not every unselected payload re-read',
        'whole_case_memory_disk_headroom_or_six_hour_cure_proven': False}


def full_facts(root: Path, declaration: dict, freeze: dict | None,
               evaluation: dict | None, package_out: Path, *, compact=None, restore_root=None, actual_processing=None) -> dict:
    proof = _selected_proof(root, declaration)
    scientific = _capture_declaration(declaration)
    postcapture = postcapture_guest_facts(root, declaration)
    toolchain = root / "toolchain"
    packages = {}
    typed = root / "toolchain-package"
    if typed.is_dir() and (typed / "payload.tar.gz").is_file():
        toolchain = package_out / "toolchain"
        packages["toolchain"] = verify_package(
            typed, toolchain, kind="toolchain",
            freeze=(freeze or {}).get("sha256_by_path"))
    handoff = root / "infrastructure/handoff-package"
    handoff_selected = package_out / "handoff"
    if handoff.is_dir() and (handoff / "payload.tar.gz").is_file():
        packages["handoff"] = verify_package(
            handoff, handoff_selected, kind="handoff")

    saved = read(root / "forecast-saved.json")
    if freeze is not None:
        if not freeze.get("all_unchanged") or saved.get("sha256_by_path") != freeze.get("sha256_by_path"):
            raise ValueError("saved forecast and freeze maps differ")
        for name, claim in (proof.get("files") or {}).items():
            if name in freeze["sha256_by_path"] and claim["sha256"] != freeze["sha256_by_path"][name]:
                raise ValueError(f"selected full evidence differs from pre-target freeze: {name}")
    build = read(root / "toolchain-build/toolchain-build.json")
    pins = {row["name"]: row["commit"] for row in build.get("binaries") or []}
    fresh = declaration["head_sha"] in FRESH_HEADS
    guest_facts = guest_platform_facts(root) if declaration["head_sha"] in GUEST_PROOF_HEADS else None
    expected_pins = {**PINS, "bering": FRESH_BERING} if fresh else PINS
    if pins != expected_pins:
        raise ValueError("saved toolchain source pins differ")
    graphs = []
    for replay_path in sorted(toolchain.glob("discovery/*/*/observed-runtime/replay-command.json")):
        replay = read(replay_path)
        if replay.get("returncode") != 0 or replay.get("status") != "complete":
            raise ValueError("saved Bering replay did not complete")
        relative = replay_path.relative_to(toolchain)
        source, variant = relative.parts[1], relative.parts[2]
        observations = read(toolchain / "inputs" / source / variant / "observations.json")
        accepted = replay.get("accepted_ingest_requests") or []
        exports = observations.get("exports") or []
        ingest = replay.get("ingest") or {}
        observed_path = replay_path.parent.parent / "observed.json"
        snapshot_path = replay_path.parent.parent / "observed.snapshot.json"
        raw_model_path = replay_path.parent.parent / "observed.bering-raw.json"
        snapshot = read(snapshot_path)
        observed = read(observed_path)
        source_model = read(raw_model_path) if raw_model_path.is_file() else observed
        if (replay.get("source_profile") != {
                "source_id": "ebpf", "input_type": "ebpf-otlp"}
                or not replay.get("source_domain")
                or replay.get("clock_admission_filter") is not False
                or ingest.get("spans") != observations.get("observations")
                or ingest.get("dropped_spans") != 0 or ingest.get("late_spans") != 0
                or (not fresh and len(accepted) != len(exports))
                or snapshot.get("model") != source_model):
            raise ValueError("Bering source/input/ingest/model binding differs")
        sequence_facts = (accepted_sequence_facts(toolchain, observations, replay, freeze)
                          if fresh else {})
        for export, request in ([] if fresh else zip(exports, accepted, strict=True)):
            if export.get("sha256") != request.get("content_sha256") or request.get("http_status") != 200:
                raise ValueError("Bering accepted request differs from saved input")
            relative_export = "toolchain/" + export["path"].split("/toolchain/", 1)[1]
            if freeze is not None and freeze["sha256_by_path"].get(relative_export) != export["sha256"]:
                raise ValueError("Bering accepted export is not the frozen source input")
        graphs.append({"source": source, "variant": variant,
                       "source_domain": replay.get("source_domain"),
                       "source_profile": replay.get("source_profile"),
                       "ingest": ingest, "accepted_inputs": len(accepted), **sequence_facts,
                       "observed_model_sha256": sha(observed_path),
                       "snapshot_sha256": sha(snapshot_path)})
    if not graphs:
        raise ValueError("selected evidence contains no actual Bering execution")
    shared_graphs = shared_observed_discovery_facts(root, toolchain, declaration,
        freeze or {'sha256_by_path':saved['sha256_by_path']}, graphs, build)
    shared_origins = {(r['source'],r['variant']):r['actual_origin_folder'] for r in shared_graphs}
    if fresh:
        expected_graphs = set()
        for source in ("ebpf", "native", "combined"):
            for variant in ("raw", "network_scope"):
                path = toolchain / "inputs" / source / variant / "observations.json"
                if (freeze is not None and freeze["sha256_by_path"].get(
                        "toolchain/" + path.relative_to(toolchain).as_posix()) != sha(path)):
                    raise ValueError("source/variant input manifest is not frozen")
                if read(path).get("observations", 0) > 0:
                    expected_graphs.add((source, variant))
        if ({(row["source"], row["variant"]) for row in graphs} | set(shared_origins)) != expected_graphs:
            raise ValueError("fresh evidence lacks a nonempty source/variant Bering execution")

    preflights = []
    for command_path in sorted(toolchain.glob("procrustes/*/*/0/preflight.command.json")):
        command = read(command_path)
        source = command_path.relative_to(toolchain).parts[1]
        argv = command.get("argv") or []
        has_neutral_source = any(
            argv[index:index + 2] == ["--collection-source", "ebpf-otlp"]
            for index in range(max(0, len(argv) - 1)))
        if (command.get("returncode") != 0
                or (source == "native" and has_neutral_source)
                or (source != "native" and not has_neutral_source)):
            raise ValueError("saved Procrustes preflight failed")
        preflights.append(command_path.relative_to(toolchain).as_posix())
    if not preflights:
        raise ValueError("selected evidence contains no actual Procrustes preflight")

    alias_facts = None
    if fresh or declaration["collector"] == "coroot":
        table_path = root / "runtime-identity-v5/supplied-service-aliases-training.json"
        admission_path = root / "runtime-identity-v5/supplied-service-alias-admission-training.json"
        table_sha = sha(table_path)
        admission = read(admission_path)
        if ((not fresh and admission.get("conflicts")) or admission.get("physical_identity_inferred")
                or admission.get("same_table_all_sources_and_direct_baseline") is not True):
            raise ValueError("supplied logical alias admission exceeds its reviewed boundary")
        projected_models = []
        retained_collisions = {}
        for alias_path in sorted(toolchain.glob(
                "discovery/*/*/observed.supplied-aliases.json")):
            alias = read(alias_path)
            directory = alias_path.parent
            raw = read(directory / "observed.bering-raw.json")
            effective = read(directory / "observed.json")
            if (alias.get("raw_model_sha256") != sha(directory / "observed.bering-raw.json")
                    or alias.get("table_sha256") != table_sha
                    or (not fresh and alias.get("metadata_collisions"))
                    or alias.get("graph_edges_injected")
                    or alias.get("physical_identity_inferred")
                    or alias.get("roles_or_endpoints_created")):
                raise ValueError("saved alias proof exceeds exact logical renaming")
            aliases = alias.get("effective_aliases") or {}
            if any((admission.get("aliases") or {}).get(key) != value
                   for key, value in aliases.items()):
                raise ValueError("saved effective alias was not admitted from supplied inventory")
            projected = alias_only_model(raw, aliases)
            if projected != effective:
                raise ValueError("saved semantic model is not exact alias-only projection")
            projected_models.append(alias_path.relative_to(toolchain).as_posix())
            if fresh:
                retained_collisions[alias_path.relative_to(toolchain).as_posix()] = alias.get("metadata_collisions") or []
        if not projected_models:
            raise ValueError("selected evidence contains no supplied-alias graph proof")
        alias_facts = {"table_sha256": table_sha, "admission_sha256": sha(admission_path),
                       "exact_alias_only_models": projected_models}
        if fresh:
            alias_facts.update(admission_conflicts=admission.get("conflicts") or [],
                               metadata_collisions=retained_collisions)

    branch_facts = []
    context_facts = None
    paired = declaration['head_sha'] in CONTEXT_BASELINE_HEADS
    forecasts_path = toolchain / "forecasts.json"
    forecasts = read(forecasts_path) if forecasts_path.is_file() else None
    if forecasts is not None:
        evaluation_list = ((evaluation or {}).get("evaluations") or [])
        evaluation_rows = {(row["source"], row["variant"], row["operation"]): row
                           for row in evaluation_list}
        if len(evaluation_rows) != len(evaluation_list):
            raise ValueError("saved evaluation contains duplicate branch keys")
        forecast_keys = {
            (source, variant, operation)
            for source, variants in forecasts.items()
            for variant, operations in variants.items()
            for operation in operations}
        expected_evaluation_keys = forecast_keys | ({
            ('context-baseline', variant, operation)
            for variant, operations in forecasts['combined'].items() for operation in operations} if paired else set())
        if evaluation is not None and expected_evaluation_keys != set(evaluation_rows):
            raise ValueError("saved forecast and evaluation branch-key coverage differs")
        for source, variants in forecasts.items():
            for variant, operations in variants.items():
                for operation, saved_row in operations.items():
                    row = evaluation_rows.get((source, variant, operation))
                    if evaluation is not None and row is None:
                        raise ValueError(
                            f"saved forecast has no evaluation row: {source}/{variant}/{operation}")
                    if row is not None:
                        for key in ("available", "reason", "prediction", "interval"):
                            evaluation_key = "forecast_interval" if key == "interval" else key
                            if row.get(evaluation_key) != saved_row.get(key):
                                raise ValueError(
                                    "saved forecast/evaluation field differs: "
                                    f"{source}/{variant}/{operation}/{key}")
                    branch = toolchain / source / variant / operation
                    command_path = branch / "simulation.command.json"
                    model_path = branch / "model.json"
                    command = read(command_path) if command_path.is_file() else None
                    if saved_row.get("available"):
                        if (command is None or command.get("returncode") != 0
                                or not model_path.is_file()):
                            raise ValueError(
                                "available saved branch lacks successful Sheaft command/model")
                        graph_sha = (row.get("graph_sha256") if row is not None
                                     else saved_row.get("graph_sha256"))
                        if graph_sha and sha(model_path) != graph_sha:
                            raise ValueError(
                                "available Sheaft model hash differs from saved forecast")
                        for path in (command_path, model_path):
                            freeze_key = "toolchain/" + path.relative_to(toolchain).as_posix()
                            if (freeze is not None
                                    and freeze["sha256_by_path"].get(freeze_key) != sha(path)):
                                raise ValueError("available Sheaft input is not frozen")
                        graph_path = (toolchain/shared_origins[source,variant]/'observed.json'
                                      if (source,variant) in shared_origins else
                                      toolchain / "discovery" / source / variant / "observed.json")
                        graph = read(graph_path)
                        model = read(model_path)
                        graph_edges = {item["id"] for item in graph.get("edges") or []}
                        graph_endpoints = {item["id"] for item in graph.get("endpoints") or []}
                        model_edges = {item["id"] for item in model.get("edges") or []}
                        model_endpoints = {item["id"] for item in model.get("endpoints") or []}
                        if not model_edges.issubset(graph_edges) or not model_endpoints.issubset(graph_endpoints):
                            raise ValueError("Sheaft model contains unobserved graph identities")
                    metadata_facts = None
                    if saved_row.get('available') and declaration['head_sha'] in METADATA_ATTACHMENT_HEADS:
                        metadata_facts = (paired_simulation_facts(toolchain, branch, saved_row, freeze)
                            if declaration['head_sha'] in CONTEXT_BASELINE_HEADS
                            else operation_metadata_facts(toolchain, branch, freeze))
                    branch_facts.append({
                        "source": source, "variant": variant, "operation": operation,
                        "available_copied": saved_row.get("available"),
                        "reason_copied": saved_row.get("reason"),
                        "prediction_copied": saved_row.get("prediction"),
                        "saved_command_present": command is not None,
                        "saved_command_returncode": command.get("returncode") if command else None,
                        "saved_model_present": model_path.is_file(),
                        "provided_metadata_attachment": metadata_facts,
                        "binding_summary": saved_binding_summary(toolchain, branch, freeze),
                        "observed_edge_ids_retained": (
                            sorted(model_edges) if saved_row.get("available") else None),
                        "observed_endpoint_ids_retained": (
                            sorted(model_endpoints) if saved_row.get("available") else None),
                    })
        if paired:
            context_facts = context_baseline_facts(root, toolchain, freeze, forecasts, evaluation)
    else:
        raise ValueError("selected evidence lacks saved forecasts")

    drain = read(root / "observations/drain-evidence.json")
    if (not drain.get("technical_complete") or not drain.get("technical_valid")
            or not drain.get("accepted_receiver_bytes_closed_and_hashed")):
        raise ValueError("saved final drain is not technically complete")
    collector = read(root / "observations/collector.json")
    expected_collector = COLLECTOR_PINS[declaration["collector"]]
    if (collector.get("collector") != declaration["collector"]
            or collector.get("technical_valid") is False
            or collector.get("closed_checkpoint") is not True
            or collector.get("nodes") != ["a", "b"]
            or any(collector.get(key) != value for key, value in expected_collector.items())):
        raise ValueError("collector manifest differs from the pinned closed acquisition")
    closures = {}
    for node in (("native",) if declaration["collector"] == "deepflow" else ("a", "b", "native")):
        closure = read(root / f"observations/receiver-closed-{node}.json")
        if (closure.get("node") != node or closure.get("saved_bytes_valid") is not True
                or closure.get("in_flight_handlers_joined") is not True
                or closure.get("listening_socket_closed") is not True
                or closure.get("wrapper_json_decode_error_count") != 0
                or closure.get("errors_json_decode_error_count") != 0
                or closure.get("receiver_parse_or_read_failure_count") != 0):
            raise ValueError(f"receiver closure is incomplete: {node}")
        closures[node] = {key: closure.get(key) for key in (
            "saved_bytes_valid", "in_flight_handlers_joined", "listening_socket_closed",
            "wrapper_json_decode_error_count", "errors_json_decode_error_count",
            "receiver_parse_or_read_failure_count")}
    control = read(root / "observations/technical-positive-control.json")
    if (control.get("collector") != declaration["collector"]
            or set(control.get("proofs") or {}) != {"a", "b"}
            or control.get("cleanup_verified") is not True
            or control.get("cleanup_failures")):
        raise ValueError("technical control lacks exact two-node origin/cleanup proof")
    controls = []
    for node, claim in (control.get("proofs") or {}).items():
        if declaration["collector"] == "deepflow":
            controls.append(deepflow_control_facts(root, control, node, claim))
            continue
        body = root / "observations" / claim["raw_ref"]
        if not body.is_file() or sha(body) != claim["raw_sha256"]:
            raise ValueError("selected-agent raw control body differs")
        request = ExportTraceServiceRequest.FromString(body.read_bytes())
        matched = []
        for resource in request.resource_spans:
            resource_attrs = {
                item.key: getattr(item.value, item.value.WhichOneof("value"))
                for item in resource.resource.attributes}
            for scope in resource.scope_spans:
                for span in scope.spans:
                    attrs = {item.key: getattr(item.value, item.value.WhichOneof("value"))
                             for item in span.attributes}
                    if control.get("marker") not in str(attrs) and control.get("marker") not in str(span):
                        continue
                    if declaration["collector"] == "obi":
                        if (resource_attrs.get("telemetry.distro.name")
                                != "opentelemetry-ebpf-instrumentation"
                                or resource_attrs.get("telemetry.distro.version") != "v0.15.2"
                                or (scope.scope.name or resource_attrs.get("otel.scope.name"))
                                != "go.opentelemetry.io/obi"
                                or resource_attrs.get("container.name") not in {
                                    f"study-ebpf-control-server-{node}",
                                    f"study-ebpf-control-client-{node}"}):
                            continue
                    elif declaration["collector"] == "coroot":
                        if (scope.scope.name != "coroot-node-agent" or span.kind != 3
                                or resource_attrs.get("service.name")
                                != f"/docker/study-ebpf-control-client-{node}"):
                            continue
                    matched.append({"scope": scope.scope.name, "span_kind": span.kind,
                                    "service": resource_attrs.get("service.name"),
                                    "container": resource_attrs.get("container.name")})
        if not matched:
            raise ValueError("raw control lacks the selected collector origin")
        controls.append({"node": node, "raw_sha256": claim["raw_sha256"], "matches": matched})
    standalone = (deepflow_closure_facts(root, collector, drain)
                  if declaration["collector"] == "deepflow" else None)
    worker_facts = None
    remote_root = root / "infrastructure/remote-toolchain-v4"
    if not (remote_root / "parent-import.json").is_file() and handoff_selected.is_dir():
        remote_root = handoff_selected
    parent_import_path = remote_root / "parent-import.json"
    if (declaration["head_sha"] in ({PETCLINIC_WORKER_HEAD, POSTCAPTURE_GUEST_RELEASE_HEAD, CLOSED_POSTCAPTURE_HEAD, CLOSED_CAPTURE_RECOVERY_HEAD} | IDENTICAL_INPUT_DISCOVERY_HEADS)) and not parent_import_path.is_file():
        raise ValueError("named worker source requires retained parent worker import")
    worker_provenance_path = remote_root / "worker/worker-provenance.json"
    worker_status_path = remote_root / "worker/worker-status.json"
    if parent_import_path.is_file():
        parent_import = read(parent_import_path)
        worker_provenance = read(worker_provenance_path)
        worker_status = read(worker_status_path)
        output_manifest = read(remote_root / "worker/output-manifest.json")
        index = read(remote_root / "training-index-proof.json")
        parent_phase = ('parent_after_dispatch_before_import'
                        if declaration['head_sha'] == UPLOAD_HOLD_PARENT_PROOF_HEAD else 'parent_before_dispatch')
        identities = [parent_import.get("identity") or {},
                      worker_provenance.get("identity") or {},
                      worker_status.get("identity") or {},
                      output_manifest.get("identity") or {}]
        for identity in identities:
            if (str(identity.get("run_id")) != str(scientific["run_id"])
                    or identity.get("system") != declaration["system"]
                    or identity.get("mode") != declaration["mode"]
                    or int(identity.get("seed")) != declaration["seed"]
                    or identity.get("commit") != scientific["head_sha"]):
                raise ValueError("saved worker/handoff identity differs from declared cell")
        if (parent_import.get("downloaded_archive_sha256")
                != str(parent_import.get("worker_artifact_digest", "")).removeprefix("sha256:")
                or worker_status.get("status") != "complete"
                or worker_status.get("checkpoint_unchanged") is not True
                or worker_provenance.get("checkpoint_unchanged") is not True
                or worker_status.get("new_application_traffic") is not False
                or worker_provenance.get("new_application_traffic") is not False
                or str(parent_import.get("worker_run_id"))
                    != str(worker_provenance.get("worker_run_id"))
                or str(parent_import.get("worker_run_id"))
                    != str(worker_status["identity"].get("worker_run_id"))
                or index.get("checkpoint") != index.get(parent_phase)
                or index.get("checkpoint") != index.get("parent_after_worker")):
            raise ValueError("saved worker import/status identity is incomplete")
        manifest_claims = output_manifest.get("toolchain_files") or {}
        package_claims = (packages.get("toolchain") or {}).get("_file_claims") or {}
        worker_freeze = freeze if freeze is not None else {
            "sha256_by_path": saved.get("sha256_by_path") or {}}
        output_claim_scope = verify_worker_output_claims(
            manifest_claims, worker_provenance.get("toolchain_files") or {},
            package_claims, toolchain, worker_freeze)
        output_claim_scope["freeze_map_binding"] = (
            "compact_freeze_equals_forecast_saved_and_selected_claims_match"
            if freeze is not None else
            "selected_claims_match_forecast_saved; compact_freeze_comparison_external_pending")
        worker_facts = {"parent_import": parent_import,
                        "worker_provenance": worker_provenance,
                        "worker_status": worker_status,
                        "output_manifest": output_manifest,
                        "training_index_proof": index,
                        "output_claim_scope": output_claim_scope}
        scheduled_proof = upload_hold_parent_proof_facts(
            root, remote_root, declaration, index, worker_provenance, parent_import, saved)
        if scheduled_proof is not None:
            worker_facts['parent_proof_schedule'] = scheduled_proof
    if declaration["system"] == "deathstarbench" and worker_facts is None:
        raise ValueError("DSB evidence lacks the required remote worker/handoff proof")
    for package in packages.values():
        package.pop("_file_claims", None)
    mode_files = {}
    sdk_flags = []
    otel_sdk_settings = {}
    for pattern in (
        "deployment/otel_demo/runtime-resolved-node-*.yaml",
        "deployment/petclinic/node-*/compose.yml",
        "deployment/deathstarbench/tracing-mode.json",
        "native/training/native-metadata.json", "native/final/native-metadata.json",
        "native/training/native-suppression-verification.json",
        "native/final/native-suppression-verification.json",
    ):
        for path in sorted(root.glob(pattern)):
            mode_files[path.relative_to(root).as_posix()] = sha(path)
            if path.suffix in (".yaml", ".yml"):
                document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                for name, service in (document.get("services") or {}).items():
                    environment = service.get("environment") or {}
                    value = (str(environment["OTEL_SDK_DISABLED"]).lower()
                             if "OTEL_SDK_DISABLED" in environment else None)
                    if declaration["system"] == "otel_demo":
                        if name in otel_sdk_settings and otel_sdk_settings[name] != value:
                            raise ValueError("rendered service has conflicting SDK settings")
                        otel_sdk_settings[name] = value
                    if "OTEL_SDK_DISABLED" in environment:
                        sdk_flags.append(value)
    if declaration["system"] == "deathstarbench":
        tracing = read(root / "deployment/deathstarbench/tracing-mode.json")
        if tracing.get("mode") != declaration["mode"]:
            raise ValueError("DSB rendered tracing mode differs from declaration")
        if declaration["mode"] == "absent" and not all(
                tracing.get(key) is True for key in (
                    "controlled_replica_sdks_disabled", "frontend_sdk_disabled",
                    "ordinary_service_sdks_disabled", "export_is_not_merely_blocked")):
            raise ValueError("DSB absent configuration does not disable native tracing")
    elif declaration["system"] == "otel_demo":
        sdk_flags = validate_otel_demo_sdk_settings(
            otel_sdk_settings, declaration["mode"])
    else:
        if not sdk_flags:
            raise ValueError("rendered deployment lacks explicit OTEL_SDK_DISABLED values")
        expected = declaration["mode"]
        if ((expected == "absent" and set(sdk_flags) != {"true"})
                or (expected == "partial" and set(sdk_flags) != {"true", "false"})
                or (expected == "full" and set(sdk_flags) != {"false"})):
            raise ValueError("rendered SDK configuration differs from declared mode")
    native_facts = native_mode_facts(root, scientific, evaluation)
    closed = closed_postcapture_facts(root, declaration,
        freeze or {"sha256_by_path": saved.get("sha256_by_path") or {}}, worker_facts, proof,
        compact=compact, restore_root=restore_root, actual_processing=actual_processing)
    return {
        "selected_transport": proof, "typed_packages": packages,
        "source_pins": pins, "saved_mode_evidence_sha256": mode_files,
        "collector_manifest": collector, "receiver_closure_facts": closures,
        "standalone_file_closure_facts": standalone,
        "rendered_sdk_disabled_values": sorted(sdk_flags),
        "native_mode_facts": native_facts,
        "guest_platform_facts": guest_facts,
        "supplied_logical_alias_facts": alias_facts,
        "paired_context_baseline_facts": context_facts,
        "worker_import_facts": worker_facts,
        "postcapture_guest_release_facts": postcapture,
        "closed_postcapture_processing_facts": closed,
        "forecast_saved_ns": saved.get("saved_ns"), "actual_bering": graphs,
        "actual_procrustes": preflights, "saved_branch_facts": branch_facts,
        "selected_raw_controls": controls, "final_drain": drain,
        **({'shared_observed_discovery_facts':shared_graphs} if shared_graphs else {}),
    }


def review(declaration: dict, compact: Path | None, full: Path | None, out: Path, *, smoke_qualification=False, restore_root=None, actual_processing=None) -> dict:
    if smoke_qualification and (compact is None or full is None):
        raise ValueError('qualification requires both selected full and compact evidence')
    if out.exists():
        raise ValueError("review output already exists")
    out.mkdir(parents=True)
    compact_result = evaluation = freeze = None
    if compact is not None:
        compact_result, evaluation, freeze = compact_facts(compact, declaration, smoke_qualification=smoke_qualification)
    full_result = None
    if full is not None:
        full_result = full_facts(full, declaration, freeze, evaluation, out / "selected-packages",
            compact=compact, restore_root=restore_root, actual_processing=actual_processing)
        if compact_result is not None and full_result["forecast_saved_ns"] >= compact_result["first_target_started_ns"]:
            raise ValueError("saved forecast does not precede first target block")
    result = {
        "schema_version": "main-saved-evidence-facts-v5",
        "review_scope": 'qualification_only_not_main' if smoke_qualification else 'saved_main_evidence',
        "declaration": declaration,
        "compact_facts": compact_result,
        "full_facts": full_result,
        "evidence_status": "automated_saved_fact_checks_complete; independent_family_interpretation_required",
        "automated_domain_checks": {
            "selected_transport_and_hashes": full_result is not None,
            "acquisition_controls_closure_and_collector_pins": full_result is not None,
            "bering_inputs_exports_and_models": full_result is not None,
            "saved_forecast_branch_coverage_and_sheaft_inputs": full_result is not None,
            "rendered_mode_and_native_census_contradictions": full_result is not None,
            "independent_scientific_admission_or_utility": False,
        },
        "independent_admission_performed": False,
        "scientific_processing_performed": False,
        "traffic_replay_refit_rescore_or_metric_performed": False,
        "availability_outcome_or_accuracy_used_as_gate": False,
        "cost_boundary": "saved cell costs copied; Actions transport/verification costs retained separately; human effort unknown",
    }
    (out / "saved-evidence-facts.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--declaration", type=Path, required=True)
    parser.add_argument("--compact", type=Path)
    parser.add_argument("--full", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--restore-diagnostics", type=Path)
    parser.add_argument("--actual-processing-metadata", type=Path)
    parser.add_argument('--smoke-qualification', action='store_true')
    args = parser.parse_args()
    declaration = read(args.declaration)
    result = review(declaration, args.compact, args.full, args.out, smoke_qualification=args.smoke_qualification,
        restore_root=args.restore_diagnostics, actual_processing=args.actual_processing_metadata)
    print(json.dumps({"cell": [declaration[key] for key in
                               ("collector", "system", "mode", "seed")],
                      "domains": {"compact": result["compact_facts"] is not None,
                                  "full": result["full_facts"] is not None}}))


if __name__ == "__main__":
    main()
