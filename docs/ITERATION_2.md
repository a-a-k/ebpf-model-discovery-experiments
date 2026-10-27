# Iteration 2: diagnose the completed experiment before changing its design

Status: pre-execution review. The user requested this diagnostic iteration on
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
