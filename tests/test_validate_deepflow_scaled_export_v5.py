from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import sqlite3
import zipfile
import io

import pytest

from ebpf_discovery.bering_v4 import _verified_stream_requests
from ebpf_discovery.raw_v4 import _DeepFlowRequestArchive


def _module():
    path = Path(__file__).parents[1] / "scripts" / "validate-deepflow-scaled-export-v5.py"
    spec = importlib.util.spec_from_file_location("validate_deepflow_scaled_export_v5", path)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_repack_changes_only_storage_boundaries(tmp_path):
    (tmp_path / "original").mkdir()
    archive = _DeepFlowRequestArchive(tmp_path / "original", "ebpf", None)
    bodies = [b'{"resourceSpans":[{"a":1}]}\n', b'{"resourceSpans":[{"a":2}]}\n']
    for body in bodies:
        archive.append(body, {"source": "ebpf", "content_type": "application/json",
            "content_encoding": "", "observations": 1}, [])
    descriptor = archive.finish()
    alternate = _module()._repack(descriptor, tmp_path / "alternate")
    assert [body for _, body in _verified_stream_requests(
        {"stream_exports": [alternate]})] == bodies
    assert alternate["requests"] == descriptor["requests"]
    assert alternate["observations"] == descriptor["observations"]
    assert len(alternate["shards"]) == 1


def test_zip_safety_rejects_escape_and_symlink():
    module = _module()
    assert module._safe(zipfile.ZipInfo("checkpoint/status.json"))
    assert not module._safe(zipfile.ZipInfo("../status.json"))
    link = zipfile.ZipInfo("checkpoint/link")
    link.external_attr = 0o120777 << 16
    assert not module._safe(link)


def test_old_oracle_calls_bytes_splitlines_on_bounded_lf_rows():
    module = _module(); payload = "one\u2028inside\ntwo\n".encode()
    assert list(module._old_bytes_splitlines_for_lf_source(io.BytesIO(payload))) == [
        (0, "one\u2028inside".encode()), (len("one\u2028inside\n".encode()), b"two")]
    with pytest.raises(ValueError, match="not LF-only"):
        list(module._old_bytes_splitlines_for_lf_source(io.BytesIO(b"one\r\ntwo\n")))


def test_old_sql_oracle_preserves_authority_and_duplicate_semantics(tmp_path):
    module = _module(); source = sqlite3.connect(":memory:")
    source.execute("CREATE TABLE runtime_identity_projection("
                   "status TEXT,resolution TEXT,inventory_path TEXT,inventory_sha256 TEXT)")
    locator = {"source_file": "a/raw", "retained_file": "deepflow-raw/a/raw",
               "offset": 0, "length": 3, "sha256": "a" * 64}
    def resolution(service, flag):
        return {"record_locator": locator, "service_identity": {"compose_service": service},
                "diagnostic": {"flag": flag}}
    for flag in (1, True):
        source.execute("INSERT INTO runtime_identity_projection VALUES (?,?,?,?)",
            ("resolved_enriched", json.dumps(resolution("database", flag)),
             "inventory.json", "b" * 64))
    source.commit()
    oracle = module._OldSqlProjectionOracle(source, tmp_path / "oracle.sqlite")
    value = oracle.get(("a/raw", "deepflow-raw/a/raw", 0, 3, "a" * 64))
    assert value["service"] == "database"
    assert value["resolution"]["diagnostic"]["flag"] is True
    oracle.close()

    source.execute("INSERT INTO runtime_identity_projection VALUES (?,?,?,?)",
        ("resolved_enriched", json.dumps(resolution("frontend", True)),
         "inventory.json", "b" * 64))
    source.commit()
    with pytest.raises(ValueError, match="conflicting duplicate"):
        module._OldSqlProjectionOracle(source, tmp_path / "conflict.sqlite")


def test_bering_semantic_projection_allows_only_documented_run_provenance():
    module = _module()
    body_sha = "a" * 64
    evidence = json.dumps({"sources": [{"ref": "bering://serve?listen=127.0.0.1%3A1234"}]})
    model = {"metadata": {"discovered_at": "now"}, "services": [{"id": "a"}],
             "edges": [{"id": "a-b", "observed": {"latency_ms": {"p50": 2.5}},
                        "metadata": {"attributes": {
                            "bering.observation_evidence.v1": evidence}}}], "endpoints": []}
    snapshot = {"model": json.loads(json.dumps(model)),
        "metadata": {"emitted_at": "now"}, "snapshot_id": "snap-one",
        "window_start": "one", "window_end": "two", "topology_version": "stable"}
    quality = {"generated_at": "now", "artifact": {"path": "/one/model.snapshot.json",
        "snapshot_id": "snap-one", "window_start": "one", "window_end": "two",
        "topology_version": "stable"}, "coverage": {"confidence": .8},
        "observation_evidence": [{"evidence": {"sources": [{"ref":
            f"/one/observed-runtime/ebpf-capture/100-00000001-{body_sha}.json"}]}}]}
    other_model = json.loads(json.dumps(model)); other_quality = json.loads(json.dumps(quality))
    other_model["metadata"]["discovered_at"] = "later"
    other_model["edges"][0]["metadata"]["attributes"]["bering.observation_evidence.v1"] = \
        json.dumps({"sources": [{"ref": "bering://serve?listen=127.0.0.1%3A9999"}]})
    other_quality.update(generated_at="later")
    other_quality["artifact"].update(path="/two/model.snapshot.json", snapshot_id="snap-two",
                                     window_start="three", window_end="four")
    other_quality["observation_evidence"][0]["evidence"]["sources"][0]["ref"] = \
        f"/two/model-runtime/ebpf-capture/999-00000001-{body_sha}.json"
    other_snapshot = json.loads(json.dumps(snapshot))
    other_snapshot.update(model=json.loads(json.dumps(other_model)), snapshot_id="snap-two",
                          window_start="three", window_end="four")
    other_snapshot["metadata"]["emitted_at"] = "later"
    first, first_diff = module._bering_semantic_projection(
        model, snapshot, quality, [body_sha])
    second, second_diff = module._bering_semantic_projection(
        other_model, other_snapshot, other_quality, [body_sha])
    assert first == second and first_diff and second_diff

    changed_model = json.loads(json.dumps(other_model))
    changed_model["edges"][0]["observed"]["latency_ms"]["p50"] = 9.5
    changed_snapshot = json.loads(json.dumps(other_snapshot)); changed_snapshot["model"] = changed_model
    assert module._bering_semantic_projection(
        changed_model, changed_snapshot, other_quality, [body_sha])[0] != first
    changed_quality = json.loads(json.dumps(other_quality))
    changed_quality["coverage"]["confidence"] = .2
    assert module._bering_semantic_projection(
        other_model, other_snapshot, changed_quality, [body_sha])[0] != first
    changed_quality["observation_evidence"][0]["evidence"]["sources"][0]["ref"] = \
        f"/two/observed-runtime/ebpf-capture/999-00000001-{'b' * 64}.json"
    with pytest.raises(ValueError, match="does not bind accepted request"):
        module._bering_semantic_projection(
            other_model, other_snapshot, changed_quality, [body_sha])
