import json
import sys

import pytest

from ebpf_discovery.plot_v4 import main, render


def aggregate(rows):
    return {"schema_version": "evaluation-v4-aggregate",
            "per_operation_source_variant_repeats": rows}


def row(operation, source, variant, mean, span, available):
    return {"system": "otel_demo", "mode": "full", "operation": operation,
            "source": source, "variant": variant, "worst_end_error_mean": mean,
            "worst_end_error_range": span,
            "coverage": {"expected_repeats": 3, "observed": 3, "available": available}}


def test_render_preserves_stored_ranges_availability_and_unknown(tmp_path):
    source = tmp_path / "evaluation-v4.json"
    source.write_text(json.dumps(aggregate([
        row("browse", "ebpf", "raw", .25, [.10, .40], 3),
        row("browse", "native", "network_scope", None, None, 0),
    ])), encoding="utf-8")
    out = tmp_path / "figures"
    result = render(source, out)

    assert result["figures"] == [{"system": "otel_demo", "mode": "full",
                                   "stem": "errors-otel_demo-full"}]
    for suffix in ("svg", "png", "pdf"):
        path = out / f"errors-otel_demo-full.{suffix}"
        assert path.is_file() and path.stat().st_size > 0
    markdown = (out / "figures-v4.md").read_text(encoding="utf-8")
    assert "25.000" in markdown
    assert "10.000–40.000" in markdown
    assert "3/3" in markdown
    assert "unknown" in markdown and "0/3" in markdown
    svg = (out / "errors-otel_demo-full.svg").read_text(encoding="utf-8")
    assert "observed repeat min–max range" in svg
    assert "unknown (0/3)" in svg


def test_render_rejects_nonaggregate_schema(tmp_path):
    source = tmp_path / "evaluation-v4.json"
    source.write_text('{"schema_version":"campaign-v4"}', encoding="utf-8")
    with pytest.raises(ValueError, match="evaluation-v4 aggregate"):
        render(source, tmp_path / "out")


def test_cli_rejects_local_research_plotting(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(sys, "argv", ["plot_v4", "--aggregate", str(tmp_path / "in.json"),
                                      "--out-dir", str(tmp_path / "out")])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
