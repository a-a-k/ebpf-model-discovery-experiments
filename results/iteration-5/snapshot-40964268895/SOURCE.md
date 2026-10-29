# Iteration-5 intermediate snapshot with saved error figures

Generated in [Actions run 40964268895](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40964268895)
at `6ecd280207fbf850757c2c67e807054305f058ec`. Files were copied from its
retained report artifact without acquisition, refitting, relinking or rescoring.
The fixed study still contains 108 main cells; 27 New Relic cells remain blocked
by unavailable authorized access and an unqualified local collector codec.

- [Generated report](report-v5.md): all declared attempts and 14 technically
  selected main cells. Smoke results do not count as main cells.
- [Figures and exact plotted values](figures/figures-v5.md): per-operation,
  per-source and per-seed saved errors, including unavailable forecasts.
- [Aggregate](evaluation-v5.json.gz), [source-payload manifest](evaluation-payload-manifest.json)
  and `evaluation-payloads/`: referenced evaluations retain their exact original
  bytes as gzip payloads. The aggregate alone is not the complete evidence.
- [Input declarations](provenance/declarations.json), [retrieval records](provenance/retrieval.json)
  and [costs](costs-v5.json) fix this snapshot's execution boundary.

## Selection and independent-review boundary

The 14 technically selected cells are nine OBI Petclinic cells (three modes and
three repeats), three Coroot Petclinic/absent repeats, OBI DeathStarBench/absent
seed 7, and OBI OTel Demo/absent seed 6. At publication preparation, the 12
Petclinic cells had separately passed actual evidence review. The DeathStarBench
and OTel packets remain pending that review; their inclusion in a technical
report is not independent admission. The reporter's independent-admission flags
remain false. Subsequent review is recorded separately in
[REVIEW_V5.md](../../../docs/REVIEW_V5.md).

The OBI Petclinic forecasts use actual recovered graphs and Sheaft executions.
Partial and full seed 7 retain the additional owner-details failure:
`2099/2400` observed against forecast `0.875`. Coroot Petclinic/absent retains
all unavailable forecasts despite known external outcomes. The OBI OTel candidate
contains available primary-request forecasts for all three operations; this
does not establish checkout-to-Kafka-to-database causal linkage or asynchronous
business completion. Missing or ambiguous DB channels are manually assumed
fulfilled for these conditional replica-only forecasts, with the same assumptions
given to the direct baseline; DB-fault forecasts remain unknown. The
DeathStarBench candidate retains unavailable forecasts.

Native Petclinic has an independently diagnosed route-versus-URL binding
limitation even though the raw trace contains the URL; see
[OBSERVATION_LIMITS_V5.md](../../../docs/OBSERVATION_LIMITS_V5.md). These results
do not demonstrate that native tracing lacks the necessary information.

Figure points and ranges copy saved values, with fractions displayed as percentage
points. Ranges are not confidence intervals. Missing forecasts and missing repeats
are not zero errors. `U` denotes unknown external outcomes. Different source and
preparation revisions prevent attributing cost differences solely to collectors.
The equally informed direct predicate gives the same primary predictions where
applicable; stable family identity equals the base entry classifier. Neither
utility superiority nor lower complete effort is established.

## Costs and immutable history

The retained declarations contain 60 attempt runs and 115 related runs. Their
175 repository-qualified cost records contain 249,826 completed job-seconds and
84,422,877,678 stored artifact bytes. These are snapshot totals, not the final
study cost: active-job tails, human effort, undeclared work and this report's own
remaining execution/publication costs are not zero. Job seconds include overlapping
jobs and parent waiting; they do not equal elapsed study duration.

The [five-cell snapshot](../snapshot-40930225342/SOURCE.md) and
[initial zero-main snapshot](../snapshot-40905967491/SOURCE.md) remain unchanged.
Original technical failures, cancelled version-replacement attempts and their
costs remain in the retained declarations and report. Selection never uses error
or forecast availability.

## Transfer and byte verification

The source artifact is `report-v5-40964268895`, ID `12938546020`, 422,662,485
bytes. GitHub reports this whole-ZIP SHA-256:

```text
61aaf7eb3890223241ddd882a77ae60fe3815c68bf754905458ed3acf5013cdb
```

Local inspection verified CRC and SHA-256 for all 623 publication members
(37,279,324 restored bytes), using 23,155,029 exact HTTP range bytes. The
[inspection record](provenance/local-selected-inspection.json) explicitly says
`whole_zip_hash_verified: false`: the complete 422 MB ZIP was not hashed locally.
The source artifact also retains 15 historical recovery ZIP bodies under
`source-artifacts/`; those bodies are not duplicated here. Their retained
provenance remains available, and this omission does not remove source-evaluation
payloads from the published report.

The [aggregate packaging proof](provenance/aggregate-packaging.json) binds the
231,288-byte gzip (`bafe4ee1629d46e0ba7250d402d4d9a86828530c6b495dcf5892de024bfc64cc`)
to its exact 2,707,661-byte JSON
(`b5be4d23b9d5d24703988137dd0e26e497462f8dc06108946714fd343dedcfc8`).
The [figure manifest](figures/figure-files-v5.json) binds each PNG, SVG, PDF and
companion table to that aggregate. Full campaign observations, graphs, forecasts
and journals remain in the source campaign artifacts identified by these records.
The separate [publication byte audit](provenance/publication-byte-audit.md)
verified all 68 restored source payloads and all 324 plotted-value rows against
their exact source fields. This checks faithful reporting, not scientific
admission of the two pending main packets.
