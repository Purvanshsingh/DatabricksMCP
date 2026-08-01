from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def test_list_query_history_passes_limit_and_returns_object() -> None:
    service = DatabricksService(FakeWorkspaceClient())
    result = service.list_query_history(limit=25)
    assert result["res"][0]["query_id"] == "q1"
    assert result["_max"] == 25


def test_query_history_tool_registered_and_invocable() -> None:
    server = create_server(Settings(), service=DatabricksService(FakeWorkspaceClient()))
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert "list_query_history" in tools
    _content, structured = asyncio.run(server.call_tool("list_query_history", {"limit": 5}))
    assert structured["res"][0]["status"] == "FINISHED"
