# eBPF observations for executable operation models

This repository evaluates whether eBPF observations can support operation models
and prospective outcome forecasts when application SDK tracing is absent or
incomplete. Bering builds graphs from retained observations; Sheaft predicts
outcomes that are checked against independent application measurements.

## Experiment

The [protocol](docs/PROTOCOL_V6.md) defines 108 cells:

- Applications: Petclinic, OpenTelemetry Demo and DeathStarBench Social Network.
- SDK tracing: absent, partial and full.
- Runtime treatments: no eBPF agent, OBI, Coroot and DeepFlow.
- Repetitions: 9, 10 and 11; all ten application operations are retained.

The no-agent treatment runs without a study eBPF collector. Model acquisition and
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

The [results and limitations](docs/FINDINGS.md) cover all 108 completed cases.
OBI supplies operation models without SDK traces for Petclinic and OTel Demo;
partial OTel coverage requires the observed-context union. The tested eBPF
eBPF-only pipelines do not restore the missing Social Network operation models.
Combining SDK structure with Coroot/DeepFlow network observations supports 48
database-fault forecast rows over 24 shared case-operation outcome sets.

The [corrected Social Network results](results/correction-publication.json)
retain 36 fresh independent checks of the corrected HTTP-ACK and timeline
contracts. All nine forecast blocks were frozen before the checks. Pure eBPF
still supplies none of the three Social Network operation models; SDK coverage
and the missing Thrift chains determine the available models. All 36 raw captures
and the correction's execution metadata are retained in Release storage.

The [original generated results](results/literal-results.json),
[publication manifest](docs/v6-full108-completed-result-manifest.json),
[cost ledger](docs/v6-full108-completed-cost-ledger.json) and
[provenance](results/provenance.json) preserve the complete result scope,
including unavailable predictions and adverse outcomes.
The [outcome-semantics correction](results/semantic-correction.json) identifies
the Social Network HTTP-ACK/MongoDB-write contract mismatch and links the
completed prospective correction. HTTP acknowledgement does not prove storage
or durability.
The [publication archive receipt](results/archive.json) identifies the retained
metadata and the report replay that does not require live Actions API access.
The [reproduction guide](docs/REPRODUCING.md) describes acquisition and report
generation; the [context baseline](docs/CONTEXT_BASELINE.md) specifies the
observed-edge union.

The [compact publication workflow](.github/workflows/compact-publication.yml)
packages the source and analytical results of every case, with an optional
single real eBPF input/model example. It has a 2 GB total budget and does not
copy the full historical raw archive. The
[reproduction guide](docs/REPRODUCING.md#compact-publication-package) states the
included checks and the limits of the compact data.

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

