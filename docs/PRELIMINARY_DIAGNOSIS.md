# Preliminary explanation of the observed limits

This is a read-only follow-up to the completed iteration-4 series, dated
2026-10-29. It inspects saved observations, models, assignments, configurations and
pinned implementation code. It changes no observations, forecasts, metrics or
selection decisions and includes no new acquisition, replay or collector trial.
The [published results](../results/iteration-4/SOURCE.md) remain authoritative.

The diagnostic question is where required information becomes unavailable:
collection/export, graph construction, identity binding, causal association or
operation classification. A demonstrated transformation of a retained example is
distinguished below from a possible cause of the underlying observations. These
examples do not estimate how frequently each mechanism occurs.

## Scope and review before inspection

The original contribution criterion remains the same useful independent outcome
with less complete effort, or a better outcome at comparable complete effort.
The equally informed direct contract/inventory predicate, native observations and
their combination remain the comparison. Available primary forecasts equal the
direct predicate; explanation of a failed branch does not remove that equivalence
or establish comparative utility. Manual preparation effort remains unmeasured.

The orchestrator and independent skeptic gave GO for this bounded inspection
under the original criterion, retaining the completed study's unestablished
positive contribution. The proposed explanations concern pipeline stages, not a
replacement success criterion. Retrieval, investigation and documentation CI are
additional work outside the frozen study cost snapshot. No new cost advantage is
claimed.

## What depends on the collector

The empirical source is **OBI v0.15.2 with the retained campaign configuration**,
not eBPF in general. The kernel mechanism alone does not specify protocol parsing,
runtime hooks, context association, exported identities or compatible graph input.
Changing any of these can change the recoverable graph, even for the same traffic.

The annotated OBI v0.15.2 tag resolves to commit
`b28e4e7fe0a01f1961b7c4747a13b8ff486d6fec`. Its
[feature matrix](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/b28e4e7fe0a01f1961b7c4747a13b8ff486d6fec/devdocs/features.md)
lists HTTP/gRPC instrumentation, Kafka produce/fetch observation without Kafka
context propagation, and MongoDB support from 5.0 with compressed payloads
excluded. Thrift is not listed. These are documented capabilities and boundaries,
not evidence that every listed feature operated in these deployments.

Different collectors may expose different evidence. For example, the official
[DeepFlow Kafka mapping](https://deepflow.io/docs/features/l7-protocols/mq/)
(documentation consulted 2026-10-29) describes topic, partition and offset fields,
with restrictions including the first corresponding field. That is not proof of
an exact order-to-consumer-to-write association: Produce base offsets and Fetch
request offsets require careful interpretation, and downstream linkage is still
needed. DeepFlow was not tested in this follow-up. Neither its documentation nor
OBI's missing Kafka context propagation proves that swapping collectors would
resolve the retained unknowns.

## DeathStarBench: a protocol-coverage hypothesis and a proven input-label issue

The saved absent/seed6 graph retains all three `nginx-thrift` HTTP entry endpoints,
but lacks outgoing application-call edges from that service and the compose
service/fanout. Full/seed7 saved bindings likewise identify missing ingress-to-
backend and internal mandatory calls, while native and combined primary forecasts
are available. This locates the practical obstruction in required graph evidence,
before a usable eBPF operation model reaches simulation.

The protocol mismatch is a concrete explanation to investigate: DSB uses Thrift
for these internal calls, whereas the pinned OBI feature matrix does not list
Thrift. Bering's [eBPF dependency logic](https://github.com/MB3R-Lab/Bering/blob/6f806428509a640a6419058c2ad845ed44db7512/internal/discovery/ebpf.go)
also requires recognized operation evidence for HTTP/RPC client dependencies;
generic TCP connectivity cannot substitute for the missing operation edges.
This supports a collector/protocol-coverage hypothesis. The graph and support
matrix alone do not identify whether a particular process was unselected, a
payload was unrecognized, or context association failed. We do not generalize
this observation to every eBPF collector or claim an alternative would resolve it.

One narrower error is located definitively **before Bering**. Original OBI export
`toolchain/inputs/ebpf/raw/exports/ebpf-000217.pb` contains a client span from
`user-timeline-service-replica-b` with `db.system.name=mysql` and endpoint
`192.168.76.11:37020`. The saved deployment exposes MongoDB 4.4.6 at that endpoint.
Bering preserves the supplied system label and an unresolved endpoint alias; it
did not invent the MySQL label. MongoDB 4.4.6 is also outside OBI's documented
network-protocol range of 5.0+. That is a support mismatch, not proof of the parser
branch responsible for the label. This single example explains neither every
missing database edge nor the missing Thrift call graph.

The original export SHA-256 is
`fe6fef65ad29e774715ee12ea9c0ed4580ad87023b486c1b5384371d72dfeff8`;
resource/scope/span indexes are `1/0/0`, trace
`9496bb1b5840d39399dd2bd9ecd5598c`, span `2f07b0fba07898d2`.
It is retained with [worker 40827363136](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40827363136)
in [data-40830558372](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40830558372).
The same worker's `toolchain/discovery/ebpf/raw/observed.json` has SHA-256
`a76e06494785fa7b0bc58a5c2eacde4799c98c96e7af24466d4cf374cfa5c176`.
The full/seed7 saved `toolchain/forecasts.json` comparison has SHA-256
`8a19a6a193b31ff3fbfd17681d65bd526309ef9668f9703877ce40c5c1018688`,
retained through [campaign 40821255620](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40821255620).

## OTel Demo: context association is a concrete candidate cause

The retained absent/seed6, partial/seed6 and full/seed7 examples all contain eBPF
HTTP entry roots. The absent graph contains `frontend -> product-catalog`
`GetProduct`, `frontend -> cart` `AddItem`/`GetCart`, and `frontend -> checkout`
`PlaceOrder` edges. The other two graphs lack those frontend outgoing edges and
instead retain proxy-to-peer HTTP client edges. The failure is therefore more
specific than missing HTTP entry capture or general gRPC incapability.

For parent-derived service-call edges, pinned
[Bering 1.2.0 discovery](https://github.com/MB3R-Lab/Bering/blob/6f806428509a640a6419058c2ad845ed44db7512/internal/discovery/discovery.go)
resolves a parent through an unambiguous exact source-domain, trace ID and parent
span ID. The [study driver](https://github.com/a-a-k/ebpf-model-discovery-experiments/blob/19ad30ea772ae5430432e2e05339a8c0d9fe0d1f/src/ebpf_discovery/bering_v4.py)
keeps OBI and native ancestry in separate source domains, including combined input.
An OBI child whose parent exists only as a native record consequently cannot obtain
that edge through this join. This is a code-supported mechanism, **not yet proof
that this is what the inspected missing edges experienced**: a matching raw child
pointer to a native-only parent has not been established here.
There is also an alternative client-dependency path: Bering requires both
`rpc.system` and `rpc.method` plus resolvable peer evidence for its RPC fallback.
Missing operation attributes or peer identity can therefore also prevent that
path from supplying an edge. Their actual role in these examples is unproven.

The context-ownership hypothesis has a concrete application path. Even in absent
mode, the study's
[checkout patch](https://github.com/a-a-k/ebpf-model-discovery-experiments/blob/19ad30ea772ae5430432e2e05339a8c0d9fe0d1f/systems/otel_demo/adapter.py)
installs a Go `NeverSample` provider and W3C propagator. No native export does not
mean no application-created context. In absent/seed6, frontend-to-checkout gRPC
and checkout-to-shipping HTTP edges exist, while checkout-to-cart, catalog,
currency and payment mandatory gRPC calls are missing or ambiguous. Interaction
between this non-recording context and OBI is therefore a testable explanation;
it is not established merely by the protocol pattern.

Partial/full additionally change active native instrumentation and proxy tracing.
OBI still exports directly to the study's per-guest OTLP receivers, bypassing the
demo's native OTel Collector. A transformation in that native collector is thus
not on the direct OBI export path. The selected modes use the same OBI configuration,
including `context_propagation: all`, with OBI's Java and Node.js helpers disabled
in the [collector configuration](https://github.com/a-a-k/ebpf-model-discovery-experiments/blob/19ad30ea772ae5430432e2e05339a8c0d9fe0d1f/src/ebpf_discovery/collectors.py).
Thus the experiment also does not exercise every optional OBI runtime capability.
These facts do not isolate which runtime/provider or propagation layer caused the
difference. Collection loss, runtime hooks and other correlation behavior remain
alternatives. The frozen absent mode means no native trace export; it is not an
entirely context-free application, and this caveat does not relabel its results.

To discriminate these explanations, the missing evidence is a request-correlated
raw child/parent comparison, followed if necessary by an intervention that separates
recording/export from propagation and runtime instrumentation. No such ablation
was run in this follow-up. A collector swap alone would change several mechanisms
and would not identify the cause of the current mode dependence.

Saved graph examples, all `toolchain/discovery/ebpf/raw/observed.json`:

| Cell | Campaign | Graph SHA-256 |
| --- | --- | --- |
| absent/6 | [40803782214](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40803782214) | `c7e6fc7cf6607e82df1a92bff480de69c48dc37e612eed8063f6b32050f1f97f` |
| partial/6 | [40803790289](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40803790289) | `d5c6253c5b6776d7b60b635aebf4605261d3df21fa88df8dbf5cc844b50ac30a` |
| full/7 | [40803798632](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40803798632) | `5f6996fbb57df575d8488fffee65dfd094e213597730249b660249d4e2957fe3` |

The absent/6 checkout binding, worker artifact `12870166975`, is
`toolchain/ebpf/raw/checkout/binding.json`, SHA-256
`f8c314654fa57e65fc20cad992c46e7e7c4ae8e09cb8d0835c79412d9709490d`.
Original archives and manifests are indexed in [SOURCE.md](../results/iteration-4/SOURCE.md).
Selected-member checks do not claim whole-file hashing of every large archive.

## Kafka: observation and end-to-end association are different capabilities

The saved native partial/full evidence supports a consumer `SpanLink` chain;
the eBPF chain remains unknown. The implemented
[association check](../src/ebpf_discovery/evidence_v4.py) requires exact source-local
ancestry plus a consumer `SpanLink` to connect checkout, producer, processing and
database write. Its saved `linker_scope` explicitly states that ID-only joins
without `SpanLinks` are not implemented. Order identifiers from the external
driver evaluate a selected chain; they cannot supply a missing link.

Thus this negative result concerns both the collected evidence and the implemented
association method. Kafka traffic, a matching topic, or independently verified SQL
persistence is insufficient for this check. OBI's documented lack of Kafka context
propagation is relevant to the hypothesis, but does not by itself prove the
absence of every usable message identity or link in every configuration. A
collector with different identifiers would also need a compatible association
method. This inspection does not implement one or reclassify the saved unknowns.

## Operation classes: a demonstrated sensitivity of the diagnostic

The [class implementation](../src/ebpf_discovery/classes_v4.py) constructs exact
signatures from indexed observations, separately from Bering graph forecasting.
The downstream variant retains the base method/route/step/source sequence and adds
a sorted list of source-local descendants. Repeated tokens remain repeated; queue
and processing span names can enter the fallback token when no HTTP/RPC/DB identity
is present. Training gives every distinct signature its own class. Evaluation
requires an exact previously seen signature; a novel one remains unknown.

A retained OTel absent/seed6 example makes the resulting fragmentation concrete:

| Saved test attempt suffix | Assigned downstream class | Saved signature for the same `GET /api/products/OLJCESPC7Z` |
| --- | --- | --- |
| `34242-28be7a150dec` | `class-621a4049168c967e` | Descendants include catalog RPC, PostgreSQL, flagd, and queue/processing tokens. |
| `34247-66b17e7f1694` | `class-91b8ed1ba5f43f37` | Empty descendant list. |
| `34258-fe08c78cab5f` | `class-f72eee1ecfdbf7af` | Repeated occurrences of the first class's descendant tokens. |

All three full attempt IDs begin `class_test-13-browse_product-`. They are saved
assignments, not newly computed classifications. The respective base assignments
use the route signature. The example demonstrates that a single declared operation
is split according to its observed descendants. It does **not** establish why
descendants were absent or repeated: application behavior, capture variation and
context association remain possible contributors requiring separate evidence.

The route baseline already has ARI 1 on the known cases described in the report.
On an identical bound population, adding exact features refines that partition and
has no ARI improvement available there. It can split a declared operation and
reduce coverage through unseen signatures. This is a limitation of the selected
classification method and task, not a general failure of eBPF or Bering discovery.
Driver-supplied attempt boundaries and routes also prevent interpreting the result
as autonomous discovery of business semantics.

The examples come from [campaign 40803782214](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40803782214),
artifact `12870644611`, permanently retained in
[data-40819771129](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819771129).
Selected ZIP members were retrieved with CRC checks; the model hash also matches
the campaign's saved `freeze-integrity.json`:

| Original member | SHA-256 |
| --- | --- |
| `toolchain/classes/classes-model.json` | `30045a2e74bb816a1c8b5128b27b0b0ce69fa99b5784964e5551e9158793f652` |
| `classes-v4.json` | `2b7298e952d3b080b99b9d3e608ece11e01516892ec72c486789c487078bf770` |

## Shared database: recovery without native tracing, not exclusive enrichment

The Petclinic shared-MySQL result demonstrates observed database dependencies
participating in a fault forecast under the supplied identity mapping and operation
contracts. Full native observations also retain database spans and usable DB-down
forecasts. For example, the published full/seed7 and full/seed8 `network_scope`
rows give both native and eBPF healthy-state prediction 1 and DB-down prediction 0
for `create_visit`, `list_owners` and `owner_details_with_visits`. The cached-vets
DB-down forecast remains unknown in both sources. These are existing
[report rows](../results/iteration-4/report-v4.md), not new calculations.

Consequently, this is enrichment relative to a graph that omits the shared DB,
and recovery of that dependency where native tracing is absent. It does not show
more DB information than full application tracing. A shared failure factor can
also be mathematically equivalent across different representations; matching
outcomes alone cannot establish that every individual DB call was recovered.

## Interpretation review

The independent reviewer gave explicit GO for publication under the original
criterion after checking the pinned source boundaries, saved class assignments
and model hash, Petclinic native/eBPF DB rows, DSB graph/forecast hashes and the
limits of the OTel explanation. The orchestrator accepts that verdict. The review
does not establish a positive utility or complete-cost advantage. Only explanatory
documentation changes; the 27-cell results and original provenance remain intact.
