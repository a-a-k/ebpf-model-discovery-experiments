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

The repaired retained replay `40674465933` completed with all three source
integrity checks passing. Actual Sheaft forecasts now exist for all four Petclinic
operations using eBPF alone; supplied network-scope mapping enables shared-DB
fault forecasts where the DB obligation is unconditional. DSB and OTel eBPF-only
graphs still lack required service paths. This is technical evidence, not fresh
accuracy measurement. Bering-only resource evidence is retained.

The first three already-planned full/seed6 cells are launched in run `40704758284`
at `fdec1a6`, after independent original-criterion GO and CI `40704617133`.
OTel and Petclinic lost their runners during discovery after training acquisition,
without artifact upload; the cause is not established. DSB's acquisition step also
failed and its uploads were skipped; final platform status and logs are pending.
The checkpoint/streaming/swap repair passed independent review and Linux CI
`40718306225` (413 tests). Unchanged OTel and Petclinic full/seed6 cells were
relaunched at `ea2e278` in `40718665137` and `40718674400`, respectively.
DSB/full/seed6 was retried at `3e70887` in `40731158179`, after review accepted the
explicitly failed acquisition step, skipped uploads and empty artifact inventory
as technical failure evidence while GitHub finalizes the outer original job.
Petclinic/full/6 `40718674400` is complete and independently admitted: all 34,800
primary operations and frozen graph/forecast integrity checks pass. Its remaining
eight cells are running in `40733841068`, `40733846961`, `40733852492` and
`40733858113`. Permanent archiving of the first Petclinic cell is in `40734810232`.
Next: assess these cells and the OTel/DSB staged retries; retain the original attempt's available
logs/costs. Each system's remaining eight cells may proceed after its own staged
integrity/resource review, independently of the other systems. Retain every
valid cell regardless of accuracy or unknown coverage.
Resource adequacy must be measured, not inferred from the small replay. Report,
archive and review the actual results without weakening the original objective.
