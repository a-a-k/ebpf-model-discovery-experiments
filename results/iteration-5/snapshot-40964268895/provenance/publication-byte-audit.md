# Report 40964268895 publication-byte audit

Scope: read-only inspection of retained publication members. No source-artifact
retrieval, forecast replay, refit, relinking, rescoring, metric calculation, or
scientific admission was performed.

## Retention boundary

- Actions artifact: `12938546020`; API ZIP size `422662485` bytes and API digest
  `sha256:61aaf7eb3890223241ddd882a77ae60fe3815c68bf754905458ed3acf5013cdb`.
- The whole ZIP was **not** downloaded or locally hash-verified. The retained
  selection is all 623 non-directory publication members except legacy
  `source-artifacts/` recovery ZIP bodies. `selected-inspection.json` is 149650
  bytes, SHA-256 `56bff638604efcec2a86b1d774f94b09cb8dd759ea20325448c403447b1c36a7`.
- All 623 selected files independently match the retained member byte and
  SHA-256 declarations; there are no missing, extra, or mismatched selected
  files. This is a selected-member claim, not a whole-ZIP claim.

## Payload and figure binding

- `evaluation-payload-manifest.json` (SHA-256
  `a1bcba5483fb2c1c9ff9cf1e7f7d779b00818c1d46b1295935fb00ef3a9b3f64`)
  declares 68 exact source evaluation payloads. All 68 gzip files match their
  declared compressed size/hash and restore without error: 25,700,743 compressed
  bytes restore to 1,614,491,752 source bytes, with every restored size and
  SHA-256 matching its declaration.
- `evaluation-v5.json.gz` (231288 bytes, SHA-256
  `bafe4ee1629d46e0ba7250d402d4d9a86828530c6b495dcf5892de024bfc64cc`)
  restores exactly to `evaluation-v5.json` (2707661 bytes, SHA-256
  `b5be4d23b9d5d24703988137dd0e26e497462f8dc06108946714fd343dedcfc8`).
- `saved-values-v5.json` (SHA-256
  `7a93d5ad00bd4c5a40bb1c86c9501043a74a231460907aaedf287849cbb9d59b`)
  names the aggregate gzip above and copies the aggregate grid, selection,
  independent-admission flag object, and 14 selected attempt references exactly.
  Its 324 saved rows were compared field-by-field with the `evaluations` arrays
  in the 14 referenced restored source payloads. Attempt metadata, evaluation
  references, availability/reason, predictions, intervals, error ranges,
  outcome counts, and empirical bounds all match; zero mismatches were found.
- All 20 entries in `figure-files-v5.json` (SHA-256
  `b51fc58baed26256f953014de2636a17e897e34c6a6cfe7b8e5b24531b899dbf`)
  match their retained bytes and hashes. The six PNGs were visually inspected:
  titles, operation/source/variant labels, axes, seed legend, colors, unknown
  labels, and `U` annotations are readable.

## Interpretation boundaries

- The aggregate contains 14 technically selected main attempts. Technical
  selection is explicitly not independent admission; the reporter does not
  perform independent review. The separately maintained reviewer status is 12
  independently reviewed attempts and must not be replaced by the reporter's
  self-reported technical selection.
- `U` is the saved count of unknown **external outcomes**, not a count of unknown
  forecasts. Every selected figure row has `U=0`; unavailable forecasts therefore
  correctly appear as `unknown; U=0`.
- Petclinic partial/full seed 7 retains a small nonzero error for
  `owner_details_with_visits`: fraction `0.0004166666666666208`, or
  `0.04166666666666208` percentage points. It is below one pixel on the fixed
  0--100 percentage-point axis, but remains exact in the companion JSON and
  Markdown. The figures must not be summarized as showing universally perfect
  forecasts.
- In Petclinic/full, saved native forecasts for `create_visit`, `list_owners`,
  and `list_vets` remain unavailable (`required_graph_evidence_unavailable`),
  consistent with the separately documented pinned-route binding limitation.
  This is not evidence that native traces lack information or that another
  binding would satisfy every obligation.
- The OTel figure's `checkout` row is the declared primary checkout outcome. It
  does not constitute a separate forecast or positive result for asynchronous
  Kafka ancestry; missing Kafka ancestry remains an empirical unknown under the
  protocol.

No byte discrepancy or figure-to-payload value discrepancy was found. Visual
resolution of the tiny adverse errors is the only presentation limitation noted;
the exact companion values and caption preserve it.
