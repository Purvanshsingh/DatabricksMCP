"""Workspace files read pack: browse and export notebooks and workspace objects."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "workspace"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_workspace_objects",
            NAME,
            RiskClass.READ,
            "List notebooks, folders, and files under a workspace path.",
        )
    )
    def list_workspace_objects(path: str, limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_workspace_objects(path=path, limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_workspace_status",
            NAME,
            RiskClass.READ,
            "Get the status and type of one workspace object by path.",
        )
    )
    def get_workspace_status(path: str) -> dict[str, Any]:
        return registrar.service.get_workspace_status(path)

    @registrar.tool(
        ToolSpec(
            "export_notebook",
            NAME,
            RiskClass.READ,
            "Export a notebook or workspace file as base64 content "
            "(export_format: SOURCE, HTML, JUPYTER, DBC, R_MARKDOWN, AUTO).",
        )
    )
    def export_notebook(path: str, export_format: str = "SOURCE") -> dict[str, Any]:
        return registrar.service.export_workspace_object(path=path, export_format=export_format)
