# Refreshed Actions cost snapshot

Copied cost files and provenance come unchanged from
[40538068099](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40538068099),
commit `38ce66bbb39fa5abb74c7a94029e662639e7db43`. All computation ran in Actions.
The original 97 primary-report files in the parent directory remain unchanged.
The refreshed report's `results.json`, `metrics.csv` and `report.md` match the
original primary report byte-for-byte; they are not duplicated here.

The snapshot records 113,348 acquisition job-seconds and 14,829 declared
preparation/reporting job-seconds. It includes the cancelled structural attempt,
the later OTel HTTP-502 failure, the OTel-only rerun, prior reporting and archive
jobs. Metadata and manifest hashes passed independent review. Storage totals
count Actions artifacts, including overlaps; they do not count every duplicate
public-release byte or measure all network transfer.

This cost report's own job, the final report archive and later publication
checks lie beyond the snapshot boundary. Their run records are retained, but
are not included in these totals. Human/agent effort and local validation compute
were not independently metered. None of those omissions is filled with zero,
and no comparative efficiency claim is made.

Original report ZIPs, both structural reporting attempts, the completed OTel
rerun, implementation-check logs and this refresh are preserved in
[data-40538614987](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-40538614987).
Downloaded `SHA256SUMS.txt` and `provenance.tar.gz` match GitHub asset digests
`092890c0666c11e5ef83e716372a32de08a01cd9763be83434db228ea6245400`
and `c9afd47b6c8cb0c9b65dbf6b770114314db110cfcf98d5c0d947e9aaef0bf0c6`.
