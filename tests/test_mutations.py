from __future__ import annotations

import pytest

from databricks_mcp.approvals import ApprovalManager
from databricks_mcp.audit import AuditLog
from databricks_mcp.mutations import ApprovalRequiredError, MutationController
from databricks_mcp.policy import PolicyDeniedError, PolicyEngine, RiskClass
from databricks_mcp.registry import ToolSpec


def _controller(access_mode: str = "controlled-write", allow: list[str] | None = None) -> tuple:
    policy = PolicyEngine(access_mode=access_mode, write_allow=allow or [])
    audit = AuditLog()
    controller = MutationController(policy, ApprovalManager(), audit)
    return controller, audit


WRITE = ToolSpec("run_job", "jobs", RiskClass.WRITE, "run a job", changes_state=True)
DESTRUCTIVE = ToolSpec(
    "delete_job", "jobs", RiskClass.DESTRUCTIVE, "delete a job", changes_state=True
)


def test_denied_write_raises_and_audits() -> None:
    controller, audit = _controller(access_mode="read-only")
    with pytest.raises(PolicyDeniedError):
        controller.run(WRITE, {"job_id": 1}, lambda: "done")
    events = list(audit.events())
    assert events[-1].outcome == "denied"
    assert events[-1].allowed is False


def test_allowed_write_executes_without_token() -> None:
    controller, audit = _controller(allow=["run_job"])
    result = controller.run(WRITE, {"job_id": 1}, lambda: {"run_id": 99})
    assert result == {"run_id": 99}
    assert list(audit.events())[-1].outcome == "executed"


def test_destructive_dry_run_returns_plan_and_token() -> None:
    controller, _ = _controller(allow=["delete_job"])
    plan = controller.run(DESTRUCTIVE, {"job_id": 1}, lambda: "boom", dry_run=True)
    assert plan["dry_run"] is True
    assert plan["requires_approval"] is True
    assert plan["approval"]["token"]


def test_destructive_requires_approval_token() -> None:
    controller, _ = _controller(allow=["delete_job"])
    with pytest.raises(ApprovalRequiredError):
        controller.run(DESTRUCTIVE, {"job_id": 1}, lambda: "boom")


def test_destructive_executes_with_valid_token() -> None:
    controller, audit = _controller(allow=["delete_job"])
    plan = controller.run(DESTRUCTIVE, {"job_id": 1}, lambda: "unused", dry_run=True)
    token = plan["approval"]["token"]
    result = controller.run(
        DESTRUCTIVE, {"job_id": 1}, lambda: {"deleted": True}, approval_token=token
    )
    assert result == {"deleted": True}
    assert list(audit.events())[-1].outcome == "executed"


def test_token_for_different_arguments_is_rejected() -> None:
    controller, _ = _controller(allow=["delete_job"])
    plan = controller.run(DESTRUCTIVE, {"job_id": 1}, lambda: "x", dry_run=True)
    token = plan["approval"]["token"]
    with pytest.raises(ApprovalRequiredError):
        controller.run(DESTRUCTIVE, {"job_id": 2}, lambda: "x", approval_token=token)


def test_execution_error_is_audited_and_reraised() -> None:
    controller, audit = _controller(allow=["run_job"])

    def boom() -> None:
        raise RuntimeError("upstream failed")

    with pytest.raises(RuntimeError, match="upstream failed"):
        controller.run(WRITE, {"job_id": 1}, boom)
    assert list(audit.events())[-1].outcome == "error"
