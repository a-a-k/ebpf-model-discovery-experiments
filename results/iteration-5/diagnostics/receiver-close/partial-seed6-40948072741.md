# OBI OTel partial seed 6 failure diagnosis

Read-only diagnosis independent of seed 8; no replay, rescoring, dispatch,
cancellation, or result promotion was performed.

## Identity, costs, and retained evidence

- Parent run `40948072741`, job `123708628357`, cell
  `obi / otel_demo / partial / 6`, source commit
  `6a616c685c10a7e17a80b1dda452d9da9e02a693`.
- The job ran from `2026-10-29T20:20:09Z` through
  `2026-10-29T23:02:45Z` (9,756 seconds). The failed continuation step ran
  4,502 seconds. Retained status reports 34,951 observed operations and
  9,403.058413979 elapsed seconds; these costs remain charged.
- Compact artifact `12939228701` is 38,373,908 bytes. Its independently
  received SHA-256 equals the API digest
  `eadb1da2f740ac151fd1aab8200ff5b4f6dc217c3783432addc2432326a2e8d3`;
  safe extraction and all member CRCs passed. Verification record SHA-256:
  `5ec7ced6d3d6e1af20724bd99c84cf50f9f0afe52b7262f358a2f289e48ebee4`.
- Authoritative compact members:
  - `status.json`: SHA-256
    `4aebfb11d7731ac1adb3bdc1dbccbe159d8e1592b069fbf258d0dd00daa4b6b3`;
  - `evaluation-v5.json`: SHA-256
    `64ff17da153852d369940005331bbf732889abbffa7f0ee332ac793e681090f5`;
  - `observations/drain-evidence.json`: SHA-256
    `59839dff5cf63c957d6b24d0421f140e158612475c1a5624d9f060b3babcae4f`;
  - `observations/collector.json`: SHA-256
    `683b0e88f82d1ee36fe80c17b1cb4834c5d9f05a769eb4ac5e2aa956385f27c3`.

## Independently established mechanism

The exact failed step was `Continue discovery and validation on the same live
guests`. It ended at `22:59:00Z` with
`RuntimeError('obi final drain is technically invalid')`. The saved evaluator
sets `complete_for_evaluation=false`, `primary_series_result=false`, and reports
`accepted_observation_capture_not_closed`.

The compact evidence independently establishes the historical 30-second normal
receiver-close mechanism:

1. At commit `6a616c6`, `collectors_v5.py:1072-1083` terminates each receiver,
   calls `process.wait(timeout=30)`, and on `TimeoutExpired` sets
   `forced=True`, kills the process, and waits up to five additional seconds.
2. Node A matches that branch exactly: receiver return code `-9`,
   `forced_kill=true`, missing `receiver-closed-a.json`, handlers not joined,
   saved bytes invalid, and parent hash verification false. Historical
   `final_drain` therefore raises at line 1012.
3. Node B and native independently closed correctly: return code 0, no forced
   kill, joined handlers, valid saved bytes, durable checkpoints, and successful
   parent hash verification.

This is not an OBI collector shutdown failure. Both OBI collectors stopped with
exit code 0, `OOMKilled=false`, restart count 0, no SIGKILL event, empty state
error, successful stop command, graceful-success marker, and no retained
source-specific failure marker. Post-termination acceptance barriers returned
HTTP 200 on all three receivers. They recorded 1,567,335,958 A bytes,
159,583,273 B bytes, and 587 native bytes, but A has no durable closure
checkpoint proving that its accepted bytes were completely closed and hashed.
The selected-agent positive control is valid on both guests.

Thus seed 6 is technically invalid specifically at saved node-A receiver
closure. It is not evidence of application acquisition failure, protocol
incapability, exporter failure, kernel loss, or OOM. This conclusion was derived
from seed 6 evidence rather than inferred from seed 8.

## Repair boundary

The later reviewed repair removes the arbitrary normal-close deadline and waits
for receiver exit before applying the same durable checkpoint, joined-handler,
saved-byte, and parent-hash gates. This old attempt cannot be retrospectively
admitted; a fresh matching repeat is required to demonstrate the repaired
behavior. No performance or causal advantage is claimed.
