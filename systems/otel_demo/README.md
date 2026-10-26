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
have recorded stable addresses. Cross-guest transport does not assume Docker
bridge-subnet routing: replica B is published on guest B port `13550`, while
guest A publishes PostgreSQL on `15432`, native OTLP/gRPC on `14317`, and flagd
on `18013`. The generated metadata records both container identity and transport
host/port.

## Native tracing modes

`full` retains native spans from every service. `partial` disables native SDK
export in both controlled product-catalog replicas. `absent` applies that setting
to every application service. Disabled containers receive
`OTEL_SDK_DISABLED=true`. Checkout and product-catalog construct Go providers
directly, and email directly adds a metric reader to what becomes a no-op Ruby
provider, so `prepare()` applies a recorded source patch and the Actions guests
build those three images from the pinned checkout. The patch skips exporter/SDK
construction when disabled (checkout retains only a never-sample provider for
context propagation). The collector does not filter spans: its file export is
the raw native OTLP stream, and the adapter fails collection when that stream
contains forbidden native spans. This also audits that the standard disable
flag worked in the other language SDKs. OTel logs, metrics, Docker application logs,
and common eBPF evidence remain separate artifacts.

## Operations and independent outcomes

The three API operations follow the Apache-2.0-licensed SIMPAT live workload:
product browse, add one fixed catalog item to a unique cart, and checkout that
cart with unique synthetic identity data. HTTP status and response bytes are
evaluator evidence only. Checkout extracts the application's actual `orderId`.
Every HTTP step carries a fresh opaque `X-Experiment-Request-Id`, retained with
the evaluator step so common acquisition can align entry observations without
encoding an operation label, dependency, or result.
The frontend receives the standard Node HTTP-instrumentation environment
settings that request capture of this one header. The adapter neither creates
nor injects a sampled `traceparent`. Because header-capture support depends on
the instrumentation bundled in the pinned image, each native snapshot reports
whether the corresponding span attribute was actually observed; zero observed
attributes are reported as unsupported/unobserved, not treated as a link.
Checkout reaches only the demo's packaged mock email service; the adapter has no
mail credentials and never sends external mail.

Native collection is an incremental snapshot: the collector is gracefully
stopped and flushed, the append-only bind-mounted files are copied, and the same
collector is restarted before the call returns. Thus a calibration snapshot
does not prevent target-period native capture; final collection obtains the
later cumulative file as a separate snapshot.
The generated `native-disable.patch` and its SHA-256 are retained in deployment
metadata. These patched images are built only in GitHub Actions; local adapter
checks do not build or run the application.
The same recorded patch wraps the existing checkout and product-catalog
`go mod download` Docker layers in at most three attempts with bounded backoff.
It does not alter `go.mod`, `go.sum`, dependency versions, checksum verification,
the compilation command, or pinned base-image digests; the full replacement
commands are included in the deployment manifest.
It does **not** infer Kafka delivery from the HTTP response or producer state;
the upstream producer uses `RequiredAcks=NoResponse`.

`verify_async` performs separately timestamped PostgreSQL reads keyed by that
returned order ID and retains every poll. Success requires the order row, at
least one matching item, and the shipping row within the independent 10-second
deadline anchored to the business operation's start. A first positive SQL read
after that boundary is unknown because it cannot prove the persistence time.
While paused, accounting remains stopped through the last registered
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
