from __future__ import annotations

import json
import unittest

from systems.deathstarbench.contracts_v3 import (
    CONTRACTS, ENTRY_SERVICES, STABLE_FIXTURE_TEXT, payload_verdict, status_ok,
)


class DeathStarBenchContractsTests(unittest.TestCase):
    def test_declared_entry_and_routes(self):
        self.assertEqual(ENTRY_SERVICES, {"ebpf": ["nginx-thrift"], "native": ["nginx-web-server"]})
        self.assertEqual(
            {name: spec["steps"][0] for name, spec in CONTRACTS.items()},
            {
                "compose_post": {"method": "POST", "path": "/wrk2-api/post/compose"},
                "read_home_timeline": {"method": "GET", "path": "/wrk2-api/home-timeline/read"},
                "read_user_timeline": {"method": "GET", "path": "/wrk2-api/user-timeline/read"},
            },
        )

    def test_status_matches_requests_response_ok(self):
        for operation in CONTRACTS:
            for code, expected in ((99, False), (100, True), (200, True), (302, True),
                                   (399, True), (400, False), (599, False),
                                   (True, False), ("200", False), (None, False)):
                self.assertIs(status_ok(operation, 0, code), expected)

    def test_compose_acknowledgement(self):
        self.assertIs(payload_verdict("compose_post", "Successfully upload post\n", {})["value"], True)
        self.assertIs(payload_verdict("compose_post", "other response", {})["value"], False)
        self.assertIsNone(payload_verdict("compose_post", None, {})["value"])

    def test_timeline_shape_and_exact_fixture(self):
        for operation in ("read_home_timeline", "read_user_timeline"):
            valid = json.dumps([{"post_id": "1", "text": STABLE_FIXTURE_TEXT},
                                {"post_id": "2", "text": "other"}])
            self.assertIs(payload_verdict(operation, valid, {})["value"], True)
            for body in ("[]", "{}", '[{"post_id":"1","text":"other"}]',
                         '[{"post_id":1,"text":"' + STABLE_FIXTURE_TEXT + '"}]',
                         '[{"post_id":"1","text":"' + STABLE_FIXTURE_TEXT + '"},{}]'):
                self.assertIs(payload_verdict(operation, body, {})["value"], False)

    def test_ambiguous_or_invalid_json_is_unknown(self):
        for operation in ("read_home_timeline", "read_user_timeline"):
            for body in ('[{"post_id":"1","post_id":"2","text":"' + STABLE_FIXTURE_TEXT + '"}]',
                         '[{"post_id":"1","text":"' + STABLE_FIXTURE_TEXT + '","x":NaN}]',
                         '[{"post_id":"1","text":"' + STABLE_FIXTURE_TEXT + '"}',
                         'garbage'):
                self.assertIsNone(payload_verdict(operation, body, {})["value"])


if __name__ == "__main__":
    unittest.main()
