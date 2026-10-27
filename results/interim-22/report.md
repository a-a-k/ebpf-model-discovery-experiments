# Generated empirical results

Complete metrics files: 22 of 27 planned campaigns.

Every value is generated from the accompanying CSV and retained per-campaign metrics. Missing/technical failures are not successful zero-error results.

| System | Mode | Source | Operation | Repeats | Mean absolute error, pp | Worst-end error, pp | Informative width | Conservative 5 pp target |
|---|---|---|---|---:|---:|---:|---|---|
| deathstarbench | absent | combined | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | absent | combined | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | absent | combined | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | absent | ebpf | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | absent | ebpf | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | absent | ebpf | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | absent | native | compose_post | 3 | unknown | 87.50 | False | False |
| deathstarbench | absent | native | read_home_timeline | 3 | unknown | 100.00 | False | False |
| deathstarbench | absent | native | read_user_timeline | 3 | unknown | 87.50 | False | False |
| deathstarbench | full | combined | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | full | combined | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | full | combined | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | full | ebpf | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | full | ebpf | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | full | ebpf | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | full | native | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | full | native | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | full | native | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | partial | combined | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | partial | combined | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | partial | combined | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | partial | ebpf | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | partial | ebpf | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | partial | ebpf | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | partial | native | compose_post | 3 | 0.00 | 4.01 | True | True |
| deathstarbench | partial | native | read_home_timeline | 3 | 0.00 | 4.58 | True | True |
| deathstarbench | partial | native | read_user_timeline | 3 | 0.00 | 4.01 | True | True |
| otel_demo | absent | combined | add_to_cart | 3 | unknown | 12.50 | False | False |
| otel_demo | absent | combined | browse_product | 3 | unknown | 12.50 | False | False |
| otel_demo | absent | combined | checkout | 3 | unknown | 12.50 | False | False |
| otel_demo | absent | ebpf | add_to_cart | 3 | unknown | 12.50 | False | False |
| otel_demo | absent | ebpf | browse_product | 3 | unknown | 12.50 | False | False |
| otel_demo | absent | ebpf | checkout | 3 | unknown | 12.50 | False | False |
| otel_demo | absent | native | add_to_cart | 3 | unknown | 87.50 | False | False |
| otel_demo | absent | native | browse_product | 3 | unknown | 87.50 | False | False |
| otel_demo | absent | native | checkout | 3 | unknown | 87.50 | False | False |
| otel_demo | full | combined | add_to_cart | 1 | unknown | unknown | False | pending |
| otel_demo | full | combined | browse_product | 1 | unknown | unknown | False | pending |
| otel_demo | full | combined | checkout | 1 | unknown | unknown | False | pending |
| otel_demo | full | ebpf | add_to_cart | 1 | unknown | unknown | False | pending |
| otel_demo | full | ebpf | browse_product | 1 | unknown | unknown | False | pending |
| otel_demo | full | ebpf | checkout | 1 | unknown | unknown | False | pending |
| otel_demo | full | native | add_to_cart | 1 | unknown | unknown | False | pending |
| otel_demo | full | native | browse_product | 1 | unknown | unknown | False | pending |
| otel_demo | full | native | checkout | 1 | unknown | unknown | False | pending |
| petclinic | absent | combined | create_visit | 3 | unknown | 42.90 | False | False |
| petclinic | absent | combined | list_owners | 3 | unknown | 13.10 | False | False |
| petclinic | absent | combined | list_vets | 3 | unknown | 13.10 | False | False |
| petclinic | absent | combined | owner_details_with_visits | 3 | unknown | 13.25 | False | False |
| petclinic | absent | ebpf | create_visit | 3 | unknown | 42.90 | False | False |
| petclinic | absent | ebpf | list_owners | 3 | unknown | 13.10 | False | False |
| petclinic | absent | ebpf | list_vets | 3 | unknown | 13.10 | False | False |
| petclinic | absent | ebpf | owner_details_with_visits | 3 | unknown | 13.25 | False | False |
| petclinic | absent | native | create_visit | 3 | unknown | 87.50 | False | False |
| petclinic | absent | native | list_owners | 3 | unknown | 100.00 | False | False |
| petclinic | absent | native | list_vets | 3 | unknown | 100.00 | False | False |
| petclinic | absent | native | owner_details_with_visits | 3 | unknown | 87.50 | False | False |
| petclinic | full | combined | create_visit | 3 | unknown | 32.68 | False | False |
| petclinic | full | combined | list_owners | 3 | 0.00 | 6.02 | True | False |
| petclinic | full | combined | list_vets | 3 | 0.00 | 6.02 | True | False |
| petclinic | full | combined | owner_details_with_visits | 3 | 12.50 | 12.50 | True | False |
| petclinic | full | ebpf | create_visit | 3 | unknown | 32.68 | False | False |
| petclinic | full | ebpf | list_owners | 3 | 0.00 | 6.02 | True | False |
| petclinic | full | ebpf | list_vets | 3 | 0.00 | 6.02 | True | False |
| petclinic | full | ebpf | owner_details_with_visits | 3 | 12.50 | 12.50 | True | False |
| petclinic | full | native | create_visit | 3 | unknown | 32.68 | False | False |
| petclinic | full | native | list_owners | 3 | 0.00 | 6.02 | True | False |
| petclinic | full | native | list_vets | 3 | 0.00 | 6.02 | True | False |
| petclinic | full | native | owner_details_with_visits | 3 | 12.50 | 12.50 | True | False |
| petclinic | partial | combined | create_visit | 3 | unknown | 16.25 | False | False |
| petclinic | partial | combined | list_owners | 3 | unknown | 13.35 | False | False |
| petclinic | partial | combined | list_vets | 3 | unknown | 13.35 | False | False |
| petclinic | partial | combined | owner_details_with_visits | 3 | unknown | 13.50 | False | False |
| petclinic | partial | ebpf | create_visit | 3 | unknown | 16.25 | False | False |
| petclinic | partial | ebpf | list_owners | 3 | unknown | 13.35 | False | False |
| petclinic | partial | ebpf | list_vets | 3 | unknown | 13.35 | False | False |
| petclinic | partial | ebpf | owner_details_with_visits | 3 | unknown | 13.50 | False | False |
| petclinic | partial | native | create_visit | 3 | 0.00 | 5.27 | True | False |
| petclinic | partial | native | list_owners | 3 | 0.00 | 6.02 | True | False |
| petclinic | partial | native | list_vets | 3 | 0.00 | 6.02 | True | False |
| petclinic | partial | native | owner_details_with_visits | 3 | 12.50 | 12.50 | True | False |

## Retained run references

- [Actions run 40335553492](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40335553492).
- [Actions run 40336898753](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40336898753).
- [Actions run 40341237065](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40341237065).
- [Actions run 40342667653](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40342667653).
- [Actions run 40349570169](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40349570169).
- [Actions run 40349582587](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40349582587).
- [Actions run 40372011776](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40372011776).
- [Actions run 40372035878](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40372035878).

Retained acquisition failures with status files: 22. See `technical-failures.json`; other failed jobs remain in the job ledger.

Recorded primary attempts in the admitted series: 47520 of 58,320 planned. All retained acquisition attempts, preparation operations and invalid runs are separately listed in `acquisition-attempts.csv`.

Superseded protocol pilots: 1. Full metrics remain in `superseded-pilots.json`; excluded by protocol, not accuracy.

Acquired campaigns excluded by predeclared implementation defects: 6. All paired sources are excluded consistently; retained metrics and exact rules are in `excluded-campaigns.json` and `technical-exclusion-rules.json`. Original acquisition metrics and raw streams remain in the corresponding Actions artifacts/archive.

Total completed job time across retained repository history, including preparation, checks, selector jobs and failures: 113020.0 seconds. See `job-costs.csv`; campaign-only time is separately in `costs.csv`. Ongoing job time is unknown and excluded from this total. Human/agent engineering time was not independently metered and remains unknown.

Class separation and coverage are in `classes.csv`; observed links, DB structure and semantic proxy mismatches in `structure.csv`; DB interventions in `database-controls.csv`; native name-derived and explicitly tagged DB activity in `database-activity.csv`; asynchronous controls and unknown identity chains in `async.csv`. Zero addressed DB nodes does not mean zero DB activity. Unknown endpoints never establish shared identity. Concrete DB-instance identity is not inferred from an IP address. Native ancestry agreement is a reference comparison, not independent ground-truth correctness. Example graphs are validation views of retained calibration observations; original model hashes and forecasts remain unchanged.

Means are reported only with exactly seeds 0, 1, and 2; duplicate attempts must be resolved explicitly from technical-failure history, not averaged or selected by accuracy.
