# DeepFlow main freeze/preflight memory: source diagnosis and bounded proposal

Read-only analysis on 2026-10-30. This is a proposed engineering qualification,
not an implementation or permission to rerun a cell. The exact relevant files are
identical between heads `51c9697ed71bfb98919936c95440e0a21ed6731b` and
`6ecd280207fbf850757c2c67e807054305f058ec`.

## What the log marker actually bounds

`toolchain_v4.py:585-589` prints `preflight_start`, runs `preflight()`, and then
runs `prepare_inputs(plans)`. There is no `preflight_complete` or
`input_preparation_start` event between them. Therefore the observed allocation
after `preflight_start` is not, by itself, evidence that the Procrustes subprocess
allocated the memory.

For seed 7, the campaign Python RSS was about 653 MiB immediately before and just
after `preflight_start` (`23:39:20` and `23:39:41`). It then rose to about 1.76 GiB
at `23:40:22`, 4.63 GiB at `23:40:43`, and later approximately 8.8 GiB. No
`shared_discovery_start` was emitted. This places the growth within
`preflight()+prepare_inputs()`, before Bering discovery, but the saved run has no
live Python allocation stack.

The actual static Procrustes inputs are small: the two retained Compose files are
9,723 and 2,494 bytes. Pinned Procrustes `internal/app/app.go:70-87` reads those
sources and prints only a goal-status and output-path line on success. Python
`Context.run()` does use `capture_output=True`, so capture is theoretically
unbounded, but the pinned successful CLI path and retained inputs give no source
basis for multi-gigabyte output. It is not the defensible primary allocator.

## Strong source-supported allocator

`toolchain_v4.py:499-502` calls `StoreV5.service_projections()` before any source
export. At the exact failed heads, `store_v5.py` does all of the following:

- lines 324-326: materializes every `resolved_enriched` SQL row, including the
  full resolution JSON string, with `rows = list(...)`;
- lines 345-346: builds a second full list while `json.loads`-decoding every
  retained resolution, keeping both the original strings and parsed dictionaries;
- lines 358-443: verifies every row and retains each full parsed resolution again
  in the returned locator-keyed `result` mapping.

The immutable seed-6 checkpoint proves the scale without recomputation:

- `observation-index.sqlite`: 5,813,833,728 uncompressed bytes;
- `runtime-identity-v5/projection-training.jsonl`: 1,518,969,265 bytes;
- `observations/a.jsonl`: 2,304,002,821 bytes;
- `observations/deepflow-codec-accounting.jsonl`: 932,602,555 bytes;
- `refresh-cost-training.json`: 433,624 projection rows, of which 432,240 are
  `resolved_enriched`;
- `index-training.json`: 433,624 unique observations.

The independently retained seed-7 checkpoint has the same scale and code path:
434,731 projection/index rows, including 433,285 `resolved_enriched` rows, a
1,972,781,056-byte observation index, 24,600 enclosures, and a 32,830,211-byte
inventory. Its saved projection SHA-256 is
`f55dfaddcfbec3c53936a25319760d2ade8833f01440e7fdd4a323ac69e253d7`.

Thus the exact source creates three simultaneous Python representations of roughly
432 thousand large resolution records. The timing and multi-gigabyte retained
input make this the strongest defensible likely allocator. Because no tracemalloc,
live stack, or completed input-preparation record survived, it remains a
source-supported diagnosis rather than proof of the exact live heap composition.

## Deterministic next scale boundary

Fixing only the SQL list is insufficient. In `raw_v4.py` the DeepFlow-derived
branch creates one exported file/manifest entry per wrapper line, embeds every
full projection object as `runtime_identity_transformations` (lines 645-649), and
retains all export dictionaries in `exports`; line 660 counts the embedded lists.
With 433,624 observations and both raw/network-scope variants, this is another
large in-memory and file-count expansion even if projection lookup becomes lazy.

## Minimum end-to-end repair to seek ORIGINAL approval for

1. Replace `service_projections()`'s three full in-memory representations with a
   read-only, disk-backed/streaming locator resolver. It must preserve all existing
   hash, size, clock, lifecycle, raw-segment and conflict checks. Immutable
   dependencies remain cached by exact path/hash/size; each raw segment remains
   independently verified.
2. Stream DeepFlow derived OTLP into deterministic bounded transport shards rather
   than one file and one manifest object per input line. Do not merge identities,
   invent IDs, change source order, or drop envelope/resource/scope/span fields.
3. Store the unchanged full transformation objects in deterministic JSONL
   sidecars and reference each sidecar by row count, raw byte count and SHA-256
   from the small export manifest. The sidecar must restore the exact ordered
   transformation sequence; it is representation/transport, not a new scientific
   input or inference.
4. Add separate events around static preflight and input preparation plus retained
   peak-RSS/cost records. Diagnostics must not become an accuracy or favorable
   graph gate.

The shard boundary is a transport bound, never an observation/early-stop bound;
all source records must be consumed. Ordinary original-wire OTLP guards and native
paths remain unchanged.

## Proposed saved-checkpoint Actions qualification (not yet authorized)

Use artifact `12940068074` only, after verifying its API identity/digest and the
checkpoint manifest. Preserve the original artifact unchanged.

- Bind exact old sources from head `51c9697...`, candidate sources, and the pinned
  Procrustes/Bering binaries.
- Run the old and new static Procrustes path on the same two retained Compose files
  and require every report/collection-plan/overlay byte to be identical.
- Build an old-semantic oracle from the immutable SQLite/projection rows using the
  exact old locator/projection rules but emit canonical hashes incrementally; it
  must not materialize the old 432k-row dictionary. Compare every candidate lookup
  and ordered sidecar row to that oracle, including unknown/conflict rows and raw
  locator/hash evidence.
- Restore each new transformation sidecar and require the exact ordered canonical
  row-hash stream to equal the old semantic oracle. Require exported OTLP records,
  order, IDs, resources/scopes/spans and copied service-name changes to match the
  same frozen effective Store view for all 433,624 observations.
- Exercise actual pinned Bering ingestion of the bounded shards as software
  qualification. Do not run Sheaft, workloads, classes, forecasts, outcomes, or
  rescore/relabel either failed main attempt. No favorable graph shape is required.
- Retain old/new source hashes, output hashes, row counts, peak RSS, wall/CPU time,
  disk bytes and all failed qualification costs. A lower memory result is an
  engineering qualification only, not the article's utility/contribution result.

Only after root and the independent skeptic grant explicit ORIGINAL-criterion GO
should implementation or this Actions qualification occur.
