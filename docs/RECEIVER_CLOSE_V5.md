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
