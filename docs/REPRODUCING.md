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

Run the result workflow at the source commit recorded in the published report:

```sh
gh workflow run read-v6-full108-results.yml --repo a-a-k/ebpf-model-discovery-experiments --ref "$REPORT_SOURCE"
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
and prospective registration. Repository cleanup does not alter the source or
hashes attached to published observations.

All application traffic, VMs, model processing and large artifact verification
run in Actions. The full standard worker envelope and six-hour job limit apply;
actual per-phase resource observations are retained with the results.
