"""First-class agent-free control, sharing the ordinary receiver/control traffic."""
from __future__ import annotations

import json
import time

from .collectors_v5 import CollectorsV5, RECEIVERS, make_collectors as existing_collectors
from .runtime import write_json


class NoAgent(CollectorsV5):
    collector = 'none'
    image = None
    source_version = None
    source_commit = None

    def _absence(self):
        observed = {}
        for node in ('a', 'b'):
            commands = {'containers': "docker ps --no-trunc --format '{{json .}}'",
                        'processes': 'ps -e -o pid=,comm=,args=',
                        'boot_id': 'cat /proc/sys/kernel/random/boot_id'}
            results = {label: self.ctx.node_exec(node, command, timeout=30)
                       for label, command in commands.items()}
            if any(r.returncode != 0 for r in results.values()):
                raise RuntimeError('no-agent process/container census failed')
            text = '\n'.join(r.stdout for r in results.values())
            # Fresh guest kernels plus an actual process/container census establish
            # absence of the study agents; nothing is inferred from missing exports.
            if any(name in text.lower() for name in (
                    'study-obi', 'study-coroot', 'deepflow-agent', 'coroot-node-agent',
                    'opentelemetry-ebpf-instrumentation', 'otel/ebpf-instrument',
                    'coroot-node-age', 'beyla')) or any(
                    line.split()[1:2] == ['obi'] for line in results['processes'].stdout.splitlines()):
                raise RuntimeError('a study agent is running in the no-agent control')
            observed[node] = {'census': text, 'checked_ns': time.time_ns(),
                              'commands': {label: {'command': commands[label],
                                  'returncode': result.returncode, 'stdout': result.stdout,
                                  'stderr': getattr(result, 'stderr', '')}
                                  for label, result in results.items()}}
        return observed

    def start(self):
        self._start_entered = True
        self.started_ns = time.time_ns()
        self._start_receivers()
        self._write_collector_metadata({
            'schema': 'collector-lifecycle-v6', 'collector': 'none',
            'source_domain': self.source_domain, 'image': None,
            'runtime_treatment': 'no study eBPF agent installed or started',
            'receivers': RECEIVERS, 'before_deployment': self._absence(),
            'started_ns': self.started_ns, 'lifecycle': 'started',
            'closed_checkpoint': False})

    def health(self):
        return self._absence()

    def certify_controls(self, timeout=60.0):
        return self.positive_control(timeout=timeout, expect_ebpf=False, fixed_window=True)

    def snapshot(self):
        write_json(self.root / 'no-agent-snapshot.json', self._absence())

    def final_drain(self):
        if self._drained:
            return self._drain_evidence
        absent = self._absence()
        barriers = {node: self._receiver_barrier(node) for node in RECEIVERS}
        receivers = self._close_receivers()
        valid = (all(v.get('accepted') for v in barriers.values())
                 and all(v.get('technical_valid') for v in receivers.values()))
        evidence = {'schema': 'no-agent-closed-receivers-v6', 'collector': 'none',
                    'agent_absence': absent, 'technical_valid': valid,
                    'technical_complete': valid, 'receiver_acceptance_barriers': barriers,
                    'receiver_closed_checkpoints': receivers,
                    'accepted_receiver_bytes_closed_and_hashed': all(
                        v.get('saved_bytes_valid') and v.get('parent_hash_verification')
                        for v in receivers.values())}
        write_json(self.root / 'drain-evidence.json', evidence)
        metadata = json.loads((self.root / 'collector.json').read_text(encoding='utf8'))
        metadata.update(lifecycle='closed', closed_checkpoint=valid,
                        technical_valid=valid, drain_evidence='drain-evidence.json')
        self._write_collector_metadata(metadata)
        self._drained, self._drain_evidence = True, evidence
        if not valid:
            raise RuntimeError('no-agent receiver closure failed')
        return evidence


def make_collectors(ctx, collector):
    return NoAgent(ctx) if collector == 'none' else existing_collectors(ctx, collector)


def certify_controls(collector):
    return collector.positive_control(timeout=60.0,
                                      expect_ebpf=collector.collector != 'none', fixed_window=True)
