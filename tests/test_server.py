from __future__ import annotations

import asyncio

import pytest

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient

# Tools that must always be present regardless of which packs are enabled.
BASELINE_TOOLS = {
    "health",
    "server_info",
    "list_enabled_capabilities",
    "get_policy_status",
    "current_identity",
    "list_catalogs",
    "list_sql_warehouses",
}


def _server() -> object:
    return create_server(Settings(), service=DatabricksService(FakeWorkspaceClient()))


def test_all_tools_register_with_schemas() -> None:
    server = _server()
    tools = asyncio.run(server.list_tools())
    names = [tool.name for tool in tools]
    assert set(names) >= BASELINE_TOOLS
    assert len(names) == len(set(names)), "tool names must be unique"
    assert all(tool.outputSchema is not None for tool in tools)
    assert all(tool.description for tool in tools)


def test_health_does_not_require_databricks_credentials() -> None:
    server = create_server(Settings())
    _content, structured = asyncio.run(server.call_tool("health", {}))
    assert structured == {
        "status": "ok",
        "version": "0.1.0.dev0",
        "access_mode": "read-only",
        "transport": "stdio",
    }


def test_current_identity_flows_through_service() -> None:
    server = _server()
    _content, structured = asyncio.run(server.call_tool("current_identity", {}))
    assert structured == {"userName": "user@example.com"}


def test_describe_table_returns_concise_summary() -> None:
    server = _server()
    _content, structured = asyncio.run(
        server.call_tool("describe_table", {"full_name": "main.default.events"})
    )
    assert structured["table_type"] == "MANAGED"
    assert [column["name"] for column in structured["columns"]] == ["id", "ts"]
    assert structured["columns"][0]["type"] == "bigint"


def test_server_info_reports_packs_and_tool_count() -> None:
    server = _server()
    tool_total = len(asyncio.run(server.list_tools()))
    _content, structured = asyncio.run(server.call_tool("server_info", {}))
    assert {"core", "catalog", "sql"} <= set(structured["packs"])
    assert structured["tool_count"] == tool_total


def test_list_enabled_capabilities_reports_read_risk() -> None:
    server = _server()
    tool_total = len(asyncio.run(server.list_tools()))
    _content, structured = asyncio.run(server.call_tool("list_enabled_capabilities", {}))
    capabilities = structured["result"]
    assert {cap["risk"] for cap in capabilities} == {"read"}
    assert len(capabilities) == tool_total


# Every catalog/sql tool exercised end-to-end through the server against the fake
# workspace, so each tool body and its argument wiring is covered.
_TOOL_CALLS = [
    ("list_catalogs", {}),
    ("get_catalog", {"name": "main"}),
    ("list_schemas", {"catalog_name": "main"}),
    ("get_schema", {"full_name": "main.default"}),
    ("list_tables", {"catalog_name": "main", "schema_name": "default"}),
    ("list_views", {"catalog_name": "main", "schema_name": "default"}),
    ("get_table", {"full_name": "main.default.events"}),
    ("list_columns", {"full_name": "main.default.events"}),
    ("list_functions", {"catalog_name": "main", "schema_name": "default"}),
    ("get_function", {"name": "main.default.to_upper"}),
    ("list_volumes", {"catalog_name": "main", "schema_name": "default"}),
    ("list_sql_warehouses", {}),
    ("get_sql_warehouse", {"warehouse_id": "w1"}),
    ("execute_read_only_sql", {"statement": "SELECT 1", "warehouse_id": "w1"}),
    ("explain_sql", {"statement": "SELECT 1", "warehouse_id": "w1"}),
    ("get_sql_statement", {"statement_id": "stmt-1"}),
    ("cancel_sql_statement", {"statement_id": "stmt-1"}),
]


@pytest.mark.parametrize(("tool", "args"), _TOOL_CALLS)
def test_read_tool_invocation_succeeds(tool: str, args: dict[str, str]) -> None:
    server = _server()
    content, structured = asyncio.run(server.call_tool(tool, args))
    assert content
    assert structured is not None
