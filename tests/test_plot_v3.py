from __future__ import annotations

from copy import deepcopy
import os
import unittest
from unittest import mock

from ebpf_discovery.plot_v3 import plot_rows, render


def aggregate():
    return {"schema_version": 3, "campaigns": 27, "application_deadline_seconds": None,
            "summaries": [{
                "system": "deathstarbench", "mode": "full", "operation": "compose_post",
                "source": "ebpf", "seeds": [3, 4, 5],
                "mean_point_absolute_error": None, "point_error_known_seeds": 2,
                "mean_nominal_worst_end_error": 0.12, "nominal_error_known_seeds": 3,
                "external_attempts": 300, "source_business_unknown": 75,
            }]}


class PlotPreparationTests(unittest.TestCase):
    def test_unknown_point_stays_missing_and_nominal_error_has_own_units(self):
        row = plot_rows(aggregate())[0]
        self.assertIsNone(row["point_error_pp"])
        self.assertEqual(row["nominal_worst_end_pp"], 12.0)
        self.assertEqual(row["source_unknown_pct"], 25.0)
        self.assertEqual(row["external_attempts"], 300)

    def test_real_zero_is_distinct_from_missing(self):
        value = aggregate()
        value["summaries"][0].update(mean_point_absolute_error=0.0, point_error_known_seeds=3)
        self.assertEqual(plot_rows(value)[0]["point_error_pp"], 0.0)

    def test_partial_or_duplicate_result_fails_closed(self):
        partial = aggregate()
        partial["summaries"][0]["mean_point_absolute_error"] = 0.02
        with self.assertRaisesRegex(ValueError, "Partially identified"):
            plot_rows(partial)
        duplicate = aggregate()
        duplicate["summaries"].append(deepcopy(duplicate["summaries"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            plot_rows(duplicate)

    def test_render_is_actions_only(self):
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}):
            with self.assertRaisesRegex(RuntimeError, "GitHub Actions only"):
                render("nonexistent-results.json", "unused")


if __name__ == "__main__":
    unittest.main()
