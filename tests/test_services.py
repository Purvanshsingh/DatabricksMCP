from __future__ import annotations

from collections.abc import Iterable

import pytest

from databricks_mcp.services import DatabricksService


class Model:
    def __init__(self, name: str) -> None:
        self.name = name

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name}


class CurrentUser:
    def me(self) -> object:
        return Model("user@example.com")


class ListingAPI:
    def __init__(self, names: list[str]) -> None:
        self.names = names

    def list(self) -> Iterable[object]:
        return (Model(name) for name in self.names)


class FakeWorkspaceClient:
    def __init__(self) -> None:
        self.current_user = CurrentUser()
        self.catalogs = ListingAPI(["main", "system", "samples"])
        self.warehouses = ListingAPI(["starter"])


def test_current_identity_is_serialized() -> None:
    service = DatabricksService(FakeWorkspaceClient())
    assert service.current_identity() == {"name": "user@example.com"}


def test_lists_are_bounded() -> None:
    service = DatabricksService(FakeWorkspaceClient())
    assert service.list_catalogs(limit=2) == [{"name": "main"}, {"name": "system"}]
    assert service.list_warehouses(limit=10) == [{"name": "starter"}]


def test_invalid_limit_is_rejected() -> None:
    service = DatabricksService(FakeWorkspaceClient())
    with pytest.raises(ValueError, match="greater than zero"):
        service.list_catalogs(limit=0)
