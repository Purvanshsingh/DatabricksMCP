"""Short-lived, single-use approval tokens for high-risk mutations.

An approval token is bound to a specific tool and a fingerprint of its
arguments, expires after a configurable TTL, and can be redeemed only once.
This prevents an approval for one action from authorizing a different action,
and prevents replay. Session identifiers are never used as authorization.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass


def fingerprint(tool: str, arguments: Mapping[str, object]) -> str:
    """Return a stable hash of a tool name and its arguments."""
    payload = json.dumps([tool, arguments], sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ApprovalChallenge:
    """A token the caller must present to execute the bound mutation."""

    token: str
    tool: str
    expires_in_seconds: int


class ApprovalManager:
    """Issues and verifies approval tokens bound to (tool, arguments)."""

    def __init__(
        self, *, ttl_seconds: int = 300, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._ttl = ttl_seconds
        self._clock = clock
        # token -> (fingerprint, expiry)
        self._pending: dict[str, tuple[str, float]] = {}

    def issue(self, tool: str, arguments: Mapping[str, object]) -> ApprovalChallenge:
        token = secrets.token_urlsafe(24)
        self._pending[token] = (fingerprint(tool, arguments), self._clock() + self._ttl)
        return ApprovalChallenge(token=token, tool=tool, expires_in_seconds=self._ttl)

    def verify(self, token: str, tool: str, arguments: Mapping[str, object]) -> bool:
        entry = self._pending.get(token)
        if entry is None:
            return False
        expected_fingerprint, expiry = entry
        # Redeem the token regardless of outcome so it can never be reused.
        del self._pending[token]
        if self._clock() > expiry:
            return False
        return expected_fingerprint == fingerprint(tool, arguments)

    def purge_expired(self) -> None:
        now = self._clock()
        for token in [t for t, (_, exp) in self._pending.items() if now > exp]:
            del self._pending[token]
