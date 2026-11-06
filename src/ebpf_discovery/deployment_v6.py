"""One new application blueprint per v6 block; restore it without pull/build.

Execution is Actions-only. The caller supplies fresh, provisioned guests and
starts no eBPF collector until prepare_blueprint has finished. The blueprint
contains images/configuration, never a running application's data volumes.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import time
from typing import Any

import yaml


SYSTEMS = {"deathstarbench", "otel_demo", "petclinic"}
NODES = ("a", "b")
SCHEMA = "v6-frozen-application-blueprint-v1"
HOST_RESERVE = 2 * 1024**3
GUEST_RESERVE = 256 * 1024**2
CHECKOUT_MEMORY_BYTES = 128 * 1024**2
IMAGE_ID = re.compile(r"sha256:[0-9a-f]{64}\Z")
AGENT_NAMES = {"obi", "beyla", "coroot-node-agent", "coroot-node-age", "deepflow-agent"}


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _stdout(result: Any) -> str:
    return str(result.stdout)


def _guard(ctx: Any, system: str) -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("v6 deployment execution is GitHub Actions only")
    if system not in SYSTEMS or ctx.mode not in {"absent", "partial", "full"}:
        raise ValueError("unknown v6 system or SDK mode")
    if type(ctx.seed) is not int or ctx.seed not in {9, 10, 11}:
        raise ValueError("v6 uses only fresh seeds 9/10/11")


def get_adapter(ctx: Any, system: str) -> Any:
    """Use the exact v5 scientific adapters; this module only freezes deployment."""
    if system not in SYSTEMS:
        raise ValueError("unknown v6 system")
    if system == "otel_demo":
        ctx.v6_build_all_native_guards = True
    version = "experiment_v5" if system == "otel_demo" else "experiment_v4"
    return importlib.import_module(f"systems.{system}.{version}").Adapter(ctx)


def _bundle(adapter: Any, system: str) -> Path:
    return Path(getattr(adapter, {"otel_demo": "bundle", "deathstarbench": "root",
                                  "petclinic": "assets"}[system]))


def _layout(system: str, node: str) -> tuple[str, str, str]:
    remote = f"/opt/ebpf-study/{system}"
    if system == "otel_demo":
        return remote, f"{remote}/node-{node}.yaml", "ebpf-otel-demo"
    if system == "deathstarbench":
        return remote, f"{remote}/node-{node}/docker-compose.yml", "dsb-ebpf-study"
    return remote, f"{remote}/node-{node}/compose.yml", f"petclinic-{node}"


def _compose(system: str, node: str, arguments: str, *, frozen: bool = True) -> str:
    remote, compose, project = _layout(system, node)
    override = f" -f {remote}/v6-images-{node}.json" if frozen else ""
    return (f"docker compose -p {project} -f {compose}{override} {arguments}")


def _tree(root: Path) -> dict[str, dict[str, Any]]:
    """Fail closed on links/devices rather than silently changing an asset tree."""
    claims = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"blueprint contains a symlink: {path}")
        if path.is_file():
            claims[path.relative_to(root).as_posix()] = {
                "bytes": path.stat().st_size, "sha256": _sha(path)}
        elif not path.is_dir():
            raise ValueError(f"blueprint contains a nonregular file: {path}")
    return claims


def _cache_path(ctx: Any, directory: Path | str) -> Path:
    supplied = Path(directory).absolute()
    if any(p.is_symlink() for p in (supplied, *supplied.parents)):
        raise ValueError("blueprint path cannot contain symlinks")
    path = supplied.resolve()
    workspace = Path(ctx.repo_dir).resolve() / "work"
    if not path.is_relative_to(workspace) or path == workspace:
        raise ValueError("blueprint must be inside this checkout's work directory")
    return path


def _host_space(path: Path, incoming: int) -> dict[str, int]:
    free = shutil.disk_usage(path).free
    if free < incoming + HOST_RESERVE:
        raise OSError("insufficient actual host space for frozen application images")
    return {"free_bytes": free, "incoming_bytes": incoming, "reserve_bytes": HOST_RESERVE}


def _guest_space(ctx: Any, node: str, incoming: int) -> dict[str, int]:
    free = int(_stdout(ctx.node_exec(node, "df -B1 --output=avail /opt | tail -n1")).strip())
    if free < incoming + GUEST_RESERVE:
        raise OSError(f"insufficient actual guest {node} image space")
    return {"free_bytes": free, "incoming_bytes": incoming, "reserve_bytes": GUEST_RESERVE}


def _no_agents(ctx: Any) -> None:
    if getattr(ctx, "collector", "none") != "none":
        raise ValueError("prepare the common blueprint with collector=none")
    for node in NODES:
        names = _stdout(ctx.node_exec(node, "ps -eo comm=")).split()
        containers = _stdout(ctx.node_exec(node, "docker ps -a --format '{{.Names}} {{.Image}}'"))
        if AGENT_NAMES.intersection(names) or any(
                token in containers.lower() for token in
                ("coroot-node-agent", "deepflow-agent", "ebpf-obi", "otel-ebpf-instrumentation")):
            raise RuntimeError("an eBPF agent is present in the preparatory deployment")


def _empty_preparatory_guests(ctx: Any) -> None:
    for node in NODES:
        for query in ("docker ps -a -q", "docker image ls -q", "docker volume ls -q"):
            if _stdout(ctx.node_exec(node, query)).strip():
                raise ValueError("blueprint preparation requires new empty golden guests")


def _healthy_checkout(bundle: Path) -> None:
    path = bundle / "node-a.yaml"
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    service = value["services"]["checkout"]
    # Compose deploy.resources.limits.memory requires a byte-value string.
    # Decimal bytes also keep the service-level and deploy-level limits equal.
    service["mem_limit"] = str(CHECKOUT_MEMORY_BYTES)
    limits = service.get("deploy", {}).get("resources", {}).get("limits")
    if limits is not None:
        limits["memory"] = str(CHECKOUT_MEMORY_BYTES)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    _json(bundle / "v6-uniform-checkout-budget.json", {
        "bytes": CHECKOUT_MEMORY_BYTES, "scope": "all four arms, both epochs, every SDK mode",
        "old20MiB_fault_repair": True, "healthy_budget_still_requires_qualification": True})


def _copy_remote_assets(ctx: Any, adapter: Any, system: str) -> None:
    bundle = _bundle(adapter, system)
    for node in NODES:
        remote, _, _ = _layout(system, node)
        ctx.node_exec(node, f"sudo mkdir -p {remote} && sudo chown $(id -u):$(id -g) {remote}")
        if system == "otel_demo":
            ctx.node_put(node, bundle, remote)
        else:
            ctx.node_put(node, bundle / f"node-{node}", f"{remote}/node-{node}")
            ctx.node_put(node, bundle / f"v6-images-{node}.json",
                         f"{remote}/v6-images-{node}.json")


def _without_exports(bundle: Path, system: str):
    volatile = ({bundle / "native"} if system == "otel_demo" else
                {bundle / f"node-{node}" / "native" for node in NODES})
    return lambda directory, names: list(names) if Path(directory) in volatile else []


def _census(ctx: Any, system: str, node: str) -> dict[str, dict[str, Any]]:
    ids = _stdout(ctx.node_exec(node, _compose(system, node, "ps -a -q"))).split()
    if not ids or any(not re.fullmatch("[0-9a-f]{12,64}", cid) for cid in ids):
        raise ValueError("frozen deployment has no unambiguous compose containers")
    rows = json.loads(_stdout(ctx.node_exec(node, "docker inspect " + " ".join(ids))))
    result = {}
    for row in rows:
        service = row["Config"]["Labels"]["com.docker.compose.service"]
        if service in result or not IMAGE_ID.fullmatch(row["Image"]):
            raise ValueError("duplicate service or invalid running image ID")
        result[service] = {"image_id": row["Image"],
                           "memory_bytes": row["HostConfig"]["Memory"]}
    return result


def _prepare_blueprint(ctx: Any, system: str, cache_dir: Path | str, started: int) -> Any:
    """Build/pull once on NEW collector-free guests, then seal portable image inputs.

    Caller must discard these preparatory guests and use fresh clones for every
    scored arm. Do not call this function on validation or a historical cache.
    """
    _guard(ctx, system)
    if os.environ.get("PETCLINIC_IMAGE_ARCHIVE", "").strip():
        raise ValueError("v6 never imports a historical Petclinic image override")
    cache = _cache_path(ctx, cache_dir)
    if cache.exists():
        raise FileExistsError("never rebuild or replace an existing v6 blueprint")
    cache.mkdir(parents=True)
    _no_agents(ctx)
    _empty_preparatory_guests(ctx)
    adapter = get_adapter(ctx, system)
    if _bundle(adapter, system).exists():
        raise FileExistsError("preparation requires new assets, not a historical deployment")
    adapter.prepare()
    bundle = _bundle(adapter, system)
    if system == "otel_demo":
        _healthy_checkout(bundle)
    adapter.deploy()
    _no_agents(ctx)
    images: dict[str, dict[str, Any]] = {}
    nodes = {}
    for node in NODES:
        config = json.loads(_stdout(ctx.node_exec(
            node, _compose(system, node, "config --format json", frozen=False))))
        services = config.get("services") or {}
        if not services:
            raise ValueError("compose has no services")
        role_images, override = {}, {"services": {}}
        for service, settings in sorted(services.items()):
            image_ref = settings.get("image")
            if not isinstance(image_ref, str) or not image_ref:
                raise ValueError("every service must resolve to an actual local image")
            info = json.loads(_stdout(ctx.node_exec(
                node, "docker image inspect " + shlex.quote(image_ref))))[0]
            image_id = info["Id"]
            if not IMAGE_ID.fullmatch(image_id) or type(info["Size"]) is not int or info["Size"] <= 0:
                raise ValueError("invalid actual Docker image identity")
            tag = f"ebpf-v6-{system}:{image_id[7:]}"
            ctx.node_exec(node, f"docker tag {image_id} {tag}")
            role_images[service] = {"image_id": image_id, "frozen_tag": tag}
            override["services"][service] = {"image": tag, "pull_policy": "never"}
            if image_id in images:
                continue
            temporary = f"/opt/ebpf-study/v6-image-{image_id[7:]}.tar"
            guard = _guest_space(ctx, node, 2 * info["Size"])
            ctx.node_exec(node, f"test ! -e {temporary} && test ! -L {temporary} && "
                          f"docker image save -o {temporary} {image_id}", timeout=1800)
            archive_meta = json.loads(_stdout(ctx.node_exec(node,
                "python3 -c " + shlex.quote(
                    "import hashlib,json,pathlib; "
                    f"p=pathlib.Path({temporary!r}); "
                    "print(json.dumps({'bytes':p.stat().st_size,"
                    "'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()}))"))))
            if (type(archive_meta["bytes"]) is not int or archive_meta["bytes"] <= 0
                    or not re.fullmatch("[0-9a-f]{64}", archive_meta["sha256"])):
                raise ValueError("invalid actual saved-image archive metadata")
            target = cache / "images" / (image_id[7:] + ".tar")
            target.parent.mkdir(exist_ok=True)
            host_guard = _host_space(cache, archive_meta["bytes"])
            ctx.node_get(node, temporary, target)
            if target.stat().st_size != archive_meta["bytes"] or _sha(target) != archive_meta["sha256"]:
                raise ValueError("saved image transfer differs from actual guest bytes")
            ctx.node_exec(node, f"test -f {temporary} && test ! -L {temporary} && rm -- {temporary}")
            images[image_id] = {**archive_meta, "archive": target.relative_to(cache).as_posix(),
                                "image_size_bytes": info["Size"], "source_node": node,
                                "guest_guard": guard, "host_guard": host_guard,
                                "repo_digests": info.get("RepoDigests") or []}
        _json(bundle / f"v6-images-{node}.json", override)
        ctx.node_put(node, bundle / f"v6-images-{node}.json",
                     f"{_layout(system, node)[0]}/v6-images-{node}.json")
        resolved = json.loads(_stdout(ctx.node_exec(
            node, _compose(system, node, "config --format json"))))
        nodes[node] = {"services": role_images, "resolved_compose": resolved,
                       "runtime_services": _census(ctx, system, node)}
    _host_space(cache, sum(p.stat().st_size for p in bundle.rglob("*") if p.is_file()))
    shutil.copytree(bundle, cache / "assets", symlinks=True,
                    ignore=_without_exports(bundle, system))
    claims = _tree(cache / "assets")
    manifest = {"schema": SCHEMA, "system": system, "mode": ctx.mode, "seed": ctx.seed,
                "preparation_collector": "none", "started_ns": started,
                "ended_ns": time.time_ns(), "images": images, "nodes": nodes,
                "assets": claims, "adapter_metadata": adapter.metadata(),
                "uniform_native_guard_builds": system == "otel_demo",
                "native_guard_build_path": ["checkout", "email", "product-catalog", "currency", "shipping"]
                    if system == "otel_demo" else None,
                "checkout_memory_bytes": CHECKOUT_MEMORY_BYTES if system == "otel_demo" else None}
    _json(cache / "blueprint.json", manifest)
    adapter.v6_blueprint_sha256 = _sha(cache / "blueprint.json")
    return adapter


def prepare_blueprint(ctx: Any, system: str, cache_dir: Path | str) -> Any:
    """Build once with no agents; expose adapter.v6_blueprint_sha256 for handoff."""
    _guard(ctx, system)
    started = time.time_ns()
    record = {"started_ns": started, "status": "started", "system": system,
              "mode": ctx.mode, "seed": ctx.seed,
              "preparatory_guests_must_not_be_scored": True}
    path = Path(ctx.out) / "v6-blueprint-preparation.json"
    _json(path, record)
    try:
        adapter = _prepare_blueprint(ctx, system, cache_dir, started)
        record.update(status="complete", blueprint_sha256=adapter.v6_blueprint_sha256)
        return adapter
    except BaseException as error:
        record.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        record["ended_ns"] = time.time_ns()
        _json(path, record)


def _deploy_blueprint(ctx: Any, system: str, cache_dir: Path | str, expected_sha256: str) -> Any:
    """Restore identical source/config/images on fresh guests; never prepare/pull/build."""
    _guard(ctx, system)
    cache = _cache_path(ctx, cache_dir)
    manifest_path = cache / "blueprint.json"
    if not re.fullmatch("[0-9a-f]{64}", expected_sha256) or _sha(manifest_path) != expected_sha256:
        raise ValueError("common parent blueprint SHA differs")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("schema"), manifest.get("system"), manifest.get("mode"), manifest.get("seed")) != (
            SCHEMA, system, ctx.mode, ctx.seed):
        raise ValueError("blueprint belongs to another block/system/SDK mode")
    if manifest.get("preparation_collector") != "none" or _tree(cache / "assets") != manifest["assets"]:
        raise ValueError("blueprint assets changed")
    adapter = get_adapter(ctx, system)
    bundle = _bundle(adapter, system)
    if bundle.exists():
        raise FileExistsError("restore requires a fresh deployment directory")
    _host_space(cache, sum(row["bytes"] for row in manifest["assets"].values()))
    shutil.copytree(cache / "assets", bundle)
    if system == "petclinic":
        adapter.fixture = json.loads((bundle / "fixture.json").read_text())
        original = json.loads((bundle / "source-image-provenance.json").read_text())
        adapter._image_id = original["image_id"]
        adapter._source_mode = original["preparation"]
    elif system == "deathstarbench":
        adapter._mapping = json.loads((bundle / "container-ip-mapping.json").read_text())["services"]
    _copy_remote_assets(ctx, adapter, system)
    for node in NODES:
        project = _layout(system, node)[2]
        for query in ("docker ps -a -q", "docker volume ls -q"):
            if _stdout(ctx.node_exec(node, query + " --filter " +
                    shlex.quote("label=com.docker.compose.project=" + project))).strip():
                raise ValueError("fresh application containers/DB volumes required")
        ids = {x["image_id"] for x in manifest["nodes"][node]["services"].values()}
        for image_id in sorted(ids):
            row = manifest["images"][image_id]
            archive = cache / row["archive"]
            if (not IMAGE_ID.fullmatch(image_id) or archive.is_symlink()
                    or not archive.resolve().is_relative_to(cache)
                    or archive.stat().st_size != row["bytes"] or _sha(archive) != row["sha256"]):
                raise ValueError("frozen image archive changed")
            remote = f"/opt/ebpf-study/v6-image-{image_id[7:]}.tar"
            _guest_space(ctx, node, row["bytes"] + row["image_size_bytes"])
            ctx.node_exec(node, f"test ! -e {remote} && test ! -L {remote}")
            ctx.node_put(node, archive, remote)
            ctx.node_exec(node, f"docker load -i {remote} && test ! -L {remote} && rm -- {remote}",
                          timeout=1800)
            observed = _stdout(ctx.node_exec(
                node, "docker image inspect --format '{{.Id}}' " + image_id)).strip()
            if observed != image_id:
                raise ValueError("Docker load did not restore the frozen image ID")
            ctx.node_exec(node, f"docker tag {image_id} ebpf-v6-{system}:{image_id[7:]}")
        current = json.loads(_stdout(ctx.node_exec(
            node, _compose(system, node, "config --format json"))))
        if current != manifest["nodes"][node]["resolved_compose"]:
            raise ValueError("actual resolved deployment differs from common blueprint")
    if system == "deathstarbench":
        for node, suffix in (("a", 11), ("b", 12)):
            ctx.node_exec(node, f"docker network inspect dsb-app-{node} >/dev/null 2>&1 || "
                          f"docker network create --driver bridge --subnet 172.28.{suffix}.0/24 dsb-app-{node}")
    if system == "petclinic":
        ctx.node_exec("a", _compose(system, "a", "up -d --no-build --pull never database collector-a"), timeout=600)
        adapter._wait_database(180)
        adapter._wait_tcp("b", ctx.node_ip("a"), 13306, 60, "node-a published MySQL")
    for node in NODES:
        ctx.node_exec(node, _compose(system, node, "up -d --no-build --pull never"), timeout=900)
        observed = _census(ctx, system, node)
        if observed != manifest["nodes"][node]["runtime_services"]:
            raise ValueError("actual service images/memory differ from frozen blueprint")
        if system == "otel_demo" and node == "a" and observed.get("checkout", {}).get(
                "memory_bytes") != CHECKOUT_MEMORY_BYTES:
            raise ValueError("uniform healthy checkout memory budget did not take effect")
    if system == "otel_demo":
        suppression = json.dumps(adapter._suppression_description(), sort_keys=True)
        ctx.node_exec("a", "printf '%s\\n' " + shlex.quote(suppression) +
                      " > /opt/ebpf-study/otel_demo/native/suppression.json")
    adapter.v6_blueprint_sha256 = expected_sha256
    adapter.v6_deployment_fact = {
        "schema": SCHEMA, "system": system, "mode": ctx.mode, "seed": ctx.seed,
        "blueprint_sha256": _sha(manifest_path), "images": manifest["nodes"],
        "pulls": 0, "builds": 0, "new_volumes": True}
    return adapter


def deploy_blueprint(ctx: Any, system: str, cache_dir: Path | str, *,
                     expected_sha256: str) -> Any:
    """Use the same parent-sealed hash for all four arms and validation epoch."""
    _guard(ctx, system)
    record = {"started_ns": time.time_ns(), "status": "started", "system": system,
              "mode": ctx.mode, "seed": ctx.seed, "expected_sha256": expected_sha256}
    path = Path(ctx.out) / "v6-blueprint-deployment.json"
    _json(path, record)
    try:
        adapter = _deploy_blueprint(ctx, system, cache_dir, expected_sha256)
        record.update(adapter.v6_deployment_fact, status="complete")
        return adapter
    except BaseException as error:
        record.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        record["ended_ns"] = time.time_ns()
        _json(path, record)
