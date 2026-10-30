# Existing eBPF graph and simulator input

These are exact saved files from OBI / Petclinic / absent tracing / seed 6 in
[main run 40910013685](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40910013685).
They are part of the fixed study, not a new experiment or a replacement for the
remaining campaigns. Application SDK tracing was disabled in this reviewed cell.

- [Bering graph](bering-model.json): the actual Bering output before supplied
  alias annotation; its nodes and edges were not redrawn for this publication.
- [Bering command](bering-command.json): actual `bering serve` execution using
  the `ebpf-otlp` source, with 335,028 input observations and retained ingest hashes.
- [Sheaft input](sheaft-model.json): the actual owner-details operation model,
  using observed graph identities and the documented supplied operation/replica
  semantics.
- [Sheaft command](sheaft-command.json): the actual simulator invocation and
  successful process exit. Process success alone is not an accuracy claim.

The [provenance file](provenance.json) binds every copied byte and the source
review record. The review and external results are part of the
[36-cell review snapshot](../main-review-snapshot-20261030/SOURCE.md).
Static semantics remain explicit and equally available to the direct baseline;
this example does not establish automatic business-semantic discovery, lower
complete cost or superiority over that baseline.
