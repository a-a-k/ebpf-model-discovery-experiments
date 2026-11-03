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



def reference_fixture(tmp_path):
    import json
    store=populated(tmp_path/'live.sqlite')
    store.db.execute('PRAGMA journal_mode=WAL')
    store.db.execute("UPDATE spans SET data='synthetic WAL content' WHERE digest='a'")
    store.db.commit()
    checkpoint=tmp_path/'checkpoint';checkpoint.mkdir()
    target=sqlite3.connect(checkpoint/'observation-index.sqlite')
    store.db.backup(target);target.close()
    path=checkpoint/'observation-index.sqlite'
    file={'relative_path':path.name,'bytes':path.stat().st_size,'sha256':remote._sha(path)}
    manifest={'identity':{'run_id':'42','commit':'a'*40,'system':'otel_demo','collector':'deepflow','mode':'absent','seed':8},'files':{path.name:file}}
    (checkpoint/'manifest.json').write_text(json.dumps(manifest))
    verified={'manifest_sha256':remote._sha(checkpoint/'manifest.json'),'files':{path.name:{k:file[k] for k in ('bytes','sha256')}}}
    return store,checkpoint,verified


@pytest.mark.parametrize('mutation',['none','data','rowid','schema','foreign_manifest','wrong_input','changed_proof'])
def test_exact_consistent_backup_reuse_preserves_full_fallback_and_scientific_changes(tmp_path,monkeypatch,mutation):
    import json
    store,checkpoint,verified=reference_fixture(tmp_path)
    original=remote._index_table_proof
    calls=[]
    def counted(path):
        calls.append(str(path));return original(path)
    monkeypatch.setattr(remote,'_index_table_proof',counted)
    temporary=tmp_path/'verification.sqlite';receipt=tmp_path/'receipt.json'
    try:
        if mutation=='foreign_manifest':verified['manifest_sha256']='0'*64
        if mutation=='wrong_input':verified['files']['observation-index.sqlite']['sha256']='0'*64
        if mutation in ('foreign_manifest','wrong_input'):
            with pytest.raises(ValueError):remote._checkpoint_index_reference(checkpoint,verified)
            return
        reference=remote._checkpoint_index_reference(checkpoint,verified)
        assert len(calls)==1
        if mutation=='changed_proof':reference['logical_proof']['spans']['rows']+=1
        if mutation=='data':store.db.execute("UPDATE spans SET data='changed WAL value' WHERE digest='a'")
        if mutation=='rowid':store.db.execute("UPDATE spans SET rowid=99 WHERE digest='a'")
        if mutation=='schema':store.db.execute('CREATE TABLE extra_scientific_table(x)')
        store.db.commit()
        if mutation=='changed_proof':
            with pytest.raises(ValueError):remote._consistent_live_index_proof(store.db,temporary,reference=reference,receipt=receipt)
            assert not temporary.exists();return
        actual=remote._consistent_live_index_proof(store.db,temporary,reference=reference,receipt=receipt)
        proof=json.loads(receipt.read_text())
        assert not temporary.exists() and proof['whole_consistent_backup_bytes_verified']
        if mutation=='none':
            assert actual==reference['logical_proof'] and len(calls)==1
            assert proof['logical_proof_reused'] and not proof['full_fallback_executed']
        else:
            assert actual!=reference['logical_proof'] and len(calls)==2
            assert proof['full_fallback_executed'] and not proof['logical_proof_reused']
        assert proof['checkpoint_identity']['run_id']=='42'
    finally:store.close()


def test_exact_proof_reference_rejects_missing_original_and_non_sqlite_mutation(tmp_path):
    store,checkpoint,verified=reference_fixture(tmp_path)
    try:
        (checkpoint/'observation-index.sqlite').unlink()
        with pytest.raises(FileNotFoundError):remote._checkpoint_index_reference(checkpoint,verified)
    finally:store.close()
