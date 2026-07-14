"""Databricks SDK adapter layer."""

from __future__ import annotations

from collections.abc import Iterable
from itertools import islice
from typing import Protocol

from databricks.sdk import WorkspaceClient

from databricks_mcp.serialization import JsonValue, to_json_value

JsonObject = dict[str, JsonValue]


class CurrentUserAPI(Protocol):
    def me(self) -> object: ...


class CatalogAPI(Protocol):
    def list(self) -> Iterable[object]: ...


class WarehouseAPI(Protocol):
    def list(self) -> Iterable[object]: ...


class WorkspaceClientLike(Protocol):
    @property
    def current_user(self) -> CurrentUserAPI: ...

    @property
    def catalogs(self) -> CatalogAPI: ...

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

    def current_identity(self) -> JsonObject:
        identity = to_json_value(self._client.current_user.me())
        if not isinstance(identity, dict):
            raise TypeError("Databricks current-user response was not an object")
        return identity

    def list_catalogs(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.catalogs.list(), limit=limit)

    def list_warehouses(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.warehouses.list(), limit=limit)

    @staticmethod
    def _bounded(values: Iterable[object], *, limit: int) -> list[JsonObject]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        results: list[JsonObject] = []
        for value in islice(values, limit):
            serialized = to_json_value(value)
            if not isinstance(serialized, dict):
                raise TypeError("Databricks list response contained a non-object item")
            results.append(serialized)
        return results
