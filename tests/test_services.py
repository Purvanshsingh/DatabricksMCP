from __future__ import annotations

import pytest

from databricks_mcp.services import DatabricksService
from tests.conftest import FakeWorkspaceClient


def _service() -> DatabricksService:
    return DatabricksService(FakeWorkspaceClient())


def test_current_identity_is_serialized() -> None:
    assert _service().current_identity() == {"userName": "user@example.com"}


def test_list_catalogs_is_bounded() -> None:
    assert _service().list_catalogs(limit=2) == [{"name": "main"}, {"name": "system"}]


def test_get_catalog_returns_object() -> None:
    assert _service().get_catalog("main") == {"name": "main", "comment": "catalog main"}


def test_list_schemas_passes_catalog_name() -> None:
    client = FakeWorkspaceClient()
    service = DatabricksService(client)
    result = service.list_schemas(catalog_name="main", limit=10)
    assert client.schemas.list_calls == ["main"]
    assert result == [
        {"name": "default", "catalog_name": "main"},
        {"name": "bronze", "catalog_name": "main"},
    ]


def test_list_tables_passes_catalog_and_schema() -> None:
    client = FakeWorkspaceClient()
    DatabricksService(client).list_tables(catalog_name="main", schema_name="default", limit=10)
    assert client.tables.list_calls == [("main", "default")]


def test_list_views_filters_to_view_types() -> None:
    views = _service().list_views(catalog_name="main", schema_name="default", limit=10)
    assert [view["name"] for view in views] == ["daily_view", "rollup"]


def test_list_columns_extracts_columns_from_table() -> None:
    columns = _service().list_columns("main.default.events")
    assert [column["name"] for column in columns] == ["id", "ts"]


def test_get_warehouse_returns_object() -> None:
    assert _service().get_warehouse("w1") == {"id": "w1", "name": "starter", "state": "RUNNING"}


def test_invalid_limit_is_rejected() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        _service().list_catalogs(limit=0)
