# OBI OTel partial seed 8 failure diagnosis

Read-only diagnosis; no replay, rescoring, dispatch, cancellation, or result
promotion was performed.

## Identity and retained evidence

- Parent run `40948072741`, job `123708628420`, cell
  `obi / otel_demo / partial / 8`, source commit
  `6a616c685c10a7e17a80b1dda452d9da9e02a693`.
- The job ran from `2026-10-29T20:20:09Z` through
  `2026-10-29T22:56:52Z` (9,403 seconds). The failed continuation step ran
  4,347 seconds. Retained status reports 34,951 observed operations and
  9,061.983028669 elapsed seconds; these costs remain charged.
- Compact artifact `12939626858` is 37,967,405 bytes. Its verified received
  SHA-256 equals the API digest
  `425d17a3a4095cc13c6ca521f2332b99b564a97647120b82c3b1041b2c87906d`;
  safe extraction and every member CRC passed. Verification record SHA-256:
  `7dbfacbbf257883431912bfec43682e644510913ea236157e189ee993897b3a4`.
- Authoritative compact members:
  - `status.json`: SHA-256
    `899a2ced99adf7d5b30aa75c644e6ce3062d322f36b15f9df71434f9019f3dc0`;
  - `evaluation-v5.json`: SHA-256
    `6f6ca617e9588a21376fca1f23eb5102f9c4232b03da971fb48c2392860ea2ab`;
  - `observations/drain-evidence.json`: SHA-256
    `f7da193aadf445b95c3df0092fd16c81df78f92048664dddf55359bf1ff0dba9`;
  - `observations/collector.json`: SHA-256
    `7943f1e3862249b7fa953734101e021411c1b404ec75c874c0100d49ab981db8`.

## Confirmed failure

The exact failed step was `Continue discovery and validation on the same live
guests`. It ended at `22:53:21Z` with
`RuntimeError('obi final drain is technically invalid')`; the retained evaluator
therefore sets `complete_for_evaluation=false`, `primary_series_result=false`,
and reports `accepted_observation_capture_not_closed`.

This is the already repaired old normal-receiver 30-second closure mechanism:

1. At source commit `6a616c6`, `collectors_v5.py:1072-1083` terminates each
   receiver, calls `process.wait(timeout=30)`, and on `TimeoutExpired` sets
   `forced=True`, kills the process, and waits up to five more seconds.
2. Retained node-A evidence is exactly that branch: receiver return code `-9`,
   `forced_kill=true`, missing `receiver-closed-a.json`,
   `in_flight_handlers_joined=false`, `saved_bytes_valid=false`, and no parent
   hash verification. The final drain then raises at historical line 1012.
3. Node B and native closed normally: return code 0, no forced kill, joined
   handlers, valid saved bytes, durable checkpoints, and successful parent hash
   verification.

The failure is not an OBI collector shutdown failure. Both pinned OBI containers
stopped with exit code 0, `OOMKilled=false`, restart count 0, no SIGKILL event,
empty state error, successful stop command, graceful-success log marker, and no
source-specific failure marker. The post-termination acceptance barriers also
returned HTTP 200 on A, B, and native. They recorded 1,630,820,963 A bytes,
172,741,734 B bytes, and 587 native bytes after their barriers, but A lacks the
durable receiver checkpoint needed to prove those accepted bytes were completely
closed and hashed.

The retained selected-agent positive control is independently valid on both
guests. Therefore this attempt is technically invalid specifically at saved
node-A receiver closure; it is not evidence of missing application acquisition,
protocol incapability, exporter failure, kernel loss, or OOM.

## Repair boundary

The later reviewed repair replaces the normal `wait(timeout=30)`/kill branch
with an unbounded normal `wait()` followed by the same durable checkpoint, joined
handler, saved-byte, and parent-hash gates. This old attempt cannot be
retrospectively admitted. A matching fresh repeat is required to demonstrate the
new closure behavior; no causal or performance advantage is inferred here.
