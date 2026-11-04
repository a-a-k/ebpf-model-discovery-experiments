set -euo pipefail
vm_root=$(realpath "$1")
campaign_root=$(realpath "$2")
ssh_args=(-i "$vm_root/id_ed25519" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10)
for n in a b; do
  destination="$campaign_root/infrastructure/$n"
  mkdir -p "$destination"
  cp "$vm_root/$n/check.txt" "$destination/" 2> "$destination/check-copy.err" || true
  if sudo test -f "$vm_root/$n/serial.log" 2> "$destination/serial-test.err"; then
    sudo stat -- "$vm_root/$n/serial.log" > "$destination/serial-stat.txt" 2> "$destination/serial-stat.err" || true
    if timeout 30 sudo cat -- "$vm_root/$n/serial.log" > "$destination/serial.log" 2> "$destination/serial-copy.err"; then
      echo 0 > "$destination/serial-copy.returncode"
    else
      echo "$?" > "$destination/serial-copy.returncode"
    fi
  else
    echo "$?" > "$destination/serial-test.returncode"
    echo owned_vm_serial_unavailable_as_regular_file > "$destination/serial-copy.status"
  fi
  case "$n" in a) address=192.168.76.11 ;; b) address=192.168.76.12 ;; esac
  if timeout 30 ssh "${ssh_args[@]}" "ubuntu@$address" 'sudo dmesg --time-format iso' \
      > "$destination/guest-kernel-final.txt" 2> "$destination/guest-kernel-final.err"; then
    echo 0 > "$destination/guest-kernel-final.returncode"
  else
    echo "$?" > "$destination/guest-kernel-final.returncode"
  fi
done
