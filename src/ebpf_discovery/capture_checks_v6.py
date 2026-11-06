"""Check the two explicitly declared capture epochs using retained source bytes."""
from __future__ import annotations

from collections import Counter
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from .evaluate_v4 import _completeness
from .plan_v6 import STUDY
from .study import workload_counts
from .study_v6 import declaration, verify_files


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def verify_preparation(root, closed, records, plans, expected):
    """Warmups are retained observations, separately proven by the closed journal."""
    if 'attempt-journal.sqlite' not in closed['files']:
        raise ValueError('preparation requires the sealed original attempt journal')
    preparation = [row for row in records if row.get('phase') == 'preparation']
    with closing(sqlite3.connect((root / 'attempt-journal.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)) as db:
        journal = {kind: [json.loads(row[0]) for row in db.execute(
            "SELECT data FROM events WHERE kind=? AND json_extract(data, '$.phase')='preparation' ORDER BY seq",
            (kind,))] for kind in ('attempt_intent', 'attempt_observed')}
    groups = [preparation, journal['attempt_intent'], journal['attempt_observed']]
    indices = []
    for rows in groups:
        ids = [row.get('attempt_id') for row in rows]
        if (len(ids) != expected or any(not isinstance(i, str) or not i for i in ids)
                or len(set(ids)) != expected):
            raise ValueError('preparation count or unique identities differ from the frozen protocol')
        indices.append(dict(zip(ids, rows)))
    external, intended, observed = indices
    if set(external) != set(intended) or external != observed:
        raise ValueError('preparation observations differ from the sealed journal')
    if set(external).intersection(row['attempt_id'] for row in plans):
        raise ValueError('preparation and scored identities overlap')
    for identity, row in external.items():
        if any(row.get(key) != intended[identity].get(key) for key in ('phase', 'operation', 'state')):
            raise ValueError('preparation phase/operation/state differs from its original intent')


def verify_capture(root, phase):
    root = Path(root).resolve()
    closed = read(root / 'closed-input.json')
    status = read(root / 'status.json')
    if (closed.get('study') != STUDY or closed.get('phase') != phase
            or status != closed.get('status') or status.get('study') != STUDY
            or status.get('phase') != phase or status.get('status') != 'capture_complete'
            or status.get('stage') not in ('qualification', 'main')
            or type(status.get('smoke')) is not bool):
        raise ValueError('inconsistent or incomplete fresh capture identity')
    verify_files(root, closed['files'])
    for folder in ('observations', 'native'):
        actual = {p.relative_to(root).as_posix() for p in (root / folder).rglob('*') if p.is_file()}
        expected = {p for p in closed['files'] if p.startswith(folder + '/')}
        if actual != expected:
            raise ValueError('unmanifested or missing capture input in ' + folder)
    runtime = root / 'runtime-identity-v5'
    for p in runtime.glob('capture-*'):
        if p.is_file() and p.relative_to(root).as_posix() not in closed['files']:
            raise ValueError('unmanifested runtime capture input')
    plans, records, census = [read(root / name) for name in ('plans.json', 'external.json', 'census.json')]
    declared = declaration(status['system'])
    count = workload_counts(len(declared.CONTRACTS), status['smoke'])
    if phase == 'training':
        expected = {'class_train': count['class_train'], 'calibration': 4 * count['calibration']}
        states = {s: 0 for s in ('11', '10', '01', '00')}
    else:
        expected = {'target': 8 * count['target'], 'class_test': count['class_test'],
                    'db_up': count['database'], 'db_down': count['database']}
        states = {s: count['target'] * n for s, n in [('11', 4), ('10', 2), ('01', 1), ('00', 1)]}
        if status['system'] == 'otel_demo':
            expected.update({name: count['async'] for name in ('async_normal', 'async_paused', 'async_recovered')})
    if (any(r.get('phase') not in expected for rows in (plans, census) for r in rows)
            or any(r.get('phase') not in {*expected, 'preparation'} for r in records)):
        raise ValueError('unexpected workload phase in closed capture')
    preparation_count = (5 if phase == 'training' else 11) * len(declared.CONTRACTS)
    if phase == 'validation' and status['system'] == 'otel_demo':
        preparation_count += 3  # One checkout warmup in each separate async block.
    verify_preparation(root, closed, records, plans, preparation_count)
    scored = [r for r in records if r['phase'] != 'preparation']
    complete = _completeness(scored, plans, census, expected_phases=expected,
                             expected_states=states, included_phases=set(expected))
    if not complete['valid']:
        raise ValueError('capture workload integrity failed: ' + ','.join(complete['problems']))
    by_id = {p['attempt_id']: p for p in plans}
    if any(r.get('operation') != by_id[r['attempt_id']].get('operation') for r in scored):
        raise ValueError('record and planned operation differ')
    for name, total in expected.items():
        rows = [r for r in records if r['phase'] == name]
        operations = ['checkout'] if name.startswith('async_') else list(declared.CONTRACTS)
        balanced = {op: total // len(operations) + (i < total % len(operations))
                    for i, op in enumerate(operations)}
        if dict(Counter(r['operation'] for r in rows)) != balanced:
            raise ValueError('unbalanced or foreign operation in ' + name)
        if name in ('target', 'calibration'):
            expected_states = states if name == 'target' else {s: count['calibration'] for s in states}
            for state, n in expected_states.items():
                values = Counter(r['operation'] for r in rows if r['state'] == state)
                if dict(values) != {op: n // len(operations) for op in operations}:
                    raise ValueError('operation/state workload imbalance')
    if phase == 'validation' and status['system'] == 'otel_demo':
        for name in ('async-normal-persistence.json', 'async-paused-snapshot.json',
                     'async-paused-after-resume.json', 'async-recovered-persistence.json'):
            if not (root / name).is_file() or name not in closed['files']:
                raise ValueError('missing sealed asynchronous evidence: ' + name)
    return closed
