# Saved OBI catalog parent diagnosis

Before implementation/execution, the main agent and independent skeptic give
ORIGINAL-feasibility design GO to inspect the two fixed OBI OTel v3 smoke captures:
absent full13017682242/compact13017817219 and partial
full13016551407/compact13016791229, run41132051267 at immutable6ef079a. The
diagnostic branch starts from common capture source
`f60cbfe5e19ca88b40e196d8e793ef0e2aac5d5c`; no capture source is changed.

The original question is whether real eBPF observations can supply useful models
with absent or incomplete tracing. The strongest simple baseline is the literal
original OTLP fields and parent IDs, with the same deployment/operation knowledge.
The strongest cheap combination must also consider genuine unique parent IDs in
the SDK prefix of the same deployment. An encoder-created source-domain split
alone cannot prove that these are independent trace universes or justify a broad
negative applicability claim. No automatic cross-source join is authorized here.

The two modes already differ in their original frozen graph: absent has actual
typed SERVER edges frontend/checkout→product-catalog in addition to CLIENT
dependencies on the Envoy address172.28.11.20. Partial has the CLIENT edges and
catalog SERVER endpoint but lacks those two cross-service SERVER edges, including
in its combined graph. Its PostgreSQL spans/edges are present. In the absent
binding, the PostgreSQL requirement is explicitly assumed fulfilled under the
same declared conditional model once catalog is reachable; partial cannot take
that conditional path while catalog is unreachable. Availability alone therefore
does not diagnose a PostgreSQL decoder failure.

The competing explanations remain raw observation coverage, preserved parent IDs,
duplicate/conflicting observations, or adapter/source-domain behavior. The audit
reads all frozen OBI input requests and their SHA-bound original protobuf bodies,
using the existing literal projection from the saved native-shipping audit. It
retains exact catalog SERVER variants and every literal same-trace parent variant,
with all conflicts and bounded source locators. It compares complete raw/input
field and identity multisets, and binds the actual ordered Bering accepted request
SHA/byte sequence. Original frozen models, quality and bindings are copied as JSON
for interpretation; none are recomputed.

Exact Bering66ca3af derives the internal eBPF domain in
`internal/connectors/ebpf/load.go:69–100` from the configured source ID/domain.
The native OTLP decoder in `internal/connectors/otlp/http.go:114–150` leaves the
Go SourceDomain string empty. `internal/discovery/discovery.go:276–293` includes
that string in the parent key. The audit records both this source-backed
derivation and any exact parent-ID counterparts in the frozen SDK input. It does
not claim to rescan the original native raw prefix, invent parent relationships,
or establish which instrument wrote a trace header. Full literal field variants
are not automatically classified as Bering ambiguity, whose signature omits time.

Routing everything through ordinary OTLP is not an exact full-model substitute:
the eBPF profile also sets SourceKind=ebpf, which affects SERVER-only entry and
gRPC endpoint handling in pinned discovery.go:429–487. A cheap combination must
retain the same observation semantics and entry guards. Any later common-domain
interpretation would require proof of shared scope, retaining source kind and
all ambiguity guards; no such change is implemented by this read-only diagnosis.

Only the existing saved audit script/workflow, fixed declarations and focused
synthetic checks are extended. Full source archives and raw processing stay in
Actions. There is no traffic, Bering replay, model fitting, Sheaft run, new primary
forecast, outcome scoring or admission change. Actual-code GO is required before
dispatch, and actual output must be interpreted before main81 GO. A mismatch is
retained and explained rather than renamed as successful preservation.

Preparation, builds/CI, downloads, failures and early stopping remain in complete
costs; human preparation time is unknown. The same-information direct baseline
is not claimed to cost more. The new common27 may execute independently; main81
remains held for its actual review and this remaining source/baseline diagnosis.

## Actual outputs

Both fixed audits succeeded at diagnostic source
`5e013adecd3d17d569b3ad3c3a6559f15a2d6bab`; CI41145184414 also passed. The
main agent and independent skeptic separately checked artifact API identity,
whole derived ZIP digest and actual retained JSON:

| Mode | Audit run | Derived artifact | Bytes | SHA256 |
| --- | --- | --- | --- | --- |
| Absent | 41145186233 | 13020690613 | 804820 | b0e6a89e9d910f05af2a29fb5a528f58d76d2269fbb95fc3a0e936f939e71119 |
| Partial | 41145190491 | 13020595954 | 992934 | ba2cbbd7aea2db8c154ab678ca5fc95df26e532a788be32d681736566720af4c |

Absent has20 frozen OBI requests,3043 spans and no SDK input. All168 retained
catalog GetProduct SERVER variants have one same-domain parent:95 frontend
CLIENT spans,20 checkout CLIENT spans and53 catalog SERVER spans. Partial has24
OBI requests,3520 spans and1274 frozen SDK input spans. Of172 catalog SERVER
variants,55 have a local catalog parent; the remaining117 have no OBI parent
but exactly one matching SDK input parent each:97 frontend CLIENT and20 checkout
CLIENT spans. Both complete literal-field and trace/span/parent/kind/name
multisets compare exactly between original OBI protobuf and frozen input.

For example, partial trace `2a4b76f71e20090d447112212b9e7314` contains catalog
child `8743ecbc82d67ab4` with parent `86b12fa49485ed11`, an actual frontend
CLIENT span in the SDK input. The SDK input's internal domain is empty; the
eBPF profile's internal domain is
`ebpf-otlp:4:ebpf:otel_demo-deployment`. These are profile annotations, not a
wire-encoded distinction between two proven independent trace universes.

The independent reviewer also checked the complete identity-field counts against
the retained full catalog variants. All168/172 child identities are unique;
their global OBI occurrence totals equal the retained catalog totals, leaving
no hidden OBI variant of those IDs in another service/kind. Retained child and
parent variants contain no conflicting duplicate attributes, including nested
key/value lists. This excludes local child ambiguity as the explanation for the
117 missing local parents. It does not check whether SDK input contains other
variants of the catalog CHILD IDs: that lookup was not emitted by this audit.
No original native raw-prefix rescan is claimed.

Both agents agree that OBI raw-to-input loss does not explain the catalog gap.
A fundamental negative eBPF applicability claim is NO-GO on these facts. The
strongest cheap combination must be considered before main81. Joint ordinary
OTLP decoding is a useful auxiliary baseline, but loses eBPF-specific client-peer
enrichment and changes endpoint candidate rules. A stronger simple comparison
would retain the original canonical graph/endpoints and add only new actual
SERVER-parent edges from the joint view, after complete joint parent/child
ambiguity checks and the same supplied aliases/entry guard. This union is not a
novel contribution; a second Bering pass and all preparation/failures must be
included in costs. No such union, product feature, capture change, new prediction
or primary outcome score has been implemented or approved by these outputs.
Main81 remains held.
