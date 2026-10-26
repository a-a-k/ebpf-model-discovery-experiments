"""Generate operation-level tables and figures from retained metrics, in Actions."""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
import json
import os
from pathlib import Path
from statistics import mean


def report(inputs, out):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Research result processing runs in GitHub Actions')
    out.mkdir(parents=True, exist_ok=True)
    rows, campaigns = [], []
    for path in sorted(inputs.rglob('metrics.json')):
        m = json.loads(path.read_text())
        campaigns.append({'system': m['system'], 'mode': m['mode'], 'seed': m['seed'], 'run_id': m['run_id'],
                          'path': str(path.relative_to(inputs)), **m['costs']})
        for source, result in m['sources'].items():
            for operation, op in result['operations'].items():
                prediction = op['forecast'] or {}
                rows.append({'system': m['system'], 'mode': m['mode'], 'seed': m['seed'], 'source': source,
                             'operation': operation, 'run_id': m['run_id'], 'forecast': prediction.get('point'),
                             'external': op['external']['point'], 'external_unknown': op['external']['unknown'],
                             'absolute_error_pp': op['absolute_error']*100 if op['absolute_error'] is not None else None,
                             'worst_interval_error_pp': op['worst_interval_error']*100,
                             'interval_width_pp': op['interval_width']*100, 'unsupported': op['unsupported'],
                             'target_unclassified': op['target_unclassified']})
    for filename, data in [('operations.csv', rows), ('costs.csv', campaigns)]:
        with (out/filename).open('w', newline='', encoding='utf-8') as stream:
            if data:
                writer = csv.DictWriter(stream, fieldnames=list(data[0]))
                writer.writeheader()
                writer.writerows(data)
    groups = defaultdict(list)
    for row in rows:
        groups[(row['system'], row['mode'], row['source'], row['operation'])].append(row)
    lines = ['# Generated empirical results', '', f'Complete metrics files: {len(campaigns)} of 27 planned campaigns.', '',
             'Every value is generated from the accompanying CSV and retained per-campaign metrics. Missing/technical failures are not successful zero-error results.', '',
             '| System | Mode | Source | Operation | Repeats | Mean absolute error, pp | Worst-end error, pp | Informative width |',
             '|---|---|---|---|---:|---:|---:|---|']
    def fmt(value):
        return f'{value:.2f}' if value is not None else 'unknown'
    for key, data in sorted(groups.items()):
        seeds = [r['seed'] for r in data]
        complete = sorted(seeds) == [0, 1, 2]
        absolute = mean(r['absolute_error_pp'] for r in data) if complete and all(r['absolute_error_pp'] is not None for r in data) else None
        conservative = mean(r['worst_interval_error_pp'] for r in data) if complete else None
        informative = complete and all(r['interval_width_pp'] <= 10 and not r['unsupported'] for r in data)
        lines.append('| ' + ' | '.join([*key, str(len(data)), fmt(absolute), fmt(conservative), str(informative)]) + ' |')
    lines += ['', '## Retained run references', '']
    for run_id in sorted({str(r['run_id']) for r in campaigns}):
        lines.append(f'- [Actions run {run_id}](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/{run_id}).')
    failures = []
    for path in inputs.rglob('status.json'):
        status = json.loads(path.read_text())
        if status.get('status') != 'acquisition_complete':
            failures.append({'path': str(path.relative_to(inputs)), **status})
    (out/'technical-failures.json').write_text(json.dumps(failures, indent=2)+'\n')
    lines += ['', f'Retained technical failures: {len(failures)}. See `technical-failures.json`.', '',
              'Means are reported only with exactly seeds 0, 1, and 2; duplicate attempts must be resolved explicitly from technical-failure history, not averaged or selected by accuracy.']
    (out/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    if rows:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        labels = sorted({(r['system'], r['operation']) for r in rows})
        fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True, constrained_layout=True)
        for axis, mode in zip(axes, ('absent', 'partial', 'full')):
            for source, offset, color in [('ebpf', -.2, '#0072B2'), ('native', 0, '#D55E00'), ('combined', .2, '#009E73')]:
                selected = [r for r in rows if r['mode'] == mode and r['source'] == source]
                xs = [labels.index((r['system'], r['operation'])) + offset + (r['seed']-1)*.04 for r in selected]
                axis.scatter(xs, [r['worst_interval_error_pp'] for r in selected], color=color, label=source, s=18)
            axis.axhline(5, color='black', linestyle='--', linewidth=.8)
            axis.set(title=mode, ylabel='Worst-end error (pp)', ylim=(-2, 102))
            axis.legend(ncol=3, loc='upper right')
        axes[-1].set_xticks(range(len(labels)), [f'{system}\n{op}' for system, op in labels], rotation=55, ha='right')
        fig.savefig(out/'errors.svg')
        fig.savefig(out/'errors.png', dpi=180)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report(args.inputs, args.out)
