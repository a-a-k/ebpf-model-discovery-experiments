# Reviewed social-network evidence from all three collectors

All 27 matched social-network cases now have both original actual-evidence
reviews: all three collectors, all three SDK modes and seeds 6/7/8. This completes
the social-network subset of the fixed81 matrix. Three DeepFlow/OTel SDK-absent
cases and the final whole-study report remain due; the social-network cases are
not waiting for a rerun.

OBI and Coroot do not supply the required cross-service Thrift paths in these
actual Bering graphs. Their eBPF operation forecasts remain unknown. Partial
native/combined tracing supports the home timeline; compose and user timeline
remain unsupported. Full native/combined tracing supports all three operations.
The context comparison adds zero edges in these cases and preserves the result.

Coroot partial/6 makes the distinction concrete: both user-timeline replicas
exist in the observed graph and have actual MongoDB/Redis CLIENT edges. Their
aliases map to two distinct replica identities. The required logical SDK group
and its Thrift call paths remain unresolved. The binding reason
`controlled_service_missing_or_ambiguous` therefore does not mean both replicas
or all their database observations are absent. Simply recognizing a replica
does not restore a missing cross-service RPC path.

DeepFlow absent/6 also has nonempty graphs: raw has 28 services, 18 edges and
three endpoints; network scope has 26 services, 15 edges and three endpoints.
The retained edges describe MongoDB/Redis activity. HTTP ingress endpoints are
observed, but the required cross-service RPC links are not represented. All
primary operation forecasts are unknown in absent/6/7/8. This is a limitation
of the tested pinned observations and processing path, not a claim that no TCP
traffic exists or that every collector version cannot decode the protocol.

The twelve newly reviewed DeepFlow/Coroot packets retain 48 available and 168
unknown primary rows; context has 24 available and 48 unknown rows. Their
external outcomes are shared across source/view methods. The extra compose
failure in Coroot absent/8 remains (2799/3200). Unknowns and adverse outcomes
are not technical retry criteria. All preparation, worker, model, simulation,
context, failed-attempt, reader, transfer and retention costs remain.

See the [root twelve-packet metadata review](clean-study-next12-DF-Coroot-DSB-derived-root-review-20261101.json)
and [independent metadata review](clean-study-next12-DF-Coroot-DSB-derived-independent-review-20261101.json).
Literal representative proofs supplement these metadata checks; they do not
replace the qualified Actions checks of every available saved model and report.
See the [Coroot root model/report chains](clean-study-Coroot-DSB-full6-literal-root-review-20261101.json),
[independent chains](clean-study-Coroot-DSB-full6-literal-independent-review-20261101.json),
[root negative graph inspection](clean-study-Coroot-DF-negative-literal-root-review-20261101.json)
and [independent graph inspection](clean-study-Coroot-DF-negative-literal-independent-review-20261101.json).


The completed DeepFlow partial/full repetitions preserve the same negative
eBPF-only finding: none of the three full operation forecasts is available.
Partial native, combined and context support home timeline only (1 versus
3200/3200); compose and user timeline remain unknown. Full native/combined/context
predict .875/1/.875 versus 2800/3200, 3200/3200 and 2800/3200. Extra observed DB
channels do not create an additional primary operation forecast. See the
[completed DeepFlow evidence](MAIN_DEEPFLOW_FINDINGS_V5.md).

The pinned application uses framed binary Thrift for these RPC paths. Required
operation-level calls are absent from the tested collector-to-Bering evidence;
nonempty TCP/HTTP/database graphs do not supply their method, caller and callee
semantics. This observation does not prove that Thrift is undecodable or that
all versions/configurations of these collectors lack support. No specialized
Thrift decoder was integrated or tested in this study. Adding such a decoder
would require a separate matched experiment, not reclassification of these
completed negative results.

HTTP acknowledgements also differ from durable database writes in the pinned
compose adapter. A source audit found that its generated Lua receiver reads a
declared backend ServiceException but does not raise it. The recorded db_down
phase has 7/7 HTTP acknowledgements. The own full/6 phase-end snapshot confirms
the selected user-timeline MongoDB was stopped before restore; it does not prove
continuous downtime for every request. Those acknowledgements cannot establish
7 durable writes. The source mechanism does not establish the actual reply
contents or all repetitions' causes. Existing measured outcomes remain unchanged; see the
[own-case audit and limits](MAIN_DEEPFLOW_FINDINGS_V5.md).
