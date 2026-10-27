"""Source binding and independent-baseline boundaries for semantic_v3."""

from __future__ import annotations

import base64
import json
from copy import deepcopy
from types import SimpleNamespace
import unittest

from ebpf_discovery.semantic_v3 import Binder, declared_census, transport_observations


ROUTE = "/wrk2-api/post/compose"
ACK = "Successfully upload post"


def span(*, source="ebpf", service="nginx-thrift", path=ROUTE, request_id="req-a",
         span_id="1" * 16, code=200, body=ACK, start=1_100_000_000):
    attributes = {
        "http.request.method": "POST", "url.path": path,
        "http.response.status_code": code,
        "http.request.header.x-experiment-request-id": request_id,
    }
    if body is not None:
        attributes["http.response.body.content"] = body
    return {"source": source, "node": "a" if source == "ebpf" else None,
            "trace_id": "a" * 32, "span_id": span_id, "parent_id": "", "service": service,
            "kind": 2 if source == "ebpf" else "server", "start_ns": start,
            "end_ns": start + 100_000, "attributes": attributes, "status": {}, "raw_file": "raw"}


class FakeStore:
    def __init__(self, *spans):
        self.spans = list(spans)

    def candidates(self, source, request_id):
        return [s for s in self.spans if s["source"] == source and
                s["attributes"].get("http.request.header.x-experiment-request-id") == request_id]

    def identity(self, source, trace, span_id):
        return [s for s in self.spans if (s["source"], s["trace_id"], s["span_id"]) ==
                (source, trace, span_id)]


def record(*, success=False, body=b"wrong", status=200):
    return {"attempt_id": "attempt-a", "operation": "compose_post", "phase": "calibration",
            "state": "11", "started_ns": 1_000_000_000, "ended_ns": 1_200_000_000,
            "deadline_seconds": 2.0, "success": success,
            "validation": {"kind": "external_oracle", "secret": "must not leak"},
            "request_intent": {"steps": [{"request_id": "req-a"}]},
            "http_steps": [{"request_id": "req-a", "status": status,
                            "response_body_base64": base64.b64encode(body).decode()}]}


class SemanticTests(unittest.TestCase):
    def test_native_nginx_selects_outer_untyped_http_boundary(self):
        child = span(source='native', service='nginx-web-server', code=200)
        root = span(source='native', service='nginx-web-server', span_id='2'*16, code=503)
        for event in (child, root):
            event['kind'] = None
            event['attributes']['component'] = 'nginx'
        child['parent_id'] = root['span_id']
        root['attributes'].pop('http.request.header.x-experiment-request-id')
        binder = Binder(FakeStore(child, root), 'deathstarbench')
        selected, reason = binder.entry('native', 'req-a')
        self.assertEqual(selected['span_id'], root['span_id'])
        self.assertIsNone(selected['kind'])
        self.assertEqual(selected['_header_binding']['source_local_parent_path'], [child['span_id'], root['span_id']])
        row = declared_census([record()])[0]
        self.assertIs(binder.source_attempt(row, 'native')['proxy'], False)
        root['start_ns'] = row['ended_ns']+2_000_000_000
        self.assertIsNone(binder.source_attempt(row, 'native')['proxy'])
        root['kind'] = 'client'
        self.assertIsNone(binder.entry('native', 'req-a')[0])
        root['kind'] = None
        second = deepcopy(child)
        second['span_id'], second['parent_id'] = '3'*16, ''
        self.assertIsNone(Binder(FakeStore(child, root, second), 'deathstarbench').entry('native', 'req-a')[0])

    def test_declared_census_excludes_oracle_status_and_response_bytes(self):
        false_record = record(success=False, body=b"wrong", status=503)
        true_record = record(success=True, body=ACK.encode(), status=200)
        self.assertEqual(declared_census([false_record]), declared_census([true_record]))
        census = declared_census([true_record])[0]
        self.assertEqual(census["operation_id"], "compose_post")
        self.assertNotIn("success", census)
        self.assertNotIn("validation", census)
        self.assertNotIn("status", census)
        self.assertNotIn("body", str(census))

    def test_entry_requires_exact_source_service_route_and_unique_identity(self):
        row = declared_census([record()])[0]
        for bad in (span(service="other"), span(path="/api/post/compose"),
                    span(source="native", service="nginx-web-server")):
            result = Binder(FakeStore(bad), "deathstarbench").source_attempt(row, "ebpf")
            self.assertIsNone(result["proxy"])
            self.assertNotEqual(result["steps"][0]["binding"], "unique_declared_entry")
        good = span()
        result = Binder(FakeStore(good), "deathstarbench").source_attempt(row, "ebpf")
        self.assertIs(result["proxy"], True)
        self.assertEqual(result["steps"][0]["binding"], "unique_declared_entry")

    def test_conflicting_entry_identity_and_multiple_entries_are_unknown(self):
        row = declared_census([record()])[0]
        original = span()
        conflict = deepcopy(original)
        conflict["attributes"]["http.response.status_code"] = 503
        result = Binder(FakeStore(original, conflict), "deathstarbench").source_attempt(row, "ebpf")
        self.assertIsNone(result["proxy"])
        self.assertEqual(result["steps"][0]["binding"], "conflicting_entry_identity")
        distinct = span(span_id="2" * 16)
        result = Binder(FakeStore(original, distinct), "deathstarbench").source_attempt(row, "ebpf")
        self.assertIsNone(result["proxy"])
        self.assertEqual(result["steps"][0]["binding"], "multiple_entries")

    def test_body_missing_invalid_or_truncated_stays_unknown(self):
        row = declared_census([record()])[0]
        for body, extra in ((None, {}), (ACK, {"http.response.header.content-length": [999]}),
                            (ACK, {"http.response.body.truncated": True})):
            entry = span(body=body)
            entry["attributes"].update(extra)
            result = Binder(FakeStore(entry), "deathstarbench").source_attempt(row, "ebpf")
            self.assertIsNone(result["proxy"])
        invalid = span(body="other")
        result = Binder(FakeStore(invalid), "deathstarbench").source_attempt(row, "ebpf")
        self.assertIs(result["proxy"], False)

    def test_complete_planned_steps_survive_early_abort(self):
        attempt = record(status=503)
        attempt["request_intent"] = {"steps": [{"request_id": "req-a"}, {"request_id": "req-b"}]}
        row = declared_census([attempt])[0]
        self.assertEqual(row["step_ids"], ["req-a", "req-b"])
        self.assertEqual(row["actual_step_ids"], ["req-a"])
        binder = Binder(FakeStore(span(code=503)), "deathstarbench")
        original = binder.contracts
        binder.contracts = SimpleNamespace(
            CONTRACTS={"compose_post": {"steps": [{"method": "POST", "path": ROUTE},
                                                  {"method": "POST", "path": ROUTE}]}},
            ENTRY_SERVICES=original.ENTRY_SERVICES,
            status_ok=original.status_ok,
            payload_verdict=original.payload_verdict,
        )
        result = binder.source_attempt(row, "ebpf")
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(result["steps"][1]["request_id"], "req-b")
        self.assertIs(result["proxy"], False)

    def test_cheap_http_baseline_uses_status_and_body_not_external_success(self):
        attempt = record(success=False, body=ACK.encode(), status=200)
        row = declared_census([attempt])[0]
        binder = Binder(FakeStore(), "deathstarbench")
        outcome = binder.cheap_attempt(row, transport_observations([attempt]))
        self.assertIs(outcome["proxy"], True)
        self.assertIs(outcome["oracle_fields_consumed"], False)
        attempt["success"] = True
        attempt["validation"]["secret"] = "changed"
        self.assertIs(binder.cheap_attempt(row, transport_observations([attempt]))["proxy"], True)
        attempt["http_steps"][0]["status"] = 503
        self.assertIs(binder.cheap_attempt(row, transport_observations([attempt]))["proxy"], False)

    def test_cheap_http_complete_empty_body_is_a_known_negative(self):
        attempt = record(body=b"", status=200)
        row = declared_census([attempt])[0]
        result = Binder(FakeStore(), "deathstarbench").cheap_attempt(row, transport_observations([attempt]))
        self.assertIs(result["proxy"], False)

    def test_automatic_arm_does_not_require_operation_label(self):
        binder = Binder(FakeStore(span()), "deathstarbench")
        row = {"step_ids": ["req-a"], "phase": "class_train", "state": "11"}
        classes, assignments = binder.automatic([row], "ebpf")
        self.assertTrue(classes)
        self.assertEqual(assignments[0]["signature"], ["POST " + ROUTE])
        self.assertNotIn("operation_id", assignments[0])

    def test_generic_span_error_does_not_override_declared_http_contract(self):
        entry = span()
        entry['status'] = {'code': 'STATUS_CODE_ERROR'}
        row = declared_census([record()])[0]
        result = Binder(FakeStore(entry), 'deathstarbench').source_attempt(row, 'ebpf')
        self.assertIs(result['proxy'], True)

    def test_combination_uses_complementary_facts_and_rejects_conflicts(self):
        row = declared_census([record()])[0]
        ebpf = span(body=None)
        native = span(source='native', service='nginx-web-server')
        del native['attributes']['http.response.status_code']
        binder = Binder(FakeStore(ebpf, native), 'deathstarbench')
        projected = binder.project([row], {})
        self.assertIsNone(projected['ebpf'][0]['proxy'])
        self.assertIsNone(projected['native'][0]['proxy'])
        self.assertIs(projected['combined'][0]['proxy'], True)
        native['attributes']['http.response.status_code'] = 503
        projected = binder.project([row], {})
        self.assertIsNone(projected['combined'][0]['proxy'])
        self.assertTrue(projected['combined'][0]['primitive_conflict'])

    def test_complete_transport_json_uses_original_parser_without_changing_source(self):
        body = b'[{"post_id":"1","text":"wrong","text":"ebpf-study-stable-timeline-fixture-v1"}]'
        attempt = record(body=body)
        attempt['operation'] = 'read_user_timeline'
        row = declared_census([attempt])[0]
        binder = Binder(FakeStore(), 'deathstarbench')
        result = binder.cheap_attempt(row, transport_observations([attempt]))
        self.assertIs(result['proxy'], True)  # original JSON parser retains last key
        self.assertNotIn('complete_transport_body', binder.context)
        self.assertIsNone(binder.contracts.payload_verdict('read_user_timeline', body.decode(), {})['value'])
        attempt['http_steps'][0]['response_body_base64'] = base64.b64encode(b'{').decode()
        self.assertIs(binder.cheap_attempt(row, transport_observations([attempt]))['proxy'], False)
        attempt['http_steps'][0].update(status=None, response_body_base64='', error='connection failed')
        self.assertIsNone(binder.cheap_attempt(row, transport_observations([attempt]))['proxy'])

    def test_create_acknowledgment_uses_same_opaque_identity_for_every_source(self):
        attempt = record(status=201)
        attempt['operation'] = 'create_visit'
        row = declared_census([attempt])[0]
        binder_context = {'fixture': {'unused': 'declaration'}}
        for description, expected in (('ebpf-study-' + row['attempt_key'], None),
                                      ('ebpf-study-' + '0' * 64, False)):
            body = json.dumps({'id': 42, 'petId': 1, 'date': '2026-09-01',
                               'description': description})
            attempt['http_steps'][0]['response_body_base64'] = base64.b64encode(body.encode()).decode()
            events = [span(source=source, service='api-gateway',
                           path='/api/visit/owners/1/pets/1/visits', code=201, body=body)
                      for source in ('ebpf', 'native')]
            binder = Binder(FakeStore(*events), 'petclinic', binder_context)
            projected = binder.project([row], transport_observations([attempt]))
            for source in ('ebpf', 'native', 'combined', 'entry_http'):
                self.assertIs(projected[source][0]['proxy'], expected)
            self.assertEqual(binder.context, binder_context)
            self.assertNotIn('attempt_key', binder.context)


if __name__ == "__main__":
    unittest.main()
