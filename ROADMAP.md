# Roadmap

The roadmap is capability- and quality-gated. Dates are intentionally omitted
until the project has a stable maintainer cadence.

## Phase 1 — Safe read-only foundation

- [x] Typed Python package and CLI entry point
- [x] `stdio` and Streamable HTTP transports
- [x] Databricks unified authentication
- [x] Health, current identity, catalog, and warehouse tools
- [x] Deny-by-default policy foundation
- [x] Unit tests, CI, container, and security documentation
- [x] Capability-pack architecture with a policy-enforcing tool registry
- [x] Capability introspection (`server_info`, `list_enabled_capabilities`, `get_policy_status`)
- [x] Unity Catalog metadata exploration (schemas, tables, views, columns, functions, volumes)
- [x] Mock-SDK contract tests for every read tool
- [ ] Read-only SQL with AST validation and bounded results
- [ ] Read-only jobs, pipeline, and cluster inspection
- [ ] Consistent cursor pagination for large listings
- [ ] Opt-in live-workspace integration tests

## Phase 2 — Controlled operations

- Jobs, pipelines, compute, and warehouse lifecycle operations
- Mutation classification, dry runs, approval tokens, and idempotency
- Workspace and Unity Catalog Volume file operations
- Async task support for long-running Databricks operations

## Phase 3 — Enterprise remote server

- MCP OAuth 2.1 protected-resource implementation
- M2M, U2M, on-behalf-of-user, and workload identity federation
- Multi-user and multi-workspace isolation
- OpenTelemetry, audit sinks, quotas, and distributed rate limiting
- Databricks Apps, Docker, Kubernetes, and Helm deployments

## Phase 4 — Platform coverage

- Unity Catalog lineage, grants, and governance
- MLflow experiments and model registry
- Model serving, Genie, AI Search, and agent tooling
- Account-level identity, workspace administration, and cost visibility
- Public extension SDK for third-party capability packs

## Phase 5 — Version 1.0

- Stable tool and response contracts
- Client compatibility and upgrade guarantees
- Security review, SBOM, provenance, and signed releases
- PyPI, container registry, MCP Registry, and Marketplace publication
