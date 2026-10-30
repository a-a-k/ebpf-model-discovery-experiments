# Experiment collaboration

This repository contains experiments and their research README. Compute, real application traffic, VM launches, model fitting, simulations and results processing run in GitHub Actions. Local work is editing, static checks and focused unit checks only.

The user reiterated on 2026-10-30: reuse the existing collector -> Bering -> Sheaft
path. Do not add generic validation frameworks, schema layers or further retry
machinery. Handle format-only review gaps by direct preserved-file inspection
under the existing criteria. Keep the fixed 81-cell scope, source/model/outcome
integrity and complete costs; do not substitute a smaller demonstration.

Keep heavy artifact validation and raw-journal processing in GitHub Actions too.
Local review should retain compact metadata, necessary selected files and their
hash-bound provenance. Do not download/unpack whole campaign archives or raw
attempt journals locally. Do not restart the old bulk-download watchers. Remove
recoverable temporary copies after preserving verification records and confirming
their original artifact remains available; preserve source, unique local evidence
and active worktrees. The 2026-10-30 disk cleanup is recorded in work/disk-cleanup-verified-copies-summary-20261030.json.

Fetch current Actions job states before reporting live running/completed counts.
Timestamp retained status inventories; do not present an earlier inventory as
the current execution state. Current authorized scope is the three-collector
81-cell study in docs/GOALS.md; New Relic is excluded, not credential-blocked.

The current objective and completion criteria are in docs/GOALS.md; the active design is docs/PROTOCOL_V5.md. Iteration 4 is completed historical evidence. Preserve all ten operations, real absent/partial tracing, two independent guest kernels and independent external outcomes. Do not replace failed evidence acquisition by invented data, native labels or an expected topology. Unsupported results remain explicit.

Three workers own systems/deathstarbench, systems/otel_demo and systems/petclinic respectively. The orchestrator owns common code, workflows and README. Work in the assigned git worktree/branch. Do not edit another worker's files. Commit your work and report the SHA; do not merge or dispatch campaigns yourself.

The reviewer checks implementation and actual results. Current review decisions are recorded in docs/REVIEW_V5.md and docs/PROTOCOL_V5.md; iteration-4 decisions remain historical. A hypothesis change requires renewed skeptic review. There is no requirement to outperform an equivalent direct calculation.
