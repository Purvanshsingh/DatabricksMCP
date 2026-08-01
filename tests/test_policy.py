from __future__ import annotations

import pytest

from databricks_mcp.policy import (
    Capability,
    PolicyDeniedError,
    PolicyEngine,
    RiskClass,
)


def test_read_capability_is_allowed() -> None:
    decision = PolicyEngine().authorize(Capability("list_catalogs", RiskClass.READ))
    assert decision.allowed is True


@pytest.mark.parametrize("risk", list(RiskClass)[1:])
def test_non_read_capabilities_are_denied_in_read_only(risk: RiskClass) -> None:
    engine = PolicyEngine()
    with pytest.raises(PolicyDeniedError, match="writes are disabled"):
        engine.require(Capability("unsafe_operation", risk))


def test_write_denied_when_not_in_allowlist() -> None:
    engine = PolicyEngine(access_mode="controlled-write", write_allow=["run_job"])
    decision = engine.authorize(Capability("delete_job", RiskClass.WRITE))
    assert decision.allowed is False
    assert "allowlist" in decision.reason


def test_write_allowed_when_allowlisted() -> None:
    engine = PolicyEngine(access_mode="controlled-write", write_allow=["run_job"])
    decision = engine.authorize(Capability("run_job", RiskClass.WRITE))
    assert decision.allowed is True
    assert decision.requires_approval is False


@pytest.mark.parametrize("risk", [RiskClass.DESTRUCTIVE, RiskClass.PRIVILEGED])
def test_high_risk_requires_approval(risk: RiskClass) -> None:
    engine = PolicyEngine(access_mode="controlled-write", write_allow=["danger"])
    decision = engine.authorize(Capability("danger", risk))
    assert decision.allowed is True
    assert decision.requires_approval is True
