from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_serving_endpoints() -> None:
    service = _service()
    assert service.list_serving_endpoints(limit=10)[0]["name"] == "llm"
    assert service.get_serving_endpoint("llm")["state"]["ready"] == "READY"


def test_vector_search() -> None:
    service = _service()
    assert service.list_vector_search_endpoints(limit=10)[0]["name"] == "vs1"
    assert service.get_vector_search_endpoint("vs1")["name"] == "vs1"
    indexes = service.list_vector_search_indexes(endpoint_name="vs1", limit=10)
    assert indexes[0]["endpoint_name"] == "vs1"
    assert service.get_vector_search_index("vs1.idx")["index_type"] == "DELTA_SYNC"


def test_genie() -> None:
    service = _service()
    assert service.list_genie_spaces()["spaces"][0]["space_id"] == "s1"
    assert service.get_genie_space("s1")["title"] == "Sales"


def test_ai_tools_registered() -> None:
    server = create_server(Settings(), service=_service())
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {
        "list_serving_endpoints",
        "get_serving_endpoint",
        "list_vector_search_endpoints",
        "get_vector_search_endpoint",
        "list_vector_search_indexes",
        "get_vector_search_index",
        "list_genie_spaces",
        "get_genie_space",
    } <= tools
