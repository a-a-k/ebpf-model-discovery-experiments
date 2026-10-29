# Iteration-5 saved-artifact report

This report copies source-produced evaluations and technical records. It performs no refit, relinking, rescoring, thresholding, or accuracy-based selection.
Technical smoke status is separate from the 108-cell main grid and is not an independent admission or positive contribution claim.

## Fixed grid and execution boundary

| Stored field | Value |
|---|---|
| blocked_main_cells | [["newrelic","deathstarbench","absent",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","absent",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","absent",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","full",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","full",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","full",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","partial",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","partial",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","deathstarbench","partial",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","absent",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","absent",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","absent",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","full",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","full",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","full",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","partial",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","partial",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","otel_demo","partial",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","absent",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","absent",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","absent",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","full",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","full",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","full",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","partial",6,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","partial",7,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."],["newrelic","petclinic","partial",8,"No authorized existing New Relic license key or verified local collector codec; no replacement or synthesized credentials."]] |
| declared_main_cells | 108 |
| incomplete_or_missing_main_cells | [["coroot","deathstarbench","absent",6],["coroot","deathstarbench","absent",7],["coroot","deathstarbench","absent",8],["coroot","deathstarbench","full",6],["coroot","deathstarbench","full",7],["coroot","deathstarbench","full",8],["coroot","deathstarbench","partial",6],["coroot","deathstarbench","partial",7],["coroot","deathstarbench","partial",8],["coroot","otel_demo","absent",6],["coroot","otel_demo","absent",7],["coroot","otel_demo","absent",8],["coroot","otel_demo","full",6],["coroot","otel_demo","full",7],["coroot","otel_demo","full",8],["coroot","otel_demo","partial",6],["coroot","otel_demo","partial",7],["coroot","otel_demo","partial",8],["coroot","petclinic","absent",6],["coroot","petclinic","absent",7],["coroot","petclinic","absent",8],["coroot","petclinic","full",6],["coroot","petclinic","full",7],["coroot","petclinic","full",8],["coroot","petclinic","partial",6],["coroot","petclinic","partial",7],["coroot","petclinic","partial",8],["deepflow","deathstarbench","absent",6],["deepflow","deathstarbench","absent",7],["deepflow","deathstarbench","absent",8],["deepflow","deathstarbench","full",6],["deepflow","deathstarbench","full",7],["deepflow","deathstarbench","full",8],["deepflow","deathstarbench","partial",6],["deepflow","deathstarbench","partial",7],["deepflow","deathstarbench","partial",8],["deepflow","otel_demo","absent",6],["deepflow","otel_demo","absent",7],["deepflow","otel_demo","absent",8],["deepflow","otel_demo","full",6],["deepflow","otel_demo","full",7],["deepflow","otel_demo","full",8],["deepflow","otel_demo","partial",6],["deepflow","otel_demo","partial",7],["deepflow","otel_demo","partial",8],["deepflow","petclinic","absent",6],["deepflow","petclinic","absent",7],["deepflow","petclinic","absent",8],["deepflow","petclinic","full",6],["deepflow","petclinic","full",7],["deepflow","petclinic","full",8],["deepflow","petclinic","partial",6],["deepflow","petclinic","partial",7],["deepflow","petclinic","partial",8],["newrelic","deathstarbench","absent",6],["newrelic","deathstarbench","absent",7],["newrelic","deathstarbench","absent",8],["newrelic","deathstarbench","full",6],["newrelic","deathstarbench","full",7],["newrelic","deathstarbench","full",8],["newrelic","deathstarbench","partial",6],["newrelic","deathstarbench","partial",7],["newrelic","deathstarbench","partial",8],["newrelic","otel_demo","absent",6],["newrelic","otel_demo","absent",7],["newrelic","otel_demo","absent",8],["newrelic","otel_demo","full",6],["newrelic","otel_demo","full",7],["newrelic","otel_demo","full",8],["newrelic","otel_demo","partial",6],["newrelic","otel_demo","partial",7],["newrelic","otel_demo","partial",8],["newrelic","petclinic","absent",6],["newrelic","petclinic","absent",7],["newrelic","petclinic","absent",8],["newrelic","petclinic","full",6],["newrelic","petclinic","full",7],["newrelic","petclinic","full",8],["newrelic","petclinic","partial",6],["newrelic","petclinic","partial",7],["newrelic","petclinic","partial",8],["obi","deathstarbench","absent",6],["obi","deathstarbench","absent",7],["obi","deathstarbench","absent",8],["obi","deathstarbench","full",6],["obi","deathstarbench","full",7],["obi","deathstarbench","full",8],["obi","deathstarbench","partial",6],["obi","deathstarbench","partial",7],["obi","deathstarbench","partial",8],["obi","otel_demo","absent",6],["obi","otel_demo","absent",7],["obi","otel_demo","absent",8],["obi","otel_demo","full",6],["obi","otel_demo","full",7],["obi","otel_demo","full",8],["obi","otel_demo","partial",6],["obi","otel_demo","partial",7],["obi","otel_demo","partial",8],["obi","petclinic","full",6],["obi","petclinic","full",7],["obi","petclinic","full",8],["obi","petclinic","partial",8]] |
| smoke_attempts_excluded_from_main_coverage | true |
| technically_complete_main_cells | 5 |

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
| 40909264363 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | petclinic | absent | 6 | true | true | true | true | false | smoke_complete | 12914820744 | sha256:7c7a78513bbe155f6cfc5af05950b71ea1023c6efb35f1d0ef6e3d6a5c772557 | 12915105479 | sha256:d30990e0b0ecc061d18008096900da24bf37e72be4d5d3f0027795627fb7cf9c | unknown |
| 40909271694 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | otel_demo | absent | 6 | true | true | true | true | false | smoke_complete | 12916370886 | sha256:d58542e64adbc1684a9c15c38d2021f1d680e84ed792ea95fa403a6f5f3a9616 | 12916535612 | sha256:493edbdf59f8f6a9b6a715464791333f23986deeaee379f9843e0f44ce6d1143 | unknown |
| 40909271694 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | otel_demo | full | 6 | true | true | true | true | false | smoke_complete | 12915476064 | sha256:8e4d007c750f81229a7bfd859c0074e6ba9a8793da4ed359df8c7383f05cc117 | 12915685223 | sha256:40ccfa55a444162f51e55508765c177ecf7957444a26203a9467a1ec31dc6302 | unknown |
| 40909271694 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | otel_demo | partial | 6 | true | true | true | true | false | smoke_complete | 12915210909 | sha256:e321e8bfb351eb379871f62ecbb9cf28fd607de97b33283ce735073978a2a7bb | 12915161149 | sha256:77fe4a735c8ccfc1f04da7f05e0fd86953ecf6e7b232ff7c5e21616950d3a41d | unknown |
| 40909279346 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | absent | 6 | false | true | true | false | false | smoke_complete | 12913303429 | sha256:ca320c3e9f195983aa4c1c50419cbfa381edf881857415af1b9f88b967c1b6fd | 12913642774 | sha256:5ebb00ea990594ee00ea5c2070bd4cf4d1f3e8b8c651d8483702cd1f44d70bdb | source_evaluation_technically_incomplete |
| 40909288192 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | deathstarbench | full | 6 | true | true | true | true | false | smoke_complete | 12914535843 | sha256:68118d4adc080078e66ce781572dcb8247d059e0be450d986c953208cc821e45 | 12914341783 | sha256:680fd0f94b45690e7b16e191bbc45ce33509e83b628b0dd828fd12193d11cd0b | unknown |
| 40909294990 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | petclinic | partial | 6 | true | true | true | true | false | smoke_complete | 12914631223 | sha256:c5c661d83fa29296ab0ad46a509644302ebb7517989ebc136cee3f6a20963460 | 12915185493 | sha256:d8104ccee1a5920afc4219936cd1492bcb36e971988253075a3e043819fd77bd | unknown |
| 40909303154 | a-a-k/ebpf-model-discovery-experiments | obi | smoke | petclinic | full | 6 | true | true | true | true | false | smoke_complete | 12915031097 | sha256:a7b3ec3beb9d9477a306b43383f5b594238b62e07dab9c0abd9429439d76ddbc | 12913644553 | sha256:79d8f85db0521c0889be36fca1ec2124a67d5e0b710cf6b2be3e13f64374fbe9 | unknown |
| 40910013685 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | absent | 6 | true | true | true | true | false | acquisition_complete | 12920055481 | sha256:be9e31621a3b26dcb33a48bcf87f112323cc864ccf983e99467bfd3fc886d59a | 12919317201 | sha256:8ee088e3e53e86e06c72bec7691636b56e2174388292b8ff99fbb10949a488d4 | unknown |
| 40910013685 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | absent | 7 | true | true | true | true | false | acquisition_complete | 12917639119 | sha256:affffd6ff25c322c2e882d216c94e63a4a616dda1d1080c382326cf1f66baeb2 | 12918282707 | sha256:21becd9e616e533c94e54658e0cb533847d43d4de871d9855d53cb3a14157fd0 | unknown |
| 40910013685 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | absent | 8 | true | true | true | true | false | acquisition_complete | 12921655146 | sha256:e4ce8d1a477a0f499bb8c67414d43bccc4ac634ce4735e7403b9a17577d2d7fe | 12921031741 | sha256:db777e637423fb224b5ea7581e9e90feed74b1dc0eff44ede41d5949a6166001 | unknown |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 7 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 8 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40910393953 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | true | true | true | true | false | smoke_complete | 12915510227 | sha256:d9f63fd47a81e73d09153132f41002b764f189abc2c539dc334e31ea738e8746 | 12915445515 | sha256:988cb584fba3a29a1967a7fb18cf7ea57f55769eaec38e4aed636ead81dd676c | unknown |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 7 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 8 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | partial | 6 | true | true | true | true | false | acquisition_complete | 12921571169 | sha256:53b09b3e433809928a7ff378e154f74b8e1ca323954ade37d2431a5abfb46468 | 12920992250 | sha256:1e646840222979ebceea09e5a88ce0cc1493f79dde22a19e22d7970a8095ce6a | unknown |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | partial | 7 | true | true | true | true | false | acquisition_complete | 12921916343 | sha256:4363a9f4ae5e4eea9a469f98da740d9a56ef03fb0760693d4e7b702490f1c494 | 12921038049 | sha256:53c019c8ba5a1a4f2d01e5b832b2cdff5c303761f8001cca7eeaa345b52db635 | unknown |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | partial | 8 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | deathstarbench | absent | 6 | true | true | true | true | false | smoke_complete | 12916642863 | sha256:8c6688ef356f4c76e2630f2285551cd53ad629ed2696dde9db559d4816796223 | 12915784254 | sha256:b2d197995b0e6addcc67207fa5a98df804d6a6d66bc7ac0b2e38eacd45969f66 | unknown |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | deathstarbench | full | 6 | true | true | true | true | false | smoke_complete | 12916983473 | sha256:874b748e98de4257fae3ae4174f7b3fd0f09c1af8d6c26475f85aa6f75462ee5 | 12917472672 | sha256:7ae5939f65873e43cbbdde394379c08d1883072ee7a6db7286884915d9ed9fae | unknown |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | deathstarbench | partial | 6 | true | true | true | true | false | smoke_complete | 12915724898 | sha256:93b82327b7b37e6ea74dccd1208838d7dba91ca51fec5165bf6822e5dda076b2 | 12916313359 | sha256:e6f90ebf73db4603499bb018ac505b6e13c1d3bdbd83e544db32445ed3d9a290 | unknown |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | absent | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | absent | 7 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | absent | 8 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40920573691 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | true | true | true | true | false | smoke_complete | 12918178508 | sha256:e2a3c8daed6041095a042115d7d9ba1008d42ed5b2c48577a78dbaf77d2f313b | 12919590912 | sha256:b6646be1c74e76533a28631fe5c88a11f4942fa768e06becc8928752af77c9f9 | unknown |
| 40921056157 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | petclinic | partial | 6 | true | true | true | true | false | smoke_complete | 12920435257 | sha256:6cae68b5ba03081bcec4d9b156a351c4f077621704116c1e6439deede72829b6 | 12918928976 | sha256:0d5189b449d96d2d6f9a2274e08f8f8d82fab47138aa7e5d7342ac9bb4083cf7 | unknown |
| 40922905708 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | petclinic | full | 6 | false | true | true | false | false | technical_failure | 12919252994 | sha256:5b293661d41afaeb80b3e57acf8260f14f8633a7ae92334a670777cf895bd4b8 | 12920375252 | sha256:ec8d53ea0075db77a3bc152261c08f2bef55eafb54233273516cf8494aa6eb56 | source_evaluation_technically_incomplete |
| 40923928201 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | otel_demo | absent | 6 | true | true | true | true | false | smoke_complete | 12922255527 | sha256:f92609a08f32deedad5503712689dc4253b359f4344fcf25001faa0bb1f9480c | 12920908046 | sha256:0d84ff3606631f016cf39c09a69355b2c8893d968bb888a1f2c27150b901d405 | unknown |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | full | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | full | 7 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | full | 8 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |

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
| 40909264363 | coroot | petclinic | absent | 6 | true | true | [] | false |
| 40909271694 | obi | otel_demo | absent | 6 | true | true | [] | false |
| 40909271694 | obi | otel_demo | full | 6 | true | true | [] | false |
| 40909271694 | obi | otel_demo | partial | 6 | true | true | [] | false |
| 40909279346 | obi | deathstarbench | absent | 6 | false | false | ["native_observations_present_in_absent_mode"] | false |
| 40909288192 | obi | deathstarbench | full | 6 | true | true | [] | false |
| 40909294990 | obi | petclinic | partial | 6 | true | true | [] | false |
| 40909303154 | obi | petclinic | full | 6 | true | true | [] | false |
| 40910393953 | deepflow | petclinic | absent | 6 | true | true | [] | false |
| 40916651613 | coroot | deathstarbench | absent | 6 | true | true | [] | false |
| 40916651613 | coroot | deathstarbench | full | 6 | true | true | [] | false |
| 40916651613 | coroot | deathstarbench | partial | 6 | true | true | [] | false |
| 40920573691 | deepflow | petclinic | absent | 6 | true | true | [] | false |
| 40921056157 | coroot | petclinic | partial | 6 | true | true | [] | false |
| 40922905708 | coroot | petclinic | full | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40923928201 | coroot | otel_demo | absent | 6 | true | true | [] | false |

## Saved main forecasts and external outcomes

| Run | Collector | System | Mode | Seed | Complete | Operation | Source | Variant | Available | Stored forecast | Stored interval | Actual true | Actual false | Actual unknown | Stored reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40910013685 | obi | petclinic | absent | 6 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 6 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 6 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 7 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 7 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40910013685 | obi | petclinic | absent | 8 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40910013685 | obi | petclinic | absent | 8 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 6 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 6 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2099 | 301 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2099 | 301 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 7 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 7 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |

## Saved campaign and Actions costs

| Ledger field | Stored value |
|---|---|
| known_completed_job_elapsed_seconds | 80264.0 |
| runs_with_unknown_job_elapsed | 0 |
| known_stored_artifact_bytes | 12748617272 |
| runs_with_unknown_artifact_bytes | 0 |
| report_artifact_transfer | {"compact_zip_downloads":39,"compact_zip_received_bytes":192384306,"full_zip_recovery_downloads":15,"full_zip_recovery_received_bytes":402194831,"scope":"actual retained HTTP response bytes in this report job, including failed or rejected downloads; unavailable response bytes remain unknown","total_received_bytes":594579137} |
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
| 40909264363 | coroot | smoke | petclinic | absent | 6 | 918.123199023 | 28.939479333999998 | 1.818156727 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40909271694 | obi | smoke | otel_demo | absent | 6 | 2307.778294418 | 30.696048976 | 520.658441263 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40909271694 | obi | smoke | otel_demo | full | 6 | 1432.32674234 | 30.018888122 | 330.732792342 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40909271694 | obi | smoke | otel_demo | partial | 6 | 1052.51150642 | 23.089833611 | 3.760823204 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40909279346 | obi | smoke | deathstarbench | absent | 6 | 577.731774457 | 27.634227167 | 0.804193617 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40909288192 | obi | smoke | deathstarbench | full | 6 | 781.051700455 | 23.305410855999998 | 181.841547449 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40909294990 | obi | smoke | petclinic | partial | 6 | 1008.804622386 | 20.702372406000002 | 216.277176321 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40909303154 | obi | smoke | petclinic | full | 6 | 1146.732074135 | 21.086086787 | 346.618061413 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40910013685 | obi | main | petclinic | absent | 6 | 4633.313614103 | 29.585512608000002 | 1018.666064187 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40910013685 | obi | main | petclinic | absent | 7 | 4304.3992328 | 29.685263464000002 | 928.998759852 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40910013685 | obi | main | petclinic | absent | 8 | 5969.804443751 | 37.149438216 | 1659.557493961 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40910021896 | obi | main | deathstarbench | partial | 6 | unknown | unknown | unknown | unknown | unknown |
| 40910021896 | obi | main | deathstarbench | partial | 7 | unknown | unknown | unknown | unknown | unknown |
| 40910021896 | obi | main | deathstarbench | partial | 8 | unknown | unknown | unknown | unknown | unknown |
| 40910393953 | deepflow | smoke | petclinic | absent | 6 | 927.363674934 | 29.024362617999998 | 2.584100688 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40913407822 | obi | main | deathstarbench | full | 6 | unknown | unknown | unknown | unknown | unknown |
| 40913407822 | obi | main | deathstarbench | full | 7 | unknown | unknown | unknown | unknown | unknown |
| 40913407822 | obi | main | deathstarbench | full | 8 | unknown | unknown | unknown | unknown | unknown |
| 40914709370 | obi | main | petclinic | partial | 6 | 4761.395654934 | 21.071642731 | 1075.135105025 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40914709370 | obi | main | petclinic | partial | 7 | 5162.707520434 | 23.89708982 | 1295.483410873 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40914709370 | obi | main | petclinic | partial | 8 | unknown | unknown | unknown | unknown | unknown |
| 40916651613 | coroot | smoke | deathstarbench | absent | 6 | 606.534134109 | 32.739758749 | 1.213493638 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40916651613 | coroot | smoke | deathstarbench | full | 6 | 894.366598367 | 20.365483743 | 286.587126566 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40916651613 | coroot | smoke | deathstarbench | partial | 6 | 682.368089674 | 29.818497398999998 | 61.54235955 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40919005648 | obi | main | deathstarbench | absent | 6 | unknown | unknown | unknown | unknown | unknown |
| 40919005648 | obi | main | deathstarbench | absent | 7 | unknown | unknown | unknown | unknown | unknown |
| 40919005648 | obi | main | deathstarbench | absent | 8 | unknown | unknown | unknown | unknown | unknown |
| 40920573691 | deepflow | smoke | petclinic | absent | 6 | 823.188866372 | 22.487764059 | 2.153130541 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40921056157 | coroot | smoke | petclinic | partial | 6 | 976.578852803 | 31.258023745000003 | 2.462806336 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40922905708 | coroot | smoke | petclinic | full | 6 | 262.806180228 | 18.799312921000002 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40923928201 | coroot | smoke | otel_demo | absent | 6 | 1787.577560942 | 29.052966591 | 2.033806565 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40924968145 | obi | main | petclinic | full | 6 | unknown | unknown | unknown | unknown | unknown |
| 40924968145 | obi | main | petclinic | full | 7 | unknown | unknown | unknown | unknown | unknown |
| 40924968145 | obi | main | petclinic | full | 8 | unknown | unknown | unknown | unknown | unknown |

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
| 40909264363 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572464552 | prepare | completed | success | 3.0 | 3 |
| 40909264363 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572527270 | campaign (petclinic, absent, 6) | completed | success | 1062.0 | 3 |
| 40909271694 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572478870 | prepare | completed | success | 4.0 | 9 |
| 40909271694 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572542685 | campaign (otel_demo, full, 6) | completed | success | 1585.0 | 9 |
| 40909271694 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572542815 | campaign (otel_demo, absent, 6) | completed | success | 2448.0 | 9 |
| 40909271694 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572542996 | campaign (otel_demo, partial, 6) | completed | success | 1191.0 | 9 |
| 40909279346 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123572504162 | prepare | completed | success | 3.0 | 4 |
| 40909279346 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123572563107 | campaign (deathstarbench, absent, 6) | completed | failure | 709.0 | 4 |
| 40909288192 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572533954 | prepare | completed | success | 3.0 | 4 |
| 40909288192 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572592259 | campaign (deathstarbench, full, 6) | completed | success | 920.0 | 4 |
| 40909294990 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572556734 | prepare | completed | success | 3.0 | 3 |
| 40909294990 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572606867 | campaign (petclinic, partial, 6) | completed | success | 1115.0 | 3 |
| 40909303154 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572585499 | prepare | completed | success | 3.0 | 3 |
| 40909303154 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123572639451 | campaign (petclinic, full, 6) | completed | success | 1258.0 | 3 |
| 40910013685 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123575126495 | prepare | completed | success | 2.0 | 9 |
| 40910013685 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123575172279 | campaign (petclinic, absent, 8) | completed | success | 6320.0 | 9 |
| 40910013685 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123575172315 | campaign (petclinic, absent, 7) | completed | success | 4582.0 | 9 |
| 40910013685 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123575172535 | campaign (petclinic, absent, 6) | completed | success | 4899.0 | 9 |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123575154880 | prepare | completed | success | 3.0 | 0 |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123575210321 | campaign (deathstarbench, partial, 8) | in_progress | unknown | unknown | 0 |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123575210440 | campaign (deathstarbench, partial, 7) | completed | failure | 6972.0 | 0 |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123575210516 | campaign (deathstarbench, partial, 6) | completed | failure | 7127.0 | 0 |
| 40910393953 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123576483454 | prepare | completed | success | 4.0 | 3 |
| 40910393953 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123576553435 | campaign (petclinic, absent, 6) | completed | success | 1060.0 | 3 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123587138277 | prepare | completed | success | 3.0 | 0 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123587179829 | campaign (deathstarbench, full, 8) | in_progress | unknown | unknown | 0 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123587179847 | campaign (deathstarbench, full, 6) | completed | failure | 4336.0 | 0 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123587179972 | campaign (deathstarbench, full, 7) | in_progress | unknown | unknown | 0 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123591742382 | prepare | completed | success | 3.0 | 7 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123591790633 | campaign (petclinic, partial, 6) | completed | success | 5014.0 | 7 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123591790713 | campaign (petclinic, partial, 8) | in_progress | unknown | unknown | 7 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123591790794 | campaign (petclinic, partial, 7) | completed | success | 5443.0 | 7 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598557302 | prepare | completed | success | 3.0 | 12 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598607263 | campaign (deathstarbench, absent, 6) | completed | success | 743.0 | 12 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598607345 | campaign (deathstarbench, partial, 6) | completed | success | 810.0 | 12 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598607439 | campaign (deathstarbench, full, 6) | completed | success | 1010.0 | 12 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123606849340 | prepare | completed | success | 3.0 | 0 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123606897153 | campaign (deathstarbench, absent, 6) | in_progress | unknown | unknown | 0 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123606897296 | campaign (deathstarbench, absent, 7) | in_progress | unknown | unknown | 0 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123606897356 | campaign (deathstarbench, absent, 8) | in_progress | unknown | unknown | 0 |
| 40920573691 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123612367739 | prepare | completed | success | 2.0 | 3 |
| 40920573691 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123612417198 | campaign (petclinic, absent, 6) | completed | success | 946.0 | 3 |
| 40921056157 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123614070873 | prepare | completed | success | 2.0 | 3 |
| 40921056157 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123614121293 | campaign (petclinic, partial, 6) | completed | success | 1115.0 | 3 |
| 40922905708 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123620638597 | prepare | completed | success | 4.0 | 2 |
| 40922905708 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123620691943 | campaign (petclinic, full, 6) | completed | failure | 369.0 | 2 |
| 40923928201 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123624273475 | prepare | completed | success | 3.0 | 3 |
| 40923928201 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123624318547 | campaign (otel_demo, absent, 6) | completed | success | 1924.0 | 3 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123627925518 | prepare | completed | success | 3.0 | 0 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123627981286 | campaign (petclinic, full, 7) | in_progress | unknown | unknown | 0 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123627981288 | campaign (petclinic, full, 6) | in_progress | unknown | unknown | 0 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123627981435 | campaign (petclinic, full, 8) | in_progress | unknown | unknown | 0 |
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
| 40905967491 | a-a-k/ebpf-model-discovery-experiments | report | completed | success | 123560684221 | report | completed | success | 146.0 | 1 |
| 40908572301 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123569971211 | checks | completed | success | 38.0 | 0 |
| 40908572301 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123569971729 | control-fixture-v5 | completed | success | 21.0 | 0 |
| 40909257494 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123572426942 | qualify | completed | failure | 49.0 | 1 |
| 40910461222 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123576718086 | checks | completed | success | 33.0 | 0 |
| 40910461222 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123576719073 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 40910330302 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123576255676 | toolchain | completed | success | 30.0 | 1 |
| 40910404800 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123576521322 | toolchain | completed | success | 209.0 | 1 |
| 40911232159 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123579444498 | toolchain | completed | success | 33.0 | 1 |
| 40911388849 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123579984050 | toolchain | completed | success | 358.0 | 1 |
| 40913108121 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123586074073 | toolchain | completed | success | 551.0 | 1 |
| 40912701537 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123584627460 | control-fixture-v5 | completed | success | 21.0 | 0 |
| 40912701537 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123584627992 | checks | completed | success | 45.0 | 0 |
| 40913421361 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123587180237 | control-fixture-v5 | completed | success | 23.0 | 0 |
| 40913421361 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123587180847 | checks | completed | success | 45.0 | 0 |
| 40913965976 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | failure | 123589127982 | adjudicate | completed | failure | 20.0 | 1 |
| 40914666129 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | success | 123591591098 | adjudicate | completed | success | 25.0 | 1 |
| 40914286531 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123590257487 | checks | completed | success | 47.0 | 0 |
| 40914286531 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123590258154 | control-fixture-v5 | completed | success | 22.0 | 0 |
| 40917708803 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123602270364 | toolchain | completed | success | 316.0 | 1 |
| 40917723956 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123602321327 | toolchain | completed | success | 31.0 | 1 |
| 40917740919 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123602381703 | toolchain | completed | success | 94.0 | 1 |
| 40919785943 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123609568351 | checks | completed | success | 48.0 | 0 |
| 40919785943 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123609568972 | control-fixture-v5 | completed | success | 19.0 | 0 |
| 40920240694 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | success | 123611189759 | adjudicate | completed | success | 23.0 | 1 |
| 40922561004 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123619419595 | control-fixture-v5 | completed | success | 27.0 | 0 |
| 40922561004 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123619420056 | checks | completed | success | 36.0 | 0 |
| 40927651775 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123637344754 | toolchain | completed | success | 29.0 | 1 |
| 40928823255 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123641490677 | control-fixture-v5 | completed | success | 18.0 | 0 |
| 40928823255 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123641491044 | checks | completed | success | 47.0 | 0 |
| 40929241254 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | failure | 123642943912 | validate | completed | failure | 19.0 | 1 |
| 40929189766 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123642757152 | checks | completed | success | 45.0 | 0 |
| 40929189766 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123642757745 | control-fixture-v5 | completed | success | 19.0 | 0 |
| 40929628640 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123644299053 | checks | completed | success | 38.0 | 0 |
| 40929628640 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123644299508 | control-fixture-v5 | completed | success | 27.0 | 0 |
| 40930045089 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123645747590 | checks | completed | success | 46.0 | 0 |
| 40930045089 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123645748133 | control-fixture-v5 | completed | success | 22.0 | 0 |

Human/agent preparation effort: unknown

Current report-job unfinished tail: unknown

The lossless aggregate retains every source evaluation object, including detailed DB, baseline, class, async, causal and cost fields not expanded into new summaries here.
