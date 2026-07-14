"""MCP server construction and tool registration."""

from __future__ import annotations

from typing import Any, TypeAlias

from mcp.server.fastmcp import FastMCP

from databricks_mcp import __version__
from databricks_mcp.config import Settings
from databricks_mcp.policy import Capability, PolicyEngine, RiskClass
from databricks_mcp.services import DatabricksService

ToolObject: TypeAlias = dict[str, Any]


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

    def require_read(name: str) -> None:
        policy_engine.require(Capability(name=name, risk=RiskClass.READ))

    def get_databricks() -> DatabricksService:
        # Resolve credentials only when a Databricks-backed tool is called so
        # the process can start and report health before upstream auth is ready.
        nonlocal databricks
        if databricks is None:
            databricks = DatabricksService.from_environment()
        return databricks

    def checked_limit(limit: int) -> int:
        if not 1 <= limit <= settings.maximum_page_size:
            raise ValueError(f"limit must be between 1 and {settings.maximum_page_size}")
        return limit

    @mcp.tool()
    def health() -> ToolObject:
        """Return process health without accessing Databricks or exposing credentials."""
        require_read("health")
        return {
            "status": "ok",
            "version": __version__,
            "access_mode": settings.access_mode,
            "transport": settings.transport,
        }

    @mcp.tool()
    def current_identity() -> ToolObject:
        """Return the Databricks identity selected by unified authentication."""
        require_read("current_identity")
        return get_databricks().current_identity()

    @mcp.tool()
    def list_catalogs(limit: int = settings.default_page_size) -> list[ToolObject]:
        """List accessible Unity Catalog catalogs, bounded to at most 200 results."""
        require_read("list_catalogs")
        return get_databricks().list_catalogs(limit=checked_limit(limit))

    @mcp.tool()
    def list_sql_warehouses(limit: int = settings.default_page_size) -> list[ToolObject]:
        """List accessible SQL warehouses, bounded to at most 200 results."""
        require_read("list_sql_warehouses")
        return get_databricks().list_warehouses(limit=checked_limit(limit))

    return mcp
