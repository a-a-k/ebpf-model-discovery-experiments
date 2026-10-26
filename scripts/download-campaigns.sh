#!/usr/bin/env bash
set -euo pipefail
source scripts/github-read.sh
mkdir -p work/inputs

# Archived replay survives Actions artifact expiry. Original ZIP hashes come
# from the release's provenance archive, not from regenerated result files.
for tag in ${ARCHIVE_TAGS:-}; do
  [[ "$tag" =~ ^data-[0-9]+$ ]] || exit 2
  directory="work/archives/$tag"
  mkdir -p "$directory"
  gh release download "$tag" --repo "$GITHUB_REPOSITORY" --pattern provenance.tar.gz --dir "$directory"
  tar -xzf "$directory/provenance.tar.gz" -C "$directory"
done

for run_id in $RUN_IDS; do
  [[ "$run_id" =~ ^[0-9]+$ ]] || exit 2
  destination="work/inputs/$run_id"
  mkdir -p "$destination"
  if [[ -z "${ARCHIVE_TAGS:-}" ]]; then
    gh_api_to_file "$destination/artifact-index.json" "repos/${GITHUB_REPOSITORY}/actions/runs/$run_id/artifacts?per_page=100"
    if jq -e '.artifacts[] | select(.name | startswith("campaign-"))' "$destination/artifact-index.json" >/dev/null; then
      gh run download "$run_id" --repo "$GITHUB_REPOSITORY" --pattern 'campaign-*' -D "$destination"
    fi
    continue
  fi
  selected_tag=''
  for tag in $ARCHIVE_TAGS; do
    if [[ -f "work/archives/$tag/$run_id-artifact-index.json" ]]; then
      selected_tag="$tag"
      break
    fi
  done
  [[ -n "$selected_tag" ]] || { echo "No archived provenance for run $run_id" >&2; exit 2; }
  directory="work/archives/$selected_tag"
  cp "$directory/$run_id-artifact-index.json" "$destination/artifact-index.json"
  while IFS= read -r artifact_name; do
    [[ "$artifact_name" =~ ^campaign-[a-zA-Z0-9._-]+$ ]] || exit 2
    filename="$run_id-$artifact_name.zip"
    gh release download "$selected_tag" --repo "$GITHUB_REPOSITORY" --pattern "$filename" --dir "$directory"
    checksum=$(awk -v filename="$filename" '$2 == filename { print $1 }' "$directory/SHA256SUMS.txt")
    [[ "$checksum" =~ ^[0-9a-f]{64}$ ]] || exit 2
    printf '%s  %s\n' "$checksum" "$directory/$filename" | sha256sum -c -
    mkdir -p "$destination/$artifact_name"
    unzip -q "$directory/$filename" -d "$destination/$artifact_name"
  done < <(jq -r '.artifacts[] | select(.name | startswith("campaign-")) | .name' "$destination/artifact-index.json")
done
