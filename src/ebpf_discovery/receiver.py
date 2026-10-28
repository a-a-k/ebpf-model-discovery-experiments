"""Separate OTLP HTTP ingress files; provenance comes from the listening port."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock


_CONTENT_HEADERS = ("Content-Type", "Content-Encoding", "Content-Length", "Transfer-Encoding")


def _append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record) + "\n")


def _read_request_body(handler: BaseHTTPRequestHandler) -> bytes:
    transfer_encoding = handler.headers.get("Transfer-Encoding", "").lower().strip()
    if transfer_encoding:
        if transfer_encoding != "chunked":
            raise ValueError(f"unsupported transfer encoding: {transfer_encoding}")
        chunks = []
        while True:
            line = handler.rfile.readline(65537)
            if not line or len(line) > 65536 or not line.endswith(b"\r\n"):
                raise ValueError("invalid chunk-size line")
            size_text = line[:-2].split(b";", 1)[0].strip()
            try:
                size = int(size_text, 16)
            except ValueError as exc:
                raise ValueError("invalid hexadecimal chunk size") from exc
            if size < 0:
                raise ValueError("negative chunk size")
            if size == 0:
                while True:
                    trailer = handler.rfile.readline(65537)
                    if not trailer or len(trailer) > 65536:
                        raise ValueError("invalid chunk trailer")
                    if trailer == b"\r\n":
                        return b"".join(chunks)
            chunk = handler.rfile.read(size)
            if len(chunk) != size or handler.rfile.read(2) != b"\r\n":
                raise ValueError("truncated chunked request body")
            chunks.append(chunk)
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise ValueError("invalid Content-Length") from exc
    if length < 0:
        raise ValueError("negative Content-Length")
    body = handler.rfile.read(length)
    if len(body) != length:
        raise ValueError("truncated request body")
    return body


def _capture_wire_body(
    output: Path,
    wire_body: bytes,
    *,
    source: str,
    node: str,
    received_ns: int,
    headers,
) -> dict:
    """Publish an immutable body and its provenance as one directory rename."""
    digest = hashlib.sha256(wire_body).hexdigest()
    content_type = headers.get("Content-Type", "")
    content_encoding = headers.get("Content-Encoding", "")
    suffix = ".json" if "json" in content_type.lower() else ".pb"
    if content_encoding.lower().strip() == "gzip":
        suffix += ".gz"

    capture_id = f"{received_ns}-{uuid.uuid4().hex}"
    capture_root = output.with_suffix(".raw")
    capture_root.mkdir(parents=True, exist_ok=True)
    final_dir = capture_root / capture_id
    temporary_dir = capture_root / f".{capture_id}.tmp"
    temporary_dir.mkdir()

    body_name = f"body{suffix}"
    (temporary_dir / body_name).write_bytes(wire_body)
    metadata = {
        "source": source,
        "node": node,
        "received_ns": received_ns,
        "content_type": content_type,
        "content_encoding": content_encoding,
        "content_headers": {
            name.lower(): headers.get(name)
            for name in _CONTENT_HEADERS
            if headers.get(name) is not None
        },
        "raw_size_bytes": len(wire_body),
        "raw_sha256": digest,
        "raw_ref": (final_dir / body_name).relative_to(output.parent).as_posix(),
    }
    (temporary_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary_dir, final_dir)
    metadata["raw_metadata_ref"] = (final_dir / "metadata.json").relative_to(output.parent).as_posix()
    return metadata


def create_server(
    port: int,
    output: Path,
    source: str,
    *,
    node: str | None = None,
    raw_capture: bool = False,
) -> ThreadingHTTPServer:
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = Lock()
    capture_node = node or source

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received_ns = time.time_ns()
            capture = None
            try:
                wire_body = _read_request_body(self)
                if raw_capture:
                    with lock:
                        capture = _capture_wire_body(
                            output,
                            wire_body,
                            source=source,
                            node=capture_node,
                            received_ns=received_ns,
                            headers=self.headers,
                        )
                body = wire_body
                if self.headers.get("Content-Encoding", "").lower().strip() == "gzip":
                    body = gzip.decompress(body)
                is_json = "json" in self.headers.get("Content-Type", "").lower()
                if is_json:
                    payload = json.loads(body)
                else:
                    from google.protobuf.json_format import MessageToDict
                    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

                    request = ExportTraceServiceRequest()
                    request.ParseFromString(body)
                    payload = MessageToDict(request)
                record = {
                    "source": source,
                    "received_ns": received_ns,
                    "path": self.path,
                    "id_encoding": "hex" if is_json else "base64",
                    "payload": payload,
                }
                if capture is not None:
                    record.update(capture)
                with lock:
                    _append_jsonl(output, record)
                self.send_response(200)
                self.send_header("Content-Type", "application/json" if is_json else "application/x-protobuf")
                self.end_headers()
                if is_json:
                    self.wfile.write(b"{}")
            except Exception as exc:
                error = {"error": str(exc), "received_ns": received_ns, "path": self.path}
                if capture is not None:
                    error.update(capture)
                with lock:
                    _append_jsonl(output.with_suffix(".errors.jsonl"), error)
                self.send_response(400)
                self.end_headers()

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("0.0.0.0", port), Handler)


def serve(
    port: int,
    output: Path,
    source: str,
    *,
    node: str | None = None,
    raw_capture: bool = False,
):
    create_server(port, output, source, node=node, raw_capture=raw_capture).serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--node")
    parser.add_argument("--raw-capture", action="store_true")
    args = parser.parse_args()
    serve(args.port, args.out, args.source, node=args.node, raw_capture=args.raw_capture)
