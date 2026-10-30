# DSB worker packaging repair and bounded qualification

The OBI DeathStarBench/full seed-6 attempt
[40947264867](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40947264867)
failed before forecast freeze and target traffic. Its worker completed discovery,
but lossless packaging rejected a byte mismatch. The retained
[failure diagnosis](../results/iteration-5/scope-correction-20261030/audit/diagnoses/failure-diagnosis.md)
does not identify the changed file or its writer. A surviving resource-sampler
descendant is a source-supported hypothesis, not an established historical cause.

The original research criterion remains recovery of useful graphs from eBPF and
their externally evaluated simulation, with identical semantic knowledge and the
strongest direct baseline. This infrastructure repair supplies no new scientific
contribution or cost advantage. The narrow technical criterion is unchanged
scientific bytes with verified termination of the owned resource writer before
packaging. The baseline is the existing strict package/source comparison and
saved successful package. Failed attempts, preparation and qualification costs
remain in the study; human effort remains unmeasured.

Before execution, the root and separate reviewer granted ORIGINAL-criterion GO
for this repair and its saved-data qualification. The reviewer checked actual
implementation `dca6aded8e830f9a36349866606a3916698d89c1`, integrated as
`f236c8f`. It owns and joins the sampler process group, retains its lifecycle
proof, rejects packaging without that proof, and preserves exact mismatch
diagnostics on future failures. No sleep or elapsed-time threshold proves
quiescence. The strict package comparisons and scientific pipeline are retained.

Qualification first runs Linux checks, then verifies and repackages the immutable
successful worker artifact `12932698721` from run `40956304402` in GitHub Actions.
Its workflow revision `597811ce6fad4466fd7f7511f4a5dc3bdc503a07` differs from its
scientific/implementation revision `5cfdd7cbb60daec95d447109a18f82219ea29e8f`;
both are checked separately. Every restored path, byte count, mode and SHA-256,
plus the complete package manifest, must match. Local focused checks passed 49
tests with six POSIX-only tests skipped on Windows; Linux CI must cover those.

Repeating the failed main cell required independent review of actual qualification
output. The historical failed attempt is never promoted to a valid result or
removed.

## Actual qualification and exact repeat

Linux CI [41005336865](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41005336865)
and the saved qualification
[41005432674](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41005432674)
passed at `8c6f1fac8ea73315e8ea98a9db0014319425d33e`. The qualification's
54 focused Linux checks passed. Its [saved validation](../results/iteration-5/worker-packaging-qualification-41005432674/validation.json)
records exact equality of 3,204 files containing 1,972,080,796 bytes and of the
836,838-byte package manifests. The standalone verification/repackaging took
37.72 seconds; this is a recorded preparation cost, not a comparative efficiency
result. Full workflow/download costs are separately retained in Actions.

The root and separate reviewer checked the actual proof ZIP, all five current
source-file hashes against immutable Git blobs, both manifests and both original
source identities. Both granted actual-output GO. Only the 339,507-byte proof
archive was downloaded locally; the large saved source and unpacked trees were
processed and removed in Actions. The [publication record](../results/iteration-5/worker-packaging-qualification-41005432674/publication.json)
binds the retained manifest's compressed and restored bytes.

The exact failed cell was then dispatched as
[41005821961](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41005821961),
on the same reviewed revision. Its outcome is pending and receives an independent
review. This qualification neither identifies the earlier mutation nor admits
any historical failed attempt.
