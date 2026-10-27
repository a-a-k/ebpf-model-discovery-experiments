# Bering task: validate and enrich discovery from eBPF-derived OTLP

Status: implementation task, not a completed capability or an experimental result.
Reviewed against Bering v1.0.0 (model/snapshot schema 1.3.0) and Sheaft v1.3.1.

## Purpose and verified gap

The study's intended chain is **eBPF observations -> Bering graph -> Sheaft
simulation -> independently observed application behavior**, with Procrustes
providing the static preflight. Native application tracing may be absent or
partial. The graph must be an input to the calculation.

Bering already accepts raw OTLP and normalized spans, including the format used
by OBI. A new OTLP receiver or a new eBPF collector is unnecessary. Its existing
trace discovery builds cross-service edges from parent/span identities, starts
each service at one replica unless overridden, and does not derive placement or
shared-resource references. It does not synthesize database nodes from DB-client
span attributes. Sources: [trace contract][trace], [loader][loader],
[discovery implementation][discovery].

Extend this existing discovery path to interpret available eBPF evidence and
preserve its limits. Start with actual saved OBI captures; keep the unmodified
OTLP path as the simplest implementation comparison. Reuse existing schema fields
where their semantics fit. Do not require a new input format merely because the
producer is eBPF.

First produce a short field-to-output audit on those captures: what the existing
path already recovers, what is present but unused, and what the collector never
observed. Implement only the demonstrated normalization/enrichment gaps. A new
standalone adapter is an implementation option, not a pre-decided requirement.

## Inputs and required behavior

1. Accept OBI OTLP plus observed host/process/container/network metadata when
   needed. Specify the mapping from actual captured fields. Record collector
   version, capture source and evidence references; keep native and eBPF origins
   distinguishable. Missing fields remain unknown.
2. Recover service dependencies and observed operation identities (HTTP
   method/route, RPC method, or messaging operation when present). Do not equate
   a route with a proven business-operation name or infer mandatory calls from
   their presence alone. Business success contracts are separate declared inputs.
3. Distinguish a service, its observed instances, and their hosts. Use observed
   identities that handle process restarts and address reuse. Distinguish an
   observed instance count from the total configured replica count; a default
   value of one is not evidence of discovery. Preserve cross-host placement.
4. Add database nodes and caller-to-database edges from supported observations,
   including client-only spans. Distinguish a logical database address, a
   namespace, and a physical instance. Merge callers' dependencies only when
   evidence identifies the same resource; otherwise retain unresolved aliases.
   Demonstrate the corner case of two services sharing one database. Do not
   create a physical identity from a missing address or port zero.
5. Distinguish a structural network dependency from a link in a particular
   distributed execution. Confirm execution links using observed unambiguous
   parent/context identities or message identifiers. A common topic, connection,
   or nearby timestamps alone cannot establish an operation's causal chain.
   Preserve conflicts and unsupported protocols explicitly.
6. Do not use cross-host clock containment or an arbitrary elapsed-time cutoff
   to accept/reject identities. Use complete retained batch observations for
   reproduction; disclose capture loss and truncation. Durations may be reported
   without becoming a business-success deadline.

Expected topology, generator operation labels and external success outcomes are
evaluation inputs, not discovery inputs. Procrustes-supplied static identities,
replicas or operation semantics must remain separately attributed manual/static
assistance and be equally available to the native-trace comparison. Do not
present these fields as recovered from eBPF.

## Outputs and integration

- Emit a validated Bering model and snapshot, with evidence/quality sidecars
  explaining inferred identities, unresolved associations and supplied fields.
  Do not repackage uncertain discovery as authoritative `topology_api` input:
  that input's default confidence of 1.0 denotes explicitly supplied topology.
- Preserve the model as the actual input to Sheaft. Use its supported
  `edge_aware`/`required_edges` contracts where the selected operation requires
  those calls. A shared DB represented only by a label is insufficient if
  Sheaft does not use that label in its calculation. [Required-call semantics][calls]
- Keep operation semantics and fault probabilities separate from topology
  discovery. Missing reliability is not automatically one, and an observed
  HTTP error rate is not automatically an independent component-failure rate.
  The live intervention law must match the selected Sheaft model; correlated
  replica states cannot be silently replaced by independent marginals.
- Check the actual Procrustes preflight for an eBPF-only source. If its current
  SDK-specific checks block this source, report a separate, minimal Procrustes
  change for the collection plan. Do not fake native instrumentation or call a
  blocked report successful. Procrustes does not ingest runtime eBPF events.

## Acceptance and deliverables

1. Publish reproducible mapping fixtures from retained captures. Cover ordinary
   OTLP compatibility, two instances on different hosts, a shared DB reached by
   two services, and an ambiguous/unsupported association. Existing native OTLP
   ingestion must continue to work. Fixture graphs alone are engineering checks.
2. Run the actual pinned Procrustes/Bering/Sheaft tools in GitHub Actions on an
   existing application with SDK tracing disabled. Save commands, versions,
   source observations, all handoff artifacts, model, predicate, fault inputs
   and Sheaft output. Identify any static assistance explicitly.
3. Check graph use: an applicable discovered dependency must affect the Sheaft
   calculation when that dependency fails. An edge/node ablation can diagnose
   that use, but acceptance also requires comparing the prediction with
   independently observed application behavior under the matching intervention.
   Include the shared-DB case and distinguish operations that actually require
   the DB from those satisfied by cache or another path.
4. Report prediction errors, uncertainty, unknown cases and comparable costs,
   including preparation and failed runs. There is no invented accuracy or
   completion-time threshold. Pending work is not failure merely because time
   elapsed. A successful format conversion or a changed internal score alone
   does not establish the research contribution.

Deliver the Bering change, focused tests, field-mapping documentation and one
reproducible integration example. Broader protocol support and additional
collectors are outside this task. An adapter cannot recover information absent
from the observations; report that limitation instead of manufacturing links.

The experiment orchestrator owns the full three-system evaluation and its
pending/recovery protocol. This task does not replace that study or authorize
claiming that its main hypothesis has already been validated. The existing
conditional-state forecasts did not consume the recovered graph and therefore
do not validate this toolchain path.

Handoff review (2026-10-27): the orchestrator and independent skeptic agree with
this task scope. The simplest baseline is the existing raw-OTLP Bering path;
the proposed gain is use of observed evidence currently left out of its graph,
tested through external outcomes with the same supplied semantics and full costs.
The skeptic's GO covers task formulation only. Implementation and experimental
success have not received GO for the corrected study.

[trace]: https://github.com/MB3R-Lab/Bering/blob/v1.0.0/docs/trace-input-format.md
[loader]: https://github.com/MB3R-Lab/Bering/blob/v1.0.0/internal/connectors/traces/loader.go
[discovery]: https://github.com/MB3R-Lab/Bering/blob/v1.0.0/internal/discovery/discovery.go
[calls]: https://github.com/MB3R-Lab/Sheaft/blob/v1.3.1/docs/required-calls.md
