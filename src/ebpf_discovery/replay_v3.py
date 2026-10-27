"""Read-only source-contract replay of three fixed, archived full/seed-0 campaigns.

This is technical development evidence, not a fresh forecast or confirmatory
outcome. Real archived captures are downloaded and processed only in Actions.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import tempfile
import time

from .diagnostics import (ARCHIVES, PROTECTED, REPORT_RUN, REPORT_SHA256,
                          REPORT_TAG, digest, download, extract, read, write)
from .observations import opaque_attempt
from .semantic_v3 import Binder, SOURCES, declared_census, transport_observations
from .store_v3 import ObservationStore

SYSTEMS = ("deathstarbench", "otel_demo", "petclinic")
PHASES = ("class_train", "calibration", "target", "class_test", "db_up", "db_down",
          "async_normal", "async_paused", "async_recovered")


def selected_evidence(report: Path, system: str) -> Path:
    """Select by saved campaign identity, never by its measured accuracy."""
    matches = []
    for status_path in (report / "evidence").glob(f"{system}-*/status.json"):
        status = read(status_path)
        if (status.get("system"), status.get("mode"), status.get("seed")) == (system, "full", 0):
            matches.append(status_path.parent)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one accepted full/seed-0 {system} campaign; found {len(matches)}")
    return matches[0]


def archive_location(status: dict, indexes: dict[str, dict[str, str]]) -> tuple[str, str, str]:
    system = status["system"]
    filename = f"{status['run_id']}-campaign-{system}-full-0-{status['run_id']}.zip"
    found = [(tag, values[filename]) for tag, values in indexes.items() if filename in values]
    if len(found) != 1:
        raise ValueError(f"Expected exactly one checksum-indexed archive for {filename}")
    return found[0][0], filename, found[0][1]


def protected_hashes(evidence: Path, capture: Path) -> dict[str, dict[str, str]]:
    saved = read(evidence / "forecast-saved.json")
    result = {}
    for source in ("ebpf", "native", "combined"):
        hashes = {}
        for name in PROTECTED:
            reference = evidence / "models" / source / name
            original = capture / "models" / source / name
            expected = digest(reference)
            if digest(original) != expected:
                raise ValueError(f"Protected original differs: {source}/{name}")
            hashes[name] = expected
        for name, field in (("model.json", "model_sha256"),
                            ("forecast.json", "sha256"),
                            ("evaluation-map.json", "evaluation_map_sha256")):
            if hashes[name] != saved[field][source]:
                raise ValueError(f"Protected saved forecast hash differs: {source}/{name}")
        result[source] = hashes
    return result


def summarize(projected: dict, reference: dict[str, dict]) -> list[dict]:
    groups = defaultdict(list)
    for source in SOURCES:
        for row in projected[source]:
            original = reference[row["attempt_key"]]
            if original["operation"] != row["operation_id"] or original["phase"] != row["phase"]:
                raise ValueError("Replay reference join changed operation or phase")
            groups[(source, row["phase"], row["operation_id"])].append((row, original.get("success")))
    summary = []
    for (source, phase, operation), selected in sorted(groups.items()):
        source_counts = Counter("true" if row["proxy"] is True else "false" if row["proxy"] is False else "unknown"
                                for row, _ in selected)
        protocol_counts = Counter("true" if row["protocol_only"] is True else "false" if row["protocol_only"] is False else "unknown"
                                  for row, _ in selected)
        comparable = [(row, gold) for row, gold in selected if row["proxy"] is not None and gold is not None]
        summary.append({"source": source, "phase": phase, "operation": operation, "n": len(selected),
                        "source_true": source_counts["true"], "source_false": source_counts["false"],
                        "source_unknown": source_counts["unknown"],
                        "protocol_true": protocol_counts["true"], "protocol_false": protocol_counts["false"],
                        "protocol_unknown": protocol_counts["unknown"],
                        "semantic_protocol_disagree": sum(row["proxy"] != row["protocol_only"]
                                                          for row, _ in selected),
                        "external_true": sum(gold is True for _, gold in selected),
                        "external_false": sum(gold is False for _, gold in selected),
                        "external_unknown": sum(gold is None for _, gold in selected),
                        "comparable": len(comparable),
                        "source_false_positive": sum(row["proxy"] is True and gold is False
                                                     for row, gold in comparable),
                        "source_false_negative": sum(row["proxy"] is False and gold is True
                                                     for row, gold in comparable)})
    return summary


def proof_samples(projected: dict, reference: dict[str, dict], capture: Path) -> list[dict]:
    """At most eight compact source witnesses; never retain response contents."""
    samples = []
    for source in SOURCES:
        for kind in ("known", "unknown"):
            row = next((r for r in projected[source]
                        if (r["proxy"] is not None) == (kind == "known")), None)
            if row is None:
                continue
            original = reference[row["attempt_key"]]
            steps = []
            for step in row.get("steps", []):
                recorded = dict(step)
                witness = recorded.get("witness")
                if witness and witness.get("raw_file"):
                    raw = Path(witness["raw_file"])
                    recorded["witness"] = {**witness, "raw_file": str(raw.relative_to(capture)),
                                           "raw_file_sha256": digest(raw)}
                steps.append(recorded)
            samples.append({"source": source, "selection": kind, "attempt_key": row["attempt_key"],
                            "operation": row["operation_id"], "phase": row["phase"],
                            "source_verdict": row["proxy"], "protocol_only": row["protocol_only"],
                            "external_success": original.get("success"),
                            "body_evidence": row.get("body_evidence"),
                            "step_witnesses": steps})
    return samples


def replay(system: str, output: Path) -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Archived research replay runs in GitHub Actions only")
    started = time.perf_counter()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="replay-v3-") as temp:
        tempdir = Path(temp)
        report_zip = download(REPORT_TAG, f"{REPORT_RUN}-report-{REPORT_RUN}.zip", tempdir)
        if digest(report_zip) != REPORT_SHA256:
            raise ValueError("Pinned original report archive hash mismatch")
        report = tempdir / "report"
        extract(report_zip, report)
        evidence = selected_evidence(report, system)
        status = read(evidence / "status.json")
        indexes = {}
        for tag in ARCHIVES:
            directory = tempdir / tag
            directory.mkdir()
            sums = download(tag, "SHA256SUMS.txt", directory)
            indexes[tag] = {line.split()[1]: line.split()[0]
                            for line in sums.read_text().splitlines() if line.strip()}
        tag, filename, expected_hash = archive_location(status, indexes)
        archive = download(tag, filename, tempdir)
        if digest(archive) != expected_hash:
            raise ValueError("Original campaign archive hash mismatch")
        capture_dir = tempdir / "capture"
        extract(archive, capture_dir)
        roots = list(capture_dir.rglob("external.json"))
        if len(roots) != 1:
            raise ValueError("Expected exactly one original campaign root")
        capture = roots[0].parent
        verified = protected_hashes(evidence, capture)
        records = read(capture / "external.json")
        if (sum(r["phase"] == "calibration" for r in records) != 960 or
                sum(r["phase"] == "target" for r in records) != 960):
            raise ValueError("Unexpected original scored population")
        if any(r["phase"] not in PHASES for r in records):
            raise ValueError("Unexpected original campaign phase")
        context = {}
        if system == "petclinic":
            fixtures = list(capture.glob("deployment/petclinic/fixture.json"))
            if len(fixtures) != 1:
                raise ValueError("Pinned archived Petclinic fixture missing")
            context["fixture"] = read(fixtures[0])
        store = ObservationStore(tempdir / "observation-index.sqlite")
        try:
            index_manifest = store.ingest(capture / "observations", capture / "native")
            rows = declared_census(records)
            projected = Binder(store, system, context).project(rows, transport_observations(records))
            reference = {opaque_attempt(r): r for r in records}
            if len(reference) != len(records) or any(len(projected[s]) != len(records) for s in SOURCES):
                raise ValueError("Replay attempt cardinality mismatch")
            write(output / "summary.json", summarize(projected, reference))
            write(output / "proof-samples.json", proof_samples(projected, reference, capture))
        finally:
            store.close()
        index_manifest["files"] = [{**item, "path": str(Path(item["path"]).relative_to(capture))}
                                   for item in index_manifest["files"]]
        write(output / "index-manifest.json", index_manifest)
        write(output / "provenance.json", {
            "system": system, "mode": "full", "seed": 0, "original_run_id": status["run_id"],
            "original_report_run_id": REPORT_RUN, "original_report_sha256": REPORT_SHA256,
            "archive_release": tag, "archive_filename": filename, "archive_sha256": expected_hash,
            "external_sha256": digest(capture / "external.json"),
            "petclinic_fixture_sha256": digest(fixtures[0]) if system == "petclinic" else None,
            "protected_original_hashes": verified, "protected_hashes_unchanged": True,
            "replay_code_sha": os.environ.get("GITHUB_SHA"), "replay_run_id": os.environ.get("GITHUB_RUN_ID"),
            "records": len(records), "elapsed_seconds_including_downloads": time.perf_counter()-started,
            "legacy_otel_planned_intent_missing": system == "otel_demo",
            "otel_missing_later_steps_remain_unknown_unless_observed_failed_step": True,
            "new_application_attempts": 0, "new_model_fitting": False,
            "replay_is_fresh_confirmation": False, "original_capture_and_models_mutated": False})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", choices=SYSTEMS, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    replay(args.system, args.out / args.system)


if __name__ == "__main__":
    main()
