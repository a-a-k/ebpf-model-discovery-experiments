"""Ordering and failure checks around real captured data and owned VM lifetime."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ebpf_discovery import guest_release_v5 as guests
from ebpf_discovery import identity_projection_v5, study


def test_capture_precedes_release_and_processing_with_no_second_application_close(monkeypatch,tmp_path):
    events=[]
    value=study.Study.__new__(study.Study)
    value.system,value.collector='otel_demo','deepflow'
    value._application_close_attempted=False
    value.ctx=SimpleNamespace(out=tmp_path)
    value.collectors=SimpleNamespace(root=tmp_path/'observations',
        snapshot=lambda:events.append('snapshot'),close=lambda:events.append('collector-close'))
    value.adapter=SimpleNamespace(collect_native=lambda path:events.append('native'),
        close=lambda:events.append('application-close'))
    value.store=SimpleNamespace(ingest=lambda *args:events.append('ingest') or {})
    monkeypatch.setattr(guests,'release',lambda ctx:events.append('release'))
    monkeypatch.setattr(identity_projection_v5,'refresh',lambda *args:events.append('refresh'))
    value.snapshot('final')
    value.close_application()
    assert events==['snapshot','native','collector-close','application-close','release','ingest','refresh']


def test_failed_application_close_is_fatal_and_not_repeated(monkeypatch,tmp_path):
    events=[]
    value=study.Study.__new__(study.Study)
    value._application_close_attempted=False
    def fail():
        events.append('application-close')
        raise RuntimeError('required application cleanup failed')
    value.adapter=SimpleNamespace(close=fail)
    with pytest.raises(RuntimeError,match='required application'):
        value.close_application()
    value.close_application()
    assert events==['application-close']


def test_retention_reuses_verified_files_and_rejects_changed_capture(monkeypatch,tmp_path):
    ctx=SimpleNamespace(out=tmp_path)
    path=tmp_path/'infrastructure/a/check.txt'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'original-guest-proof')
    manifest=tmp_path/'infrastructure/guest-evidence-capture.json'
    manifest.write_text(json.dumps({'status':'complete','files':{
        'infrastructure/a/check.txt':{'bytes':path.stat().st_size,'sha256':guests._sha(path)}}}))
    monkeypatch.setattr(guests.subprocess,'run',lambda *a,**k:pytest.fail('SSH or overwrite after retained capture'))
    assert guests.retain(ctx)['status']=='complete'
    path.write_bytes(b'changed')
    with pytest.raises(AssertionError):
        guests.retain(ctx)


def test_foreign_pid_cannot_be_stopped_or_have_overlay_deleted(monkeypatch,tmp_path):
    ctx=SimpleNamespace(vm_dir=tmp_path.resolve())
    (tmp_path/'a').mkdir()
    overlay=tmp_path/'a/root.qcow2'
    overlay.write_bytes(b'owned-overlay')
    (tmp_path/'a.pid').write_text('2000')
    monkeypatch.setattr(guests.subprocess,'check_output',lambda *a,**k:b'2000')
    monkeypatch.setattr(guests,'_process',lambda pid:{'pid':pid,'start_ticks':'4','state':'S','args':['unrelated-process']})
    monkeypatch.setattr(guests.subprocess,'run',lambda *a,**k:pytest.fail('must not stop or unlink'))
    with pytest.raises(AssertionError):
        guests._owned(ctx,'a')
    assert overlay.read_bytes()==b'owned-overlay'


def test_stop_request_without_confirmed_exit_keeps_both_overlays(monkeypatch,tmp_path):
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    root=tmp_path/'vms'
    root.mkdir()
    out=tmp_path/'campaign'
    (out/'infrastructure').mkdir(parents=True)
    (out/'infrastructure/guest-evidence-capture.json').write_text('{}')
    ctx=SimpleNamespace(vm_dir=root.resolve(),out=out.resolve(),repo_dir=tmp_path.resolve())
    owned=[]
    for index,node in enumerate(('a','b')):
        (root/node).mkdir()
        image=root/node/'root.qcow2'
        image.write_bytes(b'untouched')
        owned.append({'pid':2000+index,'start_ticks':'4','node':node,'overlay':str(image)})
    monkeypatch.setattr(guests,'retain',lambda ctx:{'status':'complete'})
    monkeypatch.setattr(guests,'_owned',lambda ctx,node:owned[('a','b').index(node)])
    monkeypatch.setattr(guests,'_process',lambda pid:{'pid':pid,'start_ticks':'4','state':'S'})
    calls=[]
    monkeypatch.setattr(guests.subprocess,'run',lambda args,**kwargs:calls.append(args))
    ticks=iter((0,31))
    monkeypatch.setattr(guests.time,'monotonic',lambda:next(ticks))
    with pytest.raises(AssertionError,match='did not exit'):
        guests.release(ctx)
    assert len(calls)==1 and calls[0][2]=='stop'
    assert all(Path(row['overlay']).read_bytes()==b'untouched' for row in owned)
    assert json.loads((out/'infrastructure/postcapture-guest-release.json').read_text())['status']=='failed'
