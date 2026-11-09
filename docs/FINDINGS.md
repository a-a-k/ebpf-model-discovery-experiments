# Operation models from eBPF observations

The completed study supports conditional use of eBPF observations when SDK
traces are absent or incomplete. OBI supplies useful operation models for
Petclinic and for OTel Demo with absent SDK traces. OTel with partial tracing
requires a different combination of the available observations. The tested
pipelines do not supply the missing Social Network models.

For Social Network `compose_post`, the measured outcome is an HTTP ACK. Its
historical unconditional MongoDB-write requirement is incorrect for that event.
The [semantic correction](../results/semantic-correction.json) applies to the
interpretation below; no corrected prospective forecast or durable-write claim
has been validated.

The evidence covers all 108 declared cases: three applications, three SDK
coverage modes, four runtime treatments and three repetitions. All ten declared
operations remain in the results. The 2,880 source/view rows reuse 360
case-operation outcome sets, containing 1,036,800 primary requests with no
unknown or invalid outcomes. Rows and operations are not additional independent
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

## External forecast agreement

All 1,146 available source/view point predictions equal the equally informed
direct conditional calculation. That reference uses the declared operation
contracts and controlled two-slot inventory, without fitting HTTP outcomes or
requiring a recovered graph. The study demonstrates conditional applicability
of observation-derived models, without establishing a forecasting advantage
over that calculation. Classification results also remain equivalent to the
cheap base-family assignment.

There are 192 case-operation outcome sets with at least one available forecast.
Fifteen disagree with their point forecast, accounting for 84 repeated source/view
rows. Across all 360 outcome sets, 17 differ from the common direct reference;
two of these have no available observation-derived forecast. All are retained.
The largest discrepancies are:

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

The other eight deviations range from 0.03125 to 0.21875 percentage points.
Most excess failures in the larger discrepancies occur in state `10`, where
the conditional forecast predicts success. Their cause is unresolved. They
cannot be attributed to a collector from these outcomes alone. Checkout's old
20 MiB container limit was corrected uniformly before this study; that previous
diagnosis is not evidence for the cause of these failures.

## Database and asynchronous limits

Every raw-view database-down prediction is unknown. The network view contains
225 finite DB predictions, matching the direct reference and observed DB-down
outcomes. This is selective conditional evidence, not complete reconstruction
of database dependencies. All OTel DB predictions remain unknown.

Social Network compose acknowledges all 252 DB-down requests across its 36 cases.
The historical direct database-down prediction of zero used an incorrect
unconditional MongoDB-write requirement for this measured HTTP ACK. The pinned
Lua client decodes but ignores a declared `ComposePost` service exception; the
HTTP handler can return its success marker after that reply. This establishes
a contract/oracle mismatch, not that every one of the 252 requests took that
execution branch. The ACK measurements remain valid; they do not establish a
successful MongoDB write, durability, or a failed fault injection.

This DB error does not establish a change in the primary model-availability
counts. Missing DB channels can be assumed satisfied in the primary replica-only
forecast; missing interservice Thrift paths remain separate obstacles. The
published counts still describe the historical contract and pinned pipelines.
The full ACK contract, including its different exception paths, needs review
before corrected model claims are made.

The [semantic correction](../results/semantic-correction.json) preserves the
original measurements and frozen predictions. Corrected forecasts have not been
computed or independently validated. Applying a corrected contract to the known
targets would be post-hoc analysis; a new prospective claim requires corrected
forecasts frozen before fresh independent targets. The same outcome definition
must apply to every compared method.

All 36 OTel cases retain 20 records in each asynchronous phase: persisted in
normal execution, pending while paused, and persisted after resumption and
recovery. These measurements do not establish reconstructed asynchronous
causality or a model-based delivery forecast.

## Data, provenance and costs

The [complete generated JSON](../results/literal-results.json) retains scientific
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
