#!/usr/bin/env bash
set -u

out=${1:?resource output directory required}
interval=${2:-15}
vm_dir=${3:-work/vms}
mkdir -p "$out"

ssh_args=(-i "$vm_dir/id_ed25519" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5)

while true; do
  now=$(date --utc +%Y-%m-%dT%H:%M:%S.%NZ)
  {
    echo "===== $now runner ====="
    free -b
    df -B1 . "$vm_dir" 2>&1
    ps -eo pid,ppid,rss,vsz,%cpu,%mem,etimes,comm,args --sort=-rss | head -n 40
  } >> "$out/runner-samples.txt" 2>&1

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
  sleep "$interval"
done
