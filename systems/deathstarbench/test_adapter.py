from __future__ import annotations

import json
import unittest

from systems.deathstarbench.adapter import Adapter


class OracleTests(unittest.TestCase):
    def test_timeline_oracle_accepts_only_pinned_shapes(self):
        self.assertTrue(Adapter._valid_timeline(b"{}"))
        self.assertTrue(Adapter._valid_timeline(json.dumps([{"post_id": "1", "text": "x"}]).encode()))
        self.assertFalse(Adapter._valid_timeline(b'{"post_id":"1","text":"x"}'))
        self.assertFalse(Adapter._valid_timeline(json.dumps([{"post_id": 1, "text": "x"}]).encode()))
        self.assertFalse(Adapter._valid_timeline(b"not json"))
