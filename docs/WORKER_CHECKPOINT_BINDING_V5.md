# Exact parent-cell liveness for remote workers

Worker [41008128142](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41008128142)
for Coroot OpenTelemetry Demo/absent seed 7 failed at checkpoint metadata
binding, before download, discovery, forecast freeze or target execution. Its
parent is the nine-cell matrix
[41004296165](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41004296165).

The old workflow required the parent workflow run to report `in_progress`.
GitHub reports this matrix run as `queued` while its currently executing cells
are `in_progress` and later cells remain queued. A fresh reconstruction matched
every immutable field from the dispatched request and failed only that old
run-status condition. The original failing API responses were not retained;
this establishes a reproducible defect in the liveness proxy, without claiming
an exact replay of that earlier API observation. The failed attempt and costs
remain retained.

Before implementation, the root and separate skeptic gave explicit
ORIGINAL-criterion GO for a workflow-only correction. The scientific criterion,
information available to every baseline, raw inputs and calculations remain
unchanged. The strongest simple baseline is the existing metadata binding;
the correction replaces its inappropriate run-level liveness proxy with the
state of the exact parent cell. It makes no scientific or efficiency claim.

The revised check allows a nonterminal parent run to be `queued` or
`in_progress`, and requires one uniquely matching
`campaign (system, mode, seed)` job in the exact parent run and run attempt to
be `in_progress`. Another live cell cannot authorize this worker. Repository,
commit, run attempt, cell, artifact ID/name/digest and source-run bindings remain
checked. Raw API metadata and individual match/mismatch results are retained
before failure. There is no age or elapsed-time heuristic.

Focused tests execute the actual workflow's inline Python. They cover the
queued-parent/live-cell case and reject terminal parents, inactive or duplicate
target jobs, live wrong siblings and changed identities. Exact-code review and
Linux CI must pass before new workers use the correction. No historical failed
attempt is admitted by this change; any replacement is a new technical attempt.

Separate actual-code review returned explicit ORIGINAL-criterion GO. The reviewer
independently ran all 17 inline-gate tests; the root's combined focused suite
passed 46 tests with one skipped. Linux CI remains the publication check.

