"""Bounded, non-scientific deployment/collector check before the fixed campaign."""
from __future__ import annotations
import argparse
import importlib
import json
import os
import time
import traceback
from pathlib import Path
from .runtime import Context, write_json
from .collectors import Collectors
from .observations import read_spans, step_id, graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--system', required=True, choices=['deathstarbench', 'otel_demo', 'petclinic'])
    parser.add_argument('--mode', default='absent', choices=['absent', 'partial', 'full'])
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx = Context(args.out, args.mode, args.seed)
    adapter = importlib.import_module(f'systems.{args.system}.adapter').Adapter(ctx)
    collectors = Collectors(ctx)
    fallback_handle = None
    start = time.time_ns()
    status = {'system': args.system, 'mode': args.mode, 'purpose': 'technical_qualification', 'started_ns': start}
    try:
        adapter.prepare()
        collectors.start()
        adapter.deploy()
        adapter.ready()
        collectors.settle()
        metadata = adapter.metadata()
        write_json(ctx.out / 'deployment.json', metadata)
        records = []
        index = 0
        for _ in range(4):
            for name in metadata['operations']:
                records.append(adapter.operation(name, index, 'qualification', 2.0))
                index += 1
        records = adapter.verify(records)
        write_json(ctx.out / 'external.json', records)
        collectors.snapshot()
        adapter.collect_native(ctx.out / 'native')
        spans, parse_errors = read_spans(collectors.root, ctx.out / 'native')
        requested = {s.get('request_id') for r in records for s in r['http_steps']}
        support = {}
        for source in ['ebpf', 'native']:
            observed = [s for s in spans if s['source'] == source]
            bound = {step_id(s) for s in observed} & (requested - {None})
            support[source] = {'spans': len(observed), 'requested_steps': len(requested), 'bound_steps': len(bound),
                               'services': sorted({s['service'] for s in observed}),
                               'graph': graph(observed)}
        write_json(ctx.out / 'observation-support.json', {'sources': support, 'parse_errors': parse_errors})
        if os.environ.get('DEEPFLOW_FALLBACK') == 'true':
            from systems.deathstarbench.deepflow_fallback import fallback
            fallback_handle = fallback(ctx, adapter, ctx.out)
            time.sleep(15)
            fallback_records = []
            for _ in range(4):
                for name in metadata['operations']:
                    fallback_records.append(adapter.operation(name, index, 'deepflow-qualification', 2.0))
                    index += 1
                    time.sleep(.25)
            write_json(ctx.out / 'deepflow-fallback' / 'external.json', adapter.verify(fallback_records))
            fallback_handle.collect()
        status.update(status='deployment_completed', successful=sum(r.get('success') is True for r in records),
                      attempts=len(records), observation_bytes={p.name: p.stat().st_size for p in collectors.root.glob('*.jsonl')})
    except Exception as exc:
        status.update(status='technical_failure', error=str(exc), traceback=traceback.format_exc())
        raise
    finally:
        if fallback_handle is not None and not fallback_handle.collected:
            try:
                fallback_handle.collect()
            except Exception as exc:
                status['deepflow_close_error'] = str(exc)
        for label, action in [('adapter', adapter.close), ('collectors', collectors.close)]:
            try:
                action()
            except Exception as exc:
                status[label + '_close_error'] = str(exc)
        status['ended_ns'] = time.time_ns()
        status['elapsed_seconds'] = (status['ended_ns'] - start) / 1e9
        write_json(ctx.out / 'qualification.json', status)
        print(json.dumps(status, indent=2), flush=True)


if __name__ == '__main__':
    main()
