"""Exact header-child proof for a coarse native nginx outer start."""
from __future__ import annotations

from copy import deepcopy
import unittest

from ebpf_discovery.semantic_v3 import Binder, declared_census, transport_observations
from ebpf_discovery.timing_v3 import automatic_census
from ebpf_discovery.observations import opaque_attempt
from tests.test_semantic_v3 import ACK, FakeStore, record, span


def native_pair():
    outer = span(source="native", service="nginx-web-server", start=999_000_000)
    outer["kind"] = None
    outer["end_ns"] = 1_500_000_000
    outer["attributes"]["component"] = "nginx"
    outer["attributes"].pop("http.request.header.x-experiment-request-id")
    child = deepcopy(outer)
    child["span_id"] = "2" * 16
    child["parent_id"] = outer["span_id"]
    child["start_ns"] = 1_100_000_000
    child["end_ns"] = 1_200_000_000
    child["attributes"] = {"component": "lua", "http.request.header.x-experiment-request-id": "req-a"}
    return outer, child


def journal(censored=False):
    attempt = record(success=True, body=ACK.encode(), status=200)
    attempt["started_ns"] = 1_000_000_000
    attempt["ended_ns"] = 2_000_000_000
    attempt["observation"] = {"policy": "censored-v3", "cap_seconds": 10.0,
                              "cutoff_ns": 11_000_000_000, "censored": censored,
                              "termination": "cap_reached" if censored else "complete"}
    return attempt


class NativeAttributionTests(unittest.TestCase):
    def test_valid_child_admits_outer_without_replacing_outer_http_facts(self):
        outer, child = native_pair()
        binder = Binder(FakeStore(outer, child), "deathstarbench")
        row = declared_census([journal()])[0]
        result = binder.source_attempt(row, "native")
        self.assertIs(result["proxy"], True)
        self.assertEqual(result["steps"][0]["status"], 200)
        self.assertEqual(result["steps"][0]["window_binding"], "native_header_child_attribution")
        self.assertEqual(result["steps"][0]["witness"]["span_id"], outer["span_id"])
        proof = result["steps"][0]["header_binding"]["window_attribution"]
        self.assertEqual(proof["outer_raw_start_ns"], 999_000_000)
        self.assertEqual(proof["outer_end_ns"], 1_500_000_000)
        self.assertEqual(proof["header_child_start_ns"], 1_100_000_000)
        self.assertEqual(proof["source_local_parent_path"], [child["span_id"], outer["span_id"]])

    def test_invalid_timing_scope_and_chain_cannot_supply_lower_bound(self):
        cases = {
            "child_after_cutoff": lambda o, c: c.update(start_ns=11_000_000_000, end_ns=11_000_000_001),
            "child_before_journal": lambda o, c: c.update(start_ns=999_500_000),
            "inverted_child": lambda o, c: c.update(start_ns=1_200_000_000, end_ns=1_100_000_000),
            "nonpositive_child": lambda o, c: c.update(start_ns=0),
            "zero_duration_child": lambda o, c: c.update(end_ns=c["start_ns"]),
            "outer_after_cutoff": lambda o, c: o.update(end_ns=11_000_000_001),
            "outer_ends_before_child": lambda o, c: o.update(end_ns=1_150_000_000),
            "inverted_outer": lambda o, c: o.update(end_ns=998_000_000),
            "nonpositive_outer": lambda o, c: o.update(start_ns=0),
            "broken_parent": lambda o, c: c.update(parent_id="f" * 16),
            "foreign_service": lambda o, c: c.update(service="other-service"),
            "foreign_source": lambda o, c: c.update(source="ebpf"),
            "foreign_trace": lambda o, c: c.update(trace_id="b" * 32),
            "foreign_node": lambda o, c: c.update(node="b"),
            "foreign_instance": lambda o, c: c.update(instance="other"),
            "outbound_client_anchor": lambda o, c: c.update(kind="client"),
            "wrong_header": lambda o, c: c["attributes"].update({
                "http.request.header.x-experiment-request-id": "req-other"}),
        }
        row = declared_census([journal()])[0]
        for label, change in cases.items():
            with self.subTest(label=label):
                outer, child = native_pair()
                change(outer, child)
                binder = Binder(FakeStore(outer, child), "deathstarbench")
                self.assertIsNone(binder.source_attempt(row, "native")["proxy"])

    def test_outer_header_alone_and_conflicting_child_identity_do_not_prove_presence(self):
        row = declared_census([journal()])[0]
        outer, child = native_pair()
        outer["attributes"]["http.request.header.x-experiment-request-id"] = "req-a"
        binder = Binder(FakeStore(outer), "deathstarbench")
        self.assertIsNone(binder.source_attempt(row, "native")["proxy"])
        outer, child = native_pair()
        conflict = deepcopy(child)
        conflict["end_ns"] += 1
        binder = Binder(FakeStore(outer, child, conflict), "deathstarbench")
        self.assertIsNone(binder.source_attempt(row, "native")["proxy"])

    def test_multiple_valid_header_children_choose_deterministic_proof(self):
        outer, child = native_pair()
        second = deepcopy(child)
        second["span_id"] = "3" * 16
        second["start_ns"] += 50_000_000
        second["end_ns"] += 50_000_000
        row = declared_census([journal()])[0]
        for order in ((child, second), (second, child)):
            binder = Binder(FakeStore(outer, *order), "deathstarbench")
            result = binder.source_attempt(row, "native")
            self.assertIs(result["proxy"], True)
            proof = result["steps"][0]["header_binding"]["window_attribution"]
            self.assertEqual(proof["header_child_span_id"], child["span_id"])
            self.assertEqual(proof["valid_header_children"], 2)

    def test_censored_attempt_stays_unknown_and_automatic_uses_same_eligibility(self):
        outer, child = native_pair()
        binder = Binder(FakeStore(outer, child), "deathstarbench")
        attempt = journal(censored=True)
        row = declared_census([attempt])[0]
        projected = binder.source_attempt(row, "native")
        self.assertIsNone(projected["proxy"])
        self.assertEqual(projected["steps"][0]["binding"], "unique_declared_entry")
        self.assertEqual(projected["steps"][0]["window_binding"], "native_header_child_attribution")
        self.assertIs(projected["steps"][0]["protocol"], True)
        raw = {"attempt_key": opaque_attempt(attempt), "step_ids": ["req-a"],
               "phase": "class_train", "state": "11"}
        classes, assigned = binder.automatic(automatic_census([attempt], [raw]), "native")
        self.assertEqual(classes, {})
        self.assertEqual(assigned[0]["signature"], ["POST /wrk2-api/post/compose"])
        self.assertIsNone(assigned[0]["proxy"])
        attempt = journal()
        raw["attempt_key"] = opaque_attempt(attempt)
        classes, assigned = binder.automatic(automatic_census([attempt], [raw]), "native")
        self.assertTrue(classes)
        self.assertEqual(assigned[0]["signature"], ["POST /wrk2-api/post/compose"])


if __name__ == "__main__":
    unittest.main()
