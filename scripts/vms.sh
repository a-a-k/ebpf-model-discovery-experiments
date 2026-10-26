#!/usr/bin/env bash
set -euo pipefail
action=${1:-start}
study_work=${2:-work/vms}
mkdir -p "$study_work"
study_work=$(realpath "$study_work")
if [[ "$action" == stop ]]; then
  for node in a b; do
    if [[ -f "$study_work/$node.pid" ]]; then
      sudo kill "$(sudo cat "$study_work/$node.pid")" 2>/dev/null || true
    fi
  done
  exit 0
fi
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'VM execution is GitHub Actions only' >&2; exit 2; }
[[ -e /dev/kvm ]] || { echo 'KVM unavailable: no container or emulation substitution' >&2; exit 3; }
sudo apt-get update -qq -o Acquire::Retries=1 -o Acquire::http::Timeout=20 -o Acquire::https::Timeout=20
sudo apt-get install -y -qq --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils jq
mkdir -p "$study_work/image"
curl --fail --location --retry 3 -o "$study_work/image/base.img" https://cloud-images.ubuntu.com/noble/20261017/noble-server-cloudimg-amd64.img
curl --fail --location --retry 3 -o "$study_work/image/SHA256SUMS" https://cloud-images.ubuntu.com/noble/20261017/SHA256SUMS
python3 - "$study_work/image" <<'PY'
import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1])
expected=[x.split()[0] for x in (p/'SHA256SUMS').read_text().splitlines() if x.split()[-1].lstrip('*')=='noble-server-cloudimg-amd64.img']
actual=hashlib.file_digest((p/'base.img').open('rb'),'sha256').hexdigest()
assert expected==[actual], (expected,actual)
assert actual=='04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94', 'pinned guest image changed'
(p.parent/'image-provenance.json').write_text(json.dumps({'url':'https://cloud-images.ubuntu.com/noble/20261017/noble-server-cloudimg-amd64.img','sha256':actual},indent=2))
PY
ssh-keygen -q -t ed25519 -N '' -f "$study_work/id_ed25519"
pubkey=$(cat "$study_work/id_ed25519.pub")
sudo ip link add br-ebpf type bridge
sudo ip addr add 192.168.76.1/24 dev br-ebpf
sudo ip link set br-ebpf up
sudo sysctl -w net.ipv4.ip_forward=1
iface=$(ip -j route show default | jq -r '.[0].dev')
sudo iptables -t nat -A POSTROUTING -s 192.168.76.0/24 -o "$iface" -j MASQUERADE
sudo iptables -A FORWARD -i br-ebpf -j ACCEPT
sudo iptables -A FORWARD -o br-ebpf -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
memory_kib=$(awk '/MemTotal/{print $2}' /proc/meminfo)
guest_memory=6144
if (( memory_kib < 14000000 )); then guest_memory=3072; fi
for node in a b; do
  if [[ "$node" == a ]]; then suffix=11; peer=12; mac=52:54:00:76:00:11; else suffix=12; peer=11; mac=52:54:00:76:00:12; fi
  mkdir -p "$study_work/$node"
  qemu-img create -f qcow2 -F qcow2 -b "$study_work/image/base.img" "$study_work/$node/root.qcow2" 24G
  cat > "$study_work/$node/user-data" <<EOF
#cloud-config
hostname: ebpf-$node
users:
  - name: ubuntu
    groups: [sudo]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - $pubkey
package_update: true
packages: [docker.io, docker-compose-v2, python3, python3-requests, curl, jq, tcpdump]
write_files:
  - path: /etc/sysctl.d/90-ebpf-study.conf
    content: |
      net.ipv4.ip_forward=1
runcmd:
  - systemctl enable --now docker
  - usermod -aG docker ubuntu
  - sysctl --system
  - ip route replace 172.28.$peer.0/24 via 192.168.76.$peer
  - iptables -I DOCKER-USER -j ACCEPT
EOF
  printf 'instance-id: ebpf-%s-%s\nlocal-hostname: ebpf-%s\n' "$node" "$GITHUB_RUN_ID" "$node" > "$study_work/$node/meta-data"
  cat > "$study_work/$node/network-config" <<EOF
version: 2
ethernets:
  eth0:
    match:
      macaddress: $mac
    set-name: eth0
    addresses: [192.168.76.$suffix/24]
    routes:
      - to: default
        via: 192.168.76.1
    nameservers:
      addresses: [1.1.1.1, 8.8.8.8]
EOF
  cloud-localds --network-config="$study_work/$node/network-config" "$study_work/$node/seed.img" "$study_work/$node/user-data" "$study_work/$node/meta-data"
  sudo ip tuntap add "tap-$node" mode tap
  sudo ip link set "tap-$node" master br-ebpf
  sudo ip link set "tap-$node" up
  sudo qemu-system-x86_64 -enable-kvm -cpu host -smp 2 -m "$guest_memory" \
    -drive "file=$study_work/$node/root.qcow2,format=qcow2,if=virtio" \
    -drive "file=$study_work/$node/seed.img,format=raw,if=virtio" \
    -netdev "tap,id=n0,ifname=tap-$node,script=no,downscript=no" \
    -device "virtio-net-pci,netdev=n0,mac=$mac" \
    -display none -serial "file:$study_work/$node/serial.log" \
    -daemonize -pidfile "$study_work/$node.pid"
  sudo ip route replace "172.28.$suffix.0/24" via "192.168.76.$suffix"
done
for node in a b; do
  if [[ "$node" == a ]]; then suffix=11; else suffix=12; fi
  ssh_args=(-i "$study_work/id_ed25519" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5)
  ready=false
  for attempt in $(seq 1 90); do
    if ssh "${ssh_args[@]}" "ubuntu@192.168.76.$suffix" true 2>/dev/null; then ready=true; break; fi
    sleep 5
  done
  [[ "$ready" == true ]] || { echo "SSH did not start: $node" >&2; exit 4; }
  timeout 600 ssh "${ssh_args[@]}" "ubuntu@192.168.76.$suffix" 'sudo cloud-init status --wait'
  ssh "${ssh_args[@]}" "ubuntu@192.168.76.$suffix" 'uname -r; cat /proc/sys/kernel/random/boot_id; test -r /sys/kernel/btf/vmlinux; docker version --format "{{.Server.Version}}"; free -m' > "$study_work/$node/check.txt"
done
python3 - "$study_work" "$guest_memory" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); nodes={n:(p/n/'check.txt').read_text() for n in ('a','b')}
assert nodes['a'].splitlines()[1]!=nodes['b'].splitlines()[1], 'guest kernels not independent'
(p/'infrastructure.json').write_text(json.dumps({'status':'ready','guest_memory_mib':int(sys.argv[2]),'nodes':nodes,'shared_physical_host':True},indent=2))
PY
