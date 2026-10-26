"""Real OBI acquisition on both guests; source and guest identity are ingress facts."""
from __future__ import annotations

import json
import shlex
import subprocess
import sys
import time

import yaml

OBI_IMAGE = 'otel/ebpf-instrument:0.15.2'


class Collectors:
    def __init__(self, ctx):
        self.ctx = ctx
        self.processes = []
        self.logs = []
        self.root = ctx.out / 'observations'
        self.root.mkdir(parents=True, exist_ok=True)

    def start(self):
        for node, port in [('a', 4318), ('b', 4320), ('native', 4319)]:
            log = (self.root / f'receiver-{node}.log').open('w')
            self.logs.append(log)
            process = subprocess.Popen([
                sys.executable, '-m', 'ebpf_discovery.receiver', '--port', str(port),
                '--out', str(self.root / f'{node}.jsonl'), '--source',
                f'ebpf:{node}' if node != 'native' else 'native',
            ], stdout=log, stderr=subprocess.STDOUT)
            self.processes.append(process)
        time.sleep(1)
        if any(p.poll() is not None for p in self.processes):
            raise RuntimeError('An OTLP receiver failed to start')
        for node, port in [('a', 4318), ('b', 4320)]:
            config = {
                'log_level': 'INFO',
                'discovery': {
                    'instrument': [{'exe_path': '*', 'containers_only': True}],
                    'exclude_otel_instrumented_services': False,
                    'disabled_route_harvesters': ['java', 'nodejs'],
                },
                'javaagent': {'enabled': False},
                'nodejs': {'enabled': False, 'manual_spans': False},
                'ebpf': {
                    'context_propagation': 'all', 'track_request_headers': True,
                    'buffer_sizes': {'http': 8192},
                    'payload_extraction': {'http': {'enrichment': {
                        'enabled': True, 'policy': {'default_action': {'headers': 'exclude', 'body': 'exclude'}},
                        'rules': [{'action': 'include', 'type': 'headers', 'scope': 'all',
                                   'match': {'patterns': ['x-experiment-request-id'], 'case_sensitive': False}}],
                    }}},
                },
                'routes': {'unmatched': 'path'},
                'otel_traces_export': {'endpoint': f'http://192.168.76.1:{port}/v1/traces',
                                       'protocol': 'http/protobuf'},
            }
            path = self.root / f'obi-{node}.yaml'
            path.write_text(yaml.safe_dump(config), encoding='utf-8')
            self.ctx.node_put(node, path, '/tmp/obi-study.yaml')
            self.ctx.node_exec(node, f'docker pull {shlex.quote(OBI_IMAGE)}', timeout=300)
            self.ctx.node_exec(node,
                f'docker run -d --name study-obi --privileged --pid=host --network=host '
                f'-v /sys:/sys -v /proc:/host/proc:ro -v /var/run/docker.sock:/var/run/docker.sock '
                f'-v /tmp/obi-study.yaml:/config.yaml:ro -e OTEL_EBPF_CONFIG_PATH=/config.yaml '
                f'{shlex.quote(OBI_IMAGE)}', timeout=120)
            result = self.ctx.node_exec(node, f'docker image inspect {shlex.quote(OBI_IMAGE)}', timeout=30)
            (self.root / f'obi-image-{node}.json').write_text(result.stdout, encoding='utf-8')
        time.sleep(10)
        self.health()

    def health(self):
        for node in ('a', 'b'):
            result = self.ctx.node_exec(node, "docker inspect --format '{{.State.Running}}' study-obi", timeout=30)
            if result.stdout.strip() != 'true':
                raise RuntimeError(f'OBI exited on guest {node}')

    def snapshot(self):
        # OBI exports in batches. This is acquisition settling, counted as cost.
        time.sleep(5)
        self.health()
        for node in ('a', 'b'):
            for command, name in [
                ('docker logs study-obi', 'obi.log'),
                ('docker stats --no-stream --format "{{json .}}"', 'stats.jsonl'),
                ('docker inspect $(docker ps -aq)', 'containers.json'),
            ]:
                result = self.ctx.node_exec(node, command, timeout=60, check=False)
                (self.root / f'{node}-{name}').write_text(result.stdout + result.stderr, encoding='utf-8')

    def close(self):
        for node in ('a', 'b'):
            try:
                self.ctx.node_exec(node, 'docker stop -t 15 study-obi', timeout=30, check=False)
                result = self.ctx.node_exec(node, 'docker logs study-obi', timeout=30, check=False)
                (self.root / f'{node}-obi.log').write_text(result.stdout + result.stderr, encoding='utf-8')
            except Exception as exc:
                (self.root / f'{node}-close-error.json').write_text(json.dumps({'error': str(exc)}))
        time.sleep(1)
        for process in self.processes:
            process.terminate()
            process.wait(timeout=10)
        for log in self.logs:
            log.close()
