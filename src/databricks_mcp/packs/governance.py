"""Governance read pack: Unity Catalog grants and workspace object permissions.

Table and column lineage are not a dedicated SDK endpoint; they live in the
``system.access.table_lineage`` / ``column_lineage`` system tables and can be
queried through ``execute_read_only_sql``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "governance"


def register(registrar: Registrar) -> None:
    @registrar.tool(
        ToolSpec(
            "get_grants",
            NAME,
            RiskClass.READ,
            "Get Unity Catalog grants directly assigned on a securable "
            "(securable_type e.g. TABLE/SCHEMA/CATALOG, full_name).",
        )
    )
    def get_grants(securable_type: str, full_name: str) -> dict[str, Any]:
        return registrar.service.get_grants(securable_type, full_name)

    @registrar.tool(
        ToolSpec(
            "get_effective_grants",
            NAME,
            RiskClass.READ,
            "Get effective Unity Catalog grants on a securable, including inherited privileges.",
        )
    )
    def get_effective_grants(securable_type: str, full_name: str) -> dict[str, Any]:
        return registrar.service.get_effective_grants(securable_type, full_name)

    @registrar.tool(
        ToolSpec(
            "get_permissions",
            NAME,
            RiskClass.READ,
            "Get the access control list for a workspace object "
            "(object_type e.g. clusters/jobs/warehouses, object_id).",
        )
    )
    def get_permissions(object_type: str, object_id: str) -> dict[str, Any]:
        return registrar.service.get_permissions(object_type, object_id)
