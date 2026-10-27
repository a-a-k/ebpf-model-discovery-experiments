# Source-contract-v3 results

All 27 campaigns and seeds 3/4/5 are included. No 5 pp accuracy or 10 pp width gate is applied.
Unknown seed-level point errors remain unknown in the aggregate rather than being averaged away.

The shared 10-second client observation cap is not an application deadline. HTTP receipt curves include incorrect terminal responses; independent SQL and async completion intervals remain separate controls.

| System | Mode | Operation | Source | Point abs. error (pp) | Empirical worst-end (pp) | Nominal worst-end (pp) | External unknown | Source unknown |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| deathstarbench | absent | compose_post | combined | unknown | 87.50 | 87.50 | 0 | 9198 |
| deathstarbench | absent | compose_post | ebpf | unknown | 87.50 | 87.50 | 0 | 9198 |
| deathstarbench | absent | compose_post | entry_http | 0.00 | 0.00 | 0.17 | 0 | 0 |
| deathstarbench | absent | compose_post | native | unknown | 87.50 | 87.50 | 0 | 9600 |
| deathstarbench | absent | read_home_timeline | combined | unknown | 42.35 | 42.83 | 0 | 6395 |
| deathstarbench | absent | read_home_timeline | ebpf | unknown | 42.35 | 42.83 | 0 | 6395 |
| deathstarbench | absent | read_home_timeline | entry_http | 0.00 | 0.00 | 0.19 | 0 | 0 |
| deathstarbench | absent | read_home_timeline | native | unknown | 100.00 | 100.00 | 0 | 9600 |
| deathstarbench | absent | read_user_timeline | combined | unknown | 38.46 | 38.94 | 0 | 6389 |
| deathstarbench | absent | read_user_timeline | ebpf | unknown | 38.46 | 38.94 | 0 | 6389 |
| deathstarbench | absent | read_user_timeline | entry_http | 0.00 | 0.00 | 0.17 | 0 | 0 |
| deathstarbench | absent | read_user_timeline | native | unknown | 87.50 | 87.50 | 0 | 9600 |
| deathstarbench | full | compose_post | combined | unknown | 87.50 | 87.50 | 0 | 8714 |
| deathstarbench | full | compose_post | ebpf | unknown | 87.50 | 87.50 | 0 | 8769 |
| deathstarbench | full | compose_post | entry_http | 0.00 | 0.00 | 0.17 | 0 | 0 |
| deathstarbench | full | compose_post | native | unknown | 87.50 | 87.50 | 0 | 8714 |
| deathstarbench | full | read_home_timeline | combined | unknown | 23.80 | 24.21 | 0 | 3020 |
| deathstarbench | full | read_home_timeline | ebpf | unknown | 23.80 | 24.21 | 0 | 3020 |
| deathstarbench | full | read_home_timeline | entry_http | 0.00 | 0.00 | 0.19 | 0 | 0 |
| deathstarbench | full | read_home_timeline | native | unknown | 100.00 | 100.00 | 0 | 9600 |
| deathstarbench | full | read_user_timeline | combined | unknown | 23.94 | 24.30 | 0 | 3015 |
| deathstarbench | full | read_user_timeline | ebpf | unknown | 23.94 | 24.30 | 0 | 3029 |
| deathstarbench | full | read_user_timeline | entry_http | 0.00 | 0.00 | 0.17 | 0 | 0 |
| deathstarbench | full | read_user_timeline | native | unknown | 87.50 | 87.50 | 0 | 8769 |
| deathstarbench | partial | compose_post | combined | unknown | 87.50 | 87.50 | 0 | 8400 |
| deathstarbench | partial | compose_post | ebpf | unknown | 87.50 | 87.50 | 0 | 8400 |
| deathstarbench | partial | compose_post | entry_http | 0.00 | 0.00 | 0.17 | 0 | 0 |
| deathstarbench | partial | compose_post | native | unknown | 87.50 | 87.50 | 0 | 8400 |
| deathstarbench | partial | read_home_timeline | combined | unknown | 13.74 | 14.04 | 0 | 0 |
| deathstarbench | partial | read_home_timeline | ebpf | unknown | 13.74 | 14.04 | 0 | 0 |
| deathstarbench | partial | read_home_timeline | entry_http | 0.00 | 0.00 | 0.19 | 0 | 0 |
| deathstarbench | partial | read_home_timeline | native | unknown | 100.00 | 100.00 | 0 | 9600 |
| deathstarbench | partial | read_user_timeline | combined | unknown | 12.31 | 12.51 | 0 | 0 |
| deathstarbench | partial | read_user_timeline | ebpf | unknown | 12.31 | 12.51 | 0 | 0 |
| deathstarbench | partial | read_user_timeline | entry_http | 0.00 | 0.00 | 0.17 | 0 | 0 |
| deathstarbench | partial | read_user_timeline | native | unknown | 87.50 | 87.50 | 0 | 8400 |
| otel_demo | absent | add_to_cart | combined | unknown | 4.09 | 4.27 | 0 | 0 |
| otel_demo | absent | add_to_cart | ebpf | unknown | 4.09 | 4.27 | 0 | 0 |
| otel_demo | absent | add_to_cart | entry_http | 0.11 | 0.11 | 0.31 | 0 | 0 |
| otel_demo | absent | add_to_cart | native | unknown | 87.50 | 87.50 | 0 | 9600 |
| otel_demo | absent | browse_product | combined | unknown | 4.06 | 4.24 | 0 | 0 |
| otel_demo | absent | browse_product | ebpf | unknown | 4.06 | 4.24 | 0 | 0 |
| otel_demo | absent | browse_product | entry_http | 0.12 | 0.12 | 0.33 | 0 | 0 |
| otel_demo | absent | browse_product | native | unknown | 87.50 | 87.50 | 0 | 9600 |
| otel_demo | absent | checkout | combined | unknown | 4.12 | 4.31 | 0 | 0 |
| otel_demo | absent | checkout | ebpf | unknown | 4.12 | 4.31 | 0 | 0 |
| otel_demo | absent | checkout | entry_http | 0.18 | 0.18 | 0.40 | 0 | 0 |
| otel_demo | absent | checkout | native | unknown | 87.50 | 87.50 | 0 | 9600 |
| otel_demo | full | add_to_cart | combined | unknown | 3.63 | 4.09 | 0 | 6 |
| otel_demo | full | add_to_cart | ebpf | unknown | 3.63 | 4.09 | 0 | 6 |
| otel_demo | full | add_to_cart | entry_http | 3.63 | 3.63 | 4.09 | 0 | 0 |
| otel_demo | full | add_to_cart | native | unknown | 87.18 | 87.18 | 0 | 8384 |
| otel_demo | full | browse_product | combined | unknown | 3.62 | 4.07 | 0 | 6 |
| otel_demo | full | browse_product | ebpf | unknown | 3.62 | 4.07 | 0 | 6 |
| otel_demo | full | browse_product | entry_http | 3.62 | 3.62 | 4.07 | 0 | 0 |
| otel_demo | full | browse_product | native | unknown | 87.16 | 87.16 | 0 | 8389 |
| otel_demo | full | checkout | combined | unknown | 5.47 | 5.89 | 603 | 608 |
| otel_demo | full | checkout | ebpf | unknown | 5.47 | 5.89 | 603 | 608 |
| otel_demo | full | checkout | entry_http | unknown | 5.46 | 5.89 | 603 | 603 |
| otel_demo | full | checkout | native | unknown | 86.40 | 86.40 | 603 | 8316 |
| otel_demo | partial | add_to_cart | combined | unknown | 2.49 | 2.90 | 0 | 122 |
| otel_demo | partial | add_to_cart | ebpf | unknown | 2.67 | 3.09 | 0 | 123 |
| otel_demo | partial | add_to_cart | entry_http | 0.88 | 0.88 | 1.19 | 0 | 0 |
| otel_demo | partial | add_to_cart | native | unknown | 87.50 | 87.50 | 0 | 8596 |
| otel_demo | partial | browse_product | combined | unknown | 2.79 | 3.32 | 0 | 135 |
| otel_demo | partial | browse_product | ebpf | unknown | 2.79 | 3.32 | 0 | 135 |
| otel_demo | partial | browse_product | entry_http | 1.00 | 1.00 | 1.31 | 0 | 0 |
| otel_demo | partial | browse_product | native | unknown | 87.50 | 87.50 | 0 | 8600 |
| otel_demo | partial | checkout | combined | unknown | 3.49 | 4.07 | 0 | 130 |
| otel_demo | partial | checkout | ebpf | unknown | 3.69 | 4.28 | 0 | 130 |
| otel_demo | partial | checkout | entry_http | 1.97 | 1.97 | 2.35 | 0 | 0 |
| otel_demo | partial | checkout | native | unknown | 87.48 | 87.48 | 0 | 8601 |
| petclinic | absent | create_visit | combined | unknown | 87.50 | 87.50 | 0 | 6600 |
| petclinic | absent | create_visit | ebpf | unknown | 87.50 | 87.50 | 0 | 6600 |
| petclinic | absent | create_visit | entry_http | unknown | 87.50 | 87.50 | 0 | 6300 |
| petclinic | absent | create_visit | native | unknown | 87.50 | 87.50 | 0 | 7200 |
| petclinic | absent | list_owners | combined | unknown | 33.30 | 33.49 | 0 | 2399 |
| petclinic | absent | list_owners | ebpf | unknown | 33.30 | 33.49 | 0 | 2399 |
| petclinic | absent | list_owners | entry_http | 0.00 | 0.00 | 0.26 | 0 | 0 |
| petclinic | absent | list_owners | native | unknown | 100.00 | 100.00 | 0 | 7200 |
| petclinic | absent | list_vets | combined | unknown | 33.32 | 33.50 | 0 | 2400 |
| petclinic | absent | list_vets | ebpf | unknown | 33.32 | 33.50 | 0 | 2400 |
| petclinic | absent | list_vets | entry_http | 0.00 | 0.00 | 0.26 | 0 | 0 |
| petclinic | absent | list_vets | native | unknown | 100.00 | 100.00 | 0 | 7200 |
| petclinic | absent | owner_details_with_visits | combined | unknown | 29.19 | 29.30 | 0 | 2401 |
| petclinic | absent | owner_details_with_visits | ebpf | unknown | 29.19 | 29.30 | 0 | 2401 |
| petclinic | absent | owner_details_with_visits | entry_http | 0.07 | 0.07 | 0.23 | 0 | 0 |
| petclinic | absent | owner_details_with_visits | native | unknown | 87.43 | 87.43 | 0 | 7200 |
| petclinic | full | create_visit | combined | unknown | 87.50 | 87.50 | 0 | 6300 |
| petclinic | full | create_visit | ebpf | unknown | 87.50 | 87.50 | 0 | 6300 |
| petclinic | full | create_visit | entry_http | unknown | 87.50 | 87.50 | 0 | 6300 |
| petclinic | full | create_visit | native | unknown | 87.50 | 87.50 | 0 | 6300 |
| petclinic | full | list_owners | combined | unknown | 7.44 | 7.89 | 0 | 2 |
| petclinic | full | list_owners | ebpf | unknown | 7.44 | 7.89 | 0 | 2 |
| petclinic | full | list_owners | entry_http | 0.00 | 0.00 | 0.26 | 0 | 0 |
| petclinic | full | list_owners | native | unknown | 100.00 | 100.00 | 0 | 7200 |
| petclinic | full | list_vets | combined | unknown | 7.24 | 7.68 | 0 | 0 |
| petclinic | full | list_vets | ebpf | unknown | 7.24 | 7.68 | 0 | 0 |
| petclinic | full | list_vets | entry_http | 0.00 | 0.00 | 0.26 | 0 | 0 |
| petclinic | full | list_vets | native | unknown | 100.00 | 100.00 | 0 | 7200 |
| petclinic | full | owner_details_with_visits | combined | unknown | 4.18 | 4.28 | 0 | 0 |
| petclinic | full | owner_details_with_visits | ebpf | unknown | 4.18 | 4.28 | 0 | 0 |
| petclinic | full | owner_details_with_visits | entry_http | 0.07 | 0.07 | 0.23 | 0 | 0 |
| petclinic | full | owner_details_with_visits | native | unknown | 87.43 | 87.43 | 0 | 7200 |
| petclinic | partial | create_visit | combined | unknown | 87.50 | 87.50 | 0 | 6600 |
| petclinic | partial | create_visit | ebpf | unknown | 87.50 | 87.50 | 0 | 6600 |
| petclinic | partial | create_visit | entry_http | unknown | 87.50 | 87.50 | 0 | 6300 |
| petclinic | partial | create_visit | native | unknown | 87.50 | 87.50 | 0 | 6600 |
| petclinic | partial | list_owners | combined | unknown | 33.31 | 33.50 | 0 | 2400 |
| petclinic | partial | list_owners | ebpf | unknown | 33.31 | 33.50 | 0 | 2400 |
| petclinic | partial | list_owners | entry_http | 0.00 | 0.00 | 0.26 | 0 | 0 |
| petclinic | partial | list_owners | native | unknown | 100.00 | 100.00 | 0 | 7200 |
| petclinic | partial | list_vets | combined | unknown | 33.32 | 33.50 | 0 | 2400 |
| petclinic | partial | list_vets | ebpf | unknown | 33.32 | 33.50 | 0 | 2400 |
| petclinic | partial | list_vets | entry_http | 0.00 | 0.00 | 0.26 | 0 | 0 |
| petclinic | partial | list_vets | native | unknown | 100.00 | 100.00 | 0 | 7200 |
| petclinic | partial | owner_details_with_visits | combined | unknown | 29.23 | 29.32 | 0 | 2399 |
| petclinic | partial | owner_details_with_visits | ebpf | unknown | 29.23 | 29.32 | 0 | 2399 |
| petclinic | partial | owner_details_with_visits | entry_http | 0.07 | 0.07 | 0.23 | 0 | 0 |
| petclinic | partial | owner_details_with_visits | native | unknown | 87.43 | 87.43 | 0 | 7200 |

## Separate controls

Automatic grouping, shared-database intervention, and asynchronous association remain separate controls. Their per-campaign counts and input hashes are retained in `results.json`; association is not durability, and absence of a predicted DB cause is not a prediction of business success.

### Automatic grouping

| System | Mode | Source | Variant | Phase | Covered / total | Mean unknown | Mean ARI on covered |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| deathstarbench | absent | combined | route | calibration | 40548 / 72000 | 0.437 | 1.000 |
| deathstarbench | absent | combined | route | class_test | 601 / 1800 | 0.666 | unknown |
| deathstarbench | absent | combined | route | target | 9626 / 28800 | 0.666 | 1.000 |
| deathstarbench | absent | combined | route_and_downstream | calibration | 40548 / 72000 | 0.437 | 1.000 |
| deathstarbench | absent | combined | route_and_downstream | class_test | 601 / 1800 | 0.666 | unknown |
| deathstarbench | absent | combined | route_and_downstream | target | 9626 / 28800 | 0.666 | 1.000 |
| deathstarbench | absent | ebpf | route | calibration | 40548 / 72000 | 0.437 | 1.000 |
| deathstarbench | absent | ebpf | route | class_test | 601 / 1800 | 0.666 | unknown |
| deathstarbench | absent | ebpf | route | target | 9626 / 28800 | 0.666 | 1.000 |
| deathstarbench | absent | ebpf | route_and_downstream | calibration | 40548 / 72000 | 0.437 | 1.000 |
| deathstarbench | absent | ebpf | route_and_downstream | class_test | 601 / 1800 | 0.666 | unknown |
| deathstarbench | absent | ebpf | route_and_downstream | target | 9626 / 28800 | 0.666 | 1.000 |
| deathstarbench | absent | native | route | calibration | 0 / 72000 | 1.000 | unknown |
| deathstarbench | absent | native | route | class_test | 0 / 1800 | 1.000 | unknown |
| deathstarbench | absent | native | route | target | 0 / 28800 | 1.000 | unknown |
| deathstarbench | absent | native | route_and_downstream | calibration | 0 / 72000 | 1.000 | unknown |
| deathstarbench | absent | native | route_and_downstream | class_test | 0 / 1800 | 1.000 | unknown |
| deathstarbench | absent | native | route_and_downstream | target | 0 / 28800 | 1.000 | unknown |
| deathstarbench | full | combined | route | calibration | 59970 / 72000 | 0.167 | 1.000 |
| deathstarbench | full | combined | route | class_test | 1373 / 1800 | 0.237 | 1.000 |
| deathstarbench | full | combined | route | target | 22588 / 28800 | 0.216 | 1.000 |
| deathstarbench | full | combined | route_and_downstream | calibration | 0 / 72000 | 1.000 | unknown |
| deathstarbench | full | combined | route_and_downstream | class_test | 0 / 1800 | 1.000 | unknown |
| deathstarbench | full | combined | route_and_downstream | target | 0 / 28800 | 1.000 | unknown |
| deathstarbench | full | ebpf | route | calibration | 58037 / 72000 | 0.194 | 1.000 |
| deathstarbench | full | ebpf | route | class_test | 1237 / 1800 | 0.313 | 1.000 |
| deathstarbench | full | ebpf | route | target | 19889 / 28800 | 0.309 | 1.000 |
| deathstarbench | full | ebpf | route_and_downstream | calibration | 58035 / 72000 | 0.194 | 1.000 |
| deathstarbench | full | ebpf | route_and_downstream | class_test | 1237 / 1800 | 0.313 | 1.000 |
| deathstarbench | full | ebpf | route_and_downstream | target | 19889 / 28800 | 0.309 | 1.000 |
| deathstarbench | full | native | route | calibration | 59964 / 72000 | 0.167 | 1.000 |
| deathstarbench | full | native | route | class_test | 1373 / 1800 | 0.237 | 1.000 |
| deathstarbench | full | native | route | target | 22584 / 28800 | 0.216 | 1.000 |
| deathstarbench | full | native | route_and_downstream | calibration | 47964 / 72000 | 0.334 | 1.000 |
| deathstarbench | full | native | route_and_downstream | class_test | 1373 / 1800 | 0.237 | 1.000 |
| deathstarbench | full | native | route_and_downstream | target | 20867 / 28800 | 0.275 | 1.000 |
| deathstarbench | partial | combined | route | calibration | 59221 / 72000 | 0.177 | 1.000 |
| deathstarbench | partial | combined | route | class_test | 1800 / 1800 | 0.000 | 1.000 |
| deathstarbench | partial | combined | route | target | 28800 / 28800 | 0.000 | 1.000 |
| deathstarbench | partial | combined | route_and_downstream | calibration | 791 / 72000 | 0.989 | unknown |
| deathstarbench | partial | combined | route_and_downstream | class_test | 0 / 1800 | 1.000 | unknown |
| deathstarbench | partial | combined | route_and_downstream | target | 0 / 28800 | 1.000 | unknown |
| deathstarbench | partial | ebpf | route | calibration | 58299 / 72000 | 0.190 | 1.000 |
| deathstarbench | partial | ebpf | route | class_test | 1800 / 1800 | 0.000 | 1.000 |
| deathstarbench | partial | ebpf | route | target | 28800 / 28800 | 0.000 | 1.000 |
| deathstarbench | partial | ebpf | route_and_downstream | calibration | 58299 / 72000 | 0.190 | 1.000 |
| deathstarbench | partial | ebpf | route_and_downstream | class_test | 1800 / 1800 | 0.000 | 1.000 |
| deathstarbench | partial | ebpf | route_and_downstream | target | 28800 / 28800 | 0.000 | 1.000 |
| deathstarbench | partial | native | route | calibration | 59219 / 72000 | 0.178 | 1.000 |
| deathstarbench | partial | native | route | class_test | 1800 / 1800 | 0.000 | 1.000 |
| deathstarbench | partial | native | route | target | 28800 / 28800 | 0.000 | 1.000 |
| deathstarbench | partial | native | route_and_downstream | calibration | 53633 / 72000 | 0.255 | 1.000 |
| deathstarbench | partial | native | route_and_downstream | class_test | 1800 / 1800 | 0.000 | 1.000 |
| deathstarbench | partial | native | route_and_downstream | target | 27600 / 28800 | 0.042 | 1.000 |
| otel_demo | absent | combined | route | calibration | 52882 / 72000 | 0.266 | 1.000 |
| otel_demo | absent | combined | route | class_test | 1800 / 1800 | 0.000 | 1.000 |
| otel_demo | absent | combined | route | target | 25200 / 28800 | 0.125 | 1.000 |
| otel_demo | absent | combined | route_and_downstream | calibration | 41369 / 72000 | 0.425 | 0.468 |
| otel_demo | absent | combined | route_and_downstream | class_test | 1376 / 1800 | 0.236 | 0.505 |
| otel_demo | absent | combined | route_and_downstream | target | 19465 / 28800 | 0.324 | 0.515 |
| otel_demo | absent | ebpf | route | calibration | 52882 / 72000 | 0.266 | 1.000 |
| otel_demo | absent | ebpf | route | class_test | 1800 / 1800 | 0.000 | 1.000 |
| otel_demo | absent | ebpf | route | target | 25200 / 28800 | 0.125 | 1.000 |
| otel_demo | absent | ebpf | route_and_downstream | calibration | 41369 / 72000 | 0.425 | 0.468 |
| otel_demo | absent | ebpf | route_and_downstream | class_test | 1376 / 1800 | 0.236 | 0.505 |
| otel_demo | absent | ebpf | route_and_downstream | target | 19465 / 28800 | 0.324 | 0.515 |
| otel_demo | absent | native | route | calibration | 0 / 72000 | 1.000 | unknown |
| otel_demo | absent | native | route | class_test | 0 / 1800 | 1.000 | unknown |
| otel_demo | absent | native | route | target | 0 / 28800 | 1.000 | unknown |
| otel_demo | absent | native | route_and_downstream | calibration | 0 / 72000 | 1.000 | unknown |
| otel_demo | absent | native | route_and_downstream | class_test | 0 / 1800 | 1.000 | unknown |
| otel_demo | absent | native | route_and_downstream | target | 0 / 28800 | 1.000 | unknown |
| otel_demo | full | combined | route | calibration | 0 / 72000 | 1.000 | unknown |
| otel_demo | full | combined | route | class_test | 0 / 1800 | 1.000 | unknown |
| otel_demo | full | combined | route | target | 0 / 28800 | 1.000 | unknown |
| otel_demo | full | combined | route_and_downstream | calibration | 0 / 72000 | 1.000 | unknown |
| otel_demo | full | combined | route_and_downstream | class_test | 0 / 1800 | 1.000 | unknown |
| otel_demo | full | combined | route_and_downstream | target | 0 / 28800 | 1.000 | unknown |
| otel_demo | full | ebpf | route | calibration | 51202 / 72000 | 0.289 | 1.000 |
| otel_demo | full | ebpf | route | class_test | 1800 / 1800 | 0.000 | 1.000 |
| otel_demo | full | ebpf | route | target | 24505 / 28800 | 0.149 | 1.000 |
| otel_demo | full | ebpf | route_and_downstream | calibration | 45703 / 72000 | 0.365 | 0.442 |
| otel_demo | full | ebpf | route_and_downstream | class_test | 1613 / 1800 | 0.104 | 0.443 |
| otel_demo | full | ebpf | route_and_downstream | target | 21592 / 28800 | 0.250 | 0.434 |
| otel_demo | full | native | route | calibration | 51202 / 72000 | 0.289 | 1.000 |
| otel_demo | full | native | route | class_test | 1799 / 1800 | 0.001 | 1.000 |
| otel_demo | full | native | route | target | 24449 / 28800 | 0.151 | 1.000 |
| otel_demo | full | native | route_and_downstream | calibration | 50745 / 72000 | 0.295 | 1.000 |
| otel_demo | full | native | route_and_downstream | class_test | 1799 / 1800 | 0.001 | 1.000 |
| otel_demo | full | native | route_and_downstream | target | 24340 / 28800 | 0.155 | 1.000 |
| otel_demo | partial | combined | route | calibration | 0 / 72000 | 1.000 | unknown |
| otel_demo | partial | combined | route | class_test | 0 / 1800 | 1.000 | unknown |
| otel_demo | partial | combined | route | target | 0 / 28800 | 1.000 | unknown |
| otel_demo | partial | combined | route_and_downstream | calibration | 0 / 72000 | 1.000 | unknown |
| otel_demo | partial | combined | route_and_downstream | class_test | 0 / 1800 | 1.000 | unknown |
| otel_demo | partial | combined | route_and_downstream | target | 0 / 28800 | 1.000 | unknown |
| otel_demo | partial | ebpf | route | calibration | 52640 / 72000 | 0.269 | 1.000 |
| otel_demo | partial | ebpf | route | class_test | 1796 / 1800 | 0.002 | 1.000 |
| otel_demo | partial | ebpf | route | target | 25179 / 28800 | 0.126 | 1.000 |
| otel_demo | partial | ebpf | route_and_downstream | calibration | 46745 / 72000 | 0.351 | 0.443 |
| otel_demo | partial | ebpf | route_and_downstream | class_test | 1589 / 1800 | 0.117 | 0.509 |
| otel_demo | partial | ebpf | route_and_downstream | target | 22233 / 28800 | 0.228 | 0.462 |
| otel_demo | partial | native | route | calibration | 51675 / 72000 | 0.282 | 1.000 |
| otel_demo | partial | native | route | class_test | 1691 / 1800 | 0.061 | 1.000 |
| otel_demo | partial | native | route | target | 24926 / 28800 | 0.135 | 1.000 |
| otel_demo | partial | native | route_and_downstream | calibration | 51542 / 72000 | 0.284 | 1.000 |
| otel_demo | partial | native | route_and_downstream | class_test | 1690 / 1800 | 0.061 | 1.000 |
| otel_demo | partial | native | route_and_downstream | target | 24910 / 28800 | 0.135 | 1.000 |
| petclinic | absent | combined | route | calibration | 48024 / 72000 | 0.333 | 1.000 |
| petclinic | absent | combined | route | class_test | 1193 / 1800 | 0.337 | unknown |
| petclinic | absent | combined | route | target | 19189 / 28800 | 0.334 | unknown |
| petclinic | absent | combined | route_and_downstream | calibration | 43574 / 72000 | 0.395 | 0.545 |
| petclinic | absent | combined | route_and_downstream | class_test | 1121 / 1800 | 0.377 | unknown |
| petclinic | absent | combined | route_and_downstream | target | 16987 / 28800 | 0.410 | unknown |
| petclinic | absent | ebpf | route | calibration | 48024 / 72000 | 0.333 | 1.000 |
| petclinic | absent | ebpf | route | class_test | 1193 / 1800 | 0.337 | unknown |
| petclinic | absent | ebpf | route | target | 19189 / 28800 | 0.334 | unknown |
| petclinic | absent | ebpf | route_and_downstream | calibration | 43574 / 72000 | 0.395 | 0.545 |
| petclinic | absent | ebpf | route_and_downstream | class_test | 1121 / 1800 | 0.377 | unknown |
| petclinic | absent | ebpf | route_and_downstream | target | 16987 / 28800 | 0.410 | unknown |
| petclinic | absent | native | route | calibration | 0 / 72000 | 1.000 | unknown |
| petclinic | absent | native | route | class_test | 0 / 1800 | 1.000 | unknown |
| petclinic | absent | native | route | target | 0 / 28800 | 1.000 | unknown |
| petclinic | absent | native | route_and_downstream | calibration | 0 / 72000 | 1.000 | unknown |
| petclinic | absent | native | route_and_downstream | class_test | 0 / 1800 | 1.000 | unknown |
| petclinic | absent | native | route_and_downstream | target | 0 / 28800 | 1.000 | unknown |
| petclinic | full | combined | route | calibration | 372 / 72000 | 0.995 | unknown |
| petclinic | full | combined | route | class_test | 360 / 1800 | 0.800 | unknown |
| petclinic | full | combined | route | target | 6 / 28800 | 1.000 | unknown |
| petclinic | full | combined | route_and_downstream | calibration | 352 / 72000 | 0.995 | unknown |
| petclinic | full | combined | route_and_downstream | class_test | 360 / 1800 | 0.800 | unknown |
| petclinic | full | combined | route_and_downstream | target | 5 / 28800 | 1.000 | unknown |
| petclinic | full | ebpf | route | calibration | 63724 / 72000 | 0.115 | 1.000 |
| petclinic | full | ebpf | route | class_test | 1425 / 1800 | 0.208 | 1.000 |
| petclinic | full | ebpf | route | target | 28792 / 28800 | 0.000 | 1.000 |
| petclinic | full | ebpf | route_and_downstream | calibration | 63724 / 72000 | 0.115 | 1.000 |
| petclinic | full | ebpf | route_and_downstream | class_test | 1425 / 1800 | 0.208 | 1.000 |
| petclinic | full | ebpf | route_and_downstream | target | 28791 / 28800 | 0.000 | 1.000 |
| petclinic | full | native | route | calibration | 64105 / 72000 | 0.110 | 1.000 |
| petclinic | full | native | route | class_test | 1785 / 1800 | 0.008 | 1.000 |
| petclinic | full | native | route | target | 28800 / 28800 | 0.000 | 1.000 |
| petclinic | full | native | route_and_downstream | calibration | 61226 / 72000 | 0.150 | 1.000 |
| petclinic | full | native | route_and_downstream | class_test | 1776 / 1800 | 0.013 | 0.999 |
| petclinic | full | native | route_and_downstream | target | 28024 / 28800 | 0.027 | 1.000 |
| petclinic | partial | combined | route | calibration | 21 / 72000 | 1.000 | unknown |
| petclinic | partial | combined | route | class_test | 3 / 1800 | 0.998 | unknown |
| petclinic | partial | combined | route | target | 10 / 28800 | 1.000 | unknown |
| petclinic | partial | combined | route_and_downstream | calibration | 17 / 72000 | 1.000 | unknown |
| petclinic | partial | combined | route_and_downstream | class_test | 3 / 1800 | 0.998 | unknown |
| petclinic | partial | combined | route_and_downstream | target | 10 / 28800 | 1.000 | unknown |
| petclinic | partial | ebpf | route | calibration | 48014 / 72000 | 0.333 | 1.000 |
| petclinic | partial | ebpf | route | class_test | 1197 / 1800 | 0.335 | unknown |
| petclinic | partial | ebpf | route | target | 19197 / 28800 | 0.333 | unknown |
| petclinic | partial | ebpf | route_and_downstream | calibration | 48014 / 72000 | 0.333 | 1.000 |
| petclinic | partial | ebpf | route_and_downstream | class_test | 1197 / 1800 | 0.335 | unknown |
| petclinic | partial | ebpf | route_and_downstream | target | 19197 / 28800 | 0.333 | unknown |
| petclinic | partial | native | route | calibration | 48035 / 72000 | 0.333 | 1.000 |
| petclinic | partial | native | route | class_test | 1200 / 1800 | 0.333 | unknown |
| petclinic | partial | native | route | target | 19207 / 28800 | 0.333 | 1.000 |
| petclinic | partial | native | route_and_downstream | calibration | 45200 / 72000 | 0.372 | 1.000 |
| petclinic | partial | native | route_and_downstream | class_test | 1194 / 1800 | 0.337 | unknown |
| petclinic | partial | native | route_and_downstream | target | 18697 / 28800 | 0.351 | 1.000 |

### Petclinic selected-database prediction

| Mode | Predictor | Operation | Phase | Predicted true | Predicted false | Predicted unknown | Supported | Contradicted |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| absent | combined | create_visit | db_down | 15 | 0 | 0 | 15 | 0 |
| absent | combined | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | combined | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| absent | combined | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | combined | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | combined | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | combined | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | combined | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | ebpf | create_visit | db_down | 15 | 0 | 0 | 15 | 0 |
| absent | ebpf | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | ebpf | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| absent | ebpf | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | ebpf | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | ebpf | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | ebpf | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | ebpf | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | native | create_visit | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | native | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | native | list_owners | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | native | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | native | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | native | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | native | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | native | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | static_endpoint_baseline | create_visit | db_down | 15 | 0 | 0 | 15 | 0 |
| absent | static_endpoint_baseline | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | static_endpoint_baseline | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| absent | static_endpoint_baseline | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | static_endpoint_baseline | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| absent | static_endpoint_baseline | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| absent | static_endpoint_baseline | owner_details_with_visits | db_down | 15 | 0 | 0 | 0 | 0 |
| absent | static_endpoint_baseline | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| full | combined | create_visit | db_down | 5 | 0 | 10 | 5 | 0 |
| full | combined | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| full | combined | list_owners | db_down | 10 | 0 | 5 | 0 | 0 |
| full | combined | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| full | combined | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| full | combined | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| full | combined | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| full | combined | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| full | ebpf | create_visit | db_down | 5 | 0 | 10 | 5 | 0 |
| full | ebpf | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| full | ebpf | list_owners | db_down | 10 | 0 | 5 | 0 | 0 |
| full | ebpf | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| full | ebpf | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| full | ebpf | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| full | ebpf | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| full | ebpf | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| full | native | create_visit | db_down | 5 | 0 | 10 | 5 | 0 |
| full | native | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| full | native | list_owners | db_down | 10 | 0 | 5 | 0 | 0 |
| full | native | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| full | native | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| full | native | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| full | native | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| full | native | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| full | static_endpoint_baseline | create_visit | db_down | 15 | 0 | 0 | 15 | 0 |
| full | static_endpoint_baseline | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| full | static_endpoint_baseline | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| full | static_endpoint_baseline | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| full | static_endpoint_baseline | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| full | static_endpoint_baseline | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| full | static_endpoint_baseline | owner_details_with_visits | db_down | 15 | 0 | 0 | 0 | 0 |
| full | static_endpoint_baseline | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | combined | create_visit | db_down | 15 | 0 | 0 | 15 | 0 |
| partial | combined | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | combined | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| partial | combined | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | combined | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | combined | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | combined | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | combined | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | ebpf | create_visit | db_down | 15 | 0 | 0 | 15 | 0 |
| partial | ebpf | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | ebpf | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| partial | ebpf | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | ebpf | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | ebpf | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | ebpf | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | ebpf | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | native | create_visit | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | native | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | native | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| partial | native | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | native | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | native | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | native | owner_details_with_visits | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | native | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | static_endpoint_baseline | create_visit | db_down | 15 | 0 | 0 | 15 | 0 |
| partial | static_endpoint_baseline | create_visit | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | static_endpoint_baseline | list_owners | db_down | 15 | 0 | 0 | 0 | 0 |
| partial | static_endpoint_baseline | list_owners | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | static_endpoint_baseline | list_vets | db_down | 0 | 0 | 15 | 0 | 0 |
| partial | static_endpoint_baseline | list_vets | db_up | 0 | 15 | 0 | 0 | 0 |
| partial | static_endpoint_baseline | owner_details_with_visits | db_down | 15 | 0 | 0 | 0 | 0 |
| partial | static_endpoint_baseline | owner_details_with_visits | db_up | 0 | 15 | 0 | 0 | 0 |

### OTel asynchronous association

| Mode | Source | Phase | Linked | Unknown | Immediate T/F/U | Durable T/F/U |
| --- | --- | --- | ---: | ---: | --- | --- |
| absent | ebpf | async_normal | 0 | 60 | 60/0/0 | 60/0/0 |
| absent | ebpf | async_paused | 0 | 60 | 60/0/0 | 0/0/60 |
| absent | ebpf | async_recovered | 0 | 60 | 60/0/0 | 60/0/0 |
| absent | native | async_normal | 0 | 60 | 60/0/0 | 60/0/0 |
| absent | native | async_paused | 0 | 60 | 60/0/0 | 0/0/60 |
| absent | native | async_recovered | 0 | 60 | 60/0/0 | 60/0/0 |
| full | ebpf | async_normal | 0 | 60 | 60/0/0 | 60/0/0 |
| full | ebpf | async_paused | 0 | 60 | 60/0/0 | 0/0/60 |
| full | ebpf | async_recovered | 0 | 60 | 60/0/0 | 60/0/0 |
| full | native | async_normal | 60 | 0 | 60/0/0 | 60/0/0 |
| full | native | async_paused | 60 | 0 | 60/0/0 | 0/0/60 |
| full | native | async_recovered | 60 | 0 | 60/0/0 | 60/0/0 |
| partial | ebpf | async_normal | 0 | 60 | 60/0/0 | 60/0/0 |
| partial | ebpf | async_paused | 0 | 60 | 60/0/0 | 0/0/60 |
| partial | ebpf | async_recovered | 0 | 60 | 60/0/0 | 60/0/0 |
| partial | native | async_normal | 60 | 0 | 60/0/0 | 60/0/0 |
| partial | native | async_paused | 60 | 0 | 60/0/0 | 0/0/60 |
| partial | native | async_recovered | 60 | 0 | 60/0/0 | 60/0/0 |

### Per-attempt semantic confusion

Full calibration/target confusion counts and bounded witness attempt IDs are retained in `results.json`. False positives, false negatives, and source/external unknowns are not absorbed into interval averages.

Recorded campaign elapsed time: 106171.5 seconds. Human/agent time is unmetered and remains unknown.
