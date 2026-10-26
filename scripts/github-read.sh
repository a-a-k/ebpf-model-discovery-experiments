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
  echo "GitHub API read failed after three attempts: $*" >&2
  return 1
}
