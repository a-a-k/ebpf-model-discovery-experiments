from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from systems.deathstarbench.experiment_v4 import entry_identity_groups


LOADER = ('opentracing_load_tracer /usr/local/lib/libjaegertracing_plugin.so '
          '/usr/local/openresty/nginx/jaeger-config.json;')
MOUNTS = [
    './nginx-web-server/conf/nginx.conf:/usr/local/openresty/nginx/conf/nginx.conf',
    './nginx-web-server/jaeger-config.json:/usr/local/openresty/nginx/jaeger-config.json',
]


def retained_fixture(root: Path):
    node = root/'deathstarbench'/'node-a'
    conf = node/'nginx-web-server'/'conf'/'nginx.conf'
    config = node/'nginx-web-server'/'jaeger-config.json'
    compose = node/'docker-compose.yml'
    conf.parent.mkdir(parents=True)
    compose.write_text(yaml.safe_dump({'services': {'nginx-thrift': {
        'container_name': 'dsb-nginx-thrift', 'hostname': 'nginx-thrift',
        'ports': ['8080:8080'], 'volumes': MOUNTS,
    }}}), encoding='utf-8')
    conf.write_text('opentracing on;\n'+LOADER+'\n', encoding='utf-8')
    config.write_text(json.dumps({'service_name': 'nginx-web-server'}), encoding='utf-8')
    return compose, conf, config


def test_exact_retained_mount_loader_and_config_prove_entry_aliases(tmp_path: Path):
    paths = retained_fixture(tmp_path)
    groups = entry_identity_groups(tmp_path)
    assert len(groups) == 1
    group = groups[0]
    assert group['aliases'] == ['nginx-thrift', 'nginx-web-server']
    assert group['scope'] == 'entry representation only; same declared container/listener; entry fixed fulfilled'
    assert len(group['proof']) == 7
    for item in group['proof']:
        path = tmp_path/item['relative_path']
        assert path in paths
        assert item['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert [p for p in group['proof'] if p['pointer'] == '/service_name'][0]['observed_value'] == 'nginx-web-server'
    assert any(p['pointer'] == 'line:2' and p['observed_value'] == LOADER for p in group['proof'])


@pytest.mark.parametrize('damage', [
    'missing-config', 'wrong-service-name', 'wrong-container', 'wrong-hostname',
    'wrong-listener', 'wrong-config-mount', 'duplicate-config-mount',
    'missing-nginx-mount', 'wrong-loader',
])
def test_no_entry_alias_group_when_proof_chain_is_broken(tmp_path: Path, damage: str):
    compose, conf, config = retained_fixture(tmp_path)
    if damage == 'missing-config':
        config.unlink()
    elif damage == 'wrong-service-name':
        config.write_text(json.dumps({'service_name': 'another-service'}))
    elif damage in ('wrong-container', 'wrong-hostname', 'wrong-listener',
                    'wrong-config-mount', 'duplicate-config-mount', 'missing-nginx-mount'):
        document = yaml.safe_load(compose.read_text())
        service = document['services']['nginx-thrift']
        if damage == 'wrong-container':
            service['container_name'] = 'another-container'
        elif damage == 'wrong-hostname':
            service['hostname'] = 'another-host'
        elif damage == 'wrong-listener':
            service['ports'] = ['8081:8080']
        elif damage == 'wrong-config-mount':
            service['volumes'][1] = './other.json:/usr/local/openresty/nginx/jaeger-config.json'
        elif damage == 'duplicate-config-mount':
            service['volumes'].append(MOUNTS[1])
        else:
            service['volumes'].pop(0)
        compose.write_text(yaml.safe_dump(document))
    else:
        conf.write_text('opentracing on;\n# '+LOADER+'\n')
    assert entry_identity_groups(tmp_path) == []
