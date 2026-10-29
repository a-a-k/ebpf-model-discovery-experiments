"""Figures of saved per-seed errors; no refitting or new uncertainty estimate."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .report_v5 import (REFERENCED_AGGREGATE_SCHEMA, _digest, _read,
                       _referenced_attempts, _validate_payload_manifest,
                       resolve_evaluation_reference)


CAPTION = (
    "Points and horizontal ranges copy saved worst-end errors and error ranges, "
    "converted from fractions to percentage points. Ranges are not confidence intervals. "
    "Unavailable errors stay unknown. U is the saved number of unknown external outcomes. "
    "Technical selection is not independent admission. Predictive error alone does not "
    "establish a utility or effort advantage; the equally informed direct baseline shares "
    "the stated arithmetic. Different source/preparation revisions prevent attribution "
    "of cost differences solely to collectors. No averaging, refit or success threshold."
)
FIELDS = (
    'operation', 'source', 'variant', 'available', 'reason', 'error', 'prediction',
    'point_prediction', 'forecast_interval', 'forecast_interval_status',
    'actual_target_success_counts', 'actual_counts', 'observed_empirical_bounds',
)


def saved_values(aggregate: Path) -> dict:
    payload = _read(aggregate)
    if payload.get('schema_version') != REFERENCED_AGGREGATE_SCHEMA:
        raise ValueError('v5 figures require a referenced saved report')
    _validate_payload_manifest(payload, aggregate)
    selected = _referenced_attempts(
        payload, aggregate, 'selected_main_attempt_references', stage='main')
    rows = []
    for attempt in selected:
        if attempt.get('eligible_main_coverage') is not True:
            raise ValueError('figure selection includes an ineligible main attempt')
        reference = attempt['evaluation_reference']
        evaluation = resolve_evaluation_reference(reference, aggregate)
        for saved in evaluation.get('evaluations') or []:
            rows.append({
                'attempt_key': attempt['attempt_key'],
                **{key: attempt.get(key) for key in
                   ('run_id', 'repository', 'collector', 'system', 'mode', 'seed')},
                'independently_admitted': attempt.get('independently_admitted'),
                'evaluation_reference': reference,
                'saved': {key: saved[key] for key in FIELDS if key in saved},
            })
        del evaluation
    return {
        'schema_version': 'v5-saved-error-figure-values',
        'aggregate': {'path': aggregate.name, 'sha256': _digest(aggregate)},
        'evaluation_payload_manifest': payload['evaluation_payload_manifest'],
        'grid': payload['grid'], 'selection': payload['selection'],
        'independent_admission': payload['independent_admission'],
        'selected_main_attempt_references': payload['selected_main_attempt_references'],
        'display_unit_conversion': 'fraction * 100 = percentage points',
        'caption': CAPTION, 'rows': rows,
    }


def display_value(row: dict) -> tuple[object, object, object]:
    saved = row['saved']
    error = saved.get('error') or {}
    counts = saved.get('actual_target_success_counts') or saved.get('actual_counts') or {}
    unknown = counts.get('none', counts.get('unknown'))
    if saved.get('available') is not True:
        return None, None, unknown
    return error.get('worst_end_error'), error.get('range'), unknown


def _figure(rows: list[dict], title: str, target: Path) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    colors = {'ebpf': '#0072B2', 'native': '#D55E00', 'combined': '#009E73'}
    markers = {6: 'o', 7: 's', 8: '^'}
    labels = sorted({tuple(row['saved'].get(key) for key in
                           ('operation', 'source', 'variant')) for row in rows})
    matplotlib.rcParams['svg.fonttype'] = 'none'
    fig, axis = plt.subplots(figsize=(12, max(4, len(labels) * .46 + 2)))
    for row in rows:
        saved = row['saved']
        label = tuple(saved.get(key) for key in ('operation', 'source', 'variant'))
        y = labels.index(label) + (row['seed'] - 7) * .23
        value, span, unknown = display_value(row)
        color = colors.get(saved.get('source'), '#444444')
        if value is not None:
            if span is not None:
                axis.plot([float(span[0]) * 100, float(span[1]) * 100], [y, y], color=color)
            axis.plot(float(value) * 100, y, marker=markers[row['seed']],
                      color=color, markersize=3, linestyle='none')
            text = f"U={unknown if unknown is not None else '?'}"
        else:
            text = f"unknown; U={unknown if unknown is not None else '?'}"
        axis.text(102, y, text, fontsize=6, va='center', color=color, clip_on=False)
    axis.set_yticks(range(len(labels)), [' / '.join(label) for label in labels], fontsize=7)
    axis.set_xlim(-1, 101)
    axis.set_ylim(-.6, len(labels) - .4)
    axis.invert_yaxis()
    axis.set_xlabel('Saved absolute error (percentage points)')
    axis.set_title(title + '\nPer-seed saved values; technical selection only', fontsize=10)
    axis.grid(axis='x', alpha=.2)
    axis.legend(handles=[Line2D([], [], marker=marker, color='#444444', linestyle='none',
                                label=f'seed {seed}') for seed, marker in markers.items()],
                ncol=3, fontsize=7, loc='lower center', bbox_to_anchor=(.5, -.12))
    fig.tight_layout()
    for suffix in ('svg', 'png', 'pdf'):
        fig.savefig(target.with_suffix('.' + suffix), dpi=180, bbox_inches='tight')
    plt.close(fig)


def render(aggregate: Path, out: Path) -> dict:
    values = saved_values(aggregate)
    out.mkdir(parents=True, exist_ok=True)
    values_path = out / 'saved-values-v5.json'
    values_path.write_text(json.dumps(values, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    groups = sorted({tuple(row[key] for key in ('collector', 'system', 'mode'))
                     for row in values['rows']})
    lines = ['# Iteration-5 saved error figures', '', CAPTION, '',
             'Exact copied values, source hashes, selection and independent-review status: '
             '[saved-values-v5.json](saved-values-v5.json).', '',
             '## Fixed main grid', '', '```json',
             json.dumps(values['grid'], indent=2), '```', '',
             'Blocked cells are listed separately within the incomplete/missing grid. '
             'A missing campaign is distinct from an available campaign with an unknown forecast.', '']
    for group in groups:
        rows = [row for row in values['rows'] if
                tuple(row[key] for key in ('collector', 'system', 'mode')) == group]
        stem = 'errors-' + '-'.join(group)
        _figure(rows, ' / '.join(group), out / stem)
        lines += ['## ' + ' / '.join(group), '', f'![Saved per-seed errors]({stem}.svg)', '']
    lines += ['## Copied per-seed values', '',
              '| Run | Collector | System | Mode | Seed | Operation | Source | Variant | Available | Saved error | Actual counts |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
    for row in values['rows']:
        saved = row['saved']
        cells = [row[key] for key in ('run_id', 'collector', 'system', 'mode', 'seed')]
        cells += [saved.get(key) for key in ('operation', 'source', 'variant', 'available', 'error')]
        cells += [saved.get('actual_target_success_counts', saved.get('actual_counts'))]
        lines.append('| ' + ' | '.join(json.dumps(cell, ensure_ascii=False).replace('|', '\\|')
                                       for cell in cells) + ' |')
    (out / 'figures-v5.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    proof = {'schema_version': 'v5-saved-error-figure-files', 'aggregate': values['aggregate'],
             'files': {path.name: {'sha256': _digest(path), 'bytes': path.stat().st_size}
                       for path in sorted(out.iterdir()) if path.is_file()
                       and path.name != 'figure-files-v5.json'}}
    (out / 'figure-files-v5.json').write_text(json.dumps(proof, indent=2, sort_keys=True) + '\n')
    return proof


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--aggregate', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        parser.error('research figure rendering is permitted only in GitHub Actions')
    render(args.aggregate, args.out_dir)


if __name__ == '__main__':
    main()
