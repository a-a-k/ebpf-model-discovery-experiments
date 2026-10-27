# Retained DeathStarBench coverage diagnostic

This directory copies the output of [audit run 40514548883](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40514548883),
commit `bd83ffe5a4328ce266ed9068e0ec2ffed33f57f3`. Inputs are all nine completed
DeathStarBench cells from [acquisition 40502990432](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40502990432),
commit `19eed302e4f7d1f56d64ba25a8b84c062349b922`.
The audit ran entirely in GitHub Actions. It generated no traffic, fitted no
model, corrected no timestamps and replaced no original forecast.

Each cell file retains input and acquisition-rule hashes, phase/block/operation
partitions, frozen route-class support and bounded early/middle/late witnesses.
Raw timestamp checks use only the SQLite-indexed prefix of each original file;
unindexed tails and duplicate timestamp variants remain explicit. The adjacent
time/cost files cover download and diagnostic processing; the final Actions job
ledger must also include this run. Human/local effort is not measured here.

## Observed mechanism

Each of the nine eBPF cells has a unique pre-window entry for every one of its
34,800 primary attempts and three frozen route classes. All missing automatic
route assignments in these cells are attributed to the timing gate, rather
than missing exact request identifiers or absent frozen route classes.

For example, [absent/3](absent-3.json) records 19 accepted target assignments and
9,581 timing rejections; [absent/5](absent-5.json) records 7 and 9,593;
[full/3](full-3.json) records 689 and 8,911. By comparison,
[absent/4](absent-4.json) accepts all 9,600 target entries.

The [partial/4](partial-4.json) calibration section separately records 13,701 timing rejections;
complete target coverage therefore does not imply complete training evidence.
The selected absent/3 rejected witnesses have source-start minus client-start
differences of -25,999, -2,741,566 and -2,505,887 nanoseconds. Each selected raw
timestamp pair matches its indexed pair. These examples establish temporal
incompatibility with the zero-tolerance host-window gate, not independently
measured clock drift, exporter semantics or collector loss.

## Interpretation and review

Independent review approved the audit's integrity and this limited explanation.
The gate adds an unvalidated cross-clock prerequisite to exact request-identity
attribution. Original forecasts remain measurements of that gated pipeline;
their low coverage cannot be described as absence of the corresponding raw
eBPF events. Recognizing a route still does not establish the operation's
semantic completion, durable database effect or correctness of every downstream
link. This retrospective diagnosis is not a corrected prospective forecast or
evidence that a different model outperforms its relevant baselines.
