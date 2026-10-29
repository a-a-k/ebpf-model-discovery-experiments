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

Technical controls establish actual selected-agent acquisition and preserved
bytes on both guests. They do not prove application protocol coverage, causal
completeness, business semantics, or forecast accuracy. A technically valid
all-unknown report does not demonstrate the graph-to-simulation contribution.
Real smoke artifacts and the supported HTTP graph-to-Sheaft path require review
before the corresponding main campaigns. No accuracy threshold is used.

Published product releases and compatibility changes are documented separately
in [TOOLCHAIN_RELEASES.md](TOOLCHAIN_RELEASES.md). Product CI cannot substitute
for empirical qualification.
