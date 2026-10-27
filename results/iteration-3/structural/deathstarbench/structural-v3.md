# Iteration 3 structural supplement: deathstarbench

All nine admitted cells are included. Frozen calibration graphs and full-capture parent links are separate.
Full-capture counts include indexed preparation and control observations; they are not primary-attempt counts.
Combined-source nodes are a source-qualified union, not additional physical instances.
Deployment and boot records are evaluation-only references and do not correct observed placement.
No per-request independent structural truth is available; correctness error rate remains unknown.

Projection diagnostics reproduce recorded reasons and flags; they are not independently proven root causes, and overlapping step-reason occurrences are not exclusive causes.
Attempt and step-occurrence denominators are reported separately; absent fields are `not recorded`.

Recorded costs cover input-artifact transfer/decompression and processing only. Complete runner-job, local-compute, and human/agent effort remain unknown.

| Mode | Seed | Source | Frozen services | Frozen DB logical nodes | Frozen/full cross-guest pairs | Missing parent | Ambiguous ID | Unresolved placement |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| absent | 3 | ebpf | 13 | 7 | 0/0 | 4957 | 0 | 0 |
| absent | 3 | native | 0 | 0 | 0/0 | 0 | 0 | 0 |
| absent | 3 | combined | 13 | 7 | 0/0 | 4957 | 0 | 0 |
| absent | 4 | ebpf | 12 | 7 | 0/0 | 4050 | 0 | 0 |
| absent | 4 | native | 0 | 0 | 0/0 | 0 | 0 | 0 |
| absent | 4 | combined | 12 | 7 | 0/0 | 4050 | 0 | 0 |
| absent | 5 | ebpf | 12 | 7 | 0/0 | 2697 | 0 | 0 |
| absent | 5 | native | 0 | 0 | 0/0 | 0 | 0 | 0 |
| absent | 5 | combined | 12 | 7 | 0/0 | 2697 | 0 | 0 |
| full | 3 | ebpf | 12 | 7 | 0/0 | 1709 | 0 | 0 |
| full | 3 | native | 13 | 0 | 0/0 | 0 | 0 | 455416 |
| full | 3 | combined | 25 | 7 | 0/0 | 1709 | 0 | 455416 |
| full | 4 | ebpf | 13 | 7 | 0/0 | 1760 | 0 | 0 |
| full | 4 | native | 13 | 0 | 0/0 | 0 | 0 | 455402 |
| full | 4 | combined | 26 | 7 | 0/0 | 1760 | 0 | 455402 |
| full | 5 | ebpf | 12 | 7 | 0/0 | 2019 | 0 | 0 |
| full | 5 | native | 13 | 0 | 0/0 | 0 | 0 | 455570 |
| full | 5 | combined | 25 | 7 | 0/0 | 2019 | 0 | 455570 |
| partial | 3 | ebpf | 14 | 11 | 0/0 | 3413 | 0 | 0 |
| partial | 3 | native | 11 | 0 | 0/0 | 0 | 0 | 380302 |
| partial | 3 | combined | 25 | 11 | 0/0 | 3413 | 0 | 380302 |
| partial | 4 | ebpf | 12 | 7 | 0/0 | 2955 | 0 | 0 |
| partial | 4 | native | 11 | 0 | 0/0 | 0 | 0 | 380378 |
| partial | 4 | combined | 23 | 7 | 0/0 | 2955 | 0 | 380378 |
| partial | 5 | ebpf | 12 | 7 | 0/0 | 2395 | 0 | 0 |
| partial | 5 | native | 11 | 0 | 0/0 | 0 | 0 | 380455 |
| partial | 5 | combined | 23 | 7 | 0/0 | 2395 | 0 | 380455 |
