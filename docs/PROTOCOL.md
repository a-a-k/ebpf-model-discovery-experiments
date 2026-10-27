# Protocol and pre-execution hypothesis review

Date: 2026-10-26. Current user criterion: an empirical possibility study, not a new-algorithm or universal superiority claim.

## Original criterion

Discover operation models from real eBPF evidence when native application tracing is absent or partial; use those models to forecast independent operation success under a changed distribution of controlled fault states. Evaluate all ten SIMPAT operations on three applications, genuinely distributed across two Linux guest kernels. Also evaluate operation classes, database-node enrichment and a real asynchronous operation chain.

## Baseline, causal mechanism and verdicts

Strong simple baseline: direct conditional-state estimation from the same permitted observations, semantic declarations, calibration population and target state weights. It is algebraically equivalent to exact integration of the same empirical execution event; Monte Carlo is an implementation of that integration, not an estimator improvement. Full native traces are an observation reference and include their database client spans.

Possible practical benefit comes from acquiring useful execution evidence without complete application instrumentation, including cross-node and missing database dependencies. It does not follow merely from a larger graph, a tool's protocol support, or internal admission statuses.

Costs include setup, manual mapping, acquisition, settling, failures, interpretation and simulation. Samples and budgets are fixed; there is no outcome-driven extension or repetition until success. Technical failures can be repaired and rerun with the original attempt retained.

Orchestrator verdict: GO for testing the original current criterion, with external validation and explicit unknown outcomes. Reviewer verdict: **GO**, supplied by the separate GPT-6.1 Sol/xhigh reviewer in this conversation before implementation. Successful Kafka collection is not assumed. An unsupported async result fails to establish that capability and is not relabelled as successful topic-graph discovery. Actual results require a final review before any success claim.

Implementation clarification reviewed on 2026-10-26: separate reviewer GO for the joint observed HTTP status/deadline proxy, with external semantic success unchanged as the criterion. Multi-step grouping is supplied knowledge. Unknown-class calibration attempts widen all compatible classes' bounds; they cannot be discarded. Class rules are fixed before target acquisition. Per-attempt proxy/semantic mismatches are reported. Durable async completion still needs actual identity/completion evidence, independently evaluated; an HTTP proxy is insufficient.

Pilot/code validity review on 2026-10-26: orchestrator and independent 6.1 Sol/xhigh reviewer GO to continue `fixed-warmup-v2`, without an empirical-success verdict. The retained pilot preserves semantic proxy mismatches and unknown native forecasts. Review repairs include exact Wilson boundary handling, nominal iid uncertainty labeling, complete preparation/failure job costs, exact published DB endpoint matching, and rejection of previous-order identifiers. Native exporters use immutable segments across restart. These are implementation/evaluation repairs; neither the target nor the fixed series is changed. Actual OTel recording guards must pass the native-absence audit before its scored absent-mode campaigns.

Native baseline repair reviewed on 2026-10-26: the DSB raw traces already contained complete nginx HTTP boundaries, but the binder ignored their exact parent relationship to the header-bearing Lua span. The independent reviewer rejected the weaker proposed Lua timing substitute. The repaired binder follows unambiguous same-process ancestry and retains the binding path; a supported nginx `opentracing_tag` additionally records the opaque header directly on the actual HTTP span. Orchestrator and reviewer **GO** for qualification and replacement of the six affected partial/full campaigns, after actual capture is checked. [Explicit exclusions](technical-exclusions.json) identify every affected run/mode/seed and exclude all paired sources consistently; every original metric and cost remains retained. The three absent-mode campaigns do not have this native binding defect. No exclusion depends on measured forecast error, and no empirical-success claim follows from this repair.

## Design

27 campaigns = 3 systems x 3 actual tracing modes (absent, partial, full) x seeds 0,1,2. The partial mode disables native tracing in both controlled replicas. eBPF is collected in every mode; automatic context propagation is permitted and recorded.

- DeathStarBench: compose_post, read_home_timeline, read_user_timeline; controlled user-timeline replicas.
- OpenTelemetry Demo: browse_product, add_to_cart, checkout; controlled product-catalog replicas.
- Petclinic: list_owners, owner_details_with_visits, create_visit, list_vets; controlled Visits replicas.

Each campaign: four 60-second calibration blocks (11,10,01,00); eight 30-second target blocks with state counts 4,2,1,1; 4 operations/second with balanced mix. Two healthy 30-second blocks support training/testing operation classes. Total 2160 primary attempts per campaign, 58320 overall. States mean availability of replicas A/B, on different guests. State-mixture transfer does not claim prediction of transition dynamics or MTTF/MTTR.

Reset/settling and pending deadlines are completed between blocks. Forecasts are saved before target observations are acquired. Each forecast uses 100000 Monte Carlo draws and is checked against exact conditional-state weighting. Unsupported interpretations are not given fabricated point values.

Preparation repair, independent reviewer GO on 2026-10-26: after each state barrier, execute exactly one unscored warmup per operation in that block, retain its outcome, and wait 10 seconds. Never retry warmups until success. After scored futures/oracles finish, hold the current intervention for a fixed 10-second drain guard before resetting. The guard does not prove completion of arbitrary server background work. These operations and waits count toward preparation costs; the 2160 scored primary attempts are unchanged. Apply `fixed-warmup-v2` consistently. The already running Petclinic run 40333270035 is a superseded protocol pilot regardless of accuracy and is retained and rerun.

## Additional controls, same deployments

Each campaign: 20 operations with selected DB available, then 20 unavailable. This validates observed dependency semantics; adding/removing a redundant node in a saturated estimator is not evidence of prediction improvement.

Each OTel campaign: 20 checkout attempts each in normal, accounting-paused, recovered conditions. Existing chain: checkout -> Kafka -> accounting -> PostgreSQL. Immediate success deadline 2 seconds; correct order/items persisted within 10 seconds is a separate target. Paused accounting stays paused until the last deadline; backlog is drained before recovery control. These controls do not establish a forecast for an uncalibrated consumer-failure regime.

Async links require an observable order identity or a confirmed message-identity chain. Kafka request correlation_id, topic adjacency, timestamps or producer acknowledgements alone are insufficient. Missing evidence stays unknown. SQL census is independent evaluator-only evidence.

Qualification-based matcher review on 2026-10-26: the independent reviewer and orchestrator GO for exact native producer SpanLinks plus accounting processing-root ancestry. The pinned consumer creates one processing activity per consumed message; its receive span links the checkout producer, and the PostgreSQL batch-write span shares that processing root. The observed write is one span with three INSERT statements; CONNECT spans are excluded. Indices remain source-separated and conflicting/empty identities are unknown. Association is distinct from SQL durability and its deadline. This implements the message-chain option already in the design, using qualification evidence before primary async results; it does not infer links from topic/time or use oracle order IDs as inputs.

Database interpretation review on 2026-10-26: Mongo/Redis activity explicitly named by native spans is tallied even when endpoint attributes are absent. The interpretation is marked name-derived, not concrete-instance evidence. Unknown-address DB nodes are scoped to the caller and never counted as shared dependencies. OBI protocol labels remain unchanged, with mismatches against the independent deployment reference reported separately. This prevents parser coverage from being mistaken for absence of native DB information.

## Acquisition and evaluation

OBI first; one bounded DeepFlow fallback if required protocol observations are unavailable. No open-ended collector benchmark or custom universal tracer. Inspect real Thrift/Kafka support. Separate eBPF, native and deployment metadata provenance. Do not inject operation labels or dependency maps into class discovery.

Class baselines: normalized method/route; augmented downstream signature. Evaluate ARI and unknown fraction. Evaluate database logical identities, concrete instances and shared dependencies against deployment evidence; retain native DB spans. Measure confirmed and erroneous cross-node request links, not just graph size.

External HTTP/SQL outcomes, signed/absolute forecast error per operation, conservative interval error max(abs(L-y),abs(U-y)), coverage, unknowns and all repeats remain visible. Practical target: mean absolute error <=5 percentage points per operation across three repeats. Intervals wider than 10 pp are not informative point forecasts. No exclusion by agreement.

## Infrastructure and output

Public GitHub repository, standard Ubuntu runner. Two QEMU/KVM guests with independent kernels and eBPF/BTF; shared physical runner is a limitation. Public visibility was explicitly requested by the user for standard runner limits. Paid compute is not authorized automatically.

Detailed English README follows a research-draft structure: abstract/status, motivation/questions, related capabilities, environment, method, design, complete results, limitations, reproduction and references. Tables/figures derive from retained data with run/artifact links. No unsupported claims or invented results.

## Actual partial-results review

Expanded review on 2026-10-27 for Actions report `40453691448`: orchestrator and independent 6.1 Sol/xhigh reviewer **GO** for reporting 22 valid campaigns as partial evidence, **NO-GO** for claiming the full original criterion established. All 198 saved model/forecast/map hashes match, and the previous 18 campaigns' 54 source-level operation/class/proxy records are unchanged. OTel absent-mode forecasts remain noninformative despite healthy route ARI 1.0. Full seed 2 has 60 native/combined associations to accounting write spans and zero eBPF associations; write spans do not prove successful commits. SQL deadline unknowns and oracle failures remain explicit. Neither class augmentation, DB-driven forecast improvement nor independent instance/cross-node correctness is established. Five technically incomplete acquisitions remain; no unfavorable accuracy result is rerun.

Technical recovery review on 2026-10-27: the orchestrator and independent 6.1 Sol/xhigh reviewer give **GO** for qualifying the isolated Kafka admin helper and completing the first evaluation of OTel full seed 2 from run `40372035878`. The completed acquisition is retained, not repeated: exact counts, final snapshots, parse checks, stable broker identity and pre-target hashes were inspected. Message matching now builds identical source-specific indexes once; independent fixture comparison found no output differences. Recovery requires byte-identical acquisition model/normalization/evaluation code and preserves all existing assignments and prediction artifacts. This is an implementation recovery, not a new empirical repeat or a success verdict. Only the five incomplete partial/full acquisitions require new traffic after qualification.

The corrected helper's actual qualification `40454954706` passed: zero orders lag within 19.55 seconds, unchanged broker identity, verified cleanup and no helper instrumentation. The original 60-second deadline, broker limits and application observation remain unchanged. Orchestrator and application-worker GO to run only partial seeds 0/1/2 and full seeds 0/1, following the independent reviewer's source GO. This does not change any scientific outcome criterion.

For Actions report `40362124923`, the orchestrator and independent 6.1 Sol/xhigh reviewer approve reporting the 18 completed campaigns as valid partial evidence. The reviewer explicitly gives **NO-GO for claiming the full original combined criterion established**. Original class/proxy assignments and all model/forecast/map hashes were preserved. DSB meets the stated entry-event forecast target with equal native/direct baselines; this does not establish internal Thrift recovery, eBPF necessity, or efficiency superiority. Petclinic retains semantic errors and unknown forecasts and does not meet the conservative target. DB protocol disagreements, missing independent cross-node references, all six implementation exclusions, the pilot, failed OTel attempts, and incomplete cost information remain visible. The original 27-campaign scope and external criterion are unchanged; nine OTel campaigns remain to be completed.
