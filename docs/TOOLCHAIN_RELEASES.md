# Published tooling and integration evidence

Read-only verification on 2026-10-28. Product publication establishes available
software, not the validity or accuracy of this experiment. The experiment builds
its three tools from exact source commits and retains binary hashes per campaign.

| Component | Published or merged revision | Release / integration evidence |
|---|---|---|
| Bering | v1.1.1, `dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3` | [Release](https://github.com/MB3R-Lab/Bering/releases/tag/v1.1.1), [successful release workflow](https://github.com/MB3R-Lab/Bering/actions/runs/40638893415), [merged fix](https://github.com/MB3R-Lab/Bering/pull/52) |
| Sheaft | v1.3.2, `686a602f4e7b71f3612f1810885e29dd66c8733a` | [Release](https://github.com/MB3R-Lab/Sheaft/releases/tag/v1.3.2), [successful release workflow](https://github.com/MB3R-Lab/Sheaft/actions/runs/40635411908) |
| Procrustes | `39f76000f8a39c971155e08ebffde829b525911b` | [Merged explicit OBI preflight and handoff](https://github.com/MB3R-Lab/Procrustes/pull/1); source-built preview, not a newly asserted product release |
| mb3r-stack | v1.3.0, `8a6dc136d67a55a8609cb9a82f6385895713603c` | [Release](https://github.com/MB3R-Lab/mb3r-stack/releases/tag/v1.3.0), [successful release workflow](https://github.com/MB3R-Lab/mb3r-stack/actions/runs/40642477259), [integration update](https://github.com/MB3R-Lab/mb3r-stack/pull/27) |
| mb3r-software-complex-repro | v1.3.4, `44d97ef075d2d2d11a2069dc8d2f9c45a01f3866` | [Release](https://github.com/MB3R-Lab/mb3r-software-complex-repro/releases/tag/v1.3.4), [successful release workflow](https://github.com/MB3R-Lab/mb3r-software-complex-repro/actions/runs/40642871942), [immutable image-tag guard](https://github.com/MB3R-Lab/mb3r-software-complex-repro/pull/3) |
| OTel stack integration | `a81989e294ffa28843c8dc1fdeb629028fa51c78` | [Merged runtime and CI pins](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/pull/5), [CI](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40653840325), [gate](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40653840261) |

Bering and Sheaft annotated release tags resolve to the exact commits in
`toolchain_v4.PINS` and `scripts/setup-toolchain-v4.sh`. Both releases contain
their versioned Helm chart packages. The stack release packages both stack and
asset charts and its published compatibility matrix names Bering 1.1.1, Sheaft
1.3.2 and the same Procrustes revision. The reproduction release's toolchain lock
pins those revisions as well; its existing `candidate` status is retained rather
than reinterpreted as evidence of scientific adequacy.

The [Bering chart metadata](https://github.com/MB3R-Lab/Bering/releases/download/v1.1.1/chart-metadata.json)
records `ghcr.io/mb3r-lab/charts/bering:1.1.1` at
`sha256:8895a5c1e8b208f58c66d526e9663578f9402f139b1f983253afb5f3bd6c87a6`.
Its [image manifest](https://github.com/MB3R-Lab/Bering/releases/download/v1.1.1/oci-image-manifest.json)
records `ghcr.io/mb3r-lab/bering:v1.1.1` at
`sha256:f39d2241d9631fec070ece4aa8e96687b16e1d480cef2a95d7a2f4db74da6cea`.
These are published manifest claims corroborated by the release workflow; this
read-only audit did not rerun a deployment or create new performance evidence.

Study code, captures, system-specific contracts and analysis remain in this research
repository. A search of the released Bering tree for the study repository name and
URL found no matches. Its existing DeathStarBench article citation predates this
work (`b77e0f5`, 2026-07-02); it is not a reference to this eBPF study.
