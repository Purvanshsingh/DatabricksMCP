from __future__ import annotations

import asyncio

import pytest

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _server_with_client(client: FakeWorkspaceClient, settings: Settings | None = None) -> object:
    return create_server(settings or Settings(), service=DatabricksService(client))


def test_execute_read_only_sql_passes_bounded_request() -> None:
    client = FakeWorkspaceClient()
    server = _server_with_client(client)
    _content, structured = asyncio.run(
        server.call_tool(
            "execute_read_only_sql",
            {"statement": "SELECT 1", "warehouse_id": "w1", "max_rows": 5},
        )
    )
    assert structured["statement_id"] == "stmt-1"
    call = client.statement_execution.calls[0]
    assert call["statement"] == "SELECT 1"
    assert call["warehouse_id"] == "w1"
    assert call["row_limit"] == 5
    assert call["byte_limit"] == Settings().sql_byte_limit
    assert call["wait_timeout"] == "30s"


def test_execute_read_only_sql_clamps_max_rows_to_ceiling() -> None:
    client = FakeWorkspaceClient()
    server = _server_with_client(client, Settings(sql_max_rows=10))
    asyncio.run(
        server.call_tool(
            "execute_read_only_sql",
            {"statement": "SELECT 1", "warehouse_id": "w1", "max_rows": 9999},
        )
    )
    assert client.statement_execution.calls[0]["row_limit"] == 10


def test_execute_read_only_sql_rejects_mutations() -> None:
    client = FakeWorkspaceClient()
    server = _server_with_client(client)
    with pytest.raises(Exception, match=r"read-only|not permitted|parse"):
        asyncio.run(
            server.call_tool(
                "execute_read_only_sql",
                {"statement": "DROP TABLE t", "warehouse_id": "w1"},
            )
        )
    assert client.statement_execution.calls == []


def test_execute_read_only_sql_enforces_warehouse_allowlist() -> None:
    client = FakeWorkspaceClient()
    server = _server_with_client(client, Settings(sql_warehouse_allowlist=("allowed",)))
    with pytest.raises(Exception, match="allowlist"):
        asyncio.run(
            server.call_tool(
                "execute_read_only_sql",
                {"statement": "SELECT 1", "warehouse_id": "w1"},
            )
        )


def test_cancel_sql_statement_calls_sdk() -> None:
    client = FakeWorkspaceClient()
    service = DatabricksService(client)
    assert service.cancel_sql_statement("stmt-9") == {"statement_id": "stmt-9", "cancelled": True}
    assert client.statement_execution.cancelled == ["stmt-9"]


def test_explain_sql_wraps_statement_with_explain() -> None:
    client = FakeWorkspaceClient()
    server = _server_with_client(client)
    asyncio.run(server.call_tool("explain_sql", {"statement": "SELECT 1", "warehouse_id": "w1"}))
    assert client.statement_execution.calls[0]["statement"] == "EXPLAIN SELECT 1"
