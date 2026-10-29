"""Lock historical replay call sites to their original Jaeger envelope shape."""
import ast
from pathlib import Path

import pytest


@pytest.mark.parametrize("module", ["checkpoint_diagnostic_v4", "replay_qualification_v4"])
def test_historical_replay_explicitly_retains_per_trace_native_envelopes(module):
    path = Path(__file__).resolve().parents[1] / "src/ebpf_discovery" / f"{module}.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "Toolchain"]
    assert len(calls) == 1
    options = {keyword.arg: keyword.value for keyword in calls[0].keywords}
    assert isinstance(options.get("native_jaeger_envelope"), ast.Constant)
    assert options["native_jaeger_envelope"].value == "per_trace"
