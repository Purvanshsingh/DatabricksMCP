from __future__ import annotations

import asyncio

import pytest

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _server(**overrides: object) -> object:
    settings = Settings(**overrides)  # type: ignore[arg-type]
    return create_server(settings, service=DatabricksService(FakeWorkspaceClient()))


def test_write_tools_absent_in_read_only_mode() -> None:
    tools = {t.name for t in asyncio.run(_server().list_tools())}
    assert "run_job" not in tools
    assert "delete_job" not in tools


def test_write_tools_present_in_controlled_write_mode() -> None:
    server = _server(access_mode="controlled-write", write_tools_allow=("run_job",))
    tools = {t.name for t in asyncio.run(server.list_tools())}
    assert {"run_job", "cancel_job_run", "delete_job"} <= tools


def test_run_job_denied_when_not_allowlisted() -> None:
    server = _server(access_mode="controlled-write", write_tools_allow=())
    with pytest.raises(Exception, match="allowlist"):
        asyncio.run(server.call_tool("run_job", {"job_id": 1}))


def test_run_job_executes_when_allowlisted() -> None:
    server = _server(access_mode="controlled-write", write_tools_allow=("run_job",))
    _content, structured = asyncio.run(server.call_tool("run_job", {"job_id": 7}))
    assert structured["run_id"] == 555
    assert structured["status"] == "submitted"


def test_delete_job_requires_approval_then_succeeds() -> None:
    server = _server(access_mode="controlled-write", write_tools_allow=("delete_job",))
    # Without a token: denied, but a dry-run returns a plan with a token.
    with pytest.raises(Exception, match="requires approval"):
        asyncio.run(server.call_tool("delete_job", {"job_id": 3}))
    _c, plan = asyncio.run(server.call_tool("delete_job", {"job_id": 3, "dry_run": True}))
    assert plan["requires_approval"] is True
    token = plan["approval"]["token"]
    _c, result = asyncio.run(server.call_tool("delete_job", {"job_id": 3, "approval_token": token}))
    assert result["deleted"] is True


def test_delete_job_dry_run_does_not_execute() -> None:
    client = FakeWorkspaceClient()
    settings = Settings(access_mode="controlled-write", write_tools_allow=("delete_job",))
    server = create_server(settings, service=DatabricksService(client))
    asyncio.run(server.call_tool("delete_job", {"job_id": 9, "dry_run": True}))
    # delete records -(1000+job_id); ensure it was NOT called during dry-run.
    assert -1009 not in client.jobs.run_calls
