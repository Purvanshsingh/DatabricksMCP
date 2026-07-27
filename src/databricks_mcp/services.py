"""Databricks SDK adapter layer.

Bounded, read-only operations against one Databricks workspace. The service
accepts an injected client so tests can supply fakes and never reach a live
workspace. Responses are converted to plain JSON values; SDK models never leave
this layer.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Protocol

from databricks.sdk import WorkspaceClient

from databricks_mcp.serialization import JsonValue, to_json_value

JsonObject = dict[str, JsonValue]

_VIEW_TABLE_TYPES = frozenset({"VIEW", "MATERIALIZED_VIEW"})


class CurrentUserAPI(Protocol):
    def me(self) -> object: ...


class CatalogAPI(Protocol):
    def list(self) -> Iterable[object]: ...
    def get(self, name: str) -> object: ...


class SchemaAPI(Protocol):
    def list(self, catalog_name: str) -> Iterable[object]: ...
    def get(self, full_name: str) -> object: ...


class TableAPI(Protocol):
    def list(self, catalog_name: str, schema_name: str) -> Iterable[object]: ...
    def get(self, full_name: str) -> object: ...


class FunctionAPI(Protocol):
    def list(self, catalog_name: str, schema_name: str) -> Iterable[object]: ...
    def get(self, name: str) -> object: ...


class VolumeAPI(Protocol):
    def list(self, catalog_name: str, schema_name: str) -> Iterable[object]: ...


class WarehouseAPI(Protocol):
    def list(self) -> Iterable[object]: ...
    def get(self, id: str) -> object: ...


class WorkspaceClientLike(Protocol):
    @property
    def current_user(self) -> CurrentUserAPI: ...

    @property
    def catalogs(self) -> CatalogAPI: ...

    @property
    def schemas(self) -> SchemaAPI: ...

    @property
    def tables(self) -> TableAPI: ...

    @property
    def functions(self) -> FunctionAPI: ...

    @property
    def volumes(self) -> VolumeAPI: ...

    @property
    def warehouses(self) -> WarehouseAPI: ...


class DatabricksService:
    """Bounded read-only operations against one Databricks workspace."""

    def __init__(self, client: WorkspaceClientLike) -> None:
        self._client = client

    @classmethod
    def from_environment(cls) -> DatabricksService:
        """Build a client using Databricks unified authentication."""
        return cls(WorkspaceClient())

    # -- Identity ---------------------------------------------------------

    def current_identity(self) -> JsonObject:
        return self._object(self._client.current_user.me())

    # -- Unity Catalog ----------------------------------------------------

    def list_catalogs(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.catalogs.list(), limit=limit)

    def get_catalog(self, name: str) -> JsonObject:
        return self._object(self._client.catalogs.get(name))

    def list_schemas(self, *, catalog_name: str, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.schemas.list(catalog_name), limit=limit)

    def get_schema(self, full_name: str) -> JsonObject:
        return self._object(self._client.schemas.get(full_name))

    def list_tables(self, *, catalog_name: str, schema_name: str, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.tables.list(catalog_name, schema_name), limit=limit)

    def get_table(self, full_name: str) -> JsonObject:
        return self._object(self._client.tables.get(full_name))

    def list_views(self, *, catalog_name: str, schema_name: str, limit: int) -> list[JsonObject]:
        return self._bounded(
            self._client.tables.list(catalog_name, schema_name),
            limit=limit,
            predicate=lambda table: table.get("table_type") in _VIEW_TABLE_TYPES,
        )

    def list_columns(self, full_name: str) -> list[JsonObject]:
        columns = self.get_table(full_name).get("columns")
        if columns is None:
            return []
        if not isinstance(columns, list):
            raise TypeError("Databricks table columns response was not a list")
        result: list[JsonObject] = []
        for column in columns:
            if not isinstance(column, dict):
                raise TypeError("Databricks table column entry was not an object")
            result.append(column)
        return result

    def list_functions(
        self, *, catalog_name: str, schema_name: str, limit: int
    ) -> list[JsonObject]:
        return self._bounded(self._client.functions.list(catalog_name, schema_name), limit=limit)

    def get_function(self, name: str) -> JsonObject:
        return self._object(self._client.functions.get(name))

    def list_volumes(self, *, catalog_name: str, schema_name: str, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.volumes.list(catalog_name, schema_name), limit=limit)

    # -- Databricks SQL ---------------------------------------------------

    def list_warehouses(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.warehouses.list(), limit=limit)

    def get_warehouse(self, warehouse_id: str) -> JsonObject:
        return self._object(self._client.warehouses.get(warehouse_id))

    # -- Serialization helpers -------------------------------------------

    @staticmethod
    def _object(value: object) -> JsonObject:
        serialized = to_json_value(value)
        if not isinstance(serialized, dict):
            raise TypeError("Databricks response was not an object")
        return serialized

    @staticmethod
    def _bounded(
        values: Iterable[object],
        *,
        limit: int,
        predicate: Callable[[JsonObject], bool] | None = None,
    ) -> list[JsonObject]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        results: list[JsonObject] = []
        for value in values:
            if len(results) >= limit:
                break
            serialized = to_json_value(value)
            if not isinstance(serialized, dict):
                raise TypeError("Databricks list response contained a non-object item")
            if predicate is not None and not predicate(serialized):
                continue
            results.append(serialized)
        return results
