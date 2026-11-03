"""Reject incomplete or misattributed closed-job evidence without scientific runs."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location(
    'closed_postcapture_saved_review', ROOT/'scripts/review-main-saved-facts-v5.py')
REVIEW = importlib.util.module_from_spec(spec)
spec.loader.exec_module(REVIEW)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def fixture(root):
    identity = {'run_id': '99', 'commit': REVIEW.CLOSED_POSTCAPTURE_HEAD,
        'system': 'otel_demo', 'collector': 'deepflow', 'controller': 'clean-study',
        'mode': 'absent', 'seed': 6, 'smoke': False}
    declaration = {**identity, 'head_sha': identity['commit'], 'run_id': 99}
    captured = {**identity, 'status': 'postcapture_complete'}
    write(root/'status.json', captured)
    for name, body in {'observation-index.sqlite': b'pre-mutation SQL',
            'attempt-journal.sqlite': b'pre-mutation journal',
            'attempt-journal.jsonl': b'pre-mutation journal export',
            'plans.json': b'{"operation": "unchanged"}',
            'toolchain/discovery/model.json': b'{"frozen": true}'}.items():
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    rows = [{'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
             'mode': 0o644, 'sha256': REVIEW.sha(path)}
            for path in sorted(root.rglob('*')) if path.is_file()]
    frozen = {'sha256_by_path': {'toolchain/discovery/model.json':
                               REVIEW.sha(root/'toolchain/discovery/model.json')}}
    folder = root/'infrastructure/postcapture'
    folder.mkdir(parents=True)
    (folder/'files.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows))
    write(folder/'capture-status.json', captured)
    sql = {'proof_basis': 'rowid-and-all-columns-v1', 'schema_sha256': '1'*64,
           'spans': {'rows': 1, 'sha256': '2'*64}}
    marker = {'schema': 'closed-otel-postcapture-v5', 'identity': identity,
        'sealing_run_id': '99', 'sealing_source': identity['commit'],
        'scientific_root': '/original/work/campaign',
        'directories': {'toolchain': 0o755, 'toolchain/discovery': 0o755},
        'files': len(rows), 'file_bytes': sum(row['bytes'] for row in rows),
        'file_inventory_sha256': REVIEW.sha(folder/'files.jsonl'),
        'capture_status_sha256': REVIEW.sha(folder/'capture-status.json'),
        'frozen_file_count': 1, 'training_SQL': sql,
        'journal_events': 1, 'journal_max_seq': 1,
        'journal_sha256': REVIEW.sha(root/'attempt-journal.sqlite'),
        'index_bytes': (root/'observation-index.sqlite').stat().st_size,
        'acquisition_closure': {'unresolved_transports': 0,
            'completeness': {'valid': True}, 'acquisition': {'valid': True}}}
    write(folder/'closed.json', marker)
    processing = {'identity': identity, 'status': 'complete', 'offline_only': True,
        'traffic_replay_or_model_refit': False, 'processing_run_id': '99',
        'processing_source': identity['commit'],
        'closed_manifest_sha256': REVIEW.sha(folder/'closed.json'),
        'input_file_inventory_sha256': marker['file_inventory_sha256']}
    write(folder/'processing.json', processing)
    artifact = {'id': 777, 'name': 'postcapture-v5-deepflow-main-otel_demo-absent-6-99',
        'expired': False, 'size_in_bytes': 100, 'digest': 'sha256:'+'3'*64,
        'workflow_run': {'id': 99, 'head_sha': identity['commit']}}
    write(folder/'artifact-api.json', artifact)
    host = root/'infrastructure/postcapture-host'
    guard = {'archive_bytes': 100, 'scientific_file_bytes': marker['file_bytes'],
        'proof_bytes': sum((folder/name).stat().st_size for name in
            ('closed.json', 'capture-status.json', 'files.jsonl')),
        'SQL_WAL_growth_reserve_bytes': 4*marker['index_bytes'],
        'scientific_limit_or_filter': False}
    guard['required_bytes'] = sum(guard[k] for k in ('archive_bytes',
        'scientific_file_bytes', 'proof_bytes', 'SQL_WAL_growth_reserve_bytes'))+1024**3
    guard['available_bytes'] = guard['required_bytes']+1
    write(host/'disk-before-download.json', guard)
    write(host/'restore.json', {'status': 'complete', 'artifact_id': 777,
        'artifact_digest': artifact['digest'], 'archive_bytes': 100,
        'archive_sha256': '3'*64, 'all_original_members_read_to_EOF_and_CRC_checked': True,
        'closed_manifest_sha256': processing['closed_manifest_sha256']})
    write(root/'infrastructure/guest-evidence-capture.json',
          {'campaign_root': marker['scientific_root']})
    remote = root/'infrastructure/remote-toolchain-v4'
    write(remote/'worker/output-manifest.json', {'toolchain_files': {}})
    parent = {'identity': {k: identity[k] for k in ('run_id', 'commit', 'system', 'mode', 'seed')},
        'worker_run_id': 888, 'worker_artifact_id': 999,
        'worker_artifact_digest': 'sha256:'+'4'*64, 'downloaded_archive_sha256': '4'*64}
    parent['identity']['manifest_sha256'] = '5'*64
    linked = {'schema_version': 'closed-discovery-import-hardlinks-v1',
        'identity': parent['identity'], 'immutable_subtree': 'toolchain/discovery/',
        'all_original_members_read_to_EOF': True,
        'output_manifest_sha256': REVIEW.sha(remote/'worker/output-manifest.json'),
        'worker_run_id': 888, 'worker_artifact_id': 999,
        'worker_artifact_digest': parent['worker_artifact_digest'],
        'archive_sha256': parent['downloaded_archive_sha256'],
        'linked_files': 0, 'duplicate_bytes_not_allocated': 0}
    write(remote/'closed-discovery-import-hardlinks.json', linked)
    # Final mutable bytes legitimately differ from the sealed pre-mutation state.
    write(root/'status.json', {**captured, 'status': 'acquisition_complete'})
    (root/'observation-index.sqlite').write_bytes(b'final SQL after ingest and refresh')
    (root/'attempt-journal.sqlite').write_bytes(b'final journal file')
    selected = {'artifact': {'name': 'campaign-v5-deepflow-main-otel_demo-absent-6-99'},
        'files': {name: {'bytes': (root/name).stat().st_size, 'sha256': REVIEW.sha(root/name)}
                  for name in ('status.json', 'plans.json', 'observation-index.sqlite')}}
    write(root/'evaluation-manifest.json', {'run_id': '99', 'commit': identity['commit'],
        'full_artifact_name': selected['artifact']['name'],
        'files_sha256': {'status.json': REVIEW.sha(root/'status.json')}})
    worker = {'parent_import': parent, 'output_manifest': {},
              'training_index_proof': {'parent_after_worker': sql}}
    return declaration, frozen, worker, selected


@pytest.mark.parametrize('mutation', ['none', 'foreign_capture', 'foreign_artifact',
    'processing_source', 'open_transport', 'wrong_SQL', 'duplicate_inventory',
    'frozen_claim', 'selected_immutable', 'qualified_publication', 'missing_restore',
    'restore_digest', 'guard_smallhost', 'worker_manifest', 'full6_replay', 'foreign_collector',
    'SQL_size_claim', 'proof_size_claim'])
def test_closed_job_requires_complete_same_source_chain_and_preserves_mutable_state(tmp_path, mutation):
    declaration, frozen, worker, selected = fixture(tmp_path)
    folder = tmp_path/'infrastructure/postcapture'
    target = None
    if mutation == 'foreign_capture': target, key, value = folder/'capture-status.json', 'commit', '0'*40
    if mutation == 'foreign_artifact':
        target, key, value = folder/'artifact-api.json', 'workflow_run', {'id': 100, 'head_sha': declaration['head_sha']}
    if mutation == 'processing_source': target, key, value = folder/'processing.json', 'processing_source', '0'*40
    if mutation == 'open_transport':
        target, key, value = folder/'closed.json', 'acquisition_closure', {
            'unresolved_transports': 1, 'completeness': {'valid': True}, 'acquisition': {'valid': True}}
    if mutation == 'qualified_publication': target, key, value = tmp_path/'evaluation-manifest.json', 'qualification_only', True
    if mutation == 'restore_digest': target, key, value = tmp_path/'infrastructure/postcapture-host/restore.json', 'archive_sha256', '0'*64
    if mutation == 'guard_smallhost':
        target = tmp_path/'infrastructure/postcapture-host/disk-before-download.json'
        key, value = 'available_bytes', 0
    if mutation == 'SQL_size_claim': target, key, value = folder/'closed.json', 'index_bytes', 1
    if mutation == 'proof_size_claim': target, key, value = tmp_path/'infrastructure/postcapture-host/disk-before-download.json', 'proof_bytes', 0
    if mutation == 'worker_manifest': target, key, value = tmp_path/'infrastructure/remote-toolchain-v4/closed-discovery-import-hardlinks.json', 'output_manifest_sha256', '0'*64
    if target:
        document = REVIEW.read(target); document[key] = value; write(target, document)
    if mutation == 'wrong_SQL':
        worker = copy.deepcopy(worker); worker['training_index_proof']['parent_after_worker']['spans']['rows'] = 2
    if mutation in ('duplicate_inventory', 'frozen_claim'):
        path = folder/'files.jsonl'; lines = path.read_text().splitlines()
        if mutation == 'duplicate_inventory': lines.append(lines[0])
        else:
            rows = [json.loads(line) for line in lines]
            next(row for row in rows if row['path'] in frozen['sha256_by_path'])['sha256'] = '0'*64
            lines = [json.dumps(row) for row in rows]
        path.write_text('\n'.join(lines)+'\n')
        marker = REVIEW.read(folder/'closed.json'); marker['file_inventory_sha256'] = REVIEW.sha(path)
        write(folder/'closed.json', marker)
        processing = REVIEW.read(folder/'processing.json')
        processing.update(closed_manifest_sha256=REVIEW.sha(folder/'closed.json'),
                          input_file_inventory_sha256=marker['file_inventory_sha256'])
        write(folder/'processing.json', processing)
        restored = REVIEW.read(tmp_path/'infrastructure/postcapture-host/restore.json')
        restored['closed_manifest_sha256'] = processing['closed_manifest_sha256']
        write(tmp_path/'infrastructure/postcapture-host/restore.json', restored)
    if mutation in ('open_transport', 'duplicate_inventory', 'frozen_claim', 'SQL_size_claim'):
        processing = REVIEW.read(folder/'processing.json')
        processing['closed_manifest_sha256'] = REVIEW.sha(folder/'closed.json')
        write(folder/'processing.json', processing)
        host = tmp_path/'infrastructure/postcapture-host'
        restored = REVIEW.read(host/'restore.json')
        restored['closed_manifest_sha256'] = processing['closed_manifest_sha256']
        write(host/'restore.json', restored)
        guard = REVIEW.read(host/'disk-before-download.json')
        guard['proof_bytes'] = sum((folder/name).stat().st_size for name in
            ('closed.json', 'capture-status.json', 'files.jsonl'))
        if mutation == 'SQL_size_claim': guard['SQL_WAL_growth_reserve_bytes'] = 4
        guard['required_bytes'] = sum(guard[k] for k in ('archive_bytes', 'scientific_file_bytes',
            'proof_bytes', 'SQL_WAL_growth_reserve_bytes'))+1024**3
        guard['available_bytes'] = guard['required_bytes']+1
        write(host/'disk-before-download.json', guard)
    if mutation == 'selected_immutable': selected['files']['plans.json']['sha256'] = '0'*64
    if mutation == 'missing_restore': (tmp_path/'infrastructure/postcapture-host/restore.json').unlink()
    if mutation == 'full6_replay': declaration.update(mode='full', seed=6)
    if mutation == 'foreign_collector': declaration['collector'] = 'coroot'
    if mutation == 'none':
        result = REVIEW.closed_postcapture_facts(tmp_path, declaration, frozen, worker, selected)
        assert result['closed_discovery_import']['linked_files'] == 0
        assert result['mutable_SQL_status_journal_not_compared_to_pre_mutation_file_bytes']
        assert result['all_frozen_claims_bound_to_pre_mutation_inventory']
        assert result['whole_case_memory_disk_headroom_or_six_hour_cure_proven'] is False
    else:
        with pytest.raises((ValueError, FileNotFoundError)):
            REVIEW.closed_postcapture_facts(tmp_path, declaration, frozen, worker, selected)
