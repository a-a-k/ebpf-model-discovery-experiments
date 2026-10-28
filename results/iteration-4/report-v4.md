# Protocol-v4 saved evaluation report

Aggregate input: [`evaluation-v4.json`](evaluation-v4.json)

This report copies stored evaluation metrics and descriptively counts retained causal verdicts. It introduces no threshold, cross-campaign pooling, relinking, refit, or new forecast.
Every retained campaign is listed as an attempt; selection metadata determines evaluation inclusion.

Optional saved cost input: [`costs-v4.json`](costs-v4.json)

## Grid and retained attempts

| Stored field | Value |
|---|---|
| expected_cells | 27 |
| selected_unambiguous_cells | 1 |
| retained_campaign_attempts | 1 |
| expected_primary_total | 939600 |
| selected_primary_total | 34800 |
| retained_attempt_primary_total | 34800 |
| missing_cells | deathstarbench, absent, 6, deathstarbench, absent, 7, deathstarbench, absent, 8, deathstarbench, full, 6, deathstarbench, full, 7, deathstarbench, full, 8, deathstarbench, partial, 6, deathstarbench, partial, 7, deathstarbench, partial, 8, otel_demo, absent, 6, otel_demo, absent, 7, otel_demo, absent, 8, otel_demo, full, 6, otel_demo, full, 7, otel_demo, full, 8, otel_demo, partial, 6, otel_demo, partial, 7, otel_demo, partial, 8, petclinic, absent, 6, petclinic, absent, 7, petclinic, absent, 8, petclinic, full, 7, petclinic, full, 8, petclinic, partial, 6, petclinic, partial, 7, petclinic, partial, 8 |

All retained attempts (not all are necessarily selected):

| Run | System | Mode | Seed | Complete | Status | Retained root | Primary |
|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40718674400/v4-summary-petclinic-full-6-40718674400 | 34800 |

Saved artifact provenance:

| Run | System | Mode | Seed | Head SHA | Summary artifact ID | Summary artifact | Summary digest | Full artifact ID | Full artifact | Full digest | Evaluation SHA-256 | Manifest SHA-256 | Original campaign root | Retained compact root | Full originals reverified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | ea2e278e50f64bd50597c243d84f834be1b92576 | 12834368897 | v4-summary-petclinic-full-6-40718674400 | sha256:27933333a58a1990652725c9bf6d0bd769e436799cf920b2bf8d9c5669261faf | 12834864581 | campaign-v4-petclinic-full-6-40718674400 | sha256:d94dbd5b37505d41e32e4cd0ff7545bfa08d581a6dc4a944f777b11540915bb6 | 8951d56bba5c424c9ae1184ca29e324e38a8d15c5380b4594b13c7895d1ad6ff | b9f75f032743cdfa1f4cd6339e6f027492d5a37be1a81637d725e0fbec7ae0e1 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40718674400/v4-summary-petclinic-full-6-40718674400 | false |

## Selection and technical replacements

| Stored field | Value |
|---|---|
| provided | false |

Technical replacements:

| Cell | Selected root | Excluded roots | Reason |
|---|---|---|---|
| unavailable | unknown | unknown | unknown |

Ambiguous duplicate cells (unscored unless explicitly selected):

| Cell | Candidate roots | Reason |
|---|---|---|
| unavailable | unknown | unknown |

## Per-attempt forecasts and external outcomes

| Run | System | Mode | Seed | Complete | Operation | Source | Variant | Available | Forecast | Forecast interval | Actual true | Actual false | Actual unknown | External bounds | Worst-end error | Unavailable reason | Graph SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 6ce42fc4696e641d95c24d6c190227ce16f0b783fecefc46255941f6c3e0d854 |
| 40718674400 | petclinic | full | 6 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 3dd528d6044843e9cebd360bfda1a6d84ce57d0a363e013c45e8e90046121580 |
| 40718674400 | petclinic | full | 6 | true | create_visit | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | dc0753883eebb2d8e22e20615939a5463a6ee2c00e9b5eda18163ee6603a6426 |
| 40718674400 | petclinic | full | 6 | true | create_visit | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 979d9b3e4b7ba7f63eb1657be64220c11fde5c1d0e34ff77532165f9dbafebda |
| 40718674400 | petclinic | full | 6 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 32f336ddf257fa741939899c7b929633cee1d148460f8ff38dec2ca53276138f |
| 40718674400 | petclinic | full | 6 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 3d04df7446e8adf05fab36594add4af378899d35819f14149c983cdc2d8a5adb |
| 40718674400 | petclinic | full | 6 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 2132a67933c6cbf1bbd7d125afaed7690f46ff11e3e78f42a74938cbe208683d |
| 40718674400 | petclinic | full | 6 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c69df99714122691e44882de5757919d1eb4e0d80c860ddc30d71e0d3040e406 |
| 40718674400 | petclinic | full | 6 | true | list_owners | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 14b31ec24df704e5e0da070762954400a227c14be6635d3bca607e96b82145f2 |
| 40718674400 | petclinic | full | 6 | true | list_owners | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e368fb6b2f4343b384f0421f768611d0b693bb5b570ee31924ba17060bf7e60c |
| 40718674400 | petclinic | full | 6 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 21c42b941fc39fc302da9e58b05d638b97224292399c53bd880dc0ce06e1af34 |
| 40718674400 | petclinic | full | 6 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 05bf7aa8250b735892dc0846c28d91287a1f49864e9b190a95ce872de5a9ee9a |
| 40718674400 | petclinic | full | 6 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 80e1da5b9c6f511b93d4d5d4cc7e9678927682328cef7bb347dfc3357f02c239 |
| 40718674400 | petclinic | full | 6 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 0172d1a10a4e4d59f70351722a5b999f0bb65b318d0eae4323d8df5c3ef34dea |
| 40718674400 | petclinic | full | 6 | true | list_vets | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 6b97acfdd4eb92dec9ba3a6007dabf1b500ad341579e94b6df3c2656777b269c |
| 40718674400 | petclinic | full | 6 | true | list_vets | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 9bae759599c1027b6fcfef63721e7f74bf531051223db724ed72fb523f12ffe4 |
| 40718674400 | petclinic | full | 6 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c1ff308a7d0c1139174af7b55989a34fe058419448a34b7acc01d48adcd0d77a |
| 40718674400 | petclinic | full | 6 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | a3def3945d88d25903a230204cf369ad5cd8fb8e9159cf256ffdebb5308849d7 |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | e9ae8b6fee4a747162b5917f4e7c89bdd732192763b509c8489fa3e84299375b |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | a6e7ccc9468ff2c847a4feb6bc0b010d6df6f9173b7fa6d460d9394141da186e |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | f2f3a2cc470bb3b4240af457110a6107f74cec1cb1ddb809ee266b83da2eacc5 |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 20e88aae5f0a508fa97cb2c4c627e71bc34b45844a68578f81a84d1003ef240f |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 27899edf15cc089bb71b2b2492db75e41a5cf06a682fa212da744e6d7c391f06 |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | d4b93229caf81d1acd7d66fe6a762c1890ded8d8c428a68212eb8e5d8e6fd3b9 |

## Database up/down evidence

| Run | System | Mode | Seed | Phase | Operation | Success | Failure | Unknown | Total |
|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |

Stored forecast impact (healthy state 11 versus database down):

| Run | System | Mode | Seed | Operation | Source | Variant | Graph available | Healthy 11 | DB down | Impact | Comparison | Accuracy benefit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | create_visit | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | create_visit | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_owners | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_owners | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |

## Strong manual baselines

| Run | System | Mode | Seed | Operation | Available | Prediction | By state | DB baseline available | DB-down prediction | DB basis/reason | Baseline basis |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40718674400 | petclinic | full | 6 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40718674400 | petclinic | full | 6 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |

## Frozen class evaluation

| Run | System | Mode | Seed | Source | Variant | Total | Known | Unknown | Coverage | ARI labeled known | ARI known subset | Unknowns merged | Labels after prediction/reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | native | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | combined | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |

## Asynchronous persistence states

| Run | System | Mode | Seed | Async phase | Available | Records | Stored states | Paused absence is failure | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40718674400 | petclinic | full | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40718674400 | petclinic | full | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40718674400 | petclinic | full | 6 | recovered | false | unknown | unknown | unknown | file_missing |

`async_paused` identifies requests issued while the consumer was paused; it does not claim completion during the pause.
The paused SQL snapshot and the separate after-resume/recovered verification remain distinct external observations.


## Cross-guest and causal evidence

| Run | System | Mode | Seed | Source | Exact parent links | Invalid IDs | Placement coverage | Header verdicts |
|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | ebpf | 6624 | 0 | known_guest_observations=487175; unattributed_guest_observations=0 | corroborated_same_planned_header=3217; unknown_missing_or_unplanned_header=3407 |
| 40718674400 | petclinic | full | 6 | native | 6 | 0 | known_guest_observations=324704; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=6 |

Causal evidence availability (not recomputed from attempt rows):

| Run | System | Mode | Seed | Attempt evidence present | Stored-summary status |
|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | false | no stored causal summary |

Stored exact-chain association verdict census:

These verdicts describe source-local exact chain association in the final capture. They do not establish SQL durability or business correctness.

| Run | System | Mode | Seed | Source | Phase | Total | Observed | Unknown | Not recorded | Unexpected states | Coverage observed/total | All stored states |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |

## Costs

| Run | System | Mode | Seed | Campaign s | Clone s | Build s | Input prep s | Toolchain commands s | Bering replay s | Bering peak RSS KiB | Infrastructure fields | Manual prep measured | Unavailable reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | 4669.68247569 | 3.23547027 | 22.549820751 | 67.482554746 | 1475.647914665 | 890.8722047489999 | 7411120 | Maximum resident set size (kbytes)=7411120; System time (seconds)=194.37; User time (seconds)=2250.74 | false | human preparation time was not instrumented; no full-cost advantage claimed |

Saved campaign phase costs:

Checkpoint creation/upload hold is nested inside campaign elapsed; swap setup precedes campaign elapsed. Full stored cost records remain in the linked evaluation input.

| Run | System | Mode | Seed | Checkpoint creation s | Checkpoint upload hold s | Checkpoint total s | Upload success | Upload artifact ID | Swap setup s | Swap status | Swap requested additional bytes | Resource heartbeat retained |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | 80.069671682 | 19.004231597 | 99.073903279 | true | 12832246532 | 0.087039723 | ready | 8589934592 | true |

Optional saved cost artifact metadata:

| Stored field | Value |
|---|---|
| all_retained_artifact_bytes | 2542553592 |
| all_retained_job_seconds | 25487.0 |
| current_report_job_elapsed_seconds | unknown |
| human_agent_seconds | unknown |
| preparation_and_failed_runs_included | true |
| rule | sum of job durations is compute use, not campaign wall clock; overlapping artifacts are charged each time |
| schema_version | v4-actions-costs |

Saved Actions jobs (independent of retained campaign artifacts):

A job with no stored artifact is retained here as a technical execution record. It is not a campaign row and does not imply zero observations or any scientific outcome.

| Run | Role | Head SHA | Run status | Run conclusion | Job ID | Job name | Job status | Job conclusion | Stored elapsed s | Run artifacts | Run artifact names |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873766641 | prepare | completed | success | 3.0 | 0 | none |
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873831100 | campaign (otel_demo, full, 6) | completed | failure | 2542.0 | 0 | none |
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873831307 | campaign (deathstarbench, full, 6) | completed | failure | 11346.0 | 0 | none |
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873831892 | campaign (petclinic, full, 6) | completed | failure | 2750.0 | 0 | none |
| 40718665137 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | in_progress | unknown | 122923240202 | prepare | completed | success | 3.0 | 1 | training-v4-otel_demo-full-6-40718665137 |
| 40718665137 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | in_progress | unknown | 122923302034 | campaign (otel_demo, full, 6) | in_progress | unknown | unknown | 1 | training-v4-otel_demo-full-6-40718665137 |
| 40718674400 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | completed | success | 122923272255 | prepare | completed | success | 3.0 | 3 | campaign-v4-petclinic-full-6-40718674400, v4-summary-petclinic-full-6-40718674400, training-v4-petclinic-full-6-40718674400 |
| 40718674400 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | completed | success | 122923328293 | campaign (petclinic, full, 6) | completed | success | 4874.0 | 3 | campaign-v4-petclinic-full-6-40718674400, v4-summary-petclinic-full-6-40718674400, training-v4-petclinic-full-6-40718674400 |
| 40731158179 | series | 3e708879889eac8a238027a4640466fc8a76eca5 | in_progress | unknown | 122967537594 | prepare | completed | success | 2.0 | 0 | none |
| 40731158179 | series | 3e708879889eac8a238027a4640466fc8a76eca5 | in_progress | unknown | 122967583738 | campaign (deathstarbench, full, 6) | in_progress | unknown | unknown | 0 | none |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122976976338 | prepare | completed | success | 4.0 | 0 | none |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977038199 | campaign (petclinic, absent, 6) | in_progress | unknown | unknown | 0 | none |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977038314 | campaign (petclinic, absent, 8) | in_progress | unknown | unknown | 0 | none |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977038331 | campaign (petclinic, absent, 7) | in_progress | unknown | unknown | 0 | none |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122976997740 | prepare | completed | success | 4.0 | 0 | none |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977061849 | campaign (petclinic, partial, 8) | in_progress | unknown | unknown | 0 | none |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977061925 | campaign (petclinic, partial, 6) | in_progress | unknown | unknown | 0 | none |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977061988 | campaign (petclinic, partial, 7) | in_progress | unknown | unknown | 0 | none |
| 40733852492 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977019489 | prepare | completed | success | 2.0 | 0 | none |
| 40733852492 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977072193 | campaign (petclinic, full, 7) | in_progress | unknown | unknown | 0 | none |
| 40733858113 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977040060 | prepare | completed | success | 3.0 | 0 | none |
| 40733858113 | series | 4276ea92c3eea897df27be7a65846238847bdfea | in_progress | unknown | 122977084450 | campaign (petclinic, full, 8) | in_progress | unknown | unknown | 0 | none |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703847782 | prepare | completed | success | 4.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703882684 | qualify (otel_demo, full, 6) | completed | failure | 735.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703882705 | qualify (deathstarbench, full, 6) | completed | failure | 360.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703882785 | qualify (petclinic, full, 6) | completed | failure | 417.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40658671556 | replay | 6810aed19ceb7ebc5dfe790aa4c9ae1f3dde527e | completed | failure | 122715914425 | replay | completed | failure | 74.0 | 1 | replay-qualification-v4-all-40655022146-40658671556 |
| 40661273773 | replay | 12954418b8413d07b09fc808f3e5762ab5d249b7 | completed | success | 122724620556 | replay | completed | success | 40.0 | 1 | replay-qualification-v4-petclinic-40655022146-40661273773 |
| 40668208749 | replay | 1d3a7bdde7e280ed7fae0e0c2ebb7928ab43f570 | completed | success | 122748041062 | replay | completed | success | 953.0 | 1 | replay-qualification-v4-all-40655022146-40668208749 |
| 40674465933 | replay | 2b72cd73d7fdb88c3dfa7f51a34e073b6e83d0b8 | completed | success | 122769236368 | replay | completed | success | 1368.0 | 1 | replay-qualification-v4-all-40655022146-40674465933 |

## Figures

[Per-operation figures and stored values](figures/figures-v4.md).

[Fixed model example provenance](provenance/model-example.json).

![Actual Bering eBPF graph](figures/petclinic-full-6-ebpf-network_scope.svg)

Observed topology before operation/placement overlays. Every observed service and edge is retained; aliases are separate. Declared network scope and supplied entry-role interpretation are part of the input. Arrows are structural Bering output, not proof of per-request causality or shared physical identity.
