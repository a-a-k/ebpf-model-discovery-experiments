# Iteration 4: graph discovery and graph-driven prediction

Current status: all nine Petclinic cells are independently admitted, with the
[generated nine-cell report](../results/iteration-4/SOURCE.md) retained. OTel/full/6
has also passed independent admission: 10/27 cells overall. Its remaining eight
are running; DSB remains incomplete after technical failures.
The full-checkpoint [OTel diagnostic](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40778455040)
completed and passed independent integrity/resource review; its one
[fresh OTel/full/6 replacement](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40786403012)
completed and is admitted;
[DSB](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40780918812)
failed during local Bering ingestion with HTTP 500. Its separate artifact upload
also failed; the exact server error and final integrity proof are unavailable.
DSB's prepared remote-worker changes await its actual diagnostic review and
separate staged-execution decision. A diagnostic cannot resume or complete a
failed campaign.

Earlier qualification failures, repairs and executions remain in the
[run history](RUN_HISTORY.md); detailed original-criterion review decisions are
recorded below. The repaired qualification replay `40674465933` established tool
path integrity for three small captures, not full-size capacity or fresh accuracy.
This protocol supersedes the earlier observation deadlines and accuracy gates.
Historical captures, code and results remain unchanged.

## Original question and decision

Can observations collected without complete application tracing support recovery
of an operation graph whose actual simulation predicts independently observed
application outcomes? The intended contribution is useful model discovery with
less instrumentation work, or better useful information at comparable complete
cost. Merely saving a graph alongside outcome-frequency forecasts does not test
this question. Iterations 1--3 did the latter and are historical diagnostics.

The new executable path is Procrustes static analysis, Bering discovery, then
Sheaft simulation of that discovered graph. External HTTP/body and database
outcomes are evaluation data, never fitting inputs. Graph adequacy is tested,
not assumed. No accuracy threshold, deadline-based success definition or
requirement to outperform an equivalent exact calculation is imposed.

Root design verdict: GO for the original experiment with the assumptions below;
no success claim. Independent 6.1 Sol/xhigh skeptic verdict: **GO for implementation
to test the original criterion**, issued before implementation on 2026-10-28.
This is not a verdict that the usefulness criterion has been met. The reviewer
requires an implementation check before research execution and a result check
before any success claim.

Execution review, 2026-10-28: root and independent 6.1 Sol/xhigh reviewer **GO**
for exactly three full-mode, seed-6 qualification campaigns after
[CI 40653952677](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40653952677).
The check covered the original graph-to-simulation criterion, identical supplied
semantics, the direct baseline/equivalence and full cost limitations. This does not
authorize an empirical success claim. Full-series review awaits actual qualification
artifacts and the final evaluator/cost implementation.

## Versions and product boundary

Original pins for the nine admitted Petclinic cells and admitted OTel/full/6:

| Tool | Source revision |
|---|---|
| Procrustes | `39f76000f8a39c971155e08ebffde829b525911b` |
| Bering | `dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3` (v1.1.1) |
| Sheaft | `686a602f4e7b71f3612f1810885e29dd66c8733a` (v1.3.2) |

Future builds use Bering 1.2.0 at `6f806428509a640a6419058c2ad845ed44db7512`;
the other two pins are unchanged. The adoption and exact historical replay modes
are recorded below. Each cell retains its actual build provenance.

All experimental adaptations, workload semantics, data and reports belong here.
Procrustes is used as its current diagnostic static analyzer. Native and explicit
`ebpf-obi` collection selections retain their own unmodified reports. The eBPF
selection records kernel/protocol coverage as unknown, rather than requiring an
application SDK. Missing custom-driver/Tracetest correspondence and conflicting
replica workload identities may still produce BLOCKED reports; retain them.
Only independently confirmed inventory facts pass into discovery overlays.
Goal-derived endpoint semantics are separately declared inputs, not discovered
facts. A real two-guest technical run checks the agent path; it does not rewrite
Procrustes eligibility. Multi-request operations use one preflight per HTTP step.
Inventory metadata attaches only to nodes already recovered by Bering. Unmatched
inventory stays separate; no inventory node or edge is inserted into discovery.

## Sources, contracts and baseline

Native, eBPF and combined observations receive identical operation contracts,
static replica inventory, intervention vectors and simulation settings. Sources
remain isolated when resolving trace/span IDs. Combining sources cannot create
cross-source parent relationships. Conflicting identities remain ambiguous.
The graph input is **all observations in the source-separated frozen training-file
prefixes**, including records without an entry request ID or connected parent chain.
Cross-host clock containment is never an admission condition. Exact request headers
and source-local ancestry are used separately for entry-alias evidence, classes and
causal-execution checks; they do not filter structural discovery. No evaluator body,
success flag, expected edge list or target-block observation enters discovery.

Retained qualification diagnosis exposed an incorrect precondition in the first
v4 implementation: selecting only descendants of exact entry roots demanded trace
reconstruction before graph discovery. Bering already supports structural L7 client
dependencies without that complete parent chain. Root and independent 6.1 Sol/xhigh
skeptic: **GO under the ORIGINAL criterion** for removing this graph-input filter,
2026-10-28, before replay execution. The causal source is restored access to actual
observed calls, not a supplied edge or a stronger success definition. Native, eBPF
and combined arms get the same training-prefix/background exposure and supplied
semantics; the direct contract/inventory baseline is unchanged. Ambient preparation,
verification and collector traffic may be present and is explicitly retained, so the
global graph is not claimed to contain only the intended operations. A structural
edge does not prove that a particular request executed it. Larger graphs alone are
not success. Earlier filtered diagnostics remain preserved.

Export each source/variant once and reuse the identical bytes in the combined arm.
Run Bering once per source/variant for the observed graph and reuse that verified
output across operation bindings. Bering itself applies each operation overlay in a
separate replay before Sheaft. Charge preparation and all actual replay costs;
references do not create duplicate commands. The current Bering offline batch keeps
all admitted spans in memory, so resource qualification must cover this global input
with the guests running before full-series approval. No cap or silent truncation is
permitted to pass qualification.

Implementation review, 2026-10-28: root and independent 6.1 Sol/xhigh reviewer
**GO for all three retained-capture diagnostics** from original run `40655022146`
using global-input integration `05b5510` and readout correction `9311c10`, after CI.
The check covers shared inputs/role union, actual Bering discovery and overlays,
Sheaft invocation, exact endpoint/RPC binding, conditional DB projection and hash
verification. This is not approval of full-series resource adequacy or a success
claim. The later resource check may stage already-planned cells rather than add
an unrelated scenario grid; that decision awaits these diagnostic outputs.

The global-input retained replay
[40668208749](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40668208749)
at `1d3a7bd` completed for all three systems. Each original-file and index integrity
check passed. Actual Sheaft outputs now exist for all combined OTel/Petclinic
operations, native OTel browse/cart, native Petclinic owner details and eBPF Petclinic
owners/vets. These are fits to qualification captures, not held-out accuracy results.
DSB native entry paths and selected DB fault mappings still exposed representation
errors, so unavailable forecasts are not attributed to collector capability.

Root and independent 6.1 Sol/xhigh reviewer **GO under the ORIGINAL criterion**,
2026-10-28, for the following evidence-bound repairs before the next retained replay:

- Derive a missing entry `url.path` from its actual observed full HTTP URL only on
  an exactly admitted supplied-role root. Preserve original attributes/bytes and
  URL/path provenance; reject contradictory source paths. Never copy the declared
  operation path into an observation.
- Interpret Bering's exact `declared:<supplied-scope>` spelling and retain its raw
  value. Relative observed HTTP route names use Bering's leading-slash spelling,
  only with the existing exact request/root and concrete URL checks.
- Read transparent-proxy names from the retained deployment inventory. Prefer a
  direct observed channel; otherwise require a unique observed path through the
  declared proxies. Record the rule and alternatives. This is justified only while
  those proxies are fixed fulfilled; no expected edge is inserted.
- Compile distinct observed DB aliases together only when every candidate belongs
  to the same explicitly mapped stopped-container fault group. Preserve all nodes,
  typed edges and scopes; no physical-identity discovery or graph merge is claimed.
  Whole-endpoint faults make these channels coextensive. A selected DB-down forecast
  requires the relevant mandatory channels and mapping; missing requirements for
  other DB systems may retain the same explicit fixed-fulfilled condition. Global
  DB completeness remains a separate field. Unattributed same-system requirements
  remain unknown. The manual inventory baseline receives the same assumptions.
- Resolve DSB entry representations only with the retained Compose mount → nginx
  loader → Jaeger service-name proof and file hashes. Try only observed aliases and
  substitute only their entry/caller role. Keep all candidate bindings and select
  the sole supported one, or declared order after agreement of the complete exact
  state vector and known DB forecasts. Conflicting predictions stay unknown; mixed
  DB coverage remains unknown for that intervention. Neither graph IDs nor edges
  change, and the entry remains fixed fulfilled, outside controlled-replica faults.

Each source arm and baseline receives these supplied identity/fault-group facts.
The repairs change compatibility and documented conditional interpretation, not
the original usefulness criterion. Their preparation and replay costs remain part
of the work; no scientific success follows from improved binding coverage.

Concrete implementation review: root and independent 6.1 Sol/xhigh reviewer
**GO for a further retained replay of all three systems** at `642f61f`, after
[CI 40674218814](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40674218814).
The review checked entry candidate preservation and complete state-vector agreement,
exact configuration hashes, DB grouping, proxy/scope/URL repairs and equal baseline
knowledge. The Linux child-resource wrapper is included; it forwards graceful
termination and retains Bering-only RSS/CPU/wall/exit evidence. Full-series resource
adequacy and external predictive accuracy remain unestablished.

Retained replay outcome (`40674465933`, artifact `12811247145`, API-advertised ZIP
SHA-256 `565a58b1b7f5ad8ae26229a6896e2927b6b0f4eaf6eae510871cd622135bd3b0`):
each system's `readout.json` reports `integrity.ok=true`. Both variants now give
native and combined DSB primary forecasts; eBPF-only DSB remains unknown because
required calls are absent. OTel native browse/cart and all combined operations
have primary forecasts; native checkout and eBPF-only operations remain unknown.
All Petclinic primary operations have forecasts for each source. In the supplied
network-scope variant, each source's Petclinic DB-down forecast is zero for owners,
details and create-visit; cached vets stays unknown. Unscoped DB-fault mappings and
DSB/OTel DB-fault predictions remain unknown. No fresh-outcome accuracy claim is made.

Retained OTel diagnosis: supplied network scope maps the observed logical
PostgreSQL endpoints, but product-catalog also has edges to `unresolved_alias`
nodes with an address and no port. Those nodes cannot be proved coextensive with
the selected whole-endpoint DB fault group. The resolver retains unknown instead
of merging them. The descriptive SQL operation hint is not used in DB matching;
it is not the cause. This limits the current evidence/resolution path, not every
possible eBPF collector or identity-resolution method.

The same readouts retain isolated Bering child RSS, input counts and exit status.
For example, combined/network_scope discovery ingested 28,490 raw observations
with 141,128 KiB peak RSS in DSB; 13,752 with 180,796 KiB in OTel; and 6,091 with
102,624 KiB in Petclinic. These are individual small-replay measurements, not
concurrent VM measurements or full-series memory bounds. Raw duplicates count
toward Bering's input buffer; unique indexed spans cannot substitute for that cost.

First-stage execution decision: root **GO** and independent 6.1 Sol/xhigh skeptic
**explicit GO for the ORIGINAL criterion**, after reviewing the above artifacts
and green implementation checks
[40704172324](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40704172324).
Execute `system=all, mode=full, seed=6, max-parallel=3` as the first three of the
27 planned cells, with the complete unchanged protocol. Retain valid cells
regardless of accuracy or unknown coverage. The remaining 24 follow review of
these cells' resource and protocol validity. This is permission to attempt the
standard-runner workload, not a capacity certification. Preserve raw multiplicity,
child and VM resources, all costs and incomplete intents; technical resource
failures remain unscored unknowns. No paid runner, shortened acquisition, input
cap, reduced trial count or accuracy selection is authorized by this decision.

### First-stage infrastructure loss and technical repair

In first-stage run `40704758284`, OTel and Petclinic runners received shutdown
signals (exit 143) during Bering discovery. Their always-run retention/upload steps
were skipped, leaving no campaign artifacts. Job logs retain completed training
blocks and the discovery start: OTel eBPF/raw had 947,706 observations and
540,646,862 wire bytes; Petclinic combined/raw had 563,661 observations and
378,274,206 bytes, after its separate-source models and simulations ran. These
are technical losses, not evaluated predictions. The logs/annotations do not
establish OOM; memory pressure is a hypothesis. DSB was still running when this
repair decision was recorded and is not canceled or replaced on elapsed time.

Root **GO** and independent 6.1 Sol/xhigh skeptic **explicit ORIGINAL-criterion
design GO** for this repair, followed by implementation review and CI before
rerunning only technically failed cells:

- Retain a closed training checkpoint before discovery: consistent SQLite backups,
  indexed raw prefixes and exact wire bodies, hashes, plans, journal, external
  training observations and tool/deployment provenance. Upload it before releasing
  the same campaign process and live guests. Upload failure aborts technically;
  ready/release markers bind run, cell and manifest hash. No fresh-host target resume.
- Stream the identical hashed wire files to Bering, preserving content length and
  encoding. All observations, one-batch semantics and ingestion checks stay intact.
- Add 8 GiB swap on the standard runner's local disk, with explicit allocation
  failure and retained disk, I/O and timing evidence. No paid runner is selected.
- Stream concise resource evidence to job logs. Prefer the Bering child as an OOM
  victim using Linux `oom_score_adj=+1000`, recording readback; this is best-effort
  host protection, not a memory/input cap or proof that memory caused the shutdown.

Checkpoint creation, upload/hold, swap and failed-run costs remain part of the
experiment. No observation cap, deduplication, shorter discovery window, reduced
trial count, experimental deadline or weaker outcome contract is introduced.
At this repair decision the remaining 24 cells awaited staged review; the later
per-system scheduling and Petclinic admission decisions below supersede that wait.

Implementation decision at `ea2e278e50f64bd50597c243d84f834be1b92576`: root **GO**
and independent 6.1 Sol/xhigh skeptic **explicit ORIGINAL-criterion execution GO**
for only OTel/full/seed6 and Petclinic/full/seed6 technical retries. Linux CI
[40718306225](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40718306225)
passed all 413 tests, including the actual supervisor/checkpoint handoff and both
Linux process-group cleanup cases. Exact wire and referenced metadata retention,
same-live-process continuation and separate creation/upload-hold costs were reviewed.
This is permission to measure the unchanged experiment, not evidence of sufficient
capacity or successful predictions. Original DSB remains running; any valid result
is retained irrespective of accuracy or unknown coverage.
The two retries were dispatched at this exact reviewed commit: OTel
[40718665137](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40718665137)
and Petclinic [40718674400](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40718674400).

Scheduling update after the user's request to accelerate execution: root **GO**
and independent 6.1 Sol/xhigh skeptic **explicit ORIGINAL-criterion GO** permit
each system's remaining eight planned cells after its own staged cell passes the
same integrity/resource review. Other systems need not finish first. All valid
outcomes and unavailable forecasts remain admissible; inputs, counts and tools
are unchanged. Select absent/all seeds, partial/all seeds, full/7 and full/8 to
avoid duplicating the staged full/6 cell.

The same review gives **GO now** for the DSB/full/6 technical retry. Its original
acquisition step is explicitly completed/failure at 16:44:08 UTC; all subsequent
retention/evaluation/upload steps are skipped, no step is active and no artifact
exists. This establishes a failed acquisition attempt even though GitHub has not
finalized its outer job. The original job remains monitored and its available
logs/costs will be retained; no elapsed-time cancellation or OOM inference is made.
The reviewed scientific implementation `ea2e278` is unchanged through `3e70887`.
The DSB retry was dispatched at `3e708879889eac8a238027a4640466fc8a76eca5`
in [40731158179](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40731158179),
after successful CI `40730137143`.

Petclinic staged admission: root **GO** and independent 6.1 Sol/xhigh skeptic
**explicit ORIGINAL-criterion GO** admit full/6 run `40718674400` and its remaining
eight planned cells. Saved evaluation confirms 34,800 primary and 9,600 target
operations with exact phase/state counts, matching plans/census, unchanged frozen
hashes and pretarget forecast ordering. All 30 Bering replays and 62 tool commands
completed; same-process cleanup and measured swap/checkpoint costs are retained.
Accuracy is not an admission gate. Raw/conditional DB unknowns remain retained.
This authorizes continuation of the unchanged series, not a general success claim.
The remaining Petclinic cells were dispatched at `4276ea9`: absent/6–8 in
`40733841068`, partial/6–8 in `40733846961`, full/7 in `40733852492` and full/8
in `40733858113`. The admitted full/6 cell is not repeated.

Petclinic completed admission: root and the independent reviewer admit all nine
planned cells. Each retains 34,800 primary and 9,600 target operations, exact
phase/state counts, unchanged pretarget freezes and actual Bering/Sheaft outputs.
All three absent-mode runs have disabled native JVM instrumentation and zero
native spans; all three partial-mode runs disable both Visits replicas while
preserving the other services' native instrumentation. The generated nine-cell
report is run `40751134324`. Equivalent direct-baseline forecasts, unavailable
native paths, conditional/raw DB unknowns, weaker absent-mode downstream classes,
and unmeasured manual costs remain visible. This is admission of one system's
planned empirical evidence, not cross-system or full-cost success.

After OTel retry `40718665137` lost its continuation and skipped final retention,
the already uploaded training checkpoint `12830934533` remains available. Root
and independent 6.1 Sol/xhigh skeptic give **ORIGINAL-criterion design GO** for
one diagnostic replay on a separate standard Actions runner. The hypothesis is
only that the exact retained full-size input can identify a reproducible tool or
resource failure; the interruption's cause is not assumed. The useful-result
criterion, source comparisons and direct baseline remain unchanged.
Verify the checkpoint identity/manifest, every consumed prefix and referenced
body/metadata, SQLite and pinned-binary hashes, and the actual 600 class-training
plus four 6,000-attempt calibration blocks. Relocate only copied index file paths,
proving unchanged span/link rows; use the same exporter and Bering configuration.
Retain transfer/preparation costs, memory/disk evidence and tool exits, drops and
publication counts. No traffic or target continuation is permitted. This replay
cannot complete the interrupted cell, prove capacity alongside live VMs, identify
the original cause merely by succeeding, or support a usefulness claim on its own.
Implementation review precedes execution. No OTLP splitting or model optimization
is approved by this diagnostic decision.

Diagnostic execution: root and independent reviewer **GO** at `0c75e0d`, after
Linux CI `40741796026` and independent focused checks. Validation mirrors actual
dispatch: preparation records are retained separately, and legitimate unissued
HTTP-step suffixes are not required. The single diagnostic is
`40742060084`; it does not replace or complete OTel/full/6.

The standalone diagnostic completed with unchanged checkpoint bytes, all six
shared Bering discoveries, fourteen available operation overlays and fourteen
Sheaft commands completing. Its retained process report records 24:43.04 elapsed
and maximum RSS 13,678,344 KiB on a runner with 16,766,414,848 bytes of RAM. This
establishes standalone feasibility, not the cause of the lost co-located runner.

Root and independent 6.1 Sol/xhigh skeptic give **ORIGINAL-criterion design GO**
for a separate standard Actions worker for the planned OTel/full/6 replacement.
The original supervised campaign and its same two guests stay alive. The worker
receives only the exact closed training checkpoint, inventory, contracts and
pinned binaries, restores verified paths inside its workspace, and returns the
complete actual toolchain evidence, including unavailable branches. Parent run,
attempt, cell, scientific checkout, checkpoint artifact/manifest and worker
run/attempt/output hashes bind the handoff. The parent verifies a separate staging
directory before atomic import, fits classes on its unchanged training index and
saves the complete forecast freeze before any target request. No cross-host
campaign resume or later observation input is permitted.

Reserve execution capacity for workers: initially dispatch only this one repaired
parent; subsequent scheduling must leave worker slots rather than filling the
account with waiting parents. Parent wait/idle-guest time and worker preparation,
transfer, compute, storage and failed attempts remain separate measured costs;
their overlapping wall times are not a new efficiency claim. Sources and the
direct equal-information baseline are unchanged. No deadlines, observation
filtering, paid runner tier or product changes are introduced. Implementation
review precedes dispatch; the already planned full/6 cell supplies the resource
confirmation without another qualification grid.

Implementation decision: root **GO** and independent 6.1 Sol/xhigh skeptic
**explicit ORIGINAL-criterion execution GO** for this one OTel/full/6 replacement
through `eaa9a8d`, included in `72133c00df3f7e4150a3f737dee33e4bee12527d`.
Linux CI `40754244720` passed at that exact dispatch head. Review repaired actual
artifact digest spelling and ZIP-restored executable modes before new acquisition.
The parent proves the same logical training index before and after worker wait;
the worker reads an immutable index and returns all actual toolchain branches.
The subsequent report must list the child worker run as series compute alongside
its parent, including its job/artifact costs; parent wait overlaps that compute.
This is authorization of the existing planned replacement, not empirical success
or permission to skip its staged integrity/resource review.
The replacement was dispatched as run `40754529169` at that reviewed head;
the two preceding failed OTel attempts and the diagnostic remain retained.

Before changing the verifier for future planned runs, root and the independent
reviewer give **explicit ORIGINAL-criterion design GO** for sequential index
verification. On the three pinned ordinary-rowid tables, hash `rowid` and every
column in rowid order, retaining schema hashing and SQLite integrity checking.
SQLite backup preserves those IDs; this adds physical-row identity to the full
content proof. The existing digest-ordered query uses an index followed by
nonsequential full-row reads, confirmed by a synthetic query-plan inspection.
The proposed change avoids that access pattern without changing observations,
graph construction, simulations or selection. Parent and worker must use the
same implementation/proof definition. Backup equality and value/add/delete/rowid
mutation checks precede use. The live run remains unchanged; its waiting time
does not establish this query as the actual bottleneck or prove a cost advantage.
Implementation `1c26956` received root **GO** and independent **explicit
ORIGINAL-criterion implementation GO** after exact-head Linux CI `40765148985`.
Synthetic tests cover consistent WAL backups, full content/schema/rowid mutations
and sequential plans for the actual verification queries. This repair applies
only to future planned runs after staged admission; it does not repeat or change
parent `40754529169` or its worker `40764150238`.

After worker `40764150238` failed before its parent imported forecasts, root and
the independent 6.1 Sol/xhigh reviewer give **explicit ORIGINAL-criterion design
GO** for exactly one standalone diagnostic of the new complete checkpoint.
The fixed source is parent `40754529169` at `72133c00df3f7e4150a3f737dee33e4bee12527d`,
training artifact `12847933267`, archive SHA-256
`ba0289fd1e0cefd4be96cfbf0a0ac4a335db2ef4f748de4b0ffa63aa00c2c422`,
manifest SHA-256 `b90d303797e4285d16659b4515195b0fc58276d8d4200ec6a9fa9eae070e333c`.
Its saved index reports 1,695,697 observations, more than the earlier successful
diagnostic's 1,066,513; that smaller replay did not establish this input's capacity.

Hypothesis: earlier collection of temporary Go allocations can reduce resource
pressure enough to execute the unchanged complete graph/simulation chain on the
standard runner. The strongest simple repair is Bering-child-only
`GOMEMLIMIT=12GiB`, with default `GOGC` unchanged and retained `gctrace` evidence.
This target leaves headroom on the approximately 16 GiB runner; it is not an
observation limit, RSS guarantee, accuracy gate or experimental deadline. The
[Go GC guide](https://go.dev/doc/gc-guide#Memory_limit) documents the soft limit,
possible overshoot and increased CPU use. Bering retains the full span window
and overlapping discovery indexes, so the live set may itself remain too large.
The failed worker's memory/swap pressure and exit 143 do not prove an OOM kill.

Keep the pinned binaries, every observation and source branch, declared contracts,
source comparisons and strong direct baseline unchanged. Verify the complete
checkpoint before and after use. Retain preparation, transfer, GC/CPU/wall time,
RSS, swap, failed-run costs and unknown branches. No fresh application traffic,
resume of the dead parent, completed-cell admission or remaining-eight rollout
is authorized by this diagnostic. Implementation review and CI precede its single
execution; a completed diagnostic would still require a fresh staged campaign.
Both agents' verdicts are GO for this technical check of the original criterion,
not for a substitute contribution or a success claim.
Implementation `5d1d3f35951fe99753c17cbdd80d53d7b9d8f877` received root GO and
independent **explicit ORIGINAL-criterion implementation GO**, with 14 independent
focused synthetic tests passing and exact-head full Linux CI `40778323259`
successful. The single execution is `40778455040`. Bering records inherited and
effective Go settings; a bounded live heartbeat also preserves recent GC lines
in Actions logs if final uploads are lost. The earlier diagnostic remains a
separate immutable default profile. No result is assumed at dispatch.

While diagnostic `40778455040` is live, root and the independent reviewer give
**explicit ORIGINAL-criterion design GO** to prepare and test the same child-only
GC profile in the future remote worker. Apply it equally to every Bering source
and variant, preserve the default GOGC and other tools' environments, and retain
requested/effective settings and full costs. The causal engineering hypothesis,
full input, source comparisons and direct baseline are unchanged. This approval
does not authorize new traffic: first require the diagnostic's actual integrity
and resource review, then separate execution GO for one fresh planned OTel/full/6
replacement. Its admission still precedes the remaining eight OTel cells. Local
Petclinic/DSB execution and currently running jobs are unchanged.
Prepared integration `d99862bf02189b4125bc708443b80f441f240e7a` received root GO
and independent **ORIGINAL-criterion implementation/code-and-docs GO** after
25 focused synthetic checks passed (one Windows executable-mode check skipped)
and exact-head Linux CI `40779398938` succeeded. The synthetic worker tests exercise
success and failure through restore, immutable checks, scoped settings and output
retention; they do not establish actual resource capacity. Activation remains
subject to the diagnostic and staged-execution decisions above.

DSB run `40731158179` has a terminal failed continuation step (22:25:38 UTC),
with final cleanup, evaluation and uploads skipped. The outer job was still
finalizing and its log/annotations unavailable when this decision was made;
neither failure cause nor last completed scientific phase is inferred. Root
and independent 6.1 Sol/xhigh reviewer give **explicit ORIGINAL-criterion design
GO** for one parallel standalone diagnostic of its fixed training checkpoint.
Use artifact `12843610949` (2,300,389,036 bytes), archive SHA-256
`8689c137f482d5ffef5a184762c7f212a5d35f22ea6d014b0d06984788cafed0`,
source `3e708879889eac8a238027a4640466fc8a76eca5`, manifest SHA-256
`8a518c3edbfb4f6904ece3b344c85f211cd55bd909cd0629f4a5f29303948235`.
The saved index reports 702,494 observations. Keep the entire checkpoint,
including its 9,437,769,728-byte journal, and verify the exact 600 + 4x6,000
training plans and all original file hashes before/after use. Bind the profile
to `deathstarbench` and its real declaration, with the same pinned toolchain,
all branches, contracts and direct baseline.

This tests engineering feasibility on a separate standard runner without live
guest contention, using the same one child-only 12 GiB GC target and GC logging.
That setting is still empirically unproven; no parameter search, observation
reduction or paid tier is introduced. Full preparation, transfer, disk, memory,
GC/CPU/wall and failed-run costs are retained. Implementation review and CI
precede the single execution. It cannot resume or complete the failed campaign,
prove shutdown causality, or authorize any new DSB acquisition.
Implementation `65843e5e5a387e40b19547bcae06c87e657911af` received root GO and
independent **ORIGINAL-criterion implementation GO**. Independent focused tests
passed (28 checks, one Windows executable-mode skip), and exact-head Linux CI
`40780702510` succeeded. The single DSB diagnostic was dispatched as
`40780918812`; it has no application traffic or campaign-resume path.

Root and the independent reviewer also give **explicit ORIGINAL-criterion design
GO** to prepare future DSB series routing through the existing exact remote
worker. Petclinic remains local; all inputs, contracts, baselines, source branches,
parent ownership, immutable binding and freeze-before-target checks are unchanged.
The preparation includes system-binding checks and retains worker-slot reservation
and parent-wait/worker costs. No new acquisition follows from this decision:
require actual DSB diagnostic integrity/resource review and separate execution GO
for one fresh full/6 cell, then its admission before the remaining eight. This
does not establish contention as the earlier failure cause.
Prepared routing `017bfba4eeadd9cd7682392e993ae17e07818ed3` received root GO and
independent **ORIGINAL-criterion implementation/preparation GO**. Independent
focused checks passed (28 checks, three Linux-only checks skipped on Windows),
and exact-head Linux CI `40781856208` succeeded. Actual supervisor argument flow
and synthetic worker success/failure were checked for both system declarations.
This remains preparation approval, not acquisition authorization.

Actual OTel diagnostic `40778455040` received root GO and independent
**ORIGINAL-criterion actual-diagnostic GO**. The saved evidence binds the complete
1,695,697-observation checkpoint and pinned binaries, verifies 603 original files
unchanged, and retains exactly 24,600 training attempts plus 15 preparation
operations. All 16 Bering executions completed with one publication, exact source
counts and zero dropped observations; all saved tool commands succeeded, including
10 actual Sheaft analyses with 100,000 trials. All source/variant branches remain:
eBPF-only leaves all three operations unknown; native supports browse/cart but
leaves checkout unknown; combined supports all three. Selected members were
independently rehashed locally; the complete original output archive is retained
in [data-40785555784](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40785555784).
The 1,737,726,417-byte output artifact is `12858178880`, SHA-256
`30b04998fc56833d79327a990ecf7210ea674dcab4c85e47ed01b51de51064d8`.

Stored GNU time reports 50:21.52 elapsed, user/system CPU 4,106.62/267.27 seconds,
maximum RSS 12,557,636 KiB and exit zero. Effective Bering settings are the declared
12 GiB soft target with GC logging, with GOGC unset. This demonstrates feasibility
for the exact retained input; it does not identify the previous shutdown cause,
establish universal capacity or predictive accuracy, or admit a tenth cell.

Root and the independent reviewer separately give **explicit ORIGINAL-criterion
execution GO** for exactly one fresh planned OTel/full/6 technical replacement.
It was dispatched as `40786403012` at `a0e7644362a4e1ac5913f33f06a9570f2a780000`
after exact-head Linux CI `40785779972` succeeded. Keep the 34,800-attempt design,
same binaries/contracts/baselines, unknown and negative outcomes, live parent
guests, verified worker import and pretarget freeze, reserved worker capacity,
and complete parent/worker costs. Remaining eight OTel cells await its actual
admission. No Bering product optimization or additional release is required by
the successful diagnostic at this point.

Bering receives actual observations. Required semantic calls are resolved against
its output; they never create missing edges. Missing or ambiguous required service
paths produce an unavailable prediction with a reason. The observed graph is analyzed
using Sheaft external edge-aware predicates, including exact recovered edge IDs
when separate calls to a shared dependency must both be required. An observed
call is not automatically a mandatory call.

A declared mandatory DB channel is compiled into its recovered typed edges. Under
this protocol's node/whole-endpoint failures and live-edge probability one, those
edges share exactly the same availability; their conjunction is equivalent to one
channel witness. This does not infer that every observed SQL/Redis command is
mandatory. The binding records this basis; individual edge or command failures
would require different semantics. Missing or ambiguous channels remain unknown as
structural findings and for DB interventions; the primary conditional projection is
defined separately below.

Qualification diagnosis exposed an unnecessary admission rule: requiring every DB
channel to be observed before predicting replica-only interventions, although the
primary conditional model assumes nonintervened DB requirements are satisfied.
For this primary target, an unobserved DB requirement can be a fixed satisfied
factor, explicitly recorded as an assumption rather than a recovered dependency.
This means fulfillment of the DB requirement, not merely a process accepting TCP.
External response/body/SQL mismatches still test this assumption. Required observed
service paths and entry evidence remain mandatory; the full observed graph stays
intact. DB-down predictions remain unknown without the relevant observed required
channel and fault-target mapping. This rule applies equally to every source arm
and the direct baseline. Primary forecast availability does not establish DB-model
completeness.

Root and independent 6.1 Sol/xhigh reviewer: **GO for this explicitly conditional
projection under the ORIGINAL criterion**, 2026-10-28, before fresh-series execution.
It follows the declared topology-only assumptions and does not repair missing
Thrift/service paths or prove business completion. Costs and external outcomes are
unchanged; original failed replay outputs are retained. No empirical-success claim.

The reviewer also approved supplied receiver-role normalization for exact bound
untyped nginx HTTP entry spans. Original bytes and missing kind are retained;
derived selected inputs record the supplied SERVER role and its rule/identifiers.
Explicit CLIENT roles and conflicting evidence are never overridden. The same
policy applies to declared receiver evidence across sources. This is manual
semantic enrichment, not newly observed telemetry, and creates no downstream edge.

Compare raw observation discovery with explicitly attributed static/network-scope
enrichment, and native/eBPF/combined graphs through the same tooling. Include the
same released Bering revision in every arm. The `raw` and `network_scope`
variants differ only in explicitly supplied network scope during discovery. Both
receive the same separately attributed confirmed static facts and controlled
placement inventory for simulation. Unaugmented Bering graphs are also retained;
configured replicas and fault placement are not claimed as autonomous recovery.
Save that additional evidence and the exact transformation rule. Include the
direct source-contract plus inventory calculation where applicable. For a single
controlled two-replica service with all other components held live, that baseline
can reduce to A OR B and be exactly equivalent to the graph prediction. The
manual call audit already contains semantic dependency knowledge; its preparation
cost is charged to every method using it. No novelty or predictive superiority
is claimed for Monte Carlo, graph size, or this equivalence. HTTP observations
are external evidence about HTTP outcomes, not an alternative discovery method.


Actual OBI HTTP bodies are retained before decoding, with collector ingress,
content headers and hashes. Selection copies complete OTLP protobuf/JSON records
from those bodies; it preserves conflicting attributes, scope, links and IDs.
Native Jaeger exports use an attributed format codec. A source prefix never
turns an invalid ID into a valid one. Bering's declared OBI endpoint decodes eBPF
exports; its native endpoint decodes native exports. Combined discovery occurs
inside one Bering runtime, with source domains preventing cross-source ancestry.
The runtime replays a single offline batch, admits native late records, and
flushes after input is complete. Any dropped input or split publication is a
technical failure. Historical reconciliation is disabled for this batch method;
source timestamps do not determine selection. No graph is constructed outside
Bering. Only its emitted model is extracted from the snapshot and given to Sheaft.

## Operation contracts

These are structural predictions under fail-stop interventions and the explicit
assumption that other required components, inputs and application logic remain
correct. A predicted live path does not prove payload validity, transactional
success or timely completion. Comparing with external outcomes tests that
assumption. Full body checks remain in the evaluation even when HTTP is 200.

| System / operation | Required path semantics | Independent outcome / conditional behavior |
|---|---|---|
| DSB compose | nginx to compose; completion waits for post storage, user timeline and home timeline; user timeline write requires Mongo and Redis | Complete acknowledgement; later timeline probes are separately recorded postconditions, not discovered compose edges |
| DSB home timeline | nginx to home timeline, Redis and post storage | Exact stable fixture in complete JSON; selected user-timeline Mongo is off-path |
| DSB user timeline | nginx to user timeline, Redis and post storage | Exact stable fixture; Mongo fallback is conditional, so a Mongo-down prediction cannot assume every read accesses Mongo |
| OTel browse | frontend to catalog to catalog PostgreSQL | Complete 200 and selected product ID; fixed USD avoids frontend currency conversion |
| OTel add to cart | browse prerequisite, then frontend to cart AddItem/GetCart and Valkey | Both complete responses and exact item/quantity; skipped suffix is not an observed call failure |
| OTel checkout | browse/cart prerequisites; frontend to checkout; cart, catalog, currency, shipping quote/ship and payment; frontend catalog enrichment | Complete responses and exact order acknowledgement; EmptyCart/email errors are ignored upstream and are not mandatory; Kafka is not required for immediate HTTP success |
| Petclinic list owners | gateway to customers to shared MySQL | Complete exact seed-derived owner payload |
| Petclinic owner details | gateway to customers and visits; both to MySQL | Exact owner, pets and visits; upstream empty-visits fallback may return HTTP 200 but fails this body contract |
| Petclinic create visit | gateway to visits to MySQL | Complete 201 acknowledgement plus independently verified unique matching persisted row; persistence is a separate outcome |
| Petclinic list vets | gateway to vets | Exact seed payload; upstream cache makes DB access conditional, so DB-down does not unconditionally imply failure |

Pinned source references and machine-readable obligation manifests accompany
each adapter. Conditional paths without enough observed evidence remain unknown;
they are not forced into a conjunctive predicate. Async queue timing is outside
Sheaft's current connectivity model.

## Interventions and acquisition

Use three systems, absent/partial/full native tracing, and seeds 6/7/8: 27 fresh
campaigns. Each uses two Linux guests with separate kernels on one standard
GitHub Actions runner. This shared physical host remains a limitation.

Keep 20 requested operations/s and balanced operation mixtures: 600 healthy
class-training attempts, four 6,000-attempt discovery blocks (11,10,01,00), eight
1,200-attempt target blocks in proportions 4/2/1/1, and 600 independent healthy
class-test attempts. This is 34,800 primary attempts per campaign, 939,600 total.
Discovery blocks supply observations, not empirical end-to-end outcome rates to
substitute for the graph. Models and predictions are saved before target traffic.

Controlled logical services are user-timeline-service, product-catalog and
visits-service respectively. Their two supplied placement buckets each contain
one replica, labeled controlled_replica=a/b and guest=a/b. Sheaft correlated
placement faults are scoped to the controlled service AND its placement labels
and express exact states: 11 no outage, 10 B down, 01 A down,
00 both down. All nonintervened node/edge live probabilities are explicitly 1;
this is an assumption, not a fitted reliability estimate. Use 100,000 Sheaft
trials per state profile. Aggregate state predictions with weights
0.5/0.25/0.125/0.125 and check the exact weighted arithmetic. Independent marginal
replica probabilities must not replace the declared correlated state mixture.

Selected DB outages use separately attributed deployment-to-observed-endpoint
mapping and Sheaft service selectors. Aliases do not prove a shared physical DB.
Unresolved mapping is unknown. Preserve each caller's required DB edge so that
a shared DB actually participates in the prediction. Report structural additions
and forecast changes separately. Run 20 DB-up and 20 DB-down operations in each
campaign, reusing the existing guests.

## Completion, journaling and async recovery

There is no experiment HTTP deadline, observation cap or timestamp eligibility
gate. Remove injected proxy request limits; record native application behavior
separately. Readiness/process-control guards are technical checks, never business
failure criteria. Request duration is descriptive only.

Commit intent and planned request IDs before dispatch to a durable journal;
commit each step-start and terminal observation separately. Full response plus
contract match is true; a definitive completed mismatch is false. Incomplete
transport, unresolved requests or missing oracle evidence are unknown. An
unresolved request keeps its original intervention state: the campaign cannot
advance to a different state underneath it. A platform/technical stop retains
issued attempts, unresolved states and complete available costs and leaves the
campaign technically incomplete. It never supplies a synthetic failed response.

For OTel, execute 20 checkout controls normally, 20 while accounting is stopped,
and 20 after restoration. Preserve actual returned order IDs. While stopped,
record an independent SQL snapshot; a missing row means not yet confirmed, not
proof that Kafka holds a message. Resume accounting before waiting for persistence,
then verify the same paused IDs and new recovered IDs against exact order/items/
shipping records. No fixed completion deadline. Pending work at technical stop
remains unknown. Causal association requires an observed order ID or exact message
identifier chain; shared topics or nearby timestamps are insufficient. This is
an association/recovery check, not simulated queue timing.

The current readout supports exact source-local ancestry plus an explicit consumer
SpanLink to the producer as the cross-queue identifier chain. It reports optional
source order/message corroboration and external order agreement separately; their
absence does not invalidate a complete causal chain. Contradictory linkage IDs
remain unknown, while a business-order mismatch is a separate evaluation result.
ID-only joins without a SpanLink are not implemented in this iteration. Such
unknowns therefore cannot establish an inability of eBPF or its collector.

## Diagnostic failure evidence

DSB diagnostic `40780918812` failed at 2026-10-29 00:00:49 UTC while posting native
exports to Bering's `/v1/traces` during the last combined/network-scope operation
replay. The original checkpoint archive passed its SHA-256 check. The separate
`upload-artifact` step failed with `Maximum call stack size exceeded`, retaining no
output artifact. Logs do not establish OOM, disk exhaustion or the exact server
error. Available logs/metadata are permanently archived in
[data-40791837386](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40791837386).

Source inspection exposes a separate batching-contract risk: the configured 24h
window is aligned to UTC midnight, which this replay crossed. Ingestion can trigger
a flush of partial input before the next POST. This is a possible trigger for the
HTTP 500, not proof of the underlying flush error. Scheduling around midnight or
choosing an arbitrarily larger window would not satisfy the full-batch contract.

Before implementation, root and the independent skeptic give **explicit
ORIGINAL-criterion design GO** for an evidence-only repair: preserve complete
failed-ingest response bytes and identity, expose concise failure/resource evidence,
upload compact evidence first, and then losslessly package full output for upload.
The hypothesis is improved diagnosability, not scientific accuracy; the strongest
simple baseline is the same full-input toolchain with ordinary file retention.
Inputs, source semantics, graph construction, forecasts and external outcomes are
unchanged. Packaging, verification, transfers and failed attempts are charged.
Do not retry an ingest, trim input, hide the original failure, or interpret partial
output as a valid forecast. Implementation review precedes execution; a new
diagnostic is held pending the batching-contract investigation.

The pinned runtime has no supported clock-independent combined-input batch mode;
its separate discovery CLI does not preserve the same combined source metadata.
Root and the independent skeptic therefore give **explicit ORIGINAL-criterion
design GO** for a generic opt-in Bering `on_shutdown` publication mode, keeping
`windowed` as its unchanged default. The engineering hypothesis is one complete
source-aware batch independent of calendar boundaries. The strongest simple
baseline is the existing runtime on the same complete input within one window;
graph construction, supplied semantics and external-outcome criteria must remain
equivalent. No forecast accuracy or total-cost benefit is assumed. Overflow must
fail the entire batch, close must publish at most once, historical reconciliation
must be explicitly excluded, and finalization must not inherit a fixed HTTP
shutdown deadline. Generic synthetic product tests, independent implementation
review, releases and separate research-pin adoption/retained-input qualification
remain required. Product code and documentation contain no study material.
Existing jobs remain pinned and existing results are never relabelled as runs of
the new version. The exact earlier HTTP 500 cause remains unknown.

## Parallel campaign scheduling and API waits

Before implementation, root and the independent skeptic give **explicit
ORIGINAL-criterion design GO** for a future-only orchestration repair. The
hypothesis is operational: independent admitted campaigns can overlap without
exhausting worker slots or the repository's API allowance. The strongest simple
baseline is the same unchanged campaigns run sequentially or in smaller batches;
no scientific or total-cost improvement is assumed. Both schedules use identical
inputs, semantic contracts, tool binaries, model/forecast rules and external
outcomes. The causal change is scheduling and API pacing only. All preparation,
worker queue/compute, parent idle/compute, transfer and failed-attempt costs remain
included; there is no observation deadline or accuracy-dependent early stopping.

GitHub documents at least 20 concurrent standard jobs for Free accounts and
1,000 `GITHUB_TOKEN` REST requests/hour/repository. Eight waiting parents polling
every 15 seconds would request up to 1,920 reads/hour before overhead. Prepare
60-second polling (480/hour for eight parents) and safe GET handling for positively
identified rate-limit responses. Respect server retry/reset instructions, retain
sanitized wait evidence, and keep authentication/permission errors fatal.
Dispatch remains exactly one POST, with no blind mutation retry. Current live
campaigns are not restarted or changed.

The implementation received root and independent **ORIGINAL-criterion
implementation GO**. Focused synthetic HTTP/handoff checks passed (23 tests,
one Linux-only test skipped locally), as did 13 index/freeze checks. Exact-head
Linux CI remains required before activating the changed parent code.

After implementation review, exact-head CI, each system's staged-cell admission
and separate execution GO, allow at most eight globally committed parent campaigns, budgeting one
worker slot for each. Count queued/booting/matrix children as committed parents,
not just running jobs. Before each batch, refresh owner activity and require
`2 * committed_parents + other_committed_jobs <= 20`; four nominal spare slots
are headroom, not a reservation against other activity. Pause new admission if
outside activity grows; never put parent and child behind the same held slot.
This scheduling approval does not authorize cells before their scientific and
technical prerequisites are met, and calendar acceleration is not evidence of
lower total effort or compute cost.

Sources: [Actions limits](https://docs.github.com/en/actions/reference/limits),
[REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

## Reporting and costs

Retain every operation, source, tracing mode and repeat, including missing graphs,
unknown predictions, failed technical runs and unsupported async semantics.
Report point/interval errors, uncertainty, observable coverage, route and
downstream class ARI, DB dependencies, cross-guest evidence, and available costs.
No 5/10 percentage-point success gates. Capture preparation, builds, observation,
discovery, simulation, verification, failed runs and early termination; unavailable
human/agent costs remain explicitly unavailable rather than zero.

Technical qualification precedes the series.
`toolchain/execution-summary.json` distinguishes branches that actually invoked
Bering and Sheaft from unavailable branches; qualification completion does not
imply that every source path was exercised. Reviewer checks actual generated
models, fault selectors, source isolation, frozen predictions and independent
outcomes before any success claim. Repair technical failures with retained history;
do not expand scenarios to obtain a positive result.

## Released Bering 1.2.0 adoption (2026-10-29)

Before implementation, root and the independent skeptic gave explicit
**ORIGINAL-criterion design GO** for this adoption, conditional only on actual
publication; release `40796211973` has now completed and the tag resolves to
`6f806428509a640a6419058c2ad845ed44db7512`. The engineering hypothesis is that
explicit final publication can process the same full source-aware batch without
a calendar rollover. The strongest simple baseline remains the same complete
batch in the original runtime within a single window, plus the existing
same-contract manual graph baseline for the external forecasts. Graph semantics,
manual knowledge, observations, intervention distributions and independent
outcomes are unchanged. No accuracy or total-cost advantage is inferred from
this repair. Build, preparation, failed diagnosis, packaging, transfers and
computation are retained; no accuracy-dependent stopping is introduced.

Future default tool builds use released Bering 1.2.0 and `on_shutdown`, without
24-hour window/flush settings. Procrustes and Sheaft source pins are unchanged.
`ORIGINAL_PINS` and explicit `windowed` execution preserve historical qualification
replays and all three original checkpoint profiles. Existing admitted cells and
the running OTel parent remain attributed to their actual old binaries.

The one new profile `full6-40731158179-dsb-bering120-on-shutdown` uses exactly
checkpoint `12843610949`: 600 class-training and four 6,000-operation blocks, the
entire indexed source prefix, all source/variant/operation branches and the same
12 GiB Bering-child GC target. It verifies original 1.1.1 binaries before
relocating a copy of the index, then separately validates the new source build,
compiler/archive hashes and executable hashes. Original and effective manifests,
pins, publication modes and build costs are retained separately. Source-built
executables are not asserted to equal the published binary assets byte for byte.
Full-count, zero-drop and single-publication checks still gate technical validity.

Root implementation checks passed 86 synthetic tests (one Linux-only check
skipped locally); independent implementation review and exact-head Actions CI
precede one diagnostic dispatch. Actual diagnostic review and a separate fresh
DSB/full/6 admission precede that system's remaining cells. OTel's remaining eight
also require its staged-cell admission and an explicit version-transition review.
No valid cell is repeated merely to change the tool version or obtain a positive
result. The original DSB HTTP 500 body remains unavailable: this is a supported
batching-contract repair, not proof of that failure's exact cause.


Implementation/execution review completed on 2026-10-29: root and independent
6.1 Sol/xhigh reviewer gave explicit ORIGINAL-criterion GO for exactly one new
DSB retained-input diagnostic at `fa2c454eaa5cca1a20a534ceb6e72ab64f8f8af3`, after
independently repeating 86 focused tests and verifying exact-head CI `40798982219`.
Run `40799411526` was dispatched once and bound to that head. Actual diagnostic
integrity/resources remain required before fresh DSB traffic.

The reviewer also approved the Bering 1.2.0 version transition for OTel's remaining
eight cells after its current full/6 cell is admitted. No extra OTel diagnostic is
required: generic mixed-source/overlay equivalence and the old worker's full-count,
zero-drop, single-publication evidence address the publication-only change.
Window metadata, timestamps and accepted-late counters need not be identical.
This transition approval is neither parent-cell admission nor bulk execution GO.


Actual OTel admission and execution review (2026-10-29): root and the independent
6.1 Sol/xhigh reviewer gave explicit ORIGINAL-criterion GO for full/6 `40786403012`
and, separately, exactly the remaining eight planned OTel cells at `19ad30e` after
CI `40800562445`. The review verified the complete compact ZIP digest/CRC,
34,800 primary and 9,600 target attempts, 19 blocks, 7,539 unchanged frozen-file
hashes, identical logical index before/after the worker, byte-identical imported
forecasts and import-before-freeze-before-target ordering. Supervisor exit was
clean. eBPF unknowns, native/combined errors and DB mapping unknowns remain valid
results. Eight cells were dispatched once: absent6-8 `40803782214`, partial6-8
`40803790289`, full7 `40803798632`, full8 `40803806299`. All four runs bind to
`19ad30ea772ae5430432e2e05339a8c0d9fe0d1f`. A fresh 01:59:03 UTC owner-wide check
found only the one DSB diagnostic active, so eight parent/worker pairs budgeted
17 job slots including that diagnostic. Archival run `40802785036` had completed.

Subsequent scheduling refinement, before execution: root and independent skeptic
also give explicit ORIGINAL-criterion operational-design GO to overlap ONE fresh
DSB/full/6 with those eight OTel parents, only after actual DSB diagnostic review
and separate staged-cell execution GO. This supersedes the eight-parent ceiling
above solely for that overlap: at most nine committed parents, each with a worker
slot reserved, and a fresh owner-wide `2*parents + all other committed jobs <=20`
check including queued/matrix/prepare/CI/archive jobs. At nine parents only two
noncampaign slots remain in total; they are not extra spare slots or a platform
reservation. Sixty-second polling requires at most 540 ordinary status reads/hour
for nine waiting parents before other reads, with existing rate-limit backoff.
The strongest baseline is the same unchanged work scheduled at eight parents or
sequentially; only calendar overlap is proposed to improve. All compute, setup,
queue, wait, transfers and failure costs remain, with no outcome gate, extra
scenario, observation cap or valid-cell rerun. DSB dispatch is not yet approved.
