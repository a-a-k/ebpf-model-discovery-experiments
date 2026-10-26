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
guest A publishes replica A on `13550`, the product router on `13551`, the HTTP
entrypoint on `18080`, PostgreSQL on `15432`, native OTLP/gRPC on `14317`, and
flagd on `18013`. The runner uses `192.168.76.11:18080`; generated metadata
records both container identity and reachable transport host/port.

## Native tracing modes

`full` retains native spans from every service. `partial` disables native SDK
export in both controlled product-catalog replicas. `absent` applies that setting
to every application service. Disabled containers receive
`OTEL_SDK_DISABLED=true`. Checkout and product-catalog construct Go providers
directly, and email directly adds a metric reader to what becomes a no-op Ruby
provider, so `prepare()` applies a recorded source patch and the Actions guests
build the affected images from the pinned checkout. The patch skips exporter/SDK
construction when disabled (checkout retains only a never-sample provider for
context propagation). The collector does not filter spans: its file export is
the raw native OTLP stream, and the adapter fails collection when that stream
contains forbidden native spans. This also audits that the standard disable
flag worked in the other language SDKs. OTel logs, metrics, Docker application logs,
and common eBPF evidence remain separate artifacts.

Qualification run 40336717147 showed that five nonstandard emitters ignored the
master switch. In `absent` mode, currency and shipping are therefore rebuilt with
explicit source guards around their direct trace exporters; the mounted Envoy
template has its tracing provider removed; nginx receives `otel_trace off`; and
flagd receives no collector URI (its documented opt-in for trace export). These
guards do not filter collector output or alter request handling. Partial mode only
disables the two controlled catalog replicas and full mode retains all native spans.
The disabled currency and shipping providers also use the pinned SDKs' explicit
always-off samplers, so they do not merely omit export while continuing to record
spans; their W3C propagation remains configured. In pinned flagd `v0.16.0`, an
empty collector target makes `autoexport.NewSpanExporter` return the none exporter,
and `BuildTraceProvider` returns before constructing or globally registering an
SDK tracer provider, leaving the process-wide `NoopTracerProvider` in place.

## Operations and independent outcomes

The three API operations follow the Apache-2.0-licensed SIMPAT live workload:
product browse, add one fixed catalog item to a unique cart, and checkout that
cart with unique synthetic identity data. HTTP status and response bytes are
evaluator evidence only. Checkout extracts the application's actual `orderId`.
Every HTTP step carries a fresh opaque `X-Experiment-Request-Id`, retained with
the evaluator step so common acquisition can align entry observations without
encoding an operation label, dependency, or result.
The pinned Node HTTP instrumentation (`0.221.0`) does not parse the attempted
header-capture environment variables. In `full` and `partial`, the adapter
therefore mounts a recorded source patch that uses its supported
`headersToSpanAttributes.server.requestHeaders` configuration to put this one
header on frontend server spans. It does not capture response bodies, operation
labels, or outcomes. The adapter neither creates nor injects a sampled
`traceparent`. Each native snapshot still reports whether the corresponding
span attribute was actually observed; zero observed attributes are reported as
unsupported/unobserved, not treated as a link.
Checkout reaches only the demo's packaged mock email service; the adapter has no
mail credentials and never sends external mail.

Native collection is an incremental snapshot: the collector is gracefully
stopped and flushed, its bind-mounted exporter files are copied and moved into
a unique remote snapshot directory, and the same collector is restarted with
fresh output targets before the call returns. Thus a calibration snapshot does
not prevent target-period native capture or get overwritten by the file
exporter's restart-time truncation; final collection retains the later interval
as a separate snapshot.
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
