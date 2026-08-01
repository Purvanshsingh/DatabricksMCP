"""Capability classification and deny-by-default policy checks."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class RiskClass(StrEnum):
    """Security and side-effect classification for an MCP capability."""

    READ = "read"
    WRITE = "write"
    DESTRUCTIVE = "destructive"
    PRIVILEGED = "privileged"
    COST_SENSITIVE = "cost-sensitive"


# Risk classes that must never execute without a valid approval token, even when
# the access mode and allowlist would otherwise permit them.
_APPROVAL_REQUIRED = frozenset({RiskClass.DESTRUCTIVE, RiskClass.PRIVILEGED})


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
    requires_approval: bool = False


class PolicyDeniedError(PermissionError):
    """Raised when policy rejects a capability."""


class PolicyEngine:
    """Deny-by-default engine.

    Read capabilities are always allowed. Any state-changing capability is denied
    unless the server runs in ``controlled-write`` mode *and* the specific tool is
    on the write allowlist; destructive and privileged capabilities additionally
    require a valid approval token, surfaced via ``requires_approval``.
    """

    def __init__(
        self,
        *,
        access_mode: str = "read-only",
        write_allow: Iterable[str] = (),
    ) -> None:
        self._access_mode = access_mode
        self._write_allow = frozenset(write_allow)

    @property
    def access_mode(self) -> str:
        return self._access_mode

    def authorize(self, capability: Capability) -> PolicyDecision:
        if capability.risk is RiskClass.READ:
            return PolicyDecision(True, "read-only capability allowed")
        if self._access_mode != "controlled-write":
            return PolicyDecision(
                False,
                f"capability '{capability.name}' is a {capability.risk.value} operation "
                f"and writes are disabled in access mode '{self._access_mode}'",
            )
        if capability.name not in self._write_allow:
            return PolicyDecision(
                False,
                f"capability '{capability.name}' is not in the write allowlist",
            )
        return PolicyDecision(
            True,
            f"{capability.risk.value} capability '{capability.name}' allowed by policy",
            requires_approval=capability.risk in _APPROVAL_REQUIRED,
        )

    def require(self, capability: Capability) -> PolicyDecision:
        decision = self.authorize(capability)
        if not decision.allowed:
            raise PolicyDeniedError(decision.reason)
        return decision
