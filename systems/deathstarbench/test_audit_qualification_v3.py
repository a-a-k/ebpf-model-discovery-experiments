"""Exercise the retained audit against the real index schema with synthetic rows."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from ebpf_discovery.store_v3 import ObservationStore
from systems.deathstarbench.audit_qualification_v3 import audit


class QualificationBindingAuditTests(unittest.TestCase):
    def test_counts_and_witnesses_use_read_only_existing_sqlite_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory)
            (capture / "projections").mkdir()
            rows = []
            for index in range(1200):
                request_id = f"req-{index:04d}"
                coarse = index == 0
                rows.append({
                    "attempt_key": f"key-{index:04d}", "operation_id": "compose_post",
                    "step_ids": [request_id], "started_ns": 1_000_000_000,
                    "ended_ns": 2_000_000_000, "deadline_ns": 11_000_000_000,
                    "observation_censored": False,
                    "observation_policy": "censored-v3",
                    "steps": [{"binding": "entry_outside_sealed_observation_window" if coarse else "entry_missing"}],
                    "body_evidence": {"reason": "body_not_exported"},
                })
            for source in ("native", "ebpf"):
                (capture / "projections" / f"{source}-final.json").write_text(json.dumps(rows))
            (capture / "status.json").write_text(json.dumps({
                "status": "qualification_complete", "system": "deathstarbench", "run_id": "synthetic",
            }))
            index = ObservationStore(capture / "observation-index.sqlite")
            candidate = {
                "source": "native", "node": None, "trace_id": "a" * 32, "span_id": "1" * 16,
                "parent_id": "", "service": "nginx-web-server", "instance": None,
                "name": "POST /wrk2-api/post/compose", "kind": None,
                "start_ns": 999_000_000, "end_ns": 1_500_000_000,
                "attributes": {"component": "nginx", "http.request.method": "POST",
                               "url.path": "/wrk2-api/post/compose"},
                "status": {}, "raw_file": "synthetic-native.json",
            }
            child = {**candidate, "span_id": "2" * 16, "parent_id": candidate["span_id"],
                     "start_ns": 1_100_000_000, "end_ns": 1_200_000_000,
                     "attributes": {"component": "lua",
                                    "http.request.header.x-experiment-request-id": "req-0000"}}
            index.db.execute("INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                "digest", "native", None, candidate["trace_id"], candidate["span_id"], "",
                candidate["service"], None, None, "None", candidate["start_ns"],
                candidate["end_ns"], None, None, None, None, 0, json.dumps(candidate),
            ))
            index.db.execute("INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                "digest-child", "native", None, child["trace_id"], child["span_id"], child["parent_id"],
                child["service"], None, "req-0000", "None", child["start_ns"],
                child["end_ns"], None, None, None, None, 0, json.dumps(child),
            ))
            index.close()
            with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
                result = audit(capture)
        self.assertEqual(result["qualification_attempts"], 1200)
        self.assertEqual(result["binding_reasons"], {
            "entry_missing": 1199, "entry_outside_sealed_observation_window": 1})
        self.assertEqual(result["native_header_anchor_categories"], {
            "allowed_service_header_anchor": 1, "no_native_header_anchor": 1199})
        self.assertEqual(result["pre_window_entry_replay_reasons"], {
            "entry_missing": 1199, "unique_declared_entry": 1})
        self.assertEqual(result["pre_window_entry_window_relation"], {
            "outside": 1, "unbound_before_window": 1199})
        self.assertEqual(result["raw_entry_boundary_counts"], {"start_before_journal": 1})
        self.assertEqual(sum(item["n"] for item in result["saved_binding_vs_revised_eligibility"]), 1200)
        self.assertEqual(sum(item["n"] for item in result["by_operation_binding_body"]), 1200)
        bound = next(item for item in result["witnesses"] if item["saved_binding_reason"] == "entry_outside_sealed_observation_window")
        self.assertTrue(bound["revised_entry_eligible"])
        self.assertEqual(bound["revised_entry_reason"], "native_header_child_attribution")
        self.assertEqual(bound["anchors_shown"][0]["spans"][0]["start_mod_millisecond_ns"], 0)
        self.assertEqual(bound["replayed_entry"]["end_minus_cutoff_ns"], -9_500_000_000)


if __name__ == "__main__":
    unittest.main()
