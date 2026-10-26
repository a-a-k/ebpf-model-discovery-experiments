# DeathStarBench Social Network adapter

This adapter runs DeathStarBench Social Network commit
`6ecb09706140f8730b5385c08f1386c654c3c526` across two Ubuntu 24.04 Docker
guests. Downloads, image pulls, deployment and traffic occur only through the
GitHub Actions context.

## Placement and addressing

Node A runs the upstream application, its data stores, Jaeger, replica A and a
TCP HAProxy retaining the original `user-timeline-service:9090` identity. Node B
runs replica B. They have static container addresses `172.28.11.41` and
`172.28.12.41`; the proxy is `172.28.11.40`. The guest infrastructure routes
`172.28.11.0/24` and `172.28.12.0/24`. Replica B receives explicit `/etc/hosts`
entries for its MongoDB, Redis, post-storage and Jaeger dependencies on node A.
HAProxy always keeps the same round-robin policy; fault states stop/start only
the selected replicas.

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

Users 0 and 1 are registered and follow one another. Fixtures are initialized
once after a fresh Compose deployment. `reset()` deliberately preserves MongoDB
and Redis containers and therefore those users and accumulated synthetic posts;
it restores the selected database and both replicas and waits for a semantic
timeline response. A compose teardown removes the unnamed container state.

Every attempt has a unique namespace/index identifier. Compose uses that value
in the post text and succeeds only for HTTP 2xx containing the exact upstream
`Successfully upload post` acknowledgement. Timeline reads succeed only for
HTTP 2xx and either the exact upstream empty-table representation `{}` or a JSON
array whose every item has string `post_id` and `text`. `verify()` separately
checks that a successful composed post becomes visible in the author's user
timeline and follower's home timeline within ten seconds. Response bytes are
preserved base64 with hashes; these evaluator records are not observation input.

The registered database control is the concrete node-A
`user-timeline-mongodb` container. Stopping it may be masked temporarily by a
warm Redis cache; that is real application behavior and is retained rather than
relabelled.

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
