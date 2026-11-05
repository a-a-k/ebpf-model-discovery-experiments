#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/github-read.sh"

: "${GITHUB_REPOSITORY:?}"
: "${RUN_IDS:?}"
archive_dir="${ARCHIVE_DIR:-work/archive}"
max_asset_bytes="${ARCHIVE_MAX_ASSET_BYTES:-2147483648}"
chunk_bytes="${ARCHIVE_CHUNK_BYTES:-1073741824}"
[[ "$max_asset_bytes" =~ ^[0-9]+$ && "$chunk_bytes" =~ ^[0-9]+$ ]] || exit 2
(( max_asset_bytes > 1 && max_asset_bytes <= 2147483648 &&
   chunk_bytes > 0 && chunk_bytes < max_asset_bytes )) || exit 2
mkdir -p "$archive_dir"
release_tag="${ARCHIVE_RELEASE_TAG:-}"
release_id="${ARCHIVE_RELEASE_ID:-}"
if [[ ( -n "$release_tag" && -z "$release_id" ) || ( -z "$release_tag" && -n "$release_id" ) ]]; then
  echo 'Incremental publication requires both release tag and ID' >&2; exit 2
fi
if [[ -n "$release_tag" ]]; then
  : "${GITHUB_SHA:?}" "${GITHUB_RUN_ID:?}"
  [[ "$release_tag" == "data-${GITHUB_RUN_ID}" ]] || exit 2
  release_id="${ARCHIVE_RELEASE_ID:?}"
  [[ "$release_id" =~ ^[1-9][0-9]*$ ]] || exit 2
  gh_api_to_file "$archive_dir/release-before.json" \
    "repos/${GITHUB_REPOSITORY}/releases/$release_id"
  jq -e --arg tag "$release_tag" --arg head "$GITHUB_SHA" \
    '.draft == true and .tag_name == $tag and .target_commitish == $head' \
    "$archive_dir/release-before.json" >/dev/null
  [[ "$(jq -r .id "$archive_dir/release-before.json")" == "$release_id" ]] || exit 2
fi

publish_verified_working_copy() {
  local original="$1" file name digest size proof asset_id
  [[ -n "$release_tag" ]] || return 0
  shopt -s nullglob
  local files=("$original")
  [[ -f "$original" ]] || files=("$original".part[0-9][0-9][0-9][0-9])
  for file in "${files[@]}"; do
    name="$(basename "$file")"
    [[ "$name" =~ ^[a-zA-Z0-9._-]+$ ]] || exit 2 # URL-unreserved generated names only.
    digest="$(sha256sum "$file")"; digest="${digest%% *}"
    size="$(stat -c%s "$file")"
    gh api --method POST -H 'Content-Type: application/octet-stream' -H 'Accept: application/vnd.github+json' \
      "https://uploads.github.com/repos/${GITHUB_REPOSITORY}/releases/$release_id/assets?name=$name" \
      --input "$file" > "$archive_dir/published-upload-response.json"
    asset_id="$(jq -r .id "$archive_dir/published-upload-response.json")"
    [[ "$asset_id" =~ ^[1-9][0-9]*$ ]] || exit 2
    proof="$archive_dir/published-asset-response.json"
    gh_api_to_file "$proof" \
      "repos/${GITHUB_REPOSITORY}/releases/assets/$asset_id"
    jq -e --arg name "$name" --arg digest "sha256:$digest" --argjson size "$size" --argjson id "$asset_id" \
      '.id == $id and .name == $name and .state == "uploaded" and .size == $size and .digest == $digest' \
      "$proof" >/dev/null
    jq -c --arg tag "$release_tag" --arg digest "$digest" --argjson release_id "$release_id" \
      '{release_id:$release_id, release_tag:$tag, asset_id:.id, filename:.name, bytes:.size,
        local_sha256:$digest, remote_digest:.digest, state:.state, asset_api_url:.url,
        observed_draft_download_url:.browser_download_url}' \
      "$proof" >> "$archive_dir/published-assets.jsonl"
    printf '%s  %s\n' "$digest" "$name" >> "$archive_dir/published-SHA256SUMS.txt"
    rm -f -- "$file"
  done
}

# GitHub release assets must be strictly under 2 GiB. Split only the retained
# local download; the source Actions artifact and its API digest stay intact.
maybe_chunk_asset() {
  local original="$1" kind="$2" api_digest="$3" status_file="${4:-}" size manifest
  [[ -f "$original" ]] || return 0
  size="$(stat -c%s "$original")"
  (( size >= max_asset_bytes )) || return 0
  split -b "$chunk_bytes" -d -a 4 "$original" "$original.part"
  manifest="$original.chunks.json"
  python3 - "$original" "$kind" "$api_digest" "$manifest" <<'PY'
import hashlib
import json
from pathlib import Path
import shlex
import sys

original, kind, api_digest, manifest = (Path(sys.argv[1]), sys.argv[2],
                                        sys.argv[3], Path(sys.argv[4]))
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

original_size = original.stat().st_size
original_sha = digest(original)
if api_digest != 'null' and api_digest.lower() != 'sha256:' + original_sha:
    raise SystemExit('Original archive digest differs from API digest')
parts = sorted(original.parent.glob(original.name + '.part[0-9][0-9][0-9][0-9]'))
if len(parts) < 2:
    raise SystemExit('Oversized archive did not produce multiple chunks')
joined = hashlib.sha256()
entries = []
offset = 0
for index, path in enumerate(parts):
    if path.name != f'{original.name}.part{index:04d}':
        raise SystemExit('Archive chunk sequence is incomplete')
    h = hashlib.sha256()
    count = 0
    with path.open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
            h.update(block)
            joined.update(block)
            count += len(block)
    entries.append({'filename': path.name, 'offset_bytes': offset,
                    'size_bytes': count, 'sha256': h.hexdigest()})
    offset += count
if offset != original_size or joined.hexdigest() != original_sha:
    raise SystemExit('Archive chunk reassembly differs from original bytes')
manifest.write_text(json.dumps({
    'schema_version': 'lossless-release-asset-chunks-v1',
    'source_kind': kind,
    'original_filename': original.name,
    'original_size_bytes': original_size,
    'original_sha256': original_sha,
    'source_api_digest': None if api_digest == 'null' else api_digest,
    'parts': entries,
    'reassembly_command': ('cat ' + ' '.join(shlex.quote(x['filename']) for x in entries)
                           + ' > ' + shlex.quote(original.name)),
    'verification': {'size_bytes': original_size, 'sha256': original_sha},
    'verification_command': (
        'test "$(stat -c%s ' + shlex.quote(original.name) + ')" -eq '
        + str(original_size) + " && printf '%s  %s\\n' " + shlex.quote(original_sha)
        + ' ' + shlex.quote(original.name) + ' | sha256sum -c -'),
}, indent=2) + '\n')
PY
  if [[ -n "$status_file" ]]; then
    jq --arg manifest "$(basename "$manifest")" --arg original "$(basename "$original")" \
      'del(.file) + {delivery:"chunked", original_filename:$original, chunks_manifest:$manifest}' \
      "$status_file" > "$status_file.tmp"
    mv "$status_file.tmp" "$status_file"
  fi
  rm -f "$original"
}

for run_id in $RUN_IDS; do
  [[ "$run_id" =~ ^[0-9]+$ ]] || { echo "Invalid run ID: $run_id" >&2; exit 2; }
  root="repos/${GITHUB_REPOSITORY}/actions/runs/$run_id"
  gh_api_to_file "$archive_dir/$run_id-run.json" "$root"
  [[ "$(jq -r .status "$archive_dir/$run_id-run.json")" == completed ]] || {
    echo "Run $run_id is not terminal" >&2; exit 2;
  }
  gh_api_to_file "$archive_dir/$run_id-artifact-index.json" "$root/artifacts?per_page=100"
  jq -e '.total_count == (.artifacts | length)' "$archive_dir/$run_id-artifact-index.json" >/dev/null || {
    echo "Incomplete artifact index for run $run_id" >&2; exit 2;
  }
  gh_api_to_file "$archive_dir/$run_id-jobs-pages.json" "$root/jobs?filter=all&per_page=100" --paginate --slurp
  jq -e 'length > 0 and .[0].total_count == ([.[].jobs[]] | length)' \
    "$archive_dir/$run_id-jobs-pages.json" >/dev/null || {
    echo "Incomplete job index for run $run_id" >&2; exit 2;
  }
  mapfile -t job_ids < <(jq -r '.[].jobs[].id' "$archive_dir/$run_id-jobs-pages.json")
  for job_id in "${job_ids[@]}"; do
    [[ "$job_id" =~ ^[0-9]+$ ]] || exit 2
    check_run_url="$(jq -r --argjson id "$job_id" \
      '[.[].jobs[] | select(.id == $id) | .check_run_url][0]' \
      "$archive_dir/$run_id-jobs-pages.json")"
    check_run_prefix="https://api.github.com/repos/${GITHUB_REPOSITORY}/check-runs/"
    [[ "$check_run_url" == "$check_run_prefix"* ]] || {
      echo "Invalid check-run URL for job $job_id" >&2; exit 2;
    }
    check_run_id="${check_run_url#"$check_run_prefix"}"
    [[ "$check_run_id" =~ ^[0-9]+$ ]] || exit 2
    check_run="$archive_dir/$run_id-job-$job_id-check-run.json"
    gh_api_to_file "$check_run" "repos/${GITHUB_REPOSITORY}/check-runs/$check_run_id"
    annotation_count="$(jq -r '.output.annotations_count' "$check_run")"
    [[ "$annotation_count" =~ ^[0-9]+$ ]] || exit 2
    annotations="$archive_dir/$run_id-job-$job_id-annotations.json"
    gh_api_to_file "$annotations" \
      "repos/${GITHUB_REPOSITORY}/check-runs/$check_run_id/annotations?per_page=100" --paginate --slurp
    jq -e --argjson expected "$annotation_count" \
      '([.[][]] | length) == $expected' "$annotations" >/dev/null || {
      echo "Incomplete annotations for job $job_id" >&2; exit 2;
    }
  done

  workflow_logs="$archive_dir/$run_id-workflow-logs.zip"
  gh_api_optional_log_to_file "$workflow_logs" \
    "$archive_dir/$run_id-workflow-logs-status.json" "$root/logs"
  if [[ -f "$workflow_logs" ]]; then
    python3 -c 'import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as archive:
    bad = archive.testzip()
if bad is not None:
    sys.exit("Corrupt workflow log ZIP member: " + bad)' "$workflow_logs"
  fi
  maybe_chunk_asset "$workflow_logs" workflow_log null \
    "$archive_dir/$run_id-workflow-logs-status.json"
  publish_verified_working_copy "$workflow_logs"
  # Whole-run ZIP presence does not prove that every job's log is inside it.
  for job_id in "${job_ids[@]}"; do
    gh_api_optional_log_to_file "$archive_dir/$run_id-job-$job_id.log" \
      "$archive_dir/$run_id-job-$job_id-logs-status.json" \
      "repos/${GITHUB_REPOSITORY}/actions/jobs/$job_id/logs"
    maybe_chunk_asset "$archive_dir/$run_id-job-$job_id.log" job_log null \
      "$archive_dir/$run_id-job-$job_id-logs-status.json"
    publish_verified_working_copy "$archive_dir/$run_id-job-$job_id.log"
  done

  while IFS=$'\t' read -r artifact_id artifact_name artifact_digest artifact_bytes; do
    [[ "$artifact_id" =~ ^[0-9]+$ && "$artifact_name" =~ ^[a-zA-Z0-9._-]+$ ]] || exit 2
    destination="$archive_dir/$run_id-artifact-$artifact_id-$artifact_name.zip"
    python3 - "$archive_dir" "$run_id" "$artifact_id" "$artifact_bytes" "$max_asset_bytes" "$chunk_bytes" <<'PY'
import datetime
import json
from pathlib import Path
import shutil
import sys
root, run_id, artifact_id = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
size, maximum, chunk_bytes = map(int, sys.argv[4:])
if size < 0:
    raise SystemExit('Negative API artifact size')
free = shutil.disk_usage(root).free
reserve = 64 * 1024 * 1024  # Filesystem rounding and small provenance/log files.
working_copies = 2 if size >= maximum else 1
required = working_copies * size + reserve
enough = free >= required
(root / f'{run_id}-artifact-{artifact_id}-disk-before.json').write_text(json.dumps({
    'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'run_id': run_id, 'artifact_id': artifact_id, 'api_size_bytes': size,
    'available_bytes_before_download': free, 'max_asset_bytes': maximum,
    'chunk_bytes': chunk_bytes, 'simultaneous_working_copies': working_copies,
    'filesystem_metadata_reserve_bytes': reserve, 'required_bytes': required,
    'action': 'download' if enough else 'stop_before_download',
    'scope': 'Archival headroom at this instant; later free space can change.',
}, indent=2) + '\n')
if not enough:
    raise SystemExit('Insufficient archival disk headroom before artifact download')
PY
    gh_api_to_file "$destination" "repos/${GITHUB_REPOSITORY}/actions/artifacts/$artifact_id/zip"
    if [[ "$artifact_digest" != null && -n "$artifact_digest" ]]; then
      [[ "$artifact_digest" =~ ^sha256:[a-fA-F0-9]{64}$ ]] || {
        echo "Invalid artifact digest for $artifact_id" >&2; exit 2;
      }
      actual="$(sha256sum "$destination")"
      expected="${artifact_digest#sha256:}"
      [[ "${actual%% *}" == "${expected,,}" ]] || {
        echo "Artifact digest mismatch for $artifact_id" >&2; exit 2;
      }
    fi
    maybe_chunk_asset "$destination" artifact "$artifact_digest"
    publish_verified_working_copy "$destination"
  done < <(jq -r '.artifacts[] | [.id, .name, (.digest // "null"), .size_in_bytes] | @tsv' \
    "$archive_dir/$run_id-artifact-index.json")
done

(
  cd "$archive_dir"
  : > SHA256SUMS.txt
  if [[ -f published-SHA256SUMS.txt ]]; then
    cat published-SHA256SUMS.txt >> SHA256SUMS.txt
  fi
  shopt -s nullglob
  for file in *.zip *.log *.part[0-9][0-9][0-9][0-9] *.chunks.json; do
    sha256sum "$file" >> SHA256SUMS.txt
  done
  provenance=(./*-artifact-index.json ./*-run.json ./*-jobs-pages.json
              ./*-check-run.json ./*-annotations.json ./*-logs-status.json
              ./*.chunks.json ./*-disk-before.json
              ./published-* ./release-*.json
              SHA256SUMS.txt)
  tar -czf provenance.tar.gz "${provenance[@]}"
)
