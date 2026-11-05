"""Locate attribute-key failures in fixed saved wire bytes without normalizing spans."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import time
import zipfile

from google.protobuf.json_format import MessageToDict, ParseDict, ParseError
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.proto.common.v1.common_pb2 import KeyValue


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def extract(source, role, expected):
    metadata = read(source / (role + '-api.json'))
    archive = source / (role + '.zip')
    if (metadata['id'] != expected['id'] or metadata['name'] != expected['name']
            or metadata['digest'] != expected['digest'] or metadata.get('expired') is not False
            or metadata['workflow_run']['id'] != expected['run_id']
            or metadata['workflow_run']['head_sha'] != expected['head_sha']
            or metadata['size_in_bytes'] != expected['bytes']
            or archive.stat().st_size != expected['bytes']
            or sha(archive) != expected['digest'].removeprefix('sha256:')):
        raise ValueError('fixed source archive identity differs')
    root = source / role
    with zipfile.ZipFile(archive) as bundle:
        if len(bundle.namelist()) != len(set(bundle.namelist())):
            raise ValueError('duplicate source ZIP member')
        for item in bundle.infolist():
            name = PurePosixPath(item.filename)
            if (name.is_absolute() or '..' in name.parts or '\\' in item.filename
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError('unsafe source ZIP member')
        bundle.extractall(root)
    return root


def key_entries(value, path=()):
    if isinstance(value, dict):
        for name, child in value.items():
            child_path = (*path, name)
            if isinstance(child, list) and (name == 'attributes'
                    or (name == 'values' and path and path[-1] == 'kvlistValue')):
                for ordinal, entry in enumerate(child):
                    yield (*child_path, ordinal), entry
            yield from key_entries(child, child_path)
    elif isinstance(value, list):
        for ordinal, child in enumerate(value):
            yield from key_entries(child, (*path, ordinal))


def proto_at(message, path):
    current = message
    for token in path:
        if isinstance(token, int):
            current = current[token]
        else:
            field = next(f for f in current.DESCRIPTOR.fields if f.json_name == token)
            current = getattr(current, field.name)
    if current.DESCRIPTOR.full_name != KeyValue.DESCRIPTOR.full_name:
        raise ValueError('attribute locator does not identify a protobuf KeyValue')
    return current


def raw_path(root, journal, reference):
    if reference.startswith('/'):
        for folder in ('observations', 'native'):
            marker = '/' + folder + '/'
            if marker in reference:
                target = root / folder / reference.split(marker, 1)[1]
                break
        else:
            raise ValueError('unrecognized original wire reference')
    else:
        target = journal.parent / reference
    target.resolve().relative_to(root.resolve())
    return target


def inspect(root):
    named = [root / 'observations' / (node + '.jsonl') for node in ('a', 'b', 'native')]
    paths = {path for path in named if path.is_file()}
    paths.update(path for path in (root / 'native').rglob('*')
                 if path.is_file() and path.name.startswith('native-node-') and path.suffix == '.jsonl')
    result = {'named_streams_absent': [p.relative_to(root).as_posix() for p in named if not p.is_file()],
              'streams': [], 'witnesses': [], 'witness_limit_per_issue_and_context': 16,
              'scope': 'Every complete record in the listed retained OTLP candidate journals; no other stream is implied.'}
    for path in sorted(paths):
        counts = {'records': 0, 'attribute_entries': 0, 'missing_key': 0,
                  'explicit_empty_key': 0, 'nonobject_attribute': 0, 'raw_refs_verified': 0}
        with path.open('rb') as stream:
            for ordinal, line in enumerate(stream, 1):
                if not line.endswith(b'\n'):
                    raise ValueError('candidate journal has an incomplete retained record')
                document = json.loads(line)
                payload = document.get('payload', document)
                protobuf = None
                raw = None
                projection_equal = None
                if document.get('raw_ref'):
                    target = raw_path(root, path, document['raw_ref'])
                    body = target.read_bytes()
                    if hashlib.sha256(body).hexdigest() != document['raw_sha256']:
                        raise ValueError('wire record SHA differs from retained receiver envelope')
                    counts['raw_refs_verified'] += 1
                    raw = {'member': target.relative_to(root).as_posix(), 'sha256': sha(target), 'bytes': len(body)}
                    if document.get('content_encoding', '').lower() == 'gzip':
                        body = gzip.decompress(body)
                    if 'protobuf' in document.get('content_type', ''):
                        protobuf = ExportTraceServiceRequest.FromString(body)
                        projection_equal = MessageToDict(protobuf) == payload
                    elif 'json' in document.get('content_type', ''):
                        projection_equal = json.loads(body) == payload
                counts['records'] += 1
                for locator, entry in key_entries(payload):
                    counts['attribute_entries'] += 1
                    issue = ('nonobject_attribute' if not isinstance(entry, dict) else
                             'missing_key' if 'key' not in entry else
                             'explicit_empty_key' if entry['key'] == '' else None)
                    if issue is None:
                        continue
                    counts[issue] += 1
                    context = ('direct_span_attributes' if len(locator) == 8 and locator[-4] == 'spans'
                               and locator[-2] == 'attributes' else
                               'direct_resource_attributes' if len(locator) == 5 and locator[-3:-1] == ('resource', 'attributes')
                               else 'other_or_nested_attributes')
                    if sum(w['issue'] == issue and w['normalizer_context'] == context
                           for w in result['witnesses']) >= result['witness_limit_per_issue_and_context']:
                        continue
                    siblings = payload
                    for token in locator[:-1]:
                        siblings = siblings[token]
                    witness = {'journal': path.relative_to(root).as_posix(), 'record_ordinal': ordinal,
                               'record_byte_offset': stream.tell() - len(line), 'record_bytes': len(line),
                               'record_sha256': hashlib.sha256(line).hexdigest(), 'raw_wire': raw,
                               'receiver_clock_fields': {k: v for k, v in document.items() if k.endswith('_ns')},
                               'raw_projection_equals_retained_payload': projection_equal,
                               'attribute_path': list(locator), 'issue': issue,
                               'normalizer_context': context, 'original_json_entry': entry,
                               'surrounding_keys': [item.get('key', '<missing>') if isinstance(item, dict)
                                                    else '<nonobject>' for item in siblings]}
                    try:
                        attribute = proto_at(protobuf, locator) if protobuf is not None else ParseDict(entry, KeyValue())
                        witness.update(protobuf_key=attribute.key,
                            protobuf_key_default=attribute.DESCRIPTOR.fields_by_name['key'].default_value,
                            protobuf_nondefault_fields=[field.name for field, _ in attribute.ListFields()],
                            protobuf_value_kind=attribute.value.WhichOneof('value'),
                            protobuf_json_projection=MessageToDict(attribute),
                            projection_equals_retained_entry=MessageToDict(attribute) == entry,
                            semantic_source='original protobuf wire' if protobuf is not None else 'KeyValue-only JSON parse; no span IDs interpreted',
                            scalar_wire_presence_claimed=False)
                    except (ValueError, TypeError, StopIteration, IndexError, ParseError) as error:
                        witness['protobuf_interpretation_error'] = type(error).__name__ + ':' + str(error)
                    result['witnesses'].append(witness)
        result['streams'].append({'member': path.relative_to(root).as_posix(),
                                 'bytes': path.stat().st_size, 'sha256': sha(path), **counts})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--cell', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    cell = read(args.cell)
    full = extract(args.source, 'full', cell['full'])
    compact = extract(args.source, 'compact', cell['compact'])
    facts = inspect(full)
    facts.update(cell=cell, original_status=read(compact / 'status.json'),
                 original_evaluation=read(compact / 'evaluation-v5.json'),
                 elapsed_seconds=time.monotonic() - started,
                 capture_refit_replay_scoring_or_admission_performed=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(facts, indent=2) + '\n')
