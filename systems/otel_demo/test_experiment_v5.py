from pathlib import Path

from .adapter import Adapter as HistoricalAdapter
from .adapter_v5 import Adapter as DeploymentAdapterV5
from .experiment_v4 import Adapter as ExperimentAdapterV4
from .experiment_v4 import CONTRACTS as V4_CONTRACTS
from .experiment_v5 import Adapter, CONTRACTS


def _adapter(tmp_path: Path, mode: str = "absent") -> Adapter:
    context = type(
        "Context",
        (),
        {
            "mode": mode,
            "deployment_dir": tmp_path,
            "node_ip": lambda self, node: "192.0.2.10" if node == "a" else "192.0.2.11",
        },
    )()
    return Adapter(context)


def test_v5_bridge_keeps_all_v4_contracts_and_planning(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    assert CONTRACTS is V4_CONTRACTS
    assert set(CONTRACTS) == {"browse_product", "add_to_cart", "checkout"}
    assert isinstance(adapter, DeploymentAdapterV5)
    assert isinstance(adapter, ExperimentAdapterV4)
    assert isinstance(adapter, HistoricalAdapter)
    plan = adapter.plan_operation("checkout", 7, "smoke-v5")
    assert plan["operation"] == "checkout"
    assert len(plan["http_steps"]) == 3
    assert all(step["request_id"] for step in plan["http_steps"])


def test_v5_patch_wins_mro_without_mutating_historical_adapter(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    assert adapter._patch_native_disable.__func__ is DeploymentAdapterV5._patch_native_disable
    assert HistoricalAdapter._patch_native_disable is not DeploymentAdapterV5._patch_native_disable
    assert Adapter.mro().index(DeploymentAdapterV5) < Adapter.mro().index(ExperimentAdapterV4)
    description = adapter._suppression_description()
    assert description["experiment_protocol"] == "iteration-5"
    assert description["raw_mode_audit"]["schema"] == "otel-demo-native-mode-audit-v5"
