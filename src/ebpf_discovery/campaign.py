"""Fixed experiment schedule; all real execution is guarded by Context (Actions)."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib
import json
import os
from pathlib import Path
import random
import socket
import time
import traceback

from .collectors import Collectors
from .model import fit
from .observations import census, read_spans
from .runtime import Context, write_json
from .evaluate import evaluation_map


class Campaign:
    def __init__(self, system, mode, seed, out):
        self.ctx = Context(out, mode, seed)
        self.system = system
        self.adapter = importlib.import_module(f'systems.{system}.adapter').Adapter(self.ctx)
        self.collectors = Collectors(self.ctx)
        self.rng = random.Random(seed)
        self.records, self.census, self.blocks, self.warmups = [], [], [], []
        self.index = 0
        self.metadata = {}

    def save_records(self):
        write_json(self.ctx.out / 'external.json', self.records)
        write_json(self.ctx.out / 'census.json', self.census)
        write_json(self.ctx.out / 'blocks.json', self.blocks)
        write_json(self.ctx.out / 'preparation-operations.json', self.warmups)

    def block(self, phase, state, count, names, *, reset=True, asynchronous=False):
        block_id = f'{phase}-{len(self.blocks):02d}'
        block_start = time.time_ns()
        if reset:
            self.adapter.reset()
            self.adapter.set_replicas(state)
        state_evidence = self.state_barrier(state)
        # Fixed preparation, never repeated until success. This clears a first
        # stale connection after a replica restart without selecting scored data.
        warm = []
        for name in names:
            row = self.adapter.operation(name, self.index, f'warmup-{block_id}', 2.0)
            self.index += 1
            row.update(phase='preparation', state=state, for_block=block_id)
            if self.system == 'otel_demo' and name == 'checkout':
                row = self.adapter.verify_async([row], 10.0)[0]
            warm.append(row)
        self.warmups.extend(self.adapter.verify(warm))
        time.sleep(10)
        ordered = [names[i % len(names)] for i in range(count)]
        self.rng.shuffle(ordered)
        futures = []
        start_mono = time.monotonic()
        start_ns = time.time_ns()

        def issue(name, index, scheduled):
            actual = time.time_ns()
            row = self.adapter.operation(name, index, block_id, 2.0)
            row.update(phase=phase, state=state, block_id=block_id, scheduled_ns=scheduled,
                       dispatch_lateness_seconds=max(0, (actual-scheduled)/1e9))
            if asynchronous or (self.system == 'otel_demo' and name == 'checkout'):
                row = self.adapter.verify_async([row], 10.0)[0]
            return row

        with ThreadPoolExecutor(max_workers=48) as pool:
            for offset, name in enumerate(ordered):
                remaining = start_mono + offset/4 - time.monotonic()
                if remaining > 0:
                    time.sleep(remaining)
                futures.append(pool.submit(issue, name, self.index, start_ns+int(offset/4*1e9)))
                self.index += 1
            rows = [f.result() for f in futures]
        # Independent verification happens while the intervention is still in
        # force, before reset can turn a failed operation into an apparent success.
        rows = self.adapter.verify(rows)
        # Fixed drain guard, not a proof of completion of arbitrary background
        # work. It occurs before any subsequent intervention or reset.
        time.sleep(10)
        self.records.extend(rows)
        self.census.extend(census(rows, phase, state))
        block = {'id': block_id, 'phase': phase, 'state': state, 'attempts': count,
                 'started_ns': block_start, 'load_started_ns': start_ns, 'ended_ns': time.time_ns(),
                 'nominal_load_seconds': count/4, 'preparation_operations': len(warm), 'fixed_settle_seconds': 10,
                 'fixed_drain_seconds': 10, 'max_dispatch_lateness_seconds': max(r['dispatch_lateness_seconds'] for r in rows)}
        block['state_evidence'] = state_evidence
        self.blocks.append(block)
        self.save_records()
        print(json.dumps(block), flush=True)

    def state_barrier(self, state):
        until = time.monotonic()+120
        evidence = []
        port = {'deathstarbench': 9090, 'petclinic': 8080, 'otel_demo': 3550}[self.system]
        while time.monotonic() < until:
            sample = []
            for replica, bit in zip(self.metadata['replicas'], state):
                try:
                    with socket.create_connection((replica.get('transport_host', replica['ip']), replica.get('transport_port', replica.get('port', port))), timeout=1):
                        accepting = True
                except OSError:
                    accepting = False
                sample.append({'name': replica['name'], 'node': replica['node'], 'ip': replica['ip'],
                               'tcp_accepting': accepting, 'expected_up': bit == '1', 'checked_ns': time.time_ns()})
            evidence.append(sample)
            if all(r['tcp_accepting'] == r['expected_up'] for r in sample):
                # Both routers use 1s checks and two consecutive results. Give
                # their independent checks a fixed five-second convergence gap.
                time.sleep(5)
                if len(evidence) >= 2 and all(r['tcp_accepting'] == r['expected_up'] for r in evidence[-2]):
                    return {'method': 'two TCP state censuses separated by 5s router settling', 'samples': evidence}
            else:
                time.sleep(1)
        write_json(self.ctx.out/'failed-state-barrier.json', {'state': state, 'evidence': evidence})
        raise RuntimeError(f'Replica state {state} did not converge within 120s')

    def snapshot(self, stage):
        self.collectors.snapshot()
        native = self.ctx.out / 'native' / stage
        self.adapter.collect_native(native)
        # Exporters may start a new file after restart. Include every immutable
        # native snapshot; read_spans deduplicates cumulative exports by IDs.
        spans, errors = read_spans(self.collectors.root, native.parent)
        write_json(self.ctx.out / f'normalized-{stage}.json', spans)
        write_json(self.ctx.out / f'parse-errors-{stage}.json', errors)
        if errors:
            raise RuntimeError('Raw observation parsing failed; retain inputs and repair before scientific use')
        return spans

    def run(self):
        status = {'system': self.system, 'mode': self.ctx.mode, 'seed': self.ctx.seed,
                  'protocol_version': 'fixed-warmup-v2',
                  'run_id': os.environ.get('GITHUB_RUN_ID'), 'commit': os.environ.get('GITHUB_SHA'),
                  'started_ns': time.time_ns(), 'status': 'running'}
        write_json(self.ctx.out / 'status.json', status)
        try:
            self.adapter.prepare()
            self.collectors.start()
            self.adapter.deploy()
            self.adapter.ready()
            self.collectors.settle()
            self.metadata = self.adapter.metadata()
            write_json(self.ctx.out / 'deployment.json', self.metadata)
            names = self.metadata['operations']
            self.block('class_train', '11', 120, names)
            states = ['11', '10', '01', '00']
            self.rng.shuffle(states)
            for state in states:
                self.block('calibration', state, 240, names)
            spans = self.snapshot('calibration')
            forecasts, models, mappings = {}, {}, {}
            for source in ('ebpf', 'native', 'combined'):
                data = spans if source == 'combined' else [s for s in spans if s['source'] == source]
                model, forecast, assignments = fit(data, self.census, self.ctx.seed)
                folder = self.ctx.out / 'models' / source
                write_json(folder / 'model.json', model)
                write_json(folder / 'forecast.json', forecast)
                write_json(folder / 'calibration-assignments.json', assignments)
                write_json(folder / 'evaluation-map.json', evaluation_map(self.records, assignments))
                forecasts[source] = hashlib.sha256((folder / 'forecast.json').read_bytes()).hexdigest()
                models[source] = hashlib.sha256((folder / 'model.json').read_bytes()).hexdigest()
                mappings[source] = hashlib.sha256((folder / 'evaluation-map.json').read_bytes()).hexdigest()
            # This file is written before any target dispatch; both timestamps
            # and hashes are retained, including in failed campaigns.
            write_json(self.ctx.out / 'forecast-saved.json', {'saved_ns': time.time_ns(), 'sha256': forecasts,
                        'model_sha256': models, 'evaluation_map_sha256': mappings})
            target_states = ['11']*4 + ['10']*2 + ['01', '00']
            self.rng.shuffle(target_states)
            for state in target_states:
                self.block('target', state, 120, names)
            self.block('class_test', '11', 120, names)
            for up in (True, False):
                self.adapter.reset()
                self.adapter.set_database(up)
                self.block('db_up' if up else 'db_down', '11', 20, names, reset=False)
            self.adapter.reset()
            if self.system == 'otel_demo':
                self.block('async_normal', '11', 20, ['checkout'], asynchronous=True)
                self.adapter.set_consumer(False)
                self.block('async_paused', '11', 20, ['checkout'], reset=False, asynchronous=True)
                self.adapter.set_consumer(True)  # waits for deadlines and queue drain
                self.block('async_recovered', '11', 20, ['checkout'], reset=False, asynchronous=True)
            self.snapshot('final')
            assert sum(b['attempts'] for b in self.blocks if b['phase'] in ('class_train', 'calibration', 'target', 'class_test')) == 2160
            status['status'] = 'acquisition_complete'
        except Exception as exc:
            status.update(status='technical_failure', error=str(exc), traceback=traceback.format_exc())
            raise
        finally:
            for name, action in [('collectors', self.collectors.close), ('application', self.adapter.close)]:
                try:
                    action()
                except Exception as exc:
                    status[name+'_close_error'] = str(exc)
            status.update(ended_ns=time.time_ns(), attempted_operations=len(self.records), preparation_operations=len(self.warmups))
            status['elapsed_seconds'] = (status['ended_ns']-status['started_ns'])/1e9
            write_json(self.ctx.out / 'status.json', status)
            self.save_records()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--system', required=True, choices=['deathstarbench', 'otel_demo', 'petclinic'])
    p.add_argument('--mode', required=True, choices=['absent', 'partial', 'full'])
    p.add_argument('--seed', type=int, required=True, choices=[0, 1, 2])
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    Campaign(a.system, a.mode, a.seed, a.out).run()


if __name__ == '__main__':
    main()
