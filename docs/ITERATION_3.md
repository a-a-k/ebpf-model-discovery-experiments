# Iteration 3: fresh source-only experiments

Status: source contracts, baselines and amended censoring policy reviewed;
implementation and revised resource qualification in progress. No fresh
27-campaign acquisition has started.
This is a new acquisition series. Original campaigns and oracle-assisted
retrospective diagnostics remain separate immutable populations.

## Objective and decisions made with the user

Test whether eBPF observations without complete native instrumentation support
operation-model discovery and independent business-outcome prediction, and what
they add relative to simpler observation methods at comparable complete effort.
Negative and unknown results remain outcomes. Equivalent conditional weighting,
larger graphs, SDK independence or provenance alone do not establish an advantage.

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
