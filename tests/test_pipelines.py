from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_list_pipelines_is_bounded() -> None:
    assert _service().list_pipelines(limit=1) == [{"pipeline_id": "p1", "name": "bronze"}]


def test_get_pipeline_returns_object() -> None:
    assert _service().get_pipeline("p1")["state"] == "RUNNING"


def test_pipeline_events_and_updates() -> None:
    service = _service()
    assert service.list_pipeline_events("p1")["events"][0]["level"] == "INFO"
    assert service.list_pipeline_updates("p1")["updates"][0]["state"] == "COMPLETED"
    assert service.get_pipeline_update("p1", "u1")["update"]["update_id"] == "u1"


def test_pipeline_tools_registered_and_invocable() -> None:
    server = create_server(Settings(), service=_service())
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {
        "list_pipelines",
        "get_pipeline",
        "list_pipeline_events",
        "list_pipeline_updates",
        "get_pipeline_update",
    } <= tools
    _content, structured = asyncio.run(server.call_tool("get_pipeline", {"pipeline_id": "p1"}))
    assert structured["pipeline_id"] == "p1"
