# Verified diagnosis before the fresh matched series

The original question is whether eBPF can supply Bering graph discovery and
Sheaft simulation when native tracing is absent or incomplete. Superiority over
an equally informed direct calculation is not a prerequisite. The new controller
and common source are described in [CLEAN_STUDY_RUNNER.md](CLEAN_STUDY_RUNNER.md).
Historical results remain evidence; they are not substituted for fresh matched
main cells. This diagnosis does not certify completion of that series.

## OTel: two distinct transitions

The original OTel failure included a verified product compatibility defect.
The pinned OBI emitted `rpc.system.name`; Bering 1.3.0 read `rpc.system`.
[The full immutable-input comparison](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41089200845)
verified all 292 input requests, 952702 spans and 312680 RPC observations. Both
binaries accepted the same ordered bytes without dropped or late spans. The fix
added 40 gRPC edges and 13 gRPC endpoints, preserving the old graph. The generic
repair is published in [Bering 1.3.1](https://github.com/MB3R-Lab/Bering/releases/tag/v1.3.1).

That repair did not resolve every operation. Required RPC methods now occur in
edges whose targets may be opaque IP peers, rather than the declared backend.
The new OBI OTel partial smoke, run 41093684285, retained actual Docker addresses,
network namespaces and listeners. Selected before/after training samples show
`172.28.11.20` belongs to `product-catalog-router`; PID 12434 is Envoy listening
on port 3550 in net namespace 4026532449, mapped to host 13551. PID start identity
and namespace were stable around the commands, with no optional command errors.
These selected members were verified by CRC and recorded SHA-256; the whole ZIP
was not downloaded or hashed locally. The exact selected hashes and actual
Docker/listener rows are retained in
[the selected evidence record](otel-router-selected-evidence-20261030.json).
Identifying the proxy does not supply an
observed proxy-to-backend edge. No automatic backend remap was performed.

Application errors and inaccurate conditional predictions are a third question.
They are retained separately from graph availability in the
[historical runtime diagnosis](OTEL_RUNTIME_LIMITS_V5.md). Neither the semantic
fix nor a technical smoke establishes the cause of those application failures.

## DSB: complete saved-prefix evidence for all three collectors

[Audit run 41097340456](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41097340456)
verified the fixed full/compact archive digests, typed toolchain package,
pre-target hashes, every ordered frozen input, original source bytes and saved
Bering graph/forecasts. The exact source artifact declarations are in
[dsb-capture-audit-20261030.json](dsb-capture-audit-20261030.json).
This is the same absent-tracing/seed6 smoke setting for every collector, at the
original clean-controller source `4ce3046`. Captures include controls and collector
traffic; total span counts are not application coverage denominators.

| Collector | Complete frozen input | What blocks the required operation model |
|---|---|---|
| OBI | 12 requests, 618 spans; raw/input marginal and joint signatures identical | HTTP entries exist, but required internal RPC fields/edges are absent already in exported raw data. Redis 93 are server spans; user-timeline 57 are client CONNECT spans without required RPC/DB operation. |
| DeepFlow | 5 requests, 493 spans: HTTP 296 and Redis 197 | Required Thrift application edges are absent. Saved Bering graph has 15 services, 13 edges, 3 endpoints; observed services do not imply an observed ingress-to-backend path. |
| Coroot | 73 requests, 258 spans; raw/input marginal and joint signatures identical | Every span is client-side without a nonzero parent ID. Redis 101 and MongoDB 68 are observed, but application entry endpoints are absent. |

For OBI and Coroot, the missing RPC information was not lost by the frozen-input
exporter. That differs from the proven OTel semantic-convention defect.
Absence from a retained export does not prove interception is impossible; the
relative roles of process/hook selection and other capture limitations are not
completely isolated. A subsequent exact-source audit confirmed a shared parser
boundary. DSB constructs TSocket/TFramedTransport/TBinaryProtocol in
[ThriftClient.h](https://github.com/delimitrou/DeathStarBench/blob/6ecb09706140f8730b5385c08f1386c654c3c526/socialNetwork/src/ThriftClient.h#L63).
None of the three pinned built-in paths decodes this Apache Thrift format:

- [OBI kernel dispatch and userspace fallback](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/b28e4e7fe0a01f1961b7c4747a13b8ff486d6fec/pkg/ebpf/common/tcp_detect_transform.go#L62).
- [Coroot protocol enum and detection chain](https://github.com/coroot/coroot-node-agent/blob/89a858a0ee35c4eb938b86d56f23168fb0ac7573/ebpftracer/ebpf/l7/l7.c#L1).
- [DeepFlow registered built-in families](https://github.com/deepflowio/deepflow/blob/9a1219fa5cf1471ba2ec8742019661567d98002e/agent/src/common/l7_protocol_log.rs#L149).

This explains a limit of obtaining RPC semantics through the tested default
paths. It does not establish absence of TCP interception, make Thrift the sole
cause of every unknown, or rule out custom/plugin extensions, which were not tested.

The DeepFlow audit independently read all complete raw snapshot records and
matched them to saved accounting: 7434 stage-local records,4323 unique source
records,3111 repeats, zero pending tails. It found 1423 rejected eBPF DNS records
and 1785 non-eBPF Packet records; no other protocol rejection. Two gRPC records
occurred only in the final stage and describe local OTLP TraceService/Export,
not DSB calls. They were absent from the frozen fit input.

The saved default configuration omitted PostgreSQL, MongoDB, Memcached parsers.
Port prefilters did not enable them. This is a configuration defect, not an
intrinsic collector limit. The codec also lacked Memcached, but these old raw
captures contain no such records: the omission is not a demonstrated cause of
their unavailable forecasts. The corrected common source explicitly enables
the supported application parsers and preserves Memcached fields. Corrected
DSB qualification run 41096128562 confirms actual parser enablement on both
guests. Its graph grows to 32 services / 22 edges / 3 endpoints; required forecasts
remain unknown. Graph growth is not a usefulness result.

Some unknowns are binding limitations. DeepFlow/Coroot observe
`user-timeline-service-replica-a/b`, while the contract looks for exact
`user-timeline-service`. A missing controlled-service binding therefore does not
prove those processes were unobserved. Automatically merging physical replicas
is not justified. This naming issue also does not supply missing application
edges. Incomplete DB aliases likewise do not imply absent DB activity; primary
replica-only predictions explicitly retain fixed-healthy DB assumptions where
the caller is reachable.

## Petclinic native route binding regression

In the final partial/seed6 qualification, native list_owners and list_vets each
have seven unique SERVER roots. Required application/DB channels resolve, but
the only primary unknown is entry_endpoint_missing_or_ambiguous. The same root
contains url.path=/api/customer/owners and http.route=customers; Bering retains
GET /customers. V4 used aliases from that exact observation. V5 accidentally
required its endpoint path to equal the external URL, dropping the alias rule.

This is a demonstrated adapter defect, not evidence that native tracing lacks
the operation. PR6 restores only same-observation aliases for every source and
collector while retaining v5 roots without ancestry IDs. Other missing visits
calls remain unknown. The bf49 primary series was stopped before further queued
cells, and all 81 must use one repaired source after paired proof and qualification.
The original source, available captures, negative/unknown records and costs remain.

## Interpretation boundary

The conditional collection-to-Bering-to-Sheaft path has positive Petclinic
evidence, including the new OBI partial smoke. DSB remains unsupported by these
saved operation graphs. OTel combines a repaired product defect with unresolved
identity/proxy binding. None of those observations justifies an intrinsic ranking
of the three collectors or a general negative verdict about eBPF. The fresh
81-cell common-source matrix and independent artifact review remain required.
