"""MCP server construction and capability-pack registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from databricks_mcp.config import Settings
from databricks_mcp.packs import register_all
from databricks_mcp.policy import PolicyEngine
from databricks_mcp.registry import Registrar
from databricks_mcp.services import DatabricksService


def create_server(
    settings: Settings,
    *,
    service: DatabricksService | None = None,
    policy: PolicyEngine | None = None,
) -> FastMCP:
    """Create an isolated server instance for a process or test."""
    databricks = service
    policy_engine = policy or PolicyEngine()

    mcp = FastMCP(
        "DatabricksMCP",
        instructions=(
            "A safety-first Databricks server. Phase 1 tools are read-only and "
            "results are bounded. Never ask for credentials as tool arguments."
        ),
        host=settings.host,
        port=settings.port,
    )

    def service_provider() -> DatabricksService:
        # Resolve credentials only when a Databricks-backed tool is called so the
        # process can start and report health before upstream auth is ready.
        nonlocal databricks
        if databricks is None:
            databricks = DatabricksService.from_environment()
        return databricks

    registrar = Registrar(mcp, settings, policy_engine, service_provider)
    register_all(registrar)
    return mcp
