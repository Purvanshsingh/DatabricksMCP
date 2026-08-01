"""Capability packs and their registration entry point."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from databricks_mcp.packs import (
    ai,
    catalog,
    compute,
    core,
    cost,
    governance,
    jobs,
    jobs_write,
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


# Read-only packs are always registered. Write packs are registered only when
# the server runs in controlled-write mode; individual write tools are then
# further gated by the allowlist and approval policy.
READ_PACKS: tuple[Pack, ...] = (
    core,
    catalog,
    sql,
    jobs,
    pipelines,
    compute,
    governance,
    workspace,
    mlflow,
    ai,
    cost,
)

WRITE_PACKS: tuple[Pack, ...] = (jobs_write,)


def register_all(registrar: Registrar) -> None:
    """Register read packs always, and write packs only in controlled-write mode."""
    for pack in READ_PACKS:
        pack.register(registrar)
    if registrar.settings.access_mode == "controlled-write":
        for pack in WRITE_PACKS:
            pack.register(registrar)
