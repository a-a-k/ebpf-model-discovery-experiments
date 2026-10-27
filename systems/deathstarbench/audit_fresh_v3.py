"""Read-only, hash-admitted diagnosis of one retained fresh DSB campaign.

Run only in Actions. Saved projections and frozen automatic assignments are the
subjects of the audit; entry/observation rules are called only to distinguish
why a saved route could not be assigned. No model is fitted or selected here.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path

import ijson

from ebpf_discovery.observations import identifier, opaque_attempt
from ebpf_discovery.semantic_v3 import Binder
from ebpf_discovery.store_v3 import LimitedReader
from systems.deathstarbench.audit_qualification_v3 import ReadOnlyStore, digest, span_fact

SOURCES = ('ebpf', 'native')
PHASES = ('class_train', 'calibration', 'target', 'class_test')


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def require_hash(path: Path, expected: str):
    actual = digest(path)
    if actual != expected:
        raise ValueError(f'hash mismatch: {path}: {actual} != {expected}')
    return actual


def verify_acquisition_rules(marker: dict, repo: Path) -> dict:
    """Refuse to replay an acquisition with changed source interpretation."""
    required = {'src/ebpf_discovery/semantic_v3.py', 'src/ebpf_discovery/store_v3.py',
                'src/ebpf_discovery/observations.py', 'src/ebpf_discovery/model.py',
                'src/ebpf_discovery/timing_v3.py', 'systems/deathstarbench/contracts_v3.py'}
    recorded = marker.get('rule_sha256') or {}
    if not required.issubset(recorded):
        raise ValueError('acquisition marker lacks replayed rule hashes')
    return {name: require_hash(repo/name, recorded[name]) for name in sorted(required)}


def admit(full: Path, compact: Path, mode: str, seed: int, run_id: str) -> dict:
    metrics = read(compact/'metrics-v3.json')
    status = read(full/'status.json')
    saved = read(full/'forecast-saved.json')
    integrity = read(full/'freeze-integrity.json')
    marker = read(full/'acquisition-complete.json')
    repo = Path(__file__).resolve().parents[2]
    rule_hashes = verify_acquisition_rules(marker, repo)
    expected = ('deathstarbench', mode, seed, run_id)
    if (metrics['system'], metrics['mode'], metrics['seed'], str(metrics['run_id'])) != expected:
        raise ValueError('compact metrics identity mismatch')
    if (status['system'], status['mode'], status['seed'], str(status['run_id'])) != expected:
        raise ValueError('full status identity mismatch')
    if status['status'] != 'acquisition_complete' or marker['status'] != 'raw_acquisition_complete':
        raise ValueError('campaign not complete')
    if metrics['protocol_version'] != 'source-contract-v3' or status['protocol_version'] != 'source-contract-v3':
        raise ValueError('unexpected protocol')
    if metrics['application_deadline_seconds'] is not None or status['application_deadline_seconds'] is not None:
        raise ValueError('unexpected application deadline')
    if metrics['primary_population']['total'] != 34800 or marker['primary_attempts'] != 34800:
        raise ValueError('unexpected primary population')
    if not (metrics['acquisition_commit'] == status['commit'] == marker['commit']):
        raise ValueError('acquisition commit mismatch')
    if metrics['freeze']['saved_ns'] >= metrics['freeze']['target_started_ns']:
        raise ValueError('frozen prediction was not saved before target')
    if not integrity['all_unchanged'] or saved['sha256_by_path'] != integrity['sha256_by_path']:
        raise ValueError('frozen manifest differs')
    hashes = {}
    for name, expected_hash in integrity['sha256_by_path'].items():
        hashes[name] = require_hash(full/name, expected_hash)
        if (compact/name).exists():
            require_hash(compact/name, expected_hash)
    for name, expected_hash in (
        ('status.json', metrics['status_sha256']),
        ('external.json', metrics['external_sha256']),
        ('forecast-saved.json', metrics['freeze']['forecast_saved_sha256']),
        ('freeze-integrity.json', metrics['freeze']['freeze_integrity_sha256']),
    ):
        hashes[name] = require_hash(full/name, expected_hash)
        if (compact/name).exists():
            require_hash(compact/name, expected_hash)
    hashes['observation-index.sqlite'] = require_hash(full/'observation-index.sqlite', marker['index_sha256'])
    for source, inputs in metrics['source_inputs'].items():
        for field, name in (('model_sha256', f'models/{source}/model.json'),
                            ('forecast_sha256', f'models/{source}/forecast.json'),
                            ('projection_sha256', f'projections/{source}-final.json')):
            hashes[name] = require_hash(full/name, inputs[field])
    for name in ('metrics-v3.json', 'index-final.json', 'automatic-metrics.json',
                 'acquisition-complete.json', 'blocks.json'):
        if (compact/name).exists():
            hashes['compact/'+name] = digest(compact/name)
            if (full/name).exists():
                require_hash(full/name, hashes['compact/'+name])
    if read(full/'index-final.json').get('discard_policy') != (
            'only byte-equivalent normalized duplicates; conflicting observations retained'):
        raise ValueError('index reports discarded observations')
    return {'metrics': metrics, 'status': status, 'marker': marker,
            'hashes': hashes, 'rule_hashes': rule_hashes}


def classify(store: ReadOnlyStore, binder: Binder, row: dict, assignment: dict,
             classes: dict, source: str) -> tuple[str, dict | None, str, int]:
    ids = row['step_ids']
    if len(ids) != 1:
        raise ValueError('DSB operation must have exactly one declared step')
    identity = ids[0]
    anchors = store.candidates(source, identity) if identity else []
    if not anchors:
        return 'no_exact_dispatched_step_id', None, 'no_exact_id', 0
    # Automatic discovery deliberately has no declared-operation route filter.
    entry, reason = binder.entry(source, identity)
    if entry is None:
        return 'exact_id_but_entry_unbound_pre_window', None, reason, len(anchors)
    eligible, timing_reason, _ = binder.entry_window(entry, source, identity, row)
    if not eligible:
        return 'unique_entry_rejected_by_timing', entry, timing_reason, len(anchors)
    if assignment.get('class_id') is not None:
        return 'accepted_frozen_route_class', entry, timing_reason, len(anchors)
    signature = assignment.get('signature') or []
    if not signature or any(part is None for part in signature):
        category = 'accepted_but_missing_route_signature'
    elif not any(item.get('signature') == signature for item in classes.values()):
        category = 'accepted_but_novel_frozen_route_class'
    else:
        category = 'accepted_but_unassigned_frozen_route_class'
    return category, entry, timing_reason, len(anchors)


def raw_timestamps(path: Path, source: str, identities: set[tuple[str, str]],
                   consumed: int) -> dict:
    """Read all timestamp variants for selected IDs, only in the indexed prefix."""
    found = defaultdict(list)
    if not identities:
        return {}
    size = path.stat().st_size
    if not 0 <= consumed <= size:
        raise ValueError(f'invalid indexed prefix for {path}: {consumed}/{size}')
    with path.open('rb') as stream:
        indexed = LimitedReader(stream, consumed)
        if source == 'native' and path.name.startswith('traces-'):
            documents = ijson.items(indexed, 'data.item')
            for trace in documents:
                for span in trace.get('spans', []):
                    key = (str(span.get('traceID', '')).lower(), str(span.get('spanID', '')).lower())
                    if key in identities:
                        found[key].append({'format': 'jaeger', 'startTime_raw': span.get('startTime'),
                                      'duration_raw': span.get('duration'), 'raw_unit': 'microseconds',
                                      'normalized_start_ns_from_raw': int(span['startTime'])*1000,
                                      'normalized_end_ns_from_raw': (int(span['startTime'])+int(span['duration']))*1000})
        else:
            for document in ijson.items(indexed, '', multiple_values=True):
                payload = document.get('payload', document)
                encoding = document.get('id_encoding', 'hex')
                for resource in payload.get('resourceSpans', []):
                    for scope in resource.get('scopeSpans', resource.get('instrumentationLibrarySpans', [])):
                        for span in scope.get('spans', []):
                            key = (identifier(span.get('traceId'), encoding), identifier(span.get('spanId'), encoding))
                            if key in identities:
                                found[key].append({'format': 'otlp', 'startTimeUnixNano_raw': span.get('startTimeUnixNano'),
                                              'endTimeUnixNano_raw': span.get('endTimeUnixNano'), 'raw_unit': 'nanoseconds',
                                              'normalized_start_ns_from_raw': int(span.get('startTimeUnixNano', 0)),
                                              'normalized_end_ns_from_raw': int(span.get('endTimeUnixNano', 0))})
    return dict(found)


def timestamp_verdict(variants: list[dict], normalized_start: int, normalized_end: int,
                      *, tail_bytes: int) -> dict:
    pairs = Counter((item['normalized_start_ns_from_raw'], item['normalized_end_ns_from_raw'])
                    for item in variants)
    matches = pairs[(normalized_start, normalized_end)]
    if not variants:
        reason = 'not_in_indexed_prefix_tail_present' if tail_bytes else 'raw_exact_span_not_found_in_indexed_prefix'
    elif len(pairs) > 1:
        reason = 'ambiguous_same_id_timestamp_variants'
    elif matches:
        reason = 'unique_raw_timestamp_pair_matches_indexed_span'
    else:
        reason = 'indexed_prefix_timestamp_mismatch'
    return {'reason': reason, 'raw_occurrences_in_indexed_prefix': len(variants),
            'distinct_timestamp_pairs_in_indexed_prefix': len(pairs),
            'matching_pair_occurrences': matches, 'unindexed_tail_bytes': tail_bytes,
            'variants': [{'start_ns': start, 'end_ns': end, 'occurrences': count,
                          'raw_example': next(item for item in variants if
                              (item['normalized_start_ns_from_raw'], item['normalized_end_ns_from_raw']) == (start, end))}
                         for (start, end), count in sorted(pairs.items())]}


def attach_raw_timestamps(full: Path, witnesses: list[dict], consumed_by_original: dict[str, int]) -> None:
    grouped = defaultdict(set)
    paths = {}
    for witness in witnesses:
        fact = witness.get('raw_span')
        if not fact or not fact.get('raw_file'):
            continue
        raw = Path(fact['raw_file'])
        parts = raw.as_posix().split('/work/campaign/', 1)
        if len(parts) != 2:
            witness['raw_timestamp_check'] = {'reason': 'raw_path_not_in_campaign'}
            continue
        local = (full/parts[1]).resolve()
        if not local.is_relative_to(full.resolve()) or not local.is_file():
            witness['raw_timestamp_check'] = {'reason': 'raw_file_unavailable_in_artifact'}
            continue
        key = (fact['trace_id'], fact['span_id'])
        original = raw.as_posix()
        if original not in consumed_by_original:
            witness['raw_timestamp_check'] = {'reason': 'raw_file_not_in_indexed_file_manifest'}
            continue
        consumed = consumed_by_original[original]
        grouped[(local, fact['source'], consumed)].add(key)
        paths[id(witness)] = (local, fact['source'], consumed, key)
    lookups = {(local, source, consumed): raw_timestamps(local, source, ids, consumed)
               for (local, source, consumed), ids in grouped.items()}
    file_hashes = {local: digest(local) for local, _, _ in grouped}
    for witness in witnesses:
        address = paths.get(id(witness))
        if not address:
            continue
        local, source, consumed, key = address
        variants = lookups[(local, source, consumed)].get(key, [])
        fact = witness['raw_span']
        witness['raw_timestamp_check'] = {
            **timestamp_verdict(variants, fact['start_ns'], fact['end_ns'],
                                tail_bytes=local.stat().st_size-consumed),
            'raw_file_sha256': file_hashes[local], 'indexed_prefix_bytes': consumed}


def attach_client_receipts(full: Path, witnesses: list[dict]) -> None:
    """Use only client receipt timestamps, never external success or response bytes."""
    wanted = {item['attempt_key'] for item in witnesses}
    with (full/'external.json').open('rb') as stream:
        for record in ijson.items(stream, 'item'):
            key = opaque_attempt(record)
            if key not in wanted:
                continue
            steps = record.get('http_steps', [])
            receipt = steps[-1].get('body_completed_ns', steps[-1].get('ended_ns')) if steps else None
            for witness in witnesses:
                if witness['attempt_key'] == key:
                    witness['client_body_end_ns'] = receipt
                    witness['client_body_end_minus_cutoff_ns'] = (
                        receipt-witness['cutoff_ns'] if type(receipt) is int else None)


def audit(full: Path, compact: Path, mode: str, seed: int, run_id: str) -> dict:
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Retained campaign research diagnostics run in Actions only')
    admitted = admit(full, compact, mode, seed, run_id)
    store = ReadOnlyStore(full/'observation-index.sqlite')
    output = {'kind': 'retained_dsb_route_coverage_diagnostic', 'source_run_id': run_id,
              'mode': mode, 'seed': seed, 'audit_commit': os.environ.get('GITHUB_SHA'),
              'no_new_traffic_fitting_or_projection_regeneration': True,
              'input_sha256': admitted['hashes'],
              'acquisition_rule_sha256': admitted['rule_hashes'], 'sources': {},
              'interpretation': ('Missing exact dispatched ID means unavailable indexed evidence, not proven collector loss. '
                                 'Raw timestamp differences are descriptive; no clock tolerance is inferred.')}
    try:
        binder = Binder(store, 'deathstarbench')
        blocks = read(full/'blocks.json')
        consumed_by_original = {path: consumed for path, consumed in
            store.db.execute('SELECT path, consumed FROM files')}
        for source in SOURCES:
            rows = read(full/'projections'/f'{source}-final.json')
            assignment_path = full/'automatic'/source/'route'/'final-assignments.json'
            class_path = full/'automatic'/source/'route'/'classes.json'
            assigned = read(assignment_path)
            classes = read(class_path)
            output['input_sha256'][f'automatic/{source}/route/final-assignments.json'] = digest(assignment_path)
            output['input_sha256'][f'automatic/{source}/route/classes.json'] = digest(class_path)
            by_key = {item['attempt_key']: item for item in assigned}
            if len(rows) != admitted['marker']['all_attempts'] or len(by_key) != len(rows):
                raise ValueError('saved projection/assignment population mismatch')
            counts, by_phase, by_operation, by_block = (Counter(), defaultdict(Counter),
                                                        defaultdict(Counter), defaultdict(Counter))
            body_reasons, saved_binding_reasons, diagnostic_reasons = Counter(), Counter(), Counter()
            frozen_class_support = defaultdict(Counter)
            eligible = defaultdict(list)
            for row in rows:
                if row['phase'] not in PHASES:
                    continue
                key = row['attempt_key']
                assignment = by_key[key]
                category, entry, reason, anchor_count = classify(store, binder, row, assignment, classes, source)
                counts[category] += 1
                by_phase[row['phase']][category] += 1
                by_operation[row['operation_id']][category] += 1
                matching_blocks = [block['id'] for block in blocks if block['phase'] == row['phase']
                                   and block['load_started_ns'] <= row['started_ns'] <= block['ended_ns']]
                block_id = matching_blocks[0] if len(matching_blocks) == 1 else 'unmapped_or_ambiguous'
                by_block[block_id][category] += 1
                body_reasons[row.get('body_evidence', {}).get('reason', 'unspecified')] += 1
                saved_binding_reasons[row['steps'][0]['binding']] += 1
                diagnostic_reasons[(category, reason)] += 1
                frozen_class_support[row['phase']][assignment.get('class_id') or 'unknown'] += 1
                eligible[category].append((row['started_ns'], key, row, entry, reason, anchor_count, assignment))
            witnesses = []
            for category, items in sorted(eligible.items()):
                items.sort(key=lambda item: (item[0], item[1]))
                for position, index in (('early', 0), ('middle', len(items)//2), ('late', len(items)-1)):
                    _, key, row, entry, reason, anchor_count, assignment = items[index]
                    fact = span_fact(entry, row) if entry else None
                    if fact:
                        fact['raw_file'] = entry.get('raw_file')
                    raw_span = entry or next(iter(store.candidates(source, row['step_ids'][0])), None)
                    raw_fact = span_fact(raw_span, row) if raw_span else None
                    if raw_fact:
                        raw_fact['raw_file'] = raw_span.get('raw_file')
                    witnesses.append({'position': position, 'category': category, 'attempt_key': key,
                        'phase': row['phase'], 'operation': row['operation_id'], 'request_id': row['step_ids'][0],
                        'saved_binding': row['steps'][0]['binding'], 'diagnostic_reason': reason,
                        'exact_id_anchor_count': anchor_count, 'journal_start_ns': row['started_ns'],
                        'journal_end_ns': row['ended_ns'], 'cutoff_ns': row['deadline_ns'],
                        'observation_censored': row['observation_censored'],
                        'automatic_class_id': assignment.get('class_id'),
                        'automatic_signature': assignment.get('signature'), 'entry': fact,
                        'raw_span_role': 'entry' if entry else 'exact_id_anchor' if raw_span else 'none',
                        'raw_span': raw_fact})
            attach_raw_timestamps(full, witnesses, consumed_by_original)
            attach_client_receipts(full, witnesses)
            output['sources'][source] = {'primary_attempts': sum(counts.values()),
                'partition': dict(sorted(counts.items())),
                'by_phase': {k: dict(sorted(v.items())) for k, v in sorted(by_phase.items())},
                'by_operation': {k: dict(sorted(v.items())) for k, v in sorted(by_operation.items())},
                'by_block': {k: dict(sorted(v.items())) for k, v in sorted(by_block.items())},
                'saved_body_reasons': dict(sorted(body_reasons.items())),
                'saved_step_binding_reasons': dict(sorted(saved_binding_reasons.items())),
                'diagnostic_reasons': [{'category': category, 'reason': reason, 'n': count}
                    for (category, reason), count in sorted(diagnostic_reasons.items())],
                'frozen_route_classes': len(classes),
                'frozen_route_class_support_by_phase': {
                    k: dict(sorted(v.items())) for k, v in sorted(frozen_class_support.items())},
                'witnesses': witnesses,
                'witness_selection': 'first, middle, last by client start within source/category'}
        combined_path = full/'automatic/combined/route/final-assignments.json'
        combined_classes_path = full/'automatic/combined/route/classes.json'
        combined_rows = read(combined_path)
        combined_classes = read(combined_classes_path)
        output['input_sha256']['automatic/combined/route/final-assignments.json'] = digest(combined_path)
        output['input_sha256']['automatic/combined/route/classes.json'] = digest(combined_classes_path)
        combined_support = defaultdict(Counter)
        for row in combined_rows:
            if row['phase'] not in PHASES:
                continue
            combined_support[row['phase']][row.get('class_id') or 'unknown'] += 1
        output['sources']['combined'] = {
            'primary_attempts': sum(sum(v.values()) for v in combined_support.values()),
            'frozen_route_classes': len(combined_classes),
            'frozen_route_class_support_by_phase': {
                k: dict(sorted(v.items())) for k, v in sorted(combined_support.items())},
            'scope': 'saved class support only; source-local binding partitions are eBPF/native',
        }
        return output
    finally:
        store.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', type=Path, required=True)
    parser.add_argument('--compact', type=Path, required=True)
    parser.add_argument('--mode', choices=('absent', 'partial', 'full'), required=True)
    parser.add_argument('--seed', type=int, choices=(3, 4, 5), required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.full, args.compact, args.mode, args.seed, args.run_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
