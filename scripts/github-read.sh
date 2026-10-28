#!/usr/bin/env bash
# Retry read-only API failures; never leave a truncated JSON evidence file.
gh_api_to_file() {
  local destination="$1" attempt
  shift
  for attempt in 1 2 3; do
    if gh api "$@" > "${destination}.tmp"; then
      mv "${destination}.tmp" "$destination"
      return 0
    fi
    if [[ "$attempt" -lt 3 ]]; then sleep "$((attempt * 3))"; fi
  done
  rm -f "${destination}.tmp"
  echo "GitHub API read failed after three attempts: $*" >&2
  return 1
}

# A completed Actions job may have no log blob after its runner disappears.
# Record only that specific API absence; auth, network and server errors fail.
gh_api_optional_log_to_file() {
  local destination="$1" status_file="$2" endpoint="$3" attempt code
  for attempt in 1 2 3; do
    if gh api "$endpoint" > "${destination}.tmp" 2> "${destination}.error.tmp"; then
      mv "${destination}.tmp" "$destination"
      rm -f "${destination}.error.tmp"
      jq -n --arg endpoint "$endpoint" --arg file "$(basename "$destination")" \
        '{endpoint:$endpoint, state:"available", file:$file}' > "$status_file"
      return 0
    fi
    # gh emits both "gh: HTTP 404 ..." and "gh: Not Found (HTTP 404)".
    code="$(grep '^gh:' "${destination}.error.tmp" | grep -oE 'HTTP [0-9]{3}' | head -n 1 | cut -d' ' -f2 || true)"
    rm -f "${destination}.tmp"
    if [[ "$code" == 404 || "$code" == 410 ]]; then
      rm -f "$destination"
      jq -n --arg endpoint "$endpoint" --argjson code "$code" \
        '{endpoint:$endpoint, state:"unavailable", http_status:$code}' > "$status_file"
      rm -f "${destination}.error.tmp"
      return 0
    fi
    if [[ "$code" =~ ^4[0-9][0-9]$ ]]; then
      cat "${destination}.error.tmp" >&2
      rm -f "${destination}.error.tmp"
      return 1
    fi
    if [[ "$attempt" -lt 3 ]]; then sleep "$((attempt * 3))"; fi
  done
  cat "${destination}.error.tmp" >&2
  rm -f "${destination}.error.tmp"
  echo "GitHub log read failed after three attempts: $endpoint" >&2
  return 1
}
