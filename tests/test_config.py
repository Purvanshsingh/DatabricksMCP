from __future__ import annotations

import pytest

from databricks_mcp.config import Settings


def test_defaults_are_local_and_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "DATABRICKS_MCP_TRANSPORT",
        "DATABRICKS_MCP_HOST",
        "DATABRICKS_MCP_PORT",
        "DATABRICKS_MCP_LOG_LEVEL",
        "DATABRICKS_MCP_ACCESS_MODE",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings.from_env()

    assert settings.transport == "stdio"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.access_mode == "read-only"


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("DATABRICKS_MCP_TRANSPORT", "sse", "stdio"),
        ("DATABRICKS_MCP_ACCESS_MODE", "write", "read-only"),
        ("DATABRICKS_MCP_LOG_LEVEL", "verbose", "log level"),
        ("DATABRICKS_MCP_PORT", "zero", "integer"),
        ("DATABRICKS_MCP_PORT", "70000", "between"),
    ],
)
def test_invalid_environment_is_rejected(
    monkeypatch: pytest.MonkeyPatch, name: str, value: str, message: str
) -> None:
    monkeypatch.setenv(name, value)

    with pytest.raises(ValueError, match=message):
        Settings.from_env()
