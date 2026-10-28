# Agreed objective and completion criteria

Recorded at the user's explicit request on 2026-10-28. This document fixes the
purpose of the work; implementation details remain in [PROTOCOL_V4.md](PROTOCOL_V4.md).
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
- Absent, partial and full native tracing; three repetitions: 27 planned campaigns.
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
updates are required deliverables. They have been published: Bering 1.1.1,
Sheaft 1.3.2, stack 1.3.0 and reproduction 1.3.4; Procrustes and the OTel
integration were updated. Product verification does not replace empirical work.

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

## Current next work

All nine Petclinic cells are independently admitted; the generated report is
`40751134324`, published in `results/iteration-4`. Actual eBPF graphs and Sheaft
forecasts are checked against independent target outcomes. Source limitations,
manual-baseline equivalence, DB unknowns and adverse class results remain visible.
The overall completion count is 9/27, not a cross-system success claim.

DSB/full/seed6 `40731158179` continues after its retained training checkpoint.
OTel/full/seed6 parent `40754529169` failed after worker `40764150238` shut down
with severe recorded RAM/swap pressure. No forecast import/freeze or target traffic
occurred. Parent artifacts and available logs are permanently archived by
`40777355932`; OOM causality is not established.

Next is one reviewed diagnostic using the larger, unchanged OTel training
checkpoint and Bering-child-only Go GC tuning, as recorded in PROTOCOL_V4.md.
It cannot complete or resume the failed campaign. After technical qualification,
a fresh staged cell must pass integrity/resource review before that system's
remaining eight cells proceed. DSB is assessed independently when it terminates.
Retain every valid cell regardless of accuracy or unknown coverage, and include
failed acquisition, worker, diagnostic, reporting and archival costs. Resource
adequacy must be measured on the actual input, not inferred from a smaller replay.
