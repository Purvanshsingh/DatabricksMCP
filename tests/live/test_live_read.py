"""Live read-only integration tests against a real Databricks workspace.

Run with:

    DATABRICKS_MCP_LIVE=1 \
    DATABRICKS_MCP_TEST_WAREHOUSE_ID=<id> \
    .venv/bin/pytest tests/live -m live -q

All tests are read-only. Operational lists (jobs, pipelines, clusters, serving,
etc.) may legitimately be empty on a fresh or Free Edition workspace; those
tests assert only that the call succeeds and returns the right shape.
"""

from __future__ import annotations

import pytest

from databricks_mcp.services import DatabricksService
from databricks_mcp.sqlguard import UnsafeSqlError, validate_read_only_sql

pytestmark = pytest.mark.live


def test_identity(service: DatabricksService) -> None:
    who = service.current_identity()
    assert who.get("userName") or who.get("id") or who.get("displayName")


def test_list_catalogs_includes_samples(service: DatabricksService) -> None:
    names = {c.get("name") for c in service.list_catalogs(limit=100)}
    assert "samples" in names


def test_browse_sample_table_end_to_end(service: DatabricksService, sample_table: str) -> None:
    catalog, schema, table = sample_table.split(".")

    schemas = {s.get("name") for s in service.list_schemas(catalog_name=catalog, limit=100)}
    assert schema in schemas

    tables = {
        t.get("name")
        for t in service.list_tables(catalog_name=catalog, schema_name=schema, limit=200)
    }
    assert table in tables

    detail = service.get_table(sample_table)
    assert str(detail.get("full_name", "")).endswith(table)

    columns = service.list_columns(sample_table)
    assert len(columns) > 0
    assert all("name" in column for column in columns)


def test_list_and_get_warehouse(service: DatabricksService, warehouse_id: str) -> None:
    warehouses = service.list_warehouses(limit=50)
    assert isinstance(warehouses, list)
    detail = service.get_warehouse(warehouse_id)
    assert detail.get("id") == warehouse_id


def test_execute_read_only_sql(
    service: DatabricksService, warehouse_id: str, sample_table: str
) -> None:
    safe_sql = validate_read_only_sql(f"SELECT * FROM {sample_table} LIMIT 3")
    result = service.execute_read_only_sql(
        statement=safe_sql,
        warehouse_id=warehouse_id,
        row_limit=3,
        byte_limit=1_000_000,
        wait_seconds=50,
    )
    assert "statement_id" in result or "status" in result


def test_sql_guard_rejects_mutation() -> None:
    with pytest.raises(UnsafeSqlError):
        validate_read_only_sql(f"DROP TABLE {'x'}")


def test_query_history_returns_response(service: DatabricksService) -> None:
    history = service.list_query_history(limit=5)
    assert isinstance(history, dict)


@pytest.mark.parametrize(
    "call",
    ["list_jobs", "list_pipelines", "list_clusters", "list_cluster_policies"],
)
def test_operational_lists_do_not_error(service: DatabricksService, call: str) -> None:
    result = getattr(service, call)(limit=5)
    assert isinstance(result, list)


def test_governance_grants_on_samples(service: DatabricksService) -> None:
    grants = service.get_grants("CATALOG", "samples")
    assert isinstance(grants, dict)
