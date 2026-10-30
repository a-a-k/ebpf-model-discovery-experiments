# Iteration-5 saved-artifact report

This report copies source-produced evaluations and technical records. It performs no refit, relinking, rescoring, thresholding, or accuracy-based selection.
Technical smoke status is separate from the 81-cell main grid and is not an independent admission or positive contribution claim.

## Fixed grid and execution boundary

| Stored field | Value |
|---|---|
| blocked_main_cells | [] |
| declared_main_cells | 81 |
| incomplete_or_missing_main_cells | [["deepflow","deathstarbench","absent",6],["deepflow","deathstarbench","absent",7],["deepflow","deathstarbench","absent",8],["deepflow","deathstarbench","full",6],["deepflow","deathstarbench","full",7],["deepflow","deathstarbench","full",8],["deepflow","deathstarbench","partial",6],["deepflow","deathstarbench","partial",7],["deepflow","deathstarbench","partial",8],["deepflow","otel_demo","absent",6],["deepflow","otel_demo","absent",7],["deepflow","otel_demo","absent",8],["deepflow","otel_demo","full",6],["deepflow","otel_demo","full",7],["deepflow","otel_demo","full",8],["deepflow","otel_demo","partial",6],["deepflow","otel_demo","partial",7],["deepflow","otel_demo","partial",8],["deepflow","petclinic","absent",6],["deepflow","petclinic","absent",7],["deepflow","petclinic","absent",8],["deepflow","petclinic","full",6],["deepflow","petclinic","full",7],["deepflow","petclinic","full",8],["deepflow","petclinic","partial",6],["deepflow","petclinic","partial",7],["deepflow","petclinic","partial",8]] |
| smoke_attempts_excluded_from_main_coverage | true |
| technically_complete_main_cells | 54 |

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
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | partial | 8 | true | true | true | true | false | acquisition_complete | 12923161927 | sha256:a23db8336c5ff5fb475f2660630dcfc63269e3d892c7fe6908907217a3e2e246 | 12922514282 | sha256:e201f9209c0406a23bc42bf790b854db37c12e226fdaa737528b5ffeea7181d8 | unknown |
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
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | full | 6 | true | true | true | true | false | acquisition_complete | 12927192823 | sha256:2691614979b7d3be7e86866b76d7fbbf668aa5e0f225ed5c9887ee2dc5cc7a09 | 12927257991 | sha256:d3b0c9f3f598af8f4e0eb3a4e057aabc484ab4825faa5d460ed62159ee8785c6 | unknown |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | full | 7 | true | true | true | true | false | acquisition_complete | 12928586162 | sha256:c3ed13afd1040641d977e25fa3bc8ddcf4b934a448c1c12e4636d1adaf0f8ade | 12928232708 | sha256:20d44f28cd289695b626dd50328599f18d7d2a06b6988756b6c80858bbcca6ad | unknown |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | obi | main | petclinic | full | 8 | true | true | true | true | false | acquisition_complete | 12926899227 | sha256:0b0ba3545eb71a129325b1f8ca9a63baef04607eff91384d6c59f8cd4c022e05 | 12927543563 | sha256:8d743cb8bb37a1b2e3cdd0fa9f633df414801154f3cb37bfec15df99ebe2e908 | unknown |
| 40930786566 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | true | true | true | true | false | smoke_complete | 12923482530 | sha256:8de74b3c52c8ebfeb9167b409e81a3dfee42c6a4f210261f2d11f7436a190d34 | 12923916576 | sha256:231559700200e24ec7a02387f971ddcf9d2642c85daf2e5fb6a9a8ebd402495f | unknown |
| 40930793452 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | petclinic | full | 6 | false | true | true | false | false | technical_failure | 12922117940 | sha256:22adcf62ba1fc3a5af799fc77f614359e2b67d979358520cac7c92b0e49b363a | 12923555440 | sha256:d8fc8e3746389789715855976983dbc70d39cd5a457e5a0f2f162c8ebd0b74ce | source_evaluation_technically_incomplete |
| 40930805848 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | absent | 6 | true | true | true | true | false | acquisition_complete | 12936501478 | sha256:80b90f0509671b34d9488ee348b942154a086d85917fd27067ca2f5da219d202 | 12936118371 | sha256:6ac43b3023a80018cfaa53c45d80d0e56e7b19c5e9774944a383d9f172a1c205 | unknown |
| 40930805848 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | absent | 7 | false | true | true | false | false | technical_failure | 12932964556 | sha256:7d461751a107b1a4d10aa39b8d131fa4228ead6fc9e70573b70daeaf89a7b7fb | 12934116302 | sha256:5c9328c71ef567d79a04dca219985a597f9bf2ce19f66992b295c64f405b1c3e | source_evaluation_technically_incomplete |
| 40930805848 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | absent | 8 | false | true | true | false | false | technical_failure | 12933112600 | sha256:8377ddce7f3bf1840f0d7ad8240fb7766db1e1e236d7937c2772c214dfadb0be | 12933941373 | sha256:6711e0d70a35354d77e7ec31a07e09ba85b68ce4fbdee411394fbdbdfc1c7290 | source_evaluation_technically_incomplete |
| 40932031732 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 6 | false | true | true | false | false | running | 12928354094 | sha256:8b192a70aaddecd6d46eb0e740b8680f2b4a53e006c73c0ac18f5558b60de2ca | 12929887000 | sha256:056f544aa3a74c5ca72cd22aa3c8f2d93597df62f87df3a76dc764226e36d4e5 | source_evaluation_technically_incomplete |
| 40933885726 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | petclinic | full | 6 | true | true | true | true | false | smoke_complete | 12925016869 | sha256:1361884874e28929cf957db78c3c9c16951588d66c7ede95ed2c0964c26705d0 | 12925795283 | sha256:dbdc8f455fa07b0235880e9cf8897e8dc5a95bc007f7ad3b8937b198a7fa97e4 | unknown |
| 40933892507 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | otel_demo | partial | 6 | true | true | true | true | false | smoke_complete | 12925187023 | sha256:a0f3787ba5086e3f8ee2024daaffcd0fac09d8cfafae3f607ebb818b689657ae | 12925925150 | sha256:6251cf7b436073f2b201dc38b33577cf1495a577403aef9e4d8c348cbc584b23 | unknown |
| 40935194776 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 6 | false | true | true | false | false | running | 12929342198 | sha256:4fe61c2356039b5e6a241bd0572e48b9744ab102f4f2828e00f38e15143918e4 | 12929856544 | sha256:d14c24b621b694aaae4a73d12d00b64260c63ac6e34e66e805c3c5ab34684fa1 | source_evaluation_technically_incomplete |
| 40935203055 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 7 | false | true | true | false | false | running | 12929237964 | sha256:2ad88cf5c4d366951509cb6dce2c8a3004445e5f1d152b34f43b6e05a614ee3c | 12929048798 | sha256:965bd224c81144ec6fc12948109c51b7f211e2798f712466e3dfc3f4bbe5d9e0 | source_evaluation_technically_incomplete |
| 40936796228 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | deathstarbench | absent | 6 | true | true | true | true | false | smoke_complete | 12924404866 | sha256:042bd1267687889f4509949a7c5f15f7ac85576e5e71b9b0dfa727c6572130a0 | 12926540663 | sha256:c3f9cb2971cc4116caaeaacfbcb9c5f3b85ca220878f86aaf0409a19af02ec91 | unknown |
| 40942429097 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | absent | 6 | true | true | true | true | false | acquisition_complete | 12937171763 | sha256:b57e0bcabb18c44800ee32ce9a23e736e9ee7f3b394b916669bb1031caed94d4 | 12938100241 | sha256:07f0c3eaa2d2dd4b593a6d5db9bd4b5f10e698317b1a974fbdc6959a30aa0a33 | unknown |
| 40942429097 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | absent | 7 | true | true | true | true | false | acquisition_complete | 12933554459 | sha256:d6003f14d541e8cc23948451142f9724c70f706318b761edbf1ff880b8fd768e | 12933019490 | sha256:5a8655821fcb86ffb27bc1811d5994e9425898a339d8801ca771a54ce184585e | unknown |
| 40942429097 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | absent | 8 | true | true | true | true | false | acquisition_complete | 12939304953 | sha256:dbf2ad71131820cf1f500908b1cee9d7ce802f8d7b0fbc6b03343ddbf54e7b3e | 12941115116 | sha256:f51eb4ead0e36ba1f6c3a6e1b1e623b24eb90f528255265c366ee21c6ac15e1e | unknown |
| 40942437542 | a-a-k/ebpf-model-discovery-experiments | coroot | smoke | otel_demo | full | 6 | true | true | true | true | false | smoke_complete | 12928941627 | sha256:4a408ee48cc52ac47134278b5246e510a7a2eaec033b1bf5efbbd84583685a19 | 12929960010 | sha256:2fba8333bdc0b94c7e394d2971ecec31d5b9f17533c2c48482ac5afb9da5d603 | unknown |
| 40942447288 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | otel_demo | absent | 6 | false | true | true | false | false | technical_failure | 12929535044 | sha256:00c3d7d9faada13408bb917ea05d7ad7392a0d42ee3ec30387a136ef25112746 | 12927583844 | sha256:6b8908edb75c0c6efd6192e1bcf8c381c979b8abc958ed687739919317975404 | source_evaluation_technically_incomplete |
| 40942447288 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | otel_demo | full | 6 | true | true | true | true | false | smoke_complete | 12928827818 | sha256:7f90b1ce5ef8d1841c103bcff82bdca85adf58148431d830c68da3c4f168a132 | 12927989528 | sha256:d6be276af94d4d41888d82f40016f156a00145e8933e9a815c6bac0658c6703a | unknown |
| 40942447288 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | otel_demo | partial | 6 | true | true | true | true | false | smoke_complete | 12929555891 | sha256:0c15d6d0490d54d3130932b1d264cb5b0f8218346a0a9b39b5037b428c00e866 | 12929530816 | sha256:5328c16f3e27b3d117794b20136626b46b0a12157ac2bd85142a3b8dd1b519f6 | unknown |
| 40943318871 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | deathstarbench | partial | 6 | true | true | true | true | false | smoke_complete | 12927818968 | sha256:a954a94f650c0f26632579784fca616cd5757ea0870f8e76415aed4ca3257dae | 12927709077 | sha256:843aa5862ada493c92d13a85a9a8f163927e5dfaf9211f55441de6d48dd55280 | unknown |
| 40943915967 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | partial | 6 | true | true | true | true | false | smoke_complete | 12930405622 | sha256:c8d024f81c2cf0dde118bb06b52e4007be45c71f79d11daa57197aecfeaef3cb | 12929856579 | sha256:06ebef0c1586eceb542e885091d36e528e5e9330052a56451c8dc4c5313f1a39 | unknown |
| 40943924937 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | full | 6 | true | true | true | true | false | smoke_complete | 12928948114 | sha256:01b7b7528c9b1209a03c1a653fbbc031a6df0c1e0a69fa4b5a770b47308e4f7b | 12929672202 | sha256:f4d955e382822cee180c1c57c85e3a7f1b487a6e4fc0dd4e9802c7ab7c583bee | unknown |
| 40944249737 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | deathstarbench | full | 6 | true | true | true | true | false | smoke_complete | 12928474218 | sha256:6090f60a738667c7c60a28e0943b631cd568544daa95d8f13397025b3d38a135 | 12928903033 | sha256:cb7e3d3a1b5fb41d4d699780bcd53b8f33559b57beeb7aac13e5c6cbd3a8e40f | unknown |
| 40945578755 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 7 | true | true | true | true | false | acquisition_complete | 12941676590 | sha256:8118b6628f07709fe6bbeb77385af709a8ae02a015919317a7c42451cec081d4 | 12942290746 | sha256:0228b6db20b8c86a91e14a72329f7da6e856d3a46e296a6703c0574532e2591b | unknown |
| 40947264867 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 6 | false | true | true | false | false | technical_failure | 12941975097 | sha256:c872c53055a0c2fa8168fd1ff2e0580e5db4c3245d057ce46027c7c197a70b97 | 12941426430 | sha256:c39b31280dd49172bb4ddb79f10747e6cfb88938b951a2ce44a06b10ff2a1574 | source_evaluation_technically_incomplete |
| 40947274375 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 6 | true | true | true | true | false | acquisition_complete | 12943498463 | sha256:6bb88172ed7a6f734e1aa67d0d1e0b3c27c0bfcce945228c24619f1d6ff2f371 | 12944423886 | sha256:1bb06dde2b934f7c1d01905f2a8889fffd6178f842e93e5df43e22d5b1046de3 | unknown |
| 40947287495 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 7 | true | true | true | true | false | acquisition_complete | 12944715103 | sha256:501ffe5a5e6d8e1737c0a4d70d5d94b125090da8176874920f161cf60f064bf5 | 12944102644 | sha256:b121d20f94a0bdc6ae03886b94158fba03c39238b6ec97c4c9022ea1bef1e197 | unknown |
| 40947299209 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | absent | 6 | true | true | true | true | false | acquisition_complete | 12933131686 | sha256:dd724f044682e8fc437466a379da331aa33a1af01df65e7ac9e7e3332c6beb22 | 12933990526 | sha256:342c1ee07dd4cb50f1129ca2b83b3f30c1ea1f34f2b332149e9ab87fcee80bb8 | unknown |
| 40947299209 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | absent | 7 | true | true | true | true | false | acquisition_complete | 12934120822 | sha256:4bbe6a1b5b2e9864e0d4ed8614f741babe4b3c2e4cc9ed33ce0bd64e11854a9b | 12933866622 | sha256:c63112065e93f41a01cff6c253aea1135fa47d24d003ef0a3f980cb4dcbf20a3 | unknown |
| 40947299209 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | absent | 8 | true | true | true | true | false | acquisition_complete | 12932104383 | sha256:0bbdac30d294653f19ec60243b432d2f02423a2eae77fade4dea68daf29967c3 | 12933064046 | sha256:8b08824c7826ca20fdd0ae0231043c272f844f9827bc4281013d7bd115817a07 | unknown |
| 40948057864 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | otel_demo | absent | 6 | true | true | true | true | false | smoke_complete | 12931813811 | sha256:c4df6e2772556998a22b58f6d5b506ee400c3cbdb1b80d48e128c3df6571dfcb | 12932630483 | sha256:317a207e11a66719f177568a37d93133bdc1c728ef8a647d97c71df52691e77b | unknown |
| 40948072741 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | partial | 6 | false | true | true | false | false | technical_failure | 12939228701 | sha256:eadb1da2f740ac151fd1aab8200ff5b4f6dc217c3783432addc2432326a2e8d3 | 12939767196 | sha256:fe04b44e0b202aba4ef752680d0f2666c6cc7bfa125f2df2afc956fdf1eb5c03 | source_evaluation_technically_incomplete |
| 40948072741 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | partial | 7 | true | true | true | true | false | acquisition_complete | 12941448669 | sha256:618ec325f7efdb29bdca5002176de5e54877316546701cb155c6c247d65b86cd | 12942715192 | sha256:0bd5e07747ff3aee63a9406c2bd8e2efb5390a76ee4946f3eac207183f69c2d1 | unknown |
| 40948072741 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | partial | 8 | false | true | true | false | false | technical_failure | 12939626858 | sha256:425d17a3a4095cc13c6ca521f2332b99b564a97647120b82c3b1041b2c87906d | 12940365274 | sha256:2e608fc92d64a1416bb55cd2cb43117cb6f1e4b26dceb143c2ca9ad8dce35ead | source_evaluation_technically_incomplete |
| 40953661709 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 8 | true | true | true | true | false | acquisition_complete | 12947519268 | sha256:b8962b47b6ebc15ff71cf0ea2eecc50c87debb482a63c6dd6e5484f9e3f69ac5 | 12948537129 | sha256:94fcf3b5968de3dac7ad72b30d3954646684c6a4d0c841600e4f1719b120d0b2 | unknown |
| 40956228868 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | partial | 6 | true | true | true | true | false | acquisition_complete | 12937232960 | sha256:0e107efd44a2308e3e164f0fd022a3e3814e274463c6b4eb10c895b7c08f539c | 12936778728 | sha256:9cd2ba5e59762eae6a745a372c288d78730c7777054d88c7a3b81c963f0a6d5b | unknown |
| 40956228868 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | partial | 7 | true | true | true | true | false | acquisition_complete | 12938360814 | sha256:08dd77cdf0640ad971d1d296a4cf8ffd359843f676ce680a8acc811296e547b8 | 12936689151 | sha256:78681678012baddd0aa0bfe7723dab0add784ae3dfd138db591b184f3072bc72 | unknown |
| 40956228868 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | partial | 8 | true | true | true | true | false | acquisition_complete | 12938705608 | sha256:3ad4d1c2dee72b51476ce2f48a7a508d32a7e057a28b68654a58dde666c2c75b | 12938112835 | sha256:7566b9b1d4203f1dcf1aa737e05dfd73b2a41782fafc7b40a21fe6f36bcaef77 | unknown |
| 40956239225 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | partial | 8 | true | true | true | true | false | acquisition_complete | 12945349527 | sha256:6861f714b77d64534607631ebb200e9892a0ecc6ab85c113c076c75fed15703c | 12946951180 | sha256:c17757515fba3b3cfdcc660a78875058b505f2d3c6d59bae3d23e6a0bb04ae1f | unknown |
| 40958365058 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | absent | 7 | true | true | true | true | false | acquisition_complete | 12945932973 | sha256:a5e886a1cb17141b4e9d4b95476f0e8b71a6232ec042244728163de1ef0d9dbd | 12946855866 | sha256:33e3f6d7047a477fdb105683a70a8134975c008751761f4caa8acd65dd829dbf | unknown |
| 40959052743 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | absent | 8 | true | true | true | true | false | acquisition_complete | 12945067476 | sha256:3860e59da72b65f2cc2350404f75f4b7a1a5f4069af156a4404b5ac1b149ac89 | 12946150034 | sha256:1cc0c3749c254a1deb1feaba9fa599640a69be7ab7e5f41ef22e7a34fa393371 | unknown |
| 40963548420 | a-a-k/ebpf-model-discovery-experiments | deepflow | main | petclinic | absent | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40965631880 | a-a-k/ebpf-model-discovery-experiments | deepflow | main | petclinic | absent | 7 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 40966250927 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | full | 6 | true | true | true | true | false | acquisition_complete | 12950085255 | sha256:78dd27ec5a376bf9c444c60ad3d3c9ed71bfc83186af1204de38fd8a47bbe2ca | 12949009780 | sha256:dbbb1437a9a78d806b499e9317043248953a7e5e6da68233e1127a65241510c8 | unknown |
| 40966258333 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | full | 7 | true | true | true | true | false | acquisition_complete | 12948423515 | sha256:f03ad01c3d27a541c33c7154a64a80f645cf34553dcac1ab614699c0d175821a | 12949317141 | sha256:fc032bbaa6202510321fce24893af76b2be06dba530d5a091cb813c55817df47 | unknown |
| 40966847000 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | full | 8 | true | true | true | true | false | acquisition_complete | 12949014963 | sha256:25fbae841b53c614cfa2bc65020f5cc0aedbd2f4072879e23759d1ab3154acf4 | 12949901009 | sha256:536fd85c23c19379b501cd66fd2f6f82d3132b30dcc9818bc5995635301a09eb | unknown |
| 40970095079 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | absent | 6 | true | true | true | true | false | acquisition_complete | 12948320780 | sha256:6ad5a1c121d2790aa0299e717316dbe1ec89f210cccf76bc1a878790805c3de2 | 12948436255 | sha256:b7b95c0a0dbf93d4c94aa6d9c6e177e279a35ccf8ad32d7ce9134ae6c982097a | unknown |
| 40970638144 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | partial | 8 | true | true | true | true | false | acquisition_complete | 12949771867 | sha256:a0850bb5a0fb839e2ff3e3396f1318d117bcf6d026894cd9accf8dec4e67ebfd | 12950191024 | sha256:a1a106dcf060e2fec22a2927298210fb4386d0f69994e92155e7a64b4ce8e69e | unknown |
| 40971766251 | a-a-k/ebpf-model-discovery-experiments | obi | main | otel_demo | partial | 6 | true | true | true | true | false | acquisition_complete | 12950256617 | sha256:6f486c61c9f6a3870d092a986ed26aafd7bf9c2424d8ee19061e357b2e6563c6 | 12950018152 | sha256:c85a186a8b25b864f76fdaf2a1e6d0de4ab82498fa9a855448d67f56505f07fa | unknown |
| 41004270443 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | absent | 7 | true | true | true | true | false | acquisition_complete | 12961242802 | sha256:b6f59b223b48e64703273f5ff9d37e5677088848995863baf25ae7c94d90c5a1 | 12961956414 | sha256:0e3e68b3fd37a2faa45cfcda450f70b8500d62d7895c929be433f671f5616cbf | unknown |
| 41004275773 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | absent | 8 | true | true | true | true | false | acquisition_complete | 12960462523 | sha256:17ae66166bc21c4aaaec973d0a377df3cf789dff353708e3a25f2724ea7157a2 | 12961305236 | sha256:aae53b249f0e50bbd553ba5a99e6ff36db09853e79842b1372fe032553bf0e5b | unknown |
| 41004281518 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | partial | 6 | true | true | true | true | false | acquisition_complete | 12963532500 | sha256:f1219c33c5a01ef639bcd1189211aaa8873530d018557ee2467e3fecd4ef51e1 | 12964237295 | sha256:770e6ff172a3888a9154163548bbf38891aadf1f3f03d368e60a8975dbc74301 | unknown |
| 41004281518 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | partial | 7 | true | true | true | true | false | acquisition_complete | 12964072241 | sha256:f300e379fd673bbcd1ec7f01be23af9b5314a446b015ea14e3bfd68711927da4 | 12963664277 | sha256:b0e32875ff4cd46dbec66e7cfc2725eb33da069b67af2c5e4915fa28ca649ba0 | unknown |
| 41004281518 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | partial | 8 | true | true | true | true | false | acquisition_complete | 12963759737 | sha256:69b0038cc7b0f084c9a8c18642a43b0f84ead2e06a48c56861930815166a2f6b | 12964607038 | sha256:cbdad9e968b55255249550006079a56664432cae581a918836f7f2213d7fc85c | unknown |
| 41004285932 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | full | 6 | true | true | true | true | false | acquisition_complete | 12965338107 | sha256:3b0cdf0c9e843b27a7aa2bc3e4a022d1c57c4daac57596a51f7fd37e0aecaf41 | 12965293560 | sha256:a1a89962119dc91d3d92ba0c846b488165c50a9813bbb3220e616ed2d7830aed | unknown |
| 41004285932 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | full | 7 | true | true | true | true | false | acquisition_complete | 12965078253 | sha256:75932d75d0c9c250f54d7f7b5615490db3e3ed77d69a24cab35d4c743fcf3f87 | 12965054250 | sha256:1a12a62c128368d380683e27d57bf487a6c1fda51a65ca84c9267de7e1f2afd8 | unknown |
| 41004285932 | a-a-k/ebpf-model-discovery-experiments | coroot | main | deathstarbench | full | 8 | true | true | true | true | false | acquisition_complete | 12962981417 | sha256:eb59cb960f1d42580ca4558d19bbb1ec9af36044e9c8720076b36e67f2632980 | 12962834328 | sha256:3317989210cf72c5f0a791d7ed7e1545275da7cd9270fbee417f70b4395c9deb | unknown |
| 41004291277 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | full | 6 | true | true | true | true | false | acquisition_complete | 12957851099 | sha256:b56c66ec22e0957960153ba892fe99cf3e457214bc8216eef604f1a6687477af | 12957387822 | sha256:4e0ee1448b421af5f3f2ec2859e511db49fbf6d46febe471faa07dc5431cd1ac | unknown |
| 41004291277 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | full | 7 | true | true | true | true | false | acquisition_complete | 12956969282 | sha256:29436cce92bc40bdc15541a3ac8f7e734a22eaab01f79641c99e7044671b1c27 | 12957357312 | sha256:e7bc64e55e31ebf84d8015c0a9c3e25d8d1d9a09f4da7cbe31d065e4606bfdce | unknown |
| 41004291277 | a-a-k/ebpf-model-discovery-experiments | coroot | main | petclinic | full | 8 | true | true | true | true | false | acquisition_complete | 12957566725 | sha256:b4261e55746cb231e0f38231910d676646eb203ab337a4618724748259582f92 | 12958120971 | sha256:04087d7c6215a7ac126e88dee8fb196db2740b24f813d8dfafef086116155a5c | unknown |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | absent | 6 | false | true | true | false | false | technical_failure | 12956722482 | sha256:b344fcd66363eb84bd0a7ccb9b2c280a916f03a06a5dd92407a2f000e6b37128 | 12956763583 | sha256:2577544f5bc58ac73e543ca969f95ae469e37ee2612334bd340ce58f213ec7e8 | source_evaluation_technically_incomplete |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | absent | 7 | false | true | true | false | false | technical_failure | 12956910340 | sha256:69ce47c81209b207923701378e1785b3d3e9197e15419b8461a1363126b2d266 | 12956825677 | sha256:4f9ad7e334bf1269974664f0886c8146dd7947f3236fc06c02cfc24dd7face86 | source_evaluation_technically_incomplete |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | absent | 8 | false | true | true | false | false | technical_failure | 12956573029 | sha256:3f142bd7f099e5f086d1cd4b5f5fc88cd6a73ea9e6a349b82f3287e042d4c7ce | 12956971490 | sha256:ba67fd77109bf5f9e075b0fca53d8a9ac4492cfb13a544d1f742e59c72b9ce28 | source_evaluation_technically_incomplete |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | full | 6 | true | true | true | true | false | acquisition_complete | 12965722293 | sha256:24267a3fed9533cc994bbb45327e283f33a326ea5959b21218a47b0f6b1e0bcb | 12965892502 | sha256:28c192a57a86af3cd50b49ba49002dee527d3ee64ae1650112ff1262b95de4f8 | unknown |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | full | 7 | false | true | true | false | false | technical_failure | 12962352547 | sha256:a37a3f08a134be71f3a00fcc8c12d441e9c359b98c0348dbe5549250e6f125c7 | 12962666631 | sha256:efd3f9be6f431910cb77b6ba084515696e15479c0552ead1e50e54633314c781 | source_evaluation_technically_incomplete |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | full | 8 | true | true | true | true | false | acquisition_complete | 12968026204 | sha256:445f192cd7eac28d0f8be425e5cc73e81340fddeafb84e9246226a3c9fd7e138 | 12967521878 | sha256:71522b839d0cf25e66612a19cbe5f862b90cd11be8d1754a49aabf37fe256515 | unknown |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | partial | 6 | true | true | true | true | false | acquisition_complete | 12960737453 | sha256:610ec1c2967c174665fa84b6804fc36f9f8a4896be075ba6c20a8b7e92e70b5c | 12961107525 | sha256:4b01a9f1ff9b0d044b6f465a414a03c1cb5a517f5f7e0cd44879d4f6e189173d | unknown |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | partial | 7 | true | true | true | true | false | acquisition_complete | 12960248168 | sha256:fae846152b30069025b0e56aae3d993338f1ca27cc9ccf8173533b7cb27f8e5a | 12960339631 | sha256:e3dfa8085fcae7d47e4724f9744ef6e8a6c826c3774277962bb8dca6a244b149 | unknown |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | partial | 8 | true | true | true | true | false | acquisition_complete | 12960798179 | sha256:755c2379e01b651d9fcfa2808578f10f72f138294ca8ac376f525744aa77db75 | 12961026796 | sha256:fe39cf4ee30f9e4180f69a996965ed35ac252cd71991d04f5c603ce2728d8c8a | unknown |
| 41005821961 | a-a-k/ebpf-model-discovery-experiments | obi | main | deathstarbench | full | 6 | true | true | true | true | false | acquisition_complete | 12969760740 | sha256:743845edd59604a6e68bc32787304557dd528ef6ce5265e0c94ac1778a65383f | 12969188019 | sha256:057cddc59258b3ce86bfc695511d8f3e23a13a0d73e529a0ff12254be77066e0 | unknown |
| 41009954091 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | absent | 6 | true | true | true | true | false | acquisition_complete | 12960716789 | sha256:3b76a302dd9f363b68e70cac2f54aa243730d02e50458ee674de76f93f821d40 | 12960592911 | sha256:4a3c2446df61fd44095515217d5f1661e3ea0d6527b85432b8560947836aeea5 | unknown |
| 41010834860 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | absent | 7 | true | true | true | true | false | acquisition_complete | 12960084037 | sha256:e76272488bb712cba0cd727ff7b69efea1132c5d63c4c3a2ae2e39d1e363bcfd | 12959699801 | sha256:6cbe3b87128aff7e951732de5be961b3d12db690137cceab3ae0a0a2361da7c2 | unknown |
| 41011398324 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | absent | 8 | true | true | true | true | false | acquisition_complete | 12961715511 | sha256:b65774715dde172cc49ac79a03d3bec812706fcafc9b1ac2dd73f19a576a620d | 12961646180 | sha256:8aa2d0cf264fefd9512613a4d7a48a150086460c39ba028579d9336af26f383f | unknown |
| 41018310659 | a-a-k/ebpf-model-discovery-experiments | deepflow | smoke | petclinic | absent | 6 | true | true | true | true | false | smoke_complete | 12960912355 | sha256:0597f318eb9628aa7f94c4efe3d25e115afa0c12dc7d44d7e1b6211404d316e7 | 12960583383 | sha256:a22a4d5b3de0d6ebf69676baee718124e0a341569b5b6619faa7822b7de4e585 | unknown |
| 41023324471 | a-a-k/ebpf-model-discovery-experiments | deepflow | main | petclinic | absent | 6 | false | false | false | false | false | unknown | unknown | unknown | unknown | unknown | not_uploaded |
| 41024050638 | a-a-k/ebpf-model-discovery-experiments | coroot | main | otel_demo | full | 7 | true | true | true | true | false | acquisition_complete | 12967044179 | sha256:24306c99b6a8984faff0972dba66aa955c1ed7486d9d2183217bd630b20381b9 | 12968161566 | sha256:a5129f5d1cdf590aaf5644f4dbb1f6d59f45caaa2900abfd2a7138de9f2d9c97 | unknown |

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
| 40930786566 | deepflow | petclinic | absent | 6 | true | true | [] | false |
| 40930793452 | coroot | petclinic | full | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed","accepted_observation_capture_not_closed"] | false |
| 40933885726 | coroot | petclinic | full | 6 | true | true | [] | false |
| 40933892507 | coroot | otel_demo | partial | 6 | true | true | [] | false |
| 40936796228 | deepflow | deathstarbench | absent | 6 | true | true | [] | false |
| 40942437542 | coroot | otel_demo | full | 6 | true | true | [] | false |
| 40942447288 | deepflow | otel_demo | absent | 6 | false | false | ["two_guest_ebpf_origin_control_missing_or_failed"] | false |
| 40942447288 | deepflow | otel_demo | full | 6 | true | true | [] | false |
| 40942447288 | deepflow | otel_demo | partial | 6 | true | true | [] | false |
| 40943318871 | deepflow | deathstarbench | partial | 6 | true | true | [] | false |
| 40943915967 | deepflow | petclinic | partial | 6 | true | true | [] | false |
| 40943924937 | deepflow | petclinic | full | 6 | true | true | [] | false |
| 40944249737 | deepflow | deathstarbench | full | 6 | true | true | [] | false |
| 40948057864 | deepflow | otel_demo | absent | 6 | true | true | [] | false |
| 41018310659 | deepflow | petclinic | absent | 6 | true | true | [] | false |

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
| 40914709370 | obi | petclinic | partial | 8 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40914709370 | obi | petclinic | partial | 8 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40914709370 | obi | petclinic | partial | 8 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 6 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 6 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 6 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 6 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 6 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 6 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | owner_details_with_visits | native | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | owner_details_with_visits | native | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 6 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 7 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 7 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 7 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 7 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 7 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 7 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | owner_details_with_visits | native | raw | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | owner_details_with_visits | native | network_scope | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 7 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2099 | 301 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | create_visit | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | create_visit | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 8 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 8 | true | create_visit | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | create_visit | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_owners | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_owners | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 8 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 8 | true | list_owners | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_owners | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_vets | ebpf | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_vets | ebpf | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 8 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40924968145 | obi | petclinic | full | 8 | true | list_vets | combined | raw | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | list_vets | combined | network_scope | true | 1.0 | [1.0,1.0] | 2400 | 0 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | owner_details_with_visits | native | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | owner_details_with_visits | native | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | owner_details_with_visits | combined | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40924968145 | obi | petclinic | full | 8 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | add_to_cart | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | add_to_cart | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40930805848 | obi | otel_demo | absent | 6 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40930805848 | obi | otel_demo | absent | 6 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | browse_product | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | browse_product | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40930805848 | obi | otel_demo | absent | 6 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40930805848 | obi | otel_demo | absent | 6 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | checkout | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | checkout | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40930805848 | obi | otel_demo | absent | 6 | true | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40930805848 | obi | otel_demo | absent | 6 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 6 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40930805848 | obi | otel_demo | absent | 7 | false | add_to_cart | ebpf | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | add_to_cart | ebpf | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | add_to_cart | combined | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | add_to_cart | combined | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | browse_product | ebpf | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | browse_product | ebpf | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | browse_product | combined | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | browse_product | combined | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | checkout | ebpf | raw | false | unknown | [0.875,0.875] | 2799 | 401 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | checkout | ebpf | network_scope | false | unknown | [0.875,0.875] | 2799 | 401 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | checkout | native | raw | false | unknown | [0,1] | 2799 | 401 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | checkout | native | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | checkout | combined | raw | false | unknown | [0.875,0.875] | 2799 | 401 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 7 | false | checkout | combined | network_scope | false | unknown | [0.875,0.875] | 2799 | 401 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | add_to_cart | ebpf | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | add_to_cart | ebpf | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | add_to_cart | combined | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | add_to_cart | combined | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | browse_product | ebpf | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | browse_product | ebpf | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | browse_product | combined | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | browse_product | combined | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | checkout | ebpf | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | checkout | ebpf | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | checkout | combined | raw | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40930805848 | obi | otel_demo | absent | 8 | false | checkout | combined | network_scope | false | unknown | [0.875,0.875] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | compose_post | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | compose_post | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | compose_post | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | compose_post | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | compose_post | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | compose_post | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_home_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_home_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_home_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_home_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_home_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_home_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_user_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_user_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_user_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_user_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_user_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40932031732 | obi | deathstarbench | full | 6 | false | read_user_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | compose_post | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | compose_post | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | compose_post | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | compose_post | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | compose_post | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | compose_post | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_home_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_home_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_home_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_home_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_home_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_home_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_user_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_user_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_user_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_user_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_user_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935194776 | obi | deathstarbench | partial | 6 | false | read_user_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | compose_post | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | compose_post | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | compose_post | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | compose_post | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | compose_post | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | compose_post | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_home_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_home_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_home_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_home_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_home_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_home_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_user_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_user_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_user_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_user_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_user_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40935203055 | obi | deathstarbench | partial | 7 | false | read_user_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40942429097 | obi | deathstarbench | absent | 6 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 6 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 6 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_home_timeline | native | raw | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_home_timeline | native | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_home_timeline | combined | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_home_timeline | combined | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 6 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 7 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 7 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_home_timeline | native | raw | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_home_timeline | native | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_home_timeline | combined | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_home_timeline | combined | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 7 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | compose_post | native | raw | false | unknown | [0,1] | 2799 | 401 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 8 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 8 | true | compose_post | combined | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_home_timeline | native | raw | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_home_timeline | native | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_home_timeline | combined | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_home_timeline | combined | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40942429097 | obi | deathstarbench | absent | 8 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40945578755 | obi | deathstarbench | full | 7 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40945578755 | obi | deathstarbench | full | 7 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40945578755 | obi | deathstarbench | full | 7 | true | compose_post | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | compose_post | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | compose_post | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | compose_post | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_user_timeline | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_user_timeline | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_user_timeline | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40945578755 | obi | deathstarbench | full | 7 | true | read_user_timeline | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40947264867 | obi | deathstarbench | full | 6 | false | compose_post | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | compose_post | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | compose_post | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | compose_post | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | compose_post | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | compose_post | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_home_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_home_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_home_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_home_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_home_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_home_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_user_timeline | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_user_timeline | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_user_timeline | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_user_timeline | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_user_timeline | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947264867 | obi | deathstarbench | full | 6 | false | read_user_timeline | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 40947274375 | obi | deathstarbench | partial | 6 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | compose_post | native | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | compose_post | combined | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947274375 | obi | deathstarbench | partial | 6 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947287495 | obi | deathstarbench | partial | 7 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 6 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 6 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 7 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 7 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | no_frozen_source_observations |
| 40947299209 | coroot | petclinic | absent | 8 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40947299209 | coroot | petclinic | absent | 8 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 6 | false | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | checkout | ebpf | raw | false | unknown | [0,1] | 2288 | 912 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | checkout | ebpf | network_scope | false | unknown | [0,1] | 2288 | 912 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | checkout | native | raw | false | unknown | [0,1] | 2288 | 912 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | checkout | native | network_scope | false | unknown | [0,1] | 2288 | 912 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | checkout | combined | raw | false | unknown | [0,1] | 2288 | 912 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 6 | false | checkout | combined | network_scope | false | unknown | [0,1] | 2288 | 912 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 7 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | checkout | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 7 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40948072741 | obi | otel_demo | partial | 8 | false | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | checkout | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | checkout | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | checkout | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40948072741 | obi | otel_demo | partial | 8 | false | checkout | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | campaign_technical_validation_failed |
| 40953661709 | obi | deathstarbench | full | 8 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40953661709 | obi | deathstarbench | full | 8 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40953661709 | obi | deathstarbench | full | 8 | true | compose_post | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | compose_post | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | compose_post | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | compose_post | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_user_timeline | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_user_timeline | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_user_timeline | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40953661709 | obi | deathstarbench | full | 8 | true | read_user_timeline | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40956228868 | coroot | petclinic | partial | 6 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 6 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 7 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | owner_details_with_visits | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | owner_details_with_visits | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956228868 | coroot | petclinic | partial | 8 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40956239225 | obi | deathstarbench | partial | 8 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40958365058 | obi | otel_demo | absent | 7 | true | add_to_cart | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | add_to_cart | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40958365058 | obi | otel_demo | absent | 7 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40958365058 | obi | otel_demo | absent | 7 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | browse_product | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | browse_product | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40958365058 | obi | otel_demo | absent | 7 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40958365058 | obi | otel_demo | absent | 7 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | checkout | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | checkout | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40958365058 | obi | otel_demo | absent | 7 | true | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40958365058 | obi | otel_demo | absent | 7 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40958365058 | obi | otel_demo | absent | 7 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | add_to_cart | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | add_to_cart | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40959052743 | obi | otel_demo | absent | 8 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40959052743 | obi | otel_demo | absent | 8 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | browse_product | ebpf | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | browse_product | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40959052743 | obi | otel_demo | absent | 8 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40959052743 | obi | otel_demo | absent | 8 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | checkout | ebpf | raw | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | checkout | ebpf | network_scope | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | checkout | native | raw | false | unknown | [0,1] | 2799 | 401 | 0 | no_frozen_source_observations |
| 40959052743 | obi | otel_demo | absent | 8 | true | checkout | native | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | no_frozen_source_observations |
| 40959052743 | obi | otel_demo | absent | 8 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 40959052743 | obi | otel_demo | absent | 8 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 40966250927 | obi | otel_demo | full | 6 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2701 | 499 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2701 | 499 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2701 | 499 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2701 | 499 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2701 | 499 | 0 | unknown |
| 40966250927 | obi | otel_demo | full | 6 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2701 | 499 | 0 | unknown |
| 40966250927 | obi | otel_demo | full | 6 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2697 | 503 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2697 | 503 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | browse_product | native | raw | false | unknown | [0,1] | 2697 | 503 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2697 | 503 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2697 | 503 | 0 | unknown |
| 40966250927 | obi | otel_demo | full | 6 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2697 | 503 | 0 | unknown |
| 40966250927 | obi | otel_demo | full | 6 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2563 | 637 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2563 | 637 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | checkout | native | raw | false | unknown | [0,1] | 2563 | 637 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | checkout | native | network_scope | false | unknown | [0,1] | 2563 | 637 | 0 | required_graph_evidence_unavailable |
| 40966250927 | obi | otel_demo | full | 6 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 2563 | 637 | 0 | unknown |
| 40966250927 | obi | otel_demo | full | 6 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 2563 | 637 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40966258333 | obi | otel_demo | full | 7 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40966258333 | obi | otel_demo | full | 7 | true | add_to_cart | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | add_to_cart | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40966258333 | obi | otel_demo | full | 7 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40966258333 | obi | otel_demo | full | 7 | true | browse_product | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | browse_product | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2798 | 402 | 0 | required_graph_evidence_unavailable |
| 40966258333 | obi | otel_demo | full | 7 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2798 | 402 | 0 | required_graph_evidence_unavailable |
| 40966258333 | obi | otel_demo | full | 7 | true | checkout | native | raw | true | 0.875 | [0.875,0.875] | 2798 | 402 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | checkout | native | network_scope | true | 0.875 | [0.875,0.875] | 2798 | 402 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 2798 | 402 | 0 | unknown |
| 40966258333 | obi | otel_demo | full | 7 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 2798 | 402 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2749 | 451 | 0 | required_graph_evidence_unavailable |
| 40966847000 | obi | otel_demo | full | 8 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2749 | 451 | 0 | required_graph_evidence_unavailable |
| 40966847000 | obi | otel_demo | full | 8 | true | add_to_cart | native | raw | true | 0.875 | [0.875,0.875] | 2749 | 451 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | add_to_cart | native | network_scope | true | 0.875 | [0.875,0.875] | 2749 | 451 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2749 | 451 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2749 | 451 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2734 | 466 | 0 | required_graph_evidence_unavailable |
| 40966847000 | obi | otel_demo | full | 8 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2734 | 466 | 0 | required_graph_evidence_unavailable |
| 40966847000 | obi | otel_demo | full | 8 | true | browse_product | native | raw | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | browse_product | native | network_scope | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2675 | 525 | 0 | required_graph_evidence_unavailable |
| 40966847000 | obi | otel_demo | full | 8 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2675 | 525 | 0 | required_graph_evidence_unavailable |
| 40966847000 | obi | otel_demo | full | 8 | true | checkout | native | raw | true | 0.875 | [0.875,0.875] | 2675 | 525 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | checkout | native | network_scope | true | 0.875 | [0.875,0.875] | 2675 | 525 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 2675 | 525 | 0 | unknown |
| 40966847000 | obi | otel_demo | full | 8 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 2675 | 525 | 0 | unknown |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_home_timeline | native | raw | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_home_timeline | native | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_home_timeline | combined | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_home_timeline | combined | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970095079 | coroot | deathstarbench | absent | 6 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | checkout | native | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | checkout | native | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | checkout | combined | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40970638144 | obi | otel_demo | partial | 8 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2714 | 486 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2714 | 486 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2714 | 486 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2714 | 486 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2714 | 486 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2714 | 486 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2710 | 490 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2710 | 490 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | browse_product | native | raw | false | unknown | [0,1] | 2710 | 490 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2710 | 490 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | browse_product | combined | raw | false | unknown | [0,1] | 2710 | 490 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2710 | 490 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2673 | 527 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2673 | 527 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | checkout | native | raw | false | unknown | [0,1] | 2673 | 527 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | checkout | native | network_scope | false | unknown | [0,1] | 2673 | 527 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | checkout | combined | raw | false | unknown | [0,1] | 2673 | 527 | 0 | required_graph_evidence_unavailable |
| 40971766251 | obi | otel_demo | partial | 6 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2673 | 527 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_home_timeline | native | raw | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_home_timeline | native | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_home_timeline | combined | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_home_timeline | combined | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004270443 | coroot | deathstarbench | absent | 7 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | compose_post | native | raw | false | unknown | [0,1] | 2799 | 401 | 0 | no_frozen_source_observations |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | no_frozen_source_observations |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | compose_post | combined | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_home_timeline | native | raw | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_home_timeline | native | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | no_frozen_source_observations |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_home_timeline | combined | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_home_timeline | combined | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004275773 | coroot | deathstarbench | absent | 8 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 6 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 7 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | compose_post | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | compose_post | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | compose_post | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | compose_post | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_user_timeline | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_user_timeline | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_user_timeline | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004281518 | coroot | deathstarbench | partial | 8 | true | read_user_timeline | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 6 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 6 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 6 | true | compose_post | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | compose_post | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | compose_post | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | compose_post | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_user_timeline | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_user_timeline | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_user_timeline | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 6 | true | read_user_timeline | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 7 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 7 | true | compose_post | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | compose_post | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | compose_post | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | compose_post | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_user_timeline | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_user_timeline | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_user_timeline | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 7 | true | read_user_timeline | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 8 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 8 | true | compose_post | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | compose_post | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | compose_post | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | compose_post | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_user_timeline | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_user_timeline | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_user_timeline | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004285932 | coroot | deathstarbench | full | 8 | true | read_user_timeline | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004291277 | coroot | petclinic | full | 6 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | owner_details_with_visits | native | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 41004291277 | coroot | petclinic | full | 6 | true | owner_details_with_visits | native | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 41004291277 | coroot | petclinic | full | 6 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 6 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | owner_details_with_visits | native | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 41004291277 | coroot | petclinic | full | 7 | true | owner_details_with_visits | native | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 41004291277 | coroot | petclinic | full | 7 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 7 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | create_visit | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | create_visit | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | create_visit | native | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | create_visit | native | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | create_visit | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | create_visit | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_owners | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_owners | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_owners | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_owners | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_owners | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_owners | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_vets | ebpf | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_vets | ebpf | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_vets | native | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_vets | native | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_vets | combined | raw | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | list_vets | combined | network_scope | false | unknown | [0,1] | 2400 | 0 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | owner_details_with_visits | ebpf | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | owner_details_with_visits | ebpf | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | owner_details_with_visits | native | raw | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 41004291277 | coroot | petclinic | full | 8 | true | owner_details_with_visits | native | network_scope | true | 0.875 | [0.875,0.875] | 2100 | 300 | 0 | unknown |
| 41004291277 | coroot | petclinic | full | 8 | true | owner_details_with_visits | combined | raw | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004291277 | coroot | petclinic | full | 8 | true | owner_details_with_visits | combined | network_scope | false | unknown | [0,1] | 2100 | 300 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | absent | 6 | false | add_to_cart | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | add_to_cart | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | add_to_cart | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | add_to_cart | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | add_to_cart | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | add_to_cart | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | browse_product | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | browse_product | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | browse_product | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | browse_product | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | browse_product | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | browse_product | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | checkout | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | checkout | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | checkout | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | checkout | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | checkout | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 6 | false | checkout | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | add_to_cart | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | add_to_cart | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | add_to_cart | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | add_to_cart | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | add_to_cart | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | add_to_cart | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | browse_product | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | browse_product | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | browse_product | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | browse_product | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | browse_product | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | browse_product | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | checkout | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | checkout | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | checkout | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | checkout | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | checkout | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 7 | false | checkout | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | add_to_cart | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | add_to_cart | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | add_to_cart | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | add_to_cart | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | add_to_cart | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | add_to_cart | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | browse_product | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | browse_product | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | browse_product | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | browse_product | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | browse_product | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | browse_product | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | checkout | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | checkout | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | checkout | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | checkout | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | checkout | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | absent | 8 | false | checkout | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 6 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2721 | 479 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 6 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2721 | 479 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 6 | true | add_to_cart | native | raw | true | 0.875 | [0.875,0.875] | 2721 | 479 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | add_to_cart | native | network_scope | true | 0.875 | [0.875,0.875] | 2721 | 479 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2721 | 479 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2721 | 479 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2734 | 466 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 6 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2734 | 466 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 6 | true | browse_product | native | raw | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | browse_product | native | network_scope | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2734 | 466 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | checkout | ebpf | raw | false | unknown | [0,1] | 276 | 2924 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 6 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 276 | 2924 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 6 | true | checkout | native | raw | true | 0.875 | [0.875,0.875] | 276 | 2924 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | checkout | native | network_scope | true | 0.875 | [0.875,0.875] | 276 | 2924 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 276 | 2924 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 6 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 276 | 2924 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 7 | false | add_to_cart | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | add_to_cart | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | add_to_cart | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | add_to_cart | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | add_to_cart | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | add_to_cart | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | browse_product | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | browse_product | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | browse_product | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | browse_product | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | browse_product | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | browse_product | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | checkout | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | checkout | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | checkout | native | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | checkout | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | checkout | combined | raw | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 7 | false | checkout | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | campaign_technical_validation_failed |
| 41004296165 | coroot | otel_demo | full | 8 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 8 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 8 | true | add_to_cart | native | raw | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | add_to_cart | native | network_scope | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | add_to_cart | combined | raw | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | add_to_cart | combined | network_scope | true | 0.875 | [0.875,0.875] | 2799 | 401 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 8 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 8 | true | browse_product | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | browse_product | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | browse_product | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | browse_product | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | checkout | ebpf | raw | false | unknown | [0,1] | 1427 | 1773 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 8 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 1427 | 1773 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | full | 8 | true | checkout | native | raw | true | 0.875 | [0.875,0.875] | 1427 | 1773 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | checkout | native | network_scope | true | 0.875 | [0.875,0.875] | 1427 | 1773 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | checkout | combined | raw | true | 0.875 | [0.875,0.875] | 1427 | 1773 | 0 | unknown |
| 41004296165 | coroot | otel_demo | full | 8 | true | checkout | combined | network_scope | true | 0.875 | [0.875,0.875] | 1427 | 1773 | 0 | unknown |
| 41004296165 | coroot | otel_demo | partial | 6 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2686 | 514 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2686 | 514 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | checkout | native | raw | false | unknown | [0,1] | 2686 | 514 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | checkout | native | network_scope | false | unknown | [0,1] | 2686 | 514 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | checkout | combined | raw | false | unknown | [0,1] | 2686 | 514 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 6 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2686 | 514 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | browse_product | native | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | browse_product | combined | raw | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2799 | 401 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2072 | 1128 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2072 | 1128 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | checkout | native | raw | false | unknown | [0,1] | 2072 | 1128 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | checkout | native | network_scope | false | unknown | [0,1] | 2072 | 1128 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | checkout | combined | raw | false | unknown | [0,1] | 2072 | 1128 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 7 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2072 | 1128 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | checkout | ebpf | raw | false | unknown | [0,1] | 518 | 2682 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 518 | 2682 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | checkout | native | raw | false | unknown | [0,1] | 518 | 2682 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | checkout | native | network_scope | false | unknown | [0,1] | 518 | 2682 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | checkout | combined | raw | false | unknown | [0,1] | 518 | 2682 | 0 | required_graph_evidence_unavailable |
| 41004296165 | coroot | otel_demo | partial | 8 | true | checkout | combined | network_scope | false | unknown | [0,1] | 518 | 2682 | 0 | required_graph_evidence_unavailable |
| 41005821961 | obi | deathstarbench | full | 6 | true | compose_post | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41005821961 | obi | deathstarbench | full | 6 | true | compose_post | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41005821961 | obi | deathstarbench | full | 6 | true | compose_post | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | compose_post | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | compose_post | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | compose_post | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_home_timeline | ebpf | raw | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | [0,1] | 3200 | 0 | 0 | required_graph_evidence_unavailable |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_home_timeline | native | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_home_timeline | native | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_home_timeline | combined | raw | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_home_timeline | combined | network_scope | true | 1.0 | [1.0,1.0] | 3200 | 0 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_user_timeline | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_user_timeline | native | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_user_timeline | native | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_user_timeline | combined | raw | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41005821961 | obi | deathstarbench | full | 6 | true | read_user_timeline | combined | network_scope | true | 0.875 | [0.875,0.875] | 2800 | 400 | 0 | unknown |
| 41009954091 | coroot | otel_demo | absent | 6 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41009954091 | coroot | otel_demo | absent | 6 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41009954091 | coroot | otel_demo | absent | 6 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41009954091 | coroot | otel_demo | absent | 6 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41009954091 | coroot | otel_demo | absent | 6 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41009954091 | coroot | otel_demo | absent | 6 | true | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41009954091 | coroot | otel_demo | absent | 6 | true | checkout | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41009954091 | coroot | otel_demo | absent | 6 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41010834860 | coroot | otel_demo | absent | 7 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41010834860 | coroot | otel_demo | absent | 7 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41010834860 | coroot | otel_demo | absent | 7 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41010834860 | coroot | otel_demo | absent | 7 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41010834860 | coroot | otel_demo | absent | 7 | true | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41010834860 | coroot | otel_demo | absent | 7 | true | checkout | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41010834860 | coroot | otel_demo | absent | 7 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41011398324 | coroot | otel_demo | absent | 8 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41011398324 | coroot | otel_demo | absent | 8 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41011398324 | coroot | otel_demo | absent | 8 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41011398324 | coroot | otel_demo | absent | 8 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | checkout | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | checkout | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41011398324 | coroot | otel_demo | absent | 8 | true | checkout | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | no_frozen_source_observations |
| 41011398324 | coroot | otel_demo | absent | 8 | true | checkout | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41011398324 | coroot | otel_demo | absent | 8 | true | checkout | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | add_to_cart | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | add_to_cart | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | add_to_cart | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | add_to_cart | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | add_to_cart | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | add_to_cart | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | browse_product | ebpf | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | browse_product | ebpf | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | browse_product | native | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | browse_product | native | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | browse_product | combined | raw | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | browse_product | combined | network_scope | false | unknown | [0,1] | 2800 | 400 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | checkout | ebpf | raw | false | unknown | [0,1] | 189 | 3011 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | checkout | ebpf | network_scope | false | unknown | [0,1] | 189 | 3011 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | checkout | native | raw | false | unknown | [0,1] | 189 | 3011 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | checkout | native | network_scope | false | unknown | [0,1] | 189 | 3011 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | checkout | combined | raw | false | unknown | [0,1] | 189 | 3011 | 0 | required_graph_evidence_unavailable |
| 41024050638 | coroot | otel_demo | full | 7 | true | checkout | combined | network_scope | false | unknown | [0,1] | 189 | 3011 | 0 | required_graph_evidence_unavailable |

## Saved campaign and Actions costs

| Ledger field | Stored value |
|---|---|
| known_completed_job_elapsed_seconds | 841536.0 |
| runs_with_unknown_job_elapsed | 0 |
| known_stored_artifact_bytes | 391786279954 |
| runs_with_unknown_artifact_bytes | 0 |
| report_artifact_transfer | {"compact_zip_download_elapsed_seconds":564.0107061210003,"compact_zip_downloads":115,"compact_zip_received_bytes":50370485154,"compact_zip_verification_elapsed_seconds":750.3945956020004,"full_zip_recovery_downloads":15,"full_zip_recovery_received_bytes":402194831,"scope":"actual retained HTTP response bytes in this report job, including failed or rejected downloads; unavailable response bytes remain unknown","total_received_bytes":50772679985} |
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
| 40914709370 | obi | main | petclinic | partial | 8 | 6305.919572663 | 32.098533768 | 1961.397052156 | false | human preparation time was not instrumented; no full-cost advantage claimed |
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
| 40924968145 | obi | main | petclinic | full | 6 | 6398.090665682 | 29.07684072 | 1989.42000273 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40924968145 | obi | main | petclinic | full | 7 | 7109.315167426 | 27.334044431 | 2417.431727915 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40924968145 | obi | main | petclinic | full | 8 | 6776.186619836 | 30.557085862 | 2358.204626672 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40930786566 | deepflow | smoke | petclinic | absent | 6 | 823.677721411 | 20.542377561000002 | 2.2075013699999997 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40930793452 | coroot | smoke | petclinic | full | 6 | 25.44000767 | 29.58863033 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40930805848 | obi | main | otel_demo | absent | 6 | 12391.731769626 | 29.944935273 | 2758.096001437 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40930805848 | obi | main | otel_demo | absent | 7 | 9970.938074037 | 30.393821245 | 2619.239607525 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40930805848 | obi | main | otel_demo | absent | 8 | 9553.472540427 | 28.876506917 | 1794.700749967 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40932031732 | obi | main | deathstarbench | full | 6 | unknown | 29.464964787 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40933885726 | coroot | smoke | petclinic | full | 6 | 797.401016937 | 19.257466562 | 10.544589896 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40933892507 | coroot | smoke | otel_demo | partial | 6 | 938.727111795 | 20.173724045 | 3.617810422 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40935194776 | obi | main | deathstarbench | partial | 6 | unknown | 31.074729377 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40935203055 | obi | main | deathstarbench | partial | 7 | unknown | 29.028301726 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40936796228 | deepflow | smoke | deathstarbench | absent | 6 | 643.09863624 | 29.347224278 | 1.397978701 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40942429097 | obi | main | deathstarbench | absent | 6 | 8660.692883516 | 23.471524584 | 95.184906061 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40942429097 | obi | main | deathstarbench | absent | 7 | 6012.636168134 | 20.802647373 | 80.588160508 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40942429097 | obi | main | deathstarbench | absent | 8 | 11626.60791329 | 26.557070889 | 73.01127513 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40942437542 | coroot | smoke | otel_demo | full | 6 | 1049.644166707 | 24.697816681 | 3.636501563 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40942447288 | deepflow | smoke | otel_demo | absent | 6 | 855.585017435 | 23.099752107 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40942447288 | deepflow | smoke | otel_demo | full | 6 | 1492.433220284 | 18.169919743 | 566.365375157 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40942447288 | deepflow | smoke | otel_demo | partial | 6 | 1142.086115166 | 29.106133817 | 7.271877825 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40943318871 | deepflow | smoke | deathstarbench | partial | 6 | 716.365152573 | 31.400348774 | 60.449938721 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40943915967 | deepflow | smoke | petclinic | partial | 6 | 1092.335853851 | 35.519652946 | 5.218575428 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40943924937 | deepflow | smoke | petclinic | full | 6 | 1081.416185499 | 29.485184246 | 23.736949501 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40944249737 | deepflow | smoke | deathstarbench | full | 6 | 809.716521079 | 19.766154952 | 222.562505314 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40945578755 | obi | main | deathstarbench | full | 7 | 12297.999328431 | 19.227643802 | 3868.453047858 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40947264867 | obi | main | deathstarbench | full | 6 | 11137.858563503 | 25.230951425 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40947274375 | obi | main | deathstarbench | partial | 6 | 14479.785445097 | 23.695329673 | 1184.547384061 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40947287495 | obi | main | deathstarbench | partial | 7 | 14458.345136112 | 33.118840739 | 1608.115152476 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40947299209 | coroot | main | petclinic | absent | 6 | 2928.788094366 | 19.542185033 | 40.6397863 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40947299209 | coroot | main | petclinic | absent | 7 | 3276.385304199 | 29.705150758000002 | 60.449157690999996 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40947299209 | coroot | main | petclinic | absent | 8 | 3327.015341918 | 30.945186095 | 61.331366294 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40948057864 | deepflow | smoke | otel_demo | absent | 6 | 1796.403351563 | 30.271893004 | 4.291459591 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40948072741 | obi | main | otel_demo | partial | 6 | 9403.058413979 | 28.646904573 | 1048.362620168 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40948072741 | obi | main | otel_demo | partial | 7 | 11719.428450904 | 20.944914108 | 1075.768295223 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40948072741 | obi | main | otel_demo | partial | 8 | 9061.983028669 | 22.958016528 | 987.52862238 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40953661709 | obi | main | deathstarbench | full | 8 | 17419.988421896 | 29.496240635 | 3905.970279628 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40956228868 | coroot | main | petclinic | partial | 6 | 4025.338935098 | 30.252395532999998 | 169.111559475 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40956228868 | coroot | main | petclinic | partial | 7 | 4132.678311779 | 29.660984988 | 179.125312778 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40956228868 | coroot | main | petclinic | partial | 8 | 4096.450486928 | 91.271894122 | 184.543508362 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40956239225 | obi | main | deathstarbench | partial | 8 | 13760.360201491 | 29.423039877 | 1323.463270414 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40958365058 | obi | main | otel_demo | absent | 7 | 13215.292825248 | 30.566867081 | 2606.624727863 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40959052743 | obi | main | otel_demo | absent | 8 | 11357.636495978 | 29.188102862 | 1782.751419885 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40963548420 | deepflow | main | petclinic | absent | 6 | unknown | unknown | unknown | unknown | unknown |
| 40965631880 | deepflow | main | petclinic | absent | 7 | unknown | unknown | unknown | unknown | unknown |
| 40966250927 | obi | main | otel_demo | full | 6 | 14273.369409211 | 23.808957743 | 2272.43200321 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40966258333 | obi | main | otel_demo | full | 7 | 13375.730792 | 29.947905893 | 1967.820722018 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40966847000 | obi | main | otel_demo | full | 8 | 13837.613020501 | 33.956478338000004 | 2615.523904432 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40970095079 | coroot | main | deathstarbench | absent | 6 | 9798.551795629 | 23.004271832 | 30.14421794 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40970638144 | obi | main | otel_demo | partial | 8 | 12236.003296455 | 27.997966306 | 922.830428818 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40971766251 | obi | main | otel_demo | partial | 6 | 12203.010698194 | 29.302354213 | 462.58289780999996 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004270443 | coroot | main | deathstarbench | absent | 7 | 9929.191073505 | 29.963037174 | 38.904663071 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004275773 | coroot | main | deathstarbench | absent | 8 | 8298.481559554 | 23.441169857 | 30.54172977 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004281518 | coroot | main | deathstarbench | partial | 6 | 12616.392675217 | 26.34681839 | 1512.977327218 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004281518 | coroot | main | deathstarbench | partial | 7 | 13413.489878401 | 29.536812273 | 1502.273922504 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004281518 | coroot | main | deathstarbench | partial | 8 | 13389.698386594 | 28.775081595 | 1489.827842239 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004285932 | coroot | main | deathstarbench | full | 6 | 15198.538312161 | 23.383564209 | 3500.489886958 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004285932 | coroot | main | deathstarbench | full | 7 | 15317.550888451 | 29.580532042999998 | 2529.441993326 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004285932 | coroot | main | deathstarbench | full | 8 | 11726.021080816 | 21.008571938 | 3169.341275667 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004291277 | coroot | main | petclinic | full | 6 | 4185.109517243 | 29.379460779 | 271.18819824499997 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004291277 | coroot | main | petclinic | full | 7 | 3893.760875113 | 22.307284176 | 206.814321434 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004291277 | coroot | main | petclinic | full | 8 | 4417.884183442 | 29.101931302 | 277.733659599 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | absent | 6 | 3258.995180688 | 30.374037925 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | absent | 7 | 2482.908310094 | 18.218548178000002 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | absent | 8 | 3224.776374284 | 28.90550356 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | full | 6 | 6690.546347765 | 30.225311891 | 1187.47380008 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | full | 7 | 1841.795269765 | 27.643025367 | unknown | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | full | 8 | 7968.857827569 | 26.751474414 | 1464.076740539 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | partial | 6 | 6818.739541665 | 19.904257956 | 460.366399969 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | partial | 7 | 5688.211073624 | 23.835240475 | 212.92925666099998 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41004296165 | coroot | main | otel_demo | partial | 8 | 5945.316292592 | 29.473443592000002 | 166.923157819 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41005821961 | obi | main | deathstarbench | full | 6 | 18330.10613174 | 29.356326353 | 3676.462773107 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41009954091 | coroot | main | otel_demo | absent | 6 | 5183.987869027 | 29.855324176 | 118.268904808 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41010834860 | coroot | main | otel_demo | absent | 7 | 4544.919666262 | 22.206045836 | 108.987559124 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41011398324 | coroot | main | otel_demo | absent | 8 | 5184.523937016 | 30.31823032 | 130.870209919 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41018310659 | deepflow | smoke | petclinic | absent | 6 | 795.417866547 | 18.641024222 | 2.367177658 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 41023324471 | deepflow | main | petclinic | absent | 6 | unknown | unknown | unknown | unknown | unknown |
| 41024050638 | coroot | main | otel_demo | full | 7 | 5640.32549268 | 29.703308775 | 166.687573605 | false | human preparation time was not instrumented; no full-cost advantage claimed |

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
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123575154880 | prepare | completed | success | 3.0 | 0 |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123575210321 | campaign (deathstarbench, partial, 8) | completed | failure | 9848.0 | 0 |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123575210440 | campaign (deathstarbench, partial, 7) | completed | failure | 6972.0 | 0 |
| 40910021896 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123575210516 | campaign (deathstarbench, partial, 6) | completed | failure | 7127.0 | 0 |
| 40910393953 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123576483454 | prepare | completed | success | 4.0 | 3 |
| 40910393953 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123576553435 | campaign (petclinic, absent, 6) | completed | success | 1060.0 | 3 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123587138277 | prepare | completed | success | 3.0 | 0 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123587179829 | campaign (deathstarbench, full, 8) | completed | failure | 9544.0 | 0 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123587179847 | campaign (deathstarbench, full, 6) | completed | failure | 4336.0 | 0 |
| 40913407822 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123587179972 | campaign (deathstarbench, full, 7) | completed | failure | 7309.0 | 0 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123591742382 | prepare | completed | success | 3.0 | 9 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123591790633 | campaign (petclinic, partial, 6) | completed | success | 5014.0 | 9 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123591790713 | campaign (petclinic, partial, 8) | completed | success | 6657.0 | 9 |
| 40914709370 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123591790794 | campaign (petclinic, partial, 7) | completed | success | 5443.0 | 9 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598557302 | prepare | completed | success | 3.0 | 12 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598607263 | campaign (deathstarbench, absent, 6) | completed | success | 743.0 | 12 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598607345 | campaign (deathstarbench, partial, 6) | completed | success | 810.0 | 12 |
| 40916651613 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123598607439 | campaign (deathstarbench, full, 6) | completed | success | 1010.0 | 12 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123606849340 | prepare | completed | success | 3.0 | 0 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123606897153 | campaign (deathstarbench, absent, 6) | completed | failure | 6466.0 | 0 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123606897296 | campaign (deathstarbench, absent, 7) | completed | failure | 6892.0 | 0 |
| 40919005648 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123606897356 | campaign (deathstarbench, absent, 8) | completed | failure | 6419.0 | 0 |
| 40920573691 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123612367739 | prepare | completed | success | 2.0 | 3 |
| 40920573691 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123612417198 | campaign (petclinic, absent, 6) | completed | success | 946.0 | 3 |
| 40921056157 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123614070873 | prepare | completed | success | 2.0 | 3 |
| 40921056157 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123614121293 | campaign (petclinic, partial, 6) | completed | success | 1115.0 | 3 |
| 40922905708 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123620638597 | prepare | completed | success | 4.0 | 2 |
| 40922905708 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123620691943 | campaign (petclinic, full, 6) | completed | failure | 369.0 | 2 |
| 40923928201 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123624273475 | prepare | completed | success | 3.0 | 3 |
| 40923928201 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123624318547 | campaign (otel_demo, absent, 6) | completed | success | 1924.0 | 3 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123627925518 | prepare | completed | success | 3.0 | 9 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123627981286 | campaign (petclinic, full, 7) | completed | success | 7475.0 | 9 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123627981288 | campaign (petclinic, full, 6) | completed | success | 6724.0 | 9 |
| 40924968145 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123627981435 | campaign (petclinic, full, 8) | completed | success | 7108.0 | 9 |
| 40930786566 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123648342826 | prepare | completed | success | 4.0 | 3 |
| 40930786566 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123648400667 | campaign (petclinic, absent, 6) | completed | success | 940.0 | 3 |
| 40930793452 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123648367512 | prepare | completed | success | 4.0 | 2 |
| 40930793452 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123648428445 | campaign (petclinic, full, 6) | completed | failure | 145.0 | 2 |
| 40930805848 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123648408674 | prepare | completed | success | 3.0 | 9 |
| 40930805848 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123648459623 | campaign (otel_demo, absent, 8) | completed | failure | 9965.0 | 9 |
| 40930805848 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123648459777 | campaign (otel_demo, absent, 7) | completed | failure | 10369.0 | 9 |
| 40930805848 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123648459875 | campaign (otel_demo, absent, 6) | completed | success | 12923.0 | 9 |
| 40932031732 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123652683350 | prepare | completed | success | 3.0 | 3 |
| 40932031732 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123652731951 | campaign (deathstarbench, full, 6) | completed | cancelled | 5898.0 | 3 |
| 40933885726 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123659194304 | prepare | completed | success | 2.0 | 3 |
| 40933885726 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123659241725 | campaign (petclinic, full, 6) | completed | success | 902.0 | 3 |
| 40933892507 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123659218989 | prepare | completed | success | 3.0 | 3 |
| 40933892507 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123659268648 | campaign (otel_demo, partial, 6) | completed | success | 1044.0 | 3 |
| 40935194776 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123663773405 | prepare | completed | success | 3.0 | 3 |
| 40935194776 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123663817818 | campaign (deathstarbench, partial, 6) | completed | cancelled | 4680.0 | 3 |
| 40935203055 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123663803267 | prepare | completed | success | 2.0 | 3 |
| 40935203055 | a-a-k/ebpf-model-discovery-experiments | series | completed | cancelled | 123663843380 | campaign (deathstarbench, partial, 7) | completed | cancelled | 4674.0 | 3 |
| 40936796228 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123669365700 | prepare | completed | success | 3.0 | 4 |
| 40936796228 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123669419664 | campaign (deathstarbench, absent, 6) | completed | success | 769.0 | 4 |
| 40942429097 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123689004919 | prepare | completed | success | 4.0 | 12 |
| 40942429097 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123689052122 | campaign (deathstarbench, absent, 7) | completed | success | 6647.0 | 12 |
| 40942429097 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123689052173 | campaign (deathstarbench, absent, 6) | completed | success | 9426.0 | 12 |
| 40942429097 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123689052223 | campaign (deathstarbench, absent, 8) | completed | success | 12615.0 | 12 |
| 40942437542 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123689034527 | prepare | completed | success | 4.0 | 3 |
| 40942437542 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123689088841 | campaign (otel_demo, full, 6) | completed | success | 1165.0 | 3 |
| 40942447288 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123689065628 | prepare | completed | success | 2.0 | 8 |
| 40942447288 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123689101330 | campaign (otel_demo, partial, 6) | completed | success | 1281.0 | 8 |
| 40942447288 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123689101447 | campaign (otel_demo, absent, 6) | completed | failure | 979.0 | 8 |
| 40942447288 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123689101545 | campaign (otel_demo, full, 6) | completed | success | 1598.0 | 8 |
| 40943318871 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123692059854 | prepare | completed | success | 3.0 | 4 |
| 40943318871 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123692100834 | campaign (deathstarbench, partial, 6) | completed | success | 848.0 | 4 |
| 40943915967 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123694143189 | prepare | completed | success | 4.0 | 3 |
| 40943915967 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123694196637 | campaign (petclinic, partial, 6) | completed | success | 1243.0 | 3 |
| 40943924937 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123694176521 | prepare | completed | success | 3.0 | 3 |
| 40943924937 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123694225974 | campaign (petclinic, full, 6) | completed | success | 1209.0 | 3 |
| 40944249737 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123695297777 | prepare | completed | success | 3.0 | 4 |
| 40944249737 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123695340888 | campaign (deathstarbench, full, 6) | completed | success | 920.0 | 4 |
| 40945578755 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123699936537 | prepare | completed | success | 4.0 | 4 |
| 40945578755 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123699987025 | campaign (deathstarbench, full, 7) | completed | success | 13068.0 | 4 |
| 40947264867 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123705842867 | prepare | completed | success | 3.0 | 4 |
| 40947264867 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123705881863 | campaign (deathstarbench, full, 6) | completed | failure | 11684.0 | 4 |
| 40947274375 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705838825 | prepare | completed | success | 3.0 | 4 |
| 40947274375 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705877412 | campaign (deathstarbench, partial, 6) | completed | success | 15896.0 | 4 |
| 40947287495 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705885027 | prepare | completed | success | 4.0 | 4 |
| 40947287495 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705936551 | campaign (deathstarbench, partial, 7) | completed | success | 15438.0 | 4 |
| 40947299209 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705926978 | prepare | completed | success | 3.0 | 9 |
| 40947299209 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705976339 | campaign (petclinic, absent, 8) | completed | success | 3548.0 | 9 |
| 40947299209 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705976349 | campaign (petclinic, absent, 7) | completed | success | 3469.0 | 9 |
| 40947299209 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123705976473 | campaign (petclinic, absent, 6) | completed | success | 3081.0 | 9 |
| 40948057864 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123708546382 | prepare | completed | success | 3.0 | 3 |
| 40948057864 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123708590945 | campaign (otel_demo, absent, 6) | completed | success | 1937.0 | 3 |
| 40948072741 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123708592517 | prepare | completed | success | 2.0 | 9 |
| 40948072741 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123708628357 | campaign (otel_demo, partial, 6) | completed | failure | 9756.0 | 9 |
| 40948072741 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123708628420 | campaign (otel_demo, partial, 8) | completed | failure | 9403.0 | 9 |
| 40948072741 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123708628680 | campaign (otel_demo, partial, 7) | completed | success | 12082.0 | 9 |
| 40953661709 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123728065057 | prepare | completed | success | 2.0 | 4 |
| 40953661709 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123728102633 | campaign (deathstarbench, full, 8) | completed | success | 18434.0 | 4 |
| 40956228868 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123736940103 | prepare | completed | success | 2.0 | 9 |
| 40956228868 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123736977002 | campaign (petclinic, partial, 8) | completed | success | 4410.0 | 9 |
| 40956228868 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123736977074 | campaign (petclinic, partial, 6) | completed | success | 4277.0 | 9 |
| 40956228868 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123736977122 | campaign (petclinic, partial, 7) | completed | success | 4381.0 | 9 |
| 40956239225 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123736971494 | prepare | completed | success | 3.0 | 4 |
| 40956239225 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123737011218 | campaign (deathstarbench, partial, 8) | completed | success | 14731.0 | 4 |
| 40958365058 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123744349149 | prepare | completed | success | 3.0 | 3 |
| 40958365058 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123744394109 | campaign (otel_demo, absent, 7) | completed | success | 13747.0 | 3 |
| 40959052743 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123746703370 | prepare | completed | success | 4.0 | 3 |
| 40959052743 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123746750141 | campaign (otel_demo, absent, 8) | completed | success | 11888.0 | 3 |
| 40963548420 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123762165761 | prepare | completed | success | 2.0 | 1 |
| 40963548420 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123762196894 | campaign (petclinic, absent, 6) | completed | failure | 10695.0 | 1 |
| 40965631880 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123769289108 | prepare | completed | success | 4.0 | 1 |
| 40965631880 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123769331220 | campaign (petclinic, absent, 7) | completed | failure | 9900.0 | 1 |
| 40966250927 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123771414140 | prepare | completed | success | 3.0 | 3 |
| 40966250927 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123771501116 | campaign (otel_demo, full, 6) | completed | success | 14796.0 | 3 |
| 40966258333 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123771435720 | prepare | completed | success | 3.0 | 3 |
| 40966258333 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123771475825 | campaign (otel_demo, full, 7) | completed | success | 13920.0 | 3 |
| 40966847000 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123773409069 | prepare | completed | success | 2.0 | 3 |
| 40966847000 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123773442164 | campaign (otel_demo, full, 8) | completed | success | 14383.0 | 3 |
| 40970095079 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123784399981 | prepare | completed | success | 2.0 | 4 |
| 40970095079 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123784431380 | campaign (deathstarbench, absent, 6) | completed | success | 10575.0 | 4 |
| 40970638144 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123786211571 | prepare | completed | success | 4.0 | 3 |
| 40970638144 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123786251016 | campaign (otel_demo, partial, 8) | completed | success | 12704.0 | 3 |
| 40971766251 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123789994641 | prepare | completed | success | 2.0 | 3 |
| 40971766251 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123790025834 | campaign (otel_demo, partial, 6) | completed | success | 12657.0 | 3 |
| 41004270443 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895478532 | prepare | completed | success | 3.0 | 4 |
| 41004270443 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895502428 | campaign (deathstarbench, absent, 7) | completed | success | 10794.0 | 4 |
| 41004275773 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895496217 | prepare | completed | success | 2.0 | 4 |
| 41004275773 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895515284 | campaign (deathstarbench, absent, 8) | completed | success | 9332.0 | 4 |
| 41004281518 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895517576 | prepare | completed | success | 2.0 | 12 |
| 41004281518 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895536927 | campaign (deathstarbench, partial, 7) | completed | success | 14349.0 | 12 |
| 41004281518 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895536964 | campaign (deathstarbench, partial, 6) | completed | success | 13891.0 | 12 |
| 41004281518 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895537035 | campaign (deathstarbench, partial, 8) | completed | success | 14358.0 | 12 |
| 41004285932 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895525851 | prepare | completed | success | 4.0 | 12 |
| 41004285932 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895548996 | campaign (deathstarbench, full, 6) | completed | success | 16145.0 | 12 |
| 41004285932 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895549032 | campaign (deathstarbench, full, 8) | completed | success | 12579.0 | 12 |
| 41004285932 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895549043 | campaign (deathstarbench, full, 7) | completed | success | 16286.0 | 12 |
| 41004291277 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895545645 | prepare | completed | success | 3.0 | 9 |
| 41004291277 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895567790 | campaign (petclinic, full, 8) | completed | success | 4674.0 | 9 |
| 41004291277 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895567827 | campaign (petclinic, full, 6) | completed | success | 4432.0 | 9 |
| 41004291277 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123895567832 | campaign (petclinic, full, 7) | completed | success | 4095.0 | 9 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895559822 | prepare | completed | success | 3.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582420 | campaign (otel_demo, partial, 7) | completed | success | 5957.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582440 | campaign (otel_demo, absent, 8) | completed | failure | 3407.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582446 | campaign (otel_demo, partial, 6) | completed | success | 7093.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582453 | campaign (otel_demo, full, 8) | completed | success | 8309.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582464 | campaign (otel_demo, partial, 8) | completed | success | 6212.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582477 | campaign (otel_demo, absent, 6) | completed | failure | 3444.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582490 | campaign (otel_demo, absent, 7) | completed | failure | 2608.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582491 | campaign (otel_demo, full, 6) | completed | success | 6969.0 | 26 |
| 41004296165 | a-a-k/ebpf-model-discovery-experiments | series | completed | failure | 123895582580 | campaign (otel_demo, full, 7) | completed | failure | 1999.0 | 26 |
| 41005821961 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123900370797 | prepare | completed | success | 2.0 | 4 |
| 41005821961 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123900390387 | campaign (deathstarbench, full, 6) | completed | success | 19377.0 | 4 |
| 41009954091 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123913363061 | prepare | completed | success | 3.0 | 3 |
| 41009954091 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123913389380 | campaign (otel_demo, absent, 6) | completed | success | 5417.0 | 3 |
| 41010834860 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123916099160 | prepare | completed | success | 3.0 | 3 |
| 41010834860 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123916124381 | campaign (otel_demo, absent, 7) | completed | success | 4736.0 | 3 |
| 41011398324 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123917869167 | prepare | completed | success | 3.0 | 3 |
| 41011398324 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123917889686 | campaign (otel_demo, absent, 8) | completed | success | 5414.0 | 3 |
| 41018310659 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123939579785 | prepare | completed | success | 2.0 | 3 |
| 41018310659 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123939602557 | campaign (petclinic, absent, 6) | completed | success | 906.0 | 3 |
| 41023324471 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123955530874 | prepare | completed | success | 3.0 | 1 |
| 41023324471 | a-a-k/ebpf-model-discovery-experiments | series | in_progress | unknown | 123955561609 | campaign (petclinic, absent, 6) | in_progress | unknown | unknown | 1 |
| 41024050638 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123957849331 | prepare | completed | success | 3.0 | 3 |
| 41024050638 | a-a-k/ebpf-model-discovery-experiments | series | completed | success | 123957878724 | campaign (otel_demo, full, 7) | completed | success | 5921.0 | 3 |
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
| 40930225342 | a-a-k/ebpf-model-discovery-experiments | report | completed | success | 123646381660 | report | completed | success | 277.0 | 1 |
| 40930267298 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | success | 123646532100 | validate | completed | success | 27.0 | 1 |
| 40933001578 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123656095659 | checks | completed | success | 41.0 | 0 |
| 40933001578 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123656096103 | control-fixture-v5 | completed | success | 21.0 | 0 |
| 40936167947 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123667155114 | checks | completed | success | 49.0 | 0 |
| 40936167947 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123667155657 | control-fixture-v5 | completed | success | 28.0 | 0 |
| 40939886539 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123680146972 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 40939886539 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123680147316 | checks | completed | success | 38.0 | 0 |
| 40940370220 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123681857876 | checks | completed | success | 44.0 | 0 |
| 40940370220 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123681858360 | control-fixture-v5 | completed | success | 24.0 | 0 |
| 40940389382 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | success | 123681935631 | validate | completed | success | 85.0 | 1 |
| 40941788546 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123686769408 | control-fixture-v5 | completed | success | 22.0 | 0 |
| 40941788546 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123686769748 | checks | completed | success | 51.0 | 0 |
| 40941821118 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123686879177 | control-fixture-v5 | completed | success | 24.0 | 0 |
| 40941821118 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123686879728 | checks | completed | success | 42.0 | 0 |
| 40941966903 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | success | 123687394695 | validate | completed | success | 27.0 | 1 |
| 40942794914 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123690262215 | checks | completed | success | 39.0 | 0 |
| 40942794914 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123690262567 | control-fixture-v5 | completed | success | 27.0 | 0 |
| 40944739751 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123697040253 | toolchain | completed | success | 2591.0 | 1 |
| 40944384775 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123695766597 | toolchain | completed | success | 94.0 | 1 |
| 40944167469 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123695020148 | toolchain | completed | success | 99.0 | 1 |
| 40944150118 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123694955141 | toolchain | completed | success | 35.0 | 1 |
| 40943785392 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123693689442 | toolchain | completed | success | 650.0 | 1 |
| 40943380030 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123692284205 | toolchain | completed | success | 3661.0 | 1 |
| 40942940044 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123690756631 | toolchain | completed | success | 3810.0 | 1 |
| 40937875714 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123673148513 | toolchain | completed | success | 32.0 | 1 |
| 40935440166 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123664619932 | toolchain | completed | success | 34.0 | 1 |
| 40947355330 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123706108082 | checks | completed | success | 47.0 | 0 |
| 40947355330 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123706108529 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 40949256533 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123712693622 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 40949256533 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123712693978 | checks | completed | success | 48.0 | 0 |
| 40950772563 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123717986199 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 40950772563 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123717986380 | checks | completed | success | 46.0 | 0 |
| 40951264845 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123719690825 | control-fixture-v5 | completed | success | 20.0 | 0 |
| 40951264845 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123719691179 | checks | completed | success | 49.0 | 0 |
| 40953234767 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123726557187 | control-fixture-v5 | completed | success | 24.0 | 0 |
| 40953234767 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123726557257 | checks | completed | success | 45.0 | 0 |
| 40953383041 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | success | 123727079044 | validate | completed | success | 31.0 | 1 |
| 40956304402 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123737190531 | toolchain | completed | success | 334.0 | 1 |
| 40952137039 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123722712612 | toolchain | completed | success | 293.0 | 1 |
| 40951395756 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123720154462 | toolchain | completed | success | 76.0 | 1 |
| 40945101309 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123698314780 | toolchain | completed | success | 261.0 | 1 |
| 40958092919 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123743397397 | checks | completed | success | 48.0 | 0 |
| 40958092919 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123743397828 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 40960428005 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123751447906 | control-fixture-v5 | completed | success | 23.0 | 0 |
| 40960428005 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123751448337 | checks | completed | success | 36.0 | 0 |
| 40961384259 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123754730148 | checks | completed | success | 48.0 | 0 |
| 40961384259 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123754730633 | control-fixture-v5 | completed | success | 24.0 | 0 |
| 40961608465 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | failure | 123755529336 | validate | completed | failure | 145.0 | 1 |
| 40962623909 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123759038728 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 40962623909 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123759038970 | checks | completed | success | 50.0 | 0 |
| 40962839097 | a-a-k/ebpf-model-discovery-experiments | evidence | completed | success | 123759775935 | validate | completed | success | 142.0 | 1 |
| 40962996489 | a-a-k/ebpf-model-discovery-experiments | worker | completed | failure | 123760312858 | toolchain | completed | failure | 4602.0 | 1 |
| 40961433032 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123754910815 | toolchain | completed | success | 2360.0 | 1 |
| 40961018213 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123753486719 | toolchain | completed | success | 2265.0 | 1 |
| 40960091896 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123750302887 | toolchain | completed | success | 911.0 | 1 |
| 40959937824 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123749766831 | toolchain | completed | success | 2483.0 | 1 |
| 40956797206 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123738880134 | toolchain | completed | success | 4606.0 | 1 |
| 40964033154 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123763819676 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 40964033154 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123763820098 | checks | completed | success | 48.0 | 0 |
| 40964268895 | a-a-k/ebpf-model-discovery-experiments | report | completed | success | 123764626686 | report | completed | success | 713.0 | 1 |
| 40969878243 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123783685659 | checks | completed | success | 49.0 | 0 |
| 40969878243 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123783685996 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 40969756336 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123783267082 | toolchain | completed | success | 3635.0 | 1 |
| 40969673932 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123782986836 | toolchain | completed | success | 2561.0 | 1 |
| 40966153584 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123771078543 | toolchain | completed | success | 1753.0 | 1 |
| 40964830630 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123766545203 | toolchain | completed | success | 2189.0 | 1 |
| 40971568397 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123789323282 | checks | completed | success | 51.0 | 0 |
| 40971568397 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123789323532 | control-fixture-v5 | completed | success | 22.0 | 0 |
| 41003958959 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123894497892 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41003958959 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123894498098 | checks | completed | success | 48.0 | 0 |
| 40982183326 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123824624724 | toolchain | completed | success | 1286.0 | 1 |
| 40981974470 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123823946284 | toolchain | completed | success | 238.0 | 1 |
| 40980528862 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123819164293 | toolchain | completed | success | 2153.0 | 1 |
| 40977092252 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123807705150 | toolchain | completed | success | 3533.0 | 1 |
| 40976806033 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123806767051 | toolchain | completed | success | 3746.0 | 1 |
| 40976716188 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123806468152 | toolchain | completed | success | 3002.0 | 1 |
| 40971982217 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123790694714 | toolchain | completed | success | 1881.0 | 1 |
| 40971161838 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123787972176 | toolchain | completed | success | 4660.0 | 1 |
| 41005336865 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123898850748 | checks | completed | success | 46.0 | 0 |
| 41005336865 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123898850944 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41005432674 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123899148137 | validate | completed | success | 64.0 | 1 |
| 41006270185 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123901763726 | checks | completed | success | 50.0 | 0 |
| 41006270185 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123901763990 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41008128142 | a-a-k/ebpf-model-discovery-experiments | worker | completed | failure | 123907585119 | toolchain | completed | failure | 22.0 | 1 |
| 41009524682 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123912008571 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41009524682 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123912008736 | checks | completed | success | 48.0 | 0 |
| 41009591141 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123912208747 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41009591141 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123912209054 | checks | completed | success | 41.0 | 0 |
| 41009701655 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123912561097 | validate | completed | success | 6825.0 | 1 |
| 41009364058 | a-a-k/ebpf-model-discovery-experiments | worker | completed | failure | 123911512335 | toolchain | completed | failure | 27.0 | 1 |
| 41009307872 | a-a-k/ebpf-model-discovery-experiments | worker | completed | failure | 123911331538 | toolchain | completed | failure | 19.0 | 1 |
| 41010401526 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123914741054 | control-fixture-v5 | completed | success | 24.0 | 0 |
| 41010401526 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123914741301 | checks | completed | success | 46.0 | 0 |
| 41010563837 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123915249026 | declare | completed | success | 6.0 | 3 |
| 41010563837 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123915287779 | review (obi, otel_demo, absent, 6, 40930805848, f5ac530ec4a13cecd6178fffcdd886628f47af04, 1293650... | completed | failure | 333.0 | 3 |
| 41010563837 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123915287828 | review (coroot, petclinic, absent, 6, 40947299209, 86b5deb19f7ba239c6f0ff40e8b098fd7e6e7e44, 1293... | completed | success | 124.0 | 3 |
| 41010563837 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123915287956 | review (obi, deathstarbench, absent, 6, 40942429097, 5cfdd7cbb60daec95d447109a18f82219ea29e8f, 12... | completed | success | 100.0 | 3 |
| 41011552198 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123918344478 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 41011552198 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123918344877 | checks | completed | success | 49.0 | 0 |
| 41011825649 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123919195883 | declare | completed | success | 8.0 | 1 |
| 41011825649 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123919243104 | review (obi, otel_demo, absent, 6, 40930805848, f5ac530ec4a13cecd6178fffcdd886628f47af04, 1293650... | completed | success | 229.0 | 1 |
| 41011723670 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123918876657 | toolchain | completed | success | 3961.0 | 1 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123921959458 | declare | completed | success | 8.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008194 | review (coroot, petclinic, partial, 7, 40956228868, 597811ce6fad4466fd7f7511f4a5dc3bdc503a07, 129... | completed | success | 21.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008196 | review (coroot, petclinic, partial, 8, 40956228868, 597811ce6fad4466fd7f7511f4a5dc3bdc503a07, 129... | completed | success | 26.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008204 | review (obi, deathstarbench, full, 7, 40945578755, 86b5deb19f7ba239c6f0ff40e8b098fd7e6e7e44, 1294... | completed | success | 385.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008208 | review (obi, deathstarbench, partial, 8, 40956239225, 597811ce6fad4466fd7f7511f4a5dc3bdc503a07, 1... | completed | success | 341.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008214 | review (obi, otel_demo, partial, 7, 40948072741, 6a616c685c10a7e17a80b1dda452d9da9e02a693, 129414... | completed | failure | 333.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008223 | review (obi, otel_demo, full, 8, 40966847000, 6ecd280207fbf850757c2c67e807054305f058ec, 129490149... | completed | failure | 369.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008225 | review (obi, deathstarbench, partial, 6, 40947274375, 86b5deb19f7ba239c6f0ff40e8b098fd7e6e7e44, 1... | completed | success | 536.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008242 | review (obi, otel_demo, absent, 8, 40959052743, 8a985f99bfd2ecd4ebe13274e100c86feaae0560, 1294506... | completed | success | 304.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008252 | review (obi, otel_demo, absent, 7, 40958365058, 8a985f99bfd2ecd4ebe13274e100c86feaae0560, 1294593... | completed | success | 271.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008253 | review (obi, deathstarbench, partial, 7, 40947287495, 86b5deb19f7ba239c6f0ff40e8b098fd7e6e7e44, 1... | completed | success | 624.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008256 | review (obi, deathstarbench, full, 8, 40953661709, 597811ce6fad4466fd7f7511f4a5dc3bdc503a07, 1294... | completed | success | 142.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008273 | review (obi, otel_demo, full, 7, 40966258333, 6ecd280207fbf850757c2c67e807054305f058ec, 129484235... | completed | failure | 686.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922008312 | review (obi, otel_demo, full, 6, 40966250927, 6ecd280207fbf850757c2c67e807054305f058ec, 129500852... | completed | failure | 616.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922009808 | review (obi, otel_demo, partial, 8, 40970638144, 7e6b6370410f2ba2010e4ab65e1e24c736805b82, 129497... | completed | failure | 287.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922009963 | review (obi, otel_demo, partial, 6, 40971766251, eb7342e79e6f622123c572e222cbf60608b099e0, 129502... | completed | failure | 590.0 | 16 |
| 41012708130 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | failure | 123922009990 | review (coroot, deathstarbench, absent, 6, 40970095079, 7e6b6370410f2ba2010e4ab65e1e24c736805b82,... | completed | success | 47.0 | 16 |
| 41013428481 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123924228941 | checks | completed | success | 58.0 | 0 |
| 41013428481 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123924229183 | control-fixture-v5 | completed | success | 24.0 | 0 |
| 41013815571 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123925458176 | declare | completed | success | 7.0 | 3 |
| 41013815571 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123925505670 | review (coroot, petclinic, full, 7, 41004291277, c5df32ffc3039136c184b7915337836c39db811f, 129569... | completed | success | 367.0 | 3 |
| 41013815571 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123925505693 | review (coroot, petclinic, full, 6, 41004291277, c5df32ffc3039136c184b7915337836c39db811f, 129578... | completed | success | 231.0 | 3 |
| 41013815571 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123925505718 | review (coroot, petclinic, full, 8, 41004291277, c5df32ffc3039136c184b7915337836c39db811f, 129575... | completed | success | 76.0 | 3 |
| 41013289569 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123923789978 | toolchain | completed | success | 1106.0 | 1 |
| 41012877435 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123922498140 | toolchain | completed | success | 212.0 | 1 |
| 41014655142 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123928128224 | control-fixture-v5 | completed | success | 23.0 | 0 |
| 41014655142 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123928128485 | checks | completed | success | 55.0 | 0 |
| 41016676228 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123934468396 | control-fixture-v5 | completed | success | 28.0 | 0 |
| 41016676228 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123934468618 | checks | completed | success | 39.0 | 0 |
| 41016977256 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123935414414 | declare | completed | success | 7.0 | 6 |
| 41016977256 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123935460180 | review (obi, otel_demo, partial, 8, 40970638144, 7e6b6370410f2ba2010e4ab65e1e24c736805b82, 129497... | completed | success | 154.0 | 6 |
| 41016977256 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123935460181 | review (obi, otel_demo, full, 8, 40966847000, 6ecd280207fbf850757c2c67e807054305f058ec, 129490149... | completed | success | 115.0 | 6 |
| 41016977256 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123935460322 | review (obi, otel_demo, partial, 6, 40971766251, eb7342e79e6f622123c572e222cbf60608b099e0, 129502... | completed | success | 182.0 | 6 |
| 41016977256 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123935460326 | review (obi, otel_demo, partial, 7, 40948072741, 6a616c685c10a7e17a80b1dda452d9da9e02a693, 129414... | completed | success | 513.0 | 6 |
| 41016977256 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123935460327 | review (obi, otel_demo, full, 7, 40966258333, 6ecd280207fbf850757c2c67e807054305f058ec, 129484235... | completed | success | 302.0 | 6 |
| 41016977256 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123935460343 | review (obi, otel_demo, full, 6, 40966250927, 6ecd280207fbf850757c2c67e807054305f058ec, 129500852... | completed | success | 437.0 | 6 |
| 41016689338 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123934515462 | toolchain | completed | success | 392.0 | 1 |
| 41015632063 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123931211177 | toolchain | completed | success | 3101.0 | 1 |
| 41015398284 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123930491006 | toolchain | completed | success | 301.0 | 1 |
| 41015372952 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123930407339 | toolchain | completed | success | 2022.0 | 1 |
| 41015232980 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123929958135 | toolchain | completed | success | 2015.0 | 1 |
| 41015180769 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123929796269 | toolchain | completed | success | 319.0 | 1 |
| 41014933903 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123929015546 | toolchain | completed | success | 2000.0 | 1 |
| 41014644661 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123928099015 | toolchain | completed | success | 251.0 | 1 |
| 41014576497 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123927884291 | toolchain | completed | success | 467.0 | 1 |
| 41014438271 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123927461728 | toolchain | completed | success | 4485.0 | 1 |
| 41014206241 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123926718954 | toolchain | completed | success | 578.0 | 1 |
| 41017883993 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123938243494 | toolchain | completed | success | 5214.0 | 1 |
| 41021603142 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123949956296 | control-fixture-v5 | completed | success | 22.0 | 0 |
| 41021603142 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123949956603 | checks | completed | success | 49.0 | 0 |
| 41024596316 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123959598761 | control-fixture-v5 | completed | success | 25.0 | 0 |
| 41024596316 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123959599022 | checks | completed | success | 46.0 | 0 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963042485 | declare | completed | success | 6.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094408 | review (coroot, otel_demo, absent, 6, 41009954091, 5c05858e8be2962fefc58657d9809d862f2b2540, 1296... | completed | success | 92.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094421 | review (coroot, deathstarbench, full, 8, 41004285932, c5df32ffc3039136c184b7915337836c39db811f, 1... | completed | success | 366.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094458 | review (coroot, otel_demo, absent, 7, 41010834860, e1cd393b6927e47ebb40a77a7336148938d24b4d, 1296... | completed | success | 307.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094478 | review (coroot, otel_demo, partial, 6, 41004296165, c5df32ffc3039136c184b7915337836c39db811f, 129... | completed | success | 717.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094484 | review (coroot, otel_demo, partial, 7, 41004296165, c5df32ffc3039136c184b7915337836c39db811f, 129... | completed | success | 292.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094486 | review (coroot, otel_demo, absent, 8, 41011398324, e1cd393b6927e47ebb40a77a7336148938d24b4d, 1296... | completed | success | 223.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094490 | review (coroot, otel_demo, partial, 8, 41004296165, c5df32ffc3039136c184b7915337836c39db811f, 129... | completed | success | 392.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094514 | review (coroot, deathstarbench, absent, 8, 41004275773, c5df32ffc3039136c184b7915337836c39db811f,... | completed | success | 145.0 | 9 |
| 41025655518 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963094534 | review (coroot, deathstarbench, absent, 7, 41004270443, c5df32ffc3039136c184b7915337836c39db811f,... | completed | success | 199.0 | 9 |
| 41025654822 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963036057 | control-fixture-v5 | completed | success | 31.0 | 0 |
| 41025654822 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123963036246 | checks | completed | success | 53.0 | 0 |
| 41025725804 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123963274876 | toolchain | completed | success | 1959.0 | 1 |
| 41024147543 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123958154590 | toolchain | completed | success | 1582.0 | 1 |
| 41028928830 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123973697417 | declare | completed | success | 7.0 | 3 |
| 41028928830 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123973757627 | review (coroot, deathstarbench, partial, 7, 41004281518, c5df32ffc3039136c184b7915337836c39db811f... | completed | success | 133.0 | 3 |
| 41028928830 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123973757687 | review (coroot, deathstarbench, partial, 6, 41004281518, c5df32ffc3039136c184b7915337836c39db811f... | completed | success | 365.0 | 3 |
| 41028928830 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123973757693 | review (coroot, deathstarbench, partial, 8, 41004281518, c5df32ffc3039136c184b7915337836c39db811f... | completed | success | 245.0 | 3 |
| 41028928019 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123973688771 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41028928019 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123973689068 | checks | completed | success | 51.0 | 0 |
| 41030953701 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123980294794 | checks | completed | success | 43.0 | 0 |
| 41030953701 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123980295080 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41031747845 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123982870293 | archive | completed | success | 171.0 | 0 |
| 41033223355 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123987717718 | declare | completed | success | 8.0 | 2 |
| 41033223355 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123987792141 | review (coroot, deathstarbench, full, 6, 41004285932, c5df32ffc3039136c184b7915337836c39db811f, 1... | completed | success | 638.0 | 2 |
| 41033223355 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123987792220 | review (coroot, deathstarbench, full, 7, 41004285932, c5df32ffc3039136c184b7915337836c39db811f, 1... | completed | success | 674.0 | 2 |
| 41033222733 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123987708630 | checks | completed | success | 49.0 | 0 |
| 41033222733 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123987709043 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41033874875 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123989866217 | declare | completed | success | 8.0 | 1 |
| 41033874875 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123989935705 | review (coroot, otel_demo, full, 6, 41004296165, 123895582491, success, c5df32ffc3039136c184b7915... | completed | success | 400.0 | 1 |
| 41033874250 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123989856256 | checks | completed | success | 55.0 | 0 |
| 41033874250 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123989856697 | control-fixture-v5 | completed | success | 23.0 | 0 |
| 41034727463 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123992659145 | archive | completed | success | 105.0 | 0 |
| 41034987343 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123993526135 | archive | completed | success | 105.0 | 0 |
| 41029901337 | a-a-k/ebpf-model-discovery-experiments | worker | completed | success | 123976861817 | toolchain | completed | success | 464.0 | 1 |
| 41036170040 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123997424190 | archive | completed | success | 104.0 | 0 |
| 41036190259 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123997485480 | control-fixture-v5 | completed | success | 22.0 | 0 |
| 41036190259 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123997485623 | checks | completed | success | 51.0 | 0 |
| 41036205012 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123997538117 | declare | completed | success | 11.0 | 2 |
| 41036205012 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123997628602 | review (coroot, otel_demo, full, 7, 41024050638, 123957878724, success, cadafe8962000f326d467b273... | completed | success | 258.0 | 2 |
| 41036205012 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123997628603 | review (coroot, otel_demo, full, 8, 41004296165, 123895582453, success, c5df32ffc3039136c184b7915... | completed | success | 496.0 | 2 |
| 41036261914 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 123997732878 | archive | completed | success | 73.0 | 0 |
| 41044007526 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 124023474905 | declare | completed | success | 8.0 | 1 |
| 41044007526 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 124023541181 | review (obi, deathstarbench, full, 6, 41005821961, 123900390387, success, 8c6f1fac8ea73315e8ea98a... | completed | success | 145.0 | 1 |
| 41043997785 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 124023440319 | control-fixture-v5 | completed | success | 26.0 | 0 |
| 41043997785 | a-a-k/ebpf-model-discovery-experiments | preparation | completed | success | 124023440476 | checks | completed | success | 56.0 | 0 |

Human/agent preparation effort: unknown

Current report-job unfinished tail: unknown

Every source evaluation remains losslessly restorable from an explicit hash-bound payload reference. The small aggregate retains only fields used by these tables.
