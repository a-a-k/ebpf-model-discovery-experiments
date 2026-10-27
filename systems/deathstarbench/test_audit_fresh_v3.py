"""Small synthetic checks for the saved-evidence diagnostic categories."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from systems.deathstarbench.audit_fresh_v3 import (
    attach_raw_timestamps, classify, raw_timestamps, timestamp_verdict, verify_acquisition_rules)


class Store:
    def __init__(self, anchors):
        self.anchors = anchors

    def candidates(self, source, identity):
        return self.anchors


class Binder:
    def __init__(self, entry=None, reason='entry_missing', eligible=True):
        self.span, self.reason, self.eligible = entry, reason, eligible

    def entry(self, source, identity, expected=None):
        if expected is not None:
            raise AssertionError('automatic entry selection must not use declared operation route')
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

    def test_automatic_entry_route_can_disagree_with_declared_operation(self):
        # An unrestricted automatic entry can bind a different declared route.
        # The classifier must then assess its saved signature against frozen classes.
        observed = {'signature': ['GET /wrk2-api/home-timeline/read'], 'class_id': None}
        self.assertEqual(classify(Store([{}]), Binder(self.entry), self.row, observed,
                                  self.classes, 'ebpf')[0], 'accepted_but_novel_frozen_route_class')

    def test_raw_jaeger_units_and_otlp_ns_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native = root/'traces-test.json'
            native.write_text(json.dumps({'data': [{'spans': [{
                'traceID': 'AA', 'spanID': 'BB', 'startTime': 123456, 'duration': 20}]}]}))
            result = raw_timestamps(native, 'native', {('aa', 'bb')}, native.stat().st_size)[('aa', 'bb')][0]
            self.assertEqual((result['normalized_start_ns_from_raw'], result['normalized_end_ns_from_raw']),
                             (123456000, 123476000))
            ebpf = root/'a.jsonl'
            ebpf.write_text(json.dumps({'payload': {'resourceSpans': [{
                'scopeSpans': [{'spans': [{'traceId': 'AA', 'spanId': 'BB',
                    'startTimeUnixNano': '900', 'endTimeUnixNano': '950'}]}]}]}})+'\n')
            result = raw_timestamps(ebpf, 'ebpf', {('aa', 'bb')}, ebpf.stat().st_size)[('aa', 'bb')][0]
            self.assertEqual((result['normalized_start_ns_from_raw'], result['normalized_end_ns_from_raw']),
                             (900, 950))

    def test_indexed_prefix_and_same_id_variants_are_not_last_write_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'a.jsonl'
            def item(start, end):
                return json.dumps({'payload': {'resourceSpans': [{'scopeSpans': [{'spans': [{
                    'traceId': 'AA', 'spanId': 'BB', 'startTimeUnixNano': str(start),
                    'endTimeUnixNano': str(end)}]}]}]}})+'\n'
            prefix = item(900, 950)+item(910, 960)
            path.write_text(prefix+item(920, 970))
            variants = raw_timestamps(path, 'ebpf', {('aa', 'bb')}, len(prefix.encode()))[('aa', 'bb')]
            verdict = timestamp_verdict(variants, 900, 950,
                                        tail_bytes=path.stat().st_size-len(prefix.encode()))
            self.assertEqual(verdict['reason'], 'ambiguous_same_id_timestamp_variants')
            self.assertEqual(verdict['raw_occurrences_in_indexed_prefix'], 2)
            self.assertEqual(verdict['distinct_timestamp_pairs_in_indexed_prefix'], 2)
            self.assertEqual(verdict['matching_pair_occurrences'], 1)
            self.assertGreater(verdict['unindexed_tail_bytes'], 0)

    def test_witness_reader_uses_sqlite_consumed_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root/'observations'/'a.jsonl'
            raw.parent.mkdir()
            def item(start):
                return json.dumps({'payload': {'resourceSpans': [{'scopeSpans': [{'spans': [{
                    'traceId': 'AA', 'spanId': 'BB', 'startTimeUnixNano': str(start),
                    'endTimeUnixNano': str(start+50)}]}]}]}})+'\n'
            prefix = item(900)
            raw.write_text(prefix+item(999))
            original = '/home/runner/work/repo/work/campaign/observations/a.jsonl'
            witness = {'raw_span': {'raw_file': original, 'source': 'ebpf', 'trace_id': 'aa',
                                    'span_id': 'bb', 'start_ns': 900, 'end_ns': 950}}
            attach_raw_timestamps(root, [witness], {original: len(prefix.encode())})
            result = witness['raw_timestamp_check']
            self.assertEqual(result['reason'], 'unique_raw_timestamp_pair_matches_indexed_span')
            self.assertEqual(result['raw_occurrences_in_indexed_prefix'], 1)
            self.assertGreater(result['unindexed_tail_bytes'], 0)

    def test_replayed_rule_hashes_must_match_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ('src/ebpf_discovery/semantic_v3.py', 'src/ebpf_discovery/store_v3.py',
                     'src/ebpf_discovery/observations.py', 'src/ebpf_discovery/model.py',
                     'src/ebpf_discovery/timing_v3.py', 'systems/deathstarbench/contracts_v3.py')
            hashes = {}
            for name in names:
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name)
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            marker = {'rule_sha256': hashes}
            self.assertEqual(verify_acquisition_rules(marker, root), hashes)
            (root/names[0]).write_text('changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                verify_acquisition_rules(marker, root)


if __name__ == '__main__':
    unittest.main()
