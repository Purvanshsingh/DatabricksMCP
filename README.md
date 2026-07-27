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

## Phase 1 capabilities

- MCP over local `stdio` and remote Streamable HTTP
- Databricks unified authentication through the official Python SDK
- Health, identity, and capability-introspection diagnostics
- Read-only Unity Catalog exploration: catalogs, schemas, tables, views,
  columns, functions, and volumes
- Read-only Databricks SQL warehouse discovery
- A capability-pack architecture with a policy-enforcing tool registry
- A deny-by-default policy foundation for future mutation tools
- Typed configuration, structured errors, tests, CI, and a non-root container

See [ROADMAP.md](ROADMAP.md) for the planned production-grade capability set.

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
| `DATABRICKS_MCP_ACCESS_MODE` | `read-only` | Policy mode; only `read-only` exists in Phase 1 |

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
