"""The existing compact-report payload hashes, shared by both finalization jobs."""
import argparse
import hashlib
import json
import os
from pathlib import Path


FILES = ("evaluation-v5.json", "status.json", "plans.json", "census.json", "blocks.json",
         "freeze-integrity.json", "toolchain/forecasts.json", "evidence-v4.json", "attempt-journal.jsonl")


def record(root, *, system, mode, seed, collector, stage, run_id, commit, qualification_only=False):
    root = Path(root)
    hashes = {}
    for name in FILES:
        path = root / name
        if path.is_file():
            with path.open("rb") as stream:
                hashes[name] = hashlib.file_digest(stream, "sha256").hexdigest()
        else:
            hashes[name] = None
    full_name = f"campaign-v5-{collector}-{stage}-{system}-{mode}-{seed}-{run_id}"
    if qualification_only:
        full_name = "qualification-" + full_name
    manifest = {
        "schema_version": "v5-cell-summary-manifest", "run_id": run_id, "commit": commit,
        "system": system, "mode": mode, "seed": seed, "collector": collector,
        "smoke": stage == "smoke", "full_artifact_name": full_name, "files_sha256": hashes,
        "full_artifact_transport": "dsb-subtree-retention-v1" if system == "deathstarbench" else "original-file-tree",
        "original_evidence_reverified_by_compact_report": False,
    }
    if qualification_only:
        status = json.loads((root / "status.json").read_text(encoding="utf-8"))
        manifest.update(qualification_only=True, scientific_capture_identity={
            key: status[key] for key in ("run_id", "commit", "system", "collector", "mode", "seed")})
    (root / "evaluation-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("report publication runs in GitHub Actions only")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--system", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--stage", choices=("main", "smoke"), required=True)
    parser.add_argument("--qualification-only", action="store_true")
    args = parser.parse_args()
    record(args.campaign, system=args.system, mode=args.mode, seed=args.seed,
           collector=args.collector, stage=args.stage, run_id=os.environ["GITHUB_RUN_ID"],
           commit=os.environ["GITHUB_SHA"], qualification_only=args.qualification_only)
