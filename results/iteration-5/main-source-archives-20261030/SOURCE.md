# Original main-attempt source archives

These eight data releases preserve 19 original main-attempt runs and 84 original artifacts, including failed and superseded attempts. This is an initial main-source archival batch, not coverage of all study sources. The two earlier failed DeepFlow sources are archived [separately](../archive-41031747845/SOURCE.md). Other sources remain available in their recorded Actions artifacts pending archival.

| Data release | Original runs | Verification |
| --- | --- | --- |
| [41044703595](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044703595) | 40910021896, 40913407822, 40919005648, 40924968145, 41011398324 | [proof](41044703595/publication-verification.json) |
| [41044707631](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044707631) | 40914709370, 41009954091 | [proof](41044707631/publication-verification.json) |
| [41044711442](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044711442) | 40910013685, 40947299209 | [proof](41044711442/publication-verification.json) |
| [41044716243](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044716243) | 40970638144 | [proof](41044716243/publication-verification.json) |
| [41044720043](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044720043) | 40971766251 | [proof](41044720043/publication-verification.json) |
| [41044724448](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044724448) | 40966847000 | [proof](41044724448/publication-verification.json) |
| [41044728499](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044728499) | 40956228868, 41004291277 | [proof](41044728499/publication-verification.json) |
| [41044732432](https://github.com/a-a-k/ebpf-model-discovery-experiments/releases/tag/data-41044732432) | 40932031732, 40935194776, 40935203055, 41010834860, 41024050638 | [proof](41044732432/publication-verification.json) |

The unchanged archive workflow checked original source bytes in Actions. Three original ZIPs exceeded the release asset size limit and were losslessly split into twelve parts. Their internal chunk manifests match the original artifact identities; each published part's API size and SHA-256 digest matches its manifest. Original reassembly was checked in Actions. Local verification read only small metadata, checksums and provenance; no original ZIP or part was downloaded or reassembled locally.

The [aggregate verification](publication-verification.json), [source inventory](source-inventory.json) and [dispatch records](dispatches.json) preserve the exact scope. Two job logs were unavailable with HTTP 404 (jobs 123575210321 and 123587179829); source artifacts were preserved. Archive integrity is not empirical admission or a favorable scientific finding. All publication costs and failures remain part of the study.
