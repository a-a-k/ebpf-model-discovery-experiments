# Experiment collaboration

This repository contains experiments and their research README. Compute, real application traffic, VM launches, model fitting, simulations and results processing run in GitHub Actions. Local work is editing, static checks and focused unit checks only.

The current objective and completion criteria are in docs/GOALS.md; the active design is docs/PROTOCOL_V4.md. docs/PROTOCOL.md is historical. Preserve all ten operations, real absent/partial tracing, two independent guest kernels and independent external outcomes. Do not replace failed evidence acquisition by invented data, native labels or an expected topology. Unsupported results remain explicit.

Three workers own systems/deathstarbench, systems/otel_demo and systems/petclinic respectively. The orchestrator owns common code, workflows and README. Work in the assigned git worktree/branch. Do not edit another worker's files. Commit your work and report the SHA; do not merge or dispatch campaigns yourself.

The reviewer checks implementation and actual results. Current review decisions are recorded in docs/PROTOCOL_V4.md. A hypothesis change requires renewed skeptic review. There is no requirement to outperform an equivalent direct calculation.
