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
from databricks.sdk.service.sql import (
    Disposition,
    ExecuteStatementRequestOnWaitTimeout,
    Format,
)
from databricks.sdk.service.workspace import ExportFormat

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


class StatementExecutionAPI(Protocol):
    def execute_statement(
        self,
        statement: str,
        warehouse_id: str,
        *,
        byte_limit: int | None = ...,
        catalog: str | None = ...,
        disposition: Disposition | None = ...,
        format: Format | None = ...,
        on_wait_timeout: ExecuteStatementRequestOnWaitTimeout | None = ...,
        row_limit: int | None = ...,
        schema: str | None = ...,
        wait_timeout: str | None = ...,
    ) -> object: ...

    def get_statement(self, statement_id: str) -> object: ...

    def cancel_execution(self, statement_id: str) -> object: ...


class JobsAPI(Protocol):
    def list(self) -> Iterable[object]: ...
    def get(self, job_id: int) -> object: ...
    def list_runs(self, *, job_id: int | None = ...) -> Iterable[object]: ...
    def get_run(self, run_id: int) -> object: ...
    def get_run_output(self, run_id: int) -> object: ...


class PipelinesAPI(Protocol):
    def list_pipelines(self) -> Iterable[object]: ...
    def get(self, pipeline_id: str) -> object: ...
    def list_pipeline_events(self, pipeline_id: str) -> object: ...
    def list_updates(self, pipeline_id: str) -> object: ...
    def get_update(self, pipeline_id: str, update_id: str) -> object: ...


class ClustersAPI(Protocol):
    def list(self) -> Iterable[object]: ...
    def get(self, cluster_id: str) -> object: ...
    def events(self, cluster_id: str) -> Iterable[object]: ...
    def list_node_types(self) -> object: ...
    def spark_versions(self) -> object: ...


class ClusterPoliciesAPI(Protocol):
    def list(self) -> Iterable[object]: ...
    def get(self, policy_id: str) -> object: ...


class QueryHistoryAPI(Protocol):
    def list(self, *, max_results: int | None = ...) -> object: ...


class GrantsAPI(Protocol):
    def get(self, securable_type: str, full_name: str) -> object: ...
    def get_effective(self, securable_type: str, full_name: str) -> object: ...


class PermissionsAPI(Protocol):
    def get(self, request_object_type: str, request_object_id: str) -> object: ...


class WorkspaceAPI(Protocol):
    def list(self, path: str) -> Iterable[object]: ...
    def get_status(self, path: str) -> object: ...
    def export(self, path: str, *, format: ExportFormat | None = ...) -> object: ...


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

    @property
    def statement_execution(self) -> StatementExecutionAPI: ...

    @property
    def jobs(self) -> JobsAPI: ...

    @property
    def pipelines(self) -> PipelinesAPI: ...

    @property
    def clusters(self) -> ClustersAPI: ...

    @property
    def cluster_policies(self) -> ClusterPoliciesAPI: ...

    @property
    def query_history(self) -> QueryHistoryAPI: ...

    @property
    def grants(self) -> GrantsAPI: ...

    @property
    def permissions(self) -> PermissionsAPI: ...

    @property
    def workspace(self) -> WorkspaceAPI: ...


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

    def list_query_history(self, *, limit: int) -> JsonObject:
        return self._object(self._client.query_history.list(max_results=limit))

    def execute_read_only_sql(
        self,
        *,
        statement: str,
        warehouse_id: str,
        row_limit: int,
        byte_limit: int,
        wait_seconds: int,
        catalog: str | None = None,
        schema: str | None = None,
    ) -> JsonObject:
        response = self._client.statement_execution.execute_statement(
            statement,
            warehouse_id,
            row_limit=row_limit,
            byte_limit=byte_limit,
            wait_timeout=f"{wait_seconds}s",
            on_wait_timeout=ExecuteStatementRequestOnWaitTimeout.CONTINUE,
            disposition=Disposition.INLINE,
            format=Format.JSON_ARRAY,
            catalog=catalog,
            schema=schema,
        )
        return self._object(response)

    def get_sql_statement(self, statement_id: str) -> JsonObject:
        return self._object(self._client.statement_execution.get_statement(statement_id))

    def cancel_sql_statement(self, statement_id: str) -> JsonObject:
        self._client.statement_execution.cancel_execution(statement_id)
        return {"statement_id": statement_id, "cancelled": True}

    # -- Jobs -------------------------------------------------------------

    def list_jobs(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.jobs.list(), limit=limit)

    def get_job(self, job_id: int) -> JsonObject:
        return self._object(self._client.jobs.get(job_id))

    def list_job_runs(self, *, job_id: int | None, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.jobs.list_runs(job_id=job_id), limit=limit)

    def get_job_run(self, run_id: int) -> JsonObject:
        return self._object(self._client.jobs.get_run(run_id))

    def get_job_run_output(self, run_id: int) -> JsonObject:
        return self._object(self._client.jobs.get_run_output(run_id))

    # -- Lakeflow pipelines ----------------------------------------------

    def list_pipelines(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.pipelines.list_pipelines(), limit=limit)

    def get_pipeline(self, pipeline_id: str) -> JsonObject:
        return self._object(self._client.pipelines.get(pipeline_id))

    def list_pipeline_events(self, pipeline_id: str) -> JsonObject:
        return self._object(self._client.pipelines.list_pipeline_events(pipeline_id))

    def list_pipeline_updates(self, pipeline_id: str) -> JsonObject:
        return self._object(self._client.pipelines.list_updates(pipeline_id))

    def get_pipeline_update(self, pipeline_id: str, update_id: str) -> JsonObject:
        return self._object(self._client.pipelines.get_update(pipeline_id, update_id))

    # -- Compute ----------------------------------------------------------

    def list_clusters(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.clusters.list(), limit=limit)

    def get_cluster(self, cluster_id: str) -> JsonObject:
        return self._object(self._client.clusters.get(cluster_id))

    def list_cluster_events(self, *, cluster_id: str, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.clusters.events(cluster_id), limit=limit)

    def list_node_types(self) -> JsonObject:
        return self._object(self._client.clusters.list_node_types())

    def list_spark_versions(self) -> JsonObject:
        return self._object(self._client.clusters.spark_versions())

    def list_cluster_policies(self, *, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.cluster_policies.list(), limit=limit)

    def get_cluster_policy(self, policy_id: str) -> JsonObject:
        return self._object(self._client.cluster_policies.get(policy_id))

    # -- Governance -------------------------------------------------------

    def get_grants(self, securable_type: str, full_name: str) -> JsonObject:
        return self._object(self._client.grants.get(securable_type, full_name))

    def get_effective_grants(self, securable_type: str, full_name: str) -> JsonObject:
        return self._object(self._client.grants.get_effective(securable_type, full_name))

    def get_permissions(self, object_type: str, object_id: str) -> JsonObject:
        return self._object(self._client.permissions.get(object_type, object_id))

    # -- Workspace files --------------------------------------------------

    def list_workspace_objects(self, *, path: str, limit: int) -> list[JsonObject]:
        return self._bounded(self._client.workspace.list(path), limit=limit)

    def get_workspace_status(self, path: str) -> JsonObject:
        return self._object(self._client.workspace.get_status(path))

    def export_workspace_object(self, *, path: str, export_format: str) -> JsonObject:
        return self._object(self._client.workspace.export(path, format=ExportFormat(export_format)))

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
