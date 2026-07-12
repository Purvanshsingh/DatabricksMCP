"""Validated process configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal, cast

Transport = Literal["stdio", "streamable-http"]
AccessMode = Literal["read-only"]


def _integer(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    transport: Transport = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    access_mode: AccessMode = "read-only"
    default_page_size: int = 100
    maximum_page_size: int = 200

    @classmethod
    def from_env(cls) -> Settings:
        """Load and validate settings without reading Databricks credentials."""
        transport = os.getenv("DATABRICKS_MCP_TRANSPORT", "stdio").lower()
        if transport not in {"stdio", "streamable-http"}:
            raise ValueError("DATABRICKS_MCP_TRANSPORT must be 'stdio' or 'streamable-http'")

        access_mode = os.getenv("DATABRICKS_MCP_ACCESS_MODE", "read-only").lower()
        if access_mode != "read-only":
            raise ValueError("Phase 1 supports only DATABRICKS_MCP_ACCESS_MODE=read-only")

        log_level = os.getenv("DATABRICKS_MCP_LOG_LEVEL", "INFO").upper()
        if log_level not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
            raise ValueError("DATABRICKS_MCP_LOG_LEVEL is not a valid log level")

        return cls(
            transport=cast(Transport, transport),
            host=os.getenv("DATABRICKS_MCP_HOST", "127.0.0.1"),
            port=_integer("DATABRICKS_MCP_PORT", 8000, minimum=1, maximum=65535),
            log_level=log_level,
            access_mode=cast(AccessMode, access_mode),
            default_page_size=_integer(
                "DATABRICKS_MCP_DEFAULT_PAGE_SIZE", 100, minimum=1, maximum=200
            ),
            maximum_page_size=200,
        )
