from __future__ import annotations

import asyncio

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_list_jobs_is_bounded() -> None:
    jobs = _service().list_jobs(limit=1)
    assert jobs == [{"job_id": 1, "settings": {"name": "etl"}}]


def test_get_job_returns_object() -> None:
    assert _service().get_job(7)["job_id"] == 7


def test_list_job_runs_filters_by_job_id() -> None:
    client = FakeWorkspaceClient()
    runs = DatabricksService(client).list_job_runs(job_id=42, limit=10)
    assert client.jobs.run_calls == [42]
    assert runs[0]["job_id"] == 42


def test_get_job_run_and_output() -> None:
    service = _service()
    assert service.get_job_run(10)["run_id"] == 10
    assert service.get_job_run_output(10) == {"run_id": 10, "logs": "done"}


def test_jobs_tools_registered_and_invocable() -> None:
    server = create_server(Settings(), service=_service())
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {"list_jobs", "get_job", "list_job_runs", "get_job_run", "get_job_run_output"} <= tools
    _content, structured = asyncio.run(server.call_tool("list_job_runs", {"job_id": 3}))
    assert structured is not None
