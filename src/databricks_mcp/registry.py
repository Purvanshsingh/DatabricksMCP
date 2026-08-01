"""Capability packs and policy-enforced tool registration.

A *capability pack* is a cohesive group of tools for one Databricks domain
(catalog, SQL, jobs, ...). Packs register their tools through a :class:`Registrar`,
which uniformly enforces the policy engine, records tool metadata for
introspection, and exposes shared helpers. Business logic never imports MCP
classes directly; only the registrar touches the server object.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from databricks_mcp.policy import Capability, PolicyEngine, RiskClass

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from databricks_mcp.config import Settings
    from databricks_mcp.mutations import MutationController
    from databricks_mcp.services import DatabricksService

P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """Policy and operational metadata declared by every registered tool."""

    name: str
    pack: str
    risk: RiskClass
    summary: str
    changes_state: bool = False
    cost_sensitive: bool = False
    supports_dry_run: bool = False
    idempotent: bool = True

    def describe(self) -> dict[str, object]:
        """Return a JSON-safe description for capability introspection tools."""
        return {
            "name": self.name,
            "pack": self.pack,
            "risk": self.risk.value,
            "summary": self.summary,
            "changes_state": self.changes_state,
            "cost_sensitive": self.cost_sensitive,
            "supports_dry_run": self.supports_dry_run,
            "idempotent": self.idempotent,
        }


class Registrar:
    """Registers pack tools onto a FastMCP server with uniform policy checks."""

    def __init__(
        self,
        mcp: FastMCP,
        settings: Settings,
        policy: PolicyEngine,
        service_provider: Callable[[], DatabricksService],
        mutations: MutationController | None = None,
    ) -> None:
        self._mcp = mcp
        self.settings = settings
        self.policy = policy
        self._service_provider = service_provider
        self._mutations = mutations
        self._specs: dict[str, ToolSpec] = {}

    @property
    def mutations(self) -> MutationController:
        """The mutation controller for write tools; raises if not configured."""
        if self._mutations is None:
            raise RuntimeError("mutation controller is not configured on this server")
        return self._mutations

    @property
    def specs(self) -> dict[str, ToolSpec]:
        """Return registered tool specifications keyed by tool name."""
        return dict(self._specs)

    @property
    def service(self) -> DatabricksService:
        """Resolve the Databricks service lazily, only when a tool needs it."""
        return self._service_provider()

    def checked_limit(self, limit: int) -> int:
        """Validate a caller-supplied result limit against the configured ceiling."""
        maximum = self.settings.maximum_page_size
        if not 1 <= limit <= maximum:
            raise ValueError(f"limit must be between 1 and {maximum}")
        return limit

    def tool(self, spec: ToolSpec) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Register ``spec``'s function as an MCP tool guarded by the policy engine."""
        if spec.name in self._specs:
            raise ValueError(f"tool '{spec.name}' is already registered")

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            self._specs[spec.name] = spec

            @functools.wraps(func)
            def guarded(*args: P.args, **kwargs: P.kwargs) -> R:
                self.policy.require(Capability(name=spec.name, risk=spec.risk))
                return func(*args, **kwargs)

            self._mcp.tool(name=spec.name, description=spec.summary)(guarded)
            return guarded

        return decorator
