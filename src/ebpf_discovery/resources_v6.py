"""Use the complete standard worker; record platform limits instead of lowering them."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from .runtime import write_json

JOB_TIMEOUT_MINUTES = 360
RUNNER = 'ubuntu-24.04'
ACCOUNT_CONCURRENCY = 40  # Documented GitHub Pro standard-hosted ceiling.
GO_OVERRIDES = ('GOMEMLIMIT', 'GOMAXPROCS', 'GOGC')
UNUSED_HOSTED_SDKS = ('/usr/local/lib/android', '/usr/share/dotnet', '/opt/ghc')
MODEL_SWAP_BYTES = 16 * 1024**3


def clear_go_overrides(environment):
    """No inherited 12GiB heap target or low CPU/GC override from v5 workers."""
    removed = {name: environment.pop(name) for name in GO_OVERRIDES if name in environment}
    return removed


def prepare(report):
    if os.environ.get('GITHUB_ACTIONS') != 'true' or not sys.platform.startswith('linux'):
        raise RuntimeError('worker resource preparation is GitHub Actions only')
    import resource
    removed = clear_go_overrides(os.environ)
    cleanup_started = time.time_ns()
    disk_before_cleanup = shutil.disk_usage('.').free
    present = {name: Path(name).exists() for name in UNUSED_HOSTED_SDKS}
    # The same three unused SDK directories were already qualified in v5.
    # Python, Go, Node, git, gh, Docker and every study/input path are preserved.
    subprocess.run(['sudo', 'rm', '-rf', '--', *UNUSED_HOSTED_SDKS], check=True)
    cleanup = {'paths_present_before': present, 'free_bytes_before': disk_before_cleanup,
               'free_bytes_after': shutil.disk_usage('.').free,
               'elapsed_seconds': (time.time_ns() - cleanup_started) / 1e9,
               'scope': 'Only three explicitly named unused hosted SDK directories'}
    affinity = sorted(os.sched_getaffinity(0))
    memory = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        memory[key] = value.strip()
    limits = {name: list(resource.getrlimit(getattr(resource, name)))
              for name in ('RLIMIT_CPU', 'RLIMIT_AS', 'RLIMIT_DATA', 'RLIMIT_NOFILE')}
    cgroups = {}
    for name in ('cpu.max', 'memory.max', 'memory.high', 'pids.max'):
        path = Path('/sys/fs/cgroup') / name
        cgroups[name] = path.read_text().strip() if path.exists() else None
    disk = shutil.disk_usage('.')
    proof = {'observed_ns': time.time_ns(), 'runner_label': RUNNER,
             'job_timeout_minutes': JOB_TIMEOUT_MINUTES,
             'documented_standard_public_runner': {'vCPU': 4, 'RAM_GB': 16},
             'removed_artificial_go_overrides': removed,
             'unused_SDK_disk_cleanup': cleanup,
             'effective_go_overrides': {name: os.environ.get(name) for name in GO_OVERRIDES},
             'allowed_CPUs': affinity, 'memory': memory, 'inherited_OS_limits': limits,
             'platform_cgroups': cgroups,
             'disk_bytes': {'total': disk.total, 'free': disk.free, 'used': disk.used},
             'model_worker_CPUs_or_memory_capped_by_study': False,
             'paid_runner_provisioned': False,
             'platform_limit_sources': [
                 'https://docs.github.com/en/actions/reference/limits',
                 'https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job']}
    write_json(report, proof)
    if len(affinity) < 4 or int(memory['MemTotal'].split()[0]) < 14 * 1024**2:
        raise RuntimeError('runner is smaller than the reviewed public standard worker')
    return proof


def model_memory_state(work):
    memory = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    return {'memory': {k: memory[k].strip() for k in
                       ('MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree')},
            'swaps': Path('/proc/swaps').read_text(),
            'disk_free_bytes': shutil.disk_usage(work).free}


def prepare_model_swap(report):
    """One additional owned swap file; physical resources and existing swap stay intact."""
    if os.environ.get('GITHUB_ACTIONS') != 'true' or not sys.platform.startswith('linux'):
        raise RuntimeError('model swap preparation is repository Actions Linux only')
    from .block_v6 import RESERVE
    work = Path(__file__).resolve().parents[2] / 'work'
    if any(p.is_symlink() for p in (work, *work.parents)):
        raise ValueError('model swap parent must not contain symlinks')
    work.mkdir(exist_ok=True)
    path = work / 'v6-model.swap'
    started, cpu = time.time_ns(), os.times()
    before = model_memory_state(work)
    proof = {'started_ns': started, 'status': 'preparing', 'path': str(path),
             'additional_swap_file_bytes': MODEL_SWAP_BYTES, 'existing_staging_reserve_bytes': RESERVE,
             'before': before, 'commands': [], 'physical_RAM_CPU_or_model_input_changed': False,
             'scope': 'Model only; identical all four arms; paging and setup costs retained'}
    write_json(report, proof)
    try:
        if path.exists() or path.is_symlink():
            raise FileExistsError('model swap path already exists; never overwrite or reuse it')
        if before['disk_free_bytes'] < MODEL_SWAP_BYTES + RESERVE:
            raise OSError('model swap requires its full size plus the existing archive/staging reserve')
        # Exclusive creation and actual writes avoid overwriting a file or creating holes.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            chunk, left = bytes(8 * 1024**2), MODEL_SWAP_BYTES
            while left:
                count = min(left, len(chunk))
                stream.write(chunk[:count])
                left -= count
            stream.flush()
            os.fsync(stream.fileno())
        identity = path.stat()
        if (identity.st_size != MODEL_SWAP_BYTES or identity.st_uid != os.getuid()
                or identity.st_mode & 0o777 != 0o600):
            raise ValueError('owned model swap identity, size or permissions differ')
        for command in (['mkswap', '--', str(path)], ['sudo', '-n', 'swapon', '--', str(path)]):
            command_started = time.time_ns()
            result = subprocess.run(command, capture_output=True, text=True)
            proof['commands'].append({'argv': command, 'returncode': result.returncode,
                                      'wall_seconds': (time.time_ns() - command_started) / 1e9,
                                      'stdout': result.stdout[:2000], 'stderr': result.stderr[:2000]})
            write_json(report, proof)
            result.check_returncode()
        after = model_memory_state(work)
        if str(path) not in [line.split()[0] for line in after['swaps'].splitlines()[1:]]:
            raise RuntimeError('owned model swap is not active')
        proof.update(status='active', after=after)
    except BaseException as error:
        proof.update(status='failed', error_type=type(error).__name__)
        raise
    finally:
        ended_cpu = os.times()
        proof.update(ended_ns=time.time_ns(),
                     wall_seconds=(time.time_ns() - started) / 1e9,
                     setup_parent_CPU_seconds=(ended_cpu.user - cpu.user) + (ended_cpu.system - cpu.system),
                     setup_children_CPU_seconds=(ended_cpu.children_user - cpu.children_user)
                         + (ended_cpu.children_system - cpu.children_system))
        write_json(report, proof)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.report)))


if __name__ == '__main__':
    main()
