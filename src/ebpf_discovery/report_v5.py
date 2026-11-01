"""Saved-artifact-only reporting for the fixed iteration-5 collector matrix.

The reporter validates and copies evaluations produced by the source campaign.
It never invokes acquisition, fitting, graph discovery, simulation, or scoring.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any
import zlib

from .compact_transport_v5 import PROOF_SCHEMA, verified_nonmaterialized_files


COLLECTORS = ("obi", "deepflow", "coroot")
SYSTEMS = ("deathstarbench", "otel_demo", "petclinic")
MODES = ("absent", "partial", "full")
SEEDS = (6, 7, 8)
STAGES = ("smoke", "main")
EXPECTED_MAIN = {
    (collector, system, mode, seed)
    for collector in COLLECTORS
    for system in SYSTEMS
    for mode in MODES
    for seed in SEEDS
}
SOURCE_PINS = {
    "obi": {
        "source_version": "v0.15.2",
        "source_commit": None,
        "image": "otel/ebpf-instrument:v0.15.2@sha256:101b5c773ac84545cac007ce3dbaf38bfb0e7091f26e813c08d649f35dca253e",
    },
    "deepflow": {
        "source_version": "v7.2.3",
        "source_commit": "9a1219fa5cf1471ba2ec8742019661567d98002e",
        "image": "deepflowce/deepflow-agent:v7.2.3@sha256:5f72c0996fdb5008fdb8fd0524f427a895fc54c61690b26ba2cae648929ea95a",
    },
    "coroot": {
        "source_version": "1.37.0",
        "source_commit": "89a858a0ee35c4eb938b86d56f23168fb0ac7573",
        "image": "ghcr.io/coroot/coroot-node-agent:1.37.0@sha256:f360c31c5e2fa75550c0029f3c02a0e54b83831bae59201b9fe76bab2fe564b4",
    },
}

LEGACY_AGGREGATE_SCHEMA = "evaluation-v5-saved-aggregate"
REFERENCED_AGGREGATE_SCHEMA = "evaluation-v5-saved-aggregate-referenced-v1"
EVALUATION_REFERENCE_SCHEMA = "evaluation-v5-source-evaluation-reference-v1"
PAYLOAD_MANIFEST_SCHEMA = "evaluation-v5-payload-manifest-v1"

# Explicitly reviewed storage preparation; every other Git entry must match.
# These are actual source revisions, never rewritten provenance identities.
PREPARATION_ONLY_SOURCE_REVISIONS = {
    "0c98bf4520e863ab021b60d00517ee2aa49ab38e": {
        "fbbda015cefc4f11ee73f32be6ed661c70375f18": {
            ".github/workflows/series-v5.yml": "8eed6cc872652a8c13125a980a9fa5eedee2311d",
            ".github/workflows/toolchain-worker-v4.yml": "4b833fed808c6701426d758bb3b9feb84e81cfa1",
            "docs/WORKER_PACKAGING_V5.md": "48c220fcb158379a3cf6216da939eafe4a153a0b",
        },
        "13c017bf72a86a6853f93a5b8f503de199bf7865": {
            ".github/workflows/series-v5.yml": "e650edfcf90656bf06ed55fc5d824ba0c06c2381",
            ".github/workflows/toolchain-worker-v4.yml": "4b833fed808c6701426d758bb3b9feb84e81cfa1",
            "docs/WORKER_PACKAGING_V5.md": "10edeef57398fc03c7f7405e55b24f157ec67cf3",
        },
        "1d646f907d0241f25445fcfb4d07d4e0ba89d88b": {
            ".github/workflows/series-v5.yml": "5546ce9214eead4e07dae0e8ed50828153f6e6e4",
            ".github/workflows/toolchain-worker-v4.yml": "4b833fed808c6701426d758bb3b9feb84e81cfa1",
            "docs/WORKER_PACKAGING_V5.md": "c270e8e4a2fb48f6d17c4dc0a334b99743d50f94",
        },
    },
}


# This one algorithm revision has a complete actual saved-input equivalence
# proof. Keep it separate from the operational-only N/M/S registry above.
IMMUTABLE_PATH_SOURCE = {
    'anchor': '0c98bf4520e863ab021b60d00517ee2aa49ab38e',
    'revision': '06d7d52bfa4b7768a4cabf02f4e66f109b3a9492',
    'tested_source': '7df056aee51ae0113626fac9e72ca673e2515d96',
    'input_equivalence': {
        'run_id': 41255795362, 'artifact_id': 13063339858,
        'artifact_digest': 'sha256:76509b2c059e482db522b8aef5d1a7cf3a948449fb417931dc818c68118a7f2c',
        'input_files': 655, 'byte_exact_files': 647, 'entry_evidence_hashes': 18,
        'root_and_independent_actual_original_GO': True,
    },
    'changed_core_blobs': {
        'src/ebpf_discovery/raw_v4.py': '8d964d7dc969a922f9ab1701f371eed5ea190321',
        'src/ebpf_discovery/remote_toolchain_v4.py': '627d0fc8d4dc466c7bf2ec3d7b403a8616e0fe89',
        'src/ebpf_discovery/store_v5.py': '6569299a8a0a31f2ded3781433045ba303ae097a',
        'src/ebpf_discovery/toolchain_v4.py': 'b8b4c635952b5d0e72d436951df2463b38f28105',
    },
    'added_paths': {
        'docs/IMMUTABLE_PATH_PREPARATION_V5.md',
        'scripts/check-fixed-dsb-path-preparation-v5.py',
        'tests/test_fixed_path_preparation_comparison_v5.py',
    },
    'reviewed_changed_blobs': {
        '.github/workflows/diagnose-dsb-training-checkpoint-v4.yml': '7fa61ce470cc4a8ff6346dafb402ebabdb3b9d37',
        '.github/workflows/series-v5.yml': '5546ce9214eead4e07dae0e8ed50828153f6e6e4',
        '.github/workflows/toolchain-worker-v4.yml': '4b833fed808c6701426d758bb3b9feb84e81cfa1',
        'docs/IMMUTABLE_PATH_PREPARATION_V5.md': '04d2c2ce314b4547723746019cf962a7837452d1',
        'docs/WORKER_PACKAGING_V5.md': 'c270e8e4a2fb48f6d17c4dc0a334b99743d50f94',
        'scripts/check-fixed-dsb-path-preparation-v5.py': 'c0422ee45523be1954cc38422bb64d35083e8b18',
        'src/ebpf_discovery/raw_v4.py': '8d964d7dc969a922f9ab1701f371eed5ea190321',
        'src/ebpf_discovery/remote_toolchain_v4.py': '627d0fc8d4dc466c7bf2ec3d7b403a8616e0fe89',
        'src/ebpf_discovery/store_v5.py': '6569299a8a0a31f2ded3781433045ba303ae097a',
        'src/ebpf_discovery/toolchain_v4.py': 'b8b4c635952b5d0e72d436951df2463b38f28105',
        'tests/test_fixed_path_preparation_comparison_v5.py': 'cad466c8affd8f72d1611c93d6784fcb9585b079',
        'tests/test_identity_projection_v5.py': '40227ccf66fe6e118e7dd74f87f97ddbfb037c66',
        'tests/test_remote_toolchain_v4.py': 'a14d76277d9179123a912c4106cee317803c77b2',
    },
}


UPLOADED_CHECKPOINT_COPY_SOURCE = {
    'anchor': IMMUTABLE_PATH_SOURCE['anchor'],
    'revision': '8fa2a454db58af487451c9aead6477adc0ca0485',
    'tested_source': '8fa2a454db58af487451c9aead6477adc0ca0485',
    'parent_revision': IMMUTABLE_PATH_SOURCE['revision'],
    'copy_release_proof': {
        'run_id': 41278513379, 'artifact_id': 13072487567,
        'artifact_digest': 'sha256:f7323f6195125699453ca2ba86d8ba3126aeefc469eef0ad5434a3847ea9a6f0',
        'payload_files': 25180, 'logical_bytes_unlinked': 21031649232,
        'observed_disk_free_delta': 21094756352,
        'all_live_mirror_hashes_and_three_metadata_hashes_preserved': True,
        'synthetic_release_control_explicit': True,
        'root_and_independent_actual_original_GO': True,
        'new_traffic_models_or_scoring': False,
        'sufficient_future_headroom_or_six_hour_cure': False,
    },
    'changed_core_blobs': {**IMMUTABLE_PATH_SOURCE['changed_core_blobs'],
        'src/ebpf_discovery/remote_toolchain_v4.py': 'eeb42971b85bbf2f15f06660bba4f2078dce30d8'},
    'added_paths': IMMUTABLE_PATH_SOURCE['added_paths'] | {
        'docs/UPLOADED_CHECKPOINT_COPY_RELEASE_V5.md',
        'scripts/check-fixed-uploaded-checkpoint-copy-release-v5.py',
        'tests/test_uploaded_checkpoint_copy_release.py'},
    'reviewed_changed_blobs': {**IMMUTABLE_PATH_SOURCE['reviewed_changed_blobs'],
        '.github/workflows/diagnose-dsb-training-checkpoint-v4.yml': 'b17914718961afa75227a04a7fa9b1e2996f6433',
        'src/ebpf_discovery/remote_toolchain_v4.py': 'eeb42971b85bbf2f15f06660bba4f2078dce30d8',
        'docs/UPLOADED_CHECKPOINT_COPY_RELEASE_V5.md': '83f08a45f9bd5866eb126315db7b0cc8c2489dc3',
        'scripts/check-fixed-uploaded-checkpoint-copy-release-v5.py': '102825a665b8dad9f63b014181beeaa95484c208',
        'tests/test_uploaded_checkpoint_copy_release.py': 'cde25145c6ad39ecc7136d909fbac45156812348'},
}


CLOSED_FINAL_SNAPSHOT_SOURCE = {
    'anchor': IMMUTABLE_PATH_SOURCE['anchor'],
    'revision': '6eaa441c40253a18f18af76e4e599496927c1739',
    'tested_source': '6eaa441c40253a18f18af76e4e599496927c1739',
    'parent_revision': UPLOADED_CHECKPOINT_COPY_SOURCE['revision'],
    'final_snapshot_proof': {
        'run_id': 41296733012, 'artifact_id': 13079348283,
        'artifact_digest': 'sha256:5c90398d86e0a842bfcb0d6fc63152ff7f3a51d1cc487f89a5c7d375d4eda2e4',
        'source_run': 41273434210, 'source_artifact': 13073478195,
        'source_archive_digest': 'sha256:02c499bca37d3e5d91299234840cedf2132f499e16cee77fb1e5b6ee70b9ba99',
        'node_logical_bytes': {'a': 1170778914, 'b': 117539976},
        'same_initial_image_source_free_inodes_and_root_uid': True,
        'roomy_original_copy_succeeded': True,
        'tight_original_copy_ENOSPC_both_nodes': True,
        'tight_closed_links_full_bytes_and_original_manifest_identical': True,
        'source_paths_bytes_and_modes_preserved': True,
        'snapshot_target_mode_matches_source_not_original_copy_0600': True,
        'final_directory_and_manifest_allocation_bytes_per_node': 8192,
        'closed_replay_of_retained_live_prefix_only': True,
        'root_and_independent_actual_original_GO': True,
        'lost_final_source_reconstructed': False,
        'new_traffic_models_or_scoring': False,
        'whole_case_headroom_zero_loss_or_six_hour_cure': False,
    },
    'changed_core_blobs': {**UPLOADED_CHECKPOINT_COPY_SOURCE['changed_core_blobs'],
        'src/ebpf_discovery/deepflow_snapshot_v5.py': '2d98f55e43956f3a95f59df118348ef495e9f1e1',
        'src/ebpf_discovery/deepflow_v5.py': 'ce4bc3c7e17d3d65c06a7330866b431205d21d49'},
    'added_paths': UPLOADED_CHECKPOINT_COPY_SOURCE['added_paths'] | {
        'scripts/check-fixed-deepflow-final-links-v5.py'},
    'reviewed_changed_blobs': {**UPLOADED_CHECKPOINT_COPY_SOURCE['reviewed_changed_blobs'],
        '.github/workflows/diagnose-dsb-training-checkpoint-v4.yml': 'dbe6ec78dfd9ba05a846190b727152e4d685bac6',
        'scripts/check-fixed-deepflow-final-links-v5.py': '5560fc0ac9212a5e87e8fda752f83f98ad128f02',
        'src/ebpf_discovery/deepflow_snapshot_v5.py': '2d98f55e43956f3a95f59df118348ef495e9f1e1',
        'src/ebpf_discovery/deepflow_v5.py': 'ce4bc3c7e17d3d65c06a7330866b431205d21d49',
        'tests/test_deepflow_snapshot_v5.py': 'a2923cb9982632af8007260121b2730b536f45f9',
        'tests/test_deepflow_v5.py': '14fde390228e054cc80fc26c3e211a3196b2c7df'},
}


# Exact lossless proof encoding and duplicate lifetime; inherited proofs keep their sources.
STREAMED_CHECKPOINT_SOURCE = {'anchor': '0c98bf4520e863ab021b60d00517ee2aa49ab38e',
 'revision': 'f7ba801d70f9d2327031efc6dd0c00b90d252708',
 'tested_source': 'f7ba801d70f9d2327031efc6dd0c00b90d252708',
 'parent_revision': 'c1369df7b579f9a4c73e9ebc7df63a9d6eef6349',
 'storage_lifetime_proof': {'tested_source': 'c1369df7b579f9a4c73e9ebc7df63a9d6eef6349',
                            'run_id': 41313534176,
                            'guest_artifact_id': 13086567672,
                            'guest_artifact_digest': 'sha256:8ad34a716dec8058edc1282831c95aa57830b7d88248e373ce07cf7396f2ba64',
                            'guest_duplicate_logical_bytes_released': 1288318890,
                            'parent_artifact_id': 13088581221,
                            'parent_artifact_digest': 'sha256:2874bddabdde57d630094b7f101a614cb2d80d6495ddec6e6cfca0bc58147acd',
                            'parent_duplicate_logical_bytes_released': 27340802393,
                            'parent_preserved_payload_files': 86527,
                            'original_bytes_and_logical_SQL_proofs_preserved': True,
                            'guest_whole_blobs_and_parent_release_functions_inherited_exactly': True,
                            'parent_entire_remote_module_identical': False,
                            'root_and_independent_actual_original_GO': True,
                            'whole_case_headroom_or_six_hour_cure': False},
 'proof_encoding_equivalence': {'run_id': 41321994264,
                                'artifact_id': 13091257133,
                                'artifact_digest': 'sha256:98c424d47bfdf19b75574137555907cde3fb45d47a07785cd536c7f4b7dbf1aa',
                                'source_run': 41273870033,
                                'source_artifact': 13075276795,
                                'source_archive_digest': 'sha256:22d706c5099c16203cef5f407273a067042a1def970ab4e3d72d3e362422d555',
                                'original_manifest_sha256': '5aad17e431831e4deb7a046af03fdf8b39249e89ade6b67c86c87dabfc745749',
                                'ordered_equal_records': 828668,
                                'original_payload_files': 86527,
                                'canonical_ordered_records_sha256': '4f6c9fab3163f82f34876e280561392b9e382bc0368318d538a6f27e3a14fd6a',
                                'every_original_file_and_logical_SQL_proof_equal': True,
                                'current_and_legacy_validators_pass': True,
                                'converted_artifact_controls_explicit': True,
                                'original_array_manifest_bytes': 1037316434,
                                'new_manifest_bytes': 51225433,
                                'retained_JSONL_bytes': 792183147,
                                'old_new_arm_maxRSS_KiB': [3036364, 751636],
                                'timing_order_pagecache_extra_legacy_validation_and_cleanup_limits_retained': True,
                                'root_and_independent_actual_original_GO': True,
                                'new_traffic_models_or_scoring': False,
                                'whole_case_headroom_or_six_hour_cure': False},
 'changed_core_blobs': {'src/ebpf_discovery/checkpoint_v4.py': '50d7db510f5ee75c3485133b046df223b77baa74',
                        'src/ebpf_discovery/deepflow_snapshot_v5.py': 'bc645c0b924f093740de819f51c33470e145afe6',
                        'src/ebpf_discovery/deepflow_v5.py': 'b8bf9e39c0969da18a39e39522e0b3293db24526',
                        'src/ebpf_discovery/raw_v4.py': '8d964d7dc969a922f9ab1701f371eed5ea190321',
                        'src/ebpf_discovery/remote_toolchain_v4.py': '612948d7f7926357d1b77404d5191230ac1e8865',
                        'src/ebpf_discovery/store_v5.py': '6569299a8a0a31f2ded3781433045ba303ae097a',
                        'src/ebpf_discovery/toolchain_v4.py': 'b8b4c635952b5d0e72d436951df2463b38f28105'},
 'added_paths': {'docs/IMMUTABLE_PATH_PREPARATION_V5.md',
                 'docs/UPLOADED_CHECKPOINT_COPY_RELEASE_V5.md',
                 'scripts/check-fixed-deepflow-final-links-v5.py',
                 'scripts/check-fixed-dsb-path-preparation-v5.py',
                 'scripts/check-fixed-early-checkpoint-release-v5.py',
                 'scripts/check-fixed-guest-prefix-release-v5.py',
                 'scripts/check-fixed-runtime-proof-jsonl-v5.py',
                 'scripts/check-fixed-uploaded-checkpoint-copy-release-v5.py',
                 'tests/test_fixed_path_preparation_comparison_v5.py',
                 'tests/test_uploaded_checkpoint_copy_release.py'},
 'reviewed_changed_blobs': {'.github/workflows/diagnose-dsb-training-checkpoint-v4.yml': '105bb8fd738f5956f3e942741ba574e93d01617d',
                            '.github/workflows/series-v5.yml': '5546ce9214eead4e07dae0e8ed50828153f6e6e4',
                            '.github/workflows/toolchain-worker-v4.yml': '4b833fed808c6701426d758bb3b9feb84e81cfa1',
                            'docs/IMMUTABLE_PATH_PREPARATION_V5.md': '04d2c2ce314b4547723746019cf962a7837452d1',
                            'docs/UPLOADED_CHECKPOINT_COPY_RELEASE_V5.md': '83f08a45f9bd5866eb126315db7b0cc8c2489dc3',
                            'docs/WORKER_PACKAGING_V5.md': 'c270e8e4a2fb48f6d17c4dc0a334b99743d50f94',
                            'scripts/check-fixed-deepflow-final-links-v5.py': '5560fc0ac9212a5e87e8fda752f83f98ad128f02',
                            'scripts/check-fixed-dsb-path-preparation-v5.py': 'c0422ee45523be1954cc38422bb64d35083e8b18',
                            'scripts/check-fixed-early-checkpoint-release-v5.py': '4a2eea6d8d99027ed082f48527bc66a004b1fc01',
                            'scripts/check-fixed-guest-prefix-release-v5.py': '5444be2c8232a51e7461cc8109f69c30ab9f2aa7',
                            'scripts/check-fixed-runtime-proof-jsonl-v5.py': '7b6e494de4b78b144790f281573e22d0b4c1f1d0',
                            'scripts/check-fixed-uploaded-checkpoint-copy-release-v5.py': '102825a665b8dad9f63b014181beeaa95484c208',
                            'src/ebpf_discovery/checkpoint_v4.py': '50d7db510f5ee75c3485133b046df223b77baa74',
                            'src/ebpf_discovery/deepflow_snapshot_v5.py': 'bc645c0b924f093740de819f51c33470e145afe6',
                            'src/ebpf_discovery/deepflow_v5.py': 'b8bf9e39c0969da18a39e39522e0b3293db24526',
                            'src/ebpf_discovery/raw_v4.py': '8d964d7dc969a922f9ab1701f371eed5ea190321',
                            'src/ebpf_discovery/remote_toolchain_v4.py': '612948d7f7926357d1b77404d5191230ac1e8865',
                            'src/ebpf_discovery/store_v5.py': '6569299a8a0a31f2ded3781433045ba303ae097a',
                            'src/ebpf_discovery/toolchain_v4.py': 'b8b4c635952b5d0e72d436951df2463b38f28105',
                            'tests/test_checkpoint_v4.py': '1f934e29aaa88cc42f57f20c87623cfb402e143a',
                            'tests/test_deepflow_snapshot_v5.py': 'd205c350ecde2035f2d4afcfd488bd48ffb17318',
                            'tests/test_deepflow_v5.py': '8963e26c652e0def46d32306bcd87447bbbf8ecc',
                            'tests/test_fixed_path_preparation_comparison_v5.py': 'cad466c8affd8f72d1611c93d6784fcb9585b079',
                            'tests/test_identity_projection_v5.py': '40227ccf66fe6e118e7dd74f87f97ddbfb037c66',
                            'tests/test_remote_toolchain_v4.py': '513ff85dc91f8915ed61f2fde348fcbc16387c10',
                            'tests/test_uploaded_checkpoint_copy_release.py': 'cde25145c6ad39ecc7136d909fbac45156812348'}}


PETCLINIC_WORKER_SOURCE = {
    **STREAMED_CHECKPOINT_SOURCE,
    'revision': '0565115511b24db1d6bbe71e98784baded772144',
    'parent_revision': STREAMED_CHECKPOINT_SOURCE['revision'],
    'reviewed_changed_blobs': {
        **STREAMED_CHECKPOINT_SOURCE['reviewed_changed_blobs'],
        '.github/workflows/series-v5.yml': '952d42a430e171319d01ab3f5d98299b1832e8bd',
        'tests/test_remote_toolchain_v4.py': 'e98a8296e1ef16b05b343ce1a5496fdc30bb53f1',
    },
    'existing_worker_placement': {
        'code_tested_source': '0565115511b24db1d6bbe71e98784baded772144',
        'CI_run_id': 41340135875,
        'CI_conclusion': 'success',
        'same_existing_PC_declaration_ToolchainV5_StoreV5_plans_and_binaries': True,
        'all_production_Python_and_app_code_identical_to_streamed_source': True,
        'existing_immutable_worker_preparation_and_GOMEMLIMIT_12GiB_retained': True,
        'same_program_and_input_equivalence_root_and_independent_original_GO': True,
        'extra_full_model_qualification_run_required': False,
        'actual_PC_worker_import_and_independent_outcomes_required_for_case_GO': True,
        'actual_PC_case_or_whole_study_success_claimed': False,
        'whole_case_speedup_or_SIGTERM_cause_proven': False,
    },
}


def _preparation_equivalence_facts(anchor, revision, anchor_tree, revision_tree):
    profile = None
    if anchor == IMMUTABLE_PATH_SOURCE['anchor']:
        if revision == IMMUTABLE_PATH_SOURCE['revision']:
            profile = IMMUTABLE_PATH_SOURCE
        elif revision == UPLOADED_CHECKPOINT_COPY_SOURCE['revision']:
            profile = UPLOADED_CHECKPOINT_COPY_SOURCE
        elif revision == CLOSED_FINAL_SNAPSHOT_SOURCE['revision']:
            profile = CLOSED_FINAL_SNAPSHOT_SOURCE
        elif revision == STREAMED_CHECKPOINT_SOURCE['revision']:
            profile = STREAMED_CHECKPOINT_SOURCE
        elif revision == PETCLINIC_WORKER_SOURCE['revision']:
            profile = PETCLINIC_WORKER_SOURCE
    algorithm = profile is not None
    approved = (profile['reviewed_changed_blobs'] if algorithm else
                PREPARATION_ONLY_SOURCE_REVISIONS.get(anchor, {}).get(revision))
    if not approved or anchor_tree.get('truncated') is not False or revision_tree.get('truncated') is not False:
        raise ValueError('unreviewed preparation source or incomplete Git tree')

    def entries(tree):
        rows = {r['path']: {k: r[k] for k in ('mode', 'type', 'sha')}
                for r in tree['tree'] if r['type'] != 'tree'}
        if len(rows) != sum(r['type'] != 'tree' for r in tree['tree']):
            raise ValueError('duplicate Git tree entry')
        return rows

    original, prepared = entries(anchor_tree), entries(revision_tree)
    if ({k: v for k, v in original.items() if k not in approved}
            != {k: v for k, v in prepared.items() if k not in approved}):
        raise ValueError('preparation revision changes scientific source or file modes')
    for path, blob in approved.items():
        added = algorithm and path in profile['added_paths']
        if ((path in original if added else path not in original) or prepared.get(path)
                != {'mode': '100644', 'type': 'blob', 'sha': blob}):
            raise ValueError('preparation revision differs from reviewed source blobs')
    if profile is STREAMED_CHECKPOINT_SOURCE or profile is PETCLINIC_WORKER_SOURCE:
        return {'anchor': anchor, 'revision': revision,
                'anchor_tree': anchor_tree['sha'], 'revision_tree': revision_tree['sha'],
                'evidence_kind': ('existing_PC_worker_execution_placement_with_inherited_lossless_checkpoint_proofs'
                                  if profile is PETCLINIC_WORKER_SOURCE else
                                  'actual_lossless_checkpoint_proof_encoding_and_storage'),
                'tested_source': profile['tested_source'],
                'parent_revision': profile['parent_revision'],
                'parent_input_equivalence_tested_source': IMMUTABLE_PATH_SOURCE['tested_source'],
                'parent_input_equivalence': IMMUTABLE_PATH_SOURCE['input_equivalence'],
                'uploaded_checkpoint_release_tested_source': UPLOADED_CHECKPOINT_COPY_SOURCE['tested_source'],
                'copy_release_proof': UPLOADED_CHECKPOINT_COPY_SOURCE['copy_release_proof'],
                'closed_final_snapshot_tested_source': CLOSED_FINAL_SNAPSHOT_SOURCE['tested_source'],
                'final_snapshot_proof': CLOSED_FINAL_SNAPSHOT_SOURCE['final_snapshot_proof'],
                'storage_lifetime_proof': profile['storage_lifetime_proof'],
                'proof_encoding_equivalence': profile['proof_encoding_equivalence'],
                **({'existing_worker_placement': profile['existing_worker_placement']}
                   if profile is PETCLINIC_WORKER_SOURCE else {}),
                'reviewed_changed_blobs': approved,
                'changed_core_blobs': profile['changed_core_blobs'],
                'identical_remaining_entries': len(set(original) - set(approved))}
    if profile is CLOSED_FINAL_SNAPSHOT_SOURCE:
        return {'anchor': anchor, 'revision': revision,
                'anchor_tree': anchor_tree['sha'], 'revision_tree': revision_tree['sha'],
                'evidence_kind': 'actual_closed_final_snapshot_storage_equivalence',
                'tested_source': profile['tested_source'],
                'parent_revision': profile['parent_revision'],
                'parent_input_equivalence_tested_source': IMMUTABLE_PATH_SOURCE['tested_source'],
                'parent_input_equivalence': IMMUTABLE_PATH_SOURCE['input_equivalence'],
                'uploaded_checkpoint_release_tested_source': UPLOADED_CHECKPOINT_COPY_SOURCE['tested_source'],
                'copy_release_proof': UPLOADED_CHECKPOINT_COPY_SOURCE['copy_release_proof'],
                'final_snapshot_proof': profile['final_snapshot_proof'],
                'reviewed_changed_blobs': approved,
                'changed_core_blobs': profile['changed_core_blobs'],
                'identical_remaining_entries': len(set(original) - set(approved))}
    if profile is UPLOADED_CHECKPOINT_COPY_SOURCE:
        return {'anchor': anchor, 'revision': revision,
                'anchor_tree': anchor_tree['sha'], 'revision_tree': revision_tree['sha'],
                'evidence_kind': 'actual_uploaded_checkpoint_copy_release',
                'tested_source': profile['tested_source'],
                'parent_revision': profile['parent_revision'],
                'parent_input_equivalence_tested_source': IMMUTABLE_PATH_SOURCE['tested_source'],
                'parent_input_equivalence': IMMUTABLE_PATH_SOURCE['input_equivalence'],
                'copy_release_proof': profile['copy_release_proof'],
                'reviewed_changed_blobs': approved,
                'changed_core_blobs': profile['changed_core_blobs'],
                'identical_remaining_entries': len(set(original) - set(approved))}
    if algorithm:
        return {'anchor': anchor, 'revision': revision,
                'anchor_tree': anchor_tree['sha'], 'revision_tree': revision_tree['sha'],
                'evidence_kind': 'actual_immutable_prefix_input_equivalence',
                'tested_source': IMMUTABLE_PATH_SOURCE['tested_source'],
                'reviewed_changed_blobs': approved,
                'changed_core_blobs': IMMUTABLE_PATH_SOURCE['changed_core_blobs'],
                'input_equivalence': IMMUTABLE_PATH_SOURCE['input_equivalence'],
                'identical_remaining_entries': len(set(original) - set(approved))}
    return {'anchor': anchor, 'revision': revision,
            'anchor_tree': anchor_tree['sha'], 'revision_tree': revision_tree['sha'],
            'approved_operational_blobs': approved,
            'identical_remaining_entries': len(original) - len(approved)}


def _read(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _stream_digest(stream) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


def _evaluation_projection(evaluation: dict[str, Any]) -> dict[str, Any]:
    """Retain only exact fields consumed by render; the reference is lossless."""
    status = evaluation.get("status") or {}
    acquisition = evaluation.get("acquisition") or {}
    cost = evaluation.get("cost") or {}
    manual = cost.get("manual_preparation") or {}
    rows = []
    row_keys = (
        "operation", "source", "variant", "available", "prediction",
        "point_prediction", "forecast_interval", "actual_target_success_counts",
        "actual_counts", "reason", "unknown_obligations", "database_unknown_reason",
        "database_fault_unknown", "assumed_satisfied_database_requirements",
    )
    for row in evaluation.get("evaluations") or []:
        rows.append({key: row[key] for key in row_keys if key in row})
    projection = {
        "status": {"status": status.get("status")},
        "smoke_technical_pass": evaluation.get("smoke_technical_pass"),
        "acquisition": {
            "valid": acquisition.get("valid"),
            "problems": acquisition.get("problems"),
        },
        "evaluations": rows,
        "cost": {
            "campaign_elapsed_seconds": cost.get("campaign_elapsed_seconds"),
            "toolchain_build_seconds": cost.get("toolchain_build_seconds"),
            "toolchain_command_seconds": cost.get("toolchain_command_seconds"),
            "manual_preparation": {
                "measured": manual.get("measured"),
                "reason": manual.get("reason"),
            },
        },
    }
    if "scientific_summaries" in evaluation:
        projection["scientific_summaries"] = evaluation["scientific_summaries"]
    encoded = json.dumps(
        projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return {**projection, "projection_sha256": hashlib.sha256(encoded).hexdigest()}


def _retain_evaluation_payload(
    source: Path, report_dir: Path, *, artifact_id: int, run_id: int,
    head_sha: str, expected_sha256: str,
) -> dict[str, Any]:
    payload_dir = report_dir / "evaluation-payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    target = payload_dir / f"{artifact_id}.evaluation-v5.json.gz"
    temporary = target.with_suffix(target.suffix + ".tmp")
    raw_digest, raw_bytes = hashlib.sha256(), 0
    with source.open("rb") as input_stream, temporary.open("wb") as output_stream:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=output_stream, compresslevel=9, mtime=0,
        ) as packed:
            while chunk := input_stream.read(1024 * 1024):
                raw_digest.update(chunk)
                raw_bytes += len(chunk)
                packed.write(chunk)
    source_sha256 = raw_digest.hexdigest()
    if source_sha256 != expected_sha256:
        temporary.unlink(missing_ok=True)
        raise ValueError(f"evaluation payload source hash changed: {source}")
    os.replace(temporary, target)
    gzip_sha256, gzip_bytes = _digest(target), target.stat().st_size
    with gzip.open(target, "rb") as restored:
        restored_sha256, restored_bytes = _stream_digest(restored)
    if (restored_sha256, restored_bytes) != (source_sha256, raw_bytes):
        raise ValueError(f"evaluation payload does not restore source bytes: {source}")
    return {
        "schema_version": EVALUATION_REFERENCE_SCHEMA,
        "path": target.relative_to(report_dir).as_posix(),
        "encoding": "gzip",
        "deterministic_gzip": {"filename": "", "mtime": 0, "compresslevel": 9},
        "source_member": "evaluation-v5.json",
        "source_sha256": source_sha256,
        "source_bytes": raw_bytes,
        "gzip_sha256": gzip_sha256,
        "gzip_bytes": gzip_bytes,
        "restore_verified": True,
        "exact_original_bytes": True,
        "artifact_id": artifact_id,
        "run_id": run_id,
        "head_sha": head_sha,
    }


def resolve_evaluation_reference(reference: dict[str, Any], aggregate_path: Path) -> dict:
    """Resolve one explicit lossless reference; legacy inline objects never enter here."""
    if (not isinstance(reference, dict)
            or reference.get("schema_version") != EVALUATION_REFERENCE_SCHEMA
            or reference.get("encoding") != "gzip"
            or reference.get("restore_verified") is not True
            or reference.get("exact_original_bytes") is not True):
        raise ValueError("invalid saved evaluation reference")
    root = Path(aggregate_path).resolve().parent
    payload = (root / str(reference.get("path", ""))).resolve()
    try:
        payload.relative_to(root)
    except ValueError as error:
        raise ValueError("saved evaluation reference escapes aggregate directory") from error
    if (not payload.is_file() or _digest(payload) != reference.get("gzip_sha256")
            or payload.stat().st_size != reference.get("gzip_bytes")):
        raise ValueError("saved evaluation payload gzip proof mismatch")
    with tempfile.TemporaryFile(mode="w+b") as restored:
        digest, size = hashlib.sha256(), 0
        with gzip.open(payload, "rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
                restored.write(chunk)
        if (size != reference.get("source_bytes")
                or digest.hexdigest() != reference.get("source_sha256")):
            raise ValueError("saved evaluation payload source proof mismatch")
        restored.seek(0)
        value = json.load(restored)
    if not isinstance(value, dict) or value.get("schema_version") != "evaluation-v5":
        raise ValueError("saved evaluation payload has wrong schema")
    return value


def _cell(row: dict[str, Any]) -> tuple[str, str, str, int]:
    value = (row.get("collector"), row.get("system"), row.get("mode"), row.get("seed"))
    if (value[0] not in COLLECTORS or value[1] not in SYSTEMS
            or value[2] not in MODES or value[3] not in SEEDS):
        raise ValueError(f"invalid v5 cell identity: {value}")
    return value  # type: ignore[return-value]


def _declarations(path: Path) -> tuple[dict[str, Any], dict[tuple[int, tuple], dict]]:
    value = _read(path)
    if not isinstance(value, dict) or value.get("schema_version") != "v5-report-declarations":
        raise ValueError("v5 report declarations have the wrong schema")
    if 'experiment_head' in value and (not isinstance(value['experiment_head'], str)
            or len(value['experiment_head']) != 40
            or any(ch not in '0123456789abcdef' for ch in value['experiment_head'])):
        raise ValueError('declared experiment_head must be a full lowercase 40-character commit SHA')
    attempts: dict[tuple[int, tuple], dict] = {}
    run_ids: set[int] = set()
    for run in value.get("attempt_runs") or []:
        repository = run.get("repository")
        if repository is not None and (
            not isinstance(repository, str) or repository.count("/") != 1
            or any(not part for part in repository.split("/"))
        ):
            raise ValueError(f"invalid attempt repository: {repository}")
        run_id = run.get("run_id")
        if type(run_id) is not int or run_id <= 0 or run_id in run_ids:
            raise ValueError("attempt run IDs must be unique positive integers")
        run_ids.add(run_id)
        collector, stage = run.get("collector"), run.get("stage")
        if collector not in COLLECTORS or stage not in STAGES:
            raise ValueError(f"invalid attempt declaration: {run}")
        cells = run.get("cells")
        if not isinstance(cells, list) or not cells:
            raise ValueError("each attempt run must declare at least one cell")
        for raw in cells:
            declared = {**raw, "collector": collector}
            identity = _cell(declared)
            if stage == "smoke" and identity[3] != 6:
                raise ValueError("smoke declarations are fixed to seed 6")
            key = (run_id, identity)
            if key in attempts:
                raise ValueError(f"duplicate declared attempt cell: {key}")
            attempts[key] = {
                "run_id": run_id, "collector": collector, "stage": stage,
                "system": identity[1], "mode": identity[2], "seed": identity[3],
                "repository": repository, "note": run.get("note"),
            }
    related_ids = set()
    roles = {"preparation", "product_ci", "worker", "wait", "report", "archive", "evidence"}
    for run in value.get("related_runs") or []:
        run_id = run.get("run_id")
        repository = run.get("repository")
        if (type(run_id) is not int or run_id <= 0 or run_id in run_ids
                or run_id in related_ids or run.get("role") not in roles
                or not isinstance(run.get("note"), str)
                or (repository is not None and (
                    not isinstance(repository, str) or repository.count("/") != 1
                    or any(not part for part in repository.split("/"))))):
            raise ValueError(f"invalid related run declaration: {run}")
        related_ids.add(run_id)
    blocked = set()
    for row in value.get("blocked_main_cells") or []:
        identity = _cell(row)
        if identity in blocked or not isinstance(row.get("reason"), str):
            raise ValueError(f"invalid blocked cell declaration: {row}")
        blocked.add(identity)
    return value, attempts


def _validate_source(folder: Path, evaluation: dict, collector: str) -> dict[str, Any]:
    path = folder / "observations" / "collector.json"
    retained = _read(path)
    if not isinstance(retained, dict):
        raise ValueError(f"saved v5 summary lacks collector provenance: {path}")
    expected = SOURCE_PINS[collector]
    for key, wanted in expected.items():
        if retained.get(key) != wanted:
            raise ValueError(f"saved collector source pin mismatch: {path}: {key}")
    acquisition = evaluation.get("acquisition") or {}
    provenance = acquisition.get("provenance") or {}
    if (retained.get("collector") != collector or provenance.get("collector") != collector
            or provenance.get("source_domain") != retained.get("source_domain")):
        raise ValueError(f"saved collector provenance mismatch: {path}")
    drain = acquisition.get("final_drain") or {}
    control = acquisition.get("positive_control") or {}
    if (drain.get("collector") != collector or control.get("collector") != collector
            or drain.get("source_version") != retained.get("source_version")):
        raise ValueError(f"saved collector technical provenance mismatch: {path}")
    return {
        "path": "observations/collector.json", "sha256": _digest(path),
        **{key: retained.get(key) for key in
           ("collector", "source_domain", "source_version", "source_commit", "image")},
    }


def _saved_summaries(
    roots: list[Path], declarations: dict[tuple[int, tuple], dict], report_dir: Path,
) -> list[dict]:
    folders = set()
    for root in roots:
        folders.update(path.parent.resolve() for path in Path(root).rglob("evaluation-manifest.json"))
    reports = []
    artifact_ids = set()
    for folder in sorted(folders):
        manifest = _read(folder / "evaluation-manifest.json")
        artifact = _read(folder / "artifact-provenance.json")
        if not isinstance(manifest, dict) or manifest.get("schema_version") != "v5-cell-summary-manifest":
            raise ValueError(f"invalid v5 summary manifest: {folder}")
        if not isinstance(artifact, dict) or type(artifact.get("artifact_id")) is not int:
            raise ValueError(f"v5 summary lacks immutable artifact identity: {folder}")
        artifact_id = artifact["artifact_id"]
        if artifact_id in artifact_ids:
            raise ValueError("duplicate v5 summary artifact ID")
        artifact_ids.add(artifact_id)
        stage = "smoke" if manifest.get("smoke") is True else "main"
        identity = _cell(manifest)
        run_id = int(manifest.get("run_id"))
        declaration = declarations.get((run_id, identity))
        if declaration is None or declaration["stage"] != stage:
            raise ValueError(f"saved summary was not declared with the same cell/stage: {folder}")
        artifact_repository = artifact.get("repository")
        if (not isinstance(artifact_repository, str)
                or artifact_repository.count("/") != 1
                or any(not part for part in artifact_repository.split("/"))
                or (declaration.get("repository") is not None
                    and artifact_repository != declaration["repository"])):
            raise ValueError(f"saved v5 artifact repository mismatch: {folder}")
        expected_name = (
            f"v5-summary-{identity[0]}-{stage}-{identity[1]}-{identity[2]}-"
            f"{identity[3]}-{run_id}"
        )
        expected_full = expected_name.replace("v5-summary-", "campaign-v5-", 1)
        if (artifact.get("name") != expected_name or artifact.get("run_id") != run_id
                or artifact.get("head_sha") != manifest.get("commit")
                or artifact.get("full_artifact_name") != expected_full
                or manifest.get("full_artifact_name") != expected_full
                or not artifact.get("digest")):
            raise ValueError(f"saved v5 artifact/run/full provenance mismatch: {folder}")
        zip_proof = artifact.get("compact_zip_verification") or {}
        if (zip_proof.get("expected_sha256") != artifact.get("digest")
                or zip_proof.get("computed_sha256") != artifact.get("digest")
                or zip_proof.get("safe_extract") is not True
                or type(zip_proof.get("received_bytes")) is not int
                or zip_proof.get("received_bytes") <= 0):
            raise ValueError(f"saved compact ZIP was not byte-verified before extraction: {folder}")
        full_available = (
            type(artifact.get("full_artifact_id")) is int
            and bool(artifact.get("full_artifact_digest"))
            and artifact.get("full_artifact_expired") is False
        )
        full_unavailable_reason = (
            None if full_available else
            "full_artifact_expired" if artifact.get("full_artifact_expired") is True else
            "full_artifact_missing" if artifact.get("full_artifact_id") is None else
            "full_artifact_provenance_incomplete"
        )
        recovery_ref = artifact.get("declared_file_recovery")
        recovery = None
        if recovery_ref is not None:
            if (not isinstance(recovery_ref, dict)
                    or recovery_ref.get("path") != "declared-file-recovery.json"
                    or not isinstance(recovery_ref.get("sha256"), str)):
                raise ValueError(f"invalid declared-file recovery reference: {folder}")
            recovery_path = folder / recovery_ref["path"]
            if (not recovery_path.is_file()
                    or _digest(recovery_path) != recovery_ref["sha256"]):
                raise ValueError(f"declared-file recovery proof mismatch: {folder}")
            recovery = _read(recovery_path)
            source = recovery.get("source") if isinstance(recovery, dict) else None
            if (not isinstance(recovery, dict)
                    or recovery.get("schema_version") != "v5-declared-file-recovery"
                    or recovery_ref.get("status") != recovery.get("status")
                    or not isinstance(source, dict)
                    or source.get("repository") != artifact_repository
                    or source.get("run_id") != run_id
                    or source.get("head_sha") != manifest.get("commit")
                    or source.get("compact_artifact_id") != artifact_id
                    or source.get("compact_artifact_name") != artifact.get("name")
                    or source.get("compact_artifact_digest") != artifact.get("digest")
                    or source.get("full_artifact_id") != artifact.get("full_artifact_id")
                    or source.get("full_artifact_name") != artifact.get("full_artifact_name")
                    or source.get("full_artifact_digest") != artifact.get(
                        "full_artifact_digest")):
                raise ValueError(f"invalid declared-file recovery proof: {folder}")
        hashes = manifest.get("files_sha256")
        if not isinstance(hashes, dict):
            raise ValueError(f"saved v5 summary lacks file hashes: {folder}")
        nonmaterialized = set()
        if zip_proof.get("schema_version") == PROOF_SCHEMA:
            nonmaterialized = verified_nonmaterialized_files(
                zip_proof, folder / "evaluation-manifest.json", artifact["digest"]
            )
        missing_declared = []
        for name, expected in hashes.items():
            target = folder / name
            if expected is None:
                if target.is_file():
                    raise ValueError(f"unexpected unhashed compact file: {target}")
            elif not target.is_file():
                if name not in nonmaterialized:
                    missing_declared.append({"name": name, "manifest_sha256": expected})
            elif _digest(target) != expected:
                raise ValueError(f"saved v5 compact hash mismatch: {target}")
        if missing_declared:
            if recovery is not None and (
                recovery.get("requested_files") != missing_declared
                or recovery.get("status") == "recovered"
            ):
                raise ValueError(f"invalid declared-file recovery proof: {folder}")
        elif recovery is not None:
            requested = recovery.get("requested_files")
            recovered = recovery.get("recovered_files")
            full_zip = (recovery.get("source") or {}).get("full_zip_verification")
            source = recovery.get("source") or {}
            full_archive = (
                Path(full_zip.get("path")) if isinstance(full_zip, dict)
                and isinstance(full_zip.get("path"), str) else None
            )
            if (recovery.get("status") != "recovered"
                    or recovery.get("nested_retention_transport_traversed") is not False
                    or not isinstance(requested, list) or not requested
                    or not isinstance(recovered, list) or len(recovered) != len(requested)
                    or not isinstance(full_zip, dict)
                    or full_zip.get("expected_digest") != artifact.get("full_artifact_digest")
                    or full_zip.get("computed_digest") != artifact.get("full_artifact_digest")
                    or type(full_zip.get("received_bytes")) is not int
                    or full_zip.get("received_bytes") <= 0
                    or full_archive is None or not full_archive.is_file()
                    or full_archive.stat().st_size != full_zip.get("received_bytes")
                    or "sha256:" + _digest(full_archive)
                    != full_zip.get("computed_digest")
                    or (type(source.get("full_artifact_size_in_bytes")) is int
                        and source.get("full_artifact_size_in_bytes")
                        != full_zip.get("received_bytes"))):
                raise ValueError(f"invalid successful declared-file recovery: {folder}")
            recovered_by_name = {row.get("name"): row for row in recovered
                                 if isinstance(row, dict)}
            if len(recovered_by_name) != len(recovered):
                raise ValueError(f"invalid successful declared-file recovery: {folder}")
            for request in requested:
                row = recovered_by_name.get(request.get("name")) if isinstance(request, dict) else None
                expected = hashes.get(request.get("name")) if isinstance(request, dict) else None
                target = folder / request.get("name") if isinstance(request, dict) else None
                target_bytes = target.read_bytes() if target is not None and target.is_file() else None
                if (not isinstance(row, dict) or expected != request.get("manifest_sha256")
                        or row.get("copied_sha256") != expected
                        or row.get("zip_member_name") != request.get("name")
                        or row.get("lineage") != "direct_full_artifact_zip_member"
                        or type(row.get("copied_bytes")) is not int
                        or target_bytes is None
                        or row.get("copied_bytes") != len(target_bytes)
                        or row.get("zip_member_file_size") != len(target_bytes)
                        or row.get("zip_member_crc32") != f"{zlib.crc32(target_bytes):08x}"
                        or type(row.get("zip_member_compress_size")) is not int
                        or row.get("zip_member_compress_size") < 0):
                    raise ValueError(f"invalid successful declared-file recovery: {folder}")
        evaluation_path = folder / "evaluation-v5.json"
        evaluation = _read(evaluation_path)
        if evaluation is None:
            reports.append({
                **declaration, "artifact": artifact, "manifest": manifest,
                "root": str(folder), "evaluation_reference": None,
                "evaluation_projection": None,
                "technical_complete_self_reported": False,
                "full_source_artifact_available": full_available,
                "full_source_artifact_reason": full_unavailable_reason,
                "eligible_main_coverage": False,
                "independently_admitted": False,
                "manifest_declared_transport_complete": not missing_declared,
                "missing_manifest_declared_files": missing_declared,
                "verified_nonmaterialized_manifest_files": sorted(nonmaterialized),
                "declared_file_recovery": recovery,
                "reason": "saved_evaluation_missing",
            })
            continue
        if hashes.get("evaluation-v5.json") != _digest(evaluation_path):
            raise ValueError(f"saved evaluation is not hash-bound: {evaluation_path}")
        if evaluation.get("schema_version") != "evaluation-v5":
            raise ValueError(f"invalid saved v5 evaluation schema: {evaluation_path}")
        status = _read(folder / "status.json")
        if not isinstance(status, dict):
            raise ValueError(f"saved v5 evaluation lacks status identity: {evaluation_path}")
        try:
            status_run_id = int(status.get("run_id"))
        except (TypeError, ValueError):
            status_run_id = None
        if (status_run_id != run_id or status.get("commit") != manifest.get("commit")
                or status.get("smoke") is not (stage == "smoke")):
            raise ValueError(f"saved v5 status run/commit/stage mismatch: {evaluation_path}")
        for key, wanted in zip(("collector", "system", "mode", "seed"), identity):
            if evaluation.get(key) != wanted or status.get(key) != wanted:
                raise ValueError(f"saved v5 evaluation identity mismatch: {evaluation_path}: {key}")
        if evaluation.get("smoke") is not (stage == "smoke"):
            raise ValueError(f"saved v5 evaluation stage mismatch: {evaluation_path}")
        if status is not None and evaluation.get("status") != status:
            raise ValueError(f"saved v5 evaluation status mismatch: {evaluation_path}")
        complete = evaluation.get("complete_for_evaluation") is True
        if evaluation.get("smoke_technical_pass") is not (stage == "smoke" and complete):
            raise ValueError(f"saved smoke verdict inconsistent with completeness: {evaluation_path}")
        if evaluation.get("primary_series_result") is not (stage == "main" and complete):
            raise ValueError(f"saved main verdict inconsistent with completeness: {evaluation_path}")
        source = _validate_source(folder, evaluation, identity[0]) if complete else None
        coverage_eligible = complete and full_available and not missing_declared
        reference = _retain_evaluation_payload(
            evaluation_path, report_dir, artifact_id=artifact_id, run_id=run_id,
            head_sha=manifest["commit"], expected_sha256=hashes["evaluation-v5.json"],
        )
        reports.append({
            **declaration, "artifact": artifact, "manifest": manifest,
            "root": str(folder), "evaluation_reference": reference,
            "evaluation_projection": _evaluation_projection(evaluation),
            "source_provenance": source,
            "technical_complete_self_reported": complete,
            "full_source_artifact_available": full_available,
            "full_source_artifact_reason": full_unavailable_reason,
            "eligible_main_coverage": coverage_eligible,
            "independently_admitted": False,
            "manifest_declared_transport_complete": not missing_declared,
            "missing_manifest_declared_files": missing_declared,
            "verified_nonmaterialized_manifest_files": sorted(nonmaterialized),
            "declared_file_recovery": recovery,
            "reason": (
                None if coverage_eligible else
                "manifest_declared_file_unavailable" if missing_declared else
                full_unavailable_reason if complete else
                "source_evaluation_technically_incomplete"
            ),
        })
    return reports


def _selection(path: Path | None, attempts: list[dict]) -> tuple[dict[tuple, int], dict]:
    if path is None:
        return {}, {"provided": False}
    value = _read(path)
    if (not isinstance(value, dict)
            or value.get("policy") != "technical_replacement_only_no_outcome_selection"):
        raise ValueError("v5 selection must assert technical-only outcome-independent replacement")
    chosen = {}
    for row in value.get("cells") or []:
        identity = _cell(row)
        if identity in chosen or type(row.get("selected_artifact_id")) is not int:
            raise ValueError(f"invalid v5 technical selection: {row}")
        candidates = [item for item in attempts
                      if item["stage"] == "main" and _cell(item) == identity]
        candidate_ids = {
            item["artifact"]["artifact_id"] for item in candidates if item.get("artifact")
        }
        candidate_runs = {item["run_id"] for item in candidates}
        declared = set(row.get("candidate_artifact_ids") or [])
        declared_runs = set(row.get("candidate_run_ids") or [])
        selected = row["selected_artifact_id"]
        complete = [item["artifact"]["artifact_id"] for item in candidates
                    if item.get("eligible_main_coverage") and item.get("artifact")]
        if (len(candidates) <= 1 or declared != candidate_ids
                or declared_runs != candidate_runs or selected not in candidate_ids
                or len(complete) != 1
                or selected != complete[0]
                or not str(row.get("reason_code", "")).startswith("technical_")):
            raise ValueError(f"invalid technical-only replacement for {identity}")
        chosen[identity] = selected
    return chosen, {"provided": True, "path": str(path.resolve()),
                    "sha256": _digest(path), "manifest": value}


def build(
    roots: list[Path], declarations_path: Path, report_dir: Path,
    *, retrieval_path: Path | None = None, selection_path: Path | None = None,
) -> dict[str, Any]:
    report_dir.mkdir(parents=True, exist_ok=True)
    declarations, declared_attempts = _declarations(declarations_path)
    reports = _saved_summaries(roots, declared_attempts, report_dir)
    by_declared = {}
    for item in reports:
        key = (item["run_id"], _cell(item))
        if key in by_declared:
            raise ValueError(f"multiple saved summaries claim the same declared run/cell: {key}")
        by_declared[key] = item
    attempts = []
    retrieval = _read(retrieval_path, []) if retrieval_path else []
    retrieval_by_key = {
        (row.get("run_id"), tuple(row.get("cell") or [])): row
        for row in retrieval if isinstance(row, dict)
    }
    for key, declaration in sorted(declared_attempts.items(), key=str):
        saved = by_declared.get(key)
        attempts.append(saved or {
            **declaration, "root": None, "artifact": None, "manifest": None,
            "evaluation_reference": None, "evaluation_projection": None,
            "technical_complete_self_reported": False,
            "manifest_declared_transport_complete": False,
            "full_source_artifact_available": False,
            "full_source_artifact_reason": "compact_artifact_not_retained",
            "eligible_main_coverage": False,
            "independently_admitted": False,
            "reason": (retrieval_by_key.get((key[0], key[1])) or {}).get(
                "status", "compact_artifact_not_retained"
            ),
        })
    common_head = declarations.get('experiment_head')
    compatible_heads = {common_head, *PREPARATION_ONLY_SOURCE_REVISIONS.get(common_head, {})}
    if common_head == IMMUTABLE_PATH_SOURCE['anchor']:
        compatible_heads.add(IMMUTABLE_PATH_SOURCE['revision'])
        compatible_heads.add(UPLOADED_CHECKPOINT_COPY_SOURCE['revision'])
        compatible_heads.add(CLOSED_FINAL_SNAPSHOT_SOURCE['revision'])
        compatible_heads.add(STREAMED_CHECKPOINT_SOURCE['revision'])
        compatible_heads.add(PETCLINIC_WORKER_SOURCE['revision'])
    for item in attempts:
        observed_head = (item.get('manifest') or {}).get('commit')
        if common_head and item['stage'] == 'main' and observed_head not in compatible_heads:
            item['common_source_coverage_exclusion'] = {
                'rule': ('outside_predeclared_common_source' if observed_head else 'source_commit_unavailable'),
                'expected_head': common_head, 'observed_head': observed_head,
                'previous_eligible_main_coverage': item['eligible_main_coverage'],
                'previous_reason': item.get('reason')}
            item['eligible_main_coverage'] = False
        item["attempt_key"] = ":".join(str(value) for value in (
            item["run_id"], item["collector"], item["stage"], item["system"],
            item["mode"], item["seed"],
        ))
    attempt_keys = [item["attempt_key"] for item in attempts]
    if len(set(attempt_keys)) != len(attempt_keys):
        raise ValueError("duplicate canonical v5 attempt key")
    selected_ids, selection = _selection(selection_path, attempts)
    grouped: dict[tuple, list[dict]] = {}
    for item in attempts:
        if item["stage"] == "main":
            grouped.setdefault(_cell(item), []).append(item)
    selected = {}
    ambiguous = []
    for identity, candidates in sorted(grouped.items()):
        complete = [item for item in candidates if item.get("eligible_main_coverage")]
        if len(candidates) == 1 and len(complete) == 1:
            selected[identity] = complete[0]
        elif len(candidates) > 1:
            artifact_id = selected_ids.get(identity)
            if artifact_id is None:
                ambiguous.append({
                    "cell": list(identity),
                    "candidate_artifact_ids": [
                        (item.get("artifact") or {}).get("artifact_id") for item in candidates
                    ],
                    "reason": "duplicate_main_cell_requires_technical_selection",
                })
            else:
                selected[identity] = next(
                    item for item in candidates
                    if (item.get("artifact") or {}).get("artifact_id") == artifact_id
                )
    blocked = {_cell(row): row["reason"] for row in declarations.get("blocked_main_cells") or []}
    undeclared_blocks = set(blocked) - EXPECTED_MAIN
    if undeclared_blocks:
        raise ValueError(f"blocked cells outside fixed main grid: {sorted(undeclared_blocks)}")
    payload_references = [
        item["evaluation_reference"] for item in attempts
        if item.get("evaluation_reference") is not None
    ]
    payload_manifest = {
        "schema_version": PAYLOAD_MANIFEST_SCHEMA,
        "payloads": sorted(payload_references, key=lambda row: row["artifact_id"]),
        "payload_count": len(payload_references),
        "claim": "exact retained source evaluation bytes; no scientific recomputation",
    }
    payload_manifest_path = report_dir / "evaluation-payload-manifest.json"
    payload_manifest_path.write_text(
        json.dumps(payload_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    result = {
        "schema_version": REFERENCED_AGGREGATE_SCHEMA,
        "input_mode": "saved_source_evaluations_no_raw_recompute",
        "declarations": declarations,
        "declarations_sha256": _digest(declarations_path),
        "retrieval": retrieval,
        "retrieval_sha256": _digest(retrieval_path) if retrieval_path else None,
        "source_pins": SOURCE_PINS,
        "source_pin_validation_scope": (
            "collector manifests only; full toolchain/input admission remains external"
        ),
        "attempts": attempts,
        "smoke_attempt_references": [
            item["attempt_key"] for item in attempts if item["stage"] == "smoke"
        ],
        "main_attempt_references": [
            item["attempt_key"] for item in attempts if item["stage"] == "main"
        ],
        "selected_main_attempt_references": [
            selected[key]["attempt_key"] for key in sorted(selected)
        ],
        "evaluation_payload_manifest": {
            "schema_version": PAYLOAD_MANIFEST_SCHEMA,
            "path": payload_manifest_path.relative_to(report_dir).as_posix(),
            "sha256": _digest(payload_manifest_path),
            "payload_count": len(payload_references),
        },
        "selection": selection,
        "ambiguous_duplicate_main_cells": ambiguous,
        "grid": {
            "declared_main_cells": len(EXPECTED_MAIN),
            "technically_complete_main_cells": len(selected),
            "blocked_main_cells": [list(key) + [blocked[key]] for key in sorted(blocked)],
            "incomplete_or_missing_main_cells": [
                list(key) for key in sorted(EXPECTED_MAIN - set(selected))
            ],
            "smoke_attempts_excluded_from_main_coverage": True,
        },
        "independent_admission": {
            "performed_by_reporter": False,
            "self_reported_technical_completeness_is_not_independent_review": True,
        },
        "claim": (
            "saved fields only; no acquisition, refit, relinking, rescoring, "
            "threshold, or positive contribution claim"
        ),
    }
    target = report_dir / "evaluation-v5.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _value(value: Any) -> str:
    if value is None:
        return "unknown"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, separators=(",", ":")).replace("|", "\\|")
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(_value(item) for item in row) + " |" for row in rows]
    if not rows:
        lines.append("| unavailable |" + " unknown |" * (len(headers) - 1))
    return lines


def _referenced_attempts(
    payload: dict[str, Any], aggregate_path: Path, field: str, *, stage: str,
) -> list[dict[str, Any]]:
    attempts = payload.get("attempts") or []
    by_key = {}
    for item in attempts:
        key = item.get("attempt_key") if isinstance(item, dict) else None
        if not isinstance(key, str) or not key or key in by_key:
            raise ValueError("invalid canonical attempt index")
        by_key[key] = item
    references = payload.get(field)
    if not isinstance(references, list) or any(not isinstance(key, str) for key in references):
        raise ValueError(f"invalid {field}")
    result = []
    seen = set()
    for key in references:
        item = by_key.get(key)
        if item is None or key in seen or item.get("stage") != stage:
            raise ValueError(f"invalid canonical attempt reference: {key}")
        seen.add(key)
        result.append(item)
    return result


def _validate_payload_manifest(payload: dict[str, Any], aggregate_path: Path) -> None:
    reference = payload.get("evaluation_payload_manifest")
    if (not isinstance(reference, dict)
            or reference.get("schema_version") != PAYLOAD_MANIFEST_SCHEMA
            or not isinstance(reference.get("path"), str)
            or not isinstance(reference.get("sha256"), str)):
        raise ValueError("invalid evaluation payload manifest reference")
    root = aggregate_path.resolve().parent
    path = (root / reference["path"]).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError("evaluation payload manifest escapes aggregate directory") from error
    manifest = _read(path)
    attempts = payload.get("attempts") or []
    expected = [item.get("evaluation_reference") for item in attempts
                if item.get("evaluation_reference") is not None]
    if (not path.is_file() or _digest(path) != reference["sha256"]
            or not isinstance(manifest, dict)
            or manifest.get("schema_version") != PAYLOAD_MANIFEST_SCHEMA
            or manifest.get("payloads") != sorted(expected, key=lambda row: row["artifact_id"])
            or manifest.get("payload_count") != len(expected)
            or reference.get("payload_count") != len(expected)):
        raise ValueError("evaluation payload manifest proof mismatch")
    for item in expected:
        payload_path = (root / str(item.get("path", ""))).resolve()
        try:
            payload_path.relative_to(root)
        except ValueError as error:
            raise ValueError("saved evaluation reference escapes aggregate directory") from error
        if (not payload_path.is_file() or payload_path.stat().st_size != item.get("gzip_bytes")
                or _digest(payload_path) != item.get("gzip_sha256")):
            raise ValueError("saved evaluation payload gzip proof mismatch")
    for attempt in attempts:
        evaluation_reference = attempt.get("evaluation_reference")
        projection = attempt.get("evaluation_projection")
        if evaluation_reference is None:
            if projection is not None:
                raise ValueError("projection exists without a source evaluation reference")
            continue
        evaluation = resolve_evaluation_reference(evaluation_reference, aggregate_path)
        if _evaluation_projection(evaluation) != projection:
            raise ValueError("saved evaluation projection does not match source payload")
        del evaluation


def _scientific_tables(attempts, schema):
    """Render source-produced summaries without reopening or rescoring raw data."""
    identity_headers = ["Run", "Collector", "System", "Mode", "Seed", "Complete"]
    failures, availability, graphs, baselines, db_counts, db_impact = [], [], [], [], [], []
    classes, persistence, cross_guest, causal_rows, causal_scope, db_identity = [], [], [], [], [], []
    for item in attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        identity = [item.get(key) for key in ("run_id", "collector", "system", "mode", "seed")]
        identity.append(item.get("technical_complete_self_reported"))
        summary = evaluation.get("scientific_summaries")
        availability.append(identity + [summary is not None,
                            "source-produced summary" if summary is not None else
                            "not retained in this historical source evaluation"])
        for row in evaluation.get("evaluations") or []:
            if row.get("available") is not True:
                failures.append(identity + [row.get("operation"), row.get("source"),
                    row.get("variant"), row.get("reason"),
                    row["unknown_obligations"] if "unknown_obligations" in row else
                    "not retained in this source evaluation"])
        if summary is None:
            continue
        for source, variants in (summary.get("graphs") or {}).items():
            for variant, operations in variants.items():
                for operation, graph in operations.items():
                    graphs.append(identity + [operation, source, variant, graph.get("available"),
                        graph.get("services"), graph.get("edges"), graph.get("endpoints"),
                        graph.get("bering_outputs_present"), graph.get("reason")])
                    db_identity.append(identity + [operation, source, variant,
                        graph.get("database_mapping"), graph.get("database_aliases"),
                        graph.get("incomplete_database_alias_count")])
        for operation, baseline in (summary.get("manual_baselines") or {}).items():
            baselines.append(identity + [operation, baseline.get("available"),
                baseline.get("prediction"), baseline.get("by_state"),
                baseline.get("primary_conditional_assumption"), baseline.get("database"),
                baseline.get("basis")])
        database = summary.get("database") or {}
        for phase in ("db_up", "db_down"):
            for operation, entry in (database.get(phase) or {}).items():
                db_counts.append(identity + [phase, operation, entry.get("counts")])
        for row in database.get("forecast_impact") or []:
            db_impact.append(identity + [row.get("operation"), row.get("source"), row.get("variant"),
                row.get("healthy_state_11_prediction"), row.get("database_down_prediction"),
                row.get("prognostic_impact"), row.get("comparison")])
        for classifier, result in (summary.get("classes") or {}).items():
            for row in result.get("class_test_metrics") or []:
                classes.append(identity + [classifier, row.get("source"), row.get("variant"),
                    row.get("total"), row.get("known"), row.get("unknown"), row.get("coverage"),
                    row.get("ari_labeled_known_subset"), row.get("ari_on_known_subset"),
                    row.get("pattern_statuses"), row.get("equivalent_to_base_family_assignment")])
        for phase, row in (summary.get("async") or {}).items():
            persistence.append(identity + [phase, row.get("available"), row.get("records"),
                row.get("states"), row.get("paused_absence_is_failure"), row.get("reason")])
        for source, row in (summary.get("cross_guest") or {}).items():
            cross_guest.append(identity + [source, row.get("exact_parent_links"),
                row.get("invalid_identity_candidates"), row.get("placement_coverage"),
                row.get("header_verdicts"), row.get("interpretation")])
        verdicts = summary.get("causal_attempt_verdicts")
        causal_scope.append(identity + [summary.get("causal_scope")])
        if verdicts is None:
            causal_rows.append(identity + [None, None, None, None,
                                          "causal attempt verdicts not retained"])
        else:
            census = {}
            for row in verdicts:
                key = (row.get("source"), row.get("phase"), row.get("four_stage_causal_chain"))
                census[key] = census.get(key, 0) + 1
            for (source, phase, verdict), count in census.items():
                causal_rows.append(identity + [source, phase, verdict, count,
                                               "census of saved verdicts; no relinking"])
    lines = ["", "## Additional saved scientific results", "",
             "Missing historical fields remain not retained. Graph presence, operation binding, "
             "simulation, independent outcomes and causal association are separate evidence.",
             "Repeated source/variant rows share external attempts and do not increase sample size."]
    tables = [
        ("Scientific detail availability", ["Details retained", "Scope"], availability),
        ("Stored unavailable obligations", ["Operation", "Source", "Variant", "Stored reason",
            "Frozen binding obligations"], failures),
        ("Actual saved Bering graph presence", ["Operation", "Source", "Variant", "Graph available",
            "Services", "Edges", "Endpoints", "Bering files present", "Reason"], graphs),
        ("Same-information direct baselines", ["Operation", "Available", "Prediction", "By state",
            "Conditional assumption", "Database baseline", "Basis"], baselines),
        ("Independent database controls", ["Phase", "Operation", "Stored outcome counts"], db_counts),
        ("Observed database identity and shared participation", ["Operation", "Source", "Variant",
            "Saved mapping checks", "Logical endpoints and callers", "Incomplete aliases"], db_identity),
        ("Saved database forecast impact", ["Operation", "Source", "Variant", "Healthy state 11",
            "DB-down prediction", "Impact", "Comparison"], db_impact),
        ("Frozen operation classification", ["Classifier", "Source", "Variant", "Total", "Known",
            "Unknown", "Coverage", "ARI labeled-known denominator", "ARI on known subset",
            "Pattern statuses", "Equivalent to base family"], classes),
        ("Independent asynchronous persistence", ["Phase", "Available", "Records", "States",
            "Paused absence treated as failure", "Reason"], persistence),
        ("Source-local cross-guest evidence", ["Source", "Exact parent links", "Invalid IDs",
            "Placement coverage", "Header verdicts", "Interpretation"], cross_guest),
        ("Saved asynchronous association verdicts", ["Source", "Phase", "Stored verdict",
            "Count", "Scope"], causal_rows),
        ("Asynchronous association scope", ["Saved scope and invalid identity count"], causal_scope),
    ]
    for title, headers, rows in tables:
        lines += ["", "### " + title, ""] + _table(identity_headers + headers, rows)
    lines += ["", "Binding obligations identify an unavailable transition, not a proven collector "
              "root cause. Direct-baseline equivalence does not invalidate feasibility. DB impact "
              "compares healthy state 11 with DB-down. Async association does not establish SQL durability.", ""]
    return lines


def render(aggregate_path: Path, out: Path, costs_path: Path | None = None) -> dict[str, Any]:
    payload = _read(aggregate_path)
    schema = payload.get("schema_version") if isinstance(payload, dict) else None
    if schema not in (LEGACY_AGGREGATE_SCHEMA, REFERENCED_AGGREGATE_SCHEMA):
        raise ValueError("report_v5 requires an evaluation-v5 saved aggregate")
    attempts = payload.get("attempts") or []
    if schema == REFERENCED_AGGREGATE_SCHEMA:
        _validate_payload_manifest(payload, aggregate_path)
        smoke_attempts = _referenced_attempts(
            payload, aggregate_path, "smoke_attempt_references", stage="smoke",
        )
        main_attempts = _referenced_attempts(
            payload, aggregate_path, "main_attempt_references", stage="main",
        )
        selected_main_attempts = _referenced_attempts(
            payload, aggregate_path, "selected_main_attempt_references", stage="main",
        )
        expected_smoke = [item for item in attempts if item.get("stage") == "smoke"]
        expected_main = [item for item in attempts if item.get("stage") == "main"]
        if smoke_attempts != expected_smoke or main_attempts != expected_main:
            raise ValueError("canonical stage references do not cover attempts in stored order")
        if any(item.get("eligible_main_coverage") is not True
               for item in selected_main_attempts):
            raise ValueError("selected main reference is not coverage eligible")
    else:
        smoke_attempts = payload.get("smoke_attempts") or []
        main_attempts = payload.get("main_attempts") or []
    costs = _read(costs_path, {}) if costs_path else {}
    if costs_path and (
        not isinstance(costs, dict) or costs.get("schema_version") != "v5-actions-costs"
    ):
        raise ValueError("report_v5 requires a v5 Actions cost ledger")
    lines = [
        "# Iteration-5 saved-artifact report", "",
        "This report copies source-produced evaluations and technical records. It performs no refit, relinking, rescoring, thresholding, or accuracy-based selection.",
        f"Technical smoke status is separate from the {(payload.get('grid') or {}).get('declared_main_cells', 'unknown')}-cell main grid and is not an independent admission or positive contribution claim.",
        "", "## Fixed grid and execution boundary", "",
    ]
    lines += _table(["Stored field", "Value"], [
        [key, value] for key, value in (payload.get("grid") or {}).items()
    ])
    if (payload.get('declarations') or {}).get('experiment_head'):
        prepared = PREPARATION_ONLY_SOURCE_REVISIONS.get(payload['declarations']['experiment_head'], {})
        boundary = ('Historical main rows remain visible; source commits outside the reviewed set do not contribute to this grid.'
                    if prepared else 'Historical main rows remain visible; other source commits do not contribute to this grid.')
        lines += ['', 'Declared common source commit: `' + payload['declarations']['experiment_head'] +
                  '`. ' + boundary]
        if prepared:
            lines += ['The reviewed runner/guest preparation revision(s) `' + '`, `'.join(prepared) +
                      '` also use this scientific implementation. The reporting workflow verifies their exact approved operational blobs and all unchanged Git entries; actual source commits remain visible in every row. See `provenance/source-equivalence.json`.']
        if payload['declarations']['experiment_head'] == IMMUTABLE_PATH_SOURCE['anchor']:
            lines += ['The separately reviewed algorithm revision `' + IMMUTABLE_PATH_SOURCE['revision'] +
                      '` changes four preparation core files. The separate record in `provenance/source-equivalence.json` verifies its exact Git entries and binds the complete saved-input proof artifact by ID and digest. Actual source and timings remain visible; shorter preparation changes guest idle age and does not identify intrinsic collector speed or causal accuracy.']
            lines += ['The exact source `' + UPLOADED_CHECKPOINT_COPY_SOURCE['revision'] +
                      '` adds verified release of an uploaded local checkpoint copy. Its separate actual cleanup proof (run 41278513379, artifact 13072487567) preserves all 25,180 physical live-mirror files and three identity files. The inherited T input-equivalence proof remains attributed to its own tested source; the cleanup is not a new model/scoring result or proof of sufficient end-to-end headroom.']
            lines += ['The exact final-retention source `' + CLOSED_FINAL_SNAPSHOT_SOURCE['revision'] +
                      '` adds shared-inode final snapshots after positive per-node producer termination. Actual storage qualification run 41296733012 (artifact 13079348283) compares the literal original copy with links on retained prefixes from both guests: identical initial filesystems, full raw bytes and original snapshot manifests. This is a closed replay of saved live prefixes, not reconstruction of the failed final source or a whole-case capacity, zero-loss or study-success claim. Original source modes remain; linked snapshot modes follow the source rather than the old copy mode 0600. T input-equivalence and U checkpoint-release proofs retain their original tested-source attribution.']
            lines += ['The exact lossless checkpoint source `' + STREAMED_CHECKPOINT_SOURCE['revision'] +
                      '` retains all 828,668 ordered audit records and all 86,527 original payload/SQL input proofs in actual qualification 41321994264 (artifact 13091257133). Its 51,225,433-byte manifest references a retained 792,183,147-byte JSONL payload. The C duplicate-lifetime proof remains attributed to source c1369df and run 41313534176; guest whole blobs and the parent release/caller functions are inherited exactly, while the remote module also adds JSONL validation. Component memory measurements and fixed-order/pagecache/extra-legacy-validation/cleanup boundaries do not establish whole-case speed, capacity or scientific success. The full exact Git profile and inherited T/U/V proofs remain in `provenance/source-equivalence.json`.']
            lines += ['The exact existing-worker source `' + PETCLINIC_WORKER_SOURCE['revision'] +
                      '` routes Petclinic models through the already implemented closed-prefix worker. All production Python, application declarations, observations, model code and binaries remain identical to f7ba801; the only producer changes are one routing line and PC atomic-import fixtures. Its source-specific Git profile and Linux CI establish this operational placement, not a new model or observed speedup. Inherited JSONL/storage qualifications retain their actual f7ba801/c1369df/T/U/V tested sources. Each PC case still requires actual retained worker import and independent outcomes.']
    lines += ["", "## Every declared attempt", ""]
    attempt_rows = []
    for item in attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        artifact = item.get("artifact") or {}
        status = evaluation.get("status") or {}
        attempt_rows.append([
            item.get("run_id"), item.get("repository"), item.get("collector"), item.get("stage"),
            item.get("system"), item.get("mode"), item.get("seed"),
            item.get("technical_complete_self_reported"),
            item.get("manifest_declared_transport_complete"),
            item.get("full_source_artifact_available"),
            item.get("eligible_main_coverage"), False,
            status.get("status"), artifact.get("artifact_id"), artifact.get("digest"),
            artifact.get("full_artifact_id"), artifact.get("full_artifact_digest"),
            item.get("reason"),
            (item.get('manifest') or {}).get('commit'), item.get('common_source_coverage_exclusion'),
        ])
    lines += _table([
        "Run", "Repository", "Collector", "Stage", "System", "Mode", "Seed",
        "Self-reported complete", "Declared transport complete",
        "Full source artifact available", "Coverage eligible", "Independently admitted",
        "Status", "Summary artifact", "Summary digest",
        "Full artifact", "Full digest", "Missing/incomplete reason",
        'Source commit', 'Common-source coverage exclusion',
    ], attempt_rows)
    lines += ["", "## Technical smoke qualification records", ""]
    smoke_rows = []
    for item in smoke_attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        acquisition = evaluation.get("acquisition") or {}
        smoke_rows.append([
            item.get("run_id"), item.get("collector"), item.get("system"), item.get("mode"),
            item.get("seed"), evaluation.get("smoke_technical_pass"),
            acquisition.get("valid"), acquisition.get("problems"), False,
        ])
    lines += _table([
        "Run", "Collector", "System", "Mode", "Seed", "Source technical pass",
        "Acquisition valid", "Stored problems", "Independent admission",
    ], smoke_rows)
    lines += ["", "## Saved main forecasts and external outcomes", ""]
    forecast_rows = []
    for item in main_attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        for row in evaluation.get("evaluations") or []:
            counts = row.get("actual_target_success_counts") or row.get("actual_counts") or {}
            forecast_rows.append([
                item.get("run_id"), item.get("collector"), item.get("system"), item.get("mode"),
                item.get("seed"), item.get("technical_complete_self_reported"),
                (item.get('manifest') or {}).get('commit'), item.get('eligible_main_coverage'),
                row.get("operation"), row.get("source"), row.get("variant"), row.get("available"),
                row.get("prediction", row.get("point_prediction")), row.get("forecast_interval"),
                counts.get("true", counts.get("success")), counts.get("false", counts.get("failure")),
                counts.get("none", counts.get("unknown")), row.get("reason"),
            ])
    lines += _table([
        "Run", "Collector", "System", "Mode", "Seed", "Complete", 'Source commit', 'Coverage eligible', "Operation", "Source",
        "Variant", "Available", "Stored forecast", "Stored interval", "Actual true",
        "Actual false", "Actual unknown", "Stored reason",
    ], forecast_rows)
    lines += _scientific_tables(main_attempts, schema)
    lines += ["", "## Saved campaign and Actions costs", ""]
    lines += _table(["Ledger field", "Stored value"], [
        [key, costs.get(key)] for key in (
            "known_completed_job_elapsed_seconds", "runs_with_unknown_job_elapsed",
            "known_stored_artifact_bytes", "runs_with_unknown_artifact_bytes",
            "report_artifact_transfer", "human_agent_seconds",
            "current_report_job_tail_seconds",
            "scope", "overlap_rule",
        )
    ])
    lines += [""]
    campaign_cost_rows = []
    for item in attempts:
        evaluation = (item.get("evaluation_projection") if schema == REFERENCED_AGGREGATE_SCHEMA
                      else item.get("evaluation")) or {}
        cost = evaluation.get("cost") or {}
        campaign_cost_rows.append([
            item.get("run_id"), item.get("collector"), item.get("stage"), item.get("system"),
            item.get("mode"), item.get("seed"), cost.get("campaign_elapsed_seconds"),
            cost.get("toolchain_build_seconds"), cost.get("toolchain_command_seconds"),
            (cost.get("manual_preparation") or {}).get("measured"),
            (cost.get("manual_preparation") or {}).get("reason"),
        ])
    lines += _table([
        "Run", "Collector", "Stage", "System", "Mode", "Seed", "Campaign s",
        "Toolchain build s", "Toolchain command s", "Manual effort measured", "Reason",
    ], campaign_cost_rows)
    lines += ["", "Actions jobs, including runs without a campaign artifact:", ""]
    job_rows = []
    for run in costs.get("runs") or []:
        jobs = run.get("jobs") or [None]
        for job in jobs:
            job = job or {}
            job_rows.append([
                run.get("run_id"), run.get("repository"), run.get("role"),
                run.get("status"), run.get("conclusion"),
                job.get("id"), job.get("name"), job.get("status"), job.get("conclusion"),
                job.get("elapsed_seconds"), len(run.get("artifacts") or []),
            ])
    lines += _table([
        "Run", "Repository", "Role", "Run status", "Run conclusion", "Job", "Job name", "Job status",
        "Job conclusion", "API interval s", "Artifacts",
    ], job_rows)
    lines += [
        "", "Human/agent preparation effort: " + _value(costs.get("human_agent_seconds")),
        "", "Current report-job unfinished tail: " + _value(costs.get("current_report_job_tail_seconds")),
        "", (
            "Every source evaluation remains losslessly restorable from an explicit hash-bound "
            "payload reference. The small aggregate retains only fields used by these tables."
            if schema == REFERENCED_AGGREGATE_SCHEMA else
            "The legacy aggregate retains every source evaluation object, including detailed "
            "DB, baseline, class, async, causal and cost fields not expanded here."
        ),
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"attempts": len(attempts), "report": str(out.resolve())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, nargs="+")
    parser.add_argument("--declarations", type=Path)
    parser.add_argument("--retrieval", type=Path)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--aggregate", type=Path)
    parser.add_argument("--costs", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        parser.error("v5 research reporting is permitted only in GitHub Actions")
    if args.inputs:
        if not args.declarations or not args.report_dir:
            parser.error("--inputs requires --declarations and --report-dir")
        build(args.inputs, args.declarations, args.report_dir,
              retrieval_path=args.retrieval, selection_path=args.selection)
    elif args.aggregate and args.out:
        render(args.aggregate, args.out, args.costs)
    else:
        parser.error("choose saved aggregation or rendering")


if __name__ == "__main__":
    main()
