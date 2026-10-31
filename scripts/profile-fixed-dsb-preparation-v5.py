"""Actions-only profile of unchanged preparation on one fixed saved full7 prefix."""
import cProfile
import faulthandler
import importlib
import json
import os
from pathlib import Path
import pstats
import resource
import signal
import subprocess
import time

from ebpf_discovery.remote_toolchain_v4 import (
    _checkpoint_toolchain, _index_table_proof, _json_sha, _readonly_store,
    _safe_extract, _validate_checkpoint,
)
from ebpf_discovery.runtime import Context
from ebpf_discovery.store_v5 import ObservationStoreV5


assert os.environ.get('GITHUB_ACTIONS') == 'true', 'Saved-prefix profiling runs in Actions'
out = Path('work/preparation-profile')
out.mkdir(parents=True, exist_ok=True)
campaign = Path('work/campaign').resolve()
expected = {
    'run_id': '41164824120', 'system': 'deathstarbench', 'mode': 'full', 'seed': '7',
    'commit': '0c98bf4520e863ab021b60d00517ee2aa49ab38e',
    'manifest_sha256': 'a6c521efe353685b267a64e6ba034c1f69ce79a7e623dc9c98646863f6f2a347',
    'plans_sha256': 'fa6e700f5553873cfc9c24ce4509e6ab45acbac2739abd83e9c8e236d9b03070',
    'training_index_proof_sha256': '8a7fcacb6207a9a58066e0754438cf3fd316112b675044b684e7ba008b663877',
}
subprocess.run(['git', 'diff', '--exit-code', expected['commit'], 'HEAD', '--', 'src', 'systems'], check=True)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
_safe_extract(Path('work/training-prefix.zip'), campaign)
manifest, before = _validate_checkpoint(campaign, expected)
index_proof = _index_table_proof(campaign/'observation-index.sqlite')
assert _json_sha(index_proof) == expected['training_index_proof_sha256']
pins, toolchain_type, collector = _checkpoint_toolchain(campaign, manifest)
assert collector['collector'] == 'deepflow'
plans = json.loads((campaign/'plans.json').read_text())
assert _json_sha(plans) == expected['plans_sha256']
status = {'diagnostic_source': head, 'input_identity': expected,
          'source_core_identical_to_original': True, 'new_traffic_or_tools_or_scoring': False,
          'status': 'preparation_not_started', 'profile_overhead_is_not_a_speed_benchmark': True,
          'diagnostic_only_budget_seconds': 4*60*60,
          'profile_started': False,
          'budget_is_not_an_experiment_deadline_or_eligibility_gate': True}
(out/'status.json').write_text(json.dumps(status, indent=2)+'\n')
store = _readonly_store(campaign/'observation-index.sqlite', ObservationStoreV5)
profiler = cProfile.Profile()
failure = None
preparation_completed = False
toolchain = None
try:
    ctx = Context(campaign, 'full', 7)
    declaration = importlib.import_module('systems.deathstarbench.experiment_v4')
    toolchain = toolchain_type(ctx, 'deathstarbench', store, declaration)
    with (out/'preparation-stacks.txt').open('w') as stacks:
        faulthandler.dump_traceback_later(60, repeat=True, file=stacks)
        started = time.time_ns()
        status.update(status='preparation_running', started_ns=started, profile_started=True)
        (out/'status.json').write_text(json.dumps(status, indent=2)+'\n')
        def diagnostic_budget_stop(signum, frame):
            raise TimeoutError('Fixed offline profiling budget reached; retain partial diagnostic')
        previous_handler = signal.signal(signal.SIGALRM, diagnostic_budget_stop)
        signal.alarm(4*60*60)
        try:
            profiler.runcall(toolchain.prepare_inputs, plans)
            preparation_completed = True
        except TimeoutError as error:
            status.update(status='partial_diagnostic_budget_stop', diagnostic_error=str(error))
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)
            faulthandler.cancel_dump_traceback_later()
            profiler.dump_stats(out/'preparation.pstats')
            status['ended_ns'] = time.time_ns()
            stats = pstats.Stats(profiler)
            rows = [{'file': key[0], 'line': key[1], 'function': key[2],
                     'primitive_calls': value[0], 'total_calls': value[1],
                     'own_profiled_seconds': value[2], 'cumulative_profiled_seconds': value[3]}
                    for key, value in stats.stats.items()]
            (out/'top-functions.json').write_text(json.dumps(
                sorted(rows, key=lambda row: row['cumulative_profiled_seconds'], reverse=True)[:100], indent=2)+'\n')
            (out/'status.json').write_text(json.dumps(status, indent=2)+'\n')
except BaseException as error:
    failure = error
    status.update(status='technical_failure', error=repr(error))
finally:
    try:
        store.close()
    except BaseException as error:
        status['store_close_error'] = repr(error)
        if failure is None:
            failure = error
    try:
        after_manifest, after = _validate_checkpoint(campaign, expected, allow_toolchain=True)
        assert after_manifest == manifest and after['files'] == before['files']
        status['full_checkpoint_unchanged'] = True
    except BaseException as error:
        status.update(full_checkpoint_unchanged=False, checkpoint_verification_error=repr(error))
        if failure is None:
            failure = error
    status.update(status=('technical_failure' if failure is not None else
                          'complete' if preparation_completed else 'partial_diagnostic_budget_stop'),
                  original_worker_input_preparation_seconds=6473.154799267,
                  max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  input_manifests=len(getattr(toolchain, 'input_manifests', {})))
    if not status['profile_started']:
        status['no_profile_data'] = True
    (out/'status.json').write_text(json.dumps(status, indent=2)+'\n')
    cost = campaign/'toolchain/input-preparation-cost.json'
    if cost.is_file():
        (out/'input-preparation-cost.json').write_bytes(cost.read_bytes())
    print(json.dumps(status), flush=True)
if failure is not None:
    raise failure
