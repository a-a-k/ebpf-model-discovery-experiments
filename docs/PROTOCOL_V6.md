# Protocol: operation models from eBPF observations

## Research question

Can eBPF observations support executable operation models and prospective
forecasts of application outcomes when SDK tracing is absent or incomplete?
A supported graph alone does not answer this question: forecasts are checked
against independently measured application outcomes.

## Experimental matrix

The study contains 108 cases in 27 logical blocks:

- Applications: Petclinic, OpenTelemetry Demo and DeathStarBench Social Network.
- SDK coverage: absent, partial and full.
- Runtime treatments: no eBPF agent, OBI, Coroot and DeepFlow.
- Repetition identifiers: 9, 10 and 11.

Each block fixes application, SDK mode and repetition and contains all four
runtime treatments. All ten operations are retained: Petclinic list owners,
list vets, owner details with visits and create visit; OTel browse product,
add to cart and checkout; Social Network compose post, read home timeline and
read user timeline. Source/view analyses share the same external attempts and
are not additional independent repetitions.

The no-agent treatment runs without a study eBPF collector. Together with
absent SDK tracing it supplies the tracing-disabled control; with partial or
full tracing it supplies clean SDK comparisons. SDK libraries can remain
installed when their providers, samplers or exporters are disabled. Actual
application span coverage is checked from retained observations. OBI uses its
configured active context propagation; its treatment is not purely passive.

## Allocation and deployment

[Allocation](PROTOCOL_V6_ISOLATED_ARMS.md) distinguishes eight physically paired
cases from 100 cases on randomized separate hosts. Application fixtures,
logical service identities, replicas, operation semantics, workload intentions
and intervention laws are the same across the four treatments.

Capture and validation use separate fresh application deployments with two
actual guest kernels. The pinned source, images, SDK configuration, routing,
resource settings and initial fixtures form a sealed deployment blueprint.
Checkout's unintended 20 MiB container limit is corrected uniformly in this
blueprint before measurement. Each deployment records fresh boot and process
identities; those identities locate observations without adding missing graph
relations.

## Prospective lifecycle

1. Prepare and seal the application and guest blueprint.
2. Capture observations in each runtime treatment. Close and hash each input;
   stop the application, collector and guests before offline model processing.
3. Construct Bering graphs, bind the declared operations and execute Sheaft
   calculations wherever the observations support them. Freeze all four models
   and forecasts before any validation target in the block.
4. Start fresh validation deployments from the same blueprint. Apply the target
   interventions and measure responses, content, SQL postconditions and order
   persistence independently of the observation-to-model pipeline.

Processing can reuse an exact published closed input after a technical worker
failure. Original capture identities and hashes remain unchanged; new model
processing and target origins are recorded separately. The final result
manifest identifies the actual producing source, job and attempt for each case.
No input is chosen using forecast accuracy or observed application outcomes.

## Workload and outcome controls

Each case retains 600 family-preparation attempts, four discovery blocks of
6000 attempts, eight primary target blocks of 1200 attempts and 600 family-test
attempts. The nominal primary rate is 20 attempts/s. The replica states
11/10/01/00 have target-block multiplicities 4/2/1/1. The fixed routing policy
continues to apply when replicas are stopped or started.

Database-up and database-down controls retain independent application
postconditions. OTel additionally retains normal, consumer-paused,
resumed and recovered persistence observations. Acknowledgement and durable
storage are distinct outcomes. Payload, SQL and order checks preserve unknown
results; there is no arbitrary operation deadline or accuracy cutoff.

## Observation sources and baselines

Each case evaluates native SDK input, eBPF input, their combination and a cheap
union of observed context edges. Each source has raw and network_scope views.
All methods receive the same declared operation contracts, logical aliases,
placements and other permitted semantic knowledge. Observation sources keep
their original identifiers and ambiguous ancestry; topology is not invented.

The direct conditional reference uses the declared source contract and the
controlled two-replica inventory. Its 7/8 or 1 forecast assumes that other
required services work. It uses neither validation outcomes nor a recovered
graph. Prediction equivalence with this calculation is reported explicitly.
The feasibility question does not require a new predictor or an advantage over
an equivalent direct calculation.

The model and family definitions remain frozen during evaluation. Classification
agreement is descriptive and does not substitute for an external outcome.

## Resources, failures and evidence

Application traffic, VMs, model construction, simulation and artifact processing
run in GitHub Actions. Standard Ubuntu 24.04 workers use their available four
CPU cores, approximately 16 GB RAM and a 360-minute job limit. Actual resources
and per-phase costs are recorded. Memory-heavy OTel processing uses the recorded
child-only GOGC=25 and additional owned 16 GiB model swap profile; per-block
provenance distinguishes these runs from the other processing profiles.

Missing or corrupted input, wrong treatment, failed fixture/intervention setup,
incomplete workload, transfer failure and platform interruption are technical
failures. Their original prefixes and costs remain recorded. Completed adverse,
unsupported, unavailable, unknown and application-failure outcomes remain in the
scientific comparison; they are not repeated to obtain a positive result.

Publications bind original inputs, forecasts, target captures and evaluations
with hashes and actual source/job/attempt identities. Disk reserves apply to
restoration, model archives and publication. Verified temporary deliveries can
be released after their immutable publication is confirmed. Whole scientific
archives and raw journals are processed in Actions.

## Costs and interpretation

The cost inventory includes preparation, image builds, controls and diagnostics,
capture, baseline/model/simulation work, both deployment phases, transfers,
failed and repeated attempts, early stops, GC/swap setup, CI, review, reader and
publication work. Reused engineering components and prior preparation are
explicit. Human and unmetered work remain unknown; worker elapsed intervals are
not CPU time, billing or sequential campaign time. Copied GitHub job aliases
referencing the same actual execution are retained without charging that
execution twice.

Protocol and collector findings apply to the pinned versions, configurations
and conversion pipeline. Missing operation evidence and runtime application
failures are separate observations. A service or transport edge does not by
itself establish an operation-level call path, database dependency or
asynchronous causal relationship.
