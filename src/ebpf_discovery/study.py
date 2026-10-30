"""One explicit controller for the matched three-collector study.

Acquisition and product components retain their existing, reviewed interfaces.
No historical Campaign class participates in initialization or phase control.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib
import json
import os
from pathlib import Path
import random
import socket
import threading
import time
import traceback

from .classes_v5 import evaluate as evaluate_classes, fit as fit_classes
from .collectors_v5 import make_collectors
from .evidence_v4 import evaluate as evaluate_evidence
from .observations import census as intent_census
from .runtime import Context, write_json
from .store_v5 import ObservationStoreV5
from .toolchain_v4 import digest
from .toolchain_v5 import Toolchain
from .transport_v4 import Journal


SYSTEMS = ("deathstarbench", "otel_demo", "petclinic")
MODES = ("absent", "partial", "full")
COLLECTORS = ("obi", "deepflow", "coroot")
CONTROLLER = "clean-study"


def workload_counts(operation_count, smoke):
    """The unchanged full study counts; smoke exercises every declared operation."""
    if operation_count <= 0:
        raise ValueError("a campaign must retain at least one operation")
    return ({"class_train": 3 * operation_count, "calibration": operation_count,
             "target": operation_count, "class_test": 3 * operation_count,
             "database": operation_count, "async": 1} if smoke else
            {"class_train": 600, "calibration": 6000, "target": 1200,
             "class_test": 600, "database": 20, "async": 20})


class Study:
    def __init__(self, system, mode, seed, out, *, collector, smoke=False,
                 training_checkpoint=None, toolchain_execution="local"):
        if system not in SYSTEMS or mode not in MODES or seed not in (6, 7, 8):
            raise ValueError("cell is outside the fixed study")
        if collector not in COLLECTORS:
            raise ValueError("unknown collector: " + str(collector))
        if smoke and seed != 6:
            raise ValueError("technical smokes use the predeclared seed 6")
        if toolchain_execution not in ("local", "worker"):
            raise ValueError("toolchain_execution must be local or worker")
        if toolchain_execution == "worker" and training_checkpoint is None:
            raise ValueError("worker execution requires a closed training checkpoint")

        self.ctx = Context(out, mode, seed)
        self.ctx.observation_policy = "uncapped-v5"
        self.ctx.collector = collector
        self.ctx.journal = Journal(self.ctx.out / "attempt-journal.sqlite")
        version = "experiment_v5" if system == "otel_demo" else "experiment_v4"
        self.declaration = importlib.import_module(f"systems.{system}.{version}")
        self.adapter = self.declaration.Adapter(self.ctx)
        self.collectors = make_collectors(self.ctx, collector)
        self.store = ObservationStoreV5(
            self.ctx.out / "observation-index.sqlite", same_trace_parents=True)

        self.system, self.collector, self.smoke = system, collector, smoke
        self.qualification = False
        self.rng = random.Random(seed)
        self.records, self.census, self.blocks, self.warmups, self.plans = [], [], [], [], []
        self.index, self.metadata = 0, {}
        self.rate, self.workers = 20, 256
        self.frozen = {}
        self.record_lock = threading.Lock()
        self.training_checkpoint = Path(training_checkpoint) if training_checkpoint else None
        self.training_release = None
        self.toolchain_execution = toolchain_execution

    def run(self):
        counts = workload_counts(len(self.declaration.CONTRACTS), self.smoke)
        status = dict(system=self.system, mode=self.ctx.mode, seed=self.ctx.seed,
                      collector=self.collector, smoke=self.smoke, controller=CONTROLLER, workload_counts=counts,
                      protocol_version="graph-v5", run_id=os.environ.get("GITHUB_RUN_ID"),
                      toolchain_execution=self.toolchain_execution,
                      commit=os.environ.get("GITHUB_SHA"), started_ns=time.time_ns(), status="running")
        write_json(self.ctx.out / "status.json", status)
        try:
            self.adapter.prepare()
            self.collectors.start()
            self.adapter.deploy()
            self.adapter.ready()
            self.collectors.settle()
            self.collectors.certify_controls()
            self.metadata = self.adapter.metadata()
            write_json(self.ctx.out / "deployment.json", self.metadata)
            names = list(self.declaration.CONTRACTS)
            self.block("class_train", "11", counts["class_train"], names)
            states = ["11", "10", "01", "00"]
            self.rng.shuffle(states)
            for state in states:
                self.block("calibration", state, counts["calibration"], names)
            self.snapshot("training")
            if self.training_checkpoint is not None:
                from .checkpoint_v4 import checkpoint_and_wait
                self.require_completed_transports()
                self.training_release = checkpoint_and_wait(self, self.training_checkpoint)
            self.freeze()
            states = ["11"] * 4 + ["10"] * 2 + ["01", "00"]
            self.rng.shuffle(states)
            for state in states:
                self.block("target", state, counts["target"], names)
            self.block("class_test", "11", counts["class_test"], names)
            for up in (True, False):
                self.adapter.reset()
                self.adapter.set_database(up)
                self.block("db_up" if up else "db_down", "11", counts["database"], names, reset=False)
            self.adapter.reset()
            if self.system == "otel_demo":
                normal = self.block("async_normal", "11", counts["async"], ["checkout"], reset=False)
                self.verify_async_until_terminal(normal, "async-normal-persistence")
                self.adapter.set_consumer(False)
                paused = self.block("async_paused", "11", counts["async"], ["checkout"], reset=False)
                snapshot = self.adapter.observe_async(paused)
                self.ctx.journal.append("async_paused_snapshot", records=snapshot)
                write_json(self.ctx.out / "async-paused-snapshot.json", snapshot)
                self.adapter.set_consumer(True)
                self.verify_async_until_terminal(paused, "async-paused-after-resume")
                recovered = self.block("async_recovered", "11", counts["async"], ["checkout"], reset=False)
                self.verify_async_until_terminal(recovered, "async-recovered-persistence")
            self.collectors.final_drain()
            self.snapshot("final")
            evaluate_classes(self.store, self.plans, self.records, self.declaration,
                             self.ctx.out / "toolchain" / "classes" / "classes-family-model.json", self.ctx.out)
            evaluate_evidence(self.ctx, self.system, self.store, self.plans, self.records)
            for relative, original in self.frozen.items():
                if digest(self.ctx.out / relative) != original:
                    raise RuntimeError("Frozen discovery or prediction changed: " + relative)
            write_json(self.ctx.out / "freeze-integrity.json", {"all_unchanged": True,
                        "sha256_by_path": self.frozen})
            status["status"] = "smoke_complete" if self.smoke else "acquisition_complete"
        except BaseException as exc:
            status.update(status="technical_failure", error=repr(exc), traceback=traceback.format_exc())
            raise
        finally:
            cleanup_errors = []
            for name, action in [("collectors", self.collectors.close), ("application", self.adapter.close),
                                 ("index", self.store.close)]:
                try:
                    action()
                except Exception as exc:
                    status[name + "_close_error"] = repr(exc)
                    status["status"] = "technical_failure"
                    cleanup_errors.append(name + ": " + repr(exc))
            status.update(ended_ns=time.time_ns(), observed_operations=len(self.records))
            status["elapsed_seconds"] = (status["ended_ns"] - status["started_ns"]) / 1e9
            write_json(self.ctx.out / "status.json", status)
            self.save_records()
            self.ctx.journal.export(self.ctx.out / "attempt-journal.jsonl")
            self.ctx.journal.close()
            if cleanup_errors and "error" not in status:
                raise RuntimeError("Campaign cleanup failed: " + "; ".join(cleanup_errors))

    def block(self, phase, state, count, names, *, reset=True):
        self.require_completed_transports()
        block_id = f'{phase}-{len(self.blocks):02d}'
        started_ns = time.time_ns()
        self.ctx.journal.append('block_intent', block_id=block_id, phase=phase, state=state, count=count)
        if reset:
            self.adapter.reset()
            self.adapter.set_replicas(state)
        state_evidence = self.state_barrier(state)
        self.before_workload_block(block_id, phase, state)
        ordered = [names[i % len(names)] for i in range(count)]
        self.rng.shuffle(ordered)
        # Preparation requests use the same durable path but are not scored.
        # They are not repeated until success and remain explicit cost/evidence.
        for name in names:
            plan = self.adapter.plan_operation(name, self.index, 'warmup-'+block_id)
            self.ctx.journal.append('attempt_intent', dict(plan, phase='preparation', state=state))
            row = self.issue(name, self.index, 'warmup-'+block_id, 'preparation', state, time.time_ns())
            self.warmups.append(row)
            self.index += 1
            self.require_completed_transports()
        start_mono, load_started_ns = time.monotonic(), time.time_ns()
        futures = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            for offset, name in enumerate(ordered):
                remaining = start_mono+offset/self.rate-time.monotonic()
                if remaining > 0:
                    time.sleep(remaining)
                plan = self.adapter.plan_operation(name, self.index, block_id)
                plan.update(phase=phase, state=state, block_id=block_id)
                self.ctx.journal.append('attempt_intent', plan)
                self.plans.append(plan)
                futures.append(pool.submit(self.issue, name, self.index, block_id, phase, state,
                                           load_started_ns+int(offset/self.rate*1e9)))
                self.index += 1
            # No timeout and no fault-state transition while HTTP is in flight.
            rows = [future.result() for future in futures]
        self.require_completed_transports()
        rows = self.adapter.verify(rows)
        for row in rows:
            self.ctx.journal.append('attempt_verified', row)
        by_id = {r['attempt_id']: r for r in rows}
        with self.record_lock:
            self.records = [by_id.get(r['attempt_id'], r) for r in self.records]
        self.require_completed_transports()
        self.after_workload_block(block_id, phase, state)
        self.census.extend(intent_census(rows, phase, state))
        block = dict(id=block_id, phase=phase, state=state, attempts=count, started_ns=started_ns,
                     load_started_ns=load_started_ns, ended_ns=time.time_ns(),
                     requested_operations_per_second=self.rate, worker_capacity=self.workers,
                     nominal_load_seconds=count/self.rate, state_evidence=state_evidence,
                     experiment_http_deadline=None, completed_requests=len(rows),
                     max_dispatch_lateness_seconds=max(r['dispatch_lateness_seconds'] for r in rows))
        self.blocks.append(block)
        self.ctx.journal.append('block_complete', block)
        self.save_records()
        write_json(self.ctx.out/'plans.json', self.plans)
        print(json.dumps(block), flush=True)
        return rows

    def issue(self, name, index, namespace, phase, state, scheduled_ns):
        plan = self.adapter.plan_operation(name, index, namespace)
        # Intent is written by the scheduling thread before pool submission.
        dispatched_ns = time.time_ns()
        self.ctx.journal.append('attempt_dispatched', attempt_id=plan['attempt_id'], phase=phase,
                                state=state, block_id=namespace)
        row = self.adapter.operation(name, index, namespace)
        if row['attempt_id'] != plan['attempt_id']:
            raise RuntimeError('Adapter changed planned attempt identity')
        planned_ids = {s['request_id'] for s in plan['http_steps']}
        if any(s.get('request_id') not in planned_ids for s in row.get('http_steps', [])):
            raise RuntimeError('Adapter emitted an unplanned request identity')
        row.update(phase=phase, state=state, block_id=namespace, scheduled_ns=scheduled_ns,
                   dispatched_ns=dispatched_ns,
                   dispatch_lateness_seconds=max(0, (dispatched_ns-scheduled_ns)/1e9))
        self.ctx.journal.append('attempt_observed', row)
        with self.record_lock:
            self.records.append(row)
        return row

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
        from .identity_projection_v5 import refresh

        self.collectors.snapshot()
        self.adapter.collect_native(self.ctx.out / "native" / stage)
        write_json(self.ctx.out / f"index-{stage}.json",
                   self.store.ingest(self.collectors.root, self.ctx.out / "native"))
        refresh(self, stage)

    def before_workload_block(self, block_id, phase, state):
        from .runtime_identity_v5 import capture
        capture(self.ctx, "before-" + block_id)

    def after_workload_block(self, block_id, phase, state):
        from .runtime_identity_v5 import capture
        capture(self.ctx, "after-" + block_id)

    def freeze(self):
        plans = [p for p in self.plans if p["phase"] in ("class_train", "calibration")]
        if self.toolchain_execution == "worker":
            if self.training_release is None:
                raise RuntimeError("worker execution requires this campaign's closed checkpoint")
            from .remote_toolchain_v4 import forecast_on_worker
            forecasts = forecast_on_worker(self, self.training_checkpoint, self.training_release, plans)
        else:
            forecasts = Toolchain(self.ctx, self.system, self.store, self.declaration).forecast(plans)
        fit_classes(self.store, plans, self.declaration, self.ctx.out / "toolchain" / "classes")
        for path in (self.ctx.out / "toolchain").rglob("*"):
            if path.is_file():
                self.frozen[str(path.relative_to(self.ctx.out))] = digest(path)
        alias_root = self.ctx.out / "runtime-identity-v5"
        alias_paths = (
            alias_root / "supplied-service-aliases-training.json",
            alias_root / "supplied-service-alias-admission-training.json")
        if any(not path.is_file() for path in alias_paths):
            raise RuntimeError("training-frozen supplied logical alias table/admission is missing")
        for path in alias_paths:
            self.frozen[str(path.relative_to(self.ctx.out))] = digest(path)
        write_json(self.ctx.out / "forecast-saved.json", {
            "saved_ns": time.time_ns(), "sha256_by_path": self.frozen,
            "uses_actual_graph_simulator": True, "collector": self.collector,
            "iteration": 5, "smoke": self.smoke})
        return forecasts

    def require_completed_transports(self):
        pending = self.ctx.journal.unresolved_transports()
        if pending:
            self.save_records()
            write_json(self.ctx.out/'unresolved-transports.json', pending)
            self.ctx.journal.append('technical_stop_unresolved_transport', pending=pending)
            raise RuntimeError('Remote completion is unconfirmed; no further intervention is allowed')

    def verify_async_until_terminal(self, rows, label):
        """No deadline: a technical stop leaves retained pending observations."""
        while True:
            observed = self.adapter.verify_async(rows)
            self.ctx.journal.append('async_sql_snapshot', label=label, records=observed)
            write_json(self.ctx.out/(label+'.json'), observed)
            pending = [r for r in observed if self.async_pending(r)]
            if not pending:
                return observed
            # Poll cadence is not an admission, success or failure cutoff.
            time.sleep(1)

    @staticmethod
    def async_pending(row):
        verification = row.get('async_verification', {})
        return verification.get('state') in ('pending', 'query_unavailable')

    def save_records(self):
        write_json(self.ctx.out / 'external.json', self.records)
        write_json(self.ctx.out / 'census.json', self.census)
        write_json(self.ctx.out / 'blocks.json', self.blocks)
        write_json(self.ctx.out / 'preparation-operations.json', self.warmups)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", required=True, choices=SYSTEMS)
    parser.add_argument("--mode", required=True, choices=MODES)
    parser.add_argument("--seed", type=int, choices=(6, 7, 8), required=True)
    parser.add_argument("--collector", choices=COLLECTORS, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--training-checkpoint", type=Path)
    parser.add_argument("--toolchain-execution", choices=("local", "worker"), default="local")
    args = parser.parse_args()
    Study(args.system, args.mode, args.seed, args.out, collector=args.collector,
          smoke=args.smoke, training_checkpoint=args.training_checkpoint,
          toolchain_execution=args.toolchain_execution).run()


if __name__ == "__main__":
    main()
