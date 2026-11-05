# Fixed main-reader qualification and concrete OTel runtime evidence

This is a three-case evidence review, not the final 81-cell result. The original
question is whether eBPF can replace or complement missing application traces
through actual Bering graphs, actual Sheaft and independent application outcomes.
Cost superiority is not required. Unknown and adverse findings remain results.

## Actual saved-reader qualification

[Uniform review 41240585632](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41240585632)
used reader `e6dff1de1b7326ff68b0379982c3259ee56f9d94` on the same three fixed
original full/compact packets. It issued no traffic, refitting, replay, simulation
or rescoring. Root and the independent skeptic checked actual saved outputs and
gave ORIGINAL-criterion technical/integrity qualification GO.

| Fixed case | Available primary rows | Unknown primary rows | Derived facts SHA256 |
|---|---:|---:|---|
| DeepFlow / DeathStarBench / absent /6 |0|18|`502a93e72ae80e3318335e3d2f1f8365e69ff1516834c72760177839b78364ba`|
| Coroot / OTel / full /6 |12|6|`b53b8b766d18235bfe80944033f07fa62dc3a4b3bd6907e711a242a8698827ac`|
| OBI / Petclinic / partial /6 |20|4|`d65711362c7c555bcc71c1dac52958ae5c4f50f25b349c559ec608e3e5c2a7a2`|

Rows are paired methods/views/operations, not independent repeated trials. All 32
available primary chains bind actual model/input/analysis/predicate/Sheaft
report bytes to the previously frozen forecasts. Conditional numeric DB
predictions, including zero, bind the corresponding saved report state too.
All 28 primary unknowns and every original external outcome remain unchanged.
The separate context comparison has 14 available and 6 unknown rows; here all
available rows reuse existing forecasts with zero added edges. Actual extra
joint-discovery work remains in the cost record.

The [root review record](clean-study-fixed3-uniform-root-review-20261031.json)
and [independent review record](clean-study-fixed3-uniform-independent-review-20261031.json)
retain the actual artifact and report hashes. This qualifies the reader and
these three packets; it does not admit the other main cases or establish utility.

## What failed in OTel checkout

The concrete case is Coroot/OTel/full/6, original
[run 41164826834](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41164826834),
full artifact 13053234263, API ZIP digest
`3eb1312814fa65875541f679e51abea1f9c990ce4fc81994565c4eb347dfc341`.
Review used 25 selected members with individual ZIP CRC and SHA verification,
not a locally downloaded complete campaign ZIP. Their provenance and the
independent literal review are in
[the retained runtime record](clean-study-otel-checkout-runtime-review-20261031.json).

Native and combined checkout forecasts are 0.875, while actual complete-response
success is 800/3200 = 0.25. Unknown outcomes are zero. Even with both catalogue
replicas up, state 11 has 571 successes/1600. This adverse result is retained.

At least two checkout process restarts occurred inside target intervals, in the same
container `2c36897e179adc1779214bee8b0203386df733e8dde665915a503e639862e436`:

| Target | Docker before/after witness | Frontend business-call witness |
|---|---|---|
|target-06, state11|PID91131→275273; new start18:14:21.948586476Z|18:14:21.924481848Z, `ECONNRESET`, saved frontend line18913|
|target-11, state10|PID275273→317030; new start18:23:18.947739938Z|18:23:19.496510699Z, `ECONNREFUSED 172.28.11.42:5050`, line54430|

All times are 2026-10-31 UTC. Docker's actual checkout address is 172.28.11.42,
port 5050. The actual V5 adapter's inherited fault method starts/stops only
product-catalog-a/b; it does not restart checkout. These are uncontrolled runtime
failures of a component the conditional model assumes continuously fulfilled.
They establish a concrete contributor to disagreement, not attribution of every
one of the 2400 failures or a causal effect of Coroot.

Shipping also fails while both catalogue replicas are up. Within target-06,
frontend lines 18330/18341 at 18:13:03 report closed shipping connections;
line 18363 at 18:13:08 reports expected 200/got 408, and line 18374 at 18:13:10 reports
a broken pipe. These are business request errors, distinct from earlier
telemetry-exporter startup failures. Log-line counts are not failed-request
counts. Product-not-found messages after the target phase are not primary-target
evidence.

The rendered checkout/shipping memory limit is 20 MiB with automatic restart, but
the old captures omit `OOMKilled` and `RestartCount`, checkout logs are empty,
and guest kernel diagnostics are unavailable. OOM is therefore unproven. The
running post-restart state and exit code 0 do not identify the earlier cause.
Shipping/frontend/router PIDs are stable in the retained before/after samples.

The actual frontend-proxy image matches the earlier verified image index, with
no entrypoint/command/mount override. Its template exposes the documented 15s
upstream timer, consistent with checkout median 15042 ms; the actual per-request
timer and the cause of all failures remain unresolved. See
[the retained timer evidence](OTEL_RUNTIME_LIMITS_V5.md).

## Later S guest evidence: confirmed PostgreSQL OOM

The completed OBI/OTel/full/6 case at `1d646f9`,
[run 41227096018](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41227096018),
retains actual guest kernel logs. Its guest-a kernel records a memory-cgroup OOM
at 21:07:46 UTC that killed PostgreSQL PID 76474. The exact full Docker container
ID and cgroup match `astronomy-db` in both surrounding runtime captures; PID
76474 is the container's main process before the event. Afterward the same
container has PID 762338 and a new start at 21:08:12.519 UTC.

The rendered limit is 83886080 bytes (80 MiB); the kernel reports usage and limit
of 81920 KiB with `CONSTRAINT_MEMCG`. PostgreSQL logs report unexpected postmaster
exit, startup and automatic recovery. This proves a main-process OOM and container
restart inside target-05, state 10 (21:06:56.901–21:08:31.281 UTC). The deliberate
DB-down probe starts later, at 21:21:37 UTC. The model assumes this required
catalogue database stays fulfilled during the primary replica-only test.

Root and independent review checked 27 selected members by ZIP CRC and SHA, with
full container/PID/guest-boot binding. The
[literal root record](clean-study-otel-obi-full6-guest-oom-root-review-20261101.json)
retains the source artifact identity, exact witnesses and limits of inference.
This does not establish whole-block DB unavailability, individual/all failed
business requests or collector causality. The two catalogue logs are empty;
healthcheck `role root does not exist` lines are not failed business-request
counts. The old Coroot checkout case still lacks evidence proving its restart
cause. All original outcomes and forecasts remain unchanged.

## Coroot full/7 and full/8: separate runtime evidence

The remaining full OTel repeats also retain severe checkout disagreement:
671/3200 and 183/3200 successes against a 0.875 forecast; browse/cart each have
2800/3200. Root and the independent reviewer checked 50 selected original
members by CRC/SHA: container snapshots, configuration and necessary app logs.
Only the two frontend logs use an explicit 6 MiB transport exception; no raw
attempt journal, wire body or original whole ZIP was read locally.

Each case has one unchanged checkout container ID and guest boot but three
successive main PIDs/start times. In full/7, the new PIDs first appear before
target-08 and after target-12. In full/8, they first appear before target-07
and before target-10. These labels describe actual snapshot observations; they
do not place every restart inside active request load. PostgreSQL retains its
same container/PID/start time in all 16 target snapshots of each case.

The frontend logs retain shipping POST failures ending in `broken pipe` and
connection resets near recorded checkout restarts. The primary fault method
only switches the two catalogue replicas. These are concrete noncatalogue
runtime problems, with no attribution of every failed response. The checkout
logs are empty and the old runtime schema omits OOM cause fields. Neither an
OOM cause nor collector causality is established. Guest UTC and runner timing
must not be treated as exactly aligned without clock evidence.

See the [root literal runtime review](clean-study-coroot-otel-full7-full8-runtime-root-review-20261101.json)
and [independent review](clean-study-coroot-otel-full7-full8-runtime-independent-review-20261101.json).
The OBI PostgreSQL OOM above is a separate case; its cause is not transferred
to these Coroot repeats. All original forecasts and outcomes remain unchanged.

## All Coroot OTel and Petclinic metadata in the first batch

Both reviewers checked all nine OTel and nine Petclinic packets under the same
qualified reader. Coroot eBPF operation forecasts are unknown throughout these
18 cases. In Petclinic, absent tracing leaves all operations unknown; partial
native/combined tracing supports owners and vets, while both visit-dependent
operations remain unknown; full tracing supports all four. The eBPF bindings
retain missing required HTTP calls, entry endpoints and reachability obligations.

In OTel, absent and partial tracing leave all operation forecasts unknown;
full native/combined tracing supports all three, with the adverse checkout
results described above. The context comparison adds zero edges and reuses
combined results in all 18 cases. These are observations of the tested pinned
pipeline, not intrinsic collector or cost rankings. All external outcomes,
unknown obligations and processing costs remain.

See the [root eighteen-packet review](clean-study-final18-Coroot-derived-root-review-20261101.json)
and [independent review](clean-study-final18-Coroot-derived-independent-review-20261101.json).

## Scope of interpretation

The fixed DeepFlow social-network packet contains genuine nonempty Bering
graphs, MongoDB/Redis observations and both timeline replica nodes. Required
framed binary Thrift calls are missing and the controlled logical timeline group
is unresolved; observing databases alone does not supply an operation graph.

Coroot's OTel packet contains an actual CLIENT edge with `protocol=http`,
`operation=POST`, route `/oteldemo.ProductCatalogService/GetProduct` and an opaque
peer. This route resembles an RPC method; it does not establish a typed gRPC
decoder result. GetProduct is observed, while the associated SERVER entry and
required channels needed for an eBPF operation forecast remain unresolved.
The fixed OBI Petclinic packet supports all four operations in eBPF/combined;
that packet alone does not rank the three collectors across the complete study.

The same supplied semantics and strong direct AND/OR baseline apply. Matching
equivalent arithmetic is not a novelty or cost-advantage claim. All original,
failed, diagnostic, review, transfer and archival work remains in complete costs;
unmeasured human effort is unknown.
