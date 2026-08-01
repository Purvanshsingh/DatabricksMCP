from __future__ import annotations

from databricks_mcp.approvals import ApprovalManager


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_valid_token_verifies_once() -> None:
    manager = ApprovalManager(ttl_seconds=300)
    args = {"job_id": 7}
    token = manager.issue("run_job", args).token
    assert manager.verify(token, "run_job", args) is True
    # single use: second verify fails
    assert manager.verify(token, "run_job", args) is False


def test_token_bound_to_arguments() -> None:
    manager = ApprovalManager()
    token = manager.issue("run_job", {"job_id": 7}).token
    assert manager.verify(token, "run_job", {"job_id": 8}) is False


def test_token_bound_to_tool() -> None:
    manager = ApprovalManager()
    token = manager.issue("run_job", {"job_id": 7}).token
    assert manager.verify(token, "delete_job", {"job_id": 7}) is False


def test_expired_token_is_rejected() -> None:
    clock = FakeClock()
    manager = ApprovalManager(ttl_seconds=60, clock=clock)
    token = manager.issue("run_job", {"job_id": 7}).token
    clock.now = 61.0
    assert manager.verify(token, "run_job", {"job_id": 7}) is False


def test_unknown_token_is_rejected() -> None:
    assert ApprovalManager().verify("nope", "run_job", {}) is False
