from __future__ import annotations

import gzip
import hashlib
import http.client
import json
import threading
from pathlib import Path

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

from ebpf_discovery.collectors import Collectors
from ebpf_discovery.receiver import create_server


def _post(
    output: Path,
    body: bytes,
    content_type: str,
    *,
    content_encoding: str | None = None,
    raw_capture: bool = True,
):
    server = create_server(0, output, "ebpf:a", node="a", raw_capture=raw_capture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    headers = {"Content-Type": content_type, "Content-Length": str(len(body))}
    if content_encoding is not None:
        headers["Content-Encoding"] = content_encoding
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        connection.request("POST", "/v1/traces", body=body, headers=headers)
        response = connection.getresponse()
        response.read()
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return response.status


def _record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").splitlines()[0])


def _assert_capture(output: Path, record: dict, expected: bytes) -> None:
    raw_path = output.parent / record["raw_ref"]
    metadata_path = output.parent / record["raw_metadata_ref"]
    assert raw_path.read_bytes() == expected
    assert record["raw_sha256"] == hashlib.sha256(expected).hexdigest()
    assert record["raw_size_bytes"] == len(expected)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["raw_ref"] == record["raw_ref"]
    assert metadata["raw_sha256"] == record["raw_sha256"]
    assert metadata["source"] == "ebpf:a"
    assert metadata["node"] == "a"


def test_raw_json_body_is_byte_exact_and_decoded_index_references_it(tmp_path: Path):
    output = tmp_path / "a.jsonl"
    wire = b'{"resourceSpans": [], "spacing": "preserved"}\n'
    assert _post(output, wire, "application/json") == 200
    record = _record(output)
    assert record["payload"]["spacing"] == "preserved"
    assert record["content_headers"]["content-type"] == "application/json"
    _assert_capture(output, record, wire)


def test_receiver_default_retains_legacy_decoded_only_record(tmp_path: Path):
    output = tmp_path / "a.jsonl"
    wire = b'{"resourceSpans": []}'
    assert _post(output, wire, "application/json", raw_capture=False) == 200
    record = _record(output)
    assert set(record) == {"source", "received_ns", "path", "id_encoding", "payload"}
    assert not output.with_suffix(".raw").exists()


def test_raw_protobuf_body_is_byte_exact_without_id_rewriting(tmp_path: Path):
    output = tmp_path / "a.jsonl"
    request = ExportTraceServiceRequest()
    span = request.resource_spans.add().scope_spans.add().spans.add()
    span.trace_id = bytes.fromhex("00112233445566778899aabbccddeeff")
    span.span_id = bytes.fromhex("0102030405060708")
    wire = request.SerializeToString()
    assert _post(output, wire, "application/x-protobuf") == 200
    record = _record(output)
    assert record["id_encoding"] == "base64"
    _assert_capture(output, record, wire)


def test_chunked_protobuf_body_is_not_acknowledged_as_empty(tmp_path: Path):
    output = tmp_path / "a.jsonl"
    request = ExportTraceServiceRequest()
    request.resource_spans.add()
    wire = request.SerializeToString()
    server = create_server(0, output, "ebpf:a", node="a", raw_capture=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        connection.request(
            "POST", "/v1/traces", body=iter([wire[:1], wire[1:]]),
            headers={"Content-Type": "application/x-protobuf"}, encode_chunked=True,
        )
        response = connection.getresponse()
        response.read()
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert response.status == 200
    record = _record(output)
    assert record["raw_size_bytes"] == len(wire) > 0
    assert record["content_headers"]["transfer-encoding"] == "chunked"
    _assert_capture(output, record, wire)


def test_raw_gzip_body_preserves_compressed_wire_bytes(tmp_path: Path):
    output = tmp_path / "a.jsonl"
    decoded = b'{"resourceSpans": [], "compressed": true}'
    wire = gzip.compress(decoded, mtime=123)
    assert _post(output, wire, "application/json", content_encoding="gzip") == 200
    record = _record(output)
    assert record["payload"]["compressed"] is True
    assert record["content_headers"]["content-encoding"] == "gzip"
    _assert_capture(output, record, wire)


def test_decode_failure_still_retains_raw_body_and_provenance(tmp_path: Path):
    output = tmp_path / "a.jsonl"
    wire = b"not-a-valid-export-request"
    assert _post(output, wire, "application/x-protobuf") == 400
    assert not output.exists()
    error = _record(output.with_suffix(".errors.jsonl"))
    assert error["error"]
    _assert_capture(output, error, wire)


def test_collectors_raw_capture_is_explicit_opt_in(tmp_path: Path, monkeypatch):
    commands: list[list[str]] = []

    class Process:
        def __init__(self, command, **_kwargs):
            commands.append(command)

        def poll(self):
            return None

        def terminate(self):
            pass

        def wait(self, timeout):
            assert timeout == 10

    class Result:
        stdout = "true"
        stderr = ""

    class Context:
        out = tmp_path

        def node_put(self, *_args):
            pass

        def node_exec(self, *_args, **_kwargs):
            return Result()

    monkeypatch.setattr("ebpf_discovery.collectors.subprocess.Popen", Process)
    monkeypatch.setattr("ebpf_discovery.collectors.time.sleep", lambda _seconds: None)

    enabled = Collectors(Context(), raw_capture=True)
    enabled.start()
    assert len(commands) == 3
    assert all("--raw-capture" in command for command in commands)
    enabled.close()

    commands.clear()
    disabled = Collectors(Context())
    disabled.start()
    assert len(commands) == 3
    assert all("--raw-capture" not in command for command in commands)
    disabled.close()
