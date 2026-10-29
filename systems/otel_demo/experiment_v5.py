"""Iteration-5 OTel Demo experiment bridge.

Workload contracts, durable request planning, and outcome verification are the
unchanged v4 implementation.  Only deployment tracing-mode semantics come from
the separately versioned v5 adapter.
"""

from __future__ import annotations

from typing import Any

from .adapter_v5 import Adapter as DeploymentAdapterV5
from .experiment_v4 import (
    CATALOG_DATABASE_ALIASES,
    CONTRACTS,
    CONTROLLED_SERVICE_ALIASES,
    ENTRY_SERVICE_ALIASES,
    SELECTED_DATABASE,
    Adapter as ExperimentAdapterV4,
)


class Adapter(DeploymentAdapterV5, ExperimentAdapterV4):
    """V4 scientific workload over v5 provider-neutral disabled tracing."""

    def metadata(self) -> dict[str, Any]:
        metadata = super().metadata()
        metadata["v5_experiment"] = {
            "protocol": "iteration-5",
            "workload_contracts": "systems.otel_demo.experiment_v4.CONTRACTS",
            "workload_semantics": "unchanged protocol-v4 operations and external outcomes",
            "deployment_semantics": "systems.otel_demo.adapter_v5.Adapter",
            "comparison_guard": (
                "apply this changed tracing-mode treatment equally to every fresh "
                "collector arm; do not attribute v5-v4 differences solely to collectors"
            ),
        }
        return metadata


__all__ = [
    "Adapter",
    "CONTRACTS",
    "CONTROLLED_SERVICE_ALIASES",
    "ENTRY_SERVICE_ALIASES",
    "CATALOG_DATABASE_ALIASES",
    "SELECTED_DATABASE",
]
