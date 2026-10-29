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
        return ("SELECT s.digest,COALESCE(p.projected_data,s.data) FROM spans s "
                "LEFT JOIN runtime_identity_projection p ON p.digest=s.digest " + where)

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
            "SELECT COALESCE(p.projected_data,s.data) FROM spans s "
            "LEFT JOIN runtime_identity_projection p ON p.digest=s.digest " + where, params)]

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
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        rows, counts = [], {'resolved_enriched': 0, 'resolved_existing': 0,
                            'label_conflict': 0, 'unknown': 0}
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
            rows.append(record)
        self.db.commit()
        with out.open('w', encoding='utf-8') as stream:
            for row in rows:
                stream.write(json.dumps(row, sort_keys=True) + '\n')
        return {'rows': len(rows), 'counts': counts, 'path': str(out),
                'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                'training_rows_immutable': True}

    def service_projections(self):
        from .identity_projection_v5 import journal_event_sha256
        result = {}
        root = self.path.parent
        for resolution, inventory_path, inventory_sha in self.db.execute(
                "SELECT resolution,inventory_path,inventory_sha256 FROM runtime_identity_projection "
                "WHERE status='resolved_enriched'"):
            path = root / inventory_path
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != inventory_sha:
                raise ValueError('runtime identity inventory dependency changed before export')
            row = json.loads(resolution)
            evidence = row.get('clock_evidence') or {}
            evidence_path = root / str(evidence.get('locator', ''))
            if (not evidence_path.is_file()
                    or hashlib.sha256(evidence_path.read_bytes()).hexdigest() != evidence.get('sha256')):
                raise ValueError('runtime identity enclosure evidence changed before export')
            enclosure = json.loads(evidence_path.read_text(encoding='utf-8'))
            journal_path = root / 'attempt-journal.sqlite'
            if not journal_path.is_file():
                raise ValueError('runtime identity journal dependency unavailable before export')
            with sqlite3.connect(journal_path) as journal:
                for label in ('started', 'terminal'):
                    event = (enclosure.get('transport') or {}).get(label) or {}
                    actual = journal.execute(
                        'SELECT seq,kind,wall_ns,monotonic_ns,data FROM events WHERE seq=?',
                        (event.get('seq'),)).fetchone()
                    if (actual is None or journal_event_sha256(*actual)
                            != event.get('event_row_sha256')):
                        raise ValueError('runtime identity journal event changed before export')
            for label in ('before_capture', 'after_capture'):
                proof = enclosure.get(label) or {}
                capture = root / str(proof.get('path', ''))
                if (not capture.is_file()
                        or hashlib.sha256(capture.read_bytes()).hexdigest() != proof.get('sha256')):
                    raise ValueError('runtime identity capture manifest changed before export')
                for name, member_proof in (proof.get('files') or {}).items():
                    member = capture.parent / name
                    if (not member.is_file() or member.stat().st_size != member_proof.get('bytes')
                            or hashlib.sha256(member.read_bytes()).hexdigest() != member_proof.get('sha256')):
                        raise ValueError('runtime identity capture member changed before export')
            raw_proof = enclosure.get('raw_locator') or {}
            raw_path = root / str(raw_proof.get('path', ''))
            try:
                with raw_path.open('rb') as stream:
                    stream.seek(int(raw_proof['offset']))
                    raw_bytes = stream.read(int(raw_proof['length']))
            except (OSError, KeyError, TypeError, ValueError) as exc:
                raise ValueError('runtime identity raw locator unavailable before export') from exc
            if hashlib.sha256(raw_bytes).hexdigest() != raw_proof.get('sha256'):
                raise ValueError('runtime identity raw locator changed before export')
            canonical = _locator(row.get('record_locator'))
            if canonical is None:
                raise ValueError('resolved runtime identity lacks canonical raw locator')
            key = tuple(canonical[name] for name in
                        ('source_file', 'retained_file', 'offset', 'length', 'sha256'))
            value = {'service': row['service_identity']['compose_service'],
                     'resolution': row, 'inventory_path': inventory_path,
                     'inventory_sha256': inventory_sha}
            if key in result and result[key] != value:
                raise ValueError('conflicting runtime identity projection for one raw locator')
            result[key] = value
        return result
