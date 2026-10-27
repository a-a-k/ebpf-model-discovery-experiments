"""Retrospective, explicitly oracle-assisted diagnostics; never a discovery fitter.

Only main() processes retained research data, and only in GitHub Actions.
The original models, mappings, assignments and forecasts are read-only inputs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
from statistics import mean
import subprocess
import tempfile
import time
import zipfile

from .evaluate import external_rate
from .model import STATES, WEIGHTS, conditional
from .observations import opaque_attempt, read_spans, normalized_route

REPORT_RUN = '40459487189'
REPORT_TAG = 'data-40460660847'
REPORT_SHA256 = '102ae31f2f357976c6c132be2b69b17e405a76b5bbe1640da9c7fa7aea1c1c89'
ARCHIVES = ('data-40362321620', 'data-40455065560', 'data-40460660847')
VARIANTS = ('original', 'oracle_class', 'oracle_outcome', 'oracle_both')
PROTECTED = ('model.json', 'forecast.json', 'evaluation-map.json',
             'calibration-assignments.json', 'target-assignments.json')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def csv_write(path, rows):
    if not rows:
        return
    with Path(path).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def calculate(rows, key, weights=WEIGHTS):
    """The same direct conditional calculation in every cell; no MC advantage."""
    if key is None:
        return {'point': None, 'identification_bounds': [0., 1.],
                'uncertainty_bounds': [0., 1.]}, {}
    states = {state: conditional(rows, key, state) for state in STATES}
    identified = [sum(weights[s] * states[s]['identification_bounds'][i] for s in STATES)
                  for i in (0, 1)]
    uncertainty = [sum(weights[s] * states[s]['uncertainty_bounds'][i] for s in STATES)
                   for i in (0, 1)]
    return {'point': identified[0] if math.isclose(*identified, abs_tol=1e-12) else None,
            'identification_bounds': identified, 'uncertainty_bounds': uncertainty}, states


def diagnostic_cell(calibration, external_calibration, key, operation, variant, weights=WEIGHTS):
    """Oracle substitutions are calibration-only and independent of one another."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    labels = variant in ('oracle_class', 'oracle_both')
    outcomes = variant in ('oracle_outcome', 'oracle_both')
    if any(r['phase'] != 'calibration' for r in calibration):
        raise ValueError('Only calibration assignments may enter a diagnostic cell')
    if any(r['phase'] != 'calibration' for r in external_calibration.values()):
        raise ValueError('Target outcomes cannot enter diagnostic fitting')
    transformed = []
    for row in calibration:
        gold = external_calibration[row['attempt_key']]
        if row['state'] != gold['state']:
            raise ValueError('State mismatch in calibration join')
        changed = dict(row)
        if labels:
            changed['class_id'] = 'operation:' + gold['operation']
            changed['compatible_classes'] = [changed['class_id']]
        if outcomes:
            changed['proxy'] = gold.get('success')  # Unknown stays unknown.
        transformed.append(changed)
    return calculate(transformed, 'operation:' + operation if labels else key, weights)


def assert_prediction_equal(computed, saved):
    saved = saved or {'point': None, 'identification_bounds': [0., 1.],
                      'uncertainty_bounds': [0., 1.]}
    for field in ('identification_bounds', 'uncertainty_bounds'):
        if any(abs(a-b) > 1e-12 for a, b in zip(computed[field], saved[field])):
            raise ValueError(f'Original cell does not reproduce saved {field}')
    a, b = computed['point'], saved['point']
    if (a is None) != (b is None) or (a is not None and abs(a-b) > 1e-12):
        raise ValueError('Original cell does not reproduce saved point')


def score(predicted, external):
    lo, hi = predicted['identification_bounds']
    lower, upper = predicted['uncertainty_bounds']
    ylo, yhi = external['bounds']
    point, actual = predicted['point'], external['point']
    return {'point': point, 'external_point': actual, 'external_lower': ylo, 'external_upper': yhi,
            'absolute_error_pp': 100*abs(point-actual) if point is not None and actual is not None else None,
            'identification_lower': lo, 'identification_upper': hi,
            'wilson_lower': lower, 'wilson_upper': upper,
            'identification_width_pp': 100*(hi-lo),
            'wilson_width_pp': 100*(upper-lower),
            'wilson_padding_pp': 100*((upper-lower)-(hi-lo)),
            'identification_worst_error_pp': 100*max(abs(lo-yhi), abs(hi-ylo)),
            'wilson_worst_error_pp': 100*max(abs(lower-yhi), abs(upper-ylo)),
            'identification_covers_external': lo <= ylo+1e-12 and hi >= yhi-1e-12,
            'wilson_covers_external': lower <= ylo+1e-12 and upper >= yhi-1e-12,
            'target_n': external['n'], 'target_unknown': external['unknown']}


def semantic_census(external):
    """Explicit operation knowledge for a diagnostic audit; no business outcomes."""
    return [{'attempt_key': opaque_attempt(r), 'step_ids': [s['request_id'] for s in r['http_steps']],
             'contract_id': r['operation'], 'phase': r['phase'], 'state': r['state'],
             'started_ns': r['started_ns'], 'ended_ns': r['ended_ns'],
             'deadline_ns': r['started_ns'] + int(r.get('deadline_seconds', 2.) * 1e9)}
            for r in external if r['phase'] in ('calibration', 'target')]


def analyze_campaign(evidence, capture, out):
    started = time.perf_counter()
    metadata, status = read(evidence/'deployment.json'), read(evidence/'status.json')
    external = read(capture/'external.json')
    identity = {k: status[k] for k in ('system', 'mode', 'seed', 'run_id')}
    gold = {opaque_attempt(r): r for r in external if r['phase'] == 'calibration'}
    if len(gold) != 960 or sum(r['phase'] == 'target' for r in external) != 960:
        raise ValueError('Unexpected fixed-study population')
    rows, state_rows, classifications, mismatches, verified = [], [], [], [], {}
    for source in ('ebpf', 'native', 'combined'):
        folder = evidence/'models'/source
        before = {name: digest(folder/name) for name in PROTECTED}
        saved_hashes = read(evidence/'forecast-saved.json')
        for name, field in (('model.json', 'model_sha256'), ('forecast.json', 'sha256'),
                            ('evaluation-map.json', 'evaluation_map_sha256')):
            if before[name] != saved_hashes[field][source]:
                raise ValueError('Original protected hash mismatch')
            if digest(capture/'models'/source/name) != before[name]:
                raise ValueError('Original capture/report core bytes differ')
        mapping, model, forecast = (read(folder/name) for name in
                                     ('evaluation-map.json', 'model.json', 'forecast.json'))
        all_training = read(folder/'calibration-assignments.json')
        calibration = [r for r in all_training if r['phase'] == 'calibration']
        target = [r for r in read(folder/'target-assignments.json') if r['phase'] == 'target']
        if len(calibration) != 960 or len(target) != 960:
            raise ValueError('Missing original assignments')
        if model['target_weights'] != WEIGHTS:
            raise ValueError('Target weights changed')
        for operation in metadata['operations']:
            key = mapping.get(operation, {}).get('class_id')
            if key not in forecast['classes']:
                key = None
            observed = external_rate([r for r in external if r['phase'] == 'target' and r['operation'] == operation])
            for variant in VARIANTS:
                predicted, states = diagnostic_cell(calibration, gold, key, operation, variant, model['target_weights'])
                if variant == 'original':
                    assert_prediction_equal(predicted, forecast['classes'].get(key))
                common = {**identity, 'source': source, 'operation': operation, 'variant': variant}
                rows.append({**common, **score(predicted, observed)})
                for state, result in states.items():
                    state_rows.append({**common, 'state': state,
                                       **{k: v for k, v in result.items() if isinstance(v, int)},
                                       'identification_lower': result['identification_bounds'][0],
                                       'identification_upper': result['identification_bounds'][1]})
        for phase, assignments in (('calibration', calibration), ('target', target)):
            reference = {opaque_attempt(r): r for r in external if r['phase'] == phase}
            for state in STATES:
                selected = [r for r in assignments if r['state'] == state]
                counts = Counter((r['class_id'] is None, r['proxy']) for r in selected)
                classifications.append({**identity, 'source': source, 'phase': phase, 'state': state,
                    'n': len(selected), 'unclassified': sum(r['class_id'] is None for r in selected),
                    'unclassified_known_failure': counts[(True, False)],
                    'unclassified_known_success': counts[(True, True)], 'unclassified_unknown_proxy': counts[(True, None)]})
            for operation in metadata['operations']:
                selected = [r for r in assignments if reference[r['attempt_key']]['operation'] == operation]
                known = [r for r in selected if r['proxy'] is not None and reference[r['attempt_key']].get('success') is not None]
                mismatches.append({**identity, 'source': source, 'phase': phase, 'operation': operation,
                    'n': len(selected), 'comparable': len(known),
                    'proxy_false_positive': sum(r['proxy'] is True and reference[r['attempt_key']]['success'] is False for r in known),
                    'proxy_false_negative': sum(r['proxy'] is False and reference[r['attempt_key']]['success'] is True for r in known),
                    'unknown_proxy': sum(r['proxy'] is None for r in selected)})
        after = {name: digest(folder/name) for name in PROTECTED}
        if before != after:
            raise ValueError('Diagnostic mutated protected originals')
        verified[source] = before
    if status['system'] in ('otel_demo', 'petclinic'):
        spans, errors = read_spans(capture/'observations', capture/'native')
        if errors:
            write(out/'parse-errors.json', errors)
            raise ValueError('Raw audit parse failure')
        if status['system'] == 'otel_demo':
            from systems.otel_demo.identity_audit import audit_message_identity
            write(out/'async-identity-audit.json', audit_message_identity(capture/'observations', capture/'native', spans))
        else:
            from systems.petclinic.semantic_audit import audit_semantics, CONTRACTS
            audit = audit_semantics(spans, semantic_census(external))
            write(out/'semantic-evidence-audit.json', audit)
            comparison = []
            reference = {opaque_attempt(r): r for r in external}
            for source, result in audit['sources'].items():
                original = {r['attempt_key']: r for name in ('calibration-assignments.json', 'target-assignments.json')
                            for r in read(evidence/'models'/source/name)}
                for attempt in result['attempts']:
                    external_outcome = reference[attempt['attempt_key']].get('success')
                    original_attempt = original[attempt['attempt_key']]
                    contract = CONTRACTS[attempt['contract_id']]
                    expected_route = contract['method'] + ' ' + normalized_route(contract['entry_path'])
                    observed_routes = [r for r in original_attempt['signature'] if r]
                    comparison.append({**identity, 'source': source, 'operation': attempt['contract_id'],
                        'phase': attempt['phase'], 'state': attempt['state'], 'attempt_key': attempt['attempt_key'],
                        'entry_binding': attempt['entry_binding']['status'],
                        'original_proxy': original_attempt['proxy'],
                        'original_non_entry_route': any(r != expected_route for r in observed_routes) if observed_routes else None,
                        'response_body_content_available': attempt['response_body_evidence']['content_available'],
                        'logical_completion': attempt['logical_completion'],
                        'source_business_verdict': attempt['source_business_verdict'],
                        'external_success': external_outcome,
                        'source_false_contradicts_external': attempt['source_business_verdict'] is False and external_outcome is True})
            csv_write(out/'semantic-audit-comparison.csv', comparison)
    csv_write(out/'forecasts.csv', rows)
    csv_write(out/'conditional-states.csv', state_rows)
    csv_write(out/'classification-by-state.csv', classifications)
    csv_write(out/'proxy-mismatches.csv', mismatches)
    write(out/'provenance.json', {**identity, 'commit': os.environ.get('GITHUB_SHA'),
          'diagnostic_run': os.environ.get('GITHUB_RUN_ID'), 'original_hashes': verified,
          'original_hashes_unchanged': True, 'original_forecasts_reproduced': True,
          'processing_seconds': time.perf_counter()-started,
          'external_sha256': digest(capture/'external.json'),
          'oracle_cells_are_deployable': False, 'fresh_confirmation': False})
    return rows, classifications, mismatches


def download(tag, filename, directory):
    repository = os.environ['GITHUB_REPOSITORY']
    for attempt in range(3):
        result = subprocess.run(['gh', 'release', 'download', tag, '--repo', repository,
                                 '--pattern', filename, '--dir', str(directory), '--clobber'])
        if result.returncode == 0:
            return Path(directory)/filename
        if attempt < 2:
            time.sleep(3*(attempt+1))
    raise RuntimeError(f'Cannot download archived {filename}')


def extract(archive, destination):
    with zipfile.ZipFile(archive) as zipped:
        base = destination.resolve()
        for name in zipped.namelist():
            if not (base/name).resolve().is_relative_to(base):
                raise ValueError('Unsafe archive path')
        zipped.extractall(destination)


def aggregate(rows):
    groups = defaultdict(list)
    keys = ('system', 'mode', 'source', 'operation', 'variant')
    for row in rows:
        groups[tuple(row[k] for k in keys)].append(row)
    summary = []
    for key, selected in sorted(groups.items()):
        if len(selected) != 3 or {int(r['seed']) for r in selected} != {0, 1, 2}:
            raise ValueError('Every summary needs exactly three original seeds')
        points = [r['absolute_error_pp'] for r in selected if r['absolute_error_pp'] is not None]
        summary.append({**dict(zip(keys, key)), 'repeats': 3, 'identified_points': len(points),
            'mean_absolute_error_pp': mean(points) if len(points) == 3 else None,
            **{'mean_'+k: mean(r[k] for r in selected) for k in
               ('identification_width_pp', 'wilson_width_pp', 'wilson_padding_pp',
                'identification_worst_error_pp', 'wilson_worst_error_pp')},
            'max_wilson_width_pp': max(r['wilson_width_pp'] for r in selected),
            'conservative_gate': mean(r['wilson_worst_error_pp'] for r in selected) <= 5
                                 and max(r['wilson_width_pp'] for r in selected) <= 10})
    return summary


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Research diagnostics run in GitHub Actions only')
    parser = argparse.ArgumentParser()
    parser.add_argument('--system', choices=('deathstarbench', 'otel_demo', 'petclinic'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rows, classifications, mismatches, downloads = [], [], [], []
    workspace = Path('work/diagnostics')
    workspace.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=workspace) as temp:
        root = Path(temp)
        report_zip = download(REPORT_TAG, f'{REPORT_RUN}-report-{REPORT_RUN}.zip', root)
        if digest(report_zip) != REPORT_SHA256:
            raise ValueError('Pinned report ZIP hash mismatch')
        report = root/'report'
        extract(report_zip, report)
        indexes = {}
        for tag in ARCHIVES:
            target = root/tag
            target.mkdir()
            sums = download(tag, 'SHA256SUMS.txt', target)
            indexes[tag] = {line.split()[1]: line.split()[0] for line in sums.read_text().splitlines() if line.strip()}
        evidence_dirs = sorted(p.parent for p in (report/'evidence').glob(f'{args.system}-*/status.json'))
        if len(evidence_dirs) != 9:
            raise ValueError('Expected all nine original campaigns for the system')
        for evidence in evidence_dirs:
            status = read(evidence/'status.json')
            filename = f"{status['run_id']}-campaign-{args.system}-{status['mode']}-{status['seed']}-{status['run_id']}.zip"
            tags = [tag for tag in ARCHIVES if filename in indexes[tag]]
            if len(tags) != 1:
                raise ValueError(f'Expected exactly one archived source for {filename}')
            tag = tags[0]
            capture_out = args.out/'evidence'/evidence.name
            capture_out.mkdir(parents=True, exist_ok=True)
            download_start = time.perf_counter()
            with tempfile.TemporaryDirectory(dir=root) as capture_temp:
                capture_root = Path(capture_temp)
                archive = download(tag, filename, capture_root)
                actual_hash = digest(archive)
                if actual_hash != indexes[tag][filename]:
                    raise ValueError('Original capture ZIP hash mismatch')
                capture = capture_root/'capture'
                extract(archive, capture)
                roots = list(capture.rglob('external.json'))
                if len(roots) != 1:
                    raise ValueError('Expected exactly one capture root')
                downloads.append({'campaign': evidence.name, 'tag': tag, 'filename': filename,
                    'sha256': actual_hash, 'bytes': archive.stat().st_size,
                    'download_extract_seconds': time.perf_counter()-download_start})
                print(f'Analyzing {evidence.name}', flush=True)
                result, classes, mismatch = analyze_campaign(evidence, roots[0].parent, capture_out)
                rows.extend(result)
                classifications.extend(classes)
                mismatches.extend(mismatch)
            write(args.out/'download-provenance.json', downloads)
            print(f'Completed {evidence.name}', flush=True)
    csv_write(args.out/'forecasts.csv', rows)
    csv_write(args.out/'summary.csv', aggregate(rows))
    csv_write(args.out/'classification-by-state.csv', classifications)
    csv_write(args.out/'proxy-mismatches.csv', mismatches)
    write(args.out/'status.json', {'status': 'complete', 'system': args.system, 'campaigns': 9,
        'original_report_run': REPORT_RUN, 'report_zip_sha256': REPORT_SHA256,
        'diagnostic_run': os.environ.get('GITHUB_RUN_ID'), 'commit': os.environ.get('GITHUB_SHA'),
        'elapsed_seconds_including_downloads': time.perf_counter()-started,
        'original_results_unchanged': True, 'new_application_attempts': 0,
        'unmetered_human_agent_cost': None})


if __name__ == '__main__':
    main()
