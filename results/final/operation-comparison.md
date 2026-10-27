# Per-operation comparison

Cells show mean absolute error / mean worst-end error in percentage points across exactly three seeds. Unknown point estimates stay unknown. The full table also records interval width and the conservative target.

| System | Operation | Mode | eBPF | Native | Combined |
|---|---|---|---:|---:|---:|
| deathstarbench | compose_post | absent | 0.00 / 4.01 | unknown / 87.50 | 0.00 / 4.01 |
| deathstarbench | compose_post | full | 0.00 / 4.01 | 0.00 / 4.01 | 0.00 / 4.01 |
| deathstarbench | compose_post | partial | 0.00 / 4.01 | 0.00 / 4.01 | 0.00 / 4.01 |
| deathstarbench | read_home_timeline | absent | 0.00 / 4.58 | unknown / 100.00 | 0.00 / 4.58 |
| deathstarbench | read_home_timeline | full | 0.00 / 4.58 | 0.00 / 4.58 | 0.00 / 4.58 |
| deathstarbench | read_home_timeline | partial | 0.00 / 4.58 | 0.00 / 4.58 | 0.00 / 4.58 |
| deathstarbench | read_user_timeline | absent | 0.00 / 4.01 | unknown / 87.50 | 0.00 / 4.01 |
| deathstarbench | read_user_timeline | full | 0.00 / 4.01 | 0.00 / 4.01 | 0.00 / 4.01 |
| deathstarbench | read_user_timeline | partial | 0.00 / 4.01 | 0.00 / 4.01 | 0.00 / 4.01 |
| otel_demo | add_to_cart | absent | unknown / 12.50 | unknown / 87.50 | unknown / 12.50 |
| otel_demo | add_to_cart | full | unknown / 12.50 | unknown / 12.50 | unknown / 62.50 |
| otel_demo | add_to_cart | partial | unknown / 12.50 | unknown / 12.50 | unknown / 39.10 |
| otel_demo | browse_product | absent | unknown / 12.50 | unknown / 87.50 | unknown / 12.50 |
| otel_demo | browse_product | full | unknown / 12.50 | unknown / 12.50 | unknown / 62.50 |
| otel_demo | browse_product | partial | unknown / 12.50 | unknown / 12.50 | unknown / 13.93 |
| otel_demo | checkout | absent | unknown / 12.50 | unknown / 87.50 | unknown / 12.50 |
| otel_demo | checkout | full | unknown / 13.09 | unknown / 13.09 | unknown / 40.25 |
| otel_demo | checkout | partial | unknown / 12.50 | unknown / 12.50 | unknown / 39.10 |
| petclinic | create_visit | absent | unknown / 42.90 | unknown / 87.50 | unknown / 42.90 |
| petclinic | create_visit | full | unknown / 32.68 | unknown / 32.68 | unknown / 32.68 |
| petclinic | create_visit | partial | unknown / 16.25 | 0.00 / 5.27 | unknown / 16.25 |
| petclinic | list_owners | absent | unknown / 13.10 | unknown / 100.00 | unknown / 13.10 |
| petclinic | list_owners | full | 0.00 / 6.02 | 0.00 / 6.02 | 0.00 / 6.02 |
| petclinic | list_owners | partial | unknown / 13.35 | 0.00 / 6.02 | unknown / 13.35 |
| petclinic | list_vets | absent | unknown / 13.10 | unknown / 100.00 | unknown / 13.10 |
| petclinic | list_vets | full | 0.00 / 6.02 | 0.00 / 6.02 | 0.00 / 6.02 |
| petclinic | list_vets | partial | unknown / 13.35 | 0.00 / 6.02 | unknown / 13.35 |
| petclinic | owner_details_with_visits | absent | unknown / 13.25 | unknown / 87.50 | unknown / 13.25 |
| petclinic | owner_details_with_visits | full | 12.50 / 12.50 | 12.50 / 12.50 | 12.50 / 12.50 |
| petclinic | owner_details_with_visits | partial | unknown / 13.50 | 12.50 / 12.50 | unknown / 13.50 |
