from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = (Path(__file__).parents[1] / "scripts" /
          "validate-deepflow-checkpoint-accounting-v5.py")
SPEC = importlib.util.spec_from_file_location("validate_df_checkpoint_accounting", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def test_canonical_comparison_is_order_stable():
    assert VALIDATOR._canonical({"b": 2, "a": [1]}) == b'{"a":[1],"b":2}\n'


def test_zip_member_guard_rejects_parent_and_accepts_file():
    import zipfile
    assert VALIDATOR._safe(zipfile.ZipInfo("checkpoint/manifest.json")) is True
    assert VALIDATOR._safe(zipfile.ZipInfo("../manifest.json")) is False
