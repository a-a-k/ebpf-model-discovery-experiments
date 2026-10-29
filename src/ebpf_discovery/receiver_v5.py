"""Gracefully closable raw OTLP receiver for iteration 5.

SIGTERM stops acceptance, joins every in-flight request handler, closes the
listening socket, and only then writes a hash checkpoint.  This proves closure
of saved receiver bytes; it makes no claim about telemetry never produced by a
collector or lost before reaching the receiver.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import signal
import threading
import time
from pathlib import Path

from .receiver import create_server


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _file(path: Path) -> dict:
    if not path.exists():
        return {"present": False, "bytes": 0, "sha256": None, "complete_jsonl": True}
    size = path.stat().st_size
    with path.open("rb") as stream:
        if size:
            stream.seek(-1, 2)
            complete = stream.read(1) == b"\n"
        else:
            complete = True
    return {
        "present": True,
        "bytes": size,
        "sha256": _sha256(path),
        "complete_jsonl": complete,
    }


def _raw_capture_audit(output: Path) -> dict:
    root = output.with_suffix(".raw")
    captures, errors = [], []
    if root.exists():
        capture_directories = sorted(path for path in root.iterdir() if path.is_dir())
        for capture_directory in capture_directories:
            metadata_path = capture_directory / "metadata.json"
            if capture_directory.name.startswith(".") or not metadata_path.is_file():
                errors.append(f"incomplete raw capture directory: {capture_directory}")
                continue
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                raw_ref = metadata.get("raw_ref")
                body = output.parent / raw_ref if isinstance(raw_ref, str) else None
                actual = _sha256(body) if body is not None and body.is_file() else None
                actual_size = body.stat().st_size if body is not None and body.is_file() else None
                valid = (
                    actual is not None
                    and actual == metadata.get("raw_sha256")
                    and actual_size == metadata.get("raw_size_bytes")
                )
                captures.append(
                    {
                        "metadata": metadata_path.relative_to(output.parent).as_posix(),
                        "metadata_sha256": _sha256(metadata_path),
                        "raw_ref": raw_ref,
                        "raw_sha256": actual,
                        "raw_size_bytes": actual_size,
                        "valid": valid,
                    }
                )
                if not valid:
                    errors.append(f"raw capture hash mismatch: {metadata_path}")
            except Exception as exc:  # retained corruption is technical evidence
                errors.append(f"raw capture metadata unreadable: {metadata_path}: {exc}")
    return {"captures": captures, "capture_count": len(captures), "errors": errors}


def serve(port: int, output: Path, source: str, *, node: str, checkpoint: Path) -> None:
    server = create_server(port, output, source, node=node, raw_capture=True)
    # ThreadingHTTPServer defaults to daemon request threads.  Override that so
    # server_close joins them before the saved-byte checkpoint is calculated.
    server.daemon_threads = False
    server.block_on_close = True
    stopping = threading.Event()

    def stop(_signum, _frame):
        if stopping.is_set():
            return
        stopping.set()
        # BaseServer.shutdown must run outside the serve_forever thread.
        threading.Thread(target=server.shutdown, name="receiver-v5-shutdown").start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    started_ns = time.time_ns()
    try:
        server.serve_forever()
    finally:
        server.server_close()
        wrapper = _file(output)
        errors_file = _file(output.with_suffix(".errors.jsonl"))
        raw = _raw_capture_audit(output)
        valid = (
            wrapper["complete_jsonl"]
            and errors_file["complete_jsonl"]
            and not raw["errors"]
        )
        checkpoint.write_text(
            json.dumps(
                {
                    "schema": "receiver-closed-checkpoint-v5",
                    "source": source,
                    "node": node,
                    "started_ns": started_ns,
                    "closed_ns": time.time_ns(),
                    "in_flight_handlers_joined": True,
                    "listening_socket_closed": True,
                    "wrapper": wrapper,
                    "errors": errors_file,
                    "raw_capture": raw,
                    "saved_bytes_valid": valid,
                    "scope": (
                        "complete saved receiver bytes only; kernel, producer, and "
                        "collector-exporter loss are not proven absent"
                    ),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--node", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    serve(args.port, args.out, args.source, node=args.node, checkpoint=args.checkpoint)
