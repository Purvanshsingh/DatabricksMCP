# Live workspace testing

DatabricksMCP ships an opt-in integration suite that runs the read tools against
a **real** Databricks workspace (the free [Databricks Free Edition] works well).
It is skipped by default, so CI and contributors without a workspace are
unaffected.

## 1. Configure authentication (never commit or paste your token)

Use Databricks unified authentication. The simplest option is a personal access
token in `~/.databrickscfg`:

```bash
umask 077
cat > ~/.databrickscfg <<'EOF'
[DEFAULT]
host  = https://<your-workspace>.cloud.databricks.com
token = <your-personal-access-token>
EOF
```

The SDK reads this file automatically. `.databrickscfg` is git-ignored, and the
server never accepts the token as a tool argument. Rotate the token if it is
ever exposed.

## 2. Point the tests at a warehouse and table

```bash
export DATABRICKS_MCP_LIVE=1
export DATABRICKS_MCP_TEST_WAREHOUSE_ID=<sql-warehouse-id>
# optional; defaults to a Free Edition sample table
export DATABRICKS_MCP_TEST_TABLE=samples.bakehouse.sales_transactions
```

## 3. Run

Quick, human-readable pass over every read pack:

```bash
.venv/bin/python scripts/live_smoke.py
```

Or the pytest integration suite (assertions per capability):

```bash
.venv/bin/pytest tests/live -m live -q
```

## Expected results on Free Edition

Free Edition is serverless-only and starts empty, so some results are legitimately
empty or restricted — these are correct, graceful behaviors, not failures:

- **Compute** — `list_clusters` is usually empty; `list_node_types` /
  `list_spark_versions` may be limited or return a permission error.
- **AI** — Model Serving, Vector Search, and Genie may be unavailable.
- **Cost** — `system.billing.usage` may not be populated.
- **Jobs / pipelines / experiments** — empty until you create some.

Catalog browsing, `get_table` / `list_columns`, warehouse listing,
`execute_read_only_sql`, and query history should all succeed.

[Databricks Free Edition]: https://www.databricks.com/learn/free-edition
