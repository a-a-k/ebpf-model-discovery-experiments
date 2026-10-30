"""Retrieve only declared saved evidence members with HTTP range/ZIP proofs.

This is evidence transport.  It never invokes the empirical pipeline.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import threading
import time
import zipfile
import zlib

import requests

try:
    import resource
except ImportError:  # pragma: no cover - Actions qualification is Linux.
    resource = None


COMPACT_FIXED = {
    "blocks.json", "census.json", "classes-v4.json", "classes-v5.json",
    "evaluation-manifest.json", "evaluation-v5.json", "evidence-v4.json",
    "freeze-integrity.json", "plans.json", "status.json", "toolchain/forecasts.json",
}
INPUT_SUPPLEMENT = {
    "toolchain/static-inputs.json",
    *{
        f"toolchain/inputs/{source}/{variant}/observations.json"
        for source in ("ebpf", "native", "combined")
        for variant in ("raw", "network_scope")
    },
}
FULL_FIXED = {
    "infrastructure/infrastructure.json", "infrastructure/image-provenance.json",
    "infrastructure/a/check.txt", "infrastructure/b/check.txt",
    "forecast-saved.json", "toolchain/forecasts.json", "toolchain/static-inputs.json",
    "toolchain/execution-summary.json", "toolchain-build/toolchain-build.json",
    "toolchain/classes/classes-family-model.json", "toolchain/classes/classes-model.json",
    "runtime-identity-v5/supplied-service-aliases-training.json",
    "runtime-identity-v5/supplied-service-alias-admission-training.json",
    "runtime-identity-v5/supplied-alias-scope-final.json",
    "observations/collector.json", "observations/technical-positive-control.json",
    "observations/drain-evidence.json", "observations/receiver-closed-a.json",
    "observations/deepflow-retention-manifest.json",
    "observations/receiver-closed-b.json", "observations/receiver-closed-native.json",
    "infrastructure/training-checkpoint/manifest.json",
    "infrastructure/training-checkpoint/ready.json",
    "infrastructure/training-checkpoint/release.json",
    "infrastructure/remote-toolchain-v4/dispatch.json",
    "infrastructure/remote-toolchain-v4/parent-import.json",
    "infrastructure/remote-toolchain-v4/cost.json",
    "infrastructure/remote-toolchain-v4/training-index-proof.json",
    "infrastructure/remote-toolchain-v4/worker/output-manifest.json",
    "infrastructure/remote-toolchain-v4/worker/worker-provenance.json",
    "infrastructure/remote-toolchain-v4/worker/worker-status.json",
    "retention-layout.json", "toolchain-package/transport.json",
    "toolchain-package/packaging.json", "toolchain-package/payload.manifest.jsonl",
    "toolchain-package/package-status.json", "toolchain-package/payload.tar.gz",
    "infrastructure/handoff-package/transport.json",
    "infrastructure/handoff-package/packaging.json",
    "infrastructure/handoff-package/payload.manifest.jsonl",
    "infrastructure/handoff-package/package-status.json",
    "infrastructure/handoff-package/payload.tar.gz",
    "deployment/petclinic/node-a/compose.yml", "deployment/petclinic/node-b/compose.yml",
    "deployment/otel_demo/native-disable-v5.patch",
    "deployment/otel_demo/runtime-resolved-node-a.yaml",
    "deployment/otel_demo/runtime-resolved-node-b.yaml",
    "deployment/deathstarbench/tracing-mode.json",
    "native/training/manifest.json", "native/final/manifest.json",
    "native/training/native-metadata.json", "native/final/native-metadata.json",
    "native/training/native-suppression-verification.json",
    "native/final/native-suppression-verification.json",
}


def wanted_member(name: str, scope: str) -> bool:
    if scope == "compact":
        return name in COMPACT_FIXED
    if scope == "input-supplement":
        return name in INPUT_SUPPLEMENT
    if scope != "full":
        raise ValueError(f"unknown evidence scope: {scope}")
    if name in FULL_FIXED or name in INPUT_SUPPLEMENT:
        return True
    if name.startswith("observations/deepflow-raw/") and name.endswith("/snapshot.json"):
        return True
    if name.startswith("observations/final-") and name.endswith(("-stop.txt", "-inspect.txt", "-events.txt")):
        return True
    if name.startswith("toolchain/inputs/") and name.endswith("-request-index.jsonl"):
        return True
    parts = name.split("/")
    if name.startswith("toolchain/discovery/"):
        return name.endswith(("observed.json", "observed.snapshot.json",
                              "observed.supplied-aliases.json", "observed.bering-raw.json",
                              "observed.signal-quality.json",
                              "observations.json", "replay-command.json", "bering.log",
                              "accepted-request-sequence.jsonl", "accepted-stream-requests.jsonl"))
    if name.startswith("toolchain/procrustes/") and "/0/" in name:
        return parts[-1] in ("preflight.command.json", "report.json")
    if (len(parts) == 5 and parts[0] == "toolchain"
            and parts[1] in ("ebpf", "native", "combined")
            and parts[2] in ("raw", "network_scope")):
        return parts[-1] in ("binding.json", "forecast.json",
                             "simulation.command.json", "model.json", "overlay.json",
                             "model.signal-quality.json", "provided-metadata-attachment.json",
                             "provided-metadata-validation.command.json")
    return False


def _safe(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name and "\\" not in name and not path.is_absolute() and ".." not in path.parts)


class RemoteZip(io.RawIOBase):
    def __init__(self, metadata: dict, out: Path):
        self.metadata = metadata
        self.size = metadata["size_in_bytes"]
        self.position = 0
        self.session = requests.Session()
        self.url = self._signed_url()
        self.failures: list[dict] = []
        self.verified_received_bytes = 0
        self.attempted_received_bytes = 0
        self._accounting_lock = threading.Lock()
        self.out = out

    def _signed_url(self) -> str:
        token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
        response = self.session.get(
            self.metadata["archive_download_url"],
            headers={"Authorization": "Bearer " + token}, allow_redirects=False,
            timeout=(30, 60))
        del token
        if response.status_code != 302:
            raise ValueError(f"archive redirect HTTP {response.status_code}")
        return response.headers["Location"]

    def readable(self) -> bool: return True
    def seekable(self) -> bool: return True
    def tell(self) -> int: return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        if self.position < 0:
            raise ValueError("negative archive range")
        return self.position

    def _chunk(self, start: int, end: int) -> tuple[int, bytes]:
        expected = end - start + 1
        for attempt in range(4):
            try:
                with requests.get(self.url, headers={"Range": f"bytes={start}-{end}"},
                                  timeout=(30, 60)) as response:
                    body = response.content
                    with self._accounting_lock:
                        self.attempted_received_bytes += len(body)
                    if (response.status_code != 206 or response.headers.get("Content-Range")
                            != f"bytes {start}-{end}/{self.size}"):
                        raise ValueError(f"range response mismatch HTTP {response.status_code}")
                if len(body) != expected:
                    raise ValueError("short range response")
                with self._accounting_lock:
                    self.verified_received_bytes += len(body)
                return start, body
            except (requests.RequestException, ValueError) as error:
                self.failures.append({"offset": start, "bytes": expected,
                                      "attempt": attempt + 1, "error": type(error).__name__})
                if attempt == 3:
                    raise
                self.url = self._signed_url()
        raise AssertionError("unreachable")

    def read(self, length: int = -1) -> bytes:
        length = min(length, self.size - self.position) if length >= 0 else self.size - self.position
        if length <= 0:
            return b""
        start, end = self.position, self.position + length - 1
        starts = iter(range(start, end + 1, 1024 * 1024))
        body = bytearray(length)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            pending = set()
            for _ in range(4):
                value = next(starts, None)
                if value is not None:
                    pending.add(pool.submit(self._chunk, value,
                                            min(end, value + 1024 * 1024 - 1)))
            while pending:
                done, pending = concurrent.futures.wait(
                    pending, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    offset, chunk = future.result()
                    body[offset - start:offset - start + len(chunk)] = chunk
                    value = next(starts, None)
                    if value is not None:
                        pending.add(pool.submit(self._chunk, value,
                                                min(end, value + 1024 * 1024 - 1)))
        self.position += length
        return bytes(body)


def select(metadata: dict, expected: dict, scope: str, out: Path) -> dict:
    identity = {key: metadata.get(key) for key in ("id", "name", "size_in_bytes", "digest")}
    wanted_identity = {key: expected[key] for key in identity}
    workflow = metadata.get("workflow_run") or {}
    if (identity != wanted_identity or metadata.get("expired") is not False
            or workflow.get("id") != expected["run_id"]
            or workflow.get("head_sha") != expected["head_sha"]):
        raise ValueError(f"artifact identity differs from declaration: {identity!r}")
    if out.exists():
        raise ValueError("evidence output already exists")
    out.mkdir(parents=True)
    started = time.monotonic()
    cpu_started = time.process_time()
    remote = RemoteZip(metadata, out)
    proof = {
        "schema_version": "selected-main-review-evidence-v5",
        "artifact": metadata, "scope": scope,
        "method": "exact HTTP206 Content-Range plus selected ZIP CRC/SHA256",
        "whole_archive_sha256_verified": False,
        "scientific_processing_performed": False,
        "complete": False, "files": {}, "range_failures": remote.failures,
    }

    def save() -> None:
        (out / "selected-transport-proof.json").write_text(
            json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    failure = None
    try:
        with zipfile.ZipFile(remote) as archive:
            infos = archive.infolist()
            names = [row.filename for row in infos]
            if len(names) != len(set(names)) or not all(_safe(name) for name in names):
                raise ValueError("duplicate or unsafe ZIP member")
            selected = sorted(name for name in names if wanted_member(name, scope))
            if scope == "compact" and not COMPACT_FIXED.issubset(selected):
                raise ValueError("compact is missing a required selected non-journal member")
            if scope == "input-supplement" and not INPUT_SUPPLEMENT.issubset(selected):
                raise ValueError("full artifact is missing the exact input supplement")

            def fetch(name: str) -> None:
                info = archive.getinfo(name)
                if info.is_dir():
                    raise ValueError(f"selected evidence is a directory: {name}")
                target = out / PurePosixPath(name)
                target.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                size = 0
                with archive.open(info) as source, target.open("wb") as output:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                if size != info.file_size:
                    raise ValueError(f"selected evidence size differs: {name}")
                proof["files"][name] = {
                    "bytes": size, "sha256": digest.hexdigest(),
                    "zip_crc32": f"{info.CRC:08x}", "zip_compressed_bytes": info.compress_size,
                }
                save()

            for name in selected:
                fetch(name)
            if scope == "full":
                control_path = out / "observations/technical-positive-control.json"
                if not control_path.is_file():
                    raise ValueError("full evidence lacks technical-positive-control.json")
                control = json.loads(control_path.read_text(encoding="utf-8"))
                for claim in (control.get("proofs") or {}).values():
                    deepflow = control.get("collector") == "deepflow"
                    if deepflow:
                        name = "observations/" + claim["raw_file"].split("/observations/", 1)[1]
                    else:
                        name = "observations/" + claim["raw_ref"]
                    if not _safe(name):
                        raise ValueError("unsafe raw selected-agent control reference")
                    if name not in proof["files"]:
                        fetch(name)
                    if deepflow:
                        with (out / name).open("rb") as source:
                            source.seek(claim["raw_offset"])
                            body = source.read(claim["raw_length"])
                        if len(body) != claim["raw_length"] or hashlib.sha256(body).hexdigest() != claim["raw_sha256"]:
                            raise ValueError("raw selected-agent control slice differs")
                    elif proof["files"][name]["sha256"] != claim["raw_sha256"]:
                        raise ValueError("raw selected-agent control hash differs")
    except BaseException as exc:
        failure = {"phase": "selected_member_transport",
                   "error_type": type(exc).__name__}
        raise
    finally:
        proof.update({
            "complete": False if failure else proof["complete"],
            "failure": failure,
            "range_verified_received_bytes": remote.verified_received_bytes,
            "range_attempted_received_bytes": remote.attempted_received_bytes,
            "elapsed_seconds": time.monotonic() - started,
            "process_cpu_seconds": time.process_time() - cpu_started,
        })
        save()

    proof.update({
        "complete": True, "selected_member_count": len(proof["files"]),
        "range_verified_received_bytes": remote.verified_received_bytes,
        "range_attempted_received_bytes": remote.attempted_received_bytes,
        "elapsed_seconds": time.monotonic() - started,
        "process_cpu_seconds": time.process_time() - cpu_started,
        "process_max_rss_platform_units": (
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None),
        "process_max_rss_units": "KiB on Linux; platform units otherwise",
        "selected_evidence_bytes_excluding_transport_proof": sum(
            path.stat().st_size for path in out.rglob("*")
            if path.is_file() and path.name != "selected-transport-proof.json"),
        "cost_boundary": "Actions evidence transport only; original campaign and human review costs are separate",
        "human_effort_seconds": None,
    })
    save()
    return proof


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=int, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--scope", choices=("compact", "full", "input-supplement"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repository", default="a-a-k/ebpf-model-discovery-experiments")
    args = parser.parse_args()
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    metadata = json.loads(subprocess.check_output([
        "gh", "api", f"repos/{args.repository}/actions/artifacts/{args.artifact}"
    ]))
    result = select(metadata, expected, args.scope, args.out)
    print(json.dumps({"artifact": args.artifact, "scope": args.scope,
                      "selected": result["selected_member_count"]}))


if __name__ == "__main__":
    main()
