"""Graph-v5 observation index with lossless duplicate provenance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3

from .store_v3 import ObservationStore, normalized_file
from .runtime_identity_v5 import _locator, resolve


def _digest(row: dict) -> str:
    evidence = {key: value for key, value in row.items() if key != 'raw_file'}
    encoded = json.dumps(evidence, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


class ObservationStoreV5(ObservationStore):
    """Retain every original occurrence even when normalized content deduplicates."""

    def __init__(self, path, *, same_trace_parents=False):
        super().__init__(path, same_trace_parents=same_trace_parents)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS observation_provenance (
            digest TEXT NOT NULL, raw_file TEXT NOT NULL, from_byte INTEGER NOT NULL,
            through_byte INTEGER NOT NULL, normalized_ordinal INTEGER NOT NULL,
            segment_sha256 TEXT NOT NULL,
            PRIMARY KEY(digest,raw_file,from_byte,through_byte,normalized_ordinal));
          CREATE INDEX IF NOT EXISTS observation_provenance_digest_idx
            ON observation_provenance(digest);
          CREATE TABLE IF NOT EXISTS runtime_identity_projection (
            digest TEXT PRIMARY KEY, stage TEXT NOT NULL, status TEXT NOT NULL,
            original_service TEXT, projected_service TEXT, projected_data TEXT,
            resolution TEXT NOT NULL, inventory_path TEXT NOT NULL,
            inventory_sha256 TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS supplied_logical_alias_projection (
            digest TEXT PRIMARY KEY, original_service TEXT NOT NULL,
            logical_service TEXT NOT NULL, projected_data TEXT NOT NULL,
            origin TEXT NOT NULL, admission_sha256 TEXT NOT NULL);
        ''')

    def ingest(self, observation_root, native_root):
        result = super().ingest(observation_root, native_root)
        for item in result['files']:
            path = Path(item['path'])
            start, end = item['from_byte'], item['through_byte']
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                stream.seek(start)
                remaining = end - start
                while remaining:
                    chunk = stream.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise ValueError(f'observation segment shortened while locating provenance: {path}')
                    digest.update(chunk)
                    remaining -= len(chunk)
            segment_sha256 = digest.hexdigest()
            for ordinal, row in enumerate(normalized_file(
                    path, item['source'], start, end,
                    same_trace_parents=self.same_trace_parents)):
                self.db.execute(
                    'INSERT OR IGNORE INTO observation_provenance VALUES (?,?,?,?,?,?)',
                    (_digest(row), str(path), start, end, ordinal, segment_sha256))
        self.db.commit()
        result['provenance_occurrences'] = self.db.execute(
            'SELECT COUNT(*) FROM observation_provenance').fetchone()[0]
        result['duplicate_policy'] = (
            'content-identical normalized observations deduplicated in spans; '
            'every original occurrence retained in observation_provenance')
        return result

    def _with_provenance(self, sql, params=()):
        output = []
        for digest, encoded in self.db.execute(sql, params):
            row = json.loads(encoded)
            row['_observation_digest'] = digest
            row['_observation_provenance'] = [
                {'raw_file': raw_file, 'from_byte': start, 'through_byte': end,
                 'normalized_ordinal': ordinal, 'segment_sha256': segment}
                for raw_file, start, end, ordinal, segment in self.db.execute(
                    '''SELECT raw_file,from_byte,through_byte,normalized_ordinal,segment_sha256
                       FROM observation_provenance WHERE digest=?
                       ORDER BY raw_file,from_byte,normalized_ordinal''', (digest,))]
            output.append(row)
        return output

    @staticmethod
    def _effective_sql(where):
        return ("SELECT s.digest,COALESCE(a.projected_data,p.projected_data,s.data) FROM spans s "
                "LEFT JOIN runtime_identity_projection p ON p.digest=s.digest "
                "LEFT JOIN supplied_logical_alias_projection a ON a.digest=s.digest " + where)

    def candidates_v5(self, source, request_id):
        return self._with_provenance(
            self._effective_sql('WHERE s.source=? AND s.request=? ORDER BY s.digest'),
            (source, request_id))

    def observation_v5(self, digest):
        rows = self._with_provenance(
            self._effective_sql('WHERE s.digest=?'), (digest,))
        return rows[0] if len(rows) == 1 else None

    def _effective_records(self, where, params=()):
        return [json.loads(row[0]) for row in self.db.execute(
            "SELECT COALESCE(a.projected_data,p.projected_data,s.data) FROM spans s "
            "LEFT JOIN runtime_identity_projection p ON p.digest=s.digest "
            "LEFT JOIN supplied_logical_alias_projection a ON a.digest=s.digest " + where, params)]

    def apply_supplied_logical_aliases(self, admission, *, scoped_digest_aliases=None):
        """Create an immutable effective logical-role view; original rows remain unchanged."""
        from .supplied_alias_v5 import admission_sha256
        aliases = admission.get('aliases') or {}
        scoped = (admission.get('scoped_digest_aliases') or {}
                  if scoped_digest_aliases is None else scoped_digest_aliases)
        admission_sha = admission_sha256(admission)
        applied = 0
        for digest, encoded in self.db.execute('SELECT digest,data FROM spans ORDER BY digest'):
            original = json.loads(encoded)
            raw = original.get('service')
            logical = aliases.get(raw)
            if not logical or logical == raw or scoped.get(digest) != logical:
                continue
            runtime = self.db.execute(
                'SELECT status,projected_data,resolution FROM runtime_identity_projection '
                'WHERE digest=?', (digest,)).fetchone()
            projected = dict(original)
            reconciled_runtime_conflict = False
            if runtime and runtime[0] == 'label_conflict':
                resolution = json.loads(runtime[2])
                if resolution.get('observed_runtime_compose_service') != logical:
                    continue
                reconciled_runtime_conflict = True
            elif runtime and runtime[1]:
                projected = json.loads(runtime[1])
            projected['service'] = logical
            projected['_supplied_logical_alias'] = {
                'raw_service': raw, 'logical_service': logical,
                'origin': 'supplied_deployment_inventory_alias',
                'physical_identity_inferred': False, 'graph_edges_injected': False,
                'runtime_label_conflict_reconciled': reconciled_runtime_conflict}
            projected_encoded = json.dumps(
                projected, sort_keys=True, separators=(',', ':'), allow_nan=False)
            existing = self.db.execute(
                'SELECT original_service,logical_service,projected_data,origin,admission_sha256 '
                'FROM supplied_logical_alias_projection WHERE digest=?', (digest,)).fetchone()
            value = (raw, logical, projected_encoded,
                     'supplied_deployment_inventory_alias', admission_sha)
            if existing is None:
                self.db.execute(
                    'INSERT INTO supplied_logical_alias_projection VALUES (?,?,?,?,?,?)',
                    (digest, *value))
            elif existing != value:
                raise ValueError('training-frozen supplied logical alias changed')
            applied += 1
        self.db.commit()
        return {'rows': applied, 'origin': 'supplied_deployment_inventory_alias',
                'training_rows_immutable': True, 'raw_observations_unchanged': True,
                'same_table_all_sources_and_direct_baseline': True}

    def verify_supplied_logical_aliases(self, admission):
        """Verify the frozen effective rows without mutating a worker checkpoint."""
        from .supplied_alias_v5 import admission_sha256
        expected_sha = admission_sha256(admission)
        aliases = admission.get('aliases') or {}
        scoped = admission.get('scoped_digest_aliases') or {}
        actual = {digest: (raw, logical, projected, origin, sha)
                  for digest, raw, logical, projected, origin, sha in self.db.execute(
                      'SELECT digest,original_service,logical_service,projected_data,origin,'
                      'admission_sha256 FROM supplied_logical_alias_projection')}
        expected_digests = set()
        for digest, encoded in self.db.execute('SELECT digest,data FROM spans ORDER BY digest'):
            original = json.loads(encoded)
            raw, logical = original.get('service'), aliases.get(original.get('service'))
            if not logical or logical == raw or scoped.get(digest) != logical:
                continue
            runtime = self.db.execute(
                'SELECT status,resolution FROM runtime_identity_projection WHERE digest=?',
                (digest,)).fetchone()
            if (runtime and runtime[0] == 'label_conflict'
                    and json.loads(runtime[1]).get('observed_runtime_compose_service') != logical):
                continue
            expected_digests.add(digest)
            row = actual.get(digest)
            if (row is None or row[0] != raw or row[1] != logical
                    or row[3] != 'supplied_deployment_inventory_alias' or row[4] != expected_sha):
                raise ValueError('frozen supplied logical projection row differs from admission')
            projected = json.loads(row[2])
            if (projected.get('service') != logical
                    or (projected.get('_supplied_logical_alias') or {}).get('raw_service') != raw):
                raise ValueError('frozen supplied logical projection payload is inconsistent')
        if set(actual) != expected_digests:
            raise ValueError('frozen supplied logical projection membership differs from admission')
        return {'rows': len(actual), 'admission_sha256': expected_sha,
                'logical_projection_verified': True, 'mutation_performed': False}

    def candidates(self, source, request_id):
        return self._effective_records('WHERE s.source=? AND s.request=?', (source, request_id))

    def identity(self, source, trace, span):
        return self._effective_records('WHERE s.source=? AND s.trace=? AND s.span=?',
                                       (source, trace, span))

    def trace_v5(self, source, trace):
        return self._effective_records('WHERE s.source=? AND s.trace=? ORDER BY s.digest',
                                       (source, trace))

    def descendants(self, root):
        source, trace = root['source'], root['trace_id']
        queue, seen, output = [root], set(), []
        while queue:
            row = queue.pop()
            sid = row['span_id']
            if sid in seen:
                continue
            seen.add(sid)
            variants = self.identity(source, trace, sid)
            if len(variants) != 1 or row.get('attribute_conflicts'):
                continue
            output.append(row)
            queue.extend(self._effective_records(
                'WHERE s.source=? AND s.trace=? AND s.parent=?', (source, trace, sid)))
        return output

    def apply_runtime_identity(self, retained_inventory, out, *, inventory_proof, stage):
        from tempfile import NamedTemporaryFile
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        counts = {'resolved_enriched': 0, 'resolved_existing': 0,
                  'label_conflict': 0, 'unknown': 0}
        rows, temporary = 0, None
        try:
            with NamedTemporaryFile(mode='w', encoding='utf-8', dir=out.parent,
                                    prefix=out.name + '.', suffix='.pending', delete=False) as stream:
                temporary = Path(stream.name)
                for row in self._runtime_identity_rows(
                        retained_inventory, inventory_proof=inventory_proof,
                        stage=stage, counts=counts):
                    stream.write(json.dumps(row, sort_keys=True) + '\n')
                    rows += 1
            self.db.commit()
            temporary.replace(out)
            temporary = None
        except BaseException:
            self.db.rollback()
            raise
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        with out.open('rb') as stream:
            output_sha256 = hashlib.file_digest(stream, 'sha256').hexdigest()
        return {'rows': rows, 'counts': counts, 'path': str(out),
                'sha256': output_sha256, 'training_rows_immutable': True}

    def _runtime_identity_rows(self, retained_inventory, *, inventory_proof, stage, counts):
        for digest, encoded in self.db.execute('SELECT digest,data FROM spans ORDER BY digest'):
            original = json.loads(encoded)
            result = resolve(original, retained_inventory)
            original_service = original.get('service')
            projected, projected_service, status = None, None, result['status']
            if result['status'] == 'resolved':
                observed = result['service_identity']['compose_service']
                if original_service in (None, '', 'unknown'):
                    projected = dict(original)
                    projected['service'] = observed
                    projected_service, status = observed, 'resolved_enriched'
                elif original_service == observed:
                    status = 'resolved_existing'
                else:
                    status = 'label_conflict'
                    projected = dict(original)
                    conflicts = list(projected.get('attribute_conflicts') or [])
                    conflicts.append({
                        'key': 'service.name',
                        'raw_values': [
                            {'stringValue': original_service, 'origin': 'source_observation'},
                            {'stringValue': observed, 'origin': 'verified_runtime_identity'},
                        ],
                        'basis': 'source_label_conflicts_with_verified_runtime_identity',
                    })
                    projected['attribute_conflicts'] = conflicts
                    projected['_runtime_identity_uncertainty'] = {
                        'kind': 'service_identity_conflict',
                        'original_source_service': original_service,
                        'observed_runtime_compose_service': observed,
                        'admissible_service_identity': None,
                    }
                    result = {**result, 'status': 'unknown', 'service_identity': None,
                              'unknown_reasons': ['existing_source_label_conflicts_with_runtime_identity'],
                              'observed_runtime_compose_service': observed,
                              'original_source_service': original_service}
            else:
                status = 'unknown'
            result = {**result, 'inventory_proof': dict(inventory_proof)}
            counts[status] += 1
            record = {'digest': digest, 'stage': stage, 'status': status,
                      'original_service': original_service, 'projected_service': projected_service,
                      'original_data_sha256': hashlib.sha256(encoded.encode()).hexdigest(),
                      'projected_data_sha256': (hashlib.sha256(json.dumps(projected, sort_keys=True,
                          separators=(',', ':'), allow_nan=False).encode()).hexdigest() if projected else None),
                      'resolution': result, 'inventory': inventory_proof,
                      'raw_observation_unchanged': True, 'graph_edges_injected': False}
            existing = self.db.execute(
                'SELECT status,projected_data,resolution,inventory_sha256 FROM runtime_identity_projection '
                'WHERE digest=?', (digest,)).fetchone()
            projected_encoded = (json.dumps(projected, sort_keys=True, separators=(',', ':'),
                                             allow_nan=False) if projected else None)
            resolution_encoded = json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False)
            if existing is None:
                self.db.execute('INSERT INTO runtime_identity_projection VALUES (?,?,?,?,?,?,?,?,?)',
                    (digest, stage, status, original_service, projected_service, projected_encoded,
                     resolution_encoded, inventory_proof['path'], inventory_proof['sha256']))
            elif existing[:3] != (status, projected_encoded, resolution_encoded):
                # Training identity is immutable; later target evidence cannot rewrite it.
                record['existing_projection_retained'] = True
            yield record

    def service_projections(self):
        from .identity_projection_v5 import (_verified_clock_relations,
                                              journal_event_sha256)
        from .runtime_identity_v5 import _evidence_key
        result = {}
        root = self.path.parent
        rows = list(self.db.execute(
                "SELECT resolution,inventory_path,inventory_sha256 FROM runtime_identity_projection "
                "WHERE status='resolved_enriched'"))
        verified_files = {}
        parsed_inventories = {}

        def verified(path, expected_sha, expected_bytes, description):
            try:
                expected_bytes = int(expected_bytes)
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{description} lacks expected byte size') from exc
            key = (str(path.resolve()), expected_sha, expected_bytes)
            if key not in verified_files:
                if (not path.is_file() or path.stat().st_size != expected_bytes):
                    raise ValueError(f'{description} changed before export')
                body = path.read_bytes()
                if hashlib.sha256(body).hexdigest() != expected_sha:
                    raise ValueError(f'{description} changed before export')
                verified_files[key] = body
            return verified_files[key]

        decoded_rows = [(json.loads(resolution), inventory_path, inventory_sha)
                        for resolution, inventory_path, inventory_sha in rows]
        needs_journal = any((row.get('bracket') or {}).get('kind') != 'source_event_clock'
                            for row, _, _ in decoded_rows)
        journal_path = root / 'attempt-journal.sqlite'
        if needs_journal and not journal_path.is_file():
            raise ValueError('runtime identity journal dependency unavailable before export')
        journal = sqlite3.connect(journal_path) if needs_journal else None
        if journal is not None:
            journal.execute('BEGIN')
        journal_events = {}
        try:
            verified_relations = None
            for row, inventory_path, inventory_sha in decoded_rows:
                path = root / inventory_path
                inventory_proof = row.get('inventory_proof') or {}
                inventory_body = verified(
                    path, inventory_sha, inventory_proof.get('bytes'),
                    'runtime identity inventory dependency')
                inventory_key = (str(path.resolve()), inventory_sha,
                                 int(inventory_proof.get('bytes')))
                if inventory_key not in parsed_inventories:
                    parsed_inventories[inventory_key] = json.loads(inventory_body)
                retained_inventory = parsed_inventories[inventory_key]
                evidence = row.get('clock_evidence') or {}
                bracket = row.get('bracket') or {}
                if bracket.get('kind') == 'source_event_clock':
                    if verified_relations is None:
                        verified_relations = _verified_clock_relations(root)
                    matches = [relation for relation in verified_relations
                               if relation.get('node') == (row.get('process_identity') or {}).get('node')
                               and relation.get('domain') == bracket.get('clock_domain')
                               and relation.get('relation') == bracket.get('clock_relation')
                               and _evidence_key(relation.get('evidence'))
                               == _evidence_key(evidence)]
                    if len(matches) != 1:
                        raise ValueError('runtime identity clock relation changed before export')
                    capture_proofs = retained_inventory.get('capture_proofs') or {}
                    lifecycle_proofs = [capture_proofs.get(bracket.get(name))
                                        for name in ('before_stage', 'after_stage')]
                    if any(not isinstance(proof, dict) for proof in lifecycle_proofs):
                        raise ValueError('runtime identity clock bracket proof is unavailable')
                else:
                    evidence_path = root / str(evidence.get('locator', ''))
                    enclosure = json.loads(verified(
                        evidence_path, evidence.get('sha256'), evidence.get('bytes'),
                        'runtime identity enclosure evidence'))
                    for label in ('started', 'terminal'):
                        event = (enclosure.get('transport') or {}).get(label) or {}
                        sequence = event.get('seq')
                        if sequence not in journal_events:
                            journal_events[sequence] = journal.execute(
                                'SELECT seq,kind,wall_ns,monotonic_ns,data FROM events WHERE seq=?',
                                (sequence,)).fetchone()
                        actual = journal_events[sequence]
                        if (actual is None or journal_event_sha256(*actual)
                                != event.get('event_row_sha256')):
                            raise ValueError('runtime identity journal event changed before export')
                    lifecycle_proofs = [(enclosure.get(label) or {})
                                        for label in ('before_capture', 'after_capture')]
                for proof in lifecycle_proofs:
                    capture = root / str(proof.get('path', ''))
                    verified(capture, proof.get('sha256'), proof.get('bytes'),
                             'runtime identity capture manifest')
                    for name, member_proof in (proof.get('files') or {}).items():
                        member = capture.parent / name
                        verified(member, member_proof.get('sha256'), member_proof.get('bytes'),
                                 'runtime identity capture member')
                canonical = _locator(row.get('record_locator'))
                if canonical is None:
                    raise ValueError('resolved runtime identity lacks canonical raw locator')
                if bracket.get('kind') == 'source_event_clock':
                    raw_path = (root / 'observations' / canonical['retained_file']).resolve()
                    if not raw_path.is_relative_to(root.resolve()):
                        raise ValueError('runtime identity raw locator leaves campaign root')
                    raw_offset, raw_length, raw_sha = (canonical['offset'], canonical['length'],
                                                       canonical['sha256'])
                else:
                    raw_proof = enclosure.get('raw_locator') or {}
                    raw_path = root / str(raw_proof.get('path', ''))
                    raw_offset, raw_length, raw_sha = (raw_proof.get('offset'),
                                                       raw_proof.get('length'),
                                                       raw_proof.get('sha256'))
                try:
                    with raw_path.open('rb') as stream:
                        stream.seek(int(raw_offset))
                        raw_bytes = stream.read(int(raw_length))
                except (OSError, KeyError, TypeError, ValueError) as exc:
                    raise ValueError('runtime identity raw locator unavailable before export') from exc
                if hashlib.sha256(raw_bytes).hexdigest() != raw_sha:
                    raise ValueError('runtime identity raw locator changed before export')
                key = tuple(canonical[name] for name in
                            ('source_file', 'retained_file', 'offset', 'length', 'sha256'))
                value = {'service': row['service_identity']['compose_service'],
                         'resolution': row, 'inventory_path': inventory_path,
                         'inventory_sha256': inventory_sha}
                if key in result and result[key] != value:
                    raise ValueError('conflicting runtime identity projection for one raw locator')
                result[key] = value
        finally:
            if journal is not None:
                journal.close()
        return result
