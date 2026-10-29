#!/usr/bin/env bash
set -euo pipefail

OUT="${1:?usage: setup-toolchain-v4.sh OUT_DIR}"
mkdir -p "$OUT/checkouts" "$OUT/bin" "$OUT/go" "$OUT/logs"
OUT="$(realpath "$OUT")"

cat >"$OUT/pins.tsv" <<'EOF'
procrustes	https://github.com/MB3R-Lab/Procrustes.git	39f76000f8a39c971155e08ebffde829b525911b	./cmd/procrustes
bering	https://github.com/MB3R-Lab/Bering.git	6f806428509a640a6419058c2ad845ed44db7512	./cmd/bering
sheaft	https://github.com/MB3R-Lab/Sheaft.git	686a602f4e7b71f3612f1810885e29dd66c8733a	./cmd/sheaft
EOF

printf 'name\tcommit\ttree\tgo_version\tgo_binary\tbinary\tbinary_sha256\tbinary_bytes\tclone_seconds\tbuild_seconds\n' >"$OUT/builds.tsv"
while IFS=$'\t' read -r name repository commit package; do
  checkout="$OUT/checkouts/$name"
  clone_start="$(date +%s%N)"
  git clone --filter=blob:none --no-checkout "$repository" "$checkout" >"$OUT/logs/$name-clone.log" 2>&1
  git -C "$checkout" fetch --depth=1 origin "$commit" >>"$OUT/logs/$name-clone.log" 2>&1
  git -C "$checkout" checkout --detach "$commit" >>"$OUT/logs/$name-clone.log" 2>&1
  actual="$(git -C "$checkout" rev-parse HEAD)"
  [[ "$actual" == "$commit" ]] || { echo "$name checkout mismatch: $actual != $commit" >&2; exit 1; }
  tree="$(git -C "$checkout" rev-parse 'HEAD^{tree}')"
  clone_end="$(date +%s%N)"

  go_version="$(awk '$1 == "go" {print $2; exit}' "$checkout/go.mod")"
  [[ "$go_version" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]] || { echo "invalid Go version in $name: $go_version" >&2; exit 1; }
  if [[ "$go_version" =~ ^[0-9]+\.[0-9]+$ ]]; then go_version="$go_version.0"; fi
  goroot="$OUT/go/$go_version"
  if [[ ! -x "$goroot/bin/go" ]]; then
    archive="$OUT/go/go${go_version}.linux-amd64.tar.gz"
    metadata="$OUT/go/go${go_version}.json"
    python - "$go_version" "$metadata" <<'PY'
import json, sys, urllib.request
version, target = sys.argv[1:]
with urllib.request.urlopen('https://go.dev/dl/?mode=json&include=all') as response:
    releases = json.load(response)
for release in releases:
    if release['version'] != 'go' + version:
        continue
    for item in release['files']:
        if item['filename'] == f'go{version}.linux-amd64.tar.gz':
            json.dump(item, open(target, 'w'), indent=2)
            break
    else:
        continue
    break
else:
    raise SystemExit(f'official Go archive metadata not found for {version}')
PY
    url="$(python -c 'import json,sys; print("https://go.dev/dl/"+json.load(open(sys.argv[1]))["filename"])' "$metadata")"
    expected="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["sha256"])' "$metadata")"
    curl --fail --location --retry 3 --output "$archive" "$url"
    echo "$expected  $archive" | sha256sum --check --status
    temporary="$OUT/go/.go-$go_version.tmp"
    mkdir "$temporary"
    tar -xzf "$archive" -C "$temporary"
    mv "$temporary/go" "$goroot"
    rmdir "$temporary"
  fi

  build_start="$(date +%s%N)"
  (
    cd "$checkout"
    env GOTOOLCHAIN=local "$goroot/bin/go" version
    env GOTOOLCHAIN=local "$goroot/bin/go" build -trimpath -o "$OUT/bin/$name" "$package"
  ) >"$OUT/logs/$name-build.log" 2>&1
  build_end="$(date +%s%N)"
  binary_sha="$(sha256sum "$OUT/bin/$name" | cut -d' ' -f1)"
  binary_bytes="$(stat -c %s "$OUT/bin/$name")"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$name" "$commit" "$tree" "$go_version" "$goroot/bin/go" "$OUT/bin/$name" \
    "$binary_sha" "$binary_bytes" "$((clone_end-clone_start))" "$((build_end-build_start))" >>"$OUT/builds.tsv"
done <"$OUT/pins.tsv"

python - "$OUT" <<'PY'
import csv, hashlib, json, pathlib, sys, time
root = pathlib.Path(sys.argv[1])
rows = list(csv.DictReader((root/'builds.tsv').open(), delimiter='\t'))
for row in rows:
    row['binary_bytes'] = int(row['binary_bytes'])
    row['clone_seconds'] = int(row['clone_seconds']) / 1e9
    row['build_seconds'] = int(row['build_seconds']) / 1e9
manifest = {
    'schema_version': 'toolchain-build-v4',
    'generated_ns': time.time_ns(),
    'binaries': rows,
    'commands': {
        'clone': 'git clone --filter=blob:none --no-checkout REPOSITORY; git fetch --depth=1 origin COMMIT; git checkout --detach COMMIT',
        'build': 'env GOTOOLCHAIN=local PINNED_GOROOT/bin/go build -trimpath -o BINARY ./cmd/NAME',
    },
    'go_archives': [
        {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in sorted((root/'go').glob('go*.linux-amd64.tar.gz'))
    ],
}
(root/'toolchain-build.json').write_text(json.dumps(manifest, indent=2)+'\n')
PY

printf '%s\n' "$OUT/bin"
