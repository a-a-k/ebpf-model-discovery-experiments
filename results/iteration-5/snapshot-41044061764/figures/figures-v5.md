# Iteration-5 saved error figures

Points and horizontal ranges copy saved worst-end errors and error ranges, converted from fractions to percentage points. Ranges are not confidence intervals. Unavailable errors stay unknown. U is the saved number of unknown external outcomes. An absent seed row means no technically selected cell, not zero error; see the fixed grid. Technical selection is not independent admission. Predictive error alone does not establish a utility or effort advantage; the equally informed direct baseline shares the stated arithmetic. Different source/preparation revisions prevent attribution of cost differences solely to collectors. No averaging, refit or success threshold.

Exact copied values, source hashes, selection and independent-review status: [saved-values-v5.json](saved-values-v5.json).

## Fixed main grid

```json
{
  "blocked_main_cells": [],
  "declared_main_cells": 81,
  "incomplete_or_missing_main_cells": [
    [
      "deepflow",
      "deathstarbench",
      "absent",
      6
    ],
    [
      "deepflow",
      "deathstarbench",
      "absent",
      7
    ],
    [
      "deepflow",
      "deathstarbench",
      "absent",
      8
    ],
    [
      "deepflow",
      "deathstarbench",
      "full",
      6
    ],
    [
      "deepflow",
      "deathstarbench",
      "full",
      7
    ],
    [
      "deepflow",
      "deathstarbench",
      "full",
      8
    ],
    [
      "deepflow",
      "deathstarbench",
      "partial",
      6
    ],
    [
      "deepflow",
      "deathstarbench",
      "partial",
      7
    ],
    [
      "deepflow",
      "deathstarbench",
      "partial",
      8
    ],
    [
      "deepflow",
      "otel_demo",
      "absent",
      6
    ],
    [
      "deepflow",
      "otel_demo",
      "absent",
      7
    ],
    [
      "deepflow",
      "otel_demo",
      "absent",
      8
    ],
    [
      "deepflow",
      "otel_demo",
      "full",
      6
    ],
    [
      "deepflow",
      "otel_demo",
      "full",
      7
    ],
    [
      "deepflow",
      "otel_demo",
      "full",
      8
    ],
    [
      "deepflow",
      "otel_demo",
      "partial",
      6
    ],
    [
      "deepflow",
      "otel_demo",
      "partial",
      7
    ],
    [
      "deepflow",
      "otel_demo",
      "partial",
      8
    ],
    [
      "deepflow",
      "petclinic",
      "absent",
      6
    ],
    [
      "deepflow",
      "petclinic",
      "absent",
      7
    ],
    [
      "deepflow",
      "petclinic",
      "absent",
      8
    ],
    [
      "deepflow",
      "petclinic",
      "full",
      6
    ],
    [
      "deepflow",
      "petclinic",
      "full",
      7
    ],
    [
      "deepflow",
      "petclinic",
      "full",
      8
    ],
    [
      "deepflow",
      "petclinic",
      "partial",
      6
    ],
    [
      "deepflow",
      "petclinic",
      "partial",
      7
    ],
    [
      "deepflow",
      "petclinic",
      "partial",
      8
    ]
  ],
  "smoke_attempts_excluded_from_main_coverage": true,
  "technically_complete_main_cells": 54
}
```

Blocked cells are listed separately within the incomplete/missing grid. A missing campaign is distinct from an available campaign with an unknown forecast.

## coroot / deathstarbench / absent

![Saved per-seed errors](errors-coroot-deathstarbench-absent.svg)

## coroot / deathstarbench / full

![Saved per-seed errors](errors-coroot-deathstarbench-full.svg)

## coroot / deathstarbench / partial

![Saved per-seed errors](errors-coroot-deathstarbench-partial.svg)

## coroot / otel_demo / absent

![Saved per-seed errors](errors-coroot-otel_demo-absent.svg)

## coroot / otel_demo / full

![Saved per-seed errors](errors-coroot-otel_demo-full.svg)

## coroot / otel_demo / partial

![Saved per-seed errors](errors-coroot-otel_demo-partial.svg)

## coroot / petclinic / absent

![Saved per-seed errors](errors-coroot-petclinic-absent.svg)

## coroot / petclinic / full

![Saved per-seed errors](errors-coroot-petclinic-full.svg)

## coroot / petclinic / partial

![Saved per-seed errors](errors-coroot-petclinic-partial.svg)

## obi / deathstarbench / absent

![Saved per-seed errors](errors-obi-deathstarbench-absent.svg)

## obi / deathstarbench / full

![Saved per-seed errors](errors-obi-deathstarbench-full.svg)

## obi / deathstarbench / partial

![Saved per-seed errors](errors-obi-deathstarbench-partial.svg)

## obi / otel_demo / absent

![Saved per-seed errors](errors-obi-otel_demo-absent.svg)

## obi / otel_demo / full

![Saved per-seed errors](errors-obi-otel_demo-full.svg)

## obi / otel_demo / partial

![Saved per-seed errors](errors-obi-otel_demo-partial.svg)

## obi / petclinic / absent

![Saved per-seed errors](errors-obi-petclinic-absent.svg)

## obi / petclinic / full

![Saved per-seed errors](errors-obi-petclinic-full.svg)

## obi / petclinic / partial

![Saved per-seed errors](errors-obi-petclinic-partial.svg)

## Copied per-seed values

| Run | Collector | System | Mode | Seed | Operation | Source | Variant | Available | Saved error | Actual counts |
|---|---|---|---|---|---|---|---|---|---|---|
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970095079 | "coroot" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004270443 | "coroot" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004275773 | "coroot" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "compose_post" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "compose_post" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "compose_post" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "compose_post" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "compose_post" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "compose_post" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "compose_post" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "compose_post" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "compose_post" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "compose_post" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "compose_post" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "compose_post" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004285932 | "coroot" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004281518 | "coroot" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41009954091 | "coroot" | "otel_demo" | "absent" | 6 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41010834860 | "coroot" | "otel_demo" | "absent" | 7 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41011398324 | "coroot" | "otel_demo" | "absent" | 8 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2721, "false": 479, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2721, "false": 479, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "add_to_cart" | "native" | "raw" | true | {"range": [0.024687499999999973, 0.024687499999999973], "worst_end_error": 0.024687499999999973} | {"true": 2721, "false": 479, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "add_to_cart" | "native" | "network_scope" | true | {"range": [0.024687499999999973, 0.024687499999999973], "worst_end_error": 0.024687499999999973} | {"true": 2721, "false": 479, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.024687499999999973, 0.024687499999999973], "worst_end_error": 0.024687499999999973} | {"true": 2721, "false": 479, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.024687499999999973, 0.024687499999999973], "worst_end_error": 0.024687499999999973} | {"true": 2721, "false": 479, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2734, "false": 466, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2734, "false": 466, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "browse_product" | "native" | "raw" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "browse_product" | "native" | "network_scope" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "browse_product" | "combined" | "raw" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 276, "false": 2924, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 276, "false": 2924, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "checkout" | "native" | "raw" | true | {"range": [0.7887500000000001, 0.7887500000000001], "worst_end_error": 0.7887500000000001} | {"true": 276, "false": 2924, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "checkout" | "native" | "network_scope" | true | {"range": [0.7887500000000001, 0.7887500000000001], "worst_end_error": 0.7887500000000001} | {"true": 276, "false": 2924, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "checkout" | "combined" | "raw" | true | {"range": [0.7887500000000001, 0.7887500000000001], "worst_end_error": 0.7887500000000001} | {"true": 276, "false": 2924, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 6 | "checkout" | "combined" | "network_scope" | true | {"range": [0.7887500000000001, 0.7887500000000001], "worst_end_error": 0.7887500000000001} | {"true": 276, "false": 2924, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 189, "false": 3011, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 189, "false": 3011, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 189, "false": 3011, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 189, "false": 3011, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 189, "false": 3011, "none": 0} |
| 41024050638 | "coroot" | "otel_demo" | "full" | 7 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 189, "false": 3011, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "add_to_cart" | "native" | "raw" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "add_to_cart" | "native" | "network_scope" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "browse_product" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "browse_product" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "browse_product" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 1427, "false": 1773, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 1427, "false": 1773, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "checkout" | "native" | "raw" | true | {"range": [0.4290625, 0.4290625], "worst_end_error": 0.4290625} | {"true": 1427, "false": 1773, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "checkout" | "native" | "network_scope" | true | {"range": [0.4290625, 0.4290625], "worst_end_error": 0.4290625} | {"true": 1427, "false": 1773, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "checkout" | "combined" | "raw" | true | {"range": [0.4290625, 0.4290625], "worst_end_error": 0.4290625} | {"true": 1427, "false": 1773, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "full" | 8 | "checkout" | "combined" | "network_scope" | true | {"range": [0.4290625, 0.4290625], "worst_end_error": 0.4290625} | {"true": 1427, "false": 1773, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2686, "false": 514, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2686, "false": 514, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2686, "false": 514, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2686, "false": 514, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2686, "false": 514, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 6 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2686, "false": 514, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2072, "false": 1128, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2072, "false": 1128, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2072, "false": 1128, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2072, "false": 1128, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2072, "false": 1128, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 7 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2072, "false": 1128, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 518, "false": 2682, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 518, "false": 2682, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 518, "false": 2682, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 518, "false": 2682, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 518, "false": 2682, "none": 0} |
| 41004296165 | "coroot" | "otel_demo" | "partial" | 8 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 518, "false": 2682, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40947299209 | "coroot" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 41004291277 | "coroot" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "create_visit" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "create_visit" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "create_visit" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "create_visit" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_owners" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_owners" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_owners" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_owners" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_vets" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_vets" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_vets" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "list_vets" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40956228868 | "coroot" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_home_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 6 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_home_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 7 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_home_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40942429097 | "obi" | "deathstarbench" | "absent" | 8 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "compose_post" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "compose_post" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "compose_post" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "compose_post" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 41005821961 | "obi" | "deathstarbench" | "full" | 6 | "read_user_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "compose_post" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "compose_post" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "compose_post" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "compose_post" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40945578755 | "obi" | "deathstarbench" | "full" | 7 | "read_user_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "compose_post" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "compose_post" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "compose_post" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "compose_post" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40953661709 | "obi" | "deathstarbench" | "full" | 8 | "read_user_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947274375 | "obi" | "deathstarbench" | "partial" | 6 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40947287495 | "obi" | "deathstarbench" | "partial" | 7 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "compose_post" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "compose_post" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "compose_post" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "compose_post" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "compose_post" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "compose_post" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 3200, "false": 0, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_home_timeline" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 3200, "false": 0, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40956239225 | "obi" | "deathstarbench" | "partial" | 8 | "read_user_timeline" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "add_to_cart" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "add_to_cart" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "browse_product" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "browse_product" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "browse_product" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "checkout" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "checkout" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "checkout" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40930805848 | "obi" | "otel_demo" | "absent" | 6 | "checkout" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "add_to_cart" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "add_to_cart" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "browse_product" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "browse_product" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "browse_product" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "checkout" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "checkout" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "checkout" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40958365058 | "obi" | "otel_demo" | "absent" | 7 | "checkout" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "add_to_cart" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "add_to_cart" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "browse_product" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "browse_product" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "browse_product" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "checkout" | "ebpf" | "raw" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "checkout" | "ebpf" | "network_scope" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "checkout" | "combined" | "raw" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 40959052743 | "obi" | "otel_demo" | "absent" | 8 | "checkout" | "combined" | "network_scope" | true | {"range": [0.00031250000000004885, 0.00031250000000004885], "worst_end_error": 0.00031250000000004885} | {"true": 2799, "false": 401, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2701, "false": 499, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2701, "false": 499, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2701, "false": 499, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2701, "false": 499, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.03093749999999995, 0.03093749999999995], "worst_end_error": 0.03093749999999995} | {"true": 2701, "false": 499, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.03093749999999995, 0.03093749999999995], "worst_end_error": 0.03093749999999995} | {"true": 2701, "false": 499, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2697, "false": 503, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2697, "false": 503, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2697, "false": 503, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2697, "false": 503, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "browse_product" | "combined" | "raw" | true | {"range": [0.032187500000000036, 0.032187500000000036], "worst_end_error": 0.032187500000000036} | {"true": 2697, "false": 503, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.032187500000000036, 0.032187500000000036], "worst_end_error": 0.032187500000000036} | {"true": 2697, "false": 503, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2563, "false": 637, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2563, "false": 637, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2563, "false": 637, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2563, "false": 637, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "checkout" | "combined" | "raw" | true | {"range": [0.07406250000000003, 0.07406250000000003], "worst_end_error": 0.07406250000000003} | {"true": 2563, "false": 637, "none": 0} |
| 40966250927 | "obi" | "otel_demo" | "full" | 6 | "checkout" | "combined" | "network_scope" | true | {"range": [0.07406250000000003, 0.07406250000000003], "worst_end_error": 0.07406250000000003} | {"true": 2563, "false": 637, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "add_to_cart" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "add_to_cart" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "browse_product" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "browse_product" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "browse_product" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2800, "false": 400, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2798, "false": 402, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2798, "false": 402, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "checkout" | "native" | "raw" | true | {"range": [0.0006249999999999867, 0.0006249999999999867], "worst_end_error": 0.0006249999999999867} | {"true": 2798, "false": 402, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "checkout" | "native" | "network_scope" | true | {"range": [0.0006249999999999867, 0.0006249999999999867], "worst_end_error": 0.0006249999999999867} | {"true": 2798, "false": 402, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "checkout" | "combined" | "raw" | true | {"range": [0.0006249999999999867, 0.0006249999999999867], "worst_end_error": 0.0006249999999999867} | {"true": 2798, "false": 402, "none": 0} |
| 40966258333 | "obi" | "otel_demo" | "full" | 7 | "checkout" | "combined" | "network_scope" | true | {"range": [0.0006249999999999867, 0.0006249999999999867], "worst_end_error": 0.0006249999999999867} | {"true": 2798, "false": 402, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2749, "false": 451, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2749, "false": 451, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "add_to_cart" | "native" | "raw" | true | {"range": [0.01593750000000005, 0.01593750000000005], "worst_end_error": 0.01593750000000005} | {"true": 2749, "false": 451, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "add_to_cart" | "native" | "network_scope" | true | {"range": [0.01593750000000005, 0.01593750000000005], "worst_end_error": 0.01593750000000005} | {"true": 2749, "false": 451, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "add_to_cart" | "combined" | "raw" | true | {"range": [0.01593750000000005, 0.01593750000000005], "worst_end_error": 0.01593750000000005} | {"true": 2749, "false": 451, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "add_to_cart" | "combined" | "network_scope" | true | {"range": [0.01593750000000005, 0.01593750000000005], "worst_end_error": 0.01593750000000005} | {"true": 2749, "false": 451, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2734, "false": 466, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2734, "false": 466, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "browse_product" | "native" | "raw" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "browse_product" | "native" | "network_scope" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "browse_product" | "combined" | "raw" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "browse_product" | "combined" | "network_scope" | true | {"range": [0.020625000000000004, 0.020625000000000004], "worst_end_error": 0.020625000000000004} | {"true": 2734, "false": 466, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2675, "false": 525, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2675, "false": 525, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "checkout" | "native" | "raw" | true | {"range": [0.0390625, 0.0390625], "worst_end_error": 0.0390625} | {"true": 2675, "false": 525, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "checkout" | "native" | "network_scope" | true | {"range": [0.0390625, 0.0390625], "worst_end_error": 0.0390625} | {"true": 2675, "false": 525, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "checkout" | "combined" | "raw" | true | {"range": [0.0390625, 0.0390625], "worst_end_error": 0.0390625} | {"true": 2675, "false": 525, "none": 0} |
| 40966847000 | "obi" | "otel_demo" | "full" | 8 | "checkout" | "combined" | "network_scope" | true | {"range": [0.0390625, 0.0390625], "worst_end_error": 0.0390625} | {"true": 2675, "false": 525, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2714, "false": 486, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2714, "false": 486, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2714, "false": 486, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2714, "false": 486, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2714, "false": 486, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2714, "false": 486, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2710, "false": 490, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2710, "false": 490, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2710, "false": 490, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2710, "false": 490, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2710, "false": 490, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2710, "false": 490, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2673, "false": 527, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2673, "false": 527, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2673, "false": 527, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2673, "false": 527, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2673, "false": 527, "none": 0} |
| 40971766251 | "obi" | "otel_demo" | "partial" | 6 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2673, "false": 527, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40948072741 | "obi" | "otel_demo" | "partial" | 7 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "add_to_cart" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "add_to_cart" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "add_to_cart" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "add_to_cart" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "add_to_cart" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "add_to_cart" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "browse_product" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "browse_product" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "browse_product" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "browse_product" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "browse_product" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "browse_product" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2800, "false": 400, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "checkout" | "ebpf" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "checkout" | "ebpf" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "checkout" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "checkout" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "checkout" | "combined" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40970638144 | "obi" | "otel_demo" | "partial" | 8 | "checkout" | "combined" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2799, "false": 401, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 6 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 7 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40910013685 | "obi" | "petclinic" | "absent" | 8 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 6 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "native" | "raw" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "native" | "network_scope" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 7 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "native" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "native" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40924968145 | "obi" | "petclinic" | "full" | 8 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 6 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2099, "false": 301, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2099, "false": 301, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 7 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0004166666666666208, 0.0004166666666666208], "worst_end_error": 0.0004166666666666208} | {"true": 2099, "false": 301, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "create_visit" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "create_visit" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "create_visit" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "create_visit" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "create_visit" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "create_visit" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_owners" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_owners" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_owners" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_owners" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_owners" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_owners" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_vets" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_vets" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_vets" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_vets" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_vets" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "list_vets" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2400, "false": 0, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "ebpf" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "ebpf" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "native" | "raw" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "native" | "network_scope" | false | {"range": null, "worst_end_error": null} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "combined" | "raw" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
| 40914709370 | "obi" | "petclinic" | "partial" | 8 | "owner_details_with_visits" | "combined" | "network_scope" | true | {"range": [0.0, 0.0], "worst_end_error": 0.0} | {"true": 2100, "false": 300, "none": 0} |
