# Exact source U: verified uploaded checkpoint copy release

U is the tested commit `8fa2a454db58af487451c9aead6477adc0ca0485`, pinned by
`capture-20261101-uploaded-checkpoint-release-v5`. It is not an implicit allowance
for a later merge commit. Its production series and worker workflow files are
byte-identical to T (`06d7d52`). The parent adds one cleanup helper and its cost
record after the last checkpoint/index reads and before worker dispatch.

The actual T full6 parent 41261041075/job 124714202937 exhausted its runner disk
at 05:26:55 UTC on 2026-11-01. The exact consuming file/subphase is unknown;
the GitHub runner's ENOSPC annotation is conclusive about storage exhaustion.
An unchanged T repetition is not the storage repair.

T partial6, run 41259904200/job 124710864475, independently exposes the packaging
peak. Continuation and evaluation succeeded, but packaging the complete toolchain
failed with `OSError(28, 'No space left on device')`: observed free space fell
from 133,922,816 bytes to zero. The console records 1,072 files and
2,033,982,202 uncompressed bytes in the attempted subtree, without deleting or
trimming its source. The compact artifact 13073185961 retains the actual target
outcomes; the original full artifact was never uploaded. Its unchanged full-source
admission gate therefore remains unsatisfied. A fresh full case recovers this
technical retention failure; the original outcomes and all costs remain visible.
T partial7, run 41259915749/job 124710889139, also terminated with the runner's
ENOSPC annotation, this time during environment/status retention. These old
running jobs did not receive the later U code.

The saved-prefix qualification 41278513379 at the exact U commit completed
successfully. Artifact 13072487567 has digest
`sha256:f7323f6195125699453ca2ba86d8ba3126aeefc469eef0ad5434a3847ea9a6f0`.
It used the original T full6 checkpoint, with full archive/hash/member checks
and a separate physical live mirror. All 25,180 mirror file hashes/lengths and
the original manifest/ready/release-control hashes remained equal. The added
release control is explicitly synthetic because the saved archive predates it.
No VM, application traffic, Bering, Sheaft, model refitting or rescoring ran.

Exactly 21,031,649,232 logical payload bytes were unlinked from the redundant
local copy. Free space increased by 21,094,756,352 bytes on the qualification
host; that observation also includes concurrent host activity. Cleanup took
71.20 seconds, including verification. The full qualification took 391.19
seconds. These are not a full-case resource bound or proof of six-hour closure.

U changes exactly 16 Git paths relative to A, including six additions; the
remaining 2,119 original entries retain exact modes and object identities.
There are four changed core files relative to A, inheriting T's preparation
changes. Only one core file changes relative to T. The complete source profile
checks all reviewed blobs and the remaining tree; it does not label U as an
operational-only revision of A.

The T input proof remains attributed to its own tested source `7df056a`:
655 inputs, 647 byte-exact files and 18 exported entry hashes. U's actual copy
release proof is separate. The report checker, all four saved-reader source
sets, and the fresh-review selector admit only the exact reviewed U commit.
Default 34,800/9,600 counts, 100,000 simulation trials, all 81 cases, source pins,
pre-target freezing, model/report checks, duplicate selection and external
review boundaries are unchanged. Unknown/adverse outcomes and every failed,
preparation, qualification, recovery, review, transfer and retention cost remain.

Producer CI 41278220942 and actual output checks have passed. The exact consumer
`23dc6d2b80b8bf79522ad7d79a73b709844f8ce3` passed CI 41280276240.
Source/tag/capacity verification and a separate ORIGINAL exact-case execution
decision remain required before each new main replacement. The
[first two dispatches](clean-study-U-two-actual-failures-dispatch-20261101.json)
and [four additional dispatches](clean-study-U-four-additional-failures-dispatch-20261101.json)
retain their actual sources and requests. A subsequent
[OTel absent8 replacement](clean-study-U-OTel-absent8-dispatch-20261101.json)
follows S job 124705195734's actual six-hour stop at 06:48:44 UTC. That old case
retains only its pre-target prefix. Its bounded console request returned an
unavailable storage object; the precise continuation subphase remains unknown,
and disk exhaustion is not established for that stop. Full-case and final-study
success are not asserted here.
