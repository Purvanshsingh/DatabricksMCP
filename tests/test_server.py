from __future__ import annotations

import asyncio
from collections.abc import Iterable

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService


class Model:
    def as_dict(self) -> dict[str, object]:
        return {"name": "example"}


class CurrentUser:
    def me(self) -> object:
        return Model()


class ListingAPI:
    def list(self) -> Iterable[object]:
        return [Model()]


class FakeWorkspaceClient:
    def __init__(self) -> None:
        self.current_user = CurrentUser()
        self.catalogs = ListingAPI()
        self.warehouses = ListingAPI()


def test_tool_schemas_are_registered_and_resolvable() -> None:
    server = create_server(
        Settings(),
        service=DatabricksService(FakeWorkspaceClient()),
    )

    tools = asyncio.run(server.list_tools())

    assert {tool.name for tool in tools} == {
        "health",
        "current_identity",
        "list_catalogs",
        "list_sql_warehouses",
    }
    assert all(tool.outputSchema is not None for tool in tools)


def test_health_does_not_require_databricks_credentials() -> None:
    server = create_server(Settings())

    content, structured = asyncio.run(server.call_tool("health", {}))

    assert content
    assert structured == {
        "status": "ok",
        "version": "0.1.0.dev0",
        "access_mode": "read-only",
        "transport": "stdio",
    }
