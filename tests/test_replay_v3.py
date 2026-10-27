from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ebpf_discovery.replay_v3 import archive_location, selected_evidence, summarize


class ReplayTests(unittest.TestCase):
    def test_selects_only_fixed_full_seed_zero_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, mode, seed in (("deathstarbench-full-0", "full", 0),
                                     ("deathstarbench-full-1", "full", 1),
                                     ("deathstarbench-absent-0", "absent", 0)):
                path = root / "evidence" / name
                path.mkdir(parents=True)
                (path / "status.json").write_text(json.dumps({
                    "system": "deathstarbench", "mode": mode, "seed": seed,
                }))
            self.assertEqual(selected_evidence(root, "deathstarbench").name, "deathstarbench-full-0")

    def test_archive_requires_unique_checksum_index(self):
        status = {"system": "petclinic", "run_id": "123"}
        name = "123-campaign-petclinic-full-0-123.zip"
        self.assertEqual(archive_location(status, {"tag-a": {name: "sha"}}), ("tag-a", name, "sha"))
        with self.assertRaises(ValueError):
            archive_location(status, {"tag-a": {name: "sha"}, "tag-b": {name: "sha"}})

    def test_source_summary_keeps_unknown_and_external_disagreement(self):
        rows = [
            {"attempt_key": "a", "operation_id": "compose_post", "phase": "target", "proxy": True,
             "protocol_only": True},
            {"attempt_key": "b", "operation_id": "compose_post", "phase": "target", "proxy": False,
             "protocol_only": True},
            {"attempt_key": "c", "operation_id": "compose_post", "phase": "target", "proxy": None,
             "protocol_only": True},
        ]
        reference = {"a": {"operation": "compose_post", "phase": "target", "success": False},
                     "b": {"operation": "compose_post", "phase": "target", "success": True},
                     "c": {"operation": "compose_post", "phase": "target", "success": True}}
        result = summarize({"ebpf": rows, "native": [], "combined": [], "entry_http": []}, reference)[0]
        self.assertEqual((result["source_true"], result["source_false"], result["source_unknown"]), (1, 1, 1))
        self.assertEqual(result["semantic_protocol_disagree"], 2)
        self.assertEqual((result["source_false_positive"], result["source_false_negative"]), (1, 1))
        self.assertEqual(result["comparable"], 2)


if __name__ == "__main__":
    unittest.main()
