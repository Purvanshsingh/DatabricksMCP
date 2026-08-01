from __future__ import annotations

import pytest
from mcp.server.fastmcp import FastMCP

from databricks_mcp.config import Settings
from databricks_mcp.policy import PolicyDeniedError, PolicyEngine, RiskClass
from databricks_mcp.registry import Registrar, ToolSpec
from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _registrar() -> Registrar:
    mcp = FastMCP("test")
    return Registrar(
        mcp,
        Settings(),
        PolicyEngine(),
        lambda: DatabricksService(FakeWorkspaceClient()),
    )


def test_read_tool_is_allowed_and_recorded() -> None:
    registrar = _registrar()

    @registrar.tool(ToolSpec("ping", "core", RiskClass.READ, "ping"))
    def ping() -> dict[str, str]:
        return {"ok": "yes"}

    assert ping() == {"ok": "yes"}
    assert registrar.specs["ping"].risk is RiskClass.READ


def test_write_tool_is_denied_by_policy() -> None:
    registrar = _registrar()

    @registrar.tool(ToolSpec("mutate", "core", RiskClass.WRITE, "mutate", changes_state=True))
    def mutate() -> dict[str, str]:
        return {"done": "yes"}

    with pytest.raises(PolicyDeniedError):
        mutate()


def test_duplicate_registration_is_rejected() -> None:
    registrar = _registrar()

    @registrar.tool(ToolSpec("dup", "core", RiskClass.READ, "dup"))
    def first() -> dict[str, str]:
        return {}

    with pytest.raises(ValueError, match="already registered"):

        @registrar.tool(ToolSpec("dup", "core", RiskClass.READ, "dup again"))
        def second() -> dict[str, str]:
            return {}


def test_checked_limit_enforces_ceiling() -> None:
    registrar = _registrar()
    assert registrar.checked_limit(50) == 50
    with pytest.raises(ValueError, match="between 1 and 200"):
        registrar.checked_limit(0)
    with pytest.raises(ValueError, match="between 1 and 200"):
        registrar.checked_limit(201)
