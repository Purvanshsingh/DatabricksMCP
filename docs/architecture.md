# Architecture

DatabricksMCP separates protocol concerns from Databricks API access so that
tools remain testable, policy-aware, and transport-independent.

```text
MCP client
   |
stdio or Streamable HTTP
   |
MCP tool registry
   |
policy engine ---- audit/telemetry
   |
service adapters
   |
Databricks SDK unified authentication
   |
Databricks workspace/account APIs
```

## Design rules

1. Safe defaults: only read-only tools are enabled in Phase 1.
2. Explicit risk: every registered capability has a risk classification.
3. Bounded data: list and query results must enforce limits.
4. SDK-first: use the supported Databricks SDK unless an API is unavailable.
5. Transport neutrality: business logic does not import MCP classes.
6. Testability: service adapters accept injected clients and fake SDK objects.
7. Stable contracts: outputs are plain JSON values rather than SDK models.

## Package layout

- `config.py`: validated environment configuration.
- `policy.py`: capability classification and authorization decisions.
- `serialization.py`: bounded conversion of SDK models to JSON values.
- `services.py`: Databricks SDK adapter layer.
- `server.py`: MCP tool registration only.
- `__main__.py`: process startup and transport selection.

Future capability packs will live under `tools/` and `services/` namespaces once
the initial contracts have been validated with multiple MCP clients.
