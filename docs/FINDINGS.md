# Operation-model evidence: 80 completed cells of the 108-cell study

These findings cover all 36 Petclinic cells, all 36 DeathStarBench Social Network
cells and eight OTel Demo cells (SDK absent, repetitions 9 and 11). The other
28 OTel cells are required for the complete study and are excluded from these
interim conclusions. Four completed cells are physically paired; 76 use the
registered allocation across separate workers.

The question is whether observations support executable operation models and
prospective forecasts checked against independent application outcomes when
SDK tracing is absent or incomplete. Superiority to an equally informed direct
calculation is a separate claim.

## Primary operation forecasts

| Application and observed scope | OBI eBPF input | Coroot eBPF input | DeepFlow eBPF input | SDK comparison |
| --- | --- | --- | --- | --- |
| Petclinic: all modes and three repetitions | 4/4 operation models in every cell | 0/4 | 0/4 | Absent: 0/4; partial: 2/4; full: 4/4 |
| Social Network: all modes and three repetitions | 0/3 | 0/3 | 0/3 | Absent: 0/3; partial: 1/3; full: 3/3 |
| OTel Demo: absent SDK, repetitions 9 and 11 only | 3/3 in both cells | 0/3 | 0/3 | Absent: 0/3 |

The denominators count the declared operations, not independent repetitions.
Each available forecast uses a retained Bering graph and an executed Sheaft
calculation. All ten operations, unavailable forecasts and adverse outcomes
remain in the evaluation.

Petclinic supplies a positive result for the tested OBI pipeline: eBPF observations
support all four operation models when SDK tracing is absent and restore the
two missing partial-SDK operations, `owner_details_with_visits` and `create_visit`.
Their forecasts match the independently measured primary outcomes in all three
repetitions. Partial SDK tracing alone supports `list_owners` and `list_vets`.
The other two tested eBPF pipelines do not restore those missing forecasts.

In Social Network, partial SDK input supports only `read_home_timeline`; neither
eBPF input nor its combination with SDK input restores `compose_post` or
`read_user_timeline`. Required operation-level call paths remain missing or
ambiguous. Identifying a service or its Redis/MongoDB connections does not close
the required chain of cross-service Thrift calls. Full SDK input supports all
three operations, including in the real no-agent control. This finding concerns
the pinned collection and conversion pipeline; it does not establish that Thrift
cannot be decoded or that every configuration of these collectors has this limit.

The completed OTel cells show model availability with OBI and imperfect outcome
forecasts. Each of the three forecasts is 0.875. In repetition 9, measured success
is 2702/3200 for browse, 2701/3200 for cart and 2665/3200 for checkout: absolute
errors of 3.0625, 3.09375 and 4.21875 percentage points. Additional failures are
concentrated in intervention state `10`; their cause is unresolved. In repetition
11, browse has one additional failure (2799/3200); cart and checkout are exactly
2800/3200. These outcomes do not establish that OBI caused the additional failures.

Two further deviations are retained where the eBPF forecast is unavailable:
Coroot/OTel/absent/9 browse and DeepFlow/Social Network/absent/11 compose each
record 2799/3200, versus the direct reference of 0.875.

## Interpretation and limits

Predictions in all 900 available source/view rows equal the equally informed
direct reference.
Combined input and the cheap observed-context union have identical saved primary
availability, primary predictions and DB predictions. Thus the evidence supports
conditional applicability of the observation-to-model pipeline, without showing
an advantage over these calculations. The 2,208 source/view rows reuse 276
case-operation outcome sets and are not independent experimental samples.

Every raw-view DB forecast remains unknown. The network view contains 225
non-null DB predictions, all equal to the direct DB reference; this does not
demonstrate complete recovery of causal DB dependencies. Social Network compose
acknowledges all seven DB-down requests despite a direct prediction of zero;
an HTTP acknowledgement does not establish durable storage or the cause of the
discrepancy. OTel persistence snapshots retain normal, paused, resumed and
recovered observations, without proving reconstructed asynchronous causality or
a model-based delivery forecast. Classification agreement with the supplied base
families is not evidence of an external benefit.

The cost inventory is provisional. Preparation, failed processing, retries,
transfers, review and publication remain in scope; active tails and unmeasured
human work are unknown. No complete cost comparison is available.

The literal report was produced by [Actions run 42466364290](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/42466364290)
from 77 original result publications. It preserves all scientific fields except
the two declared classification-assignment arrays. The derived JSON has SHA256
`e98244747417bfd89f9553eb8a9f1fe08b9dd6278952cb5ed73c8f7e6603c56d`.
