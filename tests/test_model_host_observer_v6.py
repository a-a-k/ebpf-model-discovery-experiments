"""The read-only observer cannot turn a failed model into a successful job."""
import importlib.util
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest


@pytest.fixture
def observer():
    spec = importlib.util.spec_from_file_location('host_observer',
        Path(__file__).resolve().parents[1]/'scripts/observe-v6-model-host.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('model_code,expected', [(0,0),(17,17),(-9,137)])
def test_observation_failure_preserves_actual_model_exit(observer, monkeypatch, tmp_path, model_code, expected):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    monkeypatch.setenv('GITHUB_REPOSITORY','a-a-k/ebpf-model-discovery-experiments')
    commands=[]
    def start(command):
        commands.append(command)
        return SimpleNamespace(pid=123,wait=lambda:model_code)
    monkeypatch.setattr(observer.subprocess,'Popen',start)
    monkeypatch.setattr(observer,'proc',lambda _:None)
    monkeypatch.setattr(observer,'observe',lambda *_:None)
    monkeypatch.setattr(observer,'REPORT',tmp_path)  # A directory cannot receive a log append.
    assert observer.main()==expected
    assert commands==[[observer.sys.executable,'-m','ebpf_discovery.study_v6','model','--root','work/case']]


def test_missing_journal_is_unknown_and_messages_are_not_retained(observer, monkeypatch):
    monkeypatch.setattr(observer.subprocess,'run',lambda *_args,**_kw:SimpleNamespace(returncode=1))
    assert observer.journal('kernel',0)=={'status':'UNKNOWN','returncode':1}
    body='{"MESSAGE":"memory pressure reason=LowMemory synthetic-private-data", "_PID":"42"}'
    monkeypatch.setattr(observer.subprocess,'run',lambda *_args,**_kw:SimpleNamespace(returncode=0,stdout=body))
    result=observer.journal('kernel',0)
    assert result['events'][0]['literal_reason_word']=='LowMemory'
    assert 'synthetic-private-data' not in str(result)


@pytest.mark.parametrize('model_code,expected', [(0,0),(17,17),(-9,137)])
def test_actual_wrapper_exit_survives_closed_stdout(observer, monkeypatch, tmp_path, model_code, expected):
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    monkeypatch.setenv('GITHUB_REPOSITORY','a-a-k/ebpf-model-discovery-experiments')
    program = f'''import importlib.util
from types import SimpleNamespace
spec=importlib.util.spec_from_file_location('observer',{observer.__file__!r})
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.proc=lambda _:None
module.observe=lambda *_:None
module.subprocess.Popen=lambda command:SimpleNamespace(pid=123,wait=lambda:{model_code})
raise SystemExit(module.main())
'''
    process=subprocess.Popen([sys.executable,'-c',program],cwd=tmp_path,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    process.stdout.close()
    stderr=process.stderr.read()
    assert process.wait(timeout=10)==expected, stderr.decode()
    assert b'Exception ignored' not in stderr
