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
- [Sheaft PR 101](https://github.com/MB3R-Lab/Sheaft/pull/101) and
  [OTel integration PR 8](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/pull/8)
  merged after their required checks. They update published-package compatibility
  and the runtime image respectively; the existing Sheaft release and schemas
  remain unchanged. Full revision, run and digest evidence is in
  [TOOLCHAIN_RELEASES.md](TOOLCHAIN_RELEASES.md).

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

Coroot has not yet passed smoke qualification. New Relic access and license conditions remain
unresolved; it has not been silently substituted or counted as measured.

## Further fixed smoke attempts and diagnosis

The integrated revision `161eb1d606a444e59ec18d6084bbcd62a256fd86` passed
[Linux and Docker CI 40889975595](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40889975595).
Three independently reviewed single-cell attempts ran at that revision:

| Collector and fixed cell | Run | Actual preparation outcome |
|---|---|---|
| OBI, DeathStarBench/partial/6 | [40890296710](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40890296710) | Prestarting the responder did not establish the required raw eBPF-origin proof. |
| DeepFlow, Petclinic/absent/6 | [40890303219](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40890303219) | Protected process access succeeded; collector readiness was not established. |
| Coroot, Petclinic/absent/6 | [40890763831](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40890763831) | The control server could not bind its port. |

All three failed before primary workload operations. Their failures are not
application forecast or protocol-capability findings.

For OBI, the concrete fixture incompatibility is now established from configuration,
container inspection and pinned source. Both controls used Docker host networking.
OBI's `containers_only` process matcher rejects processes in the instrumenter's
own network namespace when it has host PID access
([pinned matcher](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/b28e4e7fe0a01f1961b7c4747a13b8ff486d6fec/pkg/appolly/discover/matcher.go#L255)).
The observed instrumented HAProxy PID on guest A belonged to a different process,
not the control server. Starting the same host-networked control earlier could
not address that filter. The provisional prestart workaround has been removed.

Coroot's retained HAProxy log explicitly reports `Address in use` for
`0.0.0.0:18081`; Petclinic already publishes its visits replica on the guest's
port 18081. The common control now uses an owned private Docker network
with no host port publication, for every collector. It retains the same fresh
request and raw selected-agent origin requirements. All network preparation and
cleanup costs remain attributable to the experiment.

DeepFlow's retained logs show socket-tracer initialization followed by a failed
load of the separate on-CPU profiler's `df_PE_dwarf_unwind` program (`errno 7`)
and watchdog intervention. The attempted readiness marker also differed from
the pinned version's actual post-start marker. The proposed repair disables
unrelated CPU profiling and uses that exact marker; successful request acquisition
still requires the unchanged raw eBPF control. The effect awaits a repeated smoke.

For these three attempts, selected original ZIP members were inspected using
HTTP byte ranges, with a local member hash inventory. No independent full-ZIP
hash verification is claimed for those partial downloads; original full artifacts
and GitHub artifact digests remain available in the linked runs.

Smoke preparation, failed attempts, artifact retention and implementation effort
remain costs of this iteration. A CI pass or technically complete all-unknown
output does not establish the required graph-to-Sheaft-to-external-outcome path.

The common private-network fixture passed real Docker CI on
`a333cdd697b201c3168e4d8f9e5ede771f6d996a`
([40895444290](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40895444290)),
including the occupied-host-port regression. The prior CI failure was a missing
`socket` import in that new test, corrected before dispatch.
The fixed [OBI repeat 40895622472](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40895622472)
and [Coroot repeat 40895637294](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40895637294)
were then dispatched at the same passing revision. Their results are pending.

The DeepFlow repair also replaces the agent's default memory/CPU limits with
positive settings derived from each guest's available resources, retaining raw
inventory, generated configurations, actual Docker/cgroup constraints and
preparation costs. It does not remove the common VM capacity bound. Independent
review approved one fixed repeat after integrated CI; no application-capability
or main-series conclusion follows from this configuration repair.

The integrated DeepFlow repair passed
[CI 40895877074](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40895877074)
at `8b725b8895f0704fdf84f6c1086937dd22dfe6f6`.
Its [fixed repeat 40896064246](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40896064246)
stopped before workload traffic because the new resource verifier incorrectly
required root-cgroup limit files. Retained resource inventory shows unlimited
leaf and `system.slice` CPU/memory values and a successful traversal command;
root `memory.max` and `cpu.max` are absent as specified by the
[Linux cgroup-v2 interface](https://www.kernel.org/doc/html/v6.6/admin-guide/cgroup-v2.html).
The agent log confirms that the intended memory/CPU configuration and disabled
on-CPU profiler were applied. This attempt identifies a verifier defect, not an
application observation limit. The correction must record traversal to the root
separately from the presence of controller files, retaining all actual limits.

OBI repeat `40895622472` passed the raw selected-agent controls on both guests and
closed its training checkpoint. It then failed before forecasting and target
traffic: GitHub rejected the remote worker dispatch with HTTP 422. The exact
response, retained inside `infrastructure/handoff-package/payload.tar.gz`, names
the undeclared `collector_provenance` input. The correction removes this redundant
API input while preserving the collector binding in the checkpoint and verified
worker output. This attempt is a technical failure with partial training data,
not a complete campaign or a forecast result.
