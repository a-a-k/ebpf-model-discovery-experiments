"""Tiny Actions-only ABI check; synthetic graph, not an empirical study case."""
from copy import deepcopy
import json
import os
from pathlib import Path

from ebpf_discovery.compose_ack_contract import simulate
from ebpf_discovery.runtime import Context, write_json
from ebpf_discovery.toolchain_v4 import Toolchain, digest
from ebpf_discovery.toolchain_v5 import PINS


assert os.environ.get('GITHUB_ACTIONS') == 'true'
root = Path('work/compose-contract-product-fixture').resolve()
root.mkdir()
build = Path('work/toolchain-build')
receipt = json.loads((build / 'toolchain-build.json').read_text())
for name, pin in [('bering', PINS['Bering']), ('sheaft', PINS['Sheaft'])]:
    actual = next(b for b in receipt['binaries'] if b['name'] == name)
    assert actual['commit'] == pin and digest(build / 'bin' / name) == actual['binary_sha256']
source = build / 'checkouts/sheaft/examples/outputs/model.required-calls.sample.json'
sample = json.loads(source.read_text())
model = {key: deepcopy(sample[key]) for key in ('services', 'edges', 'endpoints', 'metadata')}
for service in model['services']:
    service['metadata'] = {}
    service['replicas'] = 1
for edge in model['edges']:
    for field in ('metadata', 'observed', 'resilience'):
        edge.pop(field, None)
for endpoint in model['endpoints']:
    endpoint.pop('metadata', None)
edge = next(e for e in model['edges'] if e['from'] == 'gateway' and e['to'] == 'checkout')
later = next(e for e in model['edges'] if e['from'] == 'checkout' and e['to'] == 'payment')
endpoint = next(e for e in model['endpoints'] if e['entry_service'] == 'gateway')
binding = {'entry_service': 'gateway', 'mandatory_targets': ['checkout'],
           'required_edges': [edge['id']], 'endpoints': [endpoint['id']]}
tool = Toolchain.__new__(Toolchain)
tool.ctx = Context(root / 'commands', 'full', 9)
tool.bin = (build / 'bin').resolve()
tool.inventory = {'replicas': [{'node': 'a'}, {'node': 'b'}]}
tool.static_overlay = lambda *_: ([], [])
tool.correction_origin_source = 'native'
mapping = {'matched_observed_nodes': ['payment']}
primary = simulate(tool, model, {}, binding, 'checkout', mapping, 'synthetic-ACK', 'primary', root / 'primary')
assert primary['values'] == {'state-11': 1, 'state-10': 1, 'state-01': 1, 'state-00': 0}
masked = simulate(tool, model, {}, binding, 'checkout', mapping, 'synthetic-ACK', 'database_down', root / 'masked')
assert masked['values'] == {'db-down': 1}
all_calls = {**binding, 'mandatory_targets': ['checkout', 'payment'],
             'required_edges': [edge['id'], later['id']]}
unmasked = simulate(tool, model, {}, all_calls, 'checkout', mapping, 'synthetic-ACK', 'database_down', root / 'unmasked')
assert unmasked['values'] == {'db-down': 0}
write_json(root / 'qualification.json', {'kind': 'synthetic_real_product_ABI_only',
    'source': os.environ['GITHUB_SHA'], 'status': 'complete',
    'fixture_source_sha256': digest(source), 'pins': PINS,
    'primary': primary, 'masked': masked, 'unmasked': unmasked,
    'scientific_success_claim': False})
