"""Extract existing edge witnesses; no discovery or contract modification.

Original Bering quality supplies the edge-to-ingested-file attribution. Selected
OTLP span records are illustrative file members, with the complete attribution
retained separately. A trace-parent witness is claimed only after exact IDs,
services and the parent relation have been checked. No request-level checkout
ancestry is inferred from membership in the common training prefix.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit

from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
import ijson


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def locate_reference(root, ref, replay=None, frozen_inputs=None):
    marker = '/toolchain/'
    if marker not in ref:
        return None
    rel = 'toolchain/' + ref.split(marker, 1)[1]
    path = (root / rel).resolve()
    if path.is_relative_to(root.resolve()) and path.is_file():
        return path
    # Portable model archives deliberately excluded toolchain/inputs. A replay
    # file can stand in for one only after matching its independently frozen SHA.
    if replay is not None and rel.startswith('toolchain/inputs/'):
        rebuilt = (replay / rel).resolve()
        expected = (frozen_inputs or {}).get(rel)
        if rebuilt.is_relative_to(replay.resolve()) and rebuilt.is_file() and expected and sha(rebuilt) == expected:
            return rebuilt
    return None


def iter_pb(path):
    from ebpf_discovery.observations import otlp
    request = ExportTraceServiceRequest()
    request.ParseFromString(path.read_bytes())
    document = MessageToDict(request)
    # OTLP protobuf JSON represents byte-valued IDs in base64.
    normalized = iter(otlp(document, 'ebpf', None, 'base64'))
    for ri, resource in enumerate(document.get('resourceSpans', [])):
        for si, scope in enumerate(resource.get('scopeSpans', [])):
            for pi, span in enumerate(scope.get('spans', [])):
                row = next(normalized)
                yield row, {'resourceSpans_index': ri, 'scopeSpans_index': si,
                            'spans_index': pi, 'resource': resource.get('resource', {}),
                            'scope': scope.get('scope', {}), 'span': span}


def candidate(row, edge):
    identity = edge.get('identity') or {}
    server = identity.get('span_kind') == 'server'
    if row['service'] != edge['to' if server else 'from']:
        return False
    kind = str(row.get('kind', '')).lower()
    allowed = ('2', 'span_kind_server', 'server') if server else ('3', 'span_kind_client', 'client')
    if kind not in allowed:
        return False
    attrs = row.get('attributes', {})
    protocol = identity.get('protocol')
    operation = identity.get('operation')
    if protocol == 'grpc':
        # Bering 66ca3af, inferDependencyOperation: child HTTP method/name
        # precedes its rpc.method/messaging.operation. rpc.service is not joined.
        observed = next((str(attrs[k]).strip() for k in
                         ('http.request.method', 'http.method')
                         if attrs.get(k) is not None and str(attrs[k]).strip()), '')
        if observed:
            observed = observed.upper()
        else:
            parts = str(row.get('name') or '').strip().split()
            if len(parts) >= 2 and parts[0].upper() in {
                    'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'}:
                observed = parts[0].upper()
            else:
                observed = next((str(attrs[k]).strip() for k in
                                 ('rpc.method', 'messaging.operation')
                                 if attrs.get(k) is not None and str(attrs[k]).strip()), '')
        # Parent-only operation inference remains outside this strict selector.
        # Its absence leaves a witness unresolved and never changes the graph.
        if observed != str(operation or '').strip():
            return False
    elif protocol == 'http':
        method = attrs.get('http.request.method', attrs.get('http.method'))
        route = attrs.get('http.route', attrs.get('url.path', attrs.get('http.target', attrs.get('url.full', attrs.get('http.url', '')))))
        if str(method).upper() != str(operation).upper() or urlsplit(str(route)).path != identity.get('route'):
            return False
    elif protocol == 'redis':
        method = next((str(attrs[k]).strip() for k in
                       ('db.operation.name', 'db.operation')
                       if attrs.get(k) is not None and str(attrs[k]).strip()), '')
        if method != str(operation or '').strip():
            return False
    elif operation:
        return False  # Leave an unimplemented token matcher explicitly unresolved.
    return True


def indexed_records(connection, row, capture):
    result = []
    for digest, raw, projected in connection.execute('''
        SELECT s.digest,s.data,COALESCE(a.projected_data,p.projected_data,s.data)
        FROM spans s LEFT JOIN runtime_identity_projection p ON p.digest=s.digest
        LEFT JOIN supplied_logical_alias_projection a ON a.digest=s.digest
        WHERE s.source='ebpf' AND s.trace=? AND s.span=? ORDER BY s.digest
        ''', (row['trace_id'], row['span_id'])):
        raw_record, effective = json.loads(raw), json.loads(projected)
        # The receiver observation must have the same temporal/content identity.
        if (raw_record.get('start_ns'), raw_record.get('end_ns')) != (row.get('start_ns'), row.get('end_ns')):
            continue
        locators = []
        for path, start, end, ordinal, segment in connection.execute('''
            SELECT raw_file,from_byte,through_byte,normalized_ordinal,segment_sha256
            FROM observation_provenance WHERE digest=? ORDER BY raw_file,from_byte,normalized_ordinal
            ''', (digest,)):
            raw_path = Path(path).resolve()
            if not raw_path.is_relative_to(capture.resolve()):
                raise ValueError('observation locator escapes retained capture')
            locators.append({'capture_member': raw_path.relative_to(capture).as_posix(),
                'from_byte': start, 'through_byte': end, 'normalized_ordinal': ordinal,
                'segment_sha256': segment,
                'verification': 'original capture member and full closed prefix verified before/after replay'})
        result.append({'observation_digest': digest, 'original_normalized_record': raw_record,
                       'effective_projected_record': effective, 'original_receiver_locators': locators})
    return result


def parent_records(connection, row, capture):
    if not row.get('parent_id'):
        return []
    records = []
    query = connection.execute('''SELECT COALESCE(a.projected_data,p.projected_data,s.data)
        FROM spans s LEFT JOIN runtime_identity_projection p ON p.digest=s.digest
        LEFT JOIN supplied_logical_alias_projection a ON a.digest=s.digest
        WHERE s.source='ebpf' AND s.trace=? AND s.span=? ORDER BY s.digest''',
        (row['trace_id'], row['parent_id']))
    for (encoded,) in query:
        parent = json.loads(encoded)
        records.extend(indexed_records(connection, parent, capture))
    return records


def extract_evidence(original, capture, evidence):
    prefix = 'toolchain/discovery/ebpf/network_scope/'
    binding = read(original / 'toolchain/ebpf/network_scope/checkout/binding.json')
    model = read(original / (prefix + 'observed.json'))
    quality = read(original / (prefix + 'observed.signal-quality.json'))
    required = binding['required_edges']
    if len(required) != 14:
        raise ValueError('archived checkout predicate does not contain the expected 14 edge IDs')
    edges = {edge['id']: edge for edge in model['edges']}
    observations = {item['entity_id']: item for item in quality.get('observation_evidence', [])
                    if item['entity_type'] == 'edge'}
    destination = evidence / 'edge-evidence'
    destination.mkdir(parents=True, exist_ok=True)
    source_hashes = {name: sha(original / name) for name in (
        prefix + 'observed.signal-quality.json', prefix + 'observed.snapshot.json',
        'toolchain/ebpf/network_scope/checkout/binding.json')}
    snapshot_path = original / (prefix + 'observed.snapshot.json')
    snapshot_edges = {}
    with snapshot_path.open('rb') as stream:
        for row in ijson.items(stream, 'discovery.edges.item', use_float=True):
            if row['id'] in required:
                snapshot_edges[row['id']] = row
    with gzip.open(destination / 'selected-original-snapshot-edges.json.gz', 'wt', encoding='utf-8') as stream:
        json.dump({'original_member': prefix + 'observed.snapshot.json',
                   'original_member_sha256': source_hashes[prefix + 'observed.snapshot.json'],
                   'selection': 'exact IDs in checkout binding.required_edges; fields unchanged',
                   'discovery_edges': snapshot_edges}, stream, ensure_ascii=False, indent=2)
    file_hashes = {}
    frozen_inputs = read(original / 'forecast-saved.json').get('complete_processing_sha256_by_path', {})
    connection = sqlite3.connect((capture / 'observation-index.sqlite').resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    results = []
    try:
        for number, edge_id in enumerate(required, 1):
            edge, item = edges[edge_id], observations.get(edge_id)
            calls = [call for call in binding['resolved_calls'] if edge_id in call['required_edge_ids']]
            record = {'number': number, 'edge_id': edge_id, 'edge': edge,
                'resolved_contract_calls': calls, 'original_quality_record': item,
                'quality_member': prefix + 'observed.signal-quality.json',
                'quality_member_sha256': source_hashes[prefix + 'observed.signal-quality.json'],
                'binding_member': 'toolchain/ebpf/network_scope/checkout/binding.json',
                'binding_member_sha256': source_hashes['toolchain/ebpf/network_scope/checkout/binding.json'],
                'quality_admission': {'exact_edge_ID_in_observed_model': edge_id in edges,
                    'exact_edge_ID_in_quality': item is not None,
                    'exact_edge_ID_in_snapshot': edge_id in snapshot_edges,
                    'exact_edge_ID_in_required_predicate': edge_id in required,
                    'resolved_contract_call_count': len(calls)},
                'membership_in_checkout_request_trace_claimed': False,
                'selection_scope': 'source-global frozen training prefix; operation-specific requirements supplied',
                'witness_status': 'no_selected_span_witness', 'file_attribution': []}
            refs = (item or {}).get('evidence', {}).get('relation', {}).get('sources', [])
            selected = None
            for ref in refs:
                path = locate_reference(original, ref.get('ref', ''), capture, frozen_inputs)
                if path is None:
                    record['file_attribution'].append({'source': ref, 'status': 'not_retained_in_selected_model'})
                    continue
                recovered_input = not path.is_relative_to(original.resolve())
                relative = path.relative_to(capture if recovered_input else original).as_posix()
                if relative not in file_hashes:
                    file_hashes[relative] = sha(path)
                file_ref = {'source': ref, 'model_member': relative, 'bytes': path.stat().st_size,
                            'sha256': file_hashes[relative],
                            'status': ('byte_identical_reconstructed_frozen_input' if recovered_input else
                                       'verified_from_pinned_model_archive'),
                            'independent_expected_sha256': frozen_inputs.get(relative) if recovered_input else None}
                record['file_attribution'].append(file_ref)
                # A Bering source attribution is retained even if a compact span
                # witness cannot be selected by these deliberately strict checks.
                if selected is not None or path.suffix != '.pb' or path.stat().st_size > 32_000_000:
                    continue
                for row, fragment in iter_pb(path):
                    if not candidate(row, edge):
                        continue
                    indexed = indexed_records(connection, row, capture)
                    if not indexed:
                        continue
                    parents = parent_records(connection, row, capture)
                    server = (edge.get('identity') or {}).get('span_kind') == 'server'
                    matching_parents = [r for r in parents if r['effective_projected_record'].get('service') == edge['from']]
                    if server and not matching_parents:
                        continue
                    selected = {'Bering_attributed_file': file_ref, 'decoded_wire_fragment': fragment,
                        'wire_normalized_record': row, 'original_receiver_records': indexed,
                        'matching_trace_parent_records': matching_parents,
                        'raw_source_is_original_receiver': True,
                        'wire_fragment_serialization': 'protobuf JSON field projection; file bytes located by SHA and member',
                        'checks': {'exact_trace_span_time_match_to_original_receiver': True,
                                   'edge_service_and_operation_match': True,
                                   'same_trace_parent_service_match': bool(matching_parents) if server else None},
                        'relation_scope': ('observed parent-child link' if server else
                                           'client dependency attributed by original Bering relation evidence')}
                    record['witness_status'] = 'verified_selected_span_and_receiver_locator'
                    break
            record['selected_span_witness'] = selected
            # Snapshot has the same edge IDs; retain its exact original member
            # separately instead of deleting long provenance from the source.
            record['snapshot_member'] = prefix + 'observed.snapshot.json'
            record['snapshot_member_sha256'] = source_hashes[prefix + 'observed.snapshot.json']
            write(destination / f'edge-{number:02d}.json', record)
            results.append(record)
    finally:
        connection.close()
    with (destination / 'required-edges.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['number', 'edge_id', 'from', 'to', 'protocol', 'operation',
            'span_kind', 'contract_call_ids', 'admission_policies', 'witness_status', 'evidence_file'])
        writer.writeheader()
        for record in results:
            edge = record['edge']
            writer.writerow({'number': record['number'], 'edge_id': record['edge_id'], 'from': edge['from'],
                'to': edge['to'], 'protocol': (edge.get('identity') or {}).get('protocol', ''),
                'operation': (edge.get('identity') or {}).get('operation', ''),
                'span_kind': (edge.get('identity') or {}).get('span_kind', ''),
                'contract_call_ids': ';'.join(call['obligation'].get('call_id', '') for call in record['resolved_contract_calls']),
                'admission_policies': ';'.join(sorted({call.get('path_resolution', {}).get('policy', '')
                                                     for call in record['resolved_contract_calls']})),
                'witness_status': record['witness_status'], 'evidence_file': f"edge-{record['number']:02d}.json"})
    summary = {'required_edges': len(required),
        'all_model_quality_binding_links_present': all(all(r['quality_admission'].values()) for r in results),
        'selected_span_witnesses': sum(r['selected_span_witness'] is not None for r in results),
        'unresolved_witness_edge_ids': [r['edge_id'] for r in results if r['selected_span_witness'] is None],
        'unresolved_witnesses_do_not_delete_archived_edges': True,
        'per_request_checkout_causality_claimed': False,
        'original_binding_and_quality_snapshot_retained': True}
    write(destination / 'summary.json', summary)
    return summary
