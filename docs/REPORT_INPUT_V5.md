# Complete declarations through a committed file

The final attempt/cost declarations exceed GitHub's 65,535-character aggregate
workflow input limit even as minified JSON. Removing provenance notes would lose
part of the retained explanation. See the
[official workflow input limit](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onworkflow_dispatchinputs).

The existing `report-v5.yml` `declarations` input accepts the committed path
`docs/clean-study-declarations-20261030.json`. It also retains the legacy inline
JSON input. The path form requires a normalized tracked `docs/*.json` file,
checks the exact workflow checkout and committed Git bytes, and records the
source path, Git blob, SHA-256 and workflow head in retained provenance.

Both forms pass the same complete object to the existing report validator and
materialize the same `provenance/declarations.json`. Scientific selection,
source equivalence, saved evaluations, plots, default counts and all cost notes
are unchanged. The existing report test executes the actual workflow bootstrap
with the complete oversized declarations, verifies whole-object and output-byte
equality, and rejects uncommitted or escaping paths. This requires no campaign
replay, model fitting or rescoring.

This is a transport repair. The final report still requires all 81 reviewed
cases, technical-only duplicate selection, source proofs, complete cost scope
and independent actual-result review.
