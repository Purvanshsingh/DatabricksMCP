"""Databricks SQL pack: warehouse discovery and bounded read-only SQL.

``execute_read_only_sql`` validates every statement with the sqlglot-based guard
(:mod:`databricks_mcp.sqlguard`) before it reaches a warehouse, and bounds the
result by rows, bytes, and wait time. Long-running statements return a
statement id the caller can poll with ``get_sql_statement`` or stop with
``cancel_sql_statement``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec
from databricks_mcp.sqlguard import validate_read_only_sql

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "sql"


def register(registrar: Registrar) -> None:
    settings = registrar.settings
    default_limit = settings.default_page_size
    limit_of = registrar.checked_limit

    def resolve_warehouse(warehouse_id: str) -> str:
        warehouse_id = warehouse_id.strip()
        if not warehouse_id:
            raise ValueError("warehouse_id is required")
        allowlist = settings.sql_warehouse_allowlist
        if allowlist and warehouse_id not in allowlist:
            raise ValueError(f"warehouse '{warehouse_id}' is not in the configured allowlist")
        return warehouse_id

    def clamp_rows(max_rows: int) -> int:
        if max_rows < 1:
            raise ValueError("max_rows must be greater than zero")
        return min(max_rows, settings.sql_max_rows)

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
        return registrar.service.get_warehouse(resolve_warehouse(warehouse_id))

    @registrar.tool(
        ToolSpec(
            "list_query_history",
            NAME,
            RiskClass.READ,
            "List recent SQL query history entries, bounded to the requested count.",
        )
    )
    def list_query_history(limit: int = default_limit) -> dict[str, Any]:
        return registrar.service.list_query_history(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "execute_read_only_sql",
            NAME,
            RiskClass.READ,
            "Run an AST-validated read-only SQL query on a warehouse, bounded by "
            "rows, bytes, and wait time. Only SELECT/SHOW/DESCRIBE/EXPLAIN are allowed.",
        )
    )
    def execute_read_only_sql(
        statement: str,
        warehouse_id: str,
        max_rows: int = settings.sql_max_rows,
        catalog: str | None = None,
        schema: str | None = None,
    ) -> dict[str, Any]:
        safe_statement = validate_read_only_sql(statement)
        return registrar.service.execute_read_only_sql(
            statement=safe_statement,
            warehouse_id=resolve_warehouse(warehouse_id),
            row_limit=clamp_rows(max_rows),
            byte_limit=settings.sql_byte_limit,
            wait_seconds=settings.sql_wait_seconds,
            catalog=catalog,
            schema=schema,
        )

    @registrar.tool(
        ToolSpec(
            "explain_sql",
            NAME,
            RiskClass.READ,
            "Return the query plan for a read-only SQL query without returning rows.",
        )
    )
    def explain_sql(
        statement: str,
        warehouse_id: str,
        catalog: str | None = None,
        schema: str | None = None,
    ) -> dict[str, Any]:
        validate_read_only_sql(statement)
        explain_statement = validate_read_only_sql(f"EXPLAIN {statement}")
        return registrar.service.execute_read_only_sql(
            statement=explain_statement,
            warehouse_id=resolve_warehouse(warehouse_id),
            row_limit=settings.sql_max_rows,
            byte_limit=settings.sql_byte_limit,
            wait_seconds=settings.sql_wait_seconds,
            catalog=catalog,
            schema=schema,
        )

    @registrar.tool(
        ToolSpec(
            "get_sql_statement",
            NAME,
            RiskClass.READ,
            "Poll the status and bounded result of a previously submitted statement.",
        )
    )
    def get_sql_statement(statement_id: str) -> dict[str, Any]:
        return registrar.service.get_sql_statement(statement_id)

    @registrar.tool(
        ToolSpec(
            "cancel_sql_statement",
            NAME,
            RiskClass.READ,
            "Cancel a running SQL statement by its id.",
        )
    )
    def cancel_sql_statement(statement_id: str) -> dict[str, Any]:
        return registrar.service.cancel_sql_statement(statement_id)
