"""Databricks SQL read pack: SQL warehouse discovery.

Read-only SQL execution (``execute_read_only_sql`` with AST validation and
bounded results) is planned for the next increment and will join this pack.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "sql"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_sql_warehouses",
            NAME,
            RiskClass.READ,
            "List accessible SQL warehouses, bounded to the configured page size.",
        )
    )
    def list_sql_warehouses(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_warehouses(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_sql_warehouse",
            NAME,
            RiskClass.READ,
            "Get configuration and state for one SQL warehouse by its id.",
        )
    )
    def get_sql_warehouse(warehouse_id: str) -> dict[str, Any]:
        return registrar.service.get_warehouse(warehouse_id)
