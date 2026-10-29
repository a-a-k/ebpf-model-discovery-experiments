# Iteration 5 review and execution boundary

Status: matching main cells have been admitted as documented below; the complete
108-cell study and any contribution verdict remain pending. The independent reviewer is the
separate 6.1 Sol/xhigh agent requested by the user, not an external peer reviewer.

## Original criterion and strongest baseline

The intended result is the complete Procrustes preparation, Bering graph
discovery from actual eBPF observations, Sheaft simulation, and independent
application-outcome comparison. Any claim of better usefulness or less effort
requires comparison with the equally informed direct contract/inventory method
and native or combined tracing. Equivalent primary availability arithmetic is
acknowledged; executing the simulator does not establish superiority over it.

Family classification is now exactly equivalent to the frozen entry-only
method/route/step baseline. Downstream evidence describes structural variation
without splitting a known entry family. An ARI advantage over that baseline is
therefore not claimed. Manual semantics, runtime inventory and request-boundary
information are disclosed and available to every source and baseline.

Preparation, source adapters, failed smokes, instrumentation, waiting, retained
data and computation are included in cost accounting. Unknown human effort is
not zero. Early termination is a retained technical failure, not a successful
cheap run. Both the orchestrator and skeptic approved this original criterion
before implementation; [PROTOCOL_V5.md](PROTOCOL_V5.md) records the design.

## Reviewed implementation

The reviewer checked the generic vendor-neutral product interface,
implemented source-specific decoding, entry selection without invented trace identifiers,
runtime identity evidence, class fitting, checkpoint closure, worker input
equivalence and prediction freezing. Conflicting identity remains unknown;
causal links still require observed identifiers. Runtime projection does not
insert dependencies or operation outcomes into the observation source.

The integrated source at `986dea703798315b0f33f5d0771ec3725fae76e2` passed
[full Linux and real Docker fixture checks](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40885659304).
Its failed technical attempts remain in [ITERATION5_PROGRESS.md](ITERATION5_PROGRESS.md).

Subsequent review approved these bounded repairs for one fixed repeat per agent:

- OBI `7d7e6318d5735d299bb675912fbb4a62f8cdd471` through
  `d87b38511e63fb3040d35c106fe1823444139eaa`: start the persistent control
  responder before agent startup so it is present for initial discovery. Emit no prestart proof
  traffic; retain the same fresh marker and raw eBPF-origin check after
  application readiness. Record the added preparation cost. This control does
  not prove admission of processes created after agent startup. Independent
  verification: 63 relevant tests passed, two environment-specific skips.
  This tests an unproven dynamic-process-admission hypothesis: no PID-map
  snapshot was retained. HAProxy-specific discovery, probe, namespace or
  transport behavior remain alternative explanations for the prior miss.
- DeepFlow `97b60f012235aada3a0255849cdbd1df85a093bc` through
  `34773b525f6dad0d419f956b512f0fa2fd35502e` and
  `898636f4d18ff736b86f2d1a64faeeb00eb704d2`: privileged read-only process
  inventory consistently for all arms, original failure preservation, and
  retention of available raw bytes and logs before failed-start cleanup.
  Incomplete captures make no producer-closure or successful-drain claim.
  Independent verification: 81 focused tests passed.

Both orchestrator and reviewer give explicit **GO for the original criterion**
to repeat the fixed OBI DeathStarBench/partial/seed-6 smoke and DeepFlow
Petclinic/absent/seed-6 smoke after the integrated revision passes Linux and
Docker CI. This is an execution decision, not a result or main-series GO.

The reviewer also approved one Coroot Petclinic/absent/seed-6 pilot at the
passing integrated `161eb1d606a444e59ec18d6084bbcd62a256fd86` revision
([CI 40889975595](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40889975595)).
The pinned source exports independent client roots; server entries, request
headers and causal parents are not presumed. Its process cleanup does not prove
SDK exporter shutdown or zero internal loss. These remain explicit uncertainties.
The same source-origin checks, complete graph/simulation path, baseline information
and cost accounting apply. Independent checks: 57 tests passed, two
environment-specific skips. Both agents give GO for this original-criterion
technical pilot only; no main-series or positive-result approval is implied.

## Interpretation of qualification

Follow-up actual evidence rejected the OBI prestart workaround as sufficient:
the host-networked control was excluded by the pinned `containers_only` matcher.
Coroot's Petclinic smoke additionally exposed a control/app host-port collision.
Both agents approved the common private bridge/DNS control correction for the
original criterion; no host port is published and the same raw-origin proof is
required. Implementation `6046aea39a732a7b501c1038819bd621e6c657b7` removes
the provisional OBI prestart path and retains creation/cleanup evidence and
costs. Independent checks: 39 relevant tests passed, two environment-specific
skips. The real Docker CI fixture now occupies the former host port and checks
private-network operation and cleanup. One fixed OBI and Coroot repeat is
approved after that CI passes on the integrated revision. DeepFlow also needs
its separate reviewed startup/resource configuration before a repeat. No
main-series or positive-result verdict is issued by this correction.

The integrated private-network revision `a333cdd697b201c3168e4d8f9e5ede771f6d996a`
passed [Linux and Docker CI 40895444290](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40895444290).
The preceding CI failed because the new Docker regression omitted its `socket`
import; that test-only error was repaired before either pilot was repeated.

DeepFlow startup and resource changes `06cc491` through `d548c984` received
independent actual-code review: 78 relevant tests passed. They disable only the
unrelated on-CPU profiler, use the pinned post-start marker, and derive positive
memory/CPU settings from each guest's actual inventory. Memory is serialized in
the MiB units required by the pinned agent. Docker and cgroup hard limits,
including shared ancestor limits, are retained and checked. The resource claim
is the common guest-wide envelope, not unlimited resources or zero data loss.
Both orchestrator and skeptic give **GO for the original criterion** for one
fixed DeepFlow Petclinic/absent/seed-6 repeat after the integrated Linux and
private-network Docker checks pass. The raw selected-agent origin requirement,
baselines, unknown handling and complete cost accounting are unchanged.

Actual OBI repeat `40895622472` passed raw acquisition controls on both guests,
then GitHub rejected worker dispatch with HTTP 422. The packaged handoff retains
the exact response: the extra `collector_provenance` workflow input is undeclared.
Both agents give original-criterion design GO to omit only that redundant API
input. Collector provenance remains in the parent expectation, hash-bound
checkpoint, worker-derived output and import comparison. The regression checks
actual dispatch keys against the workflow declaration and rejects a changed
collector in returned output. This transport correction changes no observations,
models, baselines or scoring. Actual-code review and CI precede a fixed repeat.

The DeepFlow resource-verifier correction similarly retains the same resource
policy. Both agents approve recording explicit traversal to the cgroup root
without demanding root-only limit files that the Linux interface does not expose.
Missing non-root evidence and real extra limits must still fail verification.
This is a preparation repair, not collector capability or main-series approval.

Independent actual-code review approved dispatch repair `8e427b4` (30 relevant
tests passed, one POSIX-specific skip) and DeepFlow `9ac7258` through `3ee27ec`
(47 relevant tests passed). Both agents give **GO for the original criterion**
for the same fixed OBI and DeepFlow smoke repeats after the integrated Linux and
private-network Docker CI passes. The Coroot attempt remains separate; no
main-series or positive-result approval is inferred from these repairs.

The integrated `e24c9289afa5595ee17e6d33c697fc245bfde6ac` passed
[Linux and Docker CI 40898462595](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40898462595).
Both agents also give original-criterion GO for the next predeclared OBI
Petclinic/absent/seed-6 smoke at that revision. It exercises the local toolchain
independently of the DeathStarBench remote worker; it adds no new experimental
cell or favorable-result condition. Unavailable forecasts are not technical
failures and cannot be required to become available for qualification.

Technical controls establish actual selected-agent acquisition and preserved
bytes on both guests. They do not prove application protocol coverage, causal
completeness, business semantics, or forecast accuracy. A technically valid
all-unknown report does not demonstrate the graph-to-simulation contribution.
Real smoke artifacts and the supported HTTP graph-to-Sheaft path require review
before the corresponding main campaigns. No accuracy threshold is used.

Published product releases and compatibility changes are documented separately
in [TOOLCHAIN_RELEASES.md](TOOLCHAIN_RELEASES.md). Product CI cannot substitute
for empirical qualification.

## Saved-artifact reporting boundary

The orchestrator and independent skeptic approved a reporting-only extension
under the unchanged original criterion. It may validate and copy saved v5
evaluation objects, artifact identities, hashes, technical verdicts, unknowns
and costs. It may not reacquire traffic, refit, rescore, relink, introduce a
metric or threshold, or choose an attempt using accuracy or coverage.

Technical smokes remain separate from the 108 declared main cells keyed by
collector, system, mode and seed. A smoke pass is only a self-reported technical
qualification pending independent artifact review. Only a technically complete
main evaluation can occupy main-grid coverage; incomplete, failed, cancelled,
blocked and no-artifact attempts remain in the attempt and cost ledgers. The
four-collector declaration includes the blocked New Relic arm rather than
silently shrinking the grid. Human effort and the reporting job's unfinished
tail remain unknown, not zero. This is implementation GO for the saved-artifact
reporter, not main-series or contribution GO.

Pinned-source validation in this reporter covers the retained collector
manifest. It is not independent admission of the full toolchain or its inputs;
that review remains external and is represented as not performed here.

Actual reporter `31504e06` received independent implementation GO: ten tests,
workflow parsing, ZIP hash verification, saved identity checks, failed-attempt
retention and the complete declared main frame were reviewed. Its integrated
`3332c068b7a960e401932d78e7479ee25d874cbd` passed
[CI 40900996676](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40900996676).
Actions report assembly is approved; generated content still requires review.

## DeepFlow source-schema correction

The repeat `40898777011` passed collector startup but its technical control was
rejected by the research codec. Actual retained rows on both guests contain the
fresh marker. Pinned source serializes base/session and HTTP-phase fields under
the same flattened `msg_type` name. The former decoder treated this known
namespace collision as arbitrary conflicting data and excluded the observation.

Both agents approved the original-criterion correction `4065265` through
`4adfe8a`: preserve both ordered values and their source namespaces, original
bytes and hashes, while retaining the unchanged eBPF-origin proof. Other
conflicting duplicates and producer-supplied reserved parser metadata remain
raw-only. Independent actual-code review passed 56 relevant tests, including a
byte-exact saved-row fixture. One fixed DeepFlow Petclinic/absent/seed-6 repeat
is approved after integrated Linux and Docker CI. No main or contribution GO is
implied, and all failed preparation costs remain attributable.

## Compact journal recovery

The first report assembly `40902931486` exposed a delivery omission: the source
manifest hashes `attempt-journal.jsonl`, but the compact upload did not include
it. The journal remains in the immutable full artifact. Both agents approved
the original-criterion transport repair `b185d8f` through `a4374a8`; independent
review passed 16 tests and parsed the workflow's embedded Python. Future compact
uploads include the journal. Historical recovery checks the received full ZIP's
API size/digest, safe member path and original manifest hash, retains originals
and recovery costs, and changes no saved evaluations. Missing recovery evidence
remains explicitly incomplete while any valid saved evaluation is preserved.
An Actions report-only repeat is approved after integrated CI; no campaign
repeat, refitting or rescoring is needed for this transport defect.

## Supplied logical aliases and derived-source handoff

Both agents approved a minimal supplied logical-service alias policy. Exact
container-name/guest mappings come from retained Compose inventory and are given
equally to all observation arms and the direct baseline. They are supplied
deployment semantics, not discovered process, instance, lifetime or causal
identity. Restarts with the same logical role do not require a clock gate.
Conflicting roles and incompatible model metadata remain explicit uncertainty;
no server roles, headers, peer identities, dependencies or endpoints are created.

Actual implementation `770cbd3` received independent original-criterion GO
(49 relevant tests passed, one platform skip). Parent training freezes the table
and its admission evidence before checkpointing; worker validation is read-only;
later observations use the same frozen scoped map. Raw source records and Bering
outputs are retained. One fixed Coroot Petclinic/absent/seed-6 repeat and remaining
predeclared OBI smokes are approved after integrated CI. Prior qualifying cells
may remain evidence only where unchanged semantics are demonstrated.

DeepFlow handoff `1c8d51f` also received independent original-criterion GO
(88 relevant checks). Derived OTLP is explicitly marked as non-original agent
wire and bound to raw JSONL, accounting, snapshots and the codec through exact
hash and deterministic payload checks. Ordinary OTLP wire checks are unchanged.
The old failed checkpoint is not silently upgraded or called validated.

Before another live DeepFlow repeat, `832b500` adds a bounded software
qualification in Actions using actual pinned Procrustes and Bering binaries.
Its synthetic non-control fixture tests export/ingestion, not application
capability, simulation or scientific usefulness. No VM, workload, Sheaft run or
favorable graph-shape requirement is introduced. Independent review passed 77
selected checks. The arbitrary workflow duration cap was removed, and explicit
test/protobuf dependencies and repository test mode were restored before dispatch.
The actual Actions qualification result must be reviewed before the live repeat.

## Independent saved-packet and progress-snapshot review

The reviewer checked actual retained inputs, hashes, models, command records,
closed training prefixes and external outcome journals for OBI runs `40898769649`
(DeathStarBench/partial/6) and `40899601511` (Petclinic/absent/6), plus Coroot
`40895637294` (Petclinic/absent/6). All three receive technical smoke GO with
their original source bindings. Unknown forecasts remain empirical unknowns.
Petclinic OBI has real graph-to-Sheaft execution for all four operations; its
Procrustes goal-admission report remains BLOCKED. No favorable source quality,
forecast availability, accuracy or cost-advantage claim follows from smoke GO.

Inspection of only the two OBI packets' stored source/guest/service columns and
retained training inventory found no matching supplied container-name alias.
Thus the newly introduced logical aliases are a name-level no-op for these saved
packets. The [inspection record](iteration5-obi-alias-noop-inspection.json) retains
the actual input hashes; neither fitting nor scoring was rerun locally.

Both agents approved [report 40905967491](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40905967491)
for publication as a snapshot of declared work. Independent review checked the
terminal run/head/artifact binding, selected-member CRC and hashes, gzip restored
hash, declared input/retrieval provenance, unchanged source evaluations and the
separation of smoke from the 108-cell main grid. The snapshot contains zero main
cells and retains all 27 New Relic access-blocked cells. Its costs cover declared
runs only; unknown human effort and later work are explicit. This is not final
cost accounting or a positive-contribution verdict. The reporter's transport
eligibility fields are not independent admission or main-series coverage.

For subsequent main dispatch, a matching collector/system/mode smoke is reviewed
against the same existing evidence: pinned acquisition and two-guest provenance;
mode suppression and raw origin/closure; frozen training and worker proof; actual
Procrustes/Bering and Sheaft where supported; all planned workload states and
independent outcomes; equal-information baselines and complete declared costs.
Unsupported application evidence may remain unknown. No accuracy, ARI, latency
or favorable-forecast gate is added. New Relic's access block does not prevent
reviewed execution of the other predeclared collector arms.

Actual review grants ORIGINAL-criterion main-execution GO at `33d98e2` for OBI
Petclinic/absent and DeathStarBench/partial, each fixed seeds 6/7/8. The preceding
packet reviews, demonstrated alias no-op and integrated CI support those matching
cells; the other modes/systems remain pending their own smoke review. Runs
`40910013685` and `40910021896` were dispatched accordingly. This is permission
to execute the comparison, not an empirical-success verdict.

## Actual DeepFlow software handoff qualification

Run `40909257494` remains a FAILED qualification workflow. Its synthetic fixture
has no resolved service identity, so Bering's shutdown publication reports
`discovery produced no services`. No Bering graph, emitted ingest summary or
Sheaft execution is claimed for this run.

The narrower source-to-product handoff is nevertheless established: the posted
and Bering-retained bodies are identical 6,444-byte payloads with SHA-256
`97f6083b87ca65f8d1a27484d60fdb747e5dafb67cc94b855e7e63d84ae7663e`,
containing two decoded observations. Independent inspection of the pinned Bering
handler verifies that HTTP 200 follows decoding, generic normalization and
ingestion. The configured capacity is three and the source code atomically
accepts the complete two-observation batch or returns an error. Zero capacity
drops are therefore source-derived, not a retained measured counter.

Both agents give ORIGINAL-criterion handoff-only engineering GO for one fixed
live DeepFlow Petclinic/absent/6 pilot at `33d98e2`. No replay guard is weakened,
no failed status is rewritten, and no extra favorable fixture is introduced to
make the qualification job green. Actual application acquisition, fair identity
handling and graph/simulation evidence still require that live smoke review.

## Native application-mode check and Jaeger audit observations

Before correction, both agents give ORIGINAL-criterion design GO to reconcile
the new evaluator with DeathStarBench's existing exact-name audit policy. Smoke
`40909279346` completed all 108 operations and passed integrity, capture and
closure checks, but its final evaluator treated one `jaeger-all-in-one` native
span as an application tracing leak. The actual span is the runner's GET
`/api/services` request to Jaeger's query API. The retained native manifest already
reports zero application traces, one audit trace and verified absence, consistently
with the adapter and README policy that preceded this run.

The correction separates native application and audit **span** counts while
preserving the original total/by-service counts and raw records. It excludes only
the explicitly declared exact audit service from the application-mode compliance
check; lookalikes, unknown services and all other application observations still
contradict absent mode. Partial-mode controlled-service checks remain unchanged.
No observation is removed from fitting, graphs or outcome evaluation, and the
same declaration applies to every collector and comparison arm. The direct
baseline receives no less information; forecast arithmetic and complete costs
are unchanged. This repair establishes no empirical advantage.

An Actions-only adjudication of the immutable saved packet is preferred over
repeating traffic. It must retain the original evaluation and source artifact,
verify source hashes and attribute the corrected acquisition check to its new
revision. It may not refit, replay, simulate or recompute empirical metrics.
Actual implementation and adjudication evidence require independent review
before DeathStarBench/absent main admission.

## Shared guest clock domain for observed process identity

Before implementation, both agents give ORIGINAL-criterion design GO for a
minimal correction of the DeepFlow runtime-clock adapter. Actual pilot
`40910393953` captured process IDs, guest identity and before/after inventories,
but the adapter did not supply the documented clock relation expected by the
resolver. Its sparse graph is conditional on that old adapter policy; it is not
an intrinsic collector-capability result.

Independent inspection of pinned DeepFlow `9a1219` shows that its eBPF timestamps
use kernel monotonic time plus a freshly computed guest CLOCK_REALTIME minus
CLOCK_MONOTONIC offset. The standalone configuration disables source NTP
correction. The inventory helper reads these same guest clocks. This establishes
the shared semantic clock domain. Observed endpoint-offset ranges do not prove
hard bounds between samples, and must not be described that way.

The corrected relation must be bound to pinned source, actual configuration,
guest identity and retained hashes. It retains microsecond quantization and the
possibility of unobserved clock steps. A universal hard adjustment bound was an
extra proof requirement, beyond the original empirical criterion and strongest
reasonable baseline. No arbitrary age, tolerance or eligibility threshold is
introduced in its place. Actual reversed/order, boot, namespace, PID, process
start, container ownership and before/after contradictions remain unknown.
No service, PID, dependency or ancestry is guessed. The same relation and facts
are available to every qualifying source and the direct baseline, with all
preparation and validation costs retained.

Actual code review, saved-input validation in Actions and a fresh fixed DeepFlow
qualification precede any DeepFlow main dispatch. Original sparse outputs remain
unchanged; no clock correction by itself establishes useful prediction or a cost
advantage.

Actual implementation of the shared-clock correction (`e8df74d` through
`31962a4`, integrated at `a26740c`) passed independent code review and Linux/Docker
CI `40919785943`. The retained relation binds the audited producer version,
commit, image, actual standalone command/configuration and guest identity.
Runtime intervals account for known microsecond truncation as a deterministic
representation bound; canonical OTLP/raw timestamps are unchanged. Repeated
inventory parsing is cached per immutable dependency, preserving per-row checks.

Saved-training validation `40920240694` then passed independent actual-artifact
review. Its original full ZIP is verified in Actions; the compact ZIP and source
implementation hashes were independently checked. This is new derived
preparation from old immutable training observations: 882 resolutions and 743
unknowns, with the exact retained database record correctly bound. These counts
are preparation diagnostics, not new graph or forecast results. No original
evaluation, graph, class, Sheaft output or external outcome was recomputed.
One fresh fixed DeepFlow Petclinic/absent/6 pilot is approved; DeepFlow main
admission awaits that packet.

All nine OBI system/mode settings now have independent actual-packet admission
for their matching main seeds 6/7/8. Coroot Petclinic/absent and all three
DeathStarBench modes have the same matching-cell main admission. Other Coroot
modes remain pending their smokes. Existing OBI/Coroot admissions extend to
`a26740c` after its passing CI: only DeepFlow emits the new clock declarations;
the existing other-source formats, supplied aliases and resolution semantics
are unchanged. This is a source-specific no-op assessment, not a universal
admission. Running main groups retain their original execution revisions.

## Snapshot memory repair: original-criterion check before implementation

DeathStarBench/full/6 main job `123587179847` in run `40913407822` ended with
runner shutdown/143 before uploading a checkpoint. Its last resource samples
show substantial Python memory growth and near-exhausted swap; the exact
shutdown cause is unproven and the observed OOM counter remained zero. This is
retained as a technical interruption, not a scored model result.

Source inspection found whole-segment bytes, decoded wrapper lists and normalized
span lists held together by supplied-alias verification, plus an all-span list
in runtime-identity projection serialization. The narrow repair processes these
same records incrementally. It retains the same ordinal/digest checks, raw-body
and metadata validation, resolver, sorted projection bytes, immutable training
rows and declared information for every comparator. No observations are sampled
or truncated, and no workload or criterion changes.

Root and the separate skeptic approved this design for the **original criterion**
before implementation. The strongest equally informed direct/manual comparator
still receives the same observations and supplied mappings; the repair itself
establishes no predictive or effort advantage. Complete failed-run, preparation,
validation and repeat costs remain reportable, with unknown human effort explicit.
Required checks are old-code synthetic byte equivalence, malformed/tampered input,
bounded allocation and rollback/publication behavior, followed by an immutable
saved-packet comparison in Actions before affected repeats are admitted.

## Persistent-process technical control

Both agents give ORIGINAL-criterion design GO for a bounded common-fixture
repair after Coroot Petclinic/full smoke `40922905708` failed the selected-eBPF
positive control on one guest. The HTTP responder and private-network traffic
were healthy and Coroot discovered the control containers, but no qualifying
raw marker arrived from that guest. This is a technical acquisition miss, not
application coverage or a collector-capability result.

The old direct baseline keeps a shell alive while starting a fresh `wget`
process for each request. Pinned Coroot source can silently decline an L7 record
when its PID/FD connection association is missing or has a different timestamp.
That makes short-lived socket ownership a supported hypothesis, not the proven
cause of the failed run. The old fixture has also passed other cells, and all
old successes, failures and costs remain unchanged.

The reviewed design inserts a pinned long-lived HAProxy forwarder between the
explicit wget load generator and the existing pinned HAProxy responder. It uses
the same private bridge, fresh marker, 60-second technical-readiness bound and
raw selected-agent proof in every collector arm. Coroot must bind the exact
forwarder-client origin, excluding the load generator. OBI continues to accept
either exact persistent HAProxy endpoint; DeepFlow retains its raw EBPF
marker/locator/source rule and reports observed role/process descriptively.
This does not require identical protocol roles across collectors or assert that
the proxy is the only possible origin.

Both HAProxy configurations and checks, container process evidence, generator
and responder diagnostics, preparation/runtime resource costs, and complete
container/network cleanup are retained. The forwarder's added setup and runtime
cost apply equally to all arms and the direct/manual comparison ledger. No
application, accuracy or positive-forecast gate is added, and no timeout is
extended. A passing repeat would qualify only this technical fixture; it would
not prove the old miss's internal cause or the research contribution.

Implementation `293d2ab` plus readiness/provenance correction `45d6fca` passed
independent actual-code review. Linux/Docker CI and one fixed Coroot
Petclinic/full repeat must pass before matching full-mode main admission.

## DeepFlow destination-address normalization

Inspection of fresh pilot `40920573691` found that the research codec overwrote
the observed destination IP with an HTTP authority (`host:port`) while also
retaining a separate port. Pinned Bering expects the host and port separately.
This known normalization defect superseded the initial matching-main GO; the
pilot remains unchanged as evidence of its original configuration.

Root and the skeptic approved the narrow source-faithful correction before
implementation: preserve observed `ip_dst` and `port_dst` separately for both
HTTP client and server records; retain exact `request_domain` as passive
provenance. Actual code `ae6e1f3`, integrated at `3de01f8`, passed independent
review and Linux/Docker CI `40928823255`. No service identity, ancestry, socket
join or graph edge is inferred. A corrected fixed pilot still precedes main
admission; absent genuine ancestry or named peer evidence can remain unknown.
All sources and the direct baseline retain the same supplied semantic knowledge
and complete preparation costs. This repair establishes no utility advantage.

## First independently reviewed main cells

Actual evidence review admitted OBI Petclinic/absent seeds 6/7/8 from run
`40910013685` and Petclinic/partial seeds 6/7 from run `40914709370`. Each packet
retains 34,800 primary attempts, 9,600 target outcomes, actual Bering and Sheaft
execution, raw collector controls, tracing-mode verification, receiver closure
and unchanged pre-target forecast hashes. Compact ZIP hashes were verified;
selected full-artifact members were verified without claiming a local hash of
each complete large ZIP.

The owner-details result in partial seed 7 is `2099/2400`, against prediction
`0.875`. This mismatch is retained, without exclusion or rerun based on outcome.
The equally informed direct baseline predicts the same value. These five
admissions establish usable packets for comparison, not superiority or a
complete-cost advantage. Unknown human effort and unfinished execution remain
explicit. The [intermediate snapshot](../results/iteration-5/snapshot-40930225342/SOURCE.md)
copies the saved evaluations without recalculation; its transport eligibility
flags remain distinct from this independent actual review.

Coroot Petclinic/partial, OTel/absent, Petclinic/full (`40933885726`) and
OTel/partial (`40933892507`) also passed actual smoke review, bringing
matching Coroot main-setting admission to eight of nine. Their unavailable eBPF
forecasts remain valid negative/unknown evidence, without an availability gate.

The memory-only implementation at `f5ac530` passed actual saved-input validation
`40930267298` after its Linux/Docker CI. Old and new projection JSONL, admission
bytes and full-column database proofs matched exactly, while the source artifact
remained unchanged. This is preprocessing equivalence on retained final-packet
inputs, not a reproduction of the original training result. Both variants used
the same measured peak RSS on that small packet; no full-scale memory bound or
research advantage follows. Failed validation `40929241254` remains retained.

Petclinic/partial seed 8 from `40914709370` subsequently passed actual main
review, bringing reviewed main packets to six. This later review does not change
the immutable five-cell publication snapshot or its declared boundary.

Corrected DeepFlow Petclinic/absent pilot `40930786566` passed actual review:
raw bytes, clock/identity proofs, pre-target freeze and actual Bering imports were
checked. The graph contains observed HTTP and MySQL edges but all primary
forecasts remain unknown; no named peer or ancestry was invented. Matching main
execution is qualified, without a positive scientific contribution claim.

The v5-only OTel native audit correction (`9a8e517`) removes a positive-coverage
gate: missing full-mode native observations remain unknown, while malformed data
and observed suppression contradictions still fail. Historical v4 behavior is
unchanged. Independent code review and CI `40939886539` passed.

The subsequent journal memory repair (`eaa9643`) received original-criterion
design and actual-code GO, followed by CI `40940370220`. Its
[scope and evidence contract](JOURNAL_MEMORY_V5.md) require saved-journal byte
equivalence before affected new starts. It does not establish the shutdown cause
or remove all possible full-campaign memory risks.
## Saved journal hydration validation

The root agent and independent skeptic approved a bounded saved-evidence check
for the journal-memory repair under the original criterion. The strongest
baseline is the exact `f6cb591` bulk `_journal_transports` implementation, not
a graph or accuracy proxy. The candidate must reconstruct the same complete
transport dictionary or `None` for every request from immutable artifact
`12917472672`, using the same retained SQLite journal and semantic knowledge.

The validator verifies the complete artifact against its API digest, extracts
only `attempt-journal.sqlite`, and runs the old bulk implementation and current
one-at-a-time hydration in separate processes. It compares canonical serialized
bytes and hashes for every request. Timing, peak RSS and the reused campaign cost
are retained, but validation success claims only evidence equivalence; it does
not claim a memory improvement, run workloads, refit models, or compute graphs,
forecasts, scores or outcomes. Independent actual-code review and an Actions
result are still required before this check can qualify the repair.

Actual output `40941966903` subsequently passed independent review at exact
`5cfdd7c`, after CI `40941821118`: the 144 saved transports and full canonical
stream matched, source integrity held, and both workers returned zero.
[The validation record](JOURNAL_MEMORY_V5.md) gives exact hashes and limits.
Matching-setting execution resumed; no contribution or shutdown-cause claim follows.

DeepFlow DeathStarBench/absent pilot `40936796228` also passed actual technical
review, bringing DeepFlow setting qualification to two of nine. Its real Bering
graph contains 15 services, 13 Redis-hint edges and three endpoints; all 18 primary
forecasts remain unknown and no Sheaft invocation is claimed. The retained raw
protocol evidence does not justify a universal statement about Thrift or MongoDB.

The referenced report representation passed independent actual-output review in
`40940389382`: 39 exact source payloads restore unchanged, all 538 rendered table
lines match the old representation, and the same five main cells are selected.
The old snapshot is immutable. Per-seed figure code (`3bc6061`, layout correction
`99b5db0`) passed independent review and CI; actual figures still require visual
and companion-data inspection before publication. No new forecasts, uncertainty
estimates, averages or accuracy thresholds are introduced.

All three OBI Petclinic/full main packets from `40924968145` subsequently passed
actual review, bringing independently reviewed main cells to nine. Seed 7 keeps
the owner-details outcome `2099/2400` against forecast `0.875` for all available
sources and both variants; it is not excluded or rerun. Native entry-path
limitations are explained from frozen raw inputs in
[OBSERVATION_LIMITS_V5.md](OBSERVATION_LIMITS_V5.md). The earlier five-cell snapshot
retains its original publication boundary.

Coroot OTel/full smoke `40942437542` passed independent actual review of its
complete compact and worker artifacts, all 950 worker payload files, both raw
CLIENT controls, tracing configuration, source-index/closure proofs and pre-target
freeze. All 18 forecasts remain unknown. Coroot now has nine matching settings
technically qualified, without a positive-forecast or contribution gate.

## DeepFlow ambient-load circuit breaker

DeepFlow OTel/absent smoke `40942447288` retained a technical acquisition
failure: node B captured the exact eBPF HTTP control, while node A did not. The
node-A agent log records `Load15` crossing the default relative threshold `1.0`,
then `Running -> Disabled` with `melted_down=true` before the control; the state
remained disabled throughout all 19 control captures. The closed node-A L7 file
has no pending tail or codec failure, so this is not admitted as application or
protocol-negative evidence. Its execution time and failed result remain costs.

At pinned DeepFlow v7.2.3 commit
`9a1219fa5cf1471ba2ec8742019661567d98002e`,
`agent/src/utils/guard.rs::SystemLoadGuard::check` divides the selected system
load by CPU count and sets `SystemLoadCircuitBreaker` at the configured trigger.
The same function explicitly clears and returns when either trigger or recovery
is zero; `agent/src/config/config.rs::RelativeSysLoad` supplies the default
`1.0/0.9/Load15` values. Root and the independent reviewer gave
original-criterion design GO to serialize exact zero trigger/recovery values for
this one ambient-load breaker in every future DeepFlow arm. The measured guest
memory/CPU envelope, all other guards, source codec, identity policy and exact
two-guest positive control remain unchanged. This is not threshold tuning, an
accuracy gate, or a claim of unlimited resources. Actual-code review, integrated
CI and one fixed OTel/absent repeat are required before admitting that setting.

## DeepFlow aggregate raw-retention cap

Subsequent pinned-source audit found an independent retention boundary: the
v7.2.3 logger guard counts every regular file below `/var/log/deepflow-agent`,
which is also the configured standalone L7 directory, against the default
1000 MiB `global.limits.max_local_log_file_size`. That aggregate guard can act
before the already reviewed 1 TiB standalone-file rotation ceiling. Retained
agent logs from the fixed OTel/absent packet show the typed default value
`1048576000`; the old packets and their costs remain unchanged.

The root agent and independent skeptic recorded explicit original-criterion GO
before implementation in `work/deepflow-aggregate-retention-decision.json`.
The approved change aligns only `max_local_log_file_size` with the existing
`MAX_DATA_FILE_SIZE_MIB`. A source-aware regression must prove the MiB-to-byte
conversion, and the campaign must retain the pinned agent's typed update on both
guests before application workload. No protocol, workload, collector identity,
resource envelope, codec, graph rule, forecast rule or positive-result gate is
changed. Actual-code review and integrated CI remain required.

## Completed DeepFlow setting qualification and shared closure repair

All nine DeepFlow system/mode settings subsequently passed independent actual
review. The matching sources are Petclinic/absent `40930786566`,
DeathStarBench/absent `40936796228`, Petclinic/partial `40943915967`,
Petclinic/full `40943924937`, DeathStarBench/partial `40943318871`,
DeathStarBench/full `40944249737`, OTel/partial and OTel/full `40942447288`,
and the corrected OTel/absent repeat `40948057864`.

Review covered exact compact/worker hashes, both raw eBPF controls, collector
configuration, tracing mode, source clocks, the closed source index through
worker import, pre-target graph/forecast freeze, real Bering executions, and
actual Sheaft executions where frozen evidence admitted a forecast; unavailable
cases did not execute Sheaft. Saved external outcomes and unknown forecasts
remain unchanged. Complete old
logs and unchanged raw prefixes show that the relevant old load/log guards did
not activate in the accepted packets. The failed OTel/absent packet in
`40942447288` remains a separate technical failure.

The receiver normal-close repair and DeepFlow aggregate-retention repair passed
independent code review and [integrated checks `40958092919`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40958092919)
at `8a985f99bfd2ecd4ebe13274e100c86feaae0560`. Future DeepFlow starts must retain
the actual typed retention-config update on both guests before workload. Earlier
packets are not relabelled with the new configuration. The two failed OBI
OTel/absent cells are repeated by [seed 7 run `40958365058`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40958365058)
and [seed 8 run `40959052743`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40959052743);
their earlier closure failures and all preparation costs remain retained.

The separate saved DeepFlow checkpoint-accounting validation
[`40953383041`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40953383041)
passed actual review: all 485 dependency records and nine copied files were
identical. This closes a preparation-equivalence check, not a scientific utility
or full-scale speed/memory claim. The fixed study still contains 108 main cells,
including the 27 access-blocked New Relic cells.

## Intermediate report and actual figure inspection

Report [40964268895](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40964268895)
at `6ecd280207fbf850757c2c67e807054305f058ec` retains 14 technically selected main
cells. Nine OBI Petclinic cells and three Coroot Petclinic/absent cells have
separately passed actual evidence review. The included OBI DeathStarBench/absent
seed 7 and OBI OTel/absent seed 6 remain candidates pending actual main-packet
review; the reporter does not independently admit them.

Independent publication inspection found all 623 selected members, all 68
restored source-evaluation payloads and every figure-manifest file unchanged.
All 324 plotted-value rows match their exact source fields. Six PNGs were
visually inspected; the small adverse Petclinic partial/full seed-7 errors are
below one pixel on the full-range axis and remain explicit in exact companion
tables and the narrative. Unknown forecasts are distinct from zero errors and
from the number of unknown external outcomes. The complete report ZIP was not
hashed locally; the selected-member scope remains explicit.

The [immutable snapshot and byte audit](../results/iteration-5/snapshot-40964268895/SOURCE.md)
retain the conditional OTel primary-forecast assumptions, separate DB-fault and
asynchronous unknowns, native Petclinic route-binding limitation, direct-baseline
equivalence and incomplete human/active-job cost accounting. Faithful publication
does not establish utility or complete-cost superiority, and does not alter the
earlier five-cell snapshot or the fixed campaign design.

## Subsequent OBI OTel main evidence review

OBI OpenTelemetry Demo/absent seed 6 from
[40930805848](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40930805848)
at `f5ac530ec4a13cecd6178fffcdd886628f47af04` passed independent actual-main
review. This brings the reviewed total to 13; the published intermediate
snapshot's 12-at-preparation review boundary remains unchanged.

Review verified the complete compact, 120 selected full-artifact members,
96 frozen file bodies, all 6,088 worker declarations against the parent freeze,
unchanged source-index/import identity, real tracing-mode configuration and
closed capture. Four actual Bering branches processed the retained evidence;
12 actual Sheaft invocations consumed models whose required calls and exact
edge/endpoint IDs occur in the saved graphs. Forecasts precede validation.

All three primary operations retain eBPF and combined forecasts of `0.875`
against `2800/3200` independent outcomes for both variants. Native forecasts
remain unavailable. Missing or ambiguous DB channels are manually assumed
fulfilled in these conditional replica-only forecasts, equally for the direct
baseline; DB-fault forecasts remain unknown. This does not establish asynchronous
checkout completion, a classification gain over the base entry method, or a
utility/complete-cost advantage. The successful cell used the original
30-second receiver-close implementation and does not demonstrate an effect of
the later closure repair. The failed seeds and all costs remain retained.
