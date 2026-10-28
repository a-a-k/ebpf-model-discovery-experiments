#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'Swap setup is Actions-only' >&2; exit 2; }
out=${1:?resource evidence directory required}
mkdir -p "$out"
out=$(realpath "$out")
workspace=$(realpath "${GITHUB_WORKSPACE:?}")
target="$workspace/work/v4-swapfile"
mkdir -p "$workspace/work"
[[ "$(realpath -m "$target")" == "$target" ]] || { echo 'Unexpected swap path' >&2; exit 2; }
[[ ! -e "$target" ]] || { echo 'Refusing to replace an existing swap file' >&2; exit 2; }
started_ns=$(date +%s%N)
python3 - "$out" "$target" "$started_ns" <<'PY'
import json,pathlib,shutil,sys
out,target,started=sys.argv[1:]
pathlib.Path(out,'swap-before.json').write_text(json.dumps({
    'requested_additional_bytes':8*1024**3,'path':target,'started_ns':int(started),
    'disk_free_bytes':shutil.disk_usage(pathlib.Path(target).parent).free,
    'meminfo':pathlib.Path('/proc/meminfo').read_text(),
    'vmstat':pathlib.Path('/proc/vmstat').read_text(),
    'rule':'standard-runner local disk; no observation, trial or business deadline change',
},indent=2)+'\n')
PY
finish() {
  rc=$?
  trap - EXIT
  swapon --show --bytes > "$out/swapon-after.txt" 2>&1 || true
  python3 - "$out" "$target" "$started_ns" "$rc" <<'PY'
import json,pathlib,shutil,sys,time
out,target,started,rc=sys.argv[1:]
ended=time.time_ns()
pathlib.Path(out,'swap-after.json').write_text(json.dumps({
    'status':'ready' if int(rc)==0 else 'technical_setup_failure','returncode':int(rc),
    'requested_additional_bytes':8*1024**3,'path':target,
    'started_ns':int(started),'ended_ns':ended,'elapsed_seconds':(ended-int(started))/1e9,
    'disk_free_bytes':shutil.disk_usage(pathlib.Path(target).parent).free,
    'meminfo':pathlib.Path('/proc/meminfo').read_text(),
    'vmstat':pathlib.Path('/proc/vmstat').read_text(),
},indent=2)+'\n')
PY
  exit "$rc"
}
trap finish EXIT
sudo install -m 600 /dev/null "$target"
sudo fallocate -l 8G "$target"
sudo mkswap "$target" > "$out/mkswap.txt" 2>&1
sudo swapon "$target" 2> "$out/swapon.err"
echo 'Additional 8 GiB swap enabled on standard runner local disk; allocation evidence retained.'
