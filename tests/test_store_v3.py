"""Focused contracts for the streamed observation index."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ebpf_discovery.store_v3 import ObservationStore, complete_prefix


def otlp_span(span_id, *, trace_id="a" * 32, parent_id="", request_id="req-a", status=200):
    return {
        "traceId": trace_id, "spanId": span_id, "parentSpanId": parent_id,
        "name": "GET /wrk2-api/user-timeline/read", "kind": 2,
        "startTimeUnixNano": "100", "endTimeUnixNano": "200",
        "attributes": [
            {"key": "http.request.method", "value": {"stringValue": "GET"}},
            {"key": "url.path", "value": {"stringValue": "/wrk2-api/user-timeline/read"}},
            {"key": "http.response.status_code", "value": {"intValue": str(status)}},
            {"key": "http.request.header.x-experiment-request-id", "value": {"stringValue": request_id}},
        ],
    }


def batch(*spans, service="nginx-thrift"):
    return {"resourceSpans": [{"resource": {"attributes": [
        {"key": "service.name", "value": {"stringValue": service}},
    ]}, "scopeSpans": [{"spans": list(spans)}]}]}


class StoreTests(unittest.TestCase):
    def test_conflicting_primitive_attributes_are_preserved_and_not_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            obs = root/'obs'
            obs.mkdir()
            raw = otlp_span('1'*16)
            raw['attributes'].append({'key': 'http.response.status_code', 'value': {'intValue': '503'}})
            (obs/'a.jsonl').write_text(json.dumps(batch(raw))+'\n')
            store = ObservationStore(root/'index.sqlite')
            try:
                store.ingest(obs, root/'native')
                row = store.candidates('ebpf', 'req-a')[0]
                self.assertNotIn('http.response.status_code', row['attributes'])
                self.assertEqual(row['attribute_conflicts'][0]['key'], 'http.response.status_code')
                self.assertEqual(len(row['attribute_conflicts'][0]['raw_values']), 2)
                self.assertEqual(store.descendants(row), [])
            finally:
                store.close()

    def test_large_unfinished_tail_keeps_prior_complete_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "a.jsonl"
            complete = b'{"resourceSpans":[]}\n'
            path.write_bytes(complete + b"x" * 70_000)
            self.assertEqual(complete_prefix(path), len(complete))

    def test_complete_jsonl_prefix_and_append_only_tail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            obs, native = root / "obs", root / "native"
            obs.mkdir(); native.mkdir()
            first = json.dumps(batch(otlp_span("1" * 16))).encode() + b"\n"
            second = json.dumps(batch(otlp_span("2" * 16, request_id="req-b"))).encode() + b"\n"
            path = obs / "a.jsonl"
            path.write_bytes(first + second[:-8])
            store = ObservationStore(root / "index.sqlite")
            try:
                result = store.ingest(obs, native)
                self.assertEqual(result["total_unique_observations"], 1)
                self.assertEqual(result["files"][0]["through_byte"], len(first))
                self.assertEqual(store.candidates("ebpf", "req-b"), [])
                with path.open("ab") as stream:
                    stream.write(second[-8:])
                result = store.ingest(obs, native)
                self.assertEqual(result["total_unique_observations"], 2)
                self.assertEqual(result["files"][0]["from_byte"], len(first))
                self.assertEqual(len(store.candidates("ebpf", "req-b")), 1)
                self.assertEqual(store.ingest(obs, native)["files"], [])
            finally:
                store.close()

    def test_equivalent_duplicates_collapsed_conflicting_identities_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            obs, native = root / "obs", root / "native"
            obs.mkdir(); native.mkdir()
            original = otlp_span("1" * 16)
            changed = otlp_span("1" * 16, status=503)
            child = otlp_span("2" * 16, parent_id="1" * 16, request_id="req-child")
            (obs / "a.jsonl").write_text(json.dumps(batch(original, original, changed, child)) + "\n")
            store = ObservationStore(root / "index.sqlite")
            try:
                result = store.ingest(obs, native)
                self.assertEqual(result["total_unique_observations"], 3)
                self.assertEqual(len(store.candidates("ebpf", "req-a")), 2)
                self.assertEqual(len(store.identity("ebpf", "a" * 32, "1" * 16)), 2)
                self.assertEqual(store.descendants(store.candidates("ebpf", "req-a")[0]), [])
            finally:
                store.close()

    def test_native_and_ebpf_same_ids_remain_source_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            obs, native = root / "obs", root / "native"
            obs.mkdir(); native.mkdir()
            (obs / "a.jsonl").write_text(json.dumps(batch(otlp_span("1" * 16))) + "\n")
            native_trace = {"data": [{"traceID": "a" * 32, "spans": [{
                "traceID": "a" * 32, "spanID": "1" * 16, "operationName": "GET /wrk2-api/user-timeline/read",
                "startTime": 1, "duration": 1, "processID": "p1",
                "tags": [{"key": "span.kind", "value": "server"},
                         {"key": "http.request.header.x-experiment-request-id", "value": "req-a"}],
            }], "processes": {"p1": {"serviceName": "nginx-web-server"}}}], "errors": None}
            (native / "traces-nginx-web-server.json").write_text(json.dumps(native_trace))
            store = ObservationStore(root / "index.sqlite")
            try:
                result = store.ingest(obs, native)
                self.assertEqual(result["total_unique_observations"], 2)
                self.assertEqual(len(store.identity("ebpf", "a" * 32, "1" * 16)), 1)
                self.assertEqual(len(store.identity("native", "a" * 32, "1" * 16)), 1)
                self.assertEqual(store.candidates("native", "req-a")[0]["service"], "nginx-web-server")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
