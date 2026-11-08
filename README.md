# eBPF observations for executable operation models

This repository evaluates whether eBPF observations can support operation models
and prospective outcome forecasts when application SDK tracing is absent or
incomplete. Bering builds graphs from retained observations; Sheaft predicts
outcomes that are checked against independent application measurements.

## Current study: v6

The [protocol](docs/PROTOCOL_V6.md) defines 108 cells:

- Applications: Petclinic, OpenTelemetry Demo and DeathStarBench Social Network.
- SDK tracing: absent, partial and full.
- Runtime treatments: no eBPF agent, OBI, Coroot and DeepFlow.
- Repetitions: 9, 10 and 11; all ten application operations are retained.

The no-agent treatment runs without a study eBPF collector. Training and
validation use separate deployments. All four forecasts in a logical block
must be frozen before validation starts. The
[allocation protocol](docs/PROTOCOL_V6_ISOLATED_ARMS.md) distinguishes eight
physically paired cells from 100 cells allocated across separate workers.

Usefulness is judged by externally measured operation outcomes. Comparisons
include native observations, a direct conditional calculation and a cheap union
of observed context edges, with the same semantic information. Missing evidence,
unavailable forecasts, adverse results and unknown values remain in the results.
The study does not assume that graph size or model availability demonstrates
predictive usefulness.

[Reviewed interim findings](docs/FINDINGS_V6.md) cover 80 completed cells; the
remaining 28 OTel cells are required for the complete 108-cell study.

## Code and execution

- [Study lifecycle](src/ebpf_discovery/study_v6.py): fresh capture, offline model
  construction and forecast freeze.
- [Isolated arms](src/ebpf_discovery/isolated_arm_v6.py): capture imports,
  allocation checks and independent validation workers.
- [Registered continuation](src/ebpf_discovery/main_continuation_v6.py): process
  exact published training inputs and run their first isolated validation.
- [Worker resources](src/ebpf_discovery/resources_v6.py): actual CPU, memory,
  disk and swap receipts.
- [Application deployments](systems/): pinned applications and their workloads.
- [Actions workflows](.github/workflows/): scientific execution and implementation
  checks. Application traffic, VMs, model construction and result processing run
  in Actions. Local checks use source or small synthetic fixtures.

Each publication records its actual run, source, producing job, input closures
and file hashes. Portable frozen models retain their archive format. Full
processing files use a streaming upload with a manifest of bytes, SHA256, mode
and modification time. Preparation, transfers, failures, repeated processing and
review costs remain part of the study; unmeasured costs are unknown.

## Historical evidence

The completed 81-cell study used repetitions 6/7/8. Its SDK-only input was a
filtered source projection collected while an eBPF collector was also running;
it was not a separate SDK-only runtime control. Those measurements do not fill
the fresh v6 matrix.

- [Iteration-5 findings and limitations](docs/HISTORICAL_RESULTS_V5.md).
- [Iteration-4 methods, results and reproduction](docs/LEGACY_EXPERIMENT_V4.md).
- [Artifact publication and retention](docs/ARCHIVE_PUBLICATION.md).
