# Petclinic full-mode cross-node evidence audit

This is an exploratory local diagnostic of the retained GitHub Actions capture, not a new scored metric or a research recalculation. It used Petclinic full-mode seed 0 from run `40342667653`, artifact `12663097086` (`campaign-petclinic-full-0-40342667653`), whose downloaded ZIP matched SHA-256 `3c296c3b2b4995945931896825744d966b847c8748df25a43573d06a11201809`.

## Parsing criteria

The audit inspected the retained normalized records and checked their provenance against the raw per-guest files `observations/a.jsonl`, `observations/b.jsonl`, `native/calibration/native-node-a.jsonl`, and `native/calibration/native-node-b.jsonl`. Candidate requests had to satisfy all of these conditions:

- source was `ebpf` or `native`, service was `visits-service`, and the span was a server span (`SPAN_KIND_SERVER` or native kind `2`);
- `http.request.header.x-experiment-request-id` contained exactly one opaque request ID;
- `http.request.method` was exactly `POST` and concrete `url.path` was exactly `/owners/1/pets/1/visits`;
- the key `(request ID, method, concrete path)` selected exactly one Visits server candidate across both guests in each source, and both candidates were on guest B;
- missing candidates, duplicate candidates, retries or multiple matching calls, node disagreement, and method/path disagreement were rejected as unknown; no timestamp, operation label, topic, or deployment-manifest inference was used;
- after binding the two child observations, the independent parent check indexed only native spans by `(trace_id, span_id)` and required the native child parent to resolve to a native span on guest A.

The capture contained 468 unique eBPF candidate IDs (240 on A and 228 on B) and 474 unique native candidate IDs (243 on A and 231 on B), with candidate cardinality one throughout. The criteria bound 228 guest-B requests unambiguously across sources: 222 retained `create_visit` workload steps and six preparation requests. Six native candidates had no eBPF counterpart and remained unknown. All 228 bound pairs shared trace and parent IDs but had different server span IDs, demonstrating that exact cross-source child-span-ID equality is an invalid binder for these two instrumentations.

## Concrete retained example

Request `req-216ac02a86d3f46b02af122d546a122a2ae37445af4c72147307ab23166a4202` occurs in all four raw files named above. Its trace ID is `e421913fb01182c30a51d4a241cf0172`:

- eBPF guest-B Visits server: span `8e1d286ad4df69bc`, parent `c0926c42670f7461`;
- native guest-B Visits server: span `964f2ef4b95abbd1`, parent `c0926c42670f7461`;
- the parent ID `c0926c42670f7461` resolves on guest A only to an eBPF `visits-proxy` client span;
- no native guest-A span has `(trace_id, span_id) = (e421913fb01182c30a51d4a241cf0172, c0926c42670f7461)`.

The same missing-native-parent result holds for all 228 unambiguous child bindings. Native guest A does contain a unique gateway header server in the same trace for each request, but same-trace/header co-occurrence is not exact parent evidence. HAProxy has no independent native span for the propagated proxy hop.

## Interpretation

The current validator's requirement that an eBPF child span ID also exist natively explains one binding failure: equivalent eBPF and Java-agent server observations use different span IDs. Relaxing only that requirement would still not create an independent cross-node reference. After request-based child binding, native exact-parent coverage is `0/228` because the required native guest-A parent span is absent.

Accordingly, the existing scored native-reference coverage of zero remains justified. These diagnostics must not be presented as independent cross-node truth. A future matcher may bind children with the exact opaque-ID/method/path criteria above, but it must preserve ambiguous or missing cases as unknown and must require a native-only parent on the source guest before reporting reference agreement. No matcher was implemented and no saved forecast was changed.
