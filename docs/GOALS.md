# Agreed objective and completion criteria

Recorded at the user's explicit request on 2026-10-28. This document fixes the
purpose of the work; the active iteration is [PROTOCOL_V5.md](PROTOCOL_V5.md),
following the completed [iteration 4](PROTOCOL_V4.md).
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
Any usefulness or cost-advantage claim needs an external outcome and comparable
complete costs. Missing human preparation costs are not zero.

## Required empirical scope

- DeathStarBench, OpenTelemetry Demo and Petclinic; all ten agreed operations.
- Absent, partial and full native tracing; three repetitions. Iteration 4 completed
  27 campaigns. Iteration 5 plans the same 27 cells for each of four collectors,
  after fixed smoke tests and repair of operation-class fragmentation.
- Two Linux guests with separate kernels, replicas and calls across guests;
  the shared physical Actions runner remains an explicit limitation.
- Fresh predictions saved before independent validation traffic. Report each
  operation, source, tracing mode and repeat, including unknown and adverse results.
- Compare errors, uncertainty, coverage and costs. There are no experimental
  response deadlines, timestamp eligibility gates or arbitrary accuracy cutoffs.
  Native application behavior and external platform limits are documented separately.

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

The genuine Bering eBPF source, product releases/charts and related repository
updates are required deliverables. Current published versions are Bering 1.3.0,
Sheaft 1.3.2, stack 1.4.0 and reproduction 1.3.5; Procrustes and the OTel
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
An English research README must explain the design, actual results, limitations,
reproduction and defensible conclusions without relying on this conversation.

An independent reviewer must check implementation and claims against artifacts.
A negative or unsupported finding is valid; it does not authorize substituting a
weaker objective or expanding experiments to obtain a positive result. A remaining
infrastructure blocker must be reported explicitly, not described as completion.

## Working rules

Continue autonomously through implementation, execution, diagnosis, reporting and
review. A completed PR, passing test suite or queued workflow is an intermediate
step. Keep the user informed; do not send Telegram messages.

Real application traffic, discovery, simulation and authoritative empirical
calculations run in GitHub Actions. Local work is editing, static checks, focused
unit fixtures and inspection of saved outputs. Preserve original evidence; do not
invent missing edges or infer success from elapsed time.

## Measurement completion and publication

All 27 planned cells have completed and passed independent evidence review:
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
