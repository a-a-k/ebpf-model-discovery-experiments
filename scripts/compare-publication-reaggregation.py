#!/usr/bin/env python3
"""Compare already-produced analytical outputs; no reaggregation or model calls."""
from __future__ import annotations
import argparse
import csv
import difflib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import zipfile

REPO = "a-a-k/ebpf-model-discovery-experiments"
REFERENCE = {
    "id": 13847060602, "bytes": 480484,
    "sha256": "2a76452eef3d751431f48a59f7907daabb50d6bf2b506e5096560536b4b073b8",
    "run_id": 43001870142,
    "source": "dc2b95d09af57636d9fcd6ace3ee4ae8a739f419",
    "name": "sosym-analysis-43001870142",
}
REPLAY = {
    "id": 13879962480, "bytes": 18047490,
    "sha256": "0cb833199266f63d6a9aa237c12878a61928268040e897887e70f55b92620606",
    "run_id": 43063706864,
    "source": "91c4a8334cea968c00da3f62c23b2f192cdc18e6",
    "name": "publication-example-replay-43063706864-attempt1",
}
ANALYSIS_SCRIPT = "10255b138ccd49e575007b358590066759f3b244c80dc262314e1416e86354fe"
TRANSPORT_SCRIPT = "6bea09a0310fdcc7d70c0aa60f51f01c2bed23aa5928ff85e7988d14a878a359"
PINS = {
    "original": "1153f70032bc36bbc1936e666c8338e0935c24d2c8553b64836e711c9005bf36",
    "corrected": "d772bd51c199397f5b5d2aaa623d255946cbaf6541b7955ab74a145eaac2a345",
    "correction_report": "d69134c8bf4bc617d3ab5fbe8146617277c7b62cd425801a9c9a8b3928b57f44",
    "cost_ledger": "198cd5825bea33567353afb5166d552c9a2df963b8f4a86628122de82a4cbf3e",
    "provenance": "851a1d5a3f10077ebdbf4d4da9feb9bf29fd32c9d744b9d939ada930a6c05db1",
}
CSV_NAMES = (
    "cases.csv", "source-view-results.csv", "primary-outcomes.csv",
    "primary-state-outcomes.csv", "database-outcomes.csv", "primary-summary.csv",
    "all-view-summary.csv", "case-source-summary.csv", "database-summary.csv",
    "direct-summary.csv", "operation-summary.csv", "context-comparison.csv",
    "classification.csv", "classification-summary.csv", "case-latency.csv",
    "latency-summary.csv", "asynchronous-controls.csv", "costs.csv",
    "obi-absent-results.csv", "all-primary-discrepancies.csv",
)
TEX_NAMES = (
    "table-coverage-full.tex", "table-coverage-main.tex",
    "table-errors-summary.tex", "table-all-discrepancies.tex",
)
JSON_NAMES = ("analysis.json", "case-provenance.json", "analysis-manifest.json")
EXPECTED = set(CSV_NAMES + TEX_NAMES + JSON_NAMES)
MAX_MEMBER = 64 * 1024**2
MAX_TOTAL = 128 * 1024**2
MAX_DIFFERENCES = 16 * 1024**2


class AuditError(Exception):
    pass


def need(condition, code):
    if not condition:
        raise AuditError(code)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def verify_file(path, expected):
    need(path.is_file(), "pinned_archive_missing")
    need(path.stat().st_size == expected["bytes"], "pinned_archive_size_mismatch")
    actual = sha_file(path)
    need(actual == expected["sha256"], "pinned_archive_sha256_mismatch")
    return {"bytes": path.stat().st_size, "sha256": actual}


def transport_module():
    path = Path(__file__).with_name("replay-publication-example.py")
    need(sha_file(path) == TRANSPORT_SCRIPT, "transport_source_pin_mismatch")
    spec = importlib.util.spec_from_file_location("publication_read_transport", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(module.ARCHIVE_DOWNLOAD_BUDGET == 6000000000, "shared_budget_limit_mismatch")
    return module


def read_outputs(path, manifest_suffix):
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        need(len(names) == len(set(names)), "duplicate_zip_member")
        manifests = [
            name for name in names
            if name == manifest_suffix or name.endswith("/" + manifest_suffix)
        ]
        need(len(manifests) == 1, "analysis_manifest_missing_or_ambiguous")
        prefix = manifests[0][:-len("analysis-manifest.json")]
        selected = {
            item.filename[len(prefix):]: item for item in infos
            if item.filename.startswith(prefix) and not item.is_dir()
        }
        need(set(selected) == EXPECTED, "analytical_output_file_set_mismatch")
        need(all(item.file_size <= MAX_MEMBER for item in selected.values()),
             "analytical_member_expansion_bound")
        need(sum(item.file_size for item in selected.values()) <= MAX_TOTAL,
             "analytical_total_expansion_bound")
        data = {name: archive.read(item) for name, item in selected.items()}
        locations = {name: item.filename for name, item in selected.items()}
    return data, locations


def verify_outputs(data, producer):
    analysis = json.loads(data["analysis.json"])
    manifest = json.loads(data["analysis-manifest.json"])
    need(analysis.get("schema") == "sosym-publication-analysis-v1", "analysis_schema_mismatch")
    execution = analysis.get("execution") or {}
    need(str(execution.get("run_id")) == str(producer["run_id"]), "analysis_producer_run_mismatch")
    need(execution.get("source") == producer["source"], "analysis_producer_source_mismatch")
    need(execution.get("script_sha256") == ANALYSIS_SCRIPT, "analysis_script_pin_mismatch")
    inputs = analysis.get("inputs") or {}
    need(set(inputs) == set(PINS), "analysis_input_role_set_mismatch")
    for role, expected in PINS.items():
        need(inputs[role].get("sha256") == expected, "analysis_input_sha256_mismatch")
        need(type(inputs[role].get("bytes")) is int and inputs[role]["bytes"] > 0,
             "analysis_input_size_invalid")
    need(manifest.get("schema") == "sosym-analysis-files-v1", "manifest_schema_mismatch")
    need(manifest.get("inputs") == inputs, "manifest_inputs_do_not_match_analysis")
    need(manifest.get("new_measurements") is False, "manifest_new_measurements_claim")
    outputs = manifest.get("outputs") or {}
    need(set(outputs) == EXPECTED - {"analysis-manifest.json"}, "manifest_output_set_mismatch")
    for name, record in outputs.items():
        need(record == {"bytes": len(data[name]), "sha256": sha_bytes(data[name])},
             "manifest_member_hash_or_size_mismatch")
    return analysis, manifest


def allowed_metadata_difference(filename, parts):
    if filename == "analysis.json":
        if parts in (("created_utc",), ("execution", "run_id"), ("execution", "source")):
            return True
    if filename in ("analysis.json", "analysis-manifest.json"):
        if len(parts) == 3 and parts[0] == "inputs" and parts[1] in PINS and parts[2] == "path":
            return True
    return (filename == "analysis-manifest.json" and len(parts) == 3
            and parts[:2] == ("outputs", "analysis.json")
            and parts[2] in ("bytes", "sha256"))


def json_differences(old, new, filename, parts=()):
    if type(old) is type(new) and isinstance(old, dict) and set(old) == set(new):
        for key in sorted(old):
            yield from json_differences(old[key], new[key], filename, parts + (key,))
    elif type(old) is type(new) and isinstance(old, list) and len(old) == len(new):
        for number, (left, right) in enumerate(zip(old, new)):
            yield from json_differences(left, right, filename, parts + (number,))
    elif type(old) is not type(new) or old != new:
        yield {
            "file": filename, "path": list(parts),
            "original": old, "reaggregation": new,
            "allowed_execution_or_path_metadata": allowed_metadata_difference(filename, parts),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-zip", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.main_zip, args.work, args.out = (
        value.resolve() for value in (args.main_zip, args.work, args.out)
    )
    destination = args.out / "evidence/reaggregation-comparison"
    destination.mkdir(parents=True, exist_ok=True)
    args.work.mkdir(parents=True, exist_ok=True)
    receipt = {
        "status": "started",
        "reference_artifact": REFERENCE,
        "replay_artifact": REPLAY,
        "comparison_script_sha256": sha_file(Path(__file__)),
        "transport_script_sha256": TRANSPORT_SCRIPT,
        "analysis_script_sha256": ANALYSIS_SCRIPT,
        "five_input_sha256": PINS,
        "current_run": os.environ.get("GITHUB_RUN_ID"),
        "current_source": os.environ.get("GITHUB_SHA"),
        "new_reaggregation_executed": False,
        "new_models_executed": False,
        "new_measurements": False,
    }
    exit_code = 1
    try:
        need(os.environ.get("GITHUB_ACTIONS") == "true", "github_actions_required")
        receipt["cached_main_zip_verified"] = verify_file(args.main_zip, REPLAY)
        budget_path = args.out / "download-budget.json"
        need(budget_path.is_file(), "shared_download_budget_missing")
        helper = transport_module()
        budget = helper.DownloadBudget(budget_path)
        need(budget.value["maximum_archive_response_bytes"] == 6000000000,
             "shared_budget_receipt_limit_mismatch")
        reference_path = destination / "original-analysis.zip"
        if reference_path.exists():
            verify_file(reference_path, REFERENCE)
            receipt["reference_reused"] = True
        else:
            metadata = helper.github_artifact(
                REFERENCE["id"], REFERENCE["bytes"], REFERENCE["sha256"],
                budget, reference_path)
            producer = metadata.get("workflow_run") or {}
            need(metadata.get("name") == REFERENCE["name"], "reference_artifact_name_mismatch")
            need(producer.get("id") == REFERENCE["run_id"], "reference_artifact_producer_run_mismatch")
            need(producer.get("head_sha") == REFERENCE["source"], "reference_artifact_producer_source_mismatch")
            receipt["reference_api_producer"] = producer
            receipt["reference_reused"] = False
        receipt["reference_zip_verified"] = verify_file(reference_path, REFERENCE)
        original, original_locations = read_outputs(reference_path, "analysis-manifest.json")
        replay, replay_locations = read_outputs(
                args.main_zip, "article-reaggregation/analysis-manifest.json")
        verify_outputs(original, REFERENCE)
        verify_outputs(replay, REPLAY)
        receipt["both_output_manifests_verified"] = True
        # Preserve the exact compared member bytes for inspection of every difference.
        replay_path = destination / "reaggregated-analysis.zip"
        need(not replay_path.exists(), "comparison_output_already_exists")
        with zipfile.ZipFile(replay_path, "x", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as archive:
            for name in sorted(replay):
                archive.writestr(name, replay[name])
        receipt["retained_reaggregation_zip"] = {
            "bytes": replay_path.stat().st_size, "sha256": sha_file(replay_path),
            "note": "Derived container; each member is byte-identical to the pinned main artifact.",
        }
        rows, differences = [], []
        for name in sorted(EXPECTED):
            left, right = original[name], replay[name]
            equal = left == right
            rows.append({
                "file": name,
                "original_member": original_locations[name],
                "reaggregation_member": replay_locations[name],
                "original_bytes": len(left),
                "reaggregation_bytes": len(right),
                "original_sha256": sha_bytes(left),
                "reaggregation_sha256": sha_bytes(right),
                "byte_identical": equal,
                "required_byte_identical": name not in ("analysis.json", "analysis-manifest.json"),
            })
            if equal:
                continue
            if name in ("analysis.json", "analysis-manifest.json"):
                structured = list(json_differences(json.loads(left), json.loads(right), name))
                if structured:
                    differences.extend(structured)
                else:
                    differences.append({
                        "file": name, "path": [], "reason": "serialization_only_difference",
                        "allowed_execution_or_path_metadata": False,
                    })
            else:
                patch = "".join(difflib.unified_diff(
                    left.decode("utf-8").splitlines(keepends=True),
                    right.decode("utf-8").splitlines(keepends=True),
                    fromfile="original/" + name, tofile="reaggregation/" + name))
                differences.append({
                    "file": name, "path": [], "unified_diff": patch,
                    "allowed_execution_or_path_metadata": False,
                    "complete_original_and_reaggregation_bytes_retained": True,
                })
        difference_bytes = (json.dumps(differences, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        need(len(difference_bytes) <= MAX_DIFFERENCES, "difference_report_exceeds_bound")
        (destination / "differences.json").write_bytes(difference_bytes)
        with (destination / "file-comparison.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        unexpected = [item for item in differences
                      if not item["allowed_execution_or_path_metadata"]]
        exact_required = all(row["byte_identical"] for row in rows if row["required_byte_identical"])
        matched = exact_required and not unexpected
        receipt.update(
            status="matched" if matched else "differences_found",
            files_compared=len(rows), csv_files_compared=len(CSV_NAMES),
            tex_files_compared=len(TEX_NAMES),
            all_numeric_csv_and_tex_byte_identical=all(
                row["byte_identical"] for row in rows if row["file"] in CSV_NAMES + TEX_NAMES),
            case_provenance_byte_identical=original["case-provenance.json"] == replay["case-provenance.json"],
            approved_metadata_difference_count=len(differences) - len(unexpected),
            unexpected_difference_count=len(unexpected),
            semantic_and_numerical_outputs_equal=matched,
            file_comparisons=rows,
            shared_budget_consumed_bytes=budget.value["consumed_archive_response_bytes"],
        )
        exit_code = 0 if matched else 1
    except Exception as error:
        receipt.update(status="failed", error_type=type(error).__name__)
        if isinstance(error, AuditError):
            receipt["reason"] = str(error)
        # Library exception text may include signed URLs, so it is never recorded.
    finally:
        write_json(destination / "comparison-receipt.json", receipt)
        print(json.dumps({
            "stage": "retained_reaggregation_comparison",
            "status": receipt["status"],
            "unexpected_difference_count": receipt.get("unexpected_difference_count"),
            "new_models_executed": False,
        }), flush=True)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
