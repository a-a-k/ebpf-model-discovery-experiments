"""Download two fixed immutable artifacts; no source or branch selection inputs."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile

from ebpf_discovery.checkpoint_diagnostic_v4 import DSB_SHUTDOWN_PROFILE, PROFILES
from ebpf_discovery.native_batch_equivalence_v4 import REFERENCE


if os.environ.get('GITHUB_ACTIONS') != 'true':
    raise SystemExit('This full-data preparation runs only in GitHub Actions')

root = Path('work/batch-proof/source-metadata')
root.mkdir(parents=True)
profile = PROFILES[DSB_SHUTDOWN_PROFILE]
checkpoint = {key: profile[key] for key in ('run_id', 'artifact_id', 'artifact_name', 'artifact_digest')}
checkpoint['run_sha'] = profile['commit']
repository = os.environ['GITHUB_REPOSITORY']
for label, expected, destination in (
        ('checkpoint', checkpoint, Path('work/original')),
        ('reference', REFERENCE, Path('work/reference-package'))):
    started = time.time_ns()
    metadata = {}
    try:
        for key, endpoint in (('run', 'runs/'+str(expected['run_id'])),
                              ('artifact', 'artifacts/'+str(expected['artifact_id']))):
            metadata[key] = json.loads(subprocess.check_output(['gh', 'api', f'repos/{repository}/actions/{endpoint}']))
            (root/(label+'-'+key+'.json')).write_text(json.dumps(metadata[key], indent=2)+'\n', encoding='utf-8')
        run, artifact = metadata['run'], metadata['artifact']
        if (run.get('id') != expected['run_id'] or run.get('head_sha') != expected['run_sha']
                or artifact.get('id') != expected['artifact_id'] or artifact.get('name') != expected['artifact_name']
                or artifact.get('digest') != expected['artifact_digest'] or artifact.get('expired') is True
                or artifact.get('workflow_run', {}).get('id') != expected['run_id']
                or artifact.get('workflow_run', {}).get('head_sha') != expected['run_sha']):
            raise ValueError('fixed Actions artifact identity mismatch: '+label)
        archive = Path('work')/(label+'.zip')
        with archive.open('wb') as output:
            subprocess.run(['/usr/bin/time', '-v', '-o', str(root/(label+'-download-time.txt')),
                'gh', 'api', f'repos/{repository}/actions/artifacts/{expected["artifact_id"]}/zip'],
                stdout=output, check=True)
        with archive.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if 'sha256:'+actual != expected['artifact_digest'] or archive.stat().st_size != artifact['size_in_bytes']:
            raise ValueError('downloaded fixed archive hash/length mismatch: '+label)
        if destination.exists():
            raise ValueError('artifact extraction destination must be fresh')
        with zipfile.ZipFile(archive) as source:
            names = set()
            for item in source.infolist():
                path = Path(item.filename)
                if (item.filename in names or path.is_absolute() or '..' in path.parts or '\\' in item.filename
                        or (item.external_attr >> 16) & 0o170000 == 0o120000):
                    raise ValueError('unsafe or duplicate source archive member')
                names.add(item.filename)
            source.extractall(destination)  # Every extracted member verifies ZIP CRC.
        proof = dict(expected, expired=False, full_archive_sha256_verified=True,
            full_archive_bytes=archive.stat().st_size, zip_crc_verified=True,
            run_status=run['status'], run_conclusion=run['conclusion'], run_url=run['html_url'])
        (root/(label+'-identity.json')).write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    finally:
        (root/(label+'-preparation-time.json')).write_text(json.dumps({
            'started_ns':started, 'ended_ns':time.time_ns(),
            'scope':'API metadata, download, full SHA and ZIP verification/extraction'}, indent=2)+'\n', encoding='utf-8')
