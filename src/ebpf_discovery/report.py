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


def campaign_metric_paths(inputs):
    # Native OTLP exporters also write metrics.json. Only campaign roots have
    # the acquisition status marker; exporter telemetry is never result data.
    return sorted(p for p in inputs.rglob('metrics.json') if (p.parent/'status.json').is_file())


def report(inputs, out, exclusions_path=Path('docs/technical-exclusions.json')):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Research result processing runs in GitHub Actions')
    out.mkdir(parents=True, exist_ok=True)
    rows, campaigns, jobs, superseded = [], [], [], []
    exclusion_rules = json.loads(exclusions_path.read_text()) if exclusions_path.exists() else []
    excluded = []
    classifications, structures, async_rows, db_controls, activity_rows = [], [], [], [], []
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
    for path in campaign_metric_paths(inputs):
        m = json.loads(path.read_text())
        exclusion = next((r for r in exclusion_rules if all(str(r[k]) == str(m[k]) for k in ('run_id', 'system', 'mode', 'seed'))), None)
        if exclusion:
            excluded.append({'path': str(path.relative_to(inputs)), 'rule': exclusion, 'metrics': m})
            continue
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
            for name in ('model.json', 'forecast.json', 'evaluation-map.json', 'observed-final-graph.json',
                         'validated-calibration-graph.json', 'message-chain-evidence.json'):
                if (path.parent/'models'/source/name).exists():
                    shutil.copy2(path.parent/'models'/source/name, source_out/name)
            identity = {k: m[k] for k in ('system', 'mode', 'seed', 'run_id')}
            identity['source'] = source
            for variant, value in result['classes'].items():
                classifications.append({**identity, 'variant': variant, **value})
            for activity in result.get('database_activity', []):
                activity_rows.append({**identity, 'observed_source': activity['source'],
                                      **{k: v for k, v in activity.items() if k not in ('source', 'example')}})
            reference = result.get('cross_node_reference_validation') or {}
            structures.append({**identity, 'observed_cross_node_links': len(result['cross_node']),
                               'native_reference_covered': reference.get('reference_covered'),
                               'native_reference_disagreement_rate': reference.get('error_rate_on_covered'),
                               'ground_truth_link_error_rate': result['cross_node_error_rate'],
                               'db_logical_nodes': len(result['database_nodes']),
                               'db_complete_endpoint_nodes': sum(n.get('complete_endpoint_observed') is True for n in result['database_nodes']),
                               'db_nodes_matching_selected_endpoint': sum(n['matches_selected_database'] is True for n in result['database_nodes']),
                               'db_selected_endpoint_unknown': sum(n['matches_selected_database'] is None for n in result['database_nodes']),
                               'db_selected_endpoint_protocol_disagreements': sum(n.get('selected_endpoint_protocol_agrees') is False for n in result['database_nodes']),
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
                                   'message_chains_with_native_support': sum('native' in r.get('message_chain_supporting_sources', []) for r in selected),
                                   'message_chains_with_ebpf_support': sum('ebpf' in r.get('message_chain_supporting_sources', []) for r in selected),
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
                           ('async.csv', async_rows), ('database-controls.csv', db_controls), ('database-activity.csv', activity_rows)]:
        with (out/filename).open('w', newline='', encoding='utf-8') as stream:
            if data:
                writer = csv.DictWriter(stream, fieldnames=list(data[0]))
                writer.writeheader()
                writer.writerows(data)
    groups = defaultdict(list)
    admitted = {(str(c['run_id']), c['system'], c['mode'], c['seed']) for c in campaigns}
    campaign_keys = [(c['system'], c['mode'], c['seed']) for c in campaigns]
    if len(set(campaign_keys)) != len(campaign_keys):
        raise RuntimeError('Duplicate admitted system/mode/seed campaigns require an explicit technical exclusion, never accuracy selection')
    for row in rows:
        groups[(row['system'], row['mode'], row['source'], row['operation'])].append(row)
    summaries = []
    lines = ['# Generated empirical results', '', f'Complete metrics files: {len(campaigns)} of 27 planned campaigns.', '',
             'Every value is generated from the accompanying CSV and retained per-campaign metrics. Missing/technical failures are not successful zero-error results.', '',
             '| System | Mode | Source | Operation | Repeats | Mean absolute error, pp | Worst-end error, pp | Informative width | Conservative 5 pp target |',
             '|---|---|---|---|---:|---:|---:|---|---|']
    def fmt(value):
        return f'{value:.2f}' if value is not None else 'unknown'
    for key, data in sorted(groups.items()):
        seeds = [r['seed'] for r in data]
        complete = sorted(seeds) == [0, 1, 2]
        absolute = mean(r['absolute_error_pp'] for r in data) if complete and all(r['absolute_error_pp'] is not None for r in data) else None
        conservative = mean(r['worst_interval_error_pp'] for r in data) if complete else None
        informative = complete and all(r['interval_width_pp'] <= 10 and not r['unsupported'] for r in data)
        meets = complete and informative and conservative <= 5
        summaries.append({**dict(zip(('system', 'mode', 'source', 'operation'), key)), 'repeats': len(data),
                          'complete': complete, 'mean_absolute_error_pp': absolute,
                          'mean_worst_end_error_pp': conservative, 'informative_width': informative,
                          'conservative_5pp_target_met': meets if complete else None})
        lines.append('| ' + ' | '.join([*key, str(len(data)), fmt(absolute), fmt(conservative), str(informative), str(meets) if complete else 'pending']) + ' |')
    (out/'summary.json').write_text(json.dumps({'complete_campaigns': len(campaigns), 'planned_campaigns': 27,
                                               'groups': summaries}, indent=2)+'\n')
    # Deterministic illustration selection, independent of measured accuracy.
    for system in sorted({c['system'] for c in campaigns}):
        selected = sorted((c for c in campaigns if c['system'] == system), key=lambda c: (c['mode'] != 'absent', c['seed'], str(c['run_id'])))[0]
        path = inputs/selected['path']
        observed = json.loads((path.parent/'models'/'ebpf'/'validated-calibration-graph.json').read_text())
        ids = {n['id']: f'n{i}' for i, n in enumerate(observed['nodes'])}
        diagram = ['flowchart LR']
        for node in observed['nodes']:
            label = (f"{node['system']} {node.get('address')}:{node.get('port')}" if node['kind'] == 'database'
                     else f"{node['service']} | guest {node.get('guest') or 'unknown'} | {node.get('instance') or 'instance unknown'}")
            label = label.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            diagram.append(f'  {ids[node["id"]]}["{label}"]')
        for edge in observed['edges']:
            diagram.append(f'  {ids[edge["from"]]} -->|{edge["evidence"]}| {ids[edge["to"]]}')
        (out/f'example-model-{system}.mmd').write_text('\n'.join(diagram)+'\n')
    lines += ['', '## Retained run references', '']
    for run_id in sorted({str(r['run_id']) for r in campaigns}):
        lines.append(f'- [Actions run {run_id}](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/{run_id}).')
    failures, attempts = [], []
    for path in inputs.rglob('status.json'):
        status = json.loads(path.read_text())
        key = (str(status.get('run_id')), status.get('system'), status.get('mode'), status.get('seed'))
        blocks_path = path.parent/'blocks.json'
        blocks = json.loads(blocks_path.read_text()) if blocks_path.exists() else []
        attempts.append({**{k: status.get(k) for k in ('run_id', 'system', 'mode', 'seed', 'status', 'protocol_version',
                                                     'attempted_operations', 'preparation_operations', 'elapsed_seconds')},
                         'included_in_primary_series': key in admitted,
                         'recorded_primary_attempts': sum(b['attempts'] for b in blocks if b['phase'] in ('class_train', 'calibration', 'target', 'class_test'))})
        if status.get('status') != 'acquisition_complete':
            failures.append({'path': str(path.relative_to(inputs)), **status})
    with (out/'acquisition-attempts.csv').open('w', newline='', encoding='utf-8') as stream:
        if attempts:
            writer = csv.DictWriter(stream, fieldnames=list(attempts[0]))
            writer.writeheader()
            writer.writerows(attempts)
    (out/'technical-failures.json').write_text(json.dumps(failures, indent=2)+'\n')
    (out/'superseded-pilots.json').write_text(json.dumps(superseded, indent=2)+'\n')
    (out/'excluded-campaigns.json').write_text(json.dumps(excluded, indent=2)+'\n')
    (out/'technical-exclusion-rules.json').write_text(json.dumps(exclusion_rules, indent=2)+'\n')
    lines += ['', f'Retained acquisition failures with status files: {len(failures)}. See `technical-failures.json`; other failed jobs remain in the job ledger.', '',
              f'Recorded primary attempts in the admitted series: {sum(a["recorded_primary_attempts"] for a in attempts if a["included_in_primary_series"])} of 58,320 planned. All retained acquisition attempts, preparation operations and invalid runs are separately listed in `acquisition-attempts.csv`.', '',
              f'Superseded protocol pilots: {len(superseded)}. Full metrics remain in `superseded-pilots.json`; excluded by protocol, not accuracy.', '',
              f'Acquired campaigns excluded by predeclared implementation defects: {len(excluded)}. All paired sources are excluded consistently; retained metrics and exact rules are in `excluded-campaigns.json` and `technical-exclusion-rules.json`. Original acquisition metrics and raw streams remain in the corresponding Actions artifacts/archive.', '',
              f'Total completed job time across retained repository history, including preparation, checks, selector jobs and failures: {sum(j["job_seconds_including_preparation"] or 0 for j in jobs):.1f} seconds. See `job-costs.csv`; campaign-only time is separately in `costs.csv`. Ongoing job time is unknown and excluded from this total. Human/agent engineering time was not independently metered and remains unknown.', '',
              'Class separation and coverage are in `classes.csv`; observed links, DB structure and semantic proxy mismatches in `structure.csv`; DB interventions in `database-controls.csv`; native name-derived and explicitly tagged DB activity in `database-activity.csv`; asynchronous controls and unknown identity chains in `async.csv`. Zero addressed DB nodes does not mean zero DB activity. Unknown endpoints never establish shared identity. Concrete DB-instance identity is not inferred from an IP address. Native ancestry agreement is a reference comparison, not independent ground-truth correctness. Example graphs are validation views of retained calibration observations; original model hashes and forecasts remain unchanged.', '',
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
    parser.add_argument('--exclusions', type=Path, default=Path('docs/technical-exclusions.json'))
    args = parser.parse_args()
    report(args.inputs, args.out, args.exclusions)
