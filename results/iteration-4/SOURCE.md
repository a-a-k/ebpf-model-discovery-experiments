# Interim iteration-4 report: all nine Petclinic cells

Generated in [Actions run 40751134324](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40751134324)
at `a839a94fe38d2c347f4156c528367bbef9d21116`, then copied without recalculation.
This snapshot covers **9/27 planned cells**, Petclinic absent/partial/full tracing
with seeds6–8, and 313,200 primary operations. Each original cell passed independent
integrity, mode-enforcement, graph/simulator and external-outcome review. DSB and
OTel remain incomplete; no cross-system or complete-cost advantage is established.

- [Generated report](report-v4.md): every operation/source/variant, unknowns, DB
  interventions, class results, manual baseline and available costs.
- [Figures and saved values](figures/figures-v4.md): repeat availability is shown
  per method; observed repeat ranges are not confidence intervals.
- [Actual Bering graph](figures/petclinic-full-6-ebpf-network_scope.svg) and
  [provenance](provenance/model-example.json), using the same fixed cell as the
  earlier report, before operation/placement overlays.
- [Series runs](provenance/series-input-runs.json) and
  [preparation/reporting/archival runs](provenance/preparation-input-runs.json).

Artifact `report-v4-40751134324`, ID `12843459579`, contains 86 members and is
7,369,190 bytes. Its entire downloaded ZIP and member CRCs were verified:
`f9b3ed77d62cea25bc2087d2bb9631dc00cb484e3ebe19498e89ab3e1109cae6`.

The repository preserves 85 original members byte-for-byte, plus this note.
The 244,640,459-byte plain aggregate remains in the original Actions artifact;
the repository uses the original lossless `evaluation-v4.json.gz` member
(3,741,462 bytes). No fields were omitted. The [packaging record](provenance/aggregate-packaging.json)
records both hashes; local decompression independently reproduced the original
SHA-256 `a58eb877ddb3bb140fb9844f20cbedc74402278c49695f2d2662d186d3e1f80c`.
To restore it, run `gzip -dc evaluation-v4.json.gz > evaluation-v4.json`.

The report validates compact evaluation manifests and the frozen example model;
it does not rerun full raw-data evaluation. The earlier one-cell report remains
in Git history and [data-40740761225](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40740761225).
The current original report ZIP is permanently retained with the same digest in
[data-40753100009](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40753100009).

Costs are a snapshot, including earlier failed and diagnostic attempts. DSB was
still running; its final duration, this reporting job's own eventual duration,
and later work are not included in the snapshot total. Human/agent preparation
cost remains unknown. These gaps cannot be interpreted as zero cost.
