from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate-memory-streaming-v5.py"
SPEC = importlib.util.spec_from_file_location("validate_memory_streaming_v5", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


@pytest.mark.parametrize(("raw", "relative"), [
    ("/runner/work/campaign/observations/a.jsonl", "observations/a.jsonl"),
    ("/runner/work/campaign/native/final/traces.json", "native/final/traces.json"),
])
def test_retained_evidence_path_accepts_only_declared_roots(raw, relative):
    assert VALIDATOR._retained_evidence_path(raw).as_posix() == relative


def test_retained_evidence_path_rejects_unrelated_campaign_files():
    with pytest.raises(ValueError, match="no retained evidence root"):
        VALIDATOR._retained_evidence_path("/runner/work/campaign/toolchain/output.json")
