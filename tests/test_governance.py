from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_get_grants_passes_securable() -> None:
    grants = _service().get_grants("TABLE", "main.default.events")
    assert grants["securable_type"] == "TABLE"
    assert grants["privilege_assignments"][0]["privileges"] == ["SELECT"]


def test_get_effective_grants() -> None:
    effective = _service().get_effective_grants("SCHEMA", "main.default")
    assert "USE_SCHEMA" in effective["privilege_assignments"][0]["privileges"]


def test_get_permissions() -> None:
    perms = _service().get_permissions("clusters", "c1")
    assert perms["object_type"] == "clusters"
    assert perms["object_id"] == "c1"


def test_governance_tools_registered_and_invocable() -> None:
    server = create_server(Settings(), service=_service())
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {"get_grants", "get_effective_grants", "get_permissions"} <= tools
    _content, structured = asyncio.run(
        server.call_tool("get_grants", {"securable_type": "TABLE", "full_name": "main.default.t"})
    )
    assert structured["full_name"] == "main.default.t"
