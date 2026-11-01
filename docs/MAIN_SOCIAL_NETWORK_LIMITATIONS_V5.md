# Reviewed social-network evidence from all three collectors

This is a subset of the fixed 81-cell study. All nine OBI cases, all nine
Coroot cases and the three DeepFlow absent-tracing cases have passed the
qualified saved-evidence reader and both metadata reviews. The six remaining
DeepFlow social-network cases are technical timeout replacements in progress;
no complete three-collector comparison is claimed here.

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
