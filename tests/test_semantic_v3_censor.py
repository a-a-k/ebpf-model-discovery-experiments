"""Sealed observation windows cannot turn late or censored evidence into outcomes."""

from __future__ import annotations

import unittest

from ebpf_discovery.semantic_v3 import Binder, SOURCES, declared_census, transport_observations
from ebpf_discovery.timing_v3 import automatic_census, seal_attempt
from ebpf_discovery.observations import opaque_attempt
from tests.test_semantic_v3 import ACK, FakeStore, record, span


def censored_record(*, status=200, body=ACK.encode(), censored=False, ended_ns=4_000_000_000):
    result = record(success=True, body=body, status=status)
    result["started_ns"] = 1_000_000_000
    result["ended_ns"] = ended_ns
    result["observation"] = {"policy": "censored-v3", "cap_seconds": 10.0,
                             "cutoff_ns": 11_000_000_000, "censored": censored,
                             "termination": "cap_reached" if censored else "complete"}
    result["http_steps"][0]["body_completed_ns"] = ended_ns
    return result


class CensoredSemanticTests(unittest.TestCase):
    def test_complete_correct_response_after_two_seconds_is_true_for_every_source(self):
        attempt = censored_record(ended_ns=4_000_000_000)
        ebpf = span()
        ebpf["end_ns"] = 3_500_000_000
        native = span(source="native", service="nginx-web-server")
        native["end_ns"] = 3_500_000_000
        output = Binder(FakeStore(ebpf, native), "deathstarbench").project(
            declared_census([attempt]), transport_observations([attempt]))
        self.assertEqual({source: output[source][0]["proxy"] for source in SOURCES},
                         {source: True for source in SOURCES})
        self.assertIsNone(output["ebpf"][0]["timely"])

    def test_late_span_end_and_late_http_receipt_reject_all_sources(self):
        attempt = censored_record(ended_ns=11_000_000_001)
        seal_attempt(attempt)
        ebpf = span()
        ebpf["end_ns"] = 11_000_000_001
        native = span(source="native", service="nginx-web-server")
        native["end_ns"] = 11_000_000_001
        output = Binder(FakeStore(ebpf, native), "deathstarbench").project(
            declared_census([attempt]), transport_observations([attempt]))
        for source in SOURCES:
            self.assertIsNone(output[source][0]["proxy"], source)
        for source in ("ebpf", "native"):
            self.assertEqual(output[source][0]["steps"][0]["binding"],
                             "entry_outside_sealed_observation_window")
            self.assertIsNone(output[source][0]["steps"][0]["status"])
        self.assertTrue(output["combined"][0]["observation_censored"])
        self.assertIsNone(attempt["success"])

    def test_censored_journal_never_promoted_by_positive_or_negative_payload(self):
        ebpf = span()
        native = span(source="native", service="nginx-web-server")
        binder = Binder(FakeStore(ebpf, native), "deathstarbench")
        for status, body in ((200, ACK.encode()), (500, b"failed")):
            attempt = censored_record(status=status, body=body, censored=True)
            attempt["success"] = None
            ebpf["attributes"]["http.response.status_code"] = status
            native["attributes"]["http.response.status_code"] = status
            ebpf["attributes"]["http.response.body.content"] = body.decode()
            native["attributes"]["http.response.body.content"] = body.decode()
            output = binder.project(declared_census([attempt]), transport_observations([attempt]))
            self.assertTrue(all(output[source][0]["proxy"] is None for source in SOURCES))
            self.assertEqual(output["entry_http"][0]["protocol_only"], status == 200)

    def test_automatic_arm_ignores_semantics_and_late_entry_completion(self):
        attempt = censored_record(censored=True)
        raw = {"attempt_key": opaque_attempt(attempt), "step_ids": ["req-a"],
               "phase": "class_train", "state": "11"}
        census = automatic_census([attempt], [raw])
        ebpf = span()
        ebpf["end_ns"] = 11_000_000_001
        native = span(source="native", service="nginx-web-server")
        native["end_ns"] = 11_000_000_001
        binder = Binder(FakeStore(ebpf, native), "deathstarbench")
        for source in ("ebpf", "native", "combined"):
            classes, assigned = binder.automatic(census, source)
            self.assertEqual(classes, {})
            self.assertEqual(assigned[0]["signature"], [None])
            self.assertIsNone(assigned[0]["proxy"])
            self.assertNotIn("operation_id", assigned[0])


if __name__ == "__main__":
    unittest.main()
