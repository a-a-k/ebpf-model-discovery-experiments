"""Separate OTLP HTTP ingress files; provenance comes from the listening port."""
from __future__ import annotations
import argparse,gzip,json,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Lock


def serve(port: int, output: Path, source: str):
    output.parent.mkdir(parents=True,exist_ok=True); lock=Lock()
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body=self.rfile.read(int(self.headers.get('Content-Length','0')))
            if self.headers.get('Content-Encoding')=='gzip': body=gzip.decompress(body)
            try:
                if 'json' in self.headers.get('Content-Type',''):
                    payload=json.loads(body)
                else:
                    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
                    from google.protobuf.json_format import MessageToDict
                    request=ExportTraceServiceRequest(); request.ParseFromString(body)
                    payload=MessageToDict(request)
                with lock, output.open('a',encoding='utf-8') as f:
                    f.write(json.dumps({'source':source,'received_ns':time.time_ns(),'path':self.path,'payload':payload})+'\n')
                self.send_response(200); self.send_header('Content-Type','application/x-protobuf'); self.end_headers()
            except Exception as exc:
                with lock, output.with_suffix('.errors.jsonl').open('a',encoding='utf-8') as f:
                    f.write(json.dumps({'error':str(exc),'received_ns':time.time_ns(),'path':self.path})+'\n')
                self.send_response(400); self.end_headers()
        def log_message(self,*args): pass
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--source',required=True)
    a=p.parse_args();serve(a.port,a.out,a.source)
