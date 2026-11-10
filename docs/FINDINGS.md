# Operation models from eBPF observations

The completed study supports conditional use of eBPF observations when SDK
traces are absent or incomplete. OBI supplies useful operation models for
Petclinic and for OTel Demo with absent SDK traces. OTel with partial tracing
requires a different combination of the available observations. The tested
pipelines do not supply the missing Social Network models.

For Social Network `compose_post`, the measured outcome is an HTTP ACK. Its
historical unconditional MongoDB-write requirement is incorrect for that event.
The [semantic correction](../results/semantic-correction.json) and
[prospective results](../results/correction-publication.json) apply to the
interpretation below. Corrected ACK and warm-fixture timeline contracts were
frozen before 36 fresh independent Social Network checks. The eBPF operation
coverage remains 0/3 for every tested collector, SDK mode and repetition.
Successful ACKs still do not establish MongoDB storage or durability.

The evidence covers all 108 declared cells: three applications, three SDK
coverage modes, four runtime treatments and three repetitions. All ten declared
operations remain. Petclinic and OTel retain their 72 original cases; the
corrected Social Network analysis uses 36 fresh checks against the same observed
graphs. The 2,880 source/view rows reuse 360 case-operation outcome sets and
1,036,800 primary requests: 942,168 successes, 94,632 failures and no unknown or
invalid outcomes. Rows and operations are not additional independent
repetitions. Eight cases use physically paired allocation; 100 use separate
workers. Models are frozen before independent validation deployments start.

The no-agent treatment is a real deployment without a study eBPF collector.
SDK libraries may remain installed when their providers, samplers or exporters
are disabled. OBI uses active context propagation. These results therefore
describe the pinned configurations and observation-to-model pipelines; they
do not establish the capabilities of passive kernel observation alone.

## Operation coverage

Counts below are available operation forecasts per case, identical in all three
repetitions. Primary availability is the same in the raw and network_scope
views. A count establishes model availability; outcome agreement is assessed
separately below. Native control means SDK observations from the real no-agent
treatment. The last two columns use the OBI treatment.

| Application | SDK coverage | Native control | OBI eBPF | Coroot eBPF | DeepFlow eBPF | Combined | Context union |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Petclinic | absent | 0/4 | 4/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| Petclinic | partial | 2/4 | 4/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| Petclinic | full | 4/4 | 4/4 | 0/4 | 0/4 | 4/4 | 4/4 |
| Social Network | absent | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| Social Network | partial | 1/3 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 |
| Social Network | full | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 |
| OTel Demo | absent | 0/3 | 3/3 | 0/3 | 0/3 | 3/3 | 3/3 |
| OTel Demo | partial | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 |
| OTel Demo | full | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 |

Petclinic provides a positive result for the tested OBI pipeline. Without SDK
traces it supports all four operations. With partial tracing it restores
`owner_details_with_visits` and `create_visit`, while native input supports
`list_owners` and `list_vets`. The available forecasts match the independently
measured primary outcomes in all three repetitions.

For OTel with absent SDK traces, OBI supports `browse_product`, `add_to_cart` and
`checkout`. With partial tracing, native input, eBPF input and the ordinary
combined pipeline each support none of the three. The cheap union of observed
context supports all three in every repetition, giving 18 differing source/view
rows over nine case-operation outcome sets. Its predictions match eight of those
nine sets exactly; partial/9 checkout records 2799/3200 against 2800/3200 predicted.
Thus the available observations support conditional forecasts through the cheap
combination even where ordinary model construction fails. This does not prove
recovery of per-request causal paths.

The OTel partial combined graphs retain missing or ambiguous catalog
`GetProduct` obligations, including frontend/catalog and checkout/catalog calls.
These are failures to establish the required graph evidence, rather than proof
that no relevant service observations were collected. With full tracing and OBI
running, native input supports only browse and cart: checkout retains unresolved
shipping quote and ship obligations. Combined input restores checkout. The clean
no-agent full-SDK control supports all three operations. Adding SDK or agent
observations therefore does not monotonically improve each source projection.
The experiment does not isolate the runtime or conversion mechanism causing
these differences.

Social Network remains unsupported by all three eBPF-only inputs. Partial native
input supports `read_home_timeline`; its combination with eBPF does not restore
`compose_post` or `read_user_timeline`. Required operation-level caller/callee
chains through Thrift services remain missing or ambiguous. Seeing a service,
Redis or MongoDB connection does not establish those chains. Full SDK input
supports all three operations, including in the no-agent control. No specialized
Thrift decoder was tested; the result is a limit of these pinned pipelines,
not a general impossibility result for Thrift or these products.

The corrected prospective analysis confirms this coverage in all 36 cases.
Native, combined and context inputs each support zero operations without SDK,
only `read_home_timeline` with partial SDK, and all three operations with full
SDK. Correcting the outcome contract does not supply the missing observed
Thrift caller/callee evidence.

## External forecast agreement

All 1,146 available source/view point predictions equal the equally informed
direct conditional calculation. That reference uses the declared operation
contracts and controlled two-slot inventory, without fitting HTTP outcomes or
requiring a recovered graph. The study demonstrates conditional applicability
of observation-derived models, without establishing a forecasting advantage
over that calculation. Classification results also remain equivalent to the
cheap base-family assignment.

There are 192 case-operation sets with at least one available forecast.
Eighteen differ from that forecast, producing 102 repeated source/view error
rows. The direct reference differs in 21 of the 360 sets; three of those have
no available observation-derived forecast. All are retained. These totals use
the 72 unchanged Petclinic/OTel cases and the 36 corrected Social Network checks.

The unchanged Petclinic/OTel evidence retains its deviations from the conditional
forecast, including the larger OTel discrepancies below. They are not removed
or attributed to a collector from outcome agreement alone.

| OTel case | Operation | Observed successes / requests | Point prediction | Absolute error, percentage points |
| --- | --- | --- | --- | --- |
| absent/9, OBI | browse | 2702/3200 | 0.875 | 3.0625 |
| absent/9, OBI | cart | 2701/3200 | 0.875 | 3.09375 |
| absent/9, OBI | checkout | 2665/3200 | 0.875 | 4.21875 |
| full/10, Coroot | browse | 2717/3200 | 0.875 | 2.59375 |
| full/10, Coroot | cart | 2727/3200 | 0.875 | 2.28125 |
| full/10, Coroot | checkout | 2622/3200 | 0.875 | 5.5625 |
| full/10, DeepFlow | browse | 2715/3200 | 0.875 | 2.65625 |
| full/10, DeepFlow | cart | 2727/3200 | 0.875 | 2.28125 |
| full/10, DeepFlow | checkout | 2621/3200 | 0.875 | 5.59375 |

The other original deviations range from 0.03125 to 0.21875 percentage points.
Most excess failures in the larger discrepancies occur in state `10`, where
the conditional forecast predicts success. Their cause is unresolved. They
cannot be attributed to a collector from these outcomes alone. Checkout's old
20 MiB container limit was corrected uniformly before this study; that previous
diagnosis is not evidence for the cause of these failures.

The corrected Social Network checks contain 345,600 primary requests with no
unknown or invalid outcomes. Compose records 100,794/115,200 successes; home
records 115,200/115,200; user records 100,800/115,200. All 288 available primary
source/view forecasts equal the direct conditional calculation.

Five Compose case-operation sets differ from the direct prediction of
2800/3200 successes: full/9 NONE, full/11 Coroot, full/11 DeepFlow and partial/11
NONE record 2799; partial/9 NONE records 2798. The largest error is 0.0625
percentage points. Only the three full-SDK cases have available graph forecasts,
producing 18 repeated source/view error rows. All six excess failures remain in
the results. These small deviations do not establish a collector effect.

## Database and asynchronous limits

Every raw-view database-down prediction is unknown. The network view contains
225 finite DB predictions, matching the direct reference and observed DB-down
outcomes. This is selective conditional evidence, not complete reconstruction
of database dependencies. All OTel DB predictions remain unknown.

Social Network compose acknowledges all 252 fresh DB-down requests across its
36 corrected cases. The direct conditional prediction is one, under the
registered declared-exception mask and fulfilled-prefix conditions. Across all
three operations it agrees with 720/720 DB-down outcomes. The graph-based DB-down
forecasts remain unavailable in all 864 source/view rows; the direct calculation
does not require a recovered graph or selected-endpoint attribution.

The historical direct database-down prediction of zero used an incorrect
unconditional MongoDB-write requirement for this measured HTTP ACK. The pinned
Lua client decodes but ignores a declared `ComposePost` service exception; the
HTTP handler can return its success marker after that reply. This establishes
a contract/oracle mismatch, not that every one of the 252 requests took that
execution branch. The ACK measurements remain valid; they do not establish a
successful MongoDB write, durability, or a failed fault injection.

Missing DB channels can be assumed satisfied in the primary replica-only
forecast; missing interservice Thrift paths remain separate obstacles. The
corrected prospective results establish that the operation-availability counts
remain unchanged for these pinned pipelines.

The [semantic correction](../results/semantic-correction.json) preserves the
original measurements and frozen predictions. Corrected contracts were applied
equally to native, eBPF, combined, context and direct methods. All nine blocks
were frozen before the fresh targets. ReadUserTimeline's DB-down reference
uses the preserved warm Redis fixture and fulfilled PostStorage; MongoDB can
still be attempted on this path. The source conditions and all misses remain
explicit in the [contract description](COMPOSE_OUTCOME_CORRECTION.md).

All 36 OTel cases retain 20 records in each asynchronous phase: persisted in
normal execution, pending while paused, and persisted after resumption and
recovery. These measurements do not establish reconstructed asynchronous
causality or a model-based delivery forecast.

## Data, provenance and costs

The [original generated JSON](../results/literal-results.json) retains scientific
fields, unavailable values and adverse outcomes. Only the two declared
classification-assignment arrays are omitted. It was produced by
[Actions run 42520421400](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/42520421400)
from 102 original publications, with whole-ZIP SHA256 and every member's EOF/CRC
checked in Actions. The JSON SHA256 is
`1153f70032bc36bbc1936e666c8338e0935c24d2c8553b64836e711c9005bf36`.

The [result manifest](v6-full108-completed-result-manifest.json) preserves actual
sources, publishers, attempts and the Coroot partial/10 publication retry. Its
first attempt remains historical evidence and is not an extra repetition.
The [cost ledger](v6-full108-completed-cost-ledger.json) retains the declared
pre-reader cut: 167 workflows, 873 job rows, 40 exact API aliases, 1,339,757 known
unique worker-seconds and 60 unknown intervals, including failed and cancelled
work. Nested telemetry is not added to those intervals again.

[Provenance and closing costs](../results/provenance.json) retain source checks,
the failed first report and its corrected repeat: eight additional worker
intervals totaling 1,649 seconds. Later delivery CI is outside that finite cut;
human and unmetered work remain unknown. These are worker intervals, not CPU,
billing or sequential elapsed time. No complete cost-superiority comparison
is claimed.

The [publication archive](../results/archive.json) retains the 102 canonical
metadata ZIPs, the historical Coroot prefix, required source and historical API
receipts. It supports report replay without live Actions API access. This tier
does not preserve the complete raw-capture/model-build regeneration closure;
replay agreement alone does not validate the corrected compose contract.

The [correction publication](../results/correction-publication.json) links all
36 raw-backed target receipts, full archives or lossless parts, the original
forecast barrier, and 85 permanent metadata ZIPs. Full classification arrays
remain in the raw captures; result projections omit only their two declared
assignment arrays. The first correction attempt completed measurements but lost
raw publication. Its 36 aggregates and all worker costs remain historical
evidence, not extra raw-backed repetitions. All 36 replacement cases were
selected before inspecting forecast accuracy; that series required no retries.

The incremental correction ledger records 262,974 known worker-seconds and one
unknown platform interval, including source checks, the failed raw-publication
attempt, replacement measurements and the failed metadata finalizer. The unknown
record is a skipped GitHub job whose end timestamp precedes its start. Its raw
timestamps remain retained. Nested phase telemetry is not added again. The
successful finalizer and later delivery remain outside the finite cost cut and
are not assigned zero cost. No complete cost-superiority comparison is claimed.
