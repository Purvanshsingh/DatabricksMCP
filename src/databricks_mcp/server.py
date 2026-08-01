"""MCP server construction and capability-pack registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from databricks_mcp.approvals import ApprovalManager
from databricks_mcp.audit import AuditLog
from databricks_mcp.config import Settings
from databricks_mcp.mutations import MutationController
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
    policy_engine = policy or PolicyEngine(
        access_mode=settings.access_mode,
        write_allow=settings.write_tools_allow,
    )
    approvals = ApprovalManager(ttl_seconds=settings.approval_ttl_seconds)
    audit = AuditLog()
    controller = MutationController(policy_engine, approvals, audit)

    mcp = FastMCP(
        "DatabricksMCP",
        instructions=(
            "A safety-first Databricks server. Read tools are always available and "
            "bounded. State-changing tools are disabled unless explicitly enabled, "
            "and destructive actions require an approval token. Never ask for "
            "credentials as tool arguments."
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

    registrar = Registrar(mcp, settings, policy_engine, service_provider, controller)
    register_all(registrar)
    return mcp
