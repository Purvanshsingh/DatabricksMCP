"""The mutation safety contract: policy, dry-run, approval, and audit in one place.

Every state-changing tool routes through :meth:`MutationController.run`, which:

1. asks the policy engine whether the capability may run at all;
2. in dry-run mode, returns a plan (and, for high-risk actions, an approval
   challenge) *without* executing;
3. for destructive/privileged actions, requires a valid approval token bound to
   the exact tool and arguments;
4. executes, and records an audit event for every branch.

Arguments are never written to the audit log; only a fingerprint is retained.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import Any

from databricks_mcp.approvals import ApprovalManager, fingerprint
from databricks_mcp.audit import AuditEvent, AuditLog
from databricks_mcp.policy import Capability, PolicyDeniedError, PolicyEngine
from databricks_mcp.registry import ToolSpec


class ApprovalRequiredError(PermissionError):
    """Raised when a high-risk mutation is attempted without a valid approval token."""


class MutationController:
    """Coordinates policy, dry-run planning, approval, and audit for mutations."""

    def __init__(
        self,
        policy: PolicyEngine,
        approvals: ApprovalManager,
        audit: AuditLog,
        *,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._policy = policy
        self._approvals = approvals
        self._audit = audit
        self._clock = clock

    def run(
        self,
        spec: ToolSpec,
        arguments: Mapping[str, object],
        execute: Callable[[], Any],
        *,
        dry_run: bool = False,
        approval_token: str | None = None,
        correlation_id: str | None = None,
    ) -> Any:
        capability = Capability(name=spec.name, risk=spec.risk)
        decision = self._policy.authorize(capability)

        if not decision.allowed:
            self._record(
                spec, allowed=False, outcome="denied", reason=decision.reason, cid=correlation_id
            )
            raise PolicyDeniedError(decision.reason)

        if dry_run:
            plan: dict[str, Any] = {
                "dry_run": True,
                "tool": spec.name,
                "risk": spec.risk.value,
                "changes_state": spec.changes_state,
                "requires_approval": decision.requires_approval,
                "arguments_fingerprint": fingerprint(spec.name, arguments),
            }
            if decision.requires_approval:
                challenge = self._approvals.issue(spec.name, arguments)
                plan["approval"] = {
                    "token": challenge.token,
                    "expires_in_seconds": challenge.expires_in_seconds,
                }
            self._record(
                spec, allowed=True, outcome="dry-run", reason="plan generated", cid=correlation_id
            )
            return plan

        approved = (not decision.requires_approval) or (
            approval_token is not None
            and self._approvals.verify(approval_token, spec.name, arguments)
        )
        if not approved:
            self._record(
                spec,
                allowed=False,
                outcome="approval-required",
                reason="missing or invalid approval token",
                cid=correlation_id,
            )
            raise ApprovalRequiredError(
                f"'{spec.name}' requires approval; call again with dry_run=true to obtain a token"
            )

        start = self._clock()
        try:
            result = execute()
        except Exception as error:
            self._record(
                spec,
                allowed=True,
                outcome="error",
                reason=type(error).__name__,
                cid=correlation_id,
                duration_ms=(self._clock() - start) * 1000,
            )
            raise
        self._record(
            spec,
            allowed=True,
            outcome="executed",
            reason="ok",
            cid=correlation_id,
            duration_ms=(self._clock() - start) * 1000,
        )
        return result

    def _record(
        self,
        spec: ToolSpec,
        *,
        allowed: bool,
        outcome: str,
        reason: str,
        cid: str | None,
        duration_ms: float | None = None,
    ) -> None:
        self._audit.record(
            AuditEvent(
                tool=spec.name,
                risk=spec.risk.value,
                allowed=allowed,
                outcome=outcome,
                reason=reason,
                correlation_id=cid,
                duration_ms=duration_ms,
            )
        )
