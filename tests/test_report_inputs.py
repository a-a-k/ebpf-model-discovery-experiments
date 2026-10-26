from ebpf_discovery.report import campaign_metric_paths


def test_native_exporter_metrics_are_not_campaign_results(tmp_path):
    campaign = tmp_path/'123'/'campaign-otel_demo-full-0-123'
    native = campaign/'native'/'calibration'
    native.mkdir(parents=True)
    (native/'metrics.json').write_text('{"resourceMetrics": []}')
    (campaign/'status.json').write_text('{"status": "acquisition_complete"}')
    (campaign/'metrics.json').write_text('{"sources": {}}')
    failed = tmp_path/'456'/'campaign-otel_demo-full-0-456'
    failed.mkdir(parents=True)
    (failed/'status.json').write_text('{"status": "technical_failure"}')
    assert campaign_metric_paths(tmp_path) == [campaign/'metrics.json']
