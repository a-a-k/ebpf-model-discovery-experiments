"""A stream that stays active must still expire at the total observation cap."""
import http.server
import threading
import time
import unittest

import requests
from ebpf_discovery.transport_v3 import request


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        body = b'{"ok":true}'
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        try:
            for byte in body:
                self.wfile.write(bytes([byte]))
                self.wfile.flush()
                if self.path == '/slow':
                    time.sleep(.04)
        except (BrokenPipeError, ConnectionResetError):
            pass


class TotalCapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:'+str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_complete_response_keeps_original_parser(self):
        response = request('GET', self.url+'/ok', timeout=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True})
        self.assertIsInstance(response._study_body_completed_ns, int)

    def test_periodic_body_bytes_do_not_extend_total_cap(self):
        started = time.monotonic()
        with self.assertRaises(requests.Timeout):
            request('GET', self.url+'/slow', timeout=.12)
        self.assertLess(time.monotonic()-started, .4)
