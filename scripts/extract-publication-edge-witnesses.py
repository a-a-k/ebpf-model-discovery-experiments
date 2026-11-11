#!/usr/bin/env python3
"""Select archived edge witnesses after a successful historical replay.

No application, discovery, identity projection, contract resolution or simulator
is executed. Temporary SQLite rows contain locators for selecting existing
observations; they never form a new dependency model.
"""
from __future__ import annotations
import argparse
import copy
import csv
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
import zipfile
import requests

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('publication_archive_helpers', HERE / 'replay-publication-example.py')
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
require, read, write, digest = H.require, H.read, H.write, H.digest
require(digest(HERE / 'replay-publication-example.py') ==
        '6bea09a0310fdcc7d70c0aa60f51f01c2bed23aa5928ff85e7988d14a878a359',
        'archive helper differs from the independently reviewed main source')
MAIN = (13879962480, 18047490, '0cb833199266f63d6a9aa237c12878a61928268040e897887e70f55b92620606')
MAIN_RUN = 43063706864
MAIN_HEAD = '91c4a8334cea968c00da3f62c23b2f192cdc18e6'
MAIN_NAME = 'publication-example-replay-43063706864-attempt1'
SELECTOR_BLOB = '75fbd1908279af34245551519a33818c16d81dea'
SMALL_TOTAL = 512 * 1024**2
SMALL_MEMBER = 256 * 1024**2
PB_LIMIT = 32_000_000
MODEL_SELECTED = 2 * 1024**3
CAPTURE_SELECTED = 4 * 1024**3
INDEX_LIMIT = 512 * 1024**2
INDEX_ROWS = 2_000_000
OUTPUT_LIMIT = 32 * 1024**2
LINE_LIMIT = 32 * 1024**2
D = H.DISCOVERY
BINDING = H.OPERATIONS + 'checkout/binding.json'
QUALITY = D + 'observed.signal-quality.json'
MODEL = D + 'observed.json'


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def fingerprint(row):
    body = {k: v for k, v in row.items() if k != 'raw_file'}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def identity(row):
    return (row['trace_id'], row['span_id'], int(row['start_ns']), int(row['end_ns']))


def original_relative(ref):
    if '/toolchain/' not in ref:
        return None
    rel = 'toolchain/' + ref.split('/toolchain/', 1)[1]
    H.safe_name(rel)
    return rel


class SmallReader:
    def __init__(self, archive):
        self.archive, self.total = archive, 0
        names = archive.namelist()
        require(len(names) == len(set(names)), 'duplicate main-output ZIP member')
        for name in names:
            H.safe_name(name)

    def bytes(self, name, compressed=False):
        info = self.archive.getinfo(name)
        require(not info.is_dir() and info.file_size <= SMALL_MEMBER, 'oversized small member')
        incoming = self.archive.open(info)
        stream = gzip.GzipFile(fileobj=incoming) if compressed else incoming
        result = bytearray()
        try:
            while True:
                block = stream.read(min(1024**2, SMALL_MEMBER - len(result) + 1))
                if not block:
                    break
                self.total += len(block)
                require(len(result) + len(block) <= SMALL_MEMBER and self.total <= SMALL_TOTAL,
                        'bounded decompressed main-output read exceeded')
                result.extend(block)
        finally:
            stream.close()
            incoming.close()
        return bytes(result)

    def json(self, name, compressed=False):
        return json.loads(self.bytes(name, compressed))


def checked_run():
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    headers = {'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + str(token),
               'X-GitHub-Api-Version': '2022-11-28'}
    url = f'https://api.github.com/repos/{H.REPOSITORY}/actions/runs/{MAIN_RUN}'
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    run = response.json()
    require((run['id'], run['run_attempt'], run['head_sha'], run['status'], run['conclusion']) ==
            (MAIN_RUN, 1, MAIN_HEAD, 'completed', 'success'), 'main replay producing run differs')
    return {k: run[k] for k in ('id', 'run_attempt', 'head_sha', 'status', 'conclusion')}


def bootstrap(args, budget, receipt):
    receipt['main_run'] = checked_run()
    path = args.work / 'main-replay-output.zip'
    meta = H.github_artifact(*MAIN, budget, path)
    require(meta['name'] == MAIN_NAME and meta['workflow_run']['id'] == MAIN_RUN and
            meta['workflow_run']['head_sha'] == MAIN_HEAD, 'main artifact provenance differs')
    receipt['main_artifact'] = {k: meta[k] for k in ('id', 'name', 'size_in_bytes', 'digest')}
    receipt['main_zip'] = H.reference(path)
    evidence = args.out / 'evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    records = []
    with zipfile.ZipFile(path) as archive:
        reader = SmallReader(archive)
        core = reader.bytes('evidence/code-and-results.zip')
        require((len(core), hashlib.sha256(core).hexdigest()) == H.CORE, 'deposited core differs')
        (evidence / 'code-and-results.zip').write_bytes(core)
        freeze = reader.bytes('evidence/original-forecast-saved.json')
        require(hashlib.sha256(freeze).hexdigest() == H.FREEZE, 'original forecast freeze differs')
        (evidence / 'original-forecast-saved.json').write_bytes(freeze)
        saved = json.loads(freeze)
        require([saved['case'][k] for k in ('system', 'mode', 'seed', 'collector')] == H.KEY and
                saved['case']['commit'] == H.SOURCE and int(saved['case']['run_id']) == H.PRODUCER_RUN,
                'original case identity differs')
        verified = {}
        for rel in (MODEL, QUALITY, BINDING):
            name = 'evidence/original/' + rel
            gz = name not in archive.namelist()
            if gz:
                name += '.gz'
            body = reader.bytes(name, gz)
            sha = hashlib.sha256(body).hexdigest()
            require(sha == saved['sha256_by_path'].get(rel), 'original member SHA differs: ' + rel)
            verified[rel] = json.loads(body)
            retained = evidence / 'original' / (rel + ('.gz' if gz else ''))
            retained.parent.mkdir(parents=True, exist_ok=True)
            # Preserve the exact original compressed member; decompressed hash is separate.
            with archive.open(name) as source, retained.open('xb') as target:
                shutil.copyfileobj(source, target, 1024**2)
            receipt.setdefault('original_members', {})[rel] = {
                'uncompressed_bytes': len(body), 'original_sha256': sha,
                'retained_member': retained.relative_to(args.out).as_posix(),
                'retained_bytes_sha256': digest(retained), 'gzip': gz}
            del body
        binding, model, quality = verified[BINDING], verified[MODEL], verified[QUALITY]
        required = binding['required_edges']
        require(len(required) == 14 and len(set(required)) == 14, 'checkout predicate differs')
        edges = {e['id']: e for e in model['edges']}
        items = {r['entity_id']: r for r in quality.get('observation_evidence', [])
                 if r['entity_type'] == 'edge'}
        for number, edge_id in enumerate(required, 1):
            name = f'evidence/edge-evidence/edge-{number:02d}.json'
            body = reader.bytes(name)
            record = json.loads(body)
            calls = [c for c in binding['resolved_calls'] if edge_id in c['required_edge_ids']]
            require(record['edge_id'] == edge_id and record['edge'] == edges[edge_id] and
                    record['original_quality_record'] == items[edge_id] and
                    record['resolved_contract_calls'] == calls, 'retained edge evidence differs')
            require(record['binding_member_sha256'] == saved['sha256_by_path'][BINDING] and
                    record['quality_member_sha256'] == saved['sha256_by_path'][QUALITY] and
                    record['snapshot_member_sha256'] == saved['sha256_by_path'][D + 'observed.snapshot.json'],
                    'retained edge member hashes differ')
            record['inherited_evidence'] = {'artifact_id': MAIN[0], 'artifact_sha256': MAIN[2],
                'member': name, 'member_sha256': hashlib.sha256(body).hexdigest(),
                'json_locator': '$', 'raw_receiver_reverified_in_this_job': False}
            if record.get('selected_span_witness'):
                from publication_edge_evidence import candidate
                require(candidate(record['selected_span_witness']['wire_normalized_record'], record['edge']),
                        'inherited selected witness fails the corrected selector')
            records.append(record)
        for name in ('evidence/replay-comparison.json', 'evidence/edge-evidence/summary.json',
                     'evidence/edge-evidence/selected-original-snapshot-edges.json.gz'):
            body = reader.bytes(name)
            if name == 'evidence/replay-comparison.json':
                require(json.loads(body)['all_semantic_checks_passed'] is True,
                        'main replay did not match historical semantics')
            target = evidence / 'prior-extraction' / Path(name).name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        receipt['main_small_read'] = {'uncompressed_bytes_read': reader.total,
            'PB_members_retained': sum(n.endswith('.pb') for n in archive.namelist()),
            'complete_receiver_members_retained': sum(n.endswith(('observations/a.jsonl',
                'observations/b.jsonl')) for n in archive.namelist())}
    return saved, records


def sources(record):
    return (record.get('original_quality_record') or {}).get('evidence', {}).get('relation', {}).get('sources', [])


def file_plan(saved, records):
    portable = saved['sha256_by_path']
    complete = saved.get('complete_processing_sha256_by_path', {})
    by_sha = {}
    for rel, sha in portable.items():
        if rel.startswith(D) and rel.endswith('.pb'):
            by_sha.setdefault(sha, []).append(rel)
    plan = {}
    for record in records:
        for source in sources(record):
            rel = original_relative(source.get('ref', ''))
            if rel is None or not rel.endswith('.pb'):
                continue
            expected = portable.get(rel) or complete.get(rel)
            if expected is None:
                continue
            candidates = [rel] if rel in portable else sorted(by_sha.get(expected, []))
            for member in candidates[:1]:
                entry = plan.setdefault(member, {'sha256': expected, 'edges': {}})
                require(entry['sha256'] == expected, 'one PB member has conflicting expected hashes')
                entry['edges'].setdefault(record['edge_id'], []).append({
                    'source': source, 'source_original_member': rel,
                    'source_expected_sha256': expected,
                    'source_bytes_equal_selected_member': True,
                    'link_basis': 'same_frozen_member' if member == rel else
                                  'byte_identical_copy_anchored_in_frozen_processing_map'})
    return plan


def pb_row(row, fragment, rel):
    return (row['trace_id'], row['span_id'], row.get('parent_id') or '', row['service'],
            row['start_ns'], row['end_ns'], fingerprint(row), rel,
            fragment['resourceSpans_index'], fragment['scopeSpans_index'], fragment['spans_index'])


def parent_pairs(args, saved, records, budget, receipt, E):
    from ebpf_discovery.store_v3 import attribute_conflicts
    unsupported = [r for r in records if r.get('selected_span_witness') is None and
                   ((r['edge'].get('identity') or {}).get('span_kind') != 'server' or
                    (r['edge'].get('identity') or {}).get('protocol') != 'grpc')]
    for record in unsupported:
        record['followup_unresolved_reason'] = 'unsupported_witness_relation_kind'
    wanted = [r for r in records if r.get('selected_span_witness') is None and
              (r['edge'].get('identity') or {}).get('span_kind') == 'server' and
              (r['edge'].get('identity') or {}).get('protocol') == 'grpc']
    receipt['unsupported_unresolved_edges'] = [r['edge_id'] for r in unsupported]
    plan = file_plan(saved, wanted)
    receipt['archive_fallback_reason'] = {
        'unresolved_edges': [r['edge_id'] for r in wanted],
        'small_output_has_no_PB_members': receipt['main_small_read']['PB_members_retained'] == 0,
        'selected_wire_files': len(plan)}
    if not plan:
        return {}, {}
    package = args.work / 'original-model.zip'
    H.github_artifact(*H.MODEL, budget, package)
    folder = args.work / 'selected-model'
    receipt['model_package'] = H.unpack_package(package, 'model', folder,
                                               lambda n: n in plan, MODEL_SELECTED)
    package.unlink()
    available = receipt['model_package']['selected_files']
    for name, info in available.items():
        require(info['sha256'] == plan[name]['sha256'], 'model PB differs from frozen hash')
    missing = sorted(set(plan) - set(available))
    receipt['missing_planned_PB_members'] = missing
    db_path = args.work / 'edge-locators.sqlite'
    H.capacity(args.work, INDEX_LIMIT)
    db = sqlite3.connect(db_path)
    db.execute('PRAGMA cache_size=-16384')
    db.execute('PRAGMA temp_store=FILE')
    db.execute('PRAGMA max_page_count=131072')
    db.executescript('''
        CREATE TABLE locators(id INTEGER PRIMARY KEY,trace TEXT,span TEXT,parent TEXT,service TEXT,
          start INTEGER,end INTEGER,fingerprint TEXT,member TEXT,ri INTEGER,si INTEGER,pi INTEGER);
        CREATE INDEX identity_idx ON locators(trace,span);
        CREATE TABLE candidates(edge TEXT, locator INTEGER);
        CREATE INDEX candidate_idx ON candidates(edge);
    ''')
    count = 0
    parent_services = {r['edge']['from'] for r in wanted}
    by_id = {r['edge_id']: r for r in wanted}
    try:
        for file_number, rel in enumerate(sorted(available), 1):
            path = folder / rel
            if path.stat().st_size > PB_LIMIT:
                receipt.setdefault('oversized_PB_members_unread', []).append(rel)
                continue
            possible = {eid: by_id[eid] for eid in plan[rel]['edges']}
            for row, fragment in E.iter_pb(path):
                conflicts = (attribute_conflicts(fragment['resource'].get('attributes', [])) +
                             attribute_conflicts(fragment['span'].get('attributes', [])))
                if conflicts:
                    receipt['PB_records_with_conflicting_attributes_skipped'] = (
                        receipt.get('PB_records_with_conflicting_attributes_skipped', 0) + 1)
                    continue
                matches = [eid for eid, record in possible.items() if E.candidate(row, record['edge'])]
                if not matches and row['service'] not in parent_services:
                    continue
                count += 1
                require(count <= INDEX_ROWS, 'temporary locator row bound exceeded')
                cursor = db.execute('INSERT INTO locators VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)',
                                    pb_row(row, fragment, rel))
                db.executemany('INSERT INTO candidates VALUES (?,?)',
                               [(eid, cursor.lastrowid) for eid in matches])
            db.commit()
            require(db_path.stat().st_size <= INDEX_LIMIT, 'temporary locator byte bound exceeded')
            if file_number % 100 == 0:
                print(json.dumps({'stage': 'PB-locator-read', 'files': file_number, 'rows': count}), flush=True)
        selected, queries = {}, {}
        for edge_id, record in by_id.items():
            query = db.execute('''
              SELECT c.*,p.id,p.trace,p.span,p.parent,p.service,p.start,p.end,p.fingerprint,
                     p.member,p.ri,p.si,p.pi
              FROM candidates x JOIN locators c ON c.id=x.locator
              JOIN locators p ON c.trace=p.trace AND c.parent=p.span
              WHERE x.edge=? AND p.service=? AND c.parent!=''
                AND (SELECT COUNT(DISTINCT z.fingerprint) FROM locators z
                     WHERE z.trace=c.trace AND z.span=c.span)=1
                AND (SELECT COUNT(DISTINCT z.fingerprint) FROM locators z
                     WHERE z.trace=p.trace AND z.span=p.span)=1
              ORDER BY c.member,c.ri,c.si,c.pi,p.member,p.ri,p.si,p.pi LIMIT 10000
            ''', (edge_id, record['edge']['from']))
            examined = 0
            for joined in query:
                examined += 1
                child, parent = joined[:12], joined[12:]
                # Both files must occur in this edge's original Bering attribution.
                c_refs = plan[child[8]]['edges'].get(edge_id, [])
                p_refs = plan[parent[8]]['edges'].get(edge_id, [])
                domain_pairs = [(c, p) for c in c_refs for p in p_refs
                    if c['source'].get('domain') and c['source'].get('domain') == p['source'].get('domain')]
                if not domain_pairs:
                    continue
                selected[edge_id] = {'child_locator': child, 'parent_locator': parent,
                    'child_source_link': domain_pairs[0][0], 'parent_source_link': domain_pairs[0][1]}
                break
            queries[edge_id] = {'candidate_parent_pairs_examined': examined,
                               'pair_selected': edge_id in selected, 'query_pair_limit': 10000}
        receipt['locator_selection'] = {'rows': count, 'bytes': db_path.stat().st_size,
            'purpose': 'selection of archived records only; no dependency model built', 'edges': queries}
    finally:
        db.close()
    # Decode just the selected exact locators and verify their normalized hashes.
    targets = {}
    for eid, pair in selected.items():
        for role in ('child', 'parent'):
            loc = pair[role + '_locator']
            targets.setdefault(loc[8], {}).setdefault(tuple(loc[9:12]), []).append((eid, role, loc))
    for rel, coordinates in targets.items():
        for row, fragment in E.iter_pb(folder / rel):
            key = tuple(fragment[k] for k in ('resourceSpans_index', 'scopeSpans_index', 'spans_index'))
            for eid, role, loc in coordinates.get(key, []):
                require(fingerprint(row) == loc[7], 'selected PB locator changed')
                selected[eid][role] = {'wire_normalized_record': row, 'decoded_wire_fragment': fragment,
                    'model_member': rel, 'model_member_sha256': available[rel]['sha256'],
                    'model_member_bytes': available[rel]['bytes'],
                    'source_link': selected[eid][role + '_source_link']}
    for eid in list(selected):
        if not all(role in selected[eid] for role in ('child', 'parent')):
            del selected[eid]
    return selected, plan


def retained_receivers(records, keys):
    found = {key: [] for key in keys}
    for record in records:
        witness = record.get('selected_span_witness') or {}
        for field in ('original_receiver_records', 'matching_trace_parent_records'):
            for index, item in enumerate(witness.get(field, [])):
                row = item.get('original_normalized_record') or {}
                if not all(k in row for k in ('trace_id', 'span_id', 'start_ns', 'end_ns')):
                    continue
                key = identity(row)
                if key in found:
                    copied = copy.deepcopy(item)
                    copied['reused_receiver_evidence'] = {
                        **record['inherited_evidence'],
                        'json_locator': f'$.selected_span_witness.{field}[{index}]',
                        'verification': 'inherited from hash-verified completed replay output'}
                    found[key].append(copied)
    return found


def selected_raw_fragment(document, ordinal):
    payload = document.get('payload', document)
    current = 0
    for ri, resource_record in enumerate(payload.get('resourceSpans', [])):
        scopes = resource_record.get('scopeSpans', resource_record.get('instrumentationLibrarySpans', []))
        for si, scope in enumerate(scopes):
            for pi, span in enumerate(scope.get('spans', [])):
                if current == ordinal:
                    return {'resourceSpans_index': ri, 'scopeSpans_index': si, 'spans_index': pi,
                            'resource': resource_record.get('resource', {}),
                            'scope': scope.get('scope', scope.get('instrumentationLibrary', {})),
                            'span': span,
                            'receiver_wrapper': {k: document[k] for k in
                                ('raw_ref', 'raw_sha256', 'content_type', 'content_encoding', 'id_encoding')
                                if k in document}}
                current += 1
    raise ValueError('selected normalized ordinal has no raw OTLP fragment')


def receiver_evidence(args, saved, selected, records, budget, receipt):
    from ebpf_discovery.store_v3 import normalized_file, complete_prefix
    keys = {identity(pair[role]['wire_normalized_record'])
            for pair in selected.values() for role in ('child', 'parent')}
    found = retained_receivers(records, keys)
    missing = {k for k, values in found.items() if not values}
    receipt['receiver_selection'] = {'wanted_exact_id_time_keys': len(keys),
        'keys_available_in_small_output': len(keys) - len(missing),
        'original_receiver_stream_required': bool(missing)}
    if not missing:
        return found
    package = args.work / 'original-capture.zip'
    H.github_artifact(*H.TRAINING, budget, package)
    folder = args.work / 'selected-capture'
    wanted = {'closed-input.json', 'status.json', 'observations/a.jsonl', 'observations/b.jsonl'}
    receipt['capture_package'] = H.unpack_package(package, 'capture', folder,
                                                 lambda n: n in wanted, CAPTURE_SELECTED)
    package.unlink()
    require(digest(folder / 'closed-input.json') == saved['training_closed_input_sha256'],
            'receiver capture closure differs from historical model')
    closed = read(folder / 'closed-input.json')
    require(closed['phase'] == 'training', 'receiver capture is not training')
    status = closed['status']
    require([status[k] for k in ('system', 'mode', 'seed', 'collector')] == H.KEY and
            status['commit'] == H.SOURCE and int(status['run_id']) == H.PRODUCER_RUN,
            'receiver capture case identity differs')
    scanned = []
    for rel in ('observations/a.jsonl', 'observations/b.jsonl'):
        path = folder / rel
        if not path.is_file():
            continue
        full_sha = digest(path)
        require(full_sha == closed['files'].get(rel), 'original receiver member changed')
        limit = complete_prefix(path)
        offset, ordinal_total, selected_count = 0, 0, 0
        with path.open('rb') as stream:
            while offset < limit:
                line = stream.readline(min(LINE_LIMIT + 1, limit - offset))
                require(line.endswith(b'\n') and len(line) <= LINE_LIMIT,
                        'receiver line exceeds explicit complete-document bound')
                end = offset + len(line)
                decoded = None
                for ordinal, row in enumerate(normalized_file(path, 'ebpf', offset, end,
                                                              same_trace_parents=True)):
                    ordinal_total += 1
                    key = identity(row)
                    if key not in missing:
                        continue
                    if decoded is None:
                        decoded = json.loads(line)
                    entry = {'observation_digest': fingerprint(row), 'original_normalized_record': row,
                        'effective_projected_record': None,
                        'original_receiver_locators': [{'capture_member': rel, 'from_byte': offset,
                            'through_byte': end, 'normalized_ordinal': ordinal,
                            'ordinal_scope': 'this exact JSONL document',
                            'segment_sha256': hashlib.sha256(line).hexdigest(),
                            'capture_member_sha256': full_sha, 'capture_member_bytes': path.stat().st_size,
                            'closed_input_sha256': saved['training_closed_input_sha256'],
                            'verification': 'full pinned capture ZIP/TAR/member and frozen closure verified'}],
                        'decoded_original_receiver_fragment': selected_raw_fragment(decoded, ordinal)}
                    # Preserve conflicting variants; equivalent repeated exports share one
                    # record with bounded locators and an explicit omitted-locator count.
                    same = next((r for r in found[key] if r.get('observation_digest') ==
                                 entry['observation_digest']), None)
                    if same is not None:
                        if len(same['original_receiver_locators']) < 32:
                            same['original_receiver_locators'].extend(entry['original_receiver_locators'])
                        else:
                            same['additional_equivalent_receiver_locators_omitted'] = (
                                same.get('additional_equivalent_receiver_locators_omitted', 0) + 1)
                    else:
                        require(len(found[key]) < 32, 'receiver variants exceed output bound')
                        found[key].append(entry)
                    selected_count += 1
                offset = end
        scanned.append({'member': rel, 'member_sha256': full_sha, 'through_byte': limit,
                        'normalized_records_read': ordinal_total, 'selected_records': selected_count})
    receipt['receiver_selection']['scanned_members'] = scanned
    receipt['receiver_selection']['keys_without_receiver'] = [list(k) for k, v in found.items() if not v]
    return found


def finish_records(args, records, selected, receivers, receipt):
    destination = args.out / 'evidence/edge-evidence'
    destination.mkdir(parents=True, exist_ok=True)
    for record in records:
        pair = selected.get(record['edge_id'])
        if pair:
            child, parent = pair['child'], pair['parent']
            crows, prows = receivers.get(identity(child['wire_normalized_record']), []), receivers.get(
                identity(parent['wire_normalized_record']), [])
            record['followup_observed_pair'] = {'child': child, 'parent': parent,
                'receiver_match_counts': {'child': len(crows), 'parent': len(prows)},
                'pair_scope': 'same-domain exact trace-parent IDs and services; no checkout request claim'}
            if crows and prows:
                record['selected_span_witness'] = {
                    'Bering_attributed_file': child['source_link'],
                    'model_member': child['model_member'],
                    'model_member_sha256': child['model_member_sha256'],
                    'decoded_wire_fragment': child['decoded_wire_fragment'],
                    'wire_normalized_record': child['wire_normalized_record'],
                    'original_receiver_records': crows,
                    'matching_trace_parent_records': prows,
                    'parent_wire_evidence': parent,
                    'raw_source_is_original_receiver': True,
                    'wire_fragment_serialization': 'protobuf JSON field projection',
                    'checks': {'exact_trace_span_time_match_to_original_receiver': True,
                        'edge_service_and_operation_match': True,
                        'same_trace_parent_service_match': True,
                        'child_and_parent_repeated_attribute_conflicts_absent': True,
                        'child_and_parent_files_in_original_edge_source_refs': True,
                        'source_ref_hash_equals_selected_original_member_hash': True},
                    'relation_scope': 'observed parent-child link within original source domain',
                    'prepared_wire_and_raw_receiver_fields_retained_separately': True}
                record['witness_status'] = 'verified_selected_span_and_receiver_locator'
                record['inherited_evidence']['raw_receiver_reverified_in_this_job'] = all(
                    'reused_receiver_evidence' not in r for r in [*crows, *prows])
            else:
                record['followup_unresolved_reason'] = 'observed PB pair lacks an exact original receiver match'
        elif record.get('selected_span_witness') is None:
            record.setdefault('followup_unresolved_reason',
                              'no attributed literal-operation parent-child pair selected')
        write(destination / f"edge-{record['number']:02d}.json", record)
    fields = ['number', 'edge_id', 'from', 'to', 'protocol', 'operation', 'span_kind',
              'contract_call_ids', 'admission_policies', 'witness_status', 'evidence_file']
    with (destination / 'required-edges.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in records:
            edge = record['edge']
            ident = edge.get('identity') or {}
            writer.writerow({'number': record['number'], 'edge_id': record['edge_id'],
                'from': edge['from'], 'to': edge['to'], 'protocol': ident.get('protocol', ''),
                'operation': ident.get('operation', ''), 'span_kind': ident.get('span_kind', ''),
                'contract_call_ids': ';'.join(c['obligation'].get('call_id', '') for c in record['resolved_contract_calls']),
                'admission_policies': ';'.join(sorted({c.get('path_resolution', {}).get('policy', '')
                                                     for c in record['resolved_contract_calls']})),
                'witness_status': record['witness_status'], 'evidence_file': f"edge-{record['number']:02d}.json"})
    summary = {'required_edges': len(records),
        'all_model_quality_binding_links_present': all(all(r['quality_admission'].values()) for r in records),
        'selected_span_witnesses': sum(r.get('selected_span_witness') is not None for r in records),
        'unresolved_witness_edge_ids': [r['edge_id'] for r in records if r.get('selected_span_witness') is None],
        'new_selected_archival_pairs': len(selected),
        'per_request_checkout_causality_claimed': False,
        'unresolved_witnesses_do_not_delete_archived_edges': True,
        'archived_model_contract_predicates_or_forecasts_changed': False,
        'primary_semantic_replay_run': MAIN_RUN,
        'primary_semantic_replay_status': 'matched',
        'selector_git_blob': SELECTOR_BLOB,
        'receiver_verification_scope': 'per record; inherited verification explicitly marked'}
    write(destination / 'summary.json', summary)
    receipt['edge_evidence'] = summary
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--historical', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.historical, args.work, args.out = [p.resolve() for p in (args.historical, args.work, args.out)]
    require(os.environ.get('GITHUB_ACTIONS') == 'true', 'archive processing is GitHub Actions only')
    for path in (args.work, args.out):
        path.mkdir(parents=True, exist_ok=True)
    sys.path[:0] = [str(args.historical / 'src'), str(args.historical)]
    require(subprocess.check_output(['git', '-C', str(args.historical), 'rev-parse', 'HEAD'],
            text=True).strip() == H.SOURCE, 'historical reader source differs')
    require(not subprocess.check_output(['git', '-C', str(args.historical), 'diff', '--name-only'],
            text=True).strip(), 'historical source has local edits')
    require(git_blob((HERE / 'publication_edge_evidence.py').read_bytes()) == SELECTOR_BLOB,
            'corrected edge selector differs from reviewed blob')
    import publication_edge_evidence as E
    started, cpu = time.time_ns(), os.times()
    receipt = {'status': 'running', 'started_ns': started, 'human_seconds': None,
        'human_cost_status': 'unmeasured', 'environment': H.environment(args),
        'new_capture_or_model_execution': False, 'identity_projection_executed': False,
        'historical_source': H.SOURCE, 'reader': H.reference(Path(__file__)),
        'selector': H.reference(HERE / 'publication_edge_evidence.py'),
        'bounds': {'new_archive_downloads_collective': H.ARCHIVE_DOWNLOAD_BUDGET,
            'small_decompressed_reads': SMALL_TOTAL, 'selected_model_members': MODEL_SELECTED,
            'selected_capture_members': CAPTURE_SELECTED, 'one_PB': PB_LIMIT,
            'locator_index': INDEX_LIMIT, 'reader_output': OUTPUT_LIMIT}}
    path = args.out / 'edge-extraction-receipt.json'
    budget = H.DownloadBudget(args.out / 'download-budget.json')
    write(path, receipt)
    failed = False
    try:
        saved, records = bootstrap(args, budget, receipt)
        finish_records(args, records, {}, {}, receipt)
        write(path, receipt)
        selected, plan = parent_pairs(args, saved, records, budget, receipt, E)
        write(path, receipt)
        receivers = receiver_evidence(args, saved, selected, records, budget, receipt)
        summary = finish_records(args, records, selected, receivers, receipt)
        receipt['status'] = 'completed' if not summary['unresolved_witness_edge_ids'] else 'completed_with_unknowns'
        require(sum(p.stat().st_size for p in args.out.rglob('*') if p.is_file()) <= OUTPUT_LIMIT,
                'bounded extraction output exceeded')
    except Exception as exc:
        failed = True
        receipt.update(status='failed', error_type=type(exc).__name__)
        # Exception strings from network libraries may include signed URLs.
        # Preserve stack locations only, without arguments, source lines or locals.
        frames = [{'file': f.filename, 'line': f.lineno, 'function': f.name}
                  for f in traceback.extract_tb(exc.__traceback__)]
        write(args.out / 'edge-extraction-error.json',
              {'error_type': type(exc).__name__, 'stack_locations': frames[-30:]})
    finally:
        now = os.times()
        receipt.update(ended_ns=time.time_ns(), elapsed_seconds=(time.time_ns() - started) / 1e9,
            cpu_seconds={'user': now.user - cpu.user, 'system': now.system - cpu.system},
            max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            disk_free_bytes=shutil.disk_usage(args.work).free)
        budget.save()
        write(path, receipt)
        print(json.dumps({'stage': 'archival-edge-extraction', 'status': receipt['status'],
                          'edge_evidence': receipt.get('edge_evidence')}), flush=True)
    return 1 if failed else (2 if receipt['status'] == 'completed_with_unknowns' else 0)


if __name__ == '__main__':
    raise SystemExit(main())
