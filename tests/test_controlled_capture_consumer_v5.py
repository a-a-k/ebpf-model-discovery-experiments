"""Small metadata mutations for the two named recoveries; no empirical replay."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

from ebpf_discovery.report_v5 import (CONTROLLED_CAPTURE_RECOVERY_SOURCES,
    IDENTICAL_INPUT_DISCOVERY_SOURCE, UPLOAD_HOLD_PARENT_PROOF_SOURCE,
    _preparation_equivalence_facts, _saved_capture_identity)


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location('controlled_saved_review', ROOT/'scripts/review-main-saved-facts-v5.py')
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)
PROFILES = list(CONTROLLED_CAPTURE_RECOVERY_SOURCES.values())


def declaration(p):
    return {**{k: p['capture_identity'][k] for k in ('collector', 'system', 'mode', 'seed')},
        'run_id': p['processing_run_id'], 'head_sha': p['revision'],
        'scientific_capture_run_id': int(p['capture_identity']['run_id']),
        'scientific_capture_head_sha': p['capture_identity']['commit']}


@pytest.mark.parametrize('profile', PROFILES)
@pytest.mark.parametrize('mutation', ['valid', 'cross_head', 'cross_run', 'cross_seed', 'capture_run', 'capture_head'])
def test_exact_processing_declaration_keeps_original_scientific_identity(profile, mutation):
    d = declaration(profile)
    other = next(p for p in PROFILES if p is not profile)
    changes = {'cross_head': ('head_sha', other['revision']), 'cross_run': ('run_id', other['processing_run_id']),
        'cross_seed': ('seed', other['capture_identity']['seed']), 'capture_run': ('scientific_capture_run_id', 1),
        'capture_head': ('scientific_capture_head_sha', other['capture_identity']['commit'])}
    if mutation == 'valid':
        result = REVIEW._capture_declaration(d)
        assert result['run_id'] == int(profile['capture_identity']['run_id'])
        assert result['head_sha'] == profile['capture_identity']['commit']
    else:
        key, value = changes[mutation]; d[key] = value
        with pytest.raises(ValueError): REVIEW._capture_declaration(d)


@pytest.mark.parametrize('profile', PROFILES)
@pytest.mark.parametrize('mutation', ['valid', 'capture', 'capsule', 'processing', 'cross_source', 'qualification', 'refit'])
def test_manifest_has_two_exact_origins(profile, mutation):
    original = copy.deepcopy(profile['capture_identity'])
    recovery = {'capture_run_id': original['run_id'], 'capture_source': original['commit'],
        'capture_artifact_id': profile['capture_artifact']['id'], 'capture_artifact_digest': profile['capture_artifact']['digest'],
        'processing_run_id': str(profile['processing_run_id']), 'processing_source': profile['revision'],
        'new_application_traffic': False, 'refit_models': False}
    manifest = {'commit': profile['revision'], 'scientific_capture_identity': original, 'closed_capture_recovery': recovery}
    if mutation == 'capture': original['run_id'] = str(profile['processing_run_id'])
    if mutation == 'capsule': recovery['capture_artifact_id'] += 1
    if mutation == 'processing': recovery['processing_run_id'] = original['run_id']
    if mutation == 'cross_source': manifest['commit'] = next(p['revision'] for p in PROFILES if p is not profile)
    if mutation == 'qualification': manifest['qualification_only'] = True
    if mutation == 'refit': recovery['refit_models'] = True
    args = manifest, profile['processing_run_id'], tuple(profile['capture_identity'][k] for k in ('collector','system','mode','seed'))
    if mutation == 'valid': assert _saved_capture_identity(*args) == profile['capture_identity']
    else:
        with pytest.raises(ValueError): _saved_capture_identity(*args)


@pytest.mark.parametrize('profile', PROFILES)
@pytest.mark.parametrize('mutation', ['valid', 'algorithm', 'mode', 'resource_blob'])
def test_each_recovery_inherits_its_own_original_scientific_tree(profile, mutation):
    base = IDENTICAL_INPUT_DISCOVERY_SOURCE if profile['capture_identity']['seed'] == 7 else UPLOAD_HOLD_PARENT_PROOF_SOURCE
    assert profile['parent_revision'] == base['revision']
    assert profile['changed_core_blobs'] == base['changed_core_blobs']
    original = {'sha': 'a'*40, 'truncated': False, 'tree': [
        {'path': 'systems/unchanged.py', 'mode': '100644', 'type': 'blob', 'sha': 'b'*40},
        *[{'path': path, 'mode': '100644', 'type': 'blob', 'sha': 'c'*40}
          for path in profile['reviewed_changed_blobs'] if path not in profile['added_paths']]]}
    prepared = {'sha': 'd'*40, 'truncated': False, 'tree': [copy.deepcopy(original['tree'][0]),
        *[{'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob}
          for path, blob in profile['reviewed_changed_blobs'].items()]]}
    if mutation == 'algorithm': prepared['tree'][0]['sha'] = 'e'*40
    if mutation in ('mode','resource_blob'):
        row = next(r for r in prepared['tree'] if r['path'] == 'scripts/control-closed-offline-resources-v5.py')
        row['mode' if mutation == 'mode' else 'sha'] = '100755' if mutation == 'mode' else 'e'*40
    if mutation == 'valid':
        facts = _preparation_equivalence_facts(profile['anchor'], profile['revision'], original, prepared)
        assert facts['recovered_capture_identity'] == profile['capture_identity']
        assert facts['shared_observed_discovery_policy'] == base['shared_discovery_policy']
        assert ('parent_proof_schedule' in facts) == (profile['capture_identity']['seed'] == 8)
    else:
        with pytest.raises(ValueError): _preparation_equivalence_facts(profile['anchor'], profile['revision'], original, prepared)


@pytest.mark.parametrize('profile', PROFILES)
def test_controlled_source_cannot_skip_missing_shared_discovery(tmp_path, profile):
    with pytest.raises(ValueError, match='mandatory shared'):
        REVIEW.shared_observed_discovery_facts(tmp_path, tmp_path/'toolchain', declaration(profile), {}, [], {})


def test_new8_cannot_silently_skip_original_upload_hold_proof(tmp_path):
    profile = next(p for p in PROFILES if p['capture_identity']['seed'] == 8)
    with pytest.raises(FileNotFoundError):
        REVIEW.upload_hold_parent_proof_facts(tmp_path, tmp_path, declaration(profile), {}, {}, {}, {})
    profile7 = next(p for p in PROFILES if p['capture_identity']['seed'] == 7)
    assert REVIEW.upload_hold_parent_proof_facts(tmp_path, tmp_path, declaration(profile7), {}, {}, {}, {}) is None


def resource_packet(host, p):
    d = declaration(p); original = p['capture_identity']; gib = 1024**3
    identity = {'seed': original['seed'], 'capture_run_id': original['run_id'], 'capture_source': original['commit'],
        'processing_run_id': str(d['run_id']), 'processing_source': d['head_sha']}
    sizes = {'Z': p['capture_artifact']['size_in_bytes'], **p['resource_input_bytes']}
    required = max(sizes['Z']+sizes['F']+sizes['P'], sizes['F']+sizes['P']+4*sizes['I'])+3*gib
    swap = '/original/work/closed-offline-swapfile'
    ready = {**identity, **sizes, 'status':'ready', 'started_ns':10, 'ended_ns':20,
        'requested_swap_bytes':2*gib, 'swap_path':swap, 'required_before_allocation':required,
        'actual_free_before':required, 'actual_free_after':required-2*gib, 'memory_sufficiency_or_root_cause_proven':False,
        'active_owned_swap':[swap,'file',str(2*gib//1024),'0','-2'],
        'allocation_commands':[{'argv':argv,'returncode':0} for argv in [
            ['sudo','install','-m','600','/dev/null',swap], ['sudo','fallocate','-l',str(2*gib),swap],
            ['sudo','mkswap',swap], ['sudo','swapon',swap]]]}
    child = {**identity, 'status':'complete', 'started_ns':30, 'ended_ns':100, 'owned_pid':123,
        'child_returncode':0, 'final_child_returncode':0, 'new_application_traffic':False, 'model_refit':False,
        'priority_policy':{'nice_increment':10,'ionice_class':2,'ionice_level':7,'child_oom_score_adj_at_least':500},
        'argv':['ionice','-c','2','-n','7','/opt/python/bin/python','-m','ebpf_discovery.postcapture_v5',
            'finalize','--campaign','work/campaign','--proof','work/restored-postcapture/postcapture-proof',
            '--capture-run-id',original['run_id'],'--capture-source',original['commit']],
        'child_maxrss_kib':100, 'child_user_seconds':20, 'child_system_seconds':5}
    sample = {'recorded_ns':40, 'owned_pid':123, 'actual_disk_free':100,
        'host_memory':{'MemTotal':100,'MemAvailable':5,'SwapTotal':100,'SwapFree':1},
        'process_status':{'Name':'python','State':'R (running)','VmRSS':'1 kB','VmHWM':'1 kB',
            'VmSize':'2 kB','VmSwap':'0 kB','Threads':'1'}, 'oom_score_adj':500, 'cpu_stat':'123 (python) R', 'io':'rchar: 1'}
    marker = {'scientific_root':'/original/work/campaign','file_bytes':sizes['F'],'index_bytes':sizes['I']}
    return d, marker, ready, child, [sample]


@pytest.mark.parametrize('profile', PROFILES)
@pytest.mark.parametrize('mutation', ['valid','zombie','F','P','I','peak','swap','free','allocation','capture',
    'processing','nonzero','final_nonzero','command','clock','pid','missing_live_rss','no_samples'])
def test_resource_receipts_preserve_complete_budget_identity_and_exit(tmp_path, profile, mutation):
    d,marker,ready,child,samples = resource_packet(tmp_path, profile)
    if mutation in ('F','P','I'): ready[mutation] += 1
    if mutation == 'peak': ready['required_before_allocation'] -= 1
    if mutation == 'swap': ready['requested_swap_bytes'] //= 2
    if mutation == 'free': ready['actual_free_after'] = 0
    if mutation == 'allocation': ready['allocation_commands'][0]['returncode'] = 1
    if mutation == 'capture': child['capture_run_id'] = child['processing_run_id']
    if mutation == 'processing': child['processing_source'] = child['capture_source']
    if mutation == 'nonzero': child['child_returncode'] = 1
    if mutation == 'final_nonzero': child['final_child_returncode'] = -9
    if mutation == 'command': child['argv'][-1] = '0'*40
    if mutation == 'clock': samples[0]['recorded_ns'] = 101
    if mutation == 'pid': samples[0]['owned_pid'] += 1
    if mutation == 'missing_live_rss': samples[0]['process_status'].pop('VmRSS')
    if mutation == 'no_samples': samples.clear()
    if mutation == 'zombie':
        last = copy.deepcopy(samples[0]); last['recorded_ns'] = 90
        last['process_status'] = {'Name':'python','State':'Z (zombie)','Threads':'1'}
        samples.append(last)
    for name, value in [('resource-prepare.json',ready),('processing-child-result.json',child)]:
        (tmp_path/name).write_text(json.dumps(value),encoding='utf8')
    (tmp_path/'processing-resource-samples.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in samples),encoding='utf8')
    if mutation in ('valid','zombie'):
        facts = REVIEW.controlled_processing_resource_facts(tmp_path,d,marker)
        assert facts['sample_rows'] == len(samples) and facts['owned_process_observations'] == 1
    else:
        with pytest.raises(ValueError): REVIEW.controlled_processing_resource_facts(tmp_path,d,marker)
