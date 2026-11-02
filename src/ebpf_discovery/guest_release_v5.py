"""Release only finished guests after retaining their final diagnostic files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time

from .runtime import Context, write_json


def _sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def retain(ctx):
    """Run the original guest diagnostic commands once; later retention verifies."""
    proof_path=ctx.out/'infrastructure/guest-evidence-capture.json'
    if proof_path.exists():
        proof=json.loads(proof_path.read_text(encoding='utf-8'))
        assert proof['status']=='complete'
        for name, expected in proof['files'].items():
            path=(ctx.out/name).resolve()
            assert path.is_relative_to(ctx.out.resolve())
            assert path.stat().st_size==expected['bytes'] and _sha(path)==expected['sha256']
        return proof
    started=time.time_ns()
    subprocess.run(['bash',str(ctx.repo_dir/'scripts/retain-guest-evidence-v5.sh'),
                    str(ctx.vm_dir),str(ctx.out)],check=True,timeout=180)
    files={}
    for node in ('a','b'):
        for path in sorted((ctx.out/'infrastructure'/node).iterdir()):
            if path.is_file():
                files[path.relative_to(ctx.out).as_posix()]={
                    'bytes':path.stat().st_size,'sha256':_sha(path)}
    proof={'status':'complete','started_ns':started,'ended_ns':time.time_ns(),
           'scope':'Original check/serial/stat/dmesg commands and actual returncodes; no zero-loss claim',
           'files':files}
    write_json(proof_path,proof)
    return proof


def _process(pid):
    root=Path('/proc')/str(pid)
    try:
        fields=(root/'stat').read_text().rsplit(') ',1)[1].split()
        args=(root/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')
    except FileNotFoundError:
        return None
    return {'pid':pid,'start_ticks':fields[19],'state':fields[0],
            'args':[os.fsdecode(arg) for arg in args]}


def _owned(ctx,node):
    pidfile=ctx.vm_dir/(node+'.pid')
    assert pidfile.is_file() and not pidfile.is_symlink()
    pid=int(subprocess.check_output(['sudo','cat','--',str(pidfile)]))
    assert pid>1
    process=_process(pid)
    assert process is not None, 'Owned guest already exited before controlled release'
    args=process['args']
    assert Path(args[0]).name=='qemu-system-x86_64'
    assert args[args.index('-pidfile')+1]==str(pidfile)
    overlay=ctx.vm_dir/node/'root.qcow2'
    assert not overlay.is_symlink() and overlay.resolve()==overlay
    info=overlay.stat()
    assert stat.S_ISREG(info.st_mode)
    expected='file='+str(overlay)+',format=qcow2,if=virtio'
    assert any(args[i]=='-drive' and args[i+1]==expected for i in range(len(args)-1))
    return {**process,'node':node,'pidfile':str(pidfile),'overlay':str(overlay),
            'overlay_device':info.st_dev,'overlay_inode':info.st_ino}


def release(ctx):
    """Called only after final acquisition, native capture and application close."""
    assert os.environ.get('GITHUB_ACTIONS')=='true'
    proof_path=ctx.out/'infrastructure/postcapture-guest-release.json'
    assert not proof_path.exists(), 'No repeated release or implicit retry'
    result={'status':'started','started_ns':time.time_ns(),
            'scope':'Only owned QEMU and ephemeral root.qcow2; captured observations/models unchanged',
            'disk_before':shutil.disk_usage(ctx.vm_dir)._asdict()}
    try:
        capture=retain(ctx)
        result['guest_evidence_capture_SHA256']=_sha(ctx.out/'infrastructure/guest-evidence-capture.json')
        assert capture['status']=='complete'
        owned=[_owned(ctx,node) for node in ('a','b')]
        assert len({row['pid'] for row in owned})==2
        result['owned_processes']=owned
        write_json(proof_path,result)
        subprocess.run(['bash',str(ctx.repo_dir/'scripts/vms.sh'),'stop',str(ctx.vm_dir)],check=True,timeout=30)
        deadline=time.monotonic()+30
        pending=list(owned)
        while pending:
            for row in pending[:]:
                current=_process(row['pid'])
                if (current is None or current['start_ticks']!=row['start_ticks']
                        or current['state']=='Z'):
                    pidfile=Path(row['pidfile'])
                    assert int(subprocess.check_output(['sudo','cat','--',str(pidfile)]))==row['pid']
                    subprocess.run(['sudo','rm','--',str(pidfile)],check=True)
                    pending.remove(row)
            if not pending:
                break
            assert time.monotonic()<deadline, 'Owned QEMU did not exit; overlays retained'
            time.sleep(.1)
        result['owned_guests_confirmed_exited_ns']=time.time_ns()
        removed=[]
        for row in owned:
            path=Path(row['overlay'])
            assert path==ctx.vm_dir/row['node']/'root.qcow2'
            assert not path.is_symlink() and path.resolve()==path
            info=path.stat()
            assert (info.st_dev,info.st_ino)==(row['overlay_device'],row['overlay_inode'])
            assert stat.S_ISREG(info.st_mode)
            subprocess.run(['sudo','rm','--',str(path)],check=True)
            assert not path.exists()
            removed.append({'path':str(path),'logical_bytes':info.st_size,
                            'allocated_bytes_before_unlink':info.st_blocks*512})
        result.update(status='complete',removed_ephemeral_overlays=removed,
                      disk_after=shutil.disk_usage(ctx.vm_dir)._asdict())
    except BaseException as error:
        result.update(status='failed',error=repr(error))
        raise
    finally:
        result['ended_ns']=time.time_ns()
        result['elapsed_seconds']=(result['ended_ns']-result['started_ns'])/1e9
        write_json(proof_path,result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('retain','release'))
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--vms',type=Path,required=True)
    args=parser.parse_args()
    ctx=Context(args.out,'postcapture-retention',0,vm_dir=args.vms)
    {'retain':retain,'release':release}[args.action](ctx)
