# Security Policy

## Supported versions

DatabricksMCP is pre-release software. Security fixes are applied to the latest
development release only until version 1.0 establishes a formal support policy.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private
vulnerability reporting feature for this repository. Include:

- affected version or commit;
- reproduction steps or a proof of concept;
- expected impact;
- suggested mitigations, if known.

If private vulnerability reporting is unavailable, contact the repository owner
through their public GitHub profile and request a private reporting channel.
Never include live Databricks hosts, tokens, client secrets, table contents, or
customer information in a report.

## Security posture

- The default and only Phase 1 policy is read-only.
- Credentials are obtained through Databricks unified authentication and are
  never accepted as MCP tool arguments.
- Remote HTTP mode must not be exposed publicly without TLS and an external
  authentication layer during Phase 1.
- Secret values must never be returned, logged, or included in exception text.
- Every future mutation tool must declare a risk class and pass policy checks.

See [docs/threat-model.md](docs/threat-model.md) for system boundaries and known
threats.
