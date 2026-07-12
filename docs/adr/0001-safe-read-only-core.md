# ADR 0001: Begin with a safe read-only core

- Status: Accepted
- Date: 2026-07-12

## Context

Databricks exposes high-impact operations such as deleting jobs, terminating
compute, modifying permissions, and executing arbitrary SQL. Language-model
tool selection is probabilistic and prompt content is untrusted.

## Decision

Phase 1 registers only tools classified as read-only. The policy layer denies
all other risk classes. Mutation tools will not be added until dry-run,
approval, audit, and idempotency contracts are designed and tested.

## Consequences

The first release has a smaller feature surface, but establishes a safe default
and prevents accidental expansion of privileges as tools are added.
