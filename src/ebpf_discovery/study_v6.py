"""Fresh training, offline forecast freeze, and independent deployment validation.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import sqlite3
import shutil
import threading
import time
import traceback
from types import SimpleNamespace

from .classes_v5 import fit as fit_classes
from .collectors_v6 import make_collectors, certify_controls
from .plan_v6 import COLLECTORS, MODES, REPETITIONS, SYSTEMS, STUDY, random_stream
from .runtime import Context, write_json
from .study import Study as Workload, workload_counts
from .toolchain_v4 import digest
from .transport_v4 import Journal


BERING_CHILD_GO_ENV = {'GOGC': '25'}


def declaration(system):
    version = 'experiment_v5' if system == 'otel_demo' else 'experiment_v4'
    return importlib.import_module(f'systems.{system}.{version}')


def file_hashes(root, paths):
    return {p.relative_to(root).as_posix(): digest(p)
            for folder in paths for p in (root / folder).rglob('*') if p.is_file()}


def verify_files(root, hashes):
    for name, expected in hashes.items():
        p = (root / name).resolve()
        if not p.is_relative_to(root.resolve()) or not p.is_file() or digest(p) != expected:
            raise ValueError('frozen evidence changed: ' + name)


def portable_outputs(root, complete):
    """Freeze executable outputs separately from retained large replay inputs."""
    return {name: sha for name, sha in complete.items()
            if not name.startswith('toolchain/inputs/')}


class Case:
    # Only the reviewed workload mechanics are shared, not phase orchestration.
    block = Workload.block
    issue = Workload.issue
    state_barrier = Workload.state_barrier
    before_workload_block = Workload.before_workload_block
    after_workload_block = Workload.after_workload_block
    require_completed_transports = Workload.require_completed_transports
    verify_async_until_terminal = Workload.verify_async_until_terminal
    async_pending = staticmethod(Workload.async_pending)
    save_records = Workload.save_records

    def __init__(self, root, system, mode, repetition, collector, phase, *,
                 smoke=False, stage='qualification', vm_dir=Path('work/vms/current')):
        random_stream(system, mode, repetition, 'validate-fixed-cell')
        if collector not in COLLECTORS or phase not in ('training', 'validation'):
            raise ValueError('invalid v6 runtime condition')
        if stage not in ('qualification', 'main') or (stage == 'main' and smoke):
            raise ValueError('invalid qualification/main workload identity')
        if Path(root).exists() and any(Path(root).iterdir()):
            raise ValueError('a fresh capture directory must be empty')
        self.system, self.collector, self.smoke = system, collector, smoke
        self.phase = phase
        self.ctx = Context(Path(root), mode, repetition, vm_dir=vm_dir)
        self.ctx.collector = collector
        self.ctx.observation_policy = 'uncapped-v5'
        self.ctx.journal = Journal(self.ctx.out / 'attempt-journal.sqlite')
        self.declaration = declaration(system)
        self.collectors = make_collectors(self.ctx, collector)
        self.records, self.census, self.blocks, self.warmups, self.plans = [], [], [], [], []
        self.index, self.metadata = 0, {}
        self.rate, self.workers = 20, 256
        self.record_lock = threading.Lock()
        self.rng = random_stream(system, mode, repetition, phase + '-workload')
        self._application_close_attempted = False
        self.status = {'study': STUDY, 'protocol_version': 'graph-v5',
                       'system': system, 'mode': mode, 'seed': repetition,
                       'collector': collector, 'phase': phase, 'smoke': smoke, 'stage': stage,
                       'run_id': os.environ.get('GITHUB_RUN_ID'),
                       'commit': os.environ.get('GITHUB_SHA'),
                       'runner_boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                       'started_ns': time.time_ns(), 'status': 'preparation'}
        write_json(self.ctx.out / 'status.json', self.status)

    def close_application(self):
        if not self._application_close_attempted and hasattr(self, 'adapter'):
            self._application_close_attempted = True
            self.adapter.close()

    def _workload(self):
        counts = workload_counts(len(self.declaration.CONTRACTS), self.smoke)
        names = list(self.declaration.CONTRACTS)
        if self.phase == 'training':
            self.block('class_train', '11', counts['class_train'], names)
            states = ['11', '10', '01', '00']
            self.rng.shuffle(states)
            for state in states:
                self.block('calibration', state, counts['calibration'], names)
            return
        states = ['11'] * 4 + ['10'] * 2 + ['01', '00']
        self.rng.shuffle(states)
        for state in states:
            self.block('target', state, counts['target'], names)
        self.block('class_test', '11', counts['class_test'], names)
        for up in (True, False):
            self.adapter.reset()
            self.adapter.set_database(up)
            self.block('db_up' if up else 'db_down', '11', counts['database'], names, reset=False)
        self.adapter.reset()
        if self.system == 'otel_demo':
            normal = self.block('async_normal', '11', counts['async'], ['checkout'], reset=False)
            self.verify_async_until_terminal(normal, 'async-normal-persistence')
            self.adapter.set_consumer(False)
            paused = self.block('async_paused', '11', counts['async'], ['checkout'], reset=False)
            observed = self.adapter.observe_async(paused)
            self.ctx.journal.append('async_paused_snapshot', records=observed)
            write_json(self.ctx.out / 'async-paused-snapshot.json', observed)
            self.adapter.set_consumer(True)
            self.verify_async_until_terminal(paused, 'async-paused-after-resume')
            recovered = self.block('async_recovered', '11', counts['async'], ['checkout'], reset=False)
            self.verify_async_until_terminal(recovered, 'async-recovered-persistence')

    def capture(self, blueprint, blueprint_sha256):
        from .deployment_v6 import deploy_blueprint
        failure = None
        try:
            self.collectors.start()
            self.status['blueprint_sha256'] = blueprint_sha256
            self.adapter = deploy_blueprint(self.ctx, self.system, Path(blueprint),
                                            expected_sha256=blueprint_sha256)
            self.adapter.ready()
            self.collectors.settle()
            certify_controls(self.collectors)
            self.metadata = self.adapter.metadata()
            write_json(self.ctx.out / 'deployment.json', self.metadata)
            self._workload()
            self.require_completed_transports()
            self.collectors.final_drain()
            self.adapter.collect_native(self.ctx.out / 'native' / self.phase)
            self.status['status'] = 'capture_complete'
        except BaseException as error:
            failure = error
            self.status.update(status='technical_failure', error=repr(error), traceback=traceback.format_exc())
        finally:
            cleanup_errors = []
            for name, action in [('collectors', self.collectors.close),
                                 ('application', self.close_application)]:
                try:
                    action()
                except Exception as error:
                    cleanup_errors.append({'component': name, 'error': repr(error)})
            self.status.update(ended_ns=time.time_ns(), cleanup_errors=cleanup_errors)
            if cleanup_errors:
                self.status['status'] = 'technical_failure'
            self.save_records()
            write_json(self.ctx.out / 'plans.json', self.plans)
            self.ctx.journal.export(self.ctx.out / 'attempt-journal.jsonl')
            self.ctx.journal.close()
            write_json(self.ctx.out / 'status.json', self.status)
        if failure is not None:
            raise failure
        if cleanup_errors:
            raise RuntimeError('capture cleanup failed')
        closed = file_hashes(self.ctx.out, ('observations', 'native', 'runtime-identity-v5'))
        shutil.copyfile(self.ctx.command_log, self.ctx.out / 'capture-commands.jsonl')
        for name in ('plans.json', 'external.json', 'census.json', 'blocks.json',
                     'deployment.json', 'status.json', 'attempt-journal.sqlite', 'capture-commands.jsonl'):
            closed[name] = digest(self.ctx.out / name)
        receipt = self.ctx.out / 'block-freeze-verified-before-capture.json'
        if receipt.exists():
            closed[receipt.name] = digest(receipt)
        for name in ('async-normal-persistence.json', 'async-paused-snapshot.json',
                     'async-paused-after-resume.json', 'async-recovered-persistence.json'):
            if (self.ctx.out / name).exists():
                closed[name] = digest(self.ctx.out / name)
        write_json(self.ctx.out / 'closed-input.json', {
            'study': STUDY, 'phase': self.phase, 'closed_ns': time.time_ns(),
            'status': self.status, 'files': closed,
            'scope': 'Closed input, no discovery/forecast/target leakage between epochs'})


def model(root):
    """Run only after training guests have stopped; never observes validation."""
    from .identity_projection_v5 import refresh
    from .store_v5 import ObservationStoreV5
    from .toolchain_v5 import Toolchain
    from .bering_v4 import child_go_environment
    from .resources_v6 import MODEL_SWAP_BYTES, prepare_model_swap
    root = Path(root).resolve()
    if (root / 'forecast-saved.json').exists():
        raise ValueError('a frozen model must not be recomputed')
    from .block_v6 import processing_publication_preflight
    processing_publication_preflight(root)
    processing = {'run_id': os.environ['GITHUB_RUN_ID'], 'commit': os.environ['GITHUB_SHA'],
                  'runner_boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                  'started_ns': time.time_ns(),
                  'bering_child_go_environment': dict(BERING_CHILD_GO_ENV),
                  'additional_model_swap_file_bytes': MODEL_SWAP_BYTES,
                  'scope': 'Actual offline processing execution; original capture identity remains unchanged'}
    write_json(root / 'processing-execution.json', processing)
    from .resources_v6 import prepare
    prepare(root / 'model-worker-resources.json')
    prepare_model_swap(root / 'model-swap-resources.json')
    from .capture_checks_v6 import verify_capture
    closed = verify_capture(root, 'training')
    status = closed['status']
    if status['phase'] != 'training' or status['status'] != 'capture_complete':
        raise ValueError('models require a complete fresh training capture')
    verify_files(root, closed['files'])
    expected_runtime = {n for n in closed['files'] if n.startswith('runtime-identity-v5/')}
    actual_runtime = {p.relative_to(root).as_posix() for p in (root / 'runtime-identity-v5').rglob('*') if p.is_file()}
    if actual_runtime != expected_runtime:
        raise ValueError('unmanifested runtime evidence before model construction')
    ctx = Context(root, status['mode'], status['seed'])
    ctx.collector = status['collector']
    # Read the exact closed journal without turning model work into capture.
    connection = sqlite3.connect((root / 'attempt-journal.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)
    ctx.journal = SimpleNamespace(db=connection, lock=threading.Lock(), path=root / 'attempt-journal.sqlite')
    store = ObservationStoreV5(root / 'observation-index.sqlite', same_trace_parents=True)
    plans = json.loads((root / 'plans.json').read_text(encoding='utf8'))
    case = SimpleNamespace(ctx=ctx, store=store, plans=plans, collector=status['collector'])
    declared = declaration(status['system'])
    try:
        write_json(root / 'index-training.json', store.ingest(root / 'observations', root / 'native'))
        from .evaluate_v5 import acquisition_checks
        acquisition = acquisition_checks(root, status, declared, agent_expected=status['collector'] != 'none')
        write_json(root / 'training-acquisition-checks.json', acquisition)
        if not acquisition['valid']:
            raise ValueError('training acquisition invalid: ' + ','.join(acquisition['problems']))
        if status['collector'] == 'none':
            count = store.db.execute("SELECT COUNT(*) FROM spans WHERE source LIKE 'ebpf-%'").fetchone()[0]
            if count:
                raise ValueError('unexpected eBPF observations in the actual no-agent arm')
        refresh(case, 'training')
        # Collect unreachable Bering allocations earlier without limiting the live
        # heap, input, processor count or scientific calculation. Apply to all arms.
        with child_go_environment(BERING_CHILD_GO_ENV):
            Toolchain(ctx, status['system'], store, declared).forecast(plans)
        fit_classes(store, plans, declared, root / 'toolchain' / 'classes')
        from .evaluate_v4 import _manual_baselines
        write_json(root / 'toolchain' / 'manual-baselines.json',
                   _manual_baselines(status['system'], list(declared.CONTRACTS)))
        complete_processing = file_hashes(root, ('toolchain',))
        frozen = portable_outputs(root, complete_processing)
        frozen['processing-execution.json'] = digest(root / 'processing-execution.json')
        frozen['model-swap-resources.json'] = digest(root / 'model-swap-resources.json')
        for name in ('supplied-service-aliases-training.json',
                     'supplied-service-alias-admission-training.json'):
            relative = 'runtime-identity-v5/' + name
            frozen[relative] = digest(root / relative)
        verify_files(root, closed['files'])
        write_json(root / 'forecast-saved.json', {
            'study': STUDY, 'saved_ns': time.time_ns(), 'case': status,
            'processing_execution': processing,
            'training_closed_input_sha256': digest(root / 'closed-input.json'),
            'sha256_by_path': frozen, 'uses_actual_graph_simulator': True,
            'complete_processing_sha256_by_path': complete_processing,
            'complete_processing_retention': 'separate full processing artifact; replay inputs are not discarded',
            'validation_started': False})
    finally:
        store.close()
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('training', 'model', 'validation'))
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--system', choices=SYSTEMS)
    parser.add_argument('--mode', choices=MODES)
    parser.add_argument('--repetition', type=int, choices=REPETITIONS)
    parser.add_argument('--collector', choices=COLLECTORS)
    parser.add_argument('--blueprint', type=Path)
    parser.add_argument('--blueprint-sha256')
    parser.add_argument('--vms', type=Path, default=Path('work/vms/current'))
    parser.add_argument('--frozen', type=Path)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--stage', choices=('qualification', 'main'), default='qualification')
    args = parser.parse_args()
    if args.phase == 'model':
        model(args.root)
        return
    if not all((args.system, args.mode, args.repetition, args.collector,
                args.blueprint, args.blueprint_sha256)):
        parser.error('capture requires the explicit fresh cell and frozen blueprint')
    if args.phase == 'validation':
        if args.frozen is None:
            parser.error('validation requires a previously frozen model bundle')
        from .validation_v6 import require_forecast, require_block_freeze
        require_forecast(args.frozen, args.system, args.mode, args.repetition, args.collector,
                         smoke=args.smoke, stage=args.stage)
        block_freeze = require_block_freeze([args.frozen.parent / c for c in COLLECTORS])
        if any(s['case'].get('blueprint_sha256') != args.blueprint_sha256
               for s in block_freeze['models']):
            raise ValueError('validation blueprint differs from the four frozen training arms')
    case = Case(args.root, args.system, args.mode, args.repetition, args.collector,
                args.phase, smoke=args.smoke, stage=args.stage, vm_dir=args.vms)
    if args.phase == 'validation':
        write_json(case.ctx.out / 'block-freeze-verified-before-capture.json', block_freeze)
    case.capture(args.blueprint, args.blueprint_sha256)


if __name__ == '__main__':
    main()
