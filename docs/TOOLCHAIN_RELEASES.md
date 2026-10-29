# Published tooling and integration evidence

Verification updated on 2026-10-29. Product publication establishes available
software, not the validity or accuracy of this experiment. The experiment builds
its three tools from exact source commits and retains binary hashes per campaign.

| Component | Published or merged revision | Release / integration evidence |
|---|---|---|
| Bering, current | v1.2.0, `6f806428509a640a6419058c2ad845ed44db7512` | [Release](https://github.com/MB3R-Lab/Bering/releases/tag/v1.2.0), [successful release workflow](https://github.com/MB3R-Lab/Bering/actions/runs/40796211973), [generic batch publication](https://github.com/MB3R-Lab/Bering/pull/53) |
| Bering, original iteration-4 pin | v1.1.1, `dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3` | [Release](https://github.com/MB3R-Lab/Bering/releases/tag/v1.1.1), [successful release workflow](https://github.com/MB3R-Lab/Bering/actions/runs/40638893415), [merged fix](https://github.com/MB3R-Lab/Bering/pull/52) |
| Sheaft | v1.3.2, `686a602f4e7b71f3612f1810885e29dd66c8733a` | [Release](https://github.com/MB3R-Lab/Sheaft/releases/tag/v1.3.2), [successful release workflow](https://github.com/MB3R-Lab/Sheaft/actions/runs/40635411908) |
| Procrustes | `39f76000f8a39c971155e08ebffde829b525911b` | [Merged explicit OBI preflight and handoff](https://github.com/MB3R-Lab/Procrustes/pull/1); source-built preview, not a newly asserted product release |
| mb3r-stack | v1.3.0, `8a6dc136d67a55a8609cb9a82f6385895713603c` | [Release](https://github.com/MB3R-Lab/mb3r-stack/releases/tag/v1.3.0), [successful release workflow](https://github.com/MB3R-Lab/mb3r-stack/actions/runs/40642477259), [integration update](https://github.com/MB3R-Lab/mb3r-stack/pull/27) |
| mb3r-software-complex-repro | v1.3.4, `44d97ef075d2d2d11a2069dc8d2f9c45a01f3866` | [Release](https://github.com/MB3R-Lab/mb3r-software-complex-repro/releases/tag/v1.3.4), [successful release workflow](https://github.com/MB3R-Lab/mb3r-software-complex-repro/actions/runs/40642871942), [immutable image-tag guard](https://github.com/MB3R-Lab/mb3r-software-complex-repro/pull/3) |
| OTel stack integration | `a81989e294ffa28843c8dc1fdeb629028fa51c78` | [Merged runtime and CI pins](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/pull/5), [CI](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40653840325), [gate](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40653840261) |

Current Bering and Sheaft annotated release tags resolve to the exact commits in
`toolchain_v4.PINS` and `scripts/setup-toolchain-v4.sh`; `ORIGINAL_PINS` retains
Bering 1.1.1 for historical diagnostics. Both releases contain
their versioned Helm chart packages. The stack release packages both stack and
asset charts and the existing 1.3.0 compatibility matrix names Bering 1.1.1, Sheaft
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


Bering 1.2.0 was released after independent review of the generic opt-in
`on_shutdown` mode. Exact-head CI, real OBI smoke and release dry run passed on
PR 53 before merge. The annotated tag peels to `6f806428...`; the release workflow
published chart and app version 1.2.0. Downloaded manifest/chart assets were
checked against GitHub asset digests and the chart's actual metadata inspected.
The published image is `sha256:f706b79172a8322d53422de8d08a47d7779d0fbe2909511fa08385608b74c15b`;
the OCI chart is `sha256:f76f6cddea288af4174e7a70ae986fc19145117646c5ba8b926a7aac58d2af03`.
Model and snapshot schemas remain 1.3.0. Related integration updates are under
review; their older releases above remain historical evidence until new releases
are verified. No research materials were added to Bering.


Related current-main compatibility updates passed independent review and exact-head
CI and were merged on 2026-10-29:

- [Procrustes PR 2](https://github.com/MB3R-Lab/Procrustes/pull/2),
  `ede4ae9b6595e57a32bf4ee886799cefb97e7f83`, updates the current release handoff link.
- [Sheaft PR 100](https://github.com/MB3R-Lab/Sheaft/pull/100),
  `e3cf8e158f004219568c7401b1fd486e4010d9c8`, verifies actual published Bering 1.2.0
  fixtures without changing accepted schema pins or the simulator. It does not
  relabel the existing Sheaft 1.3.2 release.
- [OTel integration PR 6](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/pull/6),
  `ce25b8f2aa4132884a49ab7fd6019e45f0ceea4f`, updates the runtime Bering image.
  The CI reproduction-package image remains separately pinned until a replacement
  package is measured, published and verified.

These changes do not silently change the research's fixed Procrustes/Sheaft pins.
