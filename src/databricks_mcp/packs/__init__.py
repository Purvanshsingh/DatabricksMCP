"""Capability packs and their registration entry point."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from databricks_mcp.packs import (
    catalog,
    compute,
    core,
    governance,
    jobs,
    mlflow,
    pipelines,
    sql,
    workspace,
)

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar


class Pack(Protocol):
    """A capability pack module: a name and a registration function."""

    NAME: str

    def register(self, registrar: Registrar) -> None: ...


DEFAULT_PACKS: tuple[Pack, ...] = (
    core,
    catalog,
    sql,
    jobs,
    pipelines,
    compute,
    governance,
    workspace,
    mlflow,
)


def register_all(registrar: Registrar) -> None:
    """Register every default capability pack onto the server."""
    for pack in DEFAULT_PACKS:
        pack.register(registrar)
