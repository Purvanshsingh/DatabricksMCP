from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_list_workspace_objects_is_bounded() -> None:
    objects = _service().list_workspace_objects(path="/Repos", limit=1)
    assert objects[0]["object_type"] == "NOTEBOOK"
    assert objects[0]["path"] == "/Repos/etl"


def test_get_workspace_status() -> None:
    assert _service().get_workspace_status("/Repos")["object_type"] == "DIRECTORY"


def test_export_notebook_maps_format() -> None:
    exported = _service().export_workspace_object(path="/Repos/etl", export_format="SOURCE")
    assert exported["file_type"] == "SOURCE"
    assert exported["content"]


def test_workspace_tools_registered_and_invocable() -> None:
    server = create_server(Settings(), service=_service())
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {"list_workspace_objects", "get_workspace_status", "export_notebook"} <= tools
    _content, structured = asyncio.run(
        server.call_tool("export_notebook", {"path": "/Repos/etl", "export_format": "JUPYTER"})
    )
    assert structured["file_type"] == "JUPYTER"
