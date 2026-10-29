# Iteration 5 observation limits

This note records two mechanisms established from retained iteration-5 evidence. It does not repair or recompute a result, change an admission decision, or claim that one observation source is generally superior.

## Petclinic native endpoint identity

In OBI Petclinic/full main run `40924968145` seed 6, the frozen native raw input contains both `http.route` and `url.path`. Representative retained spans contain route values `customers`, `vets`, and `visits`, while their URL paths are `/api/customer/owners`, `/api/vet/vets`, and `/api/visit/owners/1/pets/1/visits`. The reviewed evidence is `work/main-independent-review/40924968145/6/native-route-examples.json`; each example identifies the original frozen export and its SHA-256.

Pinned Bering 1.3.0 commit `70d4145d3e26f11d8b3fb5be8917c50c1c6d8c2a` selects endpoint path attributes in the order `http.route`, `url.path`, `http.target` in `internal/discovery/discovery.go` (`inferEndpointDetails`). It normalizes the selected route. The retained native graph therefore has gateway endpoint IDs `GET /customers`, `GET /vets`, and `POST /visits`. The external operation contracts ask for the concrete URL paths above, so the saved bindings have no exact entry candidate and retain `entry_endpoint_missing_or_ambiguous`.

This is a representation-and-binding mechanism, not evidence that the native traces lacked the URL information or that native tracing is generally inferior. Selecting or combining another attribute was not evaluated here and is not asserted to satisfy the remaining call, database, or simulation obligations. The original input, graph, binding, forecast, outcome, and independent GO remain unchanged.

## DeepFlow ambient-load circuit breaker

DeepFlow OTel/absent smoke run `40942447288` failed technical acquisition before the selected-agent control on guest A. Its retained node-A agent log records the official `SystemLoadGuard` moving from `Running` to `Disabled` with `melted_down=true` after the `Load15` relative-load check crossed the configured default. Guest B supplied the comparison capture. The failure remains a zero-operation technical attempt with its elapsed and preparation costs retained; it is not application- or protocol-negative evidence.

The retained failed-run evidence is under `work/df-otel-40942447288/absent/`: `compact/observations/final-a-collector.log`, `final-b-collector.log`, the corresponding pre-control logs, `selected/observations/deepflow-agent-standalone-{a,b}.yaml`, and the compact status, evaluation, and cost records. At pinned DeepFlow v7.2.3 commit `9a1219fa5cf1471ba2ec8742019661567d98002e`, `agent/src/config/config.rs` defines `RelativeSysLoad` defaults `trigger_threshold: 1.0`, `recovery_threshold: 0.9`, and `metric: Load15`; `agent/src/utils/guard.rs` performs the load-per-available-CPU check and treats zero trigger or recovery as disabling this guard.

Research commit `6a616c685c10a7e17a80b1dda452d9da9e02a693` serializes explicit zero trigger and recovery values for that ambient-load guard in all DeepFlow arms. It does not alter other guards, collector source, codec, identity rules, workload, or resource envelope. The fixed OTel/absent smoke `40948057864` is still pending, so this note does not claim that the revision succeeded or that the earlier miss had no additional cause. Its emitted runtime YAML and acquisition evidence must be reviewed before that setting is admitted.

