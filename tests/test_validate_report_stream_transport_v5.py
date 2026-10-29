from __future__ import annotations

import importlib.util
from pathlib import Path
import zipfile

from ebpf_discovery.report_v5 import build, render


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


def test_validator_comparison_consumes_actual_report_build_schema(tmp_path: Path) -> None:
    helper_path = Path(__file__).with_name("test_report_v5.py")
    helper_spec = importlib.util.spec_from_file_location(
        "report_v5_fixture_for_transport_validation", helper_path)
    assert helper_spec is not None and helper_spec.loader is not None
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    helper.summary(tmp_path / "inputs", 20, "main")
    declarations = helper.declared(
        tmp_path / "declarations.json", [helper.run(20, "main")])
    old_report, new_report = tmp_path / "old-report", tmp_path / "new-report"
    build([tmp_path / "inputs"], declarations, old_report)
    build([tmp_path / "inputs"], declarations, new_report)
    render(old_report / "evaluation-v5.json", old_report / "report-v5.md")
    render(new_report / "evaluation-v5.json", new_report / "report-v5.md")

    checks = VALIDATOR._comparison(old_report, new_report)

    assert checks["ambiguous_duplicate_main_cells_equal"] is True
    assert all(checks.values())
