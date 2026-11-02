"""Ordering and failure checks around real captured data and owned VM lifetime."""
import json
import importlib.util
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
    ctx=SimpleNamespace(out=tmp_path,vm_dir=tmp_path/'vms')
    path=tmp_path/'infrastructure/a/check.txt'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'original-guest-proof')
    manifest=tmp_path/'infrastructure/guest-evidence-capture.json'
    files={'infrastructure/a/check.txt':{'bytes':path.stat().st_size,'sha256':guests._sha(path)}}
    for node in ('a','b'):
        for name in ('check-copy.err','serial-test.err','guest-kernel-final.txt',
                     'guest-kernel-final.err','guest-kernel-final.returncode',
                     'serial-test.returncode','serial-copy.status'):
            member=tmp_path/'infrastructure'/node/name
            member.parent.mkdir(parents=True,exist_ok=True)
            member.write_text('1')
            files[member.relative_to(tmp_path).as_posix()]={'bytes':member.stat().st_size,'sha256':guests._sha(member)}
    proof={'status':'complete','schema':'owned-guest-diagnostics-v5',
        'campaign_root':str(ctx.out.resolve()),'vm_root':str(ctx.vm_dir.resolve()),
        'run_id':guests.os.environ.get('GITHUB_RUN_ID'),'source':guests.os.environ.get('GITHUB_SHA'),'files':files}
    manifest.write_text(json.dumps(proof))
    monkeypatch.setattr(guests.subprocess,'run',lambda *a,**k:pytest.fail('SSH or overwrite after retained capture'))
    assert guests.retain(ctx)['status']=='complete'
    empty={**proof,'files':{}}
    manifest.write_text(json.dumps(empty))
    with pytest.raises(AssertionError,match='Incomplete two-guest'):
        guests.retain(ctx)
    manifest.write_text(json.dumps(proof))
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
    monkeypatch.setattr(guests.subprocess,'check_output',lambda args,**kwargs:calls.append(args) or b'[]')
    ticks=iter((0,31))
    monkeypatch.setattr(guests.time,'monotonic',lambda:next(ticks))
    with pytest.raises(AssertionError,match='did not exit'):
        guests.release(ctx)
    assert len(calls)==1 and calls[0][3].endswith('stop-owned-guests-v5.py')
    assert all(Path(row['overlay']).read_bytes()==b'untouched' for row in owned)
    assert json.loads((out/'infrastructure/postcapture-guest-release.json').read_text())['status']=='failed'


def test_pidfile_change_before_signal_cannot_signal_either_guest(monkeypatch,tmp_path):
    spec=importlib.util.spec_from_file_location('owned_stop',Path(__file__).resolve().parents[1]/'scripts/stop-owned-guests-v5.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    expected=[]
    for index,node in enumerate(('a','b')):
        pid=2000+index
        (tmp_path/(node+'.pid')).write_text(str(pid))
        expected.append({'node':node,'pid':pid,'start_ticks':'4','state':'S',
            'args':['qemu-system-x86_64','-pidfile',str(tmp_path/(node+'.pid')),
                    '-drive','file='+str(tmp_path/node/'root.qcow2')+',format=qcow2,if=virtio']})
    (tmp_path/'b.pid').write_text('7777')
    sent=[]
    monkeypatch.setattr(module.os,'pidfd_open',lambda pid:pid,raising=False)
    monkeypatch.setattr(module.os,'close',lambda fd:None)
    monkeypatch.setattr(module.signal,'pidfd_send_signal',lambda *args:sent.append(args),raising=False)
    monkeypatch.setattr(module,'process',lambda pid:next(row for row in expected if row['pid']==pid))
    with pytest.raises(AssertionError,match='PID file changed'):
        module.stop(tmp_path,expected)
    assert sent==[]


def test_final_fallback_rejects_unowned_pid_without_signal(monkeypatch,tmp_path):
    spec=importlib.util.spec_from_file_location('owned_stop_fallback',Path(__file__).resolve().parents[1]/'scripts/stop-owned-guests-v5.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    (tmp_path/'a.pid').write_text('7777')
    sent=[]
    monkeypatch.setattr(module.os,'pidfd_open',lambda pid:pid,raising=False)
    monkeypatch.setattr(module.os,'close',lambda fd:None)
    monkeypatch.setattr(module.signal,'pidfd_send_signal',lambda *args:sent.append(args),raising=False)
    monkeypatch.setattr(module,'process',lambda pid:{'pid':pid,'start_ticks':'5','state':'S','args':['unrelated-process']})
    with pytest.raises(AssertionError):
        module.stop(tmp_path)
    assert sent==[]
