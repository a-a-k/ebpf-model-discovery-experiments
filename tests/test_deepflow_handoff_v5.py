from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import io

from google.protobuf import json_format
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)
import pytest

from ebpf_discovery.bering_v4 import _verified_stream_requests
from ebpf_discovery.deepflow_codec_v5 import codec_file
import ebpf_discovery.deepflow_handoff_v5 as handoff
from ebpf_discovery.raw_v4 import export_selection
from ebpf_discovery.store_v5 import ProjectionResolver
from ebpf_discovery.toolchain_v5 import Toolchain
from ebpf_discovery.supplied_alias_v5 import _verified_segment


class Store:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE files(path TEXT, consumed INTEGER)")
        self.db.execute("INSERT INTO files VALUES (?,?)", (str(path), path.stat().st_size))


def _row(resource: str, offset: int) -> dict:
    return {
        "signal_source": "EBPF", "tap_side": "ClientProcess",
        "ebpf_type": "TracePoint", "l7_protocol": "MySQL",
        "msg_type": "Request", "start_time": 100 + offset,
        "end_time": 110 + offset, "request_type": "Query",
        "request_resource": resource, "process_id_0": 42,
        "process_kname_0": "client",
    }


def _source(tmp_path: Path) -> tuple[Path, Path, list[dict]]:
    observations = tmp_path / "observations"
    raw = observations / "deepflow-raw" / "node-a" / "001-training" / "l7_flow_log"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"".join(
        json.dumps(_row(resource, ordinal), separators=(",", ":")).encode() + b"\n"
        for ordinal, resource in enumerate(("SELECT 1", "SELECT 2"))
    ))
    retained = raw.relative_to(observations).as_posix()
    batches, accounting, prefix = codec_file(
        raw, node="a", source_file="a/l7_flow_log", retained_file=retained,
        guest_context={"boot_id": "boot-a", "pid_namespace": "pid:[1]"},
    )
    assert prefix["normalized_records"] == 2 and len(batches) == 1
    for item in accounting:
        item.update(node="a", capture_stage="001-training")
    accounting_path = observations / "deepflow-codec-accounting.jsonl"
    accounting_path.write_text(
        "".join(json.dumps(item, separators=(",", ":")) + "\n" for item in accounting),
        encoding="utf-8",
    )
    snapshot = {
        "files": [{
            "snapshot_name": raw.name, "copied_bytes": raw.stat().st_size,
            "copied_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        }],
    }
    (raw.parent / "snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
    wrapper = observations / "a.jsonl"
    wrapper.write_text(json.dumps(batches[0], separators=(",", ":")) + "\n", encoding="utf-8")
    return wrapper, raw, accounting


def test_full_deepflow_source_codec_to_common_otlp_handoff(tmp_path: Path) -> None:
    wrapper, raw, _ = _source(tmp_path)

    result = export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "exports")

    assert result["observations"] == 2
    assert result["exports"] == []
    export, body = list(_verified_stream_requests(result))[0]
    assert export["source_representation"] == "derived_otlp_json"
    assert export["original_agent_wire"] is False
    proof = export["derived_otlp_proof"]
    assert proof["deterministic_envelope_equal"] is True
    assert proof["ids_invented"] is False
    assert proof["raw_dependencies"][0]["sha256"] == hashlib.sha256(
        raw.read_bytes()).hexdigest()
    assert proof["codec_accounting"]["path"] == "deepflow-codec-accounting.jsonl"
    payload = json.loads(body)
    request = json_format.ParseDict(payload, ExportTraceServiceRequest())
    spans = request.resource_spans[0].scope_spans[0].spans
    assert len(spans) == 2
    assert all(not span.trace_id and not span.span_id and not span.parent_span_id for span in spans)
    descriptor = result["stream_exports"][0]
    assert descriptor["requests"] == 1
    assert descriptor["wire_bytes"] == len(body)
    assert descriptor["storage_shards_are_not_http_batches"] is True


def test_alias_source_proof_uses_the_existing_deterministic_deepflow_validator(tmp_path):
    wrapper, _, _ = _source(tmp_path)
    digest = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    proof = _verified_segment(wrapper, 0, wrapper.stat().st_size, digest,
                              'a', 'ebpf-deepflow', True)
    assert proof['sources'] == ['ebpf-deepflow:a']
    assert proof['source_representation'] == 'derived_otlp_json'
    assert proof['derived_envelopes_reverified'] == 1
    assert set(proof['ordinals']) == {0, 1}
    with pytest.raises(ValueError, match='derived source/node mismatch'):
        _verified_segment(wrapper, 0, wrapper.stat().st_size, digest,
                          'b', 'ebpf-deepflow', True)


def test_alias_source_proof_rejects_changed_derived_fields_even_with_valid_segment_hash(tmp_path):
    wrapper, _, _ = _source(tmp_path)
    document = json.loads(wrapper.read_text())
    document['payload']['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['name'] = 'invented'
    wrapper.write_text(json.dumps(document) + '\n', encoding='utf-8')
    digest = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='envelope differs from deterministic codec'):
        _verified_segment(wrapper, 0, wrapper.stat().st_size, digest,
                          'a', 'ebpf-deepflow', True)
def test_accounting_uses_byte_splitlines_and_preserves_literal_u2028(tmp_path: Path) -> None:
    wrapper, _, accounting = _source(tmp_path)
    accounting[0]["literal_separator"] = "left\u2028right"
    accounting_path = wrapper.parent / "deepflow-codec-accounting.jsonl"
    accounting_path.write_text(
        "".join(json.dumps(item, separators=(",", ":"), ensure_ascii=False) + "\n"
                for item in accounting), encoding="utf-8")
    assert export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "valid")[
        "observations"] == 2

    first, second = accounting_path.read_bytes().splitlines()
    accounting_path.write_bytes(first + "\u2028".encode() + b'{"extra":true}\n' + second + b'\n')
    with pytest.raises(json.JSONDecodeError):
        export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "invalid")


def test_accounting_byte_boundaries_match_historical_bytes_splitlines() -> None:
    payload = b"one\r\ntwo\rthree\nfour\xe2\x80\xa8inside\nlast"
    class OneByteReader(io.BytesIO):
        def read(self, size=-1):
            return super().read(1 if size != 0 else 0)
    actual = [line for _, line in handoff.DeepFlowDerivedValidator._byte_lines(
        OneByteReader(payload))]
    assert actual == payload.splitlines()


def test_accounting_mutation_between_index_pass_and_proof_fails(
        tmp_path: Path, monkeypatch) -> None:
    wrapper, _, _ = _source(tmp_path)
    accounting_path = wrapper.parent / "deepflow-codec-accounting.jsonl"
    original_body = accounting_path.read_bytes()
    original_lines = handoff.DeepFlowDerivedValidator._byte_lines
    def mutate_after_index(stream):
        yield from original_lines(stream)
        accounting_path.write_bytes(original_body + b" \n")
    monkeypatch.setattr(handoff.DeepFlowDerivedValidator, "_byte_lines",
                        staticmethod(mutate_after_index))
    with pytest.raises(ValueError, match="changed while indexing"):
        export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "changed")


def test_accounting_index_preserves_typed_locator_key_distinction(tmp_path: Path) -> None:
    wrapper, _, accounting = _source(tmp_path)
    extraneous = dict(accounting[0]); extraneous["offset"] = str(extraneous["offset"])
    accounting_path = wrapper.parent / "deepflow-codec-accounting.jsonl"
    accounting_path.write_text("".join(
        json.dumps(row, separators=(",", ":")) + "\n" for row in [*accounting, extraneous]))
    result = export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "typed")
    assert result["observations"] == 2

    duplicate = dict(accounting[0])
    accounting_path.write_text("".join(
        json.dumps(row, separators=(",", ":")) + "\n" for row in [*accounting, duplicate]))
    with pytest.raises(ValueError, match="lacks unique normalized codec accounting"):
        export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "true-duplicate")


def test_derived_projection_index_preserves_old_metadata_flags(tmp_path: Path) -> None:
    wrapper, _, accounting = _source(tmp_path)
    resolver = ProjectionResolver(tmp_path, tmp_path / "values.jsonl")
    for row in accounting:
        key = tuple(row[name] for name in (
            "source_file", "retained_file", "offset", "length", "sha256"))
        resolver.add(key, {"service": "database", "resolution": {"status": "resolved"}})
    resolver.finalize()
    result = export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "projected",
                              service_projections=resolver)
    index = Path(result["stream_exports"][0]["request_index"]["path"])
    row = json.loads(index.read_text().splitlines()[0])
    assert row["validated_derived_wrapper_unchanged"] is True
    assert row["graph_edges_injected"] is False
    assert len(row["runtime_identity_transformation_refs"]) == 2
    resolver.close()


def test_common_product_profiles_accept_derived_export_without_vendor_profile() -> None:
    tool = Toolchain.__new__(Toolchain)
    tool.system = "petclinic"
    assert tool.ebpf_collection_args() == [
        "--collection-source", "ebpf-otlp",
        "--source-domain", "petclinic-deployment",
    ]
    assert tool.bering_source_profile() == {"source_id": "ebpf", "input_type": "ebpf-otlp"}


@pytest.mark.parametrize("mutation,match", [
    ("declaration", "declaration differs"),
    ("raw", "raw segment differs"),
    ("accounting", "accounting differs"),
    ("snapshot", "snapshot does not bind"),
    ("wrapper", "envelope differs"),
    ("invented_id", "envelope differs"),
])
def test_deepflow_derived_handoff_adversaries_fail_closed(
        tmp_path: Path, mutation: str, match: str) -> None:
    wrapper, raw, accounting = _source(tmp_path)
    document = json.loads(wrapper.read_text())
    if mutation == "declaration":
        document["derived_otlp"]["source_commit"] = "0" * 40
        wrapper.write_text(json.dumps(document) + "\n")
    elif mutation == "raw":
        body = raw.read_bytes().replace(b"SELECT 1", b"SELECT X", 1)
        raw.write_bytes(body)
        snapshot_path = raw.parent / "snapshot.json"
        snapshot = json.loads(snapshot_path.read_text())
        snapshot["files"][0]["copied_sha256"] = hashlib.sha256(body).hexdigest()
        snapshot_path.write_text(json.dumps(snapshot))
    elif mutation == "accounting":
        accounting[0]["protocol"] = "Kafka"
        (wrapper.parent / "deepflow-codec-accounting.jsonl").write_text(
            "".join(json.dumps(item) + "\n" for item in accounting))
    elif mutation == "snapshot":
        snapshot_path = raw.parent / "snapshot.json"
        snapshot = json.loads(snapshot_path.read_text())
        snapshot["files"][0]["copied_sha256"] = "0" * 64
        snapshot_path.write_text(json.dumps(snapshot))
    elif mutation == "wrapper":
        document["payload"]["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["name"] = "changed"
        wrapper.write_text(json.dumps(document) + "\n")
    else:
        document["payload"]["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["traceId"] = "1" * 32
        wrapper.write_text(json.dumps(document) + "\n")
    with pytest.raises(ValueError, match=match):
        export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "exports")


def test_full_dependency_hashes_are_cached_but_each_segment_is_checked(
        tmp_path: Path, monkeypatch) -> None:
    wrapper, raw, _ = _source(tmp_path)
    counts: dict[Path, int] = {}
    original = handoff._sha

    def tracked(path: Path) -> str:
        resolved = Path(path).resolve()
        counts[resolved] = counts.get(resolved, 0) + 1
        return original(path)

    monkeypatch.setattr(handoff, "_sha", tracked)
    export_selection(Store(wrapper), {"ebpf": None}, tmp_path / "exports")
    assert counts[raw.resolve()] == 1
    assert counts[(raw.parent / "snapshot.json").resolve()] == 1


def test_actions_qualification_is_no_vm_and_uses_exact_v5_build_path() -> None:
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" /
                "qualify-deepflow-handoff-v5.yml").read_text(encoding="utf-8")
    script = (root / "scripts" / "qualify-deepflow-handoff-v5.py").read_text(
        encoding="utf-8")
    assert "scripts/setup-toolchain-v4.sh work/toolchain-build v5" in workflow
    assert "scripts/qualify-deepflow-handoff-v5.py" in workflow
    assert "vms.sh" not in workflow and "campaign_v5" not in workflow
    assert "sheaft_executed\": False" in script
    assert "refit_rescore_or_external_outcomes_used\": False" in script
