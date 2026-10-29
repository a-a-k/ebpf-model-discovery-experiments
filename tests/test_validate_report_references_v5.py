from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
import zipfile

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate-report-references-v5.py"
SPEC = importlib.util.spec_from_file_location("validate_report_references_v5", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def test_retained_report_path_is_explicitly_rebased(tmp_path: Path) -> None:
    assert VALIDATOR._retained_path(
        tmp_path, "results/iteration-5/source-artifacts/repository/123.zip",
    ) == (tmp_path / "source-artifacts/repository/123.zip").resolve()
    with pytest.raises(ValueError, match="wrong root"):
        VALIDATOR._retained_path(tmp_path, "unrelated/123.zip")


def test_compact_extraction_retains_exact_evaluation_bytes(tmp_path: Path) -> None:
    archive = tmp_path / "compact.zip"
    original = b'{"schema_version":"evaluation-v5","exact":"bytes"}\n'
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("evaluation-v5.json", original)
        bundle.writestr("status.json", b"{}\n")
    result = VALIDATOR._safe_extract(archive, tmp_path / "out")
    assert result["evaluation-v5.json"]["bytes"] == len(original)
    assert result["evaluation-v5.json"]["sha256"] == hashlib.sha256(original).hexdigest()
    assert (tmp_path / "out/evaluation-v5.json").read_bytes() == original


def test_compact_extraction_rejects_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../evaluation-v5.json", b"{}")
    with pytest.raises(ValueError, match="duplicate or unsafe"):
        VALIDATOR._safe_extract(archive, tmp_path / "out")


def test_recovery_comparison_rebases_only_retained_archive_path() -> None:
    left = {"status": "recovered", "source": {"full_zip_verification": {
        "path": "old.zip", "computed_digest": "sha256:abc", "received_bytes": 5,
    }}}
    right = {"status": "recovered", "source": {"full_zip_verification": {
        "path": "new.zip", "computed_digest": "sha256:abc", "received_bytes": 5,
    }}}
    assert VALIDATOR._recovery_semantics(left) == VALIDATOR._recovery_semantics(right)
    right["source"]["full_zip_verification"]["received_bytes"] = 6
    assert VALIDATOR._recovery_semantics(left) != VALIDATOR._recovery_semantics(right)
