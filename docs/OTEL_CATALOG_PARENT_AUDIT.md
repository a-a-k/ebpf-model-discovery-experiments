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
