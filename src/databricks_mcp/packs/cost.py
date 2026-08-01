"""Cost and audit read pack over Databricks system tables (read-only).

System tables (``system.billing.usage``, ``system.access.audit``) are a recent
Databricks feature. These tools build fixed, read-only SELECT statements,
validate them through the same AST guard as ``execute_read_only_sql``, and run
them on a warehouse under the same row/byte/time bounds and warehouse allowlist.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec
from databricks_mcp.sqlguard import validate_read_only_sql

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "cost"


def register(registrar: Registrar) -> None:
    settings = registrar.settings

    def run_system_query(sql: str, warehouse_id: str) -> dict[str, Any]:
        warehouse_id = warehouse_id.strip()
        if not warehouse_id:
            raise ValueError("warehouse_id is required")
        allowlist = settings.sql_warehouse_allowlist
        if allowlist and warehouse_id not in allowlist:
            raise ValueError(f"warehouse '{warehouse_id}' is not in the configured allowlist")
        safe_sql = validate_read_only_sql(sql)
        return registrar.service.execute_read_only_sql(
            statement=safe_sql,
            warehouse_id=warehouse_id,
            row_limit=settings.sql_max_rows,
            byte_limit=settings.sql_byte_limit,
            wait_seconds=settings.sql_wait_seconds,
        )

    def bounded(limit: int) -> int:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        return min(limit, settings.sql_max_rows)

    @registrar.tool(
        ToolSpec(
            "get_recent_billing_usage",
            NAME,
            RiskClass.READ,
            "Read recent rows from system.billing.usage on a warehouse (most recent first).",
        )
    )
    def get_recent_billing_usage(warehouse_id: str, limit: int = 100) -> dict[str, Any]:
        rows = bounded(limit)
        sql = (
            "SELECT usage_date, sku_name, usage_quantity, usage_unit, workspace_id "
            f"FROM system.billing.usage ORDER BY usage_date DESC LIMIT {rows}"
        )
        return run_system_query(sql, warehouse_id)

    @registrar.tool(
        ToolSpec(
            "get_recent_audit_events",
            NAME,
            RiskClass.READ,
            "Read recent rows from system.access.audit on a warehouse (most recent first).",
        )
    )
    def get_recent_audit_events(warehouse_id: str, limit: int = 100) -> dict[str, Any]:
        rows = bounded(limit)
        sql = (
            "SELECT event_time, action_name, service_name, user_identity "
            f"FROM system.access.audit ORDER BY event_time DESC LIMIT {rows}"
        )
        return run_system_query(sql, warehouse_id)
