# Contributing

Thank you for helping build DatabricksMCP.

## Development setup

1. Install Python 3.11+ and `uv`.
2. Fork and clone the repository.
3. Run `uv sync --all-groups`.
4. Create a focused branch and add tests with every behavioral change.
5. Run `make check` before opening a pull request.

Do not use production credentials or customer data in tests. Integration tests
must use an isolated workspace and least-privilege identity.

## Design expectations

- Read operations and mutations must be implemented separately.
- Every tool must have a stable, typed input and JSON-serializable output.
- Tool descriptions must explain side effects, limits, and required permissions.
- Tool code must delegate to a service layer that can be tested without MCP.
- Results must be bounded and secrets must be redacted.
- New dependencies require a clear maintenance and security justification.

Substantial changes should begin with an issue or architecture decision record.

## Pull requests

Pull requests should explain the user impact, security impact, tests performed,
and any backward-compatibility considerations. Maintainers may request changes
when a tool expands permissions or exposes unbounded data.

Contributions are licensed under Apache-2.0.
