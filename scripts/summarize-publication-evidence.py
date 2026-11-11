#!/usr/bin/env python3
"""Print a bounded, read-only summary of completed publication evidence files."""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path
import re

MAX_JSON = 32 * 1024**2
MAX_LOG = 240 * 1024
MAX_OUTPUT = 64 * 1024**2
PREFIX = "PUBLICATION_EVIDENCE_FOLLOWUP_JSON="
TOKEN = os.environ.get("GH_TOKEN", "")
CSV_NAMES = {"required-edges.csv", "context-summary.csv", "context-added-edges.csv", "file-comparison.csv"}

def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()

def clean(value):
    if isinstance(value, str):
        if TOKEN:
            value = value.replace(TOKEN, "[REDACTED_TOKEN]")
        value = re.sub(r"""https?://[^\s<>"']+""", "[REDACTED_URL]", value)
        return re.sub(r"(?:github_pat_|gh[oprsu]_)[A-Za-z0-9_]+", "[REDACTED_TOKEN]", value)
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, dict):
        return {clean(str(k)): clean(v) for k, v in value.items()}
    return value

def compact(value, depth=7, width=30, string=900):
    if isinstance(value, str):
        return value if len(value) <= string else value[:string] + "[...omitted]"
    if not isinstance(value, (dict, list)):
        return value
    if depth <= 0:
        return {"_omitted_type": type(value).__name__, "_items": len(value)}
    if isinstance(value, list):
        result = [compact(v, depth-1, width, string) for v in value[:width]]
        if len(value) > width:
            result.append({"_omitted_items": len(value)-width})
        return result
    result = {str(k): compact(v, depth-1, width, string) for k, v in list(value.items())[:width]}
    if len(value) > width:
        result["_omitted_keys"] = len(value)-width
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.out.resolve()
    if not root.is_dir():
        raise ValueError("output_directory_missing")
    inventory, documents = [], {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(root):
            raise ValueError("output_path_escapes_directory")
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        record = {"member": rel, "bytes": size, "sha256": digest(path)}
        inventory.append(record)
        if len(inventory) > 2000:
            raise ValueError("too_many_output_members")
        chosen_json = path.name.endswith("receipt.json") or path.name.endswith("summary.json")
        chosen_csv = path.name in CSV_NAMES
        if not (chosen_json or chosen_csv):
            continue
        result = dict(record)
        if size > MAX_JSON:
            result["status"] = "not_read_member_exceeds_bound"
        else:
            try:
                if chosen_json:
                    result.update(status="read", content=compact(json.loads(path.read_text(encoding="utf-8"))))
                else:
                    with path.open(encoding="utf-8-sig", newline="") as stream:
                        reader = csv.DictReader(stream)
                        rows = list(itertools.islice(reader, 201))
                        result.update(status="read", columns=reader.fieldnames, rows=rows[:200],
                                      rows_truncated=len(rows) > 200)
            except Exception as error:
                result.update(status="read_failed", error_type=type(error).__name__)
        documents[rel] = result
    total_bytes = sum(v["bytes"] for v in inventory)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write("artifact_size_ok=" + ("true" if total_bytes <= MAX_OUTPUT else "false") + "\n")
    report = clean({
        "status": "evidence_files_inspected",
        "reader_execution": {k: os.environ.get(k) for k in ("GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB")},
        "models_executed_by_summary": False,
        "total_output_bytes": total_bytes,
        "maximum_output_bytes": MAX_OUTPUT,
        "artifact_size_ok": total_bytes <= MAX_OUTPUT,
        "documents": documents,
        "file_inventory": inventory,
    })
    encoded = json.dumps(report, ensure_ascii=True, separators=(",", ":"))
    if len((PREFIX + encoded + "\n").encode("utf-8")) > MAX_LOG:
        report["documents"] = {k: compact(v, depth=5, width=15, string=400) for k, v in report["documents"].items()}
        report["file_inventory"] = report["file_inventory"][:150]
        report["file_inventory_omitted_count"] = max(0, len(inventory)-150)
        encoded = json.dumps(report, ensure_ascii=True, separators=(",", ":"))
    if len((PREFIX + encoded + "\n").encode("utf-8")) > MAX_LOG:
        raise ValueError("summary_exceeds_log_bound")
    print(PREFIX + encoded)
    if total_bytes > MAX_OUTPUT:
        raise SystemExit(2)

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        failure = {"status": "summary_failed", "error_type": type(error).__name__}
        if isinstance(error, ValueError) and re.fullmatch(r"[a-z_]+", str(error)):
            failure["reason"] = str(error)
        print(PREFIX + json.dumps(failure, separators=(",", ":")))
        raise SystemExit(1)
