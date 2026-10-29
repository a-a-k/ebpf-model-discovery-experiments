#!/usr/bin/env python3
"""No-VM engineering qualification for the DeepFlow-derived OTLP handoff."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import time

from ebpf_discovery.bering_v4 import replay
from ebpf_discovery.deepflow_codec_v5 import codec_file
from ebpf_discovery.raw_v4 import export_selection
from ebpf_discovery.toolchain_v5 import PINS


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class _Store:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE files(path TEXT, consumed INTEGER)")
        self.db.execute("INSERT INTO files VALUES (?,?)", (str(path), path.stat().st_size))


def _row(query: str, ordinal: int) -> dict:
    return {
        "signal_source": "EBPF", "tap_side": "ClientProcess",
        "ebpf_type": "TracePoint", "l7_protocol": "MySQL",
        "msg_type": "Request", "start_time": 100 + ordinal,
        "end_time": 110 + ordinal, "request_type": "Query",
        "request_resource": query, "process_id_0": 42,
        "process_kname_0": "client",
    }


def _fixture(root: Path) -> tuple[Path, dict]:
    observations = root / "observations"
    raw = observations / "deepflow-raw" / "node-a" / "001-training" / "l7_flow_log"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"".join(
        json.dumps(_row(query, ordinal), separators=(",", ":")).encode() + b"\n"
        for ordinal, query in enumerate(("SELECT 1", "SELECT 2"))
    ))
    retained = raw.relative_to(observations).as_posix()
    batches, accounting, prefix = codec_file(
        raw, node="a", source_file="a/l7_flow_log", retained_file=retained,
        guest_context={"boot_id": "qualification-boot",
                       "pid_namespace": "pid:[qualification]"},
    )
    if prefix.get("normalized_records") != 2 or len(batches) != 1:
        raise RuntimeError("qualification fixture did not produce two observations")
    for row in accounting:
        row.update(node="a", capture_stage="001-training")
    accounting_path = observations / "deepflow-codec-accounting.jsonl"
    accounting_path.write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in accounting),
        encoding="utf-8",
    )
    snapshot = {"files": [{
        "snapshot_name": raw.name, "copied_bytes": raw.stat().st_size,
        "copied_sha256": _sha(raw),
    }]}
    _write(raw.parent / "snapshot.json", snapshot)
    wrapper = observations / "a.jsonl"
    wrapper.write_text(json.dumps(batches[0], separators=(",", ":")) + "\n",
                       encoding="utf-8")
    manifest = export_selection(
        _Store(wrapper), {"ebpf": None}, root / "frozen-export",
    )
    _write(root / "frozen-export" / "observations.json", manifest)
    return root / "frozen-export" / "observations.json", manifest


def _preflight_fixture(root: Path) -> tuple[Path, Path]:
    source = root / "procrustes-source"
    source.mkdir(parents=True)
    (source / "deployment.yaml").write_text("""apiVersion: apps/v1
kind: Deployment
metadata: {name: reader, namespace: default}
spec:
  replicas: 1
  selector: {matchLabels: {app: reader}}
  template:
    metadata: {labels: {app: reader}}
    spec:
      containers: [{name: reader, image: example.invalid/reader:qualification}]
---
apiVersion: v1
kind: Service
metadata: {name: reader, namespace: default}
spec: {selector: {app: reader}, ports: [{port: 80}]}
""", encoding="utf-8")
    (source / "scenario.yaml").write_text("""type: Test
spec:
  id: read-items
  trigger: {type: http, httpRequest: {method: GET, url: http://reader/items}}
""", encoding="utf-8")
    goal = root / "goal.yaml"
    goal.write_text("""scope:
  namespaces: [default]
  services: [reader]
operation:
  id: read-items
  entry_service: reader
  method: GET
  path: /items
  mandatory_targets: [reader]
""", encoding="utf-8")
    return source, goal


def _binary_proof(build: Path, name: str) -> dict:
    manifest = json.loads((build / "toolchain-build.json").read_text(encoding="utf-8"))
    matches = [row for row in manifest.get("binaries", []) if row.get("name") == name]
    binary = build / "bin" / name
    if (len(matches) != 1 or matches[0].get("commit") != PINS[name.capitalize()]
            or matches[0].get("binary_sha256") != _sha(binary)
            or matches[0].get("binary_bytes") != binary.stat().st_size):
        raise RuntimeError(f"pinned {name} binary proof failed")
    return {**matches[0], "actual_path": str(binary.resolve())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--toolchain-build", type=Path, required=True)
    args = parser.parse_args()
    root, build = args.out.resolve(), args.toolchain_build.resolve()
    root.mkdir(parents=True, exist_ok=False)
    started = time.time_ns()
    binaries = {name: _binary_proof(build, name) for name in ("procrustes", "bering")}
    input_path, manifest = _fixture(root)

    source, goal = _preflight_fixture(root)
    preflight = root / "procrustes"
    argv = [binaries["procrustes"]["actual_path"], "analyze", "--source",
            f"deployment={source}", "--goal", str(goal), "--out-dir", str(preflight),
            "--collection-source", "ebpf-otlp", "--source-domain", "qualification"]
    preflight_started = time.time_ns()
    completed = subprocess.run(argv, text=True, capture_output=True, check=False)
    preflight_ended = time.time_ns()
    (root / "procrustes.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (root / "procrustes.stderr.log").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"Procrustes technical command failure: {completed.returncode}")
    plan = json.loads((preflight / "collection-plan.json").read_text(encoding="utf-8"))
    sources = plan.get("trace_sources") or []
    if (len(sources) != 1 or sources[0].get("system") != "ebpf-otlp"
            or sources[0].get("bering_input") != "ebpf-otlp"
            or sources[0].get("domain") != "qualification"):
        raise RuntimeError("Procrustes did not retain the generic eBPF OTLP handoff")

    bering_started = time.time_ns()
    model, quality = replay(
        Path(binaries["bering"]["actual_path"]), manifest, root / "bering",
        "qualification", publication_mode="on_shutdown",
        source_profile={"source_id": "ebpf", "input_type": "ebpf-otlp"},
    )
    bering_ended = time.time_ns()
    replay_path = root / "bering" / "model-runtime" / "replay-command.json"
    replay_evidence = json.loads(replay_path.read_text(encoding="utf-8"))
    accepted = replay_evidence.get("accepted_ingest_requests") or []
    export = manifest["exports"][0]
    ingest = replay_evidence.get("ingest") or {}
    if (replay_evidence.get("status") != "complete"
            or ingest.get("spans") != 2 or ingest.get("dropped_spans") != 0
            or len(accepted) != 1 or accepted[0].get("http_status") != 200
            or accepted[0].get("content_bytes") != Path(export["path"]).stat().st_size
            or accepted[0].get("content_sha256") != export["sha256"]):
        raise RuntimeError("Bering did not retain exact successful fixture ingest evidence")
    _write(root / "bering-model-uninterpreted.json", model)
    _write(root / "bering-signal-quality-uninterpreted.json", quality)
    ended = time.time_ns()
    _write(root / "qualification.json", {
        "schema_version": "deepflow-derived-handoff-qualification-v5",
        "kind": "engineering_fixture_not_empirical_measurement",
        "status": "technical_complete",
        "input_manifest": str(input_path),
        "input_observations": manifest["observations"],
        "source_representation": manifest["exports"][0]["source_representation"],
        "original_agent_wire": manifest["exports"][0]["original_agent_wire"],
        "binaries": binaries,
        "procrustes": {
            "argv": argv, "returncode": completed.returncode,
            "goal_status": json.loads((preflight / "report.json").read_text()).get(
                "goal_status"),
            "favorable_status_required": False,
            "started_ns": preflight_started, "ended_ns": preflight_ended,
        },
        "bering": {
            "profile": {"source_id": "ebpf", "input_type": "ebpf-otlp"},
            "favorable_graph_shape_required": False,
            "graph_interpreted": False,
            "replay_evidence": str(replay_path),
            "replay_evidence_sha256": _sha(replay_path),
            "accepted_ingest_requests": accepted,
            "started_ns": bering_started, "ended_ns": bering_ended,
        },
        "sheaft_executed": False,
        "refit_rescore_or_external_outcomes_used": False,
        "started_ns": started, "ended_ns": ended,
    })
    census = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()
                       and item.name != "evidence-census.json"):
        census.append({"path": path.relative_to(root).as_posix(),
                       "bytes": path.stat().st_size, "sha256": _sha(path)})
    _write(root / "evidence-census.json", census)


if __name__ == "__main__":
    main()
