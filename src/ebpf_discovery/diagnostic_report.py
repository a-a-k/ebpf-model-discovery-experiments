"""Render saved diagnostic tables; run only in Actions."""
import argparse
from collections import defaultdict
import csv
import os
from pathlib import Path
import shutil

from .diagnostics import csv_write, read, write, VARIANTS


def csv_read(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def number(value):
    return f'{float(value):.2f}' if value not in ('', None) else 'unknown'


def generate(inputs, out):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Research reporting runs in GitHub Actions only')
    out.mkdir(parents=True, exist_ok=True)
    roots = sorted(p.parent for p in inputs.glob('*/status.json'))
    status = [read(p/'status.json') for p in roots]
    if len(status) != 3 or {s['system'] for s in status} != {'deathstarbench', 'otel_demo', 'petclinic'}:
        raise ValueError('Require all three completed system diagnostics')
    if any(s['status'] != 'complete' or s['campaigns'] != 9 for s in status):
        raise ValueError('Incomplete diagnostic population')
    summary, forecasts, classification, mismatches = [], [], [], []
    for root in roots:
        summary.extend(csv_read(root/'summary.csv'))
        forecasts.extend(csv_read(root/'forecasts.csv'))
        classification.extend(csv_read(root/'classification-by-state.csv'))
        mismatches.extend(csv_read(root/'proxy-mismatches.csv'))
        system = read(root/'status.json')['system']
        shutil.copytree(root, out/'systems'/system, dirs_exist_ok=True)
    csv_write(out/'summary.csv', summary)
    csv_write(out/'forecasts.csv', forecasts)
    csv_write(out/'classification-by-state.csv', classification)
    csv_write(out/'proxy-mismatches.csv', mismatches)
    protected = [read(p) for root in roots for p in root.glob('evidence/*/provenance.json')]
    if len(protected) != 27 or not all(p['original_forecasts_reproduced'] and p['original_hashes_unchanged'] for p in protected):
        raise ValueError('Original preservation/reproduction check incomplete')
    lines = ['# Iteration 2: retrospective failure diagnosis', '',
        f"Generated in [Actions {os.environ.get('GITHUB_RUN_ID')}](https://github.com/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{os.environ.get('GITHUB_RUN_ID')}).",
        '', 'All 27 original campaigns are included. No new application attempts were made. '
        'All original-cell forecasts were reproduced and protected originals were unchanged.', '',
        '**Oracle-assisted cells are diagnostic controls, not deployable eBPF results or fresh confirmation.** '
        'Only calibration class labels and/or calibration business outcomes change. '
        'Original class assignments remain frozen in the outcome-only cell. '
        'Unknown outcomes remain unknown. Direct conditional weighting is the calculation in every cell.', '',
        '## H1/H2: paired replacement effects', '',
        'Mean worst-end error of nominal Wilson envelopes, percentage points, over the same three seeds. '
        'The four columns are original; oracle class labels; oracle calibration outcomes; both oracles. '
        'All native/combined comparisons, point errors, unknowns and individual seeds are in the CSV files.', '',
        '| System | Mode | Operation | Original | Class oracle | Outcome oracle | Both oracles |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    groups = defaultdict(dict)
    for row in summary:
        if row['source'] == 'ebpf':
            groups[(row['system'], row['mode'], row['operation'])][row['variant']] = row
    for key, variants in sorted(groups.items()):
        values = [number(variants[v]['mean_wilson_worst_error_pp']) for v in VARIANTS]
        lines.append('| ' + ' | '.join([*key, *values]) + ' |')
    lines += ['', 'These replacement effects include the estimator\'s pessimistic treatment of '
              'unclassified attempts. They do not demonstrate that the raw eBPF stream contains '
              'the oracle information, or that a deployable classifier/completion binder can recover it.', '',
              '## H4: identification uncertainty and nominal sampling padding', '',
              'Original eBPF forecasts only; percentage points averaged over three seeds. '
              'Padding is the extra total interval width introduced by the nominal Wilson envelope. '
              'It is not an estimated effective sample size or validated temporal coverage.', '',
              '| System | Mode | Operation | Identification worst error | Wilson worst error | Identification width | Wilson padding |',
              '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for key, variants in sorted(groups.items()):
        row = variants['original']
        fields = ('mean_identification_worst_error_pp', 'mean_wilson_worst_error_pp',
                  'mean_identification_width_pp', 'mean_wilson_padding_pp')
        lines.append('| ' + ' | '.join([*key, *(number(row[f]) for f in fields)]) + ' |')
    lines += ['', '## H3: raw Kafka identity and normalization audit', '',
              'Raw span counts are unique exported Kafka records across the complete retained capture; '
              'matcher links are associations, not commits or timely business success.', '',
              '| Campaign | Source | Raw Kafka spans | Exact normalized matches | Raw exact candidates | Matcher linked | Assessment |',
              '| --- | --- | ---: | ---: | ---: | ---: | --- |']
    async_rows = []
    for root in roots:
        for path in sorted(root.glob('evidence/*/async-identity-audit.json')):
            for source, data in read(path)['sources'].items():
                counts = data['stage_counts']
                row = {'campaign': path.parent.name, 'source': source, **counts, 'assessment': data['assessment']['status']}
                async_rows.append(row)
                lines.append('| ' + ' | '.join(str(x) for x in (path.parent.name, source,
                    counts['raw_kafka_spans'], counts['normalized_exact_matches'],
                    counts['raw_exact_identity_candidates'], counts['matcher_linked'], data['assessment']['status'])) + ' |')
    csv_write(out/'async-identity-summary.csv', async_rows)
    lines += ['', '## Petclinic: source-only completion evidence', '',
              'The audit receives explicit operation contracts, timing and source spans, but no oracle outcomes. '
              'It does not interpret response-payload semantics. Evaluation joins outcomes only afterward. It can identify explicit '
              'failure of required completion; this protocol-only audit does not evaluate captured '
              'response bodies or certify persistence. Body-field availability is inventoried separately. '
              'Per-attempt witnesses are retained in each campaign\'s semantic-evidence-audit.json.', '',
              '| Campaign | Source | Target attempts | Proxy true / external false | Of those, source audit establishes failure | False audit / external true |',
              '| --- | --- | ---: | ---: | ---: | ---: |']
    semantic_rows = []
    for root in roots:
        for path in sorted(root.glob('evidence/*/semantic-audit-comparison.csv')):
            data = csv_read(path)
            semantic_rows.extend(data)
            for source in ('ebpf', 'native'):
                selected = [r for r in data if r['phase'] == 'target' and r['source'] == source]
                errors = [r for r in selected if r['original_proxy'] == 'True' and r['external_success'] == 'False']
                detected = sum(r['source_business_verdict'] == 'False' for r in errors)
                contradicted = sum(r['source_false_contradicts_external'] == 'True' for r in selected)
                lines.append(f'| {path.parent.name} | {source} | {len(selected)} | {len(errors)} | {detected} | {contradicted} |')
    csv_write(out/'semantic-audit-comparison.csv', semantic_rows)
    lines += ['', '## Scope and next design', '',
              'The DB graph was not an input to the original saturated predictor. Shared MySQL already '
              'exists in Petclinic. A future DB intervention must actually use that dependency in '
              'the prediction and compare ordinary endpoint inventory under the same contracts. '
              'This iteration makes no new DB forecast claim.', '',
              'Source-only repairs need fresh confirmation after their semantics are reviewed. '
              'No automatic additional 27-campaign sweep is part of this iteration.', '',
              '## Provenance and costs', '',
              'Each system status records elapsed analysis including downloads; each campaign records '
              'processing seconds, original hashes and the exact archived input ZIP hash/size. '
              'Original acquisition costs and failed attempts remain in the first report. '
              'Actions job records cover preparation/failures; human/agent time is unmetered and '
              'not zero. No efficiency superiority is established.']
    (out/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    write(out/'status.json', {'status': 'complete', 'campaigns': 27,
          'commit': os.environ.get('GITHUB_SHA'), 'run_id': os.environ.get('GITHUB_RUN_ID'),
          'system_statuses': status, 'new_application_attempts': 0,
          'protected_originals_verified': 27*3*5, 'fresh_confirmation': False})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    generate(args.inputs, args.out)


if __name__ == '__main__':
    main()
