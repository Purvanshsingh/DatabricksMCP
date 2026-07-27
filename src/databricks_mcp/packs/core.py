"""Core diagnostics pack: health, identity, and capability introspection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp import __version__
from databricks_mcp.policy import Capability, RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "core"


def register(registrar: Registrar) -> None:
    settings = registrar.settings

    @registrar.tool(
        ToolSpec(
            "health",
            NAME,
            RiskClass.READ,
            "Return process health without accessing Databricks or exposing credentials.",
        )
    )
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "access_mode": settings.access_mode,
            "transport": settings.transport,
        }

    @registrar.tool(
        ToolSpec(
            "server_info",
            NAME,
            RiskClass.READ,
            "Return server identity, version, transport, and enabled capability packs.",
        )
    )
    def server_info() -> dict[str, Any]:
        specs = registrar.specs
        packs = sorted({spec.pack for spec in specs.values()})
        return {
            "name": "DatabricksMCP",
            "version": __version__,
            "transport": settings.transport,
            "access_mode": settings.access_mode,
            "packs": packs,
            "tool_count": len(specs),
        }

    @registrar.tool(
        ToolSpec(
            "list_enabled_capabilities",
            NAME,
            RiskClass.READ,
            "List every enabled tool with its risk classification and operational metadata.",
        )
    )
    def list_enabled_capabilities() -> list[dict[str, Any]]:
        specs = sorted(registrar.specs.values(), key=lambda spec: (spec.pack, spec.name))
        return [spec.describe() for spec in specs]

    @registrar.tool(
        ToolSpec(
            "get_policy_status",
            NAME,
            RiskClass.READ,
            "Return the current access mode and which risk classes are permitted.",
        )
    )
    def get_policy_status() -> dict[str, Any]:
        allowed = [
            risk.value
            for risk in RiskClass
            if registrar.policy.authorize(Capability(name="_probe", risk=risk)).allowed
        ]
        return {"access_mode": settings.access_mode, "allowed_risk_classes": allowed}

    @registrar.tool(
        ToolSpec(
            "current_identity",
            NAME,
            RiskClass.READ,
            "Return the Databricks identity selected by unified authentication.",
        )
    )
    def current_identity() -> dict[str, Any]:
        return registrar.service.current_identity()
