#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/github-read.sh"

: "${GITHUB_REPOSITORY:?}"
: "${RUN_IDS:?}"
archive_dir="${ARCHIVE_DIR:-work/archive}"
mkdir -p "$archive_dir"

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
  if [[ -f "$workflow_logs" ]]; then python3 -m zipfile -t "$workflow_logs" >/dev/null; fi
  # Whole-run ZIP presence does not prove that every job's log is inside it.
  for job_id in "${job_ids[@]}"; do
    gh_api_optional_log_to_file "$archive_dir/$run_id-job-$job_id.log" \
      "$archive_dir/$run_id-job-$job_id-logs-status.json" \
      "repos/${GITHUB_REPOSITORY}/actions/jobs/$job_id/logs"
  done

  while IFS=$'\t' read -r artifact_id artifact_name artifact_digest; do
    [[ "$artifact_id" =~ ^[0-9]+$ && "$artifact_name" =~ ^[a-zA-Z0-9._-]+$ ]] || exit 2
    destination="$archive_dir/$run_id-artifact-$artifact_id-$artifact_name.zip"
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
  done < <(jq -r '.artifacts[] | [.id, .name, (.digest // "null")] | @tsv' \
    "$archive_dir/$run_id-artifact-index.json")
done

(
  cd "$archive_dir"
  : > SHA256SUMS.txt
  shopt -s nullglob
  for file in *.zip *.log; do sha256sum "$file" >> SHA256SUMS.txt; done
  provenance=(./*-artifact-index.json ./*-run.json ./*-jobs-pages.json
              ./*-check-run.json ./*-annotations.json ./*-logs-status.json
              SHA256SUMS.txt)
  tar -czf provenance.tar.gz "${provenance[@]}"
)
