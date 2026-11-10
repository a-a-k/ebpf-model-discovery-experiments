"""Lossless preservation and Release-only reading of the original study inputs.

Original artifact ZIP bytes are concatenated into bounded parts. Every artifact
retains its own byte/SHA identity and slices; ZIP/TAR contents are never rewritten.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import zipfile

import requests

from .publication_archive import GitHub, Release, file_digest, require
from .runtime import write_json

REPO = 'a-a-k/ebpf-model-discovery-experiments'
# Keep every published part below both the one-GiB archival boundary and the
# GitHub Release asset limit.  The strict inequality is intentional: a part
# must never be exactly the boundary after a future change in the writer.
PART_BYTES = 1024**3
MAX_RELEASE_ASSET_BYTES = 2 * 1024**3
MAX_RELEASE_ASSETS = 1000
SHARDS = 40
RESERVE = 2 * 1024**3
EXTRA_RUNS = (42267248120, 42267262342, 42520421400)
ORIGINAL_RUNS = (42267236483, 42347353371, 42347357851, 42347362261, 42347366203,
    42380945945, 42380948810, 42380952084, 42380954809, 42380957553, 42380960724,
    42380963132, 42380965603, 42380968511, 42380971028, 42380973772, 42380976315,
    42380978976, 42380981787, 42401597551, 42401601965, 42401605258, 42401608466,
    42401611728, 42457618421, 42457621770, 42457624998, 42457628549, 42457632259,
    42479096323, 42479102051, 42479107381, *EXTRA_RUNS)
REFERENCE = '1153f70032bc36bbc1936e666c8338e0935c24d2c8553b64836e711c9005bf36'


def identity(a):
    return {k: a[k] for k in ('id', 'name', 'size', 'digest', 'state', 'browser_download_url')}


def guard(folder, incoming=0):
    require(shutil.disk_usage(folder).free >= incoming + RESERVE, 'actual archive disk reserve')


class ArchiveGitHub(GitHub):
    """Respect the repository token budget, preserving every wait in the receipt."""
    def request(self, method, endpoint, **kwargs):
        started = time.monotonic()
        while True:
            try:
                return super().request(method, endpoint, **kwargs)
            except requests.HTTPError as error:
                response = error.response
                if response.status_code not in (403, 429):
                    raise
                primary = response.headers.get('x-ratelimit-remaining') == '0'
                secondary = 'secondary rate limit' in response.text.lower() or 'abuse detection' in response.text.lower()
                if not primary and not secondary and not response.headers.get('retry-after'):
                    raise
                require(time.monotonic() - started < 5 * 3600, 'archive API budget wait exceeded worker envelope')
                until = int(response.headers.get('x-ratelimit-reset', '0')) - time.time() + 2 if primary else 60
                delay = min(60, max(2, until, int(response.headers.get('retry-after', '0'))))
                self.calls.append({'rate_wait_seconds': delay, 'started_ns': time.time_ns(), 'endpoint': endpoint})
                print(json.dumps({'API_budget_wait_seconds': delay}), flush=True)
                time.sleep(delay)


def public_download(asset, path):
    """Public Release delivery is independent of Actions and REST artifact APIs."""
    path = Path(path)
    require(asset['state'] == 'uploaded' and asset['digest'].startswith('sha256:') and
            asset['browser_download_url'].startswith(f'https://github.com/{REPO}/releases/download/'),
            'qualified public Release asset required')
    guard(path.parent, asset['size'])
    for attempt in range(5):
        pending = path.with_name(path.name + '.partial')
        try:
            h, size = hashlib.sha256(), 0
            with requests.get(asset['browser_download_url'], stream=True, timeout=(30, 180)) as response:
                response.raise_for_status()
                with pending.open('xb') as stream:
                    for body in response.iter_content(4 * 1024**2):
                        size += len(body)
                        require(size <= asset['size'], 'Release body exceeds sealed size')
                        h.update(body)
                        stream.write(body)
            require(size == asset['size'] and h.hexdigest() == asset['digest'][7:], 'Release body bytes/SHA differ')
            require(not path.exists(), 'never replace an assembled archive input')
            pending.rename(path)
            return
        except (requests.RequestException, OSError):
            pending.unlink(missing_ok=True)
            if attempt == 4:
                raise
            time.sleep(min(30, 2 ** attempt))


class PartWriter:
    def __init__(self, release, root, shard, part_bytes=PART_BYTES):
        self.release, self.root, self.shard = release, Path(root), shard
        require(0 < part_bytes <= PART_BYTES and part_bytes < MAX_RELEASE_ASSET_BYTES,
                'archive part size must be at most one GiB and below the Release limit')
        self.limit, self.parts, self.records = part_bytes, [], []
        self.stream, self.path, self.offset = None, None, 0

    def flush(self):
        if self.stream is None:
            return
        self.stream.close()
        asset = self.release.publish(self.path)
        self.parts.append(identity(asset))
        self.path.unlink()  # Only verified disposable working bytes, never a source publication.
        self.stream = None

    def append(self, artifact, archive):
        require(Path(archive).stat().st_size == artifact['size_in_bytes'] and
                file_digest(archive) == artifact['digest'][7:], 'original artifact identity differs')
        record = {'original_artifact': artifact, 'slices': []}
        at = 0
        with Path(archive).open('rb') as source:
            while at < artifact['size_in_bytes']:
                if self.stream is None:
                    name = f'shard-{self.shard:02d}-part-{len(self.parts):04d}.bin'
                    self.path = self.root / name
                    self.stream, self.offset = self.path.open('xb'), 0
                count = min(self.limit - self.offset, artifact['size_in_bytes'] - at)
                record['slices'].append({'part': len(self.parts), 'offset': self.offset,
                                         'length': count, 'artifact_offset': at})
                left = count
                while left:
                    body = source.read(min(left, 4 * 1024**2))
                    require(body, 'original ZIP truncated while splitting')
                    guard(self.root, len(body))
                    self.stream.write(body)
                    left -= len(body)
                self.offset += count
                at += count
                if self.offset == self.limit:
                    self.flush()
        self.records.append(record)


class ArchiveReader:
    """Bounded chunk cache, fresh ZIP reconstruction, no Actions client or fallback."""
    def __init__(self, parts, root, download=public_download):
        self.parts, self.root, self.download = parts, Path(root), download
        self.root.mkdir(parents=True, exist_ok=True)
        self.cache = OrderedDict()

    def part(self, index):
        require(0 <= index < len(self.parts), 'missing archive part')
        if index in self.cache:
            self.cache.move_to_end(index)
            return self.cache[index]
        while len(self.cache) >= 2:
            _, path = self.cache.popitem(last=False)
            path.unlink()
        path = self.root / f'part-{index:04d}.bin'
        self.download(self.parts[index], path)
        expected = self.parts[index]
        require(path.stat().st_size == expected['size'], 'archive part is not complete')
        if expected.get('digest', '').startswith('sha256:'):
            require(file_digest(path) == expected['digest'][7:], 'archive part SHA differs')
        self.cache[index] = path
        return path

    def restore(self, record, destination):
        artifact = record['original_artifact']
        if record.get('direct_asset'):
            self.download(record['direct_asset'], Path(destination))
            require(Path(destination).stat().st_size == artifact['size_in_bytes'] and
                    file_digest(destination) == artifact['digest'][7:], 'reused original ZIP identity differs')
            return
        guard(self.root, artifact['size_in_bytes'])
        h, at = hashlib.sha256(), 0
        with Path(destination).open('xb') as target:
            for span in record['slices']:
                require(span['artifact_offset'] == at and span['length'] > 0 and span['offset'] >= 0,
                        'artifact slices overlap, reorder or leave a gap')
                part = self.part(span['part'])
                require(span['offset'] + span['length'] <= part.stat().st_size, 'slice exceeds complete part')
                with part.open('rb') as source:
                    source.seek(span['offset'])
                    left = span['length']
                    while left:
                        body = source.read(min(left, 4 * 1024**2))
                        require(body, 'archive part truncated')
                        target.write(body)
                        h.update(body)
                        at += len(body)
                        left -= len(body)
        require(at == artifact['size_in_bytes'] and h.hexdigest() == artifact['digest'][7:],
                'reconstructed original ZIP bytes/SHA differ')


class ArchivedInputs:
    """Existing package import interface backed only by the sealed Release index."""
    def __init__(self, index, root):
        require(index['status'] == 'complete', 'unsealed input archive')
        self.index, self.root = index, Path(root)
        self.records = {a['original_artifact']['id']: a for a in index['artifacts']}
        self.shards = {n: value for n, value in enumerate(index['shards'])}
        self.calls = []

    def json(self, endpoint):
        match = re.fullmatch(r'actions/artifacts/([0-9]+)', endpoint)
        require(match and int(match[1]) in self.records, 'live or unarchived Actions metadata forbidden')
        self.calls.append({'archived_official_snapshot': endpoint})
        return self.records[int(match[1])]['original_artifact']

    def download(self, endpoint, path, size, sha):
        match = re.fullmatch(r'actions/artifacts/([0-9]+)/zip', endpoint)
        require(match and int(match[1]) in self.records, 'live or unarchived Actions download forbidden')
        record = self.records[int(match[1])]
        original = record['original_artifact']
        require((size, sha) == (original['size_in_bytes'], original['digest'][7:]), 'requested original identity differs')
        reader = ArchiveReader(self.index['shards'][record['shard']]['parts'], self.root / str(original['id']))
        reader.restore(record, path)
        for cached in reader.cache.values():
            cached.unlink()
        self.calls.append({'Release_only_original_artifact': original['id'], 'bytes': size, 'sha256': sha})


def safe_name(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in name, 'unsafe archive member name')


def hash_stream(source):
    h, size = hashlib.sha256(), 0
    while body := source.read(4 * 1024**2):
        h.update(body)
        size += len(body)
    return size, h.hexdigest()


def verify_tar(source, inventory):
    seen, embedded = set(), {}
    with tarfile.open(fileobj=source, mode='r|gz') as tar:
        for member in tar:
            safe_name(member.name)
            require(member.name not in seen and (member.isfile() or member.isdir()), 'unsafe/duplicate TAR member')
            seen.add(member.name)
            if member.isdir():
                continue
            expected = inventory['files'][member.name]
            with tar.extractfile(member) as stream:
                if (PurePosixPath(member.name).name in KEY_JSON or member.name.endswith('/golden/manifest.json')) and member.size < 32 * 1024**2:
                    body = stream.read()
                    actual = (len(body), hashlib.sha256(body).hexdigest())
                    embedded[member.name] = json.loads(body)
                else:
                    actual = hash_stream(stream)
            require(actual == (expected['bytes'], expected['sha256']) and
                    stat.S_IMODE(member.mode) == expected['mode'], 'nested member bytes/SHA/mode differ')
    require(seen == set(inventory['files']) | set(inventory.get('directories', [])), 'nested member census differs')
    for key, value in embedded.items():
        if key.endswith('closed-input.json'):
            for p, sha in value['files'].items():
                if p in inventory['files']:
                    require(inventory['files'][p]['sha256'] == sha, 'closed capture hash closure differs')
        if key.endswith('forecast-saved.json'):
            for p, sha in value['sha256_by_path'].items():
                if p in inventory['files']:
                    require(inventory['files'][p]['sha256'] == sha, 'portable frozen forecast hash differs')
    return embedded


KEY_JSON = {'closed-input.json', 'forecast-saved.json', 'status.json', 'processing-manifest.json',
            'v6-training-publication-restored.json', 'isolated-shared-import.json', 'block-plan.json',
            'shared-seal.json', 'blueprint.json'}


def verify_zip(path):
    """Check every ZIP CRC and every sealed nested package; do not extract large trees."""
    evidence, manifests = [], []
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        require(len(infos) == len({i.filename for i in infos}), 'duplicate ZIP member')
        for info in infos:
            safe_name(info.filename)
            require(not info.flag_bits & 1 and stat.S_IFMT(info.external_attr >> 16) in
                    (0, stat.S_IFREG, stat.S_IFDIR), 'encrypted or unsafe study ZIP member')
        names = {i.filename for i in infos if not i.is_dir()}
        outer = {}
        for info in infos:
            if info.is_dir():
                continue
            with archive.open(info) as source:
                outer[info.filename] = hash_stream(source)
            require(outer[info.filename][0] == info.file_size, 'incomplete ZIP member')
        for name in sorted(names):
            if not name.endswith('.tar.gz') or name + '.json' not in names:
                continue
            inventory = json.loads(archive.read(name + '.json'))
            if not {'bytes', 'sha256', 'files'} <= set(inventory):
                continue
            require(outer[name] == (inventory['bytes'], inventory['sha256']), 'nested package identity differs')
            with archive.open(name) as source:
                embedded = verify_tar(source, inventory)
            if PurePosixPath(name).name == 'capture.tar.gz' and (embedded.get('status.json') or {}).get('status') == 'capture_complete':
                require('closed-input.json' in embedded and all(inventory['files'].get(p, {}).get('sha256') == sha
                        for p, sha in embedded['closed-input.json']['files'].items()),
                        'complete capture lacks its sealed input bytes')
            manifests.append({'name': name, 'inventory_sha256': outer[name + '.json'][1],
                              'files': len(inventory['files']), 'all_bytes_SHA_modes_verified': True})
            evidence.extend({'path': key, 'sha256': inventory['files'][key]['sha256'], 'value': value,
                             'complete_processing_verified': bool(value.get('complete_processing_sha256_by_path')) and
                              all(inventory['files'].get(p, {}).get('sha256') == sha for p, sha in
                                  value.get('complete_processing_sha256_by_path', {}).items()),
                             'closed_input_complete_here': key.endswith('closed-input.json') and
                              all(inventory['files'].get(p, {}).get('sha256') == sha for p, sha in value.get('files', {}).items()),
                             'portable_forecast_complete_here': key.endswith('forecast-saved.json') and
                              all(inventory['files'].get(p, {}).get('sha256') == sha for p, sha in value.get('sha256_by_path', {}).items())}
                            for key, value in embedded.items()
                            if PurePosixPath(key).name != 'manifest.json' or key.endswith('/golden/manifest.json'))
        for name in sorted(n for n in names if n.endswith('processing-manifest.json')):
            manifest = json.loads(archive.read(name))
            prefix = name[:-len('processing-manifest.json')] + 'files/'
            require({n[len(prefix):] for n in names if n.startswith(prefix)} == set(manifest['files']),
                    'complete processing file census differs')
            for p, value in manifest['files'].items():
                require(outer[prefix + p] == (value['bytes'], value['sha256']), 'full processing bytes/SHA differ')
                require(type(value['mode']) is int and 0 <= value['mode'] <= 0o777 and
                        type(value['mtime_ns']) is int, 'processing restoration metadata invalid')
            frozen_name = prefix + 'forecast-saved.json'
            frozen = json.loads(archive.read(frozen_name)) if frozen_name in names else None
            if frozen:
                for p, sha in frozen['complete_processing_sha256_by_path'].items():
                    require(manifest['files'][p]['sha256'] == sha, 'complete frozen processing closure differs')
                evidence.append({'path': frozen_name, 'sha256': outer[frozen_name][1], 'value': frozen,
                                 'complete_processing_verified': manifest['scope'] == 'COMPLETE_FROZEN'})
            manifests.append({'name': name, 'scope': manifest['scope'], 'files': len(manifest['files']),
                              'all_bytes_SHA_verified': True,
                              'restore_modes_and_mtimes_from_original_manifest': True})
        for name in (n for n in names if n.endswith('freeze.json')):
            frozen = json.loads(archive.read(name))
            if 'files' in frozen and isinstance(frozen['files'], dict):
                prefix = name[:-len('freeze.json')]
                for p, item in frozen['files'].items():
                    require(outer[prefix + p] == (item['bytes'], item['sha256']), 'corrected forecast freeze differs')
        # Metadata publications contain the original case/producer/import closure.
        for name in sorted(names):
            if PurePosixPath(name).name in KEY_JSON and not name.endswith('processing-manifest.json'):
                if archive.getinfo(name).file_size < 32 * 1024**2:
                    evidence.append({'path': name, 'sha256': outer[name][1], 'value': json.loads(archive.read(name))})
    return {'ZIP_members': len(infos), 'all_ZIP_CRCs_verified': True,
            'sealed_packages': manifests, 'closure_records': evidence}


def read(path):
    return json.loads(Path(path).read_bytes())


def output(**values):
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf8') as stream:
        for key, value in values.items():
            stream.write(f'{key}={value}\n')


def save_source_bundle(root, commits):
    for commit in sorted(commits):
        if subprocess.run(['git', 'cat-file', '-e', commit + '^{commit}'], capture_output=True).returncode:
            subprocess.run(['git', 'fetch', '--no-tags', 'origin', commit], check=True)
        subprocess.run(['git', 'update-ref', 'refs/archive/source-' + commit, commit], check=True)
    path = root / 'study-source.bundle'
    subprocess.run(['git', 'bundle', 'create', str(path), '--all'], check=True)
    subprocess.run(['git', 'bundle', 'verify', str(path)], check=True)
    return path


def prepare(github, root):
    require(file_digest('results/literal-results.json') == REFERENCE, 'original canonical results changed')
    tag = 'full-input-archive-' + os.environ['GITHUB_RUN_ID']
    infos = {}
    for group in (0, 1):
        group_tag = f'{tag}-group{group}'
        matches = [r for r in github.pages('releases') if r['tag_name'] == group_tag]
        require(len(matches) <= 1, 'ambiguous owned input archive')
        infos[group] = matches[0] if matches else github.request('POST', 'releases', json={
        'tag_name': group_tag, 'target_commitish': os.environ['GITHUB_SHA'], 'draft': False, 'prerelease': True,
        'name': f'Study inputs: unsealed archive group {group}',
        'body': 'Full-input-archive-owner: ' + os.environ['GITHUB_RUN_ID'] +
                '\nIncomplete until the linked full-input-index.json and closure receipts are published.'}).json()
        require(infos[group]['target_commitish'] == os.environ['GITHUB_SHA'], 'foreign input archive source')
    release_ids = {str(shard): infos[0 if shard < 20 else 1]['id'] for shard in range(SHARDS + 1)}
    release = Release(github, infos[0]['id'])
    if 'archive-plan.json' in release.assets:
        a = release.assets['archive-plan.json']
        output(release_ids=json.dumps(release_ids, separators=(',', ':')),
               plan_id=a['id'], plan_bytes=a['size'], plan_sha256=a['digest'][7:])
        return
    workflows, artifacts, commits = [], {}, {os.environ['GITHUB_SHA']}
    for run_id in sorted(set(ORIGINAL_RUNS)):
        run = github.json(f'actions/runs/{run_id}')
        jobs = github.pages(f'actions/runs/{run_id}/jobs?filter=all', 'jobs')
        rows = github.pages(f'actions/runs/{run_id}/artifacts', 'artifacts')
        workflows.append({'run': run, 'jobs': jobs})
        commits.add(run['head_sha'])
        for artifact in rows:
            require(not artifact['expired'] and artifact['digest'].startswith('sha256:') and
                    artifact['size_in_bytes'] < 6 * 1024**3, 'unavailable/oversized original input')
            require(artifact['workflow_run']['id'] == run_id, 'artifact producer run differs')
            artifacts[artifact['id']] = artifact
    # Existing byte-exact report ZIPs are reused and fully reread, not uploaded again.
    old = read('results/archive.json')['archive_index']
    path = root / 'metadata-archive-index.json'
    github.download(f"releases/assets/{old['asset_id']}", path, old['bytes'], old['sha256'])
    reused = {int(re.fullmatch(r'artifact-([0-9]+)\.zip', a['name'])[1]): identity(a)
              for a in read(path)['payload_assets']}
    reference = read('results/literal-results.json')
    canonical = []
    for cell in reference['cells']:
        canonical.append({'key': cell['key'], 'forecast': cell['original_forecast'],
            'validation_artifact_id': cell['original_publication']['artifact_API']['id'],
            'validation_closed_input_sha256': cell['literal_evaluation']['validation_closed_input_sha256'],
            'lineage': cell['verified_replay_lineage']})
    require(len(canonical) == 108 and all(c['validation_artifact_id'] in artifacts for c in canonical),
            'original 108 canonical validation inputs absent')
    # One representative of each actual format is read before the large fanout.
    selected = set()
    for label in ('shared', 'training', 'validation', 'model', 'processing'):
        choices = [a for a in artifacts.values() if label in a['name'] and a['size_in_bytes'] > 1024**2 and
                   (label == 'processing' or not any(s in a['name'] for s in ('metadata', 'summary', 'processing')))]
        require(choices, 'missing archive format representative: ' + label)
        selected.add(min(choices, key=lambda a: a['size_in_bytes'])['id'])
    assignments = {str(n): [] for n in range(SHARDS + 1)}
    load = {str(n): 0 for n in range(SHARDS)}
    for artifact in sorted(artifacts.values(), key=lambda a: (-a['size_in_bytes'], a['id'])):
        shard = str(SHARDS) if artifact['id'] in selected else min(load, key=lambda k: (load[k], int(k)))
        assignments[shard].append(artifact['id'])
        if shard != str(SHARDS):
            load[shard] += artifact['size_in_bytes']
    part_count = sum(
        (artifacts[artifact_id]['size_in_bytes'] + PART_BYTES - 1) // PART_BYTES
        for artifact_ids in assignments.values()
        for artifact_id in artifact_ids if artifact_id not in reused
    )
    # Parts, one receipt per worker (including the format-check worker), the
    # plan, source bundle, registered study inputs, and final index.
    group_part_counts = {
        group: sum(
            (artifacts[artifact_id]['size_in_bytes'] + PART_BYTES - 1) // PART_BYTES
            for shard, artifact_ids in assignments.items()
            if (0 if int(shard) < 20 else 1) == group
            for artifact_id in artifact_ids if artifact_id not in reused
        )
        for group in (0, 1)
    }
    require(max(group_part_counts.values()) + 41 + 4 <= MAX_RELEASE_ASSETS,
            f'planned Release asset count exceeds {MAX_RELEASE_ASSETS}: {group_part_counts}')
    if 'study-source.bundle' in release.assets:
        source_asset = release.assets['study-source.bundle']
    else:
        bundle = save_source_bundle(root, commits)
        source_asset = release.publish(bundle)
    inputs = root / 'study-inputs.zip'
    paths = sorted({str(p).replace('\\', '/') for directory in ('docs', 'results')
                    for p in Path(directory).glob('*.json')})
    with zipfile.ZipFile(inputs, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for p in paths:
            item = zipfile.ZipInfo(p, date_time=(1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(item, Path(p).read_bytes())
    inputs_asset = release.publish(inputs)
    plan = {'schema': 'full-input-archive-v1', 'original_results_sha256': REFERENCE,
            'creation_run': os.environ['GITHUB_RUN_ID'], 'creation_source': os.environ['GITHUB_SHA'],
            'release_ids': release_ids, 'release_tag': tag, 'snapshot_ns': time.time_ns(),
            'artifacts': list(artifacts.values()), 'original_workflows': workflows, 'canonical': canonical,
            'assignments': assignments, 'part_bytes': PART_BYTES, 'reused_original_ZIPs': reused,
            'planned_part_count': part_count, 'planned_release_asset_count': {
                str(group): group_part_counts[group] + 41 + (4 if group == 0 else 1)
                for group in (0, 1)},
            'study_source_bundle': identity(source_asset), 'registered_study_inputs': identity(inputs_asset),
            'correction_publication': read('results/correction-publication.json'),
            'human_seconds': None, 'complete_comparable_cost_comparison': False}
    path = root / 'archive-plan.json'
    write_json(path, plan)
    asset = release.publish(path)
    Release(github, infos[1]['id']).publish(path)
    output(release_ids=json.dumps(release_ids, separators=(',', ':')),
           plan_id=asset['id'], plan_bytes=asset['size'], plan_sha256=asset['digest'][7:])


def load_plan(github, root, args):
    path = root / 'archive-plan.json'
    release = Release(github, args.release_id)
    asset = release.assets.get('archive-plan.json')
    require(asset is not None, 'archive plan missing from shard Release')
    github.download(f"releases/assets/{asset['id']}", path, asset['size'], asset['digest'][7:])
    plan = read(path)
    require(plan['schema'] == 'full-input-archive-v1' and args.release_id in plan['release_ids'].values() and
            plan['creation_run'] == os.environ['GITHUB_RUN_ID'] and plan['creation_source'] == os.environ['GITHUB_SHA'],
            'foreign archive plan/source/run')
    return plan


def verify_part_coverage(parts, records):
    spans = {i: [] for i in range(len(parts))}
    for record in records:
        if record.get('direct_asset'):
            continue
        at = 0
        for s in record['slices']:
            require(s['artifact_offset'] == at and s['length'] > 0 and s['part'] in spans,
                    'original ZIP coverage differs')
            at += s['length']
            spans[s['part']].append((s['offset'], s['offset'] + s['length']))
        require(at == record['original_artifact']['size_in_bytes'], 'original ZIP incomplete coverage')
    for index, ranges in spans.items():
        at = 0
        for start, end in sorted(ranges):
            require(start == at and end > start, 'part coverage overlaps or leaves a gap')
            at = end
        require(at == parts[index]['size'], 'unaccounted bytes in complete part')


def worker(github, root, plan, shard):
    release = Release(github, plan['release_ids'][str(shard)])
    started = time.time_ns()
    writer = PartWriter(release, root, shard, plan['part_bytes'])
    artifacts = {a['id']: a for a in plan['artifacts']}
    records = []
    for artifact_id in plan['assignments'][str(shard)]:
        artifact = artifacts[artifact_id]
        reused = plan['reused_original_ZIPs'].get(str(artifact_id))
        if reused:
            require((reused['size'], reused['digest']) == (artifact['size_in_bytes'], artifact['digest']),
                    'reused original metadata ZIP differs')
            records.append({'original_artifact': artifact, 'direct_asset': reused})
            continue
        path = root / f'original-{artifact_id}.zip'
        github.download(f'actions/artifacts/{artifact_id}/zip', path, artifact['size_in_bytes'], artifact['digest'][7:])
        writer.append(artifact, path)
        path.unlink()
    writer.flush()
    records += writer.records
    verify_part_coverage(writer.parts, records)
    # All original deliveries and writer parts have been released. This reader has
    # no Actions client; its cache is populated from public Release bodies only.
    reader = ArchiveReader(writer.parts, root / 'fresh-release-reader')
    for record in records:
        path = reader.root / f"artifact-{record['original_artifact']['id']}.zip"
        reader.restore(record, path)
        record['verification'] = verify_zip(path)
        path.unlink()
        print(json.dumps({'shard': shard, 'verified_original_artifact': record['original_artifact']['id']}), flush=True)
    for cached in reader.cache.values():
        cached.unlink()
    correction = verify_correction(root, plan, shard)
    receipt = {'shard': shard, 'plan_sha256': file_digest(root / 'archive-plan.json'),
               'parts': writer.parts, 'artifacts': records, 'started_ns': started, 'ended_ns': time.time_ns(),
               'fresh_readback_used_Actions_API': False, 'all_original_ZIP_bytes_and_nested_inputs_verified': True,
               'corrected_input_readback': correction,
               'API_requests': github.calls, 'human_seconds': None}
    path = root / f'shard-{shard:02d}-receipt.json'
    write_json(path, receipt)
    release.publish(path)


def verify_correction(root, plan, shard):
    """Reuse the existing corrected raw bodies; reread them without copying storage."""
    report = plan['correction_publication']
    def public(asset):
        return {**asset, 'browser_download_url':
                f"https://github.com/{REPO}/releases/download/compose-ack-correction-42769442057/{asset['name']}"}
    proofs = []
    for n, row in enumerate(report['raw_publications']):
        if n % SHARDS != shard:
            continue
        raw = row['raw']
        parts = [public(raw['asset'])] if 'asset' in raw else [public(p['asset']) for p in raw['parts']]
        artifact = {'id': row['receipt']['id'], 'size_in_bytes': raw['original_bytes'],
                    'digest': 'sha256:' + raw['original_sha256']}
        at, slices = 0, []
        for index, part in enumerate(parts):
            slices.append({'part': index, 'offset': 0, 'length': part['size'], 'artifact_offset': at})
            at += part['size']
        reader = ArchiveReader(parts, root / f'corrected-{n}')
        path = reader.root / 'original.tar.gz'
        reader.restore({'original_artifact': artifact, 'slices': slices}, path)
        manifest = reader.root / 'inventory.json'
        public_download(public(row['inventory_asset']), manifest)
        inventory = read(manifest)
        require((inventory['bytes'], inventory['sha256']) == (raw['original_bytes'], raw['original_sha256']),
                'corrected raw inventory differs')
        with path.open('rb') as source:
            records = verify_tar(source, inventory)
        require(records['status.json']['status'] == 'capture_complete' and
                [records['status.json'][k] for k in ('system', 'mode', 'seed', 'collector')] == row['key'] and
                all(inventory['files'].get(p, {}).get('sha256') == sha
                    for p, sha in records['closed-input.json']['files'].items()),
                'corrected case identity or complete capture closure differs')
        proofs.append({'key': row['key'], 'raw_sha256': raw['original_sha256'],
                       'all_members_bytes_SHA_modes_verified': True,
                       'closed_input_sha256': inventory['files']['closed-input.json']['sha256'],
                       'status': records['status.json']})
        path.unlink()
        # Verified reader-owned cache only, after complete raw readback.
        for cached in reader.cache.values():
            cached.unlink()
    assets = report['archived_metadata']
    for n, item in enumerate(assets):
        if n % SHARDS == shard:
            path = root / item['archived_asset']['name']
            public_download(public(item['archived_asset']), path)
            with zipfile.ZipFile(path) as archive:
                require(archive.namelist() == item['members'] and archive.testzip() is None,
                        'corrected archived metadata CRC differs')
            path.unlink()
    for n, asset in enumerate(report['forecast_origin']['freeze_assets']):
        if n == shard:
            path = root / asset['name']
            # Forecast manifest records omit the public URL; it is deterministic.
            asset = {**asset, 'browser_download_url':
                     f"https://github.com/{REPO}/releases/download/compose-ack-correction-42685277599/{asset['name']}"}
            public_download(asset, path)
            verify_zip(path)
            path.unlink()
    return {'raw_cases': proofs,
            'metadata_ZIPs': sum(n % SHARDS == shard for n in range(len(assets))),
            'corrected_forecast_ZIPs': int(shard < len(report['forecast_origin']['freeze_assets']))}


def finalize(github, root, plan):
    releases = {str(shard): Release(github, release_id)
                for shard, release_id in plan['release_ids'].items()}
    release = releases['0']
    rows, all_artifacts, closures, corrected = [], {}, [], []
    metadata_count = freeze_count = 0
    for shard in range(SHARDS + 1):
        asset = releases[str(shard)].assets[f'shard-{shard:02d}-receipt.json']
        path = root / asset['name']
        public_download(asset, path)
        receipt = read(path)
        require(receipt['plan_sha256'] == file_digest(root / 'archive-plan.json') and
                receipt['all_original_ZIP_bytes_and_nested_inputs_verified'] is True,
                'incomplete/foreign shard receipt')
        verify_part_coverage(receipt['parts'], receipt['artifacts'])
        rows.append({'receipt_asset': identity(asset), 'parts': receipt['parts']})
        corrected += receipt['corrected_input_readback']['raw_cases']
        metadata_count += receipt['corrected_input_readback']['metadata_ZIPs']
        freeze_count += receipt['corrected_input_readback']['corrected_forecast_ZIPs']
        for record in receipt['artifacts']:
            artifact_id = record['original_artifact']['id']
            require(artifact_id not in all_artifacts, 'duplicate archived original artifact')
            all_artifacts[artifact_id] = {k: v for k, v in record.items() if k != 'verification'}
            all_artifacts[artifact_id]['shard'] = shard
            closures.extend({'artifact_id': artifact_id, **entry} for entry in record['verification']['closure_records'])
    require(set(all_artifacts) == {a['id'] for a in plan['artifacts']}, 'not every registered original input was read')
    require(len(corrected) == 36 and len({tuple(c['key']) for c in corrected}) == 36 and
            metadata_count == 85 and freeze_count == 9, 'corrected input closure incomplete')
    for asset in (plan['study_source_bundle'], plan['registered_study_inputs']):
        path = root / asset['name']
        public_download(asset, path)
        if path.suffix == '.bundle':
            subprocess.run(['git', 'bundle', 'verify', str(path)], check=True)
        else:
            with zipfile.ZipFile(path) as archive:
                require(archive.testzip() is None, 'registered source ZIP CRC differs')
    refs = set()
    def references(value):
        if isinstance(value, dict):
            if 'id' in value and 'size_in_bytes' in value and 'digest' in value:
                refs.add(value['id'])
            for key, item in value.items():
                if key.endswith('artifact_id') and type(item) is int:
                    refs.add(item)
                references(item)
        elif isinstance(value, list):
            for item in value:
                references(item)
    for closure in closures:
        references(closure['value'])
    missing = refs - set(all_artifacts)
    write_json(root / 'unresolved-artifact-references.json', sorted(missing))
    require(not missing, 'recursive artifact closure incomplete; see unresolved-artifact-references.json')
    checks = []
    for case in plan['canonical']:
        capture = [c for c in closures if c['artifact_id'] == case['validation_artifact_id'] and
                   c['path'].endswith('closed-input.json') and c['sha256'] == case['validation_closed_input_sha256'] and
                   c.get('closed_input_complete_here') is True]
        forecast_sha = case['forecast']['forecast_manifest_sha256']
        forecasts = [c for c in closures if c['path'].endswith('forecast-saved.json') and c['sha256'] == forecast_sha]
        require(capture and forecasts, 'canonical original validation/forecast closure missing: ' + str(case['key']))
        frozen = forecasts[0]['value']
        captures = [c for c in closures if c['path'].endswith('closed-input.json') and
                    c['sha256'] == frozen['training_closed_input_sha256'] and c.get('closed_input_complete_here') is True]
        shared = [c for c in closures if c['path'].endswith('blueprint/blueprint.json') and
                  c['sha256'] == frozen['case']['blueprint_sha256'] and
                  'shared' in all_artifacts[c['artifact_id']]['original_artifact']['name']]
        require(captures and shared, 'canonical original capture/shared blueprint missing')
        full = [c for c in forecasts if c.get('complete_processing_verified') is True]
        require(full, 'canonical complete processing publication missing: ' + str(case['key']))
        models = [c for c in forecasts if 'model' in all_artifacts[c['artifact_id']]['original_artifact']['name'] and
                  'processing' not in all_artifacts[c['artifact_id']]['original_artifact']['name'] and
                  c.get('portable_forecast_complete_here') is True]
        require(models, 'canonical portable model package missing')
        checks.append({'key': case['key'], 'validation': case['validation_artifact_id'],
                       'forecast_sha256': forecast_sha, 'training': captures[0]['artifact_id'],
                       'shared': shared[0]['artifact_id'], 'model': models[0]['artifact_id'],
                       'processing': full[0]['artifact_id']})
    jobs = github.pages(f"actions/runs/{os.environ['GITHUB_RUN_ID']}/jobs?filter=all", 'jobs')
    intervals, unknown = {}, []
    from .compose_ack_publication import interval_seconds
    for job in jobs:
        seconds = interval_seconds(job)
        if seconds is None:
            unknown.append({'id': job['id'], 'status': job['status'], 'timestamps':
                            [job.get('started_at'), job.get('completed_at')]})
        else:
            key = (job['name'], job['head_sha'], job['started_at'], job['completed_at'])
            intervals.setdefault(key, {'worker_seconds': seconds, 'aliases': []})['aliases'].append(job['id'])
    index = {'schema': plan['schema'], 'status': 'complete', 'plan': {
        'asset_id': int(os.environ['FULL_ARCHIVE_PLAN_ID']), 'bytes': (root / 'archive-plan.json').stat().st_size,
        'sha256': file_digest(root / 'archive-plan.json')}, 'release_ids': plan['release_ids'],
        'creation_source': plan['creation_source'], 'artifacts': list(all_artifacts.values()), 'shards': rows,
        'canonical_108_closure_checks': checks, 'study_source_bundle': plan['study_source_bundle'],
        'corrected_36_raw_input_checks': corrected, 'corrected_metadata_ZIPs_verified': metadata_count,
        'corrected_forecast_ZIPs_verified': freeze_count, 'archive_workflow_jobs_at_finite_cut': jobs,
        'unique_closed_worker_intervals': list(intervals.values()), 'unknown_worker_intervals': unknown,
        'known_worker_seconds_at_finite_cut': sum(v['worker_seconds'] for v in intervals.values()),
        'registered_study_inputs': plan['registered_study_inputs'], 'original_results_sha256': REFERENCE,
        'original_workflows': plan['original_workflows'], 'correction_publication': plan['correction_publication'],
        'created_ns': time.time_ns(), 'all_original_inputs_verified_by_fresh_Release_only_readback': True,
        'remaining_dependencies': ['GitHub repository/Release availability',
                                   'compatible Linux/Go/Python execution environment for future model builds'],
        'this_finalizer_and_later_delivery_costs_outside_worker_cut_are_not_zero': True, 'human_seconds': None}
    path = root / 'full-input-index.json'
    write_json(path, index)
    asset = release.publish(path)
    github.request('PATCH', f"releases/{release.id}", json={'prerelease': False,
        'name': 'Original study inputs and verified archive-backed closure',
        'body': 'Complete original 108-case raw/shared/model/full-processing input archive. '
                'Every ZIP and sealed member was reread from Release storage; see full-input-index.json.'})
    print(json.dumps({'index_asset': identity(asset), 'artifacts': len(all_artifacts), 'canonical_cases': len(checks)}), flush=True)
    output(index_id=asset['id'], index_bytes=asset['size'], index_sha256=asset['digest'][7:])


def import_check(github, root, args):
    path = root / 'full-input-index.json'
    github.download(f'releases/assets/{args.index_id}', path, args.index_bytes, args.index_sha256)
    index = read(path)
    backend = ArchivedInputs(index, root / 'cache')
    from .compose_ack_repair import package_import
    checks = index['canonical_108_closure_checks']
    proof = []
    for kind in ('model', 'shared'):
        selected = min(checks, key=lambda c: backend.records[c[kind]]['original_artifact']['size_in_bytes'])
        expected = backend.records[selected[kind]]['original_artifact']
        package = package_import(backend, expected, root / (kind + '-delivery'), kind, root / kind)
        proof.append({'kind': kind, 'artifact_id': expected['id'], 'complete_restored_files': len(package['files']),
                      'original_bytes_SHA_modes_verified': True})
    write_json(root / 'archive-import-proof.json', {'source': os.environ['GITHUB_SHA'],
               'run_id': os.environ['GITHUB_RUN_ID'], 'index_sha256': args.index_sha256, 'imports': proof,
               'live_Actions_API_requests': 0, 'historical_API_fields_are_archived_snapshots': True,
               'new_VM_or_model_execution': False, 'backend_reads': backend.calls})
    print(json.dumps({'existing_package_imports_verified': proof, 'Actions_API_requests': 0}), flush=True)


def model_sample(github, root, args):
    """Rebuild a predeclared technical sample from archived training inputs."""
    from .compose_ack_repair import package_import

    index_path = root / 'full-input-index.json'
    github.download(f'releases/assets/{args.index_id}', index_path, args.index_bytes, args.index_sha256)
    index = read(index_path)
    backend = ArchivedInputs(index, root / 'model-sample-cache')
    selected_keys = [
        ['petclinic', 'full', 9, 'coroot'],
        ['otel_demo', 'absent', 10, 'deepflow'],
        ['deathstarbench', 'partial', 11, 'obi'],
    ]
    checks = {tuple(row['key']): row for row in index['canonical_108_closure_checks']}
    require(all(tuple(key) in checks for key in selected_keys), 'model sample case is not archived')
    results = []
    for number, key in enumerate(selected_keys, 1):
        row = checks[tuple(key)]
        training_root = root / f'model-sample-{number}' / 'training'
        expected_root = root / f'model-sample-{number}' / 'expected'
        training_root.parent.mkdir(parents=True, exist_ok=True)
        package_import(backend, backend.records[row['training']]['original_artifact'],
                       training_root.parent / 'training-delivery', 'training', training_root)
        package_import(backend, backend.records[row['model']]['original_artifact'],
                       expected_root.parent / 'expected-delivery', 'model', expected_root)
        expected = read(expected_root / 'forecast-saved.json')
        subprocess.run([sys.executable, '-m', 'ebpf_discovery.study_v6', 'model',
                        '--root', str(training_root)], check=True)
        actual = read(training_root / 'forecast-saved.json')
        comparable = ('case', 'training_closed_input_sha256', 'sha256_by_path',
                      'complete_processing_sha256_by_path', 'uses_actual_graph_simulator')
        require(all(actual.get(field) == expected.get(field) for field in comparable),
                f'model sample output differs for {key}')
        results.append({'key': key, 'training_artifact_id': row['training'],
                        'model_artifact_id': row['model'], 'compared_fields': list(comparable),
                        'runtime_fields': ['saved_ns', 'processing_execution',
                                           'model-worker-resources.json', 'model-swap-resources.json']})
    write_json(root / 'model-sample-proof.json', {
        'schema': 'full-input-model-sample-v1', 'selected_cases': results,
        'selection_frozen_before_execution': True, 'live_Actions_API_requests': 0,
        'historical_API_fields_are_archived_snapshots': True,
        'model_execution_source': os.environ['GITHUB_SHA'],
        'technical_rebuilds': len(results),
    })
    print(json.dumps({'technical_model_rebuilds': len(results), 'Actions_API_requests': 0}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'worker', 'finalize', 'import-check', 'model-sample'))
    parser.add_argument('--release-id', type=int)
    parser.add_argument('--release-ids')
    parser.add_argument('--plan-id', type=int)
    parser.add_argument('--plan-bytes', type=int)
    parser.add_argument('--plan-sha256')
    parser.add_argument('--shard', type=int)
    parser.add_argument('--index-id', type=int)
    parser.add_argument('--index-bytes', type=int)
    parser.add_argument('--index-sha256')
    args = parser.parse_args()
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == REPO,
            'large input preservation and reading is repository Actions only')
    root = Path('work/full-input-archive').resolve()
    root.mkdir(parents=True, exist_ok=True)
    github = ArchiveGitHub(replay=args.command == 'import-check')
    started, error = time.time_ns(), None
    try:
        if args.command == 'import-check':
            import_check(github, root, args)
        elif args.command == 'model-sample':
            model_sample(github, root, args)
        elif args.command == 'prepare':
            prepare(github, root)
        else:
            if args.command == 'finalize':
                args.release_id = int(json.loads(args.release_ids)['0'])
            plan = load_plan(github, root, args)
            if args.command == 'worker':
                worker(github, root, plan, args.shard)
            else:
                finalize(github, root, plan)
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        write_json(root / 'execution.json', {'command': args.command, 'shard': args.shard,
                   'source': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
                   'attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'started_ns': started, 'ended_ns': time.time_ns(),
                   'error': error, 'API_requests': github.calls, 'free_bytes': shutil.disk_usage(root).free,
                   'human_seconds': None, 'nested_seconds_not_added_to_worker_intervals': True})


if __name__ == '__main__':
    main()
