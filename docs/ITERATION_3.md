# Iteration 3: fresh source-only experiments

Status: source contracts and baselines reviewed; implementation in progress.
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

## Source-only completion contracts

The primary arm receives explicit operation declarations and an outcome-free
request journal: opaque step IDs, operation identity, start/end timing and deadline.
The scheduler fixes the operation and complete intended step sequence before the
first request. Automatic grouping receives no supplied operation label or intended
sequence length. Every dispatched operation stays in the denominator.

Entry binding requires the declared entry service/method/path and opaque request
identity. Conflicting observations remain unknown; parent relations are strictly
source-local. Combined evidence unites independent facts for the same request,
not a synthetic cross-source trace. Deadline timing comes from the same permitted
request journal for every source, as in the original operation model.

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
| Petclinic create visit | HTTP/deadline failure can establish false. HTTP 201, INSERT text and commit-shaped spans do not alone establish exactly-once persistence; unsupported persistence remains unknown. |

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
