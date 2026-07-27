"""Shared fakes that emulate the Databricks SDK surface used by the service."""

from __future__ import annotations

from collections.abc import Iterator


class Model:
    """A minimal SDK-like model exposing ``as_dict`` for serialization."""

    def __init__(self, **fields: object) -> None:
        self._fields = fields

    def as_dict(self) -> dict[str, object]:
        return dict(self._fields)


class CurrentUser:
    def me(self) -> Model:
        return Model(userName="user@example.com")


class CatalogAPI:
    def list(self) -> Iterator[Model]:
        yield from (Model(name=name) for name in ("main", "system", "samples"))

    def get(self, name: str) -> Model:
        return Model(name=name, comment=f"catalog {name}")


class SchemaAPI:
    def __init__(self) -> None:
        self.list_calls: list[str] = []

    def list(self, catalog_name: str) -> Iterator[Model]:
        self.list_calls.append(catalog_name)
        yield from (Model(name=name, catalog_name=catalog_name) for name in ("default", "bronze"))

    def get(self, full_name: str) -> Model:
        return Model(full_name=full_name)


class TableAPI:
    def __init__(self) -> None:
        self.list_calls: list[tuple[str, str]] = []

    def list(self, catalog_name: str, schema_name: str) -> Iterator[Model]:
        self.list_calls.append((catalog_name, schema_name))
        yield Model(name="events", table_type="MANAGED")
        yield Model(name="daily_view", table_type="VIEW")
        yield Model(name="rollup", table_type="MATERIALIZED_VIEW")

    def get(self, full_name: str) -> Model:
        return Model(
            full_name=full_name,
            catalog_name="main",
            schema_name="default",
            name="events",
            table_type="MANAGED",
            comment="event log",
            columns=[
                {"name": "id", "type_text": "bigint", "nullable": False, "comment": "pk"},
                {"name": "ts", "type_text": "timestamp", "nullable": True, "comment": None},
            ],
        )


class FunctionAPI:
    def list(self, catalog_name: str, schema_name: str) -> Iterator[Model]:
        yield Model(name="to_upper", catalog_name=catalog_name, schema_name=schema_name)

    def get(self, name: str) -> Model:
        return Model(name=name)


class VolumeAPI:
    def list(self, catalog_name: str, schema_name: str) -> Iterator[Model]:
        yield Model(name="raw", catalog_name=catalog_name, schema_name=schema_name)


class WarehouseAPI:
    def list(self) -> Iterator[Model]:
        yield Model(id="w1", name="starter")

    def get(self, id: str) -> Model:
        return Model(id=id, name="starter", state="RUNNING")


class FakeWorkspaceClient:
    """A structural stand-in for ``databricks.sdk.WorkspaceClient``."""

    def __init__(self) -> None:
        self.current_user = CurrentUser()
        self.catalogs = CatalogAPI()
        self.schemas = SchemaAPI()
        self.tables = TableAPI()
        self.functions = FunctionAPI()
        self.volumes = VolumeAPI()
        self.warehouses = WarehouseAPI()
