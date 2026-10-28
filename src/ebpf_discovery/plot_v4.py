"""Publication figures from the saved protocol-v4 aggregate.

This module only renders fields already present in ``evaluation-v4.json``.
Repeat minima/maxima are descriptive ranges, never confidence intervals.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


SOURCES = ("ebpf", "native", "combined")
VARIANTS = ("raw", "network_scope")
COLORS = {"ebpf": "#0072B2", "native": "#D55E00", "combined": "#009E73"}
MARKERS = {"raw": "o", "network_scope": "s"}


def _safe(value: object) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value)).strip("-") or "unknown"


def _load(path: Path) -> tuple[dict, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "evaluation-v4-aggregate":
        raise ValueError("plot_v4 requires an evaluation-v4 aggregate")
    rows = payload.get("per_operation_source_variant_repeats")
    if not isinstance(rows, list):
        raise ValueError("aggregate lacks per_operation_source_variant_repeats")
    return payload, rows


def _coverage(row: dict) -> str:
    coverage = row.get("coverage") or {}
    return f"{int(coverage.get('available', 0))}/{int(coverage.get('expected_repeats', 3))}"


def _render(rows: list[dict], system: str, mode: str, output: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    selected = [row for row in rows if row.get("system") == system and row.get("mode") == mode]
    operations = sorted({str(row.get("operation")) for row in selected})
    if not operations:
        raise ValueError(f"no rows for {system}/{mode}")
    combinations = [(source, variant) for source in SOURCES for variant in VARIANTS]
    lookup = {(str(row.get("operation")), row.get("source"), row.get("variant")): row
              for row in selected}

    matplotlib.rcParams["svg.fonttype"] = "none"
    figure, axis = plt.subplots(figsize=(10.5, max(3.2, 1.25 * len(operations) + 1.8)))
    offsets = {pair: (index - (len(combinations) - 1) / 2) * 0.10
               for index, pair in enumerate(combinations)}
    for op_index, operation in enumerate(operations):
        for source, variant in combinations:
            row = lookup.get((operation, source, variant))
            y = op_index + offsets[source, variant]
            availability = _coverage(row) if row else "0/3"
            value = None if row is None else row.get("worst_end_error_mean")
            span = None if row is None else row.get("worst_end_error_range")
            if value is None or not isinstance(span, list) or len(span) != 2:
                axis.text(101.5, y, f"unknown ({availability})", va="center", fontsize=7,
                          color=COLORS[source], clip_on=False)
                continue
            mean_pp = float(value) * 100.0
            low_pp, high_pp = float(span[0]) * 100.0, float(span[1]) * 100.0
            axis.errorbar(mean_pp, y, xerr=[[mean_pp - low_pp], [high_pp - mean_pp]],
                          fmt=MARKERS[variant], color=COLORS[source], markersize=4,
                          capsize=2, linewidth=1)
            axis.text(101.5, y, availability, va="center", fontsize=7,
                      color=COLORS[source], clip_on=False)

    axis.set_yticks(range(len(operations)), operations)
    axis.set_xlim(0, 100)
    axis.set_xlabel("Worst-end absolute error (percentage points)")
    axis.set_title(f"{system} / {mode}: mean and observed repeat min–max range")
    axis.grid(axis="x", alpha=0.25)
    axis.invert_yaxis()
    axis.text(1.015, 1.01, "availability", transform=axis.transAxes, fontsize=8,
              ha="left", va="bottom")
    handles = [Line2D([], [], color=COLORS[source], marker=MARKERS[variant],
                      linestyle="none", label=f"{source} / {variant}")
               for source, variant in combinations]
    axis.legend(handles=handles, ncol=3, fontsize=8, loc="lower center",
                bbox_to_anchor=(0.5, -0.31))
    figure.tight_layout()
    for suffix in ("svg", "png", "pdf"):
        figure.savefig(output.with_suffix("." + suffix), dpi=200, bbox_inches="tight")
    plt.close(figure)


def render(aggregate: Path, out_dir: Path) -> dict:
    """Render one figure per stored system/mode and a companion table."""
    _, rows = _load(aggregate)
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = sorted({(str(row.get("system")), str(row.get("mode"))) for row in rows})
    figures = []
    for system, mode in groups:
        stem = f"errors-{_safe(system)}-{_safe(mode)}"
        _render(rows, system, mode, out_dir / stem)
        figures.append({"system": system, "mode": mode, "stem": stem})

    relative_input = os.path.relpath(aggregate.resolve(), out_dir.resolve()).replace("\\", "/")
    lines = [
        "# Protocol-v4 stored aggregate figures",
        "",
        f"Input: [`evaluation-v4.json`]({relative_input})",
        "",
        "Values below are copied from the saved aggregate and converted from fractions to percentage points (pp).",
        "Repeat ranges are observed min–max ranges, not confidence intervals. `k/3` is stored availability.",
        "",
    ]
    for figure in figures:
        lines += [f"## {figure['system']} / {figure['mode']}", "",
                  f"![Worst-end errors]({figure['stem']}.svg)", ""]
    lines += ["## Stored values", "",
              "| System | Mode | Operation | Source | Variant | Mean (pp) | Repeat min–max (pp) | Availability |",
              "|---|---|---|---|---|---:|---:|---:|"]
    for row in sorted(rows, key=lambda item: tuple(str(item.get(key, "")) for key in
                                                   ("system", "mode", "operation", "source", "variant"))):
        mean_value = row.get("worst_end_error_mean")
        span = row.get("worst_end_error_range")
        mean_text = "unknown" if mean_value is None else f"{float(mean_value) * 100:.3f}"
        range_text = ("unknown" if not isinstance(span, list) or len(span) != 2 else
                      f"{float(span[0]) * 100:.3f}–{float(span[1]) * 100:.3f}")
        lines.append("| " + " | ".join([
            str(row.get("system", "")), str(row.get("mode", "")), str(row.get("operation", "")),
            str(row.get("source", "")), str(row.get("variant", "")), mean_text, range_text,
            _coverage(row),
        ]) + " |")
    markdown = out_dir / "figures-v4.md"
    markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"input": str(aggregate.resolve()), "figures": figures, "markdown": str(markdown.resolve())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        parser.error("v4 research plotting is permitted only in GitHub Actions")
    render(args.aggregate, args.out_dir)


if __name__ == "__main__":
    main()
