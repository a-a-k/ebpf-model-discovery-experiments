# Iteration 5 review and execution boundary

Status: implementation and smoke qualification. No main-series approval or
positive empirical contribution is claimed. The independent reviewer is the
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
