"""Fixtures for opt-in live-workspace integration tests.

These tests run only when ``DATABRICKS_MCP_LIVE=1`` and real Databricks
credentials are configured through unified authentication (e.g.
``~/.databrickscfg``). They never read or print the token. Without either, the
whole suite skips, so it is safe in CI and for contributors with no workspace.
"""

from __future__ import annotations

import os

import pytest

from databricks_mcp.services import DatabricksService


def _live_enabled() -> bool:
    return os.environ.get("DATABRICKS_MCP_LIVE") == "1"


@pytest.fixture(autouse=True)
def _require_live() -> None:
    if not _live_enabled():
        pytest.skip("live tests disabled (set DATABRICKS_MCP_LIVE=1)")


@pytest.fixture(scope="session")
def service() -> DatabricksService:
    if not _live_enabled():
        pytest.skip("set DATABRICKS_MCP_LIVE=1 to run live workspace tests")
    try:
        svc = DatabricksService.from_environment()
        svc.current_identity()
    except Exception as error:
        pytest.skip(f"no usable Databricks credentials: {type(error).__name__}: {error}")
    return svc


@pytest.fixture(scope="session")
def warehouse_id() -> str:
    wid = os.environ.get("DATABRICKS_MCP_TEST_WAREHOUSE_ID")
    if not wid:
        pytest.skip("set DATABRICKS_MCP_TEST_WAREHOUSE_ID to run SQL tests")
    return wid


@pytest.fixture(scope="session")
def sample_table() -> str:
    return os.environ.get("DATABRICKS_MCP_TEST_TABLE", "samples.bakehouse.sales_transactions")
