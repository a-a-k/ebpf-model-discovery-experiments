# Iteration 3: fresh source-only experiments

Status: all 27 fresh campaigns completed without technical replacement in
[40502990432](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40502990432)
at commit `19eed302e4f7d1f56d64ba25a8b84c062349b922`, after explicit execution GO.
The [primary results](../results/iteration-3/SOURCE.md) retain 939,600 primary
attempts. [Structural reporting](../results/iteration-3/structural/SOURCE.md) and
the [refreshed cost snapshot](../results/iteration-3/cost-refresh/SOURCE.md) are
complete on unchanged captures. Independent review and the orchestrator agree
on the scoped applicability conclusion; execution completion does not imply
universal scientific success.
This is a new acquisition series. Original campaigns and oracle-assisted
retrospective diagnostics remain separate immutable populations.

## Objective and decisions made with the user

Test whether eBPF observations without complete native instrumentation support
operation-model discovery and independent business-outcome prediction, and what
they add relative to simpler observation methods at comparable complete effort.
Negative and unknown results remain outcomes. Equivalent conditional weighting,
larger graphs, SDK independence or provenance alone do not establish an advantage.

Comparators apply to the result they can actually produce. The cheap HTTP/body
arm estimates scalar operation-outcome rates from generator-visible responses;
it is not a recovered internal dependency, placement, database or distributed
execution model. Matching that arm's forecast is not a failure criterion for
the whole study. The central question remains empirical applicability of model
discovery and simulation without complete tracing. Structural findings and any
externally validated use of those findings need their own comparable baselines;
larger graphs alone still do not establish practical usefulness.
Independent review reaffirmed this scope after the user's clarification:
applicability and comparative advantage are separate conclusions. The HTTP arm
is scoped to outcome prediction; native graphs, obtainable inventory, route
grouping and exact native message links provide simple comparisons for their
respective outputs. Cheap combinations receive the same permitted information.
Evaluation-only deployment truth is not silently made a discovery input. The
current state-conditional forecast does not consume the recovered graph and
therefore cannot validate graph-based simulation. Unknown manual effort prevents
a cost-saving claim, without turning scalar HTTP superiority into a study-wide
success gate.

The user explicitly removed binary success gates based on 5 pp error and 10 pp
interval width: neither threshold has an application-loss or power justification.
They remain historical references only. Report operation-wise point errors,
identification bounds, nominal sampling uncertainty, unknown fractions and costs.

After the user rejected 60 seconds and 4 operations/s as too small, the planned
load is 20 operations/s, with four 300-second training blocks and eight 60-second
test blocks. Two 30-second healthy blocks support automatic grouping. This is
34,800 primary attempts/campaign and 939,600 over 27 campaigns, before controls
and preparation. A bounded resource qualification precedes live acquisition.
Requested/achieved rates, generator delays, memory and observation loss are retained;
no silent load reduction or automatic paid infrastructure is authorized.

The 27 campaigns use all ten operations, all three tracing modes, new seeds 3/4/5,
and the same two independent guest kernels. Target state weights remain
0.5/0.25/0.125/0.125. Training measures conditional outcomes in already observed
replica states; their reweighting does not predict an unseen failure from topology.
All predictions and mappings are saved before test traffic. No outcome-based
campaign exclusion, extension or retry is permitted.

## Timing amendment: no imposed application deadline

The first technical qualification used the old universal two-second predicate.
The user challenged its basis: the agreed plan named two seconds only for the
HTTP component of the asynchronous control, and no application SLO justified
extending it to every primary operation. Those 3,600 technical attempts remain
historical evidence and are not eligible fresh-series observations. Their
timeout outcomes must not be described collectively as application failures.

The fresh series separates correct completion, confirmed incorrect completion
and censored/unknown observation. There is no imposed business deadline.
A ten-second **total attempt observation cap** covers every HTTP step and body
transfer. It is an engineering bound: at 20 attempts/s it permits approximately
200 simultaneously waiting operations within the 256-worker budget. It is not
an SLA or a success gate. Actual concurrency, scheduling delays and resource use
must be requalified because the previous two-second preflight is insufficient.

All methods receive the same outcome-free transport journal, including censoring
and the fixed observation cutoff. Timeouts and incomplete responses remain
unknown. Later telemetry cannot promote them. Both span start and end must lie
inside the sealed attempt window, including downstream classification evidence.
This comparison assumes comparable guest/host UTC timestamps; it does not claim
an independently bounded per-span clock error. Rejected timing evidence remains
unknown. The HTTP client enforces a whole-transfer cap using
[`aiohttp.ClientTimeout`](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientTimeout),
plus an absolute asynchronous timeout; a socket inactivity timeout alone is
insufficient. Responses received outside the observation window are retained
but cannot fill the earlier window.

Correctness forecasts retain censored outcomes as identification uncertainty.
Client-observed HTTP response curves show cumulative observed-response fractions,
with every censored attempt retained in the denominator. They are neither an
uncensored completion-time distribution nor a Kaplan–Meier estimate. They cover
the entire 0–10 second window and
include incorrect HTTP responses; they are explicitly separate from business
success and SQL commit latency. No favourable horizon is selected. Exact
conditional weighting remains equivalent to the Monte Carlo calculation.

Primary OTel checkouts no longer perform unrelated per-request SQL polling.
The existing 60 async controls still observe accounting independently, for a
ten-second engineering window beginning at HTTP termination. Expiry without a
confirmed result is unknown. The first positive SQL query supplies an upper
bound, and a prior incomplete query may supply a lower bound; neither is an
exact commit timestamp. The consumer remains paused through all windows and the
queue drains before recovery. Petclinic retains its independent SQL postcondition
verification while the intervention is held; no matching row or an unavailable
query is not automatically a terminal violation. HTTP-and-SQL operation
completion and database commit-time bounds are named separately.

The independent skeptic and orchestrator both granted GO for this revised test
of the **original usefulness criterion**, with the same direct and HTTP/body
baselines and complete costs. This is not an empirical success claim.
Implementation and the revised technical qualifications require review before
the fixed 27 campaigns. Old/new accuracy comparisons cannot isolate an eBPF
effect: load, observation rules and collection configuration changed; use paired
comparisons within the new population.

The revised implementation received explicit skeptic GO for the three bounded
technical qualifications after total-transfer cancellation, common censoring,
sealed entry/descendant evidence, and SQL interval/unknown handling were checked.
The orchestrator agrees; full-series execution remains conditional on their
resource evidence. The first qualification's 11 apparent OTel body mismatches
were all incomplete client responses; the retained audit found 697/697 exact
matches among complete responses. Neither that audit nor qualification is a
business-success result.

## Source-only completion contracts

The primary arm receives explicit operation declarations and an outcome-free
request journal: opaque step IDs, operation identity, start/end timing and the
engineering observation cutoff.
The scheduler fixes the operation and complete intended step sequence before the
first request. Automatic grouping receives no supplied operation label or intended
sequence length. Every dispatched operation stays in the denominator.

Entry binding requires the declared entry service/method/path and opaque request
identity. Conflicting observations remain unknown; parent relations are strictly
source-local. Combined evidence unites independent facts for the same request,
not a synthetic cross-source trace. Observation-window timing comes from the same permitted
request journal for every source. Its cutoff is an observation limit, not a
business-success requirement.

The pinned DeathStarBench nginx OpenTracing exporter omits `span.kind`.
Qualification exposed that format mismatch. Its native binding uses the
outermost matching `component=nginx` HTTP ancestor within the same observed
service, instance and node, reached through exact parent IDs from the request
header. This declared format rule never invents a server kind, crosses sources,
or accepts an explicit client span. The raw kind and ancestry remain in evidence.

The revised qualification's retained-data audit found all 1,200 native entries
by exact request identity before the timing check; 637 were then rejected by the
strict observation-window rule. The
[pinned image recipe](https://github.com/delimitrou/DeathStarBench/blob/6ecb09706140f8730b5385c08f1386c654c3c526/socialNetwork/docker/openresty-thrift/xenial/Dockerfile)
selects nginx-opentracing v0.8.0, whose
[request tracing implementation](https://github.com/opentracing-contrib/nginx-opentracing/blob/v0.8.0/opentracing/src/request_tracing.cpp)
initializes the outer span from seconds/milliseconds and creates the location
child using the tracer's current time. Observed timestamp residues do not alone
establish a guest/host clock offset.

Before implementing the repair, the independent skeptic and orchestrator both
granted GO under the unchanged original usefulness criterion: strengthen the
native interpretation while retaining the same external outcomes, direct and
HTTP/body baselines, semantic knowledge and complete preparation costs. This is
a decoder correction, not evidence of an eBPF advantage.

For this declared nginx format, an outer start preceding the journal can use an
exact, unambiguous in-window request-header child as an attribution witness.
The parent path must remain in the same source, trace, service, instance and node;
timestamps must be positive and ordered, and the outer end must contain the
child end and remain within the cutoff. Outer status, body, raw start and duration
are unchanged. No arbitrary clock tolerance or child-duration substitution is
introduced. Primary and automatic entry binding use the same rule; downstream
windows remain strict, and censored attempts stay unknown. Focused rejection
checks and Actions replay of the retained qualification precede full acquisition;
the resource approval stands without generating replacement traffic.

| Application / operation | Required positive response predicate |
| --- | --- |
| DeathStarBench compose | Original HTTP acceptance predicate and observed acknowledgement containing `Successfully upload post` |
| DeathStarBench home/user timeline | Original HTTP acceptance predicate; JSON list with string post_id/text fields and the pinned stable fixture text |
| OTel browse | HTTP 200 and observed product ID equal to the declared product |
| OTel cart | Required product/cart steps HTTP 200; final body contains the declared product and quantity 1 |
| OTel checkout | Required product/cart/checkout steps HTTP 200; final body contains a nonempty order ID. Async persistence is separate. |
| Petclinic owners/details/vets | HTTP 200 and the exact seed-derived semantic fields, lists and identities specified by the pinned SQL fixture |
| Petclinic create visit | A completed incorrect HTTP response can establish false; a timeout cannot. HTTP 201, INSERT text and commit-shaped spans do not alone establish exactly-once persistence; unsupported persistence remains unknown. |

Source body content must actually be exported. Invalid, explicitly truncated,
conflicting or insufficiently attributable content remains unknown. Accepted
complete JSON relies on the declared single-JSON response format, absence of
truncation evidence and a below-limit capture; reported full-length headers are
checked when available. This assumption is qualified against independent captures,
never filled by copying evaluator response bodies into telemetry. Native body
absence is not silently replaced by HTTP success. The original HTTP-only proxy
is retained as a diagnostic arm, not a substitute business target.

OBI remains pinned. Add the missing DeathStarBench response paths to the body
allowlist and declare a 16 KiB buffer. Preserve body, header and parse provenance.
Processing must be bounded in memory for the larger load; complete raw captures
remain available and observations cannot be silently discarded to fit RAM.

## Baselines and auxiliary experiments

1. Direct state-conditional estimation receives exactly the same facts and
   contracts as its model-based counterpart. Exact integration and Monte Carlo
   are equivalent; computational arithmetic is not the expected gain.
2. A cheap `entry_http` baseline receives transport status, actual response bytes
   and the same journal/contracts. It receives neither evaluator success labels
   nor SQL oracle results. Equality or superiority over eBPF is retained, and
   telemetry-only provenance is not relabelled as practical superiority.
   A completed transport response uses the original adapter's JSON parsing
   semantics, including duplicate-key behavior: known malformed complete JSON
   can establish failure. Telemetry capture uncertainty remains unknown.
   Exception placeholders are not treated as completed empty responses.
3. Automatic method/route grouping is a separate arm from the primary supplied-
   identity comparison. Missing/censored signatures stay visible.
4. Retain 20 DB-up and 20 DB-down operations in each campaign. For Petclinic,
   freeze shared-DB impact predictions from healthy observed paths before the
   intervention. Equally supplied pinned-code necessity declarations concern
   uncached mandatory DB access, not endpoint identity. Endpoint bindings must be
   observed. Missing paths remain unknown; cached vets are not forced to fail.
   Compare with actual datasource/endpoint inventory under identical declarations
   and fault information. If both methods give the same external impact forecast,
   there is no demonstrated graph benefit. No artificial independence assumption.
5. Retain the 60 OTel async reference attempts per campaign. The known OBI identity
   gap is not promised to improve; topic/time/offset coincidences are not message
   associations and a write association is not timely persistence.

## Review and costs

The independent 6.1 Sol/xhigh skeptic approved the concrete source contracts,
cheap HTTP/body and direct baselines, DB prediction boundaries and async reference
controls as a fair test of the original criterion, not a success claim. The
subsequent user-approved removal of arbitrary gates was separately approved.
Orchestrator verdict agrees. The larger load requested afterward requires a
resource qualification; it does not change source semantics or permit selecting
campaigns by accuracy. Implementation and actual data require independent review.
The larger-load amendment also received explicit skeptic GO: interpret semantic
and identity effects through paired arms within fresh campaigns. Changing load
prevents a clean causal comparison with the old series. Qualification checks
generator scheduling, capture integrity, memory and projected disk consumption,
not model accuracy. Retain all 60 OTel async reference attempts per campaign.

Implementation review granted explicit GO for the three full-mode technical
qualifications after source boundaries, fusion, raw conflict handling, DB binding
and streaming repairs passed 48 focused checks. Full acquisition still requires
inspection of their resource evidence. Recovery seals the input index, population,
frozen predictions and source-rule hashes; it must use the acquisition rules and
cannot refit or generate replacement traffic.

Costs include preparation, fixture/contract authoring, requested and achieved
traffic, source capture/storage, unknowns, failed attempts, analysis and all
technical reruns. Unmetered human/agent time remains unknown, not zero. Earlier
acquisition/diagnostic costs remain separately available. No automatic second
series is triggered by disappointing results.

### Final execution review, 2026-10-27

The independent skeptic granted explicit GO for the fixed 27 campaigns against
the unchanged original usefulness criterion after reviewing implementation
`6f91d8f`, all three revised resource captures and retained-data replay
`40502380042`. The orchestrator agrees. The replay accounts for all 1,200 DSB
entries: 563 strict bindings, 631 exact-header-child attributions and six retained
unknowns. Valid pre-cap routes remain observable on censored attempts while
business outcomes remain unknown. No implementation or resource blocker remains;
this verdict authorizes acquisition and does not establish empirical usefulness,
algorithmic advantage or superiority over the direct/HTTP baselines.

### Structural reporting coverage

While acquisition runs, the independent reviewer identified a reporting gap:
the frozen models retain graphs, but the primary evaluator does not summarize
their service, instance or guest-placement evidence. The skeptic and orchestrator
both granted GO for a reporting-only supplement under the unchanged original
criterion. No acquisition, model fitting, classes, forecasts or outcomes change.

The supplement summarizes all 27 frozen graphs and keeps unknown instance/guest
labels explicit. Combined graphs are source-qualified unions, not additional
physical instances. Bounded witnesses from each retained full SQLite index use
unique-identity, conflict and source-local parent filters. The supplement also
rejects malformed or zero trace/span identities before qualifying ancestry;
invalid observations remain counted and witnessed. Frozen graph files and their
original counts are preserved, not retrospectively corrected by this guard.
Full-capture span-link counts are separate from frozen graph-edge counts. These
are **observed exact-ID cross-guest ancestry**; independent link correctness is
not established and its error rate remains unknown. Deployment/container and
distinct kernel boot IDs support evaluation only. Addresses and TCP reachability
do not establish request ancestry; observed placement is distinguished from any
reference-resolved placement. Missing or ambiguous evidence remains unknown.

Processing runs in Actions, one full campaign at a time per system, with input
hashes, bounded witnesses and download/processing/storage costs retained. Larger
graphs do not establish a usefulness advantage or improve the conditional-state
predictor by themselves.

Implementation review granted explicit GO at `2ca7210` after checking the
identity guards, admitted status and acquisition-index seals, matching full and
compact frozen ledgers, unknown placement/instance counts, and sequential
processing. Four focused synthetic checks passed. The orchestrator agrees;
execution approval does not establish an empirical advantage.

Before implementing explanatory reason counts, skeptic and orchestrator also
granted GO for reading the already retained final projection files during this
same supplement. Compact metrics preserve verdicts but omit body/binding reason
distributions. Projection hashes must match admitted metric inputs. Counts keep
source, operation, phase, complete denominators, censoring and bounded witnesses;
absent fields remain "not recorded". Attempt counts and step-reason occurrences
are distinct and may overlap. These are projection-reported reasons, not
independently proven root causes. No projection, model or forecast is regenerated.
Implementation review granted GO at `407d305`; all six focused synthetic checks
passed. The orchestrator agrees with that reporting-only verdict.

### Retained DSB coverage diagnosis

Inspection of all nine completed DSB compact reports found variable coverage,
including near-complete and very sparse automatic route assignment. Before
implementing a diagnostic, the independent skeptic and orchestrator granted
explicit GO under the unchanged original criterion for examining all nine
fixed cells in Actions. Competing explanations are unavailable capture evidence,
identity ambiguity, timing-filter rejection and absent frozen class support.
The same saved sources and exact request identities are examined without adding
semantic knowledge to a predictor. No timestamp correction, model fitting,
replacement traffic or forecast selection is authorized by this diagnostic.

The audit separates pre-window entry availability from saved eligibility and
class assignment, and retains bounded early/middle/late timestamp witnesses with
raw-export checks. Exact-ID timestamps incompatible with the client journal
establish rejection, not independently verified clock drift or collector loss.
All original captures and download/processing costs remain retained.

Technical replacement requires a demonstrated protocol or integration defect,
applied consistently to every affected cell and paired source. Missing evidence,
ambiguous identities, unsupported classes or unestablished timestamp comparability
alone remain unknowns. If a repair changes training inputs or frozen predictions,
retained-data replay is diagnostic and fresh confirmation is required. A pure
reporting error can be corrected without reacquiring unchanged observations.

The independent reviewer granted explicit implementation GO at `a52fbbe` after
all seven focused synthetic checks passed. Replay uses acquisition-hashed rules
and the automatic binder without declared-operation restrictions. Raw witnesses
are limited to the indexed file prefix and retain duplicate timestamp variants;
they cannot substitute a later unindexed value. The orchestrator agrees.

The [completed audit and original outputs](../results/iteration-3-diagnostics/dsb-coverage-40514548883/SOURCE.md)
passed independent result review. All nine eBPF cells retain unique pre-window
entries; observed automatic-route coverage deficits in those cells are timing
rejections. Selected raw timestamp pairs match the indexed values. This identifies
an avoidable admission gate, not collector loss or a fundamental eBPF limitation.
The existing forecasts remain unchanged measurements of that pipeline. No repair
or additional acquisition is approved merely by publishing this diagnosis.

## Structural reporting access-path repair

Run `40521759317` spends extended time inspecting the retained captures. A
synthetic SQLite query plan exposes a possible near-quadratic join: its first
materialized validity CTE lookup uses count/conflict attributes without the
source/trace/span identity key. This is a technical reporting hypothesis, not
evidence that eBPF discovery failed or that the live runner uses that exact plan.

The proposed repair materializes the identical valid-identity relation once per
read-only capture connection in a keyed TEMP table. The strongest direct baseline
is the current query with identical input and predicates. Both must return the
same synthetic outputs, including witnesses and ambiguous/invalid identities;
retained data, models, forecasts, and information boundaries remain unchanged.
File-backed temporary storage and bounded caches limit resource use. Original
and repaired job costs, preparation and cancellation are retained together.

Before implementation, the independent skeptic grants **GO under the unchanged
original criterion** for this reporting-only repair; the orchestrator agrees.
The original contribution remains empirical model discovery and validated uses
without complete tracing. An equivalent SQL access path cannot improve that
scientific contribution; it only completes the already required report. No
additional acquisition or model refitting is authorized by this repair.

Implementation `0ec2b94` passed seven focused checks. Independent review also
compared complete old/new synthetic dictionaries for all three sources,
including witnesses and null/source-identity cases: outputs agree exactly.
The test database hash stays unchanged, and query plans use the full identity
key. The reviewer grants explicit implementation **GO** for the same 27-cell
supplement; the orchestrator agrees. This is not a new empirical-success claim.

## Structural artifact delivery retry

The repaired report completed DSB and Petclinic and seven OTel cells in
`40527106796`. GitHub then returned HTTP 502 while fetching the next original
artifact. This is a transport failure, not a measurement or model failure.
The seven partial cell outputs and all job costs remain retained.

Before implementation, the independent reviewer gives explicit **GO** under the
unchanged original scope for a bounded delivery repair; the orchestrator agrees.
The direct baseline is the current artifact download with exactly the same
identities and evidence. Up to three transport/API attempts use 2/5-second
backoffs and clean, guarded download staging. Semantic admission, hash, schema
and population failures remain hard failures. An optional system selector keeps
`all` as default and permits rerunning only OTel's fixed nine cells. Reprocessing
costs are charged together with the failed attempt. No acquisition, refitting,
scientific-rule change or stronger usefulness claim follows from this repair.

Implementation `9f138a3` passed twelve focused checks and independent review.
The reviewer grants explicit implementation **GO** for the OTel-only nine-cell
reporting rerun. The orchestrator agrees; all earlier reporting costs remain
included.

## Report output isolation after publishing results

Published primary results now exist in fresh repository checkouts. Before a
report refresh, the fixed generated output tree must be cleared in the ephemeral
Actions workspace; otherwise `mkdir` fails or old files contaminate a new report.
The reviewer and orchestrator give **GO** before implementation for this scoped
preparation repair: require matching resolved workspace/cwd and the exact
`workspace/results/iteration-3` target, refusing redirected paths. Published
Git files/releases and downloaded inputs are untouched. The direct baseline is
the same report with an empty output directory; no information or calculation
changes. The original primary files remain preserved locally/in Git, and only
refreshed costs/provenance are published as a separate supplement. Reporting
costs remain disclosed.

## Reproduction of the fresh series

All application acquisition, fitting, simulation and retained-data reporting run
in GitHub Actions. Local checks only validate implementation. Each campaign uses
its own standard `ubuntu-24.04` runner and two guests. The workflow permits up to
18 simultaneous campaigns, within the documented
[standard-runner concurrency limits](https://docs.github.com/en/actions/reference/limits#job-concurrency-limits-for-github-hosted-runners);
actual scheduling also depends on other account jobs. Campaigns share no
application state. The fixed population remains 27, with no paid runner selection.

```sh
# Three technical jobs; inspect their resource evidence before acquisition.
gh workflow run qualification-v3.yml -f system=all
# Replace QUALIFICATION_RUN with the completed numeric run ID.
gh workflow run evidence-v3.yml -f run_id=QUALIFICATION_RUN
# Reviewed fixed population: three systems x three modes x seeds 3/4/5.
gh workflow run series-v3.yml -f system=all -f mode=all -f seed=all
# Replace SERIES_RUN with the completed numeric run ID (JSON numeric array).
gh workflow run report-v3.yml -f run_ids='[SERIES_RUN]'
# Read-only graph and ancestry supplement from that completed primary report.
gh workflow run structural-v3.yml -f report_run_id=REPORT_RUN
```

The resource evidence copy retains precomputed qualification, deployment,
scheduling, memory and disk records, plus an OTel captured-body fidelity audit.
It does not fit predictions. Full campaign artifacts retain raw sources,
independent operation outcomes, frozen models, forecasts, automatic classes,
controls and resource records. Compact `v3-summary-*` artifacts carry evaluated
metrics and their supporting frozen files into the report; they do not replace
the full captures. Technical failures retain available data and costs. A completed
capture can resume analysis only if its input and frozen-rule hashes still match.

The report accepts exactly the 27 distinct campaign cells, preserves unknown
values, and produces operation-level tables. Its data remain separate from
`results/final/` and the oracle-assisted `results/iteration-2/`. The archive
workflow retains original artifact ZIPs, hashes and provenance in a public
release; the run history identifies superseded and incomplete preparations.
