# Graph discovery from eBPF observations and external outcome prediction

The agreed objective and completion criteria are recorded in [docs/GOALS.md](docs/GOALS.md).

> **Current status (iteration 4): retained replay verified; no scientific-series results.**
> [The first three qualification jobs](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40655022146)
> each acquired 240 planned requests, then failed on an invalid Procrustes goal
> before discovery. Per-step goals and ancillary Sheaft predicates are repaired;
> [The repaired retained replay](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40674465933)
> reached actual Sheaft simulation for all four Petclinic operations using eBPF alone,
> with shared-DB fault forecasts for the three operations with unconditional DB obligations
> in the supplied network-scope variant. DSB and OTel eBPF-only branches still lack
> required service paths. [The first three planned full/seed6 campaigns](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40704758284)
> launched at `fdec1a6`. OTel and Petclinic received runner shutdown signals during
> graph discovery after training acquisition; their artifact uploads were skipped.
> The logs do not establish the shutdown cause. DSB's acquisition step also failed
> and its upload steps were skipped; final platform status/logs are pending. A reviewed
> technical repair adds a saved training checkpoint, streamed input and measured
> swap. After independent review and 413 passing Linux tests, the unchanged failed
> cells were relaunched: [OTel](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40718665137)
> and [Petclinic](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40718674400).
> Both saved training checkpoints and continued on the same guests. The reviewed
> [DSB retry](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40731158179)
> is also launched; the explicitly failed original acquisition remains in the history.
> Their outcomes are pending. Retained replay does not
> measure fresh predictive accuracy or full-campaign capacity.

Iterations 1–3 are retained unchanged in [README.iteration-3.md](README.iteration-3.md),
with their captures, reports, timing rules and conditional-state predictors. Those
historical predictors did not consume the recovered graph. Their results must not be
read as evidence for the graph-to-simulation claim tested here.

Original iteration-4 qualification captures and all four retained replay attempts,
including the failed replay, are preserved with workflow logs, metadata and checksums
in [this permanent data release](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40704387111).

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

The causal source of any additional value must be recovered structure that changes a
sound prediction: for example, a required observed call or selected database edge.
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

Iteration 4 builds exact source revisions in every GitHub Actions campaign:

| Component | Revision or release | Role |
|---|---|---|
| [OpenTelemetry eBPF Instrumentation] | `v0.15.2` | kernel-side HTTP and database observations without application SDK instrumentation |
| [Procrustes] | `39f76000f8a39c971155e08ebffde829b525911b` | static deployment preflight and confirmed identity/replica facts |
| [Bering v1.1.1] | `dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3` | source-domain-aware OBI/native discovery and graph publication |
| [Sheaft v1.3.2] | `686a602f4e7b71f3612f1810885e29dd66c8733a` | edge-aware predicates and deterministic state-profile simulation |
| [mb3r-stack v1.3.0] | released integration bundle | published product integration reference, not the experiment runner |

The workflow reads each tool's declared Go version, downloads the corresponding
official Go archive, verifies its digest, builds with `GOTOOLCHAIN=local`, and records
source commit/tree, binary hash, size, clone time and build time. The experiment does
not substitute an unpinned container or a locally installed binary.

Procrustes reports are consumed conservatively. Only `CONFIRMED` identity and replica
facts can attach to nodes already observed by Bering. An unmatched inventory item
stays in the sidecar; it cannot create a node or edge. Custom workload scenarios are
not fabricated to make static preflight pass.

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
expected edges to the recovered graph. A required call must resolve to an observed,
unambiguous Bering edge. Missing structure produces an unavailable prediction with a
reason. Conditional calls remain unknown when their condition is not established.

The fixed inputs intentionally avoid injecting an expected topology:

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

The planned series contains 939,600 primary attempts. Calibration/discovery blocks
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
requires both customers→MySQL and visits→MySQL edges. Both must remain present in the
edge-aware predicate; merging them into one generic “database exists” node would make
the fault prediction unsound. OTel selects catalog PostgreSQL. DSB selects
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

## 9. Reproduction, workflows and retained artifacts

All application builds, traffic, raw-data processing, discovery, simulation and report
generation run in GitHub Actions. Local work is limited to static/unit fixtures; the
evaluator CLI rejects research processing outside `GITHUB_ACTIONS=true`.

The manual workflows are:

- [qualification-v4.yml](.github/workflows/qualification-v4.yml): three full-mode
  technical qualifications by default, with reviewed diagnostic inputs;
- [series-v4.yml](.github/workflows/series-v4.yml): the fixed 27-cell matrix, maximum
  parallelism three, with exact-cell inputs for reviewed staging or technical reruns;
- [report-v4.yml](.github/workflows/report-v4.yml): aggregate saved cell evaluations
  and complete Actions job/artifact costs, including declared failed preparation runs;
  render per-operation figures from that saved aggregate as SVG, PNG and PDF.

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
```

Artifact upload steps run on ordinary job failures, with raw-data-friendly compression
and 90-day workflow retention. Abrupt runner loss can skip those steps; the separate
pre-discovery upload protects the closed training evidence once acknowledged.
Saved Actions jobs remain in the report even when no campaign artifact survived;
missing evidence does not mean zero observations. Failed history is preserved. Tool clone/build time,
campaign elapsed time, command times/return codes, process/resource samples and early
termination are reported. Unmeasured manual preparation remains unmeasured.

## 10. Current limitations, review state and references

Iteration 4 currently has no scientific-series results. The first qualification
exposed an invalid static-analysis input, repaired in `1284a5f`. Retained-capture
replay can diagnose the actual tool path but cannot establish concurrent VM/tool
resource capacity. Independent review approved the first three planned cells;
each system's remaining eight follow its own resource and protocol-validity review.
The evaluator/cost component has passed independent review. After the
series, the original criterion must be checked again against the external outcomes and
the strongest baseline before any success claim.

The principal limitations are known in advance:

- contracts and placement inventory are supplied semantic knowledge, not discovered;
- the driver supplies operation/step grouping for the class diagnostic;
- the two guests share one physical runner;
- deterministic connectivity profiles assume every nonintervened required component
  and edge is live and business logic/inputs remain correct;
- Sheaft connectivity does not model queue durability, latency or transactional
  semantics;
- OBI/native protocol coverage can be absent or ambiguous, and such cases stay unknown;
- Monte Carlo adds no mathematical advantage over the exact deterministic check;
- preparation effort is incomplete because human/agent time is unavailable.

Published product releases establish usable tooling, not empirical adequacy for this
study. Historical iteration-3 evidence and limitations remain available in
[README.iteration-3.md](README.iteration-3.md), [generated iteration-3 results](results/iteration-3/report.md),
and [run history](docs/RUN_HISTORY.md). They are not pooled with the fresh seeds.

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
