# Diagnostic report provenance

These compact tables are copied without recalculation from [Actions 40480503659](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40480503659),
at source commit `6e270c678b328e0e5e522decd16abdf6a88e34a8`.

The complete artifact is [diagnostics-report-40480503659, ID 12722822176](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40480503659/artifacts/12722822176):
7,133,942 bytes, SHA-256 `06978dab1318647d51dfd31a7c3a1a8c90aa0118ee7d811eff8db730a5b3841a`.
The [permanent archive](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40481209338)
retains this ZIP, each system artifact, workflow logs, original metadata and
matching checksums. Per-attempt semantic witnesses/comparisons, all 405 protected
input hashes and per-campaign download/processing provenance are in that full ZIP.
Git normalizes text line endings in these checked-in copies.

Inputs are the fixed final report 40459487189 and original captures for all 27
accepted campaigns. The original report ZIP and every capture ZIP are verified
before use. All original forecasts reproduce; original prediction and assignment
files remain unchanged. No new application requests were made.

Reproduce the complete diagnostic in Actions from the archived source version:

```bash
gh workflow run diagnostics.yml --ref data-40481209338
```

Oracle-assisted controls are retrospective diagnostics, not deployable methods
or fresh confirmation. The [protocol and refined design](../../docs/ITERATION_2.md)
record hypotheses, both pre-execution verdicts, result interpretation and review.

The original `workflow-jobs.json` is the snapshot taken before its report job
finished; that job's end time was then unknown. `completed-workflow-jobs.json`
is a later read-only API snapshot with completed timestamps. Setup and downloads
are included in the jobs; system and campaign status records additionally report
processing elapsed time. Archiving and CI are separate workflow runs; later
publication and unmetered human/agent time are not silently treated as zero.
No efficiency superiority is claimed.
