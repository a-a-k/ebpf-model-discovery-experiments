# Petclinic on the existing model worker

Source `0565115511b24db1d6bbe71e98784baded772144` changes one workflow routing
line: Petclinic uses the existing closed-checkpoint worker already used by
OTel Demo and DeathStarBench. All production Python, application declarations,
model code, binaries and payload-processing code remain identical to
`f7ba801d70f9d2327031efc6dd0c00b90d252708`. The second changed file extends the
existing worker import fixture with Petclinic success and atomic-import failure.

The original Petclinic partial/8 job, `124430032803`, ended with exit 143 after
the runner reported a shutdown signal. Its retained resource sample at
18:46:07 UTC shows 247,472 KiB available of 16,367,524 KiB RAM, and 835,784 KiB
free of 11,534,328 KiB swap. Bering used 8,069,868 KiB RSS while the two QEMU
processes used 4,689,296 and 2,369,892 KiB. This demonstrates severe memory
contention and swapping. The OOM-kill counter was zero; the physical cause of
the shutdown signal remains unproved.

The strongest simple baseline is the already implemented worker, with the same
closed uploaded checkpoint, `ToolchainV5`, `ObservationStoreV5`, Petclinic
`experiment_v4` declaration, plans, binaries and scientific parameters. Existing
all-file, SQL, source, output, pre-target freeze and independent-outcome checks
remain. The worker's immutable-path preparation and recorded `GOMEMLIMIT=12GiB`
are existing operational paths. There is no new inference method, cache,
runner, reduced workload or extra semantic information.

[Exact producer CI 41340135875](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41340135875)
passed the Linux implementation and pinned control checks. Local focused worker
fixtures passed 43 tests with one Windows skip. Original design and frozen-code
review accepted same-program/input equivalence without another expensive
full-model qualification run. An actual Petclinic worker case still needs its
retained verified worker import and independent outcomes before case admission.

The consumer names this exact source and retains the full Git path/blob/type/mode
guard. Compared with the common scientific anchor, its changed and added path
sets equal the streamed source's sets; only the reviewed workflow and test blob
values differ. The inherited JSONL/storage/input proofs retain their actual
`f7ba801`/C/T/U/V tested-source identities. This routing's code/CI evidence is
separate from those saved-input proofs.

All original failures, prefixes, local computations, preparation, CI, worker,
transfer, verification, waiting and archival costs remain attributable. Current
healthy captures continue at their frozen sources. This change does not prove
a whole-case speedup, a shutdown cause, zero capture loss or completion of the
81-case study.
