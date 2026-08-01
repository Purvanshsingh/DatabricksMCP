from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def test_billing_usage_builds_bounded_system_query() -> None:
    client = FakeWorkspaceClient()
    server = create_server(Settings(sql_max_rows=50), service=DatabricksService(client))
    asyncio.run(server.call_tool("get_recent_billing_usage", {"warehouse_id": "w1", "limit": 9999}))
    call = client.statement_execution.calls[0]
    assert "system.billing.usage" in call["statement"]
    assert "LIMIT 50" in call["statement"]  # clamped to sql_max_rows


def test_audit_events_query_runs() -> None:
    client = FakeWorkspaceClient()
    server = create_server(Settings(), service=DatabricksService(client))
    asyncio.run(server.call_tool("get_recent_audit_events", {"warehouse_id": "w1"}))
    assert "system.access.audit" in client.statement_execution.calls[0]["statement"]


def test_cost_tools_registered() -> None:
    server = create_server(Settings(), service=DatabricksService(FakeWorkspaceClient()))
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {"get_recent_billing_usage", "get_recent_audit_events"} <= tools
