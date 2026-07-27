"""Unity Catalog read pack: catalogs, schemas, tables, columns, functions, volumes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "catalog"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_catalogs",
            NAME,
            RiskClass.READ,
            "List accessible Unity Catalog catalogs, bounded to the configured page size.",
        )
    )
    def list_catalogs(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_catalogs(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_catalog",
            NAME,
            RiskClass.READ,
            "Get metadata for one Unity Catalog catalog by name.",
        )
    )
    def get_catalog(name: str) -> dict[str, Any]:
        return registrar.service.get_catalog(name)

    @registrar.tool(
        ToolSpec(
            "list_schemas",
            NAME,
            RiskClass.READ,
            "List schemas within a catalog, bounded to the page size.",
        )
    )
    def list_schemas(catalog_name: str, limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_schemas(catalog_name=catalog_name, limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_schema",
            NAME,
            RiskClass.READ,
            "Get metadata for one schema by its full name (catalog.schema).",
        )
    )
    def get_schema(full_name: str) -> dict[str, Any]:
        return registrar.service.get_schema(full_name)

    @registrar.tool(
        ToolSpec(
            "list_tables",
            NAME,
            RiskClass.READ,
            "List tables within a schema, bounded to the page size.",
        )
    )
    def list_tables(
        catalog_name: str, schema_name: str, limit: int = default_limit
    ) -> list[dict[str, Any]]:
        return registrar.service.list_tables(
            catalog_name=catalog_name, schema_name=schema_name, limit=limit_of(limit)
        )

    @registrar.tool(
        ToolSpec(
            "list_views",
            NAME,
            RiskClass.READ,
            "List views and materialized views within a schema, bounded to the page size.",
        )
    )
    def list_views(
        catalog_name: str, schema_name: str, limit: int = default_limit
    ) -> list[dict[str, Any]]:
        return registrar.service.list_views(
            catalog_name=catalog_name, schema_name=schema_name, limit=limit_of(limit)
        )

    @registrar.tool(
        ToolSpec(
            "get_table",
            NAME,
            RiskClass.READ,
            "Get full metadata for one table by its full name (catalog.schema.table).",
        )
    )
    def get_table(full_name: str) -> dict[str, Any]:
        return registrar.service.get_table(full_name)

    @registrar.tool(
        ToolSpec(
            "describe_table",
            NAME,
            RiskClass.READ,
            "Return a concise table summary: type, comment, and columns with types.",
        )
    )
    def describe_table(full_name: str) -> dict[str, Any]:
        table = registrar.service.get_table(full_name)
        raw_columns = table.get("columns")
        columns: list[dict[str, Any]] = []
        if isinstance(raw_columns, list):
            for column in raw_columns:
                if isinstance(column, dict):
                    columns.append(
                        {
                            "name": column.get("name"),
                            "type": column.get("type_text") or column.get("type_name"),
                            "nullable": column.get("nullable"),
                            "comment": column.get("comment"),
                        }
                    )
        return {
            "full_name": table.get("full_name"),
            "catalog_name": table.get("catalog_name"),
            "schema_name": table.get("schema_name"),
            "name": table.get("name"),
            "table_type": table.get("table_type"),
            "data_source_format": table.get("data_source_format"),
            "comment": table.get("comment"),
            "columns": columns,
        }

    @registrar.tool(
        ToolSpec(
            "list_columns", NAME, RiskClass.READ, "List the columns of one table by its full name."
        )
    )
    def list_columns(full_name: str) -> list[dict[str, Any]]:
        return registrar.service.list_columns(full_name)

    @registrar.tool(
        ToolSpec(
            "list_functions",
            NAME,
            RiskClass.READ,
            "List user-defined functions within a schema, bounded to the page size.",
        )
    )
    def list_functions(
        catalog_name: str, schema_name: str, limit: int = default_limit
    ) -> list[dict[str, Any]]:
        return registrar.service.list_functions(
            catalog_name=catalog_name, schema_name=schema_name, limit=limit_of(limit)
        )

    @registrar.tool(
        ToolSpec(
            "get_function", NAME, RiskClass.READ, "Get metadata for one function by its full name."
        )
    )
    def get_function(name: str) -> dict[str, Any]:
        return registrar.service.get_function(name)

    @registrar.tool(
        ToolSpec(
            "list_volumes",
            NAME,
            RiskClass.READ,
            "List Unity Catalog volumes within a schema, bounded to the page size.",
        )
    )
    def list_volumes(
        catalog_name: str, schema_name: str, limit: int = default_limit
    ) -> list[dict[str, Any]]:
        return registrar.service.list_volumes(
            catalog_name=catalog_name, schema_name=schema_name, limit=limit_of(limit)
        )
