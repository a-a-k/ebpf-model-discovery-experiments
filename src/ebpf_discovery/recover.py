"""Complete a timed-out first evaluation; never reacquire data or refit a model."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from .evaluate import evaluate
from .runtime import write_json


def recover(root: Path):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Evaluation recovery runs in GitHub Actions')
    read = lambda name: json.loads((root/name).read_text())
    status = read('status.json')
    if status['status'] != 'acquisition_complete' or (root/'metrics.json').exists():
        raise RuntimeError('Recovery requires a completed acquisition without completed metrics')
    if read('parse-errors-final.json') or not (root/'normalized-final.json').is_file():
        raise RuntimeError('A complete, successfully parsed final snapshot is required')
    expected = {'class_train': 120, 'calibration': 960, 'target': 960, 'class_test': 120,
                'db_up': 20, 'db_down': 20}
    if status['system'] == 'otel_demo':
        expected.update(async_normal=20, async_paused=20, async_recovered=20)
    for name in ('external.json', 'census.json'):
        if Counter(r['phase'] for r in read(name)) != expected:
            raise RuntimeError(f'Incomplete acquisition records: {name}')
    blocks = read('blocks.json')
    if Counter(b['state'] for b in blocks if b['phase'] == 'calibration') != dict.fromkeys(('11', '10', '01', '00'), 1):
        raise RuntimeError('Incomplete calibration states')
    if Counter(b['state'] for b in blocks if b['phase'] == 'target') != {'11': 4, '10': 2, '01': 1, '00': 1}:
        raise RuntimeError('Incomplete target state mixture')
    commit = status['commit']
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise RuntimeError('Invalid acquisition commit')
    repository = Path(__file__).resolve().parents[2]
    subprocess.run(['git', 'fetch', '--depth=1', 'origin', commit], cwd=repository, check=True)
    versions = {}
    # These determine normalization, projection, class assignment and evaluation
    # mapping. Ancillary message-chain indexing may be repaired independently.
    for name in ('model.py', 'observations.py', 'evaluate.py'):
        relative = f'src/ebpf_discovery/{name}'
        original = subprocess.check_output(['git', 'show', f'{commit}:{relative}'], cwd=repository)
        current = (repository/relative).read_bytes()
        if original != current:
            raise RuntimeError(f'Acquisition evaluation code differs: {name}; explicit compatibility review required')
        versions[relative] = hashlib.sha256(original).hexdigest()
    protected = {}
    for source in ('ebpf', 'native', 'combined'):
        for name in ('model.json', 'forecast.json', 'evaluation-map.json',
                     'calibration-assignments.json', 'target-assignments.json'):
            path = root/'models'/source/name
            if not path.exists() and name == 'target-assignments.json':
                continue
            protected[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    evidence = {'status': 'started', 'acquisition_commit': commit,
                'recovery_commit': os.environ.get('GITHUB_SHA'),
                'purpose': 'first evaluation after timeout; no traffic and no model fitting',
                'identical_acquisition_evaluation_files': versions,
                'protected_input_sha256': protected}
    write_json(root/'evaluation-recovery.json', evidence)
    result = evaluate(root)
    for relative, digest in protected.items():
        if hashlib.sha256((root/relative).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f'Protected acquisition input changed: {relative}')
    evidence['status'] = 'completed'
    write_json(root/'evaluation-recovery.json', evidence)
    result['evaluation_recovery'] = evidence
    write_json(root/'metrics.json', result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    recover(parser.parse_args().out)
