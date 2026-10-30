# Scope and status correction, 2026-10-30

The active study compares **OBI, DeepFlow and Coroot**: three systems, three
tracing modes and seeds 6/7/8, for **81 main cells** after **27 smoke settings**.
The user explicitly excluded New Relic. Continuing to list it as 27
credential-blocked cells was an orchestration error. No credential is needed,
and those cells are neither pending work nor negative results in the active study.

The orchestrator also repeated a stale status of 17 running campaigns before
checking GitHub again. The fresh API observation found that all had ended;
the queue had not been continued promptly. This was an execution/status error.
Neither error is evidence that the saved measurements are valid or invalid by
itself. They require a cross-check of the declared design, actual execution and
published values; a blanket assurance that only prose was affected is unwarranted.

## Retained evidence and scope change

The [previous declaration](../results/iteration-5/scope-correction-20261030/previous-declarations.json)
is preserved byte-exact with SHA-256
`aa192612de08289a70c10109babc36d4c28fda61bc23e8a5215e7aa3655d29be`.
Its 67 declared acquisition runs already identify only OBI, DeepFlow or Coroot.
The correction removes the 27 obsolete New Relic blocked rows from the current
declaration and preserves every real attempt and related cost record. Any
previous preparation effort remains a cost; it is not erased by the exclusion.

Current campaign choices, collector factory, reporting grid and protocol use
three collectors. The reporter renders the grid count stored in its input, so
historical 108-cell snapshots retain their original interpretation when read.
Those immutable snapshots remain historical artifacts with superseded scope;
their missing New Relic rows are not current failures or coverage requirements.
Regression checks reject the excluded collector in new attempt and blocked-cell
declarations and retain the old count when rendering a historical aggregate.

Root and the separate skeptic gave explicit original-criterion GO before this
correction. No remaining workload, operation, state mixture, semantic assumption,
graph rule, forecast, external outcome, accuracy rule or technical failure is
changed. Equal-information direct and native/combined baselines and complete-cost
limitations remain in force. This is not a positive-result selection.

## Timestamped execution inventory

The [fresh API inventory](../results/iteration-5/scope-correction-20261030/status-api-20261030T041344Z.json)
was observed at **04:13:44–04:13:59 UTC on 2026-10-30** (07:13 Moscow).
It covers all 30 then-declared main parent runs and their job/artifact metadata.
All were terminal in that observation. It does not claim to describe subsequent
dispatches or to independently admit any scientific result.

Execution success, scientific admission and published coverage are separate.
The audit follows agreed parameters through retained raw inputs, actual Bering
graphs and Sheaft invocations where supported, pre-validation model/forecast
freezes, independent application outcomes and exact published values. Unsupported
forecasts remain unknown; incomplete acquisition or packaging remains technical
failure. Independent review is performed by the separate agent identified in
[REVIEW_V5.md](REVIEW_V5.md), not by an external human peer reviewer.

## Bounded independent audit

The [audit manifest](../results/iteration-5/scope-correction-20261030/audit/audit-manifest.json)
and [reading notes](../results/iteration-5/scope-correction-20261030/audit/README.txt)
bind that observation to the following distinct categories:

| Category at the retained observation | Count | Interpretation |
| --- | ---: | --- |
| Independently reviewed main cells | 16 | 14 historical snapshot cells plus two later DeathStarBench/absent reviews |
| Successful jobs pending independent packet review | 17 | Candidate results; no admission is implied by job success |
| Failed or cancelled main attempts | 19 | Ineligible attempts, including earlier attempts for subsequently repeated cells |

The categories describe 52 campaign jobs in 30 parent runs, not 52 distinct
cells of the 81-cell study. Review records are stored as deterministic gzip:
1,135,113 stored bytes restore the exact 102,155,512 original bytes. Each record
has explicit stored and restored size/hash fields. No source evaluation or
scientific metric was recomputed for this audit. The old narrower DeepFlow
diagnosis is retained and explicitly superseded on the preflight/prepare-input
boundary; the exact live allocator remains unproved.

This audit does not supply missing human preparation costs, admit the 17 pending
candidates, or establish a utility or complete-effort advantage. Later runs and
reviews require their own dated evidence.

The [first-publication binding](../results/iteration-5/scope-correction-20261030/audit/publication-binding.json)
ties the original review-time hashes to immutable Git blobs at `c5df32f`.
Code, workflow and test bytes match exactly. Three documentation additions and
one line-ending normalization are explicit and reconstruct the original hashes;
the original manifest remains unchanged. This binding is specific to that first
publication, not a claim about every subsequent revision.
