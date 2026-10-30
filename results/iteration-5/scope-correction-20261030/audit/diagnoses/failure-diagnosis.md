# OBI DeathStarBench full seed 6 failure, run 40947264867

Read-only diagnosis. No replay, refit, artifact promotion, or code change was
performed. Parent source is commit
`86b5deb19f7ba239c6f0ff40e8b098fd7e6e7e44`; worker source is
`51c9697ed71bfb98919936c95440e0a21ed6731b`.

## Confirmed failure chain

This is **not** the historical 30-second receiver-close failure.

1. The parent training prefix and checkpoint completed. It dispatched worker run
   `40962996489` for the immutable training artifact `12936497476`.
2. The worker's unchanged full-prefix toolchain step succeeded. Retained
   `worker-status.json` says `status=complete`, `checkpoint_unchanged=true`, no
   new application traffic, and 6960 toolchain files.
3. The worker's lossless packaging step then failed while independently
   verifying the just-created archive against the original output tree:
   `ValueError('archive bytes differ from original output')`. The packaging proof
   records 6986 files, 128 directories and 8,621,209,854 uncompressed bytes. It
   retained more than 54 GB free disk after the failure, so this is not a disk
   exhaustion diagnosis.
4. Because normal packaging failed, worker artifact `12941271277` contains only
   six failure-proof files (6,288-byte ZIP), not the five-file typed worker
   package required by `artifact_transport_v4.unpack`.
5. The parent downloaded that failure artifact and correctly rejected it with
   `ValueError('unexpected package layout')` in `forecast_on_worker`; no forecast
   freeze or target phase followed. `status.json` therefore retains
   `technical_failure`, 24,615 observed operations and 11,137.858563503 seconds.

The exact original worker-output path whose bytes changed between archive
creation and verification is **not retained**: the verifier raises a generic
message and deletes the partial archive/manifest. A concurrent or late mutation
of at least one worker-output file is the confirmed proximal condition; naming a
particular file or writer would require evidence not present in this failed run.

## Receiver and collector evidence

The subsequent best-effort final drain is valid and distinct from the failure:
both OBI collectors exited 0, were not OOM-killed, had no restart or SIGKILL
event, and retained clean shutdown markers. A/B/native receiver checkpoints all
returned 0, joined in-flight handlers, validated saved bytes and passed parent
hash verification. Thus neither receiver close nor collector shutdown caused the
technical failure. The retained drain scope still does not prove zero kernel,
producer, or pre-receiver exporter loss.

## Retained costs and source evidence

- Parent job: started `2026-10-29T20:14:51Z`, completed
  `2026-10-29T23:29:35Z`; continuation step ran 5,115 seconds.
- Parent campaign elapsed: 11,137.858563503 seconds.
- Worker: checkpoint validation 347.309282973 s, dispatch 1.335632827 s,
  parent wait 4,645.14798366 s, worker-output ZIP download 0.444225883 s, extract
  0.00300463 s. Output transfer/import are null because typed packaging failed.
- Worker package verification: 41.238545769 s; typed transport wrapper:
  41.335642242 s. These are retained costs, not evidence of improvement.

Selected parent artifact `12941426430` evidence is under `full-selected/`.
`download-provenance.json` SHA-256 is
`d9bb40ece345105f72fc446fa1a8ff5f8642c4db004a8ec895f41cee0d398fac`;
the whole 4,627,884,270-byte full ZIP was not downloaded or locally hash-claimed.
The verified handoff payload is 98,852 bytes, SHA-256
`5de109dfb9dff1d084781d12755300a98a3d347003e7450f4a6465d875fe9f57`.
Extracted worker packaging proof SHA-256 is
`5afc5fc2333c4aac257bc6b138526f46a99890b569dce14cc7baf6fc0fc7da6b`;
worker-status SHA-256 is
`d03a1110fb543ae928a904dcc87292f9a820764507ca086fc5eb67c6e04f56e7`.

The run remains a retained technical failure and is not admissible as a completed
main cell without a separately reviewed repair and exact repeat.
