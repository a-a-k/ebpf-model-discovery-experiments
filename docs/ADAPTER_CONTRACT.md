# Application adapter interface

Each application exposes Adapter(context). The context supplies SDK mode, seed,
runner-local output and deployment paths, and guest execution, copy and address
helpers. The guests run Ubuntu 24.04 with Docker Compose. Downloads, application
builds, deployments and workload traffic execute in GitHub Actions.

## Lifecycle

- prepare(): resolve pinned sources/images and render the deployment assets.
- deploy(): instantiate both guests with the selected SDK configuration.
- ready(): check the services and initialize the declared clean fixtures.
- metadata(): record operations, transport addresses, logical and physical
  identities, selected replicas, database and source/image provenance.
- reset(): restore controlled services and workload preconditions.
- set_replicas(state): apply state 11, 10, 01 or 00 without changing routing.
- set_database(up): control the declared database service.
- operation(name, index, namespace): execute an operation with unique synthetic
  fixtures and retain response, content, timing and independent outcome evidence.
- verify(records): obtain payload/SQL postconditions while preserving unknowns.
- collect_native(destination): retain native telemetry and observed SDK coverage
  separately from eBPF input.
- close(): collect diagnostics and stop the owned deployment.

OTel additionally controls the consumer and verifies persistence using actual
application order identifiers and independent database observations. An
acknowledgement does not establish durable storage. Operations retain their
application behavior without an experiment-imposed outcome deadline.

Configuration and evaluator records remain separate from discovery input.
Response bodies, success labels and expected business topology are not supplied
as observation evidence. The recorded request marker is opaque. Actual native
and eBPF identifiers and ambiguous relationships remain explicit.
