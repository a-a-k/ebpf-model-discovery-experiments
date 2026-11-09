# Reproducing the experiment

The protocol defines the matrix, allocation, workloads, sources, baselines and
external outcomes. Application READMEs describe the pinned deployments and their
SDK controls and independent outcome checks.

## Published results

The completed-result manifest selects the exact original metadata publication
for every case. Its records include byte counts, SHA256, source commits and the
actual producing run, job and attempt. The cost ledger retains the study scope,
failed attempts and unknown costs. The result reader preserves the scientific
fields, unavailable values and adverse outcomes of those publications.

The published result was generated from commit
`c4f066d7c067d5661c3d942aacadb25d3103820d`. Its preserved source ref is
`audit/full108-literal-report-v6`. Use that ref for the fixed publication replay;
the input closures and qualified source files belong to the recorded commit.

The [generated JSON](../results/literal-results.json) and
[provenance](../results/provenance.json) are retained directly in the repository.
The [semantic correction](../results/semantic-correction.json) distinguishes
Social Network HTTP acknowledgement from successful MongoDB storage. Replaying
the historical report does not validate a corrected forecast or a durable write.

### Archive-backed report replay

The [publication archive](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/publication-archive-42658254761)
contains the exact 102 canonical metadata ZIPs and the retained historical
Coroot publication prefix: 103 ZIPs totaling 12,344,016,466 bytes. Its input
bundle preserves the original reader, required source records, reference report
and historical API receipts. The [archive receipt](../results/archive.json)
records exact asset identities, checksums and verification runs.

Run the archive-backed reader in Actions:

```sh
gh workflow run publication-archive.yml --repo a-a-k/ebpf-model-discovery-experiments --ref main -f mode=replay -f index_asset_id=728317527 -f index_bytes=213141 -f index_sha256=d5294d00a5944789b2743ae1567cc7a9b4833af4069c1012e2953805541cd277
```

This mode reads Release assets and recorded API receipts; live Actions API
requests are forbidden. It verifies original ZIP bytes/SHA256 and member CRCs,
then compares scientific fields, original forecasts, lineage and omissions with
the published report. Execution, resource and cost headers describe the new
reader run. The original scientific reader is unchanged except for its three
I/O functions; its input source remains the recorded `c4f066d` commit.

API receipts are historical snapshots. Their `expired:false`, embedded draft
release state and draft browser URLs are not current availability assertions.
Use the published tag URLs above and exact asset IDs/checksums in the receipt.
Release storage removes dependence on Actions artifact expiry; continued
GitHub repository, Release and API availability remains required.

This is reproduction of the published report from original metadata. It does
not archive the complete raw-capture/model-build input closure or demonstrate
rebuilding all models from scratch.

### Original Actions publications

While the original Actions artifacts remain available, repeat the original
publication checks directly with:

```sh
gh workflow run read-v6-full108-results.yml --repo a-a-k/ebpf-model-discovery-experiments --ref audit/full108-literal-report-v6
```

The workflow reads the fixed manifest and ledger from that commit, verifies the
original publications and produces the literal report and CSV in Actions.
The two declared classification-assignment arrays are the only omitted fields.
Source/view rows share external attempts and are not independent replications.

## Acquisition

series-v6.yml executes physically paired blocks; series-isolated-v6.yml executes
blocks with separate treatment workers. Their inputs select application, SDK
mode and repetition. The continuation workflows restore exact published closed
inputs and retain their original capture identities when processing resumes on
a different worker.

Execution uses the exact prospectively registered source, blueprint and input
records for the selected block. Those registrations belong to their recorded
commits. New acquisition or a changed source requires a new honest source census
and prospective registration. Published observations retain their original
source identities and hashes.

All application traffic, VMs, model processing and large artifact verification
run in Actions. The full standard worker envelope and six-hour job limit apply;
actual per-phase resource observations are retained with the results.
