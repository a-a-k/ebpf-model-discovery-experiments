# Protocol-v4 saved evaluation report

Aggregate input: [`evaluation-v4.json.gz`](evaluation-v4.json.gz)

This report copies stored evaluation metrics and descriptively counts retained causal verdicts. It introduces no threshold, cross-campaign pooling, relinking, refit, or new forecast.
Every retained campaign is listed as an attempt; selection metadata determines evaluation inclusion.

Optional saved cost input: [`costs-v4.json`](costs-v4.json)

## Grid and retained attempts

| Stored field | Value |
|---|---|
| expected_cells | 27 |
| selected_unambiguous_cells | 27 |
| retained_campaign_attempts | 28 |
| expected_primary_total | 939600 |
| selected_primary_total | 939600 |
| retained_attempt_primary_total | 964200 |
| missing_cells | none |

All retained attempts (not all are necessarily selected):

| Run | System | Mode | Seed | Complete | Status | Retained root | Primary |
|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40718674400/v4-summary-petclinic-full-6-40718674400 | 34800 |
| 40733841068 | petclinic | absent | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733841068/v4-summary-petclinic-absent-6-40733841068 | 34800 |
| 40733841068 | petclinic | absent | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733841068/v4-summary-petclinic-absent-7-40733841068 | 34800 |
| 40733841068 | petclinic | absent | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733841068/v4-summary-petclinic-absent-8-40733841068 | 34800 |
| 40733846961 | petclinic | partial | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733846961/v4-summary-petclinic-partial-6-40733846961 | 34800 |
| 40733846961 | petclinic | partial | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733846961/v4-summary-petclinic-partial-7-40733846961 | 34800 |
| 40733846961 | petclinic | partial | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733846961/v4-summary-petclinic-partial-8-40733846961 | 34800 |
| 40733852492 | petclinic | full | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733852492/v4-summary-petclinic-full-7-40733852492 | 34800 |
| 40733858113 | petclinic | full | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733858113/v4-summary-petclinic-full-8-40733858113 | 34800 |
| 40754529169 | otel_demo | full | 6 | false | technical_failure | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40754529169/v4-summary-otel_demo-full-6-40754529169 | 24600 |
| 40786403012 | otel_demo | full | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40786403012/v4-summary-otel_demo-full-6-40786403012 | 34800 |
| 40803782214 | otel_demo | absent | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803782214/v4-summary-otel_demo-absent-6-40803782214 | 34800 |
| 40803782214 | otel_demo | absent | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803782214/v4-summary-otel_demo-absent-7-40803782214 | 34800 |
| 40803782214 | otel_demo | absent | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803782214/v4-summary-otel_demo-absent-8-40803782214 | 34800 |
| 40803790289 | otel_demo | partial | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803790289/v4-summary-otel_demo-partial-6-40803790289 | 34800 |
| 40803790289 | otel_demo | partial | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803790289/v4-summary-otel_demo-partial-7-40803790289 | 34800 |
| 40803790289 | otel_demo | partial | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803790289/v4-summary-otel_demo-partial-8-40803790289 | 34800 |
| 40803798632 | otel_demo | full | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803798632/v4-summary-otel_demo-full-7-40803798632 | 34800 |
| 40803806299 | otel_demo | full | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803806299/v4-summary-otel_demo-full-8-40803806299 | 34800 |
| 40821198727 | deathstarbench | full | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821198727/v4-summary-deathstarbench-full-6-40821198727 | 34800 |
| 40821214009 | deathstarbench | absent | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821214009/v4-summary-deathstarbench-absent-6-40821214009 | 34800 |
| 40821214009 | deathstarbench | absent | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821214009/v4-summary-deathstarbench-absent-7-40821214009 | 34800 |
| 40821214009 | deathstarbench | absent | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821214009/v4-summary-deathstarbench-absent-8-40821214009 | 34800 |
| 40821232082 | deathstarbench | partial | 6 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821232082/v4-summary-deathstarbench-partial-6-40821232082 | 34800 |
| 40821232082 | deathstarbench | partial | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821232082/v4-summary-deathstarbench-partial-7-40821232082 | 34800 |
| 40821232082 | deathstarbench | partial | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821232082/v4-summary-deathstarbench-partial-8-40821232082 | 34800 |
| 40821255620 | deathstarbench | full | 7 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821255620/v4-summary-deathstarbench-full-7-40821255620 | 34800 |
| 40821277823 | deathstarbench | full | 8 | true | acquisition_complete | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821277823/v4-summary-deathstarbench-full-8-40821277823 | 34800 |

Saved artifact provenance:

| Run | System | Mode | Seed | Head SHA | Summary artifact ID | Summary artifact | Summary digest | Full artifact ID | Full artifact | Full digest | Evaluation SHA-256 | Manifest SHA-256 | Original campaign root | Retained compact root | Full originals reverified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | ea2e278e50f64bd50597c243d84f834be1b92576 | 12834368897 | v4-summary-petclinic-full-6-40718674400 | sha256:27933333a58a1990652725c9bf6d0bd769e436799cf920b2bf8d9c5669261faf | 12834864581 | campaign-v4-petclinic-full-6-40718674400 | sha256:d94dbd5b37505d41e32e4cd0ff7545bfa08d581a6dc4a944f777b11540915bb6 | 8951d56bba5c424c9ae1184ca29e324e38a8d15c5380b4594b13c7895d1ad6ff | b9f75f032743cdfa1f4cd6339e6f027492d5a37be1a81637d725e0fbec7ae0e1 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40718674400/v4-summary-petclinic-full-6-40718674400 | false |
| 40733841068 | petclinic | absent | 6 | 4276ea92c3eea897df27be7a65846238847bdfea | 12839653993 | v4-summary-petclinic-absent-6-40733841068 | sha256:39b9c3ece41d78e0099b039a910c092a060f202ea5daf04ef3534f55d15a3fad | 12840407519 | campaign-v4-petclinic-absent-6-40733841068 | sha256:d880359babf50fb9e04ec48b792a67bfb55c66a56a599ab7c0e540cb1ebfd63e | 07de8001f19d90829dc719084cab08b7672068d76e5aa1e4cdf9738b68127a85 | 0ad3716299c418c22cd73cf12ac2ebc5a91ead647c441a98d43ef74fb17436e3 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733841068/v4-summary-petclinic-absent-6-40733841068 | false |
| 40733841068 | petclinic | absent | 7 | 4276ea92c3eea897df27be7a65846238847bdfea | 12839863596 | v4-summary-petclinic-absent-7-40733841068 | sha256:7c29454e68ffe85a587d5f7ba1050a9cebec65796fa3f50080ef63aa1161f7ca | 12840946244 | campaign-v4-petclinic-absent-7-40733841068 | sha256:5c447df34e906765d3dd4cb643feb0f905f4cb5a543706185c531aeae62ed4fe | 8c430e6cc7fb2bb218fa2d16d4717b084c4684cdc74aea9dd2d3f9e115ddfdd7 | 03ebb6479937c17651470bbd43fb2aaebcf84d176b2b2d69f9e89cf99693a32a | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733841068/v4-summary-petclinic-absent-7-40733841068 | false |
| 40733841068 | petclinic | absent | 8 | 4276ea92c3eea897df27be7a65846238847bdfea | 12840556183 | v4-summary-petclinic-absent-8-40733841068 | sha256:fee16fdb77443376e7568e5e34bfa2bb10a758ac32930ea39657829d04e91d70 | 12838779337 | campaign-v4-petclinic-absent-8-40733841068 | sha256:cd0c1b52915c3720ecb4ced9674c5313a0ad5ed840d3ff4e6da2be6fb8587d5d | a870041c52fe9e93d4ecb916b79223303f288f2677d07e6b6c0278336c9e4bff | 9b6bf6f6f632d3ef27e0da387334a741c5cfdb4576d068ae146cc6fc7f357390 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733841068/v4-summary-petclinic-absent-8-40733841068 | false |
| 40733846961 | petclinic | partial | 6 | 4276ea92c3eea897df27be7a65846238847bdfea | 12841233237 | v4-summary-petclinic-partial-6-40733846961 | sha256:3dbf4d435a6f745675ba37d18fa9e17e9378608a80b35c611757175258ee49b3 | 12842825515 | campaign-v4-petclinic-partial-6-40733846961 | sha256:c324cec5cf9f13a87ab8404f7b124134bb49bd3cf65001b994dbfcfb5edd2767 | a2028861e32a9b10f12551e978d62a85d2556c299f735e0245d55be87fb74fe4 | 3f506a24f248d4675ef6d0d504e7e519b001a83680035c4459564d6b26aaa020 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733846961/v4-summary-petclinic-partial-6-40733846961 | false |
| 40733846961 | petclinic | partial | 7 | 4276ea92c3eea897df27be7a65846238847bdfea | 12841251276 | v4-summary-petclinic-partial-7-40733846961 | sha256:8b67811e31e0647fecfbe00743c32517bb5d2936c32fe9c3692b2b78a3816ec4 | 12841920025 | campaign-v4-petclinic-partial-7-40733846961 | sha256:50a7481cac8360ad11af037905e8fa2736f07a123b9c9e38498b9560ccaf29c4 | 2d39d6ea03b2a69dfa4e06b60b1217474a8ac8a13f6eb9bab5c8820d96f3d972 | e1cc8c6361190cac6a3af816c1d691eedcbdde8cee26a9fe870cf3ae72dad32f | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733846961/v4-summary-petclinic-partial-7-40733846961 | false |
| 40733846961 | petclinic | partial | 8 | 4276ea92c3eea897df27be7a65846238847bdfea | 12841825376 | v4-summary-petclinic-partial-8-40733846961 | sha256:41d45fb0afe503d65df6e35e33aa7ee2385d48cde44f64ed3948e84f957dd32b | 12840143004 | campaign-v4-petclinic-partial-8-40733846961 | sha256:36013a8bae4570aad67e6308f6be0587291f3cf05959c9ad2c265a76139b5212 | a7db48b9a93b98760a9a82e2b7ee15f8077af66b30f2f325e0059ff5902a918a | da766e77d4b835fb64ad4652149f00ccbd6eb0ad2486f13e3870aaad72345381 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733846961/v4-summary-petclinic-partial-8-40733846961 | false |
| 40733852492 | petclinic | full | 7 | 4276ea92c3eea897df27be7a65846238847bdfea | 12841168157 | v4-summary-petclinic-full-7-40733852492 | sha256:dbd4e402a801e61d1e89611bd31adcc73bcd2544bcf83a9ba9f7191cf48e0210 | 12842530993 | campaign-v4-petclinic-full-7-40733852492 | sha256:a8118d7807c7cc618be11770f4f98f7f43364ed9281a2651debc97950b3a1fb0 | 12b60b469db9695adb769632fec1d140eb2d7d14b21df5e5849552f7447768cd | 756949bd5e902dd25f0e0a5dca126a509bf70d77a91da906adfbedab7b250b9b | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733852492/v4-summary-petclinic-full-7-40733852492 | false |
| 40733858113 | petclinic | full | 8 | 4276ea92c3eea897df27be7a65846238847bdfea | 12842832029 | v4-summary-petclinic-full-8-40733858113 | sha256:ebcf5681ea1b211845d3707bdb6cd8d444a2d6599988640ba15fcf67638fcfc2 | 12842727211 | campaign-v4-petclinic-full-8-40733858113 | sha256:2ded3d20fff16e9c660ee98b0f6c3dc360298ee3993e815c1ba987ba137fba2a | 1698aee7bff2d73a434d5a903e7f6e718dd71dfa1d388bba4610731aaa8e5496 | db3fceadc5bcc2cab75c6139452829a4dc6b52ed77e7d9511680ba1bd2a6fff0 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40733858113/v4-summary-petclinic-full-8-40733858113 | false |
| 40754529169 | otel_demo | full | 6 | 72133c00df3f7e4150a3f737dee33e4bee12527d | 12854148226 | v4-summary-otel_demo-full-6-40754529169 | sha256:7289f4cacb7d648600a3f67a8e14034035b0171b1a51220f75e0c4988ef1e2ff | 12854127667 | campaign-v4-otel_demo-full-6-40754529169 | sha256:25926b4ce1cb1ea25d7c7b43ea03135630554d7fd455750c5d56232eed2446b9 | 30c58fa8541db4f3c6c03361c7371f61655231c98c712a98533d335b8bb39b49 | 73b1b4379f3f091ab83748f2175f075fa7a6302ab6d9759c236c5a0e0350377b | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40754529169/v4-summary-otel_demo-full-6-40754529169 | false |
| 40786403012 | otel_demo | full | 6 | a0e7644362a4e1ac5913f33f06a9570f2a780000 | 12865817745 | v4-summary-otel_demo-full-6-40786403012 | sha256:92f76b999a09878b6dbc7f63590d50d16be3b0822a9f11fdcf8773c7a4741f3a | 12866546109 | campaign-v4-otel_demo-full-6-40786403012 | sha256:d169face1d0c694e31ade8fb88ed4021447e6120ce06a2efddbe17f75b4e58cd | 35217aa342e0dce37d4f0de4025fe8810ea3e0de68766eac25769ea2691d0bb9 | 798793ba9f5d5dc94771f17463e5075e0d4ed9f265922790b0e595d232461c48 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40786403012/v4-summary-otel_demo-full-6-40786403012 | false |
| 40803782214 | otel_demo | absent | 6 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12870948672 | v4-summary-otel_demo-absent-6-40803782214 | sha256:6d230df0c85515512f53cda8078a8df1f58137aa692db840e36231a80e1bd27d | 12870644611 | campaign-v4-otel_demo-absent-6-40803782214 | sha256:0f08cd7b368562c73eb40957f4af5a3fdd975e9aa1677315a0c81e10aba3cb6a | d337c70a0559955b093c37e9a8598ac853867129b651ea75ef61ce3837a2c116 | e64307fe3645ac91bd3810b9310228b883acaacad7d0214de97d85bf5fc27fea | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803782214/v4-summary-otel_demo-absent-6-40803782214 | false |
| 40803782214 | otel_demo | absent | 7 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12871528415 | v4-summary-otel_demo-absent-7-40803782214 | sha256:038fdb93f335f2c7a3d9723cea794e1a3d1585185ce1cc638453f83a47328d57 | 12871573205 | campaign-v4-otel_demo-absent-7-40803782214 | sha256:64c6d72ec37bc096c4f8865319eb8288fd6051240c52dca0238d6a4fc0c70eac | 53b9b55e399e92d6760be73c978760ac4645e73b913cb266bc4604ccadb75868 | da080d66e97dd7c2123bafe8a7949022865798dbac8d97e499ef14f294207bd2 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803782214/v4-summary-otel_demo-absent-7-40803782214 | false |
| 40803782214 | otel_demo | absent | 8 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12870904164 | v4-summary-otel_demo-absent-8-40803782214 | sha256:782d1a22f3f326ff075c5ec441caef1aee8597ae4ad4c74042333efd90568d8a | 12871791406 | campaign-v4-otel_demo-absent-8-40803782214 | sha256:eac83d00f20f60cd9e43d24fdfb602ce30d92b90f02ef4239a546937cd7e1aa0 | 48c590a41d9c393484e4e874bf543afa9c1f249659b24dec49894448435242dd | e79b38f88afde036d34896df57d3022ca9512fc61e3fa398934627461732922b | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803782214/v4-summary-otel_demo-absent-8-40803782214 | false |
| 40803790289 | otel_demo | partial | 6 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12871384569 | v4-summary-otel_demo-partial-6-40803790289 | sha256:33d181a89b7ac235fad4219de2305a661ce4a52c83b1e921df1e22908bb4ddd6 | 12871882388 | campaign-v4-otel_demo-partial-6-40803790289 | sha256:fae58e75f73185d46d6a755db936d1dbdb7b5df3f2c1b867cfffc7e95836757a | c9971665580de90b6fe6cbc7d227614d8a582c831b3fce83ca02786aadd6f09e | 0a16ad3cef0bb36c8d896ebdd9b90bda6920e6509e9eb599e2993f55e98c41ea | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803790289/v4-summary-otel_demo-partial-6-40803790289 | false |
| 40803790289 | otel_demo | partial | 7 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12871453500 | v4-summary-otel_demo-partial-7-40803790289 | sha256:735fa712528cdd84d5cbda727a29688ae799125c2a8a577302035e26c62c169f | 12872041102 | campaign-v4-otel_demo-partial-7-40803790289 | sha256:1d95332918cdb26090d703393544575dccec8ed221e47e94b39076e27a1f5967 | 82984f064df53de6ec33ec9dfa436d4d0cda84041f674ac401ade23d21a1a111 | 1581da44c777f2bfc4a54fda30fbc335faa8357b00f09fa90b249320cbd7331a | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803790289/v4-summary-otel_demo-partial-7-40803790289 | false |
| 40803790289 | otel_demo | partial | 8 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12870714010 | v4-summary-otel_demo-partial-8-40803790289 | sha256:38ef9bc835837f060183e7e353382d1e2b552e39cb0ff84d975a0451cbba8a8a | 12870708996 | campaign-v4-otel_demo-partial-8-40803790289 | sha256:1371f84669a7c78ab2d5bc2148827f6a1c5ab114873cbfc0eef98e75fdc5f218 | 186bc550d524b6329bf9fe08e94ce8f73d4cac3cafb537774226258175ac07f9 | f9f7879baf860acfd104f9abbe43951f43e2238fdbf8064a4637ce7d574390bc | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803790289/v4-summary-otel_demo-partial-8-40803790289 | false |
| 40803798632 | otel_demo | full | 7 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12872983053 | v4-summary-otel_demo-full-7-40803798632 | sha256:375efd078553f085b60453b9b5ebf46abec4a5b4f0a86dc845ab8fbe1ca68db8 | 12872968191 | campaign-v4-otel_demo-full-7-40803798632 | sha256:d4b649a46177b365b3092bc7df3f517f58691f0e75508da6e7414f7d16d821b2 | e9d59dbe64d9021fe71c841a940e3f3e9e95bfb969af8937555e63b018decec0 | bd53490d4146cf987fa0614c3505930e0dbb380ed8753947cef2ff38267595dc | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803798632/v4-summary-otel_demo-full-7-40803798632 | false |
| 40803806299 | otel_demo | full | 8 | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | 12872469826 | v4-summary-otel_demo-full-8-40803806299 | sha256:293afe8f7957f5ac19cc9c031b43ff9256893ad506393f39aaf1c0d679cc29f4 | 12873830086 | campaign-v4-otel_demo-full-8-40803806299 | sha256:07ca25fad2d24379717f6501fb23a703f669cecb60bd357a82a630eb9ac6c6a1 | b1b430dd707c008d3216475aaad6461c5fa1044dc6315d5108af9ccb47a1bc23 | 51ebc8d0fb7964357b5791fee528413aa36285f1e78d6e13112c49eddeba2e04 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40803806299/v4-summary-otel_demo-full-8-40803806299 | false |
| 40821198727 | deathstarbench | full | 6 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12887450951 | v4-summary-deathstarbench-full-6-40821198727 | sha256:80669964701d785f7357082cc6ceec9e717a5eeababf4c6697c16e2b776e25d0 | 12887148746 | campaign-v4-deathstarbench-full-6-40821198727 | sha256:237fab102f5c44935ff699d01b3cf5c96e496fed8114d062d7f90cd5d777d08b | 0760effa307c620520ba4b21771364102e91eb33e83a47f00356fc86b82c3054 | d94739ad73018bcb15b9ac99459afd452e928e7ec7dca9e20694ea696e882d1f | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821198727/v4-summary-deathstarbench-full-6-40821198727 | false |
| 40821214009 | deathstarbench | absent | 6 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12879185808 | v4-summary-deathstarbench-absent-6-40821214009 | sha256:c4c777f54bf26c85bf19202f5b6495977330d41ea2943e4894a4f965ff669c55 | 12878682223 | campaign-v4-deathstarbench-absent-6-40821214009 | sha256:178d1af5f083b52fcf9e417bed1a4785c3126b94813c349e1c238ec047571b9e | 02bd9ebc2e767c36364e9858865ad8a0ca727dd234a1c01f1c10498f3b0f2b4a | 0c0ae404324e16ad42d25b2331dfd5c4bcc131df3513f056c9ecbecfb181dc6a | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821214009/v4-summary-deathstarbench-absent-6-40821214009 | false |
| 40821214009 | deathstarbench | absent | 7 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12882771753 | v4-summary-deathstarbench-absent-7-40821214009 | sha256:bcbce9de2393c1b1ab8e2ade788807217aefdee48fcab4a028d59d2289e434db | 12882269522 | campaign-v4-deathstarbench-absent-7-40821214009 | sha256:66cbe8d56e951612279507c6f0376dcd55ffe9512031fdc4e1b5d2f01df41e6c | ec53e8eca46c210c55dcdb1dec1c4a088e8bae34fadb9237da38156900ace9e1 | 54f141fe95c3aa784139cfa976d854d91c3207572311c02566d205b43dfb2b0d | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821214009/v4-summary-deathstarbench-absent-7-40821214009 | false |
| 40821214009 | deathstarbench | absent | 8 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12880795128 | v4-summary-deathstarbench-absent-8-40821214009 | sha256:279db89f2ebb64a2fab0918a24640ecd62429ce66947c69c39db97ca8f3b7e5c | 12880905119 | campaign-v4-deathstarbench-absent-8-40821214009 | sha256:5cb7097c5ddc43e61b2a5dc27e50da4299b4f5ce45398a0ff835073aa6e75072 | 83a75f58b135e45b5bdbd312d1348662fee12594196871c4cb116af8c26accf0 | 9a9ffcf62d3d839783970da3df6e20e1c78a2b0ee1d7159c2c9a069f3f734be0 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821214009/v4-summary-deathstarbench-absent-8-40821214009 | false |
| 40821232082 | deathstarbench | partial | 6 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12879651672 | v4-summary-deathstarbench-partial-6-40821232082 | sha256:7d1c060769805a0895ae3106c027c843f7e249a86e4d47a65fcd5374ca408ab0 | 12879866816 | campaign-v4-deathstarbench-partial-6-40821232082 | sha256:975316c52415e89b1398405f9de4e61c2c2d95e8cc5ac627727411467822c189 | d1489191d344807c2f733f1dec766910145eec1e63f625190794e3943b52b037 | 9f99e860a7f66ac511f3d7fc64c623fde9ce3a8d46017ea26f6f227b438d8560 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821232082/v4-summary-deathstarbench-partial-6-40821232082 | false |
| 40821232082 | deathstarbench | partial | 7 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12883490831 | v4-summary-deathstarbench-partial-7-40821232082 | sha256:eab3afa76dec84544e2d906c38577c2169acd0f1f7e9b7267a69235fb801fad8 | 12883023547 | campaign-v4-deathstarbench-partial-7-40821232082 | sha256:fedaf5290654a0a469f2f688fdf8c0e0ab9e6bc6374dddfd5e6bdbe8a89e9143 | baaed7fe8ccf82b846004ee81239924c08a76473b9aff22afd65220cece9c93a | e80e8dd45f92abf8b5f26f57d2067fc7d1789edebc4b5059da2e132c9ec43cee | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821232082/v4-summary-deathstarbench-partial-7-40821232082 | false |
| 40821232082 | deathstarbench | partial | 8 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12883003691 | v4-summary-deathstarbench-partial-8-40821232082 | sha256:f3b02e7f3a55ba3c0d269a6b0bbd2664a7a01069e6821564e420b81dcbf4965d | 12883423696 | campaign-v4-deathstarbench-partial-8-40821232082 | sha256:c80c8dff9c97f1ccc360a93908e1b087af61b9b244817f609219ed54ce3c28e8 | 6cd64b9faac25dfb53ec26d1ee0f2194a48d33f905493097f4fea155df65db6f | fdee65365384a1a0ee25dacc7e228705ae8170bdf3f34d0bbfc43ae676ce59db | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821232082/v4-summary-deathstarbench-partial-8-40821232082 | false |
| 40821255620 | deathstarbench | full | 7 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12885596837 | v4-summary-deathstarbench-full-7-40821255620 | sha256:aa84fd84d6a75b82e7389c7c4e639e35d2d91804ff745c80e3f2f21c501eb65d | 12886335110 | campaign-v4-deathstarbench-full-7-40821255620 | sha256:14108fd66dc2ed5301deb249ac53bc094bde05cd0a597996206f1df7a0a5fa28 | a720c395152531f99761606053bf52bb4761ef09ea4f6e61395994c19d189721 | 0213eb08e218d710c8401c94109cdff13a107370799ef370d32b45fb1ee9397a | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821255620/v4-summary-deathstarbench-full-7-40821255620 | false |
| 40821277823 | deathstarbench | full | 8 | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | 12885575667 | v4-summary-deathstarbench-full-8-40821277823 | sha256:6fb10f0249c73db7e467945cd419f9723120532e8c0fd0c8ffd83797e3a36840 | 12885307760 | campaign-v4-deathstarbench-full-8-40821277823 | sha256:1a2559402dc8d35b9d3ddace0b70e57a0e70d6868aa1821a569bd4e10637a6cb | a00ab2129fac0da03adbda58195d1bd0ec55e4159991782586667add7dbdfc31 | 61255c1b8c1a68f296146b652de861c8b56e720e27a018334b81d2ca8ed1f607 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/campaign | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40821277823/v4-summary-deathstarbench-full-8-40821277823 | false |

## Selection and technical replacements

| Stored field | Value |
|---|---|
| manifest | cells=candidate_roots=work/v4-inputs/40754529169/v4-summary-otel_demo-full-6-40754529169, work/v4-inputs/40786403012/v4-summary-otel_demo-full-6-40786403012; explanation=The first attempt failed before forecast import and target traffic; the separately reviewed replacement is the sole complete campaign. Both original summaries and all costs remain retained. Selection does not depend on forecast availability or accuracy.; mode=full; reason_code=technical_worker_interruption_before_forecast_and_validation; seed=6; selected_root=work/v4-inputs/40786403012/v4-summary-otel_demo-full-6-40786403012; system=otel_demo; policy=technical_replacement_only_no_outcome_selection |
| path | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/docs/report-v4-technical-selection.json |
| provided | true |
| sha256 | bee4fdc92de743d42cb7bcaab61885e4290023082dc44e58619d05ccb97e1270 |

Technical replacements:

| Cell | Selected root | Excluded roots | Reason |
|---|---|---|---|
| otel_demo, full, 6 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40786403012/v4-summary-otel_demo-full-6-40786403012 | /home/runner/work/ebpf-model-discovery-experiments/ebpf-model-discovery-experiments/work/v4-inputs/40754529169/v4-summary-otel_demo-full-6-40754529169 | technical_worker_interruption_before_forecast_and_validation |

Ambiguous duplicate cells (unscored unless explicitly selected):

| Cell | Candidate roots | Reason |
|---|---|---|
| unavailable | unknown | unknown |

## Per-attempt forecasts and external outcomes

| Run | System | Mode | Seed | Complete | Operation | Source | Variant | Available | Forecast | Forecast interval | Actual true | Actual false | Actual unknown | External bounds | Worst-end error | Unavailable reason | Graph SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 6ce42fc4696e641d95c24d6c190227ce16f0b783fecefc46255941f6c3e0d854 |
| 40718674400 | petclinic | full | 6 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 3dd528d6044843e9cebd360bfda1a6d84ce57d0a363e013c45e8e90046121580 |
| 40718674400 | petclinic | full | 6 | true | create_visit | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | dc0753883eebb2d8e22e20615939a5463a6ee2c00e9b5eda18163ee6603a6426 |
| 40718674400 | petclinic | full | 6 | true | create_visit | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 979d9b3e4b7ba7f63eb1657be64220c11fde5c1d0e34ff77532165f9dbafebda |
| 40718674400 | petclinic | full | 6 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 32f336ddf257fa741939899c7b929633cee1d148460f8ff38dec2ca53276138f |
| 40718674400 | petclinic | full | 6 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 3d04df7446e8adf05fab36594add4af378899d35819f14149c983cdc2d8a5adb |
| 40718674400 | petclinic | full | 6 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 2132a67933c6cbf1bbd7d125afaed7690f46ff11e3e78f42a74938cbe208683d |
| 40718674400 | petclinic | full | 6 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c69df99714122691e44882de5757919d1eb4e0d80c860ddc30d71e0d3040e406 |
| 40718674400 | petclinic | full | 6 | true | list_owners | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 14b31ec24df704e5e0da070762954400a227c14be6635d3bca607e96b82145f2 |
| 40718674400 | petclinic | full | 6 | true | list_owners | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e368fb6b2f4343b384f0421f768611d0b693bb5b570ee31924ba17060bf7e60c |
| 40718674400 | petclinic | full | 6 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 21c42b941fc39fc302da9e58b05d638b97224292399c53bd880dc0ce06e1af34 |
| 40718674400 | petclinic | full | 6 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 05bf7aa8250b735892dc0846c28d91287a1f49864e9b190a95ce872de5a9ee9a |
| 40718674400 | petclinic | full | 6 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 80e1da5b9c6f511b93d4d5d4cc7e9678927682328cef7bb347dfc3357f02c239 |
| 40718674400 | petclinic | full | 6 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 0172d1a10a4e4d59f70351722a5b999f0bb65b318d0eae4323d8df5c3ef34dea |
| 40718674400 | petclinic | full | 6 | true | list_vets | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 6b97acfdd4eb92dec9ba3a6007dabf1b500ad341579e94b6df3c2656777b269c |
| 40718674400 | petclinic | full | 6 | true | list_vets | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 9bae759599c1027b6fcfef63721e7f74bf531051223db724ed72fb523f12ffe4 |
| 40718674400 | petclinic | full | 6 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c1ff308a7d0c1139174af7b55989a34fe058419448a34b7acc01d48adcd0d77a |
| 40718674400 | petclinic | full | 6 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | a3def3945d88d25903a230204cf369ad5cd8fb8e9159cf256ffdebb5308849d7 |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | e9ae8b6fee4a747162b5917f4e7c89bdd732192763b509c8489fa3e84299375b |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | a6e7ccc9468ff2c847a4feb6bc0b010d6df6f9173b7fa6d460d9394141da186e |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | f2f3a2cc470bb3b4240af457110a6107f74cec1cb1ddb809ee266b83da2eacc5 |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 20e88aae5f0a508fa97cb2c4c627e71bc34b45844a68578f81a84d1003ef240f |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 27899edf15cc089bb71b2b2492db75e41a5cf06a682fa212da744e6d7c391f06 |
| 40718674400 | petclinic | full | 6 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | d4b93229caf81d1acd7d66fe6a762c1890ded8d8c428a68212eb8e5d8e6fd3b9 |
| 40733841068 | petclinic | absent | 6 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 106c8bfa528970a45130a32f9deb65dbdf0f7bc6cba40b29fca83a9b7090a4de |
| 40733841068 | petclinic | absent | 6 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 2dbd6c6487755396394a6c24497899fbb092e04aee11260a38d11b94743f4fe7 |
| 40733841068 | petclinic | absent | 6 | true | create_visit | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | create_visit | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | c44652d120b4ec39bf76ee8c5a48654d56cc8e6f1b65d0d980abf0b095d8f152 |
| 40733841068 | petclinic | absent | 6 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | d69df17ac9063067d4d79dfd1ab499bf7d07e5a3c352ff122cd28cef2de23b41 |
| 40733841068 | petclinic | absent | 6 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 3cf762b3ad4496fd89686f2355657b6dad418821679a40268b3fb9ec584dd138 |
| 40733841068 | petclinic | absent | 6 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | a610b5f5852f46734422752a33657acce54cc7864572092a12205623ec572eea |
| 40733841068 | petclinic | absent | 6 | true | list_owners | native | raw | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | list_owners | native | network_scope | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 67ebc50424d02791aa033a5d2d6a42ecde58c7a53eb7f305ef959ba25ad900a7 |
| 40733841068 | petclinic | absent | 6 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 9e50f68fa7e655f79fc467b2a0d02a8cc5604775944bfe0e87382db6f48ec7e5 |
| 40733841068 | petclinic | absent | 6 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 5ba70e9f58568b89f4a196a2931d77b688cbdb55f1f988f3906cda99a1ec25d4 |
| 40733841068 | petclinic | absent | 6 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 3e5483f64e63cfec541d751ef352c9b006690dcf3cd78db0ab930e24d486aa01 |
| 40733841068 | petclinic | absent | 6 | true | list_vets | native | raw | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | list_vets | native | network_scope | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | a71701e8dce61e12207a6bf76f5f9b371973171993b95f620ffb8ee7244f38ab |
| 40733841068 | petclinic | absent | 6 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | fd4f46b4aa5c513c458157c93b5a630802d0ebe6884b2402b10d949d4a567b82 |
| 40733841068 | petclinic | absent | 6 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 5aa5e129f52bd9434e1d7945dbfe3f44f4f2e472472c7af3cce884d3f1f9dc21 |
| 40733841068 | petclinic | absent | 6 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | c3056b92f971a0a6a51547f7763a475728651de2653ae97a9798ccab0509866f |
| 40733841068 | petclinic | absent | 6 | true | owner_details_with_visits | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | owner_details_with_visits | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 6 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 509df32a119295a9b6aed34a3b727510fc8dca2b4c6af9f048db340b82c2f1fc |
| 40733841068 | petclinic | absent | 6 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 9c794ed18cbf640221f7591126ea965b41e7ef644e1465d2b39608bd20129ccb |
| 40733841068 | petclinic | absent | 7 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | e7b08d3b207e4f12f9b2b7c08ca9079768a65ef3ef9ac2f82a990908a087fd1d |
| 40733841068 | petclinic | absent | 7 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | fb9a1c48c568f1f8559cd687c2be9e4ee867876c95cabd4a46adc2d9e6739a4c |
| 40733841068 | petclinic | absent | 7 | true | create_visit | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | create_visit | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | d018f184355bd5bb019646accd20ff1564b11e396bbb818e7bebc1b38dd0c13f |
| 40733841068 | petclinic | absent | 7 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | c4d92e1ae7d37d37b92621c9201e2304abe7f859a29dd84a435f6ac23e1c54d2 |
| 40733841068 | petclinic | absent | 7 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 2ed617196d8e4af5ed2c94c60927eae72f40648db248a96d985339f27aa7de5d |
| 40733841068 | petclinic | absent | 7 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | fac0916b498121f82edb02506d7699138c2a1adee1e079b3f0db0615d519dcb2 |
| 40733841068 | petclinic | absent | 7 | true | list_owners | native | raw | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | list_owners | native | network_scope | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 932fb53085be3d116f6a3cc460c41b55d75dd61ad3c3d91f80170c6452fdf369 |
| 40733841068 | petclinic | absent | 7 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 7803d54c714437ae7efb8863b70ec6eaa4feda2b54d7db41e1fb053ff85f86ce |
| 40733841068 | petclinic | absent | 7 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 57303cf1269af39cb40c908b4e409086b1646d509b752616e26dfa67ac52d9fd |
| 40733841068 | petclinic | absent | 7 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c6a10c8eae11f1ddb02c9c8c4dc42fa471bd4567074ac4f6de91aa65a046170e |
| 40733841068 | petclinic | absent | 7 | true | list_vets | native | raw | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | list_vets | native | network_scope | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 7982732ab7ef3234edd8c23494a2e6525bce458fe2a7f52d5f2d5260c4d57ea1 |
| 40733841068 | petclinic | absent | 7 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 30b0c655877f810eb430f1cd289d9816846fefdea2c3af111f050bb1e6613742 |
| 40733841068 | petclinic | absent | 7 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 6c322a80ef9f652ca35d4a29c50513a7403225e2ffaee8c016fd7ab7f8f179bf |
| 40733841068 | petclinic | absent | 7 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | e518eb4ea85103f892d21fb1a0fd253cc6855a2132c345e778bd1709b4b9fb87 |
| 40733841068 | petclinic | absent | 7 | true | owner_details_with_visits | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | owner_details_with_visits | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 7 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 4c7a23ad7ec048570df89504498f813e52797ec208128f09502799477e68609a |
| 40733841068 | petclinic | absent | 7 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | bf1814848e2e03f19db5c646c3e67fe2363e583876a76eeedb8372788c060546 |
| 40733841068 | petclinic | absent | 8 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | f0da85a9c3b832a4abe787c99cddce54a95abfd509de836ed0ab7e9fe67e1106 |
| 40733841068 | petclinic | absent | 8 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 5628e7349c04825a6fed2f3402da68613111829fd60134040f9d3d82e04d941e |
| 40733841068 | petclinic | absent | 8 | true | create_visit | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | create_visit | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | aa8f961bacf1888e182dc3773172c41540c3aad59b40b7dc345f31e138ca129e |
| 40733841068 | petclinic | absent | 8 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 87a8fcf9670dcbdcf370e29ead86cabb5c3ddcc4dbc848c9eb085279a99682f9 |
| 40733841068 | petclinic | absent | 8 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e4c640a6d0a8a2b5beb8c4af2009377fdc9d52af5d4aaf478bcef397ffb97c83 |
| 40733841068 | petclinic | absent | 8 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 6ebeca42bb8e4607d9448b8f94d9c7ad65dc38a20673ba3378278a3d3a7f9a79 |
| 40733841068 | petclinic | absent | 8 | true | list_owners | native | raw | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | list_owners | native | network_scope | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 4ecd2ceb633c5e4082f069ea595a62de0182e99eea4626320c9402d3865bd9e0 |
| 40733841068 | petclinic | absent | 8 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 3075da2b79596aa7c1d24122a19a984a2a825013f8f05c5997296924b20836fd |
| 40733841068 | petclinic | absent | 8 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | f74471fe066e0bc6734dcb3ffa499c3d00de452815bc9556be98d2ae781111f4 |
| 40733841068 | petclinic | absent | 8 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | f05a5b6e12a78b9ac7e6f948d99213f84bad423eca19e19b6443848fe1fd2674 |
| 40733841068 | petclinic | absent | 8 | true | list_vets | native | raw | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | list_vets | native | network_scope | false | unknown | 0, 1 | 2400 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 8d6aa814a647db06add572f14fe39f279a28bab1b40aece54da6731d42c0c6f0 |
| 40733841068 | petclinic | absent | 8 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | edbb3da7f5fd4f020aa0c5f89e46b0eed251e3af246113f208e1d5ab0c6b3096 |
| 40733841068 | petclinic | absent | 8 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 81ee262d6cee771607bc1178c5ccc93ed0880c4973b8ca92abea64f7e5ff5283 |
| 40733841068 | petclinic | absent | 8 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 760d61fa92e2e8b0c6f4c353d2b58138838db86f2e21eb360e397c84f7a00d59 |
| 40733841068 | petclinic | absent | 8 | true | owner_details_with_visits | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | owner_details_with_visits | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40733841068 | petclinic | absent | 8 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | c5615b90ecaaa5658f5b29ea418bc08f3170749e9cfaa1100b2b912011124fdd |
| 40733841068 | petclinic | absent | 8 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | c04ce893887f7faa9a5b58641be7b5761ed638d0e6920d3c7411bbf73ab8b7f5 |
| 40733846961 | petclinic | partial | 6 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 61b341e4379dfae4f3b1336f905a2b57bfe2c0f7338e0bd05a176040f0e74f24 |
| 40733846961 | petclinic | partial | 6 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | f0e04112c5a4ff933575cff381638cc06e6bb21561ef7d757c4b1e8ce6e59cf0 |
| 40733846961 | petclinic | partial | 6 | true | create_visit | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 6 | true | create_visit | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 6 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 195586279bbafb52d95a430ef48c6feafaf9ce85d6b6dfbeb834f3befa9a95b0 |
| 40733846961 | petclinic | partial | 6 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 64ea12aef399e8397e292f96f82d2afc2fee9efa2b60d2a258ce3f5fa95f0a22 |
| 40733846961 | petclinic | partial | 6 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 69dd9337a3ca428b34698797c8d3d9cca30ca48683f6802edfa03bd0a7671f4b |
| 40733846961 | petclinic | partial | 6 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c8d33b73b1ea40e40508890f8b1989197dea2912c5f3365cca9642cce86a50ff |
| 40733846961 | petclinic | partial | 6 | true | list_owners | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | b10d1fc4029bf1247644bb9d241f4551ccf2eb4f9926419d70fc981f869bc8b3 |
| 40733846961 | petclinic | partial | 6 | true | list_owners | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 0e8999cff6fd944cf6f9221df756c93db6c07752b74476376ed9ad0516ccd6d6 |
| 40733846961 | petclinic | partial | 6 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 715b9261b39c738b5d84d033701714c950204b5e9bc62b4e1fe944499bf3daf5 |
| 40733846961 | petclinic | partial | 6 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 6f81fc81fb28a7ca49e3e5062b74c9c8c48ee1316b16e3c5b587c63e5970f44a |
| 40733846961 | petclinic | partial | 6 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 2183e6156bb46cae6bfddc41f9709b7ad0bf8a9fabaf1b14c01c83b6bcc986a4 |
| 40733846961 | petclinic | partial | 6 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | b98af58a777ff06358f346e6ff1ff5da3c2fbe63763974f74444eb5c06b6e18c |
| 40733846961 | petclinic | partial | 6 | true | list_vets | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 8cfa954c252136caad56c78eac5da3031ea6b07ae0aed88679c09f76202e0832 |
| 40733846961 | petclinic | partial | 6 | true | list_vets | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 1c7228a3f91389bb4d81044a6141a7dd5f6e076d1232d4dddc9477987abb2e77 |
| 40733846961 | petclinic | partial | 6 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 1dd0544eda7d1ba0c70941624b6fe2df65799a52be1290ada437c23ccb00e6bb |
| 40733846961 | petclinic | partial | 6 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 8e60e24fcf81efc02623ffdc590a7b0dc849b643b82dc8ec3345e41725edd7ea |
| 40733846961 | petclinic | partial | 6 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 8466503ea147e037f7a222ceb676bf63acc1f0c5cfd5f27154d95a5af80b9eed |
| 40733846961 | petclinic | partial | 6 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | f60f26883c7901d9487ce7b60f27dfcfc4ddbf0dca44e5533dd37183ba233da1 |
| 40733846961 | petclinic | partial | 6 | true | owner_details_with_visits | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 6 | true | owner_details_with_visits | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 6 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 6439f5e14acac8e10f1c157884b7e72506adc67c5530388424df549e20849d0f |
| 40733846961 | petclinic | partial | 6 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 23668ee6e0f14a0cab1c873976bc575a54949be6ca49a1a5041a48a4d2a70128 |
| 40733846961 | petclinic | partial | 7 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 3a33183c8f0f8b3c43b0ae097d9426d05d2e5d51c3eadab267d69a050777e476 |
| 40733846961 | petclinic | partial | 7 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 1f2ddda292e01ccc7e289d115c67b8afc321702e4ea8a1d156d7f0f67c7ba885 |
| 40733846961 | petclinic | partial | 7 | true | create_visit | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 7 | true | create_visit | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 7 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 9c311a7f7a290e49b77a6fbff5d52709a1a7940e837fbde2c04161a8c66fe93d |
| 40733846961 | petclinic | partial | 7 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 27acc2f155fb9e6ab3dc0873a40991be8a34c29ce383b8ae70e543f66bf6e32b |
| 40733846961 | petclinic | partial | 7 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c5654ba08087fb3dde74262857dacc97f8c3ca83b446c4c955800e8cefedf3ad |
| 40733846961 | petclinic | partial | 7 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 9c89e785bd063dd9d9806119e8950bf3ba14a8d54f810c7fe07ba461cf3127fa |
| 40733846961 | petclinic | partial | 7 | true | list_owners | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 3fe8fb05fc89a77adcd65e98484f5cf638c00d7659fed18393eb71059fb25544 |
| 40733846961 | petclinic | partial | 7 | true | list_owners | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | cd2c754cb3e5adeda3255377737b5a29aff39e6bbfdedd73abb5351e9a6ffdb0 |
| 40733846961 | petclinic | partial | 7 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 9ff4361ba67c6395db499ca21b52d22b82ec2c94fcd0b97aaedd638ce3e777e4 |
| 40733846961 | petclinic | partial | 7 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e362139a72dcfbf613e849f3f0493574daa8be85075d81b801d0225557eafef3 |
| 40733846961 | petclinic | partial | 7 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 663da053c8f4b4f1e57a013952fe48326814014c505b44b02d85421413144403 |
| 40733846961 | petclinic | partial | 7 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 6f391681fb8880839c398a416a6fdcb2b2dd61b331f6e436712cc63983092fc1 |
| 40733846961 | petclinic | partial | 7 | true | list_vets | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | fa8aea879b201cb440adb83e93d132508a8f357fc787da73de3710fedf43d186 |
| 40733846961 | petclinic | partial | 7 | true | list_vets | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 72e81d53e1b0ad1cf2e4c6067388855f070d82c6d7425163705cb8a908236ea6 |
| 40733846961 | petclinic | partial | 7 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 97ebb88e56e5eec8187c3c7e85de0e9e9a7f49aa861a39009a4ffcb4b1b325fa |
| 40733846961 | petclinic | partial | 7 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c781980d013b46033b01231efed360b008aacd68f6e06b7dc8c7c0f3d3504185 |
| 40733846961 | petclinic | partial | 7 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | f9f6f868b5131c108416000d122a6d0dcfa3e0ef3350ab46c0e196061ab4f04a |
| 40733846961 | petclinic | partial | 7 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 13de617fb4b66feebd7a278369d3c31f9a2536d5107ee86ffc8e55e7b44a2d6c |
| 40733846961 | petclinic | partial | 7 | true | owner_details_with_visits | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 7 | true | owner_details_with_visits | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 7 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | cfde9b2e2f24c858888d5026defd8f047594ed0de2a10259cfa08852798c8e65 |
| 40733846961 | petclinic | partial | 7 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | c05f1be8ae0aec4a87b691ba7e0e0113c83e1159ce0fdc1c19d7c8721475636a |
| 40733846961 | petclinic | partial | 8 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 9f8e0ada9800e9cb2f9f46cf6f3ba572892411c156216d869e1367278b22c645 |
| 40733846961 | petclinic | partial | 8 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | f7f279852dcb039a2c18bf44b590c0bcb27383ad59a766309accca325ed825f1 |
| 40733846961 | petclinic | partial | 8 | true | create_visit | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 8 | true | create_visit | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 8 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 442a897c89bab184c120666f7782bcf2fe71d10a9dba3be52e0a878077af1de2 |
| 40733846961 | petclinic | partial | 8 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 91e1d1fe26e3078e0eaf9e225371fd3d8bf3d825a0dbfa404e73588e38c5687e |
| 40733846961 | petclinic | partial | 8 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 8b60cd8a995aea563e5e213ef552ef149173e23e72ea62a46b456c8efc6b0f39 |
| 40733846961 | petclinic | partial | 8 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | f8339e4df43195a0e1068cdb07a47ca5474ad587c23ee27c0782230f60991836 |
| 40733846961 | petclinic | partial | 8 | true | list_owners | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 8a88598ec4361c20b97bbe0c9cd72855fec566e2c29ebe03ca259170dff82cb4 |
| 40733846961 | petclinic | partial | 8 | true | list_owners | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | f6edd1bbd5dfb780424300c4230020330f2fc46a2020415b21d0e965e07696fe |
| 40733846961 | petclinic | partial | 8 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 45a4b5409389b7599f86a572cecf212149afba565d295d31b98b2ac527fd4390 |
| 40733846961 | petclinic | partial | 8 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 0e72de03d180163c42607552264ee24214d249ef68ef347059dd910292084bb2 |
| 40733846961 | petclinic | partial | 8 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | a43d73ab7a86034261267214bb0f4aff12deffc7b4c23ad70ba94dee66bfda2d |
| 40733846961 | petclinic | partial | 8 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 8b97268409a6e2c3fefad44ae487edc8cf035165dd32b71131356261d6b5bd65 |
| 40733846961 | petclinic | partial | 8 | true | list_vets | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | efd284c4656171b1f1c29b4ac691623547a29f5fa77436c813f7b854b94e145c |
| 40733846961 | petclinic | partial | 8 | true | list_vets | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 93746c187d22e6f113e4bde89d4f74ecaa47b283583a15db0b09d9e6a790729a |
| 40733846961 | petclinic | partial | 8 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 8992e2b453aa5a9fcadb1b087f8586dc15644059c2e1d81997df2a7b1f81fac4 |
| 40733846961 | petclinic | partial | 8 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 713bf26015a1832f48a8ae6e1be7d9d08e1b10821516342747593496502c7a8a |
| 40733846961 | petclinic | partial | 8 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 874c4bfe45771bc7500ce33395eb59dcda3c1b3e2f5c71665b4b20f8d52202f2 |
| 40733846961 | petclinic | partial | 8 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | d7ecdf1d6d0134fe6606bbc328d954af9f6815e0246ae454ed69f0f7a9a02c47 |
| 40733846961 | petclinic | partial | 8 | true | owner_details_with_visits | native | raw | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 8 | true | owner_details_with_visits | native | network_scope | false | unknown | 0, 1 | 2100 | 300 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40733846961 | petclinic | partial | 8 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 66e1c6e7116b03f3bd4a12f44b5ca0ea10425043f85d73a0c51cdd07fd1df253 |
| 40733846961 | petclinic | partial | 8 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 3d0740f3c40b69028701f3138f5410186d7f31e50b601a08220da178bd1ce60d |
| 40733852492 | petclinic | full | 7 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | fc7ae0144a692ae30e9bc1e32c91ae0bfa10f0daa3302961a3589b68fb56e003 |
| 40733852492 | petclinic | full | 7 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | dc083be2ffd866919fa14469a271408abd3b9b33c750b5fe5f459b89bd654b2e |
| 40733852492 | petclinic | full | 7 | true | create_visit | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 5fa307b34aba14893e9338ee21d67065919b39b501ad834c7e6597ed39e3b3fe |
| 40733852492 | petclinic | full | 7 | true | create_visit | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | d921e96c15fae57768987f3a957860b353ac5e94f7683e58701fca79ef970b1b |
| 40733852492 | petclinic | full | 7 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 52c29845c857c2b46f24db93be9b46ac94dec30cab1859c395985a8542e8f270 |
| 40733852492 | petclinic | full | 7 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 71b2eece58892359cc3e90f4f68ab772d02cc4902fc8c2d17ce7c5de38fe99c7 |
| 40733852492 | petclinic | full | 7 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | bba81e8495c5c89c1f542db5819ddc2da6de976e037ec843101a0e55f376dae2 |
| 40733852492 | petclinic | full | 7 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 31eb23966e8e7d09d28bd98446732436c4bfb983f3ed7048e9e5665b9b68b454 |
| 40733852492 | petclinic | full | 7 | true | list_owners | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | dafa32bc3281fd1aac6b3b5bb537a7b04b02c7ecb0bf15888bca854388897ddc |
| 40733852492 | petclinic | full | 7 | true | list_owners | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 0fcc9fa6bc058c0bbf94e5d891333c0a3db8012ff9f26fa9e0b5ed7b8434ae3c |
| 40733852492 | petclinic | full | 7 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | d2681a9958c239e1a808696bf82e57004a40c00d70557b174af53c724c77841a |
| 40733852492 | petclinic | full | 7 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 669b4403a48d39f869955640bb9229ba08a571b7955cc0417c484f62a36ca499 |
| 40733852492 | petclinic | full | 7 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 259d4702c248fd5f27461521a21547234b84ab6a9cb0545955ed3b8a82532174 |
| 40733852492 | petclinic | full | 7 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c889573db114d0e71df189ad4d745aa3b312de9cb6f0b21009a7849c9402b033 |
| 40733852492 | petclinic | full | 7 | true | list_vets | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 596bc8ced5c99dc0513e06c817ec8667b29f805bde830a3eb3cf3c809ca15143 |
| 40733852492 | petclinic | full | 7 | true | list_vets | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 7500b198f755730f977d3c8d6ef9e95d891ead689223927fcf6d1c49e5c2dd41 |
| 40733852492 | petclinic | full | 7 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | f2b70467d696bd6ca7385805676798eb0bd478ee2d7eccabdac522826c3cb5f6 |
| 40733852492 | petclinic | full | 7 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 83b66e22dd8a969ea70ea5ff2d6dba2b87344be52c1daa4786726d94b55351dc |
| 40733852492 | petclinic | full | 7 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 4c8d9672ad0cf8ae5e403c16a586f4e8918fff4217e52a1ffbddec6ba06b89db |
| 40733852492 | petclinic | full | 7 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 9c844515c151248d2cef776a8f8c8b7c63fa8fa78d8a6fc663a6068721e2263c |
| 40733852492 | petclinic | full | 7 | true | owner_details_with_visits | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 86364b8379d902b10664558ba738444ca1edd169d12535415833b5ca627e66f1 |
| 40733852492 | petclinic | full | 7 | true | owner_details_with_visits | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 46af8b30c6499f3c69ceebd53e1ef25eabf1a457b398cc8f0f57479eaa9efe7c |
| 40733852492 | petclinic | full | 7 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | b3e47fb89c623364f210da997e91944a5cdb55bacb26eba2c77cf40156010573 |
| 40733852492 | petclinic | full | 7 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | da918bff1b4641e646f30aeb05a1f6054dacbb21f95c9f8aa7f14dadf7163257 |
| 40733858113 | petclinic | full | 8 | true | create_visit | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 542b8bdc97914bb438289c0132fcf59268862bd77a5c325a0a0941fae8c11091 |
| 40733858113 | petclinic | full | 8 | true | create_visit | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | d2ed9c1f9956ae60b8c857aee0d825137e103018a345fd4ebacc4c995641f64a |
| 40733858113 | petclinic | full | 8 | true | create_visit | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 2f1f1af5d3edf95868da37af21c2b56311b96c145a80978255b937ad36ec911f |
| 40733858113 | petclinic | full | 8 | true | create_visit | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 19debea935b5639c487b331bb71873399cf2bad269f90282785bd675b2a2abe0 |
| 40733858113 | petclinic | full | 8 | true | create_visit | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 128052bfb2c28aa34e5d161a8089651fdb5569f0d630d37299cc519d03d5182a |
| 40733858113 | petclinic | full | 8 | true | create_visit | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | fefa9daea508b96fb61fbecb76b1d22ee433a9042321e73f1cb91409a73c5d96 |
| 40733858113 | petclinic | full | 8 | true | list_owners | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | fced95f11715071caa29ba86956dd4a3eb45db882da7a7d9296c6fcac513d08a |
| 40733858113 | petclinic | full | 8 | true | list_owners | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e4a6b7592a76183126c59ed2d150b195dd20ea2c4a7b9107c7e59093ffd9372d |
| 40733858113 | petclinic | full | 8 | true | list_owners | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 27d2d010d354d6f3d4a71afb0d95bb132f56563d46a4f9a29dac6d2f6bd9f7aa |
| 40733858113 | petclinic | full | 8 | true | list_owners | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 1c7bd5470230ce39997eefec66aa52e226e970bdbae0f5f36a5e8970482b2a1d |
| 40733858113 | petclinic | full | 8 | true | list_owners | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e7319ea9a119db620004d2568824c318062ad07483dd590b8c6b6c21b7e06af2 |
| 40733858113 | petclinic | full | 8 | true | list_owners | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 5fd60704e930653731055c4568c5ef493f59fdd3e0ce6a2ee7659b4283923006 |
| 40733858113 | petclinic | full | 8 | true | list_vets | ebpf | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 59695a6909f7c832de68d8616531549cde5a1a7b280f17b87d9556e68029f69a |
| 40733858113 | petclinic | full | 8 | true | list_vets | ebpf | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e141ddc2572e77abc048631f0cb21412204fd316a54ce2a4244aa7e52f9941a9 |
| 40733858113 | petclinic | full | 8 | true | list_vets | native | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | ccf183c8fe16b724520e8e895fd273184fd8191103980e5499dfe813b54a6156 |
| 40733858113 | petclinic | full | 8 | true | list_vets | native | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | b1d0498e55fe3361911637ecb8b23fa7aca77b9c81ef15fae89249dbd5248c48 |
| 40733858113 | petclinic | full | 8 | true | list_vets | combined | raw | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 68d9373d1b5dfb060de96bb43dc23e9323c24aab91fe013fdf35d8329c04117b |
| 40733858113 | petclinic | full | 8 | true | list_vets | combined | network_scope | true | 1.0 | 1.0, 1.0 | 2400 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 75bf87f568bfb36cd2e1d36fc86d3124c26a359ca639dfe35d63130c0831f555 |
| 40733858113 | petclinic | full | 8 | true | owner_details_with_visits | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 7e72f2c9a3e395f4c4a89e2bc91e4287de57d1c3c4d825683428b5923d2dc6bf |
| 40733858113 | petclinic | full | 8 | true | owner_details_with_visits | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 80af4df4d0973224d77cde1a1f56835d89968ff6d164577fd259c2cff228d8bb |
| 40733858113 | petclinic | full | 8 | true | owner_details_with_visits | native | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | ca0cc18f18b1fca15b2593195fdabe1fc208d7529e464af4627cbb75df9963fe |
| 40733858113 | petclinic | full | 8 | true | owner_details_with_visits | native | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | 4e41404faa5924bad4e0e56efe423ef8d466c5ca1f322ca8be0fbc8691d556b4 |
| 40733858113 | petclinic | full | 8 | true | owner_details_with_visits | combined | raw | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | a0025b7636be3c09c2e9e8b8de03220e7edbb86d3d2c4f22a0e5612bfa3645ab |
| 40733858113 | petclinic | full | 8 | true | owner_details_with_visits | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2100 | 300 | 0 | 0.875, 0.875 | 0.0 | unknown | c7aca0096e519a600623ff28ad1a1390224708dd0a78fff5697dde8a1ed7a4e2 |
| 40754529169 | otel_demo | full | 6 | false | add_to_cart | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | add_to_cart | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | add_to_cart | native | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | add_to_cart | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | add_to_cart | combined | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | add_to_cart | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | browse_product | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | browse_product | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | browse_product | native | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | browse_product | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | browse_product | combined | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | browse_product | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | checkout | ebpf | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | checkout | ebpf | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | checkout | native | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | checkout | native | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | checkout | combined | raw | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40754529169 | otel_demo | full | 6 | false | checkout | combined | network_scope | false | unknown | unknown | 0 | 0 | 0 | unknown | unknown | campaign_incomplete_or_integrity_failed | unknown |
| 40786403012 | otel_demo | full | 6 | true | add_to_cart | ebpf | raw | false | unknown | 0, 1 | 2688 | 512 | 0 | 0.84, 0.84 | unknown | required_graph_evidence_unavailable | unknown |
| 40786403012 | otel_demo | full | 6 | true | add_to_cart | ebpf | network_scope | false | unknown | 0, 1 | 2688 | 512 | 0 | 0.84, 0.84 | unknown | required_graph_evidence_unavailable | unknown |
| 40786403012 | otel_demo | full | 6 | true | add_to_cart | native | raw | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | 56226f4c4ae606119804ba1bf0810924b41992a565f80ae17dd6ca4d5e088bfe |
| 40786403012 | otel_demo | full | 6 | true | add_to_cart | native | network_scope | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | b782ff330355604e41b2738ab9ddf020ebc77f64d53dc22049c8bf0306b862e3 |
| 40786403012 | otel_demo | full | 6 | true | add_to_cart | combined | raw | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | df51621219227ad0f5aeaa027775b038a3348228adb5a8d56ede5cb2ec688633 |
| 40786403012 | otel_demo | full | 6 | true | add_to_cart | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | 81e62c26fbfb16307fc288a085f43e03f71a89ce2208205ef8a8b09bd804ad68 |
| 40786403012 | otel_demo | full | 6 | true | browse_product | ebpf | raw | false | unknown | 0, 1 | 2688 | 512 | 0 | 0.84, 0.84 | unknown | required_graph_evidence_unavailable | unknown |
| 40786403012 | otel_demo | full | 6 | true | browse_product | ebpf | network_scope | false | unknown | 0, 1 | 2688 | 512 | 0 | 0.84, 0.84 | unknown | required_graph_evidence_unavailable | unknown |
| 40786403012 | otel_demo | full | 6 | true | browse_product | native | raw | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | 8c5f1beab423599827d94d5a64404ecf1f6159890de159c705cf4da7d5792dc9 |
| 40786403012 | otel_demo | full | 6 | true | browse_product | native | network_scope | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | 1261923523f58808b5e2b50f5e074f83a5968110baba7b5ed970998a1878a18d |
| 40786403012 | otel_demo | full | 6 | true | browse_product | combined | raw | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | 428e10b6fe39ba6321a130f9d161e8cb41fde6c37118923f9f249682c47fef98 |
| 40786403012 | otel_demo | full | 6 | true | browse_product | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2688 | 512 | 0 | 0.84, 0.84 | 0.03500000000000003 | unknown | 09370cb1d14f76d65c8afbfee283ee0ca1b7512b2f9c1f87d8c39843a991a9d3 |
| 40786403012 | otel_demo | full | 6 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2635 | 565 | 0 | 0.8234375, 0.8234375 | unknown | required_graph_evidence_unavailable | unknown |
| 40786403012 | otel_demo | full | 6 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2635 | 565 | 0 | 0.8234375, 0.8234375 | unknown | required_graph_evidence_unavailable | unknown |
| 40786403012 | otel_demo | full | 6 | true | checkout | native | raw | true | 0.875 | 0.875, 0.875 | 2635 | 565 | 0 | 0.8234375, 0.8234375 | 0.051562499999999956 | unknown | 7900e6eea86ffa712c829b085f67768cbadcad96f4e6d1cb75dbe333c578fd59 |
| 40786403012 | otel_demo | full | 6 | true | checkout | native | network_scope | true | 0.875 | 0.875, 0.875 | 2635 | 565 | 0 | 0.8234375, 0.8234375 | 0.051562499999999956 | unknown | 8ecb3b5879effab5d5214dd5c1bc04b12247d34418867f982ced3e95b079f993 |
| 40786403012 | otel_demo | full | 6 | true | checkout | combined | raw | true | 0.875 | 0.875, 0.875 | 2635 | 565 | 0 | 0.8234375, 0.8234375 | 0.051562499999999956 | unknown | bb7cb124d9bcae0e1ca224c436108e9edf9228c9f6df3ac21cd7b9cb5e509120 |
| 40786403012 | otel_demo | full | 6 | true | checkout | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2635 | 565 | 0 | 0.8234375, 0.8234375 | 0.051562499999999956 | unknown | eee0371b5699df180a78f0b0541f478a2ad41638c6f787f769a2f1bfd70fdd6a |
| 40803782214 | otel_demo | absent | 6 | true | add_to_cart | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2701 | 499 | 0 | 0.8440625, 0.8440625 | 0.03093749999999995 | unknown | edd9c55c770645a1d88f346b45e164cf1c38261a8961e81e9fef7757faee26aa |
| 40803782214 | otel_demo | absent | 6 | true | add_to_cart | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2701 | 499 | 0 | 0.8440625, 0.8440625 | 0.03093749999999995 | unknown | 0eeba96333a374d2a121a78f7702e1b70789d481e6c400465188240f00e3d828 |
| 40803782214 | otel_demo | absent | 6 | true | add_to_cart | native | raw | false | unknown | 0, 1 | 2701 | 499 | 0 | 0.8440625, 0.8440625 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 6 | true | add_to_cart | native | network_scope | false | unknown | 0, 1 | 2701 | 499 | 0 | 0.8440625, 0.8440625 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 6 | true | add_to_cart | combined | raw | true | 0.875 | 0.875, 0.875 | 2701 | 499 | 0 | 0.8440625, 0.8440625 | 0.03093749999999995 | unknown | 84dcfaf00675da18c1ceae7c4278bee050e53b737c0b6a9d577606375e56e2ef |
| 40803782214 | otel_demo | absent | 6 | true | add_to_cart | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2701 | 499 | 0 | 0.8440625, 0.8440625 | 0.03093749999999995 | unknown | d0bcfcb9171d079f731a9beb92e3a10a9c952d6dc634f3df9896bb469196e3a7 |
| 40803782214 | otel_demo | absent | 6 | true | browse_product | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2714 | 486 | 0 | 0.848125, 0.848125 | 0.026874999999999982 | unknown | f56ff2bed0e5b1d629f242b0a583e1bbb842e6c9a623c62ce29de87da5ad4dce |
| 40803782214 | otel_demo | absent | 6 | true | browse_product | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2714 | 486 | 0 | 0.848125, 0.848125 | 0.026874999999999982 | unknown | b796d0e5be06f22759554b727f2b50983445c4467d70e1deeb7f40da1eeea4aa |
| 40803782214 | otel_demo | absent | 6 | true | browse_product | native | raw | false | unknown | 0, 1 | 2714 | 486 | 0 | 0.848125, 0.848125 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 6 | true | browse_product | native | network_scope | false | unknown | 0, 1 | 2714 | 486 | 0 | 0.848125, 0.848125 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 6 | true | browse_product | combined | raw | true | 0.875 | 0.875, 0.875 | 2714 | 486 | 0 | 0.848125, 0.848125 | 0.026874999999999982 | unknown | 089f40172fa69e906b9d17eb0f2f77f2c04929fdae93de2f101fa8912f6ec5d2 |
| 40803782214 | otel_demo | absent | 6 | true | browse_product | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2714 | 486 | 0 | 0.848125, 0.848125 | 0.026874999999999982 | unknown | 686ffe63ef4fb2d591a2cb96ce619e0e0517d71785fad81aa84c29384ba3730f |
| 40803782214 | otel_demo | absent | 6 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2585 | 615 | 0 | 0.8078125, 0.8078125 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 6 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2585 | 615 | 0 | 0.8078125, 0.8078125 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 6 | true | checkout | native | raw | false | unknown | 0, 1 | 2585 | 615 | 0 | 0.8078125, 0.8078125 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 6 | true | checkout | native | network_scope | false | unknown | 0, 1 | 2585 | 615 | 0 | 0.8078125, 0.8078125 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 6 | true | checkout | combined | raw | false | unknown | 0, 1 | 2585 | 615 | 0 | 0.8078125, 0.8078125 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 6 | true | checkout | combined | network_scope | false | unknown | 0, 1 | 2585 | 615 | 0 | 0.8078125, 0.8078125 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 7 | true | add_to_cart | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 66e65550814a6f9ffc5dd01d108199b403e1979c8a13492a05d85b74261a3f58 |
| 40803782214 | otel_demo | absent | 7 | true | add_to_cart | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 8462b8ff69130af4d256ff83ccf1c1bc8038182be2dc3d589681896d34649182 |
| 40803782214 | otel_demo | absent | 7 | true | add_to_cart | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 7 | true | add_to_cart | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 7 | true | add_to_cart | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | a81cf454b0489a675fbda0026d50bf0db7490c09498c9e40bd10daf83b20529a |
| 40803782214 | otel_demo | absent | 7 | true | add_to_cart | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 2a2f35a2d43da1abc772274eec07c83f7ac45d240099d26c44cb463cff8eb3de |
| 40803782214 | otel_demo | absent | 7 | true | browse_product | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 2289f5ec4a9352888686821174ab558cd7b8bcfb77f18dd50da595746bfd4344 |
| 40803782214 | otel_demo | absent | 7 | true | browse_product | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 9281ddcf4a78e54f1275fe44e2dee5a5c10e2d9f01b3104ed11081a00706be30 |
| 40803782214 | otel_demo | absent | 7 | true | browse_product | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 7 | true | browse_product | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 7 | true | browse_product | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 69b38849abdc4c0fb3e27ca9d90f624711e898581f232d6d7c13e75148f89b55 |
| 40803782214 | otel_demo | absent | 7 | true | browse_product | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 7a73a140c4d6c85666c6581748b9dcd791d07064c28e8f6eaab460ebacaa29a3 |
| 40803782214 | otel_demo | absent | 7 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 7 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 7 | true | checkout | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 7 | true | checkout | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 7 | true | checkout | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 7 | true | checkout | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 8 | true | add_to_cart | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 175320dba4bff5bdc3a937204d2563d36ba837e61e4ab2d12d989b7e49fbb952 |
| 40803782214 | otel_demo | absent | 8 | true | add_to_cart | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 6c01d49d9f143e44b249641cb73831917c8cb798833b2a91bad5c97f6f6e7c4d |
| 40803782214 | otel_demo | absent | 8 | true | add_to_cart | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 8 | true | add_to_cart | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 8 | true | add_to_cart | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 9e9b21fd9faa8e21638b6300ef76b05b19efd05760c8bdf62a4a541150721a59 |
| 40803782214 | otel_demo | absent | 8 | true | add_to_cart | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 2eb9ecbf8fde8f321496296cd08fecf451821473752615ce1854b54c226314b8 |
| 40803782214 | otel_demo | absent | 8 | true | browse_product | ebpf | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | d985208e54fb784fbdf027b02ca98b0f706307e48a7ca637fc5ec387d73d99a5 |
| 40803782214 | otel_demo | absent | 8 | true | browse_product | ebpf | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 92caebe68aa904c1a5eb5231f68e2b2e8361e694b427cbdee4f5c3cf7397d831 |
| 40803782214 | otel_demo | absent | 8 | true | browse_product | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 8 | true | browse_product | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 8 | true | browse_product | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | d0590a246ebc56c91407f4c476ccf7c3479d17ddd0d970cd13bf0a7b56adb3ec |
| 40803782214 | otel_demo | absent | 8 | true | browse_product | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 0512cf852cfd7b6e6aacadf29cb3277cbdc7b5541366a13e2ba51255fc3cd3e0 |
| 40803782214 | otel_demo | absent | 8 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 8 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 8 | true | checkout | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 8 | true | checkout | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40803782214 | otel_demo | absent | 8 | true | checkout | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803782214 | otel_demo | absent | 8 | true | checkout | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | add_to_cart | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | add_to_cart | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | add_to_cart | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | add_to_cart | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | add_to_cart | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | add_to_cart | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | browse_product | ebpf | raw | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | browse_product | ebpf | network_scope | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | browse_product | native | raw | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | browse_product | native | network_scope | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | browse_product | combined | raw | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | browse_product | combined | network_scope | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2797 | 403 | 0 | 0.8740625, 0.8740625 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2797 | 403 | 0 | 0.8740625, 0.8740625 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | checkout | native | raw | false | unknown | 0, 1 | 2797 | 403 | 0 | 0.8740625, 0.8740625 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | checkout | native | network_scope | false | unknown | 0, 1 | 2797 | 403 | 0 | 0.8740625, 0.8740625 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | checkout | combined | raw | false | unknown | 0, 1 | 2797 | 403 | 0 | 0.8740625, 0.8740625 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 6 | true | checkout | combined | network_scope | false | unknown | 0, 1 | 2797 | 403 | 0 | 0.8740625, 0.8740625 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | add_to_cart | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | add_to_cart | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | add_to_cart | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | add_to_cart | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | add_to_cart | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | add_to_cart | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | browse_product | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | browse_product | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | browse_product | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | browse_product | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | browse_product | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | browse_product | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | checkout | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | checkout | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | checkout | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 7 | true | checkout | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | add_to_cart | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | add_to_cart | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | add_to_cart | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | add_to_cart | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | add_to_cart | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | add_to_cart | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | browse_product | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | browse_product | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | browse_product | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | browse_product | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | browse_product | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | browse_product | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | checkout | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | checkout | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | checkout | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803790289 | otel_demo | partial | 8 | true | checkout | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803798632 | otel_demo | full | 7 | true | add_to_cart | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803798632 | otel_demo | full | 7 | true | add_to_cart | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803798632 | otel_demo | full | 7 | true | add_to_cart | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 7d5a48aaf222db564844b524810f6d59e9cff9dea00a93d0df7dbeb94e788fec |
| 40803798632 | otel_demo | full | 7 | true | add_to_cart | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | f4376b244c928c0fd185fbf12c559d0fd58e1b5e25119741240f6aaea2f8a0d1 |
| 40803798632 | otel_demo | full | 7 | true | add_to_cart | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 0f8cb66965b44c0df641dbcd92ffe0de73dd711cee854c5a84bc9bd30d732a2e |
| 40803798632 | otel_demo | full | 7 | true | add_to_cart | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 3cf1f42c85b5a9b44a63edb4e0d41471314a4407b403bf58c65c928e58c821c1 |
| 40803798632 | otel_demo | full | 7 | true | browse_product | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803798632 | otel_demo | full | 7 | true | browse_product | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803798632 | otel_demo | full | 7 | true | browse_product | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | fa408740ea190fcb9b00b6fff175d52d56dd0dbfc4b2ae60681b77f36d41cd2d |
| 40803798632 | otel_demo | full | 7 | true | browse_product | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 6b7b7741bf60b215afcc2b07db3db0b4da4536bfa3aa5df3364a26e678e9ed0e |
| 40803798632 | otel_demo | full | 7 | true | browse_product | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | ec8959e02cd238d0582fd464283e2efc1b6b2bfada32652ed247619e0e4f46e0 |
| 40803798632 | otel_demo | full | 7 | true | browse_product | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | c7a04fb40eb67244fdcf0902af057114166e5fbfb6eed11de716a29e33cbbdc2 |
| 40803798632 | otel_demo | full | 7 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803798632 | otel_demo | full | 7 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803798632 | otel_demo | full | 7 | true | checkout | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | b13074bd0b24f29077132cfae7983429d63d54ebd0cd9d8cfcf4b382e19fb839 |
| 40803798632 | otel_demo | full | 7 | true | checkout | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 3868227975e5ca8feb4209fbedfdb539ada6a6e4ba140b7ba72c83cfc2800c49 |
| 40803798632 | otel_demo | full | 7 | true | checkout | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | ec0eb12bd5d4c7236dd0bcc5efb63c6352c9cfc05640eb85c5b3c9a4c51faf0c |
| 40803798632 | otel_demo | full | 7 | true | checkout | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 40739f656558844f4ea62c27b945517f6cb575ac36f757e1246ebbaf805ed6dc |
| 40803806299 | otel_demo | full | 8 | true | add_to_cart | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803806299 | otel_demo | full | 8 | true | add_to_cart | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803806299 | otel_demo | full | 8 | true | add_to_cart | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | f45f2ac5f3095f3963737793636aef9c342bcb3fc73f6020afed58d24fa92b9d |
| 40803806299 | otel_demo | full | 8 | true | add_to_cart | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | f199a626f2d0ef11cfa4f9ba519839357e014044775721af190dd2d2f53fec08 |
| 40803806299 | otel_demo | full | 8 | true | add_to_cart | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | a91c23026eda16ee38d89aeb30f9d1efda58868ea48aad66a97bfa1475081d60 |
| 40803806299 | otel_demo | full | 8 | true | add_to_cart | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 5d2d1728b986b7de6ede60ea709e77e32a4cfbbf2131bcbd7acfcdc553d206c7 |
| 40803806299 | otel_demo | full | 8 | true | browse_product | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803806299 | otel_demo | full | 8 | true | browse_product | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803806299 | otel_demo | full | 8 | true | browse_product | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | badac05bb8c11b44c219776c486e80720a55fca98cc19f5c358b484b29acfcfc |
| 40803806299 | otel_demo | full | 8 | true | browse_product | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 99e21737c4c70cda30228fd95845cc4cb6107af741b2a8ecba1f3474f4faf843 |
| 40803806299 | otel_demo | full | 8 | true | browse_product | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | e7ff4ef00d3db94db1fa1ba9af962c0591dbc9f68d111d6bb47b9593ac4bb273 |
| 40803806299 | otel_demo | full | 8 | true | browse_product | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 2d2efe39aae7da3d9ffbe06584b1c98e63cf742388060ff18f479380c8182636 |
| 40803806299 | otel_demo | full | 8 | true | checkout | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803806299 | otel_demo | full | 8 | true | checkout | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40803806299 | otel_demo | full | 8 | true | checkout | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 508fca8ba3e096a837ee9cc1ee238cd75c79d83b972f0b54f4eb51c2e890c9e3 |
| 40803806299 | otel_demo | full | 8 | true | checkout | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 394565fcd9cfe0f40ed30d2b545453f588a90a8dba0d55cb028e9ce9ccc2c822 |
| 40803806299 | otel_demo | full | 8 | true | checkout | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | ccf860f6eed26acc3ffc6dc7e953a22bcf6edd3cf40eed66e110a3d8265d5c3e |
| 40803806299 | otel_demo | full | 8 | true | checkout | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 8af5433b3b47cd7f137748f9f29db8ee727ce85f3f90fd74d49021ed0080f422 |
| 40821198727 | deathstarbench | full | 6 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821198727 | deathstarbench | full | 6 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821198727 | deathstarbench | full | 6 | true | compose_post | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | aae5360dcc1e799f42335b389890b4bcbc197aa5558378751eda165320c910db |
| 40821198727 | deathstarbench | full | 6 | true | compose_post | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 39d03ee006c1ab97f44e8c8095171e15645458b88ee6a370c0399eeb163f9e4c |
| 40821198727 | deathstarbench | full | 6 | true | compose_post | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | a09100a8773ec2a5d48bbe9dc577675e0ae6ce54dcaa1dbaf8e29ee19b00a91b |
| 40821198727 | deathstarbench | full | 6 | true | compose_post | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | e80357a35a78989e3af2aad7bc2bf5b99fadf6778b2b2a7bad29ec22a31659b8 |
| 40821198727 | deathstarbench | full | 6 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821198727 | deathstarbench | full | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821198727 | deathstarbench | full | 6 | true | read_home_timeline | native | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | e3c54023318bd825f440e5c528bd744d7b5c9607f71f12b06cfd3fbe018fc5d6 |
| 40821198727 | deathstarbench | full | 6 | true | read_home_timeline | native | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 96871825054a2c106f99d18129164e0b6765af858e32947026acbacc47327860 |
| 40821198727 | deathstarbench | full | 6 | true | read_home_timeline | combined | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c363b8bc36199801dcf388a1c6bc517e1ce7e18e049f9238a621476dd852e539 |
| 40821198727 | deathstarbench | full | 6 | true | read_home_timeline | combined | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 88216cccb7487ec0afe84d6337db2b44f2b7cf2c462964b78a2a7648b316ee21 |
| 40821198727 | deathstarbench | full | 6 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821198727 | deathstarbench | full | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821198727 | deathstarbench | full | 6 | true | read_user_timeline | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 022d7a8f15e407059adbb630454b6097f1a3691495a793897fd5bd903e643be2 |
| 40821198727 | deathstarbench | full | 6 | true | read_user_timeline | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 92926d2da1ca672f77648bd0c5608fcc2860fcba0f9102b55cb2fe7b6941e5bb |
| 40821198727 | deathstarbench | full | 6 | true | read_user_timeline | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 5297f3915cd13d5ceaaa561e05af2e3139364c6a7170063bf051422e29ce0632 |
| 40821198727 | deathstarbench | full | 6 | true | read_user_timeline | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 51071aed244f0b134e24fa05fe8fc26dc4281fb5dabc55efb5ae80c6b4e5872b |
| 40821214009 | deathstarbench | absent | 6 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | compose_post | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | compose_post | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | compose_post | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | compose_post | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_home_timeline | native | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_home_timeline | native | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_home_timeline | combined | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_home_timeline | combined | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_user_timeline | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_user_timeline | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_user_timeline | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 6 | true | read_user_timeline | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | compose_post | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | compose_post | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | compose_post | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | compose_post | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_home_timeline | native | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_home_timeline | native | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_home_timeline | combined | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_home_timeline | combined | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_user_timeline | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_user_timeline | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_user_timeline | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 7 | true | read_user_timeline | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | compose_post | native | raw | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | compose_post | native | network_scope | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | compose_post | combined | raw | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | compose_post | combined | network_scope | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_home_timeline | native | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_home_timeline | native | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_home_timeline | combined | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_home_timeline | combined | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_user_timeline | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_user_timeline | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | no_frozen_source_observations | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_user_timeline | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821214009 | deathstarbench | absent | 8 | true | read_user_timeline | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | compose_post | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | compose_post | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | compose_post | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | compose_post | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_home_timeline | native | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 66174693e045442896fce08c07beaef926d6f315f381972f71d8690b4c749df8 |
| 40821232082 | deathstarbench | partial | 6 | true | read_home_timeline | native | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 4210136b781ca212ebd525dcaf122a2d3d4436a6b3dcfc978dbeb3f4030d01d2 |
| 40821232082 | deathstarbench | partial | 6 | true | read_home_timeline | combined | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 2a616d2bb137db1ccd00814bb4a2228e59ab00afa6d513b8b7dd5835673f4b98 |
| 40821232082 | deathstarbench | partial | 6 | true | read_home_timeline | combined | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 81a1efd5b1c2735eba332828798626a4598beaea3586735dd0d4068740466291 |
| 40821232082 | deathstarbench | partial | 6 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_user_timeline | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_user_timeline | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_user_timeline | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 6 | true | read_user_timeline | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | compose_post | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | compose_post | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | compose_post | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | compose_post | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_home_timeline | native | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | f0f31ad9dd9984430740d469edb9a9b257ddbbd7a1384a55892cb2244535b72f |
| 40821232082 | deathstarbench | partial | 7 | true | read_home_timeline | native | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | c6564098657a8a7bd4aedc9a1fafaac80ef4d9963cbf64696e4ec5a294220eb8 |
| 40821232082 | deathstarbench | partial | 7 | true | read_home_timeline | combined | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 0157c552379399da958d5efa2b0c0e87118488336b1599be9b7d0c0c93fd98e3 |
| 40821232082 | deathstarbench | partial | 7 | true | read_home_timeline | combined | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 60c27ae42881efd807ae1065e677003d87b9af063c936bd22d6933b1a1eacfee |
| 40821232082 | deathstarbench | partial | 7 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_user_timeline | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_user_timeline | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_user_timeline | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 7 | true | read_user_timeline | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | compose_post | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | compose_post | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | compose_post | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | compose_post | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_home_timeline | native | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | a7a790145c74e76fcafa9a895129ea197ed28540193bd79b721451163c1273b9 |
| 40821232082 | deathstarbench | partial | 8 | true | read_home_timeline | native | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 7f5f6eeea507e0160efcc4681f0df8a9d16985c59fc22014fc085f38c5aa1046 |
| 40821232082 | deathstarbench | partial | 8 | true | read_home_timeline | combined | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 99faa0fe9ab26d1949339f63224bc7e260239190d53eb10aa420f153d5a19ba9 |
| 40821232082 | deathstarbench | partial | 8 | true | read_home_timeline | combined | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | ab42631fb5a3e971cfd70918378088ad337fb004fd63bd1e58af0dbb108be414 |
| 40821232082 | deathstarbench | partial | 8 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_user_timeline | native | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_user_timeline | native | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_user_timeline | combined | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821232082 | deathstarbench | partial | 8 | true | read_user_timeline | combined | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821255620 | deathstarbench | full | 7 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821255620 | deathstarbench | full | 7 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821255620 | deathstarbench | full | 7 | true | compose_post | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | b60c138edb20b9e79813fb9e1423f38f76684cc8dcaa075607c5e129a5f03e6c |
| 40821255620 | deathstarbench | full | 7 | true | compose_post | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 92f16c56c027230817330b9bd2660486081c8e306f52bc087191caa18a79649b |
| 40821255620 | deathstarbench | full | 7 | true | compose_post | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 183960a17ac3213284306bffd1eae8a733c747ff9bdafa100a8efce82f26a8c1 |
| 40821255620 | deathstarbench | full | 7 | true | compose_post | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | e49d183b6c7614a2c5ab020e9e63c33e37febddb8661a5754da2b85335b0ea0c |
| 40821255620 | deathstarbench | full | 7 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821255620 | deathstarbench | full | 7 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821255620 | deathstarbench | full | 7 | true | read_home_timeline | native | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 76a37ce43763ad162df73e5f8d1016ef8a8050c90e37342d99be5c95adca8107 |
| 40821255620 | deathstarbench | full | 7 | true | read_home_timeline | native | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 741f9336077f8b86034ad24dc50d4cb6da520a677ed5ead464f15b9477a526ea |
| 40821255620 | deathstarbench | full | 7 | true | read_home_timeline | combined | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 542c943495d752ed0dd3c969f30d50742e7d3c011513e5bfee1f41e811d8c21f |
| 40821255620 | deathstarbench | full | 7 | true | read_home_timeline | combined | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 1e0d7fa8c06e168ff81b4c1f954ad496cde3bb5f48712992614007ac29ad47d6 |
| 40821255620 | deathstarbench | full | 7 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821255620 | deathstarbench | full | 7 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821255620 | deathstarbench | full | 7 | true | read_user_timeline | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | c3c36b9ab7b4722627ebe58047078cd8069a1081fa7a4adaad52ef808159e09e |
| 40821255620 | deathstarbench | full | 7 | true | read_user_timeline | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | f58a8df16ecb7b1a2eaf79c06a4b44dc032a77843b8d392b42b358e112b6cbd6 |
| 40821255620 | deathstarbench | full | 7 | true | read_user_timeline | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 669a75aab91e8d8fe91c002df43f2d317c9cc0e4642cc82cf7ab53aa35137766 |
| 40821255620 | deathstarbench | full | 7 | true | read_user_timeline | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 1f57f5c0938ee343e0864f200e301e1e92279150cfb63fd6ef0b936a5083317e |
| 40821277823 | deathstarbench | full | 8 | true | compose_post | ebpf | raw | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821277823 | deathstarbench | full | 8 | true | compose_post | ebpf | network_scope | false | unknown | 0, 1 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821277823 | deathstarbench | full | 8 | true | compose_post | native | raw | true | 0.875 | 0.875, 0.875 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | 0.00031250000000004885 | unknown | 5f6cd90ae14c94bfc552dcf25d602849491571ebc6218a039d3ffe1cbb104c0b |
| 40821277823 | deathstarbench | full | 8 | true | compose_post | native | network_scope | true | 0.875 | 0.875, 0.875 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | 0.00031250000000004885 | unknown | fe5218750592dcae0245d4400a89ed756b78e63ecda7c026251723007a779347 |
| 40821277823 | deathstarbench | full | 8 | true | compose_post | combined | raw | true | 0.875 | 0.875, 0.875 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | 0.00031250000000004885 | unknown | 1d1c81c9d42ef02e53b709118130dea796e7fd6d9da8c777106e5e055be71f0c |
| 40821277823 | deathstarbench | full | 8 | true | compose_post | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2799 | 401 | 0 | 0.8746875, 0.8746875 | 0.00031250000000004885 | unknown | 4f7e66396f50124ffcfdc58b61d338b8e2e6349007832faff9d2c68c517bd63e |
| 40821277823 | deathstarbench | full | 8 | true | read_home_timeline | ebpf | raw | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821277823 | deathstarbench | full | 8 | true | read_home_timeline | ebpf | network_scope | false | unknown | 0, 1 | 3200 | 0 | 0 | 1.0, 1.0 | unknown | required_graph_evidence_unavailable | unknown |
| 40821277823 | deathstarbench | full | 8 | true | read_home_timeline | native | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | f4797db3461f51cf2c687b7864c3448d4691ff4e4d8ce275f4c84e41ea82ba02 |
| 40821277823 | deathstarbench | full | 8 | true | read_home_timeline | native | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 48ef58ca394bd2019f10a1d5d825860e5c8df68ff11089410634ff2ab8231f9a |
| 40821277823 | deathstarbench | full | 8 | true | read_home_timeline | combined | raw | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 2cf73a3e714d61b81a22e580d1e799876ecb62da4e029daa8182511e2cbf3cb5 |
| 40821277823 | deathstarbench | full | 8 | true | read_home_timeline | combined | network_scope | true | 1.0 | 1.0, 1.0 | 3200 | 0 | 0 | 1.0, 1.0 | 0.0 | unknown | 862c1b9bab50cd2044b3e8b9f9a18ed69c9a4696b2081494c66d4bcf894297e6 |
| 40821277823 | deathstarbench | full | 8 | true | read_user_timeline | ebpf | raw | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821277823 | deathstarbench | full | 8 | true | read_user_timeline | ebpf | network_scope | false | unknown | 0, 1 | 2800 | 400 | 0 | 0.875, 0.875 | unknown | required_graph_evidence_unavailable | unknown |
| 40821277823 | deathstarbench | full | 8 | true | read_user_timeline | native | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 8bb40d849152789bf065ef6787cdbe4a609d3611099fda6b609ba7c1e7e82643 |
| 40821277823 | deathstarbench | full | 8 | true | read_user_timeline | native | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 1d6dd6953ddeecca953b1f880b9c1091117afc97f73d51f28d4adf87a8b7de94 |
| 40821277823 | deathstarbench | full | 8 | true | read_user_timeline | combined | raw | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | 6184d03a3f952c1e306ae27cbb2e0ca3139a99252adce4a6407c5cb8bd3be7d5 |
| 40821277823 | deathstarbench | full | 8 | true | read_user_timeline | combined | network_scope | true | 0.875 | 0.875, 0.875 | 2800 | 400 | 0 | 0.875, 0.875 | 0.0 | unknown | f401a8879a74637bd2015f21d242dbc172cf7cbef234084d3ad01e8d85b3c23b |

## Database up/down evidence

| Run | System | Mode | Seed | Phase | Operation | Success | Failure | Unknown | Total |
|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40718674400 | petclinic | full | 6 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 6 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 7 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733841068 | petclinic | absent | 8 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 6 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 7 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733846961 | petclinic | partial | 8 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733852492 | petclinic | full | 7 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_up | create_visit | 5 | 0 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_up | list_owners | 5 | 0 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_up | list_vets | 5 | 0 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_up | owner_details_with_visits | 5 | 0 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_down | create_visit | 0 | 5 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_down | list_owners | 0 | 5 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_down | list_vets | 5 | 0 | 0 | 5 |
| 40733858113 | petclinic | full | 8 | db_down | owner_details_with_visits | 0 | 5 | 0 | 5 |
| 40754529169 | otel_demo | full | 6 | db_up | add_to_cart | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | db_up | browse_product | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | db_up | checkout | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | db_down | add_to_cart | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | db_down | browse_product | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | db_down | checkout | 0 | 0 | 0 | 0 |
| 40786403012 | otel_demo | full | 6 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40786403012 | otel_demo | full | 6 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40786403012 | otel_demo | full | 6 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40786403012 | otel_demo | full | 6 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40786403012 | otel_demo | full | 6 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40786403012 | otel_demo | full | 6 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803782214 | otel_demo | absent | 6 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803782214 | otel_demo | absent | 6 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803782214 | otel_demo | absent | 6 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803782214 | otel_demo | absent | 6 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803782214 | otel_demo | absent | 6 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803782214 | otel_demo | absent | 6 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803782214 | otel_demo | absent | 7 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803782214 | otel_demo | absent | 7 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803782214 | otel_demo | absent | 7 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803782214 | otel_demo | absent | 7 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803782214 | otel_demo | absent | 7 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803782214 | otel_demo | absent | 7 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803782214 | otel_demo | absent | 8 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803782214 | otel_demo | absent | 8 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803782214 | otel_demo | absent | 8 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803782214 | otel_demo | absent | 8 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803782214 | otel_demo | absent | 8 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803782214 | otel_demo | absent | 8 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803790289 | otel_demo | partial | 6 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803790289 | otel_demo | partial | 6 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803790289 | otel_demo | partial | 6 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803790289 | otel_demo | partial | 6 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803790289 | otel_demo | partial | 6 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803790289 | otel_demo | partial | 6 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803790289 | otel_demo | partial | 7 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803790289 | otel_demo | partial | 7 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803790289 | otel_demo | partial | 7 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803790289 | otel_demo | partial | 7 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803790289 | otel_demo | partial | 7 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803790289 | otel_demo | partial | 7 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803790289 | otel_demo | partial | 8 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803790289 | otel_demo | partial | 8 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803790289 | otel_demo | partial | 8 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803790289 | otel_demo | partial | 8 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803790289 | otel_demo | partial | 8 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803790289 | otel_demo | partial | 8 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803798632 | otel_demo | full | 7 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803798632 | otel_demo | full | 7 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803798632 | otel_demo | full | 7 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803798632 | otel_demo | full | 7 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803798632 | otel_demo | full | 7 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803798632 | otel_demo | full | 7 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40803806299 | otel_demo | full | 8 | db_up | add_to_cart | 7 | 0 | 0 | 7 |
| 40803806299 | otel_demo | full | 8 | db_up | browse_product | 7 | 0 | 0 | 7 |
| 40803806299 | otel_demo | full | 8 | db_up | checkout | 6 | 0 | 0 | 6 |
| 40803806299 | otel_demo | full | 8 | db_down | add_to_cart | 0 | 7 | 0 | 7 |
| 40803806299 | otel_demo | full | 8 | db_down | browse_product | 0 | 7 | 0 | 7 |
| 40803806299 | otel_demo | full | 8 | db_down | checkout | 0 | 6 | 0 | 6 |
| 40821198727 | deathstarbench | full | 6 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821198727 | deathstarbench | full | 6 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821198727 | deathstarbench | full | 6 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821198727 | deathstarbench | full | 6 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821198727 | deathstarbench | full | 6 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821198727 | deathstarbench | full | 6 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821214009 | deathstarbench | absent | 6 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 6 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 6 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821214009 | deathstarbench | absent | 6 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 6 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 6 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821214009 | deathstarbench | absent | 7 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 7 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 7 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821214009 | deathstarbench | absent | 7 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 7 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 7 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821214009 | deathstarbench | absent | 8 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 8 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 8 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821214009 | deathstarbench | absent | 8 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 8 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821214009 | deathstarbench | absent | 8 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821232082 | deathstarbench | partial | 6 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 6 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 6 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821232082 | deathstarbench | partial | 6 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 6 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 6 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821232082 | deathstarbench | partial | 7 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 7 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 7 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821232082 | deathstarbench | partial | 7 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 7 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 7 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821232082 | deathstarbench | partial | 8 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 8 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 8 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821232082 | deathstarbench | partial | 8 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 8 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821232082 | deathstarbench | partial | 8 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821255620 | deathstarbench | full | 7 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821255620 | deathstarbench | full | 7 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821255620 | deathstarbench | full | 7 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821255620 | deathstarbench | full | 7 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821255620 | deathstarbench | full | 7 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821255620 | deathstarbench | full | 7 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821277823 | deathstarbench | full | 8 | db_up | compose_post | 7 | 0 | 0 | 7 |
| 40821277823 | deathstarbench | full | 8 | db_up | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821277823 | deathstarbench | full | 8 | db_up | read_user_timeline | 6 | 0 | 0 | 6 |
| 40821277823 | deathstarbench | full | 8 | db_down | compose_post | 7 | 0 | 0 | 7 |
| 40821277823 | deathstarbench | full | 8 | db_down | read_home_timeline | 7 | 0 | 0 | 7 |
| 40821277823 | deathstarbench | full | 8 | db_down | read_user_timeline | 6 | 0 | 0 | 6 |

Stored forecast impact (healthy state 11 versus database down):

| Run | System | Mode | Seed | Operation | Source | Variant | Graph available | Healthy 11 | DB down | Impact | Comparison | Accuracy benefit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | create_visit | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | create_visit | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_owners | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_owners | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 6 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 6 | create_visit | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | create_visit | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 6 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 6 | list_owners | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_owners | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 6 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_vets | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_vets | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 6 | owner_details_with_visits | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | owner_details_with_visits | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 6 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 7 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 7 | create_visit | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | create_visit | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 7 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 7 | list_owners | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_owners | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 7 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_vets | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_vets | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 7 | owner_details_with_visits | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | owner_details_with_visits | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 7 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 8 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 8 | create_visit | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | create_visit | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 8 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 8 | list_owners | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_owners | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 8 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_vets | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_vets | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733841068 | petclinic | absent | 8 | owner_details_with_visits | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | owner_details_with_visits | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733841068 | petclinic | absent | 8 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 6 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 6 | create_visit | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | create_visit | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 6 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 6 | list_owners | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_owners | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 6 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 6 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_vets | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_vets | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 6 | owner_details_with_visits | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | owner_details_with_visits | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 6 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 7 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 7 | create_visit | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | create_visit | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 7 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 7 | list_owners | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_owners | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 7 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 7 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_vets | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_vets | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 7 | owner_details_with_visits | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | owner_details_with_visits | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 7 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 8 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 8 | create_visit | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | create_visit | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 8 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 8 | list_owners | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_owners | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 8 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 8 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_vets | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_vets | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733846961 | petclinic | partial | 8 | owner_details_with_visits | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | owner_details_with_visits | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733846961 | petclinic | partial | 8 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | create_visit | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | create_visit | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | list_owners | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_owners | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_vets | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_vets | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | owner_details_with_visits | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | owner_details_with_visits | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733852492 | petclinic | full | 7 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733852492 | petclinic | full | 7 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | create_visit | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | create_visit | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | create_visit | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | create_visit | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | create_visit | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | create_visit | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | list_owners | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_owners | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | list_owners | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_owners | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | list_owners | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_owners | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | list_vets | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_vets | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_vets | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_vets | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_vets | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | list_vets | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | owner_details_with_visits | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | owner_details_with_visits | ebpf | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | owner_details_with_visits | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | owner_details_with_visits | native | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40733858113 | petclinic | full | 8 | owner_details_with_visits | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40733858113 | petclinic | full | 8 | owner_details_with_visits | combined | network_scope | true | 1 | 0 | 1 | healthy_state_11_minus_database_down | false |
| 40754529169 | otel_demo | full | 6 | add_to_cart | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | add_to_cart | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | add_to_cart | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | add_to_cart | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | add_to_cart | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | add_to_cart | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | browse_product | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | browse_product | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | browse_product | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | browse_product | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | browse_product | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | browse_product | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | checkout | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | checkout | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | checkout | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40754529169 | otel_demo | full | 6 | checkout | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | add_to_cart | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | add_to_cart | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | add_to_cart | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | add_to_cart | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | add_to_cart | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | add_to_cart | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | browse_product | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | browse_product | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | browse_product | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | browse_product | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | browse_product | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | browse_product | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | checkout | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | checkout | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | checkout | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40786403012 | otel_demo | full | 6 | checkout | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | add_to_cart | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | add_to_cart | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | add_to_cart | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | add_to_cart | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | add_to_cart | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | add_to_cart | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | browse_product | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | browse_product | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | browse_product | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | browse_product | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | browse_product | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | browse_product | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | checkout | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | checkout | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | checkout | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 6 | checkout | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | add_to_cart | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | add_to_cart | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | add_to_cart | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | add_to_cart | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | add_to_cart | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | add_to_cart | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | browse_product | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | browse_product | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | browse_product | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | browse_product | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | browse_product | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | browse_product | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | checkout | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | checkout | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | checkout | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 7 | checkout | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | add_to_cart | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | add_to_cart | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | add_to_cart | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | add_to_cart | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | add_to_cart | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | add_to_cart | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | browse_product | ebpf | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | browse_product | ebpf | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | browse_product | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | browse_product | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | browse_product | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | browse_product | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | checkout | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | checkout | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | checkout | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803782214 | otel_demo | absent | 8 | checkout | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | add_to_cart | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | add_to_cart | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | add_to_cart | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | add_to_cart | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | add_to_cart | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | add_to_cart | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | browse_product | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | browse_product | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | browse_product | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | browse_product | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | browse_product | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | browse_product | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | checkout | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | checkout | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | checkout | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 6 | checkout | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | add_to_cart | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | add_to_cart | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | add_to_cart | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | add_to_cart | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | add_to_cart | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | add_to_cart | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | browse_product | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | browse_product | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | browse_product | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | browse_product | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | browse_product | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | browse_product | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | checkout | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | checkout | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | checkout | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 7 | checkout | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | add_to_cart | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | add_to_cart | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | add_to_cart | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | add_to_cart | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | add_to_cart | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | add_to_cart | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | browse_product | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | browse_product | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | browse_product | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | browse_product | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | browse_product | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | browse_product | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | checkout | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | checkout | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | checkout | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803790289 | otel_demo | partial | 8 | checkout | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | add_to_cart | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | add_to_cart | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | add_to_cart | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | add_to_cart | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | add_to_cart | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | add_to_cart | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | browse_product | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | browse_product | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | browse_product | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | browse_product | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | browse_product | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | browse_product | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | checkout | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | checkout | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | checkout | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803798632 | otel_demo | full | 7 | checkout | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | add_to_cart | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | add_to_cart | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | add_to_cart | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | add_to_cart | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | add_to_cart | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | add_to_cart | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | browse_product | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | browse_product | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | browse_product | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | browse_product | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | browse_product | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | browse_product | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | checkout | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | checkout | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | checkout | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | checkout | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | checkout | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40803806299 | otel_demo | full | 8 | checkout | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | compose_post | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | compose_post | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | compose_post | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | compose_post | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_home_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_home_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_home_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_home_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_user_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_user_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_user_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821198727 | deathstarbench | full | 6 | read_user_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | compose_post | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | compose_post | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | compose_post | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | compose_post | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_home_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_home_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_home_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_home_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_user_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_user_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_user_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 6 | read_user_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | compose_post | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | compose_post | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | compose_post | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | compose_post | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_home_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_home_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_home_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_home_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_user_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_user_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_user_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 7 | read_user_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | compose_post | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | compose_post | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | compose_post | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | compose_post | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_home_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_home_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_home_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_home_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_user_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_user_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_user_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821214009 | deathstarbench | absent | 8 | read_user_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | compose_post | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | compose_post | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | compose_post | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | compose_post | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_home_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_home_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_home_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_home_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_user_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_user_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_user_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 6 | read_user_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | compose_post | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | compose_post | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | compose_post | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | compose_post | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_home_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_home_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_home_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_home_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_user_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_user_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_user_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 7 | read_user_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | compose_post | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | compose_post | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | compose_post | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | compose_post | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_home_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_home_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_home_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_home_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_user_timeline | native | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_user_timeline | native | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_user_timeline | combined | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821232082 | deathstarbench | partial | 8 | read_user_timeline | combined | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | compose_post | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | compose_post | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | compose_post | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | compose_post | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_home_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_home_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_home_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_home_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_user_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_user_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_user_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821255620 | deathstarbench | full | 7 | read_user_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | compose_post | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | compose_post | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | compose_post | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | compose_post | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | compose_post | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | compose_post | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_home_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_home_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_home_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_home_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_home_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_home_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_user_timeline | ebpf | raw | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_user_timeline | ebpf | network_scope | false | unknown | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_user_timeline | native | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_user_timeline | native | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_user_timeline | combined | raw | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |
| 40821277823 | deathstarbench | full | 8 | read_user_timeline | combined | network_scope | true | 1 | unknown | unknown | unknown_unless_both_predictions_available | false |

## Strong manual baselines

| Run | System | Mode | Seed | Operation | Available | Prediction | By state | DB baseline available | DB-down prediction | DB basis/reason | Baseline basis |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40718674400 | petclinic | full | 6 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40718674400 | petclinic | full | 6 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40718674400 | petclinic | full | 6 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 6 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 6 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 6 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 6 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 7 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 7 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 7 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 7 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 8 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 8 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 8 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733841068 | petclinic | absent | 8 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 6 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 6 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 6 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 6 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 7 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 7 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 7 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 7 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 8 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 8 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 8 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733846961 | petclinic | partial | 8 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733852492 | petclinic | full | 7 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733852492 | petclinic | full | 7 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733852492 | petclinic | full | 7 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733852492 | petclinic | full | 7 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733858113 | petclinic | full | 8 | create_visit | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733858113 | petclinic | full | 8 | list_owners | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733858113 | petclinic | full | 8 | list_vets | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40733858113 | petclinic | full | 8 | owner_details_with_visits | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40754529169 | otel_demo | full | 6 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40754529169 | otel_demo | full | 6 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40754529169 | otel_demo | full | 6 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40786403012 | otel_demo | full | 6 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40786403012 | otel_demo | full | 6 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40786403012 | otel_demo | full | 6 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 6 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 6 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 6 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 7 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 7 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 7 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 8 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 8 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803782214 | otel_demo | absent | 8 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 6 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 6 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 6 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 7 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 7 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 7 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 8 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 8 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803790289 | otel_demo | partial | 8 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803798632 | otel_demo | full | 7 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803798632 | otel_demo | full | 7 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803798632 | otel_demo | full | 7 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803806299 | otel_demo | full | 8 | add_to_cart | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803806299 | otel_demo | full | 8 | browse_product | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40803806299 | otel_demo | full | 8 | checkout | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821198727 | deathstarbench | full | 6 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821198727 | deathstarbench | full | 6 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821198727 | deathstarbench | full | 6 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 6 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 6 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 6 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 7 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 7 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 7 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 8 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 8 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821214009 | deathstarbench | absent | 8 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 6 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 6 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 6 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 7 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 7 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 7 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 8 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 8 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821232082 | deathstarbench | partial | 8 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821255620 | deathstarbench | full | 7 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821255620 | deathstarbench | full | 7 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821255620 | deathstarbench | full | 7 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821277823 | deathstarbench | full | 8 | compose_post | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | true | 0.0 | declared unconditional selected database requirement | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821277823 | deathstarbench | full | 8 | read_home_timeline | true | 1.0 | 00=1.0; 01=1.0; 10=1.0; 11=1.0 | true | 1.0 | selected database is off-path under the declared complete contract | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |
| 40821277823 | deathstarbench | full | 8 | read_user_timeline | true | 0.875 | 00=0.0; 01=1.0; 10=1.0; 11=1.0 | false | unknown | declared_database_requirement_is_conditional | declared source contract plus two-slot controlled inventory; A OR B; no HTTP outcomes or recovered graph |

## Frozen class evaluation

| Run | System | Mode | Seed | Source | Variant | Total | Known | Unknown | Coverage | ARI labeled known | ARI known subset | Unknowns merged | Labels after prediction/reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | native | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40718674400 | petclinic | full | 6 | combined | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733841068 | petclinic | absent | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733841068 | petclinic | absent | 6 | ebpf | downstream | 600 | 589 | 11 | 0.9816666666666667 | 589 | 0.488856746038883 | false | true |
| 40733841068 | petclinic | absent | 6 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40733841068 | petclinic | absent | 6 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40733841068 | petclinic | absent | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733841068 | petclinic | absent | 6 | combined | downstream | 600 | 589 | 11 | 0.9816666666666667 | 589 | 0.488856746038883 | false | true |
| 40733841068 | petclinic | absent | 7 | ebpf | base | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733841068 | petclinic | absent | 7 | ebpf | downstream | 600 | 554 | 46 | 0.9233333333333333 | 554 | 0.5043547054452483 | false | true |
| 40733841068 | petclinic | absent | 7 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40733841068 | petclinic | absent | 7 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40733841068 | petclinic | absent | 7 | combined | base | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733841068 | petclinic | absent | 7 | combined | downstream | 600 | 554 | 46 | 0.9233333333333333 | 554 | 0.5043547054452483 | false | true |
| 40733841068 | petclinic | absent | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733841068 | petclinic | absent | 8 | ebpf | downstream | 600 | 580 | 20 | 0.9666666666666667 | 580 | 0.515856230665414 | false | true |
| 40733841068 | petclinic | absent | 8 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40733841068 | petclinic | absent | 8 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40733841068 | petclinic | absent | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733841068 | petclinic | absent | 8 | combined | downstream | 600 | 580 | 20 | 0.9666666666666667 | 580 | 0.515856230665414 | false | true |
| 40733846961 | petclinic | partial | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 6 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 6 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 6 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 6 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 7 | ebpf | base | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 7 | ebpf | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 7 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 7 | native | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 7 | combined | base | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 7 | combined | downstream | 600 | 598 | 2 | 0.9966666666666667 | 598 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 8 | ebpf | base | 600 | 598 | 2 | 0.9966666666666667 | 598 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 8 | ebpf | downstream | 600 | 598 | 2 | 0.9966666666666667 | 598 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 8 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 8 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 8 | combined | base | 600 | 598 | 2 | 0.9966666666666667 | 598 | 1.0 | false | true |
| 40733846961 | petclinic | partial | 8 | combined | downstream | 600 | 598 | 2 | 0.9966666666666667 | 598 | 1.0 | false | true |
| 40733852492 | petclinic | full | 7 | ebpf | base | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733852492 | petclinic | full | 7 | ebpf | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733852492 | petclinic | full | 7 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733852492 | petclinic | full | 7 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 0.9933520891269727 | false | true |
| 40733852492 | petclinic | full | 7 | combined | base | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40733852492 | petclinic | full | 7 | combined | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 0.9955681538570289 | false | true |
| 40733858113 | petclinic | full | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733858113 | petclinic | full | 8 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733858113 | petclinic | full | 8 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733858113 | petclinic | full | 8 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733858113 | petclinic | full | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40733858113 | petclinic | full | 8 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40754529169 | otel_demo | full | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unknown | unknown | classes-v4.json pending |
| 40786403012 | otel_demo | full | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40786403012 | otel_demo | full | 6 | ebpf | downstream | 600 | 251 | 349 | 0.41833333333333333 | 251 | 0.4143500727852249 | false | true |
| 40786403012 | otel_demo | full | 6 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40786403012 | otel_demo | full | 6 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40786403012 | otel_demo | full | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40786403012 | otel_demo | full | 6 | combined | downstream | 600 | 251 | 349 | 0.41833333333333333 | 251 | 0.4143500727852249 | false | true |
| 40803782214 | otel_demo | absent | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803782214 | otel_demo | absent | 6 | ebpf | downstream | 600 | 589 | 11 | 0.9816666666666667 | 589 | 0.4820019916746742 | false | true |
| 40803782214 | otel_demo | absent | 6 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40803782214 | otel_demo | absent | 6 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40803782214 | otel_demo | absent | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803782214 | otel_demo | absent | 6 | combined | downstream | 600 | 589 | 11 | 0.9816666666666667 | 589 | 0.4820019916746742 | false | true |
| 40803782214 | otel_demo | absent | 7 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803782214 | otel_demo | absent | 7 | ebpf | downstream | 600 | 587 | 13 | 0.9783333333333334 | 587 | 0.5635556776475099 | false | true |
| 40803782214 | otel_demo | absent | 7 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40803782214 | otel_demo | absent | 7 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40803782214 | otel_demo | absent | 7 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803782214 | otel_demo | absent | 7 | combined | downstream | 600 | 587 | 13 | 0.9783333333333334 | 587 | 0.5635556776475099 | false | true |
| 40803782214 | otel_demo | absent | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803782214 | otel_demo | absent | 8 | ebpf | downstream | 600 | 575 | 25 | 0.9583333333333334 | 575 | 0.5816464413302285 | false | true |
| 40803782214 | otel_demo | absent | 8 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40803782214 | otel_demo | absent | 8 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40803782214 | otel_demo | absent | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803782214 | otel_demo | absent | 8 | combined | downstream | 600 | 575 | 25 | 0.9583333333333334 | 575 | 0.5816464413302285 | false | true |
| 40803790289 | otel_demo | partial | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 6 | ebpf | downstream | 600 | 498 | 102 | 0.83 | 498 | 0.4519201589355598 | false | true |
| 40803790289 | otel_demo | partial | 6 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 6 | native | downstream | 600 | 599 | 1 | 0.9983333333333333 | 599 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 6 | combined | downstream | 600 | 498 | 102 | 0.83 | 498 | 0.4519201589355598 | false | true |
| 40803790289 | otel_demo | partial | 7 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 7 | ebpf | downstream | 600 | 492 | 108 | 0.82 | 492 | 0.48392093092483274 | false | true |
| 40803790289 | otel_demo | partial | 7 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 7 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 0.9975020746541895 | false | true |
| 40803790289 | otel_demo | partial | 7 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 7 | combined | downstream | 600 | 490 | 110 | 0.8166666666666667 | 490 | 0.48585761284464235 | false | true |
| 40803790289 | otel_demo | partial | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 8 | ebpf | downstream | 600 | 586 | 14 | 0.9766666666666667 | 586 | 0.5784461474310859 | false | true |
| 40803790289 | otel_demo | partial | 8 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 8 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803790289 | otel_demo | partial | 8 | combined | downstream | 600 | 586 | 14 | 0.9766666666666667 | 586 | 0.5784461474310859 | false | true |
| 40803798632 | otel_demo | full | 7 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803798632 | otel_demo | full | 7 | ebpf | downstream | 600 | 581 | 19 | 0.9683333333333334 | 581 | 0.5484991317322744 | false | true |
| 40803798632 | otel_demo | full | 7 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803798632 | otel_demo | full | 7 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803798632 | otel_demo | full | 7 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803798632 | otel_demo | full | 7 | combined | downstream | 600 | 581 | 19 | 0.9683333333333334 | 581 | 0.5484991317322744 | false | true |
| 40803806299 | otel_demo | full | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803806299 | otel_demo | full | 8 | ebpf | downstream | 600 | 564 | 36 | 0.94 | 564 | 0.44049469589388796 | false | true |
| 40803806299 | otel_demo | full | 8 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803806299 | otel_demo | full | 8 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803806299 | otel_demo | full | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40803806299 | otel_demo | full | 8 | combined | downstream | 600 | 564 | 36 | 0.94 | 564 | 0.44049469589388796 | false | true |
| 40821198727 | deathstarbench | full | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821198727 | deathstarbench | full | 6 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821198727 | deathstarbench | full | 6 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821198727 | deathstarbench | full | 6 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821198727 | deathstarbench | full | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821198727 | deathstarbench | full | 6 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 6 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 6 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40821214009 | deathstarbench | absent | 6 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40821214009 | deathstarbench | absent | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 6 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 7 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 7 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 7 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40821214009 | deathstarbench | absent | 7 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40821214009 | deathstarbench | absent | 7 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 7 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 8 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 8 | native | base | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40821214009 | deathstarbench | absent | 8 | native | downstream | 600 | 0 | 600 | 0.0 | 0 | unknown | false | true |
| 40821214009 | deathstarbench | absent | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821214009 | deathstarbench | absent | 8 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 6 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 6 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 6 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 6 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 6 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 6 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 7 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 7 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 7 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 7 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 7 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 7 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 8 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 8 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 8 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821232082 | deathstarbench | partial | 8 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821255620 | deathstarbench | full | 7 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821255620 | deathstarbench | full | 7 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821255620 | deathstarbench | full | 7 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821255620 | deathstarbench | full | 7 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821255620 | deathstarbench | full | 7 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821255620 | deathstarbench | full | 7 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821277823 | deathstarbench | full | 8 | ebpf | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821277823 | deathstarbench | full | 8 | ebpf | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821277823 | deathstarbench | full | 8 | native | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821277823 | deathstarbench | full | 8 | native | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821277823 | deathstarbench | full | 8 | combined | base | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |
| 40821277823 | deathstarbench | full | 8 | combined | downstream | 600 | 600 | 0 | 1.0 | 600 | 1.0 | false | true |

## Asynchronous persistence states

| Run | System | Mode | Seed | Async phase | Available | Records | Stored states | Paused absence is failure | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40718674400 | petclinic | full | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40718674400 | petclinic | full | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40718674400 | petclinic | full | 6 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 6 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 7 | normal | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 7 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 7 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 7 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 8 | normal | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 8 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 8 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733841068 | petclinic | absent | 8 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 6 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 7 | normal | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 7 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 7 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 7 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 8 | normal | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 8 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 8 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733846961 | petclinic | partial | 8 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733852492 | petclinic | full | 7 | normal | false | unknown | unknown | unknown | file_missing |
| 40733852492 | petclinic | full | 7 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733852492 | petclinic | full | 7 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733852492 | petclinic | full | 7 | recovered | false | unknown | unknown | unknown | file_missing |
| 40733858113 | petclinic | full | 8 | normal | false | unknown | unknown | unknown | file_missing |
| 40733858113 | petclinic | full | 8 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40733858113 | petclinic | full | 8 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40733858113 | petclinic | full | 8 | recovered | false | unknown | unknown | unknown | file_missing |
| 40754529169 | otel_demo | full | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40754529169 | otel_demo | full | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40754529169 | otel_demo | full | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40754529169 | otel_demo | full | 6 | recovered | false | unknown | unknown | unknown | file_missing |
| 40786403012 | otel_demo | full | 6 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40786403012 | otel_demo | full | 6 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40786403012 | otel_demo | full | 6 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40786403012 | otel_demo | full | 6 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 6 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 6 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803782214 | otel_demo | absent | 6 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 6 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 7 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 7 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803782214 | otel_demo | absent | 7 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 7 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 8 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 8 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803782214 | otel_demo | absent | 8 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803782214 | otel_demo | absent | 8 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 6 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 6 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803790289 | otel_demo | partial | 6 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 6 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 7 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 7 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803790289 | otel_demo | partial | 7 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 7 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 8 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 8 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803790289 | otel_demo | partial | 8 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803790289 | otel_demo | partial | 8 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803798632 | otel_demo | full | 7 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803798632 | otel_demo | full | 7 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803798632 | otel_demo | full | 7 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803798632 | otel_demo | full | 7 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40803806299 | otel_demo | full | 8 | normal | true | 20 | persisted_exact=20 | false | unknown |
| 40803806299 | otel_demo | full | 8 | paused_snapshot | true | 20 | pending=20 | false | unknown |
| 40803806299 | otel_demo | full | 8 | paused_after_resume | true | 20 | persisted_exact=20 | false | unknown |
| 40803806299 | otel_demo | full | 8 | recovered | true | 20 | persisted_exact=20 | false | unknown |
| 40821198727 | deathstarbench | full | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40821198727 | deathstarbench | full | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821198727 | deathstarbench | full | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821198727 | deathstarbench | full | 6 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 6 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 7 | normal | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 7 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 7 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 7 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 8 | normal | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 8 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 8 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821214009 | deathstarbench | absent | 8 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 6 | normal | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 6 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 6 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 6 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 7 | normal | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 7 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 7 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 7 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 8 | normal | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 8 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 8 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821232082 | deathstarbench | partial | 8 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821255620 | deathstarbench | full | 7 | normal | false | unknown | unknown | unknown | file_missing |
| 40821255620 | deathstarbench | full | 7 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821255620 | deathstarbench | full | 7 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821255620 | deathstarbench | full | 7 | recovered | false | unknown | unknown | unknown | file_missing |
| 40821277823 | deathstarbench | full | 8 | normal | false | unknown | unknown | unknown | file_missing |
| 40821277823 | deathstarbench | full | 8 | paused_snapshot | false | unknown | unknown | unknown | file_missing |
| 40821277823 | deathstarbench | full | 8 | paused_after_resume | false | unknown | unknown | unknown | file_missing |
| 40821277823 | deathstarbench | full | 8 | recovered | false | unknown | unknown | unknown | file_missing |

`async_paused` identifies requests issued while the consumer was paused; it does not claim completion during the pause.
The paused SQL snapshot and the separate after-resume/recovered verification remain distinct external observations.


## Cross-guest and causal evidence

| Run | System | Mode | Seed | Source | Exact parent links | Invalid IDs | Placement coverage | Header verdicts |
|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | ebpf | 6624 | 0 | known_guest_observations=487175; unattributed_guest_observations=0 | corroborated_same_planned_header=3217; unknown_missing_or_unplanned_header=3407 |
| 40718674400 | petclinic | full | 6 | native | 6 | 0 | known_guest_observations=324704; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=6 |
| 40733841068 | petclinic | absent | 6 | ebpf | 6623 | 0 | known_guest_observations=481257; unattributed_guest_observations=0 | corroborated_same_planned_header=3252; unknown_missing_or_unplanned_header=3371 |
| 40733841068 | petclinic | absent | 6 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=0 | none |
| 40733841068 | petclinic | absent | 7 | ebpf | 6382 | 0 | known_guest_observations=481482; unattributed_guest_observations=0 | corroborated_same_planned_header=3132; unknown_missing_or_unplanned_header=3250 |
| 40733841068 | petclinic | absent | 7 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=0 | none |
| 40733841068 | petclinic | absent | 8 | ebpf | 6615 | 0 | known_guest_observations=477241; unattributed_guest_observations=0 | corroborated_same_planned_header=3244; unknown_missing_or_unplanned_header=3371 |
| 40733841068 | petclinic | absent | 8 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=0 | none |
| 40733846961 | petclinic | partial | 6 | ebpf | 6618 | 0 | known_guest_observations=486702; unattributed_guest_observations=0 | corroborated_same_planned_header=3251; unknown_missing_or_unplanned_header=3367 |
| 40733846961 | petclinic | partial | 6 | native | 0 | 0 | known_guest_observations=262343; unattributed_guest_observations=0 | none |
| 40733846961 | petclinic | partial | 7 | ebpf | 6615 | 0 | known_guest_observations=483103; unattributed_guest_observations=0 | corroborated_same_planned_header=3245; unknown_missing_or_unplanned_header=3370 |
| 40733846961 | petclinic | partial | 7 | native | 0 | 0 | known_guest_observations=262342; unattributed_guest_observations=0 | none |
| 40733846961 | petclinic | partial | 8 | ebpf | 6623 | 0 | known_guest_observations=480844; unattributed_guest_observations=0 | corroborated_same_planned_header=3261; unknown_missing_or_unplanned_header=3362 |
| 40733846961 | petclinic | partial | 8 | native | 0 | 0 | known_guest_observations=262342; unattributed_guest_observations=0 | none |
| 40733852492 | petclinic | full | 7 | ebpf | 6506 | 0 | known_guest_observations=487633; unattributed_guest_observations=0 | corroborated_same_planned_header=3198; unknown_missing_or_unplanned_header=3308 |
| 40733852492 | petclinic | full | 7 | native | 122 | 0 | known_guest_observations=324704; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=122 |
| 40733858113 | petclinic | full | 8 | ebpf | 6622 | 0 | known_guest_observations=483899; unattributed_guest_observations=0 | corroborated_same_planned_header=3283; unknown_missing_or_unplanned_header=3339 |
| 40733858113 | petclinic | full | 8 | native | 6 | 0 | known_guest_observations=324704; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=6 |
| 40786403012 | otel_demo | full | 6 | ebpf | 23978 | 0 | known_guest_observations=1283407; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=23978 |
| 40786403012 | otel_demo | full | 6 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=992281 | none |
| 40803782214 | otel_demo | absent | 6 | ebpf | 41234 | 0 | known_guest_observations=1453830; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=41234 |
| 40803782214 | otel_demo | absent | 6 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=0 | none |
| 40803782214 | otel_demo | absent | 7 | ebpf | 41254 | 0 | known_guest_observations=1476452; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=41254 |
| 40803782214 | otel_demo | absent | 7 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=0 | none |
| 40803782214 | otel_demo | absent | 8 | ebpf | 43783 | 0 | known_guest_observations=1481006; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=43783 |
| 40803782214 | otel_demo | absent | 8 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=0 | none |
| 40803790289 | otel_demo | partial | 6 | ebpf | 23562 | 0 | known_guest_observations=1496855; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=23562 |
| 40803790289 | otel_demo | partial | 6 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=1042732 | none |
| 40803790289 | otel_demo | partial | 7 | ebpf | 23514 | 0 | known_guest_observations=1417054; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=23514 |
| 40803790289 | otel_demo | partial | 7 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=979093 | none |
| 40803790289 | otel_demo | partial | 8 | ebpf | 25890 | 0 | known_guest_observations=1517007; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=25890 |
| 40803790289 | otel_demo | partial | 8 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=1045908 | none |
| 40803798632 | otel_demo | full | 7 | ebpf | 24139 | 0 | known_guest_observations=1474962; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=24139 |
| 40803798632 | otel_demo | full | 7 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=1139482 | none |
| 40803806299 | otel_demo | full | 8 | ebpf | 28799 | 0 | known_guest_observations=1471631; unattributed_guest_observations=0 | unknown_missing_or_unplanned_header=28799 |
| 40803806299 | otel_demo | full | 8 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=1139473 | none |
| 40821198727 | deathstarbench | full | 6 | ebpf | 0 | 0 | known_guest_observations=416838; unattributed_guest_observations=0 | none |
| 40821198727 | deathstarbench | full | 6 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=617717 | none |
| 40821214009 | deathstarbench | absent | 6 | ebpf | 0 | 0 | known_guest_observations=403385; unattributed_guest_observations=0 | none |
| 40821214009 | deathstarbench | absent | 6 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=1 | none |
| 40821214009 | deathstarbench | absent | 7 | ebpf | 0 | 0 | known_guest_observations=407422; unattributed_guest_observations=0 | none |
| 40821214009 | deathstarbench | absent | 7 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=1 | none |
| 40821214009 | deathstarbench | absent | 8 | ebpf | 0 | 0 | known_guest_observations=404528; unattributed_guest_observations=0 | none |
| 40821214009 | deathstarbench | absent | 8 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=1 | none |
| 40821232082 | deathstarbench | partial | 6 | ebpf | 0 | 0 | known_guest_observations=405994; unattributed_guest_observations=0 | none |
| 40821232082 | deathstarbench | partial | 6 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=533904 | none |
| 40821232082 | deathstarbench | partial | 7 | ebpf | 0 | 0 | known_guest_observations=411634; unattributed_guest_observations=0 | none |
| 40821232082 | deathstarbench | partial | 7 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=534086 | none |
| 40821232082 | deathstarbench | partial | 8 | ebpf | 0 | 0 | known_guest_observations=409128; unattributed_guest_observations=0 | none |
| 40821232082 | deathstarbench | partial | 8 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=534092 | none |
| 40821255620 | deathstarbench | full | 7 | ebpf | 0 | 0 | known_guest_observations=414971; unattributed_guest_observations=0 | none |
| 40821255620 | deathstarbench | full | 7 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=617639 | none |
| 40821277823 | deathstarbench | full | 8 | ebpf | 0 | 0 | known_guest_observations=409923; unattributed_guest_observations=0 | none |
| 40821277823 | deathstarbench | full | 8 | native | 0 | 0 | known_guest_observations=0; unattributed_guest_observations=617545 | none |

Causal evidence availability (not recomputed from attempt rows):

| Run | System | Mode | Seed | Attempt evidence present | Stored-summary status |
|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | false | no stored causal summary |
| 40733841068 | petclinic | absent | 6 | false | no stored causal summary |
| 40733841068 | petclinic | absent | 7 | false | no stored causal summary |
| 40733841068 | petclinic | absent | 8 | false | no stored causal summary |
| 40733846961 | petclinic | partial | 6 | false | no stored causal summary |
| 40733846961 | petclinic | partial | 7 | false | no stored causal summary |
| 40733846961 | petclinic | partial | 8 | false | no stored causal summary |
| 40733852492 | petclinic | full | 7 | false | no stored causal summary |
| 40733858113 | petclinic | full | 8 | false | no stored causal summary |
| 40754529169 | otel_demo | full | 6 | false | evidence-v4.json pending |
| 40786403012 | otel_demo | full | 6 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803782214 | otel_demo | absent | 6 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803782214 | otel_demo | absent | 7 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803782214 | otel_demo | absent | 8 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803790289 | otel_demo | partial | 6 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803790289 | otel_demo | partial | 7 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803790289 | otel_demo | partial | 8 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803798632 | otel_demo | full | 7 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40803806299 | otel_demo | full | 8 | true | linked attempt rows retained in evidence-v4; no saved aggregate summary |
| 40821198727 | deathstarbench | full | 6 | false | no stored causal summary |
| 40821214009 | deathstarbench | absent | 6 | false | no stored causal summary |
| 40821214009 | deathstarbench | absent | 7 | false | no stored causal summary |
| 40821214009 | deathstarbench | absent | 8 | false | no stored causal summary |
| 40821232082 | deathstarbench | partial | 6 | false | no stored causal summary |
| 40821232082 | deathstarbench | partial | 7 | false | no stored causal summary |
| 40821232082 | deathstarbench | partial | 8 | false | no stored causal summary |
| 40821255620 | deathstarbench | full | 7 | false | no stored causal summary |
| 40821277823 | deathstarbench | full | 8 | false | no stored causal summary |

Stored exact-chain association verdict census:

These verdicts describe source-local exact chain association in the final capture. They do not establish SQL durability or business correctness.

| Run | System | Mode | Seed | Source | Phase | Total | Observed | Unknown | Not recorded | Unexpected states | Coverage observed/total | All stored states |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733841068 | petclinic | absent | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733841068 | petclinic | absent | 7 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733841068 | petclinic | absent | 8 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733846961 | petclinic | partial | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733846961 | petclinic | partial | 7 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733846961 | petclinic | partial | 8 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733852492 | petclinic | full | 7 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40733858113 | petclinic | full | 8 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40754529169 | otel_demo | full | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40786403012 | otel_demo | full | 6 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40786403012 | otel_demo | full | 6 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40786403012 | otel_demo | full | 6 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40786403012 | otel_demo | full | 6 | native | async_normal | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40786403012 | otel_demo | full | 6 | native | async_paused | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40786403012 | otel_demo | full | 6 | native | async_recovered | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803782214 | otel_demo | absent | 6 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 6 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 6 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 6 | native | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 6 | native | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 6 | native | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 7 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 7 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 7 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 7 | native | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 7 | native | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 7 | native | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 8 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 8 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 8 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 8 | native | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 8 | native | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803782214 | otel_demo | absent | 8 | native | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 6 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 6 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 6 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 6 | native | async_normal | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 6 | native | async_paused | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 6 | native | async_recovered | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 7 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 7 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 7 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 7 | native | async_normal | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 7 | native | async_paused | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 7 | native | async_recovered | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 8 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 8 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 8 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803790289 | otel_demo | partial | 8 | native | async_normal | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 8 | native | async_paused | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803790289 | otel_demo | partial | 8 | native | async_recovered | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803798632 | otel_demo | full | 7 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803798632 | otel_demo | full | 7 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803798632 | otel_demo | full | 7 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803798632 | otel_demo | full | 7 | native | async_normal | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803798632 | otel_demo | full | 7 | native | async_paused | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803798632 | otel_demo | full | 7 | native | async_recovered | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803806299 | otel_demo | full | 8 | ebpf | async_normal | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803806299 | otel_demo | full | 8 | ebpf | async_paused | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803806299 | otel_demo | full | 8 | ebpf | async_recovered | 20 | 0 | 20 | 0 | none | 0/20 | unknown=20 |
| 40803806299 | otel_demo | full | 8 | native | async_normal | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803806299 | otel_demo | full | 8 | native | async_paused | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40803806299 | otel_demo | full | 8 | native | async_recovered | 20 | 20 | 0 | 0 | none | 20/20 | observed=20 |
| 40821198727 | deathstarbench | full | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821214009 | deathstarbench | absent | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821214009 | deathstarbench | absent | 7 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821214009 | deathstarbench | absent | 8 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821232082 | deathstarbench | partial | 6 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821232082 | deathstarbench | partial | 7 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821232082 | deathstarbench | partial | 8 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821255620 | deathstarbench | full | 7 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |
| 40821277823 | deathstarbench | full | 8 | unavailable | unavailable | unknown | unknown | unknown | unknown | unknown | unavailable | stored async attempt evidence missing |

## Costs

| Run | System | Mode | Seed | Campaign s | Clone s | Build s | Input prep s | Toolchain commands s | Bering replay s | Bering peak RSS KiB | Infrastructure fields | Manual prep measured | Unavailable reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | 4669.68247569 | 3.23547027 | 22.549820751 | 67.482554746 | 1475.647914665 | 890.8722047489999 | 7411120 | Maximum resident set size (kbytes)=7411120; System time (seconds)=194.37; User time (seconds)=2250.74 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733841068 | petclinic | absent | 6 | 3800.514220971 | 4.307709416 | 31.792177915000003 | 37.62741328 | 754.391958428 | 570.041811003 | 4870404 | Maximum resident set size (kbytes)=4870404; System time (seconds)=169.13; User time (seconds)=1386.29 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733841068 | petclinic | absent | 7 | 3783.514737552 | 5.8141398639999995 | 28.281987554 | 39.576497939 | 717.230629504 | 486.714270645 | 4689060 | Maximum resident set size (kbytes)=4689060; System time (seconds)=143.31; User time (seconds)=1192.97 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733841068 | petclinic | absent | 8 | 3243.894307223 | 5.121710323 | 18.943810952 | 25.838606865 | 470.90593683099996 | 329.09998643299997 | 4498872 | Maximum resident set size (kbytes)=4498872; System time (seconds)=83.83; User time (seconds)=890.34 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733846961 | petclinic | partial | 6 | 4884.778714435 | 6.5345889790000005 | 29.987832241 | 87.865785347 | 1571.85424067 | 1028.554647501 | 7349096 | Maximum resident set size (kbytes)=7349096; System time (seconds)=288.67; User time (seconds)=2376.01 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733846961 | petclinic | partial | 7 | 3879.076947378 | 8.681306982999999 | 20.210321374 | 61.024597838 | 869.248816195 | 622.81067206 | 7631224 | Maximum resident set size (kbytes)=7631224; System time (seconds)=167.37; User time (seconds)=1441.54 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733846961 | petclinic | partial | 8 | 3869.422391574 | 5.1619185430000005 | 16.541459322999998 | 60.612490972 | 853.889719474 | 547.877010985 | 6940660 | Maximum resident set size (kbytes)=6940660; System time (seconds)=125.77; User time (seconds)=1466.44 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733852492 | petclinic | full | 7 | 4870.178149396 | 7.76414388 | 20.635976547000002 | 93.475161214 | 1527.15715244 | 902.554532047 | 8251620 | Maximum resident set size (kbytes)=8251620; System time (seconds)=189.50; User time (seconds)=2293.27 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40733858113 | petclinic | full | 8 | 5389.856800755 | 5.3632503719999995 | 29.161389126 | 97.838999148 | 1886.142436688 | 1249.208880748 | 7412260 | Maximum resident set size (kbytes)=7412260; System time (seconds)=303.81; User time (seconds)=2803.89 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40754529169 | otel_demo | full | 6 | 8522.573071745 | 9.890061742 | 23.070768612000002 | unknown | unknown | unknown | unknown | Maximum resident set size (kbytes)=884036; System time (seconds)=156.02; User time (seconds)=650.28 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40786403012 | otel_demo | full | 6 | 8144.446709622 | 1.674152042 | 29.389550459 | 182.456631631 | 2493.466407811 | 1805.481193481 | 12463584 | Maximum resident set size (kbytes)=1204936; System time (seconds)=335.15; User time (seconds)=1215.23 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803782214 | otel_demo | absent | 6 | 5617.884885372 | 4.277110707 | 31.191750886999998 | 62.677860024 | 846.631225337 | 696.266463637 | 11575712 | Maximum resident set size (kbytes)=1251108; System time (seconds)=176.33; User time (seconds)=915.36 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803782214 | otel_demo | absent | 7 | 6316.339852847 | 1.56227355 | 22.011151035 | 80.965446705 | 1370.13416946 | 1043.363241877 | 11769800 | Maximum resident set size (kbytes)=1325152; System time (seconds)=173.91; User time (seconds)=772.66 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803782214 | otel_demo | absent | 8 | 6245.471888307 | 4.074697845 | 22.763079929 | 78.370392319 | 1310.860870693 | 1023.643782186 | 11674492 | Maximum resident set size (kbytes)=1258132; System time (seconds)=171.26; User time (seconds)=778.82 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803790289 | otel_demo | partial | 6 | 6624.581495893 | 4.129550321 | 23.358830587 | 198.956943746 | 642.162714655 | 642.065886229 | 12664284 | Maximum resident set size (kbytes)=1300700; System time (seconds)=218.86; User time (seconds)=984.28 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803790289 | otel_demo | partial | 7 | 6603.624322006 | 3.725251494 | 29.055159959999997 | 165.331728374 | 768.568002019 | 768.481002062 | 12513536 | Maximum resident set size (kbytes)=1291016; System time (seconds)=363.99; User time (seconds)=1284.71 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803790289 | otel_demo | partial | 8 | 5895.57750139 | 2.7795717179999997 | 20.828586610000002 | 131.940540293 | 594.636066863 | 594.576282006 | 12766284 | Maximum resident set size (kbytes)=1297036; System time (seconds)=225.32; User time (seconds)=868.37 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803798632 | otel_demo | full | 7 | 8336.549604511 | 3.1704384130000003 | 19.615715977 | 209.666078478 | 2836.290970088 | 2192.909728869 | 12844572 | Maximum resident set size (kbytes)=1226680; System time (seconds)=225.43; User time (seconds)=867.84 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40803806299 | otel_demo | full | 8 | 8800.166416979 | 2.1711151650000002 | 22.92470587 | 181.243553118 | 2753.935442789 | 2146.536779624 | 12569912 | Maximum resident set size (kbytes)=1345212; System time (seconds)=288.20; User time (seconds)=1109.39 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821198727 | deathstarbench | full | 6 | 16139.483183382 | 3.496385835 | 28.050857349 | 255.673363137 | 3983.3492345199998 | 3605.731077933 | 12554764 | Maximum resident set size (kbytes)=647052; System time (seconds)=159.97; User time (seconds)=1039.42 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821214009 | deathstarbench | absent | 6 | 5893.412938199 | 3.789259902 | 20.915316438 | 9.015191151 | 52.332983811 | 52.306331043 | 3322528 | Maximum resident set size (kbytes)=627372; System time (seconds)=104.42; User time (seconds)=351.60 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821214009 | deathstarbench | absent | 7 | 10996.078751452 | 4.021035687 | 27.688643017 | 15.358316292 | 87.029595047 | 86.986278409 | 3800896 | Maximum resident set size (kbytes)=626508; System time (seconds)=115.75; User time (seconds)=521.47 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821214009 | deathstarbench | absent | 8 | 8011.582064801 | 4.023815562999999 | 23.258184884000002 | 11.457338408 | 68.370004026 | 68.333872 | 3738772 | Maximum resident set size (kbytes)=625820; System time (seconds)=114.52; User time (seconds)=412.17 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821232082 | deathstarbench | partial | 6 | 7331.269471976 | 4.296072187 | 19.588119049 | 123.110647776 | 1061.814083745 | 1029.695825601 | 11702704 | Maximum resident set size (kbytes)=626884; System time (seconds)=126.93; User time (seconds)=611.98 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821232082 | deathstarbench | partial | 7 | 11798.226423708 | 1.7727720539999998 | 29.418471706 | 204.469777438 | 1598.983579697 | 1542.49350654 | 11628860 | Maximum resident set size (kbytes)=626204; System time (seconds)=171.36; User time (seconds)=1040.52 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821232082 | deathstarbench | partial | 8 | 12179.628717469 | 3.956149921 | 30.188508836 | 211.701110865 | 1602.379406248 | 1540.957799608 | 11626052 | Maximum resident set size (kbytes)=628320; System time (seconds)=179.05; User time (seconds)=1069.74 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821255620 | deathstarbench | full | 7 | 14226.624488311 | 3.613445476 | 30.726712377 | 190.173894114 | 3206.663360586 | 3037.668229853 | 12563392 | Maximum resident set size (kbytes)=626680; System time (seconds)=185.63; User time (seconds)=1209.36 | false | human preparation time was not instrumented; no full-cost advantage claimed |
| 40821277823 | deathstarbench | full | 8 | 13778.187771277 | 4.444433476 | 23.274326162999998 | 241.932527526 | 3982.4370261159997 | 3639.549997043 | 12566012 | Maximum resident set size (kbytes)=629700; System time (seconds)=150.91; User time (seconds)=886.76 | false | human preparation time was not instrumented; no full-cost advantage claimed |

Saved HTTP transport costs by workload category:

These are stored request counts, response bytes and summed request durations, not recomputed metrics. Preparation, verification probes and controls are additional to primary operations. Completed transport does not imply business success. Concurrent request durations overlap and must not be added to campaign wall time. Verification probes are shown once here; the auxiliary_timeline_probes field is an alias, not an additional charge.

| Run | System | Mode | Seed | Category | Started | Completed | Transport unknown | Unresolved | Sum completed request s | Sum unknown request s | Completed response bytes | HTTP error responses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | control | 40 | 40 | 0 | 0 | 250.516738696 | 0 | 24435 | 15 |
| 40718674400 | petclinic | full | 6 | preparation | 64 | 64 | 0 | 0 | 55.343659441 | 0 | 58831 | 5 |
| 40718674400 | petclinic | full | 6 | primary | 34800 | 34800 | 0 | 0 | 417.691841701 | 0 | 33365509 | 1800 |
| 40718674400 | petclinic | full | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40718674400 | petclinic | full | 6 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733841068 | petclinic | absent | 6 | control | 40 | 40 | 0 | 0 | 250.416582032 | 0 | 24435 | 15 |
| 40733841068 | petclinic | absent | 6 | preparation | 64 | 64 | 0 | 0 | 56.692685282 | 0 | 58831 | 5 |
| 40733841068 | petclinic | absent | 6 | primary | 34800 | 34800 | 0 | 0 | 419.062272534 | 0 | 33365509 | 1800 |
| 40733841068 | petclinic | absent | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733841068 | petclinic | absent | 6 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733841068 | petclinic | absent | 7 | control | 40 | 40 | 0 | 0 | 250.386624558 | 0 | 24435 | 15 |
| 40733841068 | petclinic | absent | 7 | preparation | 64 | 64 | 0 | 0 | 55.936297236 | 0 | 58831 | 5 |
| 40733841068 | petclinic | absent | 7 | primary | 34800 | 34800 | 0 | 0 | 425.500562874 | 0 | 33365509 | 1800 |
| 40733841068 | petclinic | absent | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733841068 | petclinic | absent | 7 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733841068 | petclinic | absent | 8 | control | 40 | 40 | 0 | 0 | 250.304385895 | 0 | 24435 | 15 |
| 40733841068 | petclinic | absent | 8 | preparation | 64 | 64 | 0 | 0 | 53.975488493 | 0 | 58831 | 5 |
| 40733841068 | petclinic | absent | 8 | primary | 34800 | 34800 | 0 | 0 | 270.593587684 | 0 | 33365509 | 1800 |
| 40733841068 | petclinic | absent | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733841068 | petclinic | absent | 8 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733846961 | petclinic | partial | 6 | control | 40 | 40 | 0 | 0 | 250.487260102 | 0 | 24435 | 15 |
| 40733846961 | petclinic | partial | 6 | preparation | 64 | 64 | 0 | 0 | 55.008406949 | 0 | 58831 | 5 |
| 40733846961 | petclinic | partial | 6 | primary | 34800 | 34800 | 0 | 0 | 470.255599842 | 0 | 33365509 | 1800 |
| 40733846961 | petclinic | partial | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733846961 | petclinic | partial | 6 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733846961 | petclinic | partial | 7 | control | 40 | 40 | 0 | 0 | 250.302086731 | 0 | 24435 | 15 |
| 40733846961 | petclinic | partial | 7 | preparation | 64 | 64 | 0 | 0 | 54.565694679 | 0 | 58831 | 5 |
| 40733846961 | petclinic | partial | 7 | primary | 34800 | 34800 | 0 | 0 | 320.969108954 | 0 | 33365509 | 1800 |
| 40733846961 | petclinic | partial | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733846961 | petclinic | partial | 7 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733846961 | petclinic | partial | 8 | control | 40 | 40 | 0 | 0 | 250.398999619 | 0 | 24435 | 15 |
| 40733846961 | petclinic | partial | 8 | preparation | 64 | 64 | 0 | 0 | 54.329888118 | 0 | 58831 | 5 |
| 40733846961 | petclinic | partial | 8 | primary | 34800 | 34800 | 0 | 0 | 294.134660841 | 0 | 33365509 | 1800 |
| 40733846961 | petclinic | partial | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733846961 | petclinic | partial | 8 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733852492 | petclinic | full | 7 | control | 40 | 40 | 0 | 0 | 250.523325102 | 0 | 24435 | 15 |
| 40733852492 | petclinic | full | 7 | preparation | 64 | 64 | 0 | 0 | 55.834893009 | 0 | 58831 | 5 |
| 40733852492 | petclinic | full | 7 | primary | 34800 | 34800 | 0 | 0 | 440.176541573 | 0 | 33365509 | 1800 |
| 40733852492 | petclinic | full | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733852492 | petclinic | full | 7 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733858113 | petclinic | full | 8 | control | 40 | 40 | 0 | 0 | 250.63891073099998 | 0 | 24435 | 15 |
| 40733858113 | petclinic | full | 8 | preparation | 64 | 64 | 0 | 0 | 58.782242736 | 0 | 58831 | 5 |
| 40733858113 | petclinic | full | 8 | primary | 34800 | 34800 | 0 | 0 | 470.786048173 | 0 | 33365509 | 1800 |
| 40733858113 | petclinic | full | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40733858113 | petclinic | full | 8 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | control | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | preparation | 27 | 27 | 0 | 0 | 11.568472501 | 0 | 10643 | 3 |
| 40754529169 | otel_demo | full | 6 | primary | 42951 | 42951 | 0 | 0 | 12362.016645945 | 0 | 16263230 | 6302 |
| 40754529169 | otel_demo | full | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40754529169 | otel_demo | full | 6 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40786403012 | otel_demo | full | 6 | control | 239 | 239 | 0 | 0 | 27.632854453 | 0 | 109559 | 20 |
| 40786403012 | otel_demo | full | 6 | preparation | 95 | 95 | 0 | 0 | 20.529325348 | 0 | 37688 | 11 |
| 40786403012 | otel_demo | full | 6 | primary | 59985 | 59985 | 0 | 0 | 39130.68129414 | 0 | 21004051 | 11136 |
| 40786403012 | otel_demo | full | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40786403012 | otel_demo | full | 6 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803782214 | otel_demo | absent | 6 | control | 239 | 239 | 0 | 0 | 15.411203166 | 0 | 109559 | 20 |
| 40803782214 | otel_demo | absent | 6 | preparation | 95 | 95 | 0 | 0 | 18.407620143 | 0 | 37688 | 11 |
| 40803782214 | otel_demo | absent | 6 | primary | 62117 | 62117 | 0 | 0 | 7958.068365219 | 0 | 24134316 | 7600 |
| 40803782214 | otel_demo | absent | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803782214 | otel_demo | absent | 6 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803782214 | otel_demo | absent | 7 | control | 239 | 239 | 0 | 0 | 16.60560356 | 0 | 109559 | 20 |
| 40803782214 | otel_demo | absent | 7 | preparation | 96 | 96 | 0 | 0 | 18.839315265 | 0 | 39182 | 9 |
| 40803782214 | otel_demo | absent | 7 | primary | 62400 | 62400 | 0 | 0 | 7199.561214157 | 0 | 24485200 | 7200 |
| 40803782214 | otel_demo | absent | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803782214 | otel_demo | absent | 7 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803782214 | otel_demo | absent | 8 | control | 239 | 239 | 0 | 0 | 8.788129334 | 0 | 109559 | 20 |
| 40803782214 | otel_demo | absent | 8 | preparation | 96 | 96 | 0 | 0 | 20.86180448 | 0 | 39182 | 9 |
| 40803782214 | otel_demo | absent | 8 | primary | 62400 | 62400 | 0 | 0 | 7375.211706262 | 0 | 24485200 | 7200 |
| 40803782214 | otel_demo | absent | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803782214 | otel_demo | absent | 8 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803790289 | otel_demo | partial | 6 | control | 239 | 239 | 0 | 0 | 35.595565694 | 0 | 109559 | 20 |
| 40803790289 | otel_demo | partial | 6 | preparation | 96 | 96 | 0 | 0 | 22.994008619 | 0 | 39182 | 9 |
| 40803790289 | otel_demo | partial | 6 | primary | 62317 | 62317 | 0 | 0 | 15155.373335968 | 0 | 24390906 | 7299 |
| 40803790289 | otel_demo | partial | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803790289 | otel_demo | partial | 6 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803790289 | otel_demo | partial | 7 | control | 239 | 239 | 0 | 0 | 55.643031284 | 0 | 109559 | 20 |
| 40803790289 | otel_demo | partial | 7 | preparation | 96 | 96 | 0 | 0 | 19.304238517 | 0 | 39182 | 9 |
| 40803790289 | otel_demo | partial | 7 | primary | 61969 | 61969 | 0 | 0 | 35845.201915379 | 0 | 22973090 | 8895 |
| 40803790289 | otel_demo | partial | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803790289 | otel_demo | partial | 7 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803790289 | otel_demo | partial | 8 | control | 239 | 239 | 0 | 0 | 6.807327836 | 0 | 109559 | 20 |
| 40803790289 | otel_demo | partial | 8 | preparation | 96 | 96 | 0 | 0 | 20.448250863000002 | 0 | 39182 | 9 |
| 40803790289 | otel_demo | partial | 8 | primary | 62399 | 62399 | 0 | 0 | 7422.233819344 | 0 | 24484265 | 7201 |
| 40803790289 | otel_demo | partial | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803790289 | otel_demo | partial | 8 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803798632 | otel_demo | full | 7 | control | 239 | 239 | 0 | 0 | 5.399819083 | 0 | 109559 | 20 |
| 40803798632 | otel_demo | full | 7 | preparation | 96 | 96 | 0 | 0 | 20.996428243 | 0 | 39182 | 9 |
| 40803798632 | otel_demo | full | 7 | primary | 62400 | 62400 | 0 | 0 | 7721.223043631 | 0 | 24485200 | 7200 |
| 40803798632 | otel_demo | full | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803798632 | otel_demo | full | 7 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803806299 | otel_demo | full | 8 | control | 239 | 239 | 0 | 0 | 16.499331801 | 0 | 109559 | 20 |
| 40803806299 | otel_demo | full | 8 | preparation | 96 | 96 | 0 | 0 | 14.547711877 | 0 | 39182 | 9 |
| 40803806299 | otel_demo | full | 8 | primary | 62400 | 62400 | 0 | 0 | 11859.84121051 | 0 | 24484789 | 7201 |
| 40803806299 | otel_demo | full | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40803806299 | otel_demo | full | 8 | verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821198727 | deathstarbench | full | 6 | control | 40 | 40 | 0 | 0 | 6.364862906 | 0 | 6694 | 0 |
| 40821198727 | deathstarbench | full | 6 | preparation | 48 | 48 | 0 | 0 | 1.393706726 | 0 | 8051 | 7 |
| 40821198727 | deathstarbench | full | 6 | primary | 34800 | 34800 | 0 | 0 | 267.973881131 | 0 | 5694000 | 4800 |
| 40821198727 | deathstarbench | full | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821198727 | deathstarbench | full | 6 | verification | 18428 | 18428 | 0 | 0 | 7526.840769022 | 0 | 5630724332 | 0 |
| 40821214009 | deathstarbench | absent | 6 | control | 40 | 40 | 0 | 0 | 6.199636555 | 0 | 6694 | 0 |
| 40821214009 | deathstarbench | absent | 6 | preparation | 48 | 48 | 0 | 0 | 1.197727817 | 0 | 8070 | 8 |
| 40821214009 | deathstarbench | absent | 6 | primary | 34800 | 34800 | 0 | 0 | 153.228201953 | 0 | 5694000 | 4800 |
| 40821214009 | deathstarbench | absent | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821214009 | deathstarbench | absent | 6 | verification | 18428 | 18428 | 0 | 0 | 2838.147439838 | 0 | 5630989552 | 0 |
| 40821214009 | deathstarbench | absent | 7 | control | 40 | 40 | 0 | 0 | 6.370230888 | 0 | 6746 | 0 |
| 40821214009 | deathstarbench | absent | 7 | preparation | 48 | 48 | 0 | 0 | 1.3853416760000001 | 0 | 8130 | 8 |
| 40821214009 | deathstarbench | absent | 7 | primary | 34800 | 34800 | 0 | 0 | 267.988702958 | 0 | 5735600 | 4800 |
| 40821214009 | deathstarbench | absent | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821214009 | deathstarbench | absent | 7 | verification | 18428 | 18428 | 0 | 0 | 7512.361439299 | 0 | 5636836264 | 0 |
| 40821214009 | deathstarbench | absent | 8 | control | 40 | 40 | 0 | 0 | 6.209341511 | 0 | 6720 | 0 |
| 40821214009 | deathstarbench | absent | 8 | preparation | 48 | 48 | 0 | 0 | 1.227249961 | 0 | 8100 | 8 |
| 40821214009 | deathstarbench | absent | 8 | primary | 34800 | 34800 | 0 | 0 | 157.611243065 | 0 | 5714819 | 4801 |
| 40821214009 | deathstarbench | absent | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821214009 | deathstarbench | absent | 8 | verification | 18426 | 18426 | 0 | 0 | 4754.288770974 | 0 | 5623644036 | 0 |
| 40821232082 | deathstarbench | partial | 6 | control | 40 | 40 | 0 | 0 | 6.139231228 | 0 | 6746 | 0 |
| 40821232082 | deathstarbench | partial | 6 | preparation | 48 | 48 | 0 | 0 | 1.19005979 | 0 | 8092 | 6 |
| 40821232082 | deathstarbench | partial | 6 | primary | 34800 | 34800 | 0 | 0 | 145.232864916 | 0 | 5735600 | 4800 |
| 40821232082 | deathstarbench | partial | 6 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821232082 | deathstarbench | partial | 6 | verification | 18428 | 18428 | 0 | 0 | 2658.1640155 | 0 | 5631050128 | 0 |
| 40821232082 | deathstarbench | partial | 7 | control | 40 | 40 | 0 | 0 | 6.25463808 | 0 | 6720 | 0 |
| 40821232082 | deathstarbench | partial | 7 | preparation | 48 | 48 | 0 | 0 | 1.308252669 | 0 | 8100 | 8 |
| 40821232082 | deathstarbench | partial | 7 | primary | 34800 | 34800 | 0 | 0 | 221.730432985 | 0 | 5714800 | 4800 |
| 40821232082 | deathstarbench | partial | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821232082 | deathstarbench | partial | 7 | verification | 18428 | 18428 | 0 | 0 | 6097.779138821 | 0 | 5636620780 | 0 |
| 40821232082 | deathstarbench | partial | 8 | control | 40 | 40 | 0 | 0 | 6.308231434 | 0 | 6746 | 0 |
| 40821232082 | deathstarbench | partial | 8 | preparation | 48 | 48 | 0 | 0 | 1.2950119310000001 | 0 | 8149 | 9 |
| 40821232082 | deathstarbench | partial | 8 | primary | 34800 | 34800 | 0 | 0 | 224.278615992 | 0 | 5735600 | 4800 |
| 40821232082 | deathstarbench | partial | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821232082 | deathstarbench | partial | 8 | verification | 18428 | 18428 | 0 | 0 | 6431.561584178 | 0 | 5624361268 | 0 |
| 40821255620 | deathstarbench | full | 7 | control | 40 | 40 | 0 | 0 | 6.3004286359999995 | 0 | 6720 | 0 |
| 40821255620 | deathstarbench | full | 7 | preparation | 48 | 48 | 0 | 0 | 1.3479652819999999 | 0 | 8081 | 7 |
| 40821255620 | deathstarbench | full | 7 | primary | 34800 | 34800 | 0 | 0 | 238.676874742 | 0 | 5714800 | 4800 |
| 40821255620 | deathstarbench | full | 7 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821255620 | deathstarbench | full | 7 | verification | 18428 | 18428 | 0 | 0 | 6545.668207345 | 0 | 5636569844 | 0 |
| 40821277823 | deathstarbench | full | 8 | control | 40 | 40 | 0 | 0 | 6.2276071570000004 | 0 | 6720 | 0 |
| 40821277823 | deathstarbench | full | 8 | preparation | 48 | 48 | 0 | 0 | 1.253252995 | 0 | 8100 | 8 |
| 40821277823 | deathstarbench | full | 8 | primary | 34800 | 34800 | 0 | 0 | 193.666579425 | 0 | 5714819 | 4801 |
| 40821277823 | deathstarbench | full | 8 | unclassified | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 40821277823 | deathstarbench | full | 8 | verification | 18426 | 18426 | 0 | 0 | 5286.500068098 | 0 | 5605643322 | 0 |

Saved campaign phase costs:

Checkpoint creation/upload hold is nested inside campaign elapsed; swap setup precedes campaign elapsed. Full stored cost records remain in the linked evaluation input.

| Run | System | Mode | Seed | Checkpoint creation s | Checkpoint upload hold s | Checkpoint total s | Upload success | Upload artifact ID | Swap setup s | Swap status | Swap requested additional bytes | Resource heartbeat retained |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40718674400 | petclinic | full | 6 | 80.069671682 | 19.004231597 | 99.073903279 | true | 12832246532 | 0.087039723 | ready | 8589934592 | true |
| 40733841068 | petclinic | absent | 6 | 31.288529093 | 17.004206637 | 48.29273573 | true | 12838193520 | 0.110868263 | ready | 8589934592 | true |
| 40733841068 | petclinic | absent | 7 | 54.895196458 | 17.009631473 | 71.904827931 | true | 12837538938 | 0.16080342 | ready | 8589934592 | true |
| 40733841068 | petclinic | absent | 8 | 19.195691585 | 11.003446117 | 30.199137702 | true | 12837389274 | 0.082118846 | ready | 8589934592 | true |
| 40733846961 | petclinic | partial | 6 | 64.729737824 | 25.008601661 | 89.738339485 | true | 12838517308 | 0.108945748 | ready | 8589934592 | true |
| 40733846961 | petclinic | partial | 7 | 65.824836983 | 23.006413161 | 88.831250144 | true | 12839031559 | 0.090754744 | ready | 8589934592 | true |
| 40733846961 | petclinic | partial | 8 | 68.614353227 | 30.009420127 | 98.623773354 | true | 12839020932 | 0.07308531 | ready | 8589934592 | true |
| 40733852492 | petclinic | full | 7 | 79.647242783 | 24.008772116 | 103.656014899 | true | 12838167741 | 0.092709382 | ready | 8589934592 | true |
| 40733858113 | petclinic | full | 8 | 75.690436443 | 23.007940834 | 98.698377277 | true | 12837658897 | 0.10590202 | ready | 8589934592 | true |
| 40754529169 | otel_demo | full | 6 | 300.872497326 | 62.017337472 | 362.889834798 | true | 12847933267 | 0.14220959 | ready | 8589934592 | true |
| 40786403012 | otel_demo | full | 6 | 173.046098515 | 50.02159402 | 223.067692535 | true | 12862210934 | 0.10096031 | ready | 8589934592 | true |
| 40803782214 | otel_demo | absent | 6 | 107.691221785 | 41.011559354 | 148.702781139 | true | 12868369677 | 0.083428334 | ready | 8589934592 | true |
| 40803782214 | otel_demo | absent | 7 | 133.031169888 | 31.010951961 | 164.042121849 | true | 12869555397 | 0.134784754 | ready | 8589934592 | true |
| 40803782214 | otel_demo | absent | 8 | 127.75399635 | 32.015766915 | 159.769763265 | true | 12868444304 | 0.09522913 | ready | 8589934592 | true |
| 40803790289 | otel_demo | partial | 6 | 255.970787196 | 51.01584485 | 306.986632046 | true | 12869290997 | 0.086795316 | ready | 8589934592 | true |
| 40803790289 | otel_demo | partial | 7 | 190.791376292 | 55.027169919 | 245.818546211 | true | 12869181498 | 0.101325168 | ready | 8589934592 | true |
| 40803790289 | otel_demo | partial | 8 | 234.685314492 | 38.01444781 | 272.699762302 | true | 12869196474 | 0.092548018 | ready | 8589934592 | true |
| 40803798632 | otel_demo | full | 7 | 221.640247246 | 39.016512732 | 260.656759978 | true | 12868394810 | 0.081483278 | ready | 8589934592 | true |
| 40803806299 | otel_demo | full | 8 | 244.286066967 | 55.016063802 | 299.302130769 | true | 12869017579 | 0.095990892 | ready | 8589934592 | true |
| 40821198727 | deathstarbench | full | 6 | 187.899370819 | 133.044173363 | 320.943544182 | true | 12879053957 | 0.13694859 | ready | 8589934592 | true |
| 40821214009 | deathstarbench | absent | 6 | 115.536917567 | 72.022367244 | 187.559284811 | true | 12877222019 | 0.118043848 | ready | 8589934592 | true |
| 40821214009 | deathstarbench | absent | 7 | 211.524538281 | 116.037393667 | 327.561931948 | true | 12879835217 | 0.129965396 | ready | 8589934592 | true |
| 40821214009 | deathstarbench | absent | 8 | 116.901481196 | 83.018770345 | 199.920251541 | true | 12878485168 | 0.097523281 | ready | 8589934592 | true |
| 40821232082 | deathstarbench | partial | 6 | 126.404489823 | 82.018984755 | 208.423474578 | true | 12877460736 | 0.08332783 | ready | 8589934592 | true |
| 40821232082 | deathstarbench | partial | 7 | 110.580682881 | 131.043176391 | 241.623859272 | true | 12878418058 | 0.105119573 | ready | 8589934592 | true |
| 40821232082 | deathstarbench | partial | 8 | 105.497800595 | 126.037395404 | 231.535195999 | true | 12878622790 | 0.108974703 | ready | 8589934592 | true |
| 40821255620 | deathstarbench | full | 7 | 106.391426652 | 130.037012546 | 236.428439198 | true | 12878744338 | 0.113604317 | ready | 8589934592 | true |
| 40821277823 | deathstarbench | full | 8 | 169.838821777 | 112.032962895 | 281.871784672 | true | 12878438474 | 0.218537199 | ready | 8589934592 | true |

Separate toolchain worker costs:

Parent wait is nested inside campaign elapsed and overlaps worker computation. Worker job durations belong in the Actions ledger separately; these phase values must not be added twice. The complete saved remote cost/provenance record remains in the evaluation input.

| Parent run | System | Mode | Seed | Worker run | Worker attempt | Checkpoint verification s | Dispatch s | Parent wait s | Output transfer s | Verification/import s |
|---|---|---|---|---|---|---|---|---|---|---|
| 40754529169 | otel_demo | full | 6 | 40764150238 | 1 | 1040.31912914 | 1.784036132 | 4778.004124619 | unknown | unknown |
| 40786403012 | otel_demo | full | 6 | 40792026316 | 1 | 344.994777139 | 1.247310947 | 3060.521369739 | 33.77228003 | 182.739812615 |
| 40803782214 | otel_demo | absent | 6 | 40808735563 | 1 | 185.153882671 | 1.480529959 | 1146.348275069 | 111.927880808 | 116.017565258 |
| 40803782214 | otel_demo | absent | 7 | 40808666481 | 1 | 213.249746994 | 1.403905536 | 1745.617846491 | 55.953950409 | 126.863940472 |
| 40803782214 | otel_demo | absent | 8 | 40808661139 | 1 | 211.456397854 | 1.262271858 | 1628.608875368 | 91.944705147 | 126.886513745 |
| 40803790289 | otel_demo | partial | 6 | 40808806603 | 1 | 460.519743728 | 1.285329481 | 1265.870222429 | 35.468280449 | 247.415551231 |
| 40803790289 | otel_demo | partial | 7 | 40808888799 | 1 | 367.395024966 | 1.183000508 | 1266.645075435 | 58.406883932 | 197.704003225 |
| 40803790289 | otel_demo | partial | 8 | 40808520837 | 1 | 397.709809011 | 1.06928947 | 1024.694033774 | 36.17904251 | 214.114193404 |
| 40803798632 | otel_demo | full | 7 | 40808413535 | 1 | 361.281935838 | 1.444445949 | 3436.266506713 | 60.006145714 | 210.801477767 |
| 40803806299 | otel_demo | full | 8 | 40808834064 | 1 | 359.43614953 | 1.178733508 | 3491.386321792 | 64.846068182 | 199.359615068 |
| 40821198727 | deathstarbench | full | 6 | 40833707109 | 1 | 86.044229408 | 1.204090181 | 4642.859775649 | 63.422155484 | 49.472038748 |
| 40821214009 | deathstarbench | absent | 6 | 40827363136 | 1 | 36.322409506 | 1.399613416 | 301.591484131 | 5.969508394 | 9.772045514 |
| 40821214009 | deathstarbench | absent | 7 | 40833191329 | 1 | 61.109733176 | 1.461428077 | 362.354410889 | 11.57261411 | 12.374076676 |
| 40821214009 | deathstarbench | absent | 8 | 40829685696 | 1 | 38.503278895 | 1.504051862 | 362.118499507 | 7.800104851 | 10.489986984 |
| 40821232082 | deathstarbench | partial | 6 | 40827566298 | 1 | 51.040875056 | 1.355889718 | 1449.464315502 | 29.434015768 | 29.331198296 |
| 40821232082 | deathstarbench | partial | 7 | 40831685820 | 1 | 56.997337355 | 1.305747881 | 2047.323234717 | 25.889916414 | 29.013780576 |
| 40821232082 | deathstarbench | partial | 8 | 40832082212 | 1 | 56.796698574 | 1.502254597 | 2051.415553343 | 38.158724275 | 27.748617128 |
| 40821255620 | deathstarbench | full | 7 | 40832412304 | 1 | 59.381526 | 1.450499455 | 3738.787233701 | 68.479248895 | 32.296014476 |
| 40821277823 | deathstarbench | full | 8 | 40831271725 | 1 | 62.771580632 | 1.457042122 | 4585.775289303 | 46.928686772 | 43.29839401 |

Optional saved cost artifact metadata:

| Stored field | Value |
|---|---|
| all_retained_artifact_bytes | 141072330122 |
| all_retained_job_seconds | 343146.0 |
| current_report_job_elapsed_seconds | unknown |
| human_agent_seconds | unknown |
| preparation_and_failed_runs_included | true |
| rule | sum of job durations is compute use, not campaign wall clock; overlapping artifacts are charged each time |
| schema_version | v4-actions-costs |

Saved Actions jobs (independent of retained campaign artifacts):

A job with no stored artifact is retained here as a technical execution record. It is not a campaign row and does not imply zero observations or any scientific outcome.

| Run | Role | Head SHA | Run status | Run conclusion | Job ID | Job name | Job status | Job conclusion | Stored elapsed s | Run artifacts | Run artifact names |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873766641 | prepare | completed | success | 3.0 | 0 | none |
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873831100 | campaign (otel_demo, full, 6) | completed | failure | 2542.0 | 0 | none |
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873831307 | campaign (deathstarbench, full, 6) | completed | failure | 11346.0 | 0 | none |
| 40704758284 | series | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | failure | 122873831892 | campaign (petclinic, full, 6) | completed | failure | 2750.0 | 0 | none |
| 40718665137 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | completed | failure | 122923240202 | prepare | completed | success | 3.0 | 1 | training-v4-otel_demo-full-6-40718665137 |
| 40718665137 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | completed | failure | 122923302034 | campaign (otel_demo, full, 6) | completed | failure | 9256.0 | 1 | training-v4-otel_demo-full-6-40718665137 |
| 40718674400 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | completed | success | 122923272255 | prepare | completed | success | 3.0 | 3 | campaign-v4-petclinic-full-6-40718674400, v4-summary-petclinic-full-6-40718674400, training-v4-petclinic-full-6-40718674400 |
| 40718674400 | series | ea2e278e50f64bd50597c243d84f834be1b92576 | completed | success | 122923328293 | campaign (petclinic, full, 6) | completed | success | 4874.0 | 3 | campaign-v4-petclinic-full-6-40718674400, v4-summary-petclinic-full-6-40718674400, training-v4-petclinic-full-6-40718674400 |
| 40731158179 | series | 3e708879889eac8a238027a4640466fc8a76eca5 | completed | cancelled | 122967537594 | prepare | completed | success | 2.0 | 1 | training-v4-deathstarbench-full-6-40731158179 |
| 40731158179 | series | 3e708879889eac8a238027a4640466fc8a76eca5 | completed | cancelled | 122967583738 | campaign (deathstarbench, full, 6) | completed | cancelled | 21900.0 | 1 | training-v4-deathstarbench-full-6-40731158179 |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122976976338 | prepare | completed | success | 4.0 | 9 | campaign-v4-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-8-40733841068, campaign-v4-petclinic-absent-6-40733841068, v4-summary-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-6-40733841068, campaign-v4-petclinic-absent-8-40733841068, training-v4-petclinic-absent-6-40733841068, training-v4-petclinic-absent-7-40733841068, training-v4-petclinic-absent-8-40733841068 |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977038199 | campaign (petclinic, absent, 6) | completed | success | 4021.0 | 9 | campaign-v4-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-8-40733841068, campaign-v4-petclinic-absent-6-40733841068, v4-summary-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-6-40733841068, campaign-v4-petclinic-absent-8-40733841068, training-v4-petclinic-absent-6-40733841068, training-v4-petclinic-absent-7-40733841068, training-v4-petclinic-absent-8-40733841068 |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977038314 | campaign (petclinic, absent, 8) | completed | success | 3412.0 | 9 | campaign-v4-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-8-40733841068, campaign-v4-petclinic-absent-6-40733841068, v4-summary-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-6-40733841068, campaign-v4-petclinic-absent-8-40733841068, training-v4-petclinic-absent-6-40733841068, training-v4-petclinic-absent-7-40733841068, training-v4-petclinic-absent-8-40733841068 |
| 40733841068 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977038331 | campaign (petclinic, absent, 7) | completed | success | 4012.0 | 9 | campaign-v4-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-8-40733841068, campaign-v4-petclinic-absent-6-40733841068, v4-summary-petclinic-absent-7-40733841068, v4-summary-petclinic-absent-6-40733841068, campaign-v4-petclinic-absent-8-40733841068, training-v4-petclinic-absent-6-40733841068, training-v4-petclinic-absent-7-40733841068, training-v4-petclinic-absent-8-40733841068 |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122976997740 | prepare | completed | success | 4.0 | 9 | campaign-v4-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-8-40733846961, v4-summary-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-7-40733846961, training-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-6-40733846961 |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977061849 | campaign (petclinic, partial, 8) | completed | success | 4055.0 | 9 | campaign-v4-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-8-40733846961, v4-summary-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-7-40733846961, training-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-6-40733846961 |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977061925 | campaign (petclinic, partial, 6) | completed | success | 5127.0 | 9 | campaign-v4-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-8-40733846961, v4-summary-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-7-40733846961, training-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-6-40733846961 |
| 40733846961 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977061988 | campaign (petclinic, partial, 7) | completed | success | 4072.0 | 9 | campaign-v4-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-8-40733846961, v4-summary-petclinic-partial-7-40733846961, v4-summary-petclinic-partial-6-40733846961, campaign-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-7-40733846961, training-v4-petclinic-partial-8-40733846961, training-v4-petclinic-partial-6-40733846961 |
| 40733852492 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977019489 | prepare | completed | success | 2.0 | 3 | campaign-v4-petclinic-full-7-40733852492, v4-summary-petclinic-full-7-40733852492, training-v4-petclinic-full-7-40733852492 |
| 40733852492 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977072193 | campaign (petclinic, full, 7) | completed | success | 5103.0 | 3 | campaign-v4-petclinic-full-7-40733852492, v4-summary-petclinic-full-7-40733852492, training-v4-petclinic-full-7-40733852492 |
| 40733858113 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977040060 | prepare | completed | success | 3.0 | 3 | v4-summary-petclinic-full-8-40733858113, campaign-v4-petclinic-full-8-40733858113, training-v4-petclinic-full-8-40733858113 |
| 40733858113 | series | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122977084450 | campaign (petclinic, full, 8) | completed | success | 5641.0 | 3 | v4-summary-petclinic-full-8-40733858113, campaign-v4-petclinic-full-8-40733858113, training-v4-petclinic-full-8-40733858113 |
| 40754529169 | series | 72133c00df3f7e4150a3f737dee33e4bee12527d | completed | failure | 123049798821 | prepare | completed | success | 3.0 | 3 | v4-summary-otel_demo-full-6-40754529169, campaign-v4-otel_demo-full-6-40754529169, training-v4-otel_demo-full-6-40754529169 |
| 40754529169 | series | 72133c00df3f7e4150a3f737dee33e4bee12527d | completed | failure | 123049846971 | campaign (otel_demo, full, 6) | completed | failure | 8732.0 | 3 | v4-summary-otel_demo-full-6-40754529169, campaign-v4-otel_demo-full-6-40754529169, training-v4-otel_demo-full-6-40754529169 |
| 40764150238 | series | 710c28470b400247cebb7430b39d0f599034ca9a | completed | failure | 123083675296 | toolchain | completed | failure | 4773.0 | 0 | none |
| 40786403012 | series | a0e7644362a4e1ac5913f33f06a9570f2a780000 | completed | success | 123160578368 | prepare | completed | success | 3.0 | 3 | campaign-v4-otel_demo-full-6-40786403012, v4-summary-otel_demo-full-6-40786403012, training-v4-otel_demo-full-6-40786403012 |
| 40786403012 | series | a0e7644362a4e1ac5913f33f06a9570f2a780000 | completed | success | 123160616528 | campaign (otel_demo, full, 6) | completed | success | 8463.0 | 3 | campaign-v4-otel_demo-full-6-40786403012, v4-summary-otel_demo-full-6-40786403012, training-v4-otel_demo-full-6-40786403012 |
| 40792026316 | series | 98fa033539df8f82bc05f1fb724049579ad41b4d | completed | success | 123179318002 | toolchain | completed | success | 3042.0 | 1 | toolchain-v4-otel_demo-full-6-40792026316 |
| 40803782214 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217778489 | prepare | completed | success | 3.0 | 9 | campaign-v4-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-6-40803782214, v4-summary-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-6-40803782214, training-v4-otel_demo-absent-7-40803782214, training-v4-otel_demo-absent-8-40803782214, training-v4-otel_demo-absent-6-40803782214 |
| 40803782214 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217805049 | campaign (otel_demo, absent, 7) | completed | success | 6606.0 | 9 | campaign-v4-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-6-40803782214, v4-summary-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-6-40803782214, training-v4-otel_demo-absent-7-40803782214, training-v4-otel_demo-absent-8-40803782214, training-v4-otel_demo-absent-6-40803782214 |
| 40803782214 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217805116 | campaign (otel_demo, absent, 6) | completed | success | 5941.0 | 9 | campaign-v4-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-6-40803782214, v4-summary-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-6-40803782214, training-v4-otel_demo-absent-7-40803782214, training-v4-otel_demo-absent-8-40803782214, training-v4-otel_demo-absent-6-40803782214 |
| 40803782214 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217805227 | campaign (otel_demo, absent, 8) | completed | success | 6507.0 | 9 | campaign-v4-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-7-40803782214, v4-summary-otel_demo-absent-6-40803782214, v4-summary-otel_demo-absent-8-40803782214, campaign-v4-otel_demo-absent-6-40803782214, training-v4-otel_demo-absent-7-40803782214, training-v4-otel_demo-absent-8-40803782214, training-v4-otel_demo-absent-6-40803782214 |
| 40803790289 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217802275 | prepare | completed | success | 3.0 | 9 | campaign-v4-otel_demo-partial-7-40803790289, campaign-v4-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-7-40803790289, v4-summary-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-8-40803790289, campaign-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-6-40803790289, training-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-7-40803790289 |
| 40803790289 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217826997 | campaign (otel_demo, partial, 7) | completed | success | 6925.0 | 9 | campaign-v4-otel_demo-partial-7-40803790289, campaign-v4-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-7-40803790289, v4-summary-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-8-40803790289, campaign-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-6-40803790289, training-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-7-40803790289 |
| 40803790289 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217827027 | campaign (otel_demo, partial, 6) | completed | success | 6893.0 | 9 | campaign-v4-otel_demo-partial-7-40803790289, campaign-v4-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-7-40803790289, v4-summary-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-8-40803790289, campaign-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-6-40803790289, training-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-7-40803790289 |
| 40803790289 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217827079 | campaign (otel_demo, partial, 8) | completed | success | 6136.0 | 9 | campaign-v4-otel_demo-partial-7-40803790289, campaign-v4-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-7-40803790289, v4-summary-otel_demo-partial-6-40803790289, v4-summary-otel_demo-partial-8-40803790289, campaign-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-6-40803790289, training-v4-otel_demo-partial-8-40803790289, training-v4-otel_demo-partial-7-40803790289 |
| 40803798632 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217829653 | prepare | completed | success | 3.0 | 3 | v4-summary-otel_demo-full-7-40803798632, campaign-v4-otel_demo-full-7-40803798632, training-v4-otel_demo-full-7-40803798632 |
| 40803798632 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217861511 | campaign (otel_demo, full, 7) | completed | success | 8614.0 | 3 | v4-summary-otel_demo-full-7-40803798632, campaign-v4-otel_demo-full-7-40803798632, training-v4-otel_demo-full-7-40803798632 |
| 40803806299 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217852350 | prepare | completed | success | 4.0 | 3 | campaign-v4-otel_demo-full-8-40803806299, v4-summary-otel_demo-full-8-40803806299, training-v4-otel_demo-full-8-40803806299 |
| 40803806299 | series | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123217888058 | campaign (otel_demo, full, 8) | completed | success | 9113.0 | 3 | campaign-v4-otel_demo-full-8-40803806299, v4-summary-otel_demo-full-8-40803806299, training-v4-otel_demo-full-8-40803806299 |
| 40808413535 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123232743924 | toolchain | completed | success | 3430.0 | 1 | toolchain-v4-otel_demo-full-7-40808413535 |
| 40808520837 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123233087336 | toolchain | completed | success | 984.0 | 1 | toolchain-v4-otel_demo-partial-8-40808520837 |
| 40808661139 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123233538217 | toolchain | completed | success | 1624.0 | 1 | toolchain-v4-otel_demo-absent-8-40808661139 |
| 40808666481 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123233555488 | toolchain | completed | success | 1708.0 | 1 | toolchain-v4-otel_demo-absent-7-40808666481 |
| 40808735563 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123233769130 | toolchain | completed | success | 1107.0 | 1 | toolchain-v4-otel_demo-absent-6-40808735563 |
| 40808806603 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123233998700 | toolchain | completed | success | 1217.0 | 1 | toolchain-v4-otel_demo-partial-6-40808806603 |
| 40808834064 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123234088935 | toolchain | completed | success | 3462.0 | 1 | toolchain-v4-otel_demo-full-8-40808834064 |
| 40808888799 | series | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123234258714 | toolchain | completed | success | 1241.0 | 1 | toolchain-v4-otel_demo-partial-7-40808888799 |
| 40821198727 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273830949 | prepare | completed | success | 4.0 | 4 | v4-summary-deathstarbench-full-6-40821198727, campaign-v4-deathstarbench-full-6-40821198727, retention-v4-deathstarbench-full-6-40821198727, training-v4-deathstarbench-full-6-40821198727 |
| 40821198727 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273862277 | campaign (deathstarbench, full, 6) | completed | success | 17014.0 | 4 | v4-summary-deathstarbench-full-6-40821198727, campaign-v4-deathstarbench-full-6-40821198727, retention-v4-deathstarbench-full-6-40821198727, training-v4-deathstarbench-full-6-40821198727 |
| 40821214009 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273880281 | prepare | completed | success | 4.0 | 12 | v4-summary-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-7-40821214009, retention-v4-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-8-40821214009, v4-summary-deathstarbench-absent-8-40821214009, retention-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-7-40821214009, v4-summary-deathstarbench-absent-6-40821214009, retention-v4-deathstarbench-absent-6-40821214009, campaign-v4-deathstarbench-absent-6-40821214009, training-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-6-40821214009 |
| 40821214009 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273912718 | campaign (deathstarbench, absent, 7) | completed | success | 11768.0 | 12 | v4-summary-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-7-40821214009, retention-v4-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-8-40821214009, v4-summary-deathstarbench-absent-8-40821214009, retention-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-7-40821214009, v4-summary-deathstarbench-absent-6-40821214009, retention-v4-deathstarbench-absent-6-40821214009, campaign-v4-deathstarbench-absent-6-40821214009, training-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-6-40821214009 |
| 40821214009 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273912772 | campaign (deathstarbench, absent, 8) | completed | success | 8621.0 | 12 | v4-summary-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-7-40821214009, retention-v4-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-8-40821214009, v4-summary-deathstarbench-absent-8-40821214009, retention-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-7-40821214009, v4-summary-deathstarbench-absent-6-40821214009, retention-v4-deathstarbench-absent-6-40821214009, campaign-v4-deathstarbench-absent-6-40821214009, training-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-6-40821214009 |
| 40821214009 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273912798 | campaign (deathstarbench, absent, 6) | completed | success | 6389.0 | 12 | v4-summary-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-7-40821214009, retention-v4-deathstarbench-absent-7-40821214009, campaign-v4-deathstarbench-absent-8-40821214009, v4-summary-deathstarbench-absent-8-40821214009, retention-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-7-40821214009, v4-summary-deathstarbench-absent-6-40821214009, retention-v4-deathstarbench-absent-6-40821214009, campaign-v4-deathstarbench-absent-6-40821214009, training-v4-deathstarbench-absent-8-40821214009, training-v4-deathstarbench-absent-6-40821214009 |
| 40821232082 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273936771 | prepare | completed | success | 3.0 | 12 | retention-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-7-40821232082, campaign-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-8-40821232082, retention-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-6-40821232082, v4-summary-deathstarbench-partial-6-40821232082, retention-v4-deathstarbench-partial-6-40821232082, training-v4-deathstarbench-partial-8-40821232082, training-v4-deathstarbench-partial-7-40821232082, training-v4-deathstarbench-partial-6-40821232082 |
| 40821232082 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273964510 | campaign (deathstarbench, partial, 8) | completed | success | 12894.0 | 12 | retention-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-7-40821232082, campaign-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-8-40821232082, retention-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-6-40821232082, v4-summary-deathstarbench-partial-6-40821232082, retention-v4-deathstarbench-partial-6-40821232082, training-v4-deathstarbench-partial-8-40821232082, training-v4-deathstarbench-partial-7-40821232082, training-v4-deathstarbench-partial-6-40821232082 |
| 40821232082 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273964517 | campaign (deathstarbench, partial, 7) | completed | success | 12491.0 | 12 | retention-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-7-40821232082, campaign-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-8-40821232082, retention-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-6-40821232082, v4-summary-deathstarbench-partial-6-40821232082, retention-v4-deathstarbench-partial-6-40821232082, training-v4-deathstarbench-partial-8-40821232082, training-v4-deathstarbench-partial-7-40821232082, training-v4-deathstarbench-partial-6-40821232082 |
| 40821232082 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123273964565 | campaign (deathstarbench, partial, 6) | completed | success | 7879.0 | 12 | retention-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-7-40821232082, campaign-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-7-40821232082, v4-summary-deathstarbench-partial-8-40821232082, retention-v4-deathstarbench-partial-8-40821232082, campaign-v4-deathstarbench-partial-6-40821232082, v4-summary-deathstarbench-partial-6-40821232082, retention-v4-deathstarbench-partial-6-40821232082, training-v4-deathstarbench-partial-8-40821232082, training-v4-deathstarbench-partial-7-40821232082, training-v4-deathstarbench-partial-6-40821232082 |
| 40821255620 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123274010761 | prepare | completed | success | 3.0 | 4 | campaign-v4-deathstarbench-full-7-40821255620, v4-summary-deathstarbench-full-7-40821255620, retention-v4-deathstarbench-full-7-40821255620, training-v4-deathstarbench-full-7-40821255620 |
| 40821255620 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123274034591 | campaign (deathstarbench, full, 7) | completed | success | 14983.0 | 4 | campaign-v4-deathstarbench-full-7-40821255620, v4-summary-deathstarbench-full-7-40821255620, retention-v4-deathstarbench-full-7-40821255620, training-v4-deathstarbench-full-7-40821255620 |
| 40821277823 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123274079189 | prepare | completed | success | 3.0 | 4 | v4-summary-deathstarbench-full-8-40821277823, campaign-v4-deathstarbench-full-8-40821277823, retention-v4-deathstarbench-full-8-40821277823, training-v4-deathstarbench-full-8-40821277823 |
| 40821277823 | series | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123274104505 | campaign (deathstarbench, full, 8) | completed | success | 14642.0 | 4 | v4-summary-deathstarbench-full-8-40821277823, campaign-v4-deathstarbench-full-8-40821277823, retention-v4-deathstarbench-full-8-40821277823, training-v4-deathstarbench-full-8-40821277823 |
| 40827363136 | series | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123293370726 | toolchain | completed | success | 250.0 | 1 | toolchain-v4-deathstarbench-absent-6-40827363136 |
| 40827566298 | series | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123294016438 | toolchain | completed | success | 1422.0 | 1 | toolchain-v4-deathstarbench-partial-6-40827566298 |
| 40829685696 | series | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123300771208 | toolchain | completed | success | 312.0 | 1 | toolchain-v4-deathstarbench-absent-8-40829685696 |
| 40831271725 | series | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123305804341 | toolchain | completed | success | 4567.0 | 1 | toolchain-v4-deathstarbench-full-8-40831271725 |
| 40831685820 | series | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123307121663 | toolchain | completed | success | 2030.0 | 1 | toolchain-v4-deathstarbench-partial-7-40831685820 |
| 40832082212 | series | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123308364723 | toolchain | completed | success | 2027.0 | 1 | toolchain-v4-deathstarbench-partial-8-40832082212 |
| 40832412304 | series | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123309412809 | toolchain | completed | success | 3711.0 | 1 | toolchain-v4-deathstarbench-full-7-40832412304 |
| 40833191329 | series | 1406e559d8d8f432179116460b33f118f666550f | completed | success | 123311851046 | toolchain | completed | success | 299.0 | 1 | toolchain-v4-deathstarbench-absent-7-40833191329 |
| 40833707109 | series | 1406e559d8d8f432179116460b33f118f666550f | completed | success | 123313492875 | toolchain | completed | success | 4585.0 | 1 | toolchain-v4-deathstarbench-full-6-40833707109 |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703847782 | prepare | completed | success | 4.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703882684 | qualify (otel_demo, full, 6) | completed | failure | 735.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703882705 | qualify (deathstarbench, full, 6) | completed | failure | 360.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40655022146 | qualification | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | failure | 122703882785 | qualify (petclinic, full, 6) | completed | failure | 417.0 | 3 | qualification-v4-deathstarbench-full-6-40655022146, qualification-v4-petclinic-full-6-40655022146, qualification-v4-otel_demo-full-6-40655022146 |
| 40658671556 | replay | 6810aed19ceb7ebc5dfe790aa4c9ae1f3dde527e | completed | failure | 122715914425 | replay | completed | failure | 74.0 | 1 | replay-qualification-v4-all-40655022146-40658671556 |
| 40661273773 | replay | 12954418b8413d07b09fc808f3e5762ab5d249b7 | completed | success | 122724620556 | replay | completed | success | 40.0 | 1 | replay-qualification-v4-petclinic-40655022146-40661273773 |
| 40668208749 | replay | 1d3a7bdde7e280ed7fae0e0c2ebb7928ab43f570 | completed | success | 122748041062 | replay | completed | success | 953.0 | 1 | replay-qualification-v4-all-40655022146-40668208749 |
| 40674465933 | replay | 2b72cd73d7fdb88c3dfa7f51a34e073b6e83d0b8 | completed | success | 122769236368 | replay | completed | success | 1368.0 | 1 | replay-qualification-v4-all-40655022146-40674465933 |
| 40742060084 | replay | 0c75e0d874907b99007a1f1a0d12f29f5331ad3a | completed | success | 123005984567 | diagnose | completed | success | 1608.0 | 1 | diagnostic-v4-otel-training-checkpoint-40742060084 |
| 40738379291 | evidence | c52bad2b87061ee281bf9eed547aa31312a692a0 | completed | success | 122993009204 | report | completed | success | 192.0 | 1 | report-v4-40738379291 |
| 40704387111 | evidence | c54708071e7756e0fd7577ee3cd0f57db1977e81 | completed | success | 122872446899 | archive | completed | success | 29.0 | 0 | none |
| 40734810232 | evidence | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122980379408 | archive | completed | success | 107.0 | 0 | none |
| 40739554089 | evidence | 0b04f733a5149a01a014a02a05ff6004a03c810c | completed | failure | 122997131896 | archive | completed | failure | 18.0 | 0 | none |
| 40740761225 | evidence | c0ce3e4a21c53e6586d93e08530836bc2a2e4f7d | completed | success | 123001415425 | archive | completed | success | 30.0 | 0 | none |
| 40745651023 | evidence | e15b6d1072492b9c84a530571e31b06ae602edd0 | completed | success | 123018612769 | archive | completed | success | 126.0 | 0 | none |
| 40751134324 | evidence | a839a94fe38d2c347f4156c528367bbef9d21116 | completed | success | 123037791813 | report | completed | success | 238.0 | 1 | report-v4-40751134324 |
| 40751164118 | evidence | a839a94fe38d2c347f4156c528367bbef9d21116 | completed | success | 123037905319 | archive | completed | success | 256.0 | 0 | none |
| 40753100009 | evidence | a839a94fe38d2c347f4156c528367bbef9d21116 | completed | success | 123044730417 | archive | completed | success | 14.0 | 0 | none |
| 40777355932 | evidence | 0b035db4586e489717482a680c618c73c3e321ec | completed | success | 123129987878 | archive | completed | success | 85.0 | 0 | none |
| 40778455040 | replay | 5d1d3f35951fe99753c17cbdd80d53d7b9d8f877 | completed | success | 123133734784 | diagnose | completed | success | 3210.0 | 1 | diagnostic-v4-otel-large-checkpoint-gc-40778455040 |
| 40780918812 | replay | 65843e5e5a387e40b19547bcae06c87e657911af | completed | failure | 123142098669 | diagnose | completed | failure | 5232.0 | 0 | none |
| 40784827755 | evidence | aff2b9d0c8eee2be364bab181910477105f0b3fc | completed | success | 123155280478 | archive | completed | success | 214.0 | 0 | none |
| 40785555784 | evidence | 7dc4ea23613525f909084f0d4fb28be5c4f014c1 | completed | success | 123157729442 | archive | completed | success | 77.0 | 0 | none |
| 40653952677 | evidence | 7e8deb9dfeb78723d87b254a3384bef735464d81 | completed | success | 122700372746 | checks | completed | success | 22.0 | 0 | none |
| 40655548976 | evidence | fd13e22ac28322420472f85929e146fee3455dff | completed | success | 122705588073 | checks | completed | success | 24.0 | 0 | none |
| 40658470818 | evidence | 6810aed19ceb7ebc5dfe790aa4c9ae1f3dde527e | completed | success | 122715233133 | checks | completed | success | 23.0 | 0 | none |
| 40661005833 | evidence | 12954418b8413d07b09fc808f3e5762ab5d249b7 | completed | success | 122723717635 | checks | completed | success | 29.0 | 0 | none |
| 40663736496 | evidence | 35991503ecfca76dd66719d96a750333adfa95be | completed | success | 122732892918 | checks | completed | success | 27.0 | 0 | none |
| 40667801775 | evidence | 05b5510cb168f4f4d4d86af2379d7411deaf6d3b | completed | success | 122746649356 | checks | completed | success | 26.0 | 0 | none |
| 40668009770 | evidence | 9311c1021e853ad58f33ad8b1f953db27b709691 | completed | success | 122747356368 | checks | completed | success | 25.0 | 0 | none |
| 40668187874 | evidence | 1d3a7bdde7e280ed7fae0e0c2ebb7928ab43f570 | completed | success | 122747965060 | checks | completed | success | 25.0 | 0 | none |
| 40669037976 | evidence | f30e6f77fe59e986f6ecf901f23a7280c81f713a | completed | failure | 122750823853 | checks | completed | failure | 26.0 | 0 | none |
| 40669537390 | evidence | 3dd2f510350673b55514a18ef9124f6b66c70b0f | completed | success | 122752513418 | checks | completed | success | 24.0 | 0 | none |
| 40669684799 | evidence | ddee9b669dd02e1afff1e487e6e650db875f8aef | completed | success | 122753005100 | checks | completed | success | 25.0 | 0 | none |
| 40674218814 | evidence | 642f61f5e2a395e45f2c7c8344e26b276723ae9c | completed | success | 122768389827 | checks | completed | success | 24.0 | 0 | none |
| 40674464484 | evidence | 2b72cd73d7fdb88c3dfa7f51a34e073b6e83d0b8 | completed | success | 122769227332 | checks | completed | success | 24.0 | 0 | none |
| 40704172324 | evidence | c54708071e7756e0fd7577ee3cd0f57db1977e81 | completed | success | 122871679032 | checks | completed | success | 31.0 | 0 | none |
| 40704617133 | evidence | fdec1a6fcc20317c40f834a9342d17118b5fcdff | completed | success | 122873248536 | checks | completed | success | 28.0 | 0 | none |
| 40704891608 | evidence | fd647ebf42f1f41765c43e1b7eb2aefad9038a79 | completed | success | 122874228829 | checks | completed | success | 34.0 | 0 | none |
| 40705563363 | evidence | 27186e41a47bb8482278a06f9c680b6f9d4a9ee8 | completed | success | 122876601277 | checks | completed | success | 32.0 | 0 | none |
| 40706520728 | evidence | 4486d0c1143ee6476506ffb18bb41a2850035938 | completed | success | 122880027527 | checks | completed | success | 28.0 | 0 | none |
| 40707989860 | evidence | 5045bbd602fd8d5671a766de232f51c4988d51db | completed | success | 122885200852 | checks | completed | success | 34.0 | 0 | none |
| 40711625088 | evidence | 969bdfeb16ae123dfd2390f18dca40f2a14fe1d3 | completed | success | 122898143105 | checks | completed | success | 25.0 | 0 | none |
| 40714538768 | evidence | 14a230f816369abe6101a94a2782321b3ceedc1f | completed | success | 122908512471 | checks | completed | success | 24.0 | 0 | none |
| 40718306225 | evidence | ea2e278e50f64bd50597c243d84f834be1b92576 | completed | success | 122921936758 | checks | completed | success | 31.0 | 0 | none |
| 40718840512 | evidence | 2b9c764002c7a17ab21f6dd16c5d50f9c8f5f217 | completed | success | 122923860021 | checks | completed | success | 32.0 | 0 | none |
| 40719440646 | evidence | 65c42b667d66407de28be29c8fe65a8f0572c395 | completed | success | 122925986076 | checks | completed | success | 25.0 | 0 | none |
| 40719840460 | evidence | 18d4e8db417c6a2bdfa8e156736aac83e3015395 | completed | success | 122927410300 | checks | completed | success | 31.0 | 0 | none |
| 40720633599 | evidence | 111a2e7aa22483c8dc65958b24a58176fd5c225a | completed | success | 122930234027 | checks | completed | success | 33.0 | 0 | none |
| 40722266989 | evidence | 105c7e11de28e10a4aa5ce3dc6970ea89b124b15 | completed | success | 122936052312 | checks | completed | success | 30.0 | 0 | none |
| 40726719204 | evidence | 9abab2594dfe6cdac1c48812d172306f999e7391 | completed | success | 122951850982 | checks | completed | success | 31.0 | 0 | none |
| 40730137143 | evidence | 3e708879889eac8a238027a4640466fc8a76eca5 | completed | success | 122963896612 | checks | completed | success | 33.0 | 0 | none |
| 40731360062 | evidence | 4276ea92c3eea897df27be7a65846238847bdfea | completed | success | 122968250839 | checks | completed | success | 43.0 | 0 | none |
| 40735306394 | evidence | c5f6285e528d894c33081aeb320f2ced8b96374f | completed | success | 122982126464 | checks | completed | success | 35.0 | 0 | none |
| 40737717063 | evidence | 2181e5fef0d2600a4fa17f2ada083bfd47e36446 | completed | success | 122990655671 | checks | completed | success | 39.0 | 0 | none |
| 40738224062 | evidence | c52bad2b87061ee281bf9eed547aa31312a692a0 | completed | success | 122992444933 | checks | completed | success | 30.0 | 0 | none |
| 40738952465 | evidence | 39f869ee6fe11de8c731d448c7123a381ee7b8e2 | completed | success | 122994998029 | checks | completed | success | 36.0 | 0 | none |
| 40739309766 | evidence | 0b04f733a5149a01a014a02a05ff6004a03c810c | completed | success | 122996254786 | checks | completed | success | 31.0 | 0 | none |
| 40740119846 | evidence | 5edbe1550118b9f047f466148f6d29b8435c9943 | completed | success | 122999129573 | checks | completed | success | 40.0 | 0 | none |
| 40740243461 | evidence | c0ce3e4a21c53e6586d93e08530836bc2a2e4f7d | completed | success | 122999557282 | checks | completed | success | 46.0 | 0 | none |
| 40740955249 | evidence | 4108fa72da0057a04601581240407d708d362be1 | completed | success | 123002103517 | checks | completed | success | 42.0 | 0 | none |
| 40741180198 | evidence | 2249b2b36bfc602dfe4c5e5b485e8d7446a743c3 | completed | success | 123002861709 | checks | completed | success | 33.0 | 0 | none |
| 40741796026 | evidence | 0c75e0d874907b99007a1f1a0d12f29f5331ad3a | completed | success | 123005032374 | checks | completed | success | 34.0 | 0 | none |
| 40742178560 | evidence | 6c2495c24306ca7b71a350eebab6aeaa83a7890e | completed | success | 123006384989 | checks | completed | success | 37.0 | 0 | none |
| 40743151740 | evidence | ded8be2df255762849c4948d6c15a9771131e447 | completed | success | 123009816960 | checks | completed | success | 43.0 | 0 | none |
| 40744281428 | evidence | e15b6d1072492b9c84a530571e31b06ae602edd0 | completed | success | 123013800286 | checks | completed | success | 41.0 | 0 | none |
| 40747621820 | evidence | 81b9ec370c786d5df2f8bdf0db554af58f65a2fc | completed | success | 123025503307 | checks | completed | success | 43.0 | 0 | none |
| 40749523012 | evidence | a839a94fe38d2c347f4156c528367bbef9d21116 | completed | success | 123032150073 | checks | completed | success | 40.0 | 0 | none |
| 40753750042 | evidence | 4465065a9c25680efc72848356e4cdd0e6fe662e | completed | success | 123047004567 | checks | completed | success | 33.0 | 0 | none |
| 40754244720 | evidence | 72133c00df3f7e4150a3f737dee33e4bee12527d | completed | success | 123048768633 | checks | completed | success | 41.0 | 0 | none |
| 40754659027 | evidence | 710c28470b400247cebb7430b39d0f599034ca9a | completed | success | 123050250413 | checks | completed | success | 45.0 | 0 | none |
| 40765148985 | evidence | 1c269565299705ea6a03487fb5af4d990869f36b | completed | success | 123087177772 | checks | completed | success | 43.0 | 0 | none |
| 40765657304 | evidence | 91f104be1b937425a369750ea22bfab06a9f806f | completed | success | 123088981409 | checks | completed | success | 50.0 | 0 | none |
| 40766877503 | evidence | 78473292e062299719ea263d0035fa30c3990d42 | completed | success | 123093268449 | checks | completed | success | 48.0 | 0 | none |
| 40769620673 | evidence | 0b035db4586e489717482a680c618c73c3e321ec | completed | success | 123102972978 | checks | completed | success | 36.0 | 0 | none |
| 40778021968 | evidence | da1490a1f27858ab1608929907d8b7fa6ac4a78c | completed | success | 123132248610 | checks | completed | success | 40.0 | 0 | none |
| 40778217106 | evidence | 0b0725c65e6ef2efed40ec1c0744791008f8b861 | completed | success | 123132919841 | checks | completed | success | 39.0 | 0 | none |
| 40778323259 | evidence | 5d1d3f35951fe99753c17cbdd80d53d7b9d8f877 | completed | success | 123133281547 | checks | completed | success | 32.0 | 0 | none |
| 40778574829 | evidence | cbf6154c9c310c431a13c46e525314759f7cd62e | completed | success | 123134123755 | checks | completed | success | 39.0 | 0 | none |
| 40779398938 | evidence | d99862bf02189b4125bc708443b80f441f240e7a | completed | success | 123136927042 | checks | completed | success | 37.0 | 0 | none |
| 40779630505 | evidence | 27dd242541eb796aa28036797d33d6bebe539d75 | completed | success | 123137705786 | checks | completed | success | 33.0 | 0 | none |
| 40780702510 | evidence | 65843e5e5a387e40b19547bcae06c87e657911af | completed | success | 123141367953 | checks | completed | success | 44.0 | 0 | none |
| 40781020613 | evidence | 75c85f43670ea25ac33f3b1fe00806525849d5ab | completed | success | 123142429744 | checks | completed | success | 44.0 | 0 | none |
| 40781856208 | evidence | 017bfba4eeadd9cd7682392e993ae17e07818ed3 | completed | success | 123145248104 | checks | completed | success | 42.0 | 0 | none |
| 40782767000 | evidence | aff2b9d0c8eee2be364bab181910477105f0b3fc | completed | success | 123148325002 | checks | completed | success | 36.0 | 0 | none |
| 40785125918 | evidence | 7dc4ea23613525f909084f0d4fb28be5c4f014c1 | completed | success | 123156273692 | checks | completed | success | 37.0 | 0 | none |
| 40785779972 | evidence | a0e7644362a4e1ac5913f33f06a9570f2a780000 | completed | success | 123158484014 | checks | completed | success | 29.0 | 0 | none |
| 40787442630 | evidence | a4cf57aa91e7ce17791531baef5447171a9072d4 | completed | success | 123164054957 | checks | completed | success | 42.0 | 0 | none |
| 40789168167 | evidence | 561854b3662fde45a2c1b02a8d42474204d45010 | completed | success | 123169796090 | checks | completed | success | 43.0 | 0 | none |
| 40791085245 | evidence | 98fa033539df8f82bc05f1fb724049579ad41b4d | completed | success | 123176194482 | checks | completed | success | 41.0 | 0 | none |
| 40791837386 | evidence | 98fa033539df8f82bc05f1fb724049579ad41b4d | completed | success | 123178693122 | archive | completed | success | 22.0 | 0 | none |
| 40794474890 | evidence | abb499144a639b34a7df0a05d27cc385d04f7c32 | completed | success | 123187459626 | checks | completed | success | 37.0 | 0 | none |
| 40798747501 | evidence | aa815a7eeb70ff71fd3d3829a55230d1471d6378 | completed | success | 123201471658 | checks | completed | success | 30.0 | 0 | none |
| 40798982219 | evidence | fa2c454eaa5cca1a20a534ceb6e72ab64f8f8af3 | completed | success | 123202249470 | checks | completed | success | 48.0 | 0 | none |
| 40799411526 | replay | fa2c454eaa5cca1a20a534ceb6e72ab64f8f8af3 | completed | success | 123203644634 | diagnose | completed | success | 8576.0 | 3 | diagnostic-v4-dsb-checkpoint-batch-40799411526, diagnostic-summary-v4-dsb-batch-40799411526, diagnostic-packaging-v4-dsb-batch-40799411526 |
| 40800562445 | evidence | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123207392138 | checks | completed | success | 37.0 | 0 | none |
| 40802785036 | evidence | 19ad30ea772ae5430432e2e05339a8c0d9fe0d1f | completed | success | 123214555948 | archive | completed | success | 159.0 | 0 | none |
| 40806001392 | evidence | 37b58a898bc77225990173f0d40d59ce61a114d6 | completed | success | 123224993090 | checks | completed | success | 60.0 | 0 | none |
| 40806331798 | evidence | c92869b66ed5fa13a1b6a3fd2c4d17f542b5d4c0 | completed | success | 123226050193 | checks | completed | success | 37.0 | 0 | none |
| 40808225905 | evidence | cc29856db66f96b97bedb60d4c7944264be4b22f | completed | success | 123232144066 | checks | completed | success | 35.0 | 0 | none |
| 40819158479 | evidence | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123267281930 | checks | completed | success | 33.0 | 0 | none |
| 40819375950 | replay | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123267990494 | compare | completed | success | 836.0 | 3 | native-batch-packaging-v4-40819375950, native-batch-full-v4-40819375950, native-batch-summary-v4-40819375950 |
| 40819411131 | evidence | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123268098950 | archive | completed | success | 131.0 | 0 | none |
| 40819413737 | evidence | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123268108404 | archive | completed | success | 323.0 | 0 | none |
| 40819771129 | evidence | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123269256770 | archive | completed | success | 267.0 | 0 | none |
| 40819773522 | evidence | 1ba67d0d6014bc905b82fe2425af48a5a994f264 | completed | success | 123269264465 | archive | completed | success | 421.0 | 0 | none |
| 40821512930 | evidence | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123274816468 | checks | completed | success | 33.0 | 0 | none |
| 40821883662 | evidence | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123275991677 | archive | completed | success | 51.0 | 0 | none |
| 40830558372 | evidence | febf1a7cb7ad4e29d8e5d0edf504cf45b99c940b | completed | success | 123303554028 | archive | completed | success | 54.0 | 0 | none |
| 40833189416 | evidence | 1406e559d8d8f432179116460b33f118f666550f | completed | success | 123311839231 | checks | completed | success | 44.0 | 0 | none |
| 40841674653 | evidence | 1406e559d8d8f432179116460b33f118f666550f | completed | success | 123339289399 | archive | completed | success | 2432.0 | 0 | none |
| 40845311645 | evidence | 1406e559d8d8f432179116460b33f118f666550f | completed | success | 123351238695 | archive | completed | success | 1227.0 | 0 | none |
| 40850799564 | evidence | 1406e559d8d8f432179116460b33f118f666550f | in_progress | unknown | 123369473339 | archive | in_progress | unknown | unknown | 0 | none |
| 40852591158 | evidence | 1406e559d8d8f432179116460b33f118f666550f | in_progress | unknown | 123375514494 | archive | in_progress | unknown | unknown | 0 | none |

## Original artifact availability

This is retrieval status, not a scientific verdict. Worker-only runs need not contain cell summaries. A compact summary whose full artifact is pending or unavailable is retained at its original Actions location and excluded from scientific aggregation; its run metadata and costs remain in this report.

| Run | Compact artifact | Retrieval status |
| --- | --- | --- |
| 40704758284 | not uploaded | not_uploaded |
| 40718665137 | not uploaded | not_uploaded |
| 40718674400 | v4-summary-petclinic-full-6-40718674400 | downloaded |
| 40731158179 | not uploaded | not_uploaded |
| 40733841068 | v4-summary-petclinic-absent-8-40733841068 | downloaded |
| 40733841068 | v4-summary-petclinic-absent-7-40733841068 | downloaded |
| 40733841068 | v4-summary-petclinic-absent-6-40733841068 | downloaded |
| 40733846961 | v4-summary-petclinic-partial-8-40733846961 | downloaded |
| 40733846961 | v4-summary-petclinic-partial-7-40733846961 | downloaded |
| 40733846961 | v4-summary-petclinic-partial-6-40733846961 | downloaded |
| 40733852492 | v4-summary-petclinic-full-7-40733852492 | downloaded |
| 40733858113 | v4-summary-petclinic-full-8-40733858113 | downloaded |
| 40754529169 | v4-summary-otel_demo-full-6-40754529169 | downloaded |
| 40764150238 | not uploaded | not_uploaded |
| 40786403012 | v4-summary-otel_demo-full-6-40786403012 | downloaded |
| 40792026316 | not uploaded | not_uploaded |
| 40803782214 | v4-summary-otel_demo-absent-7-40803782214 | downloaded |
| 40803782214 | v4-summary-otel_demo-absent-6-40803782214 | downloaded |
| 40803782214 | v4-summary-otel_demo-absent-8-40803782214 | downloaded |
| 40803790289 | v4-summary-otel_demo-partial-7-40803790289 | downloaded |
| 40803790289 | v4-summary-otel_demo-partial-6-40803790289 | downloaded |
| 40803790289 | v4-summary-otel_demo-partial-8-40803790289 | downloaded |
| 40803798632 | v4-summary-otel_demo-full-7-40803798632 | downloaded |
| 40803806299 | v4-summary-otel_demo-full-8-40803806299 | downloaded |
| 40808413535 | not uploaded | not_uploaded |
| 40808520837 | not uploaded | not_uploaded |
| 40808661139 | not uploaded | not_uploaded |
| 40808666481 | not uploaded | not_uploaded |
| 40808735563 | not uploaded | not_uploaded |
| 40808806603 | not uploaded | not_uploaded |
| 40808834064 | not uploaded | not_uploaded |
| 40808888799 | not uploaded | not_uploaded |
| 40821198727 | v4-summary-deathstarbench-full-6-40821198727 | downloaded |
| 40821214009 | v4-summary-deathstarbench-absent-7-40821214009 | downloaded |
| 40821214009 | v4-summary-deathstarbench-absent-8-40821214009 | downloaded |
| 40821214009 | v4-summary-deathstarbench-absent-6-40821214009 | downloaded |
| 40821232082 | v4-summary-deathstarbench-partial-7-40821232082 | downloaded |
| 40821232082 | v4-summary-deathstarbench-partial-8-40821232082 | downloaded |
| 40821232082 | v4-summary-deathstarbench-partial-6-40821232082 | downloaded |
| 40821255620 | v4-summary-deathstarbench-full-7-40821255620 | downloaded |
| 40821277823 | v4-summary-deathstarbench-full-8-40821277823 | downloaded |
| 40827363136 | not uploaded | not_uploaded |
| 40827566298 | not uploaded | not_uploaded |
| 40829685696 | not uploaded | not_uploaded |
| 40831271725 | not uploaded | not_uploaded |
| 40831685820 | not uploaded | not_uploaded |
| 40832082212 | not uploaded | not_uploaded |
| 40832412304 | not uploaded | not_uploaded |
| 40833191329 | not uploaded | not_uploaded |
| 40833707109 | not uploaded | not_uploaded |

[Exact retrieval records](provenance/compact-downloads.json).

## Figures

[Per-operation figures and stored values](figures/figures-v4.md).

[Fixed model example provenance](provenance/model-example.json).

![Actual Bering eBPF graph](figures/petclinic-full-6-ebpf-network_scope.svg)

Observed topology before operation/placement overlays. Every observed service and edge is retained; aliases are separate. Declared network scope and supplied entry-role interpretation are part of the input. Arrows are structural Bering output, not proof of per-request causality or shared physical identity.
