# Closed final DeepFlow snapshots

The original study remains the full 81-cell, three-collector experiment: actual
collector observations feed Bering and Sheaft, evaluated against independent
application outcomes when SDK tracing is absent or partial. This repair changes
final data retention. It supplies no new scientific result or cheaper-method claim.

## Actual failure and recovery boundary

DeepFlow / OTel Demo / partial / seed 6, parent `41273434210`, failed at final
snapshot creation on guest a. The original helper attempted a second complete
copy of the standalone files inside the same 24 GiB guest filesystem and raised
`OSError: [Errno 28] No space left on device` in `_copy.output.write`.
This is distinct from the uploaded parent-checkpoint copy addressed by source
`8fa2a454db58af487451c9aead6477adc0ca0485`.

Original full artifact `13077373480` and compact artifact `13077297595` preserve
the failure, forecasts and recorded operations, including actual target outcomes.
Both reviews found no retained final raw stage or drain evidence; the original
compact manifest explicitly records missing freeze-integrity and evidence files.
The saved prefix and worker output cannot reconstruct the lost final guest
suffix. This attempt remains incomplete, with all data and costs retained.

## Exact source and actual storage proof

The separately named source is `6eaa441c40253a18f18af76e4e599496927c1739`.
Its full Git profile relative to the common anchor has 21 changed or added paths,
7 additions, 6 changed core files, and 2,115 unchanged entries. Only this exact
revision is accepted; future merges or branch heads receive no automatic allowance.
The inherited input-preparation and parent-copy-release proofs keep their own
tested-source identities.

Final snapshots use exclusive same-filesystem hardlinks only after positive
per-node termination evidence. Every full file is hashed; both original and
snapshot paths remain. Prefix and failure captures retain physical copying.
Existing codec, prefix, native-receiver, frozen-model and completeness checks
remain in force. Snapshot modes follow the original files (0644 in the fixture),
rather than the old copy mode 0600; this is not a claim of identical permissions.

Actual qualification run `41296733012`, artifact `13079348283`, archive digest
`sha256:5c90398d86e0a842bfcb0d6fc63152ff7f3a51d1cc487f89a5c7d375d4eda2e4`,
used the real retained prefix `13073478195`. It verified the complete original
archive and payload remotely. Each method started from an identical filesystem
image, source path, source bytes, free space, inode count and root UID.

| Node | Retained source bytes | Initial free bytes | Original copy with limited space | Closed final links |
| --- | ---: | ---: | --- | --- |
| a | 1,170,778,914 | 154,935,296 | ENOSPC | All bytes preserved |
| b | 117,539,976 | 53,190,656 | ENOSPC | All bytes preserved |

The original copy succeeded with an external roomy destination. Its original
snapshot manifest was byte-identical to the linked snapshot on each node.
All full source and target hashes agreed, including with the original saved
prefix manifests. Final directory and manifest allocation consumed 8,192 bytes
per node. Qualification took 162.763 seconds including download, validation and
cleanup, excluding the separately recorded hosted-image SDK cleanup.

These are closed replays of retained live prefixes, including a growing original
source on node a. They do not establish historical producer closure, reconstruct
the lost final suffix, prove sufficient capacity before final capture, or prove
zero internal buffer loss or whole-case completion. The first qualification
`41295902428` failed while allocating an unnecessary synthetic filler file before
either comparison; the corrected fixture uses only a bounded filesystem. Both
qualification attempts, both CI revisions and all original failures remain costs.

No fresh case is complete merely because this source or storage proof is accepted.
