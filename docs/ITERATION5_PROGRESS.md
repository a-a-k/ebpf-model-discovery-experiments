# Iteration 5 implementation and qualification record

Status: implementation and technical qualification; no new empirical finding or
main-series completion is claimed. The scientific design is in
[PROTOCOL_V5.md](PROTOCOL_V5.md). Iteration 4 results remain unchanged.

## Product boundary and published toolchain

All four fresh collector arms use the same vendor-neutral `ebpf-otlp` input.
The product API has no collector/vendor parameter. Agent configuration and
vendor-specific codecs live in this experiment repository; collector identity is
retained in the study manifests. Logical source IDs/domains isolate observations.

- [Bering PR 54](https://github.com/MB3R-Lab/Bering/pull/54) merged at
  `70d4145d3e26f11d8b3fb5be8917c50c1c6d8c2a`.
- [Procrustes PR 3](https://github.com/MB3R-Lab/Procrustes/pull/3) merged at
  `9648ae3fe9ef24725e665d008c79d0681ce40f85`. It remains a source-built preview.
- [Bering 1.3.0](https://github.com/MB3R-Lab/Bering/releases/tag/v1.3.0) and its
  Helm chart were published by [release run 40879223434](https://github.com/MB3R-Lab/Bering/actions/runs/40879223434).
  The image digest is
  `sha256:95c29e311edfb5297c8bc22da6201a122f07e9492770a384fe93d8fac7d0da9c`;
  chart version/appVersion are `1.3.0`, with OCI manifest digest
  `sha256:e3128dc852f2ecac9358e447442266ae420beb087f80a65ddd725d95f09b0f19`.
  Published metadata checksums, chart package, anonymous image manifests/configs
  and anonymous chart retrieval were verified. Model/snapshot contracts remain
  `1.3.0`; Sheaft remains pinned to its existing `1.3.2` source revision.
- [Stack PR 31](https://github.com/MB3R-Lab/mb3r-stack/pull/31) merged at
  `4ba1d790d66c47976dc6cc05dfeb6e812427eb58` after full integration CI.
  [Stack 1.5.0](https://github.com/MB3R-Lab/mb3r-stack/releases/tag/v1.5.0)
  and its chart passed [publication and anonymous preflight download/run](https://github.com/MB3R-Lab/mb3r-stack/actions/runs/40886588360).
  Downloaded manifest and chart hashes match the published assets; the chart
  version/appVersion are `1.5.0`, and its prerelease annotation is false.

## Smoke history

The original-criterion reviewer approved OBI technical execution at
`e42442da532a815f928fefbbe961144cc412aeef` after
[Linux checks 40878924384](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40878924384).

[First OBI smoke run 40880849418](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40880849418)
reached the DeathStarBench guest deployments, then failed in the auxiliary HTTP
control before training/validation measurements. All three DeathStarBench modes
reported `technical control HTTP request failed on a`. Completed campaign and
summary artifacts were retained, and the remaining queue was cancelled after the
common failure was identified. This is a preparation failure, not an unavailable
or inaccurate application forecast.

The repaired fixture passed both the full Linux unit suite and a separate real
Docker fixture check at `b0c068aee35571565abfe6a8389599c71683d5df` in
[checks 40883942639](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40883942639).
The reviewer approved one fixed repeat before requeueing the matrix.
[Repeat smoke 40884914635](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40884914635)
uses OBI, DeathStarBench, partial tracing and seed 6 at that revision. Both HTTP
controls replied successfully, but selected eBPF origin was not confirmed:
guest A had no matching marker/origin proof, and guest B had no receiver file
at the proof check. The attempt failed before workload operations. A later
successful receiver drain does not retroactively prove the control. Diagnosis
of the retained collector logs and bytes is ongoing.

The original fixture assumed the pinned HAProxy image could run `busybox httpd`
and did not preserve sufficient failed-request diagnostics. The revised fixture
uses HAProxy itself, checks configuration/process/HTTP readiness, retains every
probe and container diagnostic on failure, and has a separate Docker execution
check in CI. The precise original server failure is not retrospectively asserted
from the generic exception alone. A single corrected campaign smoke precedes
requeueing the remaining fixed settings.

DeepFlow's standalone codec, streaming retention, common control and runtime
identity projection passed independent integration review and
[Linux/Docker CI 40885659304](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40885659304)
at `986dea703798315b0f33f5d0771ec3725fae76e2`.
[First DeepFlow smoke 40885990713](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40885990713)
used Petclinic, absent tracing and seed 6. It failed during preparation at an
unprivileged read of `/proc/1/ns/pid`, before the collector and workload started;
cleanup also attempted to use the not-yet-installed snapshot helper. These are
preparation defects, not evidence of application protocol coverage.

Coroot has no completed smoke yet. New Relic access and license conditions remain
unresolved; it has not been silently substituted or counted as measured.

Smoke preparation, failed attempts, artifact retention and implementation effort
remain costs of this iteration. A CI pass or technically complete all-unknown
output does not establish the required graph-to-Sheaft-to-external-outcome path.
