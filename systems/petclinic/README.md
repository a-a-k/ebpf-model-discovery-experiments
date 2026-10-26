# Spring Petclinic Microservices adapter

This adapter builds upstream `spring-petclinic-microservices` commit
`3858f9c630cf989bb6809a86edf47c2be78dc9f1` and deploys it on the two Ubuntu
24.04 guests. Application builds, deployment, and requests are rejected outside
GitHub Actions.

## Placement and routing

Node A hosts the API gateway, customers and vets services, MySQL, HAProxy, Visits
replica A, and an OTLP collector on `172.28.11.0/24`. Node B hosts Visits replica
B and a second collector on `172.28.12.0/24`. Every container has a fixed address.
HAProxy at `172.28.11.13` has an unchanging round-robin backend list containing
`172.28.11.14:8080` and node B's stable published endpoint
`192.168.76.12:18081`, which DNATs to the fixed `172.28.12.14:8080` container.
Visits B reaches MySQL through node A's stable `192.168.76.11:13306` publication.
These explicit guest endpoints avoid dependence on Docker's cross-bridge forwarding
rules while preserving container identity, independent guest kernels, and observable
cross-node TCP calls. `set_replicas` stops or starts only the Visits containers and
never rewrites routing. Resolved Compose files and `placement.json` are retained.

The previously qualified SIMPAT image was a GitHub Actions artifact and may be
expired or require credentials. A workflow may provide an already restored public
or otherwise authorized archive via `PETCLINIC_IMAGE_ARCHIVE`. Without it, the
adapter rebuilds the pinned source, pinned Java base, and digest-verified Java
agent remotely and records `rebuild_from_pinned_source`; it does **not** claim the
new image is byte-identical to the historical artifact.

## Operations and external oracles

The four operations are `list_owners`, `owner_details_with_visits`,
`create_visit`, and `list_vets`. Read results are compared field-by-field with an
oracle derived from pinned upstream seed SQL. In particular, owner detail must
contain the two expected pets and all four expected visits; HTTP 200 alone is not
success.

Create-visit uses the pinned gateway's single POST retry on HTTP 503. Each request
has a unique `ebpf-study-<sha256>` description. HTTP 201 leaves success pending;
`verify` independently queries MySQL once per block for all attempt markers and
requires exactly one row whose returned ID, pet ID 1, date `2026-09-01`, and
description all match. The synchronous committed rows need no live polling. This
local database census has no workload HTTP step or request header. Reset deletes
only these synthetic rows. No response, manifest, or expected topology is supplied
as learner evidence.

## Native tracing

`absent` omits `-javaagent` and sets `OTEL_SDK_DISABLED=true` in every application.
`partial` instruments gateway/customers/vets but omits the agent and disables the
SDK in both controlled Visits replicas. `full` instruments all application
processes. Spring/Micrometer exporters are disabled in all modes so the declared
mode is not bypassed. Native server spans capture the opaque
`X-Experiment-Request-Id`; the workload does not inject `traceparent` or any other
native trace context. Each guest writes native OTLP JSON separately. A collection
snapshot gracefully stops and flushes each collector, copies its cumulative file,
restarts it, waits for OTLP readiness, and checks that the file was not truncated,
so the same method is safe after calibration and at campaign end. The snapshot
also counts actual spans by `service.name`: absent mode fails on any application
span, partial mode fails on any Visits span, and partial/full remain `unknown` when
required service evidence is unavailable. Collection retains inspected
commands/environments as supporting configuration evidence. The main eBPF
collector and inference remain orchestrator-owned.

Limitations: the deployment uses two VMs on one Actions runner; the source rebuild
is reproducible by inputs but not claimed bit-reproducible; and an unavailable SQL
oracle yields an unknown create-visit result rather than inferring persistence from
HTTP alone.
