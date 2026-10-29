"""One fixed Actions-only replay checks envelope batching, not model accuracy.

The reference is the already retained per-trace Bering result. Every old archive
member is verified, but only the fixed branch is copied; native exports are
fingerprinted in their original order without creating another mountain of files.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import time

import ijson

from .bering_v4 import child_go_environment
from .checkpoint_diagnostic_v4 import (DSB_SHUTDOWN_PROFILE, PROFILES, runtime_binaries,
    validate_checkpoint_manifest, validate_training_prefix)
from .replay_qualification_v4 import digest, file_manifest, relocate_index
from .runtime import Context, write_json
from .store_v3 import ObservationStore
from .toolchain_v4 import Toolchain


REFERENCE = {
    'run_id': 40799411526, 'artifact_id': 12871565920,
    'artifact_name': 'diagnostic-v4-dsb-checkpoint-batch-40799411526',
    'artifact_digest': 'sha256:e27c347dd4282db46cf8222bc79e33660c31c76ebe789462d73f12045fcee0c3',
    'run_sha': 'fa2c454eaa5cca1a20a534ceb6e72ab64f8f8af3',
}
BRANCH = 'output/toolchain/combined/network_scope/compose_post'
NATIVE = 'output/toolchain/inputs/native/network_scope'
EBPF = 'output/toolchain/inputs/ebpf/network_scope'
EVIDENCE_KEY = 'bering.observation_evidence.v1'
CAPTURE = re.compile(r'.*/obi-capture/[0-9]{20}-([0-9]{8})-([0-9a-f]{64})(\.pb|\.json)(\.gz)?$')
LISTENER = re.compile(r'bering://serve\?listen=127\.0\.0\.1%3A[0-9]+$')
NORMALIZATION = {
    'model': ['metadata.discovered_at', 'metadata.source_ref'],
    'snapshot': ['metadata.emitted_at', 'metadata.source_ref', 'window_start', 'window_end',
                 'snapshot_id', 'topology_version (hash of complete normalized model instead)'],
    'quality': ['generated_at', 'artifact.path', 'artifact.window_start', 'artifact.window_end',
                'artifact.snapshot_id', 'artifact.topology_version (same normalized model hash)'],
    'source_references': 'Only actual localhost listener URI, OBI capture path bound to unchanged export ordinal/SHA, and fixed overlay path bound to its exact SHA',
    'ordering': 'Only source/provenance arrays are sorted after reference normalization; duplicates retained',
    'preserved': 'All entity IDs, structure, observed timestamps, typed attributes, support, instances, DB aliases, unknowns, counts and warnings',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


class Resources:
    def __init__(self):
        self.hash = hashlib.sha256()
        self.groups = self.observations = self.exports = 0

    def add(self, stream):
        self.exports += 1
        for group in ijson.items(stream, 'resourceSpans.item', use_float=True):
            self.hash.update(canonical(group) + b'\n')
            self.groups += 1
            self.observations += sum(len(scope.get('spans', [])) for scope in group.get('scopeSpans', []))

    def result(self):
        return dict(ordered_resource_spans_sha256=self.hash.hexdigest(),
                    resource_groups=self.groups, observations=self.observations, exports=self.exports)


def inspect_reference(package_dir, out, identity):
    """Stream-verify all old files; keep fixed model/overlay and ordered input digest."""
    if any(identity.get(key) != value for key, value in REFERENCE.items()):
        raise ValueError('fixed reference Actions identity mismatch')
    package_dir, out = Path(package_dir), Path(out)
    if out.exists():
        raise ValueError('reference view must be fresh')
    out.mkdir(parents=True)
    proof = read(package_dir/'packaging.json')
    archive_path, manifest_path = package_dir/'diagnostic-output.tar.gz', package_dir/'output-manifest.jsonl'
    if (proof.get('status') != 'complete' or proof.get('schema_version') != 'v4-lossless-diagnostic-package'
            or proof.get('exact_paths_bytes_and_current_source_verified') is not True
            or proof.get('gzip_crc_verified') is not True or proof.get('source_deleted_or_trimmed') is not False
            or digest(archive_path) != proof.get('archive_sha256')
            or archive_path.stat().st_size != proof.get('archive_bytes')
            or digest(manifest_path) != proof.get('manifest_sha256')):
        raise ValueError('reference package proof/hash mismatch')
    selected = {BRANCH+'/'+name for name in ('model.json', 'model.snapshot.json', 'model.signal-quality.json',
        'overlay.json', 'model-runtime/replay-command.json', 'model-runtime/bering-resources.json')}
    selected |= {NATIVE+'/observations.json', EBPF+'/observations.json',
                 'output/toolchain-provenance.json', 'output/status.json'}
    counts = dict(files=0, directories=0, uncompressed_file_bytes=0)
    native = Resources()
    retained, seen = {}, set()
    native_exports = []
    ordinal = 0
    with manifest_path.open(encoding='utf-8') as rows, gzip.open(archive_path, 'rb') as wire:
        with tarfile.open(fileobj=wire, mode='r|') as archive:
            for member in archive:
                row = json.loads(rows.readline())
                name = row['path']
                if (name != member.name or name in seen or '\\' in name
                        or PurePosixPath(name).is_absolute() or any(p in ('', '.', '..') for p in name.split('/'))
                        or row['mode'] != member.mode or row['bytes'] != member.size):
                    raise ValueError('reference archive manifest mismatch')
                seen.add(name)
                if row['type'] == 'directory' and member.isdir():
                    counts['directories'] += 1
                elif row['type'] == 'file' and member.isfile():
                    counts['files'] += 1
                    counts['uncompressed_file_bytes'] += member.size
                    source = archive.extractfile(member)
                    selected_file = name in selected
                    native_file = name.startswith(NATIVE+'/exports/')
                    # Historical single-trace envelopes are small; all other
                    # members stream without materializing the source index.
                    if native_file or selected_file:
                        payload = source.read()
                        actual = hashlib.sha256(payload).hexdigest()
                    else:
                        actual = hashlib.file_digest(source, 'sha256').hexdigest()
                    if actual != row.get('sha256'):
                        raise ValueError('reference member hash mismatch: '+name)
                    if native_file:
                        ordinal += 1
                        if name != NATIVE+f'/exports/native-{ordinal:06d}.json':
                            raise ValueError('reference native export order mismatch')
                        native_exports.append((Path(name).name, actual))
                        import io
                        native.add(io.BytesIO(payload))
                    if selected_file:
                        target = out/name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(payload)
                        retained[name] = dict(bytes=len(payload), sha256=actual)
                else:
                    raise ValueError('unsupported reference archive member')
                archive.members.clear()
            if rows.readline():
                raise ValueError('reference manifest has omitted member')
        while wire.read(1024*1024):
            pass
    if set(retained) != selected or any(proof.get(key) != value for key, value in counts.items()):
        raise ValueError('reference archive census/selected branch mismatch')
    native_manifest = read(out/NATIVE/'observations.json')
    if (native.observations != native_manifest['observations']
            or native_exports != [(Path(item['path']).name, item['sha256'])
                                   for item in native_manifest['exports']]):
        raise ValueError('reference native fingerprint accounting mismatch')
    old_status = read(out/'output/status.json')
    old_tools = read(out/'output/toolchain-provenance.json')
    command = read(out/BRANCH/'model-runtime/replay-command.json')
    if (old_status.get('status') != 'diagnostic_complete'
            or old_status.get('immutable_checkpoint_unchanged') is not True
            or old_tools['effective']['pins'] != PROFILES[DSB_SHUTDOWN_PROFILE]['replacement_pins']
            or old_tools['effective']['publication_mode'] != 'on_shutdown'
            or command.get('status') != 'complete' or command.get('returncode') != 0
            or command.get('publication_mode') != 'on_shutdown'
            or command.get('ingest', {}).get('dropped_spans') != 0
            or command.get('ingest', {}).get('late_spans') != 0):
        raise ValueError('reference is not the fixed completed Bering 1.2 shutdown branch')
    result = dict(identity=identity, complete_archive_verified=True, gzip_crc_verified=True,
                  counts=counts, native=native.result(), selected=retained,
                  full_retention='Unchanged original Actions artifact; this is a verified selected inspection view')
    write_json(out/'reference-verification.json', result)
    return result


def semantic_projection(model, snapshot, quality, export_hashes, overlay_path, overlay_sha):
    """Normalize only the predeclared transport/runtime fields, not observations."""
    model, snapshot, quality = copy.deepcopy((model, snapshot, quality))
    if snapshot['model'] != model:
        raise ValueError('snapshot/model copies disagree')
    if any(quality['artifact'].get(key) != snapshot.get(key) for key in
           ('topology_version', 'snapshot_id', 'window_start', 'window_end')):
        raise ValueError('quality/snapshot runtime identity mismatch')
    listener = model['metadata']['source_ref']
    if not LISTENER.fullmatch(listener) or snapshot['metadata']['source_ref'] != listener:
        raise ValueError('unexpected Bering runtime listener identity')

    def ref(value):
        if value == listener:
            return 'bering://serve?listen=runtime-listener'
        if value == overlay_path:
            return 'fixed-overlay:sha256:'+overlay_sha
        if match := CAPTURE.fullmatch(value):
            ordinal, payload_hash, extension, compressed = match.groups()
            position = int(ordinal)-1
            if position < 0 or position >= len(export_hashes) or export_hashes[position] != payload_hash:
                raise ValueError('OBI provenance is not bound to unchanged export ordinal/hash')
            return 'obi-capture/'+ordinal+'-'+payload_hash+extension+(compressed or '')
        return value

    def sources(rows):
        for row in rows:
            if 'ref' in row:
                row['ref'] = ref(row['ref'])
        rows.sort(key=canonical)

    def evidence(record):
        # Explicit evidence-schema locations only. Attributes are opaque and
        # never rewritten even if named ref/source_ref/timestamp/snapshot_id.
        entities = [*record.get('instances', []), *record.get('database_aliases', [])]
        entities.extend(record[key] for key in ('database', 'peer', 'relation') if key in record)
        for entity in entities:
            if 'sources' in entity:
                sources(entity['sources'])

    model['metadata']['source_ref'] = ref(listener)
    model['metadata']['discovered_at'] = '<runtime-publication>'
    normalized_digest = 'sha256:'+hashlib.sha256(canonical(model)).hexdigest()
    snapshot['model'] = copy.deepcopy(model)
    snapshot['metadata']['source_ref'] = ref(listener)
    snapshot['metadata']['emitted_at'] = '<runtime-publication>'
    sources(snapshot['sources'])
    for collection in ('services', 'edges', 'endpoints'):
        for entity in snapshot['discovery'][collection]:
            if 'provenance' in entity:
                sources(entity['provenance'])
            attributes = entity.get('metadata', {}).get('attributes', {})
            if EVIDENCE_KEY in attributes:
                record = json.loads(attributes[EVIDENCE_KEY])
                evidence(record)
                attributes[EVIDENCE_KEY] = record
    for overlay in snapshot['discovery'].get('overlays', []):
        if 'ref' in overlay:
            overlay['ref'] = ref(overlay['ref'])
    for key in ('window_start', 'window_end', 'snapshot_id'):
        snapshot[key] = '<runtime-'+key+'>'
    snapshot['topology_version'] = normalized_digest
    quality['generated_at'] = '<runtime-publication>'
    for key in ('path', 'snapshot_id', 'window_start', 'window_end'):
        quality['artifact'][key] = '<runtime-'+key+'>'
    quality['artifact']['topology_version'] = normalized_digest
    for entity in quality.get('observation_evidence', []):
        evidence(entity['evidence'])
    return dict(model=model, snapshot=snapshot, quality=quality)


def compare(original, reference, out, source, replacement_root):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('real-data batching comparison runs only in GitHub Actions')
    original, reference, out = [Path(path).resolve() for path in (original, reference, out)]
    for other in (original, reference):
        if out == other or out.is_relative_to(other) or other.is_relative_to(out):
            raise ValueError('comparison/source trees must be separate')
    out.mkdir(parents=True, exist_ok=False)
    status = dict(schema_version='v4-native-envelope-equivalence', status='started',
        started_ns=time.time_ns(), new_application_traffic=False, completed_campaign_cell=False,
        fixed_branch='combined/network_scope/compose_post', baseline='per_trace', candidate='per_file',
        normalization=NORMALIZATION)
    write_json(out/'status.json', status)
    before, failed = None, False
    try:
        before = file_manifest(original)
        validation = validate_checkpoint_manifest(original, source, DSB_SHUTDOWN_PROFILE)
        plans, training = validate_training_prefix(original)
        profile = PROFILES[DSB_SHUTDOWN_PROFILE]
        binary, old_root, toolchain = runtime_binaries(original, out, profile, replacement_root)
        reference_tools = read(reference/'output/toolchain-provenance.json')
        for version in ('original', 'effective'):
            for name, actual in toolchain[version]['binaries'].items():
                expected = reference_tools[version]['binaries'][name]
                if any(actual[key] != expected[key] for key in ('commit', 'sha256', 'bytes')):
                    raise ValueError('comparison binary differs from authenticated baseline: '+version+'/'+name)
        index = relocate_index(original, out, old_root)
        write_json(out/'provenance.json', dict(source=source, checkpoint=validation, training=training,
            index=index, toolchain=toolchain, reference=read(reference/'reference-verification.json')))
        shutil.copy2(original/'deployment.json', out/'deployment.json')
        ctx = Context(out, 'full', 6)
        ctx.deployment_dir = original/'deployment'
        store = ObservationStore(out/'observation-index.sqlite', same_trace_parents=True)
        previous_bin = os.environ.get('PBS_BIN')
        os.environ['PBS_BIN'] = str(binary)
        try:
            declaration = importlib.import_module('systems.deathstarbench.experiment_v4')
            driver = Toolchain(ctx, 'deathstarbench', store, declaration,
                tool_pins=toolchain['effective']['pins'], publication_mode='on_shutdown',
                native_jaeger_envelope='per_file')
            driver.prepare_inputs(plans)
            native = Resources()
            _, new_native = driver.input_manifests['native', 'network_scope']
            for export in new_native['exports']:
                with Path(export['path']).open('rb') as stream:
                    native.add(stream)
            old_native = read(reference/'reference-verification.json')['native']
            new_fingerprint = native.result()
            equality = {key: old_native[key] == new_fingerprint[key] for key in
                        ('ordered_resource_spans_sha256', 'resource_groups', 'observations')}
            old_ebpf = read(reference/EBPF/'observations.json')
            _, new_ebpf = driver.input_manifests['ebpf', 'network_scope']
            keys = ('sha256', 'content_type', 'content_encoding', 'observations', 'source')
            ebpf_equal = ([{key:e.get(key) for key in keys} for e in old_ebpf['exports']]
                          == [{key:e.get(key) for key in keys} for e in new_ebpf['exports']])
            write_json(out/'input-equivalence.json', dict(reference=old_native, candidate=new_fingerprint,
                exact_ordered_native_equality=equality, exact_ebpf_exports_equal=ebpf_equal,
                candidate_manifest=str(driver.input_manifests['combined', 'network_scope'][0])))
            if not all(equality.values()) or not ebpf_equal:
                raise ValueError('batching changed input evidence before Bering')
            branch = out/'fixed-branch'
            branch.mkdir()
            overlay = reference/BRANCH/'overlay.json'
            shutil.copy2(overlay, branch/'overlay.json')
            with child_go_environment(profile['bering_child_go_environment']):
                driver.discover(driver.input_manifests['combined', 'network_scope'][0], branch,
                                overlay=branch/'overlay.json')
        finally:
            store.close()
            if previous_bin is None:
                os.environ.pop('PBS_BIN', None)
            else:
                os.environ['PBS_BIN'] = previous_bin
        projections = {}
        hashes = [export['sha256'] for export in new_ebpf['exports']]
        for label, folder in (('reference', reference/BRANCH), ('candidate', out/'fixed-branch')):
            command = read(folder/'model-runtime/replay-command.json')
            overlay_path = str(Path(command['argv'][-1]).parent.parent/'overlay.json')
            projections[label] = semantic_projection(*(read(folder/name) for name in
                ('model.json', 'model.snapshot.json', 'model.signal-quality.json')), hashes,
                overlay_path, digest(folder/'overlay.json'))
            write_json(out/(label+'-semantic-projection.json'), projections[label])
        differences = {key: projections['reference'][key] != projections['candidate'][key]
                       for key in projections['reference']}
        write_json(out/'comparison.json', dict(equal=not any(differences.values()),
            differing_artifacts=differences, normalization=NORMALIZATION,
            reference_projection_sha256=digest(out/'reference-semantic-projection.json'),
            candidate_projection_sha256=digest(out/'candidate-semantic-projection.json')))
        if any(differences.values()):
            raise ValueError('fixed real Bering graph/evidence changed under native batching')
        status['status'] = 'equivalent_fixed_branch'
        return status
    except BaseException as error:
        failed = True
        status.update(status='comparison_failed', error=repr(error))
        raise
    finally:
        try:
            status['immutable_checkpoint_unchanged'] = file_manifest(original) == before if before is not None else None
        except Exception as error:
            status['immutable_checkpoint_unchanged'] = False
            status['checkpoint_rehash_error'] = repr(error)
        status['ended_ns'] = time.time_ns()
        if status['immutable_checkpoint_unchanged'] is False:
            status['status'] = 'comparison_failed'
            status.setdefault('error', 'immutable source changed or could not be rehashed')
        write_json(out/'status.json', status)
        if status['immutable_checkpoint_unchanged'] is False and not failed:
            raise RuntimeError('immutable source changed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('reference', 'compare'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--package', type=Path)
    parser.add_argument('--original', type=Path)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--replacement-root', type=Path)
    args = parser.parse_args()
    if args.operation == 'reference':
        inspect_reference(args.package, args.out, read(args.source))
    else:
        compare(args.original, args.reference, args.out, read(args.source), args.replacement_root)


if __name__ == '__main__':
    main()
