"""Structured audit logging for tool invocations and policy decisions.

Audit events record *that* a tool ran and how policy decided, never the tool
arguments, results, secrets, or SQL text. This lets an operator reconstruct who
did what without leaking governed data into logs.
"""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Iterable
from dataclasses import asdict, dataclass

_LOGGER = logging.getLogger("databricks_mcp.audit")


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """A single auditable decision or outcome. Contains no argument values."""

    tool: str
    risk: str
    allowed: bool
    outcome: str
    reason: str
    correlation_id: str | None = None
    duration_ms: float | None = None


class AuditLog:
    """In-memory ring buffer of audit events that also emits structured logs."""

    def __init__(self, *, capacity: int = 1000) -> None:
        self._events: deque[AuditEvent] = deque(maxlen=capacity)

    def record(self, event: AuditEvent) -> None:
        self._events.append(event)
        _LOGGER.info(
            "audit tool=%s risk=%s allowed=%s outcome=%s correlation_id=%s duration_ms=%s",
            event.tool,
            event.risk,
            event.allowed,
            event.outcome,
            event.correlation_id,
            event.duration_ms,
        )

    def events(self) -> Iterable[AuditEvent]:
        return tuple(self._events)

    def as_dicts(self) -> list[dict[str, object]]:
        return [asdict(event) for event in self._events]
