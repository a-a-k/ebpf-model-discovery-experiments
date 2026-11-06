"""Tiny fake-guest checks: no VM, application build, network, or traffic."""
import hashlib
import json
from pathlib import Path
import shlex
import shutil
from types import SimpleNamespace

import pytest
import yaml

from ebpf_discovery import deployment_v6 as d


IDS = {n: "sha256:" + ("a" if n == "a" else "b") * 64 for n in d.NODES}


class FakeContext:
    def __init__(self, repo, name):
        self.repo_dir, self.out = repo, repo / "work" / name
        self.out.mkdir(parents=True)
        self.deployment_dir = self.out / "deployment"
        self.deployment_dir.mkdir()
        self.mode, self.seed, self.collector = "absent", 9, "none"
        self.commands, self.remote, self.agent = [], {}, False

    def node_put(self, node, source, target):
        source = Path(source)
        if source.is_dir():
            for path in source.rglob("*"):
                if path.is_file():
                    self.remote[node, target + "/" + path.relative_to(source).as_posix()] = path.read_bytes()
        else:
            self.remote[node, target] = source.read_bytes()

    def node_get(self, node, source, target):
        Path(target).write_bytes(self.remote[node, source])

    def node_exec(self, node, command, **kwargs):
        self.commands.append((node, command))
        out = ""
        if command == "ps -eo comm=":
            out = "obi" if self.agent else "systemd\ndockerd"
        elif command in ("docker ps -a -q", "docker image ls -q", "docker volume ls -q"):
            out = ""
        elif command.startswith("df "):
            out = str(10**12)
        elif "config --format json" in command:
            base = yaml.safe_load((self.deployment_dir / "otel_demo" / f"node-{node}.yaml").read_text())
            if "v6-images-" in command:
                override = json.loads(self.remote[node, f"/opt/ebpf-study/otel_demo/v6-images-{node}.json"])
                for name, spec in override["services"].items():
                    base["services"][name].update(spec)
            out = json.dumps(base)
        elif command.startswith("docker image inspect --format"):
            out = shlex.split(command)[-1]
        elif command.startswith("docker image inspect "):
            out = json.dumps([{"Id": IDS[node], "Size": 1024, "RepoDigests": ["tiny@" + IDS[node]]}])
        elif "docker image save -o " in command:
            name = shlex.split(command.split("docker image save -o ", 1)[1])[0]
            self.remote[node, name] = ("TINY IMAGE " + IDS[node]).encode()
        elif command.startswith("python3 -c "):
            name = next(path for n, path in self.remote if n == node and path.endswith(".tar"))
            body = self.remote[node, name]
            out = json.dumps({"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        elif command.endswith("ps -a -q"):
            out = "c" * 64
        elif command.startswith("docker inspect "):
            service = "checkout" if node == "a" else "backend"
            out = json.dumps([{"Config": {"Labels": {"com.docker.compose.service": service}},
                               "Image": IDS[node], "HostConfig": {"Memory": d.CHECKOUT_MEMORY_BYTES if node == "a" else 0}}])
        return SimpleNamespace(stdout=out, returncode=0)


class TinyAdapter:
    def __init__(self, ctx):
        self.ctx, self.bundle = ctx, ctx.deployment_dir / "otel_demo"

    def prepare(self):
        self.bundle.mkdir()
        for node, name in (("a", "checkout"), ("b", "backend")):
            (self.bundle / f"node-{node}.yaml").write_text(yaml.safe_dump(
                {"services": {name: {"image": "floating:old-tag", "mem_limit": 20 * 1024**2 if node == "a" else 0}}}))
        (self.bundle / "native").mkdir()
        (self.bundle / "native" / "bootstrap-traces.json").write_text("MUST NEVER ENTER AN ARM")
        (self.bundle / "source-fixture.json").write_text("KEEP IMMUTABLE FIXTURE")

    def deploy(self):
        self.ctx.commands.append(("bootstrap", "ONE ORIGINAL DEPLOY"))

    def metadata(self):
        return {"original_adapter": True}

    def _suppression_description(self):
        return {"mode": self.ctx.mode, "same_original_sdk_guard": True}


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("PETCLINIC_IMAGE_ARCHIVE", raising=False)
    monkeypatch.setattr(d, "get_adapter", lambda ctx, system: TinyAdapter(ctx))
    ctx = FakeContext(tmp_path, "preparation")
    cache = tmp_path / "work" / "blueprint"
    return ctx, cache


@pytest.mark.parametrize('mode', ['absent', 'partial', 'full'])
def test_real_otel_adapter_constructor_uses_uniform_guard_builds_in_every_mode(tmp_path, mode):
    ctx = SimpleNamespace(mode=mode, deployment_dir=tmp_path,
                          node_ip=lambda node: '192.168.76.11' if node == 'a' else '192.168.76.12')
    adapter = d.get_adapter(ctx, 'otel_demo')
    assert ctx.v6_build_all_native_guards is True
    assert type(adapter).__module__ == 'systems.otel_demo.experiment_v5'
    assert not list(tmp_path.iterdir())


def test_frozen_blueprint_uses_actual_images_and_never_rebuilds_or_leaks_bootstrap(setup):
    ctx, cache = setup
    prepared = d.prepare_blueprint(ctx, "otel_demo", cache)
    seal = prepared.v6_blueprint_sha256
    value = json.loads((cache / "blueprint.json").read_text())
    assert set(value["images"]) == set(IDS.values())
    assert value["checkout_memory_bytes"] == 128 * 1024**2
    assert not list((cache / "assets" / "native").iterdir())
    assert (cache / "assets" / "source-fixture.json").read_text() == "KEEP IMMUTABLE FIXTURE"
    for arm in ("none", "obi", "coroot", "deepflow"):
        fresh = FakeContext(ctx.repo_dir, "arm-" + arm)
        fresh.collector = arm
        adapter = d.deploy_blueprint(fresh, "otel_demo", cache, expected_sha256=seal)
        assert adapter.v6_blueprint_sha256 == seal
        up = [command for _, command in fresh.commands if " up " in command]
        assert len(up) == 2 and all("--no-build --pull never" in c for c in up)
        assert not any("image save" in c or " pull " in c or " build " in c for _, c in fresh.commands)
        assert len([c for _, c in fresh.commands if c.startswith("docker tag ")]) == 2
        assert not list((adapter.bundle / "native").iterdir())
        assert any("suppression.json" in c for _, c in fresh.commands)
        receipt = json.loads((fresh.out / "v6-blueprint-deployment.json").read_text())
        assert receipt["status"] == "complete" and receipt["ended_ns"] >= receipt["started_ns"]


@pytest.mark.parametrize("mutation", ["wrong_seal", "asset", "image", "mode", "seed"])
def test_modified_or_cross_block_inputs_fail_closed_and_retain_cost(setup, mutation):
    ctx, cache = setup
    seal = d.prepare_blueprint(ctx, "otel_demo", cache).v6_blueprint_sha256
    fresh = FakeContext(ctx.repo_dir, "bad-" + mutation)
    if mutation == "wrong_seal":
        seal = "0" * 64
    elif mutation == "asset":
        (cache / "assets" / "node-a.yaml").write_text("services: {}")
    elif mutation == "image":
        next((cache / "images").iterdir()).write_bytes(b"changed image")
    elif mutation == "mode":
        fresh.mode = "full"
    else:
        fresh.seed = 10
    with pytest.raises(ValueError):
        d.deploy_blueprint(fresh, "otel_demo", cache, expected_sha256=seal)
    receipt = json.loads((fresh.out / "v6-blueprint-deployment.json").read_text())
    assert receipt["status"] == "failed" and receipt["ended_ns"] >= receipt["started_ns"]
    assert not any("docker load" in c or " up " in c for _, c in fresh.commands)


def test_existing_blueprint_or_deployment_never_replaced(setup):
    ctx, cache = setup
    seal = d.prepare_blueprint(ctx, "otel_demo", cache).v6_blueprint_sha256
    with pytest.raises(FileExistsError):
        d.prepare_blueprint(ctx, "otel_demo", cache)
    fresh = FakeContext(ctx.repo_dir, "already-present")
    (fresh.deployment_dir / "otel_demo").mkdir()
    with pytest.raises(FileExistsError):
        d.deploy_blueprint(fresh, "otel_demo", cache, expected_sha256=seal)


def test_preparatory_agent_rejected_before_build(setup):
    ctx, cache = setup
    ctx.agent = True
    with pytest.raises(RuntimeError, match="agent"):
        d.prepare_blueprint(ctx, "otel_demo", cache)
    assert not any(c == "ONE ORIGINAL DEPLOY" for _, c in ctx.commands)


def test_preexisting_application_state_rejected_before_build(setup):
    ctx, cache = setup
    original = ctx.node_exec
    ctx.node_exec = lambda node, command, **kw: (SimpleNamespace(stdout="old-volume")
        if command == "docker volume ls -q" else original(node, command, **kw))
    with pytest.raises(ValueError, match="new empty golden"):
        d.prepare_blueprint(ctx, "otel_demo", cache)
    assert not any(c == "ONE ORIGINAL DEPLOY" for _, c in ctx.commands)


def test_actual_host_and_guest_capacity_boundaries(setup, monkeypatch):
    ctx, cache = setup
    monkeypatch.setattr(d.shutil, "disk_usage", lambda path: SimpleNamespace(free=d.HOST_RESERVE + 5))
    assert d._host_space(ctx.out, 5)["incoming_bytes"] == 5
    with pytest.raises(OSError):
        d._host_space(ctx.out, 6)
    ctx.node_exec = lambda *a, **k: SimpleNamespace(stdout=str(d.GUEST_RESERVE + 5))
    assert d._guest_space(ctx, "a", 5)["incoming_bytes"] == 5
    with pytest.raises(OSError):
        d._guest_space(ctx, "a", 6)


def test_actions_and_fresh_seed_guards(setup, monkeypatch):
    ctx, cache = setup
    monkeypatch.delenv("GITHUB_ACTIONS")
    with pytest.raises(RuntimeError):
        d.prepare_blueprint(ctx, "otel_demo", cache)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    ctx.seed = 8
    with pytest.raises(ValueError):
        d.prepare_blueprint(ctx, "otel_demo", cache)
    assert not ctx.commands


def test_only_known_native_export_dirs_are_empty_but_config_and_fixture_remain(tmp_path):
    bundle = tmp_path / "assets"
    for node in d.NODES:
        native = bundle / f"node-{node}" / "native"
        native.mkdir(parents=True)
        (native / "old-export").write_text("discard")
        (native.parent / "fixture.json").write_text("retain")
    target = tmp_path / "copied"
    shutil.copytree(bundle, target, ignore=d._without_exports(bundle, "petclinic"))
    for node in d.NODES:
        assert not list((target / f"node-{node}" / "native").iterdir())
        assert (target / f"node-{node}" / "fixture.json").read_text() == "retain"
