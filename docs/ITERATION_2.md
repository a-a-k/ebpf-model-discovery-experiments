# Iteration 2: diagnose the completed experiment before changing its design

Status: completed and independently reviewed. The user requested this diagnostic iteration on
2026-10-27. The original 27 campaigns and published results remain unchanged.

## Criterion and interpretation

The original criterion remains useful operation-model discovery and prediction
from eBPF when application tracing is absent or incomplete, checked against
independent business outcomes and complete comparable costs. This iteration
investigates why that criterion was not established. Explaining a failure does
not establish the original criterion or authorize substituting an easier one.

The strongest simple calculation baseline remains direct conditional-state
estimation with the same observations, contracts, state weights and populations.
Its equivalence to model integration is already known. Full native traces remain
an observation reference. For database enrichment, an ordinary endpoint inventory
with the same operation contracts is an additional inexpensive baseline.

All analysis runs in GitHub Actions. Input is the fixed final report 40459487189
and the original archived captures for its 27 accepted campaigns. No new
application traffic is scheduled in this iteration. No campaign is selected or
excluded based on diagnostic improvement. Archived invalid attempts and their
costs remain part of the historical record, not new accepted observations.

## Explanations to distinguish

| Hypothesis | Diagnostic control | What it can establish |
| --- | --- | --- |
| H1: the HTTP proxy loses required business completion | Replace calibration proxy outcomes with independent calibration outcomes in an explicitly oracle-only control; audit whether missing completion evidence exists in source observations | Sensitivity to proxy semantics; feasibility of a later source-only repair |
| H2: faults censor the distinguishing operation signature | Replace inferred calibration classes with generator operation labels in an explicitly oracle-only control | Sensitivity to classification rather than source outcome coverage |
| H3: async identities are absent from export or lost in processing | Audit raw OBI/native identity fields, normalization preservation and matcher rejection reasons separately | The observed stage at which the tested pipeline lacks a supported link |
| H4: finite samples contribute materially to failed precision gates | Separate identification bounds, nominal Wilson padding and error against external outcomes | Uncertainty contribution, without claiming validated interval coverage or eliminating semantic bias |
| DB: extra graph nodes did not affect predictions | Inspect the actual predictor and existing shared-DB controls | This is an implementation fact: the original four-state predictor never uses the DB graph |

H1 and H2 form a two-by-two retrospective diagnostic: frozen original
classification/HTTP proxy; oracle classes/original proxy; frozen classification/
oracle calibration outcomes; and both oracles. The first cell must reproduce
saved forecasts. Other cells are not deployable discovery methods. In particular,
generator labels and external outcomes never enter a claimed source-only model.
Calibration/test separation is preserved, but the investigation was designed
after inspecting the first results: it is not fresh confirmatory evidence.

The source audit also checks strict entry binding and source-separated ancestry:
the original projection can select a header-bearing downstream server instead
of the declared entry, and its combined child index does not separate sources.
These are possible processing causes, not demonstrated limits of eBPF.
Petclinic exports can contain `http.response.body.content`; the protocol-only
audit inventories this availability rather than falsely declaring payloads
absent. It deliberately does not yet implement a payload-semantic binder.

The semantic substitution keeps original assignments fixed; it does not silently
reclassify attempts using their newly substituted outcomes. Unknown source
outcomes remain unknown in the class-only control. Missing classes retain the
original unsupported interval. The both-oracles control is a direct empirical
state-conditional diagnostic, not an eBPF result.

For H3, topic/time proximity, Kafka request correlation IDs and successful HTTP
responses cannot supply missing message identities. Native information is never
borrowed to complete eBPF chains. Raw events and link attributes omitted by the
normalizer are audited before attributing a failure to the collector. Association
to a SQL write attempt remains distinct from a committed, timely business effect.

For H4, there is no resampling to manufacture additional observations, no new
traffic to cross the precision threshold and no claim that Monte Carlo draws
increase empirical sample size. Reported Wilson intervals retain their nominal
iid assumptions and unvalidated temporal coverage.

## Minimum follow-up design to refine from the diagnostics

1. Keep the original operation contract and outcome target fixed across native,
   eBPF and combined observations. Any corrected completion binding must use
   observable evidence; absent evidence remains unknown.
2. Separate supplied operation identities from attempted automatic classification
   so that a classification failure cannot masquerade as an outcome-model failure.
   Both routes must disclose their manual knowledge and preparation costs.
3. Reuse Petclinic for the shared-database corner: Visits replicas on separate VMs
   share MySQL with Customers. Freeze impact predictions from healthy observations
   before separately disabling one replica and the shared DB. Supply the same
   contracts to each method; do not supply the missing DB binding as an oracle.
   Keep unreachable/unknown predictions explicit, and independently check actual
   operation effects. Existing common-cause support in the original model is not
   a new eBPF modelling capability.
4. Require a correct external prediction or narrower valid bound to change before
   describing DB enrichment as useful. A larger graph alone is insufficient. If
   endpoint inventory gives the same result at less effort, disclose that result.

New acquisition is a separate step after these diagnostics and a renewed skeptic
check of its concrete design. There is no automatic second 27-campaign sweep.

## Results and decisions

The [generated report](../results/iteration-2/report.md) contains all 27 campaigns,
all four diagnostic cells and all sources. The [summary CSV](../results/iteration-2/summary.csv)
retains each operation/mode separately over its three original seeds. Oracle
controls identify replacement effects in this estimator, not corrected eBPF models.

| Explanation | What the diagnostic established | Design consequence |
| --- | --- | --- |
| H1: proxy semantics | Petclinic full-mode owner-details point MAE is 12.50 pp with original data or oracle classes, and 0 with oracle calibration outcomes. Enabled native has the same semantic error. | Keep the original business contract. Bind mandatory calls and, where available, response-payload semantics; do not substitute HTTP 2xx for completion. |
| H2: classification | OTel absent/partial eBPF forecasts become identified with zero point MAE in the class-oracle control; outcome replacement alone does not help. Full-mode class-oracle point MAE is 0.52/1.04/2.08 pp for browse/cart/checkout. Petclinic create-visit class replacement also yields zero point MAE in all modes. | Separate supplied operation identity from automatic grouping. Fix strict entry selection and source-local ancestry before evaluating automatic discovery again. |
| H3: Kafka export | In all nine OTel captures, audited raw Kafka spans/attributes survive normalization, but eBPF has no accepted identity candidates. Enabled native has exact links. | The tested async failure is already present in exported identity evidence. Repeating the unchanged configuration is not an evidenced repair. |
| H4: nominal precision | Full-mode Petclinic owners/vets have zero point error and zero identification width, but 6.02 pp nominal worst-end error. Even both-oracle Petclinic controls retain 5.27–6.02 pp worst-end error. | Plan real observations per operation/state against the precision target before fresh acquisition. More MC draws cannot repair this design issue. |
| DB graph | The original predictor never uses DB nodes. Shared MySQL already exists and a static endpoint inventory can expose it. | A future shared-DB corner must change an external impact prediction, compare the inventory baseline, and explicitly use the dependency. |

The source-only Petclinic audit is narrower than the oracle outcome control. In
the three absent-mode captures, it identifies 24, 15 and 22 of the 30 target HTTP
proxy false positives respectively. With native tracing enabled, the eBPF audit
identifies none of those 30 per capture; the native audit identifies all 30.
No source-false verdict contradicts an externally successful operation. This
does not establish positive business completion or a repaired forecast. It
motivates checking ancestry/context interactions when both instrumentations run;
the mode contrast alone does not prove instrumentation interference.

Response bodies occur in exported Petclinic data. Their absence is not an
established explanation. The diagnostic inventories their availability without
implementing a payload binder. A source-only binder must validate field format,
completeness and attribution, use the same declared fixtures/contracts for all
sources, and keep SQL write attempts distinct from confirmed persistence.

DeathStarBench's eBPF results are unchanged by either oracle substitution. This is
a useful control against attributing every result to the same failure mechanism.

## Refined minimum design for the next implementation

1. **Source comparison first.** Use the same explicit operation identities and
   original completion contracts for native/eBPF/combined source comparison.
   Automatic classification is a separate paired arm. Supplied identities are
   manual knowledge, not an automatic-discovery result.
2. **Repair evidenced processing gaps.** Select the declared entry rather than
   the earliest header-bearing server, keep source identity in ancestry keys,
   and preserve conflicts as unknown. Bind completion from actual mandatory-call,
   status and body evidence. First replay archives as development evidence; then
   confirm using new observations. A full original-model port is not completed here.
3. **Separate errors and uncertainty.** Retain point error, identification bounds,
   nominal sampling bounds, unknowns and the original conservative gate. Set
   sample sizes before acquisition; do not relax the gate or repeat until it passes.
4. **Keep Kafka bounded.** New acquisition needs a concrete change capable of
   exporting missing message identity. Native association is the reference;
   offsets/topic/time cannot replace identity.
5. **Use one shared-DB corner on Petclinic if the comparison is informative.**
   Healthy discovery precedes single-replica and shared-DB interventions. Predict
   effects on visit creation and owner retrieval while both replicas can remain
   running during the DB outage. Compare native, eBPF, combined and cheap endpoint
   inventory with identical contracts and fault information. If inventory supplies
   the same binding, rediscovering it establishes no model/simulation advantage.
   Cache-dependent reads remain explicit.

The next live acquisition budget is not automatically the original 27 campaigns.
Its scope depends on which source-only repairs survive replay and review; the
original usefulness criterion is unchanged. This iteration ends with diagnosed
replacement effects and a revised design, not a freshly confirmed repaired method.

## Source context for the Kafka finding

The raw audit, rather than these implementation references alone, supports H3.
The pinned OBI Sarama path supplies messaging metadata without the original
trace/parent fields in [go_kafka_transform.go](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/b28e4e7fe0a01f1961b7c4747a13b8ff486d6fec/pkg/ebpf/common/go_kafka_transform.go#L41).
Its [produce parser](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/b28e4e7fe0a01f1961b7c4747a13b8ff486d6fec/pkg/internal/ebpf/kafkaparser/produce.go#L144)
skips record payload bytes. The pinned demo's [Sarama producer](https://github.com/open-telemetry/opentelemetry-demo/blob/8c47d47c9ac27710d2b2a153bcd53e483bffe66d/src/checkout/kafka/producer.go#L39)
uses NoResponse acknowledgements, another reason not to regard coincident
reported offset values as producer/consumer message identity.

## Costs, provenance and review

Retain input archive checksums, original prediction/assignment hashes, diagnostic
source commit, per-campaign processing times, download/preparation time and Actions
job durations, including technical failures. Human/agent time is unmetered and must
not be treated as zero. Existing original acquisition costs remain available in
the final report. No efficiency superiority is claimed by this iteration.

Orchestrator pre-execution verdict: **GO for these diagnostics against the unchanged
original criterion; no empirical-success verdict.** Independent 6.1 Sol/xhigh
skeptic verdict, received before implementation: **GO for the retrospective
diagnostics toward the unchanged original criterion, not for declaring it met.**
The reviewer requires exact original-cell reproduction, calibration-only oracle
substitutions with unknowns retained, identical inputs for each paired direct
calculation, and no presentation of retrospective improvements as a deployable
eBPF result. Improvements describe replacement effects in this estimator,
including its pessimistic treatment of ambiguous classes. H4 measures nominal
Wilson padding, not an inferred effective sample size. DB work remains design-only.

Independent implementation review: **GO at `6e270c6`** after verifying the
two-by-two controls, source-local identity ambiguity handling and independently
preserved raw Kafka fields. Tuple/offset overlaps are untrusted candidates, not
message identities; incomplete raw/preservation audits cannot be called evidence
of collector absence. The run is [40480503659](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40480503659).

Final result review: orchestrator and independent 6.1 Sol/xhigh reviewer **GO for
the integrity and reporting of this diagnostic iteration; NO-GO for claiming the
original usefulness criterion established.** The reviewer independently checked
all 27 distinct campaigns and all 405 protected hashes against the original
report, confirmed the calibration-only oracle boundaries, and verified all nine
raw Kafka audits. Source-only Petclinic negative verdicts have no contradictions
with successful external outcomes in either phase. Class-oracle improvements
include the original estimator's pessimistic ambiguous-class policy. The
protocol-only audit establishes neither positive business completion nor a
deployable correction. Nominal Wilson padding does not establish effective sample
size or temporal interval coverage. The [permanent archive and reproduction](../results/iteration-2/SOURCE.md)
retain the complete diagnostic evidence and cost-snapshot limitations.
