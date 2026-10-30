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
GitHub returned404 for the new draft's tag lookup. Its empty draft and failed
job remain evidence. The repair captures the structured release ID at creation
and uses release/asset IDs for draft access, upload, verification and publication.
The fake service now rejects draft-by-tag access. No source working copy was
deleted in that failed qualification. Linux tests passed13 cases before this
API correction; the corrected code needs renewed CI and real qualification.
