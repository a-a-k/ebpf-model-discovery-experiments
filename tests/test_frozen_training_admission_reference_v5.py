"""Tiny original admission/SQL fixtures; no retained experiment data."""
from copy import deepcopy
import json
import subprocess
from types import SimpleNamespace

import pytest

from ebpf_discovery import remote_toolchain_v4 as remote
from ebpf_discovery import supplied_alias_v5 as aliases
from ebpf_discovery.store_v5 import ObservationStoreV5
from ebpf_discovery.toolchain_v5 import Toolchain


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + '\n', encoding='utf-8')


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    write(tmp_path/'status.json', {'protocol_version': 'graph-v5', 'collector': 'deepflow'})
    write(tmp_path/'observations/collector.json', {'collector': 'deepflow'})
    write(tmp_path/'deployment.json', {})
    inventory = tmp_path/'runtime-identity-v5/inventory-training.json'
    write(inventory, {'schema': 'runtime-identity-inventory-v5', 'samples': []})
    table = inventory.with_name('supplied-service-aliases-training.json')
    aliases.write_training(json.loads(inventory.read_text()), inventory, table)
    store = ObservationStoreV5(tmp_path/'observation-index.sqlite', same_trace_parents=True)
    admission = aliases.admit_observed(store, json.loads(table.read_text()),
                                      expected_source_prefix='ebpf-deepflow')
    admission['effective_store_projection'] = store.apply_supplied_logical_aliases(admission)
    aliases.write_admission(admission, table, table.with_name('supplied-service-alias-admission-training.json'))
    store.close()
    identity = {'run_id': '123', 'commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'system': 'otel_demo', 'mode': 'absent', 'seed': 8}
    files = {name: {'relative_path': name, **claim}
             for name, claim in remote._manifest(tmp_path).items()}
    manifest = {'schema_version': 'v4-training-prefix-checkpoint',
                'status': 'partial_training_capture_only; no forecast or completed cell',
                'identity': identity, 'files': files}
    write(tmp_path/'manifest.json', manifest)
    expected = {**identity, 'manifest_sha256': remote._sha(tmp_path/'manifest.json')}
    write(tmp_path/'ready.json', {**identity, 'status': 'training_checkpoint_ready',
                                'manifest_sha256': expected['manifest_sha256']})
    manifest, verified = remote._validate_checkpoint(tmp_path, expected)
    proof = remote._index_table_proof(tmp_path/'observation-index.sqlite')
    expected['training_index_proof_sha256'] = remote._json_sha(proof)
    reference = remote._frozen_training_admission_reference(
        tmp_path, manifest, verified, proof, expected, {'collector': 'deepflow'})
    store = remote._readonly_store(tmp_path/'observation-index.sqlite',
                                   ObservationStoreV5, immutable_prefix=True)
    yield SimpleNamespace(root=tmp_path, manifest=manifest, verified=verified,
                          proof=proof, expected=expected, reference=reference, store=store)
    store.close()


def construct(frozen, reference):
    return Toolchain(SimpleNamespace(out=frozen.root), 'otel_demo', frozen.store,
                     SimpleNamespace(), frozen_training_admission_reference=reference)


def test_reuse_keeps_the_actual_original_projection_verifier(frozen, monkeypatch):
    original = construct(frozen, None).supplied_alias_projection_verification
    calls = []
    verify = frozen.store.verify_supplied_logical_aliases
    monkeypatch.setattr(frozen.store, 'verify_supplied_logical_aliases',
                        lambda value: (calls.append(value), verify(value))[1])
    monkeypatch.setattr(aliases, 'admit_observed', lambda *a, **kw: pytest.fail('duplicate admission'))
    tool = construct(frozen, frozen.reference)
    assert len(calls) == 1 and tool.supplied_alias_projection_verification == original
    receipt = json.loads((tool.root/'frozen-training-admission-reference.json').read_text())
    assert receipt['current_semantic_recomputation_executed'] is False
    assert receipt['full_projection_verification']['logical_projection_verified'] is True
    assert receipt['algorithm_files'] == remote._TRAINING_ADMISSION_ALGORITHM


@pytest.mark.parametrize('change', [
    lambda r: r.update(manifest_sha256='0'*64),
    lambda r: r.update(campaign_root='foreign'),
    lambda r: r['checkpoint_identity'].update(commit='f'*40),
    lambda r: r.update(training_index_proof_sha256='0'*64),
    lambda r: r.update(complete_checkpoint_census_sha256='0'*64),
    lambda r: r.update(same_trace_parents=False),
    lambda r: r.update(expected_source_prefix='ebpf-coroot'),
    lambda r: r['algorithm_files'].update(**{'supplied_alias_v5.py': '0'*40}),
    lambda r: r['input_claims'].pop('observation-index.sqlite'),
    lambda r: r['input_claims']['runtime-identity-v5/supplied-service-aliases-training.json'].update(sha256='0'*64),
    lambda r: r['input_claims']['runtime-identity-v5/supplied-service-alias-admission-training.json'].update(bytes=0),
])
def test_changed_explicit_reference_fails_closed(frozen, change):
    reference = deepcopy(frozen.reference)
    change(reference)
    with pytest.raises(ValueError, match='frozen admission'):
        construct(frozen, reference)


@pytest.mark.parametrize('attribute,value', [('_immutable_path_prefix', False),
                                          ('same_trace_parents', False)])
def test_mutable_or_different_normalization_is_not_reused(frozen, attribute, value):
    setattr(frozen.store, attribute, value)
    with pytest.raises(ValueError, match='immutable worker profile'):
        construct(frozen, frozen.reference)


def test_non_query_only_store_is_not_reused(frozen):
    frozen.store.db.execute('PRAGMA query_only=OFF')
    with pytest.raises(ValueError, match='immutable worker profile'):
        construct(frozen, frozen.reference)


def test_changed_current_sql_bytes_are_rejected(frozen):
    with (frozen.root/'observation-index.sqlite').open('ab') as stream:
        stream.write(b'changed')
    with pytest.raises(ValueError, match='input claim changed'):
        construct(frozen, frozen.reference)


def test_changed_alias_file_is_still_rejected_by_original_loader(frozen):
    path = frozen.root/'runtime-identity-v5/supplied-service-aliases-training.json'
    path.write_text(path.read_text()+' ')
    with pytest.raises(ValueError, match='table dependency changed'):
        construct(frozen, frozen.reference)


def test_missing_optional_reference_keeps_original_recomputation(frozen, monkeypatch):
    calls = []
    original = aliases.admit_observed
    monkeypatch.setattr(aliases, 'admit_observed',
                        lambda *a, **kw: (calls.append(kw), original(*a, **kw))[1])
    construct(frozen, None)
    assert calls == [{'expected_source_prefix': 'ebpf-deepflow'}]


def test_builder_rejects_changed_sql_proof_and_source_algorithm(frozen, monkeypatch):
    expected = dict(frozen.expected, training_index_proof_sha256='0'*64)
    with pytest.raises(ValueError, match='checkpoint proof'):
        remote._frozen_training_admission_reference(frozen.root, frozen.manifest,
            frozen.verified, frozen.proof, expected, {'collector': 'deepflow'})
    monkeypatch.setitem(remote._TRAINING_ADMISSION_ALGORITHM, 'supplied_alias_v5.py', '0'*40)
    with pytest.raises(ValueError, match='algorithm differs'):
        remote._frozen_training_admission_reference(frozen.root, frozen.manifest,
            frozen.verified, frozen.proof, frozen.expected, {'collector': 'deepflow'})


def test_other_collectors_and_modes_keep_the_original_worker_call(frozen):
    assert remote._frozen_training_admission_reference(frozen.root, {}, {}, {},
        frozen.expected, {'collector': 'coroot'}) is None
    assert remote._frozen_training_admission_reference(frozen.root, {}, {}, {},
        dict(frozen.expected, mode='partial'), {'collector': 'deepflow'}) is None


def test_full_projection_verification_failure_is_not_hidden(frozen, monkeypatch):
    def reject(admission):
        raise ValueError('frozen supplied logical projection membership differs from admission')
    monkeypatch.setattr(frozen.store, 'verify_supplied_logical_aliases', reject)
    with pytest.raises(ValueError, match='projection membership differs'):
        construct(frozen, frozen.reference)
