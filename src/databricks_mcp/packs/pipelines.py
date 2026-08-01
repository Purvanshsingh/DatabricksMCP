"""Lakeflow (Delta Live Tables) pipelines read pack (read-only)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "pipelines"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_pipelines",
            NAME,
            RiskClass.READ,
            "List Lakeflow pipelines, bounded to the configured page size.",
        )
    )
    def list_pipelines(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_pipelines(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_pipeline",
            NAME,
            RiskClass.READ,
            "Get the definition and state of one pipeline by id.",
        )
    )
    def get_pipeline(pipeline_id: str) -> dict[str, Any]:
        return registrar.service.get_pipeline(pipeline_id)

    @registrar.tool(
        ToolSpec(
            "list_pipeline_events",
            NAME,
            RiskClass.READ,
            "List recent events for a pipeline (status, data quality, errors).",
        )
    )
    def list_pipeline_events(pipeline_id: str) -> dict[str, Any]:
        return registrar.service.list_pipeline_events(pipeline_id)

    @registrar.tool(
        ToolSpec(
            "list_pipeline_updates",
            NAME,
            RiskClass.READ,
            "List update (run) history for a pipeline.",
        )
    )
    def list_pipeline_updates(pipeline_id: str) -> dict[str, Any]:
        return registrar.service.list_pipeline_updates(pipeline_id)

    @registrar.tool(
        ToolSpec(
            "get_pipeline_update",
            NAME,
            RiskClass.READ,
            "Get one pipeline update by pipeline and update id.",
        )
    )
    def get_pipeline_update(pipeline_id: str, update_id: str) -> dict[str, Any]:
        return registrar.service.get_pipeline_update(pipeline_id, update_id)
