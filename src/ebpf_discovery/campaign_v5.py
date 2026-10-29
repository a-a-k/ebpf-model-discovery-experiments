"""Matched collector campaigns; fixed technical smokes precede full acquisition."""
from __future__ import annotations

import argparse
import importlib
import os
from pathlib import Path
import time
import traceback

from .campaign_v4 import CampaignV4
from .classes_v5 import evaluate as evaluate_classes, fit as fit_classes
from .evidence_v4 import evaluate as evaluate_evidence
from .runtime import write_json
from .toolchain_v4 import digest
from .toolchain_v5 import Toolchain


COLLECTORS = ("obi", "deepflow", "newrelic", "coroot")


def workload_counts(operation_count, smoke):
    if operation_count <= 0:
        raise ValueError("a campaign must retain at least one operation")
    return ({"class_train": 3 * operation_count, "calibration": operation_count,
             "target": operation_count, "class_test": 3 * operation_count,
             "database": operation_count, "async": 1} if smoke else
            {"class_train": 600, "calibration": 6000, "target": 1200,
             "class_test": 600, "database": 20, "async": 20})


class CampaignV5(CampaignV4):
    def __init__(self, system, mode, seed, out, *, collector, smoke=False,
                 training_checkpoint=None, toolchain_execution="local"):
        if collector not in COLLECTORS:
            raise ValueError("unknown collector: " + str(collector))
        if smoke and seed != 6:
            raise ValueError("technical smokes use the predeclared seed 6")
        super().__init__(system, mode, seed, out, training_checkpoint=training_checkpoint,
                         toolchain_execution=toolchain_execution)
        self.collector, self.smoke = collector, smoke
        self.ctx.collector = collector
        self.ctx.observation_policy = "uncapped-v5"
        from .store_v5 import ObservationStoreV5
        self.store.close()
        self.store = ObservationStoreV5(self.ctx.out / "observation-index.sqlite", same_trace_parents=True)
        if system == "otel_demo":
            self.declaration = importlib.import_module("systems.otel_demo.experiment_v5")
            self.adapter = self.declaration.Adapter(self.ctx)
        from .collectors_v5 import make_collectors
        self.collectors = make_collectors(self.ctx, collector)

    def before_workload_block(self, block_id, phase, state):
        from .runtime_identity_v5 import capture
        capture(self.ctx, "before-" + block_id)

    def after_workload_block(self, block_id, phase, state):
        from .runtime_identity_v5 import capture
        capture(self.ctx, "after-" + block_id)

    def snapshot(self, stage):
        super().snapshot(stage)
        from .identity_projection_v5 import refresh
        refresh(self, stage)

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

    def run(self):
        counts = workload_counts(len(self.declaration.CONTRACTS), self.smoke)
        status = dict(system=self.system, mode=self.ctx.mode, seed=self.ctx.seed,
                      collector=self.collector, smoke=self.smoke, workload_counts=counts,
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True, choices=["deathstarbench", "otel_demo", "petclinic"])
    parser.add_argument("--mode", required=True, choices=["absent", "partial", "full"])
    parser.add_argument("--seed", type=int, choices=[6, 7, 8], required=True)
    parser.add_argument("--collector", choices=COLLECTORS, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--training-checkpoint", type=Path)
    parser.add_argument("--toolchain-execution", choices=["local", "worker"], default="local")
    args = parser.parse_args()
    CampaignV5(args.system, args.mode, args.seed, args.out, collector=args.collector,
               smoke=args.smoke, training_checkpoint=args.training_checkpoint,
               toolchain_execution=args.toolchain_execution).run()


if __name__ == "__main__":
    main()
