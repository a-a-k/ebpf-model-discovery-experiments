from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ebpf_discovery.full_input_archive import (
    ArchiveReader,
    MAX_RELEASE_ASSET_BYTES,
    PART_BYTES,
    require,
)


def test_archive_parts_use_one_gib_boundary():
    assert PART_BYTES == 1024**3
    assert PART_BYTES < MAX_RELEASE_ASSET_BYTES


def test_reader_reassembles_ordered_parts_and_rejects_bad_span(tmp_path):
    bodies = {0: b"abcd", 1: b"efgh"}

    def download(asset, destination):
        destination.write_bytes(bodies[asset["id"]])

    parts = [{"id": 0, "size": 4}, {"id": 1, "size": 4}]
    reader = ArchiveReader(parts, tmp_path / "cache", download=download)
    original = b"abcdefgh"
    record = {
        "original_artifact": {
            "size_in_bytes": len(original),
            "digest": "sha256:" + hashlib.sha256(original).hexdigest(),
        },
        "slices": [
            {"part": 0, "offset": 0, "length": 4, "artifact_offset": 0},
            {"part": 1, "offset": 0, "length": 4, "artifact_offset": 4},
        ],
    }

    destination = tmp_path / "restored.zip"
    reader.restore(record, destination)
    assert destination.read_bytes() == original

    broken = dict(record)
    broken["slices"] = [dict(record["slices"][1]), dict(record["slices"][0])]
    with pytest.raises(ValueError, match="overlap|reorder|gap"):
        reader.restore(broken, tmp_path / "broken.zip")


def test_reader_rejects_truncated_part(tmp_path):
    def download(_asset, destination):
        destination.write_bytes(b"shor")

    reader = ArchiveReader([{"id": 0, "size": 5}], tmp_path / "cache", download=download)
    record = {
        "original_artifact": {"size_in_bytes": 5, "digest": "sha256:" + "0" * 64},
        "slices": [{"part": 0, "offset": 0, "length": 5, "artifact_offset": 0}],
    }
    with pytest.raises(ValueError, match="part is not complete"):
        reader.restore(record, tmp_path / "truncated.zip")
