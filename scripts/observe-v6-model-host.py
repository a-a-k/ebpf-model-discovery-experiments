"""Read-only, body-free host samples around the unchanged v6 model command."""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time

REPORT = Path('work/model-host-observer.jsonl')
PERIOD = 30
COMMAND = [sys.executable, '-m', 'ebpf_discovery.study_v6', 'model', '--root', 'work/case']


def read(path):
    try:
        return Path(path).read_text(encoding='utf-8').strip()
    except OSError:
        return 'UNKNOWN'


def proc(pid):
    value = read(f'/proc/{pid}/stat')
    if value == 'UNKNOWN':
        return None
    end = value.rfind(')')
    fields = value[end + 2:].split()
    return {'pid': int(pid), 'comm': value[value.find('(')+1:end], 'ppid': int(fields[1]),
            'starttime_ticks': int(fields[19]), 'rss_bytes': int(fields[21])*os.sysconf('SC_PAGE_SIZE')}


def owned(root_pid, root_start):
    rows = {}
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            value = proc(path.parent.name)
            if value:
                rows[value['pid']] = value
        except (OSError, ValueError, IndexError):
            continue
    if root_pid not in rows or rows[root_pid]['starttime_ticks'] != root_start:
        return {'status': 'UNKNOWN', 'reason': 'original model PID/starttime no longer observed'}
    selected = {root_pid}
    while True:
        children = {pid for pid, row in rows.items() if row['ppid'] in selected}
        if children <= selected:
            break
        selected |= children
    return {'status': 'observed', 'processes': [rows[pid] for pid in sorted(selected)],
            'RSS_scope': 'Individual PID RSS; shared pages can appear in multiple processes'}


def journal(unit, since):
    command = ['sudo', '-n', 'journalctl', '-b', '--no-pager', '-n', '100', '-o', 'json',
               '--since', '@'+str(since), *(['-k'] if unit == 'kernel' else ['-u', unit])]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=2)
        if result.returncode:
            return {'status': 'UNKNOWN', 'returncode': result.returncode}
        events = []
        for line in result.stdout.splitlines():
            row = json.loads(line)
            message = str(row.get('MESSAGE', ''))
            terms = [term for term in ('out of memory', 'oom-kill', 'killed process', 'memory pressure',
                     'shutdown', 'sigterm', 'cancel', 'stopping') if term in message.lower()]
            if terms:
                reason = re.search(r'\breason\W{1,8}([A-Za-z][A-Za-z0-9_.-]{0,79})', message, re.I)
                events.append({'timestamp_us': row.get('__REALTIME_TIMESTAMP'),
                    'pid': row.get('_PID'), 'comm': row.get('_COMM'), 'matched_terms': terms,
                    'literal_reason_word': reason.group(1) if reason else 'UNKNOWN'})
        return {'status': 'read', 'last_entries_checked': len(result.stdout.splitlines()),
                'events': events, 'message_bodies_retained': False}
    except (OSError, subprocess.SubprocessError, ValueError):
        return {'status': 'UNKNOWN'}


def emit(value):
    line = json.dumps({'v6_host_observer': value}, separators=(',', ':'))
    try:
        # An observer-only broken pipe must not leave Python's buffered stdout
        # failed: its final flush would otherwise replace the model status with 120.
        os.write(1, (line+'\n').encode('utf-8'))
    except OSError:
        pass
    try:
        with REPORT.open('a', encoding='utf-8') as stream:
            stream.write(line+'\n')
    except OSError:
        pass  # stdout survives even if the owned local log cannot be written.


def observe(stop, pid, starttime):
    since = int(time.time())-30
    while not stop.is_set():
        try:
            memory = {}
            for line in read('/proc/meminfo').splitlines():
                key, _, value = line.partition(':')
                if key in ('MemTotal', 'MemAvailable', 'MemFree', 'SwapTotal', 'SwapFree', 'CommitLimit', 'Committed_AS'):
                    memory[key] = value.strip()
            disk = shutil.disk_usage('work')
            query_started = time.monotonic()
            logs = {name: journal(name, since) for name in ('kernel', 'hosted-compute-agent.service')}
            emit({'event': 'sample', 'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'memory': memory or 'UNKNOWN', 'memory_PSI': read('/proc/pressure/memory'),
                'root_cgroup_memory_events': read('/sys/fs/cgroup/memory.events'),
                'disk_bytes': {'free': disk.free, 'total': disk.total}, 'owned_model': owned(pid, starttime),
                'journal': logs, 'journal_query_wall_seconds': time.monotonic()-query_started,
                'observer_own_CPU_seconds': time.process_time()})
            since = int(time.time())
        except Exception as error:
            emit({'event': 'sample_unavailable', 'error_type': type(error).__name__, 'telemetry': 'UNKNOWN'})
        stop.wait(PERIOD)


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_REPOSITORY') != 'a-a-k/ebpf-model-discovery-experiments':
        raise RuntimeError('the fixed observed model computation is repository Actions only')
    REPORT.parent.mkdir(exist_ok=True)
    started = time.monotonic()
    process = subprocess.Popen(COMMAND)
    identity = proc(process.pid)
    emit({'event': 'observer_started', 'run_id': os.environ.get('GITHUB_RUN_ID'),
          'processing_source': os.environ.get('GITHUB_SHA'), 'period_seconds': PERIOD,
          'observer_pid': os.getpid(), 'model_identity': identity or 'UNKNOWN',
          'model_command': COMMAND})
    stop = threading.Event()
    thread = threading.Thread(target=observe, args=(stop, process.pid,
        identity['starttime_ticks'] if identity else None), daemon=True)
    thread.start()
    code = process.wait()
    stop.set()
    thread.join(timeout=6)
    emit({'event': 'model_finished', 'original_model_returncode': code,
          'model_and_observer_wall_seconds': time.monotonic()-started,
          'observer_own_CPU_seconds': time.process_time(), 'journal_children_CPU_seconds': 'UNKNOWN',
          'observer_overhead_is_not_zero': True})
    return code if code >= 0 else 128-code


if __name__ == '__main__':
    raise SystemExit(main())
