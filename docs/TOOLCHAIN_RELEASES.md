# Published tooling and integration evidence

Verification updated on 2026-10-29. Product publication establishes available
software, not the validity or accuracy of this experiment. The experiment builds
its three tools from exact source commits and retains binary hashes per campaign.

| Component | Published or merged revision | Release / integration evidence |
|---|---|---|
| Bering, iteration 5 | v1.3.0, `70d4145d3e26f11d8b3fb5be8917c50c1c6d8c2a` | [Release and chart](https://github.com/MB3R-Lab/Bering/releases/tag/v1.3.0), [successful publication](https://github.com/MB3R-Lab/Bering/actions/runs/40879223434), [vendor-neutral eBPF input](https://github.com/MB3R-Lab/Bering/pull/54) |
| Bering, later iteration-4 pin | v1.2.0, `6f806428509a640a6419058c2ad845ed44db7512` | [Release](https://github.com/MB3R-Lab/Bering/releases/tag/v1.2.0), [successful release workflow](https://github.com/MB3R-Lab/Bering/actions/runs/40796211973), [generic batch publication](https://github.com/MB3R-Lab/Bering/pull/53) |
| Bering, original iteration-4 pin | v1.1.1, `dccd1bca39b6ee85a79e5e245bdd2e727f0da1a3` | [Release](https://github.com/MB3R-Lab/Bering/releases/tag/v1.1.1), [successful release workflow](https://github.com/MB3R-Lab/Bering/actions/runs/40638893415), [merged fix](https://github.com/MB3R-Lab/Bering/pull/52) |
| Sheaft | v1.3.2, `686a602f4e7b71f3612f1810885e29dd66c8733a` | [Release](https://github.com/MB3R-Lab/Sheaft/releases/tag/v1.3.2), [successful release workflow](https://github.com/MB3R-Lab/Sheaft/actions/runs/40635411908) |
| Procrustes, iteration 5 | `9648ae3fe9ef24725e665d008c79d0681ce40f85` | [Merged vendor-neutral source preflight and handoff](https://github.com/MB3R-Lab/Procrustes/pull/3); source-built preview |
| Procrustes, iteration 4 | `39f76000f8a39c971155e08ebffde829b525911b` | [Merged explicit OBI preflight and handoff](https://github.com/MB3R-Lab/Procrustes/pull/1); source-built preview, not a newly asserted product release |
| mb3r-stack | v1.3.0, `8a6dc136d67a55a8609cb9a82f6385895713603c` | [Release](https://github.com/MB3R-Lab/mb3r-stack/releases/tag/v1.3.0), [successful release workflow](https://github.com/MB3R-Lab/mb3r-stack/actions/runs/40642477259), [integration update](https://github.com/MB3R-Lab/mb3r-stack/pull/27) |
| mb3r-software-complex-repro | v1.3.4, `44d97ef075d2d2d11a2069dc8d2f9c45a01f3866` | [Release](https://github.com/MB3R-Lab/mb3r-software-complex-repro/releases/tag/v1.3.4), [successful release workflow](https://github.com/MB3R-Lab/mb3r-software-complex-repro/actions/runs/40642871942), [immutable image-tag guard](https://github.com/MB3R-Lab/mb3r-software-complex-repro/pull/3) |
| OTel stack integration | `a81989e294ffa28843c8dc1fdeb629028fa51c78` | [Merged runtime and CI pins](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/pull/5), [CI](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40653840325), [gate](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40653840261) |
| mb3r-stack, current | v1.5.0, `4ba1d790d66c47976dc6cc05dfeb6e812427eb58` | [Release](https://github.com/MB3R-Lab/mb3r-stack/releases/tag/v1.5.0), [publication and anonymous preflight run](https://github.com/MB3R-Lab/mb3r-stack/actions/runs/40886588360), [integration PR](https://github.com/MB3R-Lab/mb3r-stack/pull/31) |
| mb3r-stack, previous | v1.4.0, `06dc632c24771f91abf7472f9d73887757e7b603` | [Release](https://github.com/MB3R-Lab/mb3r-stack/releases/tag/v1.4.0), [publication and anonymous download](https://github.com/MB3R-Lab/mb3r-stack/actions/runs/40800899484), [integration PR](https://github.com/MB3R-Lab/mb3r-stack/pull/29) |
| Reproduction package, current | v1.3.5, `2b2e012d8e85088d6d7bb9e231d0f9cc79ae634f` | [Release](https://github.com/MB3R-Lab/mb3r-software-complex-repro/releases/tag/v1.3.5), [source/container/publication/anonymous replay](https://github.com/MB3R-Lab/mb3r-software-complex-repro/actions/runs/40802150679) |
| OTel package gate, current | `3a615abf38a4e42cbfa3b7e8bdfec06ed9d0d7d4` | [Merged package pin](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/pull/7), [exact-head gate](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40804237780) |

Iteration-4 Bering and Sheaft annotated release tags resolve to the exact commits in
`toolchain_v4.PINS` and `scripts/setup-toolchain-v4.sh`; `ORIGINAL_PINS` retains
Bering 1.1.1 for historical diagnostics. Both releases contain
their versioned Helm chart packages. The stack release packages both stack and
asset charts. The historical stack 1.3.0 compatibility matrix and reproduction
1.3.4 lock name Bering 1.1.1, Sheaft 1.3.2 and the same Procrustes revision. The
previous stack 1.4.0 and retained reproduction 1.3.5 name Bering 1.2.0;
current stack 1.5.0 names Bering 1.3.0. The reproduction
package's existing `candidate` status is retained rather than reinterpreted as
evidence of scientific adequacy.

Iteration 5 uses `toolchain_v5.PINS`: Bering 1.3.0 and the merged generic
Procrustes revision above, with the same Sheaft 1.3.2 revision. Every collector
uses the same `ebpf-otlp` source kind, logical source ID and deployment domain.
No vendor parameter, API, SDK or collector-specific fingerprint enters this
product interface. Collector deployment and raw-format conversion stay in the
research repository. Historical pins and results are not rewritten.

The published Bering 1.3.0 image digest is
`sha256:95c29e311edfb5297c8bc22da6201a122f07e9492770a384fe93d8fac7d0da9c`.
Its OCI chart manifest digest is
`sha256:e3128dc852f2ecac9358e447442266ae420beb087f80a65ddd725d95f09b0f19`;
chart version and appVersion are both `1.3.0`. Published metadata checksums,
chart contents, anonymous image manifests/configs and anonymous chart retrieval
were verified. The model/snapshot contracts remain `1.3.0`.

Stack 1.5.0 passed exact-head integration CI and publication, including the
anonymous packaged preflight. Its chart was also pulled anonymously from OCI:
manifest `sha256:8217a7f12616ba348ef89716ca747c95fdff596b923611ffb5a900a1c1956958`,
chart bytes `sha256:6385eeb7df3c97065608671c72795dd0969e4aabe6bd8b01ba5b91af89e64099`.
The package matches the GitHub release asset and has version/appVersion `1.5.0`.

Related current-main updates passed independent review and exact-head CI:

- [Sheaft PR 101](https://github.com/MB3R-Lab/Sheaft/pull/101), merge
  `d59cfc63031095bf1f2346cf24849b060411d411`, verifies the actual published Bering
  1.3.0 package and canonical model/snapshot fixtures in
  [run 40886639089](https://github.com/MB3R-Lab/Sheaft/actions/runs/40886639089).
  This updates current app compatibility; it does not retag Sheaft 1.3.2 or
  change model schemas or simulation behavior.
- [OTel integration PR 8](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/pull/8),
  merge `2c50aa53cb63875bf3c7e442bf914bb26dea82ae`, updates its runtime Bering image
  to the published 1.3.0 digest. [Checks](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40887193770)
  and the [existing gate](https://github.com/MB3R-Lab/opentelemetry-demo-mb3r-stack/actions/runs/40887193685)
  passed. Native OTLP configuration and the historical reproduction package remain
  unchanged. No collector vendor configuration was added to the integration.

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
Model and snapshot schemas remain 1.3.0. The related integration updates and new
package releases are now verified below; the older releases remain historical
evidence. No research materials were added to Bering.


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
  PR 7 subsequently pins the separately verified reproduction-package image;
  that package digest is distinct from the Bering runtime image digest.

These changes do not silently change the research's fixed Procrustes/Sheaft pins.

Stack 1.4.0 passed full integration CI before publication, including the actual
native/OBI runtime handoff and pinned-image Kubernetes startup. Its public OCI
chart was pulled at `sha256:05cb6e2e6e8523d28fd1c2f01d1dead6dc5decc90eb33498696220dd0623c60e`;
the package matched the published asset and chart/app versions were both 1.4.0.
Postpublication documentation PR 30 is `ae64ef41d2330b4b7af379a792970b21d9339a5b`;
the release tag still points to the verified release commit above.

Reproduction 1.3.5 retains its `candidate` classification and historical references.
Its current operation reference was actually acquired in run `40798202806`, then
passed an independent strict replay in `40800779500`. The complete original graph
was used; diagnostic graph copies were not adopted. Main run `40802150679` passed
source verification, packaged checks, publication and an anonymous AMD64 Compose
replay with persisted-output and revision-label checks. The public multi-platform
image digest is `sha256:61061c9a0e54b38af0adc12d66aacace5ad9c4acce782bb6c92be294c2e9dfa3`.
The annotated tag and image revision both identify `2b2e012d...`. The attached
999-byte lock file matches its Git blob and API SHA-256
`d61957058992146d85c271bf2dbd47c14fa125ffd330a5b03663c12f931e2829`.
These product compatibility checks are not additional empirical cells.

Postpublication reproduction documentation [PR 5](https://github.com/MB3R-Lab/mb3r-software-complex-repro/pull/5)
passed [exact-head source and packaged checks](https://github.com/MB3R-Lab/mb3r-software-complex-repro/actions/runs/40806219605)
and independent review, then merged as `90828e39b3b261625ceee8d29b0c6db8dcb05589`.
It changes release documentation only; the immutable v1.3.5 tag and image revision
remain `2b2e012d8e85088d6d7bb9e231d0f9cc79ae634f`.
