# Final iteration-4 report: 27 independently reviewed campaigns

Generated in [Actions run 40853395506](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40853395506)
at `1406e559d8d8f432179116460b33f118f666550f`, then copied without empirical
recalculation. The selected grid contains all three systems, absent/partial/full
native tracing, and seeds 6–8: **27/27 cells and 939,600 primary attempts**.
The report retains 28 summary attempts, including one technically incomplete OTel
attempt; other failed or worker-only runs retain their available metadata and
costs without being invented as additional completed campaigns.

- [Generated report](report-v4.md): every operation/source/variant, independent
  outcomes, unknowns, DB interventions, classes, asynchronous evidence and costs.
- [Figures and saved values](figures/figures-v4.md): unknowns remain visible;
  observed repeat min–max ranges are descriptive, not confidence intervals.
- [Actual Bering eBPF graph](figures/petclinic-full-6-ebpf-network_scope.svg) and
  [frozen-file provenance](provenance/model-example.json), before operation overlays.
- [Series/worker inventory](provenance/series-input-runs.json),
  [preparation/CI/reporting/archival inventory](provenance/preparation-input-runs.json)
  and [technical selection](../../docs/report-v4-technical-selection.json).
- [Independent scope and claim review](../../docs/REVIEW_V4.md).

This is a completed empirical series, including negative findings. It does not
establish a cost or prediction advantage over the equal-information direct
contract/inventory predicate. Complete human preparation effort is unmeasured.

## Original report and lossless repository representation

Artifact `report-v4-40853395506`, ID `12887858244`, contains 491 files and is
57,824,593 bytes. Its whole ZIP and every member CRC were checked independently:

```text
deb9cc25fd3c3f450da67b90f52233038de71f9e34bcd59bf5ddc59f56cbc909
```

The repository initially copied 490 original members byte-for-byte. The only
omitted member is the 855,633,475-byte plain `evaluation-v4.json`; the unchanged
29,757,695-byte `evaluation-v4.json.gz` restores its exact bytes. The
[packaging record](provenance/aggregate-packaging.json) records:

```text
compressed SHA-256: 9f04bf247430a3f735c70df2acbbf01f204a0a5db65230d5bd4f0841cebafd16
restored SHA-256:   5e6aa5a299e06e4604f69bdcaafc89e008437332f53714136d76fc4ac7d94d85
```

Local streaming decompression independently reproduced the restored hash. No
fields were removed. To restore the plain aggregate:

```sh
gzip -dc evaluation-v4.json.gz > evaluation-v4.json
```

The original ZIP, including the plain JSON and original images, is permanently
retained in [data-40857570938](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40857570938).
The earlier nine-cell report remains in Git history and
[data-40753100009](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40753100009).

## Figure layout correction

Visual inspection found that text-only unknown rows did not affect Matplotlib's
automatic y limits, allowing their labels to overlap the availability heading.
[Actions run 40856854477](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40856854477)
at `7ae587f1e284500c6aa498735f9923511a304626` rendered the same authenticated saved
aggregate with explicit y limits containing every row. It performed no acquisition,
aggregation or refit and required `figures-v4.md` to remain byte-identical.

Artifact `12889696620` is 1,053,136 bytes, with whole-ZIP SHA-256:

```text
f11ac6050639debf2b092ada6c1c35a0085673d34067ce17f2a078fb166933e8
```

All 30 file CRCs and hashes were checked. Only 27 error-image files (nine plots in
SVG/PNG/PDF) replace original report members; 463 other original members remain
byte-identical, including the aggregate, tables, companion figure values and
observed-model example. Two new provenance files record the source and renderer.
[Figure provenance](provenance/figure-correction.json) binds every original/new
image hash and the unchanged input hashes. The figure artifact is retained in
the same permanent release as the original report. This is a presentation repair,
not a new experimental result.

## Raw campaigns, models and worker outputs

Each release's `provenance.tar.gz` lists original artifact IDs/names, run and job
metadata, available logs and SHA-256 values. Large originals use ordered lossless
parts whose manifest specifies reassembly and verification. Whole originals and
part reassembly were checked in archival Actions; local inspection of large
campaign ZIPs checked selected members and does not claim whole local downloads.

| Campaign group | Permanent original-data release |
| --- | --- |
| Petclinic full/6 | [40734810232](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40734810232) |
| Petclinic absent/6–8 | [40745651023](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40745651023) |
| Petclinic partial/6–8 and full/7–8 | [40751164118](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40751164118) |
| OTel full/6 and worker | [40802785036](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40802785036) |
| OTel absent/6–8 and workers | [40819771129](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819771129) |
| OTel partial/6–8 and workers | [40819773522](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819773522) |
| OTel full/7 and worker; completed DSB diagnostic | [40819411131](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819411131) |
| OTel full/8 and worker | [40819413737](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40819413737) |
| DSB absent/6–8 and absent/7 worker | [40841674653](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40841674653) |
| DSB partial/6–8 and partial/7–8 workers | [40845311645](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40845311645) |
| DSB absent/6, absent/8 and partial/6 workers | [40830558372](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40830558372) |
| DSB full/7–8 and workers | [40850799564](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40850799564) |
| DSB full/6 and worker | [40852591158](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40852591158) |

Failed acquisition and diagnostic originals, explicit missing logs and technical
repairs remain linked from [RUN_HISTORY.md](../../docs/RUN_HISTORY.md). The report
validates saved compact manifests and the fixed model example; it does not rerun
raw campaign evaluation. Full raw recomputation remains an Actions-only command
documented in the research README.

## Cost scope and closing evidence

The report's exact declared inventory covers every repository workflow run from
the first v4 code commit (`42ebf33223da579fc68533f2b5c07aa1c4f97f68`,
2026-10-28 03:28:33 UTC) to the pre-report inventory check at 2026-10-29 09:55:10 UTC:
149 runs, comprising 38 series/worker and 111 preparation/diagnostic/CI/reporting/
archival entries. The [saved ledger](costs-v4.json) records 185 jobs, 343,146 known
completed job-seconds and 141,072,330,122 retained Actions-artifact bytes.

This is accumulated job use, not elapsed study time or monetary cost. Artifact
bytes are not unique storage or total transfer; release copies and response bytes
have separately retained records. Two archival jobs were live during collection
(`40850799564`, `40852591158`), so their final durations remain unknown in that
immutable snapshot. The reporting job's own final duration and subsequent
figure-render/CI work are also outside it. Unknown costs are not zero.

The closing [data-40857570938 provenance](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/download/data-40857570938/provenance.tar.gz)
retains completed run/job metadata and available logs for those two archive jobs,
the report (`40853395506`), figure rendering (`40856854477`) and its CI
(`40856777024`). In that tarball, use `<run>-run.json` and
`<run>-jobs-pages.json`. Closing archival execution and subsequent publication CI
are outside both snapshots. No self-inclusive final grand total is asserted.
Independent product-development costs, earlier research iterations and
unmeasured human/agent preparation are not silently charged as zero or used to
claim a complete-effort advantage.
