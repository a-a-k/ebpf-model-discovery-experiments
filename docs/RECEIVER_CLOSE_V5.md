# Iteration 5 receiver closure boundary

Two OBI OpenTelemetry Demo absent-mode cells in run
[`40930805848`](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40930805848)
failed after completing their training checkpoints and application workload. The
OBI processes stopped cleanly and all receiver acceptance barriers succeeded, but
guest A's receiver had about 1.7 GB of wrapper data to validate and hash. The
parent killed that receiver after a fixed 30-second wait, before it could write
the durable closure checkpoint. Those cells remain technical failures and their
costs remain retained; this is not evidence of an OBI shutdown failure or OOM.

The approved repair removes the artificial deadline only from normal receiver
finalization. The parent sends the normal termination signal and waits for the
receiver to exit. It then applies the same requirements as before: zero receiver
exit status, joined request handlers, valid saved JSONL/raw bytes, and independent
parent hash verification. Waiting is not success, and missing or invalid evidence
still makes the cell technically invalid. The measured closure elapsed time and
absence of a deadline are retained for each receiver.

Best-effort cleanup after another exception remains separately bounded and may
force-kill a process while preserving the original error. The change does not
alter collector shutdown, application traffic, observations, graph discovery,
forecasting, metrics, or acceptance thresholds. It does not retroactively admit
the failed cells. A matching failed-setting repeat requires independent code
review and CI before execution.

A later-finishing OBI OTel partial-mode seed 8 in
[40948072741](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40948072741)
still used the old `6a616c6` code and failed through the same independently
verified branch: receiver A was killed with return code `-9` before its durable
checkpoint, while B/native closed correctly and both OBI collectors exited
cleanly. The original compact `12939626858`, its incomplete evaluation and all
costs remain retained. The exact failed-cell repeat is
[40970638144](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40970638144)
at `7e6b637`, after the existing repair review and successful checks
[40969878243](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40969878243).
This repeat changes no observation, graph, outcome or admission rule, and its
result is pending. No collector-capability conclusion follows from the old
driver's forced termination.

Seed 6 in the same old-source run subsequently failed. Its own compact
`12939228701` independently confirms the same A-only forced closure; the
mechanism was not inferred from seed 8. The exact failed-cell repeat is qualified
under the same existing repair and awaits runner capacity. The retained
[seed-6 diagnosis](../results/iteration-5/diagnostics/receiver-close/partial-seed6-40948072741.md)
and [seed-8 diagnosis](../results/iteration-5/diagnostics/receiver-close/partial-seed8-40948072741.md)
give artifact hashes, receiver/collector evidence, external counts and costs.
