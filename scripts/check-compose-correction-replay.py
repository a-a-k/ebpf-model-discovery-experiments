"""Replay only published correction metadata; Actions APIs and primary TARs are unused."""
import json
import os
from pathlib import Path
import time
import zipfile

from ebpf_discovery import block_v6 as b
from ebpf_discovery.compose_ack_publication import derived_statistics
from ebpf_discovery.compose_ack_repair import download_asset
from ebpf_discovery.publication_archive import GitHub, file_digest, require
from ebpf_discovery.runtime import write_json


require(os.environ.get('GITHUB_ACTIONS') == 'true', 'metadata replay runs in Actions')
started = time.time_ns()
root = Path('work/correction-report-replay')
root.mkdir(parents=True, exist_ok=True)
github = GitHub(replay=True)
report_path = root / 'correction-publication.json'
github.download('releases/assets/730638120', report_path, 1853057,
                'd69134c8bf4bc617d3ab5fbe8146617277c7b62cd425801a9c9a8b3928b57f44')
require(file_digest(report_path) == file_digest('results/correction-publication.json'), 'repository report differs')
report = b.read(report_path)
summary_asset = report['generated_summary_asset']
summary_path = root / summary_asset['name']
download_asset(github, summary_asset, summary_path)
require(derived_statistics(b.read(summary_path)) == report['statistics'], 'archive statistics replay differs')
require(len(report['archived_metadata']) == 85, 'fixed metadata closure differs')
for entry in report['archived_metadata']:
    asset = entry['archived_asset']
    require(asset['name'].endswith('.zip'), 'only metadata ZIPs are read by replay')
    path = root / asset['name']
    download_asset(github, asset, path)
    with zipfile.ZipFile(path) as archive:
        require(archive.namelist() == entry['members'] and archive.testzip() is None,
                'archived metadata member set or CRC differs')
    path.unlink()  # Verified temporary delivery copy; persistent Release is unchanged.
write_json(root / 'receipt.json', {
    'source': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
    'started_ns': started, 'ended_ns': time.time_ns(), 'status': 'success',
    'report_sha256': file_digest(report_path), 'summary_asset': summary_asset,
    'metadata_ZIPs_verified': 85, 'derived_statistics_equal': True,
    'live_Actions_API_requests': 0, 'primary_TAR_or_model_bodies_downloaded': 0,
    'API_requests': github.calls, 'whole_CI_worker_cost_is_outside_publication_finite_cut_not_zero': True})
print(json.dumps({'metadata_ZIPs_verified': 85, 'statistics_equal': True, 'Actions_API_requests': 0}), flush=True)
