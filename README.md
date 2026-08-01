# DatabricksMCP

[![CI](https://github.com/Purvanshsingh/DatabricksMCP/actions/workflows/ci.yml/badge.svg)](https://github.com/Purvanshsingh/DatabricksMCP/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

DatabricksMCP is an open-source, safety-first Model Context Protocol server for
Databricks. It is being built as a deploy-anywhere gateway for governed access
to Databricks workspaces from AI assistants and agents.

> [!IMPORTANT]
> This project is under active development and is not yet ready for production.
> The current Phase 1 surface is deliberately read-only.

DatabricksMCP is an independent community project. It is not affiliated with,
endorsed by, or sponsored by Databricks, Inc. Databricks and the Databricks logo
are trademarks of Databricks, Inc.

## Capabilities

DatabricksMCP is organized into independently enabled **capability packs**. Read
packs are always on; write tools are off by default (see
[Mutations](#controlled-mutations)). The read surface (63 tools) spans:

- **Transport & auth** — MCP over local `stdio` and remote Streamable HTTP;
  Databricks unified authentication through the official Python SDK
- **Core / diagnostics** — health, identity, `server_info`,
  `list_enabled_capabilities`, `get_policy_status`
- **Unity Catalog** — catalogs, schemas, tables, views, columns, functions, volumes
- **Databricks SQL** — warehouse discovery, query history, and AST-validated
  (sqlglot) read-only SQL with row/byte/time limits, polling, and cancellation
- **Jobs** — jobs, runs, and run output
- **Lakeflow pipelines** — pipelines, updates, and events
- **Compute** — clusters, cluster events, policies, node types, Spark versions
- **Governance** — Unity Catalog grants (direct and effective) and object permissions
- **Workspace** — browse and export notebooks and workspace objects
- **MLflow** — experiments, runs, registered models, and versions
- **AI** — Model Serving endpoints, Vector Search endpoints and indexes, Genie spaces
- **Cost & audit** — recent `system.billing.usage` and `system.access.audit` reads

Every tool carries a risk classification and is guarded by a deny-by-default
policy engine. See [ROADMAP.md](ROADMAP.md) for the full production-grade plan.

### Controlled mutations

State-changing tools are **disabled unless you opt in**. Set
`DATABRICKS_MCP_ACCESS_MODE=controlled-write` and list the exact tools you want
in `DATABRICKS_MCP_WRITE_TOOLS_ALLOW`. Even then:

- destructive/privileged actions require a short-lived, single-use **approval
  token** — call the tool with `dry_run=true` to get a plan and a token, then
  call again with `approval_token`;
- every attempt is written to a structured **audit log** (tool, risk, decision,
  outcome — never argument values).

## Quick start

Requirements:

- Python 3.11 or newer
- A Databricks workspace
- Databricks unified authentication configured through environment variables or
  a profile in `~/.databrickscfg`

Install locally with [`uv`](https://docs.astral.sh/uv/):

```bash
uv sync --all-groups
uv run databricks-mcp
```

Configure a local MCP client:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["--from", "databricks-mcp-server", "databricks-mcp"]
    }
  }
}
```

The package is not published yet, so during development point the client at a
local checkout:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/DatabricksMCP",
        "databricks-mcp"
      ]
    }
  }
}
```

### Authentication

DatabricksMCP delegates credential discovery and refresh to Databricks unified
authentication. For local development, authenticate with the Databricks CLI or
select a named profile:

```bash
export DATABRICKS_CONFIG_PROFILE=DEFAULT
uv run databricks-mcp
```

For unattended environments, use OAuth M2M or workload identity federation.
Personal access tokens are supported by the SDK but are not recommended for
production deployments.

Never place credentials in MCP tool arguments or commit them to configuration.

### Streamable HTTP

```bash
export DATABRICKS_MCP_TRANSPORT=streamable-http
export DATABRICKS_MCP_HOST=127.0.0.1
export DATABRICKS_MCP_PORT=8000
uv run databricks-mcp
```

The HTTP endpoint is `/mcp`. Phase 1 HTTP mode is suitable for local evaluation;
public deployment must be placed behind standards-compliant authentication and
TLS until native remote authorization lands in Phase 3.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `DATABRICKS_MCP_TRANSPORT` | `stdio` | `stdio` or `streamable-http` |
| `DATABRICKS_MCP_HOST` | `127.0.0.1` | HTTP bind address |
| `DATABRICKS_MCP_PORT` | `8000` | HTTP bind port |
| `DATABRICKS_MCP_LOG_LEVEL` | `INFO` | Python log level |
| `DATABRICKS_MCP_ACCESS_MODE` | `read-only` | `read-only` or `controlled-write` (enables gated write tools) |
| `DATABRICKS_MCP_WRITE_TOOLS_ALLOW` | _unset_ | Comma-separated write tool names to enable (controlled-write only) |
| `DATABRICKS_MCP_APPROVAL_TTL_SECONDS` | `300` | Lifetime of approval tokens for destructive actions (30–3600) |
| `DATABRICKS_MCP_SQL_MAX_ROWS` | `1000` | Maximum rows returned by read-only SQL (ceiling) |
| `DATABRICKS_MCP_SQL_BYTE_LIMIT` | `10000000` | Maximum result bytes for read-only SQL |
| `DATABRICKS_MCP_SQL_WAIT_SECONDS` | `30` | Synchronous wait before a statement returns a poll id (5–50) |
| `DATABRICKS_MCP_SQL_WAREHOUSES` | _unset_ | Optional comma-separated warehouse-id allowlist for SQL |

Standard `DATABRICKS_*` authentication variables are consumed by the official
Databricks SDK.

## Development

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

Architecture and security decisions live in [`docs/`](docs/). Contributions are
welcome; read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md)
before opening an issue or pull request.

## License

Licensed under the [Apache License 2.0](LICENSE).
