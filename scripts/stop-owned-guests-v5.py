"""Signal only exact owned QEMU identities through Linux process descriptors."""
import argparse
import json
import os
from pathlib import Path
import signal


def process(pid):
    root=Path('/proc')/str(pid)
    try:
        fields=(root/'stat').read_text().rsplit(') ',1)[1].split()
        args=(root/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')
    except FileNotFoundError:
        return None
    return {'pid':pid,'start_ticks':fields[19],'state':fields[0],
            'args':[os.fsdecode(arg) for arg in args]}


def stop(vm_root,expected=None):
    assert os.environ.get('GITHUB_ACTIONS')=='true'
    vm_root=vm_root.resolve(strict=True)
    if expected is not None:
        assert {row['node'] for row in expected}=={'a','b'} and len(expected)==2
    handles=[]
    result=[]
    try:
        for node in ('a','b'):
            pidfile=vm_root/(node+'.pid')
            if not pidfile.exists() and expected is None:
                continue
            assert pidfile.is_file() and not pidfile.is_symlink()
            pid=int(pidfile.read_text())
            assert pid>1
            original=next((row for row in expected or [] if row['node']==node),None)
            if original is not None:
                assert pid==original['pid'], 'PID file changed before signal'
            try:
                handle=os.pidfd_open(pid)
            except ProcessLookupError:
                result.append({'node':node,'pid':pid,'status':'already_exited_without_signal'})
                continue
            handles.append(handle)
            current=process(pid)
            if current is None or current['state']=='Z':
                result.append({'node':node,'pid':pid,'status':'already_exited_without_signal'})
                continue
            if original is not None:
                assert current['start_ticks']==original['start_ticks'], 'PID reused before signal'
                assert current['args']==original['args'], 'Owned command changed before signal'
            args=current['args']
            assert Path(args[0]).name=='qemu-system-x86_64'
            assert args[args.index('-pidfile')+1]==str(pidfile)
            drive='file='+str(vm_root/node/'root.qcow2')+',format=qcow2,if=virtio'
            assert any(args[i]=='-drive' and args[i+1]==drive for i in range(len(args)-1))
            result.append({'node':node,**current,'status':'identity_verified','handle':handle})
        # All identities are checked before either signal. A pidfd remains bound
        # to the original process even if that PID exits and is reused afterward.
        for row in result:
            if row['status']=='identity_verified':
                try:
                    signal.pidfd_send_signal(row.pop('handle'),signal.SIGTERM)
                    row['status']='TERM_sent_through_verified_pidfd'
                except ProcessLookupError:
                    row['status']='exited_before_signal'
    finally:
        for handle in handles:
            os.close(handle)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--vms',type=Path,required=True)
    parser.add_argument('--expected-json')
    args=parser.parse_args()
    print(json.dumps(stop(args.vms,json.loads(args.expected_json) if args.expected_json else None)))
