"""Standalone live read-only smoke check against a real Databricks workspace.

Auth comes from Databricks unified authentication (e.g. ``~/.databrickscfg``);
this script never sees or prints the token. It exercises one call from every
read pack and prints a per-tool status, then a summary. It exits cleanly when no
credentials are configured.

Usage:

    DATABRICKS_MCP_TEST_WAREHOUSE_ID=<id> .venv/bin/python scripts/live_smoke.py

Optional env:
    DATABRICKS_MCP_TEST_TABLE   default: samples.bakehouse.sales_transactions
"""

from __future__ import annotations

import os
from collections.abc import Callable

from databricks_mcp.services import DatabricksService
from databricks_mcp.sqlguard import validate_read_only_sql

WAREHOUSE_ID = os.environ.get("DATABRICKS_MCP_TEST_WAREHOUSE_ID", "")
TABLE = os.environ.get("DATABRICKS_MCP_TEST_TABLE", "samples.bakehouse.sales_transactions")

_counts = {"ok": 0, "warn": 0, "err": 0}


def _summary(value: object) -> str:
    if isinstance(value, list):
        return f"{len(value)} item(s)"
    if isinstance(value, dict):
        keys = list(value.keys())
        return "{" + ", ".join(keys[:4]) + ("…" if len(keys) > 4 else "") + "}"
    return str(value)[:70]


def check(name: str, call: Callable[[], object]) -> None:
    try:
        result = call()
    except Exception as error:
        _counts["err"] += 1
        print(f"[FAIL] {name:34} {type(error).__name__}: {str(error)[:90]}")
        return
    if isinstance(result, list) and not result:
        _counts["warn"] += 1
        print(f"[EMPTY] {name:33} (expected on a fresh / Free Edition workspace)")
    else:
        _counts["ok"] += 1
        print(f"[ OK ] {name:34} {_summary(result)}")


def main() -> int:
    try:
        service = DatabricksService.from_environment()
        identity = service.current_identity()
    except Exception as error:
        print(f"No Databricks credentials configured or auth failed: {type(error).__name__}")
        print("Configure unified auth (e.g. ~/.databrickscfg) and re-run. Skipping.")
        return 0

    catalog, schema, _table = [*TABLE.split("."), "", "", ""][:3]
    print(f"Authenticated as: {identity.get('userName') or identity.get('displayName') or '?'}")
    print(f"Warehouse: {WAREHOUSE_ID or '(unset — SQL tools skipped)'}   Table: {TABLE}")
    print("-" * 72)

    check("list_catalogs", lambda: service.list_catalogs(limit=10))
    check("get_catalog(samples)", lambda: service.get_catalog("samples"))
    check("list_schemas(samples)", lambda: service.list_schemas(catalog_name="samples", limit=25))
    check(
        f"list_tables({catalog}.{schema})",
        lambda: service.list_tables(catalog_name=catalog, schema_name=schema, limit=25),
    )
    check(f"get_table({TABLE})", lambda: service.get_table(TABLE))
    check(f"list_columns({TABLE})", lambda: service.list_columns(TABLE))
    check("list_warehouses", lambda: service.list_warehouses(limit=10))
    if WAREHOUSE_ID:
        check("get_warehouse", lambda: service.get_warehouse(WAREHOUSE_ID))
        safe_sql = validate_read_only_sql(f"SELECT * FROM {TABLE} LIMIT 3")
        check(
            "execute_read_only_sql",
            lambda: service.execute_read_only_sql(
                statement=safe_sql,
                warehouse_id=WAREHOUSE_ID,
                row_limit=3,
                byte_limit=1_000_000,
                wait_seconds=50,
            ),
        )
        check("list_query_history", lambda: service.list_query_history(limit=5))
    check("list_jobs", lambda: service.list_jobs(limit=5))
    check("list_pipelines", lambda: service.list_pipelines(limit=5))
    check("list_clusters", lambda: service.list_clusters(limit=5))
    check("list_node_types", lambda: service.list_node_types())
    check("list_spark_versions", lambda: service.list_spark_versions())
    check("list_experiments", lambda: service.list_experiments(limit=5))
    check("list_registered_models", lambda: service.list_registered_models(limit=5))
    check("list_serving_endpoints", lambda: service.list_serving_endpoints(limit=5))
    check("list_vector_search_endpoints", lambda: service.list_vector_search_endpoints(limit=5))
    check("list_genie_spaces", lambda: service.list_genie_spaces())
    check("get_grants(CATALOG,samples)", lambda: service.get_grants("CATALOG", "samples"))
    check("list_workspace_objects(/)", lambda: service.list_workspace_objects(path="/", limit=5))

    print("-" * 72)
    print(f"Summary:  OK {_counts['ok']}   EMPTY {_counts['warn']}   FAIL {_counts['err']}")
    return 1 if _counts["err"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
