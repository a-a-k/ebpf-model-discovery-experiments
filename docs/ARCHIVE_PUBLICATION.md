# Bounded working storage for permanent evidence publication

The fresh matched series retains every main cell. Downloading all artifacts from
a 27-cell Actions run before uploading any of them can exceed the archive runner's
disk. This is a storage/publication repair; capture, modelling and evaluation at
immutable study-20261030 are unchanged.

With ARCHIVE_RELEASE_TAG set, archive-runs.sh uses a new draft release tied to
the archiving run ID and exact source head. It verifies each original artifact
against its API digest, applies the existing lossless chunker when necessary,
uploads one retained file, and checks remote metadata by its returned asset ID.
Remote state, size and SHA-256 must all match. The publication record and checksum
are appended before that working file is removed. No source artifact is deleted.

The final checksum list includes files already uploaded and removed locally.
Original source indexes, job/run metadata, log availability and chunk/reassembly
manifests remain in provenance.tar.gz. Final provenance/checksum uploads are also
checked remotely before the workflow publishes the release. Errors leave it a
draft, with compact publication proof retained in Actions. Existing assets are
never overwritten. The script without this optional mode keeps its original
standalone output contract.

This removes accumulation across artifacts, not every possible disk limit. The
existing chunker can transiently retain the largest ZIP and all its parts:
approximately twice the largest original ZIP, plus metadata and runner overhead.

Main and independent reviewer gave design and actual-code GO before execution.
Focused synthetic cases cover standalone compatibility, cleanup before a second
download, direct asset-ID lookup, chunk hashes, upload/digest/size/state errors,
bad original digests and refusal of an already published release. Bash syntax
and Python compilation pass locally; all 13 shell cases skip on Windows.
Linux CI and a real compact-artifact qualification are required before using
this mode to publish the full main series. Publication is not scientific success.

The first real qualification (41102985375) stopped before source download:
GitHub returned 404 for the new draft's tag lookup. Its empty draft and failed
job remain evidence. The repair captures the structured release ID at creation
and uses release/asset IDs for draft access, upload, verification and publication.
The fake service now rejects draft-by-tag access. No source working copy was
deleted in that failed qualification. Linux tests passed 13 cases before this
API correction; the corrected code needs renewed CI and real qualification.

Corrected exact-head Linux CI 41104872805 and 41104883471 passed. Real
qualification 41105413963 published data-41105413963 with nine verified assets.
The independent reviewer matched every remote ID, size and SHA-256 to the
publication proof, confirmed all three source ZIP digests against Actions, and
verified ledger/checksum/provenance agreement. Explicit GO was given for the
full-series archive after each source run becomes terminal. PR5 merged this
engineering repair; the scientific source remains immutable bf49d46.

After the route-binding regression was found, the bf49 parent series was
technically stopped. Publication41113544016 retained all then-available artifacts
from parents41099986985/41099992213/41099997831 and workers41108415418/41111105552.
The public data-41113544016 release has45 assets,17,728,580,180 bytes. The root
review matched all43 payload ledger records and two metadata assets to current
remote IDs, names, states, sizes and SHA256; checksum and provenance hashes agree.
Only the244KB publication proof was downloaded locally. This batch covers the
available packets, not unrecovered cancellation-tail data. Completed OBI worker
41112538790 is retained separately and remains due in the next archive batch.

Cancelled queued jobs can have nonzero API started/completed intervals even with
runner_id=0. The report retains those timestamps as recorded job elapsed; these
values do not establish CPU consumption or billed runner usage.

Subsequent preserved batches include failed preparation and early stopping:

| Archive run / public data tag | Original artifacts | Remote assets | Remote bytes | Verification |
|---|---:|---:|---:|---|
| [41129382005](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41129382005) | 100 | 151 | 2,214,906,734 | All149 payload ledger records and two metadata assets agree with remote IDs, states, sizes and SHA256. |
| [41143725458](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41143725458) | 124 | 306 | 2,263,705,192 | All304 payload ledger records and two metadata assets agree. Includes failed archive41142560426 evidence; that earlier HTTP504 draft is not described as complete. |
| [41152387177](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41152387177) | 114 | 272 | 2,194,445,670 | All270 payload ledger records and two metadata assets agree. Covers52 terminal runs, including all f60 qualification parents/workers and the completed catalog/metadata audits and preparation CI. |
| [41162733906](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41162733906) | 119 | 290 | 2,233,096,346 | All288 payload ledger records and two metadata assets agree. Covers53 terminal runs, including all final0c98 qualification parents/workers, diagnostic41152205197, canceled first saved-reader41162303053 and failed archive41162374422. |
| [41165335207](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41165335207) | 28 | 73 | 46,363,207 | All71 payload ledger records and two metadata assets agree. Covers27 qualification saved-facts packets in reader41162715350, preceding archive's own proof/logs and four pre-execution/main-declaration CI runs. |
| [41204936218](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41204936218) | 31 | 154 | 22,924,555,553 | All152 published payload ledger records and two metadata assets agree in ID, state, size and SHA256. Covers47 terminal runs, including26 DSB workers, the completed OBI/DSB/absent6 replacement and prior publication/preparation tails. |

The41152387177 batch's locally rehashed metadata assets are provenance.tar.gz
(130952 bytes, SHA256 `33b3d7d110fd189ac1a98a367e199dbc923140cc1d7407fbf71bdf20852388c3`)
and SHA256SUMS.txt (32785 bytes, SHA256
`c3b8aad78e459945aaa19153f2df5f950ee2e8275f13800b0ded0d25e7b2a418`).
Original ZIPs were verified by archival Actions; the local review checked API
digests, lossless-part manifests and every published payload record, without
downloading original campaign archives or journals. At that batch's cutoff,
paired diagnostic41152205197 and later preparation runs remained due; they are
included in41162733906.

The later batch locally rehashes only provenance.tar.gz (144966 bytes, SHA256
`cbb5518c81851697a7526daf39443d2c00045468e7f0a6b1b5de253b551712b5`)
and SHA256SUMS.txt (34915 bytes, SHA256
`e9bbdd51c03c3edca4ba049458e29b645b6722456ea7c6d2aae006aa565a9057`).
Every original artifact digest and published payload ID/state/size/digest matches.
The first attempt41162374422 stopped after three existing transport attempts
returned GitHub502 for run41154077137 job metadata; its draft is not complete.
After the endpoint returned valid metadata, the new release retained the same
49 terminal runs and four failure/CI tails. No existing release was overwritten.
Active saved-reader41162715350 and this publication's own tail require the next
terminal-run batch. Archive completeness does not establish research success.

Batch41165335207 closes that saved-reader and declaration tail. Only its two
small metadata assets were rehashed locally: provenance.tar.gz (33400 bytes,
SHA256 `4a55e986a6b50e3a75c8b1237a1a00479388c02c2119c89ba0dee98c01cef779`)
and SHA256SUMS.txt (8754 bytes, SHA256
`fe692bda5d742414478e2ebcf30e6fa241ffd2bd2218be4301d88c7c5a3c45bb`).
All28 original artifact identities and71 published payload ID/state/size/digest
records match the current release API. The active final81 main series, its
workers, final report/reviews and this publication's own tail remain due.

Batch41204936218 published at13:51:59UTC. Local review rehashed only
provenance.tar.gz (84472 bytes, SHA256
`0ae5d9ae01444b04f5d5388a8451cd536023188303a4d0d55909b0e05798ca2d`)
and SHA256SUMS.txt (17394 bytes, SHA256
`22270aa1eb3c3c0d093aa1edd5591bfc7ddc22c44c2183c8d6b855d2e3c388e6`).
All152 published payload records match both remote asset metadata and checksums;
the two additional checksum entries identify small chunk manifests inside the
provenance archive and their hashes also match. Original ZIPs were verified by
archival Actions. The three original main parents were still active at dispatch
and were excluded, as was the then-active full7 replacement. Their subsequent
outputs, the new parent-disk replacements and later review/report/publication
tails require future terminal-run batches. Publication does not establish
scientific admission or utility.
