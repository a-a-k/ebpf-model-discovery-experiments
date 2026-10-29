import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ebpf_discovery.toolchain_v5 import PINS, Toolchain, collector_provenance


def _write(root: Path, status_collector='coroot', retained_collector='coroot'):
    (root/'observations').mkdir(parents=True)
    (root/'status.json').write_text(json.dumps({
        'protocol_version': 'graph-v5', 'collector': status_collector}))
    (root/'observations'/'collector.json').write_text(json.dumps({
        'schema': 'collector-lifecycle-v5', 'collector': retained_collector,
        'source_domain': 'ebpf-'+retained_collector}))


def test_study_collector_uses_vendor_neutral_product_profiles_and_pins(tmp_path):
    _write(tmp_path)
    (tmp_path/'deployment.json').write_text('{}')
    tool = Toolchain(SimpleNamespace(out=tmp_path), 'demo', None, SimpleNamespace())
    assert tool.tool_pins == PINS
    assert tool.ebpf_collection_args() == [
        '--collection-source', 'ebpf-otlp',
        '--source-domain', 'demo-deployment']
    assert tool.bering_source_profile() == {'source_id': 'ebpf', 'input_type': 'ebpf-otlp'}
    assert tool.collector_static_input()['procrustes_profile'] == 'ebpf-otlp'
    assert tool.collector_static_input()['collector'] == 'coroot'
    assert tool.collector_static_input()['study_provenance_only'] is True
    assert tool.collector_static_input()['product_profile_contains_collector_identity'] is False


def test_v5_obi_arm_also_uses_common_profile_and_mismatch_is_rejected(tmp_path):
    _write(tmp_path, 'obi', 'obi')
    (tmp_path/'deployment.json').write_text('{}')
    tool = Toolchain(SimpleNamespace(out=tmp_path), 'demo', None, SimpleNamespace())
    assert tool.ebpf_collection_args()[1] == 'ebpf-otlp'
    assert '--collector' not in tool.ebpf_collection_args()
    assert tool.bering_source_profile() == {'source_id': 'ebpf', 'input_type': 'ebpf-otlp'}
    (tmp_path/'observations'/'collector.json').write_text(json.dumps({'collector': 'coroot'}))
    with pytest.raises(ValueError, match='differs'):
        collector_provenance(tmp_path)
