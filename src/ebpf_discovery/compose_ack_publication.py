"""Publish the completed correction's metadata, derived results and finite costs."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import json
import os
from pathlib import Path
import re
import time
import zipfile

from . import block_v6 as b
from . import compose_ack_repair as repair
from .compose_ack_recovery import frozen_inputs
from .publication_archive import GitHub, Release, file_digest, require
from .runtime import write_json


TARGET_RUN = 42769442057
TARGET_SOURCE = 'a53b45d510584b79e6a558945740a17a46bb0830'
RELEASE = 440020384
PRIOR_RUNS = (42682423732, 42682471264, 42684234727, 42684244053,
              42684834340, 42684842098, 42685244031, 42685277599,
              42768713295, 42768742396, 42768861689, 42768870755,
              42769114098, 42769121434, 42769408009)
ORIGINAL_LEDGER_SHA = '198cd5825bea33567353afb5166d552c9a2df963b8f4a86628122de82a4cbf3e'


def check_asset(actual, expected):
    require(all(actual.get(k) == expected[k] for k in ('id', 'name', 'size', 'digest', 'state')),
            'published asset identity differs')


def interval_seconds(job):
    if not job.get('started_at') or not job.get('completed_at'):
        return None
    start, end = (datetime.fromisoformat(job[n].replace('Z', '+00:00'))
                  for n in ('started_at', 'completed_at'))
    require(end >= start, 'negative worker interval')
    return (end - start).total_seconds()


def cost_census(github):
    ids = set(PRIOR_RUNS) | {TARGET_RUN}
    extra = github.pages('actions/workflows/checks.yml/runs?branch=report/ack-correction-publication', 'workflow_runs')
    extra += github.pages('actions/workflows/checks.yml/runs?head_sha=' + os.environ['GITHUB_SHA'], 'workflow_runs')
    ids.update(r['id'] for r in extra if r['path'] == '.github/workflows/checks.yml')
    rows, executions, unknown = [], {}, []
    for run_id in sorted(ids):
        run = github.json(f'actions/runs/{run_id}')
        jobs = github.pages(f'actions/runs/{run_id}/jobs?filter=all', 'jobs')
        rows.append({'workflow_API': run, 'jobs_API': jobs})
        for job in jobs:
            seconds = interval_seconds(job)
            if seconds is None:
                unknown.append({'run': run_id, 'job_id': job['id'], 'status': job['status']})
                continue
            key = (run_id, job['name'], job['head_sha'], job['started_at'], job['completed_at'])
            if key not in executions:
                executions[key] = {'run': run_id, 'name': job['name'], 'source': job['head_sha'],
                                   'started_at': job['started_at'], 'completed_at': job['completed_at'],
                                   'worker_seconds': seconds, 'API_alias_job_ids': []}
            executions[key]['API_alias_job_ids'].append(job['id'])
    require(file_digest('docs/v6-full108-completed-cost-ledger.json') == ORIGINAL_LEDGER_SHA,
            'original study cost ledger changed')
    return {'incremental_workflows': rows, 'unique_actual_worker_intervals': list(executions.values()),
            'known_incremental_worker_seconds': sum(v['worker_seconds'] for v in executions.values()),
            'unknown_intervals': unknown, 'human_seconds': None,
            'original_reused_study_cost_ledger': {'path': 'docs/v6-full108-completed-cost-ledger.json',
                                                'sha256': ORIGINAL_LEDGER_SHA},
            'nested_phase_seconds_are_not_added_to_worker_seconds': True,
            'complete_comparable_cost_comparison': False,
            'this_finalizer_and_later_delivery_CI_outside_finite_cut_are_not_zero': True}


def derived_statistics(summary):
    groups = defaultdict(list)
    direct_primary, direct_db, availability = [], [], []
    totals = defaultdict(int)
    keys = set()
    for case in summary['cases']:
        key, result = case['key'], case['result']
        require(tuple(key) not in keys and result['technical_complete'] is True, 'duplicate/incomplete replacement')
        keys.add(tuple(key))
        rows = result['rows']
        require(len(rows) == 24 and len({(r['operation'], r['source'], r['view']) for r in rows}) == 24,
                'replacement source/view census differs')
        for phase, n in result['all_retained_phase_counts'].items():
            totals[phase] += n
        for operation in repair.contract.OPERATIONS:
            selected = [r for r in rows if r['operation'] == operation]
            row = selected[0]
            for r in selected:
                require(all(r[n] == row[n] for n in ('observed', 'by_state', 'db_up', 'db_down',
                                                    'direct_baseline', 'direct_primary_error',
                                                    'direct_database_down_error')),
                        'source projections do not share the same measured operation outcomes')
            direct_primary.append({'key': [*key, operation], 'counts': row['observed'],
                                   'error': row['direct_primary_error']})
            direct_db.append({'key': [*key, operation], 'counts': row['db_down'],
                              'error': row['direct_database_down_error']})
        for row in rows:
            group = (key[1], key[3], row['source'], row['view'])
            groups[group].append(row)
        for source in ('ebpf', 'native', 'combined', 'context-baseline'):
            matching = [r for r in rows if r['source'] == source and r['view'] == 'raw']
            # Source names are copied from the actual generated result, not imputed.
            if matching:
                availability.append({'key': key, 'source': source,
                                     'operations': [r['operation'] for r in matching if r['primary_forecast']['available']]})
    require(len(keys) == 36 and totals['target'] == 345600 and totals['db_up'] == totals['db_down'] == 720 and
            totals['class_test'] == 21600 and totals['preparation'] == 1188, 'fixed replacement workload differs')
    expected = {('deathstarbench', mode, repetition, arm) for mode in ('absent', 'partial', 'full')
                for repetition in (9, 10, 11) for arm in repair.ARMS}
    require(keys == expected, 'registered 36-case matrix differs')
    def metrics(rows, field):
        values = [r[field]['worst_end_error'] for r in rows]
        known = [v for v in values if v is not None]
        return {'rows': len(rows), 'known': len(known), 'unknown': len(values) - len(known),
                'nonzero_errors': sum(v > 1e-12 for v in known), 'max_error': max(known, default=None)}
    comparisons = [{'mode': k[0], 'collector': k[1], 'source': k[2], 'view': k[3],
                    'primary': metrics(rows, 'primary_error'), 'database_down': metrics(rows, 'database_down_error')}
                   for k, rows in sorted(groups.items())]
    return {'fresh_cases': 36, 'case_operation_sets': 108, 'source_view_rows': 864,
            'all_retained_phase_counts': dict(totals), 'availability': availability,
            'comparison_by_mode_collector_source_view': comparisons,
            'direct_primary': direct_primary, 'direct_database_down': direct_db,
            'source_view_rows_reuse_outcomes_and_are_not_independent_repetitions': True,
            'first_attempt_36_aggregates_are_not_additional_raw_backed_repetitions': True,
            'unavailable_predictions_and_adverse_outcomes_retained': True,
            'write_or_durability_evidence': False}


def main():
    repair.record()
    origin = frozen_inputs()
    root = Path('work/ack-publication')
    root.mkdir(parents=True, exist_ok=True)
    started = time.time_ns()
    github, metadata = GitHub(), []
    release = Release(github, RELEASE)
    run = github.json(f'actions/runs/{TARGET_RUN}')
    require(run['head_sha'] == TARGET_SOURCE and run['conclusion'] == 'success' and run['status'] == 'completed',
            'all replacement targets and summary must complete before finalization')
    info = github.json(f'releases/{RELEASE}')
    require(info['target_commitish'] == TARGET_SOURCE and
            info['tag_name'] == 'compose-ack-correction-' + str(TARGET_RUN), 'foreign replacement Release')
    summaries = [a for a in release.assets.values() if re.fullmatch(r'prospective-results-attempt[0-9]+\.json', a['name'])]
    require(len(summaries) == 1, 'exact successful generated summary required')
    summary_asset = summaries[0]
    summary_path = root / summary_asset['name']
    repair.download_asset(github, summary_asset, summary_path)
    summary = b.read(summary_path)
    require(summary['source'] == TARGET_SOURCE and summary['run_id'] == str(TARGET_RUN) and
            summary['counts'] == {'fresh_cases': 36, 'case_operation_sets': 108, 'source_view_rows': 864},
            'foreign/incomplete generated summary')
    raw_publications = []
    for case in summary['cases']:
        asset = case['publication']
        check_asset(github.json(f"releases/assets/{asset['id']}"), asset)
        path = root / asset['name']
        repair.download_asset(github, asset, path)
        receipt = b.read(path)
        require(receipt['error'] is None and receipt['result'] == case['result'] and
                receipt['source'] == TARGET_SOURCE and receipt['run_id'] == str(TARGET_RUN) and
                receipt['result']['forecast_execution_source'] == origin['forecast_source'] and
                receipt['result']['forecast_execution_run_id'] == str(origin['forecast_run_id']),
                'canonical target receipt differs')
        raw = receipt['raw_data']
        assets = [raw['asset']] if 'asset' in raw else [p['asset'] for p in raw['parts']] + [raw['chunks_manifest_asset']]
        for published in assets:
            check_asset(github.json(f"releases/assets/{published['id']}"), published)
        stem = asset['name'][:-5]
        inventory = release.assets[stem + '.tar.gz.json']
        path = root / inventory['name']
        repair.download_asset(github, inventory, path)
        inventory_value = b.read(path)
        require(inventory_value['bytes'] == raw['original_bytes'] and
                inventory_value['sha256'] == raw['original_sha256'], 'raw archive inventory identity differs')
        classification = receipt['result']['full_classification_in_raw_capture']
        member = inventory_value['files'][classification['path']]
        require(member['bytes'] == classification['bytes'] and member['sha256'] == classification['sha256'] and
                {'external.json', 'status.json', 'closed-input.json', 'attempt-journal.sqlite'} <= set(inventory_value['files']),
                'complete capture/classification inventory differs')
        if 'parts' in raw:
            path = root / raw['chunks_manifest_asset']['name']
            repair.download_asset(github, raw['chunks_manifest_asset'], path)
            chunks = b.read(path)
            require(all(chunks[k] == raw[k] for k in ('original_bytes', 'original_sha256', 'parts')) and
                    sum(p['asset']['size'] for p in raw['parts']) == raw['original_bytes'],
                    'lossless chunk manifest differs')
            offset = 0
            for part in raw['parts']:
                require(part['offset'] == offset, 'chunk offsets do not cover the complete raw archive')
                offset += part['asset']['size']
        raw_publications.append({'key': case['key'], 'receipt': asset, 'raw': raw,
                                 'inventory_asset': repair.asset_identity(inventory)})
    for run_id in (origin['forecast_run_id'], TARGET_RUN):
        artifacts = github.pages(f'actions/runs/{run_id}/artifacts', 'artifacts')
        if run_id == origin['forecast_run_id']:
            require(len(artifacts) == 47, 'original metadata census differs')
        for artifact in artifacts:
            require(not artifact['expired'] and artifact['size_in_bytes'] < 4 * 1024**2 and
                    artifact['workflow_run']['id'] == run_id and
                    artifact['name'].startswith(('ack-correction-', 'ack-recovery-')) and
                    'failed-prefix' not in artifact['name'], 'nonqualified metadata artifact')
            old_name = f"prior-target-metadata-{artifact['id']}.zip"
            name = old_name if old_name in release.assets else f"correction-metadata-{artifact['id']}.zip"
            path = root / name
            github.download(f"actions/artifacts/{artifact['id']}/zip", path,
                            artifact['size_in_bytes'], artifact['digest'][7:])
            with zipfile.ZipFile(path) as archive:
                require(archive.testzip() is None, 'metadata ZIP CRC differs')
                members = archive.namelist()
            saved = release.publish(path)
            metadata.append({'original_artifact': artifact, 'archived_asset': repair.asset_identity(saved),
                             'members': members})
    costs = cost_census(github)
    statistics = derived_statistics(summary)
    report = {'study': repair.plan_name(), 'status': 'complete', 'capture_source': TARGET_SOURCE,
              'capture_run_id': TARGET_RUN, 'publication_source': os.environ['GITHUB_SHA'],
              'publication_run_id': os.environ['GITHUB_RUN_ID'], 'forecast_origin': origin,
              'generated_summary_asset': repair.asset_identity(summary_asset), 'statistics': statistics,
              'raw_publications': raw_publications, 'archived_metadata': metadata, 'costs': costs,
              'finalization_started_ns': started, 'finite_metadata_cut_ns': time.time_ns(),
              'primary_tar_bodies_downloaded_by_finalizer': 0,
              'original_108_archive_is_metadata_report_replay_not_full_raw_model_regeneration': True,
              'API_requests': github.calls}
    path = root / 'correction-publication.json'
    write_json(path, report)
    asset = release.publish(path)
    print(json.dumps({'report_asset': repair.asset_identity(asset), 'metadata_archives': len(metadata),
                      'statistics': {k: statistics[k] for k in ('fresh_cases', 'case_operation_sets', 'source_view_rows')},
                      'known_incremental_worker_seconds': costs['known_incremental_worker_seconds']}), flush=True)


if __name__ == '__main__':
    main()
