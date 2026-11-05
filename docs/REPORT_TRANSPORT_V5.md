# Saved report transport and verification

The first completed iteration-5 DeathStarBench/absent seed-7 compact artifact
contains a 14,074,465,721-byte attempt journal. The journal remains intact in the
original compact and full campaign artifacts. It is not needed as a separately
unpacked file when copying the saved evaluation into the report.

The report job now downloads one compact archive at a time, verifies its whole
SHA-256 and size against Actions metadata, and streams every member through CRC
and SHA-256 checks. Manifest claims must match. It extracts the other members and
retains exact verification evidence for the journal. Only the verified temporary
ZIP is then removed; the original Actions artifacts are unchanged. The reporter
describes the skipped file as retained Actions stream-verification evidence,
not as a locally reopened journal or a retained working ZIP. Missing sources
remain unavailable and wrong bytes fail validation. Earlier retained-ZIP reports
remain supported.

[Validation run `40962839097`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40962839097)
passed independent actual-output review at `51c9697ed71bfb98919936c95440e0a21ed6731b`.
It used the exact [source compact `12933554459`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40942429097/artifacts/12933554459)
and compared the original extraction/reporting implementation with the new path.
All 23 member proofs, the restored 74,735,705-byte source evaluation, rendered
tables and the nonempty selected main-cell identity agree. The
[validation artifact `12936228315`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40962839097/artifacts/12936228315)
retains both reports, their payloads and manifests, API metadata and verification
costs. Whole compact-ZIP and journal checks ran in Actions; they were not repeated
locally after removal of the temporary ZIP.

The first validation attempt, [run `40961608465`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40961608465),
built both reports but failed in its comparison code because it used the wrong
schema field name. Its failure and costs remain part of the record. A regression
now constructs and compares actual report outputs.

This changes transport and storage, not discovery, simulations, outcomes or
selection criteria. The [technical replacement manifest](iteration5-main-selection.json)
retains the original failed run and explicitly identifies its complete repeat;
it does not assert independent scientific admission. A generated report's
technical coverage and independently reviewed coverage are reported separately.
No scientific utility, speed or complete-cost advantage follows from this check.


## Current report disk checks

The report job uses the already qualified cleanup of unused hosted SDKs and
images while protecting Python, gh, git, node and the checkout. Before each
compact or required full-archive download it checks the actual filesystem free
space against the API byte count plus a 2 GiB output reserve. Before compact
extraction it checks every materialized nonjournal ZIP member, including members
outside the manifest. Before declared-file recovery it checks the exact requested
member sizes. These checks run before member bodies are read or written.

Full archives used for recovery remain on disk for the unchanged downstream
size/SHA verification. They are included in capacity planning. Only verified
compact working ZIPs are removed through the existing transport proof. Before
aggregation, a further check reserves every raw source-evaluation byte before
deterministic gzip retention, plus 2 GiB for aggregate, tables, figures and small
provenance. The raw byte count is a conservative budget for the gzip copies. The checks
preserve the source bytes and every eligibility predicate; insufficient capacity
is a technical stop before the corresponding write.

The current 249 compact ZIP directories cover every available compact across
all 119 declared study attempts. Their aggregate transfer size is
77,239,065,376 bytes, not the simultaneous disk requirement. Sequential verified
ZIP disposal and journal stream verification retain 28,221,017,375 bytes of
materialized nonjournal inputs. The conservative raw source-evaluation copy
budget is 13,118,903,052 bytes; retained copies use deterministic gzip.

Including the largest temporary compact ZIP (2,612,473,883 bytes) and the 2 GiB
output reserve gives a conservative bound of **46,099,877,958 bytes**. Existing
247 API identities and prior hash-bound header/nullability proofs are unchanged.
The final two compact directories and their small provenance manifests have all
non-null publisher claims present. Required full recovery is therefore zero
for these exact 249 compacts; this is not an assumption about missing future
data. Actual runner free space remains subject to the qualified runtime guards.
No source evaluation, raw, SQL, model, journal or whole scientific ZIP body was
read locally to calculate this bound.

The [current 81-cell technical selection](clean-study-final-technical-selection-20261105.json)
includes every candidate run/artifact identity across all current attempts.
The earlier79 selections are unchanged. The final two selections are verified
processing of the same original captures, not repetitions selected by forecast
availability, accuracy or external outcomes. The reporter still requires
exactly one eligible candidate per cell; scientific interpretation is recorded
separately in the [matrix closure](clean-study-original-matrix81-scientific-closure-20261105.json).
The report copies saved evaluations and renders their values. It does not invoke
Bering, Sheaft, new application traffic, model fitting or outcome remeasurement.
