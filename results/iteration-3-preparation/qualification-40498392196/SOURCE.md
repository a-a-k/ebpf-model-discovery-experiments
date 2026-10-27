# Revised iteration 3 resource qualification

These are three technical qualifications, not scientific campaigns or evidence
of model usefulness. Each uses full native tracing, seed 3, two independent
guest kernels and 1,200 healthy attempts at 20 operations/s. No application
deadline is imposed; the ten-second engineering cap produces unknown outcomes
for incomplete observations.

- Acquisition: [40498392196](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40498392196), commit `79ca71e8d6d54ced18fec96e3d03141a5c43f464`.
- Evidence copy and body audit: [40500194868](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40500194868), commit `2e534c6eedf9679ef3dbb86950482a5cae27f57d`.
- [Copied-file checksums](revised-review/copied-sha256.json), [original artifact index](revised-review/source-artifacts.json), and [workflow jobs](revised-review/source-jobs.json).
- Permanent [original ZIPs, logs, provenance and checksums](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40510390283), including the superseded qualification and retained-data audits.

The `revised-review/` directory is an unmodified copy of the compact Actions
artifact. It retains deployment, index, scheduling, memory and disk evidence.
The complete raw observations remain in the acquisition artifacts. The
[OTel body audit](revised-review/otel-body-fidelity.json) consumes saved source
projections and independently recorded response bytes, without fitting or using
business-outcome/SQL labels.

All three jobs completed. Resource review is separate from source coverage:
unsupported native response bodies, missing compose acknowledgement bodies and
unbound entries remain explicit. No qualification attempts are admitted into the
27-campaign population.

The [first binding audit](binding-audit-40501095000.json), produced in
[40501095000](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40501095000),
found all 1,200 native entries by exact request identity before the timing rule.
The [reviewed attribution replay](binding-replay-40502380042.json), produced in
[40502380042](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40502380042),
confirmed that all 637 rejected outer spans started before the client journal.
The documented exact-header-child rule recovers 631, while six remain unknown;
563 already satisfied the strict window. No traffic, model fitting or accuracy
selection occurred. Raw input hashes agree between the two audits.
