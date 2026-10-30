# Retained original failed DeepFlow inputs

[Data release data-41031747845](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41031747845)
preserves the original artifacts and available logs/provenance of failed runs
40963548420 and 40965631880. Their two original training ZIPs contain
2,511,819,922 bytes. Both failures remain failures; archiving is not empirical
admission or a successful measurement.

The unchanged [archive workflow](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41031747845)
downloaded and checked the original bytes in Actions. The final Release API sizes
and SHA-256 digests equal the original Actions API identities for both ZIPs. The
[publication verification](publication-verification.json),
[Release metadata](release-metadata.json), [checksums](SHA256SUMS.txt), and
[small provenance archive](provenance.tar.gz) record that comparison, including
explicit unavailable-log records. Local inspection downloaded only the small
metadata assets; no local download/hash verification of either original ZIP is
claimed.

These two runs are only an initial archival batch. Other iteration-5 source runs
remain in their recorded Actions artifacts pending further archival. All archive
publication time/storage and any failures remain study costs.
