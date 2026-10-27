# Iteration 2: retrospective failure diagnosis

Generated in [Actions 40480503659](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40480503659).

All 27 original campaigns are included. No new application attempts were made. All original-cell forecasts were reproduced and protected originals were unchanged.

**Oracle-assisted cells are diagnostic controls, not deployable eBPF results or fresh confirmation.** Only calibration class labels and/or calibration business outcomes change. Original class assignments remain frozen in the outcome-only cell. Unknown outcomes remain unknown. Direct conditional weighting is the calculation in every cell.

## H1/H2: paired replacement effects

Mean worst-end error of nominal Wilson envelopes, percentage points, over the same three seeds. The four columns are original; oracle class labels; oracle calibration outcomes; both oracles. All native/combined comparisons, point errors, unknowns and individual seeds are in the CSV files.

| System | Mode | Operation | Original | Class oracle | Outcome oracle | Both oracles |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| deathstarbench | absent | compose_post | 4.01 | 4.01 | 4.01 | 4.01 |
| deathstarbench | absent | read_home_timeline | 4.58 | 4.58 | 4.58 | 4.58 |
| deathstarbench | absent | read_user_timeline | 4.01 | 4.01 | 4.01 | 4.01 |
| deathstarbench | full | compose_post | 4.01 | 4.01 | 4.01 | 4.01 |
| deathstarbench | full | read_home_timeline | 4.58 | 4.58 | 4.58 | 4.58 |
| deathstarbench | full | read_user_timeline | 4.01 | 4.01 | 4.01 | 4.01 |
| deathstarbench | partial | compose_post | 4.01 | 4.01 | 4.01 | 4.01 |
| deathstarbench | partial | read_home_timeline | 4.58 | 4.58 | 4.58 | 4.58 |
| deathstarbench | partial | read_user_timeline | 4.01 | 4.01 | 4.01 | 4.01 |
| otel_demo | absent | add_to_cart | 12.50 | 4.01 | 12.50 | 4.01 |
| otel_demo | absent | browse_product | 12.50 | 4.01 | 12.50 | 4.01 |
| otel_demo | absent | checkout | 12.50 | 4.01 | 12.50 | 4.01 |
| otel_demo | full | add_to_cart | 12.50 | 5.42 | 12.50 | 5.42 |
| otel_demo | full | browse_product | 12.50 | 4.78 | 12.50 | 4.78 |
| otel_demo | full | checkout | 13.09 | 6.65 | 13.09 | 6.65 |
| otel_demo | partial | add_to_cart | 12.50 | 4.01 | 12.50 | 4.01 |
| otel_demo | partial | browse_product | 12.50 | 4.01 | 12.50 | 4.01 |
| otel_demo | partial | checkout | 12.50 | 4.01 | 12.50 | 4.01 |
| petclinic | absent | create_visit | 42.90 | 5.27 | 42.90 | 5.27 |
| petclinic | absent | list_owners | 13.10 | 6.02 | 13.10 | 6.02 |
| petclinic | absent | list_vets | 13.10 | 6.02 | 13.10 | 6.02 |
| petclinic | absent | owner_details_with_visits | 13.25 | 12.50 | 12.35 | 5.27 |
| petclinic | full | create_visit | 32.68 | 5.27 | 32.68 | 5.27 |
| petclinic | full | list_owners | 6.02 | 6.02 | 6.02 | 6.02 |
| petclinic | full | list_vets | 6.02 | 6.02 | 6.02 | 6.02 |
| petclinic | full | owner_details_with_visits | 12.50 | 12.50 | 5.27 | 5.27 |
| petclinic | partial | create_visit | 16.25 | 5.27 | 16.25 | 5.27 |
| petclinic | partial | list_owners | 13.35 | 6.02 | 13.35 | 6.02 |
| petclinic | partial | list_vets | 13.35 | 6.02 | 13.35 | 6.02 |
| petclinic | partial | owner_details_with_visits | 13.50 | 12.50 | 12.60 | 5.27 |

These replacement effects include the estimator's pessimistic treatment of unclassified attempts. They do not demonstrate that the raw eBPF stream contains the oracle information, or that a deployable classifier/completion binder can recover it.

## H4: identification uncertainty and nominal sampling padding

Original eBPF forecasts only; percentage points averaged over three seeds. Padding is the extra total interval width introduced by the nominal Wilson envelope. It is not an estimated effective sample size or validated temporal coverage.

| System | Mode | Operation | Identification worst error | Wilson worst error | Identification width | Wilson padding |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| deathstarbench | absent | compose_post | 0.00 | 4.01 | 0.00 | 4.58 |
| deathstarbench | absent | read_home_timeline | 0.00 | 4.58 | 0.00 | 4.58 |
| deathstarbench | absent | read_user_timeline | 0.00 | 4.01 | 0.00 | 4.58 |
| deathstarbench | full | compose_post | 0.00 | 4.01 | 0.00 | 4.58 |
| deathstarbench | full | read_home_timeline | 0.00 | 4.58 | 0.00 | 4.58 |
| deathstarbench | full | read_user_timeline | 0.00 | 4.01 | 0.00 | 4.58 |
| deathstarbench | partial | compose_post | 0.00 | 4.01 | 0.00 | 4.58 |
| deathstarbench | partial | read_home_timeline | 0.00 | 4.58 | 0.00 | 4.58 |
| deathstarbench | partial | read_user_timeline | 0.00 | 4.01 | 0.00 | 4.58 |
| otel_demo | absent | add_to_cart | 12.50 | 12.50 | 12.50 | 4.01 |
| otel_demo | absent | browse_product | 12.50 | 12.50 | 12.50 | 4.01 |
| otel_demo | absent | checkout | 12.50 | 12.50 | 12.50 | 4.01 |
| otel_demo | full | add_to_cart | 12.50 | 12.50 | 14.56 | 4.43 |
| otel_demo | full | browse_product | 12.50 | 12.50 | 14.46 | 4.40 |
| otel_demo | full | checkout | 11.43 | 13.09 | 14.52 | 5.04 |
| otel_demo | partial | add_to_cart | 12.50 | 12.50 | 12.50 | 4.01 |
| otel_demo | partial | browse_product | 12.50 | 12.50 | 12.50 | 4.01 |
| otel_demo | partial | checkout | 12.50 | 12.50 | 12.50 | 4.01 |
| petclinic | absent | create_visit | 38.06 | 42.90 | 42.22 | 5.35 |
| petclinic | absent | list_owners | 6.18 | 13.10 | 6.18 | 6.92 |
| petclinic | absent | list_vets | 6.18 | 13.10 | 6.18 | 6.92 |
| petclinic | absent | owner_details_with_visits | 12.50 | 13.25 | 6.18 | 6.92 |
| petclinic | full | create_visit | 29.17 | 32.68 | 33.33 | 4.01 |
| petclinic | full | list_owners | 0.00 | 6.02 | 0.00 | 6.02 |
| petclinic | full | list_vets | 0.00 | 6.02 | 0.00 | 6.02 |
| petclinic | full | owner_details_with_visits | 12.50 | 12.50 | 0.00 | 6.02 |
| petclinic | partial | create_visit | 9.93 | 16.25 | 9.93 | 7.07 |
| petclinic | partial | list_owners | 6.46 | 13.35 | 6.46 | 6.89 |
| petclinic | partial | list_vets | 6.46 | 13.35 | 6.46 | 6.89 |
| petclinic | partial | owner_details_with_visits | 12.50 | 13.50 | 6.46 | 6.89 |

## H3: raw Kafka identity and normalization audit

Raw span counts are unique exported Kafka records across the complete retained capture; matcher links are associations, not commits or timely business success.

| Campaign | Source | Raw Kafka spans | Exact normalized matches | Raw exact candidates | Matcher linked | Assessment |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| otel_demo-absent-0-40372011776 | ebpf | 6930 | 6930 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-absent-0-40372011776 | native | 0 | 0 | 0 | 0 | no_observation |
| otel_demo-absent-1-40372011776 | ebpf | 6709 | 6709 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-absent-1-40372011776 | native | 0 | 0 | 0 | 0 | no_observation |
| otel_demo-absent-2-40372011776 | ebpf | 6989 | 6989 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-absent-2-40372011776 | native | 0 | 0 | 0 | 0 | no_observation |
| otel_demo-full-0-40456053398 | ebpf | 6562 | 6562 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-full-0-40456053398 | native | 1337 | 1337 | 668 | 668 | matcher_confirmed |
| otel_demo-full-1-40456061253 | ebpf | 6846 | 6846 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-full-1-40456061253 | native | 1365 | 1365 | 682 | 682 | matcher_confirmed |
| otel_demo-full-2-40372035878 | ebpf | 7017 | 7017 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-full-2-40372035878 | native | 1365 | 1365 | 682 | 682 | matcher_confirmed |
| otel_demo-partial-0-40456045810 | ebpf | 6818 | 6818 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-partial-0-40456045810 | native | 1365 | 1365 | 682 | 682 | matcher_confirmed |
| otel_demo-partial-1-40456045810 | ebpf | 7044 | 7044 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-partial-1-40456045810 | native | 1365 | 1365 | 682 | 682 | matcher_confirmed |
| otel_demo-partial-2-40456045810 | ebpf | 6884 | 6884 | 0 | 0 | raw_candidate_absent_observed_scope |
| otel_demo-partial-2-40456045810 | native | 1365 | 1365 | 682 | 682 | matcher_confirmed |

## Petclinic: source-only completion evidence

The audit receives explicit operation contracts, timing and source spans, but no oracle outcomes. It does not interpret response-payload semantics. Evaluation joins outcomes only afterward. It can identify explicit failure of required completion; this protocol-only audit does not evaluate captured response bodies or certify persistence. Body-field availability is inventoried separately. Per-attempt witnesses are retained in each campaign's semantic-evidence-audit.json.

| Campaign | Source | Target attempts | Proxy true / external false | Of those, source audit establishes failure | False audit / external true |
| --- | --- | ---: | ---: | ---: | ---: |
| petclinic-absent-0-40335553492 | ebpf | 960 | 30 | 24 | 0 |
| petclinic-absent-0-40335553492 | native | 960 | 0 | 0 | 0 |
| petclinic-absent-1-40335553492 | ebpf | 960 | 30 | 15 | 0 |
| petclinic-absent-1-40335553492 | native | 960 | 0 | 0 | 0 |
| petclinic-absent-2-40335553492 | ebpf | 960 | 30 | 22 | 0 |
| petclinic-absent-2-40335553492 | native | 960 | 0 | 0 | 0 |
| petclinic-full-0-40342667653 | ebpf | 960 | 30 | 0 | 0 |
| petclinic-full-0-40342667653 | native | 960 | 30 | 30 | 0 |
| petclinic-full-1-40342667653 | ebpf | 960 | 30 | 0 | 0 |
| petclinic-full-1-40342667653 | native | 960 | 30 | 30 | 0 |
| petclinic-full-2-40342667653 | ebpf | 960 | 30 | 0 | 0 |
| petclinic-full-2-40342667653 | native | 960 | 30 | 30 | 0 |
| petclinic-partial-0-40341237065 | ebpf | 960 | 30 | 0 | 0 |
| petclinic-partial-0-40341237065 | native | 960 | 30 | 30 | 0 |
| petclinic-partial-1-40341237065 | ebpf | 960 | 30 | 0 | 0 |
| petclinic-partial-1-40341237065 | native | 960 | 30 | 30 | 0 |
| petclinic-partial-2-40341237065 | ebpf | 960 | 30 | 0 | 0 |
| petclinic-partial-2-40341237065 | native | 960 | 30 | 30 | 0 |

## Scope and next design

The DB graph was not an input to the original saturated predictor. Shared MySQL already exists in Petclinic. A future DB intervention must actually use that dependency in the prediction and compare ordinary endpoint inventory under the same contracts. This iteration makes no new DB forecast claim.

Source-only repairs need fresh confirmation after their semantics are reviewed. No automatic additional 27-campaign sweep is part of this iteration.

## Provenance and costs

Each system status records elapsed analysis including downloads; each campaign records processing seconds, original hashes and the exact archived input ZIP hash/size. Original acquisition costs and failed attempts remain in the first report. Actions job records cover preparation/failures; human/agent time is unmetered and not zero. No efficiency superiority is established.
