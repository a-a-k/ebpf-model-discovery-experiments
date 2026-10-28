# Iteration 4: graph discovery and graph-driven prediction

Status: original-criterion design GO; implementation pending review; no iteration-4 measurements exist.
This protocol supersedes the earlier observation deadlines and accuracy gates.
Historical captures, code and results remain unchanged.

## Original question and decision

Can observations collected without complete application tracing support recovery
of an operation graph whose actual simulation predicts independently observed
application outcomes? The intended contribution is useful model discovery with
less instrumentation work, or better useful information at comparable complete
cost. Merely saving a graph alongside outcome-frequency forecasts does not test
this question. Iterations 1--3 did the latter and are historical diagnostics.

The new executable path is Procrustes static analysis, Bering discovery, then
Sheaft simulation of that discovered graph. External HTTP/body and database
outcomes are evaluation data, never fitting inputs. Graph adequacy is tested,
not assumed. No accuracy threshold, deadline-based success definition or
requirement to outperform an equivalent exact calculation is imposed.

Root design verdict: GO for the original experiment with the assumptions below;
no success claim. Independent 6.1 Sol/xhigh skeptic verdict: **GO for implementation
to test the original criterion**, issued before implementation on 2026-10-28.
This is not a verdict that the usefulness criterion has been met. The reviewer
requires an implementation check before research execution and a result check
before any success claim.

## Versions and product boundary

| Tool | Source revision |
|---|---|
| Procrustes | `39f76000f8a39c971155e08ebffde829b525911b` |
| Bering | `dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3` (v1.1.1) |
| Sheaft | `686a602f4e7b71f3612f1810885e29dd66c8733a` (v1.3.2) |

All experimental adaptations, workload semantics, data and reports belong here.
Procrustes is used as its current diagnostic static analyzer. Native and explicit
`ebpf-obi` collection selections retain their own unmodified reports. The eBPF
selection records kernel/protocol coverage as unknown, rather than requiring an
application SDK. Missing custom-driver/Tracetest correspondence and conflicting
replica workload identities may still produce BLOCKED reports; retain them.
Only independently confirmed inventory facts pass into discovery overlays.
Goal-derived endpoint semantics are separately declared inputs, not discovered
facts. A real two-guest technical run checks the agent path; it does not rewrite
Procrustes eligibility. Multi-request operations use one preflight per HTTP step.
Inventory metadata attaches only to nodes already recovered by Bering. Unmatched
inventory stays separate; no inventory node or edge is inserted into discovery.

## Sources, contracts and baseline

Native, eBPF and combined observations receive identical operation contracts,
static replica inventory, intervention vectors and simulation settings. Sources
remain isolated when resolving trace/span IDs. Combining sources cannot create
cross-source parent relationships. Conflicting identities remain ambiguous.
Exact request headers and source-local ancestry select operation observations;
cross-host clock containment is never an admission condition. No evaluator body,
success flag, expected edge list or target-block observation enters discovery.

Bering receives actual observations. Required semantic calls are resolved against
its output; they never create missing edges. Missing or ambiguous obligations
produce an unavailable prediction with a reason. A complete graph is analyzed
using Sheaft external edge-aware predicates, including exact recovered edge IDs
when separate calls to a shared dependency must both be required. An observed
call is not automatically a mandatory call.

A declared mandatory DB channel is compiled into its recovered typed edges. Under
this protocol's node/whole-endpoint failures and live-edge probability one, those
edges share exactly the same availability; their conjunction is equivalent to one
channel witness. This does not infer that every observed SQL/Redis command is
mandatory. The binding records this basis; individual edge or command failures
would require different semantics. Missing or ambiguous channels remain unknown.

Compare raw observation discovery with explicitly attributed static/network-scope
enrichment, and native/eBPF/combined graphs through the same tooling. Include the
same released Bering revision in every arm. The `raw` and `network_scope`
variants differ only in explicitly supplied network scope during discovery. Both
receive the same separately attributed confirmed static facts and controlled
placement inventory for simulation. Unaugmented Bering graphs are also retained;
configured replicas and fault placement are not claimed as autonomous recovery.
Save that additional evidence and the exact transformation rule. Include the
direct source-contract plus inventory calculation where applicable. For a single
controlled two-replica service with all other components held live, that baseline
can reduce to A OR B and be exactly equivalent to the graph prediction. The
manual call audit already contains semantic dependency knowledge; its preparation
cost is charged to every method using it. No novelty or predictive superiority
is claimed for Monte Carlo, graph size, or this equivalence. HTTP observations
are external evidence about HTTP outcomes, not an alternative discovery method.


Actual OBI HTTP bodies are retained before decoding, with collector ingress,
content headers and hashes. Selection copies complete OTLP protobuf/JSON records
from those bodies; it preserves conflicting attributes, scope, links and IDs.
Native Jaeger exports use an attributed format codec. A source prefix never
turns an invalid ID into a valid one. Bering's declared OBI endpoint decodes eBPF
exports; its native endpoint decodes native exports. Combined discovery occurs
inside one Bering runtime, with source domains preventing cross-source ancestry.
The runtime replays a single offline batch, admits native late records, and
flushes after input is complete. Any dropped input or split publication is a
technical failure. Historical reconciliation is disabled for this batch method;
source timestamps do not determine selection. No graph is constructed outside
Bering. Only its emitted model is extracted from the snapshot and given to Sheaft.

## Operation contracts

These are structural predictions under fail-stop interventions and the explicit
assumption that other required components, inputs and application logic remain
correct. A predicted live path does not prove payload validity, transactional
success or timely completion. Comparing with external outcomes tests that
assumption. Full body checks remain in the evaluation even when HTTP is 200.

| System / operation | Required path semantics | Independent outcome / conditional behavior |
|---|---|---|
| DSB compose | nginx to compose; completion waits for post storage, user timeline and home timeline; user timeline write requires Mongo and Redis | Complete acknowledgement; later timeline probes are separately recorded postconditions, not discovered compose edges |
| DSB home timeline | nginx to home timeline, Redis and post storage | Exact stable fixture in complete JSON; selected user-timeline Mongo is off-path |
| DSB user timeline | nginx to user timeline, Redis and post storage | Exact stable fixture; Mongo fallback is conditional, so a Mongo-down prediction cannot assume every read accesses Mongo |
| OTel browse | frontend to catalog to catalog PostgreSQL | Complete 200 and selected product ID; fixed USD avoids frontend currency conversion |
| OTel add to cart | browse prerequisite, then frontend to cart AddItem/GetCart and Valkey | Both complete responses and exact item/quantity; skipped suffix is not an observed call failure |
| OTel checkout | browse/cart prerequisites; frontend to checkout; cart, catalog, currency, shipping quote/ship and payment; frontend catalog enrichment | Complete responses and exact order acknowledgement; EmptyCart/email errors are ignored upstream and are not mandatory; Kafka is not required for immediate HTTP success |
| Petclinic list owners | gateway to customers to shared MySQL | Complete exact seed-derived owner payload |
| Petclinic owner details | gateway to customers and visits; both to MySQL | Exact owner, pets and visits; upstream empty-visits fallback may return HTTP 200 but fails this body contract |
| Petclinic create visit | gateway to visits to MySQL | Complete 201 acknowledgement plus independently verified unique matching persisted row; persistence is a separate outcome |
| Petclinic list vets | gateway to vets | Exact seed payload; upstream cache makes DB access conditional, so DB-down does not unconditionally imply failure |

Pinned source references and machine-readable obligation manifests accompany
each adapter. Conditional paths without enough observed evidence remain unknown;
they are not forced into a conjunctive predicate. Async queue timing is outside
Sheaft's current connectivity model.

## Interventions and acquisition

Use three systems, absent/partial/full native tracing, and seeds 6/7/8: 27 fresh
campaigns. Each uses two Linux guests with separate kernels on one standard
GitHub Actions runner. This shared physical host remains a limitation.

Keep 20 requested operations/s and balanced operation mixtures: 600 healthy
class-training attempts, four 6,000-attempt discovery blocks (11,10,01,00), eight
1,200-attempt target blocks in proportions 4/2/1/1, and 600 independent healthy
class-test attempts. This is 34,800 primary attempts per campaign, 939,600 total.
Discovery blocks supply observations, not empirical end-to-end outcome rates to
substitute for the graph. Models and predictions are saved before target traffic.

Controlled logical services are user-timeline-service, product-catalog and
visits-service respectively. Their two supplied placement buckets each contain
one replica, labeled controlled_replica=a/b and guest=a/b. Sheaft correlated
placement faults are scoped to the controlled service AND its placement labels
and express exact states: 11 no outage, 10 B down, 01 A down,
00 both down. All nonintervened node/edge live probabilities are explicitly 1;
this is an assumption, not a fitted reliability estimate. Use 100,000 Sheaft
trials per state profile. Aggregate state predictions with weights
0.5/0.25/0.125/0.125 and check the exact weighted arithmetic. Independent marginal
replica probabilities must not replace the declared correlated state mixture.

Selected DB outages use separately attributed deployment-to-observed-endpoint
mapping and Sheaft service selectors. Aliases do not prove a shared physical DB.
Unresolved mapping is unknown. Preserve each caller's required DB edge so that
a shared DB actually participates in the prediction. Report structural additions
and forecast changes separately. Run 20 DB-up and 20 DB-down operations in each
campaign, reusing the existing guests.

## Completion, journaling and async recovery

There is no experiment HTTP deadline, observation cap or timestamp eligibility
gate. Remove injected proxy request limits; record native application behavior
separately. Readiness/process-control guards are technical checks, never business
failure criteria. Request duration is descriptive only.

Commit intent and planned request IDs before dispatch to a durable journal;
commit each step-start and terminal observation separately. Full response plus
contract match is true; a definitive completed mismatch is false. Incomplete
transport, unresolved requests or missing oracle evidence are unknown. An
unresolved request keeps its original intervention state: the campaign cannot
advance to a different state underneath it. A platform/technical stop retains
issued attempts, unresolved states and complete available costs and leaves the
campaign technically incomplete. It never supplies a synthetic failed response.

For OTel, execute 20 checkout controls normally, 20 while accounting is stopped,
and 20 after restoration. Preserve actual returned order IDs. While stopped,
record an independent SQL snapshot; a missing row means not yet confirmed, not
proof that Kafka holds a message. Resume accounting before waiting for persistence,
then verify the same paused IDs and new recovered IDs against exact order/items/
shipping records. No fixed completion deadline. Pending work at technical stop
remains unknown. Causal association requires an observed order ID or exact message
identifier chain; shared topics or nearby timestamps are insufficient. This is
an association/recovery check, not simulated queue timing.

The current readout supports exact source-local ancestry plus an explicit consumer
SpanLink to the producer as the cross-queue identifier chain. It reports optional
source order/message corroboration and external order agreement separately; their
absence does not invalidate a complete causal chain. Contradictory linkage IDs
remain unknown, while a business-order mismatch is a separate evaluation result.
ID-only joins without a SpanLink are not implemented in this iteration. Such
unknowns therefore cannot establish an inability of eBPF or its collector.

## Reporting and costs

Retain every operation, source, tracing mode and repeat, including missing graphs,
unknown predictions, failed technical runs and unsupported async semantics.
Report point/interval errors, uncertainty, observable coverage, route and
downstream class ARI, DB dependencies, cross-guest evidence, and available costs.
No 5/10 percentage-point success gates. Capture preparation, builds, observation,
discovery, simulation, verification, failed runs and early termination; unavailable
human/agent costs remain explicitly unavailable rather than zero.

Technical qualification precedes the series.
`toolchain/execution-summary.json` distinguishes branches that actually invoked
Bering and Sheaft from unavailable branches; qualification completion does not
imply that every source path was exercised. Reviewer checks actual generated
models, fault selectors, source isolation, frozen predictions and independent
outcomes before any success claim. Repair technical failures with retained history;
do not expand scenarios to obtain a positive result.
