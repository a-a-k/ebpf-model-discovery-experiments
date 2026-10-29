from __future__ import annotations

import sqlite3

import pytest

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery.store_v3 import ObservationStore
from ebpf_discovery.store_v5 import ObservationStoreV5


def populated(path):
    store = ObservationStore(path, same_trace_parents=True)
    # Digest ordering intentionally differs from insertion/rowid order.
    store.db.executemany('INSERT INTO spans(digest,conflicted,data) VALUES (?,0,?)',
                         [('z', 'first complete payload'), ('a', 'second payload'), ('m', 'third')])
    store.db.execute('INSERT INTO links VALUES (?,?,?,?)', ('native', 'producer', 'span', 'consumer'))
    store.db.execute('INSERT INTO files VALUES (?,?)', ('synthetic.jsonl', 16))
    store.db.commit()
    return store


def test_proof_matches_consistent_backup_with_wal_and_preserves_source(tmp_path):
    path = tmp_path/'live.sqlite'
    store = populated(path)
    try:
        assert store.db.execute('PRAGMA journal_mode=WAL').fetchone()[0] == 'wal'
        store.db.execute("UPDATE spans SET data='committed WAL content' WHERE digest='a'")
        store.db.commit()
        checkpoint = tmp_path/'checkpoint.sqlite'
        target = sqlite3.connect(checkpoint)
        try:
            store.db.backup(target)
        finally:
            target.close()
        before = remote._sha(checkpoint)
        expected = remote._index_table_proof(checkpoint)
        temporary = tmp_path/'verification.sqlite'
        assert remote._consistent_live_index_proof(store.db, temporary) == expected
        assert expected['proof_basis'] == 'rowid-and-all-columns-v1'
        assert expected['spans']['rows'] == 3
        assert remote._sha(checkpoint) == before
        assert not temporary.exists()
    finally:
        store.close()


@pytest.mark.parametrize('mutation', [
    "UPDATE spans SET data='changed' WHERE digest='a'",
    "INSERT INTO spans(digest,conflicted,data) VALUES ('extra',0,'new')",
    "DELETE FROM spans WHERE digest='a'",
    "UPDATE spans SET rowid=rowid+100 WHERE digest='a'",
    "UPDATE links SET linked_span='changed'",
    "UPDATE files SET consumed=17",
    "ALTER TABLE spans ADD COLUMN extra TEXT",
])
def test_proof_detects_content_membership_row_identity_and_schema_changes(tmp_path, mutation):
    path = tmp_path/'index.sqlite'
    populated(path).close()
    before = remote._index_table_proof(path)
    with sqlite3.connect(path) as db:
        db.execute(mutation)
    assert remote._index_table_proof(path) != before


def test_actual_proof_queries_scan_tables_sequentially(tmp_path, monkeypatch):
    path = tmp_path/'index.sqlite'
    populated(path).close()
    connect = sqlite3.connect
    queries = []

    def traced(*args, **kwargs):
        connection = connect(*args, **kwargs)
        connection.set_trace_callback(queries.append)
        return connection

    monkeypatch.setattr(remote.sqlite3, 'connect', traced)
    remote._index_table_proof(path)
    reads = [query for query in queries if query.startswith('SELECT rowid,*')]
    assert len(reads) == 3
    with connect(path) as db:
        for query in reads:
            plan = ' '.join(row[-1] for row in db.execute('EXPLAIN QUERY PLAN '+query)).upper()
            assert 'SCAN ' in plan
            assert 'USING INDEX' not in plan
            assert 'TEMP B-TREE' not in plan


def test_graph_v5_proof_binds_supplied_logical_projection_rows(tmp_path):
    path = tmp_path/'index-v5.sqlite'
    store = ObservationStoreV5(path, same_trace_parents=True)
    store.db.execute('INSERT INTO spans(digest,conflicted,data) VALUES (?,0,?)',
                     ('d', '{"source":"ebpf","service":"/docker/app"}'))
    admission = {'schema': 'supplied-logical-alias-admission-v5',
                 'origin': 'supplied_deployment_inventory_alias',
                 'aliases': {'/docker/app': 'app'}, 'conflicts': [],
                 'occurrence_proofs': [], 'unique_verified_segments': 0,
                 'receiver_segments_reverified': True,
                 'same_table_all_sources_and_direct_baseline': True,
                 'physical_identity_inferred': False}
    store.apply_supplied_logical_aliases(admission, scoped_digest_aliases={'d': 'app'})
    store.close()
    before = remote._index_table_proof(path)
    assert before['supplied_logical_alias_projection']['rows'] == 1
    with sqlite3.connect(path) as db:
        db.execute("UPDATE supplied_logical_alias_projection SET logical_service='changed'")
    assert remote._index_table_proof(path) != before
