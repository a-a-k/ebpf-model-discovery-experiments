# Preliminary diagnosis of adverse OTel checkout outcomes

The completed Coroot/OTel partial-tracing main runs retain checkout successes of
2686/3200, 2072/3200 and 518/3200. All corresponding model forecasts are
unavailable. These outcomes remain in the comparison; their unfavorable values
are not grounds for a replacement run. The unchanged review records are in
[the nine-cell publication](../results/iteration-5/main-review-41025655518/SOURCE.md).

For seed 8, the retained frontend log contains cart and shipping dependency errors:
DNS/connect timeouts, closed or reset connections, shipping HTTP 408/400 responses
and `ECONNRESET`. Errors also occur in a state-11 target block whose two controlled
product replicas passed the pre-load TCP censuses. Thus the prescribed failure
of the controlled product replicas alone does
not explain every unsuccessful checkout. Resource samples show elevated guest
load and checkout CPU/memory pressure. Saturation or connection instability is a
plausible mechanism, but the exact root cause and any contribution from the
collector are not established. The selected kernel log does not establish an
OOM, and final healthy containers do not prove that no earlier transient restart
occurred.

The concentration of latencies around 15 seconds is **not an experiment deadline**.
At the actual campaign source `c5df32ffc3039136c184b7915337836c39db811f`, the v5
adapter resolves operations to the uncapped v4 implementation, which rejects a
supplied operation deadline and calls the transport with `timeout=None`. The
transport waits for the response body. The legacy capped adapter method is not
the method used by this campaign. Completed evaluated failures are not
automatically all HTTP-negative responses: payload and postcondition checks can
also reject an HTTP 200 response.

The two Envoy proxies have different configurations. The selected deployed
product-catalog router explicitly sets its route timeout to `0s`. The external
entry instead publishes port 18080 to the application's `frontend-proxy:8080`.
Its captured image, `ghcr.io/open-telemetry/demo:3.0.0-frontend-proxy`, resolves to
OCI index `sha256:1c53bfb596970a014682925f804c686762c0c593949ce58a90ac38563f317841`.
The actual partial-mode service has no configuration mount, command override or
entrypoint override. The image runs `envsubst` on its embedded template and then
starts Envoy. The exact embedded catch-all route selects `frontend` and omits
`timeout`; its connection-manager timeout fields are also absent.

Envoy documents a 15-second default for the
[route timeout](https://www.envoyproxy.io/docs/envoy/v1.39.1/faq/configuration/timeouts).
The deployed frontend configuration therefore exposes a native proxy timer that
is consistent with the approximately 15-second concentration. The catalog
router's `0s` setting does not disable this separate timer. This configuration
evidence does not attribute every failed checkout to that timer, establish an
individual timeout response, or identify the cause of the upstream delays.
Per-attempt response correlation and any collector contribution remain unproved.

Both reviewers checked the [selected configuration and immutable image evidence](../results/iteration-5/otel-frontend-proxy-41004296165/root-configuration-review.json).
The image proof uses 9,749 bytes of public registry JSON and the single
2,445-byte static-template COPY layer; a separate base-image metadata comparison
used another 6,620 bytes of JSON. No complete image, base or binary layer was pulled.
The selected template has SHA-256
`e39bb0479ad16086db393df37bded2f4aa72ff4ad98fc75b2d320f58c26908c0`.
It differs from the later pinned upstream checkout's template, so that checkout
alone cannot establish the prebuilt image's configuration or exact Envoy binary
version. The actual template and complete index/manifest/config chain are
retained with the review. This is a diagnosis of existing historical evidence;
the fresh matched matrix and its outcome rules are unchanged.

This runtime diagnosis is separate from graph coverage. A graph without the
required entry/dependency evidence does not yield a supported forecast in this
pipeline; that does not cause an application request to fail. Likewise, runtime
errors do not establish a fundamental limitation of eBPF or Coroot. The seed-8
logs support these narrow observations; an identical error mechanism for seeds
6/7 has not been confirmed from their logs.

## Preserved sources and verification limits

Source run: [41004296165](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/41004296165).
Campaign artifact `12961026796` contains 1,356,339,755 bytes, API ZIP SHA-256
`fe39cf4ee30f9e4180f69a996965ed35ac252cd71991d04f5c603ce2728d8c8a`.
Only selected members were inspected locally; no complete ZIP, complete event
history or independent raw terminal-response journal inspection is claimed here.

| Selected member | SHA-256 |
|---|---|
| `native/final/application-logs/a-frontend.log` | `26804484bc27217bf677fedce610ba1f9310435d9b6455192ba5b797a7538775` |
| `native/final/application-logs/a-shipping.log` | `b626228fe2341e56f9e22cb59dfbcf5375572078dbff17b06d65e75679997cc1` |
| `blocks.json` | `c0e4b2faad60387ceb5523345b5de60cbc4eaf1d4f877f7ff91361066fac105e` |
| `infrastructure/resources/guest-a-samples.txt` | `06f6639536716258f824ed6503f567ac6a7730ddf7c35185b1616189bab74cc4` |
| `infrastructure/resources/kernel-latest.txt` | `bdbd8f2844d035d53adfec7b2030c17a526a00eb45ed47f37d8adc38a8c6d2da` |

The operation and transport implementation is retained at the exact source:
[v5 adapter bridge](https://github.com/a-a-k/ebpf-model-discovery-experiments/blob/c5df32ffc3039136c184b7915337836c39db811f/systems/otel_demo/experiment_v5.py),
[uncapped operations](https://github.com/a-a-k/ebpf-model-discovery-experiments/blob/c5df32ffc3039136c184b7915337836c39db811f/systems/otel_demo/experiment_v4.py),
[uncapped transport](https://github.com/a-a-k/ebpf-model-discovery-experiments/blob/c5df32ffc3039136c184b7915337836c39db811f/src/ebpf_discovery/transport_v4.py).
