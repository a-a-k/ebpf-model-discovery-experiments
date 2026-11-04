import hashlib
import json

from ebpf_discovery.summary_manifest_v5 import FILES, record


def test_existing_manifest_fields_and_journal_hash_are_preserved(tmp_path):
    journal = b'{"preserved":"complete response"}\n'
    (tmp_path / "attempt-journal.jsonl").write_bytes(journal)
    result = record(tmp_path, system="otel_demo", mode="absent", seed=6, collector="deepflow",
                    stage="main", run_id="42", commit="a"*40)
    assert set(result["files_sha256"]) == {
        "evaluation-v5.json", "status.json", "plans.json", "census.json", "blocks.json",
        "freeze-integrity.json", "toolchain/forecasts.json", "evidence-v4.json", "attempt-journal.jsonl"}
    assert result["files_sha256"]["attempt-journal.jsonl"] == hashlib.sha256(journal).hexdigest()
    assert result == {
        "schema_version": "v5-cell-summary-manifest", "run_id": "42", "commit": "a"*40,
        "system": "otel_demo", "mode": "absent", "seed": 6, "collector": "deepflow", "smoke": False,
        "full_artifact_name": "campaign-v5-deepflow-main-otel_demo-absent-6-42",
        "files_sha256": {name: hashlib.sha256(journal).hexdigest() if name == "attempt-journal.jsonl" else None
                         for name in FILES},
        "full_artifact_transport": "original-file-tree",
        "original_evidence_reverified_by_compact_report": False,
    }
    assert json.loads((tmp_path / "evaluation-manifest.json").read_text()) == result


def test_qualification_publication_cannot_appear_as_a_new_main_case(tmp_path):
    capture = {"run_id": "original", "commit": "a"*40, "system": "otel_demo",
               "collector": "deepflow", "mode": "full", "seed": 6}
    (tmp_path / "status.json").write_text(json.dumps(capture))
    result = record(tmp_path, system="otel_demo", mode="full", seed=6, collector="deepflow",
                    stage="main", run_id="qualification", commit="b"*40, qualification_only=True)
    assert result["qualification_only"] is True and result["scientific_capture_identity"] == capture
    assert result["run_id"] == "qualification" and result["commit"] == "b"*40
    assert result["full_artifact_name"] == "qualification-campaign-v5-deepflow-main-otel_demo-full-6-qualification"
