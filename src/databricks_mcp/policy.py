"""Capability classification and deny-by-default policy checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskClass(StrEnum):
    """Security and side-effect classification for an MCP capability."""

    READ = "read"
    WRITE = "write"
    DESTRUCTIVE = "destructive"
    PRIVILEGED = "privileged"
    COST_SENSITIVE = "cost-sensitive"


@dataclass(frozen=True, slots=True)
class Capability:
    """Policy metadata attached to a tool."""

    name: str
    risk: RiskClass


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """An auditable authorization result."""

    allowed: bool
    reason: str


class PolicyDeniedError(PermissionError):
    """Raised when policy rejects a capability."""


class PolicyEngine:
    """Phase 1 policy engine that permits read-only capabilities only."""

    def authorize(self, capability: Capability) -> PolicyDecision:
        if capability.risk is RiskClass.READ:
            return PolicyDecision(True, "read-only capability allowed")
        return PolicyDecision(
            False,
            f"capability '{capability.name}' has disallowed risk class '{capability.risk.value}'",
        )

    def require(self, capability: Capability) -> None:
        decision = self.authorize(capability)
        if not decision.allowed:
            raise PolicyDeniedError(decision.reason)
