# Iteration-5 progress snapshot

Generated in [Actions run 40905967491](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40905967491)
at `84dd7532acbad466343cf34976abc3bbfec40cfa`, then copied without empirical
recalculation. This is a snapshot of declared work, not a completed main series
or a self-inclusive final cost account.

- [Generated report](report-v5.md): all 21 declared smoke attempt cells across
  13 runs, including failures, cancellations and missing packets.
- [Saved aggregate](evaluation-v5.json.gz): the original compressed bytes;
  [packaging proof](provenance/aggregate-packaging.json) identifies the exact
  restored JSON. No source evaluations have been refitted or rescored.
- [Declared inputs](provenance/declarations.json), [retrieval evidence](provenance/retrieval.json)
  and [saved costs](costs-v5.json) retain the declared scope and missing costs.
- [Independent review](../../../docs/REVIEW_V5.md) separates actual packet review
  from the reporter's transport checks.

Main coverage is **0/108**. The 27 New Relic main cells remain blocked by absent
authorized collector access and a verified codec. Smoke rows marked transport
eligible are not main coverage. The reporter does not itself perform independent
admission; later independent reviews are recorded separately.

The snapshot includes 59 repository-qualified runs: 13 smoke runs and 46 related
runs. Their known job-time sum is 14,607 seconds. Human preparation, earlier work
outside the declaration boundary and subsequent execution/report/publication
costs remain unknown or outside this snapshot, rather than being counted as zero.

The source artifact is `report-v5-40905967491`, ID `12912435473`, 402,010,349
bytes. GitHub reports its ZIP SHA-256 as:

```text
047fbeb2f1cad93fa97a44c40d3c502a3412dfd6e0adc3c17f149a9d01d4b5ac
```

Local inspection downloaded selected ZIP members with HTTP ranges, verified their
CRC and recorded their SHA-256. It did not independently verify the whole ZIP.
The three download records in `provenance/` retain this distinction. The large
original artifact also retains historical recovery ZIPs; these are not copied
into this compact repository snapshot.

To restore the original 9,368,272-byte aggregate:

```sh
gzip -dc evaluation-v5.json.gz > evaluation-v5.json
```

The restored SHA-256 is
`02f59e8d79b198a540192ebeb3c3199cf1f98c02e4e258a1b1575d20c9842aa4`.
The compressed SHA-256 is
`3b073e88c3962e417e25d588f7dafa2bcb39e19eda6bb43e8543bfdaffe5ec2c`.
