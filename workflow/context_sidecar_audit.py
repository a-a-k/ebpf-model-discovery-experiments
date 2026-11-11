#!/usr/bin/env python3
"""Inspect three frozen context-union results in GitHub Actions.

This reader runs no application, discovery, binding, simulation or new capture.
It verifies saved model differences and evidence annotations. Exact parent/child
source and span pairs are not inferred from a mixed-input edge or aggregate
source references. The separate core replay remains authoritative for replay.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import time


MODEL_SOURCE = '76aebebfc11c68c2c6f4b916f715a833f548d9cc'
CAPTURE_SOURCE = '5e622ed58c340e2cfe85c3c287ba90bc9c610190'
PINS = {
    9: {
        'artifact_id': 13610535986, 'artifact_bytes': 877410215,
        'artifact_sha256': 'ca6ed509851cc045d9c6555c932054bc979412e4a94f75428249a1b345c93af6',
        'model_run': 42457618421, 'model_slot': 0,
        'capture_run': 42401605258, 'capture_artifact_id': 13587602964,
        'closed_input_sha256': '15f79df031b523eac4661cfa57b0a58aba1d7b07089f22f92461e03ecd391a9c',
        'forecast_manifest_sha256': '00277f12cf6cee3992439993da9cdcf74e99159d8f52b09c7833afec6e32f0e3',
    },
    10: {
        'artifact_id': 13610776995, 'artifact_bytes': 878355134,
        'artifact_sha256': '0b21874598346af45397eb29bb5a29b8b893189cf00fb6d8f15359a288e7bdda',
        'model_run': 42457621770, 'model_slot': 1,
        'capture_run': 42401608466, 'capture_artifact_id': 13587388281,
        'closed_input_sha256': 'b102c1d16b223c5e36f155f38f8e9b89162458a01e4eedd0a8c9285bde9ac13c',
        'forecast_manifest_sha256': '6e88a515d60e697aa0ace1988b1038d7eda7d2358601db0d9a65b37d7cc84dbd',
    },
    11: {
        'artifact_id': 13610478019, 'artifact_bytes': 875593371,
        'artifact_sha256': 'cf792daeb2f780f76f0299f375a1fbd17ad4d83dfe6d5d659f3cf92b7d811a40',
        'model_run': 42457624998, 'model_slot': 3,
        'capture_run': 42401611728, 'capture_artifact_id': 13587602313,
        'closed_input_sha256': '9e6405db09c4c4be93bcbffacf8e23f5cadfd6a9b21c545559b4969475600d13',
        'forecast_manifest_sha256': 'f8ace8b44df495b9b82643bcf15d06bcdeedb3145960a547553aac478338f87f',
    },
}
VARIANTS = ('raw', 'network_scope')
OPS = ('browse_product', 'add_to_cart', 'checkout')
MAX_SELECTED_BYTES = 512 * 1024**2
MAX_REPORT_BYTES = 16 * 1024**2
PAIR_STATUS = 'unknown_original_source_span_pair_not_established_by_sidecar_audit'


def load_helper(path):
    spec = importlib.util.spec_from_file_location('publication_replay_reader', path)
    if spec is None or spec.loader is None:
        raise ValueError('cannot load the reviewed publication reader')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selected_member(name):
    if name in {'forecast-saved.json', 'status.json', 'closed-input.json',
                'toolchain/forecasts.json', 'toolchain/context-baseline/forecasts.json'}:
        return True
    for variant in VARIANTS:
        if name == f'toolchain/discovery/combined/{variant}/observed.json':
            return True
        prefix = f'toolchain/context-baseline/{variant}/'
        if name in {prefix + tail for tail in (
                'union-proof.json', 'union-model.json', 'provenance.json',
                'joint/canonical.json', 'joint/canonical.signal-quality.json')}:
            return True
        if name in {prefix + f'operations/{op}/{tail}'
                    for op in OPS for tail in ('binding.json', 'forecast.json')}:
            return True
    return False


def compact_evidence(row):
    """Keep the relation basis and bounded examples; certify no source pair."""
    if row is None:
        return {'status': 'unknown_no_edge_quality_annotation',
                'cross_source_pair_status': PAIR_STATUS}
    evidence = row.get('evidence') or {}
    relation = evidence.get('relation') or {}
    sources = relation.get('sources') or []
    descriptors = sorted({(str(s.get('kind', '')), str(s.get('connector', '')),
                           str(s.get('domain', ''))) for s in sources})
    raw_record = json.dumps(row, sort_keys=True, separators=(',', ':'),
                            ensure_ascii=False).encode('utf-8')
    return {
        'status': 'saved_quality_annotation', 'schema_version': evidence.get('schema_version'),
        'saved_evidence_fields': sorted(evidence), 'saved_relation_fields': sorted(relation),
        'relation_kind': relation.get('kind'), 'relation_basis': relation.get('basis'),
        'from_instances': relation.get('from_instances'),
        'to_instances': relation.get('to_instances'),
        'source_descriptors': [{'kind': a, 'connector': b, 'domain': c} for a, b, c in descriptors],
        'source_reference_count': len(sources), 'source_reference_examples': sources[:2],
        'omitted_source_reference_count': max(0, len(sources) - 2),
        'saved_annotation_canonical_json_sha256': hashlib.sha256(raw_record).hexdigest(),
        'cross_source_pair_status': PAIR_STATUS,
        'original_source_span_pair_reconstructed': False,
    }


def anchored_reference(helper, root, reference, expected_name):
    path = root / expected_name
    helper.require(path.is_file(), 'required context member unavailable: ' + expected_name)
    helper.require(reference.get('path', '').endswith('/' + expected_name)
                   or reference.get('path') == expected_name,
                   'context reference path differs from the selected member')
    helper.require(helper.digest(path) == reference.get('sha256'),
                   'context proof reference differs from verified member')
    return helper.reference(path)


def inspect_variant(helper, root, seed, variant):
    prefix = f'toolchain/context-baseline/{variant}/'
    proof = helper.read(root / (prefix + 'union-proof.json'))
    references = {
        'base_model': f'toolchain/discovery/combined/{variant}/observed.json',
        'joint_model': prefix + 'joint/canonical.json',
        'union_model': prefix + 'union-model.json',
        'joint_canonical_quality': prefix + 'joint/canonical.signal-quality.json',
    }
    verified_refs = {key: anchored_reference(helper, root, proof['files'][key], name)
                     for key, name in references.items()}
    base = helper.read(root / references['base_model'])
    joint = helper.read(root / references['joint_model'])
    union = helper.read(root / references['union_model'])
    def edge_index(model):
        edges = {e['id']: e for e in model['edges']}
        helper.require(len(edges) == len(model['edges']), 'duplicate saved edge identifier')
        return edges
    before, added_view, after = edge_index(base), edge_index(joint), edge_index(union)
    recorded = proof['added_edge_ids']
    helper.require(len(recorded) == len(set(recorded)), 'duplicate union-proof edge identifier')
    helper.require(set(after) - set(before) == set(recorded) and set(before) <= set(after),
                   'recorded added edge IDs differ from saved graph delta')
    helper.require(all(after[key] == value for key, value in before.items()),
                   'an original edge record changed in the saved union')
    helper.require({k: v for k, v in base.items() if k != 'edges'} ==
                   {k: v for k, v in union.items() if k != 'edges'},
                   'saved union changed services, endpoints or other original model fields')
    helper.require(not proof.get('semantic_identity_conflicts') and
                   not proof.get('joint_alias_metadata_collisions'),
                   'saved union retains identity conflicts')
    service_ids = {s['id'] for s in base['services']}
    quality = helper.read(root / references['joint_canonical_quality'])
    annotations = [r for r in quality.get('observation_evidence', [])
                   if r.get('entity_type') == 'edge']
    evidence = {r['entity_id']: r for r in annotations}
    helper.require(len(evidence) == len(annotations), 'duplicate edge-quality annotation')
    provenance = helper.read(root / (prefix + 'provenance.json'))
    operations = {}
    for op in OPS:
        folder = root / (prefix + 'operations/' + op)
        binding, forecast = helper.read(folder / 'binding.json'), helper.read(folder / 'forecast.json')
        operations[op] = {'available': binding['available'],
                          'forecast': forecast.get('prediction'),
                          'required_edges': binding.get('required_edges', [])}
    rows = []
    for edge_id in recorded:
        edge = after[edge_id]
        helper.require(edge == added_view.get(edge_id), 'added edge differs from saved joint model')
        helper.require((edge.get('identity') or {}).get('span_kind') == 'server',
                       'added edge lacks the required SERVER-child identity')
        helper.require(edge['from'] in service_ids and edge['to'] in service_ids,
                       'added edge endpoint service absent from canonical graph')
        rows.append({'repetition': seed, 'variant': variant, 'edge': edge,
                     'in_canonical_graph': False, 'copied_from_saved_joint_model': True,
                     'endpoint_services_in_canonical_graph': True,
                     'required_by_operations': [op for op, row in operations.items()
                                                if edge_id in row['required_edges']],
                     'joint_quality_evidence': compact_evidence(evidence.get(edge_id))})
    return {
        'repetition': seed, 'variant': variant, 'status': 'verified_saved_union_edges',
        'verified_member_references': verified_refs, 'provenance_status': provenance.get('status'),
        'saved_source_observation_counts': provenance.get('source_observations'),
        'recorded_added_edge_ids': recorded, 'added_edge_count': len(recorded),
        'existing_edges_unchanged': True, 'services_endpoints_and_other_model_fields_unchanged': True,
        'all_added_edges_copied_from_joint_model': True,
        'all_added_edges_server_child_with_existing_endpoint_services': True,
        'cross_source_pair_status': PAIR_STATUS, 'operations': operations, 'added_edges': rows,
    }


def check_pin(helper, cell, seed, pin):
    lineage = cell['verified_replay_lineage']
    api, processing = lineage['model_artifact_API'], lineage['processing_execution']
    helper.require((api['id'], api['size_in_bytes'], api['digest']) ==
                   (pin['artifact_id'], pin['artifact_bytes'], 'sha256:' + pin['artifact_sha256']),
                   'model artifact differs from independently anchored result')
    helper.require(int(processing['run_id']) == pin['model_run'] and processing['commit'] == MODEL_SOURCE,
                   'historical model producer differs')
    helper.require((lineage['training_run_id'], lineage['training_artifact_id'],
                    lineage['training_source'], lineage['training_closed_input_sha256']) ==
                   (pin['capture_run'], pin['capture_artifact_id'], CAPTURE_SOURCE,
                    pin['closed_input_sha256']), 'historical capture lineage differs')
    helper.require(cell['original_forecast']['forecast_manifest_sha256'] == pin['forecast_manifest_sha256'],
                   'frozen forecast digest differs')


def save_tables(destination, cases):
    edge_fields = ('repetition', 'variant', 'edge_id', 'from', 'to', 'span_kind',
                   'relation_basis', 'endpoints_in_canonical', 'required_by_operations',
                   'cross_source_pair_status')
    with (destination / 'context-added-edges.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=edge_fields)
        writer.writeheader()
        for case in cases:
            for variant in case.get('variants', []):
                for row in variant['added_edges']:
                    edge, evidence = row['edge'], row['joint_quality_evidence']
                    writer.writerow({'repetition': row['repetition'], 'variant': row['variant'],
                        'edge_id': edge['id'], 'from': edge['from'], 'to': edge['to'],
                        'span_kind': edge['identity']['span_kind'],
                        'relation_basis': evidence.get('relation_basis', 'unknown'),
                        'endpoints_in_canonical': True,
                        'required_by_operations': ';'.join(row['required_by_operations']),
                        'cross_source_pair_status': evidence['cross_source_pair_status']})
    with (destination / 'context-summary.csv').open('w', newline='', encoding='utf-8') as stream:
        fields = ('repetition', 'variant', 'status', 'added_edges', 'existing_edges_unchanged',
                  'services_endpoints_unchanged', 'supported_operations', 'cross_source_pair_status')
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            for variant in case.get('variants', []) or [{'status': case['status']}]:
                writer.writerow({'repetition': case['key'][2], 'variant': variant.get('variant', 'unknown'),
                    'status': variant['status'], 'added_edges': variant.get('added_edge_count'),
                    'existing_edges_unchanged': variant.get('existing_edges_unchanged'),
                    'services_endpoints_unchanged': variant.get('services_endpoints_and_other_model_fields_unchanged'),
                    'supported_operations': ';'.join(op for op, row in variant.get('operations', {}).items()
                                                    if row['available']),
                    'cross_source_pair_status': variant.get('cross_source_pair_status', 'unknown')})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helper', type=Path, default=Path('scripts/replay-publication-example.py'))
    parser.add_argument('--core', type=Path, default=Path('out/evidence/code-and-results.zip'))
    parser.add_argument('--work', type=Path, default=Path('work/context-sidecars'))
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise SystemExit('saved scientific artifact inspection must run in GitHub Actions')
    helper = load_helper(args.helper.resolve())
    args.work, args.out = args.work.resolve(), args.out.resolve()
    args.work.mkdir(parents=True, exist_ok=True)
    destination = args.out / 'evidence/context'
    destination.mkdir(parents=True, exist_ok=True)
    receipt = {'status': 'running', 'started_ns': time.time_ns(), 'cases': [],
               'separate_from_main_replay': True, 'new_model_execution': False,
               'new_application_measurements': False, 'source_span_pairs_inferred': False,
               'model_source': MODEL_SOURCE, 'capture_source': CAPTURE_SOURCE,
               'reader_sha256': helper.digest(Path(__file__)),
               'shared_helper_sha256': helper.digest(args.helper),
               'reader_execution': {k: os.environ.get(k) for k in
                                    ('GITHUB_SHA', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_JOB')},
               'maximum_selected_member_bytes_per_case': MAX_SELECTED_BYTES,
               'human_seconds': None, 'human_cost_status': 'unmeasured'}
    receipt_path = destination / 'context-sidecar-receipt.json'
    helper.write(receipt_path, receipt)
    try:
        helper.verify(args.core, *helper.CORE)
        receipt['core'] = helper.reference(args.core)
        cells = helper.load_core(args.core)['cells']
        helper.require((args.out / 'download-budget.json').is_file(),
                       'shared download-budget receipt from the core stage is required')
        budget = helper.DownloadBudget(args.out / 'download-budget.json')
        for seed, pin in PINS.items():
            result = {'key': ['otel_demo', 'partial', seed, 'obi'], 'status': 'started', 'pins': pin}
            receipt['cases'].append(result)
            archive, target = args.work / f'context-{seed}.zip', args.work / f'repetition-{seed}'
            owns_paths = False
            try:
                helper.require(not archive.exists() and not target.exists(),
                               'context working paths must be new and owned by this invocation')
                owns_paths = True
                matches = [row for row in cells if row['key'] == result['key']]
                helper.require(len(matches) == 1, 'exactly one frozen case required')
                cell = matches[0]
                check_pin(helper, cell, seed, pin)
                result['artifact_API'] = helper.github_artifact(pin['artifact_id'], pin['artifact_bytes'],
                    pin['artifact_sha256'], budget, archive)
                api = result['artifact_API']
                helper.require(api['workflow_run']['id'] == pin['model_run'] and
                               api['workflow_run']['head_sha'] == MODEL_SOURCE and
                               api['name'] == f"v6-isolated-model-slot{pin['model_slot']}-{pin['model_run']}-attempt1",
                               'retrieved artifact producer identity differs')
                result['package'] = helper.unpack_package(archive, 'model', target,
                                                           selected_member, MAX_SELECTED_BYTES)
                helper.require(helper.digest(target / 'forecast-saved.json') == pin['forecast_manifest_sha256'],
                               'forecast freeze differs from the anchored result')
                saved = helper.read(target / 'forecast-saved.json')
                helper.require(saved['case'] == cell['original_forecast']['case'], 'frozen capture case differs')
                helper.require(helper.digest(target / 'closed-input.json') == pin['closed_input_sha256'],
                               'closed capture input differs from anchored lineage')
                for name in result['package']['selected_files']:
                    if name.startswith('toolchain/'):
                        helper.require(saved['sha256_by_path'].get(name) == helper.digest(target / name),
                                       'selected sidecar differs from the anchored forecast freeze')
                variants = [inspect_variant(helper, target, seed, variant) for variant in VARIANTS]
                encoded = json.dumps(variants, ensure_ascii=False).encode('utf-8')
                helper.require(len(encoded) <= MAX_REPORT_BYTES, 'bounded context report exceeded')
                result['variants'] = variants
                result['status'] = 'verified_saved_union_edges'
                result['cross_source_pair_status'] = PAIR_STATUS
            except Exception as exc:
                result.update(status='unknown', error_type=type(exc).__name__)
                if isinstance(exc, (ValueError, FileNotFoundError)):
                    result['reason'] = str(exc)[:600]
                response = getattr(exc, 'response', None)
                if response is not None:
                    result['http_status'] = response.status_code
            finally:
                if owns_paths:
                    if archive.exists():
                        archive.unlink()
                    if target.exists():
                        shutil.rmtree(target)
                result['owned_archive_and_expanded_members_released'] = owns_paths
                helper.write(receipt_path, receipt)
        receipt['status'] = ('verified_saved_edges_pair_sources_unresolved' if
                             all(r['status'] == 'verified_saved_union_edges' for r in receipt['cases'])
                             else 'completed_with_unknowns')
    except Exception as exc:
        receipt.update(status='unavailable', error_type=type(exc).__name__)
        if isinstance(exc, (ValueError, FileNotFoundError)):
            receipt['reason'] = str(exc)[:600]
    finally:
        save_tables(destination, receipt['cases'])
        receipt.update(ended_ns=time.time_ns(),
                       elapsed_seconds=(time.time_ns() - receipt['started_ns']) / 1e9,
                       max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       disk_free_bytes=shutil.disk_usage(args.work).free)
        helper.write(receipt_path, receipt)
        print(json.dumps({'context_sidecar_status': receipt['status'],
                          'cases_retained': len(receipt['cases'])}), flush=True)
    return 0 if receipt['status'] == 'verified_saved_edges_pair_sources_unresolved' else 2


if __name__ == '__main__':
    raise SystemExit(main())
