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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.report)))


if __name__ == '__main__':
    main()
