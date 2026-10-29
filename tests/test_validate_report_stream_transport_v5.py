from __future__ import annotations

import importlib.util
from pathlib import Path
import zipfile


SCRIPT = (Path(__file__).parents[1] / "scripts" /
          "validate-report-stream-transport-v5.py")
SPEC = importlib.util.spec_from_file_location("validate_report_stream_transport", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def test_validator_zip_guard_rejects_parent_and_accepts_file() -> None:
    assert VALIDATOR._safe(zipfile.ZipInfo("observations/collector.json")) is True
    assert VALIDATOR._safe(zipfile.ZipInfo("../collector.json")) is False


def test_validator_declaration_preserves_exact_saved_cell() -> None:
    declaration = VALIDATOR._declarations({
        "collector": "obi", "system": "deathstarbench", "mode": "absent",
        "seed": 7, "smoke": False,
    })
    run = declaration["attempt_runs"][0]
    assert run["run_id"] == 40942429097
    assert run["stage"] == "main"
    assert run["cells"] == [{"system": "deathstarbench", "mode": "absent",
                             "seed": 7}]


def test_validator_sidecar_binds_actual_full_artifact() -> None:
    sidecar = VALIDATOR._sidecar(
        {"full_artifact_name": VALIDATOR.FULL_ARTIFACT_NAME},
        {"safe_extract": True},
    )
    assert sidecar["full_artifact_id"] == 12933019490
    assert sidecar["full_artifact_digest"].startswith("sha256:5a865582")
    assert sidecar["full_artifact_expired"] is False
