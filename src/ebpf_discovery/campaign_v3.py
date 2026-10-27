"""Fresh 20 ops/s campaigns with frozen declared completion and source comparisons."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import traceback

from .campaign import Campaign
from .collectors import Collectors
from .evaluate import ari, evaluation_map, external_rate
from .async_links import message_chains
from .observations import opaque_attempt
from .runtime import write_json
from .semantic_v3 import Binder, SOURCES, declared_census, fit_declared, transport_observations
from .store_v3 import ObservationStore
from .timing_v3 import automatic_census, http_curves

PRIMARY_PHASES = ('class_train', 'calibration', 'target', 'class_test')
RULE_FILES = ['src/ebpf_discovery/'+name+'.py' for name in
              ('semantic_v3', 'store_v3', 'observations', 'model', 'async_links', 'campaign_v3', 'timing_v3')]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class CampaignV3(Campaign):
    def __init__(self, system, mode, seed, out, qualification=False):
        super().__init__(system, mode, seed, out)
        self.rate, self.workers = 20, 256
        self.http_cap, self.verify_all_checkouts = 10.0, False
        self.ctx.observation_policy = 'censored-v3'
        self.ctx.observation_cap_seconds = self.http_cap
        self.qualification = qualification
        self.collectors = Collectors(self.ctx, semantic=True)
        self.store = ObservationStore(self.ctx.out/'observation-index.sqlite')
        self.frozen = {}
        self.automatic_classes = {}
        self.database_model = None

    def snapshot(self, stage):
        self.collectors.snapshot()
        self.adapter.collect_native(self.ctx.out/'native'/stage)
        started = time.time_ns()
        evidence = self.store.ingest(self.collectors.root, self.ctx.out/'native')
        evidence.update(started_ns=started, ended_ns=time.time_ns())
        write_json(self.ctx.out/f'index-{stage}.json', evidence)
        # Index preserves source-local conflicting variants rather than silently
        # selecting one. Raw sources stay immutable/append-only alongside it.
        return evidence

    def binder(self):
        context = {}
        if self.system == 'petclinic':
            context['fixture'] = json.loads((self.ctx.deployment_dir/'petclinic'/'fixture.json').read_text())
        return Binder(self.store, self.system, context)

    def remember(self, path):
        self.frozen[str(path.relative_to(self.ctx.out))] = digest(path)

    def freeze(self, names):
        started = time.perf_counter()
        rows = declared_census(self.records)
        write_json(self.ctx.out/'declared-journal-training.json', rows)
        binder = self.binder()
        projections = binder.project(rows, transport_observations(self.records))
        for source in SOURCES:
            graph = self.store.graph(source) if source != 'entry_http' else {'nodes': [], 'edges': []}
            model, forecast = fit_declared(projections[source], names, self.ctx.seed, graph)
            folder = self.ctx.out/'models'/source
            for filename, value in (('model.json', model), ('forecast.json', forecast)):
                path = folder/filename
                write_json(path, value)
                self.remember(path)
            write_json(self.ctx.out/'projections'/f'{source}-training.json', projections[source])
        # Label-free class discovery is evaluated separately. No external labels
        # feed these classes, and no future signatures may extend them.
        for source in ('ebpf', 'native', 'combined'):
            self.automatic_classes[source] = {}
            for variant in ('route', 'route_and_downstream'):
                classes, assigned = binder.automatic(automatic_census(self.records, self.census), source, downstream=variant != 'route')
                self.automatic_classes[source][variant] = classes
                folder = self.ctx.out/'automatic'/source/variant
                for filename, value in (('classes.json', classes),
                                        ('evaluation-map.json', evaluation_map(self.records, assigned))):
                    path = folder/filename
                    write_json(path, value)
                    self.remember(path)
                write_json(folder/'training-assignments.json', assigned)
        if self.system == 'petclinic':
            from systems.petclinic.database_v3 import endpoint_inventory, learn_database_effects, predict_database_effects
            healthy = [dict(r, declared_operation_id=r['operation_id']) for r in rows if r['phase'] == 'class_train']
            self.database_model = learn_database_effects(self.store.request_traces(healthy), healthy,
                                                         endpoint_inventory(self.ctx.deployment_dir))
            path = self.ctx.out/'database'/'model.json'
            write_json(path, self.database_model)
            self.remember(path)
            # Freeze operation templates before DB-up/down traffic; post-hoc
            # evaluation only binds template values to actual attempt identities.
            templates = [{'attempt_key': name, 'declared_operation_id': name} for name in names]
            path = self.ctx.out/'database'/'predictions.json'
            write_json(path, {str(up): predict_database_effects(self.database_model, templates, up) for up in (True, False)})
            self.remember(path)
        write_json(self.ctx.out/'forecast-saved.json', {'saved_ns': time.time_ns(), 'sha256_by_path': self.frozen,
                                                      'fit_and_discovery_seconds': time.perf_counter()-started})

    def finish_projection(self):
        binder = self.binder()
        rows = declared_census(self.records)
        write_json(self.ctx.out/'http-observation-curves.json', http_curves(self.records, self.http_cap))
        write_json(self.ctx.out/'declared-journal-final.json', rows)
        projections = binder.project(rows, transport_observations(self.records))
        for source, projected in projections.items():
            write_json(self.ctx.out/'projections'/f'{source}-final.json', projected)
        if self.qualification:
            self.qualification_evidence(projections)
            return
        automatic_metrics = {}
        labels = {opaque_attempt(r): r['operation'] for r in self.records}
        for source in ('ebpf', 'native', 'combined'):
            automatic_metrics[source] = {}
            for variant, classes in self.automatic_classes[source].items():
                _, assigned = binder.automatic(automatic_census(self.records, self.census), source, classes, downstream=variant != 'route')
                write_json(self.ctx.out/'automatic'/source/variant/'final-assignments.json', assigned)
                metrics = {}
                for phase in ('calibration', 'target', 'class_test'):
                    population = [r for r in assigned if r['phase'] == phase]
                    covered = [r for r in population if r['class_id'] is not None]
                    metrics[phase] = {'total': len(population), 'covered': len(covered),
                        'unknown_fraction': 1-len(covered)/len(population) if population else None,
                        'ari_on_covered': ari([labels[r['attempt_key']] for r in covered], [r['class_id'] for r in covered])}
                automatic_metrics[source][variant] = metrics
        write_json(self.ctx.out/'automatic-metrics.json', automatic_metrics)
        self.controls(rows)
        for relative, before in self.frozen.items():
            if digest(self.ctx.out/relative) != before:
                raise RuntimeError(f'Frozen prediction changed: {relative}')
        write_json(self.ctx.out/'freeze-integrity.json', {'all_unchanged': True, 'sha256_by_path': self.frozen})

    def controls(self, rows):
        database = {}
        for phase in ('db_up', 'db_down'):
            population = [r for r in self.records if r['phase'] == phase]
            database[phase] = {operation: external_rate([r for r in population if r['operation'] == operation])
                               for operation in self.metadata['operations']}
        if self.database_model is not None:
            from systems.petclinic.database_v3 import predict_database_effects
            predictions = []
            for up, phase in ((True, 'db_up'), (False, 'db_down')):
                declared = [dict(r, declared_operation_id=r['operation_id']) for r in rows if r['phase'] == phase]
                predictions.extend(predict_database_effects(self.database_model, declared, up))
            write_json(self.ctx.out/'database'/'attempt-predictions.json', predictions)
            database['interpretation'] = ('DB-caused failure is a one-sided prediction of external failure. '
                'DB-up/absent dependency never implies business success. Compare down-state supported failure '
                'predictions with external outcomes; paired up/down rates are descriptive, not individual causal labels.')
        write_json(self.ctx.out/'database-controls.json', database)
        if self.system == 'otel_demo':
            controls = [r for r in rows if r['phase'].startswith('async_')]
            # Exact anchor traces and all traces linking to them. Retain every
            # conflicting variant. No time/topic proximity or oracle IDs select events.
            selected = self.store.request_traces(controls, linked_consumers=True)
            chains = message_chains(selected)
            write_json(self.ctx.out/'async-chains.json', chains)
            write_json(self.ctx.out/'async-selection.json', {
                'rule': 'all source-local traces with an actual control request header, plus all exact span-linked traces',
                'control_attempts': len(controls), 'selected_spans': len(selected),
                'raw_observations_retained_in_full': True})

    def qualification_evidence(self, projections):
        raw_bytes = sum(p.stat().st_size for folder in ('observations', 'native')
                        for p in (self.ctx.out/folder).rglob('*') if p.is_file())
        index_bytes = self.store.path.stat().st_size
        free = shutil.disk_usage(self.ctx.out).free
        projected = (raw_bytes+index_bytes)*34800/max(len(self.records), 1)*2
        summary = {'kind': 'technical_qualification_not_scientific_campaign', 'attempts': len(self.records),
                   'requested_operations_per_second': self.rate, 'raw_bytes': raw_bytes, 'index_bytes': index_bytes,
                   'disk_free_bytes': free, 'projected_full_capture_and_index_bytes_with_2x_margin': projected,
                   'disk_projection_fits': projected < free, 'source_summary': {},
                   'no_accuracy_success_gate': True, 'memory_and_scheduling_evidence': 'infrastructure/ and blocks.json'}
        summary.update(observation_policy=self.ctx.observation_policy,
                       application_deadline_seconds=None, http_observation_cap_seconds=self.http_cap,
                       peak_in_flight_attempts=max(b['peak_in_flight_attempts'] for b in self.blocks))
        for source, projected_rows in projections.items():
            summary['source_summary'][source] = {
                'outcomes': dict(Counter(str(r['proxy']) for r in projected_rows)),
                'body_reasons': dict(Counter(r.get('body_evidence', {}).get('reason', 'not_applicable') for r in projected_rows))}
        # Independent byte captures check the response-length assumption for
        # qualification only; no copied body enters source-only fitting.
        external = transport_observations(self.records)
        fidelity = {}
        for source in ('ebpf', 'native'):
            compared, equal = 0, 0
            for row in projections[source]:
                evidence = row.get('body_evidence', {})
                actual = external.get(row['attempt_key'], [])
                if evidence.get('sha256') and actual and actual[-1]['body'] is not None:
                    compared += 1
                    equal += evidence['sha256'] == hashlib.sha256(actual[-1]['body'].encode()).hexdigest()
            fidelity[source] = {'compared': compared, 'exact_body_matches': equal,
                                'mismatches': compared-equal, 'unsupported_without_body_evidence': compared == 0}
        summary['independent_body_fidelity'] = fidelity
        write_json(self.ctx.out/'qualification.json', summary)
        if not summary['disk_projection_fits']:
            raise RuntimeError('Projected full capture exceeds available disk; no automatic resource escalation')

    def run(self):
        status = {'system': self.system, 'mode': self.ctx.mode, 'seed': self.ctx.seed,
                  'protocol_version': 'source-contract-v3', 'qualification': self.qualification,
                  'observation_policy': self.ctx.observation_policy,
                  'http_observation_cap_seconds': self.http_cap, 'application_deadline_seconds': None,
                  'run_id': os.environ.get('GITHUB_RUN_ID'), 'commit': os.environ.get('GITHUB_SHA'),
                  'started_ns': time.time_ns(), 'status': 'running', 'requested_operations_per_second': self.rate}
        write_json(self.ctx.out/'status.json', status)
        try:
            self.adapter.prepare()
            self.collectors.start()
            self.adapter.deploy()
            self.adapter.ready()
            self.collectors.settle()
            self.metadata = self.adapter.metadata()
            write_json(self.ctx.out/'deployment.json', self.metadata)
            names = self.metadata['operations']
            if self.qualification:
                self.block('qualification', '11', 1200, names)
                self.snapshot('qualification')
            else:
                self.block('class_train', '11', 600, names)
                states = ['11', '10', '01', '00']
                self.rng.shuffle(states)
                for state in states:
                    self.block('calibration', state, 6000, names)
                self.snapshot('calibration')
                self.freeze(names)
                states = ['11']*4+['10']*2+['01', '00']
                self.rng.shuffle(states)
                for state in states:
                    self.block('target', state, 1200, names)
                self.block('class_test', '11', 600, names)
                for up in (True, False):
                    self.adapter.reset()
                    self.adapter.set_database(up)
                    self.block('db_up' if up else 'db_down', '11', 20, names, reset=False)
                self.adapter.reset()
                if self.system == 'otel_demo':
                    self.block('async_normal', '11', 20, ['checkout'], asynchronous=True)
                    self.adapter.set_consumer(False)
                    self.block('async_paused', '11', 20, ['checkout'], reset=False, asynchronous=True)
                    self.adapter.set_consumer(True)
                    self.block('async_recovered', '11', 20, ['checkout'], reset=False, asynchronous=True)
                self.snapshot('final')
                if sum(b['attempts'] for b in self.blocks if b['phase'] in PRIMARY_PHASES) != 34800:
                    raise RuntimeError('Unexpected primary campaign size')
                write_json(self.ctx.out/'acquisition-complete.json', {
                    'completed_ns': time.time_ns(), 'status': 'raw_acquisition_complete',
                    'commit': status['commit'], 'primary_attempts': 34800,
                    'all_attempts': len(self.records), 'frozen_predictions': self.frozen,
                    'index_snapshot': 'index-final.json',
                    'index_sha256': digest(self.store.path),
                    'rule_sha256': {name: digest(self.ctx.repo_dir/name) for name in RULE_FILES+
                        [f'systems/{self.system}/contracts_v3.py']+
                        (['systems/petclinic/database_v3.py', 'systems/petclinic/adapter.py'] if self.system == 'petclinic' else [])},
                    'fixture_sha256': digest(self.ctx.deployment_dir/'petclinic'/'fixture.json')
                        if self.system == 'petclinic' else None,
                    'external_sha256': digest(self.ctx.out/'external.json')})
                status['status'] = 'analysis_pending'
                write_json(self.ctx.out/'status.json', status)
            self.finish_projection()
            status['status'] = 'qualification_complete' if self.qualification else 'acquisition_complete'
        except Exception as exc:
            status.update(status='technical_failure', error=str(exc), traceback=traceback.format_exc())
            raise
        finally:
            for name, action in [('collectors', self.collectors.close), ('application', self.adapter.close),
                                 ('index', self.store.close)]:
                try:
                    action()
                except Exception as exc:
                    status[name+'_close_error'] = str(exc)
            status.update(ended_ns=time.time_ns(), attempted_operations=len(self.records),
                          preparation_operations=len(self.warmups))
            status['elapsed_seconds'] = (status['ended_ns']-status['started_ns'])/1e9
            write_json(self.ctx.out/'status.json', status)
            self.save_records()

    def resume_analysis(self):
        """Recover complete captures without generating traffic or refitting."""
        out = self.ctx.out
        marker = json.loads((out/'acquisition-complete.json').read_text())
        status = json.loads((out/'status.json').read_text())
        if marker['external_sha256'] != digest(out/'external.json'):
            raise RuntimeError('Sealed external population changed')
        if marker['index_sha256'] != digest(self.store.path):
            raise RuntimeError('Sealed observation index changed')
        for relative, before in marker['rule_sha256'].items():
            if digest(self.ctx.repo_dir/relative) != before:
                raise RuntimeError(f'Recovery must use original source rules: {relative}')
        if self.system == 'petclinic' and marker['fixture_sha256'] != digest(
                self.ctx.deployment_dir/'petclinic'/'fixture.json'):
            raise RuntimeError('Sealed Petclinic semantic fixture changed')
        if (status['system'], status['mode'], status['seed']) != (self.system, self.ctx.mode, self.ctx.seed):
            raise RuntimeError('Resume arguments do not match retained population')
        for attr, filename in (('records', 'external.json'), ('census', 'census.json'),
                               ('blocks', 'blocks.json'), ('warmups', 'preparation-operations.json'),
                               ('metadata', 'deployment.json')):
            setattr(self, attr, json.loads((out/filename).read_text()))
        self.frozen = marker['frozen_predictions']
        for relative, before in self.frozen.items():
            if digest(out/relative) != before:
                raise RuntimeError(f'Sealed prediction changed: {relative}')
        for source in ('ebpf', 'native', 'combined'):
            self.automatic_classes[source] = {variant: json.loads(
                (out/'automatic'/source/variant/'classes.json').read_text())
                for variant in ('route', 'route_and_downstream')}
        if self.system == 'petclinic':
            self.database_model = json.loads((out/'database'/'model.json').read_text())
        started = time.time_ns()
        try:
            self.finish_projection()
            status['status'] = 'acquisition_complete'
        finally:
            status.setdefault('analysis_recoveries', []).append({
                'started_ns': started, 'ended_ns': time.time_ns(), 'commit': os.environ.get('GITHUB_SHA'),
                'acquisition_marker_sha256': digest(out/'acquisition-complete.json')})
            write_json(out/'status.json', status)
            self.store.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--system', required=True, choices=['deathstarbench', 'otel_demo', 'petclinic'])
    p.add_argument('--mode', required=True, choices=['absent', 'partial', 'full'])
    p.add_argument('--seed', type=int, required=True, choices=[3, 4, 5])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--qualification', action='store_true')
    p.add_argument('--resume-analysis', action='store_true')
    args = p.parse_args()
    if args.qualification and args.resume_analysis:
        p.error('Qualification and analysis recovery are distinct operations')
    campaign = CampaignV3(args.system, args.mode, args.seed, args.out, args.qualification)
    campaign.resume_analysis() if args.resume_analysis else campaign.run()


if __name__ == '__main__':
    main()
