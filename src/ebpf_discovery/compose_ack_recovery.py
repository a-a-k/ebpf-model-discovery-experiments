"""Reuse exact pre-target forecasts after the first raw-publication failure."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

from . import block_v6 as b
from . import compose_ack_repair as repair
from .publication_archive import GitHub, Release, file_digest, require
from .runtime import write_json


INPUTS = Path('docs/compose-ack-frozen-inputs.json')


def frozen_inputs():
    value = b.read(INPUTS)
    require(value['plan_sha256'] == file_digest(repair.PLAN) and
            value['contract_source_sha256'] == file_digest('src/ebpf_discovery/compose_ack_contract.py') and
            len(value['freeze_assets']) == 9 and len(value['prior_target_metadata_artifacts']) == 36 and
            value['replacement_scope']['all_cases'] == 36,
            'recovery cannot change the registered forecasts, contracts or complete replacement scope')
    for name, sha in value['unchanged_runtime_files'].items():
        require(file_digest(name) == sha, 'recovery changed original runtime/oracle/classification source: ' + name)
    return value


def prepare(github, root):
    started = time.time_ns()
    origin = frozen_inputs()
    plan = repair.record()
    source_run = github.json(f"actions/runs/{origin['forecast_run_id']}")
    require(source_run['head_sha'] == origin['forecast_source'] and source_run['status'] == 'completed' and
            source_run['path'] == '.github/workflows/compose-ack-correction.yml', 'foreign original forecast run')
    jobs = github.pages(f"actions/runs/{origin['forecast_run_id']}/jobs?filter=all", 'jobs')
    freezes = [j for j in jobs if j['name'].startswith('freeze ')]
    barriers = [j for j in jobs if j['name'] == 'barrier']
    require(len(freezes) == 9 and len(barriers) == 1 and
            all(j['conclusion'] == 'success' for j in freezes + barriers), 'original prospective freeze incomplete')
    repair.prepare(github, root)
    release = Release(github, b.read(root / 'release.json')['id'])
    old_release = github.json(f"releases/{origin['forecast_release_id']}")
    require(old_release['target_commitish'] == origin['forecast_source'] and
            old_release['tag_name'] == 'compose-ack-correction-' + str(origin['forecast_run_id']),
            'foreign original forecast release')
    barrier = origin['barrier_asset']
    barrier_path = root / 'original-prospective-barrier.json'
    repair.download_asset(github, barrier, barrier_path)
    value = b.read(barrier_path)
    require(value['execution_source'] == origin['forecast_source'] and
            value['execution_run_id'] == str(origin['forecast_run_id']) and
            value['plan_sha256'] == file_digest(repair.PLAN) and value['all_36_forecasts_before_any_target'] is True,
            'original forecast barrier provenance differs')
    expected = {tuple(block['key']): block for block in plan['blocks']}
    require({tuple(row['key']) for row in value['blocks']} == set(expected) and len(value['blocks']) == 9,
            'original barrier block census differs')
    registered_assets = {a['id']: a for a in origin['freeze_assets']}
    require({r['asset']['id'] for r in value['blocks']} == set(registered_assets), 'original freeze asset census differs')
    for row in value['blocks']:
        require(row['asset'] == registered_assets[row['asset']['id']], 'original freeze asset identity differs')
        path = root / row['asset']['name']
        repair.download_asset(github, row['asset'], path)
        frozen = repair.read_freeze(path, expected[tuple(row['key'])], source=origin['forecast_source'],
                                    run_id=origin['forecast_run_id'])
        require(row['saved_ns'] == frozen['saved_ns'] < value['saved_ns'] < started,
                'original prospective freeze clocks differ')
        path.unlink()  # Verified disposable download; original Release remains immutable.
    # Persist every first-attempt aggregate and its original exact ZIP/API identity.
    # They remain measured but lack independently replayable raw capture evidence.
    prior = []
    for registered in origin['prior_target_metadata_artifacts']:
        actual = github.json(f"actions/artifacts/{registered['id']}")
        require(all(actual[k] == registered[k] for k in ('id', 'name', 'size_in_bytes', 'digest', 'workflow_run')) and
                not actual['expired'], 'first-attempt metadata publication differs')
        path = root / f"prior-target-metadata-{actual['id']}.zip"
        github.download(f"actions/artifacts/{actual['id']}/zip", path, actual['size_in_bytes'], actual['digest'][7:])
        saved = release.publish(path)
        prior.append({'original_artifact': actual, 'archived_asset': repair.asset_identity(saved),
                      'raw_capture_missing': True, 'canonical_replacement_selected_before_accuracy_inspection': True})
    proof = {'source': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
             'forecast_origin': origin, 'verification_started_ns': started, 'verified_ns': time.time_ns(),
             'all_9_original_freezes_verified_before_any_replacement_target': True,
             'no_new_discovery_or_forecast_compilation': True,
             'first_attempt_metadata': prior, 'original_workflow_API': source_run, 'original_job_API': jobs,
             'API_requests': github.calls, 'human_seconds': None,
             'later_prepare_and_delivery_costs_are_not_zero': True}
    path = root / 'recovery-input-verification.json'
    write_json(path, proof)
    release.publish(path)
    repair.output(barrier_asset_id=barrier['id'], barrier_bytes=barrier['size'],
                  barrier_sha256=barrier['digest'][7:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare',))
    parser.parse_args()
    repair.record()
    root = Path('work/ack-correction').resolve()
    root.mkdir(parents=True, exist_ok=True)
    prepare(GitHub(), root)


if __name__ == '__main__':
    main()
