# Iteration-5 intermediate main-series snapshot

Generated in [Actions run 40930225342](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40930225342)
at `f5ac530ec4a13cecd6178fffcdd886628f47af04`, then copied without refitting,
relinking or rescoring. This is an intermediate snapshot; the fixed study has
108 main cells, including 27 access-blocked New Relic cells.

- [Generated report](report-v5.md) retains every declared attempt and five
  technically complete main cells. Smoke results are separate.
- [Saved aggregate](evaluation-v5.json.gz) preserves the original compressed
  bytes. Its [packaging proof](provenance/aggregate-packaging.json) identifies
  the exact restored JSON; no source fields were omitted or recomputed.
- [Declared inputs](provenance/declarations.json) and [saved costs](costs-v5.json)
  identify the snapshot boundary. Full retrieval and Actions metadata remain
  in the source artifact.
- [Independent review](../../../docs/REVIEW_V5.md) is separate from the
  reporter's transport checks, whose independent-admission flags remain false.

The five main cells have separately passed actual evidence review: OBI
Petclinic/absent seeds 6/7/8 from [run 40910013685](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40910013685),
and OBI Petclinic/partial seeds 6/7 from [run 40914709370](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40914709370).
Each retains an actual Bering graph, Sheaft invocation, forecast saved before
validation, original observations, and independent application outcomes.
Partial seed 7 retains the owner-details mismatch: forecast `0.875`, observed
`2099/2400`. It is not rerun or excluded for this difference. The equally
informed direct baseline makes the same prediction; no utility or complete-cost
advantage is established by this snapshot.

The retained ledger declares 103 repository-qualified runs and records 80,264
completed job-seconds. Running-job tails, human effort, work outside the declared
boundary and later publication costs are not zero or a completed total. Job
seconds sum overlapping execution and waiting; they are not wall-clock duration.
The original zero-main [earlier snapshot](../snapshot-40905967491/SOURCE.md)
remains unchanged.

The source artifact is `report-v5-40930225342`, ID `12921733573`, 638,543,351
bytes. GitHub reports this whole-ZIP SHA-256:

```text
b997086495790899f2579338cb2345b464280c8581bae6bb1caa1d3ae6ff6e04
```

Local inspection fetched selected ZIP members, verified their CRC and recorded
member SHA-256 values in the five `provenance/download-*.json` records. It did
**not** verify the complete ZIP locally. The source artifact retains historical
recovery ZIPs and complete retrieval metadata, which are not duplicated here.

The compressed aggregate is 34,568,276 bytes with SHA-256
`110cd3572ffef0ae47e2cbd42b02d25ea902484e82bf595f35c6bac8ee614803`.
Its exact restored 2,027,464,966 bytes were verified with streaming decompression
and SHA-256 `9dfe956b26a5608440e04f0d5e1a43e33faaa867113c88d4d5253e2636d12108`.
This aggregate contains large copied source records; prefer the generated report
for reading and streaming decompression for inspection.

```sh
gzip -dc evaluation-v5.json.gz > evaluation-v5.json
```
