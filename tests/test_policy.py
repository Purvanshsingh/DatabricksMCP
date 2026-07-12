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
def test_non_read_capabilities_are_denied(risk: RiskClass) -> None:
    engine = PolicyEngine()
    capability = Capability("unsafe_operation", risk)

    with pytest.raises(PolicyDeniedError, match="disallowed risk class"):
        engine.require(capability)
