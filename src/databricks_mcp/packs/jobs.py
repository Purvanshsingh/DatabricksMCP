"""Jobs read pack: workflow definitions and run inspection (read-only)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "jobs"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_jobs",
            NAME,
            RiskClass.READ,
            "List jobs in the workspace, bounded to the configured page size.",
        )
    )
    def list_jobs(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_jobs(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec("get_job", NAME, RiskClass.READ, "Get the full definition of one job by its id.")
    )
    def get_job(job_id: int) -> dict[str, Any]:
        return registrar.service.get_job(job_id)

    @registrar.tool(
        ToolSpec(
            "list_job_runs",
            NAME,
            RiskClass.READ,
            "List job runs, optionally filtered to one job id, bounded to the page size.",
        )
    )
    def list_job_runs(
        job_id: int | None = None, limit: int = default_limit
    ) -> list[dict[str, Any]]:
        return registrar.service.list_job_runs(job_id=job_id, limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_job_run",
            NAME,
            RiskClass.READ,
            "Get the details and state of one job run by its id.",
        )
    )
    def get_job_run(run_id: int) -> dict[str, Any]:
        return registrar.service.get_job_run(run_id)

    @registrar.tool(
        ToolSpec(
            "get_job_run_output",
            NAME,
            RiskClass.READ,
            "Get the output of a completed job run (task results, logs metadata).",
        )
    )
    def get_job_run_output(run_id: int) -> dict[str, Any]:
        return registrar.service.get_job_run_output(run_id)
