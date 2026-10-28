import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests

from ebpf_discovery.campaign_v4 import CampaignV4
from ebpf_discovery.transport_v4 import Journal, request


class CompletionBarrierTests(unittest.TestCase):
    def test_complete_error_response_is_terminal_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(Path(directory)/'journal.sqlite')
            response = requests.Response()
            response.status_code, response._content = 503, b'unavailable'
            with patch('ebpf_discovery.transport_v4.requests.request', return_value=response):
                self.assertEqual(request('GET', 'http://example.test/', journal=journal).status_code, 503)
            self.assertEqual(journal.unresolved_transports(), [])
            journal.close()

    def test_transport_loss_stays_unresolved_after_journal_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'journal.sqlite'
            journal = Journal(path)
            with patch('ebpf_discovery.transport_v4.requests.request', side_effect=requests.ConnectionError('lost')):
                with self.assertRaises(requests.ConnectionError):
                    request('POST', 'http://example.test/', journal=journal)
            journal.close()
            journal = Journal(path)
            self.assertEqual(len(journal.unresolved_transports()), 1)
            self.assertEqual(journal.unresolved_transports()[0]['method'], 'POST')
            journal.close()

    def test_unknown_remote_completion_prevents_reset_or_next_fault(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(Path(directory)/'journal.sqlite')
            journal.append('step_started', transport_id='pending', request_id='issued')
            journal.append('step_transport_unknown', transport_id='pending', outcome=None)
            campaign = CampaignV4.__new__(CampaignV4)
            campaign.ctx = SimpleNamespace(out=Path(directory), journal=journal)
            campaign.adapter, campaign.save_records = Mock(), Mock()
            with self.assertRaisesRegex(RuntimeError, 'no further intervention'):
                campaign.block('target', '10', 1, ['operation'])
            campaign.adapter.reset.assert_not_called()
            campaign.adapter.set_replicas.assert_not_called()
            self.assertTrue((Path(directory)/'unresolved-transports.json').is_file())
            journal.close()


if __name__ == '__main__':
    unittest.main()
