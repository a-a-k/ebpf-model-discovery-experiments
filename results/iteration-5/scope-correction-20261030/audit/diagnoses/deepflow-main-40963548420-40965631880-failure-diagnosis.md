# DeepFlow Petclinic absent main seeds 6/7: retained failure diagnosis

Read-only diagnosis on 2026-10-30. No rerun, cancellation, source change, forecast,
or empirical recomputation was performed.

## Fixed executions

- seed 6: run `40963548420`, job `123762196894`, head
  `51c9697ed71bfb98919936c95440e0a21ed6731b`
- seed 7: run `40965631880`, job `123769331220`, head
  `6ecd280207fbf850757c2c67e807054305f058ec`

Both successfully acquired and closed the training prefix, uploaded its checkpoint,
and bound the upload to the still-live campaign. Both failed only in step 13,
`Continue discovery and validation on the same live guests`. Therefore these are
technical interruptions after training capture, not evidence that an unavailable
forecast or an application operation failed.

## Seed 7 direct failure evidence

The last scientific-stage event printed was:

`2026-10-29T23:39:31.9051668Z {"toolchain_event":"preflight_start","system":"petclinic"}`

No `shared_discovery_start` or later toolchain completion event was printed. The
campaign Python process (PID 6453) grew from about 5.1 GiB RSS to about 8.8 GiB and
remained around 8.3--8.8 GiB until interruption. Near the end the two QEMU guests
used roughly 4.1 GiB and 2.1 GiB RSS. `MemAvailable` was roughly 0.2 GiB, the
11 GiB allocated swap was almost exhausted, and the retained heartbeat showed
millions of swapped pages and sustained memory pressure. The retained
`oom_kill_counter` remained zero.

At `2026-10-30T01:09:37Z` GitHub reported exit code 143 and explicitly said that
the runner received a shutdown signal. This establishes runner termination under
severe resource pressure, but does **not** establish a kernel OOM kill. The saved
log does not identify which preflight suboperation allocated the memory, so that
lower-level allocator cause remains unknown.

## Seed 6 direct failure evidence

The campaign job annotation is:

`The hosted runner lost communication with the server. Anything in your workflow
that terminates the runner process, starves it for CPU/Memory, or blocks its network
access can cause this error.`

The job-log endpoint returns `log not found`, so seed 6 does not independently
prove the seed-7 memory trajectory or a specific OOM/network cause. Its step
boundary is nevertheless the same: training/checkpoint/upload succeeded and
continuation failed. The precise seed-6 low-level mechanism therefore remains
`runner communication lost; cause unresolved`.

## Retained artifacts and unavailable results

- seed 6 training artifact `12940068074`, 1,254,329,913 bytes,
  API digest `sha256:02524ce918c2ab95e2b8a6854c5f1888b0493ee3b924c63777db2591b9f95116`
- seed 7 training artifact `12941184407`, 1,257,490,009 bytes,
  API digest `sha256:8de2dc25fecb8ada7c44107f426d69976a1174a7fc7519468cd41ee5df54dbf9`

No final campaign/status/evaluation artifact was published for either run. Their
original acquisition and preparation costs remain attributable, but neither run
is technically complete or eligible for a forecast/result claim.

## Source boundary observed, not a root-cause claim

At these heads `Toolchain.forecast()` prints `preflight_start`, then executes
`preflight()` before input export or Bering discovery. `preflight()` runs the
source-pinned Procrustes analyses through `Context.run()`, whose subprocess output
is captured in memory and only journaled after a command returns. Since there is
no completed command record/final artifact, the retained evidence locates the
interruption before `shared_discovery_start` but does not distinguish a particular
Procrustes invocation, output capture, retained campaign state, or another
preflight-time allocation. That distinction requires a separately reviewed
diagnostic change; it must not be inferred from these incomplete executions.

New Relic is excluded from the active series by the user's later directive and is
not part of this diagnosis.
