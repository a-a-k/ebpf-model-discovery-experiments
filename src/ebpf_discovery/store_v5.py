"""Graph-v5 observation index with lossless duplicate provenance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .store_v3 import ObservationStore, normalized_file


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

    def candidates_v5(self, source, request_id):
        return self._with_provenance(
            'SELECT digest,data FROM spans WHERE source=? AND request=? ORDER BY digest',
            (source, request_id))

    def observation_v5(self, digest):
        rows = self._with_provenance(
            'SELECT digest,data FROM spans WHERE digest=?', (digest,))
        return rows[0] if len(rows) == 1 else None
