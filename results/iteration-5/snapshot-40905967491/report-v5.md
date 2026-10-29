# Iteration-5 saved-artifact report

This report copies source-produced evaluations and technical records. It performs no refit, relinking, rescoring, thresholding, or accuracy-based selection.
Technical smoke status is separate from the 108-cell main grid and is not an independent admission or positive contribution claim.

## Fixed grid and execution boundary

| Stored field | Value |
|---|---|
| blocked_main_cells | [["newrelic","deathstarbench","absent",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","absent",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","absent",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","full",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","full",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","full",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","partial",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","partial",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","partial",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","absent",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","absent",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","absent",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","full",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","full",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","full",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","partial",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","partial",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","partial",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","absent",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","absent",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","absent",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","full",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","full",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","full",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","partial",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","partial",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","partial",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."]] |
| declared_main_cells | 108 |
| incomplete_or_missing_main_cells | [["coroot","deathstarbench","absent",6],["coroot","deathstarbench","absent",7],["coroot","deathstarbench","absent",8],["coroot","deathstarbench","full",6],["coroot","deathstarbench","full",7],["coroot","deathstarbench","full",8],["coroot","deathstarbench","partial",6],["coroot","deathstarbench","partial",7],["coroot","deathstarbench","partial",8],["coroot","otel_demo","absent",6],["coroot","otel_demo","absent",7],["coroot","otel_demo","absent",8],["coroot","otel_demo","full",6],["coroot","otel_demo","full",7],["coroot","otel_demo","full",8],["coroot","otel_demo","partial",6],["coroot","otel_demo","partial",7],["coroot","otel_demo","partial",8],["coroot","petclinic","absent",6],["coroot","petclinic","absent",7],["coroot","petclinic","absent",8],["coroot","petclinic","full",6],["coroot","petclinic","full",7],["coroot","petclinic","full",8],["coroot","petclinic","partial",6],["coroot","petclinic","partial",7],["coroot","petclinic","partial",8],["deepflow","deathstarbench","absent",6],["deepflow","deathstarbench","absent",7],["deepflow","deathstarbench","absent",8],["deepflow","deathstarbench","full",6],["deepflow","deathstarbench","full",7],["deepflow","deathstarbench","full",8],["deepflow","deathstarbench","partial",6],["deepflow","deathstarbench","partial",7],["deepflow","deathstarbench","partial",8],["deepflow","otel_demo","absent",6],["deepflow","otel_demo","absent",7],["deepflow","otel_demo","absent",8],["deepflow","otel_demo","full",6],["deepflow","otel_demo","full",7],["deepflow","otel_demo","full",8],["deepflow","otel_demo","partial",6],["deepflow","otel_demo","partial",7],["deepflow","otel_demo","partial",8],["deepflow","petclinic","absent",6],["deepflow","petclinic","absent",7],["deepflow","petclinic","absent",8],["deepflow","petclinic","full",6],["deepflow","petclinic","full",7],["deepflow","petclinic","full",8],["deepflow","petclinic","partial",6],["deepflow","petclinic","partial",7],["deepflow","petclinic","partial",8],["newrelic","deathstarbench","absent",6],["newrelic","deathstarbench","absent",7],["newrelic","deathstarbench","absent",8],["newrelic","deathstarbench","full",6],["newrelic","deathstarbench","full",7],["newrelic","deathstarbench","full",8],["newrelic","deathstarbench","partial",6],["newrelic","deathstarbench","partial",7],["newrelic","deathstarbench","partial",8],["newrelic","otel_demo","absent",6],["newrelic","otel_demo","absent",7],["newrelic","otel_demo","absent",8],["newrelic","otel_demo","full",6],["newrelic","otel_demo","full",7],["newrelic","otel_demo","full",8],["newrelic","otel_demo","partial",6],["newrelic","otel_demo","partial",7],["newrelic","otel_demo","partial",8],["newrelic","petclinic","absent",6],["newrelic","petclinic","absent",7],["newrelic","petclinic","absent",8],["newrelic","petclinic","full",6],["newrelic","petclinic","full",7],["newrelic","petclinic","full",8],["newrelic","petclinic","partial",6],["newrelic","petclinic","partial",7],["newrelic","petclinic","partial",8],["obi","deathstarbench","absent",6],["obi","deathstarbench","absent",7],["obi","deathstarbench","absent",8],["obi","deathstarbench","full",6],["obi","deathstarbench","full",7],["obi","deathstarbench","full",8],["obi","deathstarbench","partial",6],["obi","deathstarbench","partial",7],["obi","deathstarbench","partial",8],["obi","otel_demo","absent",6],["obi","otel_demo","absent",7],["obi","otel_demo","absent",8],["obi","otel_demo","full",6],["obi","otel_demo","full",7],["obi","otel_demo","full",8],["obi","otel_demo","partial",6],["obi","otel_demo","partial",7],["obi","otel_demo","partial",8],["obi","petclinic","absent",6],["obi","petclinic","absent",7],["obi","petclinic","absent",8],["obi","petclinic","full",6],["obi","petclinic","full",7],["obi","petclinic","full",8],["obi","petclinic","partial",6],["obi","petclinic","partial",7],["obi","petclinic","partial",8]] |
| smoke_attempts_excluded_from_main_coverage | true |
| technically_complete_main_cells | 0 |

## Every declared attempt

| Run | Repository | Collector | Stage | System | Mode | Seed | Self-reported complete | Declared transport complete | Full source artifact available | Coverage eligible | Independently admitted | Status | Summary artifact | Summary digest | Full artifact | Full digest | Missing/incomplete reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | absent | 6 | false | true | true | false | false | technical_failure | 12899539679 | sha256:5f7c91b5707bae0f8f9463d745f371cb33afa4cf3dbfc7c4ee2dcfc82fa7d454 | 12900367017 | sha256:5137d6a3a505a10c9b9ab17cb4f8576e31524797e31b3d8a7cca672b8e2dc6d8 | source_evaluation_technically_incomplete |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | full | 6 | false | true | true | false | false | technical_failure | 12899729040 | sha256:c3105c13f55b7318f0b85493577b82b0d315aba17d065d13ebaefcefc02daa33 | 12900786008 | sha256:a9b3fc6590afe5b91f60638be6bd724bfe19a5512e7dc83f87eb2b71e3a2a148 | source_evaluation_technically_incomplete |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | partial | 6 | false | true | true | false | false | technical_failure | 12900696318 | sha256:6db9894081c147f3ab095cd89c2a25b0f548b13f3c4e46711d84395bc16b7fb7 | 12900113822 | sha256:139d1a89b3bb8dc35b0d233253827e49c440a31fd80876c0ca0024d468fa5c41 | source_evaluation_technically_incomplete |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | otel_demo | absent | 6 | false | true | true | false | false | running | 12900143007 | sha256:4a1748f292cd1c71d335a5562dc839a069e964e82e86cfe94fc7f44114ec47d9 | 12901275629 | sha256:3b71143f7d10f849c9848e29f4d956f23c9adb7292eff71c7273d7b7e742eb64 | source_evaluation_technically_incomplete |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | otel_demo | full | 6 | false | true | true | false | false | running | 12899759896 | sha256:f9b45380bbf8998f35ace122001fbf6f400aa610ad57bf2fe0b66c38a12baead | 12899834966 | sha256:4b2e28a052715b95de222a2f6914f2b74dff3679f423c9c1238638184650e6a8 | source_evaluation_technically_incomplete |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | otel_demo | partial | 6 | false | true | true | false | false | running | 12899824429 | sha256:9ef1fd01ce5ce8d6ecf8639d8f2d2be1d9c4b9b1b33d55d6805fb0b8f87efaa0 | 12899978709 | sha256:04d19d268542871564c53ab92179072528dd59a43b6ed832d9eec99cc1bec3a3 | source_evaluation_technically_incomplete |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | petclinic | absent | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | petclinic | full | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | petclinic | partial | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40884914635 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | partial | 6 | false | true | true | false | false | technical_failure | 12902441322 | sha256:f22e92d08b3b1d73c8505dd2592cbf5e9f5bcfa653885bff8c4ed664aa379b36 | 12901603339 | sha256:5b0dcec2b879fcbbca8d1f7fb90a5eccf17866bb264fd85a66a8cd03d65f04d3 | source_evaluation_technically_incomplete |
| 40885990713 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | false | true | true | false | false | technical_failure | 12902762367 | sha256:4187629055b16aa82645782dc4fbef2c41791953f9e75958d29f6f4e242143ca | 12902598140 | sha256:fab2b8ad69fc5c863308ce1a1d392577ed090ed374f1f41e38c2aa3c9b838f5c | source_evaluation_technically_incomplete |
| 40890296710 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | partial | 6 | false | true | true | false | false | technical_failure | 12903798377 | sha256:02a8d063aceb03d146ac7c45aa5881a6e412304841605c349ce77299d8fb7870 | 12905535158 | sha256:694fe0a6f92b49e6c2bf523c7e6a73ab5d117ec5f1c9b43f9e21fd4c76a010ac | source_evaluation_technically_incomplete |
| 40890303219 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | false | true | true | false | false | technical_failure | 12904504707 | sha256:3ba47030bdc0617b8bbfac6ef37433561639908d50a2db4e414f841e1982555f | 12904339074 | sha256:4114a2aebb2019a14be2a8fdc669220b3c37b7799aba5e182909064d414053e6 | source_evaluation_technically_incomplete |
| 40890763831 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | petclinic | absent | 6 | false | true | true | false | false | technical_failure | 12905425997 | sha256:361b6521a236b2c0aa04d0657a60252d1834eb6ee03aedce63c7087e7fb298c3 | 12905002563 | sha256:bbd7b5cbcd8e59862e0e7a77780bc357696036bdeca4a8f4ab8c0453ac7a930c | source_evaluation_technically_incomplete |
| 40895622472 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | partial | 6 | false | true | true | false | false | technical_failure | 12908010750 | sha256:2845d17c641dbdb1c4f18c76b0b26c0e0367eccfcbf3407a32b044cb2b5ed33f | 12907756205 | sha256:f84764ef3eb4d2968d5bfee68381dfc74a8cc29fd637bde63df709595af89a91 | source_evaluation_technically_incomplete |
| 40895637294 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | petclinic | absent | 6 | true | true | true | true | false | smoke_complete | 12907518474 | sha256:1a110ad94d1964f6b8d7fe9d119f09ffcb7572bc8ed3cff04519cc3653a469b3 | 12907623166 | sha256:911d8758eb5a6625cdbd0afe3e070e7035a7362c640236084c4ff0ccdaaf8e22 | unknown |
| 40896064246 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | false | true | true | false | false | technical_failure | 12907516425 | sha256:a90813f7becdf5c4c53104a0830fcef56235c06b5169283414af7f8b604aca0a | 12907860762 | sha256:e90182528b47452d593ebb70be040640e0c9816592a69adb2ad36fca562b8f6c | source_evaluation_technically_incomplete |
| 40898769649 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | partial | 6 | true | true | true | true | false | smoke_complete | 12909436226 | sha256:dcdff8fdc05b9f97ac84ab2f4a6b934e114d4cee7fb8be941eb76f1747153928 | 12909541061 | sha256:1d4e1c9cb822749b5be7728721a0acf278ffa32ed9e82d00061cbf5f289968ac | unknown |
| 40898777011 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | false | true | true | false | false | technical_failure | 12907604591 | sha256:604ae6942620c968f87ad887ccedb94e95414458f13a32dd7fca465a14c8393c | 12908028942 | sha256:d978116fea3e732e6b011edf9adba64aa5d19dc3d556405d10894b82f57895cc | source_evaluation_technically_incomplete |
| 40899601511 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | petclinic | absent | 6 | true | true | true | true | false | smoke_complete | 12910541431 | sha256:a179be88750184a925bd90b4d36346b1c778b49c3f8ab2972f9c6aa7a0e79996 | 12911020083 | sha256:74d27d524ec29d9c2fa70336acc0f8400bfd7c8d058a6637c420eaad0c7b2863 | unknown |
| 40902922833 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | false | true | true | false | false | technical_failure | 12911410794 | sha256:14c125019b228d04901ce21dc44e01d7824da6742d76f21827a617a8f63ad46f | 12910762488 | sha256:39f55c75f59cc5c6ac03a4a72b6da8ba77ddafbd0e36cf1692a59c6d82c228b6 | source_evaluation_technically_incomplete |

## Technical smoke qualification records

| Run | Collector | System | Mode | Seed | Source technical pass | Acquisition valid | Stored problems | Independent admission |
|---|---|---|---|---|---|---|---|---|
| 40880849418 | obi | deathstarbench | absent | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40880849418 | obi | deathstarbench | full | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40880849418 | obi | deathstarbench | partial | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40880849418 | obi | otel_demo | absent | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed","accepted_observation_capture_not_closed"] | false |
| 40880849418 | obi | otel_demo | full | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed","accepted_observation_capture_not_closed"] | false |
| 40880849418 | obi | otel_demo | partial | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed","accepted_observation_capture_not_closed"] | false |
| 40880849418 | obi | petclinic | absent | 6 | unknown | unknown | unknown | false |
| 40880849418 | obi | petclinic | full | 6 | unknown | unknown | unknown | false |
| 40880849418 | obi | petclinic | partial | 6 | unknown | unknown | unknown | false |
| 40884914635 | obi | deathstarbench | partial | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40885990713 | deepflow | petclinic | absent | 6 | false | false | ["collector_provenance_invalid:graph-v5 collector provenance is missing","two_guest_ebpf_origin_control_missing_or_failed","accepted_observation_capture_not_closed"] | false |
| 40890296710 | obi | deathstarbench | partial | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40890303219 | deepflow | petclinic | absent | 6 | false | false | ["collector_provenance_invalid:graph-v5 collector provenance is missing","two_guest_ebpf_origin_control_missing_or_failed","accepted_observation_capture_not_closed"] | false |
| 40890763831 | coroot | petclinic | absent | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40895622472 | obi | deathstarbench | partial | 6 | false | true | [] | false |
| 40895637294 | coroot | petclinic | absent | 6 | true | true | [] | false |
| 40896064246 | deepflow | petclinic | absent | 6 | false | false | ["collector_provenance_invalid:graph-v5 collector provenance is missing","two_guest_ebpf_origin_control_missing_or_failed","accepted_observation_capture_not_closed"] | false |
| 40898769649 | obi | deathstarbench | partial | 6 | true | true | [] | false |
| 40898777011 | deepflow | petclinic | absent | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40899601511 | obi | petclinic | absent | 6 | true | true | [] | false |
| 40902922833 | deepflow | petclinic | absent | 6 | false | true | [] | false |

## Saved main forecasts and external outcomes

| Run | Collector | System | Mode | Seed | Complete | Operation | Source | Variant | Available | Stored forecast | Stored interval | Actual true | Actual false | Actual unknown | Stored reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| unavailable | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown |

## Saved campaign and Actions costs

| Ledger field | Stored value |
|---|---|
| known_completed_job_elapsed_seconds | 14607.0 |
| runs_with_unknown_job_elapsed | 0 |
| known_stored_artifact_bytes | 867112397 |
| runs_with_unknown_artifact_bytes | 0 |
| report_artifact_transfer | {"compact_zip_downloads":18,"compact_zip_received_bytes":944250,"full_zip_recovery_downloads":15,"full_zip_recovery_received_bytes":402194831,"scope":"actual retained HTTP response bytes in this report job, including failed or rejected downloads; unavailable response bytes remain unknown","total_received_bytes":403139081} |
| human_agent_seconds | unknown |
| current_report_job_tail_seconds | unknown |
| scope | only explicitly declared repositories/runs; omitted or inaccessible product work remains unknown |
| overlap_rule | job seconds are compute use; overlapping jobs and parent waits are not campaign wall time |

| Run | Collector | Stage | System | Mode | Seed | Campaign s | Toolchain build s | Toolchain command s | Manual effort measured | Reason |
|---|---|---|---|---|---|---|---|---|---|---|
| 40880849418 | obi | smoke | deathstarbench | absent | 6 | 121.68541055 | 29.79936214 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40880849418 | obi | smoke | deathstarbench | full | 6 | 107.17795546 | 21.457236652 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40880849418 | obi | smoke | deathstarbench | partial | 6 | 106.916571342 | 20.694920503 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40880849418 | obi | smoke | otel_demo | absent | 6 | unknown | 30.050459471 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40880849418 | obi | smoke | otel_demo | full | 6 | unknown | 29.098320092 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40880849418 | obi | smoke | otel_demo | partial | 6 | unknown | 29.279652547 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40880849418 | obi | smoke | petclinic | absent | 6 | unknown | unknown | unknown | unknown | unknown |
| 40880849418 | obi | smoke | petclinic | full | 6 | unknown | unknown | unknown | unknown | unknown |
| 40880849418 | obi | smoke | petclinic | partial | 6 | unknown | unknown | unknown | unknown | unknown |
| 40884914635 | obi | smoke | deathstarbench | partial | 6 | 204.750437006 | 29.762401884 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40885990713 | deepflow | smoke | petclinic | absent | 6 | 59.354809413 | 30.815604344999997 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40890296710 | obi | smoke | deathstarbench | partial | 6 | 201.347097635 | 22.750342886 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40890303219 | deepflow | smoke | petclinic | absent | 6 | 160.693604084 | 29.377815630999997 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40890763831 | coroot | smoke | petclinic | absent | 6 | 255.635358463 | 30.797730125 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40895622472 | obi | smoke | deathstarbench | partial | 6 | 297.154349069 | 23.922550968 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40895637294 | coroot | smoke | petclinic | absent | 6 | 921.655310176 | 29.032697767000002 | 1.784548567 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40896064246 | deepflow | smoke | petclinic | absent | 6 | 73.335884608 | 26.508525064 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40898769649 | obi | smoke | deathstarbench | partial | 6 | 629.366752902 | 23.741258443 | 49.650957433 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40898777011 | deepflow | smoke | petclinic | absent | 6 | 284.383700533 | 26.899899422 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40899601511 | obi | smoke | petclinic | absent | 6 | 1111.979088367 | 30.242466739 | 229.156127421 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40902922833 | deepflow | smoke | petclinic | absent | 6 | 477.306109557 | 30.23993979 | 0.046824699 | false | human preparation time was not instrumented; no full-cost advantage claimed |

Actions jobs, including runs without a campaign artifact:

| Run | Repository | Role | Run status | Run conclusion | Job | Job name | Job status | Job conclusion | Stored elapsed s | Artifacts |
|---|---|---|---|---|---|---|---|---|---|---|
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471648094 | prepare | completed | success | 4.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696616 | campaign (petclinic, partial, 6) | completed | cancelled | 369.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696629 | campaign (otel_demo, full, 6) | completed | cancelled | 171.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696690 | campaign (otel_demo, partial, 6) | completed | cancelled | 173.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696742 | campaign (otel_demo, absent, 6) | completed | cancelled | 175.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696793 | campaign (petclinic, full, 6) | completed | cancelled | 369.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696803 | campaign (deathstarbench, absent, 6) | completed | failure | 245.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696819 | campaign (deathstarbench, partial, 6) | completed | failure | 214.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696826 | campaign (deathstarbench, full, 6) | completed | failure | 218.0 | 15 |
| 40880849418 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123471696833 | campaign (petclinic, absent, 6) | completed | cancelled | 369.0 | 15 |
| 40884914635 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123485923133 | prepare | completed | success | 3.0 | 3 |
| 40884914635 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123485975559 | campaign (deathstarbench, partial, 6) | completed | failure | 342.0 | 3 |
| 40885990713 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123489723504 | prepare | completed | success | 3.0 | 2 |
| 40885990713 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123489768574 | campaign (petclinic, absent, 6) | completed | failure | 190.0 | 2 |
| 40890296710 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123504955360 | prepare | completed | success | 3.0 | 3 |
| 40890296710 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123504998136 | campaign (deathstarbench, partial, 6) | completed | failure | 338.0 | 3 |
| 40890303219 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123504981046 | prepare | completed | success | 3.0 | 2 |
| 40890303219 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123505033282 | campaign (petclinic, absent, 6) | completed | failure | 295.0 | 2 |
| 40890763831 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123506616975 | prepare | completed | success | 3.0 | 2 |
| 40890763831 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123506670186 | campaign (petclinic, absent, 6) | completed | failure | 397.0 | 2 |
| 40895622472 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123523801259 | prepare | completed | success | 2.0 | 4 |
| 40895622472 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123523845192 | campaign (deathstarbench, partial, 6) | completed | failure | 421.0 | 4 |
| 40895637294 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123523850039 | prepare | completed | success | 2.0 | 3 |
| 40895637294 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123523890856 | campaign (petclinic, absent, 6) | completed | success | 1067.0 | 3 |
| 40896064246 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123525383445 | prepare | completed | success | 3.0 | 2 |
| 40896064246 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123525437245 | campaign (petclinic, absent, 6) | completed | failure | 208.0 | 2 |
| 40898769649 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123535031052 | prepare | completed | success | 3.0 | 4 |
| 40898769649 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123535085159 | campaign (deathstarbench, partial, 6) | completed | success | 757.0 | 4 |
| 40898777011 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123535061359 | prepare | completed | success | 3.0 | 2 |
| 40898777011 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123535116154 | campaign (petclinic, absent, 6) | completed | failure | 404.0 | 2 |
| 40899601511 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123537952353 | prepare | completed | success | 4.0 | 3 |
| 40899601511 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123538022599 | campaign (petclinic, absent, 6) | completed | success | 1263.0 | 3 |
| 40902922833 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123549819222 | prepare | completed | success | 3.0 | 3 |
| 40902922833 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123549868522 | campaign (petclinic, absent, 6) | completed | failure | 613.0 | 3 |
| 40900996676 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123542915526 | checks | completed | success | 39.0 | 0 |
| 40900996676 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123542916005 | control-fixture-v5 | completed | success | 35.0 | 0 |
| 40899833610 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123538765475 | toolchain | completed | success | 76.0 | 1 |
| 40898462595 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123533933163 | checks | completed | success | 38.0 | 0 |
| 40898462595 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123533933778 | control-fixture-v5 | completed | success | 19.0 | 0 |
| 40895877074 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123524700863 | control-fixture-v5 | completed | success | 17.0 | 0 |
| 40895877074 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123524701341 | checks | completed | success | 37.0 | 0 |
| 40895444290 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123523158263 | checks | completed | success | 41.0 | 0 |
| 40895444290 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123523158968 | control-fixture-v5 | completed | success | 22.0 | 0 |
| 40894248440 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123518918701 | checks | completed | success | 45.0 | 0 |
| 40894248440 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123518919237 | control-fixture-v5 | completed | failure | 16.0 | 0 |
| 40890810980 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123506774788 | control-fixture-v5 | completed | success | 21.0 | 0 |
| 40890810980 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123506775225 | checks | completed | success | 45.0 | 0 |
| 40889975595 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123503794910 | control-fixture-v5 | completed | success | 18.0 | 0 |
| 40889975595 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123503795442 | checks | completed | success | 47.0 | 0 |
| 40885659304 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123488542805 | checks | completed | success | 42.0 | 0 |
| 40885659304 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123488543376 | control-fixture-v5 | completed | success | 20.0 | 0 |
| 40883942639 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123482513643 | control-fixture-v5 | completed | success | 20.0 | 0 |
| 40883942639 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123482513972 | checks | completed | success | 44.0 | 0 |
| 40878924384 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123464898796 | checks | completed | success | 53.0 | 0 |
| 40879223434 | MB3R-Lab/Bering | product_ci | completed | success | 123465947870 | release | completed | success | 468.0 | 0 |
| 40877778287 | MB3R-Lab/Bering | product_ci | completed | success | 123460959558 | checks | completed | success | 63.0 | 0 |
| 40876595689 | MB3R-Lab/Bering | product_ci | completed | success | 123456890583 | dry-run | completed | success | 395.0 | 1 |
| 40876595701 | MB3R-Lab/Bering | product_ci | completed | success | 123456891005 | checks | completed | success | 22.0 | 0 |
| 40876595722 | MB3R-Lab/Bering | product_ci | completed | success | 123456890416 | smoke | completed | success | 55.0 | 1 |
| 40874629052 | MB3R-Lab/Bering | product_ci | completed | success | 123450160020 | smoke | completed | success | 57.0 | 1 |
| 40874629030 | MB3R-Lab/Bering | product_ci | completed | success | 123450160287 | checks | completed | success | 23.0 | 0 |
| 40874629029 | MB3R-Lab/Bering | product_ci | completed | success | 123450160168 | dry-run | completed | success | 309.0 | 1 |
| 40876610601 | MB3R-Lab/Procrustes | product_ci | completed | success | 123456938131 | checks | completed | success | 16.0 | 1 |
| 40876461856 | MB3R-Lab/Procrustes | product_ci | completed | success | 123456423792 | checks | completed | success | 17.0 | 1 |
| 40874642494 | MB3R-Lab/Procrustes | product_ci | completed | success | 123450206067 | checks | completed | success | 19.0 | 1 |
| 40888915800 | MB3R-Lab/mb3r-stack | product_ci | completed | success | 123500040811 | validate | completed | success | 143.0 | 1 |
| 40888384949 | MB3R-Lab/mb3r-stack | product_ci | completed | success | 123498153197 | validate | completed | success | 135.0 | 1 |
| 40886588360 | MB3R-Lab/mb3r-stack | product_ci | completed | success | 123491831572 | release | completed | success | 18.0 | 0 |
| 40886588360 | MB3R-Lab/mb3r-stack | product_ci | completed | success | 123492027379 | Download and run the published preflight without authentication | completed | success | 19.0 | 0 |
| 40886462764 | MB3R-Lab/mb3r-stack | product_ci | completed | success | 123491386951 | validate | completed | success | 133.0 | 1 |
| 40885945200 | MB3R-Lab/mb3r-stack | product_ci | completed | success | 123489550982 | validate | completed | success | 139.0 | 1 |
| 40883389521 | MB3R-Lab/mb3r-stack | product_ci | completed | success | 123480568136 | validate | completed | success | 141.0 | 1 |
| 40881171793 | MB3R-Lab/mb3r-stack | product_ci | completed | failure | 123472761595 | validate | completed | failure | 46.0 | 1 |
| 40888154808 | MB3R-Lab/Sheaft | product_ci | completed | success | 123497332698 | verify-schema-contract | completed | success | 29.0 | 0 |
| 40888154744 | MB3R-Lab/Sheaft | product_ci | completed | success | 123497332818 | verify-ci-template-smoke | completed | success | 60.0 | 0 |
| 40888155130 | MB3R-Lab/Sheaft | product_ci | completed | success | 123497334477 | validate-release-surface | completed | success | 470.0 | 1 |
| 40886639089 | MB3R-Lab/Sheaft | product_ci | completed | success | 123492016277 | validate-release-surface | completed | success | 456.0 | 1 |
| 40886639081 | MB3R-Lab/Sheaft | product_ci | completed | success | 123492016371 | verify-schema-contract | completed | success | 33.0 | 0 |
| 40886639078 | MB3R-Lab/Sheaft | product_ci | completed | success | 123492016328 | verify-ci-template-smoke | completed | success | 55.0 | 0 |
| 40888435266 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498331069 | fossa | completed | failure | 5.0 | 0 |
| 40888435331 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123498331039 | analysis | completed | success | 54.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498334321 | checklicense | completed | success | 10.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498334608 | yamllint | completed | success | 7.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498334872 | misspell | completed | success | 14.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498335068 | linkspector | completed | failure | 63.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498335221 | build_images / protobufcheck | completed | success | 220.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498335452 | Procrustes static preflight | completed | success | 27.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498335574 | markdownlint | completed | success | 30.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123498335722 | sanity | completed | success | 4.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492474 | build_images / build_and_push_images (./src/email/Dockerfile, email, ./, true) | completed | failure | 11.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492480 | build_images / build_and_push_images (./src/accounting/Dockerfile, accounting, ./, true) | completed | failure | 10.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492568 | build_images / build_and_push_images (./src/ad/Dockerfile, ad, ./, true) | completed | failure | 11.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492631 | build_images / build_and_push_images (./src/frontend/Dockerfile, frontend, ./, true) | completed | failure | 11.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492633 | build_images / build_and_push_images (./src/flagd-ui/Dockerfile, flagd-ui, ./, true) | completed | failure | 11.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492688 | build_images / build_and_push_images (./src/frontend/Dockerfile.cypress, frontend-tests, ./, true) | completed | failure | 8.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492864 | build_images / build_and_push_images (./src/frontend-proxy/Dockerfile, frontend-proxy, ./, true) | completed | failure | 9.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492916 | build_images / build_and_push_images (./src/product-catalog/Dockerfile, product-catalog, ./, true) | completed | failure | 7.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492973 | build_images / build_and_push_images (./src/kafka/Dockerfile, kafka, ./, true) | completed | failure | 10.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500492980 | build_images / build_and_push_images (./src/opensearch/Dockerfile, opensearch, ./, true) | completed | failure | 12.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493000 | build_images / build_and_push_images (./src/payment/Dockerfile, payment, ./, true) | completed | failure | 9.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493022 | build_images / build_and_push_images (./src/image-provider/Dockerfile, image-provider, ./, true) | completed | failure | 11.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493026 | build_images / build_and_push_images (./src/checkout/Dockerfile, checkout, ./, true) | completed | failure | 9.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493046 | build_images / build_and_push_images (./test/tracetesting/Dockerfile, traceBasedTests, ./, true) | completed | failure | 13.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493052 | build_images / build_and_push_images (./src/shipping/Dockerfile, shipping, ./, true) | completed | failure | 8.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493063 | build_images / build_and_push_images (./src/llm/Dockerfile, llm, ./, true) | completed | failure | 9.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493115 | build_images / build_and_push_images (./src/recommendation/Dockerfile, recommendation, ./, true) | completed | failure | 11.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493132 | build_images / build_and_push_images (./src/cart/src/Dockerfile, cart, ./, false) | completed | failure | 12.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493200 | build_images / build_and_push_images (./src/load-generator/Dockerfile, load-generator, ./, true) | completed | failure | 10.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493219 | build_images / build_and_push_images (./src/currency/Dockerfile, currency, ./, true) | completed | failure | 7.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493223 | build_images / build_and_push_images (./src/fraud-detection/Dockerfile, fraud-detection, ./, true) | completed | failure | 8.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500493517 | build_images / build_and_push_images (./src/product-reviews/Dockerfile, product-reviews, ./, true) | completed | failure | 7.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500494780 | build_images / build_and_push_images (./src/quote/Dockerfile, quote, ./, true) | completed | failure | 11.0 | 1 |
| 40888435462 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | failure | 123500740176 | build-test | completed | failure | 3.0 | 1 |
| 40887193858 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | skipped | 123494074883 | assign-reviewers | completed | skipped | -9.0 | 0 |
| 40887193681 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | skipped | 123493991657 | dependabot-auto-update-protobuf-diff | completed | skipped | 0.0 | 0 |
| 40887193928 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493988529 | label | completed | success | 5.0 | 0 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986113 | checklicense | completed | success | 16.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986161 | sanity | completed | success | 4.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986212 | linkspector | completed | success | 62.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986291 | Procrustes static preflight | completed | success | 21.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986319 | yamllint | completed | success | 7.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986332 | markdownlint | completed | success | 24.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986385 | misspell | completed | success | 22.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986437 | build_images / protobufcheck | completed | success | 202.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941882 | build_images / build_and_push_images (./src/recommendation/Dockerfile, recommendation, ./, true) | completed | success | 21.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941898 | build_images / build_and_push_images (./src/flagd-ui/Dockerfile, flagd-ui, ./, true) | completed | success | 22.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941908 | build_images / build_and_push_images (./src/opensearch/Dockerfile, opensearch, ./, true) | completed | success | 23.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941925 | build_images / build_and_push_images (./src/payment/Dockerfile, payment, ./, true) | completed | success | 19.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941927 | build_images / build_and_push_images (./src/frontend-proxy/Dockerfile, frontend-proxy, ./, true) | completed | success | 15.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941931 | build_images / build_and_push_images (./src/email/Dockerfile, email, ./, true) | completed | success | 14.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941982 | build_images / build_and_push_images (./src/accounting/Dockerfile, accounting, ./, true) | completed | success | 16.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495941997 | build_images / build_and_push_images (./src/frontend/Dockerfile, frontend, ./, true) | completed | success | 20.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942037 | build_images / build_and_push_images (./src/product-reviews/Dockerfile, product-reviews, ./, true) | completed | success | 13.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942074 | build_images / build_and_push_images (./src/checkout/Dockerfile, checkout, ./, true) | completed | success | 21.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942085 | build_images / build_and_push_images (./src/product-catalog/Dockerfile, product-catalog, ./, true) | completed | success | 15.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942096 | build_images / build_and_push_images (./src/frontend/Dockerfile.cypress, frontend-tests, ./, true) | completed | success | 17.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942100 | build_images / build_and_push_images (./src/ad/Dockerfile, ad, ./, true) | completed | success | 15.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942125 | build_images / build_and_push_images (./src/load-generator/Dockerfile, load-generator, ./, true) | completed | success | 19.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942140 | build_images / build_and_push_images (./src/fraud-detection/Dockerfile, fraud-detection, ./, true) | completed | success | 15.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942173 | build_images / build_and_push_images (./src/llm/Dockerfile, llm, ./, true) | completed | success | 19.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942213 | build_images / build_and_push_images (./src/shipping/Dockerfile, shipping, ./, true) | completed | success | 18.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942265 | build_images / build_and_push_images (./src/cart/src/Dockerfile, cart, ./, false) | completed | success | 11.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942345 | build_images / build_and_push_images (./src/image-provider/Dockerfile, image-provider, ./, true) | completed | success | 14.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942370 | build_images / build_and_push_images (./src/kafka/Dockerfile, kafka, ./, true) | completed | success | 20.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495942621 | build_images / build_and_push_images (./src/quote/Dockerfile, quote, ./, true) | completed | success | 18.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495943003 | build_images / build_and_push_images (./src/currency/Dockerfile, currency, ./, true) | completed | success | 14.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123495943225 | build_images / build_and_push_images (./test/tracetesting/Dockerfile, traceBasedTests, ./, true) | completed | success | 20.0 | 1 |
| 40887193770 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123496316671 | build-test | completed | success | 4.0 | 1 |
| 40887193685 | MB3R-Lab/opentelemetry-demo-mb3r-stack | product_ci | completed | success | 123493986146 | MB3R / recommendations gate | completed | success | 326.0 | 1 |
| 40902646348 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123548819409 | checks | completed | success | 47.0 | 0 |
| 40902646348 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123548819649 | control-fixture-v5 | completed | success | 24.0 | 0 |
| 40902931486 | a-a-k/ebpf-model-discovery-experiments | report | completed | failure | 123549848327 | report | completed | failure | 80.0 | 1 |
| 40905568198 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123559248398 | control-fixture-v5 | completed | success | 22.0 | 0 |
| 40905568198 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123559248816 | checks | completed | success | 36.0 | 0 |

Human/agent preparation effort: unknown

Current report-job unfinished tail: unknown

The lossless aggregate retains every source evaluation object, including detailed DB, baseline, class, async, causal and cost fields not expanded into new summaries here.
