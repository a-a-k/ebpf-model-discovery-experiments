"""Generate operation-level tables and figures from retained metrics, in Actions."""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime
import csv
import json
import os
from pathlib import Path
import shutil
from statistics import mean


def report(inputs, out):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Research result processing runs in GitHub Actions')
    out.mkdir(parents=True, exist_ok=True)
    rows, campaigns, jobs, superseded = [], [], [], []
    classifications, structures, async_rows, db_controls = [], [], [], []
    seen_jobs = set()
    for path in sorted(inputs.rglob('*jobs.json')):
        for job in json.loads(path.read_text()).get('jobs', []):
            if job['id'] in seen_jobs:
                continue
            seen_jobs.add(job['id'])
            started, ended = job.get('started_at'), job.get('completed_at')
            seconds = (datetime.fromisoformat(ended.replace('Z', '+00:00')) - datetime.fromisoformat(started.replace('Z', '+00:00'))).total_seconds() if started and ended else None
            jobs.append({'run_id': job['run_id'], 'job_id': job['id'], 'name': job['name'],
                         'conclusion': job['conclusion'], 'job_seconds_including_preparation': seconds,
                         'url': job['html_url']})
    for path in sorted(inputs.rglob('metrics.json')):
        m = json.loads(path.read_text())
        if m.get('protocol_version') != 'fixed-warmup-v2':
            superseded.append({'path': str(path.relative_to(inputs)), 'reason': 'superseded preparation protocol',
                               'metrics': m})
            continue
        campaigns.append({'system': m['system'], 'mode': m['mode'], 'seed': m['seed'], 'run_id': m['run_id'],
                          'path': str(path.relative_to(inputs)), **m['costs']})
        # Keep the small, reviewable evidence beside generated tables. Raw
        # telemetry remains in the original Actions artifact/archive.
        evidence = out/'evidence'/f"{m['system']}-{m['mode']}-{m['seed']}-{m['run_id']}"
        evidence.mkdir(parents=True, exist_ok=True)
        for name in ('metrics.json', 'metrics-acquisition-version.json', 'status.json',
                     'forecast-saved.json', 'blocks.json', 'deployment.json'):
            if (path.parent/name).exists():
                shutil.copy2(path.parent/name, evidence/name)
        for source, result in m['sources'].items():
            source_out = evidence/'models'/source
            source_out.mkdir(parents=True, exist_ok=True)
            for name in ('model.json', 'forecast.json', 'evaluation-map.json', 'observed-final-graph.json'):
                if (path.parent/'models'/source/name).exists():
                    shutil.copy2(path.parent/'models'/source/name, source_out/name)
            identity = {k: m[k] for k in ('system', 'mode', 'seed', 'run_id')}
            identity['source'] = source
            for variant, value in result['classes'].items():
                classifications.append({**identity, 'variant': variant, **value})
            reference = result.get('cross_node_reference_validation') or {}
            structures.append({**identity, 'observed_cross_node_links': len(result['cross_node']),
                               'native_reference_covered': reference.get('reference_covered'),
                               'native_reference_disagreement_rate': reference.get('error_rate_on_covered'),
                               'ground_truth_link_error_rate': result['cross_node_error_rate'],
                               'db_logical_nodes': len(result['database_nodes']),
                               'db_nodes_matching_selected_address': sum(n['matches_selected_database'] for n in result['database_nodes']),
                               'db_concrete_instances_confirmed': sum(n.get('concrete_instance_confirmed') is True for n in result['database_nodes']),
                               'db_shared_dependencies': len(result.get('shared_database_dependencies', {})),
                               'db_forecast_effect': result['database_forecast_effect'],
                               'proxy_semantic_mismatches': result['proxy_mismatches'],
                               'proxy_semantic_comparable': result['proxy_comparable'],
                               'normalized_spans': result['normalized_spans']})
            for operation, phases in result['db_controls'].items():
                for phase, rate in phases.items():
                    db_controls.append({**identity, 'operation': operation, 'phase': phase,
                                        **{k: v for k, v in rate.items() if k != 'bounds'}})
            for phase in sorted({r['phase'] for r in result['async']}):
                selected = [r for r in result['async'] if r['phase'] == phase]
                async_rows.append({**identity, 'phase': phase, 'attempts': len(selected),
                                   'http_successes': sum(r['http_success'] is True for r in selected),
                                   'http_unknown': sum(r['http_success'] is None for r in selected),
                                   'durable_successes': sum((r.get('durable') or {}).get('success') is True for r in selected),
                                   'durable_unknown': sum((r.get('durable') or {}).get('success') is None for r in selected),
                                   'identity_chains_confirmed': sum(r['complete_identity_chain'] is True for r in selected),
                                   'identity_chains_unknown': sum(r['complete_identity_chain'] is None for r in selected)})
            for operation, op in result['operations'].items():
                prediction = op['forecast'] or {}
                rows.append({'system': m['system'], 'mode': m['mode'], 'seed': m['seed'], 'source': source,
                             'operation': operation, 'run_id': m['run_id'], 'forecast': prediction.get('point'),
                             'external': op['external']['point'], 'external_unknown': op['external']['unknown'],
                             'absolute_error_pp': op['absolute_error']*100 if op['absolute_error'] is not None else None,
                             'worst_interval_error_pp': op['worst_interval_error']*100,
                             'interval_width_pp': op['interval_width']*100, 'unsupported': op['unsupported'],
                             'target_unclassified': op['target_unclassified']})
    for filename, data in [('operations.csv', rows), ('costs.csv', campaigns), ('job-costs.csv', jobs),
                           ('classes.csv', classifications), ('structure.csv', structures),
                           ('async.csv', async_rows), ('database-controls.csv', db_controls)]:
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
    (out/'superseded-pilots.json').write_text(json.dumps(superseded, indent=2)+'\n')
    lines += ['', f'Retained technical failures: {len(failures)}. See `technical-failures.json`.', '',
              f'Superseded protocol pilots: {len(superseded)}. Full metrics remain in `superseded-pilots.json`; excluded by protocol, not accuracy.', '',
              f'Total completed job time across retained repository history, including preparation, checks, selector jobs and failures: {sum(j["job_seconds_including_preparation"] or 0 for j in jobs):.1f} seconds. See `job-costs.csv`; campaign-only time is separately in `costs.csv`. Ongoing job time is unknown and excluded from this total. Human/agent engineering time was not independently metered and remains unknown.', '',
              'Class separation and coverage are in `classes.csv`; observed links, DB structure and semantic proxy mismatches in `structure.csv`; DB interventions in `database-controls.csv`; asynchronous controls and unknown identity chains in `async.csv`. Concrete DB-instance identity is not inferred from an IP address. Native ancestry agreement is a reference comparison, not independent ground-truth correctness.', '',
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
