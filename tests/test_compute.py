from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_list_clusters_is_bounded() -> None:
    assert _service().list_clusters(limit=1) == [
        {"cluster_id": "c1", "cluster_name": "analytics", "state": "RUNNING"}
    ]


def test_get_cluster_and_events() -> None:
    service = _service()
    assert service.get_cluster("c1")["state"] == "RUNNING"
    events = service.list_cluster_events(cluster_id="c1", limit=10)
    assert events[0]["cluster_id"] == "c1"


def test_node_types_and_spark_versions() -> None:
    service = _service()
    assert service.list_node_types()["node_types"][0]["node_type_id"] == "m5.large"
    assert service.list_spark_versions()["versions"][0]["key"].startswith("14.3")


def test_cluster_policies() -> None:
    service = _service()
    assert service.list_cluster_policies(limit=10)[0]["policy_id"] == "pol1"
    assert service.get_cluster_policy("pol1")["name"] == "default"


def test_compute_tools_registered() -> None:
    server = create_server(Settings(), service=_service())
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {
        "list_clusters",
        "get_cluster",
        "list_cluster_events",
        "list_cluster_policies",
        "get_cluster_policy",
        "list_node_types",
        "list_spark_versions",
    } <= tools
