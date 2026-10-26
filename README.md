# Discovering operation models from eBPF observations in distributed applications

**Research status: the measurement series is running; technical failures and completed acquisitions are being reviewed. No final accuracy or enrichment result is claimed.** This README is the evolving research report. A green deployment job is not a successful research result. The [run history](docs/RUN_HISTORY.md) retains failed preparations and the superseded protocol pilot.

## Abstract

Application traces can support discovery of execution dependencies and operation-success models, but many projects have no tracing or incomplete coverage. This empirical study tests whether eBPF observations can supply sufficiently useful evidence in those settings. Ten operations from DeathStarBench Social Network, OpenTelemetry Demo, and Spring Petclinic Microservices run across two Linux virtual machines with independent kernels. We compare absent, partial, and full application tracing; calibrate under four controlled replica states; and predict success under a new mixture of those states. Independent HTTP content and database checks evaluate the predictions. Additional controls examine operation classes, cross-machine execution links, database dependencies, and asynchronous checkout/accounting. Measurements are in progress; conclusions await the complete series and review of the retained evidence.

## Motivation and research questions

The contribution sought is empirical evidence about applying model discovery and simulation with missing instrumentation. We do not introduce a new discovery algorithm or assume that eBPF necessarily provides more information than native tracing.

1. Can evidence acquired without complete application tracing support useful predictions on an independent workload?
2. Which execution links remain identifiable across processes, replicas, and independent Linux kernels?
3. Can observed method/route signatures identify operation classes, and does downstream execution add useful separation?
4. Does eBPF recover database dependencies missing from the available native traces? Does an addition affect an independently validated prediction?
5. Can a synchronous checkout response be connected to its asynchronous accounting effect using actual order/message identity?

The practical forecast target is mean absolute error at most **5 percentage points per operation**, across three repeats of each tracing mode. This is an evaluation target, not a condition for publishing a run. Unknowns, wide intervals, and failures remain visible.

## Context and scope

Native traces can already include database client spans and database attributes. Adding a DB node is therefore not intrinsically an eBPF advantage. Full tracing retains all collected DB spans; traces, eBPF, and their combination are compared on actual evidence. See the [OpenTelemetry database conventions](https://opentelemetry.io/docs/specs/semconv/database/).

[OpenTelemetry eBPF Instrumentation (OBI)](https://opentelemetry.io/docs/zero-code/obi/) is the first acquisition path. We use release 0.15.2 and retain resolved image digests, configurations, and collector diagnostics. Documented [protocol instrumentation](https://opentelemetry.io/docs/zero-code/obi/configure/export-data/) motivates a test; it does not prove recovery of these application operations. One bounded [DeepFlow](https://github.com/deepflowio/deepflow) fallback is allowed for a system with missing necessary protocol evidence. This is not a collector benchmark.

The operation set and controlled-replica approach continue the [SIMPAT experiment repository](https://github.com/a-a-k/telemetry-availability-identification). This study does not reuse an unconditional forecast under a changed state distribution: conditional-state weighting makes the transfer explicit. The [protocol](docs/PROTOCOL.md) records the criterion, equivalent direct baseline, and prior independent skeptic GO.

## Applications and environment

| Application | Pinned source | Operations | Controlled replicas |
|---|---|---|---|
| DeathStarBench Social Network | [`6ecb097`](https://github.com/delimitrou/DeathStarBench/tree/6ecb09706140f8730b5385c08f1386c654c3c526) | Compose post; home timeline; user timeline | User-timeline A/B |
| OpenTelemetry Demo 3.0.0 | [`8c47d47`](https://github.com/open-telemetry/opentelemetry-demo/tree/8c47d47c9ac27710d2b2a153bcd53e483bffe66d) | Browse product; add to cart; checkout | Product-catalog A/B |
| Petclinic Microservices | [`3858f9c`](https://github.com/spring-petclinic/spring-petclinic-microservices/tree/3858f9c630cf989bb6809a86edf47c2be78dc9f1) | List owners; owner details with visits; create visit; list vets | Visits A/B |

Each campaign creates two Ubuntu guests using QEMU/KVM on one standard public GitHub Actions Linux runner. Each has its own kernel, boot ID, network stack, Docker daemon, and eBPF collector. Guest addresses are `192.168.76.11` and `.12`; their separate Docker subnets are `172.28.11.0/24` and `172.28.12.0/24`. Cross-guest calls use published guest ports, because qualification did not establish direct Docker-subnet reachability. Replicas A/B reside on different guests. Routing remains fixed during replica failures.

```mermaid
flowchart LR
  H[Actions runner: workload and evidence]
  A[Guest A: application services, replica A, OBI]
  B[Guest B: replica B, OBI]
  H --> A
  A <--> B
  A --> H
  B --> H
```

The shared physical host is a limitation: these experiments exercise inter-kernel execution and networking, but not independent physical-machine failures. KVM and readable guest BTF are required. Infrastructure failures are recorded; two containers are not substituted for two machines, and paid runners are not connected automatically.

The default allocation is two vCPUs and 6 GiB per guest when runner memory permits. Host resources, guest allocation, kernel versions, boot IDs, cloud-image checksum, application image digests, and resolved Compose configurations are retained. The guest image is pinned to Ubuntu Noble's 2026-10-17 build, SHA-256 `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`.

Deployment changes and manual knowledge are detailed in the [DeathStarBench](systems/deathstarbench/README.md), [OTel Demo](systems/otel_demo/README.md), and [Petclinic](systems/petclinic/README.md) notes. These are real pinned upstream systems, not replacement services producing synthetic spans.

## Method and information boundaries

### Acquisition

OBI runs on both guests in every tracing mode. Exclusion of already instrumented services is disabled. Automatic eBPF context propagation is enabled and recorded. OBI Java-agent and Node.js runtime injection are disabled in the current configuration; this may limit language-specific correlation and is part of the interpretation of coverage. The experiment also captures SQL query text and HTTP bodies on `/api/*` to inspect business-identity evidence. These are synthetic application fixtures. Oracle CLI processes, Jaeger, native collectors, and the fallback collector are excluded from OBI targeting.

Every workload HTTP step carries a unique opaque `X-Experiment-Request-Id`. Only this header is selected for OBI enrichment. It contains no operation name, dependency map, or outcome. It binds the request census to an observed entry span; it does not establish a downstream link. Native header capture is requested where supported, with support checked in actual spans. The generator does not inject sampled `traceparent` or Jaeger contexts.

eBPF and native raw records have separate provenance. The receiver records OTLP JSON versus protobuf encoding; normalized trace/span identifiers use hexadecimal. Native Jaeger exports are also supported. Missing or malformed observations are recorded rather than replaced.

### Discovery and evaluation

The learner receives observed spans and a restricted census: opaque attempt keys, ordered opaque step IDs, phase, and controlled state. It does not receive operation labels, response bodies, SQL oracle results, or expected dependency maps. Grouping HTTP steps into one attempt is supplied workload knowledge; this is not automatic business-process segmentation.

The evaluator separately receives labels, fixture expectations, request/response evidence, and SQL observations. Deployment manifests are references for placement and DB identity, not discovered topology. Both simulation and the direct weighted baseline receive the same permitted evidence and state weights.

The basic class representation uses observed method and normalized route; an augmentation uses confirmed downstream signatures. Healthy training and test segments are separate. Generator labels are evaluation-only. Missing anchors and ambiguous classes remain unknown. Unclassified calibration attempts must widen compatible classes' bounds rather than disappear from denominators. Class assignment rules are fixed before target acquisition.

The combined source is a deterministic union. Where several sources describe an HTTP step, projection selects the earliest observed server boundary, with an eBPF tie preference. This is not an optimized fusion method: differently normalized routes or incomplete observations can fragment classes, and adding a stream need not improve the result.

Service instances and placement use available resource/process attributes and collector provenance. A cross-node link requires observed parent/child or message identity. A connection, common topic, or temporal proximity is insufficient. Observed link counts are distinct from an independently validated link-error rate; the latter is unknown without a reference.

Database analysis distinguishes logical address, concrete instance evidence, and dependencies shared by multiple services. Known database ports alone do not identify an operation's dependency.

Native database activity named in spans is retained even when endpoint attributes are absent. For example, a named Mongo client call is evidence of activity, not proof of a particular Mongo instance. Unknown endpoints are scoped to their callers and cannot establish a shared database. Observed protocol labels are never corrected using the deployment reference: endpoint agreement and protocol agreement are separate evaluation fields.

For asynchronous execution, the implemented message matcher requires a unique checkout producer, an accounting consumer's exact SpanLink to that producer, and a PostgreSQL write sharing the consumer's exact processing-root ancestry. All IDs must be unambiguous within one source. Combining streams does not lend native message identities to eBPF. The retained proof establishes association; the independent SQL oracle establishes whether the correct order arrived before its deadline.

### Conditional execution model and simulation

The four states `11`, `10`, `01`, and `00` indicate replica availability. Target weights are `(4,2,1,1)/8`. For class c, exact integration is `p(c) = sum_s w(s) p(c | s)`. Monte Carlo uses 100,000 draws from the same conditional model and is checked against exact integration.

Reported point estimates use exact integration when the identification bounds coincide; Monte Carlo endpoints and their deviations are retained separately. The simulation check rejects a deviation above one percentage point. Thus zero reported point error is not a claim that a finite random simulation produces exactly the same number. The final report exposes these saved values in `simulation.csv` and fitting/integration timers in `model-costs.csv`; each integration timer includes the exact calculation and simulation together.

Direct stratified estimation is algebraically equivalent and is the strongest simple baseline. Simulation is not claimed to improve it. Potential usefulness comes from acquiring evidence despite missing tracing and is judged against external outcomes. The current implementation design uses the joint observed entry-status/deadline event as a proxy; semantic mismatches must be measured independently. Products of independent per-step success rates are not substituted for joint outcomes.

Model and forecast files are saved before target acquisition. Unknown outcomes yield bounds, not fabricated point estimates. Adding graph structure that does not affect the calculation is not a forecast improvement. HTTP status/duration alone does not implement durable asynchronous completion.

Uncertainty uses weighted nominal pointwise 95% Wilson envelopes under an iid Bernoulli assumption. Within-block temporal dependence is not estimated, so these are not validated 95% predictive intervals or simultaneous confidence bounds. Worst-end error and interval width are reported separately from point error.

## Experimental design

**27 campaigns:** three systems × three actual tracing modes × seeds `0`, `1`, `2`.

- `absent`: native tracing disabled; eBPF available.
- `partial`: native tracing disabled on both controlled replicas; other native traces and eBPF available.
- `full`: native tracing enabled throughout the deployed application; eBPF also recorded.

Suppression is checked through configuration and retained telemetry. A disconnected exporter alone does not prove disabled instrumentation.

| Segment per campaign | Blocks | Seconds/block | Operations/s | Attempts |
|---|---:|---:|---:|---:|
| Healthy class training | 1 | 30 | 4 | 120 |
| Calibration, one block per state | 4 | 60 | 4 | 960 |
| Independent target, state counts 4/2/1/1 | 8 | 30 | 4 | 960 |
| Healthy class test | 1 | 30 | 4 | 120 |
| **Primary total** | **14** | | | **2,160** |

The primary series contains **58,320 operation attempts**. Multi-step operations generate more HTTP requests; this is not a packet or span count. Each application's mixture is balanced. Reset, readiness, settling, and outstanding-work completion happen between blocks and count toward cost.

Every block uses the same fixed preparation: one unscored warmup per operation present in that block, a ten-second settling period, and a ten-second drain guard after scored futures and oracle checks complete. Warmups are recorded and never repeated until success. The guard is a bounded preparation rule, not proof that arbitrary background work has ended. A prior pilot using different preparation is retained separately and excluded by protocol version.

The external predicates are declared independently of the observation model. The primary HTTP deadline is two seconds for the complete operation, including all of its HTTP steps.

| Operation | External success predicate in addition to the deadline |
|---|---|
| Compose post | HTTP 2xx and the upstream upload acknowledgement; eventual fan-out is recorded separately |
| Home timeline | HTTP 2xx, well-formed posts, and the exact stable followed-user fixture |
| User timeline | HTTP 2xx, well-formed posts, and the exact stable owner fixture |
| Browse product | HTTP 200 and the requested fixture product ID |
| Add to cart | Product prerequisite succeeds; returned cart contains the fixture product with quantity one |
| Checkout | Product and cart prerequisites succeed; HTTP 200 returns an order ID; durable accounting is a separate outcome |
| List owners | HTTP result matches the pinned seed-data oracle |
| Owner details with visits | Owner/pet fields and all expected visits match the seed-data oracle; an HTTP 200 fallback without visits fails |
| Create visit | HTTP 201 plus exactly one independently queried MySQL row matching returned ID, pet, date, and unique description |
| List vets | HTTP result matches the pinned seed-data oracle |

### Database controls

Each campaign performs 20 attempts with its selected DB available and 20 unavailable, on the same deployment: 1,080 additional attempts overall. Detected dependencies are checked against behavior. Caches can mask outages; that is a result, not permission to infer outcomes from topology. Structural additions and prediction changes are reported separately.

### Asynchronous controls

OTel Demo uses its existing `checkout → Kafka → accounting → PostgreSQL` chain through the full Compose configuration. Each OTel campaign adds 20 checkouts in normal operation, 20 with accounting stopped, and 20 after recovery: 540 additional attempts overall.

Immediate success requires the HTTP result within two seconds. Durable success requires the correct order and items to be observed in PostgreSQL within ten seconds of operation start. Producer API return, HTTP 200, topic name, and Kafka request correlation ID do not establish durable completion or identify the consumer's business event.

Accounting remains stopped until all deadlines expire; the queue is drained before the recovery block. A first positive DB observation after the deadline cannot prove timely success. These controls do not claim prediction of an uncalibrated consumer-failure regime.

## Outcomes, uncertainty, and cost

Evaluation retains every operation, tracing mode, and repeat. Outputs include signed/absolute forecast errors, uncertainty intervals, external success, unknown fractions, class ARI, supported cross-node links, database dependencies, and costs. Conservative interval error for `[L,U]` and external rate y is `max(|L-y|,|U-y|)`. Width above 10 percentage points is insufficiently informative. Per-attempt proxy-versus-business mismatches prevent compensating semantic errors from disappearing inside an aggregate.

Costs include preparation, downloads/builds, VM startup, acquisition, state changes, settling, queue draining, oracle queries, inference, simulation, analysis, and technical failures. Job duration and machine resources accompany measured process timings. Manual semantic declarations and engineering work are described separately, not treated as free automation.

## Results

**The series is incomplete: 18 of 27 campaigns have valid results.** The [reviewed interim tables](results/interim-18/report.md), [per-repeat operation data](results/interim-18/operations.csv), and [artifact provenance](results/interim-18/SOURCE.md) were generated in [Actions report 40362124923](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40362124923). They contain 38,880 admitted primary attempts; OTel is still outstanding. Independent review approved reporting this partial evidence, not a claim that the full research criterion has been established.

For DeathStarBench, all three eBPF entry-event forecasts have zero point error across the three repeats in each mode. Conservative mean worst-end error is 4.01 pp for compose/user timeline and 4.58 pp for home timeline, meeting the stated target. Native partial/full observations produce the same forecasts. This result concerns conditional entry outcomes: OBI does not reconstruct the internal Thrift execution topology in these captures.

Petclinic does not meet the conservative target for any operation/mode group. In full mode, list owners and list vets have zero point error but 6.02 pp worst-end error under the nominal interval construction. Owner details has 12.50 pp point error: HTTP 200 can omit required visits. Create-visit forecasts and several absent/partial forecasts retain unknowns. These are limitations of the tested observation/projection procedure and semantic proxy, not proof that all eBPF approaches fail.

The [class results](results/interim-18/classes.csv) preserve coverage alongside ARI. For example, Petclinic absent seed 0 has route ARI 1.0 on all 120 test attempts, while the downstream augmentation has ARI 0.5122 on 119 attempts. Additional downstream detail therefore did not automatically improve this representation. [DB activity](results/interim-18/database-activity.csv) includes native Mongo calls even without endpoint attributes; [structure results](results/interim-18/structure.csv) retain OBI's Mongo-to-MySQL misclassification. No DB-driven forecast improvement or independently validated cross-node error rate is established.

![Interim worst-end errors by operation, source and repeat](results/interim-18/errors.svg)

Each marker is one repeat's worst-end error, including conservative bounds for unknown forecasts; it is not necessarily a point-estimate error. The dashed line is 5 pp. The [cost ledger](results/interim-18/job-costs.csv) records 71,928 completed job-seconds through this report's snapshot, including preparation and failures. Ongoing work and unmetered engineering time are not included as zero.

| Stage | Evidence | Interpretation |
|---|---|---|
| Adapters | Three implementations and [focused checks](.github/workflows/checks.yml) | App-specific deployment, workload and independent outcome checks |
| Two-kernel infrastructure | [Passed first technical run](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40324200754) | Two distinct boot IDs, kernel 6.8.0-147, BTF, 6 GiB per guest; infrastructure only |
| Protocol support | [Technical attempts and repairs](docs/RUN_HISTORY.md) | DSB Mongo endpoints are mislabelled as MySQL by OBI; labels are retained. Exact native Kafka message chains passed qualification; eBPF-only recovery is not presumed |
| Petclinic series | [Initial jobs](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40335553492), [partial repairs](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40341237065), [full repairs](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40342667653) | All nine campaigns acquired and evaluated; failed exporter snapshots retained |
| DSB series | [Absent campaigns](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40336898753), [partial replacements](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40349570169), [full replacements](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40349582587) | All nine admitted campaigns acquired and evaluated; six invalid native-baseline campaigns explicitly excluded and retained |
| OTel series | [Recovery qualification](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40370126016), [absent](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40372011776), [partial](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40372023737), [full](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40372035878) | Nine replacements running after reset-permission and admin-JVM repairs; all incomplete attempts retained |
| Final empirical review | Pending | No overall accuracy or enrichment claim |

Technical reruns retain the failed attempt and its cause. The series is not expanded to obtain positive results.

The [first permanent data archive](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40362321620) retains original campaign/qualification artifact ZIPs and workflow logs through OTel attempt `40351820494`, including failed preparations, the superseded pilot, and intermediate reports. Its `SHA256SUMS.txt` and `provenance.tar.gz` identify the exact assets and source runs. Later acquisitions will have a separate archive; this release does not represent a completed series.

## Discussion and limitations

Guests share physical resources. Four controlled states provide a restricted transfer test, not arbitrary failure extrapolation or failure-transition dynamics. Target mixture weights are supplied. Fixed application versions and three repeats limit generalization. Workload grouping and semantic rules include manual knowledge. Protocol/language coverage can leave links unknown. Context propagation changes metadata and affects interpretation of portability and cost. Full native tracing may already contain every database dependency eBPF recovers.

All native observations here are collected while OBI is also running. They are a paired observation-source reference, not a separate native-only runtime experiment; automatic propagation can affect the parent contexts native spans observe. Collector overhead was not isolated experimentally. The conditional forecast uses entry events rather than the full dependency graph, so accurate forecasts do not establish recovery of an application's internal call topology. Equivalent direct estimation from sufficiently complete HTTP observations can produce the same forecast; the study makes no claim that eBPF is necessary or cheaper than that alternative.

The downstream class representation uses the observed service/route names. Replica-specific names and variable child calls can fragment one business operation into several observed classes; a lower augmented ARI is not proof that downstream information is inherently unhelpful. No extra representation search is performed after inspecting results. A DB endpoint match is evaluated separately from protocol correctness and concrete-instance identity. Native ancestry is an independent telemetry reference, not ground truth for every eBPF link. Order-chain matching supports declared current-order fields; unimplemented alternative message matchers remain a limitation.

The [Petclinic cross-node audit](docs/petclinic-cross-node-audit.md) identifies two distinct reference limitations. Native and eBPF server spans for the same request can have different span IDs, which the strict reference binder does not reconcile. Even after an exact opaque-request/method/path match, the native child points to an eBPF proxy parent that has no native counterpart. Matching requests therefore does not supply an independent native parent reference. Cross-node correctness remains unknown rather than being inferred from matching traces or deployment placement.

Database counts distinguish observed structure from validated dependencies. Endpoint/protocol agreement is checked against the selected intervention database; other endpoints are not all independently validated. An observed shared address is not automatically a confirmed dependency shared by application services: collectors may also describe database processes as clients. These counts must not be read as a count of correctly recovered business dependencies, and no concrete physical database-instance identity is established by address alone.

## Reproduction

Application execution and research computation run in GitHub Actions. Local activity is editing, static checks, and focused unit checks.

```bash
gh repo clone a-a-k/ebpf-model-discovery-experiments
cd ebpf-model-discovery-experiments
gh workflow run infrastructure.yml
gh workflow run qualification.yml -f system=all -f mode=absent
gh run list
gh run view RUN_ID
gh run download RUN_ID -D downloaded/RUN_ID
```

`qualification.yml` accepts `all`, `deathstarbench`, `otel_demo`, or `petclinic`, and `absent`, `partial`, or `full`. It creates two guests, starts collectors, exercises a small healthy census, exports observations/oracles, and tears down. This technical check does not replace a campaign. Runs and artifacts are linked from [Actions](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions).

The fixed campaign interface and report regeneration are implemented:

```bash
gh workflow run campaigns.yml -f system=all -f mode=all -f seed=all
# A technical rerun can select one system, mode, and seed; preserve the prior run.
gh workflow run report.yml -f run_ids='CAMPAIGN_RUN_ID ANOTHER_RUN_ID'
# Replay the same originals from permanent releases after Actions artifacts expire.
gh workflow run report.yml -f run_ids='40336898753' -f archive_tags='data-40362321620'
# Retain original artifact ZIPs beyond Actions expiry, including failed attempts.
gh workflow run archive.yml -f run_ids='CAMPAIGN_RUN_ID QUALIFICATION_RUN_ID PILOT_RUN_ID'
```

Campaigns must follow successful deployment and observation qualification and implementation review. A campaign saves its model, forecast, evaluation map and their hashes before target traffic. Report replay preserves the original target classifications and proxies byte-for-byte, and checks the saved model/forecast/map hashes. Independent database and message-chain audits can reparse the raw streams with recorded evaluation-code provenance; this never refits the predictor. Original metrics remain beside the regenerated metrics. The report requires all three distinct seeds for an aggregate and rejects duplicate admitted campaigns. Missing files do not represent successful empty experiments. Selector-only matrix jobs are not campaigns. Artifacts expire after 90 days; the archive workflow publishes original ZIPs, checksums and provenance in a GitHub release.

Report outputs include `operations.csv`, `summary.json`, `classes.csv`, `structure.csv`, `database-controls.csv`, `async.csv`, error figures, example observed graphs, and per-campaign models/metrics under `evidence/`. `job-costs.csv` covers repository preparation, checks, failures and reruns, while `costs.csv` contains valid-campaign timings. Ongoing job time and unmetered engineering time are explicitly unknown. Nominal Wilson envelopes may exceed the conservative 5 pp target even when point error is zero; both measures remain visible.

`archive_tags` can name several space-separated data releases. Archived replay verifies original ZIP checksums before extraction and uses the same evaluation and exclusion rules. The job-cost ledger is a new repository-history snapshot when replay runs; use the archived report's ledger for the original cost snapshot. A missing release, asset, checksum, or campaign provenance stops replay instead of silently omitting a run.

The archived path passed [replay run 40365033726](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40365033726): the admitted DeathStarBench absent-mode summary groups exactly matched the earlier report, while the same six excluded campaigns remained excluded. This replay generated no application traffic.

```text
.github/workflows/       Infrastructure and application qualification
docs/PROTOCOL.md         Criterion, baseline, design, skeptic review
docs/ADAPTER_CONTRACT.md System interface and information boundaries
scripts/vms.sh          Independent guests and routed networking
src/ebpf_discovery/     Acquisition and observation normalization
systems/               Deployments, workloads, independent oracles
results/               Run artifacts (large files uploaded by Actions)
```

Artifacts include `qualification.json`, `deployment.json`, `commands.jsonl`, `external.json`, `observation-support.json`, separate `observations/` and `native/` directories, and diagnostics. Infrastructure uploads exclude SSH private keys and guest disks. Image/source provenance is retained; mutable references are not described as immutable.

## Conclusions and sources

The study is incomplete. Conclusions will identify operations/settings that did or did not meet the external criterion, with unknowns and costs. Collection, plausible graphs, and agreement with equivalent arithmetic alone do not establish useful discovery.

- [Existing SIMPAT experiments](https://github.com/a-a-k/telemetry-availability-identification).
- [DeathStarBench](https://github.com/delimitrou/DeathStarBench).
- [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo) and [accounting](https://opentelemetry.io/docs/demo/services/accounting/).
- [Petclinic Microservices](https://github.com/spring-petclinic/spring-petclinic-microservices).
- [OBI v0.15.2](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/tree/v0.15.2), [discovery](https://opentelemetry.io/docs/zero-code/obi/configure/service-discovery/), and [enrichment](https://opentelemetry.io/docs/zero-code/obi/configure/metrics-traces-attributes/).
- [DeepFlow](https://github.com/deepflowio/deepflow).
- [QEMU system documentation](https://www.qemu.org/docs/master/system/index.html).
