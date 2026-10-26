# DeathStarBench Social Network adapter

This adapter runs DeathStarBench Social Network commit
`6ecb09706140f8730b5385c08f1386c654c3c526` across two Ubuntu 24.04 Docker
guests. Downloads, image pulls, deployment and traffic occur only through the
GitHub Actions context.

## Placement and addressing

Node A runs the upstream application, its data stores, Jaeger, replica A and a
TCP HAProxy retaining the original `user-timeline-service:9090` identity. Node B
runs replica B. They have static container addresses `172.28.11.41` and
`172.28.12.41`; the proxy is `172.28.11.40`. Cross-guest Docker bridge routing
is not assumed: Docker 29 blocked it in qualification run 40328775069, where
replica B repeatedly timed out creating its MongoDB index and never listened.

The required cross-node edges therefore use bounded guest-published ports.
Both replicas expose the same per-guest transport port 19090 (the proxy still
uses A's direct container endpoint and B's guest endpoint); only B's service configuration
points to node A's published user-timeline MongoDB (37020), Redis (16383),
post-storage Thrift (19092), and Jaeger UDP (16831). Node A services retain their
original container-local names and ports. HAProxy routes A directly and B via
`192.168.76.12:19090` with the same round-robin policy in every fault state.
Readiness stops the other replica and requires the exact stable timeline from
each replica separately, then restores both. A merely running B process cannot
pass, because the upstream process does not listen until its database index is
available.

The adapter retains both rendered Compose files and a container/IP mapping.
These are deployment provenance, not an expected dependency graph and are not
fed to discovery.

## Native tracing modes

DeathStarBench uses Jaeger OpenTracing SDKs in both its C++ services and nginx
Lua frontend. Suppression changes the SDK configurations themselves:

* `absent`: `disabled: true` and a const-zero sampler in every C++ service and
  the nginx tracer;
* `partial`: tracing remains enabled in the frontend and ordinary services, but
  both controlled user-timeline replicas mount a disabled SDK configuration;
* `full`: all SDKs use a const-one sampler.

Jaeger remains running even in absent mode so its empty service/trace census can
verify absence. This is not exporter filtering. Native data is exported from
the Jaeger API into a separate directory. This adapter makes no claim that a
generic OBI collector understands Thrift; eBPF collection/fallback belongs to
the common orchestrator.

## Fixtures and success oracle

Users 0 and 1 are reserved for unique compose attempts and compose fan-out
checks. Dedicated user 2 has one stable post and dedicated follower 3 follows
user 2; measured timeline reads use those otherwise untouched principals and
must contain that exact post. Fixtures are initialized once after a fresh
Compose deployment. `reset()` deliberately preserves MongoDB and Redis
containers, restores the selected database and both replicas, and requires the
same stable post through both the owner and follower reads. This prevents an
empty `{}` response from passing and keeps every block's read precondition
comparable. A compose teardown removes the unnamed container state.

Every attempt has an evaluator-only namespace/index identifier. On the wire it
has only `X-Experiment-Request-Id: req-<sha256>`; neither the header nor URL
contains an operation or namespace label, and no sampled native trace context
is injected. Compose uses the opaque request id in the post text and succeeds
only for HTTP 2xx containing the exact upstream
`Successfully upload post` acknowledgement. Timeline reads succeed only for
HTTP 2xx and a JSON array whose every item has string `post_id` and `text` and
which contains the exact stable fixture. A response is successful only when the
complete local processing elapsed time is within the supplied monotonic
deadline. `verify()` returns copies with a separate `eventual_postcondition`;
it never changes immediate HTTP success, and the fan-out deadline remains ten
seconds from the original response rather than restarting after fault recovery.
Late verification remains unknown. A control epoch is captured with each
attempt; if replica or database control changes before verification, the fan-out
result is also unknown rather than being measured after restoration. Response bytes are preserved base64 with
hashes; these evaluator records are not observation input.

The registered database control is the concrete node-A
`user-timeline-mongodb` container. Stopping it may be masked temporarily by a
warm Redis cache. The stable read fixture therefore cannot by itself prove a
MongoDB access on every request, and database-down effects are operation- and
cache-state-dependent. The adapter retains this uncertainty and the external
outcome rather than interpreting a cached success as proof that the database is
irrelevant (or a failure as proof of one unique causal path).

## Provenance and licensing

The request payloads, follower choice and response predicates were independently
reimplemented from the public SIMPAT repository at commit
`61e65e4c09e25dd3c752756d07fe91ca504ece2f`, particularly
`live_pilot.py` and `live_placement_pilot.py`. That repository has no top-level
license, so no source code was copied. The behavior originates in DeathStarBench;
its pinned source and license are fetched unchanged during preparation. Image
digests and the HAProxy lock are reused from SIMPAT's pinned public configs.

## Limitations

The application is split across two independent guest kernels on one physical
Actions runner. Shared backing stores mean the two controlled replicas are
redundant service processes, not independent databases. HAProxy TCP health
checks detect process/route availability; they do not inspect Thrift semantics.
The adapter never derives a discovery graph from the known deployment.

## Bounded DeepFlow fallback

`deepflow_fallback.fallback(ctx, adapter, out)` starts the one permitted fallback
on both guests and returns a handle whose `collect()` method stops the agents,
copies their raw file output, and writes a hash/provenance manifest. Triggering
is deliberately outside this adapter: the common orchestrator may call it only
after actual OBI coverage is absent, before fallback traffic, and must collect
before guest teardown. It is not a parallel collector comparison.

The fallback pins official DeepFlow agent `v7.2.3` and its multi-platform image
digest. It uses the official `--standalone` mode, which requires no DeepFlow
server and writes `l4_flow_log` and `l7_flow_log` locally. Each guest is limited
to one CPU, 1024 MiB RAM and 1024 PIDs. Flow files rotate at 128 MiB with at most
two files for each of the two supported output types (512 MiB maximum per
guest); Docker logs are limited to two 50 MiB files. Raw files, agent logs,
container/image inspection, exact configuration, hashes and errors are retained.

This option has a concrete DSB limitation: the pinned official
`L7Protocol` enum includes HTTP, MongoDB, Redis and other protocols but not
Thrift. No custom parser is added. The fallback can therefore retain L4
connections for DSB's Thrift calls and supported database/frontend L7 records,
but cannot turn those connections into Thrift method observations. Unsupported
operation interpretation remains explicit rather than being inferred from the
known deployment.
