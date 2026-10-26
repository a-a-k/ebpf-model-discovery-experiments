# OpenTelemetry Demo adapter

This adapter deploys the pinned OpenTelemetry Demo 3.0.0 source commit
`8c47d47c9ac27710d2b2a153bcd53e483bffe66d` across two Ubuntu 24.04 guests.
It loads both `compose.yaml` and `compose.full.yaml`; consequently checkout's
real Kafka producer, Kafka, accounting consumer, and PostgreSQL persistence are
active. It intentionally omits the demo load generator and observability UI
services because experiment traffic and retained evidence are controlled by the
study runner.

## Placement and routing

Guest A runs the application, databases, Kafka/accounting, collector, a fixed
Envoy product-catalog endpoint, and replica A (`172.28.11.21`). Guest B runs
replica B (`172.28.12.21`). Envoy at `172.28.11.20:3550` always uses the same
round-robin policy and active gRPC health checks. Replica state changes only
stop or start the selected backends; they never rewrite routing. All containers
have recorded stable addresses, and guest B reaches collector, flagd, and
PostgreSQL over the routed application subnets.

## Native tracing modes

`full` retains native spans from every service. `partial` disables native SDK
export in both controlled product-catalog replicas. `absent` applies that setting
to every application service. Disabled containers receive
`OTEL_SDK_DISABLED=true` and `OTEL_TRACES_EXPORTER=none` (plus disabled metrics).
Some Go programs construct providers directly and can ignore those environment
settings, so the remote collector independently filters all forbidden spans.
This guard does not alter request handling and allows context propagation. The
adapter inspects the final collector file and fails collection when the selected
mode leaked forbidden native spans. OTel logs, metrics, Docker application logs,
and common eBPF evidence remain separate artifacts.

## Operations and independent outcomes

The three API operations follow the Apache-2.0-licensed SIMPAT live workload:
product browse, add one fixed catalog item to a unique cart, and checkout that
cart with unique synthetic identity data. HTTP status and response bytes are
evaluator evidence only. Checkout extracts the application's actual `orderId`.
Every HTTP step carries a fresh opaque `X-Experiment-Request-Id`, retained with
the evaluator step so common acquisition can align entry observations without
encoding an operation label, dependency, or result.
Checkout reaches only the demo's packaged mock email service; the adapter has no
mail credentials and never sends external mail.
It does **not** infer Kafka delivery from the HTTP response or producer state;
the upstream producer uses `RequiredAcks=NoResponse`.

`verify_async` performs separately timestamped PostgreSQL reads keyed by that
returned order ID and retains every poll. Success requires the order row, at
least one matching item, and the shipping row within the independent 10-second
deadline. While paused, accounting remains stopped through the last registered
deadline. Recovery starts accounting and blocks until Kafka consumer-group lag
is zero, so the backlog drains before the recovered control begins. The database
schema and catalog fixture come from the pinned upstream PostgreSQL initializer.

## Limitations

The Envoy endpoint is experiment deployment metadata, not learner input or an
expected dependency graph. SQL census is evaluator-only evidence. This adapter
does not invent Kafka message identity links: absence of a confirmed identity
chain remains unknown to the common inference code. Images, source acquisition,
guest launches, application traffic, and builds are intended only for GitHub
Actions; local use is limited to static and focused unit checks.
