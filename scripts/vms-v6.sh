#!/usr/bin/env bash
# Fresh owned overlays of one NEW provisioned pair; never a historical VM cache.
set -euo pipefail
action=${1:?provision/start/stop/discard}
requested_root=${2:?checkout work directory required}
label=${3:-preparation}
[[ ${GITHUB_ACTIONS:-} == true ]] || { echo 'VM execution is GitHub Actions only' >&2; exit 2; }
[[ $action =~ ^(provision|start|stop|discard)$ && $label =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$ ]] || exit 2
script_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd -- "$script_root/.." && pwd)
python3 - "$requested_root" "$repo_root/work" <<'PY'
import pathlib,sys
p,w=map(pathlib.Path,sys.argv[1:]);p=p.absolute();w=w.resolve()
assert not any(x.is_symlink() for x in (p,*p.parents)), 'VM root cannot contain symlink components'
assert p.resolve().is_relative_to(w) and p.resolve()!=w, 'VM root must stay within this checkout/work'
PY
mkdir -p -- "$requested_root"
root=$(realpath -- "$requested_root")
mkdir -p "$root/history" "$root/events"
event="$root/events/$(date -u +%Y%m%dT%H%M%S)-$action-$label-$$.json"
started_ns=$(date +%s%N)
finish() {
  result=$?
  python3 - "$event" "$action" "$label" "$started_ns" "$result" <<'PY'
import json,pathlib,sys,time
p,a,l,s,r=sys.argv[1:]
pathlib.Path(p).write_text(json.dumps({'action':a,'label':l,'started_ns':int(s),'ended_ns':time.time_ns(),'exit_status':int(r)},indent=2)+'\n')
PY
}
trap finish EXIT
reserve=$((2*1024*1024*1024))
space() {
  python3 - "$root" "$1" "$reserve" <<'PY'
import json,pathlib,shutil,sys,time
p=pathlib.Path(sys.argv[1]); incoming,reserve=map(int,sys.argv[2:]); free=shutil.disk_usage(p).free
row={'at_ns':time.time_ns(),'free_bytes':free,'incoming_bytes':incoming,'reserve_bytes':reserve}
with (p/'disk-guards.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
assert free>=incoming+reserve, 'insufficient actual VM volume space'
PY
}
wait_stopped() {
  sudo python3 - "$1" <<'PY'
import pathlib,sys,time
p=pathlib.Path(sys.argv[1]); deadline=time.monotonic()+90
while True:
    alive=[]
    for n in ('a','b'):
        f=p/(n+'.pid')
        if not f.exists():continue
        q=pathlib.Path('/proc')/f.read_text().strip()
        try:
            state=(q/'stat').read_text().rsplit(') ',1)[1].split()[0]
        except FileNotFoundError:continue
        if state!='Z':alive.append(n)
    if not alive:break
    assert time.monotonic()<deadline, 'owned guests did not stop; disks remain untouched'
    time.sleep(.25)
PY
}
verify_golden() {
  python3 - "$root/golden" "${V6_GOLDEN_SHA256:-}" <<'PY'
import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); expected=sys.argv[2]; m=p/'manifest.json'
sha=lambda x:hashlib.file_digest(x.open('rb'),'sha256').hexdigest()
if expected:assert sha(m)==expected, 'parent-bound golden manifest differs'
v=json.loads(m.read_text());assert v['schema']=='v6-new-provisioned-pair-v1'
assert v['run_id']==__import__('os').environ['GITHUB_RUN_ID'] or expected, 'cross-job restore requires explicit golden SHA'
for name,row in v['files'].items():
    q=p/name;assert q.is_file() and not q.is_symlink() and q.resolve().is_relative_to(p.resolve())
    assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'], name
assert set(v['files'])=={'a.qcow2','b.qcow2','id_ed25519','id_ed25519.pub'}
print(sha(m))
PY
}
if [[ $action == provision ]]; then
  [[ ! -e "$root/golden" && ! -e "$root/preparation" && ! -e "$root/active" ]] || { echo 'provision requires an unused root' >&2; exit 3; }
  [[ -e /dev/kvm ]] || exit 3
  space $((2*24*1024*1024*1024))
  bash "$script_root/vms.sh" start "$root/preparation"
  for node in a b; do
    [[ $node == a ]] && suffix=11 || suffix=12
    ssh -i "$root/preparation/id_ed25519" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "ubuntu@192.168.76.$suffix" 'bash -se' > "$root/preparation/$node/golden-guest.txt" <<'GUEST'
test -z "$(docker ps -aq)"
test -z "$(docker image ls -q)"
test -z "$(docker volume ls -q)"
! ps -eo comm= | grep -Ex 'obi|beyla|coroot-node-age|deepflow-agent'
sudo systemctl disable --now apt-daily.timer apt-daily-upgrade.timer unattended-upgrades.service || true
sudo systemctl mask apt-daily.service apt-daily-upgrade.service unattended-upgrades.service
uname -r
docker version --format '{{.Server.Version}}'
dpkg-query -W -f='${Package}\t${Version}\n'
sudo cloud-init clean --logs --machine-id
sync
GUEST
  done
  bash "$script_root/vms.sh" stop "$root/preparation" > "$root/preparation/owned-stop.json"
  wait_stopped "$root/preparation"
  mkdir "$root/golden"
  for node in a b; do
    needed=$(qemu-img measure --output=json -O qcow2 "$root/preparation/$node/root.qcow2" | python3 -c 'import json,sys;print(json.load(sys.stdin)["required"])')
    space "$needed"
    sudo qemu-img convert -O qcow2 "$root/preparation/$node/root.qcow2" "$root/golden/$node.qcow2"
    sudo chown "$(id -u):$(id -g)" "$root/golden/$node.qcow2"
    qemu-img check -q "$root/golden/$node.qcow2"
    qemu-img info --output=json "$root/golden/$node.qcow2" | python3 -c 'import json,sys;v=json.load(sys.stdin);assert v["format"]=="qcow2" and not v.get("backing-filename") and v["virtual-size"]==24*1024**3'
    chmod a-w "$root/golden/$node.qcow2"
  done
  cp "$root/preparation/id_ed25519" "$root/preparation/id_ed25519.pub" "$root/golden/"
  python3 - "$root" <<'PY'
import hashlib,json,os,pathlib,subprocess,time
p=pathlib.Path(__import__('sys').argv[1]);g=p/'golden'
files={n:{'bytes':(g/n).stat().st_size,'sha256':hashlib.file_digest((g/n).open('rb'),'sha256').hexdigest()} for n in ('a.qcow2','b.qcow2','id_ed25519','id_ed25519.pub')}
base=json.loads((p/'preparation/infrastructure.json').read_text())
value={'schema':'v6-new-provisioned-pair-v1','run_id':os.environ['GITHUB_RUN_ID'],'source':os.environ['GITHUB_SHA'],'prepared_at_ns':time.time_ns(),'files':files,'guest_memory_mib':base['guest_memory_mib'],'preparation_boots':{n:(p/'preparation'/n/'check.txt').read_text().splitlines()[1] for n in ('a','b')},'guest_baseline':{n:(p/'preparation'/n/'golden-guest.txt').read_text() for n in ('a','b')},'no_application_or_agent':True,'host_cpu_count':os.cpu_count(),'host_memory':pathlib.Path('/proc/meminfo').read_text(),'qemu_version':subprocess.check_output(['qemu-system-x86_64','--version'],text=True)}
(g/'manifest.json').write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
(p/'network-owned.json').write_text(json.dumps({'run_id':os.environ['GITHUB_RUN_ID'],'root':str(p)})+'\n')
PY
  verify_golden
  exit 0
fi
active="$root/active"
if [[ $action == stop || $action == discard ]]; then
  python3 - "$active" "$label" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]);assert not p.is_symlink()
v=json.loads((p/'owner.json').read_text());assert v['label']==sys.argv[2], 'foreign active label'
assert v['run_id']==__import__('os').environ['GITHUB_RUN_ID'], 'foreign owner run'
PY
  if [[ $action == stop ]]; then
    bash "$script_root/vms.sh" stop "$active" > "$active/owned-stop.json"
    wait_stopped "$active"
    python3 - "$active/owner.json" <<'PY'
import json,pathlib,sys,time
p=pathlib.Path(sys.argv[1]);v=json.loads(p.read_text());v.update(status='stopped',stopped_ns=time.time_ns());p.write_text(json.dumps(v,indent=2)+'\n')
PY
  else
    wait_stopped "$active"
    python3 - "$active" "$root/history/$label" <<'PY'
import json,pathlib,shutil,sys
p,h=map(pathlib.Path,sys.argv[1:]);v=json.loads((p/'owner.json').read_text());assert v['status']=='stopped'
assert not h.exists();h.mkdir()
allowed={'owner.json','id_ed25519','id_ed25519.pub','infrastructure.json','owned-stop.json','a.pid','b.pid'}
child={'root.qcow2','seed.img','user-data','meta-data','network-config','serial.log','check.txt'}
for q in p.iterdir():
    assert not q.is_symlink()
    if q.is_dir():
        assert q.name in {'a','b'}; (h/q.name).mkdir()
        for f in q.iterdir():
            assert f.name in child and f.is_file() and not f.is_symlink()
            if f.name!='root.qcow2':shutil.copy2(f,h/q.name/f.name)
            f.unlink()
        q.rmdir()
    else:
        assert q.name in allowed and q.is_file()
        if not q.name.startswith('id_ed25519'):shutil.copy2(q,h/q.name)
        q.unlink()
p.rmdir()
PY
  fi
  exit 0
fi
[[ ! -e "$active" && ! -e "$root/history/$label" ]] || { echo 'stop/discard the owned active pair first; labels never repeat' >&2; exit 3; }
[[ ${V6_GOLDEN_SHA256:-} =~ ^[a-f0-9]{64}$ ]] || { echo 'start requires the common parent golden SHA' >&2; exit 3; }
golden_sha=$(verify_golden)
[[ -e /dev/kvm ]] || exit 3
if ! command -v qemu-system-x86_64 >/dev/null || ! command -v cloud-localds >/dev/null; then
  sudo apt-get update -qq -o Acquire::Retries=1 -o Acquire::http::Timeout=20 -o Acquire::https::Timeout=20
  sudo apt-get install -y -qq --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils jq
fi
space $((2*24*1024*1024*1024))
guest_memory=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["guest_memory_mib"])' "$root/golden/manifest.json")
memory_kib=$(awk '/MemTotal/{print $2}' /proc/meminfo)
(( memory_kib >= 2*guest_memory*1024+768*1024 )) || { echo 'host too small for identical golden guest RAM' >&2; exit 3; }
if ip link show br-ebpf >/dev/null 2>&1; then
  [[ -f "$root/network-owned.json" ]] || { echo 'foreign pre-existing VM bridge' >&2; exit 3; }
else
  sudo ip link add br-ebpf type bridge
  sudo ip addr add 192.168.76.1/24 dev br-ebpf
  sudo ip link set br-ebpf up
fi
sudo sysctl -w net.ipv4.ip_forward=1
iface=$(ip -j route show default | jq -r '.[0].dev')
sudo iptables -t nat -C POSTROUTING -s 192.168.76.0/24 -o "$iface" -j MASQUERADE 2>/dev/null || sudo iptables -t nat -A POSTROUTING -s 192.168.76.0/24 -o "$iface" -j MASQUERADE
sudo iptables -C FORWARD -i br-ebpf -j ACCEPT 2>/dev/null || sudo iptables -A FORWARD -i br-ebpf -j ACCEPT
sudo iptables -C FORWARD -o br-ebpf -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || sudo iptables -A FORWARD -o br-ebpf -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
mkdir "$active"
cp "$root/golden/id_ed25519" "$root/golden/id_ed25519.pub" "$active/"
chmod 600 "$active/id_ed25519"
python3 - "$active/owner.json" "$label" "$golden_sha" <<'PY'
import json,os,pathlib,sys,time
p,l,s=sys.argv[1:];pathlib.Path(p).write_text(json.dumps({'label':l,'golden_sha256':s,'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ.get('GITHUB_RUN_ATTEMPT','1'),'status':'starting','started_ns':time.time_ns()},indent=2)+'\n')
PY
pubkey=$(cat "$active/id_ed25519.pub")
nonce=$(python3 -c 'import uuid;print(uuid.uuid4())')
for node in a b; do
  if [[ $node == a ]]; then suffix=11; peer=12; mac=52:54:00:76:00:11; else suffix=12; peer=11; mac=52:54:00:76:00:12; fi
  mkdir "$active/$node"
  qemu-img create -f qcow2 -F qcow2 -b "$root/golden/$node.qcow2" "$active/$node/root.qcow2"
  cat > "$active/$node/user-data" <<EOF
#cloud-config
hostname: ebpf-$node
users:
  - name: ubuntu
    groups: [sudo, docker]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - $pubkey
package_update: false
package_upgrade: false
runcmd:
  - systemctl enable --now docker
  - ip route replace 172.28.$peer.0/24 via 192.168.76.$peer
  - iptables -I DOCKER-USER -j ACCEPT
EOF
  printf 'instance-id: v6-%s-%s-%s\nlocal-hostname: ebpf-%s\n' "$label" "$node" "$nonce" "$node" > "$active/$node/meta-data"
  cat > "$active/$node/network-config" <<EOF
version: 2
ethernets:
  eth0:
    match: {macaddress: $mac}
    set-name: eth0
    addresses: [192.168.76.$suffix/24]
    routes: [{to: default, via: 192.168.76.1}]
    nameservers: {addresses: [1.1.1.1, 8.8.8.8]}
EOF
  cloud-localds --network-config="$active/$node/network-config" "$active/$node/seed.img" "$active/$node/user-data" "$active/$node/meta-data"
  if ! ip link show "tap-$node" >/dev/null 2>&1; then sudo ip tuntap add "tap-$node" mode tap; fi
  sudo ip link set "tap-$node" master br-ebpf
  sudo ip link set "tap-$node" up
  sudo qemu-system-x86_64 -enable-kvm -cpu host -smp 2 -m "$guest_memory" \
    -drive "file=$active/$node/root.qcow2,format=qcow2,if=virtio" \
    -drive "file=$active/$node/seed.img,format=raw,if=virtio" \
    -netdev "tap,id=n0,ifname=tap-$node,script=no,downscript=no" \
    -device "virtio-net-pci,netdev=n0,mac=$mac" \
    -display none -serial "file:$active/$node/serial.log" -daemonize -pidfile "$active/$node.pid"
  sudo ip route replace "172.28.$suffix.0/24" via "192.168.76.$suffix"
done
for node in a b; do
  [[ $node == a ]] && suffix=11 || suffix=12
  args=(-i "$active/id_ed25519" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5)
  ready=false
  for attempt in $(seq 1 90); do
    if ssh "${args[@]}" "ubuntu@192.168.76.$suffix" true 2>/dev/null; then ready=true; break; fi
    sleep 5
  done
  [[ $ready == true ]] || exit 4
  timeout 600 ssh "${args[@]}" "ubuntu@192.168.76.$suffix" 'sudo cloud-init status --wait'
  ssh "${args[@]}" "ubuntu@192.168.76.$suffix" 'set -e; uname -r; cat /proc/sys/kernel/random/boot_id; test -r /sys/kernel/btf/vmlinux; docker version --format "{{.Server.Version}}"; test -z "$(docker ps -aq)"; test -z "$(docker image ls -q)"; test -z "$(docker volume ls -q)"; free -m' > "$active/$node/check.txt"
done
python3 - "$root" "$label" "$golden_sha" <<'PY'
import json,os,pathlib,sys,time
p=pathlib.Path(sys.argv[1]);a=p/'active';g=json.loads((p/'golden/manifest.json').read_text());nodes={n:(a/n/'check.txt').read_text() for n in ('a','b')};boots=[x.splitlines()[1] for x in nodes.values()]
previous=list(g['preparation_boots'].values())
for old in (p/'history').glob('*/infrastructure.json'):previous.extend(json.loads(old.read_text())['boot_ids'].values())
assert len(set(boots))==2 and not set(boots).intersection(previous), 'fresh independent boots required'
for n,text in nodes.items():
    reference=g['guest_baseline'][n].splitlines();assert text.splitlines()[0]==reference[0] and text.splitlines()[2]==reference[1], 'guest kernel/Docker drift'
value={'status':'ready','label':sys.argv[2],'golden_sha256':sys.argv[3],'shared_physical_host':True,'guest_memory_mib':g['guest_memory_mib'],'boot_ids':dict(zip(nodes,boots)),'nodes':nodes,'qemu_host_version':__import__('subprocess').check_output(['qemu-system-x86_64','--version'],text=True)}
(a/'infrastructure.json').write_text(json.dumps(value,indent=2)+'\n');owner=json.loads((a/'owner.json').read_text());owner.update(status='ready',ready_ns=time.time_ns());(a/'owner.json').write_text(json.dumps(owner,indent=2)+'\n')
(p/'network-owned.json').write_text(json.dumps({'run_id':os.environ['GITHUB_RUN_ID'],'root':str(p)})+'\n')
PY
