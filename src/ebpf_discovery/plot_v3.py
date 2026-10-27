"""Publication figures from the already aggregated iteration-3 results only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SYSTEMS = ("deathstarbench", "otel_demo", "petclinic")
MODES = ("absent", "partial", "full")
SOURCES = ("ebpf", "native", "combined", "entry_http")
COLORS = {"ebpf": "#2166ac", "native": "#b2182b", "combined": "#542788", "entry_http": "#1b7837"}
SOURCE_LABELS = {"ebpf": "eBPF", "native": "native", "combined": "combined", "entry_http": "entry HTTP"}
PANELS = (
    ("point_error_pp", "Point absolute error (pp)"),
    ("nominal_worst_end_pp", "Nominal worst-end error (pp)"),
    ("source_unknown_pct", "Source outcome unknown (%)"),
)


def plot_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert aggregate fractions to plot units while preserving missing points."""
    if result.get("schema_version") != 3 or result.get("campaigns") != 27:
        raise ValueError("Expected complete 27-campaign iteration-3 aggregate")
    if result.get("application_deadline_seconds", "missing") is not None:
        raise ValueError("Plot input must not impose an application SLO")
    output = []
    seen = set()
    for row in result["summaries"]:
        key = (row["system"], row["mode"], row["operation"], row["source"])
        if key in seen or key[0] not in SYSTEMS or key[1] not in MODES or key[3] not in SOURCES:
            raise ValueError(f"Duplicate or invalid plot row: {key}")
        seen.add(key)
        if row["seeds"] != [3, 4, 5]:
            raise ValueError(f"Incomplete three-seed row: {key}")
        attempts = row["external_attempts"]
        unknown = row["source_business_unknown"]
        if type(attempts) is not int or attempts <= 0 or type(unknown) is not int or not 0 <= unknown <= attempts:
            raise ValueError(f"Invalid unknown denominator: {key}")
        values = {}
        for field, count_field, target in (
            ("mean_point_absolute_error", "point_error_known_seeds", "point_error_pp"),
            ("mean_nominal_worst_end_error", "nominal_error_known_seeds", "nominal_worst_end_pp"),
        ):
            value, known_seeds = row[field], row[count_field]
            if type(known_seeds) is not int or not 0 <= known_seeds <= 3:
                raise ValueError(f"Invalid known-seed count: {key}")
            if known_seeds != 3 and value is not None:
                raise ValueError(f"Partially identified mean must stay missing: {key}")
            if value is not None and (not isinstance(value, (int, float)) or not 0 <= value <= 1):
                raise ValueError(f"Invalid error fraction: {key}")
            values[target] = None if value is None else 100 * value
        output.append({"system": key[0], "mode": key[1], "operation": key[2], "source": key[3],
                       **values, "source_unknown_pct": 100 * unknown / attempts,
                       "source_unknown": unknown, "external_attempts": attempts})
    if not output:
        raise ValueError("Aggregate has no operation summaries")
    return output


def render(input_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Research figures are rendered in GitHub Actions only")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    source = Path(input_path)
    result = json.loads(source.read_text(encoding="utf-8"))
    rows = plot_rows(result)
    destination = Path(out_dir)
    destination.mkdir(parents=True, exist_ok=True)
    outputs = []
    offsets = {"ebpf": -0.24, "native": -0.08, "combined": 0.08, "entry_http": 0.24}
    for system in SYSTEMS:
        selected = [row for row in rows if row["system"] == system]
        if not selected:
            continue
        operations = sorted({row["operation"] for row in selected})
        categories = [(operation, mode) for operation in operations for mode in MODES]
        positions = {category: index for index, category in enumerate(categories)}
        fig, axes = plt.subplots(3, 1, figsize=(max(13, len(categories)*1.1), 10), sharex=True,
                                 constrained_layout=True)
        missing_counts = {}
        for ax, (field, label) in zip(axes, PANELS, strict=True):
            missing_counts[field] = sum(row[field] is None for row in selected)
            plotted = 0
            for source_name in SOURCES:
                source_rows = [row for row in selected if row["source"] == source_name and row[field] is not None]
                if not source_rows:
                    continue
                x = [positions[(row["operation"], row["mode"])] + offsets[source_name] for row in source_rows]
                y = [row[field] for row in source_rows]
                ax.scatter(x, y, s=35, color=COLORS[source_name], marker="o", alpha=0.9)
                plotted += len(source_rows)
            ax.set_ylabel(label)
            ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
            ax.set_axisbelow(True)
            ax.set_ylim(bottom=0)
            if not plotted:
                ax.text(0.5, 0.5, "No identified values", ha="center", va="center", transform=ax.transAxes)
            elif missing_counts[field]:
                ax.text(0.99, 0.95, f"{missing_counts[field]} missing", transform=ax.transAxes,
                        ha="right", va="top", fontsize=9, color="#555555")
        axes[-1].set_xticks(range(len(categories)))
        axes[-1].set_xticklabels([f"{operation.replace('_', ' ')}\n{mode}" for operation, mode in categories],
                                 rotation=35, ha="right", fontsize=9)
        axes[-1].set_xlim(-0.6, len(categories)-0.4)
        fig.suptitle(f"{system.replace('_', ' ').title()}: operation forecasts and unknown outcomes")
        fig.legend(handles=[Line2D([0], [0], marker="o", linestyle="", color=COLORS[s],
                                   label=SOURCE_LABELS[s]) for s in SOURCES],
                   loc="upper center", bbox_to_anchor=(0.5, 0.985), ncol=4, frameon=False)
        fig.text(0.5, 0.005,
                 "Point error requires all three seed estimates. Nominal worst-end is interval-end error against external empirical bounds; "
                 "missing values have no marker. Unknown denominator includes every attempt. No accuracy gate or application SLO.",
                 ha="center", va="bottom", fontsize=8)
        stem = f"operation-forecasts-{system}"
        for extension in ("svg", "png"):
            path = destination / f"{stem}.{extension}"
            fig.savefig(path, dpi=200, bbox_inches="tight")
            outputs.append({"system": system, "path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "missing_values": missing_counts})
        plt.close(fig)
    manifest = {"input": source.name, "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "figure_meaning": "source comparison; missing values are not zero; nominal worst-end is not point error",
                "figures": outputs}
    (destination / "plot-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.input, args.out), sort_keys=True))


if __name__ == "__main__":
    main()
