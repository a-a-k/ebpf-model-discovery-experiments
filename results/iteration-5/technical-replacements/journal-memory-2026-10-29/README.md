# Technical replacement of three pre-target attempts

The [decision](decision-before-cancellation.json) was recorded at
2026-10-29 20:09:50 UTC, before cancellation requests. Both root and independent
skeptic approved replacement under the original criterion. Fresh Actions metadata
showed all three jobs still acquiring the training prefix, with no checkpoint
artifact or frozen validation forecast. The replacement rule used the known bulk
journal-body preparation implementation and the validated equivalent replacement;
it used no outcome, accuracy, or elapsed-duration threshold.

| Cancelled attempt | Mode / seed | Original head | Replacement at `86b5deb` |
|---|---|---|---|
| [40932031732](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40932031732) | full / 6 | `f5ac530` | [40947264867](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40947264867) |
| [40935194776](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40935194776) | partial / 6 | `950b35a` | [40947274375](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40947274375) |
| [40935203055](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40935203055) | partial / 7 | `950b35a` | [40947287495](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40947287495) |

All are OBI DeathStarBench main attempts. Cancellation requests were accepted at
20:10:01, 20:10:06 and 20:10:10 UTC. The respective campaign jobs completed as
cancelled at 20:12:33, 20:12:42 and 20:12:39 UTC; final API metadata is retained
under each run directory. The independent reviewer also retrieved whole run-log
ZIPs and retained their hashes and CRC checks in `retention-proof.json`; those
ZIPs are not duplicated here. Actions run links remain the external log source.

Cancelled attempts are technically incomplete and ineligible for empirical
admission. They are neither collector failures nor successful cheap runs. Every
abandoned attempt, preparation, repair, wait and replacement remains in the
Actions cost declarations. Completed valid old-head campaigns remain valid.
No result is replaced based on its error, no shutdown cause is asserted, and no
full-campaign memory or utility advantage follows from the saved-journal
equivalence [validation](../../../../docs/JOURNAL_MEMORY_V5.md).
