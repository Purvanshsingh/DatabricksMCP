from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_experiments_and_runs() -> None:
    service = _service()
    assert service.list_experiments(limit=10)[0]["experiment_id"] == "e1"
    assert service.get_experiment("e1")["experiment"]["experiment_id"] == "e1"
    runs = service.search_experiment_runs(experiment_id="e1", limit=10)
    assert runs[0]["info"]["experiment_id"] == "e1"


def test_registered_models_and_versions() -> None:
    service = _service()
    assert service.list_registered_models(limit=10)[0]["name"] == "fraud"
    assert service.get_registered_model("fraud")["registered_model"]["name"] == "fraud"
    version = service.get_model_version("fraud", "3")
    assert version["model_version"]["version"] == "3"


def test_mlflow_tools_registered() -> None:
    server = create_server(Settings(), service=_service())
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {
        "list_experiments",
        "get_experiment",
        "search_experiment_runs",
        "list_registered_models",
        "get_registered_model",
        "get_model_version",
    } <= tools
