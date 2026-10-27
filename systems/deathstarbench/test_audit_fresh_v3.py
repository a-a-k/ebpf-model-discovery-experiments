"""Small synthetic checks for the saved-evidence diagnostic categories."""
import json
from pathlib import Path
import tempfile
import unittest

from systems.deathstarbench.audit_fresh_v3 import classify, raw_timestamps


class Store:
    def __init__(self, anchors):
        self.anchors = anchors

    def candidates(self, source, identity):
        return self.anchors


class Binder:
    def __init__(self, entry=None, reason='entry_missing', eligible=True):
        self.span, self.reason, self.eligible = entry, reason, eligible

    def entry(self, source, identity, expected):
        return self.span, self.reason

    def entry_window(self, entry, source, identity, row):
        return self.eligible, 'strict_sealed_window' if self.eligible else 'entry_outside_sealed_observation_window', None


class FreshAuditTests(unittest.TestCase):
    def setUp(self):
        self.row = {'step_ids': ['one'], 'operation_id': 'compose_post'}
        self.classes = {'frozen': {'signature': ['POST /wrk2-api/post/compose']}}
        self.entry = {'start_ns': 10, 'end_ns': 20}

    def test_separates_missing_id_unbound_timing_and_frozen_class(self):
        assign = {'signature': ['POST /wrk2-api/post/compose'], 'class_id': 'frozen'}
        self.assertEqual(classify(Store([]), Binder(), self.row, assign, self.classes, 'ebpf')[0],
                         'no_exact_dispatched_step_id')
        self.assertEqual(classify(Store([{}]), Binder(), self.row, assign, self.classes, 'ebpf')[0],
                         'exact_id_but_entry_unbound_pre_window')
        self.assertEqual(classify(Store([{}]), Binder(self.entry, eligible=False), self.row,
                                  assign, self.classes, 'ebpf')[0], 'unique_entry_rejected_by_timing')
        self.assertEqual(classify(Store([{}]), Binder(self.entry), self.row,
                                  assign, self.classes, 'ebpf')[0], 'accepted_frozen_route_class')

    def test_distinguishes_missing_and_novel_signature_after_entry(self):
        binder = Binder(self.entry)
        store = Store([{}])
        missing = {'signature': [None], 'class_id': None}
        novel = {'signature': ['GET /new'], 'class_id': None}
        self.assertEqual(classify(store, binder, self.row, missing, self.classes, 'native')[0],
                         'accepted_but_missing_route_signature')
        self.assertEqual(classify(store, binder, self.row, novel, self.classes, 'native')[0],
                         'accepted_but_novel_frozen_route_class')

    def test_raw_jaeger_units_and_otlp_ns_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native = root/'traces-test.json'
            native.write_text(json.dumps({'data': [{'spans': [{
                'traceID': 'AA', 'spanID': 'BB', 'startTime': 123456, 'duration': 20}]}]}))
            result = raw_timestamps(native, 'native', {('aa', 'bb')})[('aa', 'bb')]
            self.assertEqual((result['normalized_start_ns_from_raw'], result['normalized_end_ns_from_raw']),
                             (123456000, 123476000))
            ebpf = root/'a.jsonl'
            ebpf.write_text(json.dumps({'payload': {'resourceSpans': [{
                'scopeSpans': [{'spans': [{'traceId': 'AA', 'spanId': 'BB',
                    'startTimeUnixNano': '900', 'endTimeUnixNano': '950'}]}]}]}})+'\n')
            result = raw_timestamps(ebpf, 'ebpf', {('aa', 'bb')})[('aa', 'bb')]
            self.assertEqual((result['normalized_start_ns_from_raw'], result['normalized_end_ns_from_raw']),
                             (900, 950))


if __name__ == '__main__':
    unittest.main()
