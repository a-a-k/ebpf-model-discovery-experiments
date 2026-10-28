#!/usr/bin/env bash
set -u
out=${1:?resource output directory required}
interval=${2:-15}
vm_dir=${3:-work/vms}
mkdir -p "$out"
ssh_args=(-i "$vm_dir/id_ed25519" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5)
while true; do
  now=$(date --utc +%Y-%m-%dT%H:%M:%S.%NZ)
  # This concise copy survives a lost runner because it also enters Actions logs.
  python3 - "$now" "$out" <<'PY'
import json,pathlib,subprocess,sys
now,out=sys.argv[1:]
memory={k:int(v.split()[0]) for k,v in (line.split(':',1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines())}
vmstat=dict(line.split() for line in pathlib.Path('/proc/vmstat').read_text().splitlines())
pressure=pathlib.Path('/proc/pressure/memory')
cgroup=pathlib.Path('/sys/fs/cgroup/memory.events')
read_errors={}
def optional_read(path):
    try:
        return path.read_text().strip()
    except OSError as exc:
        read_errors[str(path)]=repr(exc)
        return None
row={'resource_heartbeat':now,'mem_available_kib':memory.get('MemAvailable'),
     'mem_total_kib':memory.get('MemTotal'),'swap_total_kib':memory.get('SwapTotal'),
     'swap_free_kib':memory.get('SwapFree'),'swap_pages_in':vmstat.get('pswpin'),
     'swap_pages_out':vmstat.get('pswpout'),'oom_kill_counter':vmstat.get('oom_kill'),
     'memory_pressure':optional_read(pressure),
     'root_cgroup_memory_events':optional_read(cgroup),'read_errors':read_errors}
print(json.dumps(row,separators=(',',':')),flush=True)
with pathlib.Path(out,'heartbeats.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
PY
  heartbeat_rc=$?
  if [[ "$heartbeat_rc" != 0 ]]; then
    echo "resource_heartbeat_failure $now returncode=$heartbeat_rc" | tee -a "$out/errors.txt"
  fi
  {
    echo "===== $now runner ====="
    free -b
    df -B1 . "$vm_dir" 2>&1
    swapon --show --bytes
    ps -eo pid,ppid,rss,vsz,%cpu,%mem,etimes,comm,args --sort=-rss | head -n 40
    cat /proc/vmstat
  } >> "$out/runner-samples.txt" 2>&1
  echo "resource_process_rss $now"
  ps -eo pid,ppid,rss,comm --sort=-rss | head -n 10
  for item in a:192.168.76.11 b:192.168.76.12; do
    node=${item%%:*}
    address=${item#*:}
    {
      echo "===== $now guest-$node ====="
      ssh "${ssh_args[@]}" "ubuntu@$address" \
        'free -b; df -B1 / /var/lib/docker; cat /proc/loadavg; docker stats --no-stream --format "{{json .}}"' 2>&1
      echo "ssh_returncode=$?"
    } >> "$out/guest-$node-samples.txt" 2>&1
  done
  sudo dmesg --time-format iso > "$out/kernel-latest.txt" 2> "$out/kernel-read.err" || true
  sleep "$interval"
done
