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
To repeat the publication checks and report generation in Actions:

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
