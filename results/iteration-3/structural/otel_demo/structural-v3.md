# Iteration 3 structural supplement: otel_demo

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
| absent | 3 | ebpf | 24 | 8 | 4/6 | 64933 | 6 | 0 |
| absent | 3 | native | 0 | 0 | 0/0 | 0 | 0 | 0 |
| absent | 3 | combined | 24 | 8 | 4/6 | 64933 | 6 | 0 |
| absent | 4 | ebpf | 25 | 8 | 4/6 | 65064 | 4 | 0 |
| absent | 4 | native | 0 | 0 | 0/0 | 0 | 0 | 0 |
| absent | 4 | combined | 25 | 8 | 4/6 | 65064 | 4 | 0 |
| absent | 5 | ebpf | 25 | 7 | 7/12 | 64946 | 2 | 0 |
| absent | 5 | native | 0 | 0 | 0/0 | 0 | 0 | 0 |
| absent | 5 | combined | 25 | 7 | 7/12 | 64946 | 2 | 0 |
| full | 3 | ebpf | 25 | 6 | 3/5 | 191785 | 3 | 0 |
| full | 3 | native | 15 | 4 | 0/0 | 74151 | 0 | 981817 |
| full | 3 | combined | 40 | 10 | 3/5 | 265936 | 3 | 981817 |
| full | 4 | ebpf | 23 | 8 | 3/4 | 180050 | 26 | 0 |
| full | 4 | native | 15 | 4 | 0/0 | 69613 | 0 | 932574 |
| full | 4 | combined | 38 | 12 | 3/4 | 249663 | 26 | 932574 |
| full | 5 | ebpf | 28 | 8 | 4/9 | 178027 | 12 | 0 |
| full | 5 | native | 15 | 4 | 0/0 | 68204 | 0 | 916668 |
| full | 5 | combined | 43 | 12 | 4/9 | 246231 | 12 | 916668 |
| partial | 3 | ebpf | 25 | 8 | 4/6 | 192339 | 4 | 0 |
| partial | 3 | native | 14 | 2 | 0/0 | 74167 | 0 | 889228 |
| partial | 3 | combined | 39 | 10 | 4/6 | 266506 | 4 | 889228 |
| partial | 4 | ebpf | 25 | 10 | 4/6 | 187974 | 14 | 0 |
| partial | 4 | native | 14 | 2 | 0/0 | 73599 | 0 | 882544 |
| partial | 4 | combined | 39 | 12 | 4/6 | 261573 | 14 | 882544 |
| partial | 5 | ebpf | 26 | 9 | 4/6 | 186694 | 15 | 0 |
| partial | 5 | native | 14 | 2 | 0/0 | 72670 | 0 | 873530 |
| partial | 5 | combined | 40 | 11 | 4/6 | 259364 | 15 | 873530 |
