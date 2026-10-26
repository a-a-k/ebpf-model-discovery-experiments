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

## Design

27 campaigns = 3 systems x 3 actual tracing modes (absent, partial, full) x seeds 0,1,2. The partial mode disables native tracing in both controlled replicas. eBPF is collected in every mode; automatic context propagation is permitted and recorded.

- DeathStarBench: compose_post, read_home_timeline, read_user_timeline; controlled user-timeline replicas.
- OpenTelemetry Demo: browse_product, add_to_cart, checkout; controlled product-catalog replicas.
- Petclinic: list_owners, owner_details_with_visits, create_visit, list_vets; controlled Visits replicas.

Each campaign: four 60-second calibration blocks (11,10,01,00); eight 30-second target blocks with state counts 4,2,1,1; 4 operations/second with balanced mix. Two healthy 30-second blocks support training/testing operation classes. Total 2160 primary attempts per campaign, 58320 overall. States mean availability of replicas A/B, on different guests. State-mixture transfer does not claim prediction of transition dynamics or MTTF/MTTR.

Reset/settling and pending deadlines are completed between blocks. Forecasts are saved before target observations are acquired. Each forecast uses 100000 Monte Carlo draws and is checked against exact conditional-state weighting. Unsupported interpretations are not given fabricated point values.

## Additional controls, same deployments

Each campaign: 20 operations with selected DB available, then 20 unavailable. This validates observed dependency semantics; adding/removing a redundant node in a saturated estimator is not evidence of prediction improvement.

Each OTel campaign: 20 checkout attempts each in normal, accounting-paused, recovered conditions. Existing chain: checkout -> Kafka -> accounting -> PostgreSQL. Immediate success deadline 2 seconds; correct order/items persisted within 10 seconds is a separate target. Paused accounting stays paused until the last deadline; backlog is drained before recovery control. These controls do not establish a forecast for an uncalibrated consumer-failure regime.

Async links require an observable order identity or a confirmed message-identity chain. Kafka request correlation_id, topic adjacency, timestamps or producer acknowledgements alone are insufficient. Missing evidence stays unknown. SQL census is independent evaluator-only evidence.

## Acquisition and evaluation

OBI first; one bounded DeepFlow fallback if required protocol observations are unavailable. No open-ended collector benchmark or custom universal tracer. Inspect real Thrift/Kafka support. Separate eBPF, native and deployment metadata provenance. Do not inject operation labels or dependency maps into class discovery.

Class baselines: normalized method/route; augmented downstream signature. Evaluate ARI and unknown fraction. Evaluate database logical identities, concrete instances and shared dependencies against deployment evidence; retain native DB spans. Measure confirmed and erroneous cross-node request links, not just graph size.

External HTTP/SQL outcomes, signed/absolute forecast error per operation, conservative interval error max(abs(L-y),abs(U-y)), coverage, unknowns and all repeats remain visible. Practical target: mean absolute error <=5 percentage points per operation across three repeats. Intervals wider than 10 pp are not informative point forecasts. No exclusion by agreement.

## Infrastructure and output

Public GitHub repository, standard Ubuntu runner. Two QEMU/KVM guests with independent kernels and eBPF/BTF; shared physical runner is a limitation. Public visibility was explicitly requested by the user for standard runner limits. Paid compute is not authorized automatically.

Detailed English README follows a research-draft structure: abstract/status, motivation/questions, related capabilities, environment, method, design, complete results, limitations, reproduction and references. Tables/figures derive from retained data with run/artifact links. No unsupported claims or invented results.
