from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
import time


class Context:
    def __init__(self, out: Path, mode: str, seed: int, vm_dir: Path = Path('work/vms')):
        if os.environ.get('GITHUB_ACTIONS') != 'true':
            raise RuntimeError('Application and research execution is GitHub Actions only')
        self.out = out.resolve(); self.out.mkdir(parents=True, exist_ok=True)
        self.mode = mode; self.seed = seed
        self.repo_dir = Path(__file__).resolve().parents[2]
        self.vm_dir = vm_dir.resolve()
        self.deployment_dir = self.out/'deployment'; self.deployment_dir.mkdir(exist_ok=True)
        self.command_log = self.out/'commands.jsonl'

    def node_ip(self, node):
        return {'a':'192.168.76.11','b':'192.168.76.12'}[node]

    def run(self, command_list, cwd=None, timeout=300, check=True):
        start = time.time_ns()
        result = subprocess.run(command_list, cwd=cwd, timeout=timeout, text=True, capture_output=True)
        with self.command_log.open('a', encoding='utf-8') as f:
            f.write(json.dumps({'command':command_list,'cwd':str(cwd) if cwd else None,'started_ns':start,'ended_ns':time.time_ns(),'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})+'\n')
        if check and result.returncode:
            raise RuntimeError(f'Command failed ({result.returncode}): {command_list[0]}\n{result.stderr[-4000:]}\n{result.stdout[-2000:]}')
        return result

    def ssh_args(self):
        return ['-i',str(self.vm_dir/'id_ed25519'),'-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=/dev/null','-o','ConnectTimeout=10']

    def node_exec(self, node, command, timeout=300, check=True):
        return self.run(['ssh',*self.ssh_args(),f'ubuntu@{self.node_ip(node)}','bash -lc '+shlex.quote(command)],timeout=timeout,check=check)

    def node_put(self, node, source, destination):
        source = Path(source)
        self.node_exec(node, 'mkdir -p '+shlex.quote(str(destination if source.is_dir() else Path(destination).parent)))
        target = f'ubuntu@{self.node_ip(node)}:{destination}'
        paths = [str(x) for x in source.iterdir()] if source.is_dir() else [str(source)]
        return self.run(['scp',*self.ssh_args(),'-r',*paths,target],timeout=600)

    def node_get(self, node, source, destination):
        Path(destination).parent.mkdir(parents=True,exist_ok=True)
        return self.run(['scp',*self.ssh_args(),'-r',f'ubuntu@{self.node_ip(node)}:{source}',str(destination)],timeout=600)


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
