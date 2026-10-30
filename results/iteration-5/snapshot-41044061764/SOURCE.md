# Iteration-5 snapshot: all OBI and Coroot main cells

Generated in [Actions run 41044061764](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41044061764)
at `c7defbcb470adc2b3af3a54879fe1d1be9a7c655`. The report copies saved
evaluations; it does not replay traffic, refit models, relink events, rescore
outcomes, or select by error or forecast availability.

The fixed study contains **81 main cells**. This snapshot selects all **54 OBI
and Coroot cells**, with all 27 DeepFlow cells still incomplete at its retrieval
boundary. Eighteen further DeepFlow cells were dispatched after this report's
declaration boundary; this snapshot is not a live execution inventory.

- [Generated report](report-v5.md): retained attempts, per-operation results,
  source availability, technical replacements and costs.
- [Figures and exact saved values](figures/figures-v5.md): each operation,
  source and repeat, including unknown forecasts and adverse measurements.
- [Compressed aggregate](evaluation-v5.json.gz) and
  [source-payload manifest](evaluation-payload-manifest.json): source identities
  and exact original evaluation references.
- [Declarations](provenance/declarations.json),
  [retrieval records](provenance/retrieval.json) and [costs](costs-v5.json):
  the exact reporting boundary. The [full narrative declarations](provenance/full-narrative-declarations.json)
  also retain optional attempt notes omitted from the workflow input.

## Independent review and interpretation

All 54 selected cells separately passed actual evidence review in the
[first 36 records](../main-review-snapshot-20261030/SOURCE.md),
[next nine](../main-review-41025655518/SOURCE.md), and
[final nine](../main-review-completion-20261030/SOURCE.md).
These are independent AI-agent checks, not external human peer review. The
reporter's own independent-admission flags remain false: copying and checking
saved values does not itself provide independent scientific review.

Available forecasts use actual Bering outputs and actual Sheaft executions with
the disclosed supplied semantics. An unavailable forecast is not a zero error,
nor proof that no graph was produced. Coroot OTel full seeds 6 and 8 retain
native/combined checkout predictions of `0.875` against external outcomes
`276/3200` and `1427/3200`; seed 7 retains unavailable forecasts and `189/3200`.
Those measurements were not replaced to improve results. Their collector labels
do not establish the cause of runtime failures.

Figure ranges copy saved error ranges; they are **not confidence intervals**.
`U` denotes unknown external outcomes, separately from unavailable forecasts.
The direct baseline receives the same declared semantics and has the documented
arithmetic equivalence. Neither useful-result superiority nor lower complete
effort is established by this snapshot. Conditional assumptions about
nonintervened dependencies and manually supplied operation meanings remain
explicit in the source records.

The report's `Status` column is the frozen source-evaluation status. Some older
failed or cancelled attempts therefore still say `running` in their saved
evaluation. Report-time Actions statuses are retained separately in provenance
and cost records; neither table is a current live inventory. The unresolved
duplicate incomplete DeepFlow/Petclinic/absent/6 placeholders have no selected
artifact and do not enter the 54 complete cells.

## Costs and reporting limits

Costs are a snapshot, not the final total. Parent waits overlap worker execution;
job-seconds are not elapsed study time. Human effort, undeclared work, active-job
tails, this report's remaining execution and later dispatch/publication costs
are not zero. The later 18 DeepFlow cells and eight main-source archival runs
are outside this report's declarations and remain in the ongoing cost ledger.

In particular, `runs_with_unknown_job_elapsed: 0` counts missing aggregate
completed-job totals; it does **not** mean that every job duration was known.
The retained row for live run `41023324471` has
`jobs_with_unknown_elapsed: 1`, a null active campaign-job duration, and only
the three completed preparation seconds. The immutable generated values are
preserved with this clarification.

## Full evidence and reproduction

The [permanent full report archive](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/download/data-41048730378/41044061764-artifact-12972574868-report-v5-41044061764.zip)
contains the referenced `evaluation-payloads/`, all figure formats and the
remaining provenance. Download and extract it when resolving payload references
or reproducing the report from saved evaluations. The selected repository copy
does not include the 115 source-evaluation gzip payloads or SVG/PDF counterparts;
the aggregate alone is not the complete evidence. Original campaign captures
are identified by their own artifact references.

The report artifact is ID `12972574868`, 534,512,742 bytes. Its Actions API
SHA-256 and the permanent Release asset SHA-256 both equal:

```text
deb8bd394b3f7db4ded43c5abcab361be4154605df3925e60d62d6a504359b19
```

[Archive verification](provenance/report-archive-review.json),
[release metadata](provenance/report-release-api.json),
[checksums](provenance/report-archive-SHA256SUMS.txt), and
[archive provenance](provenance/report-archive-provenance.tar.gz) record that
identity. Both job and workflow logs were preserved.

Local inspection selected 29 original members totaling 9,437,801 bytes and
verified their CRCs and SHA-256 hashes. The [selection proof](provenance/local-selected-inspection.json)
explicitly records `whole_zip_hash_verified: false`: neither the full report ZIP,
large input captures, nor raw journals were downloaded locally. The complete
source archive was verified in Actions. The [publication review](provenance/independent-publication-review.json)
binds the selected report fields to the 54 independently reviewed cells and
documents these verification limits.

The earlier [14-cell snapshot](../snapshot-40964268895/SOURCE.md) is preserved
unchanged as historical evidence, including its superseded four-collector scope.
The current authorized study has three collectors; New Relic is excluded.
