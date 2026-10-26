from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from systems.deathstarbench.adapter import Adapter


class OracleTests(unittest.TestCase):
    def test_timeline_oracle_accepts_only_pinned_shapes(self):
        self.assertFalse(Adapter._valid_timeline(b"{}", "fixture"))
        self.assertTrue(Adapter._valid_timeline(json.dumps([{"post_id": "1", "text": "fixture"}]).encode(), "fixture"))
        self.assertFalse(Adapter._valid_timeline(json.dumps([{"post_id": "1", "text": "other"}]).encode(), "fixture"))
        self.assertFalse(Adapter._valid_timeline(b'{"post_id":"1","text":"fixture"}', "fixture"))
        self.assertFalse(Adapter._valid_timeline(json.dumps([{"post_id": 1, "text": "fixture"}]).encode(), "fixture"))
        self.assertFalse(Adapter._valid_timeline(b"not json", "fixture"))

    def test_deadline_uses_monotonic_elapsed_time(self):
        self.assertTrue(Adapter._within_deadline(1_000, 2_000_000_000, 2.0))
        self.assertFalse(Adapter._within_deadline(1_000, 2_000_001_001, 2.0))

    def test_late_response_fails_and_wire_identity_is_opaque(self):
        class Context:
            mode = "full"
            seed = 0

            def __init__(self, root):
                self.deployment_dir = root / "deployment"
                self.out = root

            @staticmethod
            def node_ip(_node):
                return "192.0.2.1"

        class Response:
            ok = True
            status_code = 200
            content = b"Successfully upload post"

        with tempfile.TemporaryDirectory() as directory:
            adapter = Adapter(Context(Path(directory)))
            with mock.patch("systems.deathstarbench.adapter.requests.request", return_value=Response()) as request:
                with mock.patch("systems.deathstarbench.adapter.time.monotonic_ns", side_effect=[0, 1_900_000_000, 2_100_000_001]):
                    with mock.patch("systems.deathstarbench.adapter.time.time_ns", side_effect=[10, 20]):
                        record = adapter.operation("compose_post", 7, "secret-operation-label", deadline=2.0)
        self.assertFalse(record["success"])
        step = record["http_steps"][0]
        self.assertFalse(step["within_deadline"])
        self.assertEqual(step["request_id"], step["request_headers"]["X-Experiment-Request-Id"])
        self.assertTrue(step["request_id"].startswith("req-"))
        self.assertNotIn("secret-operation-label", step["url"])
        self.assertNotIn("secret-operation-label", json.dumps(step["request_headers"]))
        self.assertNotIn("uber-trace-id", {key.lower() for key in step["request_headers"]})

    def test_verification_after_control_change_is_unknown_and_nonmutating(self):
        class Context:
            mode = "full"
            seed = 0

            def __init__(self, root):
                self.deployment_dir = root / "deployment"
                self.out = root

            @staticmethod
            def node_ip(_node):
                return "192.0.2.1"

        source = [{
            "operation": "compose_post", "success": True, "ended_ns": 1,
            "http_steps": [{"request_id": "req-abc"}],
            "validation": {"control_epoch": 0},
        }]
        with tempfile.TemporaryDirectory() as directory:
            adapter = Adapter(Context(Path(directory)))
            adapter._control_epoch = 1
            verified = adapter.verify(source)
        self.assertNotIn("eventual_postcondition", source[0])
        self.assertIsNone(verified[0]["eventual_postcondition"]["success"])
        self.assertEqual(verified[0]["eventual_postcondition"]["unknown_reason"], "control state changed before verification")
