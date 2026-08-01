"""MLflow read pack: experiments, runs, and the model registry (read-only)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "mlflow"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_experiments",
            NAME,
            RiskClass.READ,
            "List MLflow experiments, bounded to the page size.",
        )
    )
    def list_experiments(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_experiments(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec("get_experiment", NAME, RiskClass.READ, "Get one MLflow experiment by id.")
    )
    def get_experiment(experiment_id: str) -> dict[str, Any]:
        return registrar.service.get_experiment(experiment_id)

    @registrar.tool(
        ToolSpec(
            "search_experiment_runs",
            NAME,
            RiskClass.READ,
            "List runs for one experiment, bounded to the page size.",
        )
    )
    def search_experiment_runs(
        experiment_id: str, limit: int = default_limit
    ) -> list[dict[str, Any]]:
        return registrar.service.search_experiment_runs(
            experiment_id=experiment_id, limit=limit_of(limit)
        )

    @registrar.tool(
        ToolSpec(
            "list_registered_models",
            NAME,
            RiskClass.READ,
            "List registered models in the model registry, bounded to the page size.",
        )
    )
    def list_registered_models(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_registered_models(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec("get_registered_model", NAME, RiskClass.READ, "Get one registered model by name.")
    )
    def get_registered_model(name: str) -> dict[str, Any]:
        return registrar.service.get_registered_model(name)

    @registrar.tool(
        ToolSpec(
            "get_model_version",
            NAME,
            RiskClass.READ,
            "Get one registered model version by name and version.",
        )
    )
    def get_model_version(name: str, version: str) -> dict[str, Any]:
        return registrar.service.get_model_version(name, version)
