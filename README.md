# Graph discovery from eBPF observations and external outcome prediction

**Current work: iteration 5, matched main series and remaining collector qualification.**
The [new protocol](docs/PROTOCOL_V5.md) repairs operation-class fragmentation and
plans matched OBI, DeepFlow, New Relic and Coroot campaigns. All nine OBI
system/mode settings and eight Coroot settings have passed actual smoke review;
main groups are being staged. Six OBI Petclinic main cells have passed actual
evidence review. DeepFlow's corrected Petclinic/absent and DeathStarBench/absent
pilots have also passed actual review; the other settings remain under qualification.
The 27 New Relic main cells remain access-blocked. No utility or complete-cost
advantage is claimed.
Original large DeathStarBench runs failed during training-prefix preparation;
severe host memory pressure was observed, but the precise shutdown cause remains
unproved. A [journal memory repair](docs/JOURNAL_MEMORY_V5.md) preserves exact
evidence while avoiding retention of every response body. Independent saved-data
equivalence validation passed and affected starts resumed; failed attempts and
their costs remain.
The [review boundary](docs/REVIEW_V5.md) and [qualification history](docs/ITERATION5_PROGRESS.md)
distinguish product publication, technical smokes and empirical results.
Two retained [observation limits](docs/OBSERVATION_LIMITS_V5.md) explain a
Petclinic native endpoint-binding mismatch and a DeepFlow technical guard failure
without relabelling their original evidence.
The [current intermediate snapshot](results/iteration-5/snapshot-40930225342/SOURCE.md)
contains five main cells: three absent-tracing repeats and two partial-tracing
repeats in Petclinic. These use actual eBPF graphs and Sheaft forecasts checked
against external outcomes. One partial-tracing repeat retains an additional
owner-details failure (`2099/2400` observed versus forecast `0.875`); the equally
informed direct baseline gives the same forecast. The
[earlier snapshot](results/iteration-5/snapshot-40905967491/SOURCE.md) preserves
the initial 13 smoke runs and zero-main status unchanged.
The results below belong to completed iteration 4.

**Completed experimental series (iteration 4).** All 27 planned campaigns completed
and passed independent evidence review. The
[generated report, figures and provenance](results/iteration-4/SOURCE.md) cover
939,600 primary attempts. Original captures, models, forecasts and technical
failures are retained. The [independent review](docs/REVIEW_V4.md) distinguishes
empirical completion from a positive utility or cost-advantage claim, which is
not established.

## Abstract

Can runtime observations collected by eBPF support graph model discovery and
simulation when application tracing is absent or incomplete? We study ten operations
in DeathStarBench, OpenTelemetry Demo and Petclinic on two Linux guests, with three
tracing modes and three repeats. Procrustes supplies documented static facts, Bering
constructs graphs from retained observations, and Sheaft consumes those graphs to
predict independently measured outcomes under controlled replica failures. All
forecasts are frozen before validation. Available evidence supports this complete
path for all four Petclinic operations and for two OTel operations without native
tracing. Every eBPF-only DeathStarBench forecast remains unknown because required
operation evidence is missing. Other OTel source/mode combinations also lack usable
dependencies.
A shared-database intervention in Petclinic shows observed DB edges participating
in fault prediction, with explicitly supplied identity and semantic information.
Richer operation signatures and asynchronous correlation do not show a consistent
eBPF advantage. Available primary replica-failure forecasts equal a direct predicate
given the same manual
contracts; complete preparation effort is unmeasured. Thus the evidence establishes
specific applicability and observed limits, not lower total effort or superior
prediction. The retained cost snapshot includes preparation and failed attempts;
later publication costs and unmeasured human effort are distinguished explicitly.

The agreed scope is [GOALS.md](docs/GOALS.md), and the executable method is
[PROTOCOL_V4.md](docs/PROTOCOL_V4.md). The final report links every operation's
saved evaluation, graph, forecast, uncertainty and costs. Original attempts and
technical repairs remain in [RUN_HISTORY.md](docs/RUN_HISTORY.md).

Application tracing can already represent service calls, database spans and
asynchronous links. The question is whether the eBPF source recovers sufficient
evidence for the same modelling task when those observations are unavailable.
OBI provides observations; Bering supplies graph discovery; Sheaft supplies the
simulator. Merely exporting OTLP is not the tested end result.

The research questions are:

1. Which operations retain a usable graph and an externally testable forecast
   without complete native instrumentation?
2. Which distributed and database dependencies are recovered, and do they actually
   participate in a forecast rather than only enlarge the graph?
3. Do downstream observations improve operation identification, and what accuracy,
   coverage, uncertainty and preparation/computation costs accompany each source?

Iterations 1–3 are preserved in [README.iteration-3.md](README.iteration-3.md).
Their conditional-state predictors did not consume recovered graphs, so their
results are not evidence for the graph-to-simulation claim tested here.

## 1. Research question and contribution criterion

The question is whether observations collected without complete application tracing
can recover an operation graph whose actual simulation predicts independently
observed application behavior:

`eBPF observations → Bering graph → Sheaft simulation → external outcomes`

[Procrustes] supplies static preparation and confirmed deployment facts, [Bering]
discovers the runtime graph, and [Sheaft] evaluates declared failure profiles on that
graph. The desired contribution is the same useful external result with less
instrumentation effort, or a better useful result at comparable complete cost. A
graph that merely looks plausible, a high internal quality score, or an outcome-rate
predictor stored beside a graph does not satisfy that criterion.

The strongest simple baseline receives the same operation contracts, controlled
replica inventory and state mixture as the graph arm. For a required two-replica
service with all other required components held live, it directly computes the
controlled-service predicate `A OR B`. Under the planned state weights
`11/10/01/00 = .5/.25/.125/.125`, that baseline is `.875` when the controlled service
is mandatory and `1.0` when it is not. It may therefore be mathematically equivalent
to the Sheaft result. That equivalence is reported, not hidden by Monte Carlo.

Additional value would require recovered evidence that changes a sound prediction
or reduces measured preparation while preserving the useful external result. An
example of the former is a required observed call or selected database edge.
Manual semantic declarations are charged to both methods. Human/agent preparation
time was not instrumented and remains explicitly unmeasured; no full-cost advantage
will be claimed from runtime measurements alone.

The executable protocol is [PROTOCOL_V4.md](docs/PROTOCOL_V4.md). It supersedes old
two/ten-second admission rules, timestamp-containment gates and arbitrary accuracy
thresholds. An unfavorable result remains an empirical result; it does not authorize
a weaker post-hoc claim.

## 2. Released product path and pinned tools

The product capability and the research result are different things. [Bering v1.1.1]
is a published product release with an actual SDK-free OBI input and a generic Linux
smoke test. That proves the product accepts real OBI OTLP and emits a graph in its own
acceptance environment. It is **not** a result for these applications or interventions.

The nine admitted Petclinic cells and the admitted OTel/full/6 run use these exact
source revisions (each campaign retains its own build manifest):

| Component | Revision or release | Role |
|---|---|---|
| [OpenTelemetry eBPF Instrumentation] | `v0.15.2` | kernel-side HTTP and database observations without application SDK instrumentation |
| [Procrustes] | `39f76000f8a39c971155e08ebffde829b525911b` | static deployment preflight and confirmed identity/replica facts |
| [Bering v1.1.1] | `dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3` | source-domain-aware OBI/native discovery and graph publication |
| [Sheaft v1.3.2] | `686a602f4e7b71f3612f1810885e29dd66c8733a` | edge-aware predicates and deterministic state-profile simulation |
| [mb3r-stack v1.3.0] | released integration bundle | published product integration reference, not the experiment runner |

The remaining eight OTel cells and all nine fresh DSB cells pin [Bering v1.2.0](https://github.com/MB3R-Lab/Bering/releases/tag/v1.2.0),
commit `6f806428509a640a6419058c2ad845ed44db7512`, and use explicit `on_shutdown`
publication. This removes the calendar window from complete offline batches;
it does not change graph construction, source scope, operation contracts or
the comparison baseline. The other two research tool pins remain as above.
One separately named diagnostic reuses the full retained DSB checkpoint and
records both the original 1.1.1 binaries and the separately verified new build.
Historical replay profiles keep their original binaries and `windowed` mode.
The diagnostic and fresh dispatches received separate independent execution
review. Product tests do not establish their empirical outcome; valid earlier
cells were not relabelled or reacquired for a version change.

The workflow reads each tool's declared Go version, downloads the corresponding
official Go archive, verifies its digest, builds with `GOTOOLCHAIN=local`, and records
source commit/tree, binary hash, size, clone time and build time. The experiment does
not substitute an unpinned container or a locally installed binary.

Procrustes reports are consumed conservatively. Only `CONFIRMED` identity and replica
facts can attach to nodes already observed by Bering. An unmatched inventory item
stays in the sidecar; it cannot create a node or edge. Custom workload scenarios are
not fabricated to make static preflight pass. Retained `BLOCKED` or unknown
Procrustes reports remain visible; successful execution does not imply that every
preflight requirement was satisfied.

## 3. Systems, operations and two-guest environment

Ten operations are exercised across three pinned applications:

| System and source | Operations | Controlled service |
|---|---|---|
| [DeathStarBench Social Network `6ecb097`] | compose post, read home timeline, read user timeline | user-timeline A/B |
| [OpenTelemetry Demo 3.0.0 `8c47d47`] | browse product, add to cart, checkout | product-catalog A/B |
| [Spring Petclinic Microservices `3858f9c`] | list owners, owner details with visits, create visit, list vets | visits A/B |

Each campaign boots two Ubuntu 24.04 QEMU/KVM guests on one standard public GitHub
Actions runner. Each guest has a separate kernel, boot ID, network stack, Docker
daemon and OBI process. Controlled replicas occupy different guests. Guest addresses
are `192.168.76.11` and `.12`; application Docker subnets are `172.28.11.0/24` and
`172.28.12.0/24`. Cross-guest paths use explicit published ports and stable routing;
fault states stop replicas without rewriting routes.

The shared physical runner is a limitation: this is an inter-kernel and routed-network
experiment, not a two-physical-host failure study. Guest/runner CPU, memory, kernel,
BTF, boot, image, process and network evidence are retained. Workflows use public
runner resources and do not silently switch to a paid larger runner.

The OTel and DSB workflows compute the saved training model on a separate
standard Actions runner. OTel's full-input diagnostic and fresh full/6 replacement
passed independent review, as did all eight remaining OTel cells. DSB
activation passed the reviews recorded in
[the protocol](docs/PROTOCOL_V4.md). The two application guests stay on their original runner and
remain alive until the returned model is verified and the same campaign completes.
This separates toolchain resource use from the application host; it does not move
replicas to additional physical machines or change the application's placement.

Application adapters and their source-audited contracts are documented separately:
[DeathStarBench](systems/deathstarbench/V4.md),
[OTel Demo](systems/otel_demo/V4.md), and
[Petclinic](systems/petclinic/V4.md).

## 4. Information boundary and operation contracts

Before dispatch, the driver durably records the attempt and every planned HTTP step.
Each step carries a unique opaque `X-Experiment-Request-Id`. The value contains no
operation name, expected topology, fault class or outcome, and the driver injects no
sampled trace context. Entry binding requires that exact ID plus the actual HTTP
method, canonical route and a declared entry-service alias.

Manual contracts declare business obligations equally for eBPF, native and combined
arms. They may name required callers/callees or a database role, but they do not add
expected edges to the recovered graph. Required service calls must resolve to
observed, unambiguous Bering edges. Missing structure produces an unavailable
prediction with a reason. In the primary replica-only intervention, nonintervened
database obligations are explicitly assumed fulfilled even if their channels are
unobserved; a primary forecast therefore does not prove discovery of every DB edge.
The separate DB-down forecast requires observed, mapped mandatory DB channels.
Conditional calls remain unknown when their condition is not established.

The inputs distinguish supplied semantic and inventory knowledge from observed
nodes and edges. Mandatory caller/callee contracts supply structural knowledge, but
cannot create a missing Bering edge:

- operation plans supply step boundaries, methods, routes and opaque request IDs;
- source contracts state which calls are semantically mandatory;
- rendered deployment inventory supplies confirmed identities and the two controlled
  placements;
- database inventory supplies separately attributed endpoint candidates;
- external HTTP bodies, persistence results, success flags and target observations
  are unavailable to discovery and simulation fitting.

Multi-step prerequisites are evaluated independently. Browse/add/checkout validate
the selected product, cart item and quantity, and order acknowledgement; Petclinic
checks its fixed payloads and separately verified create-visit persistence; DSB checks
its fixed fixture responses and preserves later probes as external postconditions.
A skipped suffix is `not_attempted`, not an invented failed internal call.

No experiment HTTP deadline, observation cap or cross-clock eligibility gate exists.
Native application/proxy connect behavior is documented separately. A fully received
response with a contract mismatch can be false; an incomplete transport, unresolved
request or absent oracle is unknown. The intervention cannot change while an issued
request is unresolved.

## 5. Lossless observation-to-graph-to-simulation pipeline

OBI exports genuine OTLP protobuf (or OTLP JSON) to the study receiver. The receiver
atomically retains the original body, including optional gzip encoding, content
headers, receipt metadata and SHA-256, even if decoding fails. Its JSONL index points
back to the exact raw file; it does not repair IDs. Native OTLP/Jaeger exports remain
in a separate source with their own provenance.

The SQLite observation index streams complete file prefixes and retains conflicting
same-ID variants. Bering receives **all records in the frozen training prefixes** of
the selected source, including calls without a connected entry trace. Exact request
binding remains a separate input to endpoint-alias, class and causal checks. Complete
protobuf resource/scope/span messages preserve attributes, links, unknown fields, IDs
and timestamps. Invalid/all-zero IDs do not become valid through prefixing. Native
Jaeger has an explicit format codec; original evidence is retained.

For each source and variant, one offline batch is replayed through the actual Bering
runtime and its observed graph is reused across operations:

1. `ebpf` uses Bering's declared `ebpf-obi` endpoint and source domain;
2. `native` uses the native endpoint and a separate domain;
3. `combined` sends both domains to one runtime but never creates cross-source parent
   relationships;
4. Bering flushes after all input. Each operation overlay is then applied by Bering
   in a separate replay, and only its published model is passed to Sheaft.

New Bering 1.2.0 runs implement this with `on_shutdown`, without a window size or
publication timer. Earlier 1.1.1 runs used a 24-hour runtime window and checked
that every source observation was present, none were dropped and exactly one
snapshot was published. The failed DSB diagnostic crossed a UTC window boundary;
this exposed a possible early-publication path, but its unavailable HTTP 500
body prevents attributing the precise error. The failed attempt is retained.

This corrects the first v4 implementation, which required complete parent chains
before admitting downstream calls. Structural calls do not by themselves establish
causality for an individual operation. The global graph can also include preparation,
verification and ambient traffic; all arms have the same scope policy. Inputs are
shared without copying wire bodies per operation. Preparation/replay costs are retained.
The offline Bering batch still holds spans in memory; the SQLite index does not make
that tool memory bounded. Actual guest/tool resource qualification remains necessary.

There are two discovery variants. `raw` preserves the original wire structures,
with separately attributed format conversion, source-URL path derivation and
explicitly supplied receiver roles where exact entry evidence permits them; it is
not claimed to be entirely unaided.
`network_scope` differs only by adding the explicitly attributed
`bering.network.scope` resource attribute. Existing conflicting attributes are
retained rather than overwritten. Both variants receive the same contracts and
confirmed static/placement facts. Comparing them measures the consequence of that
declared scope; it is not autonomous network recovery.

For every available graph, source contracts resolve observed required edges. Sheaft
runs 100,000 trials for each correlated state profile with all nonintervened node and
edge live probabilities fixed at one. The implementation also evaluates the exact
deterministic graph law and refuses a disagreement between that law and Sheaft. The
weighted prediction is saved before target traffic, hashed, and checked unchanged
after acquisition.

## 6. Fixed 27-cell experimental design

The fresh grid is three systems × three tracing modes × seeds `6,7,8`, for 27 cells:

- `absent`: application native tracing is genuinely disabled; OBI remains active;
- `partial`: both controlled replicas lack native tracing; remaining native coverage
  may be present;
- `full`: configured native tracing is enabled across the application.

Suppression is a source/runtime property, not a collector-side filter. eBPF and native
raw evidence stay separate in every mode.

Each cell requests 20 operations/s with a balanced operation mixture:

| Primary phase | Blocks | Attempts/block | Attempts |
|---|---:|---:|---:|
| healthy class training | 1 | 600 | 600 |
| discovery/calibration states `11,10,01,00` | 4 | 6,000 | 24,000 |
| independent target, states in ratio `4:2:1:1` | 8 | 1,200 | 9,600 |
| independent healthy class test | 1 | 600 | 600 |
| **total per campaign** | **14** | | **34,800** |

The fixed series specifies 939,600 primary attempts. Calibration/discovery blocks
supply observations to the graph path; their empirical success rates are not used as
a replacement predictor. The target state counts are fixed at 4,800/2,400/1,200/1,200.

The state profile is correlated placement failure: `11` keeps both replicas, `10`
removes B, `01` removes A and `00` removes both. Supplied placement labels identify
one controlled replica on each guest. They do not claim that Bering autonomously
recovered deployment placement.

Technical qualification first runs 120 healthy plus 120 both-down requests for each
system in full mode, exercises the actual toolchain, and checks retained source and
model artifacts. The first run at revision `7e8deb9` failed on an empty
`operation.mandatory_targets` input. Repair `1284a5f` supplies the already-audited
service targets separately for each HTTP step; it changes no Bering discovery or
Sheaft obligation. Original captures and failed outputs are retained. Qualification is a technical prerequisite,
not a favorable-accuracy filter.

## 7. Database and asynchronous controls

Each campaign includes 20 selected-database-up and 20 selected-database-down attempts.
The prediction compares the graph's healthy `11` result with its selected-DB-down
result. It does not compare DB-down with the `.875` weighted target mixture.

Database identity has two levels. A recovered `(system,address,port,scope)` is a
logical observed endpoint; deployment metadata attributes which stopped container
owns matching endpoints. An alias alone does not prove that multiple logical nodes
are one physical database. Unresolved or conflicting mapping stays unknown.

Petclinic deliberately exercises a shared MySQL container. `owner_details_with_visits`
requires both customers→MySQL and visits→MySQL edges. We retain each caller-specific
witness so a generic DB node cannot substitute for missing caller evidence. Under
the tested whole-endpoint outage and live-edge assumptions, their availability
factors may be mathematically equivalent; matching that outcome alone does not
prove both calls were recovered. OTel selects catalog PostgreSQL. DSB selects
user-timeline MongoDB; its user-timeline read fallback is conditional, while home
timeline is off that selected path. The manual baseline uses the same declarations:
unconditional selected DB means 0 under DB-down, a conditional dependency is unknown,
and a declared complete off-path operation means 1.

OTel also retains 20 checkout controls in each of normal, accounting-paused and
recovered conditions. While accounting is paused, the evaluator takes one independent
SQL snapshot and records pending rows as unknown. It then resumes accounting before
waiting for persistence of those same returned order IDs. Recovered checkouts are
verified separately against exact order, item/quantity and shipping rows.

There is no HTTP or persistence deadline in these controls. A technical stop retains
pending state. Trace context, a shared Kafka topic, broker request correlation or
nearby timestamps do not prove the identity of an order. A causal association requires
an observed order ID or an exact source-local producer/consumer message chain. Async
recovery is reported separately because Sheaft's current connectivity simulation does
not model queue timing or durable delivery.

## 8. Frozen classes and external evaluation

The class diagnostic is separate from graph forecasting. It learns exact signatures
only from the healthy `class_train` block and freezes them before target traffic:

- `base`: the observed method/canonical-route sequence for supplied planned steps;
- `downstream`: the base sequence plus source-local descendant service/call identities
  from HTTP, RPC and database attributes;
- raw operation names are a fallback only when no canonical HTTP/RPC/database identity
  exists, because names may embed IDs or SQL values.

eBPF, native and combined models remain separate. Missing/ambiguous roots, conflicting
identities and unseen test signatures are unknown; they are not fitted at test time or
pooled into one artificial class. Operation labels enter only after prediction to
compute [adjusted Rand index](https://doi.org/10.1007/BF01908075) on the known subset. Coverage and unknown counts accompany
ARI. Driver-supplied attempt and step grouping is explicit: this does not claim
automatic business-session segmentation in arbitrary production traffic.

External evaluation reports, per operation/source/variant/repeat:

- `true`, `false`, `unknown` and invalid outcome counts;
- empirical identification bounds `[success/n, (success+unknown)/n]`;
- the saved point/interval prediction, absolute-error range and worst-end error;
- per-state outcomes and predictions;
- descriptive latency with no deadline interpretation;
- nominal [Wilson envelopes](https://jhanley.biostat.mcgill.ca/c607/ch08/wilson_jasa_1927.pdf)
  labelled with their IID Bernoulli assumption;
- class coverage/ARI, DB and async controls, integrity checks and available costs.

There is no 5 pp/10 pp gate and no overall mean that can mask a failed operation or
source. Missing forecasts retain explicit uncertainty rather than contributing zero to
a mean. A cell is scorable only if status, frozen hashes, exact phase/state counts,
unique attempt IDs, and external/plan/census identities all agree.

Duplicate `(system,mode,seed)` attempts are never silently overwritten. Without an
explicit technical-selection manifest the cell is ambiguous and unscored, while all
attempts and costs remain in the report. A manifest may retain only the sole complete
campaign while excluding technically incomplete attempts; it cannot choose among two
complete campaigns by outcome.
Keep a committed selection manifest outside the generated `results/iteration-4`
directory, which each report run replaces in its disposable Actions checkout.

## 9. Results

The [Actions-generated report](results/iteration-4/report-v4.md) and
[figures](results/iteration-4/figures/figures-v4.md) retain all 27 selected cells and
939,600 primary attempts. One additional incomplete OTel attempt remains visible
as a technical exclusion; it is not an extra repeat. Values below are copied from
saved, independently reviewed evaluations;
they are not local recalculations. Unknown forecasts are retained as unknown and
are excluded from numerical error means rather than assigned a baseline value.

The following availability pattern holds in all three repeats and both graph
variants. Availability is conditional on the stated nonintervened-component
assumptions; it does not mean zero prediction error.

| System | Native tracing | eBPF forecasts | Native forecasts | Combined forecasts |
| --- | --- | --- | --- | --- |
| Petclinic | Absent | All four operations | Unknown | All four operations |
| Petclinic | Partial | All four operations | List owners, list vets | All four operations |
| Petclinic | Full | All four operations | All four operations | All four operations |
| OTel Demo | Absent | Browse product, add to cart | Unknown | Browse product, add to cart |
| OTel Demo | Partial | Unknown | Unknown | Unknown |
| OTel Demo | Full | Unknown | All three operations | All three operations |
| DeathStarBench | Absent | Unknown | Unknown | Unknown |
| DeathStarBench | Partial | Unknown | Home timeline | Home timeline |
| DeathStarBench | Full | Unknown | All three operations | All three operations |

### Petclinic: graph-driven forecasts and a shared database

Across all nine Petclinic cells, eBPF and combined graphs supported all four operation forecasts in both raw and network_scope variants. Sheaft consumed the frozen graphs before target traffic. Forecasts matched the saved target frequencies: 0.875 for owner details with visits and create visit, and 1.0 for list owners and list vets. Each operation retained 2,400 target outcomes per cell; the Visits-dependent operations recorded 2,100 successes and 300 failures. Native observations were absent in all three absent-mode repeats. With Visits instrumentation disabled in partial mode, native-only models left Visits-dependent operations unknown while eBPF supplied usable graphs.

The shared-MySQL intervention tests a dependency used by multiple services. In the declared network_scope variant, eBPF graph-based DB-down forecasts were zero for the three mandatory DB-dependent operations, matching five failures per operation. Raw DB mappings and the cached-vets case remained unknown. This shows a recovered DB dependency participating in prediction under the supplied identity and operation contracts; it does not establish a capability exclusive to eBPF, since full native tracing retains DB spans.

The richer operation grouping did not improve identification against the declared labels. In absent-mode eBPF records, downstream grouping had known-subset ARI approximately 0.489, 0.504 and 0.516, versus route-grouping ARI 1, and retained more unknown assignments. The equally informed manual predicate made the same primary forecasts. These results support the concrete graph-to-simulator path for this application, without establishing comparative utility or a complete-cost advantage.

The [generated report](results/iteration-4/SOURCE.md) contains the
per-operation evidence, source comparisons and fixed observed-model example.

### OpenTelemetry Demo: mode-dependent coverage and asynchronous limits

Across the three admitted absent repeats, eBPF and combined graphs supported forecasts for `browse_product` and `add_to_cart`, but not `checkout`; native was unavailable by design. The fixed prediction was 0.875. In seed 6 its stored worst-end errors were 2.6875 percentage points for browse and 3.09375 for cart; seeds 7 and 8 had zero stored error. Partial tracing produced no forecast for any operation or source in all three repeats. Under full tracing, native and combined supported all three operations, whereas eBPF supported none. Full/6 errors were 3.5 points for browse/cart and 5.15625 for checkout; full/7 and full/8 had zero stored error. Raw and network-scope variants had the same availability pattern.

This mode dependence is material, but its mechanism is unresolved. The retained absent/6 eBPF graph contains the exact `frontend -> product-catalog` `GetProduct` edge. Partial/6 and full/7 lack it and instead contain a proxy-to-reported-peer edge. Entry roots exist in every mode, but the retained entry-only proof does not establish descendant context behavior, so native context propagation changing OBI/Bering correlation remains a hypothesis—not evidence that OBI generally cannot observe gRPC.

Database controls behaved externally as intended (all up checks succeeded and all down checks failed), yet every source's database-down prediction and prognostic impact remained unknown because the observations did not yield an unambiguous dependency usable for that fault forecast. For Kafka, native partial/full retained exact consumer `SpanLink` associations while eBPF remained unknown; independent SQL checks confirm the expected order and items at observation time; the links alone do not prove persistence.

The route-only class baseline reached full known coverage and ARI 1.0 wherever its source existed; downstream features were not consistently better and could reduce coverage. Moreover, every available structural forecast equalled the 0.875 strong manual source-contract/inventory predicate. These cells therefore do not demonstrate an advantage over that equal-information baseline, nor an overall utility or cost advantage.

Original complete archives are available for
[full/6](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40802785036),
[absent/6–8](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819771129),
[partial/6–8](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819773522),
[full/7](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819411131)
and [full/8](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819413737).

### DeathStarBench: incomplete internal paths

All nine repeats have passed independent review. Each retains 34,800 primary
attempts, including 9,600 target operations.
All eBPF-only forecasts remain unknown in both variants: the graph lacks required
operation evidence. These branches do not execute Sheaft and are not counted as
simulation coverage. Native observations are absent in absent mode. Under partial
tracing, native and combined graphs support only home-timeline forecasts, each 1.0,
matching the 3,200 successful target operations. The other forecasts remain unknown.
The home-timeline forecast assumes its nonintervened Redis obligation fulfilled;
it does not prove complete Redis discovery. The equal-information direct predicate
also yields 1.0.

Saved target success fractions are 0.875 for compose post and user timeline, and
1.0 for home timeline in these repeats, except compose post in absent/8:
2,799/3,200 = 0.8746875. No target outcome is unknown. Both selected-MongoDB-up and
selected-MongoDB-down controls record 20 successful primary responses per cell.
Those responses do not establish persistence or a DB-induced primary failure.
Route and downstream classes both have ARI 1 on 600 known cases wherever the
corresponding source exists; this does not recover the missing mandatory paths.

In one retained absent/6 example, original OBI attributes label the endpoint
`192.168.76.11:37020` as MySQL, whereas the saved runtime deployment exposes MongoDB
there. The original body has SHA-256
`fe6fef65ad29e774715ee12ea9c0ed4580ad87023b486c1b5384371d72dfeff8`.
It is `toolchain/inputs/ebpf/raw/exports/ebpf-000217.pb` in worker
`40827363136`, resource/scope/span indexes `1/0/0`. The deployment counterpart is
`deployment/deathstarbench/runtime-resolved-node-a.yml` in parent artifact
`12878682223`; both originals are retained in the releases linked below.
The mismatch exists before Bering: a protocol label alone does not certify correct
DB reconstruction. This single example establishes neither a mismatch frequency
nor the cause of all missing application paths. Deployment truth was not used to
rewrite the observations.

Original evidence is preserved in
[absent campaigns](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40841674653),
[partial campaigns](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40845311645)
and the [first three workers](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40830558372).
In all three full-mode repeats, native and combined graphs support all three operations in
both variants, with 12 actual Sheaft invocations per cell. Predictions are 0.875
for compose and user timeline and 1.0 for home timeline. Full/6 and full/7 match the saved
target frequencies; full/8 retains 2,799 successful compose operations out of 3,200,
with saved absolute error 0.0003125 (0.03125 percentage points). The other full/8
forecasts match their outcomes. The six eBPF-only branches per cell remain unknown
and do not execute Sheaft. Native/combined compose forecasts conditionally assume
missing or ambiguous MongoDB and Redis obligations fulfilled; every DB-fault
forecast remains unknown. Native query manifests document the actual Jaeger
queries; their service list does not establish exhaustive controlled-replica
coverage even though the configured tracing mounts are enabled.

### Distributed evidence and available costs

Cross-guest placement is supplied and verified deployment information. A structural
edge across guest endpoints is not, by itself, a confirmed causal link for a request.
The per-source linker retains exact observed identifier witnesses or an explicit
unknown. The asynchronous result above illustrates why a connection or common topic
cannot substitute for that distinction.

We report exact source-local parent-link counts, guest attribution and planned-header
corroboration or contradictions. These do not estimate overall false-positive or
false-negative linking rates: complete per-request cross-guest ground truth is
unavailable. An unattributed link or zero observed links is not evidence of zero
linking errors.

The final report retains every source/variant/operation separately, including
forecast availability, external identification bounds and repeated-run errors.
It also reports campaign elapsed time, actual tool
commands and peak memory, guest and runner evidence, checkpoint/import costs,
worker job time, and the complete declared Actions preparation/failure/reporting/
archival inventory. Parent waiting overlaps worker computation; these are not
successive elapsed phases.

Twenty operations/s is the requested primary workload, not the application's total
HTTP traffic. Preparation, verification and control probes are separately retained.
The HTTP cost table copies their recorded counts, response bytes and summed request
durations; overlapping request durations are not wall time, and completed transports
are not necessarily successful business operations. `auxiliary_timeline_probes`
duplicates the verification category and must not be added again. For example,
DSB/absent/6 records 18,428 verification GETs in addition to its primary operations.
Human/agent preparation time is unavailable, not zero. Runtime totals therefore
cannot establish a complete-cost advantage.

The [Actions cost snapshot](results/iteration-4/costs-v4.json) covers 149 declared
runs and 185 job rows, with 343,146 recorded completed job-seconds and
141,072,330,122 retained Actions-artifact bytes. Job-seconds measure accumulated
job duration, not sequential campaign wall time. Artifact bytes are not unique
storage or total transfer bytes; release parts duplicate originals separately.
Two archival jobs were still running when their metadata was read, and the report
cannot record its own eventual duration. Their completed closing metadata is
linked in [SOURCE.md](results/iteration-4/SOURCE.md), separately from this snapshot.

## 10. Reproduction, workflows and retained artifacts

All application builds, traffic, raw-data processing, discovery, simulation and report
generation run in GitHub Actions. Local work is limited to static/unit fixtures; the
evaluator CLI rejects research processing outside `GITHUB_ACTIONS=true`.

The manual workflows are:

- [qualification-v4.yml](.github/workflows/qualification-v4.yml): three full-mode
  technical qualifications by default, with reviewed diagnostic inputs;
- [series-v4.yml](.github/workflows/series-v4.yml): the fixed 27-cell matrix, up to
  three campaign jobs per workflow, with exact-cell inputs for reviewed staging or
  technical reruns; global parent/worker admission follows [the protocol](docs/PROTOCOL_V4.md#parallel-campaign-scheduling-and-api-waits);
- [report-v4.yml](.github/workflows/report-v4.yml): aggregate saved cell evaluations
  and Actions job/artifact costs for the declared run inventory, including failed preparation runs;
  render per-operation figures from that saved aggregate as SVG, PNG and PDF.
- [figures-v4.yml](.github/workflows/figures-v4.yml): render an immutable report's
  saved aggregate, require its numerical companion table to remain byte-identical,
  and retain source/image hashes. The final figures use the documented y-layout
  correction in [SOURCE.md](results/iteration-4/SOURCE.md).
- [native-batch-equivalence-v4.yml](.github/workflows/native-batch-equivalence-v4.yml):
  one fixed saved-input Bering comparison of per-trace and per-query native
  envelopes; this is an implementation check, not a completed campaign.
- [archive.yml](.github/workflows/archive.yml): retain original artifact ZIPs, job
  logs and provenance in permanent data releases, with lossless numbered parts
  when an original file exceeds the release-asset delivery limit.

For OTel and DSB, the series invokes [toolchain-worker-v4.yml](.github/workflows/toolchain-worker-v4.yml)
automatically after the training upload. Schedule parent groups with capacity left
for those workers; `max-parallel: 3` applies to each series workflow, not all
separately dispatched workflows together.

The acquisition entry point is:

```text
python -m ebpf_discovery.campaign_v4 \
  --system SYSTEM --mode absent|partial|full --seed 6|7|8 --out work/campaign
```

Qualification adds `--qualification`. There is no experiment job timeout; the external
GitHub-hosted runner limit is recorded as a platform constraint. Interruption or
eviction is a retained technical unknown, not a failed application outcome.

The fresh-series workflow supervises that command with
`--training-checkpoint work/training-checkpoint`. After training, before Bering, the
same process waits while Actions uploads a closed `training-v4-SYSTEM-MODE-SEED-RUN`
artifact. It contains consistent index/journal backups, the exact indexed raw byte
prefixes, referenced wire bodies and metadata, external training outcomes, plans,
deployment evidence, pinned binaries and file hashes. The upload acknowledgement
is bound to the run, commit, cell and manifest SHA. Only then does that process
continue on the same live guests; an unsuccessful upload is a technical failure.
This checkpoint is partial evidence, not a finished campaign or permission to
resume target measurements on a replacement host.

For OTel and DSB the supervisor adds `--toolchain-execution worker`; the CLI default
and Petclinic remain `local`. The parent dispatches one child with the exact
checkpoint artifact/manifest, parent run/attempt/cell and scientific commit. The
worker checks out that commit, restores the original paths and verifies the pinned
binaries before executing the same Bering/Sheaft pipeline. Its workflow revision
is recorded separately from the scientific checkout. Complete outputs, including
unknown branches, return as one manifested artifact. The parent verifies all
toolchain files and its unchanged training index, imports the files, fits classes,
then freezes everything before any target request. No later observation is used
by that worker. A failed worker or inconsistent import is a technical failure.
The prepared worker applies `GOMEMLIMIT=12GiB` and GC logging to Bering children
equally across source/variant branches. This is a soft Go runtime target on the
standard runner, not an input limit or RSS guarantee; GOGC and other tools'
environments are unchanged. Requested, inherited and effective settings are
retained. The OTel full-input diagnostic completed in 50:21.52 with GNU time
maximum RSS 12,557,636 KiB; this establishes feasibility for that input, not a
general capacity guarantee or proof of the earlier shutdown's cause.

Worker job and artifact costs are separate series-computation costs. Include each
`cost.remote_toolchain.worker_run_id` in the report workflow's `run_ids` alongside
its parent; it is not another scientific cell. Parent waiting/idle-guest time is
already included in campaign elapsed time and overlaps worker computation, so
these durations must not be added as sequential wall time.

The repaired series uses an additional measured 8 GiB swap file on the standard
runner's local disk. Allocation failure remains explicit. Wire files are streamed
unchanged to Bering; no observation or simulation-trial cap is introduced. Resource
heartbeats enter both files and Actions logs. A recorded child-only Linux OOM
preference is best-effort host protection, not evidence that earlier shutdowns
were caused by memory exhaustion. Checkpoint creation and upload hold are included
in campaign elapsed time; swap setup precedes it and is recorded separately.

Evaluation commands, run in Actions, are:

```text
python -m ebpf_discovery.evaluate_v4 --campaign PATH --out evaluation.json
python -m ebpf_discovery.evaluate_v4 --aggregate ROOT [ROOT ...] \
  --report-dir report [--selection technical-replacements.json]
python -m ebpf_discovery.plot_v4 --aggregate report/evaluation-v4.json \
  --out-dir report/figures
python -m ebpf_discovery.report_v4 --aggregate report/evaluation-v4.json \
  --costs report/costs-v4.json --out report/report-v4.md
```

The report extra (`pip install -e '.[report]'`) pins
[Matplotlib](https://doi.org/10.1109/MCSE.2007.55). Figures retain
each operation/source/mode separately, show unknown errors and available repeats,
and label observed repeat min–max ranges as descriptive ranges, not confidence
intervals. `figures/figures-v4.md` links the aggregate and lists the stored values.
`report-v4.md` retains individual attempts, artifact provenance, selection metadata,
operation outcomes, DB controls, class metrics, async verdicts and measured or
unavailable costs. Async verdict counts describe the stored final-capture links;
they do not change the linker or establish completion during a paused phase.

The report also renders the fixed Petclinic/full/seed6 eBPF/network-scope observed
graph when that cell has one complete unambiguous attempt, irrespective of its
accuracy. It downloads the advertised full artifact and verifies the graph against
the admitted frozen-file SHA before rendering with Graphviz. Every observed node,
alias and edge is retained, with the original model, DOT, SVG, hash and Graphviz
version. Missing or ambiguous examples stay unavailable. The picture precedes
operation/placement overlays; it is not a per-request causal or physical-topology claim.

The series evaluates each cell against its full retained evidence before upload.
The report workflow downloads compact `v4-summary-*` artifacts, verifies their
file hashes and original run/artifact identities, and aggregates those saved
evaluations. It explicitly does not reverify raw originals. The full-artifact
`--aggregate` command above remains available for independent recomputation in
Actions. Technical attempts with no completed acquisition stay unscorable; their
available costs and missing evidence remain in the report.

New report runs also retain `evaluation-v4.json.gz` for compact repository
publication. Decompression must restore the exact original JSON SHA-256; both
forms and `provenance/aggregate-packaging.json` remain in the Actions artifact.
The table and figure commands accept either form. Compression removes no fields
and changes no calculation. Earlier snapshots remain in Git history and permanent
data releases. Use the `.json.gz` path when reading the compact repository copy.

Fresh DSB full artifacts retain `toolchain/` and the closed remote handoff as
typed lossless packages to avoid upload overhead from many small files. Restore
them into absent destinations from the extracted campaign root:

```text
python -m ebpf_discovery.artifact_transport_v4 unpack --package toolchain-package --out toolchain --kind toolchain
python -m ebpf_discovery.artifact_transport_v4 unpack --package infrastructure/handoff-package --out infrastructure/remote-toolchain-v4 --kind handoff
```

The manifests preserve original paths, bytes, SHA-256 values and modes. The original
driver's native Jaeger codec unnecessarily created a file per trace. Its replacement
creates one OTLP envelope per original query file, with no filtering or deduplication.
The [fixed full-input check](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40819375950)
compared the same ordered observations and actual Bering output: 323 envelopes
replaced 174,952 files for the checked variant, with identical normalized graph,
snapshot and quality evidence. This is a representation repair, not a scientific
result or a requirement imposed by Jaeger, OTLP or Bering.

Permanent archives retain the original artifact digest. A large file may be
delivered as numbered `.part0000`, `.part0001`, and subsequent parts. Its manifest
inside `provenance.tar.gz` supplies the ordered parts, sizes, hashes and exact
reassembly/verification commands. Reassembly restores the original ZIP bytes.

A campaign artifact retains, as available:

```text
status.json, deployment.json, blocks.json, plans.json, external.json, census.json
attempt-journal.sqlite, attempt-journal.jsonl, unresolved-transports.json
training-checkpoint-cost.json        # creation/upload hold; nested in campaign time
observation-index.sqlite, index-training.json, index-final.json
observations/a.raw/, b.raw/, native.raw/ # original OTLP bodies and metadata
native/training/, native/final/      # source-separated native snapshots
toolchain-build/                     # commits, Go archives, binaries, hashes, costs
toolchain/static-inputs.json
toolchain/procrustes/                 # goals, reports and command evidence
toolchain/inputs/{source}/{variant}/  # shared frozen source wire inputs/manifests
toolchain/discovery/{source}/{variant}/ # actual shared observed Bering graph
toolchain/{source}/{variant}/{op}/    # verified input/observed references, final model,
                                     # binding, overlays, faults, predicates,
                                     # Sheaft analysis/simulation and forecast
toolchain/forecasts.json, forecast-saved.json, freeze-integrity.json
toolchain/classes/classes-model.json, classes-v4.json (campaign root)
async-*.json, infrastructure/         # SQL controls, VM/resource/platform evidence
infrastructure/campaign-process/     # same-host supervisor identity, log and exit
infrastructure/training-checkpoint/  # manifest, ready and upload acknowledgement
infrastructure/remote-toolchain-v4/  # dispatch/import identity, index proofs and costs
infrastructure/remote-toolchain-v4/worker/ # child provenance and resource evidence
```

Artifact upload steps run on ordinary job failures, with raw-data-friendly compression
and 90-day workflow retention. Abrupt runner loss can skip those steps; the separate
pre-discovery upload protects the closed training evidence once acknowledged.
Saved Actions jobs remain in the report even when no campaign artifact survived;
missing evidence does not mean zero observations. Failed history is preserved. Tool clone/build time,
campaign elapsed time, command times/return codes, process/resource samples and early
termination are reported. Unmeasured manual preparation remains unmeasured.

Before the final report, reconcile the declared inventory with repository Actions
runs since the first v4 code commit, `42ebf33223da579fc68533f2b5c07aa1c4f97f68`
(2026-10-28 03:28:33 UTC), through the stated report snapshot. Include CI, including
failed and documentation-only checks, as shared preparation overhead alongside
campaign, worker, qualification, diagnostic, report and archive jobs. Do not
allocate shared CI overhead as instrumentation cost to one source. Earlier
iterations and independent product development remain outside this v4 automation
window; human/agent effort is unmeasured. Earlier interim ledgers retain their
original declared subsets; the final snapshot uses the reconciled inventory above.

## 11. Discussion, limitations and conclusions

The current evidence supports a precise, conditional statement: eBPF observations
can supply an actual recovered graph that an existing simulator uses to predict
independent outcomes for some applications and operations without native tracing.
Petclinic also demonstrates recovery of a shared-DB dependency used in prediction
under declared identity and business contracts. These observations are not evidence
that all protocols, operations or native tracing modes are interchangeable.

Graph accuracy and useful forecast coverage are separate. A correct available
forecast does not resolve operations for which a mandatory call is absent or
ambiguous. Similarly, a database node is not useful fault information until its
identity, callers and mandatory role are established and the simulator uses it.
The source comparison retains full native DB spans; database discovery is not
claimed as exclusive to eBPF. The saved Petclinic full-mode native observations
also support the shared-DB fault predictions. The eBPF result is recovery without
native tracing, not extra DB information beyond full native tracing.

A [preliminary diagnosis](docs/PRELIMINARY_DIAGNOSIS.md) separates collector,
graph-joining and evaluation effects without changing the reported results.
For OTel, exact entry roots survive in inspected partial/full examples while
required downstream graph edges disappear. Native/non-recording context interacting
with OBI and Bering's exact source-local parent join is a concrete hypothesis;
the missing raw parent correspondence is not yet proven. The async check also
requires consumer SpanLinks and does not implement alternative ID-only joins.
For classes, saved examples directly show one route-defined operation split by
empty, nonempty and repeated descendant signatures under exact matching.
These findings cannot all be attributed to the eBPF collector.

Collector choice can nevertheless affect protocol recognition, available
identifiers and context association. The empirical limits here concern OBI
v0.15.2 and the actual configuration and processing method. Documentation for
another collector is not an observed improvement, and no collector replacement
was evaluated in this follow-up.

The direct supplied-contract predicate equals the available primary replica-failure
forecasts.
Monte Carlo does not improve equivalent arithmetic. The study therefore does not
establish better external predictions than that baseline. It also does not establish
less overall preparation effort: manually supplied contracts, request/step grouping,
identity and placement information remain essential, and their human costs are
unmeasured. A class ARI of 1 does not establish automatic business semantics, and
additional downstream features can reduce coverage or label agreement.

OBI runs in every campaign, and source arms replay observations from the same
campaign. These measurements do not isolate OBI's acquisition overhead against an
uninstrumented deployment. Nominal primary load also coexists with recorded
preparation and verification traffic, which can affect the application.

Other limits are the common physical Actions host, three repeats per cell, one
selected collector configuration, application-specific contracts and limited
intervention scope. Nonintervened components are held conditionally live; Sheaft's
connectivity model does not simulate queue timing, transactional semantics or
durable delivery. Native collector queries and instrumentation may themselves have
incomplete coverage. Bering versions differ between the retained earlier cells and
later cells, with each revision explicitly recorded; valid cells were not rerun to
remove that difference. Negative and unknown results are retained without accuracy
thresholds or artificial response deadlines.

Technical repairs, including failed deployments/replays, memory pressure, unavailable
logs and excessive converter file counts, remain in the run history and cost ledger.
Historical qualification proves only the input and capacity it actually exercised.
Independent review checks final claims against retained artifacts, rather than
treating CI, manifest validity or graph quality flags as the contribution.
The [independent review record](docs/REVIEW_V4.md) documents these distinctions
and its verification scope. The defensible finding is specific applicability of
the observed graph-to-simulation path together with measured coverage failures;
the original full-effort usefulness advantage remains unestablished.

[OpenTelemetry eBPF Instrumentation]: https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.15.2
[Procrustes]: https://github.com/MB3R-Lab/Procrustes/tree/39f76000f8a39c971155e08ebffde829b525911b
[Bering]: https://github.com/MB3R-Lab/Bering
[Bering v1.1.1]: https://github.com/MB3R-Lab/Bering/releases/tag/v1.1.1
[Sheaft]: https://github.com/MB3R-Lab/Sheaft
[Sheaft v1.3.2]: https://github.com/MB3R-Lab/Sheaft/releases/tag/v1.3.2
[mb3r-stack v1.3.0]: https://github.com/MB3R-Lab/mb3r-stack/releases/tag/v1.3.0
[DeathStarBench Social Network `6ecb097`]: https://github.com/delimitrou/DeathStarBench/tree/6ecb09706140f8730b5385c08f1386c654c3c526
[OpenTelemetry Demo 3.0.0 `8c47d47`]: https://github.com/open-telemetry/opentelemetry-demo/tree/8c47d47c9ac27710d2b2a153bcd53e483bffe66d
[Spring Petclinic Microservices `3858f9c`]: https://github.com/spring-petclinic/spring-petclinic-microservices/tree/3858f9c630cf989bb6809a86edf47c2be78dc9f1
