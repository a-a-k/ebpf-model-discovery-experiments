"""Adjudicate one immutable DSB acquisition check without replaying results."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
from typing import Callable
import zipfile

from ebpf_discovery import evaluate_v5
from systems.deathstarbench import experiment_v4 as declaration


REPOSITORY = "a-a-k/ebpf-model-discovery-experiments"
RUN_ID = 40909279346
HEAD_SHA = "33d98e2ba522af1b740ec4465dc6ba6e7b3e0530"
ARTIFACT_ID = 12913642774
ARTIFACT_NAME = "campaign-v5-obi-smoke-deathstarbench-absent-6-40909279346"
ARTIFACT_DIGEST = "sha256:5ebb00ea990594ee00ea5c2070bd4cf4d1f3e8b8c651d8483702cd1f44d70bdb"
ARTIFACT_SIZE = 29877697
MEMBERS = (
    "evaluation-v5.json",
    "evaluation-manifest.json",
    "status.json",
    "observation-index.sqlite",
    "observations/collector.json",
    "observations/drain-evidence.json",
    "observations/technical-positive-control.json",
)
OLD_SOLE_PROBLEM = "native_observations_present_in_absent_mode"


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _safe_member(member: zipfile.ZipInfo) -> bool:
    name = member.filename
    parts = PurePosixPath(name).parts
    return bool(name and "\\" not in name and not PurePosixPath(name).is_absolute()
                and ".." not in parts and not stat.S_ISLNK(member.external_attr >> 16))


def _verify_source(archive: Path, artifact: dict, run: dict) -> dict:
    expected_artifact = {
        "id": ARTIFACT_ID, "name": ARTIFACT_NAME,
        "size_in_bytes": ARTIFACT_SIZE, "digest": ARTIFACT_DIGEST,
        "expired": False,
    }
    actual_artifact = {key: artifact.get(key) for key in expected_artifact}
    if actual_artifact != expected_artifact:
        raise ValueError(f"artifact API identity mismatch: {actual_artifact!r}")
    workflow_run = artifact.get("workflow_run") or {}
    if (workflow_run.get("id") != RUN_ID or workflow_run.get("head_sha") != HEAD_SHA
            or run.get("id") != RUN_ID or run.get("head_sha") != HEAD_SHA
            or run.get("repository", {}).get("full_name") != REPOSITORY):
        raise ValueError("workflow run API identity mismatch")
    received_size = archive.stat().st_size
    received_digest = "sha256:" + _sha256(archive)
    if received_size != ARTIFACT_SIZE or received_digest != ARTIFACT_DIGEST:
        raise ValueError("downloaded full artifact differs from the API size or digest")
    return {
        "repository": REPOSITORY, "run_id": RUN_ID, "head_sha": HEAD_SHA,
        "artifact_id": ARTIFACT_ID, "artifact_name": ARTIFACT_NAME,
        "api_digest": ARTIFACT_DIGEST, "computed_digest": received_digest,
        "api_size_in_bytes": ARTIFACT_SIZE, "received_bytes": received_size,
    }


def _extract_exact(archive: Path, destination: Path) -> list[dict]:
    destination.mkdir(parents=True, exist_ok=False)
    proofs = []
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries):
            raise ValueError("full artifact contains duplicate member names")
        if not all(_safe_member(entry) for entry in entries):
            raise ValueError("full artifact contains an unsafe member")
        by_name = {entry.filename: entry for entry in entries}
        for name in MEMBERS:
            entry = by_name.get(name)
            if entry is None or entry.is_dir():
                raise ValueError(f"required original member is missing: {name}")
            raw = bundle.read(entry)  # zipfile verifies CRC while reading.
            target = destination / PurePosixPath(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            proofs.append({
                "path": name, "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "zip_crc32": f"{entry.CRC:08x}",
                "zip_compressed_bytes": entry.compress_size,
            })
    return proofs


def adjudicate(
    archive: Path,
    artifact_metadata: Path,
    run_metadata: Path,
    out: Path,
    acquisition_fn: Callable = evaluate_v5.acquisition_checks,
) -> dict:
    if out.exists():
        raise ValueError("output directory already exists")
    out.mkdir(parents=True)
    source = _verify_source(archive, _json(artifact_metadata), _json(run_metadata))
    original = out / "original"
    members = _extract_exact(archive, original)

    manifest = _json(original / "evaluation-manifest.json")
    if (manifest.get("run_id") != str(RUN_ID) or manifest.get("commit") != HEAD_SHA
            or manifest.get("full_artifact_name") != ARTIFACT_NAME):
        raise ValueError("saved evaluation manifest differs from fixed source")
    manifest_hashes = manifest.get("files_sha256") or {}
    for name in ("evaluation-v5.json", "status.json"):
        expected = manifest_hashes.get(name)
        actual = _sha256(original / name)
        if expected != actual:
            raise ValueError(f"saved manifest hash mismatch: {name}")

    old_evaluation = _json(original / "evaluation-v5.json")
    old_acquisition = old_evaluation.get("acquisition") or {}
    if old_acquisition.get("problems") != [OLD_SOLE_PROBLEM]:
        raise ValueError("old evaluation does not have the fixed sole acquisition problem")
    status = _json(original / "status.json")
    if (status.get("system"), status.get("mode"), status.get("seed"),
            status.get("collector"), status.get("smoke")) != (
            "deathstarbench", "absent", 6, "obi", True):
        raise ValueError("saved status differs from the fixed DSB smoke cell")

    new_acquisition = acquisition_fn(original, status, declaration)
    adjudicator_sha = os.environ.get("GITHUB_SHA", "")
    adjudicator_run_id = os.environ.get("GITHUB_RUN_ID", "")
    if (len(adjudicator_sha) != 40
            or any(character not in "0123456789abcdef" for character in adjudicator_sha)
            or not adjudicator_run_id.isdigit()):
        raise ValueError("adjudicator GitHub revision/run provenance is missing or invalid")
    adjudicator = {
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "run_id": adjudicator_run_id,
        "head_sha": adjudicator_sha,
        "sources_sha256": {
            "scripts/adjudicate-dsb-native-v5.py": _sha256(Path(__file__)),
            "src/ebpf_discovery/evaluate_v5.py": _sha256(Path(evaluate_v5.__file__)),
            "systems/deathstarbench/experiment_v4.py": _sha256(Path(declaration.__file__)),
        },
    }
    report = {
        "schema_version": "dsb-native-acquisition-adjudication-v5",
        "scope": "acquisition_checks_only",
        "source": source,
        "adjudicator": adjudicator,
        "members": members,
        "old_evaluation": old_evaluation,
        "old_acquisition": old_acquisition,
        "new_acquisition": new_acquisition,
        "selected_original_members_preserved": True,
        "source_full_artifact_unchanged": True,
        "source_full_artifact_retained_in_output": False,
        "original_evaluation_overwritten": False,
        "model_refit_or_replay_performed": False,
        "sheaft_or_forecast_recomputation_performed": False,
        "acquisition_validation_counts_recomputed": True,
        "forecast_class_outcome_metrics_recomputed": False,
    }
    (out / "adjudication.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(artifact_metadata, out / "artifact-api.json")
    shutil.copy2(run_metadata, out / "run-api.json")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--artifact-metadata", type=Path, required=True)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = adjudicate(args.archive, args.artifact_metadata, args.run_metadata, args.out)
    if report["new_acquisition"].get("valid") is not True:
        raise SystemExit("adjudicated acquisition checks remain invalid")


if __name__ == "__main__":
    main()
