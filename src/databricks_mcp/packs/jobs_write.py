"""Gated jobs write pack: trigger, cancel, and delete job runs.

These tools change state and are therefore OFF by default. They execute only
when the server runs in ``controlled-write`` mode and the tool name is on the
write allowlist. ``delete_job`` is destructive and additionally requires an
approval token: call it once with ``dry_run=true`` to receive a token, then
call again with that ``approval_token``. Every attempt is audited.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "jobs"

RUN_JOB = ToolSpec(
    "run_job",
    NAME,
    RiskClass.WRITE,
    "Trigger a run of a job.",
    changes_state=True,
    supports_dry_run=True,
    idempotent=False,
)
CANCEL_JOB_RUN = ToolSpec(
    "cancel_job_run",
    NAME,
    RiskClass.WRITE,
    "Request cancellation of a job run.",
    changes_state=True,
    supports_dry_run=True,
    idempotent=True,
)
DELETE_JOB = ToolSpec(
    "delete_job",
    NAME,
    RiskClass.DESTRUCTIVE,
    "Permanently delete a job.",
    changes_state=True,
    supports_dry_run=True,
    idempotent=True,
)


def register(registrar: Registrar) -> None:
    @registrar.tool(RUN_JOB)
    def run_job(
        job_id: int,
        idempotency_token: str | None = None,
        dry_run: bool = False,
        approval_token: str | None = None,
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            registrar.mutations.run(
                RUN_JOB,
                {"job_id": job_id, "idempotency_token": idempotency_token},
                lambda: registrar.service.run_job(
                    job_id=job_id, idempotency_token=idempotency_token
                ),
                dry_run=dry_run,
                approval_token=approval_token,
            ),
        )

    @registrar.tool(CANCEL_JOB_RUN)
    def cancel_job_run(
        run_id: int,
        dry_run: bool = False,
        approval_token: str | None = None,
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            registrar.mutations.run(
                CANCEL_JOB_RUN,
                {"run_id": run_id},
                lambda: registrar.service.cancel_job_run(run_id),
                dry_run=dry_run,
                approval_token=approval_token,
            ),
        )

    @registrar.tool(DELETE_JOB)
    def delete_job(
        job_id: int,
        dry_run: bool = False,
        approval_token: str | None = None,
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            registrar.mutations.run(
                DELETE_JOB,
                {"job_id": job_id},
                lambda: registrar.service.delete_job(job_id),
                dry_run=dry_run,
                approval_token=approval_token,
            ),
        )
