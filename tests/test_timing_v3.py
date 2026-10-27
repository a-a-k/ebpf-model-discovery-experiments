"""Observation cap accounting is separate from business success and SLOs."""

from __future__ import annotations

from copy import deepcopy
import unittest

from ebpf_discovery.observations import opaque_attempt
from ebpf_discovery.timing_v3 import automatic_census, http_curves, seal_attempt


def attempt(*, name="compose_post", status=200, success=True, completed_ns=4_000_000_000,
            censored=False, request_id="req-a"):
    return {"attempt_id": request_id, "operation": name, "phase": "target", "state": "11",
            "started_ns": 1_000_000_000, "ended_ns": completed_ns,
            "success": success, "http_steps": [{"request_id": request_id, "status": status,
                "ended_ns": completed_ns, "body_completed_ns": completed_ns}],
            "observation": {"policy": "censored-v3", "cap_seconds": 10.0,
                            "cutoff_ns": 11_000_000_000, "censored": censored,
                            "termination": "cap_reached" if censored else "complete"}}


class TimingTests(unittest.TestCase):
    def test_late_complete_response_is_sealed_unknown_despite_raw_success(self):
        record = attempt(completed_ns=11_000_000_001, success=True)
        returned = seal_attempt(record)
        self.assertIs(returned, record)
        self.assertIsNone(record["success"])
        self.assertTrue(record["observation"]["censored"])
        self.assertEqual(record["observation"]["termination"], "cap_reached")
        self.assertTrue(record["observation"]["late_completed_response_retained"])
        self.assertEqual(record["http_steps"][0]["status"], 200)
        self.assertEqual(record["http_steps"][0]["body_completed_ns"], 11_000_000_001)

    def test_on_time_complete_response_stays_success_without_two_second_slo(self):
        record = attempt(completed_ns=4_000_000_000, success=True)
        seal_attempt(record)
        self.assertIs(record["success"], True)
        self.assertFalse(record["observation"]["censored"])
        self.assertEqual(record["observation"]["termination"], "complete")

    def test_automatic_census_uses_censor_metadata_without_semantic_label(self):
        record = attempt(status=200, success=True, censored=True)
        raw = {"attempt_key": opaque_attempt(record), "step_ids": ["req-a"],
               "phase": "target", "state": "11"}
        output = automatic_census([record], [raw])[0]
        self.assertEqual(output["observation_policy"], "censored-v3")
        self.assertTrue(output["observation_censored"])
        self.assertEqual(output["deadline_ns"], 11_000_000_000)
        for forbidden in ("operation", "operation_id", "success", "status", "body",
                          "planned_steps", "request_intent", "actual_step_ids"):
            self.assertNotIn(forbidden, output)
        changed = deepcopy(record)
        changed["success"] = False
        changed["http_steps"][0]["status"] = 500
        self.assertEqual(automatic_census([changed], [raw]), [output])

    def test_http_curve_counts_wrong_completed_response_but_not_incomplete(self):
        correct = attempt(status=200, success=True, completed_ns=3_000_000_000, request_id="a")
        wrong = attempt(status=500, success=False, completed_ns=4_000_000_000, request_id="b")
        incomplete = attempt(status=None, success=None, completed_ns=11_000_000_000,
                             censored=True, request_id="c")
        result = http_curves([correct, wrong, incomplete], cap_seconds=10.0)
        curve = result["curves"][0]
        self.assertEqual(curve["n"], 3)
        self.assertEqual(curve["completed_response_observations"], 2)
        self.assertEqual(curve["censored"], 1)
        self.assertEqual(curve["points"][-1], {"seconds": 10.0, "fraction": 2 / 3})
        self.assertIsNone(result["application_slo"])
        self.assertEqual(result["engineering_observation_cap_seconds"], 10.0)
        self.assertIn("incorrect HTTP responses", result["meaning"])


if __name__ == "__main__":
    unittest.main()
