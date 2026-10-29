"""Compare old and streamed DeepFlow checkpoint dependencies on saved evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time
import traceback
import zipfile


RUN_ID = 40936796228
ARTIFACT_ID = 12923969985
ARTIFACT_DIGEST = "sha256:efb51e5e3cdced6c8f2e7334aa39b50255216565a4129501564b2b772e4e649e"
ORIGINAL_COMMIT = "f6cb591a9bd93bd9cf1e9e75ac5eb241dc1c312d"
SOURCE_FILE = "src/ebpf_discovery/checkpoint_v4.py"


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def _safe(entry: zipfile.ZipInfo) -> bool:
    path = Path(entry.filename)
    mode = (entry.external_attr >> 16) & 0xFFFF
    return (not path.is_absolute() and ".." not in path.parts
            and not stat.S_ISLNK(mode))


def _extract(archive: Path, destination: Path) -> tuple[Path, dict]:
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len({entry.filename for entry in entries}) != len(entries):
            raise ValueError("artifact ZIP contains duplicate names")
        if not all(_safe(entry) for entry in entries if not entry.is_dir()):
            raise ValueError("artifact ZIP contains unsafe names")
        bundle.extractall(destination)
    manifests = list(destination.rglob("manifest.json"))
    if len(manifests) != 1:
        raise ValueError("saved checkpoint artifact must contain one manifest")
    root = manifests[0].parent
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    for relative, proof in manifest.get("files", {}).items():
        path = root / relative
        if (not path.is_file() or path.stat().st_size != proof.get("bytes")
                or _sha(path) != proof.get("sha256")):
            raise ValueError(f"saved checkpoint member differs from manifest: {relative}")
    return root, {"files_verified": len(manifest.get("files", {})),
                  "manifest_bytes": manifests[0].stat().st_size,
                  "manifest_sha256": _sha(manifests[0])}


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location("ebpf_discovery." + name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load checkpoint source: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _peak_rss_kib() -> int | None:
    try:
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (ImportError, AttributeError):
        return None


def _worker(args) -> None:
    started = time.monotonic()
    module = (_load(args.original_source, "_saved_checkpoint_accounting_old")
              if args.variant == "original" else
              _load(Path(SOURCE_FILE), "_saved_checkpoint_accounting_current"))
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(args.checkpoint / "observation-index.sqlite",
                 output / "observation-index.sqlite")
    copied = {}
    records = module._runtime_observation_dependencies(
        args.checkpoint.resolve(), output, copied)
    files = []
    for relative in sorted(copied):
        path = output / relative
        files.append({"path": relative, "bytes": path.stat().st_size, "sha256": _sha(path)})
    report = {"variant": args.variant, "records": records, "copied": copied, "files": files,
              "elapsed_seconds": time.monotonic() - started, "peak_rss_kib": _peak_rss_kib()}
    _write(output / "worker-report.json", report)


def _invoke(script: Path, variant: str, checkpoint: Path, old: Path, out: Path) -> dict:
    command = [sys.executable, str(script), "--worker", "--variant", variant,
               "--checkpoint", str(checkpoint), "--original-source", str(old),
               "--out", str(out)]
    completed = subprocess.run(command, text=True, capture_output=True)
    _write(out.parent / f"{variant}-invocation.json", {
        "argv": command, "returncode": completed.returncode,
        "stdout": completed.stdout, "stderr": completed.stderr})
    if completed.returncode:
        raise RuntimeError(f"{variant} checkpoint dependency worker failed")
    return json.loads((out / "worker-report.json").read_text(encoding="utf-8"))


def validate(args) -> dict:
    started = time.monotonic()
    artifact = json.loads(args.artifact_metadata.read_text(encoding="utf-8"))
    run = json.loads(args.run_metadata.read_text(encoding="utf-8"))
    digest = "sha256:" + _sha(args.archive)
    if (artifact.get("id") != ARTIFACT_ID or artifact.get("digest") != ARTIFACT_DIGEST
            or digest != ARTIFACT_DIGEST or run.get("id") != RUN_ID
            or run.get("head_sha") != ORIGINAL_COMMIT):
        raise ValueError("saved artifact/run identity differs from pinned validation source")
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    checkpoint, checkpoint_proof = _extract(args.archive, root / "saved-checkpoint")
    old_source = root / "source-original.py"
    old_source.write_bytes(subprocess.run(
        ["git", "show", f"{ORIGINAL_COMMIT}:{SOURCE_FILE}"], check=True,
        stdout=subprocess.PIPE).stdout)
    original = _invoke(Path(__file__).resolve(), "original", checkpoint, old_source,
                       root / "original")
    current = _invoke(Path(__file__).resolve(), "current", checkpoint, old_source,
                      root / "current")
    for field in ("records", "copied", "files"):
        if _canonical(original[field]) != _canonical(current[field]):
            raise ValueError(f"old/current DeepFlow checkpoint {field} differ")
    result = {
        "schema": "deepflow-checkpoint-accounting-equivalence-v5",
        "scope": ("saved DeepFlow training-prefix checkpoint dependency/copy equivalence only; "
                  "no workload, discovery, fit, forecast, score, or outcome processing"),
        "source": {"run_id": RUN_ID, "artifact_id": ARTIFACT_ID,
                   "artifact_digest": ARTIFACT_DIGEST,
                   "artifact_name": artifact.get("name"), "head_sha": ORIGINAL_COMMIT,
                   "checkpoint": checkpoint_proof},
        "implementations": {
            "original": {"commit": ORIGINAL_COMMIT, "path": SOURCE_FILE,
                         "bytes": old_source.stat().st_size, "sha256": _sha(old_source)},
            "current": {"github_sha": os.environ.get("GITHUB_SHA"), "path": SOURCE_FILE,
                        "bytes": Path(SOURCE_FILE).stat().st_size,
                        "sha256": _sha(Path(SOURCE_FILE))}},
        "comparison": {"dependency_records_identical": True,
                       "copied_manifest_records_identical": True,
                       "all_copied_file_bytes_and_hashes_identical": True,
                       "dependency_records": len(original["records"]),
                       "copied_files": len(original["files"])},
        "costs": {"elapsed_seconds": time.monotonic() - started,
                  "original_worker_elapsed_seconds": original["elapsed_seconds"],
                  "current_worker_elapsed_seconds": current["elapsed_seconds"],
                  "original_worker_peak_rss_kib": original["peak_rss_kib"],
                  "current_worker_peak_rss_kib": current["peak_rss_kib"],
                  "source_campaign_cost_reused_not_zero": True,
                  "memory_or_time_improvement_claimed": False},
        "equivalent": True,
    }
    _write(root / "validation.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--artifact-metadata", type=Path)
    parser.add_argument("--run-metadata", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--variant", choices=("original", "current"))
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--original-source", type=Path)
    args = parser.parse_args()
    try:
        if args.worker:
            if not all((args.variant, args.checkpoint, args.original_source)):
                parser.error("worker mode requires variant, checkpoint, and original source")
            _worker(args)
        else:
            if not all((args.archive, args.artifact_metadata, args.run_metadata)):
                parser.error("validation mode requires archive and API metadata")
            validate(args)
    except BaseException as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        _write(args.out / "failure.json", {"error": f"{type(exc).__name__}: {exc}",
                                            "traceback": traceback.format_exc()})
        raise


if __name__ == "__main__":
    main()
