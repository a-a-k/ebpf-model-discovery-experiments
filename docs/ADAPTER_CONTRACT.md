# System adapter contract v1

Workers implement `systems/<system>/adapter.py`, exporting `Adapter(context)`; system IDs are deathstarbench, otel_demo, petclinic. Modules use the standard library plus requests/PyYAML. Common context is supplied by the orchestrator.

## Context

- `ctx.mode`: absent/partial/full; `ctx.out`: runner-local pathlib.Path; `ctx.seed`: integer.
- `ctx.node_exec(node, command, timeout=300)`: run bash via SSH, return CompletedProcess; raise on nonzero by default. Nodes are `a` and `b`.
- `ctx.node_put(node, source, destination)`: copy a runner-local file/directory to the guest.
- `ctx.node_ip(node)`: guest address (a=192.168.76.11, b=192.168.76.12).
- `ctx.deployment_dir`: runner-local output/deployment directory; `ctx.repo_dir`: experiment source root.
- `ctx.run(command_list, cwd=None, timeout=300)`: runner-local subprocess with return code checking.

Guests run Ubuntu 24.04, Docker Compose and Python3; root-equivalent SSH user `ubuntu`. The host has Python3 and common dependencies. Each guest has a routed app subnet: a=172.28.11.0/24, b=172.28.12.0/24; guest routes and forwarding are prepared by common infrastructure. Use stable container IPs and extra_hosts for cross-node names. Save resolved compose files and IP/container mapping. The host runner can route to both app subnets. Source/archive downloads, application builds and requests happen only in Actions.

## Required methods

- `prepare()`: fetch pinned upstream sources/images, generate separate guest deployment assets. No model/expected graph is emitted as discovery input.
- `deploy()`: copy assets and start services across guests, with real tracing mode applied; record how SDKs/agents are disabled, not just exporters dropped.
- `ready()`: bounded readiness plus fixture initialization; raise a meaningful error when unavailable.
- `metadata() -> dict`: operations list, entry URL, concrete replica names/nodes/IPs, chosen DB identity/node/container, source/version/image information and native-export locations. Do not include expected business dependency graphs.
- `reset()`: restore replicas/DB, drain or reset workload state and outstanding work; bounded readiness.
- `set_replicas(state: str)`: one of 11,10,01,00; control the two replicas without silently changing the routing policy.
- `set_database(up: bool)`: control the registered DB.
- `operation(name: str, index: int, namespace: str, deadline: float=2.0) -> dict`: execute an existing operation with unique synthetic fixtures. Return JSON-serializable evaluator record with `operation`, `attempt_id`, `started_ns`, `ended_ns`, `success` (bool or null), `http_steps` (request/response/status/timing, original bytes base64 allowed), `error`, and any independent validation evidence. Do not use this evaluator record as native/eBPF observation. The orchestrator strips business labels and results from learner census.
- `verify(records: list[dict]) -> list[dict]`: obtain independent SQL/payload postconditions where needed, preserving uncertainty and original evidence. Can be a no-op for operations already independently verified.
- `collect_native(destination: Path)`: retain native application telemetry separately; absence itself must be verified.
- `close()`: collect diagnostics and stop only this campaign's services.

OTel additionally implements `set_consumer(up: bool)` and `verify_async(records, deadline=10.0)` using independent SQL observations and actual order IDs; no inference from successful produce/client response alone. Preserve primary timed SQL evidence. Polling must not miss deadline semantics; retain unknown if measurement does not settle it.

The worker may add focused helper files in its own system directory. Do not modify common workflow/runtime code; report interface needs to orchestrator. Preserve attribution and source provenance when reusing SIMPAT code. Write a system README explaining actual tracing suppression, placement, fixture/oracle and limitations. Never run applications locally.
