# Historical iteration-5 results

The completed matrix contains 81 cases: three collectors, three applications,
three SDK modes and repetitions 6/7/8. The saved report contains 2,160 operation
rows and 27 figure groups. These are historical measurements, separate from v6.

## Comparative-design limit

The SDK-only source was filtered from observations acquired while an eBPF
collector was running. It is not a clean SDK-only runtime comparator. Collector
causality, total overhead and total effort cannot be inferred from that design.

## Observed applicability

OBI supported the tested Petclinic and OTel HTTP operation models without SDK
traces. Partial OTel coverage required an explicitly declared union of observed
SERVER edges. The tested Coroot and DeepFlow pipelines did not close the selected
missing-trace paths. All three lacked the necessary operation evidence for the
Social Network Thrift paths. These findings concern the tested versions,
configurations and conversion pipelines; they do not establish universal
collector or protocol limits. See [the feasibility findings](CURRENT_FEASIBILITY_FINDINGS_V5.md).

The Petclinic native comparison contained a route-versus-URL representation
mismatch even though exact URLs existed in raw traces. This limits the tested
pipeline comparison; it does not establish less information in native traces.
See [observation limits](OBSERVATION_LIMITS_V5.md).

## Forecasts and external outcomes

- DeepFlow OTel absent/6, absent/7 and absent/8 each retained 24 unavailable forecasts.
  Each operation had 2,800 successful and 400 failed attempts out of 3,200;
  the equally informed direct conditional baseline predicted 0.875.
- OBI OTel full/6 combined checkout predicted 0.875, while the external outcome
  was 2,563/3,200. The direct conditional baseline also predicted 0.875.
- Coroot OTel partial/6, partial/7 and partial/8 retained unavailable forecasts
  and checkout outcomes of 2,686/3,200, 2,072/3,200 and 518/3,200.
- Coroot OTel full/6 and full/8 native/combined forecasts predicted 0.875 against
  checkout outcomes of 276/3,200 and 1,427/3,200. Full/7 retained unavailable
  forecasts and 189/3,200 successful checkouts.

A graph can exist while evidence required for a forecast is missing. Application
failures and graph coverage are separate observations. Runtime errors alone do
not attribute their cause to a collector. The [runtime diagnosis](OTEL_RUNTIME_LIMITS_V5.md)
records measured failures and unresolved causes. No adverse or unavailable
outcome was replaced merely to obtain a positive result.

## Saved report and provenance

The [final report run](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/42030778818)
and tracked records preserve the report, figures, evidence and cost boundaries:

- [Scientific closure](clean-study-original-matrix81-scientific-closure-20261105.json).
- [Report delivery](clean-study-final-report-delivery-20261105.json).
- [Source-specific review records](../results/iteration-5/main-review-completion-20261030/SOURCE.md).
- [Publication and permanent data releases](ARCHIVE_PUBLICATION.md).

Recorded preparation, failures and workers count toward costs. Unmetered human
work and unfinished publication tails remain unknown. Technical completion does
not establish lower total effort, better forecasts or collector causality.
