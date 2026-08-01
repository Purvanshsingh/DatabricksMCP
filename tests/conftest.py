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


class StatementExecutionAPI:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.cancelled: list[str] = []

    def execute_statement(self, statement: str, warehouse_id: str, **kwargs: object) -> Model:
        self.calls.append({"statement": statement, "warehouse_id": warehouse_id, **kwargs})
        return Model(
            statement_id="stmt-1",
            status={"state": "SUCCEEDED"},
            result={"data_array": [["1"]]},
        )

    def get_statement(self, statement_id: str) -> Model:
        return Model(statement_id=statement_id, status={"state": "SUCCEEDED"})

    def cancel_execution(self, statement_id: str) -> None:
        self.cancelled.append(statement_id)
        return None


class JobsAPI:
    def __init__(self) -> None:
        self.run_calls: list[int | None] = []

    def list(self) -> Iterator[Model]:
        yield Model(job_id=1, settings={"name": "etl"})
        yield Model(job_id=2, settings={"name": "ml"})

    def get(self, job_id: int) -> Model:
        return Model(job_id=job_id, settings={"name": "etl"})

    def list_runs(self, *, job_id: int | None = None) -> Iterator[Model]:
        self.run_calls.append(job_id)
        yield Model(run_id=10, job_id=job_id or 1, state={"life_cycle_state": "TERMINATED"})

    def get_run(self, run_id: int) -> Model:
        return Model(run_id=run_id, state={"life_cycle_state": "TERMINATED"})

    def get_run_output(self, run_id: int) -> Model:
        return Model(run_id=run_id, logs="done")


class PipelinesAPI:
    def list_pipelines(self) -> Iterator[Model]:
        yield Model(pipeline_id="p1", name="bronze")
        yield Model(pipeline_id="p2", name="silver")

    def get(self, pipeline_id: str) -> Model:
        return Model(pipeline_id=pipeline_id, name="bronze", state="RUNNING")

    def list_pipeline_events(self, pipeline_id: str) -> Model:
        return Model(events=[{"id": "e1", "level": "INFO"}], next_page_token=None)

    def list_updates(self, pipeline_id: str) -> Model:
        return Model(updates=[{"update_id": "u1", "state": "COMPLETED"}])

    def get_update(self, pipeline_id: str, update_id: str) -> Model:
        return Model(update={"update_id": update_id, "state": "COMPLETED"})


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
        self.statement_execution = StatementExecutionAPI()
        self.jobs = JobsAPI()
        self.pipelines = PipelinesAPI()
