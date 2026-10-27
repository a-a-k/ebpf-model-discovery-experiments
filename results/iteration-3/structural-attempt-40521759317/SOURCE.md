# Cancelled structural-reporting attempt

[Run 40521759317](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40521759317)
used commit `865aa8140ccb6967cf2e4d3a1f39ce98888191f7`. Its three jobs were
cancelled during read-only reporting after approximately 27 minutes. All three
uploaded status files record zero completed cells. They are copied unchanged;
their stale `running` value predates process termination, while the Actions
record gives the final `cancelled` state.

This attempt produced no structural result. A synthetic query plan identified
a possible inefficient validity-CTE join; the live runner's plan was not captured.
The reviewed repair changes only the SQL access path. See the
[protocol record](../../../docs/ITERATION_3.md#structural-reporting-access-path-repair).
No acquisition, frozen model or primary forecast is replaced. These jobs remain
in the complete cost ledger and their original artifacts/logs remain retained.
