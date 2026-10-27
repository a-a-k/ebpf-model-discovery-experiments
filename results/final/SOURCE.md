# Final report provenance

The accompanying generated files are copied without recalculation from [Actions report 40459487189](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40459487189), generated at commit `69fc1e3397ad945a8d6580011ed431e4c5141085`.

Original artifact: [`report-40459487189`, ID 12714127173](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40459487189/artifacts/12714127173).

Original ZIP digest: `sha256:102ae31f2f357976c6c132be2b69b17e405a76b5bbe1640da9c7fa7aea1c1c89`. The permanent archive's checksum agrees with the Actions artifact digest. Git normalizes text line endings in checked-in copies; verify this digest against the original ZIP.

The complete artifact retains per-campaign evidence, original models/forecasts/maps, calibration and target assignments, proxy/semantic comparisons, and the first-evaluation recovery proof for OTel full seed 2. The compact checked-in tables do not replace these files or the original raw captures. Earlier reviewed snapshots remain under `results/interim-18` and `results/interim-22`.

Independent final review verified all 27 campaigns, 58,320 primary attempts, 243 model/forecast/evaluation-map hashes and 81 target-assignment hashes. The previous 22 campaigns' evaluated results are unchanged. Review approves reporting the completed mixed/negative series, not a claim that the full original usefulness criterion is established; see the [recorded verdict](../../docs/PROTOCOL.md#final-result-review-2026-10-27).

Permanent releases containing the exact original input artifacts, workflow logs, checksums and provenance:

- [First acquisitions and preparations](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40362321620).
- [Later OTel attempts and reviewed partial reports](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40455065560).
- [Final technical replacements and complete report](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40460660847).

Reproduce the original analysis from retained data in GitHub Actions:

```bash
gh workflow run report.yml --ref data-40460660847 \
  -f run_ids='40335553492 40341237065 40342667653 40336898753 40349570169 40349582587 40344799981 40346563009 40346575968 40333270035 40351820494 40361979734 40372011776 40372023737 40372035878 40456045810 40456053398 40456061253' \
  -f archive_tags='data-40362321620 data-40455065560 data-40460660847'
```

The release tag points to `4c24c2434fe859924b0318b88f3b523ae5b1840f`; its analysis, adapters, scripts and workflow files are identical to the final report commit. Only documentation differs. Archived replay verifies ZIP checksums and preserves existing assignments/prediction files. Recovery of the completed full seed-2 capture performs evaluation only, with byte-identical acquisition projection/model/evaluation code and protected original inputs.

The cost ledger is the completed-job snapshot taken during the original report. A replay obtains a new history snapshot; it does not reproduce the old cost cutoff. Later publication/review jobs, ongoing time and unmetered human/agent work are not silently included as zero. Failed attempts and the superseded pilot remain in the archive and separate report outputs.
