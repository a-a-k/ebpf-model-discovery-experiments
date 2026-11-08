# Study objective and completion criteria

The active study follows [PROTOCOL_V6.md](PROTOCOL_V6.md) and its
[allocation amendment](PROTOCOL_V6_ISOLATED_ARMS.md).
The study is empirical. Positive results are not assumed.

## Primary objective

Determine whether eBPF observations can replace or complement incomplete
application tracing as input to graph model discovery and useful simulation.

The required executable chain is:

`Procrustes preparation → Bering graph from eBPF observations → Sheaft simulation of that graph → independent application outcomes`

Bering must construct the graph. Sheaft must consume it. Saving a graph beside an
outcome-frequency predictor does not satisfy the objective. Neither an OTLP-only
product change nor a successful CI job establishes the research result.

Native, eBPF and combined arms receive the same declared semantics and inventory.
Use native tracing as a source comparison and retain the strong direct
contract/inventory baseline where applicable. Known mathematical equivalence is
explicit; superiority over equivalent arithmetic is not required or claimed.
Feasibility and usefulness require checks against external outcomes. A separate
cost or effort advantage claim requires comparable complete costs. Missing human
preparation costs are not zero.

## Required empirical scope

- DeathStarBench, OpenTelemetry Demo and Petclinic; all ten agreed operations.
- Absent, partial and full SDK tracing; repetitions 9/10/11; four runtime
  treatments: no eBPF agent, OBI, Coroot and DeepFlow. This defines 108 fresh
  cells in 27 logical blocks. All ten operations are retained. New Relic is
  outside the study scope. The historical 81-cell study remains separate.
- The no-agent treatment is a real runtime control. Training and validation
  use fresh separate deployments; all four forecasts in a logical block must
  be frozen before any validation target. Eight cells retain physical pairing;
  the other 100 use the registered allocation across separate workers.
- Two Linux guests with separate kernels, replicas and calls across guests.
  Each guest pair shares one physical Actions runner; the registered allocation
  places most treatment arms on separate hosts.
- Fresh predictions saved before independent validation traffic. Report each
  operation, source, tracing mode and repeat, including unknown and adverse results.
- Compare errors, uncertainty, coverage and costs. There are no experimental
  response deadlines, arbitrary time cutoffs or accuracy cutoffs. Mandatory
  forecast-before-target ordering remains enforced. Native application behavior
  and external platform limits are documented separately.

## Additional questions

- **Shared database dependencies:** recover DB nodes and callers where supported;
  test a shared-DB corner case and show whether those nodes actually affect the
  simulation and the independently observed result. A larger graph alone is not
  an improvement; native tracing can also expose DB spans.
- **Distributed execution:** distinguish service connections from confirmed causal
  links, preserve source-local identifiers, and assess cross-guest evidence.
- **Asynchronous completion:** separate an HTTP acknowledgement from order
  persistence. Require observed causal identifiers; time proximity or a common
  Kafka topic does not prove association. Unresolved links stay unknown.
- **Operation classes:** compare route-based and downstream-enriched grouping,
  disclosing supplied request/step boundaries and semantic knowledge. Do not claim
  automatic business semantics that were supplied manually.

## Product and repository boundaries

The Bering eBPF source, product releases/charts and related repository
updates are required deliverables. Historical published versions include Bering 1.3.1,
Sheaft 1.3.2, stack 1.5.0 and reproduction 1.3.5; Procrustes and the OTel
integration were updated. Earlier versions remain attributed to their original
experiments. Product verification does not replace empirical work.

No study code, data, results, mentions or links belong in Bering. Further product
work must be necessary generic functionality, not migration of experiment code.
Published release, chart and integration evidence is collected in
[TOOLCHAIN_RELEASES.md](TOOLCHAIN_RELEASES.md).
The public research repository is `a-a-k/ebpf-model-discovery-experiments`, under
the single local `ebpf/ebpf-model-discovery-experiments` directory.

## Completion

The work is complete when the agreed experiments have been executed and assessed,
technical failures have been repaired and retained in the history, and the
repository contains reproducible code, workflows, captures, actual Bering models,
Sheaft forecasts, independent outcomes, costs and generated tables/figures.
The research documentation must explain the design, actual results, limitations,
reproduction and defensible conclusions from retained evidence.

An independent reviewer must check implementation and claims against artifacts.
A negative or unsupported finding is valid; it does not authorize substituting a
weaker objective or expanding experiments to obtain a positive result. A remaining
infrastructure blocker must be reported explicitly, not described as completion.

## Execution

Real application traffic, discovery, simulation and authoritative empirical
calculations run in GitHub Actions. Local work is editing, static checks, focused
unit fixtures and inspection of selected derived outputs and compact metadata.
Preserve original evidence; do not
invent missing edges or infer success from elapsed time.

## Iteration 4 measurement completion and publication

All 27 planned iteration-4 cells have completed and passed independent evidence review:
nine cells each for Petclinic, OpenTelemetry Demo and DeathStarBench. Admission
checks source provenance, actual Bering and Sheaft use where forecasts are
available, forecast-before-validation ordering, independent outcomes, exact
workload/state counts and complete retained evidence. Unknown forecasts and
unfavorable outcomes are retained; they are not implementation failures to rerun.

The final saved-evidence report is
[40853395506](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40853395506).
Publication and retention status is recorded in [SOURCE.md](../results/iteration-4/SOURCE.md).
The report inventory covers 38 series/worker runs and 111 preparation, diagnostic,
CI, reporting and archival runs. Its snapshot is not a self-inclusive final cost:
ongoing archival work and reporting/publication tail metadata are identified
separately. Unmeasured human preparation remains unknown.

The observed eBPF applicability is operation- and system-specific. All four
Petclinic operations have graph-driven forecasts; absent-mode OTel supports browse
and add to cart, while its other eBPF forecasts and all DSB eBPF forecasts remain
unknown. Native/combined availability, DB conditions and primary errors are kept
per operation. Matching the equal-information direct predicate does not establish
superiority, and total effort advantage is not demonstrated.

Original failed acquisition, diagnostic and reporting attempts remain in
[RUN_HISTORY.md](RUN_HISTORY.md). Their replacements address technical failures,
not accuracy. The complete DSB native-envelope equivalence proof retained the same
ordered observations and Bering result while removing the driver's unnecessary
per-trace files; it is an engineering repair, not a completed experimental cell.
No additional experiment is authorized merely to seek a positive finding.
